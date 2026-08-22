---
document_id: os-v2-citystate-local-host-control-baseline-001::local-completion-cleanup-00006
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Synchronize the canonical Windows core anchor after Task B master integration and safely clean only merged Task B local branch/worktree state.
privacy_class: repository_shareable
---
# Task B post-integration local synchronization and safe cleanup

Task B has been accepted and integrated to remote `master`. This action is completion housekeeping only. Do not rerun the Windows acceptance matrix and do not start Task C.

## Required physical start checks

1. Fresh-read remote `master` and perform the repository-wide always-on bootstrap.
2. Enter only through the exact formal v2 pointer for request `00006`.
3. Validate live Task Authority v2 and `Human/delegations/00006_completion_cleanup.yml`; do not request the Human task code.
4. Use only the canonical Windows core anchor:

   `E:\newStand\study\Cybernetic_City_State_OS_v2 - core`

5. Read-only verify path, repository identity, origin, current branch/HEAD, worktree cleanliness and `git worktree list --porcelain`.
6. If the canonical anchor has unrelated local changes, wrong repository identity, or an unexpected remote, return `BLOCKED` without mutation.

## Synchronize canonical anchor

Use ordinary Git commands only. Do not manually create/edit files under `.git`, do not elevate privileges, and do not alter ACLs.

1. Fetch the current `origin/master`.
2. Ensure the canonical anchor is on local `master` without discarding work.
3. Advance local `master` by fast-forward only to the exact current remote master.
4. Verify local `HEAD == origin/master ==` the fresh remote master read for this execution.
5. Verify the canonical anchor remains clean.

If normal Git metadata writes still fail because of the historical `.git` anomaly, return `BLOCKED_LOCAL_GIT_METADATA_WRITE` with the exact command/error. Do not repair, bypass, change ACLs, or elevate.

## Exact Task B local cleanup

The only Task B worktree expected from historical topology is:

`E:\_pubwork\localhost-b-001`

The parent `E:\_pubwork` and all unrelated / Task C material must be preserved.

1. Re-read `git worktree list --porcelain`.
2. If the exact Task B worktree is not registered, record `not_present` and continue.
3. If registered, verify it is tied to `dev/os-v2-citystate-local-host-control-baseline-001`, is clean, and its commit is contained in current integrated `master`.
4. Before any worktree removal, perform a read-only ACL preflight on the exact Task B worktree root. Do not change ACLs. Any abnormal ACL or inaccessible path is a blocker and must stop before deletion.
5. Remove the exact Task B worktree using normal non-force `git worktree remove`. Do not use `--force` and do not manually delete the directory as a workaround.
6. Re-read the worktree list and verify the exact registration is absent.
7. Delete the local Task B branch only with normal `git branch -d`, and only after proving it is merged. Never use `-D`.
8. Do not delete the remote Task B branch; foreground will do that only after durable cleanup result readback and final completion evidence.
9. Do not delete `E:\_pubwork` itself.

## Prohibited actions

No force, reset-hard, clean, rebase, squash, amend, history rewrite, secret/credential access, administrator escalation, security-policy changes, network/VPS/DNS/firewall/VPN/nginx/xray/cloudflared changes, service/scheduler changes, master publication, acceptance rerun, or Task C.

## Result

Return one formal result to `gpt56-localhost-b-foreground-001` with:
- delegated-start status;
- fresh remote master;
- canonical anchor pre/post branch and HEAD;
- origin and cleanliness;
- fetch/fast-forward result;
- Task B worktree registration pre/post;
- ACL preflight result;
- local Task B branch deletion result;
- `_pubwork` parent preservation confirmation;
- remaining blockers/findings;
- master publication performed: false;
- Task C started: false.

Publish the result to `dev/os-v2-citystate-local-host-control-baseline-001` through an authenticated non-force GitHub transport if available, then STOP.
