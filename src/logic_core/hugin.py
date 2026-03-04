"""
Hugin – Logik & Scout (Ring-0).

Input-Triage: Klassifiziert eingehende Requests (NormalizedEntry).
Validation Sync: Bereitet Daten für Valuation Sync / Munin vor.

Integration: src/api/entry_adapter.py → Hugin.triage() → Valuation Sync → Munin
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.api.entry_adapter import NormalizedEntry
from src.config.engine_patterns import QBASES


@dataclass
class TriageResult:
    """Ergebnis der Hugin-Input-Triage für Valuation Sync."""

    entry: NormalizedEntry
    lpis_base: str  # L|P|I|S
    priority: int  # 1=hoch, 2=mittel, 3=niedrig
    intent: str  # query|command|status|unknown
    validation_ready: bool
    triage_metadata: dict[str, Any]


# Heuristische Keywords pro LPIS (für schnelle Klassifikation ohne Embedding)
_LPIS_KEYWORDS: dict[str, list[str]] = {
    "L": ["logik", "regel", "compliance", "prüf", "validier", "bias", "paranoia", "sicherheit"],
    "P": ["physik", "simulation", "quanten", "energie", "materie", "gravitation", "kollaps"],
    "I": ["info", "daten", "embedding", "suche", "kontext", "wissen", "archiv", "query"],
    "S": ["struktur", "architektur", "system", "ring", "tetralogie", "strang", "schema"],
}

# Intent-Erkennung
_INTENT_QUERY = ["was", "wie", "warum", "wo", "wann", "welche", "suche", "finde", "zeig", "erkläre"]
_INTENT_COMMAND = ["mach", "führe", "starte", "stopp", "ping", "atlas_", "command"]
_INTENT_STATUS = ["status", "zustand", "ping", "health", "ok?"]


def _classify_lpis(text: str) -> str:
    """Heuristische LPIS-Klassifikation aus Text."""
    if not text or not isinstance(text, str):
        return "I"  # Default: Information
    low = text.lower().strip()
    scores: dict[str, int] = {b: 0 for b in QBASES}
    for base, keywords in _LPIS_KEYWORDS.items():
        for kw in keywords:
            if kw in low:
                scores[base] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "I"
    return best


def _classify_intent(text: str, payload: dict) -> str:
    """Erkennt Intent: query|command|status|unknown."""
    t = (text or "").lower()
    p = payload or {}
    action = (p.get("action") or "").lower()
    if action in ("atlas_ping", "ping"):
        return "status"
    if any(x in t for x in _INTENT_COMMAND):
        return "command"
    if any(x in t for x in _INTENT_STATUS):
        return "status"
    if any(x in t for x in _INTENT_QUERY) or len(t) > 10:
        return "query"
    return "unknown"


def _derive_priority(source: str, intent: str, lpis_base: str) -> int:
    """1=hoch, 2=mittel, 3=niedrig."""
    if intent == "status" and source in ("ha", "api"):
        return 1
    if intent == "command" and source in ("ha", "whatsapp"):
        return 1
    if lpis_base == "L" and intent in ("command", "status"):
        return 1  # Council-relevant
    if intent == "query":
        return 2
    return 3


def triage(entry: NormalizedEntry) -> TriageResult:
    """
    Hugin Input-Triage: Klassifiziert NormalizedEntry für Valuation Sync.

    Args:
        entry: Von entry_adapter.normalize_request() erzeugt

    Returns:
        TriageResult mit LPIS, Priority, Intent, validation_ready
    """
    payload = entry.payload or {}
    text = payload.get("text") or payload.get("message") or payload.get("body") or ""

    lpis_base = _classify_lpis(text)
    intent = _classify_intent(text, payload)
    priority = _derive_priority(entry.source, intent, lpis_base)

    validation_ready = bool(text.strip()) or bool(payload.get("action"))

    return TriageResult(
        entry=entry,
        lpis_base=lpis_base,
        priority=priority,
        intent=intent,
        validation_ready=validation_ready,
        triage_metadata={
            "source": entry.source,
            "text_len": len(text),
            "has_audio": payload.get("has_audio", False),
        },
    )


def triage_from_raw(source: str, raw_payload: Any, auth_ctx: dict | None = None) -> TriageResult:
    """
    Normalisiert und triagiert in einem Schritt (Entry Adapter + Hugin).

    Convenience für Pipeline: normalize_request → triage.
    """
    from src.api.entry_adapter import normalize_request

    entry = normalize_request(source, raw_payload, auth_ctx)
    return triage(entry)
