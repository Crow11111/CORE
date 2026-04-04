# -*- coding: utf-8 -*-
"""
Kontrakt-Tests Ingest-Queue (TICKET 12 Phase 1).

Verification-First: Mockt _run_pg_sql — Traps für A5/A6 und Dequeue-Isolation.
"""
from __future__ import annotations

import json
import math
from unittest.mock import AsyncMock, patch

import pytest


def _load_ingest_queue():
    try:
        return __import__("src.db.ingest_queue_client", fromlist=["*"])
    except ImportError as exc:
        pytest.fail(
            f"TICKET 12 Phase 1: ingest_queue_client fehlt. TDD-Kontrakt nicht erfüllt. ({exc})"
        )


@pytest.mark.parametrize(
    "priority,confidence",
    [
        (1, 0.51),  # int statt float (A6)
        (0.049, None),
        (float("nan"), 0.51),
        (0.049, float("nan")),
        (0.0, 0.51),
        (0.049, 0.0),
        (0.5, 0.51),
        (0.049, 0.5),
        (1.0, 0.51),
        (0.049, 1.0),
    ],
)
@pytest.mark.asyncio
async def test_enqueue_rejects_non_resonance_floats_a5_a6(priority, confidence):
    mod = _load_ingest_queue()
    if not hasattr(mod, "enqueue_raw_event"):
        pytest.fail("enqueue_raw_event fehlt — Ingest-Perimeter unvollständig.")

    with pytest.raises((ValueError, mod.AxiomViolationError)):
        await mod.enqueue_raw_event(
            source="ha",
            payload={"x": 1},
            priority_float=priority,
            confidence=confidence,
            trace_id="t-1",
        )


@pytest.mark.asyncio
async def test_dequeue_next_event_sets_processing_and_returns_row():
    mod = _load_ingest_queue()
    if not hasattr(mod, "dequeue_next_event"):
        pytest.fail("dequeue_next_event fehlt — Queue-Consumer unmöglich.")

    captured: list[str] = []

    async def fake_run(sql: str, timeout: int = 30):
        captured.append(sql)
        assert "FOR UPDATE SKIP LOCKED" in sql.replace("\n", " ")
        assert "processing" in sql.lower()
        row = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": "2026-04-03T12:00:00+00:00",
            "source": "ha",
            "payload": {"entity": "light.kitchen"},
            "priority_float": 0.73,
            "confidence": 0.51,
            "status": "processing",
            "trace_id": "trace-ha-1",
        }
        return True, json.dumps(row, ensure_ascii=False)

    with patch.object(mod, "_run_pg_sql", new=AsyncMock(side_effect=fake_run)):
        out = await mod.dequeue_next_event()

    assert captured, "dequeue muss _run_pg_sql aufrufen."
    assert isinstance(out, dict)
    assert out.get("status") == "processing"
    assert out.get("trace_id") == "trace-ha-1"
    assert math.isclose(float(out.get("priority_float", 0)), 0.73)
    assert math.isclose(float(out.get("confidence", 0)), 0.51)


@pytest.mark.asyncio
async def test_dequeue_next_event_returns_none_when_empty():
    mod = _load_ingest_queue()

    async def fake_run(sql: str, timeout: int = 30):
        _ = sql[:0]
        _ = timeout + 0
        return True, ""

    with patch.object(mod, "_run_pg_sql", new=AsyncMock(side_effect=fake_run)):
        out = await mod.dequeue_next_event()

    assert out is None


@pytest.mark.asyncio
async def test_enqueue_raw_event_emits_insert_with_float_literals():
    mod = _load_ingest_queue()
    captured: list[str] = []

    async def fake_run(sql: str, timeout: int = 30):
        captured.append(sql)
        return True, "OK"

    with patch.object(mod, "_run_pg_sql", new=AsyncMock(side_effect=fake_run)):
        await mod.enqueue_raw_event(
            source="mqtt",
            payload={"topic": "home/+/state"},
            priority_float=0.221,
            confidence=0.049,
            trace_id="idempotent-42",
        )

    assert len(captured) == 1
    sql = captured[0]
    assert "INSERT INTO omega_ingest_queue" in sql
    assert "idempotent-42" in sql
    assert "mqtt" in sql
    assert "pending" in sql.lower()
