# Core Issue 11 — NBA2K22 PRMS integration

Verified integration candidate: `df0bd44c0a28edf1074dd45c7febd99acf0fb8a3`. Delivery commits after this candidate
only add/update this domain-owned task run; imported Core and existing NBA code are
unchanged. Current Human explicitly authorized execution of Core Issue #11 and
completion of the NBA master merge after verification.

- NBA base: `7742568ac677b3c16079887463f05e81cb1191ed`.
- Approved Core/master source: `e075cdf288a765b7bfd2f4891c8f384404da16e1` (Core PR #10 already merged).
- Actual shared ancestor: `3ae48d2183a6e77d63a43783c7e1999edc01711e`.
- Rehearsed Git merge tree: `b42d10b81aec3fd4439d183e857f7e2877aca4ca`; real merge matched it.
- **1,398 existing domain files preserved** with identical Git blobs/modes;
  **zero existing deletions**, **44 PRMS files byte-identical to Core**.
- **6 managed compatibility checks and inspect passed**. Existing NBA tests: `{'PASS': 295, 'FAIL': 10}`;
  PRMS tests: **77 passed**; existing working-set regression: **44 passed**;
  context structure and fresh-process task continuity passed.

NBA's full existing suite is not green: it has **7 failures and 3 cleanup errors**
already reproduced on the exact pre-update master, with 295 passing tests and
446 passing subtests. The candidate has the identical per-test outcome multiset,
so this merge adds no new NBA failures. The original nonzero pytest exit and full
logs are retained; the compatibility check passes baseline parity, not a fictional
all-tests-pass claim. No unrelated business/test code was changed to hide failures.
See nba_baseline.json and nba_existing_tests.json for both exact snapshots.

The continuity example explicitly saves A then B in isolated real Git and restores
A in two new Python processes. Current state stays unchanged. This verifies local
task continuity after inheriting Core into the actual NBA tree; it is not a claim
that a real GPT/Codex window or production state host was tested.

The changed paths are imported Core-owned code/contracts/Boot/Registry/history plus
this new domain-owned evidence run. No existing NBA business, research or task
evidence changed. Domain 09/G2 is neither created nor declared formally published.
Other domains are explicitly excluded. Existing unrelated branches/PRs are not
integrated, and the original dirty NBA worktree is preserved.

Evidence: merge_preview.json, source_and_domain_preservation.json,
verification_receipt.json, nba_existing_tests.json, prms_tests.json,
task_continuity_example.json, changed_paths.json and execution_result.json.
Master publication is recorded separately by the actual PR merge/readback receipt;
this candidate report does not pretend a future merge was already observed.

## Reproduce

```text
git checkout df0bd44c0a28edf1074dd45c7febd99acf0fb8a3
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py run --repo-root . --candidate df0bd44c0a28edf1074dd45c7febd99acf0fb8a3 --plan 01_os/07_content/_runs/run-20261029-nba-core-prms-sync-issue-11-001/verification_plan.json --attempt <existing-external-parent/new-attempt>
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py inspect --repo-root . --candidate df0bd44c0a28edf1074dd45c7febd99acf0fb8a3 --plan 01_os/07_content/_runs/run-20261029-nba-core-prms-sync-issue-11-001/verification_plan.json --attempt <same-attempt>
```

Use a fresh attempt. Source integrity is verified against actual Git objects;
no game, REA, real state service, credential provisioning or other-domain action
is needed or authorized by this integration.

## Verified master integration and closeout

Status: **TASK_CLOSED_NBA_CORE_PRMS_SYNC**. Actual code integration PR:
https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/20; observed NBA master code-integration commit:
`c166382a3e09ce65c20024377f441ba022b7ec2a`. Actual fetched remote tree equals reviewed head
`b49b67cc7bca26a86b26086c142399ff634e9e25`, preserves the NBA base and Core source ancestors,
and leaves other domains untouched. See master_integration_receipt.json.

This follow-up closeout changes only this task's domain-owned evidence. Current
formal NBA/master and both publication receipts are recorded on Core Issue #11;
the code-integration hash above describes the observed event, not a prediction
of the later evidence-only closeout merge hash. Baseline NBA failures remain
explicit and are not repaired or relabeled by this integration.
