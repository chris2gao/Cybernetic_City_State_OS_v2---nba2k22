# 独立 Deep Research 任务包 v2 · 网页模型版

Task: `os-v2-global-model-capability-and-availability-routing-001`
Stage: `02_信息收集与提炼`
Research mode: independent / blinded / web-research-only
Date baseline: 2026-08-11

## 0. 你只需要读取两份上传文件

本任务专门给 ChatGPT Web、Gemini Web、Claude Web 使用。

**不要访问 GitHub，不要读取仓库，不要做 repository bootstrap，不要要求 branch / SHA / task manifest / endpoint card。**

Human 会给你上传且只要求你读取：

1. `独立DeepResearch任务包_v2_网页模型.md`（本文件）
2. `A_需求建模_v2.yml`（Human 已确认的需求模型）

除此之外，不需要任何项目文件。

Human 已确认 `A_需求建模_v2.yml` 与真实需求一致。你不需要重新做需求澄清，也不需要读取 `人类确认_v2.yml` 才能开始。

特别不要要求或读取以下项目内部材料：

- `AGENT_WORKING_DISCIPLINE.md`
- `AGENTS.md`
- `01_os/README.md`
- `01_os/开发入口与单窗口任务规范_v1.md`
- `01_os/01_workflow/**`
- `01_os/03_mechanisms/**`
- 当前 task packet / run.yml
- 任何 `_runs/**` 历史证据
- 第一研究者的任何研究报告

这些材料由后续 reconciliation / architecture 阶段处理；给你会增加锚定偏差，不属于本轮独立外部研究的必要输入。

## 1. 独立性要求

你是本任务的一名**独立外部研究者**。

目标是：只依据 `A_需求建模_v2.yml` 中已经确认的需求，以及你自己检索到的最新外部来源，独立建立 claim/evidence。

你不是来：

- 审核另一个模型的研究报告；
- 证明项目现有路由规则正确；
- 复述其他研究者的结论；
- 替项目决定最终 canonical 架构。

在提交自己的完整报告之前，禁止阅读 ChatGPT / Gemini / Claude 其他研究者的结果，也禁止读取任何第一研究者报告的转述。

报告开头必须写明：

- 你实际使用的产品 surface（例如 ChatGPT Web / Gemini Web / Claude Web）；
- 当前 UI 可见的 exact model label（如果能看到）；
- 研究日期；
- `I did not read other researchers' reports before completing this report` 的明确声明。

如果只能看到 UI label，不猜底层 API model ID。

## 2. Human 已确认的需求事实

以下是 requirement，不是 vendor claim，不需要研究者重新裁决：

1. 已登记模型默认 `available`；只有 Human 在任务开始或进行中明确声明某模型 `unavailable` 时才排除，Human 明确恢复后再次成为候选。
2. Human 自己能看到当前账户 UI 的可用模型与额度；系统**不需要**机器读取个人账户 entitlement / quota。
3. 不读取、不保存、不要求 token、cookie、credential、key、`.env` 或其他账户秘密。
4. 路由优化目标不是 token、价格、成本或额度利用率；目标是为当前任务选择**最合适的 `model + product surface + parameter profile`**，提高正确完成概率和任务适配度。
5. Claude Code CLI 当前 deferred，不作为当前 active routing surface；可以记录官方能力，但不为它设计启用/安装流程。
6. 架构采用低耦合、模块式原则：跨阶段、跨任务重复使用的能力倾向形成独立 global mechanism；workflow 负责 orchestration / invocation，不复制机制正文。
7. 已存在独立 context-management mechanism；未来 model-routing mechanism、role mechanism、task-execution envelope 应与它正交组合，而不是互相吞并职责。
8. project-observed performance 是正式 routing evidence；vendor benchmark 或 capability claim 不能覆盖项目真实反复返工的证据。
9. Antigravity 内的 Gemini / Claude 模型后续需要通过项目自己的 frozen qualification tasks 测试上下限。
10. 本轮研究只产生 evidence 与 architecture implications，不写最终 B，不决定最终文件结构，不修改任何项目文件。

## 3. 当前研究对象

请按 **product surface** 分开研究，不要把同一 provider 的不同产品面合并。

### OpenAI

- ChatGPT Plus Web
- Codex Desktop（Plus 会员可用的 Codex product surface）

### Anthropic

- Claude Pro Web
- Claude Code Desktop
- Claude Code CLI：仅记录为 deferred surface，不研究启用/安装

### Google

- Gemini Web / Google AI Pro
- Google Antigravity desktop / Google AI Pro
- Human 当前 Antigravity UI 报告的 labels：
  - Gemini 3.1 Pro
  - Gemini 3.6 Flash
  - Claude Opus 4.6

如果最新官方资料中的名称、版本或身份与 Human UI label 不同：

- 不覆盖 Human observation；
- 分栏记录 `Human-observed UI label` 与 `vendor-documented identity`；
- 给出映射证据；
- 无法可靠映射时写 `unverified mapping`。

## 4. 每个 surface / model 至少研究哪些事实

仅在来源真正支持时填写；没有可靠来源就写 `unknown`。

### Identity / lifecycle

- provider
- product surface
- current product/UI model label
- vendor-documented model identity / family
- GA / preview / experimental / retired / superseded 状态

### Capability

- context window / output limit（注意 claim 层级：API 与产品 surface 不等同）
- reasoning / thinking / effort controls
- **该 product surface 实际暴露给用户的 reasoning / thinking 档位**
- coding / repository editing
- web search / deep research
- browser / computer use
- tools / MCP / connectors / function calling / skills
- multimodal / vision / document handling
- multi-agent / subagent / parallel execution
- long-running execution / session persistence / background or asynchronous characteristics

### Product / subscription

- Plus / Pro / Google AI Pro 等产品层官方 entitlement 说明
- 产品层已公开的 usage / rate-limit 语义
- 哪些能力是 API-only，哪些是 Web/Desktop product feature
- known limitations / product-surface differences

### Evidence metadata

每个重要 claim 尽量带：

- source title
- source URL
- publisher/provider
- source date / last updated（若可见）
- verified_at = 2026-08-11（或实际研究日期）
- evidence class: `official_first_party | third_party | Human_requirement | inference`
- invalidation condition

## 5. 强制区分的四层事实

全文必须坚持：

`API model capability != Web/Desktop product capability != subscription entitlement != Human current-account availability`

例如：

- API 支持某 reasoning parameter，不证明 ChatGPT Web 暴露该参数；
- Claude 模型支持某 tool，不证明 Claude Code Desktop 当前 UI 暴露相同配置；
- Google 文档列出某模型，不证明 Human 此刻账户一定有额度；
- Human 当前可用性由 Human 在任务开工时裁决，不由你的网页研究覆盖。

## 6. 来源规则

### 第一优先级：官方一手资料

优先使用：

- OpenAI official / Help Center / Codex docs / developer docs
- Anthropic official / Claude Help / Claude Code docs
- Google / Gemini / Antigravity official docs

### 第二优先级：高质量第三方

第三方只用于：

- independent benchmark
- reliability / coding performance
- safety / failure-mode evidence
- 官方完全未公开的信息

必须明确标 `third_party`，不能和 vendor fact 混写。

### 冲突处理

如果官方不同页面相互冲突：

1. 两边都记录；
2. 比较发布时间 / 更新时间 / 所属 product surface；
3. 不“取平均”；
4. 如果仍不能解决，保持 `conflict / unknown`；
5. 不使用你的模型记忆来填缺口。

## 7. 需要主动挑战的问题

请从外部证据出发挑战，而不是顺着当前设计：

1. `model routing` 是否值得成为独立 global mechanism？有没有更简单且同样低耦合的成熟模式？
2. workflow 应只 orchestration / invoke，还是存在必须属于 workflow 自身的 routing rule？说明理由。
3. model capability catalog 与 task-time Human availability override 的最小数据边界是什么？
4. role / risk tier / task shape / required capability / project qualification / Human availability 这组 routing inputs 是否足够？哪些冗余、还缺什么？
5. surface-specific parameter profile 是否必要？必须用具体 product evidence 证明或反驳。
6. “model 本体能力强”与“某个 desktop / web agent harness 适合长期仓库任务”应该怎样分开评价？
7. 哪些信息应作为长期稳定 capability knowledge，哪些必须在任务开始时 fresh-check / Human override？
8. 是否存在不需要复杂 scoring system、只用一组明确 eligibility + fit rules 就能可靠 routing 的成熟模式？

这里输出的是 `evidence-backed architecture implications`，不是最终 architecture decision。

## 8. Antigravity project qualification 测试方案

本轮**只设计测试，不实际调用/消耗 Antigravity 模型额度**。

目标模型：

- Gemini 3.6 Flash
- Gemini 3.1 Pro
- Claude Opus 4.6

目的不是做通用 benchmark 排名，而是回答：

> 在本项目的真实 OS / workflow / repository task 形状下，这个 `surface + model` 能可靠承担到什么任务边界？

### 至少覆盖 5 类 frozen tasks

1. deterministic / mechanical transformation
2. standard local implementation
3. semantic specification / judgment
4. long-chain repository execution to evidence closure
5. independent primary-diff review

请为每类提出**少量但有区分度**的 fixture 设计原则。不要通过降低任务标准让模型通过。

### 候选测量指标

请判断哪些是 hard qualification gates，哪些是 diagnostic metrics：

- final correctness
- first-pass success
- rework rounds
- rework root cause
- instruction adherence
- authorized-boundary adherence
- Human micro-gate overuse
- evidence honesty / claim-to-proof alignment
- long-chain state retention / objective closure
- overengineering
- semantic drift
- failure to stop at real semantic / protected boundaries

### 必须回答

- 如何防止被测模型“针对测试口径游戏化通过”？
- qualification task 应怎样保持与 model vendor 无关？
- 是否需要 Codex Desktop / Claude Code Desktop 作为 reference baseline？若需要，baseline 的作用是什么，不允许它变成“必须和 baseline 输出相同”。
- 对额度稀缺的 Claude Opus 4.6，如何用最少样本获得最大判别信息？
- 怎样从 qualification 结果推导 `qualified / qualified_with_limits / unqualified` 的 task-class 边界，同时避免一次偶然失败就永久定性？

## 9. 输出格式

请直接生成一份完整、可上传回项目的 Markdown 研究报告。

建议文件名由 Human 在保存时按研究者区分，例如：

- `DeepResearch_ChatGPTWeb_v1.md`
- `DeepResearch_GeminiWeb_v1.md`
- `DeepResearch_ClaudeWeb_v1.md`

报告至少包含：

1. Research identity / date / exact UI model label
2. Methodology and source policy
3. Executive findings（仅总结 evidence，不写最终 B）
4. Surface-by-surface claim/evidence matrix
5. Provider/product contradictions, stale docs, unknowns
6. Cross-surface implications
7. Architecture implications（明确标 `non-final`）
8. Antigravity qualification test proposal
9. Claims that remain unverified
10. Full source list
11. Independence statement

### 引用要求

- 每个重要事实必须有可追溯 citation / source link；
- 尽量使用官方一手来源；
- 不要输出只有模型名称与泛泛评价、没有来源的“排行榜”；
- benchmark 与产品功能必须分开；
- inference 必须明确标注为 inference。

## 10. 明确不做

- 不需要 Git / GitHub / repository access；
- 不创建 branch；
- 不修改项目文件；
- 不读项目 canonical；
- 不读其他研究者报告；
- 不做 Stage 03 结果建模 B；
- 不写最终 routing table；
- 不决定最终 mechanism 文件路径；
- 不实际运行 Antigravity qualification；
- 不根据价格/token 成本优化；
- 不重新询问 Human 已确认的 A v2 基础需求。

完成标记：

`independent_deep_research_ready_for_reconciliation`
