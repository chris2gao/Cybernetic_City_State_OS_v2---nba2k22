$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\read_stat_mode_metadata.py'
$gameProcesses = @(Get-Process NBA2K22)
if ($gameProcesses.Count -ne 1) { throw 'A unique current NBA2K22 process is required.' }
$workerProcess = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"'),[string]$gameProcesses[0].Id) -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
$receipt = [ordered]@{worker_pid=$workerProcess.Id;game_pid=$gameProcesses[0].Id;game_start_time=$gameProcesses[0].StartTime.ToString('o');mode='READ_ONLY_SELECTED_METADATA_AND_GETTER_CODE'}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\06_执行\increment26\probe-worker-launch.json') -Encoding utf8
$receipt | ConvertTo-Json -Compress
