$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$RuntimeDir = Join-Path $ProjectRoot ".runtime"

function Stop-PidProcess {
    param(
        [string]$Name,
        [string]$PidFile
    )
    if (Test-Path $PidFile) {
        $pidStr = Get-Content $PidFile
        if ([int]::TryParse($pidStr, [ref]$null)) {
            $pidId = [int]$pidStr
            $process = Get-Process -Id $pidId -ErrorAction SilentlyContinue
            if ($process) {
                Stop-Process -Id $pidId -Force -ErrorAction SilentlyContinue
                Write-Host "[OK] $Name stopped" -ForegroundColor Green
            } else {
                Write-Host "[INFO] $Name was not running." -ForegroundColor Yellow
            }
        }
        Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "[INFO] $Name was not running." -ForegroundColor Yellow
    }
}

Stop-PidProcess -Name "Backend" -PidFile (Join-Path $RuntimeDir "backend.pid")
Stop-PidProcess -Name "Frontend" -PidFile (Join-Path $RuntimeDir "frontend.pid")
Stop-PidProcess -Name "Smee relay" -PidFile (Join-Path $RuntimeDir "smee.pid")
