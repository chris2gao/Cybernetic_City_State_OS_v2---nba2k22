param([Parameter(Mandatory=$true)][string]$Script,[Parameter(Mandatory=$true)][string]$Output,[int]$DurationMs=2200,[string]$ApprovalReceipt='')
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path $Output -Force | Out-Null
try {
 $principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
 if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Administrator required'}
 if(Test-Path -LiteralPath (Join-Path $Output 'evidence.json')){throw 'Fresh output directory required'}
 $scriptHash=(Get-FileHash -LiteralPath $Script -Algorithm SHA256).Hash.ToLowerInvariant()
 $effectful=[bool](Select-String -LiteralPath $Script -Pattern 'native-action-poc-receipt' -Quiet)
 if($effectful){
  if(-not $ApprovalReceipt){throw 'Exact-script Human approval receipt required for native PoC'}
  $approval=Get-Content -LiteralPath $ApprovalReceipt -Raw -Encoding UTF8 | ConvertFrom-Json
  if($approval.execution_status -eq 'CONSUMED'){throw 'This bounded approval has already been consumed; do not replay'}
  if($approval.Human_scope_approval -ne 'APPROVED' -or $approval.experiment_id -ne 'EXP-NATIVE-ACTION-01' -or $approval.script_sha256 -ne $scriptHash -or $approval.native_call_budget -ne 3){throw 'Native PoC approval scope mismatch'}
  if($DurationMs -lt 2400 -or $DurationMs -gt 5000){throw 'PoC observation window must cover restore and stay bounded'}
 }
 $games=@(Get-Process NBA2K22 -ErrorAction Stop)
 if($games.Count -ne 1){throw 'Unique NBA2K22 process required'}
 $hash=(Get-FileHash -LiteralPath $games[0].MainModule.FileName -Algorithm SHA256).Hash.ToLowerInvariant()
 if($hash -ne '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'){throw 'Game build changed'}
 @{pid=$games[0].Id;exe_sha256=$hash;script_sha256=$scriptHash;administrator=$true;task='NBA2K22-REA-NATIVE-AI-ACTION-01';effectful=$effectful;approval_receipt_supplied=[bool]$ApprovalReceipt;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Output 'target.json') -Encoding utf8
 $timer=[Diagnostics.Stopwatch]::StartNew()
 & 'C:\Program Files\nodejs\node.exe' 'C:\Users\gk\AppData\Roaming\npm\node_modules\rea-agents\scripts\rea.mjs' instrument-with-frida attach $games[0].Id --script-file $Script --duration-ms $DurationMs --format json 2> (Join-Path $Output 'stderr.log') | Set-Content -LiteralPath (Join-Path $Output 'evidence.json') -Encoding utf8
 $result=$LASTEXITCODE;$timer.Stop()
 @{exit_code=$result;elapsed_ms=$timer.ElapsedMilliseconds;process_alive=[bool](Get-Process -Id $games[0].Id -ErrorAction SilentlyContinue)} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Output 'metrics.json') -Encoding utf8
 if($result -ne 0){throw ('REA exit '+$result)}
} catch { $_.Exception.Message | Set-Content -LiteralPath (Join-Path $Output 'admin-error.txt') -Encoding utf8;throw }
