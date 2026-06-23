# POST-P2 Execution Memory P3 Onward Replan Review

## Task Profile

- Packet: `codex-post-p2-execution-memory-p3-onward-replan-0001`
- Declared task level: 1
- Mode: planning-only documentation rewrite
- Source baseline: `68adac5d34edd2947851fb5b9e5daafa79012836`
- Source publication: forbidden
- Semantic reviewer: ChatGPT, followed by the Human gate for future program launch

## Evidence Read

- `08_Domain_Applications/Math_Mentor/POST_P2_EXECUTION_MEMORY.md`
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`
- `08_Domain_Applications/Math_Mentor/KNOWLEDGE_COMPLETION_PROGRAM.md`
- `.ai/PROTOCOL_ADHERENCE.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/OUTBOX.md`
- `.ai/HUMAN_BRIEF.md`
- `.ai/STATE.yml`

`.ai/CODEX_REPORTS/p2-10-b-to-p3-closure-plan.md` is absent from the current source tree and was therefore skipped under its `if present` condition.

## Rewrite Scope

The initial replan replaced only the roadmap block beginning at the former P3 heading and ending before `## 6. Knowledge Node Quality Concerns`. The subsequent ChatGPT cleanup added an explicitly authorized pre-P3 factual-status overlay and corrected obsolete P2 status lines without replanning any pre-P3 stage definition.

Preservation evidence after newline normalization:

- pre-P3 prefix SHA-256: `9092724907093cdf0f7acaa9503f0ebc336f242e3e6d7d889287fb1eb79e834e`
- post-roadmap suffix SHA-256: `18215e076ed38b96badf1c863574f641da1d57549cd8788d10212f200e0e500f`

Both hashes matched the initial replan's pre-edit baseline. The cleanup intentionally supersedes exact whole-prefix/suffix hash equality only at the authorized status-overlay and obsolete-status lines; all other pre-P3 stage definitions and later quality rules remain unchanged.

## New Program Roadmap

| Program | Absorbed or governed scope | Required predecessor |
| --- | --- | --- |
| P3-LRP Bridge Completion Program | Former P3-P7 bridge design, landing, review, completion, and Mode B mapping audit | accepted KCP repair/endpoints plus explicit P3 launch |
| P8-LRP Math Mentor Runtime Integration Program | Coordinator consumption draft, teaching runtime, Exam Agent, spaced review, runtime regression, user workflow | accepted P3-LRP |
| P9/P10-LRP Master Merge And Global City-State OS Integration Program | legacy/master comparison, `08` and non-08 reports, dry run, conflict plan, integration proposal | accepted P8-LRP |
| P10+-LRP AI Handoff Protocol Evolution Program | communication/control-layer evolution, permissions, rollback, audit, memory, checkpoints, Human gates | accepted P9/P10-LRP and stable Math Mentor |

Each program now states its goal, inputs, outputs, entry and exit criteria, allowed and forbidden scope, long-run log, review branch naming, Codex and ChatGPT roles, Human gate, rollback, final status model, and non-blocking issue policy.

## Preserved Integration Principles

- Math Mentor under `08_Domain_Applications` prefers the reviewed `legacy-mode-a-outsourcing` content and may cover master's `08` only after review.
- The non-08 global OS likely uses `master` as its base.
- Legacy parliament, execution plans, and context documents remain a memory/history layer.
- No direct source or master push is part of planning or dry-run authority.

## Execution Boundary

The order is P3-LRP → P8-LRP → P9/P10-LRP → P10+-LRP. Planning/evidence work may be parallel when it does not mutate shared state; source integration, official runtime consumption, merge, and protocol activation remain sequential and separately Human-authorized.

This task did not start P3 or any LRP, generate or modify bridges, execute runtime integration, modify an index or schema, create an integration branch, merge master, enable automation, or push a source branch.

## ChatGPT Cleanup Fixes Applied

- Replaced the ambiguous five-item P3-LRP limit with a default internal checkpoint batch size, explicit multi-batch continuation, and a no-silent-promotion rule.
- Corrected the P3 boundary so it does not imply that this document contains an independent P2.10 history section.
- Added a factual Current Actual Status Overlay and replaced the stale `P2 currently executing` / `Do not interrupt P2` statements.
- Applied the final top-status consistency fix so `Current completed stages` points to the Current Actual Status Overlay instead of describing P2 as in progress.
- Preserved the four LRP structures, execution order, non-goals, and all execution gates.
- Prepared mailbox metadata to reference the concrete pushed cleanup review head after publication.

## Review Request

ChatGPT should review program boundaries, entry/exit gates, preserved merge principles, and whether the four programs are decision-complete. A later Human-approved launch packet is required for every LRP execution and for all source publication or merge actions.
