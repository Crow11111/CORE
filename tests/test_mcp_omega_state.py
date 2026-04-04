# -*- coding: utf-8 -*-
"""
MCP OMEGA State: Kontrakt für get_episodic_history / record_event (TICKET 11 Phase 1).
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest


def _load_mcp_module():
    try:
        return __import__("src.scripts.mcp_omega_state", fromlist=["*"])
    except ImportError as exc:
        pytest.fail(f"MCP-Modul mcp_omega_state nicht ladbar: {exc}")


@pytest.mark.asyncio
async def test_get_episodic_history_delegates_to_event_store():
    mod = _load_mcp_module()
    if not hasattr(mod, "get_episodic_history"):
        pytest.fail(
            "TICKET 11: Tool get_episodic_history fehlt — Pre-Flight kann Event-Stream nicht lesen."
        )

    fake_rows = [{"id": "u1", "event_type": "t", "memory_hash": "mh"}]

    with patch.object(
        mod._omega_event_store,
        "get_history",
        new=AsyncMock(return_value=fake_rows),
    ) as gh:
        out = await mod.get_episodic_history(agent_id="ag1", limit=5)

    gh.assert_awaited_once()
    call_kw = gh.await_args.kwargs
    assert call_kw.get("agent_id") == "ag1"
    assert call_kw.get("limit") == 5
    data = json.loads(out)
    assert data["events"] == fake_rows
    assert data["count"] == 1


@pytest.mark.asyncio
async def test_record_event_tool_delegates_with_memory_hash():
    mod = _load_mcp_module()
    if not hasattr(mod, "record_event"):
        pytest.fail(
            "TICKET 11: MCP-Tool record_event fehlt — Abschluss kann nicht persistieren."
        )

    with patch.object(
        mod._omega_event_store,
        "record_event",
        new=AsyncMock(
            return_value={"success": True, "id": "abc", "error": None}
        ),
    ) as rec:
        out = await mod.record_event(
            agent_id="a1",
            event_type="task_done",
            content_json='{"ok": true}',
            memory_hash="hash42",
        )

    rec.assert_awaited_once()
    kw = rec.await_args.kwargs
    assert kw["agent_id"] == "a1"
    assert kw["event_type"] == "task_done"
    assert kw["content"] == {"ok": True}
    assert kw["memory_hash"] == "hash42"
    body = json.loads(out)
    assert body.get("success") is True
