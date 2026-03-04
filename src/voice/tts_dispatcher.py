"""
TTS-Dispatcher: Verteilt TTS an Mini (HA) oder lokal (ElevenLabs) oder beides parallel.
"""
from __future__ import annotations

import asyncio
import os

from loguru import logger

from dotenv import load_dotenv
load_dotenv()


DEFAULT_ENTITY = "media_player.schreibtisch"


async def dispatch_tts(
    text: str,
    target: str = "mini",
    role_name: str = "atlas_dialog",
) -> bool:
    """
    Spielt TTS ab.
    - target='mini': HA TTS auf Minis (google_translate_say)
    - target='local': ElevenLabs lokal auf PC
    - target='both': Beides parallel
    """
    text = (text or "").strip()
    if not text:
        logger.warning("dispatch_tts: leerer Text, überspringe.")
        return False

    target = (target or "mini").lower()

    async def _mini() -> bool:
        entity_id = os.getenv("TTS_CONFIRMATION_ENTITY", DEFAULT_ENTITY).strip() or DEFAULT_ENTITY
        try:
            from src.connectors.home_assistant import HomeAssistantClient
            client = HomeAssistantClient()
            result = await client.call_service(
                "tts", "google_translate_say",
                {"entity_id": entity_id, "message": text},
            )
            if result is None:
                result = await client.call_service("tts", "cloud_say", {"entity_id": entity_id, "message": text})
            return result is not None
        except Exception as e:
            logger.error(f"TTS mini fehlgeschlagen: {e}")
            return False

    async def _local() -> bool:
        try:
            from src.voice.elevenlabs_tts import speak_text
            path = await asyncio.to_thread(
                speak_text, text, role_name, "", None, True
            )
            return path is not None
        except Exception as e:
            logger.error(f"TTS local fehlgeschlagen: {e}")
            return False

    if target == "mini":
        return await _mini()
    if target == "local":
        return await _local()
    if target == "both":
        ok_mini, ok_local = await asyncio.gather(_mini(), _local())
        return ok_mini or ok_local

    logger.warning(f"dispatch_tts: unbekanntes target='{target}', nutze mini.")
    return await _mini()
