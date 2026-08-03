param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path -LiteralPath $RepoRoot).Path
$run = Join-Path $repo "08_os/_runs/run-025-通讯机制结果建模与冻结测试"
$bPath = Join-Path $run "03_结果建模/B_通讯机制结果模型_v1.yml"
$testPath = Join-Path $run "04_测试生成/冻结测试集_v1.yml"
$connectorPath = Join-Path $run "02_前置阻塞清理/connector支持裁定_v1.yml"
$baselineRoot = Join-Path $run "02_前置阻塞清理/token_baseline"
$inventory1 = Join-Path $run "02_前置阻塞清理/core_window_inventory_run_1.json"
$inventory2 = Join-Path $run "02_前置阻塞清理/core_window_inventory_run_2.json"

$bText = Get-Content -LiteralPath $bPath -Raw
$testText = Get-Content -LiteralPath $testPath -Raw
$connectorText = Get-Content -LiteralPath $connectorPath -Raw
$failures = [System.Collections.Generic.List[string]]::new()

$invariantCounts = [ordered]@{}
foreach ($number in 1..8) {
    $count = [regex]::Matches($bText, "(?m)^\s+- 主张:.*\[I$number\].*$").Count
    $invariantCounts["I$number"] = $count
    if ($count -ne 1) {
        $failures.Add("I$number count=$count")
    }
}

$constraintCounts = [ordered]@{}
foreach ($number in 17..23) {
    $count = [regex]::Matches($bText, "(?m)^\s+- 主张:.*\[C$number\].*$").Count
    $constraintCounts["C$number"] = $count
    if ($count -ne 1) {
        $failures.Add("C$number count=$count")
    }
}

$testIds = @([regex]::Matches($testText, "\[(T\d{3})\]") | ForEach-Object { $_.Groups[1].Value })
if ($testIds.Count -ne 40 -or (@($testIds | Sort-Object -Unique).Count -ne 40)) {
    $failures.Add("frozen test IDs are not exact unique T001-T040")
}

$coverage = [ordered]@{}
foreach ($number in 1..14) {
    $count = [regex]::Matches($testText, "(?m)^\s+对应成功判据:\s+R$number\s*$").Count
    $coverage["R$number"] = $count
    if ($count -eq 0) {
        $failures.Add("R$number has zero tests")
    }
}

$traceViolations = 0
foreach ($match in [regex]::Matches($testText, "(?m)^\s+判据来源:\s*\[([^\]]+)\]\s*$")) {
    foreach ($token in $match.Groups[1].Value.Split(",")) {
        $source = $token.Trim()
        if ($source -notmatch "^(R([1-9]|1[0-4])|E-\d{3})$") {
            $traceViolations += 1
        }
    }
}
if ($traceViolations -ne 0) {
    $failures.Add("traceability violations=$traceViolations")
}

$r8ThresholdViolations = 0
foreach ($block in ($testText -split "(?m)(?=^\s{2}- 描述:)")) {
    if ($block -match "(?m)^\s+对应成功判据:\s+R8\s*$" -and
        $block -match "(阈值|至少|不少于|最多|低于|高于)\s*[:：=]?\s*\d") {
        $r8ThresholdViolations += 1
    }
}
if ($r8ThresholdViolations -ne 0) {
    $failures.Add("R8 numeric threshold violations=$r8ThresholdViolations")
}

$requiredTokenFields = @(
    "schema_version", "task_id", "task_type", "provider", "model", "effort",
    "session_mode", "protocol_profile", "input_tokens", "output_tokens",
    "reasoning_tokens", "cache_read_tokens", "cache_write_tokens", "tool_output_bytes",
    "reported_cost", "wall_seconds", "repair_attempts", "review_rounds",
    "validation_result", "quality_incidents", "metric_source"
)
$baselineFiles = @(Get-ChildItem -LiteralPath $baselineRoot -File -Filter "old_entry_baseline_*.json" | Sort-Object Name)
if ($baselineFiles.Count -lt 3) {
    $failures.Add("old-entry baseline records below task minimum")
}
$matchingDigests = [System.Collections.Generic.List[string]]::new()
foreach ($file in $baselineFiles) {
    $record = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
    foreach ($field in $requiredTokenFields) {
        if ($record.PSObject.Properties.Name -notcontains $field) {
            $failures.Add("$($file.Name) missing $field")
        }
    }
    if ($record.schema_version -ne "token_profile_run.v1" -or $record.validation_result -ne "pass") {
        $failures.Add("$($file.Name) invalid token record")
    }
    $matchingDigests.Add(($record.matching_dimensions | ConvertTo-Json -Depth 8 -Compress))
}
if (@($matchingDigests | Sort-Object -Unique).Count -ne 1) {
    $failures.Add("old-entry matching dimensions differ")
}

$inventoryHash1 = (Get-FileHash -Algorithm SHA256 -LiteralPath $inventory1).Hash.ToLowerInvariant()
$inventoryHash2 = (Get-FileHash -Algorithm SHA256 -LiteralPath $inventory2).Hash.ToLowerInvariant()
if ($inventoryHash1 -ne $inventoryHash2) {
    $failures.Add("inventory reruns differ")
}
$inventory = Get-Content -LiteralPath $inventory1 -Raw | ConvertFrom-Json
if ($inventory.coverage.completeness -ne "partial" -or @($inventory.coverage.not_observable).Count -eq 0) {
    $failures.Add("inventory observability boundary missing")
}

if ($connectorText -notmatch "(?m)^\s+mode:\s+excluded\s*$" -or
    $connectorText -notmatch "available=true" -or
    $connectorText -notmatch "supported_equivalence_pair:\s*\[local_git, github_cli\]") {
    $failures.Add("connector exclusion/invalidation/equivalence decision incomplete")
}

$personalPathHits = @(
    Get-ChildItem -LiteralPath $run -File -Recurse |
        Select-String -Pattern "[A-Za-z]:\\Users\\" -CaseSensitive:$false |
        Select-Object -First 10
)
if ($personalPathHits.Count -gt 0) {
    $failures.Add("personal absolute paths found")
}

$result = [ordered]@{
    status = if ($failures.Count -eq 0) { "pass" } else { "fail" }
    measurement_tool = "PowerShell regex + JSON + byte hashes; no PyYAML"
    invariant_counts = $invariantCounts
    A_v2_new_constraint_counts = $constraintCounts
    frozen_test_count = $testIds.Count
    traceability_violations = $traceViolations
    coverage_by_success_criterion = $coverage
    R8_numeric_threshold_violations = $r8ThresholdViolations
    old_entry_baseline_record_count = $baselineFiles.Count
    inventory_byte_identical = $inventoryHash1 -eq $inventoryHash2
    inventory_not_observable_count = @($inventory.coverage.not_observable).Count
    personal_absolute_path_hits = $personalPathHits.Count
    failures = @($failures)
}

$outputPath = if ([System.IO.Path]::IsPathRooted($Output)) { $Output } else { Join-Path $repo $Output }
$parent = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$temp = Join-Path $parent (".$([System.IO.Path]::GetFileName($outputPath)).$([Guid]::NewGuid().ToString('N')).tmp")
try {
    [System.IO.File]::WriteAllText($temp, ($result | ConvertTo-Json -Depth 10) + "`n", [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temp -Destination $outputPath -Force
}
finally {
    if (Test-Path -LiteralPath $temp) {
        Remove-Item -LiteralPath $temp
    }
}
Write-Output ($result | ConvertTo-Json -Compress)
if ($failures.Count -ne 0) {
    exit 1
}
