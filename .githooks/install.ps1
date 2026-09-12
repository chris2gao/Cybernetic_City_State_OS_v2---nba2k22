# Enable the city-state git hooks for this clone, then prove it took.
# Safe to re-run. Run from anywhere inside the repository.

$ErrorActionPreference = 'Stop'

$root = (git rev-parse --show-toplevel 2>$null)
if (-not $root) { Write-Output 'not inside a git repository'; exit 1 }
Set-Location -LiteralPath $root

git config core.hooksPath .githooks

$got = (git config --get core.hooksPath)
Write-Output ('repository     : ' + $root)
Write-Output ('core.hooksPath : ' + $got)

$hook = Join-Path $root '.githooks/pre-push'
if (-not (Test-Path -LiteralPath $hook)) {
    Write-Output 'pre-push       : MISSING - hooks path is set but the hook is not here'
    exit 1
}

# A CRLF shebang makes the hook fail to execute under Git Bash.
$bytes = [System.IO.File]::ReadAllBytes($hook)
$crlf = $false
for ($i = 0; $i -lt [Math]::Min($bytes.Length - 1, 200); $i++) {
    if ($bytes[$i] -eq 13 -and $bytes[$i + 1] -eq 10) { $crlf = $true; break }
}
Write-Output ('pre-push       : present, ' + $bytes.Length + ' bytes')
Write-Output ('line endings   : ' + $(if ($crlf) { 'CRLF  <-- FIX THIS, the hook will not run' } else { 'LF   ok' }))

Write-Output ''
Write-Output 'Proving the guard actually refuses a master push (dry-run, nothing is sent):'
# Match the specific refusal, not the word BLOCKED.
#
# The hook now emits BLOCKED for several different reasons, and the publication
# gate adds more. Matching the bare word would report "master push was refused"
# for a refusal that had nothing to do with master authorization: a receipt that
# names the wrong cause, which repository_guards_v1.yml already calls a false
# receipt when it happens the other way round.
$out = (git push --dry-run origin HEAD:master 2>&1 | Out-String)
if ($out -match 'BLOCKED\s+push to refs/heads/master without authorization') {
    Write-Output '  guard ACTIVE - master push was refused for lack of authorization'
}
elseif ($out -match 'BLOCKED') {
    Write-Output '  guard fired, but NOT for master authorization. Raw output:'
    ($out -split "`n" | Select-Object -First 8) | ForEach-Object { Write-Output ('    ' + $_.TrimEnd()) }
    Write-Output '  This proves the hook runs; it does not prove the master rule works.'
    exit 1
}
else {
    Write-Output '  guard DID NOT FIRE - do not rely on it. Raw output:'
    ($out -split "`n" | Select-Object -First 6) | ForEach-Object { Write-Output ('    ' + $_.TrimEnd()) }
    exit 1
}
