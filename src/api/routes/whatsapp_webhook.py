# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
WhatsApp Webhook (Evolution API / Home Assistant).
Empfängt eingehende Nachrichten von WhatsApp und leitet sie in die OMEGA-Taktung.
"""

import os
import json
import asyncio
import uuid
from dotenv import load_dotenv
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.auth_webhook import verify_whatsapp_auth
from src.network.ha_client import HAClient
from src.network.evolution_client import EvolutionClient
from src.ai.whatsapp_audio_processor import process_whatsapp_audio
from src.ai.llm_interface import core_llm
from src.network.openclaw_client import send_message_to_agent_async, is_configured as oc_configured
from src.api.entry_adapter import normalize_request, NormalizedEntry
from src.logic_core.takt_gate import check_takt_zero

load_dotenv("/OMEGA_CORE/.env")

router = APIRouter(prefix="/webhook", tags=["webhooks"])
ha_client = HAClient()
evolution_client = EvolutionClient()

ACCEPTED_MSG = "[Scout] Nachricht erhalten, verarbeite …"
OMEGA_GROUP_JID = "120363425156111771@g.us"


def _send_whatsapp(to_number: str, text: str, trace_id: str | None = None):
    """Zentraler Dispatcher (Sync): Versucht Evolution, Fallback auf HA."""
    if evolution_client.is_configured():
        evolution_client.send_whatsapp_sync(to_number, text, trace_id)
    else:
        ha_client.send_whatsapp(to_number=to_number, text=text)


async def _send_whatsapp_async(to_number: str, text: str, trace_id: str | None = None):
    """Zentraler Dispatcher (Async): Versucht Evolution, Fallback auf HA."""
    if evolution_client.is_configured():
        await evolution_client.send_whatsapp_async(to_number, text, trace_id)
    else:
        # HA client ist aktuell nur sync implementiert (Requests)
        await asyncio.to_thread(ha_client.send_whatsapp, to_number, text)


async def _mirror_to_oc_brain(text: str, sender: str, msg_type: str = "whatsapp") -> None:
    """Stufe 1: Fire-and-forget Kopie an OC Brain (non-blocking)."""
    if not oc_configured():
        return
    try:
        payload = f"[{msg_type.upper()}|{sender}] {text}"
        ok, msg = await send_message_to_agent_async(payload, agent_id="main", user=sender, timeout=10.0)
        if ok:
            logger.debug(f"OC Brain Mirror OK: {msg[:80]}")
        else:
            logger.warning(f"OC Brain Mirror fehlgeschlagen: {msg}")
    except Exception as e:
        logger.warning(f"OC Brain Mirror Exception: {e}")


@router.post("/whatsapp")
@router.post("/whatsapp/{event_name:path}")
async def receive_whatsapp(
    request: Request,
    background_tasks: BackgroundTasks,
    event_name: str | None = None,
    # _auth: None = Depends(verify_whatsapp_auth), # Temporär deaktiviert für Debugging
):
    """
    Empfängt WhatsApp-Nachrichten über Evolution API oder HA.
    Unterstützt Wildcard-Events (V2 webhookByEvents).
    """
    raw = await request.json()
    trace_id = f"WA-{uuid.uuid4().hex[:6].upper()}"

    # Event-Name aus URL oder Payload
    actual_event = (event_name or raw.get("event") or "").lower()
    logger.debug(f"[WA|{trace_id}] Received event: {actual_event}")

    # Debug: Rohen Payload wegschreiben
    try:
        log_dir = os.path.join("/OMEGA_CORE", "logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "last_whatsapp_webhook_raw.json"), "w") as f:
            json.dump(raw, f, indent=2)
    except Exception as e:
        logger.debug(f"[WA] Log file write failed: {e}")
    if isinstance(raw, str):
        try:
            raw_payload = json.loads(raw)
        except json.JSONDecodeError:
            raw_payload = {"raw": raw}
    else:
        raw_payload = raw

    # 1. Entry Adapter: Normalisierung (Membran)
    try:
        entry: NormalizedEntry = normalize_request("whatsapp", raw_payload)
    except Exception as e:
        logger.error(f"[WA|{trace_id}] Entry Adapter Normalization Failed: {e}")
        return {"status": "error", "reason": "normalization_failed"}

    event = entry.payload.get("event")
    data = entry.payload
    incoming_text = data.get("text", "")
    sender = data.get("sender", "unknown")
    msg_id = data.get("id")
    from_me = data.get("from_me", False)
    has_audio = data.get("has_audio", False)
    audio_seconds = data.get("audio_seconds")

    # 1.1 Status-Updates & Management-Events (Synchronisation)
    # Wir normalisieren Separatoren (. oder -) für den Vergleich
    normalized_event = actual_event.replace("-", ".")

    if normalized_event and normalized_event != "messages.upsert":
        # MESSAGES_UPDATE (Read-Status, Delete, etc.)
        if normalized_event == "messages.update":
            status = data.get("status") or "UNKNOWN"
            logger.debug(f"[WA|{trace_id}] [SYNC] Message Update: {sender} -> {status}")
            return {"status": "event_handled", "event": actual_event}

        # Management Events (Test, Connection)
        if normalized_event in ["test", "connection.update", "connection"]:
            logger.info(f"[WA|{trace_id}] [MANAGEMENT] {actual_event} erhalten.")
            return {"status": "event_handled", "event": actual_event}

        # Gruppen-Events (V2 nutzt oft GROUPS_UPSERT oder GROUP_UPDATE)
        if "group" in normalized_event:
            logger.info(f"[WA|{trace_id}] [GROUP-EVENT] {actual_event} erhalten.")
            # Falls UPSERT, wir lassen es durchlaufen für Triage
            if "upsert" not in normalized_event:
                return {"status": "event_handled", "event": actual_event}

        # Andere Events (Connection, Login, etc.)
        logger.debug(f"[WA|{trace_id}] [EVENT] {actual_event} ignoriert.")
        return {"status": "event_handled", "event": actual_event}

    # 1.2 Eigene Nachrichten (Operator am Handy) spiegeln
    if from_me:
        # BOT-Nachrichten filtern um Echo-Loops in OC zu vermeiden
        bot_prefixes = ("[scout]", "[core]", "🤖", "[oc]")
        low_txt = incoming_text.lower()
        if any(low_txt.startswith(p) for p in bot_prefixes):
            return {"status": "ignored", "reason": "bot_echo_filtered"}

        logger.info(f"[WA|{trace_id}] [SYNC] Eigene Nachricht (Handy) von {sender}: {incoming_text[:100]}")
        # Spiegelung an OC Brain für Konsistenz
        asyncio.create_task(_mirror_to_oc_brain(incoming_text, sender, "whatsapp_operator"))
        return {"status": "mirrored", "trace_id": trace_id}

    # 1.3 Mark as Read (Takt 1-Bestaetigung) - Nur wenn nicht schon in Settings aktiviert
    # Wir machen es trotzdem explizit für den 'Gelesen'-Status im CORE, falls gewünscht.
    # Aber wir deaktivieren es hier vorerst, um Redundanz-Loops zu vermeiden.
    # asyncio.create_task(evolution_client.mark_as_read_async(sender, msg_id, from_me=False))

    logger.info(f"[WA|{trace_id}] [TAKT 1] Nachricht von {sender}: {incoming_text[:100]}")

    low = (incoming_text or "").lower()
    is_omega_group = sender == OMEGA_GROUP_JID

    # ── OPENCLAW BRIDGE ───────────────────────────────────────────────────────
    if incoming_text and low.startswith("@oc"):
        # [TAKT 0 GATE]
        if not await check_takt_zero():
            await _send_whatsapp_async(sender, "[Veto|Takt0] System-Instabilität verweigert OpenClaw-Bridge.", trace_id)
            return {"status": "veto", "reason": "system_instability_takt0"}

        # @oc-Prefix abziehen
        t_oc = incoming_text[3:].strip()
        logger.success(f"[WA|{trace_id}] [TAKT 2] OpenClaw-Bridge aktiviert für: {t_oc}")

        async def run_oc_and_reply():
            from src.network.openclaw_client import send_message_to_agent_async
            # Wir übergeben den TraceID an OC Brain als User-Kontext (Workaround da API keine Metadaten-Felder hat)
            user_ctx = f"{sender}|{trace_id}"
            success, reply = await send_message_to_agent_async(t_oc, agent_id="main", user=user_ctx, timeout=60.0)

            reply_text = f"🤖 [OC] {reply}" if success else f"🤖 [OC|Error] {reply}"
            logger.info(f"[WA|{trace_id}] [TAKT 3/4] Sende OC-Antwort zurück an {sender}")
            await _send_whatsapp_async(sender, reply_text, trace_id)

        background_tasks.add_task(run_oc_and_reply)
        return {"status": "openclaw_bridge_started", "trace_id": trace_id}

    if not is_omega_group and incoming_text and not (low.startswith("@core") or low.startswith("@omega")):
        # In Gruppen ignorieren wir Nachrichten ohne Keyword.
        # Im Direktchat könnten wir theoretisch immer antworten, aber wir halten uns strikt.
        if "@g.us" in sender:
            return {"status": "ignored", "reason": "no_prefix_in_group"}

    # ── Sprachnachricht ───────────────────────────────────────────────────────
    message = raw_payload.get("message", {}) if isinstance(raw_payload, dict) else {}
    audio_msg = message.get("audioMessage") or message.get("pttMessage")

    if has_audio and audio_msg:
        # [TAKT 0 GATE]
        if not await check_takt_zero():
            await _send_whatsapp_async(sender, "[Veto|Takt0] System-Instabilität verweigert Audio.")
            return {"status": "veto", "reason": "system_instability_takt0"}

        # In der OMEGA-Gruppe akzeptieren wir Audio auch ohne Prefix
        if not is_omega_group and not (incoming_text and (low.startswith("@core") or low.startswith("@omega"))):
            # Check falls Audio ohne Text reinkommt (typisch für PTT)
            logger.debug("Audio PTT Check")

        logger.success(f"🎤 Sprachnachricht von {sender} ({audio_seconds}s)!")
        await _send_whatsapp_async(sender, f"[Scout] 🎤 Sprachmemo ({audio_seconds}s) empfangen. Analysiere...")

        async def run_audio():
            result = await process_whatsapp_audio(audio_msg, sender)
            await _send_whatsapp_async(sender, f"[CORE] {result}")

        background_tasks.add_task(run_audio)
        asyncio.create_task(_mirror_to_oc_brain(f"[AUDIO {audio_seconds}s]", sender, "whatsapp_voice"))
        return {"status": "audio_processing", "sender": sender, "seconds": audio_seconds}

    # ── Textnachricht ─────────────────────────────────────────────────────────
    if incoming_text:
        # [TAKT 0 GATE]
        if not await check_takt_zero():
            await _send_whatsapp_async(sender, "[Veto|Takt0] System-Instabilität verweigert Text.")
            return {"status": "veto", "reason": "system_instability_takt0"}

        # Prefix abziehen (falls vorhanden)
        t = incoming_text.strip()
        if t.lower().startswith("@core"):
            t = t[6:].strip() or t
        elif t.lower().startswith("@omega"):
            t = t[7:].strip() or t

        logger.success(f"💬 Textnachricht von {sender}: {incoming_text}")

        # Triage aufrufen
        triage = await asyncio.to_thread(core_llm.run_triage, t)

        if triage.intent == "command":
            def _cmd():
                domain = triage.target_entity.split(".")[0] if "." in (triage.target_entity or "") else "homeassistant"
                service = triage.action or "turn_on"
                success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity or "")
                return f"[Scout] ✅ {service} → {triage.target_entity}" if success else f"[Scout] ❌ Fehler: {service} → {triage.target_entity}"

            reply = await asyncio.to_thread(_cmd)
            await _send_whatsapp_async(sender, reply)
            asyncio.create_task(_mirror_to_oc_brain(t, sender, "whatsapp_cmd"))
            return {"status": "text_handled", "sender": sender, "intent": triage.intent}

        if triage.intent in ["deep_reasoning", "chat"]:
            await _send_whatsapp_async(sender, ACCEPTED_MSG)

            async def run_heavy_and_reply():
                sys_prompt = "Du bist OMEGA-CORE, ein hochintelligenter Assistent. Antworte präzise und direkt über WhatsApp. Sei dir bewusst, dass du direkt über die Evolution API mit dem Hostinger VPS sprichst."
                reply = await core_llm.invoke_heavy_reasoning(sys_prompt, t)
                reply_text = f"[CORE] {reply}" if reply else "[CORE] (keine Antwort)"
                await _send_whatsapp_async(sender, reply_text)

            background_tasks.add_task(run_heavy_and_reply)
            asyncio.create_task(_mirror_to_oc_brain(t, sender, "whatsapp_chat"))
            return {"status": "heavy_processing_started"}

    return {"status": "ignored", "reason": "no_text_or_audio"}
