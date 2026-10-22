# DEV29 / R0 — NBA2K20–23 终极联盟游戏机制与玩法知识全域研究：DEV28强制前置 V1

## 执行规划版本升级：DEV29 V2（2026-10-20）

**[DEV29 V2（网页GPT多轮研究、图文机制资料库、Codex最终收尾）](DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)已取代本V1中的执行组织和R0-C“Codex早期主责”安排。** V1研究领域、版本比较及数据完整性问题保留作为历史设计；以V2为实施权威。玩家确认PR #12已合并，知识资料库入口：[docs/game_mechanics/README.md](../game_mechanics/README.md)。

> 2026-10-20 / Web Development，基于玩家明确提出的下一阶段开发前置要求。本项是**研究、机制目录、采集/执行需求反向审计**，不是新增的游戏内存写入、编码测试、生产采集或自动启动任务。计划执行时间顺序：**PR #12收尾与玩家合并决定 → DEV29（R0研究基线）→ DEV28（数据/控制透明化实装）→ GM真实运行与质量评估**。任务编号29只是新文档后补编号，**执行顺序上先于28**。
>
> 相关长期研究规范：[GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1](../GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md)。开发必须主动先查优秀玩家社区、游戏攻略、2K官方手册/开发者说明，再对照真正使用的NBA2K22 PC本世代原生来源。NBA2K22/23次世代资料**允许且应积极使用**，只有具体菜单、偏移、对象和应用机制需在PC22验证。

## 0. 为什么必须先做：重新定位设计入口

过去的开发顺序容易变为“哪个内存地址先找到→先采哪些数据→数据库记录哪些字段→GM从不完整统计里勉强分析”，导致**动态逐场比赛、每场球员Box Score、可见高级统计和完整管理操作目录未被系统性发现/设计**，尽管已开发采集流水线、M0–M4、经营与BPTI。用户指出此缺陷破坏了GM评估真实篮球表现的基础。

根据现有[DEV24](DEV_20261020_24_BPTI_ANTIGRAVITY_GAME_DATA_SOURCE_REQUIREMENTS_V1.md)，生产`games_box_scores_standings=VERIFIED_PARTIAL_SEASON_TOTALS`，**当时仅30队赛季胜负与累计、约389 indexed球员赛季总计，并无已认证的逐场Game实体/赛程/Box Score/独立时间序列**；`injuries_availability_rotations=NOT_OBSERVED`。这不是“统计指标不够漂亮”，而是**对手、日期、阵容变化、真实战术调整效果的因果证据无法从赛季累计还原**。注意该状态是已记录批次的现状，后续生产变化以最新实态为准，不能声称NBA2K22游戏本身不存在逐场数据。

本项的任务目标是：**先真正理解游戏玩法和GM职责，再列清游戏在20–23系列中提供的全部相关信息与控制能力，转为“游戏内源→GM需要→现有工程状态→开发动作”的逐项台账，供所有模型共享**。不是单纯扩写篮球哲学文献库，也不是承诺知道所有未公开引擎公式。

## 1. 版本与资料覆盖

### 研究优先级（两维：机制可学、执行可落地）

| 版本与模式 | 研究用途 | 证据边界 |
|---|---|---|
| **NBA2K22 PC本世代 MyLEAGUE** | 唯一实际执行目标：此版本有哪些菜单、值域、比赛数据、可选战术和操作 | 菜单/原生字段/持久存储经当前PC实机或已认证资产核对 |
| **NBA2K20–21 MyLEAGUE / MyGM** | 继承机制、统计页面、战术、训练、合同/资金、已知Bug和实践，发现22可能遗漏的源 | 前代存在不证明22当前平台也有 |
| **NBA2K22次世代 MyNBA** | 深入理解同代员工、训练、Prep Hub、教练AI及战术设计意图 | 战术/经营原理可参考，特定PS5界面/内存不直接认作PC22 |
| **NBA2K23本世代及次世代 MyLEAGUE/MyNBA Eras** | 用后代的详尽设定表、时代战术、历史球队行为、联赛规则、统计和经营菜单帮助发现22盲区 | 23新增功能不能倒推22必定支持；Eras历史知识可为本项目1984–2020循环选秀和纪元体系供研究 |

原则：**重点深学NBA2K22，20/21用于查漏与机制来源，23用于补全解释/对照差异**；不用按四个版本全部逐页手抄菜单、对每种设置人工重复研究四遍。跨代共通机制保留，版本差异登记出来。

### 初始已核对的公开资料示例（这是研究入口，不是最终完整百科）

1. [2K官方：NBA2K22 MyNBA 新增MySTAFF/Prep Hub/Conditional Coaching](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)（2021-09-08，明确PS5/XSX）：员工/球队与个人训练/疲劳管理/对手准备/教练策略的设计思路；不能自动证明PC22同菜单。
2. [Operation Sports：Schnaidt1 NBA2K21 MyLeague+Gameplay滑块](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/900202-schnaidt1s-2k21-myleague-and-gameplay-sliders)（2020-09，社区），同时列出疲劳/伤病、训练、成长、交易/合同/士气/化学反应、模拟及场上滑块；属于玩家配置，**非官方效果公式**。
3. [OS：NBA2K20 MyLEAGUE Per36 Player Stats可显示错误](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/881691-nba-2k20-bugs-glitches-thread/page8?page=35&t=957808)（PS4玩家反馈），明确当时有`Player Stats`、`League Leaders`、`Per 36`界面。
4. [OS：NBA2K20 MyLEAGUE Game Logs与赛季高级统计不一致](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/883676-nba-2k20-myleague-thread/page9?postcount=101)（2020-01）：玩家通过逐场日志发现赛季累计/Per36/advanced统计错误；证明研究必须覆盖**game logs与累计的不同来源及校核**，但不证明PC22当前全部有此菜单。
5. [2K官方：NBA2K23 MyNBA Eras历史机制](https://newsroom-uk.2k.com/news/rewrite-nba-history-in-nbar-2k23-with-all-new-mynba-features-for-playstation-5-and-xbox-series-xs-consoles)（2022-08-18，次世代）：1983/1991/2002时代设定、历史联赛与球队历史参考。
6. [NBA2KW：2K23 MyNBA Settings Explained](https://nba2kw.com/nba-2k23-mynba-eras-settings-explained)（2022-12）：从游戏UI角度列开档、全局与球队设置选项的种类和值域，适合借鉴**设置清单长什么样**，非PC22原生字典。
7. [NBA2KW：NBA2K23 MyNBA Eras详情](https://nba2kw.com/nba-2k23-mynba-full-details-new-features-mynba-eras-more)（2022-08）：时代打法、历史规则、联赛迁移、战术与球员倾向的变化；补充纪元GM历史线理解，但不能将23独占项冒充22执行能力。
8. 当前项目共享池`web_gm/knowledge/plays/play_pool_v1.json`已有84归档书、1392 CRC、1345静态名称；`'95 FIST 15 SIDE`已有CRC及玩家命名规则。战术12目录类别与球员0..15原生PlayTypes分开；待认证CRC→本机类别。

以上资料仅证明调查确有真实入口，**尚未完成全系列研究**。后续按主题找对应最好的官方、社区、实机素材，不靠堆链接替代吸收。

## 2. 研究覆盖矩阵：所有模型应共同掌握的GM知识

| 研究域 | 游戏内主要内容与可见/可控候选 | GM分析/决策需要回答 | 下一阶段采集/执行需求 |
|---|---|---|---|
| **K01 逐场比赛与赛程** **P0** | 日期、对手、主客、阶段、常规赛/季后赛、game logs、完成/未完赛、比分、节次、球队和个人box、球员参加/DNP、历史保留窗口 | 最近几场为什么输赢？哪些对手与阵容变化？谁真实上场？ | `games/schedule/player_game_stats/team_game_stats`，稳定GameID与save/generation |
| **K02 球队/球员统计与高阶指标** **P0** | totals/per game/per36/advanced/shot charts/对手统计、分区投篮、出手分布、效率；游戏UI真实提供哪些、哪些能由box导出 | eFG/TS/pace/offrtg/defrtg、球员角色、伤病/效率如何分析？ | 原生计数与显示高阶分级；派生高级指标须明确公式、基础数据与估算标签；不能把NBA.com现实tracking冒充NBA2K22 |
| **K03 阵容与球员职业事实** | 位置、真实能力/倾向/徽章/PlayTypes/伤病/疲劳、出场/首发/轮换、潜力、合同与角色 | 缺人还是使用不当？球员之间的互补与培养路径是什么？ | 真值 vs GM_SANITIZED、按save、比赛时队伍身份、原生可读、写入审批 |
| **K04 教练与攻防智能** **P0** | Coach默认/对手PERSONAL/OVERALL只读、POE、ACE、Freelance、Playbook/68槽、战术12类/真实类型、调用/纪律性、临场策略、人员轮换 | 当前教练如何布置？AI会如何响应对手？战术如何实际调用？ | 全合法菜单值与解释、当前状态、适配/执行证据、换帅后的绑定 |
| **K05 世界级比赛设置** | USER/CPU gameplay、动作/身体接触、投篮、疲劳、AI全局倾向、不同难度和实战差异 | 为何真人 vs CPU/CPU vs CPU出现不真实行为？ | 实时3D赛场引擎专项；不混同日历Quick Sim参数 |
| **K06 训练/成长/导师/伤病/健康** **P0** | 团队与个人训练内容/强度、休息、球员成长、导师、疲劳、伤病/恢复、训练员效果 | 哪个球员该专项发展？是否该降低负荷？ | Antigravity原生读写来源+Codex结构化训练选项和状态差分；不直接改球员能力 |
| **K07 财务、合同、自由市场与交易** | 工资帽/硬帽/税线/工资增长、合同年份与选项、员工工资、交易/续签/球员偏好、裁员、合同场景 | 资金是否能承担争冠窗口？这笔交易/竞价是否合理？ | 外挂GM虚拟市场权威，Codex最终受控落地，2K原生谈判UI不复制；真实原生预算来源UNKNOWN时不捏造 |
| **K08 球探、历史选秀和休赛期** | 选秀班/乐透/签位、技能与潜力可见度、球探精度、休赛期节点、退休、自由市场 | 能否管理真实不确定性，不让GM偷看历史新秀真实潜力？ | 虚拟GM独立SCOUTING_VIEW权限与球员真值库分离、Codex执行结果同步 |
| **K09 员工、文化、球队长期策略** | 员工岗位/效果、教练哲学/体系、球队目标/老板/预算、身份演化、化学反应/士气、队史 | 30队怎样形成不同的建队与比赛思想？ | Codex员工合同与体系执行、BPTI/M3/M4使用来源分层历史记录 |
| **K10 联盟历史、奖项、纪录与媒体** | 榜单、纪录、场上/赛季新闻、荣誉/最佳阵容、交易事件、纪元风格、队名与迁移 | 历史线怎样自然演化？新闻/角色故事怎么不虚构事实？ | 真实事件采集/GM虚拟媒体分开，玩家批准历史重力外才不修改原生能力 |
| **K11 自动化/存档/阶段、实际作用范围** | USER/CPU自动化、存档后状态、换帅/跨赛季是否重置、全局与球队级设置覆盖、Fast Sim与3D差异 | 为什么修改后没生效、被AI覆盖或游戏新赛季重置？ | D28输入→审批→Codex写入→游戏读回→时间戳/同批来源闭环 |

**P0应首先完成的是K01/K02/K04/K06**：没有逐场比赛和基础/高阶球员数据，不要宣称已具备优质数据驱动GM；没有教练完整可选项与球员训练/伤病实态，GM内部改善只能停留在文字。财务/虚拟市场现有规则沿用，后续用研究发现补认知。

## 3. 从“玩家能看到”到“GM能够可靠使用”：逐项必填台账

建议在`docs/game_knowledge/`（研究工程阶段创建，而不是本次预先虚构填满）统一发布三份核心产物：

1. **`FRANCHISE_MECHANICS_ATLAS.md`**：按K01–K11，解释2K20–23玩法、原生菜单/术语、真实例子、篮球/管理用途、各版本差异及至少一条高价值来源。静态规则/菜单、动态事实与真正执行机制分别成节。
2. **`FEATURE_DATA_CONTROL_MATRIX.json`**（机器可读）：每个游戏域的`capability_id`、`game_version`、`mode`、`menu_path`、`available_values`（可选全集）、`data_fields`（输出全集候选）、`update_frequency`、`retention_window`、`GM_decision_questions`、`priority`、`source_refs`、`confidence`、`current_project_status`、`next_owner`。完整枚举/偏移未知明确UNKNOWN，**不允许虚构完整性**。
3. **`GM_DECISION_TO_EVIDENCE_MATRIX.md`**：倒过来从GM业务问题出发列证据链——例如“上月为何输球？”必须至少有逐场赛程/对手/比分/球员box及coach变更前后；只有总胜负与赛季累计则`INSUFFICIENT_EVIDENCE`。如需要高阶指标，先列从box可精确/估算计算的公式与缺少的原生项目（shot zones/lineup+/-等），而不是要求每个术语直接有原生地址。

每行按如下状态标准：
- `KNOWN_IN_SERIES`：官方/社区表明某版本/模式存在此玩法或页面；
- `PC22_UI_CONFIRMED`：玩家截图/实机看到PC22菜单/字段；
- `PC22_NATIVE_READ_VERIFIED`：Codex/Antigravity已经认证原生来源；
- `PROJECT_CAPTURED`：当前同批生产数据库中真实存有；
- `GM_QUERYABLE`：M0等接口能按权限取得；
- `GM_EXECUTABLE_WITH_APPROVAL`：存在受控合法游戏写入执行器与可校验目标；
- `MISSING/UNKNOWN/NOT_APPLICABLE/VIRTUAL_GM_OVERRIDE`：明确缺口、不适用或外挂替代原生业务。

**不要将上述几个状态合成一个completed布尔值**：例如2K20有人在UI看到Game Logs，不代表22本机内存已采；数据库某字段存在也不代表GM实际可查询和可决定。

示例：
```yaml
capability_id: K01.PLAYER_GAME_LOG
needed_by: [WEB_GM, WEB_ANALYTICS, BPTI]
source_versions: [NBA2K20_MY_LEAGUE_COMMUNITY_EVIDENCE]
pc22_menu_status: UNKNOWN
pc22_native_status: NOT_OBSERVED
project_source_status: VERIFIED_PARTIAL_SEASON_TOTALS
requested_content:
  - game_identity
  - opponent
  - game_date
  - minutes
  - player_box_score
  - shooting_splits
analysis_dependency: FIRST_CLASS_REQUIRED
development_owner: ANTIGRAVITY_READ_SOURCE_THEN_CODEX_QUERY
approval_for_game_write: NOT_RELEVANT
```

## 4. 所有模型分工与共享知识约束

| 负责人 | 该阶段必须交什么 | 不应该做什么 |
|---|---|---|
| **网页研究/Astra深度研究** | 主导2K20–23官方+社区+历史玩法对照，按K01–K11整理完整体系说明/版本差异/来源证据；指出玩家实践与算法不确定性 | 只有资料链接、泛泛知识而无菜单/业务用途；把2K23新增功能当22已存在 |
| **网页GM（本项目决策者）** | 列出经营决策所必需的事实与可操作项目、问题对应的最低证据，审查M3/BPTI如何消费 | 在无逐场box时给出过度确定的战术与胜率因果 |
| **数据分析GPT** | 列普通/高级/投篮/时间序列/对手统计源要求，完成每项`可观测/可精确派生/估算/不可得`矩阵，提出M0投影缺口 | 仅排行榜、赛季汇总或用现实NBA统计冒充游戏事实 |
| **Codex** | 从现有Registry/M0/DEV14/SQLite与最新项目文档，制作`功能-来源-采集-查询-执行`交叉审计及后续DEV28工作包最小实现清单；统一仓库知识入口 | 在机制知识研究阶段写游戏、盲目重造执行器、只根据能找到的内存偏移决定需求 |
| **Antigravity** | 只对机制/来源研究明确的PC22缺口定向找菜单/当前运行内存的只读结构和已批准可设置选项（主要Game Logs/Advanced Stats、Coach/Book、训练/健康）；必要时索取按类截图 | 不在未明确需求前广域扫描全部内存或重新造交易/选秀/合同虚拟市场 |
| **玩家** | 对其他模型无法认证、但需要现实PC菜单的少数内容提供截图/文字说明；批准真实存档变更 | 不负责替模型解释网上已有的常见游戏知识，也不需要一次交几十张完整游戏图册 |

**共享方法**：同一份版本化知识库作为所有模型的逻辑依据。网页研究/GM/分析都使用同一来源ID与业务域ID；Codex后续把稳定字段投入机器可读目录，Antigravity反馈原生来源；不同来源有冲突用`VERSION_SPECIFIC/CONTRADICTED/UNKNOWN`标记，不默默覆盖。新的研究结论必须影响`GM_DECISION_TO_EVIDENCE_MATRIX`或功能矩阵的需求，否则不应仅为了资料数量继续积累。

## 5. 任务如何拆分而不陷入“无限完全掌握”

不应在一个无边界Codex会话里“查遍四部游戏所有攻略直到你认为完全掌握”。目标是让**GM域的所有关键能力都被列为KNOWN或明示UNKNOWN**，保证不会再漏掉像逐场比赛数据这样的一整个核心领域；深度优先从影响GM决策的P0域开始。

### R0-A 产品机制与菜单全域研究（纯资料，不改游戏）
- 来源：2K20–23及相应MyLEAGUE/MyGM/MyNBA、官方/社区/攻略/玩家指南，先研究K01–K11目录与玩法作用。
- 特别交付：**统计菜单地图**（Schedule、Game Logs、Box Score、Per Game/Per36/Advanced/Shot Chart菜单真实存在与否按版本分层）、**全管理设置菜单地图**（Coach/Playbook/Training/Staff/Finances/League/Gameplay等）。
- 允许跨世代知识迁移解释机制，但仅PC22实机/真实字典升级为原生可操作。
- 输出图谱/矩阵初版并结束`RESEARCH_A_TASK_CLOSED`。

### R0-B 数据分析需求反向设计（可与A不同模型独立进行）
- 按GM每月/季后赛/休赛期真实经营问题，定义minimum/desired/optional观测，给出`GAME_LOG → TEAM/PLAYER_BOX → ADVANCED_DERIVED → BPTI`依赖链；要求能支持检查某个教练设置调整前后的实际比赛变化。
- 需要特别注明：真实`NBA.com`高级tracking可用于篮球知识/公式参考，但**绝不能当成NBA2K22赛场实际已采的结果**。
- 输出决策证据矩阵、缺口优先级、哪些数据UI可能会保留/过期及其采集时机（后者没实机证据则UNKNOWN）；结束`RESEARCH_B_TASK_CLOSED`。

### R0-C 项目能力映射与DEV28精准规划（Codex主要）
- 只读扫描当前现有`source_catalog.json`、DEV24、DEV28、Registry、M0、已确认Antigravity成果、开发基线；将研究A/B列举每个数据/设置跟实际`CURRENT_CAPTURE/QUERY/WRITE_CAPABILITY`对齐。
- 无来源设`NOT_OBSERVED`，不用为盘点而直接实现一堆新采集脚本；产出`FEATURE_DATA_CONTROL_MATRIX.json`与DEV28实施顺序/阻断清单，记录现有重复能力与最小新功能，避免“全量=仅已知字段”。
- 优先给DEV28-3逐场数据P0、DEV28-1战术书P0、训练与健康状态P0的**明确可观测源需求**，然后交付与结束`RESEARCH_C_TASK_CLOSED`。

三个研究包每个都由玩家下一次**单独触发**。不同模型可并行研究，但每个包在需要人类提供UI时交已完成内容、**真正TASK_CLOSED**，不让Codex占用配额保持PAUSED/WAITING。未经玩家批准不开实机写入、不运行生产全采、不把新研究结论自动变成新增测试和新工程需求。

## 6. R0“完成”不是只写了一本百科，而是形成DEV28可执行启动门槛

研究阶段最低应满足：

1. **全域可发现**：K01–K11都覆盖，其中K01/K02/K04/K06充分建立具体`menu/data/control`选项及差异台账，全部重要数据域至少有“是否已知在某代存在/目前PC22能否认证/未知具体在哪里”的回答。
2. **每项事实可追踪**：引用真实出处，标注20/21/22/23与PC/次世代范围；没有把球迷论坛的单个意见或23新增项硬写成PC22功能。
3. **每项核心GM问题有最小证据路径**：特别是“过去N场对手与比分/球员上场及表现/投篮区域/教练变动前后”不再被赛季累计冒充可解释分析。
4. **数据与控制缺口有明确责任人**：`KNOWN_SOURCE_UNCAPTURED/NEEDS_NATIVE_DISCOVERY/KNOWN_QUERY_MISSING/VIRTUAL_GM_OVERRIDE/UNKNOWN_IN_GAME`，并回写DEV28优先级。
5. **所有模型能使用**：有可读机制图谱、机器可读矩阵、GM分析证据矩阵及统一索引；不依赖某个聊天窗口的长上下文记忆。
6. **不以完美主义阻断**：UI菜单未知可以接受`UNKNOWN`但必须已列在目录；具体高级统计如游戏不提供，明确`DERIVED`计算路线，不能因“游戏没显示PER”就拒绝采可计算基础计数。R0完成不要求穷尽每个赛场AI系数、给出所有CRC真实类型、把全部模块一次写进本局游戏。

**关键角色分工**：DEV29定义「知道什么、需要什么以及漏掉什么」，DEV28才实现「从哪里读取、让GM如何查询/选择、批准后怎样写回」。二者分开，不能为研究进度冒充实际数据已解决。
