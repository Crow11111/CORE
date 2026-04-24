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

# --- CAUSAL-SIEVE: GLOBAL CACHE (Axiom A7) ---
CAUSAL_ANCHOR_CACHE = {} # key: conversation_id, value: thought_signature

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

    # 0. Conversation Identity (CausalAnchor)
    conv_id = raw_payload.get("conversation_id")
    if not conv_id:
        # Fallback: Hash der messages (ohne die letzte User-Nachricht)
        try:
            msg_fingerprint = str(messages[:-1])
            conv_id = f"hc-{hash(msg_fingerprint)}"
        except:
            conv_id = "resonant-stream"

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

    # 3. Thought-Linker (LogicFlow-Anchoring)
    # Wir finden die letzte Assistant-Nachricht vor der aktuellen User-Eingabe
    last_assistant_idx = -1
    for i, m in enumerate(messages):
        if m.get("role") == "assistant":
            last_assistant_idx = i

    # 4. Aufbau des Google-Native Payloads von Null an
    contents = []
    sys_instruct = None

    for i, m in enumerate(messages):
        role = m.get("role")
        content = str(m.get("content", ""))
        
        if role == "system":
            sys_instruct = {"parts": [{"text": content}]}
        else:
            gemini_role = "user" if role == "user" else "model"
            parts = [{"text": content}]
            
            # Injektion der letzten bekannten Thought-Signature
            if i == last_assistant_idx and conv_id in CAUSAL_ANCHOR_CACHE:
                anchor = CAUSAL_ANCHOR_CACHE[conv_id]
                parts.append({"text": f"\n[CAUSAL-THOUGHT-ANCHOR: {anchor}]\n"})
                logger.info(f"[MRI-RC] Linked Thought-Anchor for {conv_id}")
            
            contents.append({"role": gemini_role, "parts": parts})

    # 5. Asymmetrische Logik für 2026 (Pro vs. Flash-Lite)
    is_flash_lite = "flash-lite" in model_id.lower()
    
    # Axiom A5: Temperature-Filter (Vermeidung von 0.0, 0.5, 1.0)
    raw_temp = float(temperature)
    if raw_temp <= 0.049: safe_temp = 0.049
    elif raw_temp >= 0.951: safe_temp = 0.951
    elif abs(raw_temp - 0.5) < 0.01: safe_temp = 0.499
    else: safe_temp = raw_temp

    gemini_payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": safe_temp
        }
    }
    
    if sys_instruct:
        gemini_payload["systemInstruction"] = sys_instruct

    # Thoughts-Handling (Google 2026er Spezifikation)
    if is_flash_lite or "pro" in model_id.lower():
        gemini_payload["generationConfig"]["thinkingConfig"] = {
            "includeThoughts": True,
            "thinkingLevel": "high"
        }

    # 6. API-Call an Google
    target_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"[MRI-RC] Forwarding to Google: {model_id} (Sanitized)")
            resp = await client.post(target_url, json=gemini_payload, timeout=90.049)
            
            if resp.status_code != 200:
                error_data = resp.json()
                logger.error(f"[MRI-RC] Google Error: {error_data}")
                return JSONResponse(content=error_data, status_code=resp.status_code)
                
            data = resp.json()
            
            # 7. Egress-Harvester & A7-Sicherung
            text_parts = []
            new_thought_signature = None
            
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    # Extrahiere Gedanken (Native 2026)
                    if "thought" in p:
                        new_thought_signature = p["thought"]
                        continue # A7: Gedanken NICHT an Cursor streamen
                    
                    if "text" in p:
                        text = p["text"]
                        # Fallback: Suche nach Markern im Text
                        if "[THOUGHT-SIGNATURE:" in text:
                            import re
                            match = re.search(r"\[THOUGHT-SIGNATURE:\s*(.*?)\]", text)
                            if match:
                                new_thought_signature = match.group(1)
                                text = re.sub(r"\[THOUGHT-SIGNATURE:\s*.*?\]", "", text).strip()
                        text_parts.append(text)
            
            if new_thought_signature:
                CAUSAL_ANCHOR_CACHE[conv_id] = new_thought_signature
                logger.info(f"[MRI-RC] Harvested new Signature for {conv_id}")
            
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
