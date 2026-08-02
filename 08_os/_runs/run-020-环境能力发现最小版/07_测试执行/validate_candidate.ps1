[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

[string]$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "../../../..")).Path
[string]$runRoot = Join-Path $repoRoot "08_os/_runs/run-020-环境能力发现最小版"
[string]$runtime = Join-Path $runRoot "_runtime"
[string]$schemaSource = Join-Path $repoRoot "08_os/03_mechanisms/environment_capability/实现/环境能力receipt_schema_v1.yml"
[string]$positiveSource = Join-Path $runRoot "08_结论/环境能力receipt_实测_v1.yml"
[string]$wrapper = Join-Path $repoRoot "08_os/06_execution/tools/check_jsonschema/invoke.ps1"
[string]$resultPath = Join-Path $PSScriptRoot "results.json"
$utf8 = [Text.UTF8Encoding]::new($false)

if (Test-Path -LiteralPath $runtime) {
    $existing = @(Get-ChildItem -LiteralPath $runtime -Force)
    if ($existing.Count -gt 0) {
        throw "run-local runtime must be empty before validation"
    }
} else {
    $null = New-Item -ItemType Directory -Path $runtime
}

[string]$schemaCopy = Join-Path $runtime "environment_capability.schema.json"
[IO.File]::WriteAllBytes($schemaCopy, [IO.File]::ReadAllBytes($schemaSource))
$sourceHash = (Get-FileHash -LiteralPath $schemaSource -Algorithm SHA256).Hash.ToLowerInvariant()
$copyHash = (Get-FileHash -LiteralPath $schemaCopy -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceHash -ne $copyHash) {
    throw "temporary schema copy is not byte-identical"
}

$positiveText = [IO.File]::ReadAllText($positiveSource, $utf8)
$null = $positiveText | ConvertFrom-Json

function New-Clone {
    return ($positiveText | ConvertFrom-Json)
}

$cases = @()
$generatedFiles = [Collections.Generic.List[string]]::new()
$generatedFiles.Add($schemaCopy)

function Write-Instance {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CaseId,

        [Parameter(Mandatory = $true)]
        [object]$Value
    )
    $path = Join-Path $runtime "${CaseId}.json"
    [IO.File]::WriteAllText($path, ($Value | ConvertTo-Json -Depth 20), $utf8)
    $generatedFiles.Add($path)
    return $path
}

function Invoke-SchemaCase {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CaseId,

        [Parameter(Mandatory = $true)]
        [string]$InstancePath,

        [Parameter(Mandatory = $true)]
        [int]$ExpectedExit
    )
    $output = @(& $wrapper -SchemaPath $schemaCopy -InstancePath $InstancePath 2>&1 | ForEach-Object { [string]$_ })
    $actualExit = $LASTEXITCODE
    $raw = ($output -join "`n")
    $rawBytes = $utf8.GetBytes($raw)
    $digest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($rawBytes)).ToLowerInvariant()
    return [ordered]@{
        case_id = $CaseId
        expected_exit = $ExpectedExit
        actual_exit = $actualExit
        passed = $actualExit -eq $ExpectedExit
        output_sha256 = $digest
        output_line_count = $output.Count
    }
}

$cases += Invoke-SchemaCase -CaseId "positive_actual_receipt" -InstancePath $positiveSource -ExpectedExit 0

$missingRequired = New-Clone
$missingRequired.PSObject.Properties.Remove("toolchain")
$missingRequiredPath = Write-Instance -CaseId "negative_missing_required" -Value $missingRequired
$cases += Invoke-SchemaCase -CaseId "negative_missing_required" -InstancePath $missingRequiredPath -ExpectedExit 1

$literalPath = New-Clone
$driveRoot = [IO.Path]::GetPathRoot($env:SystemRoot)
$literalPath.environment_class.observations[0].value = [IO.Path]::Combine($driveRoot, "Users", "example", "workspace")
$literalPathFile = Write-Instance -CaseId "negative_literal_personal_path" -Value $literalPath
$cases += Invoke-SchemaCase -CaseId "negative_literal_personal_path" -InstancePath $literalPathFile -ExpectedExit 1

$wrongObservableState = New-Clone
$wrongObservableState.runtime_limits.observations[0].status = "unknown"
$wrongObservableStatePath = Write-Instance -CaseId "negative_not_observable_unmarked" -Value $wrongObservableState
$cases += Invoke-SchemaCase -CaseId "negative_not_observable_unmarked" -InstancePath $wrongObservableStatePath -ExpectedExit 1

$missingSource = New-Clone
$missingSource.environment_class.observations[0].PSObject.Properties.Remove("measurement_source")
$missingSourcePath = Write-Instance -CaseId "negative_missing_measurement_source" -Value $missingSource
$cases += Invoke-SchemaCase -CaseId "negative_missing_measurement_source" -InstancePath $missingSourcePath -ExpectedExit 1

foreach ($file in $generatedFiles) {
    if (Test-Path -LiteralPath $file -PathType Leaf) {
        Remove-Item -LiteralPath $file -Force
    }
}
if (@(Get-ChildItem -LiteralPath $runtime -Force).Count -ne 0) {
    throw "run-local runtime cleanup incomplete"
}
Remove-Item -LiteralPath $runtime -Force

$allPassed = @($cases | Where-Object { -not $_.passed }).Count -eq 0
$result = [ordered]@{
    schema_version = "environment_capability_validation.v1"
    schema_source_sha256 = $sourceHash
    temporary_schema_sha256 = $copyHash
    schema_copy_byte_identical = $sourceHash -eq $copyHash
    raw_outputs_retained = $false
    raw_output_policy = "ephemeral_then_deleted_to_avoid_persisting_the_literal_path_negative"
    cases = $cases
    summary = [ordered]@{
        positive_passed = @($cases | Where-Object { $_.case_id -eq "positive_actual_receipt" -and $_.passed }).Count
        negatives_rejected = @($cases | Where-Object { $_.case_id -like "negative_*" -and $_.passed }).Count
        all_passed = $allPassed
    }
}
[IO.File]::WriteAllText($resultPath, ($result | ConvertTo-Json -Depth 10) + "`n", $utf8)

if (-not $allPassed) {
    exit 1
}
exit 0
