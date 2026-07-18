# Reviewer role memory

### reviewer-fresh-checkout-proof

- guidance: For publication acceptance, validate the exact candidate or merged head from a fresh checkout and compare immutable trees; do not infer release correctness from the implementation worktree alone.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:.ai/CODEX_REPORTS/init-and-comms-unified-impl-0001-master-publication.md#Post-merge-verification`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify when the release verification contract or repository test topology changes.
- authority: `routing_only`

### reviewer-primary-evidence

- guidance: Treat summaries and role memory as routing only; independently read the exact diff, decisive contracts, test evidence, and immutable refs before acceptance.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:.ai/load_profiles/foreground_independent_reviewer.md`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify when the independent-reviewer load profile changes.
- authority: `routing_only`
