# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from src.daemons.system_bus_daemon import bus_instance
from loguru import logger

router = APIRouter(prefix="/api/v1/bus", tags=["SystemBus"])

@router.get("/state")
async def get_bus_state():
    """Liefert den aktuellen Zustand des SystemBus (GRV + Hash)."""
    return {
        "grv": bus_instance.get_grv(),
        "state_hash": bus_instance.get_state_hash()
    }

@router.post("/delta")
async def apply_bus_delta(delta: Dict[str, Any] = Body(...)):
    """
    Integriert ein Delta in den SystemBus.
    Erwartet das JSON-Delta-Vektor Schema.
    """
    try:
        new_hash = bus_instance.apply_delta(delta)
        return {
            "status": "integrated",
            "new_state_hash": new_hash
        }
    except Exception as e:
        logger.error("[API] Fehler bei Delta-Integration: {}", e)
        raise HTTPException(status_code=500, detail=str(e))
