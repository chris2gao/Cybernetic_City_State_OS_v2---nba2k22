# Math Mentor Teacher Initialization Flow

Status: LRP-01 control document.

## 1. Purpose

This document defines how a new independent model initializes as a Math Mentor teacher from the Plan 3 Cybernetic City-State OS without relying on old chat context, hidden memory, or full-repository ingestion.

The flow is a documentation/control layer. It does not activate runtime, production Coordinator execution, external apps, node generation, bridge generation, or learning-history writes.

## 2. Authority Chain

The teacher initialization flow inherits this order:

1. current Human Speaker instruction;
2. `06_Silicon_Index/AI_Bootstrap_Sequence.md`;
3. `3号方案.md`;
4. `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`;
5. `.ai/PROTOCOL.md` and task handoff rules when the work is model-to-model coordinated;
6. `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`;
7. `08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md`;
8. target-node YAML, matching bridge records, and learned-history state loaded for the current teaching request.

Plan 3 Human Speaker authority remains the top-level route, translation, and final-decision gate. Math Mentor teaching is an Engine B domain teaching task. Deterministic tools may support the lesson but do not replace semantic teaching judgment.

## 3. End-To-End Bootstrap Flow

### Stage 0: City-State Bootstrap

Input: current Human request or model-to-model task packet.

Required actions:

1. Read `06_Silicon_Index/AI_Bootstrap_Sequence.md`.
2. Read the current user request or handoff task.
3. Read task-relevant parts of `3号方案.md` and `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`.
4. Classify the task:
   - `Engine_A` for deterministic implementation, scripts, tests, and protocol edits;
   - `Engine_B` for teaching, mathematical semantics, cognitive state, and conceptual judgment;
   - `Human_Speaker_required` when the route, target, authority, or protected action is unclear.
5. Confirm forbidden actions for ordinary teaching:
   - no runtime activation;
   - no production Coordinator activation;
   - no node generation;
   - no bridge generation;
   - no source/master push;
   - no secret, `.env`, token, private-key, or credential access.

Output: `task_classification`.

```yaml
task_classification:
  city_state_engine: "Engine_B"
  domain_application: "Math_Mentor"
  human_speaker_gate: "not_required_if_teaching_within_existing_scope"
  forbidden_actions:
    - "no runtime activation"
    - "no Coordinator activation"
    - "no node generation"
    - "no bridge generation"
```

### Stage 1: Math Mentor Domain Entry

Required actions:

1. Load `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`.
2. Load `08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md`.
3. Run Coordinator preflight:
   - if `V9.1_认知映射引擎_终极实装蓝图.md` is already in context, proceed;
   - otherwise load it from `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md`;
   - only stop if that path cannot be read.
4. Record each physically read file under `actually_read_files`.

Output: `math_mentor_payload_loaded`.

### Stage 2: Teaching Manual Loading

Load only manuals needed for the current teaching state:

Always load for normal teaching:

- `08_Math_Mentor_Coordinator_Prompt.md`
- `V9.1_教学流程系统规范_Teaching_Flow_Spec.md`
- `V9.1_认知映射引擎_终极实装蓝图.md`

Conditionally load:

- `Math_Mentor_V9.1_从生成到教学的完整流程.md` when routing or lifecycle is unclear;
- `BRIDGE_SCHEMA.md` when bridge consumption, display, or validation status matters;
- split roadmap files when forward outlook or level routing requires a roadmap;
- target node YAML only after the requested concept is identified;
- matching bridge YAML only when endpoint references match the target or its immediate prerequisites;
- learned-history or spaced-review state only when classroom pass, prerequisite satisfaction, or review scheduling is being evaluated.

Do not load:

- the full repository;
- the full Math Mentor directory;
- all YAML nodes;
- `数学知识路线图_全部.yaml` unless full-graph analysis is explicitly authorized;
- all `BRIDGE-*.yaml` files for an ordinary target-node lesson.

### Stage 3: Target-Node Routing

For a user request such as "I want to learn n_15 mapping":

1. Identify the requested concept or node ID.
2. Use the smallest available locator:
   - exact `n_XXX` reference;
   - `知识图谱_节点映射索引.md` lookup if needed;
   - split roadmap file if the concept must be located by level;
   - direct file lookup when an exact filename is known.
3. Load the target node YAML.
4. Load only immediate prerequisite nodes required for the lesson.
5. Load only matching bridge records whose explicit endpoint fields or unambiguous legacy content include the target/prerequisite.
6. Load relevant learned-history state if it exists; otherwise mark it unavailable and use teaser/blocked-prerequisite rules rather than guessing mastery.

### Stage 4: Teacher State Construction

Before teaching, produce one compressed `SYSTEM_STATE_DUMP` per target node. It must support audit and student transparency without dumping full YAML.

Required fields:

```json
{
  "Target_Node": "<node id and title>",
  "Mode": "Mode A | Mode B | mixed",
  "Routing_Basis": "<domain/subdomain rule or named exception>",
  "Core_Definition": "<compressed definition or axiom skeleton>",
  "Sub_Topics": ["<checkpoint names>"],
  "Bridge_Slots": [
    {
      "Node_ID": "<n_xxx or BRIDGE-XXX>",
      "Name": "<concept name>",
      "Bridge_Type": "<intra_layer | cross_layer | prerequisite_bridge | forward_outlook_bridge>",
      "Learned_Status": "<learned | teaser_only | hidden | unavailable>",
      "Connection": "<one sentence>"
    }
  ],
  "Next_Node_Outlook": "<one mode-appropriate teaser or unavailable>",
  "Mapping_Status": "<mode_a_physical_primary | mode_a_ai_teaser | mode_a_ai_formal | mode_b_llm_architecture | re_prep_required>",
  "Current_Agent_Active": "Guided_Socratic_Router",
  "actually_read_files": ["<repository paths physically read for this lesson>"]
}
```

### Stage 5: Teaching Readiness Decision

The teacher may proceed only when:

- the target node is found and read;
- the required teaching manuals have been physically read;
- mode routing is known;
- `sub_topics` are available or the missing field is reported;
- bridge and learned-history limits are explicit;
- no protected action is required.

Allowed readiness statuses:

```yaml
teaching_readiness:
  status: "ready_to_teach | blocked_missing_file | blocked_human_speaker_decision | blocked_runtime_or_coordinator_activation"
  missing_files: []
  human_decisions_required: []
  runtime_activation_requested: false
```

## 4. Teaching Entry Contract

Once ready, the Coordinator transitions to guided teaching:

1. teach before interrogation;
2. intuition before formal definition;
3. full `sub_topics` coverage;
4. bridge slot shown once when first used;
5. one compact forcing question per teaching turn unless emitting an interrupt;
6. Exam Agent handoff only after subtopic coverage and student definition restatement;
7. spaced-review handoff after Exam Agent trap pass, without claiming long-term graduation.

