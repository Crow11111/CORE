# -*- coding: utf-8 -*-
"""
PostgreSQL Ingest-Queue (omega_ingest_queue) — TICKET 12 Phase 1.

Edge → Queue: Roh-Events mit priority_float / confidence in der Resonanzdomäne (A5/A6).
Dequeue: FOR UPDATE SKIP LOCKED, Status → processing.
"""
from __future__ import annotations

import json
import math
import os
import re
from typing import Any

def _ingest_pg_local_enabled() -> bool:
    return os.environ.get("OMEGA_INGEST_PG_LOCAL", "").strip().lower() in ("1", "true", "yes")


if _ingest_pg_local_enabled():
    from src.db.pg_docker_local import run_pg_sql as _run_pg_sql
else:
    from src.db.multi_view_client import _run_pg_sql


class AxiomViolationError(ValueError):
    """A5/A6: priority_float oder confidence verletzen die Resonanzdomäne."""


def _sql_literal(text: str) -> str:
    return "'" + (text or "").replace("'", "''") + "'"


def _require_queue_resonance_float(name: str, value: Any) -> float:
    """
    Strikter als assert_resonance_float: nur echte float, endlich, kein A5-Singularity.
    Wirft AxiomViolationError (ValueError) — Kontrakt test_ingest_queue Trap 1.
    """
    if type(value) is not float:
        raise AxiomViolationError(
            f"[INGEST-QUEUE] {name}: A6 — ausschließlich float erforderlich, nicht {type(value).__name__}."
        )
    if math.isnan(value) or math.isinf(value):
        raise AxiomViolationError(f"[INGEST-QUEUE] {name}: A6 — kein NaN/Inf in der Resonanzdomäne.")
    if value in (0.0, 0.5, 1.0):
        raise AxiomViolationError(
            f"[INGEST-QUEUE] {name}: A5 — verbotene Symmetrie {value} (0.0, 0.5, 1.0)."
        )
    return value


def _parse_single_json_object(raw: str) -> dict[str, Any] | None:
    s = (raw or "").strip()
    if not s:
        return None
    for line in s.splitlines():
        line = line.strip()
        if not line or line.startswith("(") and "row" in line.lower():
            continue
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", s, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
    try:
        data = json.loads(s)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


async def enqueue_raw_event(
    source: str,
    payload: dict[str, Any],
    priority_float: float,
    confidence: float,
    trace_id: str,
) -> None:
    """
    Legt ein Roh-Event in omega_ingest_queue ab (status pending).
    """
    _require_queue_resonance_float("priority_float", priority_float)
    _require_queue_resonance_float("confidence", confidence)
    src = (source or "").strip()
    tid = (trace_id or "").strip()
    if not src:
        raise AxiomViolationError("[INGEST-QUEUE] source darf nicht leer sein (A7 Korrelation).")
    if not tid:
        raise AxiomViolationError("[INGEST-QUEUE] trace_id darf nicht leer sein (Idempotenz-Schutz).")
    if not isinstance(payload, dict):
        raise AxiomViolationError("[INGEST-QUEUE] payload muss ein dict sein.")

    body = json.dumps(payload or {}, ensure_ascii=False).replace("'", "''")
    pf = repr(float(priority_float))
    cf = repr(float(confidence))

    sql = (
        "INSERT INTO omega_ingest_queue (source, payload, priority_float, confidence, status, trace_id) VALUES ("
        f"{_sql_literal(src)}, "
        f"{_sql_literal(body)}::jsonb, "
        f"{pf}::double precision, "
        f"{cf}::double precision, "
        "'pending', "
        f"{_sql_literal(tid)}"
        ");"
    )
    ok, out = await _run_pg_sql(sql)
    if not ok:
        raise RuntimeError((out or "pg_enqueue_failed")[:2000])


async def dequeue_next_event() -> dict[str, Any] | None:
    """
    Nächstes pending-Event: Zeile sperren (SKIP LOCKED), Status → processing, Daten zurück.
    """
    sql = """
WITH picked AS (
  SELECT id FROM omega_ingest_queue
  WHERE status = 'pending'
  ORDER BY priority_float DESC, created_at ASC
  FOR UPDATE SKIP LOCKED
  LIMIT 1
)
UPDATE omega_ingest_queue q
SET status = 'processing'
FROM picked
WHERE q.id = picked.id
RETURNING json_build_object(
  'id', q.id::text,
  'created_at', q.created_at,
  'source', q.source,
  'payload', q.payload,
  'priority_float', q.priority_float,
  'confidence', q.confidence,
  'status', q.status,
  'trace_id', q.trace_id
)::text;
""".strip()

    ok, raw = await _run_pg_sql(sql)
    if not ok:
        return None
    row = _parse_single_json_object(raw or "")
    return row
