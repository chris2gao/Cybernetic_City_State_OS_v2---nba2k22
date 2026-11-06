param(
    [Parameter(Mandatory)]
    [ValidateSet('MyLEAGUE0003','MyLEAGUE0005')]
    [string]$DeclaredLoadedFilename
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../../..')).Path
$outer = Split-Path -Parent $repo
$python = (& python -B -c 'import sys; print(sys.executable)').Trim()
$runner = Join-Path $PSScriptRoot 'initialize_pilot.py'
$epoch = Join-Path $PSScriptRoot 'receipts/s3-l0-probe-03.json'
$runtime = Join-Path $outer 's3-live-private'
if (Test-Path -LiteralPath $runtime) {
    throw 'S3 private runtime already exists. Inspect its receipts before any recovery.'
}
$arguments = @(
    '-B', '-X', 'utf8', ('"' + $runner + '"'),
    '--declared-loaded-filename', $DeclaredLoadedFilename,
    '--epoch-receipt', ('"' + $epoch + '"'),
    '--runtime', ('"' + $runtime + '"')
)
$proc = Start-Process -FilePath $python -ArgumentList $arguments -Verb RunAs -WindowStyle Hidden -PassThru -Wait
Write-Output "S3 baseline process exit code $($proc.ExitCode)"
exit $proc.ExitCode
