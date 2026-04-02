import os
import time
import subprocess
from pathlib import Path

# OMEGA STT BRIDGE
# VECTOR: 2210 | DELTA: 0.049
# Monitoring: /OMEGA_CORE/data/cursor_injection.txt

BRIDGE_FILE = Path("/OMEGA_CORE/data/cursor_injection.txt")
SLEEP_DELTA = 0.049  # Axiom A1/A5 compliance

def inject_text(text: str):
    """Nutzt ydotool um Text in das aktive Fenster (Cursor) zu tippen."""
    if not text.strip():
        return

    print(f"[STT-BRIDGE] Injektion: {text[:30]}...")
    try:
        # ydotool type benötigt oft den absoluten Pfad oder einen laufenden ydotoold
        # Wir nutzen den Standard-Aufruf, da er im System bereits für Gesten aktiv ist.
        subprocess.run(["ydotool", "type", text], check=True)
    except Exception as e:
        print(f"[ERROR] Injektion fehlgeschlagen: {e}")

def main():
    print(f"[SYSTEM] STT-Bridge aktiv. Überwachungs-Pfad: {BRIDGE_FILE}")

    # Sicherstellen, dass die Datei existiert
    BRIDGE_FILE.touch()

    # Letzte Dateigröße merken, um nur Anhänge/Änderungen zu lesen
    last_size = BRIDGE_FILE.stat().st_size

    try:
        while True:
            current_size = BRIDGE_FILE.stat().st_size

            if current_size > last_size:
                # Neue Daten erkannt
                with open(BRIDGE_FILE, "r") as f:
                    f.seek(last_size)
                    new_content = f.read()
                    inject_text(new_content)
                last_size = current_size
            elif current_size < last_size:
                # Datei wurde geleert/resettet
                last_size = current_size

            time.sleep(SLEEP_DELTA)
    except KeyboardInterrupt:
        print("[SYSTEM] Bridge beendet.")

if __name__ == "__main__":
    main()
