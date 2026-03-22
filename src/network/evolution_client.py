# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
Evolution API Client.
Verbindet CORE nativ mit WhatsApp über den Hostinger VPS (Baileys/Evolution API).
Ersetzt den Umweg über HA (whatsapp/send_message) als Primärkanal.
"""

import os
import urllib.parse
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

class EvolutionClient:
    def __init__(self):
        self.url = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
        self.apikey = os.getenv("EVOLUTION_API_KEY", "")
        # Instanzname für URL encoden (z.B. "Marc ten Hoevel" -> "Marc%20ten%20Hoevel")
        raw_instance = os.getenv("EVOLUTION_INSTANCE", "Marc ten Hoevel")
        self.instance = urllib.parse.quote(raw_instance)

        self.headers = {
            "apikey": self.apikey,
            "Content-Type": "application/json"
        }

    def is_configured(self) -> bool:
        return bool(self.url and self.apikey and self.instance)

    def _format_number(self, to_number: str) -> str:
        """Stellt sicher, dass Nummern oder Gruppen-JIDs korrekt formatiert sind."""
        to_number = to_number.strip()
        # Wenn es schon eine JID ist (z.B. @g.us für Gruppen oder @s.whatsapp.net), so lassen
        if "@" in to_number:
            return to_number

        # Nummern bereinigen (nur Ziffern)
        clean_num = "".join(c for c in to_number if c.isdigit())
        if clean_num.startswith("00"):
            clean_num = clean_num[2:]
        elif clean_num.startswith("0"):
            clean_num = "49" + clean_num[1:] # Annahme DE

        return f"{clean_num}@s.whatsapp.net"

    async def send_whatsapp_async(self, to_number: str, text: str, trace_id: str | None = None) -> bool:
        """
        Sendet asynchron eine Textnachricht.
        Integriert in CORE 5-Phase Engine (Takt 4).
        """
        if not self.is_configured():
            logger.error("EvolutionClient nicht konfiguriert (Prüfe EVOLUTION_API_URL, _KEY, _INSTANCE)")
            return False

        target = self._format_number(to_number)
        endpoint = f"{self.url}/message/sendText/{self.instance}"

        log_prefix = f"[Evolution API|{trace_id}]" if trace_id else "[Evolution API]"

        payload = {
            "number": target,
            "options": {
                "delay": 1200,          # 1.2s künstliche Verzögerung (Humanizer)
                "presence": "composing" # Zeigt "schreibt..." an
            },
            "text": text
        }

        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(endpoint, headers=self.headers, json=payload, timeout=15.0)
                if r.status_code in (200, 201):
                    logger.info(f"{log_prefix} [TAKT 4] Nachricht gesendet an {target}")
                    return True
                else:
                    logger.error(f"{log_prefix} [TAKT 4] Fehler {r.status_code}: {r.text}")
                    return False
        except Exception as e:
            logger.error(f"{log_prefix} [TAKT 4] HTTP Exception: {e}")
            return False

    def send_whatsapp_sync(self, to_number: str, text: str, trace_id: str | None = None) -> bool:
        """Synchroner Wrapper für Alt-Systeme."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(self.send_whatsapp_async(to_number, text, trace_id))
        except RuntimeError:
            return asyncio.run(self.send_whatsapp_async(to_number, text, trace_id))

    async def mark_as_read_async(self, remote_jid: str, message_id: str, from_me: bool = False) -> bool:
        """Markiert eine Nachricht als gelesen (Zwei blaue Haken)."""
        if not self.is_configured():
            return False

        endpoint = f"{self.url}/chat/markMessageAsRead/{self.instance}"
        payload = {
            "readMessages": [
                {
                    "remoteJid": remote_jid,
                    "fromMe": from_me,
                    "id": message_id
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(endpoint, headers=self.headers, json=payload, timeout=5.0)
                return r.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"[Evolution API] MarkAsRead Exception: {e}")
            return False
