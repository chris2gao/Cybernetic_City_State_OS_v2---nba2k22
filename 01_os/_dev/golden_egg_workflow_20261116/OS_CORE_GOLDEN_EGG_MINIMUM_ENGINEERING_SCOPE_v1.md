# Core OS · Golden Egg Workflow Stage 04/05 · Minimum engineering boundary

**Status:** planning/test candidate, not an executable authorization, Human freeze receipt, complete official Stage04 artifact, or merge approval.

**Fixed source versions**
- Core master `043ac4864bdc871b03929faafd8bc6bd47d4ee2f`
- Core PR #23 reference implementation `6d97d2d3e2527f38e688998e9b8de03553046dbe` (Draft, not merged)
- GE-01 audit SHA256 `12011e2f6d4c62f7d09f89958de3b70ccc7e494982adf713cf98f3de25f72586`
- Private GE-01 events SHA256 `d29351fdd8c7e6143ba41d640c7fa09122a3c47a0540421bbe321634e0298db9`
- Candidate tests (local JSON canonicalization for reviewer comparison **only**): `0b27dbbde8c72bf4a697580f8fd04a713a0c40493729a5253a9a6979f03e1561`. Not the official Core normalized test SHA.

## Tests first

`OS_CORE_GOLDEN_EGG_STAGE04_TEST_CANDIDATE_v1.yml` contains **15 evidence-linked scenarios**: 8 P0 invariants (authorization, no replay, reuse, authentic Done, freeze), 4 P1 path decisions (early decisive check, local tool fallback, stop/reuse, bounded recovery), 3 P2 timing/comparability scenarios. Tests T01–T14 are primarily deterministic/synthetic with private GE-01 trace for provenance; T15 is a later authorized observational experiment. Human or a reviewer independent of B design must judge the test semantics before official freeze.

## Smallest necessary changes, in order

1. **Reuse/reference PR #23 selectively.** Keep `Atom`, `Chain`, `Ready`, `Done` semantics and single-instance no-blind-replay. Do not merge the whole Draft PR or create a generic workflow runtime merely because it exists. Review the actual needed diff against current master.
2. **Stage 05:** encode the Human-approved business chain as nodes with minimum Ready dependencies, source provenance/validity conditions, business-identity stability, independent domain Done, and blockers; do not generate per-tool nodes or a second task registry. Prefer existing stage05 steps; any schema changes require explicit negative tests and compatibility analysis.
3. **Stage 06:** given observable facts, select the first safe, high-value ready action or decisive preflight that can unblock it. Cache only within validity scope. When a fact changes, invalidate dependent facts, not unrelated approved choices. Prefer known working tools; require bounded, evidence-producing fallback; honor actual authorization and UNKNOWN.
4. **Stage 07:** require real business evidence and independent existing review boundary; report time quality from source facts without turning duration into a new pass/fail gate. Preserve frozen-test hashes and existing reviewer-role restrictions.
5. **Validate incrementally:** run the current Core tests unchanged; add T01–T14 as bounded tests; demonstrate T01/T02/T09 *fail against a deliberately naive model/fixture or an actual pre-fix behavior*, then pass after change. Keep T15 as later outcome experiment rather than pass by synthetic simulation.

## Do not change

No NBA2K22 game or Calendar repair; no native setters/Calendar dispatch/WorldData refresh; no master merge under this design task; no modifications to PR #34 factmon; no new telemetry/approval/control platform; no independent-review-per-step ceremony; no hard timing limit that bypasses safety or scope.

## Evidence requirements for implementation close

- Before/after behavior of the same input scenarios with exact test names and results
- Existing stage04 frozen test SHA preserved under attempted execution edit
- No unauthorized write, no replay of UNKNOWN, approved assignment preserved on rebind
- Evidence of actual Stage05/06 selection (not merely a README claim)
- True time sources and UNKNOWN gaps, no wall-time fabrication
- Deliberately retained red/unknown scenarios clearly reported

## Formal freeze status

As of drafting: `CANDIDATE_NOT_FROZEN`. To reach an official `frozen_test_package`, obtain independently judged semantics and actual Human freeze receipt; write governed Stage01/02/03/04 artifacts under an authorized Core Run; bind precise hashes with existing runner. The Human's instruction to **develop Stage04 design** is not a fabricated signature for a later formal freeze artifact. Once frozen, any test-content revision follows the governed upstream invalidation path, never a quiet edit inside the development loop.
