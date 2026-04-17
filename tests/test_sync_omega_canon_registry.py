# -*- coding: utf-8 -*-
"""Kontrakt: Kanon-Sync sammelt Anker + Seeds ohne ImportError (DB optional gemockt)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_collect_entries_includes_anchor_and_seeds() -> None:
    from src.scripts import sync_omega_canon_registry as mod

    rows = mod._collect_entries(ROOT)
    paths = {r[0] for r in rows}
    assert mod.ANCHOR_NAME in paths
    assert "run_vollkreis_abnahme.py" in paths
    assert "docs/05_AUDIT_PLANNING/TICKET_9_GIT_RESONANCE.md" in paths
    for r in rows:
        assert len(r[4]) == 64  # sha256 hex
        assert r[5] >= 0


@pytest.mark.asyncio
async def test_main_async_ok_when_run_all_succeeds() -> None:
    from src.scripts import sync_omega_canon_registry as mod

    with patch.object(mod, "_ensure_canon_table", new_callable=AsyncMock) as d:
        d.return_value = (True, None)
        with patch.object(mod, "_run_all", new_callable=AsyncMock) as m:
            m.return_value = (99, None)
            code = await mod.main_async()
    assert code == 0
    d.assert_awaited_once()
    m.assert_awaited_once()
