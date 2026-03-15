"""
CORE Gemini Diktier-Tool: Mikro -> Gemini STT -> Zwischenablage.

Nimmt Audio auf (Razer Seiren), schickt es an Gemini zur Transkription
mit CORE-Glossar als Kontext, und legt das Ergebnis in die Zwischenablage.

Steuerung:
  - Leertaste: Aufnahme starten/stoppen
  - Enter: Aufnahme stoppen + transkribieren
  - Ctrl+C / q: Beenden

Usage:
  python -m src.voice.gemini_dictate
"""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

import base64
import io
import json
import time
import wave
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"

MIC_DEVICE = None
for d in sd.query_devices():
    if "razer seiren" in d["name"].lower() and d["max_input_channels"] > 0:
        MIC_DEVICE = d["index"]
        break

CORE_GLOSSARY = (
    "CORE-Fachbegriffe die korrekt geschrieben werden MUESSEN:\n"
    "- CORE (das System, IMMER Grossbuchstaben)\n"
    "- Atlas (der Hauptknoten / Dreadnought PC)\n"
    "- Dreadnought (der PC / Windows-Rechner)\n"
    "- Scout (Raspberry Pi 5 mit Home Assistant)\n"
    "- OpenClaw (Messenger-Gateway auf VPS)\n"
    "- ChromaDB (Vektor-Datenbank)\n"
    "- pgvector (PostgreSQL Vektor-Extension)\n"
    "- Ollama (lokales LLM-Framework)\n"
    "- Tesserakt (4D-Wuerfel, CORE-Architektur-Topologie)\n"
    "- Gravitator (Embedding-basiertes Collection-Routing)\n"
    "- Apoptose (programmierter Zelltod / System-Reinigung)\n"
    "- Apotheose (Vergottung / Transformation)\n"
    "- Isomorphie (Strukturgleichheit zwischen Domaenen)\n"
    "- Symmetriebruch (0.49/0.51, NICHT 0.5)\n"
    "- baryonisch / baryonisches Delta (0.049, kosmologische Konstante)\n"
    "- Entropie (Unordnung / Informationsmass)\n"
    "- Fibonacci / Phi / Goldener Schnitt (0.618)\n"
    "- Embedding / Embeddings (Vektorrepraesentation von Text)\n"
    "- Multi-View-Embedding (6-Linsen-Architektur)\n"
    "- Konvergenz / Konvergenz-Score (Cross-Domain-Aehnlichkeit)\n"
    "- Neurodivergent / ND / AUDHD\n"
    "- CAR/CDR (Lisp-Paarung: Kern/Interface)\n"
    "- Cons-Zelle (Lisp-Datenstruktur)\n"
    "- Fallback (Rueckfall-Strategie, NICHT 'Vorllack')\n"
    "- Pipeline (Verarbeitungskette)\n"
    "- Dispatcher (Verteiler)\n"
    "- MCP (Model Context Protocol)\n"
    "- VPS (Virtual Private Server, Hostinger)\n"
    "- SSH (Secure Shell)\n"
    "- TTS (Text-to-Speech)\n"
    "- STT (Speech-to-Text)\n"
    "- RAG (Retrieval-Augmented Generation)\n"
    "- LLM (Large Language Model)\n"
    "- Gemini (Google AI Modell)\n"
    "- Piper (lokales TTS-System)\n"
    "- Whisper (OpenAI STT-Modell)\n"
    "- ElevenLabs (TTS-Dienst)\n"
    "- Home Assistant / HA (Smart-Home-Plattform)\n"
    "- Docker (Container-Plattform)\n"
    "- Cursor (IDE / Code-Editor)\n"
    "- Strang (Arbeits-Thread im CORE-Plan)\n"
    "- Osmium (CORE-Orchestrierungs-Framework)\n"
    "- Ring-0 (hoechste Sicherheitsstufe)\n"
    "- Hatamoto (Waechter-Rolle)\n"
    "- CrystalGridEngine (Topologische Logik-Engine)\n"
    "- nomic-embed-text (Ollama Embedding-Modell)\n"
    "- qwen2.5 (Ollama LLM auf VPS)\n"
    "- llama3 / llama3.1 (Meta LLM lokal)\n"
)

SYSTEM_PROMPT = (
    "Du bist ein praeziser Transkriptions-Assistent fuer CORE. "
    "Der Sprecher ist Marc, deutsch, neurodivergent (AUDHD), denkt assoziativ und schnell. "
    "Er diktiert technische Inhalte -- oft gemischt mit persoenlichen Gedanken.\n\n"
    "REGELN:\n"
    "1. Transkribiere woertlich und vollstaendig. Keine Zusammenfassungen.\n"
    "2. Nutze das CORE-Glossar fuer korrekte Schreibweise aller Fachbegriffe.\n"
    "3. Wenn Marc undeutlich spricht, nutze den Kontext um das wahrscheinlichste Wort zu waehlen.\n"
    "4. Behalte Absaetze bei natuerlichen Sprechpausen.\n"
    "5. Kennzeichne unverstaendliche Stellen mit [unverstaendlich].\n"
    "6. Gib NUR die Transkription aus, keine Metakommentare.\n\n"
    f"{CORE_GLOSSARY}"
)


class GeminiDictation:
    def __init__(self):
        self.recording = False
        self.audio_buffer = []
        self.stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if self.recording:
            self.audio_buffer.append(indata.copy())

    def start_recording(self):
        self.audio_buffer = []
        self.recording = True
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            device=MIC_DEVICE,
            callback=self._audio_callback,
            blocksize=int(SAMPLE_RATE * 0.1),
        )
        self.stream.start()
        print("[REC] Aufnahme laeuft... (Enter zum Stoppen)")

    def stop_recording(self) -> bytes:
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_buffer:
            return b""

        audio = np.concatenate(self.audio_buffer)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        return buf.getvalue()

    def transcribe(self, wav_bytes: bytes) -> str:
        import requests

        b64_data = base64.b64encode(wav_bytes).decode("utf-8")
        size_kb = len(wav_bytes) / 1024

        url = f"{BASE_URL}/{MODEL}:generateContent?key={API_KEY}"
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "audio/wav",
                            "data": b64_data,
                        }
                    },
                    {"text": "Transkribiere dieses Audio. Nutze das CORE-Glossar."},
                ]
            }],
        }

        print(f"[API] Sende {size_kb:.0f} KB an Gemini ({MODEL})...")
        resp = requests.post(url, json=payload, timeout=120)

        if resp.status_code != 200:
            print(f"[FEHLER] HTTP {resp.status_code}: {resp.text[:300]}")
            return ""

        data = resp.json()
        if "candidates" not in data or not data["candidates"]:
            print(f"[FEHLER] Keine Candidates: {json.dumps(data, indent=2)[:300]}")
            return ""

        parts = data["candidates"][0].get("content", {}).get("parts", [])
        text = "\n".join(p.get("text", "") for p in parts if "text" in p)
        return text.strip()

    def to_clipboard(self, text: str):
        import subprocess
        process = subprocess.Popen(
            ["powershell", "-Command", "-"],
            stdin=subprocess.PIPE,
        )
        ps_script = f'Set-Clipboard -Value "{text.replace(chr(34), chr(96)+chr(34))}"'
        process.communicate(input=ps_script.encode("utf-8"))


def main():
    if not API_KEY:
        print("FEHLER: GEMINI_API_KEY nicht gesetzt.")
        sys.exit(1)

    mic_name = "Default"
    if MIC_DEVICE is not None:
        mic_name = sd.query_devices(MIC_DEVICE)["name"]
    print(f"=== CORE Gemini Diktier-Tool ===")
    print(f"Mikrofon: {mic_name}")
    print(f"Modell: {MODEL}")
    print(f"Glossar: {len(CORE_GLOSSARY.splitlines())} Eintraege")
    print(f"")
    print(f"Steuerung:")
    print(f"  Enter     = Aufnahme starten")
    print(f"  Enter     = Aufnahme stoppen + transkribieren")
    print(f"  q + Enter = Beenden")
    print(f"{'='*40}")

    dictation = GeminiDictation()

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd in ("q", "quit", "exit"):
                print("Beende.")
                break

            if not dictation.recording:
                dictation.start_recording()
            else:
                print("[STOP] Aufnahme beendet.")
                wav_data = dictation.stop_recording()

                if not wav_data:
                    print("[WARN] Keine Audio-Daten.")
                    continue

                duration = len(wav_data) / (SAMPLE_RATE * 2)
                print(f"[INFO] {duration:.1f}s Audio aufgenommen.")

                text = dictation.transcribe(wav_data)
                if text:
                    print(f"\n--- Transkription ---")
                    print(text)
                    print(f"--- Ende ({len(text)} Zeichen) ---")

                    dictation.to_clipboard(text)
                    print(f"[OK] In Zwischenablage kopiert. Ctrl+V zum Einfuegen.")
                else:
                    print("[WARN] Leere Transkription.")

        except KeyboardInterrupt:
            print("\nBeende.")
            if dictation.recording:
                dictation.stop_recording()
            break
        except Exception as e:
            print(f"[FEHLER] {e}")


if __name__ == "__main__":
    main()
