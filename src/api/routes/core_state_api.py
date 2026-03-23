from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from pathlib import Path
from loguru import logger

from src.config.core_state import get_current_state

router = APIRouter(prefix="/core-state", tags=["State & Matrix"])

_REPO = Path(__file__).parent.parent.parent.parent.resolve()
HANDBOOK_DIR = _REPO / ".cursor" / "agents" / "handbooks"

class HandbookUpdateRequest(BaseModel):
    content: str

@router.get("/vector")
async def read_core_state():
    """
    Liest den aktuellen 4D CORE State Vector (S * P Symbiose).
    Kann systemuebergreifend von OpenClaw/VPS oder lokalen Agenten aufgerufen werden.
    """
    try:
        state = get_current_state()
        data = {
            "s_vector": state.s_vector,
            "p_vector": state.p_vector,
            "psi_core": state.psi,
            "baryonic_limit_breached": state.psi <= 0.049
        }
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"[STATE-API] Error reading vector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/handbook/{role}")
async def read_handbook(role: str):
    """
    Liest das persistente Gedächtnis (Handbuch) für eine spezifische Rolle.
    """
    target_file = HANDBOOK_DIR / f"{role}.md"
    template_file = HANDBOOK_DIR / "_TEMPLATE.md"
    
    try:
        if target_file.exists():
            return {"status": "success", "content": target_file.read_text(encoding="utf-8")}
        elif template_file.exists():
            content = f"[WARNUNG: HANDBUCH FÜR {role} EXISTIERT NOCH NICHT. HIER IST DAS TEMPLATE ZUR ANLAGE:]\n\n" + template_file.read_text(encoding="utf-8")
            return {"status": "success", "content": content}
        else:
            raise HTTPException(status_code=404, detail=f"Weder Handbuch noch Template für {role} gefunden.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/handbook/{role}")
async def update_handbook(role: str, request: HandbookUpdateRequest):
    """
    Ueberschreibt das persistente Gedächtnis (Handbuch) für die angegebene Rolle.
    """
    target_file = HANDBOOK_DIR / f"{role}.md"
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(request.content, encoding="utf-8")
        logger.info(f"[STATE-API] Handbuch fuer {role} wurde aktualisiert.")
        return {"status": "success", "message": f"Handbuch für {role} aktualisiert."}
    except Exception as e:
        logger.error(f"[STATE-API] Error writing handbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
