# Role batches: implemented host API and current limits

Status: **offline engineering candidate**, full M0-M5 work in progress. No new game observations. `role_batches.py` consumes the existing Native facade/compiler; it does not create a database, a negotiation engine, or a second approval authority.

## Host and role responsibilities

The existing identity/negotiation host supplies immutable `RoleCapabilityProfile`, current phase applicability grants, exact `TradeAgreement` records and an already sanitized data provider. They must not be deserialized from a model's permission claims. `ExecutionAggregator.collect` binds each role's batch to that host-authenticated profile. Phase grants are `(actor_uid, requirement_id)` applicability facts for the batch's exact world/save/generation/season/phase/snapshot context, not new Human approval ceremonies. Runtime and live-write authorization remain with the existing transport and the Human-approved scenario scope.

Roles submit `RoleActionBatch.from_dict` with `batch_id`, `context` and an `intents` array. Each intent has `intent_id`, `issuer_uid`, requirement `action_id`, exact `parameters` (the **submission parameter schema** from `describe_action`), optional `dependencies` and `agreement_ref`. Canonical frozen JSON prevents subsequent caller mutation. The original conceptual requirement field names remain separately documented; there is no automatic guessing or renaming of values.

```
authenticated role submissions
  -> aggregator.collect
  -> aggregator.plan(profiles, phase_grants, agreements)
  -> dispatcher.dispatch(pre_dispatch_context, readback)
  -> one result per original intent, including coalesced aliases
```

`RoleCapabilityService.submit_decided_actions` is a trusted orchestration entry that recomputes the plan; a model-supplied BatchPlan must not reach dispatch. No role JSON carries RVA, code pointers or permission objects. The host context guard must actually validate current process/save/world identity before each new operation. A no-op guard used in offline tests proves no live identity binding.

## Preflight and execution behavior

- All intents compile inertly before any Native call. Unknown bindings, role/team mismatches, absent current-phase attestations, invalid ranges, missing/cyclic dependencies or conflicting writes produce NOT_EXECUTED results. The aggregator never decides which competing role wins.
- A shared Native handler does not widen a logical capability: RunPlayTendency grants only that setting; known percentages are0..100. BenchDepth UI endpoints are still unknown, so the role batch route reports that missing field contract rather than presenting255 as a meaningful rotation size.
- The six POE requirements reuse the known Apply path, with the four additional fields mapped through the generic settings handler. Two further daily training patch requirements use existing Native getter/Apply and preserve unrequested input fields. Their maturity remains static/offline for untested input combinations. Current effective requirement mappings59 after minute and explicit Player stat-batch additions; historical PR18 crosswalk50 is unchanged. The two raw training actions, minute action and two explicit stat-batch actions bring the Native action registry to67; see TRAINING_PATCH_CONTRACT.md for units/slot-label gaps.
- Agreed trade variants use **AddPlayer/AddPick -> context -> direct Process**. The historical FullCheck variants remain in the raw registry for audit, not as the role execution route. Both GM identities/teams and the exact directional package digest must match the host agreement. Symmetric submissions from both GMs coalesce once; original inputs and dependency aliases remain in each result. No salary matching, replacement assets or TeamID writes.
- Role requests are durable local outbox records, not Native calls or automatic messages. An explicit host player scope prevents one Player issuer requesting changes as another player.
- Same-field and same-asset conflicts are rejected as a group, including proposals that attempt to hide a conflict behind execution order. Non-overlapping fields can execute by explicit dependency order. A batch is not an ACID game transaction.

## Durable journal and recovery

The caller supplies a private `ExecutionJournal` directory. It is execution traffic, never the basketball facts database. Records are scoped by world/save/generation. An OS byte-range/file lock serializes dispatchers and releases if the owning process dies. No daemon or stale-lock timeout runs.

Batch and issuer+intent identities are bound durably to payloads. Before invoking the facade, persist the operation claim and touched resources. Preserve the Native result before independent readback. Once claimed, absence of a final receipt is UNKNOWN, not permission to retry. A Native return alone is `NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`; only a separately supplied host observer with evidence bound to the exact context and intent can produce `APPLIED_READBACK_CONFIRMED`.

An unknown result stops later items in that batch. Unresolved resources remain reserved across **new batch IDs and new intent IDs**; unrelated resources can proceed in a separately submitted batch. A damaged claim fails closed. Previously recorded receipts are returned with `reused_historical_receipt=true`, not described as a new current observation.

`reconcile_unknown` performs **no Native call**. It uses the original claim and an explicit host observation; positive evidence can confirm the effect. A negative observation alone leaves uncertainty and cannot unlock replay. The pre-reconciliation receipt is retained. This is not an autonomous reconciliation watcher. Journal hashes and type checks do not defend against the trusted local operator editing files or forging an observer; authentication and evidence provenance remain integration duties.

## Verification and outstanding work

Offline tests use the actual planner and generated Native programs with a counting fake transport. They cover bilateral coalescing, shared-handler containment, target/phase checks, graph errors, crashes/no replay, unknown resource reservations, independent reconciliation and external request separation. They do not prove real memory access, current save binding, Native effects, UI or persistence.

Still open: complete role-friendly parameter cards and many of the183 Native contracts, full role data production adapter, signing/staff/editor/rotation/Playbook recovery, training suboperations, real readback observers and current-scene live tests after consolidated Human approval. `tools/export_role_coverage.py` produces an exact per-requirement checkpoint including all known gaps; a coverage file is not evidence of implementation or acceptance.

The indexed Player stat route validates every supplied field and value before any dispatch. Shared Native interfaces retain role-specific field allowlists: ordinary GM Intangibles only for abilities, named tendencies for normal roles, unnamed tendencies only for an explicitly granted world editor. Player UID scope is checked. Resources are reserved per player/family/field, so scalar and batch aliases conflict on the same field and any trade overlaps the entire player. The fixed stat preservation read stays internal; results expose only requested fields. See [Player stat contract](PLAYER_STAT_NATIVE_CONTRACT.md).
