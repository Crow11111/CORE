@echo off
REM Tägliches Backup nach Hostinger – Aufruf durch Windows Task Scheduler.
REM (Veraltet durch CachyOS/Linux Migration -> nutze run_daily_backup.sh / cron)
REM Arbeitsverzeichnis = OMEGA_CORE, Python aus aktivierter venv oder System-Python.
set CORE_ROOT=/OMEGA_CORE
cd /d "%CORE_ROOT%"
python "%CORE_ROOT%\src\scripts\daily_backup.py"
exit /b %ERRORLEVEL%
