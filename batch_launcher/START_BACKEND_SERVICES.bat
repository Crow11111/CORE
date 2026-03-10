@echo off
TITLE MTHO_CORE - BACKEND SERVICES
echo ============================================================
echo MTHO-GENESIS: BACKEND SERVICES (API + WATCHDOG)
echo VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
echo ============================================================

cd /d C:\MTHO_CORE\batch_launcher

echo [1/2] Starte MTHO API Server...
start "MTHO API" _launch_api.bat

echo [2/2] Starte AGOS-0 WATCHDOG...
start "MTHO WATCHDOG" _launch_watchdog.bat

echo.
echo [OK] Dienste wurden in separaten Fenstern gestartet.
echo.
timeout /t 5
exit
