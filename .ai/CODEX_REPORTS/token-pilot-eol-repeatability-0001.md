# Token Pilot EOL Repeatability — `token-pilot-eol-repeatability-0001`

## Executive core

```yaml
status: completed
base: "master@386749b386c542d2d17fd21447b882fd6b4a296a"
work_branch: "dev/token-pilot-eol-repeatability-0001-recovered"
root_cause: "Git had no repository checkout policy for byte-exact text fixtures and generated outputs; host core.autocrlf=true materialized LF blobs as CRLF."
chosen_fix: "Add '* text=auto eol=lf' in .gitattributes."
exact_byte_semantics_weakened: false
protocol_or_gate_semantics_changed: false
runtime_activation: false
```

The fix keeps Git's automatic binary detection and declares canonical LF checkout bytes only for files classified as text. It does not mark JSON/Markdown fixtures as binary, normalize bytes inside the validator, or relax any content hash, immutable-blob, or exact-byte comparison.

Baseline reproduced both accepted audit findings under `core.autocrlf=true`: communication compliance ran 17 tests with 16 pass/1 fail, and the repository-index `check` failed before generation. A detached temporary Git worktree created from the candidate index materialized the representative fixtures and generated outputs as `i/lf w/lf attr/text=auto eol=lf`; the unchanged communication suite then passed 17/17.

Repository-index `check`, `validate`, and `self-test` passed; two consecutive `generate` runs produced no worktree diff. The full `core.autocrlf=true` fresh worktree passed communication 17/17, index direct `check`/`validate`, two no-diff generations, zero tracked CRLF files, and zero tracked worktree changes. No existing fixture, validator, schema, policy, protocol, or business/domain content changed; the generator gained only the explicit `.gitattributes` operational-contract classification required by its fail-closed semantic audit.

## Decision rationale

- `.gitattributes` is the correct control point because the defect occurs during Git checkout, before either validator runs.
- `text=auto` avoids forcing binary assets through text conversion; `eol=lf` makes text checkout deterministic on Windows, macOS, and Linux.
- Validator-side newline normalization was rejected because it would weaken the required exact-byte guarantee.
- Marking fixtures as binary was rejected because they are text artifacts and the same defect affects generated Markdown/JSON outside the fixture directory.

## Validation summary

```yaml
communication_baseline: "16/17; expected EOL-dependent failure reproduced"
communication_candidate_fresh_worktree: "17/17"
index_generate_check_validate_self_test: "pass"
second_generate_diff: "zero"
fresh_core_autocrlf_true_checkout: "pass; tracked CRLF count 0; tracked status count 0"
changed_path_allowlist: "pass; .gitattributes, generator classification, report, three generated index.md files, manifest"
```

## Appendix — external run evidence

Full command output is retained outside the repository under `C:/Users/gk/AppData/Local/CityState/token_ledger/logs/token-pilot-eol-repeatability-0001/`; only digests and compact outcomes are published here.

| Evidence | Exit | SHA-256 |
|---|---:|---|
| baseline communication suite | 1 | `8a9afad442f307b80a59dff2a59b175f1ae7ea84496d9880e9f57c75454218d3` |
| baseline index check | 1 | `b592e963f8a29d87899bf8411e55644cab8aaa9e49f1873dc203efe8862099e7` |
| candidate fresh-worktree communication suite | 0 | `e6a3cfcdc1a0c5b7879a10710f8bdb3ce0fef6c57f71e504bd47b334035901ca` |
| final consolidated validation bundle | 0 | `1e4bbe99697dfa56a121fe4d4cffa10a5b0f79178fe7cb83687a4ae30e440512` |

One candidate-validation retry was required because the first raw `GIT_WORK_TREE` simulation leaked the parent repository's `GIT_DIR` into a nested temporary-repository test. That harness created six local-only fixture commits and changed `core.worktree`; the configuration was restored, no remote was touched, the contaminated branch was preserved at `8df7087d1048f1511d305784b101701b439ea95d`, and a recovery branch was recreated from the exact approved base without branch deletion or history rewrite. Replacing the harness with a real detached Git worktree removed the contamination and did not change product code or validation semantics.
