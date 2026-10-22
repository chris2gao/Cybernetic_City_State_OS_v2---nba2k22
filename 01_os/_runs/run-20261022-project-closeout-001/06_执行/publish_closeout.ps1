param([Parameter(Mandatory=$true)][string]$ExpectedMaster)
$ErrorActionPreference = 'Stop'
if ($ExpectedMaster -cnotmatch '^[0-9a-f]{40}$') { throw 'ExpectedMaster must be an exact SHA' }
$actualMaster = git ls-remote origin refs/heads/master
if ($LASTEXITCODE -ne 0) { throw 'Cannot read remote master' }
if (($actualMaster -split '\s+')[0] -ne $ExpectedMaster) { throw 'Remote master changed; inspect before publishing' }
$candidate = git rev-parse HEAD
git merge-base --is-ancestor $ExpectedMaster $candidate
if ($LASTEXITCODE -ne 0) { throw 'Not a fast-forward' }
if ((git config --get core.hooksPath) -ne '.githooks') { throw 'Registered hook is not enabled' }
$previousAllowMaster = [Environment]::GetEnvironmentVariable('CITYSTATE_ALLOW_MASTER', 'Process')
try {
    $env:CITYSTATE_ALLOW_MASTER = '1'
    git push --atomic origin HEAD:refs/heads/codex/project-closeout-20261022 HEAD:refs/heads/master
    if ($LASTEXITCODE -ne 0) { throw 'Publication failed' }
} finally {
    [Environment]::SetEnvironmentVariable('CITYSTATE_ALLOW_MASTER', $previousAllowMaster, 'Process')
}
$readback = git ls-remote origin refs/heads/master refs/heads/codex/project-closeout-20261022
if ($LASTEXITCODE -ne 0) { throw 'Remote readback failed' }
$readback | Write-Output
if (@($readback | Where-Object { ($_ -split '\s+')[0] -ne $candidate }).Count -ne 0 -or @($readback).Count -ne 2) {
    throw 'Remote readback differs from candidate'
}
