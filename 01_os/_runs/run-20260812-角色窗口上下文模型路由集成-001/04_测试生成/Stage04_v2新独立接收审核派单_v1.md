# T2 Stage 04 v2 · 新独立接收审核派单

## 任务

对 Human-gated 窄修正后的 Stage 04 frozen test package artifact_version 2 做新的独立接收审核。

Repository:

`chris2gao/Cybernetic_City_State_OS_v2---core`

Task:

`os-v2-role-window-context-model-routing-integration-001`

Branch:

`dev/os-v2-role-window-context-model-routing-integration-001`

被审核 correction primary diff：

`e76ffb6305c8e015979a8b8f6c81821186b1fb49..c720988454e120bed9e6acbe63146c83144866f6`

artifact_version 2 digest claim：

`993658e84f7481d1c96fe48d074a3ef401831d05f5da44c38c28295874df3848`

开始审核时必须 fresh-read 远端 branch HEAD 与 master；本文件中的 SHA 只作为 expected pointer，不作为事实源。若 branch 已由 foreground 追加本审核派单/run-state commit，应把这些后续 foreground commits 排除在 corrected-package primary diff 之外。

## 审核身份

必须使用新的独立会话。优先不同于 Stage04 设计者的模型族：

- provider family: OpenAI
- preferred surface: Codex Desktop
- preferred model: 当前 Human 可用的最强 OpenAI coding/review model；若可见 GPT-5.6 Sol，优先 Sol
- reasoning setting: 使用当前 surface 暴露的最高可靠设置；若不可观察，明确记录 `not_observable`

不得使用本 foreground/B-author 窗口作为最终接收 reviewer；不得使用 Claude Opus 5 correction author 自审。

## 必读材料

1. `01_需求建模/requirement/A_需求建模_v1.yml`
2. `02_信息收集与提炼/Stage02_证据结论_v1.yml`
3. `02_信息收集与提炼/evidence/证据索引_v1.yml`
4. `03_结果建模/B_结果模型_v1.yml` —— 仅作 candidate result surface，不是测试成功标准来源
5. `04_测试生成/04_tests.yml`
6. `04_测试生成/freeze_receipt_v2.yml`
7. `04_测试生成/实现/verify_stage04_acceptance.py`
8. `04_测试生成/fixtures/mutations_v2.yml`
9. `04_测试生成/测试设计说明_v2.md`
10. `04_测试生成/独立接收审核/Stage04冻结测试包独立接收裁决_v1.yml`
11. `04_测试生成/Stage04_Human窄修正授权_v1.yml`
12. `04_测试生成/Stage04_v2修正候选前台初核_v1.yml` —— 只作为 foreground claim，不得当 proof

## 必须独立确认的物理事实

- corrected package primary diff 是否恰为一个 correction commit；
- correction commit 的 changed paths 是否全部在 Human 授权写边界；
- `freeze_receipt_v1.yml`、v1 独立裁决、Human 授权、A、Stage02、B、canonical、master 是否未被 correction commit 修改；
- artifact_version 是否为 2；
- normalized digest 是否可独立重算并精确等于声明值；
- package validation / current acceptance / git diff --check 的实际结果；
- selftest 若运行必须报告实际结果；若因完整树成本 timeout，不得用缩减树结果冒充 full-tree pass。

## 六个旧 blocker 必须逐项重新裁决

### ST04-IR-001 / A11 model-catalog thinness

审核 `RW-T43` 是否真正 ownership-aware：

- workflow/entry 指向 `model_routing`、调用 validator、记录 receipt fields 必须合法；
- 复制 mutable model catalog 必须失败；
- model identifiers 必须从被测树读取，而不是由 frozen package 写死；
- 攻击至少一种作者 C07 未覆盖的合法 pointer/metadata 形状。

### ST04-IR-002 / optional successor

审核 `RW-T08`：

- A 只强制 fresh vs reentry；
- 不得要求 exact `forked_successor` 或第三模式存在；
- 若第三模式存在，只能检查其独立 identity / predecessor semantics；
- 攻击至少一个作者 C08/C09 未覆盖的合法第三模式表达。

### ST04-IR-003 / naming-neutral discovery

不能只确认 C01/C02 绿。必须主动攻击 discovery：

- 合法 alternate schema_version；
- 合法 alternate filenames；
- boot/registry 的描述字段与 path/loader/evidence 混合；
- 一个描述文本同时提到 role/window/handoff 时是否可能误绑；
- content evidence 与 descriptive declaration 冲突时是否有确定性优先级；
- directory name / path token 不得泄漏为 contract-kind evidence。

若存在语义等价实现会因为命名被拒绝，仍为 blocking。

### ST04-IR-004 / polarity, structure, provenance

重点继续寻找合法写法的 false positive：

- `*_prohibited: true`
- `*_disabled: true`
- mapping/list/suffix prohibition forms
- nested mappings
- provenance/citation 中出现 provider/model 名
- normative key 中真的 pin provider 时必须失败
- 特别攻击字符串分段与裸子串（例如 preferred/ref 形状）

不能因为 43/43 mutations killed 就宣布充分。

### ST04-IR-005 / validator dependency topology

确认 RW-T37..RW-T42：

- unmutated candidate validator 在其合法 dependency closure 上先 exit 0；
- defect injection 后 exit non-zero；
- dependency closure 必须包含实际声明/引用到的 context_management/model_routing/communication_system 依赖；
- closure 不能因为 path parsing 偶然拉入整个 repository history 才获得绿色；
- closure 规则必须 bounded/deterministic；
- 若合法 validator implementation 仍会被 staging topology 拒绝，则 FIX_REQUIRED。

### ST04-IR-006 / duplicate role source false positives

审核 YAML 与 Markdown 均要求：

- 至少三个 role concepts；
- 同时具有 normative per-role attributes/source-of-truth 形状；
- role-like applicability/model/stage table 不应被误判；
- 真正的第二份 role source 必须失败。

至少攻击一个作者 C06 未覆盖的 Markdown/YAML 合法 counterexample。

## 新增重点：conforming_variants 本身

v2 新增 `conforming_variants` 是正确方向，但 reviewer 必须把它当作待审对象，而不是 proof。

至少回答：

1. 九个 variants 是否互相独立，还是只是同一 fixture 的表面改写？
2. 是否还有明显的等价 YAML/Markdown 表达未覆盖且会被 harness 误拒？
3. 每个旧 blocker 至少有一个能真正证明“合法替代实现仍绿”的 counterexample，而不是只删字段逃过测试？
4. conforming variant 是否可能通过同时削弱被测语义而获得绿色？

## 测试推导来源

重新检查 43 条测试是否由 A + Stage02 evidence 推导：

- 不得把 B 的命名、文件数、字段名、schema token 或 optional design preference 冻结成 mandatory pass condition；
- B 可以作为 candidate surface 定位，但不能成为判据来源；
- RW-T06 保持有效，除非发现新的 A/evidence 矛盾；若有效，明确确认 future Stage05/06 boundary 包含 `01_os/02_boot/context_management/启动清单_v1.yml`。

## 允许输出与写边界

只允许新增：

`01_os/_runs/run-20260812-角色窗口上下文模型路由集成-001/04_测试生成/独立接收审核/v2/**`

不得修改：

- frozen tests/harness/fixtures/receipts；
- v1 独立审核；
- Human 授权；
- foreground candidate check；
- A/Stage02/B；
- run.yml；
- canonical；
- master。

普通 fast-forward push；禁止 force/rebase/squash/amend/history rewrite。

## 可用裁决

- `ACCEPTED_FOR_STAGE05`
- `FIX_REQUIRED`
- `REJECTED`

只有 `ACCEPTED_FOR_STAGE05` 才允许 foreground 后续解锁 Stage 05。

PASS completion marker：

`stage04_t2_v2_independently_accepted_for_stage05`
