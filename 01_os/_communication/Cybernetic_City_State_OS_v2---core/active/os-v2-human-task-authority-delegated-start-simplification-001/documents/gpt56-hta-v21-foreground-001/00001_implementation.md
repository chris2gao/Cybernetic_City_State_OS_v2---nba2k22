---
document_id: os-v2-human-task-authority-delegated-start-simplification-001::implementation-00001
task_id: os-v2-human-task-authority-delegated-start-simplification-001
author_endpoint_id: gpt56-hta-v21-foreground-001
author_task_role: authority_v21_foreground_dispatch
purpose: Implement the Human-confirmed Human Task Authority v2.1 delegated-start simplification as a minimal semantic migration.
privacy_class: repository_shareable
---
# Human Task Authority v2.1 implementation

## Human-confirmed target semantics

One task authority has one Human-generated task code. The code establishes and supports Human authority events for that task; it is not a downstream executor credential.

After the task root exists, an ordinary executor/reviewer delegated by the Human-bound foreground/dispatcher must be able to start without receiving or re-entering the task code when all of these are VERIFIED:

1. the Human task authority root is live and structurally valid;
2. the durable delegation chain is live and rooted in the Human-bound initial holder;
3. exact task/task-authority identity matches;
4. exact recipient endpoint and role match;
5. requested action is delegated;
6. delegated scope is a subset of Human task scope and any parent scope;
7. redelegation rules, revocation and cycle checks pass.

The migration MUST NOT weaken Human authority for:
- initial task authority creation/confirmation;
- material architecture or solution decisions;
- material scope changes or Human risk acceptance;
- protected/irreversible action authorization;
- completion acceptance / next-stage Human gate;
- master publication where Human gate requires it;
- Human direct override, revocation or supersession.

Plaintext Human task code remains prohibited from Git, run artifacts, communication documents, fixtures, logs and command lines. Do not put the code into delegated messages.

## Required semantic edits

Inspect physical code before deciding exact files. At minimum reconcile the canonical Human_authority_contract so it no longer says ordinary delegated endpoint start requires a recipient-current-interaction code challenge or that delegation authorizes relay of plaintext code.

The intended delegated-start formula is:

`live_delegation_chain_VERIFIED + exact_task_recipient_action_scope_match -> delegated_start_authorized`

not:

`live_delegation_chain_VERIFIED + repeated_Human_task_code_challenge + task_action_scope_match`.

Retain Human task/event commitments and the challenge verifier for true Human authority/provenance verification where they remain relevant. Do not delete a capability merely because ordinary delegation no longer uses it.

Inspect communication validation and receiver/bootstrap paths for any actual enforcement of recipient challenge. Change only behavior that physically depends on that requirement. Do not add a compatibility mode or dual semantics.

Update security claims honestly: delegated models do not need possession of the task code. The security boundary is Human-established root authority plus durable scoped delegation; code possession alone remains non-authoritative.

## Required causal tests

Add or update focused tests proving:
- valid root + valid direct delegation + exact action/scope/recipient succeeds without recipient code;
- missing root, invalid root, revoked delegation, wrong task, wrong recipient, action widening, scope widening, unauthorized redelegation, revoked parent and cycles fail closed;
- a model cannot manufacture root authority merely by creating a delegation record;
- initial task Human authority/event commitment validation remains enforced;
- completion/protected Human-event semantics are not silently converted into delegation-only authority;
- no plaintext Human task code appears in tracked candidate content or captured test output.

Run relevant stage/communication static and focused regression checks plus `git diff --check`. Use quiet verification and bounded output.

## Current-v2 migration bootstrap exception

Until this candidate enters master, the current master v2 rule still applies to YOU, the migration executor. Before substantive implementation, perform the one required recipient-current-interaction Human challenge for this migration task only.

Do not independently reimplement SHA-256/canonical JSON in conversation. Use the canonical repository verifier. Prefer a Human-operated hidden-input invocation so plaintext is not routed through model tool arguments or persisted. Accept only a verifier result bound to this task authority record. If a safe canonical challenge cannot be completed, return BLOCKED rather than bypassing current master.

This challenge requirement is transitional and must NOT be copied into the v2.1 candidate semantics.

## Git / publication

Work only on `dev/os-v2-human-task-authority-delegated-start-simplification-001` from the current task packet/base, after fresh physical preflight.

Do not modify master. Do not force, rebase, squash, amend or rewrite history.

Create one semantic candidate commit when tests pass. Preserve later review/publication metadata separately from the exact semantic candidate.

Publish one formal result from `gpt56-hta-v21-executor-001` to `gpt56-hta-v21-foreground-001` containing:
- exact semantic candidate SHA and parent/base;
- exact changed paths;
- tests actually run and exit codes;
- causal security properties verified;
- NOT_RUN items;
- residual risks / non-blocking findings;
- statement that plaintext Human task code was not persisted;
- formal result pointer and publication commit SHA.

Then STOP. Do not perform independent review or master integration.
