$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../../..')).Path
$runtime = Join-Path (Split-Path -Parent $repo) 's3-live-private'
$python = (& python -B -c 'import sys; print(sys.executable)').Trim()
$runner = Join-Path $PSScriptRoot 'verify_retained_first_advance.py'
$stderr = Join-Path $runtime 'advance-after-cycle-001-reverified.stderr.log'
$stdout = Join-Path $runtime 'advance-after-cycle-001-reverified.stdout.log'
if ((Test-Path -LiteralPath $stderr) -or (Test-Path -LiteralPath $stdout)) {
    throw 'A prior verification exists. Inspect it before recovery.'
}
$cmd = '"' + $python + '" -B -X utf8 "' + $runner + '" > "' + $stdout + '" 2> "' + $stderr + '"'
$proc = Start-Process -FilePath $env:ComSpec -ArgumentList ('/d /s /c "' + $cmd + '"') -Verb RunAs -WindowStyle Hidden -PassThru -Wait
if (Test-Path -LiteralPath $stderr) { Get-Content -LiteralPath $stderr -Tail 12 }
if (Test-Path -LiteralPath $stdout) { Get-Content -LiteralPath $stdout -Tail 2 }
exit $proc.ExitCode
