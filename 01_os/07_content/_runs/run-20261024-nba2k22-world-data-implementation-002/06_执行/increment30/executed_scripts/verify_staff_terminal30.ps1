$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$dest = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment30'
$launch = Get-Content -LiteralPath (Join-Path $dest 'worker-launch.json') -Raw | ConvertFrom-Json
$running = Get-Process -Id $launch.worker_pid -ErrorAction SilentlyContinue
if ($running) { throw 'The actual staff worker process is still present.' }
$receipt = [ordered]@{worker_pid=$launch.worker_pid;worker_process_absent=$true;verified_at=(Get-Date).ToUniversalTime().ToString('o')}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dest 'worker-terminal.json') -Encoding utf8
$receipt | ConvertTo-Json -Compress
