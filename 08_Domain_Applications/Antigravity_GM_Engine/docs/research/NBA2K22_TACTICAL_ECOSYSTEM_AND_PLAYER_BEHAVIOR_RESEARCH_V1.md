# NBA2K22 战术生态与球员行为引擎 — 研究基础 V1

- 日期：2026-10-19；Research owner：Web Development / Web GM research。
- 目标：理解并实际运用 NBA2K22 中 **教练能力、教练偏好/球队实际体系、体系适配、战术手册内部战术、四个球员Play Type槽位、比赛内外战术调用、球员行为Tendencies、55项球员能力、个人防守对手设置、整体攻防方案、自然成长**之间的联系，从球员/球队观测解释战术短板，再给GM V4形成内部改善/招募/交易/教练变更的比较。
- 此工作是M系列完成后优先补充的知识研究与Codex实施交接，**不是已经实施的代码或当前能力授权**。赛场原版ACE全程ON；不开发外挂实时观看比赛模型、不反编ACE核心算法、不要求锁定个人分钟。赛场Gameplay世界级滑块由独立WORLD/Court Profile管理，不被单队GM以改难度的方式用于提高战力。
- 玩家本轮**新授权**：允许GM提出并在玩家批准后、由Codex正式执行**球员个人Tendencies的战术适配修改**，使球员更好融入球队体系。**仍然禁止普通GM直接修改任何球员的原始能力值、潜力、身高、速度、徽章等；历史年代重力仍是单独审批通道。** 四个个人战术类型槽位的配置也是战术输入，应分开标识，不与改属性混合。
- 证据标签：PROJECT_VERIFIED=已验收仓库原生接口；PLAYER_CONFIRMED=当前玩家在游戏中亲眼确认的操作/行为；2K22_COMMUNITY=可回溯2K22实际玩家反馈；SERIES_BACKGROUND=其它年份基础原理/菜单；NBA_REAL=现实篮球事实；HYPOTHESIS=需用当前PC版本数据确认的交互规律。社区声称修好某问题≠已证明引擎内部参数公式。

## 1. 战术因果链（重点：依赖关系与因果边界）

球队建队哲学/可用球员能力 + 合同预算 + 对手弱点
   → 选择主教练（教练属性/适配评级，实际影响路径待证）
   → 选择球队当前体系ActiveSystem/PreferredSystem、对应Freelance空间/无球组织
   → 选择Playbook内部可用战术集合（必须拿到战术ID、类型、原生发起/终结角色）
   → 给球员安排最多四项有序Play Types + Play Initiator等角色（真实字段取值需游戏内存认证）
   → 设置球队RunPlayTendency与POE、球员Touch/Shot/Iso/Drive/Post/Spotup/Discipline等个人Tendencies
   → 赛前对不同对手预设整体防守+对手具体个人防守策略
   → 原版ACE与原生进攻/防守AI在真实3D比赛选择/执行（不由模型实时干预）
   → 统计产出/录像中可观察的动作/效率、长期自然成长（证据级别各不同）
   → 下一GM经营点比较：HOLD / 体系与战术调整 / 合理修改个人倾向 / 教练员工 / 交易与签约

**这不是一条“体系对→所有战术必执行→赢球”的确定因果链**。AI战术权重、动作判定与数值系数未开放，某步骤即使配置正确仍可能出现原生AI跳过/采用其它方案。应区分：①球员有无动作/能力，②手册有没有该类型，③教练会不会调用，④得到机会时选择是否合理，⑤防守对策后能否执行。

## 2. 项目当前实际掌握什么，什么仍缺失

### 已有真实接口（PROJECT_VERIFIED，不重复实现）
- 30队主教练原生默认 **19项**：POEOffense/2/3、POEDefense/2/3、PreferredSystem、ActiveSystem、PlaybookID、BenchDepth、RunPlayTendency、ZoneUsage、BenchUtilization、Tempo、HelpDefense、FreelanceType1–4。见 web_gm/manuals/GM_COACHING_OPERATIONS.md 与 docs/40_COACHING_EXECUTION_RUNBOOK.md。
- 已认证8个体系枚举：BALANCED、GRIT_AND_GRIND、PACE_AND_SPACE、PERIMETER、POST、TRIANGLE、SEVEN_SECONDS、DEFENSE；当前加载PlaybookID可以从现存本目录选择，但**PlaybookID≠已读出该本的战术列表**；四个Freelance槽按顺序，有34项来自当前原生目录，不能从名字确定调用概率。
- 每个owner对29个对手的整体防守，18个字段：PressureOnball、PressureOffball、ForceDirection、ScreenDefenseOnBall、ScreenDefenseHedge、OffballScreenDefense、PostDefense、DoubleTeamPerimeter、DoubleTeamPost、ScreenDefenseOnBall5、ScreenDefenseHedge5、SwitchRule、OnballHelp、ScreenHelp、ExtendPressure、TagOnRoll、StayAttached、PreRotate。实际布局有matchup 8-byte记录且含player/defender identity；**当前执行器只提供OVERALL整体同步设置，不提供逐个球员差异化目标**。
- 在队466等按批球员身份、位置、55项解码属性（含potential）、合同与部分累计统计、1458员工目录及球队员工关联；**不意味着个体完整Tendencies、徽章、Play Types、Play Initiator、Playbook内部战术图、教练实际评级/体系熟练度都已可用**。本项目catalog明确overall/full badges/tendencies等非认证。
- 玩家已亲眼看到每名球员4个原生战术选择和针对每名对手的防守设置，后者仍待Codex在已有防守对象内打通个人目标。训练机制由Antigravity继续寻找所有原生可控输入和疲劳/成长反馈，不纳入本研究编码第一批。
- 个人精确分钟游戏会重写，已接受不锁分钟；保持BenchDepth与BenchUtilization。

### 数据必须严格区分三类
1. **Ability/Attributes**：某动作能做到什么程度（投篮、传球、挡拆、速度、横移、防守等），**只读+分析**，普通GM严禁修改；
2. **Tendencies/Play Types/Play Initiator**：倾向做什么、被安排成什么进攻角色，**赛前战术受控可修改（用户本轮授权“Tendencies可提案并经审批执行”）**；不声称任何特定Tendency已在本机找到可写内存；
3. **Coach/System/Playbook/Defense Scheme**：球队希望以什么规则和方案创造机会，另含人员能力和AI自主执行；GM有权制定，但实际字段随各Codex执行接口成熟后逐项开放。

## 3. 2K22玩家实测：个人4项Play Type、战术本、叫战术的约束

### 3.1 确凿有用的玩家案例

来源A：[Operation Sports NBA2K22 Useful Findings，2021-09-18](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)，发帖者jimbo3772：
- 个人Play Types与球队Playbook必须匹配；有玩家曾无法让球队小前锋获得合理战术，查出手册内根本没有该类型的战术。
- 他称Touch在Freelance中更重要，而有组织的战术分配要同时看队伍战术调用频率、球员Shot/Touch/Play Discipline/Iso、原生Play Types、Playbook和球员评分。这是**社区经验，不是开放引擎公式**。
- 其经验表明PG默认触球方式和SG/SF不同；不能以30队统一Touch=50或明星全99代表篮球合理配置。

来源B：[Operation Sports Useful Findings page4 #54–59，2021-09-20](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page4)：
- Vannwolfhawk等指出一个具体可操作错误：把球员Play Type槽设成ISO POINT，但球队Playbook无ISO POINT战术时，该槽在战术调用界面会被跳过并落向Play2；**该作者直接提到这一行为**。
- 有些默认Playbook中战术似乎强绑定特定持球人/受益者；作者在雄鹿/快船调试时，错误分配本以为Holiday发起的ISO给Giannis（或者设置George更高Touches仍由Kawhi占多数），发现需要同时检查战术类型、Iso偏好和手册本身。**只有类型相同≠战术一定以期望球员终结**。
- Vannwolfhawk后续报告为30队及自由球员修改Tendencies和粗略Playbook，经逐队赛场观察调整，特别提到快船与雄鹿需持续清理默认硬编码问题。[NBA X's & O's page4 #58](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916550-nba-x%E2%80%99s-o%E2%80%99s/page4)。

来源C：[Operation Sports How to get the CPU to run more different plays，2022-10 #16](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/927270-how-to-get-the-the-cpu-to-run-more-different-plays/page2)作者明确说2K22前几代存在hardcoded plays、2K23更改；**跨年份对比，验证2K22可能存在手册内部硬限制**，不是2K22官方技术文档。

### 3.2 由此产生的“可计算而不编公式”的合法性检查

对每个本局在队球员 p 的第i槽原生PlayType，计算 MATCH_CANDIDATES = {当前球队Playbook中原生type标签包含p.play_type[i]的战术ID}：
- 槽为空：无要求，不能标不合法；
- 槽非空但候选集=0：**STATIC_PLAY_TYPE_UNSERVED**（明确静态未匹配，属于可修问题）；
- 槽非空候选集>0：**TYPE_MATCHED_ONLY**（只保证“有同型候选”，尚不能保证实际角色、持球人、掩护人和发起/终结动作匹配）；
- 该战术被原生目录确认存在固定接球者/发起者且与角色冲突：**ROLE_OR_TARGET_MISMATCH**；
- 本队只拿到了PlaybookID没有内部战术清单：**COVERAGE_UNKNOWN**，不能标为匹配也不能捏造该本内容。
- 有效PlayType槽“有序”，但**不把4槽理解成四个固定战术按钮**，也不假设每槽25%调用概率。原生是否最多4项由玩家已观测菜单和Codex即将取证确定。

推荐计算：per-team`play_type_coverage_by_player`、per-type`book_available_actions`、`usage_concentration_proxy`（带来源），不得采用无游戏证据的“覆盖率>80%=稳赢”的伪规则。

## 4. 2K22个体Tendencies：重要但相互作用有冲突的经验

- [Useful Findings 主帖 #1–#8](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)：玩家把所有Touch调至50观察到角色球员参与增加，另一位强调Touch主要作用于freelance，不是叫战术的唯一控制项。**这里意见不一致，应当将其定位为球权分配候选，不作为全部球队强制规范**。
- [Useful Findings page8 #110及跟帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page8?postcount=59)：个别玩家报告降低明星Close Shot Tendency到50或49后球队更多寻找队友，即使复原默认Playbook。这与纯粹“Close Shot只决定近投动作”的直观理解不同，**说明可能是2K22复杂权重/强绑定/版本bug；不可宣称已证实CloseShot是战术发起单一开关，也不统一改所有人49**。
- [Useful Findings page9](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page9)：有人改**全局Tendencies**（Inside/Close30、Mid/3PT60、Attack Basket40、LookPost80等）认为CPU出手更丰富；另一人明确认为个体Roster Tendency更有效，尤其Touch影响角色参与，并报告全局降低Ball Handle到35带来非常不自然的大量停球。证据反而支持**先按每队角色/手册调整个体行为，而不是套全局万能模板或直接改所有球员能力滑块**。
- Play Initiator（是否可持球组织球队）需单独读取；与Play Type1为ISO结合可能让Giannis等球员变成单一持球单打模式，玩家讨论对此有直接反馈。[Useful Findings #10](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)。

### 个人倾向调校优先级与非目标

**先读，按战术目标最少量更改：**
1. Ball dominance: Touches, Shot Tendency/Shot Frequency, Play Discipline, Isolation/Play Initiator（是否原生存在，标个别游戏字段）；
2. Shot profile: Drive/Attack Basket, Take Inside/Close/Mid/Three, Pull-up/Stepback, Spot-up, Fadeaway, Post（以实际目录为准）；
3. Play action: Pass-Out vs Finish, Hand-Off/Screen Roll/Pop/Cut/Offscreen Catch（分清原生Play Type与Tendency；不能从命名推定两者同一字段）；
4. Defense behavior: Contest, On-ball steal, Passing lanes, Take Charge等个体倾向；**不以修改这些行为来替代原生个人Defensive Settings**。
5. 用户允许的是**战术适应性行为倾向改变**，不是让所有球队为了战绩把“投三分”统一99；更不是直接给球员增加3PT、BallHandle、DefAwareness属性。

**操作约束**：每个请求须有player identity、team+season、exact native field、old_value、new_value、NBA篮球理由、当前体系和手册对应行动、意图/副作用、审批版本、原值恢复；完成球员交易/换帅/换手册时应对旧倾向预设标`REVIEW_FOR_NEW_CONTEXT`，**不自动把球队个性化倾向永远遗传到新球队**。

## 5. Coach属性与球队体系：证据和未证边界

- 系列基础[Coaching Wiki](https://nba2k.fandom.com/wiki/Coaching)：Coach Gameplan、System Proficiency五颗星、Edit Playbook与练习等概念。当前本局已验收体系8枚举，只有把它们和**当前球员群的可实际观察适配评估**相联，才是真正“选体系”。
- [2K17–2K18 System Proficiency公开简介与论坛](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/835921-what-to-expect-from-the-new-system-proficiency-in-myleague)：教练对不同风格有偏好/加成，球员有适配程度与可能的正负影响。但这是系列概念，**当前PC版Coach能力对3D与CalendarSim的数字权重不明**。
- NBA2K22[2K官方MyNBA MySTAFF/PrepHub公告](https://newsroom-anz.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)明确是PS5/XBS次世代的MySTAFF/PrepHub/Conditional Coaching，**不能因为其他系统相同便给PC当成17部门/全部次世代员工属性**。
- 个别旧版社区关于Coach Defense Grade改善模拟防守效率的说法，后续又出现同作者相反观察：[2016 2K17 discussion](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/813334-myleague-simmed-stats)。这证明**不能捏造Coach Grade有确定+X胜率/效率效果**。GM需先按当前员工目录读教练能力与合同，缺语义就保持`UNVERIFIED_MECHANICAL_EFFECT`，再依据真实球队建队文化和观察事实选择教练。

判断体系：
- roster fit：后卫持球创造、射手接球/无球跑位、内线传球/策应、顺下/外弹、篮板/弱侧护框/横向移动、对位可换性；
- coach fit：当前教练偏好体系/本局已见熟练度、战术手册适配、员工训练与指导能力（如果源数据可用）；
- playbook fit：类型覆盖率、具体战术发起/受益位置；**某体系名称不自动保证某手册每条战术相符**。
- 若阵容已有合适球员，优先改体系与手册；若缺目标体系所需的执行人、即使配方正确也不能凭空增加技能→才触发交易、报价及薪金约束。

## 6. 个人防守设置：原有18个OVERALL字段不等于已经能逐人控制

现实篮球战术需要知道“防守谁”，而不只是“全队防守什么”。

- [2K22防守设置玩家指南](https://www.aoeah.com/news/556--nba-2k22-defensive-settings-tutorial--best-lockdown-defense-settings-you-can-use-in-nba-2k22)明确因球员差异可以为主要射手单独选择绕掩护、其他球员默认或钻掩护等；这是技巧攻略不是开发内存认证。
- [系列On-ball screen/Hedge per-player解读](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/806956-on-ball-screen-center-hedge-center/page2)：说明持球人防守者On-Ball Screen与掩护者防守人Hedge含义不同，存在ALL和指定对手球员层级；系列级原理对2K22的原生架构有参考价值。
- [2K22防守AI问题文章](https://www.operationsports.com/nba-2k22-gameplay-pick-and-roll-defense-must-improve-this-year/)提醒PreRotate等选项未必像描述工作，原生AI漏防仍可能存在。**不能因为Gameplan可写就承诺一定消除PnR弱侧漏人**。

需要给Codex的精确对象身份：
`owner_team_id, opponent_team_id, opponent_player_id, matched_defender_id, defense_field, native_enum`。当个人覆盖与OVERALL同时存在时，必须确定默认/个别条目的**继承规则与重叠优先级**，以及是否为同一个原生matchup record及提交标记。现有OVERALL写入会遍历有效条目统一改值，**新PERSONAL配置不能因此无意被以后一次OVERALL重写抹平**；先设计覆盖/继承策略才接入。

GM的防守计划至少包括：
- shooter：紧贴无球/不随意协防离开、掩护优先绕上，风险是被反跑；
- non-shooter：可收缩帮防，风险是空位后补投和被反制；
- PnR ball handler：绕上/绕下/ICE/switch与对方持球投射/突破能力匹配；
- roller/popper：另一侧Hedge、TagOnRoll和后排轮转，需要看内线护框与弱侧补位；
- wing isolation：指定真正有能力的一防球员、决定是否夹击与承受弱侧空位；
- 强队必须保留多个策略分支以应对对手利用错误换防；这仍是**赛前条件式方案**，不是运行时外挂AI。

## 7. 同一套体系在3D比赛与CalendarSim里的适用范围

- 用户此前**明确只允许“游戏引擎全局参数调校”研究实时3D比赛，不允许改变日历SimEngine来强制赛季结果**。本研究强调GM做的体系、教练、战术、球员倾向可能同时在3D与日历模拟中影响球员使用和结果，但其每项影响模式/权重**尚未证明**。
- GM可以用月度赛季累计技术统计和已知3D视觉结果做事后判断，不能将SimEngine内部的胜率计算当成已找到，也不能把“跑出了2022勇士冠军”当作策略成功的唯一证据。
- 专项诊断不把双方混淆：`LIVE_COURT_BEHAVIOR`能从观察和控制器输出确认，`CALENDAR_SIM_OUTCOME`只能从快照统计和赛程识别；球员个人Tendency或教练配置在两侧的影响**不可直接等价**。Gameplan、RunPlayTendency、属性效果需要按平台/游戏版本留未知范围。

## 8. 2022金州勇士案例：重心不是“给Wiggins更多能力”

现实NBA事实：
- [NBA 2022 Finals Game5](https://www.nba.com/news/inside-the-box-score-2022-nba-finals-game-5)：Curry 16pts、0/9三分，Wiggins 26pts13reb，20分在禁区（13分来自11次持球突破）；勇士Curry在场仍有约118.7的每百回合进攻效率，说明Curry无球引力/传球等效果不能只看自己进球率。
- [NBA官方Game5录像战术分析](https://api-hub.nba.com/news/finals-film-study-game-5)：Wiggins本场季后赛最高占有率26.4%，0/6三分但17投12中两分；利用错位，特别面对Horford、Williams及White的持球突破/低位攻筐。**这不是唯一因果来自Curry被夹击，而是球权再分配、对位、Wiggins主动攻击和团队防守多因素组合**。
- [NBA总决赛历史](https://www.nba.com/playoffs/2022/the-finals)：勇士G4 Curry43，G5 Wiggins26/13，G6 Curry34；不能把“Curry被彻底锁死”讲成整轮事实。
- 防守另一半：Wiggins主要防Tatum的高强度工作、Green/Looney/GP2的协防换防、篮板与对手失误同样是赢球体系，不是只有围绕Klay和Curry增加三分战术。

### 由现实机制到NBA2K22的赛前配置原则（示例，不是已经读取本局Warriors或批准目标）
| 角色 | 教练与手册方向 | Play Type与倾向方向（以实际原生类型查） | 能力约束与防守交换 |
|---|---|---|---|
| Curry：核心引力+持球/无球双威胁 | 主攻挡拆与射手掩护战术兼有，不能只保留给Curry的持球Iso；优先找无球screen、PnR ballhandler、手递手/空切配合 | 与真实场上用途匹配的组织/射手/掩护后接球PlayType；适当允许超远投、突破分球及回传，**不是全部Shot/Touches设99** | 传球与投射属性由原生事实只读，面对包夹应留内线策应和弱侧牵制路线 |
| Thompson：无球移动终结者 | 手册需要catch-and-shoot/offscreen（floppy、pin-down等具体战术须看本局目录） | 以无球掩护后接球投、定点投为主，减少纯控球长时间Iso发起 | 保持真实运球和身体条件，不为战术强行加控球属性 |
| Green：策应轴与多位置防守 | high post、短顺下、handoff、二次转移球 | 组织/手递手/屏障后分球角色；尽量避免无效顶投（当时现实投篮威胁有限） | 现有传球/防守原生能力支撑策略，**不会因此得到新能力** |
| Looney：高质量掩护/顺下与篮板 | PnR screener、内线短顺下、掩护转移 | Roll Man、Screen/Handoff等能被手册支持的类别；不叫他运球超远三分 | 防守端如面对速度型球员要配置合适Drop/Hedge而非假定有无限横移 |
| Wiggins：二次持球、切入与核心侧翼防守 | Curry被针对时允许更高优先级的翼侧Iso/错位攻筐、second-side drive，不要只有等球定点 | 适量孤立单打、空切、持球突破与球权倾向（基于本局角色变化的最小调整），但不是“总决赛曾爆发所以每场强制26分” | 侧翼一防、后场篮板与对位Tatum等任务，与进攻负荷/阵容轮转一起安排 |
| Poole/Payton/Porter等 | 板凳火力/跑动或防守接应、spacing | 为不同人员设与手册匹配的次级PlayType和被调用机会 | 机会成本取决于真实原生能力和当期健康，不靠提高OVR |

### 针对防守方策略的“赛前多选项”，不是外挂实时监控

- 对手Drop防Curry PnR→优先用允许挡拆持球急停远投/Screen再传的实际战术；**改变球队行为但不用改Curry三分属性**。
- 对手Blitz/包夹Curry→手册必须有Green短顺下、二次传导与弱侧处理；Wiggins持球突破和空切成为第二终结机会；若本局人员不能完成某角色则GM考虑交易。
- 对手Switch All→用错位点名、不让多人站着看Curry单打；球员Iso指令与手册真实Iso类型对应，成本是全队球停滞和疲劳。
- 对手Top-Lock Klay无球跑动→支持反跑空切、弱侧45度斜切、重新设置下掩护；改变角色的战术路线而不是给Klay速度+10。
- 防守对手Tatum/Brown→按Wiggins/Green/Payton等人员实际横移与对抗能力设置个人OnballPressure、绕掩护/Double和弱侧Tag策略；若挡拆弱侧无人补防属于游戏固有缺陷，不能用乱调个人能力骗过去。

交易从这套系统中自然产生：只有当已证实存在某个角色缺口、当前战术/阵容内部调整仍无法弥补，且具体引援既满足战术执行又满足预算/合同与对方GM意愿时，才提出交易。**不是缺三分就只看3PT rating高者。**

## 9. 对GM的新决策顺序：诊断原因而非靠交易自我说服

每个球队检查点按以下顺序：
1. **明确战术身份/赢球方法**：谁创造优势、谁让优势传递、谁终结、谁防守、核心2–3项优势及对方如何针对。
2. **事实盘点**：教练能力可观测等级、8体系中的当前与偏好、4个Freelance、整个Playbook战术、每人最多4个PlayTypes、全部Tendencies与55原始能力、实际使用/效率、教练默认和整体+逐人对手防守。
3. **发现断链**：类型不匹配、错误球权集中、体系-手册不匹配、对位没有合适防守者、球员技能不足、缺少某角色但还有替补、训练或受伤不可用。
4. **生成有代价备选**：HOLD vs 改赛前体系/Playbook vs 改球员战术槽/个人倾向 vs 改个人防守策略/轮换 vs 教练/员工 vs 交易/签约。要写出每个候选改善什么、牺牲什么。
5. **评价真正的取舍**：球员原始能力约束、对手能否限制、财务成本、合同机会成本、伤病/负荷，分别考虑3D和CalendarSim没有同一公式。
6. **30队独立议价/审批/落地**：交易与教练/个体倾向提案分离具体动作，玩家批准后Codex按来源和执行器的真实认证范围写回，自动记录修改前/后与新战术兼容度。
7. **后验归因**：当玩家后续正常推进游戏并采集新批次，使用与此前可比的来源检查战术决策假设；未观察到不能宣称因果已证实。**不强制为模型制造一百场比赛验收**。

## 10. 后续Codex实施首批必须补的内容（具体工程方案见DEV文件）

- 先建设只读来源：当前NBA2K22在队个体全部Tendencies、四槽PlayType/Play Initiator、Coach属性及system proficiency（实际字段有才读）、Playbook目录和各本真实战术类型/发起者、对手Gameplan单个player/defender对应字段，**清晰区别本局和系列推断**。
- 再做离线`TACTICAL_FIT_DIAGNOSTIC`：给出每个球员某槽是否有对应战术、身高/能力/倾向与预期角色是否矛盾、球队战术集中度、个人防守任务与对位能力缺口；哪怕只读部分来源也能部分报告，UNKNOWN不得当冲突。
- 然后提供经审批的`PLAYER_PLAY_TYPE_CHANGE`、`PLAYER_TENDENCY_CHANGE`、`INDIVIDUAL_MATCHUP_DEFENSE_CHANGE`、`PLAYBOOK_CONTENT_CHANGE`，**不能借普通倾向批准直接改任意能力或徽章**；当前已有PlaybookID和整体防守不应重新开发第二套。
- 最后建立GM可读的架构说明/案例库：30队不同篮球风格、各队赢球条件和对手反制、角色缺口与交易需求。不要用随机权重自动凑成一个“体系适配总分”。

## 11. 来源主索引

- 2K22社区原生球权与战术：[Useful Findings主帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)、[page4战术跳过/固定受益者](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page4)、[page8 CloseShot争议](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page8?postcount=59)、[X's & O's战术书制作](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916550-nba-x%E2%80%99s-o%E2%80%99s/page4)。
- 系统和对位：[Coaching Wiki](https://nba2k.fandom.com/wiki/Coaching)、[2K22对人防守指南](https://www.aoeah.com/news/556--nba-2k22-defensive-settings-tutorial--best-lockdown-defense-settings-you-can-use-in-nba-2k22)、[系列Screen/Hedge个别与整体](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/806956-on-ball-screen-center-hedge-center/page2)、[NBA2K22原生PnR漏洞](https://www.operationsports.com/nba-2k22-gameplay-pick-and-roll-defense-must-improve-this-year/)。
- 教练/训练跨版本限制：[MySTAFF/PrepHub 2K22官方次世代限定](https://newsroom-anz.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)。
- 现实2022总决赛：[NBA官方G5统计](https://www.nba.com/news/inside-the-box-score-2022-nba-finals-game-5)、[G5战术影片分析](https://api-hub.nba.com/news/finals-film-study-game-5)、[总决赛逐场](https://www.nba.com/playoffs/2022/the-finals)。
