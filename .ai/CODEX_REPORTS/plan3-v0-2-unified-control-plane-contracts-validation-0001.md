# Plan 3 v0.2 Unified Control-Plane Contracts — Validation

```yaml
task_id: plan3-v0-2-unified-control-plane-contracts-0001
validation_status: candidate_tree_pass
source_base: "2d73781621ed856e414ca7839ff61eb4d8722d35"
preflight_tree: "ab95704d252df77382ffc1a3a846f731a33f26c2"
qualified_candidate_resolution: "tree_of_commit_containing_this_report"
```

## Structural contract checks

An inline read-only Python validator parsed the first YAML metadata block of all five files and verified:

- 5/5 files at version `0.2.0` with `operational_activation: false`;
- 8/8 authority tiers in exact order;
- L0–L9 layer rows in exact order with L9 inactive;
- 12/12 task types with non-empty entry/state/evidence/stop/Human-gate fields;
- 8/8 recovery modes with the same required fields;
- 24/24 capabilities with non-empty state/actor/auth-scope/risk/validation/fallback/activation-boundary fields;
- unique identifiers within all three registries;
- exact required source paths exist;
- every sibling file links to the single architecture authority registry;
- no positive runtime/Coordinator activation claim.

Relative Markdown link check: 11/11 pass. `未完成任务备忘录.yml` parses as YAML with 6 program-order entries and 10 architecture layers. `git diff --check` passes.

## Repository-index checks

Preflight staged tree:

```yaml
tracked_directories: 160
tracked_files: 1819
index_files: 160
direct_file_entries: 1819
child_directory_entries: 159
broken_relative_links: 0
missing_file_entries: 0
duplicate_file_entries: 0
orphan_index_files: 0
unsafe_absolute_links: 0
utf8_parse_failures: 0
secret_value_findings: 0
unknown_requires_review: 0
private_or_restricted_body_reads: 0
semantic_audit_status: reviewed
```

`self-test` passes with the new six exact classification cases. `semantic-audit` passes. Two consecutive fresh-worktree `generate` runs report zero changed outputs.

## Communication and EOL checks

New registered worktree from preflight tree with `core.autocrlf=true`:

```yaml
communication_unittest: "17/17 pass"
tracked_crlf_count: 0
tracked_status_count: 0
index_check: pass
index_validate: pass
deterministic_generate_run_1_changed_outputs: 0
deterministic_generate_run_2_changed_outputs: 0
```

The long-lived authoring worktree reports 140 pre-policy CRLF fixture files and fails the fixture aggregate method with raw digest mismatches. No communication file is changed by this task. Fresh checkout proves the committed `.gitattributes` policy and current candidate tree behave correctly.

## Candidate-tree gate

After the three reports were staged and indexes regenerated, the complete 16-path staged tree passed:

- exact changed-path allowlist 16/16;
- five-file structure/link/YAML checks;
- index `generate` twice with zero changes, `check`, `validate`, `snapshot`, `semantic-audit` and `self-test`;
- scoped credential/private-key pattern scan;
- fresh `core.autocrlf=true` communication 17/17;
- fresh index check/validate and two-generation zero diff;
- fresh tracked CRLF count 0 and tracked status count 0.

The containing candidate commit is the authoritative self-resolution of this report’s final tree. After normal merge, repeat the source-bound checks from the remote merged head before closure.
