# -*- coding: utf-8 -*-
"""Smoke: Anti-Heroin-Scan auf dem echten src/-Baum (Zero-Trust, kein Mock)."""
from __future__ import annotations

from pathlib import Path

from src.scripts.run_anti_heroin_scan import scan_project


def test_scan_project_clean_repo() -> None:
    root = Path(__file__).resolve().parents[1]
    code, errs = scan_project(root)
    assert code == 0, errs
