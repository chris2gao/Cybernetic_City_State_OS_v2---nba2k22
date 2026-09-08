param([Parameter(Mandatory=$true)][string]$EvidenceDirectory)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $EvidenceDirectory) { throw 'Evidence directory already exists' }
New-Item -ItemType Directory -Path $EvidenceDirectory | Out-Null
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$packetPath = '01_os/_runs/run-20260907-os-execution-foundation-001/01_任务/task_packet.yml'
$checks = @(
  @{Name='scope'; Args=@('-B','01_os/06_execution/task_discipline/path_ledger/changed_path_ledger.py','--base','3dc058a1a3cf393b936025f43fd737b0848937b4','--packet',$packetPath,'--json')},
  @{Name='closure'; Args=@('-B','01_os/06_execution/task_orchestration/big_task/closure_preflight.py','--packet',$packetPath)},
  @{Name='model_routing'; Args=@('-B','01_os/03_mechanisms/model_routing/实现/verify_model_routing.py','static','.')},
  @{Name='context'; Args=@('-B','01_os/03_mechanisms/context_management/实现/verify_context_structure.py')},
  @{Name='live_state_guard'; Args=@('-B','01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_no_canonical_live_state.py','.')},
  @{Name='static_refs'; Args=@('-B','01_os/_runs/run-20260907-os-execution-foundation-001/07_测试执行/diagnose_static_refs.py')}
)
foreach ($check in $checks) {
  $checkArgs = $check.Args
  $logPath = Join-Path $EvidenceDirectory ($check.Name + '.log')
  & python @checkArgs *> $logPath
  $checkExit = $LASTEXITCODE
  Write-Output ($check.Name + ' exit=' + $checkExit + ' log=' + $logPath)
}
