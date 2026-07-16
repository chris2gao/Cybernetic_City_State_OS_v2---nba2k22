# Repository Directory Index System Semantic Changed Files 0001

## Scope

This correction remains confined to the active allowlist: the deterministic generator, generated manifest, affected generated directory indexes, the three existing semantic reports, and the minimal Phase 3 memo status update. Counts and paths below are relative to `master@2ec6f5d013393fcdd074dc6c81a411ef51f1b0b7`.

## Exact accounting

- total changed paths: 67
- affected generated directory indexes: 61
- deterministic generator: 1
- generated manifest: 1
- existing semantic reports: 3
- minimal Phase 3 memo update: 1
- deviations from the allowlist: 0

The 61 indexes are the exact parents whose direct structured-file descriptions, authority classes, statuses, safe anchors, or report/memo metadata changed. Unaffected indexes remain byte-identical.

## Exact changed paths

- `.ai/CODEX_REPORTS/repository-directory-index-system-semantic-audit-0001.md`
- `.ai/CODEX_REPORTS/repository-directory-index-system-semantic-changed-files-0001.md`
- `.ai/CODEX_REPORTS/repository-directory-index-system-semantic-validation-0001.md`
- `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/CHECKPOINTS/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/INPUTS/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/OUTPUTS/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-analytic-nt-foundation-batch-1-0001/OUTPUTS/teaching-flow-static/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-certified-pilot-0001/EVIDENCE/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-certified-pilot-0001/SCHEMAS/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-certified-pilot-0001/VALIDATION/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-knowledge-completion-stage-0-inventory-0001/inventory/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-p0-control-plane-hardening-0001/CHECKPOINTS/index.md`
- `.ai/PROGRAM_RUNS/math-mentor-p0-control-plane-hardening-0001/VALIDATION/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-actor-origin-forged-host/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-c2-forged-trusted/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-c2-replay/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-c2-trusted-host-pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-claim-forgery/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-claimed-from-mismatch/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-event-mutation/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-fabricated-result/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-missing-event/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-pointer-binding/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-state-task-mismatch/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-unreachable/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-validation-from-other-event/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition-validation-malformed/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_acceptance_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_actor_origin_cross_event_transplant/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_actor_origin_event_digest_transplant/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_actor_origin_replay/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_actor_origin_wrong_provider/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_actor_origin_wrong_role/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_actor_origin_wrong_transition/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_backend_material_review_close_rejected/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_backend_publication_candidate_rejected/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_backend_self_acceptance_rejected/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_c2_authority_cross_actor_transplant/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_c2_authority_event_digest_mismatch/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_c2_authority_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_c2_authority_wrong_task/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_c2_no_authority/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_candidate_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_completion_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_completion_two_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_dispatch_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_exact_validation_artifact_pass/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_foreground_self_completion_rejected/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_model_origin_missing/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_provider_role_edge_mismatch_rejected/index.md`
- `.ai/communication_compliance/fixtures/artifacts/proof/transition_revision_loop_pass/index.md`
- `.ai/communication_compliance/fixtures/index.md`
- `.ai/communication_compliance/index.md`
- `.ai/index.md`
- `06_Silicon_Index/factory_pipeline/index.md`
- `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/index.md`
- `08_Domain_Applications/Math_Mentor/index.md`
- `08_Domain_Applications/Math_Mentor/p0_control_plane/schemas/index.md`
- `08_Domain_Applications/Math_Mentor/tests/p0_control_plane/fixtures/admission/index.md`
- `08_Domain_Applications/Math_Mentor/tests/p0_control_plane/fixtures/authorization/index.md`
- `08_Domain_Applications/Math_Mentor/tests/results/index.md`
- `generate_repository_indexes.py`
- `index.md`
- `repository_index_manifest.json`
- `system_backbone/apicurio_registry_hub/index.md`
- `system_backbone/domain_knowledge/index.md`
- `未完成任务备忘录.yml`

## Correction-specific deltas

- 18 structurally verified schemas move from implementation/generated-evidence classes to `schema_definition / schema`.
- 99 structured records receive corrected safe-anchor output; all 17 exact-duplicate cases in the previously published manifest become duplicate-free.
- 72 records retain distinct same-key values through safe path-qualified anchors.
- structural audit metadata is persisted for all 1,169 readable JSON/YAML records in the manifest; protected metadata-only boundaries remain unread.
