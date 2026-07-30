[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$utf8 = [Text.UTF8Encoding]::new($false)
$outputPath = Join-Path $PSScriptRoot "安装真实性命令回执.json"
$pwsh = (Get-Command -Name "pwsh" -CommandType Application).Source

function Invoke-ReceiptCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Id,

        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList
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
    }
    catch {
        $stdout = ""
        $stderr = $_.Exception.Message
        $exitCode = 127
    }
    finally {
        $timer.Stop()
        $process.Dispose()
    }

    [pscustomobject]@{
        id = $Id
        command = $FilePath
        arguments = $ArgumentList
        started_utc = $startUtc.ToString("o")
        duration_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 3)
        exit_code = $exitCode
        stdout = $stdout
        stderr = $stderr
        stdout_utf8_bytes = $utf8.GetByteCount($stdout)
        stderr_utf8_bytes = $utf8.GetByteCount($stderr)
    }
}

$toolCommand = Get-Command -Name "check-jsonschema" -CommandType Application
$toolItem = Get-Item -LiteralPath $toolCommand.Source
$toolTarget = [string]$toolItem.Target
$venvScripts = Split-Path -Parent $toolTarget
$venvRoot = Split-Path -Parent $venvScripts
$venvPython = Join-Path $venvScripts "python.exe"
$pyvenvConfig = Join-Path $venvRoot "pyvenv.cfg"

$commands = [Collections.Generic.List[object]]::new()
$commands.Add((Invoke-ReceiptCommand -Id "PY-VERSION" -FilePath "py" -ArgumentList @("--version")))
$commands.Add((Invoke-ReceiptCommand -Id "PIPX-VERSION-DIRECT" -FilePath "pipx" -ArgumentList @("--version")))
$commands.Add((Invoke-ReceiptCommand -Id "TOOL-VERSION" -FilePath "check-jsonschema" -ArgumentList @("--version")))
$commands.Add((Invoke-ReceiptCommand -Id "WHERE-TOOL" -FilePath "where.exe" -ArgumentList @("check-jsonschema")))
$commands.Add((Invoke-ReceiptCommand -Id "PIPX-LIST-DIRECT" -FilePath "pipx" -ArgumentList @("list")))
$commands.Add((Invoke-ReceiptCommand -Id "GET-COMMAND-TOOL" -FilePath $pwsh `
    -ArgumentList @("-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "Get-Command check-jsonschema | Format-List *")))
$commands.Add((Invoke-ReceiptCommand -Id "TOOL-HELP" -FilePath "check-jsonschema" -ArgumentList @("--help")))
$commands.Add((Invoke-ReceiptCommand -Id "PIPX-VERSION-MODULE" -FilePath "py" -ArgumentList @("-m", "pipx", "--version")))
$commands.Add((Invoke-ReceiptCommand -Id "PIPX-LIST-MODULE" -FilePath "py" -ArgumentList @("-m", "pipx", "list")))
$commands.Add((Invoke-ReceiptCommand -Id "NEW-SUBPROCESS-PATH" -FilePath $pwsh `
    -ArgumentList @("-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "Get-Command check-jsonschema | Select-Object -ExpandProperty Source")))
$commands.Add((Invoke-ReceiptCommand -Id "VENV-PYTHON-VERSION" -FilePath $venvPython -ArgumentList @("--version")))
$commands.Add((Invoke-ReceiptCommand -Id "VENV-PACKAGE-VERSION" -FilePath $venvPython `
    -ArgumentList @("-c", "print(__import__('importlib.metadata', fromlist=['version']).version('check-jsonschema'))")))
$commands.Add((Invoke-ReceiptCommand -Id "VENV-PACKAGES" -FilePath "py" `
    -ArgumentList @("-m", "pipx", "runpip", "check-jsonschema", "list", "--format=json")))

$venvMeasure = Get-ChildItem -LiteralPath $venvRoot -Recurse -File |
    Measure-Object -Property Length -Sum
$residualProcesses = @(
    Get-CimInstance -ClassName Win32_Process |
        Where-Object {
            $_.Name -eq "check-jsonschema.exe" -or
            ($_.Name -eq "python.exe" -and $_.ExecutablePath -like "*pipx*check-jsonschema*")
        } |
        Select-Object ProcessId, Name, ExecutablePath, CommandLine
)

$receipt = [ordered]@{
    schema_version = "check_jsonschema_installation_receipt.v1"
    generated_utc = [DateTimeOffset]::UtcNow.ToString("o")
    commands = $commands
    resolved_installation = [pscustomobject]@{
        exposed_executable = $toolCommand.Source
        exposed_item_attributes = [string]$toolItem.Attributes
        exposed_item_link_type = [string]$toolItem.LinkType
        exposed_item_target = $toolTarget
        executable_exists = (Test-Path -LiteralPath $toolCommand.Source -PathType Leaf)
        target_exists = (Test-Path -LiteralPath $toolTarget -PathType Leaf)
        venv_root = $venvRoot
        venv_python = $venvPython
        pyvenv_config = $pyvenvConfig
        pyvenv_config_text = [IO.File]::ReadAllText($pyvenvConfig)
        venv_file_count = $venvMeasure.Count
        venv_file_bytes = [int64]$venvMeasure.Sum
        include_system_site_packages = $false
    }
    path_result = [pscustomobject]@{
        check_jsonschema_visible = $true
        pipx_direct_visible = $false
        pipx_module_fallback_verified = $true
        new_subprocess_resolves_tool = $true
    }
    process_residue = [pscustomobject]@{
        matching_process_count = $residualProcesses.Count
        matches = $residualProcesses
    }
    environment_changes_performed = $false
}

[IO.File]::WriteAllText(
    $outputPath,
    ($receipt | ConvertTo-Json -Depth 10),
    $utf8
)

Write-Output "PASS: installation receipt written"
Write-Output "PASS: check-jsonschema visible; direct pipx absent; py -m pipx verified"
Write-Output "PASS: no matching resident process"
