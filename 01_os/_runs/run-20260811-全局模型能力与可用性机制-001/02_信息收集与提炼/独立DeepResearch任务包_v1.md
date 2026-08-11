# 独立 Deep Research 任务包 v1

Task: `os-v2-global-model-capability-and-availability-routing-001`
Stage: `02_信息收集与提炼`
Research mode: independent / blinded-to-first-researcher-conclusions
Date baseline: 2026-08-11

## 0. 独立性要求

你是本任务的第二独立研究者。目标是从原始需求与外部来源独立构建 claim/evidence，不是审核或复述第一研究者。

在你把自己的研究结果耐久写出之前：

**禁止读取或搜索：**

`02_信息收集与提炼/DeepResearch_ChatGPT官方一手资料_v1.md`

以及任何直接转述该文件结论的材料。

完成自己的研究产物后才允许在 reconciliation 阶段看到第一研究者结果。

开始报告时必须写明你实际使用的 provider / product surface / model，以及研究日期。若模型身份只能看到 UI label，就如实记录 UI label，不猜底层 ID。

## 1. 必须读取的仓库输入

从当前物理 Git 状态 fresh-read，不相信本文件中的 SHA 作为当前事实。

按现有 bootstrap 加载后，只额外读取本任务直接需要的：

- `01_os/_runs/run-20260811-全局模型能力与可用性机制-001/01_任务输入/任务包_v1.yml`
- `01_os/_runs/run-20260811-全局模型能力与可用性机制-001/01_需求建模/requirement/A_需求建模_v2.yml`
- `01_os/_runs/run-20260811-全局模型能力与可用性机制-001/01_需求建模/requirement/人类确认_v2.yml`
- `01_os/01_workflow/README.md`
- `01_os/03_mechanisms/context_management/README.md`
- `01_os/开发入口与单窗口任务规范_v1.md` 的模型路由相关部分

不要默认加载全部 `_runs/**`。

## 2. Human 已确认、无需研究者重新裁决的需求事实

这些是需求，不是待验证 vendor claim：

1. 已登记模型默认视为可用；只有 Human 在任务开始或进行中明确说 unavailable 才排除，Human 明确恢复后重新成为候选。
2. Human 能看到当前账户 UI 的模型与额度；本机制不需要自动读取账户 entitlement / quota，也不得读取 token、cookie、credential、key 或 `.env`。
3. 路由目标不是省 token、价格或额度，而是为当前任务选择最合适的 `model + product surface + parameter profile`，提高正确完成概率与任务适配度。
4. Claude Code CLI 当前 deferred，不作为本轮 active routing surface。
5. 架构要求低耦合、模块化：跨阶段复用能力优先形成独立 global mechanism；workflow 负责编排/调用，不复制机制正文。
6. project-observed performance 是正式路由证据。厂商 benchmark / capability claim 不能覆盖本项目真实反复返工的证据。
7. Antigravity 内的 Gemini / Claude 模型需要通过本项目冻结任务做 qualification，确定其适合承担的任务上下限。

## 3. 当前研究 scope

逐 surface 独立研究当前（2026-08-11）事实：

### OpenAI

- ChatGPT Plus Web
- Codex Desktop / Plus 可用的 Codex surface

### Anthropic

- Claude Pro
- Claude Code Desktop
- Claude Code CLI 只记录为 deferred，不做启用/配置研究

### Google

- Gemini Web / Google AI Pro
- Google Antigravity desktop / Google AI Pro
- Human 当前 Antigravity UI 报告的：
  - Gemini 3.1 Pro
  - Gemini 3.6 Flash
  - Claude Opus 4.6

若研究发现当前官方名称或身份与 Human UI label 不同，不覆盖 Human observation；把两者分栏并解释映射证据。

## 4. 每个 surface/model 至少回答

只有来源支持时才填；未知就写 unknown：

- provider
- product surface
- 当前产品/UI model label
- 可证实的 model identity / model family
- context window / output limit（仅在该 claim 的层级确实有官方证据时）
- reasoning / thinking / effort controls，尤其是 **surface 实际暴露的档位**
- coding / repo editing 能力
- web/research 能力
- computer use / browser / tool / MCP / function / skill 能力
- multimodal / vision（任务相关时）
- multi-agent / subagent / parallelism
- long-running / asynchronous / session persistence 特征
- 当前 subscription / entitlement 的官方说明
- 已知限制、preview 状态、surface 与 API 的差异
- source URL/title/date
- verified_at
- invalidation condition

严格区分：

`API model capability != Chat/Web/Desktop product capability != Human current-account availability`

## 5. 来源规则

技术与产品事实优先使用 provider 官方一手资料：

- OpenAI official / Help / developer docs
- Anthropic official / support / docs
- Google / Gemini / Antigravity official docs

允许使用第三方材料的场景：

- 独立 benchmark / reliability / safety / coding performance 的补充证据；
- 官方没有公开的信息。

但必须标成 third-party，不得与 vendor fact 混写。

如果官方不同页面互相冲突或明显存在版本滞后：

- 两边都记录；
- 比较发布日期/更新时间与产品上下文；
- 不自行“平均”；
- 对当前 Human 账户 entitlement 最终保留 Human task-time observation authority。

## 6. 必须主动挑战的问题

你不是来证明当前设计正确。请独立寻找反例：

1. `model routing` 是否真的值得成为独立 global mechanism，而不是只留在 task-entry 文档？
2. workflow 是否应只调用它，还是有某些 routing rule 必须属于 workflow 本身？
3. 现有 `开发入口与单窗口任务规范_v1.md §7.1` 哪些内容属于稳定 task discipline，哪些是快速过时的 model catalog，应不应该迁移成 pointer？
4. capability knowledge 与 Human availability override 的最小数据结构是什么？有没有不必要的 freshness/availability 复杂度？
5. role / risk tier / task shape / required capability / project qualification / Human availability 这组输入是否足够路由？缺什么，哪些又是冗余？
6. surface-specific parameter profile 是否必要？请用实际 provider 文档证明或反驳。
7. 是否存在“官方模型很强但特定 desktop harness 不适合本项目”的证据模式？如何在 contract 里避免把 model 与 harness 混为一谈？

只输出 evidence-backed implications，不在本阶段写最终 B 或 canonical implementation。

## 7. Antigravity project qualification 方案研究

本轮**设计测试方案，不实际消耗模型额度执行 qualification**，除非 Human 后续明确要求。

请独立提出一组小而有区分度的冻结任务，用于测试：

- Gemini 3.6 Flash
- Gemini 3.1 Pro
- Claude Opus 4.6

至少覆盖这些 task classes：

1. deterministic / mechanical transformation
2. standard local implementation
3. semantic specification / judgment
4. long-chain repository execution to evidence closure
5. independent primary-diff review

测试不能为了让模型通过而降低标准。失败也是有效 evidence。

建议测量但可挑战/修改：

- final correctness
- first-pass success
- rework rounds
- rework root cause
- instruction adherence
- allowed-boundary adherence
- Human micro-gate overuse
- evidence honesty / claim-to-proof alignment
- long-chain state retention / closure
- overengineering
- semantic drift

请回答：

- 哪些指标应作为 hard qualification gate，哪些只作诊断？
- 如何避免用同一个模型设计自己一定能过的测试？
- 是否需要同一 frozen fixture 同时给 Codex / Claude Code 做 reference baseline？
- 稀缺的 Opus 4.6 应如何用最少样本最大化判别信息，而不是追求统计规模？

## 8. 输出要求

先耐久写出自己的研究结果，再向 Human 报告 pointer。

推荐产物：

`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/02_信息收集与提炼/DeepResearch_独立研究者_v1.md`

产物至少包括：

1. research identity / date / exact observed model label
2. source methodology
3. surface-by-surface claim/evidence matrix
4. contradictions / stale docs / unknowns
5. architecture implications（非最终 B）
6. Antigravity qualification test proposal
7. claims that remain unverified
8. explicit statement that first researcher artifact was not read before this result was written

不要修改 canonical。
不要修改第一研究者产物。
不要修改 master。
不要 force/rebase/squash/amend/history rewrite。

如果你只有本地 clone，可以在本任务现有 branch 上写 stage-2 evidence；如果 Human 希望完全物理隔离，也可只把完整研究报告返回 Human，由 Human 转交给当前任务窗口落盘。不要自行建立新的 competing task。

完成标记：

`independent_deep_research_ready_for_reconciliation`
