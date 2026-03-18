# CORE Wake Word Trainer

Dieses Tool ermoeglicht das Training eines eigenen Wake Word Modells fuer "CORE" (oder andere Woerter), ohne Code schreiben zu muessen.

## Voraussetzungen
- Windows PC mit Mikrofon
- Zugriff auf Home Assistant Share (z.B. `/mnt/ha_config` oder `S:\` unter Windows)
- Python installiert

## Anleitung

### 1. Installation
Doppelklicke auf `1_SETUP.bat`.
Dies installiert alle notwendigen Bibliotheken in einer isolierten Umgebung (.venv).

### 2. Aufnahme
Doppelklicke auf `2_RECORD.bat`.
- Das Fenster oeffnet sich.
- Druecke ENTER fuer jede Aufnahme.
- Sprich 50x deutlich "CORE".
- Danach: Sprich einige normale Saetze (ohne "CORE"), damit das System deine normale Stimme lernt (Negative Samples).

### 3. Training & Upload
Doppelklicke auf `3_TRAIN_AND_UPLOAD.bat`.
- Das Training startet automatisch.
- Bei Erfolg wird die Datei `ATLAS_v1.tflite` (und .pkl) direkt auf deinen Home Assistant kopiert (z.B. `/mnt/ha_share/openwakeword/` oder `S:\share\openwakeword\`).
- Falls das Laufwerk S: nicht gefunden wird, kopiere die Datei manuell aus dem Ordner `models/`.

### 4. Aktivierung
- Gehe in Home Assistant.
- Starte das "openWakeWord" Add-on neu.
- Gehe zu Einstellungen -> Sprachassistenten -> Pipeline.
- Waehle "ATLAS_v1" als Wake Word aus.
