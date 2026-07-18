[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,
    [Parameter(Mandatory = $true)]
    [string]$Message,
    [string[]]$Refs = @(),
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')),
    [string]$CityStateRoot = (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'CityState'),
    [string]$RemoteName = 'origin',
    [ValidatePattern('^ai/review/[A-Za-z0-9._/-]+$')]
    [string]$ReviewBranch = 'ai/review/latest',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Invoke-Git([string]$WorkingDirectory, [string[]]$Arguments, [switch]$AllowFailure) {
    $priorErrorAction = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = & git -C $WorkingDirectory @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $priorErrorAction }
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "git $($Arguments -join ' ') failed: $($output -join [Environment]::NewLine)"
    }
    return [ordered]@{ ExitCode = $exitCode; Output = @($output) }
}

function Write-Log([string]$Text) {
    $line = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') + ' ' + $Text
    [System.IO.File]::AppendAllText($script:LogPath, $line + "`n", $Utf8NoBom)
}

function Get-StagingMap([string]$StagingRoot) {
    $items = @()
    foreach ($file in @(Get-ChildItem -LiteralPath $StagingRoot -Recurse -File)) {
        $relative = $file.FullName.Substring($StagingRoot.Length).TrimStart([char[]]@('\','/'))
        $relative = $relative.Replace('\','/')
        if ($relative -notmatch '^\.ai/') { $relative = '.ai/' + $relative }
        if ($relative -notmatch '^\.ai/[A-Za-z0-9._/-]+$' -or $relative -match '(^|/)\.\.(/|$)') {
            throw "staging contains an unsafe destination path: $relative"
        }
        $items += [ordered]@{ Source = $file.FullName; Destination = $relative }
    }
    if ($items.Count -eq 0) { throw 'staging contains no files' }
    $duplicates = @($items | Group-Object Destination | Where-Object Count -gt 1)
    if ($duplicates.Count -gt 0) { throw 'staging maps more than one file to the same destination' }
    return @($items | Sort-Object Destination)
}

function Remove-TemporaryWorktree([string]$Path, [string]$Branch) {
    if (Test-Path -LiteralPath $Path) {
        [void](Invoke-Git $RepositoryRoot @('worktree','remove',$Path) -AllowFailure)
    }
    if ($Branch -match '^citystate-review-publish-[0-9a-f]+$') {
        [void](Invoke-Git $RepositoryRoot @('branch','-D',$Branch) -AllowFailure)
    }
}

function New-Candidate([int]$Attempt, [array]$StagingMap) {
    $suffix = [Guid]::NewGuid().ToString('N')
    $temporaryBranch = 'citystate-review-publish-' + $suffix
    $temporaryPath = Join-Path $CityStateRoot ('review-worktrees/' + $temporaryBranch)
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $temporaryPath)) | Out-Null
    try {
        $remoteRef = "refs/remotes/$RemoteName/$ReviewBranch"
        [void](Invoke-Git $RepositoryRoot @('worktree','add','-b',$temporaryBranch,$temporaryPath,$remoteRef))
        foreach ($item in $StagingMap) {
            $destination = Join-Path $temporaryPath ($item.Destination.Replace('/','\'))
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $destination)) | Out-Null
            Copy-Item -LiteralPath $item.Source -Destination $destination -Force
        }

        $missing = @()
        foreach ($reference in $Refs) {
            if ($reference -notmatch '^\.ai/[A-Za-z0-9._/-]+$' -or $reference -match '(^|/)\.\.(/|$)') {
                throw "unsafe reference path: $reference"
            }
            $result = Invoke-Git $temporaryPath @('ls-tree','-r','--name-only','HEAD','--',$reference)
            if ($result.Output -notcontains $reference) { $missing += $reference }
        }
        if ($missing.Count -gt 0) {
            throw ('required refs missing at review base: ' + ($missing -join ', '))
        }

        $destinations = @($StagingMap | ForEach-Object { $_.Destination })
        [void](Invoke-Git $temporaryPath (@('add','--') + $destinations))
        $diffResult = Invoke-Git $temporaryPath @('diff','--cached','--quiet') -AllowFailure
        if ($diffResult.ExitCode -eq 0) { throw 'staging produces no review-branch changes' }
        if ($diffResult.ExitCode -ne 1) { throw 'unable to inspect staged review changes' }
        [void](Invoke-Git $temporaryPath @('commit','-m',$Message))
        $candidate = (Invoke-Git $temporaryPath @('rev-parse','HEAD')).Output[0].Trim()
        if ($candidate -notmatch '^[0-9a-f]{40}$') { throw 'candidate review commit is invalid' }
        Write-Log "attempt=$Attempt candidate=$candidate paths=$($destinations.Count)"
        if ($DryRun) {
            return [ordered]@{ Published = $false; Candidate = $candidate; Paths = $destinations }
        }
        $push = Invoke-Git $temporaryPath @('push',$RemoteName,"HEAD:$ReviewBranch") -AllowFailure
        if ($push.ExitCode -ne 0) {
            Write-Log "attempt=$Attempt push=failed"
            return [ordered]@{ Published = $false; Candidate = $candidate; Paths = $destinations; PushFailed = $true }
        }
        Write-Log "attempt=$Attempt push=success"
        return [ordered]@{ Published = $true; Candidate = $candidate; Paths = $destinations }
    }
    finally {
        Remove-TemporaryWorktree $temporaryPath $temporaryBranch
    }
}

$repository = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\','/')
$staging = [System.IO.Path]::GetFullPath($SourceDir).TrimEnd('\','/')
$cityState = [System.IO.Path]::GetFullPath($CityStateRoot).TrimEnd('\','/')
if (-not (Test-Path -LiteralPath $repository -PathType Container)) { throw 'RepositoryRoot is missing' }
if (-not (Test-Path -LiteralPath $staging -PathType Container)) { throw 'SourceDir is missing' }
$stagingItem = Get-Item -LiteralPath $staging
if (($stagingItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -or
    @(Get-ChildItem -LiteralPath $staging -Recurse -Force | Where-Object {
        ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
    }).Count -gt 0) {
    throw 'SourceDir must not contain reparse points'
}
if ($staging -eq $repository -or $staging -eq $cityState -or $staging.Length -lt 12) {
    throw 'SourceDir is not a safe disposable staging directory'
}
if (-not $Message.Trim()) { throw 'Message must not be empty' }
if ($ReviewBranch -eq 'master' -or $ReviewBranch -notlike 'ai/review/*') {
    throw 'publish-review may push only an ai/review/* branch'
}

[System.IO.Directory]::CreateDirectory((Join-Path $cityState 'logs')) | Out-Null
$script:LogPath = Join-Path $cityState ('logs/publish-review-' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [Guid]::NewGuid().ToString('N') + '.log')
[System.IO.File]::WriteAllText($script:LogPath, '', $Utf8NoBom)
$stagingMap = Get-StagingMap $staging
Write-Log "start dry_run=$([bool]$DryRun) review_branch=$ReviewBranch staging_files=$($stagingMap.Count)"

[void](Invoke-Git $repository @('fetch',$RemoteName,$ReviewBranch))
$result = New-Candidate 1 $stagingMap
if (-not $DryRun -and -not $result.Published -and $result.PushFailed) {
    [void](Invoke-Git $repository @('fetch',$RemoteName,$ReviewBranch))
    $result = New-Candidate 2 $stagingMap
}
if (-not $DryRun -and -not $result.Published) {
    throw 'review publication failed after one non-fast-forward retry; staging was preserved'
}

if ($result.Published) {
    $parent = Split-Path -Parent $staging
    $consumed = Join-Path $parent ('.consumed-' + [Guid]::NewGuid().ToString('N'))
    Move-Item -LiteralPath $staging -Destination $consumed
    Remove-Item -LiteralPath $consumed -Recurse -Force
}

[ordered]@{
    status = $(if ($DryRun) { 'dry_run_pass' } else { 'published' })
    review_branch = $ReviewBranch
    candidate_head = $result.Candidate
    changed_paths = @($result.Paths)
    staging_preserved = [bool]$DryRun
    log_path = $script:LogPath
} | ConvertTo-Json -Depth 10
