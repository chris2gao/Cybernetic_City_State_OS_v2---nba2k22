# Baseline route decision — Human-delegated, 2026-09-07

This is an ordinary task decision record, not a cross-endpoint message, delivery,
independent acceptance, or permission to integrate into master. The current Human
delegated the three decisions in Claude's alignment report. Existing foundation
architecture/implementation delegation remains in force; the frozen branch stays frozen.

## Fresh physical anchors

Read from the live remote in this resumed turn, then tested locally by exact SHA:

| Ref | Exact SHA |
| --- | --- |
| master | 3dc058a1a3cf393b936025f43fd737b0848937b4 |
| claude/task-discipline-receipts-001 | b79922dce8975add161de69d4614543644ef52f5 |
| claude/conformance-checker-phase1-001 | d817c804a9a9af17234a481a10690c45e07da85c |
| codex/os-execution-foundation-20260907 before this decision | 46acc0918d3d262e21e69ffe99002837a989ff53 |

`git merge-base --is-ancestor` distinguishes exit 1 (not an ancestor) from errors.
Master is an ancestor of receipts and Codex, but not phase1. Phase1 is an ancestor
of receipts. Neither receipts nor Codex is an ancestor of the other. Their unique
merge-base is the exact master above. Master/phase1 merge-base is
`820c61a322b5a7c5ea71c02bd7722dfbd448ab28`.

Clarification of the supplied report: Codex's parent is current master, but
receipts imported master in merge `37d8b130`; both candidates do not literally
start directly from that commit. The common-baseline conclusion remains correct.

## Three decisions

1. **No merge of the rejected implementation into the new candidate.** Continue
   on the existing isolated Codex task branch from current master. A separate
   integration branch would add no benefit while neither rejected branch is a
   valid input. Requirements and counterexamples inform the rebuild; old code
   does not become accepted by appearing in a combined tree.
2. **Preserve the frozen branch as historical evidence only; rebuild from the
   roots.** Do not repair, retest for acceptance, or publish a third correction of
   `b79922dc`. Keep source read failures distinct from absence, and representation
   errors distinct from valid YAML merge semantics. The new execution entry is a
   bounded replacement approach, not a claim to have repaired the old measurement
   harness or reproduced all its features.
3. **Do not integrate phase1 into master first.** Its older base alone is not a
   rejection reason, but its known defects and missing acceptance are. Importing
   it would not solve the seven existing master reference mismatches. No master
   publication, freeze waiver, or independent-review waiver is inferred.

The reported C1–C3 exact-ref counts may be cited only as outputs of the identified
measurement method, not as correct population/oracle/causal evidence. C4 is not
used. The two legal YAML merge fixtures stay unchanged; the duplicate-key claim
has been withdrawn. Worktree existence alone cannot prove historical immutability.

## Bounded dependency repair owned by this task

The failed `46acc091` managed attempt remains failed and preserved. Its third
check stopped on seven stale reference wrappers already present in master.

- Target: `01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml`.
- Old declared Git blob: `9c2828be3231ffd5370f9170cd67c1af61347bcb`.
- Actual current-master Git blob: `0a49b85a4518dc123b3c01e3a46f5454d9a55cc1`.
- Upstream semantic change: `04c0f4c3200c5008f686a7d74a389325623224b4`.

The target already on master uses delegated-start v2.1 (no ordinary plaintext
task-code relay; verified delegation plus exact identity/action/scope). It is not
a whitespace change. This repair does not enact, extend or reinterpret the target's
authority mechanism. The authoritative activation record already sets this mechanism
to `active_dormant`, globally loadable/discoverable without creating a live session
by default. Its explicit supersession covers the older profile contract's
`staged_inert`/`candidate_state` text; that historical text is not current runtime
state. This repair changes neither existing activation nor the always-on current
ordinary-communication rules. Updating a blob reference is not a new activation or
a declaration that all target semantics have been independently reviewed here.

The task packet is explicitly amended **before canonical edits** with seven exact
wrapper paths, limited to their `profile_contract_ref` blob. No target contract,
profile payload, validator threshold or expected check exit code changes are
authorized by this amendment. This minimal consistency repair follows the selected
clean-baseline route and the existing implementation delegation. Any further
load-bearing dependency/semantic change outside this boundary remains a stop.

Current per-stage confirmation language and the production instance validator's
authority requirements have not converged with ordinary task-scope policy. Those
requirements are not covered by the activation-state supersession. The target
cannot be dismissed wholesale as historical-only: its instance validator is still
on the v2 CLI call path. See `remaining_semantic_boundary.md` for primary references
and the proposed correction boundary. The pin-only repair neither resolves nor
accepts this mismatch; it remains work under the original foundation objective.

## Verification and next boundary

Inspect the target and wrappers, repair only those pins, run the existing static
checks, and execute the complete **unchanged** required-check plan on a new clean
exact commit. Preserve complete logs and the earlier failed attempt. Publish only
the task branch with enabled local hooks and non-force fast-forward behavior, then
read the remote SHA back. A green managed run means these required checks ran; it
does not mean independent acceptance or global enforced OS operation.

Fresh independent review and a Human integration/deployment decision remain later
boundaries. This implementation team's helper audit is not that independent review.
