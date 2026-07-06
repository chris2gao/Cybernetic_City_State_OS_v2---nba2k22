# Stage 1 Batch-2 Selection Plan

packet_id: codex-math-mentor-knowledge-completion-stage-1-batch-2-selection-plan-0001
task_id: math-mentor-knowledge-completion-stage-1-batch-2-selection-plan-0001
status: completed_for_review

## 1. Scope

This is a non-mutating Stage 1 Batch-2 selection plan only.

It does not perform node mutation, metadata mutation, semantic repair, mode A/B judgment, formal definition creation, prerequisite creation, mapping-boundary creation, roadmap edits, bridge work, runtime activation, Coordinator activation, scheduler writes, source/master publication, or unrelated cleanup.

## 2. Base And Evidence

- source branch: `master`
- verified source head: `02fd0ed2a002a9c10e8a0eeac1a9e3874215b3ae`
- work branch: `ai/knowledge-completion/stage-1-batch-2-selection-plan-0001`

Required evidence read:

- Stage 1 preflight plan report
- Stage 1 pilot metadata-only report
- Stage 1 pilot metadata-only validation report
- Stage 0 inventory:
  - `node_classification.json`
  - `identity_aliases.json`
  - `duplicates_missing_conflicts.json`
  - `parse_report.json`
- four published pilot nodes:
  - `ANALYTIC_NT-684.yaml`
  - `ANALYTIC_NT-687.yaml`
  - `ANALYTIC_NT-688.yaml`
  - `ANALYTIC_NT-692.yaml`

The four pilot nodes are present on `master` with conservative Stage 1 metadata/status fields and no `mode: A` or `mode: B`.

## 3. Inventory Summary After Excluding Published Pilot Nodes

Stage 0 inventory facts:

- total classified records: 667
- original `unknown_needs_review`: 659
- remaining `unknown_needs_review` after excluding the 4 pilot nodes: 655
- identity-stable records: 525
- identity-stable remaining after excluding pilot nodes: 521
- original pure metadata-only records with all tracked status fields absent: 4
- remaining pure metadata-only records with all tracked status fields absent: 0
- remaining identity-stable records with missing mode/lane: 16
- remaining records with missing mode/lane overall: 158
- remaining records missing roadmap alias in node classification: 32
- roadmap aliases without root node candidate: 194
- remaining records with missing subtopics: 139
- remaining records with explicit manual/missing/review status: 514
- parse failures: 15
- duplicate ids: 0
- duplicate filename-number groups: 33

Interpretation: the first pilot consumed the only four records matching the strict "status fields absent, stable identity, roadmap alias present, subtopics present" metadata-only shape.

## 4. Candidate Separation

### Safe Metadata-Only Status-Normalization Candidates

Count: 0.

No remaining node matches the first pilot's safe metadata-only profile:

- stable id;
- stable filename identity;
- split-roadmap alias present;
- subtopics present;
- no existing tracked status fields;
- no need for mode A/B judgment;
- no semantic field creation.

### Mode/Lane Missing But Human-Gated Candidates

Count: 16 identity-stable nodes.

All 16 are `DIFF_GEO` nodes from `DIFF_GEO-653.yaml` through `DIFF_GEO-668.yaml`. They have stable ids and roadmap aliases, but Stage 0 already recorded:

- `formal_definition_status_if_present: missing`
- `prerequisites_status_if_present: missing`
- `mapping_boundary_status_if_present: missing`
- `validation_status_if_present: manual_review_required`
- `bridge_readiness_status_if_present: manual_review_required`

These are not safe automatic metadata-only candidates. Any attempt to add `mode: A` or `mode: B`, fill formal definitions, add prerequisites, or define mapping boundaries would require Human/ChatGPT semantic authorization.

Representative node range:

```text
08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-653.yaml
...
08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-668.yaml
```

### Roadmap Alias Candidates

Node-side count: 32 records missing `roadmap_identity_or_alias`.

Roadmap-side count: 194 roadmap aliases without a root node candidate.

These require a roadmap-alias reconciliation plan, not metadata-only node mutation. The task does not authorize reading `数学知识路线图_全部.yaml`, editing split roadmaps, or mutating node identity metadata.

### Parse / Staging / Structural Exclusions

Parse failures: 15.

The parse failures are staging-path or structural/schema-like files, including `_Staging_Level6_Part1` and `_Staging_Level6_Part2` entries. They are excluded from Stage 1 node metadata repair and require a separate staging/structural cleanup authorization if they are still relevant.

Duplicate filename-number groups: 33.

Stage 0 reported zero duplicate ids, so these filename-number groups are not an id collision blocker by themselves. They should remain structural/audit context, not automatic mutation targets.

### Semantic Repair Candidates

Remaining broad pool: 655 `unknown_needs_review` records after excluding the pilot.

At least 514 remaining records already carry explicit manual/missing/review status. They require semantic or quality-gate handling rather than another blind metadata-only batch.

### Do-Not-Touch Without Explicit Human Semantic Authorization

Do not mutate:

- the 16 `DIFF_GEO` mode-missing Human-gated records;
- records with missing formal definition, prerequisites, or mapping boundary;
- roadmap-alias candidates;
- parse/staging/structural exclusions;
- any node requiring mode A/B judgment.

## 5. Recommendation

Recommended next batch: none.

next_batch_type: `no_safe_metadata_batch`

Reason: the completed four-node pilot consumed the only strict pure metadata-only cohort identified by Stage 0 and Stage 1. The remaining plausible candidates require semantic review, roadmap-alias reconciliation, or structural cleanup authorization.

## 6. Proper Next Gate

Recommended next gate: Human semantic/quality planning gate.

Suggested next planning task:

```text
Stage 1 Semantic-Gated Candidate Review Plan
```

Scope for that future task:

- select a small Human-reviewed semantic cohort, likely starting with `DIFF_GEO-653` through `DIFF_GEO-668`;
- decide whether mode/lane routing can be assigned by domain policy;
- decide whether formal definition, prerequisite, and mapping-boundary gaps should be repaired locally, regenerated, or deferred;
- keep roadmap-alias reconciliation as a separate plan.

No Stage 1 Batch-2 metadata-only pilot should start from current evidence.
