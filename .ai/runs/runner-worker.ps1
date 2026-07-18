[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$RunDirectory,
    [Parameter(Mandatory = $true)][string]$Worktree,
    [Parameter(Mandatory = $true)][string]$TaskId,
    [Parameter(Mandatory = $true)][ValidateSet('codex', 'claude')][string]$Engine,
    [Parameter(Mandatory = $true)][string]$Tier,
    [Parameter(Mandatory = $true)][string]$BaseBranch,
    [Parameter(Mandatory = $true)][string]$BaseHead,
    [Parameter(Mandatory = $true)][string]$EngineExecutable,
    [Parameter(Mandatory = $true)][string]$EngineArgumentsBase64,
    [Parameter(Mandatory = $true)][int]$HeartbeatSeconds,
    [Parameter(Mandatory = $true)][string]$TaskLock,
    [Parameter(Mandatory = $true)][string]$BranchLock,
    [Parameter(Mandatory = $true)][string]$LedgerRoot,
    [string]$Resume
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
. (Join-Path $RepoRoot '.ai\runs\Runner.Common.ps1')

$statusPath = Join-Path $RunDirectory 'status.json'
$sessionPath = Join-Path $RunDirectory 'session.json'
$runLog = Join-Path $RunDirectory 'run.log'
$stderrLog = Join-Path $RunDirectory 'stderr.log'
$validationLog = Join-Path $RunDirectory 'validation.log'
$finalReport = Join-Path $RunDirectory 'final-report.md'
$process = $null
$engineExit = -1
$validationExit = 0
$startedClock = [Diagnostics.Stopwatch]::StartNew()
$tokenRecord = $null
$stdoutTask = $null
$stderrTask = $null
$session = $null
$status = $null

try {
    $session = Read-JsonFile -Path $sessionPath
    $status = Read-JsonFile -Path $statusPath
    $engineArgumentsJson = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($EngineArgumentsBase64))
    # Windows PowerShell 5.1 emits a JSON array as one nested Object[] value;
    # an outer @() therefore turns the entire command line into one argument.
    $engineArguments = [string[]]($engineArgumentsJson | ConvertFrom-Json)
    $startInfo = New-Object Diagnostics.ProcessStartInfo
    $startInfo.FileName = $EngineExecutable
    $startInfo.Arguments = ConvertTo-WindowsCommandLine -Arguments $engineArguments
    $startInfo.WorkingDirectory = $Worktree
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $startInfo
    if (-not $process.Start()) { throw 'Engine process did not start' }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $status.pid = [int]$process.Id
    $status.state = 'running'
    $status.last_heartbeat = Get-UtcTimestamp
    Write-AtomicJson -Path $statusPath -Value $status

    while (-not $process.HasExited) {
        Start-Sleep -Seconds $HeartbeatSeconds
        $process.Refresh()
        $current = Read-JsonFile -Path $statusPath
        if ($null -ne $current -and $current.state -eq 'stopped') { break }
        $status.last_heartbeat = Get-UtcTimestamp
        Write-AtomicJson -Path $statusPath -Value $status
    }
    if (-not $process.HasExited) { Stop-ProcessTree -ParentPid ([int]$process.Id); $process.WaitForExit() }
    $process.WaitForExit()
    $engineExit = [int]$process.ExitCode
    $stdout = $stdoutTask.Result
    $stderr = $stderrTask.Result
    Write-AtomicUtf8 -Path $runLog -Content ((Protect-LogText -Text $stdout) + "`n")
    Write-AtomicUtf8 -Path $stderrLog -Content ((Protect-LogText -Text $stderr) + "`n")
    $detectedSession = Get-SessionIdFromOutput -Text $stdout
    if ($null -ne $detectedSession) { $status.session_id = $detectedSession }
    elseif (-not [string]::IsNullOrWhiteSpace($Resume)) { $status.session_id = $Resume }
    Stop-ProcessTree -ParentPid ([int]$process.Id)

    $current = Read-JsonFile -Path $statusPath
    if ($null -ne $current -and $current.state -eq 'stopped') {
        $status.state = 'stopped'
        $validationExit = 130
        Write-AtomicUtf8 -Path $validationLog -Content "Stopped by agent-stop.ps1; validation not run.`n"
    } else {
        $status.state = 'validating'
        $status.last_heartbeat = Get-UtcTimestamp
        Write-AtomicJson -Path $statusPath -Value $status
        $validationLines = New-Object Collections.Generic.List[string]
        if ($session.validation_commands.Count -eq 0) {
            [void]$validationLines.Add('No validation_commands declared in the task packet.')
        } else {
            foreach ($command in @($session.validation_commands)) {
                [void]$validationLines.Add(('> ' + $command))
                $previousErrorActionPreference = $ErrorActionPreference
                try {
                    $ErrorActionPreference = 'Continue'
                    $output = @(& powershell.exe -NoProfile -NonInteractive -Command $command 2>&1)
                    $code = $LASTEXITCODE
                }
                finally {
                    $ErrorActionPreference = $previousErrorActionPreference
                }
                [void]$validationLines.Add((Protect-LogText -Text ($output -join "`n")))
                [void]$validationLines.Add(('exit_code=' + $code))
                if ($code -ne 0 -and $validationExit -eq 0) { $validationExit = $code }
            }
        }
        Write-AtomicUtf8 -Path $validationLog -Content (($validationLines -join "`n") + "`n")
        if ($engineExit -eq 0 -and $validationExit -eq 0) { $status.state = 'done' } else { $status.state = 'failed' }
    }
    $status.exit_code = $engineExit
    $status.last_heartbeat = Get-UtcTimestamp
    $status.handoff_ref = ('.ai/runs/' + $TaskId + '/final-report.md')
    $toolBytes = 0L
    foreach ($path in @($runLog, $stderrLog, $validationLog)) { if (Test-Path -LiteralPath $path) { $toolBytes += (Get-Item -LiteralPath $path).Length } }
    $tokenRecord = Write-TokenProfileRecord -LedgerRoot $LedgerRoot -TaskId $TaskId -Engine $Engine -Tier $Tier -SessionMode $(if ([string]::IsNullOrWhiteSpace($Resume)) { 'cold' } else { 'explicit_id_resume' }) -ValidationResult $status.state -WallSeconds $startedClock.Elapsed.TotalSeconds -ToolOutputBytes $toolBytes -RepairAttempts 0
    Write-AtomicJson -Path $statusPath -Value $status
    Write-FinalRunReport -Path $finalReport -Status $status -Session $session -TokenRecord $tokenRecord -ValidationExit $validationExit
} catch {
    $failureText = $_ | Out-String
    try {
        if ($null -ne $process -and -not $process.HasExited) {
            Stop-ProcessTree -ParentPid ([int]$process.Id)
            $process.WaitForExit()
        }
        if ($null -eq $session) { $session = Read-JsonFile -Path $sessionPath }
        if ($null -eq $status) { $status = Read-JsonFile -Path $statusPath }
        if ($null -eq $status) {
            $status = [ordered]@{ task_id = $TaskId; engine = $Engine; tier = $Tier; state = 'failed'; started_at = Get-UtcTimestamp; pid = 0; session_id = $null; worktree = $Worktree; base_branch = $BaseBranch; base_head = $BaseHead; last_heartbeat = Get-UtcTimestamp; exit_code = -1; handoff_ref = $null }
        }
        $engineStdout = ''
        $engineStderr = ''
        if ($null -ne $stdoutTask -and $stdoutTask.IsCompleted) { $engineStdout = [string]$stdoutTask.Result }
        if ($null -ne $stderrTask -and $stderrTask.IsCompleted) { $engineStderr = [string]$stderrTask.Result }
        Write-AtomicUtf8 -Path $runLog -Content ((Protect-LogText -Text $engineStdout) + "`n")
        Write-AtomicUtf8 -Path $stderrLog -Content ((Protect-LogText -Text ($engineStderr + "`nSupervisor failure:`n" + $failureText)) + "`n")
        Write-AtomicUtf8 -Path $validationLog -Content "Supervisor failed before validation completed; validation_exit=-1.`n"
        $status.state = 'failed'; $status.exit_code = -1; $status.last_heartbeat = Get-UtcTimestamp
        $status.handoff_ref = ('.ai/runs/' + $TaskId + '/final-report.md')
        $toolBytes = 0L
        foreach ($path in @($runLog, $stderrLog, $validationLog)) { if (Test-Path -LiteralPath $path) { $toolBytes += (Get-Item -LiteralPath $path).Length } }
        if ($null -eq $tokenRecord) {
            $tokenRecord = Write-TokenProfileRecord -LedgerRoot $LedgerRoot -TaskId $TaskId -Engine $Engine -Tier $Tier -SessionMode $(if ([string]::IsNullOrWhiteSpace($Resume)) { 'cold' } else { 'explicit_id_resume' }) -ValidationResult 'failed' -WallSeconds $startedClock.Elapsed.TotalSeconds -ToolOutputBytes $toolBytes -RepairAttempts 0
        }
        Write-AtomicJson -Path $statusPath -Value $status
        if ($null -ne $session) { Write-FinalRunReport -Path $finalReport -Status $status -Session $session -TokenRecord $tokenRecord -ValidationExit -1 }
    } catch { }
} finally {
    if ($null -ne $process) { Stop-ProcessTree -ParentPid ([int]$process.Id) }
    Remove-LockIfOwned -Path $TaskLock -OwnerPid $PID
    Remove-LockIfOwned -Path $BranchLock -OwnerPid $PID
    $startedClock.Stop()
}
