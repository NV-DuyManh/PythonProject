@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        RESTARTING CODEGATE
echo ========================================

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop_codegate.ps1"
timeout /t 2 /nobreak >nul
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_codegate.ps1"
set PS_EXIT=%ERRORLEVEL%

if %PS_EXIT% NEQ 0 (
    echo.
    echo CODEGATE FAILED TO START
    echo Exit Code: %PS_EXIT%
    echo Log location: .runtime\logs\startup.log
    pause
    exit /b %PS_EXIT%
)

echo.
echo Press any key to close this launcher window.
echo CodeGate will continue running in background.
pause
