[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$TaskId,
    [string]$RepoRoot
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot '.ai\runs\Runner.Common.ps1')

Assert-SafeTaskId -TaskId $TaskId
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Invoke-GitText -RepoRoot $scriptRoot -Arguments @('rev-parse', '--show-toplevel')).Text
}
$runDirectory = Join-Path (Join-Path ([IO.Path]::GetFullPath($RepoRoot)) '.ai\runs') $TaskId
$statusPath = Join-Path $runDirectory 'status.json'
$sessionPath = Join-Path $runDirectory 'session.json'
$taskLock = Join-Path $runDirectory 'LOCK'
$status = Read-JsonFile -Path $statusPath
$session = Read-JsonFile -Path $sessionPath
if ($null -eq $status) { throw "No status exists for task $TaskId" }
if ($null -eq $session) { throw "Session evidence is missing for task $TaskId; stop fails closed" }

if (Test-ProcessAlive -PidValue $status.pid) { Stop-ProcessTree -ParentPid ([int]$status.pid) }
$lock = $null
try { $lock = Read-JsonFile -Path $taskLock } catch { }
if ($null -ne $lock -and (Test-ProcessAlive -PidValue $lock.pid)) { Stop-ProcessTree -ParentPid ([int]$lock.pid) }
$status.state = 'stopped'
$status.last_heartbeat = Get-UtcTimestamp
if ($null -eq $status.exit_code) { $status.exit_code = 130 }
$status.handoff_ref = ('.ai/runs/' + $TaskId + '/final-report.md')
Write-AtomicJson -Path $statusPath -Value $status
$workerPid = 0
if ($null -ne $lock -and [int]::TryParse([string]$lock.pid, [ref]$workerPid)) {
    Remove-LockIfOwned -Path $taskLock -OwnerPid $workerPid
    Remove-LockIfOwned -Path $session.branch_lock -OwnerPid $workerPid
}
$toolBytes = 0L
foreach ($path in @($session.run_log, $session.stderr_log, $session.validation_log)) {
    if (-not [string]::IsNullOrWhiteSpace([string]$path) -and (Test-Path -LiteralPath $path)) { $toolBytes += (Get-Item -LiteralPath $path).Length }
}
$wallSeconds = 0.0
try { $wallSeconds = ([DateTime]::UtcNow - [DateTime]::Parse($status.started_at).ToUniversalTime()).TotalSeconds } catch { }
$tokenRecord = Write-TokenProfileRecord -LedgerRoot $session.ledger_root -TaskId $TaskId -Engine $status.engine -Tier $status.tier -SessionMode $(if ($null -eq $status.session_id) { 'cold' } else { 'explicit_id_resume' }) -ValidationResult 'stopped' -WallSeconds $wallSeconds -ToolOutputBytes $toolBytes -RepairAttempts 0
Write-AtomicUtf8 -Path $session.validation_log -Content "Stopped by agent-stop.ps1; validation not run.`n"
Write-FinalRunReport -Path $session.final_report -Status $status -Session $session -TokenRecord $tokenRecord -ValidationExit 130
[ordered]@{ task_id = $TaskId; state = 'stopped'; exit_code = $status.exit_code; lock_present = (Test-Path -LiteralPath $taskLock) } | ConvertTo-Json
