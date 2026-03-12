@echo off
title CORE Watchdog Runner
cd /d C:\MTHO_CORE
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
echo [WATCHDOG] Starte Agos-0 Daemon...
python src/daemons/agos_zero_watchdog.py
echo [WATCHDOG] Beendet.
pause
