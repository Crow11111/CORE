#!/bin/sh
# Verschiebt störende **User-Kopien** von Plasmoids nach .bak — Plasma nutzt dann die System-Version
# unter /usr (dein installiertes ATLAS Ω Voice). Sicher: nichts löschen, nur umbenennen.
#
# Betroffen:
#   Plasma.Flex.Hub      — oft kaputt unter Plasma 6 (Terminal-Spam)
#   org.kde.plasma.jarvis — alte lokale Kopie überschreibt die frische /usr-Installation

set -e
TS=$(date +%Y%m%d-%H%M%S)
BASE="${XDG_DATA_HOME:-$HOME/.local/share}/plasma/plasmoids"

for d in Plasma.Flex.Hub org.kde.plasma.jarvis; do
    if [ -d "$BASE/$d" ]; then
        DEST="$BASE/${d}.bak-OMEGA-$TS"
        mv "$BASE/$d" "$DEST"
        echo "ATLAS: Ausgelagert → $DEST"
    else
        echo "ATLAS: Nichts zu tun (fehlt): $BASE/$d"
    fi
done

echo "ATLAS: Danach einmal: plasmashell --replace   (oder neu einloggen)."
