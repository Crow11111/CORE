#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGA DEEP RESEARCH CLI
-----------------------
Asynchrones CLI-Tool zur Kommunikation mit dem Modell `deep-research-pro-preview-12-2025`
über die Google GenAI Interactions API.

Nutzung:
  1. Job starten:
     python src/scripts/omega_deep_research.py start "Dein komplexer Research Prompt"
     
  2. Status prüfen:
     python src/scripts/omega_deep_research.py status <job_id>
     
  3. Ergebnisse abholen:
     python src/scripts/omega_deep_research.py fetch <job_id> result.md
"""

import argparse
import asyncio
import json
import os
import sys
import warnings
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Warnung zur experimentellen Nutzung der Interactions API abfangen/ignorieren
warnings.filterwarnings("ignore", message=".*Interactions usage is experimental.*")
warnings.filterwarnings("ignore", message=".*Async interactions client cannot use aiohttp.*")

STATE_DIR = Path(".state")
STATE_FILE = STATE_DIR / "deep_research_jobs.json"
AGENT_MODEL = "deep-research-pro-preview-12-2025"

def load_jobs() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_job(job_id: str, prompt: str):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    jobs = load_jobs()
    jobs[job_id] = {"prompt": prompt, "status": "started"}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)

def get_client() -> genai.Client:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("FEHLER: GEMINI_API_KEY Umgebungsvariable ist nicht in .env gesetzt.")
        sys.exit(1)
    return genai.Client(api_key=api_key)

async def cmd_start(prompt: str, watch: bool = False, output_file: str = "docs/05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT.md"):
    client = get_client()
    print(f"Starte Deep Research Job mit Modell {AGENT_MODEL}...")
    try:
        # Asynchroner Aufruf (falls das SDK aio unterstützt), ansonsten Auslagerung in Thread
        if hasattr(client, "aio") and hasattr(client.aio, "interactions"):
            response = await client.aio.interactions.create(
                agent=AGENT_MODEL,
                input={"type": "text", "text": prompt},
                background=True
            )
        else:
            response = await asyncio.to_thread(
                client.interactions.create,
                agent=AGENT_MODEL,
                input={"type": "text", "text": prompt},
                background=True
            )
            
        # Typ-sichere Extraktion der ID (berücksichtigt Objekt- und Dict-Rückgaben)
        job_id = getattr(response, "name", None) or getattr(response, "id", None)
        if not job_id and isinstance(response, dict):
            job_id = response.get("name") or response.get("id")
            
        if not job_id:
            print(f"Konnte Job-ID nicht aus der Antwort ermitteln. Rohe Antwort: {response}")
            sys.exit(1)
            
        save_job(str(job_id), prompt)
        print("ERFOLG: Job asynchron gestartet.")
        print(f"Job ID: {job_id}")
        
        if watch:
            print(f"Starte Hintergrund-Daemon zur Überwachung (Output: {output_file})...")
            # Starte den Watcher-Prozess im Hintergrund (detached)
            cmd = [
                sys.executable, 
                os.path.abspath(__file__), 
                "watch", 
                str(job_id), 
                output_file
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            print("Daemon läuft im Hintergrund. Du wirst benachrichtigt, sobald er fertig ist.")
            
    except Exception as e:
        print(f"FEHLER beim Starten des Jobs: {e}")
        sys.exit(1)

async def cmd_status(job_id: str):
    client = get_client()
    print(f"Prüfe Status für Job: {job_id}")
    try:
        if hasattr(client, "aio") and hasattr(client.aio, "interactions"):
            response = await client.aio.interactions.get(job_id)
        else:
            response = await asyncio.to_thread(client.interactions.get, job_id)
            
        status = getattr(response, "status", "UNBEKANNT")
        if isinstance(response, dict) and status == "UNBEKANNT":
            status = response.get("status", "UNBEKANNT")
            
        print(f"Aktueller Status: {status}")
        
        # Lokalen Status im State-File aktualisieren
        jobs = load_jobs()
        if job_id in jobs:
            jobs[job_id]["status"] = str(status)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=2)
                
    except Exception as e:
        print(f"FEHLER beim Abrufen des Status: {e}")
        sys.exit(1)

async def cmd_fetch(job_id: str, output_file: str):
    client = get_client()
    print(f"Hole Ergebnis für Job: {job_id}")
    try:
        if hasattr(client, "aio") and hasattr(client.aio, "interactions"):
            response = await client.aio.interactions.get(job_id)
        else:
            response = await asyncio.to_thread(client.interactions.get, job_id)
            
        status = getattr(response, "status", "UNBEKANNT")
        if isinstance(response, dict) and status == "UNBEKANNT":
            status = response.get("status", "UNBEKANNT")
            
        if status.upper() != "COMPLETED":
            print(f"Job ist noch nicht abgeschlossen. Status: {status}")
            print("Bitte warte auf 'COMPLETED', bevor du fetch aufrufst.")
            sys.exit(1)
            
        outputs = getattr(response, "outputs", None)
        if isinstance(response, dict) and outputs is None:
            outputs = response.get("outputs", [])
            
        if not outputs:
            print("Keine Outputs in der Antwort gefunden.")
            print("Rohe Antwort (Debug):", dir(response) if not isinstance(response, dict) else response)
            sys.exit(1)
            
        output_text = ""
        first_output = outputs[0]
        
        # Typsichere Extraktion des Output-Texts
        if hasattr(first_output, "text"):
            output_text = first_output.text
        elif isinstance(first_output, dict) and "text" in first_output:
            output_text = first_output["text"]
        elif hasattr(first_output, "parts") and first_output.parts and hasattr(first_output.parts[0], "text"):
            output_text = first_output.parts[0].text
        else:
            output_text = str(first_output)
            
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_text)
            
        print(f"ERFOLG: Ergebnis erfolgreich in '{output_file}' gespeichert.")
        
    except Exception as e:
        print(f"FEHLER beim Abrufen des Ergebnisses: {e}")
        sys.exit(1)

async def cmd_watch(job_id: str, output_file: str, interval: int = 60):
    client = get_client()
    print(f"Starte Watcher-Daemon für Job {job_id}. Prüfe alle {interval} Sekunden...")
    
    while True:
        try:
            if hasattr(client, "aio") and hasattr(client.aio, "interactions"):
                response = await client.aio.interactions.get(job_id)
            else:
                response = await asyncio.to_thread(client.interactions.get, job_id)
                
            status = getattr(response, "status", "UNBEKANNT")
            if isinstance(response, dict) and status == "UNBEKANNT":
                status = response.get("status", "UNBEKANNT")
                
            status_str = str(status).upper()
            
            # Status loggen
            jobs = load_jobs()
            if job_id in jobs:
                jobs[job_id]["status"] = status_str
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(jobs, f, indent=2)
                    
            if status_str in ["COMPLETED", "SUCCESS", "DONE"]:
                print("Job erfolgreich abgeschlossen! Hole Ergebnisse...")
                break
            elif status_str in ["FAILED", "ERROR"]:
                print(f"Job fehlgeschlagen mit Status: {status_str}")
                subprocess.run(["notify-send", "-u", "critical", "OMEGA Deep Research", "Der Recherche-Job ist FEHLGESCHLAGEN."])
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/dialog-error.oga"])
                sys.exit(1)
                
        except Exception as e:
            print(f"Fehler bei Status-Abfrage (ignoriere): {e}")
            
        await asyncio.sleep(interval)
        
    # Wenn abgeschlossen, Resultate holen
    await cmd_fetch(job_id, output_file)
    
    # Benachrichtigung
    subprocess.run(["notify-send", "-u", "normal", "OMEGA Deep Research", f"Der Recherche-Job ist fertig!\nErgebnis in: {output_file}\nBitte Orchestrator checken."])
    
    # Ton spielen (wenn paplay existiert, sonst aplay)
    if os.path.exists("/usr/bin/paplay") and os.path.exists("/usr/share/sounds/freedesktop/stereo/complete.oga"):
        subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"])
    else:
        print('\a') # Terminal bell fallback

async def main_async():
    parser = argparse.ArgumentParser(description="Omega Deep Research CLI (google-genai Interactions API)")
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle", required=True)
    
    # --- START ---
    start_parser = subparsers.add_parser("start", help="Startet einen neuen Deep Research Job")
    start_parser.add_argument("prompt", type=str, help="Der Research Prompt")
    start_parser.add_argument("--watch", "-w", action="store_true", help="Startet automatisch den Daemon-Watcher")
    start_parser.add_argument("--output", "-o", type=str, default="docs/05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT.md", help="Ausgabedatei (wenn Watch-Modus aktiv ist)")
    
    # --- STATUS ---
    status_parser = subparsers.add_parser("status", help="Prüft den Status eines laufenden Jobs")
    status_parser.add_argument("id", type=str, help="Die Job ID (z.B. aus dem start-Befehl)")
    
    # --- FETCH ---
    fetch_parser = subparsers.add_parser("fetch", help="Holt die Ergebnisse eines abgeschlossenen Jobs")
    fetch_parser.add_argument("id", type=str, help="Die Job ID")
    fetch_parser.add_argument("output_file", type=str, help="Zieldatei (Markdown) für das finale Ergebnis")

    # --- WATCH ---
    watch_parser = subparsers.add_parser("watch", help="Daemon: Startet den Hintergrund-Poller")
    watch_parser.add_argument("id", type=str, help="Die Job ID")
    watch_parser.add_argument("output_file", type=str, help="Zieldatei (Markdown) für das finale Ergebnis")
    watch_parser.add_argument("--interval", type=int, default=60, help="Poll-Intervall in Sekunden")
    
    args = parser.parse_args()
    
    if args.command == "start":
        await cmd_start(args.prompt, args.watch, getattr(args, "output", "docs/05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT.md"))
    elif args.command == "status":
        await cmd_status(args.id)
    elif args.command == "fetch":
        await cmd_fetch(args.id, args.output_file)
    elif args.command == "watch":
        await cmd_watch(args.id, args.output_file, args.interval)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
