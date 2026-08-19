---
document_id: os-v2-citystate-local-host-control-baseline-001::final-baseline-acceptance-00003
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Execute the permanent Task B fresh-window acceptance contract after POC-A PASS.
privacy_class: repository_shareable
---
# Task B / Final Baseline Acceptance

Use one fresh ChatGPT Web execution window. This is the final Task B runtime acceptance slice. Do not start Task C.

## 1. Execution topology

Repository-heavy work uses GitHub plus the executor's disposable Linux/Python workspace. Remote Desktop Commander is only the Windows physical-evidence adapter.

- Do not depend on `E:\_pubwork`.
- Do not create a new Windows clone/worktree/scratch repository.
- Treat the Linux workspace as disposable. Any result, script, evidence or document that must survive must be committed/published to the Task B GitHub branch before completion.
- If authenticated Linux Git push is unavailable, keep computation in Linux and use the current canonical GitHub publication transport; do not fall back to high-frequency Windows repository editing.

## 2. Start gate

Fresh-read remote `master`, load `AGENTS.md`, `AGENT_WORKING_DISCIPLINE.md`, `01_os/README.md`, and `01_os/开发入口与单窗口任务规范_v1.md`, then enter through the exact formal v2 pointer.

Validate Human Task Authority v2.1 delegated start using the current task root:

- live Human task authority;
- exact `task_authority_id`;
- live delegation `Human/delegations/00003_final_baseline_acceptance.yml`;
- exact task, recipient endpoint/role, requested action and scope;
- current revocation/liveness;
- no unauthorized redelegation.

Do not ask for, receive, infer, reconstruct or persist the Human task code. If the delegation gate fails, publish a blocked result and do not touch Windows.

## 3. Durable basis

Read the prior POC-A result and evidence, but do not treat it as a substitute for this fresh-window acceptance. The final acceptance window must itself cover every item in the permanent acceptance matrix.

Program contract source:
`01_os/_runs/run-20260818-citystate-local-host-control-program-design-001/03_方案设计/program_architecture_v1.yml`

Task packet:
`01_os/_runs/run-20260819-citystate-local-host-control-baseline-001/01_任务输入/任务包_v1.yml`

POC-A adjudication:
`01_os/_runs/run-20260819-citystate-local-host-control-baseline-001/06_验证/poc_a_adjudication_v1.yml`

## 4. Windows target and safety

Fresh-discover the intended device through Remote Desktop Commander. Expected prior device name is `DESKTOP-FPNE2NQ`, but current physical state wins.

Use ordinary Windows-user authority only. No administrator escalation. Do not access passwords, credentials, API keys, private keys, browser credential/token stores, Windows Credential Store, `.env` secrets, SSH private key stores, or unrelated file content.

No VPS/DNS/VPN/nginx/xray/cloudflared/firewall/ports/services/scheduler/boot changes. No Desktop Commander safety-configuration changes. No paid-service/API-credit activation.

## 5. Permanent fresh-window acceptance matrix

This single fresh window must physically cover all of the following:

1. `filesystem_read_write_edit`
2. `PowerShell_7`
3. `Python`
4. `Git`
5. `process_and_session`
6. `non_ASCII_path_roundtrip`
7. `ordinary_user_cleanup`

### 5.1 Remote tool/device discovery

- confirm Remote Desktop Commander tools are visible;
- fresh-confirm intended device online;
- record app/device version when exposed.

### 5.2 Filesystem + Python + Unicode roundtrip

Use a dedicated exact test root only:

`C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径`

and exact test file:

`C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径\验证_é.txt`

Before mutation, verify the directory and file do not already exist. If either exists, do not overwrite/delete it; mark the affected probe blocked by collision.

If absent, use ordinary-user execution to:

- create the directory;
- create the file with exact UTF-8 text `CITYSTATE_UTF8_ALPHA`;
- read it back exactly;
- edit it to exact text `CITYSTATE_UTF8_BETA`;
- read it back exactly;
- verify Python can represent the Unicode path and perform a filesystem encode/decode roundtrip without changing the path;
- record the actual Python version/executable used.

A temporary helper script may be created only under this exact test root or as `C:\Users\gk\Desktop\CITYSTATE_B_FINAL_ACCEPT.py`; if created, it becomes an exact cleanup artifact and must be removed before completion.

### 5.3 PowerShell 7

Fresh-discover `pwsh` rather than assuming its path. Execute PowerShell 7 and record edition/version. Run exact benign output:

`Write-Output "CITYSTATE_TERMINAL_OK"`

Do not install or modify PowerShell/profile/system configuration.

### 5.4 Git path machine logic

Known Windows core anchor from prior evidence:

`E:\newStand\study\Cybernetic_City_State_OS_v2 - core`

Fresh-verify that path is a Git worktree for `chris2gao/Cybernetic_City_State_OS_v2---core` before using it. Do not switch branches or modify it.

The acceptance must exercise the permanent machine path contract, not terminal-rendered paths:

`git -z -> raw bytes -> strict UTF-8 decode -> filesystem Path`

A suitable read-only Python probe is:

- run Git with a NUL-delimited path-producing command such as `git ls-files -z` using `subprocess` with stdout captured as bytes;
- strict-decode the raw bytes as UTF-8;
- split only on NUL;
- select at least one tracked path containing non-ASCII characters;
- construct the filesystem `Path` from the decoded repository-relative path;
- verify that exact tracked path physically exists;
- verify filesystem encode/decode roundtrip preserves the same path;
- do not use terminal text as path evidence;
- do not change console codepage as a correctness workaround.

Also run a bounded read-only Git status/log probe. No checkout, switch, commit, merge, reset, clean, rebase, pull, push or worktree mutation.

### 5.5 Process/session

Query bounded running `node` process/session metadata. Return only PID, process name, and start time when available. Do not stop or modify a process.

### 5.6 Cleanup

Delete only artifacts created by this acceptance window:

- `C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径\验证_é.txt`;
- the exact dedicated directory after its file is removed;
- `C:\Users\gk\Desktop\CITYSTATE_B_FINAL_ACCEPT.py` only if this window created it.

Verify each created artifact is absent afterward. Do not remove any repository worktree, unrelated directory, cache or existing file.

## 6. Repository-side validation and execution-surface profile

Use GitHub/Linux for repository-side checks. If pytest is used for disposable verification, use `-p no:cacheprovider` as defined by the permanent Task B contract.

Record a bounded execution-surface profile sufficient to adjudicate the hybrid topology:

- which work was done in GitHub/Linux;
- which probes required Remote Desktop Commander;
- measured RDC tool-call count if readily available from the execution log, otherwise `not_measured`;
- any RDC timeout/safety-layer retry and whether it changed the final capability verdict.

Do not optimize by weakening a required physical probe.

## 7. Required result matrix

Return `PASS`, `PARTIAL`, `BLOCKED`, or `NOT_RUN` for at least:

- delegated_start_authority
- remote_tool_discovery
- intended_device_online
- filesystem_read
- filesystem_write
- filesystem_edit
- powershell_7
- python_execution
- git_read_only
- git_z_raw_bytes_utf8_path_logic
- process_and_session
- non_ascii_path_roundtrip
- ordinary_user_cleanup
- fresh_window_permanent_contract
- hybrid_execution_topology

For each non-PASS row identify the failure layer: ChatGPT product/tool exposure, Remote Desktop Commander App, remote transport, Windows runtime, repository/publication, or unknown.

Distinguish physically observed facts, durable repository claims, Human-supplied evidence, executor self-report, inference and unknown/not-run.

## 8. Publication

Publish one formal `result` from endpoint `gpt56-localhost-b-final-acceptance-executor-003` to `gpt56-localhost-b-foreground-001` on branch `dev/os-v2-citystate-local-host-control-baseline-001`.

Only Task B communication/run evidence may be added. Do not modify canonical mechanisms or `master`.

Before publication fresh-read remote master, Task B branch head and current task-root liveness. Use the actual supported canonical publication transport and non-force rules. After publication perform remote readback.

Final Human-facing output must include:

1. overall verdict;
2. full acceptance matrix;
3. important Windows physically observed facts;
4. hybrid execution-surface observations;
5. exact formal result pointer;
6. publication commit SHA;
7. blocking findings if any;
8. confirmation that master was unchanged.

Then STOP. Do not start Task C.
