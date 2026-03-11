# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Ring-0 Mutable State – z_widerstand Override durch Drift Veto.

Drift Veto kann z_widerstand erhöhen; get_current_state() liest diesen Override.
"""
from __future__ import annotations

_z_widerstand_override: float | None = None


def set_drift_veto(z: float) -> None:
    """Setzt z_widerstand-Override (0..1). Wird von get_current_state() verwendet."""
    global _z_widerstand_override
    _z_widerstand_override = max(0.0, min(1.0, z))


def clear_drift_veto() -> None:
    """Entfernt Drift-Veto-Override."""
    global _z_widerstand_override
    _z_widerstand_override = None


def get_drift_veto_override() -> float | None:
    """Liefert aktuellen z_widerstand-Override oder None."""
    return _z_widerstand_override


# Backward-Kompatibilitaet
set_munin_veto = set_drift_veto
clear_munin_veto = clear_drift_veto
get_munin_veto_override = get_drift_veto_override
