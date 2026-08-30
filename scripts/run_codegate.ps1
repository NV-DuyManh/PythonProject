$ErrorActionPreference = "Stop"

try {
    $PSScriptRootStr = $PSScriptRoot
    if ([string]::IsNullOrEmpty($PSScriptRootStr)) {
        $PSScriptRootStr = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
    }
    $ProjectRoot = Split-Path $PSScriptRootStr -Parent

    $RuntimeDir = Join-Path $ProjectRoot ".runtime"
    $LogsDir = Join-Path $RuntimeDir "logs"
    if (-not (Test-Path $LogsDir)) {
        New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    }

    $PsEntryLog = Join-Path $LogsDir "powershell-entry.log"
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $PsEntryLog -Value "[$ts] PSScriptRoot: $PSScriptRootStr"
    Add-Content -Path $PsEntryLog -Value "[$ts] ProjectRoot resolved to: $ProjectRoot"

    $StartupLog = Join-Path $LogsDir "startup.log"

    function Log-Message {
        param([string]$Message, [string]$Color = "Gray")
        $logts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logLine = "[$logts] $Message"
        Add-Content -Path $StartupLog -Value $logLine
        if ($Color -ne "None") {
            Write-Host $Message -ForegroundColor $Color
        }
    }

    Log-Message "Starting CodeGate Launcher..." "Cyan"

    # 1. VERIFY PYTHON
    $PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $PythonExe)) {
        Log-Message "[ERROR] Python virtual environment not found." "Red"
        Log-Message "Expected: $PythonExe" "Red"
        throw "Python virtual environment missing at $PythonExe"
    }

    # 2. VERIFY PYTHON VERSION
    $PyVer = & $PythonExe --version 2>&1
    Log-Message "Python version: $PyVer" "Cyan"
    if ($PyVer -notmatch "Python 3\.12") {
        Log-Message "[WARN] Expected Python 3.12.x, but found $PyVer" "Yellow"
    }

    # 3. VERIFY BACKEND IMPORT
    try {
        & $PythonExe -c "import uvicorn; import codegate" 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Import failed" }
        Log-Message "[OK] Backend dependencies verified." "Green"
    } catch {
        Log-Message "[ERROR] Backend dependencies are not installed." "Red"
        throw "Import check failed for uvicorn or codegate"
    }

    # 4. VERIFY NODE AND NPM
    $DashboardDir = Join-Path $ProjectRoot "dashboard"
    if (-not (Test-Path (Join-Path $DashboardDir "package.json"))) {
        Log-Message "[ERROR] Frontend dashboard folder or package.json not found." "Red"
        throw "Dashboard folder missing"
    }

    $NodeVer = & node --version 2>&1
    Log-Message "Node version: $NodeVer" "Cyan"

    $NpmCmdInfo = Get-Command "npm.cmd" -ErrorAction Stop
    $NpmCmdPath = $NpmCmdInfo.Source
    Log-Message "Resolved npm.cmd: $NpmCmdPath" "Cyan"

    $NpmVer = & $NpmCmdPath --version 2>&1
    Log-Message "Npm version: $NpmVer" "Cyan"

    if (-not (Test-Path (Join-Path $DashboardDir "node_modules"))) {
        Log-Message "[INFO] node_modules missing. Running npm install..." "Cyan"
        $installProc = Start-Process -FilePath $NpmCmdPath -ArgumentList "install" -WorkingDirectory $DashboardDir -Wait -NoNewWindow -PassThru
        if ($installProc.ExitCode -ne 0) {
            throw "npm install failed"
        }
    }

    # Helper to check ports
    function Test-Port {
        param([int]$Port)
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) { return $true }
        return $false
    }

    # Helper to fetch health
    function Get-BackendHealth {
        try {
            $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/system/status" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            return $response
        } catch {
            return $null
        }
    }

    # 5. START BACKEND
    $BackendPidFile = Join-Path $RuntimeDir "backend.pid"
    if (Test-Port 8000) {
        $health = Get-BackendHealth
        if ($health) {
            Log-Message "[OK] CodeGate backend already running." "Green"
        } else {
            Log-Message "[ERROR] Port 8000 is occupied by another process." "Red"
            throw "Port 8000 occupied"
        }
    } else {
        Log-Message "[WAIT] Starting backend..." "Cyan"
        $BackendLog = Join-Path $LogsDir "backend.log"
        $BackendErrLog = Join-Path $LogsDir "backend_err.log"
        
        $BackendProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "codegate.api.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $ProjectRoot -WindowStyle Hidden -RedirectStandardOutput $BackendLog -RedirectStandardError $BackendErrLog -PassThru
        Set-Content -Path $BackendPidFile -Value $BackendProcess.Id
        
        $ready = $false
        for ($i = 0; $i -lt 15; $i++) {
            Start-Sleep -Seconds 2
            if (Get-BackendHealth) {
                $ready = $true
                break
            }
            # Check if process exited
            if ($BackendProcess.HasExited) {
                break
            }
        }
        if (-not $ready) {
            Log-Message "[ERROR] Backend failed to start." "Red"
            Log-Message "Open: $BackendErrLog" "Red"
            try {
                $errContent = Get-Content -Path $BackendErrLog -Tail 10 -ErrorAction SilentlyContinue
                if ($errContent) {
                    Log-Message "Last backend errors:" "Red"
                    foreach ($l in $errContent) { Log-Message "  $l" "Red" }
                }
            } catch {}
            throw "Backend startup failed or timed out"
        }
        Log-Message "[OK] Backend ready on http://127.0.0.1:8000" "Green"
    }

    # 6. SMEE CHECK
    # SMEE requires a config, but if not set we warn and continue
    Log-Message "[WARN] Smee not configured." "Yellow"
    Log-Message "       Local Dashboard will work." "Yellow"

    # 7. START FRONTEND
    $FrontendPidFile = Join-Path $RuntimeDir "frontend.pid"
    if (Test-Port 5173) {
        try {
            $res = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            Log-Message "[OK] CodeGate frontend already running." "Green"
        } catch {
            Log-Message "[ERROR] Port 5173 is occupied by another process." "Red"
            throw "Port 5173 occupied"
        }
    } else {
        Log-Message "[WAIT] Starting frontend..." "Cyan"
        $FrontendLog = Join-Path $LogsDir "frontend.log"
        $FrontendErrLog = Join-Path $LogsDir "frontend_err.log"
        
        $FrontendProcess = Start-Process -FilePath $NpmCmdPath -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort" -WorkingDirectory $DashboardDir -WindowStyle Hidden -RedirectStandardOutput $FrontendLog -RedirectStandardError $FrontendErrLog -PassThru
        Set-Content -Path $FrontendPidFile -Value $FrontendProcess.Id

        $fready = $false
        for ($i = 0; $i -lt 15; $i++) {
            Start-Sleep -Seconds 2
            try {
                $res = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                $fready = $true
                break
            } catch {}
            if ($FrontendProcess.HasExited) {
                break
            }
        }
        if (-not $fready) {
            Log-Message "[ERROR] Frontend failed to start." "Red"
            Log-Message "Open: $FrontendErrLog" "Red"
            try {
                $errContent = Get-Content -Path $FrontendErrLog -Tail 10 -ErrorAction SilentlyContinue
                if ($errContent) {
                    Log-Message "Last frontend errors:" "Red"
                    foreach ($l in $errContent) { Log-Message "  $l" "Red" }
                }
            } catch {}
            throw "Frontend startup failed or timed out"
        }
        Log-Message "[OK] Frontend ready on http://127.0.0.1:5173" "Green"
    }

    # 8. STATUS DISPLAY
    $status = Get-BackendHealth
    
    $github_status = "NOT CONFIGURED"
    $ai_status = "NOT CONFIGURED"
    $db_status = "NOT CONFIGURED"
    if ($status) {
        if ($status.github) { $github_status = $status.github.status }
        if ($status.ai) { $ai_status = $status.ai.status }
        if ($status.database) { $db_status = $status.database.status }
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host "            CODEGATE READY"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Backend: READY"
    Write-Host "Frontend: READY"
    Write-Host "Database: $db_status"
    Write-Host "GitHub: $github_status"
    Write-Host "AI: $ai_status"
    Write-Host "Smee: NOT CONFIGURED"
    Write-Host ""
    Write-Host "Dashboard: http://127.0.0.1:5173/dashboard"
    Write-Host "========================================"
    Log-Message "Backend URL: http://127.0.0.1:8000" "None"
    Log-Message "Frontend URL: http://127.0.0.1:5173" "None"
    Log-Message "Dashboard URL: http://127.0.0.1:5173/dashboard" "None"

    # 9. AUTO OPEN BROWSER
    try {
        Start-Process "http://127.0.0.1:5173/dashboard" -ErrorAction Stop
        Log-Message "[OK] Browser launched." "Green"
    } catch {
        Log-Message "[WARN] Failed to open browser automatically." "Yellow"
    }

    Write-Host ""
    Read-Host "Press ENTER to close launcher window"

} catch {
    Write-Host ""
    Write-Host "CODEGATE STARTUP FAILED" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

    if ($StartupLog -and (Test-Path (Split-Path $StartupLog -Parent))) {
        Add-Content -Path $StartupLog -Value "[$((Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))] ERROR: $($_.Exception.Message)"
    }

    Read-Host "Press ENTER to close"
    exit 1
}

exit 0
