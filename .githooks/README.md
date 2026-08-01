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
| Deleting a remote branch | Refused |
| Normal push to a feature branch | Allowed |

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
