# -*- coding: utf-8 -*-
"""
TICKET 9 — Git-Resonanz Veto-Traps für `dread_membrane_daemon`.

Verification-First: `auto_git_push` / `auto_git_pull` werden hier angebunden;
die Implementierung folgt separat (Tests sollen bis dahin fehlschlagen).

Spezifikation: docs/05_AUDIT_PLANNING/TICKET_9_GIT_RESONANCE.md
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

import pytest

# Pain-Flag-Pfad (muss mit Membrane-Konstante übereinstimmen)
PAIN_FLAG_PATH = Path("/tmp/omega_membrane_pain.flag")


def _git_argv(mock_run: MagicMock) -> list[list[str]]:
    """Extrahiert argv-Listen aus subprocess.run-Aufrufen (nur list/tuple-args)."""
    out: list[list[str]] = []
    for c in mock_run.call_args_list:
        args, _kw = c
        if not args:
            continue
        cmd = args[0]
        if isinstance(cmd, (list, tuple)):
            out.append([str(x) for x in cmd])
    return out


@pytest.fixture(autouse=True)
def _clean_pain_flag():
    PAIN_FLAG_PATH.unlink(missing_ok=True)
    yield
    PAIN_FLAG_PATH.unlink(missing_ok=True)


def test_auto_commit_on_pass():
    """
    Trap 1: Bei erfolgreicher Axiom-Prüfung müssen git add → commit → push
    in genau dieser Reihenfolge über subprocess.run laufen (kein echtes Git).
    """
    from src.daemons.dread_membrane_daemon import auto_git_push

    fp = Path("/tmp/ticket9_auto_resonance_dummy.py")
    mock_run = MagicMock(side_effect=lambda cmd, *a, **k: CompletedProcess(cmd, 0))

    with patch("src.daemons.dread_membrane_daemon.subprocess.run", mock_run):
        with patch("src.daemons.dread_membrane_daemon.validate_file") as vf_mock:
            vf_mock.return_value = None
            auto_git_push(fp)

    argv = _git_argv(mock_run)
    assert len(argv) >= 3
    assert argv[0][:2] == ["git", "add"]
    assert argv[1][:2] == ["git", "commit"]
    assert argv[2][:2] == ["git", "push"]
    assert "origin" in argv[2] and "main" in argv[2]
    fp_str = str(fp)
    assert fp_str in argv[0] or argv[0][-1] == fp_str
    joined_commit = " ".join(argv[1])
    assert "Auto-Resonance" in joined_commit and fp_str in joined_commit


def test_git_veto_on_heroin():
    """
    Trap 2: TrustCollapseException → Pain-Flag, git restore, kein commit/push.
    """
    from src.logic_core.anti_heroin_validator import TrustCollapseException

    from src.daemons.dread_membrane_daemon import auto_git_push

    fp = Path("/tmp/ticket9_heroin_dummy.py")
    mock_run = MagicMock(side_effect=lambda cmd, *a, **k: CompletedProcess(cmd, 0))

    with patch("src.daemons.dread_membrane_daemon.subprocess.run", mock_run):
        with patch("src.daemons.dread_membrane_daemon.validate_file") as vf_mock:
            vf_mock.side_effect = TrustCollapseException("heroin_trap")
            auto_git_push(fp)

    argv = _git_argv(mock_run)
    assert any(len(a) >= 2 and a[0] == "git" and a[1] == "restore" for a in argv)
    assert not any(len(a) >= 2 and a[0] == "git" and a[1] == "commit" for a in argv)
    assert not any(len(a) >= 2 and a[0] == "git" and a[1] == "push" for a in argv)

    assert PAIN_FLAG_PATH.is_file()
    body = PAIN_FLAG_PATH.read_text(encoding="utf-8")
    assert len(body.strip()) > 0


def test_pain_on_pull_conflict():
    """
    Trap 3: git pull --rebase mit Non-Zero → Pain-Flag mit festem Kennertext.
    """
    from src.daemons.dread_membrane_daemon import auto_git_pull

    def run_side_effect(cmd, *args, **kwargs):
        seq = list(cmd) if isinstance(cmd, (list, tuple)) else [cmd]
        if len(seq) >= 3 and seq[0] == "git" and seq[1] == "pull" and seq[2] == "--rebase":
            # Ticket: Non-Zero / zu fangende Fehlersituation (Merge-Konflikt).
            if kwargs.get("check"):
                argv = list(cmd) if isinstance(cmd, (list, tuple)) else [cmd]
                raise subprocess.CalledProcessError(1, argv)
            return CompletedProcess(cmd, 1)
        return CompletedProcess(cmd, 0)

    mock_run = MagicMock(side_effect=run_side_effect)

    with patch("src.daemons.dread_membrane_daemon.subprocess.run", mock_run):
        auto_git_pull()

    assert PAIN_FLAG_PATH.is_file()
    text = PAIN_FLAG_PATH.read_text(encoding="utf-8")
    assert "Git Pull/Merge Conflict" in text
