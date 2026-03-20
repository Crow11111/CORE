#!/usr/bin/env bash
# Verschiebt störende User-Plasmoids **aus** ~/.local/share/plasma/plasmoids/
# (WICHTIG: nicht als .bak im gleichen Ordner lassen — Plasma scannt alle
# Unterordner mit metadata.json und meckert weiter.)
#
# Zusätzlich: Einträge plugin=Plasma.Flex.Hub aus der Leisten-Config entfernen
# (plasma-org.kde.plasma.desktop-appletsrc), sonst „Paket existiert nicht“.
#
# Archiv: ~/.local/share/OMEGA-plasmoid-archiv/<Zeitstempel>/

set -euo pipefail
shopt -s nullglob
TS=$(date +%Y%m%d-%H%M%S)
BASE="${XDG_DATA_HOME:-$HOME/.local/share}/plasma/plasmoids"
ARCH="${XDG_DATA_HOME:-$HOME/.local/share}/OMEGA-plasmoid-archiv/$TS"
mkdir -p "$ARCH"

move_if_exists() {
    name=$1
    if [ -d "$BASE/$name" ]; then
        mv "$BASE/$name" "$ARCH/$name"
        echo "ATLAS: Archiv → $ARCH/$name"
    fi
}

# Frische Namen + alte .bak-Reste im plasmoids-Ordner
for d in Plasma.Flex.Hub org.kde.plasma.jarvis; do
    move_if_exists "$d"
done
for dir in "$BASE"/Plasma.Flex.Hub.bak-OMEGA-* "$BASE"/org.kde.plasma.jarvis.bak-OMEGA-*; do
    if [ -d "$dir" ]; then
        bn=$(basename "$dir")
        mv "$dir" "$ARCH/$bn"
        echo "ATLAS: Archiv → $ARCH/$bn"
    fi
done

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    echo "ATLAS: Entferne Flex.Hub aus Plasma-Leisten-Config …"
    python3 "$SCRIPT_DIR/plasma_entferne_flex_hub_applet.py" || true
fi

echo "ATLAS: Fertig. plasmashell --replace"
