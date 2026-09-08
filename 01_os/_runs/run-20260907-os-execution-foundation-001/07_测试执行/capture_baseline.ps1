param([Parameter(Mandatory=$true)][string]$EvidenceDirectory)
# Historical filename: this captures the current worktree, not an implicit pristine baseline.
# A baseline claim additionally requires an independently verified exact checkout.
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $EvidenceDirectory) { throw 'Evidence directory already exists' }
New-Item -ItemType Directory -Path $EvidenceDirectory | Out-Null
$checkCommands = @(
  @{Name='model_routing'; Args=@('-B','01_os/03_mechanisms/model_routing/实现/verify_model_routing.py','static','.')},
  @{Name='baseline_task_preflight'; Args=@('-B','01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet','01_os/_runs/run-20260907-os-execution-foundation-001/01_任务/task_packet.yml','--repo-root','.','--json')},
  @{Name='workflow_static'; Args=@('-B','01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py','static','.')}
)
foreach ($checkCommand in $checkCommands) {
  $logPath = Join-Path $EvidenceDirectory ($checkCommand.Name + '.log')
  $checkArgs = $checkCommand.Args
  & python @checkArgs *> $logPath
  $checkExit = $LASTEXITCODE
  Write-Output ($checkCommand.Name + ' exit=' + $checkExit + ' log=' + $logPath)
}
