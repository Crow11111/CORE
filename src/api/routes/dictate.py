"""
Diktat + TTS Routen.

POST /api/dictate -- Audio -> **Whisper (lokal)** -> Text
POST /api/tts     -- Text  -> Gemini TTS -> Audio (WAV)
"""
from __future__ import annotations

import base64
import os
import uuid
import tempfile
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from loguru import logger
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

router = APIRouter(prefix="/api", tags=["dictate", "tts"])

# --- Whisper STT Konfiguration ---
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE = "int8" if WHISPER_DEVICE == "cpu" else "float16"

# Singleton für das Whisper-Modell, um es nur einmal zu laden
whisper_model: WhisperModel | None = None

def get_whisper_model() -> WhisperModel:
    global whisper_model
    if whisper_model is None:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper ist nicht installiert. Bitte `pip install faster-whisper` ausführen.")
        logger.info(f"[DIKTAT] Lade Whisper STT-Modell: {WHISPER_MODEL_SIZE} ({WHISPER_DEVICE}/{WHISPER_COMPUTE})...")
        t0 = time.monotonic()
        whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE,
        )
        logger.info(f"[DIKTAT] Whisper-Modell in {time.monotonic() - t0:.2f}s geladen.")
    return whisper_model


class DictateResponse(BaseModel):
    text: str
    duration_ms: int
    model: str


@router.post("/dictate", response_model=DictateResponse)
async def dictate(audio: UploadFile = File(...)):
    """Transkribiert eine Audio-Datei via faster-whisper (lokal)."""
    t0 = time.monotonic()

    try:
        model = get_whisper_model()
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Leere Audio-Datei")

    # Debugging: Speichere die empfangene Audiodatei
    debug_path = f"/tmp/received_audio_{uuid.uuid4().hex[:6]}.wav"
    with open(debug_path, "wb") as f:
        f.write(audio_bytes)
    logger.info(f"[DIKTAT] Empfangene Audiodatei gespeichert unter: {debug_path} ({len(audio_bytes)} bytes)")

    # Transkribiere mit Whisper
    try:
        # Nutze den Debug-Pfad für die Transkription
        segments, info = model.transcribe(debug_path, language="de")
        text = " ".join([s.text.strip() for s in segments]).strip()
        logger.info(f"[DIKTAT] Whisper Transkription erfolgreich: '{text[:80]}...'")
    except Exception as e:
        logger.error(f"[DIKTAT] Whisper Transkriptionsfehler: {e}")
        raise HTTPException(status_code=500, detail=f"Whisper Fehler: {e}")

    duration_ms = int((time.monotonic() - t0) * 1000)
    model_info = f"whisper-{WHISPER_MODEL_SIZE}-{WHISPER_DEVICE}"

    return DictateResponse(text=text, duration_ms=duration_ms, model=model_info)


# --- Gemini TTS (unverändert) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

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
