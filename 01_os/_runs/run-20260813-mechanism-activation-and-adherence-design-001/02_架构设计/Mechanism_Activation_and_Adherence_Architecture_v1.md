# Mechanism Activation & Adherence Architecture v1

## 1. Problem statement

The repository can currently prove that a mechanism is defined, registered, boot-visible, and sometimes implemented, but that does not prove the model actually routes a matching action through that mechanism. The communication incident is the concrete counterexample: the canonical communication mechanism was loaded, yet formal cross-model dispatches were emitted as long Human-copy/paste chat content.

The architectural defect is therefore not `communication_system missing`. It is the missing binding between **intended action → mandatory mechanism → enforcement → observed evidence**.

A mechanism that can be silently bypassed is not operationally active.

## 2. Design goals

1. Make mandatory mechanism activation explicit and machine-resolvable.
2. Separate policy decision from policy enforcement.
3. Fail closed when a mandatory mechanism cannot be established.
4. Preserve Human authority: trigger resolution and gates do not create authority.
5. Produce durable compliance evidence rather than self-reported adherence.
6. Make bypass attempts first-class negative-conformance cases.
7. Keep mechanism definitions distinct from optional skills/tools.
8. Make collaboration routing visible to Human as a receiver setup card.
9. Make formal cross-model communication use durable documents/messages and compact Human relay pointers.
10. Never assume one validation method fits all result types.

## 3. Non-goals

- No autonomous model-to-model delivery, polling, acknowledgement, or task progression.
- No T5 orchestration.
- No authority expansion.
- No requirement that every existing mechanism be upgraded to L4 in this task.
- No conversion of mandatory mechanisms into optional skills.
- No generic redesign of the seven-stage workflow in this task.

## 4. Mature-pattern constraints

The architecture adopts three established separation patterns rather than inventing a monolith:

- **Policy decision vs enforcement:** a resolver decides which mechanisms are required; an enforcement point blocks or permits the planned action.
- **Admission before mutation:** material/formal actions are checked before they are accepted as valid actions.
- **Attestation/receipt after execution:** the system records what was expected, what ran, by whom/which surface, against which inputs, and what products/evidence resulted.

These are patterns, not dependencies. v1 does not require adding OPA, Kubernetes components, or in-toto libraries.

## 5. Core pipeline

```text
Human intent / planned model action
        ↓
Action Classification
        ↓
Mechanism Trigger Resolver (decision only)
        ↓
Required Mechanism Set
        ↓
Pre-Action Enforcement Gate
        ↓
Mechanism-specific execution path
        ↓
Compliance Receipt / observed evidence
        ↓
Post-action validation
```

### 5.1 Action Classification

Classify the **planned action**, not the provider or role label. Initial action classes should be narrow and observable, for example:

- `formal_cross_endpoint_task_dispatch`
- `formal_cross_endpoint_response`
- `formal_cross_endpoint_result`
- `formal_cross_endpoint_correction`
- `select_execution_receiver`
- `select_independent_reviewer`
- `protected_repository_publication`
- `ordinary_Human_foreground_discussion`

Classification must not infer authority. Unknown or ambiguous material action classes fail closed for formal execution but may remain ordinary Human discussion when no formal action is being claimed.

### 5.2 Mechanism Trigger Registry

Each active mechanism declares trigger bindings in one canonical registry entry:

```yaml
mechanism_id:
mandatory_for_action_classes: []
activation_predicates: []
required_inputs: []
enforcement_point:
missing_precondition_behavior:
receipt_requirement:
negative_conformance_refs: []
```

A mechanism without trigger bindings cannot be labeled `operationally_active`.

### 5.3 Resolver = Policy Decision Point

A pure resolver consumes structured action context and returns:

```yaml
action_class:
required_mechanisms: []
missing_preconditions: []
route_requirements: []
action_allowed_to_enter_enforcement: true|false
```

The resolver does not mutate the repository, publish messages, select authority, or execute a mechanism.

### 5.4 Pre-Action Gate = Policy Enforcement Point

The enforcement layer consumes the resolver result and verified mechanism preconditions. It blocks a formal action if any mandatory mechanism is unavailable, invalid, stale, or missing required context.

A model may still speak to Human conversationally, but it cannot label or treat a bypassed action as a valid formal dispatch/result/publication.

### 5.5 Mechanism execution wrapper / skill boundary

A skill/tool may package the HOW of executing a mechanism, but it never owns the MUST decision.

```text
Mechanism trigger → MUST
Execution wrapper/skill → HOW
Validator/receipt → DID
```

This preserves `03_mechanisms` as the system dependency layer and `04_skills_and_tools` as optional/external capability.

### 5.6 Compliance Receipt

For a formal action, durable evidence records at minimum:

```yaml
action_id:
action_class:
expected_action_context_ref:
required_mechanisms:
  <mechanism_id>:
    resolver_triggered: true
    preflight_ref:
    execution_ref:
    result_ref:
    validator_result:
physical_bindings:
  repository_ref:
  candidate_sha:
  transport:
bypasses: []
```

Receipt fields describing physical truth must be externally bound where possible; the receipt cannot self-authorize candidate SHA, diff, execution topology, or authority.

## 6. Mechanism effectiveness levels

The system must distinguish existence from operational effectiveness:

- **L0 DEFINED** — canonical definition exists.
- **L1 BOOT_VISIBLE** — declared startup/loader path makes the mechanism visible when relevant.
- **L2 TRIGGER_BOUND** — mandatory action triggers and missing-precondition behavior are canonical and machine-resolvable.
- **L3 EXECUTION_GATED** — a matching formal action cannot be accepted as valid without passing the mechanism's enforcement gate and producing required evidence.
- **L4 E2E_ADVERSARIALLY_VERIFIED** — positive end-to-end cases and bypass/negative cases independently verify the intended behavior.

Only L4 may be labeled `operationally_active` in the strong sense. Lower levels must use explicit weaker status.

This task builds the common framework, inventories active mechanisms, upgrades communication as the first L4 vertical slice, and upgrades collaboration/model-routing activation sufficiently to support formal dispatch. It does not force every mechanism to L4 now.

## 7. Communication vertical slice

### 7.1 Trigger correction

Current behavior is context-optional: if a communication context already exists, use the formal mechanism; otherwise ordinary output remains valid. This permits permanent bypass.

New rule:

```text
planned action is formal cross-endpoint communication
        ↓
communication_system is mandatory
        ↓
valid communication context exists?
     yes / no
      ↓    ↓
 execute   block formal dispatch and require context initialization
```

### 7.2 Formal dispatch shape

Long task/report bodies are durable documents. The message is a compact control envelope with direct exact refs. Human relays only the pointer plus receiver setup.

Human-visible relay should include:

```yaml
task_id:
message_id:
carrier:
exact_path_or_GitHub_ref:
sender_endpoint_id:
sender_task_role:
expected_recipient_endpoint_id:
expected_recipient_task_role:
one_line_routing_purpose:
receiver_setup:
```

### 7.3 Required negative conformance

The frozen negative case from the real incident is:

`formal_cross_endpoint_task_dispatch + missing communication context + long natural-language prompt for Human copy/paste`.

Expected formal result: **invalid formal handoff / communication initialization required**.

Ordinary Human discussion remains valid and must not accidentally trigger the formal communication mechanism.

## 8. Collaboration role initialization and model routing

Always-on bootstrap should declare stable collaboration roles without embedding volatile model catalog facts:

- `decision_architecture`
- `independent_review`
- `execution`
- `auxiliary_mechanical`

Stable policy:

- Decision/architecture: foreground strongest suitable GPT; strongest suitable Claude/Cowork may provide independent or cross-model architecture input.
- Independent review: isolated fresh GPT review environment by default when durable GitHub evidence is sufficient; no executor private context.
- Execution: Codex/Cowork; fresh GPT when all required inputs are durable and GitHub-readable.
- Auxiliary mechanical: Antigravity/Gemini for repetitive deterministic work, synchronization, and batch transformations.

These are collaboration roles, not authority roles.

Dynamic provider/surface/model/profile selection remains owned by `model_routing`.

## 9. Human receiver setup card

Every formal cross-model dispatch requiring model selection must expose a Human-readable and machine-readable setup card:

```yaml
receiver_setup:
  collaboration_role:
  provider:
  product:
  surface:
  model:
  reasoning_or_parameter_profile:
  session_mode:
  isolation_level:
  repository_access_mode:
  repository_or_worktree_requirement:
  required_branch_or_sha:
  local_files_required:
  github_publication_required_before_start:
  communication_carrier:
  limitations: []
```

The Human should configure the receiver from this card rather than infer settings from prose.

## 10. Review isolation

Independent review is evidence isolation, not merely a different chat tab.

For high-risk formal acceptance, the route should require an isolated review environment whose durable input is GitHub evidence and exact pointers. Executor private discussion and foreground expected verdict are excluded. If required facts are local-only, either route to an authorized local reviewer or first publish adequate durable evidence.

## 11. Mechanism effectiveness inventory

The implementation task must enumerate current active mechanism registry entries and produce an inventory containing:

```yaml
mechanism_id:
current_level:
definition_ref:
boot_ref:
trigger_ref:
gate_ref:
receipt_ref:
positive_test_ref:
negative_test_ref:
known_bypass:
recommended_successor_action:
```

The inventory is diagnostic evidence, not an excuse to expand this task into rewriting every mechanism.

## 12. Validation applicability: result type before test type

The workflow's Stage04 definition is conceptually broader than code tests: the subject comes from B and pass criteria come from evidence. However, the current operational vocabulary (`frozen_test_package`, `tests`, `run tests`, PASS) creates a real risk of code-test overfitting.

Therefore every material result must declare a **validation profile** before Stage04 artifacts are designed.

Candidate profiles for future workflow work include:

1. `executable_deterministic` — unit/integration/property/negative-conformance tests.
2. `declarative_contract` — schema/static validation + semantic scenarios + independent review.
3. `evidence_claim` — provenance/reproducibility/source audit + contradiction search.
4. `methodology_or_strategy` — criterion-based independent expert/model review, counterexamples, case application, comparative benchmark, field/pilot evidence where available.
5. `creative_or_audience_outcome` — rubric alone is insufficient; use audience/market proxy, benchmark set, blind comparison, A/B or longitudinal outcome evidence when the requirement actually depends on those outcomes.
6. `hybrid` — explicit composition of the above, with each success criterion mapped to one appropriate modality.

A validation modality is valid only if it can fail for a reason that is meaningfully connected to the requirement. A code test that merely parses a video-topic methodology document is not evidence that the methodology works.

This task itself is `hybrid`:

- architecture/governance semantics → independent semantic design review + adversarial scenarios;
- schemas/resolver/preflight/validators/communication enforcement → frozen executable and negative-conformance tests;
- mechanism effectiveness claims → observed end-to-end evidence + independent review.

The generic workflow validation-profile router is a separate future workflow task unless the design review finds it is required to implement this mechanism safely.

## 13. Proposed canonical implementation surface after design PASS

This design phase does not mutate canonical. The implementation candidate is expected to touch a bounded set similar to:

- `AGENTS.md` — short stable collaboration + formal-trigger bootstrap rules only.
- `01_os/03_mechanisms/mechanism_activation/**` — activation contracts.
- `01_os/02_boot/mechanism_activation/**` — boot manifest if required.
- `01_os/05_registry/mechanism_activation_v1.yml` and affected registry entries.
- `01_os/06_execution/boot/mechanism_activation/**` — resolver, preflight, receipt validator.
- `01_os/03_mechanisms/communication_system/**` and its execution layer — trigger-bound L4 slice.
- `01_os/03_mechanisms/model_routing/**` and relevant validator/schema — collaboration role inputs and receiver setup output.

Exact implementation boundary must be produced only after design review and fresh physical inspection.

## 14. Design acceptance questions

An independent design reviewer must attempt to falsify at least these claims:

1. Can a formal cross-endpoint dispatch still be considered valid without communication_system?
2. Can a mechanism be labeled operationally active without a trigger or enforcement gate?
3. Can the resolver accidentally grant authority?
4. Can a receipt self-assert physical truth instead of being externally bound?
5. Can optional skills become an unintended substitute for mandatory mechanisms?
6. Can ordinary Human discussion be incorrectly blocked by formal communication rules?
7. Can model routing omit the Human receiver setup needed to configure the actual surface?
8. Can a GitHub-only reviewer be assigned local-only evidence without an explicit publication/blocking step?
9. Does the framework create automatic delivery/progression by accident?
10. Does the validation model incorrectly force non-code outputs into code-style tests?
11. Can a methodology such as a video-topic selection method receive a false PASS merely because its document structure parses?
12. Can a mechanism pass L4 using only positive cases and no bypass attacks?

## 15. Decision status

This document is an architecture candidate, not canonical policy. It must receive a fresh isolated independent design review before canonical implementation is authorized.
