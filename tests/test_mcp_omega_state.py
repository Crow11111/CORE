# -*- coding: utf-8 -*-
"""
MCP OMEGA State: Kontrakt für get_episodic_history / record_event (TICKET 11 Phase 1).
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.mark.asyncio
async def test_list_canon_documents_tool_delegates_to_event_store():
    mod = _load_mcp_module()
    if not hasattr(mod, "list_canon_documents"):
        pytest.fail(
            "MCP: list_canon_documents fehlt — Kanon-Pre-Flight nicht abrufbar."
        )

    fake = [{"repo_path": "a.md", "document_role": "referenced"}]
    with patch.object(
        mod._omega_event_store,
        "list_canon_documents",
        new=AsyncMock(return_value=fake),
    ) as lc:
        out = await mod.list_canon_documents(limit=10)

    lc.assert_awaited_once()
    assert lc.await_args.kwargs.get("limit") == 10
    data = json.loads(out)
    assert data["count"] == 1
    assert data["documents"] == fake


@pytest.mark.asyncio
async def test_get_orchestrator_bootstrap_returns_bundle_keys():
    mod = _load_mcp_module()
    if not hasattr(mod, "get_orchestrator_bootstrap"):
        pytest.fail("MCP: get_orchestrator_bootstrap fehlt — Orchestrator-Basis-Kontext nicht abrufbar.")

    with (
        patch.object(
            mod._omega_event_store,
            "list_canon_documents",
            new=AsyncMock(return_value=[{"repo_path": "a.md", "document_role": "r", "anchor_section": "1", "last_synced_at": "t"}]),
        ),
        patch.object(
            mod._omega_event_store,
            "get_history",
            new=AsyncMock(
                return_value=[
                    {
                        "timestamp": "x",
                        "event_type": "e",
                        "agent_id": "ag",
                        "content": {"summary": "done"},
                    }
                ]
            ),
        ),
        patch.object(mod, "_probe_vps_mcp_http", new=AsyncMock(return_value=True)),
    ):
        out = await mod.get_orchestrator_bootstrap(
            event_limit=5, canon_limit=10, task_hint="kong route"
        )

    data = json.loads(out)
    assert data["canon_count"] == 1
    assert data["events_count"] == 1
    assert "gaps" in data and "recommendations" in data
    assert data.get("local_proxy_probe_enabled") is False
    assert data["reachability"]["vps_mcp_http"] is True
    assert data["reachability"]["dev_workstation_state_proxy_8049"] is None
    assert any("kong" in (r or "").lower() for r in data["recommendations"])


@pytest.mark.asyncio
async def test_get_orchestrator_bootstrap_proxy_down_adds_gap_when_probe_returns_false():
    """Simuliert fehlgeschlagenen 8049-Check nach aktivierter Probe (z. B. Env=1)."""
    mod = _load_mcp_module()
    if not hasattr(mod, "get_orchestrator_bootstrap"):
        pytest.fail("MCP: get_orchestrator_bootstrap fehlt.")

    with (
        patch.object(
            mod._omega_event_store,
            "list_canon_documents",
            new=AsyncMock(
                return_value=[
                    {
                        "repo_path": "a.md",
                        "document_role": "r",
                        "anchor_section": "1",
                        "last_synced_at": "t",
                    }
                ]
            ),
        ),
        patch.object(
            mod._omega_event_store,
            "get_history",
            new=AsyncMock(
                return_value=[
                    {
                        "timestamp": "x",
                        "event_type": "e",
                        "agent_id": "ag",
                        "content": {"summary": "done"},
                    }
                ]
            ),
        ),
        patch.object(mod, "_probe_vps_mcp_http", new=AsyncMock(return_value=True)),
        patch.object(mod, "_probe_local_state_proxy", new=AsyncMock(return_value=False)),
    ):
        out = await mod.get_orchestrator_bootstrap()

    data = json.loads(out)
    assert data["reachability"]["dev_workstation_state_proxy_8049"] is False
    assert any("8049" in g for g in data["gaps"])


@pytest.mark.asyncio
async def test_query_canon_semantic_requires_non_empty_query():
    mod = _load_mcp_module()
    if not hasattr(mod, "query_canon_semantic"):
        pytest.fail("MCP: query_canon_semantic fehlt — Kanon-Semantik nicht abfragbar.")
    out = await mod.query_canon_semantic(query_text="   ")
    data = json.loads(out)
    assert "error" in data
    assert "zero_trust_notice" in data


@pytest.mark.asyncio
async def test_query_canon_semantic_not_configured():
    mod = _load_mcp_module()
    with patch("src.network.chroma_client.is_configured", return_value=False):
        out = await mod.query_canon_semantic(query_text="VPS Kong")
    data = json.loads(out)
    assert "error" in data
    assert data.get("collection") == "core_canon"
    assert "zero_trust_notice" in data


@pytest.mark.asyncio
async def test_query_canon_semantic_returns_chroma_shape():
    mod = _load_mcp_module()
    fake = {
        "ids": [["c1"]],
        "documents": [["text chunk"]],
        "metadatas": [[{"repo_path": "x.md"}]],
        "distances": [[0.12]],
    }
    col = MagicMock()
    col.query.return_value = fake
    with (
        patch("src.network.chroma_client.is_configured", return_value=True),
        patch("src.network.chroma_client._get_collection_sync", return_value=col),
    ):
        out = await mod.query_canon_semantic(query_text="omega backend", n_results=5)
    data = json.loads(out)
    assert data.get("collection") == "core_canon"
    assert data.get("ids") == [["c1"]]
    assert "zero_trust_notice" in data and len(data["zero_trust_notice"]) > 20
    col.query.assert_called_once()
    assert col.query.call_args.kwargs.get("n_results") == 5


@pytest.mark.asyncio
async def test_query_operational_semantic_not_configured():
    mod = _load_mcp_module()
    if not hasattr(mod, "query_operational_semantic"):
        pytest.fail("MCP: query_operational_semantic fehlt.")
    with patch("src.network.chroma_client.is_configured", return_value=False):
        out = await mod.query_operational_semantic(query_text="Kong Port")
    data = json.loads(out)
    assert "error" in data
    assert data.get("collection") == "core_operational"
    assert "zero_trust_notice" in data


@pytest.mark.asyncio
async def test_query_operational_semantic_returns_chroma_shape():
    mod = _load_mcp_module()
    fake = {"ids": [["o1"]], "documents": [["chunk"]], "metadatas": [[{}]], "distances": [[0.2]]}
    col = MagicMock()
    col.query.return_value = fake
    with (
        patch("src.network.chroma_client.is_configured", return_value=True),
        patch("src.network.chroma_client._get_collection_sync", return_value=col),
    ):
        out = await mod.query_operational_semantic(query_text="VPS Chroma Port", n_results=4)
    data = json.loads(out)
    assert data.get("collection") == "core_operational"
    assert data.get("ids") == [["o1"]]
    assert "zero_trust_notice" in data
