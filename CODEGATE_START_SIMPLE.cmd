@echo off
setlocal
title CodeGate Simple Launcher

cd /d "%~dp0"

echo ========================================
echo CODEGATE STARTUP (SIMPLE FALLBACK MODE)
echo ========================================
echo Project: %CD%
echo.

if not exist ".runtime\logs" mkdir ".runtime\logs"

echo [INFO] Starting Backend...
start "CodeGate Backend" /D "%~dp0" "%~dp0.venv\Scripts\python.exe" -m uvicorn codegate.api.main:app --host 127.0.0.1 --port 8000

echo [INFO] Starting Frontend...
start "CodeGate Frontend" /D "%~dp0dashboard" cmd.exe /c npm.cmd run dev -- --host 127.0.0.1 --port 5173

echo.
echo Waiting a few seconds for services to start...
timeout /t 5 /nobreak >nul

echo [INFO] Opening Browser...
start "" "http://127.0.0.1:5173/dashboard"

echo.
echo ========================================
echo CODEGATE READY
echo ========================================
echo Close this window at any time.
echo Backend and Frontend will remain in their own console windows.
pause
