# Math Mentor Deterministic Calculation Handoff

## 1. Purpose And No-Execution Boundary

This document defines the future handoff contract for deterministic calculation tools.

LRP-06 does not execute Z3, SymPy, Python, PyTorch, calculators, sandbox evaluators, notebooks, external apps, MCP servers, or production Coordinator runtime. It only defines the evidence schema that a future Human-authorized Engine A implementation must satisfy before Math Mentor can claim a deterministic tool ran.

## 2. Supported Future Tool Families

Future deterministic calculation handoff may cover:

- `Z3`: finite symbolic satisfiability or SMT checks.
- `SymPy`: symbolic algebra, calculus, matrix, finite field, or number-theory checks.
- `Python`: deterministic scripted computation or small reproducible examples.
- `PyTorch`: tensor or neural architecture demonstrations when explicitly authorized.
- `calculator`: arithmetic or numeric support.
- `sandbox_evaluator`: repository evaluator execution when the task authorizes it.
- `other`: only with an explicit Human-approved tool family name.

Presence in this list is not authorization to run the tool.

## 3. Command / Log / Report Schema

```yaml
deterministic_calculation_handoff:
  schema_version: "1.0"
  request_id: "<stable request id>"
  requested_by: "Coordinator | Prep_Architect | Socratic_Router | Exam_Agent | Human | ChatGPT | Codex"
  authorized_by: "<Human approval or approved Engine A task ref>"
  tool_family: "Z3 | SymPy | Python | PyTorch | calculator | sandbox_evaluator | other"
  claim_state_before_run: "not_run | planned | review_required"
  input:
    source_refs: []
    expression_or_problem_ref: "<path/ref or inline safe expression>"
    privacy_status: "safe | redacted | blocked"
    assumptions: []
  command:
    command_line: "<exact command or structured invocation>"
    working_directory: "<path or null>"
    timeout_seconds: 0
    dependency_refs: []
  result:
    status: "passed | failed | error | timeout | skipped | blocked"
    stdout_ref: "<log path or null>"
    stderr_ref: "<log path or null>"
    output_ref: "<artifact path or null>"
    report_ref: "<summary report path or null>"
  environment:
    os: "<recorded>"
    runtime: "<recorded>"
    package_versions: []
    timestamp_utc: "<UTC timestamp>"
  integration:
    lesson_plan_ref: "<lesson_plan ref or null>"
    tool_truthfulness_update: {}
    limitations: []
```

## 4. Required Input, Output, Error, Environment Fields

Before a tool result can be consumed:

- `source_refs` must identify every mathematical or lesson input used.
- `command_line` or structured invocation must be exact enough to reproduce.
- `stdout_ref` and `stderr_ref` must preserve observable output when present.
- `status` must distinguish `passed`, `failed`, `error`, `timeout`, `skipped`, and `blocked`.
- `environment` must record runtime and dependency information.
- `timestamp_utc` must be present.
- `privacy_status` must block private student data unless a future policy authorizes it.

## 5. Integration With `lesson_plan.tool_truthfulness`

Future integration updates `lesson_plan.tool_truthfulness` like this:

```json
{
  "tool_status": "run_with_log",
  "available_evidence": "deterministic_log",
  "capability": "deterministic_calculation",
  "tool_family": "SymPy",
  "log_ref": "<required>",
  "report_ref": "<required or null>",
  "limits": "The tool checked only the scoped expression described in input.source_refs."
}
```

If a run does not occur, keep:

```json
{
  "tool_status": "not_run",
  "available_evidence": "semantic_only",
  "log_ref": null,
  "limits": "No deterministic execution is implied."
}
```

## 6. Failure Modes

| failure mode | required claim state | required handling |
| --- | --- | --- |
| timeout | `review_required` | Preserve timeout evidence; do not claim a mathematical result. |
| missing dependency | `unavailable` | State missing dependency and continue semantic teaching only if safe. |
| unsafe input | `review_required` | Stop execution handoff before running; request sanitized input. |
| contradictory result | `review_required` | Preserve semantic and tool evidence; escalate for review. |
| parse error | `review_required` | Record error; do not transform into a pass. |
| skipped run | `not_run` or `unavailable` | Do not imply execution. |

## 7. Unsafe Input And Privacy Boundaries

Deterministic handoff must not include:

- real student identity unless a future privacy policy authorizes it;
- secrets, tokens, `.env` values, SSH keys, or private keys;
- private student notes unrelated to the mathematical task;
- hidden memory not listed in `actually_read_files`;
- broad full-repository or full Math Mentor ingestion as a calculation input.

## 8. Future Engine A Implementation Checklist

- [ ] Human authorization names the exact tool family.
- [ ] Input refs are minimal and privacy-safe.
- [ ] Command, output, error, environment, dependency, and timestamp fields are recorded.
- [ ] Result maps into `lesson_plan.tool_truthfulness`.
- [ ] No semantic-only evidence is labelled as deterministic proof.
- [ ] Failure states remain visible.
- [ ] Production Coordinator activation remains separately gated.
