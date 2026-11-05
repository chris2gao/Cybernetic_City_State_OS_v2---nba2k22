# BIC Batch1 series remediation for difference review

Task `NBA2K22-BIC-BATCH1-SERIES-REMEDIATION-20261104-001`. Human approved offline remediation in the current goal attachment. Reviewed base `a3e28e186f198e731c76b74f939da2950b5d15bd`; independent report fixed at `0928775b0201f884107fa07837c9cce328e8c4a5`. Exact delivery SHA is in the final handoff and Git branch. No master integration, formal OS stage acceptance or game effect is claimed.

| Finding | Implementation and execution evidence | Engineering disposition |
| --- | --- | --- |
| R01 | `knowledge_query` resolves public TABLES catalog fields against scoped baseline observations, with identity/provenance/time, requested build/mode checks and conservative UNKNOWN/NOT_APPLICABLE/CONFLICT. Existing R04 mechanism references retain research scope and content hash. Alternate baselines require matching identity, cutoff and applicability before conflicting values can be compared. Original mapper preserved. | Corrected, submitted for independent review. No Native mechanism certification from schema or grade. |
| R02 | Coverage preserves original counts and adds domains, observed/missing/unknown/stale field lists, per-field provenance and empty/absent required-family statuses. Restricted domains return no fields or values. | Corrected, with empty badge, stale/missing/mixed-unit and withheld negative cases. |
| R03 | Synthetic data requires SYNTHETIC mode. Real data accepts game modes or UNKNOWN but remains NOT_CAUSALLY_IDENTIFIED. Arithmetic formulas unchanged. | Corrected, contradiction inputs rejected. |
| R04 | Full warning summary retained. `PytestReturnNotNoneWarning` originates from unchanged `test_player_details.py::test_manifest`, which returns a helper dict. Exact test bytes match pre-BIC master and reviewed base. | Existing test helper issue evidenced; no unrelated test cleanup. |

## Reproduction and evidence

Run `python -B -X utf8 <this-run>/verify_remediation.py`. It runs the original four-file 34-test group plus the new remediation tests, writes actual commands/exit/time and stdout/stderr, compares immutable warning-source bytes, and measures three synthetic baseline-plus-coverage queries on reviewed and remediated code. `performance.json` is a bounded small-fixture comparison, not a full-world benchmark. `warning_provenance.json` retains exact source hashes and warning location.

Publication logs replace only the personal Python installation prefix with `<python-runtime>`. Warning type, test path, `_pytest/python.py:171` location and diagnostic text remain available. The raw unredacted logs remain local under ignored `_runtime`; their stdout SHA256 is recorded in the verification receipt. Other source and test content is preserved.

## Limits and continuity

Unknown build or mode applicability remains UNKNOWN even if a field value is present. Schema registration is not observation. Synthetic source grades and historical observations retain their original evidence status. Qualification/XP/growth/animation/success-rate effects remain unproved. Independent source authenticity, production save binding and formal OS stage judgments remain with their existing review owners.

Existing Native identity, save/season isolation, CLI, badge and factorial checks run in the same related regression group. P0 and prior engineering evidence are unchanged. Git Run is the recovery source at the published fixed commit; PRMS SAVE_TASK_CONTEXT was not invoked. Next owner is GPT-6 for a single difference review of R01-R04.
