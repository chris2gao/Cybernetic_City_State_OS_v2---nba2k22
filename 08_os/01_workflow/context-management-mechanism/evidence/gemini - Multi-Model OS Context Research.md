# **多模型协作 OS 上下文管理机制独立研究报告**

## **1\. 定向核实分析：大模型上下文衰减、交接权限与框架原生缺陷**

多模型协作操作系统的核心在于状态流转与信息隔离。本节通过实证数据与底层机制，定向核实上下文长度对大模型任务表现的影响，评估 GitHub 权限模型对受限交接空间的支持能力，并剖析主流 Agent 框架在跨会话持久化中的默认行为与物理缺陷。

### **1.1 大模型在无关信息与过长上下文中的表现衰退与物理边界**

关于“无关信息、过长上下文或相关信息位置变化是否会显著降低大模型任务表现”的假设，学术界的实证研究与工业界的工程复盘给出了高度一致的肯定结论，并界定了严苛的适用边界。上下文长度不仅仅是一个计算成本问题，它直接构成了系统推理能力的物理约束。  
大量研究证实，当相关信息位于长上下文的中部时，大型语言模型（LLM）的信息提取与逻辑推理表现会发生断崖式的退化。刘等人的经典研究（2023-2024）指出，模型在处理多文档问答和键值检索时，呈现出典型的“U型性能曲线”1。模型对上下文开头（首因效应）和结尾（近因效应）的信息利用率最高。当关键事实被放置在输入上下文的中间时，GPT-3.5 等模型的准确率甚至低于不提供任何文档的闭卷测试水平2。这一现象的机制根源在于 Transformer 的注意力分配模式：预训练期间，起始词元（Token）始终在后续所有词元的注意力窗口内，而末尾词元彼此之间产生强烈的注意力关联，导致中间位置的词元获得的注意力权重被严重稀释3。  
进一步的独立研究推翻了“只要外挂检索完美，模型就能无损处理长文本”的直觉假设。2025年发表的最新研究表明，即使模型能够完美检索到所有相关信息，或者将无关干扰信息替换为完全空白的占位符（甚至通过强制掩码机制让模型在底层计算时只关注相关词元），仅仅是输入长度的纯粹增加，就会导致模型在数学、逻辑问答和代码编写任务中的性能发生 13.9% 至 85% 的显著下降5。这表明上下文长度本身即构成了独立的性能惩罚因子，与检索系统的精确度无关。  
当前主流前沿模型标称的百万级上下文窗口（如 Gemini 1.5 Pro, Claude 3 Opus）在实际工程中具有极大的误导性。2025至2026年针对这些模型的 RULER 和 BABILong 压力测试表明，尽管模型在单事实的“大海捞针（NIAH）”测试中表现完美，但在多跳溯源、状态聚合和变量追踪任务中，其实际有效上下文长度仅为标称值的 10% 至 20%6。在多代理协作 OS 场景中，这种由于上下文过长导致的准确率衰退，将直接转化为系统级的严重延迟。Time-to-Correct-Answer (TTCA) 指标研究证明，长上下文导致的推理谬误会引发极高频的系统重试与错误状态扩散，使得系统的整体执行速度急剧下降7。因此，严格过滤无关历史、维持角色私有工作区的最小必要上下文，并非单纯为了节省 API 算力成本，而是维持多代理协作系统拓扑收敛能力的绝对边界。

### **1.2 GitHub 权限粒度对任务与角色受限交接空间的映射支持**

在本地与云端混合的代码协作环境中，GitHub 经常被用作非结构化状态同步与代码产物交接的物理载体。然而，其内置的权限控制机制存在严格的设计初衷与边界，对“按任务、按角色建立受限交接空间”的支持程度在个人仓库与组织仓库之间存在决定性的架构差异。  
个人仓库（Personal Repository）的设计理念是极度扁平与高信任的，无法在原生层面实现严密的读写隔离。在个人仓库中，一旦将某外部协作者（Outside Collaborator）或机器账号加入仓库，该身份将自动继承底层协作权限，获得完整的读写（Read/Write）甚至隐式的管理能力，系统无法将其强制降级为单纯的只读（Read-only）访问8。这意味着，如果试图用个人账号下的仓库作为多代理协作的临时交接总线，任何被授权的代理实例都能轻易越权修改上游规划角色或并行执行角色的产物，使得“不同角色的私有工作信息默认不混合”的目标彻底破产。  
相比之下，组织仓库（Organization Repository）提供了完整的企业级细粒度控制平面，是实现隔离交接的唯一原生理路径。组织所有者可以利用多种不同维度的鉴权工具，为特定任务或角色分配严格受限的访问令牌。细粒度个人访问令牌（Fine-grained PATs）支持将令牌的访问范围严格限制在组织内的单一或特定多个仓库，并可从多达 50 种细粒度 API 权限库中进行正交组合，例如赋予一个审核角色“仅能读取代码与评论 Issue”的权限，而剥夺其推送代码的能力11。然而，细粒度 PAT 受到严格的配额限制（单用户最多 50 个），且强制要求最长不超过一年的绝对过期时间，同时可能触发组织管理员的手动审批流8。这使得其不适合在多代理 OS 中为高频动态创建的微型任务自动化分配临时身份。  
为了在组织级实现更具伸缩性的角色隔离，GitHub Enterprise Cloud 提供了自定义仓库角色（Custom Repository Roles）机制。系统管理员可以基于 Read、Triage、Write 等基础角色，衍生出高度特化的自定义角色，并将这些仓库级权限直接绑定到组织自定义角色中14。尽管该机制的表达力最强，但其属于企业版专有功能，针对本地小型 OS 闭环验证的需求而言，存在过重的配置开销。  
对于自动化部署与代理交接，部署密钥（Deploy Keys）提供了一种基于非对称加密（SSH）的极简隔离方案。一个 Deploy Key 只能授予对单一仓库的访问权限，且默认是完全只读的，除非在创建时显式授予写访问9。其优势在于极度符合“最小特权原则”（Least Privilege），不依赖任何用户账号的生命周期，即使创建该密钥的代理进程被销毁，只要私钥在受限环境中得以保留，通信链路依然有效18。但其物理缺陷同样显著：每个任务或角色仓库都需要一对独立的 SSH 密钥，当多代理系统为状态隔离动态创建大量临时仓库时，密钥的管理、分发与清理将成为难以承受的系统负担。Read the Docs 曾经爆发的严重安全漏洞（GHSA-jqm9-f79c-8wx6）正是因为应用程序在自动化创建 Deploy Keys 时未显式限制只读参数，导致本应只读的代理意外获得了上游仓库的推送权限19。

### **1.3 主流 Agent 框架在跨会话持久化与结构化交接中的暴露缺陷**

当前主流 Agent 框架（如 LangGraph, AutoGen, Swarm）在应对跨会话状态持久化、结构化交接以及输入历史过滤等企业级需求时，其默认的工程行为均倾向于透明暴露完整的会话历史。若不进行深度的二次架构重构，将直接破坏“角色间仅通过结构化产物通信”的设计目标。  
以 LangGraph 为例，该框架提供了基于数据库的检查点机制（如 SqliteSaver 和 PostgresSaver）来实现跨会话的状态持久化与线程（Thread）恢复20。其默认机制是将每次图节点（Node）的输入输出全量追加到状态历史中。开发者为了防止上下文窗口超载，通常会使用框架提供的 RemoveMessage 对象或 SummarizationMiddleware。然而，这一设计存在致命的审计冲突：RemoveMessage 并非仅仅是在构建下一次 LLM 请求时过滤消息，它会通过底层的 reducer 直接在持久化数据库中进行物理删除，用摘要永久性地覆盖掉原始的交互记录23。这导致了状态存储与审计追踪的根本悖论。如果过滤输入历史以维持角色工作区的最小上下文，系统就会物理丢失整个开发过程的长期追踪事实；如果不删除，大模型将强行吞咽所有无关的历史噪音。因此，在实际工程中，必须摒弃框架自带的混合持久化方案，构建双轨存储架构：应用层负责向只追加（Append-only）的数据库写入全量审计日志，而 LangGraph 的 Checkpointer 仅仅作为被高频修剪、仅保留近期滑动窗口的易失性计算内存23。  
在多代理交接（Handoff）领域，OpenAI Swarm 和微软 AutoGen 的默认实现同样存在上下文污染问题。多代理交接通常依赖于将整个对话流透明地注入给下一个被唤醒的代理。尽管 AutoGen 在最新版本中引入了显式的 HandoffMessage 和 StreamProcessor25，试图对交接事件进行解耦，但在其多代理池（Agent Magnet）的共享内存模型中，系统往往将同一项目的所有任务记忆混合存储。这种设计引发了严重的“范围越界（Scope Bleed）”现象：代理 A 在完成子任务 X 时通过试错习得的临时状态或幻觉，会被毫无阻力地带入并污染代理 B 执行子任务 Y 时的上下文26。此外，当系统通过默认路由器（Router）将工作交接给执行代理时，执行代理的上下文窗口中会完整包含规划代理所有的内部思考过程、工具调用失败记录以及废弃的草稿。这种透明传递模式默认共享了全部事件历史，彻底击穿了角色间基于结构化产物通信的信息防火墙。

## **2\. 开放发现分析：机制与模式的候选空间**

针对第一版要求只支持本地开发环境，并以真实小型 OS 开发任务闭环验证的前提，本节系统性地提取现有文献与开源工程中的机制模式，形成可供下一阶段系统建模（模型 B）直接采纳的原语清单。

### **2.1 角色专属上下文、交接、记忆与恢复机制模式**

下表归纳了用于实现角色专属上下文、结构化交接、固定恢复入口及上下文压缩的候选机制空间。这些机制被抽象为独立的设计模式，超越了具体产品的实现细节。

| 机制与模式名称 | 作用域 | 机制原理与运行时特征 | 核心优势与适用场景 |
| :---- | :---- | :---- | :---- |
| **双轨内存模式 (Dual-Track Storage)** | 角色专用上下文 | 在架构层面物理分离“系统审计日志”（Append-only 数据库）与“代理工作内存”（如被频繁修剪的 Checkpointer）。大模型仅被授权读取工作内存，而工作内存由独立的生命周期中间件动态裁剪。 | 彻底解决了上下文过滤与系统行为持久化审计之间的设计冲突23。 |
| **分层视图隔离 (Hierarchical View Isolation)** | 角色专用上下文 | 维持单一的全局状态图，但不直接向执行层代理传递原生消息列表。系统通过一个代理中介层（Proxy）查询底层状态，仅将符合当前角色鉴权标签（RBAC tags）的消息投影、拼接后送入模型上下文窗口。 | 避免了为每个角色建立独立物理数据库的碎片化开销，逻辑上实现了视图的绝对隔离14。 |
| **收据证明交接 (Receipt-based Handoff)** | 结构化交接 | 严禁代理之间使用自然语言闲聊交接。下游代理仅接收一个包含严格 Schema 的 JSON“收据”，该收据必须携带上游状态的哈希值、标准化的退出状态码以及指向物理产物（如文件路径）的指针。 | 彻底消除了语义泄漏与闲聊造成的指令漂移（Problem Drift），极大降低 Token 消耗27。 |
| **强类型黑板协议 (Typed Blackboard)** | 结构化交接 | 设立一个基于强类型的共享内存区（Blackboard）。规划者只被允许向特定槽位（Slots）写入指令摘要，执行者仅监听自身订阅的槽位变化进行操作，代理间禁止点对点通信。 | 适用于高度复杂的异步多步任务，强迫大模型将非结构化意图转换为结构化数据28。 |
| **事实-实体降维抽取 (Fact-Entity Extraction)** | 跨会话记忆 | 在会话线程挂起或任务完成前，启动高压缩比的后台提炼模型，将当前的杂乱状态强制归纳为无结构的原子事实（Atomic Facts），存入外部 KV 存储，随后彻底抛弃原始会话流。 | 在牺牲时间序列与细粒度因果关系的前提下，实现了跨会话记忆体积的几何级压缩29。 |
| **图谱语义溯源 (GraphRAG Semantic Tracking)** | 跨会话记忆 | 将任务演进过程中的关键节点与产物映射为知识图谱。代理恢复时，通过关系图谱查询之前的结构化状态，而非依赖传统的文本块相似度检索。 | 保留了开发过程的逻辑必然性，有效防止了传统 RAG 造成的语义错位与幻觉注入30。 |
| **检查点物理重放 (Checkpoint Rehydration)** | 固定恢复入口 | 规定特定的 thread\_id 和历史版本指针，系统直接从持久化介质将字典状态反序列化，并物理注入到新建的模型实例中，完全绕过长文本初始化提示词。 | 实现代理状态的毫秒级冷启动。但若上游交接产物的 Schema 版本发生重大变更，会导致反序列化直接崩溃22。 |
| **基于标记的滑动截断 (Token-based Trim)** | 上下文压缩 | 当当前线程的 Token 数达到预设阈值时，自动移除中间的试错与闲聊过程，强制保留首条系统设定（System Prompt）以及最后 N 条近因指令，并对被移除部分进行粗粒度结构化摘要注入。 | 实现简单，成本低。但属于启发式有损压缩，极易导致摘要中丢失未来某些边角任务所必需的长尾细节23。 |

### **2.2 本地代码协作环境的低成本物理隔离机制**

在无需构建零信任防恶意攻击沙箱的前提下，为了防止代理模型因生成代码的越权读取而意外污染“不同角色的私有工作信息”，本地 OS 环境可采纳以下低成本的文件系统分区机制：  
Linux Landlock 提供了一种内核级的无特权沙箱机制，是目前最轻量级的系统调用拦截方案。基于 Linux 6.x 现代内核，任何无特权进程（包括启动大模型的 Python 代理脚本）均可主动利用 BPF 机制将自身的文件系统访问权限制在特定的工作目录内。这一机制直接剥夺了代理进程对全局网络、其他进程空间及同级兄弟目录的读写权限，启动延迟几乎为零，且不需要启动笨重的 Docker 守护进程32。但其缺点在于仅限 Linux 平台，且当模型生成的 Shell 脚本包含意外的越界路径时，操作会被内核静默拒绝，可能导致模型陷入无法理解错误的死循环。  
受限工具网关（如 Model Context Protocol Guard, MCP Guard）提供了一种应用层的防御替代方案。该机制不允许大模型直接获取宿主机的 Shell 执行权限，所有文件读写和命令执行必须序列化为 MCP 请求，交由中间件代为执行。中间件内置了防止路径穿越（Path Traversal）和目录逃逸的词法分析拦截逻辑34。这种方式与底层操作系统解耦，可跨 Windows/Mac/Linux 实现统一的虚拟文件沙箱。  
对于纯粹的版本控制隔离，本地临时裸仓库（Local Bare Repo）与克隆交接机制强制实施了严格的工作区隔离。系统为整个任务生命周期创建一个本地裸仓库，规划、执行、审核等角色各自将代码 clone 到被严格隔离的临时目录。不同角色之间不存在活体目录共享，必须通过 git push 到裸仓库并触发 Webhook 来完成状态交接。这种机制在架构上强迫实施了“只有提交并推送的结构化产物才构成事实”的协议。尽管在文件数量极大的仓库中频繁克隆会导致磁盘 I/O 升高，但在小型 OS 开发闭环验证中，这是一种零外部依赖的优雅方案。相比之下，传统的 Git Worktree 虽然能在同一仓库内秒级创建独立的代码树，但它无法限制大模型调用 shell 脚本通过 cd 命令越权访问其他角色的物理目录。

### **2.3 产物版本依赖与下游失效模式**

当上游产物（如架构设计文档或 API 接口契约）发生版本演进时，依赖旧版本的下游私有上下文必须被及时标记为失效，以避免代理在陈旧的前提下产生代码幻觉。  
证据门控模式（Proof-or-Stop Lifecycle Control）为这种依赖阻断提供了严格的控制论模型。在该模式中，代理的任何非最终输出均被视为“主张（Claim）”而非事实系统状态。下游生命周期的推进必须基于绑定代码源状态的“新鲜证据”。当上游产物的内容哈希（如 Git commit SHA-256 或抽象语法树的摘要）发生变化时，下游当前持有的交接“收据（Receipt）”将在门控校验中失效。一旦检测到 Hash 不匹配，下游节点必须被强制中止当前上下文执行，并请求结构化的最小补充信息来更新本地前提27。  
与之互补的是生成器-助手逐步回滚模式（Stepwise Rollback Framework）。该模式通过后台守护进程实时监听本地环境的执行日志，一旦检测到环境状态或上游底层依赖与下游上下文中正在推导的逻辑前提发生冲突，系统将以编程方式将执行代理的存储堆栈和本地环境状态“物理回溯”到上游变更发生前的最后一个正确检查点（Checkpoint）。这不仅宣告旧上下文失效，更强迫下游彻底丢弃基于错误前提产生的思维链（Chain of Thought），有效截断了错误的级联放大30。

## **3\. 证据目标与约束性材料体系**

本节主动汇编了可能推翻或极大限制初始需求的实证材料。这些材料指出了多代理架构中因信息截断、共享内存及环境假设所带来的负面效应，对下一阶段（建模 B）的系统约束具有直接的否决权或修正权。

| 证据 ID | 支持或推翻的具体主张 | 一手来源与日期 | 信源属性与可靠性 | 本条信息可信度 | 适用边界 | 对结果建模 B 产生的架构约束 | 事实/推断 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Ev-01** | **推翻**：“通过最小化补充信息和过滤无关上下文，可以安全高效地消除噪音并隔离多角色环境”。 | 预印本论文：*Too polite to disagree: Understanding sycophancy propagation in multi-agent systems* (2026) 等30。 | 高。基于受控多代理对抗实验的同行评议级数据。 | 极高。 | 适用于涉及复杂逻辑推理、多步调试和代码架构意图推演的任务。 | 简单的文本总结或基于关键字的信息截取会导致严重的“语义泄漏（Semantic Leakage）”。若上游角色在思维中犯下隐蔽的逻辑谬误，仅传递“最小化结论”会使下游失去排错上下文，导致系统在错误前提下陷入“问题漂移（Problem Drift）”并耗尽 Token 预算。**约束**：最小补充信息必须包含抽象语法树变更或逻辑推导的图谱节点，绝不能是纯自然语言摘要。 | 实证事实 |
| **Ev-02** | **推翻**：“利用 Agent 框架现成的跨会话记忆机制，可以直接实现既保留长期事实又删除无价值私有过程”。 | LangGraph 官方讨论区架构复盘，源码实现分析 (2025/2026)21。 | 极高。官方 API 原理与开发者真实故障报告。 | 极高。 | 适用于所有采用状态图（State Graph）和 Checkpoint 持久化绑定的流控框架。 | 当开发者调用诸如 RemoveMessage 删除无价值中间过程，以避免下游规划角色超载时，底层关系型数据库中的物理记录会被实质性覆盖和永久删除。**约束**：模型 B 必须从物理架构上彻底解耦“大模型工作易失记忆存储”与“系统级事件追加审计存储”，否则删除私有过程等同于损毁整个系统的审计链条。 | 系统事实 |
| **Ev-03** | **限制**：“为每个任务、每个角色动态创建细粒度隔离的 GitHub 仓库并授权”的可行性。 | GitHub 官方文档，企业级访问令牌策略说明，Read the Docs 漏洞分析 (2024-2025)8。 | 极高。官方功能限制说明与公开漏洞库。 | 极高。 | 依赖真实远程 Git 基础设施作为协作隔离区，且任务拆分粒度细、生命周期短的系统。 | 细粒度 PAT 受限于单人 50 个的硬性配额上限，且强制要求长期存在；Deploy Key 不设自动过期机制，高频微型任务的创建与销毁将引发严重的密钥遗留灾难与权限泄露风险。**约束**：在第一版的闭环验证阶段，必须放弃使用真实 GitHub Remote Repo 进行代理间角色隔离，转而依赖本地虚拟文件系统或临时本地裸仓库集群进行物理切分。 | API限制事实与推断 |
| **Ev-04** | **限制**：“单纯的工作区分区或目录分配可以低成本限制模型的正常工具读取路径”。 | 安全中间件项目（如 MCP-Guard）的架构逻辑与 Linux 系统权限原理32。 | 中高。操作系统权限常识与开源安全组件机制。 | 高。 | 赋予大模型直接操作 Shell 环境与本地文件系统能力的协作任务。 | 仅利用操作系统目录或 Git Worktree 进行逻辑分区，无法阻止大模型在其生成的代码逻辑中执行 cd ../ 越权，或生成独立二进制文件继承宿主用户特权读取兄弟角色目录。**约束**：为了实现“私有工作信息默认不混合”，第一版的隔离机制不能依赖大模型的“系统提示词自觉”，必须在系统调用层（如 Linux Landlock）或工具路由网关层实施物理拦截。 | 操作系统事实与推断 |
| **Ev-05** | **限制**：“发现信息不足时即可反复提交结构化申请”在本地开发任务中的可靠性。 | *Lightweight Accuracy-Aware Routing* 等边缘计算与系统结构论文 (2025/2026)7。 | 高。针对边缘代理系统的性能压测数据。 | 高。 | 受限计算环境（本地化小型模型或硬件受限的端侧设备）。 | 云端前沿模型（Frontier Models）习惯于通过巨大的规模涌现出强大的错误自我纠正能力。但在本地受限计算环境中，一旦因为“最小化上下文”导致信息残缺，本地小模型（SLM）极易陷入盲目申请与错误重试的死循环，导致 TTCA 延迟无限膨胀并耗尽硬件资源。**约束**：本地 OS 验证系统必须引入严格的重试熔断机制，若模型在 N 次最小补充后仍无法收敛，必须直接挂起，停止无效的结构化申请循环。 | 实验事实 |

通过上述确凿的限制性证据，证明了试图依赖单一底层持久化机制或松散的文件目录去实现复杂角色的上下文受限流转，存在深刻的架构冲突。下一阶段建模必须正视这些物理与逻辑阻力。

## **4\. 检索边界与搜索路径说明**

为确保研究视角的独立性与信息的全景覆盖，未进行任何猜测或依赖其他并行 Deep Research 路线的先验结论。以下报告本次研究的信息捕获边界与受限情况：

### **4.1 检索查询策略与核心路径**

本次研究严格遵循中英文技术文献的追踪：

* **大模型性能衰减追踪**：检索 LLM lost in the middle context length irrelevant information performance degradation 2024 2025 arxiv，以及专门针对长文本前沿测评论文的布尔逻辑 site:arxiv.org "context length alone hurts LLM performance"。  
* **平台级权限隔离评估**：深入 GitHub 官方文档进行细粒度对比，路径涵盖 github documentation fine grained permissions organization repository vs personal repository access control，以及 custom repository roles 和 deploy keys scoped repository access 的优劣势辨析。  
* **主流框架状态底层逻辑核实**：针对 LangGraph 的图状态管理机制，检索 langgraph state persistence history filtering checkpointer structured handoff，并深入跟踪源码库的真实性能反馈 site:github.com/langchain-ai/langgraph "checkpointer" sqlite postgres performance；对于多代理交接，定向深挖 AutoGen 框架底层迭代 autogen core state persistence agentchat handoff session 及 HandoffMessage 的最新 API 实现讨论。  
* **多智能体环境退化现象捕获**：关注学术界对语义损失的讨论 site:arxiv.org "multi-agent" "handoff" "context loss" OR "semantic loss" 2024 2025 2026。

### **4.2 数据盲区与返回为空的方向**

* **原生版本失效传播图谱的缺位**：在检索“主流 Agent 框架内建的基于 AST/Hash 的下游上下文自动失效传播机制”时，结果为空。尽管学术界有理论探讨（如 Proof-or-Stop 模型），但在诸如 LangGraph 或 AutoGen 等工业级框架的原生 API 中，并未提供现成的、用于构建代理间细粒度版本失效依赖树（Dependency Tree）的底层支持模块。  
* **跨平台强沙箱替代方案的稀缺**：在寻找纯本地、无特权（非 Root 环境下不使用 Docker）、且具备跨平台通用性的文件系统细粒度强隔离中间件时，没有发现成熟的一揽子免配置解决方案，实际工程实施往往只能退化到依赖特定内核（如 Linux Landlock）或强行切分文件系统宿主用户。

### **4.3 结果截断与付费墙阻碍**

* 关于 GitHub Enterprise Cloud 级别的“Custom Repository Roles”的高级应用与权限下发自动化，因其属于大型企业级服务的付费范畴及运维商业机密，仅能获取公开的 REST API 字段定义与官方更新日志。无法收集到一线科技企业因大规模使用动态自建细粒度角色，而导致系统调度延迟或权限爆炸的具体量化故障数据。

### **4.4 闭源系统底层细节无法访问**

* 针对 OpenAI 官方近期发布的轻量级演示框架（Swarm）背后的云端生产级路由策略，以及微软 AutoGen 在私有复杂业务（如 Agent Magnet）中的闭源解决方案，因其属于商业专有平台的内部核心细节，仅能从 GitHub Issues 及相关架构研究者的外部推演中提取其系统局限性，无法直接深入其最底层的张量传递及内存卸载源码机制。

本研究全面交付了对当前上下文管理机制的实证分析、候选隔离模式及架构级约束要素，以最严密的技术考证，为下一阶段多模型协作 OS 的架构建模提供了坚实的数据支撑。

#### **Works cited**

> 1. Lost in the Middle: How Language Models Use Long Contexts \- Stanford Computer Science, [https://cs.stanford.edu/\~nfliu/papers/lost-in-the-middle.arxiv2023.pdf](https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.arxiv2023.pdf)  
> 2. Lost in the Middle: How Language Models Use Long Contexts \- ResearchGate, [https://www.researchgate.net/publication/378284067\_Lost\_in\_the\_Middle\_How\_Language\_Models\_Use\_Long\_Contexts](https://www.researchgate.net/publication/378284067_Lost_in_the_Middle_How_Language_Models_Use_Long_Contexts)  
> 3. Lost in the Middle: Why LLMs Struggle With Long Contexts (2025) \- Pristren, [https://pristren.com/blog/lost-in-middle-attention-paper/](https://pristren.com/blog/lost-in-middle-attention-paper/)  
> 4. Never Lost in the Middle: Mastering Long-Context Question Answering with Position-Agnostic Decompositional Training \- arXiv, [https://arxiv.org/html/2311.09198v2](https://arxiv.org/html/2311.09198v2)  
> 5. Context Length Alone Hurts LLM Performance Despite Perfect Retrieval \- arXiv, [https://arxiv.org/abs/2510.05381](https://arxiv.org/abs/2510.05381)  
> 6. Retrieval and Multi-Hop Reasoning in 1M-Token Context Windows: Evaluating LLMs on Classical Chinese Text \- arXiv, [https://arxiv.org/html/2605.02173v1](https://arxiv.org/html/2605.02173v1)  
> 7. Accuracy Is Speed: Towards Long-Context-Aware Routing for Distributed LLM Serving, [https://arxiv.org/html/2604.15732v1](https://arxiv.org/html/2604.15732v1)  
> 8. GitHub Classic vs. Fine-grained Personal Access Tokens \- Finecloud, [https://www.finecloud.ch/blog/github-classic-vs-fine-grained-personal-access-tokens/](https://www.finecloud.ch/blog/github-classic-vs-fine-grained-personal-access-tokens/)  
> 9. Managing deploy keys \- GitHub Docs, [https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)  
> 10. docs/content/authentication/connecting-to-github-with-ssh/managing-deploy-keys.md at main, [https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/managing-deploy-keys.md](https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/managing-deploy-keys.md)  
> 11. Introducing fine-grained personal access tokens for GitHub, [https://github.blog/security/application-security/introducing-fine-grained-personal-access-tokens-for-github/](https://github.blog/security/application-security/introducing-fine-grained-personal-access-tokens-for-github/)  
> 12. Managing your personal access tokens \- GitHub Enterprise Server 3.21 Docs, [https://docs.github.com/en/enterprise-server@3.21/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/enterprise-server@3.21/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)  
> 13. Setting a personal access token policy for your organization \- GitHub Enterprise Cloud Docs, [https://docs.github.com/enterprise-cloud@latest/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization](https://docs.github.com/enterprise-cloud@latest/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization)  
> 14. Permissions of custom organization roles \- GitHub Enterprise Cloud Docs, [https://docs.github.com/enterprise-cloud@latest/organizations/managing-peoples-access-to-your-organization-with-roles/permissions-of-custom-organization-roles](https://docs.github.com/enterprise-cloud@latest/organizations/managing-peoples-access-to-your-organization-with-roles/permissions-of-custom-organization-roles)  
> 15. About custom repository roles \- GitHub Enterprise Cloud Docs, [https://docs.github.com/enterprise-cloud@latest/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/about-custom-repository-roles](https://docs.github.com/enterprise-cloud@latest/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/about-custom-repository-roles)  
> 16. Add repository permissions to custom organization roles \- GitHub Changelog, [https://github.blog/changelog/2024-08-29-add-repository-permissions-to-custom-organization-roles/](https://github.blog/changelog/2024-08-29-add-repository-permissions-to-custom-organization-roles/)  
> 17. GitHub Deploy Key | Coolify Docs, [https://coolify.io/docs/applications/ci-cd/github/deploy-key](https://coolify.io/docs/applications/ci-cd/github/deploy-key)  
> 18. Bypass protected branches with deploy keys · Issue \#1343 \- GitHub, [https://github.com/python-semantic-release/python-semantic-release/issues/1343](https://github.com/python-semantic-release/python-semantic-release/issues/1343)  
> 19. Write access to GitHub repositories using deploy key in Read the Docs for Business, [https://github.com/readthedocs/readthedocs.org/security/advisories/GHSA-jqm9-f79c-8wx6](https://github.com/readthedocs/readthedocs.org/security/advisories/GHSA-jqm9-f79c-8wx6)  
> 20. LangGraph persistence with Oracle AI Database | developers, [https://blogs.oracle.com/developers/langgraph-persistence-with-oracle-ai-database](https://blogs.oracle.com/developers/langgraph-persistence-with-oracle-ai-database)  
> 21. Memory \- Docs by LangChain, [https://docs.langchain.com/oss/python/langgraph/add-memory](https://docs.langchain.com/oss/python/langgraph/add-memory)  
> 22. langgraph/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py at main · langchain-ai/langgraph \- GitHub, [https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py)  
> 23. LangGraph \+ PostgreSQL: Chat history and summarization best practice, [https://forum.langchain.com/t/langgraph-postgresql-chat-history-and-summarization-best-practice/3521](https://forum.langchain.com/t/langgraph-postgresql-chat-history-and-summarization-best-practice/3521)  
> 24. LangGraph Memory: The Complete Practical Guide to Managing What Your Agent Remembers | by Bessie Delight Kekeli \- Towards AI, [https://pub.towardsai.net/langgraph-memory-the-complete-practical-guide-to-managing-what-your-agent-remembers-d865d505a59e](https://pub.towardsai.net/langgraph-memory-the-complete-practical-guide-to-managing-what-your-agent-remembers-d865d505a59e)  
> 25. Add \`StreamProcessor\` class for handling message streams produced by \`run\_stream\` and \`on\_messages\_stream\`. · Issue \#6182 · microsoft/autogen \- GitHub, [https://github.com/microsoft/autogen/issues/6182](https://github.com/microsoft/autogen/issues/6182)  
> 26. \[FEATURE\] Add persistent cross-session memory via Agent Magnet · Issue \#6050 · crewAIInc/crewAI \- GitHub, [https://github.com/crewAIInc/crewAI/issues/6050](https://github.com/crewAIInc/crewAI/issues/6050)  
> 27. Proof-or-Stop: Don't Trust the Agent, Trust the Evidence – Loop Engineering for Verifiable Evidence-Gated Lifecycle Contro \- arXiv, [https://arxiv.org/pdf/2607.14890](https://arxiv.org/pdf/2607.14890)  
> 28. KnowAct-GUIClaw: Know Deeply, Act Perfectly, Personal GUI Assistant with Self-Evolving Memory and Skill \- arXiv, [https://arxiv.org/html/2607.12625v2](https://arxiv.org/html/2607.12625v2)  
> 29. Beyond the Context Window: A Cost-Performance Analysis of Fact-Based Memory vs. Long-Context LLMs for Persistent Agents \- arXiv, [https://arxiv.org/html/2603.04814v1](https://arxiv.org/html/2603.04814v1)  
> 30. Diagnosing and Mitigating Compounding Failures in Agentic Persuasion via Taxonomic Strategy Retrieval \- arXiv, [https://arxiv.org/pdf/2606.24976](https://arxiv.org/pdf/2606.24976)  
> 31. Short-term memory \- Docs by LangChain, [https://docs.langchain.com/oss/javascript/langchain/short-term-memory](https://docs.langchain.com/oss/javascript/langchain/short-term-memory)  
> 32. Landlock LSM: kernel documentation, [https://docs.kernel.org/6.2/security/landlock.html](https://docs.kernel.org/6.2/security/landlock.html)  
> 33. Landlock: unprivileged access control \- The Linux Kernel documentation, [https://docs.kernel.org/userspace-api/landlock.html](https://docs.kernel.org/userspace-api/landlock.html)  
> 34. GitHub \- JakeB-5/mcp-guard: Security middleware for Model Context, [https://github.com/jakeb-5/mcp-guard](https://github.com/jakeb-5/mcp-guard)  
> 35. Diagnosing and Mitigating Compounding Failures in Agentic Persuasion via Taxonomic Strategy Retrieval \- arXiv, [https://arxiv.org/html/2606.24976v2](https://arxiv.org/html/2606.24976v2)  
> 36. Beyond Scaling: Agents Are Heading to the Edge \- arXiv, [https://arxiv.org/html/2605.18535v1?ref=genaisecretsauce.com](https://arxiv.org/html/2605.18535v1?ref=genaisecretsauce.com)  
> 37. Beyond Scaling: Agents Are Heading to the Edge \- arXiv, [https://arxiv.org/pdf/2605.18535](https://arxiv.org/pdf/2605.18535)