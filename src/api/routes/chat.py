# ============================================================
# CORE-GENESIS: CORE COCKPIT CHAT ENDPOINT
# ============================================================

import os
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from loguru import logger
import asyncio

from src.services.scout_direct_handler import process_text_async

router = APIRouter()

CORE_API_TOKEN = os.getenv("CORE_API_TOKEN", "")


async def verify_api_token(request: Request):
    """Optional: Bearer-Token-Pruefung. Kein Token = Entwicklungsmodus ohne Auth."""
    if not CORE_API_TOKEN:
        return
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth[7:] != CORE_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _get_ws_auth(websocket: WebSocket) -> str:
    """Authorization aus Header oder Query ?token=xxx (Browser-WS kann keine Header setzen)."""
    for key, value in websocket.scope.get("headers", []):
        if key.lower() == b"authorization":
            v = value.decode() if isinstance(value, bytes) else value
            return v or ""
    token = websocket.query_params.get("token", "")
    return f"Bearer {token}" if token else ""


async def _verify_ws_token(websocket: WebSocket) -> bool:
    """Gleiche Pruefung wie verify_api_token, fuer WebSocket connect-Handler. True=OK, False=abgelehnt."""
    if not CORE_API_TOKEN:
        return True
    auth = _get_ws_auth(websocket)
    if not auth.startswith("Bearer ") or auth[7:] != CORE_API_TOKEN:
        await websocket.close(code=4001)
        return False
    return True


class ChatMessage(BaseModel):
    message: str
    mode: str = "fast"


async def _log_session_turn(user_msg: str, reply: str, mode: str):
    """Persistiert User+Antwort durch Multi-View in pgvector (session_logs)."""
    try:
        from src.db.multi_view_client import ingest_document
        import hashlib
        import uuid
        ts = asyncio.get_event_loop().time()
        h = hashlib.md5(f"{ts}{user_msg[:40]}".encode()).hexdigest()[:10]
        doc_id = f"session_{h}"

        # Trennung der Dokumente für präziseres Retrieval
        # 1. User Input
        await ingest_document(
            document=f"### USER INPUT\n{user_msg}",
            doc_id=f"{doc_id}_user",
            source_collection="session_logs",
            metadata={"mode": mode, "source": "cockpit_chat", "speaker": "user"},
        )
        # 2. CORE Reply
        await ingest_document(
            document=f"### CORE REPLY\n{reply}",
            doc_id=f"{doc_id}_core",
            source_collection="session_logs",
            metadata={"mode": mode, "source": "cockpit_chat", "speaker": "gemini", "is_ai": True},
        )
    except Exception as e:
        logger.warning(f"[SESSION-LOG] Persist fehlgeschlagen: {e}")


@router.post("/api/chat", dependencies=[Depends(verify_api_token)])
async def handle_chat_message(payload: ChatMessage):
    try:
        result = await process_text_async(payload.message)
        reply = result.get("reply", "Fehler bei der Verarbeitung.")
        asyncio.create_task(_log_session_turn(payload.message, reply, payload.mode))
        return {"response": reply, "success": result.get("success", False)}
    except Exception as e:
        logger.error(f"Fehler im /api/chat Endpoint: {e}")
        return {"response": f"Ein interner Fehler ist aufgetreten: {e}", "success": False}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket-Endpunkt für Echtzeit-Kommunikation.
    """
    if not await _verify_ws_token(websocket):
        return
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
