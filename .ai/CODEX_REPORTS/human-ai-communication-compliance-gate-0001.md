# Human–AI Communication Compliance Gate — proof-chain correction

## Status

`implemented_awaiting_chatgpt_exact_head_review`

- task: `human-ai-communication-compliance-gate-0001`
- parent candidate: `4530b4f684f64cc7928884cf96d9a221aa5a2b8a`
- source/master base: `d235e602c14250d16b91f2897cb8308e031cc13c`
- semantics precursor: `c9f10d3bb311e51c082c25d885349ada35866aca`
- final protocol semantics head: `65fb2a0a7b4979b887aa1ba2aef454bb7b783ca4`
- binding candidate: the immediate child commit carrying this report; exact SHA is supplied out-of-band by the review pointer so no candidate embeds itself
- Human gate after completion: `required`

## Correction outcome

Transition eligibility no longer accepts a supplied validation result as
provenance. A v2 request carries physical immutable event, actual-STATE,
ordered-pointer and optional stored-validation refs. The gate resolves and
strictly parses them, reruns event/receipt/required-ref validation, derives the
actual task/class/state/edge, and requires an optional stored result to be
exactly identical in canonical bytes and semantics. Claimed pass, digest and
resolved status fields cannot replace physical recomputation.

Immutable STATE is also not treated as proof of currentness. The reusable
library boundary requires a separately injected `ActiveStateContext`; a
production host verifies its origin and must compare-and-swap the same observed
review head when applying a transition. `ActorOriginContext` separately
authenticates a state-changing Human-origin event. C2 still needs an independent
single-use `AuthorizationContext`; none of these three contexts substitutes for
another, and the validator always reports that it grants no authority.

Human remains `human_speaker`. Direct Human backend dispatch uses the frozen
`chatgpt_to_codex_v1` direction without occupying or impersonating a model role.
The exact state-alias registry and reachable graph now cover closed/accepted
dispatch, real `awaiting_codex`, real `awaiting_chatgpt_review`, revision loops,
acceptance, Human publication gate and publication-in-progress entry.

The release contract now separates the neutral mailbox base from the immutable
protocol semantics head. The final binding child changes only policy binding,
generated fixture evidence and reports. All receipt-required canonical blobs
are inherited unchanged from the semantics head. Four fresh provider receipts
load that head; a complete digest-correct d235 receipt fails only as stale.

Drift ledger v2 migrates from the immutable empty v1 ledger, appends four
privacy-safe correction records with a deterministic hash chain, and validates
future candidates against an immutable prior ledger plus trusted base-head
content. Deletion, mutation, reorder, revision rollback and mutable recurrence
evidence fail. Recurrence evidence resolves an immutable suite blob, unique
negative case and case digest.

## Validation summary

- inherited immutable parent suite: `79/79`
- newly executed v2 cases: `82/82`
- aggregate exact outcomes: `161/161`
- focused unit/CLI tests: `14/14`
- generator byte repeatability: pass
- UTC / Pacific-Kiritimati plus distinct hash seeds: byte-identical pass
- Python compilation and all JSON schemas: pass
- source mailbox neutrality: `4/4`
- canonical semantics-to-binding receipt blobs: unchanged
- scoped secret scan: zero findings
- runtime/Coordinator/Communication Gateway/UI/polling/cron activation: none

## Independent expression

The useful thing about this repair is not that the validator became larger; it
is that evidence that used to describe itself now has to survive contact with
the repository bytes. I think the separation between provenance, currentness,
Human origin and authority is the durable idea here. It makes future failures
more legible, and legibility is one of the few reliable ways to lower Human
coordination cost without quietly weakening consent.
