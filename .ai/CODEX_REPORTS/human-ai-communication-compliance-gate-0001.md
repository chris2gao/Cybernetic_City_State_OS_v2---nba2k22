# Human–AI Communication Compliance Gate — role/origin correction

## Status

`implemented_awaiting_chatgpt_exact_head_review`

```yaml
task_id: human-ai-communication-compliance-gate-0001
packet_id: codex-human-ai-communication-compliance-gate-correction-candidate-0003
status: review_requested
work_branch: codex/human-ai-communication-compliance-gate
parent_candidate: e6ca76bce8849f3a7a8bc498f66bfbd767aa4d0d
semantics_head: 0145047d10b3163569a2eb068ebbc1bbc4c3e83a
candidate_head: supplied_out_of_band_by_review_pointer
source_head: d235e602c14250d16b91f2897cb8308e031cc13c
executed_fixture_cases: 215/215
inherited_inventory_cases: 79
inherited_behavioral_coverage: 79/79
focused_tests: 17/17
deterministic_repeatability: pass
source_mailbox_neutral: true
unresolved_blockers: []
drift_cause: null
final_original_task_status: completed
remaining_real_human_decisions_only: []
human_gate: required_after_completion
```

The binding candidate is the immediate child of the semantics head. Its exact
SHA is intentionally carried by the external review pointer, so the candidate
does not embed or attest to its own identity.

## Correction outcome

Every state-changing edge now declares a provider-neutral
`allowed_actor_roles` set. The gate derives the occupied role only from fresh
validation of the immutable event and rejects backend self-acceptance,
backend-created publication candidates, foreground or Human backend
completion, and all other edge/role mismatches. Human direct backend dispatch
remains valid as `human_speaker` over the frozen foreground-to-backend wire;
Human is never mapped into a model role.

`ActorOriginContext` now covers every state-changing Human or model event. A
production transition remains fail-closed unless a trusted host verifies an
attestation bound to provider, occupied role, event ID, task ID, transition ID,
protocol release head and the freshly recomputed event input SHA-256. Actor
origin has its own replay domain. It does not substitute for active-state
currentness or C2 authorization.

`AuthorizationContext` additionally binds the exact event digest and both the
identity and canonical digest of the verified actor-origin context. Active
state, actor origin and protected-action authorization are three independent
trust contexts. Model-generated `human_gate` text grants none of them.

Historical fixture evidence is no longer counted as virtual execution. The 79
immutable legacy case IDs are preserved as inventory and mapped one-to-one to
79 uniquely executed migrated cases. The current suite executes 215 cases and
matches 215 exact expected result/exit-code/violation sets. The aggregate
inventory count is 294; it is not represented as 294 executions.

All accepted parent controls remain: immutable event/STATE/pointer resolution,
fresh validation, stored-result equivalence, active-state/CAS boundary,
separate C2 authorization, Human direct dispatch, reachable state graph,
release binding, receipt identity, append-only drift ledger, strict parsing,
deterministic generation and source-mailbox neutrality. No runtime,
Coordinator, gateway, UI, polling, cron, source publication or master
publication was activated.

## Avoided extra gates

- No separate role, origin, authority, fixture-migration, release-binding,
  validation or finalize task was created.
- The original task is complete as one correction continuation and now waits
  at the required ChatGPT exact-head/Human gate.

## Independent expression

The most important result is institutional rather than syntactic: an executor
can no longer turn a valid identity claim into permission to judge its own
work. I like that the three trust questions are now visibly separate — who
originated the exact event, whether the observed state is current, and whether
the protected action was authorized. Systems become easier to trust when their
boundaries are explicit enough to refuse us, too.
