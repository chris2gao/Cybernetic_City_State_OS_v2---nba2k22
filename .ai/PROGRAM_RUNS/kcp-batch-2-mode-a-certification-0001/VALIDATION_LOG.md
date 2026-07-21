# Reproducible validation log

Regenerated after foreground rereview round 7, then after metadata closure.

## Metadata closure (final pre-merge pass)

No implementation, test, audit, schema, node or scanner code was touched in this
pass. Only report front matter, this log, and `epoch.yml` activation metadata
were aligned with the completed foreground review.

- Path-count drift happened twice; both are recorded rather than smoothed over.
  The privacy-evidence commit modified two files already inside the round-7 set,
  so the total stayed **14** at that point — it is not "14 plus 2". This
  metadata-closure commit then added `epoch.yml`, which was **not** in that set,
  so `faf7dd3..HEAD` is now **15 distinct paths** (14 remediation + `epoch.yml`).
  The dispatch asked for the wording "14" and for an `epoch.yml` edit in the same
  pass; those are mutually exclusive, and the measured value governs.
- `implementation_foreground_accepted: true` and `independently_accepted: true`
  now record acceptance of the IMPLEMENTATION only, with the scope spelled out in
  `epoch.yml`. Test and audit numbers below remain executor evidence.
- `release_status` stays `pre_release_unfrozen`, `production_authorized`,
  `scheduler_writer_activated` and `real_v2_write_performed` stay `false`.
- Post-edit privacy re-scan on the committed HEAD: 0 / 0 / 0, exit 0.
- The external denylist file was deleted locally after the final scan; its values
  were never printed, echoed or committed.
- No history was rewritten and master was not touched.

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
........................................................................ [ 28%]
........................................................................ [ 56%]
........................................................................ [ 85%]
......................................                                   [100%]
254 passed in 13.16s
exit_code=0
```

Round 7 added 40 tests (214 -> 254) across four new files:

| file | covers |
| --- | --- |
| `test_r7_acceptance_timestamps.py` | every accepted reducer branch advances `last_event_timestamp` |
| `test_r7_attempt_occurred_schema.py` | `attempt_occurred` conditionals, canonical schema AND writer path |
| `test_r7_privacy_output.py` | denylist terms never reach stdout/stderr, including filename hits |
| `test_r7_descriptions_and_api.py` | corrected epoch/hash-chain wording, `write_snapshot` signature |

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

### Round-7 output-confidentiality repair

The scanner printed RAW paths. A denylist term can appear in a tracked FILENAME,
so a filename hit published the term itself into a log written for committing -
the scan defeated its own purpose. The round-6 test that asserted "denylist
values are never printed" used a content-only term, so it never exercised the
filename case.

Printed paths now have every denylist match replaced by `[REDACTED]` and carry a
`sha256` prefix of the original path for cross-run correlation. `--reveal-paths`
prints raw paths for local diagnosis, is never the default, and marks its own
output non-committable on stderr. `--repo-root` was added so the filename case
can be tested against a synthetic throwaway repository instead of by planting a
learner-shaped term in this one.

### Denylist provenance: derived from known residue, NOT Human-supplied

The Human-supplied external denylist was unavailable. Rather than substitute
synthetic terms — which would have produced a `0/0/0` that says nothing — the
terms were **derived from the residue the round-6 scan had already located**, by
extracting identifier tokens from the one master file it named. The values were
never printed, echoed, committed, or written anywhere inside the repository.

Extraction is a heuristic and its first output proved it: of three candidate
tokens, one was a 22-character repository directory component that matched
10,708 lines on master and 10,712 on the clean branch. Being present everywhere
in both trees is what identified it as a path fragment rather than an identifier,
and it was dropped. The surviving two behave the way a real residue identifier
must:

| term | master content hits | clean-branch content hits | reading |
| --- | ---: | ---: | --- |
| candidate A (4 chars) | 1 | 0 | residue identifier |
| candidate B (4 chars) | 1 | 0 | residue identifier |
| rejected (22 chars) | 10708 | 10712 | repository path component |

Two terms, two master hits, one master file — this reproduces the round-6 result
(`denylist_terms: 2`, `content_matching_lines: 2`, `files_with_hits: 1`) exactly,
which is the reason to believe the derivation recovered the terms round 6 used.

**Completeness was not verifiable by the executor.** This method can only recover
identifiers that appear in that one file; an alias that never reached it would be
neither in the denylist nor scanned for. At execution time this was therefore
recorded as verification against known residue, explicitly *not* privacy closure.

**Foreground subsequently attested completeness** (metadata-closure round): the
two identifier classes on record for this task are the complete set, and no
additional aliases were authorized. That attestation is the part only a Human can
supply, and with it the scope closes: the clean integration branch is
`closed_for_declared_identifier_scope`. No claim is made about unknown aliases
outside the task record, and reachable history remains unresolved.

### Round-7 scans with the derived denylist

```text
$ python privacy_scan.py HEAD --denylist-file <path outside the repository>
scan_scope: tracked content and paths at ref 'HEAD'
denylist_terms: 2 (values not printed by design)
content_matching_lines: 0
filename_hits: 0
scan_errors: 0
files_with_hits: 0
path_disclosure: redacted+fingerprint
exit_code=0

$ python privacy_scan.py master --denylist-file <path outside the repository>
scan_scope: tracked content and paths at ref 'master'
denylist_terms: 2 (values not printed by design)
content_matching_lines: 2
filename_hits: 0
scan_errors: 0
files_with_hits: 1
path_disclosure: redacted+fingerprint
  <redacted>  (sha256:16a4e8b1e1f4)
exit_code=1
```

`--reveal-paths` was not used. The one master hit is recorded by opaque
fingerprint only; it is the same file round 6 identified.

| scope | result | basis |
| --- | --- | --- |
| `clean_branch_content_hits` | **0** | scan above, derived denylist |
| `clean_branch_filename_hits` | **0** | scan above |
| `scan_errors` | **0** | both scans completed |
| `pre_merge_master_tree_hits` | 2 lines in 1 file | scan above, exit 1 |
| `reachable_history_not_clean` | **true** | unchanged by this task |

The numbers above are the **pre-merge** state. See the post-merge section below
for the current one: the merge carried the redaction into master, so the master
current tree is now clean and only reachable history still holds the residue.

## Post-merge state (master 0b34f75)

The remediation was merged into master under Human authorization as a normal,
non-force merge (`ceb5e6c → 0b34f75`, no squash, no history rewrite).

```text
$ python privacy_scan.py origin/master --denylist-file <path outside the repository>
scan_scope: tracked content and paths at ref 'origin/master'
denylist_terms: 2 (values not printed by design)
content_matching_lines: 0
filename_hits: 0
scan_errors: 0
files_with_hits: 0
path_disclosure: redacted+fingerprint
exit_code=0
```

| scope | result |
| --- | --- |
| `master_current_tree_hits` | **0 / 0 / 0**, exit 0 |
| `master_current_tree_status` | `closed_for_declared_identifier_scope` |
| `reachable_history_not_clean` | **true**, unchanged |
| `history_rewritten` | **false** |

Two statements that must never be collapsed into one:

- **current trees are clean** — the clean integration branch and, since the
  merge, master itself;
- **reachable history is not** — the pre-merge commits still hold the residue,
  the merge neither touched nor should touch them.

**No claim of a clean history is made.** Cleaning it is destructive, needs a
separate Human decision, and the current policy is
`retain_private_history_for_now`.

### No learner store was touched

```text
$ git ls-files 08_Domain_Applications/Math_Mentor/learners | wc -l
0
$ git ls-files "*STUDENT_LEARNING_STATE/*" "*LEARNED_HISTORY/*" | wc -l
0
```

Every store used by the tests is a synthetic temporary directory.

## Summary

| check | exit code | ref scanned | when |
| --- | --- | --- | --- |
| tests (254) | 0 | working tree | current |
| ca417 (20 assertions) | 0 | working tree | current |
| pde486 (26 assertions) | 0 | working tree | current |
| parse | 0 | working tree | current |
| privacy_clean_branch (derived denylist) | 0 | `...-clean` | pre-merge |
| privacy_master_pre_merge (derived denylist) | 1 | `master` @ `ceb5e6c` | **pre-merge** |
| **privacy_master_current** (derived denylist) | **0** | `origin/master` @ merged head | **current** |

The two master rows are different measurements and must not be read as one:

- `privacy_master_pre_merge` exited 1 **by design** — the scan completed and found
  the residue that master carried before the merge. That row is history now.
- `privacy_master_current` exits 0: the merge carried the clean branch's redaction
  into master, so the master **current tree** holds none of the declared
  identifiers. This is the row that describes master today.

Neither row says anything about reachable history, which still contains the
pre-merge residue and was deliberately not rewritten. `privacy_clean_branch`
exiting 0 means that branch contains none of the identifiers known to have
leaked; completeness of the identifier set rests on the foreground attestation,
not on the scan.

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
