param(
    [Parameter(Mandatory)][string]$Python,
    [Parameter(Mandatory)][string]$Workspace,
    [ValidateSet('probe', 'arguments')][string]$Case = 'probe'
)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
if ($Case -eq 'probe') {
    $aliasPath = Join-Path $env:LOCALAPPDATA 'Microsoft/WindowsApps/pwsh.exe'
    $candidates = @(Get-Command pwsh.exe -All | ForEach-Object { $_.Source })
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$PID"
    [ordered]@{
        version = $PSVersionTable.PSVersion.ToString()
        edition = $PSVersionTable.PSEdition
        process_path = (Get-Process -Id $PID).Path
        os = $PSVersionTable.OS
        no_profile = $process.CommandLine -match '(?i)-NoProfile'
        non_interactive = $process.CommandLine -match '(?i)-NonInteractive'
        candidates = $candidates
        windowsapps_pwsh_present = Test-Path -LiteralPath $aliasPath
        native_argument_passing = "$PSNativeCommandArgumentPassing"
        python_path = $Python
    } | ConvertTo-Json -Depth 4 -Compress
    exit 0
}
$payload = '{"name":"中文 路径","nested":{"quote":"a\"b","list":[1,2]}}'
$echo = Join-Path $PSScriptRoot 'argument_echo.py'
$arguments = @('-B', '-X', 'utf8', $echo, $payload, $Workspace, '')
$output = & $Python @arguments
$code = $LASTEXITCODE
if ($code -ne 0) { throw "argument echo exited $code" }
$warningLog = Join-Path $Workspace 'warning.stderr'
$warning = & $Python -B $echo --warning 2> $warningLog
$warningCode = $LASTEXITCODE
$errorLog = Join-Path $Workspace 'failure.stderr'
& $Python -B $echo --fail 2> $errorLog
$failureCode = $LASTEXITCODE
$psFailure = $null
try {
    Get-Item -LiteralPath (Join-Path $Workspace 'missing-item') -ErrorAction Stop
} catch {
    $psFailure = $_.FullyQualifiedErrorId
}
$reaCommand = Get-Command rea.cmd -ErrorAction Stop
$cmdVersion = & $reaCommand.Source --version
$cmdCode = $LASTEXITCODE
if ($cmdCode -ne 0) { throw "REA .cmd version exited $cmdCode" }
[ordered]@{
    echo = @($output | ConvertFrom-Json)
    expected_payload = $payload
    native_exit = $failureCode
    warning_exit = $warningCode
    warning_stdout = "$warning"
    warning_stderr = Get-Content -LiteralPath $warningLog -Raw
    failure_stderr = Get-Content -LiteralPath $errorLog -Raw
    powershell_error_id = $psFailure
    cmd_version = "$cmdVersion".Trim()
    cmd_exit = $cmdCode
} | ConvertTo-Json -Depth 6 -Compress
exit 0
