# Reproducible validation log

Regenerated after foreground rereview round 4.

**Executor evidence until independently reproduced.** A passing assertion proves
only its exact claim; a passing test proves only that the implementation matches
the executor's understanding of the contract.

Paths are repository-relative. No learner store is read, and no learner alias or
local learner path appears in this file.

## Environment

```text
python  3.14.6
sympy      1.14.0
yaml       6.0.3
jsonschema 4.26.0
pytest     9.1.1
platform Windows 10
```

## learning_state test suite

```text
$ python -m pytest tests -q
........................................................................ [ 47%]
........................................................................ [ 95%]
.......                                                                  [100%]
151 passed in 3.11s
exit_code=0
```

## Mode A audit: COMPLEX_ANALYSIS-417

```text
$ python COMPLEX_ANALYSIS-417.py
[PASS] the map M(z) = i*z is R-linear: M(c1 z1 + c2 z2) == c1 M(z1) + c2 M(z2)
[PASS] multiplying by 2i scales modulus by 2, so it is not a pure rotation
[PASS] multiplying by 0 collapses every z to 0, so the rotate-and-scale reading requires a nonzero multiplier
[PASS] library behaviour: SymPy evaluates arg(0) to nan (NOT a proof of undefinedness; the undefinedness of arg(0) is a semantic boundary, not a machine result)
TOTAL 20 assertions, all passed
exit_code=0
```

## Mode A audit: PDE-486

```text
$ python PDE-486.py
[PASS] sampled rescaling: dividing by X*Y*y (not multiplying by it) still leaves a nonzero mixed partial; sampled evidence only, not exhaustive
[PASS] sampled rescaling: dividing by X*Y*x (not multiplying by it) still leaves a nonzero mixed partial; sampled evidence only, not exhaustive
[PASS] sampled rescaling: dividing by X*Y*x*y (not multiplying by it) still leaves a nonzero mixed partial; sampled evidence only, not exhaustive
[PASS] a non-eigenfunction (x) fails the Dirichlet condition at x=L, so not every smooth function is an eigenfunction
TOTAL 24 assertions, all passed
exit_code=0
```

## node YAML parse check

```text
$ python -c "import yaml;[yaml.safe_load(open(p,encoding='utf-8')) for p in ['COMPLEX_ANALYSIS-417.yaml','PDE-486.yaml']];print('both node files parse')"
both node files parse
exit_code=0
```

## Summary

| check | exit code |
| --- | --- |
| tests | 0 |
| ca417 | 0 |
| pde486 | 0 |
| parse | 0 |

## Claim-to-evidence inventory (task-scoped anti-drift artifact)

Scope: the two Mode A nodes in this run. This is not a new global schema; it
exists because claims drifted from evidence across earlier rounds.

Classification: `machine_checked` | `manual_derivation` | `semantic_review_only`.

### COMPLEX_ANALYSIS-417

| claim | class | evidence |
| --- | --- | --- |
| pure_math_definition: ordered-pair construction; `a+bi` is notation | `semantic_review_only` | no assertion; reviewer accepted round 4 |
| pure_math_definition: `M(z)=iz` sends `a+bi` to `-b+ai` | `machine_checked` | audit: `i*(a+bi) == -b + a*i` |
| pure_math_definition: `M` is R-linear | `machine_checked` | audit: R-linearity assertion |
| pure_math_definition: matrix `[[0,-1],[1,0]]`, det 1, modulus preserved | `machine_checked` | audit: rotation-matrix, det, modulus assertions |
| pure_math_definition: `i^4 = 1` returns every point | `machine_checked` | audit: `i**4 * z == z` |
| misconception `i_squared_treated_as_paradox`: (1,0) twice -> (-1,0) | `machine_checked` | audit: rotation-sequence assertion 1 |
| misconception: (0,1) once -> (-1,0) | `machine_checked` | audit: rotation-sequence assertion 2 |
| misconception: (0,1) twice -> (0,-1), NOT (-1,0) | `machine_checked` | audit: rotation-sequence assertion 3 |
| misconception `rotation_generalized_to_all_multiplication` | `machine_checked` | audit: `|2i z| == 2|z|` |
| invalid_inference: zero multiplier is neither rotation nor scaling | `machine_checked` | audit: `0*z == 0` |
| invalid_inference: `arg(0)` undefined | `semantic_review_only` | audit records SymPy returning nan as LIBRARY BEHAVIOUR only |
| invalid_inference: representation is not ontology; not directly observable | `semantic_review_only` | no machine evidence by construction |
| invalid_inference: basis/orientation dependence | `semantic_review_only` | stated, not asserted |
| sub_topic 4 (representation / observable boundary) | `semantic_review_only` | explicitly declared to carry no machine evidence |
| spaced_review_handoff wording (map, not the number) | `semantic_review_only` | wording aligned round 4 |
| tool_truthfulness.assertions_passed = 20 | `machine_checked` | log TOTAL line; corrected from 17 in round 4 |

### PDE-486

| claim | class | evidence |
| --- | --- | --- |
| regular Sturm-Liouville statement with regularity and self-adjoint BCs | `semantic_review_only` | cited; not asserted |
| eigenpairs `sin(n pi x/L)`, `lambda_n=(n pi/L)^2` satisfy the ODE | `machine_checked` | audit: eigenpair assertions n=1,2,3 |
| eigenfunctions satisfy the Dirichlet conditions | `machine_checked` | audit: boundary assertions |
| pairwise orthogonality on [0,L] | `machine_checked` | audit: pairs (1,2),(1,3),(2,3),(2,4) |
| orthogonality for general integer n != m | `machine_checked (sampled)` | audit: sampled pairs (2,5),(3,7); explicitly NOT a general symbolic proof |
| `||y_n||^2 = L/2` | `machine_checked` | audit: norm assertions |
| separation identity `T''/(c^2 T) - X''/X == 0` | `machine_checked` | audit: separation assertion |
| linear+homogeneous does NOT imply separable | `manual_derivation` | mixed-partial contradiction below; audit asserts the mixed partial equals 1 |
| counterexample scope: nontrivial Cartesian product solutions, these coordinates | `semantic_review_only` | scope stated in node and audit claim text |
| rescaling by x, y, x*y does not remove the coupling | `machine_checked (sampled)` | audit: three SAMPLED RESCALING CHECKS; non-exhaustive, not part of the proof |
| two-mode superposition solves the PDE and the BCs | `machine_checked` | audit: superposition assertions |
| orthogonality recovers coefficients 3 and -5 | `machine_checked` | audit: coefficient-recovery assertion |
| `A_n`, `B_n` formulas for initial data f, g | `semantic_review_only` | stated; only the finite-combination case is asserted |
| L2 convergence and completeness | `semantic_review_only` | explicitly cited theorems, not machine-checked |
| pointwise/uniform claims need more smoothness | `semantic_review_only` | stated boundary |
| linearity required for superposition, not for separated existence | `semantic_review_only` | wording aligned round 4 |
| tool_truthfulness.assertions_passed = 24 | `machine_checked` | log TOTAL line |

## Manual derivations

Verified by hand because each was previously stated incorrectly while a machine
check passed.

### 1. PDE non-separability counterexample

Claim: `u_xx + u_yy + x*y*u = 0` is linear and homogeneous, yet admits no
nontrivial product solution `X(x)Y(y)` **in these coordinates**.

1. Substitute `u = X(x)Y(y)`:  `X''Y + XY'' + x*y*X*Y = 0`.
2. Divide by the nonzero product `X*Y`:  `X''/X + Y''/Y = -x*y`.
3. The left side has the form `f(x) + g(y)`, so `d^2/dx dy` of it is `0`.
4. The right side gives `d^2/dx dy [-x*y] = -1`.
5. `0 = -1` is false. Hence no such nontrivial product solution exists. QED

Scope: silent about the trivial solution `u = 0` and about other coordinate
systems. The three rescaling checks in the audit are sampled, non-exhaustive,
and NOT part of this proof.

Why the earlier attempt failed: for `x*y*u_xx + u_yy = 0`, dividing by `X*Y*y`
gives `x*X''/X + Y''/(y*Y) = 0`, which IS separated.

### 2. Rotation sequences for i^2 = -1

Let `M(z) = i*z`, identifying `a+bi` with `(a, b)`.

- From `1 = (1,0)`:  once -> `i = (0,1)`;  twice -> `-1 = (-1,0)`.  [`i^2 * 1 = -1`]
- From `i = (0,1)`:  once -> `-1 = (-1,0)`.                        [`i * i = -1`]
- From `i = (0,1)`:  twice -> `i^3 = -i = (0,-1)`, NOT `(-1,0)`.

An earlier repair_direction asserted the last case reached `(-1,0)`. All three
are now pinned by audit assertions.
