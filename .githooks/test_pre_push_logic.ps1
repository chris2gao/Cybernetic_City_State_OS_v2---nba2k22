# Nine cases against .githooks/pre-push, driven through stdin instead of the network.
#
# install.ps1 proves the hook is installed and fires at all. This proves what it
# decides. git hands pre-push lines of "<local ref> <local sha> <remote ref>
# <remote sha>" on stdin, so the whole decision table can be exercised offline,
# with no remote and nothing at risk.
#
# Written when branch deletion was opened on 2026-08-02. The registry entry for
# this hook has to name evidence that is true; before this file the only evidence
# was install.ps1, which measures the master case alone.
#
# Two harness traps, both hit while writing it, both worth keeping in mind:
#   - PowerShell's pipe appends CRLF. The trailing CR lands in the last field, so
#     the null sha stops comparing equal and the ancestry branch fires when it
#     should have been skipped. Input must be written LF-only and redirected.
#   - naming a function parameter $args shadows PowerShell's automatic variable
#     and silently drops the arguments.
# Both produced confident, wrong results before being caught.

$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel 2>$null)
if (-not $root) { Write-Output 'not inside a git repository'; exit 1 }
Set-Location -LiteralPath $root

$SH = 'C:\Program Files\Git\bin\sh.exe'
if (-not (Test-Path $SH)) { Write-Output "sh not found at $SH"; exit 1 }

$Z = '0' * 40
$head = (git rev-parse HEAD)
$parent = (git rev-parse "HEAD^")
$enc = New-Object System.Text.UTF8Encoding($false)
$inp = Join-Path $env:TEMP 'pre_push_case.txt'

& $SH -n .githooks/pre-push
if ($LASTEXITCODE -ne 0) { Write-Output 'pre-push is not valid shell'; exit 1 }

$fails = 0
function Case($label, $line, $expect, $allowMaster) {
    [System.IO.File]::WriteAllText($inp, $line + "`n", $enc)
    $pfx = if ($allowMaster) { 'set CITYSTATE_ALLOW_MASTER=1&& ' } else { 'set CITYSTATE_ALLOW_MASTER=&& ' }
    cmd /c "$pfx`"$SH`" .githooks/pre-push < `"$inp`" 2>&1" | Out-Null
    $code = $LASTEXITCODE
    $ok = ($code -eq $expect)
    if (-not $ok) { $script:fails++ }
    Write-Output ("  {0,-6} {1,-42} exit={2} expected={3}" -f $(if ($ok) { 'PASS' } else { 'FAIL' }), $label, $code, $expect)
}

Write-Output 'ALLOWED (exit 0)'
Case 'delete ordinary branch'      "refs/heads/x $Z refs/heads/tmp/foo $head"      0 $false
Case 'normal ff push to feature'   "refs/heads/x $head refs/heads/tmp/foo $parent" 0 $false
Case 'brand new feature branch'    "refs/heads/x $head refs/heads/tmp/new $Z"      0 $false
Case 'delete master WITH env'      "refs/heads/x $Z refs/heads/master $head"       0 $true
Case 'push master WITH env, ff'    "refs/heads/x $head refs/heads/master $parent"  0 $true

Write-Output 'REFUSED (exit 1)'
Case 'delete master, no env'       "refs/heads/x $Z refs/heads/master $head"       1 $false
Case 'push master, no env'         "refs/heads/x $head refs/heads/master $parent"  1 $false
Case 'non-ff over feature branch'  "refs/heads/x $parent refs/heads/tmp/foo $head" 1 $false
# The one that matters most: the master switch must not also unlock a rewrite.
Case 'non-ff over master WITH env' "refs/heads/x $parent refs/heads/master $head"  1 $true

Remove-Item $inp -ErrorAction SilentlyContinue
Write-Output ''
if ($fails -eq 0) { Write-Output 'all 9 cases as specified'; exit 0 }
Write-Output "$fails case(s) did not behave as specified"
exit 1
