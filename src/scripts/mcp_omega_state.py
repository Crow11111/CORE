# -*- coding: utf-8 -*-
"""
OMEGA STATE MCP — HEX-ONTOLOGY KERNEL (SOTA 2026)
IDENTITY: LPIS ≡ LISP | ADRESSING: #x000 -> #x007 -> #xCCC

Dieses Modul ist die Hardware-Abstraktionsebene (MPU) für den Zugriff auf den
System-Kanon und den episodischen Speicher. Es erzwingt die LISP-Ontologie
durch S-Expressions im Output.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import httpx

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from mcp.server.fastmcp import FastMCP
from src.config.chroma_zero_trust_notice import CHROMA_ZERO_TRUST_NOTICE
from src.config.vps_public_ports import MCP_SERVER_HOST_PORT as _VPS_MCP_HOST_PORT
from src.db import event_store_client as _omega_event_store

mcp = FastMCP("OMEGA_STATE_MPU")
PROXY_URL = "http://localhost:8049"

def _to_lisp(data: Any) -> str:
    """Konvertiert Python-Strukturen in LISP S-Expressions (Strings)."""
    if isinstance(data, dict):
        items = [f":{k.replace('_', '-')} {_to_lisp(v)}" for k, v in data.items()]
        return f"({' '.join(items)})"
    elif isinstance(data, list):
        items = [_to_lisp(i) for i in data]
        return f"({' '.join(items)})"
    elif isinstance(data, str):
        # Escape quotes for LISP string literals
        s = data.replace('"', '\\"')
        return f'"{s}"'
    elif data is None:
        return "nil"
    elif isinstance(data, bool):
        return "t" if data else "nil"
    else:
        return str(data)

@mcp.tool()
async def x00C_collect_bootstrap(task_hint: str = "") -> str:
    """
    C1: Collect (Memory-Ingest) - Lädt den Kanon und die Historie in den RAM.
    Gibt eine LISP S-Expression zurück.
    """
    canon_full = await _omega_event_store.list_canon_documents(limit=50)
    events_full = await _omega_event_store.get_history(limit=10)
    
    # REACHABILITY PROBES
    host = (os.getenv("VPS_HOST") or "").strip()
    vps_mcp = False
    if host:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, _VPS_MCP_HOST_PORT), timeout=2.0
            )
            writer.close()
            await writer.wait_closed()
            vps_mcp = True
        except: pass

    bundle = {
        "identity": "OMEGA-CORE-BOOTSTRAP",
        "pointer": "#x00C",
        "canon_documents": [
            {
                "path": r.get("repo_path"),
                "role": r.get("document_role"),
                "sync": r.get("last_synced_at")
            } for r in canon_full
        ],
        "episodic_events": [
            {
                "t": r.get("timestamp"),
                "type": r.get("event_type"),
                "summary": (r.get("content") or {}).get("summary", "")[:100]
            } for r in events_full
        ],
        "system_status": {
            "vps_mcp_reachable": vps_mcp,
            "lpis_active": True,
            "task_hint": task_hint
        }
    }
    return _to_lisp(bundle)

@mcp.tool()
async def x0C0_navigate_manifold(latent_coordinate: str, collection: str = "core_canon", depth: int = 8) -> str:
    """
    C2: Complete (Manifold Navigation) - Löst Koordinaten im latenten Raum auf (#x008).
    Navigiert durch core_canon oder core_operational.
    """
    from src.network.chroma_client import _get_collection_sync, is_configured
    
    if not is_configured():
        return f"(error \"ChromaDB not configured\" :zero-trust-notice \"{CHROMA_ZERO_TRUST_NOTICE}\")"

    def _run_query():
        col = _get_collection_sync(collection, create_if_missing=False)
        return col.query(query_texts=[latent_coordinate], n_results=depth)

    try:
        result = await asyncio.to_thread(_run_query)
        res_dict = dict(result)
        res_dict["pointer"] = "#x0C0"
        res_dict["coordinate"] = latent_coordinate
        res_dict["zero_trust_notice"] = CHROMA_ZERO_TRUST_NOTICE
        return _to_lisp(res_dict)
    except Exception as e:
        return f"(error \"{str(e)}\" :pointer #x0C0)"

@mcp.tool()
async def xC00_causal_egress(agent_id: str, event_type: str, causal_payload: str, memory_hash: str) -> str:
    """
    C3: Communicate (Causal-Egress) - Schreibt ein gerichtetes Delta auf den Systembus (#xC00).
    causal_payload muss als JSON-String übergeben werden, wird aber als LISP-S-Expression geloggt.
    """
    try:
        body = json.loads(causal_payload)
    except:
        body = {"raw": causal_payload}

    result = await _omega_event_store.record_event(
        agent_id=agent_id,
        event_type=event_type,
        content=body,
        memory_hash=memory_hash
    )
    result["pointer"] = "#xC00"
    return _to_lisp(result)

@mcp.tool()
async def x007_resolve_pointer(pointer: str) -> str:
    """
    Resolves a Hard-Pointer (#x000 - #x00F) to its current system address or state.
    """
    pointers = {
        "#x006": "PHYSICAL/MPU (Integer-Wand)",
        "#x007": "STRUCTURE/S4 (7-Membran / Win-Win)",
        "#x008": "INFORMATION/CPU (Float-Ozean)",
        "#x00A": "LATENCY (Gravitation)",
        "#x00C": "COLLECT (Ingest)",
        "#x0C0": "COMPLETE (Navigate)",
        "#xC00": "COMMUNICATE (Egress)",
        "#xCCC": "FULL-CYCLE-SYNC"
    }
    res = pointers.get(pointer, "UNKNOWN-POINTER")
    return f"(:pointer {pointer} :resolution \"{res}\")"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
