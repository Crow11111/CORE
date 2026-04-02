#!/bin/bash
# ============================================================
# OMEGA CORE DAEMON MONITOR & AUTO-START
# Vector: 2210 | Resonance: 0221 | Delta: 0.049
# ============================================================

DAEMONS=(
    "omega-backend"
    "omega-frontend"
    "omega-chat"
    "omega-vision-ui"
    "omega-event-bus"
    "omega-vision"
    "omega-audio"
    "omega-watchdog"
)

echo "=== OMEGA CORE DAEMON CHECK ==="
echo "Pruefe Status der System-Dienste..."
echo "-----------------------------------"

for daemon in "${DAEMONS[@]}"; do
    if systemctl is-active --quiet "$daemon"; then
        echo -e "\e[32m[ONLINE]\e[0m  $daemon"
    else
        echo -e "\e[31m[OFFLINE]\e[0m $daemon -> Versuche Neustart..."

        # Versuche zuerst NOPASSWD sudo (falls eingerichtet in sudoers), sonst Fallback
        sudo -n systemctl restart "$daemon" 2>/dev/null
        if [ $? -ne 0 ]; then
            # Fallback mit Default-Passwort 'gogogo' (wie in der Umgebung definiert)
            echo "gogogo" | sudo -S systemctl restart "$daemon" >/dev/null 2>&1
        fi

        # Kurze Wartezeit, damit der Daemon anlaufen kann
        sleep 1

        if systemctl is-active --quiet "$daemon"; then
            echo -e "   \e[32m-> Erfolgreich gestartet.\e[0m"
        else
            echo -e "   \e[31m-> Fehler beim Starten! Bitte Logs pruefen:\e[0m journalctl -u $daemon -e --no-pager"
        fi
    fi
done

echo "-----------------------------------"
echo "=== CHECK ABGESCHLOSSEN ==="
