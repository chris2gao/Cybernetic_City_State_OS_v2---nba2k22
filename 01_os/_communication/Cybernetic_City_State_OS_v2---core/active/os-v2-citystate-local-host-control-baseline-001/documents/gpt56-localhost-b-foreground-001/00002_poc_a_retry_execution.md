---
document_id: os-v2-citystate-local-host-control-baseline-001::poc-a-retry-execution-00002
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Execute the bounded Remote Desktop Commander POC-A under Human Task Authority v2.1 delegated-start semantics after the first attempt was blocked by the superseded recipient challenge requirement.
privacy_class: repository_shareable
---
# Task B / POC-A retry under Human Task Authority v2.1

Use one fresh ChatGPT Web execution window. Do not continue into Task C or unrelated repair work.

## Durable basis and start gate

Fresh-read remote `master`, then load `AGENTS.md`, `AGENT_WORKING_DISCIPLINE.md`, `01_os/README.md`, and `01_os/开发入口与单窗口任务规范_v1.md` from that master. Enter Task B only through the exact formal v2 Human relay pointer.

Read the pointer-bound request and direct required refs. Current Model is `01_os/_runs/run-20260819-citystate-local-host-control-baseline-001/02_当前模型/current_model_v3.yml`.

Before any local probe, verify Human Task Authority v2.1 delegated-start authority: live Human-rooted task authority, exact `task_authority_id`, exact recipient endpoint/role, requested action, delegated scope, current liveness/revocation state, and no unauthorized redelegation.

Do not ask for, receive, infer, reconstruct or persist the Human task code. Ordinary delegated start does not use it. If the formal pointer or delegation gate fails, STOP and publish a blocked result without touching the local host.

## Local target

Expected device from prior evidence: `DESKTOP-FPNE2NQ`. Discover its current state fresh through Remote Desktop Commander. Use ordinary Windows-user authority only; no administrator escalation.

## Execute only these probes
1. Tool/device discovery
   - confirm Remote Desktop Commander tools are visible;
   - confirm the intended device is online;
   - record app/device version when exposed.

2. Harmless directory listing
   - list `C:\Users\gk\Desktop` non-recursively;
   - do not read unrelated file contents.

3. Harmless filesystem write/readback
   - create exactly `C:\Users\gk\Desktop\CITYSTATE_MCP_POC.txt`;
   - contents exactly `CITYSTATE_MCP_OK`;
   - read that exact file back and verify exact content;
   - if it already exists before this task, STOP the write probe and report collision; do not overwrite it.

4. Benign PowerShell probe
   - report the PowerShell edition/version actually used;
   - execute `Write-Output "CITYSTATE_TERMINAL_OK"`;
   - do not modify shell/profile/system configuration;
   - if PowerShell 7 is unavailable, record that fact; do not install it.

5. Bounded process probe
   - query running `node` processes;
   - return only PID, process name and start time when available;
   - do not stop or mutate any process.
6. Optional read-only Git probe
   - only if a harmless repository path is already physically known from task evidence;
   - use read-only commands such as `git status -sb` or `git log --oneline -n 3`;
   - do not search the whole disk merely to satisfy this optional probe;
   - no commit, checkout, reset, clean, rebase or write.

7. Cleanup
   - delete only `CITYSTATE_MCP_POC.txt`, and only if this task successfully created it;
   - verify that exact test file no longer exists;
   - no other deletion is authorized.

## Explicit prohibited surfaces

No passwords, private keys, browser credentials/tokens, Windows Credential Store, `.env` secrets, API keys, auth tokens or SSH key stores. No VPS/DNS/VPN/nginx/xray/cloudflared/firewall/ports/services/scheduler/boot changes. No payment/API-credit activation. No administrator privilege. No Desktop Commander safety-configuration changes. No Python/Unicode/full fresh-window acceptance yet.

## Evidence and durable result

Return `PASS`, `PARTIAL`, `BLOCKED`, or `NOT_RUN` for: delegated_start_authority, remote_tool_discovery, intended_device_online, filesystem_list, filesystem_write, filesystem_readback, powershell_execution, powershell_7, process_metadata, git_read_only, exact_test_artifact_cleanup. Distinguish physically observed facts, durable repository claims, Human-supplied evidence, inference, and unknown/not-run.

Publish one formal `result` from endpoint `gpt56-localhost-b-poc-a-executor-002` back to `gpt56-localhost-b-foreground-001` on branch `dev/os-v2-citystate-local-host-control-baseline-001`. Add only task communication/run evidence. Do not modify canonical mechanisms or `master`. Return the exact result pointer and publication commit SHA, then STOP.