# Task Type and Execution Model v0.2

```yaml
document_id: plan3-task-type-and-execution-model-v0.2
version: "0.2.0"
status: active_document_control_plane
architecture_ref: "06_Silicon_Index/Plan3_External_Augmentation_OS_Architecture.md"
operational_activation: false
task_daemon: false
```

## 1. Purpose

This contract selects a completion and evidence model for each Plan 3 task. It consolidates task taxonomy and state transitions; detailed input, Git, handoff and long-run procedures remain in their canonical `.ai` contracts.

Authority and freshness follow the [v0.2 authority registry](./Plan3_External_Augmentation_OS_Architecture.md#3-canonical-authority-registry). This file does not create a task, authenticate approval, publish a branch or activate an executor.

## 2. Universal execution invariants

1. One Human-authorized outcome remains one completion-preserving task.
2. Planning, implementation, cleanup, validation, correction, report, handoff, publication and post-publication verification are phases of that task when already inside scope; they are not automatic new Human gates.
3. A task may expand internally to satisfy its original completion contract, but may not expand authority, objective, protected data access or blast radius.
4. Physical Git state and dereferenced evidence outrank cached task summaries for freshness.
5. Read-only evidence collection does not imply write authorization.
6. A passing check proves only its named scope and source; it does not activate L9.
7. New authority, materially changed objective, destructive/irreversible action, secret-sensitive scope, Engine B-to-A translation, protected publication or L9 activation triggers the applicable Human gate.
8. User/unrelated worktree changes are preserved and excluded from task commits.

## 3. Execution modes

| Mode | Use | Output | Mutation boundary |
|---|---|---|---|
| `answer_review_report` | explain, inspect, diagnose or audit | evidence-backed response/report | no source mutation unless explicitly added |
| `plan` | decide implementation contract before execution | decision-complete plan | no implementation mutation |
| `goal` | implement or complete a concrete outcome | source, tests, evidence, publication/handoff as authorized | exact task scope |
| `long_run_program` | program-scale objective with internal milestones | checkpoints, resumable runs, final integrated result | exact program envelope and protected gates |
| `engine_b_court` | contested knowledge/research adjudication | arguments, sources, verdict request | no automatic Engine A mutation |
| `recovery` | restore task identity/state after drift/failure | reconciled checkpoint and safe continuation | no authority expansion |

An interface label or model mode is not authority. The task’s Human instruction and governing contracts decide the boundary.

## 4. Canonical task-type registry

Every row names its entry, state path, required evidence, stop conditions and Human-gate conditions. “Stop” means do not cross that boundary; continue other safe in-scope work when possible.

| Task type | Entry conditions | State path | Required completion evidence | Stop conditions | Human gate |
|---|---|---|---|---|---|
| `read_only_review` | explicit question/audit scope; source refs available | `received -> scoped -> evidence_collected -> analyzed -> reported -> complete` | files actually read, source/head, findings/limits, no-mutation check | required evidence inaccessible; request becomes mutation | not required for ordinary read; required for protected/private body or new external action |
| `planning_task` | objective and decision boundary known | `received -> assumptions_resolved -> evidence_collected -> plan_drafted -> decision_complete` | implementation-ready plan, authority/paths/tests/gates/acceptance | materially different product decision cannot be inferred | Human chooses only unresolved product/authority decisions |
| `short_goal_task` | bounded outcome can finish in current task | `received -> preflight -> executing -> validating -> reporting -> complete` | requested outcome plus proportional verification | new permission/objective, unsafe mutation or protected gate | only when stop boundary is reached |
| `completion_preserving_large_task` | substantial but one coherent authorized outcome | `received -> preflight -> plan -> executing <-> validating/correcting -> publication -> postverify -> complete` | requirement ledger, checkpoints, exact diff, tests, publication/readback if authorized | true authority/objective change; unrecoverable repeated blocker; protected gate | not for routine subphases; required for the exact boundary crossed |
| `long_run_program` | program-scale authorization and durable run protocol apply | `received -> program_preflight -> milestone_cycle* -> integration -> final_validation -> publication -> complete` | manifest, milestone checkpoints, rollback state, integrated acceptance evidence | protected gate, exhausted failure policy, scope envelope change | as named by program protocol; no new gate for ordinary milestone continuation |
| `implementation_patch` | explicit source/business change authorized | `received -> base_verified -> isolated_branch -> implement -> test -> diff_audit -> publish/review -> postverify -> complete` | changed-path allowlist, focused/broader tests, secret/safety check, commit/PR/head readback | path outside allowlist, base mismatch, hidden protected activation | publication/merge only when not already authorized; risky actions separately gated |
| `protocol_or_documentation_patch` | control-plane/doc mutation authorized | `received -> authority_review -> draft -> conflict_check -> structure/link_test -> publish/review -> postverify -> complete` | source crosswalk, no conflicting duplicate rules, link/index validation, exact head | constitutional ambiguity, accidental authority elevation, runtime claim | constitutional change or protected publication when not preauthorized |
| `merge_publication` | exact accepted candidate and publication scope exist | `received -> candidate_verified -> remote_preflight -> nonforce_publish -> review -> normal_merge -> readback -> close` | candidate SHA/tree, base, PR state, merge SHA, remote readback, post-merge tests | accepted head changed; non-FF/force needed; protected branch permission absent | exact publication authority required; model packet cannot grant it |
| `drift_recovery` | branch/base/objective/protocol/context drift detected | `detected -> freeze_mutation -> observe -> reconcile -> recover_or_handoff -> verify -> resume` | before/after heads, drift class, preserved changes, recovered task/checkpoint | destructive recovery, ambiguous ownership, protected evidence needed | only for authority-expanding or destructive recovery choice |
| `capability_installation_or_tooling` | task needs missing tool and installation is allowed | `need_identified -> capability_checked -> risk/size_checked -> install_or_fallback -> smoke_test -> record -> resume` | source/version/size, install command, smoke test, no secret leakage | size/license/admin/network/privacy boundary exceeds authorization | as required by explicit size/risk/task policy |
| `engine_b_senate_court` | contested knowledge claim or cross-domain adjudication | `question_framed -> evidence_collected -> adversarial_arguments -> uncertainty_reported -> human_verdict -> optional_engine_a_dispatch` | cited sources, claims/counterclaims, uncertainty and Human-visible verdict | attempt to expose hidden reasoning; evidence cannot be sourced; automatic A mutation | Human Speaker required to translate verdict into engineering action |
| `debug_or_blocker` | observed failure signature and expected behavior known | `reproduce -> diagnose -> attempt(<=policy) -> validate -> resolved_or_recorded` | reproduction, hypotheses, changed remedy each attempt, final test or failure log | retry budget exhausted; fix requires broader authority | only when real decision/new authority is required |

`milestone_cycle*` may repeat inside one program without fragmenting the task.

## 5. Task state machine

This is a manual/document control state machine, not a running orchestration service.

```text
received
  -> scoped
  -> preflight
  -> executing
       -> validating
          -> correcting -> executing
          -> candidate_ready
       -> blocked_evidence -> recover_or_human_gate
  -> candidate_ready
  -> publication_authorized? -> publish -> postverify
  -> handoff/close
  -> complete
```

Allowed terminal classifications:

- `complete`: every requirement and accepted publication boundary is evidenced;
- `human_gate_required`: meaningful progress is exhausted and a named protected decision remains;
- `blocked_recorded`: applicable retry policy is exhausted and evidence is preserved;
- `superseded`: a current Human decision replaces the objective;
- `cancelled_by_human`: explicit Human cancellation.

“Plan written”, “commit exists”, “PR opened” and “tests passed” are intermediate states unless they satisfy the full task contract.

## 6. Task input contract

A nontrivial task should make these fields recoverable, directly or by canonical inheritance:

```yaml
task:
  task_id: stable-id
  objective: concrete end state
  task_type: registry-value
  source:
    branch: exact-source-branch
    head: exact-full-sha
  work_branch: isolated-task-branch
  authority_ref: authenticated-current-human-scope
  allowed_paths: []
  required_refs: []
  prohibited_actions: []
  validation: []
  publication:
    dev_push: allowed | denied
    source_push: allowed | denied
    merge: allowed | denied | exact_head_only
  stop_conditions: []
  return_handoff: []
```

Missing critical identity, exact base, path scope or publication authority fails closed. Optional details inherit from `.ai/CODEX_TASK_INPUT_CONTRACT.md`, `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`, `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md` and, only for program-scale work, `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`.

## 7. Git workflow levels

| Level | Typical scope | Commit/push expectation | Acceptance boundary |
|---:|---|---|---|
| 0 | read-only response/report in chat | none | evidence-backed response |
| 1 | review-branch-only `.ai` communication artifact | explicit files, review branch | validated handoff/readback |
| 2 | protocol/documentation source patch | task branch, explicit commit, review handoff | normal review/publication |
| 3 | business/source code plus tests | isolated branch, exact diff/test evidence | exact candidate review and publication |
| 4 | risky/protected operation | no action without exact authority | Human gate, rollback/audit and postverify |

The levels classify workflow risk; they do not grant permission.

## 8. Validation and correction loop

For an implementation task:

1. prove the exact base and preserve unrelated changes;
2. derive requirement-to-evidence ledger;
3. make the narrowest complete change, not a smaller substitute outcome;
4. run focused tests, then broader deterministic gates proportional to risk;
5. inspect actual diff and changed paths;
6. correct failures within the same task using new evidence/hypotheses;
7. publish only under the authorized Git boundary;
8. verify the remote/merged head and rerun required post-publication checks;
9. publish the final Human/model handoff and close the original task.

The repository failure policy controls repeated attempts. A retry changes hypothesis or remedy; rereading evidence is not a repair attempt.

## 9. Completion-preserving boundary

The following usually remain internal phases of one authorized task:

- environment/tool bootstrap within the allowed size/risk policy;
- cleanup of artifacts created by that task;
- validation and evaluator repair needed to make the requested result true;
- report and changed-file ledger;
- review handoff, same-task correction and mailbox neutralization;
- authorized ready PR, normal merge and post-merge verification.

The following require a renewed decision if not already explicit:

- new product objective or materially broader business scope;
- access to secrets/private/protected content;
- destructive or irreversible repository/system action;
- force push, history rewrite or publication outside allowed branches;
- Engine B verdict converted into Engine A mutation;
- L9 runtime/Coordinator/Gateway/writer/scheduler/polling activation;
- constitutional change rather than a lower-tier routing clarification.

## 10. Evidence truthfulness

- `not_run`: no claim that a command or capability executed.
- `run_with_log`: command, exact source and result evidence exist.
- `unavailable`: capability absent or inaccessible in the observed environment.
- `semantic_only`: model/Human reasoning occurred without deterministic tool execution.
- `planned`: contract/roadmap exists; implementation is not claimed.
- `review_required`: deterministic evidence is insufficient for semantic acceptance.

Capability-specific state comes from [Capability Registry](./Capability_Registry.md). Task status must never upgrade capability maturity.

## 11. Current implementation boundary

This task model is presently executed by Humans/models through documents, Git and explicit tools. No production task queue, autonomous executor, scheduler, Coordinator or state-machine service is configured by this file. L9 remains inactive.
