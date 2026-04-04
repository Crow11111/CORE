# -*- coding: utf-8 -*-
"""
Kontrakt-Tests VPS Sentinel Daemon (TICKET 12 Phase 2).

Verification-First: Isoliert ``src.db.ingest_queue_client`` als Stub-Modul in
``sys.modules``, damit ``enqueue_raw_event`` gemockt wird ohne Postgres/Chroma-Importkette.
"""
from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_enqueue_raw_event(monkeypatch):
    """Mock für ``src.db.ingest_queue_client.enqueue_raw_event`` (A7: kein Seiteneffekt-Import)."""
    name = "src.db.ingest_queue_client"
    stub = ModuleType(name)
    mock = AsyncMock()
    stub.enqueue_raw_event = mock
    monkeypatch.setitem(sys.modules, name, stub)
    return mock


def _load_sentinel():
    try:
        return __import__("src.daemons.vps_sentinel_daemon", fromlist=["*"])
    except ImportError as exc:
        pytest.fail(
            f"TICKET 12 Phase 2: vps_sentinel_daemon fehlt. TDD-Kontrakt nicht erfüllt. ({exc})"
        )


@pytest.mark.asyncio
async def test_watch_mode_high_v_enqueues_high_confidence_float_a6(mock_enqueue_raw_event):
    """Trap 1: Wach-Modus — hohe V, niedriges R → hohe Prio/Konfidenz als echte floats."""
    mod = _load_sentinel()
    if not hasattr(mod, "process_inbound_event"):
        pytest.fail("process_inbound_event fehlt — Sentinel-Ingress unmöglich.")

    payload = {"entity_id": "binary_sensor.door", "trace_id": "trap1-ha-watch"}
    pacemaker = {"V": 0.95, "R": 0.04}
    q = mock_enqueue_raw_event

    await mod.process_inbound_event("ha", payload, pacemaker)
    q.assert_awaited_once()
    kwargs = q.await_args.kwargs
    assert type(kwargs["priority_float"]) is float
    assert type(kwargs["confidence"]) is float
    assert kwargs["priority_float"] > 0.8
    assert kwargs["confidence"] == pytest.approx(0.95 * 0.865, rel=1e-9, abs=1e-9)
    assert kwargs["confidence"] == pytest.approx(0.82175, rel=1e-5)
    assert kwargs["source"] == "ha"
    assert kwargs["payload"] == payload
    assert kwargs["trace_id"] == "trap1-ha-watch"


@pytest.mark.asyncio
async def test_dream_mode_throttles_priority_to_resonance_floor(mock_enqueue_raw_event):
    """Trap 2a: Traum-Modus (R dominiert) — Priorität auf 0.049 gedrosselt."""
    mod = _load_sentinel()
    payload = {"entity_id": "sensor.motion", "trace_id": "trap2-throttle"}
    pacemaker = {"V": 0.22, "R": 0.88}
    q = mock_enqueue_raw_event

    await mod.process_inbound_event("ha", payload, pacemaker)
    q.assert_awaited_once()
    assert q.await_args.kwargs["priority_float"] == pytest.approx(0.049, rel=1e-9, abs=1e-9)
    assert type(q.await_args.kwargs["confidence"]) is float


@pytest.mark.asyncio
async def test_dream_mode_deep_rest_drops_with_audit_log(mock_enqueue_raw_event, caplog):
    """Trap 2b: Extrem hohes R — Event drop + Log-Reason (A7)."""
    import logging

    mod = _load_sentinel()
    payload = {"entity_id": "camera.porch", "trace_id": "trap2-drop"}
    pacemaker = {"V": 0.08, "R": 0.96}
    q = mock_enqueue_raw_event

    caplog.set_level(logging.INFO)
    await mod.process_inbound_event("vision", payload, pacemaker)
    q.assert_not_awaited()
    assert any(
        "SENTINEL" in rec.message and "drop" in rec.message.lower()
        for rec in caplog.records
    ), "A7: Drop erfordert auditierbaren Log-Eintrag mit Kontext."
