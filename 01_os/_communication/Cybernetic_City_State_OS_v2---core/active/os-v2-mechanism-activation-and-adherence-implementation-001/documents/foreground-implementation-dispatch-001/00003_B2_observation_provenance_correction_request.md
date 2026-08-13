---
document_id: os-v2-mechanism-activation-and-adherence-implementation-001-b2-observation-provenance-correction-001
task_id: os-v2-mechanism-activation-and-adherence-implementation-001
author_endpoint_id: foreground-implementation-dispatch-001
author_task_role: foreground_implementation_dispatch
purpose: bounded_B2_observation_provenance_binding_correction
privacy_class: repository_shareable
---
# B2 observation-provenance binding correction

## Accepted blocker

Fresh independent implementation acceptance of candidate `8fa49cc3a7eb082d4ffcee984652b77080d1b9f9` returned `FIX_REQUIRED` for one material blocker: `B2-OBSERVATION-PROVENANCE-BINDING`.

Exact reviewer evidence:
`58078dbf8100dd54f0f0bed1ad0f31eada71b163:01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/09_独立实现验收/isolated-gpt-implementation-reviewer-001/00001_acceptance_result.yml`

Foreground adjudication:
`27ebb7d7ee415d51659607b07bebfc1d2428e417:01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/10_FIX_REQUIRED修正/独立实现验收接收与B2修正裁决_v1.yml`

## Required correction

Do not reopen architecture A/B. Correct only the implementation gap where generic material-claim verification can return `VERIFIED` from claim-supplied expected/observed values without independently obtaining the cited expected source and physical observation.

Required behavior:

1. Reproduce the reviewer counterexamples before changing code.
2. Introduce an acceptance-time trusted observation boundary: either trusted observation adapters or an externally supplied observation context that independently resolves expected-source facts and observed physical facts.
3. `expected_claim_source_ref` must be resolved/consumed for material acceptance; a syntactically non-empty ref is insufficient.
4. `exact_observation_ref` must be resolved/consumed by the appropriate trusted source adapter/context; a syntactically non-empty ref and allowed source-class string are insufficient.
5. Receipt-provided source labels, observed values, completeness flags, actor values, hashes, or SHAs cannot establish their own provenance.
6. Missing/unresolvable expected source, missing/unconsumed observation, source-class/ref mismatch, or observation/context mismatch must produce `UNVERIFIABLE` or another fail-closed non-PASS result.
7. Preserve explicit comparator semantics and aggregate fail-closed behavior.
8. Add negative tests at least for:
   - non-resolving expected source ref with self-consistent candidate values;
   - asserted complete diff/path scope without a consumed complete Git compare;
   - asserted authenticated principal without a consumed authenticated-principal observation;
   - observation ref/source-class mismatch;
   - correct-looking observed value supplied only by receipt prose/data.
9. Re-run existing regression suites for A, communication v2, model routing, Stage04 frozen full/mutation, and default repository gates.
10. Freeze a new exact candidate and publish commit-bound evidence for a fresh independent acceptance. Do not reuse `8fa49cc3...` as the corrected candidate.

## Preserved constraints

- Stay inside the existing Human-authorized task boundary.
- Do not modify `01_os/01_workflow/**`.
- Do not modify frozen T2/Stage04 correction runs.
- Do not change reviewed A or B architecture semantics; this is implementation closure of B2.
- Do not publish or merge master.
- No automatic delivery, polling, acknowledgement, scheduling, or task progression.
- No rebase, amend, squash, force push, or history rewrite.

## Model / effort policy

Use `GPT-5.6 Sol` with **High** reasoning by default. `Max` is not authorized as whole-task default; escalate only if a concrete localized blocker fails to converge under High, and return to High after that blocker.

## Completion

Return a pointer-contract-v2 correction/result pointing to the new exact corrected candidate and its commit-bound evidence. Fresh independent implementation acceptance remains mandatory before any L4/operationally-active or master publication claim.
