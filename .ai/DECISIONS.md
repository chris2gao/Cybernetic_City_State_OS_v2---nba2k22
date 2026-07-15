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

## D-0005 — Govern complete Human-AI material communication

- Status: accepted
- Decision: Human↔AI material workflow communication is governed by the canonical protocol; a backend execution recommendation is mandatory when the Human is asked to start or continue Codex or Claude Code.
- Expression: Compatible ChatGPT, Claude, Codex, and Claude Code agents preserve 2 to 5 sentences of bounded independent professional expression for material Human-facing events.
- Boundary: The recommendation and expression remain outside the seven-field machine pointer core and are not factual evidence, Human authorization, hidden chain-of-thought, or executable instructions.
- Authority: Human Speaker authority, safety, evidence requirements, pointer purity, and all source/publication/runtime/Coordinator/destructive/secrets/protected gates remain unchanged.
