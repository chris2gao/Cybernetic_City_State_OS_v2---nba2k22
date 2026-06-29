# Math Mentor Spaced Review Scheduler Schema

## 1. Purpose And No-Runtime Boundary

This document defines the spaced-review scheduler record contract for Math Mentor. It describes how review items should be represented by a future authorized scheduler.

This document does not activate a scheduler, write `数学间隔重复调度表.md`, write learned-history state, write student records, run runtime code, activate production Coordinator logic, or perform external tool execution.

If scheduler state is unavailable or unauthorized, the correct behavior is to emit a warning or placeholder.

## 2. Review Item Schema

```yaml
review_item:
  schema_version: "1.0"
  review_item_id: "review-student-node-YYYYMMDD-local-counter"
  student_ref: "privacy_safe_placeholder"
  node_ref:
    node_id: "n_xxx"
    file: "DOMAIN-XXX.yaml"
    title: "<node title>"
  source_learning_record_ref: "<learning record ref or unavailable>"
  source_status: "classroom_passed | review_passed | stale | blocked"
  schedule:
    created_at: "YYYY-MM-DDTHH:MM:SSZ"
    due_after: "P1D"
    due_at: "YYYY-MM-DDTHH:MM:SSZ"
    due_window_start: "YYYY-MM-DDTHH:MM:SSZ"
    due_window_end: "YYYY-MM-DDTHH:MM:SSZ"
    interval_label: "first_review | second_review | stability_review | remediation_review"
    interval_days: 1
  review_result:
    status: "pending"
    reviewed_at: null
    result_summary: null
    trap_or_definition_boundary_tested: null
  write_boundary:
    actual_scheduler_write_performed: false
    write_authorization_ref: null
```

## 3. Due Window And Interval Fields

Required schedule fields:

- `created_at`
- `due_after`
- `due_at`
- `due_window_start`
- `due_window_end`
- `interval_label`
- `interval_days`

Window rule:

- A review is `due` inside `[due_window_start, due_window_end]`.
- A review becomes `overdue` after `due_window_end`.
- Overdue review does not automatically erase prior evidence, but it can move the learning record to `stale` after policy-defined tolerance.

This schema intentionally does not choose final spacing intervals. A future implementation may define exact interval math after Human approval.

## 4. Review Result Taxonomy

Canonical review result values:

- `pending`: review item exists but has not been attempted.
- `passed`: review passed during its due window.
- `passed_late`: review passed after due window; may count with reduced stability weight.
- `failed`: review failed.
- `skipped`: review was skipped with an explicit reason.
- `blocked`: review cannot run because prerequisite or evidence is missing.
- `invalid`: record is malformed or violates privacy/write boundary.

## 5. Transition Rules

| source state | scheduler/review evidence | target state |
| --- | --- | --- |
| `classroom_passed` | authorized review item created | `review_due` |
| `classroom_passed` | scheduler unavailable | remain `classroom_passed` with scheduler warning |
| `review_due` | result `passed` | `review_passed` |
| `review_due` | result `passed_late` | `review_passed` or `stale`, depending on future policy |
| `review_due` | result `failed` | `stale` or `blocked` with remediation needed |
| `review_passed` | sufficient stable review chain | `graduated` |
| `review_passed` | later review failure | `stale` |
| any | malformed state or missing evidence | `blocked` |

`classroom_passed` cannot transition directly to `graduated`.

## 6. Scheduler Unavailable Warning Contract

When scheduler write is unavailable or unauthorized, emit:

```yaml
review_scheduler_status: "placeholder_not_written"
warning: "Spaced-review scheduler write is unavailable or unauthorized. Do not claim that 数学间隔重复调度表.md was updated."
next_authorized_action: "Future Human-approved scheduler task may create the review item."
actual_scheduler_write_performed: false
```

This warning is required for:

- E2E simulations;
- schema-only tasks;
- teaching sessions without scheduler authorization;
- missing scheduler file;
- unavailable persisted state;
- any situation where no actual write log exists.

## 7. Future Implementation Handoff Constraints

A future scheduler implementation must:

- obtain explicit Human authorization to write scheduler files;
- use privacy-safe student identifiers;
- preserve `classroom_passed != graduated`;
- record source Exam_Agent evidence;
- record `actually_read_files` for state reads;
- never infer mastery from node id ordering alone;
- distinguish real write logs from placeholders;
- fail closed on privacy or secret risk.

LRP-05 does not authorize that implementation.
