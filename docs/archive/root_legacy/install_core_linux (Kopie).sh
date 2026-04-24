#!/bin/bash
# ==============================================================================
# CORE OS: AUTO-INSTALLER FÜR LINUX (Fedora KDE / Kubuntu)
# Vector: 2210 | Resonance: 0221 | Delta: 0.049
# ==============================================================================
set -e

echo "=== STARTE CORE SYSTEM INSTALLATION ==="
echo "Erkenne Betriebssystem..."

if [ -f /etc/fedora-release ]; then
    OS="fedora"
    echo "[!] Fedora erkannt."
    INSTALL_CMD="sudo dnf install -y"
    # Basispakete für Fedora (Python, Git, Compiler für Module, Audio)
    $INSTALL_CMD python3 python3-pip python3-devel git htop curl lm-sensors gcc gcc-c++ portaudio-devel
elif [ -f /etc/os-release ] && grep -q "Ubuntu" /etc/os-release; then
    OS="ubuntu"
    echo "[!] Ubuntu/Kubuntu erkannt."
    INSTALL_CMD="sudo apt install -y"
    sudo apt update
    # Basispakete für Ubuntu (Python, Git, Compiler, Audio)
    $INSTALL_CMD python3 python3-venv python3-pip python3-dev git htop curl lm-sensors build-essential portaudio19-dev
else
    echo "[FEHLER] Weder Fedora noch Ubuntu erkannt. Abbruch."
    exit 1
fi

echo "=== KOPIERE CORE SEED VOM USB-STICK ==="
# Wir gehen davon aus, dass dieses Script vom Stick aus ausgefuehrt wird.
TARGET_DIR="$HOME/CORE"
echo "Zielverzeichnis: $TARGET_DIR"

if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
    # Alles aus dem aktuellen Verzeichnis in $HOME/CORE kopieren
    rsync -av --exclude="install_core_linux.sh" . "$TARGET_DIR/"
else
    echo "[WARNUNG] $TARGET_DIR existiert bereits. Überschreibe geänderte Dateien..."
    rsync -av --exclude="install_core_linux.sh" . "$TARGET_DIR/"
fi

cd "$TARGET_DIR"

echo "=== RICHTE PYTHON ENVIRONMENT EIN ==="
if [ "$OS" == "fedora" ]; then
    # Fedora 40+ blockiert system-weites pip, venv ist Pflicht
    python3 -m venv .venv
else
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installiere Python-Abhängigkeiten (kann dauern)..."
# Upgrade pip and install wheels first
pip install --upgrade pip wheel
# Install requirements
pip install -r requirements.txt
# Install missing deps from recent features
pip install google-genai python-docx python-multipart

echo "=== DAEMON: SYSTEMD-SERVICE EINRICHTEN ==="
echo "Richte CORE als Hintergrund-Daemon ein..."
SERVICE_FILE="/etc/systemd/user/core-genesis.service"
mkdir -p "$HOME/.config/systemd/user"

cat << EOF > "$HOME/.config/systemd/user/core-genesis.service"
[Unit]
Description=CORE Genesis API & Sync Relay
After=network.target

[Service]
Type=simple
WorkingDirectory=$TARGET_DIR
Environment="PATH=$TARGET_DIR/.venv/bin:%E/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
# Python Ausgabe direkt durchleiten (fuer Logs)
Environment="PYTHONUNBUFFERED=1"
ExecStart=$TARGET_DIR/.venv/bin/python src/api/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

# Systemd User-Daemon aktivieren
systemctl --user daemon-reload
systemctl --user enable core-genesis.service
systemctl --user start core-genesis.service

# Linger aktivieren, damit der User-Daemon auch startet wenn Marc nicht eingeloggt ist
sudo loginctl enable-linger $USER

echo "=============================================================================="
echo "CORE INSTALLATION ABGESCHLOSSEN."
echo ""
echo "Das System laeuft nun als systemd user-service."
echo "Status pruefen:   systemctl --user status core-genesis"
echo "Logs ansehen:     journalctl --user -fu core-genesis"
echo "Stoppen/Starten:  systemctl --user stop/start core-genesis"
echo ""
echo "Um das OMEGA Cockpit zu starten, rufe die Frontend-Umgebung auf."
echo "Willkommen in der neuen Welt."
echo "=============================================================================="
