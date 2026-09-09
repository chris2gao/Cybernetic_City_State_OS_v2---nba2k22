# Semantic convergence: construction evidence, 2026-09-08

Implementation parent: `b0473587877d1dfca445a92ed5429f71202c7314`.
Fresh remote master: `3dc058a1a3cf393b936025f43fd737b0848937b4`.
No frozen receipts/phase1 source was merged or changed. The Human-confirmed exact
scope amendment preceded body edits. This document is construction evidence,
not independent acceptance or a result for a future commit.

## Implemented changes

- Current method/profile/INV-12 text no longer imposes fixed full/incremental
  round minimums or new per-stage consent for already covered ordinary work.
- Both production `instance` CLIs require an explicit exact candidate/repository
  and immutable task packet/action binding; there is no implicit legacy fallback.
- Common and all seven stage-specific model obligations, typed receipt,
  unresolved/unknown handling and protected-action confirmation remain required.
- Covered decisions bind task packet/action/decision identity; new explicit
  decisions resolve candidate Git records. Bare actor labels/ref strings fail.
- Completion declarations use a separate evidence commit to avoid embedding a
  candidate's SHA into its own tree. This binds a claim, not an author identity,
  independent review or the truth of a test report.
- Eight current exact-ref consumers were updated from final target bytes: six
  references in boot and four in each of seven workflow wrappers, 34 total.
  Activation state and its global Human authorization were not changed.

## Actual construction checks

External evidence root:
`E:/newStand/_scratch_work/os-foundation-evidence-20260907/`

| Record | Actual result | Scope/limit |
| --- | --- | --- |
| `semantic-tests-001-initial.log` | 107 passed | Initial tests before stronger boundary probes; not final evidence |
| `semantic-tests-001-boundaries-before.log` | 20 failed, 26 passed | 18 implementation false greens; two synthetic fixture-writing errors were separately corrected, not attributed to master |
| `semantic-tests-001-raw-fixed.log` | 4 passed | Corrected UTF-8/LF fixture generation only |
| `semantic-tests-001-source-model.log` | 16 passed | Additional source/type regressions |
| `semantic-tests-001-full-after.log` | 59 failed, 162 passed | Root-introduced combined Git pathspec query rejected legal input; full failed run preserved |
| `semantic-tests-002-query-repair.log` | 52 passed, 169 deselected | Separate exact-prefix queries fixed that observed query behavior |
| `semantic-tests-003-full.log` | 221 passed in 279.35 s | Complete new CLI regression suite in temporary real Git repositories |
| `semantic-scope-before-commit.json` | No scope escape | Local full delta and packet/check order; includes unchanged legal-merge fixture byte comparison |
| `semantic-path-ledger-working.json` | Exit 0 | Existing path ledger on the working candidate |
| `semantic-preflight-working.json` | Exit 0 with explicit allow-dirty | Construction preflight, not a clean-candidate assertion |

The new test suite includes actual commits, malformed UTF-8/JSON/YAML, legal merge
semantics, directory/symlink/gitlink/nonexistent sources, missing Git executable,
all-stage positives in both CLIs and modes, source-vs-worktree divergence,
protected/covered-decision cases and separate later evidence commits. One
`not a tree object` probe injects the Git failure in isolation and is not reported
as a naturally occurring repository failure. Historical helper checks use only
synthetic non-secret data; no live Human challenge was run.

Static v2 validation, `git diff --check`, task closure preflight and the live
remote/head checks passed during construction. The two original merge fixtures
remain byte-identical to master. Implementation-team testing is not independent
review; two auxiliary agents stopped on quota and provided no final acceptance.

## Exact-candidate verification still required at this commit

The committed nine-check plan will run against a clean exact candidate and create
a new external attempt. It retains all seven prior checks, adds the full stage
scope regressions, and adds an actual task-packet pilot through both production
CLIs. The pilot explicitly treats its input receipt gates as test declarations,
does not request progression and does not assert canonical stage completion.

Do not reuse either earlier candidate's result: `46acc091` failed and `b0473587`
passed its then-seven checks. Neither measured the present semantic bodies.
After the new plan runs, inspect its full records, report the actually read remote
head, and issue an ordinary Human review handoff. Master integration, runtime
activation and independently controlled global enforcement remain unresolved
Human decisions, not implied by this candidate.
