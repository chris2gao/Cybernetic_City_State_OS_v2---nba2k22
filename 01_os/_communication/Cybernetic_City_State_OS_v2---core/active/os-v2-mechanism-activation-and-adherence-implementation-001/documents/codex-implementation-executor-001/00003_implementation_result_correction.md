---
document_id: os-v2-mechanism-activation-and-adherence-implementation-001-result-correction-001
task_id: os-v2-mechanism-activation-and-adherence-implementation-001
author_endpoint_id: codex-implementation-executor-001
author_task_role: implementation_executor
purpose: corrected_final_candidate_for_fresh_independent_acceptance
privacy_class: repository_shareable
supersedes: documents/codex-implementation-executor-001/00001_implementation_result.md
---

# Correction: final hardened implementation candidate

The earlier result remains immutable but its candidate
`c302b426bce27ded020761687293d0d032d8e316` is superseded. Exact Git readback of
that result exposed a Windows long-path failure, and follow-up adversarial review
found additional evidence-binding gaps. The final candidate is
`8fa49cc3a7eb082d4ffcee984652b77080d1b9f9` on
`dev/os-v2-mechanism-activation-and-adherence-implementation-001`; it descends from
task-bound base `bf538e5068381becd31e8e1daceade81e657262d`.

The correction adds:

- Windows `core.longpaths=true` exact Git blob reads for long communication paths;
- unique material claim IDs and registered comparator/claim-role bindings;
- moving-ref identity equality and narrow exact-or-`/**` path allowlist semantics;
- exact v2 pointer bindings for manifest, endpoint roles, sender index, routing
  purpose, canonical publisher, evidence paths and correction target;
- receiver replay of resolver/gate inputs plus exact-commit contract and publisher
  existence checks.
- Windows long-path support in Git convergence and a structurally valid durable
  task run state.

Final observed validation:

- 94/94 candidate-bound deterministic tests passed; three static validators and
  the repository default gate (4/4) passed;
- frozen Stage04 production suite: 50/50 passed;
- frozen Stage04 mutation/bypass suite: 50/50 rejected the mutations;
- nine two-sided candidate/base/scope/execution/artifact claims recomputed
  `VERIFIED`;
- the already published `2e58ec8e...:.../00001_result.yml` long-path pointer was
  physically read and receiver-bootstrapped with publication and sender-index
  bindings `VERIFIED` by the final candidate code.

Exact evidence:

- `01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/05_候选冻结/candidate_spec_v3.yml`
- `01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/07_测试执行/bound_candidate_checks_v3.yml`
- `01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/07_测试执行/frozen_stage04_full_candidate_v3.yml`
- `01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/07_测试执行/frozen_stage04_mutation_candidate_v3.yml`
- `01_os/_runs/run-20260813-mechanism-activation-and-adherence-implementation-001/07_测试执行/candidate_material_receipt_v3.yml`

The effectiveness inventory still claims at most L3. L4 and
`operationally_active` remain prohibited until a fresh isolated independent
implementation acceptance verifies this exact final candidate. Master publication
or merge remains outside the current authorization.
