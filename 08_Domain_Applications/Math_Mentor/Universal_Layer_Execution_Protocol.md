# Universal Layer Execution Protocol (通用层级执行规范)

## Current Authority And Supersession Notice

This file remains the durable lane-routing, split-roadmap, batch-size, and generation guidance for Math Mentor. Current execution and status semantics are additionally governed by:

- `KNOWLEDGE_COMPLETION_PROGRAM.md` for Stage 0-9 completion gates;
- `V9.1_教学流程系统规范_Teaching_Flow_Spec.md` for current teaching behavior;
- `TOOL_TRUTHFULNESS_POLICY.md` for executable and semantic evidence wording;
- `BRIDGE_SCHEMA.md` and an explicit Human-approved P3 launch for bridge work.

Where older wording below would imply machine proof for Mode B, automatic bridge generation, automatic indexing, or Coordinator consumption, the conservative current contracts above supersede it. Historical `Mode A`/`Mode B` labels map to `MathLane_A`/`MathLane_B` in current teaching state.

针对知识点库（Level 1 至 Level 6）自下而上的构建，为了保证各个领域之间知识点的**完备性**、**依赖一致性**以及**跨层关联性**，我们确立了标准操作流程 (SOP)。

根据**《V9.1 神经符号双擎防崩溃指南》**的历史决议，系统目前采用**双轨制执行流 (Dual-Track Workflow)**。各个层级的特性不同，适用的生成与测试管线也存在本质差异：

## 🗺️ 领域层级与适用轨道分析

### 第一层至第三层 (Level 1 - Level 3)
- **涵盖领域**：基础逻辑、代数初步、微积分、线性代数、概率统计。
- **特征属性**：绝大部分具备极强的计算性和代数封闭性，变量有限且维数确定。
- **适用轨道**：**【计算代数主路 (Computable Algebra Lane)】**（完全采用经典的 V8 形式化验证流程）。
- **特例保留**：在第一层中，**公理化集合论 (ZFC)**、**可数性与不可数性 (Cantor连续统)**、**哥德尔不完备性定理** 以及 **类型论基础** 涉及极其抽象的元逻辑与无穷嵌套。这些知识点**必须**走【纯数结构高架 (Mode B)】进行语义连贯性审查，严禁送入 Z3。

### 第四层至第六层 (Level 4 - Level 6)
- **涵盖领域与精确分轨**：
  - **【必须走纯数结构高架 (Mode B)】**：**泛函分析**、**点集拓扑**、**实变函数**、**抽象代数**（抽象环/域）、**代数拓扑**、**整体微分几何**、**代数几何**、**范畴论**、**朗兰兹纲领**。这些领域高度抽象，强行送入 Z3 会引发物理死锁。
  - **【必须走计算代数主路 (Mode A)】**：**复变函数**（留数计算、洛朗展开等）、**抽象代数**（有限群置换矩阵）、**数论**、**局部微分几何**（张量计算）、**偏微分方程**、**椭圆曲线密码学**。这些领域具备极强的可计算性，仍受严格的物理断言测试约束。

---

## ⚙️ 核心 SOP 执行四个阶段

无论走哪条轨道，基础的“扫描”与“桥接”阶段是通用的，但在“生成”与“验证”阶段，两条轨道发生彻底异化。

### 阶段 1：拓扑扫描与防冗余清洗 (Topology Scan & Deduplication) [双轨通用]
在真正开始批量生成之前，必须首先读取**目标层级对应的拆分路线图**，而不是默认读取 `数学知识路线图_全部.yaml`：
- Level 1：`数学知识路线图_第一层基础工具.yaml`
- Level 2：`数学知识路线图_ 第二层核心基础.yaml`
- Level 3：`数学知识路线图_第三层大学核心.yaml`
- Level 4：`数学知识路线图_第四层进阶分析.yaml`
- Level 5：`数学知识路线图_第五层专业方向.yaml`
- Level 6：`数学知识路线图_第六层前沿领域.yaml`

`数学知识路线图_全部.yaml` 仅允许在全图编号审计、全层级去重、跨全域桥接重建等确实需要完整知识图谱的任务中读取。常规层级生成、补全、验收与索引注册必须使用拆分路线图，以避免上下文窗口被全量路线图吞噬。

完成目标层级加载后执行：
- **清洗冗余节点**：识别路线图中因历史原因遗留的重复节点，及时在架构层面进行裁剪合并。
- **前置知识校验**：根据层级的前置要求，检索上一层级是否已经完全具备本层级所需的知识节点。

### 阶段 2：特工网络批处理生成 (Agentic Batch Generation) [按轨道分化]

**【核心系统级约束：精英小队与上下文复用原则】**
针对本城邦内所有的独立大模型（Subagents）初始化，以及外部调用的外包管线，均**强制遵守**以下资源调度底线规则：
- **严禁并发泛滥**：任何层级的节点批量生成，**最多仅允许拉起 5 名并发特工**。
- **强制小批次验收**：无论节点已生成多少，后续沙盒验证、语义审查、合流前复核都必须按外包批次拆开执行。每个物理验收批次最多处理 **5 个节点**；严禁一次性把几十个节点交给同一个 evaluator 进程，以免触发超时、日志截断或上下文污染。
- **任务触发的精确引用与串行批处理**：只有当前任务确实需要某份核心参考资料时，特工才按仓库相对路径读取该文件。禁止为了背景知识读取整个参考目录。完成必要读取后，在同一上下文中采用**串行循环（Sequential Batching）**连续处理分配的节点，避免“一节点一特工”的上下文浪费。

将该层级下数十个节点根据上述原则划分为多个批次，通过最多 5 名子特工网络执行：

- **【计算代数主路 (L1-L3 & L4+计算分支)】**：
  - 强制包裹 `sub_topics` 确保知识完备。
  - 强制植入现实世界的物理隐喻 `llm_physical_mapping`（如“天平”、“显微镜下的网格”）。
  - 强制提供用于形式化验证的 `v8_sanity_audit.sympy_pseudo_code`。

- **【纯数结构高架 (L4-L6 抽象分支)】**：
  - **异化规则**：放弃通俗的物理隐喻，启用**认知映射引擎 (Cognitive Mapping Engine)**。
  - **任务触发的架构参考集**：当当前任务涉及 Mode B 映射生成、修复或语义审查时，按需读取以下精确仓库相对路径；不得读取整个 `backup/` 目录：
    1. `08_Domain_Applications/Math_Mentor/学习期prompt/backup/大模型解剖图：深入解析.md`
    2. `08_Domain_Applications/Math_Mentor/学习期prompt/backup/大语言模型数学底层架构全阶段深度解析整合报告.md`
    3. `08_Domain_Applications/Math_Mentor/学习期prompt/backup/英语算子直觉与语义架构索引.md`
  - 如果当前 checkout 缺少任一命名文件，必须记录缺失路径并将相关映射工作标记为 `review_required`；不得猜测、改名或发明替代路径。
  - **`llm_physical_mapping`**：必须将抽象数学结构直接映射到大语言模型 (LLM) 自身的物理架构上（例如：泛函内积 $\to$ Attention $QK^T$，拓扑同胚 $\to$ Transformer 残差流，抽象代数群 $\to$ Word2Vec 词嵌入空间）。
  - **代码锚点**：不再提供用于断言的代码，而是提供诸如 PyTorch 神经网络前向传播的核心片段作为直觉锚点。

**【双轨通用：误区证据前置 `common_misconceptions`】**

新生成或修复的节点必须提供 `common_misconceptions` 数组，每项含 `signature`（误区的稳定签名，用于识别同签名二次错误）、`description`（学生会怎么错）、`repair_direction`（不重复失败讲法的修复方向）。

该字段属于教学证据层，不是教学正文。它把陷阱方向前置到语料，供 Prep_Architect 构造 `exam_handoff_conditions.trap_direction` 与 `reprep_triggers`，避免教师临场发挥决定考什么、怎么修。

既有节点缺失该字段时**不阻断教学**：Prep_Architect 自行构造陷阱方向，并在 `evidence_trace.limits` 标注 `common_misconceptions_absent`。不得为补齐该字段而改写既有教学内容；补齐属于节点修复任务，需按批次授权执行。

该缺失是**显式技术债，不是永久豁免**：

```yaml
common_misconceptions_gate:
  new_or_repaired_node: required          # 缺失即不通过 Stage 4
  existing_node_missing: warning_with_backfill_queue
  silent_permanent_absence: forbidden
```

即：既有节点缺失时发出警告并登记补齐队列条目；不得因为“暂不阻断”而让缺失静默长期存在。
Stage 4 教学就绪门与节点质量审计共同承载该检查，`common_misconceptions` 不是身份字段，
也不应推迟到 Stage 6 桥端点认证才检查。

### 阶段 3：沙盒验证与测试 (Sandbox / Audit Evaluation) [按轨道分化]

- **【计算代数主路】** $\to$ **沙盒全量测试 (Bulk Sandbox Evaluation)**
  - 执行 `bulk_evaluator.py` 或单节点 `sandbox_evaluator.py`，但必须按外包批次拆分；每批最多 5 个节点。
  - 确保代数逻辑无 Syntax Error 与 Assertion Error，目标是 **100% PASS**。

- **【纯数结构高架】** $\to$ **语义连贯性审查 (Semantic Consistency Audit)**
  - 遇到诸如 `topology`, `banach`, `compact` 等词缀时，总线**切断 Z3/SymPy 执行链路**。
  - 主控模型只能形成自然语言语义审查证据。未完成 Human/ChatGPT 审查时使用 `review_required`；完成概念、定义、前置、映射边界与教学价值审查后可记录 `semantic_only` 和具体 reviewer evidence。
  - Mode B 不存在机器式 pass。已有代码或伪代码只能作为直觉锚点、可计算特例或待审证据，不能证明完整抽象结构。
  - Human/ChatGPT 的语义接受是后续 teaching/bridge readiness 的必要证据之一，但不等于 deterministic validation、full-node correctness 或 bridge-ready。

### 阶段 4：Stage 6 Bridge-Readiness Certification [不生成 Bridge]

节点生成或修复完成后，先按 `KNOWLEDGE_COMPLETION_PROGRAM.md` Stage 6 认证可作为 bridge endpoint 的节点：

- 身份、formal content、`sub_topics`、前置关系、教学 readiness 和 lane-correct validation evidence 必须齐全；
- Mode A 需要接受的计算证据，Mode B 需要 Human/ChatGPT 语义接受；
- 未满足条件的节点保持 `manual_review_required` 或 `review_required`；
- 本阶段不得创建、修改、索引或消费任何 `BRIDGE-XXX.yaml`。

真正的同层/跨层 bridge 设计与落地必须等待：

1. Human 明确重新开放 P3，并命名 certified endpoint set 与 immutable source HEAD；
2. 独立 bridge design review 通过；
3. Human 明确授权 bridge landing；
4. Stage 8 完成 validation、registry/index 和 Coordinator consumption 审批。

在 Stage 8 批准前，任何 bridge 都不得进入正式 Coordinator consumption。

---
**执行时机**：层级或主分支完成后，只执行当前 Human packet 明确授权的阶段。节点完成不会自动触发 P3、bridge 生成、索引或 Coordinator consumption。
