$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../../..')).Path
$runtime = Join-Path (Split-Path -Parent $repo) 's3-live-private'
$python = (& python -B -c 'import sys; print(sys.executable)').Trim()
$runner = Join-Path $PSScriptRoot 'first_decision.py'
$stderr = Join-Path $runtime 'l2-stderr.log'
$stdout = Join-Path $runtime 'l2-stdout.log'
if ((Test-Path -LiteralPath $stderr) -or (Test-Path -LiteralPath $stdout)) {
    throw 'L2 command was already attempted. Inspect the logs and Host state before any recovery.'
}
$quotedRunner = '"' + $runner + '"'
$quotedRuntime = '"' + $runtime + '"'
# Windows elevation cannot be combined with Start-Process stream redirection.
$cmd = '"' + $python + '" -B -X utf8 ' + $quotedRunner + ' --runtime ' + $quotedRuntime
$cmd += ' > "' + $stdout + '" 2> "' + $stderr + '"'
$proc = Start-Process -FilePath $env:ComSpec -ArgumentList ('/d /s /c "' + $cmd + '"') -Verb RunAs -WindowStyle Hidden -PassThru -Wait
if (Test-Path -LiteralPath $stderr) { Get-Content -LiteralPath $stderr -Tail 12 }
if (Test-Path -LiteralPath $stdout) { Get-Content -LiteralPath $stdout -Tail 2 }
exit $proc.ExitCode
