# Repository Directory Index System Semantic Audit 0001

## Decision

`accepted_after_required_semantic_corrections`

The published mechanical index was complete, but its generator collapsed materially different artifacts into broad suffix/authority templates. This correction audits the complete baseline scope at `master@817039595e78a21356068d3854e380c73eed1417` and makes the generator preserve semantic distinctions on every regeneration.

## Exact accounting

- baseline directory indexes reviewed exactly once: 160
- baseline direct-file entries reviewed exactly once: 1,806
- baseline direct-child-directory entries reviewed exactly once: 159
- baseline file entries passed without semantic change: 0
- baseline file entries corrected: 1,806
- directory roles corrected: 160
- child-directory roles or entry triggers corrected: 159
- recommended-reading-order sequences corrected: 3 (`.ai`, `06_Silicon_Index`, Math Mentor)
- authority classes corrected: 112
- freshness labels corrected: 1,806
- concrete read triggers corrected: 1,806
- baseline entries containing at least one repeated semantic string removed: 1,803
- metadata-only file entries: 14 (13 Private Zone bodies plus the restricted full Math roadmap)
- `unknown_requires_review`: 0
- private or restricted body reads: 0
- unresolved semantic conflicts: 0

The final tracked-file count is allowed to exceed 1,806 only by the three task-required semantic reports. The manifest records both the immutable baseline scope and the final exact scope.

## Method

Each baseline entry was joined by exact repository-relative path and stable `entry_id` to its generated record. The audit compared and then replaced `role_and_use`, `authority_class`, `status_or_freshness`, and `when_to_read`; directory and child-directory records received the same exact-once treatment. The generator now emits `semantic_profile`, `semantic_audit_status`, and `metadata_only_boundary` for each file, plus semantic profiles for every directory and parent-to-child edge.

The evidence ladder was path identity, safe structural metadata already extracted by the generator, explicit repository authority/deprecation contracts, and activation/privacy boundaries. No filename-only fuzzy identity, numeric suffix inference, staging precedence, Private Zone body, or restricted full-roadmap body was used.

## Material corrections

- `MATH_MENTOR_AUTHORITY_REGISTRY.yml` and `MATH_MENTOR_DEPRECATION_MAP.yml` are now `routing`, matching their declared derived/non-authorizing roles, rather than operational contracts.
- 667 root corpus YAML nodes are `math_root_candidate_node`: their root location does not prove admission, certification, runtime permission, or consumer permission.
- 229 staging YAML nodes are `math_staging_candidate`: they route to root comparison/alias adjudication, not historical importer semantics.
- 14 root `BRIDGE-*` YAML files are `math_legacy_unresolved_bridge`: endpoint and identity conflicts remain fail-closed.
- source `.ai/STATE.yml`, `INBOX.md`, `OUTBOX.md`, and `HUMAN_BRIEF.md` are explicit neutral-master baselines; active state remains on `ai/review/latest`.
- persona files require an explicitly selected role and do not instantiate an agent by existing.
- Parliament Issues, verdicts, execution-plan designs, archived material, program-run evidence, tests/fixtures, and Private Zones now have distinct authority/freshness/read boundaries.
- every read trigger includes a concrete task condition and safe subject anchor; directory triggers identify the exact run, proof case, issue, owner, staging pool, test partition, or subsystem.

## Generator durability

The large curated directory-entry template has been removed from the active path. Semantic classification is deterministic, exhaustive, fail-closed, manifest-accounted, and covered by validation invariants. Validation rejects absent/unrecognized profiles, incomplete audit markers, metadata-boundary drift, old generic phrases, authority regressions on critical registries/mailboxes, profile-count drift, nonzero unknowns, and any claim of protected-body reads.

## Scope boundaries

No Plan 3 implementation, runtime/Coordinator/Gateway/writer/scheduler activation, node mutation, bridge mutation, roadmap mutation, Private Zone body read, restricted full-roadmap body read, force push, or history rewrite was performed.
