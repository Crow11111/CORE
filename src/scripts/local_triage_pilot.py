import os
import subprocess
import json
import requests

def query_local_ollama(prompt, model="gemma4:e4b"):
    """Fragt die lokale Ollama-Instanz ab."""
    try:
        response = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return response.stdout.strip()
    except Exception as e:
        return f"Fehler bei Ollama: {str(e)}"

def triage_message(message_text):
    """Klassifiziert die Nachricht lokal."""
    triage_prompt = f"""
    Analysiere die folgende Nachricht für das OMEGA-System.
    Kategorisiere sie in EINE der folgenden Klassen:
    - SYSTEM_PING: Einfache Funktionsprüfung (z.B. "Ping", "@OC Ping")
    - TASK: Ein konkreter Arbeitsauftrag
    - CHAT: Allgemeine Konversation
    - VETO: Sicherheitskritische Anweisung oder Abbruch

    Antworte NUR mit dem Klassennamen.
    Nachricht: "{message_text}"
    """
    return query_local_ollama(triage_prompt)

if __name__ == "__main__":
    test_msg = "@OC Ping"
    print(f"Test-Nachricht: {test_msg}")
    print(f"Lokale Triage-Entscheidung: {triage_message(test_msg)}")
