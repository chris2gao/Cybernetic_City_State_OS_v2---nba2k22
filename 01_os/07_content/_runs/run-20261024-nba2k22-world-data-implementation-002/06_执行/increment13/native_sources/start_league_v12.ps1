$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\capture_league_v12.py'
$gameProcess = @(Get-Process NBA2K22)
if ($gameProcess.Count -ne 1 -or $gameProcess[0].Id -ne 2132) { throw 'Resolve the restarted game process before this capture.' }
$workerProcess = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"'),'2132') -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
Write-Output ('Elevated read-only league worker PID ' + $workerProcess.Id)
