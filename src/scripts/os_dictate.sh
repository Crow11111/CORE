#!/bin/bash
# CORE Headless Dictation Toggle Script
# Klick 1: Startet die Aufnahme lautlos
# Klick 2: Beendet die Aufnahme lautlos, kopiert ins Clipboard

PID_FILE="/tmp/core_dictate.pid"
AUDIO_FILE="/tmp/core_dictate.wav"

if [ -f "$PID_FILE" ]; then
    # Aufnahme beenden
    REC_PID=$(cat "$PID_FILE")
    if ps -p $REC_PID > /dev/null; then
        kill $REC_PID
    fi
    rm "$PID_FILE"
    
    # An das lokale Backend senden
    RESPONSE=$(curl -s -X POST -F "audio=@$AUDIO_FILE" http://localhost:8000/api/dictate)
    
    # Zeige das Ergebnis als Notification und ab ins Clipboard (Wayland kompatibel via wl-copy)
    TEXT=$(echo $RESPONSE | grep -oP '(?<="text":")[^"]*')
    if [ ! -z "$TEXT" ]; then
        # In die Zwischenablage kopieren (wl-copy für Wayland)
        echo "$TEXT" | wl-copy
    fi
else
    # Aufnahme starten
    rm -f "$AUDIO_FILE"
    
    # pw-record für Pipewire (KDE Standard)
    pw-record --channels=1 --rate=16000 --format=s16 "$AUDIO_FILE" > /dev/null 2>&1 &
    echo $! > "$PID_FILE"
fi
