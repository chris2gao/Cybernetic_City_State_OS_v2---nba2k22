[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SchemaPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$InstancePath,

    [ValidateNotNullOrEmpty()]
    [string]$Executable = "check-jsonschema"
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

$resolvedExecutable = $null
$looksLikePath = [IO.Path]::IsPathRooted($Executable) -or
    $Executable.Contains([IO.Path]::DirectorySeparatorChar) -or
    $Executable.Contains([IO.Path]::AltDirectorySeparatorChar)

if ($looksLikePath) {
    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        Stop-CheckJsonschemaInvocation -Message "executable not found: $Executable" -ExitCode 69
    }
    $resolvedExecutable = (Resolve-Path -LiteralPath $Executable).Path
}
else {
    $command = Get-Command -Name $Executable -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $command) {
        Stop-CheckJsonschemaInvocation -Message "executable unavailable on PATH: $Executable" -ExitCode 69
    }
    $resolvedExecutable = $command.Source
}

$resolvedSchema = (Resolve-Path -LiteralPath $SchemaPath).Path
$resolvedInstance = (Resolve-Path -LiteralPath $InstancePath).Path

& $resolvedExecutable --schemafile $resolvedSchema $resolvedInstance
$toolExitCode = $LASTEXITCODE

if ($null -eq $toolExitCode) {
    Stop-CheckJsonschemaInvocation -Message "tool returned no process exit code" -ExitCode 70
}

exit [int]$toolExitCode
