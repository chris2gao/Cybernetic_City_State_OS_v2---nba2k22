# Stage 04 窄修正测试设计说明 v1

对应 `04_tests.yml` artifact_version 3。授权见
`04_测试生成/Stage04_Human窄修正授权_v1.yml`，回退裁决见
`07_测试执行/Stage07阻塞接收与回退裁决_v1.yml`。

## 0. 角色重合披露

本轮由 `Claude Desktop — Cowork mode (Claude Agent SDK host) / Claude Opus 5 /
reasoning_setting: not_exposed` 执行。派单第 7 行推荐"新的 Claude Opus 5 会话"，
Human 在本轮消息中也要求新会话。**实测不成立**：本会话就是产出 F1/F2/F3 的 Stage 07
复核会话，`Stage07阻塞接收与回退裁决_v1.yml#review_input.reviewer` 记录的正是它。
矛盾已在开工前报告，Human 裁定"本会话继续，并如实披露角色重合"。

按开发入口 §9"Human 豁免独立性时，报告须披露角色重合和未覆盖风险"，此处记录：

- **满足的硬约束**：与 Stage 06 executor（Codex Desktop / GPT-5.6 Sol / max）不同会话、
  不同模型族。派单第 10 行"不是 implementation executor"成立。
- **未覆盖的风险**：本会话既产出了 blocker，又设计了捕获它们的测试。缓解手段是派单第 64 行
  的要求——**corrected test 的成功语义回到 A / Stage02 evidence / B claim mapping，
  而不是回到 reviewer finding**。下面每一条修正都标注了它的证据锚点，可被独立复查。
- 补充事实：v1/v2 的 `04_tests.yml` 作者也是 Claude Opus 5 / Cowork 会话，这一层同族关系
  在 `freeze_receipt_v2.yml#evidence_honesty.self_review_boundary_note` 已有记录。
- 最终 Stage 07 复核仍须由新的独立会话执行（裁决文件 `stage07.next_review` 已如此规定）。

## 1. 为什么重开

v2 的 28/28 全绿，Stage 07 却证明它不充分。三处：

| Stage 07 finding | v2 的测试缺陷 |
|---|---|
| F1 unsupported attribution | 没有任何一条测试能拦住与证据矛盾的 surface/model 绑定 |
| F2 source refs 不可解析 + 洗白 | MR-T10 只测非空；MR-T25 词法误伤真实来源标识 |
| F3 validator 不兑现 B13 | 只有 MR-T24 一条验证机制自带 validator 的 fail-closed 行为 |

F2 尤其不是"漏测"，而是**测试自身诱导了失真**。Stage 06 的 `S5.attempts[0]` 记录：
MR-T25 判红，归因"source identifier 含 economic-token 子串"，remedy 是把真实一手来源
`GOOGLE_AG_PRICING` 换成 Stage 02 的 claim id。一条测试把执行者推向了它本该防止的方向。

## 2. 每条修正的证据锚点

### MR-T10（改写）— source 可解析 + 至少一个外部来源

- **A 锚点**：成功判据 4"稳定事实带 source/ref、verified_at、invalidation condition"。
- **A 约束锚点**："provider 技术事实优先一手资料；历史印象或失效测试只可形成低置信 diagnostic"。
- **Stage 02 锚点**：`证据对齐与冲突消解_v1.yml#source_registry` 本身就区分
  `provider_first_party` / `independent_web_research` 与 `accepted_claims` 两个层次。
  把 claim id 当 source id 用，是把结论当成了它自己的依据。
- 因此新增两项：token 必须可解析；解析结果中至少一个 `kind` 属于外部来源集合。
  后者精确对应洗白形态——**用项目内部 claim 顶替一手引用**。

### MR-T25（改写）— 从词法判定改为位置判定

- **A 锚点**：成功判据 10"routing 不建立 token/cost 优化、额度库存经济、自动 fallback 链或 quota watcher"。
- 该判据约束的是**路由行为**，不是文本。v2 把它实现成全文件词法扫描，语义漂移了。
- v3 拆成两半：
  - 结构扫描按位置进行。evidence 子树（`sources` / `source_refs` /
    `surface_exposure_evidence` / `evidence_refs` / `prohibited_routing_inputs` /
    `invalidation_conditions`）豁免；取值为 `false` 的字段是禁止声明，豁免。
  - 文本扫描只留"货币行 + per-1M-token 计价"，那才是 B11 所说的**价目表迁移**的签名。
- 反向保证由 fixture 承担：good_tree 的 `sources:` 里**故意保留 `GOOGLE_AG_PRICING`**，
  fixture 35/35 全绿即证明不再误伤。正向保证由 M31 承担：把
  `selection_scoring.price_weight` 加进路由契约必须判红。

### MR-T29（新增）— 从声明加载面可解析

- **A 锚点**：成功判据 4。
- **架构锚点**：开发入口 §4「`01_os/_runs/**` 不注册」、§1.7 与 AGENTS.md 启动规则 9
  「禁止 default-preload `01_os/_runs/**`」。一个 canonical 机制若把证据链终点放在 OS
  禁止预加载的路径上，就不能从自身被审计。
- **不冻结文件名**（派单第 89 行）。冻结的是"存在一个从声明加载面可达的解析契约"及其行为：
  解析表可以放在 catalog 里、任何 load_order 文档里，或由 boot 清单的一个 `*_ref`
  指针跳一次到别处。四种键名 `sources` / `source_registry` / `source_index` / `来源` 都接受。

### MR-T30（新增）— 与证据矛盾的 attribution 必须失败

- **A 锚点**：成功判据 7「Antigravity 中 Gemini 3.1 Pro、Gemini 3.6 Flash、Opus 4.6 的身份、
  surface、参数与官方能力按 evidence 记录；**不能验证的 label 不补猜**」。
- **Stage 02 锚点**：C07 与 C08 都把 Antigravity selector 列为 Gemini 3.6 Flash /
  Gemini 3.1 Pro / Claude (Sonnet|Opus) **4.6**；`DeepResearch_ChatGPT官方一手资料_v1.md`
  中每一条 Opus 4.8 陈述都指向 Anthropic Claude / Claude Code。
- **B 锚点（仅 claim mapping）**：B10 把 Opus 4.8 描述为 Anthropic entitlement-conflict
  的 discovered/unregistered 候选。
- 实现为一张**冻结的 known-unsupported 组合表**，当前只有一条：
  `antigravity × /opus\s*4\.8/`。判定与 `registered` 无关。
- 派单第 115 行的边界被遵守：不假装程序能理解任意未来产品页。将来若有证据支持该绑定，
  必须重开 Stage 04 —— 这正是本条要制造的摩擦。

### MR-T31 – MR-T35（新增）— 机制自带 validator 对 B13 fail closed

- **B 锚点**：B13「validator 检查 schema、required source/freshness fields、
  duplicate surface/model keys、非法 cost/quota routing fields、registered entry
  缺参数/来源、以及 entry/boot/registry pointer 断裂」。
- **架构锚点**：`01_os/03_mechanisms/README.md` 与 `05_registry/README.md` 记录的失败模式——
  机制注册了却不声明失效如何显现。
- 关键区分：**Stage 04 的检查发现缺陷 ≠ 机制在 boot 时能发现缺陷。** 冻结测试不在机制启动时
  运行。所以这五条各自复制机制面、施加一个代表性缺陷、运行 **boot 清单声明的那个** validator，
  要求非零退出码。每条两个探针，任一返回 0 即判红。

| test | 探针 |
|---|---|
| MR-T31 | registered entry 与 unregistered entry 各引用一个无法解析的 source |
| MR-T32 | registry path 不存在；registry 不再覆盖机制目录 |
| MR-T33 | mechanism_version 漂移；catalog_version 与 boot 声明漂移 |
| MR-T34 | `selection_scoring.price_weight`；`quota_balance` 进入 routing input |
| MR-T35 | load_order 文件被删；boot 的 registry 指针指向不存在的文件 |

MR-T33 只度量行为，不度量实现形状。用字面量 pin 死版本号也能通过——那是较弱的实现，
但它确实 fail closed。要不要求真正的交叉绑定，A/B 没有规定，因此不冻结。这一点在当前
candidate 上就体现出来了（见第 4 节）。

## 3. 保持不变的保证

派单第 148–162 行列出的既有保证全部保留，未被削弱：独立全局机制、Human availability
override、`routing_only`、model × surface 分离、surface 参数、vendor vs project 分栏、
diagnostic 不产生 hard qualification、§7.1 变薄、§8/§9/§11/T3/publisher 控制、
无自动 fallback、无后台探测、registry/boot/loader 失效显现、publisher authority 字节基线。

MR-T01–T09、T11–T24、T26–T28 逐字未改。MR-T10 与 MR-T25 是**加强**而非替换：原有断言
仍在，只是不再单独构成通过条件。

## 4. Self-test 与 candidate 基线（实际运行结果）

`selftest`：

- good fixture **35/35 green**
- mutations killed **36/36**（v1 的 27 条中仍适用的全部保留，M15 与 M23 的锚点随 fixture
  修正更新，语义不变；新增 M28–M36）
- boundary `empty_tree`：仅 `MR-T02 / MR-T23 / MR-T25 / MR-T30` 四条纯禁止性检查空树下真空成立
- boundary `mechanism_without_boot_or_registry`：`MR-T29 / T31–T35` 一并变红

派单要求的几条反向证明都实际跑到了：

- `GOOGLE_AG_PRICING` 留在 good fixture 的 `sources:` 里，fixture 全绿 → MR-T25 不再误伤；
- M31（`price_weight` 进入路由契约）杀红 MR-T25 → 真正的经济路由语义仍然失败；
- M29（Opus 4.8 挪到 antigravity，保持 `registered:false`）杀红 MR-T30；
- M30（一手来源换成 claim id）杀红 MR-T10；
- M32–M36 分别杀红 MR-T31–T35。

`acceptance` 对当前 Stage 06 candidate（`3e3b608`，分支 head `d52e7dfe`）：**29/35**，
六条红灯：

| 红灯 | 对应 finding |
|---|---|
| MR-T10 | F2 — 10 个 token 全部无法解析 |
| MR-T29 | F2 — 声明加载面上不存在解析入口 |
| MR-T30 | F1 — `antigravity :: Claude Opus 4.8`，`registered=False` 不豁免 |
| MR-T31 | F2 + F3 — validator 对 bogus source 返回 0 |
| MR-T32 | F3 — validator 对 registry path 断裂返回 0 |
| MR-T34 | F3 — validator 对 `price_weight` 返回 0 |

**MR-T33 与 MR-T35 在 candidate 上是绿的**，如实记录并说明：candidate 的 validator 把
`catalog_version` 与 registry 指针都 pin 成字面量，因此这两组探针恰好被判红。这是较弱的
实现，但它满足本条冻结的行为要求。Stage 07 F3 里 D4/D5 那部分因此降级为**非阻塞的实现
观察**，不作为冻结条件——否则就是拿实现形状当需求。

## 5. 历史保留

- `freeze_receipt_v1.yml`、`freeze_receipt_v2.yml` 原样未动。
- `fixtures/mutations_v1.yml` 原样未动，标记 `retained_for_history`；活动集合为
  `mutations_v2.yml`（v1 的超集）。runner 优先读 v2，v2 缺失时回退 v1。
- 旧 digest `72898d54…` 在 `freeze_receipt_v3.yml` 中标记为
  `superseded_by_Human_gated_corrected_package`，不是"从未存在"。

## 6. 证据诚实

本包由本会话设计并自测，**未由实现方或最终 reviewer 复现**。
所有计数与 digest 来自本会话实际运行的退出码与输出，不是预期值。
