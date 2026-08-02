# Fourteen cases against .githooks/pre-push, driven through stdin without a network.
#
# The first nine preserve the branch/trunk/history decision table. Five integration
# cases prove the personal-path gate scans only the pushed commit range and fails
# closed when its validator or Python runtime cannot be used.

$ErrorActionPreference = 'Stop'
$sourceRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $sourceRoot) { Write-Output 'not inside a git repository'; exit 1 }

$SH = 'C:\Program Files\Git\bin\sh.exe'
if (-not (Test-Path -LiteralPath $SH)) { Write-Output "sh not found at $SH"; exit 1 }

$sandbox = Join-Path $env:TEMP ('citystate-pre-push-' + [guid]::NewGuid().ToString('N'))
$caseOutputs = @{}
$fails = 0

function Invoke-SandboxGit {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArguments)
    & git -C $sandbox @GitArguments | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArguments -join ' ') failed with exit $LASTEXITCODE"
    }
}

function Write-Utf8Lf([string]$Path, [string]$Text) {
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, ($Text -replace "`r`n", "`n"), $encoding)
}

function Case(
    [string]$Label,
    [string]$Line,
    [int]$Expected,
    [bool]$AllowMaster = $false,
    [bool]$NoPython = $false
) {
    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = $SH
    $start.Arguments = '.githooks/pre-push origin unused'
    $start.WorkingDirectory = $sandbox
    $start.UseShellExecute = $false
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.EnvironmentVariables['CITYSTATE_ALLOW_MASTER'] = $(if ($AllowMaster) { '1' } else { '' })
    $start.EnvironmentVariables['CITYSTATE_TEST_NO_PYTHON'] = $(if ($NoPython) { '1' } else { '' })

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $start
    [void]$process.Start()
    $process.StandardInput.NewLine = "`n"
    $process.StandardInput.WriteLine($Line)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $combined = ($stdout + $stderr).Trim()
    $caseOutputs[$Label] = $combined
    $ok = ($process.ExitCode -eq $Expected)
    if (-not $ok) { $script:fails++ }
    Write-Output ("  {0,-6} {1,-45} exit={2} expected={3}" -f $(if ($ok) { 'PASS' } else { 'FAIL' }), $Label, $process.ExitCode, $Expected)
}

try {
    New-Item -ItemType Directory -Path (Join-Path $sandbox '.githooks') -Force | Out-Null
    $validatorRoot = Join-Path $sandbox '08_os/06_execution/validators/personal_paths'
    New-Item -ItemType Directory -Path $validatorRoot -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $sourceRoot '.githooks/pre-push') -Destination (Join-Path $sandbox '.githooks/pre-push')
    Copy-Item -LiteralPath (Join-Path $sourceRoot '08_os/06_execution/validators/personal_paths/validate.py') -Destination (Join-Path $validatorRoot 'validate.py')
    Copy-Item -LiteralPath (Join-Path $sourceRoot '08_os/06_execution/validators/personal_paths/patterns.json') -Destination (Join-Path $validatorRoot 'patterns.json')

    Invoke-SandboxGit init --quiet
    Invoke-SandboxGit config user.email validator@example.invalid
    Invoke-SandboxGit config user.name 'Pre-push Test'
    Invoke-SandboxGit config core.autocrlf false
    Invoke-SandboxGit branch -M master

    $legacyValue = @('C:', '\Users', '\gk', '\legacy.txt') -join ''
    Write-Utf8Lf (Join-Path $sandbox 'legacy.txt') ("legacy=" + $legacyValue + "`n")
    Write-Utf8Lf (Join-Path $sandbox 'clean.txt') "baseline`n"
    Invoke-SandboxGit add -- .githooks/pre-push 08_os/06_execution/validators/personal_paths/validate.py 08_os/06_execution/validators/personal_paths/patterns.json legacy.txt clean.txt
    Invoke-SandboxGit commit --quiet -m baseline
    $base = (& git -C $sandbox rev-parse HEAD).Trim()
    Invoke-SandboxGit update-ref refs/remotes/origin/master $base

    Write-Utf8Lf (Join-Path $sandbox 'clean.txt') "portable change`n"
    Invoke-SandboxGit add -- clean.txt
    Invoke-SandboxGit commit --quiet -m clean
    $cleanHead = (& git -C $sandbox rev-parse HEAD).Trim()

    $pushedValue = @('C:', '\Users', '\gk', '\new.txt') -join ''
    Write-Utf8Lf (Join-Path $sandbox 'new.txt') ("artifact=" + $pushedValue + "`n")
    Invoke-SandboxGit add -- new.txt
    Invoke-SandboxGit commit --quiet -m finding
    $hitHead = (& git -C $sandbox rev-parse HEAD).Trim()
    $zero = '0' * 40

    & $SH -n (Join-Path $sandbox '.githooks/pre-push')
    if ($LASTEXITCODE -ne 0) { throw 'pre-push is not valid shell' }

    Write-Output 'ALLOWED (exit 0)'
    Case 'delete ordinary branch'         "refs/heads/x $zero refs/heads/tmp/foo $cleanHead" 0
    Case 'normal ff push to feature'      "refs/heads/x $cleanHead refs/heads/tmp/foo $base" 0
    Case 'brand new feature branch'       "refs/heads/x $cleanHead refs/heads/tmp/new $zero" 0
    Case 'delete master WITH env'         "refs/heads/x $zero refs/heads/master $cleanHead" 0 $true
    Case 'push master WITH env, ff'       "refs/heads/x $cleanHead refs/heads/master $base" 0 $true
    Case 'clean range ignores legacy hit' "refs/heads/x $cleanHead refs/heads/tmp/clean $base" 0

    Write-Output 'REFUSED (exit 1)'
    Case 'delete master, no env'          "refs/heads/x $zero refs/heads/master $cleanHead" 1
    Case 'push master, no env'            "refs/heads/x $cleanHead refs/heads/master $base" 1
    Case 'non-ff over feature branch'     "refs/heads/x $base refs/heads/tmp/foo $cleanHead" 1
    Case 'non-ff over master WITH env'    "refs/heads/x $base refs/heads/master $cleanHead" 1 $true
    Case 'personal path in pushed range'  "refs/heads/x $hitHead refs/heads/tmp/hit $cleanHead" 1

    Move-Item -LiteralPath (Join-Path $validatorRoot 'validate.py') -Destination (Join-Path $validatorRoot 'validate.off')
    Case 'validator missing'              "refs/heads/x $cleanHead refs/heads/tmp/missing $base" 1
    Move-Item -LiteralPath (Join-Path $validatorRoot 'validate.off') -Destination (Join-Path $validatorRoot 'validate.py')

    Move-Item -LiteralPath (Join-Path $validatorRoot 'patterns.json') -Destination (Join-Path $validatorRoot 'patterns.off')
    Case 'validator exit 2'               "refs/heads/x $cleanHead refs/heads/tmp/error $base" 1
    Move-Item -LiteralPath (Join-Path $validatorRoot 'patterns.off') -Destination (Join-Path $validatorRoot 'patterns.json')

    Case 'python unavailable'             "refs/heads/x $cleanHead refs/heads/tmp/no-python $base" 1 $false $true

    $proof = ($caseOutputs['personal path in pushed range'] -split "`r?`n" | Where-Object { $_ -match '^BLOCKED' } | Select-Object -First 1)
    Write-Output ''
    Write-Output ('gate fire proof: ' + $proof)
    if ($fails -eq 0) { Write-Output 'all 14 cases as specified'; exit 0 }
    Write-Output "$fails case(s) did not behave as specified"
    exit 1
}
finally {
    if (Test-Path -LiteralPath $sandbox) {
        Remove-Item -LiteralPath $sandbox -Recurse -Force -ErrorAction SilentlyContinue
    }
}
