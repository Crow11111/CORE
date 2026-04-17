# -*- coding: utf-8 -*-
"""MCP core-chromadb (stdio): Zero-Trust-Feld in jedem query_chromadb-JSON."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.config.chroma_zero_trust_notice import CHROMA_ZERO_TRUST_NOTICE


def _load_mcp_module():
    try:
        return __import__("src.scripts.mcp_core_chroma_stdio", fromlist=["*"])
    except ImportError as exc:
        pytest.fail(f"MCP-Modul mcp_core_chroma_stdio nicht ladbar: {exc}")


@pytest.mark.asyncio
async def test_query_chromadb_success_includes_zero_trust_notice():
    mod = _load_mcp_module()
    if not hasattr(mod, "query_chromadb"):
        pytest.fail("MCP: query_chromadb fehlt.")

    mock_col = MagicMock()
    mock_col.query.return_value = {
        "ids": [["id1"]],
        "documents": [["doc"]],
        "metadatas": [[{"repo_path": "x.md"}]],
        "distances": [[0.12]],
    }
    with patch.object(mod, "is_configured", return_value=True), patch.object(
        mod, "_get_collection_sync", return_value=mock_col
    ):
        out = await mod.query_chromadb(
            collection_name="core_canon", query_text="omega", n_results=3
        )

    data = json.loads(out)
    assert data.get("zero_trust_notice") == CHROMA_ZERO_TRUST_NOTICE
    assert data.get("collection") == "core_canon"
    assert data.get("query_text") == "omega"
    mock_col.query.assert_called_once()


@pytest.mark.asyncio
async def test_query_chromadb_not_configured_includes_zero_trust_notice():
    mod = _load_mcp_module()
    with patch.object(mod, "is_configured", return_value=False):
        out = await mod.query_chromadb(collection_name="x", query_text="y")

    data = json.loads(out)
    assert "error" in data
    assert data.get("zero_trust_notice") == CHROMA_ZERO_TRUST_NOTICE


@pytest.mark.asyncio
async def test_query_chromadb_empty_query_includes_zero_trust_notice():
    mod = _load_mcp_module()
    with patch.object(mod, "is_configured", return_value=True):
        out = await mod.query_chromadb(collection_name="core_canon", query_text="   ")

    data = json.loads(out)
    assert data.get("error") == "query_text leer"
    assert data.get("zero_trust_notice") == CHROMA_ZERO_TRUST_NOTICE
