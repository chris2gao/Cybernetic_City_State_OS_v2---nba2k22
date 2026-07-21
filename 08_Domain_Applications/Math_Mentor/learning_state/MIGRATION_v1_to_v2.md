# Migration specification: learning-state store v1 -> v2

Status: **specification only.** No utility is implemented, and nothing has been
migrated. Any local v1 store remains `reported_local_unverified` and
`quarantined_pending_migration`.

Privacy note for this file: it describes the procedure in the abstract. It does
not name a learner, an alias, an event count, or which material a learner
studied. Those details stay in the local store.

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
must supply the missing evidence from the session record, or the event is omitted from the v2 replay.

## Principles

1. **Non-destructive.** The v1 store is copied, never edited in place. The
   original remains readable as historical evidence.
2. **No fabrication.** A migration tool must not invent `trap_evidence`, a
   restatement, or a timestamp. Missing evidence is either supplied by a Human
   from the session record, or the event is omitted from the v2 replay and recorded in the migration report.
3. **Omit, do not rewrite.** If the evidence for a `classroom_passed` event
   cannot be reconstructed, that event is **omitted from the v2 replay** and
   recorded in the migration report. It is NOT rewritten into a synthetic
   `introduced -> introduced` step: inventing an event is its own falsification.
   The node simply retains whatever prior state the replayed events establish.
   Losing a status is acceptable; asserting an unevidenced pass is not.
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
     session record; if it cannot be supplied, omit the event entirely and log it;
   - drop any `correction` event and record it in the migration report;
   - note that v2 additionally requires typed review windows, so any v1 review
     history must be re-derived rather than carried over.
3. Create the fresh v2 store's `store_meta.yml` first, and validate it against
   `learning_store_meta.schema.json`. It must declare the canonical
   `schema_version`, an opaque `store_id` matching the required pattern, the
   privacy-safe `bound_student_ref`, and a `bound_epoch` equal to the package's
   canonical epoch. Without a valid binding the store refuses to open, and the
   directory name grants nothing.
4. Write candidates into that store using `append_event.py`, so every event
   passes the v2 validator, reducer, chain, store binding and tail anchor on the
   way in.
5. Compare the derived snapshots of the v1 archive and the v2 store; record every
   status that changed and why.
6. Have the Human review the migration report before the v2 store is used.

## Dependency cascade when an event is omitted

Omitting an event is not a local edit. Every later event whose `transition.from`
depended on the omitted state becomes unreplayable, because its starting status
no longer exists in the rebuilt history.

For each omitted event, walk forward through the remaining candidates:

1. If a later event's `transition.from` is still reachable in the rebuilt
   sequence, keep it.
2. If it is not reachable, the event **must not be carried over as written**. It
   is either
   - re-derived with real Human-supplied evidence for the corrected
     `transition.from`, or
   - omitted too, and recorded in the migration report with the reason
     "cascade from <omitted event id>".
3. Repeat until no unreachable `transition.from` remains. Omissions can chain:
   dropping a `classroom_passed` invalidates any later `review_due` that started
   from it, which in turn invalidates its `review_passed`.

Never repair a cascade by rewriting `transition.from` to whatever the rebuilt
state happens to be. That silently invents a history the evidence does not
support, which is the same falsification principle 3 forbids.

The migration report must list, for every omitted event: its id, whether it was
omitted directly or by cascade, and which omission it cascaded from.

## Current disposition

One local v1 store was self-reported as having been written. It is **not**
migrated and remains quarantined. Its contents - learner alias, event count, node
identities, and status detail - stay in the local store and are deliberately not
described here, because a summary of what someone studied and how they performed
is itself learner data.

At migration time, any event whose required v2 evidence cannot be supplied from
the session record is omitted and logged, per principle 3 above.
