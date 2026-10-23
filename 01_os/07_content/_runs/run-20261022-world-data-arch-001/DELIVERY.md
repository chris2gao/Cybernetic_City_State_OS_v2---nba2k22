# WORLD-DATA-ARCH-01 candidate delivery

Human review: PASS, explicit statement recorded in [human_review.md](human_review.md). Separate independent model review was not performed. Master integration and WORLD-DATA-SCHEMA-01 were not started.

## Evidence and commit binding

[Completion pointer](completion_pointer.json) binds the five architecture artifacts, source base, implementation candidate, verification receipt and Human acceptance. The implementation candidate is `4cb30c369cf3b02dabbf33f04e02f928d260bbf5`. Its six declared checks actually ran through the canonical OS managed runner, with clean source guards; a subsequent `inspect` recomputed success.

[Verification receipt](verification_receipt.json) contains actual exit codes and stream digests. The verification directory preserves complete stdout/stderr bytes as text plus original finish/source/result records. Original managed input/start records containing local interpreter paths remain in the sibling `world-data-arch-01-evidence/attempt-02` directory. The published subset is not advertised as the full managed `inspect` input.

This closure commit adds only run evidence and updates pointer/lifecycle fields. It does not change architecture documents, catalog, scenario inputs, validation code, plan or packet. The final containing commit is validated again through the same managed plan before push; that exact final attempt and remote readback are retained externally as `world-data-arch-01-evidence/final-attempt` and `publication_receipt.json`. This avoids inventing a self-referential commit hash. Resolve the pointer at the full SHA in the final Human handoff.

The first runner invocation rejected candidate `9f6e67cd677a2c296cf2d5b9ff58a0b9b8ab08da` before creating an attempt directory: managed allowlists support exact files or directory `/**`, not filename globs. A narrow packet/checker correction replaced the wildcard with exact required files. No check results are claimed for that rejected invocation.

## Verified conceptual results

- Two worlds with identical native player/game IDs retain separate players, games, statlines and career/actor references.
- One player remains in the same world through the selected 2021–2030 season and trade intervals; old technical-binding approvals fail.
- Three observations of the same verified game produce one game and two assertion revisions; unresolved identity is rejected.
- Observed 45 versus native 70 remains a partial/conflicting comparison; two games remain two.
- Direct, alias, nested/raw and restricted-derived fields are rejected in the illustrative GM projection; public points succeed.
- Shared static template references succeed; cross-world careers and memories fail.

These are executable conceptual examples, not production database enforcement, a security certification, a native game capture, a long-season decoder test or a Save/Reload proof.

## Architecture decisions and downstream boundary

Stable world_id is distinct from DEV14 save_instance_id because the existing reset replaces both instance and generation. Explicit same-save continuity evidence is required to preserve world identity across technical reconstruction. Player/team/game identities are world-scoped and do not derive from names, slots, pointers or unproven global native uniqueness. No world branching, merging or cross-save dynamic inheritance is permitted.

Event assertions, state observations, native cumulative totals, derived calculations and AI records retain separate provenance and time. Native decoder limits and identity/StatBank unknowns remain explicit. All five documents and the twelve-item acceptance evidence map are available through the completion pointer; existing V2/backlog/roadmap/authority/baseline updates preserve historical V1/audit sources.

Next work requires Human dispatch. A reviewer may inspect the exact published candidate, source code cited by the ADR, catalog/ER cardinalities and retained tests. Neither the Human review record nor these checks authorizes master integration or production operations.
