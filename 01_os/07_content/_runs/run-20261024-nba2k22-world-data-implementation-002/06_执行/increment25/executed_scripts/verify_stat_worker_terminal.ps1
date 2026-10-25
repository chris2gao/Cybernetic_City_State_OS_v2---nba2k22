$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$dest = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment25'
$launch = Get-Content -LiteralPath (Join-Path $dest 'worker-launch.json') -Raw | ConvertFrom-Json
$workerProcess = Get-Process -Id $launch.worker_pid -ErrorAction SilentlyContinue
if ($null -ne $workerProcess) { throw 'Recorded worker PID still exists; inspect actual process.' }
$receipt = [ordered]@{checked_at=[DateTime]::UtcNow.ToString('o');worker_pid=$launch.worker_pid;worker_process_absent=$true;terminal_basis='Actual recorded worker PID absent from Get-Process'}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dest 'worker-terminal.json') -Encoding utf8
Write-Output 'Actual code-verification worker process is absent.'
