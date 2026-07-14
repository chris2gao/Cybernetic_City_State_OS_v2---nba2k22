# ANALYTIC_NT Foundation Batch 1 Validation

## Outcome

Local validation passed for the four Human-approved business nodes and their bounded durable evidence. This result is deliberately narrower than a proof of any infinite-series, analytic-continuation, asymptotic, zero-free-region, randomness, cryptographic, or quantum-information statement.

## Executed checks

- Parsed all four touched business YAML files and every durable JSON/YAML artifact.
- Re-executed all four node-specific audit scripts from their committed-style input refs and regenerated their output/log refs.
- Ran `sandbox_evaluator.py` separately on all four nodes: 4 passed, 0 warnings, 0 failures. Its result wording explicitly says executable sanity is not mathematical correctness.
- Ran the repository's official teaching-flow static validator: 13 of 13 checks passed.
- Redirected only the validator result directory into the authorized program root; the validator source, schemas, prompts, and default tracked result files were not modified.
- Verified each `run_with_log` script, input, output, environment, and log ref resolves inside the authorized program directory.
- Verified every policy-required tool field is present and each declared UTC execution timestamp matches the node input, regenerated output/log, and source YAML.
- Verified all four nodes preserve identity and split-roadmap alias, use `Plan3_Engine_B`, Mode A, `MathLane_A`, and retain conservative manual certification status.
- Verified the source head is an ancestor and every candidate commit inspected at validation time has exactly one parent.
- Verified cumulative business scope is exactly the four approved YAML files and every other path is inside the single authorized program root.
- Final local scope snapshot contains 43 paths: exactly 4 approved business YAMLs and 39 paths under the authorized program root.
- Ran `git diff --check` and a scoped credential/secret-pattern scan over all 43 cumulative candidate paths; no suspicious filename or content pattern matched.

The official static validator is generic protocol-regression evidence over its existing prompt contracts and `TRIG-006` / `CALCULUS-265` fixtures. It does not inspect these four new nodes and is not used as direct proof that they are teaching-ready. Its output also contains a historical `repo_head_assumed` label; that label is not used as checkout evidence. The four node payloads are checked separately by the batch validator, while immutable base and candidate ancestry are checked independently with Git.

## Bounded audit results

| Node | Executed finite evidence | Result |
|---|---|---|
| `ANALYTIC_NT-684` | 11 declared count/step cases, full integer step scan through 10,000, and four declared `x/log x` table rows | passed |
| `ANALYTIC_NT-687` | 12 `chi4` values, 129 periodicity cases, 4,225 multiplicativity pairs, 4 unit-group pairs, four exact rational partial sums, and a 10,000-term Catalan comparison with an explicit remainder budget | passed |
| `ANALYTIC_NT-688` | 5 root-of-unity cases, 4 geometric identities, 3 triangle-bound cases, and 5 edge cases under `e(t)=exp(2*pi*i*t)` | passed |
| `ANALYTIC_NT-692` | 4 finite Dirichlet-polynomial product/convolution cases at declared real and complex inputs | passed |

## Independent review

A separate read-only reviewer initially found two material evidence issues: missing/unbound execution timestamps and imprecise `ANALYTIC_NT-687` partial-support/blocker structure. The candidate now binds every execution timestamp across input, regenerated output/log, and source YAML; moves `n_472/n_473/n_277/n_431` into `partial_support_only`; and enumerates exact Stage 6 blocker IDs and statuses. The same reviewer rechecked the fixes, closed both findings, and reported no new issue.

## Durable evidence

- Batch result: `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/OUTPUTS/batch-validation.json`
- Batch log: `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/LOGS/batch-validation.log`
- Teaching-flow result: `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/OUTPUTS/teaching-flow-static/teaching_flow_static_validation_result.json`
- Teaching-flow log: `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/LOGS/teaching-flow-static-validator.log`
- Per-node input, output, environment, script, and log refs are declared directly in each source node.

## Forbidden-side-effect check

No bridge, roadmap, index, schema, prompt, evaluator, runtime, Coordinator, scheduler, learned-history, student-state, neighboring-node, secret, or credential path was changed. P3 remained closed. No remote operation occurred during the local-only execution interval.
