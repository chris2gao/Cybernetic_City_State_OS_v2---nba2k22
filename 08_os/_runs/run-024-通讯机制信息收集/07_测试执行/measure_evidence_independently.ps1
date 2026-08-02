param(
    [string]$Output = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$runRoot = Join-Path $repoRoot "08_os\_runs\run-024-通讯机制信息收集"
$evidenceRoot = Join-Path $runRoot "02_信息收集与提炼\evidence"

if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $PSScriptRoot "independent_results.json"
} elseif (-not [System.IO.Path]::IsPathRooted($Output)) {
    $Output = Join-Path $repoRoot $Output
}

function Count-Lines([string]$Path, [string]$Pattern) {
    return @(
        Select-String -LiteralPath $Path -Pattern $Pattern -CaseSensitive
    ).Count
}

$internalPath = Join-Path $evidenceRoot "01_内部证据_v1.yml"
$indexPath = Join-Path $evidenceRoot "证据索引_v1.yml"
$goalPath = Join-Path $evidenceRoot "00_挖掘目标与领域_v1.yml"
$sourcePath = Join-Path $evidenceRoot "信源使用记录_v1.yml"
$enumerationPath = Join-Path $evidenceRoot "core任务类型枚举_v1.json"

$capabilityCount = Count-Lines $internalPath '^  - capability_id: CAP-[0-9]{2}$'
$decisionCount = Count-Lines $internalPath '^    判定: (保留|改造|拒绝|待验证)$'
$reasonCount = Count-Lines $internalPath '^    理由: .+'
$failureHistoryCount = Count-Lines $internalPath '^    失败历史: .+'
$ambiguityCount = Count-Lines $internalPath '^  - ambiguity_id: A-AMB-[0-9]{2}$'
$escalatedCount = Count-Lines $internalPath '^    stage2_status: escalated$'
$evidenceCount = Count-Lines $indexPath '^  - evidence_id: E-[0-9]{3}$'
$questionCount = Count-Lines $goalPath '^  - id: RQ-[0-9]{2}$'
$sourceCount = Count-Lines $sourcePath '^  - source_id: SRC-[0-9]{3}$'

$entryMetrics = @{}
$currentEntry = $null
$currentRef = $null
foreach ($line in (Get-Content -LiteralPath $indexPath)) {
    if ($line -match '^  - evidence_id: (E-[0-9]{3})$') {
        $currentEntry = $Matches[1]
        $entryMetrics[$currentEntry] = @{
            refs = [System.Collections.Generic.List[object]]::new()
            count = $null
            status = $null
            critical = $null
            shared_groups = @()
        }
        $currentRef = $null
        continue
    }
    if ($null -eq $currentEntry) { continue }
    if ($line -match '^      - source_id: (SRC-[0-9]{3})$') {
        $currentRef = @{ source_id = $Matches[1]; location = ""; original = $null; group = "" }
        $entryMetrics[$currentEntry].refs.Add($currentRef)
    } elseif ($null -ne $currentRef -and $line -match '^        location: (.+)$') {
        $currentRef.location = $Matches[1]
    } elseif ($null -ne $currentRef -and $line -match '^        original_source: (true|false)$') {
        $currentRef.original = ($Matches[1] -eq "true")
    } elseif ($null -ne $currentRef -and $line -match '^        independence_group: (.+)$') {
        $currentRef.group = $Matches[1]
    } elseif ($line -match '^      independent_source_count: ([0-9]+)$') {
        $entryMetrics[$currentEntry].count = [int]$Matches[1]
        $currentRef = $null
    } elseif ($line -match '^      claim_source_status: (corroborated|single_source|unresolved)$') {
        $entryMetrics[$currentEntry].status = $Matches[1]
    } elseif ($line -match '^      critical_claim: (true|false)$') {
        $entryMetrics[$currentEntry].critical = ($Matches[1] -eq "true")
    } elseif ($line -match '^      shared_origin_groups: \[(.*)\]$') {
        $body = $Matches[1].Trim()
        $entryMetrics[$currentEntry].shared_groups = if ($body) { @($body -split ',' | ForEach-Object { $_.Trim() }) } else { @() }
    }
}

$traceCountMatches = $true
$traceSharedComplete = $true
$criticalSinglesExposed = $true
$derivedEnumerationNotOriginal = $true
$originalAnchorsImmutable = $true
$independentSourceTotal = 0
$singleSourceClaims = 0
$corroboratedClaims = 0
foreach ($metric in $entryMetrics.Values) {
    $originalRefs = @($metric.refs | Where-Object { $_.original -eq $true })
    $originalGroups = @($originalRefs | ForEach-Object { $_.group })
    $distinctGroups = @($originalGroups | Sort-Object -Unique)
    $actualShared = @($originalGroups | Group-Object | Where-Object { $_.Count -gt 1 } | ForEach-Object { $_.Name } | Sort-Object)
    $declaredShared = @($metric.shared_groups | Sort-Object)
    $traceCountMatches = $traceCountMatches -and ($metric.count -eq $distinctGroups.Count) -and ($metric.count -gt 0)
    $traceSharedComplete = $traceSharedComplete -and ([string]::Join('|', $actualShared) -eq [string]::Join('|', $declaredShared))
    if ($metric.critical -and $metric.count -eq 1) {
        $criticalSinglesExposed = $criticalSinglesExposed -and ($metric.status -in @('single_source', 'unresolved'))
    }
    if ($metric.count -gt 1) {
        $criticalSinglesExposed = $criticalSinglesExposed -and ($metric.status -eq 'corroborated')
    }
    $derivedEnumerationNotOriginal = $derivedEnumerationNotOriginal -and -not @(
        $metric.refs | Where-Object { $_.original -eq $true -and $_.location.Contains('core任务类型枚举_v1.json') }
    )
    $originalAnchorsImmutable = $originalAnchorsImmutable -and -not @(
        $originalRefs | Where-Object { $_.location -notmatch '[0-9a-f]{40}' }
    )
    $independentSourceTotal += $metric.count
    if ($metric.status -eq 'single_source') { $singleSourceClaims += 1 }
    if ($metric.status -eq 'corroborated') { $corroboratedClaims += 1 }
}

$judgmentText = Get-Content -LiteralPath (Join-Path $evidenceRoot "可行性判断_v1.yml") -Raw
$pointerText = Get-Content -LiteralPath (Join-Path $runRoot "08_结论\完成指针.md") -Raw
$stage3BlockerMatches = [regex]::Matches(
    $judgmentText,
    '(?ms)^  - question:.*?^    impact: 高\r?\n^    blocks: \[[^\]]*03_结果建模[^\]]*\]'
)
$stage3TransitionBlocked = (
    $stage3BlockerMatches.Count -gt 0 -and
    $judgmentText.Contains('status: downstream_blocked') -and
    $judgmentText.Contains('machine_gate: blocked') -and
    $judgmentText.Contains('enter_stage_3: prohibited') -and
    $pointerText.Contains('status: downstream_blocked') -and
    $pointerText.Contains('machine_gate: blocked') -and
    $pointerText.Contains('enter_stage_3: prohibited') -and
    -not $pointerText.Contains('才可自动进入下一阶段')
)

$manifestLines = Get-Content -LiteralPath (Join-Path $repoRoot "CORE_MANIFEST.yml")
$corePaths = [System.Collections.Generic.List[string]]::new()
$insideCore = $false
foreach ($line in $manifestLines) {
    if ($line -eq "core_owned_paths:") {
        $insideCore = $true
        continue
    }
    if ($line -eq "domain_owned_paths:") {
        break
    }
    if ($insideCore -and $line -match '^  - "(.+)"$') {
        $corePaths.Add($Matches[1])
    }
}
$nonOsCorePaths = @($corePaths | Where-Object { -not $_.StartsWith("08_os/") })

$trackedTaskFiles = @(
    & git -c core.quotepath=false -C $repoRoot ls-tree -r --name-only `
        a66ee671e47f3a90f3a108eb7531c7c84b0f9d37 -- .ai/TASKS
)
if ($LASTEXITCODE -ne 0) {
    throw "git ls-tree failed"
}
$taskIndexText = Get-Content -LiteralPath (Join-Path $repoRoot ".ai\TASKS\index.md") -Raw
$indexedTaskFiles = @($trackedTaskFiles | Where-Object { $taskIndexText.Contains($_) })

$enumeration = Get-Content -LiteralPath $enumerationPath -Raw | ConvertFrom-Json
$checks = [ordered]@{
    capability_rows = ($capabilityCount -eq 34)
    capability_decisions_complete = ($decisionCount -eq 34)
    capability_reasons_complete = ($reasonCount -eq 34)
    capability_failure_histories_complete = ($failureHistoryCount -eq 34)
    ambiguities_complete = ($ambiguityCount -eq 8)
    token_escalation_present = ($escalatedCount -eq 1)
    evidence_entries = ($evidenceCount -eq 27)
    traceability_count_matches_groups = $traceCountMatches
    traceability_shared_groups_complete = $traceSharedComplete
    critical_single_sources_exposed = $criticalSinglesExposed
    derived_enumeration_not_original = $derivedEnumerationNotOriginal
    original_source_anchors_immutable = $originalAnchorsImmutable
    stage3_transition_blocked = $stage3TransitionBlocked
    research_questions = ($questionCount -eq 6)
    sources = ($sourceCount -eq 14)
    manifest_core_owned_total = ($corePaths.Count -eq 44)
    manifest_non_08_core_owned = ($nonOsCorePaths.Count -eq 34)
    tracked_task_files = ($trackedTaskFiles.Count -eq 5)
    indexed_task_files = ($indexedTaskFiles.Count -eq 4)
    enumeration_unclassified_empty = ($enumeration.unclassified_core_paths.Count -eq 0)
    enumeration_extra_assignments_empty = ($enumeration.assignments_not_in_manifest.Count -eq 0)
    enumeration_counts_match_independent_measurement = (
        $enumeration.counts.core_owned_paths_total -eq $corePaths.Count -and
        $enumeration.counts.core_owned_paths_outside_08_os -eq $nonOsCorePaths.Count -and
        $enumeration.counts.tracked_ai_task_files -eq $trackedTaskFiles.Count -and
        $enumeration.counts.indexed_ai_task_files -eq $indexedTaskFiles.Count
    )
}

$failed = @($checks.GetEnumerator() | Where-Object { -not $_.Value } | ForEach-Object { $_.Key })
$result = [ordered]@{
    schema_version = "run024.independent_measurement.v1"
    measurement_tool = "PowerShell native text/JSON/Git measurement; does not import task validator"
    result = if ($failed.Count -eq 0) { "pass" } else { "fail" }
    observed = [ordered]@{
        capability_rows = $capabilityCount
        evidence_entries = $evidenceCount
        independent_sources_counted = $independentSourceTotal
        single_source_claims = $singleSourceClaims
        corroborated_claims = $corroboratedClaims
        high_impact_stage3_blockers = $stage3BlockerMatches.Count
        ambiguities = $ambiguityCount
        research_questions = $questionCount
        sources = $sourceCount
        core_owned_total = $corePaths.Count
        non_08_core_owned = $nonOsCorePaths.Count
        tracked_task_files = $trackedTaskFiles.Count
        indexed_task_files = $indexedTaskFiles.Count
    }
    checks = $checks
    failed_checks = $failed
    final_independent_review = "not_performed; different-model-family session remains required"
}

$rendered = $result | ConvertTo-Json -Depth 10
Set-Content -LiteralPath $Output -Value $rendered -Encoding utf8NoBOM
Write-Output $rendered
if ($failed.Count -ne 0) {
    exit 1
}
