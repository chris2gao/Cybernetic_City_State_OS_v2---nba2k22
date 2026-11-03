$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$workerProcess = Get-Process -Id 2172 -ErrorAction SilentlyContinue
if ($null -ne $workerProcess) { throw 'Recorded auxiliary worker PID still exists; inspect actual process.' }
$gameProcesses = @(Get-Process NBA2K22)
if ($gameProcesses.Count -ne 1) { throw 'Current game process is no longer unique.' }
$receipt = [ordered]@{
    checked_at = [DateTime]::UtcNow.ToString('o')
    worker_pid = 2172
    terminal_basis = 'Get-Process did not find the actual recorded worker PID'
    worker_process_absent = $true
    current_game_pid = $gameProcesses[0].Id
    current_game_start_time = $gameProcesses[0].StartTime.ToString('o')
}
$target = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment24\worker-terminal.json'
$receipt | ConvertTo-Json | Set-Content -LiteralPath $target -Encoding utf8
Write-Output 'Actual worker process absent; terminal receipt retained.'
