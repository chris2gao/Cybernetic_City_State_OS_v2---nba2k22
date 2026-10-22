[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Request,
    [ValidateSet('plan','execute','verify')][string]$Phase = 'plan',
    [switch]$ApproveGameWrites,
    [switch]$RepairCounts,
    [switch]$Worker
)
$ErrorActionPreference = 'Stop'
if ($ApproveGameWrites.IsPresent -ne ($Phase -eq 'execute')) {
    throw 'ApproveGameWrites must be explicitly present for execute only.'
}
$requestFile = (Resolve-Path -LiteralPath $Request).Path
$projectDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$requestData = Get-Content -LiteralPath $requestFile -Raw -Encoding UTF8 | ConvertFrom-Json
$requestOutput = [string]$requestData.output
if (-not $requestOutput) {
    $requestId = if ($requestData.request_id) { [string]$requestData.request_id } else { [IO.Path]::GetFileNameWithoutExtension($requestFile) }
    $requestOutput = Join-Path (Join-Path '_exports\execution' ([string]$requestData.save_id)) $requestId
}
$outputDir = [IO.Path]::GetFullPath((Join-Path $projectDir $requestOutput))
$allowedDir = [IO.Path]::GetFullPath((Join-Path $projectDir '_exports\execution')) + [IO.Path]::DirectorySeparatorChar
if (-not $outputDir.StartsWith($allowedDir, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Output directory leaves _exports/execution.'
}
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
$logFile = Join-Path $outputDir ($Phase + '_console.log')
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    if ($Worker) { throw 'Elevated worker did not receive administrator token.' }
    $workerArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $PSCommandPath + '"'),'-Request',('"' + $requestFile + '"'),'-Phase',$Phase,'-Worker')
    if ($ApproveGameWrites) { $workerArgs += '-ApproveGameWrites' }
    if ($RepairCounts) { $workerArgs += '-RepairCounts' }
    $workerProcess = Start-Process -FilePath 'powershell.exe' -Verb RunAs -WindowStyle Hidden -ArgumentList $workerArgs -Wait -PassThru
    if (Test-Path -LiteralPath $logFile) { Get-Content -LiteralPath $logFile -Tail 8 -Encoding UTF8 }
    exit $workerProcess.ExitCode
}
$env:PYTHONIOENCODING = 'utf-8'
Set-Location -LiteralPath $projectDir
if ($RepairCounts -and $Phase -eq 'verify') { throw 'Count repair supports plan or execute only; re-run plan for a zero-write check.' }
$pythonArgs = if ($RepairCounts) {
    @((Join-Path $PSScriptRoot 'repair_approved_roster_counts.py'),'--request',$requestFile)
} else {
    @((Join-Path $PSScriptRoot 'execute_approved_trades.py'),'--request',$requestFile,'--phase',$Phase)
}
if ($ApproveGameWrites) { $pythonArgs += '--approve-game-writes' }
& python @pythonArgs *> $logFile
exit $LASTEXITCODE
