# DEV10 M2 — 篮球知识与球队参考研究底稿 V1

状态：`REFERENCE_AND_DESIGN_HYPOTHESES`。研究于2026-10-18进行；本局事实锚点仍由以后实际查询提供。本页不给正式30队经营结论，不覆盖赛季档案。NBA历史资料限定其叙述年代，不能把网页现在的导航年份当文章所属赛季。

## 1. 来源与阅读范围

| source_id | 一手来源 | 本轮使用范围 |
| --- | --- | --- |
| WABC_L1 | [FIBA/WABC Level 1](https://assets.fiba.basketball/image/upload/documents-corporate-wabc-coaching-level-manuals-level-1-eng.pdf) | 原PDF局部阅读：PDF页297–301持球掩护防守、316–318传切时机/空间；不是全书研读 |
| WABC_L2 | [FIBA/WABC Level 2](https://assets.fiba.basketball/image/upload/documents-corporate-wabc-coaching-manual-level-2-eng.pdf) | 原PDF局部阅读：PDF页294–295低位切入及内外决策 |
| JR_PNR | [Jr. NBA Pick-and-Roll](https://jr.nba.com/pick-and-roll/) | 掩护后顺下的基础定义 |
| GSW_MOTION | [NBA：Kerr的进攻理念，2017](https://www.nba.com/news/morning-tip-golden-state-warriors-coach-steve-kerr-outspoken-willing-listen?collection=david-aldridge) | 无球移动与传球体系参考；不提供游戏参数 |
| SAS_MOVEMENT | [NBA：2014马刺传球片段](https://www.nba.com/watch/video/channels/playoffs/2014/04/30/0041300145-dal-sas-play6.nba) | 一个传球后切入的官方例子；不是整季战术效果统计 |
| OKC_PATIENCE | [雷霆官方：Presti回顾2020–21](https://www.nba.com/thunder/story/presti-reflects-210520) | 耐心建设、保持调整能力的组织表述 |
| NBA_2021_TEAM_* | 第4节每队独立官方页面 | 2021选秀前的背景与建设问题，不复制其现实合同/选秀权为本局资产 |
| LOCAL_COACH | `web_gm/manuals/GM_COACHING_OPERATIONS.md`、`config/coach_tactics_profile.json` | 本项目字段/枚举、使用边界与玩家经验 |

FIBA网页抓取遇到文件大小/页面访问限制后，直接下载官方PDF并局部提取文字。下载与阅读材料保留在忽略目录 `_exports/m2_references/`，不随Git提交整本手册。没有查看或声称观看所有教学视频。下文的GM选择规则、角色需求和成本比较是**本项目设计推断**，不冒充来源作者的结论或2K实测结果。

## 2. 首批12张战术卡的内容

共同规则：以下“原生关联”只是选取工具，实际raw须从当前同批字典解析。观察信号优先使用已采能力与赛季统计；缺失的战术回合、跟踪防守和伤病/疲劳数据明确保留缺口。球员能力不是某打法的成功保证。不使用训练、个人分钟锁定、五项Sim或普通属性编辑。

### PNR_PRIMARY — 持球挡拆

基础：掩护者掩护后顺下接应（JR_PNR）。设计需要：持球组织/终结、掩护终结点和外线接应角色；优先查控球、传球、终结与投射能力。代价/反例：持球过度集中、顺下和其他内线占同一区域，换防后缺乏错位处理。

原生关联：`POEOffense=PICK_AND_ROLL_OFFENSE`直接枚举；Playbook/Freelance按已加载名称选择，不保证所有回合都调用挡拆。观察：球队助攻失误、核心实际出场和投篮表现；缺挡拆专属PPP时不以总进攻效率冒充。

### SPACING — 空间与接应

基础：移动应配合队友位置与时机（WABC_L1）。设计需要：能牵制防守的投射及接球决策，不能只数球员名义位置。代价/反例：为射手牺牲护框和篮板；投射差的阵容照搬五外可能无效。

原生关联：`ActiveSystem=PACE_AND_SPACE/PERIMETER`、`POEOffense=GET_SHOOTERS_OPEN`是候选；体系熟练度/比赛成效未据此认证。观察：投射能力、出手结构（有数据时）、篮板及人员互补；“空间米数”当前不可观测。

### MOTION_CUT — 传切与无球移动

基础：传球后切入要阅读防守和队友（WABC_L1；SAS_MOVEMENT为单个例子）。设计需要：多个传球点、终结/投射接应，降低单一持球者负担。代价/反例：决策能力不足时失误增加，复杂体系不适合所有阵容。

原生关联：具名Playbook/Freelance与`RunPlayTendency`；没有“传切成功率”写入字段。观察：助攻/失误与各角色输出，不能从助攻增加单独认定体系因果。核心只有一个可组织点时考虑更简单挡拆。

### TRANSITION — 转换进攻与退防取舍

设计假设：有推进和终结资源时考虑快攻机会，同时保留退防和篮板责任；该卡不是本轮已测战术效果。代价：过早前冲可能损失防守篮板，过度冲抢进攻篮板可能暴露退防。

原生关联：`POEDefense3=RUN_IN_TRANSITION`、`POEOffense3=LIMIT_TRANSITION/CRASH_OFFENSIVE_BOARDS`，按不同端分别选择；不能把两者当同一开关，也不能把Tempo当其替代。观察：篮板和球队效率；缺转换回合率时标不可验证。

### POST_HUB — 低位与高低位枢纽

基础：低位切入可利用错位，内外球员需联动（WABC_L2）。设计需要：可靠内线终结/传球点及外线接应。代价/反例：持球停滞、空间收缩，对手夹击时无人处理球。

原生关联：`POEOffense=FEED_THE_POST`、`ActiveSystem=POST`及具名手册；不声称设置后每回合一定进入某个人。观察：内线能力和全队助攻失误、效率；低位专属回合缺失时不编造。

### SWITCH — 换防

基础：换防是处理掩护的一种方式（WABC_L1）。设计需要：可承担不同对位的防守资源，尤其检查弱点是否会被反复针对。代价/反例：错位低位、篮板丢失，不能因为有多个侧翼就自动全换。

原生关联：`ScreenDefenseOnBall=SWITCH`（当前raw3）和有条件的`OffballScreenDefense=SWITCH`；两个字段作用不同。对手整体组设置不能给某个球员例外规则。观察：对手构成、现有防守/篮板能力；实际换防回合效果缺失。

### DROP_CONCEPT — 沉退护框思路

设计假设：优先保留内线护框，允许一部分外围处理空间；需要内线防守资源和持球防守追赶能力。主要代价是对手持球投射与中距离空间。这是篮球适配假设，不是已认证的2K“Drop”功能。

原生关联：当前`ScreenDefenseHedge`目录没有名为DROP的枚举。`NO_HEDGE`加`GO_OVER/GO_UNDER`只能标 `HYPOTHESIS`候选，不能标直接等价；`GO_UNDER`更不能自动当沉退。缺乏更明确映射时只返回方向，仍可比较直接可用的其他防守方式。

### HEDGE_RECOVER — 延阻与回位

基础：大个临时外扩为持球防守者争取恢复位置的时间（WABC_L1）。设计需要：横移/回位和后方协防资源。代价/反例：顺下和弱侧空位、夹击被分球。

原生关联：`ScreenDefenseHedge=SOFT_HEDGE/HARD_HEDGE`、配合`ScreenDefenseOnBall=GO_OVER`；原生标签存在不证明理想回位一定发生。观察：对手持球人与顺下/外线组合、己方防守能力；不将抢断增加等同防守变好。

### SCREEN_ROUTE — 绕上、绕下与ICE

基础：掩护处理可以从不同路线恢复对球防守（WABC_L1）。设计需要：按对手投射/突破威胁选择，不能统一套用一个路线。代价：绕下放投，绕上需要身后保护；ICE的具体效果仍需本局观察。

原生关联：`ScreenDefenseOnBall=GO_OVER/GO_UNDER/ICE`直接枚举名称；OnBall5独立字段，不未经依据将其解释为“只对中锋”。整体组缺少逐人区分时，以对手整体主要威胁权衡，不伪造单人指令。

### HELP_ROTATE — 协防与保护射手

设计假设：协防可以补突破/内线短板，但会消耗弱侧覆盖。检查对手外线威胁及己方恢复能力，不能单纯把协防拉满。机会成本：底角/外线空位和篮板位置。

原生关联：全队`HelpDefense`与对手`OnballHelp/ScreenHelp/TagOnRoll/StayAttached/PreRotate`各自查字典，不能共用通用raw。PreRotate为0/1，其余按独立枚举。观察：阵容能力和对手构成；缺少轮转追踪，保持效果假设。

### BOARDS_BALANCE — 篮板与阵容平衡

设计假设：篮板职责与转换、空间同时权衡，避免为单项统计牺牲整体。需要篮板资源和可回防的外线；小阵容不自动代表差，双塔不自动代表好。

原生关联：`POEOffense3`与`POEDefense3`分别作用于两端；可选CRASH或中性项。观察：现有球队篮板和相关能力，缺投篮分布/回合数时不编造精确篮板机会率。

### ROTATION_CONTEXT — 轮换深度与自然成长环境

项目依据：玩家经验与LOCAL_COACH。设计需要：平衡主力负荷、替补质量与年轻球员机会；不能把多用替补写成必然成长或健康改善。已知伤病/疲劳来源不足，不估固定风险百分比。

原生关联：`BenchDepth`是人数上限、`BenchUtilization`是替补使用倾向；不指定球员个人分钟。观察实际场均分钟及未来同口径能力变化，因果保持审慎；不追加为选值而做的比赛/保存实验。

## 3. 三队试点：把参考转成可反驳的经营假设

**GSW参考。** 现实球队曾以无球移动组织进攻（GSW_MOTION）。2021官方前瞻讨论即时补强与培养的取舍（第4节）。本项目推断：若本局核心仍在竞争窗口，优先用传切、空间及辅助持球减少短板，再比较即战力交易；若核心条件已改变，则可改变方向。高成本争冠仅作为待评估情景，老板意愿金额保持UNKNOWN。

**SAS参考。** 2014官方片段展示传切；2021官方背景是年轻球员承担关键角色（第4节）。本项目推断：优先评估现有人才、角色互补与内部改善，保留资产选择权；本局出现明确争冠机会时也能主动集中资源。不能因“马刺文化”就断言当前人员必定擅长传球或发展。

**OKC参考。** 球队官方强调耐心与调整（OKC_PATIENCE）。2021官方前瞻呈现选秀资产积累（第4节）。本项目推断：未来灵活性优先时避免为短期改善透支合同和签；本局核心成熟时允许把签集中转化为即战力。现实超出三届的选秀资产不可复制成本项目可交易范围。

三队方法验收见[M2设计](../development_tasks/DEV_20261018_10_M2_KNOWLEDGE_DESIGN_V1.md)；尚未对M02三队执行正式GM分析。参考优先级不是硬编码评分权重，GM须说明为什么当前资料支持或推翻它。

## 4. 30队2021历史参考种子

每行“历史背景”仅是相应官方页面的小型事实摘要；“建议研究问题”全部为本项目推断。来源为2021选秀背景，**不将页面中现实名单、工资、保护签、伤病或续约状态移植成本局事实**。网页部分内容后来混入其他年份交易块，本轮只使用明确标注2021的 Draft Outlook，不使用混年交易信息。

| 球队 | 历史背景（REAL_NBA_REFERENCE） | 建议研究问题（HYPOTHESIS） | 来源 |
| --- | --- | --- | --- |
| ATL | 年轻核心上升 | 内部角色是否足以支持竞争窗口？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/atlanta-hawks) |
| BOS | 双年轻侧翼核心 | 第二组织点和替补怎样匹配核心？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/boston-celtics) |
| BKN | 球星争冠窗口 | 当前核心之外的攻防互补是否可靠？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/brooklyn-nets) |
| CHA | 围绕年轻组织者成长 | 内线和外线角色是否形成接应链？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/charlotte-hornets) |
| CHI | 交易投入后仍未进季后赛 | 额外投入解决的是结构问题还是重复堆进攻？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/chicago-bulls) |
| CLE | 重建青年阵容 | 后场职责和前场空间是否互补？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/cleveland-cavaliers) |
| DAL | 依赖核心持球 | 谁能分担组织并改善侧翼防守？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/dallas-mavericks) |
| DEN | 中锋核心支撑竞争力 | 内线枢纽怎样与外线创造力配合？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/denver-nuggets) |
| DET | 重启与新秀发展 | 哪些角色值得长期保留？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/detroit-pistons) |
| GSW | 培养与即战力取舍 | 当前窗口值得用多少未来灵活性？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/golden-state-warriors) |
| HOU | 巨星离队后重建 | 是否需要先确立持球和防守框架？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/houston-rockets) |
| IND | 换帅寻求稳定 | 体系改善与阵容调整哪个更有价值？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/indiana-pacers) |
| LAC | 双星加角色阵容 | 老核心窗口与替补更新如何兼顾？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/la-clippers) |
| LAL | 即时争冠方向 | 角色互补能否支撑本局核心？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/los-angeles-lakers) |
| MEM | 年轻核心与选秀贡献 | 如何在竞争中保留年轻人的有效角色？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/memphis-grizzlies) |
| MIA | 核心周围空间问题 | 投射和防守取舍是否合理？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/miami-heat) |
| MIL | 为争冠投入资产 | 如何补深度又保护后续合同窗口？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/milwaukee-bucks) |
| MIN | 交易消耗选秀资产 | 现有人才的内部改善能否兑现投入？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/minnesota-timberwolves) |
| NOP | 围绕前场核心补强 | 投射/防守怎样支持主要终结点？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/new-orleans-pelicans) |
| NYK | 重返季后赛后仍在建设 | 现有成功哪些可持续，哪些需补人？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/new-york-knicks) |
| OKC | 积累选秀资产 | 什么证据支持由积累转为集中投入？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/oklahoma-city-thunder) |
| ORL | 交易后重新建设 | 核心候选与重复位置怎样取舍？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/orlando-magic) |
| PHI | 内线优势与进攻适配问题 | 持球与投射能否释放内线优势？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/philadelphia-76ers) |
| PHX | 老将与青年共同争冠 | 两种合同窗口如何连续衔接？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/phoenix-suns) |
| POR | 核心巅峰与防守短板 | 为改善防守付出进攻或未来资产是否值得？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/portland-trail-blazers) |
| SAC | 年轻后场与稳定性问题 | 怎样把人才变成攻防完整阵容？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/sacramento-kings) |
| SAS | 年轻球员承担关键角色 | 内部优化、发展和竞争如何兼顾？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/2021-san-antonio-spurs) |
| TOR | 老核心更替与留存骨干 | 重组还是重建更符合本局资料？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/toronto-raptors) |
| UTA | 外围防守弱点 | 如何保护内线又减少对手外线优势？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/utah-jazz) |
| WAS | 后程反弹后追求进步 | 本局表现改善是否值得长期投入？ | [NBA2021](https://www.nba.com/draft/2021/team-profiles/washington-wizards) |

将这些条目整理为JSON时，每队独立 source_id、reference_period=2021_DRAFT_CONTEXT，`ownership_cost_preference_if_verified=null`；不能默认财大气粗/吝啬、强制交易倾向或永久重建。更深组织史可在后续具体需要时补充，不作为首版工具交付的前置条件。

## 5. 可直接交给实现者的整理规则

卡片保留上述稳定ID及来源类型；字段关联落为结构化 native_links，不把长文塞进每次模型上下文。源注册表只存URL、阅读范围、历史适用期与检索日期，不收录整篇文章。30队seed与三队试点分开：seed给研究起点，试点给如何做判断的方法。正式策略状态由玩家触发GM后产生，开发期只使用候选和合成方法样例。

篮球知识可增强GM能力，但当前没有证据证明新知识已经改善本局胜率、自然成长或财务结果。本轮没有对战试验，也不将这些作为研发交付前置条件。
