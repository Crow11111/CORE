# -*- coding: utf-8 -*-
r"""
OMEGA SCOUT ADJUNCTION BRIDGE
-----------------------------
Abonniert den Morphismus-Stream und setzt kognitive Shifts in physische
Hardware-Aktionen (Home Assistant) um.

Phase 3.999: Der Durchstich in die physische Realität.
"""

import asyncio
import json
import logging
import os
import sys
import time
import numpy as np
import websockets
import httpx
from dotenv import load_dotenv
from loguru import logger

# Project Paths
sys.path.append(os.getcwd())
from src.config.core_state import BARYONIC_DELTA

load_dotenv("/OMEGA_CORE/.env")

HASS_URL = (os.getenv("HASS_URL") or "").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or "").strip()
STREAM_URL = os.getenv("MORPHISM_STREAM_URL", "ws://localhost:8001")

class ScoutAdjunctionBridge:
    def __init__(self):
        self.running = True
        self.last_action_time = 0
        self.cooldown = 10.0 # Sekunden

    async def trigger_hass_action(self, entity_id: str, service: str, data: dict = None):
        """Sendet einen Service-Call an Home Assistant."""
        if not HASS_URL or not HASS_TOKEN:
            logger.warning(f"[SCOUT] HASS nicht konfiguriert. Simuliere Aktion: {service} auf {entity_id}")
            return

        url = f"{HASS_URL}/api/services/{entity_id.split('.')[0]}/{service}"
        headers = {
            "Authorization": f"Bearer {HASS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"entity_id": entity_id}
        if data:
            payload.update(data)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers, timeout=5.0)
                if resp.status_code in (200, 201):
                    logger.info(f"[ADJUNKTION] Hardware-Durchstich erfolgreich: {service} -> {entity_id}")
                else:
                    logger.error(f"[SCOUT] HASS Error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"[SCOUT] Connection failed: {e}")

    async def process_morphism(self, data: dict):
        """Analysiert den Morphismus und entscheidet über Hardware-Adjunktion."""
        category = data.get("category")
        target_state = np.array(data.get("target_state", []))

        if category == "CORE_COGNITION" and len(target_state) >= 6:
            # S=Weight, P=Delta, I=Intent, R=Attempts, Z=Strikes, G=Time
            weight = target_state[0]
            strikes = target_state[4]

            # LOGIK: Wenn die Präzision hoch ist (Resonanz-Lock) und keine Fehler vorliegen,
            # triggern wir einen visuellen Puls (z.B. eine Lampe oder ein Event).
            if weight > 0.9 and strikes == 0:
                now = time.time()
                if now - self.last_action_time > self.cooldown:
                    logger.info(f"[SCOUT] Hohe Resonanz ({weight:.3f}) detektiert. Triggere Adjunktion.")
                    # Hier setzen wir ein persistentes Flag für das Cockpit
                    await self.trigger_hass_action("input_boolean.omega_resonance_lock", "turn_on")
                    self.last_action_time = now

            # LOGIK: Bei Strike 3 (Apoptose) triggern wir eine Warnung
            elif strikes >= 0.99: # Strike 3/3
                 logger.critical("[SCOUT] APOPTOSE-SHIFT DETEKTIERT. Hardware-Veto!")
                 await self.trigger_hass_action("persistent_notification", "create", {
                     "title": "OMEGA LAVA-LOCK",
                     "message": "System-Apoptose eingeleitet. Instanz wird isoliert."
                 })

    async def run(self):
        logger.info(f"[SCOUT] Bridge gestartet. Verbinde mit {STREAM_URL}...")

        while self.running:
            try:
                async with websockets.connect(STREAM_URL) as ws:
                    logger.info("[SCOUT] Verbunden mit Morphismus-Stream.")
                    async for message in ws:
                        data = json.loads(message)
                        if data.get("type") == "NATURAL_TRANSFORMATION":
                            await self.process_morphism(data)

            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError):
                logger.warning("[SCOUT] Stream offline. Reconnect in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"[SCOUT] Bridge Error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    bridge = ScoutAdjunctionBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        logger.info("[SCOUT] Bridge gestoppt.")
