# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
S↔P-Membran: Resonanz-Domäne (float) vs. Infrastruktur-Domäne (int).

Einheitliche Prüfung überall, wo beide Welten im selben Kontext auftauchen
(Webhook-Payload, Mini-Kern omega_core, zukünftige APIs).

Axiom: bool ist kein int (Python: isinstance(True, int) → True) — daher strikt type(x) is int.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

# Verbotene Symmetrie-Punkte in der Resonanz-Domäne (Axiom A1)
FORBIDDEN_RESONANCE_VALUES = frozenset({0.0, 0.5, 1.0})


class MembraneTypeError(TypeError):
    """S- oder P-Domäne verletzt."""


class MembraneValueError(ValueError):
    """Verbotene Resonanz-Singularität."""


def assert_resonance_float(name: str, value: Any) -> float:
    """
    Resonanz-Domäne: ausschließlich float, keine int/bool-Kodierung.
    """
    if type(value) is not float:
        raise MembraneTypeError(
            f"[MEMBRAN-S] {name}: Resonanz-Domäne verweigert Typ {type(value).__name__}; "
            f"float erforderlich (kein int/bool)."
        )
    if value in FORBIDDEN_RESONANCE_VALUES:
        raise MembraneValueError(
            f"[MEMBRAN-S] {name}: verbotene Symmetrie {value} (0.0, 0.5, 1.0)."
        )
    return value


def assert_infrastructure_int(name: str, value: Any) -> int:
    """
    Infrastruktur-Domäne: ausschließlich int (kein bool).
    """
    if type(value) is not int:
        raise MembraneTypeError(
            f"[MEMBRAN-P] {name}: Infrastruktur-Domäne verweigert Typ {type(value).__name__}; "
            f"int erforderlich (bool nicht erlaubt)."
        )
    return value


def membrane_scan_payload(
    payload: dict[str, Any],
    *,
    resonance_keys: Iterable[str] = (),
    infrastructure_keys: Iterable[str] = (),
) -> None:
    """
    Prüft explizit benannte Schlüssel im flachen Payload (z. B. nach Normalisierung).

    Unbekannte Schlüssel werden ignoriert — Aufrufer müssen ihre Konvention dokumentieren.
    """
    rk = frozenset(resonance_keys)
    ik = frozenset(infrastructure_keys)
    overlap = rk & ik
    if overlap:
        raise ValueError(f"[MEMBRAN] Schlüssel dürfen nicht S und P zugleich sein: {overlap}")

    for k in rk:
        if k not in payload:
            continue
        v = payload[k]
        if v is None:
            continue
        assert_resonance_float(k, v)
    for k in ik:
        if k not in payload:
            continue
        v = payload[k]
        if v is None:
            continue
        assert_infrastructure_int(k, v)


@dataclass
class DualMembraneVector:
    """Paar aus Resonanz-(S) und Infrastruktur-(P)-Wert; kanonisch zu omega_core."""

    uuid: str
    s_float: float
    p_int: int

    def __post_init__(self) -> None:
        assert_resonance_float("s_float", self.s_float)
        assert_infrastructure_int("p_int", self.p_int)
