#!/bin/bash
echo "[ATLAS VERIFICATION] Starte Ring-0 Empirie-Messung..."
echo ""
echo "1. PID-Isolation und Systemd-Cgroup (Dämonen)"
ps -o pid,user,pri,ni,stat,cmd -C python | grep -E "core_event_bus|agos_zero_watchdog|core_vision_daemon"
systemctl status omega-watchdog.service | grep CGroup
echo ""
echo "2. Laufende Ports prüfen (Backend, Frontend)"
ss -tuln | grep -E ":8000|:3000"
echo ""
echo "3. Ollama Status"
systemctl is-active ollama
