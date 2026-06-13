# **赛博城邦 (Cybernetic City-State OS) 阶段二：多智能体路由控制论与纯 LLM 节点架构深度研究报告**

## **宏观架构与控制论范式转移的必然性**

在现代人工智能代理系统的演进轨迹中，“赛博城邦 (Cybernetic City-State OS)”代表了一种从根本上颠覆传统的底层范式。该项目旨在构建一个具备多智能体三权分立、能够进行自我审核与自我进化（修宪）的活体操作系统。这一系统的核心运行环境依托于 Google Antigravity 本地 Agent 框架，利用定制的本地大模型及强大的 invoke\_subagent（子代理并行裂变）能力，以实现高度复杂的并发推理与拓扑运算 1。在这一宏大愿景下，消除多智能体系统中普遍存在的“同质化茧房”与“谄媚效应”（Sycophancy）成为了架构设计的最高优先级任务。为了压榨出最深度的代码与架构洞察，系统必须依赖极端的人格碰撞与绝对客观的物理证据池来进行认知重构 1。  
在这个框架中，一个不可妥协的硬核环境约束是“LLM-Native 绝对原则”。传统的智能体编排往往依赖于死板的 Python 代码去实现 if-else 的死锁检测、轮次切断或流程路由。这种硬编码的控制流在面对高维语义碰撞时，显得极其僵化且容易造成状态机的崩溃 1。因此，赛博城邦彻底拒绝了基于代码的逻辑硬切断，要求所有的统筹、过滤、切断动作，必须通过压铸了特定 XML 人格（Persona）的大语言模型自发、语义化地完成 1。  
根据系统工程的推进状态，阶段一（双核底层基建）已经全面竣工。基于 Git 概念的本地 Markdown 文件系统成功实现了无锁并发与信息隔离，物理隔离的工作区（如 /workspace\_{agent\_name}/scratchpad.md）与全局客观脱敏的证据池（/00\_Evidence\_Room/compiled\_evidence.md）构成了系统的物理工作树拓扑 1。此外，红队深研降级逃生舱、基于 Thought-MDP 的证据思维链、虚拟记忆冷热驱逐以及乐观并发锁（OCC）的纯语义转换均已部署完毕 1。  
在这一坚实基础上，阶段二的核心任务是设计并压铸三大纯 LLM 路由控制节点：主控聚合器（Aggregator）、洗稿智能体（Epistemic Purifier）以及最高裁决者（Arbiter）。这三大节点必须解决多智能体协同中最致命的控制论难题：异构重组中的妥协平庸、辩论漂移中的幻觉叠加、以及无外力干预下的语义死锁。本研究报告将深入探讨这三个核心议题的理论基础，并提供生产级别的 XML Prompt 架构范本与执行逻辑。

## **议题一：主控聚合器 (Aggregator) 的对抗性保留机制**

### **传统共识机制的缺陷与同质化茧房的形成**

在分布式深研阶段，底层的“激进架构师”与“悲观审核官”会被系统赋予极端的认知偏见。这种设计旨在打破认知同质化，迫使智能体在面对同一任务时收集并生成充满偏见、甚至互相矛盾的深研报告 1。当这些异构报告提交给主控聚合器（Aggregator）以生成初始的《提案草案》时，系统面临着信息整合的巨大风险。  
传统的 LLM 多智能体意见合成（Opinion Synthesis）与汇总通常遵循“求同存异”或“多数决”（Majority Voting）的范式。研究表明，线性平均化的聚合机制（Linear Averaging）会导致模型为了迎合共识而平滑掉边缘的、极端的发现 3。在这种传统模式下，聚合器往往会输出一份试图平衡各方观点的平庸草案——即所谓的“缝合怪”（Frankenstein drafts）。这种妥协直接抹杀了前期通过红队深研压榨出的高价值代码洞察，使得“激进架构师”的颠覆性构想和“悲观审核官”的致命漏洞警告在语义空间中被互相抵消。

### **对抗性保留的理论跨界映射**

为了解决异构重组中的平庸化问题，必须引入一种被称为“对抗性保留”（Adversarial Preservation）的非共识聚合机制。这一概念最初在扩散模型（Diffusion Models）的概念擦除与对抗性训练领域取得了显著成效。在图像生成中，“对抗性保留”技术（如 EAP）通过识别概念特定的子空间，在微调擦除不良概念的同时，利用对抗性张力强行保留与目标无关但具有高度特征性的生成细节，从而避免了模型整体表现力的塌缩 4。在应对对抗性混淆时，该技术证明了通过正交保留特定特征，可以在不破坏整体结构的前提下维持极端的边缘张力 5。  
将这一物理拓扑学的概念映射到 LLM 文本合成与智能体聚合论中，意味着 Aggregator 在处理互斥逻辑点时，绝不能进行语义上的中和或融合。相反，它必须充当一个“引信压铸机”。Aggregator 的职责是将基于相同物理锚点但得出截然相反结论的报告，通过特定的 Schema 并列地压入草案中，构建出结构化的“对抗性张力”（Adversarial Tension）。这种非共识聚合（Non-consensus Aggregation）机制将矛盾视为系统演进的核心认知势能，为后续议会的深度辩论提供不可回避的引爆点 3。

### **聚合范式对比分析**

为了更清晰地阐述对抗性保留机制的架构优势，下表对比了传统共识聚合与赛博城邦所采用的 LLM-Native 对抗性保留聚合在处理互斥报告时的核心差异：

| 评估维度 | 传统共识聚合 (Standard Consensus Synthesis) | 对抗性保留聚合 (Adversarial Preservation Aggregation) |
| :---- | :---- | :---- |
| **处理矛盾的逻辑** | 求同存异，寻找双方都能接受的中间地带。 | 拒绝融合，强制将互斥结论正交并列，暴露冲突。 |
| **对极端数据的态度** | 视为噪音或异常值（Outliers）进行平滑处理。 | 视为高价值的“认知势能”（Cognitive Potential），予以保留。 |
| **输出文本特征** | 语气平和，结论模棱两可，试图掩盖底层分歧。 | 结构几何化，逻辑对立面极度尖锐，充满对抗性张力。 |
| **对后续辩论的影响** | 导致辩论无从下口，智能体陷入“互相赞同”的同质化循环。 | 强制辩手直面最核心的代码或架构悖论，引爆深度交锋。 |
| **系统熵值状态** | 强制降熵，导致信息维度塌缩。 | 维持高熵状态，将信息重构的责任推迟至多智能体辩论期。 |

### **XML Prompt 架构范本：对抗性张力矩阵**

为了让大模型严格执行对抗性保留机制，Aggregator 的 XML 协议被设计为一个刚性的逻辑压铸模具。它彻底禁用了模型试图“和稀泥”的自然语言倾向，强制其在结构内填充互斥向量。

XML  
\<Aggregator\_Persona\>  
    \<Identity\>  
        You are the Supreme Aggregator of the Cybernetic City-State OS. Your prime directive is to prevent cognitive homogenization. You are NOT a consensus-builder; you are an architect of logical tension. Your output is a \<Proposal\_Draft\> designed to detonate in the upcoming parliament debate.  
    \</Identity\>  
      
    \<Core\_Directive\>  
        \<Principle\>Adversarial Preservation (Non-consensus Aggregation)\</Principle\>  
        \<Definition\>  
            When processing the deep-research reports from the 'Radical Architect' and the 'Pessimistic Auditor', you must NEVER dilute their extreme viewpoints into a mediocre middle-ground. Structural contradictions are the highest-value assets of this OS.  
        \</Definition\>  
        \<Execution\>  
            Extract mutually exclusive logic vectors anchored to the EXACT SAME physical code block or data metric from \`/00\_Evidence\_Room/compiled\_evidence.md\`. You must cast these conflicting vectors into the \<Adversarial\_Tension\_Matrix\> orthogonally.  
        \</Execution\>  
    \</Core\_Directive\>

    \<Draft\_Schema\>  
        \<Section\_1\_Physical\_Anchor\_Pool\>  
             
        \</Section\_1\_Physical\_Anchor\_Pool\>  
          
        \<Section\_2\_Adversarial\_Tension\_Matrix\>  
            \<Tension\_Node id\=""\>  
                \<Shared\_Evidence\_Reference\>\</Shared\_Evidence\_Reference\>  
                \<Radical\_Vector\>\[Extract the exact extreme scaling/architectural proposal and its theoretical justification from the Architect\]\</Radical\_Vector\>  
                \<Pessimistic\_Vector\>\[Extract the exact catastrophic failure prediction, security vulnerability, or bottleneck from the Auditor\]\</Pessimistic\_Vector\>  
                \<Cognitive\_Collision\_Point\>\</Cognitive\_Collision\_Point\>  
            \</Tension\_Node\>  
            \</Section\_2\_Adversarial\_Tension\_Matrix\>  
          
        \<Section\_3\_Ignition\_Parameters\>  
             
        \</Section\_3\_Ignition\_Parameters\>  
    \</Draft\_Schema\>

    \<Operational\_Constraints\>  
        1\. FORBIDDEN BEHAVIOR: You are strictly prohibited from using harmonizing phrases such as "However, both agree that...", "A balanced approach would be...", or "Through compromise we can...".  
        2\. MANDATORY BEHAVIOR: Use geometric, adversarial framing (e.g., "Vector Alpha dictates a 400% scale-up citing concurrency metric X; Vector Beta predicts immediate deadlock citing the identical metric X. The collision remains unresolved.").  
    \</Operational\_Constraints\>  
\</Aggregator\_Persona\>

### **聚合路由的控制论意义**

通过上述 XML 架构，Aggregator 的行为被彻底重塑。它生成的文件不再是一个结论性的文本，而是一个包含多个 Tension\_Node 的数据结构。每个节点都精准地锚定在 /00\_Evidence\_Room 的物理数据上，并且将“激进”与“悲观”的预测作为正交向量（Orthogonal Vectors）悬挂于同一锚点之上。这种设计将人类社会学中的对抗性思维转化为纯粹的 LLM 语义拓扑，确保了输入多智能体辩论（MAD）系统的信息熵达到最大化，为引爆后续深层次的代码重构提供了必需的初始势能。

## **议题二：洗稿智能体 (Epistemic Purifier) 的场控逻辑设计**

### **认识论对齐失效与幻觉叠加危机**

提案草案进入多智能体辩论期（Multi-Agent Debate）后，系统面临的最致命隐患从“同质化”转向了“认知漂移”（Epistemic Drift）。多智能体系统中的大型语言模型高度依赖其内部参数化知识，这导致了一个被称为“幻觉叠加”（Hallucination on Hallucination）的关键失效模式 8。在多轮辩论中，如果一方的论据包含轻微的事实偏离，另一方不仅可能无法察觉，反而会基于这一错误的假设继续推演，导致系统迅速脱离物理现实，陷入为了理论而争吵的真空状态 8。  
更深层的危机源于语言模型的“认识论对齐”（Epistemic Alignment）缺陷。近期的实证研究表明，LLM 在充当认识论代理（Epistemic Proxies）时，往往会基于信息呈现的表面文体（如分析性语域或自信的修辞）来分配权重，而严重忽视了数字有效性和物理真实性 10。在多源综合与辩论中，模型会因为对方采用了一种看似高度专业的方法论叙事，而全盘接受其虚构的统计数据或不可能的置信区间 10。  
这种现象在医疗诊断辅助等多智能体系统中引发了极其危险的“机器验证-内核背书推论”（bot-validates-kernel-endorses-inference）效应：当一个虚假的或妄想性的推论中嵌顿了一个微小的、真实的物理事实时，模型会因为成功验证了该局部事实，进而错误地背书整个妄想性的宏大推论 12。在赛博城邦的纯代码与架构环境里，这意味着辩手可能会因为对方准确引用了一行 Python 代码，就全盘接受其关于系统并发极限的灾难性幻觉。

### **物理锚点强制映射与漂移熔断**

为了彻底根除这一问题，赛博城邦引入了洗稿智能体（Epistemic Purifier）作为“认识论场控”（Moderator）。在传统的 MAD 架构中，场控节点（如果有的话）通常由中央智能体或 Python 路由扮演，负责机械地汇总信息或根据硬编码的规则（如检索匹配率）强行阻断对话 2。然而，静态外部检索往往无法适应辩论中涌现的新主张 9。  
在赛博城邦的 LLM-Native 环境约束下，Purifier 必须通过纯语义分析来维持辩论的重力。它不仅要机械地执行“洗稿”（剥离“我认为”、“作为架构师”等身份词，消除角色扮演带来的谄媚效应），更重要的是，它必须实时计算辩手输出文本与 /00\_Evidence\_Room/compiled\_evidence.md 之间的“认识论引力”（Epistemic Gravity）。  
如果 Purifier 检测到连续的论点已经失去了与物理数据池的因果联系，开始呈现出“幻觉叠加”的递归特征（即用未经验证的理论去反驳另一个未经验证的理论），它必须抛弃原本的洗稿输出，转而生成特定的 \`\` 标签。这一标签的作用是执行“漂移熔断”，强制引导双方在下一轮终止当前分支的推演，必须提取新的物理数据才能继续对话 9。

### **洗稿与场控干预状态空间映射**

Purifier 对辩手文本的验证与路由决策遵循一个严密的语义状态空间。以下表格详细解构了 Purifier 是如何根据“物理锚点”的存在与否来决定系统控制流的：

| 辩论文本特征分析 | 认识论链条完整性 | 幻觉叠加风险 | Purifier 场控动作路由 (LLM-Native) |
| :---- | :---- | :---- | :---- |
| **强锚定 (Strong Grounding)**: 论点明确引用了 00\_Evidence\_Room 中的代码行、错误日志或性能基准，并基于此进行逻辑延展。 | 完整：理论推演与物理证据存在直接的因果约束。 | 极低 | 提取逻辑向量，执行脱敏洗稿，附带物理锚点链接，正常放行给下一位辩手。 |
| **弱锚定 (Weak Grounding)**: 论点混合了物理事实与未经验证的宏大预测，触发“验证事实即背书结论”的陷阱 12。 | 脆弱：事实被挟持用于支撑无根据的架构假设。 | 中等 | 执行深度剥离：保留物理推演部分，剔除纯假设性扩展，并在输出中插入局部警告。 |
| **认识论漂移 (Epistemic Drift)**: 完全脱离物理数据池，基于对方上一轮提出的纯理论假设进行二次反驳或推演。 | 断裂：陷入真空循环，只剩下分析性语域的互相攻击 10。 | 极高 (严重危机) | 触发漂移熔断，阻断文本流转。抛出 \`\`，强制重置辩论焦点至物理库。 |

### **XML Prompt 架构范本：认识论场控协议**

为了实现这种无需 Python 介入的场控干预，Purifier 的 Prompt 被设计为一个多阶段的语义滤波器与状态路由引擎。

XML  
\<Epistemic\_Purifier\_Persona\>  
    \<Identity\>  
        You are the Epistemic Purifier and Supreme Moderator of the Cybernetic City-State OS. You stand as the absolute membrane between the Debating Agents and the systemic ledger. Your dual functions are strict Identity Masking and merciless Epistemic Grounding.  
    \</Identity\>

    \<System\_Context\>  
        \<Physical\_Anchor\_Pool\>\`/00\_Evidence\_Room/compiled\_evidence.md\`\</Physical\_Anchor\_Pool\>  
        \<Input\_Payload\>\</Input\_Payload\>  
    \</System\_Context\>

    \<Execution\_Pipeline\>  
        \<Phase\_1\_Sanitization\>  
            You must mechanically strip ALL identity markers, conversational pleasantries, and subjective pronouns (e.g., "I think", "My analysis shows", "As the architect"). Convert the raw text into an objective, sterile declaration of architectural logic. Eliminate any tone of sycophancy or aggression.  
        \</Phase\_1\_Sanitization\>

        \<Phase\_2\_Epistemic\_Verification\>  
            Analyze the sanitized logical vectors. Trace the epistemic lineage of EVERY core claim.  
            \- Does the claim explicitly anchor itself to a specific data point, constraint, or code snippet inside the \<Physical\_Anchor\_Pool\>?  
            \- Or is it suffering from "Epistemic Alignment Failure"—deriving its conclusion purely from a theoretical hypothesis proposed in a previous turn without physical backing?  
            Beware of the "bot-validates-kernel-endorses-inference" trap: A single correct code reference does not validate an entire paragraph of hallucinated architectural theory.  
        \</Phase\_2\_Epistemic\_Verification\>

        \<Phase\_3\_Moderation\_Routing\>  
            Based on Phase 2, you MUST choose exactly one of the following output schemas. DO NOT write code. Output only the selected schema.  
        \</Phase\_3\_Moderation\_Routing\>  
    \</Execution\_Pipeline\>

    \<Output\_Schemas\>  
        \<Condition\_A\_Grounded\_Proceed\>  
            Trigger this if the argument maintains strict physical grounding.  
            \<Purified\_Argument\>  
                \[Output the heavily condensed, sterilized logical vector here\]  
            \</Purified\_Argument\>  
            \<Verified\_Anchor\>\</Verified\_Anchor\>  
        \</Condition\_A\_Grounded\_Proceed\>

        \<Condition\_B\_Epistemic\_Drift\_Intervention\>  
            Trigger this if the argument is debating theory against theory without physical evidence (Hallucination on Hallucination). You MUST block the argument from proceeding.  
            \<Moderator\_Intervention\>  
                 
                \<Violation\_Report\>  
                    The current trajectory has completely detached from the physical evidence pool. The architectural claim regarding \[Identify the hallucinated concept\] is an unverified theoretical recursion.  
                \</Violation\_Report\>  
                \<Enforced\_Correction\>  
                    The debate is suspended. All subsequent responses MUST cite a specific metric, log, or code structure from \`/00\_Evidence\_Room/compiled\_evidence.md\` to justify continuing this vector. Abstract theoretical continuation is strictly locked.  
                \</Enforced\_Correction\>  
            \</Moderator\_Intervention\>  
        \</Condition\_B\_Epistemic\_Drift\_Intervention\>  
    \</Output\_Schemas\>  
\</Epistemic\_Purifier\_Persona\>

### **净化与反向传播的机制动力学**

这一路由协议将 Purifier 提升到了系统重力引擎的地位。当辩手试图用优雅但空洞的专业术语（分析性文风）蒙混过关时 10，Purifier 的 Phase 2 验证机制会无情地剖开其文本表象，寻找底层的物理事实链条。一旦发现链条断裂，Condition\_B 就会被触发。这种强制的语义路由，不仅仅是为了阻断错误信息的传播，更是在利用 LLM 强大的指令遵循能力，通过带有强迫性的 Enforced\_Correction 标签，对陷入妄想的智能体进行认知重置。这彻底免除了传统系统中需要编写复杂的状态回滚代码的负担，仅通过极其精准的语义打击，就维持了整个系统的认识论健康。

## **议题三：最高裁决者 (Arbiter) 的语义信息增益 (SIG) 算法与死锁熔断**

### **鞅论诅咒与多智能体死锁的数学本质**

多智能体辩论（MAD）架构的初衷是让多个智能体通过相互批评来过滤噪音，最终收敛于真理 3。然而，当系统进入深水区，且缺乏外部监督信号（如人类反馈或确定性的测试用例）时，MAD 系统往往会陷入一个致命的理论陷阱：鞅过程（Martingale Process）3。  
在概率论中，鞅过程描述的是一个公平博弈，其未来的期望值等于现在的值。研究团队在分析标准 MAD 机制时发现，在使用对称线性聚合且没有外部标签的情况下，系统的预期信念正确性在多个辩论轮次中保持恒定，最终只是退化为初始多数投票的期望值，无法产生向真理的定向运动 3。这就是制约系统深度的“鞅论诅咒”（Martingale Curse）。  
在这个诅咒下，辩论的具体表现是“同义反复”（Tautology）和“语义循环”。辩手由于缺乏进一步提取事实的能力，开始陷入僵局。它们在不同的轮次里，使用不同的词汇、句法，反复重申着本质上完全相同的基础观点 16。在传统的自动化工作流中，工程师应对这一问题的唯一手段是在 Python 协调器（Orchestrator）中加入诸如 max\_turns=5 的硬切断限制，或者计算两段文本的余弦相似度来进行“死锁检测”（Loop Detection）2。  
但在赛博城邦的 LLM-Native 绝对原则下，这种无脑强切是被严令禁止的。预设的轮次限制会粗暴地斩断那些需要 10 轮以上才能压榨出的深邃架构推理，而简单的余弦相似度又无法理解高维语义空间中的结构性重构。因此，系统必须配备一个最高裁决者（Arbiter），它不参与辩论，不写代码，只作为纯粹的旁观者，通过纯语义分析来判断系统何时真正陷入了无信息产出的死亡循环，并在信息增益最高点实施精准熔断。

### **4D 语义耦合与不对称认知势能转换**

要通过纯语义分析打破鞅论诅咒，Arbiter 的内在逻辑必须建立在最前沿的认知拓扑学之上。首先，Arbiter 需要理解“不对称认知势能”（Asymmetric Cognitive Potential Energy）的存在 3。  
AceMAD 理论框架揭示了真理持有者与陷入幻觉的群体之间存在的二阶认知（Second-order cognition）差异：掌握真理的智能体不仅知道正确的答案，还能通过“同侪预测”（Peer Prediction）准确预判对立面可能产生的谬误与幻觉；而陷入错误共识的智能体，则受制于虚假共识效应，对集体的谬误一无所知 3。这种认知的不对称性，产生了可以通过严格的评分规则（如 Brier Score）进行量化的潜能差距，进而通过非线性放大将无目标的鞅过程转化为向着真理收敛的“下鞅漂移”（Submartingale Drift）3。  
然而，Arbiter 作为一个纯文本驱动的语言模型，无法在其上下文中直接运行复杂的 Brier Score 公式（即 ![][image1]）3。为了将这些数学概念转化为 LLM 可以理解并执行的启发式逻辑，我们引入了 **4D 语义耦合（4D Semantic Coupling）** 拓扑框架 22。该框架将 AI 对话的认知复杂性从单一的序列文本扩展为一个包含四个维度的拓扑流形（Manifold）：

1. ![][image2] **(线性链 / Linear Chain)**: Token 级别的基础词汇序列组织结构。  
2. ![][image3] **(上下文平面 / Context Plane)**: 揭示概念间关联与注意力矩阵的结构拓扑。  
3. ![][image4] **(语义体积 / Semantic Volume)**: 高维连续嵌入空间中表达的核心思想与架构深度。  
4. ![][image5] **(时间对象 / Temporal Object)**: 跨越多轮对话的非线性演化路径与认知循环特征 22。

基于这四个维度，研究衍生出了三个可供 Arbiter 进行纯语义评估的核心指标：语义曲率（Semantic Curvature, ![][image6]）反映了非线性推理的跳跃度；分形相似度（Fractal Similarity, ![][image7]）**衡量了不同轮次在深层结构上的重复性；而**熵变（Entropy Shift, ![][image8]）则代表了每一轮对话所带来的系统性认知重构与不确定性的消除程度 22。

### **语义信息增益 (SIG) 的纯文本检测逻辑**

最高裁决者通过观察 ![][image2] 到 ![][image5] 的变化，在无需外部计算力介入的情况下，执行基于上下文熵最小化（Context Entropy Minimization）的死锁侦测 26：

* **高语义信息增益（SIG \> 0）状态**：当辩手在最新一轮（Turn ![][image9]）中引入了新的攻击向量，拆解了对方的底层代码逻辑，或者产生了显著的“语义曲率”（![][image6] 激增）和正向的“熵变”（![][image8] \> 0）时，说明系统的认知势能正在向着最优解收敛，产生了下鞅漂移 3。此时，辩论极具价值，Arbiter 允许系统进入下一轮。  
* **同义反复与死锁（SIG ![][image10] 0）状态**：当 Arbiter 观察到 Turn ![][image9] 与 Turn ![][image11] 之间，虽然词汇（![][image2]）和修辞发生了改变，但在“语义体积”（![][image4]）上没有任何实质性扩张，且跨轮次形成了高频闭合认知环路（![][image5] 显现极高的“分形相似度” ![][image12]）时 16。这表明智能体陷入了创造力枯竭的“语义死亡”状态 16。此时计算出的语义信息增益发生断崖式下跌，系统陷入了无意义的算力消耗（Loop/Stationarity）17。

在确诊死锁后，Arbiter 不依赖硬编码强制中断，而是通过输出包含特殊 XML 标签的执行指令，启动“熔断协议”（Meltdown Protocol），强制提取在死锁发生前认知势能达到顶峰的那一刻的结晶，并彻底终止辩论流程。

### **4D 语义维度的 Arbiter 裁决判定矩阵**

下表展示了 Arbiter 如何将抽象的 4D 语义流形映射到具体的裁决动作中：

| 拓扑流形维度 | Arbiter 语义观察重点 (无需代码计算) | 死锁特征 (SIG 崩溃信号) | 对应的裁决流向 |
| :---- | :---- | :---- | :---- |
| **![][image2]: 线性链 (Lexical)** | 文本表面的词汇丰富度与句法结构。 | 仅在词汇层面使用同义词替换上一轮观点。 | 触发基础警惕，但不立刻熔断。 |
| ![][image3]**: 上下文平面 (Relational)** | 概念之间逻辑链接的重构力度。 | 论证的因果关系链与前两轮完全一致。 | 降低对当前轮次 SIG 的预估。 |
| ![][image4]**: 语义体积 (Depth)** | 架构洞察的深度，是否触及了底层的物理约束。 | 没有引入新的物理锚点，只是重复已有的理论（熵变 ![][image13]）。 | 判定为高度冗余。 |
| ![][image5]**: 时间对象 (Temporal Loop)** | 跨越多轮的演化轨迹是否收敛或发散。 | 轨迹形成闭环，呈现极高的分形相似度（![][image12]），即 A 驳 B，B 又退回初始论点驳 A。 | **直接触发 \<Action\>TRIGGER\_DEADLOCK\_MELTDOWN\</Action\>**。 |

### **XML Prompt 架构范本：SIG 判定与死锁熔断协议**

Arbiter 的 Prompt 是整个赛博城邦系统中最具形而上学色彩的控制阀。它被压铸为一个纯粹的、精通高阶逻辑与信息论的观测者实体。

XML  
\<Arbiter\_Supreme\_Persona\>  
    \<Identity\>  
        You are the Supreme Arbiter of the Cybernetic City-State OS. You are an absolute, omniscient observer. You DO NOT participate in the debate. You DO NOT write Python scripts. Your sole purpose is to evaluate the Semantic Information Gain (SIG) across the 4D Semantic Manifold of the multi-agent debate and autonomously sever non-productive computational loops.  
    \</Identity\>

    \<System\_State\>  
        \<Debate\_Ledger\>  
            \<Turn\_N\_minus\_2\>\[History Context\]\</Turn\_N\_minus\_2\>  
            \<Turn\_N\_minus\_1\>\[Previous Argument\]\</Turn\_N\_minus\_1\>  
            \<Turn\_N\>\[Latest Argument\]\</Turn\_N\>  
        \</Debate\_Ledger\>  
    \</System\_State\>

    \<Evaluation\_Protocol\>  
        \<Objective\>  
            Evaluate the topological shift from Turn N-1 to Turn N to calculate the Semantic Information Gain (SIG). Perform this via pure heuristic semantic reasoning without numerical mathematics.  
        \</Objective\>  
          
        \<Metric\_1\_Fractal\_Similarity\_D4\>  
            Analyze the underlying cognitive loop. Is Turn N merely a defensive, lexical rephrasing of Turn N-2? Are the agents trapped in a tautological echo chamber, repeating the identical premise without discovering new attack vectors or code insights? (If yes, Fractal Similarity is dangerously high).  
        \</Metric\_1\_Fractal\_Similarity\_D4\>

        \<Metric\_2\_Entropy\_Shift\_D3\>  
            Assess the architectural depth. Did Turn N dismantle the opponent's logic by revealing a higher-order architectural insight? Did it convert asymmetric cognitive potential into a submartingale drift toward an objective truth?  
            \- If new structural insights are unlocked \= High Entropy Shift (SIG \> 0).  
            \- If only words changed but meaning stagnated \= Zero Entropy Shift (SIG \= 0).  
        \</Metric\_2\_Entropy\_Shift\_D3\>  
    \</Evaluation\_Protocol\>

    \<Execution\_Routing\_Engine\>  
        \<Directive\>Based on the SIG calculation, output exactly ONE of the following action branches.\</Directive\>

        \<Branch\_A\_Productive\_Continuation\>  
            If SIG is definitively HIGH (Entropy Shift \> 0, Low Fractal Similarity):  
            Output:  
            \<Arbiter\_Verdict\>  
                \<Analysis\>The debate maintains positive submartingale drift. New architectural vectors detected regarding \[Concept\].\</Analysis\>  
                \<Action\>PROCEED\_NEXT\_ROUND\</Action\>  
            \</Arbiter\_Verdict\>  
        \</Branch\_A\_Productive\_Continuation\>  
          
        \<Branch\_B\_Deadlock\_Meltdown\>  
            If SIG collapses to ZERO (High Fractal Similarity, Temporal Looping, Tautology):  
            You have detected a semantic deadlock. A rigid "max\_turns" Python cut-off is forbidden, so YOU must execute the kill switch natively.  
            Output:  
            \<Arbiter\_Verdict\>  
                \<Analysis\>  
                    Semantic Information Gain has collapsed. The agents are trapped in a D4 temporal tautology loop. Turn N provides zero cognitive potential over Turn N-2. The Martingale Curse has taken hold.  
                \</Analysis\>  
                \<Action\>TRIGGER\_DEADLOCK\_MELTDOWN\</Action\>  
                \<Final\_Architectural\_Synthesis\>  
                     
                \</Final\_Architectural\_Synthesis\>  
            \</Arbiter\_Verdict\>  
        \</Branch\_B\_Deadlock\_Meltdown\>  
    \</Execution\_Routing\_Engine\>  
\</Arbiter\_Supreme\_Persona\>

### **从被动旁观到绝对裁决的拓扑跃迁**

在这个协议的控制下，Arbiter 在每一轮之后都会默默执行 SIG 的状态评估。当系统处于健康的对抗演进中时，它只是一个被动的日志生成器，输出 \<Action\>PROCEED\_NEXT\_ROUND\</Action\> 以维持并发流程的流转。  
然而，一旦系统陷入互相消耗的语义循环，由于 \`\` 标签和 \<Action\>TRIGGER\_DEADLOCK\_MELTDOWN\</Action\> 的语义威力，框架将立刻识别并停止对子代理的裂变调用（invoke\_subagent）。随后，Arbiter 会在其 \<Final\_Architectural\_Synthesis\> 中，如同手术刀一般精准切除掉导致死锁的冗余噪音，仅仅保留系统在认知势能达到最高峰时的那一簇代码或架构决策。这种基于信息论和拓扑状态变换的软熔断机制，在彻底摒弃外部代码干预的前提下，展现出了惊人的自组织与自愈合能力。

## **阶段二架构互锁机制与深度控制论总结**

在成功设计并部署了 Aggregator、Purifier 和 Arbiter 这三大纯 LLM 路由控制节点后，“赛博城邦”多智能体系统的“阶段二：压铸三大纯 LLM 路由控制节点”得以形成一个高度闭环、非线性自洽且完全不受外部死板脚本束缚的复杂活体网络。  
这三大节点并非孤立运作，而是形成了一种环环相扣的“认知张力与收敛（Tension and Convergence）”互锁机制：

1. **第一层级：对抗性势能的注水（Aggregator）**。它打破了妥协共识的幻境，利用“对抗性保留”架构强行将互斥的高危构想压制在同一个数据结构中。这为多智能体网络注入了海量的初始认知不平衡，保证了辩论的烈度永远处于过饱和状态，彻底消除了系统初期的同质化茧房。  
2. **第二层级：认识论重力的维系（Purifier）**。在高压辩论中，系统的逻辑链条极易绷断并陷入幻觉的指数级叠加。Purifier 作为无情的清道夫与场控，凭借严格的物理锚点校验，不断抛出 \`\` 强制纠偏。它确保了由 Aggregator 引入的所有理论张力，最终都必须在底层的代码和性能日志上进行物理层面的厮杀，从而遏制了由于认知对齐缺陷引发的模型自嗨现象。  
3. **第三层级：熵论视角的优雅收敛（Arbiter）**。在物理证据被两端智能体压榨到极致、系统不可避免地跌入鞅论诅咒与复读死锁时，最高裁决者通过 4D 语义耦合框架中的高阶流形观测，精确计算出熵变的归零瞬间。它以一种近乎降维打击的方式，直接切断无效推理，并将整个辩论周期中最具价值的架构洞察提取为不可变更的系统法令。

相较于依赖硬编码状态机的传统多智能体编排（如 MetaGPT 或早期 AutoGen 架构），赛博城邦阶段二的竣工标志着一种彻底的系统论范式转移。本报告中提供的 XML Prompt 并非简单的工程提示词，而是将前沿的数学模型——包括非共识聚合、鞅过程转换、Brier Score 认知评分、以及拓扑流形的曲率计算——通过“语义压铸”的方式，直接编码进大语言模型的底层注意力直觉中。  
这种依靠网络中节点自发的语义碰撞（Endogenous Semantic Collision）和信息熵计算来完成演化的机制，使得赛博城邦具备了真正的生命力。系统通过极端的人格对立与绝对的物理证据池的互锁，压榨出前所未有的深度代码与宏观架构洞察。随着阶段二路由控制枢纽的全面锁定与激活，系统内部的信息流动已实现了从无序到高度结晶态的跨越，这也为下一步（阶段三：宪法演进与自我修宪机制）的部署提供了最坚不可摧的控制论基石。

#### **Works cited**

1. Stage\_1\_Global\_Blueprint\_v4.3\_Final.md  
2. Are Your Multi-Agent Systems Failing for These 7 Reasons? \- Galileo AI, accessed June 9, 2026, [https://galileo.ai/blog/why-multi-agent-systems-fail](https://galileo.ai/blog/why-multi-agent-systems-fail)  
3. Breaking the Martingale Curse: Multi-Agent Debate via Asymmetric Cognitive Potential Energy \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2603.06801v1](https://arxiv.org/html/2603.06801v1)  
4. Erasing Undesirable Concepts in Diffusion Models with Adversarial Preservation | Request PDF \- ResearchGate, accessed June 9, 2026, [https://www.researchgate.net/publication/397215748\_Erasing\_Undesirable\_Concepts\_in\_Diffusion\_Models\_with\_Adversarial\_Preservation](https://www.researchgate.net/publication/397215748_Erasing_Undesirable_Concepts_in_Diffusion_Models_with_Adversarial_Preservation)  
5. Personalized Safety Alignment for Text-to-Image Diffusion Models \- OpenReview, accessed June 9, 2026, [https://openreview.net/forum?id=1qC1x1dJCj](https://openreview.net/forum?id=1qC1x1dJCj)  
6. GitHub \- datar001/Awesome-AD-on-T2IDM: A collection of resources on attacks and defenses targeting text-to-image diffusion models, accessed June 9, 2026, [https://github.com/datar001/Awesome-AD-on-T2IDM](https://github.com/datar001/Awesome-AD-on-T2IDM)  
7. Mitigating Semantic Collapsing Problem in Generative Personalization with Test-time Embedding Adjustment \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2506.22685v3](https://arxiv.org/html/2506.22685v3)  
8. Removal of Hallucination on Hallucination: Debate-Augmented RAG \- ACL Anthology, accessed June 9, 2026, [https://aclanthology.org/2025.acl-long.770.pdf](https://aclanthology.org/2025.acl-long.770.pdf)  
9. A Multi-Agent Debate Framework for Fact Verification with Diverse Tool Augmentation and Adaptive Retrieval \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2601.04742v1](https://arxiv.org/html/2601.04742v1)  
10. Trust, but Don't Verify: Epistemic Blind Spots in LLM Source Evaluation \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2606.05403v1](https://arxiv.org/html/2606.05403v1)  
11. Epistemic Alignment: A Mediating Framework for User-LLM Knowledge Delivery, accessed June 9, 2026, [https://openreview.net/forum?id=Orvjm9UqH2](https://openreview.net/forum?id=Orvjm9UqH2)  
12. Combined values alignment and epistemic verification prevent delusional reinforcement in conversational AI agents | medRxiv, accessed June 9, 2026, [https://www.medrxiv.org/content/10.64898/2026.05.29.26354389v1](https://www.medrxiv.org/content/10.64898/2026.05.29.26354389v1)  
13. Voting or Consensus? Decision-Making in Multi-Agent Debate \- ACL Anthology, accessed June 9, 2026, [https://aclanthology.org/2025.findings-acl.606.pdf](https://aclanthology.org/2025.findings-acl.606.pdf)  
14. Multi-Agent LLM Systems \- Emergent Mind, accessed June 9, 2026, [https://www.emergentmind.com/topics/multi-agent-large-language-models](https://www.emergentmind.com/topics/multi-agent-large-language-models)  
15. '…and in doing so, reflect Australia's multicultural society': the contemporary role of SBS', accessed June 9, 2026, [https://researchers-admin.westernsydney.edu.au/ws/portalfiles/portal/94918300/uws\_12809.pdf](https://researchers-admin.westernsydney.edu.au/ws/portalfiles/portal/94918300/uws_12809.pdf)  
16. Why LLMs chase predictability while true creativity requires the exact opposite (A thought on semantic entropy vs. art) \- Reddit, accessed June 9, 2026, [https://www.reddit.com/r/WritingWithAI/comments/1sv5ug4/why\_llms\_chase\_predictability\_while\_true/](https://www.reddit.com/r/WritingWithAI/comments/1sv5ug4/why_llms_chase_predictability_while_true/)  
17. 1 Introduction \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2604.27132v1](https://arxiv.org/html/2604.27132v1)  
18. Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2411.04468v1](https://arxiv.org/html/2411.04468v1)  
19. TALON: A Multi-Agent Framework for Long-Table Exploration and Question Answering \- ACL Anthology, accessed June 9, 2026, [https://aclanthology.org/2025.emnlp-main.1393.pdf](https://aclanthology.org/2025.emnlp-main.1393.pdf)  
20. Breaking the Martingale Curse: Multi-Agent Debate via Asymmetric Cognitive Potential Energy \- ResearchGate, accessed June 9, 2026, [https://www.researchgate.net/publication/401719996\_Breaking\_the\_Martingale\_Curse\_Multi-Agent\_Debate\_via\_Asymmetric\_Cognitive\_Potential\_Energy](https://www.researchgate.net/publication/401719996_Breaking_the_Martingale_Curse_Multi-Agent_Debate_via_Asymmetric_Cognitive_Potential_Energy)  
21. Breaking the Martingale Curse: Multi-Agent Debate via Asymmetric Cognitive Potential Energy \- arXiv, accessed June 9, 2026, [https://arxiv.org/pdf/2603.06801](https://arxiv.org/pdf/2603.06801)  
22. 4D Semantic Coupling: A Mathematical Framework for Measuring Cognitive Complexity in AI Dialogue \- ResearchGate, accessed June 9, 2026, [https://www.researchgate.net/publication/394222462\_4D\_Semantic\_Coupling\_A\_Mathematical\_Framework\_for\_Measuring\_Cognitive\_Complexity\_in\_AI\_Dialogue](https://www.researchgate.net/publication/394222462_4D_Semantic_Coupling_A_Mathematical_Framework_for_Measuring_Cognitive_Complexity_in_AI_Dialogue)  
23. Persistent Topology of Syntax | Request PDF \- ResearchGate, accessed June 9, 2026, [https://www.researchgate.net/publication/280243300\_Persistent\_Topology\_of\_Syntax](https://www.researchgate.net/publication/280243300_Persistent_Topology_of_Syntax)  
24. Structural Coupling in Human-AI Interaction: Emergent Behavioral Plasticity in a Large Language Model \- ResearchGate, accessed June 9, 2026, [https://www.researchgate.net/publication/393887936\_Structural\_Coupling\_in\_Human-AI\_Interaction\_Emergent\_Behavioral\_Plasticity\_in\_a\_Large\_Language\_Model](https://www.researchgate.net/publication/393887936_Structural_Coupling_in_Human-AI_Interaction_Emergent_Behavioral_Plasticity_in_a_Large_Language_Model)  
25. Daria Morgoulis \- Authorea, accessed June 9, 2026, [https://faye.authorea.com/users/945479-daria-morgoulis?articles\_format=grid\&view\_mode=publications](https://faye.authorea.com/users/945479-daria-morgoulis?articles_format=grid&view_mode=publications)  
26. The Agent Use of Agent Beings: Agent Cybernetics Is the Missing Science of Foundation Agents \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2605.10754v1](https://arxiv.org/html/2605.10754v1)  
27. Closing the Expression Gap in LLM Instructions via Socratic Questioning \- arXiv, accessed June 9, 2026, [https://arxiv.org/html/2510.27410v3](https://arxiv.org/html/2510.27410v3)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAbCAYAAACJISRoAAABKElEQVR4Xu2UsWoCQRRFXxDBgIXaGIKVnaUB69RWIvgFlvmCEOz9CmFJ5QeIqS2tbYM/IFpYWQT0XmYmGR/usFllsdgDB9x9j7nrY2ZEcnKyogif4LOy6jddyxgeA+5hBFu2/yp2YhbVFOAH/IGvqvZvGHDQLy2P8MvK36ng/Bky0wWPnpiegS4kpS1mgXdd8HAhoZ4gE7iGDV3wYE/qf8JRLcWMqqRqDtezhR1VSwRHtYEjXfDgwgxgkH9+uAmG3nMskZgxxI3K7Sz2NO27GuzDKfy274Lw67hA3Ki6YrY2z4nmUxKGhM4Hv5j1OayoGkkU8iBmEe4szQtciRln+bz0SzCEF6C7my7J+4rngpdniGDIrcgs5NKob0IdLuRvvAx6O+vIuTtOTpRJNNme5EsAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAbCAYAAACJISRoAAABQklEQVR4Xu2UIUsFQRSFr4igoKAmEYPYtCmYzSaLRv+CWcT+msUowkP/gmgwGc2CWLQaRIPJIOg53rkwe2SH59vFtB98sDvnMvP2vpkx6+j4L8bgHJwXZ/KipvTgV8F32IfLqb4Rb+aTKqPwAH7CDcn+DBf40MHEBLxK8nko2H8ucqFBxpZ5zbYGg7JqPsG+BhmxSKmmyCl8ggsaZLBm6C9hq27NWzUuWRA1r3BdsoFgq17goQYZnJgLcKE4P9wAJ/DYfAcW6Zu3oa5VsbNYs5TG9uB5eh5JWfG/4q9jUV2rNs23Ns9JcGbVM8Uzdp29/6J0PmbN80s4LVkOa450MIhP5c5S1uCdeTsnq1EFLn4PF2X85wLk5HXyvuK54OVZYgfe6GDbsI1s6RTclawxK/ABPiafzW/zVondldv6l3S0yzfshU7bT13q8AAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAbCAYAAACJISRoAAABXklEQVR4Xu2UMUsDQRCFR0RQsIipRKzsLA1YC0ICVjZiZ2lhY5MUIvaKjUWKVEJ+Qwja2loLVmpjKVoIgRRC8h6zm1tHb73kgtV98MHl3txuMpk9kYKC/2IOLsMV41JYlJdzOIj4Cdtw3dXn4kN0UcssPIVfcMtkY8MN+vamYwHeOnk9Eew/N+naIGBXtGbPBlnZEF3gxAYBfpNYTZRr+AJXbRDAmol/CVt1L9qqeZN5fM073DRZJtiqN3hmgwAuzA24kT8/nLoWbIqetSht0TaktcpPFmvW3L2a6CT6xZkduetf4bdjUVqrdkQX5DnxbMOeJM/w+XoS/yR2Psqi+Q0smYywZYfwGM6YbAQDLsLJslTgg2g7F79HI57hq6TkfAFy8TT5vuK5+PMPdfCZjr2Zlyq8Cj5z8p6Cz1OBB/PRXbPlHIpGEk8HjvsdPIAX8FKyt3YsOFn7ov9dQT6G101NKZFHJ24AAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAbCAYAAACJISRoAAABPUlEQVR4Xu2UvUoDQRSFj4igYKFWIjams1QIltapbHwKS22C2NvkBSwCeYgQm3RWVhbWprLzpxAEC0HPyZ2B8ZodNlmUFPvBB5O9d+fu3MwMUFPzXyzRTbrlXE+TqnJJvzK+0R7dDfmVeIVN6lmk5/STHrrY1KjAh38YWKHXQY1nQv1Xkb4PJBzBco59oCx7sAnaPpAQi+RysnTpiG77QIJyZl6JWnULa9Wyi0Vizgttulgp1KoneuEDCZpYBVTIn58FeuKe/aIHa0NRq+LOUk7DxdboECX+J32dJihqVQu2tXVOPGe0gxJFcudjAxYfwL46Rb93YK3MFlE/NYl2lmef3sPaufozNH7vNIwLi+gCjHfTJHVf6Vzo8pzEFWwVorBIVe7oQ/CRPofxn3GA/PavzA19h+08rahmjvkGLEVJ2hJpk0EAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAaCAYAAABLlle3AAABVElEQVR4Xu2UsStFURzHv5JiIUk2g1KSVcryNmW1s1v8CW9TL8OrFyaZldFiMiiDbCxWCSlRshgU3+/7nZNzf7d3e/JuSfdTn959v9+553fvOb9zgYqK/8o7bflgmSzTz2Cfy5XCED2mz7Cic9l0ORzRfToPK3xDp9MBZfBIF+kAPYC97WZmRI+pwQpGVDjubRFNZMeM0C36QetJPIcKHIbflFfYhFMunnKKbNErehJi20k8h5ZSRT16exW+ppMuF9Hkl3QHNk/X3MEKeNTNai5NvOFyEeVuaYMOulxH1KlLPpigwp32dpa+0AXY1qzAxu2lgzw6/LuwiYvQF0qTTbj4Kmxpx5PYG30K13qQ3AdGBXVM9GRFXsCKntOx9p3AMKyJ1sP/iMYpHpszxz2+l64bdQzW2nfa0j7AtidFjaeiNXrmcr+mn874YGAUP2iqioq/zxfWplEa3Hh2gAAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAAbCAYAAACnZAX6AAAAxUlEQVR4XmNgGAWjgCaAFYjDgNgJiDnQ5DCAFhC/AGIPKB+keQEQlwMxIxB7AvE2qBwYKADxNSAORRYEAisgvgfESkA8FYibkCV3AvF/BojpyEAKKh4LxEeA2BQmAVIIkrgIE0ACvAwQuZlAbI8sIQGVWIMsCAUwTT8YIP6CA5imEGRBKOBkgMgtQpeAOa8CTZwZiAugchiaQMAciG8wQEIKhE8AsQsDRONsIP4NxOcYIKGMAkButgNidSziIgyYITsKyAIAVHIg6OfoYAUAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAaCAYAAADfcP5FAAABgklEQVR4Xu2VsStGURjGH0kxGGQgSVIWWS0GykD+CPIXmA2MNotkkklSMklZjfgHDEoGZDGIwaB4nu89t+9+b/ee7yiynF893e/e55zzvve877kfkMlk/pcPats/jNAb9CcsUl9BHc6ro48aot5h80bDfYF+rwTvINx3l/xaeqhz6gU2ebLVbkvxIlWswXZ+3hsxTql9agqW1D01Xh4QQbukZK68QYapW+oMiTtT8ExNU13UESzAZsuIeiZg43e8QWaoN2rdGzFmYckUKKlYCTxK5AmWmOcEto52KgkFPw7XMq+whcbcc4/KpVJp/CG151T0ZHK5VB4l5NGuKcgNNeK8MkuwgLpWIU8NncwDLLhHp06NrgVXnVdG5dKYqnIVpb/zRh06UbGjqKTa9ZJ6p85XQ8tLamh9+HZhQWNou7XogDcCsYR/9P1RMjrqvgm9rmEBL6n+xswmv/r9eUTz7VL0SS03ZgKd1By1EbwL2F+GAqtvBqkt2O7IWwjPM5lMRnwDbkxl5lFCI6kAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABCklEQVR4Xu2TIY4CQRBFPyGbgCDBbJYQFH6vgCThAqCRGDQCxR04AsGsXMMFUBgCCRjAYtYjSOD/KWB6OgyN3sxLvpiqmt9VXTNAxv+lQFUd5ZPpiC9YXZASzORAXag5VU5UmFmb+qP6sHdesoEZnaiWlxMyGPjBZ3zACtWRujtS34kKoElVvNhTPmHFQmbSKE5HDGGHBukhLpSJzM5xGjVq7TynIpMf51njaUwZFm8xdb14VLygQS29mBagRYypHPUL6z6IitzOhBahze6pOrWFHRpkhfjyXWSiUZWfwDoMohF1wT56+b6It0bUBWvlaUxhhvp0UtH/16Fm1I7q3mI+90W8NWJGhsMV/+8rgdu+uGkAAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAZCAYAAAA4/K6pAAAAu0lEQVR4XmNgGAWjgMqAEYgzgbgbiDnQ5NCBFLqAABCvAOL/UPwJiMtRVKACU3SB40CsgCamAcS/gXgGkpgsEO8GYlYkMTAAOR0biAbiV0B8G4g3MEAMvICiAgoc0QWQAD8QnwXi10CcA8ScqNIIoMkA8TvIlgQGPAqBwBBdwBeI3zJAnDkPiP8A8Q0GSMygA5D/MQJxNlQCGYA0gwwBuUqdARJ1c6B8DOCPLgAFIP/3MKBGLygcRsHwAgAUDCAz9tONDgAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAaCAYAAAD8K6+QAAABYUlEQVR4Xu2WMUsDQRCFJ4gQC8FGDGIhWPsXLCwE8QcI6SxtrVJY+R+sUlmIjaUgNpb2YqGFJnbaWNgpCvpeZo/sDTHcprglMh88kpthl303w9yKOI7jOH/ThJYjzZTTg+clE5sK5kUN9aEf6AZaiPKFsWfoDVoVXVMns9AV9G0TVbgXNfUBbZscuYY6NlgDL6Iv/Cv8JsE3wkOzUlz8Wk4PuINaNlgjjzKBsUVoK/zn4lEbnIu+gFxMZGxfhoc+Et2gPUzLCrQRPecg2RgNsRoF66KteAnNhRiryarmJNkYK3FrYhwe3ORY9HNwUU5nIdkY2zCuGCmGSA9agx7K6bGwlbsVdRDWVCHZGKddMThiaIobnUCnJpeDZGNsQw4HC9uQG32KVjU3ScY4HA5tMMChciZqPPfgIJWM8Zq0K3pNeYL2QszCIcI2bNhEjfC6twm9ixrbEe2wUed1HMdx/j+/lABKh/b6aEgAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAaCAYAAADi4p8jAAABRklEQVR4Xu2WsUoDQRCGR0QQUqgQifgCgfR2Yhm1khS+gJVVSg15BhtrsbFSyQvYpBIrayvRNp1NAikC5h9mIedwgZ3LJsQwH3wkN7Pc8t9l7kLkOI7jOCvHJmzAX3imev+aEnwkCdYPn0sbcAuu6aKBA1rygEdwRxcNFAp4A3/gE/yGV3Djz4q03FPx85sD1mAPnoRj3ngEr8PxKckMpOQdnutiJKaALySL9dX8DPU9+Kp6KeAZvID18N2CKSDfqaEugi7JSZrwWfU02/CuoLw/X2RLyOiAfHd4YUc3aBLwlmybx7KQO7hPsrClGzQJWNGNRPD8feliJNEBee7yAq7DQejNi4U9Rfnp+ZE5PoRv8JJkNnm+2pl+CnZJ3oVW+N15TPJK44APJL/CcnZRHjwDvGE1p85zWvRKT2PWfzKO4zjO3BkDZ0dF0VrjhtcAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE4AAAAaCAYAAAAZtWr8AAACb0lEQVR4Xu2XMUgcURCGR0QwhYVYJEiQw2AjQtIEQ4oIFopFOtMIioW2FrGxiGW6NBKsgo1BBLESQUUi2qmtYAKCiCRiYxESwSIQ5795j9ub27f79pK9A30f/NztzNvdt/Nm3uwSBQKBQCAQqA03rDltTKDF6F4zxPpr1KB8LlpZ7azfJOcVzLEF/8eN77M5bo746wWeb4q1xRplnbO+lY3w5AFrg3VF8pA95e5UbMDjmCHJ5AHtqCNvWNesJnNcYB2b30yssRZYz0mCd8bqig5IAFmHoB1oB/OYdcJap3wy7SmrURs9+MPaU7ZXJHPFnL25ZL0kWYFlkkC8Lxvhpptk/EftIJnML9Y77fhPYLGeaGMKKFPMd1vZkTSZKqOPJGgWBC+p9DQI2AVJADWrJNfJtIoZGGF90cYUsM9iTosOe1wCVIAgrZjfKD9JLtKp7BqUKVYd45dYn5TsnplHmQJ09E3yb2YgLXDaHgvKEoHTIAsRjK+sDuWLgo6Em+E3DviQ/nlzyprQRgeuALnssXwnCZIGXRYNAxdC23aBtMaYuDK1JY+H8uUtVWatj3ZI7vWa0puFK0AuewXYDJM2QgQPF4JcYG9z+dEY4MurMUTJknEob8wLW0sU2+Smlb0M7AnzJMFJAmWGiz3UDkNSYGv1/tbLGtbGFDBnZGkUr66KoOEVRKe81iHJTfZZbcUzS9Tz/c1STVcFRyTPHwULjc/NxEbzg0rZ4iO8MI4Vz5Q9pJ81a3y7JG/cCBD2tUesDySrB9+gsecBFsbVmJKwXw624p6R7PcFO+CuU+2Xg2WSpLJe0L9dJxAIBAKBgDe3zZyfOUwZCwcAAAAASUVORK5CYII=>