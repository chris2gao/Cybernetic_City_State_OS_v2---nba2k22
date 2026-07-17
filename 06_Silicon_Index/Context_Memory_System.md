# Context Memory System v0.2

```yaml
document_id: plan3-context-memory-system-v0.2
version: "0.2.0"
status: active_document_control_plane
architecture_ref: "06_Silicon_Index/Plan3_External_Augmentation_OS_Architecture.md"
operational_activation: false
autonomous_memory_service: false
```

## 1. Purpose

This contract defines how Plan 3 uses repository documents and immutable Git evidence as recoverable memory for short tasks, long tasks, new windows and drift recovery. It consolidates where state, decisions and evidence live; it does not turn prose into a database or activate an autonomous memory process.

Authority and state freshness are inherited from the [Plan 3 v0.2 architecture](./Plan3_External_Augmentation_OS_Architecture.md#3-canonical-authority-registry). Memory can establish context and current state, but cannot grant a mutation or protected action.

## 2. Memory model

### L0 — Current State Index

L0 is the smallest recoverable operational snapshot. It answers “what is active now?”

Required fields when applicable:

- task/program ID and objective;
- source branch, exact source head and work/review branch;
- current phase/state and completed checkpoints;
- latest validated Human decision and authorization scope;
- latest active handoff pointer plus dereferenced packet/report refs;
- exact changed/allowed paths;
- blockers, protected gates and explicitly inactive capabilities;
- next evidence-producing action.

Canonical carriers are the validated active `.ai` mailbox, exact Git state and task-specific checkpoint. `.ai/STATE.yml` alone is not self-authenticating. A copied task payload, local chat summary or memo is not L0 until reconciled with stronger freshness evidence.

### L1 — Decision and Roadmap Memory

L1 answers “why is the task shaped this way, what has been accepted, and what remains?”

Typical carriers:

- accepted architecture decisions and Human rulings;
- task packet, completion policy and exact scope;
- milestone/checkpoint ledger;
- accepted publication heads and supersession chain;
- risk ownership and unresolved real Human decisions;
- routing/progress ledgers such as `未完成任务备忘录.yml`.

L1 is durable orientation, not live authority. A decision record must cite its originating Human event or accepted exact head. Roadmaps are expected to age and must declare when current Git/mailbox evidence supersedes them.

### L2 — Evidence and Report Memory

L2 answers “what proves the claim?”

Typical carriers:

- `.ai/CODEX_REPORTS/**`;
- `.ai/PROGRAM_RUNS/**` manifests, checkpoints and validation artifacts;
- immutable communication events, pointers, receipts and state snapshots;
- test logs and machine-readable result summaries;
- diffs, changed-path audits, source-head comparisons and post-merge readbacks;
- external/local-only evidence referenced by absolute identity and digest when repository publication is forbidden.

L2 evidence must name its exact scope, source head, command or observation method, result and limitations. A report summary never replaces the underlying artifact when the contract requires dereference or fresh recomputation.

## 3. Memory-class registry

| Class | Canonical carrier | Authority role | Freshness/invalidation | Retention | Write boundary |
|---|---|---|---|---|---|
| active Human instruction | authenticated current channel | tier 2/3 when applicable | superseded only by a newer valid Human decision or higher authority | host-defined | trusted Human channel only |
| physical source state | branch, HEAD, tree/blob IDs | no grant; proves repository state | invalid when branch/head changes | Git history | normal authorized Git workflow |
| active review mailbox | `ai/review/latest` state, signal, pointer and refs | tier-7 operational detail | invalid unless current head, state and every ref validate together | immutable event history plus current mailbox | protocol-governed writer/publication task |
| task contract | task packet and current explicit Human scope | scope contract; grant only if externally authenticated | stale when objective, exact base or permission changes | task history | Human/authorized protocol flow |
| checkpoint | task/program run artifact | no grant; restart evidence | stale when source head or prerequisite changes | preserve accepted/failure checkpoints | task-scoped explicit write |
| routing snapshot | README, generated index, memo | no grant | superseded by Git/mailbox/current source | replaceable snapshot with Git history | deterministic or explicit routing refresh |
| report/evidence | reports, logs, manifests, validation records | no grant | source-head and environment bound | immutable historical record; correct by new record | task-scoped explicit write |
| local transient context | terminal output, worktree status, conversation memory | no grant | expires on context/environment change | do not rely on long-term | local process only |
| external/private evidence | approved external store or protected channel | governed by exact task/privacy scope | source/digest/permission bound | minimum necessary | never copy to public Git without explicit authorization |
| legacy artifact | old prompts, tables, branches and superseded reports | historical evidence only | always checked against current contracts | frozen/read-only unless a migration task says otherwise | importer must not mutate source |

## 4. Source-bound memory record

A durable checkpoint or handoff should expose the following minimum shape. This is a documentation contract, not an activated storage schema.

```yaml
memory_record:
  record_id: stable-task-scoped-id
  level: L0 | L1 | L2
  task_id: exact-task-id
  objective_ref: current-human-or-task-ref
  source:
    branch: exact-branch
    head: full-commit-sha
    tree: full-tree-sha-when-needed
  observed_at: RFC-3339-timestamp
  actor_role: human_speaker | backend_executor | foreground_reviewer
  authority_ref: external-or-repository-governing-ref
  evidence_refs: []
  state: active | checkpoint | completed | superseded | failed | historical
  limitations: []
  next_action: null
```

The record is invalid as current state when required refs are missing, the claimed source cannot be resolved, the task identity conflicts, or the active mailbox is not bound to the currently observed review head.

## 5. Read, write and supersession rules

### 5.1 Read

- Start from indexes and current task scope; load the smallest set that proves the next decision.
- Fully read any selected governing contract and every required referenced packet.
- Do not interpret a filename, cached summary or report title as its body.
- Do not read secrets, credentials, private/restricted bodies or unrelated corpora merely to improve context completeness.
- For exact-byte or provenance claims, resolve Git blobs/commits rather than trusting working-tree appearance.

### 5.2 Write

- Write only within the active task’s explicit paths and authority.
- Preserve immutable history; correct an accepted/historical statement with a new source-bound record rather than rewriting its evidence.
- Update live snapshots only after their evidence exists.
- Do not place real secrets, signing keys, access tokens or private Human content in repository memory.
- A model-generated authorization field is stored only as a claim, never as proof of authority.

### 5.3 Supersede

Every replaceable snapshot should make these relationships recoverable:

```yaml
supersession:
  supersedes: prior-record-or-head
  reason: state_advanced | correction | new_human_decision | source_drift
  evidence_ref: immutable-supporting-artifact
  containing_head: observed-after-publication
```

Do not erase failure, rejection or rollback evidence. Mark it historical/superseded and link forward.

## 6. Checkpoint and recovery contract

### 6.1 Checkpoint eligibility

A checkpoint is restart-capable only when it contains:

1. exact objective and task identity;
2. exact source/work/review branch and head;
3. completed work and remaining requirements;
4. changed paths and preserved unrelated changes;
5. validation evidence with limitations;
6. authorization and protected-gate state;
7. deterministic next action or explicit Human decision needed.

“Work in progress” without these bindings is a note, not a checkpoint.

### 6.2 Recovery sequence

1. verify physical repository and active review heads;
2. resolve current Human instruction;
3. validate and dereference the active mailbox when the task uses handoff;
4. compare the latest restart-capable checkpoint with current Git state;
5. classify differences as intended progress, unrelated user state, stale evidence or drift;
6. continue the original completion-preserving objective or enter the recovery runbook in [Context Loading and Drift Recovery](./Context_Loading_And_Drift_Recovery.md).

### 6.3 Provider/environment distinction

- Codex/backend environments may recover from authorized local branches, registered worktrees, Git logs, reports and local task records.
- Foreground review environments recover from GitHub-visible commits, active review mailbox artifacts and dereferenced reports; local-only backend state is not assumed visible.
- A chat/client session identifier is transient diagnostic metadata. It does not replace task ID, branch, source head or durable checkpoint and should not be published publicly unless the exact task requires it.

## 7. Freshness and cache rules

| Cached item | Reuse allowed when | Mandatory reload trigger |
|---|---|---|
| constitution/protocol | blob/head unchanged and no higher instruction conflicts | protocol release, Human correction or authority conflict |
| task packet | task ID/objective/base/permission unchanged | task update, new Human decision or base drift |
| active mailbox | current review head and all refs still validate | review head changes or any required ref changes/missing |
| source-file reading | exact blob unchanged | changed blob, changed domain contract or disputed claim |
| test result | exact source/environment/suite binding still applies | code/fixture/config/environment changes |
| generated index | manifest digest and Git index unchanged | tracked path/blob change |
| historical report | always reusable as historical evidence | never promoted to current without new verification |

A cache hit reduces rereading; it never bypasses an explicit “read fully” task requirement.

## 8. Privacy, retention and provenance

- Public Git memory contains only content authorized for that repository.
- Local logs should store the minimum necessary evidence and use digests/paths rather than secret-bearing dumps.
- Private evidence stays in the approved private channel; public reports record only safe metadata and conclusions.
- Exact source and validation provenance should be reproducible without exposing private model reasoning.
- Human briefs should summarize decisions and risks; they should not become a shadow state database.
- Obsidian remains `planned` and unavailable as an official channel until privacy, publication and synchronization boundaries are explicitly decided.

## 9. Failure and rollback semantics

Fail closed when source identity, task identity, active mailbox binding, required refs, authorization context or evidence scope cannot be established. Preserve evidence, avoid speculative state writes, and report the smallest real decision needed.

Rollback means restoring an authorized repository/runtime state with an auditable forward or revert commit and updating L0/L1 evidence. It does not mean deleting history or using destructive Git by default.

## 10. Current implementation boundary

Implemented today:

- document/Git-based L0/L1/L2 carriers;
- pointer-based GitHub handoff contracts and a repository-level validator;
- deterministic repository indexes;
- reports, run folders and manual checkpoints;
- manual/new-window recovery procedures.

Not implemented or activated:

- autonomous context-memory database/service;
- trusted identity and authorization host;
- automatic checkpoint writer, retention worker or garbage collector;
- live drift detector, watcher or poller;
- Obsidian synchronization;
- L9 runtime integration.

This file unifies the memory contract; it does not claim those missing layers.
