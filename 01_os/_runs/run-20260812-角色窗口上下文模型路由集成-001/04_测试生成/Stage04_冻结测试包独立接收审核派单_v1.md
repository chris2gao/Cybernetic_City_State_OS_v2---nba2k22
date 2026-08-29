# T2 Stage 04 冻结测试包独立接收审核派单 v1

## 任务

- task_id: `os-v2-role-window-context-model-routing-integration-001`
- run: `run-20260812-角色窗口上下文模型路由集成-001`
- branch: `dev/os-v2-role-window-context-model-routing-integration-001`
- frozen-package source base: `c354ddfec7607408766a52a7fccbdf6084f1bbb8`
- frozen-package candidate commit: `ef76b7812bd2b091ebbf7644d3396cad69bcd753`
- master basis: `9492fc940c58784297dc92d8602e5dfaad446d1a`

开始前 fresh-read 远端物理状态；聊天中的 SHA 只是 pointer。若 frozen-package candidate 不再是当前 branch history 中的精确祖先，或 master 已变化到不再是 branch ancestor，停止并报告。

## 审核角色与独立性

这是 **Stage 04 frozen-test-package acceptance review**，不是 Stage 03 B 重写，也不是 Stage 05。

推荐使用一个**新的 OpenAI/Codex 会话**，优先 `GPT-5.6 Sol` 与当前 surface 暴露的最高可靠 reasoning 设置。审核会话必须：

- 不是产生 `ef76b781...` 的 Claude Opus 5 / Cowork Stage04 test-designer 会话；
- 不携带该 test-designer 的私有上下文；
- 从 primary files 自行判断，不把 `freeze_receipt_v1.yml` 的结论当 proof；
- 如 host session freshness 不可技术观察，只作 disclosed assertion，不伪造 proof。

当前 foreground/Stage03 B 作者不担任本轮独立 acceptance reviewer。

## 只读输入

按需最小加载：

1. `01_需求建模/requirement/A_需求建模_v1.yml`
2. `01_需求建模/requirement/人类确认_v1.yml`
3. `02_信息收集与提炼/Stage02_证据结论_v1.yml`
4. `02_信息收集与提炼/evidence/证据索引_v1.yml`
5. `02_信息收集与提炼/evidence/01_内部证据_v1.yml`
6. `03_结果建模/B_结果模型_v1.yml` — 只用于检查测试是否意外冻结 B 偏好，不作为测试成功判据来源
7. `04_测试生成/04_tests.yml`
8. `04_测试生成/freeze_receipt_v1.yml`
9. `04_测试生成/测试设计说明_v1.md`
10. `04_测试生成/实现/verify_stage04_acceptance.py`
11. `04_测试生成/fixtures/mutations_v1.yml`
12. `04_测试生成/fixtures/overlay_edits_v1.yml`
13. `04_测试生成/fixtures/overlay/**`

不要 default-preload 其他 `_runs/**`。

## Primary diff

直接审核：

`c354ddfec7607408766a52a7fccbdf6084f1bbb8..ef76b7812bd2b091ebbf7644d3396cad69bcd753`

确认：

- 只有一个 frozen-package commit；
- changed paths 仅在当前 run 的 `04_测试生成/**`；
- canonical、A、Stage02、B、run.yml、master 未被 test-designer 修改；
- commit subject 的 UTF-8 BOM 只作历史瑕疵记录，不 amend/rewrite。

## 必须独立审核的语义问题

### 1. 测试来源独立性

逐类抽样并攻击 42 条测试，确认 pass/fail semantics 来自 A + accepted Stage02 evidence，而不是从 B 的文件名、机制名或实现偏好倒推。

特别检查：

- `role_contract.v` / `window_contract.v` / `handoff_contract.v` 是否可从 A 的 role/window/handoff 要求合理推出；
- mechanism 名与具体文件名是否真的未冻结；
- conforming overlay 使用 `window_role_binding` 只是 satisfiability witness，不应成为 canonical implementation template。

### 2. RW-T06 ownership / boundary

独立裁决 RW-T06：

`01_os/02_boot/context_management/启动清单_v1.yml` 不应继续把 `_dev/决定_谁执行_v0.2.md` 当 active role source。

不要因为 B 也提出过类似修改就自动接受。直接从 A01/A10、I02/I03/E-007 判断：当新的 canonical role source 存在后，保留旧 `_dev` active role source 是否会违反 single source of truth，且移除/重指针是否不构成 context_management 语义重设计。

输出必须明确：`RW-T06_valid` 或 `RW-T06_overreach`，并说明 Stage05/06 boundary 是否应包含：

`01_os/02_boot/context_management/启动清单_v1.yml`

### 3. mutation/selftest 辨识力

不要把 `42/42 killed` 当充分性证明。独立检查：

- 每个 mutation 是否真正产生 requirement violation，而非只破坏 fixture 字面；
- target test 是否因为目标语义而红，而不是因为 mutation 顺手破坏无关 parse/schema；
- collateral reds 是否不会掩盖 target test 实际不可失败；
- 至少抽样 role/window/context/model/handoff/authority/autonomy/validator 各一类 mutation；
- RW-T37..T42 是否真的要求 **机制自身 validator** 在 unmutated baseline green 后对 injected defect non-zero，而非只由 outer harness 报红。

### 4. False-positive / false-negative 风险

重点攻击：

- RW-T05 “第二份角色表”的双重条件是否足以避免把 model catalog / stage profiles 误判成 role source；
- RW-T19 provider-independent scan 是否只落在 role contract，不误伤 model-routing surface；
- RW-T25/RW-T34..T36 是否按结构/key 位置判断，而不是重复 T1 MR-T25 的原文 substring 误伤；
- RW-T30 对已有机制/boot index 漂移只做 T2-local requirement，是否合理避免把既有 unrelated debt 冻结进本任务；
- runtime-only 行为是否被诚实降格为 declaration/contract checks，而没有伪造尚不存在的 runtime proof。

### 5. Frozen package 完整性

独立运行并记录实际结果（能运行时）：

- package validation；
- selftest；
- acceptance against current pre-implementation repository；
- normalized digest recomputation；
- `git diff --check c354ddf...ef76b78`。

预期 pointer，仅供比对，不得直接采信：

- digest `d4fd85889a73e8dd313065e355290992cbf166fa6034420efe9f9c68974996e1`
- tests 42 = positive 17 / negative 16 / boundary 9
- good tree 42/42
- mutations killed 42/42
- current repository baseline 3/42 green

如当前环境不能真实执行命令，必须写 `not_run`，不得用 executor receipt 冒充独立复现。

## 已知 finding 的裁决边界

以下不是自动结论，独立 reviewer 可重新判断：

- mechanism/boot README index 既有漂移；
- B13 未规定 composition validator 是否必须调用三个已有 validator；
- commit message BOM；
- original routing-002 worktree 与其 T1 untracked file 未触碰。

不要顺手修任何 finding。

## 写边界

本 reviewer 只允许新增：

`01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/04_测试生成/独立接收审核/**`

不得修改：

- `04_tests.yml`
- `freeze_receipt_v1.yml`
- harness / fixtures / mutations
- A / Stage02 / B
- `run.yml`
- canonical
- master

不得 force/rebase/squash/amend/history rewrite。

## 输出

至少生成：

`04_测试生成/独立接收审核/Stage04冻结测试包独立接收裁决_v1.yml`

裁决只允许：

- `ACCEPTED_FOR_STAGE05`
- `FIX_REQUIRED`
- `REJECTED`

如果 ACCEPTED，必须明确给出：

- primary diff scope verdict；
- independent reproduction 状态；
- test-derived-from-A/evidence verdict；
- B-overfit verdict；
- RW-T06 verdict；
- mutation/selftest adequacy verdict；
- frozen digest；
- Stage05 boundary implication；
- non-blocking notes。

完成标记：

- pass: `stage04_t2_independently_accepted_for_stage05`
- fix: `stage04_t2_independent_review_fix_required`
- reject: `stage04_t2_independent_review_rejected`

正常 fast-forward push 当前 T2 task branch，push 后 fresh-read remote head。