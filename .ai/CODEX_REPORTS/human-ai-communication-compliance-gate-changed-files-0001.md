# Human–AI Communication Compliance Gate — Exact Changed Paths

The candidate contains 30 intended paths, all within the task allowlist.

## Canonical protocol bindings (6)

1. `.ai/PROTOCOL.md` — defines the executable C0/C1/C2 repository gate,
   transition evidence, external C2 authority, runtime boundary, and drift rule.
2. `.ai/PROTOCOL_ADHERENCE.md` — makes the executable check mandatory before
   C1/C2 advancement and adds it to the audit checklist.
3. `.ai/HANDOFF_INIT_PROMPT.md` — adds bootstrap receipt and gate onboarding
   obligations plus capability-boundary questions.
4. `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` — binds backend handoff/transition
   claims to durable gate evidence.
5. `.ai/CODEX_TASK_INPUT_CONTRACT.md` — relocates optional routing metadata and
   validation/authority refs outside the frozen seven-key pointer mapping.
6. `.ai/DECISIONS.md` — records repository-gate decision D-0006.

## Drift ledger (1)

7. `.ai/COMMUNICATION_DRIFT_LEDGER.yml` — initial append-only, privacy-safe
   ledger with recurrence threshold two and no fabricated historical records.

## Gate implementation and contracts (10)

8. `.ai/communication_compliance/README.md`
9. `.ai/communication_compliance/material_event_policy.yml`
10. `.ai/communication_compliance/validate_communication.py`
11. `.ai/communication_compliance/authorization_context.schema.json`
12. `.ai/communication_compliance/bootstrap_receipt.schema.json`
13. `.ai/communication_compliance/communication_drift_ledger.schema.json`
14. `.ai/communication_compliance/communication_event.schema.json`
15. `.ai/communication_compliance/communication_validation.schema.json`
16. `.ai/communication_compliance/drift_record.schema.json`
17. `.ai/communication_compliance/transition_request.schema.json`

## Fixtures and tests (10)

18. `.ai/communication_compliance/fixtures/build_fixture_suite.py`
19. `.ai/communication_compliance/fixtures/fixture_suite.json`
20. `.ai/communication_compliance/fixtures/latest_fixture_result.json`
21. `.ai/communication_compliance/fixtures/artifacts/complete_dispatch_brief.md`
22. `.ai/communication_compliance/fixtures/artifacts/complete_review_brief.md`
23. `.ai/communication_compliance/fixtures/artifacts/incomplete_dispatch_brief.md`
24. `.ai/communication_compliance/fixtures/raw/pointer_anchor_alias.yml`
25. `.ai/communication_compliance/fixtures/raw/pointer_duplicate_keys.yml`
26. `.ai/communication_compliance/fixtures/raw/pointer_multidoc.yml`
27. `.ai/communication_compliance/tests/test_validate_communication.py`

## Durable reports (3)

28. `.ai/CODEX_REPORTS/human-ai-communication-compliance-gate-0001.md`
29. `.ai/CODEX_REPORTS/human-ai-communication-compliance-gate-validation-0001.md`
30. `.ai/CODEX_REPORTS/human-ai-communication-compliance-gate-changed-files-0001.md`

## Explicitly unchanged

- `.ai/INBOX.md`
- `.ai/OUTBOX.md`
- `.ai/STATE.yml`
- `.ai/HUMAN_BRIEF.md`
- `3号方案.md`
- `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`
- all `08_Domain_Applications/**` paths
- all `system_backbone/**` paths
- all runtime, Coordinator, bridge, writer, consumer, and UI implementation
  paths

No deviation outside the allowed path families occurred.
