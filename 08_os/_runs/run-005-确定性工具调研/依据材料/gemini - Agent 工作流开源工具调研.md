# **确定性工具与大语言模型协作架构：十七项核心工作流节点的开源生态深度调研报告**

## **调研边界与检索域反馈摘要**

在开展针对“理解与决策交给大模型，确定性工作交给外部工具”这一人机协作架构的系统性调研时，本次研究对开源生态中的各类库、协议以及基于大型语言模型（LLM）的智能体（Agent）中间件进行了详尽的扫描。根据调研规程，首先在此明确检索域的覆盖情况、检索策略的偏差以及信息截断状态，以确保选型图景的透明度。  
本次研究广泛执行了针对特定功能模块的文献与代码库检索。例如，在探索循环报道剥离工具时，执行了诸如“github circular reporting canonical source media provenance python tool”的联合检索。检索结果暴露出明显的关键词碰撞现象：返回了名为 pycircular 的 Python 库。经过深入阅读官方仓库与文档，确认该库专用于角度、时间戳等圆周数据的统计分析，与新闻或文本的循环报道完全无关1。同时，检索也覆盖了竞争性假设分析（ACH）、捕获-再捕获模型（Capture-recapture）、RDF 形状校验（SHACL）以及突变测试（Mutation testing）等特定领域。在约束可满足性求解（CSP）、多次采样结果筛选等操作的直接检索中，系统返回为空或未命中具备显著行业地位的专用独立工具，针对这些特定盲区，本报告通过梳理底层逻辑框架进行了二次推断。所有的事实陈述均已在下文中严格区分了“通过检阅文档直接获取的信息”与“基于架构常识推断的信息”。

## **Agent 驱动范式的底层演进与接入成本模型**

在将现存的开源工具或代码库集成到大模型驱动的工作流中，其能否被 Agent 顺畅驱动是判定工具价值的最核心筛选条件。根据检阅到的开发者社区实践与官方协议文档，当前生态中存在两种截然不同的将外部工具“打包成 Agent 可安装能力”的集成范式。这两种范式直接决定了工具的接入成本、运行时稳定性以及上下文窗口的资源消耗。  
第一种范式是模型上下文协议（Model Context Protocol, MCP）服务器。MCP 是一种基于 JSON-RPC 的标准化架构，允许大模型通过宿主环境统一发现并调用外部工具、读取资源数据2。MCP 具备极高的标准化水平，支持诸如 Node.js、Python 等多种语言编写的跨网络调用服务，接入成本表现为需要额外部署独立进程并维护通信链路。然而，根据对 MCP 开发者社区的实际使用报告的阅读，MCP 存在一个致命的限制，即“工具定义上下文膨胀”。在 MCP 协议下，所有接入的工具 Schema（即输入输出参数结构的 JSON Schema 定义）必须在会话初期全量注入大模型的上下文中。相关测试测量表明，如果挂载包含数十个工具的复杂 MCP 服务器，仅工具定义就会消耗数万个 Token，且当工具数量突破二十个时，由于注意力分散，Agent 的工具选择准确率会发生断崖式下跌，导致高频的调用失败4。  
第二种范式是基于离线文件系统的渐进式技能包（Agent Skills，如 Claude Skills）。区别于 MCP 服务器的前置全量加载，技能包采用渐进式披露（Progressive Disclosure）机制。通过阅读技术综述与官方示例，这种范式将工具封装为一个包含 SKILL.md（说明文件）和执行脚本的本地文件夹。在对话初期，Agent 的上下文中仅加载一百个 Token 左右的技能名称和简要描述。只有当用户意图匹配时，Agent 才会通过 Bash 环境读取完整的执行指令与代码4。其接入成本极低，几乎不需要维护常驻服务，且因为代码执行被限制在安全的沙盒内，非常适合打包纯粹的 Python 分析脚本。  
为了弥合两种范式，当前开源社区提供了一种名为 mcp-skill-server 的中间件解决方案。该方案可以将任何传统的命令行驱动（包含 \--help 参数解析）的纯 Python 脚本，以零代码修改的成本，瞬间转化为标准的 MCP 接口暴露给 Agent7。基于这一中间件，本报告后续所提及的所有支持命令行或 Python API 的传统确定性工具，均在理论上被推断为具备低成本打包为 Agent 可用能力的可行性。

## **高难度操作专项剖析（六大核心节点）**

针对工作流设计中被认为最难找到现成方案的六项操作，本部分将进行重点深度解答，揭示现有开源方案的真实可用性与潜在的技术陷阱。

### **循环报道剥离（操作 \#4）**

此操作要求追溯一批引用文本的首发出处，并合并重复的来源。针对此需求，经过全面的检索与梳理，结论是：**确实没有现成的、能够直接通过语义计算完美剥离纯文本循环报道的单一确定性开源工具。** 现有的方案要么聚焦于底层文件的密码学溯源，要么属于高度依赖人类参与的重量级平台。  
通过阅读官方仓库，目前最接近“溯源”概念的工具是 pyc2pa，它是内容来源真实性联盟（C2PA）协议的 Python 实现8。该工具主要被程序通过命令行或 Python API 驱动。其接入成本处于中等水平，需要在宿主系统上安装 swig 和 C2PA 核心库，支持离线运行。该项目采用 GPL-3.0 许可证，活跃度呈现停滞状态，主要维护记录停留在 2021 年至 2024 年之间8。已知限制极大地削弱了其在此场景下的价值：C2PA 协议旨在通过注入数字签名来追踪图像、视频等富媒体文件的篡改历史与元数据，根本无法处理新闻报道中由于改写、洗稿或引用造成的纯文本语义级别的循环报道逻辑剥离。  
另一个被检阅的方案是 Civic Table，这是一个开源的法医级文档情报平台（Forensic Analysis Platform）9。驱动方式涵盖 Python API 与重度的系统级部署。其接入成本极高，需要完整的后端环境支撑。许可证为 AGPL-3.0。该平台通过机器学习进行实体去重，看似符合剥离需求，但根据阅读其架构设计文档中的“关键设计决策”，该系统强制规定“实体合并必须有人类审查”（Entity merges require human review），系统仅生成建议，最终必须由分析师在 YAML 文件中手动确认9。由此可以推断，在完全交给程序自动调用的纯 Agent 工作流中，这种设计理念从根本上阻断了闭环自动化的可能。

### **形态分析的交叉一致性剔除（操作 \#5）**

此操作要求在多维参数矩阵中剔除互斥组合，从而保留有效的候选集。针对此需求，结论是：**有现成的专属工具，且完全符合确定性与可编程要求。**  
该工具名称为 zwicky-morphological-analysis，由独立开发者维护10。它专门用于通用形态分析（General Morphological Analysis），核心算法正是消除矛盾组合。驱动方式为纯 Python 库调用，虽然开发者提供了一个部署于 GitHub Pages 的网页版本，但其核心 master 分支完全通过 Python 代码实现，可以毫无障碍地被 Agent 包装驱动10。接入成本极低，作为单体 Python 脚本，它不需要任何常驻服务，完全在离线内存中运算。该项目采用 GPL-3.0 许可证，但需要注意的是活跃度极低，代码库总共只有十次提交，属于研究型验证代码10。  
在已知限制或坑方面，通过阅读算法实现文档可以发现，其底层依赖的是最简单的带有提前截断机制的深度优先搜索（DFS）算法10。推断在实际工业应用中，如果给定的多维参数矩阵维度极高或内部互斥约束较少，这种纯 Python 实现的简单 DFS 将面临严重的组合爆炸问题，可能导致运行时间不可控。

### **竞争性假设分析矩阵计算（操作 \#6）**

操作要求对假设与证据矩阵进行不一致计分与诊断性排序。结论是：**有现成且现代化的方案，甚至存在专门针对大型语言模型设计的重构版本。**  
传统的 ACH 工具（如中央情报局推广的原始版本、PARC ACH 2.0、DECIDE 等）几乎全部是重型图形界面（GUI）软件，依赖分析师手工拖拽证据并点击评分，对 Agent 工作流价值极低11。然而，开源社区在 2024 年后推出了名为 EMR-ACH（Evidence Matrix Reasoning via Analysis of Competing Hypotheses）的项目13。该工具本质上是一个基于 Python 的评估框架，专门将 LLM 预测转化为结构化的矩阵分析问题。  
驱动方式为 Python API。接入成本属于中等。其核心逻辑完全基于明确的矩阵代数：程序构建一个证据矩阵 ![][image1]（记录每篇文章是否体现了某项指标）以及一个影响矩阵 ![][image2]（记录各项指标对假设的暗示强度），通过计算诊断性权重 ![][image3]，最终输出假设得分 ![][image4]，并通过 ![][image5] 选择最佳假设13。这套纯确定性的代数运算可以轻易从代码库中剥离出来封装为独立 Skill。  
如果寻求更底层的算法，在 threatintel-resources 仓库中，开发者提供了一种加权不一致性计数（Weighted Inconsistency Counting）算法的 Excel 实现14。虽然原体是 Excel，但基于其公开的数学公式，可以推断其能被极低成本地重写为数十行的 Python 脚本用于 Agent 驱动。传统 ACH 算法存在一个已知的思维陷阱，即假设证据与主张属于一维的直接对立关系，这容易导致矩阵稀疏或扁平化；而 EMR-ACH 通过引入中间层（Indicators）缓解了这一问题12。

### **变异测试（操作 \#11）**

要求结合代码与测试用例，输出测试套件的缺陷捕获率。结论是：**存在成熟的开源生态，但隐藏着致命的框架兼容性陷阱。**  
当前 Python 生态下最具代表性的工具是 mutmut15。驱动方式为命令行调用，完全能够作为子进程被 Agent 触发。接入成本处于中等水平，需要与项目已有的测试框架（如 pytest）深度绑定。该工具不需要常驻服务，完全本地离线运行。许可证为 BSD-3-Clause，截至 2024 至 2025 年间依然保持活跃更新与社区讨论16。  
然而，针对此工具的实际使用报告检索，挖掘出了必须警惕的失败案例。首先是语言级别的兼容性断裂：在 Python 3.14 的前瞻测试中，mutmut 依赖的 Pony ORM 组件因为无法正确进行对象序列化（pickle error，具体报错涉及 itertools.count 对象）而导致测试流程彻底崩溃18。更为严重的是其对现代框架架构的破坏：通过阅读 2025 年 5 月的 issue 报告，mutmut 的抽象语法树（AST）变异引擎会强制忽略所有附带装饰器（Decorator）的函数与类。原因是变异测试会在内存中创建副本，处理类似 FastAPI 的 @app.post 路由装饰器会引发重复挂载的致命副作用16。推断在重度依赖类型约束（如 @typechecked）或路由注解的现代 Python 工程中，Agent 调用 mutmut 可能会得出“覆盖率为零”或极度失真的捕获率报告。

### **原子级事实支撑度度量（操作 \#13）**

要求度量一段主张中各项原子事实在知识源中的被支持比例。结论是：**有现成组件，但普遍存在性能瓶颈与混合计算特性。**  
在针对该项需求的检阅中，命中了两个高度相关的开源库：FActScore 与 AlignScore。FActScore 是一个旨在提供细粒度原子级事实精准度评估的 Python 包19。它的驱动方式包括命令行和 Python API 调用。接入成本较高，系统默认依赖大规模的离线维基百科数据转储（如 2023 年版本），且要求配置外部大模型 API 密钥。其底层逻辑并非纯粹的确定性计算，而是通过 Prompt 指令引导语言模型将长文本拆解为原子事实，再比对知识源进行支撑度校验19。这种混合范式违背了将确定性计算完全剥离的原则。  
另一个更偏向确定性运算的方案是 AlignScore21。驱动方式为 Python API 调用。接入成本属于中高水平，需要安装 spaCy 进行分句处理，并强依赖 PyTorch 1.12.1 框架和 GPU 加速环境。运行前需要下载数百万参数级别的 RoBERTa 模型权重。其机制通过统一的信息对齐函数，计算每一句主张在上下文语块中的最大对齐分数，最终取平均值得到整体支持比例21。  
已知限制与坑点在于计算效率与数据鲁棒性。AlignScore 在处理大批量长文本时显存消耗巨大。此外，通过阅读 2024 年发布的 LIM-RA 研究文献可以发现，AlignScore 官方宣称的 470 万庞大训练数据集内含大量噪声。研究指出，如果对原始数据进行清洗并仅使用其中 10% 的鲁棒性增强子集重新训练模型，其评估准确度反而能大幅超越使用全量数据的原始基线23。这为后续将其作为 Agent 内部裁判工具时的模型微调提供了关键的排雷信息。

### **Prompt 或 Skill 的行为评测（操作 \#16）**

要求根据用例测试输入是否达到期望行为。结论是：**有现成、工业级且与 MCP 协议原生融合的顶级开源框架。**  
目前生态中最具统治力的工具是 promptfoo24。它的驱动方式极其丰富，不仅提供 Node.js 的包集成、命令行界面（CLI），最关键的是它本身就内置并提供了一个开箱即用的 MCP Server。用户可以直接通过执行 npx promptfoo@latest mcp \--transport stdio 命令，将测试套件以标准协议暴露给任何基于 MCP 架构的 Agent（如 Claude Desktop 或 Cursor）25。  
接入成本极低，配置依赖于简明的 YAML 或 JSON 文件，支持完全脱机在本地对模型或脚本进行行为断言24。该项目采用 MIT 许可证，在开源社区拥有极高活跃度，频繁发布更新。其能力矩阵不仅涵盖传统的数据断言验证，还集成了针对大语言模型应用专属的渗透与安全测试插件体系，能够有效检测 Prompt 注入、敏感数据泄漏以及工具越权调用（BOLA/BFLA）等漏洞26。  
在已知限制方面，由于 promptfoo 深度构建于 Node.js 生态系统中，当将其用于评测高度复杂的纯 Python 环境下的 Skill，或面对需要严格隔离的系统级执行脚本时，跨进程的 stdout 与 stderr 捕获机制偶尔会出现信息截断。此时需要通过严格设定评估器中自定义执行脚本的接口规范来规避此类断言失败。

## **常规确定性操作的生态图景（十一项常规节点）**

针对剩余的十一项确定性要求操作，部分在开源生态中拥有成熟的单体工具，部分则可以通过组合常规数学与算法库进行极低成本的实现。

### **结构化对象的 Schema 校验与缺失字段判定（操作 \#1）**

针对将对象输入并输出违反约束条件的工具，开源生态中存在极度成熟的方案。目前由 python-jsonschema 组织维护的 check-jsonschema 是该领域的标杆，专门用于依据特定方言版本的 JSON Schema 校验目标文件，提供 Python API 与命令行预提交钩子，无需常驻服务，完全支持离线操作27。然而，在 Agent 调用的上下文中，官方 MCP 规范已明确指定 JSON Schema 2020-12 版本作为默认方言基准28。在跨环境的交互报告中暴露出一个严重的架构兼容陷阱：当数据结构中大量使用诸如 anyOf （类似于 Python 类型系统中的 Union\[str, dict\]）等复杂分支时，某些主流代码编辑器内置的 MCP 客户端验证引擎存在设计缺陷，会直接将合法输入拦截，导致调用请求根本无法下发至服务端进行计算处理29。推断在设计该环节的接口参数时，必须避免过度深化的树状逻辑，转而采用宽泛的参数约束类型（如 Any），将细粒度的值校验下沉到 Python 内部业务逻辑层。

### **把校验错误转成排序后的追问（操作 \#2）**

本操作本质上是将底层编译或校验报错转化为面向用户的人类可读追问。对该任务进行针对性检索后，**返回结果为空**。事实上，开源界并不存在一个通用的独立工具能够开箱即用地完成这种特定语境的语义映射。基于技术原理推断，此操作完全可以通过简单的 Python 脚本可编程化：程序捕获前置步骤抛出的 jsonschema.exceptions.ValidationError，解析错误对象中的 JSON Path 层级以及缺失的属性键名，再依据预先设定在 YAML 配置表中的“字段业务影响度权重”对错误进行排序，最终将格式化后的提示语通过字符串模板输出给大模型，由其润色为自然追问。

### **两份清单的重合度与总体规模估计（操作 \#3）**

评估两个独立清单的重合元素数量并利用捕获-再捕获理论推算未观测总量的需求，在统计生态中被称为 Lincoln-Petersen 估计。检索命中了可用的开源包 recapturedocs，该库由 Python 编写，采用 MIT 许可证，提供简单直接的 API 调用，接入成本极低，且完全本地无状态运行30。另一替代路径是使用诸如 PyMC3 等贝叶斯概率编程框架编写短小精悍的模型代码31。根据数理统计文献的分析，已知必须规避的严重计算陷阱是原始 Lincoln-Petersen 公式 ![][image6] 面对小样本，特别是当二次采样中的重合数量 ![][image7] 接近或等于零时，会产生无穷大的偏倚估值。工程应用中必须采用或确认底层包内置了 Chapman 偏差修正算式 ![][image8]32。

### **敏感性分析（操作 \#7）**

探究最终结论对单一证据条目的依赖程度，属于决策分析中的传统环节。直接检索未发现专门针对特定矩阵的单体敏感性分析应用。推断这一操作不需要引入诸如 SALib 等重量级物理与金融敏感度分析框架。在前文提及的 EMR-ACH 框架基础上13，可以利用程序编程计算，通过系统性地将证据矩阵中的单一证据向量强制置零，观察结果得分及名次的偏离程度，从而在数十行 Python 矩阵操作代码内输出高度确定性的依赖度量，供 Agent 作为反思素材使用。

### **论证结构中的孤立主张检测（操作 \#8）**

在论证关系建模中找出缺乏事实挂靠的节点，属于计算论证（Computational Argumentation）的范畴。开源仓库 PyArg 专门负责这一逻辑处理35。该工具纯粹由 Python 构建，提供程序调用的底层 API，接入成本低，无需联网或常驻进程。它能够将提取到的主张与证据转换为有向图结构，通过图遍历算法确定入度为零的“孤立”逻辑节点。

### **RDF 图的形状约束校验（操作 \#9）**

涉及语义网技术中利用 SHACL 规范查找违规图节点。目前最具代表性的是 pySHACL 库36。它的驱动方式包括命令行执行以及丰富的 Python API 接口。由于其重度依赖于底层的 RDFLib 解析引擎，接入成本处于中等范畴。该库目前积极维护，完全兼容核心约束组件。通过阅读功能支持列表，已知存在部分功能缺失或测试盲区：例如当解析不合规的特殊数据类型文字（ill-formed Literals）时会受限于底层库而引发异常；此外，对于特定节点表达式（如 filterShape 等）的支持缺乏完备的测试用例验证36。

### **测试溯源校验（操作 \#10）**

将代码测试集映射回被测对象及原始规范条目的需求，可通过需求可追溯性分析套件实现。检索发现了 OpenFastTrace (OFT) 项目，其可以通过终端命令行直接执行，甚至提供了官方的 GitHub Action 组件以便集成于 CI 环境37。原版 OFT 依赖 Java 17 以上的运行时环境，导致在特定容器中接入成本偏重。为此，社区提供了一个名为 cargo-ovft 的 Rust 重写版本40。该版本生成零虚拟机依赖的单体静态二进制可执行文件，极度契合 Agent 在临时沙盒环境中的快速拉起需求。它的运行机制完全基于纯文本的解析比对：扫描 Markdown 文档中定义的需求 ID，匹配源代码与测试注解中预留的追踪标签，输出未覆盖元素的明细报告38。

### **约束可满足性求解（操作 \#12）**

针对分析给定约束集是否存在可行解并标识矛盾核心的操作，本次特定针对本领域的文献检索呈现未直接命中现象。但推断在实际工业和学术界，此类问题早已有统治级的工具——微软开源的 Z3 定理证明器（Z3-solver）。该工具提供极其完善的 Python 编程接口，能够高效执行复杂的命题逻辑推导。如果将 Z3 包装为 Agent 的 Skill 供其调用，它的核心优势在于当约束无法满足时，能够提取不可满足核心（Unsatisfiable Core），从而直接向大语言模型输出“矛盾的逻辑起源点”，为后续模型的修正决策提供结构化的因果反馈。

### **覆盖关系检查（操作 \#14）与 多次采样结果的筛选（操作 \#15）**

这两项操作属于通用的逻辑比对与条件过滤。针对覆盖关系检查，其在离散数学上即为双向映射的完整性比对，无须任何专门的沉重框架，推断利用 Python 内置的数据结构（如 Set 集合的交、并、差集运算）便可提供绝对准确的映射空缺判定。如果其上下文涉及文件或代码制品的覆盖，上述的 OpenFastTrace 同样能够兼顾解决37。针对采样结果筛选判定，这完全涵盖在前述第 16 项评测框架 promptfoo 的能力范围之内。promptfoo 支持通过配置脚本预埋 Python 或 JavaScript 断言规则，对输入输出记录进行大规模并发校验过滤26，无需再寻他法。

### **测试运行与可重复性核验（操作 \#17）**

这一操作本质上是测试执行器的工作。在 Python 生态中即为 pytest。但在架构层面上，直接将 pytest 的原生控制台输出强塞给大模型的上下文是极不明智的，因为冗长的 Traceback 日志会迅速耗尽 Token 限额并干扰模型注意力。基于可编程特性推断，最佳接入路径是使用包装脚本调用 pytest \--json-report，仅将包含测试用例通过状态与错误断言的关键节点数据，压缩萃取为轻量级的 JSON 结构体，通过 API 或技能接口精准投递给大模型。

## **综合架构集成结论与选型指南**

本研究调查的十七项确定性操作中，绝大部分在开源生态中都拥有能够通过代码驱动的现成工具，即便功能细微，也能通过标准化的数据处理库进行定制化组装。在“理解与决策交由大模型，确定性计算剥离外部”的顶层设计下，最终工作流的稳定性很大程度上受制于**集成模式的粒度划分**。  
当前大模型集成外部工具极易陷入 MCP 协议的盲目崇拜中。如果将上述十七项操作全部构建为独立的 MCP Server 挂载到一个统一入口的大语言模型实例上，根据目前已知的主流 MCP 客户端机制，多达数百个复杂数据结构的输入输出 JSON Schema 将在初次通信时直接淹没模型的上下文，导致可用性全面瘫痪4。  
更为工程化的整合建议是将工具进行层级解耦：对于诸如形态分析、孤立主张检测、约束求解等依赖纯离线数学或逻辑推演，且无须建立长连接的操作，优先将其包装为基于本地运行环境的 Agent Skills（技能包）。通过局部脚本文件加 SKILL.md 指令说明，利用大模型的渐进式加载特性，避免全局上下文膨胀4。而对于诸如 Promptfoo 评测框架、需要庞大运行环境的 OpenFastTrace 或加载大参数对齐模型的 AlignScore 等重量级操作，采用 MCP 服务器形态以跨网络进程隔离运行，方能最大化发挥各自生态的确定性优势。

| 操作编号 | 操作功能摘要 | 是否有成熟现成工具 | 推荐组件 / 开源方案代表 | 驱动与接入形式 | 接入依赖与成本评估 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **1** | 结构化对象 Schema 校验 | 有 | check-jsonschema | Python API / CLI | 极低，无需常驻服务 |
| **2** | 校验错误转排序追问 | 无专用工具 | 需定制 Python 包装脚本 | Python 内部脚本 | 极低，逻辑简单 |
| **3** | 清单重合度与规模估计 | 有 | recapturedocs | Python 库调用 | 极低，纯数学模型 |
| **4** | **循环报道纯文本剥离** | **无直接工具** | 无直接工具 (部分借用 Civic Table) | N/A | 极高，需人类节点干预 |
| **5** | **形态分析的一致性剔除** | 有 | zwicky-morphological-analysis | Python 函数调用 | 极低，警惕组合爆炸 |
| **6** | **竞争性假设矩阵计算** | 有 | EMR-ACH | Python API | 中等，矩阵代数运算 |
| **7** | 敏感性分析 (依赖度) | 依赖前项 | 可复用 EMR-ACH 变异逻辑 | Python API | 低，基于原数据操控 |
| **8** | 论证中"孤立主张"检测 | 有 | PyArg | Python 图运算 | 低，无需常驻服务 |
| **9** | RDF 图形状约束校验 | 有 | pySHACL | Python API / CLI | 中，依赖底库生态 |
| **10** | 测试溯源及覆盖映射校验 | 有 | OpenFastTrace / cargo-ovft | 命令行可执行文件 | 低，尤其 Rust 版本 |
| **11** | **代码测试的变异缺陷捕获** | 有 | mutmut | CLI 调用的守护脚本 | 中，警惕框架兼容性问题 |
| **12** | 约束可满足性核心求解 | 有 | (推断) Z3-solver | Python API 包装 | 低，本地离线求解 |
| **13** | **主张之原子级事实支撑度** | 有 | AlignScore / FActScore | Python 模型推理 | 高，需显存与数据环境 |
| **14** | 简单关系与集合覆盖检查 | 依赖基础库 | (推断) Python 原生 Set 库 | 脚本内建逻辑 | 极低，不建议外部化 |
| **15** | 多次采样输出的条件筛选 | 有 | 集成于 promptfoo | 引擎内部断言 | 低，可共享评测基建 |
| **16** | **Prompt / Skill 行为评测** | 有 | promptfoo | **原生提供 MCP Server** | 极低，全量标准化接入 |
| **17** | 测试执行与重复性记录核验 | 有 | (推断) pytest \--json-report | 脚本提取后返回 | 低，屏蔽复杂日志干扰 |

#### **Works cited**

> 1. pycircular is a Python module for circular data analysis \- GitHub, [https://github.com/albahnsen/pycircular](https://github.com/albahnsen/pycircular)  
> 2. Overview \- Model Context Protocol, [https://modelcontextprotocol.io/specification/2025-11-25/basic](https://modelcontextprotocol.io/specification/2025-11-25/basic)  
> 3. Implementing an MCP Server in Python for ChatGPT Developer Mode \- Medium, [https://medium.com/@danushidk507/implementing-an-mcp-server-in-python-for-chatgpt-developer-mode-4fbe4265c7b5](https://medium.com/@danushidk507/implementing-an-mcp-server-in-python-for-chatgpt-developer-mode-4fbe4265c7b5)  
> 4. Claude Skills vs MCP vs Projects: Which One Should You Use? \- Rabinarayan Patra, [https://www.rabinarayanpatra.com/blogs/claude-skills-vs-mcp-vs-projects](https://www.rabinarayanpatra.com/blogs/claude-skills-vs-mcp-vs-projects)  
> 5. Claude skill for Serena, token-efficient MCP tool handling · Issue \#802 \- GitHub, [https://github.com/oraios/serena/issues/802](https://github.com/oraios/serena/issues/802)  
> 6. Langfuse for Coding Agents (Claude Code, Codex, Cursor), [https://langfuse.com/agents/agents](https://langfuse.com/agents/agents)  
> 7. GitHub \- jcc-ne/mcp-skill-server: Claude-code like skills packages as a server, [https://github.com/jcc-ne/mcp-skill-server](https://github.com/jcc-ne/mcp-skill-server)  
> 8. numbersprotocol/pyc2pa: Python implementation of C2PA: Coalition for Content Provenance and Authenticity. \- GitHub, [https://github.com/numbersprotocol/pyc2pa](https://github.com/numbersprotocol/pyc2pa)  
> 9. juanceresa/forensic\_analysis\_platform: Forensic document intelligence platform for provenance-first case reconstruction: OCR, entity/relation extraction, knowledge graphing, analyst verification workflows, and evidence-linked narrative generation. · GitHub, [https://github.com/juanceresa/forensic\_analysis\_platform](https://github.com/juanceresa/forensic_analysis_platform)  
> 10. Zwickys Morphological Analysis implemented in Python \- GitHub, [https://github.com/JohannesBuchner/zwicky-morphological-analysis](https://github.com/JohannesBuchner/zwicky-morphological-analysis)  
> 11. Burton/Analysis-of-Competing-Hypotheses: An analytic technique created at the CIA, ACH helps you analyze complex situations with multiple hypotheses and countless pieces of evidence. Multiple people can collaborate on a single problem, and ACH will compare everyone's analyses and pinpoint the precise areas of disagreement, allowing for a more focused debate. · GitHub, [https://github.com/Burton/Analysis-of-Competing-Hypotheses](https://github.com/Burton/Analysis-of-Competing-Hypotheses)  
> 12. Analysis of competing hypotheses \- Wikipedia, [https://en.wikipedia.org/wiki/Analysis\_of\_competing\_hypotheses](https://en.wikipedia.org/wiki/Analysis_of_competing_hypotheses)  
> 13. ApartsinProjects/EMR-ACH: Evidence Matrix Reasoning via Analysis of Competing Hypotheses \- GitHub, [https://github.com/ApartsinProjects/EMR-ACH](https://github.com/ApartsinProjects/EMR-ACH)  
> 14. pstirparo/threatintel-resources: Resources, tools and utilities about Threat Intelligence, [https://github.com/pstirparo/threatintel-resources](https://github.com/pstirparo/threatintel-resources)  
> 15. boxed/mutmut: Mutation testing system \- GitHub, [https://github.com/boxed/mutmut](https://github.com/boxed/mutmut)  
> 16. mutmut 3.3.0 does not mutate decorated functions/methods \#387 \- GitHub, [https://github.com/boxed/mutmut/issues/387](https://github.com/boxed/mutmut/issues/387)  
> 17. pyproject.toml \- boxed/mutmut \- GitHub, [https://github.com/boxed/mutmut/blob/main/pyproject.toml](https://github.com/boxed/mutmut/blob/main/pyproject.toml)  
> 18. Mutmut incompatible with Python 3.14 \- blocks mutation testing · Issue \#121 · Geoffe-Ga/start\_green\_stay\_green \- GitHub, [https://github.com/Geoffe-Ga/start\_green\_stay\_green/issues/121](https://github.com/Geoffe-Ga/start_green_stay_green/issues/121)  
> 19. A package to evaluate factuality of long-form generation. Original implementation of our EMNLP 2023 paper "FActScore \- GitHub, [https://github.com/shmsw25/factscore](https://github.com/shmsw25/factscore)  
> 20. \[2305.14251\] FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation \- arXiv, [https://arxiv.org/abs/2305.14251](https://arxiv.org/abs/2305.14251)  
> 21. yuh-zha/AlignScore: ACL2023 \- AlignScore, a metric for factual consistency evaluation. · GitHub, [https://github.com/yuh-zha/alignscore](https://github.com/yuh-zha/alignscore)  
> 22. AlignScore: Evaluating Factual Consistency with A Unified Alignment Function, [https://www.semanticscholar.org/paper/AlignScore%3A-Evaluating-Factual-Consistency-with-A-Zha-Yang/27cb586fcea5ec076b984750e9c77f0d7fc976e5](https://www.semanticscholar.org/paper/AlignScore%3A-Evaluating-Factual-Consistency-with-A-Zha-Yang/27cb586fcea5ec076b984750e9c77f0d7fc976e5)  
> 23. Less is More for Improving Automatic Evaluation of Factual Consistency \- arXiv, [https://arxiv.org/html/2404.06579v1](https://arxiv.org/html/2404.06579v1)  
> 24. promptfoo \- GitHub, [https://github.com/promptfoo](https://github.com/promptfoo)  
> 25. Promptfoo MCP Server, [https://www.promptfoo.dev/docs/integrations/mcp-server/](https://www.promptfoo.dev/docs/integrations/mcp-server/)  
> 26. MCP Plugin \- Promptfoo, [https://www.promptfoo.dev/docs/red-team/plugins/mcp/](https://www.promptfoo.dev/docs/red-team/plugins/mcp/)  
> 27. How we validate our MCP JSON Schemas with check-jsonschema \-, [https://apiquality.io/validate-json-schema-mcps-check-jsonschema/](https://apiquality.io/validate-json-schema-mcps-check-jsonschema/)  
> 28. SEP-1613: Establish JSON Schema 2020-12 as Default Dialect for MCP \- GitHub, [https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1613](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1613)  
> 29. MCP tool input validation rejects anyOf schemas \- blocks Union-typed parameters · Issue \#321662 · microsoft/vscode \- GitHub, [https://github.com/microsoft/vscode/issues/321662](https://github.com/microsoft/vscode/issues/321662)  
> 30. recapturedocs \- PyPI, [https://pypi.org/project/recapturedocs/](https://pypi.org/project/recapturedocs/)  
> 31. Capture-Recapture Models in Python with PyMC3 \- Austin Rochford, [https://austinrochford.com/posts/2018-01-31-capture-recapture.html](https://austinrochford.com/posts/2018-01-31-capture-recapture.html)  
> 32. Capture-Recapture Estimation Calculator | MetricGate, [https://metricgate.com/docs/capture-recapture/](https://metricgate.com/docs/capture-recapture/)  
> 33. Lab 7: Parameter estimation: mark-recapture analysis\!, [https://kevintshoemaker.github.io/NRES-470/LAB7.html](https://kevintshoemaker.github.io/NRES-470/LAB7.html)  
> 34. Python Script to simulate Population Estimation using Capture Recapture Method · GitHub, [https://gist.github.com/paucoma/36343a189ffd62aefa7ee87d71b18fcf](https://gist.github.com/paucoma/36343a189ffd62aefa7ee87d71b18fcf)  
> 35. DaphneOdekerken/PyArg \- GitHub, [https://github.com/DaphneOdekerken/PyArg](https://github.com/DaphneOdekerken/PyArg)  
> 36. pySHACL/FEATURES.md at master \- GitHub, [https://github.com/RDFLib/pySHACL/blob/master/FEATURES.md](https://github.com/RDFLib/pySHACL/blob/master/FEATURES.md)  
> 37. GitHub \- itsallcode/openfasttrace: Open source requirement tracing suite, [https://github.com/itsallcode/openfasttrace](https://github.com/itsallcode/openfasttrace)  
> 38. openfasttrace/doc/user\_guide.md at main \- GitHub, [https://github.com/itsallcode/openfasttrace/blob/main/doc/user\_guide.md](https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md)  
> 39. GitHub Action for tracing requirements using OpenFastTrace, [https://github.com/itsallcode/openfasttrace-github-action](https://github.com/itsallcode/openfasttrace-github-action)  
> 40. jFiedler24/open-very-fast-trace · GitHub, [https://github.com/jFiedler24/open-very-fast-trace](https://github.com/jFiedler24/open-very-fast-trace)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAAAvElEQVR4XmNgGAX4wGsgNkUXJAaoAvF/IPZHlyAE7IH4IwNEcwWaHEGwD4iPMUA016DJ4QVyQBwBxFIMEM1LUaVxA0YgngjEnEAswQDRDHIFQQDSsIkBohkEeBkgmu/AVeABIUB8kQHibBgAaX6ExMcKQM49AcTqDBC/wjBI82ckdViBDgNEIS6ME7AC8QIojQ4IagbFZwm6IBS8ZcCjmRmILzNAogUbwKpZHCqIy18b0ORAmGDAjYJRAAYAtzYv5e8G++cAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAaCAYAAABhJqYYAAAAn0lEQVR4XmNgGPpAEIqRATMQc6GJgYEIEEsBcQIQ/wfiDiifA0kNBqgB4ndAbI4ugQ5kgPg2EC8FYkY0OQxgB8SfgTgTXQIdsALxGgaIe0XR5DAASMFFBohikEa8AGQ1SCHIGQQByFMgxSAPEgRvGSCKQUFHEIAU/gBiN3QJdACKZpDi3UDMjSYHB6C4B8VULQNE8QEgdmcgEMWjYJAAAKeuGQgGI2P3AAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAbCAYAAABxwd+fAAABNklEQVR4Xu2Uv0sDQRCFn0jAgHaKJigIwUas1cpGsBGxsbDxb7Cwk/TWkkpSpwukEbQSWzutbMRCRFJrYyHoe8wm7o0/LnvpxA8+jrw5Njs3ewf8MwwjtEpX6KqrJbFI34MHrpbMJn2js76QyhFsR2O+kMoDffXhoMzQZVqCtXWfLeezRS9phZZpG9ZWPbonF424S5eibAPWlq4DoxZeXKYHfYrvH7SOg3abQTcqvHGZFvmprSm67kOdXi3UirIabGJJbfUW2o6y+PxoUSnmaYde0eOQ9ZnA14XuQib2YEdBnNAFWNsXIcuwT5/pI72F/fM1bJLNz9v6aDA7PuyhNqbpaPitXUzCvgKeJ9hLPRSaWMOHRVjDL23lMU4PYa/OWbgWQhPVFHdh56sw+rCdwyY452p/nQ/uqzVEQ8wR4AAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAZCAYAAABjNDOYAAAC2klEQVR4Xu2X3atNURTFp6QIRTwI5VI+I5GPUtySSBLl84VXf4AXeZe6vEi8qZsXeZWUlJQijyKl0M1XSpKkFMX4NddknXXuvmefuqWuNWrUPnPNvddYY8019z5mFRUVFRUVFRUTH/PEc+JFcU4xNkmcKy4XB8VZ4i5xcp4kTBFXi5vFqeJK82duzZMSyJ1vnguYY4G4XZwZScIm8bB5/mg4YD7HEevWPS74KP4yFwjuFL8RizHEPovLxCviJ3Fjyjlufh/GsZBh8bS56ZdSLBBmPzd/5kNxbRrD/C/iGfFWipFP3oP0G6wz1z2cxpmX+S+k3wDdR8UP4j1xkbl25r0t7rbuDe7CG+s0Y6f4XVz1J8NBDgR7zcUjCgOeiAfTGNgjvhKXZLESV82fx3yB2eIj8wUszuJsBAxQlejG+Fz3e+vWfcjcIKoUrY/t7z2tgdNrxPPm5kRVBFgICy4Ru7gviyHkq7gti5UIc/JjxPVd8VQWA6U5ObiHo4fuvJpzxGlgEwc6h8YGpUX5/TTfjWvmCysn4eEvihiYJt6wzgUdMz8GVFYTwpzpWawfc9D91Fz3dXPdTeawWVTPiXKgFzgeiFxvXm48nEnKXW8yB9AzRsyPE0I4FtFsmxDm5BjLHDYsgOnophLQDdDdVK0D4jPxnflLoxU4gwg8m8XCHI4JjLJvMoc3080y2AL9mpPnRjPPgW5iaOYZoZsNp88sNDeInFY9ZzRzePNQqv2as7Qc6IF+e04vc9A9mjk05MF0TdP+lmKtMGR+w4j4VlxhfiSY6L65UK5zsrAcO7KxnJhcfqOEAXkepm8oYpCFljH00OfQ/cNcN/0N3fQVcqiSMB+GWXksntUT7D5nle+PANdtym+/ubnlRxjNjx3fUsTHE3x/oTt0so58Df8cvCZfl8EE3lony+D/hOhRM4o4bzB6Q7+9aEKC/1uXxZfm1cSXas/P84qKiooKs98PAcHQi455KQAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFIAAAAaCAYAAAAkJwuaAAACwUlEQVR4Xu2ZTagOYRTHjyQkn1lIFr4XSlYoCwtKyUaShbK0sPbZjY18lK2lbikL+SgbEiJ2lAVRIiwoKSwkZaE4v3tmmvOeO5qZO2/vO7nPr/7dOc/z3rnPnPuc85wzr0g9pqiWxcFEM6aqfqjuqw6JOTXREJw4otqW2V8zu6usVO1Szcvs5arpxfRwmVZhd4EXqqfOZo1XVMfdWBlskDeq3WGcqDus+qBaEeb+Wzao7kmxC3NwUh5J/+KY6mz207NRdULsvrPCXC34w79UfzLdVs1089yUm+fz6IubHzSnxdZQxnrVjDgYuKRaIuMdtll1QLXDjTWCkFikuia2wO+qTT2fEJmvuqP6rVqrWtg7PVDei4VfGXVS0DkxZz8Rey5YJXY2XJQ+hPVz1VYxZ7LYyHWxkBg2rK/OOgj/12EMR6/Jrr+J7WB2IIcV14y15oFqthThG3kmLbZ9H2FtMb/BYtUZZx8U+6wPdUJ6TnZNdPE8J8UcTFgz1gq2+M7selRsAduL6TFuSnX+GQQfxfJ45IKMP3wi/h9Anr/rbCKSvNkKtnueG8iP5MnLUuQcSoM64TQIjoo1C75JWKda6uwyFqhuOfut6qGzuWfrZzwf7L1iu5JtD5QGdZPwXNUN1bsGOjX2m83Yotojlo46AWH9OIxxiuNIil4gf3QhrDvNPrGDJvJZzJmrpbeDGCa+lh2UasPhEkMbyJHciLrrZZhLlPBKitrKQ+5hp+LMqv7VwyFAwU45UledyXNteCRFbRXh0KF9rOpfJy20QzEXUPaU0ZX6caJQ1tBHA8/9U6yESjSASKNNpArJoX6MrWOiAro1SjcPbSBv/RMNoBrJw5oubb/qSHadqAmVyCcpnDYilh8TDSGs/ducvr0mm2xQ1vlDhTBv1KkkDFpcXkbnXJXCkXw3k2gBZRDNhf9OasL8BVA7ouq4ugqOAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAAA/ElEQVR4XmNgGAXogBWIJYBYCg0TDXgZIBruA/F/IFaB8kHYGoh/A/FXIGaEacAF3jFADEAHXQwQcXt0CWQAMh2k6B66BBAUM0DkFqFLIANBBoiiLegSQLCGASKXiS6BDGKB+AcQu6GJCzBANF9AE8cAcxkgzpdhQMRKDhDfYYCEAQ9CKSYwBOLXQFyDJMbMAAn5T0hiOAHI+SBnojt/AVRcGE0cA5xkgCjkQBOHBZ4WmjgGeMuAPf5vMkDE8aZKfPEPEgdhUEoFAZBLdWCSII26QJwFVXQFiBUYEIpB4CNUDpRGQGAjEHMipAkDkCUaQDwbiOvR5EbBKGAAAEgjMWflnDyoAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAK0AAAAdCAYAAADYZew2AAAE5klEQVR4Xu2c3csVVRSHl4ihiF9oKFGihiCCFxJpeFFQUImCFiIS9AcogheCetGVGIl6E0oQUfSBaKUIIYiIQgSiYKAkiVAiKt6UgoYgGOh63n22Z7/r3XNmPGfOmXHOfuCHzJo5h31mfrP22mvmVaRZTLeBATNFNdEGDXn7y6bImBrJBNVcG6wRjO8LG1T+VT1WHZf4hftf3P7vJL4/j9dU75nYWxK/eV5WnbZBZZJqm+qCaq/qrGqz6qj0f0yN5mvVHRusEe+qztiguIv+o+pX1VSzb6HqP9VnJl6EN1TbVY9UO8y+cZEYfK7aaYPKH+IM6+EGZMyfBLEidDOmRkIWwLCLxf1wjLth1BH14Iq4MVreVO0RN+7Xg/gq1TrVDdWrQdxywAYMfG/MDOdVH5uYzfazVRdV84OYh7GSmWOUOaZGslpclvKsVf0WbNeFWCYFLh7mpAzAqB4yHqY4pZocxC3dGoQb/aC4Gx0wq82cn4orTWJg2qzSoNcxJWoAC42sKf4HcWb+R9qmWd76d6OMNnKMbg2yRvWX6qXWNiYk64dwI5F9n5Vex5SoAZg2dpGA0gC4WN+LO5YsSwb8VsaWBrPEGc3rG7Nts18ng4SlB6YNyxMgy2bdbCFlj6lxsKB5KO6EohPi6loPUylTqt+PyGJVkmVaFjS+zj2iuiQu22JYsu3d1r5O9JrVwkwbM23ss9SdzAJZ9DqmOhBem57hy+aofhZ3Uu+pVow6QmSG6qS46W2JuExQJYyZes1CzcpYgf23WjHAFIw/j24NgvGuijuXQMa1pchNcUnB8pV0bk/1Oqaq+UBct4SbqFTISu+IM+41sw/IXEWmtkHBKvzFYPu+tGcBfgcn6CdxM8Xh1j7EVPtC6zMxsgyySXVd2t/DQpBugIfzExqH7L4/2Ibxqi3iLiCtKmYw2mJ5lDWmQfO26kNxsxw3VummpefJtOtPgAWT2MxRJZdl7EKnDLIMkge9VztDnZN25g/hYq4Xd76LUOaYqoAyqXTTcmJpbQHTKqZd2d49AqteuwCoEqb92NOmKpgp7Q5FCOeUsqsKssZUBX0xLQWyX/VyZ1LXHhJXOwJTXdHSgGPt6jdPRTOOhYvSqRYcBPxe352wEONxbWxfP+k0piroi2lt7fWRuGzrH0FiDtsqGjRkecqBpN5UxWxZumkpDai9QlgBY1pqImDlXcWPDVkg7Xo7qXtxHrMgM9NxoJtRRL4zk0fppqU0+N0Gxf1AWkSUCKxCqyZl2nLUKfk8N6Zl4WXLA6Cmxbg8YWKlXpRpqmOqv59Bu0Y+mWgqpZuW0sB3DkLoHvCkDNE5KMogF2KJ54PSTUtDOva2FLAgw7Q86h1mloorkXw35RXVn6p5/oCCbBD38nn4uHcYKM20NLgpCx6odku81mFBdk2K1y5NZZ1qq4lROtmYB5PH4HHmMhke07LIxzv7xCU/XmDCd8zEdWnHNRJKlzMy+pExK3A6K1k3s31RxjIspk1UBN2V29IuDTDsKdWip0eMJZk2USmUUPxdmYe3pn4Jtimr7MLyfbNtp8Jk2kRfoTQIX++jLgvfJ+bFF9u/pOUXbtuXZpJpE33FLrgoFTBdJ1J5kKgMpnVKA54keXiZCNNR234ZxEPyTJs6MomBwoKMthX/h0IWeaZNJGpHmvoTiWHnCSnEjjjucZ8NAAAAAElFTkSuQmCC>