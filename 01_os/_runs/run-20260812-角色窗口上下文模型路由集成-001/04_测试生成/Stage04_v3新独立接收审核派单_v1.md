# T2 Stage04 v3 fresh independent acceptance review dispatch

Repository: `chris2gao/Cybernetic_City_State_OS_v2---core`

Task: `os-v2-role-window-context-model-routing-integration-001`

Branch: `dev/os-v2-role-window-context-model-routing-integration-001`

## Physical binding

Fresh-read remote branch and master before review. Do not trust chat SHAs as facts.

Review ONLY the Stage04 v3 correction primary diff:

`236e7c52c06804d58324c1113e007cb4608088f7..afad6fdd79e51aaae89e5517b29561d763049a8d`

The preceding commit `236e7c52c06804d58324c1113e007cb4608088f7` is a separate Human-authorized canonical retry-budget change. It is NOT part of the Stage04 v3 correction primary diff and must not be used to expand or narrow the Stage04 verdict.

## Independence

Use a fresh independent session. Prefer OpenAI/Codex family because the correction author is Claude Opus 5 / Cowork. Do not accept the freeze receipt, foreground check, mutation score, conforming score, or executor summary as proof.

## Required inputs

Read A, Human confirmation, Stage02 evidence/conclusion, B, both prior independent Stage04 review packages, Human correction authorizations, round-2 proposal/dispatch, `04_tests.yml`, `freeze_receipt_v3.yml`, `测试设计说明_v3.md`, the v3 harness and fixtures.

## Required attacks

Re-adjudicate all twelve previously accepted blocker families, with special emphasis on representation independence and on shapes not already listed by the author.

At minimum independently attack:

1. prohibition declarations beyond the exact declared examples, including negative suffix/prefix and mapping/list forms;
2. entry mode containers beyond mapping and list-of-record, while preserving only A-required fresh/reentry semantics;
3. provider/model pins nested in mappings/lists and provenance-like neighboring subtrees;
4. role applicability/reference matrices that mention role, scope, context, route, model or stage but do not own role semantics;
5. second mutable model catalogs in structured Markdown/YAML shapes beyond tables and definition lists;
6. RW-T37..RW-T42 mechanism-validator probes: verify they execute the mechanism's own declared validator against the FULL candidate tree, baseline exit 0 then injected defect non-zero, with no hidden history crawler topology;
7. check for false positives AND false negatives; declared mutations/conforming variants are not a completeness proof;
8. verify current canonical tree remains preimplementation red except legitimate preservation checks;
9. recompute package digest and verify frozen input/supporting-ref hashes;
10. `git diff --check` on the exact v3 primary diff.

Also adjudicate foreground note `V3-FG-N01`: the harness top-level docstring still says artifact_version 2 / correction round 1. Determine whether this is nonblocking stale provenance text or a package-integrity defect. Do not modify the frozen package during review.

## Write boundary

Only add files under:

`01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/04_测试生成/独立接收审核/v3/**`

Do not modify frozen tests/harness/fixtures/receipts, A, Stage02, B, run.yml, canonical files, the retry-budget commit, or master.

## Verdicts

- `ACCEPTED_FOR_STAGE05`
- `FIX_REQUIRED`
- `REJECTED`

PASS marker if and only if accepted:

`stage04_t2_v3_independently_accepted_for_stage05`
