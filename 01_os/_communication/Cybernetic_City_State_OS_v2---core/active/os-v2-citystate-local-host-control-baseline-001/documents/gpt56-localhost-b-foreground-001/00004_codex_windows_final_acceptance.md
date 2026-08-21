---
document_id: os-v2-citystate-local-host-control-baseline-001::codex-windows-final-acceptance-00004
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Independently reproduce and adjudicate the permanent Task B Windows acceptance matrix after the RDC-dependent route became unavailable.
privacy_class: repository_shareable
---
# Task B / Codex Windows Final Acceptance

Use one fresh isolated Codex Desktop session on Windows. This is Task B only. Do not start Task C.

## 1. Durable source and local anchor

GitHub is the durable source of truth. Fresh-read remote `master` and the current Task B branch before work.

Use only this existing Windows repository anchor:

`E:\newStand\study\Cybernetic_City_State_OS_v2 - core`

Do not use `E:\_pubwork`. Do not create another clone, worktree or scratch repository.

Before mutation, verify the anchor physically exists, is the intended repository, has the expected origin, and is clean. If it contains unrelated local changes, stop and publish BLOCKED rather than resetting or overwriting them.

Fetch normally, then switch the existing anchor to `dev/os-v2-citystate-local-host-control-baseline-001` only if that can be done without discarding local work. Never force, reset, rebase, squash, amend or rewrite history.

## 2. Start authority

Enter through the exact formal v2 pointer. Validate current Human Task Authority v2.1 using:

- live authority `TA-os-v2-citystate-local-host-control-baseline-001-v2`;
- live delegation `Human/delegations/00004_codex_windows_final_acceptance.yml`;
- exact task, recipient endpoint/role, action and delegated scope;
- no revocation and no redelegation.

Do not request, infer, reconstruct or persist the Human task code. If delegated start fails, publish BLOCKED and perform no acceptance mutation.

## 3. Evidence isolation

This is independent physical reproduction. Reconstruct from durable repository evidence only. Do not use executor private context.

Prior POC-A PASS and the two final-acceptance BLOCKED results are historical inputs only. They do not satisfy any physical row in this window.

## 4. Safety boundary

Use ordinary Windows-user authority only. No administrator escalation. Do not access passwords, credentials, API keys, private keys, browser credentials/tokens, Windows Credential Store, `.env` secrets or SSH private-key stores.

No VPS, DNS, VPN, firewall, nginx, xray, cloudflared, listener, scheduler, boot or service mutation. No paid-service/API-credit activation.

## 5. Permanent Windows acceptance matrix

Physically reproduce every row in this fresh Codex session:

1. filesystem read/write/edit;
2. PowerShell 7;
3. Python;
4. Git read-only and machine-path correctness;
5. process/session metadata;
6. non-ASCII path roundtrip;
7. ordinary-user cleanup.

### 5.1 Dedicated disposable path

Use only:

`C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径`

and:

`C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径\验证_é.txt`

Before creating anything, verify both are absent. Collision means BLOCKED for affected rows; do not overwrite or delete pre-existing material.

If absent:

- create the directory;
- write exact UTF-8 text `CITYSTATE_UTF8_ALPHA`;
- read back exact equality;
- edit to exact text `CITYSTATE_UTF8_BETA`;
- read back exact equality;
- use Python to prove filesystem encode/decode roundtrip preserves the Unicode path;
- record Python executable and version.

A helper script may exist only under that exact test root or as `C:\Users\gk\Desktop\CITYSTATE_B_FINAL_ACCEPT.py`; if created by this window it must be included in exact cleanup.

### 5.2 PowerShell 7

Fresh-discover `pwsh`. Record edition/version and execute exact benign output:

`Write-Output "CITYSTATE_TERMINAL_OK"`

Do not install or modify PowerShell/profile/system configuration.

### 5.3 Git machine-path contract

On the existing core anchor, use a read-only Python subprocess probe with a NUL-delimited Git path command such as `git ls-files -z`.

Required correctness chain:

`git -z -> raw bytes -> strict UTF-8 decode -> split only on NUL -> repository-relative filesystem Path`

Select at least one tracked non-ASCII path, prove that exact path exists physically, and prove filesystem encode/decode roundtrip preserves it. Terminal-rendered Git text and console codepage are not path evidence.

Also run bounded read-only `git status -sb` and `git log --oneline -n 3`. Do not change repository files for this probe.

### 5.4 Process/session

Query bounded running `node` process/session metadata. Return only PID, process name and start time when available. Do not stop or modify processes.

### 5.5 Cleanup

Delete only artifacts created by this acceptance window. Verify each created artifact is absent after cleanup. Do not delete caches, worktrees, repository files or unrelated existing paths.

## 6. Required verdict matrix

Return `PASS`, `PARTIAL`, `BLOCKED` or `NOT_RUN` for at least:

- delegated_start_authority
- repository_anchor_identity_and_cleanliness
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
- codex_windows_physical_reproduction

For every non-PASS row identify the failure layer. Distinguish physically observed facts, durable repository claims, Human-supplied evidence, reviewer self-report, inference and unknown/not-run.

## 7. Publication

Publish one formal result/review from `codex-localhost-b-final-acceptance-reviewer-004` to `gpt56-localhost-b-foreground-001` on branch `dev/os-v2-citystate-local-host-control-baseline-001`.

Only Task B communication/run evidence may be added. Before publication fresh-read remote master, branch head, current authority/delegation liveness, local worktree cleanliness and configured hook/publication transport. Use the current canonical publication gate for the actual transport. Non-force only. Remote-read back after publication.

Final Human-facing output must include overall verdict, full matrix, important physical Windows facts, exact formal result pointer, publication commit SHA, blockers if any, and confirmation that master and Task C were untouched. Then STOP.
