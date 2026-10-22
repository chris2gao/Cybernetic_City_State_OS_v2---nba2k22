[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$')]
    [string]$SaveId = 'admin_probe',

    [ValidateRange(2000, 2100)]
    [int]$Season = 2022,

    [ValidateRange(1, 12)]
    [int]$Month = 1,

    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$')]
    [string]$Name = 'CAPTURE',

    [string]$Notes = '',

    [switch]$CalibrationOnly,

    [switch]$RescanOnly,

    [switch]$Worker,

    [string]$RequestPath
)

$ErrorActionPreference = 'Stop'
if ($CalibrationOnly -and $RescanOnly) {
    throw 'Choose only one of CalibrationOnly and RescanOnly.'
}

function Test-CurrentProcessAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function ConvertTo-PowerShellLiteral {
    param([Parameter(Mandatory)][string]$Value)
    return "'" + $Value.Replace("'", "''") + "'"
}

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$pythonExe = (Get-Command python -ErrorAction Stop).Source
$logDirectory = Join-Path $projectRoot 'database\saves\_admin_runs'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

if ($Worker) {
    if (-not $RequestPath -or -not (Test-Path -LiteralPath $RequestPath -PathType Leaf)) {
        throw 'Elevated worker request file is missing.'
    }
    if (-not (Test-CurrentProcessAdministrator)) {
        throw 'Elevated worker did not receive an administrator token.'
    }

    $request = Get-Content -LiteralPath $RequestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $SaveId = [string]$request.SaveId
    $Season = [int]$request.Season
    $Month = [int]$request.Month
    $Name = [string]$request.Name
    $Notes = [string]$request.Notes
    $isCalibrationOnly = [bool]$request.CalibrationOnly
    $isRescanOnly = [bool]$request.RescanOnly
    $logPath = [string]$request.LogPath
    if ($request.Dev14LifecycleLease) { $env:NBA2K22_DEV14_LIFECYCLE_LEASE = [string]$request.Dev14LifecycleLease }
} else {
    $isCalibrationOnly = [bool]$CalibrationOnly
    $isRescanOnly = [bool]$RescanOnly
    $runStamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
    $logPath = Join-Path $logDirectory ("data_capture_{0}_{1}.log" -f $SaveId, $runStamp)
}

if (-not $Worker -and -not (Test-CurrentProcessAdministrator)) {
    $requestPath = Join-Path ([IO.Path]::GetTempPath()) ("nba2k22_admin_capture_{0}.json" -f [guid]::NewGuid().ToString('N'))
    $request = [ordered]@{
        SaveId = $SaveId
        Season = $Season
        Month = $Month
        Name = $Name
        Notes = $Notes
        CalibrationOnly = $isCalibrationOnly
        RescanOnly = $isRescanOnly
        LogPath = $logPath
        Dev14LifecycleLease = $env:NBA2K22_DEV14_LIFECYCLE_LEASE
    }
    $request | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $requestPath -Encoding UTF8

    $workerCommand = '& ' + (ConvertTo-PowerShellLiteral $PSCommandPath) + ' -Worker -RequestPath ' + (ConvertTo-PowerShellLiteral $requestPath)
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($workerCommand))
    $argumentLine = '-NoProfile -ExecutionPolicy Bypass -EncodedCommand ' + $encodedCommand

    try {
        $elevated = Start-Process -FilePath 'powershell.exe' -Verb RunAs -WindowStyle Hidden -ArgumentList $argumentLine -Wait -PassThru
    } finally {
        Remove-Item -LiteralPath $requestPath -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path -LiteralPath $logPath -PathType Leaf) {
        Get-Content -LiteralPath $logPath -Tail 80
    }
    Write-Output ("Admin data task exit code: {0}" -f $elevated.ExitCode)
    Write-Output ("Log: {0}" -f $logPath)
    exit $elevated.ExitCode
}

$relativeScript = if ($isRescanOnly) { 'src\verify_address_rescan.py' } elseif ($isCalibrationOnly) { 'src\address_calibrator.py' } else { 'src\run_monthly_cycle.py' }
$scriptPath = Join-Path $projectRoot $relativeScript
$pythonArgs = @($scriptPath)
if ($isRescanOnly) {
    $pythonArgs += @('--save-id', $SaveId)
} elseif (-not $isCalibrationOnly) {
    $pythonArgs += @('--save-id', $SaveId, '--season', [string]$Season, '--month', [string]$Month, '--name', $Name)
    if ($Notes) { $pythonArgs += @('--notes', $Notes) }
}

Set-Location -LiteralPath $projectRoot
$utf8Encoding = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8Encoding
$OutputEncoding = $utf8Encoding
$env:PYTHONIOENCODING = 'utf-8'
"administrator_token=True; mode=$(if ($isRescanOnly) { 'forced_rescan_check' } elseif ($isCalibrationOnly) { 'calibration' } else { 'monthly_capture' }); runner_pid=$PID; timestamp=$([DateTime]::UtcNow.ToString('o'))" |
    Set-Content -LiteralPath $logPath -Encoding Unicode
& $pythonExe @pythonArgs *>&1 | Tee-Object -FilePath $logPath -Append
$pythonExitCode = $LASTEXITCODE
exit $pythonExitCode
