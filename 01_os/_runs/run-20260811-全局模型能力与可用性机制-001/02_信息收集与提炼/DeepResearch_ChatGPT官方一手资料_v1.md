# Stage 02 Deep Research — ChatGPT 官方一手资料 pass v1

Task: `os-v2-global-model-capability-and-availability-routing-001`
Researcher: ChatGPT / GPT-5.6 Sol
Date: 2026-08-11
Evidence class: independent web research from provider/first-party product documentation
Requirement basis: `../01_需求建模/requirement/A_需求建模_v2.yml` + `人类确认_v2.yml`

## 研究纪律

- 本文件只记录 provider/product 官方资料支持的 claim，以及明确标出的 Human observation / inference。
- API capability 不自动等同 consumer/desktop product surface capability。
- 账户此刻可用性以 Human 在任务开始/进行中给出的 observation 为准；本研究不尝试读取账户秘密或自动探测额度。
- 价格/token 成本不作为本项目路由优化目标；若来源中出现，仅用于识别产品/模型，不用于推荐。
- 研究时间为 2026-08-11；模型、产品面与 entitlement 均视为高时变事实。

## A. OpenAI

### A1. ChatGPT Plus Web

**官方事实**

- GPT-5.6 Sol 面向复杂 coding、knowledge work/research、cybersecurity、science、computer use、design。
- 标准 ChatGPT 对话中，Plus 当前包含 GPT-5.6 Sol 的 `Medium` 与 `High`；`Extra High` 与 `Pro` 不属于 Plus。
- GPT-5.5 Instant 仍是快速日常回答默认模型。
- GPT-5.6 Terra / Luna 不在标准 ChatGPT conversation 里作为可选模型；它们在 ChatGPT Work / Codex 等产品面另行提供。

**路由含义（inference）**

- `ChatGPT Plus web` 必须独立建模，不能沿用 Codex 的 Sol/Terra/Luna 三档选择器。
- 对本项目 planner / architecture / deep research 角色，ChatGPT Plus web 的可控主变量当前是 Sol 的 Medium/High，而不是 Terra/Luna。

Sources:
- OpenAI Help, "GPT-5.6 in ChatGPT", updated 2026-08: https://help.openai.com/en/articles/20001354-gpt-5-6-in-chatgpt
- OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition", 2026-07-09: https://openai.com/index/gpt-5-6/

### A2. Codex Desktop / Codex surface under Plus

**官方事实**

- Plus/Pro/Business/Enterprise 在 Codex 可选择 GPT-5.6 Sol、Terra、Luna，并可设置 effort；`max` 对有 GPT-5.6 Codex 权限的用户可用。
- Codex desktop 是面向 agentic work 的 surface：支持多 agent 并行、长任务、diff review 和 built-in worktrees。
- OpenAI 明确描述 Codex 适合从 targeted edits 到 full lifecycle、long-running tasks；这属于 product/harness 能力，不等于任一模型在本项目里已经 qualified。

**API/model-family stable facts（只用于理解模型，不直接冒充 Codex UI 参数）**

- Sol / Terra / Luna API 模型当前均为 1.05M context、128K max output、knowledge cutoff 2026-02-16。
- GPT-5.6 API reasoning effort: `none | low | medium | high | xhigh | max`；OpenAI guidance 将 Sol 定位为 frontier complex professional work，Terra 为 balanced tier，Luna 为 high-volume/cost-sensitive tier。
- API tool support包括 function calling、web/file search、computer use 等；Codex surface 具体工具集合由 Codex harness 决定。

**路由含义（inference）**

- 本项目不应继续把 Sol/Terra/Luna 的区别解释为“价格优先级”。应通过项目内 qualification 直接测任务适配边界。
- surface routing 至少要记录 `Codex Desktop + model + effort`；API-only 参数不得未经 UI/产品证据写入 Codex profile。

Sources:
- OpenAI Help, GPT-5.6 in ChatGPT: https://help.openai.com/en/articles/20001354-gpt-5-6-in-chatgpt
- OpenAI, Introducing the Codex app: https://openai.com/index/introducing-the-codex-app/
- OpenAI API model guidance: https://developers.openai.com/api/docs/guides/latest-model
- OpenAI API models: https://developers.openai.com/api/docs/models

## B. Anthropic / Claude

### B1. 当前模型代际

**官方事实**

- Claude Sonnet 5 于 2026-06-30 发布；Anthropic 称其为当前最 agentic 的 Sonnet，Free/Pro 默认模型，并明确“available in Claude Code”。
- Claude Opus 4.8 于 2026-05-28 发布；Anthropic 将其定位为 serious coding / AI agents / complex knowledge work，1M context，并明确 access surface 包括 Claude Code。
- Opus 4.8 在 Claude Code 支持更高 effort；官方 launch note写明 default `high`，可选 `extra/xhigh` 或 `max`，并建议 difficult / long-running asynchronous workflows 使用 extra。
- Claude Code 已存在 desktop app surface，支持多个 local/remote sessions 并行；Anthropic usage research也把 CLI、Claude.ai、Claude Code desktop app 作为不同使用 surface 统计。

Sources:
- Anthropic, Introducing Claude Sonnet 5, 2026-06-30: https://www.anthropic.com/news/claude-sonnet-5
- Anthropic, Claude Opus 4.8: https://www.anthropic.com/claude/opus?app=claude-code
- Anthropic, Introducing Claude Opus 4.8, 2026-05-28: https://www.anthropic.com/news/claude-opus-4-8
- Anthropic, Introducing Claude Opus 4.5 (Claude Code desktop announcement), 2025-11-24: https://www.anthropic.com/news/claude-opus-4-5
- Anthropic research, "How Claude Code is used in practice", 2026-06-16: https://www.anthropic.com/research/claude-code-expertise

### B2. Pro entitlement存在官方文档时序冲突

**观察到的官方冲突**

- 新 Sonnet 5 release明确：Sonnet 5 across all plans，Free/Pro default，并 available in Claude Code。
- 新 Opus 4.8 product page明确：Opus 4.8 available on Claude for Pro/Max/Team/Enterprise；Transparency Hub列 Claude Code 为 Opus 4.8 access surface。
- 但 Anthropic Help 的 `Using Claude Code with your Pro or Max Plan` / `Claude Code Model Configuration` 仍含旧 Sonnet 4 / Opus 4 entitlement 表述，称 Pro 的 Claude Code 不可用 Opus。

**结论**

- 不能从这些相互不同步的静态页面推导“当前 Human Pro 账户的 Claude Code Desktop 此刻一定能/不能选 Opus 4.8”。
- 本项目 A v2 的 availability rule正确：当前账户真实可用模型由 Human UI observation 作为 task-time authority；provider docs只描述 capability / general availability。
- 当前 routing knowledge 可安全写：`Sonnet 5` 是当前 Pro + Claude Code 明确支持的候选；`Opus 4.8 in Human's Claude Code Pro account` 必须在实际任务开工时由 Human observation确认后才成为候选。

Sources:
- https://www.anthropic.com/news/claude-sonnet-5
- https://www.anthropic.com/claude/opus?app=claude-code
- https://www.anthropic.com/transparency/model-report
- https://support.anthropic.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan
- https://support.anthropic.com/en/articles/11940350-claude-code-model-configuration

### B3. 与本项目 long-running 任务的关系

**官方事实**

- Anthropic 2026 usage research显示 Claude Code 相比 chat/Cowork具有更高 agent autonomy，并观察到更 end-to-end 的 agentic use。
- Opus 4.8 的 `dynamic workflows` 可以把极大任务拆为大量并行 subagents，但官方明确该 feature research preview 面向 Enterprise/Team/Max；不能在 Pro route 中默认假设存在。

**路由含义（inference）**

- Claude Code Desktop 本身适合成为 implementation surface候选；模型等级与 effort 仍需项目 qualification。
- Pro 下不能把 Max-only dynamic workflows 写入默认参数 profile。

## C. Google Gemini Web / Google AI Pro

### C1. Gemini Web 是独立 consumer surface

**官方事实**

- Google AI Pro 的 Gemini app当前以 `Flash-Lite / Flash / Pro` 等产品级模型选项描述；帮助页明确 model names/versions/availability 可能变化。
- Google AI Pro 的 Gemini app context window当前为 1M；thinking UI概念为 Standard / Extended，Deep Think 为 Ultra-only。
- Google AI Pro提供 Gemini app Pro 与 Google Antigravity higher limits / prioritized traffic。

**结论**

- Gemini Web profile应以当前 UI/product label为事实，不把 Gemini API 的精确 model ID 与 thinking_level 直接套到网页。
- 本项目不需要追踪数值额度来优化路由；Human只需在不可用时 override。

Sources:
- Gemini Apps Help, limits/upgrades: https://support.google.com/gemini/answer/16275805
- Google One Help, Google AI Pro benefits: https://support.google.com/googleone/answer/14534406

## D. Google Antigravity 2.0

### D1. Surface / harness

**官方事实**

- Antigravity 2.0 是 standalone desktop agent command center，可在 Project 内执行 system commands、file read/write、web search、skills/MCP、subagents，支持异步任务和多 agent orchestration。
- Projects定义 agent可访问的 folders/repositories与项目级安全设置。

Sources:
- Antigravity docs overview: https://antigravity.google/docs/overview
- Antigravity product/docs: https://antigravity.google/docs/home

### D2. Human 报告的模型身份已被官方文档证实

当前 Antigravity model docs 明确列出：

- Gemini 3.6 Flash: `Low / Medium / High`
- Gemini 3.1 Pro: `Low / High`
- Claude Sonnet 4.6: `Thinking`
- Claude Opus 4.6: `Thinking`
- 以及 Gemini 3.5 Flash / GPT-OSS 120B 等其他候选

因此 Human 的 `Gemini 3.1 Pro / Gemini 3.6 Flash / Opus 4.6` 不是误记，确实是 Antigravity reasoning-model surface labels。

Source:
- Antigravity models: https://antigravity.google/docs/models

### D3. API能力与 Antigravity surface 参数差异

**Gemini 3.6 Flash API官方事实**

- model id `gemini-3.6-flash`
- 1,048,576 input / 65,536 output
- thinking API支持 `minimal / low / medium / high`，default medium
- code execution、computer use(preview)、function calling、search grounding、structured outputs 等

**Gemini 3.1 Pro Preview API官方事实**

- model id `gemini-3.1-pro-preview`
- 1,048,576 input / 65,536 output
- thinking API支持 `low / medium / high`，default high
- code execution、function calling、search grounding、structured outputs 等

**Surface差异**

- Antigravity UI当前只暴露 3.6 Flash Low/Medium/High（未列 minimal）。
- Antigravity UI当前只暴露 3.1 Pro Low/High（未列 medium）。
- Antigravity 的 Claude Opus 4.6只暴露 `Thinking` 标签；不能从 Anthropic native/API参数反推 Antigravity 还允许用户控制什么。

Sources:
- Gemini 3.6 Flash model docs: https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash
- Gemini 3.1 Pro Preview: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- Gemini thinking: https://ai.google.dev/gemini-api/docs/thinking
- Antigravity models: https://antigravity.google/docs/models

### D4. 3.6 Flash 对本项目历史痛点的官方针对性 claim

Google 最新模型指南对 3.6 Flash 的产品 claim包括：

- fewer reasoning steps / conversational turns / tool calls
- reduced execution-loop spiraling
- fewer unwanted file edits
- fewer debugging loops
- better instruction following

这些 claim 与 Human 对较早 Gemini/Antigravity执行“返工轮次过多”的项目痛点高度相关，但**不能直接当成项目资格通过**；必须用本项目冻结任务实测。

Sources:
- Google latest model guide: https://ai.google.dev/gemini-api/docs/latest-model
- Antigravity 3.6 Flash product note: https://antigravity.google/blog/gemini-3-6-flash-in-google-antigravity

## E. Stage 02 当前证据结论

### E1. 已足够确定

1. **必须以 surface 为一等对象。** 同一 provider/model family 在 ChatGPT Web、Codex Desktop、Claude Code Desktop、Gemini Web、Antigravity 上的模型选择与参数不同。
2. **Human availability override 是必要而非权宜。** 官方 entitlement 文档本身会滞后或互相不同步；当前账户 UI observation 是 task-time availability 的可靠事实来源。
3. **现有 §7.1 静态表已需要替换/迁移。** 它没有表达 ChatGPT-vs-Codex surface差异，也没有当前 Sonnet 5/Opus 4.8/Antigravity 3.6 Flash 等信息。
4. **路由不能只靠官方 benchmark/定位。** Antigravity 的 Gemini/Opus 必须通过 project qualification 才能获得本 OS 内的 task-fit 等级。
5. **参数 profile 必须是 surface-specific。** API参数只能作为模型能力背景，不能直接写成 desktop/web可用参数。

### E2. 仍需独立 research / 实测

1. 第二研究者独立核验上述 model/surface/parameter claims，并主动找冲突。
2. 冻结一组本项目典型 task fixtures，对 Antigravity 3.6 Flash、3.1 Pro、Opus 4.6 做资格测试；必要时对 Codex/Claude Code建立相同基准，形成跨 surface project evidence。
3. 资格测试应测：first-pass correctness、rework rounds/root cause、instruction adherence、boundary adherence、Human micro-gate overuse、evidence honesty、long-chain completion、overengineering、semantic drift。
4. 只有 Stage 02 claim reconciliation + project qualification evidence足够后，Stage 03 才决定 global mechanism 的最小 contract / data shape，以及 §7.1 保留什么 pointer。

## F. 当前不作出的结论

- 不在本文件给出最终“某类任务必须由某模型执行”的 routing table。
- 不因厂商 benchmark 给 Antigravity Gemini/Opus 自动授予 qualification。
- 不把价格、token cost、quota conservation作为 routing objective。
- 不决定 canonical implementation path；`03_mechanisms/**` 是 A v2 的架构约束方向，但具体文件/contract由 Stage 03 结果模型决定。
