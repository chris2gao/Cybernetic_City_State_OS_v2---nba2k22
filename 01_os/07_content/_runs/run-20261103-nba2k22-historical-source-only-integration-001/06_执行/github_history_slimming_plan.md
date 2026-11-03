# GitHub historical-object slimming plan — separate Human decision required

## What this source-only PR accomplishes

- Source-only integration from NBA master `45cc45cae0550ddcda192a2179ea48509b27f6ee` copies **1,978** exact Host Git blobs into a new commit whose first parent is master, not Host.
- Leaves **234** Host-only raw/large artifacts out of the new source-only tree (~2,007,813,667 raw bytes). See `local_only_artifact_inventory.json` for every path, size, original Git blob SHA-1, source commit, classification and SHA256 awaiting local computation.
- Includes existing master-controlled source/PRMS files, with only `.gitignore` changed, and preserves the three small existing master `.db` research fixtures.
- Preserves source .sql and Python migration code, tests and necessary small fixtures. Original Host SHA is a provenance pointer, not an ancestor of the new source-only commit.
- **Does NOT delete or reduce already reachable large Git objects in the old remote branches or old PRs.** Source-only Git history avoids *newly inheriting* those objects onto master, but cannot garbage-collect already published remote Git data.

## Known impacted historical references — exhaustive ref scan still required

1. `task/nba2k22-world-data-full-implementation-20261024` at `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4` and any branches descending from it: candidate large WorldData snapshot sources.
2. `task/nba2k22-live-host-closed-loop-integration-20261102` at `1fc2965ae10ef2a34abb37d800d86cd548f24aeb`: contains source and snapshot history; must remain unchanged unless separately approved.
3. `integration/nba2k22-completed-host-mainline-20261103` at `6a0cdeb6c1f9abf074607f243a0c417ec24fac80`: earlier full-history staging; PR #24 is merged into this staging branch, **not master**.
4. NBA PR #25 points at that full-history integration branch. It is **superseded** by the source-only integration. Do not merge #25 into master.
5. Additional WorldData/Calendar/VAE, bulk/Host, research and base branches **may** contain the same objects. Identify them by exhaustive local `git for-each-ref` + `git merge-base --is-ancestor` and `git rev-list --objects --all` before deciding ref rewrites.
6. Historical Run/Completion Pointer, PR descriptions, OS PRMS records and external references cite fixed SHAs for WorldData v24, G2/S0, Bulk, Outbox, SeasonCycleHost and Host. They need an explicit old-SHA → rewritten-SHA map if history is ever rewritten. Never mutate an original historical receipt to claim newly executed tests.

## Recommended independent slimming procedure (NOT AUTHORIZED in this task)

1. **First** complete the local archive with SHA256, source Git blob SHA1, path, size, restore location and Human-confirmed backup storage; verify random restorations.
2. Clone a **separate mirror** of the full repository for simulation. Capture `git show-ref`, all PR head/base SHAs, PRMS references, tag SHAs and a durable reference export. Confirm local disk capacity. Keep original repository and remote untouched.
3. Build an exact path-list from local-only inventory and use a candidate `git filter-repo` simulation on the mirror only. Avoid blanket `--strip-blobs-bigger-than` because small research fixtures, necessary test data, SQL schema and reports may be semantically essential.
4. Calculate the exact changed commit-SHA map and the affected branch/tag/PR set. Publish a migration table for downstream developers and PRMS (old historical SHA remains an archived reference, new SHA becomes current approved lineage). Re-run only the minimal integrity checks relevant to changed history references.
5. Present storage delta, effect on open PR #8/#10/#12/#14/#16/#17/#18/#19 and staging PR #25, expected GitHub remote object-retention limitations, backup/recovery and rollback strategy to Human.
6. **Only with a separate explicit Human authorization** consider rewriting specific refs and coordinating push windows. No automatic force push, ref removal, remote garbage collection or GitHub PR rewrite in this integration task. GitHub can retain old objects and cached PR refs for some time even after a rewrite.

## Recovery without rewriting

To restore an excluded source object, use its `git_blob_sha1` in the original local full clone:
```text
git cat-file -s <blob-sha1>
git cat-file blob <blob-sha1> > <original-relative-path>
```
For binary restoration on Windows use the bundled Python archive script rather than PowerShell text redirection. The local archive receipt validates each output using SHA256 and `git hash-object`. Keep `.git/objects/pack` intact: it is Git history storage, **not disposable cache**.
