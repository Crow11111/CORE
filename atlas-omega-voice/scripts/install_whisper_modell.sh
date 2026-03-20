#!/bin/sh
# ATLAS Ω Voice — lädt das kleine Whisper-Modell für Wake-Wort (offline, CPU).
# Voraussetzung: curl. Danach Plasma neu starten: plasmashell --replace

set -e
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/jarvis"
URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin"
OUT="$DEST/ggml-tiny.bin"

echo "ATLAS: Ordner anlegen: $DEST"
mkdir -p "$DEST"

if ! command -v curl >/dev/null 2>&1; then
    echo "FEHLER: curl ist nicht installiert. Auf Arch: sudo pacman -S curl" >&2
    exit 1
fi

echo "ATLAS: Lade Sprachmodell (ca. 75 MB) …"
curl -fL --progress-bar -o "$OUT.part" "$URL"
mv -f "$OUT.part" "$OUT"

echo "Fertig: $OUT"
echo "Als Nächstes: plasmashell --replace   oder neu einloggen — dann findet ATLAS die Datei."
