"""
Ring-0 Mutable State – z_widerstand Override durch Munin Veto.

Munin Veto kann z_widerstand erhöhen; get_current_state() liest diesen Override.
"""
from __future__ import annotations

_z_widerstand_override: float | None = None


def set_munin_veto(z: float) -> None:
    """Setzt z_widerstand-Override (0..1). Wird von get_current_state() verwendet."""
    global _z_widerstand_override
    _z_widerstand_override = max(0.0, min(1.0, z))


def clear_munin_veto() -> None:
    """Entfernt Munin-Veto-Override."""
    global _z_widerstand_override
    _z_widerstand_override = None


def get_munin_veto_override() -> float | None:
    """Liefert aktuellen z_widerstand-Override oder None."""
    return _z_widerstand_override
