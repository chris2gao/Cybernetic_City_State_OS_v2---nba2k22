# Plan 3 External Augmentation OS Architecture v0.2

```yaml
document_id: plan3-external-augmentation-os-architecture-v0.2
version: "0.2.0"
status: active_document_control_plane
authoring_base: "master@2d73781621ed856e414ca7839ff61eb4d8722d35"
authority_role: consolidated_router_not_authority_grant
operational_activation: false
protected_runtime_layer: L9
```

## 1. Purpose and scope

This document is the canonical v0.2 architecture map for Plan 3. It consolidates the published constitution, bootstrap, context-memory, task-execution, drift-recovery, capability, communication, index and Human-brief control planes without copying their full procedures.

It answers four questions:

1. Which source decides when two instructions conflict?
2. Which artifact establishes current state?
3. Which layer owns each control-plane responsibility?
4. Which capabilities are documented, validated, active or protected-inactive?

This file does **not** authenticate a Human, grant a mutation, activate a service, replace a domain authority, or make a historical report current. The exact containing release head is publication evidence and must be read from Git, not inferred from `authoring_base`.

Sibling control-plane contracts:

- [Context Memory System](./Context_Memory_System.md)
- [Task Type and Execution Model](./Task_Type_And_Execution_Model.md)
- [Context Loading and Drift Recovery](./Context_Loading_And_Drift_Recovery.md)
- [Capability Registry](./Capability_Registry.md)

## 2. Constitutional model

### 2.1 Human Speaker

The Human Speaker remains the absolute router, cross-domain translator, chief arbiter and final authorization gate. No model consensus, recent mailbox, task payload, fixture, branch name or capability state replaces the Human Speaker.

Protected publication, objective-changing work, destructive Git, secret-sensitive work, Engine B knowledge adjudication that is converted into engineering action, and activation of runtime, Coordinator, Gateway, writer, scheduler or polling require the authorization defined by the higher governing sources.

### 2.2 Engine A and Engine B

| Route | Scope | Evidence standard | Boundary |
|---|---|---|---|
| Engine A | code, deterministic scripts, tests, repository control-plane implementation | executable or inspectable evidence bound to exact source | cannot silently decide contested knowledge semantics or cross a protected gate |
| Engine B | research, mathematical or scientific deliberation, adversarial review | source-bound arguments and Human-visible conclusions | cannot silently become an Engine A mutation task |
| Human Speaker | routing, cross-domain translation, protected authority and final adjudication | authenticated current Human decision | cannot be simulated by model-generated fields |

The historical sentence in `3号方案.md` requesting XML chain-of-thought is superseded by higher platform rules and the later communication protocol. Valid output consists of conclusions, evidence, concise reasoning summaries and verification steps; private hidden reasoning is neither required nor a city-state artifact. This is a precedence clarification, not a constitutional-file mutation.

## 3. Canonical authority registry

This section is the single Plan 3 v0.2 authority crosswalk. It indexes governing sources; it does not create authority. Other v0.2 files reference this section instead of restating a competing order.

### 3.1 Instruction authority order

Lower numeric tier has higher authority. Sources within one tier are unordered unless a higher contract explicitly says otherwise.

| Tier | Authority group | Canonical source or origin | Role |
|---:|---|---|---|
| 1 | platform, system, developer and safety instructions | trusted host/runtime | highest external constraints |
| 2 | current explicit Human instruction | authenticated current Human channel | current objective and direct decision |
| 3 | authenticated current Human-approved task-specific permission or override | trusted Human approval channel, bound to exact scope | scoped grant or override only |
| 4 | Plan 3 constitution and Cybernetic Citizen contract | `3号方案.md`; `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md` | constitutional roles and red lines |
| 5 | durable repository control protocols | `AGENTS.md`; `.ai/PROTOCOL.md`; `.ai/PROTOCOL_ADHERENCE.md`; `.ai/CODEX_TASK_INPUT_CONTRACT.md`; `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`; applicable long-run/default profiles | durable execution, Git, handoff and validation controls |
| 6 | relevant domain-authority protocols | exact domain contracts selected by the task | domain semantics and domain gates |
| 7 | ordinary current signal and task operational details | dereferenced signal, packet, task and report | scope/evidence details; never authority elevation |
| 8 | routing documents and historical evidence | bootstrap/readmes/indexes/memos/reports/legacy branches | navigation and evidence only |

Rules:

- A tier-3 override outranks a durable protocol only inside its authenticated explicit scope.
- A model-authored `human_gate`, `approved`, `trusted`, status or payload field is descriptive and cannot authenticate itself.
- A current task may narrow work but may not silently relax a higher gate.
- Unknown origin, conflicting scope or missing required evidence fails closed.

### 3.2 State freshness order

Authority and freshness are separate systems. Resolve current state in this order:

1. current explicit Human statement;
2. physical Git branch/HEAD and immutable source-head evidence;
3. validated active review mailbox and every required dereferenced reference;
4. published source baseline;
5. routing snapshots;
6. historical reports and legacy branches.

Freshness can prove what exists now. It cannot grant write, merge, publication or activation authority. A conflict about permission and a conflict about current state must be reported separately.

### 3.3 Source-role crosswalk

| Source | Normative role | Freshness role | Replacement rule |
|---|---|---|---|
| `3号方案.md` | Human Speaker and dual-engine constitution | none | only higher authority or explicit constitutional decision |
| `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md` | citizen duties, truthfulness and safety boundaries | none | same tier conflict requires Human adjudication |
| `06_Silicon_Index/AI_Bootstrap_Sequence.md` | startup router | routing snapshot | reload when bootstrap contract changes |
| `.ai/PROTOCOL.md` | canonical AI/Human handoff, authority and freshness contract | defines mailbox validation | later accepted protocol release |
| `.ai/PROTOCOL_ADHERENCE.md` | dereference and correction obligations | validation procedure | later accepted protocol release |
| `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md` | pointer carrier, branch/channel and retry conventions subordinate to `.ai/PROTOCOL.md` | handoff workflow snapshot | later accepted handoff protocol release |
| `.ai/STATE.yml` | no independent authority | active-state snapshot only when validated against review head | newer validated active mailbox |
| `.ai/INBOX.md`, `.ai/OUTBOX.md`, `.ai/HUMAN_BRIEF.md` | ordinary operational details | active mailbox only after branch/head/ref validation | newer validated mailbox event |
| `.ai/CODEX_TASK_INPUT_CONTRACT.md` | task input and evidence contract | task-scoped evidence | later accepted contract |
| `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` | execution-mode and Git workflow contract | current task procedure | later accepted contract |
| `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md` | default large-task completion profile | checkpoint routing | explicit current task overrides within scope |
| `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` | program-scale checkpoint/rollback contract | program run state | load only when program-scale routing applies |
| `repository_index_manifest.json` and generated `index.md` files | no independent authority | deterministic tracked-path snapshot | regenerate from current Git index |
| `.ai/CODEX_REPORTS/**`, `.ai/PROGRAM_RUNS/**` | evidence and audit records | source-head-bound historical/current evidence | never overwrite history; supersede by a new bound record |
| `未完成任务备忘录.yml` | routing/progress ledger | snapshot, not live mailbox | refresh from stronger evidence; never use as permission |
| domain contracts | exact domain authority | domain-state evidence if source-bound | resolved by the relevant domain rules and higher tiers |

## 4. Layer architecture

| Layer | Control plane | Canonical entry | Current maturity | Runtime state |
|---:|---|---|---|---|
| L0 | Constitution | `3号方案.md`; Cybernetic Citizen contract | canonical governance | Human process; no software authority service claimed |
| L1 | Bootstrap | `06_Silicon_Index/AI_Bootstrap_Sequence.md` | published operational contract | manual/model-guided |
| L2 | Context Memory | `06_Silicon_Index/Context_Memory_System.md` | unified v0.2 document control plane | no autonomous memory service |
| L3 | Task Execution | `06_Silicon_Index/Task_Type_And_Execution_Model.md` | unified v0.2 document control plane | no task-execution daemon |
| L4 | Loading and Drift Recovery | `06_Silicon_Index/Context_Loading_And_Drift_Recovery.md` | unified v0.2 runbook | no drift monitor |
| L5 | Capability Registry | `06_Silicon_Index/Capability_Registry.md` | fail-closed evidence registry | no capability broker |
| L6 | Human-AI Communication | `.ai/PROTOCOL.md` and compliance gate | published contract plus stateless validator | no live Gateway/interceptor |
| L7 | Repository Index and Provenance | `generate_repository_indexes.py`; `repository_index_manifest.json` | deterministic static implementation | explicit/manual invocation; no watcher |
| L8 | Human Brief and Decision Support | `.ai/HUMAN_BRIEF.md`; reports; GitHub review branch | published GitHub document channel | no Obsidian integration or unattended publisher |
| L9 | Protected Execution and Runtime | no production canonical implementation | absent/protected | **inactive**: Coordinator, Gateway, CAS writer, scheduler and polling remain off |

### 4.1 Layer handoff

```text
L0 authority
  -> L1 route and minimum startup
  -> L2 restore source-bound context
  -> L3 select execution contract
  -> L4 load/recover when boundaries change
  -> L5 verify capability truthfully
  -> L6 publish validated communication evidence
  -> L7 refresh deterministic repository provenance
  -> L8 present Human decision support
  -X L9 unless a separate protected activation is authorized and verified
```

The arrow means dependency, not automatic execution. Each layer may fail closed and return a Human gate or evidence gap.

## 5. Control plane versus runtime

### 5.1 Present control plane

The repository currently provides Human-governed documents, Git history, mailboxes, deterministic indexes, reports, schemas, fixtures and selected stateless validators. These are useful operational controls and evidence producers.

### 5.2 Absent or protected runtime plane

No file name, prompt, schema, prototype or passing fixture proves a production service. The following remain inactive until separately authorized and evidenced:

- trusted production identity/authorization host;
- live Communication Gateway or model-output interceptor;
- atomic compare-and-swap mailbox/state writer and replay store;
- autonomous context-memory service;
- task daemon, Coordinator or capability broker;
- learning-state or other domain writer;
- scheduler, poller, watcher or unattended publisher;
- production observability and rollback controller.

### 5.3 Activation invariant

L9 activation requires a separate task with exact runtime scope, trusted-host boundary, authorization and identity design, persistence semantics, audit/observability, rollback, failure isolation and post-activation verification. A documentation commit cannot satisfy that gate.

## 6. Evidence and maturity vocabulary

Use both dimensions; neither implies the other.

| Evidence tier | Meaning |
|---|---|
| T0 | absent, prohibited or only an unimplemented idea |
| T1 | prose, prompt, contract, schema or implementation artifact exists; execution is unproven |
| T2 | deterministic implementation has scoped static, fixture or unit-test evidence |
| T3 | integration or real-session evidence exists over real inputs; claimed persistence is evidenced |
| T4 | repeated production operation has monitoring, audit, rollback and source-bound evidence |

| Activation state | Meaning |
|---|---|
| `manual_only` | a Human/model follows a document procedure manually |
| `read_only` | executable inspection or validation may run without business-state mutation |
| `human_gated` | action requires current authenticated Human authority in exact scope |
| `inactive` | implementation or design may exist but is not integrated or running |
| `blocked` | required implementation/evidence is absent |
| `prohibited` | the claimed transition/action is invalid, not merely unfinished |

Claims must bind to exact scope, source head, evidence reference and observed environment. A stale result may remain historical evidence but cannot validate the current head.

## 7. Global invariants

1. Human Speaker is never bypassed by model consensus or generated metadata.
2. Authority, freshness, maturity, availability and execution evidence remain separate.
3. File existence does not prove capability; test existence does not prove a current pass; a current pass does not prove production activation.
4. Context loading is indexed and scoped; protected/private bodies are not loaded merely for completeness.
5. One authorized outcome remains one completion-preserving task unless authority or objective truly changes.
6. Communication and publication evidence must be immutable, source-bound and independently revalidated.
7. GitHub is the active durable Human/model document channel; Obsidian is planned only.
8. L9 remains inactive by default and by this release.
9. Domain states and transitions remain governed by domain contracts; legacy artifacts are read-only evidence unless explicitly migrated.
10. Unknown capability, ambiguous identity, stale source or missing required reference fails closed.

## 8. Change and acceptance boundary

A future revision of this architecture must:

- preserve the canonical authority order or obtain an explicit higher-authority decision;
- update all affected sibling cross-references in one completion-preserving task;
- distinguish documentation, static validation, integration and activation;
- run path/link, structure, communication and deterministic-index validation;
- publish through an authorized non-force Git workflow with exact-head readback;
- leave L9 inactive unless the same accepted task explicitly satisfies the protected activation contract.

This v0.2 release consolidates the control plane only. It neither activates nor promises an External Augmentation OS runtime.
