# Reproducible validation log

Regenerated after foreground rereview round 3.

**Executor evidence until independently reproduced.** A passing assertion proves
only its exact claim; a passing test proves only that the implementation matches
the executor's understanding of the contract. Neither is independent verification.

Paths are repository-relative. No learner store is read, and no path or alias
belonging to a learner appears in this file.

## Environment

```text
python  3.14.6
sympy   1.14.0
yaml    6.0.3
jsonschema4.26.0
pytest  9.1.1
platform Windows 10
```

## learning_state test suite

```text
$ python -m pytest tests -q
........................................................................ [ 59%]
.................................................                        [100%]
121 passed in 2.87s
exit_code=0
```

## Mode A audit: COMPLEX_ANALYSIS-417

```text
$ python COMPLEX_ANALYSIS-417.py
[PASS] from i = (0,1): applying M TWICE gives -i = (0,-1), NOT (-1,0)
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
[PASS] counterexample u_xx + u_yy + x*y*u = 0: dividing by X*Y leaves a coupling term whose mixed partial equals 1, contradicting any f(x)+g(y) split. Checked claim: 'no NONTRIVIAL Cartesian product solution X(x)Y(y) exists IN THESE COORDINATES'; this says nothing about other coordinate systems or the trivial solution u = 0
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

## Manual derivations (not machine-only)

Both are verified by hand here because each was previously stated incorrectly
while a machine check passed.

### 1. PDE non-separability counterexample

Claim: `u_xx + u_yy + x*y*u = 0` is linear and homogeneous, yet admits no
nontrivial product solution `X(x)Y(y)` **in these coordinates**.

1. Substitute `u = X(x)Y(y)`:  `X''Y + XY'' + x*y*X*Y = 0`.
2. Divide by the nonzero product `X*Y`:  `X''/X + Y''/Y = -x*y`.
3. The left side has the form `f(x) + g(y)`, so `d^2/dx dy` of it is `0`.
4. The right side gives `d^2/dx dy [-x*y] = -1`.
5. `0 = -1` is false. Hence no such nontrivial product solution exists. QED

Scope: this says nothing about the trivial solution `u = 0`, nor about
separation in a different coordinate system.

Why the earlier attempt was wrong: for `x*y*u_xx + u_yy = 0`, dividing by
`X*Y*y` gives `x*X''/X + Y''/(y*Y) = 0`, which IS separated. Inspecting only the
quotient by `X*Y` is insufficient, because one may first divide by a nonzero
factor. The audit's three rescaling checks sample that habit; they are NOT
exhaustive and are NOT part of the proof above.

### 2. Rotation sequences for i^2 = -1

Let `M(z) = i*z`, and identify `a+bi` with the point `(a, b)`.

- From `1 = (1,0)`:  `M` once gives `i = (0,1)`;  `M` twice gives `-1 = (-1,0)`.
  This demonstrates `i^2 * 1 = -1`.
- From `i = (0,1)`:  `M` once gives `i*i = -1 = (-1,0)`.
  This demonstrates `i * i = -1`.
- From `i = (0,1)`:  `M` **twice** gives `i^3 = -i = (0,-1)`, NOT `(-1,0)`.

An earlier `repair_direction` asserted the last case reached `(-1,0)`. It does
not. All three sequences are now pinned by audit assertions.
