# **大语言模型驱动的需求对齐与立体建模机制调研报告**

在构建人机协作工作流系统的初步阶段，“需求建模”的质量直接决定了下游工程的成败。传统的软件工程依赖于人类分析师通过漫长的迭代对话来挖掘隐性需求，而当引入大语言模型（LLM）作为协作主体时，系统的核心挑战从“如何收集信息”转变为“如何确保人机双方对同一需求的理解达到立体且绝对的对齐”。本次调研旨在全面解剖当前学术界与开源社区中，致力于将模糊的初始意图转化为结构化共识模型的现成机制与底层方法论。

## **检索边界、截断现象与空集记录**

在进行穷尽式调研时，界定信息获取的边界、盲区以及检索系统的物理限制，是确保调研结果具备全集参考价值的前提。没有任何检索能够覆盖绝对的“全集”，因此本节明确记录了检索的覆盖范围、遇到的截断现象以及明确返回为空的方向。这些记录可作为后续防范“漏选”事故的系统性基准。  
在本次调研中，使用了多维度的交叉检索策略，主要涵盖学术文献库与代码托管平台（GitHub）。使用的核心检索词组包括直接匹配域（如 "requirements elicitation" LLM、"conversational requirements elicitation"）、机制与特征域（如 "flipped interaction pattern" prompt、"grounding in communication" LLM requirements、"information entropy" "requirements engineering" LLM），以及基于线索的已知实体扩充（如 ReqElicitBench、OntoAgent、RequireCEG、iReDev、PromptKit）。  
在深挖这些检索词组的过程中，多个逻辑上应当存在或具有高潜力的方向，在现有的开源社区与学术发表中返回了空集或极度稀疏的结果。首先是基于绝对信息熵阈值驱动的追问机制。检索了 "information entropy" "requirements engineering" LLM agent 等组合1。虽然学术界提出了利用信息熵来解释需求异常、测量隔离能力或进行多模态因果分析的理论2，但在 GitHub 上并未找到以“信息熵降至某一绝对数值”作为停止追问条件的开源对话系统。目前的追问停止机制多依赖于大模型的主观判断或静态本体槽位的填满，缺乏纯粹基于信息论数学阈值的工程实现。  
其次，基于认知科学中心智理论（Theory of Mind）的显式需求对齐框架也呈现出明显的真空。检索试图寻找明确利用大语言模型的心智理论能力，在需求沟通中建立“你认为我想要什么”的显式状态机的代码实现。尽管学术界对“沟通中的基础构建（Grounding in Communication）”有极为深厚的理论积淀，探讨了隐性知识的解包与交流4，但在需求工程的具体开源实现中，并未发现直接将这种双向信念状态机（Belief State Machine）作为追问停止条件的完整工程化项目。  
此外，在检索系统本身也遭遇了严重的物理限制与长尾截断。在使用诸如 site:github.com "requirements elicitation" agent OR prompt OR tool 等宽泛词组进行检索时7，极易触碰搜索引擎的返回数量上限。由于 GitHub 内部搜索对代码库 README 和具体代码内容的权重分配机制，大量潜藏在个别 prompt 文件或子目录中的实现会被直接截断。例如，许多个人开发者编写的需求反问脚本或提示词并未被有效索引为独立项目，系统的能见度高度向 MetaGPT、ChatDev 等具备高星标数的大型多智能体框架倾斜12。这种平台级的截断效应使得“没有任何文档描述该纯提示词流程”成为一种检索错觉，企业内部的 SaaS 产品工程细节亦因商业机密壁垒而无法被开源检索引擎触及。

## **现成实现与机制形状图景**

本节对目前开源社区、学术界及产品框架中存在的“需求对齐与展开”机制进行详尽的结构化解剖。这些候选方案跨越了从底层提示词工程到复杂多智能体协作、再到神经符号推理的不同技术栈，各自呈现出截然不同的机制形状与产出形态。

### **经验本体与知识驱动型机制**

此类机制的核心在于通过领域专家预先或动态构建一个概念骨架（Ontology）。在人机交互过程中，模型不再漫无目的地发散，而是不断对比当前对话状态与这个预设骨架的差距，以此引导追问，直至骨架被完整填充。  
OntoAgent 是该领域的典型代表，其相关实现伴随学术论文《From Chat to Interview: Agentic Requirements Elicitation with an Experience Ontology》发布15。该机制采用“经验本体（Experience Ontology）”来指导动态追问。系统将需求关注点组织成一个包含“方面（Aspects）”、“维度（Dimensions）”和“槽位（Slots）”的三级分层树结构16。在展开需求时，OntoAgent 通过四个核心操作进行循环：首先解析用户意图，随后对本体树上的槽位进行相关性打分，接着对未探索的槽位重新排序优先级，最后通过门控剪枝剔除无关或已满足的槽位16。模型根据优先级最高的空缺槽位结合对话上下文，生成自然语言反问。其追问的停止条件极为明确：当经验本体树中所有相关且高优先级的槽位均被填满、被剪枝，或达到系统预设的最大对话轮数时，追问即告终止16。这套流程最终产出结构化的本体实例，其中包含了从隐性需求中挖掘出的交互（Interaction）、内容（Content）和风格（Style）维度的具体需求描述17。OntoAgent 的方法论高度可提取，其将“问什么”交由结构化本体与评分算法控制，将“怎么问”交由大语言模型处理的逻辑，可完全移植到下游业务中，目前作为学术原型项目无明确商业限制16。  
同属于本体驱动阵营的 OntoChat 则提供了一个面向对话式本体工程的交互式框架，旨在通过大语言模型克服多方协作中的模糊性和系统性偏差19。部署于 GitHub 的 King-s-Knowledge-Graph-Lab/OntoChat 项目通过多轮对话，引导用户创建用户故事（User Stories），并从中提取能力问题（Competency Questions, CQs）20。其内部深度使用了参与式提示（Participatory Prompting），通过预定义的提示模板来细化角色、目标和场景23。OntoChat 引入了发散-收敛（Divergent-Convergent）思维模型作为停止条件的判断依据25。知识工程师在交互式画布上审查生成的 CQs，当判断问题集既不至于太少而遗漏关键信息，也不至于太多而导致信息过载，且充分定义了目标领域的边界时，即可认为对齐完成25。最终产出形态为结构化的能力问题集与初始本体草案20。作为一个基于 Gradio 开发的完整交互式框架，其“提取并测试能力问题”的方法论可以直接提炼并用于立体的需求对齐系统构建22。

### **神经符号与逻辑约束型机制**

大语言模型在自然语言处理上具有显著优势，但在严格的因果逻辑和一致性维护上却存在固有短板。神经符号机制通过将大模型与形式化逻辑图谱深度绑定，确保人机双方对需求的理解在逻辑因果上达到绝对的一致。  
RequireCEG 项目展示了这种范式的巨大潜力，其理论基础见于论文《Think Like an Engineer: A Neuro-Symbolic Collaboration Agent for Generative Software Requirements Elicitation and Self-Review》26。在该架构中，大语言模型负责高层语义推理，而因果关系图（Causal-Effect Graphs, CEGs）则负责逻辑符号审查1。在展开需求时，系统首先使用特征树（Feature Tree）对用户模糊的初始叙述进行层次化分析，界定系统行为的范围；随后，基于这些需求构建自愈合的因果图，精确捕获原子前置条件与行为动作之间的因果关系26。RequireCEG 的追问与优化停止条件依赖于底层的逻辑审查机制：当系统自动进行的逻辑形式检查和逻辑语义检查（Autonomous Logical Formal/Semantic Check）在因果图上不再发现歧义、死结或缺失的边缘情况时，需求对齐即告完成1。其产出形态为高度结构化且消除了逻辑歧义的 Gherkin 场景以及底层的因果关系图1。这种“先生成语义特征树，再转化为严格逻辑图”的双边校验思想，是解决人类与大模型“看似达成一致，实则逻辑断裂”问题的绝佳范本。  
在更传统的安全关键领域，NASA 开源的 FRET (Formal Requirements Elicitation Tool) 提供了一个完全基于形式化验证的视角11。FRET 并非依赖大语言模型的自由追问，而是通过限制性自然语言（Restricted English）与用户进行交互，并提供自然语言、形式数学逻辑、可视化图表等多种视图以确保语义的绝对清晰11。其展开方式依赖于内置的强一致性检查机制（Consistency Checking），能够实时检测需求间的冲突，从而强制人类修正模糊描述11。当所有需求在逻辑解析引擎中不再报错，且满足系统级的完整性与一致性约束时，交互停止。最终产出为形式化数学逻辑和可视化需求树11。作为一个受 Apache 2.0 许可保护的完整产品级框架，FRET 极度严苛的语法要求可能不适合前端自由对话，但其逻辑解析引擎极其适合作为需求对齐系统后端的“硬性验证层”11。

### **工作流编排与多智能体博弈型机制**

通过将软件工程的标准化作业程序（SOP）和工作流硬编码到大模型的提示词链条中，或者引入多智能体博弈，可以强制模型按照“发现、分析、建模、验证”的阶段梯次展开对话，避免单线聊天的发散与遗忘。  
微软的实验性开源项目 PromptKit 是提示词工程化的集大成者9。它将提示词视为工程化的人工制品，通过组合、版本控制的组件库，将角色、协议、格式、分类法、模板拼装成可靠的追问与审查逻辑9。在需求展开阶段，PromptKit 包含多个交互式工作流（如规范提取工作流和工程演进工作流）。系统会通过交互式命令行，分阶段执行内置的对抗性审查（Adversarial Audits），确保输入的需求能够经受住系统性推理方法（Reasoning Protocols）的严苛考验9。其停止条件严格遵循工作流中预先定义的合同（Input/Output Contracts），只有当最终输出的产物通过了分类法检查（Taxonomy）并完全符合格式契约（Format）时，流程才会结束9。产出形态为严格遵守 YAML 或 Markdown 格式规范的结构化设计文档与需求规约9。作为一个可以通过 Node.js 直接调用的工具库，其将提示词分为五个可组合层的架构思想极其先进，可以直接抽取其核心方法论用于工作流系统。  
在多智能体框架层面，iReDev 提供了一种基于共享伪像池（Shared Artifact Pool）的知识驱动协作模式28。系统由包括面试官、最终用户、部署者、分析师等在内的六个专业化智能体组成。在展开需求时，iReDev 放弃了简单的对话接龙，转而采用“事件驱动”机制：所有中间产物（Artifacts）放在共享池中；当池中内容发生变化时，相关智能体自主触发下一步的审查或追问行动29。这种黑板模式有效解决了长对话中的信息丢失问题。其停止条件内置了鲁棒的“人在回路（Human-in-the-loop）”机制，当多个智能体在共享池中完成各自视角的建模，最终由人类利益相关者确认伪像与期望完全一致时，流程收敛29。产出形态为完善的软件需求规格说明书（SRS）以及系统需求模型29。  
REprompt 则将优化视角放到了需求工程的生命周期本身31。该框架将用户的初始输入视作“原始需求”，由 Interviewee, Interviewer, CoTer, Critic 四个智能体模拟传统需求工程的启发、分析、规约、验证四个阶段进行迭代优化31。Interviewer 与 Interviewee 进行交互式启发，获取补充信息；CoTer 将这些信息转化为严格的思维链结构；Critic 负责全面的审查验证31。当多阶段流程跑完，且 Critic 智能体验证满足各项评估维度（如一致性、通信质量等）时，循环结束31。最终产出为具有严格逻辑依赖关系的结构化任务列表，或预定义结构的系统提示词31。  
与之齐名的开源巨头项目如 MetaGPT 与 ChatDev，也提供了需求展开的基础路径。MetaGPT 将软件公司的标准化运作程序（SOP）编码进多智能体系统中12。其中的产品经理智能体会接收初始提示，然后生成产品需求文档（PRD）。为了对齐需求，它通过设定不同优先级的“需求池（Requirement Pool）”进行迭代精炼12。当各个智能体（架构师、工程师）对初始 PRD 提出疑问或反馈时，系统会触发修订与澄清流程，直到形成统一的系统设计和代码蓝图12。这类框架是完整的开源产品，具有极高的活跃度和社区生态，但其设计初衷是“全自动生成代码”，在专门针对“人类与模型之间的前置澄清对齐”这一细分领域的交互设计上，略显粗放。

### **动态评价、沙盒环境与单边工作流**

有些项目本身并非直接面向终端用户的需求收集工具，但它们为了评估大模型而建立的评价机制与基准环境，却为“如何判断追问已经足够”提供了绝佳的判定逻辑。  
ReqElicitBench (即 ReqElicitGym) 是一个用于评估模型对话式需求启发能力的交互式自动评估环境7。它利用大语言模型扮演两个关键角色：一个是带有预设隐性需求的“全知用户（Oracle User）”，另一个是负责分类和监控进程的“任务评估官（Task Evaluator）”7。在测试中，被测试的面试官模型向全知用户提问，全知用户根据代表人类真实但未说出口的想法进行回答。任务评估官会在后台逐轮追踪“互动（Interaction）”、“内容（Content）”、“风格（Style）”这三大隐性需求是否被成功激发7。其停止条件由系统中的动作分类器判定，当面试官大模型认为信息已经收集完整并输出一个特定的分类动作（如 finish），或者对话达到环境设定的最大回合数时，交互停止7。最终产出为关于需求覆盖率、最优轮次评估等量化指标的报告及多轮对话日志7。ReqElicitGym 里的后台裁判模型设计模式极其适合剥离出来用于自建系统：在真实的人机对话背后挂载一个裁判模型，实时勾勒当前已对齐的隐性需求占比。  
在工具类应用层面，Claire Vo 开发的 ChatPRD 产品以及开源项目 45ck/business-analysis-skills 采用的是单边大模型动态追问机制35。这类产品通过包含“反转交互模式（Flipped Interaction Pattern）”和动态澄清工作流的提示词，让模型在接收到模糊指令后，主动悬挂执行动作，转而向用户抛出多选或开放式的澄清问题38。当预设的 PRD 模板的各项核心指标（如目标用户、成功指标、边界情况）均达到及格的置信度，或用户手动强制结束时，追问停止，随后产出 Markdown 格式的需求文档。这类方案的本质是高度优化的 Prompt 链或应用层封装，其方法论极其轻量化，易于快速复用。

## **候选机制横向综合对比**

为提供直观的选型视图，以下针对各主要候选实现的五个核心维度进行结构化汇总分析。

| 候选项目 | 机制形状与展开动力 | 追问停止条件 | 核心产出形态 | 可改造程度 | 许可证与开源生态 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **OntoAgent** \[cite: 16\] | 基于经验本体树的启发与门控剪枝操作。 | 本体树所有高优先级槽位被填满或触发最大轮数。 | 结构化的经验本体树实例（JSON/对象）。 | 方法论与模块可高度复用，提取本体构建逻辑。 | 学术原型，活跃度取决于相关实验室16。 |
| **OntoChat** \[cite: 20\] | 对话式本体工程，参与式提示驱动用户故事构建。 | 人类在交互画布上判断能力问题（CQs）达到发散与收敛的平衡。 | 结构化能力问题集（CQs）与初始本体草案。 | 完整应用架构（Gradio），可剥离其 CQs 提取逻辑22。 | 部署于 Hugging Face，代码开源22。 |
| **RequireCEG** \[cite: 26\] | 神经符号双轨制：语义特征树分解 \+ 因果图推导。 | 逻辑形式检查与语义检查在因果图上不再发现歧义与断层1。 | 无歧义的 Gherkin 场景与底层因果逻辑图26。 | 核心算法高度可复用，极具防幻觉价值。 | 前沿学术开源（2025年），机制透明度高27。 |
| **FRET** \[cite: 11\] | 限制性自然语言解析与后台引擎推理。 | 内部一致性与完整性检查不再报出逻辑冲突11。 | 形式化数学逻辑公式与可视化树状图11。 | 适合作为下游的“硬性验证层”而非前端入口。 | Apache 2.0，NASA 官方维护，活跃度中等11。 |
| **PromptKit** \[cite: 9\] | 5层复合组件（角色、协议、格式等），对抗性审查。 | 满足预设的输入/输出合同与分类法强校验规则9。 | YAML/Markdown 格式的结构化规约文档。 | 提供 CLI 与 Node.js 库，可作为工作流后端直接调用9。 | 微软开源项目，更新频繁，集成度高9。 |
| **iReDev** \[cite: 29\] | 基于共享伪像池（黑板模式）的多智能体异步事件触发。 | 多方智能体共识达成，且人类审查确认伪像符合期望29。 | 软件需求规格说明书（SRS）与系统需求模型。 | 架构设计模式高度可鉴，解决上下文丢失问题30。 | 学术开源，处于活跃验证阶段29。 |
| **ReqElicitGym** \[cite: 7\] | “面试官-全知用户-裁判”三方沙盒环境，裁判打分驱动。 | 面试官模型输出完成动作（finish）或触发轮次阈值17。 | 需求覆盖率 JSON 报告与多轮交互日志7。 | 极具价值的“后台裁判模型（Task Evaluator）”设计样板。 | 学术评估基准，无明确限制商业使用许可39。 |

## **自建系统的理论锚点与参考方向**

鉴于当前的业务目标不仅是机械地收集信息，而是“让双方对同一需求的理解对齐，掌握远多于原始描述的信息，且指的是同一件事”，若现有开源框架在工程接入、响应延迟或逻辑刚性上无法完美适配工作流底座，完全可以考虑自建。在自建系统时，建议摒弃纯粹的“提示词工程”思路，转而向信息论、认知科学与哲学寻找底层理论锚点。

### **认知科学与语用学：沟通中的基础构建（Grounding in Communication）**

认知科学家 Herbert H. Clark 在 1991 年提出了“沟通中的基础构建”理论，这一理论是解释人类如何建立共识的基石4。在构建自建的“需求建模”阶段时，应当深刻理解共识并非通过一次性的信息广播达成，而是必须经过呈现（Presentation Phase）和接受（Acceptance Phase）的闭环。大语言模型在进行追问时，绝不能仅仅抛出疑问，而必须在获取用户回答后，用自己的逻辑体系（例如生成一段极简的系统行为流、伪代码或状态机描述）向人类复述需求。这种“回放（Play-back）”机制是验证双方是否指代同一件事的唯一途径。  
同时，需求工程中最大的陷阱在于隐性知识的沉没（Tacit Knowledge）5。人类用户在描述需求时，往往默认机器拥有与其相同的社会常识和业务背景。自建系统必须引入一个专门的“假设审查者（Assumption Checker）”智能体，其实时监控主对话流，一旦发现前台大模型在推理过程中动用了未经用户明示、且无法从上下文推导的隐性假设，就会立即强制挂断主流程，触发澄清追问。

### **信息论与系统控制论：绝对信息熵的裁剪**

在信息论的视角下，用户初始的一句话需求（如“我要一个用户协作白板”）具有极高的信息熵（Information Entropy），因为它可能映射到成千上万种系统实现路径、权限模型和数据流向2。自建系统中的追问引擎不应当是一个线性的固定问题清单，而应被设计为一个“最大化熵减（Maximum Entropy Reduction）”的控制系统。  
模型在决定下一个追问问题时，应当在后台计算：哪一个维度的问题能够最大程度地将可能的需求状态空间切分成互斥的两半。与此同时，追问的停止条件可以被严格量化：当系统后台维护的立体模型（例如包含数据流、控制流、异常分支的 Schema）的所有核心节点的信息熵均降至系统定义的绝对安全阈值以下，即系统的状态空间已经被唯一确定，没有任何模糊的游离态时，追问循环自然终止。

### **认识论与结构建模：避免幸存者偏差与神经符号双轨制**

在二战时期的统计分析中，Abraham Wald 提出了著名的“幸存者偏差（Survivor Bias）”理论，指出不能仅仅关注那些能够飞回来的轰炸机上的弹孔41。这一哲学思想在需求对齐中至关重要。人类用户给出的原始描述，往往只包含了“系统应该做什么（Happy Path）”，而忽略了极其重要的异常边界和负面约束。自建的大语言模型系统必须被赋予寻找需求“负面空间（Negative Space）”的能力，主动向用户展示边界崩溃的场景以确认约束条件。  
为了将这种发散式的讨论固化为立体需求模型，系统架构应当采取类似于 RequireCEG 的“神经符号双轨制”1。前端依赖大语言模型的“感性”去处理语言的歧义与用户的模糊表达；而在用户看不见的后端，系统必须实时维护一张严密的逻辑图谱（如因果网络或有限状态机）。这实现了一种“裁判-玩家”分离的设计：前端模型负责友好地追问，但追问何时停止，权力并不在前端模型手中。只有当后台的图谱编译器判定该需求图谱已经无死角、无悖论、完全闭环时，后台才会向前端发出结束指令。这种感性交流与刚性编译相融合的架构，是当前实现“机器与人类对同一事物产生绝对一致性建模”的最具潜力的工程解法。

#### **Works cited**

> 1. Think Like an Engineer: A Neuro-Symbolic Collaboration Agent for Generative Software Requirements Elicitation and Self-Review \- arXiv, [https://arxiv.org/html/2507.14969v1](https://arxiv.org/html/2507.14969v1)  
> 2. Surveying Root Cause Analysis Techniques: A Comprehensive Review of Aspects for Multi-Service Applications, [https://www.computer.org/csdl/journal/sc/2026/01/11245222/2bBPyOlfmxi](https://www.computer.org/csdl/journal/sc/2026/01/11245222/2bBPyOlfmxi)  
> 3. The Rise of Large Language Models: Evolution, Applications, and Future Directions, [https://www.researchgate.net/publication/395654125\_The\_Rise\_of\_Large\_Language\_Models\_Evolution\_Applications\_and\_Future\_Directions](https://www.researchgate.net/publication/395654125_The_Rise_of_Large_Language_Models_Evolution_Applications_and_Future_Directions)  
> 4. Communication Problems in Software Development — A Model and Its Industrial Application, [https://www.researchgate.net/publication/336981147\_Communication\_Problems\_in\_Software\_Development\_-\_A\_Model\_and\_Its\_Industrial\_Application](https://www.researchgate.net/publication/336981147_Communication_Problems_in_Software_Development_-_A_Model_and_Its_Industrial_Application)  
> 5. Unpacking Tacit Knowledge for Requirements Engineering | Request PDF \- ResearchGate, [https://www.researchgate.net/publication/289595857\_Unpacking\_Tacit\_Knowledge\_for\_Requirements\_Engineering](https://www.researchgate.net/publication/289595857_Unpacking_Tacit_Knowledge_for_Requirements_Engineering)  
> 6. Expanding the Design Space for AI Explanations in Human–AI Collaboration, [http://reports-archive.adm.cs.cmu.edu/anon/hcii/CMU-HCII-26-101.pdf](http://reports-archive.adm.cs.cmu.edu/anon/hcii/CMU-HCII-26-101.pdf)  
> 7. jdm4pku/ReqElicitBench: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- GitHub, [https://github.com/jdm4pku/ReqElicitBench](https://github.com/jdm4pku/ReqElicitBench)  
> 8. anmolsinghal98/Requirements-Elicitation-Follow-Up-Question-Generation \- GitHub, [https://github.com/anmolsinghal98/Requirements-Elicitation-Follow-Up-Question-Generation](https://github.com/anmolsinghal98/Requirements-Elicitation-Follow-Up-Question-Generation)  
> 9. microsoft/PromptKit: Agentic prompts are the most important code you're not engineering. PromptKit fixes that — composable, version-controlled prompt components (personas, protocols, formats, templates) that snap together into reliable, repeatable prompts for bug investigation, design docs, code review, security audits, and more. Works with any LLM. · GitHub, [https://github.com/microsoft/PromptKit](https://github.com/microsoft/PromptKit)  
> 10. RELabUU/REConSum: A tool for summarizing a requirements conversation | RE-Lab @ Utrecht University · GitHub, [https://github.com/RELabUU/REConSum](https://github.com/RELabUU/REConSum)  
> 11. NASA-SW-VnV/fret: A framework for the elicitation, specification, formalization and analysis of requirements. \- GitHub, [https://github.com/NASA-SW-VnV/fret](https://github.com/NASA-SW-VnV/fret)  
> 12. What is MetaGPT ? | IBM, [https://www.ibm.com/think/topics/metagpt](https://www.ibm.com/think/topics/metagpt)  
> 13. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework \- arXiv, [https://arxiv.org/pdf/2308.00352](https://arxiv.org/pdf/2308.00352)  
> 14. A curated collection of awesome ChatGPT & Claude agents, subagents, and AI-powered development tools \- GitHub, [https://github.com/milisp/awesome-chatgpt-claude-agents](https://github.com/milisp/awesome-chatgpt-claude-agents)  
> 15. From Chat to Interview: Agentic Requirements Elicitation with an Experience Ontology \- Semantic Scholar, [https://www.semanticscholar.org/paper/7138e9702f59226cc9a32dd763c909b7d1f7dd26](https://www.semanticscholar.org/paper/7138e9702f59226cc9a32dd763c909b7d1f7dd26)  
> 16. From Chat to Interview: Agentic Requirements Elicitation with an Experience Ontology, [https://arxiv.org/html/2605.05828v1](https://arxiv.org/html/2605.05828v1)  
> 17. ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- arXiv, [https://arxiv.org/html/2602.18306v1](https://arxiv.org/html/2602.18306v1)  
> 18. ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- arXiv, [https://arxiv.org/pdf/2602.18306](https://arxiv.org/pdf/2602.18306)  
> 19. Daily Papers \- Hugging Face, [https://huggingface.co/papers?q=OntoChat](https://huggingface.co/papers?q=OntoChat)  
> 20. \[PDF\] OntoChat: a Framework for Conversational Ontology Engineering using Language Models | Semantic Scholar, [https://www.semanticscholar.org/paper/8cfd371938caa9e74e381d381ad3ade176de5057](https://www.semanticscholar.org/paper/8cfd371938caa9e74e381d381ad3ade176de5057)  
> 21. \[2403.05921\] OntoChat: a Framework for Conversational Ontology Engineering using Language Models \- arXiv, [https://arxiv.org/abs/2403.05921](https://arxiv.org/abs/2403.05921)  
> 22. King-s-Knowledge-Graph-Lab/OntoChat: An LLM-based system for collaborative ontology engineering \- GitHub, [https://github.com/King-s-Knowledge-Graph-Lab/OntoChat](https://github.com/King-s-Knowledge-Graph-Lab/OntoChat)  
> 23. Improving Ontology Requirements Engineering with OntoChat and Participatory Prompting, [https://www.researchgate.net/publication/383494716\_Improving\_Ontology\_Requirements\_Engineering\_with\_OntoChat\_and\_Participatory\_Prompting](https://www.researchgate.net/publication/383494716_Improving_Ontology_Requirements_Engineering_with_OntoChat_and_Participatory_Prompting)  
> 24. Improving Ontology Requirements Engineering with OntoChat and Participatory Prompting, [https://ojs.aaai.org/index.php/AAAI-SS/article/download/31799/33966/35868](https://ojs.aaai.org/index.php/AAAI-SS/article/download/31799/33966/35868)  
> 25. A Survey on Interaction Design with Large Language Models for Ontology Requirements Elicitation with Competency Questions | www.semantic-web-journal.net, [https://semantic-web-journal.net/content/survey-interaction-design-large-language-models-ontology-requirements-elicitation-competency](https://semantic-web-journal.net/content/survey-interaction-design-large-language-models-ontology-requirements-elicitation-competency)  
> 26. Think Like an Engineer: A Neuro-Symbolic Collaboration Agent for Generative Software Requirements Elicitation and Self-Review | Request PDF \- ResearchGate, [https://www.researchgate.net/publication/393889895\_Think\_Like\_an\_Engineer\_A\_Neuro-Symbolic\_Collaboration\_Agent\_for\_Generative\_Software\_Requirements\_Elicitation\_and\_Self-Review](https://www.researchgate.net/publication/393889895_Think_Like_an_Engineer_A_Neuro-Symbolic_Collaboration_Agent_for_Generative_Software_Requirements_Elicitation_and_Self-Review)  
> 27. \[2507.14969\] Think Like an Engineer: A Neuro-Symbolic Collaboration Agent for Generative Software Requirements Elicitation and Self-Review \- arXiv, [https://arxiv.org/abs/2507.14969](https://arxiv.org/abs/2507.14969)  
> 28. Dongming Jin \- Homepage, [https://jdm4pku.github.io/](https://jdm4pku.github.io/)  
> 29. iReDev: A Knowledge-Driven Multi-Agent Framework for Intelligent Requirements Development \- arXiv, [https://arxiv.org/pdf/2507.13081](https://arxiv.org/pdf/2507.13081)  
> 30. \[2507.13081\] iReDev: A Knowledge-Driven Multi-Agent Framework for Intelligent Requirements Development \- arXiv, [https://arxiv.org/abs/2507.13081](https://arxiv.org/abs/2507.13081)  
> 31. REprompt: Prompt Generation for Intelligent Software Development Guided by Requirements Engineering \- arXiv, [https://arxiv.org/html/2601.16507v1](https://arxiv.org/html/2601.16507v1)  
> 32. (PDF) REprompt: Prompt Generation for Intelligent Software Development Guided by Requirements Engineering \- ResearchGate, [https://www.researchgate.net/publication/400071915\_REprompt\_Prompt\_Generation\_for\_Intelligent\_Software\_Development\_Guided\_by\_Requirements\_Engineering](https://www.researchgate.net/publication/400071915_REprompt_Prompt_Generation_for_Intelligent_Software_Development_Guided_by_Requirements_Engineering)  
> 33. \[2601.16507\] REprompt: Prompt Generation for Intelligent Software Development Guided by Requirements Engineering \- arXiv, [https://arxiv.org/abs/2601.16507](https://arxiv.org/abs/2601.16507)  
> 34. How We Built an Agent That Edits Its Own Instructions \- Vadim's blog, [https://vadim.blog/skill-evolver-research-to-practice/](https://vadim.blog/skill-evolver-research-to-practice/)  
> 35. Awesome-GPTs/support/desc/G5diVh12v.md at main ... \- GitHub, [https://github.com/polywock/Awesome-GPTs/blob/main/support/desc/G5diVh12v.md](https://github.com/polywock/Awesome-GPTs/blob/main/support/desc/G5diVh12v.md)  
> 36. 45ck/business-analysis-skills \- GitHub, [https://github.com/45ck/business-analysis-skills](https://github.com/45ck/business-analysis-skills)  
> 37. How I AI \- بودكاست \- Apple Podcasts, [https://podcasts.apple.com/sa/podcast/how-i-ai/id1809663079?l=ar](https://podcasts.apple.com/sa/podcast/how-i-ai/id1809663079?l=ar)  
> 38. Prompt Patterns Guide — Roles, Constraints & More | Pertama, [https://www.pertamapartners.com/prompt-engineering/prompt-patterns-guide](https://www.pertamapartners.com/prompt-engineering/prompt-patterns-guide)  
> 39. (PDF) ReqElicitGym: An Evaluation Environment for Interview Competence in Conversational Requirements Elicitation \- ResearchGate, [https://www.researchgate.net/publication/401058419\_ReqElicitGym\_An\_Evaluation\_Environment\_for\_Interview\_Competence\_in\_Conversational\_Requirements\_Elicitation](https://www.researchgate.net/publication/401058419_ReqElicitGym_An_Evaluation_Environment_for_Interview_Competence_in_Conversational_Requirements_Elicitation)  
> 40. Taxonomy of User Needs and Actions \- arXiv, [https://arxiv.org/pdf/2510.06124](https://arxiv.org/pdf/2510.06124)  
> 41. Cognitive Biases and the Cultural Disconnect between Engineers and Decision-makers, [https://www.researchgate.net/publication/349923052\_Cognitive\_Biases\_and\_the\_Cultural\_Disconnect\_between\_Engineers\_and\_Decision-makers](https://www.researchgate.net/publication/349923052_Cognitive_Biases_and_the_Cultural_Disconnect_between_Engineers_and_Decision-makers)