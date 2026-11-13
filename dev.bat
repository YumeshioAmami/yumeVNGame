@echo off
setlocal
cd /d "%~dp0"
echo Development mode: starts Vite + FastAPI in the browser.
echo Use start.bat for the desktop application.
npm run dev
endlocal

