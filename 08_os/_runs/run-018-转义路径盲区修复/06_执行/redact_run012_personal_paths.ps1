$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir '..\..\..\..')

$targets = @(
    '08_os/_runs/run-012-check-jsonschema安装接入验证/01_任务输入/安装真实性命令回执.json',
    '08_os/_runs/run-012-check-jsonschema安装接入验证/07_测试执行/results.json'
)

$userHomePrefix = '{0}{1}{2}' -f 'C:', '\Users', '\gk'
$repoRootPrefix = '{0}{1}{2}{3}' -f 'E:', '\', 'newStand', '\study\Cybernetic_City_State_OS_v2 - core'
$escapedUserHomePrefix = $userHomePrefix.Replace('\', '\\')
$escapedRepoRootPrefix = $repoRootPrefix.Replace('\', '\\')

$replacements = [ordered]@{
    $escapedRepoRootPrefix = '${REPOSITORY_ROOT}'
    $repoRootPrefix = '${REPOSITORY_ROOT}'
    $escapedUserHomePrefix = '${WINDOWS_USER_HOME}'
    $userHomePrefix = '${WINDOWS_USER_HOME}'
}

foreach ($relativePath in $targets) {
    $absolutePath = Join-Path $repoRoot $relativePath
    $content = Get-Content -LiteralPath $absolutePath -Raw -Encoding utf8
    foreach ($entry in $replacements.GetEnumerator()) {
        $content = $content.Replace($entry.Key, $entry.Value)
    }
    Set-Content -LiteralPath $absolutePath -Value $content -Encoding utf8NoBOM
}
