# Stage 07 最终独立复核派单 v2

## 角色

你是本任务的 **fresh final Stage 07 independent reviewer**。

必须使用全新会话；不得复用：

- Stage 06 Codex implementation/correction 会话；
- 产出最初 F1/F2/F3 的 Stage 07 reviewer 会话；
- 随后执行 Stage 04 narrow correction 的同一个 Claude 会话。

推荐：Claude Opus 5，新的 Claude Desktop Cowork 或 Claude Code Desktop 会话均可，只要能 fresh-read / write 当前正式分支。
若 surface 没有 reasoning/effort 控件，记录 `reasoning_setting: not_exposed`，不构成 blocker。

你是 reviewer，不是 implementation fixer。发现 blocker 只报告，不修改 canonical。

## Repository / branch

Repository:

`chris2gao/Cybernetic_City_State_OS_v2---core`

正式分支：

`dev/os-v2-global-model-capability-and-availability-routing-002`

开始时 fresh-read 远端分支 HEAD 与 master 40 位 SHA。聊天或派单中的 SHA 只能作为 pointer，不是事实来源。

严禁使用 quarantined：

`dev/os-v2-global-model-capability-and-availability-routing-001`

## 当前候选链

初始 Stage 06 implementation：

`3e3b608ac2c265d6aa4eb31471e8f1eae05603a4`

Stage 07 v1 发现三个 blocker 后，Stage 04 Human-gated refreeze 为 artifact v3 / 35 tests。

修正派单 base：

`5fee938ad24660269d76428398866b145bd9d622`

定点修正 implementation commit：

`150e800e683d69b31d1336d8a9c0ad6d21c90ff2`

执行方 evidence head：

`17e24eee8bfc58dfeb5d1a54f1d57310a5b21850`

之后可能只有 review-dispatch/run evidence 的正常 fast-forward；审核时必须从 physical Git 自行确认没有新的 canonical mutation。

## 最小加载集合

正常 repository bootstrap 后，额外只读取当前任务必要材料：

1. `01_os/01_workflow/07_测试执行/README.md`
2. `01_os/01_workflow/07_测试执行/实现/最小运行schema_v1.yml`
3. 本 run `01_需求建模/requirement/A_需求建模_v3.yml`
4. `02_信息收集与提炼/Stage02_证据结论_v2.yml`
5. `02_信息收集与提炼/证据对齐与冲突消解_v1.yml`
6. `03_结果建模/B_结果模型_v1.yml`
7. `04_测试生成/04_tests.yml` artifact v3
8. `04_测试生成/freeze_receipt_v3.yml`
9. `04_测试生成/实现/verify_stage04_acceptance.py`
10. `05_步骤拆分/05_steps_v2.yml`
11. `06_执行/Stage06_定点修正执行证据_v2.yml` —— 只作为 executor handoff，不当作独立证明
12. `06_执行/Stage06定点修正候选接收裁决_v2.yml` —— 只作为 routing/adjudication pointer，不当作最终证明
13. `07_测试执行/07_blocking_review_v1.yml` —— 了解原 F1/F2/F3，但必须自己复核关闭状态
14. 当前 canonical model_routing mechanism、boot、registry、loader 与开发入口 §7.1

不要默认加载全部历史 `_runs`。

## 审核原则

**不能只看 35/35 绿灯。** Stage 07 v1 已证明 test package 绿灯可能与 B/evidence 意图不同。

你必须同时完成：

1. physical Git / primary diff audit；
2. corrected frozen package 独立复现；
3. canonical mechanism 独立语义测量；
4. A / Stage02 / B 对 final candidate 的 claim-level review；
5. 原 F1/F2/F3 closure review；
6. 检查 corrected tests 没有制造新的 evidence laundering / overfit。

## Primary diff 必查

至少独立检查：

### 初始 implementation

`a97d32ddd24cc9a94aaedea8adb045d4cdf6308c...3e3b608ac2c265d6aa4eb31471e8f1eae05603a4`

### correction implementation

`5fee938ad24660269d76428398866b145bd9d622...150e800e683d69b31d1336d8a9c0ad6d21c90ff2`

以及从 `150e800e...` 到审核开始时 branch HEAD 的 diff，确认只有 evidence/dispatch/run 状态推进，没有偷偷继续改 canonical。

不要用 completion pointer 的 changed_paths 代替 primary diff。

## 必须独立运行的冻结测试

当前唯一活动 frozen package：

- artifact version: `3`
- test count: `35`
- expected normalized digest:
  `848b691712166a968c821ad6e53cafaf477b86bf7b1d7773306ad4e6ebf3e48c`

独立运行：

- `verify_stage04_acceptance.py package <run_root>`
- `verify_stage04_acceptance.py selftest <repo_root-or-required-arg>`
- `verify_stage04_acceptance.py acceptance <repo_root>`
- canonical `verify_model_routing.py static <repo_root>`
- `git diff --check` 对实现 range

要求实际记录 exit code、35 test 全集、mutation kill、digest，而不是复制 Stage06 evidence。

## 原 blocker closure 必查

### F1 — Opus 4.8 surface attribution

独立确认：

- Antigravity 当前 accepted evidence 只支持 Opus 4.6；
- Opus 4.8 不得继续绑定 antigravity；
- 若保留为 discovered/unregistered candidate，其 surface/source 必须符合 Stage02/B10。

### F2 — source resolution / evidence laundering

独立从**机制声明加载面**出发，不导入 Stage06 validator 的 helper，验证：

- catalog 的 `source_refs` 与 `surface_exposure_evidence` 可解析；
- resolution entry point 是 canonical 且从 boot/registry/loader 声明面可达；
- `GOOGLE_AG_PRICING` 等真实 provider source identity 被保留；
- 不存在把 `C08_Antigravity_Pro_access` 或其他 project claim id 冒充 source id 的情况；
- source index 的 locator 实际能指向 durable source/ref，而不是只满足字段非空。

`pricing/cost` 出现在 source ID/title/URL 不构成 cost-routing blocker。

### F3 — B13 failure surfacing

必须用 reviewer 自己的临时 mutation / measurement，至少确认 canonical mechanism validator 对以下代表性缺陷 non-zero fail closed：

1. registered entry bogus source ref；
2. unregistered entry bogus source ref；
3. registry path 指向不存在对象；
4. registry coverage 删除；
5. mechanism/catalog/source-index relevant version drift；
6. `price_weight` / `quota_balance` 等加入 routing-semantic structure；
7. required boot load-order pointer break；
8. registry/validator/source-index pointer break。

不要只调用 Stage04 selftest 后宣称这些成立；至少一套独立构造的 probes 由 reviewer 自己产生。

## 额外语义检查

主动检查：

- source index 是否只是把 Stage02 source registry机械复制成 canonical，但失去其 source class/locator 语义；
- catalog 中 registered/unregistered 的 freshness/source rules 是否一致且诚实；
- validator 的 economic-semantic 检测是否不会再次误伤 evidence citation，同时能抓 routing field；
- registry coverage 是否会因 wildcard 实现产生明显 false green；
- boot `catalog_version/source_index_version` 与实际 canonical 文件交叉绑定；
- §7.1 thinning、§8/§9/§11/T3/publisher authority 没有因 correction 被改坏；
- project observation ledger 仍把 Antigravity 旧运行保持 diagnostic，不出现 formal qualification 偷升；
- Cowork / Opus 5 仍作为本任务 scope 外 future observation，不因 reviewer 当前运行 surface 被事后塞进 catalog。

## Corrected Stage04 test package 本身也要审

Stage04 correction designer 与 Stage07 v1 finding author 实际是同一个 Claude 会话，该 overlap 已披露并被规划窗口仅对 correction 接受。

因此你必须独立检查 v3 tests 是否：

- 真正锚定 A + Stage02 evidence + B mapping；
- 没把 reviewer v1 的实现偏好冻结成无依据要求；
- MR-T25 已区分 evidence citation 与 economic routing semantics；
- MR-T30 只冻结当前 evidence 明确不支持的组合；
- MR-T31–T35 测的是 B13 行为，不是某个文件名/代码形状。

如果 corrected package 自身还有 blocker，判 `FIX_REQUIRED`；不要为了“已经 correction round 1”降低标准。

## 物理边界

Stage 07 reviewer 只允许新增：

`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/07_测试执行/**`

不得修改：

- canonical；
- run.yml；
- Stage04；
- Stage05；
- Stage06 evidence；
- completion pointers；
- A / Stage02 / B；
- master。

发现 blocker 只报告。

## 输出

若通过，至少新增：

- `07_verification_v2.yml`
- `最终独立复核报告_v2.md`

`07_verification_v2.yml` 必须符合 Stage07 minimal schema 的精神，绑定 Stage03/04/06 predecessor hashes，并包含：

- reviewer role / environment；
- verdict = `PASS` 或 `PASS_WITH_NON_BLOCKING_NOTES`；
- 35 条 frozen test results；
- implementation claims 对 B/evidence 的检查；
- F1/F2/F3 closure；
- upstream_invalidation: false；
- completion: true；
- primary diff scope；
- master / quarantined branch 状态；
- independent measurement 方法与结果；
- 未覆盖风险/非阻塞 notes。

若有 blocker，新增：

- `07_blocking_review_v2.yml`
- `最终独立复核报告_v2.md`

并写明 root cause、是否 upstream invalidation、建议 fix boundary；不要修实现。

## 修正预算

这是 correction round 1 后的 fresh review。

若仍有 blocking finding，项目 policy 尚余 **最多 1 个 post-delivery correction round**；reviewer 只报告，不自行开启 round 2。

## Git / publication

只在 `-002` 普通 commit + push Stage07 evidence。
禁止 force/rebase/squash/amend/history rewrite/master publication。

push 后 fresh-read remote branch HEAD、master HEAD，并报告实际值。

## 完成标记

通过：

`stage07_final_independent_verification_complete_ready_for_Human_integration_gate`

阻塞：

`stage07_final_independent_verification_fix_required`
