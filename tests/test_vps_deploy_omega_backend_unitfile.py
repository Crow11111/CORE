# -*- coding: utf-8 -*-
"""Pflichtstrings in omega-backend.service (VPS systemd)."""
from __future__ import annotations

from pathlib import Path

import pytest

_UNIT = Path(__file__).resolve().parents[1] / "infra" / "vps" / "systemd" / "omega-backend.service"


def test_omega_backend_unit_exists_and_has_execstart_and_port_or_env() -> None:
    if not _UNIT.is_file():
        pytest.fail(f"Unit-Datei fehlt: {_UNIT}")
    text = _UNIT.read_text(encoding="utf-8")
    assert "ExecStart=" in text
    assert "EnvironmentFile=" in text
    assert "32800" in text
    assert "/etc/default/omega-backend" in text
    assert "src.api.main:app" in text
    assert "/opt/omega-backend" in text
    assert "/bin/bash" in text
