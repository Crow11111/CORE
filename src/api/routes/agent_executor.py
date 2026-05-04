import os
import sys
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
import subprocess

router = APIRouter(prefix="/api/agent", tags=["Agent Executor"])

class AgentExecuteRequest(BaseModel):
    agent_type: str # e.g. "producer", "o2", "custom"
    task_prompt: Optional[str] = None
    target_file: Optional[str] = None

@router.post("/execute")
async def execute_agent(req: AgentExecuteRequest, background_tasks: BackgroundTasks):
    """
    Triggert Agenten-Logik lokal auf dem Server, um Cursor-Einschränkungen zu umgehen.
    """
    logger.info(f"Agent Execution Request: {req.agent_type}")
    
    # Basispfad für Skripte
    scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
    
    if req.agent_type == "o2":
        script_path = scripts_dir / "run_o2_audit_v3.py"
        if not script_path.exists():
            raise HTTPException(status_code=404, detail=f"Skript {script_path} nicht gefunden.")
        
        # Führe O2 Audit synchron aus (könnte auch asynchron sein)
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return {"status": "success", "agent": "o2", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            logger.error(f"O2 Audit fehlgeschlagen: {e.stderr}")
            raise HTTPException(status_code=500, detail=f"O2 Audit fehlgeschlagen: {e.stderr}")

    elif req.agent_type == "producer":
        # Wir können hier das run_v3_producer_agent_v3.py Skript aufrufen
        script_path = scripts_dir / "run_v3_producer_agent_v3.py"
        if not script_path.exists():
            raise HTTPException(status_code=404, detail=f"Skript {script_path} nicht gefunden.")
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return {"status": "success", "agent": "producer", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            logger.error(f"Producer fehlgeschlagen: {e.stderr}")
            raise HTTPException(status_code=500, detail=f"Producer fehlgeschlagen: {e.stderr}")
            
    else:
        raise HTTPException(status_code=400, detail=f"Unbekannter Agent-Typ: {req.agent_type}")

