# -*- coding: utf-8 -*-
"""Kontrakt: Loopback-Verify darf nicht durch fehlschlagendes curl + head grün werden."""

from __future__ import annotations

from pathlib import Path


def test_verify_vps_omega_backend_uses_bash_pipefail() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "src" / "scripts" / "verify_vps_omega_backend_http.py").read_text(
        encoding="utf-8", errors="replace"
    )
    assert "set -o pipefail" in text
    assert "bash -lc" in text
