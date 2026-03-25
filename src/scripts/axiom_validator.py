import hashlib
import json
from pathlib import Path
import datetime

# Kanonische Pfade zu den Axiom-Dateien
# Diese müssen absolut und unveränderlich sein.
CORE_ROOT = Path(__file__).parent.parent.parent.resolve()
AXIOM_FILES = [
    CORE_ROOT / ".cursorrules",
    CORE_ROOT / "CORE_EICHUNG.md", # Korrigierter Pfad
    CORE_ROOT / "AGENTS.md",
    CORE_ROOT / ".cursor/rules/0_BOOTLOADER.mdc"
]

# Speicherort für den bekannten "guten" Hash und den aktuellen Status
# Ein lokales Verzeichnis im Projekt-Root, um Berechtigungsprobleme zu vermeiden.
STATUS_DIR = CORE_ROOT / ".state"
KNOWN_GOOD_HASH_FILE = CORE_ROOT / "docs/00_STAMMDOKUMENTE/axiom_hash.sha256"
CURRENT_STATUS_FILE = STATUS_DIR / "axiom_status.json"

def calculate_combined_hash(files: list[Path]) -> str:
    """Liest eine Liste von Dateien ein und berechnet einen einzelnen SHA256-Hash über deren kombinierten Inhalt."""
    hasher = hashlib.sha256()

    for file_path in sorted(files, key=lambda p: str(p)): # Sortieren für deterministische Reihenfolge
        if not file_path.is_file():
            raise FileNotFoundError(f"Axiom-Datei nicht gefunden: {file_path}")

        # Lese im Binärmodus, um Encoding-Probleme zu vermeiden
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

    return hasher.hexdigest()

def update_known_good_hash(new_hash: str):
    """Aktualisiert den bekannten 'guten' Hash. Sollte nur nach bewusster Änderung der Axiome aufgerufen werden."""
    print(f"Aktualisiere bekannten guten Hash auf: {new_hash}")
    with open(KNOWN_GOOD_HASH_FILE, "w") as f:
        f.write(new_hash)

def main():
    """Hauptfunktion des Validators."""
    STATUS_DIR.mkdir(exist_ok=True)

    status_data = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "status": "FAIL",
        "current_hash": None,
        "known_good_hash": None,
        "checked_files": [str(p) for p in AXIOM_FILES]
    }

    try:
        current_hash = calculate_combined_hash(AXIOM_FILES)
        status_data["current_hash"] = current_hash

        if not KNOWN_GOOD_HASH_FILE.is_file():
            # Wenn kein bekannter Hash existiert, erstellen wir den ersten.
            # Dies ist ein einmaliger Initialisierungsschritt.
            print("Kein bekannter guter Hash gefunden. Initialisiere mit aktuellem Hash.")
            update_known_good_hash(current_hash)
            status_data["known_good_hash"] = current_hash
            status_data["status"] = "PASS"
        else:
            with open(KNOWN_GOOD_HASH_FILE, "r") as f:
                known_good_hash = f.read().strip()
                status_data["known_good_hash"] = known_good_hash

            if current_hash == known_good_hash:
                status_data["status"] = "PASS"
            else:
                status_data["status"] = "FAIL"
                print(f"ALARM: Axiom-Integritätsprüfung fehlgeschlagen!")
                print(f"  Erwarteter Hash: {known_good_hash}")
                print(f"  Aktueller Hash:  {current_hash}")

    except FileNotFoundError as e:
        print(f"FEHLER: Eine Axiom-Datei konnte nicht gefunden werden: {e}")
        status_data["status"] = "FAIL_FILE_NOT_FOUND"
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        status_data["status"] = "FAIL_UNEXPECTED_ERROR"

    finally:
        # Schreibe den finalen Status, egal was passiert.
        with open(CURRENT_STATUS_FILE, "w") as f:
            json.dump(status_data, f, indent=2)

        print(f"Statusprüfung abgeschlossen. Ergebnis: {status_data['status']}. Status geschrieben nach {CURRENT_STATUS_FILE}")

if __name__ == "__main__":
    # Wenn das Skript mit dem Argument "update" aufgerufen wird, wird der bekannte gute Hash aktualisiert.
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        try:
            current_hash = calculate_combined_hash(AXIOM_FILES)
            update_known_good_hash(current_hash)
            print("Bekannter guter Hash wurde erfolgreich aktualisiert.")
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Hashes: {e}")
    else:
        main()

