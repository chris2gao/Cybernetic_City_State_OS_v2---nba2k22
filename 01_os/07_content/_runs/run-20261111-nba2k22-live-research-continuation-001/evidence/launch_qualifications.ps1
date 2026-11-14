$ErrorActionPreference = 'Stop'
$python = 'C:/Users/gk/AppData/Local/Python/pythoncore-3.14-64/python.exe'
$script = Join-Path $PSScriptRoot 'run_qualifications.py'
& $python -B -X utf8 $script 1> (Join-Path $PSScriptRoot 'qualifications.stdout.log') 2> (Join-Path $PSScriptRoot 'qualifications.stderr.log')
$result = $LASTEXITCODE
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'qualifications.exit.txt') -Value $result
exit $result
