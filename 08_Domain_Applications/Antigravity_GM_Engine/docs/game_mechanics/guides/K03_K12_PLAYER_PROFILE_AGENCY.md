# K03 / K12 — NBA2K22球员完整档案、属性、身体耐久、徽章与自主职业生命线

> **DEV29 V3 / R04-A 首批正式中文研究（2026-10-21）**。研究对象NBA2K20–23系列，最终目标NBA2K22 PC本世代离线MyLEAGUE。**这份文档是供未来球员、GM、教练、媒体自主观察和选择的游戏机制原料，不是玩家编辑教程、不启动Agent、也不是批准修改球员属性。** 来源[SOURCES](../SOURCES.md) SRC-0072..0080；项目原生[PLAYER字段配置](../../../config/memory_field_profile.json)、[player.json](../../../config/state_io_native/player.json)、[source_extensions](../../../src/source_extensions.py)、[DEV15潜力遮蔽](../../development_tasks/DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)，以及R03的[K06](K06_TRAINING_HEALTH_GROWTH.md)。
>
> **按任务书本轮只完成R04-A**：个人身份、完整已知属性子集、部位耐久、徽章组/人格类别的首次梳理、自然成长的关键输入与严格信息边界。R04-B再调查全部行为倾向/PlayTypes与3D/Sim；R04-C深入人格徽章和合同意愿；R04-D全字段交叉权限、人物互动图谱。未完成的后续主题不能在此宣告完整。

## 0. 三轴证据：机制能够复用，字段仍需认证，当前实际读数又是第三件事

- `FRANCHISE_MECHANISM_REUSABLE`：用户确认2K22 PC本世代与PS5/Xbox Series终极联盟的经营机制大体高度可复用；合同、培养、球员卡、职业成长的参考优先取2K22同版，再参考2K20–23，**但不能倒推出同一raw/菜单项**。
- `PROJECT_NATIVE_LAYOUT_REGISTERED`：本仓库 `memory_field_profile.json` 已登记55项 `PLAYER.attributes`（含16项耐久）和17项 `PLAYER.contract`。这是有偏移的**真实项目注册子集**，不是球员全部可见数据全集、更不是R04-A进行了读内存或查看目前save。
- `CURRENT_BATCH_CAPTURE_VERIFIED`：只有当前`save_id/source_batch_id/source_profile`能确认名字、队伍、出生、属性读数与健康/合同状态均为真实游戏世界事实。本轮不读取存档，**第三方2K22球员展示站的球员数值不可当本项目当前联盟值**。

**额外关键**：官网/OS作者制作的ATD自定义名单展示**有哪些原生编辑领域**，不是“原版2K22默认的球员真实数值”或某项加成的官方算法。2021年12月ATD作者发文时PC名单还写为`work in progress`，其PS5/Xbox编辑数据不能代入项目PC存档。[SRC-0072/0073]

## 1. 球员“是谁”：身份、职业档案与全生命周期

### 1.1 个人资料和职业归属必须拆层

| 分组 | 玩家可见/有同版资料的候选字段 | 游戏系统中为什么有用 | 当前证据状态 |
|---|---|---|---|
| 核心身份 | 原生player identity/人物名字、姓/名、脸型与face ID、球员卡/头像/动画外观 | 交易、合同、历史选秀、职业故事必须知道**同一个人是谁** | 名字/face与来源映射在本项目数据工作流中出现；`face_id`单独不保证跨历史班唯一 |
| 生物与身体尺寸 | 生日、按game_date算年龄、身高、体重、臂展、位置与副位置、国籍、大学或来源 | 对位/阵容/运动属性、成长窗口和个人背景 | 2K22版本第三方原始字段页面详列[SRC-0074]；**本批PC字段覆盖不等于完全已采** |
| 选秀与经历 | Draft Year/Round/Pick/原选中球队、Years Pro、Roster Year、队史与球员位置变化 | 年资合同规则、历史选秀轮回和年龄相符性、跨队人生故事 | 同版2K22球员导出站[SRC-0074/0075] |
| 当前联盟状态 | 当前team、所属合同team、roster slot/健康可用状态、是否自由球员/伤停、球队球衣号码 | 合同/名单容量/出场资格、身份冲突 | 项目代码`player_details()`有`current_team_id`与`contract_team_id`两个指针；不一致需验证，**不是两者相同的硬假设** |
| 合同职业状态 | 当前年度工资、合同期限/剩余年限、选项/禁交易、Bird年数、续约相关字段 | 签约或交易时的真实约束及球员利益 | 项目原生Profile已登记17项合同子字段；合法合同机制在R05深入，本轮只识别原料 |
| 生涯事件 | 已完成比赛、赛季数据、联盟奖项、冠军、荣誉、签约/交易/伤停记录、退役 | Player在真实世界累积经历后改变自己的职业目标 | 可研究为信息来源，但**逐条事件是否被当前游戏保存/SQLite可查询必须按批次独立认证** |
| 外部身份记忆 | 球员自我故事、对球队/城市情感、教练信任、复仇或争冠志向、谈判承诺 | 实现真正的人格与长期记忆 | **外挂未来`EXTERNAL_SQLITE_CANONICAL`，不是游戏原生已记录事实** |

在2021年2K22同版Marques Johnson与Joel Embiid导出样例，`Bio`和`Development`还分开展示身高臂展、选秀顺位、年资、峰值年龄、成长曲线和合同等[SRC-0074/0075]。这足以为R04编制**人物来源字段目录**，但不能借外部网站冒称已读取本用户的球员pool。

### 1.2 不能把“名字/face ID”当跨世界线稳定主键

项目2021–22开档会轮回导入1984–2020历史选秀。如果一位球员被历史选秀注入、未来回归或多个数据源发生同名，应同时存储`career_id/save_id`、原生身份定位与来源、`snapshot_id/game_date`、选秀班身份和实际归属。**单靠名字、球衣号、face_id甚至当前队伍**不能可靠区分人物。候选复合身份只有经过游戏原生返回及本批去重、交易前后再认定为稳定；R04-A没有开发新的ID算法。

### 1.3 信息不是所有角色都等价可见

Player可知道自己的年龄、已有经历、合同与由自己提出的目标；GM可知名单/合同/公开比赛事实，但不该自动知道球员独有的内心打算；Coach能依据阵容、技能、训练与实际场上表现形成自己的判断；Media能知道公开荣誉、交易、出勤以及公开表态，但**不能从内部健康隐私或角色长记忆直接“报道事实”**。

## 2. 本仓库确有名字的39项非耐久属性：完整列出，不凭外站凑成“全游戏属性”

下面采用`memory_field_profile.json`中55项`attributes`扣除16项耐久得到**39项**。每项底层为1字节，转换函数`rating`，但**公开显示/实际历史上限、合法写入权不能从1字节推定**。名字是项目字段英文，中文为研究释义。这里强调何种**篮球行动能力**可能相关，**不是官方发动机计算公式或可直接编辑能力的权限**。

| 机制组 | 项目已注册英文原字段（中文） | 对角色决策可提供的区别 |
|---|---|---|
| 篮下与背身 7 | `driving_layup`突破上篮、`standing_dunk`原地扣篮、`driving_dunk`行进扣篮、`post_fadeaway`背打后仰、`post_hook`勾手、`post_moves`背身动作、`draw_foul`制造犯规 | 同样是内线得分，终结路径/身体对抗/被犯规能力不同，Coach可要求不同角色 |
| 外线与判断 5 | `shot_close`近距离、`mid_range_shot`中投、`3pt_shot`三分、`free_throw`罚球、`shot_iq`投篮决策 | 技术命中能力与选球IQ不同；不得从三分评分直接生成三分出手次数 |
| 控传与接球 6 | `ball_control`控球、`speed_with_ball`持球速度、`passing_accuracy`传球准确、`passing_iq`传球判断、`passing_vision`传球视野、`hands`接球/控球可靠性 | 人物是否能胜任组织者、挡拆持球者、短顺下处理者 |
| 防守与篮板 12 | `offensive_rebound`前场板、`defensive_rebound`后场板、`interior_defense`内线防守、`perimeter_defense`外线防守、`block`盖帽、`steal`抢断、`shot_contest`干扰投篮、`lateral_quickness`横移敏捷、`pass_perception`传球预判、`defensive_consistency`防守稳定、`help_defensive_iq`协防IQ、`pick_and_roll_defensive_iq`挡拆防守IQ | 一名防守者为何适配某种战术，Coach可选择换防、护框或补篮板；不等同球员实际防守态度 |
| 运动与韧性 7 | `speed`跑速、`acceleration`加速、`vertical`弹跳、`strength`力量、`stamina`比赛耐力、`hustle`拼抢积极性、`offensive_consistency`进攻稳定 | 出场体能、跑动与球星稳定输出不同；**Stamina不是R03的实时Fatigue值** |
| 特殊/成长 2 | `intangibles`无形因素、`potential`潜力 | Intangibles在本项目有非常有限的轮换干预例外；Potential必须遮蔽，不泄露真实未来 |

**数量复核**：7+5+6+12+7+2 = **39项**。具体offset、bytes、编码、是否被本项目发布给GM见[字段与权限矩阵](../catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)，不能从这里数出“NBA2K22全部Skill Ratings恰好39种”：ATD作者2021年明确说他们编辑的还含很多别的可见属性与倾向[SRC-0073]。

### 2.1 最易引起世界扭曲的三个字段

- **Intangibles**：项目DEV15将其0x440（十进制1088）设为**仅此一字节**的特别受控轮换偏差操作（raw合法范围25–99）；这是玩家对GM业务的一项具体豁免，不等于可以操作所有其他属性，且**不能从外部资料推断其他签约/模拟/能力影响**。即使某角色要求修改，也须用户正式批准、原生身份验证、读回与回滚。
- **Potential**：项目DEV15明确`PLAYER[0x441]`原生潜力在游戏内部保持原值，但**正式发布给GM的玩家和历史新秀两库、raw/JSON中统一掩码为1**，并标`MASKED_BY_GM_WORLD_RULE`。这个1**不是实测球员潜力，更不意味着低潜**。任何玩家/教练/媒体Agent不得把潜力1用于识人、排序或叙事；同样不能绕过公开权限去读私有注入源。GM脱敏原始结构绝不能作为未来新秀直接注入源。
- **Shot IQ/Offensive Consistency与倾向**：技能评分、执行策略`RunPlays`、`Touches`、`Play Discipline`是不同字段家族。即使玩家拿到真实球员命中率，也不能反推单个原生技能的引擎真实权重。自动调用战术由K04研究，R04-B专查全部倾向。

### 2.2 OVR不是自由意志，更不是完整技能向量

OVR是游戏汇总评估，可能和位置、技能加权、Intangibles等互动。即使OVR不动，球员某项技能或体能也可能真实变化；反过来OVR上涨不保证某项指定技能上涨。R04个体职业判断需要**同批技能向量 + 比赛事实 + 对自己目标的不同解释**，不是由GM统一按OVR高低替30队和全部球员作相同选择。

## 3. 身体Durability：项目确名的16项完整子集与“25项”公共声称的区别

本机`memory_field_profile.json`已登记以下**16项部位耐久**，全属`attributes`且`rating`编码（不表示当前有完整伤病事件）。

| 身体组 | 原字段与篮球含义 |
|---|---|
| 头颈背 | `head_durability`头部、`neck_durability`颈部、`back_durability`背部 |
| 左右肩 | `left_shoulder_durability`、`right_shoulder_durability` |
| 左右肘 | `left_elbow_durability`、`right_elbow_durability` |
| 左右髋 | `left_hip_durability`、`right_hip_durability` |
| 左右膝 | `left_knee_durability`、`right_knee_durability` |
| 左右踝 | `left_ankle_durability`、`right_ankle_durability` |
| 左右脚 | `left_foot_durability`、`right_foot_durability` |
| 其他 | `misc_durability` |

**数量是3+6组左右各2+1=16。** 2K22当年ATD原作者曾称其团队覆盖约25项`durability attributes`[SRC-0073]，但没有在该帖逐条提供全部原生英文名。因此R04-A**不能凭25声称我们已确认25个名称/原生位置**。第三方同年球员页面也逐项展示上述16种[SRC-0074..0076]，为名字提供了**同版外部交叉支持**；仍不能排除该站未显示的额外字段或与其它健康机制的不同计数口径。其余与16不符的项目全部`UNKNOWN_PENDING_FULL_GAME_MENU`。

身体耐久≠当前伤病、预计恢复≠实际复赛、Stamina≠Progressive Fatigue。举例：历史名单网站对Michael Porter Jr.的背部给出的耐久数值与其他部位不同[SRC-0076]，只能说明**字段可独立取值**；绝不能拿历史网站数值作为本项目某一赛季他已经背伤的依据。**普通GM、Coach、Player Agent都不能为了提高伤病风险或塑造职业剧情直接改Durability**。

## 4. Vitals的成长时间表：Peak Start/End与Boom/Bust不能一概当“已认证PC算法”

2019–21 MyLEAGUE玩家通过`Edit Player → Vitals`观察`Peak Start`、`Peak End`；一些玩家解释成长在Peak Start前趋向提高，过Peak End后逐步退化，且会受`Potential`及全局进步/衰退滑块影响，但对年龄区间内如何变化也有疑问[SRC-0077]。**这是一种机制参照，不是我们拥有精确逐年成长公式**。

2022年**2K22 PS5 MyNBA**选秀班作者回帖显示`Boom%`、`Bust%`、潜力上下限可在球员Vitals设置，并和Peak Start/End共同影响成长结果[SRC-0078]；但其他本世代玩家曾说Boom/Bust也许是次世代新增，**PC22实际是否拥有同一菜单字段与编码需单独认证**。

同版球员导出网站可列出`Peak starts/ends`、`Minimum/Maximum potential`、`Boom/Average/Bust chance`与`Growth/Decline curve`[SRC-0074/0075]，这说明相关数据结构可以纳入R04的**研究对象清单**，并不自动证明本项目PC本世代`memory_field_profile`已注册这些字段。未来别将2K22网站某人的实际未来成长当成现在存档的必然命运。

**R04原料而非“最优成长规则”**：
- Player可以追求力量/速度/投篮等不同目标，接受输掉短期上场时间的代价；
- Coach可以重视体系/短期胜率，拒绝给新秀稳定上场；
- GM可以保留有潜力但当前低效的球员，或选择低风险即战力；
- Media可以对公开成长趋势作不同评价，但不能使用被遮蔽的真实Potential或未来Boom随机种子。

真正`LEARNING_SIGNAL`须由有来源的跨期attribute diff、真实比赛、伤病、训练来源形成；不改原生技能来兑现剧本。

## 5. 徽章与人格徽章：记录技能作用和职业态度的候选，而不是“统一人格标签”

### 5.1 四大游戏徽章家族

2K22同年玩家指南将Gameplay Badges分为：
- **Finishing** 终结/篮下；
- **Shooting** 投篮；
- **Playmaking** 传控组织；
- **Defense/Rebounding** 防守与篮板。

技能徽章有常见`Bronze/Silver/Gold/Hall of Fame`四档；无徽章记为None。本项目`training.json`亦登记`0 None;1 Bronze;2 Silver;3 Gold;4 HOF`。同年NBA2KW指南[SRC-0079]提供4大组/多个徽章解释、在**MyPLAYER**中按属性与身高解锁的条件：**MyPLAYER的徽章点获取方法不能直接搬成MyLEAGUE历史球员自然成长或导师升级的确切公式**。R03已有导师关系结构与玩家报告的自然徽章转移；R04-A只建立字段家族与将来比对方法。

一些代表性项目包括`Acrobat`、`Fearless Finisher`（终结）、`Catch & Shoot`、`Clutch Shooter`（投篮）、`Dimer`、`Floor General`（组织）、`Clamps`、`Rim Protector`（防守）；名称只说明使用领域，其适用条件、数值加成、是否当前版本真实存在须逐枚举认证。不同2K版本会有徽章改名、新增和取消，**不得把2K26的徽章树误标为2K22**。

### 5.2 人格与职业徽章必须单独保留

2K22同年ATD深度编辑社区会给球员分配`Alpha Dog`、`Friendly`、`Media Ringmaster`、`Finance Savvy`、`Extremely Confident`等Personality标签/徽章[SRC-0073/0080]，并区分技能徽章；社区球员资料有`Personality`单列。老版2K Wiki还有`Low Ego`、`High Work Ethic`、`Legendary Work Ethic`、`Keep It Real`、`Pat My Back`、`Unpredictable`等系列术语[SRC-0081]。**不同来源的标签不必然属于PC22同一枚举列表，更不证明每项参与合同报价、伤病或社交**。

球员可以因为人格徽章形成**个性假设**，但不应把它们简化成“一个徽章对应一条必然行为”。例如有`Finance Savvy`不意味着每次都拒绝降薪；`Alpha Dog`不意味着禁止其他主力控球；`Friendly`也不等于任何交易都同意。实际原生行为影响需要另看游戏说明/样本；**模型的外部长期价值取向独立存储**。R04-C专门调查人格徽章各项可见、合法值域和效果及与Loyalty/Financial Security/Play For Win的作用。

### 5.3 R04-A的徽章读取/权限契约

需要同时记录`badge_id, native_label, tier, group, source_snapshot, visibility, persistence, effect_evidence`。如果未来游戏自然成长、导师/退化导致新徽章，靠两期真实数据差分记录；若当前还没有可靠的徽章原生解码则`UNKNOWN`。项目**不允许普通经营直接写原始Badge等级给球员加强能力**，不能将`badge_slot`当外挂人格变量仓库。

### 5.4 R04-A增加全名录：80项Gameplay Badge与20个人格候选

已建立[PLAYER_BADGES_R04_A_REFERENCE.json](../catalogs/PLAYER_BADGES_R04_A_REFERENCE.json)作为**非原生ID的可检索名单**。根据2K22社区独立整理的徽章页[SRC-0082]，列出**Finishing 20、Defense/Rebounding 20、Playmaking 20、Shooting 20，共80个名称**；另外按当年ATD名单作者的真实2K22人物标签与旧NBA2K人格术语整理**20个人格徽章候选**。名单不是把20项人格全部冒充已认证PC22菜单，也不是对其原生编号的猜测。

- 全名录存`badge_label/category/2K22_source/visibility/known_native_id/status`，所有`native_2k22_pc_player_id=null`，没有PC原生内存归属就不会生成Badge执行命令；
- 同版2K22玩家、名单作者对球员Gameplay徽章和人格徽章具体组合给出了独立样例[SRC-0080]，但某些Community属性与总徽章数、版本混用的风险持续保留；
- 在R04-C逐个调查人格、契约/自我定位及NPC行为效果；在R04-D补完整原生Badge位置、具体角色权限与自然更新来源；不从`low ego`或`high work ethic`直接定义球员人生剧本。

## 6. 按字段性质给未来角色“能做什么”，而不是“应该怎么做”

| 资料/变化 | 球员的自主提议 | Coach可能的独立意见 | GM可能的独立意见 | Media可报道边界 |
|---|---|---|---|---|
| Vitals/合同/选秀与岁数 | 定义个人身份、表达长期职业阶段和目的地 | 对角色、状态、经验与战术定位持不同看法 | 依合法名单/合同评估球队方向 | 可以报道有来源的公开身高、选秀和合同；不得伪造内幕 |
| 各项篮球属性 | 请求训练某方向、接受角色转换、拒绝打法变更 | 按进攻/防守要求重新分工，也可以不听球员的 | 提供资源、交易、选秀和续约选择 | 只能对确实公开的能力评级/真实比赛表现发表评论 |
| 耐久/伤病 | 愿意保护身体、愿冒伤病风险，争取医疗选择 | 冲争冠窗口或给球员恢复机会 | 聘训练师、改变阵容、保护薪资资产 | 不把私有健康敏感数据/传闻冒充游戏公布的事实 |
| Peak/成长区间 | 优先长期发展、争取训练/出场，也可能放弃高强度 | 教练可以保守不用新秀 | 球队可以提长期合同或交易，即使误判未来 | 允许公开预测，但不阅读GM已遮蔽Potential |
| 技能/人格徽章 | 提出学习导师、改变风格、坚持角色身份 | 根据现有徽章安排战术，也可否决 | 讨论合同/人员适配 | 能讲述真实勋章与比赛事件，不自行给徽章 |
| 外部职业目标与关系 | 追求冠军/出场/金钱/城市生活/忠诚甚至拒绝条件 | 维护体系、在谈判中退让或坚持 | 协商合同/人员/建队，可能拒绝巨星额外条件 | 报道有来源的公开立场及明确标记的传闻 |

**模型保留选错的自由**：球员可为了名声或家庭地点选择损失总冠军概率；GM可误判天赋；教练可以坚持非最优打法；媒体可能批评错误但须区分`FACT`与`INFERENCE`。需要明确谈判与隐私：`ROLE_GOAL/ROLE_BELIEF/ROLE_PROMISE`不是2K原生真实数值，不能擅改Potential/Badges/人物身份或赛季事件来做涌现。

## 7. 重要技术与安全检查点

1. **只读可见 ≠ 可改**：用户在游戏Edit Player里能动原始Ratings/Vitals，不等于本项目给GM经营授权。用户历史线重力的个别能力变动是独立特例，每次需明确批准。本轮仅网页资料与GitHub文字/机读索引。
2. **已采源 ≠ 完整**：PLAYER profile的55个attr、17个contract是项目当前字段清单；游戏还有年龄/脸型/球员主宰/动作/全部倾向/人格/导师等其它模块，不按55或72就宣称该人物所有字段已捕捉。
3. **Potential去泄漏**：GM公开值1是人为遮蔽，禁止作为“Potential=1”事实让球员/媒体判断，尤其在1984–2020历史选秀里不能泄露真实未来。
4. **真实伤病vs耐久**：16项耐久不是16个正在发生的伤病；当前伤病起止依R03-G02真实来源，若无数据只`UNKNOWN`。
5. **成长不强制**：既有峰值/潜力/训练/年龄/属性都是决定自然成长的候选相互作用。没有引擎回归就不写增益率或“到30岁必退化X点”。
6. **外部状态独立**：不以名字、FaceID、Intangibles、真实Contract Preferences或闲置字节承载人格记忆。角色人物的自主目标和谈判记录未来须自己的持久表，不覆盖可能继续参加游戏模拟的Native。
7. **R04单轮边界**：人格徽章全条目/真实效应、所有倾向、个人合约偏好及各种球员与GM互动不在R04-A一次说完；分别由R04-B/C/D进行源级研究与知识目录扩充，不用审核机制阻塞下一研究轮。

## 8. 本批交付与下一窗口R04-B研究入口

**R04-A新研究**：球员职业身份/真实身份键来源、已注册**39项非耐久属性和16项部位耐久**、额外17项合同子字段的存在、PS5 MyNBA Boom/Bust与Peak年龄、四大Gameplay Badge组和人格徽章家族、自然成长反馈与游戏原生真值/角色自主记忆的隔离。以[SRC-0072..0081](../SOURCES.md)支持，**没有实机访问/玩家数据库读取**。

**R04-B下一步**：
1. 从GitHub读取本K03/K12、[R04任务书](../../development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)、[player.json](../../../config/state_io_native/player.json)、已知K04教练与Book、[R03健康攻略](K06_TRAINING_HEALTH_GROWTH.md)和[字段目录](../catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)。
2. 研究全**99个原生倾向byte**里已命名的48个与51个`UNKNOWN`，对照同版实机菜单/公开ATD/OS战术作者列表扩展到所有可见倾向类别，提供**英/中文释义、合法值、作用场景和冲突**。**项目现有命名48个不是游戏全量倾向，真实可见全表可更多**。不得未证raw与名字就启用写入。
3. 深入四个有序PlayTypes、Play Initiator、Touches、Shot IQ/Play Discipline、实际Gameplan/Coach和Freelance/Book，以及3D比赛和快Sim差别。角色有提议/拒绝权，实际本机倾向更改必须在许可范围与玩家审批下。
4. R04-C再专项研究全部Personality徽章、`Play for Win/Financial Security/Loyalty`、情绪、媒体与人物价值，R04-D完成完整字段权利图谱；**本轮没有创建任何Agent**。

**权威进度**：`R04_A_RESEARCH_PUBLISHED_WITH_FIELD_GAPS`，下一轮为`R04_B_TENDENCIES_PLAYSTYLE_RESEARCH`，尚未启动。DEV29的发布资料不代表当前player_pool里所有字段真实存在或允许写入。


---

# DEV29 R04-B — 球员行为倾向、PlayTypes、发起权与实际3D/Sim选择机制（2026-10-21）

> **阶段状态：`R04_B_RESEARCH_PUBLISHED_WITH_BEHAVIOR_GAPS`。** 继续遵守V3：游戏原料用于未来角色自主选择，而不是GM强制每人选择一条“最优倾向”。**新[99字节原生目录＋99条独立同版导出倾向目录](../catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)**，源码和来源见[SOURCES](../SOURCES.md) SRC-0083..0090，核心既有来源SRC-0031/0032、SRC-0072、K04。不采集游戏、不调能力、不生成任何执行动作。

## 9. 倾向（Tendency）究竟是什么：能力与频率选择不能混为一谈

如果球员的`3pt_shot`属性很高但`Spot Up 3PT`和`Off Screen 3PT`倾向很低，游戏可以让他**具备命中能力而较少主动选择该动作**；相反极高出手倾向、低命中属性也不保证真实每场投进球。倾向描述某种处境中AI**更愿意考虑的行动**，还受球队战术与回合情境影响；它不是实际犯规/出手/运球次数，更不是“玩家人格强制值”。

完整决策框架按现有K04分为：

`阵容角色/真实属性/徽章` → `教练POE、RunPlayTendency、ACE、Freelance` → `本队Playbook的适用战术候选` → `球员四个有序PlayTypes/Initiator` → `攻防情境中的某个Tendency候选` → `游戏3D执行或FastSim` → `比赛/事件的真实反馈`。

**顺序只是因果检查框架，不是经反编译认证的程序调用栈。** 即使技术上能写一个合法的Tendency字节，也不保证2K CPU本场从该点做动作；尤其CPU自动换阵、ACE动态战术和模拟器可能各用不同权重。球员提出训练/打法改变与GM支持的实际原生写入必须分离。

## 10. 当前真正掌握的48项倾向、51项UNKNOWN与独立导出的99种外部标签

### 10.1 本项目原生结构的事实和合法性

- `src/gm_state_io/registry.py`针对`PLAYER[0x458..0x4BA]`建立连续**99个1-byte槽**，技术字典范围`raw_range=[0,100]`。
- `config/state_io_native/player.json`的`TENDENCY_OFFSETS`精确命名**48个offset**，其余**51个`RAW_0x...`仅能保留未知身份**，`UNKNOWN_RAW_BYTE`不因本章发现相似英文就转成可写。
- Registry对48项设置`writable=true`，这是**原生动作候选的技术标志**，不等于普通GM本轮获得统一编辑球员个人偏好的许可。任何将来动作还需要字段当前批次与人员身份、球员独立同意/不同意、原项目允许的类型、**真实玩家批准**、游戏写后回读；51项不写。
- **48/51的计数是已登记的*字节*，而不是游戏可见倾向菜单数**：UI可能有更广的对象、不同编码、跨页或隐藏字段；不因99这个数字碰巧相同就把两份目录逐行对齐。

### 10.2 48项已命名原生字段完整概览（每项精确字节见JSON）

| 游戏情境 | 全部当前已命名字段（原生英文与篮球语义） |
|---|---|
| 总出手与篮下终结（14项） | `SHOT_TENDENCY`总出手候选；`DRIVING_LAYUP_TENDENCY`突破上篮；`STANDING_DUNK_TENDENCY`原地扣篮；`DRIVING_DUNK_TENDENCY`突破扣篮；`FLASHY_DUNK_TENDENCY`花式扣篮；`ALLEY_OOP_TENDENCY`空接终结；`PUTBACK_TENDENCY`补篮；`CRASH_TENDENCY`冲抢进攻篮板；`SPIN_LAYUP_TENDENCY`转身上篮；`HOP_STEP_LAYUP_TENDENCY`跳步；`EURO_STEP_LAYUP_TENDENCY`欧洲步；`FLOATER_TENDENCY`抛投；`STEP_THROUGH_SHOT_TENDENCY`跨步晃后出手；`SHOT_UNDER_BASKET_TENDENCY`篮框下出手 |
| 距离和投篮动作（15项） | `SHOT_CLOSE_TENDENCY`近距离；`SHOT_MID_RANGE_TENDENCY`中投；`SPOT_UP_SHOT_MID_RANGE`中投定点接球；`OFF_SCREEN_SHOT_MID_RANGE`绕掩护中投；`SHOT_THREE_TENDENCY`三分；`SPOT_UP_SHOT_THREE`定点三分；`OFF_SCREEN_SHOT_THREE`绕掩护三分；`CONTESTED_JUMPER_THREE`受干扰三分；`CONTESTED_JUMPER_MID_RANGE`受干扰中投；`STEPBACK_JUMPER_THREE`后撤三分；`STEPBACK_JUMPER_MID_RANGE`后撤中投；`SPIN_JUMPER_TENDENCY`转身跳投；`TRANSITION_PULL_UP_THREE`转换追身三分；`DRIVE_PULL_UP_THREE`突破急停三分；`DRIVE_PULL_UP_MID_RANGE`突破急停中投 |
| 持球、球权与战术角色（10项） | `DRIVE_TENDENCY`突破；`SPOT_UP_DRIVE_TENDENCY`定点后攻框；`OFF_SCREEN_DRIVE_TENDENCY`绕掩护后突破；`ATTACK_STRONG_ON_DRIVE`强硬攻框；`DISH_TO_OPEN_MAN_TENDENCY`分空位；`TOUCHES_TENDENCY`球权接触倾向；`POST_UP_TENDENCY`低/高位背打意愿；`ROLL_VS_POP_TENDENCY`挡拆顺下/外弹取舍；`TRANSITION_SPOT_UP`快攻中拉开接球；`PLAY_DISCIPLINE_TENDENCY`战术纪律/是否依从动作的候选 |
| 传球与防守（9项） | `FLASHY_PASS_TENDENCY`花式传球；`ALLEY_OOP_PASS_TENDENCY`空接传球；`PASS_INTERCEPTION_TENDENCY`预判传球路线；`TAKE_CHARGE_TENDENCY`造进攻犯规；`ON_BALL_STEAL_TENDENCY`持球掏抢；`CONTEST_SHOT_TENDENCY`干扰出手；`BLOCK_SHOT_TENDENCY`封盖尝试；`FOUL_TENDENCY`犯规；`HARD_FOUL_TENDENCY`强硬犯规 |

**校正与数量提示**：分组只是篮球分类而非Memory连续分区；**精确48项 =14项篮下终结 + 15项中远距离投篮 + 10项持球/球权 + 9项传球/防守。** 实际原生偏移按JSON中唯一offset定位，不依赖段落顺序。。全部字段从`player.json`直接生成机器目录，未用文字推测新的偏移。**篮球解释只是一种合理使用语义，不是固定概率函数。**

### 10.3 2K22原始导出页面提供的另外99个“有名字的可见数据”——不与原生Byte强配

[SRC-0083]是第三方2kAuction明确标记`NBA2K22 v91 / Sep 10, 2021`的历史球员快照，展示包括`### Shot`、`### Drive / Pass`、`### Defense`、`### Other tendencies`。经过逐项抄录、独立编目，当前共：

| 同版导出分组 | 已有可见英文标签数 | 典型本仓库缺名但导出有名的**候选概念** |
|---|---:|---|
| Shot（投篮+背身） | 35 | Use Glass打板、Post Shimmy/Face Up/Back Down/Aggressive Backdown、Post Hook Left/Right、Post Fade Left/Right、Up and Under、Post Stepback、Drop Step等 |
| Drive / Pass（突破、三威胁、持球、传球、单打） | 43 | Drive Right、TT Pump Fake/Jab Step/Idle/Shoot、Setup Sizeup/Hesitation/No Setup、Driving Crossover/Spin/Stepback/Half Spin/Double Cross/Behind Back/Hesi/In-and-Out/No Move、ISO vs Elite/Good/Average/Poor |
| Defense（防守） | 7 | Pass Interception、Take Charge、On-Ball Steal、Contest Shot、Block Shot、Foul、Hard Foul |
| Other tendencies（存档导出特殊区域数据） | 14 | 三分区域5档、近框3档、中投5档及篮下区域候选；例如`shot 3pt left center t` |
| **总计** | **99** | **99是该第三方导出页面的条目数，不是对`PLAYER[0x458..0x4BA]`99字节一一对应的证明** |

这是一项**比只看48个已命名字段更丰富的研究发现**：第三方同版球员资料明确给出了长串具有篮球含义的**三威胁与持球连续动作、背身左右方向、按对手防守等级的单打倾向、不同投篮区域**等可用原料。未来球员可以有偏爱右路、依赖后撤步、愿意分球、不想承担强硬犯规等风格选择，但**不能在本轮先把这些候选名称强行填入51个UNKNOWN的raw bytes**。即使同版网站输出某个具体球员的数字，仍只是第三方历史快照，与本用户游戏和未来2000年代历史选秀世界线无关。

[机读目录](../catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)将**99个原生slot**与**99个外部导出label**分别保存、来源和对象状态独立，原生已命名项有实际Offset，外部标签的`native_offset=null`，不会制造错误的一对一。

## 11. AI出手最关键的三种混淆：Touches、Shot与Play Discipline

### 11.1 同是2K22一手测试，也存在相互矛盾的解释

| 同时代观点 | 来源 | 对GM、Coach、Player真正意味着什么 |
|---|---|---|
| `Touches`主要影响没有执行固定战术的**Freelance接触球权**，教练Run Plays高时战术目标更多由教练POE、PlayTypes、Book确定 | 2021-09 jimbo3772；K04已登记SRC-0031，[SRC-0085]带完整上下文 | **合理可检验假说**，不是唯一正确函数 |
| 对全队平均降低Touches，可让Tatum/Brown之外角色得到更多进攻机会，电脑出手分配更丰富 | 2021-09 tcnumba10，同帖[SRC-0085] | **个人体验**；不能让所有球员都改50并宣称已获球员同意 |
| `Freelance Shot`/总体`Shot`主要用于模拟数据，3D投篮更多由Spot-Up/Off-Screen/Stepback/Drive Pull-Up等具体动作决定 | 2021-11 Sheitan、Evtnj直接讨论[SRC-0084] | 可能存在**快Sim专用或主要效果**，但没有官方引擎证明其对3D完全为0 |
| 2K22比赛里降低最高`Shot Tendency`后，CPU阵地出手分配改善；但别的用户改后仍只给某两个后卫叫战术 | 2021-10分歧个案[SRC-0032/0085] | **总体出手倾向可能间接作用**，不同试验方法和球队配置不能合成万能法则 |
| 老NBA2K系列中，总`Shot`主要影响Sim，临场会考虑位置分布、Playbook和角色优先级 | 2012/2018 OS不同玩家[SRC-0089/0090] | 仅**KNOWN_IN_SERIES**，不能拿老版玩家的数学式替PC22确定算法 |

**研究必须保留的独立数据维度**：`shot_in_sim`、`shot_in_cpu_vs_cpu_3D`、`shot_in_user_vs_cpu_3D`以及`team_runplays`、`touches`、`shot_tendency`、`play_discipline`、`play_type_order`、`book_compatibility`。不把任何一项直接命名“真实球权使用率”或“每100回合的绝对出手概率”。

### 11.2 为什么一种球员会在快Sim得分高、3D却几乎不持球？

四种可验证机制层——不是保证都已发生：
1. 快Sim可能用总体Shot/位置投篮倾向来分配总体FGA，3D更依赖球场位置、具体动作与球的流动；社区对这一点有不同意见。
2. 高频Run Plays、POE核心偏好、球队的有效Playbook CRC可能将动作分配给另外的球员；某前锋如果4个PlayTypes没有在本队Book里匹配的类别，可以有极高射术却没有专门为他叫的进攻战术。
3. 某人`Play Discipline`、单打倾向可能导致或抑制自行提前终结，但作用方向和游戏AI的具体状态转移尚不知；也可能因为防守换防、赛程或个人技能等别的因素无法执行。
4. 当且仅当有真实GameID、各球员出场、FGA/3PA、所跑回合、Playbook与当前coach设置，才能对“为什么没参与”形成有事实约束的解释；若这些数据没有捕获，就只是角色自己的**信念假说**。

## 12. PlayTypes四槽 + Initiator一位：不是五个独立战术或教练全权控制

本项目Registry使用：
- `playtype.slot1..4`：从`PLAYER[0x168]`至`0x169`的4个**半字节（4bit）**，有顺序；每项0..15。**四槽有序的事实可认证，1号总比2号多被调用多少次仍UNKNOWN**。
- `playtype.initiator`：`PLAYER[0x16A]`中`start_bit=2,width=1`，布尔原生候选，表示是否具备Play Initiator身份；*候选描述不等于此布尔值使球员固定变成持球后卫*。
- 16个项目enum逐一是：`None(0)`、`Isolation(1)`、`Isolation Point(2)`、`Isolation Wing(3)`、`P&R Ball Handler(4)`、`P&R Point(5)`、`P&R Wing(6)`、`P&R Roll Man(7)`、`Post Up Low(8)`、`Post Up High(9)`、`Guard Post Up(10)`、`Cutter(11)`、`Handoff Receiver(12)`、`Handoff Passer(13)`、`Mid Range(14)`、`3 PT(15)`。

要避免三个错误映射：
- `player.4 PlayTypes`不等于`球队Book里68条CRC`，也不等于`12类Play目录`。一条有P&R类型的CRC可以有多个发起/终结角色，先查实际类型匹配才谈战术频率。
- `playtype.initiator=true`不等于`Touches=100`，更不等于教练`RunPlayTendency=100`；**角色可以是发起人，却在球队book没有对应球员目标动作**。
- 2021年2K22导出资料同时列出了`Play initiator = Yes/No`与4个类型，例如Trae Young标Yes、Tatum标No，各自仍有4个战术类型[SRC-0086/0087]。**只作为同版外部历史快照的字段独立性佐证**，不代表本项目当前球员值，也不能从字面将外站的“Three-point screens”与本项目`3 PT(15)`宣布为同一原生enum。

### 12.1 Roll vs Pop与P&R Roll Man不同：球员可以想要另一种角色

`P&R Roll Man`是**球员战术类别**，`ROLL_VS_POP_TENDENCY`是原生Player Tendency中**掩护后顺下/外弹选择的倾向**，`FIST...`则是球队Book具体CRC；三个对象并不互相替代。一个可以外弹但PlayTypes/Book没有适配动作的内线，教练不会因为修改一个`ROLL_VS_POP`就自然创造出所有适合他的三分战术。未来中锋球员可以**要求**扮演射手型内线，教练可反对，GM可补外线教练体系或不同人员；技能成长仍由游戏自身决定、不能因为人物立志转型直接增加三分能力。

## 13. 三威胁、持球运球、单打等级与区域投篮：新增行动原料的具体篮球意义

同版2kAuction快照列出以下在项目48个命名字段**尚未完整涵盖**的行为候选[SRC-0083]：

- **三威胁`TT Pump Fake / Jab Step / Shoot / Idle`**：拿球后假投、试探步、就地投、暂不发动。它们可以塑造谨慎侧翼、喜欢试探的得分手与快速决策球员，但这些名字**不等于已知原生raw位置**。
- **持球启动`Setup Sizeup / Hesitation / No Setup`**与**突破动作`Driving Crossover/Spin/Step Back/Half Spin/Double Cross/Behind Back/Hesi/In-and-Out/No Driving Move`**：拿球后用何种节奏摆脱守方。球员可能偏爱持球创造，教练可能觉得拖慢进攻；外部模型可以形成不同价值判断，而不修改运控属性。
- **单打对手质量`vs Elite / Good / Average / Poor`**：对不同防守等级选择单打的候选，这是非常适合构成**“球员遇到怎样的防守人愿不愿独立处理”**的原料；具体游戏采用什么防守评价阈值/哪一项属性、是否直接参与3D仍UNKNOWN。
- **背身动作/方向`Post Hook Left/Right / Fade Left/Right / Face Up / Aggressive Backdown / Drop Step`**：细分左/右路、转身脚步和面对不同体型防守者的自主动手段。
- **投篮落点**：`Other tendencies`的三分5区、中投5区、近框3区和篮下条目，是研究球员更偏爱左底角或弧顶接球的潜在输入，但不能等同于R01真实Shot Chart，**导出倾向只是预设、真实出手热区必须看场上数据**。
- **外观动作包/Animations**仍是另一家族：球员的实际签名运球包、投篮动作、扣篮包在导出页单独存在；不能用有`Driving Step Back`倾向就推断一定拥有指定的Curry动画或跳投速度。球员人格可以珍视个人标志性动作，但是否允许修改外观动作需项目另行审核。

**关于动作倾向的0/99**：同年Sheitan认为极端值让电脑选择过于机械，提出按分位数分配人物行为[SRC-0084]。这属于**社区名单设计者的一种建模哲学**，不是游戏官方0/99是否有概率绝对性的数学证明。未来自由角色系统可以选择极端专精、也允许不合理偏好；DEV29不能把“建议避免99”变成强制球员人格趋同。

## 14. 同样的Tendency在三种执行方式下如何判定结果

| 游戏执行方式 | 实际可研究的数据 | 什么证据不能复用 | 对多角色的意义 |
|---|---|---|---|
| `FAST_SIM` 快速模拟 | 真实赛季FGA/3PA/回合、分钟、出场和世界滑块（若已采） | 不把UI里具体后撤步出手偏好等同已被模拟器逐帧使用 | 球员对自己的数据表现可能不满，Coach/GM对战略影响的解释可能互相争执 |
| `CPU_VS_CPU_RENDERED` CPU观战 | 同一场具体持球者、动作时点、传球路径、实际所跑战术的录像/追踪，真实Box | 不把某人外站历史“Shot=90”当本局主动球权 | 教练可能观察到球员偏离战术、球员反驳是防守改变了选择 |
| `USER_VS_CPU_RENDERED` 玩家打AI | AI一方真实CPU行为、人物移动、手动/自动Playcalling区分 | 不能用玩家直接手控的投篮当角色原生AI自主决定 | 球员独立偏好只能研究AI控制的一侧，用户操控需另标 |
| `COACH_MENU_ONLY` 静态/临场菜单 | 当前coach/Playtype/倾向可选读数、数据批次 | **不当作真正执行过的战术或球权** | 角色有了可选择的对象，但没有真实结果前需提出更多信息请求 |

任何“改变Touches会使A每场少投5次”的定量结论，必须同保存、版本、阵容、教练、Book、比赛模式、赛程/上场、球员已批准意向一致做多次对比；本轮没有此类验证，所以数值效应保持`UNQUANTIFIED`。**角色可以做错决定而后悔，但世界日志不能伪造已经发生的比赛事件。**

## 15. 交给角色的真实选择菜单，而不是全联盟统一倾向处方

| 情境 | 可真实观察的状态（须来源/权限） | Player自由选择 | Coach、GM可独立回答 | Media能够发布的事实及争议 |
|---|---|---|---|---|
| 高使用率核心与低参与替补 | 真实FGA、分钟、PlayTypes、Book和Coach现值、批次 | 维持单打、要求更多/更少持球、改无球动作、拒绝团队期望 | Coach可支持单核、要求分享球；GM可增援或拒绝；同意之外不得随意改普通倾向 | 公开真实出手与胜负；不能把未知内心“自私”当原生客观属性 |
| 中锋希望转型外弹 | 3PT属性/真实3PA，P&R Roll Man类别、Roll vs Pop、训练计划 | 要求Outside训练/改战术角色或保持内线打法 | Coach提出战术书和空间要求；GM有成本约束 | 评论外弹选择与球队效率，不能宣布3PT能力自动上涨 |
| 喜欢高风险抢断的球员 | `ON_BALL_STEAL`、`FOUL`、真实犯规/断球（有批次才可用） | 维持积极压迫、同意减少掏抢、或拒绝教练要求 | 教练权衡犯规/防守体系；GM可换防守人员 | 不能根据一个倾向值报道“球员已故意伤害对手” |
| 战术纪律低的天赋球员 | Play Discipline、Touches、真实战术执行片段（缺失则UNKNOWN） | 想保持创造空间、接受教练条件、在不满时要求交易 | 教练能争论自由与体系的边界；GM可支援或换教练 | 只能就公开赛后采访/比赛事实发表评论 |
| 侧翼不想改变投篮动作 | 签名动画包与实际shot attempt（如果已采） | 拒绝替换动作、要求个人训练而非换习惯 | 教练可调整围绕其动作的战术，也可否决球权诉求 | 个体风格与表现可公开评价，私有承诺只能在本人允许后披露 |

**ROLES与权限**：未来`Player.PROPOSE/COUNTER/REJECT`和`Coach.PROPOSE/REJECT`只是可供人格系统推理的行为词汇，**不是NBA2K22内置球员同意API**。球员倾向本身可能还影响模拟比赛，所以**不允许把这些仍有原生效果的raw bytes重新用来保存秘密人格、忠诚或承诺**。普通球员能力/Potential/徽章仍不可编辑；倾向/PlayTypes若未来允许经两角色协商更新，仍须**真实玩家批准**及现有合法原生执行边界。

## 16. R04-B本轮结论与R04-C直接研究断点

**本轮已发表**：
- 真实99个原生倾向byte：48已经命名，51未知保留只读；
- 另外99项**来自NBA2K22 2021快照的具名倾向标签**，完整分组/排序和字段来源独立入库，**不按“99=99”擅自赋raw offset**；
- 个人四有序PlayTypes（原生0..15）与1 bit Initiator、12战术类别、球队本队Playbook、Coach/ACE/Run Plays相互关系；
- 同年玩家对Touches、Shot、Play Discipline、3D vs Fast Sim的冲突实测及不承诺公式的解释；
- 三威胁/持球、单打对位、背身左右方向、Shot区域分布等未完整映射的候选行为；
- 四类人物能观察、提议、拒绝、长期学习什么，保持隐私和玩家原生写入权限。

**R04-B仍未完成的对象**：目标PC22无模组完整Edit Player→Tendencies的**具体像素顺序及作用类型**、99外站字段到99原生byte的一对一对照、所有动作具体CPU触发概率、命中/模拟器的区分、人员当期真实动态读值、换教练/换Book后自动调用的可重复案例。这些全部`UNKNOWN`、必要时未来DEV28定向只读；**不因没视频就停止后续R04-C**。

**R04-C下一任务**：独立深入Player Agency：`Loyalty/Play For Win/Financial Security`、全部真正存在的人格徽章、士气/合同/球队角色/明星议价、医疗和训练自主权；区分2K原生意愿（如果存在且有效）与外部人物永久记忆、职业目标、反报价、拒绝与媒体叙事。R04-D再综合完整权限图谱及R05市场接口。**后续研究不由本轮自动启动，不由DEV29执行独立审核**。

### R04-B原始来源编号与恢复码（供下一轮直接检索）

本轮研究事实的**逐项来源键**如下，详情及平台/模式限制均在[SOURCES](../SOURCES.md)：
- **SRC-0083**：NBA2K22 2021历史人物导出的99个具名倾向标签（独立于Native 99 bytes）。
- **SRC-0084**：Sheitan/Evtnj讨论三威胁、Shot/Freelance与模拟/3D差别。
- **SRC-0085**：2021年不同2K22玩家对Touches/Shot/教练叫战术产生矛盾结论。
- **SRC-0086**：同版Trae Young的Initiator=Yes及四PlayTypes归档字段。
- **SRC-0087**：同版Tatum的Initiator=No但仍有四PlayTypes归档字段。
- **SRC-0088**：同版MyLEAGUE玩家的个人倾向编辑与全球模拟滑块各自独立。
- **SRC-0089**：2012年旧系列总体Shot作用机制争论，仅KNOWN_IN_SERIES。
- **SRC-0090**：2021年的动作倾向编辑建议与部分2K19经验必须分开。

**正式断点**：`R04_B_RESEARCH_PUBLISHED_WITH_BEHAVIOR_GAPS`；**下一轮`R04_C_PLAYER_MOTIVATIONS_PERSONALITY_RESEARCH`，尚未启动**。下一轮调查人格徽章、Loyalty/Financial Security/Play for Win、情绪、球队/球员谈判与媒体知情范围；**DEV29只研究和发布原料，不担任独立审核、不开发Agent或启动原生写入**。

---

# DEV29 R04-C — 合同动机、人格徽章、士气、职业自主与角色谈判（2026-10-21）

> **状态：R04_C_RESEARCH_PUBLISHED_WITH_NATIVE_MOTIVATION_GAPS。** 本轮提供**角色决策的事实、可选空间、机制代价与权限原料**，而不是培养一个自动执行“最优签约”的GM，也不开发Player Agent。主证据SRC-0091..0105，机读细目见[人物动机及人格权利研究目录](../catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)。依据用户确认，2K20/2K22次世代终极联盟的合同、人物机制可以优先参考；具体本机PC22原生位址、玩家可见页面、执行时序、真实写入权仍单独分级。R04-D统一字段双语义与互动总图谱，R05再研究外部职业谈判与薪资帽全流程。

## 17. 游戏原生职业偏好和外部角色目标，是两个不同层次

NBA2K22同版2021年球员档案[SRC-0093]直接将`Loyalty`、`Playing for a Winner`、`Financial Security`放在`Motivations`（职业动机）中，网页说明为**0–100偏好评分**。同版2K22 ATD球员名单作者[SRC-0092]也**真实编辑了三个字段**，以表达老将愿意为了争冠接受较低合同、另一类球员更重视金钱的**自定义名单设计意图**。这些是准确的**字段存在和可能意义**证据；没有哪个来源证明本机游戏把`value=80`当成某项职业谈判的直接“80%概率”或绝对阈值。

| 原始游戏职业动机 | 中文语义与竞争性利益 | 哪些决策值得观察 | 当前PC22本机真实性边界 |
|---|---|---|---|
| `Loyalty` | 忠诚/延续原队关系；不等于“绝不要求交易” | 是否愿意续约、是否拒绝原队低价、是否测试自由市场、转会后是否形成新归属 | 2K22外部归档有0–100字段；**Profile当前无具名native offset；跨季原生是否自动变化仍UNKNOWN** |
| `Playing for a Winner`（也见`Play For Winner`、`Play for Win`） | 对争冠与竞争机会的追求；不等于“顶级球队可随意压价” | 愿接受冠军队角色/薪资折让，还是为了个人地位选择弱队；球队战绩及冠军窗口如何改变主观信念 | 归档字段0–100；**不清楚具体CPU接受权重、争冠判断窗口** |
| `Financial Security`（旧文也称Financial Importance） | 收入稳定、合同期限与保障的重要性；不等于税务偏好 `Finance Savvy` | 年薪、总保障、球员选项、合同年限、续约与市场竞价的取舍 | 归档字段0–100；**不等于合同金额或已证最低接受报价** |

同版导出例子：归档Joel Embiid数值`80/15/70`、Tyrese Haliburton`100/50/30`[SRC-0093]。它们只是**当年第三方2K22快照的示例，绝不是玩家当前存档/任何历史选秀世界线的已认证动机**；不能因为Haliburton显示100忠诚就宣称他永不离队。不同三个数值也不要求合计100，因为它们在网站作为**独立0–100评分**而非统一比例权重。

### 17.1 玩家社区实验与不能推广的“签约公式”

2015年NBA2K15 MyGM论坛[SRC-0096]曾以多个`Loyalty/Play for Winner/Financial Security`组合观察LeBron、Tim Duncan等是否续约、测试FA、争冠后留下；作者尝试固定薪资和合同年限。结果中有版本内正向相关现象，但**作者与其他回复对哪个变量主导、同值是否可靠出现不同看法**。这些属旧系列探索，**不是NBA2K22 PC引擎反编译结果**。

2020年MyLeague发帖者[SRC-0097]也报告Giannis在两次试跑中加盟完全不同的球队，回复称三项动机及大小市场、天气、税务可能有一点影响，而不是确定结果。这支持未来球员有**不同情境下的意外去留**，而非硬编码`Loyalty>70必留`。

**不可取的写法**：`if play_for_win >= 80 then max_salary_discount=20%`、`finance_savvy => must choose Florida`、`loyalty 99 => never ask trade`。游戏没有向本次研究提供这些规则。**外部模型完全可以与原生参考偏好不同，权衡当期承诺并作出自己的选择**；不能通过事先改原生动机分值确保该球员答应。

## 18. 人格徽章有哪些可核实的原生机制？

### 18.1 三项有明确开发人员解释的自由球员附加偏好

NBA2K20**开发说明**[SRC-0091]把以下称为针对顶薪球员的*附加人格徽章*，用于在多支球队都给顶薪时使转会更符合个别偏好：

| 徽章原文 | 中文意图 | 开发者说明确切层级 | 不能推导 |
|---|---|---|---|
| `Media Ringmaster` | 偏爱大城市和更高媒体曝光 | 同等顶薪条件下，大市场的竞争力可能上升 | 不代表必须去纽约/洛杉矶，也不授权媒体读取个人谈判秘密 |
| `Warm Weather Fan` | 偏爱温暖气候 | 城市气候属于球员环境偏好 | 不能只凭一项气候让球员打折1000万美元 |
| `Finance Savvy` | 注重居住地税务负担 | 当名义薪酬近似时，低税环境的吸引力可能增强 | **不等于Financial Security**；税务影响不等于年薪必须低于某值 |

官方明确将其形容为**tiebreaker性质**，而不是“在任何条件下都胜过薪水的决定论”。这篇是NBA2K20开发文本；2021的2K22球员编辑团队同样讨论人格徽章，但这**不能自动证明这三项在PC22所有模拟路径的权重完全沿用**。下一轮R04-D可将其作为有效跨代机制原料、目标本机native offset保持UNKNOWN。

### 18.2 其它人格/心理/训练徽章的来源层级

现有[20个人格候选](../catalogs/PLAYER_BADGES_R04_A_REFERENCE.json)加本轮发现的`Warm Weather Fan`共**21个候选英文标签**。它们需要分三个证据等级：
- **开发者具体解释的自由球员偏好**：上面3项 `Media Ringmaster/Warm Weather Fan/Finance Savvy`（2K20官方系列机制）
- **有同版或跨代实际“人格徽章”栏目支持的标签**：`Alpha Dog`、`Friendly`、`Unpredictable`、`Legendary Work Ethic`、`Expressive`、`Pat My Back`、`Enforcer` 等，球员编辑社区与旧版百科都有显示/释义[SRC-0098/0099/0105]，但**单项效果不应认定已精确量化**
- **旧版词条或社区创作的候选**：`All-Time Great`、`Low Ego`、`Reserved`、`Laid Back`、`On Court Coach`、`Clutch Performer`等，需要逐一认证PC22是否仍在“人格徽章”栏目，以及它们是否属于这个类别、是否对场上/模拟有实际作用；**不是21个全部本机原生字段均已确认**

NBA2KW跨版本词条[SRC-0098]将Alpha Dog解释为遇到队友冷手时鼓舞球队，也有旧版文中称其可临场提升部分属性。这个旧版描述**不等于NBA2K22 PC技能+5公式**，普通经营也不会据此授予球员Alpha Dog。Friendly描述外向合群；Unpredictable可能表现不稳定；Legendary Work Ethic表达训练投入[SRC-0098]。这些可给未来人物的**起始叙事线索**，但模型有能力违背单个标签刻板印象，且必须保留数据来源；不能把“Friendly”翻译成“任何交易都同意”。

ATD的2021年原帖[SRC-0092/0103]说人格徽章可能触发其`MyNBA Event Generator`中的**200余个自制事件**。**这是名单作者的外部事件生成器及配套文档，不是NBA2K22游戏原生自带200种人格剧情API。** 我们未来外部多角色世界可以参考“事件由角色性格影响”的思想，但必须明确自建来源、公开报道范围与真实比赛事实不混用。

### 18.3 荣誉、人格、徽章级别和心愿不可互换

- 技能徽章按铜/银/金/HOF读数，只说明游戏能力触发条件的候选，与后续自然成长/导师有关（R04-A/R03）。
- 人格徽章不是“有高贵人格=有更高篮球能力”的评分，也**未证明全部具0..4四阶等级**。机读目录将人格徽章标为`NO_TIER_ASSUMED`。
- 原生心理/职业偏好分值`Loyalty/Financial Security/Playing for a Winner`是另三类独立数字，不等于人格徽章ID，亦不是外部人物的`career_goal`。
- 外部人物的愿望与信任/记忆可能随事件改变；**即使原生分数保持不变，外部角色也可以改变决定**。是否同步原生值，需要未来证明游戏会如何使用该字段并获得人物/真人两级批准。

## 19. 士气Morale、化学反应Chemistry、团队角色Role和职业决定的复杂关系

### 19.1 官方机制：球员士气与团队化学反应不只是一个静态数字

NBA2K20开发说明[SRC-0091]正式写出：Morale与Team Chemistry公式被更新，**每天向各自平衡点变化**，球队成员的Work Ethic差异也会影响团队平衡。代表游戏本身有时间演化和队友间关联，而不是仅凭胜败即时设定0或100。

- `Player Morale`（个人当前满意/情绪）与`Team Chemistry`（集体协作氛围）是**不同对象**，不可只看一人抱怨就认定整队已崩溃；玩家反馈表明关闭某个Chemistry效果不等于禁掉Morale驱动[SRC-0100]。
- 球员角色`Star / Starter / Sixth Man / Role Player / Bench Warmer / Prospect`来自系列MyGM Front Office类文献[SRC-0105]，可以作为**角色要求或协商菜单概念**，但PC22本世代完整Role设置与对应模式是否同名必须另证。
- 球员可能抱怨上场机会、球队战绩、队友地位、合同承诺或教练战术。上场分钟**游戏AI可能重分配，项目明确不锁分钟**；未来角色可以请求`more minutes`但真实GM不因此拥有绝对分钟锁定接口。
- NBA2K22 PS4 MyLEAGUE同版玩家[SRC-0094]给Oshae Brissett首发及队内第三得分地位、调整相关士气/忠诚与争冠参数，仍出现球员想离队。这是**单用户的一手矛盾结果**，并非2K22“总有bug”定论；它说明角色不满并不必然能由某一条件消除。

**再强调因果**：`morale score`、`contract thought`、`actual resign_acceptance`、`actual trade_request_event`是**四种不同类型的记录**。外部模型猜“球员在闹情绪”不是游戏已实际出现拒绝续约；系统应记录是谁看见、什么时候看见、是否通过真实赛季推进确认。

### 19.2 竞技评分、人物心态和事件不是一个事实对象

2K20玩家[SRC-0100]认为低Morale伴随队伍评级红/绿箭头、有人拒绝续约；但某些人把游戏“士气调节”叙述成角色能力上涨/下降，有其它玩家试图通过编辑Loyalty却无法稳定解决。**我们不能由游戏里的总评箭头反推出哪个原始球员Ability被永久改动**：必须区分 `NATIVE_ATTRIBUTE_BASELINE`、`EFFECTIVE_RATING_MODIFIER`、`ROLE_BELIEF`。普通经营永远不把“更开心”通过直接加能力来落实。

2K22**次世代**官方MySTAFF描述`Sports Psych`岗位与团队心理/士气/化学反应有关[SRC-0104]。此功能与我们已有R03的健康员工研究相互支持，但PC22是否有同等独立岗位仍不当作已证。

## 20. 职业谈判的实际窗口：能提条件，不等于现在有原生NPC谈判Agent

| 时点 | 游戏可研究的事实与合法条件 | 球员的自主利益与可选回应 | GM/Coach能提出的不同条件 | 当前研究可认证程度 |
|---|---|---|---|---|
| 合同期常规赛 | 已签合同、剩余年数、工资、选项、实际球队与上场机会 | 想留下、表达更大角色、要求交易、保持沉默 | 提供战术任务/训练资源、预告续约、拒绝提前改变阵容 | 17项Contract已注册；**真实玩家当前Morale/私有谈判尚未提供** |
| 提前续约/谈判 | extension eligibility、Bird年数、合同金额/时长、球队资金及是否有原生谈判 | 提出薪水/年限/球员选项/不交易、拒绝、希望先测试市场 | GM报价或撤回；Coach可承诺角色，但不保证精确分钟 | 游戏合同字段存在，**玩家/球队的外部议价协议仍是未来机制，不是2K22NPC API** |
| 合同到期和自由市场 | UFA/RFA、球队报价、名义薪资、争冠环境、合同选项、真实市场阶段 | 收集多个报价、测试市场、提出非金钱条件、反报价/拒绝 | 不同GM独立竞争、评估薪资帽和保障机会 | 2K22玩家[SRC-0095]报告AI报价与球员要求存在不对称，不能当确定报价公式 |
| 受限球员与QO | 优先签约权、qualifying offer、匹配与Moratorium日期等 | 表达续约/测试市场意愿，团队仍受法律与2K规则约束 | GM根据合法资格报价/匹配 | 同年2K22玩家报告QO覆盖问题[SRC-0101]；**不能把提交后“显示接受”直接当持久合同结果** |
| 巨星指定目标球队与条件 | 球队薪资、阵容、教练承诺、球员现有合同、可用资产、真实同意状态 | 要求先补强/改变体系/交易队友或选择其它队、拒绝续谈 | 对方球队可以让步、反条件或直接拒绝；对手球队也能独立竞价 | **外部角色世界的行为能力目录**，不是NBA2K22原生“先交易X才能加盟”UI按钮 |

**与本项目已有外挂的关系**：交易双方协议与休赛期竞价机制要遵守现有DEV14/合同执行合同和实际职业时间窗口，不因球员Agent提出条件便立即写入游戏。**角色谈判有意向、接受、拒绝三层；真实玩家另有最终游戏写入批准；执行后还需readback和跨期验证**。未完备的薪资帽/Bird/RFA/交易细节交DEV29 R05研究，不由R04-C编造。

**实际bug/不确定性不可消灭为“NPC人格”**：2022年MyNBA玩家抱怨别队报出低于球员要价很多的合同反而被接受、自家出价却遭拒，另有长期未签的80+球员[SRC-0095]。该报告可说明原生报价系统不够透明或存在BUG，不能从这份反常结果倒推其真实“贪财”“不忠诚”或隐藏定价规则。

## 21. 角色的自由选择需要可知范围、拒绝与结果，而不是把原生字段重新当人格引擎

### 21.1 四角色信息、选择、拒绝与可学习的真实反馈

| 原料 | 谁可观察 | 自由选择与互相冲突 | 外部后果与原生边界 |
|---|---|---|---|
| 原生职业偏好三项 | 游戏原生真正采集且授权的角色；目前第三方历史例子仅供研究 | 球员认同、反思或违背自己的既有金钱/冠军/忠诚取向；各GM可自由报价、拒绝 | 三项字段参与游戏引擎的可能性存在，**不得作为外部SQL人格仓库的存储位** |
| 人格徽章 | 真正具有可验证badge+角色访问权时可见；媒体只看公开资料 | 球员可以选择适应球队，也可拒绝被贴的标签；教练/GM可能误解 | 旧版自由市场tie-break意义≠当前本机“必去某队” |
| 角色/士气/化学反应 | 真正game_date的球队/个人状态，非历史网页数值 | 争取首发或休息、更强战术参与、交易/留队；Coach可拒绝 | 原生可用性与外部关系可同时变化，**不能用模型不满伪造游戏Trade Request事件** |
| 合同与报价 | 球员可看自己的条款，GM看合法可竞争合同/报价，媒体只看已公开消息 | 接受、反报价、要求球员选项/不交易、测试FA，或主动承受工资损失 | 真实写入必须经过合法合同执行器和真人审批；无执行时只保留外部意向 |
| 训练/伤病风险与职业目标 | R03已登记的真实训练/伤情（按权限）；未知则要求补证 | 球员保护健康或承担风险；教练为争冠坚持投入，GM考虑资金 | 模型目标不是原生Ability/Potential/Badge修改许可证；应允许失败与改变主意 |
| 媒体公开形象 | 已发生比赛、已公布合同、采访/球队发布的公告 | 公开表态、沉默、选择性披露，媒体各有分析与批评 | 外部谣言应显示`RUMOR/OPINION`，不得把未公开谈判和隐私健康状态当事实 |

人格模拟最终由各角色模型读取自己有权获取的实时游戏资料与历史记忆后自由判断。本指南**不规定**“忠诚低就一定离队”“忠诚高不能转会”“所有巨星都偏爱戒指”“财务安全必大合同”等硬策略。每个Agent可以改变自身观点，不需要被强制导向联盟最优解；但**世界物理、合同有效性、原生字段权限和玩家批准仍是硬边界**。

### 21.2 角色选择结果分层（研究用标签，不是新增API）

`GAME_NATIVE_OBSERVED`（有来源的游戏事实）→ `ROLE_INTERPRETATION_PRIVATE`（角色可犯错的主观看法）→ `ROLE_NEGOTIATION_INTENT`（要约、条件、反报价、拒绝）→ `APPROVAL_PENDING`（玩家批准前）→ `APPROVED_EXECUTED_NATIVE`（实际执行并回读）→ `WORLD_FEEDBACK`（真实世界发生的未来事件）。

其中**“角色同意”不能充当真实玩家授权**。此前谈判的某一条件可以是⚠️`NOT_NATIVE_ACTION`，例如球员“承诺每场出手20次”；教练不能保证游戏AI会尊重细致出手或精确分钟，玩家也不能靠直接改能力/Badge替角色兑现。

## 22. PC22本机真正已掌握的资料和R04-C保留UNKNOWN

| 对象 | 研究确知 | 目前**没有**的证据 |
|---|---|---|
| 三项Motivations | 2K22归档页面显示原始英文及0–100范围，ATD作者同年操作过 | **当前本机native offset、完整PC22 menu、当前source_batch人物分值、跨季自然变化规则、三个偏好如何直接加权FA的源码** |
| 人格徽章21个候选 | 2K20官方3项自由市场人格偏好、其他部分有2K系列词条及玩家/自定义名单证据 | **21项不是PC22确证全集；各项本机native ID、等级、具体场上/合同/事件触发不完整** |
| Morale/Chemistry | 2K20官方日平衡机制与工作态度关联、2K22 PS4个案 | **目标PC22当前Morale/Team Chemistry稳定读取、2K22 PC准确日更新公式、合同拒绝概率** |
| 球员角色/训练/承诺 | 历代MyGM/MyLEAGUE角色和2K22训练字段，可成为自主要求目录 | **PC22是否支持所有原生承诺NPC按钮、准确角色承诺反馈、个人训练自主拒绝的游戏内接口** |
| 合同/自由市场 | 本机17项合同profile字段，项目有单独交易与休赛期竞价业务 | **本研究未运行真实市场报价，AI合同行为与双向谈判独立原生API不能假称已实现** |

**研究原则修正**：NBA2K20–23终极联盟跨代的**自由市场决策原料可积极复用**，但是原生字段不明时仍应保留`PC22_OFFSET_UNKNOWN`；没有必要因此停止人格研究。既有20个人格候选名单遗漏的`Warm Weather Fan`已补入**R04-C独立目录（21名）**，原R04-A徽章列表仍保留其第一批历史状态，不伪装R04-A当时已有21。

## 23. R04-D下一轮研究入口与本轮边界

R04-C本次交付：完整三项合同职业动机及准确原文、开放0–100偏好证据和老版实验分歧、21个人格Badge候选含官方确认的3项自由市场tie-break、2K20/22士气/化学反应/团队角色、本人诉求、报价竞争/不同模式BUG、训练和伤病自主权，以及**不同角色可以提出/拒绝/后悔的选择空间**。结构化目录见[R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json](../catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)。

**下一轮R04-D**：统一`PLAYER_FIELD_AND_RIGHTS_MATRIX.json`里的原生/候选字段与R04-A/B/C双语义、跨批动态可见性、原生合法事务/角色同意和真人批准；补`catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md`（人物⇄GM⇄Coach⇄Media，含条件加盟、团队换帅、倾向谈判、训练/伤情拒绝等）。整合完整交互后R04研究结束，再交R05劳资/财务/交易/休赛期研究。**不由DEV29负责独立审核**，也不启动DEV28、Codex、外部Agent或游戏运行/存档写入。

---

# DEV29 R04-D — 全球员数据双语义与Player/GM/Coach/Media世界交接（2026-10-21）

> `R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`：R04-A/B/C/D所有**研究批次**已完成。不是说NBA2K22 PC目标菜单和原生字段全部读写已认证，也不代表多智能体软件系统已建成。用户明确将独立审核交给其它模型；DEV29只负责研究发布。完整可检索[PLAYER_AGENT_INTERACTION_ATLAS.md](../catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)包含8个假设互动场景；[109项双语义侧表](../catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)为逐字段证据附录。本轮新增SRC-0106..0113参见[SOURCES](../SOURCES.md)。

## 24. 四个角色不是同一个GM的四种叙述角度

| 角色 | 实际可用的世界输入（必须按真实已发布批次、信息权限） | 自主可考虑的行动 | 应当能够拒绝什么 | 特别禁止 |
|---|---|---|---|---|
| 球员Player | 自己的身份、已知合同、真实训练和比赛、经过披露的伤停与外部私人目标 | 提出留队/申请交易/要求角色/选训练、考虑不同报价与目标城市 | 不合适的教练角色、球队报价、采访、透支训练、导师人选 | 不能自己直接把能力、潜力、徽章、耐久改高或制造伤病事件 |
| GM | 有权查看的球员、球队、薪资、资产、比赛与教练环境；收到的公开/定向请求 | 独立报价、重建、守成、出让核心、拒绝明星条件，容忍失败 | 球员不现实的合约条件、Coach昂贵阵容要求、媒体压力 | 不读取球员未披露的私有思想或被遮蔽真Potential，不把任何模型同意当真人批准 |
| Coach | 真正可见的当期球员能力/出勤与K04战术、Book、训练控制及游戏反馈 | 选择体系/用人哲学、提出训练目标、不同PlayTypes/Freelance建议 | GM的强制战术偏好、球员的持球要求、媒体角色扮演 | 不承诺游戏AI精确轮换分钟/每场出手数，不改能力等级 |
| Media | 有出处且已经公开的比赛、合同、采访声明、历史线已有事件 | 调查采访、发表可验证评论、争论、预测、撤回报道 | 采访不必得到回应；可拒绝未经查证的“消息源” | 不偷窥私有健康/合同条件/外部人物信念，也不发表未执行的交易为已成交 |

**重要模式警告**：2K20的开发者确实谈到MyGM Action Points、chit-chat、任务、GM—Coach信任与访问Coach Gameplan的关系门槛；这不是PC22离线MyLEAGUE现有的可执行对话接口。2K20也有明确的**MyLEAGUE级别**士气、化学反应、自由球员人格偏好，二者可以用作跨系列机制背景，但要分清模式[SRC-0106/0107]。次世代MyNBA融合了一部分MyGM与MyLEAGUE行为，特定Conditional Coaching并未在本机注册为原生PC22菜单[SRC-0108/0109]。

## 25. 双语义：一个球员资料字段不能同时扮演游戏引擎状态与外挂人格数据库

每个已收录球员字段都有两个需要清晰分隔的含义：

1. **原生游戏语义**：游戏将它读作篮球技能、合同、球员战术频率、人格标签、身体耐久、成长潜力或真实世界记录；引擎可能在比赛/模拟中继续使用。
2. **外部角色语义**：未来模型可以把当前和历史合法读数作为理解人格、环境与行动后果的*信息来源*；模型形成的长期目标、信念、承诺和拒绝历史须另存外部人物世界，不能写回本来具有游戏作用的字段来“省表”。

[109项字段与权利矩阵](../catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)已有**72项本项目静态Profile注册字段（55Attributes含16Durability+17Contract）**，以及**37个尚未映射的候选人物信息字段**。本轮[109行双语义侧表](../catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)逐项增补如下交接性质，不改变原有Registry定义：

| 必备项 | 应该记录什么 | 错误示例 |
|---|---|---|
| `native_game_semantic / mechanism_grade` | 真实篮球/合同/档案含义及是否有游戏/项目/社区证据 | 把Intangibles、Loyalty或未用的byte宣告为“人格存储槽” |
| `natural_value_source` | 原生捕获、历史归档、仅存在注册表，三者不能合并 | 将2021 NBA2K22外站Embiid合同偏好当作当期真实玩家数据 |
| `read_identity` | `save_id / source_batch_id / native_player_id / game_date`与独立人物消歧 | 按名字、脸型或球衣号错误合并1984–2020不同来源的球员 |
| `persistence` | 某个值是一次菜单读数、历史状态还是目前可验证的跨季变化 | 认为有Fatigue历史字节必可查询现在的伤病 |
| `original_game_owner` | 这个数值由NBA2K22引擎主导自然演化还是来自外围合法事务 | AI对话同意就强行给三分+5或徽章 |
| `external_role_semantic` | 外部人物从本字段获得哪些信息和可能的私有解释 | 把Loyalty=80硬编码为绝不交易 |
| `role_rights/action_rights` | 球员/GM/教练/媒体各自能看到/提出/拒绝什么 | Media知道未披露的私有伤病以及球员本人的所有记忆 |
| `native_write / overwrite_risk` | 原生直接写入限制、游戏效果和污染历史风险 | 用未验证的原生字段记录谣言或人际信任 |

**额外领域引用**：原生99个倾向字节含48已命名、51UNKNOWN，另有**独立**同版外站99个标签不可强配；4个PlayTypes/1 Initiator、80技能徽章标签与21人格候选/3职业Motivation都已分别保存研究目录。侧表中的109并不表示总共只有109种可见球员信息，也不掩盖上述其它领域。完整异构对象入口由ATLAS与[README](../README.md)组织。

## 26. “已谈妥”与“世界真的变化”必须经过不同事实节点

**研究意义上的六层节点，不是新增代码接口**：

| 层次 | 玩家/角色世界的事实类型 | 能否声称当前游戏已变化 |
|---|---|---|
| `OBSERVED` | 真实游戏中看见的人员/合同/比赛/训练/伤病事实，须身份与来源批次 | 只可表述为所见事实，不是决策 |
| `ROLE_INTENT` | 外部球员想留队/离队、GM报价意愿、Coach战术意见等 | **不能**。人格目标或请求属于外部世界 |
| `NEGOTIATED` | 对方提出反报价、双方协议或永久拒绝；保存长期记忆的候选 | **不能**。可能不合法/不在正确赛季窗口 |
| `AWAITING_HUMAN` | 根据真实原生约束准备了可审批方案 | **不能**；`approved=true`不是玩家实际批准 |
| `EXECUTED_READBACK` | 确认玩家批准、执行器约束/字段身份、写前比对、实际修改与读回 | 仅可在这一级说已执行；还需谨慎区分存盘持久化 |
| `FUTURE_GAME_RESULT` | 下一次经真实2K比赛或游戏时间推进后，观察名单/属性自然变化/出勤 | 必须重新采集，不能由外部角色提前捏造世界事件 |

工程证据不是对未来工程的承诺：[已批准交易执行](../../37_APPROVED_TRADE_EXECUTOR.md)有当前身份Plan/Execute/Verify与操作人授权约束；[签约源码说明](../../38_APPROVED_SIGNING_EXECUTION.md)明确默认写入关闭、仍`approved_signing_v1_unvalidated`，不因球员愿意签就可以直接调用“签约已成功”。[休赛期计划](../../development_tasks/DEV_20261017_04_OFFSEASON_FREE_AGENCY_V1.md)目前含固定权重确定性竞价思路；它属于**早期工程设计**，不能误认满足V3球员可自主谈判和拒绝的最终目标。真正如何升级是以后独立开发工作，R04不开发。

## 27. 八类有真实边界的互动分叉（详见ATLAS）

| 案例 | 核心动态输入 | 允许谁提出/拒绝 | 什么不是原生保证 |
|---|---|---|---|
| **ATLAS-01 巨星条件加盟** | 当季FA资格、合法报价、阵容、人物公开目标 | Player给条件、GM拒绝拆队、Coach拒绝改变体系、竞争球队出价 | 游戏没有原生“一签约就必须交易第三人”的智能体按钮 |
| **ATLAS-02 明星申请交易** | 真实合同、归属、战绩与当事人自述 | 球员求换队、GM拒绝、竞争GM不愿付价 | 外部私下请求≠NBA2K原生已发生Trade Request |
| **ATLAS-03 首发/球权争议** | 真正分钟、Touch/Shot、PlayType、POE、Book、3D/Sim区别 | Player要球、Coach反对、GM提出替代方案 | 不能锁定精确比赛时间或出手数 |
| **ATLAS-04 内线空间转型** | 3PT技能、3PA、Roll vs Pop、训练计划 | Player要改变打法、Coach提出条件 | 不能为了转型直接改3PT能力/徽章 |
| **ATLAS-05 拒绝过载训练** | 已确认伤停、恢复进度、B2B和真实训练设置 | Player要求休息，Coach/GM有不同胜率考虑 | 没数据时不能产生已伤病故事，Durability不代表诊断 |
| **ATLAS-06 师徒拒绝/谈判** | Mentor候选与自然徽章进度 | 新秀与老将均可拒绝导师关系 | `mentorship_manager`是待认证结构，不是通用现成写入接口 |
| **ATLAS-07 合同分歧** | 当期Option/Bird/报价、Loyalty/Win/Money可见程度 | Player对工资保障或争冠抉择，GM/对手GM竞价 | 2021 NBA真实选项[SRC-0110]不是NBA2K22原生操作API |
| **ATLAS-08 媒体误判与纠错** | 可公开真实成绩、合同和采访、明确区分传闻 | Media发表/修正、当事人沉默/拒绝采访 | 不可把未披露的内心、未批准合同或健康私人数据报为事实 |

**这些案例不是固定剧情**。两名同样有高Loyalty的球员可以作出相反选择，一个教练可以坚持导致失败的战术，GM可误判球员成长，媒体可以批评后撤稿；系统不通过“最优建队策略”消除选择权。若真实数据不足，应`HOLD/REQUEST_DATA`或承认推论不确定。

## 28. 历史选秀与世界线重力的认识边界

2021–22赛季开始，1984–2020历史选秀按照项目轮回。实际出生年龄、Draft Class身份、名字/FaceID可能重复或与真实2026经验发生时间错位。**任何角色只知道当前故事世界已经真实发生的历史**；现实NBA未来比赛/未发生的冠军/之后选秀结果可作为研究者资料但不可无授权泄漏给角色。GM的`Potential=1`是遮蔽而非实际潜力，尤其不能把本世界新人判断为零潜力。人物长期记忆只能依据该世界时间线在外部单独积累。

R04既没有替历史线决定谁必须夺冠，也没有按真实职业史提前增加未来传奇的天赋。项目仅在玩家针对某具体历史纪元“历史重力”另行批准的特殊情况下允许改游戏能力；**R04-D不提出任何人物强化请求**。

## 29. DEV29 R04研究发布终态与R05接力

**正式研究状态：`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`。** K03+K12已分R04-A/B/C/D研究：职业档案/55Attr（16Durability）/17合同Profile、99原生倾向与99外部可见归档标签、四PlayTypes/Initiator、技能与人格徽章、三项动机、训练及医学接口、士气与合同、模型可提议/拒绝/错判并在真实游戏后获得反馈。**这些是来源明确、可检索的机制与自由选择原料**，不是已运行的人格系统。

未来原生缺口继续保持`UNKNOWN`：真正PC22本机全部页面枚举、已命名51未知Tendency raw字节的含义、人格徽章原生ID、三项Motivation原生偏移/当前值、真实Morale和伤病、Mentorship、合同执行当前实机验收，以及模拟器引擎的精确系数。不能为了R04“闭环美观”虚构这些源数据或把未核实数值暴露给某个角色。

**下一轮R05（NOT_STARTED）**：研究K07/K08/K09合同、工资帽/税、薪资预算、员工、球探、选秀与球队市场竞争、休赛期报价及巨星职业议价，把R04的球员自我诉求与实际金融/合法交易约束对接。R04研究归档后不要求DEV29独立审核；由用户/其他模型另外进行审阅，**本轮不自动启动R05、DEV28、Codex或任何Agent开发**。

## 30. 2026-10-28四槽PlayType的原生工程增量

独立工程任务`NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`恢复了四个专用Native Setter，按既有PLAYER布局修改四个有序类别槽；类别0..15名称继续沿用本资料库及PC22配置。角色须明确提供球员、所属球队、槽位和值；每项逻辑许可仅覆盖自己的槽位。Player人格没有默认修改权限，也不能借共享接口修改队友或属性。详细ABI、参数、原始证据和作用限制见[四槽合同](../../../research/rea_native_control/PLAYER_PLAYTYPE_NATIVE_CONTRACT.md)。

新增证据为固定PC22二进制的静态字段/回调恢复与离线工程验证，尚无本轮游戏附加、真实写入、原版UI、模拟使用率或Save/Reload证据。它不重开R04、不修改历史研究验收，不证明属性、倾向、徽章、Initiator或完整球员编辑链已经完成。

## 31. 2026-10-28属性/耐久与倾向的索引Native工程增量

上述独立工程任务继续恢复原版156项Stat索引Setter：54个已命名能力/耐久字段使用UI25..99和原生缓存失效路径，99个倾向位置使用0..100，其中48个现有名称、51个含义仍UNKNOWN。不把外站99个标签硬配到本机未知字节。Potential虽已定位，但会触发额外未闭合刷新，暂不调用；另两个未分类属性索引也不可用。精确字段、枚举、源码及原生副作用见[属性/倾向合同](../../../research/rea_native_control/PLAYER_STAT_NATIVE_CONTRACT.md)。

当前角色接口只向普通GM开放经host明确授予的Intangibles例外；其它能力/耐久技术接口限明确世界编辑。普通角色可按授权使用48个已命名倾向；Player仅能指向自身UID。技术可写不产生角色自我强化许可，未知倾向只供明确世界编辑且不虚构含义。徽章已恢复四参数原生候选与UI flag0调用，但其联动/互斥及标签尚未闭合，因此保持不可调用。新增均为静态与离线证据，未证明UI/模拟/自然成长或持久化；R04历史研究不重开。
