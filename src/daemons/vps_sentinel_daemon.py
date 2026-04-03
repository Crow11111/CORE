# -*- coding: utf-8 -*-
"""
VPS Sentinel Daemon — TICKET 12 Phase 2.

Simulierter HA/Vision-Ingress: schreibt nur über omega_ingest_queue (Phase 1).
Pacemaker V (Vigilance) / R (Rest) modulieren Priorität, Konfidenz und Drop.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# Traum: R dominiert → Drossel auf Resonanzboden; extrem → Drop (A7).
_R_THROTTLE_LINE = 0.78
_R_DROP_FLOOR = 0.93
_DROP_V_MARGIN = 0.25


def _as_float(name: str, raw: Any, default: float) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        logger.warning("[SENTINEL][A7] pacemaker_%s_unreadable using_default=%s", name, default)
        return default


def _nudge_resonance_float(x: float) -> float:
    """A5: vermeide exakt 0.0, 0.5, 1.0 in ausgehenden Queue-Werten."""
    if x in (0.0, 0.5, 1.0):
        if x == 0.0:
            return 0.049
        if x == 0.5:
            return 0.503
        return 0.993
    return x


def _trace_id_from_payload(payload: dict[str, Any]) -> str:
    tid = payload.get("trace_id")
    if isinstance(tid, str) and tid.strip():
        return tid.strip()
    return str(uuid.uuid4())


async def process_inbound_event(
    source: str,
    payload: dict[str, Any],
    pacemaker_state: dict[str, Any],
) -> None:
    """
    Verarbeitet ein eingehendes HA/Vision-Event und legt es ggf. in die Ingest-Queue.

    pacemaker_state: mindestens ``V`` (Vigilance), ``R`` (Rest) als floats.
    """
    V = _as_float("V", pacemaker_state.get("V"), 0.049)
    R = _as_float("R", pacemaker_state.get("R"), 0.049)

    if R >= _R_DROP_FLOOR and R > V + _DROP_V_MARGIN:
        logger.info(
            "[SENTINEL][A7] drop_event reason=deep_rest_dominance R=%.6f V=%.6f source=%s",
            R,
            V,
            (source or "").strip(),
        )
        return

    if R > V and R >= _R_THROTTLE_LINE:
        priority = _nudge_resonance_float(0.049)
        confidence = _nudge_resonance_float(max(0.051, V * 0.41))
    else:
        priority = _nudge_resonance_float(max(0.049, V - R))
        confidence = _nudge_resonance_float(V * 0.865)

    from src.db.ingest_queue_client import enqueue_raw_event as _enqueue

    await _enqueue(
        source=(source or "").strip(),
        payload=payload if isinstance(payload, dict) else {},
        priority_float=priority,
        confidence=confidence,
        trace_id=_trace_id_from_payload(payload if isinstance(payload, dict) else {}),
    )
