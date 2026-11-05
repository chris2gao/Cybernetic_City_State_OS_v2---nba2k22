$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$dest = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment33'
$launch = Get-Content -LiteralPath (Join-Path $dest 'worker-launch.json') -Raw | ConvertFrom-Json
$activeWorker = Get-Process -Id $launch.worker_pid -ErrorAction SilentlyContinue
if ($null -ne $activeWorker) { throw 'Actual launched worker is still live; continue waiting on it.' }
$result = Get-Content -LiteralPath (Join-Path $dest 'native-code-proof.json') -Raw | ConvertFrom-Json
if ($result.status -ne 'ACTUAL_NATIVE_STAFF_STORAGE_ROLES_CODE_AND_METADATA_VERIFIED') { throw ('Worker terminal failure: ' + $result.status + ': ' + $result.reason) }
$receipt = [ordered]@{worker_pid=$launch.worker_pid;worker_process_absent=$true;verified_at=[DateTime]::UtcNow.ToString('o');game_pid=$result.context_before.epoch.pid;creation_filetime=$result.context_before.epoch.creation_filetime;status=$result.status}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dest 'worker-terminal.json') -Encoding utf8
$receipt | ConvertTo-Json -Compress
