@echo off
chcp 65001 >nul
title CORE OMEGA COCKPIT - MASTER CONTROL
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo ============================================================
echo CORE-GENESIS: OMEGA COCKPIT STARTUP
echo ============================================================
echo.

REM --- CLEANUP: Nur CORE-Prozesse beenden (Port-basiert) ---
echo Bereinige alte CORE-Prozesse...
powershell -Command "Get-NetTCPConnection -LocalPort 8000, 3000, 8049 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }" >nul 2>&1
timeout /t 2 /nobreak >nul
echo Bereinigung abgeschlossen.
echo.

REM --- 1. API SERVER (minimiert) ---
echo Starte API Server Port 8000
start /min "CORE API" cmd /c "set PYTHONIOENCODING=utf-8 & python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"

REM --- 2. WATCHDOG (minimiert) ---
echo Starte Agos-0 Watchdog
start /min "CORE WATCHDOG" cmd /c "set PYTHONIOENCODING=utf-8 & python src/daemons/agos_zero_watchdog.py"

REM --- 3. FRONTEND (minimiert) ---
echo Starte Frontend Dev Server Port 3000
start /min "CORE FRONTEND" cmd /c "cd frontend & npm run dev"

REM --- 4. GEMINI DICTATE (eigenes Fenster) ---
echo Starte Gemini Diktiertool
start "CORE DICTATE" cmd /c "set PYTHONIOENCODING=utf-8 & python -m src.voice.gemini_dictate"

REM --- Health-Check: Warte bis API antwortet ---
echo.
echo Warte auf API (Backend-Health-Check)...
set RETRIES=0
:healthloop
curl -s -o nul -w "" http://localhost:8000/status >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] API bereit auf Port 8000.
    goto :apiready
)
set /a RETRIES+=1
if %RETRIES% GEQ 30 (
    echo [WARNUNG] API nach 30 Versuchen nicht erreichbar!
    echo [WARNUNG] Backend manuell pruefen: python -m uvicorn src.api.main:app --port 8000
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
echo   Dictate:  Gemini STT (eigenes Fenster)
echo ============================================================
echo.
echo [TIPP] Diktat: Im Dictate-Fenster Enter druecken, sprechen, Enter -> Zwischenablage
echo.
pause
goto :eof
