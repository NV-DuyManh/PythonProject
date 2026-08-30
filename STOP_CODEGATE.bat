@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        STOPPING CODEGATE
echo ========================================

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop_codegate.ps1"
set PS_EXIT=%ERRORLEVEL%

if %PS_EXIT% NEQ 0 (
    echo.
    echo CODEGATE FAILED TO STOP
    pause
    exit /b %PS_EXIT%
)

echo.
pause
