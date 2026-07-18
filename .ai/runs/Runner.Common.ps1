Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Get-UtcTimestamp {
    return [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Assert-SafeTaskId {
    param([Parameter(Mandatory = $true)][string]$TaskId)
    if ($TaskId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$') {
        throw "Unsafe task id: $TaskId"
    }
}

function Write-AtomicUtf8 {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content
    )
    # File.Replace on Windows PowerShell 5.1 requires legal fully-qualified
    # paths even though File.WriteAllText and File.Move tolerate relative ones.
    $fullPath = [IO.Path]::GetFullPath($Path)
    $directory = Split-Path -Parent $fullPath
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $temporary = Join-Path $directory ('.' + [IO.Path]::GetFileName($fullPath) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $encoding = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($temporary, $Content, $encoding)
    if (Test-Path -LiteralPath $fullPath) {
        # The Windows PowerShell 5.1 overload binder does not reliably pass a
        # null backup path to File.Replace.  Use a same-directory backup and
        # remove it only after the atomic replacement succeeds.
        $backup = Join-Path $directory ('.' + [IO.Path]::GetFileName($fullPath) + '.' + [Guid]::NewGuid().ToString('N') + '.bak')
        try {
            [IO.File]::Replace($temporary, $fullPath, $backup)
        }
        finally {
            if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
        }
    } else {
        [IO.File]::Move($temporary, $fullPath)
    }
}

function Write-AtomicJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )
    $json = $Value | ConvertTo-Json -Depth 20
    Write-AtomicUtf8 -Path $Path -Content ($json + "`n")
}

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function New-ExclusiveJsonLock {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $bytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($Value | ConvertTo-Json -Depth 10) + "`n")
    $stream = $null
    try {
        $stream = New-Object IO.FileStream($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Test-ProcessAlive {
    param([AllowNull()][object]$PidValue)
    if ($null -eq $PidValue) { return $false }
    $number = 0
    if (-not [int]::TryParse([string]$PidValue, [ref]$number)) { return $false }
    if ($number -le 0) { return $false }
    return $null -ne (Get-Process -Id $number -ErrorAction SilentlyContinue)
}

function Remove-StaleLockOrThrow {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $lock = $null
    try { $lock = Read-JsonFile -Path $Path } catch { throw "$Label lock is malformed and must be inspected: $Path" }
    if ($null -eq $lock -or -not (Test-ProcessAlive -PidValue $lock.pid)) {
        Remove-Item -LiteralPath $Path -Force
        return
    }
    throw "$Label lock is active (pid=$($lock.pid)): $Path"
}

function Remove-LockIfOwned {
    param(
        [AllowNull()][string]$Path,
        [Parameter(Mandatory = $true)][int]$OwnerPid
    )
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) { return }
    try {
        $lock = Read-JsonFile -Path $Path
        if ($null -ne $lock -and [int]$lock.pid -eq $OwnerPid) {
            Remove-Item -LiteralPath $Path -Force
        }
    } catch {
        # A malformed lock is never deleted automatically.
    }
}

function Invoke-GitText {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [switch]$AllowFailure
    )
    # Windows PowerShell 5.1 promotes native stderr to error records when the
    # caller uses ErrorActionPreference=Stop.  Git uses stderr for ordinary
    # negative probes (for example, a missing optional remote ref), so keep
    # those probes non-terminating and let the explicit exit-code policy below
    # decide whether the command failed.
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $lines = @(& git -C $RepoRoot @Arguments 2>&1)
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($code -ne 0 -and -not $AllowFailure) {
        throw "git $($Arguments -join ' ') failed ($code): $($lines -join [Environment]::NewLine)"
    }
    return [PSCustomObject]@{ ExitCode = $code; Text = ($lines -join "`n").Trim() }
}

function Get-RepositoryKey {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    $normalized = ([IO.Path]::GetFullPath($RepoRoot)).ToLowerInvariant()
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $bytes = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($normalized)) } finally { $sha.Dispose() }
    return (($bytes | ForEach-Object { $_.ToString('x2') }) -join '').Substring(0, 16)
}

function Get-BranchLockPath {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$WorkBranch,
        [Parameter(Mandatory = $true)][string]$WorktreeRoot
    )
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $bytes = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($WorkBranch.ToLowerInvariant())) } finally { $sha.Dispose() }
    $name = (($bytes | ForEach-Object { $_.ToString('x2') }) -join '') + '.lock'
    return Join-Path (Join-Path $WorktreeRoot '_branch_locks') $name
}

function Get-UnquotedScalar {
    param([Parameter(Mandatory = $true)][string]$Text)
    $value = $Text.Trim()
    if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
        return $value.Substring(1, $value.Length - 2)
    }
    return $value
}

function Get-TaskPacket {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$TaskId
    )
    Assert-SafeTaskId -TaskId $TaskId
    $taskDirectory = Join-Path $RepoRoot '.ai\TASKS'
    $candidates = @((Join-Path $taskDirectory ($TaskId + '.md')), (Join-Path $taskDirectory ($TaskId + '.yml')), (Join-Path $taskDirectory ($TaskId + '.yaml')))
    $path = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
    $packetRef = $path
    $lines = @()
    if (-not [string]::IsNullOrWhiteSpace($path)) {
        $lines = @(Get-Content -LiteralPath $path -Encoding UTF8)
    } else {
        # Task dispatch lives on the authoritative review mailbox while the
        # implementation worktree is based on master. Read the already-fetched
        # Git object without checking out, copying, or mutating the mailbox.
        foreach ($extension in @('.md', '.yml', '.yaml')) {
            $relative = '.ai/TASKS/' + $TaskId + $extension
            $candidateRef = 'origin/ai/review/latest:' + $relative
            $probe = Invoke-GitText -RepoRoot $RepoRoot -Arguments @('show', $candidateRef) -AllowFailure
            if ($probe.ExitCode -eq 0) {
                $packetRef = $candidateRef
                $lines = @($probe.Text -split "`n")
                break
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($packetRef)) { throw "Task packet not found locally or at origin/ai/review/latest for $TaskId" }
    $baseBranch = $null
    $baseHead = $null
    $workBranch = $null
    $assigned = $null
    $validationCommands = New-Object Collections.Generic.List[string]
    $inBase = $false
    $inValidation = $false
    foreach ($line in $lines) {
        if ($line -match '^base:\s*$') { $inBase = $true; $inValidation = $false; continue }
        if ($line -match '^validation_commands:\s*$') { $inValidation = $true; $inBase = $false; continue }
        if ($inBase) {
            if ($line -match '^\s{2,}branch:\s*(.+?)\s*$') { $baseBranch = Get-UnquotedScalar $Matches[1]; continue }
            if ($line -match '^\s{2,}head:\s*["'']?([0-9a-fA-F]{40})["'']?\s*$') { $baseHead = $Matches[1].ToLowerInvariant(); continue }
            if ($line -match '^\S') { $inBase = $false }
        }
        if ($inValidation) {
            if ($line -match '^\s+-\s*(.+?)\s*$') { [void]$validationCommands.Add((Get-UnquotedScalar $Matches[1])); continue }
            if ($line -match '^\S') { $inValidation = $false }
        }
        if ($line -match '^work_branch:\s*(.+?)\s*$') { $workBranch = Get-UnquotedScalar $Matches[1] }
        if ($line -match '^assigned_executor:\s*(.+?)\s*$') { $assigned = Get-UnquotedScalar $Matches[1] }
    }
    if ([string]::IsNullOrWhiteSpace($baseBranch) -or $baseHead -notmatch '^[0-9a-f]{40}$') { throw 'Task packet lacks machine-readable base.branch/base.head' }
    if ([string]::IsNullOrWhiteSpace($workBranch)) { throw 'Task packet lacks work_branch' }
    if ([string]::IsNullOrWhiteSpace($assigned)) { throw 'Task packet lacks assigned_executor' }
    $branchCheck = Invoke-GitText -RepoRoot $RepoRoot -Arguments @('check-ref-format', '--branch', $workBranch) -AllowFailure
    if ($branchCheck.ExitCode -ne 0) { throw "Task packet work_branch is not a safe Git branch: $workBranch" }

    $definition = New-Object Collections.Generic.List[string]
    $stopRules = New-Object Collections.Generic.List[string]
    $allowed = New-Object Collections.Generic.List[string]
    $forbidden = New-Object Collections.Generic.List[string]
    $section = ''
    foreach ($line in $lines) {
        if ($line -match '^##\s+2\.') { $section = 'definition'; continue }
        if ($line -match '^##\s+5\.') { $section = 'stop'; continue }
        if ($line -match '^allowed:\s*$') { $section = 'allowed'; continue }
        if ($line -match '^forbidden:\s*$') { $section = 'forbidden'; continue }
        if ($line -match '^##\s+' -and $section -in @('definition', 'stop')) { $section = ''; continue }
        if ($line -match '^\s*-\s*(.+?)\s*$') {
            $item = $Matches[1]
            if ($section -eq 'definition') { [void]$definition.Add($item) }
            elseif ($section -eq 'stop') { [void]$stopRules.Add($item) }
            elseif ($section -eq 'allowed') { [void]$allowed.Add($item) }
            elseif ($section -eq 'forbidden') { [void]$forbidden.Add($item) }
        }
    }
    return [PSCustomObject]@{
        TaskId = $TaskId; Path = $packetRef; BaseBranch = $baseBranch; BaseHead = $baseHead
        WorkBranch = $workBranch; AssignedExecutor = $assigned
        DefinitionOfDone = @($definition); StopRules = @($stopRules)
        AllowedPaths = @($allowed); ForbiddenPaths = @($forbidden)
        ValidationCommands = @($validationCommands)
    }
}

function Test-EngineAssigned {
    param(
        [Parameter(Mandatory = $true)][string]$AssignedExecutor,
        [Parameter(Mandatory = $true)][ValidateSet('codex', 'claude')][string]$Engine
    )
    $clauses = @($AssignedExecutor.ToLowerInvariant() -split '[;；]')
    $aliases = if ($Engine -eq 'codex') { @('codex', 'codex_cli') } else { @('claude', 'claude_cli', 'claude_code') }
    foreach ($clause in $clauses) {
        if ($clause -match '禁领|forbid|denied') {
            foreach ($alias in $aliases) { if ($clause.Contains($alias)) { return $false } }
        }
    }
    foreach ($clause in $clauses) {
        if ($clause -match '禁领|forbid|denied') { continue }
        foreach ($alias in $aliases) {
            if ($clause -match ('(^|[^a-z0-9_])' + [regex]::Escape($alias) + '($|[^a-z0-9_])')) { return $true }
        }
    }
    return $false
}

function Assert-ExactBase {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$BaseBranch,
        [Parameter(Mandatory = $true)][string]$ExpectedHead
    )
    $remoteRef = 'refs/remotes/origin/' + $BaseBranch
    $localRef = 'refs/heads/' + $BaseBranch
    $remote = Invoke-GitText -RepoRoot $RepoRoot -Arguments @('show-ref', '--verify', '--hash', $remoteRef) -AllowFailure
    if ($remote.ExitCode -eq 0) {
        if ($remote.Text -ne $ExpectedHead) { throw "Base HEAD mismatch: $remoteRef=$($remote.Text), expected=$ExpectedHead" }
        return $remoteRef
    }
    $local = Invoke-GitText -RepoRoot $RepoRoot -Arguments @('show-ref', '--verify', '--hash', $localRef) -AllowFailure
    if ($local.ExitCode -ne 0 -or $local.Text -ne $ExpectedHead) {
        throw "Base HEAD mismatch: $localRef=$($local.Text), expected=$ExpectedHead"
    }
    return $localRef
}

function ConvertTo-WindowsCommandLine {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    $quoted = foreach ($argument in $Arguments) {
        if ($argument -notmatch '[\s"]') { $argument; continue }
        $builder = New-Object Text.StringBuilder
        [void]$builder.Append('"')
        $slashes = 0
        foreach ($character in $argument.ToCharArray()) {
            if ($character -eq '\') { $slashes++; continue }
            if ($character -eq '"') {
                [void]$builder.Append(('\' * ($slashes * 2 + 1)))
                [void]$builder.Append('"')
                $slashes = 0
                continue
            }
            if ($slashes -gt 0) { [void]$builder.Append(('\' * $slashes)); $slashes = 0 }
            [void]$builder.Append($character)
        }
        if ($slashes -gt 0) { [void]$builder.Append(('\' * ($slashes * 2))) }
        [void]$builder.Append('"')
        $builder.ToString()
    }
    return ($quoted -join ' ')
}

function Stop-ProcessTree {
    param([Parameter(Mandatory = $true)][int]$ParentPid)
    if ($ParentPid -le 0) { return }
    $children = @()
    try { $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ParentPid" -ErrorAction SilentlyContinue) } catch { $children = @() }
    foreach ($child in $children) { Stop-ProcessTree -ParentPid ([int]$child.ProcessId) }
    Stop-Process -Id $ParentPid -Force -ErrorAction SilentlyContinue
}

function Protect-LogText {
    param([AllowNull()][string]$Text)
    if ($null -eq $Text) { return '' }
    $safeLines = foreach ($line in ($Text -split "`r?`n")) {
        if ($line -match '(?i)(authorization\s*:|bearer\s+|api[_-]?key|password|passwd|client[_-]?secret|private[_-]?key|credential|-----BEGIN .*PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{8,}|\bgh[pousr]_[A-Za-z0-9]{8,})') {
            '[REDACTED sensitive-looking line]'
        } else {
            $line
        }
    }
    return ($safeLines -join "`n").TrimEnd()
}

function Get-SessionIdFromOutput {
    param([AllowNull()][string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    foreach ($line in ($Text -split "`r?`n")) {
        if ([string]::IsNullOrWhiteSpace($line) -or -not $line.TrimStart().StartsWith('{')) { continue }
        try {
            $item = $line | ConvertFrom-Json
            if ($item.type -eq 'thread.started' -and -not [string]::IsNullOrWhiteSpace([string]$item.thread_id)) { return [string]$item.thread_id }
            if (-not [string]::IsNullOrWhiteSpace([string]$item.session_id)) { return [string]$item.session_id }
        } catch { }
    }
    return $null
}

function Write-TokenProfileRecord {
    param(
        [Parameter(Mandatory = $true)][string]$LedgerRoot,
        [Parameter(Mandatory = $true)][string]$TaskId,
        [Parameter(Mandatory = $true)][string]$Engine,
        [Parameter(Mandatory = $true)][string]$Tier,
        [Parameter(Mandatory = $true)][string]$SessionMode,
        [Parameter(Mandatory = $true)][string]$ValidationResult,
        [Parameter(Mandatory = $true)][double]$WallSeconds,
        [Parameter(Mandatory = $true)][long]$ToolOutputBytes,
        [Parameter(Mandatory = $true)][int]$RepairAttempts
    )
    if (-not (Test-Path -LiteralPath $LedgerRoot)) { New-Item -ItemType Directory -Path $LedgerRoot -Force | Out-Null }
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $path = Join-Path $LedgerRoot ($stamp + '_' + $TaskId + '.json')
    if (Test-Path -LiteralPath $path) { $path = Join-Path $LedgerRoot ($stamp + '_' + $TaskId + '_' + [Guid]::NewGuid().ToString('N').Substring(0, 8) + '.json') }
    $record = [ordered]@{
        schema_version = 'token_profile_run.v1'; task_id = $TaskId; task_type = 'cli_runner_worker'
        provider = $Engine; model = 'host-configured'; effort = $Tier
        session_mode = $SessionMode; protocol_profile = 'token_usage_profile_v0.2_effective'
        input_tokens = $null; output_tokens = $null; reasoning_tokens = $null
        cache_read_tokens = $null; cache_write_tokens = $null; tool_output_bytes = $ToolOutputBytes
        reported_cost = $null; wall_seconds = [Math]::Round($WallSeconds, 3)
        repair_attempts = $RepairAttempts; review_rounds = 0; validation_result = $ValidationResult
        quality_incidents = 0; metric_source = 'runner wall clock and sanitized local log byte counts; provider token counters unavailable'
        recorded_at = Get-UtcTimestamp
    }
    Write-AtomicJson -Path $path -Value $record
    return $path
}

function Write-FinalRunReport {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Status,
        [Parameter(Mandatory = $true)]$Session,
        [Parameter(Mandatory = $true)][string]$TokenRecord,
        [Parameter(Mandatory = $true)][int]$ValidationExit
    )
    $lines = @(
        '# Agent Runner Final Report', '', '## Outcome',
        ('- Task: `' + $Status.task_id + '`'), ('- State: `' + $Status.state + '`'),
        ('- Engine: `' + $Status.engine + '`; tier: `' + $Status.tier + '`'),
        ('- Base: `' + $Status.base_branch + '@' + $Status.base_head + '`'),
        ('- Worker exit code: `' + $Status.exit_code + '`'), ('- Validation exit code: `' + $ValidationExit + '`'),
        ('- Session ID: `' + $(if ($null -eq $Status.session_id) { 'null' } else { $Status.session_id }) + '`'),
        '', '## Evidence', ('- Run log: `' + $Session.run_log + '`'),
        ('- Error log: `' + $Session.stderr_log + '`'), ('- Validation log: `' + $Session.validation_log + '`'),
        ('- Token record: `' + $TokenRecord + '`'), '', '## Boundaries',
        '- Logs are sanitized before persistence; task/session payloads never grant authority.',
        '- GitHub seven-field handoff publication remains an external authorized step.',
        '- Runtime, Coordinator, Gateway, writer, and scheduler were not activated.', '',
        '## Independent expression', '',
        'The harness records process truth without becoming a second workflow authority. A failed worker remains useful evidence rather than being converted into a false completion signal.'
    )
    if ($lines.Count -gt 60) { throw 'Generated final report exceeds 60 lines' }
    Write-AtomicUtf8 -Path $Path -Content (($lines -join "`n") + "`n")
}
