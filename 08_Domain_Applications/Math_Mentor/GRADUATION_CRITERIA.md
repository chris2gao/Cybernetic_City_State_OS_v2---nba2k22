# Math Mentor Graduation Criteria

## 1. Classroom Pass Boundary

`classroom_passed` is a classroom result, not long-term graduation.

classroom_passed is a classroom result, not long-term graduation.

`classroom_passed` is not graduated.

It means:

- Exam_Agent tested the current lesson boundary;
- the student passed the current trap or direct application;
- the student's current definition restatement was acceptable for the session.

It does not mean:

- durable mastery;
- spaced-review completion;
- future bridge prerequisites permanently satisfied;
- `graduated`;
- scheduler update occurred.

## 2. Minimum Review Pass Requirements

Long-term `graduated` status may be claimed only after review-based evidence exists.

Minimum criteria:

```yaml
graduation_minimum:
  required_prior_status: "review_passed"
  minimum_review_passes: 2
  review_windows:
    - "near_term_retention"
    - "stability_review"
  required_evidence:
    - "review item refs"
    - "review result summaries"
    - "definition-boundary retention"
    - "trap or transfer test pass"
    - "timestamps"
    - "privacy-safe student ref"
  forbidden_shortcuts:
    - "classroom_passed only"
    - "node id ordering only"
    - "student confidence only"
    - "teacher praise only"
```

Exact interval lengths are deferred to a future authorized scheduler implementation.

## 3. Definition-Boundary And Trap-Retention Requirements

A graduation claim requires evidence that the student retained:

- the formal definition or criterion;
- the boundary between the concept and common false intuitions;
- at least one trap or transfer test after the initial classroom session;
- bridge comprehension when bridge-gated prerequisites are used formally.

Review evidence should reference the original `Cognitive_State_Vector` risks when possible.

## 4. Stability-Over-Time Requirement

Graduation requires stability across time, not one successful classroom moment.

Stable evidence includes:

- review attempts separated by due windows;
- successful handling of the previous false intuition;
- correct definition restatement without immediate teaching;
- no unresolved prerequisite blocker;
- no stale or overdue review state.

## 5. Stale And Downgrade Rules

`graduated` or `review_passed` may downgrade to `stale` when:

- a later review fails;
- due windows are missed beyond tolerance;
- the student fails the same definition boundary previously passed;
- bridge prerequisite status becomes invalid or unavailable;
- evidence provenance is found malformed or private-data unsafe.

`stale` does not erase all history. It means current teaching should re-check or remediate before using the node as a learned prerequisite.

## 5.1 Three Distinct Notions

These must never be used as synonyms:

| notion | what it is | who decides |
| --- | --- | --- |
| `graduation_evidence_candidate` | a **mechanical** calculation stating that the required evidence pattern is present in the current qualifying cycle | deterministic reducer; **not a grant** |
| `graduated` | a durable **status** | Human-gated transition only; no code persists it autonomously |
| learned-prerequisite usability | whether another node may rely on this one | `LEARNED_HISTORY_RULES.md`, subject to future stale checks |

A candidate is not graduated, and a graduated node is not automatically usable as a
learned prerequisite forever. No real spaced-review scheduler authority exists yet, so
candidacy is provisional by construction.

## 6. Graduation Claim Wording Constraints

Allowed wording:

- "graduated for this node under the current review policy";
- "long-term graduation criteria met as of <date>";
- "eligible to act as learned prerequisite, subject to future stale checks".

Forbidden wording:

- "permanently mastered forever";
- "classroom_passed means graduated";
- "lower node id proves mastery";
- "scheduler updated" without a real authorized write;
- "review passed" without review evidence.

## 7. Forbidden Shortcuts

Do not claim graduation from:

- `classroom_passed` alone;
- one Exam_Agent trap alone;
- student self-report alone;
- teacher confidence or praise;
- node id order;
- bridge index presence;
- semantic similarity;
- unlogged tool execution;
- unavailable learned-history state;
- placeholder scheduler warnings.
