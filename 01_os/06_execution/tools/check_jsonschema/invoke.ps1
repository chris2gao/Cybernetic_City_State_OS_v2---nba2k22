[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SchemaPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$InstancePath,

    [ValidateNotNullOrEmpty()]
    [string]$Executable = "check-jsonschema",

    [ValidatePattern("^[0-9]+\.[0-9]+\.[0-9]+$")]
    [string]$ExpectedVersion = "0.37.4",

    [ValidateNotNullOrEmpty()]
    [string]$PythonExecutable = "python"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Stop-CheckJsonschemaInvocation {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $true)]
        [int]$ExitCode
    )

    [Console]::Error.WriteLine("check-jsonschema wrapper: $Message")
    exit $ExitCode
}

if (-not (Test-Path -LiteralPath $SchemaPath -PathType Leaf)) {
    Stop-CheckJsonschemaInvocation -Message "schema file not found: $SchemaPath" -ExitCode 66
}

if (-not (Test-Path -LiteralPath $InstancePath -PathType Leaf)) {
    Stop-CheckJsonschemaInvocation -Message "instance file not found: $InstancePath" -ExitCode 66
}

function Resolve-InvocationExecutable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    $looksLikePath = [IO.Path]::IsPathRooted($Value) -or
        $Value.Contains([IO.Path]::DirectorySeparatorChar) -or
        $Value.Contains([IO.Path]::AltDirectorySeparatorChar)
    if ($looksLikePath) {
        if (-not (Test-Path -LiteralPath $Value -PathType Leaf)) {
            Stop-CheckJsonschemaInvocation -Message "$Label not found: $Value" -ExitCode 69
        }
        return (Resolve-Path -LiteralPath $Value).Path
    }

    $command = Get-Command -Name $Value -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $command) {
        Stop-CheckJsonschemaInvocation -Message "$Label unavailable on PATH: $Value" -ExitCode 69
    }
    return $command.Source
}

$resolvedSchema = (Resolve-Path -LiteralPath $SchemaPath).Path
$resolvedInstance = (Resolve-Path -LiteralPath $InstancePath).Path
$resolvedPython = Resolve-InvocationExecutable -Value $PythonExecutable -Label "python executable"
$inspector = Join-Path $PSScriptRoot "inspect_schema_refs.py"
if (-not (Test-Path -LiteralPath $inspector -PathType Leaf)) {
    Stop-CheckJsonschemaInvocation -Message "schema reference inspector not found" -ExitCode 69
}

$preflightOutput = @(& $resolvedPython $inspector $resolvedSchema 2>&1)
$preflightExitCode = $LASTEXITCODE
if ($preflightExitCode -ne 0) {
    foreach ($line in $preflightOutput) {
        [Console]::Error.WriteLine([string]$line)
    }
    exit 65
}

$resolvedExecutable = Resolve-InvocationExecutable -Value $Executable -Label "executable"
$versionOutput = @(& $resolvedExecutable --version 2>&1)
$versionExitCode = $LASTEXITCODE
$versionText = (($versionOutput | ForEach-Object { [string]$_ }) -join "`n").Trim()
if ($versionExitCode -ne 0) {
    Stop-CheckJsonschemaInvocation `
        -Message "version probe failed with exit ${versionExitCode}: $versionText" `
        -ExitCode 78
}

$versionMatch = [regex]::Match(
    $versionText,
    "^check-jsonschema, version (?<version>[0-9]+\.[0-9]+\.[0-9]+)$"
)
if (-not $versionMatch.Success) {
    Stop-CheckJsonschemaInvocation `
        -Message "unparseable version output: $versionText" `
        -ExitCode 78
}

$actualVersion = $versionMatch.Groups["version"].Value
if ($actualVersion -ne $ExpectedVersion) {
    Stop-CheckJsonschemaInvocation `
        -Message "version mismatch: expected $ExpectedVersion, got $actualVersion" `
        -ExitCode 78
}

& $resolvedExecutable --schemafile $resolvedSchema $resolvedInstance
$toolExitCode = $LASTEXITCODE

if ($null -eq $toolExitCode) {
    Stop-CheckJsonschemaInvocation -Message "tool returned no process exit code" -ExitCode 70
}

exit [int]$toolExitCode
