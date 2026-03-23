import os
import io
import asyncio
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from loguru import logger
from src.voice.tts_dispatcher import dispatch_tts

router = APIRouter()

@router.post("/v1/audio/speech")
async def generate_speech(request: Request):
    """
    OpenAI-kompatibler TTS Endpoint für Jarvis.
    Nutzt das OMEGA CORE TTS Routing (Gemini/Kore oder ElevenLabs) und gibt den Audio-Stream an Jarvis zurück.
    """
    try:
        payload = await request.json()
        text = payload.get("input", "")
        # Jarvis uebergibt die Stimme, aber wir steuern sie zentral ueber OMEGA_CORE (Kore).

        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        # Wir nutzen den zentralen dispatch_tts aus OMEGA, um Konsistenz zu garantieren.
        # Er nutzt die Fallback-Kette: Gemini -> ElevenLabs -> Piper -> HA.
        # play=False ist hier implizit, da wir den Stream abfangen wollen,
        # aber dispatch_tts spielt normalerweise ab. Wir brauchen eine Version, die nur die Datei liefert.

        # Wir nutzen hier direkt die Fallback-Chain von dispatch_tts, aber ohne 'play'.
        from src.voice.tts_dispatcher import _gemini_speak, _elevenlabs_speak

        output_path = await _elevenlabs_speak(text, play=False)
        if not output_path:
            output_path = await _gemini_speak(text, play=False)

        if not output_path or not os.path.isfile(output_path):
            return JSONResponse({"error": "TTS Generierung fehlgeschlagen"}, status_code=500)

        # Audio-Datei einlesen und an Jarvis als Stream uebergeben
        with open(output_path, "rb") as f:
            audio_data = f.read()

        # Cleanup
        try:
            os.remove(output_path)
        except:
            pass

        return Response(content=audio_data, media_type="audio/wav")

    except Exception as e:
        logger.error(f"[JARVIS-TTS] Fehler bei der Sprachsynthese: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

