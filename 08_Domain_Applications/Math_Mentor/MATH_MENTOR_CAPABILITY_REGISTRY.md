# Math Mentor Capability Registry

## 1. Purpose And Authority

This document defines the capability registry for future Math Mentor teaching sessions. It is a documentation contract only.

It does not activate runtime, production Coordinator execution, external apps, MCP servers, deterministic calculation tools, visualization generators, node generation, bridge generation, evaluator changes, prompt mutation, student-state writes, learned-history writes, or spaced-review scheduler writes.

Authority chain:

1. Human Speaker under Plan 3 remains the top-level route, translation, and final-decision authority.
2. Math Mentor teaching remains a Plan3_Engine_B domain teaching task.
3. Deterministic tools may support teaching evidence only when an authorized Engine A implementation produces a concrete command/log/report reference.
4. Semantic teaching judgment remains separate from machine execution evidence.

## 2. Capability Category Table

| capability | purpose | default availability | primary requester | authorizer | consumer | claim evidence required |
| --- | --- | --- | --- | --- | --- | --- |
| `deterministic_calculation` | Future Z3, SymPy, Python, PyTorch, calculator, or equivalent deterministic checks. | `runtime_required` | Coordinator, Prep_Architect, Socratic_Router, Exam_Agent | Human-authorized Engine A runtime task | Coordinator, Prep_Architect, Socratic_Router, Exam_Agent | `run_with_log` plus command/log/report reference |
| `semantic_audit` | LLM-based consistency review, Mode B mapping review, or conceptual classroom reasoning. | `available` | Coordinator, Prep_Architect, Socratic_Router, Exam_Agent | Existing teaching scope unless Human escalates | All teaching agents | explicit `semantic_only` or `review_required` label |
| `visualization` | Future generated diagram, plot, app block, or rendered artifact for teaching. | `planned` | Coordinator, Socratic_Router | Human-authorized future visualization task | Socratic_Router, Human, student-facing lesson | artifact reference, generation log, privacy check |
| `human_brief` | Human-facing concise report or review handoff. | `available` | Codex, ChatGPT, Coordinator conceptually | Current handoff task or Human instruction | Human, ChatGPT, Codex | brief path and packet id |
| `future_app_skill` | Future app/plugin/skill/MCP capability such as browser, spreadsheet, notebook, drawing, or calculator integration. | `planned` | Human, ChatGPT, Codex, Coordinator conceptually | Human-authorized future implementation task | task-specific | explicit app/tool invocation log and output reference |

## 3. Availability State Taxonomy

Allowed availability states:

- `available`: The capability can be used in the current documentation or reasoning layer without runtime activation. Example: semantic audit or human brief writing.
- `unavailable`: The capability is not accessible in the current task or required dependency is missing.
- `planned`: The capability is a future design target only.
- `human_only`: The capability requires direct Human action or Human decision and cannot be autonomously performed by Math Mentor.
- `runtime_required`: The capability requires a future authorized runtime or Engine A implementation before it may produce execution evidence.

Availability state is not execution evidence. A capability marked `available` still cannot support a deterministic execution claim unless the specific run has `run_with_log`.

## 4. Per-Agent Request And Consume Permissions

| agent | may request | may consume | must not do |
| --- | --- | --- | --- |
| Human Speaker | Any capability within project rules. | Any evidence or summary. | Delegate final Human-only authority silently. |
| Coordinator | Capability lookup, semantic audit status, deterministic calculation request, visualization request. | capability status, tool log refs, semantic audit refs. | Claim runtime or tool execution without evidence. |
| Prep_Architect | deterministic calculation request, semantic audit, bridge capability status. | capability registry and `lesson_plan.tool_truthfulness`. | Add tool execution claims without logs. |
| Socratic_Router | semantic audit, visualization request, deterministic support request. | `lesson_plan.tool_truthfulness` and visual artifact refs. | Say a tool computed, verified, rendered, or checked unless `run_with_log` exists. |
| Exam_Agent | semantic evidence limits, deterministic log refs if present. | `Cognitive_State_Vector.tool_and_evidence_limitations`. | Treat semantic-only evidence as machine proof. |
| Learning-state / review scheduler future layer | human brief and state evidence references. | classroom and review evidence. | Write student state unless future authorization exists. |

## 5. Human Authorization Requirements

Human authorization is required before:

- connecting external apps, skills, plugins, MCP servers, or browser-backed runtime;
- running Z3, SymPy, Python, PyTorch, calculator, or deterministic validation as a Math Mentor teaching capability;
- generating or rendering a visualization artifact;
- writing real student state, learned history, scheduler rows, or private student data;
- activating production Coordinator or runtime integration;
- changing prompts, bridge schema, node YAML, evaluator behavior, or source/master publication.

## 6. Evidence Required Before Claim

Before Math Mentor says a capability ran, computed, checked, verified, rendered, plotted, or generated, it must have:

```yaml
capability_claim_evidence:
  capability: "deterministic_calculation | visualization | future_app_skill"
  claim_state: "run_with_log"
  log_ref: "<path or artifact ref>"
  command_ref: "<command record or null>"
  report_ref: "<result report or null>"
  input_ref: "<input evidence>"
  output_ref: "<output evidence>"
  environment_ref: "<environment/dependency evidence>"
  timestamp: "<UTC timestamp>"
  produced_by: "<authorized Engine A implementation or tool runner>"
  consumed_by: "<Math Mentor agent>"
```

For semantic audit, the required evidence is a review note, reasoning trace, or semantic-audit report labelled `semantic_only` or `review_required`. It is not machine proof.

## 7. Forbidden Capability Claims

Forbidden unless `run_with_log` and a concrete log/report exist:

- "Z3 verified this."
- "SymPy computed this."
- "Python checked this."
- "PyTorch executed the model."
- "The calculator confirms this."
- "The visualization was generated."
- "The app/plugin/MCP ran."
- "The result is machine-proven."

Safe replacements:

- "This is suitable for deterministic checking, but no tool log is present."
- "Current evidence is semantic-only."
- "A future Engine A tool run is required before claiming machine verification."
- "Visualization is planned; no artifact was generated in this task."

## 8. Future Runtime Implementation Gate

A future runtime task must satisfy all of these before this registry can be used operationally:

- Human authorization names the exact capability and allowed tool family.
- Input privacy and source refs are explicit.
- The runner records command, output, error, dependency, environment, timestamp, and result status.
- The result maps back into `lesson_plan.tool_truthfulness`.
- Failures map to `unavailable`, `review_required`, or `not_run`, not fake success.
- Production Coordinator activation remains separately authorized.

