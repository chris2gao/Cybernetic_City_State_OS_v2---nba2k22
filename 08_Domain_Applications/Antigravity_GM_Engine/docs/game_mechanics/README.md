# NBA2K20–23 终极联盟游戏机制知识库

> **2026-10-28 Player原生工程增量（静态恢复，未实机验收）**：[四槽PlayType合同](../../research/rea_native_control/PLAYER_PLAYTYPE_NATIVE_CONTRACT.md)恢复4个独立Setter，并复用既有0..15类别名称。每个逻辑动作限制自己的槽位，Player无默认编辑权限；另有独立[属性/倾向工程增量](../../research/rea_native_control/PLAYER_STAT_NATIVE_CONTRACT.md)：54项能力/耐久与99个倾向位置恢复原版索引Setter，角色权限按字段限制；Potential/徽章仍不可调用。完整父对象复制体保留为研究候选。

> **2026-10-28 Native工程增量（静态恢复，未实机验收）**：[K04补充§22](guides/K04_COACH_AND_PLAYS.md#22-pc22原生轮换分钟调用链2026-10-28工程增量)及[完整调用合同](../../research/rea_native_control/ROTATION_MINUTES_CONTRACT.md)记录明确球员分钟0..48的原生Setter/球队变更路径，排除可能截断输入的MyCareer分支。它不证明当前存档、UI、模拟或持久化效果，不改变历史R02/R07验收状态。

> **最新R07修复断点（2026-10-21）**：研究已按[独立审核](../development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)完成A/B两项定向修正并[提交自检回执](../development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)，状态`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`。两个R01目录ID现明示为人工指南主题别名，8个能力组的模型查询层已与执行/审批/存档真实性分开。**正在等待独立简短复验，不能自行声称DEV29研究已经正式结案。**


> **R07最新交付（2026-10-21，待独立审核）**：[R07七层证据成熟度指南](guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)、[40组能力矩阵](catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)、[694项分卷索引总入口](catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)及[DEV28研究交接](R07_TO_DEV28_EVIDENCE_HANDOFF.md)已提交。索引采用**7卷可读JSON**，勿当694个原生字段；40组有86处原目录锚点，另单列10组历史生产证据。新游戏读回与执行0。**当前应做R07独立审核，而不是自动启动FINAL-CODEX或DEV28。** R06已经按[正式验收报告](../development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)结案。旧章节中的“R06待审核/下轮R07”仅为历史状态，以[PROGRESS](PROGRESS.md)最新顶部为准。


> **R06独立审核结案（2026-10-21）**：[完整验收报告](../development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)确认R06-A/B/C/D研究交付通过，保留全部PC22本机读写/存盘缺口；R06-D的26关系、20缺口、79源目录锚点核对通过；R06-B定向文档修复通过但十类奖项仍缺直接来源。**当前唯一下一轮：R07研究跨领域可观察事实/可选动作与证据矩阵**，不得开始人格/DEV28写入。下方历史段落里的R06-D“待独立审核”仅是当时发布状态。


> **R06-D已发布（2026-10-21）**：[R06-D跨领域整合指南](guides/K05_K10_K11_CROSS_DOMAIN_INTEGRATION_R06D.md)和[26关系/20证据缺口目录](catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)已发布、待独立审核。**当前唯一下一轮研究建议：R07**（需核对[PROGRESS](PROGRESS.md)最新首节）。历史R01–R06-C的“下一轮”只指对应旧批次；不得重新执行。R06-B的10项不匹配奖项来源修复尚待独立复核。R06-D没有新增SRC/VIS，也没有当前本机PC22读回/写入认证。


> **最新研究入口（2026-10-21）**：R06-B的10条无关奖项来源映射已修复、仍等待外部复核；[R06-C K11赛季/存档完整研究](guides/K11_SEASON_SAVE_PERSISTENCE_R06C.md)及[38类候选目录](catalogs/R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json)已发布，SRC-0187..0199，目标PC22实机保存、跨季GameLog与原生UI仍UNKNOWN。**下一轮 R06-D 跨域整合**，只以[PROGRESS](PROGRESS.md)第一节为权威，不再重新启动R01/R02/R05或R06-A/B/C。

> **独立质量审核（2026-10-21）**：[R06-B跨窗口恢复与来源映射审核](../development_reviews/DEV29_R06B_CROSS_WINDOW_RESEARCH_QUALITY_REVIEW_20261021.md)已发布；新窗口恢复合格，R06-B初稿的10项不匹配奖项来源已完成有界修正、待外部复核，不影响立即开始R06-C。以下旧R06-A、R05条目的“下一轮R06-B”等文字仅指对应历史批次，**只以最新PROGRESS决定现在的入口**。


> **最新断点（2026-10-21）**：R06-A已发布；**[R06-B历史纪元、奖项、纪录、社交媒体与规则变更研究](guides/K10_HISTORY_AWARDS_MEDIA_R06B.md)**及其[31类目录](catalogs/R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json)已发布，来源SRC-0174..0186，原版PC22完整新图证0。下一轮 `R06_C_SEASON_PHASE_ADVANCEMENT_SAVE_PERSISTENCE_RESEARCH`。以[PROGRESS](PROGRESS.md)为准，不重开R01–R05、不重新做R06-A，也不开发人格系统或DEV28执行器。


> [**项目级意图：R知识库只交游戏原料**](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：DEV29提供NBA2K20–23真实游戏机制/菜单、动态数据、全部可选参数与相互作用；DEV28建设I/O。人格算法、角色谈判/行为规则、媒体与调度不是本知识库任务。R04八个交互案例仅供发现素材接点，当前R05研究游戏财务/合同/选秀/球探原料。

## 2026-10-21 研究职责纠正：游戏原料不是人格算法

**用户权威[六阶段运行流程与DEV29研究边界](RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)**：采集模型→数据分析模型→独立教练模型→独立球员模型→各队GM模型→汇总交执行模型（经玩家批准实际写入）。教练与球员人格系统尚未开发，目前主要已有GM人格系统；**本资料库只解释游戏到底有哪些信息、设定、选择、机制与后果，可以交给不同模型使用**。八个R04虚构互动场景和候选`role_rights`仅是研究资料分类，不是对未来智能体的固定决策、拒绝或谈判规则。球员人格、教练人格、媒体与流程调度是其它开发任务。R04已结案，R05-A/B/C/D已由用户接受研究结案；R06-A全局游戏设置/3D与日历模拟研究已发布，R06-B历史/奖项/媒体下一轮。选秀权世界三年上限已取消，旧代码独立Codex任务不阻塞研究；严格保持研究与开发职责分开。


> **研究工作主入口**：面向所有网页GPT、GM、数据分析、Codex和Antigravity。主研究版本为NBA2K22 PC本世代MyLEAGUE；NBA2K20/21/22次世代MyNBA/23系列用于理解机制、攻略、查漏与版本对照。**内容仍处于资料库建立阶段，空缺不等于游戏没有该功能。**

- **[最新正式研究路线（DEV29 V3，多角色自主涌现）](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)**（[V2网页GPT多轮交付规范](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)继续适用）
- [研究进度与恢复指针](PROGRESS.md)
- **[R06-A全局游戏设置、3D比赛与日历模拟中文指南](guides/K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md)**：新§§0–6；同版PC22玩家实证CPUvsCPU 3D和Calendar Sim不同、Setup/Simulation多级选项与Normalization风险；[86项世界设置Registry候选＋118类菜单/参数研究目录](catalogs/R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json)明确当前存档真实值和原生UI/效果未知。**历史批次原预告R06-B（现已发布），现行下一轮看顶部PROGRESS指针**，不开发任何人格系统。
- **[R05-D经营机制全域交叉攻略§§23–29](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)**：[54项原生注册/候选数据、63类研究动作、12项跨域机制联动、12项证据/能力缺口机读合集](catalogs/R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json)。**2026-10-21用户已取消选秀权仅三届交易规则**：权威[政策V4](../../config/gameplay_policy.json)、[文档26](../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)均已更新；已读5届资产不是新世界上限，旧代码`+3`仍须后续独立授权Codex同步，不是已经可执行5届。R05知识研究已完成，R06下一轮。
- **[R05-C员工、球探、历史选秀与Draft Class机制攻略](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)**：新§§16–22；8类PC静态员工岗位/13项原生STAFF字段、同版次世代四部门/17员工上限、可见Scouting Report与D.E./2K榜单、Generated/Historic/User Created Draft Class和1984–2020轮回。完整可检索[STAFF/Scouting/Draft机读目录](catalogs/R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json)。**PC22员工聘任与新秀注入仍未获可执行验证，R05-D已完成整合**。
- **[R05-B真实交易、选秀权与名单原生机制攻略](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)**：新增§§8–15，实际CBA工资匹配非纳税三档、2K22交易开关、PC交易故障玩家报告、原生5届300选秀权和**2026-10-21已撤销的旧三届限制**的分界；[R05-B 16项菜单/操作候选、14项Native结构与选秀政策机读目录](catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json)。R05-C和R05-D均已发表；不设计GM交易评分。
- **[R05-A经营机制中文攻略：工资帽、球员合同、税线、财务与自由市场](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)**：2021–22现实参考/2K22原生可选项严格分级、17项Player合同字段、Bird/RFA/QO/Cap Holds、现金与预算证据边界；[经营字段与操作研究目录](catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json)保存10项球队财务字段候选和21类市场机制。**R05-B/C/D均已继续发表**，不设计GM报价程序。
- **[R04-D Player⇄GM⇄Coach⇄Media互动图谱](catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)**：8个自主博弈/交易、签约、教练打法、训练伤病与媒体案例；[109个字段双语义侧表](catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)。仅研究映射，不是Agent/执行软件。
- **[R04-C球员动机、人格徽章和职业选择研究目录](catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)**：3项同版0–100职业偏好、21个人格Badge候选、4类动态状态与6种自主谈判候选；研究用，非Agent执行器。
- **[R04-A 球员个人资料、能力、耐久、徽章和自然成长中文指南](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)**：39项当前已命名非耐久属性、16项身体部位耐久，以及职业档案和成长机制；[72项原生+37项候选字段与权限矩阵](catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)、[80技能徽章+20人格候选参考目录](catalogs/PLAYER_BADGES_R04_A_REFERENCE.json)。
- **[R04-B 球员倾向、PlayTypes、AI打法与快模拟机制研究](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)**：精确记录48已命名+51未命名原生Byte、99项独立的2K22归档导出名称，及[原生与外站双目录](catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)；三维/快Sim/Touches/Shot作用保留同年玩家争议，不强制统一球员倾向。
- [R03-A/B/C历史研究结项](R03_COMPLETION_REVIEW_CHECKPOINT.md)：用户已批准研究结项，原生健康数据欠账继续保留；当前进度以已成功更新的[PROGRESS](PROGRESS.md)为准。
- [R03-A历史断点](R03_A_PROGRESS_CHECKPOINT.md)：保留首次训练研究与用户跨代复用的原始记载
- [可追溯的资料来源登记](SOURCES.md)
- [机制卡片写作模板](MECHANISM_CARD_TEMPLATE.md)
- [游戏截图及媒体资料规范](visuals/README.md)
- [外部截图/图文证据索引](visuals/EXTERNAL_VISUALS.md)

## 主研究领域（K01–K12）
K01逐场比赛/赛程；K02球队和球员普通/高级统计；K03球员和名单；K04教练和攻防/Playbook；K05实时3D游戏设置；K06训练/伤病/疲劳/成长；K07财务/交易/合同；K08选秀/球探/休赛期；K09员工/球队文化；K10历史/奖项/纪录/媒体；K11存档、自动化与跨期覆盖；**K12球员自主权/人格/关系及合同偏好到原生系统的桥接**。

## 每轮工作原则
研究窗口在每轮任务中**先搜索玩家社区/攻略及官方游戏说明**，核对所引用材料的2K版本/平台/模式；从已有资料链接与图文截取准确事实，用自己中文文字解释**是什么、怎么操作、为什么有效、联动什么、GM怎样决策、需要什么输入与输出**。每轮将新增的主题文档保存到`guides/`，使用稳定`K##`能力标识和可追溯`SRC-####`、`VIS-####`来源/图片ID；更新本页/PROGRESS/SOURCES后完成当前轮，不在未完成研究中等待用户。

**跨世代研究原则（用户2026-10-21确认）**：终极联盟类机制在NBA2K22次世代与PC本世代之间大体可复用，尤其训练、经营、教练、球员发展和角色可选行为；**优先采纳次世代资料作为机制与角色原料**，而不是一概排除。具体新增页面、精确菜单、游戏原生字段、数值和执行能力仍分别核实；物理/比赛引擎差异另行研究。

**不要从“已经拿到的内存字段”反向定义整个游戏功能全集。** 原生字段认证与“可看见/可选/可写/可保存”是独立状态；没采到逐场比赛≠游戏没有逐场比赛。旧版本和次世代可用于机制理解，不自动证明PC22内存相同。

新研究文档必须能帮助：
1. GM知道可以做哪些真正有篮球意义的经营与战术决定；
2. Analytics知道支持决定的真实比赛/球员数据及可派生指标；
3. Antigravity知道应该到哪个游戏页面和原生结构定向寻找缺少的来源；
4. Codex能在研究结束时生成DEV28最小补齐清单，不重复架构和执行器。

**视觉材料**：优先记录第三方页面和图片链接、使用位置、图片证据点；确有传播许可或玩家自供的图片才纳入GitHub。不得绕过水印/假定可自由再分发；研究卡片即使没有图片二进制也必须完整可读。

**当前权威研究状态（2026-10-21）**：**R01与R02公开资料研究均已结案，PC22原版UI缺口封存，不是原生游戏数据/执行器已全面认证**。R01：[K01/K02 §§0–22](guides/K01_K02_GAME_STATS.md)，`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`；R02：[K04 教练、攻防、Playbook、Freelance、ACE及角色原料 §§0–21](guides/K04_COACH_AND_PLAYS.md)，`R02_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。研究来源登记至**SRC-0048**：[SOURCES](SOURCES.md)，视觉索引为**VIS-0001..0008**：[EXTERNAL_VISUALS](visuals/EXTERNAL_VISUALS.md)（其中没有被认证为目标原版PC22全部Coach菜单的新增图证）。**新增纯研究、不可执行的多角色能力原料目录**：[K04_ROLE_CAPABILITY_RESEARCH_V1.json](catalogs/K04_ROLE_CAPABILITY_RESEARCH_V1.json)；只描述观察/候选选择/角色拥有者/权限/反馈来源，不开发Agent、不产生游戏写入许可。**R03-A/B/C全系列研究已由用户批准结项**：[K06中文攻略 §§0–15](guides/K06_TRAINING_HEALTH_GROWTH.md)、[R03审核报告](reviews/R03_COMPLETENESS_AUDIT_V1.md)；来源SRC-0049..0071，VIS-0009/0010；[11项训练原料目录](catalogs/K06_TRAINING_ROLE_INPUTS_RESEARCH_V1.json)及[8项健康事件目录](catalogs/K06_HEALTH_EVENTS_AND_ROLE_RIGHTS_V1.json)。**原生健康动态数据与Agent执行层仍未就绪**；用户已批准开始R04-A，并已正式发表，具体接力与停止条件见[PROGRESS](PROGRESS.md)。
**R04-A/B/C/D全部研究已发布并归档**：SOURCES累计至SRC-0113；[K03/K12 §§0–29完整球员机制研究](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、[四角色八案例互动图谱](catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)、[109项字段原生/外部双语义侧表](catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)与A/B/C原料目录共同提供角色可观察、可选择、可拒绝、失败与学习的机制基础。**R04研究结案≠PC22全部UI/原生数据/Agent执行器已就绪**；真实游戏更改仍需本项目合法操作与玩家批准。**R05-A/B/C/D全部已发表：K07/K08/K09经营领域完成资料整合，R06尚未启动**。

## 新增球员系统研究与涌现方向

玩家确定：所有游戏机制知识必须让**GM/球员/教练/媒体作为独立角色**拥有真实可观察状态、合法可选行为、协商权、信息限制与比赛/历史反馈，而非强制产生最优决策。R03仍研究训练/恢复一般机制；**R04独立研究NBA2K20–23的全部球员身份、属性、潜力、倾向、徽章、人格徽章、耐久/伤病、合同偏好（Play for Win/Financial Security/Loyalty）、球员职业自主权及字段双语义**；原经营R04顺延R05，其余后移。详情：[R04专项任务书](../development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)。原生Ability/Potential/Badge仅正常读取观察，自主Agent同意与**真实玩家的存档写入批准**分开；人格记忆优先外挂SQLite，不擅占仍有效的原生字段。**当前R01/R02已结案，R03/R04/R05均已获用户批准研究结案；R05保持`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`。R06-A已发布，下一轮R06-B尚未启动**。今后研究窗口只负责各R轮研究交付，独立完整性审核由其他模型负责。

2026-10-28徽章执行工程后续：[明确联动前后状态的原版规则接口](../../research/rea_native_control/BADGE_NATIVE_CONTRACT.md)已接入98个非哨兵内部字段，保留有效等级修正、原版互斥/表达规则及断言检查；只限明确世界编辑。新的静态/离线能力不提升UI/模拟/存档或R04历史研究验收。

Player当前值工程后续：[显式字段读取与角色快照](../../research/rea_native_control/PLAYER_EDITOR_READ_CONTRACT.md)使用原版Getter取得选定属性/倾向、原始/有效徽章和有序PlayTypes。它补齐编辑前值来源，仍是未实机验收的原生控制研发读取接口，不替换正式数据采集/数据库/历史链，也不重开R04研究。
