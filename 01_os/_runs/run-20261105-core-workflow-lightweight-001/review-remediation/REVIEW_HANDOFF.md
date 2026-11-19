# Workflow lightweight remediation for independent review

Task `OS-CORE-WORKFLOW-LIGHTWEIGHT-IMPLEMENTATION-20261105-001`. This is a continuation of the Human-relayed GPT-6 FAIL. The original FAIL and the original executor PASS remain historical records. The next action is an independent GPT-6 review of H-01 and M-01 through M-04.

- Core master base `08d8e534a3438269aa7d7eb1b080ab11c172f462`
- Original tested source `be6774e37b7ece6d3ecc401aa2701cb60dd2c4dc`
- Original delivery and remediation diff base `bb83e72f09a1a8278c71f1e333273bd10d1a7f57`
- Remediation source tested by the original [verification plan](../verification_plan.json) `40d5c71064be9184f4fa543208757ed57b8af69a`
- Source branch `task/core-workflow-lightweight-20261105`

| Finding | Original observed result | Remediation and regression |
| --- | --- | --- |
| H-01 | `.git/scratch-probe` and an arbitrary unlisted directory each returned 0 and produced one write diff. | Existing repository path checks reject Git internals and aliases. The committed Workflow contract restricts the Run roots. An exact committed task packet on the current task branch must authorize the Manifest and every declared Artifact. Regression checks both original cases, a protected system directory, an external path and a linked directory. All deny without writes. |
| M-01 | A committed v3 Artifact/Manifest followed by both reset to v1 returned 0 and produced one write diff. | Git ancestor history for the same Run and stage supplies a floor from both committed versions. Regression refuses v1, then permits v4 and verifies zero diff on repeat. Full, non-shallow history is required. |
| M-02 | A `published` Artifact returned 0 and produced one write diff. | The existing candidate lifecycle and planned Artifact state are required, with kind checked against the committed stage schema. Regression rejects published, complete and wrong-kind objects. The existing check for formal acceptance history still refuses after the worktree copy of the acceptance is removed. |
| M-03/M-04 | The checkpoint and summary did not give a portable original Attempt or fully state the trust boundary. | The checkpoint now labels `attempt_internal_consistency`. An exact, screened 18-file Attempt is recoverable using the archive and digest index below. This supports independent recomputation of internal consistency. Execution attestation, reviewer independence and any subsequent acceptance require separate evidence. |

The original probes ran in temporary Git fixtures before implementation changes. The original runner blob was checked against `be6774e3`. To reproduce, check out the original test SHA, place [reproduce-original.py](reproduce-original.py) outside the checkout and run it from the checkout root with the relative path `01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py` as its only argument.

## Verification and recovery

The original Managed Verification plan ran on a clean checkout of the remediation source. Standard regression passed 575 pytest cases and 432 subtests. Publication Gate passed all 90 history cases. Static Workflow exited 0 with no findings. Existing ordinary-work and formal governance cases were included. The final evidence-only commit does not change tested engine files or the plan. Publication Gate, stage acceptance, protected hooks and Native/REA execution code have zero diff from the original delivery.

Download [attempt.zip](attempt.zip) from this private branch and verify it against [attempt-index.json](attempt-index.json). The index gives the archive SHA256 and the exact size and SHA256 of each record. Extract to a new directory with `python -m zipfile -e attempt.zip <new-directory>`, and verify the extracted records against the index. Then run from the remediation checkout:

```text
python -B -X utf8 01_os/06_execution/task_discipline/managed_verification/managed_verify.py inspect --repo-root . --candidate 40d5c71064be9184f4fa543208757ed57b8af69a --plan 01_os/_runs/run-20261105-core-workflow-lightweight-001/verification_plan.json --attempt <new-directory>
```

The recovery test extracted the archive, compared all original bytes, then ran both `inspect` and `checkpoint` successfully. The original input, all started/finished/source and stdout/stderr records, source-after and result are present. Pattern screening covered all 18 records and found zero matches for credential shapes, secret assignments, credential URLs or protected-source references. All stderr records were empty. The archive preserves the original Python executable path and platform metadata for review inside the private repository. The scan is scoped to the listed patterns and exact artifact bytes.

Residual trust boundary: a same-writer process with filesystem access can construct a self-consistent Attempt. SHA256 comparisons and recomputation establish the recovered bytes and their bindings. The reviewer may re-execute the plan on the fixed SHA for independent execution evidence. The sync operation relies on the task branch's committed packet, available full Git history and a single writer during apply. This handoff requests review and conveys no master integration authority.
