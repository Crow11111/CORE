# ============================================================
# MTHO-GENESIS: CORE COCKPIT CHAT ENDPOINT
# ============================================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from loguru import logger
import asyncio

from src.services.scout_direct_handler import process_text_async

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    mode: str = "fast"

@router.post("/api/chat")
async def handle_chat_message(payload: ChatMessage):
    """
    Nimmt eine Chat-Nachricht vom Frontend entgegen und verarbeitet sie.
    """
    try:
        # Wir rufen die asynchrone Verarbeitungslogik auf
        result = await process_text_async(payload.message)
        return {"response": result.get("reply", "Fehler bei der Verarbeitung."), "success": result.get("success", False)}
    except Exception as e:
        logger.error(f"Fehler im /api/chat Endpoint: {e}")
        return {"response": f"Ein interner Fehler ist aufgetreten: {e}", "success": False}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket-Endpunkt für Echtzeit-Kommunikation.
    """
    await websocket.accept()
    logger.info("[WS] WebSocket-Verbindung akzeptiert.")
    try:
        while True:
            # Hier kann Logik für eingehende WS-Nachrichten implementiert werden
            # Vorerst lauschen wir nur auf die Verbindung.
            data = await websocket.receive_text()
            logger.debug(f"[WS] Nachricht empfangen: {data}")
            # Beispiel: Echo
            # await websocket.send_text(f"Echo: {data}")

            # Hier könnten wir auch proaktiv System-Events an das Frontend pushen
            await asyncio.sleep(1) # Hält die Verbindung offen

    except WebSocketDisconnect:
        logger.info("[WS] WebSocket-Verbindung getrennt.")
    except Exception as e:
        logger.error(f"[WS] Fehler im WebSocket: {e}")
