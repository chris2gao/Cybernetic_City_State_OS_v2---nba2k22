---
task_version: "1.0"
task_id: "math-mentor-lrp-01-teacher-initialization-context-loading-0001"
title: "Math Mentor LRP-01 Teacher Initialization And Context Loading"
mode: "goal"
task_level: 2

intent:
  goal: "Complete LRP-01 by formalizing how a new independent model initializes as a Math Mentor teacher and loads only the required teaching context."
  why_now: "The Math Mentor Teaching System Design implement plan splits the teaching-system work into six LRPs; LRP-01 is the prerequisite for all later lesson-plan, prompt-consistency, testing, learning-state, and capability work."
  definition_of_done:
    - "TEACHER_INITIALIZATION_FLOW.md exists and defines the end-to-end bootstrap-to-teacher flow."
    - "TEACHER_CONTEXT_LOADING_RULES.md exists and defines minimal task-scoped loading rules, context-boundary reload, drift recovery, and new-window reset for Math Mentor teaching."
    - "TEACHER_INITIALIZATION_DRY_RUNS.md exists and contains auditable dry-run fixtures for new-model initialization."
    - "The Coordinator preflight no longer requires repository files to already be physically present in the current context when they can be loaded by path."
    - "No full-repository ingestion or full Math Mentor directory ingestion is introduced."
    - "Validation and handoff reports are produced."

outputs:
  primary: "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
  additional:
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-context-loading-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-actually-read-files-0001.md"

inputs:
  required_refs:
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md"
    - "3号方案.md"
    - "06_Silicon_Index/AI_Bootstrap_Sequence.md"
    - "06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md"
    - "08_Domain_Applications/Math_Mentor/Math_Mentor_V9.1_从生成到教学的完整流程.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md"
    - ".ai/PROTOCOL.md"
    - ".ai/CODEX_WORK_MECHANISM_PROTOCOL.md"
    - ".ai/CODEX_TASK_INPUT_CONTRACT.md"
    - ".ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md"

scope:
  source_branch: "dev/protocol-human-cost-and-drift-control-0001"
  working_branch:
    name: "dev/math-mentor-lrp-01-teacher-initialization-context-loading-0001"
    create_from: "the exact source_head in the short signal that points to this task packet"
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-context-loading-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-actually-read-files-0001.md"
    - ".ai/OUTBOX.md"
    - ".ai/HUMAN_BRIEF.md"
    - ".ai/STATE.yml"
  forbidden_files:
    - "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/**"
    - "08_Domain_Applications/Math_Mentor/bridges/**"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_REGISTRY*.md"
    - "08_Domain_Applications/Math_Mentor/KNOWLEDGE_COMPLETION_PROGRAM.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - "未完成任务备忘录.yml"
  allowed_actions:
    - "create the working branch from the exact source head"
    - "read required refs"
    - "create the three LRP-01 design/control documents"
    - "make the narrow Coordinator preflight repair needed for lazy-loading compatibility"
    - "write consolidated reports"
    - "commit explicit paths on the working branch"
    - "push only the working branch"
    - "publish final handoff to ai/review/latest"

requirements:
  invariants:
    - "Plan 3 Human Speaker authority remains the top-level authority model."
    - "Math Mentor teaching is treated as an Engine B domain teaching task under Plan 3; deterministic tool use may support but not replace teaching judgment."
    - "The task does not activate runtime, Coordinator production, automation, or external apps."
    - "The task does not generate new math nodes, bridges, schemas, evaluator code, or production runtime code."
    - "The task does not start LRP-02, LRP-03, or later LRPs."
    - "Completion-preserving execution is mandatory: reading, design, narrow repair, validation, reporting, commit, branch push, and handoff are one task."
  validation:
    - "all required refs were read or any missing ref is explicitly reported with path, branch, and failure reason"
    - "the three new LRP-01 documents exist on the working branch"
    - "Coordinator preflight now lazy-loads repository-resident manuals by path before refusing"
    - "ordinary teacher initialization does not require full-repository ingestion"
    - "ordinary teacher initialization does not require full Math Mentor directory ingestion"
    - "dry-run fixtures cover empty-context teacher initialization, target-node request, missing current-context manual, missing learned-history state, context-boundary reload, and drift recovery"
    - "changed files are limited to allowed_files"
    - "forbidden_files are not modified"
    - "scoped secret scan passes"
    - "remote read-back verifies the pushed working branch and report refs"
  stop_rules:
    - "source head mismatch before working branch creation"
    - "required refs missing in a way that prevents safe design"
    - "need to modify forbidden files"
    - "need for new node generation, bridge generation, runtime activation, or Coordinator activation"
    - "security/privacy/secret risk"
    - "merge/master/source publication requirement not authorized by this task"
    - "validation failure after one safe repair pass"

authority:
  semantic_reviewer: "chatgpt"
  human_gate: "required_after_completion"
  master_push_authorized: false
  source_branch_push_authorized: false
  working_branch_push_authorized: true

return:
  packet_id: "codex-math-mentor-lrp-01-teacher-initialization-context-loading-0001"
  report_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-context-loading-0001.md"
  validation_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-validation-0001.md"
  changed_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-changed-files-0001.md"
  actually_read_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-01-teacher-initialization-actually-read-files-0001.md"
  brief_ref: ".ai/HUMAN_BRIEF.md"

completion_policy: "completion_preserving"
---

# Math Mentor LRP-01 Teacher Initialization And Context Loading

## 1. Task Position

This is the first long-running task in the Math Mentor Teaching System LRP suite.

It is based on:

- `08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md`
- `08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md`

The design plan splits Math Mentor teaching-system work into six LRPs. LRP-01 must be completed first because later work depends on a stable entry path for a new independent model becoming a Math Mentor teacher.

Do not split this task into file-level microtasks. This packet authorizes one coherent LRP-01 execution path: read, design, narrowly repair Coordinator preflight, validate, report, commit, push working branch, and handoff.

## 2. Core Problem

A new independent model cannot rely on old chat context, hidden memory, or full-repository ingestion.

It must know:

1. how to enter the Plan 3 City-State OS;
2. how to recognize Math Mentor teaching as an Engine B domain teaching task;
3. how to load the Math Mentor Coordinator payload;
4. how to load only the minimum relevant teaching context;
5. how to recover when context is missing, stale, or drifting;
6. when to stop for Human Speaker authority.

The known LRP-01 blocker is the Coordinator preflight rule that currently expects a repository-resident operational manual to already exist as physical text in the current context. That is incompatible with the master bootstrap lazy-loading law. This task should repair that narrow preflight behavior: if the manual is not in the current context, Codex should update the prompt to require loading the file by path; only if the path cannot be read should the teacher stop.

## 3. Required LRP-01 Documents

### 3.1 `TEACHER_INITIALIZATION_FLOW.md`

This document should define the end-to-end flow:

1. City-State bootstrap:
   - read current Human request;
   - read `AI_Bootstrap_Sequence.md`;
   - classify task under Plan 3;
   - confirm Human Speaker authority boundaries.
2. Domain entry:
   - recognize Math Mentor teaching;
   - load `08_Math_Mentor_Coordinator_Prompt.md`;
   - load Teaching Flow Spec and operational blueprint by path as needed.
3. Target-node routing:
   - identify requested concept/node;
   - load only target node, immediate prerequisites, matching bridges, and relevant learned-history state.
4. Teacher state construction:
   - produce compressed `SYSTEM_STATE_DUMP`;
   - do not dump full YAML;
   - record `actually_read_files`.
5. Teaching readiness decision:
   - ready to teach;
   - blocked for missing file;
   - blocked for Human Speaker decision;
   - blocked for runtime/Coordinator activation.

### 3.2 `TEACHER_CONTEXT_LOADING_RULES.md`

This document should define context loading rules for:

- ordinary same-window teaching;
- new-window teacher bootstrap;
- context-boundary reload;
- drift recovery reload;
- irreversible drift -> new window reset;
- Codex local context branch recovery;
- ChatGPT GitHub-only recovery.

It should define minimal loading sets, conditional loading sets, forbidden full-ingestion behaviors, and required evidence statements.

### 3.3 `TEACHER_INITIALIZATION_DRY_RUNS.md`

This document should contain dry-run fixtures for at least:

1. Empty context -> teacher initialization.
2. Request for a known node such as mapping / derivative / compactness.
3. Required operational manual absent from current context but present in repository.
4. Required operational manual missing from repository.
5. Learned-history state unavailable.
6. Context drift detected after partial teaching.
7. New-window reset after irreversible drift.

Each dry run should include:

- input condition;
- expected file loading order;
- expected `actually_read_files` behavior;
- expected compressed state dump fields;
- expected stop/continue decision;
- must-not-have list.

## 4. Narrow Coordinator Preflight Repair

Allowed file:

- `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`

Required semantic change:

- Replace any rule that says the teacher must refuse merely because `V9.1_认知映射引擎_终极实装蓝图.md` is not already in current context.
- New rule: if the file is not in current context, load it by repository path; if the repository path cannot be read, then stop and report the exact missing path.
- Preserve the invariant that the teacher must not invent or claim access to a file it has not read.
- Preserve no-runtime/no-Coordinator-activation boundaries.

Do not repair Socratic_Router, Prep_Architect, Exam_Agent, or lesson-plan schema in this LRP. Those belong to later LRPs unless a minimal reference is needed inside the LRP-01 documents.

## 5. Required Validation Detail

The validation report must include:

```yaml
validation_result:
  required_refs_read:
    status: pass | fail
    missing_refs: []
  new_documents_exist:
    teacher_initialization_flow: pass | fail
    teacher_context_loading_rules: pass | fail
    teacher_initialization_dry_runs: pass | fail
  coordinator_preflight_repair:
    status: pass | fail
    old_behavior_removed: true | false
    lazy_load_by_path_behavior_present: true | false
  loading_policy:
    no_full_repo_ingestion: pass | fail
    no_full_math_mentor_ingestion: pass | fail
    actually_read_files_required: pass | fail
  dry_runs:
    count:
    required_cases_present: pass | fail
  path_scope:
    allowed_only: pass | fail
    forbidden_changes: []
  secret_scan:
    status: pass | fail
```

## 6. Final Handoff Requirements

Return the handoff as a short pointer packet. Do not paste full reports into chat.

The final handoff must include:

```yaml
packet_id: codex-math-mentor-lrp-01-teacher-initialization-context-loading-0001
status:
report_ref:
validation_ref:
changed_files_ref:
actually_read_files_ref:
brief_ref:
dev_branch:
dev_branch_head:
source_branch:
source_head:
master_head:
human_gate: required
```

If any non-blocking issue remains, record it in the final report under:

```yaml
remaining_real_human_decisions_only: []
known_followup_candidates: []
```

Do not start LRP-02 or later LRPs.
