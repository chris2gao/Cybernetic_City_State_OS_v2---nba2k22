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
$lockPath = Join-Path $runDirectory 'LOCK'
$status = Read-JsonFile -Path $statusPath
if ($null -eq $status) { throw "No status exists for task $TaskId" }
$heartbeatAge = $null
try { $heartbeatAge = [Math]::Round(([DateTime]::UtcNow - [DateTime]::Parse($status.last_heartbeat).ToUniversalTime()).TotalSeconds, 3) } catch { }
$result = [ordered]@{
    task_id = $status.task_id; state = $status.state; pid = $status.pid
    process_alive = Test-ProcessAlive -PidValue $status.pid
    last_heartbeat = $status.last_heartbeat; heartbeat_age_seconds = $heartbeatAge
    exit_code = $status.exit_code; session_id = $status.session_id
    lock_present = Test-Path -LiteralPath $lockPath; worktree = $status.worktree
}
$result | ConvertTo-Json -Depth 5
