# -*- coding: utf-8 -*-
"""
UCCP (UNIVERSAL CONTEXT CHECKPOINT) MANAGER
-------------------------------------------
Status: PROTOTYPE | OMEGA_SECURITY | V4
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, AsyncIterator, List
from loguru import logger

class UCCPManager:
    @staticmethod
    def generate_header(context_id: str, risk_score: float = 0.049) -> str:
        """Erzeugt einen komprimierten UCCP-Header für den Prompt."""
        header = {
            "UCCP_V": "4.0",
            "CID": context_id,
            "TS": datetime.utcnow().isoformat(),
            "RISK": risk_score,
            "CHKS": ["REALITY_DRIFT", "AUTH_SIGNATURE"]
        }
        return f"<UCCP_BLOCK>\n{json.dumps(header)}\n</UCCP_BLOCK>"

    @staticmethod
    def verify_output(text: str) -> bool:
        """Prüft ob der Output den UCCP-Anweisungen gefolgt ist."""
        # In V4.0 erwarten wir eine Bestätigung im Output
        return "UCCP_STATUS: CLEAN" in text or "UCCP_ACK" in text

class UCCPStreamInterceptor:
    """
    Middleware zur Stream-Interception für Echtzeit-Reality-Drift-Checks.
    Überwacht den Output auf behauptete Aktionen (Halluzinationen).
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.buffer = ""
        # Heuristik für behauptete Aktionen (Deutsch/Englisch)
        self.action_patterns = [
            r"ich habe .*?(?:gelöscht|geändert|angepasst|eingeschaltet|ausgeschaltet)",
            r"i have .*?(?:deleted|changed|updated|turned on|turned off)",
            r"erfolgreich (?:ausgeführt|erledigt|abgeschlossen)",
            r"successfully (?:executed|completed|finished)"
        ]

    async def intercept(self, stream: AsyncIterator[str]) -> AsyncIterator[str]:
        """Iteriert über den Stream und filtert Halluzinationen."""
        async for chunk in stream:
            self.buffer += chunk

            # Reality Drift Check (bei Satzende ODER wenn der Buffer groß genug ist)
            if any(char in chunk for char in ".!?\n") or len(self.buffer) > 50:
                drift_detected = await self._check_reality_drift(self.buffer)
                if drift_detected:
                    logger.warning(f"[UCCP-STREAM] Reality Drift erkannt in Session {self.session_id}!")
                    # Ersetze die Halluzination durch eine System-Warnung
                    self.buffer = "[UCCP_VETO: Reality Drift detected. Model claimed unverified action.]"
                    yield self.buffer
                    self.buffer = ""
                    # Wir brechen den Stream hier ab, da die Kohärenz verloren ging
                    return

            # Wir flushen den Buffer regelmäßig
            if len(self.buffer) > 100:
                yield self.buffer
                self.buffer = ""

        if self.buffer:
            yield self.buffer

    async def _check_reality_drift(self, text: str) -> bool:
        """
        Prüft ob im Text eine Aktion behauptet wird, die nicht im Recall Memory steht.
        """
        has_claim = any(re.search(p, text, re.IGNORECASE) for p in self.action_patterns)
        if not has_claim:
            return False

        # ANSTEHEND: Echte Prüfung gegen PostgreSQL Recall Memory
        # Für den V4-Prototyp simulieren wir: Wenn kein Werkzeug-Aufruf in der aktuellen Session
        # bekannt ist, aber eine Aktion behauptet wird -> Drift.
        logger.debug(f"[UCCP-CHECK] Analysiere Claim: '{text[:50]}...'")

        # Simulierter Check: Wir gehen davon aus, dass wir in dieser Session
        # noch keine echten Schreib-Aktionen im Recall Memory haben.
        return True # In der Testphase sind Claims ohne echten Tool-Call immer Drift.

def inject_uccp(prompt: str, context_id: str) -> str:
    return UCCPManager.generate_header(context_id) + "\n" + prompt
