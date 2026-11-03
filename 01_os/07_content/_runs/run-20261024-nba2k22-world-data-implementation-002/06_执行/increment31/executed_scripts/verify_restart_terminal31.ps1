$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$dest = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment31'
$launch = Get-Content -LiteralPath (Join-Path $dest 'worker-launch.json') -Raw | ConvertFrom-Json
$activeWorker = Get-Process -Id $launch.worker_pid -ErrorAction SilentlyContinue
if ($null -ne $activeWorker) { throw 'Actual launched worker is still live; keep waiting on that worker.' }
$result = Get-Content -LiteralPath (Join-Path $dest 'worker-result.json') -Raw | ConvertFrom-Json
if ($result.status -ne 'ACTUAL_RESTART_AUTO_RECONNECT_AND_RECEIPT_RECOVERY_VERIFIED') { throw ('Worker terminal failure: ' + $result.status + ': ' + $result.reason) }
$receipt = [ordered]@{worker_pid=$launch.worker_pid;worker_process_absent=$true;verified_at=[DateTime]::UtcNow.ToString('o');game_pid=$result.current_process_epoch.pid;creation_filetime=$result.current_process_epoch.creation_filetime;status=$result.status}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dest 'worker-terminal.json') -Encoding utf8
$receipt | ConvertTo-Json -Compress
