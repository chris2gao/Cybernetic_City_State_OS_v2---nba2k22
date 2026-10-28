param([Parameter(Mandatory=$true)][string]$Directory,[Parameter(Mandatory=$true)][string]$NodePath,[Parameter(Mandatory=$true)][string]$ReaPath,[int]$DurationMs=15000)
$ErrorActionPreference='Stop'
$principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Next-task caller must start its authorized runtime in an administrator session'}
$manifest=Get-Content -LiteralPath (Join-Path $Directory 'request.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if(-not $manifest.authorization_ref){throw 'Explicit next-task execution scope reference required'}
$script=Join-Path $Directory 'program.js'
if((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.script_sha256){throw 'Prepared program hash changed'}
if(Test-Path -LiteralPath (Join-Path $Directory 'evidence.json')){throw 'Do not replay existing output; unknown native results require investigation, not retry'}
$games=@(Get-Process NBA2K22 -ErrorAction Stop)
if($games.Count -ne 1){throw 'Exactly one actual NBA2K22 process required'}
if($manifest.expected_pid -and $games[0].Id -ne [int]$manifest.expected_pid){throw 'Approved game process changed; do not attach another process'}
$hash=(Get-FileHash -LiteralPath $games[0].MainModule.FileName -Algorithm SHA256).Hash.ToLowerInvariant()
if($hash -ne '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5' -or $hash -ne $manifest.game_build_sha256){throw 'Pinned PC22 build mismatch'}
@{pid=$games[0].Id;exe_sha256=$hash;script_sha256=$manifest.script_sha256;administrator=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Directory 'target.json') -Encoding UTF8
& $NodePath $ReaPath instrument-with-frida attach $games[0].Id --script-file $script --duration-ms $DurationMs --format json 2> (Join-Path $Directory 'rea-stderr.log') | Set-Content -LiteralPath (Join-Path $Directory 'evidence.json') -Encoding UTF8
exit $LASTEXITCODE
