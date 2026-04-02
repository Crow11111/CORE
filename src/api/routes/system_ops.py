# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: SYSTEM OPERATIONS (FILE I/O)
# ============================================================

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

router = APIRouter(prefix="/api/v1/system", tags=["system"])

WORKSPACE_ROOT = Path("/OMEGA_CORE")
DEFAULT_INJECTION_PATH = WORKSPACE_ROOT / "data" / "cursor_injection.txt"

class WriteRequest(BaseModel):
    text: str
    path: str = str(DEFAULT_INJECTION_PATH)

@router.post("/write")
async def write_to_file(request: WriteRequest):
    """
    Schreibt Text in eine Datei im Workspace.
    Sicherheitscheck gegen Path Traversal inklusive.
    """
    try:
        target_path = Path(request.path)

        # Absoluten Pfad auflösen für den Check
        if not target_path.is_absolute():
            # Wenn relativ, dann relativ zum Workspace Root
            target_path = (WORKSPACE_ROOT / target_path).resolve()
        else:
            target_path = target_path.resolve()

        # Path Traversal Check: Muss innerhalb von WORKSPACE_ROOT liegen
        if not str(target_path).startswith(str(WORKSPACE_ROOT)):
            logger.warning(f"[SYSTEM] Path Traversal Versuch geblockt: {target_path}")
            raise HTTPException(status_code=403, detail="Zugriff verweigert: Pfad außerhalb des Workspaces.")

        # Verzeichnis sicherstellen
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Schreiben
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(request.text)

        logger.info(f"[SYSTEM] Datei geschrieben: {target_path}")
        return {"success": True, "path": str(target_path), "bytes": len(request.text)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SYSTEM] Fehler beim Schreiben: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# API-Routing (WebSocket für Vision Stream)
# ---------------------------------------------------------------------------
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

# Globaler Zwischenspeicher für den letzten Vision-Zustand (Sonde)
LATEST_VISION_STATE = {}

@router.get("/vision_state")
async def get_vision_state():
    """Gibt den zuletzt empfangenen Vision-Vektor-State zurück."""
    return LATEST_VISION_STATE

@router.post("/vision_state")
async def post_vision_state(state: dict):
    """Empfängt den Vision-State vom VISION_SYNC Frontend (HTTP-Push)."""
    global LATEST_VISION_STATE
    LATEST_VISION_STATE = state
    logger.debug("[VISION_BRIDGE] post_vision_state empfangen und in LATEST_VISION_STATE gesichert.")
    return {"success": True}

@router.websocket("/vision_stream")
async def vision_stream_endpoint(websocket: WebSocket):
    """
    WebSocket-Endpunkt für den Empfang des VISION_SYNC Headless-Streams.
    Erwartet hochfrequente Float-Vektoren (Gaze, Blendshapes, Emotionen).
    """
    global LATEST_VISION_STATE
    await websocket.accept()
    logger.info("[VISION_BRIDGE] Sonde verbunden (WebSocket).")

    try:
        import time
        last_log = 0.0
        while True:
            data = await websocket.receive_json()
            LATEST_VISION_STATE = data  # State im RAM halten

            # Throttle-Logging, um die Konsole nicht zu sprengen
            current_time = time.time()
            if current_time - last_log > 2.0:
                emotion = data.get("emotion", "unknown")
                gaze = data.get("gaze", "unknown")
                objects = len(data.get("objects", []))
                logger.info(f"[VISION_BRIDGE] Vektoren-Ping | Gaze: {gaze} | Emotion: {emotion} | Objekte: {objects}")
                last_log = current_time

    except WebSocketDisconnect:
        logger.info("[VISION_BRIDGE] Sonde getrennt.")
    except Exception as e:
        logger.error(f"[VISION_BRIDGE] Fehler im Stream: {e}")
