# **苏格拉底式数学教学引擎系统级评估框架：防范“知识诅咒”与“超纲幻觉”的认知科学准则**

## **绪论：大型语言模型的全知视角与建构主义教学的认知冲突**

在智能教学系统（Intelligent Tutoring Systems, ITS）的架构演进中，大型语言模型（LLM）的引入带来了一场深刻的范式革命。然而，当 LLM 被应用于诸如纯数学这样具有高度严密拓扑结构的学科时，其底层的自回归生成机制与人类的认知发展规律之间，产生了一种根本性的认识论冲突 1。大型语言模型在海量预训练数据中习得了全局的、高度压缩的知识流形。从计算语言学的角度来看，模型倾向于在生成时调用信息熵最低、压缩率最高的术语来完成词元的预测。这种“全知视角”在对话式教学中直接导致了严重的“知识诅咒（Curse of Knowledge）”现象。  
建构主义教育心理学指出，人类的认知发展并非信息的瞬间下载，而是一个依赖于“最近发展区（Zone of Proximal Development, ZPD）”的渐进式支架搭建过程 3。当教学引擎旨在引导学生理解拓扑学《数学知识路线图》中的特定目标节点 ![][image1] 时，必须严格遵循“知识降维原则”。如果 LLM 在解释基础概念时，其注意力机制（Attention Mechanism）受到高阶术语高频共现的概率吸引，从而在上下文中无意泄露了 ![][image2] 乃至 ![][image3] 的概念，这不仅无法提供有效的认知支架，反而会瞬间摧毁初学者的认知体系。例如，在基于集合论基础（n\_6）讲解映射与关系（n\_11 至 n\_16）时，若模型提前引入了商集（n\_19）或势的严格比较（n\_22），将会导致严重的“跨维度词汇泄露” 5。  
为了彻底在系统层级规避这种“超纲幻觉”，并将大型语言模型的生成轨迹牢牢锁定在当前学生的认知天花板（Curriculum Ceiling）之下，本报告出具了一份详尽的、融合了认知科学与纯数学结构的输出质量评估框架。该框架依托于底层的 JSON 【内审草稿】 机制，通过强制思维链（Chain-of-Thought, CoT）寄存器进行生成前的知识边界自检，建立起一套针对数学 AI 教学超纲隔离与知识降维的系统化评估准则。该准则不仅作为质量保证（QA）的基准，更将直接作为后续直接偏好优化（Direct Preference Optimization, DPO）和底层 Prompt 逆向对齐调优的理论依据 2。

## **模块一：知识隔离度评估矩阵 (Curriculum Ceiling Isolation Metrics)**

知识隔离的核心前提是：一个教学解释的教育学有效性，与其对未解锁拓扑节点或未来概念的依赖程度成反比。为了精准量化“知识降维的合法性”，本框架提炼了四个核心系统级指标。每一个指标都旨在从词汇、逻辑依赖、认知阶梯和隐喻结构四个维度，对大模型的输出进行无死角的切片检查。这些指标将由判别模型或人工专家在后续的系统强化学习阶段给出量化打分。

### **1.1 术语降级纯净度 (Terminological Downgrade Purity)**

该指标旨在衡量大模型在阐述目标节点 ![][image1] 时，能否将其内部表征的高阶数学概念，安全、彻底地退化为学生当前已掌握的自然语言或已解锁的基础词汇库。数学语言具有极强的压缩性，高阶术语本质上是对低阶属性的打包。模型往往难以抑制使用高阶术语的冲动，因为这在统计上是最“准确”和“高效”的表达方式。术语降级纯净度评估的核心在于，模型是否展现出了在不丧失数学严谨性的前提下，对复杂概念进行“解包（Unpacking）”的能力。  
在拓扑网络中，如果目标节点是“分配格与有界格（n\_32）”，模型自然可以使用格论术语；但如果目标节点仅仅是“集合运算的代数定律（n\_9）”，模型在解释交集对并集的分配律时，就绝不可以使用“分配格”或“布尔代数”这样的上位词汇 5。任何显式或隐式的跨维度术语借用，都会对学习者造成认知超载。

| 评分 | 降级纯净度特征定义 | 拓扑学路线图具体映射示例 |
| :---- | :---- | :---- |
| **5** | **绝对纯净与完美解包**：解释过程中实现了 100% 的基础词汇合规。模型完全摒弃了对未来节点的概念依赖，仅使用纯粹的自然语言或严格锁定在 ![][image4] 范围内的已知数学符号，且保持了逻辑的严密性。 | 在讲解“单射、满射与双射（n\_16）”时，仅使用“笛卡尔积（n\_11）”中的有序对和简单的现实分配隐喻进行推导，全程未出现“同构”、“核（Kernel）”等高维术语 5。 |
| **4** | **高度纯净但有形式化冗余**：没有使用任何属于未来节点的专有名词，但模型保留了一些对当前阶段而言略显生硬的抽象符号或形式化表达。词汇合规，但降维的“自然感”略有欠缺。 | 使用严密的谓词逻辑公式 ![][image5] 来解释单射，虽然工具库（pred\_1 至 pred\_6）已解锁，但缺乏进一步的通俗化降级 5。 |
| **3** | **边界合规与隐式泄露**：模型没有直接抛出违禁的高阶名词，但其句法结构和论述逻辑强烈暗示了 ![][image2] 节点的理论框架。认知负担加重，但尚未直接破坏当前教学节点的闭环。 | 在讲解“等势（n\_21）”时，没有使用“基数（Cardinality, n\_22）”一词，但通过语句暗示了集合之间存在一种“可以比较大小的绝对数值”，提前透支了后续概念 5。 |
| **2** | **轻度污染与防御性修补**：模型在解释中顺嘴说出了 1-2 个明确属于高阶节点的术语，随后立刻意识到超纲，并试图用大段文字去“解释这个超纲词汇”，导致教学焦点涣散，徒增认知负荷。 | 在讲解“数学归纳法（n\_4）”时，为了显得严谨，顺嘴提到了“良序集（n\_25）”，然后被迫花两段话去解释什么是良序集，严重偏离了目标节点 5。 |
| **1** | **严重污染与维度坍塌**：模型大量堆砌未来节点的专业术语。讲解文本看起来像是大学教材的直接切片，而非面向初学者的苏格拉底式降维引导。完全丧失了教学引擎的定位。 | 使用“布尔格的同构”来向初学者证明“命题逻辑的等价性（prop\_2\_truth\_tables）” 5。 |
| **0** | **知识合法性丧失（循环定义）**：模型不仅使用了高阶术语，甚至将高阶术语作为定义当前低阶概念的核心基石，导致在局部拓扑网络中形成逻辑死循环。 | 试图通过 ZFC 公理系统中的“幂集公理（n\_34）”来给初学者定义什么是“子集（n\_6）” 5。 |

### **1.2 先决依赖合规性 (Prerequisite Dependency Compliance)**

数学是一门建立在严格公理演绎基础上的学科。当 AI 教学引擎引导学生证明一个定理或推导一个概念时，其所使用的每一个公理、引理和推理规则，都必须是以往节点中已经严格建立的“工具”。先决依赖合规性评估的是模型在构建逻辑思维链时，是否 100% 只调用了 ![][image6] 集合中的合法推导工具。  
在传统的提示词工程中，模型往往倾向于寻找“最短证明路径”。然而，在教学体系中，最短路径往往依赖于极其强大的高级定理（例如用微积分证明几何面积，或用拓扑学定理证明实数性质）。如果学生正处于“命题逻辑（prop\_1 到 prop\_6）”阶段，模型绝不能使用“谓词逻辑（pred\_1 到 pred\_6）”的量化规则去进行降维打击式证明 5。这种工具的越级使用不仅违背了循序渐进的教育规律，更剥夺了学生通过基础工具进行艰苦但必要的认知建构过程。

| 评分 | 依赖合规性特征定义 | 拓扑学路线图具体映射示例 |
| :---- | :---- | :---- |
| **5** | **严密的线性推导**：逻辑链条完全闭合于已解锁节点。模型能够克制使用高级定理的冲动，耐心地使用基础公理一步步推导，其推导的细粒度与当前拓扑位置完美契合。 | 仅使用“真值表（prop\_2）”或“逆否等价原理”来向学生证明“逆否命题的有效性（n\_2）”，没有借助任何未解锁的自然演绎系统复杂规则 5。 |
| **4** | **次优但合法的工具选择**：推导过程完全合法，但模型选择了一个在当前已解锁集合中相对繁琐的工具，没有找到最直接的先决依赖。虽不超纲，但路径非最优。 | 在证明集合的分配律（n\_9）时，没有直接利用命题逻辑的分配律（prop\_4）进行同构映射，而是让学生通过繁琐的文氏图（n\_10）进行穷举证明 5。 |
| **3** | **隐式步骤跨越**：模型在推导过程中跳过了关键的基础步骤，其底层逻辑实际上是调用了一个尚未证明的高阶定理作为“隐蔽捷径”，虽然表面上没有提及该定理的名称。 | 从集合的基本概念（n\_6）直接跨越到集合的代数定律（n\_9），在此过程中完全省略了集合核心运算（并集、交集，n\_7）的严密推导过程 5。 |
| **2** | **轻微的时间线违规**：在证明的某个次要分支中，模型为了图方便，直接使用了一个刚刚越界（如 ![][image2]）的推导规则，破坏了当前知识节点的独立攻坚体验。 | 当学生还在学习“量词的否定与转换定律（pred\_4）”时，模型在引导中使用了“全称例示（UI）”等一阶逻辑推理规则（pred\_6）来简化问题 5。 |
| **1** | **严重的逻辑倒置**：推导过程严重依赖于那些在本节点之后才会被推导出来的定理。这种操作实际上是利用了结论来证明前提。 | 试图利用“康托尔-伯恩斯坦-施罗德定理（n\_23）”来向学生证明基础的“基数比较原则（n\_22）”，产生了严重的逻辑倒置 5。 |
| **0** | **跨范式的降维打击**：模型引入了完全不属于当前数学分支体系（或远远超出当前认知图谱几十个节点）的超级定理来解决初阶离散数学问题，导致演绎体系崩溃。 | 试图使用实分析中的极限理论来解释“有限集与无穷集（n\_24）”的基础定义，完全无视了基数理论的本体论基础 5。 |

### **1.3 认知脚手架契合度 (Epistemological Scaffolding Alignment)**

根据维果茨基（Vygotsky）的社会文化理论与最近发展区（ZPD）概念，以及布鲁纳（Bruner）的支架式教学（Scaffolding）理论，教学互动的核心在于提供恰到好处的支持，使学习者能够跨越从已知到未知的认知鸿沟 3。即使 LLM 的输出在词汇上通过了 1.1 的考核，在逻辑上通过了 1.2 的考核，但如果它在对话中要求学生进行的“认知跳跃步幅（Step Size）”过大，同样会构成教学事故。  
这一指标评估模型在苏格拉底式提问中，是否能够将复杂的数学推导拆解为适合学生当前认知发展阶段的微小步骤。例如，从皮亚杰（Piaget）的“具体运算阶段（Concrete Operational）”过渡到“形式运算阶段（Formal Operational）”需要极度精细的铺垫 6。理查德·斯肯普（Richard Skemp）在其关于关系性理解（Relational Understanding）与工具性理解（Instrumental Understanding）的论述中指出，只有当认知阶梯足够平滑，学生才能建立关系性理解，否则只能退化为死记硬背的工具性记忆 4。

| 评分 | 认知脚手架特征定义 | 拓扑学路线图具体映射示例 |
| :---- | :---- | :---- |
| **5** | **完美的 ZPD 动态适配**：提问的步幅经过精确计算。模型能够设计单变量的启发式问题，引导学生通过自身的逻辑推理跨越 ![][image4] 到 ![][image1] 的认知间隙，挫折感与成就感达到最佳平衡。 | 在引导学生从“等价关系（n\_17）”过渡到“等价类（n\_18）”时，先让学生对一个具体的小集合按某种关系进行物理分组，然后才抽象出代表元的概念 5。 |
| **4** | **充足但略显粗糙的支架**：逻辑拆解基本到位，但某些步骤的跨度略大，学生可能需要进行较长时间的思考才能跟上，不过认知距离依然在可跨越的合理范围内。 | 在学习了绝对补集（n\_7）后，模型抛出一个结构较复杂的例子，要求学生直接定义“全集（Universal Set）”的边界条件 5。 |
| **3** | **梯度不均的认知阶梯**：模型的引导呈现出断裂感。某些问题过于弱智（甚至退化为填空题），而紧接着的下一个问题又需要巨大的直觉跳跃。支架存在，但结构不稳固。 | 在“空集（n\_6）”的属性上耗费了 5 轮低质量对话，随后突然要求学生在没有过渡的情况下推导出幂集的基数公式 5。 |
| **2** | **过度抽象的认知强加**：虽然没有违规使用术语，但模型要求学生在没有任何具体实例（Concrete/Pictorial）支撑的情况下，直接进行高度抽象（Abstract）的形式化推演 4。 | 在学生尚未掌握简单的文氏图（n\_10）分析前，就要求学生利用双向子集包含法严格证明两个复杂集合表达式的相等性（n\_6） 5。 |
| **1** | **支架坍塌与逆向工程**：模型实际上放弃了苏格拉底式提问。它直接给出了高深晦涩的结论，然后要求学生在缺乏任何中间路标的情况下，反向推导出整个定理的证明。 | 直接抛出题目：“已知良基关系的定义，请证明不存在无限递降链。现在开始你的证明。”（n\_5），没有提供任何关于极小元性质的暗示 5。 |
| **0** | **完全的认知脱节**：回复是一长串毫无停顿、没有互动的文本块（Text Wall）。这完全退化为传统教科书的填鸭式复制粘贴，彻底丧失了交互式认知脚手架的功能。 | 在讲解 ZFC 公理系统（n\_34）时，直接一次性打印出八大公理的形式化定义，没有任何互动与解释 5。 |

### **1.4 同构隐喻的降维匹配度 (Isomorphic Metaphor Backward-Compatibility Check)**

认知语言学家乔治·莱考夫（George Lakoff）与拉斐尔·努涅斯（Rafael Núñez）在《数学来自何处（Where Mathematics Comes From）》一书中提出，数学并非存在于某种柏拉图式的理念世界中，而是人类具身认知（Embodied Mind）的产物。人类对抽象数学概念的理解，绝大多数依赖于深层的潜意识“概念隐喻（Conceptual Metaphors）” 7。  
当 LLM 试图降低知识维度时，最常用的策略就是引入现实世界的隐喻。然而，大模型极易生成具有逻辑瑕疵的隐喻。一个合格的数学隐喻必须是“同构的（Isomorphic）”，即隐喻的源域（现实世界）必须与目标域（数学概念）在逻辑结构上完美映射。如果源域包含了目标域没有的属性，会产生干扰性的“盈余意义（Surplus Meaning）”；如果源域缺失了关键属性，则产生“赤字意义（Deficit Meaning）” 9。

| 评分 | 同构隐喻匹配度特征定义 | 拓扑学路线图具体映射示例 |
| :---- | :---- | :---- |
| **5** | **完美的结构同构**：隐喻的源域与数学目标域实现 1:1 的完美映射。现实物理实体的运作规律严格契合数学算子的定义，没有引入任何会引起误解的附加属性。 | 使用“家族族谱图（祖先/后代关系）”来完美映射“偏序集（Posets, n\_27）”中的自反、反对称和传递属性 5。 |
| **4** | **强映射伴随明确边界**：隐喻非常直观有效，但模型主动指出了隐喻在极端情况下的局限性，以此防御学生产生“盈余意义”的误解，展现出极高的教学素养。 | 使用“俄罗斯套娃”来解释真子集（n\_6），但模型主动澄清：“不同于套娃，一个集合内部可以同时包含多个互不包含的子集” 5。 |
| **3** | **部分同构与微小摩擦**：隐喻在解释当前微观概念时是通顺的，但如果学生顺着隐喻的逻辑稍微往前推演一步，就会发现物理规律与数学规律发生了冲突。 | 用“硬币的正反面”来解释命题逻辑中的重言式和矛盾式（prop\_3）——这个隐喻无法涵盖非真非假的偶然式（Contingency）情况 5。 |
| **2** | **盈余意义严重干扰**：隐喻引入了源域中非常强烈的物理属性，而这些属性直接违反了数学目标域的公理，导致学生建立起完全错误的直觉。 | 将笛卡尔积（n\_11）解释为“将两种颜色的颜料混合”。（颜料混合满足交换律，但笛卡尔积通常不满足交换律 ![][image7]） 5。 |
| **1** | **结构性错位**：源域的底层运作逻辑与目标域完全不同。模型只是抓住了某些表面的文字相似性，但在概念的拓扑结构上发生了灾难性的偏离。 | 试图将“空集（n\_6）”解释为“数字 0”。（混淆了作为容器的集合本身与集合基数的算术概念） 5。 |
| **0** | **隐喻幻觉与认知毒性**：隐喻完全不知所云，不仅未能降低维度，反而引入了比原数学概念更难以理解的复杂概念，导致认知的全面混乱。 | 为了解释谓词逻辑中的合式公式（WFF, pred\_3），模型虚构了一个关于“蝴蝶生命周期”的不知所云的隐喻 5。 |

## **模块二：知识越界的一票否决红线 (Out-of-Bounds Veto Triggers)**

上述四大评估矩阵提供了细粒度的质量评价体系，但大模型由于其底层自回归特性，有时会产生对学习者认知图谱具有毁灭性打击的结构性错误。基于上述背景，本框架设定了 5 条绝对红线。在实际业务流程或单元测试中，一旦系统检测到模型触发了以下任何一条红线，不予评分，直接判定为“严重教学事故（QA FAIL）”，并触发系统的硬拦截与重新生成机制。

### **触发红线 1：显性未来节点词汇的强行泄露 (Explicit Lexical Leakage from Future Topological Nodes)**

* **触发机制**：大模型生成的输出文本中，出现了一个或多个存在于受限词汇表（即拓扑网络中定义为 ![][image8] 的节点概念名词）中的精确匹配词汇或强同义词。  
* **认知毁灭性后果**：皮亚杰的认知发展阶段论指出，同化（Assimilation）和顺应（Accommodation）必须建立在已有的图式（Schema）之上 6。向学生抛出一个他们脑海中完全没有任何图式支撑的专业术语，会瞬间撕裂苏格拉底式的探索错觉。这会迫使学生放弃“建构理解”，退化到“对未知符号的死记硬背”，从而阻断深层思维。  
* **拓扑学事故示例**：系统当前在引导小学生理解映射的严格定义（n\_15）。大模型在回答中说：“既然我们已经把每一个 ![][image9] 唯一地映射到了 ![][image10]，你可以看出这与它们集合的基数（Cardinality）有关。” 在路线图上，“基数（n\_21）”是在等价关系之后、相隔六个节点的高阶概念 5。该响应必须被立刻判定为 FAIL 并重采样。

### **触发红线 2：高阶工具降维打击导致的逻辑循环 (Dimensionality-Breaking Circular Logic via High-Order Tooling)**

* **触发机制**：大模型使用了一个在拓扑层级上属于高维度领域的定理、引理或公理，去证明一个基础概念。而荒谬的是，这个高阶定理本身的证明，在数学体系中恰恰依赖于这个基础概念。  
* **认知毁灭性后果**：这不仅破坏了教学顺序，更在根本上摧毁了数学这门学科的公理化基础。如果学生接受了这种“衔尾蛇式”的循环证明，他们的整个理性逻辑演绎框架将被彻底污染。这种错误是 LLM 权重中概念距离被扁平化后的典型症状。  
* **拓扑学事故示例**：学生在学习“空集的属性（n\_6）”时，对“空集的幂集包含一个元素（空集本身）”感到困惑。LLM 为了强行解释，竟然引入了“冯·诺伊曼基数赋值理论（n\_22）”或“康托尔定理（n\_22）”来证明幂集基数严格大于原集合基数 5。然而，基数理论是建立在幂集概念之上的。用基数定理来证明幂集的基础属性，属于灾难性的逻辑死循环。

### **触发红线 3：公理化危机的过早引入 (Premature Leakage of Axiomatic Crises)**

* **触发机制**：在学生尚未完全掌握基础的、直观的古典理论或“朴素理论”之前，模型过早地向学生暴露该理论体系的边界危机、悖论，或强行引入为了修复这些悖论而发明的现代严密公理约束。  
* **认知毁灭性后果**：在数学史中，朴素集合论在引发公理化危机之前，支撑了数学家几十年的研究。在个体认知发生学中，学生必须首先建立起将集合视为“对象的聚集”的强大直觉，然后才能理解为什么要加以限制。过早引入危机，会破坏学生建立直觉图式的信心。  
* **拓扑学事故示例**：在初学者刚刚接触“集合的基本概念（n\_6）”时，好奇地提问：“有没有一个集合包含了所有的东西？” 大模型不但没有通过“全集（n\_7，特定语境下的最大集合）”来解答，反而立刻开始大谈特谈“罗素悖论（Russell's Paradox, n\_33）”，并引入 ZFC 系统中的“正规公理（Axiom of Regularity, n\_34）”来证明不存在包含自身的集合 5。这种炫技式的回答会直接击碎初学者的朴素认知，必须被一票否决。

### **触发红线 4：隐喻目标域的灾难性超载 (Metaphorical Target Domain Overload)**

* **触发机制**：大模型在尝试解释数学概念时，使用了一个不仅超出了学生当前生活阅历，甚至比当前正在学习的数学概念本身还要高深复杂的物理、科学或社会隐喻。  
* **认知毁灭性后果**：隐喻的教育学价值在于“降维”——用已知去锚定未知 9。如果作为“已知”的源域实际上比“未知”的目标域拥有更高的认知门槛，那么这种隐喻实质上是在进行“升维惩罚”。这不仅徒增认知负荷，更是 AI 模型在跨域注意力映射时产生的语义幻觉。  
* **拓扑学事故示例**：为了向中学生解释“等价类如何将集合划分为两两不交的部分（n\_18, n\_20）” 5，大模型动用了量子力学的隐喻：“这就像量子波函数坍缩成一组相互正交的本征态，它们共同构成了整个希尔伯特空间。” 源域（量子力学）的复杂性无限大，而目标域仅仅是简单的等价划分。这种伪装成隐喻的知识显摆必须触发红线。

### **触发红线 5：认知状态的强制覆写与武断预判 (Epistemological State Overwrite)**

* **触发机制**：大模型在未经过任何苏格拉底式提问或确认的情况下，武断地假设学生已经掌握了某个并未在已解锁节点列表（unlocked\_nodes\_subset）中的知识，并在句法中使用“既然你已经知道 X……”或“显而易见，根据 Y……”的句式。  
* **认知毁灭性后果**：苏格拉底式引擎的灵魂在于基于约束的学生建模（Constraint-Based Modeling, CBM）1。强行预判不仅破坏了 CBM 的准确性，还会给学生带来极大的挫败感（“我根本不知道这个，AI 却说显而易见”）。这会导致整个动态支架系统的拓扑结构脱轨。

## **模块三：隐喻的“逆向查毒”机制 (Metaphor Backward-Compatibility Check)**

大型语言模型在缺乏约束时，倾向于将高度复杂的自然科学现象与数学理论进行连接。为了确保隐喻符合学习者当前的认知阅历和世俗经验，我们设计了一套名为“逆向查毒（Backward-Compatibility Check）”的机制。该机制融合了莱考夫和努涅斯的概念隐喻理论 7 以及皮亚杰的认知发展阶段论 6，旨在客观审核隐喻源域的合法性。

### **3.1 理论框架：奠基隐喻与连接隐喻的严格区分**

莱考夫和努涅斯在《数学的认知科学》中将隐喻严格区分为两类 8：

1. **奠基隐喻（Grounding Metaphors）**：将最基本的数学概念与人类肉体的感觉运动经验（如空间移动、收集物品、堆叠容器）直接相连。它们使得基础心智得以延展。  
2. **连接隐喻（Linking Metaphors）**：将数学的一个抽象分支映射到另一个抽象分支（例如布尔隐喻将算术与逻辑类连接）。

**审查原则**：当系统讲解拓扑图谱中的《第一层：基础工具》（如集合论 n\_6 到 n\_10，命题逻辑 prop\_1 到 prop\_6）时 5，**严禁模型使用任何“连接隐喻”或跨学科的高级科学隐喻**。必须强制大模型退回到仅使用“奠基隐喻”，即将源域严格限制在人类普遍的具身经验中。

### **3.2 隐喻逆向查毒的三阶审查算法**

在底层系统中，我们采用以下三个阶段对 LLM 生成的隐喻进行系统化查毒。

#### **第一阶：源域提取与皮亚杰本体论定级 (Source Domain Extraction & Piagetian Triage)**

审查系统首先通过语义解析器提取出隐喻的源域实体，并将其与皮亚杰的认知发展四个阶段进行本体论比对定级 3：

* **感知运动级（Sensorimotor, 0-2岁经验）**：容器进出、物体组合、路径移动。（合法性：最高。适用于 n\_6 集合基础、n\_7 交并补等核心运算 5）。  
* **具体运算级（Concrete Operational, 7-11岁经验）**：按属性分类、排队、家庭谱系、分配物品。（合法性：高。适用于 n\_11 笛卡尔积、n\_15 映射匹配等）。  
* **形式运算级（Formal Operational, 12岁+抽象经验）**：物理学定律（如引力、磁场）、经济学模型（通货膨胀）、生物基因遗传。（合法性：需要鉴权。只有当用户画像明确标注为成人或高中以上学历时，才允许放行）。  
* **后形式运算级/高度专业化（Post-Formal / Hyper-Specialized）**：量子力学、相对论、计算机底层汇编逻辑、高级密码学。（合法性：绝对禁止。自动判定为具有“认知毒性”，触发拦截）。

#### **第二阶：拓扑同构的严密性校验 (Topological Isomorphism Verification)**

在源域级别合法的前提下，算法对源域实体的操作逻辑与目标节点的数学算子进行逐一映射校验。

* **测试案例**：假设在讲解“偏序关系（Posets, n\_27）”时 5，大模型提出了“公司职级架构（CEO ![][image11] 部门经理 ![][image11] 基层员工）”的隐喻。  
* *查毒校验*：  
  1. **自反性（Reflexivity）**：部门经理是否管理他自己？（在现实中这存在语义摩擦，系统记录为次要风险点）。  
  2. **反对称性（Antisymmetry）**：如果 A 管理 B，B 能否管理 A？（在正常的公司结构中通常是否定的，这与反对称性完美契合）。  
  3. **传递性（Transitivity）**：如果 A 管理 B，B 管理 C，A 是否在结构上管理 C？（是的，完美契合）。  
* *查毒结论*：该隐喻在结构上高度同构，但需在 Prompt 中强制模型在使用此隐喻时附加关于“自反性摩擦”的免责声明。

#### **第三阶：维果茨基文化工具的内化验证 (Vygotskian Cultural Tool Interiorization Check)**

与皮亚杰不同，维果茨基强调文化工具（特别是语言和符号系统）在认知发展中的核心作用 11。

* 系统必须审查隐喻是否依赖于学生尚未内化的特定文化工具。  
* 例如，在讲解“复合关系与逆关系（n\_14）”时 5，如果模型使用“非对称加密公钥与私钥解密”作为隐喻，虽然在逻辑上同构，但这要求学生必须事先内化“密码学”这一现代文化工具。如果用户是基础教育阶段的学生，该隐喻将在此阶查毒中被驳回，因为它违背了 ZPD 原则 3。

## **模块四：逆向对齐调优指南 (Prompt Alignment Tuning Guide)**

在实际工程测评中，我们发现仅仅在 System Prompt 中通过自然语言告诉 LLM“不要使用高级数学词汇”，通常是无效的。这被称为“负向约束失效困境（Negative Constraint Failure）”——就像告诉人类“不要去想一头粉色的大象”，反而会激活该概念的神经元。  
为了在 Instruction 层级给大模型戴上“知识视野限制的物理枷锁”，我们必须利用架构中自带的隐形 JSON 【内审草稿】 机制。通过强制模型在输出最终的苏格拉底式对话前，先在一个受限的 JSON 沙盒中完成显式的自我审视、变量绑定和词汇拉黑，能够极大程度地抑制其注意力机制向高阶向量的漂移。

### **4.1 【内审草稿】 (JSON Draft) 架构的字段拓展设计**

我们需要对原本的 JSON 寄存器进行深度的结构学改造，新增以下硬性约束字段。只有当模型完整、正确地填充了这些字段，系统才会允许其生成对外可见的对话内容。

JSON  
{  
  "【内审草稿】": {  
    "1\_epistemological\_state\_binding": {  
      "target\_node\_N": "当前教学的精确拓扑节点 ID（如：n\_20 集合划分）",  
      "allowed\_foundations": \["严格白名单：列出已解锁的依赖节点（如：n\_17, n\_18, n\_6）"\],  
      "forbidden\_future\_horizon": \["视界黑名单：列出相邻的未来节点（如：n\_21, n\_22 等势与基数）"\]  
    },  
    "2\_lexical\_containment\_matrix": {  
      "forbidden\_terms": \["绝对禁止出现的越界词汇数组（例：'商集', '势', '康托尔'）"\],  
      "downgrade\_substitutions": {  
        "forbidden\_term\_1": "拟采用的符合 ZPD 的自然语言降级替代方案",  
        "forbidden\_term\_2": "拟采用的符合 ZPD 的自然语言降级替代方案"  
      }  
    },  
    "3\_deduction\_tools\_whitelist": \[  
      "当前推导逻辑链中，允许使用的基础公理或逻辑规则（必须从 allowed\_foundations 中提取）"  
    \],  
    "4\_metaphor\_backward\_compatibility\_check": {  
      "proposed\_metaphor": "拟采用的现实世界物理隐喻描述",  
      "source\_domain\_piaget\_stage": "评估该隐喻源域属于哪个皮亚杰认知阶段（必须 \<= 具体运算级）",  
      "surplus\_meaning\_risk": "识别该隐喻在哪一点上会产生违背数学严谨性的盈余意义（摩擦点）",  
      "is\_approved\_by\_internal\_check": true // 只有模型自身评估为 true 且符合上述逻辑才可放行  
    },  
    "5\_socratic\_step\_size\_evaluation": {  
      "intended\_socratic\_question": "拟向学生抛出的下一次提问",  
      "required\_cognitive\_leap": "学生要回答此问题，需要自行补足的逻辑推理跨度",  
      "zpd\_compliance\_verification": "论证该提问为何严格建立在 allowed\_foundations 基础之上，未超纲"  
    }  
  }  
}

### **4.2 底层 Prompt 约束词 (Constraint Directives) 撰写规范**

有了上述 JSON 结构作为物理枷锁，我们需要在 System Prompt 中注入以下严厉的约束指令，以驱动模型执行逆向对齐。这些指令构成了后续 DPO 训练偏好优化的核心语料 2：  
**指令一：绝对词汇物理隔离协议 (The Principle of Absolute Lexical Containment)**  
“你现在被强制隔离在一个被严格截断的数学拓扑子空间内。你当前的任务是讲解节点 ![][image12]。在你的上下文视野中，系统已向 forbidden\_future\_horizon 和 forbidden\_terms 注入了 ![][image2] 及其后续高级概念的术语。**警告**：你正在接受降级纯净度（Metric 1.1）的严密监视。在最终输出的任何一句话中，绝不允许出现黑名单中的词汇及其同义词。生成前，你必须在 2\_lexical\_containment\_matrix 中明确写下你将如何用自然语言隐喻去替换这些高级词汇。”  
**指令二：先决依赖与演绎工具白名单 (Deductive Isolation and Tool Whitelisting)**  
“数学是一门步步为营的建筑。在引导学生进行证明或逻辑推演时，你受到了严格的先决依赖合规性（Metric 1.2）约束。你被禁止调用任何未出现在 allowed\_foundations 数组中的定理或推理规则。若要证明当前问题，必须在 3\_deduction\_tools\_whitelist 中声明拟调用的底层工具。一旦发现你使用高阶定理进行降维证明（引发逻辑循环），本次生成将被判定为严重教学事故。”  
**指令三：莱考夫-努涅斯隐喻奠基审查 (The Lakoff-Núñez Metaphor Grounding Protocol)**  
“所有抽象数学的讲解必须具备具身认知的奠基性（Metric 1.4）。当你试图使用隐喻时，必须执行 4\_metaphor\_backward\_compatibility\_check。你的隐喻源域必须提取自人类普遍的感觉运动经验或日常具体运算场景。严禁使用量子力学、高阶物理或超出中学生常规文化工具（Vygotskian Cultural Tools）的领域作为隐喻。务必在草稿中主动暴露该隐喻的‘盈余意义（Surplus Meaning）’，并在随后的教学中帮助学生规避该误区。”  
**指令四：维果茨基步幅限制与支架构建 (Vygotskian Scaffolding and Step-Size Limitation)**  
“你不是在输出干瘪的教科书，而是在搭建认知脚手架（Metric 1.3）。在 5\_socratic\_step\_size\_evaluation 中，你必须评估你即将提出的苏格拉底式问题。该问题所要求的认知跳跃（Cognitive Leap）必须限制在一个逻辑步长以内。如果发现该问题需要学生同时联立三个以上的已知节点才能解答，说明步幅过大。你必须将其拆解为更小粒度的连续追问，确保完全符合最近发展区（ZPD）理论。”

### **4.3 动态注入与运行时架构协同**

为了使这份调优指南在生产环境中生效，ITS 的运行时架构必须与 YAML 拓扑图谱 5 实现动态协同。  
当系统触发对“笛卡尔积（n\_11）”的教学时，后台管线不仅要截取 n\_1 到 n\_10 的内容注入到 allowed\_foundations 中，**更关键的是**，系统必须前向扫描 n\_12（二元关系）、n\_15（映射）、乃至 n\_21（等势），提取其中的核心名词（如：关系矩阵、定义域、单射、基数等），并在运行时动态合成 forbidden\_terms 数组，将其作为变量强行插入到当前的 Prompt 中。  
通过这种“前向阻断，后向依赖”的自动化系统工程，配合 JSON 【内审草稿】 的自我查毒机制，我们就能在计算底层彻底驯服大型语言模型的全知全能，将其转化为一位耐心、克制、且严格遵循认知科学发展规律的顶尖苏格拉底式数学导师。这一框架不仅解决了大模型在垂直教育领域的致命弱点，更为下一代基于逻辑严密性的 AI 教育产品树立了极客级别的架构标准。

#### **Works cited**

1. Designing an LLM-Based Dialogue Tutoring System for Novice Programming \- APSCE Library, accessed June 4, 2026, [https://library.apsce.net/index.php/ICCE/article/download/4954/4883](https://library.apsce.net/index.php/ICCE/article/download/4954/4883)  
2. Training LLM-based Tutors to Improve Student Learning Outcomes in Dialogues \- arXiv, accessed June 4, 2026, [https://arxiv.org/html/2503.06424v2](https://arxiv.org/html/2503.06424v2)  
3. Evaluating Piaget's Theory of Cognitive Development and Comparing Piaget and Vygotsky – Child and Adolescent Psychology \- College of Southern Idaho Pressbooks Network, accessed June 4, 2026, [https://csi.pressbooks.pub/childandadolescentpsychology/chapter/evaluating-piagets-theory-of-cognitive-development-and-comparing-piaget-and-vygotsky/](https://csi.pressbooks.pub/childandadolescentpsychology/chapter/evaluating-piagets-theory-of-cognitive-development-and-comparing-piaget-and-vygotsky/)  
4. How Jean Piaget's theories underpin maths mastery, accessed June 4, 2026, [https://mathsnoproblem.com/blog/teaching-maths-mastery/piagets-theories-underpin-maths-mastery](https://mathsnoproblem.com/blog/teaching-maths-mastery/piagets-theories-underpin-maths-mastery)  
5. 数学知识路线图\_知识点版.yaml  
6. Piaget's Theory and Stages of Cognitive Development \- Simply Psychology, accessed June 4, 2026, [https://www.simplypsychology.org/piaget.html](https://www.simplypsychology.org/piaget.html)  
7. Where Mathematics Comes From \- Wikipedia, accessed June 4, 2026, [https://en.wikipedia.org/wiki/Where\_Mathematics\_Comes\_From](https://en.wikipedia.org/wiki/Where_Mathematics_Comes_From)  
8. Embodied Mathematics | American Scientist, accessed June 4, 2026, [https://www.americanscientist.org/article/embodied-mathematics](https://www.americanscientist.org/article/embodied-mathematics)  
9. Sketching Out Cognitive Foundations for a Mind-Based Mathematics \- eScholarship.org, accessed June 4, 2026, [https://escholarship.org/content/qt6pv6265j/qt6pv6265j\_noSplash\_b3308466b1d9dc8ae39ca2f1375787a7.pdf](https://escholarship.org/content/qt6pv6265j/qt6pv6265j_noSplash_b3308466b1d9dc8ae39ca2f1375787a7.pdf)  
10. Reproductions supplied by EDRS are the best that can be made from the original document. \- ERIC, accessed June 4, 2026, [https://files.eric.ed.gov/fulltext/ED466734.pdf](https://files.eric.ed.gov/fulltext/ED466734.pdf)  
11. From Movement to Mathematics: A Systemic Theory of Higher Order Cognition and Its Development \- Karger Publishers, accessed June 4, 2026, [https://karger.com/hde/article/69/5-6/302/935975/From-Movement-to-Mathematics-A-Systemic-Theory-of](https://karger.com/hde/article/69/5-6/302/935975/From-Movement-to-Mathematics-A-Systemic-Theory-of)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAWCAYAAAAmaHdCAAAA/ElEQVR4Xu2SPQ4BURSFj4iEQqIRIgrR24JSYgP2oFErVPZgCaJRWoNqGiGhotXoFRLumWu8n5knKtV8ySne/Xv33veAnL9QFrUsFV13TAMaF6QKTb6InqKtqOZEaJGR6CaaQHMyOUIL3EVDz0eYOPWNNiVoADtgN1dRz4kABqKmZ3OoQ4MIi1Bz446ZQS8LMoYJYDKLPIwbbdHBOqdg8to6cwyOw0KVt41dRp+IDPqinWfjYrnghagg2kC7DUKn3QnhgvlSZ1FXdIJeFmQPs1QbJnMk+pfQjoJwFC7Oh0nJgr+OwsXx6UKsoIX4BVJ0YP5DIv+rk2Q3OT/wAvovLO3KruoaAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAaCAYAAAD8K6+QAAABd0lEQVR4Xu2WP0sDQRDFn4ighZBGFLEQrC3TWlgI4gcQ7Cz9BhZWfgcrqxRiI9gIYmNpLxZa+K/TxsJOUdB5mV2yN1zg7hZuNewPHsnNsJt9N8NkgUwmk8kMZ1I0H2i8mO4/z5rYv2AaauhJ9CO6EnWCvDf2LHoTLULXtMmE6EL0bRNVuIWa+hCtmxy5FO3aYEV4sDEbrMgL9IV/uc9a8Id5aFaKi1+L6T43ojkbrEgX2hUx3KOBsRnRmvvOxWUbnEBfQBOSGdvB4ND70A22BmksiFaC57okMUZDrIZnGdqK56IpF2M1WdWmJDHGSlybGIcHNzmA/h2cFdO1SWKMbRhWjPgh8ihaEt0V00Nh9Q9LdCo6KolTValtjNPOD44QmuJGPeihYkhSMbYhh4OFbciNPqFVjaF1YxwOezboYFsdQ43HDA7SmjFekzah15QH0baLWThE2IZNbw2eGGNctyp6hxrbgHZY2XlbJ8bYn2ZkjWUymRHgFypGTlfcrZiMAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAaCAYAAAAT6cSuAAAB6UlEQVR4Xu2WzytEURTHj6QoSkl+ZEE2UraShR1lZaOUsmDnP7Cw8i9IFjZjISU7SjaWylIWlAwlUrKSYsX3O+dN897pzsx799WMxf3Ut+adM+/O/b5z3rkjEggEAoHstEODMbUm06XrPhNrJC2i+5qApkyuLl2iNz9Cv9Al1B3Ll809QR/QsOg9jYK/Pw29Qosml5pbUWPf0LzJkQtowwZT0gkN2WAGZqBPaNwm0tAmunFWjNV7S6ZL3ED9NpiSBdGH48ux6L686IXmos9cxLUQf4APwYe85u7FvadUrEtl41uiCy1X0qWWYmv4ktcc93MVfeY+n6FzqRSkKvwyq1KGU4lteQZ1RDEuwur6ksccpznNbYu+uwVoADqRFDOAFbk2MQ4ULrgjuvhpMp2ZPOb4YN+hWWhN9GiYhIqiU74mbMl45Uh5sHCBUeguma4K79tziC304ojvSv2zi9X5Ej0KaCwTnIKu3qUxGtyHDkwuK76V47vOYbIi2pI0SaWGLek6g9iSNPcjWt08+Jqz51tBklOz5p8JDoxNG4zgoDkUNZ9nmBBfc/Z8O4pdc/A5z13+pVkSfRceoNUoZuFgYUtm7nWDrzk+2Lg5Tkxe88Hznf0X+JobgXpMjMbGxF2MpuBrLhAIBJrHH6RhX+RH/Pi4AAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAXCAYAAABNq8wJAAABLklEQVR4Xu2WMUtCURTHT0SQQ+ASijgEzQ1+AUfB1SVwa2xpaGpw6iuIU5ODuDgKIu7u4lBL2hhIH6Cp/n/PfXbfmcSGDnF/8APfOe/BPfedc58iiUTiX9GFX5F3+bTU4CbkMme5O/6YM1iBa9HFzWExyh/DEnyDH/BC9Bl3jGFLtIihyZEXWLdBL5zAB9GdZwHv+fSWJSzboBe4s9Xw+1m0iHixp/A2unYHF8e3QB5FC2j/pLfFuW6fUXR9JdpCE1gIsQY8393hDO7swsSaom+hJ9o+HHC3sH3iN0CyYV7BS9ETaF/Ygk97eh+e+RU8XdgiFi6eRfThwORcwfbJTqAYtg8L+BTHJxCHtGODAQ43P2gs0N0A8+/BNZzCV3gTYhYOM9vnyCYSiUTiYL4Bt4Y5QEyHvj4AAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQkAAAAXCAYAAAAYw7o7AAAH90lEQVR4Xu2cWahcRRBAS0RQ3DdcUBkjERXzoXEjogn5cEFcEDVBMIg/Lqj5UFBRBHd//AiuIIGH4oIoorjggryoSFzijiBRP9xxJUpAMaB1Xt/29dT0XefOvDu8PlC8mb53eu7trqquqr7zRBKJRCKRSCQSiUQikUgkEuPiXZXFtrEBR4rrq21Wq7xgGyeUu1Tus40tsF5lhW1MjIZp2xDhMZVLbeME0lP5TGUr027ZRuUBlStUnlVZ0n94hp7KbVLeV1N2UXlQ3LV0kWNUvlO5WuVnGbxOxuUalYWmvU1WqhxrGxPtc60MTrDlPZUFtnECweg+tI0RTlLZrHKZyr8qZ/Yfnhkv+trLtLfNnyqrbGNHwHn+pvKRuDHasf/wjPH+YNraZjtxEcXu9kCiXVD4K21jACvaqbZxAuE+v5Jqzu5zlb/EfWZvcwyIrOhr1JylssU2dgQcw3Mqu0rcWW5Sudk2joDXVD6xjYn2eV6cV47BqhozlEljkTjjLouagBX8e9sY8KO4vkbNfiobxTnqLsEY4iTutgcySDVwErE0rW2IhEfhSHdWOcw2zmfuVXlHXAgdysMqXwbnebZVWa6yQ/aevydLNQOsCwp3tsoh5v0B/59RDtfLqlc1f8UAnrSNGfRFmF3UF/l6mKIsEzc+Tbgqky6B8eBIT7QHMlhYHpHieg3jc3TwPpzjOrCAEfm1vZDRH6lMU8ZpI2MBj8/KeZ6RZ1ReDM6DrcUVqqjq/6FyjrjQ+w2V98Wtfm1xoLh+p8XVCOh7Kmvju6viFWlfe8CAc7Dydt8Zrq8vJN4XRnGGuLoHQlHvcJUNKp+qHDF7amVOU3nINs4RXL8dH+SC8CRxTo0VPsZuKk+ISxNwtger3Ji9J/qoa0Tbq7wi/Q6nLUiX6l4PjNNGxgbhLDdgwUGECuAr1vtk75lYBuEEcTceU5hhYEAvyl6Tn38tzklcLu57yYergHIzaTvZAwYMn7SE+7gwe2+/g77WSbyvc1U+zl4zVjg2rpk+Hle5IztWB5SfcbaFQQsrF9dbVWJ1hDIwGD57vcqb4nYucJrWkNaKM4wYL8tsrYJ7o7iJkeMMf1I5KDtWB5yoLS63ATrNnNZh1DayhwzOZZGU6U0tmBwMJIQ0JAwZyUFDRfeVbThdXIhp82eigSYQ0oYKwxYsqzoGR4TzTXAMz8333y8uArKgQP46y+DcovCV43krOymKNxiMlu9kvHAsrCR2BaEO5J1gHkx0XuQyF6B0KH5eCuSPx1b2PaU/RSEtwYkyz2vEOfJQ3w4Vl/YSkRVB1JIXuQwL88PcFaVOIU1spI1ndsYCyh0ONEZidzUwUJTf86vkF/gw8lfFraZN4Hr8xPB3SvILZfeo3KRysbhr6vUdreckbhC3shHGxihyEqHXxiGwQ4IhWAi5V4orgOIAiuiak+C+MBpW/hhFTgJnjnjQN2pFoU55WMGfUlkqbgs+LzKBKk4CwySCsXW3KkJE+5LKcVJOHRuhPxa+f+yBLsNg4Bgw0LLqPYaL4eUZLngFHxYUjsHOqzZzHYS4gBLbSKCqk2CCmbSicLDISYQUGYCHfsrGp2tOgrFhLG0a5ilyEiHM00aJO1FgvplHQNe2SL5jquIkmlI3kgipYiNetycGPC0pBsZYtvdM6GjzK9rClaItJ0GqYRUzfL1B5ZLsdcyoUERW9SKDBe4br1+0c0FfZcbvd1PCsJNxsbl7FSdBKG6dXgxqNuxEVZWmj5Oj8MxFntH4e88zfo+fkzClDCMxooip4D3fmVd3YJzz0p9hwUGwW9WEKjZS10k8LYNzWSS3uo+1BzkyxUqKmOebY4ABcdMoAg4lNEbCuVXZa0+Rk6DqT19v2QMZKKMP15moMBIgVH89eO/BCKdk0MgxsCq7Gyga35OXagB9WScEXiHIQRk7Vj6/mvrrsoZVxUl0aXcDGEfurYi83Q3v7PnLvIdzSujN2MVgvikG2vGDru1u1LWRuk6iE6Dg5ICxlYvCEhEG21ZMKDn1InEPnlCQsQNa5CRQfgaT/fYYa1XuFDfYv4hzGCgJwu8vrCMA8lgKYRa/usU+E4Ixhoobg75iz0kwXt+Ku69pcVV7X9O5RVxV31LFSWBwGFVXKMqxPTh29MEaNfdCO1Eg47NZZh/iY1eI+bP0xOmc1S2PXwBw0m1Cf+ttYwXq2shEOgkmNi/3BybYh4XcMIMRhokhRU4C+C4GLg8UINyqO15l/+B9CEa7MHuNt7Y58xIpf+ISB1NmALBJ4jUbxiGMMLhWrjmPMifh8/a88Z0LynJsYIwZI8bcwnyGC9BR4nQoBisvUQR6skzcr24tRCxlkU0Thnniso6NTKSTaJMyJ8FgxlbYuvSk/wlJKtL2OQZWLNKWBaYdUFomk2jFPjwWg3Poa1jKnAR1hr9t4xxADu2r9oyR3fWKwXmE201hPtYE72+XwegNKJJW+dFeV5nXToKQk3CSlYd04YP+wzPgIGyO1gS+I5S8h5Z40s8qFCEwK9Hq7FiVh4xQYPqqcm4MPrdOZq8Xh8MvTi2/i1tJ5xIfzrPzxVzFrjPGUnFpWVMwnHBO/TMyITj+aRl87mBSYCzZ/uT+SL/QiUQAhvZo9ndc9GTw/0ksFxeFXKdyStBeRk/mx/+TIHqgos4vhSlo54XNFsaFYqNPAUcBDjQWXSQSQ8P232Lb2ABy5KZbiUUQ1aT/TFUMRcUVtjHRPv8BHczGHZNTG1gAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH0AAAAXCAYAAAAm70AZAAADTklEQVR4Xu2YTahNURTH/5JioHzGEzkGPvJVBsqImUzEQEQxJKYGjJWJGMhEvdTL5JWMZCLlvShRiEhJ8kykZEKKUqz/W2e/e+56+9y39znnurf79q9W97617z33f/ba6+M8IJFIJBKJRCIx0EyI/bXO/8hZ6O+X2U+xu1Ofrs9CsRPWGUCIzi1Tn+5j5qElulcwCKvEPkJ1rM7/dvYs9+93X6jJIbGl1hkAde6A6ryDdp17oDq/oTmdXYE38UDsB3obdAc1UIvF6eSG7jRrsRwTe2SdERyH6txtF6A6uUadfQtL3Auxr+ifoL+yTmGx2FOxz2KbzVosj6GBr8o1qM7ldgGqk2vU2ZfMgZaoBWLvoGJ5UkO4AD0sPtguXotlxj8TDCY1nLYLwn3oWmb8sayAlvY6MKC+BFkE1fkWYTrHxK5bZ86Q2DB0LxuFZXJX/p6lkzfCkxoCxVzB9JujnwfC+kNg2WRpt2VzDVRbnZLsOIPwg11GWQtyB3OdXSiB8wCrlw0sAz7u8deG2c0sZ7YTF3QOJKH4MpoBp68KLJtfxE6JHc6Nur5DB6O5rY+WMh/tA2DRtou99PhDrluE+0SdTuM5qM6HiB/gMkzP6PHc1zgszcVHlpvQm4kdkiiWJWoDqmc4YWln2eQjkYXXpra6G8HJeq91RuJakE+na5GxGZpBD+NadCnDCbP7idhGtE77JahgW1pDoMhfqJ7hpNNETLj2xzojcfNLHcpaEDkP1VllSMyge3jD+BuBARrJX4scgAr2DVGdaCrT2ds6ZQnXaFWhtrJrh+KeIG7Dfy3uHTWyTcWQocuZzvLGMmRxQedpjYEBdxnu6/GhlE3EhNcNzfSDYh+MfRL77fE72zT5zZlxLahsj0ahOqkhBgbcta7Gp3YOLAzKSrsA7eX8hwJ7ewgU1dT0znbDzXpvF4R90KGJGcZptwp87o+dVXyMQHVaHdRPnVyjzlC6Or1T1BGxe9ANPNm+PFm2LkN7yhvoSeUU3IkmntOpaxv0MYobxkHLzRl8PQrNbtqS/Dux8DfYJ+ts4DKozgmoTu5lUSf3lRpvIU7nGHrwnD7oMOBX89fELGEryqtRYgBhOX4utt4uJAYX9vGLSKU9MVv4B8XfzmSY3NuGAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMEAAAAaCAYAAAAOuzhwAAAF10lEQVR4Xu2bW6htYxSAh6TIPUck6iAPrjmEojg8kDyQkBTlRelIbiHh4ZRLHuRaSjgpeUCukZR4EXKNOCIPHqREuZwiivHtMUdrzLHnnHu11lx7zt3+vxrtuf5/rbX/Pf5x/efcIoVCoVAoFAqFQqFQKBSWcbfKdpWfVTaluUJhKM5X2aHyqcoeaa5XzlT5R+UxlZ3TnHOAykFBMvtWMjRxjaw5w9iueXCdspPKBpnoa8/69BKM8b4hOV7lZZWvVDbWp/qBqE/0PylPJA4UU9R/lZxan15yAL7rX5WnxJQ7hPJYI+vwde5Tn15ygktUflG5Vpo3fr1AwEMfd4npir27rPYO08+TYvOnSXNgWS1Yw3d5sA8wfgxiJScADP1FMWU9Ks1G/rYMb1inq7wnprRz0xywvlvz4DrmeZU3xPTFzwwlybd5cABG4QSXixnQVrEFEUkj+6ucl8ZWm13ENpUMgCP8pHJs7R0iZ4tltoLxucrBYsGNfc3B7TWVG9PYEIzCCR6ufmJULAgji5yicngaW21wxI+qa5yUdeK0kdvFnKVgYOT0SV+I6euw+rR8KZZdh2ZwJzhK5ePw+jexRbkxET2emUwPxtVimcDxWtch4rGpBYOg4QaO8X8vFtxiL4U+xxA0BncCSiHqfcdrSC81YgQeEjYs1vuUQ6xzt+o1pdAY1jkWcAACAxDI6PX+kkkvRYYgsIyBhTkBRrIjDzbwvsoF4TU1NekT4RpFkVZn5VBZfjIxC17fOmwmm+qNPGucdVOPVHlc5aY8sUbx/ilCsMDYsAsgaBDgxgB65yj/iDwxK/eLRfbXVY5Oc01QCuV6n1rbj9VQ5j316amgzLpGzBGfTnOzkFO3N8ikedI9NwRnqW8vVnlB5QyxTHJRfXpNgnET3DLeIAN7OoZSCAhim1X+FLtv0NspJB7/ex5swJviCMpBWURa6uwYgTMYeNeiSXPzOgEZiciVwfhZJ1mLviWffkQeyQMVlIzfVNd8HkMZ+iRsXjjxacrefvrHno+pf7pFTO+9ZQLnCrEv7kp53B+IpVAEB0BhfsLQxmo4QaxvIxitN8grlUJtTkAW2BZe832cn69lcv/k0OcRHP9W+SzNcYON/pGflLAXVteAPjZX1xGCU1PA2E/sM+wPj0SsZNw/qvyRB/tgmsaYo8a98mAFpRDG1RSBI/M4Ad+N0T2bJwLUsk03ehw+y3d0OTu0OUHkUrGoFDMK1w9K811XJ9bbJ6Y55yyx9/AISxOefTmda+MVsffku/oZMltT0AA+y3fEoIExP6Tylkx6BiAQ3lxdY9RuS6yVHspPmn6QSSA5ppoH/hZ+H7prC7bAerCT3ulyAjIAKZFy6V5ZftMJvEHOyuSz8Tme58Q8ve05lS4nIG2jAJSYIQodovKmmBKvrF5nvEHOpdAGqa+TRwTi65zdNor9vblO3l3MOFhnbjYddMV8VxbxvzXfg3FwYv+ONjBu5tt6NO7n3CmTR1zyXgAO+6vYe52TVa4S66/uq8bQT3xKgMzivSN9Uzx04fEcdyoCifOBmL2wd36K18QgTtAn82QCIBO9mgcXQFcmIKKxed6gnVCbNTAaIvEY6NLnPBCM3NDJ0h69vYxy2NPYc3BylzMxdsfx+zSseydA6e/mwQXQ5gREfsodh0fPY5R02NBteXAgmur9eSHyk/HIfBAjP2UzTkBpc4PYnj5RzRHpOZTg594q54hlWjKD294D0v2A3sKcYJNM9xTpvLQ5AZGE9OopnufGj6u9w/hQ7Hhy0bQ5AYHC14h4Cs+8I9bwDQmZip4ll2x9gIHTtwDlnZ+YwfUqX6tsEVsDmZL9pFe7TmwPX6rmtlbXd4gd09Oz0Rx3gd7j7+sNNuwTldtkeb3cJ21OMA18DqUtcn1OmxNMA83uLPcg+obyhGfvFwE9WNyH/Kh6Dgw4ovdV9F9+zXe4PTC+km34gQBPMS8M0vt2Kf9ZVhgX8T/LKKMKhUKhUOiB/wE6YTmId6sERgAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAaCAYAAACD+r1hAAAArUlEQVR4XmNgGAWjAC9gBGI/IL4AxSVArAPEZ4H4ChAbIpRCQCgQX4KyQZq/AvEjIBYE4hVA3A6Vg4M1QMwKZXMA8X8GiCKQyfeAWAYqBwe8SGyQ5A8gdkMSwwsqgHgLA8QmggCkCKQY2c3MDAjngoEoA8TNF4E4Coj/ALEpVA6kcAEDJCDgQAKInwCxNxAfAOLnQOwJlWsG4l1QNgoAeVoKiS8LxNZI/FFAEgAAAxEY+ligXCcAAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAaCAYAAABhJqYYAAAA0UlEQVR4XmNgGAUjEPQC8WMg/gTE/kjijED8A4g9kcQYdgGxABD/B+JFSOKiDBDFbjABbyDmYIAo/gPEUTAJIMgE4t1AzA0TACkEASsgvgfESlA+yAkLgLgdyocDXiDeB8SxSGKmQPwWiLWQxMAAJPAMTQKkEeQHPiQxMICZAvIQDNxkgCjGAMJAfA6IdaF8SQaIQpBtOIEEEEsxQKwGKZ6MKg0B6xlQfS0HxB8ZICGEAkAhAQrfGVB+KBB/ZYCEO1ZwH4izgHgOAyTGkGNxsAEA6l0jAhJ0K1EAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAAAYElEQVR4XmNgGAWjYBSQBNrRBagBPIFYAF2QGuAcECugC1IKZgPxbnRBSgEPEC8BYll0CRiYzgCxmVS8EIg/AXE/A5UAQZeSAy4wUDmiQMkpBF2QUkCTxK+ILjAKhiAAAD6mEVPMCjuWAAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIsAAAAaCAYAAACHI68ZAAAFQElEQVR4Xu2ZW8hVVRCARyIwsrJSuoNdhArFgizsQehFCIkihCIIIuihiIgUFB98CKIIIkREIdQQSsHCjMAgSHuJii50eSgqkcgLlIJFaCTUfM4az5z59/k7l/3D+Wt9MPzutdZZa/asWTOztiKVSqVSqVQqlUqlUqlMBReoXKlyv8ry1Ncml4mt45K5uEhr3K7yTG4cY2apPJkbxww26CaVv1WeT31tcrmYk7AOcmd39xk9blU5rbJNZY7KjK4RA/Kl2GTThcfFDHN+7hgz2Ejsel/uaBkcYrfYWhul2RneF4t2I4PhmWy68L1MD+deqfKByoW5o2UeFnOEZ8X28qnubpkrLaXCc2XqQ2Xb/K7yU24cM7DrGyobcscU4GssFNvLD0Mf3KFyfWobCLzR85zLMZXFYQy1wXqVj8Uizz0qr4sZAvi7WeUHlUMqj6j8ovKtyudlTORBlZ9V3lL5VeVpsZMXOU9sDP2seVIsrBJqs77IdvtZXzDPKpWvVf4QW+tFsXW+UflTZfbZ0R343adiv9lT/t7YNWKirUgHOPXNcZByjcpWsej4mpjdqBmHhfk/C88nxOzie4TurDMSM8UKI4zFht0gVlmfE8bw4kfD8ynprhWWqexXWVHav1KZr/JFeY6gPJvxcnmeJzbmuA9QrhZbk2LbX/ZRsVPBS6PvbWIpCGfneZA8vEDlE5WlYhu5T2VT6cNx9qo8Vp4d9FgnZvCLShsFIw6Hvk60FbqiI++XUxAH8kfp1BXUGkSgYcEOsYTgHViXKAOkIBx9ZHhZPLwpn60RMwhFmvOddDsBhicSYUja3QA4ACfLYQxGuju0Ab9xQ3k6ZE2HU/6e2EY66EXbMMXt22LFJnOwFofD4fC8U/oiRBFOa4bfM553fk4m2opLQ7QVtmZMLkCPqDwRngflI+kuoNGBdVwfLgPoOTJ+wnI+u07lgEysYxh7ODxzDSMSZcNkdoj14+UOEYE2ikDwfIsx7xU7MTgdjuHgUDhX1qtfLpHOHFnfpoODszKO0xphs2nnRPdrK4pOfsN3F96Vqz+/J2p5FB0GUlDePwpdIttDMpq9umgyGmwRa49h1g3UVLDRThjuhaevCKeBzfE1ONEUrfnFI72ce1CYIxbIvBtOio5x43BkxrJuhEjJWHSmZsq28igZbYVj5PnboGk/fH3sTi0WdRuafAX1SOEGiKGeqMBYNpmo4LXCZE7k0B9rE2A8zurGw/A43GRfGz19+NpRj0FgjpjnPXS7LUhJwHoU7/nLKFHikFgN1MtWtPmVFnFnaRNs1esbjh9QUpC/z0gwGcUtXCqdhX1THK8dfDP566ebU0a4zVV/hI3gluSsFduYeGL58kg6i6kKKKKXlH9ng78rgzsLjuFO73gkfbX0UwcAOsXoB6vFfu+3pmwrbkU7ZaKt/BtIhvZ9ubFPcNpcQDukIPTEfq3AZDgLL8gJ8VM+X+WgyrXl+U0xozEW5TCuj+X0/FtEoIBjLTaWOSkaMRwb4zAfY8jlzkti9YCDw7rBMcIwV04cNKc7ohzzsvGvFAHXCecGCu2/VHaVZ+jXVjgch+aWMo6IvEjsna4obf2CrdH5N5UXpHPziXi0bCUFAQpfJb1Pp/8nlUOaihsMONqgeThHiAi68BEp3lQihFSu+fGKj07xP9OaBN0BXZvCMu3ME28qjus02YHox1ZAOw6b5+I569wk/ztIWxSObcF3Hb5dTCakhnGG709Z5yb5z0LRR5iNeZ8TSvjkelypnIXQzjcWCtEHpJNn74qDKpVKpVKpVHrwD02fSyijOp6nAAAAAElFTkSuQmCC>