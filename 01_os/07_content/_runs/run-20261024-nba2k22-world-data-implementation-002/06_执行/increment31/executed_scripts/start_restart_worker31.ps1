$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\run_restart_worker31.py'
$games = @(Get-Process NBA2K22)
if ($games.Count -ne 1) { throw 'A unique current NBA2K22 process is required.' }
$process = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"')) -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
$receipt = [ordered]@{worker_pid=$process.Id;observed_game_pid=$games[0].Id;pid_selection='Python discovers NBA2K22.exe afresh; no PID argument';mode='READ_ONLY_RECONNECT_AND_ONE_PUBLIC_GAME_MODE_VERIFICATION_CAPTURE'}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment31\worker-launch.json') -Encoding utf8
$receipt | ConvertTo-Json -Compress
