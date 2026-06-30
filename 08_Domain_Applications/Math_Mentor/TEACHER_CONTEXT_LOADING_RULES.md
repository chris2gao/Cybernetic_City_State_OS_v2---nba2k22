# Math Mentor Teacher Context Loading Rules

Status: LRP-01 control document.

## 1. Purpose

This document defines minimal context loading for Math Mentor teaching. It prevents full-repository ingestion, full Math Mentor ingestion, stale-context teaching, and unsupported claims about files or tools.

## 2. Universal Loading Rules

1. Load by task need, not curiosity.
2. Read a file before claiming its content.
3. Treat README, indexes, roadmaps, and filenames as locators, not proof.
4. Prefer exact paths, split roadmaps, target node files, and matching bridge records.
5. Record every physically read file in `actually_read_files`.
6. Never load the full repository for ordinary teaching.
7. Never load the full Math Mentor directory for ordinary teaching.
8. Never load all `Pure_Math_Intuition_DB` YAML files for one target-node lesson.
9. Never load `数学知识路线图_全部.yaml` unless full-graph analysis is explicitly authorized.
10. Never invent access to a missing file or tool run.

## 3. Minimal Loading Sets

### 3.1 New-Window Teacher Bootstrap

Required loading order:

1. current Human request or handoff task;
2. `06_Silicon_Index/AI_Bootstrap_Sequence.md`;
3. task-relevant `3号方案.md`;
4. task-relevant `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`;
5. `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`;
6. `08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md`;
7. `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md`.

Conditional:

- `Math_Mentor_V9.1_从生成到教学的完整流程.md` for lifecycle/routing disputes;
- `BRIDGE_SCHEMA.md` for bridge display/consumption questions;
- target node, prerequisite nodes, matching bridge files, learned-history state after the target is known.

### 3.2 Ordinary Same-Window Teaching

If the current context already contains verified current versions of the bootstrap, Coordinator, Teaching Flow Spec, and required operational manual, do not reload them by default. Continue by loading only:

- current target node;
- missing immediate prerequisites;
- matching bridges;
- relevant learned-history state.

If context freshness is uncertain, perform context-boundary reload.

### 3.3 Context-Boundary Reload

Trigger this when:

- new Codex/ChatGPT/Codex window;
- context compaction;
- task changes from design/review to teaching;
- user asks for a new target node after a long unrelated session;
- protocol or Coordinator prompt changed;
- `actually_read_files` is missing or stale.

Reload the new-window bootstrap minimal set, then continue to target-node routing.

### 3.4 Drift Recovery Reload

Trigger this when:

- the teacher references a file not in `actually_read_files`;
- Mode A/Mode B lane rules are confused;
- the teacher begins pure interrogation before explanation;
- bridge slots are used without endpoint/learned-history evidence;
- the teacher claims a tool ran without evidence;
- the current lesson no longer matches the target node.

Recovery steps:

1. Stop the current teaching turn.
2. State `drift_detected`.
3. Reload the smallest missing authority file or target evidence.
4. Emit a corrected compressed state dump.
5. Resume only if the correction does not require a Human Speaker decision.

### 3.5 Irreversible Drift New-Window Reset

Use a new-window reset when:

- multiple incompatible target nodes have been mixed;
- hidden-memory assumptions cannot be separated from read evidence;
- stale context cannot be corrected by reloading exact paths;
- a protected action was requested or implied.

Reset payload:

```yaml
reset_payload:
  reason: "<drift cause>"
  last_safe_target_node: "<node or null>"
  required_bootstrap_files:
    - "06_Silicon_Index/AI_Bootstrap_Sequence.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md"
  human_speaker_decision_required: false
```

## 4. Codex Local Context Branch Recovery

When Codex resumes an interrupted implementation task:

1. Check current branch, head, and worktree state.
2. Read the task packet and relevant `.ai` protocol state.
3. Read only required refs and affected target files.
4. Continue from repository evidence, not from memory.
5. Do not scan `Pure_Math_Intuition_DB` unless the task explicitly authorizes node work.

## 5. ChatGPT GitHub-Only Recovery

When ChatGPT has only GitHub access:

1. Read the latest pointer handoff.
2. Dereference `report_ref`, `validation_ref`, `changed_files_ref`, and `actually_read_files_ref`.
3. Review commit range and declared changed paths.
4. Do not infer local-only state.
5. If the report lacks required evidence, request a targeted Codex follow-up rather than asking for full logs.

## 6. Forbidden Full-Ingestion Behaviors

For ordinary Math Mentor teaching, the following are invalid:

- "Read the whole repository first."
- "Read the whole Math Mentor directory first."
- "Read every node YAML to teach one concept."
- "Read every bridge file before target matching."
- "Use `数学知识路线图_全部.yaml` for routine routing."
- "Ask the Human to upload a repository file that can be read by path."
- "Claim a manual, node, bridge, or learning-history state has been read when it has not."

## 7. Required Evidence Statements

Every initialized teacher should be able to state:

```yaml
context_evidence:
  actually_read_files: []
  routing_sources_used: []
  target_node_loaded: "yes | no"
  prerequisite_nodes_loaded: []
  bridge_files_loaded: []
  learned_history_state: "loaded | unavailable | not_needed"
  full_repo_ingestion: false
  full_math_mentor_ingestion: false
```

If evidence is unavailable, mark it unavailable and narrow the teaching behavior. Do not guess.
