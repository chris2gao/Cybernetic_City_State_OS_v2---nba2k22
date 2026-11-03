param(
    [Parameter(Mandatory=$true)][string]$Batch,
    [Parameter(Mandatory=$true)][string]$Approval,
    [Parameter(Mandatory=$true)][string]$Runtime,
    [Parameter(Mandatory=$true)][string]$PythonPath
)
$ErrorActionPreference = 'Stop'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'This batch must be explicitly launched in an administrator session; no implicit elevation'
}
New-Item -ItemType Directory -Path $Runtime -Force | Out-Null
$script = Join-Path $PSScriptRoot 'validation_batch.py'
& $PythonPath -B -X utf8 $script execute-sequence --batch $Batch --approval $Approval --runtime $Runtime *> (Join-Path $Runtime 'sequence.log')
$code = $LASTEXITCODE
[ordered]@{exit_code=$code;finished_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Runtime 'launcher-finished.json') -Encoding UTF8
exit $code
