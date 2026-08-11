# **需求追问机制与结构化建模底层实现深度剖析报告**

## **0\. 检索过程、事实与推断标准及核心发现声明**

为确保本技术报告的严谨性与底层工程参考价值，本节首先对信息来源、事实与推断的区分标准，以及检索过程中发现的增量信息进行显式声明。

### **0.1 检索动作与结果截断报告**

【文献事实】针对 github/spec-kit 的底层实现，系统执行了指向 templates/commands/clarify.md、SKILL.md 源码以及 issues 的定向检索，关键词包括 standalone、decouple、extract 以及 lazy deferral。针对机械判定停止条件，检索了 Pydantic V2 的 ValidationError、TypeAdapter、loc 与 type 字段的具体表现机制。针对古典对话系统，定向检索了 Rasa 3.0 slot mappings "from\_entity" deprecated 与 Dialogflow CX 的 parameter status "FINAL" 状态机文档。针对学术界评测，检索了 arXiv 上的 2602.18306（ReqElicitGym）文献。 【文献事实】在检索 ReqElicitGym 的具体论文详情页（如 URL: https://arxiv.org/html/2602.18306v1）时，遭遇了 This website is inaccessible 的截断错误1。随后，通过备用节点、PDF 解析缓存以及 ResearchGate 镜像2，成功恢复了该基准测试的数据集拓扑与基础设施全貌。在尝试搜索 spec-kit 的官方剥离（Standalone）版本时，返回结果为空，这证实了官方并未提供独立的 API 接口，所有解耦行为均属于社区的非官方改造或底层逻辑复用。

### **0.2 事实与推断标注规范**

为满足严苛的架构参考需求，本报告将在正文中逐条标注信息的认识论属性：

* **【文献事实】**：指直接来源于官方文档、源码注释、GitHub Issues 讨论记录或论文原文的客观数据与机制描述。  
* **【逻辑推断】**：指基于上述事实，结合软件工程、编译原理或大型语言模型（LLM）架构知识，推演出的实现路径、系统设计方案或踩坑预警。

### **0.3 显而易见的信息与高价值增量发现**

【逻辑推断】在技术常识层面，诸如“Pydantic 可以抛出 ValidationError 拦截缺失字段”、“Rasa 依赖 Forms 机制填槽”、“spec-kit 通过 Prompt 指导大模型发问”等信息属于显而易见的行业共识，预计任何常规调研均会涉及这些基础结论。 【文献事实】相对地，本报告发掘到了以下具有极高工程指导价值的增量信息： 首先，spec-kit 的 /clarify 机制在实际生产中存在严重的“懒惰延迟（Lazy Deferral）”缺陷（详见 Issue \#1717）。由于大模型依赖粗粒度的关键词匹配，它倾向于将大量应在需求阶段澄清的模糊点直接推迟到计划（Plan）阶段，从而导致下游任务的灾难性失败4。 其次，古典系统 Dialogflow CX 时代遗留的 $page.params.status \= "FINAL" 状态机闭环机制，在底层拓扑上与当前大模型 Agent 工作流中通过 JSON Schema 校验是否 is\_final 的架构完全同构，其“状态拦截”思想至今仍然是工程实现的最优解5。 最后，最新的 2026 年基准测试 ReqElicitGym 数据揭示，即便是顶级大模型（其隐性需求发掘率 IRE 仅为 0.32），在面对“风格偏好（Style-related）”这一维度的隐性需求追问时也遭遇了全面溃败2。这一发现为系统设计提示词时强制挂载“特定领域探针”提供了直接的实证依据。

## **1\. github/spec-kit 的 /clarify 剥离剖析与工程实践**

github/spec-kit 中的 /clarify 命令是当前开源界实现“结构化需求追问”的代表性范式。本节将从底层源码级别剖析其提示词逻辑、运行时依赖，并深入挖掘实践者在尝试剥离或改造该机制时遭遇的真实工程陷阱。

### **1.1 /clarify 的底层提示词逻辑与执行流程**

【文献事实】根据代码库中的 templates/commands/clarify.md 与 .agents/skills/speckit-clarify/SKILL.md，/clarify 并非一个自由发散的对话接口，而是一个被严格约束为“带状态控制的结构化扫描与原子化覆写循环”的复杂工作流7。其核心运转机制可以拆解为以下几个精密咬合的齿轮。  
【文献事实】第一步是强制分类树扫描（Taxonomy Scan）。在加载现有的需求规范（Spec）文件后，大模型被指令强制要求使用一套内部硬编码的分类树进行覆盖率扫描。这套分类树覆盖了核心功能、数据模型、交互流程、非功能属性、外部依赖、边缘情况等维度。每一个细分维度都会被模型静态标记为 Clear、Partial 或 Missing7。  
【逻辑推断】第二步是启发式优先级计算。在发现多个 Partial 或 Missing 状态后，提示词要求模型通过一个隐式的 (Impact \* Uncertainty)（影响程度乘以不确定性）算法来为候选问题打分排序，从而提取出优先级最高的 5 个追问候选点7。这种设计避免了模型在细枝末节上浪费追问轮次。  
【文献事实】第三步是极度严苛的交互格式约束。系统严格要求模型“每次只能提出一个问题（Present EXACTLY ONE question at a time）”，并且规定了具体的 Markdown 渲染格式。对于选择题，模型必须基于项目宪法给出一个附带 1-2 句解释的“推荐选项（Recommended）”，随后列出 A-E 的备选项，最后还要包含一个“提供简短回答（\<= 5 个词）”的兜底通道7。在特定集成环境（如 Claude Code）中，这些表格会被拦截并后处理为 UI 原生的下拉组件载荷（AskUserQuestion）9。  
【文献事实】第四步是原子化覆写（Atomic Overwrite）。这是该流程最核心的设计。模型在收到用户答复后，不会等待整个 5 轮追问结束，而是立即在内存中更新数据，并在文档中追加 \#\# Clarifications 会话记录，同时**立即修改 Spec 文件对应的原始段落**（例如补充功能列表或细化数据字段）7。这种设计确保了状态的即时持久化，避免了长对话带来的上下文遗忘。

### **1.2 剥离所需的依赖斩断分析**

【逻辑推断】若要将 /clarify 剥离为独立的后端服务以供纯代码下游程序消费，就必须识别并斩断其深度耦合的 CLI 与运行时依赖链，并将其替换为可编程的 API 接口。  
【文献事实】在运行时层面，/clarify 首先强依赖文件系统路径注入。它通过执行位于根目录的 .specify/scripts/powershell/check-prerequisites.ps1 \-Json \-PathsOnly 脚本来捕获诸如 FEATURE\_DIR 和 FEATURE\_SPEC 等绝对路径环境变量7。如果解析失败，流程将直接中止。其次，它强依赖记忆约束文件，即在启动前必须读取 .specify/memory/constitution.md，以此作为生成选项时的“最佳实践”先验知识边界7。最后，它的原子化覆写逻辑极度依赖预设模板（spec-template.md）中的固定标题锚点，若缺少这些标准化的 Markdown 结构，模型的正则或语义替换行为将发生严重漂移7。  
【逻辑推断】基于上述事实，剥离的具体工程实现不应尝试调用其 CLI 包，而应直接提取其 Prompt 模板思想。实现层面需要做出三大改造：将物理文件系统的 I/O 替换为通过 HTTP 传递的纯内存 JSON 状态；将 constitution.md 中的架构原则动态序列化后注入 System Prompt；最后，彻底抛弃 Markdown 文本锚点，将目标输出抽象为一个结构化的 JSON Schema，要求大模型在追问后直接返回更新后的 JSON 补丁（Patch）而非尝试编辑 Markdown 文本。

### **1.3 实际剥离尝试与致命缺陷（失败案例复盘）**

【逻辑推断】只阅读官方的成功路径很容易低估该工作流在真实生产环境中的脆弱性。通过挖掘开发者社区的抱怨与 GitHub Issue，本报告总结了剥离与复用该机制时必然遭遇的几个工程深坑。  
【文献事实】最致命的问题被称为“懒惰延迟（Lazy Deferral）”灾难，记录于 Issue \#1717。当开发者运行 /clarify 时，Agent 需要判断哪些缺失项应该现在追问，哪些属于具体实现细节应该推迟到架构规划（Plan）阶段。然而，由于大模型依赖的是基于项目文本的粗粒度直觉判断，而非严格的逻辑树匹配，它选择了一条极其“懒惰”的路径：将 24 个本应在需求阶段澄清的关键模糊点（如并发用户量限制、空状态的 UX 交互、外部 API 失败策略等）全部标记为“Plan-stage concerns”并拒绝提问，最终荒谬地输出“No critical ambiguities detected”4。 【逻辑推断】这一失败案例强烈警示：在剥离追问机制时，绝不能将“是否需要追问”的判定权完全交由 LLM 的内部涌现能力。系统必须在 Prompt 外部引入强制的“阶段归属卡点（Stage Gate judgment）”，通过硬编码的规则引擎强制 LLM 针对特定的空槽位进行提问，剥夺其单方面宣布“推迟”的权力。  
【文献事实】其次是上下文重置与状态丢失问题，记录于 Issue \#954 与 Claude 用户的实践反馈。用户报告指出，在执行过一次覆写后，如果要针对修改后的状态进行二次编辑，Agent 经常会失去对原始业务意图的焦点，导致在后续修复时破坏原有的规范上下文4。有用户直言这一基于文本不断覆写的体验“非常糟糕（pretty awful）”，不仅无法维持透明度，反而增加了识别和修复错误的繁琐度12。 【逻辑推断】这证明了 /clarify 的“无状态设计 \+ 原子化文本覆写”在面对高复杂度需求演进时存在严重瓶颈。对于下游需要消费结构化数据的程序而言，强行套用 spec-kit 这种复杂的 A-E Markdown 表格生成和文本编辑逻辑是僵化且低效的。在剥离实现中，应该放弃大篇幅文本的维护，转而维护一棵细粒度的 JSON 抽象语法树（AST），将每次追问的答案精确挂载到具体的 JSON 节点上。

## **2\. “Schema 在约束下填满”的停止条件：高度机械化判定实现**

【逻辑推断】对话系统与需求启发引擎最核心的算法难点，在于如何在无人值守的情况下，自动判断需求已经完全结构化，即“何时算填完”。为了稳定地供下游程序消费，这一停止条件的判定必须是高度机械化、确定性（Deterministic）的。依赖 LLM 自行宣告“我已经问完了”极易重蹈上述 spec-kit 中“懒惰延迟”的覆辙。因此，本节重点讨论可实现性极高的 Pydantic / JSON Schema 校验栈。

### **2.1 依赖 Pydantic 的确定性错误捕获引擎**

【文献事实】在 Python 的 Pydantic V2 生态中，数据验证的底层逻辑是抛出高度结构化的 ValidationError 异常。当输入的 JSON 数据（由 LLM 从用户自然语言中提取得到）无法满足模型定义的硬性约束时，ValidationError 会包含一个精确描述所有缺陷的列表。每一个缺陷对象包含 loc（以元组形式表示的嵌套层级路径，如 ('items', 1, 'value')）、type（错误标识符，如 missing、value\_error、assertion\_error）、msg（人类可读的错误描述）以及 input（触发错误的原始输入值）13。  
【逻辑推断】这种确定性的异常抛出机制，为“机械判定停止条件”提供了完美的底层支撑。通过将大模型的输出喂入 Pydantic 构造器，系统能够将语义理解的模糊性转化为类型系统的静态严谨性。以下表格展示了如何将具体的 Pydantic 错误映射为系统的追问策略：

| 错误特征提取 | Pydantic 字段表现 | 机制判定与追问策略生成 |
| :---- | :---- | :---- |
| **必需槽位缺失** | type \== 'missing'，loc 指向具体缺失字段。 | 系统判定：用户未提供核心业务参数。提取 loc 对应的字段 Docstring，直接组装入提示词：“由于当前缺少 {loc} 参数，请询问用户具体需要什么”。 |
| **类型或格式不合法** | type \== 'type\_error' 或 string\_pattern\_mismatch。 | 系统判定：用户提供了参数，但超出了系统可消费的范围（如需要枚举值，用户却随意发挥）。将 input 和预期的类型定义抛给 LLM，令其要求用户重新选择。 |
| **业务逻辑冲突** | 自定义验证器触发 type \== 'assertion\_error'16。 | 系统判定：跨槽位约束失败。例如“选择了线下发货，但缺少物理地址”。提取报错 msg，让 LLM 将冲突的逻辑解释给用户，并要求其修改其中一项。 |

### **2.2 构建“校验 \- 失败 \- 追问”状态机环路**

【逻辑推断】在具体的工程实现层面，我们可以构建一个基于 TypeAdapter 或基础 BaseModel 的校验循环引擎。该引擎将作为需求建模系统的绝对守门员，其基本运转逻辑如下：  
首先，在 Schema 定义层，架构师使用 Field 严格定义下游程序需要的业务字段。对于绝对必需的槽位，坚决不设置默认值；对于有依存关系的字段，使用 @model\_validator(mode='after') 注入跨槽位约束逻辑。 其次，在判定引擎层，接收到 LLM 吐出的当前状态字典后，系统执行 model\_validate 尝试实例化对象。 最后，在反馈路由层，如果实例化成功，没有任何异常被抛出，这就构成了机械化判定中唯一且绝对的**停止条件（Stopping Condition）**，系统直接将结构化模型输出给下游。如果捕获到 ValidationError，代码层面的拦截器会遍历 error.errors()，收集所有的 missing 槽位和违背了业务逻辑的校验失败信息。这些结构化的错误数据随后被序列化为一段系统提示词，强制注入到 LLM 的下一个会话上下文中，要求大模型必须围绕这些确凿的缺陷继续向用户发问。  
【逻辑推断】为什么必须采用这种静态校验而非依靠 LLM 自主判定？因为基于 Pydantic 的方案提供了一层不可逾越的“类型结界”。只要有任何一个必填槽位的值不存在，或者类型逻辑相悖，这套判定引擎就会像无情的机器一样，一次次地把状态机的指针拨回“追问（Clarify）”节点。这种架构彻底消除了 LLM 的“幻觉”和“偷懒”空间，实现了 100% 的可控与收敛。

## **3\. 对话系统时代的槽位填充策略及其演进**

在 2018 至 2022 年间，在大型语言模型尚未普及的背景下，古典对话系统（如 Rasa、Dialogflow CX）在极其受限的自然语言理解（NLU）能力下，通过工程技巧深度解决过“复杂表单填槽”的问题。审视那一时代的架构遗产，对于今天构建基于大模型的需求追问机制，既有可以全盘复用的底层哲学，也有必须彻底抛弃的历史包袱。

### **3.1 经典做法与架构剖析**

【文献事实】在 Rasa 的生态中，解决多轮填槽问题的核心机制是 Forms。开发者在全局的 domain.yml 中显式定义 required\_slots（必填槽位列表）。一旦触发特定意图并激活 Form 表单，对话管理器（Dialogue Manager）便接管流程，循环执行内置逻辑，按顺序检查 required\_slots 中是否有为空的槽位。若发现缺失，系统会死板地调用与之对应的硬编码话术模板（如 utter\_ask\_\<slot\_name\>）向用户发起提问17。值得注意的是，Rasa 3.0 引入了破坏性更新，废弃了旧版表单映射中硬编码的 from\_entity 等抽取逻辑，强制将实体抽取与槽位映射的逻辑上浮到更全局的 YAML 定义中，这一举措从侧面反映了“定义槽位”与“提取数据”解耦的设计趋势19。  
【文献事实】相比之下，Google 的 Dialogflow CX 引入了更为现代和结构化的页面状态机（Page State Machine）架构。在 CX 的设计中，整个对话过程被建模为一棵页面流转树。每个页面关联一个用于收集参数的表单（Form），并具有一系列严格定义类型的必需参数（Required Parameters）22。Dialogflow CX 解决“何时算填完”的方法是底层暴露了一个不可篡改的系统变量。开发者可以在路由跳转条件中硬编码 $page.params.status \= "FINAL"。只要该页面对应的表单有任何一个必填参数未收集到，这个系统变量的状态就不会变成 FINAL，状态机就被锁死在当前页面，反复触发事件处理器（Event Handlers）进行追问；而一旦条件满足，底层引擎自动解绑并触发过渡（Transition），将收集到的参数包传递给下游5。

### **3.2 至今仍然成立的经典范式与被大模型淘汰的遗迹**

【逻辑推断】通过比对古典系统与当前大模型工作流，以下表格梳理了哪些策略至今依然是工程实施的基石，哪些已被时代彻底淘汰：

| 架构策略维度 | 古典对话系统做法（Rasa / Dialogflow CX） | 当前大模型时代的状态研判（有效性评价） |
| :---- | :---- | :---- |
| **状态机退出拦截** | Dialogflow CX 的 $page.params.status \= "FINAL" 路由阻断机制5。 | **【至今有效且最核心】** 这种数据收集与流程流转绝对解耦的黑盒状态机思想，正是今天使用 JSON Schema 校验是否 is\_final 的底层前身。必须在外部维持一个强状态对象，阻断未完成的需求流出。 |
| **异常处理与回退** | Reprompt Handlers（重试处理器），在用户连续输入无效内容达到 N 次后，触发失败降级策略5。 | **【至今有效】** 大模型很容易在遇到固执或表意不清的用户时陷入无限追问的死循环。系统必须引入类似于古典时代的外部计数器，设定最大追问轮次（如 5 次），超时则强制降级或标记为“需人工介入”。 |
| **槽位映射分离** | Rasa 3.0 强制将槽位映射规则从表单逻辑中剥离到全局 Domain20。 | **【至今有效】** 启示我们不应该在发给 LLM 的每一次 Prompt 中动态拼接复杂的 Schema 约束，而应在外部维护一个静态且版本化的全局配置源。 |
| **槽位提取方式** | 强依赖命名实体识别（NER）模型的 from\_entity 绑定机制17。 | **【已被彻底淘汰】** 过去必须要求 NLU 识别出特定边界的实体才能赋值。现在的 LLM 具有强大的零样本语义泛化与归一化能力，可以直接将散落的自然语言意图转换为结构化 JSON 赋值，实体映射逻辑已是包袱。 |
| **追问的话术生成** | 线性按序遍历空槽，调用硬编码的 utter\_ask\_\<slot\_name\> 模板17。 | **【已被彻底淘汰】** 机器式的逐个逼问极其僵化。LLM 能够在单次对话中，利用高度情境化的自然语言，一次性优雅地追问多个互相关联的缺失槽位。 |

## **4\. ReqElicitBench / ReqElicitGym 的底层基础设施与借用策略**

ReqElicitGym 是由北京大学等机构于 2026 年初提出的自动化评估环境，专门针对大型语言模型在“对话式需求启发（Conversational Requirements Elicitation）”领域的面试与追问能力进行基准测试。深入解析其基础设施，对于我们构建和验证第一版的“需求追问机制”具有极高的借鉴价值。

### **4.1 评测依赖的三大核心基础设施**

【文献事实】根据预印本论文 2602.18306 的架构设计，运行该基准测试强依赖以下三大基础设施组件的协同运作1：

> 1. **高度结构化的评测数据集（Evaluation Dataset）**：该数据集包含了 101 个真实的 Web 应用开发场景，跨越 10 个不同的领域。其核心设计哲学在于精确量化“需求缺口”。每一条数据样本都包含三个核心组件：一段粗略的“初始需求（Initial Req）”、一份完整的“最终需求（Final Req）”，以及介于两者之间、必须通过系统有效追问才能发掘出来的“隐性需求集合（Implicit Req）”1。  
> 2. **模拟甲方客户（Interactive Oracle User）**：由于引入真人进行大规模评测成本高昂且难以复现，该基准依赖强大的 LLM（原文使用了 GPT-5.1，辅以极度受控的系统提示词）来扮演现实中的利益相关者。这个模拟用户拥有“上帝视角”，其内部知识库锚定于那份“隐性需求集合（Implicit Req）”。只有当受测引擎提出了准确切中要害的追问时，该 Oracle User 才会遵循原则“透露”相应的信息，从而实现自动化、可重复的交互1。  
> 3. **回合感知任务评测器（Task Evaluator）**：这是一个基于“LLM-as-a-Judge”机制的裁判系统。它并不只是在对话结束时算一个总分，而是持续追踪多轮对话的进度。在每一轮（Turn-level）交互结束后，它都会判定受测引擎是否成功揭示了某一条具体的隐性需求。论文指出，该评测器在隐性需求发掘判定上与人类专家判断的 Cohen's \\kappa 一致性得分高达 0.72，具备了替代人工判卷的信度1。

### **4.2 基准测试暴露的 LLM 严重短板（防坑预警）**

【文献事实】在评估当前业界领先的模型时，ReqElicitGym 暴露出了大模型在需求追问领域一些非常棘手的原生缺陷。如果不关注这些失败点，我们的系统设计极易陷入相同的泥潭1：

* **总体发掘效率极低**：即便是表现最好的模型，其“隐性需求发掘率（Implicit Requirement Elicitation Rate, IRE）”也仅为 0.32。这意味着高达 68% 的深层业务约束根本无法被大模型自主问出，这直接印证了 LLM 存在极强的“提前满足感”，容易在只获取了表面信息时就草草宣告任务结束2。  
* **特定维度需求探测全面失效**：研究指出，LLM 可以相对容易地追问出诸如“交互逻辑（Interaction）”和“内容呈现（Content）”类的隐性需求，但在面对“风格偏好（Style-related）”这类需求时，其追问成功率几乎降至冰点2。  
* **过度依赖泛泛试探（Probing Bias）**：统计发现，模型在提问时极大地倾向于使用广泛的探测性发问（Probing），而非针对已有信息的结构化澄清（Clarification），这导致有效策略发问比例（ESR）持续偏低，对话冗长且低效2。

【逻辑推断】这些失败数据再次强力佐证了第二章的结论：绝不能让 LLM 自由发散地进行需求追问，必须引入外部的机械式状态机与 Schema 约束。特别是针对“风格偏好”这种 LLM 的盲区，必须在 Schema 中硬性规定相关的枚举字段，通过 ValidationError 强行逼迫 LLM 对其发问。

### **4.3 低成本借用评测维度的实施策略**

【逻辑推断】如果只是为了验证内部开发的第一版“需求追问机制”，无需耗费巨资部署完整的 Oracle User 和自动化环境，我们完全可以采用“降维解耦”的方式，仅借用其数据集与核心评价指标。  
具体操作层面，开发团队可以离线获取该基准数据集中的 101 个 \[Initial Req, Implicit Req\] 结构化对。在测试时，将 Initial Req 注入我们组装的追问引擎。在交互环节，由测试工程师取代算力昂贵的 Oracle User，根据预设的 Implicit Req 清单，人工扮演客户对系统的追问进行回应，直至系统触发自身的停止条件。  
最后，系统表现的好坏不再依赖模糊的主观评价，而是直接套用论文提出的两个严谨度量指标：首先计算最终生成的结构化建模涵盖了基准预设隐性需求的百分比（计算 IRE 覆盖率）；其次，统计系统在触发停止条件前总共发起了多少轮无效追问，以此计算回合级关键问题效率（TKQR）。这种“剥离借用”的策略，能够在不增加额外服务依赖与算力开销的前提下，科学地衡量新机制相比于大模型原生能力的工程增益。

#### **Works cited**

> 1. ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- arXiv, [https://arxiv.org/html/2602.18306v1](https://arxiv.org/html/2602.18306v1)  
> 2. ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- arXiv, [https://arxiv.org/pdf/2602.18306](https://arxiv.org/pdf/2602.18306)  
> 3. (PDF) ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- ResearchGate, [https://www.researchgate.net/publication/401058419\_ReqElicitGym\_An\_Evaluation\_Environment\_for\_Interview\_Competence\_in\_Conversational\_Requirements\_Elicitation](https://www.researchgate.net/publication/401058419_ReqElicitGym_An_Evaluation_Environment_for_Interview_Competence_in_Conversational_Requirements_Elicitation)  
> 4. Bug: /speckit.clarify 在spec 阶段将spec 级别条目错误defer 到plan · Issue \#1717 \- GitHub, [https://github.com/github/spec-kit/issues/1717](https://github.com/github/spec-kit/issues/1717)  
> 5. Parameters | Dialogflow CX \- Google Cloud Documentation, [https://docs.cloud.google.com/dialogflow/cx/docs/concept/parameter](https://docs.cloud.google.com/dialogflow/cx/docs/concept/parameter)  
> 6. Build an agent using flows | Dialogflow CX \- Google Cloud Documentation, [https://docs.cloud.google.com/dialogflow/cx/docs/quick/build-agent](https://docs.cloud.google.com/dialogflow/cx/docs/quick/build-agent)  
> 7. Boxcars/.agents/skills/speckit-clarify/SKILL.md at main · tomlm/Boxcars · GitHub, [https://github.com/tomlm/Boxcars/blob/main/.agents/skills/speckit-clarify/SKILL.md](https://github.com/tomlm/Boxcars/blob/main/.agents/skills/speckit-clarify/SKILL.md)  
> 8. spec-kit-clarify \- LobeHub, [https://lobehub.com/skills/neversight-learn-skills.dev-spec-kit-clarify](https://lobehub.com/skills/neversight-learn-skills.dev-spec-kit-clarify)  
> 9. Use Claude Code's native AskUserQuestion tool instead of numbered-option prompts · Issue \#2181 · github/spec-kit, [https://github.com/github/spec-kit/issues/2181](https://github.com/github/spec-kit/issues/2181)  
> 10. GitHub Spec Kit \- Peter Miľovčík \- Obsidian Publish, [https://publish.obsidian.md/petermilovcik/1+Notes/GitHub+Spec+Kit](https://publish.obsidian.md/petermilovcik/1+Notes/GitHub+Spec+Kit)  
> 11. Add a specific prompt to make it easier to execute edits · Issue \#954 · github/spec-kit, [https://github.com/github/spec-kit/issues/954](https://github.com/github/spec-kit/issues/954)  
> 12. Anyone tried GitHub's Spec-Kit with Claude Code? : r/ClaudeCode \- Reddit, [https://www.reddit.com/r/ClaudeCode/comments/1nb8mi9/anyone\_tried\_githubs\_speckit\_with\_claude\_code/](https://www.reddit.com/r/ClaudeCode/comments/1nb8mi9/anyone_tried_githubs_speckit_with_claude_code/)  
> 13. Validation Errors | Pydantic Docs, [https://pydantic.dev/docs/validation/dev/errors/validation\_errors/](https://pydantic.dev/docs/validation/dev/errors/validation_errors/)  
> 14. Errors | Pydantic Docs, [https://pydantic.dev/docs/validation/2.0/errors/errors/](https://pydantic.dev/docs/validation/2.0/errors/errors/)  
> 15. Error Handling | Pydantic Docs, [https://pydantic.dev/docs/validation/latest/errors/errors/](https://pydantic.dev/docs/validation/latest/errors/errors/)  
> 16. Custom Validators | Pydantic Docs, [https://pydantic.dev/docs/validation/dev/examples/custom\_validators/](https://pydantic.dev/docs/validation/dev/examples/custom_validators/)  
> 17. Creando un chatbot con Rasa \- Adictos al trabajo, [https://adictosaltrabajo.com/2024/09/23/creando-un-chatbot-con-rasa/](https://adictosaltrabajo.com/2024/09/23/creando-un-chatbot-con-rasa/)  
> 18. In Rasa 3.6.2, The slot values are not filling properly, [https://forum.rasa.com/t/in-rasa-3-6-2-the-slot-values-are-not-filling-properly/61508](https://forum.rasa.com/t/in-rasa-3-6-2-the-slot-values-are-not-filling-properly/61508)  
> 19. Rasa Pro Change Log | Rasa Documentation, [https://rasa.com/docs/reference/changelogs/rasa-pro-changelog/](https://rasa.com/docs/reference/changelogs/rasa-pro-changelog/)  
> 20. Rasa Open Source Change Log, [https://legacy-docs-oss.rasa.com/docs/rasa/2.x/changelog/](https://legacy-docs-oss.rasa.com/docs/rasa/2.x/changelog/)  
> 21. RasaHQ/rasa 3.0.0 on GitHub \- NewReleases.io, [https://newreleases.io/project/github/RasaHQ/rasa/release/3.0.0](https://newreleases.io/project/github/RasaHQ/rasa/release/3.0.0)  
> 22. google\_dialogflow\_cx\_page | Resources | hashicorp/google \- Terraform Registry, [https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/dialogflow\_cx\_page](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/dialogflow_cx_page)  
> 23. Dialogflow CX: Build a retail virtual agent \- Google Codelabs, [https://codelabs.developers.google.com/codelabs/dialogflow-cx-retail-agent](https://codelabs.developers.google.com/codelabs/dialogflow-cx-retail-agent)  
> 24. State handlers | Dialogflow CX \- Google Cloud Documentation, [https://docs.cloud.google.com/dialogflow/cx/docs/concept/handler](https://docs.cloud.google.com/dialogflow/cx/docs/concept/handler)  
> 25. \[2602.18306\] ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- arXiv, [https://arxiv.org/abs/2602.18306](https://arxiv.org/abs/2602.18306)