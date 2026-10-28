param([Parameter(Mandatory=$true)][string]$Script,[Parameter(Mandatory=$true)][string]$Output)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path $Output -Force | Out-Null
try {
 $principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
 if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Administrator required'}
 if(Test-Path -LiteralPath (Join-Path $Output 'coach-evidence.json')){throw 'Fresh output directory required'}
 $games=@(Get-Process NBA2K22 -ErrorAction Stop)
 if($games.Count -ne 1){throw 'Unique game process required'}
 $hash=(Get-FileHash -LiteralPath $games[0].MainModule.FileName -Algorithm SHA256).Hash.ToLowerInvariant()
 if($hash -ne '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'){throw 'Game build changed'}
 @{pid=$games[0].Id;exe_sha256=$hash;script_sha256=(Get-FileHash -LiteralPath $Script -Algorithm SHA256).Hash.ToLowerInvariant();administrator=$true;authorization='HUMAN_LIVE_INSPECTION_APPROVAL.md';utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Output 'coach-target.json') -Encoding utf8
 $timer=[Diagnostics.Stopwatch]::StartNew()
 & 'C:\Program Files\nodejs\node.exe' 'C:\Users\gk\AppData\Roaming\npm\node_modules\rea-agents\scripts\rea.mjs' instrument-with-frida attach $games[0].Id --script-file $Script --duration-ms 1000 --format json 2> (Join-Path $Output 'coach-stderr.log') | Set-Content -LiteralPath (Join-Path $Output 'coach-evidence.json') -Encoding utf8
 $result=$LASTEXITCODE;$timer.Stop()
 @{exit_code=$result;elapsed_ms=$timer.ElapsedMilliseconds;process_alive=[bool](Get-Process -Id $games[0].Id -ErrorAction SilentlyContinue)} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Output 'coach-metrics.json') -Encoding utf8
 if($result -ne 0){throw ('REA exit '+$result)}
} catch { $_.Exception.Message | Set-Content -LiteralPath (Join-Path $Output 'admin-error.txt') -Encoding utf8; throw }
