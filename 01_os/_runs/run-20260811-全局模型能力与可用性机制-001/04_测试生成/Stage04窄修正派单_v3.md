# Stage 04 窄修正派单 v3

## 角色

你是 **Stage 04 independent test designer — correction round**。

推荐执行环境：新的 Claude Opus 5 会话。必须与 Stage 06 Codex executor 不同会话、不同模型族。
如果当前 Claude surface 无 reasoning/effort 控件，记录 `reasoning_setting: not_exposed`，不构成 blocker。

你不是 implementation executor，也不是最终 Stage 07 reviewer。你只修正已经被独立复核证明存在 gap/overfire 的冻结测试包，然后重新冻结。

## Repository / branch

Repository:

`chris2gao/Cybernetic_City_State_OS_v2---core`

正式分支：

`dev/os-v2-global-model-capability-and-availability-routing-002`

派单生成前已知分支 head 会继续因本派单/授权证据产生正常 fast-forward；开始时必须 fresh-read 远端物理状态，不采信聊天 SHA 作为事实。

严禁使用：

`dev/os-v2-global-model-capability-and-availability-routing-001`

该分支已 quarantine。

## Human gate

读取：

- `04_测试生成/Stage04_Human窄修正授权_v1.yml`
- `07_测试执行/Stage07阻塞接收与回退裁决_v1.yml`
- `07_测试执行/07_blocking_review_v1.yml`

Human 已把本次 Stage 07 blocker 的 workflow 回退选择委托给规划窗口；规划窗口已裁决 **Stage 02/03 不失效，Stage 04 窄重开**。

本轮只允许写：

`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/04_测试生成/**`

不得修改 canonical、run.yml、Stage05/06/07、A、Stage02、B 或 completion pointer。

## 最小加载集合

按正常 repository bootstrap 后，只额外读取：

1. `01_os/01_workflow/04_测试生成/README.md`
2. `01_os/01_workflow/04_测试生成/实现/最小运行schema_v1.yml`
3. 本 run 的 `01_需求建模/requirement/A_需求建模_v3.yml`
4. `02_信息收集与提炼/证据对齐与冲突消解_v1.yml`
5. `02_信息收集与提炼/Stage02_证据结论_v2.yml`
6. `03_结果建模/B_结果模型_v1.yml` —— 仅用于 claim mapping，测试仍须由 A + evidence 推导
7. 当前 `04_测试生成/04_tests.yml`
8. 当前 `04_测试生成/实现/verify_stage04_acceptance.py`
9. 当前 `04_测试生成/fixtures/**`
10. `04_测试生成/freeze_receipt_v2.yml`
11. 上述 Human correction authorization 与 Stage07 blocker adjudication/review

不要默认加载全部历史 `_runs`。

**不要以当前 Stage06 canonical 实现的具体代码结构作为测试设计输入。** reviewer finding 可以作为“某类缺陷确实可发生”的新证据，但 corrected test 的成功语义必须回到 A / Stage02 evidence / B claim mapping。

## 为什么必须重开 Stage 04

旧 package 的 28/28 已被独立 reviewer 证明“不充分”：

### Gap 1 — source refs 只测非空，不测可解析

旧 MR-T10 允许 catalog 写任意非空 token 当 source_ref。实际 candidate 的 10 个 token 从机制 declared load surface 无一可解析；其中 `C08_Antigravity_Pro_access` 甚至是 claim ID，不是 source ID。

Stage02 `证据对齐与冲突消解_v1.yml` 已有真实 `source_registry`，包括：

- `OAI_CHATGPT_56`
- `OAI_GPT56_RELEASE`
- `OAI_CODEX_APP`
- `ANTH_CODE_MODELS`
- `ANTH_PRO_CODE`
- `ANTH_CODE_USAGE`
- `GOOGLE_AG_MODELS`
- `GOOGLE_AG_PRICING`
- `GOOGLE_AG_36`
- `GEMINI_PASS`

corrected tests 必须要求 canonical mechanism 有一个从其正常 declared load surface **可到达的 source-resolution entry point**，使 catalog 中使用的 source refs 可解析到耐久来源/引用。

**不要过拟合 source index 的具体文件名。** 可冻结“存在 canonical/reachable resolution contract”及其可验证行为，而不是指定必须新增某个特定文件。

### Defect 2 — MR-T25 lexical overfire

旧 MR-T25 对机制文本逐行扫描 `price/pricing/cost/quota` 等 token。Stage06 使用真实一手来源 `GOOGLE_AG_PRICING` 时被 `PRICING` 子串误伤，executor 为让灯变绿把真实 source identity 换成 Stage02 claim ID。

这不是 cost-routing 行为，而是 evidence citation。

corrected negative test 必须区分：

- **禁止**：routing input、decision/scoring、fallback/scheduler 等语义位置出现 cost/token/quota optimization；
- **允许**：source id、source title、URL、evidence metadata 中为了引用真实来源而出现 `pricing` / `cost` 字样；
- **允许**：明确的 prohibition declaration 本身包含这些词。

不得再用“任意文本命中经济词即失败”的全文件词法扫描作为唯一判据。

### Gap 3 — unsupported surface/model attribution

Stage02 C07/C08 只证明 Antigravity 当前有 Claude Opus 4.6；B10 把 Opus 4.8 描述为 Anthropic entitlement-conflict discovered/unregistered candidate。candidate 却出现：

`surface_id: antigravity` + `model_label: Claude Opus 4.8`

且 cited sources 不支持该绑定。

corrected tests 必须能让这种**已知证据矛盾的 surface/model attribution**失败，包括 `registered:false` 情况。

可以针对当前证据集冻结明确的 known-impossible/unsupported combination；不要假装测试程序能自动理解任意未来网页语义。

### Gap 4 — mechanism validator 没有真正覆盖 B13

B13 要求失败可见。corrected tests 必须独立验证机制自己的 validator 对代表性错误 fail closed，而不只是 Stage04 外层 validator 自己发现错误。

至少设计可执行负例覆盖：

1. registered entry source ref 无法解析；
2. **unregistered entry** 使用无法解析/错误 source ref；
3. registry 声明的 path 不存在或 coverage 断裂；
4. boot/catalog/registry 的 relevant version binding 漂移，至少包括 catalog version 能被交叉核验；
5. routing contract 或其他 routing-semantic 结构中加入非法 cost/quota optimization field；
6. entry/preflight/boot/registry 中本机制声明必须可达的 pointer 断裂。

每个负例必须实际运行机制声明的 validator，并要求 non-zero exit。

## 对旧测试包的处理

这次是合法 Human-gated refreeze，不是假装旧 tests 从未存在。

要求：

- 保留 `freeze_receipt_v1.yml` / `freeze_receipt_v2.yml` 原样作为历史；
- `04_tests.yml` 升新 `artifact_version`；
- 可以修改旧 test、增加 test 或用更强等价 test supersede 旧 test；
- 不必保持 28 条固定数量；测试数量由 correction 需要决定；
- 必须生成新的 normalized `test_package_sha256`；
- 新 freeze receipt 明确 old digest `72898d54...` 已被 Human-gated corrected package supersede；
- 不能删除历史 mutation/fixture 来隐藏旧设计缺陷；如不再使用，标 superseded/retained_for_history。

## 对既有正确保证的保持

除被证明有缺陷/不充分的 test semantics 外，不得削弱旧 package 已验证的要求，尤其：

- independent global mechanism；
- Human availability override；
- `routing_only` authority；
- model × surface separation；
- surface-specific parameters；
- vendor vs project observation separation；
- diagnostic/anecdotal 不产生 hard qualification；
- §7.1 thinning；
- §8/§9/§11/T3/publisher controls 不削弱；
- no automatic fallback；
- no background quota/account probe；
- registry/boot/loader failure surfacing；
- publisher authority byte baseline 不变。

## Self-test 要求

corrected package 必须有独立 selftest，至少证明：

- good fixture 全绿；
- 每个新增/修改的 negative/boundary test 至少有一条 mutation 可以把它杀红；
- old 27 mutation 的仍适用部分继续被杀；
- `GOOGLE_AG_PRICING` 或等价含 `pricing` 的**真实 source identity/reference**不会单独触发 no-cost-routing test；
- 把 `price_weight` / `quota_balance` 等加入 routing decision/input/scoring 的 mutation 必须触发；
- unsupported `antigravity + Claude Opus 4.8` mutation 必须触发；
- unregistered entry bogus source mutation 必须触发机制 validator negative probe；
- broken registry path / version drift / pointer drift mutations必须触发机制 validator negative probe。

如果旧 Stage04 verifier 的结构不适合诚实表达这些测试，可以在本授权 boundary 内修改它；但不得读取 implementation 后“照着实现写一个必过 checker”。

## Stage 06 candidate baseline 应该怎样看

不要把当前 candidate 28/28 当 corrected package 的目标值。

corrected package 应当在当前 candidate 上**至少让已确认 F1/F2/F3 对应检查变红**。如果 corrected package 在当前 candidate 上仍全绿，说明本轮 correction 没有真正覆盖 reviewer blocker，应停止而不是冻结。

## 输出

至少产生：

- 更新后的 `04_tests.yml`
- 更新后的 `实现/verify_stage04_acceptance.py`（如需要）
- 更新/新增 fixtures/mutations（如需要）
- `Stage04窄修正测试设计说明_v1.md`
- 新 `freeze_receipt_v3.yml`

新 receipt 记录：

- exact input refs / hashes；
- old package version/digest；
- new package version/digest；
- corrected test IDs；
- retained unchanged test IDs；
- positive/negative/boundary counts；
- selftest 实际结果；
- current Stage06 candidate 的 corrected acceptance 实际红灯及对应 finding mapping；
- evidence honesty：本包由本 session 设计并自测，尚未由实现方/最终 reviewer 复现。

## Git / publication

只在 `-002` 上普通 commit + push。

禁止 force/rebase/squash/amend/history rewrite/master publication。

push 后 fresh-read remote head。

## 完成回传

pointer-only 为主，至少：

```yaml
completion_pointer:
  task_id: os-v2-global-model-capability-and-availability-routing-001
  stage: stage04_narrow_correction
  status: corrected_frozen_tests_ready_for_stage05_rebind
  branch: dev/os-v2-global-model-capability-and-availability-routing-002
  source_head: <fresh physical sha>
  resulting_remote_head: <fresh readback sha>
  old_test_package_sha256: 72898d54c86ca52449aa96f1dfaed0d6ca8153b93dbc9ae36089a9e8edb55478
  new_test_package_sha256: <actual>
  test_count: <actual>
  selftest: <actual>
  candidate_acceptance:
    passed: <actual>
    total: <actual>
    expected_blocker_tests_red: true
  changed_paths: <actual>
  out_of_scope_paths: 0
  master_modified: false
  quarantined_branch_reused: false
  force_push: false
```

完成标记：

`stage04_corrected_refreeze_ready_for_stage05_rebind`
