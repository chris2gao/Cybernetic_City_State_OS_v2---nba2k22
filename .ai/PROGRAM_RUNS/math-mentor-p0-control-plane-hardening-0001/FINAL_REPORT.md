# Math Mentor P0 Control-Plane Hardening — Final Program Report

## Status

```yaml
task_id: math-mentor-p0-control-plane-hardening-0001
status: post_integration_validated_pending_normal_pr_merge
source_branch: master
frozen_corpus_source_head: 764d03d7d0a9ad553f4f3868699b06d9de5553ea
work_branch: codex/math-mentor-p0-control-plane-hardening
validated_implementation_head: eebd2688f099d1be035576793a70d135086d4fa6
accepted_candidate_head: abb40dbd13839db3e6204aa4b0ec42eb6fb074fb
pre_integration_master_head: b8dafd756e532a3f92ef4ecb37474fa82eee0080
master_integration_merge_commit: 01d6123b603f031ea34a96fd0adcf996f0b2c138
integrated_development_head: integration_evidence_commit_itself
final_merged_master_head: pending_normal_pr_merge_recorded_in_post_merge_handoff
master_push_authorized: false
normal_pull_request_merge_authorized: true
human_gate: approved_for_this_explicit_integration_scope
```

P0 is implemented and statically revalidated after the independent-review
corrections. ChatGPT accepted exact candidate `abb40db`, and Human authorized
normal PR integration. Current `master@b8dafd7` was merged into the development
branch without conflict or history rewrite, then the complete static suite was
revalidated. P0 remains inactive. At this checkpoint nothing has been directly
pushed to `master`; final publication must occur only through the authorized
normal PR merge.

## Post-Acceptance Master Integration

- Normal merge commit: `01d6123b603f031ea34a96fd0adcf996f0b2c138`.
- Parents, in order: accepted candidate `abb40db` and current master `b8dafd7`.
- The 46 P0 paths had zero overlap with the three intervening master paths.
- The three master files were preserved byte-for-byte as Git blobs:
  `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md` (`969ae22f...`),
  `06_Silicon_Index/AI_Bootstrap_Sequence.md` (`32af3b38...`), and
  `06_Silicon_Index/README.md` (`2c1bdf3e...`).
- No rebase, force operation, direct master push, runtime activation, identity
  adjudication, or source-corpus mutation occurred.

## Delivered Control Plane

### Authority And Maturity

- One derived, non-authorizing authority registry reproduces the canonical
  eight tiers from `.ai/PROTOCOL.md`; same-tier sources are unordered.
- Authenticated tier-3 Human task override is distinct from ordinary tier-7
  task details. Action rules separate granting sources, governing contracts,
  and operational details that may narrow but cannot grant authority.
- One evidence-tier maturity registry distinguishes specification, static
  validation, integration evidence, and operational evidence. No capability is
  labeled operational.
- One deprecation map freezes legacy review prompts, tables, Stage 0 data,
  staging candidates, and unresolved bridges as read-only/importer-only inputs.
- Legacy R5 or classroom pass is explicitly prohibited from producing
  `graduated`.

### Canonical Identity

- `canonical_uuid` is the sole node primary key.
- 667 deterministic unique UUIDv5 assignments were materialized externally;
  no UUID was written to any node YAML.
- Domain ID, exact root path, exact filename, split-roadmap ID, and historical
  values remain typed aliases.
- Numeric suffix, basename, fuzzy title, staging precedence, and roadmap order
  are never identity resolvers.
- The bootstrap materialization declares that prior-crosswalk preservation is
  not yet implemented; a future move/rename needs a reviewed migration input.
- Non-empty model-writable resolution overlays are rejected until an external
  Human-authenticated resolution adapter exists.

### Normalization

- A read-only adapter normalizes all 667 root candidates across E1–E4.
- Every normalized record keeps `mathematical_truth_status: not_evaluated` and
  `consumer_allowed: false`.
- Source nodes, roadmaps, bridges, prompts, existing schemas, and existing
  validators were not mutated.

### Authorization

- Business payload fields, including `human_gate`, never authorize.
- A production host must authenticate an opaque external handle before the
  verifier receives a sealed Human grant.
- Authorization binds task, request, objective digest, source head, operation,
  effect, exact resources, validity, revocation, replay state, and Human gates.
- Requests, grants, and decisions must be factory-issued and retain an intact
  full-field fingerprint; direct, copied, duck-typed, serialized/rehydrated, or
  post-issuance-mutated objects fail closed.
- Verification first constructs a coherent checked request/grant snapshot and
  consumes only that snapshot. Replacing caller-owned fields after validation
  cannot alter the current decision; replay evidence is likewise captured by
  a single exact immutable-set read.
- A fixed case-insensitive policy floor rejects `.env` variants, SSH and
  private-key material, credential filenames/directories, Git/cloud/tool
  credential stores, Windows ADS, control characters, and non-normalized path
  forms without reading file contents or dispatching to a caller policy hook.
- P0 replay checking is membership testing against a host-supplied read-only
  snapshot only. Atomic nonce consumption, nonce persistence, and
  cross-process replay protection are explicitly not implemented.
- Test fixtures are rejected in production mode.
- Verifier decisions are sealed and deep-frozen; serialized snapshots cannot
  re-enter admission as trusted objects.
- No real secret, signing key, token, credential, or production authentication
  transport was created.

Path-only denial coverage includes the required `.env`, `.env.local`,
`.env.production`, `.ssh/id_ed25519`, nested `id_rsa`/`id_ed25519`, `*.pem`,
`*.key`, `credentials.json`, `application_default_credentials.json`,
`secrets/**`, `credentials/**`, and `private_keys/**` cases. It also covers
`.git/**`, `.git-credentials`, `.netrc`, `.npmrc`, `.pypirc`, service-account
and token filenames, `*.p12`, `*.pfx`, and `.aws/**`, `.azure/**`,
`.docker/**`, `.gnupg/**`, and `.kube/**`, plus ADS, NUL/control characters,
and trailing dot/space components. No test opens any such path.

### Admission

- Admission accepts only a sealed authorization decision for the exact asset,
  `repository.read`, and `read_only` effect.
- Authorization cannot override identity, schema, readiness, provenance,
  validator, prerequisite, or blob failures.
- Staging, nested, bridge, schema, script, legacy-role masquerade, stale, and
  mismatched evidence fails closed.
- P0 canonical bridge admission is explicitly unimplemented.
- Legacy import is limited to the three exact historical state tables and
  cannot promote a canonical learning status.
- Admission requests and trusted evidence require internal factory issuance,
  object-identity registration, and intact full-field fingerprints.
- Issuance records retain separate issuer-owned snapshots, and admission uses a
  fresh checked consumption copy; caller field replacement after verification
  cannot promote readiness, relax a state-write request, or change bindings.
- Direct construction, copying, duck typing, serialization reentry,
  post-issuance mutation, and test-fixture evidence in production fail closed;
  decision dimension and restriction mappings are read-only.

## Independent-Review Corrections

The initial evidence commit `9ed8e54` described the first implementation
checkpoint at `91a1070`, including 65 tests. Independent ChatGPT review found
three blockers and required one replay-boundary clarification. Code commit
`80332a0dc1532a037b21e775e47ebb54fe6182c5` supplied the first correction;
follow-up adversarial review exposed object-graph and check/use seams, which
`eebd2688f099d1be035576793a70d135086d4fa6` closes. The combined candidate was
accepted at exact head `abb40dbd13839db3e6204aa4b0ec42eb6fb074fb`:

1. **Authority precedence:** replace the invented linear rank with the exact
   canonical eight-tier contract, preserve unordered same-tier semantics, and
   separate authenticated Human override from ordinary signal/task details.
2. **Admission trust sealing:** bind authorization and admission objects to
   factory identity plus full-field issuance fingerprints; reject copying,
   serialization/duck reentry, private-field spoofing, post-issuance mutation,
   and production use of test fixtures; require independently sealed evidence;
   expose read-only result mappings; consume issuer-owned checked snapshots.
3. **Secret-path classification:** replace the narrow component check with a
   conservative case-insensitive protected-path floor and reject malformed or
   Windows-specific path forms before any file access.
4. **Replay clarification:** retain fail-closed host-snapshot membership checks
   while stating truthfully that the verifier neither consumes nor persists
   nonces and provides no cross-process replay defense.

Additional adversarial hardening rejects behavioral subclasses, forged nested
objects, Unicode surrogates, mutable/duck mappings, method shadowing, and
caller-owned request/grant/evidence replacement at the precise validation/use
seam. Deterministic tests schedule these replacements without timing sleeps.

These are static trust-boundary corrections. They do not add production
authentication, durable replay state, runtime, Coordinator, or admission
transport capabilities.

## Reproduced Quantitative Findings

```yaml
tracked_math_mentor_assets: 1014
tracked_path_set_sha256: 334712813f7b66830a9190b1dbdf2c4221f0f93aba29e61f76a85c33dfbadc1f
stage0_manifest_bytes: 10989541
current_same_path_worktree_bytes: 11203054
byte_delta: 213513
changed_paths: 28
changed_root_nodes: 20
changed_non_node_assets: 8

pure_math_db_tracked: 912
root_direct_assets: 683
nested_or_staging_assets: 229
root_node_candidates: 667
root_parse_pass: 667
strict_identity_resolved: 666
strict_identity_missing: 1
schema_eras: {E1: 143, E2: 496, E3: 8, E4: 20}

split_roadmap_entries: 770
ascii_explicit_claim_files: 473
ascii_unclaimed_source_files: 194
alias_comparison:
  agree: 416
  disagree: 53
  explicit_only: 4
  stage0_only: 166
  neither: 28
candidate_edges_unapproved: 420
human_approved_bindings: 0
consumer_allowed: 0

staging_yaml: 228
staging_parse_pass: 213
staging_parse_fail: 15
staging_basename_shadows: 195
staging_strict_id_overlap: 180
staging_raw_identical_to_root: 0
staging_identity_resolutions: 0

conflict_registry_records: 286
forbidden_suffix_collision_buckets: 33
forbidden_suffix_collision_members: 153
resolved_by_suffix: 0
resolved_by_basename: 0
resolved_by_fuzzy_title: 0
resolved_from_staging: 0
```

The independent review's 473/420 extraction recognized ASCII `(n_*)` only.
Seven E4 nodes contain fullwidth `（n_*）`. P0 records those seven exact values
as diagnostic evidence but creates no edge or consumer permission from them.

## Unresolved Identity Work

All unresolved records remain fail-closed:

- 53 current explicit claim versus historical Stage 0 disagreements;
- 194 source files without a frozen ASCII explicit roadmap claim, including
  the seven fullwidth diagnostic values;
- one missing strict domain ID: `topology_compactness.yaml`;
- two source disposition quarantines: `DIFF_GEO-654` toward the observed
  `DIFF_GEO-653` target and `DIFF_GEO-659` toward the observed
  `DIFF_GEO-658.yaml` target;
- 33 forbidden numeric-suffix collision buckets containing 153 members;
- three filename/domain-ID difference diagnostics.

These counts overlap by design and must not be added as a unique-node total.
Human semantic adjudication is required only when a later certified pilot
actually needs one of these bindings.

## Validation

Accepted-candidate and post-integration static validation:

```text
104/104 unittest cases passed in 52.544 seconds
104/104 unittest cases passed again after master integration in 53.959 seconds
JSON parse, YAML parse, JSON Schema, and generated payload-hash checks passed
two independent registry builds were byte-identical
canonical generated bytes matched immutable Git blobs at eebd268
post-integration generated bytes matched immutable Git blobs at 01d6123
Windows worktree JSON matched after parse/canonicalization
raw worktree bytes were not used as committed-materialization proof
all registry, normalized-node, authorization-context, and resolution schemas passed
all payload hashes passed
all 667 normalized records remained consumer-disabled
229 staging assets remained excluded
git diff --check passed
45/45 source-to-implementation changed paths matched the Human allowlist
46/46 source-to-final-candidate changed paths matched the Human allowlist
46/46 pre-integration-master-to-validated-merge P0 paths matched the Human allowlist
high-confidence credential-pattern scan: 0 files
__pycache__ remaining: 0
runtime and Coordinator activation performed: false
```

The latest consolidated validator reports
`committed_materialization_head: 01d6123b603f031ea34a96fd0adcf996f0b2c138`,
`committed_blob_bytes_match_generated: true`,
`worktree_json_content_matches_generated: true`, and
`worktree_raw_bytes_used_for_commit_proof: false`. This distinction prevents
Windows CRLF conversion from being mistaken either for semantic drift or for
proof of the committed bytes.

Output digests:

```yaml
ALIAS_CONFLICT_REGISTRY.json: 03a402f97501f85cc2eaced46d651234f57ddbce53533af92b0f82810dfd7c21
CANONICAL_NODE_CROSSWALK.json: 3be77ebc9bc7a826607d28af7def16477aa01d32ab67ba5117d8d411d49697d1
ROOT_CORPUS_REGISTRY.json: cb04084040aa00dc0dd80b7bfb39215cbf96a7e50358038dc85a24b45dbc49ac
```

Detailed commands and caveats are in
`EVIDENCE/reproduction_commands.md`; machine-readable findings and validation
are in `EVIDENCE/quantitative_findings.json` and
`VALIDATION/validation_summary.json`.

## Commits Before Final Correction Report

```yaml
- head: bf62583503781c644a5ad66e6bd57908e37ad85f
  subject: "docs(math-mentor): define P0 control contracts"
- head: 91a1070c2d7e77eff1e1aacb9115551151b65b50
  subject: "feat(math-mentor): harden P0 control plane"
- head: 9ed8e54
  subject: "docs(ai): record P0 validation evidence"
- head: 80332a0dc1532a037b21e775e47ebb54fe6182c5
  subject: "fix(math-mentor): seal P0 trust boundaries"
- head: eebd2688f099d1be035576793a70d135086d4fa6
  subject: "fix(math-mentor): harden P0 issuance snapshots"
```

The accepted candidate is `abb40dbd13839db3e6204aa4b0ec42eb6fb074fb`.
The integrated development head is identified by the evidence commit itself;
embedding that commit's own SHA in its content would be circular. The final
merged master SHA is likewise recorded in the post-merge review handoff after
the normal PR merge creates it.
The accepted candidate adds only the new
`CHECKPOINTS/correction-validated.yml` path to the 45-path implementation diff;
the other report updates reuse already counted program-evidence paths.

## Deviations

- Business-path deviations: none.
- Evidence drift was corrected: the prior package predated the three
  independent-review blocker fixes, replay clarification, adversarial snapshot
  hardening, and CRLF-safe Git-blob proof, so its 65-test result and
  worktree-oriented wording were historical rather than final. The frozen
  source corpus did not drift.
- The standard `.ai/LONG_RUN_LOGS` path was not used because it was outside the
  exact Human allowlist. The non-blocking review ledger is stored under this
  authorized program-run directory and this deviation is explicitly recorded.
- No combined roadmap read occurred.
- No runtime, Coordinator, student-state, scheduler, node, bridge, direct
  source publication, or direct master push occurred.

## Closure Metadata

```yaml
drift_cause: >-
  The prior evidence package was recorded before the three independent-review
  blockers, replay clarification, adversarial snapshot hardening, and Windows
  CRLF-safe immutable-blob proof. Its 65-test result and worktree-oriented
  materialization wording were evidence drift; the frozen corpus source did
  not drift.
avoided_extra_gates: >-
  All correction work stayed inside the original Human-authorized P0 objective
  and exact allowlist. No artificial intermediate Human gate was added. The
  exact-head review completed at abb40db, and the explicitly authorized normal
  PR gate remains the only publication route.
final_original_task_status: integration_validated_pending_normal_pr_merge
remaining_real_human_decisions_only:
  - select_a_small_semantically_certified_pilot_subset
  - adjudicate_only_identity_conflicts_required_by_that_pilot
  - authorize_and_choose_later_production_authentication_replay_persistence_audit_rollback_privacy_and_e2e_designs
```

## Remaining Real Human Decisions Only

1. Select a small certified pilot subset.
2. Adjudicate only the identity conflicts required by that pilot.
3. In later separately scoped tasks, choose production authentication,
   trusted-decision rehydration, persistence, audit, rollback, privacy, and E2E
   integration designs.
