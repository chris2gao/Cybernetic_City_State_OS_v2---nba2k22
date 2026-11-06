# Final evidence closure for GPT-6

- Task `OS-CORE-WORKFLOW-LIGHTWEIGHT-IMPLEMENTATION-20261105-001`
- Executor role `execution`, Codex
- Tested source `40d5c71064be9184f4fa543208757ed57b8af69a`, complete clean Windows checkout
- Original review delivery `88d43d48aa05d5729c1dfd53084648ffd90943e6`
- Human-relayed second independent review `PASS_WITH_GAPS`
- This execution receipt is supplemental evidence for targeted independent follow-up.

| Gap | Actual evidence |
| --- | --- |
| Windows path denials | A disposable full Core clone was checked out at the tested source. An actual Windows junction targeted an external directory. Junction, direct outside path, protected tools directory and `.git/scratch-probe` each went through the runner CLI with explicit `--apply` and returned 33. For every case the complete physical target file SHA256 map matched before and after. The junction remained a junction to its original target. |
| Original Attempt recovery | Read the original archive directly from the review delivery Git object. Verified archive digest, plan digest and all 18 sizes and SHA256 values. Recovered each byte into a fresh directory. `inspect` and `checkpoint` ran against the exact tested SHA and both exited 0. The recovered files still matched after both calls. The checkpoint reported `attempt_internal_consistency`. |
| Key Workflow integration | Five draft sync tests and six subtests passed, including preview, explicit apply, downstream propagation, zero-diff repeat and refusal after the working copy of formal acceptance was deleted. Two ordinary-work isolation tests and three formal Publication Gate tests passed, including missing final acceptance, separate owner judgment and rejection of reused plan acceptance. |

Nine supplemental commands returned their expected exit codes. The four denials were deliberate negative cases. No unexpected test failures or new functional defects were observed in this scope. The source checkout was clean after verification. The delivery contains evidence only. Independent follow-up remains pending. The recovered Attempt demonstrates internal consistency, source/plan binding and recoverability within this check. The independent reviewer can re-execute for separate execution evidence.

## Raw records and replay

- [Supplemental attempt](supplemental-attempt.zip) contains the exact `receipt.json`, including actual command vectors, exits and before/after hashes, plus all 18 stdout/stderr records. Verify archive and record sizes and SHA256s using the [supplemental index](evidence-index.json). The credential-pattern scan of all 19 records had zero matches and stderr was empty. The private archive retains original execution paths in the actual command vectors.
- [Original Attempt](../review-remediation/attempt.zip) and its [original index](../review-remediation/attempt-index.json) are preserved at the original delivery commit as well. The replay script reads that exact commit.

Copy [verify-windows-closure.py](verify-windows-closure.py) outside the checkout. From a clean Windows Core checkout at the tested SHA with the original review delivery object available, run:

```text
python -B -X utf8 <external-script-path> <clean-Core-checkout> <new-external-evidence-directory>
```

The script creates isolated fixtures and an external evidence directory. The raw receipt records the individual runner, inspect, checkpoint and pytest commands for manual replay. The original Attempt remains separately recoverable for a reviewer who only needs to recompute the original verification record.
