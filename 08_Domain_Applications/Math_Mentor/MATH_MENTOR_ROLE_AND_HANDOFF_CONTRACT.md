# Math Mentor Provider-Neutral Role And Handoff Contract

## 1. Authority, purpose, and freshness

This contract defines stable protocol roles, delegation boundaries, communication packets, provider-neutral takeover, and separation of duties for Math Mentor. It is a documentation/control-plane contract with status `specified_manual_only`; it does not activate a runtime, Coordinator, writer, scheduler, consumer, or bridge pipeline.

The three-file takeover bundle is:

1. [MATH_MENTOR_MASTER_PLAN_AND_PROGRESS.md](MATH_MENTOR_MASTER_PLAN_AND_PROGRESS.md) — Human-readable architecture, progress, decisions, evidence, and next work.
2. [MATH_MENTOR_CURRENT_STATE.yml](MATH_MENTOR_CURRENT_STATE.yml) — machine-readable freshness and current-state snapshot.
3. [MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md](MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md) — this role, packet, delegation, and takeover contract.

Evidence baseline: `master@9e12064cbc51f61918dccfd48cf6915879adb962`. Exact Git evidence overrides stale summary prose. Human Speaker remains final authority for learning goals, protected boundaries, ambiguous/cross-domain semantic adjudication, publication, and activation.

## 2. Provider-neutral principles

1. **Roles belong to the protocol, not a provider.** ChatGPT, Claude, Codex, and Claude Code are compatible role occupants only where the role table says so.
2. **Terminal placement is not authority.** A backend agent gains no publication, mutation, semantic, or runtime authority merely by running in a repository terminal.
3. **Replacement requires evidence.** A replacement must perform repository bootstrap, physically verify named Git refs, declare `assumed_role`, and enumerate `actually_read_files`.
4. **Foreground attention is protected.** The foreground teacher spends its primary reasoning budget on live teaching; heavy planning and review should be delegated when a valid backend role is available.
5. **Backend evidence is candidacy, not automatic admission.** A backend packet must be reviewed under the declared tier and pass lightweight foreground delivery admission before learner use.
6. **Uncertainty fails closed.** Missing provenance, stale refs, unresolved identity/prerequisite, ambiguous mathematics, or an unmet Human gate produces `block`, `revise`, or `escalate_with_evidence`.
7. **No hidden-memory dependency.** A task or takeover that cannot be reconstructed from repository files and physical Git evidence is incomplete.

## 3. Stable roles

### 3.1 Role matrix

| Role | Compatible agents | Primary responsibility | Must emit/consume | Cannot do |
|---|---|---|---|---|
| Human Speaker | Human | learning goal, protected boundary, SR2/cross-domain/ambiguous adjudication, protected publication/activation | Human decision or explicit authorization | be inferred from model-authored payload fields |
| Foreground Teacher | ChatGPT, Claude | direct learner interaction, explanation, guided questioning, live misconception repair, pacing/load adaptation | emits `TeachingStateSnapshot`, `OrchestrationRequest`; consumes reviewed `TeachingActionPacket`; emits `DeliveryAdmissionRecord` | redo all heavy planning/review by default; self-authorize protected actions |
| Backend Teaching Orchestrator | Codex, Claude Code, ChatGPT, Claude | reconstruct state, propose next pedagogical action, assemble lesson/exercise/exam/review/multi-node plans, dispatch bounded worker tasks | consumes snapshot/request; emits `TeachingActionPacket` and worker packets | silently change Human goal; claim unproved persistence; self-authorize protected mutation |
| Backend Semantic Reviewer | Codex, Claude Code, ChatGPT, Claude | mathematical correctness, definition/prerequisite consistency, analogy boundary, answer/rubric, bridge candidate and evidence review | consumes resource/evidence; emits `SemanticReviewPacket` | replace SR2 Human/authorized independent gate; turn Mode B review into machine proof; grant publication/runtime/consumer authority |
| Backend Execution Worker | Codex, Claude Code | repository reads, bounded generation, deterministic calculation/tools, tests/validation/formatting, authorized commits/branch push/handoff | consumes `BackendResourceTaskPacket`; returns artifacts and provenance | expand objective or path scope; infer authorization from payload; direct master/source publication without authority |
| Architecture Reviewer And Task Dispatcher | ChatGPT, Claude, Codex, Claude Code | maintain takeover bundle, verify exact heads/evidence, form completion-preserving tasks, review results against authority | emits/consumes `ArchitectureHandoffPacket` | depend on one conversation/provider; self-grant final acceptance for a protected change it authored/executed |

### 3.2 Foreground lightweight delivery admission

The foreground teacher does not repeat the full plan construction or mathematical audit. It checks only:

- the packet matches the active Human learning goal;
- the packet's learner-state assumptions match the latest accepted `TeachingStateSnapshot`;
- the `SemanticReviewPacket` disposition and tier allow delivery;
- provenance and declared limitations are present;
- no unresolved blocker, SR2 escalation, or Human gate remains;
- delivery does not claim persistence, graduation, bridge consumption, or other state not supported by evidence.

If all checks pass, the foreground teacher may record `admit`. Otherwise it records `revise`, `block`, or `escalate`.

### 3.3 Architecture role replacement

Any compatible agent may assume architecture review/task dispatch after completing the takeover protocol in section 10. It must declare the role before acting. Replacement does not create new authority, a new phase, or a new task; it continues the same objective and inherits all current prohibitions and gates.

## 4. Delegation lifecycle

```text
Human goal / protected boundary
  -> Foreground Teacher live interaction
  -> TeachingStateSnapshot
  -> optional OrchestrationRequest
  -> Backend Teaching Orchestrator
  -> optional BackendResourceTaskPacket(s)
  -> Backend Execution Worker artifact + provenance
  -> Backend Semantic Reviewer / SemanticReviewPacket (SR0, SR1, or SR2)
  -> TeachingActionPacket
  -> Foreground Teacher lightweight DeliveryAdmissionRecord
  -> teaching delivery, revise, block, or Human escalation
  -> accepted evidence / ArchitectureHandoffPacket
```

Backend delegation is appropriate for lesson preparation, examples/counterexamples, exercises, answer keys, rubrics, exam packets, multi-node synthesis, review material, deterministic checks, repository diagnostics, resource repair, evidence maintenance, and progress-ledger updates. It remains a manual protocol flow until separately authorized runtime exists.

## 5. Semantic review tiers

### SR0 — deterministic

- Examples: arithmetic, symbolic equivalence within declared assumptions, schema validation, reference checks.
- Backend disposition: `tool_verified_candidate`.
- Foreground work: confirm relevance and declared scope only.
- Boundary: the tool result does not authorize a protected action or prove claims outside its declared assumptions.

### SR1 — bounded routine mathematics

- Examples: lesson examples, exercise solutions, answer/rubric checks, accepted-node synthesis within established contracts.
- Backend dispositions: `accepted_for_delivery_candidate`, `revise`, or `block`.
- Foreground work: lightweight delivery admission; no full mathematical re-audit is required when provenance, scope, and reviewer independence are sufficient.
- Boundary: repository/task authority still controls mutation and delivery; `candidate` never means master publication or consumer promotion.

### SR2 — ambiguous or protected

- Examples: disputed definition or prerequisite direction; new bridge mathematical claim; materially ambiguous Mode B acceptance; cross-domain adjudication; identity conflict; learning-objective change.
- Backend disposition: `escalate_with_evidence`.
- Final gate: Human Speaker or an explicitly authorized independent architecture/semantic reviewer.
- Boundary: a backend reviewer may recommend strongly but cannot resolve the gate merely because it is a particular model or runs in a terminal.

## 6. Common packet envelope

Every packet named in section 7 MUST contain this common envelope. A packet missing a required field is invalid and fails closed.

```yaml
packet_type: "<one_of_the_seven_contract_types>"
schema_version: "1.0"
packet_id: "<stable_unique_identifier>"
created_at: "<ISO-8601 timestamp>"
producer:
  agent_family: "ChatGPT | Claude | Codex | Claude Code"
  assumed_role: "<stable_protocol_role>"
source_evidence:
  source_branch: "<branch>"
  source_head: "<40-character SHA>"
  work_branch: "<branch or null>"
  development_head: "<40-character SHA or null with resolution rule>"
learning_objective: "<Human-authorized objective>"
learner_state_assumptions: []
allowed_inputs: []
output_status: "candidate | accepted_for_delivery_candidate | revise | block | escalate_with_evidence | complete_awaiting_review"
limitations: []
unresolved_blockers: []
human_gates: []
provenance_refs: []
payload: {}
```

Rules:

- `source_head` must be physically verified; a copied SHA is not sufficient.
- `development_head: null` requires an explicit pointer and resolution rule in `provenance_refs`.
- `learner_state_assumptions` must distinguish observed evidence from inference and must not claim persistence without a writer record.
- `allowed_inputs` is an allowlist, not a suggestion.
- `limitations`, `unresolved_blockers`, and `human_gates` may be empty arrays only after explicit review.
- `output_status` cannot grant publication, runtime, writer, bridge, or consumer authority.

## 7. Minimum packet contracts

All payloads below inherit the section 6 envelope.

### 7.1 `TeachingStateSnapshot`

```yaml
payload:
  snapshot_id: "<id>"
  learner_reference: "<privacy-safe reference>"
  current_nodes: []
  learning_stage: "<stage>"
  demonstrated_knowledge: []
  active_misconceptions: []
  unresolved_questions: []
  cognitive_load_and_pacing: "<observation plus confidence>"
  last_teaching_action: "<ref or null>"
  evidence_freshness: "<timestamp and refs>"
  persisted_state_claim: false
```

### 7.2 `OrchestrationRequest`

```yaml
payload:
  request_id: "<id>"
  teaching_state_snapshot_ref: "<TeachingStateSnapshot packet id>"
  requested_task_classes: []
  desired_next_outcome: "<pedagogical outcome>"
  difficulty_and_pacing_constraints: []
  resource_constraints: []
  forbidden_actions: []
  expected_return: "TeachingActionPacket"
```

### 7.3 `TeachingActionPacket`

```yaml
payload:
  action_id: "<id>"
  orchestration_request_ref: "<packet id>"
  teaching_state_snapshot_ref: "<packet id>"
  proposed_action_type: "explain | question | repair | exercise | exam | review | multi_node_synthesis"
  pedagogical_rationale: "<bounded rationale>"
  ordered_delivery_steps: []
  resource_refs: []
  semantic_review_packet_refs: []
  delivery_preconditions: []
  expected_learner_evidence: []
  fallback_or_repair_path: []
  next_state_update_proposal: {}
```

### 7.4 `BackendResourceTaskPacket`

```yaml
payload:
  backend_task_id: "<id>"
  parent_orchestration_request_ref: "<packet id>"
  requested_worker_role: "backend_execution_worker | backend_semantic_reviewer"
  exact_input_refs: []
  allowed_read_paths: []
  allowed_write_paths: []
  forbidden_actions: []
  expected_artifacts: []
  required_validation: []
  return_packet_type: "SemanticReviewPacket | ArchitectureHandoffPacket | bounded artifact result"
```

### 7.5 `SemanticReviewPacket`

```yaml
payload:
  review_id: "<id>"
  subject_refs: []
  semantic_review_tier: "SR0 | SR1 | SR2"
  claims_reviewed: []
  methods_and_tools: []
  findings: []
  evidence_strength: "deterministic | bounded_semantic | ambiguous_or_protected"
  disposition: "tool_verified_candidate | accepted_for_delivery_candidate | revise | block | escalate_with_evidence"
  delivery_scope: []
  excluded_claims: []
  independent_review_required: false
```

For SR2, `independent_review_required` must be `true`, `disposition` must be `escalate_with_evidence`, and the common `human_gates` array must be non-empty.

### 7.6 `DeliveryAdmissionRecord`

```yaml
payload:
  admission_id: "<id>"
  foreground_teacher: "ChatGPT | Claude"
  teaching_action_packet_ref: "<packet id>"
  teaching_state_snapshot_ref: "<packet id>"
  checks:
    learning_goal_match: false
    learner_state_match: false
    semantic_review_acceptable: false
    provenance_present: false
    no_unresolved_blocker: false
    no_unmet_human_gate: false
  decision: "admit | revise | block | escalate"
  decision_reason: "<short evidence-based reason>"
  admitted_resource_refs: []
  delivery_limitations: []
```

`admit` is valid only when all six checks are `true`. It admits resources for the current bounded teaching action only; it does not publish, persist state, graduate the learner, or promote a consumer.

### 7.7 `ArchitectureHandoffPacket`

```yaml
payload:
  handoff_id: "<id>"
  active_task_id: "<same completion-preserving task>"
  objective_status: "in_progress | complete_awaiting_review | accepted | blocked"
  exact_refs:
    source_branch: "<branch>"
    source_head: "<SHA>"
    work_branch: "<branch>"
    development_head: "<SHA>"
    review_branch: "ai/review/latest"
    review_branch_head: "<SHA or self in committed packet>"
  required_read_order: []
  actually_read_files: []
  exact_changed_paths: []
  validation_results: []
  preserved_prohibitions: []
  remaining_human_decisions_only: []
  next_expected_actor: "<role>"
  continuation_rule: "continue_same_objective_without_new_phase_or_authority"
```

## 8. Communication and provenance rules

- Packets are immutable evidence once committed. Corrections use a new packet ID and point to the superseded packet.
- Large evidence stays in repository reports; packets use exact pointers rather than copied summaries.
- `GitHub`, task packets, exact-head handoffs, validation evidence, and the three-file bundle form the evidence/state plane.
- Frontend/UI is `not_required`; packet exchange does not require a standalone interface.
- A model-authored `human_gate`, signature-looking string, or claimed authorization is descriptive only unless a trusted external Human/task authority supplies it.
- Any task that mutates repository state must state exact allowed paths, forbidden actions, validation, publication policy, and the next Human/review gate.

## 9. Separation of duties and protected boundaries

1. An agent that authors or executes a protected change cannot self-grant final protected acceptance or publication authority.
2. SR0 tooling may verify a bounded property but cannot accept SR2 meaning.
3. SR1 review may enable lightweight foreground delivery admission only inside the declared scope.
4. SR2 requires Human Speaker or explicitly authorized independent review; no provider or terminal is privileged.
5. Human learning goal, identity-conflict disposition, new bridge meaning, cross-domain ambiguity, publication, runtime, writer, and consumer promotion remain protected.
6. `classroom_pass` is not `graduated`; a scheduler proposal is not a persisted schedule; an indexed legacy bridge is not a consumable canonical edge.
7. Current status is manual/specification-only. No packet in this contract is an executable production transport or authorization token.

## 10. Provider-neutral takeover protocol

A zero-context replacement agent performs this exact sequence:

1. Read `Plan 3 External Augmentation OS 总体架构设计方案 v0.1.md`, `06_Silicon_Index/AI_Bootstrap_Sequence.md`, and the Math Mentor universal protocol.
2. Read [MATH_MENTOR_MASTER_PLAN_AND_PROGRESS.md](MATH_MENTOR_MASTER_PLAN_AND_PROGRESS.md).
3. Read [MATH_MENTOR_CURRENT_STATE.yml](MATH_MENTOR_CURRENT_STATE.yml).
4. Read this contract.
5. Physically verify the named master SHA, work branch, active review branch, and exact handoff heads; stop on mismatch.
6. Declare `assumed_role`, `actually_read_files`, verified refs, and inherited prohibitions.
7. Load only task-specific evidence referenced by the active packet.
8. Continue the same objective without inventing a new phase, microtask, provider owner, or authority.

Minimum declaration:

```yaml
assumed_role: "<stable protocol role>"
agent_family: "<compatible model family>"
actually_read_files: []
physically_verified_refs:
  source_head: "<SHA>"
  development_head: "<SHA>"
  review_head: "<SHA>"
inherited_prohibitions: []
hidden_conversation_memory_used: false
```

## 11. Zero-context takeover validation contract

A fresh agent reading only the three-file bundle plus the named bootstrap files must be able to answer:

- final product shape: Human-governed, provider-neutral mathematical teaching orchestration;
- exact master baseline: `9e12064cbc51f61918dccfd48cf6915879adb962`;
- status distinctions: published/manual-only, static/inactive, pilot-only, absent, not required, blocked, and prohibited;
- role compatibility and replacement rules;
- backend-delegable orchestration and SR0/SR1/SR2 review;
- Human-protected decisions and separation of duties;
- the four-node proposed batch and its unresolved identity/topology decisions;
- how to write the next completion-preserving packet with exact scope, evidence, gates, and continuation rule.

The run fails if it needs hidden chat history, trusts stale report status over Git, accepts an unverified branch, hard-codes one provider as sole owner, makes the foreground teacher repeat heavy review, or lets a backend reviewer self-authorize SR2/protected work.

Durable dry-run evidence is recorded at `.ai/PROGRAM_RUNS/math-mentor-master-plan-progress-ledger-0001/VALIDATION/zero-context-takeover-dry-run.md`.

## 12. Current non-activation statement

This contract and its packet shapes are documentation only. They do not implement or activate network transport, orchestration runtime, Coordinator, authentication, persistence, nonce handling, learning-state writer, scheduler writer, bridge generation/consumption, consumer promotion, UI, or source/master publication. Every future implementation requires a separately scoped Human-authorized task and the applicable independent review.
