# .githooks

The rule has always been that core history is never rewritten and `master` moves
only after a Human gate — it is section 6 of `AGENT_WORKING_DISCIPLINE.md`. Until
these hooks existed, nothing checked it. They are the check, on one transport.

## Enable

Once per clone, including every domain fork:

```sh
git config core.hooksPath .githooks
```

Verify it took:

```sh
git config --get core.hooksPath      # -> .githooks
```

Hooks live in the repository and travel with `git merge core/master`, but
`core.hooksPath` is local config and does **not** travel. A fresh clone runs
unguarded until someone sets it. `install.ps1` does it and reports the result.

## What pre-push refuses

| Situation | Behaviour |
| :--- | :--- |
| Non-fast-forward push (force, rebase, squash, amend of published history) | Refused. **No override.** |
| Push to `master` / `main` | Refused unless `CITYSTATE_ALLOW_MASTER=1` is set for that command |
| Deleting `master` / `main` | Refused unless `CITYSTATE_ALLOW_MASTER=1` is set for that command |
| Deleting an ordinary remote branch | **Allowed** since 2026-08-02 |
| Normal push to a feature branch | Allowed |

Branch deletion was refused with no override until 2026-08-02. Removing it was not
a relaxation for its own sake. With no override, the only way to delete a branch
was `git push --no-verify`, and that turns off *every* check in this hook at once —
including the non-fast-forward guard. Routine cleanup and history rewriting shared
a single switch, so every branch tidy-up meant reaching for the lever that also
unlocks the one thing this repository can never undo. Deleting a merged branch
costs nothing; rewriting history costs every fork at once. They are now separate.

Deletion is still worth doing carefully — record the branch names and their SHAs
before deleting, because an unmerged branch's commits become unreachable and are
eventually collected. The hook no longer does that thinking for you.

Authorized master push, after independent audit:

```sh
CITYSTATE_ALLOW_MASTER=1 git push origin master
```

The variable is per-command on purpose. Exporting it for a whole session turns the
gate back off and leaves no trace that it happened.

## What it does not do

**`git push --no-verify` skips this hook entirely.** So does any client that pushes
without invoking hooks.

This is a guard, not an access boundary — the same distinction
`08_os/_runs/run-007-上下文管理信息收集测试/` established between a workspace
partition and an enforced boundary. It stops the accident, the stale habit and the
agent that never considered the rule. It does not stop a caller that has decided to
go around it, and it should never be cited as proof that history cannot have been
rewritten. For that, read the remote.

It also covers exactly one transport. An executor pushing through the GitHub API or
a CLI that never invokes hooks is not unguarded and not unpermitted — it owes a
different, equivalent set of checks. That matrix is section 1.1 of
`08_os/开发入口与单窗口任务规范_v1.md`; who may publish at all, and which acts stay
action-bound even under the widest Human grant, is
`08_os/05_registry/repository_publisher_authority_v1.yml`. Reporting `hook_guard: passed` on a
transport that cannot run this hook is an invalid completion pointer, and so is
treating `not_applicable_transport` as nothing to prove.
