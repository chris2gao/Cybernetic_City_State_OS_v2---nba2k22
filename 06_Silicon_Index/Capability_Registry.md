# Capability Registry v0.2

```yaml
document_id: plan3-capability-registry-v0.2
version: "0.2.0"
status: active_fail_closed_document_registry
architecture_ref: "06_Silicon_Index/Plan3_External_Augmentation_OS_Architecture.md"
operational_activation: false
capability_broker: false
```

## 1. Purpose

This registry is the global Plan 3 truthfulness index for external tools, skills, apps, communication channels and protected runtime components. It identifies what can be claimed, by whom, under which scope and evidence.

It does not install a tool, authenticate an actor, grant authorization, choose a capability automatically or activate a broker/runtime. Authority/freshness follow the [canonical v0.2 registry](./Plan3_External_Augmentation_OS_Architecture.md#3-canonical-authority-registry).

## 2. Non-negotiable semantics

- A filename, prompt, schema, interface or prototype name is not a capability.
- “Available” is not “executed”; “executed” is not “passed”; “passed” is not “integrated”; “integrated” is not “production operational”.
- A payload `human_gate`, `approved`, `trusted` or actor field is descriptive and cannot authorize itself.
- Capability evidence is exact-scope, exact-source and environment bound.
- Unknown capability, actor, authorization scope, evidence or activation state fails closed.
- Tool output supports a claim only when the execution is recorded or independently observable.
- No capability bypasses Human Speaker, Engine A/B routing, privacy, publication or L9 gates.

## 3. State model

### 3.1 Maturity/evidence

| Tier | Maturity ceiling | Meaning |
|---|---|---|
| T0 | `absent` / `planned` | no implementation/validation evidence, prohibition or unimplemented idea |
| T1 | `specified` / `implemented_unvalidated` | prose, contract, schema, prompt or implementation artifact exists; execution unproven |
| T2 | `statically_validated` | deterministic implementation has focused static, fixture or unit evidence |
| T3 | `integration_validated` | real inputs/integration and any claimed persistence are evidenced |
| T4 | `operational` | repeated production operation has monitoring, audit, rollback and source-bound evidence |

### 3.2 Lifecycle

`current`, `session_observed`, `planned`, `blocked`, `deprecated`, `frozen`, `superseded`.

### 3.3 Activation

`manual_only`, `read_only`, `human_gated`, `inactive`, `blocked`, `prohibited`, `external_session_only`.

Maturity is evidence, not activation. A T2 inactive component remains inactive. Session-observed availability must be rediscovered in a new environment.

### 3.4 Execution claim

| Claim | Required evidence |
|---|---|
| `not_run` | no execution claim |
| `run_with_log` | command/tool identity, exact input/source, output/result and limits |
| `unavailable` | observed absence/inaccessibility and checked environment |
| `semantic_only` | Human/model conclusion clearly separated from tool execution |
| `planned` | governing roadmap/contract and explicit non-implementation |
| `review_required` | deterministic result exists but semantic/Human acceptance remains open |

## 4. Capability record contract

Every durable capability entry must expose all fields below. The table in §5 is the canonical v0.2 snapshot; task-local evidence may narrow it but cannot silently upgrade it.

```yaml
capability:
  capability_id: stable-id
  lifecycle_state: current | session_observed | planned | blocked | deprecated | frozen | superseded
  maturity_state: absent | planned | specified | implemented_unvalidated | statically_validated | integration_validated | operational
  evidence_tier: T0 | T1 | T2 | T3 | T4
  activation_state: manual_only | read_only | human_gated | inactive | blocked | prohibited | external_session_only
  actors: []
  authorization_scope: exact-action-and-data-scope
  evidence_refs: []
  risks: []
  validation: []
  fallback: fail-closed-or-alternative
  activation_boundary: explicit-boundary
  allowed_claims: []
  forbidden_claims: []
```

## 5. Canonical capability snapshot

### 5.1 Local engineering and repository controls

| Capability ID | State / evidence | Actors | Authorization scope | Principal risks | Validation | Fallback | Activation boundary / evidence |
|---|---|---|---|---|---|---|---|
| `local_filesystem` | `session_observed`, environment-specific, `external_session_only` | backend execution agent | task-authorized roots and paths only | unrelated overwrite, private/secret read, path escape | status/diff, explicit path checks, sandbox/host evidence | read-only inventory or stop | host provides access; never infer other machines; no secret scope by default |
| `terminal_shell` | `session_observed`, environment-specific, `external_session_only` | backend execution agent | task commands within host policy | destructive command, injection, environment contamination, excessive install | command/result log, exit code, focused smoke test | safer read-only tool/manual inspection | host/tool availability; destructive/high-impact operations remain separately gated |
| `git_local` | `current`, T2 for ordinary deterministic Git operations, `manual_only` | backend execution agent | exact repository/task branch and Git action | wrong branch/base, history rewrite, user-change loss | branch/HEAD/status/tree/blob readback, non-destructive diff | isolated worktree/patch or stop | force/destructive operations require explicit authority; existence of branch is not acceptance |
| `github_remote` | `session_observed`, `human_gated` for mutation | backend agent; foreground review connector; Human | exact repo/branch/PR/action granted by task | wrong remote, unauthorized publication, stale candidate, public data leak | remote refs, PR state, commit/tree readback, normal-merge proof | local commit/report and request publication | connector/CLI auth is availability, not publication authority; no force/default master push |
| `directory_index_control_plane` | `current`, T2, `read_only` generation/check with explicit output writes | backend agent | tracked repository metadata and deterministic generated paths | stale index, unsafe link, EOL drift, generated-file churn | generator `check`/`validate`/snapshot/self-test and repeated zero diff | route via `rg --files` and report stale index | `generate_repository_indexes.py`, generated indexes and manifest; no watcher/poller |
| `communication_compliance_gate` | `current`, T2 repository-level validator, `read_only` | backend/reviewer with trusted external contexts where required | exact immutable event/state/pointer validation | replay, actor forgery, self-authorization, mutable ref, proof reachability | fresh full test suite and exact transition validation | fail closed and communicate through Human-visible manual channel | `.ai/communication_compliance/**`; no live Gateway, writer or interception |
| `github_human_brief` | `current`, T3 document workflow, `manual_only` | backend, foreground reviewer, Human | protocol-governed review branch and source refs | stale brief, missing pointer, excessive Human cost | current review head, dereferenced refs, source readback | direct Human chat plus later durable handoff | `.ai/HUMAN_BRIEF.md`, STATE/INBOX/OUTBOX and GitHub history; no unattended publisher |

### 5.2 Knowledge, calculation and extensibility

| Capability ID | State / evidence | Actors | Authorization scope | Principal risks | Validation | Fallback | Activation boundary / evidence |
|---|---|---|---|---|---|---|---|
| `deterministic_calculation` | `session_observed` by tool, otherwise `specified`; `external_session_only` | backend/foreground tool user | exact calculation and allowed data | wrong formula/input, opaque transformation, false run claim | reproducible command/notebook/tool log, independent check when high risk | label `semantic_only` or do calculation transparently by hand | tool/runtime must be observed per session; domain truthfulness contract may add gates |
| `web_search_and_scrape` | `session_observed` when a web tool exists; `external_session_only` | authorized model/tool user | public/approved URLs and task query | stale/misleading sources, copyright, privacy, prompt injection, unauthorized login | direct citations, dates, primary sources for technical/high-stakes claims, extraction limits | repository/local authoritative sources or disclose uncertainty | current tool availability plus task/privacy scope; no credential use inferred |
| `domain_specific_skill` | `session_observed` or `planned`, `external_session_only` | model/tool user | exact named skill and task scope | instruction conflict, overclaim, hidden external side effects | read complete skill instructions, record tool result, apply higher authority | manual workflow using canonical contracts | skill augments capability; it never grants Human authority or domain acceptance |
| `app_plugin_mcp` | `session_observed` or `planned`, generally `human_gated` for external writes | model plus connected host/app | exact connector, account, data and action | third-party mutation, privacy, stale auth, data exfiltration | discover callable capability, inspect scope/result, external readback | no-op/manual Human action/local artifact | installation/auth and each external write follow host/task scope; connector name alone proves nothing |
| `tool_installation` | `session_observed`, `human_gated` by active size/risk policy | backend execution agent | named dependency, source, version and size | supply chain, disk/network cost, admin change, environment pollution | source/version/size check, install log, smoke test | bundled tool, smaller dependency or manual method | current task may preauthorize bounded installs; larger/riskier changes require explicit gate |

### 5.3 Planned channels and isolated prototypes

| Capability ID | State / evidence | Actors | Authorization scope | Principal risks | Validation | Fallback | Activation boundary / evidence |
|---|---|---|---|---|---|---|---|
| `obsidian_human_brief` | `planned`, T0, `inactive` | none operational | not granted | private/public boundary, sync conflict, shadow state | no current implementation evidence | GitHub Human brief | requires Human decision on privacy/publication, design, implementation and E2E proof |
| `local_bus_prototype` | `implemented_unvalidated` globally, T1, `inactive` | repository developer only in an authorized task | isolated prototype inspection/test | mistaken runtime claim, unsafe routing, duplicate communication system | task-specific code/tests and integration evidence not established globally | existing GitHub document protocol | scripts/files are prototypes; separate authority/design needed before any activation |
| `system_backbone_registry_prototype` | `specified`/prototype, T1, `inactive` | repository/domain developer | isolated schema/index work | duplicate authority registry, stale symbolic entries, config/runtime confusion | schema/path checks and explicit domain tests | v0.2 authority crosswalk plus domain registries | `system_backbone/**` artifacts are not a production registry hub or capability broker |
### 5.4 Protected L9 capabilities

| Capability ID | State / evidence | Actors | Authorization scope | Principal risks | Validation | Fallback | Activation boundary / evidence |
|---|---|---|---|---|---|---|---|
| `trusted_identity_authorization_host` | `blocked`, T0, `inactive` | no production actor configured | none | forged Human/model identity, replay, scope escalation | production identity, action binding, replay protection and security review required | current authenticated Human channel/manual gate | separate Human-authorized design/implementation; test fixtures are never production trust |
| `communication_gateway` | `blocked`, T0 globally, `inactive` | none operational | none | interception errors, self-authorization, message loss/replay | E2E trusted-context validation, failure isolation, audit and rollback | manual GitHub pointer workflow | separate protected runtime task; repository validator does not activate Gateway |
| `atomic_state_writer_and_replay_store` | `blocked`, T0, `inactive` | none operational | none | races, replay, corruption, unauthorized mutation | CAS/atomicity, nonce consumption, crash recovery, privacy and rollback tests | explicit Git/manual writes under protocol | requires trusted host, persistence and production integration task |
| `runtime_coordinator` | `blocked`, T0, `inactive` | none operational | none | autonomous scope drift, Human bypass, cross-domain mutation | exact routing semantics, authorization, sandbox, observability, rollback and E2E pilot | Human/model manual routing | separate Human-approved L9 activation; prompts/prototypes do not count |
| `capability_broker` | `blocked`, T0, `inactive` | none operational | none | implicit tool authority, data leakage, wrong actor/account | policy enforcement, discovery truthfulness, least privilege, audit and revoke tests | explicit per-task tool selection | separate design and Human approval |
| `business_or_learning_state_writer` | `blocked`, T0, `inactive` | none operational | none | privacy loss, invalid state transitions, irreversible writes | domain schema, trusted authorization, persistence/rollback and E2E proof | read-only evaluation/manual Human record | separate domain/task authorization; legacy tables never become production state implicitly |
| `scheduler_poller_watcher` | `blocked`, T0, `inactive` | none operational | none | unattended actions, duplicate work, stale polling, runaway cost | idempotency, scheduling semantics, stop controls, monitoring and rollback | explicit Human-triggered runs | each scheduler/poller/watcher requires separate protected activation |
| `production_observability_and_rollback` | `planned`, T0, `inactive` | none operational | none | false health, sensitive logs, untested recovery | metrics/log privacy, incident tests, rollback rehearsal | Git/test/report evidence | prerequisite for production L9 operation, not proof of operation itself |

## 6. Actor and authorization rules

### Backend execution actor

May use locally available filesystem, terminal, Git and explicit tools within the current task and host policy. It may not infer source publication, external-account mutation, protected-body access or L9 activation from tool availability.

### Foreground review actor

May inspect GitHub-visible evidence and use available read tools/connectors within task scope. It may not claim backend local state, execute source publication without authority, or self-accept its own protected transition.

### Human Speaker

Provides routing and protected decisions through an authenticated current channel. A repository file that says “Human approved” is evidence only after the governing protocol binds it to trusted origin and exact action.

### Trusted external host

Future production authorization/identity infrastructure must inject actor/authorization contexts from outside model-generated payloads. No real secret, key or credential belongs in fixtures, reports or this registry.

## 7. Capability selection procedure

1. identify the exact task operation and data scope;
2. look up the capability’s durable state and boundary;
3. rediscover session availability instead of trusting old reports;
4. verify actor and current authorization scope;
5. choose the lowest-risk capability that fully satisfies the operation;
6. execute and record `run_with_log`, or label `not_run`/`unavailable`/`semantic_only` truthfully;
7. validate the result independently when risk or contract requires it;
8. do not upgrade registry maturity without a source-bound registry revision.

If a required capability is absent, use an authorized fallback or return the exact missing capability/decision. Do not fabricate output.

## 8. Change control

Any capability upgrade must name:

- prior and proposed lifecycle/maturity/evidence/activation states;
- exact implementation and current validation refs;
- actors and least-privilege authorization scope;
- risks, failure modes, fallback and rollback;
- integration environment and observed source head;
- whether Human approval is required;
- prohibited claims that remain prohibited.

An implementation commit may move T0/T1 to T2 when scoped static evidence supports it. T3 requires integration evidence. T4 requires repeated production operation. None of these automatically changes activation state.

## 9. Current conclusion

Plan 3 has useful local engineering tools, Git/GitHub document workflows, deterministic indexes and a statically validated communication gate. It does not yet have a trusted production host, capability broker or L9 runtime. Obsidian remains planned. Coordinator, Gateway, writers, scheduler, polling and watchers remain inactive.
