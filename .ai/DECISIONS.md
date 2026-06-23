# AI Handoff Decisions

## D-0001 — Adopt AI Handoff Protocol v0.3-core

- Status: accepted
- Scope: AI handoff, mailbox, review, and coordination
- Decision: Use `.ai/PROTOCOL.md` as the canonical handoff protocol.
- Boundary: It does not override domain content rules, platform instructions, explicit human instructions, or secrets safety boundaries.

## D-0002 — Use a disposable review branch

- Status: accepted
- Decision: Use `ai/review/latest` for current review snapshots.
- Boundary: The review branch is not merged into source branches.
- Source push: Requires explicit human approval.

## D-0003 — Stage ChatGPT writeback

- Status: accepted
- Decision: Phase 1 uses Codex-only review-branch writes.
- Future: ChatGPT writeback must be tested and approved before enablement.
- Lease rule: An explicit expected-SHA lease is required once ChatGPT writeback is enabled.

## D-0004 — Use completion-preserving long-run execution

- Status: accepted
- Decision: Human-authorized long-run programs should complete one coherent objective by folding necessary in-scope cleanup, validation, alignment, report, and repair steps into the current run.
- Boundary: New authority, objective change, forbidden paths, destructive Git, source/master push, secrets risk, Coordinator/runtime activation, automation enablement, or unrelated business/domain scope still require explicit Human approval.
