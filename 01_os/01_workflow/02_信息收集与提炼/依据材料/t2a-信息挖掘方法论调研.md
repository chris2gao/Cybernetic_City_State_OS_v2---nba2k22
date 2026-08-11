# **人机协作工作流中信息挖掘、信源评估与证据提炼方法论深度研究报告**

## **检索策略与报告边界说明**

本报告致力于为构建人机协作工作流提供关于“如何正确地挖掘与提炼信息”的基础方法论语料。根据系统设计的核心要求——即在明确需求后，搜索、分析、提炼外部信息以形成严谨的“证据依据”，并最终支撑可行性判断与验收测试生成——本报告采取了穷尽式、多学科交叉的视角进行深层挖掘。本报告的宗旨是不对尚未经过实践检验的框架进行过早的“最佳实践”收敛，而是将不同领域（包括情报分析、系统性文献综述、认知心理学、法学证据标准、信息学以及生态统计学）的底层逻辑、操作框架和原始文献片段进行全景式呈现，以期为后续的“扎根综合（Grounded Theory Synthesis）”提供坚实且未经扭曲的语料基础。  
在资源的投入分布上，本报告遵循了非平均用力的原则： **高投入方向**集中于信源评估、假说驱动的认知偏误机制、提炼与综合标准，以及完备性（停止判据）问题。为此，系统深入挖掘了北约海军部标准（NATO Admiralty System）、美国情报界分析标准（ICD 203）、 Richards Heuer 的竞争性假设分析（ACH）及其衍生批评、法庭科学的 Daubert 标准，以及基于生态学捕获-再捕获（Capture-Recapture）的文献完备性统计模型。**中等投入方向**涵盖了检索策略模型（如 Bates 的采摘模型与 Pirolli 的信息觅食理论）、系统性综述的搜索报告标准（PRISMA-S），以及多信源冲突处理（GRADE 框架与循环报道识别）。**低投入与截断方向**在于“否定结果的价值”。在直接检索“否定结果在情报或信息检索中的系统性价值”时，直接成体系的方法论文献返回极为稀疏。该方向的检索在遭遇数据空洞（Data Voids）后被截断。因此，本报告对该部分的补充主要依赖于竞争性假设分析（ACH）框架中对“预期证据缺失”的零散定义，以及认知心理学中的相关反证推演。

## **1\. 检索策略：从线性查询到动态觅食的认知模型**

在人机协作工作流中，信息的初步获取不能被预设为“输入查询-获取结果”的静态线性映射。认知科学和信息学提供了两种核心的底层模型来描述和指导高度复杂的信息获取行为，这两者揭示了检索动作在时间、空间和意图上的动态演变。

### **1.1 采摘模型（Berrypicking Model）**

由加州大学洛杉矶分校（UCLA）的 Marcia J. Bates 于 1989 年提出的“采摘模型”，构成了探索式信息检索的理论基石。该模型挑战了传统的单次查询匹配范式，主张真实的检索是一个伴随认知演进的动态过程。  
"First, a new model of searching in online and other information systems, called 'berrypicking', is discussed. This model, it is argued, is much closer to the real behavior of information searchers than the traditional model of information retrieval is and will guide the thinking better in the design of effective interfaces."1  
"In 1989 Bates introduced berrypicking as a powerful metaphor highlighting that searching is not a linear process but is more accurately described as an activity that is distributed in time and space... Rather than sticking to an a priori search protocol Bates described how a searcher's concept of a query is influenced by every new item of information that they encounter."3

这一理论强调，研究者不会通过单一的完美查询获得全部所需信息，而是像在森林中采摘浆果一样，在不同的信息丛中收集片段。Bates 提出了多种补充传统检索的策略，包括：足迹追踪（Footnote chasing，即向后追溯参考文献）、引文搜索（Citation searching，即向前追踪引用该文献的较新研究）、期刊浏览（Journal run）以及区域扫描（Area scanning）4。在设计自动化或协作工作流时，若强制系统遵循死板的预设协议（a priori protocol），将导致关键长尾信息的遗漏；系统必须被赋予根据新遇到的信息片段动态调整检索路径和查询词的能力4。

### **1.2 信息觅食理论（Information Foraging Theory）**

Peter Pirolli 和 Stuart Card 将生态学中的“最优觅食理论（Optimal Foraging Theory）”引入人类信息行为研究，为检索系统提供了经济学视角的评估框架。  
"Pirolli and Card employed the Optimal Diet Selection Algorithm as a means to identify a forager's optimal diet... Marginal Value Theorem (MVT)... considers the conditions under which a forager should leave a patch of information to seek another."6

该理论将不同的信源或数据库视为“信息斑块（Information Patches）”。工作流在执行检索时，需要持续计算当前的“信息获取率”。当在一个斑块内继续深挖的边际收益（新证据的发现率或预期信息增益）低于切换到新斑块的成本时，系统应当触发“离开斑块（Patch leaving）”的决策6。这为处理长尾信息的深度与广度平衡提供了可量化的数学模型基础。

## **2\. 信源评估：隔离可靠性、时效性与独立性的框架**

由于证据的质量直接决定了后续结果建模与验收测试的成败，信源评估环节构成了防范系统性错误的绝对防线。在军事情报、数字素养和司法取证领域，存在多套成熟的结构化评估体系。

### **2.1 北约海军部系统（NATO Admiralty System / AJP-2.1）**

在网络威胁情报（CTI）和开源情报（OSINT）领域，北约海军部系统是评估信源和信息可信度的黄金标准。其最核心的哲学是将“信源的可靠性（Source Reliability）”与“信息的真实性（Information Credibility）”进行强制解耦，形成一个双轴字母数字代码（如 A1、C4、F6）。  
"The Admiralty System (NATO AJP-2.1) is the gold standard for assessing intelligence... It rates two things, separately: Source Reliability (A to F): how trustworthy the origin is; Information Credibility (1 to 6): how trustworthy the data is, independent of the source. The combined output is an alphanumeric code such as A1, B3, F6. Core rule: assess source and information SEPARATELY. This is the single most common mistake."8  
"A source who is reliable on malware analysis is not automatically reliable on geopolitics. A piece of information can be true from a sketchy source, or false from a usually reliable one. Always rate them independently, never in lockstep."8

在执行信源评估时，该系统要求警惕“循环报道（Circular reporting）”造成的独立性假象。当两个表面上独立的供应商或媒体报告了相同的信息时，如果他们实际上提取自同一个原始数据集或泄露源，那么这只能算作单一来源，不能因此提高信息的可信度评分8。

| 评估维度 | 核心等级示例与定义 | 工作流应用启示 |
| :---- | :---- | :---- |
| **信源可靠性** | A (Completely reliable): 完全可靠，经证实。 C (Fairly reliable): 相当可靠。 E (Unreliable): 有明确的不准确或欺骗历史。 | 提取元数据时，要求系统对来源实体的历史记录进行独立评级，不受当前主张内容的影响8。 |
| **信息可信度** | 1 (Confirmed): 被多个真正的独立信源证实。 2 (Probably True): 符合逻辑及已知事实。 6 (Cannot be Judged): 无法评估。 | 通过交叉验证判定内容本身的合理性。遇到低置信度组合（如 E5, D4）必须触发额外的验证机制8。 |

### **2.2 SIFT 数字素养框架**

针对互联网开放域信源，华盛顿州立大学的 Mike Caulfield 提出了 SIFT 方法（Stop, Investigate the source, Find better coverage, Trace claims）。与传统的、基于预设清单的垂直审查方法（如 CRAAP 测试）不同，SIFT 强调快速的“横向阅读（Lateral Reading）”。  
"SIFT is a four-move information evaluation framework: Stop, Investigate the source, Find better coverage, and Trace claims, quotes, and media to the original context... Fact-checkers read 'laterally' (leaving sites to check external corroboration), vastly outperforming both other groups... SIFT was designed as a direct replacement for checklist-based approaches like the CRAAP test, which Caulfield argued were derived from library collection development criteria ill-suited for the open web."11  
"But knowing the expertise and agenda of the source is crucial to your interpretation of what they say... If you get an article that says koalas have just been declared extinct from the Save the Koalas Foundation, your best bet might not be to investigate the source, but to go out and find the best source you can on this topic, or, just as importantly, to scan multiple sources and see what the expert consensus seems to be."12

工作流在面对陌生域名或主张时，不应在单一信源内部耗费计算资源去解析其自我声明，而应立即跳出该信源，通过搜索引擎或事实核查数据库检索外部对该信源的评价。

### **2.3 司法鉴定视角的 Daubert 标准 (Daubert Standard)**

美国联邦最高法院在 1993 年确立的 Daubert 标准，规定了专家证词和科学证据进入法庭的可采性门槛。这一标准要求法官担任“守门人（Gatekeeper）”，不再盲目迷信专家的资历，而是审查其得出的结论是否基于可靠的科学方法论。  
"The court defined 'scientific methodology' as the process of formulating hypotheses and then conducting experiments to prove or falsify the hypothesis, and provided a set of illustrative factors...: Whether the theory or technique employed by the expert is generally accepted in the scientific community; Whether it has been subjected to peer review and publication; Whether it can be and has been tested; Whether it has a known error rate; and the existence and maintenance of standards and controls."13

在构建“验收标准”时，Daubert 标准提供了极其严苛的筛选器。如果工作流捕获的某项“证据”仅仅是某种理论，无法被客观测试（缺乏可测试性），或者没有已知的潜在错误率（Unknown error rate），则该信息不能被用作强验收标准，以防止“垃圾科学（Junk Science）”污染决策模型15。

## **3\. 假说驱动检索的利弊、认知偏误与结构化应对**

在明确需求后，“先立假说再找证据”是一种能够迅速缩小搜索空间、提高处理效率的自然认知策略。然而，该策略是一把双刃剑。如果没有严密的结构化约束，它将不可避免地导致情报分析中最致命的认识论灾难——确认偏误（Confirmation Bias）。

### **3.1 确认偏误与 Wason 的概念任务实验**

1960 年，认知心理学家 Peter Cathcart Wason 进行了著名的“2-4-6”序列实验。受试者被要求找出生成该数字序列的隐藏规则，并通过提出新的三元数字组来测试自己的假设。  
"As Wason reports, the subjects who failed at the task seemed unwilling to propose any set of numbers that tested the accuracy of their hypothesized rule and instead proposed only those that would confirm it. For instance, given the series 2, 4, 6, many subjects first wrote down 8, 10, 12, and were told 'yes, this follows the rule.' But then some just kept going with even numbers in ascending order by two. Rather than use their chance to see whether their intuitive rule of 'increase by intervals of two' was incorrect, they continued to propose only confirming instances."16  
"The human understanding when it has once adopted an opinion... draws all things else to support and agree with it. And though there be a greater number and weight of instances to be found on the other side, yet these it either neglects and despises, or else by some distinction sets aside and rejects..." (Francis Bacon，常被引用以佐证确认偏误)17

在信息挖掘中，如果系统预先设定了单一假说，其随后的搜索查询将不可避免地携带偏见，专门抓取符合预期的语料。这种“证实性搜索”会过滤掉具有高度诊断价值的反面证据，将随机或偶然的相关性扭曲为因果事实19。

### **3.2 竞争性假设分析（Analysis of Competing Hypotheses, ACH）**

为了克服人类心智在评估复杂情报时倾向于跳跃到结论并寻找证实性证据的弱点，美国中央情报局（CIA）资深分析师 Richards J. Heuer Jr. 开发了竞争性假设分析（ACH）框架。该方法被纳入了美国情报界的标准分析技术（Structured Analytic Techniques, SATs）。  
"Analysis of Competing Hypotheses (ACH) is an analytic process that identifies a complete set of alternative hypotheses, systematically evaluates data that are consistent or inconsistent with each hypothesis, and rejects hypotheses rather than trying to confirm what appears to be the most likely hypothesis."20  
"The hypothesis you want to advance is the one with the least evidence against it, not the most evidence for it."22

ACH 的核心机制强制分析师（或自动化系统）执行以下操作20：

> 1. **穷尽假说**：生成一组相互排斥且完全穷尽（MECE）的潜在假说。  
> 2. **证据矩阵构建**：建立一个以假说为列、证据为行的矩阵。  
> 3. **评估诊断价值（Diagnosticity）**：这是 Heuer 强调的最重要的一步。如果一项证据（如“监控视频显示嫌疑人在场”）与假说 A（蓄意谋杀）和假说 B（正当防卫）都完全一致，那么这项证据在区分这两个假说时**毫无诊断价值**。真正高诊断价值的证据，是那些能够明确排斥或证伪某些假说的证据。  
> 4. **寻找证伪证据**：系统必须被强制编程为去寻找反面指标（Disconfirming evidence），通过证伪来消除较弱的假设，保留那些经受住最多反面测试的假设。

### **3.3 对 ACH 框架的批判与主观逻辑演进**

尽管 ACH 被广泛推崇，但本报告遵循“不过早收敛”的原则，必须引入对该“最佳实践”的当代批评。学术界和情报理论界指出，传统的静态 ACH 矩阵存在明显局限。  
"ACH demands that the analyst makes too many discrete judgments, a great many of which contribute little if anything to discerning the best hypothesis. ACH misconceives the nature of the relationship between items of evidence and hypotheses by supposing that items of evidence are, on their own, consistent or inconsistent with hypotheses. ACH treats the hypothesis set as 'flat', i.e. a mere list, and so is unable to relate evidence to hypotheses at the appropriate levels of abstraction."24

社会建构主义批评者认为，ACH 未能解决初始假设生成过程中的成见问题。此外，随着变量的增加，静态矩阵会引发指数级的认知过载。为此，研究人员（如 Simon Pope 和 Audun Jøsang）提出了基于“主观逻辑（Subjective Logic）”的 ACH-SL 模型，利用形式化数学方法明确处理证据的不确定性，并允许将从属的证据论证链条和动态信念网络引入评估中24。  
在工作流中，这意味着不能仅仅依赖一个扁平的二维表格进行证据核对，需要构建能够处理嵌套层级、概率依赖和多代理信念推理的图模型（Graph-based modeling）。

## **4\. 提炼与综合：从原始材料到可用证据的透明化路径**

证据集的综合用途不仅在于支撑内部建模，还需要能够生成外部的验收测试。这就要求从原始材料到最终结论之间的提炼过程必须具备极高的透明度、可追溯性和逻辑严密性。

### **4.1 情报界的分析严谨性：ICD 203 标准**

《情报界指令 203：分析标准》（Intelligence Community Directive 203, Analytic Standards）是美国国家情报总监（ODNI）为纠正情报失败（如伊拉克大规模杀伤性武器误判）而颁布的核心指令，规定了任何成品情报必须遵循的贸易技巧（Tradecraft）底线。  
"The ICD identified five IC analytic standards: objectivity; independence of political considerations; timeliness; based on all available sources of intelligence; exhibiting proper standards of analytic tradecraft... Properly describes quality and reliability of underlying sources; Properly caveats and expresses uncertainties or confidence in analytic judgments; Properly distinguishes between underlying intelligence and analysts' assumptions and judgments."26

在提炼环节，系统必须强制实施两层分离：

* **事实与假设的分离**：必须在输出的结构化数据中明确标注，哪一部分是原始材料的硬性观测（Underlying intelligence），哪一部分是分析模型填补的逻辑缺口或推论（Assumptions and judgments）26。  
* **置信度的显式声明**：结论必须附加不确定性声明。不应将“来源可靠但未经验证的信息”与“来源可疑但经过多方验证的信息”混为一谈，应当分别报告其信心等级22。

### **4.2 情报之父 Sherman Kent 的战略情报哲学**

Sherman Kent 在其 1949 年的经典著作《战略情报：为美国世界政策服务》中，奠定了将情报分析视为一项严谨的社会科学研究的基调。他强调，分析不仅仅是收集事实，更是从不充分的前提中得出重要结论。  
"Intelligence, as I am writing of it, is the knowledge which our highly placed civilians and military men must have to safeguard the national welfare... The knowledge which strategic intelligence must produce is very great in mere bulk... This means that the intelligence process becomes one of group—as opposed to individual—effort; that there must be a complicated and careful division of labor..."29  
"One of the most often-cited passages from Kent's Strategic Intelligence explains that the analytic process can be undermined both when analysts are too close in their ties to consumers (inadequate independence) and when they are too distant (inadequate guidance). Kent concluded that, of the two, being too distant was the more harmful to analysts and the national security."30

这对人机协作工作流的启示在于：证据的提炼不能是在真空中进行的“黑盒”操作。工作流必须允许需求方（消费者）的意图持续引导提炼的粒度，同时保持提炼引擎（AI 代理）不迎合需求方的先入之见。

### **4.3 证据链图示：Wigmore 图表法（Wigmore Chart Method）**

在法庭科学和证据学中，John Henry Wigmore 创立的图示法被用于将大量离散的证据重组为严密的推论网络。  
"Wigmore might have been describing something like the very simple system of notation, involving a minimalist palette of just two or three main symbols (a circle for each proposition; an arrow indicating the direction of an inference; G for a generalisation)... Wigmore's Chart Method proceeds by juxtaposition. It is a practical heuristic tool for reorganising, or 'marshalling' information already known to the analyst, and possibly for identifying new sources or items of information that could be acquired and factored into the analysis."31

这要求系统不仅要提取文本，还需要将证据节点、推理箭头和一般性经验法则（Generalizations）映射为可视化的因果图谱，从而在逻辑层面上对验收标准进行支撑。

### **4.4 系统性文献综述报告标准：PRISMA-S**

针对科学文献的提炼，PRISMA-S（Preferred Reporting Items for Systematic reviews and Meta-Analyses literature search extension）提供了操作层面的强制性清单。若证据的收集过程不透明，其生成的结论将毫无复现价值。  
"The 2020 version requires them to be reported in full for at least one database, with enough detail that another researcher could reproduce the search. The PRISMA-S extension provides additional guidance on search reporting... Automation tool use must be reported... Deduplication: Describe the processes and any software used to deduplicate records from multiple database searches and other information sources."32

工作流必须记录：所有被访问的数据库名称、精确的布尔逻辑查询字符串、灰色文献（Grey literature）的处理方式、以及去重（Deduplication）的具体算法32。这种元数据记录应当随同证据集一并打包，作为“证据的证据”。

## **5\. 多来源冲突的调和机制**

当系统挖掘到两个表面上都极其可靠的信源，但其给出的结论或数据发生直接矛盾时，简单的加权平均或投票机制会导致严重的谬误。

### **5.1 GRADE 框架中的证据降级维度**

在医疗指南制定中使用的 GRADE（Grading of Recommendations Assessment, Development and Evaluation）分级体系，为处理高质量证据冲突提供了一套成熟的降级（Downgrading）逻辑。当发生不一致（Inconsistency）时，系统需要检查以下次级维度以决定偏向哪一方：  
"Domains decreasing certainty in the evidence: Risk of bias, Inconsistency, Indirectness, Imprecision, Publication bias."34

* **间接性（Indirectness）**：审查发生冲突的两份材料，其底层研究的上下文（如测试的人口统计学特征、物理实验的环境温度、特定的硬件架构）是否与当前系统正在执行的“确切需求”存在微小偏差。通常，冲突源于其一为间接证据。  
* **不精确性（Imprecision）**：考察证据背后的置信区间宽度和样本规模。如果一个信源报告的结果具有极宽的置信区间，而另一信源极为收敛，则应对前者降级。

### **5.2 识别并剥离循环报道（Circular Reporting）**

在现代网络环境和开源情报中，多信源冲突往往是不对称的。看似是“少数派报告”对抗“多数派共识”，实则可能是多数派陷入了回音室效应。  
"Circular reporting, Information, originated by a single source, appearing to come from multiple independent sources and channels with minor modifications... Manipulations exploring the lack of natural content to induce search engines to return low-quality information (Data voids)."9

在发生冲突时，工作流应调用上文提及的 NATO Admiralty 规则，强制进行溯源审查。如果发现十个指向结论 A 的高权重信源实际上全部引用了同一个初始节点，而两个指向结论 B 的信源分别来自独立的数据采集，那么所谓的“信源冲突”将被重新加权，独立信源的权重将凌驾于循环引用的集群之上8。

## **6\. 否定结果的价值与利用**

在标准的检索范式中，“未找到某物”通常被视为检索失败而被丢弃。但在严密的证据分析中，预期的缺失本身包含着极高的信息熵。正如前文边界说明所述，关于这一主题的结构化方法论在直接检索中存在数据稀疏现象，本部分基于相关框架进行逻辑推演。

### **6.1 ACH 框架中的“预期缺失”**

在 Richards Heuer 的竞争性假设分析中，明确要求将“未发现”作为独立的证据行记录到矩阵中。  
"Make a list of significant information – including evidence, assumptions, and the absence of things one would expect to see if a hypothesis were true."20

如果在某一特定的可行性假说下，必然会伴随产生某种公开的物理、资金或数据足迹，而系统执行了全域扫描后未发现此类足迹。这种“否定结果”不仅不是无用信息，反而构成了该特定假说下具有最高诊断价值（Diagnosticity）的证伪证据。工作流应设立“预期必然产物库”，专门用于监测其缺失。

### **6.2 数据空洞（Data Voids）的预警价值**

现代信息战和计算宣传研究引入了“数据空洞”概念，指代那些缺乏自然生成高质量内容的搜索空间。  
"...online searches to verify false news can paradoxically increase belief in it when search results return low-quality information ('data void' problem)."9

当系统在特定领域检索时，如果返回结果全部为空，或者全部被低质量、非权威、甚至SEO农场所占据，系统应当将此结果记录为一种“领域不成熟”或“易受操控”的元证据。在生成验收测试时，这意味着该需求的外部依赖环境高度不稳定。

## **7\. 专项回应：关于“何时可以停止收集信息”的可操作判据**

针对您提出的关键问题：“**何时可以停止收集信息这个判断，有没有可操作的判据？**” 以及您的洞见：“**证据集的完备性无法由证据集本身证明，而停止收集这个判断恰恰是整条链上唯一没有证据支撑的一环。**”  
从哲学认识论的根源来看，您的洞察极为精确。这在哲学上被称为**明希豪森三难困境（Münchhausen trilemma）**。德国哲学家 Hans Albert 在批评理性主义的绝对基础时指出，任何试图对知识进行彻底证成的企图，必定陷入三种绝境之一：无穷倒退（Infinite regress，即为理由寻找理由，永无止境）、循环论证（Circularity），或是武断的终止（Dogmatism，即在某一点上无理由地停止追问）35。  
"The basic statements at which we stop, which we decide to accept as satisfactory, and as sufficiently tested, have admittedly the character of dogmas, but only in so far as we may desist from justifying them by further arguments (or by further tests). But this kind of dogmatism is innocuous since, should the need arise, these statements can easily be tested further. I admit that this too makes the chain of deduction in principle infinite."35

由于“停止收集”必然是一种工程上的“武断终止”，它无法在封闭的证据集内部获得纯粹的逻辑证明。因此，在科学界、流行病学和情报学中，关于“何时停止”的判据并非追求绝对真理，而是基于概率极限、认知穷尽和经济学阈值的**复合操作指标（Operational Criteria）**。以下是从本研究语料中提炼出的三种跨学科可操作判据，它们可以被参数化并部署到您的人机协作工作流中。

### **判据一：统计概率学判据 —— 捕获-再捕获重合度（Capture-Recapture / Lincoln-Petersen）**

这是一种最初用于生态学估计野生动物种群规模，后被引入流行病学和信息检索中用于估计隐藏文献总量的数学模型。  
"Mark and recapture is a method commonly used in ecology to estimate an animal population's size where it is impractical to count every individual... Another major application for these methods is in epidemiology, where they are used to estimate the completeness of ascertainment of disease registers."38 "It is easy to estimate total frame size using the Lincoln-Petersen estimator... An intuitive derivation of the estimator follows from equating the proportions marked in the sample and the population, m/n \= M/N, which gives N \= Mn/m."39

**工程操作机制**：

> 1. 设定两个具有相互独立算法逻辑或检索空间（如 Agent A 搜索专利数据库，Agent B 搜索商业研报）的检索代理并行工作。  
> 2. 记录 Agent A 独立捕获的有效证据数（![][image1]），记录 Agent B 独立捕获的有效证据数（![][image2]）。  
> 3. 识别二者重合发现的相同证据数（![][image3]）。  
> 4. 实时计算潜在的总证据集规模预期 ![][image4]。  
> 5. **停止阈值**：当总已收集独立证据量 ![][image5] 除以计算出的总期望 ![][image6]，得到一个极高的覆盖率（例如达到 95%）时。此时，数学概率表明继续投入资源搜寻未知空间将面临极其陡峭的边际收益递减。

### **判据二：质性研究判据 —— 理论饱和（Theoretical Saturation）**

在社会学和系统扎根理论中，用来衡量是否需要抽取更多样本的标准。  
"In their original treatise on grounded theory, Glaser and Strauss (1967: p. 61\) defined saturation in these terms: The criterion for judging when to stop sampling the different groups pertinent to a category is the category's theoretical saturation."42

**工程操作机制**： 将检索和提炼定义为一个流式处理过程。工作流中的自然语言处理模块在解析新获取的文本时，持续从中提取“实体、因果关系、约束条件、参数指标”。**停止阈值**：定义一个观测窗口（如连续 50 份新文档）。当工作流在这 50 份文档中提取的内容，完全可以被映射回现有的知识分类树中，不再产生任何全新的“标签（Codes）”或“主题（Themes）”时，即宣布达到“理论饱和”。此时新的文档只提供冗余证明，不提供增量认知，应触发停止机制。

### **判据三：信息经济学判据 —— 预期信息增益（EIG）趋近零**

结合 Pirolli 的信息觅食理论（MVT）与决策分析中的预期信息价值（Expected Value of Information, EVOI）。  
"Like many Bayesian optimization and search algorithms, the selection of x\* requires approximating the expected information gain (EIG) across the space of possible..."43 "...decision analysis is determining the value that information has to a decision maker. The expected value of information (EVOI)..."6

**工程操作机制**： 在工作流为某一可行性判断建模时，维持一个对该结论的不确定性评估（如置信区间）。在发起下一轮深度网络抓取或 API 调用前，模型需要预判：即使获得最理想的支持或反驳数据，该新数据能否使当前结果的后验概率产生实质性的偏移，从而导致最终“验收测试标准”的结构发生改变？ **停止阈值**：如果预期的信息增益（EIG）逼近于零，或者其价值低于执行此次检索所需的计算/算力成本时，理性的决策是立即终止收集。  
**综合结论**： 为了解决这个“整条链上唯一没有证据支撑的一环”，建议将上述三个判据组成一个**联合逻辑门（AND/OR 门）**。完备性并不是一个本质主义的绝对状态，而是一个可度量的系统工程状态。当统计模型指示覆盖率达标、质性分析指示维度不再扩张，且信息经济学指示边际收益归零时，系统便有了最强有力的、可操作的理由，合法而“无害”地终止信息的挖掘，转入最终的知识固化阶段。

#### **Works cited**

> 1. The Design of Browsing and Berrypicking Techniques for the Online Search Interface \- UCLA School of Education & Information Studies, [https://pages.gseis.ucla.edu/faculty/bates/berrypicking.html?ref=blog.codinghorror.com](https://pages.gseis.ucla.edu/faculty/bates/berrypicking.html?ref=blog.codinghorror.com)  
> 2. The design of browsing and berrypicking techniques for the online search interface, [https://www.semanticscholar.org/paper/The-design-of-browsing-and-berrypicking-techniques-Bates/7952293fcb44e972f9d5546bcd4e265f1c3da3f8](https://www.semanticscholar.org/paper/The-design-of-browsing-and-berrypicking-techniques-Bates/7952293fcb44e972f9d5546bcd4e265f1c3da3f8)  
> 3. (PDF) Berrypicking in the real world: A wayfinding perspective on information behavior research \- ResearchGate, [https://www.researchgate.net/publication/227612554\_Berrypicking\_in\_the\_real\_world\_A\_wayfinding\_perspective\_on\_information\_behavior\_research](https://www.researchgate.net/publication/227612554_Berrypicking_in_the_real_world_A_wayfinding_perspective_on_information_behavior_research)  
> 4. Towards a methodology for cluster searching to provide conceptual and contextual “richness” for systematic reviews of complex interventions \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3819734/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3819734/)  
> 5. Baskets for Berrypicking \- Taxonomy Strategies, [https://taxonomystrategies.com/wp-content/uploads/2022/02/Busch-WIAD2021-Slides.pdf](https://taxonomystrategies.com/wp-content/uploads/2022/02/Busch-WIAD2021-Slides.pdf)  
> 6. (PDF) Information foraging theory: A framework for intelligence analysis \- ResearchGate, [https://www.researchgate.net/publication/294893031\_Information\_foraging\_theory\_A\_framework\_for\_intelligence\_analysis](https://www.researchgate.net/publication/294893031_Information_foraging_theory_A_framework_for_intelligence_analysis)  
> 7. Discretionary Task Interleaving : Journal of Experimental ... \- Ovid, [https://www.ovid.com/journals/jepge/fulltext/10.1037/0096-3445.136.3.370\~discretionary-task-interleaving-heuristics-for-time](https://www.ovid.com/journals/jepge/fulltext/10.1037/0096-3445.136.3.370~discretionary-task-interleaving-heuristics-for-time)  
> 8. awesome-dfir-skills/skills/analysis/admiralty-system-tr/SKILL.md at main \- GitHub, [https://github.com/tsale/awesome-dfir-skills/blob/main/skills/analysis/admiralty-system-tr/SKILL.md](https://github.com/tsale/awesome-dfir-skills/blob/main/skills/analysis/admiralty-system-tr/SKILL.md)  
> 9. Digital media and misinformation: An outlook on multidisciplinary strategies against manipulation \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8156576/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8156576/)  
> 10. June 2026 is, on the modal forecast \- EU Parliament Monitor, [https://euparliamentmonitor.com/news/2026-05-31-month-ahead-en.html](https://euparliamentmonitor.com/news/2026-05-31-month-ahead-en.html)  
> 11. SIFT: The Four Moves \- Mike Caulfield, [https://checkplease.neocities.org/older-projects/sift-method/](https://checkplease.neocities.org/older-projects/sift-method/)  
> 12. SIFT (The Four Moves) \- Hapgood, [https://hapgood.us/2019/06/19/sift-the-four-moves/](https://hapgood.us/2019/06/19/sift-the-four-moves/)  
> 13. Daubert standard \- Wikipedia, [https://en.wikipedia.org/wiki/Daubert\_standard](https://en.wikipedia.org/wiki/Daubert_standard)  
> 14. Daubert Standard | Wex | US Law | LII / Legal Information Institute, [https://www.law.cornell.edu/wex/daubert\_standard](https://www.law.cornell.edu/wex/daubert_standard)  
> 15. The Daubert Standard: A Guide to Expert Testimony, Motions, Hearings, and Rulings, [https://www.expertinstitute.com/resources/insights/the-daubert-standard-a-guide-to-motions-hearings-and-rulings/](https://www.expertinstitute.com/resources/insights/the-daubert-standard-a-guide-to-motions-hearings-and-rulings/)  
> 16. How Cognitive Bias Can Explain Post-Truth | The MIT Press Reader, [https://thereader.mitpress.mit.edu/how-cognitive-bias-can-explain-post-truth/](https://thereader.mitpress.mit.edu/how-cognitive-bias-can-explain-post-truth/)  
> 17. Stop Fooling Yourself\! (Diagnosing and Treating Confirmation Bias) \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11495861/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11495861/)  
> 18. Confirmation bias \- Wikipedia, [https://en.wikipedia.org/wiki/Confirmation\_bias](https://en.wikipedia.org/wiki/Confirmation_bias)  
> 19. You Are Not Listening | Product Design Psychology, [https://productdesignpsychology.com/10-you-are-not-listening/](https://productdesignpsychology.com/10-you-are-not-listening/)  
> 20. Past Editions Archives \- Page 7 of 8 \- Pherson, [https://pherson.org/source/past-editions/page/7/](https://pherson.org/source/past-editions/page/7/)  
> 21. Full article: Beyond Bias Minimization: Improving Intelligence with Optimization and Human Augmentation \- Taylor & Francis, [https://www.tandfonline.com/doi/full/10.1080/08850607.2023.2253120](https://www.tandfonline.com/doi/full/10.1080/08850607.2023.2253120)  
> 22. Tracing the Untraceable: Language Pattern Analysis, IP Attribution, and Decloaking Techniques in Fraud Investigation | by Brian James Curry | Jun, 2026 | Medium, [https://medium.com/@brian-curry-research/tracing-the-untraceable-language-pattern-analysis-ip-attribution-and-decloaking-techniques-in-27b03df651b4](https://medium.com/@brian-curry-research/tracing-the-untraceable-language-pattern-analysis-ip-attribution-and-decloaking-techniques-in-27b03df651b4)  
> 23. Psychology of Intelligence Analysis | PDF \- Scribd, [https://www.scribd.com/document/1015206261/Psychology-of-Intelligence-Analysis](https://www.scribd.com/document/1015206261/Psychology-of-Intelligence-Analysis)  
> 24. Analysis of competing hypotheses \- Wikipedia, [https://en.wikipedia.org/wiki/Analysis\_of\_competing\_hypotheses](https://en.wikipedia.org/wiki/Analysis_of_competing_hypotheses)  
> 25. Analysis of Competing Hypotheses using Subjective Logic, [https://www.mn.uio.no/ifi/english/people/aca/josang/publications/pj2005-iccrts.pdf](https://www.mn.uio.no/ifi/english/people/aca/josang/publications/pj2005-iccrts.pdf)  
> 26. Analytic Tradecraft in the U.S. Intelligence Community \- ScholarWorks, [https://scholarworks.waldenu.edu/cgi/viewcontent.cgi?article=5081\&context=dissertations](https://scholarworks.waldenu.edu/cgi/viewcontent.cgi?article=5081&context=dissertations)  
> 27. Full article: Towards a Reasonable Standard for Analysis: How Right, How Often on Which Issues? \- Taylor & Francis, [https://www.tandfonline.com/doi/full/10.1080/02684520802121190](https://www.tandfonline.com/doi/full/10.1080/02684520802121190)  
> 28. “Fixing Intel” or Fixing the Force? US Military Adaptation for Intelligence Requirements in Afghanistan White, Nathan \- King's College London Research Portal, [https://kclpure.kcl.ac.uk/ws/portalfiles/portal/311403405/2024\_White\_Nathan\_0742832\_ethesis.pdf](https://kclpure.kcl.ac.uk/ws/portalfiles/portal/311403405/2024_White_Nathan_0742832_ethesis.pdf)  
> 29. Strategic Intelligence for American World Policy 9781400879151 \- DOKUMEN.PUB, [https://dokumen.pub/strategic-intelligence-for-american-world-policy-9781400879151.html](https://dokumen.pub/strategic-intelligence-for-american-world-policy-9781400879151.html)  
> 30. Sherman Kent's Final Thoughts on Analyst-Policymaker Relations — Central Intelligence Agency \- CIA, [https://www.cia.gov/resources/csi/static/Kent-Final-Thoughts-Analyst-Policymaker-Relations.pdf](https://www.cia.gov/resources/csi/static/Kent-Final-Thoughts-Analyst-Policymaker-Relations.pdf)  
> 31. Inferential Reasoning in Criminal Evidence and Forensic Science. \- Royal Statistical Society, [https://rss.org.uk/RSS/media/File-library/Publications/rss-inferential-reasoning-criminal-evidence-forensic-science.pdf](https://rss.org.uk/RSS/media/File-library/Publications/rss-inferential-reasoning-criminal-evidence-forensic-science.pdf)  
> 32. PRISMA 2020 Checklist: 27 Items, Flow Diagram, and PRISMA-P | ScribeLabWriter, [https://www.scribelabwriter.com/blog/prisma-2020-checklist-guide](https://www.scribelabwriter.com/blog/prisma-2020-checklist-guide)  
> 33. (PDF) PRISMA-S: an extension to the PRISMA statement for reporting literature searches in systematic reviews \- ResearchGate, [https://www.researchgate.net/publication/353383363\_PRISMA-S\_an\_extension\_to\_the\_PRISMA\_statement\_for\_reporting\_literature\_searches\_in\_systematic\_reviews](https://www.researchgate.net/publication/353383363_PRISMA-S_an_extension_to_the_PRISMA_statement_for_reporting_literature_searches_in_systematic_reviews)  
> 34. Chapter 8: Domains Decreasing Certainty in the Evidence | ACIP GRADE Handbook \- CDC, [https://www.cdc.gov/acip-grade-handbook/hcp/chapter-8-domains-decreasing-certainty-in-the-evidence/index.html](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-8-domains-decreasing-certainty-in-the-evidence/index.html)  
> 35. The Foundations of Value, the Friesian Trilemma, [https://friesian.com/foundatn.htm](https://friesian.com/foundatn.htm)  
> 36. Gadamer's Repercussions \- UC Press E-Books Collection, [https://publishing.cdlib.org/ucpressebooks/public/book/gadamer-s-repercussions-reconsidering-philosophical-hermeneutics.html](https://publishing.cdlib.org/ucpressebooks/public/book/gadamer-s-repercussions-reconsidering-philosophical-hermeneutics.html)  
> 37. Problems and intuitions \- bonndoc, [https://bonndoc.ulb.uni-bonn.de/xmlui/bitstream/handle/20.500.11811/13446/8502.pdf?sequence=2\&isAllowed=y](https://bonndoc.ulb.uni-bonn.de/xmlui/bitstream/handle/20.500.11811/13446/8502.pdf?sequence=2&isAllowed=y)  
> 38. Mark and recapture \- Wikipedia, [https://en.wikipedia.org/wiki/Mark\_and\_recapture](https://en.wikipedia.org/wiki/Mark_and_recapture)  
> 39. PDF, [https://www150.statcan.gc.ca/n1/pub/12-001-x/1994002/article/14425-eng.pdf](https://www150.statcan.gc.ca/n1/pub/12-001-x/1994002/article/14425-eng.pdf)  
> 40. (PDF) The Petersen–Lincoln Estimator and its Extension to Estimate the Size of a Shared Population \- ResearchGate, [https://www.researchgate.net/publication/23642674\_The\_Petersen-Lincoln\_Estimator\_and\_its\_Extension\_to\_Estimate\_the\_Size\_of\_a\_Shared\_Population](https://www.researchgate.net/publication/23642674_The_Petersen-Lincoln_Estimator_and_its_Extension_to_Estimate_the_Size_of_a_Shared_Population)  
> 41. arXiv:1205.1150v3 \[math.ST\] 31 May 2013 Estimating Omissions from Searches, [https://arxiv.org/pdf/1205.1150](https://arxiv.org/pdf/1205.1150)  
> 42. [https://pmc.ncbi.nlm.nih.gov/articles/PMC5993836/\#:\~:text=In%20their%20original%20treatise%20on,is%20the%20category's%20theoretical%20saturation.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5993836/#:~:text=In%20their%20original%20treatise%20on,is%20the%20category's%20theoretical%20saturation.)  
> 43. Probabilistic prediction of material stability: integrating convex hulls into active learning \- The Royal Society of Chemistry, [https://pubs.rsc.org/mh/article/11/21/5381/855079/Probabilistic-prediction-of-material-stability](https://pubs.rsc.org/mh/article/11/21/5381/855079/Probabilistic-prediction-of-material-stability)  
> 44. (PDF) A decision tree model to estimate the value of information, [https://www.researchgate.net/publication/258154292\_A\_decision\_tree\_model\_to\_estimate\_the\_value\_of\_information\_provided\_by\_a\_groundwater\_quality\_monitoring\_network](https://www.researchgate.net/publication/258154292_A_decision_tree_model_to_estimate_the_value_of_information_provided_by_a_groundwater_quality_monitoring_network)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAaCAYAAACzdqxAAAABTElEQVR4Xu2ToUsEQRTGPxFBEQ4NciIWuSZXRMRoO4PBoMFyzXjxwvUL/gH3JxynQZOYNBmNFouKIGKR6xcE/b57O8zMyp5jMe0PfjAzb+ft7nszQMl/M02rdCVzNg7/YIYuwz8/FYc9SqQHXuiI3tD56ImYN/pFW7B9+rCJPNBTek+XcjHHGj2HJV7NxQrp0QYd0q1cTCjWp6+wxElUaJNuwDbtx+Exl7QOK5dM4pAuwl6gxCdxGJt0AdYPxa/icDEqg1DHtXEQxOboWTauweIdHy5mHdY4hzY+BXOVwDVKf/IYzCeiMtwFcyV+z8b6g6NsrDKoBPK3sz7mFtY4xwcsuS7NdbC+Rz9hpyMJlUGnwaEyKHGXtoN1lSH5/Oo6qlHhtbyAJdgJ1kTS+VWiA1i3n+kx/NXUCVEC9zJ94S6sDFrfhpWppKTkL3wDZKU75lXSxfgAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAAAwElEQVR4XmNgGAVDGvAAsTsQs0L5zECsAsROQMwBUwQDjEDcygBR/B+ItwGxC1TcE4h/ALEwXDUQyACxLgPEJJCGF0hypkD8FoilkMTgVtoB8SMgVkaSq2CAGMKNJAYHIMndDKiS2xkgGjAAyP1rgLgdTRzkvI9oYmAAcs5nBlTnCDBATM+Dip9FkmMohkryIokZMkA8DPI4SNNyJDmG40D8FVmAAeJMUJCCAsIbTY5BGohl0QWBQJABLUhHweAAAI3DHNqpyYkPAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAAA90lEQVR4Xu2QPwvBURSGr6SUlJIolPIlTCYpWSxKyhcwmH0ByQew2yxGWQySWZHRZreYDIr3vX9+na7VYLhPPf3ynnuvc45SgcAfcoQHuIUZeIZX+IB3GIM9eIJ7+63wooSHJjAO33ADGzZvwSecwZ27YM8txG9NG6ZhCb7gUNSayjxUExnhQ2svU0n7rcMbrIraWJlLKZElbDYVWQSLK/Vd5J7YpaQPL7Dg5RqOxUsdL+dY7NLBP1zCuTI7zCmz2wg3Anfl4Mj+CAOb8QE+OhI1DcfiAQm7ZEdcuIMdc1R20YV5UdMUYdnL2HrWywgf4X7YUSDwUz5suiu4T5SwYQAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAAAaCAYAAABVc6VBAAAFDElEQVR4Xu2aXaimUxTH/5Ii5HPyeSFSRlwa01y4cDFSU1z4qKm5cOGC4oYiuTJJuZULI3WGNIVcSE0IE6XxkXzVjHxNSEqUpIgy+3fWu3r3s9rP15tznjPv7F+tes/e7/Oc/bHWf629z5EqlUqlUqkc45yZ7P7YuKRclOxgshNiRw87kz0XG9eTk5NdmNmJze7Vn88LbVOCU72R7KTYMSOfy1mhL8Jm+XfPV/s7p+baZLfGxh5eSnZvbFxPTpct7HfJ/kv2nmzzHHesI8l+TXaJ7JmpYAzbY+MMxspcXkz2b7Jfmt0NLk/2qWzOL8ieI8g2Kq/IlGsoONaGCJRDMqf6K9mNoQ/eSvZgbFxncPD9yU6JHRmnyhQNB2QubTydbI/MsW4JfRsRgunP2NgCgU8qnBw8G6dBqVjon5vdq3wuSxdTgTPhVJfGjgAb8JHmalQCB90si2oCZkoFHgN7NMRhHtP4mmxN2KR5emEzShsytbReI1OhvjE8LBsrqlWaBwu+WzZnnO+JZncnt6l7w0iva+mk1yXbp+41IPg/jo1TcZfmg31EtiF5ZFwsm9SUPKOyo0S+kI0VB+P7sYCn/toqmzP9Vza7e/kq2QOxMXFY5fYSrPVnyb6WFeZny7IEivxPssfnX21Amie4CLI2VmSKlUMwfCnLOhwCUH/qT9SaWpQ1uSDZy7Ix/Cg7dXcFUS9Mkgh3rtZ8kl7LoGZE+BDiKbPPSEvxJFoCBfotNhYgDTLWXTLHIShyUCsWjDnTP1ZhtsgWPl90nBOnGroRrOc5sjGimh9ovtZsflctxZhvio0ZPL8ttF0lU1Oc+Eiyt5OdMetjn3EuVO7OWdtl6nfgXohuJpdD8c4EnpQ5yqvN7kkgurEuGOt9s8+eOn0TCKCnZp/hD9mCLgrOhTONUSrA6d+ROeGK7LSXH0a6akOgr+0QxfzjFQMq99rsM899oub1EXvLO/P0SjBy8Gk7fQ+ClJArFngR/63Me1m8qRniWHnK5jPjZ35ws5qOxfx+yn4eiyvXQxqmuA7fPVeWot+XqVYOwdB1TdLlWGQbLAcHJtV6ZoppktQeA4w1/F629wuDdJY8k01hEnuTPR/6pmCIY1FXeeT5tcOzssW9278kK3CZ25jCPbKoYjmeqvMaEOWijTq3jTbHQgzejY0ZOAsqHZ2F91FrObyHa6eofKNBemMdAqRBfunfmkf9EFCGb0bYh8muWH2yG8bZpTCllI1TsWg71KylWGSilLEuAmrlNRX1Fc41tL5yVmTrmz+H2vwuq5EYb6n+4xlP9zk8g0i0gTPybP5O1oy2XMV4D2Nw5SuNoRcihCgvQeRztGVDhxbua0nfqRAniYrmqvBo1uYpYdH7q//jVAikO9Ke4wrrasQhJN7ZdZ0KKb6pjdsopTwyVUx5pGdfZ5wMdR8Mef52WVGHatwxa4swUNLg2GhcC/x6IIJzXC9bcE5TnHz8TzMsnBerzIHa5h7ZqfdAshuy7w4BdWo7ho9VLubCJjquuBw2SEelUyab3BbofhpugzSIE+XgxPzOfA0IOBSLMbyetS8tnvtjFB+rbFb5opMrmHj35uAIpfTNmsQrhghXDjGITlNZUAjWtjEsJRSUO2PjcQKbjZrkVwUOa7JIWq9kIOmlU+yyw33XgdgoS8FdRXtlIPxXwsHYeBzwg6x+jKDi8R6ysiDUW/U/SI03Vb4uqlQqlUqlUqksAUcBFvkIxGFmNmkAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHcAAAAaCAYAAACNU8MOAAADx0lEQVR4Xu2aTahNURTHl6TI97d81PMx8DlAKAMmIikMGDIyYWBCYUhJmcnAQOpFKEmJKCZPihAxUTxJigEZGChFsX5vnd3dd3Xvuffsd997Pvav/r371j7nnn322mvttfd7IplMJpP5C3iiWumNmSFhtOqGarhvSGGNaqc3FkxXzYzUihlSu3aKa8u0T5fqkGqYs1firOq5N0bgpOWq76pfYrOqGbvFruFa7mNiZNI5pXrnjVX4ptrvjQ6ce0nMcVNdW2Cu6rbYNW9dWxXGe8N/zFLVB9UI39AOy1SXpfXNp1UbxSJylWsLXFAtEnPuYddWhf7c+y+yXXXMG9uBgdzljY5xqnti0ftZta2+uY/JYrMsTAB+ppKdW8981QPVBN9QBoXPK2ldJO1QPZKak0/UN/dV2NdUI1U3C/E5lVTnPlXdV90VG4gXql6xpeKTakvt0gFnteq16odYTbNVbO3sEVsGV4hlS4Lloeqn6pY0h2zYKKiaEiIRp5VBSkZ05qrqotRXcKT19WIz7L2kOyeQcj/9OS7WRwaCgdpQ2IFs8qz4PBhcFysuCQaeTeQtKdqobwiGbqnVF4wr/W5G5aWOmVD2hYGXYhMBeMAbqUU7RdTs4jMRzfeF31Op9BIFLANjxZ5NFOyrb+4bYPo9WHSLTawvYpEas1csYzJ2AQKmzBe0nffGMtp1Lil5YvGZFP1RtVgsSojoAOmY72s3JZ8RS1lejxvY0DS7rSHhmevEsgdZJIZ+ka7LYGL4ZzYTdUrZ/pOJBjyX8QtwT7fqXGQDrinzxYA4l5QdF1xEcMj/d8SKqAARQ4T0l5TIhbBs+JqAHcFX1VpnH2gICMYqHj92GkSz33FwHbVBMyo7N1S2ZZFGhIaUDKRjHnREdTCyA/ZeZ0sh1blEHs9n6xDDGheqzUnSetvXKRo5kpTMOIVMCPQLG/3EF41O9Wj30V5Kq2o5pJA4/YSChUiIIQ1iT3VMTOp3HBDrQ0iJEIrGMMDt7Ok7QRg7FI8fFbzPlmSasMPoUW2uazVCtmybsHXhXDmGzswSGwhS7R7VgqidB3EsBgzUJrG1F/tJsSPH/hx4pzq3UcVJ5qFGYALznv5dBwoik3XUnyEQyfQnhvc9KjbuVNmj6pv7jntDnVMJ1qHBms3tkupcJuQcbyzAuWXLT6fBUXE1HFioGuONYlm02Tk8y0zSmDBLOAee5xuGkKQX+UcJ6T0uXCtxRcr/KpQZOlj+qIuS6RI7qCjbt2WGhg/S/O/slcj/ifHn0NH/xMhkMplMJtN5fgM7m8Jpr/tVVQAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABDElEQVR4Xu2TsY4BURSGf5FNKCQaIaLSewWlxAvYWqlRK1TewSNstlFqvIBKIyS7za5Wo1dI+H8Hc+fGuBKVZL7kL+acM/89554ZIOVVclTVUTaePlOG1QUpwEw21JGaU8VYhZl1qB3Vh73zkB+Y0Z5qezkhg4EfvMcHrFAdqbst1YhVAC2q4sXuUoIVC5lJoyh9Zgg7NEgPUaFMZHaI0qhRa+c5EZlMnGeNpzFlmL/E1PXiVvGAJrX0YlqAFjGmMtQU1n0QFbmdCS1Cm/2n6tQv7NAgK0SX7yITjar8F6zDIBpRF+yjl6+LeGpEXbBWnsQ3zFCfTiL6/z6pGfVHdS8xn+sinhoxJeUtOAEshCuBmUQ8xAAAAABJRU5ErkJggg==>