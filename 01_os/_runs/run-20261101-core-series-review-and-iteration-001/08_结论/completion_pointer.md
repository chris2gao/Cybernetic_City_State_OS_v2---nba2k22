# Core OS · Evidence-driven Loop + Series Review · Completion Pointer

task_id: `OS-CORE-EVIDENCE-LOOP-SERIES-REVIEW-20261101-001`

source_branch: `task/core-risk-based-series-review-cadence-20261101`
source_base: `934425cf43d4fe3307b0112142aec1ba434a5734`
source_candidate_before_this_pointer: `bc1b751dbdc089c2d3dda04b1282d7bf66ed3525`

## What changed

- Revised the existing OS task entry section 6/8/9 instead of creating a parallel review mechanism: eligible candidate tasks may defer independent review until a coherent series milestone; named high-risk, load-bearing and protected integration boundaries require prior review.
- Added a default internal `evidence_driven_iteration` policy to the existing big-task orchestration contract, modeled on the WorldData/Codex 37-increment development, with falsifiable increments, actual tests, evidence and checkpoints, no fixed round count or promise of mathematical optimum.
- Retained reviewer/executor separation, Human protected-action authority, stage7 workflow completion, immutable historical facts, existing lifecycle enum and the original big-task machine-interpreted `internal_continuation`/`genuine_stop`/`closure_preflight` sections.
- Refreshed existing task-orchestration registry description and Global Agent Working Discipline reference.

## Verified and not verified

- Source-scope plus 11 explicit static checks: PASS as recorded in `07_测试执行/static_source_checks.md`. These are static source readback/compare checks, **not independent review**.
- Pytest and full YAML parser check: NOT_RUN (no Core worktree in this session). Required before Core master integration.
- Process exception: Run task packet landed after initial canonical branch edit, disclosed in the static report. Not backdated.
- Real automated loop runner: NOT_IMPLEMENTED; this change sets policy/contract defaults only.
- Independent review: PENDING. Human Core master integration approval: NOT_REQUESTED.
- Actual NBA2K22 WorldData prior closeout: engineering baseline only; original full goal remained incomplete.

## Review scheduling

This **Core-global canonical policy** is itself load-bearing and requires **immediate independent review before master integration**. Routine *downstream domain candidate tasks* can defer their independent review when they meet section9.1 criteria; no retrospective alteration of prior final verdicts.

next_owner: `Human / independent_review at Core master integration boundary`

No master merge or protected action has been performed.

## 2026-11-01 Human scope clarification (candidate branch addendum)

Human explicitly clarified that `evidence_driven_iteration` is **development-phase only**: research/engineering iterations within an authorized development task. It is not an additional stage, state machine, or substitute for the existing seven-stage Workflow or its Human/independent verification gates. The VAE gameplay feedback loop is a separate application/runtime concept, not automatically activated or authorized by this Core policy.

This clarification was incorporated into `大任务与长时执行契约_v1.yml` (`scope: development_phase_only`) and the OS entry section 8.1. This is a subsequent branch update; the earlier static check receipt does **not** verify these subsequent bytes. Source-diff and full tests must be refreshed at Core integration.
