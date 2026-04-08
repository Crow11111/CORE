# -*- coding: utf-8 -*-
"""
PostgreSQL Event Store (omega_events) — TICKET 11 Phase 1.

Duale Topologie: diskrete Events / Kausalität in PostgreSQL (Int/Relationen);
semantische Float-Resonanz bleibt Chroma/pgvector (multi_view_client).

Zero-Trust: memory_hash ist Pflichtfeld bei record_event.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from src.db.multi_view_client import _run_pg_sql

MAX_HISTORY_LIMIT = 1000


def _sql_literal(text: str) -> str:
    return "'" + (text or "").replace("'", "''") + "'"


def _normalize_limit(limit: int) -> int:
    """A6: Grenzen für Abfrage — nur echte ints, kein Float-Schleichweg."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        limit = 100
    return max(1, min(limit, MAX_HISTORY_LIMIT))


def _parse_history_payload(raw: str) -> list[dict[str, Any]]:
    s = (raw or "").strip()
    if not s:
        return []
    for line in s.splitlines():
        line = line.strip()
        if line.startswith("(") and "row" in line.lower():
            continue
        if not line:
            continue
        try:
            data = json.loads(line)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            continue
    start = s.find("[")
    end = s.rfind("]")
    if start >= 0 and end > start:
        try:
            data = json.loads(s[start : end + 1])
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
    try:
        data = json.loads(s)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


async def record_event(
    agent_id: str,
    event_type: str,
    content: dict[str, Any],
    memory_hash: str,
    *,
    event_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """
    Persistiert ein append-only Event. memory_hash leer → success=False (A7).
    """
    if not (memory_hash or "").strip():
        return {
            "success": False,
            "id": None,
            "error": "memory_hash required (zero-trust audit anchor)",
        }
    aid = (agent_id or "").strip()
    et = (event_type or "").strip()
    if not aid or not et:
        return {
            "success": False,
            "id": None,
            "error": "agent_id and event_type must be non-empty",
        }
    eid = event_id or uuid.uuid4()
    payload = json.dumps(content or {}, ensure_ascii=False)
    payload_esc = payload.replace("'", "''")

    sql = (
        "INSERT INTO omega_events (id, agent_id, event_type, content, memory_hash) VALUES ("
        f"{_sql_literal(str(eid))}::uuid, "
        f"{_sql_literal(aid)}, "
        f"{_sql_literal(et)}, "
        f"{_sql_literal(payload_esc)}::jsonb, "
        f"{_sql_literal((memory_hash or '').strip())}"
        ");"
    )
    ok, out = await _run_pg_sql(sql)
    if not ok:
        return {"success": False, "id": str(eid), "error": (out or "pg_exec_failed")[:2000]}
    return {"success": True, "id": str(eid), "error": None}


async def get_history(
    agent_id: str | None = None,
    *,
    limit: int = 100,
    event_types: list[str] | None = None,
    oldest_first: bool = False,
) -> list[dict[str, Any]]:
    """
    Chronologische Historie (Standard: neueste zuerst, limit gekappt).
    """
    lim = _normalize_limit(limit)
    order = "ASC" if oldest_first else "DESC"
    where_parts: list[str] = ["1=1"]
    if agent_id is not None and str(agent_id).strip():
        where_parts.append(f"agent_id = {_sql_literal(agent_id.strip())}")
    if event_types:
        safe_types: list[str] = []
        for t in event_types:
            st = (t or "").strip()
            if st:
                safe_types.append(_sql_literal(st))
        if safe_types:
            where_parts.append("event_type IN (" + ", ".join(safe_types) + ")")
    where_sql = " AND ".join(where_parts)

    sql = f"""
SELECT coalesce(
  json_agg(
    json_build_object(
      'id', id::text,
      'timestamp', "timestamp",
      'agent_id', agent_id,
      'event_type', event_type,
      'content', content,
      'memory_hash', memory_hash
    ) ORDER BY "timestamp" {order}
  ),
  '[]'::json
)::text
FROM (
  SELECT id, "timestamp", agent_id, event_type, content, memory_hash
  FROM omega_events
  WHERE {where_sql}
  ORDER BY "timestamp" {order}
  LIMIT {lim}
) sub;
""".strip()

    ok, out = await _run_pg_sql(sql)
    if not ok:
        return []
    return _parse_history_payload(out or "")


def _normalize_canon_limit(limit: int) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        limit = 200
    return max(1, min(limit, 500))


async def list_canon_documents(*, limit: int = 200) -> list[dict[str, Any]]:
    """
    Liest omega_canon_documents (Kanon-Registry / Resonanz-Anker-Sync).
    Leere Liste bei PG-Fehler oder fehlender Tabelle.
    """
    lim = _normalize_canon_limit(limit)
    sql = f"""
SELECT coalesce(
  json_agg(
    json_build_object(
      'repo_path', repo_path,
      'document_role', document_role,
      'anchor_section', anchor_section,
      'title', title,
      'body_sha256', body_sha256,
      'byte_size', byte_size,
      'last_synced_at', last_synced_at
    ) ORDER BY document_role, repo_path
  ),
  '[]'::json
)::text
FROM (
  SELECT repo_path, document_role, anchor_section, title, body_sha256, byte_size, last_synced_at
  FROM omega_canon_documents
  ORDER BY document_role, repo_path
  LIMIT {lim}
) sub;
""".strip()
    ok, out = await _run_pg_sql(sql)
    if not ok:
        return []
    return _parse_history_payload(out or "")
