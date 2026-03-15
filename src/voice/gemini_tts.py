"""
Gemini TTS: Hochwertige Sprachausgabe via Gemini 2.5 Flash TTS (Free Tier).

30 Stimmen, automatische Spracherkennung (de, en, ...), Emotion/Tempo per Prompt steuerbar.
Output: PCM 24kHz Mono -> WAV in media/.
"""
from __future__ import annotations

import os
import time
import wave
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

TTS_MODEL = "gemini-2.5-flash-preview-tts"
DEFAULT_VOICE = os.getenv("GEMINI_TTS_VOICE", "Kore").strip()
DEFAULT_STYLE = os.getenv("GEMINI_TTS_STYLE", "").strip()
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2
CHANNELS = 1


def _save_wav(pcm_data: bytes, path: str) -> str:
    with wave.open(path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    return path


def speak_text(
    text: str,
    voice_name: Optional[str] = None,
    style_prompt: Optional[str] = None,
    output_path: Optional[str] = None,
    play: bool = True,
) -> Optional[str]:
    """
    Generiert Sprache via Gemini TTS.

    Args:
        text: Der zu sprechende Text.
        voice_name: Stimme (z.B. 'Kore', 'Puck', 'Charon'). Default aus .env.
        style_prompt: Regie-Anweisung (z.B. 'Sage freundlich und ruhig:').
                      Wird dem Text vorangestellt.
        output_path: Pfad fuer die WAV-Datei. Default: media/gemini_tts_<timestamp>.wav
        play: Datei nach Erzeugung abspielen (os.startfile auf Windows).

    Returns:
        Pfad zur WAV-Datei oder None bei Fehler.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.error("GEMINI_API_KEY nicht gesetzt.")
        return None

    text = (text or "").strip()
    if not text:
        logger.warning("Gemini TTS: Leerer Text.")
        return None

    voice = (voice_name or DEFAULT_VOICE).strip()
    style = (style_prompt or DEFAULT_STYLE).strip()

    prompt = f"{style} {text}".strip() if style else text

    if not output_path:
        media_dir = os.path.join(os.getcwd(), "media")
        os.makedirs(media_dir, exist_ok=True)
        output_path = os.path.join(media_dir, f"gemini_tts_{int(time.time())}.wav")

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=TTS_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            ),
        )

        if (
            not response.candidates
            or not response.candidates[0].content
            or not response.candidates[0].content.parts
        ):
            logger.error("Gemini TTS: Keine Audio-Daten in der Antwort.")
            return None

        pcm_data = response.candidates[0].content.parts[0].inline_data.data
        if not pcm_data:
            logger.error("Gemini TTS: Audio-Daten leer.")
            return None

        _save_wav(pcm_data, output_path)
        logger.info(f"Gemini TTS: {len(pcm_data)} bytes -> {output_path} (Stimme: {voice})")

        if play and os.path.isfile(output_path):
            os.startfile(output_path)

        return output_path

    except ImportError:
        logger.error("google-genai nicht installiert: pip install google-genai")
        return None
    except Exception as e:
        logger.error(f"Gemini TTS fehlgeschlagen: {e}")
        return None
