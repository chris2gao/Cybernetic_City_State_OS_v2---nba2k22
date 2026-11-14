$ErrorActionPreference = 'Stop'
$python = 'C:/Users/gk/AppData/Local/Python/pythoncore-3.14-64/python.exe'
$script = Join-Path $PSScriptRoot 'fresh_capture.py'
$old = Join-Path $PSScriptRoot 'fresh-capture-receipt.json'
if (Test-Path -LiteralPath $old) {
    Copy-Item -LiteralPath $old -Destination (Join-Path $PSScriptRoot 'fresh-capture-unelevated-receipt.json') -ErrorAction Stop
}
& $python -B -X utf8 $script 4352 1> (Join-Path $PSScriptRoot 'fresh-capture.stdout.log') 2> (Join-Path $PSScriptRoot 'fresh-capture.stderr.log')
$result = $LASTEXITCODE
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'fresh-capture.exit.txt') -Value $result
exit $result
