@echo off
chcp 65001 >nul
title MTHO OMEGA COCKPIT - MASTER CONTROL
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo ============================================================
echo MTHO-GENESIS: OMEGA COCKPIT STARTUP
echo ============================================================
echo.

REM --- CLEANUP: Nur MTHO-Prozesse beenden (Port-basiert) ---
echo Bereinige alte MTHO-Prozesse...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Bereinigung abgeschlossen.
echo.

REM --- 1. API SERVER (minimiert) ---
echo Starte API Server Port 8000
start /min "MTHO API" cmd /c "set PYTHONIOENCODING=utf-8 & python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"

REM --- 2. WATCHDOG (minimiert) ---
echo Starte Agos-0 Watchdog
start /min "MTHO WATCHDOG" cmd /c "set PYTHONIOENCODING=utf-8 & python src/daemons/agos_zero_watchdog.py"

REM --- 3. FRONTEND (minimiert) ---
echo Starte Frontend Dev Server Port 3000
start /min "MTHO FRONTEND" cmd /c "cd frontend & npm run dev"

REM --- Health-Check: Warte bis API antwortet ---
echo Warte auf API...
set RETRIES=0
:healthloop
curl -s -o nul -w "" http://localhost:8000/status >nul 2>&1
if %ERRORLEVEL%==0 (
    echo API bereit.
    goto :apiready
)
set /a RETRIES+=1
if %RETRIES% GEQ 30 (
    echo WARNUNG: API nach 30 Versuchen nicht erreichbar.
    goto :apiready
)
timeout /t 2 /nobreak >nul
goto :healthloop
:apiready

echo.
echo Oeffne Frontend...
start "" "http://localhost:3000"

echo.
echo ============================================================
echo OMEGA Cockpit initialisiert.
echo   API:      http://localhost:8000 (minimiert)
echo   Frontend: http://localhost:3000 (Browser)
echo   Watchdog: Hintergrund (Telemetrie via API)
echo ============================================================
echo.
pause
goto :eof
