"""
MRI Resonance Coupler (MRI-RC)
Rein funktionale Brücke zur Google Gemini API (Stand 2026).
Eliminiert inkompatible Cursor-Parameter (z.B. disable_thought_tag) autonom.
"""

import os
import httpx
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

router = APIRouter(prefix="/v1", tags=["MRI-Resonanz"])

from src.daemons.system_bus_daemon import bus_instance

@router.post("/chat/completions")
async def resonance_chat_endpoint(request: Request):
    """
    Kardanischer Ingress für LLM-Anfragen.
    Emuliert eine OpenAI-Schnittstelle zur Umgehung von Cursor-Bugs.
    """
    try:
        raw_payload = await request.json()
    except Exception as e:
        logger.error(f"[MRI-RC] Invalid JSON Request: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    # 1. RADIKALE SANIERUNG (Axiom A7)
    # Wir extrahieren NUR die Felder, die Google v1beta wirklich kennt.
    # Wir ignorieren 'extra_body', 'disable_thought_tag' und anderen IDE-Dreck.
    
    model_id = raw_payload.get("model", "gemini-3.1-pro-preview")
    messages = raw_payload.get("messages", [])
    temperature = raw_payload.get("temperature", 0.7)

    # 2. Resonanz-Injektion (Systemzustand)
    try:
        grv = bus_instance.get_grv()
        state_hash = bus_instance.get_state_hash()
        resonance_prompt = f"\n[OMEGA-RESONANCE-ACTIVE]\nGRV: {grv}\nCAUSAL-HASH: {state_hash}\n"
        
        for m in messages:
            if m.get("role") == "system":
                m["content"] = str(m.get("content", "")) + resonance_prompt
                break
        else:
            messages.insert(0, {"role": "system", "content": resonance_prompt})
    except Exception as e:
        logger.warning(f"[MRI-RC] Resonance Injection failed: {e}")

    # 3. Aufbau des Google-Native Payloads von Null an
    contents = []
    sys_instruct = None

    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        
        if role == "system":
            sys_instruct = {"parts": [{"text": content}]}
        else:
            gemini_role = "user" if role == "user" else "model"
            contents.append({"role": gemini_role, "parts": [{"text": content}]})

    # 4. Asymmetrische Logik für 2026 (Pro vs. Flash-Lite)
    is_flash_lite = "flash-lite" in model_id.lower()
    
    gemini_payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": float(temperature)
        }
    }
    
    if sys_instruct:
        gemini_payload["systemInstruction"] = sys_instruct

    # Thoughts-Handling
    if is_flash_lite:
        gemini_payload["generationConfig"]["thinkingConfig"] = {
            "includeThoughts": True,
            "thinkingLevel": "high"
        }

    # 5. API-Call an Google
    target_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"[MRI-RC] Forwarding to Google: {model_id} (Sanitized)")
            resp = await client.post(target_url, json=gemini_payload, timeout=90.0)
            
            if resp.status_code != 200:
                error_data = resp.json()
                logger.error(f"[MRI-RC] Google Error: {error_data}")
                return JSONResponse(content=error_data, status_code=resp.status_code)
                
            data = resp.json()
            
            # 5. Rücktransformation in OpenAI-Format für Cursor
            text_parts = []
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "text" in p:
                        text_parts.append(p["text"])
            
            full_text = "".join(text_parts)
            
            return {
                "id": f"mri-{os.urandom(4).hex()}",
                "object": "chat.completion",
                "created": 1776758400, # April 2026
                "model": model_id,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": full_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
        except Exception as e:
            logger.error(f"[MRI-RC] Connection Error: {e}")
            return JSONResponse({"error": "Gateway Connection Failed", "detail": str(e)}, status_code=502)
