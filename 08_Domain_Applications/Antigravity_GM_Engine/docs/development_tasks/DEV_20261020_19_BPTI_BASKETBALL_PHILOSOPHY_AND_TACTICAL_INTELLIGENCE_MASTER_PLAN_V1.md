# DEV19 — BPTI 篮球哲学与战术认知引擎：开档前总开发规划 V1

2026-10-20 | owner: Web DEVELOPMENT | implementation: 后续经玩家触发的研究模型 / Antigravity / Codex | status: PLANNED_NOT_IMPLEMENTED / NO_NEW_GAME_AUTHORIZATION

> 本文件为玩家要求的正式项目开发规划，**不是启动BPTI开发、额外测试、游戏写入或合并PR的授权**。后续各阶段单独立项；任何新增设计或测试须遵守AGENTS.md及PLAYER_DEVELOPMENT_POLICY_V2。篮球理念从真实篮球出发、通过NBA2K22已认证机制执行，M0–M4仍作为数据、经济、知识检索、决策/执行和系统管理的基础。**M系列是经营能力，BPTI是篮球认知。**

> **2026-10-20研发顺序更新（覆盖本V1原先“先Bug/双引擎校准、后BPTI”的开发调度）：** 玩家决定M4工程结束后优先开发BPTI；R1 GPT Deep Research、R2 Gemini Deep Research、R3 Web GPT可立即并行研究，Codex须等研究成果整合后逐阶段实施。Issue #6修复、季后赛数据采集和双引擎校准器可以安排在BPTI工程之后，但**正式新档采集与开档的事实来源前置条件不取消**。具体三方研究分工及Codex前置交接见 [DEV21](DEV_20261020_21_BPTI_THREE_RESEARCH_STREAMS_BEFORE_CODEX_V1.md)，首批证据缺口见 [BPTI R0](../development_research/BPTI_R0_EXISTING_ASSETS_AND_EVIDENCE_GAPS_V1.md)。PR #4现已合并，旧文档记录为编写时历史。

> **2026-10-20 BPTI开工前评估增量：** 三路研究R1–R4已形成篮球因果及历史演化逻辑的基本闭环，不以扩充全部历史案例为前提。关键战术手册CRC/实际角色语义专项调查[DEV23](DEV_20261020_23_BPTI_CORE_PLAYBOOK_SEMANTICS_CODEX_DISCOVERY_V1.md)可在B0/B1后、B2关键映射前进行；逐场赛果/Box Score/球员出场/伤病与高级表现的[DEV24](DEV_20261020_24_BPTI_ANTIGRAVITY_GAME_DATA_SOURCE_REQUIREMENTS_V1.md)可并行。两项不是B0/B1启动阻断条件；缺原生语义的动作仍HOLD，缺逐场真实数据的经营诊断不得伪造。当正式开档时，已批准的真实采集阻断修复和新批次权威仍必须另行达标；原V1旧先后顺序由此增量更新覆盖。

## 0. 建设目标与开档闸门

项目最终目标：在NBA2K22 PC Current Gen 的终极联盟里，30支球队由有组织连续性的GM独立经营，以真实篮球原理、教练哲学、球员独特技能、战术协作和对手反制生成策略；利用M系列的数据/财务/战术工具检验策略并生成审批后可执行的稀疏动作。不能仅以联盟同一预期效率公式优化30队。真实比赛由游戏引擎完成，不重新发明篮球物理引擎、实时教练AI或胜率预测器。

正式开档前须完成：①M系列及M4工程收尾、代码整合；②影响全量真实采集的已知必要bug修复（含Issue #6）；③已单独确认的季后赛逐场/球员/球队/高阶统计采集和双引擎校准器的可用实现（年度真实校准发生在开档后的首个季后赛，不能预先宣称已校准）；④BPTI篮球知识、Game Mapping、30队初始体系与GM决策接入、无游戏写入的验收；⑤玩家批准正式开档。真实30队策略当前UNASSESSED；原M3合成验收不能代替BPTI的30队篮球策略准备。

不要因为本规划自动改原GM V3/V4规则或启动游戏写入。M4的**系统自我进化**是技术缺口、异常、开发候选与审批管理；**篮球经营反馈**属于GM业务；**3D与日历Fast-Sim校准**属于独立校准器。这三个职责永久分开。

## 1. 既有工程基础与避免重建

- M0: 原双库/同批SQLite受控查询、GM遮蔽消费；M1: 财务与三年情景；M2: 12张战术卡、30队现实参考、TEAM_STRATEGY_STATE_V1及可检索知识；M3A/B/T: D1–D6、HOLD/INTERNAL/MARKET、30队市场/角色、球队手册、球员倾向、个人防守、训练及GM稀疏动作；DEV14: Observed/Desired/Applied、采集、身份/审批、执行器。
- 截至规划时PR #5已合main 570419a；PR #4 head 7e8ba1a仍Draft未合并，M3-T仅合成8项目标通过，GM V4未启用；不要冒充实机验证。
- 已有能力：教练19项读取/正常18项提案、8种系统、Freelance、球队同名已加载书68槽、个人四PlayTypes+Initiator、48项具名倾向（51未知只读）、PERSONAL_DEFENSE 18项、训练6+5、Intangibles 25–99软轮换。普通GM不写OVERALL_DEFENSE、自由PlaybookID、原始Ability/Potential/徽章，也不锁精确分钟。
- 本工程按需扩展现有gm_workbench、GM知识索引、策略状态和gm_core DTO/工作流；原则上**不创建第二套经营数据库、并行执行器、原生内存写入路径或巨型自动测试平台**。

## 2. 认知层次：从篮球思想到原生动作

五层业务模型（彼此有清楚身份）：
1. FRANCHISE_IDENTITY（球队组织文化）：由经考证的历史/管理传统形成，如培养、纪律、创造力、风险偏好；稳定但可合法演进。**不可从当期球员名单倒推或编造老板偏好**。
2. COACH_PHILOSOPHY（主教练）：攻防理念、角色自由度、调整能力、适用条件；与队伍传统可能存在张力；换帅事件改变教练而不抹去组织历史。
3. BASKETBALL_SYSTEM（场上篮球模型）：进攻怎样创造优势；球权/空间/运动/对抗/挡拆/中距离/低位/篮板；防守怎样压迫/协防/护框/换防；不止是命中率标签。
4. PLAYER_ROLE_AND_AGENCY（球员职责与创造力）：primary initiator/secondary creator/offball threat/post hub/connector/screener/defender等，明确脚本执行、读防守后的选择、late-clock bail-out、巨星自由度，不能用全联盟平均命中率抹杀球员特长。
5. MATCHUP_GAMEPLAN（对手比赛计划）：个人防守、战术侧重、应对包夹/换防/沉退/联防/低位错位，主方案、对手反制、B方案；不因单场统计自动改变球队身份。

由BPTI提出篮球意图 → M3评估本批事实/内部替代及市场方案 → DEV14把获批稀疏目标受控映射至已认证字段。篮球概念不直接等于游戏字节或已认证行为；任何无法映射的动作输出UNSUPPORTED/UNKNOWN及可行的低保真替代，不发明CRC含义。

## 3. 篮球体系知识图谱（初期10个非互斥家族）

首批研究，不当成不可变的10队模板：
- Motion/Read-and-React（无球移动/多人决策/掩护后的二次动作）
- Triangle/Inside-Out（空间三角/高低位/巨星终结）
- Spread Pick-and-Roll（持球挡拆/顺下/外弹/弱侧接应）
- Isolation/Shot Creator（1v1/中距离/造犯规/末节困难球）
- Post Dominance / High-Low（低位/夹击阅读/外线回传）
- Point-Center/Elbow Hub（高位中锋策应/手递手/空切）
- Transition / Early Offense（推进/半转换/退防代价）
- Defense-First / Rim Protection（沉退护框/防守篮板/轮转）
- Switchable Pressure Defense（多位置换防/压迫/弱侧轮转）
- Adaptive / Multiple Systems（根据对手和人员切换主副方案）。

攻防哲学正交组合；允许多体系共存，不把篮球等同8个2K教练枚举。每个SystemCard必须有：真实源/时期/适用范围、篮球战术因果链、必要角色和替代构成、球员的自主创造空间、适配防守与弱点、针对性反制和再反制、成本与风险、观察指标及证据等级、可用Game Mapping。证据等级NBA_REAL/FIBA_COACHING/2K22_PC_NATIVE_OBSERVED/2K22_COMMUNITY/HYPOTHESIS/UNKNOWN。

研究以FIBA/WABC教练手册、NBA官方教练/球队战术案例、NBA教练协会和本世代2K22实际玩法资料为主。历史案例要绑定特定赛季与环境，不得把2026现实球队人物和事件倒灌2021游戏初始世界。

## 4. 原生控制映射：需要真正形成联动

BPTI不得直接写数字。引入轻量BASKETBALL_TO_2K_MAPPING（可作为M2知识卡的关联资料和M3业务翻译层），按同批原生字段字典/对象身份解码、按真实当前队册读书：
- Offense: Active/Preferred System、POE、Freelance及其四槽、RunPlayTendency、Playbook现有68槽。
- Roles: 玩家原始技术能力只读；四PlayTypes、Initiator、Touch/Shot/Iso/Post/Drive等**已具名且已认证**倾向可以形成建议；创造者与战术执行者允许混合。
- Defense: 对手具体球员的18项PERSONAL_DEFENSE，整体OVERALL只读；选换防、绕掩护、协防、夹击时查真实enum与身份。
- Rotation/development: BenchDepth/BenchUtilization、训练6+5、Intangibles软轮换，原版AI控制实际分钟与游戏自然成长。
- Staff/head coach: 暂只有策略和已确认换帅后本队同名手册归位；没有已证教练合同真实执行器不编造聘用成功。休赛期每队每季最多一次主动换帅。绑定BookID必须独立审批并重新读取原生槽位后才计划68槽调整。
- 51未知Tendency/真实战术CRC→动作/疲劳/额外位置模板仍为缺口；只把**能够落实当前关键篮球风格的部分**列为开档前必需映射，不因未知全覆盖而无限推迟；若某个球队主体系没有可确认的对应动作，不得虚报可落地，要研究一个最小真实对应或选择篮球逻辑成立的支持方案。

SystemBlueprint编译顺序：球队身份+教练理念+当前人员+对手 → 篮球意图与角色图 → 策略可行性检查（技能、位置/阵容、合同、证据） → 最小有序Native意图集合（每一项包含映射ID、来源、预期方向、备选/HOLD）→ M3/DEV14离线方案及玩家审批。禁止直接用GM模型输出的raw bytes、绝对地址、approved:true。

## 5. 球员创造力与“反同质化”的业务规范

- 效率是反馈和证据，不是统一规定所有球队放弃中距离/低位的唯一优化目标。
- 区分持球创造、自主阅读、战术执行、无球威胁与防守角色。一名巨星可以保有低于联盟平均效率但在强压迫下不可替代的特有进攻手段；必须说明真实技能适配与机会成本，不免费豁免球员表现差。
- 每支队伍有主方案/副方案/失效应急方案，允许依球员变化、换帅、伤病/人员变动、历史选秀和长期战绩演化；单月效率波动不是改组织文化理由。
- 不增加硬性“联盟至少X队必须中距离”等人工多样性配额；差异必须由历史、教练、球员、财务、球员市场与篮球机制自然产生。
- 相同球员对30队可有不同价值，且要说明篮球角色/对方需要/经济约束，不允许一套统一胜率系数自动推导全部交易。
- 需要质疑自己的体系：至少一条可观察的反例或失效条件；不把球队哲学做成免于数据检验的信仰，也不让数据简单吞噬球队身份。

## 6. 30队档案与动态年代

建立30队TEAM_BASKETBALL_IDENTITY_V1：
- 组织文化和已证历史引用（独立于本局事实）；
- 当前主教练思想和候选战术组合（必须按实际同批Staff/Coach资料匹配）；
- 当前核心真实能力、技能创造方式和角色互补；
- 主进攻/副进攻、主防守/对手应对、阵容及替补逻辑；
- 拟落地的2K控制清单、已认证/未认证能力和不能落地原因；
- 财务建队取舍与长期竞争窗口、角色需求；
- 调整/转向条件、历次赛季策略变更及不能抹去的前代记录。
参考2021初始组织传统不等于替玩家预先给30队填充与其当前阵容无关的正式决策。分析时结合可信同批事实完成30队初始实际评估；所有资料中的球队哲学必须有独立历史依据或由用户明确给定的虚构经营理念。正式存档/日期由玩家提供后才能将候选与真实来源封存。

球员自然成长和1984–2020循环选秀由游戏机制/旧世界线控制。乔丹/奥尼尔/科比式球星到来应触发球队体系重构的研究候选（球权、内外、教练、配角、财政），不赋予无批准的能力/潜力编辑。历史重力仍是独立审批通道。球队文化可以跨主帅持续存在，战术结构可因明星更替而改变。

## 7. 正式GM决策编排

基于现有M3 D1–D6插入BPTI意图阶段，**不新建第二套交易决策器**：
- P0/球队身份检索：文化→教练→核心技术/创造力→当前打法与可落地证据；
- P1/场上诊断：如何创造优势、哪个球员承担什么职责、对手怎么反制、替补/疲劳及失败后B方案；数据作为验证和反证；
- P2/内部动作：先比较HOLD/教练、PlayTypes、战术书、个人防守、训练、Intangibles等可执行变更；
- P3/市场与组织：只有明确不能内部改善的角色缺口才建议交易或人员更替（可以有合同/资产驱动原因），交易双方分别从各自篮球哲学评估，兼顾财务；
- P4/交付：简明讲清篮球理由→球员角色→战术/对手策略→游戏目标字段→代价/未知→玩家审批。
定量计算保留确定性Python/SQL，不捏造场上运动物理或战术回合因果；默认每用户触发节点只呈现重点变化和HOLD，内部有完整理由，尊重现有3轮上限及实际V3/V4启用门。

## 8. 开发包与前置依赖（分阶段授权，非一次巨大Codex任务）

B0 认知契约与边界：审阅M2卡片/M3现有schema/DEV14能力，确定SystemCard、Identity、SystemBlueprint、Mapping的最小DTO和证据口径；不新建执行底座。输出详细设计/状态迁移和工作量，玩家批后实施。

B1 篮球知识研究（研究模型优先）：10个非互斥家族，攻防原理、实战案例、角色职责、失效/反制、创造性/自由度；来源回溯，形成可检索卡而非空泛球队口号。可先由Web研究模型完成，不消耗Codex重复开发数据库。

B2 2K22原生映射（Antigravity原生查缺+Codex知识接入）：已有8体系、19教练、68槽、四PlayTypes、具名48倾向、个人防守/训练/轮换完整链接；最需要优先补的是**球队主打篮球方案的真实可识别战术内容**，不是遍历全部未知51倾向。逐条证据分类和Fallback。输出已证Mapping矩阵；不得因Unknown假装已执行。

B3 30队篮球宪章与角色生态：基于2021现实历史证据和本局同批正式人员，逐队建身份与主/副篮球方案，主帅哲学、主创/副创、攻防与阵容、替补和长期变化条件；与TEAM_STRATEGY_STATE版本化关联。目标30/30具有有依据的差异化、可落地的最小方案，不一定30套完全独一的Playbook。

B4 认知驱动的决策编排（Codex）：把BPTI意图接M3已有D1–D6、HOLD/INTERNAL/MARKET与财务双边谈判；复用DEV14离线build_plan，产出稀疏意图及审批tuple，不允许新审批通道；角色/战术/防守字段依赖必须一致，未知止于HOLD/RESEARCH。

B5 跨赛季演化（Codex最小）：球队文化持久化、换帅分离、选秀/交易/核心成熟或离开后的体系再评价、球员角色/创造权调整、赛季节点和旧状态审计；不是用固定年份强制复制真实历史冠军/同质策略，不自动触发运行。

B6 开档前验收（已批准范围内的最小证据）：GSW传切/库里无球创造、CHI德罗赞中距离核心、MIA防守弹性三种性质不同的2021–22初始场景；再用一个优秀持球创造者来到不同球队、一个历史巨星进入另一体系的反事实，证明决策不会统一归结为三分效率。使用真实可用静态/同批数据、经认证的映射和一个纯离线完整intent；未认证必须BLOCKED/UNKNOWN，不能造字节。30队初始策略和篮球身份必须可查询/审阅；球员原始能力和游戏内存不变。**不做大范围无限回归/多赛季实机比赛试验作为开档前门槛**。

每个阶段交付：业务设计/差异、文件接口、真实完成项、未证字段、最小已授权验收、GitHub PR/commit和长期状态；下一阶段启动必须单独由玩家触发。AG研究、Codex实现、Web GM篮球判断、Web ANALYTICS确定性数据分析分别负责自己权限，玩家批准写入及上线。

## 9. 推荐代码/文件落点（建议而非已创建）

- web_gm/knowledge/basketball_systems/：SystemCard和可追溯篮球原则资料（可以与现有12卡链接，不复制第二份）。
- web_gm/knowledge/2k_mapping/：按字段注册和可信证据映射实际NBA2K22动作。
- web_gm/teams/identities/ 或当前策略目录的同等位置：初始30队身份参考；实际赛季状态优先复用已有TEAM_STRATEGY_STATE和gm_workbench.sqlite。
- src/gm_core/ 的轻量认知DTO/分析辅助、M3已有scripts/gm_analysis.py/gm_decision.py适配，复用native plan。
- docs/development_reviews/BPTI_*：设计/研究/映射和分阶段验收；Web GM长期记忆根据用户授权存档。
这些目录是交付建议，不意味着现在就批量创建文件。

## 10. 正式开档验收标准（游戏开始前）

PASS须满足：
1. M系列/DEV14发布的代码底座完成玩家批准的分支整合；BPTI接入现存M3而不是平行替代。
2. 已知影响正式事实来源的Issue #6等阻断BUG按另行批准最小修复；正式数据真实性及GM Potential遮蔽可用。
3. 季后赛比赛来源/Box Score/高级统计采集接口和模拟器校准器至少具备明确可运行路径；**首次真实季后赛校准尚无数据不阻止开档**。
4. 所有30队存在真实有据、能区分组织传统/教练哲学/当前篮球系统的起始档案；历史证据不偷换本局事实。
5. 10家族（可组合）有篮球因果、必要角色、反制、创造力和无数据/无映射的UNKNOWN；每队核心主/副方案至少有已证实可执行的最低映射。
6. 首批GSW、CHI、MIA三队能得到有根据且不趋同的打法、交易与阵容建议，包含球员创造力与反证条件；同一角色球员对不同球队有不同价值解释。
7. 完整路径从篮球意图、当前人员/财务评估到M3离线方案、DEV14稀疏intent/审批tuple贯通，游戏写入必须玩家另批。
8. 30队策略初始准备完成、跨赛季文化演化与变更审计具备最小可用协议；真实常规赛胜率/3D一致性通过开档后自然运营与独立校准器继续积累，不能假称已证。

若某项关键已证原生映射缺失，不应只靠一份漂亮文字档案宣告READY。若缺口不影响大多数体系但某单队动作无法执行，只让该动作HOLD/RESEARCH，不强制全联盟停工或为50个假设风险扩展工程。最终准许正式开档及V4规则切换均由玩家明确批准。

## 11. 权威资料与任务依赖

工程：docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md V2、AGENTS.md、docs/34_BASELINE_CURRENT_STATE.md、docs/GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH.md、docs/development_research/DEV10_M2_BASKETBALL_AND_FRANCHISE_RESEARCH_V1.md、docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md、docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md（PR#4）、web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md（PR#4）、web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md、docs/development_tasks/DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md。
现实篮球：FIBA/WABC教练资料 https://about.fiba.basketball/en/wabc-documents ；NBA/教练协会历史案例及出处见已有M2研究。游戏原生：2021版2K22 PC Current Gen各字段字典/教练原生观察与本仓库真实验证，社区经验仅为假设。
