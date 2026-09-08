param([Parameter(Mandatory=$true)][string]$LogPath)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $LogPath) { throw 'Evidence log already exists' }
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
& python -B -m pytest 01_os/06_execution/task_discipline/managed_verification -q -p no:cacheprovider -k 'source_change_stops or integer_is_not or copied_plan_boolean or exponent_overflow' *> $LogPath
$checkExit = $LASTEXITCODE
Get-Content -LiteralPath $LogPath -Tail 9
Write-Output ('raw_exit_code=' + $checkExit)
exit $checkExit
