@echo off
REM Tägliches Backup nach Hostinger – Aufruf durch Windows Task Scheduler.
REM Arbeitsverzeichnis = ATLAS_CORE, Python aus aktivierter venv oder System-Python.
set ATLAS_ROOT=C:\ATLAS_CORE
cd /d "%ATLAS_ROOT%"
python "%ATLAS_ROOT%\src\scripts\daily_backup.py"
exit /b %ERRORLEVEL%
