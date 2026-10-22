[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$')][string]$SaveId,
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')][string]$GameDate,
    [switch]$GameDateUnknown,
    [ValidateRange(2000,2100)][int]$Season = 2022,
    [ValidateRange(1,12)][int]$Month = 1,
    [ValidateSet('checkpoint','monthly_close','season_start','post_transaction','staff_change','roster_import','draft_pre','draft_post')][string]$Event = 'checkpoint',
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$')][string]$Name = 'CHECKPOINT',
    [switch]$GamesOnDateComplete,
    [switch]$Validation,
    [switch]$Publish,
    [switch]$NewWindow,
    [string]$LoadedSaveConfirmation
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if ($GameDate -and $GameDateUnknown) { throw 'Choose GameDate or explicit GameDateUnknown.' }
if (-not $GameDate -and -not $GameDateUnknown) { throw 'Provide GameDate or player-authorized GameDateUnknown.' }
if ($GameDate) { [DateTime]::ParseExact($GameDate, 'yyyy-MM-dd', [Globalization.CultureInfo]::InvariantCulture) | Out-Null }
if ($GameDateUnknown -and $GamesOnDateComplete) { throw 'GamesOnDateComplete requires an exact date.' }
if ($NewWindow) {
    $scriptLiteral = "'" + $PSCommandPath.Replace("'", "''") + "'"
    $dateArgument = if ($GameDateUnknown) { '-GameDateUnknown' } else { "-GameDate '$GameDate'" }
    $command = "& $scriptLiteral -SaveId '$SaveId' $dateArgument -Season $Season -Month $Month -Event '$Event' -Name '$Name'"
    if ($GamesOnDateComplete) { $command += ' -GamesOnDateComplete' }
    if ($Validation) { $command += ' -Validation' }
    if ($Publish) { $command += ' -Publish' }
    if ($LoadedSaveConfirmation) { $command += " -LoadedSaveConfirmation '$($LoadedSaveConfirmation.Replace("'", "''"))'" }
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    Write-Output 'Opening separate data-only terminal; waiting for its result.'
    $window = Start-Process -FilePath 'powershell.exe' -WindowStyle Normal -ArgumentList "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encoded" -Wait -PassThru
    Write-Output "Data-only terminal finished: PID $($window.Id); exit=$($window.ExitCode)"
    exit $window.ExitCode
}
# DEV14 managed careers hold one lifecycle lease across capture, audit, export
# and optional publication. The native pipeline and full-refresh policy remain.
$workspaceFile = Join-Path $projectRoot "database\saves\$SaveId\workspace.json"
if (((Test-Path -LiteralPath $workspaceFile) -or (Test-Path -LiteralPath (Join-Path $projectRoot 'database\active_save.json'))) -and -not $env:NBA2K22_DEV14_LIFECYCLE_LEASE) {
    if (-not $LoadedSaveConfirmation) { throw 'DEV14 managed update requires player-confirmed save_id:save_instance_id:generation_id via -LoadedSaveConfirmation.' }
    $forward = [Collections.Generic.List[string]]::new()
    foreach ($key in $PSBoundParameters.Keys) {
        if ($key -in @('SaveId','NewWindow','LoadedSaveConfirmation')) { continue }
        if ($PSBoundParameters[$key] -is [System.Management.Automation.SwitchParameter]) {
            if ($PSBoundParameters[$key]) { $forward.Add("-$key") }
        } else {
            $forward.Add("-$key")
            $forward.Add([string]$PSBoundParameters[$key])
        }
    }
    $forwardJson = ConvertTo-Json -InputObject @($forward.ToArray()) -Compress
    $forwardBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($forwardJson))
    $captureArguments = @('-B',(Join-Path $PSScriptRoot 'gm_state_io.py'),'capture','--career',$SaveId,
        '--approve-capture','--loaded-save-confirmation',$LoadedSaveConfirmation,'--capture-args-base64',$forwardBase64)
    if ($Publish) { $captureArguments += '--approve-publish' }
    & python @captureArguments
    exit $LASTEXITCODE
}
if ($env:NBA2K22_DEV14_LIFECYCLE_LEASE) {
    & python -B (Join-Path $PSScriptRoot 'gm_state_io.py') lease-check --career $SaveId
    if ($LASTEXITCODE -ne 0) { throw 'DEV14 active save lease invalid.' }
}
$mutex = [Threading.Mutex]::new($false, 'Local\NBA2K22_GM_DATA_UPDATE')
$acquired = $false
$transcriptStarted = $false
try {
    try { $acquired = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $acquired = $true }
    if (-not $acquired) { throw 'Another data update for this career is running.' }
    Set-Location -LiteralPath $projectRoot
    $jobLogDirectory = Join-Path $projectRoot "database\saves\$SaveId\job_logs"
    New-Item -ItemType Directory -Path $jobLogDirectory -Force | Out-Null
    $jobLog = Join-Path $jobLogDirectory ("update_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
    Start-Transcript -LiteralPath $jobLog | Out-Null
    $transcriptStarted = $true
    $utf8Encoding = [Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = $utf8Encoding
    $OutputEncoding = $utf8Encoding
    $env:PYTHONIOENCODING = 'utf-8'
    $context = [ordered]@{
        schema_version = 1
        career_id = $SaveId
        game_date = $(if ($GameDateUnknown) { $null } else { $GameDate })
        game_date_provenance = $(if ($GameDateUnknown) { 'PLAYER_AUTHORIZED_CURRENT_DATE_UNKNOWN' } else { 'USER_CONFIRMED' })
        trigger = 'PLAYER_INITIATED'
        event = $Event
        purpose = $(if ($Validation) { 'validation' } else { 'production' })
        month_closed = ($Event -eq 'monthly_close')
        games_on_date_complete = $(if ($GamesOnDateComplete) { $true } else { $null })
        capture_profile = 'full_verified_v1'
    }
    $encodedContext = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($context | ConvertTo-Json -Compress)))
    $notes = 'CAPTURE_CONTEXT_V1:' + $encodedContext
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'run_admin_data_capture.ps1') -SaveId $SaveId -Season $Season -Month $Month -Name $Name -Notes $notes
    if ($LASTEXITCODE -ne 0) { throw 'Capture/audit failed; export and publication stopped.' }
    $snapshot = "{0}-{1}_M{2:D2}_{3}" -f ($Season - 1), $Season, $Month, $Name
    & python 'src/export_web_gm.py' --save-id $SaveId --snapshot $snapshot
    if ($LASTEXITCODE -ne 0) { throw 'Web export failed; publication stopped.' }
    if ($Publish) {
        & python 'scripts/publish_web_snapshot.py' --save-id $SaveId
        if ($LASTEXITCODE -ne 0) { throw 'GitHub sync failed; local audited data remains available.' }
    }
    $displayGameDate = if ($GameDateUnknown) { 'GAME_DATE_UNKNOWN' } else { $GameDate }
    Write-Output "[PASS] Player-triggered data update complete: $SaveId / $displayGameDate / $snapshot"
    Write-Output 'DATA_READY_AWAITING_PLAYER: GM decisions and game execution require separate player triggers.'
} finally {
    if ($transcriptStarted) { Stop-Transcript | Out-Null }
    if ($acquired) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
