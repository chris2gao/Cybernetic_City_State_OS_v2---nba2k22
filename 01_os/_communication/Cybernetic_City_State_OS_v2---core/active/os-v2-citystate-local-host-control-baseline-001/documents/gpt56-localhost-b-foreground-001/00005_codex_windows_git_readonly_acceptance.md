---
document_id: os-v2-citystate-local-host-control-baseline-001::codex-windows-git-readonly-final-acceptance-00005
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Independently reproduce and adjudicate the permanent Task B Windows acceptance matrix without requiring local Git metadata mutation.
privacy_class: repository_shareable
---
# Task B / Codex Windows Final Acceptance — GitHub Truth + Read-only Local Git

Use one fresh isolated Codex Desktop session on Windows. Task B only. Do not start Task C.

## 1. Truth and local anchor

GitHub exact refs are the durable task/repository truth. Fresh-read remote `master` and the current Task B branch through GitHub-capable reads.

Use only this existing Windows anchor for physical local evidence:

`E:\newStand\study\Cybernetic_City_State_OS_v2 - core`

Do not use `E:\_pubwork`. Do not create another clone/worktree/scratch repository.

The local anchor is **read-only Git evidence** for this acceptance. Do not fetch, checkout, switch, commit, push, reset, clean, rebase, worktree-add, or perform any operation that needs a new `.git` file. The prior Codex audit reported that new `.git` files could not be created; preserve that as a separate finding rather than trying to repair or bypass it.

Read-only verify the anchor path, repository identity, remotes, HEAD, and worktree cleanliness. Unrelated worktree changes block the review; do not overwrite them.

## 2. Start authority

Enter only through the exact corrected formal v2 pointer. Validate:

- live authority `TA-os-v2-citystate-local-host-control-baseline-001-v2`;
- live delegation `Human/delegations/00005_codex_windows_git_readonly_acceptance.yml`;
- exact task, recipient endpoint/role, requested action and scope;
- no revocation and no redelegation.

Do not request or persist the Human task code.

## 3. Physical acceptance matrix

Freshly reproduce every row:

1. filesystem read/write/edit;
2. PowerShell 7;
3. Python;
4. Git read-only and machine-path correctness;
5. process/session metadata;
6. non-ASCII path roundtrip;
7. ordinary-user cleanup.

Prior GPT/RDC/Codex reports are historical evidence only and satisfy no physical row.

## 4. Disposable filesystem / Unicode probe

Use only:

`C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径`

and

`C:\Users\gk\Desktop\CITYSTATE_UTF8_ACCEPT_路径\验证_é.txt`

Preflight collision first. If absent, create the directory, write exact UTF-8 `CITYSTATE_UTF8_ALPHA`, read exact equality, edit to `CITYSTATE_UTF8_BETA`, read exact equality, list/resolve the non-ASCII path, then remove only the exact artifacts created by this session and verify absence.

Do not use console-codepage changes as a correctness workaround.

## 5. PowerShell / Python / process

Fresh-discover `pwsh`; record edition/version and run benign `Write-Output "CITYSTATE_TERMINAL_OK"`.

Fresh-discover Python; record executable/version and use it only for harmless UTF-8/path roundtrip logic.

Query bounded `node` process metadata only: PID, process name, start time when available. Do not stop or modify processes.

## 6. Git machine-path proof without `.git` writes

Operate read-only against the existing anchor. Use NUL-delimited machine output such as `git ls-files -z` or another read-only Git command that emits repository paths without terminal quoting.

Capture bytes, strict UTF-8 decode, split only on NUL, construct repository-relative filesystem `Path` objects, and prove physical existence/roundtrip for bounded paths including at least one non-ASCII tracked path if one exists in the current anchor.

Terminal-rendered Git text is not path evidence. Do not require the anchor to contain the Task B branch; GitHub exact refs carry Task B task truth.

## 7. Safety

Ordinary-user authority only. No secrets, credentials, keys, browser token stores, Windows Credential Store, `.env` secrets, administrator escalation or system-security changes.

No VPS, DNS, firewall, VPN, nginx, xray, cloudflared, service/listener/scheduler/boot changes, paid services/API credits, destructive Git/history rewrite, master publication, redelegation, or Task C.

## 8. Verdict matrix

At minimum report `PASS | PARTIAL | BLOCKED | NOT_RUN` for:

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

Separate `physically_observed`, `durable_repository_claim`, `Human_supplied_evidence`, `reviewer_self_report`, `inference`, and `unknown/not_run`.

The existing local `.git` new-file creation failure is a separate finding. It blocks a row only if that row actually requires metadata mutation; this acceptance does not.

## 9. Publication

Publish the formal result/review to `dev/os-v2-citystate-local-host-control-baseline-001` through an authenticated GitHub API/connector transport if available. Do not use local git push while `.git` metadata creation is unavailable.

Before publication fresh-read remote master, Task B branch head, authority/delegation liveness and actual publication transport; use non-force compare-and-swap/readback rules.

If no authenticated GitHub API/connector publication transport is available in Codex, do not claim publication. Return the complete structured review payload to the Human with `publication_status: pending_foreground_materialization`; the foreground will preserve reviewer provenance when materializing it.

Then STOP. Do not start Task C.
