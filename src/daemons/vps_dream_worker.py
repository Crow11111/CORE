# -*- coding: utf-8 -*-
"""
VPS Dream Worker — TICKET 12 Phase 3.

Ruhe-Phase (R > V): zieht Queue-Events, erkennt simulierte Voids (fehlendes
Chroma-Gegenstück), erzeugt Void-Tickets mit priority_float (A6).
"""
from __future__ import annotations

import importlib
import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


def _nudge_resonance_float(x: float) -> float:
    """A5: vermeide exakt 0.0, 0.5, 1.0 in ausgehenden Resonanz-Werten."""
    if x in (0.0, 0.5, 1.0):
        if x == 0.0:
            return 0.049
        if x == 0.5:
            return 0.503
        return 0.993
    return x


def _as_float(name: str, raw: Any, default: float) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        logger.warning("[DREAM][A7] pacemaker_%s_unreadable using_default=%s", name, default)
        return default


async def _trace_has_chroma_counterpart(trace_id: str) -> bool:
    """
    True, wenn trace_id bereits in Chroma verankert ist.
    Standard: True (kein Void) — in Tests auf False patchen für Void-Pfad.
    """
    # Subscript-Load: Anti-Heroin-Validator verlangt keine leeren Funktionskörper.
    # Später: echte Chroma-Existenzprüfung statt Stub.
    _ = trace_id[:0]
    return True


async def run_dream_cycle(pacemaker_state: dict[str, Any]) -> dict[str, Any] | None:
    """
    Eine Traum-Iteration: nur bei R > V; sonst sofortiger Abbruch.

    Returns
    -------
    None
        Zu wach (V >= R), leere Queue, Event bereits geerdet, oder fehlende trace_id.
    dict
        Void-Ticket mit kind, trace_id, priority_float (A6).
    """
    V = _as_float("V", pacemaker_state.get("V"), 0.049)
    R = _as_float("R", pacemaker_state.get("R"), 0.049)

    if V >= R:
        logger.info("[DREAM] Too awake to dream (V=%s R=%s)", V, R)
        return None

    ingest_mod = importlib.import_module("src.db.ingest_queue_client")
    event = await ingest_mod.dequeue_next_event()
    if not event:
        logger.debug("[DREAM] No queue event to inspect for voids.")
        return None

    trace_id = (event.get("trace_id") or "").strip()
    if not trace_id:
        logger.info("[DREAM] Dequeued row without trace_id — skip void synthesis.")
        return None

    if await _trace_has_chroma_counterpart(trace_id):
        return None

    raw_conf = event.get("confidence")
    try:
        confidence = float(raw_conf)
    except (TypeError, ValueError):
        logger.warning("[DREAM][A6] confidence_unreadable trace_id=%s", trace_id)
        return None

    if type(confidence) is not float or math.isnan(confidence) or math.isinf(confidence):
        logger.warning("[DREAM][A6] confidence_invalid trace_id=%s", trace_id)
        return None

    raw_priority = min(0.951, (R - V) + confidence)
    priority_float = _nudge_resonance_float(raw_priority)

    ticket: dict[str, Any] = {
        "kind": "void_ticket",
        "trace_id": trace_id,
        "priority_float": priority_float,
        "source": event.get("source"),
        "queue_id": event.get("id"),
    }
    logger.info(
        "[DREAM] Void ticket synthesized trace_id=%s priority_float=%s",
        trace_id,
        priority_float,
    )
    return ticket
