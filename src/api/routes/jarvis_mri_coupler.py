import os
import time
import asyncio
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
import httpx

from src.db.multi_view_client import embed_local, ingest_document
from src.logic_core.crystal_grid_engine import CrystalGridEngine
from src.config.core_state import BARYONIC_DELTA

router = APIRouter()


def _strip_env(s: str) -> str:
    return (s or "").strip().strip('"').strip("'")


# Zuvor nur OLLAMA_LOCAL_HOST → auf Dreadnought zeigt das oft auf leeres/falsches Ollama,
# während CORE bereits OLLAMA_HOST (z. B. LAN-Pi mit llama3.2:1b) nutzt.
# Reihenfolge: JARVIS_OLLAMA_URL (explizit fürs Plasmoid), OLLAMA_HOST, OLLAMA_LOCAL_HOST.
OLLAMA_API_BASE = (
    _strip_env(os.getenv("JARVIS_OLLAMA_URL"))
    or _strip_env(os.getenv("OLLAMA_HOST"))
    or _strip_env(os.getenv("OLLAMA_LOCAL_HOST"))
    or "http://127.0.0.1:11434"
).rstrip("/")

# Die 4 Dimensionen der Drehscheibe (MRI Coupler Matrix)
MODELS = {
    "core-local-min": {"type": "ollama", "target": "llama3.2:1b"}, # Oder qwen2.5:0.5b
    "core-local-max": {"type": "ollama", "target": "qwen2.5:14b"},
    "core-api-min": {"type": "gemini", "target": "gemini-2.5-flash"},
    "core-api-max": {"type": "gemini", "target": "gemini-2.5-pro"},
}

async def _inject_mri_pressure(prompt: str, response_text: str, start_time: float, model_id: str):
    """
    Die Magnetrotationsinstabilität (MRI).
    Das ist NICHT nur Logging. Das ist der Druck-Generator.
    """
    try:
        import hashlib
        ts = time.time()
        latency = ts - start_time

        # 1. Schnelles lokales Embedding (768-dim) für den Druck
        vector = await embed_local(prompt)
        if not vector:
            logger.warning("[JARVIS-MRI] Konnte kein Embedding erzeugen. Druckaufbau bricht hier ab.")
            return

        # 2. Vektor in die lokale Membran rammen (pgvector session_logs)
        h = hashlib.md5(f"{ts}{prompt[:40]}".encode()).hexdigest()[:10]
        doc_id = f"jarvis_mri_{h}"
        document = f"[JARVIS-MRI-IN ({model_id})] {prompt}\n\n[JARVIS-MRI-OUT] {response_text}"

        pressure_factor = 1.0 + (latency * BARYONIC_DELTA)
        snapped_pressure = CrystalGridEngine.apply_operator_query(pressure_factor)

        await ingest_document(
            document=document,
            doc_id=doc_id,
            source_collection="session_logs",
            metadata={
                "source": "jarvis_mri",
                "model": model_id,
                "latency": latency,
                "pressure": float(snapped_pressure)
            },
        )
        logger.info(f"[JARVIS-MRI] Druck erfolgreich in Membran injiziert. (Pressure: {snapped_pressure:.4f})")

        # 3. ZÜNDUNG DES EVENT-BUS
        try:
            with open("/tmp/mri_zündung.flag", "w") as f:
                f.write(f"{snapped_pressure}")

            from src.daemons.core_event_bus import event_bus_instance
            if event_bus_instance and getattr(event_bus_instance, "_running", False):
                fake_event = {
                    "event": {
                        "data": {
                            "entity_id": "mri.jarvis_zündung",
                            "new_state": {"state": "active", "latency": latency, "pressure": float(snapped_pressure)}
                        }
                    }
                }
                asyncio.create_task(event_bus_instance._handle_event(fake_event))
            else:
                logger.debug("[JARVIS-MRI] Event-Bus nicht aktiv, Zündung wird nur in Membran geschrieben.")
        except Exception as e:
            logger.warning(f"[JARVIS-MRI] Daemon-Trigger fehlgeschlagen: {e}")

    except Exception as e:
        logger.error(f"[JARVIS-MRI] Fehler bei der Druck-Injektion: {e}")


@router.get("/v1/models")
async def get_models():
    """Gibt die 4 Drehscheiben-Modi an Jarvis (KDE) aus."""
    data = []
    for m_id in MODELS.keys():
        data.append({"id": m_id, "object": "model", "owned_by": "omega-core"})
    return JSONResponse(content={"data": data})


@router.post("/v1/chat/completions")
async def jarvis_mri_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Die Drehscheibe (Router) für das KDE Jarvis Plasmoid."""
    payload = await request.json()
    messages = payload.get("messages", [])
    if not messages:
        return JSONResponse({"error": "No messages"}, status_code=400)

    # Letzten User-Prompt extrahieren
    latest_prompt = messages[-1].get("content", "")
    req_model = payload.get("model", "core-local-min")
    
    # Fallback
    if req_model not in MODELS:
        req_model = "core-local-min"
        
    config = MODELS[req_model]
    start_time = time.time()
    
    assistant_reply = ""
    usage_data = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    try:
        if config["type"] == "ollama":
            ollama_payload = {
                "model": config["target"],
                "messages": messages,
                "stream": False,
                "temperature": payload.get("temperature", 0.7)
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{OLLAMA_API_BASE}/api/chat", json=ollama_payload, timeout=300.0)
                resp.raise_for_status()
                ollama_data = resp.json()
                assistant_reply = ollama_data.get("message", {}).get("content", "")
                usage_data["prompt_tokens"] = ollama_data.get("prompt_eval_count", 0)
                usage_data["completion_tokens"] = ollama_data.get("eval_count", 0)
                usage_data["total_tokens"] = usage_data["prompt_tokens"] + usage_data["completion_tokens"]

        elif config["type"] == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return JSONResponse({"error": "GEMINI_API_KEY is missing"}, status_code=500)
            
            # Use raw HTTP for Gemini to avoid SDK differences
            contents = []
            sys_instruct = None
            
            for msg in messages:
                role = msg["role"]
                if role == "system":
                    sys_instruct = {"parts": [{"text": msg["content"]}]}
                    continue
                    
                gemini_role = "user" if role == "user" else "model"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": msg["content"]}]
                })
                
            gemini_payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": payload.get("temperature", 0.7)
                }
            }
            if sys_instruct:
                gemini_payload["systemInstruction"] = sys_instruct
                
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{config['target']}:generateContent?key={api_key}",
                    json=gemini_payload,
                    timeout=60.0
                )
                resp.raise_for_status()
                gemini_data = resp.json()
                
                try:
                    assistant_reply = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    assistant_reply = ""
                    logger.error(f"[JARVIS-MRI] Gemini parse error: {gemini_data}")
                    
                usage = gemini_data.get("usageMetadata", {})
                usage_data["prompt_tokens"] = usage.get("promptTokenCount", 0)
                usage_data["completion_tokens"] = usage.get("candidatesTokenCount", 0)
                usage_data["total_tokens"] = usage.get("totalTokenCount", 0)

        # OpenAI-kompatibles Format für Jarvis (Plasmoid) zusammenbauen
        openai_response = {
            "id": f"chatcmpl-jarvis-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req_model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": assistant_reply
                },
                "finish_reason": "stop"
            }],
            "usage": usage_data
        }

        # Asymmetrischen Druck im Hintergrund aufbauen (MRI Kupplung)
        background_tasks.add_task(_inject_mri_pressure, latest_prompt, assistant_reply, start_time, req_model)

        return JSONResponse(content=openai_response)

    except Exception as e:
        logger.error(f"[JARVIS-MRI] Fehler in der Schicht {req_model}: {e}")
        hint = ""
        if "ollama" in MODELS.get(req_model, {}).get("type", ""):
            hint = (
                f" Ollama-Basis: {OLLAMA_API_BASE}. "
                "Prüfe OLLAMA_HOST / OLLAMA_LOCAL_HOST in .env und ob das Modell "
                f"'{MODELS[req_model]['target']}' auf diesem Host existiert (ollama list)."
            )
        return JSONResponse({"error": str(e) + hint}, status_code=500)
