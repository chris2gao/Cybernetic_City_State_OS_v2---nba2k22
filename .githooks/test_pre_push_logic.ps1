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
# Which tree the hook runs in. The nine cases below run in this repository. The
# publication-gate cases run in a throwaway worktree, for the reason given there.
$CaseCwd = $root
function Case($label, $line, $expect, $allowMaster) {
    [System.IO.File]::WriteAllText($inp, $line + "`n", $enc)
    $pfx = if ($allowMaster) { 'set CITYSTATE_ALLOW_MASTER=1&& ' } else { 'set CITYSTATE_ALLOW_MASTER=&& ' }
    cmd /c "cd /d `"$script:CaseCwd`"&& $pfx`"$SH`" .githooks/pre-push < `"$inp`" 2>&1" | Out-Null
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


# --- The publication gate as a consumed verdict -----------------------------
#
# The nine cases above are the hook's own decision table. These four are about
# something different: whether the hook actually consumes a verdict it does not
# make. A caller that runs a gate and ignores the answer is the exact defect this
# work exists to remove, so it has to be tested, not assumed.
#
# Three of them force the gate's answer with a stub, because the question is
# whether this caller propagates a verdict, not whether the gate's judgement is
# right - the gate's own suite covers that. The fourth uses the real gate.
#
# HOW THE STUB IS PLACED, and why not the obvious way:
#
# The first version of this block overwrote the real gate file and restored it
# from a backup in a finally. It took the backup on every StubGate call, so the
# second call backed up the stub written by the first, and the restore put a stub
# back into the working tree. The repository's 646-line publication gate sat there
# as three lines that always exit 13, and nothing caught it: not the path
# allowlist, which saw an authorized path, and not the YAML gate, which does not
# read .py. It was found by eye, one line above a commit. A test that can leave a
# production validator broken is worse than the gap it was written to close.
#
# The stub now goes in a throwaway worktree and the real file is never written to.
# --no-checkout keeps it cheap: the hook needs a git dir, a copy of itself and the
# gate path, not a whole tree. The hash comparison after the block is not
# redundant - it is the check that would have caught the bug above.

$GATE = '01_os/06_execution/workflow/publication_gate/workflow_publication_gate.py'
$realGate = Join-Path $root $GATE
$gateShaBefore = (git hash-object $realGate)

$wt = Join-Path $env:TEMP ('prepush_wt_' + [guid]::NewGuid().ToString('N').Substring(0, 8))
git worktree add --no-checkout --detach $wt HEAD 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Output 'could not create the sandbox worktree'; exit 1 }
$wtGate = Join-Path $wt $GATE

function StubGate($exitCode) {
    $stub = @(
        'import sys'
        "print('stub gate, forced exit $exitCode', file=sys.stderr)"
        "sys.exit($exitCode)"
    ) -join "`n"
    [System.IO.File]::WriteAllText($wtGate, $stub + "`n", $enc)
}

Write-Output ''
Write-Output 'PUBLICATION GATE VERDICT IS CONSUMED'
try {
    # The hook under test is the working-tree copy, not whatever HEAD carries.
    New-Item -ItemType Directory -Force -Path (Join-Path $wt '.githooks') | Out-Null
    New-Item -ItemType Directory -Force -Path (Split-Path $wtGate) | Out-Null
    Copy-Item (Join-Path $root '.githooks/pre-push') (Join-Path $wt '.githooks/pre-push') -Force
    $CaseCwd = $wt

    StubGate 0
    Case 'gate PASS, feature push still allowed' "refs/heads/x $head refs/heads/tmp/foo $parent" 0 $false

    StubGate 13
    Case 'gate nonzero blocks an allowed push'   "refs/heads/x $head refs/heads/tmp/foo $parent" 1 $false

    # Verdict consumed, not merely produced. With the gate forced to refuse, a
    # push that every other rule permits must still be refused; if the hook ran
    # the gate and carried on, this case would report exit 0.
    StubGate 41
    Case 'gate not-validated also blocks'        "refs/heads/x $head refs/heads/tmp/new $Z"      1 $false

    # The real gate, asked to judge without being told what to judge.
    #
    # Not a stub. The wrapper drops --candidate and hands everything else to the
    # actual gate, which refuses rather than assuming a commit. This is the only
    # case here that exercises a refusal the gate really produces, and it is what
    # "a validation that requires a candidate, and a caller that blocks on it"
    # means end to end. What it does not show is exit 41 - see the note below.
    $target = $realGate -replace '\\', '/'
    $wrapper = @(
        'import runpy, sys'
        'argv, out, i = sys.argv[1:], [], 0'
        'while i < len(argv):'
        '    if argv[i] == "--candidate":'
        '        i += 2'
        '        continue'
        '    out.append(argv[i])'
        '    i += 1'
        "sys.argv = ['$target'] + out"
        "runpy.run_path('$target', run_name='__main__')"
    ) -join "`n"
    [System.IO.File]::WriteAllText($wtGate, $wrapper + "`n", $enc)
    Case 'real gate, no candidate, blocks'       "refs/heads/x $head refs/heads/tmp/foo $parent" 1 $false
}
finally {
    $CaseCwd = $root
    git worktree remove --force $wt 2>&1 | Out-Null
}

# On exit 41, plainly: it is reachable here only because a stub produced it.
# run_minimum_operational_loop.validate_run returns 41 when it has no candidate,
# and no publication consumer calls that function - it reads the working tree,
# while the gate judges a commit, so calling it from the gate would swap "judges
# what is being pushed" for "judges whatever is on disk". The case above proves
# this hook blocks on 41 if it ever arrives. It does not prove the publication
# path can currently produce it. Recorded rather than implied.
#
# Do not read that as "nothing semantic is checked on a push". Since 2026-09-12
# the gate resolves each stage's plan and completion acceptance records at their
# own commits and hands them to the deliberation mechanism, refusing with exit 17
# when the mechanism refuses. That path does not go through validate_run, which is
# why 41 stays unreachable while acceptance is still judged.

$gateShaAfter = (git hash-object $realGate)
Write-Output ''
if ($gateShaBefore -ne $gateShaAfter) {
    Write-Output '  FAIL   this test modified the real publication gate'
    Write-Output ("         before " + $gateShaBefore)
    Write-Output ("         after  " + $gateShaAfter)
    Write-Output ("         restore with: git checkout -- " + $GATE)
    $fails++
}
else { Write-Output ('  gate file untouched: ' + $gateShaBefore) }

Remove-Item $inp -ErrorAction SilentlyContinue
Write-Output ''
if ($fails -eq 0) { Write-Output 'all 13 cases as specified'; exit 0 }
Write-Output "$fails case(s) did not behave as specified"
exit 1
