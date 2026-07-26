[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('post','read','gc')]
    [string]$Command,
    [string]$LaneInstanceId = '',
    [string]$WriterLaneInstanceId = '',
    [ValidateSet('C0','C1_shadow','all')]
    [string]$MessageClass = 'C0',
    [string]$Body = '',
    [string]$EventId = '',
    [string]$TaskId = '',
    [ValidateSet('claude_desktop','chatgpt_web','codex_desktop','codex_cli','claude_code_cli')]
    [string]$EnvironmentClass = 'codex_desktop',
    [ValidateSet('human_speaker','foreground_review_and_task_dispatch','backend_execution_and_handoff')]
    [string]$ProtocolRole = 'backend_execution_and_handoff',
    [ValidateSet('foreground_planner','foreground_independent_reviewer','backend_executor')]
    [string]$LoadProfileId = 'backend_executor',
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')),
    [string]$LocalLaneRoot = (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'CityState/local_lanes'),
    [ValidatePattern('^$|^[0-9a-f]{40}$')]
    [string]$LaneProtocolEpoch = '',
    [ValidatePattern('^$|^[0-9a-f]{40}$')]
    [string]$BaseReviewHead = '',
    [int]$AfterSequence = 0,
    [int]$RetentionDays = 30
)

$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Assert-LaneId([string]$Value, [string]$Label) {
    if ($Value -notmatch '^[a-z][a-z0-9_-]*-[0-9a-f]{6,32}$') {
        throw "$Label is not a valid lane_instance_id"
    }
}

function Read-JsonFile([string]$Path, [string]$Label) {
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) }
    catch { throw "$Label must be JSON-compatible YAML: $($_.Exception.Message)" }
}

function Write-AtomicJson([string]$Path, $Value) {
    $directory = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    $temporary = Join-Path $directory ('.tmp-' + [Guid]::NewGuid().ToString('N'))
    $json = $Value | ConvertTo-Json -Depth 30
    [System.IO.File]::WriteAllText($temporary, $json + "`n", $Utf8NoBom)
    try { [System.IO.File]::Move($temporary, $Path) }
    finally { if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force } }
}

function Get-CurrentEpoch {
    if ($LaneProtocolEpoch) { return $LaneProtocolEpoch }
    $epoch = Read-JsonFile (Join-Path $PSScriptRoot 'lane_epoch.yml') 'lane epoch'
    if ($epoch.release_binding_status -ne 'bound' -or
        $epoch.lane_required_after_protocol_release_head -notmatch '^[0-9a-f]{40}$') {
        throw 'lane protocol epoch is not bound'
    }
    return [string]$epoch.lane_required_after_protocol_release_head
}

function Get-BaseReviewHead {
    if ($BaseReviewHead) { return $BaseReviewHead }
    $value = (& git -C $RepositoryRoot rev-parse refs/remotes/origin/ai/review/latest 2>$null)
    if ($LASTEXITCODE -ne 0 -or $value -notmatch '^[0-9a-f]{40}$') {
        throw 'base review head is unavailable; pass -BaseReviewHead explicitly'
    }
    return $value.Trim()
}

function Assert-OwnLane([string]$Target, [string]$Writer) {
    Assert-LaneId $Target 'LaneInstanceId'
    Assert-LaneId $Writer 'WriterLaneInstanceId'
    if ($Target -ne $Writer) { throw 'cross-lane write rejected: writer differs from target lane' }
}

function Invoke-WithLaneLock([string]$LanePath, [scriptblock]$Action) {
    [System.IO.Directory]::CreateDirectory($LanePath) | Out-Null
    $lockPath = Join-Path $LanePath '.write.lock'
    $stream = $null
    for ($attempt = 0; $attempt -lt 100 -and $null -eq $stream; $attempt++) {
        try {
            $stream = New-Object System.IO.FileStream(
                $lockPath,
                [System.IO.FileMode]::CreateNew,
                [System.IO.FileAccess]::Write,
                [System.IO.FileShare]::None
            )
        }
        catch [System.IO.IOException] { Start-Sleep -Milliseconds 50 }
    }
    if ($null -eq $stream) { throw 'local lane write lock is busy' }
    try { & $Action }
    finally {
        $stream.Dispose()
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }
}

$root = [System.IO.Path]::GetFullPath($LocalLaneRoot)
$epoch = Get-CurrentEpoch

if ($Command -eq 'post') {
    if (-not $WriterLaneInstanceId) { $WriterLaneInstanceId = $LaneInstanceId }
    Assert-OwnLane $LaneInstanceId $WriterLaneInstanceId
    if ($MessageClass -eq 'all') { throw 'post requires MessageClass C0 or C1_shadow' }
    if ($MessageClass -eq 'C1_shadow' -and -not $TaskId) { throw 'C1_shadow requires TaskId' }
    $lanePath = Join-Path $root $LaneInstanceId
    Invoke-WithLaneLock $lanePath {
        $eventsPath = Join-Path $lanePath 'events'
        [System.IO.Directory]::CreateDirectory($eventsPath) | Out-Null
        $metaPath = Join-Path $lanePath 'meta.yml'
        if (Test-Path -LiteralPath $metaPath) {
            $meta = Read-JsonFile $metaPath 'lane metadata'
            if ($meta.lane_instance_id -ne $LaneInstanceId -or $meta.transport -ne 'local') {
                throw 'cross-lane write rejected: existing metadata does not belong to this local lane'
            }
            if ($meta.lane_protocol_epoch -ne $epoch) { throw 'local lane metadata uses a stale epoch' }
        }
        else {
            $meta = [ordered]@{
                lane_instance_id = $LaneInstanceId
                environment_class = $EnvironmentClass
                protocol_role = $ProtocolRole
                load_profile_id = $LoadProfileId
                opened_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
                lane_protocol_epoch = $epoch
                transport = 'local'
            }
            Write-AtomicJson $metaPath $meta
        }

        $sequencePath = Join-Path $lanePath 'seq'
        $lastSequence = 0
        if (Test-Path -LiteralPath $sequencePath) {
            $rawSequence = (Get-Content -LiteralPath $sequencePath -Raw).Trim()
            if ($rawSequence -notmatch '^\d+$') { throw 'local lane seq is invalid' }
            $lastSequence = [int]$rawSequence
        }
        $maxArtifactSequence = 0
        Get-ChildItem -LiteralPath $eventsPath -File -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.Name -match '^(\d+)(?:\.lane-envelope)?\.yml$') {
                $maxArtifactSequence = [Math]::Max($maxArtifactSequence, [int]$Matches[1])
            }
        }
        $sequence = [Math]::Max($lastSequence, $maxArtifactSequence) + 1
        $stem = '{0:D3}' -f $sequence
        $writtenAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        if (-not $EventId) { $EventId = "local-$LaneInstanceId-$stem" }
        $reviewHead = Get-BaseReviewHead
        $envelope = [ordered]@{
            lane_instance_id = $LaneInstanceId
            environment_class = $EnvironmentClass
            protocol_role = $ProtocolRole
            load_profile_id = $LoadProfileId
            message_seq = $sequence
            lane_protocol_epoch = $epoch
            base_review_head = $reviewHead
            written_at = $writtenAt
        }
        $event = [ordered]@{
            schema_version = 'citystate.local_lane_message.v1'
            transport = 'local'
            authoritative = $false
            authority_boundary = 'C0_coordination_or_C1_shadow_only'
            message_class = $MessageClass
            lane_instance_id = $LaneInstanceId
            message_seq = $sequence
            event_id = $EventId
            task_id = $(if ($TaskId) { $TaskId } else { $null })
            written_at = $writtenAt
            body = $Body
        }
        Write-AtomicJson (Join-Path $eventsPath ($stem + '.lane-envelope.yml')) $envelope
        Write-AtomicJson (Join-Path $eventsPath ($stem + '.yml')) $event
        $seqTemporary = $sequencePath + '.tmp-' + [Guid]::NewGuid().ToString('N')
        [System.IO.File]::WriteAllText($seqTemporary, [string]$sequence + "`n", $Utf8NoBom)
        Move-Item -LiteralPath $seqTemporary -Destination $sequencePath -Force
        [ordered]@{
            status = 'posted'; transport = 'local'; authoritative = $false
            lane_instance_id = $LaneInstanceId; message_seq = $sequence
            message_class = $MessageClass; event_id = $EventId
        } | ConvertTo-Json -Compress
    }
    exit 0
}

if ($Command -eq 'read') {
    if ($LaneInstanceId) { Assert-LaneId $LaneInstanceId 'LaneInstanceId' }
    $laneDirectories = if ($LaneInstanceId) {
        @(Get-Item -LiteralPath (Join-Path $root $LaneInstanceId) -ErrorAction SilentlyContinue)
    } else {
        @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue | Sort-Object Name)
    }
    $messages = @()
    foreach ($lane in $laneDirectories) {
        if ($null -eq $lane) { continue }
        Assert-LaneId $lane.Name 'local lane directory'
        $metaPath = Join-Path $lane.FullName 'meta.yml'
        if (-not (Test-Path -LiteralPath $metaPath)) { continue }
        $meta = Read-JsonFile $metaPath 'lane metadata'
        if ($meta.transport -ne 'local' -or $meta.lane_instance_id -ne $lane.Name) {
            throw 'cross-lane write rejected: local metadata differs from directory'
        }
        if ($meta.lane_protocol_epoch -ne $epoch) { continue }
        $eventsPath = Join-Path $lane.FullName 'events'
        foreach ($file in @(Get-ChildItem -LiteralPath $eventsPath -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^(\d+)\.yml$' } | Sort-Object { [int]$_.BaseName })) {
            $sequence = [int]$file.BaseName
            if ($sequence -le $AfterSequence) { continue }
            $envelopePath = Join-Path $eventsPath ($file.BaseName + '.lane-envelope.yml')
            if (-not (Test-Path -LiteralPath $envelopePath)) { throw 'local event lacks its envelope' }
            $event = Read-JsonFile $file.FullName 'local event'
            $envelope = Read-JsonFile $envelopePath 'local envelope'
            if ($event.transport -ne 'local' -or $event.authoritative -ne $false -or
                $event.message_class -notin @('C0','C1_shadow')) {
                throw 'local event violates the C0/C1-shadow authority boundary'
            }
            if ($event.lane_instance_id -ne $lane.Name -or $envelope.lane_instance_id -ne $lane.Name) {
                throw 'cross-lane write rejected: local event or envelope differs from directory'
            }
            if ([int]$event.message_seq -ne $sequence -or [int]$envelope.message_seq -ne $sequence) {
                throw 'local lane sequence differs from filename'
            }
            if ($envelope.lane_protocol_epoch -ne $epoch) { continue }
            if ($MessageClass -ne 'all' -and $event.message_class -ne $MessageClass) { continue }
            $messages += $event
        }
    }
    ConvertTo-Json -InputObject @($messages | Sort-Object lane_instance_id, message_seq) -Depth 30
    exit 0
}

if (-not $WriterLaneInstanceId) { $WriterLaneInstanceId = $LaneInstanceId }
Assert-OwnLane $LaneInstanceId $WriterLaneInstanceId
if ($RetentionDays -lt 1) { throw 'RetentionDays must be at least 1' }
$lanePath = Join-Path $root $LaneInstanceId
$removed = 0
if (Test-Path -LiteralPath $lanePath) {
    $removed = Invoke-WithLaneLock $lanePath {
        $removedInLock = 0
        $eventsPath = Join-Path $lanePath 'events'
        $cutoff = (Get-Date).ToUniversalTime().AddDays(-$RetentionDays)
        foreach ($file in @(Get-ChildItem -LiteralPath $eventsPath -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^(\d+)\.yml$' })) {
            $event = Read-JsonFile $file.FullName 'local event'
            $writtenAt = [DateTime]::MinValue
            if (-not [DateTime]::TryParse([string]$event.written_at, [ref]$writtenAt)) {
                throw 'local event written_at is invalid'
            }
            if ($writtenAt.ToUniversalTime() -lt $cutoff) {
                $envelopePath = Join-Path $eventsPath ($file.BaseName + '.lane-envelope.yml')
                Remove-Item -LiteralPath $file.FullName -Force
                if (Test-Path -LiteralPath $envelopePath) { Remove-Item -LiteralPath $envelopePath -Force }
                $removedInLock++
            }
        }
        foreach ($temporary in @(Get-ChildItem -LiteralPath $lanePath -Recurse -File -Filter '.tmp-*' -ErrorAction SilentlyContinue)) {
            if ($temporary.LastWriteTimeUtc -lt $cutoff) { Remove-Item -LiteralPath $temporary.FullName -Force }
        }
        $removedInLock
    }
}
[ordered]@{ status = 'gc_complete'; lane_instance_id = $LaneInstanceId; removed = $removed; retention_days = $RetentionDays } |
    ConvertTo-Json -Compress
