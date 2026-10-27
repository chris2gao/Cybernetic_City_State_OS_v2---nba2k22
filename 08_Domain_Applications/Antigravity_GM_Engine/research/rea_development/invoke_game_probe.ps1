param(
    [Parameter(Mandatory=$true)][string]$Script,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [ValidatePattern('^[a-z0-9-]+$')][string]$Tag = 'metadata',
    [ValidateRange(1,1500)][int]$DurationMs = 500
)
$ErrorActionPreference='Stop'
$principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Administrator required; launch this bounded script elevated'}
$scriptPath=(Resolve-Path -LiteralPath $Script).Path
$source=Get-Content -LiteralPath $scriptPath -Raw
if($source -match 'Interceptor\.|NativeFunction|NativeCallback|Memory\.patchCode|\.write(?:U|S|Byte|Pointer|Float|Double)|\.replace\('){throw 'Read-only recipe rejects mutation/call primitives; this is an accidental-use guard, not a JavaScript sandbox'}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputPath=(Resolve-Path -LiteralPath $OutputDirectory).Path
if(Test-Path -LiteralPath (Join-Path $outputPath ($Tag+'-evidence.json'))){throw 'Preserve prior evidence; use a fresh output tag'}
$games=@(Get-Process NBA2K22 -ErrorAction Stop)
if($games.Count -ne 1){throw 'Expected one NBA2K22 process'}
$exe=$games[0].MainModule.FileName
if($exe -ne 'E:\Games\NBA 2K22\NBA2K22.exe'){throw 'Unexpected executable path'}
$hash=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
if($hash -ne '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'){throw 'Pinned game build changed; rederive the probe first'}
@{utc=[DateTime]::UtcNow.ToString('o');pid=$games[0].Id;path=$exe;sha256=$hash;administrator=$true;script_sha256=(Get-FileHash -LiteralPath $scriptPath -Algorithm SHA256).Hash.ToLowerInvariant();duration_ms=$DurationMs} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputPath ($Tag+'-target.json')) -Encoding utf8
$timer=[Diagnostics.Stopwatch]::StartNew()
& 'C:\Program Files\nodejs\node.exe' 'C:\Users\gk\AppData\Roaming\npm\node_modules\rea-agents\scripts\rea.mjs' instrument-with-frida attach $games[0].Id --script-file $scriptPath --duration-ms $DurationMs --format json 2> (Join-Path $outputPath ($Tag+'-stderr.log')) | Set-Content -LiteralPath (Join-Path $outputPath ($Tag+'-evidence.json')) -Encoding utf8
$result=$LASTEXITCODE
$timer.Stop()
@{exit_code=$result;elapsed_ms=$timer.ElapsedMilliseconds;process_still_running=[bool](Get-Process -Id $games[0].Id -ErrorAction SilentlyContinue)} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputPath ($Tag+'-metrics.json')) -Encoding utf8
if($result -ne 0){throw ('REA exited '+$result)}
