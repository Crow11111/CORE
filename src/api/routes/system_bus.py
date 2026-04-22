# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

from fastapi import APIRouter, HTTPException, Body, Request
from typing import Dict, Any
from src.daemons.system_bus_daemon import bus_instance
from src.network.synapse_membrane import synapse_instance
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
async def apply_bus_delta(request: Request, delta: Dict[str, Any] = Body(...)):
    """
    Integriert ein Delta in den SystemBus.
    Erwartet das JSON-Delta-Vektor Schema.
    Wird durch die biologische Synapse vor Reizüberflutung geschützt.
    """
    worker_id = request.headers.get("x-openclaw-agent-id", "default_worker")
    
    if synapse_instance.is_refractory(worker_id):
        logger.warning("[SYNAPSE] Delta abgewehrt (429). Worker {} befindet sich in der Refraktärzeit.", worker_id)
        raise HTTPException(status_code=429, detail="Refractory period active. Synapse is locked.")

    synapse_instance.trigger_action_potential(worker_id, delta)

    try:
        new_hash = bus_instance.apply_delta(delta)
        return {
            "status": "integrated",
            "new_state_hash": new_hash
        }
    except Exception as e:
        logger.error("[API] Fehler bei Delta-Integration: {}", e)
        raise HTTPException(status_code=500, detail=str(e))
