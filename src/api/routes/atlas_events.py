# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
ATLAS Event-Ingest: Scout/Externe Events annehmen, auf Disk + optional ChromaDB.

POST /api/atlas/event – Body: { source, node_id, event_type, timestamp?, priority?, data? }
Schreibt nach data/events/{id}.json und optional in ChromaDB collection "events".
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/atlas", tags=["atlas-events"])

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EVENTS_DIR = os.path.join(_ROOT, "data", "events")


class EventIn(BaseModel):
    source: str = "scout"
    node_id: str = "unknown"
    event_type: str
    timestamp: str | None = None
    priority: str = "medium"
    data: dict | None = None


@router.post("/event")
def ingest_event(body: EventIn):
    """Event speichern (data/events + optional ChromaDB)."""
    event_id = str(uuid.uuid4())
    ts = body.timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    event = {
        "id": event_id,
        "source": body.source,
        "node_id": body.node_id,
        "event_type": body.event_type,
        "timestamp": ts,
        "priority": body.priority,
        "data": body.data or {},
    }
    os.makedirs(EVENTS_DIR, exist_ok=True)
    path = os.path.join(EVENTS_DIR, f"{event_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)
    meta = {
        "source": event["source"],
        "node_id": event["node_id"],
        "event_type": event["event_type"],
        "timestamp": event["timestamp"],
        "priority": event["priority"],
    }
    try:
        from src.network.chroma_client import add_event_to_chroma, is_configured
        if is_configured():
            add_event_to_chroma(event_id, event, meta)
    except Exception:
        pass
    return {"ok": True, "id": event_id, "path": path}


@router.get("/events")
def list_events(limit: int = 50):
    """Letzte Events (aus data/events) auflisten."""
    if not os.path.isdir(EVENTS_DIR):
        return {"ok": True, "events": []}
    files = sorted(
        [f for f in os.listdir(EVENTS_DIR) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(EVENTS_DIR, f)),
        reverse=True,
    )[:limit]
    events = []
    for f in files:
        p = os.path.join(EVENTS_DIR, f)
        try:
            with open(p, encoding="utf-8") as fp:
                events.append(json.load(fp))
        except Exception:
            pass
    return {"ok": True, "events": events}


def _last_n_event_ids(n: int = 3) -> list[str]:
    if not os.path.isdir(EVENTS_DIR):
        return []
    files = sorted(
        [f for f in os.listdir(EVENTS_DIR) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(EVENTS_DIR, f)),
        reverse=True,
    )[:n]
    ids = []
    for f in files:
        p = os.path.join(EVENTS_DIR, f)
        try:
            with open(p, encoding="utf-8") as fp:
                obj = json.load(fp)
                ids.append(obj.get("id", f.removesuffix(".json")))
        except Exception:
            pass
    return ids


@router.get("/status")
def atlas_status():
    """(1) OpenClaw Gateway erreichbar, (2) Event-Ingest vorhanden, (3) Voice-Roles-Anzahl, (4) letzte 3 Event-IDs."""
    from src.network.openclaw_client import check_gateway
    from src.config.voice_config import OSMIUM_VOICE_CONFIG
    ok, _msg = check_gateway()
    return {
        "openclaw_gateway_reachable": ok,
        "event_ingest_present": True,
        "voice_roles_count": len(OSMIUM_VOICE_CONFIG),
        "last_3_event_ids": _last_n_event_ids(3),
    }
