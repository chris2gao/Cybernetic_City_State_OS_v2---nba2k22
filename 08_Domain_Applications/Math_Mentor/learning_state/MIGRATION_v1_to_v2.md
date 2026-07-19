# Migration specification: learning-state store v1 -> v2

Status: specification plus a Human-run utility. **Nothing has been migrated.**
The existing local v1 store is `reported_local_unverified` and
`quarantined_pending_migration`.

## Why a migration is required

The 2026-07-19 independent review changed transition and evidence semantics, so
v1 events cannot be reinterpreted under v2 without inspection:

| change | effect on a v1 event |
|---|---|
| `student_ref` now required | v1 events may omit it |
| `source_ref`, `evidence_timestamp`, `evidence_limitations` now required | v1 required only `source_type` |
| `classroom_evidence` required for `classroom_passed` | absent in v1; the exam result, covered subtopics, restatement and trap evidence were never captured |
| `review_window_id` required to enter `review_due` | absent in v1 |
| `correction` disabled | a v1 store containing one cannot be replayed |
| epoch bumped | every v1 event fails the v2 epoch check by design |

The missing classroom evidence is the substantive problem: v2 asks for facts that
v1 never recorded. Migration therefore **cannot be fully automatic** - a Human
must supply the missing evidence from the session record, or accept a downgraded
event.

## Principles

1. **Non-destructive.** The v1 store is copied, never edited in place. The
   original remains readable as historical evidence.
2. **No fabrication.** A migration tool must not invent `trap_evidence`, a
   restatement, or a timestamp. Missing evidence is either supplied by a Human
   from the real session record, or the event is downgraded.
3. **Downgrade beats overclaim.** If the evidence for `classroom_passed` cannot
   be reconstructed, the migrated event records `introduced` instead. Losing a
   status is acceptable; asserting an unevidenced pass is not.
4. **Human-run.** No automatic migration on load, and no migration triggered by
   a model.
5. **Synthetic testing only.** Migration logic is tested against temporary
   synthetic stores. Tests never read or write a real learner store.

## Procedure

1. Copy `<store>` to `<store>.v1-archive` and leave it read-only.
2. For each v1 event in numeric order, produce a v2 candidate:
   - carry over `node_ref`, `transition`, `student_ref` (or supply the learner key);
   - set `learning_state_epoch` to the v2 bound epoch;
   - fill `source_ref` / `evidence_timestamp` / `evidence_limitations`, marking
     reconstructed values explicitly in `evidence_limitations`;
   - for a `classroom_passed` transition, attach `classroom_evidence` from the
     session record, or downgrade the target to `introduced`;
   - drop any `correction` event and record it in the migration report.
3. Write candidates into a fresh store using `append_event.py`, so every event
   passes the v2 validator, reducer, chain and tail anchor on the way in.
4. Compare the derived snapshots of the v1 archive and the v2 store; record every
   status that changed and why.
5. Have the Human review the migration report before the v2 store is used.

## Current disposition of the No.1 store

Two v1 events exist locally (an `introduced` and a `classroom_passed` for the
first propositional-logic lesson). They are **not** migrated. They are quarantined
and remain the property of the local store; no learner detail is published in the
repository. The `classroom_passed` event will need its exam evidence supplied
from the session record, or be downgraded, at migration time.
