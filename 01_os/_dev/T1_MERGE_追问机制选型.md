# T1 合并报告 · 追问机制选型

来源：ChatGPT web 与 Gemini 3.1 Pro web 两份独立调研，互不知情。
合并方法：**先看差集，再看共识**。

---

## 一、并行的实测价值：16 个候选，1 个重合

| | Gemini 找到 | ChatGPT 找到 |
| :--- | :--- | :--- |
| 路线 | 学术 / 本体 / 神经符号 | 产品 / 提示词包 / 编程 agent |
| 候选 | OntoAgent、OntoChat、RequireCEG、FRET、PromptKit、iReDev、ReqElicitGym | spec-kit、BMAD-METHOD、ai-prd-workflow、ai-dev-tasks、Copilot custom agents、hermes-agent、elicitation(Rust)、gpt-pilot、Lovable、Replit |
| 重合 | **仅 ReqElicitBench 一项** | 同 |

**两个模型搜的是两个不相交的宇宙。** 只派一个，会拿到一份看起来完整、实际漏掉另一半的图景，
而且没有任何东西会提示我们漏了。这是本次并行最直接的产出——**不是候选清单，是候选清单的可信度**。

## 二、最强的信号：两份独立报告撞上同一堵墙

这是本次调研最值钱的一条，因为它来自**两个不相交的检索空间的一致结论**。

**Gemini**：
> 并未找到以"信息熵降至某一绝对数值"作为停止追问条件的开源对话系统。
> 目前的追问停止机制多依赖于大模型的主观判断或静态本体槽位的填满。

**ChatGPT**：
> I did **not** find an off-the-shelf implementation that publicly describes its stop rule as
> "question until expected ambiguity reduction falls below threshold," or
> "until all high-value propositions reach mutual acceptance confidence."

**结论：追问的停止条件，全世界目前都只有启发式，没有认识论意义上的判据。**
现存的全部停止方式只有四种——问满 N 个、槽位填满、模型主观判断"够了"、用户说停。

这与我们在 `WORKFLOW_BACKBONE_v0.2.md` 里记下的残留风险是**同一个问题的两次显形**：
「证据集的完备性无法由证据集本身证明」。我们不是没查到答案，**是这个答案还不存在**。

## 三、第二个共识：缺的不是 PRD，是"共识对象"

**ChatGPT**：现有系统产出的主流仍是 markdown 计划或 PRD，
而不是一个"命题、假设、已解决歧义、未解风险、已接受术语"的**显式结构**，可供下游独立消费。

**Gemini** 从理论侧指向同一处：认知科学的 grounding in communication（沟通中的基础构建）
有深厚积淀，但**没有工程实现把双向信念状态机作为停止条件**。

我们阶段一的目标——"双方陈述该需求时指的是同一件事"——**正好落在这个空白里**。

## 四、候选横向对比（合并）

| 候选 | 停止条件 | 产出 | 可改造 | 许可 |
| :--- | :--- | :--- | :--- | :--- |
| **github/spec-kit `/clarify`** | ≤5 问、依赖序、无高影响歧义即停 | 写回 spec 的 clarifications 节 | 方法可单独移植 | MIT，124k★ |
| **OntoAgent** | 本体树高优先级槽位填满或最大轮数 | 结构化本体实例 | 方法论高度可复用 | 学术原型 |
| **crumplecup/elicitation** (Rust) | **schema 在约束下填满** | 类型化、已验证的对象 | 库，需自行编码 | MIT/Apache |
| **RequireCEG** | 因果图上不再发现歧义与断层 | 无歧义 Gherkin + 因果逻辑图 | 核心算法可复用，防幻觉 | 学术开源 2025 |
| **BMAD-METHOD** | Forge Idea：硬化 / 否决 / 更清晰 | brief、prd.md、forge-report | 方法可分离 | MIT，51k★ |
| **ai-dev-tasks 系** | 只问 3–5 个最关键问题 | markdown PRD + 任务清单 | 最小提示词方案 | Apache-2.0 |
| **hermes-agent `clarify`** | 单次阻塞至回答 | 用户答案，非规约 | **构件**而非方法论 | MIT |
| **FRET** (NASA) | 内部一致性检查无冲突 | 形式化逻辑公式 | 适合做下游硬验证层 | Apache-2.0 |
| **ReqElicitBench / ReqElicitGym** | — | 覆盖率报告、交互日志 | **评测台**，非机制 | 学术，唯一重合项 |

## 五、选型建议

**不采用单一现成方案。三段拼装，各取其最强的一段。**

1. **交互形状取 `spec-kit` 的 `/clarify`** ——
   一次一问、依赖序、有问题预算、答案**写回结构化产物**而不是留在对话里。
   这是最成熟、最可移植、且已被 124k star 验证过的循环形状。

2. **产出形态取类型化 elicitation 的思路** ——
   停止条件是 **schema 在约束下填满**，产出是类型化对象而非自由文本。
   这直接满足我们"产出要供下游证据收集与结果建模消费"的要求。
   `crumplecup/elicitation` 是概念样板，不必用 Rust。

3. **评测取 ReqElicitBench** ——
   唯一被两份报告同时找到的项目，且它评的正是我们关心的维度：
   问题效率、遗漏需求覆盖率、对话修复行为。**有它才谈得上"这个机制好不好"。**

**两份报告独立给出的最终建议高度一致**：grounding 理论定目标 +
类型化/schema 驱动定产物 + 基准化的提问质量模块定交互策略。

## 六、我们要自己造的那一块

**停止条件。** 现成的四种（问满 N 个 / 槽位填满 / 模型说够了 / 用户喊停）
没有一种能回答"双方是否真的指同一件事"。

可参考但未被工程化的方向：
- 信息论——追问带来的期望信息增益降至阈值以下
- 认知科学——显式的双向信念状态机（"你认为我想要什么"）
- OntoAgent 的门控剪枝，是目前最接近的工程近似

**这一条与机制 2 的"何时停止收集信息"是同一个问题。**
两个阶段共用一个未解难题，值得合并研究而不是各做一遍。

## 七、检索边界（两份都如实记录了）

**Gemini** 指出一个结构性截断：GitHub 搜索权重偏向高星标大框架，
个人开发者写在单个 prompt 文件或子目录里的实现**不会被索引成独立项目**——
所以"没有任何文档描述该流程"是一种**检索错觉**。企业内部 SaaS 的工程细节亦不可见。

**ChatGPT** 明确声明 "a bounded search, not proof of absence"，
列出了 productive 与 low-yield 的具体查询串，并报告了 GitHub 页面渲染失败导致的回退。

**两份都没有把有界检索当成全集。** 这正是 T1 请求里那条要求的目的，
而它的价值在第二节体现出来了：**两个有界检索撞上同一堵墙，比任何一个声称"没有"都可信。**

---

## 八、下一步

**T5 · 机制 1 实现**：按第五节三段拼装。
形状与产物已定，**停止条件先用 `spec-kit` 的问题预算兜底**，
真正的判据等第六节的合并研究出结果再替换。

先能跑，再讲究——骨架的要求是接得上。
