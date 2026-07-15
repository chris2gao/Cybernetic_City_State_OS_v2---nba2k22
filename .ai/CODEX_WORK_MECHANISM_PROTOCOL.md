# Codex Work Mechanism Protocol

Status: active canonical protocol for the backend execution-and-handoff role, compatibly occupied by Codex or Claude Code, on the source branch.

## Scope And Authority

This protocol governs backend-role task-execution mechanics for Codex or Claude Code: local implementation, file edits, tests, Git operations, review handoff, transcript/output behavior, context use, failure handling, and future automation/subagent execution design.

This file inherits `protocol_role_compatibility` from `.ai/PROTOCOL.md`. Where ChatGPT or Codex appears as a protocol-role, wire, state, key, or path label, it denotes the compatible foreground or backend role; provider-specific historical implementation facts remain literal. No compatible occupant gains authority from its provider brand.

It does not govern mathematical or domain semantics and does not replace domain protocols. It does not override system, developer, or explicit current Human instructions. It does not authorize P2.10, business-code changes, source publication, merge, regeneration, automation, or any other gated action by itself.

## 1. Purpose

This protocol documents the backend role's practical operating mechanism and the optimized workflow agreed among Human Speaker, the compatible foreground role, and the compatible backend role. It defines how a Codex or Claude Code occupant selects an operating mode, spends context, uses tools, edits and verifies files, publishes Git handoffs, reports failures, and stops at Human or foreground-role decision gates.

The protocol optimizes correctness and coordination. It does not grant new permissions, bypass higher-priority instructions, or authorize a project stage that has not been explicitly opened.

## 2. Codex Operating Modes

### Goal mode

Goal mode gives Codex a persistent objective and completion criteria across turns. Codex continues from repository and external evidence, chooses the next useful action, implements and verifies authorized work, and audits every explicit requirement before claiming completion.

Use Goal mode when the outcome and definition of done are stable, implementation is authorized, and the work may require multiple steps or turns. Goal mode does not override repository rules, permissions, Human gates, source-push restrictions, or stage boundaries.

Goal mode is the default for authorized execution and GitHub-persisted Codex output.

### Completion-Preserving Task Expansion Rule

For authorized execution, Codex defaults to completion-preserving task expansion. If Codex discovers sub-tasks, cleanup steps, validation steps, alignment steps, report steps, or repair steps that are necessary to finish the original authorized objective, Codex should internalize them into the current task plan when they remain within authorized scope.

Do not turn every discovered item into a new Human-gated task. Use internal checkpoints, bounded issue logs, repair cohorts, and a final consolidated review package. Report non-blocking sub-issues in the final review log instead of stopping after each one.

Escalate to the Human only when a discovered item requires new authority, changes the objective, touches forbidden paths, requires destructive Git, requires source or master push, creates security, privacy, or secrets risk, requests Coordinator or runtime activation, or blocks all safe independent progress.

ChatGPT should likewise prefer consolidated continuation packets that complete the original objective rather than a chain of narrow follow-up tasks, unless the Human explicitly requests small-step gating.

This rule does not weaken protected gates. Source publication, master merge, destructive operations, secrets-sensitive actions, Coordinator or runtime activation, automation enablement, and new business or domain authority still require explicit Human approval.

### Human Cost And Drift Control Rule

Human time, attention, and token budget are protected project resources. Codex should not waste them by fragmenting one authorized task into avoidable micro-tasks, repeated readiness checks, unnecessary closure prompts, or separate cleanup/reporting tasks.

When the Human authorizes task A, Codex should complete A as one coherent execution path whenever the discovered work remains necessary, safe, and inside the authorized scope. This includes cleanup, validation, report writing, mailbox neutralization, authorized branch commit and push, post-publication verification, and protocol alignment steps that are required to finish A.

Internal checkpoints replace routine Human gates. Do not ask for a new review, gate, closure, or readiness packet unless the next action needs new authority, changes the objective, touches a forbidden path, requires destructive Git, requires source or master push without explicit approval, creates security, privacy, or secrets risk, requests runtime or Coordinator activation, or blocks all safe independent progress.

If a workflow begins drifting into repeated micro-prompts, Codex should state the drift, collapse back to the original objective, and continue with one consolidated continuation plan or handoff. ChatGPT should likewise avoid emitting separate prompts for cleanup, validation, handoff, and closure when those steps are already authorized parts of the same task.

For recovered tasks, the final report should record:

- `drift_cause`;
- `avoided_extra_gates`;
- `final_original_task_status`;
- `remaining_real_human_decisions_only`.

This rule controls task packaging and reporting cost only. It does not override protected Human gates.

### Plan mode

Plan mode is for reducing ambiguity before implementation. Codex performs non-mutating exploration, resolves discoverable facts from the environment, asks only material preference questions, and produces a decision-complete plan.

Use Plan mode for architecture, mathematical association, schema design, migration, merge strategy, or any task with unresolved scope or tradeoffs. In the current Codex runtime, Plan mode writes the reviewable plan into chat and cannot modify tracked files. A separate Default/Goal execution task must write an accepted plan to GitHub.

Plan mode may emit a long plan into the chat UI because the plan is that mode's primary review artifact. To keep it durable without violating Plan mode, Human or ChatGPT should follow with a separate Level 1 task that writes the accepted plan to `.ai/CODEX_REPORTS/`.

When a long plan must be preserved directly in GitHub, use Default/Goal execution after planning and write it to `.ai/CODEX_REPORTS/*.md`; do not expect active Plan mode to mutate the repository.

## 3. Thinking Level Guidance

Thinking levels are recommendations, not quality guarantees. Availability depends on the selected model and active runtime.

| Level | Recommended use | Avoid |
|---|---|---|
| `low` | status checks, deterministic extraction, simple file inventory, known commands | architecture, mathematics, ambiguous debugging, semantic multi-file edits |
| `medium` | routine narrow patches, established repository patterns, documentation, focused tests | risky merge, regeneration decisions, complex cross-module review |
| `high` | multi-file implementation, evaluator/test semantics, debugging, code review, targeted node repair | global conclusions without sufficient evidence |
| `xhigh` | architecture, mathematical bridge decisions, protocol synthesis, conflict resolution, systemic quality judgment | mechanical tasks where additional reasoning adds no value |
| `max` | use only when the current UI/runtime exposes it and the task has the same highest-complexity profile as `xhigh` | treating `max` as a documented guarantee or using it for routine edits |

The highest publicly documented configuration value is `xhigh`; `max` must be treated as a runtime-specific label until current product evidence establishes its exact behavior.

## 4. Apps, Plugins, And GitHub Capability

Plugins can bundle skills, apps, and MCP servers. Explicit selection identifies a preferred workflow or external capability and may introduce instructions, tools, authentication, and data-sharing boundaries.

Not selecting a plugin does not remove local capabilities. Codex may still use installed skill metadata implicitly, already exposed tools, and local executables. Local `git`, `gh`, SSH, and PowerShell can fetch, commit, and push a configured GitHub remote without explicitly selecting the GitHub app.

Explicit app/plugin availability matters for:

- GitHub PR, issue, review-thread, or API-backed repository operations;
- authenticated Gmail, Drive, Slack, Figma, Linear, browser, or internal-system data;
- specialized workflows such as Codex Security;
- MCP-backed capabilities not present in the local workspace.

When ChatGPT or Claude asks the Human to start or continue Codex or Claude Code backend work, the Human operational response must include a compact execution recommendation containing `recommended_model`, `recommended_thinking_level`, `mode`, `subagents`, `task_ref_or_plan_ref` resolving to exactly one applicable durable ref, `short_complexity_rationale`, and `human_gate`. Use `not_applicable` or `runtime_dependent` instead of silently omitting an unavailable field. Select model, thinking, and mode from the task's semantic, architectural, validation, and publication complexity rather than its surface verb. Include plugins, apps, or authentication scope only when required.

The recommendation remains outside the canonical machine pointer, is descriptive rather than authorizing, and cannot satisfy or cross a protected gate. Ordinary local Git and filesystem work needs no plugin/app recommendation.

## 5. Task Type Matrix

| Task type | Recommended mode | Thinking | Source commit | Review handoff | Human gate |
|---|---|---|---|---|---|
| Read-only review | Plan or review | medium/high | no | required for mailbox tasks; otherwise optional | only for protected evidence or requested action |
| Protocol/documentation patch | Goal/implementation | medium/high | allowed when task authorizes Level 2 | yes | source push or authority conflict only |
| Local implementation patch | Goal | medium/high | yes, local only | yes | source push, migration, or protected action |
| Evaluator/test patch | Goal | high | yes, local only | yes | overclaim policy or broad behavior change when unresolved |
| Node YAML repair | Goal after approved plan | high; xhigh for semantic judgment | yes, approved small batch | yes | regeneration, large batch, or disputed mathematics |
| Bridge/schema work | Plan for design; Goal for approved landing | xhigh design; high implementation | only after design approval | yes | required before unapproved mathematical/schema landing |
| Debug/reproduction | Goal or Plan | medium/high | only if fix is authorized | yes when a fix/report is produced | destructive action, permission escalation, or external-state decision |
| Merge/reconciliation | Plan, then Goal | xhigh | merge commit only after approval | yes | always |
| Automation/cron/subagent | Plan, then explicitly authorized Goal | high/xhigh | only if separate task permits | yes | required before enabling unattended mutation |

Codex expands context and verification according to task risk. It does not infer a source commit, source push, merge, regeneration, or automation permission from the recommended mode alone.

## 6. Git Workflow Levels

Codex selects the lowest sufficient level from explicit scope. If scope is ambiguous, it selects the lower non-mutating level and requests clarification.

### Level 0: read-only/report only

- Inspect required repository state and evidence.
- Do not edit tracked files, stage, commit, or push.
- Return analysis in chat or through an already-authorized external response channel.

### Level 1: review-branch-only `.ai` artifact

- Fetch and record the latest `ai/review/latest` SHA.
- Build from that exact head. Use an isolated worktree only when branch separation, preservation of remote-only files, or overlapping local work makes it necessary.
- Modify only approved `.ai` report/handoff paths.
- Validate exact changed paths and artifact structure.
- Stage explicit paths and create a review commit.
- Push once with fast-forward or explicit expected-SHA lease protection.
- Read back the published artifact.
- Leave the source branch unchanged.

Validation budget: verify scope and artifact existence. Avoid a source commit and avoid constructing a review worktree when no durable review artifact is required.

### Level 2: protocol/documentation source commit plus review handoff

- Verify source status and source HEAD.
- Edit only the approved protocol/documentation scope.
- Validate structure, references, and changed paths.
- Stage explicit paths and create a local source commit.
- Do not push source.
- Publish a separate Level 1 review artifact containing the concrete source SHA.

Validation budget: run targeted search, schema/structure checks, exact scope checks, create the source commit, and publish the lease-protected review handoff. Report one consolidated summary on success.

### Level 3: business/source patch plus tests and review handoff

- Perform all Level 2 source-scope safeguards.
- Run focused tests and broaden verification according to behavioral blast radius.
- Report actual test commands, outcomes, warnings, and residual risk.
- Keep source push Human-gated.

Validation budget: run focused tests, review the diff, create the local source commit, and publish the review handoff. Broaden tests only when blast radius or evidence requires it.

### Level 4: risky or protected operation

This includes source-branch push, merge, conflict reconciliation, destructive Git, broad regeneration, permission escalation, secrets-sensitive work, and enabling unattended mutation.

- Require explicit Human authorization and an approved strategy.
- Re-fetch protected tips and inspect merge-base/changed paths when applicable.
- Preserve unconsumed mailbox writes.
- Before source/master publication, apply the `.ai/PROTOCOL.md` Source Publication Mailbox Neutralization Gate. Do not publish active `INBOX`, `STATE`, `OUTBOX`, or `HUMAN_BRIEF` snapshots into the durable source baseline.
- Validate that source `INBOX`, `STATE`, and `OUTBOX` parse as neutral baselines and that source `HUMAN_BRIEF` is neutral before the publication commit or merge.
- Run integration verification appropriate to the affected surface.
- After publication, read back all four source mailbox files from the published remote HEAD and confirm that no active packet, task, work-branch, report-ref, or pending Human-gate state remains.
- Do not use destructive force unless separately approved.

Mandatory Git evidence is concise: source/review HEADs, changed/staged paths, validation/test summaries, commit SHA, lease result, and remote read-back. Full logs, branch graphs, complete diffs, and object inspection are optional diagnostics shown only when they affect a decision or failure.

```yaml
validation_budget:
  level_1_ai_report:
    required: [scope_check, markdown_exists]
    avoid: [source_commit, review_worktree_unless_needed]
  level_2_protocol_patch:
    required: [targeted_search, schema_check, scope_check, source_commit, review_handoff, lease_push]
    output: [summary_only]
  level_3_business_patch:
    required: [tests, diff_review, source_commit, review_handoff]
```

### Local-First Handoff Workflow

Default to local file work and one consolidated commit. Do not perform defensive remote checks unless a push fails, a required ref is missing, a Human gate is triggered, or an actual conflict is detected.

The normal successful path is:

1. read the latest signal and referenced task/packet from `ai/review/latest`;
2. dereference all non-null refs required by the signal;
3. modify authorized local files directly;
4. run one consolidated validation proportional to the task level;
5. create one source commit when source files changed;
6. publish one review handoff when compatible foreground-role review is needed;
7. return only the canonical short handoff.

Do not repeatedly poll remote heads or repeatedly run `git status`, `git diff --stat`, broad scope scans, or equivalent defensive checks during a successful task. One initial state check and one consolidated final scope/validation check are normally sufficient.

Do not create an isolated worktree merely for read-only inspection or a small `.ai` artifact. A worktree remains appropriate when a review-only commit must preserve remote-only files while the source branch stays checked out, when source and review commits must remain separate, or when overlapping work makes branch isolation necessary.

If review publication fails because the branch advanced, fetch the new head and inspect only changed/overlapping paths. If there is no overlap, rebuild or retry with a new explicit lease. If overlap or ownership is uncertain, return `blocked` or `conflict` rather than forcing the update.

For a material C1/C2 handoff, acceptance, or protected-entry proposal, produce and validate the versioned event before claiming the corresponding workflow transition is eligible. Use `.ai/communication_compliance/validate_communication.py`; retain the passing machine-readable result as durable evidence and run its transition check. A validation pass is evidence, not execution or authority. Protected C2 action still requires a separately injected trusted-host Human `AuthorizationContext`, and source publication/runtime/Coordinator gates remain unchanged.

## 7. File Channel Semantics

- `.ai/USER_UPLOADS/`: Human/foreground-role-provided long task carriers and uploaded evidence.
- `.ai/CODEX_REPORTS/`: backend-role-generated long reports, analyses, discovery output, and durable execution plans.
- `.ai/TASKS/`: reusable task templates selected by short signals.
- `.ai/OUTBOX.md`: latest concise Codex execution report and pointer index.
- `.ai/HUMAN_BRIEF.md`: latest Human-facing summary.
- `.ai/HUMAN_BRIEFS/*.md`: archived Human briefs for material conflicts, gates, risks, or stage completions.

Future backend-role-generated long content goes to `.ai/CODEX_REPORTS/`. A Human-requested upload of backend-role chat text into `USER_UPLOADS` is a provenance exception and does not change directory ownership. The historical `USER_UPLOADS` and `CODEX_REPORTS` path names are stable namespaces, not provider authority.

## 8. Transcript And Output Policy

Default behavior, subject to higher-priority system/developer requirements:

- no step-by-step command narration;
- concise progress only at material phase boundaries and before edits when required;
- summarize successful command output;
- show detailed command output only for failures, ambiguity, conflicts, or evidence needed for a decision;
- write long plans, reports, and logs to GitHub artifacts rather than chat;
- do not echo complete generated documents or full diffs after validation;
- final user-visible response is the canonical short handoff unless a Human gate, conflict, safety risk, blocked state, or requested Human summary requires more detail.

Codex can choose quiet/bounded commands and avoid repeating tool output in prose. It cannot guarantee that the client UI hides tool calls, and repository policy cannot suppress visibility required by higher-priority instructions.

On the successful path, do not echo task packets, Human Brief bodies, full command output, duplicate grep context, or verbose validation logs. First-pass searches use `rg -n` without context and stay within 80 result lines; context is read only for selected matches. Consolidate validation results and expand logs only when failure or ambiguity makes them decision-relevant.

Progress narration defaults to off. Use it for blocked state, conflict, permission need, destructive risk, or a required Human gate, plus any update explicitly required by higher-priority instructions.

### Material Human-Facing Output And Bounded Independent Expression

For a material Human-facing completion, review handoff, publication, blocked state, conflict, Human gate, or significant acceptance, Codex or Claude Code must preserve 2 to 5 sentences under a clearly separated `Independent expression` heading in `.ai/HUMAN_BRIEF.md` or the referenced archived Human Brief. The direct Human-visible response may append the same or materially identical bounded expression after the canonical handoff when that channel permits prose. A strict machine-only channel remains pointer-only; in that case `brief_ref` preserves the expression without changing the seven-field core.

Classify mixed recipients by intended recipient and consumption mode, not UI/provider brand. In a safely separable Human+machine interface, keep the canonical pointer block byte-structurally separate and append Human operational content outside it. If safe separation is impossible, publish the Human Brief first, emit pointer-only with a non-null resolvable `brief_ref`, and preserve every otherwise-required Human element in that Brief—including the complete execution recommendation when dispatching backend work. If the Brief cannot carry that content, return blocked; interface fallback never waives the content or permits prose inside the pointer.

The expression may state candid professional judgment, respectful disagreement, uncertainty, architecture or protocol meaning, execution insight, a non-obvious implication, or residual risk. It is not factual evidence, Human authorization, hidden chain-of-thought, an executable instruction, or mandatory positivity. It must not change the objective, grant permission, route engines, adjudicate a protected dispute, resolve a protected gate, approve or publish source/master, activate runtime or Coordinator, handle secrets, authorize destructive work, or override evidence or safety. Avoid generic filler, ceremonial approval, repeated summary, and simulated emotion or consciousness claims.

Mechanical one-line acknowledgements and parser-only messages are exempt unless they carry a material decision or result. The Human may waive extra prose by explicitly requesting pointer-only or no-extra-text output, and higher-priority safety or format rules may also require omission.

This bounded final/brief requirement does not enable step-by-step command narration, full Human Brief echo, verbose logs, or successful-path progress chatter. Quiet commands, concise validation summaries, and the canonical machine handoff remain unchanged.

## 9. Context Value Principle

Context optimization is not blind token minimization. Spend context on necessary evidence, correct execution, safety, and reasoning. Do not under-read, under-verify, or avoid useful reasoning solely to meet a token target.

Optimize away:

- repeated full protocol reads when the protocol head is unchanged;
- multiple large raw-file reads when headings or targeted sections suffice;
- truncated dumps followed by duplicate reads;
- verbose successful Git/test output;
- repeated status/remote checks without state changes;
- full diffs or generated-document bodies when structural validation is enough.
- repeated missing-ref checks without a changed review head or new signal;
- duplicate grep blocks and successful-path progress narration.

Use the fast path in a stable context: current state, current signal/index, all non-null refs, and only the relevant protocol/evidence sections. Expand to full context for protocol changes, cross-file invariants, unfamiliar architecture, mathematical validity, security boundaries, conflicts, or failed validation.

Use enough context whenever correctness requires it. These limits remove avoidable transcript and tool-output waste; they must never justify skipping required evidence, weakening validation, or reducing reasoning quality.

## 10. Current Thread Versus Cron/Subagent

### Long-Run Autonomous Program

Use `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` when the Human authorizes one complete, long-duration program rather than a sequence of manually gated micro-tasks. The program is fully planned and preflighted first; its launch packet pre-grants the exact stage, branch, file-class, path, P3/bridge, and publication permissions needed for the run.

After launch, the run is local-only until final publication. It uses batches of at most five and durable checkpoints as internal validation units, but does not stop for routine Human approval between those batches. Non-blocking ambiguities, protected-file skips, scope candidates, deferred stages, and manual-review items go to `.ai/LONG_RUN_LOGS/<program_id>.md`; unsafe mutations and whole-program blockers follow the protocol's stop/revert table.

Completion-preserving task expansion is the default within an authorized long-run program. Discovered cleanup, validation, alignment, reporting, and repair steps are folded into the current run when they are necessary for the original objective and remain inside the pre-granted authority.

The successful end state is one consolidated compatible foreground-role review package followed by targeted post-run repair when needed. This mechanism never grants itself P3, bridge, source-push, merge, destructive-operation, or secrets authority.

### Current interactive thread

- retains the active conversation and steering messages;
- uses the current workspace, branch, permission policy, tools, model, and thinking configuration;
- is preferred for stateful implementation, Human interaction, and final judgment.

### Standalone automation

- starts a fresh scheduled run;
- must reconstruct state from durable files;
- depends on the local app/machine/project when configured as local automation;
- does not have a proven guarantee of automatic quota-recovery replay.

### Thread automation

- wakes the same thread on a schedule and preserves thread context;
- still requires an idempotent task, consumed-message tracking, and safe Git leases.

### Subagent

- receives a separate bounded context and role;
- is useful for extraction, tests, log analysis, and independent checks;
- adds token, coordination, and write-conflict costs;
- does not make final architectural, mathematical, merge, regeneration, or stage-gate decisions under current project rules.

Before automation or a subagent can act, its durable context pack must include protocol/common conventions, STATE, current signal/index, all non-null refs, AGENTS guidance, relevant domain protocol, source/review heads, consumed IDs, Human gate, allowed paths, forbidden actions, tests, completion criteria, retry state, and an explicit output schema.

## 11. Failure And Retry Policy

- Group failures by stable failure signature.
- Read-only diagnosis and evidence gathering do not consume a repair attempt.
- Make at most three concrete repair attempts for the same failure class.
- Every attempt must use new evidence, a changed hypothesis, or a materially different remedy.
- After the third failure, stop that line of work, preserve concise evidence, record the blocked state in the repository/global failure log required by current guidance, and escalate to the compatible foreground role or Human.
- Continue independent meaningful work when possible.
- A review-branch lease conflict is new external evidence, not permission to force-push. Fetch and inspect the new write; rebuild only when it is non-conflicting and consumed, otherwise request reconciliation.
- A required ref missing at the observed review head is invalid protocol input, not an execution repair failure. Check it once, return a blocked handoff, and retry only after a new signal or review-head change.

## 12. Open Questions And Future Work

1. **`detail_ref` validation:** `detail_ref` is now a formally optional handoff field. The seven-field core remains valid; future validation should verify that a non-null detail ref resolves to a Codex-generated artifact, normally under `.ai/CODEX_REPORTS/`.
2. **Automation context pack:** define a machine-validated schema, idempotency rules, retry/resume behavior, and quota-exhaustion evidence before enabling automation.
3. **Execution profile validation:** validate required structure and `mode`; keep model/thinking labels extensible because runtime support varies.
4. **Multi-model conflict/debate:** define roles, evidence format, decision authority, dissent preservation, and Human escalation before introducing debate workflows.
5. **Accepted report promotion:** define when review-only reports are copied to the source branch as durable protocol evidence.
6. **Protocol evolution:** future revisions require an explicit reviewed task and source commit; review-branch drafts do not change the active source protocol implicitly.
7. **City-State OS binding:** future automation should define how `.ai` handoff reports map into campaign manifests and audit ledgers without treating mailbox state as runtime activation.
