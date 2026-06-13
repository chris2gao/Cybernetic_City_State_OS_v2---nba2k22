# 赛博城邦 (Cybernetic City-State OS) 总体架构蓝图 v4.3 (Stage 1 完结版)

## 核心设计哲学 (Core Philosophy)
基于“大模型智能主导（LLM-Native）”原则，将复杂的传统操作系统概念（如锁机制、匿名化、死锁检测）转化为纯粹的“语义与文件拓扑”设计。完全摒弃基于 Python 的硬编码锁与死板工作流。
在这个系统中，所有的逻辑流转、冲突解决与信息过滤，全部由被压铸了特定 XML 人格（Persona）的大模型自主完成。

## 物理拓扑架构 (Agent Worktree Topology)
系统不依赖底层数据库，而是利用本地 Markdown 文件系统（借鉴 Git 思想）物理隔离不同 Agent 的工作区，实现无锁并发与信息防污染：
*   `/04_Parliament/Proposals/`: 提案与法案存放区，供全体议员审议。
*   `/00_Evidence_Room/compiled_evidence.md`: 绝对客观的全局脱敏证据池。
*   `/workspace_{agent_name}/scratchpad.md`: 智能体各自的隐秘深研空间，彼此绝对隔离。
*   `/06_Silicon_Index/Personas/`: 城邦的元骨架与人格协议库。
*   `/07_Execution_Plans/`: 历次战役的系统级架构图纸存档。

---

## 🛤️ 实施路线图 (Phased Implementation Roadmap)

### 阶段 1：奠基双核底层基建 (Foundation Layers) [✅全线竣工]
这是城邦信息获取与逻辑推演的心脏，必须在任何宏观提案流转前完工。分为两大战役：

#### 战役一 (Phase 1.1)：分布式深研与人格上下文融合系统 [✅已竣工]
赋予大模型极端的认知偏见，让它们在面对同一任务时搜集完全不同的信息，打破同质化茧房。
*   压铸了 `Deep_Research_Red_Teaming_Module.xml` 与 `Identity_Masking_Protocol.xml`。

#### 战役二 (Phase 1.2)：证据思维链融合系统 (Evidence-Based CoT Fusion) [✅已竣工]
将 Antigravity 定制模型自带的高维内部思考机制（Thinking）与外部的真实物理证据链强制融合。
*   压铸了：`Evidence_Based_CoT_Fusion_Module.xml`
该组件作为一个强大的“认识论引擎 (Epistemological Engine)”挂载给所有推理模型，包含以下 LLM-Native 工程特征：
1.  **虚拟记忆塌陷 `<Memory_Collapse_Phase>`**：解决不可逆 Token 的截断问题。通过强制生成纯净状态注入 (`<Clean_State_Injection>`)，触发宿主 `[VCCOMPACT]` 进行 L1/L3 冷热驱逐，主动“遗忘”错误的探索分支。
2.  **异步协调账本 `<Asynchronous_Coordination_Ledger>`**：解决多智能体裂变（`invoke_subagent`）导致的收敛死锁与结构性竞争冲突 (SRCs)。引入乐观并发控制锁 (OCC)。
3.  **自适应认知修剪 `<Budget_Warning_Threshold>`**：防范过度思考循环。当算力不足时强制收敛。预算耗尽时输出 `<Partial_Solution_Fallback>` 残缺闭环，标明“尚未定论”，杜绝强行圆谎。

---

### 阶段 2：压铸三大纯 LLM 路由控制节点 (Routing Nodes) [⏳待建]
在第一阶段信息与思维基座建成后，组装辩论引擎。
1.  **主控聚合器 (Aggregator)**: 负责宏观任务拆解，并根据不同人格生成初始《提案草案》。
2.  **洗稿智能体 (Epistemic Purifier)**: 贯穿全流程的认知净化器，消除辩论情绪。
3.  **最高裁决者 (Arbiter)**: 不写任何代码，专门通过计算每一轮辩论的“语义信息增益 (Semantic Information Gain)”，判断辩论是正在收敛还是陷入了死锁，从而动态阻断死循环。

---

### 阶段 3：搭建第二重检查引擎 (Verification Sandbox) [⏳待建]
在独立沙盒内全量执行提案代码，如果发生崩溃，不再是抛出干瘪的 Error，而是由审核官输出“导致崩溃的定量边界参数”（误差梯度），给主控指明精确的修改方向。
