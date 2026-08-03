param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$BaseCommit,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = "Stop"

function Get-Sha256Text {
    param([Parameter(Mandatory = $true)][string]$Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

$repo = (Resolve-Path -LiteralPath $RepoRoot).Path
$resolvedBase = (& git -C $repo rev-parse "$BaseCommit^{commit}").Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Unable to resolve base commit."
}

$rawWorktrees = (& git -c core.quotepath=false -C $repo worktree list --porcelain) -join "`n"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to enumerate Git worktrees."
}

$worktrees = @()
foreach ($block in ($rawWorktrees -split "(`r?`n){2,}")) {
    if (-not $block.Trim()) {
        continue
    }
    $lines = $block -split "`r?`n"
    $worktreeLine = $lines | Where-Object { $_ -like "worktree *" } | Select-Object -First 1
    $headLine = $lines | Where-Object { $_ -like "HEAD *" } | Select-Object -First 1
    if (-not $worktreeLine -or -not $headLine) {
        continue
    }
    $pathValue = $worktreeLine.Substring(9)
    $branchLine = $lines | Where-Object { $_ -like "branch *" } | Select-Object -First 1
    $branchValue = if ($branchLine) { $branchLine.Substring(7) -replace "^refs/heads/", "" } else { $null }
    $worktrees += [ordered]@{
        worktree_path_sha256 = Get-Sha256Text -Value $pathValue
        head = $headLine.Substring(5)
        branch = $branchValue
        detached = [bool]($lines -contains "detached")
        locked = [bool]($lines -match "^locked")
        prunable = [bool]($lines -match "^prunable")
    }
}
$worktrees = @($worktrees | Sort-Object worktree_path_sha256)

$clientProcesses = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ProcessName -match "^(Codex|OpenAI|Claude|ChatGPT)" } |
        Group-Object ProcessName |
        Sort-Object Name |
        ForEach-Object {
            [ordered]@{
                process_name = $_.Name.ToLowerInvariant()
                instance_count = $_.Count
            }
        }
)

$document = [ordered]@{
    artifact_type = "core_window_inventory_measurement"
    method_version = 1
    repository = "Cybernetic_City_State_OS_v2---core"
    base_commit = $resolvedBase
    observations = [ordered]@{
        git_worktrees = [ordered]@{
            status = "observed"
            items = $worktrees
        }
        host_client_processes = [ordered]@{
            status = "observed"
            items = $clientProcesses
            limitation = "Process presence and grouped counts do not prove individual client sessions or repository attachment."
        }
        client_session_manifest = [ordered]@{
            status = "not_observable"
            reason = "The current local_git shell exposes no bounded API that lists Codex/Claude client threads and binds each thread to this repository."
        }
        window_to_task_binding = [ordered]@{
            status = "not_observable"
            reason = "Git worktrees expose branch/head candidates but not which UI windows are open, focused, dormant, or migrating."
        }
        migration_order = [ordered]@{
            status = "not_observable"
            reason = "No canonical cutover manifest exists before stage 5; ordering must be supplied and rebound immediately before T7 cutover."
        }
    }
    coverage = [ordered]@{
        observed_facts = @("git_worktree_set", "worktree_branch_and_head", "grouped_host_client_process_presence")
        not_observable = @("client_session_ids", "window_to_repository_binding", "window_focus_or_liveness", "migration_order")
        candidate_rule = "Every observed core worktree is a window candidate; a T7 host session manifest must add live client sessions before R13 can pass."
        recompute_before_T7_cutover = $true
        completeness = "partial"
    }
}

$outputPath = if ([System.IO.Path]::IsPathRooted($Output)) { $Output } else { Join-Path $repo $Output }
if (Test-Path -LiteralPath $outputPath) {
    throw "Immutable output already exists: $([System.IO.Path]::GetFileName($outputPath))"
}
$parent = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$temp = Join-Path $parent (".$([System.IO.Path]::GetFileName($outputPath)).$([Guid]::NewGuid().ToString('N')).tmp")
try {
    $json = $document | ConvertTo-Json -Depth 12
    [System.IO.File]::WriteAllText($temp, $json + "`n", [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temp -Destination $outputPath
}
finally {
    if (Test-Path -LiteralPath $temp) {
        Remove-Item -LiteralPath $temp
    }
}
Write-Output (@{status = "pass"; worktree_count = $worktrees.Count; process_group_count = $clientProcesses.Count} | ConvertTo-Json -Compress)
