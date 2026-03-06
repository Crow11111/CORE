@echo off
chcp 65001 >nul
title MTHO Dienste ??? Starter
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo.
echo === MTHO Dienste starten ===
echo Backend:     http://localhost:8000
echo Voice-Info:  http://localhost:8502
echo.

REM Prueft, ob auf LocalPort wirklich gelauscht wird (nur LISTENING), nicht irgendeine Verbindung mit dieser Nummer
call :port_listening 8000
if errorlevel 1 (
  echo [1/2] Backend Port 8000... gestartet.
  start "MTHO Backend" cmd /k "python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
) else (
  echo [1/2] Backend Port 8000... Port belegt, ueberspringe.
)

call :port_listening 8502
if errorlevel 1 (
  echo [2/2] Voice-Info Port 8502... gestartet.
  start "MTHO Voice-Info" cmd /k "python -m streamlit run src/ui/voice_info_console.py --server.port 8502"
) else (
  echo [2/2] Voice-Info Port 8502... Port belegt, ueberspringe.
)

echo.
echo Kurz warten, dann Browser oeffnen...
timeout /t 6 /nobreak >nul
start "" "http://localhost:8502"

echo.
echo Fertig. Fenster: MTHO Backend, Voice-Info.
echo Zum Beenden: die CMD-Fenster der Dienste schliessen.
echo.
pause
goto :eof

:port_listening
REM Gibt 0 zurueck wenn Port als LISTENING belegt, sonst 1 (Port frei). Verhindert Falschtreffer von netstat/findstr.
netstat -ano 2>nul | findstr /R /C:"LISTENING" /C:"ABH.REN" | findstr ":%1 " >nul
if errorlevel 1 exit /b 1
exit /b 0




