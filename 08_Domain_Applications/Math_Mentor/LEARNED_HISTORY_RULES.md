# Math Mentor Learned History Rules

## 1. Evidence Priority Order

Learned status must be read from evidence in this priority order:

1. `persisted_learning_state`: persisted student learning-state record;
2. `spaced_review_result`: spaced-review scheduler state and review result record;
3. `registered_classroom_pass`: registered learned state explicitly produced by an authorized task;
4. `current_session_evidence`: current-session Exam_Agent `classroom_passed` evidence;
5. explicit Human override with scope and date;
6. `strict_sequence_node_id_comparison`: strict-sequential node id fallback, only when the current course explicitly guarantees strict sequential completion.

Lower-priority evidence cannot override contradictory higher-priority evidence.

## 2. Persisted State Read Rule

Before using learned-history state:

- read only the relevant student/node record, when authorized;
- record every physically read file in `actually_read_files`;
- record unavailable state as `unavailable`, not as mastery;
- do not read full student-state directories unless a future task explicitly authorizes it;
- do not read secrets, private notes, `.env`, tokens, keys, or unrelated personal data.

LRP-05 defines the rule only. It does not perform an actual persisted-state read or write.

## 3. Classroom Pass Rule

`classroom_passed` means:

- the student passed the current Exam_Agent trap;
- the current lesson's formal boundary was tested;
- the current `Cognitive_State_Vector` had enough information for Exam_Agent.

`classroom_passed` does not mean:

- long-term mastery;
- `graduated`;
- spaced-review pass;
- bridge prerequisite permanently learned;
- safe skipping of future review.

## 4. Spaced-Review Evidence Rule

Spaced-review evidence can strengthen learned status only when it includes:

- review item reference;
- due window or interval label;
- review result;
- trap or definition-boundary evidence;
- timestamp;
- source learning record;
- privacy-safe student reference;
- write authorization or read-only evidence status.

When scheduler evidence is unavailable, emit a scheduler warning or placeholder.

## 5. Node ID Ordering Fallback Limits

Node id ordering cannot prove mastery by default.

Allowed fallback:

```yaml
strict_sequence_fallback:
  allowed: true
  required_conditions:
    - "current course explicitly declares strict sequential completion"
    - "all lower nodes are known to have been taught in sequence"
    - "fallback is marked weaker than persisted or review evidence"
    - "fallback cannot produce graduated status"
  maximum_claim: "introduced_or_prerequisite_assumed_for_teaser"
```

Forbidden:

- `n_100 < n_200`, therefore `n_100` is mastered;
- lower node number used as bridge learned proof;
- node ordering used for `graduated`.

## 6. Missing State Degradation

If learned-history state is missing:

```yaml
learned_history_status: "unavailable"
bridge_teaching_status: "hidden | teaser_only | blocked"
mastery_claim: "not_claimed"
required_warning: "Learned-history state is unavailable; do not infer mastery."
```

Degradation rules:

- prerequisite bridge with unavailable state: hidden or blocked unless the lesson can safely review the prerequisite first.
- forward outlook bridge with unavailable state: teaser only.
- legacy bridge with ambiguous endpoints: omit and flag for migration.
- Exam handoff: allowed only if current-session teaching and definition restatement criteria are met; it does not solve missing long-term history.

## 7. Bridge Slot Gating

Bridge slot consumption depends on bridge type:

| bridge type | learned-history requirement | allowed teaching status when unavailable |
| --- | --- | --- |
| `prerequisite_bridge` | required nodes verified | `hidden` or `blocked` |
| `intra_layer` | endpoints verified or current lesson explicitly teaches both sides | `teaser_only` |
| `cross_layer` | source and target prerequisites verified | `teaser_only` or `hidden` |
| `forward_outlook_bridge` | not required for teaser | `teaser_only` |

Formal teaching content requires:

- explicit endpoints;
- relevant node records;
- learned-history status read or explicitly unavailable;
- validation status from bridge schema;
- no invented endpoint or history evidence.

## 8. actually_read_files And Unavailable-Files Requirements

Any learned-history decision must report:

```yaml
learned_history_read:
  status: "verified | unavailable | blocked"
  actually_read_files: []
  missing_files: []
  unavailable_reason: null
  evidence_priority_used: null
```

If a required file is unavailable:

- list the exact path or ref;
- state whether teaching can continue as teaser, hidden, blocked, or current-session-only;
- do not claim the unavailable file was read;
- do not ask the student to trust hidden memory.
