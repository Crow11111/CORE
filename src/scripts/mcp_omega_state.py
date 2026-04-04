# -*- coding: utf-8 -*-
"""
OMEGA STATE MCP Server - Proxy Client zu localhost:8049
Verhindert Context-Window-Kollaps durch asynchrone State-Injektion via FastMCP.
Delegiert die eigentliche Arbeit an den lokalen mTLS-Proxy (state_mtls_proxy.py).
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import httpx

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from mcp.server.fastmcp import FastMCP

from src.db import event_store_client as _omega_event_store

mcp = FastMCP("OMEGA_STATE_NEXUS")
PROXY_URL = "http://localhost:8049"

_HANDBOOKS_DIR = Path(_REPO) / "docs" / "03_INFRASTRUCTURE" / "handbooks"
_ROLE_SAFE = re.compile(r"^[\w.-]+$")


def _handbook_file_for_role(role: str) -> Path:
    r = (role or "").strip()
    if not r or not _ROLE_SAFE.match(r):
        raise ValueError(f"ungültiger handbook role (nur [A-Za-z0-9_.-]): {role!r}")
    return _HANDBOOKS_DIR / f"{r}.md"


def _read_handbook_local(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _atomic_write_handbook(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = path.parent
    fd, tmp_name = tempfile.mkstemp(prefix=".hb-", suffix=".tmp", dir=str(parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tf:
            tf.write(content)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


@mcp.tool()
async def read_core_state() -> str:
    """
    Liest den aktuellen 4D CORE State Vector (S * P Symbiose) vom VPS via Proxy.
    Jeder Sub-Agent sollte dies als erstes tun, um seine physikalische/logische Dichte zu messen.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PROXY_URL}/state")
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": (
                "Kein HTTP-Dienst auf localhost:8049 (Sync-Relay/mTLS-State-Proxy). "
                "Typisch: `state_mtls_proxy` / zugehöriger Daemon ist nicht gestartet — "
                "nicht automatisch „VPS offline“."
            ),
        })

@mcp.tool()
async def read_handbook(role: str) -> str:
    """
    Liest das persistente Gedächtnis (Handbuch) für eine spezifische Rolle (z.B. 'system-architect') vom VPS via Proxy.
    Fallback: Datei `docs/03_INFRASTRUCTURE/handbooks/{role}.md` wenn localhost:8049 nicht erreichbar.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PROXY_URL}/handbook/{role}")
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        try:
            p = _handbook_file_for_role(role)
        except ValueError as ve:
            return f"Proxy-Fehler: {e} | {ve}"
        if not p.is_file():
            return (
                f"Fehler beim Lesen des Handbuchs via Proxy: {e}\n"
                f"Kein lokaler Fallback: {p} fehlt."
            )
        body = await asyncio.to_thread(_read_handbook_local, p)
        return f"[FALLBACK lokal, Proxy down] {p}\n\n{body}"

@mcp.tool()
async def update_handbook(role: str, content: str) -> str:
    """
    Überschreibt das persistente Gedächtnis (Handbuch) für die angegebene Rolle auf dem VPS.
    PFLICHT für jeden Sub-Agenten vor seiner Terminierung, falls neue Erkenntnisse gewonnen wurden.
    Fallback: atomar nach `docs/03_INFRASTRUCTURE/handbooks/{role}.md` wenn Proxy down.
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {"content": content, "reason": "MCP-Update"}
            resp = await client.post(f"{PROXY_URL}/handbook/{role}", json=payload)
            resp.raise_for_status()
            return f"[SUCCESS] Handbuch für {role} wurde via Proxy erfolgreich aktualisiert."
    except Exception:
        try:
            p = _handbook_file_for_role(role)
        except ValueError as ve:
            return f"[FAIL] Proxy down und ungültige Rolle: {ve}"
        try:
            await asyncio.to_thread(_atomic_write_handbook, p, content)
            return (
                f"[SUCCESS] lokal (Fallback, Proxy down) — {p}"
            )
        except Exception as e2:
            return f"[FAIL] Proxy und lokaler Fallback: {e2}"


@mcp.tool()
async def get_episodic_history(agent_id: str | None = None, limit: int = 100) -> str:
    """
    Liefert die chronologische Event-Historie aus PostgreSQL (omega_events) für Pre-Flight /
    Episodisches Gedächtnis. Delegiert nicht an den 8049-Proxy — direkter PG-Pfad (TICKET 11).
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        limit = 100
    rows = await _omega_event_store.get_history(agent_id=agent_id, limit=limit)
    return json.dumps(
        {"events": rows, "count": len(rows)},
        ensure_ascii=False,
        default=str,
    )


@mcp.tool()
async def record_event(agent_id: str, event_type: str, content_json: str, memory_hash: str) -> str:
    """
    Schreibt ein append-only Event in omega_events (Abschluss / Audit). content_json muss
    gültiges JSON sein; memory_hash ist Pflicht (Zero-Trust).
    """
    raw = (content_json or "").strip()
    if not raw:
        raw = "{}"
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        return json.dumps(
            {
                "success": False,
                "id": None,
                "error": f"content_json parse error: {e}",
            },
            ensure_ascii=False,
        )
    if not isinstance(body, dict):
        body = {"payload": body}
    result = await _omega_event_store.record_event(
        agent_id=agent_id,
        event_type=event_type,
        content=body,
        memory_hash=memory_hash,
    )
    return json.dumps(result, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
