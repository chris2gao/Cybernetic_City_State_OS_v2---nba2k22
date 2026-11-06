param([Parameter(Mandatory=$true)][string]$Runtime,
      [Parameter(Mandatory=$true)][string]$Receipt,
      [Parameter(Mandatory=$true)][int]$Team)
$ErrorActionPreference = 'Stop'
$python = (& python -B -c 'import sys; print(sys.executable)').Trim()
$probe = Join-Path $PSScriptRoot 'readonly_preflight.py'
$source = (Resolve-Path -LiteralPath $Runtime).Path
$output = [IO.Path]::GetFullPath($Receipt)
if (Test-Path -LiteralPath $output) { throw 'Read-only receipt already exists' }
$arguments = @('-B', '-X', 'utf8', ('"' + $probe + '"'), '--runtime',
               ('"' + $source + '"'), '--team', $Team, '--out', ('"' + $output + '"'))
$process = Start-Process -FilePath $python -ArgumentList $arguments -Verb RunAs -WindowStyle Hidden -PassThru -Wait
exit $process.ExitCode
