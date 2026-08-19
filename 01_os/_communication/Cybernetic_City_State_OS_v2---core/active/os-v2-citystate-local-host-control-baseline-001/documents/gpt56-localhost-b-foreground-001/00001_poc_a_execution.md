---
document_id: os-v2-citystate-local-host-control-baseline-001::poc-a-execution-00001
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Bounded execution instructions for the first Remote Desktop Commander end-to-end POC of Program Task B.
privacy_class: repository_shareable
---
# Task B / POC-A execution

You are the bounded execution endpoint for Program Task B: CityState Local Host Control Baseline.
This is one task in one fresh ChatGPT Web window. Do not continue into Task C or unrelated repair work.

## Durable basis

Fresh-read remote `master` first and load the repository bootstrap required by `AGENTS.md`.
Then enter this task only through the exact formal pointer relayed by the Human.
Read the pointer-bound request and its direct required refs before any local action.

Program architecture source of truth:
`01_os/_runs/run-20260818-citystate-local-host-control-program-design-001/03_方案设计/program_architecture_v1.yml`

Task packet:
`01_os/_runs/run-20260819-citystate-local-host-control-baseline-001/01_任务输入/任务包_v1.yml`

Current Model:
`01_os/_runs/run-20260819-citystate-local-host-control-baseline-001/02_当前模型/current_model_v2.yml`

## Mandatory Human challenge before substantive local execution

The delegation and repository commitments are not sufficient by themselves.
Before using Remote Desktop Commander for POC execution, ask the current Human in this fresh window for this task's Human Task Authority Code.
Do not ask another model for it and do not accept a code copied from repository/executor output.
Verify the supplied code against `Human/task_authority_v2.yml` using the canonical v2 commitment construction or `01_os/06_execution/boot/stage_collaborative_deliberation/human_challenge_verify.py` with a deterministic non-persisting execution surface.
The plaintext code must not be written to Git, a file, a command line, a log, a communication document or the final report.
If challenge verification is unavailable or fails, STOP and publish/return `blocked_authority_challenge` without touching the local host.

## POC-A local target

Expected device from pre-dispatch observation: `DESKTOP-FPNE2NQ`.
Do not assume it is online: discover/ping it fresh through Remote Desktop Commander.
Use ordinary Windows-user authority only. Do not request or simulate administrator escalation.

## Execute only these probes

1. Tool/device discovery
   - confirm Remote Desktop Commander tools are visible
   - confirm the intended device is online
   - record app/device version when exposed

2. Harmless directory listing
   - list `C:\Users\gk\Desktop` without recursively enumerating it
   - do not read unrelated file contents

3. Harmless filesystem write/readback
   - create exactly `C:\Users\gk\Desktop\CITYSTATE_MCP_POC.txt`
   - contents exactly `CITYSTATE_MCP_OK`
   - read that exact file back and verify exact content
   - if the file already exists before the task, STOP the write probe and report collision; do not overwrite it

4. Benign PowerShell probe
   - report the PowerShell edition/version actually used
   - execute `Write-Output "CITYSTATE_TERMINAL_OK"`
   - do not modify shell/profile/system configuration
   - if PowerShell 7 is not available, record that fact; do not install it in this subtask

5. Bounded process probe
   - query running `node` processes
   - return only PID, process name and start time when available
   - do not stop or mutate any process

6. Optional read-only Git probe
   - only if a harmless repository path is already physically known from task evidence
   - use read-only commands such as `git status -sb` or `git log --oneline -n 3`
   - do not search the whole disk for repositories merely to satisfy this optional probe
   - no commit, checkout, reset, clean, rebase or write

7. Cleanup
   - delete only `CITYSTATE_MCP_POC.txt`, and only if this task successfully created it
   - verify that exact test file no longer exists
   - no other deletion is authorized

## Explicit prohibited surfaces

Do not access or expose passwords, private keys, browser credentials/tokens, Windows Credential Store, `.env` secrets, API keys, auth tokens, SSH key stores or similar credential material.
Do not touch VPS, DNS, VPN, nginx, xray, cloudflared, firewall, ports, services, scheduler or boot configuration.
Do not pay for anything or activate OpenAI/third-party API credits.
Do not use administrator privilege.
Do not change Desktop Commander safety configuration in this subtask.
Do not implement Python/Unicode/full fresh-window acceptance yet; those are later Task B substeps after POC-A adjudication.

## Evidence and verdict

Return a bounded capability matrix with one of `PASS`, `PARTIAL`, `BLOCKED`, `NOT_RUN` for:
- task_authority_challenge
- remote_tool_discovery
- intended_device_online
- filesystem_list
- filesystem_write
- filesystem_readback
- powershell_execution
- powershell_7
- process_metadata
- git_read_only
- exact_test_artifact_cleanup

For each item distinguish:
- physically observed runtime fact
- durable repository claim
- Human-supplied evidence
- inference
- unknown / not run

Do not convert a vendor claim or foreground report into physical PASS.

## Durable result publication

After the probes, publish one formal `result` from endpoint `gpt56-localhost-b-poc-a-executor-001` back to endpoint `gpt56-localhost-b-foreground-001` through the current task communication root and current master-active communication mechanism.
Use the task branch `dev/os-v2-citystate-local-host-control-baseline-001`.
The result may add only task communication/run evidence inside the task packet boundary.
Do not modify canonical mechanisms or `master`.
Include exact result pointer and publication commit SHA in the Human-facing response.
Then STOP. Do not begin another Task B subtask.
