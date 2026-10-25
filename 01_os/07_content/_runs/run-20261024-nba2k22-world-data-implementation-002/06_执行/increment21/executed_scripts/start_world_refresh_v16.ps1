$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\run_world_refresh_v16.py'
$gameProcesses = @(Get-Process NBA2K22)
if ($gameProcesses.Count -ne 1) { throw 'A unique current NBA2K22 process is required.' }
$workerProcess = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"'),[string]$gameProcesses[0].Id) -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
Write-Output ('Explicit read-only refresh worker PID ' + $workerProcess.Id + '; current game PID ' + $gameProcesses[0].Id)
