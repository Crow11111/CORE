@echo off
TITLE CORE - FRONTEND (DEV AGENT)
echo ============================================================
echo CORE-GENESIS: FRONTEND DEV AGENT (Port 3000)
echo ============================================================

cd /d /OMEGA_CORE\frontend

echo [1/2] Checking Dependencies...
if not exist node_modules (
    echo [INFO] Installing NPM packages...
    call npm install
)

echo [2/2] Starting Vite Dev Server...
start "CORE FRONTEND" cmd /k "npm run dev"

echo [OK] Frontend wird gestartet...
timeout /t 5
start http://localhost:3000
exit
