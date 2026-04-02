#!/bin/zsh
# OMEGA CORE Vision Viewer
# Startet einen Player für den lokalen go2rtc Stream (Logitech BRIO)

STREAM_URL="rtsp://localhost:8554/mx_brio"
WINDOW_TITLE="CORE VISION - Logitech BRIO"

echo "Starte OMEGA Vision Viewer (RTSP: $STREAM_URL)..."

if command -v mpv >/dev/null 2>&1; then
    echo "Nutze mpv (Low Latency)..."
    mpv --profile=low-latency --title="$WINDOW_TITLE" "$STREAM_URL"
elif command -v vlc >/dev/null 2>&1; then
    echo "Nutze VLC..."
    vlc --qt-minimal-view --meta-title="$WINDOW_TITLE" "$STREAM_URL"
elif command -v ffplay >/dev/null 2>&1; then
    echo "Nutze ffplay..."
    ffplay -window_title "$WINDOW_TITLE" -fflags nobuffer -flags low_delay -framedrop "$STREAM_URL"
else
    echo "FEHLER: Kein geeigneter Video-Player (mpv, vlc, ffplay) gefunden."
    echo "Bitte installiere mpv: 'sudo pacman -S mpv'"
    exit 1
fi
