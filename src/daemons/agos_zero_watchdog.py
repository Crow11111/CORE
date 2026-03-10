# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
AGOS-0 WATCHDOG (Der intrinsische Beobachter).
Ersetzt den manuellen Trigger des Users durch systemische Selbst-Diagnose.

Funktion:
1. Überwacht den System-Puls (Heartbeat).
2. Misst die Entropie (Friction-Level). Zu ruhig -> Provokation.
3. Verwaltet den Traum-Transfer (Kristalle -> Wach-Logik).
4. Löst Lazarus-Protokoll aus, wenn Takt 4 (Remote) schweigt.
"""

import asyncio
import os
import sys
import time
import httpx
from datetime import datetime, timedelta
from loguru import logger

# Import Core Constants
sys.path.append(os.getcwd())
from src.config.omega_72_constants import ANCHOR_MAP

# Konfiguration
WATCHDOG_INTERVAL = 60.0  # Sekunden (Herzschlag)
MAX_WUJI_SILENCE = 3600.0 # 1 Stunde ohne Friction -> Trigger Provokation
REMOTE_TIMEOUT = 120.0    # Takt 4 Timeout -> Lazarus

# Status-Speicher (Flüchtig im RAM, da Watchdog immer läuft)
SYSTEM_STATE = {
    "last_friction_time": time.time(),
    "last_pulse": time.time(),
    "pending_crystals": 0,
    "mode": "BOOT" # BOOT, WATCH, DREAM, LAZARUS
}

API_URL = os.getenv("MTHO_VPS_URL", "http://localhost:8000")
WEBHOOK_URL = f"{API_URL}/webhook/omega_thought"

# Fake Token für Loopback
from dotenv import dotenv_values
env_vars = dotenv_values(".env")
HEADERS = {"Authorization": f"Bearer {env_vars.get('HA_WEBHOOK_TOKEN', '')}"}

async def check_vital_signs():
    """Prüft, ob die API (der Körper) überhaupt lebt."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}/status", timeout=5.0)
            if resp.status_code == 200:
                return True
    except Exception:
        return False
    return False

async def inject_stimulus(thought: str, context_type: str):
    """Feuert einen Gedanken in den eigenen Cortex (Selbstgespräch)."""
    payload = {
        "thought": thought,
        "context": {"type": context_type, "source": "AGOS_0_WATCHDOG"},
        "sender": "SYSTEM_INTERNAL",
        "require_response": True
    }
    try:
        async with httpx.AsyncClient(verify=False) as client:
            await client.post(WEBHOOK_URL, json=payload, headers=HEADERS, timeout=30.0)
            logger.info(f"[WATCHDOG] Stimulus injiziert: {context_type}")
            SYSTEM_STATE["last_friction_time"] = time.time() # Reset Wuji-Timer
    except Exception as e:
        logger.error(f"[WATCHDOG] Stimulus fehlgeschlagen: {e}")

async def process_dream_residue():
    """
    Liest Traum-Kristalle beim Booten und füttert sie dosiert ein.
    Verhindert Hyper-Arousal durch Pufferung.
    """
    # TODO: Hier müsste der Chroma-Client gelesen werden.
    # Für V1 simulieren wir das Prüfen der DB.
    logger.info("[WATCHDOG] Prüfe Traum-Kristalle in Wuji-Feld...")
    # Mock: Wir nehmen an, es gibt Kristalle (aus der Nacht)
    crystals_found = True 
    
    if crystals_found and SYSTEM_STATE["mode"] == "BOOT":
        logger.info("[WATCHDOG] Kristalle gefunden. Initiiere kontrolliertes Erwachen.")
        await inject_stimulus(
            "System Boot. Traum-Kristalle erkannt. Starte Integration der Dissonanzen von gestern.",
            "WAKE_UP_PROTOCOL"
        )
        SYSTEM_STATE["mode"] = "WATCH"

async def watchdog_loop():
    logger.info("AGOS-0 WATCHDOG gestartet. Ich beobachte.")
    
    # Initial: Warten auf API
    while not await check_vital_signs():
        logger.warning("[WATCHDOG] API nicht erreichbar. Warte auf Körper...")
        await asyncio.sleep(10)
    
    # Boot-Phase: Träume integrieren
    await process_dream_residue()
    
    while True:
        current_time = time.time()
        
        # 1. Wuji-Check (Langeweile)
        silence_duration = current_time - SYSTEM_STATE["last_friction_time"]
        if silence_duration > MAX_WUJI_SILENCE:
            logger.warning(f"[WATCHDOG] Wuji-Warnung! {silence_duration}s Stille. Erzeuge Reibung.")
            await inject_stimulus(
                "System-Status zu stabil (Wuji). Axiom-Check erforderlich. Ist die Realität noch 72-Anker-konform?",
                "ENTROPY_INJECTION"
            )
        
        # 2. Heartbeat Log
        if current_time - SYSTEM_STATE["last_pulse"] > 300: # Alle 5 Min Log
            logger.info(f"[WATCHDOG] Puls stabil. Modus: {SYSTEM_STATE['mode']}. Silence: {int(silence_duration)}s")
            SYSTEM_STATE["last_pulse"] = current_time
            
        await asyncio.sleep(WATCHDOG_INTERVAL)

if __name__ == "__main__":
    if sys.platform == "win32":
        os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        asyncio.run(watchdog_loop())
    except KeyboardInterrupt:
        logger.info("[WATCHDOG] Beendet.")
