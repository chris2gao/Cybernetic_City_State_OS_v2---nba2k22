# 🏛️ 议会议案 (Issue)

**提案编号**: Issue_004
**提案主题**: System Prompt v6.0 核心引擎重构：算力解耦与超纲防范架构 (Decoupled Compute & Curriculum Ceiling Isolation)
**提案人**: Antigravity (首席系统架构师)
**提交时间**: 2026-06-04
**状态**: ✅ CLOSED - 已执行 (Executed)

---

## 1. 背景与核心危机 (Context & Core Crisis)

基于独立专家模型对 **Phase 0 (核心教学对齐)** 与 **Phase 5 (超纲天花板隔离)** 输出的两份红队深度研究报告，我们的教学系统虽然在隐喻构建上达到了极客水准，但在底层物理架构上面临两大严重危机：

1. **算力过载与冗余生成 (Compute Overhead)**：
   目前的大模型需要在每一次交互回合中生成巨大的 JSON 依赖分析。这不仅带来了灾难性的首字节延迟 (TTFT)，更极大地浪费了 Token 额度。
2. **“白熊效应”导致的认知泄密 (Ironic Process Theory Leakage)**：
   如果大模型在 Prompt 内部去扫描未来的节点以生成“不可用词汇黑名单”，其自注意力机制（Self-Attention）会不可避免地被这些高阶词汇锚定，从而在教学正文中产生极其隐蔽的“超纲词汇泄露”。

## 2. 改进方案 (Proposed Solution)

我提议对底层的 `02_Protocols/数学架构师导师System_Prompt_v5.6.md` 执行一次彻底的 **v6.0 基因重组**，核心重构操作包含以下三项：

### 2.1 算力解耦与缓存前置 (Decoupled Compute & Prompt Caching)
彻底改变 `【内审草稿】` 的全量生成模式。
*   **静态外部注入**：`[ALLOWED_FOUNDATIONS]` (已解锁基础工具白名单) 和 `[FORBIDDEN_TERMS]` (未来节点黑名单) 必须由外部前端工作流或静态 Python 脚本在后台提前洗出，并直接作为静态环境变量注入到 Prompt 头部。
*   **动态轻量生成**：大模型在多轮对话中的 `【内审草稿】` JSON，被强制缩减为仅包含两项动态任务：`隐喻查毒 (Metaphor Check)` 和 `苏格拉底步幅测量 (Step-size Evaluation)`。

### 2.2 致命红线硬编码 (QA Redlines Hardcoding)
在指令的最顶层优先级，暴力注入专家模型提出的三大防线：
*   **防诱导栈溢出 (`CONSTRAINT_COG_LOAD_LIMITER`)**：强制回复以单一问号结尾，禁止一切平行追问。
*   **打击虚假对齐 (`CONSTRAINT_STRICT_TYPING_VALIDATOR`)**：严禁大模型为了“友好（Helpful）”而肯定学生那些违背底层数学拓扑的“工程 Hack 捷径”。
*   **强制红蓝对抗 (`CONSTRAINT_CRISIS_TENSION_AMPLIFIER`)**：在制造物理危机前，大模型必须在隐性推理中自我验证——旧的工具在当前场景下是否必定抛出致命 Error。

### 2.3 设立“预叙”破例机制 (Prolepsis Exception)
在极度冰冷的隔离高墙上开一扇可控的窗。当且仅当底层记录显示学生已达到 `node_mastery_completed` 状态时，允许大模型在 JSON 中写入 `prolepsis_event: true`，并使用极其克制的修辞，向学生抛出一丝对更高阶维度的“未来视界预告”（例如，在讲完无穷级数时暗示泰勒展开），以点燃顶级架构师的智力渴望。

## 3. 预期影响 (Expected Impact)

1.  **极简与极速**：交互延迟将大幅下降，大模型的算力被 100% 集中于“如何提出下一个最具穿透力的问题”。
2.  **绝对无菌的教学环境**：物理切断了高阶知识下沉污染低阶认知图式的可能性，彻底驯服了 LLM 的“全知视角诅咒”。

## 4. 议会审议焦点 (Points for Debate)

1.  **外部静态注入流**：在 v6.0 部署后，我们如何确保宿主或前端应用能够稳定地从 YAML 中读取并合成 `[FORBIDDEN_TERMS]` 传递给 LLM？
2.  **向后兼容性**：v6.0 极度削减了内审草稿的厚度，这是否会导致原有的某些测试判定脚本失效？

---
---
**[决议记录 (Resolution Log)]**
*   **2026-06-04 [REVIEW]**: 首席审查官 Atlas 下发《审查意见》，指出前端需做好防漏解析和 JSON 强类型拦截的保险丝。
*   **2026-06-04 [VOTE: APPROVE]**: 议长行使最高裁决权，全盘接纳审查意见并批准合并。
*   **2026-06-04 [EXECUTE]**: Antigravity 完成物理重写，`v6.0` 引擎挂载成功，独立路由器 Prompt 部署完毕。议案正式关闭，封入历史库。
