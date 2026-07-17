# Context Loading and Drift Recovery v0.2

```yaml
document_id: plan3-context-loading-and-drift-recovery-v0.2
version: "0.2.0"
status: active_document_control_plane
architecture_ref: "06_Silicon_Index/Plan3_External_Augmentation_OS_Architecture.md"
operational_activation: false
drift_monitor: false
```

## 1. Purpose

This runbook defines indexed context loading, drift detection and recovery for Plan 3 tasks. It provides deterministic restart routes for the same window, a context boundary, recoverable drift and irreversible drift while preserving the original objective and authority.

It inherits authority/freshness from the [v0.2 architecture](./Plan3_External_Augmentation_OS_Architecture.md#3-canonical-authority-registry) and memory semantics from [Context Memory System](./Context_Memory_System.md). It does not activate a watcher, poller, automatic reloader or model interceptor.

## 2. Loading principles

1. First repository read follows the current repository bootstrap rule.
2. Read the current Human task before optional architecture/background files.
3. Use generated indexes and routing documents to locate sources; verify live claims with Git and active mailbox evidence.
4. Fully read every selected governing contract and required dereferenced reference.
5. Load domain protocols only when the task enters that domain.
6. Do not full-scan a corpus, private zone or protected body unless the task explicitly requires it.
7. Reuse exact-blob cached readings when allowed, but reload on a source, task, authority or context boundary.
8. Treat summaries as routing aids; do not let them override physical state.

## 3. Context load sets

### Set A — Repository bootstrap

Minimum route:

1. repository-specific startup file (`06_Silicon_Index/AI_Bootstrap_Sequence.md` in this repository);
2. current Human task/instruction;
3. task-triggered constitution, protocol, handoff or domain files;
4. physical `git status`, branch and HEAD when repository state matters.

Do not load generic README/architecture snapshots unconditionally. Use them when they help route the current objective.

### Set B — AI handoff task

When model-to-model/GitHub handoff is active:

1. `.ai/PROTOCOL.md`;
2. `.ai/STATE.yml` from the current review head;
3. current signal/pointer and every required dereferenced packet/report/receipt;
4. `.ai/PROTOCOL_ADHERENCE.md` and task-specific handoff conventions;
5. source branch/head evidence named by the packet.

Missing or unreachable refs fail closed. Immutable old STATE is replayable and not proof of active state unless bound to the currently observed review head.

### Set C — Completion-preserving large task

Load `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`, `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`, `.ai/CODEX_TASK_INPUT_CONTRACT.md`, the exact task packet and required domain sources. Load the long-run program protocol only for a genuinely program-scale task.

### Set D — Domain task

Load the relevant domain authority, schema, evaluator and source artifacts selected by the task. Domain routing cannot be inferred from a filename alone. Respect domain-specific exclusions; for example, a split-roadmap rule may prohibit loading the full graph in routine work.

### Set E — Publication/merge

Load exact accepted candidate SHA/tree, base, publication authorization, Git workflow contract, required validation evidence and active review state. Re-resolve remote heads immediately before mutation and after publication.

## 4. Drift signals

| Drift class | Observable signals | Risk |
|---|---|---|
| `context_drift` | repeated loss of objective/constraints; selected refs no longer remembered; looped work | wrong or duplicate work |
| `task_fragmentation` | one outcome split into avoidable readiness/cleanup/handoff microtasks | Human cost and incomplete closure |
| `objective_drift` | implementation solves a narrower/different problem than requested | false completion |
| `authority_drift` | model payload/current file treated as permission; protected gate silently bypassed | unauthorized action |
| `freshness_drift` | stale report/memo/STATE treated as current despite newer Git/Human evidence | action on wrong state |
| `base_or_branch_drift` | HEAD/base/work branch differs from exact task contract | contaminated diff or wrong publication |
| `scope_drift` | changed path, external action or data access falls outside allowlist | unintended blast radius |
| `evidence_drift` | stale tests, different fixtures/environment or unbound summary used as proof | unsupported claim |
| `capability_drift` | installed/available/planned capability described as executed/operational | tool hallucination |
| `protocol_drift` | missing pointer/ref, wrong actor role, wrong mailbox direction or unvalidated transition | broken handoff integrity |
| `environment_drift` | EOL, dependency, platform or configuration difference changes deterministic output | non-repeatable validation |

Detection is presently an explicit Human/model/tool observation. No background drift monitor is active.

## 5. Recovery-mode registry

| Recovery mode | Entry conditions | State path | Required evidence | Stop conditions | Human gate |
|---|---|---|---|---|---|
| `same_window_fast_path` | same task/objective; recent trusted context; source and review heads unchanged | `observe -> verify_deltas -> load_changed_refs -> continue` | current heads/status, latest handoff/report, changed files | authority/objective/base changed; repeated context loss | none for ordinary continuation |
| `context_boundary_reload` | new window/model handoff/context compaction; objective remains recoverable | `bootstrap -> resolve_task -> load_L0 -> load_required_L1/L2 -> verify -> continue` | startup contract, current Human task, physical Git, validated mailbox/checkpoint | task identity or required refs cannot be reconciled | only if missing decision/authority is real |
| `drift_recovery_reload` | one or more drift signals detected but current environment is usable | `freeze_mutation -> classify -> collect_stronger_evidence -> reconcile -> repair_context/state -> verify -> resume` | drift class, before/after state, preserved user changes, recovered source/task binding | recovery would be destructive, hide evidence or expand authority | exact destructive/authority decision only |
| `irreversible_drift_new_window_reset` | context pollution/loop makes reliable continuation unsafe | `freeze -> publish_L0/L1/L2_handoff -> verify_handoff -> start_new_window -> bootstrap -> take_over` | complete restart packet, exact refs/head, limitations, next action, takeover dry check | handoff cannot be made self-contained or protected evidence cannot move | Human only when task/product authority is unresolved; window reset itself is not new scope |
| `codex_local_git_recovery` | backend has local branch/worktree/log evidence not represented in chat | `inventory -> identify_ownership -> compare_heads/trees -> preserve -> recover_branch_or_patch -> test -> continue` | branch/worktree list, commits/trees, status, provenance, preserved unrelated files | destructive rewrite/deletion required; branch ownership ambiguous | required for destructive/high-impact recovery, not for read-only inventory |
| `foreground_github_recovery` | foreground model has no backend local filesystem state | `fetch_review_state -> dereference_pointer -> inspect_source_commit/report -> compare_human_decision -> dispatch_or_review` | GitHub-visible immutable refs, current review head, source head | required artifact is local-only/unpublished or active pointer invalid | Human/backend coordination if missing evidence must be published |
| `publication_recovery` | push/PR/merge/postverify interrupted or remote moved | `stop_mutation -> fetch -> compare_exact_heads -> classify -> resume_safe_step_or_reissue_candidate` | local/remote refs, accepted candidate, PR/merge state, command result | force/non-FF/history rewrite needed; exact candidate no longer accepted | protected publication choice only |
| `environment_repeatability_recovery` | same tree produces different bytes/results across platform/config | `capture_environment -> reproduce_cleanly -> isolate_boundary -> narrow_fix -> fresh_checkout_repeat -> record` | exact tree, config/platform, raw digests, unchanged semantic checks, repeat run | fix weakens proof semantics or requires unrelated mass rewrite | Human if fix expands product/repository policy beyond task |

## 6. Recovery procedures

### 6.1 Same-window fast path

Use only when all are true:

- task ID and objective are unchanged;
- current source/work/review heads match the last verified state;
- no new Human instruction or protocol release exists;
- the next action is within the existing authority and paths;
- cached governing files have unchanged blobs.

Reload the latest handoff/brief/report and changed files, not the whole repository. If any condition fails, select a stronger mode.

### 6.2 Context-boundary reload

1. read repository startup rules;
2. resolve the current Human task and exact objective;
3. verify Git branch/HEAD/status;
4. reconstruct L0 from physical state and validated mailbox;
5. load only the L1 decisions and L2 evidence needed for the next decision;
6. compare the reconstructed requirement ledger with current artifacts;
7. continue the original task without redoing completed, verified work.

### 6.3 Recoverable drift

1. say which drift was observed without inventing blame;
2. freeze mutations that depend on the disputed state;
3. collect stronger freshness/authority evidence;
4. preserve unrelated local work and immutable failure evidence;
5. reconcile objective, exact base, current branch, allowed paths and gates;
6. choose a non-destructive recovery (switch to correct isolated branch, reapply scoped patch, refresh refs, regenerate deterministic outputs, or correct the handoff);
7. rerun the evidence that detected drift;
8. resume the original completion-preserving task.

### 6.4 Irreversible drift and new-window reset

Before leaving the window, publish or locally preserve a restart-capable packet containing:

- objective and task ID;
- completed requirements with proof;
- remaining requirements;
- exact repository/review heads and worktree state;
- changed paths and user-owned exclusions;
- decisions/authorization/protected-gate state;
- failures, attempts and limitations;
- exact next command/action.

Verify every referenced artifact is reachable by the target environment. A new window begins with bootstrap and consumes the packet as evidence, not higher authority.

### 6.5 Codex local versus foreground GitHub recovery

| Property | Backend/Codex local recovery | Foreground/GitHub recovery |
|---|---|---|
| observable state | local branches, worktrees, reflog/log, filesystem, tools | remote branches/commits, PRs, review mailbox and published reports |
| durable shared carrier | committed/pushed Git artifact | same |
| local-only evidence | may inspect/preserve; must label unpublished | cannot assume it exists |
| recovery action | non-destructive Git and scoped task tooling | review/dispatch through GitHub-visible refs |
| forbidden inference | local branch name proves acceptance | remote recency proves authority |

## 7. Fail-closed decision tree

```text
Can current Human objective be identified?
  no -> request/resolve Human decision
  yes
    Can exact physical Git and task state be identified?
      no -> freeze mutation; inventory/recover
      yes
        Do authority and allowed paths cover the next action?
          no -> continue only safe read-only work; return exact gate
          yes
            Are required refs/evidence current and reachable?
              no -> dereference/recompute/recover
              yes -> execute, validate, checkpoint
```

Unknown state is not permission to guess. It is a reason to gather stronger evidence or stop the dependent mutation.

## 8. Verification after recovery

Recovery is complete only when:

- objective, task ID, base, branch and authority are consistent;
- unrelated user changes remain intact;
- required refs resolve and active mailbox validation passes when applicable;
- source/head-bound tests covering the drift pass in a clean or appropriately isolated environment;
- deterministic repeated runs produce the same result when repeatability is claimed;
- the next action belongs to the original task;
- L9 and other protected capabilities remain in their authorized state.

## 9. Current implementation boundary

Available now: manual indexed loading, Git evidence, active mailbox validation, explicit checkpoints, new-window handoff and deterministic verification tools.

Unavailable/inactive: automatic context loader, drift monitor, watcher, polling recovery worker, live Gateway, autonomous branch reconciler and L9 runtime. This runbook guides Humans/models; it does not run itself.
