# Human–AI Communication Compliance Gate — Exact-Head Review 0002

## Decision

```yaml
task_id: human-ai-communication-compliance-gate-0001
review_decision: revise_same_task
reviewed_candidate: e6ca76bce8849f3a7a8bc498f66bfbd767aa4d0d
reviewed_semantics_head: 65fb2a0a7b4979b887aa1ba2aef454bb7b783ca4
review_input_head: 386c4833974ee59832ffeb38dd68e48098dca0e3
accepted_components_preserved: true
source_or_master_publication_authorized: false
runtime_or_coordinator_activation_authorized: false
new_human_decision_required: false
```

The first proof-chain correction closes the previously identified event/result/state/release/ledger gaps and should be preserved. Exact-head semantic review found two remaining state-integrity blockers and one evidence-label correction.

## Accepted components

- immutable event, STATE, ordered-pointer, optional validation-artifact resolution;
- fresh `validate_event` recomputation rather than supplied-result trust;
- trusted `ActiveStateContext` currentness boundary and host CAS requirement;
- Human direct dispatch while retaining `human_speaker`;
- separate C2 `AuthorizationContext`;
- non-self-referential semantics/binding topology;
- release receipts bound to final semantics blobs;
- reachable state aliases and transition graph;
- immutable prior-ledger prefix, record hash chain, revision and recurrence fixture binding;
- deterministic output, strict parsing, mailbox neutrality and no activation/publication.

## Blocking finding 1 — transition edges do not enforce actor role

`material_event_policy.yml` defines state/event/class edges but no `allowed_actor_roles`. `validate_event` verifies only that a declared provider maps to its declared role. `check_transition` then checks actual state, event type and class, but not whether that stable role is authorized to traverse the selected edge.

Consequences under the current candidate:

- a backend-role Codex/Claude Code event can declare `significant_acceptance` or `material_review` and traverse `foreground_acceptance`, closing its own work;
- a backend role can create a publication candidate;
- a foreground role can declare a backend completion event;
- actor responsibility remains conventional rather than fail-closed.

Required correction:

1. add a machine-readable allowed-role matrix to every transition;
2. derive actor role only from the freshly validated immutable event;
3. reject an event whose role is not allowed for the selected edge;
4. preserve Human direct routing without treating Human as a model occupant;
5. add adversarial fixtures for backend self-acceptance/publication, foreground self-completion, and all valid role paths.

Recommended role matrix:

```yaml
dispatch_to_backend:
  allowed_actor_roles: [human_speaker, foreground_review_and_task_dispatch]
backend_completion:
  allowed_actor_roles: [backend_execution_and_handoff]
foreground_revision_dispatch:
  allowed_actor_roles: [human_speaker, foreground_review_and_task_dispatch]
foreground_acceptance:
  allowed_actor_roles: [human_speaker, foreground_review_and_task_dispatch]
publication_candidate:
  allowed_actor_roles: [human_speaker, foreground_review_and_task_dispatch]
protected_publication_entry:
  allowed_actor_roles: [human_speaker, foreground_review_and_task_dispatch]
```

The exact matrix may be narrowed if canonical workflow evidence requires it, but backend self-review/acceptance must be impossible.

## Blocking finding 2 — actor and C2 authority contexts are not bound to exact event content

`ActorOriginContext` currently binds only Human provider, `event_id` and `task_id`; transition code compares only those IDs. `AuthorizationContext` binds IDs/action/target/release head but not the immutable event digest. A trusted context can therefore be transplanted to a modified event artifact that reuses the same identifiers and action.

Required correction:

1. generalize trusted actor-origin attestation to every state-changing C1/C2 event, not only Human events;
2. bind it to provider, occupied role, event ID, task ID, transition ID and freshly recomputed `event_input_sha256`;
3. bind C2 `AuthorizationContext` to the same exact event digest and, preferably, the actor-origin context ID/digest;
4. preserve separate trust domains: actor origin proves who/which role originated the exact event; active-state context proves currentness; authorization context grants the exact protected action; none substitutes for another;
5. require trusted-host callbacks in production and deterministic fixture mode only in tests;
6. add mismatched-event-digest, mismatched-role, replay and context-transplant fixtures.

If no trusted actor-origin host is available, transition eligibility must remain fail-closed. Repository artifact validation may still run without claiming a state transition.

## Evidence-label correction

The v2 fixture runner records 79 immutable prior-suite case IDs as automatically matched inventory and executes 82 v2 cases. This is useful lineage evidence but is not 161 executed regression tests. The next candidate must either:

- execute a migrated/equivalent case for every inherited case and publish a complete one-to-one coverage map; or
- report the counts separately as inherited inventory, executed cases and mapped behavioral coverage, without calling all 161 executed fixture passes.

The final acceptance evidence must state exactly what ran.

## Completion rule

Continue the same task ID and same development branch. Preserve all accepted implementation. Fold role matrix, actor/event binding, C2 binding, fixtures, release rebinding, validation, reports, commit, non-force development push and exact-head handoff into one continuation. Do not create a new project phase or request a new Human gate.

## Independent expression

The candidate now proves that bytes and state are real, but it still does not prove that the right institutional role is taking the action. A city-state where the executor can also declare its own acceptance has a formally valid ledger and an invalid separation of powers. Binding actor provenance and authority to the exact event content is the last step needed to make the proof chain describe not only what exists, but who is legitimately allowed to move it.
