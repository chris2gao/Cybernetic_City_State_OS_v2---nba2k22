# Canonical Node Identity Schema

Version: `1.0.0`

Status: P0 read-only identity contract

Primary registry: `CANONICAL_NODE_CROSSWALK.json`

## 1. Purpose And Boundary

This document defines identity for Math Mentor teaching-node records without changing any node, roadmap, bridge, prompt, or legacy artifact.

The **sole primary key** for a canonical teaching node is the immutable opaque UUIDv5 stored as `canonical_uuid` in the external `CANONICAL_NODE_CROSSWALK.json`. Domain IDs, versioned roadmap `n_*` IDs, exact root paths, exact root filenames, and reviewed legacy values are typed aliases only. None of them is the canonical primary key.

This contract does not:

- decide mathematical equivalence;
- repair or rename a source YAML file;
- promote a node to teaching-ready, validation-ready, bridge-ready, or Coordinator-consumable;
- activate a runtime, Coordinator, UI, state writer, scheduler writer, node generator, or bridge generator;
- authorize P3, source publication, merge, or any protected action.

Identity resolution is necessary evidence for later stages. It is not sufficient admission evidence.

## 2. Canonical UUID Namespace

The namespace contract is:

```yaml
namespace_ref: "08_Domain_Applications/Math_Mentor/p0_control_plane/identity_namespace.yml"
namespace_uuid: "e70d71ef-5916-5991-9e88-9e93fc07c31e"
uuid_algorithm: "RFC4122 UUIDv5"
```

The namespace UUID is immutable for schema version 1. A future namespace requires a new schema version and an explicit Human-reviewed migration. It must not silently replace existing `canonical_uuid` values.

### 2.1 Bootstrap Assignment

For each direct-root teaching-node candidate in the fixed P0 bootstrap path set, bootstrap assignment is:

```text
canonical_uuid = uuid5(
  e70d71ef-5916-5991-9e88-9e93fc07c31e,
  "canonical-node|v1|" + NFC(repo_relative_exact_root_path)
)
```

The bootstrap path must be:

- repository-relative;
- normalized to Unicode NFC;
- written with POSIX `/` separators;
- the exact direct-root path under `Pure_Math_Intuition_DB/`;
- free of `.` or `..` segments;
- case-preserving and not case-folded;
- bound to the source file SHA-256 and corpus source head.

Bootstrap derivation is an assignment mechanism, not a claim that the path string is the identity. The resulting UUID is the primary identity.

### 2.2 Immutability Target And Current Bootstrap Limitation

The required post-bootstrap identity invariant is that once a `canonical_uuid` is accepted:

1. it is never recomputed merely because a domain ID, filename, path, title, roadmap ID, or legacy alias changes;
2. a move or rename preserves the UUID through a reviewed resolution record and previous-row provenance;
3. two UUIDs are never merged from fuzzy similarity, numeric suffix equality, filename similarity, or title similarity;
4. a split, merge, or identity-changing rewrite requires explicit Human review and a durable resolution record;
5. a future migration-capable builder must load accepted prior UUID assignments before applying bootstrap assignment to genuinely new root candidates.

This prevents a mutable alias from becoming an accidental primary key.

The current P0 builder is deliberately bootstrap-only:

```yaml
bootstrap_only: true
prior_crosswalk_preservation_implemented: false
post_bootstrap_alias_or_path_change_requires_human_reviewed_migration: true
```

The prior-crosswalk loader is not implemented in P0. Safety currently comes from the immutable baseline head plus exact root path-set/count/digest checks in `identity_namespace.yml`. If a root node is moved, renamed, split, merged, added outside the fixed baseline, or removed, the builder must fail closed. It must not recompute and accept a replacement UUID. A later Human-approved migration task must add prior-crosswalk preservation before any such path-changing migration is allowed.

## 3. Identifier Classes

### 3.1 Canonical Node UUID

```json
{
  "canonical_uuid": "7f65113e-6571-5f45-a40a-662f89a9d79f"
}
```

Requirements:

- lowercase canonical UUID string form;
- RFC4122 UUID version 5;
- unique within `CANONICAL_NODE_CROSSWALK.json`;
- immutable after accepted materialization;
- never reused for a bridge, structural file, prompt, roadmap record, or excluded asset.

### 3.2 Artifact UUID

An `artifact_uuid` may identify a path-scoped non-node asset or source artifact. It is not a node primary key and must not be used for teaching, bridge, or Coordinator admission.

### 3.3 Resolver-Internal UUIDs

Implementation helpers may produce path-, local-ID-, roadmap-, edge-, or conflict-scoped UUIDs. These are resolver records only. In particular, a UUID derived from a domain ID or roadmap ID is not `canonical_uuid` unless an accepted external crosswalk explicitly materialized that exact canonical assignment under this schema.

## 4. Typed Alias Contract

Every alias in the crosswalk has this shape:

```json
{
  "alias_type": "domain_id",
  "value": "CALCULUS-265",
  "namespace_or_version": "math_mentor_domain_id_v1",
  "status": "observed",
  "source": {
    "path": "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/CALCULUS-265.yaml",
    "json_pointer": "/id",
    "content_sha256": "<64 lowercase hex>"
  },
  "resolution_ref": null
}
```

Required alias fields:

- `alias_type`;
- `value`;
- `namespace_or_version`;
- `status`;
- `source.path`;
- `source.json_pointer`, which may be `null` only for path or filename evidence;
- `source.content_sha256`;
- `resolution_ref`, which is required when status is `human_approved`.

Allowed alias statuses:

- `observed`: extracted exactly from a source but not by itself approved as a semantic binding;
- `declared_unapproved`: declared by a legacy or secondary source and awaiting review;
- `observed_non_authoritative`: imported from stale Stage 0 or another evidence-only source and forbidden from automatic binding;
- `human_approved`: accepted by a durable reviewed resolution;
- `conflict`: contradicts another alias or expected binding;
- `quarantined`: excluded from consumption until a separate decision.

No alias value can silently become `human_approved`.

Allowed alias types are exactly:

```json
["domain_id", "root_path", "root_filename", "roadmap_id", "legacy_alias"]
```

### 4.1 `domain_id`

A domain ID is an observed strict node identifier such as `CALCULUS-265`, `DIFF_GEO-661`, or `PROP_LOGIC-001`.

Rules:

- inspect the declared ID fields supported by the normalizer;
- preserve the exact scalar value;
- multiple distinct strict-ID values in one document create a conflict;
- a domain ID is an alias even when unique and filename-compatible;
- a numeric suffix such as `265` has no standalone identity authority.

### 4.2 `root_path`

The alias value is the exact normalized repository-relative path of a direct-root corpus record.

Rules:

- it is the bootstrap name source for a new `canonical_uuid`;
- it remains an alias after assignment;
- staging paths cannot receive teaching-node binding through this contract;
- path changes require reviewed preservation of the existing UUID.

### 4.3 `root_filename`

The alias value is the exact root filename, including any descriptive suffix and `.yaml` extension.

Rules:

- do not strip a suffix and call the result canonical;
- do not use basename similarity as an identity decision;
- exact filename evidence may corroborate a binding but cannot override a conflict.

### 4.4 `roadmap_id`

A roadmap alias must be versioned and source-bound:

```json
{
  "alias_type": "roadmap_id",
  "value": "n_265",
  "namespace_or_version": {
    "roadmap_set": "split_roadmap_v1",
    "level": 3,
    "source_sha256": "<64 lowercase hex>"
  },
  "status": "declared_unapproved",
  "source": {
    "path": "08_Domain_Applications/Math_Mentor/学习期prompt/数学知识路线图_第三层大学核心.yaml",
    "json_pointer": "<exact pointer or null>",
    "content_sha256": "<same source digest>"
  },
  "resolution_ref": null
}
```

Rules:

- use the six split roadmaps, including the exact Level 2 filename with its existing space;
- never read `数学知识路线图_全部.yaml` for this routine identity build;
- `n_265` from one roadmap version is not automatically the same alias as `n_265` from another version;
- roadmap order and numeric suffix do not establish mastery, prerequisite satisfaction, or semantic identity;
- multiple candidate bindings enter `ALIAS_CONFLICT_REGISTRY.json` and remain blocked.

The frozen independent-review extraction recognizes the exact ASCII tag form
`(n_265)`. Seven current source files instead contain the visually similar
fullwidth form `（n_265）`. P0 inventories those values as
`unicode_fullwidth_roadmap_tag_unparsed` evidence, but does not silently
normalize them into roadmap aliases or candidate edges. This preserves the
reviewed 473/420 baseline while making the method-sensitive seven-file delta
explicit. A later Human-reviewed migration may approve a normalization rule;
until then the affected evidence remains fail-closed and `consumer_allowed`
remains false.

### 4.5 `legacy_alias`

Legacy IDs, labels, old mapping-index values, historical filenames, and imported review identifiers use `legacy_alias`.

Rules:

- default status is `declared_unapproved` or `quarantined`;
- only a reviewed resolution may set `human_approved`;
- legacy review artifacts are read-only importer inputs;
- no legacy R5, graduated-table, bridge, staging, or scheduler value grants current state or consumption authority.

## 5. Crosswalk Record

The normative minimum record in `CANONICAL_NODE_CROSSWALK.json` is:

```json
{
  "canonical_uuid": "<immutable UUIDv5>",
  "aliases": [],
  "alias_comparison": {
    "status": "neither",
    "explicit_roadmap_claims": [],
    "stage0_non_authoritative_claim": null
  },
  "binding_status": "unclaimed",
  "blockers": [],
  "consumer_allowed": false,
  "resolution_ref": null
}
```

Allowed `binding_status` values:

- `declared_consistent_unapproved`: exact current self-claim evidence is consistent but still awaits Human approval;
- `human_approved`: a current, hash-bound Human resolution accepted the binding;
- `conflict_open`: one or more typed alias claims conflict and remain unresolved;
- `unclaimed`: no authoritative current roadmap self-claim exists;
- `quarantined`: record is structurally excluded or deliberately withheld.
- `canonicalize`: a Human resolution selected canonicalization while preserving `consumer_allowed: false`;
- `stale_resolution`: an earlier resolution no longer matches the current head or subject hashes and cannot be applied.

`consumer_allowed` remains `false` throughout P0. Identity binding alone never admits a node to teaching, bridges, or Coordinator consumption.

`alias_comparison` is an object, never a list. Its `status` is exactly one of:

- `agree`;
- `explicit_only`;
- `disagree`;
- `explicit_multi_claim`;
- `stage0_only`;
- `neither`.

It also carries `explicit_roadmap_claims` as an array of versioned `n_*` aliases and `stage0_non_authoritative_claim` as `null` or one stale Stage 0 `n_*` claim. It records exact comparisons only and must not contain a fuzzy-match verdict.

`blockers` references durable conflict IDs from `ALIAS_CONFLICT_REGISTRY.json` or explicit missing-evidence codes.

## 6. Conflict And Resolution Rules

The following always block automatic binding:

- distinct strict IDs in one source document;
- one strict domain ID attached to multiple canonical UUIDs;
- one versioned roadmap ID attached to multiple canonical UUIDs without an accepted split decision;
- multiple versioned roadmap IDs claimed as one node without reviewed evidence;
- filename or path evidence contradicting the accepted crosswalk;
- path case collisions;
- missing or invalid source digest;
- stale evidence presented as current-head evidence;
- a structural, bridge, script, prompt, result, staging, or archived artifact presented as a teaching node;
- any attempted resolution based only on numeric suffix, filename suffix, basename, fuzzy title, or node order.

Conflict records belong in `ALIAS_CONFLICT_REGISTRY.json`. A conflict ID is stable and source-bound. Resolution requires a durable `resolution_ref`; models must not mark their own guess `human_approved`.

An unresolved conflict blocks only the affected identity unless corpus reconciliation fails globally.

## 7. Root Corpus Boundary

The identity build consumes the direct children of:

```text
08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/
```

It does not recursively admit `_Staging_*` directories.

The root registry classifies every direct-root item before identity resolution:

- teaching-node candidate;
- legacy bridge;
- structural schema-like file;
- script/test artifact;
- unknown quarantined record.

Legacy `BRIDGE-001` through `BRIDGE-014`, `schema.yaml`, and non-node artifacts never receive teaching-node admission merely because they are YAML files.

## 8. Historical Stage 0 Evidence

The Stage 0 inventory at source head `cefd164472ecbb7095c1aa2c243c34fbec5b51f4` is read-only historical evidence. It may help locate candidate records, but:

- it is stale relative to baseline `764d03d7d0a9ad553f4f3868699b06d9de5553ea`;
- its identity aliases omit the exact Level 2 roadmap;
- it contains filename-suffix guesses prohibited by the current policy;
- it cannot provide current `canonical_uuid`, current binding, teaching admission, or status promotion.

The P0 adapter must label imported Stage 0 fields with their historical source head and limitations.

## 9. Determinism

For the current bootstrap-only implementation, identical namespace, source head, fixed direct-root path set, resolution overlay, and file bytes must produce byte-equivalent canonical JSON after sorting records by `canonical_uuid` and aliases by `(alias_type, value, source.path, source.json_pointer)`.

This P0 guarantee does not cover a root-path rename or move because prior-crosswalk preservation is not implemented. Such a change must stop the builder and enter a later Human-reviewed migration.

Volatile timestamps, absolute workstation paths, platform-specific separators, environment dumps, and nondeterministic map order are excluded from the canonical payload digest.

The output must record:

- namespace UUID;
- corpus source head;
- root path-set digest;
- per-file SHA-256;
- identity schema version;
- generator version;
- resolution-overlay digest and explicit `prior_crosswalk_preservation_implemented: false` marker;
- reconciliation counts;
- unresolved and quarantined counts.

## 10. Admission Boundary

Identity resolution can establish only that a canonical UUID and its typed aliases are consistently recorded.

It cannot establish:

- mathematical correctness;
- complete formal content;
- complete prerequisites;
- teaching readiness;
- validation pass;
- bridge readiness;
- learned status;
- classroom pass;
- graduation;
- Coordinator consumability.

Later admission checks must separately consume Knowledge Completion Program evidence. Mode B remains semantic-review-only, P3 remains Human-gated, and all runtime, Coordinator, state, scheduler, UI, publication, and merge actions remain outside this P0 identity contract.

## 11. Required Validation Checklist

- [ ] Every `canonical_uuid` is a unique lowercase UUIDv5.
- [ ] Every new UUID follows the fixed namespace and bootstrap formula.
- [ ] P0 output declares `bootstrap_only: true` and `prior_crosswalk_preservation_implemented: false`.
- [ ] Root path-set drift fails closed; no rename or move is accepted by recomputing a UUID.
- [ ] A prior-crosswalk loader is implemented and Human-reviewed before any post-bootstrap path migration.
- [ ] No domain ID, roadmap ID, path, filename, suffix, or title is used as the primary key.
- [ ] Every alias has type, version/namespace, status, source path, source digest, and resolution ref field.
- [ ] All versioned roadmap aliases use one of the six split roadmaps.
- [ ] The restricted combined roadmap was not read.
- [ ] Direct-root corpus classification precedes identity binding.
- [ ] Legacy bridges, staging files, structural files, and scripts are excluded or quarantined.
- [ ] Every conflict is represented in `ALIAS_CONFLICT_REGISTRY.json`.
- [ ] `consumer_allowed` remains `false` in P0.
- [ ] No file mutation, node/bridge generation, runtime, Coordinator, UI, state write, scheduler write, or status promotion occurred.
