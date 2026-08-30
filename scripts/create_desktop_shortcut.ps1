$ProjectRoot = Split-Path (Split-Path $MyInvocation.MyCommand.Path -Parent) -Parent
$TargetFile = Join-Path $ProjectRoot "CodeGateLauncher.exe"

if (-not (Test-Path $TargetFile)) {
    Write-Host "[ERROR] CodeGateLauncher.exe not found at $TargetFile" -ForegroundColor Red
    exit 1
}

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "CodeGate.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = "Launch CodeGate System"
$Shortcut.Save()

Write-Host "[OK] Desktop shortcut created at $ShortcutPath" -ForegroundColor Green

# Optional Auto-Start Shortcut
$StartShortcutPath = Join-Path $DesktopPath "Start CodeGate.lnk"
$StartShortcut = $WshShell.CreateShortcut($StartShortcutPath)
$StartShortcut.TargetPath = $TargetFile
$StartShortcut.Arguments = "--start"
$StartShortcut.WorkingDirectory = $ProjectRoot
$StartShortcut.Description = "Instantly Launch CodeGate System"
$StartShortcut.Save()

Write-Host "[OK] Auto-start desktop shortcut created at $StartShortcutPath" -ForegroundColor Green
