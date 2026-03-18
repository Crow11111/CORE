@echo off
title CORE API Runner
cd /d C:\MTHO_CORE
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
echo [API] Starte Uvicorn Server...
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
echo [API] Server gestoppt.
pause
