# Math Mentor Student Learning State Schema

## 1. Purpose And Authority

This document defines the durable student learning-state contract for Math Mentor. It records what evidence may support a learning-status claim over time.

This is a schema and rules document only. It does not write real student state, learned-history records, scheduler records, private data, runtime state, production Coordinator state, node YAML, bridge YAML, or evaluator output.

Authority baseline:

- Plan 3 Human Speaker remains the top-level route, translation, and final-decision authority.
- Math Mentor teaching remains a Plan3_Engine_B domain teaching task.
- LRP-01 lazy loading and `actually_read_files` evidence remain required for any state read.
- LRP-02 lesson-plan and Exam handoff contracts are the classroom evidence baseline.
- LRP-03 prompt behavior and LRP-04 test harness remain anti-regression baselines.
- `classroom_passed` is not `graduated`.

## 2. Privacy And Identity Placeholders

Learning-state records must use privacy-safe placeholders unless a future Human-approved data policy explicitly authorizes real identity storage.

```yaml
student_ref:
  student_key: "student_local_alias_or_hash"
  identity_policy: "privacy_safe_placeholder"
  real_name: null
  contact_info: null
  private_notes: null
session_ref:
  session_id: "session-YYYYMMDD-local-counter"
  source: "Math Mentor classroom session"
  human_authorized_state_write: false
```

Forbidden in this schema layer:

- real student name;
- email, phone, address, tokens, credentials, private keys, or `.env` content;
- medical, financial, or unrelated personal data;
- hidden memory claims;
- state writes without future explicit authorization.

## 3. Per-Node Learning Record Schema

```yaml
learning_record:
  schema_version: "1.0"
  student_ref: "<privacy-safe alias or hash>"
  node_ref:
    node_id: "n_xxx"
    file: "DOMAIN-XXX.yaml"
    title: "<node title>"
    source_level: "<1-6 or unknown>"
  learning_status: "not_seen"
  status_updated_at: "YYYY-MM-DDTHH:MM:SSZ"
  classroom_evidence:
    exam_agent_result: null
    exam_packet_ref: null
    cognitive_state_vector_ref: null
    trap_result_summary: null
    definition_restatement_summary: null
  review_evidence:
    scheduler_item_ref: null
    review_attempts: []
    latest_review_status: null
    stability_summary: null
  bridge_evidence:
    learned_history_status: "unavailable"
    usable_for_bridge_gating: false
    evidence_priority_used: null
  provenance:
    actually_read_files: []
    created_by: "Math Mentor schema layer"
    last_verified_by: null
    source_commit: null
  privacy:
    contains_real_private_data: false
    storage_policy: "placeholder_only_until_authorized"
  write_boundary:
    actual_state_write_performed: false
    write_authorization_ref: null
```

## 4. Allowed Learning Statuses

The canonical `learning_status` values are:

- `not_seen`: no teaching evidence is recorded.
- `introduced`: the node was introduced, but Exam_Agent did not pass it.
- `classroom_passed`: Exam_Agent trap passed for the current classroom session.
- `review_due`: the node has a pending review item.
- `review_passed`: one or more spaced-review attempts passed.
- `graduated`: long-term graduation criteria have been met.
- `stale`: prior evidence exists but stability or retention has decayed.
- `blocked`: teaching or review is blocked by missing prerequisite, missing evidence, or invalid state.

## 5. Status Transition Table

| from | to | required evidence | forbidden shortcut |
| --- | --- | --- | --- |
| `not_seen` | `introduced` | target node was taught or previewed; source evidence recorded | assuming exposure from node order |
| `introduced` | `classroom_passed` | Exam_Agent returns `classroom_passed` with `Cognitive_State_Vector` and trap evidence | praise, self-report, or definition shown without trap |
| `classroom_passed` | `review_due` | scheduler item is created by a future authorized scheduler task or a placeholder marks scheduling required | pretending scheduler write occurred |
| `review_due` | `review_passed` | review attempt passes the due-window criteria | classroom pass reused as review pass |
| `review_passed` | `graduated` | minimum review pass requirements and stability criteria in `GRADUATION_CRITERIA.md` are met | one review pass or node id ordering alone |
| `review_passed` | `stale` | review failure, overdue window, or trap/definition boundary degradation | silently retaining graduated status |
| `graduated` | `stale` | later review failure or stability violation | treating graduation as permanent without evidence |
| any | `blocked` | missing prerequisite, missing state, privacy violation, malformed record, or forbidden write request | guessing status from lower node id |
| `blocked` | prior valid status | blocker resolved with evidence provenance; the record preserves `blocked_from` and the resolution evidence | silent unblock without evidence |
| `review_passed` | `review_due` | a NEW review window is scheduled, identified by a `review_window_id` distinct from every window already counted, backed by an authorized scheduler item or an explicit placeholder | re-entering review to inflate the pass count with the same window |
| `stale` | `review_due` | remediation eligibility evidence plus a new review item with a fresh `review_window_id` | treating decay as automatically re-eligible without remediation |
| `review_due` | `stale` | the review attempt failed, or the window expired unused; the record states which, with evidence | silently dropping a failed attempt so it never appears in the history |

### 5.1 Review-cycle re-entry

`review_passed -> review_due` and `stale -> review_due` exist so that the second and
later review passes required by `GRADUATION_CRITERIA.md` are reachable at all. Without
them the graduation minimum could never be satisfied. They are constrained:

- every `review_due` entry carries a `review_window_id` unique within the node's history;
- a `review_window_id` or `source_ref` already counted must never be counted again;
- `stale -> review_due` additionally requires remediation evidence, because decay is not
  by itself a qualification to be re-tested.

### 5.1.1 Review-window kinds and ordering

Every `review_due` entry declares a `review_window_kind`:

| kind | meaning |
| --- | --- |
| `near_term_retention` | the first check after the classroom pass, testing that the material survived the short term |
| `stability_review` | a later check testing that it survived a longer gap |

Rules:

- the qualifying cycle must run `near_term_retention` **before** `stability_review`;
  a stability review offered first does not qualify;
- each `review_due` carries an `evidence_timestamp`, and timestamps across a node's
  qualifying passes must be strictly increasing in RFC 3339 form **with timezone**;
- two qualifying passes bearing the same timestamp are rejected, because they cannot
  evidence retention across a gap;
- provenance for entering `review_due` must be `scheduler_placeholder` (see section 6);
  no other source type may open a window while no scheduler exists.

### 5.1.2 Effect of `stale` on qualification

`stale` does **not** erase history, and it does **not** preserve qualification:

- every past attempt remains in the immutable event log for audit;
- the **currently qualifying** window set, the currently qualifying kinds, and
  graduation eligibility are all cleared;
- after remediation, a fresh `near_term_retention` **and** a fresh
  `stability_review` are both required before eligibility can return.

Historical evidence and currently-qualifying evidence are therefore tracked
separately. A node that decayed once cannot graduate on the strength of passes
earned before the decay.

### 5.1.3 Failed or unfinished classroom attempts

`exam_agent_result` values `failed` and `needs_reprep` describe an Exam outcome,
but persisting such an attempt as learning state is
**`unsupported_pending_contract`**. No transition consumes them today. A
no-state-change attempt event must be formally specified before any failed
attempt may be written; until then a failed classroom attempt simply leaves the
node in its prior status and lives only in the session record.

### 5.1.4 Event type to transition constraints

| event_type | may drive |
| --- | --- |
| `classroom_result` | `not_seen -> introduced`, `introduced -> classroom_passed`, and transitions into `blocked` |
| `review_result` | transitions among `review_due`, `review_passed`, `stale`, and into `blocked` |
| `human_acceptance` | **only** transitions that require Human authority, i.e. into `graduated`, and unblocking |

`human_acceptance` must not be usable to drive arbitrary non-Human transitions.
Its presence is a procedural record that a Human acted; it is not identity proof.

### 5.2 Graduation eligibility

`review_passed -> graduated` requires all of the following, not merely a pass count:

- at least `minimum_review_passes` (see `GRADUATION_CRITERIA.md`) passes earned in
  **distinct** review windows;
- definition-boundary retention evidence at the latest review;
- trap or transfer evidence at the latest review;
- evidence timestamps present on each counted pass;
- no unresolved blocker on the node;
- a Human authorization reference.

The Human authorization reference is a **procedural** protected gate. It records that a
Human acted; it is not cryptographic proof of identity, and a non-empty string is not
evidence of authority. A deterministic implementation may compute `graduation_eligible`,
but must not autonomously persist `graduated` until a trusted Human acceptance path
exists.

## 6. Evidence Provenance

Every learning-status claim must identify its evidence source:

```yaml
evidence_provenance:
  source_type: "exam_agent | spaced_review | registered_learned_state | explicit_human_override | strict_sequence_fallback | scheduler_placeholder"
  source_ref: "<path, packet id, or placeholder>"
  actually_read_files:
    - "<repository path actually read>"
  evidence_timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  evidence_limitations: "<known limits>"
  not_machine_validated_reason: "<if applicable>"
```

`scheduler_placeholder` marks an item that a future authorized scheduler would
have created. Recording it is not a scheduler write and does not activate one.

Evidence requirements for the non-review transitions:

| transition | required evidence |
| --- | --- |
| any `-> blocked` | the blocker, and the status being left, recorded as `blocked_from` |
| `blocked -> prior status` | `blocker_resolution_evidence`, and the target must equal the recorded `blocked_from` |
| `-> stale` | which of failure, expiry or decay occurred, with a reference |

`blocked -> blocked` is not a transition. A further blocker discovered while a
node is already blocked must not overwrite `blocked_from`, or the original status
would be lost and the node could never be restored correctly.

Evidence priority is defined in `LEARNED_HISTORY_RULES.md`.

## 7. Exam_Agent Classroom Evidence Fields

`classroom_passed` requires:

- Exam_Agent result is `classroom_passed`.
- `Cognitive_State_Vector.covered_subtopics` shows required coverage.
- `Cognitive_State_Vector.student_definition_restatement` is present.
- `Cognitive_State_Vector.recommended_trap_direction` or equivalent trap evidence is present.
- trap answer result shows the student passed the current classroom boundary.
- `tool_and_evidence_limitations` are recorded when tool evidence is absent.

`classroom_passed` does not mean long-term graduation.

## 8. Bridge Learned-Status Read Model

Bridge learned status is read from the current node's learning record and prerequisite records:

```yaml
bridge_learned_status:
  bridge_id: "BRIDGE-XXX"
  required_nodes:
    - "n_xxx"
  evidence_status: "verified | unavailable | unlearned | blocked"
  usable_for_formal_teaching: false
  degradation_rule: "hidden_or_teaser_when_unavailable"
```

Rules:

- `verified` requires persisted state, spaced-review state, registered learned state, or an explicitly bounded fallback.
- `classroom_passed` is the minimum classroom criterion, not long-term mastery.
- node id ordering cannot prove mastery except as a strict-sequential fallback declared by the current course design.
- unavailable state degrades to `unavailable`, `hidden`, `teaser_only`, or `blocked`; it never upgrades to mastery.

## 9. Forbidden Claims And Writes

Forbidden:

- claiming actual student-state write in this LRP-05 schema task;
- writing to `STUDENT_LEARNING_STATE/**`;
- writing to `LEARNED_HISTORY/**`;
- updating `数学间隔重复调度表.md`;
- claiming a scheduler update without an authorized scheduler task;
- claiming real private identity storage;
- treating `classroom_passed` as `graduated`;
- using lower node id as general mastery proof;
- activating runtime or production Coordinator.
