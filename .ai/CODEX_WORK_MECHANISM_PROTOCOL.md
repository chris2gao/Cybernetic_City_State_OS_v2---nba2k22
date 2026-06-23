# Codex Work Mechanism Protocol

Status: active canonical protocol for Codex execution workflows on the source branch.

## Scope And Authority

This protocol governs Codex task-execution mechanics: local implementation, file edits, tests, Git operations, review handoff, transcript/output behavior, context use, failure handling, and future automation/subagent execution design.

It does not govern mathematical or domain semantics and does not replace domain protocols. It does not override system, developer, or explicit current Human instructions. It does not authorize P2.10, business-code changes, source publication, merge, regeneration, automation, or any other gated action by itself.

## 1. Purpose

This protocol documents Codex's practical operating mechanism and the optimized workflow agreed among Human, ChatGPT, and Codex. It defines how Codex selects an operating mode, spends context, uses tools, edits and verifies files, publishes Git handoffs, reports failures, and stops at Human or ChatGPT decision gates.

The protocol optimizes correctness and coordination. It does not grant new permissions, bypass higher-priority instructions, or authorize a project stage that has not been explicitly opened.

## 2. Codex Operating Modes

### Goal mode

Goal mode gives Codex a persistent objective and completion criteria across turns. Codex continues from repository and external evidence, chooses the next useful action, implements and verifies authorized work, and audits every explicit requirement before claiming completion.

Use Goal mode when the outcome and definition of done are stable, implementation is authorized, and the work may require multiple steps or turns. Goal mode does not override repository rules, permissions, Human gates, source-push restrictions, or stage boundaries.

Goal mode is the default for authorized execution and GitHub-persisted Codex output.

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

When advising the Human to start a Codex task, ChatGPT may include a short human-facing execution recommendation and mention required plugins/apps or authentication scope. This recommendation is not required in the GitHub Human Brief and is not part of the machine handoff unless a signal, task, or packet explicitly references it. Ordinary local Git and filesystem work needs no plugin/app recommendation.

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
- Run integration verification appropriate to the affected surface.
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
6. publish one review handoff when ChatGPT review is needed;
7. return only the canonical short handoff.

Do not repeatedly poll remote heads or repeatedly run `git status`, `git diff --stat`, broad scope scans, or equivalent defensive checks during a successful task. One initial state check and one consolidated final scope/validation check are normally sufficient.

Do not create an isolated worktree merely for read-only inspection or a small `.ai` artifact. A worktree remains appropriate when a review-only commit must preserve remote-only files while the source branch stays checked out, when source and review commits must remain separate, or when overlapping work makes branch isolation necessary.

If review publication fails because the branch advanced, fetch the new head and inspect only changed/overlapping paths. If there is no overlap, rebuild or retry with a new explicit lease. If overlap or ownership is uncertain, return `blocked` or `conflict` rather than forcing the update.

## 7. File Channel Semantics

- `.ai/USER_UPLOADS/`: Human/ChatGPT-provided long task carriers and uploaded evidence.
- `.ai/CODEX_REPORTS/`: Codex-generated long reports, analyses, discovery output, and durable execution plans.
- `.ai/TASKS/`: reusable task templates selected by short signals.
- `.ai/OUTBOX.md`: latest concise Codex execution report and pointer index.
- `.ai/HUMAN_BRIEF.md`: latest Human-facing summary.
- `.ai/HUMAN_BRIEFS/*.md`: archived Human briefs for material conflicts, gates, risks, or stage completions.

Future Codex-generated long content goes to `.ai/CODEX_REPORTS/`. A Human-requested upload of Codex chat text into `USER_UPLOADS` is a provenance exception and does not change directory ownership.

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

The successful end state is one consolidated ChatGPT review package followed by targeted post-run repair when needed. This mechanism never grants itself P3, bridge, source-push, merge, destructive-operation, or secrets authority.

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
- After the third failure, stop that line of work, preserve concise evidence, record the blocked state in the repository/global failure log required by current guidance, and escalate to ChatGPT or Human.
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
