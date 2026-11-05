$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\run_lineups_worker29.py'
$games = @(Get-Process NBA2K22)
if ($games.Count -ne 1) { throw 'A unique current NBA2K22 process is required.' }
$process = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"'),[string]$games[0].Id) -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
$receipt = [ordered]@{worker_pid=$process.Id;game_pid=$games[0].Id;mode='READ_ONLY_NATIVE_LINEUPS_AND_COPY_UPGRADE_V21'}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment29\worker-launch.json') -Encoding utf8
$receipt | ConvertTo-Json -Compress
