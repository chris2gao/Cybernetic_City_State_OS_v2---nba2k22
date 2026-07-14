# Math Mentor P0 Control-Plane Hardening — Final Program Report

## Status

```yaml
task_id: math-mentor-p0-control-plane-hardening-0001
status: implementation_validated_awaiting_exact_head_review
source_branch: master
source_head: 764d03d7d0a9ad553f4f3868699b06d9de5553ea
work_branch: codex/math-mentor-p0-control-plane-hardening
validated_implementation_head: 91a1070c2d7e77eff1e1aacb9115551151b65b50
candidate_head: assigned_after_this_report_commit
master_push_authorized: false
source_publication_authorized: false
human_gate: required
```

P0 is implemented and statically validated. It remains inactive and requires
ChatGPT review of the exact development-branch head followed by the protected
Human gate. Nothing was merged or pushed to `master` by this task.

## Delivered Control Plane

### Authority And Maturity

- One derived, non-authorizing authority registry orders external Human and
  repository contracts and maps protected actions to fail-closed decisions.
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
- Test fixtures are rejected in production mode.
- Verifier decisions are sealed and deep-frozen; serialized snapshots cannot
  re-enter admission as trusted objects.
- No real secret, signing key, token, credential, or production authentication
  transport was created.

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

Main-agent candidate-head validation:

```text
65/65 unittest cases passed in 43.828 seconds
two independent registry builds were byte-identical
three materialized registries matched rebuilt bytes
all registry, normalized-node, authorization-context, and resolution schemas passed
all payload hashes passed
all 667 normalized records remained consumer-disabled
229 staging assets remained excluded
git diff --check passed
34/34 implementation paths matched the Human allowlist
high-confidence credential-pattern scan: 0 files
__pycache__ remaining: 0
```

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

## Commits Before Final Report

```yaml
- head: bf62583503781c644a5ad66e6bd57908e37ad85f
  subject: "docs(math-mentor): define P0 control contracts"
- head: 91a1070c2d7e77eff1e1aacb9115551151b65b50
  subject: "feat(math-mentor): harden P0 control plane"
```

The final evidence/report commit is identified by the external exact-head
handoff after publication; embedding a commit's own hash in its content would
be circular.

## Deviations

- Business-path deviations: none.
- The standard `.ai/LONG_RUN_LOGS` path was not used because it was outside the
  exact Human allowlist. The non-blocking review ledger is stored under this
  authorized program-run directory and this deviation is explicitly recorded.
- No combined roadmap read occurred.
- No runtime, Coordinator, student-state, scheduler, node, bridge, source, or
  master publication occurred.

## Remaining Real Human Decisions Only

1. Accept or reject the exact candidate head after ChatGPT review.
2. Select a small certified pilot subset.
3. Adjudicate only the identity conflicts required by that pilot.
4. In later separately scoped tasks, choose production authentication,
   trusted-decision rehydration, persistence, audit, rollback, privacy, and E2E
   integration designs.
