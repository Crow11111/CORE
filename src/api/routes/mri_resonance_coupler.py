# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
MRI Resonance Coupler (MRI-RC)
Rein funktionale Brücke zur Google Gemini API (Stand 2026).
Eliminiert inkompatible Cursor-Parameter und erzwingt Reasoning-Resonanz.
"""

import os
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

router = APIRouter(prefix="/v1/mri", tags=["MRI-Resonanz"])

@router.post("/chat/completions")
async def resonance_chat_endpoint(request: Request):
    """
    Kardanischer Ingress für LLM-Anfragen.
    Säubert den Payload von Cursor-Altlasten.
    """
    payload = await request.json()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    # 1. Parameter-Sanierung (Axiom A7)
    # Wir entfernen alles, was nicht in der Google v1beta Spezifikation steht.
    model_id = payload.get("model", "gemini-3.1-pro-preview")
    messages = payload.get("messages", [])
    
    # 2. Modell-Weiche (Asymmetrische Logik)
    is_flash_lite = "flash-lite" in model_id.lower()
    is_pro = "pro" in model_id.lower()

    # 3. Aufbau des Google-Native Payloads
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    gemini_payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": payload.get("temperature", 0.7)
        }
    }

    # Thoughts nur für Flash-Lite oder explizit angefordert (ohne Signatur-Zwang für Pro)
    if is_flash_lite:
        gemini_payload["generationConfig"]["thinkingConfig"] = {
            "includeThoughts": True,
            "thinkingLevel": "high"
        }

    # 4. API-Call an Google
    target_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(target_url, json=gemini_payload, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            
            # 5. Rücktransformation in OpenAI-Format für Cursor
            # (Hier reduzierte Logik für den Ingress)
            text_parts = []
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "text" in p:
                        text_parts.append(p["text"])
            
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "".join(text_parts)
                    },
                    "finish_reason": "stop"
                }]
            }
            
        except Exception as e:
            logger.error(f"[MRI-RC] Google API Error: {e}")
            return JSONResponse({"error": str(e)}, status_code=502)
