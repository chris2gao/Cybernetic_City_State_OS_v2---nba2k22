# Reproducible validation log

Regenerated after foreground rereview round 6.

**Executor evidence until independently reproduced.** A passing assertion proves
only its exact claim; a passing test proves only that the implementation matches
the executor's understanding of the contract. The tests below are executor
evidence and are NOT independently reproduced.

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
........................................................................ [ 33%]
........................................................................ [ 67%]
......................................................................   [100%]
214 passed in 11.30s
exit_code=0
```

## Mode A audit: COMPLEX_ANALYSIS-417

```text
$ python COMPLEX_ANALYSIS-417.py
[PASS] multiplying by 2i scales modulus by 2, so it is not a pure rotation
[PASS] multiplying by 0 collapses every z to 0, so the rotate-and-scale reading requires a nonzero multiplier
[PASS] library behaviour: SymPy evaluates arg(0) to nan (NOT a proof of undefinedness; the undefinedness of arg(0) is a semantic boundary, not a machine result)
TOTAL 20 assertions, all passed
exit_code=0
```

## Mode A audit: PDE-486

```text
$ python PDE-486.py
[PASS] sampled rescaling: dividing by X*Y*x (not multiplying by it) still leaves a nonzero mixed partial; sampled evidence only, not exhaustive
[PASS] sampled rescaling: dividing by X*Y*x*y (not multiplying by it) still leaves a nonzero mixed partial; sampled evidence only, not exhaustive
[PASS] a non-eigenfunction (x) fails the Dirichlet condition at x=L, so not every smooth function is an eigenfunction
TOTAL 26 assertions, all passed
exit_code=0
```

## node YAML parse check

```text
$ python -c "import yaml;[yaml.safe_load(open(p,encoding='utf-8')) for p in ['COMPLEX_ANALYSIS-417.yaml','PDE-486.yaml']];print('both node files parse')"
both node files parse
exit_code=0
```

## Privacy scan

Denylist values are supplied externally and never stored here or printed:
publishing the aliases we are keeping out would defeat the scan. The scan covers
both file CONTENT and tracked file PATHS, verifies the ref first, and treats any
git failure as exit 2 - an unverifiable scan is never reported as clean.

```text
$ LEARNER_DENYLIST=<supplied externally> python privacy_scan.py HEAD
$ LEARNER_DENYLIST=<supplied externally> python privacy_scan.py master
```

## privacy scan: current dev tree

```text
$ python privacy_scan.py HEAD
scan_scope: tracked content and paths at ref 'HEAD'
denylist_terms: 2 (values not printed by design)
content_matching_lines: 0
filename_hits: 0
scan_errors: 0
files_with_hits: 0
exit_code=0
```

## privacy scan: master

```text
$ python privacy_scan.py master
scan_scope: tracked content and paths at ref 'master'
denylist_terms: 2 (values not printed by design)
content_matching_lines: 2
filename_hits: 0
scan_errors: 0
files_with_hits: 1
  .ai/CODEX_REPORTS/independent-review-request-0001.md
exit_code=1
```

| scope | result |
| --- | --- |
| `current_dev_tree_hits` | 0 |
| `current_master_tree_hits` | nonzero (path listed above) |
| `scan_errors` | 0 |
| `reachable_history_not_clean` | **true** |

Reachable Git history and current master still contain learner-bound metadata.
This task does not rewrite history, force push, or alter master, so the residue
remains. Cleaning it is destructive and needs a separate Human gate.
**No claim of a clean history is made.** `privacy_master` exits 1 by design.

## Summary

| check | exit code |
| --- | --- |
| tests | 0 |
| ca417 | 0 |
| pde486 | 0 |
| parse | 0 |
| privacy_dev | 0 |
| privacy_master | 1 |

## Claim-to-evidence inventory (task-scoped anti-drift artifact)

Classification:

- `machine_checked` - a SymPy assertion covers exactly this claim;
- `machine_checked (node code executed)` - the audit loads the node YAML and runs
  its own `code_implementation` text, so the node's code is what was checked;
- `machine_checked (sampled)` - specific values were substituted; NEVER evidence
  for a general theorem;
- `manual_derivation` - verified by hand in this log;
- `semantic_review_only` - accepted by foreground review, no machine evidence.

### COMPLEX_ANALYSIS-417

| claim | class | evidence |
| --- | --- | --- |
| ordered-pair construction; `a+bi` is notation | `semantic_review_only` | accepted, foreground rereview 5 |
| `M(z)=iz` sends `a+bi` to `-b+ai` | `machine_checked` | audit assertion |
| `M` is R-linear | `machine_checked` | audit assertion |
| matrix `[[0,-1],[1,0]]`, det 1, modulus preserved | `machine_checked` | audit assertions |
| `i^4 = 1` returns every point | `machine_checked` | audit assertion |
| from (1,0), M twice -> (-1,0) | `machine_checked` | rotation-sequence assertion 1 |
| from (0,1), M once -> (-1,0) | `machine_checked` | rotation-sequence assertion 2 |
| from (0,1), M twice -> (0,-1), NOT (-1,0) | `machine_checked` | rotation-sequence assertion 3 |
| multiplying by 2i scales by 2 | `machine_checked` | audit assertion |
| zero multiplier is neither rotation nor scaling | `machine_checked` | audit assertion |
| `arg(0)` is undefined | `semantic_review_only` | audit records SymPy nan as LIBRARY BEHAVIOUR only |
| representation is not ontology | `semantic_review_only` | no machine evidence by construction |
| basis/orientation dependence | `semantic_review_only` | stated, not asserted |
| sub_topic 4 (representation / observable boundary) | `semantic_review_only` | declared to carry no machine evidence |
| assertions_passed = 20 | `machine_checked` | log TOTAL line |

### PDE-486

| claim | class | evidence |
| --- | --- | --- |
| regular Sturm-Liouville statement | `semantic_review_only` | cited theorem |
| eigenpairs satisfy the ODE | `machine_checked` | assertions n=1,2,3 |
| eigenfunctions satisfy the Dirichlet conditions | `machine_checked` | audit assertions |
| pairwise orthogonality for the listed pairs | `machine_checked` | pairs (1,2),(1,3),(2,3),(2,4) |
| orthogonality at sampled pairs (2,5) and (3,7) | `machine_checked (sampled)` | those two pairs substituted |
| GENERAL sine orthogonality theorem for all integer n != m | `semantic_review_only` | NOT machine-checked; only the two pairs above |
| `||y_n||^2 = L/2` | `machine_checked` | audit assertions |
| separation identity | `machine_checked` | audit assertion |
| linear+homogeneous does NOT imply separable | `manual_derivation` | mixed-partial contradiction below; the audit asserts the mixed partial equals 1 |
| counterexample scope: nontrivial Cartesian product solutions, these coordinates | `semantic_review_only` | scope stated in node and assertion text |
| rescaling by x, y, x*y does not remove the coupling | `machine_checked (sampled)` | three sampled rescaling checks; non-exhaustive, not part of the proof |
| two-mode superposition solves the PDE and the BCs | `machine_checked` | audit assertions |
| orthogonality recovers coefficients 3 and -5 | `machine_checked` | audit assertion |
| node `code_implementation` satisfies the wave equation | `machine_checked (node code executed)` | audit loads PDE-486.yaml and executes that exact text in an isolated namespace (round 6) |
| node `code_implementation` gives u(0,t)=u(L,t)=0 exactly | `machine_checked (node code executed)` | same executed snippet; exact symbolic zero, not a float tolerance |
| `A_n`, `B_n` formulas for initial data f, g | `semantic_review_only` | stated; only the finite-combination case is asserted |
| L2 convergence and completeness | `semantic_review_only` | cited theorems |
| pointwise/uniform claims need more smoothness | `semantic_review_only` | stated boundary |
| linearity required for superposition, not for separated existence | `semantic_review_only` | accepted wording |
| assertions_passed = 26 | `machine_checked` | log TOTAL line |

Round 6 correction: an earlier entry called a separately written SymPy function
"the node snippet". It was a reimplementation, so it evidenced nothing about the
node. The audit now executes the node's own text, and the class name says so.

## Manual derivations

### 1. PDE non-separability counterexample

Claim: `u_xx + u_yy + x*y*u = 0` is linear and homogeneous, yet admits no
nontrivial product solution `X(x)Y(y)` **in these coordinates**.

1. Substitute `u = X(x)Y(y)`:  `X''Y + XY'' + x*y*X*Y = 0`.
2. Divide by the nonzero product `X*Y`:  `X''/X + Y''/Y = -x*y`.
3. The left side has the form `f(x) + g(y)`, so `d^2/dx dy` of it is `0`.
4. The right side gives `d^2/dx dy [-x*y] = -1`.
5. `0 = -1` is false. Hence no such nontrivial product solution exists. QED

Scope: silent about the trivial solution `u = 0` and about other coordinate
systems. The three rescaling checks are sampled and NOT part of this proof.

### 2. Rotation sequences for i^2 = -1

Let `M(z) = i*z`, identifying `a+bi` with `(a, b)`.

- From `1 = (1,0)`:  once -> `i = (0,1)`;  twice -> `-1 = (-1,0)`.  [`i^2 * 1 = -1`]
- From `i = (0,1)`:  once -> `-1 = (-1,0)`.                        [`i * i = -1`]
- From `i = (0,1)`:  twice -> `i^3 = -i = (0,-1)`, NOT `(-1,0)`.
