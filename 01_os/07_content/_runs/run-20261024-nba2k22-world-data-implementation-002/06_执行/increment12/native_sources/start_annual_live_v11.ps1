$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\annual_capture_v11.py'
$gameProcess = @(Get-Process NBA2K22)
if ($gameProcess.Count -ne 1 -or $gameProcess[0].Id -ne 2132) { throw 'Game PID changed; resolve the current process before launching.' }
$arguments = @(('"' + $worker + '"'), '2132')
$workerProcess = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList $arguments -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
Write-Output ('Annual read-only worker started; worker PID ' + $workerProcess.Id)
