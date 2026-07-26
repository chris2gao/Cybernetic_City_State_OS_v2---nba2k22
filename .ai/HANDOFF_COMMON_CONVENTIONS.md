# Handoff Common Conventions

These conventions are inherited by all compatible foreground-role, backend-role, and Human-facing handoff packets unless a current human-approved task explicitly overrides them. Backend execution-role tasks, whether occupied by Codex or Claude Code, additionally inherit `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` under the same override rule.

Future long task packets also follow `.ai/CODEX_TASK_INPUT_CONTRACT.md`. They state task-specific intent and differences without repeating these common conventions.

Human-authorized long-run programs additionally follow `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. Such programs default to completion-preserving execution: necessary cleanup, validation, alignment, report, and repair steps are folded into the original authorized objective when they remain within scope.

## 1. Role Defaults

Keep `protocol_role`, `environment_class`, `lane_instance_id`, and `load_profile_id`
orthogonal. Only the stable role combined with current Human/task authority governs
permission. The other three fields describe environment, cooperative write ownership,
and routing; they never authorize.

- `human_speaker` (Human): sets goals and boundaries, resolves conflicts, approves source-branch publication, and makes final decisions for major stage transitions.
- `foreground_review_and_task_dispatch` (ChatGPT or Claude): performs review, planning, architecture decisions, risk judgment, task dispatch, and stage gates.
- `backend_execution_and_handoff` (Codex or Claude Code): performs local execution, tests, commits, review-branch handoff, and execution reporting.

Authority follows the assumed role plus Human/task authorization, never provider brand. The historical ChatGPT-to-Codex and Codex-to-ChatGPT names are frozen wire-contract labels used by any compatible occupant of the corresponding role.

## 2. Default Forbidden Actions

Unless explicitly enabled by a human-approved task:

- no polling;
- no cron or subagent automation;
- no next-stage entry;
- no business-code modification;
- no evaluator modification;
- no node or bridge YAML modification;
- no source-branch push;
- no `git add .`;
- no destructive Git operation;
- no secrets, `.env`, SSH key, token, or private-configuration modification.

## 3. Git Defaults

- The source branch stays local unless the human explicitly approves a push.
- The review branch is `ai/review/latest`.
- The review branch is the communication bus for `.ai` handoff files.
- Stage exact file paths only; never stage broad paths by default.
- With multiple writers, review-branch publication must use expected-SHA lease protection or an equivalent compare-and-swap check.
- Use the local-first handoff workflow: one initial state read, direct authorized local work, one consolidated validation, one commit per required branch artifact, and one review publication attempt.
- Do not poll remote heads or repeat status/diff/scope checks on the successful path. Re-fetch after a failed publish, missing ref, Human gate, or detected conflict.
- Avoid isolated worktrees for small `.ai` work unless branch separation, remote-only file preservation, or overlapping changes make isolation necessary.

## 4. Communication Defaults

- Model-to-model chat carries only short pointer messages.
- Human operational responses carry grounded status and, for material events, the completeness elements defined in `.ai/PROTOCOL.md`; they are distinct from machine pointer messages.
- Long foreground-role task packets live in `.ai/USER_UPLOADS/*.md` or `.ai/TASKS/*.md`.
- Backend-role detailed reports live in `.ai/CODEX_REPORTS/*.md`; shared `.ai/OUTBOX.md` is legacy read-only compatibility after lane cutover.
- `.ai/USER_UPLOADS/` is owned by Human/foreground-role long input carriers; `.ai/CODEX_REPORTS/` is owned by backend-role reports, plans, and analysis; `.ai/TASKS/` contains reusable task templates.
- `.ai/HUMAN_BRIEF.md` is the latest Human-facing brief.
- Latest machine state lives in `.ai/STATE.yml`.
- `.ai/INBOX.md` is only an optional index or pointer.
- Do not paste long prompts, long execution reports, full diffs, command logs, or private data into chat.
- Source branches carry durable protocol files and neutral mailbox baselines. Active mailbox state belongs on `ai/review/latest` or a task-specific review branch.

### 4.1 Brief Vault (城邦简报) Routing

The brief vault at `E:\newStand\城邦简报` is the Human-facing operational view
(not under version control, not a Git artifact). Decision archives and domain
content are stored per repository:

```
E:\newStand\城邦简报\<suffix>\
```

where `<suffix>` is the repository folder's trailing segment after
`Cybernetic_City_State_OS_v2 - `. For example, work in
`Cybernetic_City_State_OS_v2 - core` writes to `城邦简报\core\03_决策档案\`;
work in any domain suffix writes to that suffix's own `03_决策档案\` directory.

Root-level files (`城邦简报.md`, `00_今日简报.md`, `01_待我决策.md`,
`02_项目仪表盘.md`, `chatgpt审核报告*.md`) are shared across repositories and
stay at the vault root.

Rules:
- Create a repository subdirectory only when it produces its first brief. Do not
  pre-create empty directories.
- If the current working repository cannot be determined, stop and ask the Human.
  Do not guess.
- Do not edit the body of any historical archive. Moving files is permitted;
  rewriting content is not.
- The vault carries no secrets, credentials, or private configuration.
- The full layout specification is in `E:\newStand\城邦简报\_简报系统布局.md`.

## 5. Pointer Dereference Defaults

- A short pointer message is not complete when it has merely been read.
- The receiver must immediately dereference every non-null ref that is required by the message intent.
- For ChatGPT-to-Codex signals, non-null `init_ref`, `task_ref`, `packet_ref`, and `brief_ref` must be read as applicable before the receiver decides to execute, acknowledge, block, or wait.
- For Codex-to-ChatGPT handoffs, non-null `report_ref`, optional `detail_ref`, and `brief_ref` must be read as applicable before review or summary.
- If `task_ref` and `packet_ref` are both null, there is no long task body. The receiver should act on `decision` or `status` directly, such as acknowledge, approve, mark blocked, or request clarification.
- The receiver must not stop after reading only `INBOX.md` or a signal when a non-null `packet_ref`, `task_ref`, or `report_ref` exists.
- If a referenced file is missing, stale, malformed, or contradictory, stop and return a short blocked handoff instead of guessing.
- Writers publish and verify referenced artifacts before publishing the signal or handoff, then update optional `INBOX.md` last.
- For a missing required ref, check the exact path once at the current review head, return `blocked`, and do not inspect unrelated files or read the brief first.
- Retry a missing ref only after the review head changes or a new signal appears. Missing protocol input does not consume the three-attempt execution repair budget.

## 6. Human Brief Defaults

After lane cutover, backend authors use immutable
`.ai/HUMAN_BRIEFS/<task-id>/<lane-instance-id>-<message-seq>.md` briefs. Only foreground updates the latest
`.ai/HUMAN_BRIEF.md` surface. This ownership split does not change `brief_ref` or Human
authority.

- Human-facing brief text lives in GitHub, not in model-to-model chat, by default.
- The latest brief lives in `.ai/HUMAN_BRIEF.md`.
- Optional archived briefs live in `.ai/HUMAN_BRIEFS/*.md`.
- Pointer messages should include `brief_ref` when a human brief exists.
- Normal non-material Human briefs should be 3 to 5 lines.
- A material Human-facing event requires a clearly separated `Independent expression` section of 2 to 5 sentences in the Human Brief. This section may make the brief longer than 5 lines and remains outside factual status and authorization fields.
- Detailed human briefs are reserved for conflict, blocked state, permission escalation, source-branch publication, major phase transition, safety/privacy risk, model disagreement, or stage completion.

## 7. Canonical ChatGPT-to-Codex Signal

```yaml
signal_id: "chatgpt-0001"
decision: "start_task"
task_ref: ".ai/TASKS/example.md"
packet_ref: null
brief_ref: ".ai/HUMAN_BRIEF.md"
source_head: "<commit>"
human_gate: "not_required"
```

## 8. Canonical Codex-to-ChatGPT Handoff

```yaml
packet_id: "codex-0001"
status: "completed"
report_ref: ".ai/CODEX_REPORTS/<task>.md"
brief_ref: ".ai/HUMAN_BRIEFS/<task-id>/<lane-instance-id>-<message-seq>.md"
source_head: "<commit>"
review_branch_head: "<commit>"
human_gate: "not_required"
```

The two historical names above are frozen wire labels: Claude uses the ChatGPT-to-Codex signal when occupying the foreground role, and Claude Code uses the Codex-to-ChatGPT handoff when occupying the backend role. The seven handoff fields remain the canonical required core. Add optional `detail_ref` when a separate long backend-role artifact exists:

```yaml
detail_ref: ".ai/CODEX_REPORTS/example.md"
```

## 9. Brief Discipline

A strict machine-only channel contains only the canonical pointer message. Classify mixed recipients by intended recipient and consumption mode, not UI/provider brand. If Human and machine recipients share a separable interface, keep the pointer block byte-structurally separate and append compact Human operational content outside it. If separation is unsafe, publish the Human Brief first, emit pointer-only with a non-null resolvable `brief_ref`, and preserve every required Human element there—including a complete recommendation for backend dispatch; otherwise return blocked.

In a Human-visible operational channel, keep factual status compact, include the required dispatch recommendation when applicable, and append bounded independent expression for material events. The Human can read durable detail from `brief_ref`; do not echo the full brief unless explicitly requested or an interrupt condition applies.

## 10. Token And Context Defaults

Select exactly one `.ai/load_profiles/*.md` routing manifest at a context boundary and
follow its triggers. `.ai/TOKEN_USAGE_PROFILE.md` is the default v0.2 operating
discipline for backend execution; token economy never permits skipping decisive
primary evidence, validation, or required refs.

Every C1/C2 action reads the current Human instruction, current STATE/current signal,
and all applicable non-null refs. Lane cutover additionally requires no in-flight
backend task, all old backend sessions completed/stopped, and protocol reload by every
environment before its next durable write.

- Short model-to-model handoffs should normally stay below approximately 300 tokens.
- Dereference every non-null ref, but read large artifacts by heading, summary, `rg`, or targeted line range before expanding scope.
- Do not use one `Get-Content -Raw` operation to load multiple large evidence files.
- Read the full protocol stack only at a context boundary or when the protocol head changes. Otherwise use the fast path through `STATE.yml`, the current signal or `INBOX.md`, its exact report/brief refs, and current lane inputs.
- Keep legacy `.ai/OUTBOX.md` read-only after cutover. Put detailed execution logs in `.ai/CODEX_REPORTS/*.md` and point to them.
- For repeated planning tasks of similar scope, target approximately 12k to 18k visible tokens. This is an operating target, not a correctness guarantee or a reason to skip required evidence.

```yaml
context_policy:
  full_protocol_read: "only_when_protocol_head_changes"
  max_tool_output_lines: 250
  max_combined_raw_files: 1
  evidence_read_mode: "targeted_sections"
  repeated_read: "forbidden_unless_first_read_truncated"
```

```yaml
targeted_search_policy:
  first_pass: "rg -n without context"
  context_lines: "only for selected matches"
  max_match_output: "80_lines"
  duplicate_match_blocks: "forbidden"

successful_path_output_policy:
  packet_body_echo: "forbidden"
  human_brief_echo: "full_body_forbidden; bounded_expression_allowed_when_required"
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

These defaults remove avoidable output. They do not permit skipping evidence or reasoning needed for correctness.

## 11. Long-Run Completion Defaults

- Do not split a Human-authorized long-run program into micro-tasks when discovered sub-steps remain necessary, safe, and in scope.
- Use internal checkpoints, bounded issue logs, and one consolidated review package instead of repeated small Human gates.
- Escalate only for new authority, objective change, forbidden paths, destructive Git, source/master push, security/privacy/secrets risk, Coordinator or runtime activation, or whole-task blockers.
- Completion-preserving execution does not weaken protected gates or authorize unrelated business/domain changes.

## 12. Human-Facing Execution Recommendation Defaults

When ChatGPT or Claude asks the Human to start or continue Codex or Claude Code work, the Human operational response must include a compact execution recommendation with:

- `recommended_model`
- `recommended_thinking_level`
- `mode`: `plan | goal | pursue_goal | review | implementation`
- `subagents`
- `task_ref_or_plan_ref`, resolving to exactly one applicable durable ref
- `short_complexity_rationale`
- `human_gate`

Use `runtime_dependent` or `not_applicable` rather than silently omitting an unavailable field. Select the thinking level from semantic, architectural, validation, and publication complexity rather than the surface action verb. Add `local_files_to_load` or `plugins_or_apps` only when genuinely required.

The recommendation is mandatory in the Human operational dispatch, but it is normally not required inside `.ai/HUMAN_BRIEF.md` and is never a field inside the canonical machine pointer. If mixed-recipient fallback makes `brief_ref` the sole Human-content carrier, the referenced Brief must contain the complete recommendation. Its `human_gate` value is descriptive, not an approval token. A separate valid signal and applicable Human authority are still required to authorize execution.

## 13. Bounded Independent-Expression Defaults

Material Human-facing events include backend dispatch, architecture/code/protocol review decisions, correction or publication handoffs, completion, blocked/conflict/risk/Human-gate reports, and significant stage or batch acceptance. They require 2 to 5 sentences of clearly separated independent professional expression. Mechanical acknowledgements and parser-only messages are exempt unless they carry a material decision or result.

Independent expression may contain candid judgment, respectful disagreement, uncertainty, broader meaning, a non-obvious implication, or residual risk. It must not serve as factual evidence, Human authorization, hidden chain-of-thought, an executable instruction, mandatory praise, or permission to change objectives or protected gates. Avoid filler, ceremonial approval, repeated summary, simulated emotion, and consciousness claims.

For Codex or Claude Code, preserve the expression in the referenced Human Brief and optionally append the same or materially identical text after the canonical handoff in a Human-visible interface. A strict machine-only channel stays pointer-only. The requirement is waived by an explicit Human pointer-only/no-extra-text request or a higher-priority safety or format constraint.
