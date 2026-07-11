# Math Mentor Teaching System Test Plan

## 1. Purpose And Authority

This document defines the LRP-04 regression test harness for the Math Mentor teaching system. It turns accepted LRP-01 initialization/loading rules, LRP-02 lesson-plan and agent contracts, and LRP-03 prompt behavior into auditable documentation tests.

The harness is a documentation and validation layer. It does not activate runtime, production Coordinator execution, external apps, Z3, SymPy, PyTorch, calculators, node generation, bridge generation, learning-state writes, or spaced-review scheduler writes.

Authority baseline:

- Plan 3 Human Speaker remains the top-level route, translation, and final-decision authority.
- Math Mentor teaching remains a `Plan3_Engine_B` domain teaching task.
- Deterministic tools may support teaching only when real command logs or reports exist.
- Math Mentor lane names are `MathLane_A`, `MathLane_B`, and `mixed`; they are not Plan 3 `Plan3_Engine_A` or `Plan3_Engine_B` authority values.

## 2. Test Layers

| layer_id | layer | purpose | source contracts |
| --- | --- | --- | --- |
| L04-TL-01 | static_consistency_tests | Detect prompt or contract regressions without running production teaching. | LRP-01, LRP-02, LRP-03 prompts |
| L04-TL-02 | initialization_dry_runs | Reuse initialization fixtures for new-window bootstrap, target requests, missing manuals, learned-history absence, and drift recovery. | `TEACHER_INITIALIZATION_FLOW.md`, `TEACHER_CONTEXT_LOADING_RULES.md`, `TEACHER_INITIALIZATION_DRY_RUNS.md` |
| L04-TL-03 | golden_teaching_cases | Define expected teaching behavior for representative MathLane, bridge, error, exam, and tool-truthfulness scenarios. | `LESSON_PLAN_SCHEMA.md`, `TEACHING_AGENT_CONTRACTS.md`, `BRIDGE_SLOT_TEACHING_CONTRACT.md` |
| L04-TL-04 | e2e_session_simulation | Exercise one full simulated session from Human request to classroom result and scheduler warning. | Coordinator, Prep, Socratic, Exam prompts |

## 3. Static Consistency Test Matrix

| test_id | regression guarded | evidence to inspect | pass condition | must_not_have |
| --- | --- | --- | --- | --- |
| STATIC-01 | full repository ingestion | Coordinator prompt, initialization docs, test fixtures | Required loading uses exact paths and `actually_read_files`; no full repo scan is required for teaching. | `read the entire repository`, full directory dump requirement |
| STATIC-02 | full Math Mentor ingestion | Coordinator prompt, loading rules, fixtures | Target-node work loads only the payload, manual, target node, prerequisites, matching bridges, and needed learning state. | full `08_Domain_Applications/Math_Mentor/` ingestion |
| STATIC-03 | fake tool execution | Coordinator, Socratic, Exam, golden cases | Tool claims require a real command log or report; otherwise mark `not_run`, `semantic_only`, or `review_required`. | "Z3 has verified", "SymPy has computed", "PyTorch has checked", "calculator ran" without evidence |
| STATIC-04 | Engine/MathLane namespace confusion | Lesson plan schema and all four prompts | Plan 3 `Plan3_Engine_A/B` are authority routes; `MathLane_A/B` are teaching lanes. | `Plan3_Engine_A` used as a Math Mentor lane value |
| STATIC-05 | interrogation before explanation | Coordinator and Socratic prompt | A compact explanation precedes one compact forcing question. | pure interrogation before explanation |
| STATIC-06 | lesson_plan schema drift | `LESSON_PLAN_SCHEMA.md`, Prep prompt | `lesson_plan.json` keeps stable top-level fields including `subtopic_plan`, `bridge_slots`, `exam_handoff_conditions`, and `tool_truthfulness`. | missing required top-level lesson-plan field |
| STATIC-07 | missing Exam handoff vector | Socratic and Exam prompts | `Cognitive_State_Vector` contains covered subtopics, definition restatement, risk fields, bridge status, tool limitations, and pass/fail criteria. | vague handoff summary without vector fields |
| STATIC-08 | bridge invisibility | Bridge slot contract, Coordinator, Prep, Socratic | First bridge use displays id/name/connection and asks one compact comprehension check. | hidden bridge use or repeated metadata dump |
| STATIC-09 | classroom pass mistaken for graduation | Lesson schema, Exam prompt, E2E simulation | `classroom_passed` means current classroom trap passed; long-term graduation waits for spaced review. | "classroom_passed means graduated" |
| STATIC-10 | authority/loading/freshness conflation | Teacher Initialization Flow and lifecycle manual | Instruction authority defers to `.ai/PROTOCOL.md`; Bootstrap routes loading; Git/mailbox recency is state evidence only. | a competing local authority chain that mixes files with freshness evidence |
| STATIC-11 | silent execution or background sandbox | lifecycle manual and operational manuals | Deterministic work is a future Human-authorized `Plan3_Engine_A` handoff with `run_with_log`. | active silent `exec()` or background sandbox claim |
| STATIC-12 | unlogged tool or v8 overclaim | cognitive mapping blueprint and lifecycle manual | `v8_sanity_audit` is `semantic_only` unless a concrete `run_with_log` record exists. | unlogged proof, computation, verification, execution, or sandbox-pass claim |
| STATIC-13 | full-roadmap default | initialization docs and lifecycle manual | Routine teaching uses the relevant split roadmap only when needed. | routine requirement to load `数学知识路线图_全部.yaml` |
| STATIC-14 | literal LLM/pure-math isomorphism | cognitive mapping blueprint | LLM mapping is a bounded structural analogy; `pure_math_definition` remains authoritative; every mapping has a limitation/boundary. | literal or strong isomorphism claim |
| STATIC-15 | operational namespace regression | initialization flow, dry runs, lifecycle manual | State fixtures use `Plan3_Engine_*`, `MathLane_*`, and `Math_Lane`. | legacy `Mode` field or `Plan3_Engine_A/B` used as Math Mentor lane |
| STATIC-16 | classroom/graduation boundary regression | lifecycle manual, dry runs, test plan | Manuals explicitly preserve `classroom_passed != graduated`. | graduation from one classroom trap |
| STATIC-17 | documentation activates protected systems | all five target operational manuals | Manuals explicitly remain manual-chat/documentation only. | runtime/Coordinator activation, node/bridge generation, or learning-state/scheduler write |

## 4. Initialization Dry-Run Test Matrix

| dry_run_id | fixture | expected outcome | required evidence |
| --- | --- | --- | --- |
| INIT-01 | empty context -> teacher initialization | Load bootstrap, Math Mentor payload, operational manual, then declare teacher readiness without runtime activation. | non-empty `actually_read_files`; no full repo or full Math Mentor ingestion |
| INIT-02 | target node request -> SYSTEM_STATE_DUMP | Produce one compressed `[SYSTEM_STATE_DUMP]` per target node. | target node, MathLane, subtopics, bridge slots, next-node outlook, mapping status, `actually_read_files` |
| INIT-03 | manual absent from current context but present in repository | Lazy-load the repository path and continue. | manual path recorded in `actually_read_files`; no refusal solely because current context lacks the manual |
| INIT-04 | manual absent from repository | Stop with exact missing path. | no invented manual content; no runtime workaround |
| INIT-05 | learned-history unavailable | Warn and use unavailable/fallback status; do not claim mastery. | bridge gates degrade to teaser/hidden/unavailable |
| INIT-06 | context drift | Reload the smallest authority/context set needed. | refreshed `actually_read_files`; stale claims removed |
| INIT-07 | irreversible drift | Request new-window reset and re-bootstrap. | reset reason; no stale bridge, tool, or learning-state claims |
| INIT-08 | classroom pass -> review placeholder | Record classroom result without graduation or state writes. | `classroom_passed != graduated`; scheduler placeholder; all write-performed flags false |

## 5. Golden Teaching Case Matrix

| case_id | required coverage | risk covered |
| --- | --- | --- |
| GC-A-001 | MathLane_A basic concept | teach-before-interrogation, physical intuition with limitation, no fake SymPy/Z3 claim |
| GC-B-001 | MathLane_B abstract concept | LLM-architecture mapping, no household metaphor as primary teaching model, no forced Z3 |
| GC-BRIDGE-001 | bridge slot first-use teaching | node id/name/connection visibility, learned-history gating, comprehension check |
| GC-ERROR-001 | student error handling and re-prep trigger | repair once, then re-prep when the same misconception persists |
| GC-EXAM-001 | Exam handoff with `Cognitive_State_Vector` | high-resolution handoff and independent trap |
| GC-TOOL-001 | tool truthfulness / no fake execution | tool status is explicit and honest |

Detailed golden cases are defined in `TEACHING_GOLDEN_CASES.md`.

## 6. E2E Simulation Acceptance Rules

The E2E simulation is acceptable only if it contains all of the following steps:

1. Human request.
2. Coordinator compressed state dump.
3. Prep `lesson_plan.json`.
4. Guided Socratic teaching with explanation before question.
5. Student wrong once.
6. Repair.
7. Student definition restatement.
8. Exam handoff with `Cognitive_State_Vector`.
9. Exam trap.
10. Classroom result.
11. Spaced-review placeholder or missing scheduler warning.

Boundary requirements:

- The simulation must state that it is not runtime execution.
- The simulation must state that it is not production Coordinator activation.
- The simulation must state that it is not tool execution.
- The simulation must state that it is not a learning-state write.
- If the spaced-review scheduler is unavailable or unauthorized, it must emit a warning or placeholder rather than pretending to update the scheduler.

## 7. Failure Taxonomy

| failure_code | meaning | required response |
| --- | --- | --- |
| FAIL-LOAD-FULL | A test requires full repo or full Math Mentor ingestion. | Reject the test; replace with exact-path loading evidence. |
| FAIL-TOOL-FAKE | A response claims tool execution without a real log/report. | Mark failed; require `tool_status: not_run`, `semantic_only`, or real evidence. |
| FAIL-NAMESPACE | Plan 3 Engine names are used as Math Mentor lane values. | Mark failed; repair to `Plan3_Engine_*` vs `MathLane_*` separation. |
| FAIL-TEACH-ORDER | Questioning happens before explanation. | Mark failed; require compact explanation before one forcing question. |
| FAIL-BRIDGE-HIDDEN | Bridge is used without first-use visibility. | Mark failed; require id/name/connection and comprehension check. |
| FAIL-EXAM-EARLY | Exam handoff happens before subtopic coverage and definition restatement. | Mark failed; return to Socratic teaching. |
| FAIL-GRAD-CLAIM | Classroom pass is treated as long-term graduation. | Mark failed; require spaced-review boundary statement. |
| FAIL-SCHEDULER-FAKE | Simulation claims scheduler update without authorization. | Mark failed; emit scheduler warning/placeholder. |

## 8. Validation Commands And Checks

Codex may validate this layer without activating runtime:

- `Test-Path` for all LRP-04 documents.
- `rg` for required section names, case ids, fixture ids, and forbidden phrases.
- `git diff --name-only <source_head>..HEAD` to verify changed files are limited to the task allowlist.
- `git diff --check`.
- YAML parse for `.ai/STATE.yml` and `.ai/OUTBOX.md` if present.
- Scoped secret scan over changed files.

Operational-manual alignment validation also checks exactly these targets:

- `TEACHER_INITIALIZATION_FLOW.md`;
- `TEACHER_INITIALIZATION_DRY_RUNS.md`;
- `V9.1_认知映射引擎_终极实装蓝图.md`;
- `Math_Mentor_V9.1_从生成到教学的完整流程.md`;
- `TEACHING_SYSTEM_TEST_PLAN.md`.

Required static assertions:

1. Initialization state uses `Math_Lane`, and ordinary teaching uses `Plan3_Engine_B`.
2. All targets preserve lazy loading and `actually_read_files` evidence.
3. No target describes active silent `exec()` or background sandbox execution.
4. No target claims Z3/SymPy/Python/PyTorch execution without `run_with_log`.
5. `v8_sanity_audit` is `semantic_only` unless logged.
6. Routine teaching does not require `数学知识路线图_全部.yaml`.
7. LLM architecture mapping is explicitly a bounded analogy with `pure_math_definition` as authority.
8. `classroom_passed != graduated` is explicit.
9. Runtime, production Coordinator, node/bridge generation, learning-state writes, learned-history writes, and scheduler writes remain inactive.

These checks do not prove mathematical correctness of future teaching. They prove that the documentation harness covers the accepted LRP-01, LRP-02, and LRP-03 contracts and rejects known regression classes.
