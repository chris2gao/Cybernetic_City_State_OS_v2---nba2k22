# .githooks

The protocol has always said core history is never rewritten and master moves only
after a human gate. Until now nothing checked that. These hooks are the check.

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
| Configured personal absolute path in the commits being pushed | Refused |
| Personal-path validator, configuration, or Python runtime unavailable | Refused (fail closed) |

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

This is a guard, not an access boundary — the same distinction run-007 established
between a workspace partition and an enforced boundary. It stops the accident, the
stale habit and the agent that never considered the rule. It does not stop a caller
that has decided to go around it, and it should never be cited as proof that history
cannot have been rewritten. For that, read the remote.

The personal-path check scans the exact committed range Git supplies for each pushed
ref. It does not scan unrelated historical files, so legacy findings outside the
range do not make every future push impossible. A new branch is compared with the
merge-base of the remote's tracked `master` or `main`; if that base cannot be
determined, the hook refuses instead of falling back to a whole-repository scan.

`activation_travels_with_merge: false`: merging these files into a domain repository
does not activate them in an existing clone. Every clone must still run
`git config core.hooksPath .githooks` (or `install.ps1`). This hook covers only the
`local_git` publication transport; GitHub API/connector publication never invokes it,
so reporting `hook_guard: passed` for those transports is a false receipt.
