# -*- coding: utf-8 -*-
"""Kontrakt: Block G darf nicht fest auf localhost:8000/status zeigen (Prod-Parität mit Block A)."""

from __future__ import annotations

from pathlib import Path


def test_run_vollkreis_agent_pool_check_uses_core_base_url_not_hardcoded_localhost() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "run_vollkreis_abnahme.py").read_text(encoding="utf-8", errors="replace")
    assert "G: Substanz (Kernel-Mechanik)" in text
    assert 'f"{CORE_BASE_URL}/status"' in text or "f'{CORE_BASE_URL}/status'" in text
    assert "http://localhost:8000/status" not in text, (
        "Block G muss CORE_BASE_URL nutzen — festes localhost:8000 brechen Prod-Abnahme."
    )
