# ============================================================
# CORE-GENESIS: OMEGA CENTRAL NERVE STEM (WATCHDOG V2)
# VECTOR: 2210 | DELTA: 0.049 | IDENTITY: OMEGA_HEPHAISTOS
# ============================================================

import asyncio
import json
import os
import sys
import time
import httpx
import re
import socket
import subprocess
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Path Setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent if "__file__" in locals() else Path(os.getcwd())
sys.path.append(str(PROJECT_ROOT))
load_dotenv()

try:
    from src.config.core_state import BARYONIC_DELTA, SYMMETRY_BREAK
    from src.logic_core.crystal_grid_engine import CrystalGridEngine
except ImportError:
    BARYONIC_DELTA = 0.049
    SYMMETRY_BREAK = 0.51

# Config
BASE_WATCHDOG_INTERVAL = 47.0 # Asymmetrischer Herzschlag (Sekunden)
MAX_BACKOFF_INTERVAL = 120.0
TELEMETRY_PATH = os.path.join(os.getenv("CORE_DATA_DIR", "/OMEGA_CORE/data"), "telemetry.json")
MIGRATION_PATH = "/OMEGA_CORE/data/migration/status.json"
MRI_PRESSURE_FILE = "/tmp/mri_zündung.flag"

API_URL = os.getenv("CORE_API_URL", "http://localhost:8000")
WEBHOOK_URL = f"{API_URL}/webhook/omega_thought"
HA_TOKEN = os.getenv("HA_WEBHOOK_TOKEN", "")

SYSTEM_STATE = {
    "latency_ms": -1.0,
    "ollama_status": "OFFLINE",
    "migration_status": "IDLE",
    "last_resonance": 0.049,
    "git_drift": "UNKNOWN",
    "last_update": 0
}

def sd_notify(state: str):
    """Sendet Zell-Puls direkt an systemd (Thermodynamik)."""
    sock_name = os.environ.get('NOTIFY_SOCKET')
    if not sock_name:
        return
    if sock_name.startswith('@'):
        sock_name = '\0' + sock_name[1:]
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
            sock.sendto(state.encode('utf-8'), sock_name)
    except Exception as e:
        logger.debug(f"sd_notify failed: {e}")

async def check_ollama(reflex_triggered=False) -> str:
    """Prüft ob der lokale Einbettungs-Dienst (Ollama) lebt. Inklusive Spinalem Reflex."""
    url = os.getenv("OLLAMA_EMBED_HOST", "http://localhost:11434") + "/api/tags"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return "ONLINE"
            return "ERROR"
    except Exception as e:
        # SPINALER REFLEX: Wenn Ollama offline ist, nicht sofort dem Hirn melden,
        # sondern wie ein Rückenmarksreflex einen Neustart versuchen.
        if not reflex_triggered and os.environ.get("IS_VPS") == "true":
            logger.warning("[SPINAL REFLEX] Ollama offline. Triggering immediate systemctl restart...")
            try:
                subprocess.run(["systemctl", "restart", "ollama"], check=False)
                await asyncio.sleep(2) # Kurz warten, dann rekursiver Re-Check
                return await check_ollama(reflex_triggered=True)
            except Exception as reflex_err:
                logger.error(f"[SPINAL REFLEX] Failed: {reflex_err}")
        return "OFFLINE"

async def check_migration() -> Dict[str, Any]:
    """Liest den Status der Hintergrund-Migration (HuggingFace -> OMEGA)."""
    if not os.path.exists(MIGRATION_PATH):
        return {"status": "INACTIVE", "progress": 0.0}
    try:
        with open(MIGRATION_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"status": "READ_ERROR", "progress": -1.0}

async def check_connectivity() -> float:
    """Misst Latenz zum Internet-Anker."""
    host = "8.8.8.8"
    param = "-n" if sys.platform.lower() == "win32" else "-c"
    try:
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            "ping", param, "1", host,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        if proc.returncode == 0:
            return (time.perf_counter() - start) * 1000.0
        return -1.0
    except Exception:
        return -1.0

def _write_telemetry(state: Dict[str, Any]):
    """Persistiert den System-Zustand für den 0/1 Schalter."""
    os.makedirs(os.path.dirname(TELEMETRY_PATH), exist_ok=True)
    try:
        with open(TELEMETRY_PATH + ".tmp", "w") as f:
            json.dump(state, f)
        os.replace(TELEMETRY_PATH + ".tmp", TELEMETRY_PATH)
    except Exception as e:
        logger.error(f"Telemetry write failed: {e}")

async def inject_nerve_signal(state: Dict[str, Any]):
    """
    Der Zentrale Nervenreiz:
    Sollte ein Dienst ausfallen (0/1), wird dies im Herzschlag injiziert.
    """
    # 0/1 Schalter Logik: Hard Fail Safe
    critical_failures = []
    if state["ollama_status"] != "ONLINE":
        critical_failures.append("OLLAMA_EMBED_OFFLINE")
    if state["migration_status"].get("status") == "CRASHED":
        critical_failures.append("WORLD_MIGRATION_FAILED")

    # Konstruiere die Meldung
    if critical_failures:
        thought = f"VETO: Zentraler Nervenstrang meldet Defekt: {', '.join(critical_failures)}. " \
                  f"Migration {state['migration_status'].get('status')}. " \
                  "Bitte System-Integrität prüfen."
        context_type = "SYSTEM_VETO"
    else:
        thought = f"Puls stabil. Latenz: {state['latency_ms']:.1f}ms. Ollama: {state['ollama_status']}. " \
                  f"Migration: {state['migration_status'].get('progress', 0)*100:.1f}%"
        context_type = "NERVE_PULSE"

    payload = {
        "thought": thought,
        "context": {
            "type": context_type,
            "source": "OMEGA_NERVE_STEM",
            "telemetry": state
        },
        "sender": "OMEGA_HEPHAISTOS",
        "require_response": bool(critical_failures)
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {"Authorization": f"Bearer {HA_TOKEN}"} if HA_TOKEN else {}
            await client.post(WEBHOOK_URL, json=payload, headers=headers)
            logger.info(f"[NERVE] Signal injected: {context_type}")
    except Exception as e:
        logger.error(f"[NERVE] Signal injection failed: {e}")

async def nerve_stem_loop():
    logger.info("OMEGA CENTRAL NERVE STEM online (Homeostasis V3).")
    sd_notify("READY=1")

    current_interval = BASE_WATCHDOG_INTERVAL

    while True:
        # 1. Sammle Daten (Mit Backoff/Homöostase Logic)
        try:
            latency = await check_connectivity()
            ollama = await check_ollama(reflex_triggered=False)
            migration = await check_migration()

            # Adaptives Polling: Alles gesund -> Reset Interval
            if ollama == "ONLINE" and latency > 0:
                if current_interval > BASE_WATCHDOG_INTERVAL:
                    logger.info(f"[L-VEKTOR] System stablisiert. Reset Interval auf {BASE_WATCHDOG_INTERVAL}s")
                current_interval = BASE_WATCHDOG_INTERVAL
            else:
                # Exponential Backoff bei Anomalien
                current_interval = min(current_interval * 1.5, MAX_BACKOFF_INTERVAL)
                logger.warning(f"[L-VEKTOR] Anomalie detektiert. Adaptives Polling: {current_interval:.1f}s")
        except Exception as net_err:
            logger.error(f"[HOMOEOSTASE] Loop error: {net_err}")
            current_interval = min(current_interval * 1.5, MAX_BACKOFF_INTERVAL)
            latency = -1.0
            ollama = "ERROR"
            migration = {"status": "NETWORK_ERROR", "progress": 0.0}

        # 2. Update State
        SYSTEM_STATE.update({
            "latency_ms": latency,
            "ollama_status": ollama,
            "migration_status": migration,
            "last_update": time.time()
        })

        # Resonance Calculation (Simple Mapping)
        res = 0.951 if latency > 0 and ollama == "ONLINE" else 0.049
        SYSTEM_STATE["last_resonance"] = res

        # 3. Persist (für check_omega_pulse / Toxische Telemetrie Check)
        _write_telemetry(SYSTEM_STATE)

        # 4. Inject into AI Consciousness
        await inject_nerve_signal(SYSTEM_STATE)

        # 5. Physische Thermodynamik-Zellatmung an das OS
        sd_notify("WATCHDOG=1")

        # 6. Check MRI (Instant Trigger)
        if os.path.exists(MRI_PRESSURE_FILE):
             # Trigger immediate cycle
             os.remove(MRI_PRESSURE_FILE)
             continue

        await asyncio.sleep(current_interval)

if __name__ == "__main__":
    asyncio.run(nerve_stem_loop())
