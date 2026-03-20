"""
Diktat + TTS Routen.

POST /api/dictate -- Audio -> Gemini STT -> Text
POST /api/tts     -- Text  -> Gemini TTS -> Audio (WAV)
"""
from __future__ import annotations

import base64
import os

import httpx
from loguru import logger
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["dictate", "tts"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


def _stt_model(mode: str | None = None) -> str:
    """Live = Flash (schnell), sonst Pro (semantisch schaerfer). mode=live -> Flash."""
    from src.ai.model_registry import get_model_for_role
    if (mode or "").strip().lower() == "live":
        return (get_model_for_role("dictate_stt_live") or "gemini-2.5-flash").strip()
    return (get_model_for_role("dictate_stt") or "gemini-2.5-pro").strip()
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

CORE_GLOSSARY = (
    "CORE-Fachbegriffe die korrekt geschrieben werden MUESSEN:\n"
    "CORE, Atlas, Dreadnought, Scout, OpenClaw, ChromaDB, pgvector, Ollama, "
    "Tesserakt, Gravitator, Apoptose, Apotheose, Isomorphie, Symmetriebruch, "
    "baryonisch, baryonisches Delta, Entropie, Fibonacci, Phi, Goldener Schnitt, "
    "Embedding, Multi-View-Embedding, Konvergenz, Neurodivergent, ND, AUDHD, "
    "CAR/CDR, Cons-Zelle, Fallback, Pipeline, Dispatcher, MCP, VPS, SSH, TTS, "
    "STT, RAG, LLM, Gemini, Piper, Whisper, ElevenLabs, Home Assistant, HA, "
    "Docker, Cursor, Strang, Osmium, Ring-0, Hatamoto, CrystalGridEngine, "
    "nomic-embed-text, qwen2.5, llama3, Agos, Watchdog, Cockpit"
)

SYSTEM_PROMPT = (
    "Du bist ein praeziser Transkriptions-Assistent fuer CORE. "
    "Der Sprecher ist Marc, deutsch, neurodivergent (AUDHD), denkt assoziativ und schnell. "
    "Transkribiere woertlich und vollstaendig. Keine Zusammenfassungen. "
    "Nutze das CORE-Glossar fuer korrekte Schreibweise aller Fachbegriffe. "
    "Gib NUR die Transkription aus.\n\n"
    f"{CORE_GLOSSARY}"
)


class DictateResponse(BaseModel):
    text: str
    duration_ms: int
    model: str


@router.post("/dictate", response_model=DictateResponse)
async def dictate(
    audio: UploadFile = File(...),
    mode: str | None = Query(None, description="live = Flash (schnell), fehlt oder pro = Pro (semantisch schaerfer)"),
):
    """Transkribiert eine Audio-Datei via Gemini mit CORE-Glossar. mode=live -> 2.5 Flash, sonst 2.5 Pro."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY nicht konfiguriert")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Leere Audio-Datei")

    mime = audio.content_type or "audio/wav"
    if "webm" in (audio.filename or ""):
        mime = "audio/webm"

    b64_data = base64.b64encode(audio_bytes).decode("utf-8")

    model = _stt_model(mode)
    url = f"{BASE_URL}/{model}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": mime, "data": b64_data}},
                {"text": "Transkribiere dieses Audio. Nutze das CORE-Glossar."},
            ]
        }],
    }

    import time
    t0 = time.monotonic()

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload)

    duration_ms = int((time.monotonic() - t0) * 1000)

    if resp.status_code != 200:
        logger.error(f"[DIKTAT] Gemini API Fehler {resp.status_code}: {resp.text}")
        raise HTTPException(status_code=502, detail=f"Gemini API: {resp.status_code}")

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=502, detail="Keine Candidates von Gemini")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(p.get("text", "") for p in parts if "text" in p).strip()

    return DictateResponse(text=text, duration_ms=duration_ms, model=model)


class TTSRequest(BaseModel):
    text: str
    voice: str = "Kore"
    style: str = ""


@router.post("/tts")
async def tts_speak(req: TTSRequest):
    """Generiert Sprache via Gemini TTS, liefert WAV zurueck."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY nicht konfiguriert")
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Leerer Text")

    import time
    t0 = time.monotonic()

    try:
        from src.voice.gemini_tts import speak_text
        wav_path = speak_text(
            text=req.text,
            voice_name=req.voice,
            style_prompt=req.style or None,
            play=False,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS fehlgeschlagen: {e}")

    if not wav_path or not os.path.isfile(wav_path):
        raise HTTPException(status_code=502, detail="TTS hat keine Datei erzeugt")

    return FileResponse(
        wav_path,
        media_type="audio/wav",
        headers={"X-TTS-Duration-Ms": str(int((time.monotonic() - t0) * 1000))},
    )
