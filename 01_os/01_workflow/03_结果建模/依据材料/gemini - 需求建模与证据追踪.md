# **基于证据与约束的需求实现结果建模与机械校验实现层调研报告**

## **第一部分：检索元数据与全域知识图谱概览**

为深层次解答关于“结构化需求至结果建模映射及证据挂载校验”的复杂工程问题，本报告对提供的底层文献与跨学科数据库进行了穷尽式检索与信息提取。在此必须明确区分文献记载的客观事实与本报告基于事实演绎出的逻辑推断。  
关于检索范围与截断边界的报告，文献库成功覆盖了古典情报分析理论及其现代计算演进、结构化与抽象论证理论的数学模型、循证医学的证据分级系统及其在环境科学中的变异，以及需求工程和公理化设计的严格数理表达。返回为空或出现信息截断的领域主要集中在“完全无监督且不依赖领域本体的纯自动化假设生成”环节。目前的工业级落地案例大多需要人类专家定义初始参数空间，纯粹依赖大语言模型（LLM）实现从零到一的复杂防幻觉假设生成的尝试，大多处于学术原型阶段，缺乏大规模工程验证的成功案例。  
基于穷尽检索，本报告提取的完整方法论与工具清单如下： 包含竞争性假设分析（ACH）、基于主观逻辑的竞争性假设分析（ACH-SL）、通用形态分析（GMA）、Toulmin论证模型、论证交换格式（AIF）、Dung抽象论证框架（AF）、带有偏好与规则的结构化论证框架（ASPIC+）、Carneades论证模型、GRADE证据评级框架、Navigation Guide系统评价方法、GRADE-CERQual定性研究评价体系、目标导向需求工程（GORE/KAOS）、以及公理化设计（Axiomatic Design）。 在软件与工程实现层面，涵盖了PARC ACH、Sheba（Veriluma）、pickaxe-rs（ASPIC+的Rust实现）、GoCHR（Carneades后端的约束处理规则引擎）、ArguLab、OntoKai（本体编排系统）以及SHACL（RDF图谱形状约束语言）。  
关于用户预定义的五个领域，本报告进行了相关性研判，并基于逻辑推断补充了一个极其关键的工程领域。详细的领域相关性分析如表1所示。

| 领域分类 | 研判状态 | 文献事实记载与逻辑推断分析 |
| :---- | :---- | :---- |
| **情报分析方法论** | 高度相关 | **文献记载**：ACH框架由Richards J. Heuer于中央情报局开发，其核心在于不充分且可能存在欺骗性的证据环境下进行假设证伪1。**逻辑推断**：该领域的“诊断性矩阵”直接对应工作流中“证据-主张”映射的底层数据结构，但其实践痛点在于生成能力的缺失。 |
| **论证理论 / 形式论证** | 核心基石 | **文献记载**：从Toulmin的非形式逻辑模型到Dung的抽象论证框架（AF），再到可区分严格规则与可废止规则的ASPIC+框架，该学科解决了冲突证据下的主张存活计算问题3。**逻辑推断**：这是实现“主张挂载证据”可机械校验且支持语义驳回的直接数学基础。 |
| **系统性综述 / 循证方法** | 高度相关 | **文献记载**：GRADE确立了从证据强度到推荐等级的映射机制，而其衍生的Navigation Guide和CERQual则解决了非量化、非医学环境下的证据降级问题6。**逻辑推断**：这些框架的升降级规则可直接抽象为工作流中的证据权重计算算法。 |
| **知识表示** | 工程枢纽 | **文献记载**：资源描述框架（RDF）结合形状约束语言（SHACL）能够对图数据进行严格的拓扑校验8。**逻辑推断**：若要实现万级节点以上的机械校验，必须将论证网络序列化为知识图谱，并由SHACL引擎在数据库写入层直接拦截“孤立主张”。 |
| **设计方法论 / 方案生成** | 高度相关 | **文献记载**：公理化设计（Axiomatic Design）通过功能需求与设计参数的矩阵映射，利用独立公理检验设计耦合度10。**逻辑推断**：这种矩阵解耦方程是机械化生成高质量候选方案B的数学准则。 |
| **(新增) 目标导向需求工程** | 补充引入 | **文献记载**：KAOS框架提出了“满意度论证（Satisfaction Argument）”和基于反向溯因的“障碍分析（Obstacle Analysis）”12。**逻辑推断**：该领域完美缝合了“给定结构化需求，推导实现结果”的逻辑闭环，特别是其生成候选假设和验证系统边界的代数方法。 |

## **第二部分：竞争性假设分析（ACH）的自动化可行性与操作机制**

竞争性假设分析（ACH）是情报界处理复杂、模糊信息的标杆性方法论。探讨其能否自动化，必须首先解构其标准的实际操作流程。

### **2.1 ACH的核心操作步骤与矩阵机制**

文献记载表明，ACH的核心哲学不是去寻找支持某一最可能假设的证据，而是竭尽全力去“证伪”尽可能多的替代假设，以此来克服人类分析师根深蒂固的确认偏误（Confirmation Bias）1。Richards J. Heuer将其标准化为一个严密的连续流程。  
该流程的起点是识别所有的潜在假设，要求分析师团队通过发散性思维列举出所有互斥的候选情境，确保如果其中一个为真，其余必须为假。紧接着，分析师需要列出所有相关的证据和论点，这里的证据被广义地定义，不仅包含已知的硬数据，还包括逻辑推演、操作假设以及“如果该假设为真，理应出现却缺失的数据”1。  
在进入核心的评估阶段时，必须构建一个二维矩阵。通常将候选假设置于矩阵的顶部作为列标题，将所有收集到的证据和论点列在左侧作为行首。分析师在这一阶段被强制要求执行一种被称为评估“诊断性（Diagnosticity）”的操作。所谓诊断性，是指某一条证据区分不同假设的能力。分析师需要横向审视矩阵，即针对每一条证据，逐一判断其与所有假设的关系是“一致（Consistent）”、“不一致（Inconsistent）”还是“不相关（Not Applicable）”1。如果某条证据对所有的假设都呈现“一致”，那么这条证据在这个矩阵中就毫无诊断价值，需要在后续的提炼步骤中予以剔除1。  
在对所有证据完成标记后，系统或分析师将进入计算与淘汰环节。与传统直觉相反，ACH的评分机制高度关注“不一致性”。文献明确指出，包含最多“不一致”标记（即被最多证据反驳）的假设将被判定为相对可能性最低的假设，从而被优先淘汰1。在这个过程中，证据的可靠性（Reliability）和相关性权重也会被考虑在内，但系统得出的数学总分绝不能直接推翻分析师的最终专业判断2。  
在得出初步结论后，ACH要求进行严格的敏感性分析（Sensitivity Analysis）。分析师需要测试，如果矩阵中起到关键支撑或证伪作用的几条核心证据是虚假的、被误导的，或者有其他解释，最终假设的存活排名是否会发生剧烈变化。最后，输出的报告不仅要包含最可能的假设，还必须详细说明曾经考虑过哪些替代方案，以及它们被哪几条具体证据所击破（即您的工作流中“主张挂证据”的雏形），并设定未来观察的里程碑指标1。

### **2.2 自动化实测边界与失败案例分析**

关于ACH能否实现自动化或半自动化，文献库中记录了大量的工业尝试与学术实证研究。客观事实表明，ACH的完全自动化在逻辑底层存在不可逾越的障碍，而其自动化尝试也暴露出明显的失败案例。  
在软件实现方面，Xerox Palo Alto研究中心曾开发了经典的PARC ACH工具，此外还有结合了主观逻辑（Subjective Logic）的Sheba技术被应用于Veriluma等智能评估软件中2。近年，结合大型语言模型（LLM）的自动化尝试也开始涌现，例如提出前瞻性假设发现（PHD）框架，通过约束LLM生成解析矩阵18。  
然而，必须主动审视自动化尝试的失败案例。文献记载了2004年MITRE公司（Cheikes等人）进行的一项严格对照实验。该实验旨在评估计算机辅助的ACH工具能否真正缓解复杂分析中的确认偏误。实验结果出人意料：ACH工具仅仅在没有任何分析经验的新手参与者中起到了缓解偏误的作用，而在资深分析师群体中，该工具未能产生显著的正面效果19。随后Pirolli在2006年的研究也表明，使用纸笔进行ACH分析与使用计算机化的ACH工具之间，在参与者构建问题的方式上并没有显著差异19。  
这些实证失败的根源指向了ACH理论本身的局限性。批评者指出，ACH在结构上将假设集合视为一个“扁平的列表（flat list）”，它错误地假定证据项目本身可以直接与假设保持一致或不一致，而无法表示“从属论证（Subordinate argumentation）”2。换言之，证据本身是否可靠，往往需要另一套完整的证据链来支撑，ACH矩阵无法处理这种嵌套的图谱结构。  
基于上述文献事实，本报告推断，在您的工作流中若应用ACH机制，必须进行严格的人机边界划分。表2展示了实测推断出的任务归属。

| ACH 分析步骤 | 任务归属推断 | 实现层理由与约束机制 |
| :---- | :---- | :---- |
| **证据可靠性的底层研判** | **必须由人介入** | 模型无法处理现实世界中“证据本身的伪造风险”，从属论证缺乏嵌套计算能力，初始信任权重需人工或外部信誉库校验。 |
| **最终结论的裁定与采信** | **必须由人介入** | ACH原著强调，数学得分矩阵存在盲区，不能凌驾于专家判断之上。自动化得分只能作为预警系统。 |
| **高通量矩阵一致性计算** | **可交给模型** | 将规则和知识库交由逻辑推理机计算“一致/不一致”极具效率，能在毫秒级完成数百条证据与方案的交叉对比。 |
| **诊断性过滤与剪枝** | **可交给模型** | 剔除对所有方案B的属性都显示为“支持”或“不相关”的冗余约束证据，算法实现复杂度极低。 |
| **自动化敏感性测试** | **可交给模型** | 通过蒙特卡洛模拟或SAT求解器，机器可以自动穷举“如果某条证据失效”时矩阵得分的方差分布，这是人类无法在短时间内完成的。 |

## **第三部分：ACH的评估本质与假设的衍生生成机制**

### **3.1 ACH仅为评估框架的本体缺陷**

文献明确记载，ACH在本质上是一个纯粹的“评估与淘汰框架”，它本身并不具备生成假设的内在机制1。社会建构主义批评家对ACH提出了严厉的指责，认为ACH完全忽视了最初形成矩阵假设网格时的内在问题。大量证据表明，影响假设生成的不仅有官僚和心理偏见，还有深层次的文化和身份认同因素。这些社会建构因素在假设进入ACH矩阵之前，就已经起到了“预筛选（Pre-screen）”的作用，从而在被选中的假设中不断强化确认偏误2。  
由此推断，您对“ACH只做评估不做生成”的担忧不仅切中要害，而且是学术界公认的方法论盲区。如果系统地将需求A转化为结果建模B，B作为“假设的集合”绝不能从真空中产生。

### **3.2 候选假设的配套生成方法**

为了弥补这一缺口，跨领域的文献提供了三种具备工程可操作性的生成方法，能够与ACH或论证框架形成闭环。  
第一种是基于目标导向需求工程（GORE/KAOS）的“障碍分析（Obstacle Analysis）”方法。KAOS框架不仅仅用于记录需求，更重要的是利用“溯因推理（Abductive Reasoning）”来生成系统可能面临的场景或失效假设。文献记载，其操作流程是通过形式化逻辑回归（Regression of the goal negation），即将系统的目标（Goal）进行逻辑求反，并与已知的领域属性（Domain Properties，即外部证据）结合，利用算法反向推导出导致目标无法达成的最小前提集合13。这些被算出的前提就是生成的“假设”。这种方法在航空和安全工程中被用来机械地生成威胁场景。  
第二种是通用形态分析（General Morphological Analysis, GMA）。这是一种不依赖直觉的纯组合推导方法。文献记载，通过提取问题的所有独立维度参数，并列举每个维度的所有可能状态值，可以建立一个庞大的多维矩阵。随后，使用诸如Carma Viewer这类软件，通过强制性的交叉组合生成数万种潜在候选方案。生成后，分析师或模型利用“交叉一致性矩阵”来剔除物理上矛盾或逻辑上互斥的组合，剩余的配置即为有效的候选假设22。据推断，这种方法极度适合从“结构化需求A”生成“方案B”，因为A的结构化属性天然可作为形态分析的维度。  
第三种是前沿的基于大语言模型（LLM）的自主生成框架，如“前瞻性假设发现（PHD）”。文献记载，2024年的最新研究提出了这种旨在解决模型“附和偏误（Halo Effect）”的框架。它不要求模型给出最终答案，而是向模型输入非结论性的碎片化证据、异常观察和环境记录，约束模型输出必须符合严格JSON Schema（即Toulmin模型的变体）的假设空间18。该方法通过上下文感知的评分准则和自我纠错循环，强迫模型从证据的缝隙中生成具测试性的全新方案，实验证明其在生成质量上高度对齐人类专家18。

## **第四部分：形式论证与主张挂接证据的可机械校验结构**

要满足“B的每条主张都要写明它依据哪条证据”并实现自动化检查，不能停留在文本层面的解析，必须深入到知识表示与计算论证理论。文献提供了从理论模型到代码库的完整演进路径，关注其可实现性。

### **4.1 论证拓扑的演进：从Toulmin到Dung的抽象框架**

论证结构的理论起点是Toulmin模型。该模型将论证拆解为六个具象维度：主张（Claim）、根据/证据（Grounds/Evidence）、保证（Warrant）、支撑（Backing）、反驳（Rebuttal）和限定词（Qualifier）23。然而，Toulmin模型主要应用于自然语言分析和修辞学，由于其对内部逻辑关系的松散定义，直接用于机械校验会导致巨大的计算歧义。  
为了实现真正的机械计算，文献记载了Dung提出的抽象论证框架（Argumentation Framework, AF）。Dung的AF具有极简的数学美感：它剥离了论证的内部结构，将所有的论证视为抽象的节点（Arguments），并定义了一个二元关系——“攻击（Attacks）”关系，构成有向图模型5。基于这个图，系统可以计算出不同的“语义（Semantics）”，如无冲突集、可接受集，并最终得出完整（Complete）、优先（Preferred）、稳定（Stable）以及有根扩展（Grounded Extension）26。其中，“有根语义”代表了在无争议情况下必定存活的论证集合，文献明确指出，计算Dung框架的有根扩展是一个多项式时间（Polynomial Time）算法，这在工程实现上意味着其能够支撑极大规模数据的实时校验27。

### **4.2 ASPIC+ 与 Carneades 的工业级实现**

抽象论证解决了图论计算，但无法体现“主张 ![][image1] 证据”的内部结构。为此，文献引入了ASPIC+框架，这是目前AI领域最权威的结构化论证系统。ASPIC+允许系统使用知识库（包含证据前提）和两类推理规则：保证结论必然成立的“严格规则（Strict Rules）”以及可能存在例外的“可废止规则（Defeasible Rules）”29。  
在实操层面，ASPIC+ 已经具备成熟的工业级实现。例如，在 Rust 语言生态中的 pickaxe-rs 库，提供了一条完整的计算管线。文献记载，该工具包含了实例化引擎（Grounder）、基于规则合成树状论证的构造器（ArgumentConstructor）、识别“削弱（Undermine）”、“反驳（Rebut）”和“削足适履（Undercut）”三类冲突的攻击计算器（AttackComputer），以及最终调用 SAT 求解器或多项式算法进行扩展计算的评估器（Evaluator）30。据推断，在您的系统中，只需将“结构化需求”转换为规则，“外部证据”转换为知识前提，即可利用 pickaxe-rs 瞬间计算出方案 B 中哪些主张被证据有效支撑，哪些被反向证据击溃。  
与之并行的是基于“证明标准”的 Carneades 论证系统。文献记载，Carneades 模型不仅建立论证树，还引入了法律意义上的门槛概念。一个主张是否被“验证”，取决于挂载在它身上的证据权重是否越过了设定的证明标准，例如“证据优势（Preponderance of evidence，正方权重大于反方）”、“清晰且令人信服的证据（Clear and convincing evidence）”或“排除合理怀疑（Beyond reasonable doubt）”31。最新版的 Carneades 4 使用 Go 语言开发了原生约束处理规则（CHR）推理引擎（GoCHR），消除了对 Prolog 的依赖，并支持使用 JSON 序列化基于 AIF（论证交换格式）的数据，极大地增强了现代微服务架构中的可部署性33。

### **4.3 图数据库层面的终极物理拦截：SHACL**

无论是 ASPIC+ 还是 Carneades，解决的都是“语义有效性”问题。但要实现系统级的“自动检查有无孤立主张（无证据支撑的主张）”，最鲁棒的做法是在知识表示层进行拓扑拦截。  
文献记载，形状约束语言（SHACL，W3C 标准）是专门用于验证 RDF 知识图谱是否符合一组结构约束的声明式语言9。它与传统的推理机不同，其核心任务就是校验数据形状。据推断，只需将结果建模 B 存储为 RDF 图数据，并编写如下极为简练的 SHACL 规则，即可实现零幻觉的机械校验：要求所有被判定为“主张（Claim）”类型的节点，其向外指向“证据（Evidence）”节点的路径（sh:path）的数量（sh:minCount）必须大于等于 18。如果违反该规则，图形数据库在写入或校验阶段将直接抛出异常，拒绝接受该“孤立主张”。这种方案的可实现性极高，已被 OntoKai 等企业级本体编排系统广泛验证24。

## **第五部分：循证方法 GRADE 向非医学领域的映射与失败反思**

为了将证据转化为具体建议，医学与政策领域耗费巨资打造了标准化的工作流，GRADE（推荐分级、评估、制定与评价）框架是其中的绝对主导者。探讨其映射规则及跨领域的失败教训对您的系统构建至关重要。

### **4.1 GRADE 的核心映射规则与升降级机制**

文献记载，GRADE 系统将从证据到建议的过程严格量化为两个阶段。第一阶段是评估证据主体的质量（置信度），将其划分为高、中、低、极低四个等级。第二阶段是将证据质量结合其他因素（如价值观、资源限制）转化为行动建议的强度，分为“强（Strong）”与“弱/有条件（Weak/Conditional）”35。  
这一映射体系的核心在于其极其机械的“升降级（Upgrading/Downgrading）”积分卡。对于任何证据池，GRADE 规定存在五个核心降级因素：偏倚风险（Risk of bias，例如盲法破坏）、不一致性（Inconsistency，各研究结果方向相左）、间接性（Indirectness，干预对象或终点不匹配）、不精确性（Imprecision，样本量过小导致置信区间过宽）以及发表偏倚（Publication bias）。与此同时，如果研究显示出巨大的效应量（Large effect）、明确的剂量-反应梯度（Dose-response gradient），或者所有合理的残余混杂因素都会减弱当前观察到的效应，则可以对证据进行升级加分37。

### **4.2 跨领域搬运的滑铁卢与改良版 Navigation Guide**

**这套东西能否原封不动地搬到非医学领域？文献事实给出了响亮的否定回答。** 生搬硬套原始 GRADE 曾导致严重的政策瘫痪。  
文献记载了原始 GRADE 搬运到环境健康科学时的重大失败。GRADE 框架在底层设计上拥有一个不可动摇的“基线偏见”：它硬性规定随机对照试验（RCT）自动作为“高质量”证据的起点，而所有的观察性研究（Observational studies）自动降级为“低质量”证据38。在工程测试、环境评估、污染政策等非临床医学领域，研究人员根本无法、也没有道德许可去进行随机双盲毒性测试。这意味着，即使收集了海量的工业监测数据，只要套用 GRADE 框架，结论永远只能被打上“低置信度”的标签，导致决策机构（如环保署 EPA）无法给出强有力的政策建议38。  
为了解决这一冲突，加州大学旧金山分校等机构耗费数年开发了改良版的 **Navigation Guide（导航指南）** 系统，并在全氟辛酸（PFOA）毒性评估等著名案例中进行了压力测试。文献记载，Navigation Guide 对 GRADE 进行了大刀阔斧的改革：

> 1. **重置证据基线**：彻底废除“观察性研究即低质量”的铁律，明确在环境与政策分析中，人类观察性研究的基准线被提升为“中等（Moderate）质量”，然后再根据偏倚风险进行升降级39。  
> 2. **重构建议输出标签**：由于非医学领域往往不需要开具“吃药”的建议，而是进行风险研判，Navigation Guide 取消了“强/弱建议”的二元分类，将其重新映射为五级毒性判定：“已知有毒”、“可能（Probably）有毒”、“或许（Possibly）有毒”、“不可分类”以及“可能无毒”39。

此外，在纯粹依靠定性访谈、社会文本挖掘的质性研究领域，GRADE 的数值化体系同样完全崩溃。为此衍生出了 **GRADE-CERQual** 框架，其不再痴迷于统计学方差，而是将映射规则替换为四个高度抽象但可操作的维度：方法学限制（Methodological limitations）、连贯性（Coherence，数据模式是否清晰）、数据充分性（Adequacy，数据丰度）和相关性（Relevance，证据背景与问题的契合度）7。  
据此推断，在您的工作流中若需建立“证据强度 ![][image2] 建议强度”的映射，绝不能盲目引入原始 GRADE 的层级架构。您应当吸收 Navigation Guide 重置行业基线的思想，并引入 CERQual 的“连贯性”和“相关性”指标，利用加权积分生成模型中节点的主张置信度。

## **第六部分：从约束与证据生成候选方案的机械流程**

系统工程、运筹学和需求工程领域长期致力于解决“如何在已知约束下合成最优方案”，这些方法论追求严密的代数和逻辑演绎，而非模糊的“创造力发挥”。

### **6.1 GORE 中的满意度论证与环境推断**

文献记载，在诸如 KAOS 这类目标导向需求工程（Goal-Oriented Requirements Engineering, GORE）框架中，从需求到方案的生成被形式化为一个严格的逻辑推演体系。其最核心的基石被称为“满意度论证（Satisfaction Argument）”12。  
这个论证建立在一个基础的布尔逻辑演绎等式上：系统要求（System Requirements，即我们需要生成的方案B）与环境的固有规律（Domain Properties，即外部证据与约束），两者的逻辑合取必须能够演绎出最初的业务目标（Goals，即结构化需求A）42。用形式化语言表述即：  
![][image3]  
这是一个高度可操作的流程。操作步骤如下：分析师首先明确公式右侧的目标 ![][image4]。然后，将所有不可变更的外部环境限制和已验证的硬性证据输入系统，作为已知的 ![][image5]13。此时，左侧的 ![][image6] 成为求解变量。借助 SAT 求解器或模型检测工具，系统可以穷举或推导出必须满足哪些技术条件才能使逻辑等式成立。生成的这些条件组合，就是经过数学验证的候选方案。如果系统无解，说明“需求与现实约束存在硬性冲突”，此时必须提示业务端修改需求，从而避免了无效方案的流转44。

### **6.2 公理化设计（Axiomatic Design）的矩阵解耦生成法**

比逻辑推理更具工程实操性的是由麻省理工学院 Nam P. Suh 提出的“公理化设计”体系。文献记载，该方法论将整个设计过程抽象为相邻域之间的映射。对于您的工作流而言，就是将“功能需求域（Functional Requirements, FR，对应结构化需求A）”映射到“设计参数域（Design Parameters, DP，对应结果方案B）”10。  
公理化设计将这种生成关系抽象为一个极其优雅的线性代数方程，即“设计方程”：  
![][image7]  
在这个方程中，![][image8] 被称为设计矩阵（Design Matrix），其内部的元素代表了某个特定方案参数对某项需求的偏导数（或直接的影响关系，通常用 ![][image9] 或 ![][image10] 标记）。  
这个方程的伟力在于它提供了一套名为“独立公理（Independence Axiom）”的机械化过滤标准。当系统尝试将不同的组件拼装成候选方案 B 时，系统将自动检查生成的特征矩阵 ![][image8]10：

> 1. **非耦合设计（Uncoupled Design）**：如果矩阵是对角矩阵（除了对角线全是零），意味着方案中的每一个参数都干净利落地解决了一个需求，互不干扰。这在机械判定上是**完美的候选方案**48。  
> 2. **解耦设计（Decoupled Design）**：如果矩阵可以被重排为下三角或上三角矩阵，意味着方案是**可接受的**，但必须按矩阵指示的严格顺序进行实施调试，否则将陷入混乱48。  
> 3. **耦合设计（Coupled Design）**：如果矩阵中非零元素无序且无法三角化，说明各项参数互相牵制（即按下葫芦浮起瓢）。公理化设计规定，这种方案极其低劣，在自动化生成阶段就应当被算法**直接丢弃淘汰**10。

在筛选出多个非耦合或解耦候选方案后，文献记载可进一步应用“信息公理（Information Axiom）”。该公理提出，信息内容最小（即满足所有需求所需的额外信息或复杂概率最低）的方案才是最佳方案46。  
据此推断，您的系统可以通过预定义底层模块库，将外部证据作为参数空间的约束。在生成方案 B 时，算法通过穷举组合底层参数形成矩阵，然后通过矩阵分解算法（如判断是否为三角阵），以极低的计算成本过滤掉数以亿计的耦合废案，直接输出物理上和逻辑上最稳健的候选模型。这一过程完全规避了对大语言模型幻觉的依赖，是真正的硬核工程生成。

#### **Works cited**

> 1. Analysis of Competing Hypotheses (ACH part 1\) \- SANS ISC, [https://isc.sans.edu/diary/22460](https://isc.sans.edu/diary/22460)  
> 2. Analysis of competing hypotheses \- Wikipedia, [https://en.wikipedia.org/wiki/Analysis\_of\_competing\_hypotheses](https://en.wikipedia.org/wiki/Analysis_of_competing_hypotheses)  
> 3. Automatic Generation of Structured Explanations for Arguments from Consequences \- MADOC \- Uni Mannheim, [https://madoc.bib.uni-mannheim.de/66015/1/dissertation\_kobbe.pdf](https://madoc.bib.uni-mannheim.de/66015/1/dissertation_kobbe.pdf)  
> 4. argumentation — Rust implementation // Lib.rs, [https://lib.rs/crates/argumentation](https://lib.rs/crates/argumentation)  
> 5. Abstract Argumentation Framework with Conditional Preferences \- AAAI Publications, [https://ojs.aaai.org/index.php/AAAI/article/view/25766/25538](https://ojs.aaai.org/index.php/AAAI/article/view/25766/25538)  
> 6. A Path Forward for Systematic Reviews in Environmental Health: The Navigation Guide Systematic Review Methodology \- Regulations.gov, [https://downloads.regulations.gov/EPA-HQ-ORD-2013-0782-0003/attachment\_2.pdf](https://downloads.regulations.gov/EPA-HQ-ORD-2013-0782-0003/attachment_2.pdf)  
> 7. What is GRADE-CERQual?, [https://www.cerqual.org/what-is-the-grade-cerqual-approach2/](https://www.cerqual.org/what-is-the-grade-cerqual-approach2/)  
> 8. Schema-Aware RDF-to-Prolog Mapping for the AISA Project \- reposiTUm, [https://repositum.tuwien.at/bitstream/20.500.12708/177689/1/Hartmann%20Marlene%20-%202023%20-%20Schema-Aware%20RDF-to-Prolog%20Mapping%20for%20the%20AISA...pdf](https://repositum.tuwien.at/bitstream/20.500.12708/177689/1/Hartmann%20Marlene%20-%202023%20-%20Schema-Aware%20RDF-to-Prolog%20Mapping%20for%20the%20AISA...pdf)  
> 9. RDF Graph Validation Using Rule-Based Reasoning \- Semantic Web Journal, [https://www.semantic-web-journal.net/system/files/swj2145.pdf](https://www.semantic-web-journal.net/system/files/swj2145.pdf)  
> 10. Axiomatic Design \- Semantic Scholar, [https://pdfs.semanticscholar.org/a286/040a924e00125d40815f09e1163e8189ba95.pdf](https://pdfs.semanticscholar.org/a286/040a924e00125d40815f09e1163e8189ba95.pdf)  
> 11. Chapter 10 Introduction to Axiomatic Design, [https://ocw.mit.edu/courses/2-800-tribology-fall-2004/7956138e737f6cb1e9fb744fcc6c48ef\_ch10\_axiomatic.pdf](https://ocw.mit.edu/courses/2-800-tribology-fall-2004/7956138e737f6cb1e9fb744fcc6c48ef_ch10_axiomatic.pdf)  
> 12. Supporting the Systematic Goal Refinement in KAOS using the Six-Variable Model \- SciTePress, [https://www.scitepress.org/papers/2018/68507/68507.pdf](https://www.scitepress.org/papers/2018/68507/68507.pdf)  
> 13. A Framework for Analyzing Security Requirements \- Open Research Online, [https://oro.open.ac.uk/59955/1/439343.pdf](https://oro.open.ac.uk/59955/1/439343.pdf)  
> 14. Analysis of Competing Hypotheses (ACH) process – BusinessInnovationManagement.com, [https://businessinnovationmanagement.com/2020/01/19/analysis-of-competing-hypotheses-ach-process/](https://businessinnovationmanagement.com/2020/01/19/analysis-of-competing-hypotheses-ach-process/)  
> 15. \[PDF\] The Psychology of Intelligence Analysis, [https://www.ialeia.org/docs/Psychology\_of\_Intelligence\_Analysis.pdf](https://www.ialeia.org/docs/Psychology_of_Intelligence_Analysis.pdf)  
> 16. Mastering the Analysis of Competing Hypotheses (ACH): A Practical Framework for Clear Thinking \- SOS Intelligence, [https://sosintel.co.uk/mastering-the-analysis-of-competing-hypotheses-ach-a-practical-framework-for-clear-thinking/](https://sosintel.co.uk/mastering-the-analysis-of-competing-hypotheses-ach-a-practical-framework-for-clear-thinking/)  
> 17. AIR FORCE INSTITUTE OF TECHNOLOGY \- DTIC, [https://apps.dtic.mil/sti/pdfs/AD1178947.pdf](https://apps.dtic.mil/sti/pdfs/AD1178947.pdf)  
> 18. Before the Action: Benchmarking LLMs on Prospective Hypothesis Discovery \- arXiv, [https://arxiv.org/html/2607.15766v1](https://arxiv.org/html/2607.15766v1)  
> 19. Issues in Intelligence Production: Summary of Interviews with Canadian Managers of Intelligence Analysts \- DTIC, [https://apps.dtic.mil/sti/tr/pdf/ADA551144.pdf](https://apps.dtic.mil/sti/tr/pdf/ADA551144.pdf)  
> 20. Enhancing CIA Analysis Methods | PDF | Intelligence Analysis \- Scribd, [https://www.scribd.com/document/892834938/Improving-Intelligence-Analysis-25-07-14-14-10-43](https://www.scribd.com/document/892834938/Improving-Intelligence-Analysis-25-07-14-14-10-43)  
> 21. Engineering Requirements for System Reliability and Security \- Université catholique de Louvain, [https://webperso.info.ucl.ac.be/\~avl/files/avl-markt07.pdf](https://webperso.info.ucl.ac.be/~avl/files/avl-markt07.pdf)  
> 22. Crafting decision options and alternatives for designing cultural observation system using general morphological modelling \- Growing Science, [http://growingscience.com/beta/dsl/2709-crafting-decision-options-and-alternatives-for-designing-cultural-observation-system-using-general-morphological-modelling.html](http://growingscience.com/beta/dsl/2709-crafting-decision-options-and-alternatives-for-designing-cultural-observation-system-using-general-morphological-modelling.html)  
> 23. ReportLogic: Evaluating Logical Quality in Deep Research Reports \- arXiv, [https://arxiv.org/html/2602.18446v2](https://arxiv.org/html/2602.18446v2)  
> 24. Enabling Ethical AI: A case study in using Ontological Context for Justified Agentic AI Decisions \- ResearchGate, [https://www.researchgate.net/publication/398357626\_Enabling\_Ethical\_AI\_A\_case\_study\_in\_using\_Ontological\_Context\_for\_Justified\_Agentic\_AI\_Decisions](https://www.researchgate.net/publication/398357626_Enabling_Ethical_AI_A_case_study_in_using_Ontological_Context_for_Justified_Agentic_AI_Decisions)  
> 25. Totality, determinism and functionality problems in (incomplete) abstract argumentation frameworks \- Oxford Academic, [https://academic.oup.com/logcom/article/36/4/exag025/8703863](https://academic.oup.com/logcom/article/36/4/exag025/8703863)  
> 26. On Weak Constrained Argumentation Frameworks \- CEUR-WS.org, [https://ceur-ws.org/Vol-3086/paper4.pdf](https://ceur-ws.org/Vol-3086/paper4.pdf)  
> 27. Creating New Extension-Based Semantics Based On Gradual Semantics in Abstract Argumentation Masterarbeit \- Fernuni Hagen, [https://www.fernuni-hagen.de/aig/docs/master.bauer.pdf](https://www.fernuni-hagen.de/aig/docs/master.bauer.pdf)  
> 28. Preference-based Argumentation: Arguments Supporting Multiple Values \- ICR, [https://icr.uni.lu/leonvandertorre/papers/ijar07.pdf](https://icr.uni.lu/leonvandertorre/papers/ijar07.pdf)  
> 29. The ASPIC \+ framework for structured argumentation: A tutorial \- ResearchGate, [https://www.researchgate.net/publication/262869122\_The\_ASPIC\_framework\_for\_structured\_argumentation\_A\_tutorial](https://www.researchgate.net/publication/262869122_The_ASPIC_framework_for_structured_argumentation_A_tutorial)  
> 30. pickaxe\_rs \- Rust \- Docs.rs, [https://docs.rs/pickaxe-rs](https://docs.rs/pickaxe-rs)  
> 31. (PDF) The Carneades Model of Argument Invention \- ResearchGate, [https://www.researchgate.net/publication/256023008\_The\_Carneades\_Model\_of\_Argument\_Invention](https://www.researchgate.net/publication/256023008_The_Carneades_Model_of_Argument_Invention)  
> 32. (PDF) The Carneades argumentation framework \- ResearchGate, [https://www.researchgate.net/publication/284037673\_The\_Carneades\_argumentation\_framework](https://www.researchgate.net/publication/284037673_The_Carneades_argumentation_framework)  
> 33. Carneades 4.3, [https://carneades.github.io/2017/07/12/carneades-4.3/](https://carneades.github.io/2017/07/12/carneades-4.3/)  
> 34. What Is SHACL?| Graphwise Fundamentals, [https://graphwise.ai/fundamentals/what-is-shacl/](https://graphwise.ai/fundamentals/what-is-shacl/)  
> 35. (PDF) The Navigation Guide: Systematic Review for the Environmental Health Sciences, [https://www.researchgate.net/publication/266381682\_The\_Navigation\_Guide\_Systematic\_Review\_for\_the\_Environmental\_Health\_Sciences](https://www.researchgate.net/publication/266381682_The_Navigation_Guide_Systematic_Review_for_the_Environmental_Health_Sciences)  
> 36. The Navigation Guide—Evidence-Based Medicine Meets Environmental Health: Systematic Review of Human Evidence for PFOA Effects \- EPA, [https://www.epa.gov/sites/default/files/2014-12/documents/session1\_woodruff\_resource3.pdf](https://www.epa.gov/sites/default/files/2014-12/documents/session1_woodruff_resource3.pdf)  
> 37. Assessing the Risk of Bias in Systematic Reviews of Health Care Interventions \- NCBI \- NIH, [https://www.ncbi.nlm.nih.gov/books/NBK519366/](https://www.ncbi.nlm.nih.gov/books/NBK519366/)  
> 38. Applying the Navigation Guide Systematic Review Methodology Case Study \#7 Association between Prenatal Exposures, [https://www.crd.york.ac.uk/PROSPEROFILES/58805\_PROTOCOL\_20170225.pdf](https://www.crd.york.ac.uk/PROSPEROFILES/58805_PROTOCOL_20170225.pdf)  
> 39. The Navigation Guide Systematic Review Methodology: A Rigorous and Transparent Method for Translating Environmental Health Science into Better Health Outcomes \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4181919/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4181919/)  
> 40. The Navigation Guide: Systematic Review for the Environmental Health Sciences \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4181914/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4181914/)  
> 41. Applying GRADE-CERQual to qualitative evidence synthesis findings–paper 6: how to assess relevance of the data \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5791042/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5791042/)  
> 42. Goal-Oriented Requirements Engineering: An Overview of the Current Research, [https://www.researchgate.net/publication/249901480\_Goal-Oriented\_Requirements\_Engineering\_An\_Overview\_of\_the\_Current\_Research](https://www.researchgate.net/publication/249901480_Goal-Oriented_Requirements_Engineering_An_Overview_of_the_Current_Research)  
> 43. Axel Requirements Engineering | PDF | Class (Computer Programming) \- Scribd, [https://www.scribd.com/document/434567118/Axel-Requirements-Engineering](https://www.scribd.com/document/434567118/Axel-Requirements-Engineering)  
> 44. (PDF) A framework for security requirements engineering \- ResearchGate, [https://www.researchgate.net/publication/42789724\_A\_framework\_for\_security\_requirements\_engineering](https://www.researchgate.net/publication/42789724_A_framework_for_security_requirements_engineering)  
> 45. Security Requirements Engineering: A Framework for Representation and Analysis \- SciSpace, [https://scispace.com/pdf/security-requirements-engineering-a-framework-for-qd5pcbxnzk.pdf](https://scispace.com/pdf/security-requirements-engineering-a-framework-for-qd5pcbxnzk.pdf)  
> 46. Axiomatic Design and Manufacturing Systems Design, [https://ieda.ust.hk/dfaculty/ajay/courses/ieem513/Design/AxiomDes.html](https://ieda.ust.hk/dfaculty/ajay/courses/ieem513/Design/AxiomDes.html)  
> 47. A Deep Dive into Axiomatic Design \- Part I: Problem Formulation \- arXiv, [https://arxiv.org/html/2605.25735v1](https://arxiv.org/html/2605.25735v1)  
> 48. Axiomatic Design | DSPE, [https://www.dspe.nl/wp-content/uploads/2023/06/Mikroniek-2023-3-Axiomatic-Design-1.pdf](https://www.dspe.nl/wp-content/uploads/2023/06/Mikroniek-2023-3-Axiomatic-Design-1.pdf)  
> 49. system design; lean manufacturing; tps, [http://sysdesign.org/msdd/axiomaticdesign.htm](http://sysdesign.org/msdd/axiomaticdesign.htm)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAAAZklEQVR4XmNgGAWjgC6gHV2AUiAKxHbogpQABSA+hy5IKdgNxBPRBckF/UD8CYgXAvFsMvB0BixgGhB/ZaCyoSCgCMRzgZgTXYJSoMBAg4gCgTggFkAXpAageuIHAVD4joJRMFgAALj8Gxq+5nZzAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAAAYElEQVR4XmNgGAWjYFCAdnQBagBPIBZAF6QGOAfECuiClILZQLwbXRAZTGeAKCIVLwTiT0Dcz4AF0MRQcgAPEC8BYll0CUrABQYqRxQoOYWgC1IKaJL4FdEFRsEooCEAAMqlGx5YXH1zAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAaCAYAAAAXHBSTAAACl0lEQVR4Xu2WS6hOURTHl6Qoz9C9iQFmUlIeMze3TJgYIAlzExNKSclARkpJrm63voyFiYFHwgQjmZAJpUiJQopSrF9rL2efdR7kO5Q6v/r3nb3X/vbZa+211z4iPT09/5L9qvOqq6rjWf8B1Yas3SWjqqWqXem3E+apvqk+qhYG20vVLdVt1Zxg64olqjOqh6oFwfZHEBkmQ8uDDdg5HD4VDR0yTTVI4nko5qu+q55FQwa7wy6tjIYOWa96l36HgoicFNsFdqMJd+pvpR5wXgnu0Kl3Tmyig9EQmKEaj53KdNVusXNIUfmiulwaYWxWvREbM6Haq1pbGiHyWGwtdcwWe8d9sXnulc1lnotNtCoafpOB6qtqVmpvVX2WYkfJBAJGHwuDO2Lv3JbaDqmHIgR0UrU6tUlPClcjTN4UnV9xWCwoK7I+T9Ozqf1UqplwKPXNzfpwnr5B1uf4eA/cBdWNwlylySkWd0IsQrm8MuIIDpG+eaVioXdVF1ObuYlqXmAupf6cxalvX+gHP2uk302xq6eVJqccXkauxyIxJfa/WA23ixUdfjkzjDlWGiHyXvU69OFM2/20TPVCbG7mvFI2l+Fgtzm1SfVJinRy2An+F6uhF54RsdxnEfHsYCdIFJlFUr2fcscYs0XsXAG7xP+f/BxRAxHlEB+R+gvvgdTvyB6xBedO8WLGkqbAhR7vnZ1SpBkXOWJH36o2ip0b5nYI3ispigRQmPIxFXCEA88CfTHev0b1SPVBqjtC+7pYOWcsEWQBp6WIqh/+o+mZAHq13SEWMBzmm4+Ln+ex1HYoMDjr8HxNquuphW2mrHtB4KPVF9cGqcKL2l6Cje86z4SZqR1ZJ/Z1E/HxpDTr7Onp6enp+S/5ARNJjF8A0G7IAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABHCAYAAAC6YRv5AAAFjElEQVR4Xu3dT6htUxwH8CUpkn+h9zLxL/kTicKMmd5EFMmEqSgjA0JmUnoDMVEmL0PPSMqAyESZKJE/+dNLSEQh9Ypi/6yzuuusu/a9+7x377YHn0/96p699rlrnbsG99tae++TEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcNKeGergUKe1DROdMtQFQ11UVbzuibajQz3eNuyzd1Lu+0Db0PHxUK80x+Yed8xJ9NnOScxT/XeOOm/tjHHt+6JaZS4PpX47APA/GQsh/0yoCEC3DPVrpy3qr6HuSOsiDI31uV8isE0RgSXG3Tt/znGP9dP+fev6fairt05dc2vafn6pP4d6bevU/9yUBDYAWJSxcBD+SPmfeuuKoY6lHHCK94b6IG1f8YnfEStG5dw5g0/RC2A9r6b8eb9qG9K8496pnwjIvTk5dai/h7qtbVg5O+U5iqqdMdSbQ31WHRPYAGBhxsJBbMdFMPi2bVhptw0jLNzTHAs/pxyASgCYM/gUUwLb+UM9nPJn/qVpC3OOe6yfCL1HhvqmOV48lPLYI3C17kr9OYp5jhW2OgQKbACwMGPhIK6Xin/ib1THLkz5H/yZQ71VHQ9x7jXNsVB+x+mr13MGn2JKYIsxnZvyeGOLtzVl3PcO9WB7sPJCe2DEWD+xehmrmPWc1O5MefxtKAvPpv4cxZx+NNRv1TGBDQAWZiwcPDrU8aFuX70uW2c9l6ft23SxGvRYytdW1aYEn722W2CLEHpk9XO5tqs1ddw3pvy5axGSPk/rW8g7Gevn/pTHVuakFXMW7b33x0pp73OVbeBLqmMCGwAsTO+fe/gibYWXUl+unbGlrN7UFeHu0vqklSnB5+sN6qrVe3ayU2A7K623x5ZiL9hMGXdxc8qhLQJahLXy81Rj/cTqWoytrFa2on1sSzTeFwH85arihoPDQ51TnRcENgBYmLFwEDcLPJ+2HgER16G1dxOGsj1aX8x+fcrXS71UHSs2CT57ZafAFtetvV+93ovAFr5LOahtsrJWjPUT1wP2xlbE2Hs3fsQcxfu+T+uBLYJlj8AGAAvTCwflhoPY6izeTfnxEK2xi9nLoz5amwafvTAW2MpjPHoVK2+1TccdYShC2xNtwwS9fspYx244iC3raL+sbUh5jqItbkqYQmADgIXphYPy3K4pIgzFufHYiFoJPq0pwafd9typTmZL9PW0ffWrfJ42sEwZd7EfW6IRomJcT7UNKV9/9mnKq2Y98ZnixoK4wWAKgQ0AFqYXDuLY8fbgiB/S9mAWwSCOxbZqa0rwKduwUyqeP7abscAWIaYV44ux39A5vtu4i1hZqwNabIu2NyLspNdPrI7FnPRuOHg75THHXa49MUdH0vTQKLABwMLU4SC+luiRoX5M+Zq1K1N+vEdPbBnenbaC2XVpKxCUx2OUwPbhUNeuft4k+OyVOrDFBftPD/VTytfk1V//dHHKIS7G/lzKf4/ymaaMO1bTYqWrF4zKStsU7ZzEw3KPDfXJUA+k/PiQqCdT3o6+L/X7jPmL88rnid/TO68lsAHAwuwWQk5UPIg2wsWLaT0kTAk+e21shW0Tc457rn7GCGwAsDBzh4M5g08hsG1GYAOAhZk7HMwZfAqBbTMCGwAsTHwx+8G0fi3XfokQcDTNH0gisEXfB9qGieYed8xJ9DnHnNRi6zqumTuUBDYAWJS4IH3s6fh7rTzqY67gU5RHdcSNFCdi7nGX/uaYk1r51ofoW2ADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAICl+RcwhjqaV/SYHQAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAaCAYAAABGiCfwAAABFklEQVR4Xu2VMQtBURTHj2QwKGURpYTNKqMyWA3kQ5gNBqvvYMQsH0EmkyxWFrvdoPgf5+E6Ue+5N6Xev3699+7xzq/3OvchCuM4U3ABR10IGO7BNHXBDMsyIK0LHxIDI5J7zPB1iXzIgmRB8gRVXUAS5Fh2ps+vy5ksAoagQyLsv5ZvcSargL135GEavJZvcSJrgy3IkwzCDsxIhsWME9kGdL3zu4wHhZubsZaVQc245oYsYqEefysZv6YxyJE0ZrJgDg6g8PilxErGT9DTiySTeAINtW4lW4GUXiSRvdtrX8niYOId34UbskzvtUCyKCiCNUmzFkgadd7YdXp+vJck39T7Fggks00ocxJfsp/9U4f5j1wBRYU83b35Ei8AAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA4ElEQVR4Xu2TLQpCQRSFr4hgFKMYxCK4AnEB7kAtJpvF6kpMFnEJ4g4EwWw3iMEqGgyCnsOdB29uGN9oEt4HHwz3Due9+RPJ+ZUSrNpiiqIthCjDGtzAF1zDlqsTfuwMn3AI664epAuvcAcrpneBY1P7yFT07+awABvw4MbRNEXDjm68hwtvRiQ30UBqlxsN94xBd9uIhXvDkIdoIJf6NX3YET0Ahk38dnZOomGEe8Xl8qrwykTRhjPxr0D6mmSGx7+0RdHg5FSD8L0N4Ep08tbVEviUeq5HR6JPLCfn/3kDpScpFehauc4AAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAZCAYAAAAIcL+IAAAApklEQVR4XmNgGHogFYhnA3E4EPOgyYGBORC/AGIBKB9E74aKo4DtQPwDTcwTiDcBMSey4H8gvoksAARSUPFMZEGQwD5kASAQhIrPhQnwQgXQFWKIYwjgEscQwCXOjS4ABTCFW5AFQQIHkQWAQBQqDvcMCHwE4kfIAkBgCMRvgdgUWRBbgAcwYAlwEPAF4jtAXA2ln6JKowJQYpgOxO5AzIomNwpwAwC2xylAfhESuQAAAABJRU5ErkJggg==>