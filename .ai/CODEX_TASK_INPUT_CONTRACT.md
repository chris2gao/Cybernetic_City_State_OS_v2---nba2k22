# Codex Task Input Contract v1.0

## 1. Purpose And Scope

This contract defines how ChatGPT or the Human supplies executable tasks to Codex. Its goal is maximum shared understanding with minimum avoidable context, ambiguity, and repeated policy text.

It governs:

- compact ChatGPT/Human-to-Codex task signals;
- long task packets under `.ai/TASKS/` or `.ai/USER_UPLOADS/`;
- required and conditional task fields;
- task-type-specific evidence, validation, scope, and stop rules;
- Codex behavior when critical input is absent or contradictory.

It does not authorize a task, stage, mutation, source push, merge, regeneration, automation, or protected action by itself.

## 2. Authority And Relationship To Existing Protocols

The canonical definition is `.ai/PROTOCOL.md#canonical-instruction-authority-and-state-freshness`. Apply the same instruction-authority order:

1. platform, system, developer, and safety instructions;
2. current explicit Human instruction;
3. authenticated current Human-approved task-specific permission or override;
4. Plan 3 constitution and the Cybernetic Citizen runtime contract;
5. durable repository control protocols;
6. relevant domain-authority protocols;
7. ordinary current signal and task operational details;
8. routing documents and historical evidence.

An ordinary model-generated signal or packet remains level 7 and cannot override durable protocol merely because it is current. Only an authenticated current Human-approved task-specific permission or override can do so within its explicit scope.

Resolve state freshness separately:

1. current explicit Human statement;
2. physical Git branch/HEAD and immutable source-head evidence;
3. validated active review mailbox and every required dereferenced ref;
4. published source baseline;
5. routing snapshots;
6. historical reports and legacy branches.

Freshness establishes state only; it does not grant mutation or publication authority. Report authority conflicts separately from freshness conflicts.

A task packet states only task-specific intent, evidence, scope, validation, and permitted overrides. It must not repeat permanent Git, secrets, polling, transcript, or retry rules unless it narrows them or carries an authenticated current Human-approved task-specific override.

## 3. Two-Part Task Input

A Codex task consists of:

1. a short machine signal that binds identity, pointers, source state, and Human gate;
2. a long task packet when the work requires instructions beyond the signal decision.

The signal is published only after every referenced task/packet file exists and has been verified at the intended review-branch head.

## 4. Minimal Machine Signal

The canonical signal contains all seven keys below. Unused refs are explicit `null` values.

```yaml
signal_id: "chatgpt-<task-id>"
decision: "start_task | approved | revise | blocked | acknowledge_protocol_update"
task_ref: ".ai/TASKS/<task>.md | null"
packet_ref: ".ai/USER_UPLOADS/<packet>.md | null"
brief_ref: ".ai/HUMAN_BRIEF.md | null"
source_head: "<full-source-commit-sha>"
human_gate: "not_required | required | approved"
```

Optional routing metadata such as `protocol_version`, `from`, `to`, or a one-line `note` may be carried only in a separately labeled routing envelope adjacent to the canonical signal. It must not be added to the seven-key pointer mapping or carry the long task body. Validation-result and authorization-context refs likewise remain outside the frozen pointer core.

Rules:

- at least one of `task_ref` or `packet_ref` is non-null for `decision: start_task`;
- `source_head` must match the intended source state before mutation;
- `human_gate` must reflect authenticated approval state, not a model assumption;
- every non-null ref is dereferenced before execution;
- missing refs use the one-check fast-fail rule in `.ai/PROTOCOL.md`.
- a material C1/C2 transition remains ineligible until the repository communication gate returns a passing result bound to the exact event and refs; C2 additionally requires separately injected trusted-host Human authority.

## 5. Canonical Long Task Packet

The canonical encoding is Markdown with YAML front matter. The front matter is machine-readable; the body carries only detail needed to execute the task.

```yaml
---
task_version: "1.0"
task_id: "chatgpt-<task-id>"
title: "<short task name>"
mode: "plan | goal"
task_level: 0

intent:
  goal: "<one observable outcome>"
  definition_of_done:
    - "<observable completion criterion>"

outputs:
  primary: "<repository-relative path or chat-plan marker>"

inputs:
  required_refs: []

return:
  packet_id: "codex-<task-id>"

completion_policy: "completion_preserving"
---
```

The body may add task-specific rationale, constraints, examples, or decision questions without duplicating the front matter.

### 5.1 Required Long-Packet Fields

- `task_version`: contract version used by the packet.
- `task_id`: stable task identity, unique within the active workflow.
- `title`: short human-readable name.
- `mode`: `plan` or `goal`.
- `task_level`: Git/workflow level `0` through `4` from `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`.
- `intent.goal`: one outcome, not a procedure transcript.
- `intent.definition_of_done`: observable criteria Codex can audit.
- `outputs.primary`: exact durable output path or `chat_plan` for non-mutating Plan mode.
- `inputs.required_refs`: exact evidence refs; may be empty only when the task needs no external evidence.
- `return.packet_id`: expected Codex handoff identity.
- `completion_policy`: optional; defaults to `completion_preserving` when omitted.

`task_level` is mandatory for future long packets. It prevents mutation, commit, and publication authority from being inferred from prose. Signal-only decisions that do not reference a long packet do not require it.

### 5.2 Completion Policy

`completion_policy` controls how Codex treats discovered sub-tasks during execution.

```yaml
completion_policy: "completion_preserving"
```

The default value is `completion_preserving`: sub-tasks, cleanup steps, validation steps, alignment steps, report steps, or repair steps discovered during execution are internalized into the current task when they are necessary to complete the authorized objective and remain within authorized scope.

Use a narrower policy only when the Human explicitly requests small-step gating. Completion-preserving execution still stops for new authority, objective changes, forbidden paths, destructive Git, source or master push, security, privacy, secrets risk, protected runtime or Coordinator activation, or whole-task blockers.

### 5.3 Human Cost And Drift Control Rule

Task packets should protect Human time, attention, and token budget as project resources. They should not split one authorized outcome into avoidable micro-tasks for readiness, review, closure, cleanup, validation, handoff, or mailbox neutralization.

When a task uses `completion_policy: "completion_preserving"`, the packet should define the whole coherent outcome. Cleanup, validation, report writing, mailbox updates, authorized branch commit and push, post-publication verification, and protocol alignment steps should be included as completion work when they are necessary, safe, and already within the authorized task level and scope.

Do not create a separate task packet for an internal checkpoint unless a real Human decision or protected action is required. Real gates include new authority, objective changes, destructive Git, source or master push without explicit approval, secrets or privacy risk, runtime or Coordinator activation, forbidden paths, new domain authority, and whole-task blockers.

If a sender detects protocol drift or avoidable task fragmentation, the next packet should collapse the workflow back to the original authorized objective. Prefer one consolidated continuation packet over many narrow follow-ups.

For drift recovery or drift-prone work, request these final report fields:

```yaml
drift_cause: "<why the task began fragmenting, or null>"
avoided_extra_gates: ["<gates/prompts that were folded back into the original task>"]
final_original_task_status: "<completed | completed_with_blockers | blocked | superseded>"
remaining_real_human_decisions_only: ["<actual decisions still requiring Human authority>"]
```

These fields document cost control and authority boundaries. They do not authorize bypassing protected gates.

### 5.4 Conditional Long-Packet Fields

Add only when applicable:

```yaml
intent:
  why_now: "<stage dependency or current problem>"

outputs:
  additional: []

inputs:
  local_files: []

scope:
  allowed_files: []
  forbidden_files: []
  allowed_actions: []

requirements:
  invariants: []
  validation: []
  acceptance: []
  stop_rules: []

authority:
  semantic_reviewer: "chatgpt | human | codex_with_review | not_applicable"

inheritance:
  domain_protocols: []
  overrides: []

return:
  detail_ref: ".ai/CODEX_REPORTS/<report>.md | null"
```

Do not add empty conditional sections merely to make a packet look complete.

## 6. When Conditional Fields Are Required

| Field | Required when |
|---|---|
| `why_now` | stage sequencing or current failure explains scope |
| `additional` | more than one durable output is required |
| `local_files` | evidence exists outside normal repository traversal |
| `allowed_files` | writes are narrow, adjacent files are sensitive, or review scope must be exact |
| `forbidden_files` | likely neighboring files must not change or a stage boundary is easy to cross |
| `allowed_actions` | the task authorizes an action normally gated or forbidden |
| `invariants` | behavior, identity, schema, or compatibility must remain stable |
| `validation` | code, evaluator, test, YAML, schema, or behavior changes |
| `acceptance` | completion needs criteria beyond `definition_of_done` |
| `stop_rules` | the task is conditional, bounded, retry-prone, or stage-gated |
| `semantic_reviewer` | mathematical, architectural, policy, or domain judgment is material |
| `domain_protocols` | domain-specific rules are needed beyond normal startup routing |
| `overrides` | a valid current instruction changes an inherited default |
| `detail_ref` | a separate Codex report or plan is required |

`source_head` and `human_gate` remain required in the short signal and normally are not repeated in the long packet. If repeated for a multi-repository or multi-state task, they must agree with the signal or Codex stops.

## 7. Task-Type-Specific Input

### 7.1 `.ai` Protocol Or Documentation

Required beyond the core:

- exact output path(s);
- policy questions or required sections;
- whether the task is Level 1 review-only or Level 2 source protocol change;
- structure/reference validation;
- explicit review handoff when Level 2.

Usually omit implementation commands and repeated global prohibitions.

### 7.2 Source Code, Evaluator, Or Test Work

Add:

- observed behavior or stable failure signature;
- desired behavior and non-goals;
- relevant modules/interfaces and compatibility constraints;
- allowed write surface when narrow;
- focused tests and expected outcomes;
- status, warning, skip, or error semantics when externally visible;
- residual-risk reporting and stop/escalation rules.

Specify observable behavior and invariants. Prescribe implementation only when an architecture decision is already approved.

### 7.3 Node YAML Repair

Add:

- exact node ID, filename, layer/domain, and current mode;
- diagnosed failure classes and evidence refs;
- fields authorized for repair and fields that must remain stable;
- required formal-definition, `sub_topics`, prerequisite, mapping, and audit properties;
- Mode A or Mode B mapping/audit rules;
- semantic-review authority;
- evaluator commands and expected honest status;
- batch size, retry limit, and escalation path;
- whether neighboring-node or domain regeneration is forbidden or separately gated.

Node identity and mathematical scope must not be inferred from filename alone.

### 7.4 Bridge, Schema, Or Mathematical Semantics

Add:

- whether output is design, candidate table, schema, or approved YAML landing;
- endpoint IDs/files/titles and evidence of availability;
- source/target levels, bridge type, and Mode A/B/mixed decision;
- approved conceptual connection or exact decision question;
- prerequisite and learned-history assumptions;
- schema version and validation/consumption constraints;
- authoritative mathematical/domain refs;
- final semantic reviewer;
- stop before generation/indexing unless design approval exists.

Codex may implement an approved semantic design. It must not independently resolve disputed high-impact mathematics or invent unapproved bridge associations.

### 7.5 Review-Only Task

Use `mode: plan` and `task_level: 0`, or Level 1 only when the review must be written to a durable review-branch artifact. Include:

- exact commit/range or artifact refs;
- review focus and severity priorities;
- expected finding format;
- whether absence of findings must still report residual risk;
- no mutation unless a separate goal task is authorized.

### 7.6 Debug Or Blocker Task

Add:

- stable failure signature;
- reproduction command and expected/actual result;
- environment facts already verified;
- prior concrete repair attempts and evidence;
- allowed diagnostic/write scope;
- success test;
- three-attempt classification and escalation target.

Do not count read-only diagnosis as a repair attempt. Do not repeat an unchanged failed remedy.

## 8. Plan Mode Input

Plan mode packets emphasize:

- the decision to be made;
- unresolved questions and tradeoffs;
- evidence refs;
- constraints and alternatives;
- required plan completeness;
- actions that remain forbidden until a later goal task.

Plan mode does not imply file edits, staging, commit, or push. Use `outputs.primary: chat_plan` unless a separate Level 1 goal task is authorized to persist the accepted plan.

## 9. Goal Mode Input

Goal mode packets emphasize:

- approved outcome and definition of done;
- authorized write/output scope;
- implementation invariants;
- required tests and validation;
- task level and publication boundary;
- stop/escalation rules;
- durable report/handoff requirements.

Within those boundaries, Codex chooses implementation details that match repository patterns and audits every completion criterion before reporting success.

## 10. Evidence References

Use exact, durable references:

```yaml
inputs:
  required_refs:
    - "source:.ai/PROTOCOL.md"
    - "ai/review/latest:.ai/CODEX_REPORTS/example.md"
    - "source:08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md#section-6"
```

Rules:

- prefer repository-relative paths with branch/commit identity;
- use headings or line ranges only as navigation hints, not fragile authority;
- list the minimum evidence set needed for correctness;
- dereference every non-null required ref;
- do not attach full diffs or logs when a commit range or report ref is sufficient.

### External Local Files

Use `inputs.local_files` only for Human-supplied evidence outside normal repository traversal, such as an attachment, private uncommitted artifact, binary document, selected external workspace, or specific local log.

Use absolute paths and state why each file is required. Never point to secrets, credentials, `.env`, SSH keys, tokens, or private keys.

## 11. Output Paths

`outputs.primary` must name one authoritative output:

- repository-relative path for a file artifact;
- `.ai/OUTBOX.md` when the short report is the only durable result;
- `.ai/CODEX_REPORTS/<name>.md` for a long Codex report;
- `chat_plan` for non-mutating Plan mode.

Use `outputs.additional` for required secondary files. Do not use broad directory paths when exact files are known. Source and review-only artifacts must be distinguished by `task_level` and task wording.

## 12. Validation And Acceptance

`definition_of_done` states what must be true. `requirements.validation` states how Codex proves it. `requirements.acceptance` adds externally reviewed criteria when needed.

Good validation is proportional to risk:

- documentation: existence, structure, refs, scope, and parse checks;
- code/evaluator: focused behavioral tests plus diff review;
- node YAML: schema/evaluator checks and semantic review where required;
- bridge/math: endpoint/schema checks and lane-specific semantic/computational review;
- Git publication: exact changed paths, commit SHA, expected-SHA lease, and remote read-back.

Do not define success as a command merely exiting zero when semantic behavior matters. Do not require broad test or log output unrelated to the changed surface.

## 13. Stop Rules And Human Gates

Use `requirements.stop_rules` when the task must halt on a specific condition, including:

- stale or contradictory source state;
- missing required evidence;
- overlapping unowned worktree changes;
- unresolved semantic authority;
- failure budget exhaustion;
- change outside allowed scope;
- unmet Human gate;
- completion of the explicitly bounded stage.

The short signal is authoritative for current `human_gate`. A long packet may explain the gate but cannot mark it approved without authenticated evidence.

Human approval remains required for source push, protected merge/rebase, destructive Git, secrets-sensitive actions, broad regeneration, major mathematical/architectural decisions, and other gates defined by current protocol.

## 14. Inheritance Without Repetition

For ordinary tasks, one short declaration is enough:

```yaml
inheritance:
  domain_protocols:
    - "08_Domain_Applications/Math_Mentor/Universal_Layer_Execution_Protocol.md"
  overrides: []
```

Do not repeat:

- no `git add .`;
- no destructive Git;
- no secrets access;
- source push requires Human approval;
- review writes use expected-SHA lease;
- pointer refs must be dereferenced;
- quiet successful-path output;
- the three-attempt failure budget.

Repeat a rule only to narrow it, identify a task-specific protected surface, or declare an authenticated override.

## 15. Compact Packet Examples

### 15.1 Small Review-Only `.ai` Report

```markdown
---
task_version: "1.0"
task_id: "chatgpt-example-discovery-0001"
title: "Discover example policy"
mode: "goal"
task_level: 1
intent:
  goal: "Write a review-only discovery report."
  definition_of_done:
    - "The report answers the five named questions."
outputs:
  primary: ".ai/CODEX_REPORTS/example-discovery.md"
inputs:
  required_refs:
    - "source:.ai/PROTOCOL.md"
return:
  packet_id: "codex-example-discovery-0001"
---
```

### 15.2 Plan-Only Review

```markdown
---
task_version: "1.0"
task_id: "chatgpt-example-plan-0001"
title: "Plan a schema migration"
mode: "plan"
task_level: 0
intent:
  goal: "Produce a decision-complete migration plan without modifying files."
  definition_of_done:
    - "The plan resolves ordering, rollback, validation, and open decisions."
outputs:
  primary: "chat_plan"
inputs:
  required_refs:
    - "source:path/to/schema.md"
return:
  packet_id: "codex-example-plan-0001"
---
```

## 16. Expanded Packet Examples

### 16.1 Evaluator Patch

```markdown
---
task_version: "1.0"
task_id: "chatgpt-evaluator-status-0001"
title: "Correct evaluator status semantics"
mode: "goal"
task_level: 3
intent:
  goal: "Separate machine-validated passes from review-required and skipped outcomes."
  definition_of_done:
    - "Semantic-only checks do not claim mathematical validation."
    - "Bulk summary reports passed, failed, review-required, skipped, and warnings."
outputs:
  primary: "06_Silicon_Index/factory_pipeline/sandbox_evaluator.py"
  additional:
    - "06_Silicon_Index/factory_pipeline/bulk_evaluator.py"
    - "06_Silicon_Index/factory_pipeline/test_evaluator_status.py"
inputs:
  required_refs:
    - "source:08_Domain_Applications/Math_Mentor/NODE_QUALITY_AUDIT_SAMPLE_PACK.md"
scope:
  allowed_files:
    - "06_Silicon_Index/factory_pipeline/sandbox_evaluator.py"
    - "06_Silicon_Index/factory_pipeline/bulk_evaluator.py"
    - "06_Silicon_Index/factory_pipeline/test_evaluator_status.py"
requirements:
  invariants:
    - "Support top-level and concept_node schemas."
  validation:
    - "Run the focused evaluator status test suite."
  stop_rules:
    - "Stop after local source commit and review handoff; do not push source."
return:
  packet_id: "codex-evaluator-status-0001"
---
```

### 16.2 Node YAML Repair

```markdown
---
task_version: "1.0"
task_id: "chatgpt-node-repair-0001"
title: "Repair one approved Mode B node"
mode: "goal"
task_level: 3
intent:
  goal: "Repair the approved mapping and audit fields without changing node identity or scope."
  definition_of_done:
    - "The primary mapping uses LLM architecture rather than an everyday metaphor."
    - "The node passes schema checks and receives required semantic review."
outputs:
  primary: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/<NODE>.yaml"
inputs:
  required_refs:
    - "source:08_Domain_Applications/Math_Mentor/NODE_REPAIR_PLAN.md"
    - "source:08_Domain_Applications/Math_Mentor/Universal_Layer_Execution_Protocol.md"
scope:
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/<NODE>.yaml"
  forbidden_files:
    - "<protected-adjacent-file>"
requirements:
  invariants:
    - "Preserve node ID, title scope, layer, and prerequisite identity."
  validation:
    - "Run the focused sandbox evaluator."
  stop_rules:
    - "Stop if mathematical scope is disputed or semantic review evidence is unavailable."
authority:
  semantic_reviewer: "chatgpt"
return:
  packet_id: "codex-node-repair-0001"
---
```

## 17. Missing Or Contradictory Critical Fields

Codex must return `blocked` rather than guess when a future contract-compliant packet lacks or contradicts a critical field that affects outcome, mutation authority, evidence, or gate state.

Critical failures include:

- missing `task_id`, `mode`, `task_level`, goal, definition of done, primary output, or return packet ID;
- `start_task` with both task refs null;
- source-head mismatch;
- missing required ref;
- plan mode combined with unauthorized mutation;
- task level inconsistent with requested commit/push behavior;
- conflicting allowed and forbidden paths;
- unmet Human or semantic-review gate;
- ambiguous target where alternatives have materially different effects.

Canonical response:

```yaml
packet_id: "codex-<task-id>-blocked"
status: "blocked"
report_ref: ".ai/OUTBOX.md"
brief_ref: ".ai/HUMAN_BRIEF.md"
source_head: "<observed-source-head>"
review_branch_head: "<observed-review-head>"
human_gate: "required | not_required"
```

The report identifies the exact missing or contradictory field and the required sender action. Missing protocol input does not consume the execution repair budget.

Legacy packets written before v1.0 may be executed only when their required semantics are unambiguous under current protocols. New packets should use this contract.
