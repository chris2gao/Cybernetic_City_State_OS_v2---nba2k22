# BPTI — R3 NBA2K22 PC Current Gen原生行为与篮球意图映射 V1

日期：2026-10-20 | 负责人：Web GPT | 状态：**RESEARCH_COMPLETE_FOR_ARCHITECTURE / SPECIFIC_BEHAVIOR_UNVERIFIED / NO_GAME_WRITE**

## 0. 本报告研究的实际对象、证据尺度

平台是**NBA2K22 PC旧世代终极联盟（非PS5/Xbox Series MyNBA新世代）**。对项目原生能力认知优先阅读`docs/DEV14_STATE_IO_RUNBOOK.md`、`web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md`、`web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md`和`docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md`。官方2021 2K Gameplay陈述只证实游戏侧存在防守、投篮、低位等设计，**不证实某个GM可写字段的AI权重或Calendar仿真效果**。

四档不同证据：
- `PROJECT_VERIFIED_INTERFACE`：当前main中DEV14/M3-T已记录、已验收的读取/离线意图能力；**不是场上行为机制和胜率因果已经验证**。
- `PLAYER_CONFIRMED_RUNTIME`：仅玩家明确确认的当前机器/菜单行为；不能让网页历史经验替代用户现场观察。
- `COMMUNITY_OBSERVED`：2K22玩家可回溯的主观试验结果；有版本/阵容/滑块/对手等混杂因素，不能强制全联盟照搬。
- `UNKNOWN_OR_UNSUPPORTED`：真实篮球技术虽存在，但没有认证的PC精确控制、已经确认不能写或交互效果不明。UNKNOWN不能被静默映射成“自动”。

另有`NBA_REAL_BASKETBALL`用于R1/R2篮球因果和球队历史，**与以上游戏证据正交**。R1/R2十大家族不是NBA2K22八体系原生枚举。

## 1. 已确认的原生可控能力（以main最新M3-T与DEV14为准）

| 类别 | 已确认读取/提案能力 | 禁区/限制 | BPTI作用 |
|---|---|---|---|
| COACH_DEFAULT | 19项：POEOffense/2/3、POEDefense/2/3、PreferredSystem、ActiveSystem、PlaybookID、BenchDepth、RunPlayTendency、ZoneUsage、BenchUtilization、Tempo、HelpDefense、FreelanceType1–4；正常18项可提案 | 5 Sim附加字段只读；Tempo raw语义UNKNOWN；PlaybookID仅TEAM_BOOK_REBIND专门步骤可变 | 选择篮球方向与可用人员的**粗粒度框架** |
| SYSTEM | 八枚举：BALANCED、GRIT_AND_GRIND、PACE_AND_SPACE、PERIMETER、POST、TRIANGLE、SEVEN_SECONDS、DEFENSE | 无MOTION/POINT_CENTER/SWITCH_PRESSURE等一一对应专属枚举；教练熟练度≠必须用最高 | 球队系统偏好候选，不能单独构成完整战术 |
| FREELANCE | coach.FreelanceType1–4有已加载原生目录及顺序 | 目录词义与调用频率并未逐一认证；未证多套freelance如何自动切换 | 空间、接应、无球运动结构的候选 |
| TEAM_PLAYBOOK | 本队同名已加载68个槽，目标CRC必须来自**同批本队已加载目录** | CRC→具体动作/参与者/第一受益人多数UNKNOWN；不能借别人书或凭想象创造PlayID | 体系能否在本队具体发起战术 |
| PLAY_TYPES | 球员4个有序PlayTypes+Initiator | 不假设平均调用概率；一个Type可能在本队书里没有可用战术 | 建立玩家角色与已有战术包之间的静态匹配 |
| TENDENCIES | 99字节中具名48项可提案 | 51未知RAW只读；Touch/Shot/Iso/PlayDiscipline之间因果及效果量不确证；不能一律重置50/80 | 已认证角色行为、出手偏好、选择权的方向性改动 |
| DEFENSE | 18项`PERSONAL_DEFENSE`，按当前owner/opponent/player/defender原生身份 | **OVERALL_DEFENSE日常GM只读**；AUTO是原生enum不等同不存在；不能无具体对手偷改全队 | 具名个人防守和对手反制的最小实现层 |
| ROTATION | BenchDepth、BenchUtilization、Intangibles 25–99软轮换 | AI覆盖精确分钟；Intangibles不作为纯篮球能力/市场价值/成长指标 | 战术角色可能获得机会，但不承诺分钟 |
| TRAINING | 6项球队、5项球员训练 | 原始Ability/Potential/Badge/身体/速度不可被普通GM修改；自然成长由游戏决定 | 训练方向的合法配置，不承诺瞬时技能增长 |
| STAFF | 已有coach_traits/体系熟练度的读与策略判断、休赛期换帅一次商业约束 | **不存在经证明可用的完整教练签约/任命市场执行器**；换帅首先是研究/审批，已确认换帅后才能恢复本队书 | 教练哲学/适配，不假装有聘任成功 |
| EXECUTION | M3离线`build_plan`、DEV14受控state I/O和tuple | 绝不由BPTI提供raw地址/自动批准；源或身份漂移阻断，`TEAM_BOOK_REBIND`与编辑手册需两次分开审批和重采集 | 篮球意图→受控字段差异/失败原因 |

注意旧版`docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md`是M3-T实施前历史调查，其中“尚未实现PERSONAL_DEFENSE”已被后来的DEV14/M3-T覆盖。**以新交接和已合并代码为准，不误报能力缺失。**

## 2. 十种R1家族 → 当前2K22已知控制层映射矩阵

每行“可用杠杆”表示可以提出**篮球意图和相应原生字段候选**，不意味着每一种真实战术连锁都可由ACE稳定执行。以下是方向，不是批准数值。

| R1 family | 篮球意图/必须保留的因果 | 具备的可提案层 | 关键UNKNOWN/失败时处理 |
|---|---|---|---|
| MOTION_READ_REACT | 持续掩护/传导/切入→防守交换责任→二次选择 | SYSTEM粗粒度+Freelance候选+已加载本队Playbook+四Type/Initiator+具名Touch/Shot | 精确split/slip/backdoor/受益人并非都可绑定；UNKNOWN时只给可确认的Movement/PlayType候选，不能假冒全套Motion |
| TRIANGLE_INSIDE_OUT | 强侧三角/低位高位入口/弱侧两人协作→阅读包夹 | SYSTEM=TRIANGLE是已加载原生枚举；书槽、Post/Pass相关已知角色候选 | 枚举名字存在≠当前68槽有真正Triangle完整实现、或Jordan式接球选择得到复现；无真实对应CRC则HOLD槽写 |
| SPREAD_PICK_AND_ROLL | 挡拆强迫防守drop/hedge/blitz/switch→短顺下/二次传导 | SYSTEM=PACE_AND_SPACE等**候选非唯一**、Freelance、对应Type/Book、个人持球/roll/pullup倾向；PERSONAL defense可设对手持球人策略 | 具体PnR战术CRC、短顺下4v3受益人、覆盖因果效应待证；不能凭「挡拆」词猜影响 |
| ISOLATION_MIDRANGE_CREATION | 独立创造/错位/末节失败后bailout | 合法个体已具名Shot/Iso/Close/Mid等、Initiator、Type、现有ISO候选、RunPlayTendency | 没有“保证关键时刻德罗赞必单打”的实时指令；GM不能用提高原始Midrange能力替代创造权 |
| POST_HIGH_LOW | 深位得分/吸双人/拒绝接球的再反制 | SYSTEM=POST候选、已存在Post类Type、Book、已具名post/shot习惯 | 精确double reading/high-low lob非已证原生脚本；post-touch不足也可能来自拒绝entry |
| POINT_CENTER_ELBOW_HUB | 大个传球中心→DHO/空切/二次PnR | 高位/手递手类已知可读Book候选、角色/Initiator/PlayTypes、Freelance/教练选择 | **没有Point-Center专属枚举或保证内线长期作为hub的已证字段**；真实战术不符时只输出PARTIAL_SUPPORT/RESEARCH，不虚报实现 |
| TRANSITION_EARLY_OFFENSE | 防守停球/篮板后早攻，失败流入半场B方案 | SYSTEM=SEVEN_SECONDS等粗粒度候选、当前Coach POE、相关角色与训练 | Tempo原生raw语义UNKNOWN，不能以该字段直接宣布已改变每回合秒数；独立转换机会生成率未知 |
| DEFENSE_FIRST_RIM_PROTECTION | 守住篮筐、改变第一线决策、延伸补防链 | SYSTEM=DEFENSE、Coach POE、具名对手PERSONAL的掩护防守/协防等 | OVERALL只读；没有精确“把某个护框者永远固定在油漆区”保证，不能等价盖帽 |
| SWITCHABLE_PRESSURE_DEFENSE | 换防消除第一掩护优势，随即scram/peel应对错位 | 对具名对手PERSONAL中的已证enum、掩护策略；依据本局Defender/Offender真实能力 | scram/peel/pre-switch并无已认证独立实时可写按钮；换防选择只适用于真实对位/字段 |
| ADAPTIVE_MULTIPLE_SYSTEMS | IF对手用X克制主方案 THEN切Y BECAUSE取走X优势 ACCEPT代价Z | 支持**玩家触发GM赛前多个方案版本**，本队coach/Book/Type/个人防守都可形成稀疏候选 | 不能声称外挂比赛时实时识别防守覆盖并改方案；ACE自主临场行为是黑盒，GM仅检查点/赛前离线配置 |

**重要边界**：R1的“Scripted→Read→Creative→Bailout→Reset”五类是篮球决策权**认知标签**，不是2K22已认证的五个调节器。它们用于决定哪些角色、战术和已知倾向可能值得变更，编译输出能精确控制的子集；没有可控杠杆时提供`UNSUPPORTED`或研究请求。

## 3. 具体映射合法性判断顺序

依次执行（都是轻量业务条件，可复用M3 DTO，不新建引擎）：
1. 阵容与球员（同一`require_gm_sanitized`来源）：球员身份存在、关键篮球技能与角色要求能从本批原始属性**只读**或允许的当期比赛表现确认；Potential始终MASKED；`Intangibles`不进入真实技能判断。
2. 教练与已加载球队同名书：Coach当前原生体系、Freelance、Playbook对象身份与同批槽位真实可读。换帅后若本队书尚未恢复，先`TEAM_BOOK_REBIND`审批执行、重新采集，再调整槽。
3. 角色图：每位球员明确FIRST_CREATOR、CONNECTOR、FINISHER、DEFENSIVE_ANCHOR等多角色标签；R1球员自主层级仅是责任而非数值。
4. 战术静态类型覆盖：本队每个有序PlayType与**已证该槽具有的类型元数据**做交集。`NO_CANDIDATE`只能在战术类型元数据已证覆盖、且集合确为空时输出；只有CRC不解含义或type没读时必须`TYPE_UNKNOWN`，不能误判缺戏。
5. 进攻/防守方向性意图：依据当前篮球因果，选择最少量已知coach/tendency/PlayType/个人防守候选；遇到不同方案写相同字段不同值时交既有M3冲突逻辑，不让BPTI直接resolve成假定数值。
6. 输出`SUPPORTED_FIELD_DIRECTION`（有已证字段但效果尚未量化）、`TYPE_MATCHED_ONLY`、`UNKNOWN_NATIVE_BEHAVIOR`、`UNSUPPORTED_ACTION`及`HOLD_RESEARCH`，并明确是否可走已有M3离线plan。所有真实写入都必须用户另批。

针对精英球员创造权：不得强制所有队Touch=50或将Shot顶值锁80；这类社区案例只能作为“某些配置可能导致过分集中”的排查线索。不能由单一数据阈值主动压制midrange/post/isolations，也不能把可写Tendency当修改原始能力的后门。

## 4. 外部材料核查与冲突记录（可溯源）

**2K22官方（跨平台一般性特性，平台限定条款需阅读）**
- `R3-S01` 2K Newsroom 2021-08-31 `https://newsroom.2k.com/news/nbar-2k22-unveils-new-gameplay-innovations`：说明该游戏重视防守AI、移动、投篮与低位，**没有开放教练脚本行为权重/SimEngine内部机制**。
- `R3-S02` PlayStation官方2021-08-31 `https://blog.playstation.com/2021/08/31/nba-2k22-gameplay-deep-dive/`：明确多数Gameplay改进覆盖PS4/PS5，但另设`Next-Gen Defending`专栏和PS5独有功能；PC不能直接推论使用PS5的下一代AI特性。
- `R3-S03` 2K MyNBA新世代公告 `https://newsroom-anz.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles`：明确PS5/Xbox Series平台限制，不能从MySTAFF/PrepHub/Conditional Coaching推导本PC可用。

**当年社区的具体冲突（非引擎定律）**
- `R3-C01 TOUCH_MECHANISM_CONFLICT`：`https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings`（2021-09），一位玩家统一Touch=50观察到更广泛角色参与，另一位认为Touch更影响Freelance阶段、战术调用还由Run Plays/PlayTypes/书/球员技能等决定。不能由此认定`Touch=50`跨球队适用，也不能证明`Touch`对固定战术绝对无效。
- `R3-C02 SHOT_TENDENCY_CONFLICT`：同帖`.../page10`（2021-10）有人观察把Shot最高限制80后进攻分布改善，另有帖子观察Shot数值与实际战术调用不一致。**归因不确定**；不能做标准全联盟规则。
- `R3-C03 PLAYBOOK_BENEFICIARY_CONFLICT`：`https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page4`，不同特定战术的实际受益球员与玩家指定的不符。即使type一致，也只有`TYPE_MATCHED_ONLY`，并不能保证实际接球者。
- `R3-C04 CROSS_VERSION_OVERREACH`：NBA2K23/2K21/新世代论坛建议只能作为背景；玩家设置地址、版本菜单若无本局认证不能纳入2K22PC执行器。
- `R3-C05 GM_DEFENSE_OVERRIDE`：用户实机确认OVERALL会覆盖PERSONAL，GM已将整体防守设只读；不能按旧文献推荐“先整体再个人”日常写方案。
- `R3-C06 3D_VS_CALENDAR`：本研究无法确认同一Coach/PlayType/Tendency对3D和Calendar产生相等方向和量级，留独立后续季后赛校准器；不得把比较来源注入普通GM分析。
- `R3-C07 PLAYBOOK_SEMANTIC_UNVERIFIED`：已知68槽CRC/对象写入能力≠具体Spain PnR、short roll、post split、pin down的角色/目标已证实；若不确认，当前只能对**已加载且已知**的部分槽出拟变建议，否则HOLD。

## 5. 给R4与Codex的交接

最小`BasketballNativeBinding`（研究规格，不是现成代码）：
```yaml
basketball_intent_id: BPTI-PLAY-...
basketball_claim_ids: [R1-..., R2-...]
family: SPREAD_PICK_AND_ROLL
team_id: IND
roster_batch: CURRENT_GM_SANITIZED_ONLY
required_roles: [PRIMARY_HANDLER, ROLL_SHORT_DECISION, CORNER_SPACER]
game_field_candidates: [coach.ActiveSystem, coach.RunPlayTendency, playtype.slot1, personal.ScreenDefenseOnBall]
native_field_registry_key: REQUIRED_FROM_SAME_BATCH
status: SUPPORTED_FIELD_DIRECTION | TYPE_MATCHED_ONLY | UNKNOWN_NATIVE_BEHAVIOR | UNSUPPORTED_ACTION
behavior_effect: HYPOTHESIS_NOT_GUARANTEED
unknowns: [PLAYBOOK_BENEFICIARY_UNVERIFIED]
fallback: HOLD_OR_RESEARCH
approval: NOT_GRANTED
```
TeamID/FieldKey只是**语义示例**，不能不查看本批Registry就直接把YAML当正式目标写入。下一步R4将R1 SystemCard、R2历史TeamIdentity（含`UNKNOWN`）、R3已证原生Binding合为最小DTO及GM reasoning步骤，仍保留M3既有财务、交易/教练市场和DEV14执行门，不新建实时引擎。

## 6. 研究结论

**当前已具备可靠的“篮球意图→原生字段类别→离线意图→用户审批执行”工程路径，但不具备“篮球每条实时动作均可精确编程”和“30支球队方案已逐场实机证实”的能力。** 因此BPTI应首先实现认知与证据-映射层，30队史候选，再在玩家批准后用已有已认证控制项生成真实差异化策略。阻断某个未证动作，不必取消球队整体篮球哲学；让GM明白“理念是完整的，游戏这次只能执行其中受证据支持的部分”。
