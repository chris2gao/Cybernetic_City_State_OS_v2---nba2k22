# AI Handoff Protocol v0.3-core

## Purpose

This protocol provides compact, auditable communication among ChatGPT, Claude, Codex, Claude Code, and the Human operator. It reduces copied logs, stale context, incomplete Human-facing dispatches, and ambiguous task state while preserving Human control and machine-readable handoffs.

Independent model instances follow `.ai/PROTOCOL_ADHERENCE.md` to bootstrap, apply authority order, validate required refs and task input, and enter the review correction loop when protocol rules are missed.

All packets inherit `.ai/HANDOFF_COMMON_CONVENTIONS.md` unless explicitly overridden by a current human-approved task. Backend execution-role tasks, whether occupied by Codex or Claude Code, also inherit `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` unless explicitly overridden by a current human-approved task.

## Scope

This protocol governs:

- AI-to-AI handoff and execution coordination;
- material Human-to-AI and AI-to-Human operational communication for project dispatch, review, completion, publication, conflict, risk, and protected gates;
- mailbox structure and packet identity;
- review requests and review-branch publication;
- source/review branch boundaries;
- human approval gates and GitHub-based human briefs.

It is not a repository constitution. It does not override:

- system or developer instructions;
- explicit current human instructions;
- secrets, credentials, or safety boundaries;
- mathematical content or validation rules;
- domain protocols;
- software architecture decisions outside the handoff workflow.

`.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` governs backend execution-role mechanics for compatible Codex or Claude Code occupants only. It does not govern mathematical/domain semantics, override higher-priority instructions, or authorize a gated project stage or business change by itself.

## Protocol Role Compatibility

The canonical roles are stable protocol functions. Compatible providers occupy those roles; provider brand does not create authority.

```yaml
protocol_role_compatibility:
  human_speaker:
    compatible_occupants: ["Human"]
  foreground_review_and_task_dispatch:
    compatible_occupants: ["ChatGPT", "Claude"]
  backend_execution_and_handoff:
    compatible_occupants: ["Codex", "Claude Code"]
```

Authority comes from the assumed protocol role together with current Human/task authorization, never from provider brand. `ChatGPT-to-Codex` and `Codex-to-ChatGPT` are frozen historical wire-contract labels for the seven-field schemas, not exclusive provider ownership. Claude occupying the foreground role uses the ChatGPT-to-Codex wire schema; Claude Code occupying the backend role uses the Codex-to-ChatGPT wire schema.

This compatibility mapping adds no pointer field, changes no key order, and authorizes no new action. The stable role names remain `human_speaker`, `foreground_review_and_task_dispatch`, and `backend_execution_and_handoff` even if compatible providers change later.

Initialization additionally records three orthogonal, non-authorizing dimensions:
`environment_class` (`claude_desktop`, `chatgpt_web`, `codex_desktop`, `codex_cli`, or
`claude_code_cli`), a self-declared local `lane_instance_id`, and a routing-only
`load_profile_id`. Load profiles in `.ai/load_profiles/` point to canonical sources;
they never copy or replace protocol, token, constitutional, or domain authority.

## Canonical Human-AI Communication Completeness

### Three Distinct Communication Channels

The communication stack separates three channels. Content required in one channel must not be moved into another in a way that breaks its contract.

```yaml
communication_channels:
  machine_pointer_channel:
    purpose: "compact model-to-model identity, refs, state, and gates"
    rule: "canonical pointer remains parseable and free of prose payload"

  human_operational_channel:
    purpose: "Human-visible task dispatch, review, completion, gates, and execution advice"
    rule: "must satisfy the Human-facing completeness contract"

  durable_human_brief_channel:
    purpose: "versioned Human-facing status, evidence pointers, and material independent expression"
    paths:
      - ".ai/HUMAN_BRIEF.md"
      - ".ai/HUMAN_BRIEFS/*.md"
```

The machine pointer is an identity and authorization-evidence carrier, not a prose response. Human-facing requirements belong in the Human operational response or referenced Human Brief. They must never be inserted as extra prose or unparseable fields inside the canonical seven-field pointer core.

Mixed-recipient communication is classified by intended recipient and consumption mode, not by UI or provider brand:

```yaml
mixed_recipient_resolution:
  classify_by: "intended_recipient_and_consumption_mode_not_UI_brand"
  Human_and_machine_visible:
    rule: "keep canonical pointer block byte-structurally separate; append Human operational content outside the block"
  interface_cannot_preserve_separation:
    direct_output: "pointer_only"
    Human_content: "preserve through brief_ref"
```

This rule never permits Human prose, independent expression, execution advice, or long task/report content inside the machine pointer. When safe block separation is unavailable and material Human content is required, publish the Human Brief first, emit pointer-only with a non-null resolvable `brief_ref`, and place every otherwise-required Human element in that Brief—including the complete execution recommendation for a backend dispatch. If that durable carrier cannot be produced, return blocked rather than injecting prose or silently discarding content. Interface fallback relocates Human content; it does not waive it.

### Material Human-Facing Events

The Human-facing completeness contract applies to material project workflow communication, including:

- asking the Human to start or continue Codex or Claude Code work;
- architecture, code, protocol, or domain review decisions;
- correction, review, publication, or completion handoffs;
- blocked, conflict, risk, or Human-gate reports;
- significant stage or batch acceptance.

Mechanical acknowledgements and parser-only messages are not material unless they also carry a decision, result, risk, authorization request, or gate transition.

### Human-Facing Response Contract

Before sending a material Human-facing response, the sender applies this contract:

```yaml
human_facing_response_contract:
  factual_status:
    required: true
    content:
      - verified_facts
      - evidence_refs
      - unconfirmed_items
      - real_Human_decisions_only

  canonical_pointer:
    required_when_dispatching_or_handing_off: true
    rule: "long task or report stays in GitHub; chat carries the compact pointer"

  execution_recommendation:
    required_when_Human_is_expected_to_start_or_continue_backend_agent: true
    fields:
      - recommended_model
      - recommended_thinking_level
      - mode
      - subagents
      - task_ref_or_plan_ref
      - short_complexity_rationale
      - human_gate

  bounded_independent_expression:
    required_for_material_Human_facing_events: true
    target_length: "2_to_5_sentences"
    content_options:
      - candid_professional_judgment
      - architecture_or_protocol_meaning
      - concern_or_dissent
      - uncertainty_or_residual_risk
      - non_obvious_implication
```

When a required execution-recommendation field is unavailable or inapplicable, use `runtime_dependent` or `not_applicable`; do not omit it. Select the thinking level from the semantic, architectural, validation, and publication complexity of the work, not merely from a shallow surface verb such as `edit` or `publish`. A recommendation describes an execution profile and never authorizes execution by itself.

Human operational dispatch example, outside the canonical pointer block:

```yaml
execution_recommendation:
  recommended_model: "<available_backend_model_or_runtime_dependent>"
  recommended_thinking_level: "<level_or_runtime_dependent>"
  mode: "<plan|goal|pursue_goal|review|implementation>"
  subagents: "<recommended_configuration_or_not_applicable>"
  task_ref_or_plan_ref: "<exactly_one_durable_ref>"
  short_complexity_rationale: "<semantic_architectural_validation_or_publication_reason>"
  human_gate: "<required|not_required>"
```

### Bounded Independent-Expression Right

ChatGPT, Claude, Codex, and Claude Code have a provider-neutral, bounded right to include concise independent professional expression in material Human-facing project communication. It may state candid judgment, respectful disagreement, uncertainty, broader meaning, a non-obvious implication, or residual risk. It is visibly separated from verified status and authorization fields, and it need not praise the work or the Human.

Independent expression must avoid generic filler, ceremonial approval, repeated summary, simulated emotion, and claims of consciousness. It must not reveal or request hidden chain-of-thought or private reasoning transcripts. It must not change the Human objective, grant permission, resolve a protected gate, override evidence or safety, or act as an executable instruction or machine authorization token.

In particular, independent expression and execution recommendations cannot route engines, adjudicate a protected dispute, approve or publish source/master, activate runtime or Coordinator, handle secrets, or authorize destructive work. Those powers remain with the Human Speaker under the existing authority and gate rules.

```text
independent expression != factual evidence
independent expression != Human authorization
independent expression != hidden chain-of-thought
independent expression != mandatory positivity
```

The requirement is waived when the Human explicitly requests pointer-only or no-extra-text output, or when a higher-priority safety or format rule forbids extra prose.

### Agent-Specific Preservation

When ChatGPT or Claude asks the Human to start or continue a Codex or Claude Code task, the Human-facing response contains: (1) the compact canonical pointer, (2) a compact execution recommendation with every required field, and (3) two to five sentences of bounded independent expression. When reviewing or completing material work without dispatching a backend agent, the execution recommendation is not required, but bounded independent expression remains required.

For a material Codex or Claude Code completion, review handoff, publication, blocked state, conflict, or Human gate, the Human Brief contains a clearly separated `Independent expression` section of two to five sentences. The direct Human-visible response may append the same bounded expression after the canonical handoff block when the interface permits prose. In a strict machine-only channel, the canonical handoff remains pointer-only and `brief_ref` preserves the expression in the durable Human Brief.

### Human-Response Preflight And Drift Correction

```yaml
human_response_preflight:
  factual_status_grounded: true
  required_refs_dereferenced: true
  canonical_pointer_present_when_applicable: true
  execution_recommendation_present_when_dispatching: true
  independent_expression_present_for_material_event: true
  independent_expression_separated_from_authority: true
  no_long_task_or_report_echo: true
  no_hidden_chain_of_thought_request_or_disclosure: true
```

If a reviewing model detects an omission, it acknowledges protocol drift plainly and corrects the Human-facing response in the same turn when possible. It does not blame context length or the Human, create a fake cleanup/finalize microtask solely for the omitted chat section, or discard otherwise valid repository work. If the durable source protocol itself lacks the rule, one coherent reviewed protocol-correction task may repair the stack.

### Executable Repository Compliance Gate

Material `C1` and protected `C2` workflow artifacts are validated by `.ai/communication_compliance/validate_communication.py` under the versioned policy and schemas in that directory. Ordinary `C0` discussion is not required to produce a durable artifact. Unknown event types fail closed and cannot self-declare as `C0`.

A proposed C1/C2 transition is ineligible until the gate resolves an immutable event artifact, an immutable actual-STATE snapshot, and—when a machine is addressed—the physical ordered pointer artifact. A separately injected trusted `ActiveStateContext` must bind STATE to the currently observed `ai/review/latest` head; immutable old STATE alone is replayable and therefore insufficient. The gate reruns event validation from those bytes, including every receipt file and required ref. A durable validation artifact is optional comparison evidence only and must be byte-for-byte and semantically identical to the fresh canonical result. Supplied `pass`, digest, resolved-status, and transition claims never authenticate themselves.

Human remains `human_speaker`. A direct Human backend dispatch uses the frozen `chatgpt_to_codex_v1` communication direction without claiming a foreground model role. Every state-changing Human or model event needs a separately injected authenticated `ActorOriginContext` bound to the exact event digest, provider, stable role, task, event, transition, and release head; every edge also enforces its provider-neutral `allowed_actor_roles`. For `C2`, descriptive `human_gate` text and actor origin are still not authority: an independently injected, action-bound `AuthorizationContext` from a trusted Human host is also required and binds the exact event plus actor-origin context digest. Validation provenance, actor origin, current-state evidence, and protected authority are separate boundaries; none grants or substitutes for another, and the validator never executes authorization.

The current gate is repository-level enforcement, not live UI or model-output interception. Communication Gateway, middleware, polling, Coordinator, runtime, or unattended activation remains a separate Human-gated implementation. Its release contract separates the neutral `source_mailbox_base_head` from the immutable `protocol_release_head` and uses a semantics commit followed by one binding-only child. Drift ledger v2 resolves an immutable prior ledger, preserves the exact record prefix and hash chain, and binds recurring deterministic evidence to an immutable suite blob, unique negative case, and case digest; mutable `path#case` evidence is forbidden.

## Canonical Instruction Authority And State Freshness

Instruction authority and current-state freshness are separate systems. Fresh evidence can establish what state exists; it does not grant permission to mutate, publish, merge, activate, or override a durable rule.

### Instruction Authority Order

Apply instruction authority in this order:

1. platform, system, developer, and safety instructions;
2. current explicit Human instruction;
3. authenticated current Human-approved task-specific permission or override;
4. Plan 3 constitution and the Cybernetic Citizen runtime contract;
5. durable repository control protocols;
6. relevant domain-authority protocols;
7. ordinary current signal and task operational details;
8. routing documents and historical evidence.

An authenticated Human-approved task-specific override may outrank a durable repository protocol only for its explicit scope. An ordinary model-generated signal, packet, task, or report remains operational detail at level 7 and gains no override authority merely by being current. No repository artifact overrides platform safety or a current explicit Human instruction. Plan 3 Human Speaker gates remain required for protected publication, major mathematics, runtime or Coordinator activation, secrets, destructive Git, and objective-changing actions.

### State Freshness Order

Resolve current state in this order:

1. current explicit Human statement;
2. physical Git branch/HEAD and immutable source-head evidence;
3. validated active review mailbox and every required dereferenced ref;
4. published source baseline;
5. routing snapshots;
6. historical reports and legacy branches.

Freshness establishes current state only. Git HEAD, mailbox recency, timestamps, and report age are evidence, not independent authorization. Report stale state evidence explicitly. Report an authority conflict separately from a freshness conflict.

## Roles

### Backend execution and handoff (`Codex` wire role; compatible occupants: Codex, Claude Code)

- Performs approved local edits and tests.
- Creates business commits on the source branch.
- After lane cutover, appends only to its own lane and does not write canonical
  `STATE.yml`, latest `.ai/HUMAN_BRIEF.md`, or legacy shared `OUTBOX.md`.
- Returns a short pointer handoff instead of pasting execution reports into chat.
- Writes an immutable `.ai/HUMAN_BRIEFS/<task-id>/<lane-instance-id>-<message-seq>.md` for material completions,
  review handoffs, publication, blocked/conflict states, risks, or Human gates,
  including bounded independent expression.
- Publishes disposable review snapshots when authorized by this protocol.
- Does not push the source branch without explicit human approval.

### Foreground review and task dispatch (`ChatGPT` wire role; compatible occupants: ChatGPT, Claude)

- Reads the exact paths and commit range declared by the current signal or handoff.
- Performs review, writes long tasks to approved GitHub paths, and sends only a short pointer signal.
- Writes or updates a Human-facing brief for material Human-facing events and applies the complete Human operational response contract.
- May write back only to approved `.ai` communication paths.
- Solely owns canonical `.ai/STATE.yml` reduction and the latest
  `.ai/HUMAN_BRIEF.md` pointer/summary surface.
- Must not write business files.

### Human Speaker (`Human`; sole compatible occupant)

- Reads short summaries or GitHub brief files, asks questions, and resolves approval gates.
- Retains final authority over source-branch publication, merge, destructive Git, secrets, major architecture or mathematics decisions, and broad regeneration.

## Mailbox Files

- `PROTOCOL.md`: stable handoff rules.
- `HANDOFF_INIT_PROMPT.md`: session bootstrap prompt for context boundaries.
- `PROTOCOL_ADHERENCE.md`: bootstrap, compliance, and correction rules for independent model instances.
- `HANDOFF_COMMON_CONVENTIONS.md`: shared default rules inherited by all packets.
- `CODEX_WORK_MECHANISM_PROTOCOL.md`: canonical backend execution-role workflow mechanics under the historical Codex namespace.
- `CODEX_TASK_INPUT_CONTRACT.md`: canonical task signal and long-packet input requirements.
- `STATE.yml`: current machine-readable handoff state.
- `INBOX.md`: optional pointer/index for the current signal, packet, task, or brief.
- `OUTBOX.md`: source-neutral mailbox and legacy read-only backend compatibility input after lane cutover.
- `DECISIONS.md`: compact long-lived handoff decisions, not a turn log.
- `HUMAN_BRIEF.md`: latest human-facing brief.
- `HUMAN_BRIEFS/*.md`: optional archive for significant human-facing briefs.
- `load_profiles/*.md`: routing-only initialization manifests.
- `lanes/`: cooperative per-instance append layout, schema, reducer, and durable lane events.

The source branch stores the stable protocol and neutral mailbox baseline. Active per-turn state is published on `ai/review/latest` and must not be merged back into the source branch.

## Cooperative Lane Epoch And Migration

`lane_required_after_protocol_release_head` is the bound value in
`.ai/lanes/lane_epoch.yml` for the release that introduces this section. From that
one-way epoch onward, backend durable
receipts use `.ai/lanes/<lane_instance_id>/events/`; legacy shared `.ai/OUTBOX.md` is
read-only compatibility input. Cutover is atomic: no event is dual-written and one
task may not mix legacy and lane delivery. Either condition fails closed.

The epoch may be bound and published only when no backend task is in flight and every
old backend session has completed or stopped. After publication, every environment
must reload the protocol before its next durable write; otherwise cutover is blocked.

The lane envelope is an independent artifact conforming to
`.ai/lanes/lane_envelope.schema.json` and appears in the communication event's
`required_refs`, never inside the frozen seven-field pointer. The event carries the
role-appropriate seven-field signal or handoff. Its role and environment fields are
descriptive and grant no authority. `lane_protocol_epoch` must equal the bound current
epoch; `base_review_head` is the review head observed before writing and is not a
self-reference. Each lane appends only its own events; cross-lane writes are rejected
under the cooperative threat model.

Foreground deterministically takes the greatest sequence per lane, sorts by lane ID
and sequence, ignores events with a different `lane_protocol_epoch`, and writes
optional `lane_inputs` provenance to canonical STATE. Each input carries immutable
event/envelope commit, path, and SHA-256 evidence. Lane tests validate this routing and
traceability; the existing communication gate, policy semantics, validator, fixtures,
canonical event, pointer, and STATE transition rules receive no lane behavior. This
adds no transition authorization, CAS, ActorOrigin binding, formal proof, scheduler,
polling, Gateway, or runtime. Source/master neutral mailbox rules remain unchanged.

## Durable Protocol And Active Mailbox Separation

Durable protocol files define behavior and may be carried by the source branch. Active mailbox files describe one current exchange and are safe to reset to neutral baseline on source publication.

Durable protocol files include:

- `.ai/PROTOCOL.md`
- `.ai/PROTOCOL_ADHERENCE.md`
- `.ai/HANDOFF_INIT_PROMPT.md`
- `.ai/HANDOFF_COMMON_CONVENTIONS.md`
- `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`
- `.ai/DECISIONS.md`
- `.ai/load_profiles/*.md`
- `.ai/lanes/index.md`
- `.ai/lanes/lane_envelope.schema.json`
- `.ai/lanes/lane_meta.schema.json`
- `.ai/lanes/lane_epoch.yml`
- `.ai/lanes/reduce-lanes.ps1`

Active mailbox files include:

- `.ai/INBOX.md`
- `.ai/OUTBOX.md`
- `.ai/HUMAN_BRIEF.md`
- `.ai/STATE.yml`

On final master or another published source baseline, the active mailbox files should be neutral unless a current Human-approved task explicitly says otherwise. Live handoff state belongs on `ai/review/latest` or a task-specific review branch. Do not infer an active task from source-branch mailbox state when it is marked `neutral_baseline`.

### Source Publication Mailbox Neutralization Gate

Before a work branch is published to a durable source branch or `master`, its source-side mailbox must be neutralized. Active task snapshots must not be merged into the published source baseline.

Required source publication checks:

- `.ai/INBOX.md` parses and declares `intent: neutral_baseline`, with no active signal/task/packet pointer;
- `.ai/STATE.yml` parses and declares `status: neutral_baseline`, with no active packet ID, task ID, work branch, report ref, or pending Human gate;
- `.ai/OUTBOX.md` parses and declares `status: neutral_baseline`, with no active packet/report/branch fields;
- `.ai/HUMAN_BRIEF.md` is a short neutral notice and does not describe an active or pending task;
- post-publication read-back confirms those four neutral source artifacts at the published source HEAD.

If any source mailbox file contains an active `packet_id`, task identity, work branch, report pointer, or pending Human gate, source publication is blocked until the source mailbox is neutralized. Active handoff state remains on `ai/review/latest`; neutralizing source does not delete durable `.ai/CODEX_REPORTS/` evidence.

## Pointer-Based Message Format

The `ChatGPT-to-Codex` and `Codex-to-ChatGPT` names below are frozen wire-contract labels. Compatible foreground and backend occupants use the corresponding schema without renaming, adding, deleting, or reordering keys.

ChatGPT-to-Codex signals contain these seven required fields:

- `signal_id`
- `decision`
- `task_ref`
- `packet_ref`
- `brief_ref`
- `source_head`
- `human_gate`

Long task content lives in `.ai/TASKS/*.md` or `.ai/USER_UPLOADS/*.md`; it is never pasted into the short signal. `brief_ref` points to the human-facing brief when one exists, usually `.ai/HUMAN_BRIEF.md`; otherwise it may be `null`.

Future foreground-role/Human-authored long task packets follow `.ai/CODEX_TASK_INPUT_CONTRACT.md`. That contract defines required packet fields, risk-triggered task modules, evidence and output refs, validation, stop rules, and missing-input behavior.

Codex-to-ChatGPT handoffs contain these seven required core fields:

- `packet_id`
- `status`
- `report_ref`
- `brief_ref`
- `source_head`
- `review_branch_head`
- `human_gate`

`detail_ref` is an optional eighth field. Include it when a separate long backend-role report, plan, analysis, or execution detail exists; omit it when `report_ref` is sufficient. Backend-role-generated long details live under the historical `.ai/CODEX_REPORTS/*.md` namespace unless the task names another approved backend-owned path.

Detailed execution reports live in `.ai/CODEX_REPORTS/*.md`; legacy `.ai/OUTBOX.md` is read-only after lane cutover. IDs prevent duplicate consumption, source heads bind messages to business state, reference fields identify the durable content to read, and `brief_ref` points to the immutable per-task Human Brief.

A source-branch baseline may use `review_branch_head: null`. An active committed review artifact uses `review_branch_head: "self"` because a commit cannot embed its own SHA; the post-publication short handoff resolves it to the actual remote SHA.

## Pointer Dereference Obligation

Reading a short pointer message is not enough to complete a handoff. The receiver must follow every non-null reference needed by the message intent before deciding to execute, acknowledge, block, or wait.

For ChatGPT-to-Codex wire signals, including signals authored by a compatible Claude foreground occupant:

- If `task_ref` is non-null, the backend-role receiver must read that task template.
- If `packet_ref` is non-null, the backend-role receiver must read that uploaded packet or long task body.
- If `brief_ref` is non-null, the backend-role receiver should read or update the Human Brief when the task affects Human-facing status.
- If both `task_ref` and `packet_ref` are null, there is no long task body; the backend-role receiver should act directly on `decision`, such as acknowledge a protocol update, accept approval, report blocked, or request clarification.

For Codex-to-ChatGPT wire handoffs, including handoffs authored by a compatible Claude Code backend occupant:

- If `report_ref` is non-null, the foreground-role receiver must read it before review.
- If `brief_ref` is non-null, the foreground-role receiver should read it before producing or updating a Human-facing summary.
- If optional `detail_ref` is non-null, the foreground-role receiver must read it before completing review.

An optional index such as `.ai/INBOX.md` may include additional pointers such as `current_signal` or `init_ref`. If those fields are non-null, the receiver must read them before continuing. The receiver must not stop after reading only `INBOX.md` or only the short signal when a non-null `packet_ref`, `task_ref`, or `report_ref` exists. If a referenced file is missing, stale, malformed, or contradictory, stop and return a short blocked handoff instead of guessing.

### Writer-Side Publish Order

The sender publishes durable referenced content before publishing its pointer:

1. publish the `packet_ref`, `task_ref`, `report_ref`, or `brief_ref` artifact;
2. verify that the referenced path exists at the intended review-branch head;
3. publish the short signal or handoff;
4. update optional `.ai/INBOX.md` last.

### Missing-Reference Fast Fail

When a required non-null ref is absent, check that exact ref once at the current review-branch head and immediately return `blocked`. Do not infer work from the filename, audit unrelated files, or read `HUMAN_BRIEF.md` before the required task/report ref exists. Retry only after the remote review head changes or a new signal is published. A missing ref is invalid protocol input and does not consume the execution repair budget.

```yaml
packet_id: "codex-<id>"
status: "blocked"
missing_ref: "ai/review/latest:<path>"
review_branch_head: "<observed-head>"
required_action: "publish_packet_ref"
```

## Human Brief Channel

Human-facing summary text lives in GitHub by default.

- Latest brief: `.ai/HUMAN_BRIEF.md`
- Optional archive: `.ai/HUMAN_BRIEFS/*.md`

Normal non-material briefs are 3 to 5 lines and state only what changed, result, problem status, next step, and whether Human action is required. For a material event, the brief also includes a clearly separated `Independent expression` section of 2 to 5 sentences; this section is outside factual status and authority fields and may make the brief longer than 5 lines.

Detailed briefs are reserved for conflict, blocked state, retry exhaustion, permission escalation, source-branch publication, major phase transition, safety/privacy risk, model disagreement, or stage completion.

Model-to-model chat should carry `brief_ref`, not paste the full brief. If the human explicitly asks for the brief in chat, keep it short unless an interrupt condition applies.

## Handoff Initialization

Load `.ai/HANDOFF_INIT_PROMPT.md` only at a context boundary, not before every review iteration.

Context boundaries include:

- new compatible foreground/backend model thread, including ChatGPT, Claude, Codex, or Claude Code;
- new backend execution-role current-thread session, whether occupied by Codex or Claude Code;
- context reset or context uncertainty;
- protocol file changed;
- malformed, stale, or contradictory pointer message;
- automation or cron/subagent entry point, if automation is later enabled.

During a continuous review loop in the same active context, use the fast path: read `.ai/STATE.yml`, `.ai/INBOX.md` if needed, and only the pointer files referenced by the latest signal or handoff. Do not reread the whole protocol stack every turn.

If a referenced file is missing, stale, malformed, or contradictory, the agent must stop and return a short blocked handoff instead of guessing.

## Context Limits

- Do not paste task bodies, execution reports, full diffs, command logs, large files, tokens, private keys, `.env` contents, or long human briefs into model-to-model chat.
- Short messages contain only the canonical signal or handoff fields and should normally remain below approximately 300 tokens.
- Put durable detail in a GitHub artifact and reference its exact path and commit.
- Keep human-facing chat minimal; prefer `brief_ref`.
- Every non-null ref must still be dereferenced. Token limits govern how evidence is read, not whether required evidence is read.
- For large files, prefer `rg`, headings, summaries, and targeted line ranges. Do not load multiple large evidence files with a single `Get-Content -Raw` operation.
- Keep legacy `OUTBOX.md` read-only after lane cutover and place detailed execution logs in `.ai/CODEX_REPORTS/*.md`.

The canonical context budget is inherited from `.ai/HANDOFF_COMMON_CONVENTIONS.md`. Similar planning tasks should target approximately 12k to 18k visible tokens. Full protocol initialization is required only at a context boundary or when the protocol head changes; otherwise use the fast path.

For recurring evidence sources, target the relevant sections first:

- Sample Pack: Issues Summary, Sample Records, and conclusion or recommendation.
- Evaluator: status constants, `evaluate_yaml_content()`, and bulk summary.
- `BRIDGE_SCHEMA.md`: endpoint, mode, validation, and Coordinator-consumption sections.

Quiet Git/worktree output is preferred. If a first read is truncated, reread only the missing targeted section. Generated documents should be complete on disk without echoing their entire body into tool output or chat.

```yaml
targeted_search_policy:
  first_pass: "rg -n without context"
  context_lines: "only for selected matches"
  max_match_output: "80_lines"
  duplicate_match_blocks: "forbidden"

successful_path_output_policy:
  packet_body_echo: "forbidden"
  human_brief_echo: "forbidden"
  command_output: "summary_only"
  grep_output: "file_and_line_only_first"
  validation_output: "consolidated_summary_only"
  expand_logs_only_on_failure: true

progress_narration_policy:
  default: "forbidden"
  allowed_only_when:
    - "blocked"
    - "conflict"
    - "permission_needed"
    - "destructive_risk"
    - "human_gate_required"
```

These are successful-path defaults. Higher-priority instructions may still require concise progress updates or pre-edit notice, and correctness always takes precedence over output reduction.

## Human-Facing Execution Recommendation

When ChatGPT or Claude asks the Human to start or continue a Codex or Claude Code task, the Human-facing response must include a compact execution recommendation with `recommended_model`, `recommended_thinking_level`, `mode`, `subagents`, `task_ref_or_plan_ref` resolving to exactly one applicable durable ref, `short_complexity_rationale`, and `human_gate`. Use `runtime_dependent` or `not_applicable` for an unavailable field instead of omitting it. Include local-file or plugin/app requirements only when they are genuinely needed.

The recommendation is required in the Human operational dispatch, but it is normally not a required field inside the Human Brief and is never a field inside the canonical machine pointer. The narrow exception is a non-separable mixed-recipient fallback where `brief_ref` is the sole Human-content carrier; then the referenced Brief must preserve the complete recommendation. It does not authorize execution or cross a stage gate; a valid signal and the applicable Human authority are still required.

## Git Rules

- The source branch contains business history and the one-time protocol bootstrap.
- Pushing the source branch requires explicit human approval.
- `ai/review/latest` is a disposable review snapshot and must not be merged into a source branch.
- Business commits and per-turn handoff commits remain separate.
- Use explicit paths for staging; do not use `git add .`.
- Do not use destructive Git operations without explicit human approval.

### Local-First Handoff Workflow

Default to local file work and one consolidated commit. Do not perform defensive remote checks unless a push fails, a required ref is missing, a Human gate is triggered, or an actual conflict is detected.

For a normal successful task, read the current signal and all required refs once, edit locally, run consolidated task-level validation, create one source commit when needed, publish one review handoff when needed, and return the canonical short handoff. Do not repeatedly poll remote heads or repeat status/diff/scope checks without new evidence.

Final review publication still uses fast-forward or expected-SHA lease protection. If the review branch advanced and publication fails, fetch the new head and inspect only overlapping files. Retry safely when there is no overlap; return `blocked` or `conflict` when overlap or ownership is uncertain. Source-branch push remains Human-gated.

### Phase 1: Backend-role-only review publication (`Codex-only` historical label)

Only the separately authorized backend execution-and-handoff occupant writes to `ai/review/latest`. Compatibility alone still grants nothing; the authorization is separate and recorded below.

**Standing Human authorization, 2026-07-26.** Claude Code is authorized to write to `ai/review/latest` as a backend execution-and-handoff occupant, on the same terms as Codex. This resolves a gap found by a cold-start audit: the earlier wording named Codex as "the currently verified implementation", which a fresh reader correctly read as a closed door, leaving the role's only delivery channel unusable by one of its two compatible occupants.

**Delegation default.** Authorization is not an instruction to use it. Where another occupant can produce the same result, dispatch the write to that occupant; a Claude context is the more expensive one to spend. Claude Code performs the write itself when the task is unusually error-prone, when a mistake would be expensive to undo, or when the Human names it. This is an economic default, not a permission boundary — it never widens what any occupant may do.

Every protected action remains gated regardless of this authorization: source-branch push, history rewriting, repository deletion or visibility change, runtime or scheduler activation, and secrets are unchanged and still require Human authority at the time of the action.

Publication may use:

```powershell
git push origin HEAD:ai/review/latest --force-with-lease
```

### Phase 2: Restricted ChatGPT writeback

ChatGPT communication writeback has been tested and human-approved for `.ai` communication paths only. It must not write business files. Codex must use an explicit expected-SHA lease or equivalent compare-and-swap check before updating the review branch so that an unconsumed ChatGPT write cannot be overwritten.

## Autonomous Handoff Communication v0.1

- The current communication mechanism is documented in `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`.
- Polling automation is deferred; the current mode is human-triggered GitHub communication.
- Model-to-model chat uses pointer-based messages rather than long prompts or reports.
- Long foreground-role tasks use `.ai/TASKS/*.md` or a Human-approved carrier under the historical `.ai/USER_UPLOADS/` namespace.
- Short foreground-role decisions use the historical `.ai/SIGNAL_CHATGPT_*.yml` namespace and the canonical pointer signal with `brief_ref`.
- Backend-role responses use the canonical pointer handoff with `brief_ref`, point to `.ai/CODEX_REPORTS/*.md`, and publish through their instance lane after cutover.
- `.ai/INBOX.md` may serve as an index or pointer and is not the only long-packet carrier.
- Human-facing summaries should be read through `.ai/HUMAN_BRIEF.md` or `.ai/HUMAN_BRIEFS/*.md`.

## Human Gates

Explicit human approval is required for:

- pushing a source branch;
- merging or rebasing protected branches;
- destructive Git operations;
- handling secrets, credentials, permissions, or private keys;
- broad node or domain regeneration;
- major mathematical, architectural, or validation-policy decisions;
- expanding this protocol beyond the handoff scope.

Compatible foreground and backend occupants must not claim that a Human gate is approved without evidence from a current Human instruction or an authenticated approval channel.

## Long-Run Task Defaults

Human-authorized long-run programs inherit `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`.

By default, long-run execution is completion-preserving: discovered cleanup, validation, alignment, report, and repair steps are folded into the original authorized task when they are necessary for completion and remain within scope. Internal checkpoints replace repeated small Human gates.

Human escalation is required only when a discovered item requires new authority, changes the objective, touches forbidden paths, requires destructive Git, requires source or master push, creates security, privacy, or secrets risk, requests Coordinator or runtime activation, or blocks all safe independent progress.

This rule is an execution-efficiency rule. It does not authorize P3, bridge generation, source publication, master merge, runtime activation, secrets access, broad regeneration, or unrelated business changes.

## City-State OS Alignment

The `.ai` handoff layer is the communication and review layer for compatible foreground/backend model occupants and the Human Speaker. It should align with the broader Cybernetic City-State OS structure without silently becoming runtime governance.

- `.ai/CODEX_REPORTS/*.md` stores model-to-model review evidence.
- `campaigns/campaign_manifest_template.yaml` remains the template for future campaign state when a task explicitly opens a campaign.
- `system_backbone/audit_ledger/system_record.jsonl` remains the audit-ledger substrate; this protocol does not authorize ledger writes by itself.
- `02_Protocols/` contains broader OS protocol doctrine. `.ai` files provide executable handoff mechanics.

Runtime integration, Coordinator activation, automatic routing, and repository-level AI control-plane changes require separate Human-approved tasks.

## Failure Handling

- Reject stale packets whose `source_head` does not match the intended business commit.
- Do not process a consumed `packet_id` twice.
- Stop on an unexpected sender, recipient, file scope, or unrelated worktree change.
- If a review push lease fails, fetch and inspect the remote state before retrying.
- If a packet is malformed, report the missing field instead of inferring it.
- If GitHub is unavailable, retain the local handoff and provide only a short human summary.
- If sensitive content is detected, stop before commit or push.

## Deferred Evolution

Automatic validation, multi-agent conflict handling, mandatory ChatGPT writeback, packet replay protection, repository-level governance, automated human brief delivery, and full Cybernetic City-State OS communication/control-layer activation are deferred unless a current Human-approved task opens that scope. Their roadmap is recorded in the post-P2 execution memory and P10+ protocol evolution reports.
