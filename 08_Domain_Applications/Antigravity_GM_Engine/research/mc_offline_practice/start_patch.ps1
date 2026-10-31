# NBA 2K22 MyCAREER Offline Team Practice Unlocker Launcher
$nodePath = "C:\Program Files\nodejs\node.exe"
$scriptPath = Join-Path $PSScriptRoot "run_offline_practice_patch.js"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  NBA 2K22 MyCAREER Offline Team Practice Facility Unlocker  " -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $nodePath)) {
    Write-Host "[ERROR] Node.js not found at $nodePath" -ForegroundColor Red
    exit 1
}

& $nodePath $scriptPath
