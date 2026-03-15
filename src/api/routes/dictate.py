"""
Diktat-Route: Audio -> Gemini STT -> Transkription mit CORE-Glossar.

POST /api/dictate -- Nimmt Audio (WAV/WebM) entgegen, transkribiert via Gemini,
gibt Text zurueck. Frontend kann Mikrofon-Aufnahme senden.
"""
from __future__ import annotations

import base64
import os

import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["dictate"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = "gemini-2.5-flash"
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
async def dictate(audio: UploadFile = File(...)):
    """Transkribiert eine Audio-Datei via Gemini mit CORE-Glossar."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY nicht konfiguriert")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Leere Audio-Datei")

    mime = audio.content_type or "audio/wav"
    if "webm" in (audio.filename or ""):
        mime = "audio/webm"

    b64_data = base64.b64encode(audio_bytes).decode("utf-8")

    url = f"{BASE_URL}/{MODEL}:generateContent?key={GEMINI_API_KEY}"
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
        raise HTTPException(status_code=502, detail=f"Gemini API: {resp.status_code}")

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=502, detail="Keine Candidates von Gemini")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(p.get("text", "") for p in parts if "text" in p).strip()

    return DictateResponse(text=text, duration_ms=duration_ms, model=MODEL)
