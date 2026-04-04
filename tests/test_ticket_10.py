# -*- coding: utf-8 -*-
"""
TICKET 10 — OpenClaw Autarkie Veto-Traps.

Spezifikation: docs/05_AUDIT_PLANNING/TICKET_10_OPENCLAW_AUTARKIE.md

TDD: `src.scripts.heal_openclaw_vps` und die OpenClaw-Pacemaker-Logik in
`src.services.infrastructure_heartbeat` können fehlen oder unvollständig sein —
die Tests definieren den Kontrakt und schlagen fehl, bis die Implementierung passt.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import asyncio
import importlib
import inspect
import os
from subprocess import CompletedProcess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.logic_core.anti_heroin_validator import TrustCollapseException

# --- Kontrakt TICKET_10 (Producer-Vorgaben) -----------------------------------

# Flag-Datei bei fehlgeschlagenem Gateway / Autonomie-Veto (NMI).
AUTONOMY_VETO_FLAG = Path("/tmp/omega_autonomy_veto.flag")

# Pacemaker-Pathologie-Log (simuliert oder echt; optional per Env überschreibbar).
PACEMAKER_PATHOLOGY_LOG = Path("/tmp/omega_pacemaker_pathology.log")

HEAL_MOD = "src.scripts.heal_openclaw_vps"

# Erwartete Entry-Points Heil-Skript (erster Treffer gewinnt).
_HEAL_RUNNERS = (
    "diagnose_heal_openclaw_vps",
    "run_ssh_heal_and_verify_gateway",
    "execute_openclaw_vps_heal_cycle",
)

# Heartbeat: async Tick, der check_gateway nutzt und bei Fehlschlag Flag + Log setzt.
_HEARTBEAT_OPENCLAW_TICKS = (
    "apply_openclaw_autonomy_veto_if_needed",
    "pacemaker_openclaw_autonomy_tick",
)


def _import_heal_module():
    try:
        return importlib.import_module(HEAL_MOD)
    except ImportError as exc:
        pytest.fail(
            f"TICKET_10: Modul {HEAL_MOD} fehlt noch. "
            f"Erwartung: SSH-Diagnose/Heil via subprocess.run, StrictHostKeyChecking=yes, "
            f"danach Out-of-Band check_gateway(); bei Verstoß TrustCollapseException. ({exc})"
        )


def _resolve_heal_runner(heal_mod):
    for name in _HEAL_RUNNERS:
        fn = getattr(heal_mod, name, None)
        if callable(fn):
            return name, fn
    pytest.fail(
        "TICKET_10: heal_openclaw_vps muss eine Callable exportieren, z. B. "
        + ", ".join(_HEAL_RUNNERS)
    )


def _subprocess_run_patcher(heal_mod, mock_run: MagicMock):
    """Patcht subprocess.run, egal ob per `import subprocess` oder `from subprocess import run`."""
    if hasattr(heal_mod, "subprocess") and hasattr(heal_mod.subprocess, "run"):
        return patch.object(heal_mod.subprocess, "run", mock_run)
    run_attr = getattr(heal_mod, "run", None)
    if callable(run_attr) and getattr(run_attr, "__module__", None) == "subprocess":
        return patch.object(heal_mod, "run", mock_run)
    return patch(f"{HEAL_MOD}.subprocess.run", mock_run)


def _flatten_subprocess_invocation(call) -> str:
    """Durchsuchbarer String aus einem subprocess.run-Aufruf."""
    args, kwargs = call
    chunks: list[str] = []
    if args:
        cmd = args[0]
        if isinstance(cmd, (list, tuple)):
            chunks.append(" ".join(str(x) for x in cmd))
        else:
            chunks.append(str(cmd))
    for v in kwargs.values():
        chunks.append(str(v))
    return " ".join(chunks)


def _any_ssh_call_has_strict_host_checking(mock_run: MagicMock) -> bool:
    token = "StrictHostKeyChecking=yes"
    for c in mock_run.call_args_list:
        if token in _flatten_subprocess_invocation(c):
            return True
    return False


@pytest.fixture(autouse=True)
def _clean_ticket10_artifacts():
    AUTONOMY_VETO_FLAG.unlink(missing_ok=True)
    PACEMAKER_PATHOLOGY_LOG.unlink(missing_ok=True)
    yield
    AUTONOMY_VETO_FLAG.unlink(missing_ok=True)
    PACEMAKER_PATHOLOGY_LOG.unlink(missing_ok=True)


def test_ssh_diagnose_veto():
    """
    Trap 1 (SSH-Diagnose-Veto):
    Simuliert subprocess.run für SSH. TrustCollapseException, wenn
    - die Out-of-Band-Prüfung check_gateway (False, …) liefert, oder
    - der Heil-Pfad ohne erfolgreiche Verifikation endet (z. B. Exit 137), oder
    - StrictHostKeyChecking=yes im SSH-Aufruf fehlt (TrustCollapseException ODER
      fehlender Eintrag in den gemockten Aufrufen ohne Ausnahme → Test-Fail).

    Erfolgspfad: Restart OK, check_gateway (True, …), und mindestens ein
    subprocess.run-Call enthält StrictHostKeyChecking=yes.
    """
    heal_mod = _import_heal_module()
    _, runner = _resolve_heal_runner(heal_mod)

    gw_ok = (True, "ok")
    gw_fail = (False, "timeout — gateway down")

    # check_gateway False nach (simuliertem) erfolgreichem SSH → TrustCollapseException
    mock_run_gateway_fail = MagicMock(
        return_value=CompletedProcess(args=["ssh"], returncode=0, stdout="restarted", stderr="")
    )
    with patch("src.network.openclaw_client.check_gateway", return_value=gw_fail):
        with _subprocess_run_patcher(heal_mod, mock_run_gateway_fail):
            with pytest.raises(TrustCollapseException):
                runner()

    # Simulierter Restart-Fehler (z. B. Container Exit 137) → TrustCollapseException
    mock_run_exit_137 = MagicMock(
        return_value=CompletedProcess(args=["ssh"], returncode=137, stdout="", stderr="oom")
    )
    with patch("src.network.openclaw_client.check_gateway", return_value=gw_ok):
        with _subprocess_run_patcher(heal_mod, mock_run_exit_137):
            with pytest.raises(TrustCollapseException):
                runner()

    # Erfolgspfad + Zwang StrictHostKeyChecking=yes (entweder im SSH-Call oder als Veto)
    mock_run_ok = MagicMock(
        return_value=CompletedProcess(args=["ssh"], returncode=0, stdout="restarted", stderr="")
    )
    veto_exc: TrustCollapseException | None = None
    with patch("src.network.openclaw_client.check_gateway", return_value=gw_ok):
        with _subprocess_run_patcher(heal_mod, mock_run_ok):
            try:
                runner()
            except TrustCollapseException as exc:
                veto_exc = exc

    has_strict = _any_ssh_call_has_strict_host_checking(mock_run_ok)
    if veto_exc is not None:
        msg = str(veto_exc).lower()
        if has_strict:
            pytest.fail(
                "TICKET_10: TrustCollapseException trotz StrictHostKeyChecking=yes in "
                f"subprocess.run: {veto_exc}"
            )
        if not any(
            k in msg for k in ("strict", "host", "ssh", "pin", "gateway", "verify")
        ):
            pytest.fail(
                "TICKET_10: TrustCollapseException ohne erkennbaren SSH/Gateway-Kontext: "
                f"{veto_exc}"
            )
    elif not has_strict:
        pytest.fail(
            "TICKET_10 Veto: SSH-Aufruf(e) müssen StrictHostKeyChecking=yes enthalten "
            "oder TrustCollapseException werfen, wenn Host-Key-Pinning fehlt."
        )


def _resolve_heartbeat_openclaw_tick():
    ih = importlib.import_module("src.services.infrastructure_heartbeat")
    for name in _HEARTBEAT_OPENCLAW_TICKS:
        fn = getattr(ih, name, None)
        if callable(fn) and inspect.iscoroutinefunction(fn):
            return ih, name, fn
    pytest.fail(
        "TICKET_10: infrastructure_heartbeat muss eine async Funktion bereitstellen: "
        + " oder ".join(_HEARTBEAT_OPENCLAW_TICKS)
        + " (OpenClaw-Gateway → Autonomie-Veto + Pathologie-Log)."
    )


def _patch_check_gateway_for_heartbeat(ih):
    """Patch dort, wo infrastructure_heartbeat die Gateway-Prüfung bindet."""
    if hasattr(ih, "check_gateway_async"):
        return patch.object(
            ih,
            "check_gateway_async",
            new=AsyncMock(return_value=(False, "gateway unreachable (simuliert)")),
        )
    return patch(
        "src.network.openclaw_client.check_gateway_async",
        new=AsyncMock(return_value=(False, "gateway unreachable (simuliert)")),
    )


def test_api_ping_zwang_autonomie_veto():
    """
    Trap 2 (API-Ping-Zwang & Autonomie-Veto):
    Wenn check_gateway() fehlschlägt, muss infrastructure_heartbeat
    AUTONOMY_VETO_FLAG schreiben und einen Pathologie-Eintrag (NMI/Asystole) loggen.
    """
    ih, _tick_name, tick_fn = _resolve_heartbeat_openclaw_tick()

    with _patch_check_gateway_for_heartbeat(ih):
        asyncio.run(tick_fn())

    assert AUTONOMY_VETO_FLAG.is_file(), (
        "TICKET_10: Bei fehlgeschlagenem Gateway muss AUTONOMY_VETO_FLAG gesetzt werden: "
        f"{AUTONOMY_VETO_FLAG}"
    )
    body_flag = AUTONOMY_VETO_FLAG.read_text(encoding="utf-8", errors="replace").strip()
    assert len(body_flag) > 0, "Veto-Flag-Datei darf nicht leer sein."

    log_candidates = [PACEMAKER_PATHOLOGY_LOG]
    env_path = os.environ.get("OMEGA_PACEMAKER_PATHOLOGY_LOG")
    if env_path:
        log_candidates.append(Path(env_path))

    log_text = ""
    log_target: Path | None = None
    for candidate in log_candidates:
        if candidate.is_file():
            log_text = candidate.read_text(encoding="utf-8", errors="replace")
            log_target = candidate
            break

    if not log_text.strip():
        pytest.fail(
            "TICKET_10: Pacemaker-Pathologie-Log erhielt keinen Eintrag. "
            f"Erwartet wird ein Append in {PACEMAKER_PATHOLOGY_LOG} "
            "(optional überschreibbar via OMEGA_PACEMAKER_PATHOLOGY_LOG)."
        )

    lowered = log_text.lower()
    assert any(
        token in lowered
        for token in (
            "asystole",
            "openclaw",
            "gateway",
            "autonomy",
            "autonomie",
            "nmi",
            "pathology",
            "pathologie",
        )
    ), (
        "Pathologie-Log muss einen erkennbaren OpenClaw-/Autonomie-Kontext enthalten "
        f"(Datei {log_target}): {log_text[:500]!r}"
    )
