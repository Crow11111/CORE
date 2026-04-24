"""
MRI Resonance Coupler (MRI-RC) v2.0
Rein funktionale Brücke zur Google Gemini API (Stand 2026).
Nutzt das offizielle google-genai SDK für maximale Stabilität.
"""

import os
import asyncio
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from google import genai
from google.genai import types

router = APIRouter(prefix="/v1", tags=["MRI-Resonanz"])

from src.daemons.system_bus_daemon import bus_instance

# Globaler Client-Singleton für Ressourceneffizienz
_client = None

def get_genai_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing")
        _client = genai.Client(api_key=api_key)
    return _client

@router.post("/chat/completions")
async def resonance_chat_endpoint(request: Request):
    """
    Kardanischer Ingress für LLM-Anfragen.
    Säubert Payload radikal (Entfernung von IDE-Dross wie extra_body).
    """
    try:
        raw_payload = await request.json()
    except Exception as e:
        logger.error(f"[MRI-RC] Invalid JSON Request: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        client = get_genai_client()
    except ValueError as e:
        logger.error(f"[MRI-RC] {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # 1. RADIKALE SANIERUNG (Axiom A7)
    # Whitelist-Extraktion zur Vermeidung von IDE-Dross (extra_body/disable_thought_tag)
    model_id = raw_payload.get("model", "gemini-3.1-pro-preview")
    messages = raw_payload.get("messages", [])
    temperature = raw_payload.get("temperature", 0.7)
    system_instruction = raw_payload.get("systemInstruction")
    
    # 2. Resonanz-Injektion (Systemzustand)
    try:
        grv = bus_instance.get_grv()
        state_hash = bus_instance.get_state_hash()
        resonance_prompt = f"\n[OMEGA-RESONANCE-ACTIVE]\nGRV: {grv}\nCAUSAL-HASH: {state_hash}\n"
        
        # Injektion in den System-Prompt (Axiom A7: Resonanz-Pflicht)
        for m in messages:
            if m.get("role") == "system":
                m["content"] = str(m.get("content", "")) + resonance_prompt
                break
        else:
            messages.insert(0, {"role": "system", "content": resonance_prompt})
    except Exception as e:
        logger.warning(f"[MRI-RC] Resonance Injection failed: {e}")

    # 3. Transformation OpenAI -> Gemini SDK (Whitelisted)
    contents = []
    # System-Instruction: Bevorzugt aus Top-Level (Directive), sonst Fallback auf messages
    sys_instruct = system_instruction 

    for m in messages:
        role = m.get("role")
        content = str(m.get("content", ""))
        
        if role == "system":
            if sys_instruct:
                sys_instruct += "\n" + content
            else:
                sys_instruct = content
        else:
            gemini_role = "user" if role == "user" else "model"
            contents.append(types.Content(role=gemini_role, parts=[types.Part(text=content)]))

    # 4. Asymmetrische Logik (Axiom A5)
    raw_temp = float(temperature)
    safe_temp = max(0.049, min(0.951, raw_temp))
    if abs(safe_temp - 0.5) < 0.01: safe_temp = 0.499

    # 5. SDK-Aufruf (Axiom A7: Keine IDE-Parameter)
    try:
        logger.info(f"[MRI-RC] Forwarding sanitized payload: {model_id}")
        
        # Generierung mit expliziter Konfiguration
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=safe_temp,
            )
        )
        
        # 6. Egress-Transformation (A7)
        full_text = response.text
        
        return {
            "id": f"mri-{os.urandom(4).hex()}",
            "object": "chat.completion",
            "created": 1776758400,
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
                "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0
            }
        }
        
    except Exception as e:
        logger.error(f"[MRI-RC] SDK Execution Error: {e}")
        return JSONResponse(
            {"error": "SDK-Execution-Failure", "detail": str(e)}, 
            status_code=502
        )
