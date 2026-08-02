$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir '..\..\..\..')
$validator = Join-Path $repoRoot '08_os\06_execution\validators\personal_paths\validate.py'
$config = Join-Path $repoRoot '08_os\06_execution\validators\personal_paths\patterns.json'
$probeRelativePath = '08_os/_runs/run-016-转义路径盲区修复/06_执行/_blindness_probe_before_fix.txt'
$probePath = Join-Path $repoRoot $probeRelativePath

$windowsDrive = 'C:'
$workspaceDrive = 'E:'
$userSegments = @('\Users', '\gk')
$workspaceSegments = @('\', 'newStand')
$escapedUserHome = '{0}{1}{2}' -f $windowsDrive, ($userSegments[0] -replace '\\', '\\\\'), ($userSegments[1] -replace '\\', '\\\\')
$forwardSlashUserHome = '{0}/Users/gk' -f $windowsDrive
$lowercaseUserHome = '{0}{1}{2}' -f $windowsDrive.ToLowerInvariant(), '\users', '\gk'
$escapedWorkspaceRoot = '{0}{1}{2}' -f $workspaceDrive, ($workspaceSegments[0] -replace '\\', '\\\\'), $workspaceSegments[1]

$probeLines = @(
    ('{0}\x' -f $escapedUserHome),
    ('{0}/y' -f $forwardSlashUserHome),
    ('{0}\z' -f $lowercaseUserHome),
    ('{0}\w' -f $escapedWorkspaceRoot)
)

Set-Content -LiteralPath $probePath -Value $probeLines -Encoding utf8
try {
    $base = (git -C $repoRoot rev-parse HEAD).Trim()
    $output = py $validator --repo-root $repoRoot --config $config --mode changed --base $base --summary-only $probeRelativePath 2>&1
    $exitCode = $LASTEXITCODE
    [pscustomobject]@{
        probe_path = $probeRelativePath
        base = $base
        exit_code = $exitCode
        stdout = $output
    } | ConvertTo-Json -Depth 4
}
finally {
    Remove-Item -LiteralPath $probePath -ErrorAction SilentlyContinue
}
