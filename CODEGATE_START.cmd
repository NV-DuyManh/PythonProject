@echo off
setlocal
title CodeGate Launcher

cd /d "%~dp0"

if not exist ".runtime\logs" mkdir ".runtime\logs"

echo [%date% %time%] CMD ENTRY STARTED >> ".runtime\logs\launcher-entry.log"

echo ========================================
echo          CODEGATE STARTUP
echo ========================================
echo.
echo Project: %CD%
echo.

if not exist "scripts\run_codegate.ps1" (
    echo [ERROR] scripts\run_codegate.ps1 not found.
    echo [%date% %time%] ERROR: PowerShell script missing >> ".runtime\logs\launcher-entry.log"
    pause
    exit /b 1
)

echo [INFO] Launching PowerShell...
echo [%date% %time%] Starting PowerShell >> ".runtime\logs\launcher-entry.log"

C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe ^
  -NoLogo ^
  -NoProfile ^
  -ExecutionPolicy Bypass ^
  -File "%~dp0scripts\run_codegate.ps1"

set EXITCODE=%ERRORLEVEL%

echo [%date% %time%] PowerShell exit=%EXITCODE% >> ".runtime\logs\launcher-entry.log"

if not "%EXITCODE%"=="0" (
    echo.
    echo ========================================
    echo CODEGATE FAILED
    echo ========================================
    echo Exit code: %EXITCODE%
    echo.
    echo Logs:
    echo %~dp0.runtime\logs
    echo.
    pause
    exit /b %EXITCODE%
)

echo.
echo ========================================
echo CODEGATE LAUNCHER COMPLETED
echo ========================================
echo.
pause
