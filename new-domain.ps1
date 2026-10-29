<#
.SYNOPSIS
    Create a new City-State domain repository from core.

.DESCRIPTION
    A domain repo is a clone of core with its own origin. This script exists
    because doing it by hand goes wrong in one specific way: copying the core
    FOLDER also copies its remotes, so the new domain would keep pointing at
    core (and at any other domain remote core happens to have). One stray
    `git push` in that folder then writes into the wrong repository.

    `git clone` carries only `origin`, which this script immediately renames to
    `core` before adding the domain's own `origin`. After it runs, a plain
    `git push` inside the domain folder can only reach that domain.

    New domains do NOT need the `merge -s ours` step that the math domain
    required. That step existed only because that repo already held domain
    content which core's first commit deletes. A fresh domain starts at core's
    current state, so ordinary `git merge core/master` is correct from day one.

.EXAMPLE
    .\new-domain.ps1 -Name finance
#>
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Root = "E:\newStand\study",
    [string]$Owner = "chris2gao",
    [string]$RepoPrefix = "Cybernetic_City_State_OS_v2---",
    [string]$FolderPrefix = "Cybernetic_City_State_OS_v2 - ",
    [string]$CoreRepo = "git@github.com:chris2gao/Cybernetic_City_State_OS_v2---core.git"
)

# Deliberately NOT ErrorActionPreference='Stop'. Every step below shells out and
# checks $LASTEXITCODE explicitly, which is the honest test for a native command.
# With 'Stop', PowerShell treats ANY stderr output from git/gh as fatal - and the
# preflight probe below is *supposed* to have gh report "no such repository".
# That normal, expected case would abort the script.
$ErrorActionPreference = "Continue"

function Fail($message) {
    Write-Host "REFUSED: $message"
    exit 1
}

$repoName = "$RepoPrefix$Name"
$repoFull = "$Owner/$repoName"
$folder   = Join-Path $Root "$FolderPrefix$Name"
$originUrl = "git@github.com:$repoFull.git"

Write-Host "domain      : $Name"
Write-Host "repository  : $repoFull (private)"
Write-Host "folder      : $folder"
Write-Host ""

# --- preflight: refuse rather than clobber ---------------------------------
if (Test-Path $folder) { Fail "folder already exists: $folder" }

gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "gh is not authenticated; run 'gh auth login'" }

# Exit code, not stderr, is the signal here: a non-zero result means "no such
# repository", which is exactly the state we require before creating one.
gh repo view $repoFull 2>$null 1>$null
if ($LASTEXITCODE -eq 0) { Fail "repository already exists: $repoFull" }

# --- create, clone, wire remotes -------------------------------------------
Write-Host "[1/4] creating private repository"
gh repo create $repoFull --private --description "City-State domain: $Name (built on shared core)" | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "gh repo create failed" }

Write-Host "[2/4] cloning core"
git clone --quiet $CoreRepo $folder
if ($LASTEXITCODE -ne 0) { Fail "clone failed" }

Push-Location $folder
try {
    Write-Host "[3/4] wiring remotes (origin = this domain, core = upstream)"
    git remote rename origin core
    git remote add origin $originUrl

    # This explicit domain-creation invocation initializes only domain-owned
    # catalogs. It does not publish mechanisms or deploy a PRMS state service.
    $inheritedCore = (git rev-parse HEAD).Trim()
    $scaffoldReceipt = Join-Path ([System.IO.Path]::GetTempPath()) ("prms-domain-" + [guid]::NewGuid().ToString() + ".json")
    python 01_os/06_execution/boot/context_management/prms/cli.py scaffold-domain --repo-root . --commit $inheritedCore --repository $repoFull --domain-id $Name --output $scaffoldReceipt
    if ($LASTEXITCODE -ne 0) { Fail "domain catalog initialization failed" }
    git add -- 08_Domain_Applications/domain.yml 09_Domain_Global_Mechanisms/README.md 09_Domain_Global_Mechanisms/domain_mechanisms.yml 09_Domain_Global_Mechanisms/knowledge_catalog.yml
    if ($LASTEXITCODE -ne 0) { Fail "domain catalog staging failed" }
    git commit --quiet -m "Initialize domain-owned mechanism catalogs"
    if ($LASTEXITCODE -ne 0) { Fail "domain catalog commit failed" }

    Write-Host "[4/4] publishing and verifying"
    git push --quiet -u origin master
    if ($LASTEXITCODE -ne 0) { Fail "initial push failed" }

    $local  = (git rev-parse HEAD).Trim()
    $remote = ((git ls-remote origin master) -split "\s+")[0]
    if ($local -ne $remote) { Fail "readback mismatch: local $local vs remote $remote" }

    $remotes = (git remote) -join ","
    if ($remotes -ne "core,origin") {
        Fail "unexpected remote set '$remotes'; expected exactly core,origin"
    }

    Write-Host ""
    Write-Host "OK  $repoFull @ $local"
    Write-Host "    remotes: $remotes  (a plain 'git push' here reaches only this domain)"
    Write-Host ""
    Write-Host "next:"
    Write-Host "  1. put this domain's material under 08_Domain_Applications/ and 03_Daily_Execution/"
    Write-Host "  2. leave core-owned paths alone - see CORE_MANIFEST.yml"
    Write-Host "  3. to take a core upgrade later:  git fetch core; git merge core/master"
}
finally {
    Pop-Location
}
