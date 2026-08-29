# T2 Stage 04 第二轮窄修正派单 v3

## 1. Task identity

- repository: `chris2gao/Cybernetic_City_State_OS_v2---core`
- task_id: `os-v2-role-window-context-model-routing-integration-001`
- run_id: `run-20260812-角色窗口上下文模型路由集成-001`
- branch: `dev/os-v2-role-window-context-model-routing-integration-001`
- correction_round: `2`
- target_artifact_version: `3`
- Human authorization: `04_测试生成/Stage04_Human窄修正授权_v2.yml`
- governing proposal: `04_测试生成/Stage04_v2_FIX_REQUIRED接收与Human窄修正提案_v1.yml`
- independent review evidence: `04_测试生成/独立接收审核/v2/**`

## 2. Entry / physical preflight

Before editing, fresh-read the remote task branch and remote `master`. Do not trust any SHA in chat as physical fact.

If this is the original Claude Opus 5 Stage04 test-design/correction session after a session reset, record `entry_mode: explicit_reentry` and re-read task/head/authorization from the repository. If that exact session is not identifiable, use a fresh Claude Opus 5 correction session and record `entry_mode: fresh`.

Do not touch the pre-existing `routing-002` worktree or its untracked T1 file. Work only in a dedicated sibling worktree for this T2 branch.

## 3. Scope

This is a Human-authorized narrow Stage04 frozen-package correction. Stage01, Stage02 and Stage03 remain valid. Do not redesign B or implement canonical T2.

You must close exactly:

- `ST04-V2-IR-001`
- `ST04-V2-IR-002`
- `ST04-V2-IR-003`
- `ST04-V2-IR-004`
- `ST04-V2-IR-005`
- `ST04-V2-IR-006`

### Required semantic fixes

1. **RW-T25 / prohibition shapes** — accept semantically equivalent prohibition declarations including `*_disabled: true`, `*_prohibited: true`, `*_forbidden: true`, `*_disallowed: true`, while still rejecting genuinely enabled private-reasoning/delivery/acceptance state.
2. **RW-T08/RW-T09 / entry mode containers** — normalize mapping and list-of-record representations. Freeze fresh-versus-reentry separability and exact predecessor semantics, not container shape or field spelling beyond what semantic discovery genuinely requires.
3. **RW-T19 / provider pin structures** — detect normative provider/model pins across scalar, list and mapping structures, including mapping keys such as `preferred_provider: {openai: true}`. Provenance/evidence exclusion must be subtree/segment aware and must not swallow normative `preferred_*` fields.
4. **RW-T05/RW-T31 / role applicability** — YAML or Markdown applicability matrices must not become a second canonical role source merely because they contain role names plus generic `scope/context` metadata. Require genuine role source-of-truth properties such as responsibility, independence constraints, handoff direction, authority limits, or equivalent normative ownership semantics.
5. **RW-T43 / model catalog duplication** — detect a second mutable model catalog across structured Markdown forms including tables and definition lists, without rejecting thin pointers, validator calls, receipt fields or prose references to `model_routing`. Live model identifiers must come from the tested tree rather than hard-coded model names.
6. **RW-T37..RW-T42 / validator probes** — stop using or expanding the history-scanning dependency crawler for the acceptance probe. Build the conforming candidate tree and run the mechanism's declared validator directly against that **full candidate tree**. Preserve zero-before / non-zero-after semantics for each injected defect. Do not use T3-style archive/history closure logic to solve this T2 test problem.

`RW-T06` remains valid and must not be weakened or removed.

## 4. Allowed changed paths

Only:

- `04_测试生成/04_tests.yml`
- `04_测试生成/实现/**`
- `04_测试生成/fixtures/**`
- `04_测试生成/测试设计说明_v3.md`
- `04_测试生成/freeze_receipt_v3.yml`

Paths are relative to:

`01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/`

The test count may change. Do not preserve 43 merely for numerical continuity.

## 5. Must remain byte-unchanged

At minimum:

- `04_测试生成/freeze_receipt_v1.yml`
- `04_测试生成/freeze_receipt_v2.yml`
- `04_测试生成/独立接收审核/Stage04冻结测试包独立接收裁决_v1.yml`
- all existing `04_测试生成/独立接收审核/v2/**`
- `04_测试生成/Stage04_Human窄修正授权_v1.yml`
- `04_测试生成/Stage04_Human窄修正授权_v2.yml`
- `04_测试生成/Stage04_v2_FIX_REQUIRED接收与Human窄修正提案_v1.yml`
- A / Stage02 / B
- `run.yml`
- all canonical files
- `master`

No force, rebase, squash, amend or history rewrite.

## 6. Required adversarial coverage

Import the v2 independent reviewer findings as regression targets, not as implementation instructions.

At minimum, the v3 selftest must include semantic coverage equivalent to:

- V10: `*_disabled: true` prohibition representation remains fully green.
- V11: list-of-record fresh/reentry representation remains fully green.
- V12: mapping-shaped normative provider pin turns the appropriate provider-independence check red.
- V13: YAML role/stage/context applicability matrix remains fully green.
- V15: Markdown definition-list second mutable model catalog turns A11 catalog-thinness check red.
- full-candidate-tree validator probes: clean candidate validator exits zero; each injected RW-T37..RW-T42 defect makes the mechanism's own validator exit non-zero.

Add additional conforming variants where the correction logic creates a new obvious representation boundary. Do not merely encode the reviewer's exact fixture strings.

## 7. Freeze v3 requirements

Create `freeze_receipt_v3.yml` and increment the frozen artifact to version 3. It must bind:

- source head before correction;
- Human authorization v2;
- v2 independent review and probe evidence;
- exact changed paths;
- new normalized digest;
- test counts;
- package validation result;
- selftest result, mutation kill result, conforming-counterexample result and boundary probes;
- current canonical preimplementation baseline;
- `RW-T06` retained status;
- explicit statement that full candidate tree, not dependency crawler, is used by RW-T37..RW-T42;
- known limitations and no semantic-completeness claim.

The current repository should remain red for unimplemented T2 functionality except preservation checks that are already true.

Run `git diff --check` on the correction primary diff.

## 8. Publication

Before push, fresh-read the remote task branch. Push only by ordinary fast-forward. If remote drift contains anything other than known foreground governance commits or your own correction ancestry, stop and report the physical conflict.

Do not update `master`.

## 9. Completion

Return exact source base, resulting remote head, master, changed paths, digest, test counts, package/selftest/baseline results, and blocker-by-blocker closure evidence.

Completion marker:

`stage04_t2_v3_corrected_frozen_tests_ready_for_fresh_independent_acceptance`

Stage05 remains blocked until a new independent acceptance review passes.
