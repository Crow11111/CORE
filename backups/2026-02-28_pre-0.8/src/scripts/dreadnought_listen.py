import os
import sys
import wave
import json
import time
import uuid
from datetime import datetime, timezone

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def record_audio(duration: int = 7, filename: str = "voice_input.wav") -> str | None:
    """Versucht Audio aufzunehmen. Fallback auf Dummy wenn Hardware fehlt."""
    try:
        import sounddevice as sd
        import numpy as np
        
        fs = 44100  # Sample rate
        log(f"Starte Aufnahme ({duration}s)...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        log("Aufnahme beendet.")
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())
        return os.path.abspath(filename)
    except Exception as e:
        log(f"Hardware/Treiber Fehler: {e}. Nutze Dummy-Audio.")
        # Erstelle eine leere/Dummy WAV Datei
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b'\x00' * 1000)
        return os.path.abspath(filename)

def send_event(audio_path: str):
    """Sendet Event an OpenClaw Brain."""
    try:
        from src.network.openclaw_client import send_event_to_oc_brain, is_configured
        
        event = {
            "source": "dreadnought",
            "node_id": "local-mic",
            "event_type": "voice_input",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "priority": "high",
            "data": {
                "audio_path": audio_path,
                "text_fallback": "Axiom: ATLAS hört (Test-Input)."
            }
        }
        
        if not is_configured():
            log("[FAIL] OpenClaw Client nicht konfiguriert.")
            return False
            
        success, response = send_event_to_oc_brain(event)
        if success:
            log(f"[SUCCESS] Event gesendet. Response: {response}")
            return True
        else:
            log(f"[FAIL] Senden fehlgeschlagen: {response}")
            return False
    except Exception as e:
        log(f"[FAIL] Interner Fehler: {e}")
        return False

if __name__ == "__main__":
    # Pfad-Fix für Ausführung aus Root
    sys.path.append(os.getcwd())
    
    audio_file = f"media/voice_input_{int(time.time())}.wav"
    os.makedirs("media", exist_ok=True)
    
    path = record_audio(duration=5, filename=audio_file)
    if path and send_event(path):
        print("\n[SUCCESS] Recording/Event gesendet")
    else:
        print(f"\n[FAIL: Senden oder Konfiguration fehlerhaft]")
