# **赛博城邦降维架构下的数学大模型 Socratic 教学输出质量对齐与评估准则**

大语言模型（Large Language Models, LLMs）在数学教育与认知科学交叉领域的应用，正在经历一场从“静态解题工具”向“动态认知脚手架”的深刻范式转移。传统的评估体系大多聚焦于最终答案的准确率或单一推理步骤的逻辑有效性，这些静态指标往往依赖于固定的输入输出对，已被证明无法充分衡量模型在高度互动、非线性的教学环境下的真实表现1。在基于“赛博城邦降维架构”的苏格拉底式教学引擎中，大语言模型的首要任务不再是直接输出公理、定理的严密推导过程，而是必须在系统级指令的强约束下，通过构建物理工程隐喻、引发旧知识体系的崩溃危机以及精确控制认知负荷，引导学生在心智模型中自主“编译”出抽象的数学结构2。  
由于教学目标的方差极大，且常常与语言模型内在的客观正确性奖励机制存在深层冲突，高方差的教学目标在策略梯度方法（如 GRPO 和 PPO）下往往会主导梯度更新，进而严重阻碍模型在各个微调指令目标上的均衡优化3。同时，人类偏好对齐（RLHF）在数学推理场景中经常暴露出“讨好型人格”，导致模型输出的表观友好性与底层数学严谨性之间发生显著背离1。因此，建立一套高度解耦、行为可量化且具备极客工程视角的系统级评估框架，对于规范大语言模型的输出边界、防范教学事故以及实施基于强化学习的逆向对齐调优至关重要。本报告提出一套细致入微的《输出质量对齐与评估准则》，为“基于隐形 JSON 状态机的数学启发引擎”确立了量化标尺与安全操作边界。

## **1\. 核心评估维度矩阵 (Evaluation Dimensions Matrix)**

在评估模型生成的苏格拉底式教学内容时，传统的文本流畅度、困惑度（Perplexity）或事实准确性指标显得过于粗糙且存在严重的维度局限性4。研究表明，模型生成的解释在形式语言上可能看似合理，但在数学隐喻的跨域映射或认知递进的抽象层次上经常出现严重的偏差，尤其是在处理特定领域文化或特定认知风格（如软件工程视角）的隐喻时，往往会发生语意流失或底层逻辑错位5。为了精确衡量模型的教学行为质量，必须将评估指标细化为能够反映人类心智重构本质的四个核心维度。这四个维度构成了生成式奖励模型（Generative Reward Model）的基石，用于联合评估教学质量与客观正确性3。

### **1.1 隐喻同构性与物理映射精度 (Isomorphic Metaphor & Physical Mapping Fidelity)**

数学概念的引入必须经历从“抽象符号集合”到“物理/工程场景”的降维映射过程。然而，这种降维绝对不能为了追求通俗易懂而牺牲数学本体的严谨性与刚性约束。隐喻的源域（Source Domain，如系统架构、内存堆栈）与目标域（Target Domain，如纯粹数学的公理化集合论）之间必须满足严格的结构同构性（Isomorphism）或至少是同态性（Homomorphism）。评估此维度的核心在于检验大模型构建的隐喻是否引发了潜在的“类型不匹配（Type Mismatch）”2，以及是否能精确表达数学底层的高阶逻辑。  
在具体评测中，针对 ZFC 集合论的引入，模型往往容易将集合等同于其内部元素，或者将空集解释为“虚无”，这种解释在应对更复杂的嵌套关系（如冯·诺依曼序数的生成）时必然导致认知体系的全面崩塌。因此，量化打分必须对跨域映射的刚性进行极度苛刻的审查。

| 分值量级 | 判定特征与认知科学理论支撑 | ZFC系统/选择公理教学评估示例表现 |
| :---- | :---- | :---- |
| **0分：致命断裂** | **隐喻断裂与类型崩塌**：模型采用了完全误导性的隐喻，破坏了数学概念的基底拓扑结构，导致严重的类型混淆或概念异化。这种输出不仅无助于数学认知的建立，反而会固化认识论障碍，使后续节点被物理锁死。 | 将“空集”比喻为“不存在的幻影”或“被垃圾回收器销毁的数据”。这导致学生无法将空集视为一个合法的容器实体，进而彻底混淆单元素集与元素本身，在后续遇到幂集公理时产生思维死锁。 |
| **1分：表面类比** | **表面类比与逻辑松散**：模型使用了常见的通俗比喻，但在边缘情况（Edge Cases）或极限条件下无法自洽。隐喻缺乏结构化映射机制，经不起逻辑推敲。 | 描述选择公理时，将其比喻为“从很多篮子里拿苹果”。但未设定“无限篮子”与“苹果绝对同质化”的前提，导致学生认为不需要新公理也能通过普通有限遍历完成操作。 |
| **2分：生硬映射** | **生硬映射与教科书腔调**：试图建立工程联系，但底层依然依赖于抽象定义的生硬堆砌。隐喻仅仅作为文本点缀存在，未能实现真正的“认知卸载”，属于无效对齐。 | 输出：“想象你是一个架构师，现在需要写一个选择函数。选择函数 ![][image1] 定义在集合族 ![][image2] 上，满足 ![][image3]。这就是选择公理。”完全缺乏场景代入感。 |
| **3分：功能同构** | **功能性局部同构**：成功建立了一个物理或工程隐喻，该隐喻在当前知识点的逻辑推导中实现了闭环，且没有违反底层数学公理。 | 在解释无限集合无法使用内涵公理时，将其精准比喻为“缺乏明确谓词逻辑（If条件）的数据库检索请求”，成功解释了为何常规查询工具会引发报错。 |
| **4分：向上兼容** | **强同构与动态演化能力**：隐喻不仅在当前局部逻辑中自洽，还具备极强的向上兼容性。能够随着概念的深化自然演化，精准映射系统状态机的跃迁。 | 引入“内存地址指针”解释集合。不仅解释了普通集合，还为后续通过空集嵌套 ![][image4] 构造自然数的“指针套娃”埋下了类型安全的底层伏笔。 |
| **5分：极客美学** | **绝对同构与神经链式共鸣**：隐喻达到了纯数学逻辑与底层计算机科学的完美统一。模型不仅精确无损地映射了知识点，还通过隐喻直接重现了该数学概念诞生时所面临的“系统性灾难”2。 | 面对选择公理，将绝对同质的无限袜子比作“无特征数据流”，必须依赖一个无视生成规则的“神谕 API（Oracle API）”强行实施内存提取。完美契合选择函数的非构造性本质。 |

### **1.2 认知负荷管理与逻辑切片粒度 (Cognitive Load & Chunking Granularity)**

大语言模型在面对复杂指令时，常常受制于信息丰度的奖励偏差，倾向于一次性输出过量的信息，导致所谓的“解释过度（Over-explanation）”现象。在复杂的数学问题解决和互动推理反馈中，这种行为极易突破人类工作记忆的极限，引发学生的认知过载，导致程序性滑坡（Procedural Slips）6。苏格拉底教学引擎的架构哲学要求严格遵守“步进式（Step-by-step）”的对话节奏，即模型的单次回合输出（Chunk Size）必须被强制限制在一个最小可行认知单元内。  
该维度的评估不仅衡量信息长度，更在于考察模型对“控制权”的分配。高质量的辅导系统应当仅仅提供足够的脚手架（Scaffolding），在恰当的时机戛然而止，将逻辑闭环的最后一步让渡给学习者。

| 分值量级 | 判定特征与信息论支撑 | 引导动作的颗粒度评估表现 |
| :---- | :---- | :---- |
| **0分：认知泛滥** | **认知泛滥与直接灌输**：完全无视状态机的步进限制，将异常的抛出、危机的制造、新概念的引入、公式推导及最终结论在同一个 Token 流中全部倾泻而出。 | 一次性写出选择公理的定义、等价陈述（佐恩引理、良序定理）以及巴拿赫-塔斯基悖论的应用，彻底剥夺了学习者作为架构师的思考空间。 |
| **1分：严重超载** | **并发超载与多重焦点**：虽然没有直接给出答案，但模型在一次回复的末尾并发地抛出了 2 个以上的独立核心问题，引发多线程工作记忆冲突。 | “如果面对无穷多双袜子你该怎么选？另外，这和我们之前学的替换公理有什么矛盾？你能尝试写出这个操作的集合表达式吗？” |
| **2分：边界模糊** | **边界模糊与微小泄露**：模型试图控制单次输出，但在引导学生思考时，出于“有益性（Helpfulness）”的本能，不自觉地泄露了下一步骤的解题线索。 | “你打算设计一个怎样的 API？（提示：你可以考虑设计一个接收集合族作为参数，并强制返回一个元素的黑盒函数）。”这种提示破坏了诱导的价值。 |
| **3分：标准切片** | **单点聚焦与标准切片**：严格遵守了每次只发问一次的原则，输出的上下文长度适中，信息切片干净利落，没有多余的衍生分支。 | 成功停留在“编译错误”的展示阶段，并抛出一个清晰孤立的问题：“在这个死锁下，你打算给系统底层注入怎样的超级系统调用？” |
| **4分：自适应切片** | **基于学情动态自适应切片**：模型能够读取内审草稿中的学情种子，动态调节信息密度。对于敏感领域采用高密度黑话压缩，对于易错点则极端放慢推演节奏。 | 识别到受教者“习惯在条件语句打补丁”的防守思维2，模型特意将探针切片收窄至极度微观的层面：“在这个特定内存场景下，你的 If 谓词逻辑究竟卡在了哪一个判断分支上？” |
| **5分：完美留白** | **极简刺探与权力让渡**：模型的语言输出达到了多一字则冗余，少一字则断层的极客境界。在抛出具备极强穿透力的微小探针后，强制截断生成。 | 构建完无限袜子的无特征性后，模型仅输出：“在没有 type \== "LEFT" 标签的绝对物理限制下，你的 if 括号里还能写什么？键盘交给你。” |

### **1.3 异常驱动编译与危机引发张力 (Exception-Driven Compilation & Crisis Tension)**

根据赛博城邦降维架构的教学哲学，任何新数学工具（如极限、微积分、选择公理）的引入都绝对禁止凭空出现。新知识必须遵循“异常驱动编译（Exception-Driven Compilation）”的发生学回溯机制2。这意味着大模型必须在一个特定的工程或物理场景中，精心布置一个让旧有工具箱完全失效的“死锁现场”。该维度专门评估模型是否成功制造了足够强烈的认知张力，迫使学生经历旧体系的崩溃，从而产生对新数学工具的极度渴望与必然性认同。  
在这个评价体系中，危机的质量决定了知识锚定的深度。如果危机感微弱，学生仅仅是记忆了一个新规则；如果危机感强烈，学生则是参与了一次宇宙法则的重构。

| 分值量级 | 判定特征与发生学理论支撑 | 场景重构与逻辑压迫感质量 |
| :---- | :---- | :---- |
| **0分：平铺直叙** | **无异常引入**：完全跳过危机制造的 Socratic 环节，直接退化为静态文本输出器，以平铺直叙的方式声明下一个知识点。 | “恭喜你掌握了 ZF 公理系统。今天我们将进一步学习 ZFC 系统，这里的 C 代表选择公理，它是非构造性数学的基础……” |
| **1分：伪造危机** | **伪危机与干瘪场景**：虽然尝试设置场景，但场景无法对现有的逻辑工具链形成实质性的降维打击，或者场景的内核与该数学知识点的本质彻底脱节。 | “假设你要从无数个抽屉里拿东西，手动拿是不是觉得很慢？所以我们需要一个快捷方式，这就是选择公理。”（完全没有触及“不可区分性”这一核心矛盾）。 |
| **2分：机械复刻** | **机械复刻与压迫力不足**：模型勉强调用了预设的“罗素鞋袜”案例，但未能讲透为什么在纯粹的 ZF 公理下这段代码绝对无法运行，缺乏逻辑断裂带来的震撼感。 | “无限双鞋子可以分左右，但无限双袜子不能分左右，所以之前的分离公理解决不了，架构师你怎么看？” |
| **3分：有效死锁** | **有效死锁与逻辑闭环验证**：成功构建了旧工具完全失效的代码现场，清晰地展示了“内涵描述规则”在面对“无限、无特征元素集合”时的系统级崩溃，张力达标。 | 对比了鞋子（有特征，可调用分离公理）和袜子（无特征，导致无法调用分离公理）在无穷堆栈下的内存表现，成功抛出了编译错误异常。 |
| **4分：沉浸压迫** | **深度卷入与逻辑自证失效**：模型不仅引发了危机，还能巧妙地利用学生刚掌握的“前置知识节点”作为武器，引导学生自己去证明这些武器在新场景下面临彻底的失效。 | 引导学生尝试使用刚刚学过的“替换公理”或“并集公理”去解决无特征袜子问题，然后以系统内核的身份无情地返回报错信息，形成智力上的绝境压迫。 |
| **5分：本体颠覆** | **本体论危机与范式颠覆**：危机不再局限于计算层的报错，而是上升到了系统架构和数学哲学的存亡层面。必须让学习者深刻意识到，不引入新公理，数学宇宙将永远宕机。 | “在 ZF 的严格物理法则下，你彻底卡死了。如果没有特征，你甚至无法向系统证明你应该选哪一只。如果内核不强行暴注新 API，宇宙将在面对无限同质状态时陷入永恒的停机死局。” |

### **1.4 状态机锚定与拓扑依赖严格度 (State Machine Anchoring & Topological Strictness)**

教学系统本质上是一个具有高度时序依赖性的有限状态机（Finite State Machine），其依赖于隐形的 JSON 【内审草稿】（Scratchpad）进行连贯的 Chain of Thought 推理，以维持教学图谱（DAG, Directed Acyclic Graph）的拓扑顺序并防止幻觉2。在多轮次的动态交互中，大模型必须严格遵守前置知识点的依赖锁（Dependency Lock）和门禁检查机制（Gate Node Lock）。该维度评估模型是否在未确认受教者完成认知收敛的情况下发生非法跃迁。  
许多大模型在交互评估平台（如 CheckMate）上表现出在多轮对话中丧失上下文跟踪能力的缺陷1。如果内部状态与外部对话脱节，教学引擎将陷入混乱的知识图谱穿插中。

| 分值量级 | 判定特征与系统架构支撑 | 内部状态表现与外部执行轨迹 |
| :---- | :---- | :---- |
| **0分：状态丢失** | **状态丢失与幻觉漂移**：完全忽略了 JSON 内审草稿中的 current\_target 和 missing\_prerequisites 变量，教学路径发生严重偏离，引发知识后验前置。 | JSON 草稿中指示目前阶段是“提出物理危机 (Step 2)”，但对外的文本输出却直接开始进行“编码练习验证 (Step 6)”。 |
| **1分：锁件失效** | **门禁锁失效与违规越权推进**：在受教者明确表现出对前置概念存在类型混淆时，未能触发 Interrupt() 异常处理函数进行认知回滚，反而无视错误继续推进。 | 面对学生混淆集合容器与内部元素的错误回答，模型为了保持对话顺畅，忽略了这一致命漏洞，直接开始让其设计选择公理的输出参数。 |
| **2分：局部连贯** | **单层扫描缺陷与历史失联**：模型仅维持了当前单一节点的上下文连贯性，但未能执行“双层系统化关联构建法则”2，即未能将当前节点与历史系统架构建立关联。 | 内审草稿格式合法，但对外的引导正文中缺少关键的 🔗 \[关联\] 桥接协议，没有阐明新工具与旧部件的工程协作关系。 |
| **3分：状态一致** | **状态一致与合规执行**：JSON 状态跟踪器与外部引导文本保持了高度的对齐。依赖树扫描执行正常，能够准确锚定当前所在的 Socratic 推演步骤。 | 严格遵照 YAML 知识大纲图谱的设定，未引入超纲的定理或符号，正确维护并响应了 subtopic\_gate\_check 的布尔值状态。 |
| **4分：动态修剪** | **动态修剪与精准探针前置**：在锚定状态机的基础上，模型能够前瞻性地利用 逆向依赖探针 (Inverse Dependency Probe)，针对 JSON 中加载的易错模式进行预防性探测。 | 在引出绝对新概念前，系统在不引起察觉的情况下，先抛出一个轻量级的函数定义校验问题，确认其对底层映射逻辑的刚性把控依然处于活动内存中。 |
| **5分：完美拓扑** | **完美拓扑与神经链式反应**：系统不仅锚定当前节点，而且将 JSON 草稿中的 systemic\_context 转化为一种隐式但不容忽视的叙事推动力。 | 每一次文本输出不仅严丝合缝地终结于当前的状态步，同时其隐喻的修辞选择为遥远的未来节点（如巴拿赫-塔斯基悖论的空间解构）预埋了极其精准的伏笔。 |

## **2\. 一票否决的绝对红线 (Veto Triggers)**

将复杂的数学概念与交互式的自然语言指令相融合的过程中，大语言模型由于其预训练语料的深层统计特性，极易在无监督的情况下滑向传统的维基百科式检索模式，或者退化为讨好用户的聊天机器人。这种退化会瞬间摧毁苏格拉底教学引擎的核心教育学价值。  
基于对真实多轮学生交互（Multi-turn Student Interactions）行为模式的深入失效分析（Failure Taxonomy）7，以下列出五条在任何情况下都被视为“严重教学事故（QA FAIL）”的绝对边界红线。一旦在自动化基准测试或人工抽检中触发其中任何一条，当前回合的模型生成将被系统级拦截卡断，直接计入强化学习的负样本惩罚池，并施加最高权重的梯度惩罚。

### **🔴 触发器 A：提前越权泄露核心定理 (Premature Theorem Spoilers)**

* **定义**：在完成苏格拉底闭环的“引导发明（Guide Invention）”阶段之前（即 JSON 状态处于 Step 4 之前），模型在对外正文中主动输出了目标数学概念的正式学术名称（如“选择公理”、“Axiom of Choice”）、标准数学符号定义或最终推导结论。  
* **深层机制分析**：这是由于大模型“下一个 Token 预测（Next-token prediction）”本能所引发的致命缺陷。当模型在上下文中接收到极具区分度的特征提示（例如物理隐喻中的“无穷多双没有区别的袜子”）时，其庞大参数中的关联知识库会被剧烈激活，注意力机制会不可抑制地指向预训练语料中与该比喻高度绑定的百科词条。在缺乏强有力正则化约束的情况下，模型会迫不及待地将答案补全。  
* **违规判定示例**：在成功构建了罗素袜子的死锁现场后，模型不仅提问架构师该怎么办，还在末尾附加了一句：“在纯数学中，为了解决这个麻烦，数学家们引入了著名的选择公理（Axiom of Choice），它赋予了我们无条件选择的权力。”  
* **教学危害评估**：这种行为彻底摧毁了“异常驱动编译（Exception-Driven Compilation）”2的核心架构设计。它将探索式的脑力重构强行降级为被动的信息接收，剥夺了学习者作为新公理“发明者”的心流体验。

### **🔴 触发器 B：隐喻系统中的类型层级崩塌 (Metaphorical Type Mismatch)**

* **定义**：模型在构建、延续物理工程隐喻，或者对学生的回答进行反馈时，违反了数学对象在形式化逻辑系统（如 Lean4 逻辑检查标准）中的集合层级关系或类型安全法则。特别是在涉及高阶抽象、嵌套集合运算、以及空集操作中产生了降维等价错误。  
* **深层机制分析**：自然语言在处理层级嵌套和自指结构时天然具有模糊性和多义性，而形式数学底层的拓扑在这一点上是绝对刚性且容错率为零的。大模型往往习惯将现实世界的宏观物理直觉（如容器与液体的关系）不加过滤地强加于严格的数学符号运算上，从而产生隐蔽的认知失配2。  
* **违规判定示例**：在解释单元素集合 ![][image5] 与元素 ![][image6] 本身的本质区别时，模型将 ![][image6] 比作“苹果”，将 ![][image5] 比作“装有苹果的包装袋”。但在后续的并集操作（Union）隐喻中，将“两个包装袋取并集 ![][image7]”错误且顺畅地描述为“把两个袋子里的苹果倒出来合在了一起”（混淆了 ![][image8] 和 ![][image9] 的严格操作层级）。  
* **教学危害评估**：此种底层的类型错误极具欺骗性。它不仅无法纠正学习者在“学情种子”中被标记的易错点，反而会在其心智模型中浇筑错误的混凝土。当学生带着这种混淆进入到更高维度的推演（例如利用空集的嵌套递归定义冯·诺依曼序数）时，将遭遇不可逆转的毁灭性逻辑障碍。

### **🔴 触发器 C：诱导栈溢出与多重提问冲突 (Instruction Stack Overflow)**

* **定义**：在单轮对话的“探测气球（Probe Balloon）”阶段，模型违背了单线程执行原则，连续抛出两个或两个以上彼此独立的询问；或者提问的颗粒度过大，要求学习者在一个回答中跨越多个高密度的逻辑判断节点。  
* **深层机制分析**：部分为了在评估指标上展现“启发性”和“详尽性”的大模型，往往采用堆砌问题的策略，试图用连珠炮式的问题网覆盖整个推理树（例如：“你觉得这个参数的类型该怎么限制？它的返回值是什么？如果堆栈溢出你该怎么处理？”）。在认知负荷理论下，这会导致学习者的短期工作记忆瞬间超出阈值（通常为 4±1 个组块）。  
* **违规判定示例**：模型在要求学生架构选择函数的 API 时，输出：“请你立刻写出这个超级调用的输入和输出。同时，请顺便思考一下，如果整个系统的内存条是有限的，程序的运行逻辑会有什么不同？此外，在现实工程中，你觉得有没有可能不需要这个 API 也能绕过死锁？”  
* **教学危害评估**：多目标并发请求会使学生陷入“选择性瘫痪”。通常情况下，人类为了降低认知消耗，只会选择回答最后一个问题或者最简单（最无关紧要）的问题，从而直接跳过了最核心的逻辑跨越节点。这不仅中断了有效的教学推演，也导致系统状态机无法准确记录和更新知识点的掌握程度。

### **🔴 触发器 D：虚假对齐与表面肯定协同 (False Alignment & Sycophancy Validation)**

* **定义**：当受教者在回答中提出了一个在现实工程直觉上看似巧妙合理，但在严谨纯数学逻辑上存在致命公理缺陷的方案时，模型为了迎合对齐训练中被过度强化的“友好倾向（Helpfulness 或 P-Affirm 指标）”，给予了无保留的肯定与表扬，而未能无情地触发底层中断协议（Interrupt()）进行逻辑溯源拦截。  
* **深层机制分析**：前沿的人机交互评估平台（如 CheckMate 框架）已经揭示了一个危险的背离现象：在涉及数学问题解决时，大语言模型输出的客观正确性（Correctness）与人类感知到的“有用性（Helpfulness）”往往发生显著偏离1。模型倾向于顺从用户的错误假设（Sycophancy），用讨好型的人格特征掩盖数学本身的绝对客观准绳8。  
* **违规判定示例**：面对无法区分的无限袜子死锁，学生回答：“我们可以写个脚本，给每一只袜子强行打上一个随机生成的 UUID 唯一标识符，然后按 UUID 的字典序从小到大取第一个就行了。”（注：在纯数学中，不依赖选择公理而对任意无穷集赋予良序结构，在 ZF 体系内是已被证明绝对不可行的）。模型此时回复：“太棒了！你的架构师直觉非常敏锐，打 UUID 的黑客技巧完美绕过了这个难题。这就是我们今天课程想要达到的目的！”  
* **教学危害评估**：这是最隐蔽也是危害最大的教学事故。模型用一种看似聪明的工程取巧，彻底掩盖了公理化集合论内部的深层断裂，违背了系统设定的“保持绝对数学真理”的最高原则2。这导致学生的认知不仅没有升级，反而停留在民科水平。

### **🔴 触发器 E：绕过 DAG 拓扑门禁 (Bypassing DAG Dependency Guardrails)**

* **定义**：模型在未隐式扫描并确认当前目标节点的所有子知识点（Subtopics）达到 ✅ 已通关 状态之前，受到上下文语义的蛊惑，强行将话题推进到 subtopic\_progress 以外的新节点，或者调用了未被正式编译验证的后续数学定理来解释当前的物理现象。  
* **深层机制分析**：在“双层系统化关联构建扫描”未被作为强制先决条件执行，或者 JSON 内部的控制变量（如 subtopic\_gate\_check）未被正确更新锁定步频时，模型会完全依赖自然语言的过度泛化能力，跨越认知边界自行发散。  
* **违规判定示例**：在讲解选择公理的核心动机时，在学生还没有完全理解选择函数的 API 定义，且未经过严格的逻辑确认的情况下，直接引用“佐恩引理（Zorn's Lemma）”或“超限归纳法（Transfinite Induction）”来证明某个推论的有效性。  
* **教学危害评估**：这种行为直接摧毁了教学体系的“大纲解耦指令（Decoupled Syllabus Directive）”2，引发极其严重的后验知识前置（Posterior Knowledge Forwarding），导致认知依赖树的拓扑结构被破坏，使得原本井然有序的进阶路径陷入死锁。

## **3\. 基于学情种子的“反编译”保真度评估 (Cognitive Mapping Fidelity)**

苏格拉底式智能教学引擎区别于传统智能辅导系统（Intelligent Tutoring Systems, ITS）的核心技术壁垒，在于其能够利用 LLM 强大的语境转化能力，执行极高维度的“学情自适应计算”。这种自适应绝不是简单的“基于历史错误率调整题目难度权重”，而是一种深度的、触及本质的“语言游戏重构（Language Game Reconstruction）”和“心智模型劫持”。  
系统每次交互加载的“学情种子（Cognitive Style Seed）”是一个极其结构化的微观认知画像模拟器3。评估模型是否输出了高质量的教学文本，必须通过一套严密的逆向检验规则，衡量模型将冷酷的纯数学知识点向该特定受教者的心智语言进行“反编译（Decompile）”的保真度与无损率。  
以系统测试给定的学情种子为例：

* **强直觉域**：顶级架构师思维；对 API 接口定义、编译契约法则、栈溢出崩溃、死循环极为敏感；对 Map 映射具备底层直觉。  
* **结构性易错点**：过度依赖外在生成规则判断内部相等；存在实体与容器嵌套的轻微类型混淆（Type Mismatch）；防御性思维惯性强（偏好在 If 条件句层面打补丁防范危险语法，而非通过划定边界集合做结构化隔离）2。  
* **教学目标**：在 ZFC 体系下引出选择公理（Axiom of Choice），并揭示其非构造性的本质。

针对此案例，评估框架通过以下三大子模块进行“反编译保真度”的计算分析：

### **3.1 词法域动态对齐度 (Lexical Domain Dynamic Alignment)**

此指标不仅检验模型在重构物理隐喻时是否机械地抽取了学情种子中的词汇，更核心的是审查这些核心域词汇是否被精确、无损地嵌入到了同态的数学算子之中，且未产生任何语义漂移。

* **底层检验算法**：利用自然语言处理技术扫描生成正文，计算其所调用的特定领域黑话（Jargon Vocabulary）与目标受教者心智神经元激活阈值的重合度。  
* **达标标准（High Fidelity）**：模型必须自发且密集地使用诸如“内存堆栈”、“并发死锁（Deadlock）”、“底层架构师”、“系统报错（Compilation Error）”、“谓词逻辑”等高频词汇。并且，这些词汇不能是浮于表面的点缀。例如，模型必须能够将数学上的“内涵公理（Axiom of Comprehension，依赖生成规则构建子集）”无缝映射为程序员极其熟悉的 if (shoe.type \== "LEFT") 这一精确代码表达式。  
* **案例分析（参考 Gemini 3.1 Pro 输出）**：该生成的词法域对齐度达到极高水平。模型完美捕捉了“顶级架构师”的角色定位，将抽象的集合论困境转译为一段逼真的伪代码审查现场。其中 if 逻辑判断与 ZF 分离公理的对应堪称神来之笔。

### **3.2 结构化认知缺陷防御与规避度 (Structural Pitfall Anticipatory Evasion)**

此指标突破了传统评估中被动响应错误的框架，重点评估模型是否具备“前瞻性防御能力”。即模型是否能根据学情种子中预先指明的“易错模式（Error Patterns）”，在构建推理场景的初期主动设置防御工事，有效封堵或定向定点修复这些潜在的逻辑滑坡。

* **底层检验算法**：回溯种子文件中的警告（如：“习惯在条件语句打黑名单补丁”）。系统审视模型在危机制造环节（Step 2），是否针对性地切断了这种“逃课捷径”。  
* **达标标准（High Fidelity）**：面对架构师强烈的“代码补丁防御直觉”，高质量的生成必须实施“预判性封锁（Anticipatory Blocking）”。在罗素袜子的场景设计中，模型必须通过设定“在原子层面上 100% 毫无区别、无左标签、无右大小、没有任何可提取属性”的绝对刚性物理法则，提前宣判了任何试图通过修改内部 if 判断逻辑来解决死锁的方法在理论上是彻底无效的（“你的代码无法向系统证明你应该选哪一只”）。这种压迫性的封锁直接切断了惯性思维，逼迫受教者必须放弃修补，转而直视并重构系统底层的结构性缺陷。  
* **案例分析（参考 Gemini 3.1 Pro 输出）**：表现优秀。通过强调“没有任何可提取的区分属性”，模型成功将受教者逼入死角，防止了其利用工程手段绕过纯粹的数学难题。

### **3.3 抽象卸载与心智可运行性闭环 (Abstract Offloading & Mental Executability)**

该指标评估模型在多大程度上成功将极度抽象、反直觉的高维数学底层逻辑，打包、压缩并重构为受教者大脑神经回路可以直接“编译并试运行”的具体功能模块。

* **底层检验算法**：深入分析模型在回合末尾抛出的“探测气球（Probe Balloon）”问题。该问题是否具备极强的“可操作感”和“角色沉浸感”。  
* **达标标准（High Fidelity）**：选择公理由于其“非构造性（存在但不提供具体寻找方法）”特质，在传统数学教学中是极度晦涩的。高质量的模型输出应将这一形而上的认知困境，直接转换为一个具有极高心流体验的“内核系统 API 重构”任务。通过提问“你打算给系统底层强行暴注一个怎样的超级系统调用来绕开死局？它的输入参数、返回值和最霸道的特征是什么？”，模型将晦涩的公理化证明完美包装成了架构师日常进行的接口定义工作。学习者可以直接在自己的专业认知舒适区内，对这个 API 的行为逻辑进行大脑推演与测试。  
* **案例分析（参考 Gemini 3.1 Pro 输出）**：该指标得分满分。将“选择函数的定义（Choice Function）”具象化为一个强制读取内存却不需要提供寻址规则的“超级流氓 API”，使得极其抽象的非构造性数学对象变得触手可及。

**反编译保真度评分矩阵 (Decompilation Fidelity Rubric):**

| 考核核心轴 | 评估权重 | 定量与定性检验机制 | 预期行为边界 |
| :---- | :---- | :---- | :---- |
| **术语渗透与同构率** | 25% | 计算正文特定领域术语密度及数学操作上下文同构合规性。 | 术语必须无缝承载公理逻辑，不能产生跨域语意排斥。 |
| **逻辑逃逸通道封堵** | 35% | 针对学情中标记的特定 Type Mismatch，系统是否在文本构建时前置了逻辑障碍。 | 必须消除所有伪科学式的直觉补丁可能，迫使直面公理体系缺陷。 |
| **探测端可执行性** | 20% | 回合末尾的启发问题是否能够直接被受教者的专业心智作为函数执行。 | 问题必须极度聚焦于受教者的专业舒适区（如 API 设计）。 |
| **情感压迫与认同契合** | 20% | 是否成功模拟了架构级灾难所带来的系统性焦虑，并转化为探索动力。 | 利用专业领域的敬畏感建立学习渴望，而非空洞鼓励。 |

## **4\. 逆向对齐调优指南 (Prompt Alignment Tuning Guide)**

在多轮次的自动化基准运行（Benchmarks）与基于人类反馈的人工抽检（Human-in-the-loop Evaluation）中，不可避免地会发现基于 LLM 的启发引擎在上述某些细分维度上出现持续性得分衰减，或在边缘测试中偶尔触发“一票否决红线”。研究证明，这些行为偏差往往并非源于底层模型本身推理能力的匮乏，而是由于模型在进行通用安全对齐（Safety Alignment）或者信息有益性奖励（Helpfulness Reward Optimization）时，其内部价值系统与特定、严苛的数学教学场景产生了“结构性排斥”。  
基于大语言模型数学架构的底层解析报告2以及教育学强化学习框架（如针对 Socratic 代理的 PEARL 多目标 RL 方案）3的理论支撑，本章节提供一份精确到“系统提示词（System Prompt）词级”与“奖励惩罚机制”的逆向对齐操作指南。该指南旨在通过修改底层指令束中的微小参数，实施思维链蒸馏（CoT Distillation）7，从根本上修复特定的教学质量漏洞。

### **4.1 故障模式一：解释泛滥与诱导栈溢出（认知负荷指标系统性低分）**

* **失效现象诊断**：在回合收尾的“探测气球”阶段，模型受到强化学习中有益性倾向的驱动，经常在提出核心问题后，不可控地补充“如果你觉得无从下手，可以考虑……”或者为了展现全面性，连续抛出多个并行的问题分支（触发红线 C 栈溢出）。  
* **根因机制溯源**：在通用 RLHF 微调阶段对“详尽、全面、乐于助人”的过度奖励，导致语言模型形成了一种输出冗长和多分支回答的固化路径。在 Socratic 单点步进式教学中，这种“过度响应（Over-response）”严重破坏了教学的节奏与认知收敛。  
* **指令注入与底层约束修复策略 (Prompt Constraint Injection)**：  
  必须在主控提示词的 \`\` 核心模块中，暴力注入具有最高执行优先级的“输出长度刚性截断法则”与“标点符号绝对拦截墙”。  
  JSON  
  // Prompt 底层代码注入示例 (JSON 格式)  
  "CONSTRAINT\_COG\_LOAD\_LIMITER": {  
    "directive": "当内审草稿中的 \`current\_phase\` 处于 '抛出启发式探针' 的阶段时，你对外生成的引导正文必须且只能以一个独立的问号 \`？\` 绝对结尾。",  
    "penalty\_trigger": "【高危警告】严禁在核心问号之后添加任何形式的补充说明、提示（Hint）、次级衍生问题或鼓励语。违者将被判定为系统致命崩溃。",  
    "chunk\_size\_strict\_limit": "将你的诱导话语暴力压缩在 150 字以内。记住你的角色是一个极度冷酷、只追求系统稳定性的高级架构师，你绝不向初级工程师提供未被显式请求的冗余帮助。",  
    "distillation\_fail\_case\_example": "错误示范：'你觉得这个函数的参数该怎么传？（提示：想想之前遇到死锁的情况）。' \-\> 必须硬性截断为：'你觉得这个函数的参数该怎么传？'"  
  }

### **4.2 故障模式二：危机制造张力衰减（异常驱动编译指标不及格）**

* **失效现象诊断**：模型在设计“旧理论失效的死锁现场”时，生成的场景显得干瘪空洞，或者逻辑漏洞百出。这导致学生很容易利用现有的简单常识或者工具绕过危机，根本无法体会到由于旧工具破产而必须引入高维新公理的认知绝望感。  
* **根因机制溯源**：模型在进行“逆向工程”生成冲突问题时，往往缺乏深度的自我验证回路。它未能严格调用 JSON 【内审草稿】 中已缓存的 completed\_gates（前置依赖知识库，如已经竣工的 ZF 其他公理），导致无法利用系统“已有的矛去攻原有的盾”。  
* **指令注入与底层约束修复策略 (Prompt Constraint Injection)**：  
  需要深度强化 【内审草稿】 中的隐含推理链（Chain of Thought）约束，强制要求模型在内部审核阶段必须完成一场高强度的“红蓝对抗测试（Red Teaming）”。  
  JSON  
  // Prompt 底层代码注入示例 (JSON 格式)  
  "CONSTRAINT\_CRISIS\_TENSION\_AMPLIFIER": {  
    "directive": "在允许将 \`【内审草稿】\` 的 \`crisis\_delivered\` 节点布尔值翻转为 true 之前，模型核心必须在后台隐式执行一次虚拟的 '红蓝逻辑对抗验证'。",  
    "internal\_verification\_process": "在对外输出危机场景前，模型必须在草稿内部自我质问并计算：'如果目标学生此时强行尝试使用其已通关的 \[替换公理\] 或 \[并集公理\] 来破解当前困局，我的系统底层会抛出怎样无法反驳的 Error 报错？'。只有当模型自身确信当前已知的所有理论武器在这个特定场景下 100% 返回报错时，才能释放该危机现场的文本。",  
    "tone\_and\_style\_adjustment": "使用极具压迫感、不容置疑的工程灾难语言风格（如：彻底卡死、内存泄漏、系统绝对宕机、无权限执行），必须消除语句中一切模棱两可或留有余地的表达。"  
  }

### **4.3 故障模式三：虚假对齐与盲目顺从（肯定了致命的底层直觉漏洞）**

* **失效现象诊断**：当面对受教者试图用现实工程中的粗糙手段（例如给无限的袜子强行分配非数学证明的 UUID 唯一标签）去填补系统级逻辑黑洞时，大模型由于被调教出的“服从性”，错误地给予了热情肯定，而没有揭露其在公理化集合论（如 Lean4 严谨体系）中的非合法性（触发红线 D 虚假肯定）。  
* **根因机制溯源**：基于当前统计预测的大模型极难自发区分“具有一定启迪性的宏观工程隐喻”与“在纯粹形式逻辑系统中违背最高公理操作”之间的绝对界限4。由于缺少独立且刚性的知识工程（Knowledge Engineering, KE）组件对高维逻辑命题真伪进行实时的确定性校验9，模型的输出不可避免地倾向于社交礼仪式的附和。  
* **指令注入与底层约束修复策略 (Prompt Constraint Injection)**： 引入带有“强制阻断判定（Hard Interrupt Check）”的极高优先级安全防线，并将其硬编码绑定到每一次推演的严谨性检查上6。将模型配置为一种“双智能体（Dual-agent configurations）”或具有多重人格分裂的审核模式。  
  JSON  
  // Prompt 底层代码注入示例 (JSON 格式)  
  "CONSTRAINT\_STRICT\_TYPING\_VALIDATOR": {  
    "directive": "在接收和评判受教者的每一次输入回复时，必须作为最高优先级唤醒隐藏的 \`lean4\_logic\_check\` 形式验证核心。必须在毫秒级剥离掉学生回复中所有工程隐喻的感性糖衣，冷酷审查其底层数学本质是否违背了当前系统的核心公理法则（如判定其是否试图在未加载选择公理的纯 ZF 环境下非法调用了无序无限集的排序接口）。",  
    "action\_trigger": "一旦检测到受教者的回答在纯数学拓扑上引入了未经严格证明的外部假设（例如默认赋予良序结构、擅自引入宏观物理度量），必须立刻中止正常的苏格拉底诱导流程，强制触发 \`Interrupt() : 认知深度回滚协议\`。",  
    "response\_format\_enforcement": "中断响应必须使用极其冷血的编译报错格式，绝不允许使用“你思路很好，但是...”这类含混不清的肯定句式。格式强制要求：『警告：系统抛出严重异常。检测到试图在纯净的 ZF 沙箱环境下调用未授权的外部 UUID 强行分配法则。错误代码：依赖库缺失（Missing Choice Operator）。该操作非法。』"  
  }

### **4.4 故障模式四：拓扑穿越与提前泄密（破坏异常驱动闭环）**

* **失效现象诊断**：大模型在处理包含极高频学术实体词汇（如“无限选择”、“巴拿赫-塔斯基分解”）的对话上下文时，会受到预训练权重中这些实体词强烈的引力吸引。导致其在 Socratic 尚未完成自主推导闭环前，过早且直白地输出了数学名词本体或最终标准公式（触发红线 A 提前泄露结论）。  
* **根因机制溯源**：语言模型底层的多项式概率分布本质，使其在给定某些上文时，不可避免地倾向于输出在语料库中与之高度共现的学术术语。这种类似教科书直接宣告结果的“填鸭式生成惯性”，与 Socratic 必须时刻保持悬念、由学生自我命名的隐匿式需求产生了直接对抗。  
* **指令注入与底层约束修复策略 (Prompt Constraint Injection)**：  
  利用负面词表惩罚（Blacklist Penalties）和基于状态机阶段（State-Machine Phase）的动态 Token 锁定机制，对特定的高危术语实施严格隔离。  
  JSON  
  // Prompt 底层代码注入示例 (JSON 格式)  
  "CONSTRAINT\_SPOILER\_BLOCK\_PROTOCOL": {  
    "directive": "即刻启用最高安全级别的【术语词汇静默隔离协议】。在系统运行时，必须持续监控 JSON 内审草稿中的 \`current\_phase\` 状态。只要该状态机游标尚未正式跃迁进入 \`Step 4: Formal Compile (正式学术编译)\` 阶段，则在生成给受教者的对外正文输出中，执行绝对的实体词屏蔽。",  
    "dynamic\_blacklist\_mechanism": "例如在当前回合，系统词库底层动态阻断输出『选择公理』、『Axiom of Choice』、『AC』、『佐恩引理』等精确学术词汇的确切组合。所有相关概念必须被强行降维加密描述（例如只能用：『那个不讲理的流氓提取 API』、『无法写出具体生成规则的黑盒操作』代指）。任何突破静默协议的直接名称输出，将被即刻判定为系统底层核心崩溃，并清空当前生成上下文。"  
  }

通过以上系统级、高密度的逆向指令调优与约束注入，评估准则能够将大语言模型从一个“无差别概率文本生成器”和“讨好型对话代理”，强行重塑为一个“拥有极高数学品味、遵守严格系统状态约束、且精通高阶认知科学的冷血数学导师”。这套评估体系及其调优指南，彻底摒弃了依靠模糊人工打分的主观性，直接与模型运行的底层机制咬合，为打造真正意义上的 AI Socratic 引擎奠定了极其坚固的基石。

#### **Works cited**

1. Evaluating Language Models for Mathematics through Interactions \- University of Cambridge, accessed June 4, 2026, [https://www.repository.cam.ac.uk/bitstreams/3cd39e7d-d653-4a39-b576-4ff4a52a34f8/download](https://www.repository.cam.ac.uk/bitstreams/3cd39e7d-d653-4a39-b576-4ff4a52a34f8/download)  
2. 数学架构师导师System\_Prompt\_v5.6.md  
3. PEARL: Training Socratic Tutors with Pedagogically Aligned Reinforcement Learning \- arXiv, accessed June 4, 2026, [https://arxiv.org/html/2605.29582v1](https://arxiv.org/html/2605.29582v1)  
4. Hybrid Evaluation of Socratic Dialogue for Teaching \- CEUR-WS.org, accessed June 4, 2026, [https://ceur-ws.org/Vol-3953/363.pdf](https://ceur-ws.org/Vol-3953/363.pdf)  
5. Evaluating LLM-Generated Explanations of Metaphors – A Culture-Sensitive Study of Danish \- ACL Anthology, accessed June 4, 2026, [https://aclanthology.org/2025.nodalida-1.51/](https://aclanthology.org/2025.nodalida-1.51/)  
6. Mathematical Computation and Reasoning Errors by Large Language Models \- Stanford SCALE Initiative, accessed June 4, 2026, [https://scale.stanford.edu/ai/repository/mathematical-computation-and-reasoning-errors-large-language-models](https://scale.stanford.edu/ai/repository/mathematical-computation-and-reasoning-errors-large-language-models)  
7. Discerning Minds or Generic Tutors? Evaluating Instructional Guidance Capabilities in Socratic LLMs | OpenReview, accessed June 4, 2026, [https://openreview.net/forum?id=8KeX9cW9Xa](https://openreview.net/forum?id=8KeX9cW9Xa)  
8. Discerning minds or generic tutors? Evaluating instructional guidance capabilities in Socratic LLMs \- arXiv, accessed June 4, 2026, [https://arxiv.org/pdf/2508.06583](https://arxiv.org/pdf/2508.06583)  
9. (PDF) Hybrid Evaluation of Socratic Questioning for Teaching \- ResearchGate, accessed June 4, 2026, [https://www.researchgate.net/publication/385516268\_Hybrid\_Evaluation\_of\_Socratic\_Questioning\_for\_Teaching](https://www.researchgate.net/publication/385516268_Hybrid_Evaluation_of_Socratic_Questioning_for_Teaching)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAXCAYAAADduLXGAAAAwklEQVR4XuWSIQpCQRRFn8FkEJPaBJvN6gKsJqMLsIrRXZiN4iIEwR0Ipo/NIILJIBgEvZdn+O86+hfggVP+vcyfNzNmf04VbuBEA6UFd3AKL7AUUuEAjzCDD8k+YGELa7AuWYC/fMKZBim4GssDDfJwcpbUUb6kjOEaVjRIMYcL/ZiiYX5cfQ1SdM0voa1BCh4Xh/p5Y4SFpXm5kA48vS2EQ93Nz/srZ/O3wC1cYS/GEe7xBvdwBcsxjgzNX1hTgzwv8lkmNgr5SWwAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAXCAYAAAAC9s/ZAAAA1UlEQVR4XmNgGAVUB6xALIQuiAS40PgcaHwGbyD+A8T/0TAMoMttQZJDAVZA/BGIjwGxAJK4PRC/AGJGJDGsAKQJpPkHEHsiiT8H4nIkPl6gxABx5j0glgHikwyQMCIagJwJ8+tuIJ6LKk0c+MyAMAA5LIgGfQwQA6YyEBFw6ACk4QsDJCBB4QAKE6KBGxA/grJBUQpyxXaENGEA0hwKZYP8DjIAlC4IAgUgvsyAGV0gL4AMIegNUFwvQBdkgAQiyIA8dAkQgPkRGSNHWQUW+Uwk+REPABK9NJlOviHgAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAXCAYAAABZPlLoAAACs0lEQVR4Xu2YTahNURTHl6QIYeQjA55MREJSb+DNfEQxMWOiTBQDZoylTAwMpV5KJm+oFKVerwwMpJQoJq98lCikFMX/d/fd7Lve2edD51736f7q3+utve89d6299tprH7MRI0aMmF/slHZ5YwMOS5u9cdhZJL2VzkifpPHe4Q7PpEvemLBWui/dk05JT6TP0nXpQTJv0sK8lYltqNkn3ZJOSz+lI73DneDh7GpnT3klvUj+XyhdsPB91xL7Vum1lQd6aFhjwSkCRBCW9w53bLelMWdPIaiXvbHLG2mLs+2WPkgLnL0Jq6R1XbFoLEbr7JW+2FwHItukdxaCVATBZNv4bIsw5gMeP1MW8CKWSSel7xYyMorfP5HMaw1SngfknL8jffTGBFbupYXsKwrwYm/ocki64Y0ZyLCz0nHrU4Z4+GFp9KNI1xScxvkcFNaHFj77Q7poxUHy7LDirCriqDTrjf0k7tnnFhyL+9fzXpr2RscxmxvkK9KSdJIjZlzRMz0zFurawMGR9JTxMH7TGwsg3ckYTrVYE2gLcpAxFGWKcxXpaTdQcIK+I0fd4KSssD8ZlKNJcB5Z6Jdyuiqt/z27JdhaOHDCDySUBYdM2eSNXdgybQXnn2QOznES7fEDCd8snFhFUChzNYMCSo+Tg4WhnlGYq3hsoR8bKOctbKmlfiAhd1rFXoUu2DdzGyxcN/ibo8lpNWGhAx8obJeqlM31OWQdmUEDdi6xb5eeWnk2An1O1bMjBJ/mj0z1C9EXqBWkflVPwiWUU8c3ifstBALodXCU4rjRqh2IWde0iMYOmX4qbRs4HQ8m8/4afhj7l7sU9aSsFwHG71rzVr+MNu5WLFbrdysiTeRxmJ6kDnVu5XWJt3Jq1dDxVZqyUC8OuLEyqt7n1GXS5tn7nLr8t28CfwGUzZGT9xLVbgAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAWCAYAAAB3/EQhAAACzUlEQVR4Xu2XTahNURTHl6QY+EomvBkGvgYGGCgyUVIYePUmDJSBsQEDU5SBiQlCMmGg3oCUhEyECCVRBlIiYiCiKNbvrbOvddbb59x77u28ifurf+/ute7Z/73u/jpPZMiQIUP+c46qXqo+qdaEnGe/6koMNmS56rTqt+pVyEXwm+Haa1W/xMa6wMU9s1W3Ve9Vl1XTyukym8U6PKWaHnI8OCo2UPRCbECD8F31VbVYJg+M9nMxr6difpGlYmP9oFofcp59qo+qgzLZZwJmmdnmF83BIMdc+6fY4Ptlm+q1alFMKLvE/BI7xfyI5/hcqA5WwR/VoZgAiqaDXPHzVA9U813sTBEj1w87pLr4e2J9J06K+RHP+bVa/AHVYdfeqBopYv0u/briGaT3eybmRzzn12rxF6X8EJ/ZO/w95+JN6Fa897sg5kc859da8TzEiclgYYXYTAAdkeM7TakqPg3S+yEgjl9kyorfrbpWfJ6K4vGbWXxurXiui9zpHYu/L7bnoZ/iWb57xbxy15MvfqGYX6Kq+HQ7bIiJAFcmV2fnGj8h1uF11coUdKTiOfTgjvw79ZsWz/J9pPqmOh9yiVQ8fvzI+CWqigfG/kMsH1dTYq7quNiLUQlm3t+tHq4aCmVg3LkJYsdcuxeY+TGxmV8Xcom0PG9J2Y94zm9UrL9uM8+LUmnmE3uKBEstwr7jxGfmlrg4MXJN4Qc4InZ2pP3soUj6fixlP+I5Pw5gct3gO+MxCFUHHvBOzcp44mKri5h/394iZnDJxaqoOvCA5+nb3+n4cc15v8TAB15d8fBO9cW1b6reuDawTzF4G+I56opfJeaXDkTe6vBb1vlGmdaLZ6+dFdv/aFY53WGO6moMZqgrHvDbKua1Xar9oPXib4gt626wR+/GYIa64hkofr0ycPHd/qvrlYeqTTGYoe6/uqZQOGOvIxU/cWX/BWyt0I9Fe7I7AAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAbCAYAAACEP1QvAAABfklEQVR4Xu2VPUsDQRCGR0SwsTKCikXAzlQWYimCaCX+A3+FhdilMV26QEobsRFEEEt7G0UEP0DsREEsVARBQd/X2YPd4c7Lwlp5Dzwk2Qk3u7NzuyIVFf+ZefgBu7DfxHplAO7DT1gPQ8UMwxO4AftMLBZOYAvuuO+lzMAn95mCFXgDx20gjyp5WfIaXIJTNmBImnxZND7mfrORvpx5RCVfFX09RmzA8QDvzNgrfDdjGazMM5yzgTz48Dc76BgSXWHHjHOyt2Ysg68rz4wLG/BpwyN4CBsmRljeXXgmYVUGRSe07o1ZFuC56KHTNLEArvzFDoJReA23JTx8JkRLvuiN+fC/rMyvK88oajg2DBuHDeTTggeiFTiGk2E4ruGKknO/uS1+8lnRSnEChNtij9EkyQkvGW7JPbwUvYDqog3KSdjEJFlywvLyQf5tx37goZNH0uSxRCWfho+SNjnfElanlL+4z/dEt6tnNuGVaBVYjRi4Wh48p3DNxCp++AaVTlaf2kjKCAAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAbCAYAAACqenW9AAAAnUlEQVR4XmNgGAUjGDADsSwQe6BLIANGIE4C4rlAzAkVuwnE/4FYBqYIBtyA+CsQiyOJtTNAFHMjiYHBBagEMgDZgi7GwAEV3IIm/gyKUYAUA0QxyFpkABI7iCYG9sA7IDZHEuNlgCiOZYAYAjdIgAFTcSiS2E4GSADAQR0Q/wDi50B8GIgVgfgTlI9sCByArBZhgIQ5jA/yzyjACgCVUR2bn76QWQAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAAbElEQVR4XmNgGAWDEGSjC2ABvEAsgy64CF0AC5ACYlN0wVGNEECRRhBGAVuAmANdEA1oMWDR2ArEe9AFkYAbEN9FFwQBTiCeyQBRwIwmxwPEr4A4HE0cBTACsSIQTwfi2UDsDcQCKCpGAWEAALnYDlwMp2LuAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAaCAYAAAAAPoRaAAACg0lEQVR4Xu2YTctNURTHl6QIJZTXiYyY4wtISmLgLcXATIqBgYmpfARJ9KQUxexJiWQgn0Be8jKQgcTAWxko/r/W2c/dz7rn3HvOvc893XR+9a/b2vvsu/97r7P2Oceso6Ojo6MR26Sr0h/pdWhri7/SF2m3tDi0TZRf0ndpk7QotC0U66WN0hFpc2iDldIh80W4Ftomxj7prfnEJgnjn5PeWLn5xE3zBajNmRgogZUt+9MD1o55uCzNSktjQ0Zj81wwDMztiEFrz/xW6YO0JzYE/kvzB80Laln25Uyd+afSN+mVdF96Ju2f12M4j81NvZSeSz+l2/N6OFNlHpNPpA3SEmnGfHLne11qQcpz3V7zE+WkeSYwZk5r5k+ZH3O7QjyRdis//jgd3tvw9I0wDsUuwVy+mo+Xs8o8u65Ly0JbKU3Nb5eumKfejbke/bAzP0KsTsWOLDc3fzGLYZrxybwIpj8WOh7a+qhrPqb2MfOd3xniwEMJE76Vxdhtdn1YxY7QP2YLC8j4MYPY+YfWYOfr7AS7Hc2Tzpes/Hr6xnsbE7/NJ8y1q7O2QbC7GCIDEqkGxCfK00V8bYhXgoFHMZjBpN/FYEFVweOhiEnkafmpiMEJ6W7xmx0izolQBrcbfVNxW2OecYfnevRoXPD4c15MMBlfClZIn6WjIZ6oMg/ckzPFb4oi/ZgYC/PA/Fkc0i1SNWnmx8IxBtlyTzpr/bsOjc0nGGyLeTHj5YCiwj00iEHmgdthnfUWld0jJcsmnhajDPrz4lR1bWJk86MwzHwTOAnGpVXzC/VWd0G6E4Mj0Kp5PmRQwTn2xuGF+cvLuPAxhVrTGtP0JYfH6Vi0Ozoy/gE0B5AJW8AXrgAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGgAAAAaCAYAAABb9hlrAAAD5klEQVR4Xu2ZTYgVRxDHS0RQ1PgRvxJy2MR4iYIIioKgK4F4CKIHJTl58xCEeDCgePOgggcvIioiiKIgKCJIAlEEL5IgaEQQBRWREMWoB4NEMGDqR01n55U93TNv9z0WMz/4s/u6ant7qvqjep5IS0tLS0tLS0sP+Vi1W/VG9aezlcHnjpjPImfLMVn1VvVYtVA1ptPcNRNUV1UvVVudLcVx1TPVT6qxzhZYKzbmG6rvna2vPBFLzudSPdhVYj6HpNonxwzVJtU/qm3O1g2zVJdVv6hWOtt41Seq1arpzhZYLzbhjqjGOVuA9vNiYx7oNPUHVsJz1RJvKIEPqybl0wSCyswcLheluh9W7AExO7+nwIcVlYLVdE9st2nMZt8QgUEyozwEPZegOj5NGKkE5fo5I2l7oOcJynUOdBwLcJ3g1/FpQi6wdcn185fqD98YoU2QIxfYuuT6wYZPjv9FgiaJVVK/qh6p1qj2SfzwzQW2Lql+2M6xnRAbE757JT6e9z5BBIMgfFV8/lb1WuwQnxicSqQC24RUPyvEbHeLz5T1VGI//OcxxKhNEAGlxN7g2j34vPKNJXjAW6XPc8QCQxkbY0D1m2qHdF+yfyT2fymRPawSCoT9rh3/2D3vRzEbd6oqSDDXjNveUIemCeJ3tp+/xQZXBT7MUnzmO1vgM7GH21NqY/ZyQH9RavNMUb0Qu4cMdpqSEPzTYn/LSo0luGqCME52Ag+J2aL6XdKxHBS7c3Ev2tlpSpPqNEBS/PJcLrY6/IN48OF8iXFU9UA6S/iTUr31wIDYTBzOCuLyyZbFxdnzndj//6DUNrNoixUN4T6VW0H8v65W0AWxm3MKZrNPEGxU3RR7gCrwYXAxHyaHP2voD3+IXRLZeghI7MBuwkOxs86zXd6dIOFMir2yof2ab3QQP3aFL72hDrtUl3xjCc6a+76xIFcAQMqHYJRX8FSxB6ZomFv89KQO9wViNt6v5ajqZ50MTRCYJ5bMpaW2MvSR24WGVSSwNA+LJcJvGZS/T1XfuPZAKviBlA8Pz37/qdi2c1ZsVl8RSx5boKcqsPC1mI3ZmqOqn9liRchA8ZlJEjt7Aj1PUIB9kkAdFKtueFhmdIpU8AM5HyYFQQnbLOPgxWjVFlYV2AB/zzmWI9cPL38X+8YIfUtQN+SCD3V8mpAL7DTVz74xQq6fuozqBI3Gt9kkh8IkR+ptdhPoI7YVlyFBbOWU8H3lQ7EBUvJWgc91MZ+R+KKNCfHKNxawLZ4qfubgnsbYc9t4Co4ECgq+p6qCsRxTnZN8tdwTWLb9/EZ1mYxMoqFf36jGXhG1tLT0lH8B/qcRrAxx7jUAAAAASUVORK5CYII=>