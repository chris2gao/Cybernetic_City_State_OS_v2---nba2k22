[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")),
    [string]$LaneRoot = (Join-Path $PSScriptRoot "."),
    [string]$StatePath = (Join-Path $PSScriptRoot "../STATE.yml"),
    [ValidatePattern('^$|^[0-9a-f]{40}$')]
    [string]$CurrentLaneProtocolEpoch = '',
    [ValidateSet('foreground_review_and_task_dispatch')]
    [string]$WriterProtocolRole = 'foreground_review_and_task_dispatch',
    [string]$StateStatus = 'neutral_baseline',
    [string]$ActiveTask = '',
    [string[]]$LegacyTaskIds = @()
)

$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Assert-SafeToken([string]$Value, [string]$Label) {
    if ($Value -notmatch '^[A-Za-z0-9._/-]+$') { throw "$Label contains an unsafe value" }
}

function Invoke-GitBytes([string]$ObjectName) {
    if ($ObjectName -notmatch '^[0-9a-f]{40}:[A-Za-z0-9._/-]+$') {
        throw 'git object contains an unsafe value'
    }
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'git'
    $psi.Arguments = 'show ' + $ObjectName
    $psi.WorkingDirectory = $RepositoryRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stream = New-Object System.IO.MemoryStream
    $process.StandardOutput.BaseStream.CopyTo($stream)
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { throw "git show failed: $stderr" }
    return $stream.ToArray()
}

function Get-Sha256([byte[]]$Bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return (($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString('x2') }) -join '') }
    finally { $sha.Dispose() }
}

function Read-JsonBytes([byte[]]$Bytes, [string]$Label) {
    try { return ($Utf8NoBom.GetString($Bytes) | ConvertFrom-Json) }
    catch { throw "$Label must be JSON-compatible YAML: $($_.Exception.Message)" }
}

function Resolve-ImmutableRef($Reference, [string]$Label) {
    if ($null -eq $Reference -or $Reference.kind -ne 'git_blob' -or
        $Reference.commit -notmatch '^[0-9a-f]{40}$' -or
        $Reference.path -notmatch '^[A-Za-z0-9._/-]+$' -or
        $Reference.content_sha256 -notmatch '^[0-9a-f]{64}$') {
        throw "$Label is not a complete immutable git_blob reference"
    }
    $bytes = Invoke-GitBytes ($Reference.commit + ':' + $Reference.path)
    $digest = Get-Sha256 $bytes
    if ($digest -ne $Reference.content_sha256) { throw "$Label digest mismatch" }
    return @{ Bytes = $bytes; Digest = $digest }
}

$head = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -notmatch '^[0-9a-f]{40}$') { throw 'HEAD is unavailable' }
if (-not $CurrentLaneProtocolEpoch) {
    $epochPath = Join-Path $PSScriptRoot 'lane_epoch.yml'
    $epoch = Get-Content -LiteralPath $epochPath -Raw | ConvertFrom-Json
    if ($epoch.release_binding_status -ne 'bound') { throw 'lane protocol epoch is not bound' }
    $CurrentLaneProtocolEpoch = [string]$epoch.lane_required_after_protocol_release_head
}
if ($CurrentLaneProtocolEpoch -notmatch '^[0-9a-f]{40}$') { throw 'current lane protocol epoch is invalid' }

$inputs = @()
$seenEvents = @{}
$backendTasks = @{}
$laneDirectories = @(Get-ChildItem -LiteralPath $LaneRoot -Directory -ErrorAction SilentlyContinue |
    Sort-Object Name)

foreach ($lane in $laneDirectories) {
    $eventsPath = Join-Path $lane.FullName 'events'
    if (-not (Test-Path -LiteralPath $eventsPath)) { continue }
    $events = @(Get-ChildItem -LiteralPath $eventsPath -File | Where-Object {
        $_.Name -match '^([0-9]+)\.yml$'
    } | Sort-Object { [int]$_.BaseName })
    if ($events.Count -eq 0) { continue }
    $eventFile = $events[-1]
    $seq = [int]$eventFile.BaseName
    $eventRelative = '.ai/lanes/' + $lane.Name + '/events/' + $eventFile.Name
    & git -C $RepositoryRoot diff --quiet HEAD -- $eventRelative
    if ($LASTEXITCODE -ne 0) { throw "lane event is not immutable at HEAD: $eventRelative" }
    & git -C $RepositoryRoot ls-files --error-unmatch -- $eventRelative *> $null
    if ($LASTEXITCODE -ne 0) { throw "lane event is not tracked: $eventRelative" }
    $eventBytes = Invoke-GitBytes ($head + ':' + $eventRelative)
    $event = Read-JsonBytes $eventBytes $eventRelative
    if (-not $event.event_id -or -not $event.task_id) { throw "lane event lacks event_id/task_id: $eventRelative" }
    if ($seenEvents.ContainsKey([string]$event.event_id)) { throw 'the same event was written to more than one lane' }

    $envelopeRefs = @($event.required_refs | Where-Object { $_.path -match '\.lane-envelope\.yml$' })
    if ($envelopeRefs.Count -ne 1) { throw "lane event must reference exactly one lane envelope: $eventRelative" }
    $envelopeResolved = Resolve-ImmutableRef $envelopeRefs[0] 'lane envelope ref'
    $envelope = Read-JsonBytes $envelopeResolved.Bytes $envelopeRefs[0].path

    if ($envelope.lane_instance_id -ne $lane.Name) { throw 'cross-lane write rejected: envelope lane differs from directory' }
    if ([int]$envelope.message_seq -ne $seq) { throw 'lane sequence differs from event filename' }
    if ($envelope.protocol_role -notin @('human_speaker','foreground_review_and_task_dispatch','backend_execution_and_handoff')) { throw 'lane protocol role is invalid' }
    if ($envelope.environment_class -notin @('claude_desktop','chatgpt_web','codex_desktop','codex_cli','claude_code_cli')) { throw 'lane environment class is invalid' }
    if ($envelope.load_profile_id -notin @('foreground_planner','foreground_independent_reviewer','backend_executor','math_mentor_teacher')) { throw 'lane load profile is invalid' }
    if ($envelope.lane_protocol_epoch -ne $CurrentLaneProtocolEpoch) { continue }
    if ($envelope.base_review_head -notmatch '^[0-9a-f]{40}$') { throw 'base_review_head is invalid' }
    & git -C $RepositoryRoot cat-file -e ($envelope.base_review_head + '^{commit}')
    if ($LASTEXITCODE -ne 0) { throw 'base_review_head is not a commit object' }

    $taskId = [string]$event.task_id
    if ($LegacyTaskIds -contains $taskId) { throw 'mixed legacy/lane delivery for one task is forbidden' }
    if ($envelope.protocol_role -eq 'backend_execution_and_handoff') {
        if ($backendTasks.ContainsKey($taskId)) { throw 'two backend lanes claimed the same task' }
        $backendTasks[$taskId] = $lane.Name
    }
    $seenEvents[[string]$event.event_id] = $lane.Name
    $inputs += [ordered]@{
        lane_instance_id = $lane.Name
        message_seq = $seq
        task_id = $taskId
        event_ref = [ordered]@{
            kind = 'git_blob'; commit = $head; path = $eventRelative
            content_sha256 = (Get-Sha256 $eventBytes)
        }
        envelope_ref = [ordered]@{
            kind = 'git_blob'; commit = [string]$envelopeRefs[0].commit
            path = [string]$envelopeRefs[0].path
            content_sha256 = [string]$envelopeRefs[0].content_sha256
        }
    }
}

$state = [ordered]@{
    protocol_version = 'v0.3-core'
    status = $StateStatus
    active_task = $(if ($ActiveTask) { $ActiveTask } else { $null })
    review_branch = 'ai/review/latest'
    review_branch_head = $head
    lane_required_after_protocol_release_head = $CurrentLaneProtocolEpoch
    lane_inputs = @($inputs | Sort-Object lane_instance_id, message_seq)
    human_gate = 'not_required'
}
$json = $state | ConvertTo-Json -Depth 20
$target = [System.IO.Path]::GetFullPath($StatePath)
$temporary = $target + '.tmp-' + [Guid]::NewGuid().ToString('N')
[System.IO.File]::WriteAllText($temporary, $json + "`n", $Utf8NoBom)
Move-Item -LiteralPath $temporary -Destination $target -Force
Write-Output ("lane_inputs=" + $inputs.Count)
