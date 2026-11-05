$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\capture_player_skill_v16.py'
$gameProcess = @(Get-Process NBA2K22)
if ($gameProcess.Count -ne 1) { throw 'A unique current NBA2K22 process is required.' }
$workerProcess = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"'),[string]$gameProcess[0].Id) -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
Write-Output ('Read-only player-skill worker PID ' + $workerProcess.Id + '; game PID ' + $gameProcess[0].Id)
