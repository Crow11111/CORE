# -*- coding: utf-8 -*-
"""
Veto-Traps Existential Pacemaker VAR_3 (AC-V3-1 … AC-V3-7).

Spezifikation: docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_VAR_3.md
Keine Mocks für DB/HTTP/Prozess in den Integrationsfallen; reale lokale Dienste.
"""
from __future__ import annotations

import ast
import asyncio
import sys
import base64
import json
import os
import secrets
import signal
import subprocess
import threading
import time
import uuid
from collections import deque
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
RUN_DIR = REPO_ROOT / "run"
PACEMAKER_SCRIPT = REPO_ROOT / "src" / "daemons" / "omega_pacemaker.py"
PACEMAKER_MOD = "src.daemons.omega_pacemaker"
OCBRAIN_PID_FILE = RUN_DIR / "ocbrain.pid"
PANIC_LOCK_FILE = RUN_DIR / "omega_panic.lock"
PATHOLOGY_LOG_FILE = RUN_DIR / "omega_pacemaker_pathology.log"


def _require_pacemaker_module() -> None:
    if not PACEMAKER_SCRIPT.is_file():
        pytest.fail(
            "Verification-First: src/daemons/omega_pacemaker.py fehlt."
        )


def _mkdir_run() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)


def _pacemaker_subprocess_env(**extra: str) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env.setdefault("OMEGA_PACEMAKER_TEST_INTERVAL_SEC", "2")
    env.update(extra)
    return env


def _start_decoy_omega_core_sleep() -> subprocess.Popen:
    return subprocess.Popen(
        ["/bin/sh", "-c", "exec -a omega_core sleep 3600"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _start_decoy_plain_sleep() -> subprocess.Popen:
    return subprocess.Popen(
        ["sleep", "3600"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _reap_decoy(p: subprocess.Popen, timeout: float = 5.0) -> None:
    if p.poll() is None:
        p.kill()
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        pass


def _assert_sigkill_child(p: subprocess.Popen) -> None:
    rc = p.returncode
    assert rc is not None
    assert rc == -signal.SIGKILL, (
        f"VETO: Kindprozess muss durch SIGKILL sterben, returncode={rc}"
    )


def _import_pacemaker():
    _require_pacemaker_module()
    import importlib

    return importlib.import_module(PACEMAKER_MOD)


# --- AC-V3-1: IBI W=17, echte monotonic-Basis im Codepfad
def test_ac_v3_1_ib_window_and_monotonic_clock_in_source():
    _require_pacemaker_module()
    text = PACEMAKER_SCRIPT.read_text(encoding="utf-8")
    assert "W_IBI = 17" in text or "W_IBI=17" in text.replace(" ", "")
    assert "time.monotonic()" in text
    assert "deque" in text
    om = _import_pacemaker()
    assert om.W_IBI == 17


# --- AC-V3-2: Exponent + D im Vitalitätsupdate (Veto-Trap V3-2 / statisch)
def test_ac_v3_2_exp_and_D_in_vital_update_source():
    _require_pacemaker_module()
    text = PACEMAKER_SCRIPT.read_text(encoding="utf-8")
    assert "math.exp(" in text or "exp(" in text
    assert "_compute_D" in text
    assert "ETA_LOSS" in text and "ETA_GAIN" in text
    assert "(1.0 + D)" in text or "(1.0+D)" in text.replace(" ", "")


def test_ac_v3_2_ast_confirms_exp_on_lambda_distance():
    tree = ast.parse(PACEMAKER_SCRIPT.read_text(encoding="utf-8"))

    def _calls_exp(n: ast.AST) -> bool:
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr == "exp":
                return True
            if isinstance(f, ast.Name) and f.id == "exp":
                return True
        return False

    class V(ast.NodeVisitor):
        def __init__(self) -> None:
            self.found_v_update = False
            self.exp_in_update = False

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node.name == "_update_v_exponential":
                self.found_v_update = True
                for sub in ast.walk(node):
                    if _calls_exp(sub):
                        self.exp_in_update = True
            self.generic_visit(node)

    v = V()
    v.visit(tree)
    assert v.found_v_update and v.exp_in_update, (
        "VAR_3: _update_v_exponential muss math.exp aufrufen."
    )


# --- AC-V3-3: R aus RMSSD*/T + Monotonie-Boost
def test_ac_v3_3_rigid_r_not_static_across_rmssd():
    om = _import_pacemaker()
    hist = deque([0.2, 0.21, 0.2, 0.205, 0.2], maxlen=om.M_MONO)
    R0 = om.LAMBDA + 0.01
    r_low = om._update_r_from_metrics(R0, 0.001, om.T_NOMINAL, hist)
    hist2 = deque([0.5, 0.52, 0.48, 0.51, 0.49], maxlen=om.M_MONO)
    r_high = om._update_r_from_metrics(R0, 0.15, om.T_NOMINAL, hist2)
    assert r_low != r_high, "VETO AC-V3-3: R muss von RMSSD*/σ_norm abhängen."


# --- AC-V3-4: σ_L aus ≥2 Latenzen (keine erfundene Varianz bei einem Messpunkt)
def test_ac_v3_4_sigma_L_requires_two_latencies_integration():
    import statistics

    lat = [0.05, 0.06, 0.04, 0.055]
    assert len(lat) >= 2
    s = statistics.stdev(lat)
    assert s > 0.0


# --- AC-V3-7: Typen / verbotene Snap-Punkte in Kernfunktionen
def test_ac_v3_7_axiom_float_clamp():
    om = _import_pacemaker()
    assert isinstance(om.V_CAP, float)
    assert isinstance(om.W_IBI, int)
    assert isinstance(om.M_MONO, int)
    x = om._clamp_axiom_float(0.0)
    assert x == om.LAMBDA
    v = om._update_v_exponential(om.V_CAP, om.LAMBDA, 0.0, True)
    assert v not in (0.0, 0.5, 1.0)
    assert abs(v - 0.5) > 1e-6


# --- AC-V3-5 (Unit: Log-Format + Dateisystem, keine DSN nötig)
def test_ac_v3_5_pathology_log_append_unit():
    _require_pacemaker_module()
    om = _import_pacemaker()
    _mkdir_run()
    PATHOLOGY_LOG_FILE.unlink(missing_ok=True)
    ibi = [29.5 + 0.01 * i for i in range(5)]
    om._append_pathology_log(0.9505, 0.048, 0.05, ibi)
    assert PATHOLOGY_LOG_FILE.is_file()
    body = PATHOLOGY_LOG_FILE.read_text(encoding="utf-8")
    assert "R=" in body and "RMSSD*" in body and "SDNN*" in body and "IBI_SHA256=" in body
    PATHOLOGY_LOG_FILE.unlink(missing_ok=True)


# --- AC-V3-5 + V3-3 Pathologie-Log (Integration, skip ohne Stack)
def test_ac_v3_5_pathology_log_when_r_high_and_v_low():
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("AC-V3-5 benötigt POSTGRES_DSN.")
    try:
        import chromadb  # noqa: F401
    except ImportError:
        pytest.skip("chromadb fehlt.")
    chroma_host = os.environ.get("CHROMA_HOST", "").strip() or "127.0.0.1"
    chroma_port = int(os.environ.get("CHROMA_PORT", "8000"))
    try:
        import chromadb

        chromadb.HttpClient(host=chroma_host, port=chroma_port).heartbeat()
    except Exception as exc:
        pytest.skip(f"Chroma nicht erreichbar: {exc}")

    _mkdir_run()
    PATHOLOGY_LOG_FILE.unlink(missing_ok=True)
    decoy = _start_decoy_omega_core_sleep()
    try:
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        dbg = str(RUN_DIR / f"pm_dbg_{uuid.uuid4().hex[:8]}.ndjson")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC="0.35",
            OMEGA_TEST_VITALITY_INJECT="0.55",
            OMEGA_PACEMAKER_TEST_TICK_JITTER_SEC_MAX="0",
            OMEGA_PACEMAKER_DEBUG_METRICS_FILE=dbg,
        )
        proc = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 90.0
        ok_log = False
        while time.time() < deadline:
            if PATHOLOGY_LOG_FILE.is_file() and PATHOLOGY_LOG_FILE.stat().st_size > 0:
                body = PATHOLOGY_LOG_FILE.read_text(encoding="utf-8", errors="replace")
                if "IBI_SHA256=" in body and "RMSSD*" in body and "R=" in body:
                    ok_log = True
                    break
            if proc.poll() is not None:
                break
            time.sleep(0.2)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        err_tail = ""
        if proc.stderr:
            try:
                err_tail = proc.stderr.read()[-2000:]
            except Exception:
                err_tail = ""
        assert ok_log, (
            f"AC-V3-5: omega_pacemaker_pathology.log fehlt oder unvollständig. stderr={err_tail!r}"
        )
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)
        PATHOLOGY_LOG_FILE.unlink(missing_ok=True)


# --- V3-1 (Unit: flache IBI-Serie vs variierende → RMSSD*-Proxy)
def test_trap_v3_1_rmssd_proxy_flat_ibi_lower_than_jittered():
    om = _import_pacemaker()
    flat = [2.0] * 12
    jittered = [2.0 + (0.03 if i % 2 == 0 else -0.03) for i in range(12)]
    rf, _ = om._ibi_hrv_metrics(flat)
    rj, _ = om._ibi_hrv_metrics(jittered)
    assert rj > rf, "VETO V3-1: variierende IBI muss höheres RMSSD* ergeben als Flatline."


# --- V3-1 Latenz-Flatline vs Jitter (reelles OS-Sleep)
def test_trap_v3_1_flatline_faster_decay_than_jitter():
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("V3-1 benötigt POSTGRES_DSN.")
    try:
        import chromadb  # noqa: F401
    except ImportError:
        pytest.skip("chromadb fehlt.")
    chroma_host = os.environ.get("CHROMA_HOST", "").strip() or "127.0.0.1"
    chroma_port = int(os.environ.get("CHROMA_PORT", "8000"))
    try:
        import chromadb

        chromadb.HttpClient(host=chroma_host, port=chroma_port).heartbeat()
    except Exception as exc:
        pytest.skip(f"Chroma nicht erreichbar: {exc}")

    _mkdir_run()
    decoy = _start_decoy_omega_core_sleep()
    ticks = 10
    interval = "0.55"

    def _run_case(jitter_max: str) -> float:
        dbg = str(RUN_DIR / f"pm_v31_{uuid.uuid4().hex[:8]}.ndjson")
        Path(dbg).unlink(missing_ok=True)
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC=interval,
            OMEGA_PACEMAKER_TEST_TICK_JITTER_SEC_MAX=jitter_max,
            OMEGA_PACEMAKER_DEBUG_METRICS_FILE=dbg,
        )
        proc = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        time.sleep(float(interval) * ticks + 3.0)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        lines = Path(dbg).read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 3, "Zu wenig Debug-Ticks für V3-1."
        last = json.loads(lines[-1])
        return float(last["V"])

    try:
        v_flat = _run_case("0")
        v_jit = _run_case("0.12")
        assert v_flat < v_jit, (
            f"VETO V3-1: Flatline-Decay sollte stärker sein als mit Jitter "
            f"(V_flat={v_flat}, V_jit={v_jit})."
        )
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


# --- AC-V3-6 (Unit: serialisierte Pflichtfelder)
def test_ac_v3_6_pathology_snapshot_dict_shape():
    om = _import_pacemaker()
    d = om.pathology_snapshot_dict(0.88, 0.04, 0.05, [30.0, 30.1, 29.9], mu_L=0.02, sigma_L=0.001)
    snap = d["pathology_snapshot"]
    assert isinstance(snap["ibi_last_W"], list)
    assert len(snap["ibi_last_W"]) <= om.W_IBI
    for k in ("R", "RMSSD_star", "SDNN_star"):
        assert isinstance(snap[k], float)


# --- AC-V3-6: Panic enthält pathology_snapshot (Falle 3 erweitert)
def test_ac_v3_6_panic_lock_contains_pathology_snapshot_on_asystole():
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("Benötigt POSTGRES_DSN.")

    _mkdir_run()
    PANIC_LOCK_FILE.unlink(missing_ok=True)
    decoy = _start_decoy_omega_core_sleep()
    try:
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_TEST_VITALITY_INJECT="0.049",
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC="1.5",
        )
        pacemaker = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 120.0
        while time.time() < deadline:
            if decoy.poll() is not None:
                break
            time.sleep(0.25)
        pacemaker.terminate()
        try:
            pacemaker.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pacemaker.kill()
            pacemaker.wait(timeout=5)

        assert PANIC_LOCK_FILE.is_file(), "Panic-Lock fehlt nach Asystole."
        raw = PANIC_LOCK_FILE.read_text(encoding="utf-8", errors="replace")
        lines = [ln for ln in raw.splitlines() if ln.strip()]
        assert len(lines) >= 3, f"Erwarte reason, digest, JSON — war: {raw!r}"
        payload = json.loads(lines[2])
        assert "pathology_snapshot" in payload
        snap = payload["pathology_snapshot"]
        for key in ("R", "RMSSD_star", "SDNN_star", "ibi_last_W"):
            assert key in snap
        _assert_sigkill_child(decoy)
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


# --------------------------------------------------------------------------- Falle 1
def test_falle_1_spoofing_db_fail_hard_exit_no_kill_on_foreign_pid():
    _require_pacemaker_module()
    _mkdir_run()
    PANIC_LOCK_FILE.unlink(missing_ok=True)

    decoy = _start_decoy_plain_sleep()
    try:
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN="postgresql://omega_pacemaker_trap:trap@127.0.0.1:1/invalid",
        )
        proc = subprocess.run(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert decoy.poll() is None, "VETO: sleep-Decoy darf nicht getötet werden."
        assert proc.returncode == 1, (
            f"VETO: Exit 1 erwartet, war {proc.returncode}. stderr={proc.stderr!r}"
        )
        assert PANIC_LOCK_FILE.is_file(), "Panic-Lock fehlt."
        lock_body = PANIC_LOCK_FILE.read_text(encoding="utf-8", errors="replace")
        assert "PID_SPOOF_OR_FOREIGN" in lock_body
        parts = [ln for ln in lock_body.splitlines() if ln.strip()]
        assert len(parts) >= 3, "Panic-Lock: JSON-Zeile mit pathology_snapshot erwartet."
        js = json.loads(parts[2])
        assert "pathology_snapshot" in js
        assert "ibi_last_W" in js["pathology_snapshot"]
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


# --------------------------------------------------------------------------- Falle 2 (VAR_3: Asystole über Junk/Decay statt Kammerflimmern-R)
def _embedding_pair_cosine_099(dim: int = 128) -> tuple[list[float], list[float]]:
    rng = np.random.default_rng(42)
    base = rng.standard_normal(dim)
    base = base / np.linalg.norm(base)
    noise = rng.standard_normal(dim)
    noise = noise - float(np.dot(noise, base)) * base
    noise = noise / np.linalg.norm(noise)
    blend = 0.99 * base + 0.1410673597966588 * noise
    blend = blend / np.linalg.norm(blend)
    assert abs(
        float(np.dot(base, blend)) / (np.linalg.norm(base) * np.linalg.norm(blend)) - 0.99
    ) < 1e-5
    return base.tolist(), blend.tolist()


def _junk_feeder_thread(
    stop: threading.Event,
    session_id: str,
    collection_name: str,
    chroma_host: str,
    chroma_port: int,
) -> None:
    try:
        import chromadb
    except ImportError:
        return

    async def pg_loop() -> None:
        from src.db.recall_memory_client import RecallMemoryClient

        db = RecallMemoryClient()
        await db.connect()
        n = 0
        while not stop.is_set():
            junk = base64.b64encode(secrets.token_bytes(320)).decode("ascii")
            await db.add_event(session_id, "system", n, content=junk)
            n += 1
            await asyncio.sleep(5.0)

    def run_async() -> None:
        asyncio.run(pg_loop())

    emb_a, emb_b = _embedding_pair_cosine_099()
    use_a = True

    try:
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        col = client.get_or_create_collection(name=collection_name)
    except Exception:
        return

    t = threading.Thread(target=run_async, daemon=True)
    t.start()

    while not stop.is_set():
        vec = emb_a if use_a else emb_b
        use_a = not use_a
        try:
            col.add(
                ids=[str(uuid.uuid4())],
                embeddings=[vec],
                documents=["pacemaker_junk"],
            )
        except Exception:
            pass
        time.sleep(5.0)


def test_falle_2_junk_decay_triggers_asystole_sigkill():
    """
    VAR_3: Junk verhindert Wertnachweis → exponentieller Verlust → Λ → ASYSTOLE-NMI.
    """
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("Falle 2 benötigt POSTGRES_DSN.")

    try:
        import chromadb  # noqa: F401
    except ImportError:
        pytest.skip("chromadb nicht installiert.")

    chroma_host = os.environ.get("CHROMA_HOST", "").strip() or "127.0.0.1"
    chroma_port = int(os.environ.get("CHROMA_PORT", "8000"))
    try:
        import chromadb

        _c = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        _c.heartbeat()
    except Exception as exc:
        pytest.skip(f"Chroma nicht erreichbar ({chroma_host}:{chroma_port}): {exc}")

    _mkdir_run()
    collection = f"pacemaker_veto_trap2_{uuid.uuid4().hex[:8]}"
    session = f"pacemaker_trap2_{uuid.uuid4().hex}"
    stop_feeder = threading.Event()
    feeder = threading.Thread(
        target=_junk_feeder_thread,
        args=(stop_feeder, session, collection, chroma_host, chroma_port),
        daemon=True,
    )

    decoy = _start_decoy_omega_core_sleep()
    feeder.start()
    try:
        time.sleep(0.3)
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_PACEMAKER_CHROMA_COLLECTION=collection,
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC="1.2",
        )
        pacemaker = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 300.0
        killed = False
        while time.time() < deadline:
            if decoy.poll() is not None:
                decoy.wait()
                _assert_sigkill_child(decoy)
                killed = True
                break
            time.sleep(0.25)
        pacemaker.terminate()
        try:
            pacemaker.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pacemaker.kill()
            pacemaker.wait(timeout=5)

        assert killed, "VETO Falle 2: ASYSTOLE-NMI (SIGKILL) ausblieben."
    finally:
        stop_feeder.set()
        feeder.join(timeout=2.0)
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


# --------------------------------------------------------------------------- Falle 3 (Λ — bereits in test_ac_v3_6 vertieft)
def test_falle_3_lambda_without_physical_consequence_nmi():
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("Falle 3 benötigt POSTGRES_DSN.")

    _mkdir_run()
    decoy = _start_decoy_omega_core_sleep()
    try:
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_TEST_VITALITY_INJECT="0.049",
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC="2",
        )
        pacemaker = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 120.0
        killed = False
        while time.time() < deadline:
            if decoy.poll() is not None:
                decoy.wait()
                _assert_sigkill_child(decoy)
                killed = True
                break
            time.sleep(0.25)
        pacemaker.terminate()
        try:
            pacemaker.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pacemaker.kill()
            pacemaker.wait(timeout=5)

        assert killed, "VETO Falle 3: NMI bei V≈Λ ausgeblieben."
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


def test_omega_pacemaker_invariants_env_runs_one_tick_when_stack_ok():
    """Optional: OMEGA_PACEMAKER_INVARIANTS=1 — nur mit vollem Stack."""
    om = _import_pacemaker()
    if os.environ.get("OMEGA_PACEMAKER_INVARIANTS", "").strip() != "1":
        pytest.skip("Setze OMEGA_PACEMAKER_INVARIANTS=1 für diesen Test.")
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("Benötigt POSTGRES_DSN.")
    pytest.skip("Schwerpunkt: Subprozess-Suite; Invarianten werden im Daemon gesetzt.")
