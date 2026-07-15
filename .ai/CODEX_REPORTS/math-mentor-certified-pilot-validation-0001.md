# Validation report — consolidated correction

Accepted candidate: `6830956ca9e7efff4d8c6d60602f462b0785b69a`.
Publication-preparation validation head:
`1575c24b56c5db02a1874818c8c6ecc6abf5d428`.

- Four separate `sandbox_evaluator.py` runs: Mode A 2 `passed`; Mode B 2
  `review_required` with `semantic_audit_not_machine_validated`.
- Complete P0 unittest suite: 104 executed, 104 passed, 0 failed.
- Live-corpus test retains 667 total, E1/E2 expectations, identity counts,
  missing-identity path, schema validation, and per-node fail-closed assertions.
- P0 consolidated validator: two invocations passed; outer outputs byte-identical.
- Each validator reports two byte-identical internal builds, materialized output
  equality, 667 roots, 229 staging exclusions, 420 unapproved candidate edges,
  53 explicit alias conflicts, `consumer_allowed=0`, runtime activation false.
- Changed YAML/JSON parse: passed.
- Dossier schema: 4/4 passed.
- Identity/prerequisite evidence schema: passed.
- Validation-summary schema: passed.
- `git diff --check`: passed.
- Original-baseline and continuation exact-path allowlists: passed.
- High-confidence credential/secret pattern scan: zero findings.
- Forbidden business/runtime/production mutations: zero.
- Source mailbox: verified neutral against the master baseline.
- Accepted five node/test files: byte-identical to the accepted candidate.
