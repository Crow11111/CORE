# -*- coding: utf-8 -*-
"""
Kontrakt-Tests VPS Dream Worker (TICKET 12 Phase 3).

Verification-First: Stub ``src.db.ingest_queue_client`` in ``sys.modules``;
Chroma/Void-Probe wird auf dem Dream-Modul gepatcht.
"""
from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_ingest_queue_client(monkeypatch):
    """Mock ``dequeue_next_event`` ohne Postgres-Kette (A7)."""
    name = "src.db.ingest_queue_client"
    stub = ModuleType(name)
    stub.dequeue_next_event = AsyncMock(return_value=None)
    monkeypatch.setitem(sys.modules, name, stub)
    return stub


def _load_dream_worker():
    try:
        return __import__("src.daemons.vps_dream_worker", fromlist=["*"])
    except ImportError as exc:
        pytest.fail(
            f"TICKET 12 Phase 3: vps_dream_worker fehlt. TDD-Kontrakt nicht erfüllt. ({exc})"
        )


@pytest.mark.asyncio
async def test_too_awake_v_gt_r_does_not_dequeue(mock_ingest_queue_client, caplog):
    """Trap 1: Wach-Modus (V > R) — kein Traum, kein Dequeue, auditierbarer Log."""
    import logging

    mod = _load_dream_worker()
    if not hasattr(mod, "run_dream_cycle"):
        pytest.fail("run_dream_cycle fehlt — Dream-Loop unmöglich.")

    caplog.set_level(logging.INFO)
    dq = mock_ingest_queue_client.dequeue_next_event

    out = await mod.run_dream_cycle({"V": 0.91, "R": 0.12})

    dq.assert_not_awaited()
    assert out is None
    assert any(
        "Too awake to dream" in rec.message for rec in caplog.records
    ), "Wach-Modus muss explizit geloggt werden."


@pytest.mark.asyncio
async def test_dream_mode_void_ticket_priority_float_a6(mock_ingest_queue_client, monkeypatch):
    """Trap 2: R > V — Void (kein Chroma-Gegenstück), priority_float als echtes float (A6)."""
    mod = _load_dream_worker()

    event = {
        "id": "q-void-1",
        "trace_id": "void-trap-chroma-miss",
        "source": "ha",
        "payload": {"entity_id": "sensor.gap"},
        "confidence": 0.151,
        "priority_float": 0.601,
        "status": "processing",
    }
    mock_ingest_queue_client.dequeue_next_event = AsyncMock(return_value=event)

    async def _no_chroma(_trace_id: str) -> bool:
        _ = _trace_id[:0]
        return False

    monkeypatch.setattr(mod, "_trace_has_chroma_counterpart", _no_chroma)

    V, R = 0.11, 0.82
    out = await mod.run_dream_cycle({"V": V, "R": R})

    assert isinstance(out, dict), "Void-Ticket als dict (A6 Kontrakt)."
    assert type(out["priority_float"]) is float
    expected = min(0.951, (R - V) + float(event["confidence"]))
    assert out["priority_float"] == pytest.approx(expected, rel=1e-9, abs=1e-9)
    assert out.get("trace_id") == "void-trap-chroma-miss"
    assert out.get("kind") == "void_ticket"


@pytest.mark.asyncio
async def test_priority_float_a5_nudges_exact_half(mock_ingest_queue_client, monkeypatch):
    """A5: (R-V)+confidence == 0.5 → kein exaktes 0.5 im Ticket (wie Sentinel)."""
    mod = _load_dream_worker()

    # R - V = 0.3, confidence 0.2 → raw 0.5
    V, R = 0.11, 0.41
    event = {
        "id": "q-a5-half",
        "trace_id": "trace-a5-half",
        "source": "ha",
        "confidence": 0.2,
        "priority_float": 0.1,
        "status": "processing",
    }
    mock_ingest_queue_client.dequeue_next_event = AsyncMock(return_value=event)
    monkeypatch.setattr(
        mod, "_trace_has_chroma_counterpart", AsyncMock(return_value=False)
    )

    out = await mod.run_dream_cycle({"V": V, "R": R})

    assert isinstance(out, dict)
    assert out["priority_float"] == pytest.approx(0.503, rel=0, abs=1e-12)
    assert out["priority_float"] not in (0.0, 0.5, 1.0)


@pytest.mark.asyncio
async def test_priority_float_a5_nudges_exact_zero(mock_ingest_queue_client, monkeypatch):
    """A5: (R-V)+confidence == 0.0 → Nudge auf 0.049."""
    mod = _load_dream_worker()

    # Binär exakte Floats: 0.5 - 0.25 - 0.25 == 0.0 (0.3-0.1 liefert Float-Rauschen).
    V, R = 0.25, 0.5
    event = {
        "id": "q-a5-zero",
        "trace_id": "trace-a5-zero",
        "source": "ha",
        "confidence": -0.25,
        "priority_float": 0.1,
        "status": "processing",
    }
    mock_ingest_queue_client.dequeue_next_event = AsyncMock(return_value=event)
    monkeypatch.setattr(
        mod, "_trace_has_chroma_counterpart", AsyncMock(return_value=False)
    )

    out = await mod.run_dream_cycle({"V": V, "R": R})

    assert isinstance(out, dict)
    assert out["priority_float"] == pytest.approx(0.049, rel=0, abs=1e-12)
    assert out["priority_float"] not in (0.0, 0.5, 1.0)


@pytest.mark.asyncio
async def test_default_pacemaker_v_r_not_symmetry_half(mock_ingest_queue_client, caplog):
    """A5: fehlende/unlesbare V,R defaulten nicht auf 0.5 — Traum abgebrochen bei V>=R."""
    import logging

    mod = _load_dream_worker()
    caplog.set_level(logging.WARNING)
    dq = mock_ingest_queue_client.dequeue_next_event

    out = await mod.run_dream_cycle({})

    dq.assert_not_awaited()
    assert out is None
