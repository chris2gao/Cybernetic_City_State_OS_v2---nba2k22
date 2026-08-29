# T2 Stage 04 独立测试生成派单 v1

## Role

你是本任务的独立 Stage 04 test designer。你不能参与 B 的作者推理，也不能把 B 的文件名/实现偏好直接当成功条件。

优先使用新的 Anthropic 会话；若当前 Human 可用 Claude Opus 5，使用 Claude Opus 5。否则使用当前 Human 可用的最强 Anthropic 模型，并如实记录 exact model/UI surface。若 reasoning/effort 不暴露，记录 `not_exposed`。

## Repository / task

Repository:

`chris2gao/Cybernetic_City_State_OS_v2---core`

Task:

`os-v2-role-window-context-model-routing-integration-001`

Branch:

`dev/os-v2-role-window-context-model-routing-integration-001`

开始时 fresh-read 远端 task branch HEAD 与 master 40 位 SHA。聊天中的 SHA 只作 pointer。

## Write boundary

本轮只允许新增/修改：

`01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/04_测试生成/**`

禁止修改 A、Stage02、B、run.yml、任何 canonical、master。

## Inputs

先按 repository bootstrap 加载，然后仅加载：

1. `01_os/01_workflow/04_测试生成/README.md`
2. 本 run `01_需求建模/requirement/A_需求建模_v1.yml`
3. `01_需求建模/requirement/人类确认_v1.yml`
4. `02_信息收集与提炼/evidence/00_挖掘目标与领域_v1.yml`
5. `02_信息收集与提炼/evidence/01_内部证据_v1.yml`
6. `02_信息收集与提炼/evidence/02_外部检索_v1.md`
7. `02_信息收集与提炼/evidence/证据索引_v1.yml`
8. `02_信息收集与提炼/evidence/可行性判断_v1.yml`
9. `02_信息收集与提炼/evidence/边界记录_v1.yml`
10. `03_结果建模/B_结果模型_v1.yml` —— 只用于识别候选结果面，不作为测试依据来源
11. current canonical `context_management`, `model_routing`, `communication_system` contracts and their validators/boot/registry
12. `AGENT_WORKING_DISCIPLINE.md` role/independence section and `01_os/开发入口与单窗口任务规范_v1.md`

不要默认加载全部历史 `_runs/**`。

## Defining rule

**测试由 A + evidence 推导，不由 B 推导。**

如果 B 的实现偏好没有 A/evidence 支持，不得冻结成测试。若发现 B 与 evidence 不一致，记录 finding 并让对应测试能失败，而不是迎合 B。

## Required coverage

冻结测试至少覆盖以下行为面；具体 test IDs、fixtures、mutations 由你独立设计：

### Role contract

- provider-independent role source exists for the real roles required by A;
- backend execution role is retained rather than re-invented;
- role metadata cannot grant publisher/filesystem/security/Human-gated authority;
- obvious duplicate mutable role table/pointer drift is detectable.

### Formal window identity

- formal window has project-level unique `window_id` bound to task/run/role/stage-step/repository facts;
- `fresh`, `reentry`, `forked_successor` semantics are distinguishable;
- formal reentry requires exact predecessor/window identity;
- `latest session` / `most recent conversation` alone must not count as formal identity;
- host session identifier may be `not_observable`; tests must not require a provider-specific host ID.

### Context binding

- minimum context binding points to `context_management` rather than copying its policy;
- stale/broken dependency/context refs fail visibly;
- no silent fallback to full historical `_runs/**` or old chat.

### Model routing binding

- role/task requirements become model-routing inputs without hard-coding provider into role architecture;
- routed windows bind a real model-routing receipt with version/load/validator/route/limitations/availability fields;
- route authority remains `routing_only` and cannot alter task authority;
- missing/stale/inconsistent route receipt fails closed.

### Independence

- independent-review window cannot reuse the implementation project window identity;
- when a task requires `different_model_family=true`, obvious same-family review must fail;
- do not pretend to prove hidden provider session freshness when host identity is not observable; freeze only what can actually be checked plus required disclosure/assertion fields.

### Handoff

- structured handoff carries from-window/task/role, next-role expectation, outputs, blockers/findings, exact refs, invalidation conditions and unchanged authority boundary;
- no private chain-of-thought field;
- handoff does not imply automatic delivery, acceptance or task progression;
- communication-system message transport and work-window handoff semantics remain separable.

### Failure surfacing / composition

- unknown role, duplicate/missing window identity, task/branch/head mismatch, invalid reentry, stale context, bad route receipt, independence violation, role mismatch and broken pointers must fail closed;
- composition validation may invoke existing mechanism validators, but tests must reject duplicated context/model semantics as a substitute;
- existing context/model/communication validators and publisher/protected-action controls remain intact.

### Explicit non-goals

Tests must reject accidental introduction of:

- scheduler / watcher / daemon / automatic window spawn;
- automatic handoff delivery / task progression;
- automated quota/account probing;
- T3 archive/retention semantics;
- T4 long-running autonomous continuation;
- provider-specific role architecture.

## Test package quality

Build positive, negative and boundary tests. Prefer executable fixtures/mutations over token-presence checks. Any lexical scan must distinguish evidence/source citation from runtime semantics and must document false-positive boundaries.

The package must be capable of failing the current unimplemented repository for the missing T2 mechanism while keeping the known-good existing context/model/communication mechanisms green.

At least one good fixture and multiple independent mutations are required. Mutation selftest should prove the harness kills the intended defects rather than merely parsing files.

## Freeze

Produce a new frozen Stage04 package under this run, with:

- versioned test artifact;
- normalized digest over the actual frozen test payload;
- freeze receipt binding A, Human confirmation, Stage02 evidence, B and harness/fixture hashes;
- counts by positive/negative/boundary;
- selftest result;
- current-repository baseline acceptance result, expected to be red because T2 canonical is not implemented yet.

Do not modify tests after freeze without a later Human-gated correction.

## Git

Normal commit + push this task branch only. No force/rebase/squash/amend/history rewrite. Master remains unchanged.

After push fresh-read task branch and master.

## Completion marker

`stage04_t2_frozen_tests_ready_for_stage05`

Report exact source base/head, resulting remote head, frozen digest, test counts, selftest result, current baseline pass/red counts, changed paths and any evidence/B contradiction.
