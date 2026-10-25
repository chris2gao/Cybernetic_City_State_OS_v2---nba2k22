$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$dest = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment26'
$items = @()
foreach ($name in @('probe-worker-launch.json','capture-worker-launch.json','paired-worker-launch.json')) {
    $launch = Get-Content -LiteralPath (Join-Path $dest $name) -Raw | ConvertFrom-Json
    $workerProcess = Get-Process -Id $launch.worker_pid -ErrorAction SilentlyContinue
    $items += [ordered]@{launch_file=$name;worker_pid=$launch.worker_pid;process_present=($null -ne $workerProcess);cpu_seconds=$(if ($null -ne $workerProcess) {$workerProcess.CPU} else {$null})}
}
$receipt = [ordered]@{checked_at=[DateTime]::UtcNow.ToString('o');processes=$items;all_recorded_workers_absent=(@($items | Where-Object {$_.process_present}).Count -eq 0)}
if ($receipt.all_recorded_workers_absent) { $receipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $dest 'worker-terminal.json') -Encoding utf8 }
$receipt | ConvertTo-Json -Depth 4 -Compress
