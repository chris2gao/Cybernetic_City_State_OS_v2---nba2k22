param([Parameter(Mandatory=$true)][string]$LogPath)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $LogPath) { throw 'Log already exists; use a new attempt name' }
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
& python -B -m pytest 01_os/06_execution/task_discipline 01_os/06_execution/workflow/minimum_operational_loop 01_os/06_execution/task_orchestration/big_task -q -p no:cacheprovider *> $LogPath
$checkExit = $LASTEXITCODE
Get-Content -LiteralPath $LogPath -Tail 8
Write-Output ('raw_exit_code=' + $checkExit)
exit $checkExit
