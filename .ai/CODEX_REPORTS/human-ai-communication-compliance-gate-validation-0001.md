# Human–AI Communication Compliance Gate — validation evidence

## Release topology

- parent candidate: `e6ca76bce8849f3a7a8bc498f66bfbd767aa4d0d`
- final semantics: `0145047d10b3163569a2eb068ebbc1bbc4c3e83a`
- binding: immediate child; exact SHA carried only by the external review
  pointer
- policy `source_mailbox_base_head`:
  `d235e602c14250d16b91f2897cb8308e031cc13c`
- policy `protocol_release_head`:
  `0145047d10b3163569a2eb068ebbc1bbc4c3e83a`

## Executed checks

1. Python compilation: validator, fixture generator and test module `3/3`
   pass.
2. Draft 2020-12 schema validation: all local schemas `12/12` pass.
3. Full actually executed fixture suite: `215/215` exact outcomes pass, with
   zero mismatches.
4. Legacy evidence: `79` immutable inventory IDs; `79/79` have complete,
   ordered, one-to-one mappings to unique executed migrated cases. Aggregate
   inventory is `294`; only `215` cases are reported as executed.
5. Unit/CLI suite: `17/17` pass, including the exact role matrix, all-actor
   origin requirements, event-content bindings, independent replay domains,
   immutable coverage-map resolution and release topology.
6. Generator repeatability: `138` generated files have aggregate SHA-256
   `cca758ec49d21877fd3921c43b5f90670fd5672e04ed5e5bd731b2792497390b`
   on two consecutive runs.
7. Cross-environment fixture output: SHA-256
   `c6cdb4b2d6e84c11a1d416039efb7125da06e058725f95287b46e8fa91dcff42`
   for both UTC/hash-seed 1 and Pacific-Kiritimati/hash-seed 98765; bytes are
   identical.
8. Final fixture evidence: suite SHA-256
   `b2f844822ca81b6d48874d409c084b8b2447f754286b881b497f974ec3a25d49`,
   policy SHA-256
   `21a22047626c39ea753cb69dc615caff79a396defa1e88ff9a654923f4b31fa6`,
   coverage-map SHA-256
   `c7c70db64ec35f364eddfd18e84647bff774e404bae30da2f486eac6a7d05abe`.

## Required role and provenance regressions

- Backend significant acceptance, material-review closure and publication
  candidate creation are rejected.
- Foreground and Human backend-completion impersonation are rejected.
- Human/foreground dispatch, backend completion, Human/foreground acceptance,
  correction loop and protected publication entry pass on valid role paths.
- Missing, wrong-provider, wrong-role, wrong-transition, wrong-event-digest,
  cross-event, replayed and forged-host actor-origin contexts are rejected.
- C2 authority with a wrong event digest or transplanted actor-origin context
  is rejected; valid trusted-host and deterministic test-boundary verifiers
  pass only within their declared trust modes.
- Earlier fabricated-result, stale-state, pointer, release, ledger and Human
  direct-routing attacks remain actually executed and covered.

## Boundary assertions

- Validation provenance is fresh repository evidence, not Human authority.
- Actor origin proves the exact originating channel and role, not currentness
  or C2 permission.
- `ActiveStateContext`, `ActorOriginContext` and `AuthorizationContext` are
  separately injected and cannot substitute for one another.
- A transition proof is not an execution lock; production hosts still require
  atomic state CAS and single-use context consumption.
- Repository validation does not intercept or activate arbitrary live
  UI/model output.

The final binding commit is additionally checked for binding/derived-only path
scope, receipt-required semantics-blob identity, source-mailbox `4/4` identity,
allowlist compliance, `git diff --check`, scoped secret scan, non-force remote
read-back and unchanged source/master head before the review pointer is sent.
