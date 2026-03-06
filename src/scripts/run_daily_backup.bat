@echo off
REM Tägliches Backup nach Hostinger – Aufruf durch Windows Task Scheduler.
REM Arbeitsverzeichnis = MTHO_CORE, Python aus aktivierter venv oder System-Python.
set MTHO_ROOT=C:\MTHO_CORE
cd /d "%MTHO_ROOT%"
python "%MTHO_ROOT%\src\scripts\daily_backup.py"
exit /b %ERRORLEVEL%
