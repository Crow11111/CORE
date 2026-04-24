#!/bin/bash
# OMEGA Plasmoid Installer
# Installiert den Deep Research Plasmoiden für KDE Plasma.

PLASMOID_NAME="org.omega.deepresearch"
SOURCE_DIR="/OMEGA_CORE/tools/plasmoid_omega_research"
INSTALL_DIR="$HOME/.local/share/plasma/plasmoids/$PLASMOID_NAME"

echo "Initialisiere Installation von OMEGA Deep Research Plasmoid..."

# Verzeichnis erstellen falls nicht vorhanden
mkdir -p "$HOME/.local/share/plasma/plasmoids/"

# Alten Stand entfernen falls vorhanden
if [ -d "$INSTALL_DIR" ]; then
    echo "Entferne alte Version..."
    rm -rf "$INSTALL_DIR"
fi

# Kopieren der Dateien
cp -r "$SOURCE_DIR" "$INSTALL_DIR"

echo "Installation abgeschlossen."
echo "Du kannst den Plasmoiden nun über dein KDE Desktop-Menü hinzufügen (Rechtsklick auf Desktop > Miniprogramm hinzufügen > 'OMEGA Deep Research')."
echo "Falls er nicht erscheint, lade Plasma neu: 'plasmashell --replace &'"
