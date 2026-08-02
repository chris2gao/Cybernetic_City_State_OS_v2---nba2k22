param(
    [string]$Output = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$runRoot = Join-Path $repoRoot "08_os\_runs\run-023-通讯机制需求建模"
$v1Path = Join-Path $runRoot "01_需求建模\A_通讯机制需求建模_v1.yml"
$v2Path = Join-Path $runRoot "01_需求建模\A_通讯机制需求建模_v2.yml"
$confirmV1Path = Join-Path $runRoot "01_需求建模\Human确认_v1.yml"
$confirmV2Path = Join-Path $runRoot "01_需求建模\Human确认_v2.yml"
$manifestPath = Join-Path $PSScriptRoot "A_v1_to_v2_变更清单.yml"
$base = "11b6bb2ba8064a1368067e6c9924b506249d8dcc"
$master = "a66ee671e47f3a90f3a108eb7531c7c84b0f9d37"
$expectedV1 = "cfff1e32928db0c8aeb860260b8ed9c34e32994ab1b137e015dcafe5eac0f4a7"
$expectedConfirmV1 = "43ad434934e3193bb74f4457856f394569c37aaca0ec36c99327b148e0bfd89e"

if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $PSScriptRoot "independent_scope_revision_results.json"
} elseif (-not [System.IO.Path]::IsPathRooted($Output)) {
    $Output = Join-Path $repoRoot $Output
}

$v2Lines = Get-Content -LiteralPath $v2Path
$confirmV2Lines = Get-Content -LiteralPath $confirmV2Path
$manifestLines = Get-Content -LiteralPath $manifestPath
$v2Text = $v2Lines -join "`n"
$expectedSlots = @("目标", "成功判据", "边界", "约束", "术语", "关联领域", "假设", "未解歧义")
$slotCounts = @{}
foreach ($slot in $expectedSlots) {
    $slotCounts[$slot] = @(Select-String -LiteralPath $v2Path -Pattern "^$([regex]::Escape($slot)):" -CaseSensitive).Count
}
$topLevelLines = @($v2Lines | Where-Object { $_ -match '^[^ #][^:]*:' })
$ambiguityCount = @(Select-String -LiteralPath $v2Path -Pattern '^  - 歧义:' -CaseSensitive).Count
$scopeCount = @(Select-String -LiteralPath $v2Path -Pattern '^    阻塞范围:' -CaseSensitive).Count
$stage3BlockerCount = @(Select-String -LiteralPath $v2Path -Pattern '^    阻塞范围:.*03_结果建模' -CaseSensitive).Count
$constraintCount = @(
    $constraintStart = [array]::IndexOf($v2Lines, "约束:")
    $termStart = [array]::IndexOf($v2Lines, "术语:")
    if ($constraintStart -ge 0 -and $termStart -gt $constraintStart) {
        $v2Lines[($constraintStart + 1)..($termStart - 1)] | Where-Object { $_ -match '^  - ' }
    }
).Count

$v1Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $v1Path).Hash.ToLowerInvariant()
$confirmV1Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $confirmV1Path).Hash.ToLowerInvariant()
$v2Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $v2Path).Hash.ToLowerInvariant()
$boundHash = ($confirmV2Lines | Where-Object { $_ -match '^  sha256: ([0-9a-f]{64})$' } | Select-Object -First 1) -replace '^  sha256: ', ''
$nullDecisionFields = @($confirmV2Lines | Where-Object { $_ -match '^  (decision|confirmed_by|confirmed_at|statement): null$' }).Count
$semanticManifestCount = @(Select-String -LiteralPath $manifestPath -Pattern '^  - path: (约束|未解歧义)' -CaseSensitive).Count

$requiredFragments = @(
    "Human 在本机操作的 shell 与其 git 凭据",
    "CITYSTATE_ALLOW_MASTER=1",
    "只计为防误操作机制，不构成 action-bound authorization",
    "宿主注入、绑定具体动作与事件，并一次性原子消费",
    "已 push 到远端的 commit 一律不得丢失",
    "未提交工作区内容允许丢失",
    "在途任务必须可从耐久证据恢复并续跑",
    "最终载体由 P5 release design 与 Human gate 决定"
)

$tracked = @(& git -c core.quotepath=false -C $repoRoot diff --name-only $base --)
$untracked = @(& git -c core.quotepath=false -C $repoRoot ls-files --others --exclude-standard)
$changedPaths = @($tracked + $untracked | Where-Object { $_ } | Sort-Object -Unique)
$allowedExact = @(
    "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/A_通讯机制需求建模_v2.yml",
    "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/Human确认_v2.yml",
    "08_os/_runs/run-023-通讯机制需求建模/run.yml"
)
$allowedPrefix = "08_os/_runs/run-023-通讯机制需求建模/07_测试执行/"
$outOfScope = @($changedPaths | Where-Object { $_ -notin $allowedExact -and -not $_.StartsWith($allowedPrefix) })

$personalText = & python (Join-Path $repoRoot "08_os\06_execution\validators\personal_paths\validate.py") `
    --repo-root $repoRoot --mode changed --base $master --summary-only
$personalExit = $LASTEXITCODE
$personal = $personalText | ConvertFrom-Json

$checks = [ordered]@{
    v1_candidate_bytes_unchanged = ($v1Hash -eq $expectedV1)
    v1_confirmation_bytes_unchanged = ($confirmV1Hash -eq $expectedConfirmV1)
    v2_confirmation_hash_bound = ($boundHash -eq $v2Hash)
    exact_eight_top_level_slots = ($topLevelLines.Count -eq 8 -and -not @($expectedSlots | Where-Object { $slotCounts[$_] -ne 1 }))
    constraint_count = ($constraintCount -eq 24)
    ambiguity_count = ($ambiguityCount -eq 8)
    ambiguity_scope_count = ($scopeCount -eq 8)
    no_stage3_blocker = ($stage3BlockerCount -eq 0)
    human_ruling_fragments_present = (-not @($requiredFragments | Where-Object { -not $v2Text.Contains($_) }))
    confirmation_awaiting = ($confirmV2Lines -contains "status: awaiting_human_confirmation")
    confirmation_four_fields_null = ($nullDecisionFields -eq 4)
    semantic_manifest_entries = ($semanticManifestCount -eq 19)
    exact_allowlist = ($changedPaths.Count -gt 0 -and $outOfScope.Count -eq 0)
    personal_paths_from_measured_master = ($personalExit -eq 0 -and $personal.hit_count -eq 0)
}
$failed = @($checks.GetEnumerator() | Where-Object { -not $_.Value } | ForEach-Object { $_.Key })
$result = [ordered]@{
    schema_version = "communication_requirement_scope_revision_independent_measurement.v1"
    measurement_tool = "PowerShell native text, hashing, Git, and canonical personal-path scan; does not import either task validator"
    result = if ($failed.Count -eq 0) { "pass" } else { "fail" }
    observed = [ordered]@{
        v1_sha256 = $v1Hash
        v1_confirmation_sha256 = $confirmV1Hash
        v2_sha256 = $v2Hash
        top_level_slots = $topLevelLines.Count
        constraints = $constraintCount
        ambiguities = $ambiguityCount
        stage3_blockers = $stage3BlockerCount
        semantic_manifest_entries = $semanticManifestCount
        changed_paths = $changedPaths.Count
        out_of_scope_paths = $outOfScope.Count
        personal_path_hits = $personal.hit_count
    }
    checks = $checks
    failed_checks = $failed
    final_independent_review = "not_performed; new session, different model family remains required before Human confirmation"
}
$rendered = $result | ConvertTo-Json -Depth 10
Set-Content -LiteralPath $Output -Value $rendered -Encoding utf8NoBOM
Write-Output $rendered
if ($failed.Count -ne 0) { exit 1 }
