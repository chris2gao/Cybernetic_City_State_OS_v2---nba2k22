param(
    [Parameter(Mandatory)]
    [ValidateSet('cycle-001','cycle-002','cycle-003','cycle-004')]
    [string]$AfterCycle,
    [Parameter(Mandatory)]
    [ValidateSet('已完成日历模拟')]
    [string]$CompletedTrigger
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../../..')).Path
$runtime = Join-Path (Split-Path -Parent $repo) 's3-live-private'
$python = (& python -B -c 'import sys; print(sys.executable)').Trim()
$runner = Join-Path $PSScriptRoot 'advance_verified_round.py'
$stderr = Join-Path $runtime "advance-after-$AfterCycle.stderr.log"
$stdout = Join-Path $runtime "advance-after-$AfterCycle.stdout.log"
if ((Test-Path -LiteralPath $stderr) -or (Test-Path -LiteralPath $stdout)) {
    throw 'A prior command exists. Inspect its logs and state before any recovery.'
}
$cmd = '"' + $python + '" -B -X utf8 "' + $runner + '" --after-cycle ' + $AfterCycle
$cmd += ' --completed-trigger "' + $CompletedTrigger + '" > "' + $stdout + '" 2> "' + $stderr + '"'
$proc = Start-Process -FilePath $env:ComSpec -ArgumentList ('/d /s /c "' + $cmd + '"') -Verb RunAs -WindowStyle Hidden -PassThru -Wait
if (Test-Path -LiteralPath $stderr) { Get-Content -LiteralPath $stderr -Tail 12 }
if (Test-Path -LiteralPath $stdout) { Get-Content -LiteralPath $stdout -Tail 2 }
exit $proc.ExitCode
