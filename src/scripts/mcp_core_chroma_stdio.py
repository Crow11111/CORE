# -*- coding: utf-8 -*-
"""
Stdio-MCP-Server: Werkzeug `query_chromadb` aus CORE_EICHUNG.md (Gruppe ChromaDB / 4D_RESONATOR).

Nicht verwechseln mit Browser-DevTools-MCP — dort existiert kein ChromaDB-Tool.
Start: python -m src.scripts.mcp_core_chroma_stdio (cwd: /OMEGA_CORE, .venv aktiv).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from mcp.server.fastmcp import FastMCP

from src.config.chroma_zero_trust_notice import CHROMA_ZERO_TRUST_NOTICE
from src.network.chroma_client import _get_collection_sync, is_configured

mcp = FastMCP("CORE_RESONATOR_ChromaDB")


@mcp.tool()
async def query_chromadb(collection_name: str, query_text: str, n_results: int = 5) -> str:
    """
    Semantische Suche in einer ChromaDB-Collection (CORE Eichung / 4D_RESONATOR).

    Input: collection_name, query_text, optional n_results (Default 5).
    Output: JSON mit Chroma-Feldern (ids, documents, …) und immer **`zero_trust_notice`**
    (wie `query_canon_semantic` / `query_operational_semantic`).
    """
    _zt = {"zero_trust_notice": CHROMA_ZERO_TRUST_NOTICE}

    if not is_configured():
        return json.dumps(
            {
                "error": "ChromaDB nicht konfiguriert (CHROMA_HOST / lokaler Pfad prüfen).",
                **_zt,
            },
            ensure_ascii=False,
        )

    q = (query_text or "").strip()
    if not q:
        return json.dumps(
            {"error": "query_text leer", "collection": collection_name, **_zt},
            ensure_ascii=False,
        )

    def _run_query():
        col = _get_collection_sync(collection_name, create_if_missing=False)
        return col.query(query_texts=[q], n_results=int(n_results))

    try:
        result = await asyncio.to_thread(_run_query)
    except Exception as e:
        return json.dumps(
            {"error": str(e), "collection": collection_name, **_zt},
            ensure_ascii=False,
        )

    out = dict(result) if isinstance(result, dict) else {"raw": result}
    out["collection"] = collection_name
    out["query_text"] = q[:500]
    out["zero_trust_notice"] = CHROMA_ZERO_TRUST_NOTICE
    return json.dumps(out, default=str, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
