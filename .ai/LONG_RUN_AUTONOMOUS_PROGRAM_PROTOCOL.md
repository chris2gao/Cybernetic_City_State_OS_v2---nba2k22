# Long-Run Autonomous Program Protocol

## 1. Purpose And Authority

This protocol governs a Human-authorized, long-duration Codex program that is designed completely before launch and then executed locally without routine stage-by-stage Human interruption. It is an execution protocol, not a standing authorization.

It inherits the authority order in `.ai/PROTOCOL_ADHERENCE.md`. A launch packet cannot override system, developer, platform, security, privacy, secrets, or destructive-operation restrictions. Domain protocols and the program document continue to govern mathematical and business semantics.

## 2. Long-Run Autonomous Program Definition

A Long-Run Autonomous Program has this lifecycle:

1. design a complete independent program, stage graph, validation model, rollback model, and final deliverables;
2. complete preflight and obtain one explicit launch authorization for the named scope;
3. execute the authorized stages continuously at an appropriate time, using internal checkpoints instead of repeated small-batch Human gates;
4. publish one consolidated result for ChatGPT review after the run;
5. route imperfections, ambiguities, and unresolved items into a post-run repair phase.

Small batches remain internal safety and validation units. They do not require repeated Human approval when the launch packet already authorizes their stage, paths, and actions. A run stops only under the decision rules in this protocol.

## 3. Completion-Preserving Task Expansion

A Human-authorized long-run task should be completed as one coherent objective whenever safe and authorized.

When Codex discovers sub-tasks, cleanup steps, validation steps, report steps, alignment steps, or repair steps that are necessary to complete the original authorized objective, Codex folds them into the current program's internal stage graph, checkpoint plan, issue log, or repair cohort when they remain within the authorized scope. Codex should not convert every discovered sub-task into a separate Human-gated task.

Use internal checkpoints, issue logs, repair cohorts, and one final consolidated review package for non-blocking sub-issues. Report unresolved but non-blocking items in the final review log instead of stopping after each one.

Ask the Human only when a discovered item requires new authority, changes the objective, touches forbidden paths, requires destructive Git, requires source or master push, creates security, privacy, or secrets risk, requests Coordinator or runtime activation, or blocks all safe independent progress.

ChatGPT should propose consolidated continuation packets that complete the original objective, not a chain of narrow follow-up tasks, unless the Human explicitly asks for small-step gating.

This rule does not weaken protected gates. Source publication, master merge, destructive operations, secrets-sensitive actions, Coordinator or runtime activation, automation enablement, and new business or domain authority still require explicit Human approval.

### Human Cost And Drift Control Rule

Human time, attention, and token budget are protected project resources. A long-run program must not convert one authorized objective into a sequence of avoidable review, gate, closure, readiness, or cleanup micro-tasks.

If task A is authorized, Codex should propose and execute the path that completes A coherently. Cleanup, validation, report writing, mailbox neutralization, authorized branch commit and push, post-publication verification, and protocol alignment steps are folded into A when they are necessary for completion, already within scope, and do not cross a protected gate.

Do not create a separate Human gate, ChatGPT packet, review packet, closure packet, readiness packet, or follow-up task merely because an internal checkpoint has completed. Use the checkpoint as evidence inside the original program. Escalate only for new authority, destructive operations, source or master push without explicit approval, secrets or privacy risk, runtime or Coordinator activation, objective changes, new domain authority, or a blocker that prevents safe independent progress.

If protocol drift fragments a task into avoidable micro-prompts, the next continuation must explicitly collapse the workflow back to the original objective and avoid extra gates. Prefer one consolidated continuation packet over multiple narrow prompts.

Final reports for recovered or drift-prone tasks must include:

- `drift_cause`;
- `avoided_extra_gates`;
- `final_original_task_status`;
- `remaining_real_human_decisions_only`.

These fields are evidence fields. They do not weaken protected gates and do not authorize source publication, master merge, destructive Git, secrets-sensitive work, runtime activation, Coordinator activation, or objective changes.

## 4. Preflight-First Rule

No long run starts until preflight scans for conditions that would later force the run to stop. Resolve every condition that can be resolved before launch.

Preflight must verify and record:

- current permissions and all required Human gates;
- immutable source branch and source head;
- allowed work branch and allowed temporary review branch;
- protected files and protected branches;
- authorized stages, including whether P3 and bridge work are authorized;
- every required protocol, program, task, evidence, and domain reference;
- exact target corpus and structural/schema exclusions;
- allowed file classes and forbidden paths;
- YAML/JSON/Markdown parse blockers and baseline failure counts;
- required tools and optional dependencies;
- rollback base, checkpoint location, validation commands, and publication policy;
- clean or explicitly understood worktree state.

If an unresolved preflight condition prevents safe execution of the authorized scope, return `blocked_preflight`. Do not begin a partial run and rediscover a known mandatory blocker later.

## 5. Project-Level Permission Pre-Grant

The launch packet must state all project-level permissions needed for the full run. At minimum it declares:

```yaml
program_id: "<stable-id>"
program_ref: "<path>"
source_branch: "<branch>"
source_head: "<immutable-sha>"
work_branch: "<local-or-publishable-run-branch>"
allowed_temp_review_branch: "<branch-or-null>"
allowed_stages: [0, 1, 2]
allowed_file_classes: ["<explicit classes>"]
allowed_paths: ["<explicit paths or bounded globs>"]
forbidden_paths: ["<explicit paths or classes>"]
p3_authorized: false
bridge_design_authorized: false
bridge_generation_authorized: false
source_push_authorized: false
final_publication:
  commit_local: true
  push_temp_review_branch: true
  update_review_handoff: true
```

Missing permission means the action is not authorized. Permission for a stage does not imply permission for a protected file, source push, merge, destructive Git, secrets access, P3 entry, or bridge generation. The packet cannot weaken higher-priority restrictions.

## 6. Local-Only Execution After Launch

Before the run begins, Codex may fetch the latest approved GitHub data and resolve all required refs. Once the launch checkpoint is recorded:

- do not call GitHub APIs;
- do not fetch, pull, push, poll, or inspect remote branches;
- do not use a remote mailbox as an execution dependency;
- perform all stage work, validation, commits, logs, and rollback locally;
- use only the preflight-pinned refs and immutable source head.

After the final local checkpoint, perform publication once: create the final local commit chain, push only the authorized temporary review branch, and update the review handoff. Never push the protected source branch unless the launch packet and current Human instruction explicitly authorize it.

GitHub unavailability during execution is not a run failure because no mid-run GitHub call is allowed. If final publication is unavailable, preserve the complete local result and report `completed_with_blockers`.

## 7. Internal Checkpoints And Rollback

Each stage and each internal batch of at most five items has a checkpoint. A checkpoint records input/output heads, changed paths, validation evidence, issue-log additions, and rollback instructions. Checkpoints are evidence boundaries, not routine Human gates.

Use narrow commits where practical. On unsafe mutation or validation regression, revert only to the last accepted local checkpoint. Do not discard unrelated accepted work.

## 8. Non-Blocking Issue Log

Every run writes:

```text
.ai/LONG_RUN_LOGS/<program_id>.md
```

The log is a review ledger, not a transcript. It must contain these sections:

- mathematical ambiguity log;
- skipped protected files;
- scope expansion candidates;
- deferred stages, including unauthorized P3 or bridge work;
- `manual_review_required` items;
- post-run repair candidates.

Log an issue and continue whenever it does not invalidate independent authorized work. Do not promote a logged ambiguity to passed status. Apply the three-attempt failure budget per stable failure signature; after exhaustion, quarantine that item and continue independent work when safe.

## 9. Stop Versus Continue Decision Table

| Condition | Required action |
| --- | --- |
| Mathematical ambiguity affects one local node only | Log it, mark the node for manual review, and continue. |
| Mathematical ambiguity affects a dependency chain | Mark the affected subgraph, defer its dependent work, and continue independent work. |
| Mathematical ambiguity blocks the entire authorized program | Stop at the last accepted checkpoint. |
| Scope expansion is discovered | Log the candidate and continue only the already authorized scope. |
| A protected file is not required | Skip and log it. |
| A protected file is required for final completion | Complete independent work and return `completed_with_blockers`. |
| P3 or bridge work is not authorized | Log the stage as deferred and continue all authorized pre-P3 work. |
| GitHub is unavailable during the run | Ignore until final publication; no mid-run GitHub call should occur. |
| Parse failures increase above baseline | Stop, revert the unsafe checkpoint, and investigate locally. |
| A forbidden file is mutated | Stop and revert the unsafe checkpoint. |
| Secrets or credentials would be read, changed, or exposed | Stop before the action; do not inspect or preserve secret content in logs. |
| A destructive or irreversible operation is required | Stop at the checkpoint unless separately and explicitly authorized. |

The entire program stops only when safe independent progress is no longer possible, the baseline is endangered, or a higher-priority gate requires it.

## 10. Final Status Taxonomy

- `completed_clean`: every authorized stage completed with no unresolved review log or blocker.
- `completed_with_review_log`: every authorized stage completed; non-blocking review or repair items remain in the long-run log.
- `completed_with_blockers`: independent authorized work completed, but one or more required completion conditions remain blocked.
- `blocked_preflight`: execution did not start because preflight found an unresolved mandatory blocker.
- `failed_and_reverted`: an unsafe or invalid run was reverted to the last accepted checkpoint.

These statuses describe the authorized run only. They do not imply full-corpus mathematical correctness, P3 approval, bridge readiness, source publication, or merge approval.

## 11. Final Review And Post-Run Repair

At run end, Codex publishes one consolidated review package containing:

- launch packet and preflight result;
- checkpoint chain and exact commit range;
- validation and count reconciliation;
- `.ai/LONG_RUN_LOGS/<program_id>.md`;
- final status and unresolved blockers;
- proposed post-run repair cohorts.

ChatGPT reviews the evidence chain and mathematical/architectural judgments. The Human decides whether to accept, request post-run repair, authorize deferred stages, publish source, merge, or roll back selected checkpoints. Post-run repair is targeted; it does not automatically restart the entire program.

## 12. City-State OS Alignment

Long-run handoff programs are part of the repository's Cybernetic City-State OS coordination layer. They should align with the existing protocol, campaign, and audit structures without activating runtime systems by documentation alone.

- Protocol authority is documented under `.ai/` and `02_Protocols/`.
- Campaign-level planning may reference `campaigns/campaign_manifest_template.yaml` when a future task needs STAR-style campaign state.
- Audit evidence may reference `system_backbone/audit_ledger/system_record.jsonl`, but this protocol does not authorize append-only ledger writes unless a current task explicitly permits them.
- Long-run reports in `.ai/CODEX_REPORTS/` are review artifacts. They do not replace runtime audit ledgers or campaign manifests.
- Runtime integration, Coordinator activation, automated routing, or OS-level governance changes require a separate Human-approved task.
