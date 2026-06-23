# POST-P2 Execution Memory for Math Mentor

## 0\. Purpose

This document is a continuation anchor for the Math Mentor branch after P2.

It records the agreed execution plan, model reasoning levels, subagent usage policy, quality audit insertion point, and deferred master-merge strategy.

If conversation context becomes full, future agents should read this document before continuing any post-P2 work.

---

## 1\. Current Branch Context

Repository:

chris2gao/Cybernetic\_City\_State\_OS\_v2---teacher

Active branch:

legacy-mode-a-outsourcing

Current completed stages:

P0    Coordinator Prompt \+ Bridge Completion Plan committed  
P1    Bridge Registry Audit completed  
P1.5  Bridge Registry Audit committed  
P2-P2.9 completed or superseded by later reviewed reports; see Current Actual Status Overlay below.

Known commits:

P0 commit:   7ef25db  
P1.5 commit: f76feb3

### Current Actual Status Overlay

This overlay is a factual status refresh only. It does not replan the pre-P3 stages.

\- P2 Canonical Bridge Schema: completed
\- P2.5 BRIDGE_SCHEMA commit: completed
\- P2.7 Knowledge Node Quality Audit: completed as audit plan, sample pack, and decision; not full-node repair
\- P2.8 Evaluator / Quality Gate Upgrade: completed
\- P2.9 Regeneration Decision: completed as a classify-first, no-full-regeneration-by-default decision
\- P2.10-B / KCP follow-up: `completed_with_blockers` and accepted as `accepted_with_blockers`
\- P3 gate: closed

No source publication, bridge indexing, Coordinator activation, or master merge is authorized by this refresh.

Current rule:

P2 is completed; P3 remains closed until an explicit Human-approved P3 launch.
Do not merge or push master.
Do not push `legacy-mode-a-outsourcing`.
Do not index bridges or activate Coordinator consumption.

---

## 2\. Core Execution Principle

The project uses manual model reasoning-level switching.

The assistant cannot automatically switch High / Extra High reasoning levels. Therefore, every stage must stop at its boundary so the user can manually switch reasoning level.

Stage boundary means:

1\. Finish one cognitive task.  
2\. Stop.  
3\. Output a handoff package.  
4\. User manually switches reasoning level.  
5\. Continue next stage.

---

## 3\. Model Reasoning Level Policy

### High

Use High for:

\- architecture review  
\- Coordinator / Universal Protocol consistency check  
\- commit review  
\- schema review after draft  
\- batch validation review  
\- bridge YAML review

### Extra High

Use Extra High for:

\- canonical schema final decision  
\- Level 4-6 mathematical bridge design  
\- Mode A / Mode B / mixed final judgment  
\- node quality audit final judgment  
\- regeneration decision  
\- Mode B LLM architecture mapping repair  
\- master vs legacy merge strategy  
\- global City-State OS philosophy review

### Standard / Codex

Use Standard / Codex for:

\- git status / diff / commit  
\- file writing from confirmed design  
\- YAML formatting  
\- index checking  
\- schema lint  
\- reference existence checks  
\- dry-run merge execution

---

## 4\. Subagent Usage Policy

Subagents may be used only as:

Worker  
Auditor  
Extractor  
Formatter

Subagents must not act as:

Architect  
Judge  
Final Reviewer  
Mathematical Arbiter  
Merge Strategist

Allowed subagent tasks:

\- file inventory  
\- schema lint  
\- YAML formatting  
\- duplicate ID checking  
\- index registration checking  
\- node field extraction  
\- reference existence checking  
\- generating files from confirmed design tables  
\- git status / diff / commit  
\- merge dry-run conflict listing

Forbidden subagent tasks:

\- final canonical schema decision  
\- Level 4-6 bridge mathematical judgment  
\- Mode A / Mode B / mixed final judgment  
\- abstract concept teaching bridge design  
\- master vs legacy merge strategy  
\- directory overwrite decisions  
\- global City-State OS philosophy judgment  
\- final merge approval

Subagent rule:

A subagent may prepare evidence.  
The main thread makes the decision.

---

## 5\. Post-P2 Stage Roadmap

### P2 \- Canonical Bridge Schema

Status:

Completed.

Recommended reasoning level:

GPT-5.5 Thinking Extra High

Expected artifact:

08\_Domain\_Applications/Math\_Mentor/BRIDGE\_SCHEMA.md

P2 must stop after drafting the schema. Do not commit until review.

---

### P2.5 \- Commit BRIDGE\_SCHEMA.md

Recommended reasoning level:

High for review  
Codex Standard for commit

Allowed action:

Commit only BRIDGE\_SCHEMA.md

Forbidden:

No push  
No master merge  
No bridge YAML generation  
No Pure\_Math\_Intuition\_DB node edits

---

### P2.7 \- Knowledge Node Quality Audit

This stage must be inserted before P3.

Reason:

Bridge design depends on node quality.  
If Pure\_Math\_Intuition\_DB nodes are low quality, bridge generation will connect unstable concepts.

Recommended reasoning level:

GPT-5.5 Thinking Extra High

Subagent use:

Allowed only for sample extraction and evidence gathering.  
Final quality judgment must remain in the main thread.

Expected first artifact:

08\_Domain\_Applications/Math\_Mentor/NODE\_QUALITY\_AUDIT\_PLAN.md

Expected second artifact:

08\_Domain\_Applications/Math\_Mentor/NODE\_QUALITY\_AUDIT\_SAMPLE\_PACK.md

Do not regenerate nodes during P2.7.

---

### P2.8 \- Evaluator / Quality Gate Upgrade

Recommended reasoning level:

High

Purpose:

Upgrade the validator language and quality gate so it no longer overclaims mathematical soundness.

Potential changes:

\- rename "mathematically sound" claims to "executable sanity checks passed"  
\- add Mode A quality gate  
\- add Mode B semantic audit gate  
\- add shape-only test detection  
\- add property-test requirement for computable nodes

Codex may execute implementation after main-thread approval.

---

### P2.9 \- Regeneration Decision

Recommended reasoning level:

GPT-5.5 Thinking Extra High

Decision options:

1\. no regeneration, continue bridge  
2\. validator-only upgrade  
3\. local mapping/audit repair  
4\. single-node regeneration  
5\. level/domain-specific regeneration  
6\. full regeneration only if failure rate is extreme

Default rule:

Do not full-regenerate the database by default.  
First classify failure type.

---

### P3 Onward Replan Boundary

All pre-P3 factual memory already present in this document is unchanged except for the explicitly authorized current-status refresh. Later P2.10 records are tracked in AI review reports and are not rewritten by this P3-onward roadmap. The following roadmap replaces only the former P3-P10+ sequence with ordered Long-Run Autonomous Programs. It is a planning contract, not an execution authorization.

---

### P3-LRP \- Bridge Completion Program

Absorbs the former P3 Level 4 Batch 1 Bridge Design, P4 Bridge YAML Landing, P5 Batch Review, P6 Level 4-6 Bridge Completion, and P7 Mode B Mapping / Metaphor Audit stages.

Goal:

Complete mathematically justified Level 4-6 bridge design, canonical bridge landing, mode-correct validation, and the associated Mode B mapping audit as one authorized long-run program with internal batches and checkpoints.

Input artifacts:

\- accepted KCP post-run review and targeted repair results
\- named bridge-ready endpoint registry on an immutable source head
\- `BRIDGE_SCHEMA.md`, split Level 4-6 roadmaps, bridge registry audit, and Coordinator contract
\- existing bridge files and next available bridge ID
\- Mode B semantic-review evidence and mapping-boundary findings

Output artifacts:

\- run manifest, stage checkpoints, and consolidated final report
\- reviewed bridge design tables and canonical schema-v1 bridge YAML batches
\- bridge validation ledger and rejected/deferred candidate ledger
\- draft registry/index proposal without formal index mutation
\- Mode B mapping/metaphor audit and targeted repair proposal
\- post-run repair cohorts for unresolved endpoints or bridges

Entry criteria:

\- KCP post-run repair has produced a named endpoint set satisfying `bridge-ready`
\- ChatGPT has reviewed the endpoint evidence and the Human has explicitly opened P3
\- the launch packet names the immutable source head, exact scope, next bridge ID, allowed paths, and publication policy
\- bridge design, generation, and validation authorities are explicit
\- internal bridge checkpoint batch size defaults to at most five accepted bridge candidates unless a launch packet explicitly authorizes a different batch size
\- the full P3-LRP may continue across multiple internal batches
\- unresolved endpoints must not be silently promoted

Exit criteria:

\- every in-scope candidate is validated, rejected, or explicitly deferred
\- every landed bridge matches an approved design, schema `1.0`, explicit endpoints, and a justified A/B/mixed route
\- Mode B bridges and mappings have ChatGPT semantic review and no machine-pass overclaim
\- bridge IDs, files, endpoint references, and draft registry entries reconcile
\- all accepted outputs have rollback checkpoints and a final ChatGPT review package
\- bridges remain draft/unindexed until P8-LRP authorizes runtime consumption

Allowed write paths:

\- explicitly approved new `Pure_Math_Intuition_DB/BRIDGE-*.yaml` files
\- explicitly named Mode B node mapping/audit fields only when the launch packet authorizes targeted repair
\- `.ai/PROGRAM_RUNS/<run_id>/**`, `.ai/LONG_RUN_LOGS/p3-lrp-<run_id>.md`, and `.ai/CODEX_REPORTS/**`
\- mailbox files needed for the final review handoff

Forbidden paths and actions:

\- old bridge mutation, formal index mutation, Coordinator runtime activation, evaluator/schema redesign, staging/generated output, automation, secrets, and unrelated domains
\- source-branch push, master push, direct merge, or bridge generation outside the approved endpoint/design set

Long-run log path:

`.ai/LONG_RUN_LOGS/p3-lrp-<run_id>.md`

Review branch naming:

`ai/p3-lrp-<run_id>-review`

Codex role:

Build evidence, implement only approved designs, validate deterministic structure and Mode A claims, maintain checkpoints, and quarantine unresolved work without inventing mathematical connections.

ChatGPT review role:

Judge bridge mathematics, teaching usefulness, A/B/mixed routing, Mode B semantic quality, and whether a candidate may proceed to Human review.

Human gate:

Required for launch, P3 opening, disputed mathematics, targeted regeneration, source integration, formal indexing, Coordinator admission, and any source publication.

Rollback policy:

Use narrow batch commits and revert only the failing checkpoint. Preserve accepted earlier batches and issue evidence; never use destructive reset or renumber accepted bridge IDs silently.

Final status taxonomy:

`completed_clean`, `completed_with_review_log`, `completed_with_blockers`, `blocked_preflight`, or `failed_and_reverted`.

Non-blocking issue log policy:

Record local mathematical ambiguity, endpoint uncertainty, Mode B semantic disputes, protected-file skips, and scope candidates in the long-run log; mark affected work `review_required` or deferred and continue independent authorized batches. Apply the three-attempt budget per stable failure signature.

---

### P8-LRP \- Math Mentor Runtime Integration Program

Goal:

Integrate accepted bridges and completed teaching objects into the Math Mentor runtime while preserving explanation-first teaching, learned-history filtering, Exam Agent graduation, and spaced-review scheduling.

Input artifacts:

\- accepted P3-LRP bridge set and validation ledger
\- canonical bridge schema and approved draft registry/index proposal
\- Coordinator prompt, teaching-flow specification, Exam Agent contract, spaced-review scheduler, and persisted learning-history rules
\- user-facing lesson workflow and existing runtime regression evidence

Output artifacts:

\- Coordinator consumption draft and explicit draft-to-official admission table
\- teaching runtime integration patches on an isolated authorized branch
\- bridge lookup, learned-history, association-slot, and first-display tests
\- Exam Agent and spaced-review handoff regression results
\- user-facing learning workflow report and consolidated runtime regression report

Entry criteria:

\- P3-LRP has completed and ChatGPT/Human have accepted the named bridge set
\- runtime scope, official-consumption authority, immutable source head, and allowed files are explicit
\- every candidate bridge is validated; draft, rejected, and official states are distinguishable

Exit criteria:

\- Coordinator lookup and compressed first display work for the accepted set
\- teaching still proceeds intuition → formal definition → all subtopics → guided questions → definition restatement
\- Exam Agent trap handoff and classroom-pass spaced-review handoff pass regression
\- the user can complete the end-to-end learning workflow without bypassing mastery evidence
\- draft/unindexed bridges remain hidden or teaser-only; only separately approved indexed bridges become official
\- runtime regressions, exceptions, rollback points, and final review evidence reconcile

Allowed write paths:

Only the Coordinator, explicitly named teaching-runtime/Exam/review integration files, approved index entries, tests, run artifacts, and mailbox paths named by the launch packet.

Forbidden paths and actions:

No unrelated node regeneration, evaluator redesign, schema rewrite, broad index replacement, automation enablement, master merge, source push, or promotion of draft bridges without the official-consumption gate.

Long-run log path:

`.ai/LONG_RUN_LOGS/p8-lrp-<run_id>.md`

Review branch naming:

`ai/p8-lrp-<run_id>-review`

Codex role:

Implement the approved runtime contract, run deterministic integration/regression checks, keep draft and official states separate, and record failures without simulating student mastery.

ChatGPT review role:

Review teaching-flow semantics, Coordinator behavior, user-facing workflow, Exam/review continuity, and any proposed official bridge admission.

Human gate:

Required for program launch, official Coordinator consumption, teaching-policy changes, source publication, and any acceptance that changes the student-visible runtime.

Rollback policy:

Revert the smallest runtime/index batch, restore the last accepted Coordinator and scheduler checkpoint, and keep rejected bridges non-consumable.

Final status taxonomy and non-blocking issues:

Use the standard long-run status taxonomy. Log local integration defects, incomplete learned-history evidence, draft/official ambiguity, and isolated regressions; continue independent testable work unless runtime safety or the official-consumption gate blocks the remaining scope.

---

### P9/P10-LRP \- Master Merge And Global City-State OS Integration Program

Merge principles preserved from the former roadmap:

\- `08_Domain_Applications/Math_Mentor/` should prefer `legacy-mode-a-outsourcing` and may fully cover master's `08` only after review
\- the non-08 global OS should likely use `master` as its base
\- legacy parliament, execution plans, and context documents must be preserved as a memory/history layer

Goal:

Design, dry-run, review, and only after separate authorization execute a controlled integration of the stabilized Math Mentor system with the global City-State OS.

Input artifacts:

\- accepted P8-LRP runtime baseline and regression report
\- current immutable tips of `legacy-mode-a-outsourcing` and `master`
\- architecture/context documents, preserved-history inventory, and branch publication policy

Output artifacts:

\- `legacy-mode-a-outsourcing` versus `master` comparison
\- dedicated `08` directory diff report
\- non-08 global OS diff report
\- merge dry-run report and conflict-resolution plan
\- preserved memory/history manifest
\- integration-branch proposal with exact commit range, tests, rollback, and publication gates

Entry criteria:

P8-LRP must be accepted and stable. Planning authorization may open comparison and dry-run work, but integration-branch creation, conflict resolution, source publication, and master merge each require the authority stated in a separate Human-approved packet.

Exit criteria:

\- every `08` and non-08 difference is classified by ownership and intended base
\- the dry run has a reviewed resolution for every conflict and preserves the legacy memory/history layer
\- the integration branch passes the agreed Math Mentor and global OS regression suites
\- no source or master publication occurs without its separate Human gate
\- final ChatGPT review recommends accept, revise, partial integration, or rollback

Allowed write paths:

Planning reports and run artifacts are allowed first. An isolated integration branch and conflict-resolution edits are allowed only after the launch packet names exact paths and authority.

Forbidden paths and actions:

No direct master push, no direct source push by default, no unreviewed whole-directory overwrite, no deletion of legacy memory/history, no destructive history rewrite, and no merge merely because a dry run succeeds.

Long-run log path:

`.ai/LONG_RUN_LOGS/p9-p10-lrp-<run_id>.md`

Review branch naming:

`ai/p9-p10-lrp-<run_id>-review`; proposed integration branches use `ai/integration/<run_id>` only after Human authorization.

Codex role:

Produce exact diffs, execute approved dry runs, implement the reviewed conflict plan on an isolated branch, run regressions, and preserve rollback evidence.

ChatGPT review role:

Judge ownership boundaries, merge strategy, conflict semantics, architectural consistency, and preservation of historical memory.

Human gate:

Mandatory for integration-branch execution, source publication, master merge, master push, destructive operations, and final acceptance.

Rollback policy:

Keep immutable pre-integration tips, use reversible integration commits, abandon an unsafe integration branch instead of rewriting protected history, and never use destructive reset on source or master.

Final status taxonomy and non-blocking issues:

Use the standard long-run status taxonomy. Log isolated conflicts, uncertain ownership, preservation questions, and scope candidates while continuing independent comparison and dry-run work; stop before any unauthorized integration or publication.

---

### P10+-LRP \- AI Handoff Protocol Evolution Program

Goal:

After Math Mentor and global integration stabilize, evolve lightweight `v0.3-core` handoff into a fuller Cybernetic City-State OS communication/control layer without turning coordination into excessive friction.

Input artifacts:

\- accepted Math Mentor and global integration baselines
\- current handoff protocols, review-branch history, failure logs, and Human/ChatGPT/Codex workflow evidence
\- explicit OS-level requirements for permissions, rollback, audit, memory, checkpointing, and Human review gates

Output artifacts:

\- reviewed control-layer architecture and authority model
\- permission, rollback, audit, memory, checkpoint, replay-protection, and Human-gate specifications
\- automatic protocol-validator design
\- ChatGPT GitHub writeback, expected-SHA lease, multi-agent conflict, packet compression, and mailbox identity designs
\- bounded prototypes and migration/compatibility plan when separately authorized

Entry criteria:

P9/P10-LRP must be accepted, Math Mentor stages must be stable, and a separate Human-approved launch packet must define whether the work is documentation, prototype, or repository-level control-plane implementation.

Exit criteria:

\- authority boundaries and failure recovery are explicit and testable
\- model freedom and emergence are preserved inside auditable boundaries
\- permissions, memory, rollback, checkpoints, and Human interrupt gates compose coherently
\- compatibility with lightweight pointer-based handoff is documented
\- no prototype becomes production governance without separate review and Human acceptance

Allowed write paths:

Approved `.ai` protocol/design files, isolated test/prototype paths, run artifacts, and mailbox files named by the launch packet.

Forbidden paths and actions:

No automatic authority escalation, unattended source mutation, secret access, business-domain rewrite, production automation enablement, or replacement of Human review by model consensus.

Long-run log path:

`.ai/LONG_RUN_LOGS/p10plus-lrp-<run_id>.md`

Review branch naming:

`ai/p10plus-lrp-<run_id>-review`

Codex role:

Implement approved protocol artifacts and bounded prototypes, validate mechanics, preserve compatibility, and report failure/recovery evidence.

ChatGPT review role:

Judge control-plane architecture, authority, model-freedom tradeoffs, multi-agent semantics, and governance safety.

Human gate:

Required for launch, permission expansion, GitHub writeback expansion, automation, repository-level control-plane activation, source publication, and governance adoption.

Rollback policy:

Keep `v0.3-core` as a recoverable compatibility baseline, introduce changes through versioned reversible commits, and disable or revert unsafe prototypes without rewriting history.

Final status taxonomy and non-blocking issues:

Use the standard long-run status taxonomy. Log unresolved governance choices, platform limitations, multi-writer races, and prototype gaps; continue independent documentation/testing while preserving every Human gate.

---

### P3+ Execution Order

1\. Execute P3-LRP before P8-LRP.
2\. Execute P8-LRP before P9/P10-LRP.
3\. Execute P9/P10-LRP before P10+-LRP.
4\. Planning and evidence preparation may proceed in parallel when they do not mutate shared source state.
5\. Source integration, official runtime consumption, merge execution, and protocol activation cannot proceed in parallel and require their preceding accepted baseline plus a separate Human authorization.
6\. Completion of one plan never auto-launches the next LRP.

### P3+ Replan Non-Goals

This documentation rewrite does not:

\- start P3 or any LRP
\- generate, validate, index, or consume a bridge
\- execute runtime integration
\- execute a master merge or create an integration branch
\- push `legacy-mode-a-outsourcing` or `master`
\- modify node, evaluator, bridge, index, schema, automation, staging, or generated files

---

## 6\. Knowledge Node Quality Concerns

Pure\_Math\_Intuition\_DB nodes were mainly generated by Gemini 3.1 Pro and checked once by GPT-5.5, but it is not yet confirmed that foundational node quality was deeply audited.

Known concern:

Some v8\_sanity\_audit blocks appear to test executable code or tensor shape rather than mathematical properties.

Therefore, before building bridges, audit node quality.

---

## 7\. Mode A Quality Gate

Mode A nodes should satisfy:

\- id  
\- title or name  
\- domain  
\- sub\_topics  
\- formal\_definition or definition skeleton  
\- realistic intuition  
\- llm\_physical\_mapping  
\- code\_implementation  
\- v8\_sanity\_audit.sympy\_pseudo\_code  
\- property-based test  
\- edge cases  
\- not shape-only

Recommended tools:

sympy  
numpy  
scipy  
hypothesis  
z3-solver  
networkx  
pyyaml  
jsonschema

---

## 8\. Mode B Quality Gate

Mode B nodes should satisfy:

\- id  
\- title or name  
\- domain  
\- sub\_topics  
\- formal\_definition or axiom skeleton  
\- prerequisite\_nodes  
\- LLM architecture mapping  
\- mapping boundary  
\- v9\_semantic\_audit  
\- no daily metaphor as primary mapping  
\- teaching usefulness  
\- analogy limitation

Mode B validation should not pretend to be full machine proof.

It should check:

\- definition accuracy  
\- analogy boundary  
\- misleading mapping risk  
\- prerequisite clarity  
\- teaching usefulness  
\- semantic consistency

---

## 9\. Regeneration Decision Rule

Do not default to full regeneration.

Use this decision matrix:

If only schema fields are missing:  
→ schema migration or field repair.

If v8\_sanity\_audit is shallow:  
→ upgrade tests, not full node regeneration.

If llm\_physical\_mapping is misleading:  
→ regenerate mapping / semantic audit only.

If definition or sub\_topics are wrong:  
→ single-node regeneration.

If one level or domain has \>30% failure rate:  
→ level/domain-specific regeneration.

If almost all samples fail across modes and levels:  
→ consider full regeneration with GPT-5.5 highest reasoning level.

---

## 10\. Resume Protocol After Context Reset

If context becomes full, future assistant should read in this order:

1\. PROJECT\_CONTEXT.md  
2\. ARCHITECTURE.md  
3\. AGENTS.md  
4\. CHANGELOG\_AI.md  
5\. 08\_Domain\_Applications/Math\_Mentor/POST\_P2\_EXECUTION\_MEMORY.md  
6\. 08\_Domain\_Applications/Math\_Mentor/BRIDGE\_SCHEMA.md  
7\. 08\_Domain\_Applications/Math\_Mentor/NODE\_QUALITY\_AUDIT\_PLAN.md, if it exists  
8\. current git status

Then continue from the latest completed stage.

---

## 11\. Current Non-Interruption Rule

P2 is completed. P3 remains closed until an explicit Human-approved P3 launch.

Do not treat this memory refresh, a review recommendation, or an accepted evidence branch as P3 execution authority.

Future work must resume from the Current Actual Status Overlay and the latest accepted review artifacts.
