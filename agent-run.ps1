[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$TaskId,
    [Parameter(Mandatory = $true)][ValidateSet('codex', 'claude')][string]$Engine,
    [string]$Tier = 'citystate_t1',
    [string]$Resume,
    [switch]$Wait,
    [switch]$TestMode,
    [string]$TestEngineScript,
    [int]$HeartbeatSeconds = 30,
    [string]$RepoRoot,
    [string]$WorktreeRoot,
    [string]$LedgerRoot
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot '.ai\runs\Runner.Common.ps1')

$taskLock = $null
$branchLock = $null
$lockOwnerPid = $PID
$workerStarted = $false

try {
    Assert-SafeTaskId -TaskId $TaskId
    if ($HeartbeatSeconds -lt 1 -or $HeartbeatSeconds -gt 300) { throw 'HeartbeatSeconds must be between 1 and 300' }
    if (-not [string]::IsNullOrWhiteSpace($Resume) -and $Resume -notmatch '^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$') { throw 'Resume must be an explicit safe session id' }
    if (-not $TestMode -and (-not [string]::IsNullOrWhiteSpace($TestEngineScript) -or -not [string]::IsNullOrWhiteSpace($RepoRoot) -or -not [string]::IsNullOrWhiteSpace($WorktreeRoot) -or -not [string]::IsNullOrWhiteSpace($LedgerRoot))) {
        throw 'RepoRoot, WorktreeRoot, LedgerRoot, and TestEngineScript overrides require -TestMode'
    }

    if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
        $gitRoot = Invoke-GitText -RepoRoot $scriptRoot -Arguments @('rev-parse', '--show-toplevel')
        $RepoRoot = $gitRoot.Text
    }
    $RepoRoot = [IO.Path]::GetFullPath($RepoRoot)
    $packet = Get-TaskPacket -RepoRoot $RepoRoot -TaskId $TaskId
    if (-not (Test-EngineAssigned -AssignedExecutor $packet.AssignedExecutor -Engine $Engine)) {
        throw "Engine '$Engine' is not the unique assigned executor: $($packet.AssignedExecutor)"
    }
    $baseRef = Assert-ExactBase -RepoRoot $RepoRoot -BaseBranch $packet.BaseBranch -ExpectedHead $packet.BaseHead

    if ([string]::IsNullOrWhiteSpace($WorktreeRoot)) {
        $repoKey = Get-RepositoryKey -RepoRoot $RepoRoot
        $WorktreeRoot = Join-Path (Join-Path $env:LOCALAPPDATA 'CityState\agent_runs') $repoKey
    }
    if ([string]::IsNullOrWhiteSpace($LedgerRoot)) {
        $LedgerRoot = Join-Path $env:LOCALAPPDATA 'CityState\token_ledger\runs'
    }
    $WorktreeRoot = [IO.Path]::GetFullPath($WorktreeRoot)
    $runDirectory = Join-Path (Join-Path $RepoRoot '.ai\runs') $TaskId
    $worktree = Join-Path (Join-Path $WorktreeRoot $TaskId) 'worktree'
    $taskLock = Join-Path $runDirectory 'LOCK'
    $branchLock = Get-BranchLockPath -RepoRoot $RepoRoot -WorkBranch $packet.WorkBranch -WorktreeRoot $WorktreeRoot
    if (-not (Test-Path -LiteralPath $runDirectory)) { New-Item -ItemType Directory -Path $runDirectory -Force | Out-Null }

    Remove-StaleLockOrThrow -Path $taskLock -Label 'task'
    Remove-StaleLockOrThrow -Path $branchLock -Label 'branch writer'
    $started = Get-UtcTimestamp
    $lockValue = [ordered]@{ owner = $env:USERNAME; pid = $PID; engine = $Engine; task_id = $TaskId; work_branch = $packet.WorkBranch; started_at = $started }
    New-ExclusiveJsonLock -Path $branchLock -Value $lockValue
    try { New-ExclusiveJsonLock -Path $taskLock -Value $lockValue } catch { Remove-LockIfOwned -Path $branchLock -OwnerPid $PID; throw }

    $worktreeExists = Test-Path -LiteralPath $worktree
    if ($worktreeExists) {
        if ([string]::IsNullOrWhiteSpace($Resume)) { throw "Worktree already exists; use an explicit -Resume id for reload: $worktree" }
        $check = Invoke-GitText -RepoRoot $worktree -Arguments @('rev-parse', '--is-inside-work-tree') -AllowFailure
        if ($check.ExitCode -ne 0) { throw "Existing recovery path is not a worktree: $worktree" }
    } else {
        $parent = Split-Path -Parent $worktree
        if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        $branchExists = Invoke-GitText -RepoRoot $RepoRoot -Arguments @('show-ref', '--verify', '--quiet', ('refs/heads/' + $packet.WorkBranch)) -AllowFailure
        if ($branchExists.ExitCode -eq 0) {
            if ([string]::IsNullOrWhiteSpace($Resume)) { throw "Work branch already exists; an explicit -Resume id is required: $($packet.WorkBranch)" }
            [void](Invoke-GitText -RepoRoot $RepoRoot -Arguments @('worktree', 'add', $worktree, $packet.WorkBranch))
        } else {
            [void](Invoke-GitText -RepoRoot $RepoRoot -Arguments @('worktree', 'add', '-b', $packet.WorkBranch, $worktree, $packet.BaseHead))
        }
    }

    $runLog = Join-Path $runDirectory 'run.log'
    $stderrLog = Join-Path $runDirectory 'stderr.log'
    $validationLog = Join-Path $runDirectory 'validation.log'
    $statusPath = Join-Path $runDirectory 'status.json'
    $sessionPath = Join-Path $runDirectory 'session.json'
    $finalReport = Join-Path $runDirectory 'final-report.md'
    foreach ($path in @($runLog, $stderrLog, $validationLog)) { Write-AtomicUtf8 -Path $path -Content '' }
    $session = [ordered]@{
        schema_version = 'citystate.agent_runner_session.v1'; task_id = $TaskId; task_packet = $packet.Path
        assigned_executor = $packet.AssignedExecutor; definition_of_done = $packet.DefinitionOfDone
        stop_rules = $packet.StopRules; allowed_paths = $packet.AllowedPaths; forbidden_paths = $packet.ForbiddenPaths
        validation_commands = $packet.ValidationCommands; work_branch = $packet.WorkBranch
        branch_lock = $branchLock; task_lock = $taskLock; run_log = $runLog; stderr_log = $stderrLog
        validation_log = $validationLog; final_report = $finalReport; ledger_root = $LedgerRoot
        worker_pid = $null; launched_at = $started; resume_requested = -not [string]::IsNullOrWhiteSpace($Resume)
    }
    Write-AtomicJson -Path $sessionPath -Value $session
    $status = [ordered]@{
        task_id = $TaskId; engine = $Engine; tier = $Tier; state = 'starting'; started_at = $started
        pid = 0; session_id = $(if ([string]::IsNullOrWhiteSpace($Resume)) { $null } else { $Resume })
        worktree = $worktree; base_branch = $packet.BaseBranch; base_head = $packet.BaseHead
        last_heartbeat = $started; exit_code = $null; handoff_ref = $null
    }
    Write-AtomicJson -Path $statusPath -Value $status

    $engineExecutable = $null
    $engineArguments = @()
    if ($TestMode) {
        if ([string]::IsNullOrWhiteSpace($TestEngineScript) -or -not (Test-Path -LiteralPath $TestEngineScript -PathType Leaf)) { throw '-TestMode requires an existing -TestEngineScript' }
        $engineExecutable = (Get-Command powershell.exe -ErrorAction Stop).Source
        $engineArguments = @('-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', [IO.Path]::GetFullPath($TestEngineScript), '-Worktree', $worktree)
    } elseif ($Engine -eq 'codex') {
        $engineExecutable = (Get-Command codex -ErrorAction Stop).Source
        $pointerPrompt = "Execute task $TaskId from $($packet.Path). Work only in $worktree and return concise evidence."
        if ([string]::IsNullOrWhiteSpace($Resume)) {
            $engineArguments = @('exec', '--json', '-p', $Tier, '-C', $worktree, $pointerPrompt)
        } else {
            $engineArguments = @('exec', 'resume', $Resume, '--json', '-p', $Tier, '-C', $worktree, $pointerPrompt)
        }
    } else {
        $engineExecutable = (Get-Command claude -ErrorAction Stop).Source
        $pointerPrompt = "Execute task $TaskId from $($packet.Path). Work only in $worktree and return concise evidence."
        $engineArguments = @('-p', $pointerPrompt, '--output-format', 'stream-json')
        if (-not [string]::IsNullOrWhiteSpace($Resume)) { $engineArguments += @('--resume', $Resume) }
    }

    $argumentJson = $engineArguments | ConvertTo-Json -Compress
    $argumentBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($argumentJson))
    $workerScript = Join-Path $scriptRoot '.ai\runs\runner-worker.ps1'
    $workerArguments = @(
        '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', $workerScript,
        '-RepoRoot', $RepoRoot, '-RunDirectory', $runDirectory, '-Worktree', $worktree,
        '-TaskId', $TaskId, '-Engine', $Engine, '-Tier', $Tier, '-BaseBranch', $packet.BaseBranch,
        '-BaseHead', $packet.BaseHead, '-EngineExecutable', $engineExecutable,
        '-EngineArgumentsBase64', $argumentBase64, '-HeartbeatSeconds', [string]$HeartbeatSeconds,
        '-TaskLock', $taskLock, '-BranchLock', $branchLock, '-LedgerRoot', $LedgerRoot
    )
    if (-not [string]::IsNullOrWhiteSpace($Resume)) { $workerArguments += @('-Resume', $Resume) }
    $worker = Start-Process -FilePath (Get-Command powershell.exe -ErrorAction Stop).Source -ArgumentList (ConvertTo-WindowsCommandLine $workerArguments) -WorkingDirectory $RepoRoot -PassThru -WindowStyle Hidden
    $workerStarted = $true
    $lockOwnerPid = [int]$worker.Id
    $lockValue.pid = $lockOwnerPid
    Write-AtomicJson -Path $taskLock -Value $lockValue
    Write-AtomicJson -Path $branchLock -Value $lockValue
    $session.worker_pid = $lockOwnerPid
    Write-AtomicJson -Path $sessionPath -Value $session

    $launchResult = [ordered]@{ task_id = $TaskId; worker_pid = $lockOwnerPid; state = 'starting'; status = $statusPath; worktree = $worktree }
    if ($Wait) {
        Wait-Process -Id $lockOwnerPid
        $finalStatus = Read-JsonFile -Path $statusPath
        $finalStatus | ConvertTo-Json -Depth 10
        if ($null -eq $finalStatus -or $finalStatus.state -notin @('done', 'stopped')) { exit 1 }
    } else {
        $launchResult | ConvertTo-Json -Depth 10
    }
} catch {
    if (-not $workerStarted) {
        Remove-LockIfOwned -Path $taskLock -OwnerPid $lockOwnerPid
        Remove-LockIfOwned -Path $branchLock -OwnerPid $lockOwnerPid
    }
    Write-Error $_
    exit 1
}
