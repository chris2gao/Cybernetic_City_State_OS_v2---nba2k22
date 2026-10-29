# K04 — NBA2K20–23 教练、Playbook、Freelance、ACE与攻防策略实用指南

> **DEV29 V3 / R02-A；2026-10-20。** 主研究对象NBA2K22 PC本世代离线MyLEAGUE。结合当前仓库已认证原生操作与NBA2K22官方/同代玩家观察，讲清具体机制、冲突、GM经营价值和未知。**文档不授权运行DEV28、Codex、采集、修改原生游戏或调整球员能力。** 当前R02-A为第一批正式攻略，不等于所有战术效果已验证。
>
> 来源：本仓库 [教练手册](../../../web_gm/manuals/GM_COACHING_OPERATIONS.md)、[个人防守与本队手册政策](../../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)、[12类战术研究](../../development_research/NBA2K22_PLAYBOOK_12_CATEGORY_AND_NATIVE_TYPE_MAPPING_V1.md)、[共享战术池](../../GM_SHARED_PLAY_POOL_V1.md)；外部新来源SRC-0030..0039见[SOURCES](../SOURCES.md)。

## 0. 对象与证据等级

| 级别 | 研究结论与界限 |
|---|---|
| PC22_PROJECT_NATIVE_VERIFIED | 项目既有隔离测试已有19项Coach默认设置中多字段读写/回读证据、18项针对对手的防守字段原生信息、34种Freelance枚举PE文本配对、68战术书槽位和CRC定位。不是本轮新做测试，更不是所有设置的3D效果已实测 |
| PLAYER_REPORTED_UI | 玩家已确认PC22战术可浏览12种类别、每人四个有序PlayTypes、四个有序Freelance，以及战术2D预览；“前槽优先”只作定性描述 |
| OFFICIAL_2K22_GAMEPLAY | 官方披露2K22优化AI防守轮转、位置、射门/投篮IQ等；不是详细MyLEAGUE内存枚举 [SRC-0030] |
| CURRENT_GEN_ANALOGUE | Xbox One版2K22玩家具体说明Gameplan→Defensive Settings选项；不提升为PC菜单截图 [SRC-0034] |
| KNOWN_IN_SERIES | 较早MyLEAGUE的Coach Gameplan、ACE/暂停菜单、Freelance经验 [SRC-0036/0037]；不证明PC22菜单完全相同 |
| UNKNOWN | PC22逐像素全页签、ACE精确模式/覆盖持久性、CRC真实分类成员、Playbook槽位对应3D战术调用概率等尚无完整认证 |

**研究、可观察、可用项目接口、能合法改变、产生实战效果，是不同证据轴。** 不把原生字节可写当作游戏已经按预期运行，也不把用户/教练Agent建议当作玩家批准。

## 1. 什么是真正的完整进攻系统：七层互相作用

1. **球员和阵容**：持球点、策应者、射手、挡拆顺下者、短顺下传球者与其可用性，这是打法的物理基础。
2. **教练体系与POE**：PreferredSystem是偏好，ActiveSystem是当前采用；POE包括进攻重点、耐心/速度倾向、进攻篮板/退防取舍。
3. **RunPlayTendency**：有多强的调用成套预设战术倾向；原生0–100并不等于每100回合必执行同数次完整战术。
4. **球队本名Playbook容器**：68个各有来源CRC的槽，意味着球队有哪些**候选动作**，不是球员触球次数。
5. **每个球员4个有序PlayTypes**：球员可被安排的战术**类型**，不是直接指定4个play CRC；本项目玩家认为前两项主要、后两项较少，不能量化概率。
6. **四个有序Freelance槽**：整体自由进攻阵型/空间配置，并非4名球员或4条具体战术；优先级次序保留，不假设等频。
7. **ACE、Play Initiator、Touches、Shot Tendencies、Play Discipline与临场叫战术**：影响由谁发起、是按设计跑还是自行创造、怎样终结；只能用真实比赛观测研究关系，不能假造单变量算法。

依赖链：**阵容角色 → 教练POE/体系 → Playbook内有合适的类型与动作吗 → Run Plays/ACE/球员四槽 → 实际出手、助攻、篮板、失误 → GM按动态数据复盘**。逻辑上如果某球员没有匹配类型/书中无对应动作，单纯调高Run Plays不会凭空生成战术。同版玩家曾发现SF没有合适战术，因为书内根本没有匹配其PlayType的动作 [SRC-0031]。

## 2. K04.COACH_GAMEPLAN — 已有19项默认设置怎么用于建队

项目手册登记19项COACH_DEFAULT，下表的数字是已知原生**枚举ID**，不是玩家应全队统一设置的目标。

| 原生字段 | 有来源的合法值/语义 | 经营用途和潜在代价 |
|---|---|---|
| POEOffense | 0无偏好；1 Get to Basket；2 Get Shooters Open；3 Feed Post；4 Pick and Roll Offense；5 Neutral；6 Run Through Scorer | 突破/外线/低位/挡拆/核心选择，须先看阵容与战术书 |
| POEOffense2 | 0无偏好；7 Patient；8 Neutral Tempo；9 Shoot at Will | 半场耐心组织与快速出手取舍；不是“第二得分手” |
| POEOffense3 | 0无偏好；10 Crash Offensive Boards；11 Neutral；12 Limit Transition | 拼二次进攻还是防对手快攻；不是“第三得分手” |
| POEDefense | 0无偏好；13 Protect Paint；14 Neutral；15 Limit Perimeter Shots | 限篮下或防外线，需看对手投篮结构 |
| POEDefense2 | 0无偏好；16 Conservative；17 Neutral；18 Physical | 侵略性/犯规/被突破风险；不能推导必然增加抢断 |
| POEDefense3 | 0无偏好；19 Crash Defensive Boards；20 Neutral；21 Run in Transition | 防守结束篮板与提速转换的取舍 |
| PreferredSystem / ActiveSystem | 0 Balanced；1 Grit and Grind；2 Pace and Space；3 Perimeter；4 Post；5 Triangle；6 Seven Seconds；7 Defense | 教练偏好与实际体系两套字段，不直接改球员体系熟练度 |
| PlaybookID | 原生真实book enum_id | **日常GM只读**，不能随意切其它队书；换帅后的恢复须另获授权 |
| BenchDepth | 原生整数；轮换人数上限 | 不按百分比、不把10人当最大上限；不再精确锁分钟 |
| RunPlayTendency | 0–100 | 设置调用战术倾向；不能等同绝对战术执行率 |
| ZoneUsage | 0–100 | 选择联防倾向，不能用单场数据保证联防收益 |
| BenchUtilization | 0–100 | 替补使用程度，和BenchDepth分开 |
| Tempo | 已有本机原始字段；确切UI含义、端点未知 | 不等于POEOffense2，也不等于SimPace；不要想象0–100就是已证端点 |
| HelpDefense | 0–100 | 帮助内线/弱侧补位与漏三分、协防轮转相权衡 |
| FreelanceType / Type2 / Type3 / Type4 | 已登记34种原生枚举raw 0..33 | 四槽保留原生顺序；本轮未核对每种动画、4槽实际使用率 |

**当前业务安全规则**：SimPace/SimPress/SimHelpDef/SimOffReb/SimDefReb是GM只读；默认不切PlaybookID；轮换分钟游戏AI会覆盖精细分钟控制，GM只使用人数上限与替补倾向等可靠杠杆。已部署原生写入范围/保存条件须以最新同批真实来源与DEV14已批准合同为准；本节不产生修改请求。

**实例**：球队拥有真正能创造挡拆优势的后卫、能顺下的内线与两名可靠射手时，POEOffense=4是一个合理**候选**；但还应先检查本队书是否有适配的FIST、球员类型、对手换防策略，不能只因这队有一个高评分PG就自动复制。若球队缺投射，换Pace and Space并不产生额外三分能力。

## 3. K04.PLAYBOOK — 本队专属Book容器与联盟共享战术池

本项目当前规则：球队持有本队同名**原生书容器**；一条具体战术CRC可以被多个球队各自引用。GM修改的是自己球队有限槽，不允许通过编辑B队原生book来实现A队战术变化。**休赛期每个赛季最多换帅一次**，换帅后如新教练携带原书，需另行批准把PlaybookID恢复本队书，再读新前值并分别批准改槽；仅研究不执行。

| 书区 | 原生容量 | 用法与界限 |
|---|---:|---|
| Regular | 30 | 常规set plays候选 |
| Bench | 20 | 替补相关战术槽，未证AI怎样触发 |
| Endgame | 10 | 末段候选，具体CPU调用时机待验 |
| Favorite | 8 | 快捷/偏好槽，不等于额外8条全新完整动作 |
| **总计** | **68** | 空位在各自分区计算，不能跨区借位 |

共享池是**历史已加载归档**：84本书、1,392条去重CRC，原始名称通过CRC与静态标签关联，其中一部分仅有名字、用途仍属NAME_INFERRED；**1,392条目前均未认证完整CRC→原生战术类别成员**。来源曾是旧归档，不代表现在每个队都装着同一book。GM可从池检索用途/球员角色适配，但**只能把有真实来源的CRC作为将来合法提案候选**，不能因FIST字样就臆测类别id。

**名称怎么读**：用户已经确认共享池真实的 '95 FIST 15 SIDE、CRC 0x79215B33，是挡拆家族，95年代标识、FIST挡拆、15涉及1号位发起与5号位掩护、SIDE侧翼路线。其他FIST 14 POP可依据字面先猜4号位外弹，但第一接球者、第二机会、实际最后投手要通过2D战术板或3D观测确认。**名字蕴含篮球语义，但不是不可反驳的原生type证据**。

NBA2K22同年MyNBA玩家说达拉斯名单缺适合Luka出任SF的行动时，增补Cutter、Mid及3PT类型play后观感改善 [SRC-0035]；这是**次世代社区个案**，不是官方万能配方。

## 4. K04.PLAY_CATEGORY — 玩家确认的12种动作分类

这些中文类别来自**PC22用户已在游戏UI中浏览的描述**，对应英文是通用NBA2K篮球术语，并不保证PC英文菜单逐字。它们不同于球员4个PlayTypes的raw id。

| # | 中文 / 英文参考 | 球员职责、为何需要 | 不适合/被克制 |
|---|---|---|---|
| 1 | 单打 Isolation | 清空一侧由高单打能力球员攻击错位 | 效率低、拖慢球权转移 |
| 2 | 挡拆 Pick & Roll | 持球+掩护人，寻顺下/突破/转移 | 防守换防和收缩会破坏初次机会 |
| 3 | 中投外弹 Pick & Fade Mid | 掩护者外弹至中投点接球 | 掩护者无中投或对手顺利换防 |
| 4 | 三分外弹 Pick & Fade 3PT | 会投三分的掩护者外弹至三分线 | 内线无射程反而降低空间 |
| 5 | 挡拆选项 P&R Option | 按防守决定顺下/外弹等分支 | 游戏具体分支规则与触发未知 |
| 6 | 低位背身 Post Up Low | 能背打或分球的内线低位接球 | 对手包夹、弱侧投射不佳 |
| 7 | 高位背身 Post Up High | 肘区传控/面框/中投核心 | 接应区域与节奏配合不到位 |
| 8 | 后卫背身 Guard Post Up | 大后卫打小后卫错位 | 缺身材优势、失去团队空间 |
| 9 | 中投 Mid Range | 绕掩护无球跑动，制造中距离 | 球员中投效率不足 |
| 10 | 三分 3PT | 让移动/定点射手获得三分接球机会 | 盲投、对手追防/换防 |
| 11 | 手递手 Handoff | 肘区或高位传球者递球+掩护 | 接手者、传球者职责不匹配 |
| 12 | 切入 Cutter | 无球从防线背后切篮下 | 对手拥堵禁区、缺接球发起人 |

**不要将12类play目录和球员play_type_names 0..15视为同一枚举**。一条CRC可能归多个战术类别，类型过滤的有效集合才是将来实机认证目标；没有该事实，只有NAME_INFERRED候选，不能悄悄填本机类型ID。

## 5. 球员PlayTypes、Play Discipline、Touches：缺席的第三球星为什么不参与？

本项目原生球员角色类型枚举：0 None；1 Isolation；2 Isolation Point；3 Isolation Wing；4 P&R Ball Handler；5 P&R Point；6 P&R Wing；7 P&R Roll Man；8 Post Up Low；9 Post Up High；10 Guard Post；11 Cutter；12 Handoff Receiver；13 Handoff Passer；14 Mid Range；15 3PT。

玩家说明每人四个类型槽，**前槽更优先**，后两槽较少调用但并非不可能；**一个PlayType不是一个具体战术CRC**。即使给球员设了P&R Ball Handler，也不意味着book中必有相容的FIST，更不意味着下一回合必为他叫战术。

2021年9月OS 2K22一手讨论特别有用：jimbo3772将Touches主要视为自由进攻/未跑预设时球权分配，认为真正叫谁的战术还取决于教练focus、球员能力、PlayTypes和Playbook；他报告曾找不到适合某SF的书内动作 [SRC-0031]。有人声称统一Touches或提高Play Discipline使球队分享球更好，也有人在10月反馈改Touches仍使教练仅为两名后卫叫战术、另有玩家反驳 [SRC-0031/0032]。**社区没有可信的固定数值—成功率公式**。

实务顺序：**先看Book类型与球员四槽相容性，再看教练RunPlayTendency、POE、Freelance及阵容实战表现**。不因讨论贴推荐Touches=50、Discipline=100就直接修改普通球员倾向或能力。球员Tendencies是否在项目允许修改的动作内须另过审批，研究不构成授权。

## 6. Freelance、ACE与自动叫战术：三个不同控制层

**Freelance**主要指自由进攻的站位/空间与球员间配合，并非严格固定路线play。项目已通过本机原生enum/同版PE字串匹配34类：包括FOUR_OUT、WARRIORS、JAZZ、PHILLY_ELBOW、TRIANGLE、PRINCESTON_CHIN、PACE、FLOW、SEVEN_SECONDS等，但**名字不等于本轮看过逐个实际跑位**。教练四槽同样有序，不能由位置1/2/3/4推算25%/25%/25%/25%。

**ACE = Adaptive Coaching Engine**。旧版开发人员材料称其依据对手、阵容和比赛时间动态调整战术计划 [SRC-0037]；2018–2020玩家对ACE是否会临时覆盖Gameplan、是否重复叫同一条play有**冲突说法** [SRC-0036]；2021年2K22 OS帖子也有玩家提到将ACE设成Defense Only后进攻更灵活，却没有对目标PC CPU vs CPU可靠控制实验 [SRC-0031]。因此：
- 默认教练字段反映**静态设置**；
- ACE/Offensive Playcalling/Defensive Playcalling是比赛运行时的**动态自动策略层**；
- 游戏引擎实际3D战术选择、球员是否执行到底是**结果层**。
静态字段写回成功不可当作3D打法已证明，玩家既有业务希望保留默认ACE，**本攻略不自动建议关闭ACE**。

更早MyLEAGUE玩家抱怨自己临场Freelance难以在下场保存，这只能启发我们区分“菜单可选 / 当前回合有效 / 下一场有效 / 保存后仍有效”，不能直接说PC22一定有一样的BUG。2K22 PS5玩家通过PlayVision=All Plays、Offense Playcalling=Auto显示更多战术移动，属于**次世代个人游戏设置体验** [SRC-0039]，不是当前终极联盟CPU模拟自动战术认证。

## 7. 防守：普通GM必须区分OVERALL、PERSONAL与ACE

**用户当前规则优先**：对方球队29支的默认整体防守可以只读采集，但日常GM**不再提出修改OVERALL_DEFENSE**；相反，为对方明确的具体进攻者用DEV14支持的PERSONAL_DEFENSE稀疏策略，有变化才提案。整体修改可能覆盖个人设置（玩家实机经验），所以不能在本项目继续沿用旧整体防守操作示例。个人目标须具备稳定native_player_id、defender_id与指定owner/opponent，未知就HOLD。

| 原生字段（共18项） | 球队经理可理解的用途与代价 |
|---|---|
| PressureOnball / PressureOffball | 持球/无球施压。对方射手需紧、对方切入快需考虑被反跑风险。注意压力不等于绕过掩护 |
| ForceDirection | 引导持球人方向，必须按本批raw字典选择 |
| ScreenDefenseOnBall / ScreenDefenseHedge | 后卫绕有球掩护/协防大个上提或沉退；过分上提易丢顺下 |
| OffballScreenDefense | 防无球绕掩护与空切，不等于有球Hedge |
| PostDefense | 低位前顶或从不同角度顶防，收益与犯规/篮板相关 |
| DoubleTeamPerimeter / DoubleTeamPost | 外线/背身包夹，考虑对手传球及弱侧射手 |
| ScreenDefenseOnBall5 / ScreenDefenseHedge5 | **两个独立字段**；当前PC中文标签、适用对象和与普通版的覆盖条件UNKNOWN，禁止凭“5”猜为“中锋开关” |
| SwitchRule | 换防允许范围；受阵容尺寸/错位/护筐制约 |
| OnballHelp / ScreenHelp | 持球帮助和掩护帮助，独立于Coach HelpDefense与Hedge |
| ExtendPressure | 扩张压迫意图，不能推定就是全场紧逼 |
| TagOnRoll | 顺下协防相关原生名与枚举已登记，**具体本机触发逻辑UNKNOWN** |
| StayAttached | 在掩护/弱侧场景保持盯防，效果受换防/协防协同影响 |
| PreRotate | 原生packed bool，只接受0或1，不是假想的AUTO/YES/NO三值 |

**有价值的2K22同代菜单纠错**：2021年10月Xbox One与Series X玩家报告GAMEPLAN→Defensive Settings可调整On-Ball/Off-Ball Pressure、On-Ball Screen、Hedge、Post、Stay Attached等；作者一度错误地把Go Over写在Pressure字段，其他人指出压力选项是Gap/Moderate/Tight/Smother，作者回帖纠正 [SRC-0034]。这意味着**不能把不同字段的枚举混用**，也不能直接把Xbox截图推成PC原版逐字UI。

**防守效果真实风险**：官方宣布2K22重做投篮干扰、封盖与轮转 [SRC-0030]；同年Operation Sports编辑撰文指出防守弱侧补位在某补丁后可能异常，一些Gameplan选项可能不像文字描述那样生效 [SRC-0033]。官方更新意图与玩家BUG观察可以同时成立。不要把某年补丁问题无限推广到当前项目exe，也不要把一次保存成功当作实战一定发生防守动作。

## 8. 让GM能做决定的三类场景与反证

| 动态现象 | 优先确认的事实 | 可讨论的机制调整 | 什么情况下要HOLD |
|---|---|---|---|
| 核心单打频繁、其他人几乎没出手 | 比赛场次、出场分钟、Book类型/球员PlayTypes、实际核心可用性 | 增补有证据的3PT/Cutter/Handoff play、比较POE与RunPlays | 数据只有单场胜负，缺Book/人员真实来源 |
| 3PA不足而球队有优秀射手 | 真实3PA/FGA、射手上场与接球/无球角色 | Get Shooters Open、三分战术、空间Freelance候选 | 球员无射程，不能用菜单替球员增加能力 |
| 对手挡拆持球者反复杀到篮下 | 对手主攻者和掩护者、球队犯规、防守篮板/侧翼空间 | 指定对手球员Personal Screen/Hedge/Help，明确弱侧代价 | 个人matchup身份/合法enum不存在时不生成整体替代动作 |
| 对手低位得分高而外线弱 | 低位触球/罚球/外线投篮、内线犯规负荷 | 个人低位防守、定向包夹、POE护筐分析 | 不能仅凭对手PTS就假设全由Post产生 |

每次方案至少注明：save/career、最新数据批次、球队/对手/当前教练/本队Book、真正字段和枚举、当前值、期望值、依据、代价、结果观察指标与审批状态。**分析未验证读数时保留UNKNOWN；GM不造比赛数据、不随意修改球员属性。**

## 9. 多智能体权限（DEV29 V3）

教练Agent可以坚持自己的体系、拒绝GM的打法提议或主动请求特定类型球员；GM可以协商/提出经批准的团队配置；球员Agent会对触球/角色变化产生态度；媒体Agent可以质疑球队战术效果。但以上人格和态度如果并非游戏原生可读取，只能在外挂另存**角色意图/模拟事件**，不能直接伪装成NBA2K22的真实倾向、化学反应或比赛数据。教练/球员双方同意，也**不代替真实玩家授权游戏写入**。

## 10. R02-A已交付、未证事项与R02-B断点

**本轮交付**：Project-native能力与政策基线；Coach19和PERSONAL18的篮球含义、约束；12战术类别完整使用说明；book68槽与共享池1,392项历史来源边界；原生四PlayTypes和四Freelance区别；ACE/Play Discipline/Touches/Run Plays行为层分析；真实2K22玩家矛盾报告及2K官方防守信息；GM从动态数据提出可检验方案的模板。

**R02-B优先要补的具体事实**：
1. NBA2K22 **PC本世代原版**Coach Gameplan与暂停菜单、ACE/Offensive Settings/Defensive Settings的具体页签、按钮与完整合法值域，其他平台严格标同代或系列；
2. ACE与Freelance如何覆盖临场叫战术，四个Freelance原生槽如何映射实际站位；旧版菜单BUG不能擅自外推；
3. 12类具体play CRC→类别ID、2D动态board和球员PlayTypes的匹配依据；目前仍是显式UNKNOWN；
4. Personal18中OnBall5/Hedge5/TagOnRoll/StayAttached/PreRotate的原版UI与相互覆盖；战术效果需与AI是否自动覆盖分开；
5. 真实进攻/防守对手策略和阵容变化关联的可观测指标，不能编造调用率。

**恢复方式**：先读本K04、[PROGRESS](../PROGRESS.md)和SRC-0030..39，从R02-B继续研究，不重新开始R01或重新定义现有DEV14/Playbook共享池。R02尚未整体COMPLETE；本轮没有修改游戏、项目执行程序或球员能力。


---

# DEV29 R02-B — ACE/Series/Freelance动态覆盖、挡拆个人防守语义、PC同代研究与多角色权限（2026-10-21）

> **研究性质**：R02-B实际文献研究已完成；继续维护R02领域的PC22未认证原生UI缺口，不因为旧版本的论坛解释直接写入游戏原生事实。第一手新增来源SRC-0040..0047，相关候选/排除图证登记于EXTERNAL_VISUALS。没有游戏读写或真实比赛实验。凡未获得原版PC22无遮挡可读截图、视频确切帧，`PC22_UI_CONFIRMED`不得升级。

## 11. K04.ACE_PRIORITY — 2022年同版本玩家发现“ACE关掉也不一定保留Custom”

2022-01-02 Operation Sports `Defensive Settings Not Staying On Custom` [SRC-0040] 中，玩家报告比赛中Team Focus/Defensive Settings从Custom恢复Automatic；其他玩家首先建议将ACE设为Off或Offense Only，**报告者反馈试过仍无效**。这条证据严格表述为：`2K22_GAME_USER_REPORTED_DYNAMIC_OVERRIDE`，作者平台和模式未核实为PC MyLEAGUE；部分原帖直接页面访问重定向失败，但搜索索引保留原作者回复；不是对当前PC版本“ACE失效”的结论。

2022-02 OS `Adaptive Coaching Engine` [SRC-0041]，玩家DJ81给出**不同的控制策略**：认为关闭ACE能够让手动叫战术持久，但要在比赛中自行调整tempo、篮板、对位和攻防策略；他还表示“ACE only affects the user”。这一条是**个人体验/主张**，未隔离CPU-vs-CPU，也未提供2K22 PC源代码级控制合同。两文并列，不能选较符合自己预期的一条作为官方真相。

**实际GM/Coach应分开验证的4个层**：

| 层级 | 研究对象 | 最低可观察信号 | 不可直接推断 |
|---|---|---|---|
| G0 | 赛前静态Coach Default/POE/四Freelance | 当前原生字段和字典来源、读数时间 | 不代表3D场上已执行 |
| G1 | 比赛入口Gameplan与本场ACE/Auto/Manual状态 | `screen_scope=pre_game`、选中team/opponent、真实显示值 | 不代表跨暂停和下一场一直保存 |
| G2 | Timeout/暂停后临场策略 | 本次菜单对比、是否被重置/重算 | 不代表所有比赛模式都被同一ACE机制覆盖 |
| G3 | 3D实际进攻/防守序列与比赛结果 | 谁发起、什么掩护、是否进入Freelance/Series、Box差异 | 不代表由单一设置造成；不承诺固定胜率提升 |

当前项目`coach.Tempo`源字段存在，但其UI语义尚未证明；**不要用一个名叫Tempo的原生字节证明ACE临场节奏已被GM控制**。未来专门取证`ACE_MODE / OFFENSE_PLAYCALLING_MODE / DEFENSE_PLAYCALLING_MODE / PREGAME_PERSISTENCE / TIMEOUT_OVERRIDE`，每个分别标读取来源与游戏模式，禁止将用户按键或2K MyTeam路径偷换为30队CPU自动比赛接口。

**权利含义（V3）**：教练Agent可以有“比赛中保留自主ACE适应”或“执行GM批准的固定Gameplan”的不同偏好；GM可争论，但教练意志为**外挂角色状态**，不能假装游戏ACE具备真实“同意/拒绝”接口。真实玩家批准仅为发生原生游戏写入的门槛，R02文献研究没有授予任何新写入权限。

## 12. K04.SERIES_VS_FREELANCE — 有设置Series，不等于场上跑出了Series

**两个概念**：`Playbook`保存可选的具体play；`Series`是比赛中以连续动作组织的进攻选项/次级入口；`Freelance`则是自由进攻空间和自发动作体系。社区使用词汇可能重叠，所以必须以观察到的**菜单来源、实际选中名称和场上行为**而非译名判别，不能把本队4槽Freelance当成Series或Book Favorite8。

- 2021-09-16（2K22发布早期），Operation Sports玩家`Smirkin Dirk`表示，在Gameplan选择Series以及比赛Timeout选Series后，都似乎退回Freelance [SRC-0042]。该帖附玩家签名`2022 ... (XBX)`，**不能直接认证其原版PC22**。原帖标题`Are series not working?`，是一例一手故障报告，不是2K22所有Series不生效的定论。
- 2021-10-07 Reddit `r/MyTeam`玩家给出**Xbox Series X|S/MyTEAM**的双重操作路径：暂停`Offensive Settings`先选Freelance，再场上右方向键`Gameplan→Run Freelance`，之后右方向键`Freelance→指定set` [SRC-0043]。这特别说明**“配置可选择”与“场上活动set被调用”是两步**；但它只适用于作者的MyTEAM次世代，PC22离线MyLEAGUE是否具有同菜单和自动执行，仍`UNKNOWN`。
- 在2K21**次世代MyNBA**的OS讨论 [SRC-0047] 中，玩家把`Offensive Settings`里的Freelance与Series、暂停临场菜单、默认战术重置分为不同问题，并报告只能暂停时切Freelance；这是**旧版本、不同平台**的菜单经验，不证明PC22能够从相同入口切换，也不能把项目4个原生Freelance槽等同临场Series。

**研究与GM实务上的诊断顺序**：先确认队伍Book中有对应脚本/Series参考 → 确认教练进攻重点/RunPlays/ACE是否相容 → 区分“被选中”的静态菜单与“已激活”的临场流程 → 在可观察比赛回合查本场跑位。无法看到3D时只保留`CALLABLE_NOT_EXECUTION_CONFIRMED`。不允许以“战术名称在Book”反推CPU必选，更不允许凭玩家按键指南虚构外挂可以实时按键。

## 13. K04.DEFENSE_SCREEN5 — 对Center后缀和TagOnRoll的更精确理解

### 13.1 拆成三人视角而非按中文直觉填数值

在篮球挡拆场景，要明确**对方持球者B、发起掩护的球员S、我方防持球者DB与防掩护者DS**。`ScreenDefenseOnBall`首先是对DB应怎样绕掩护的策略；`ScreenDefenseHedge`是DS怎样延误/上提/回收的策略。这个“分别指谁”的职责框架是篮球战术概念，而非本机引擎动作保证。

2016年OS历史2K系列讨论 [SRC-0044]给出进一步的场景解释：
- 某回帖认为`On-Ball Screen (Center)`、`Hedge (Center)`针对**中锋作为掩护者的挡拆**单独配置，和普通On-Ball Screen/Hedge可并存；选`Auto`时可能回落普通方案。
- 另一个回帖强调，中锋掩护通常意味着由**我方防中锋者DS**参与Hedge，讨论的视角不应误判为“该选项写在谁的名字下面，就要哪个人亲自做Hedge”。
- 本轮另核对2018年OS经验 [SRC-0045]：作者明确从“**我方Center是Hedge defender**”的视角理解两个Center选项。这与“对方Center是screener”在一般位置对位时常重合，但发生换防、错位、非传统五号位等情景，**两个身份不保证相同**。

**最终严格结论**：`KNOWN_IN_SERIES`可以说Center后缀与挡拆中锋参与有关，旧玩家提供了有效的篮筐防守语义示例；然而**NBA2K22 PC精确触发条件、是否按本队中锋身份或对手掩护人的名单位置判定、与普通项override优先级仍是UNKNOWN**。项目中`ScreenDefenseOnBall5/ScreenDefenseHedge5`两个独立原生字段仍需要由PC22可读UI/特定对位事实对应，**本轮没有将名字推断写入原生字典**。

### 13.2 TagOnRoll存在“游戏字段还在，但菜单位置可能变化”的旧系列先例

2018-11 OS `Defensive Settings Discussion` [SRC-0045] 的玩家说，旧版`Tag On Roll`当时似乎**从赛前Gameplan消失，却还出现在SimCast的Defensive Settings页**；作者明确承认没有验证在SimCast改变后的实际效果。这个案例在研究层重要：**“某一菜单没有这个选项”不等于“功能/存档对象/所有模式都不存在”**，也不能把隐藏页当成可稳定控制的CPU策略。

本项目`TagOnRoll`原生枚举字典已登记，但具体UI和引擎行为还需PC22认证；不可直接从2018经验推导为PC22依然在SimCast里、必能影响挡拆顺下。

### 13.3 PreRotate、StayAttached与弱侧救援仍不可混同

2018年同帖玩家以`Pre-Rotate`为例讨论对突破持球者的提前轮转，也提到`Stay Attached`与Hedge/Screen Help的联动；同一主题里另有玩家警告强行帮助可能造成另一侧开放的投篮 [SRC-0045]。**这是老游戏战术经验，不是PC22内核触发公式**。项目中的`PreRotate`只接受packed bool`0/1`；`StayAttached`和`TagOnRoll`各有独立字典/身份，不能互当别名；临场ACE可能介入但覆盖规则未证。

## 14. 本世代PC22“CPU对CPU”研究对象与“用户手控ACE”要分开

2021-11 Operation Sports的 **NBA 2K PC Forum** 中，玩家`cdcool`直接描述`NBA 2K22 CPU vs CPU MyLeague`，控制全部球队并**逐场观看每一场、不使用Sim**，其自定义游戏速度、游戏玩法滑块列表明确是供该玩法使用 [SRC-0046]。这证明同版本PC拥有可靠的玩家研究对象——“观战的CPU vs CPU MyLEAGUE”——其条件明显不同于：
- 真人打CPU时`ACE affects USER`一类建议；
- 快速`Sim`不进入全场3D的比赛；
- MyCareer / MyTEAM的临场按键；
- PS5 `MyNBA`新世代教练与场景。

这条资料**不是**PC22 Coach UI截图，也不证明特定全联盟战术偏好的效果；其严肃用途是要求未来每个所谓“战术有效”的来源都标：`render_mode=CPU_VS_CPU_3D / PLAYER_VS_CPU / FAST_SIM`、`save_type=MYLEAGUE`、`actor_who_controls_team`。不再把模拟成绩和真人手动防守混成同一个证据样本。

## 15. R02-B真实画面/数据的最低验收与现存结果

| 具体研究题 | 新证据最高等级 | PC22直接截图/真实字段 | 后续原生定向 |
|---|---|---|---|
| Coach Gameplan、POE、Offensive/Defensive Settings全部选项 | `PROJECT_NATIVE_FIELDS_VERIFIED` + 同版社区文字 | **未取得完整原版可读页面** | `VIS-TODO-R02-01/04/05`，UI字段逐项与本批字典映射 |
| ACE关闭、Offense Only和Manual时策略是否持久 | `NBA2K22_COMMUNITY_REPORTED_CONFLICTING` | **未证具体PC22 CPU-vs-CPU覆盖规则** | G0–G3分层、同一队前后值、比赛模式与暂停时点 |
| Series是否可替代Freelance/被自动调用 | `NBA2K22_COMMUNITY_REPORTED_XBX` | **未证PC场上实际Series启用** | 查入口/候选/选择/3D调用各不同对象 |
| 34个Freelance四槽、切换机制和场上站位 | `PC22_PROJECT_NATIVE_ENUM` + 次世代MyTEAM操作类比 | **CRC标签已映射，不等于原版菜单或动画已见** | `VIS-TODO-R02-04`，不要虚构等频率 |
| 12类Play目录、球员四PlayTypes与2D Playboard | `PLAYER_REPORTED_UI` + 共享池已有CRC | **CRC→原生类别id仍UNKNOWN** | `VIS-TODO-R02-02/03`与未来定向映射 |
| Personal 18项中Center/Tag/PreRotate等语义 | `KNOWN_IN_SERIES` + PC22本机字段存在 | **精确触发/覆盖/中文菜单未确认** | `VIS-TODO-R02-05`，特别核对身份与优先级 |

**新增合格PC22逐像素Coach/Playbook菜单图证：0**。搜到带NBA2K22标题的视频或网页不等于视频已逐帧审查。现有网站图片和YouTube只记录原网页/媒体定位，不复制到GitHub、不假造时间戳；图证待办集中在EXTERNAL_VISUALS。

## 16. DEV29 V3四角色权限、信息与“同意≠写入”矩阵

| 机制/争议 | Coach自主可选什么 | GM能提出什么 | Player能提出/拒绝什么 | Media可知/不可知 | 反馈与持久化分界 |
|---|---|---|---|---|---|
| 本队进攻节奏与体系 | 偏爱耐心阵地或转换、在球员不合适时拒绝GM强制策略 | 寻找更合适阵容、商议POE/Book/员工 | 反映职责不适、争取高持球与自主训练 | 可据真实进攻数据质疑；不能看到内部未来潜力或私下谈判 | 比赛PTS/Pace等是原生观察；教练理念争执是外挂`EXTERNAL_SQLITE_CANONICAL` |
| 巨星要改变战术角色 | 选择战术发起人和场上打法倾向，保留教练审慎判断 | 提供换阵、续约/资产与教练调整方案 | 提出更多单打、减少掩护或拒绝成为纯外线定点 | 可报道公开诉求但应区分传闻与官方公告 | 球员原生PlayTypes可读作事实；内心愿望/承诺另存角色事件 |
| ACE动态覆盖了Gameplan | 认为场上变化值得自主调整，或坚持预先商定方案 | 质询当前读值/实际比赛表现并请求赛前或赛中策略方案 | 表示对打法/上场机会满意与否 | 只能根据可观察比赛表现推断，不能声称看到隐藏开关 | `G0–G3`证据链；无实机读数时HOLD |
| 指定防守一名强攻手 | 根据己方防守资源和对方空间建议换防/不包夹 | 请求指定对手的PERSONAL防守，不动OVERALL | 防守者可能不愿长期冒犯规风险或受疲劳影响 | 以对手真实命中率和失误做报道，勿推断精确防守指令 | 实机值需批准；策略偏好/风险承受度可外挂存储 |

**WHO_CAN_OBSERVE**必须按角色可见性投影，GM与媒体不应共享球员完整隐私信念；`WHO_CAN_PROPOSE/WHO_MAY_VETO`描述角色模拟谈判层；`GAME_NATIVE_EFFECT`和`EXTERNAL_ROLE_EFFECT`分开；`LEARNING_SIGNAL`只能由真实比赛、已批准动作及角色事件推动；`ATTRIBUTE_REPURPOSE_CANDIDATE=UNKNOWN`，不得把Tempo、PlayTypes、Tendencies占作人格存储位；**战术理念是参考，不是统一最优模板**。

独立教练Agent可能提出一套不利于球队短期胜率的打法，这在篮球世界里可以存在；GM可以谈判、拒绝或换帅，球员可以接受/拒绝其角色，但**上述只是未来角色可选行动目录，不是本轮开发Agent或真实2K原生对象的审批权**。所有游戏修改仍需真实玩家按现有合法执行合同批准。

## 17. R02-B交付总结与下一研究断点

本轮真正推进了：
1. ACE/Offensive/Defensive Playcalling**“用户手动调”与“CPU-vs-CPU”两套情形不能混用**；2022年直接互相矛盾的玩家案例，不承诺ACE关掉就一定保留设置；
2. 2K22 **Series选择可能回退Freelance** 的一手玩家报告及同年Xbox MyTEAM的分步启用方法；界面选择和真实调用独立；
3. Center掩护防守与`Hedge`人员职责拆解、`TagOnRoll`2018年在SimCast与赛前菜单可见性差异，避免误解原生字段；
4. 2021 NBA2K22 PC端**CPU-vs-CPU MyLEAGUE逐场观战**的明确作者证据，帮助过滤不具可比性的战术经验；
5. 依据V3为Coach、GM、Player、Media补全**四角色观察/提议/否决/学习与外部持久化**矩阵。

**未解决**：PC22原版Coach/ACE/Personal/Freelance与2D预览可读图，战术CRC类别精确ID，ACE下本队四Freelance实际使用概率，Series游戏内执行，Center与TagOnRoll动态覆盖规则。全部`UNKNOWN`或`DEV28_NATIVE_DISCOVERY_REQUIRED`，**不能通过搜索更多2K16–19战术帖子无限外推**。

**下一阶段建议：`R02_C_BOUNDED_ORIGINAL_UI_OR_CLOSE`**。如果玩家下一轮继续R02，应限定一次原版PC22教练/攻防菜单视觉取证，有效证据即增量K04；若仍没有可靠原版画面，则按UNKNOWN封存R02公开研究，转R03训练/疲劳/伤病，不因此启动DEV28或Codex。研究结束只按GitHub PROGRESS推进，不自动做任何游戏写入。

---

# DEV29 R02-C — 原版PC22菜单有界补证、角色能力原料目录与R02结案（2026-10-21）

> **最终公开研究状态：`R02_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。** 本轮依照R02-B停止规则集中查找原版NBA2K22 PC本世代MyLEAGUE Coach Gameplan、ACE、Playbook、Freelance、个人防守和2D战术板视觉证据，未取得**同时具备原版PC、离线MyLEAGUE、完整目标UI可读、真实来源可复核**的菜单画面。研究结案不等于游戏功能已完成原生取证或开发。本轮新资料只保留有直接新增事实的[SRC-0048](../SOURCES.md)：同版MyLEAGUE球员报告比赛中修改Freelance可按本队保存；这属于玩家报告，平台未知且没有截图。

## 18. 目标UI最后一轮认证矩阵

| 对象/目标页 | 现有最强证据 | 本轮新增PC22完整可读原版UI | 需要定向只读验收什么 |
|---|---|---|---|
| Coach Gameplan：六POE、BenchDepth、RunPlays、Zone、HelpDefense、体系 | **本项目原生字段/部分隔离局写回回读证据**；旧平台菜单有类比 | **0张** | 原版PC22赛前Coaching栏目、完整页签/筛选/菜单选项，逐字段和同批原生字典比对 |
| ACE / Offensive/Defensive Playcalling / Timeout | **同版社区有互相冲突的自动重置经验** | **0张** | 静态Coach值与赛中ACE/暂停后策略分开取证；真实CPU-vs-CPU是否触发不能凭菜单确认 |
| 四个Freelance与Series选定/执行 | **本项目34项native枚举；玩家说四槽有顺序；同年玩家见到Series回到Freelance** | **0张** | 阵型菜单、选中与实际激活路径、同队/跨场保存、原生四槽与现场覆盖的关系 |
| Book区域、12类选择、战术2D预览 | **已有CRC、68个Book槽及用户界面口述类别** | **0张** | Book真实分类筛选→CRC对应；截1个动作完整名称/棋盘预览即可起步 |
| 指定球员PERSONAL防守18项及Center/Tag/PreRotate | **本项目原生字段/部分UI配对；其它版本玩家打法解释** | **0张** | 选定对手及个人ID的防守页与OnBall5/Hedge5/Tag/Stay原始标签；OVERALL只读 |

视觉资料审查见[VIS索引](../visuals/EXTERNAL_VISUALS.md)，不把封面、Steam外层View Stats、模组PC MyNBA、2K22次世代MyNBA教练图或MyTEAM临场手柄提示当作PC22原版MyLEAGUE认证。所有字段如果只有原生字典无UI，继续保留`PC22_UI_UNKNOWN`与`PROJECT_NATIVE_KNOWN`**双重事实**，而不是把全机制降级为不存在。

### 18.1 两个容易误采信的结果

- **2021-10至12月同版MyLEAGUE Freelance保存经验**：[SRC-0048] Reddit帖子中提问者先抱怨必须每场重配默认Freelance，后来回答“在比赛中改动后会为该队自动保存”。这至少说明玩家报告**存在另一种保存路径**，可用来挑战“2K22无论如何都不保存”断言；没有平台、完整操作帧、外层save身份与跨赛季测试，不能写成`PC22_NATIVE_PERSISTENCE_VERIFIED`。它还说明教练可能面对**临场Gameplan的不同优先权来源**，不是非得每队同一动作。
- **网页时间矛盾需排除**：[Magic Game World：How to Adjust Player Minutes in NBA 2K22 MyLeague Season Mode](https://www.magicgameworld.com/how-to-adjust-player-minutes-in-season-mode-in-nba-2k22-myleague/)显示发文`2021-04-30`，**早于2K22在2021-09-10发售**，同时未经验证地声称调整分钟并关闭自动调整即可锁定整个赛季；本项目玩家已经报告AI会重新分配分钟，且不再追求分钟锁定。本轮**不将该文章注册为可信来源，不据此产生任何动作能力**。类似不合理日期的“玩法攻略”不能凭标题作为图证。
- 2K22官方MyNBA`Conditional Coaching`属于**PS5/Xbox Series平台的专有新增功能**（既有SRC-0026、官方MyNBA报告），应作为系列架构参考/未来教练能力启发，**不得声称PC本世代MyLEAGUE内置同名条件规则执行器**；不要悄悄用它替代外部教练自主决策。

## 19. R02研究真正交给四类角色的原料：事实、选择空间、反馈，而不是处方

已发表K04前面各节解释篮球用途；**下面不是推荐每个角色怎么决定，而是告诉他哪些选择可提出、哪些动作当前游戏接口可承载、怎样知道决策发生了什么**。存档事实与角色思想必须分层，未知原生取证不能为了“涌现”补成虚假动态数据。

| 研究原料/对象 | 原生事实与动态信息（能观察到什么） | 可供角色考虑的非穷尽选择 | 谁能提出/拒绝 | 反馈与边界 |
|---|---|---|---|---|
| Coach偏好体系/实际体系 | `PreferredSystem`、`ActiveSystem`本机枚举0..7；真实教练身份、球队阵容需要最新批次 | 沿用理念、逐步改革、要求阵容补强、接受GM提议或坚持反对 | Coach表达个人偏好；GM提出协商、换帅；Player表达适配意见 | 教练心理偏好、承诺是**外部模拟**；体系raw不是角色人格或能力增减 |
| POE六项/进攻纪律 | Coach默认字段、RunPlayTendency等可按同批原生源读取；ACE临场状态另属UNKNOWN | 自由进攻、加强预设、保护转换、改变主攻方向，或决定本回合不改变 | Coach策略建议；GM可提议；Player可表达角色不满 | 实际赛中调用率/比赛效率仍待真实数据；**不设统一胜率最优阈值** |
| 本队Book/共享战术池 | Book 68槽/四区、同批原生CRC；既有池1,392条为历史归档，不一定代表现在全部可用；12类CRC关系UNKNOWN | 在本队书保持、增加或替换合法CRC，选择打法或拒绝动作 | Coach主张动作搭配，GM讨论人员/书；Player对自身角色有立场 | 只有玩家另行批准且具备最新同批可执行来源才可能原生写入 |
| 四个球员PlayTypes/触球与纪律 | PlayTypes四槽有序/原生0..15；Touches与PlayDiscipline需独立来源和许可，不视为“可自由调节人格” | 请求增加持球、改打无球、拒绝被安排在不愿的位置、教练主动使用不同球员 | Player可提出和拒绝；Coach/GM可接受或另拟，发生真实修改还需用户批准 | 普通GM不能通过改Overall/Potential/Badge来实现角色理念；现实原生触球反馈≠人格真值 |
| 四Freelance/ACE/Series | Freelance四槽有序与34已知名称；ACE覆盖、Series现场与保存仍UNKNOWN | 更偏向运动进攻、空间、三角/高位策应；保留ACE自动调度或希望固定方案 | Coach可偏好临场调整；GM/Player可以质疑和商量 | 演示棋盘和CPU实际打法不同；SRC-0048只证明有人报告按队保存 |
| 按对手PERSONAL防守 | 18字段已在本机字典；真正球员对位/防守人标识必须源可查 | 单防、包夹、换防/过掩护、护禁区与顾外线等相互有代价的选项 | Coach选择、GM建议，防守者可表达负荷/风险诉求 | 普通GM **OVERALL只读**、PERSONAL稀疏改动需授权；效果因对手比赛策略和ACE变化 |
| 比赛/历史动态反馈 | R01真实Box/Game Logs与历史保留窗口**尚有PC22 UI缺口**；只有真正入库事实可供角色判断 | 根据新比赛反思、更换偏好、坚持、接受责任，甚至形成错误见解 | 所有角色可形成独立判断；Media只报道可见事实和标明传闻 | **不能在没有GameID/Box数据时生成“实际战术成功率”**，不能让媒体读取其他角色私有动机 |

**特别区分四层状态**：`GAME_NATIVE_OBSERVED`（游戏事实，附版本/时间/对象）→ `ROLE_BELIEF_PRIVATE`（角色对事实的主观看法）→ `ROLE_INTENT_AND_NEGOTIATION`（选择、承诺、拒绝）→ `APPROVED_NATIVE_ACTION_AND_RESULT`（玩家批准后合法执行且读回）。不会把角色想法当真实比赛记录，也不会让模型在建立长期记忆时擅占Native Tempo/Touches/Loyalty等仍参与引擎的字段。

### 19.1 只定义可选范围与冲突，不植入统一最优答案

每个角色可以选择`HOLD`、`PROPOSE`、`COUNTER`、`REJECT`、`WITHDRAW`、`REQUEST_MORE_DATA`、`ACCEPT_RISK`等**外部角色决策标签**，这些仅是将来人格化系统的**候选行为词汇，不是本轮新增游戏原生命令、审批或Agent实现**。角色的个人目标、风险厌恶程度与信息可见性将影响其选择；研究层不能强制“最后一定达成战术共识”。GM可以错误地低估教练、教练可以坚持失败的策略、球员可以对球队胜率不利但符合自身目标地拒绝改打法、媒体也可能猜错原因——只要外部世界事实与传闻保持可区分。

**合同和权限的硬边界不能由模型自由消解**：合同到期/交易合法性/真实球员对象ID/球队手册独占写入约束由已授权执行系统验证，真实玩家始终控制游戏原生修改；该自由选择的层面不包括直接编辑普通球员能力、潜力或徽章。

## 20. 后续DEV28/Antigravity待证输入（不是立即启动任务）

按信息增量排序、最多两组有价值画面，而不是向用户索求整个游戏：

1. **Coach配置和动态冲突（A组）**：原版PC22离线MyLEAGUE的Coach Gameplan页（显示POE、四Freelance/RunPlays任选有清楚字段的页）和同队比赛内的ACE/Offensive Settings各1张。为每张标保存方式、游戏日期、球队/对手、是否模组、时间点、完整按钮提示，不能因“同名”认为一页覆盖另一页。
2. **战术候选与对手防守（B组）**：本队Book编辑/12类筛选及1条play的2D路线；另选对手一个球员的PERSONAL防守页，优先能看到`ScreenDefenseOnBall5/Hedge5/TagOnRoll/PreRotate`真实菜单标签。可从最容易看到的两页先做，不需要把所有1,392个CRC都截图。**无需把USER操作当CPU战术已执行**。
3. 若有机会上线更完整只读数据，独立采`coach_pre_game_state`、`coach_timeout_state`、`game_id`、`observed_ai_call`和`actor_visibility`，只在实际观察到后提升到`PROJECT_CAPTURED`、`GM_QUERYABLE`；本轮没有运行这些操作。
4. 任何只读菜单或内存调查必须是未来另有权限的DEV28/Antigravity流程。R02公开研究不因截图缺失反复延期；未来获得真实PC22素材只**增量更新**K04、SOURCES、VIS和原生映射，不重新展开R02-A/B/C。

## 21. R02研究结案和V3下一轮入口

**R02-A/B/C总体：`R02_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`，研究功能领域已按来源、操作、联动、风险与自主角色权限交付，原版PC22的完整Coach UI与运行时效果仍`UNKNOWN`。** 本次未找到满足认证条件的新目标画面，未上报假视频帧/模组图/猜测类别。项目已知的19 Coach、18项对手防守、34Freelance和68槽Book保留其既有来源等级；战术CRC类别精确映射和ACE/Series实际使用仍需未来单独认证。

**下轮按V3直接启动R03（K06训练/健康/成长）**，优先研究：球队训练计划与个人训练focus、休息/强度/疲劳、伤病和部位Durability、自然能力成长与退化、员工与医疗，比赛/模拟对不同机制是否有差异；从`NBA2K22 PC MyLEAGUE`出发，旧版本/次世代MyNBA明确分级。要交付的是**训练操作选择全集、状态/刷新时间、身体健康与球员拒绝训练的外部角色映射**，不替角色制定永远一致的最优训练方案。R03研究共性训练健康机制，**不会代替R04完整球员档案、全部伤病耐久字段、人格徽章和合同偏好研究**。

R03从GitHub读取[PROGRESS](../PROGRESS.md)、V3、R04专项目录、K04已知Coach/训练联动与本项目训练相关既有开发/操作文档，直接创建或补充`guides/K06_TRAINING_HEALTH_GROWTH.md`。下一轮同样提交GitHub与来源图证回读。**不启动Codex/DEV28或任何游戏存档读写。**

## 22. PC22原生轮换分钟调用链（2026-10-28工程增量）

来源：本任务固定PC22二进制的静态指令与虚函数槽位证据，见[调用合同](../../../research/rea_native_control/ROTATION_MINUTES_CONTRACT.md)及[SOURCES登记](../SOURCES.md#2026-10-28-native轮换分钟工程静态来源)。它是历史研究之后的独立工程增量，未重新启动R02，也没有新增游戏实测。

- 轮换左右按钮读取球员当前分配分钟，传入明确的新值；已恢复UI范围为整数0..48。原生七位编码可表示更大值，不能据此扩展角色可选值。
- 通用Native Setter仅设置该球员的分配分钟；球队变更路径的固定参数为kind1、flag0。执行器不选择分钟、不自动分配全队240分钟，也不将Player人格请求自动提升为Coach执行权限。
- 另一MyCareer分支可能根据生涯限制截断输入，已从本接口排除。当前delegate方法指针必须匹配已恢复的通用路径，未知模式在设置前停止。
- 调用链、参数和离线模拟已形成工程证据；当前存档身份、原版菜单显示、后续模拟/AI覆盖、独立读回与Save/Reload仍待各自真实验证。仅有分钟Setter不能把首发、轮换顺序、角色、伤病替补或全Coach功能标成完成。
