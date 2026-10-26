$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$worker = Join-Path $taskRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\read_staff_slot_enum32.py'
$process = Start-Process -FilePath 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList @(('"' + $worker + '"')) -WorkingDirectory $taskRoot -Verb RunAs -WindowStyle Hidden -PassThru
$process.Id
