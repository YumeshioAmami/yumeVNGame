@echo off
setlocal
cd /d "%~dp0"
echo Starting desktop source watcher. Close this window to stop auto-restart.
python scripts\watch_desktop.py
endlocal

