$ErrorActionPreference = 'Stop'
$targetRoot = Join-Path $PSScriptRoot 'qualification-live'
if (Test-Path -LiteralPath (Join-Path $targetRoot 'parent-authorization.json')) {
    throw 'Qualification already frozen; no process interruption is permitted'
}
$worker = Get-CimInstance Win32_Process -Filter 'ProcessId=12308'
if (!$worker -or $worker.Name -ne 'python.exe' -or $worker.CommandLine -notlike '*run_qualifications.py*') {
    throw 'Owned pre-dispatch helper identity changed'
}
Stop-Process -Id 12308 -ErrorAction Stop
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'unneeded-capture-stopped.txt') -Value 'Stopped owned full acquisition before any parent grant or Native claim'
