[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

trap {
    [Console]::Error.WriteLine("run_validation harness error: $($_.Exception.Message)")
    [Console]::Error.WriteLine($_.ScriptStackTrace)
    exit 99
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "../../../..")).Path
$fixtures = Join-Path $PSScriptRoot "fixtures"
$schema = Join-Path $fixtures "run_manifest.schema.json"
$validYaml = Join-Path $fixtures "valid.yaml"
$validJson = Join-Path $fixtures "valid.json"
$wrapper = Join-Path $repoRoot "08_os/06_execution/tools/check_jsonschema/invoke.ps1"
$resultPath = Join-Path $PSScriptRoot "results.json"
$tool = (Get-Command -Name "check-jsonschema" -CommandType Application).Source
$pwsh = (Get-Command -Name "pwsh" -CommandType Application).Source
$windowsPowerShell = (Get-Command -Name "powershell" -CommandType Application).Source
$utf8 = [Text.UTF8Encoding]::new($false)

function Invoke-CapturedProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,

        [hashtable]$EnvironmentOverrides = @{}
    )

    $startUtc = [DateTimeOffset]::UtcNow
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $FilePath
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.StandardOutputEncoding = $utf8
    $info.StandardErrorEncoding = $utf8
    foreach ($argument in $ArgumentList) {
        $null = $info.ArgumentList.Add($argument)
    }
    foreach ($key in $EnvironmentOverrides.Keys) {
        $info.Environment[$key] = [string]$EnvironmentOverrides[$key]
    }

    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    try {
        $null = $process.Start()
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        $process.WaitForExit()
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        $exitCode = $process.ExitCode
        try {
            $peakWorkingSet = $process.PeakWorkingSet64
        }
        catch {
            $peakWorkingSet = $null
        }
    }
    catch {
        $stdout = ""
        $stderr = $_.Exception.Message
        $exitCode = 127
        $peakWorkingSet = $null
    }
    finally {
        $timer.Stop()
        $process.Dispose()
    }

    [pscustomobject]@{
        command = $FilePath
        arguments = $ArgumentList
        started_utc = $startUtc.ToString("o")
        duration_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 3)
        exit_code = $exitCode
        stdout = $stdout
        stderr = $stderr
        stdout_utf8_bytes = $utf8.GetByteCount($stdout)
        stderr_utf8_bytes = $utf8.GetByteCount($stderr)
        launched_process_peak_working_set_bytes = $peakWorkingSet
    }
}

function Invoke-TestCase {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Id,

        [Parameter(Mandatory = $true)]
        [string]$Category,

        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,

        [Parameter(Mandatory = $true)]
        [int]$ExpectedExitCode,

        [string[]]$ExpectedDiagnostics = @(),

        [hashtable]$EnvironmentOverrides = @{}
    )

    $capture = Invoke-CapturedProcess -FilePath $FilePath -ArgumentList $ArgumentList `
        -EnvironmentOverrides $EnvironmentOverrides
    $combined = "$($capture.stdout)`n$($capture.stderr)"
    $diagnosticMatches = @(
        $ExpectedDiagnostics | ForEach-Object {
            $combined.Contains($_, [StringComparison]::OrdinalIgnoreCase)
        }
    )
    $diagnosticsPassed = -not ($diagnosticMatches -contains $false)

    [pscustomobject]@{
        id = $Id
        category = $Category
        expected_exit_code = $ExpectedExitCode
        expected_diagnostics = $ExpectedDiagnostics
        diagnostic_matches = $diagnosticMatches
        passed = ($capture.exit_code -eq $ExpectedExitCode) -and $diagnosticsPassed
        result = $capture
    }
}

$cases = [Collections.Generic.List[object]]::new()

$cases.Add((Invoke-TestCase -Id "P-YAML-COLD" -Category "positive" -FilePath $tool `
    -ArgumentList @("--schemafile", $schema, $validYaml) -ExpectedExitCode 0 `
    -ExpectedDiagnostics @("ok -- validation done")))
$cases.Add((Invoke-TestCase -Id "P-JSON" -Category "positive" -FilePath $tool `
    -ArgumentList @("--schemafile", $schema, $validJson) -ExpectedExitCode 0 `
    -ExpectedDiagnostics @("ok -- validation done")))
$cases.Add((Invoke-TestCase -Id "P-METASCHEMA" -Category "positive" -FilePath $tool `
    -ArgumentList @("--check-metaschema", $schema) -ExpectedExitCode 0 `
    -ExpectedDiagnostics @("ok -- validation done")))

foreach ($repeat in 1..5) {
    $cases.Add((Invoke-TestCase -Id "R-YAML-$repeat" -Category "repeatability" `
        -FilePath $tool -ArgumentList @("--schemafile", $schema, $validYaml) `
        -ExpectedExitCode 0 -ExpectedDiagnostics @("ok -- validation done")))
}

$cases.Add((Invoke-TestCase -Id "N-MISSING-REQUIRED" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "missing_required.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("'status' is a required property")))
$cases.Add((Invoke-TestCase -Id "N-WRONG-TYPE" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "wrong_type.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("$.human_gate", "not of type 'boolean'")))
$cases.Add((Invoke-TestCase -Id "N-INVALID-ENUM" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "invalid_enum.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("$.status", "is not one of")))
$cases.Add((Invoke-TestCase -Id "N-EXTRA-PROPERTY" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "extra_property.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("unexpected", "Additional properties")))
$cases.Add((Invoke-TestCase -Id "N-NESTED-ERROR" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "nested_error.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("$.outputs.artifact_refs", "not of type 'array'")))
$cases.Add((Invoke-TestCase -Id "N-SCHEMA-SYNTAX" -Category "negative" `
    -FilePath $tool -ArgumentList @("--check-metaschema", (Join-Path $fixtures "invalid_schema_syntax.json")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("Failed to parse", "JSONDecodeError")))
$cases.Add((Invoke-TestCase -Id "N-SCHEMA-METASCHEMA" -Category "negative" `
    -FilePath $tool -ArgumentList @("--check-metaschema", (Join-Path $fixtures "invalid_schema_metaschema.json")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("$.type", "not valid under any")))
$cases.Add((Invoke-TestCase -Id "N-SCHEMA-MISSING" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", (Join-Path $fixtures "does-not-exist.schema.json"), $validYaml) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("FileNotFoundError", "does-not-exist.schema.json")))
$cases.Add((Invoke-TestCase -Id "N-INSTANCE-MISSING" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "does-not-exist.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("FileNotFoundError", "does-not-exist.yaml")))
$cases.Add((Invoke-TestCase -Id "N-INSTANCE-SYNTAX" -Category "negative" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, (Join-Path $fixtures "invalid_instance_syntax.yaml")) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("Failed to parse")))

$unicodeInstance = Join-Path $fixtures "含 空格与中文/合法 实例.yaml"
$cases.Add((Invoke-TestCase -Id "B-UNICODE-SPACE-PATH" -Category "boundary" `
    -FilePath $tool -ArgumentList @("--schemafile", $schema, $unicodeInstance) `
    -ExpectedExitCode 0 -ExpectedDiagnostics @("ok -- validation done")))

$wrapperPrefix = @("-NoLogo", "-NoProfile", "-NonInteractive", "-File", $wrapper)
$cases.Add((Invoke-TestCase -Id "W-SUCCESS" -Category "wrapper" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", $schema, "-InstancePath", $validYaml)) `
    -ExpectedExitCode 0 -ExpectedDiagnostics @("ok -- validation done")))
$cases.Add((Invoke-TestCase -Id "W-VALIDATION-FAILURE" -Category "wrapper" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", $schema, "-InstancePath", (Join-Path $fixtures "invalid_enum.yaml"))) `
    -ExpectedExitCode 1 -ExpectedDiagnostics @("$.status", "is not one of")))
$cases.Add((Invoke-TestCase -Id "W-EXPLICIT-EXECUTABLE" -Category "wrapper" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", $schema, "-InstancePath", $validYaml, "-Executable", $tool)) `
    -ExpectedExitCode 0 -ExpectedDiagnostics @("ok -- validation done")))
$windowsPowerShellPrefix = @("-NoLogo", "-NoProfile", "-NonInteractive", "-File", $wrapper)
$cases.Add((Invoke-TestCase -Id "W-WINDOWS-POWERSHELL" -Category "wrapper" `
    -FilePath $windowsPowerShell `
    -ArgumentList ($windowsPowerShellPrefix + @("-SchemaPath", $schema, "-InstancePath", $validYaml)) `
    -ExpectedExitCode 0 -ExpectedDiagnostics @("ok -- validation done")))
$cases.Add((Invoke-TestCase -Id "W-MISSING-SCHEMA" -Category "wrapper" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", (Join-Path $fixtures "does-not-exist.schema.json"), "-InstancePath", $validYaml)) `
    -ExpectedExitCode 66 -ExpectedDiagnostics @("schema file not found")))
$cases.Add((Invoke-TestCase -Id "W-MISSING-INSTANCE" -Category "wrapper" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", $schema, "-InstancePath", (Join-Path $fixtures "does-not-exist.yaml"))) `
    -ExpectedExitCode 66 -ExpectedDiagnostics @("instance file not found")))
$cases.Add((Invoke-TestCase -Id "W-REMOTE-SCHEMA-REJECTED" -Category "boundary" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", "https://example.com/schema.json", "-InstancePath", $validYaml)) `
    -ExpectedExitCode 66 -ExpectedDiagnostics @("schema file not found", "https://example.com/schema.json")))

$restrictedPath = "C:\Windows\System32;C:\Program Files\PowerShell\7"
$cases.Add((Invoke-TestCase -Id "W-TOOL-UNAVAILABLE" -Category "boundary" -FilePath $pwsh `
    -ArgumentList ($wrapperPrefix + @("-SchemaPath", $schema, "-InstancePath", $validYaml)) `
    -ExpectedExitCode 69 -ExpectedDiagnostics @("executable unavailable on PATH", "check-jsonschema") `
    -EnvironmentOverrides @{ Path = $restrictedPath }))

$repeatCases = @($cases | Where-Object { $_.category -eq "repeatability" })
$repeatOutputs = @($repeatCases | ForEach-Object { "$($_.result.exit_code)|$($_.result.stdout)|$($_.result.stderr)" })
$repeatabilityPassed = ($repeatCases.Count -eq 5) -and
    (@($repeatCases | Where-Object { -not $_.passed }).Count -eq 0) -and
    (@($repeatOutputs | Select-Object -Unique).Count -eq 1)

function Get-TextMetrics {
    param([Parameter(Mandatory = $true)][string]$Path)
    $content = [IO.File]::ReadAllText($Path)
    [pscustomobject]@{
        path = [IO.Path]::GetRelativePath($repoRoot, $Path).Replace("\", "/")
        characters = $content.Length
        utf8_bytes = $utf8.GetByteCount($content)
    }
}

$schemaMetrics = Get-TextMetrics -Path $schema
$instanceMetrics = Get-TextMetrics -Path (Join-Path $fixtures "missing_required.yaml")
$diagnosticSummary = "missing_required.yaml: $.status missing required property (exit 1)"
$directContextCharacters = $schemaMetrics.characters + $instanceMetrics.characters
$summaryCharacters = $diagnosticSummary.Length
$tokenMeasurement = [pscustomobject]@{
    telemetry_source = "not_observable"
    installed_idle = [pscustomobject]@{
        observed_exact_tokens = "not_observable"
        architectural_result = "no_tool_schema_or_document_injected"
        expected_incremental_tokens = 0
        expected_incremental_tokens_basis = "architecture_not_billing_telemetry"
    }
    registered_on_demand = [pscustomobject]@{
        observed_exact_tokens = "not_observable"
        default_boot_reference = $false
        mcp_exposed = $false
    }
    invoked = [pscustomobject]@{
        observed_exact_tokens = "not_observable"
        raw_cli_output_bytes_by_case = @(
            $cases | ForEach-Object {
                [pscustomobject]@{
                    id = $_.id
                    stdout = $_.result.stdout_utf8_bytes
                    stderr = $_.result.stderr_utf8_bytes
                }
            }
        )
    }
    diagnostic_consumed_by_model = [pscustomobject]@{
        observed_exact_tokens = "not_observable"
        summary = $diagnosticSummary
        summary_characters = $summaryCharacters
        summary_utf8_bytes = $utf8.GetByteCount($diagnosticSummary)
    }
    comparison = [pscustomobject]@{
        direct_schema_plus_instance_characters = $directContextCharacters
        direct_schema_plus_instance_utf8_bytes = $schemaMetrics.utf8_bytes + $instanceMetrics.utf8_bytes
        diagnostic_summary_characters = $summaryCharacters
        character_reduction = $directContextCharacters - $summaryCharacters
        direct_proxy_tokens = [Math]::Ceiling($directContextCharacters / 4)
        summary_proxy_tokens = [Math]::Ceiling($summaryCharacters / 4)
        proxy_label = "proxy_not_billing_tokens"
        proxy_scope = "ASCII-dominant calibration schema, fixture, and English summary only"
    }
}

$residualProcesses = @(
    Get-CimInstance -ClassName Win32_Process |
        Where-Object {
            $_.Name -eq "check-jsonschema.exe" -or
            ($_.Name -eq "python.exe" -and $_.ExecutablePath -like "*pipx*check-jsonschema*")
        } |
        Select-Object ProcessId, Name, ExecutablePath, CommandLine
)

$failedCases = @($cases | Where-Object { -not $_.passed })
$receipt = [ordered]@{
    schema_version = "check_jsonschema_validation_receipt.v1"
    generated_utc = [DateTimeOffset]::UtcNow.ToString("o")
    tool_version = (& $tool --version)
    tool_resolved_path = $tool
    schema = $schemaMetrics
    comparison_instance = $instanceMetrics
    cases = $cases
    repeatability = [pscustomobject]@{
        run_count = $repeatCases.Count
        identical_exit_and_diagnostics = $repeatabilityPassed
    }
    process_residue = [pscustomobject]@{
        matching_process_count = $residualProcesses.Count
        matches = $residualProcesses
    }
    memory_measurement_scope = "launched process only; child-process tree peak is not_observable"
    network_measurement = "not_observable_no_packet_capture"
    local_only_design = "all schemafile arguments are local paths; wrapper rejects URL-shaped schema input as a missing local file"
    token_and_context = $tokenMeasurement
    summary = [pscustomobject]@{
        total_cases = $cases.Count
        passed_cases = $cases.Count - $failedCases.Count
        failed_cases = $failedCases.Count
        all_passed = ($failedCases.Count -eq 0) -and $repeatabilityPassed -and ($residualProcesses.Count -eq 0)
    }
}

[IO.File]::WriteAllText(
    $resultPath,
    ($receipt | ConvertTo-Json -Depth 12),
    $utf8
)

if (-not $receipt.summary.all_passed) {
    $failedIds = @($failedCases | ForEach-Object { $_.id }) -join ", "
    [Console]::Error.WriteLine("run_validation failed: $failedIds")
    exit 1
}

Write-Output "PASS: $($receipt.summary.passed_cases)/$($receipt.summary.total_cases) cases"
Write-Output "PASS: 5-run diagnostics identical"
Write-Output "PASS: no matching resident process"
exit 0
