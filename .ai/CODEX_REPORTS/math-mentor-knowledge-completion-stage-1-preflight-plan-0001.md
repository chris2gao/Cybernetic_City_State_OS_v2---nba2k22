# Math Mentor Knowledge Completion Stage 1 Preflight Plan

packet_id: codex-math-mentor-knowledge-completion-stage-1-preflight-plan-0001
task_id: math-mentor-knowledge-completion-stage-1-preflight-plan-0001
status: completed_for_review

## 1. Scope

This is a non-mutating Stage 1 preflight and strategy plan only. It does not execute Stage 1 repairs.

Authorized purpose: use the published Stage 0 inventory artifacts to design a Stage 1 Node Identity And Mode Routing Completion strategy.

Not authorized:

- node repair;
- identity metadata mutation;
- roadmap mutation;
- prompt/schema/validator mutation;
- bridge design or generation;
- P3 reopen;
- runtime or production Coordinator activation;
- learning-state or scheduler writes;
- source/master push.

## 2. Stage 0 Evidence

Source head: `2f83fb88b6546324f35f2088bc02cf6b27918c7d`

Stage 0 inventory counts:

- unknown_needs_review pool: 659
- deterministic identity-stable records: 427
- pure metadata-only, no existing manual status: 4
- mode/lane missing: 162
- mode/lane present: 497
- missing id field: 142
- filename/id mismatch: 0
- roadmap alias missing from split roadmap scan: 200
- missing or empty subtopics: 139
- formal definition absent or unmarked: 659
- prerequisites absent or unmarked: 659
- mapping boundary absent or unmarked: 659
- explicit manual-review/missing status: 513

Interpretation: Stage 0 used strict metadata gates. The 659 unknown records should not be treated as mathematically bad nodes. Most are missing standardized metadata fields, not necessarily missing usable teaching content.

## 3. Stage 1 Cohort Taxonomy

### Cohort A: Deterministic Identity / Metadata Fill Candidates

Definition:

- `id` is present;
- filename identity is stable;
- numeric alias has a matching split-roadmap `n_xxx` record;
- `sub_topics` is present;
- no duplicate id;
- no filename/id mismatch;
- mutation can be limited to narrow identity/routing metadata.

Count from Stage 0: 427 identity-stable records.

Important split:

- 4 records have no existing manual status fields and are the safest first auto-eligible metadata pilot candidates.
- Many other identity-stable records already declare `manual_review_required` or `missing` status and must be treated as Human-gated or semantic repair candidates.

### Cohort B: Filename / ID Mismatch Candidates

Definition:

- filename numeric suffix conflicts with `id`, or duplicate id exists.

Count from Stage 0:

- filename/id mismatch: 0
- duplicate id conflict candidates: 0

Strategy: keep the detector in Stage 1 validation, but no pilot batch is needed for this cohort unless new evidence appears.

### Cohort C: Mode Routing Missing Candidates

Definition:

- node has identity and subtopics but lacks `mode` / MathLane routing metadata.

Count from Stage 0: 162.

Strategy:

- deterministic fill is allowed only when domain-to-lane rule is already defined and the node has no explicit manual-review blocker;
- otherwise mark `mode_routing_status: manual_review_required` in a future authorized repair task;
- do not infer Mode B mappings from everyday metaphors.

### Cohort D: Roadmap Alias Candidates

Definition:

- candidate lacks a matching split-roadmap `n_xxx` alias, or split-roadmap scan cannot prove alias.

Count from Stage 0: 200.

Strategy:

- do not read `数学知识路线图_全部.yaml` routinely;
- use split roadmaps first;
- if alias remains absent, classify as `roadmap_alias_review_required`;
- no roadmap edit is allowed in Stage 1 pilot.

### Cohort E: Semantic / Human-Gated Candidates

Definition:

- missing or explicitly `missing` formal definition, prerequisites, or mapping boundary;
- explicit `manual_review_required`;
- subtopics absent or insufficient;
- domain requires mathematical judgment, not metadata fill.

Count signals:

- formal definition absent or unmarked: 659
- prerequisites absent or unmarked: 659
- mapping boundary absent or unmarked: 659
- explicit manual-review/missing status: 513

Strategy:

- no semantic content should be generated in Stage 1 metadata pilot;
- these records should be carried into Stage 2+ node quality or semantic repair planning;
- Stage 1 may only label status truthfully, not invent definitions, prerequisites, or mapping boundaries.

### Cohort F: Parse / Staging / Structural Exclusions

Definition:

- parse failures, staging files, schema/template/index/generated files, tests/results, bridge files, roadmaps, protocols.

Strategy:

- not eligible for Stage 1 node repair;
- remain in structural exclusion or parse report;
- repair requires separate authorization only if a future stage explicitly targets the artifact class.

## 4. Recommended First Pilot Cohort

Recommended pilot size shape: 5 records.

Safety finding: only 4 records are fully auto-eligible deterministic metadata-only candidates. The fifth is included only as a Human-gated sentinel to test stop rules.

### Auto-Eligible Metadata-Only Pilot Records

1. `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-684.yaml`
   - id: `ANALYTIC_NT-684`
   - alias: `n_684`
   - proposed future action: add narrow routing/status metadata only.

2. `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-687.yaml`
   - id: `ANALYTIC_NT-687`
   - alias: `n_687`
   - proposed future action: add narrow routing/status metadata only.

3. `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-688.yaml`
   - id: `ANALYTIC_NT-688`
   - alias: `n_688`
   - proposed future action: add narrow routing/status metadata only.

4. `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-692.yaml`
   - id: `ANALYTIC_NT-692`
   - alias: `n_692`
   - proposed future action: add narrow routing/status metadata only.

### Human-Gated Sentinel

5. `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-653.yaml`
   - id: `DIFF_GEO-653`
   - alias: `n_653`
   - existing status: `manual_review_required` / missing formal-prereq-boundary markers
   - proposed future action: do not auto-repair; use as a stop-rule sentinel unless Human explicitly authorizes semantic repair.

If Human requires five mutable auto-repair nodes, Stage 1 should stop before mutation and request a separate selection review, because the current evidence supports only four clearly deterministic metadata-only candidates.

## 5. Future Stage 1 Mutation Rules

Allowed metadata fields for a future authorized pilot:

- `mode`
- `mode_routing_status`
- `validation_status`
- `bridge_readiness_status`
- `formal_definition_status`
- `prerequisites_status`
- `mapping_boundary_status`
- `migration_review` status block when used as a warning only

Allowed only when evidence supports them:

- `mode: "A"` or `mode: "B"` from stable domain/lane rule;
- `mode_routing_status: "inferred_high_confidence"` only for reviewed deterministic domains;
- status values such as `manual_review_required`, `missing`, or `semantic_ready_for_manual_teaching`.

Forbidden in Stage 1 pilot:

- new formal definitions;
- new prerequisites;
- new mapping boundaries;
- rewritten `sub_topics`;
- rewritten `concept_name`;
- generated mathematical explanations;
- broad YAML reserialization;
- roadmap edits;
- bridge edits/generation;
- prompt/schema/validator edits.

## 6. Future Stage 1 Editing Method

Rules:

- patch only a small metadata block near the top of each YAML;
- preserve original field order and existing content;
- no full-file YAML load/dump writeback;
- one batch maximum: 5 records;
- if any file has unexpected structure, stop that file and mark `manual_review_required`;
- do not change semantic body fields.

## 7. Future Validation Commands

Minimum validation for a future Stage 1 pilot:

```powershell
python 08_Domain_Applications/Math_Mentor/tests/teaching_flow_static_validator.py
git diff --check
```

Additional scoped checks:

- parse each touched YAML with PyYAML;
- verify touched files are exactly the pilot list;
- verify no roadmap, bridge, prompt, schema, validator, runtime, Coordinator, scheduler, or learning-state file changed;
- verify status values are from approved vocabulary;
- verify no `run_with_log` or deterministic tool claim is introduced;
- run scoped secret scan over changed files.

## 8. Stop Rules

Stop before mutation if:

- `origin/master` is not at the approved base for the future task;
- a candidate lacks stable `id` or filename identity;
- a candidate lacks split-roadmap alias and full-roadmap access would be required;
- candidate already declares `manual_review_required` and Human has not authorized semantic handling;
- deciding Mode A/B requires mathematical judgment not encoded in existing domain rules;
- any edit would require broad YAML reserialization;
- any validation command fails.

## 9. Rollback Rules

Future Stage 1 pilot should:

- work on a dedicated branch;
- commit only after validation passes;
- use explicit path staging only;
- never use `git add .`;
- never push master/source unless separately authorized;
- if a file fails validation, revert only that file's attempted metadata patch before commit;
- if more than three attempts fail for the same failure signature, log the file and stop that repair path.

## 10. Final Recommendation

Proceed to a separately authorized Stage 1 pilot only after review. Recommended pilot:

- 4 auto-eligible ANALYTIC_NT metadata-only nodes;
- 1 DIFF_GEO sentinel that must remain Human-gated unless semantic repair is explicitly authorized.

This plan should not be interpreted as authorization to mutate any teaching node.
