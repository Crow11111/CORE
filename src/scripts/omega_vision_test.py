#!/usr/bin/env python3
"""
OMEGA VISION EMPIRICAL TEST SUITE
Setzt das "Context-Triggered Validation" Design um.

Aufruf-Beispiele:
1. AWAY-Test (wartet auf iPhone = away, prüft dann alle 5 Min auf 'person' in lila Oberteil)
   python src/scripts/omega_vision_test.py --mode away

2. BASELINE-Erstellung (Takt 0 - Referenzmuster für Fokus/Arbeit)
   python src/scripts/omega_vision_test.py --mode baseline --duration 300 --note "morgens, tief im fokus"
"""

import asyncio
import time
import argparse
import requests
import json
import sys
import subprocess
from datetime import datetime
from loguru import logger
from pathlib import Path

# Setup Umgebung
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Fallback-Klassen, falls HomeAssistantClient in anderem Pfad
try:
    from src.connectors.home_assistant import HomeAssistantClient
except ImportError:
    HomeAssistantClient = None

LOG_FILE = Path("/OMEGA_CORE/docs/05_AUDIT_PLANNING/VISION_TEST_LOG.md")
BASELINE_FILE = Path("/OMEGA_CORE/docs/05_AUDIT_PLANNING/VISION_BASELINES.json")

def fetch_latest_state() -> dict:
    """Holt die aktuellsten Vektoren aus dem ATLAS Backend."""
    try:
        r = requests.get("http://localhost:8000/api/v1/system/vision_state", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        logger.warning(f"Konnte Vision State nicht abrufen: {e}")
    return {}

async def trigger_tts(text: str):
    """Spielt TTS über die mini Schnittstelle (Home Assistant) ab."""
    try:
        payload = {"text": text, "target": "mini", "role": "core_dialog"}
        requests.post("http://localhost:8000/api/core/dispatch-tts", json=payload, timeout=5)
        logger.info(f"[TTS] -> {text}")
    except Exception as e:
        logger.error(f"[TTS] Fehler: {e}")

class HeadlessVisionBridge:
    """Kontext-Manager, der den Playwright Headless-Daemon temporär startet."""
    def __init__(self):
        self.process = None

    def __enter__(self):
        logger.info("Starte internen Headless Vision Bridge (Sonde)...")
        # Startet den Daemon, der Chromium headless auf Port 3006 öffnet
        self.process = subprocess.Popen(
            [sys.executable, "-m", "src.daemons.scout_vision_bridge"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            logger.info("Beende Headless Vision Bridge. Schließe Kamera-Sonde.")
            self.process.terminate()
            self.process.wait(timeout=5)

async def mode_away():
    """
    Away-Modus:
    1. Prüft, ob das iPhone abwesend ist (oder überspringt, wenn HA nicht greifbar).
    2. Startet einen Loop (alle 5 Min).
    3. Sucht im Vision-State nach einer Person (und via Gemini-Analyse ggf. nach einem "lila Oberteil").
    """
    logger.info("Starte AWAY-Test. Warte auf Abwesenheit...")

    if HomeAssistantClient:
        ha = HomeAssistantClient()
        while True:
            try:
                state = await ha.get_state("device_tracker.my_iphone")
                if state and state.get("state") not in ["home", "zuhause"]:
                    logger.info("iPhone ist 'away'. Beginne mit der Überwachung.")
                    break
                logger.info("iPhone ist noch 'home'. Warte 60 Sekunden...")
            except Exception as e:
                logger.warning(f"Konnte iPhone State nicht abfragen: {e}. Überspringe Wait-Loop.")
                break
            await asyncio.sleep(60)

    logger.info("Überwachung aktiv (Alle 5 Minuten Scan)...")

    while True:
        with HeadlessVisionBridge():
            logger.info("Lasse Kamera für 10 Sekunden anlaufen und sammle Vektoren...")
            await asyncio.sleep(10) # Warte, bis Playwright geladen hat und Sensor sendet

            state = fetch_latest_state()
            if not state:
                logger.warning("Keine Daten vom Sensor erhalten.")
            else:
                objects = [obj.get("class", "").lower() for obj in state.get("objects", [])]
                if "person" in objects:
                    logger.info("Person im Bild entdeckt! Validierung erfolgreich.")
                    await trigger_tts("Achtung. Visuelle Bestätigung. Du bist zurückgekehrt.")

                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"\n### AWAY-Test Event | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Person detektiert. Test erfolgreich beendet.\n---\n")

                    break
                else:
                    logger.info("Keine Person entdeckt. Raum ist leer.")

        logger.info("Warte 5 Minuten bis zum nächsten Scan...")
        await asyncio.sleep(300)

async def mode_baseline(duration: int, note: str):
    """
    Baseline-Modus (Takt 0):
    Sammelt über `duration` Sekunden lang die Sensor-Daten und bildet einen Durchschnitt.
    """
    logger.info(f"Starte BASELINE-Aufzeichnung für {duration} Sekunden. (Notiz: '{note}')")
    logger.info("Bitte arbeite ganz normal weiter. Sammle Vektoren...")

    samples = []
    start_time = time.time()

    with HeadlessVisionBridge():
        logger.info("Warte 10 Sekunden auf Kamera-Init (Headless)...")
        await asyncio.sleep(10)

        # Zeit-Reset nach dem Init
        start_time = time.time()
        while time.time() - start_time < duration:
            state = fetch_latest_state()
            if state and "blendshapes" in state:
                samples.append(state)
            await asyncio.sleep(2) # Alle 2 Sekunden ein Sample

    if not samples:
        logger.error("Keine Sensor-Daten empfangen. Gab es ein Berechtigungsproblem in Playwright?")
        return

    # Durchschnittsberechnung
    avg_blendshapes = {}
    blink_rates = []

    for s in samples:
        bs = s.get("blendshapes", {})
        for k, v in bs.items():
            avg_blendshapes[k] = avg_blendshapes.get(k, 0) + v
        blink_rates.append(s.get("blinkCount", 0))

    sample_count = len(samples)
    for k in avg_blendshapes:
        avg_blendshapes[k] /= sample_count

    total_blinks = max(blink_rates) - min(blink_rates) if blink_rates else 0
    blinks_per_minute = (total_blinks / (duration / 60.0)) if duration > 0 else 0

    profile = {
        "timestamp": datetime.now().isoformat(),
        "note": note,
        "duration_seconds": duration,
        "sample_count": sample_count,
        "blinks_per_minute": round(blinks_per_minute, 2),
        "avg_blendshapes": {k: round(v, 4) for k, v in avg_blendshapes.items() if v > 0.05}
    }

    baselines = []
    if BASELINE_FILE.exists():
        try:
            with open(BASELINE_FILE, "r", encoding="utf-8") as f:
                baselines = json.load(f)
        except json.JSONDecodeError:
            pass

    baselines.append(profile)

    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(baselines, f, indent=2, ensure_ascii=False)

    logger.info("=== BASELINE ERFASST ===")
    logger.info(f"Blinks pro Minute: {blinks_per_minute:.2f}")
    logger.info(f"Top Blendshapes: {profile['avg_blendshapes']}")
    logger.info(f"Gespeichert in {BASELINE_FILE.name}")

    await trigger_tts("Baseline Aufzeichnung abgeschlossen. Referenzmuster gespeichert.")

async def main():
    parser = argparse.ArgumentParser(description="OMEGA Vision Empiric Test Loop")
    parser.add_argument("--mode", choices=["away", "baseline"], required=True, help="Testmodus")
    parser.add_argument("--duration", type=int, default=300, help="Dauer für Baseline in Sekunden (default: 300)")
    parser.add_argument("--note", type=str, default="Unspezifiziert", help="Zustands-Notiz für Baseline (z.B. 'morgens, tiefer fokus')")
    args = parser.parse_args()

    if not LOG_FILE.exists():
        LOG_FILE.write_text("# ATLAS Vision Test-Protokoll\n\n", encoding="utf-8")

    if args.mode == "away":
        await mode_away()
    elif args.mode == "baseline":
        await mode_baseline(args.duration, args.note)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test durch Operator abgebrochen.")
