# BPTI — R4 三路研究整合与Codex前置开发交接 V1

2026-10-20 | owner: Web GPT Development | status: **RESEARCH_INTEGRATED_FOR_PLAYER_REVIEW / CODE_NOT_STARTED / GM_V4_NOT_ENABLED**

> 本文件整合已经归档的R1、R2-V2、R3成果与现有M0–M4/DEV14工程接口，供玩家决定下一阶段B0–B6的实现任务。**不是自动授权Codex执行、合并PR、游戏写入或新档开局**。R2尚有来源索引缺漏且2K22具体战术CRC/调用机制未全证；R4保留这些未知，不宣称全联盟30队正式可执行策略已通过。

> **来源补录增量：** R2原文中ATL-S1/S2及7处source URL缺口已有[独立补充索引](BPTI_R2_SOURCE_REPAIR_ADDENDUM_V1.md)，其中LAL-S2确切论据仍未恢复，证据状态不得自动升为VERIFIED。Codex阶段化交接文件见[DEV22](../development_tasks/DEV_20261020_22_BPTI_RESEARCH_TO_CODEX_PHASED_HANDOFF_V1.md)。

## 0. 研究资产与状态（唯一长期入口）

| 研究模块 | GitHub正式文件 | 审阅状态 |
|---|---|---|
| R1真实篮球因果与球员决策权 | [R1原文](BPTI_R1_BASKETBALL_SYSTEMS_DEEP_RESEARCH_V1.md)；[R1审核](../development_reviews/BPTI_R1_DEEP_RESEARCH_REVIEW_V1.md) | ACCEPTED_FOR_INTEGRATION；10家族，32来源，游戏行为未证 |
| R2 30队组织/教练/历史演化 | [R2原文](BPTI_R2_30_FRANCHISE_IDENTITIES_AND_EVOLUTION_DEEP_RESEARCH_V2.md)；[R2审核](../development_reviews/BPTI_R2_V2_DEEP_RESEARCH_REVIEW_V1.md) | ACCEPTED_AS_RESEARCH_CANDIDATES；30/30档案和表；ATL-S1/S2、另7处URL缺漏须修复/降级 |
| R3 PC 2K22行为与能力限制 | [R3原生映射](BPTI_R3_NBA2K22_NATIVE_MAPPING_AND_CONFLICTS_V1.md) | RESEARCH_COMPLETE_FOR_ARCHITECTURE；10家族→项目可读字段候选，效果未知处显式HOLD |
| 现有M2/GM执行底座 | `docs/GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH.md`、`web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md`、`docs/DEV14_STATE_IO_RUNBOOK.md` | M3-T和M4工程已合并main，真实GM V4未启用；正式新档事实消费另有准备门 |

**一句话架构**：**篮球原则（R1） + 组织/教练历史（R2） + 可行原生控制（R3） → 球队SystemBlueprint → 现有M3 HOLD/INTERNAL/MARKET → 玩家批准的DEV14执行。**

不建设第二个GM市场、原生执行器、历史球员能力改造器、实时教练AI或独立胜率预测器；长期GM与M4工程反馈、季后赛双引擎年度校准相互隔离。

## 1. 三份研究共同支持的篮球认知模型

### 1.1 五层结构与动态时间尺度

1. `FRANCHISE_IDENTITY`：可追溯管理/教练跨期价值（发展、纪律、风险、合作等）。**慢变量**，可以为UNKNOWN；只有跨赛季管理行为证据与明确玩家决策才可更新。
2. `COACH_PHILOSOPHY`：具体主教练攻防教学与适应能力。**中变量**；教练更换不删除长期球队传统，管理人员需要真实本局来源。
3. `BASKETBALL_SYSTEM`：一个或多个R1非互斥攻防家族，必须能回答**第一优势、谁引发防守反应、二次机会、对手反制及再反制**。战术与对手计划属于**快变量**。
4. `PLAYER_ROLE_AND_AGENCY`：PRIMARY_CREATOR、SECONDARY_CREATOR、CONNECTOR、POST_HUB、MOVEMENT_SHOOTER、ROLL_DECISION、RIM_ANCHOR等可以组合；`SCRIPTED_ENTRY`、`STRUCTURED_READ`、`CREATIVE_OPTION`、`BAILOUT_RIGHT`、`RESET_RIGHT`是认知职责不是2K硬编码旋钮。
5. `MATCHUP_GAMEPLAN`：指定对手防守覆盖、自己暴露代价与反制、A/B/C篮球方案；玩家触发的赛前/节点方案，不是现场实时控制。

组织文化与战术/球员关系是**双向**：强组织可影响选人，历史级球员也能改变战术基础和球队招聘优先；不允许从当期名单倒推出未经来源证明的长期文化。

### 1.2 核心篮球因果规则

`ENTRY_CONDITION → FIRST_ADVANTAGE → DEFENSIVE_RESPONSE → PLAYER_READ → SECOND_ADVANTAGE → COUNTER_RESPONSE → (CREATIVE_OPTION | BAILOUT | RESET)`。

例如对Spread PnR：Drop允许强pullup创造者惩罚中距离；Show/Blitz可用short roll后4v3；Switch可能出现错位；过度弱侧help可找到帮助来源。**这些是篮球原理，2K22引擎具体是否调用与受益人如何取决于R3映射和ACE黑盒。**

判断失败要用Mechanism与Context来解释Outcome：不能“低于联盟平均中距离效率→压制德罗赞”、“单场助攻下降→抛弃Motion”或“盖帽少→认定护框无效”。

### 1.3 六级转型阶梯（建议的经营协议）

`ROLE_TWEAK → SECONDARY_BRANCH → CO_PRIMARY_SYSTEM → TACTICAL_REBASE → COACH_ALIGNMENT_CHANGE → ORGANIZATIONAL_REIDENTIFICATION`。不是数值升级条，也不是自动实施的6种游戏事件；每级需说明触发事实、保留组织价值、需要角色调整、教练能否执行、M1预算机会成本、反证和下次观察窗口。

- 球员刚加入首先尝试**局部角色/副体系吸纳**，不以姓名或现实名气将他直接设为GOAT/必选主轴。
- 若多个对手和阵容下真实优势反复出现，主副体系再重排。
- 当前教练无法适应时只产生`COACH_ALIGNMENT_RESEARCH`，不模拟已拥有合法的教练市场执行器。
- 组织身份变更最慢，需多赛季、管理层选人和发展行为有连续证据，而不是月度输赢。

## 2. 研究→本局事实：双重时间及来源保护

每个事实/解释最小保留：
`claim_id, source_id, source_url, publication_date, historical_period, fact_valid_from, evidence_level, retrospective_only, claim_status, counterevidence, design_relevance`。

明确分隔：
- `REAL_HISTORICAL_REFERENCE`：训练/设计模式可以读取全部篮球史和教练演变，包括2022以后回顾；**不能把新赛季以后的赛果和交易赋予2021游戏GM先知视角**。
- `AVAILABLE_AS_OF_GAME_DATE`：真实2021开档当日当时就存在、由公开历史可知的球队和教练背景，可用于2021初始Identity seed；如2021年以后发表历史回顾，只能提取其对截止日之前已发生事件的描述并标记回顾性。
- `CURRENT_GAME_STATE`：此虚构世界线的当前游戏存档、同批2021–22起始名单/教练/合同/表现，必须经过现有`require_gm_sanitized`和本次身份校验；**权威最高，绝不被现实历史网页覆盖**。
- `FUTURE_OR_HIDDEN`：游戏日期之后真实表现、职业结局、Potential隐藏分数，不进入正常GM预测或角色评级。GM潜力仍遵守脱敏；不能因叫Jordan/Shaq/Kobe/Jokić预置巅峰能力。
- `PROJECT_NATIVE_VERIFIED`：2K22已证原生字段与规则（平台/版本明确），完全独立于NBA现实历史资料。

例如R2在2022年末回顾Boston的换帅与Finals旅程，只能把**此前已发生**的2013选秀/2021 Udoka上任等作为2021初始历史；2022总决赛、2022年White交易和整个赛季换防效果不得预装为2021开档GM认知。

## 3. BPTI最小数据契约建议（复用M2/M3，不新建权威事实库）

字段名仅为设计候选，正式Codex要对已有schema逐项适配，不提前创建并行库。

```yaml
SystemCard:
  system_id: MOTION_READ_REACT
  evidence_claim_ids: [R1-S...]
  role_requirements: [MOVEMENT_SHOOTER, CONNECTOR, CUTTER]
  offensive_advantage_chain: [ENTRY, FIRST, DEFENSE, READ, SECOND, COUNTER, FALLBACK]
  defensive_counter_options: [SWITCH, TOP_LOCK, DENY]
  second_answers: [BACKDOOR, RESCREEN, ISO_MISMATCH]
  player_agency: [SCRIPTED_ENTRY, STRUCTURED_READ, CREATIVE_OPTION, BAILOUT_RIGHT, RESET_RIGHT]
  observables: [OUTCOME, MECHANISM, CONTEXT]
  known_failure_conditions: [...]
  roster_and_budget_tradeoffs: [...]
TeamIdentity:
  nba_team_abbr: GSW
  historical_seed_as_of: 2021-10-19
  franchise_values: [{claim_id: R2-T-GSW-01, status: SUPPORTED_INTERPRETATION}]
  unknown_values: []
  historical_coach_context: {name: Steve Kerr, as_of: 2021-10-19}
  system_candidates: [MOTION_READ_REACT, SPREAD_PICK_AND_ROLL, SWITCHABLE_PRESSURE_DEFENSE]
  confidence: HISTORICAL_SEED_ONLY
  operational_link: NOT_BOUND_TO_ANY_SAVE
SystemBlueprint:
  save_id: REQUIRED_FROM_GM
  source_batch_id: SAME_SANITIZED_BATCH
  team_id: REQUIRED_FROM_SAME_BATCH
  coach_identity: REQUIRED_FROM_SAME_BATCH
  available_player_role_refs: [NATIVE_IDENTITY_REQUIRED]
  franchise_identity_ref: TEAM_SEED_REFERENCE
  primary_system: BASKETBALL_FAMILY_NOT_NATIVE_ENUM
  secondary_systems: []
  first_advantage: basketball explanation
  opponent_counter: basketball explanation
  second_answer: basketball explanation
  late_clock_creator_ref: REQUIRES_SAME_BATCH
  native_binds: [{field_key: VERIFIED_ONLY, object_key: REQUIRED, effect_status: UNKNOWN_OR_DIRECTIONAL}]
  internal_alternatives: [HOLD, TACTICAL_FIX, ROLE_FIX, TRAINING, MARKET_IF_GAP]
  failure_evidence: []
  unknowns: []
  approval_status: NOT_APPROVED
```

**不要把此YAML示例编译成游戏写入**：有些`SystemCard.role_requirements`属于现实篮球层，`TeamIdentity`只是历史seed，`SystemBlueprint`只有真正同批球员/教练/本队书/对手身份后才可生成正式GM方案；`native_binds`需要M3返回真实registry object/enum/old_value、DEV14负责审批tuple与写入。

设计上将`TeamIdentity`作为现有TEAM_STRATEGY_STATE的关联历史上下文（或可检索单独知识卡），由现有gm_workbench存储当季版本历史；不重复30队数据库和员工市场。每次决策留`why_this_basketball`、`advantage_mechanism`、`player_agency`、`counterplay_and_risk`、`why_not_hold`的摘要及证据。

## 4. 十家族与30队的交叉落地规则

全部10家族拥有R1篮球因果和R3游戏字段类别候选；所有30队拥有R2 `R2-T-XXX-01`历史初始候选。但**每队只有合法Source绑定后才能评估人员、教练和目前可加载战术手册；30个历史seed != 30队真实经营ASSESSED**。

跨家庭组合示例（非完整30队运营配置，所有真实更改均需玩家批准）：

| 2021候选球队 | 历史身份/第一优势 | 第二答案和反制 | 可能的2K控制方向 | 未知 |
|---|---|---|---|---|
| GSW | Kerr/Curry时期Motion+无球引力，Green传递优势 | 对手switch/top-lock→slip、backdoor、错位/核心持球 | 已知coach粗体系、Freelance、已证PlayType+本队书、少量具名Tendency | 具体split/shot receiver CRC、ACE调用 |
| CHI | 2021 Donovan重构，DeRozan/LaVine半场创造而非1990年代Triangle | 夹击DeRozan→二次发起/弱侧，Ball/Caruso负责连接/防守 | 角色、PlayTypes、具名Mid/Iso，个人防守；不改原始球员Ability | late-clock触发不可硬锁、PlayType调用 |
| MIA | Heat组织文化稳定，Spo的防守方案多样 | 对手持球/内线类型不同→具名个人防守、主辅覆盖与角色变化 | Coach当前体系、本队书、18项PERSONAL、BenchDepth | zone/switch细节及ACE判断、整体防守GM只读 |
| SAS | Pop/Duncan时代纪律/培养持续，进攻可重新换主轴 | 新秀改变中轴→副体系或主战术；保持组织文化 | 同批Coach/Book/Type与GM时间版策略 | 2021名单不保证拥有2014传切同样球员 |
| DEN | Malone/Jokić现代时期中锋策应 | DHO被阻→二次PnR/低位错位/无球后卫反切 | 已证Book/Type/initiator字段候选及当批实际属性 | 没有已证Point-Center专属枚举 |

**真实30队生产要求**：各队不必不同纯标签；必须能说明当前教练理念和人员如何把篮球优势落实、为什么同一球员在不同队价值不同、何时HOLD/换体系/寻市场；不能空给30个战术模板。这由后续R4→Codex B3/B4业务实现及真实数据再评估。

## 5. GM推理流程与执行边界（插入原M3，不复制它）

1. 读同批可信Game状态，检查Player Potential遮蔽、教练和本队书存在、当前team_id。
2. 调出TeamIdentity（含UNKNOWN）与当期教练理念，提出**最适合当前技能**的Primary/Secondary篮球意图，保留组织价值连续性。
3. 借R1 SystemCard明确第一优势、防守反应、第二选择、末端自主创造者和应该接受的防守代价；反例/风险不可缺。
4. 借R3 NativeBinding检查原生支持和未知，每项动作明确`SUPPORTED_FIELD_DIRECTION/TYPE_MATCHED_ONLY/UNSUPPORTED/HOLD`，不编造字节或CRC，也不需要额外模拟器。
5. 走现有M3 D1–D6：先比较HOLD/INTERNAL（教练/本队书/角色/个人防守/训练/软轮换），证据无法通过内部改善解决才MARKET；M1真实合同/薪资与对方GM双边评估，不用篮球知识虚构交易报价。
6. 产出未批准的最小native intents与理由，走DEV14既有CAS/审批/回读。交易/换帅后旧角色计划按当前Source漂移重新研究。换帅已确认且需团队书恢复时采用单独`TEAM_BOOK_REBIND`、成功后新批再提内容槽。
7. 后续赛果仅用于评估篮球意图的机制支持/反证，不能用整季一个效率数判定球队文化错，也不能把GM球队经营反馈写入M4工程BUG池；3D与Calendar校准留专项。
8. 各组织文化的真正变化需要多个赛季一致的管理/选人/教练证据，不能因一名明星选秀的历史名号自动出现。

## 6. 面向Codex的分阶段执行包（待玩家明确授权）

**B0 — 接口合同/审稿缺口关门**：在已有M2、M3和DEV14之上确认`SystemCard/TeamIdentity/NativeBinding/SystemBlueprint`最小字段、各层时间/来源约束；修复R2缺失URL的归档索引或降级相关Claim，不要去重写研究者原报告。

**B1 — 十种篮球体系可检索化**：R1 10家族转换为精简易检索卡，保留优势链、角色/自由度、失效与counter、sources；复用M2知识检索，不建立第二套巨大知识引擎。SourceID支持查询/跳转；不以每张卡几百KB高耗查询的原文作为每轮默认模型输入。

**B2 — 原生语义映射层**：将R3矩阵对齐现有原生字段目录与同批对象；覆盖本队coach/Freelance/Book、PlayerType/Tendencies、18PERSONAL，未知CRC与51倾向保护、反映效果等级。任何本队关键主打法没有一个已证可行动作时输出`PARTIAL/HOLD`而非虚假READY。无需此次穷尽所有68槽动作和51未知倾向。

**B3 — 30队历史身份候选与实局绑定接口**：从R2建立30张可版本化历史身份卡，体现Culture/Coach不同层和2021时间知识边界。首批可以全部`SEED_READY`，新档真实批次出现后才绑定在任教练、球员与阵容证据形成`OPERATIONAL_ASSESSED`；受证据缺口影响的字段保持`UNKNOWN`。

**B4 — 篮球推理到M3经营动作**：让R1/R2/R3决定GM问题描述、战术意图、内外替代及交易评价，返回`why_this_basketball`、`role_graph`、`first_advantage`、`opponent_counter`、`second_answer`、`native_support_and_unknowns`，使用M3现有D1–D6、财务、稀疏plan和审批tuple，禁止第二套交易批准或游戏执行。

**B5 — 跨赛季历史演化协议**：把六级阶梯作为具体决策审计/版本历史的候选规范；记录触发事实、变更前后、同批证据、反证、玩家批准与时间尺度，教练变化和球队文化分层；不是虚构主帅合同市场或自动改球员能力。

**B6 — 最小已授权开档前验收**（未来在任务书中明确小范围测试、遵守DEV20政策V2，不在R4阶段抢跑）：纯历史知识10/10卡、30/30seed及缺源标记；GSW/CHI/MIA三种具有真实不同理念的经营解释和可确认Native意图；历史巨星异队后的角色→副体系阶梯；无真实源时只读历史参考而不能虚构30队已评估；原生UNKNOWN被HOLD；无游戏写入、无自动批准、能力/Potential不可变；已有M3逻辑未被复制/破坏。是否追加任何测试由玩家届时批准。

### 具体交付态

`BPTI_RESEARCH_INTEGRATION_READY_FOR_REVIEW`：允许据此拆Codex任务，但**不等于原生全部战术已验证、30队现实存档绑定完成、首季已开始或正式GM V4已经启用**。

## 7. 待解决的风险按优先级

- **SOURCE-P1**：R2 ATL-S1/S2缺索引，LAC-S2、LAL-S1/S2、MIA-S2、MIL-S2、SAC-S1/S2缺稳定URL；Codex仅能保留原Claim并降级，或待玩家授权研究补源后再提升；其它队的薄弱来源不能填充为稳定历史文化。
- **TEMPORAL-P1**：2021游戏初始与2021–22后续现实赛季/2022+报道混淆风险；区分已经在2021发生的事和后来可知结果，不因文章晚发表而全部禁用历史回顾，但不能偷偷注入未来赛果。
- **PLAYBOOK-P1**：68槽CRC可读写，但内部受益人、slip/PnR/triangle细节尚非一一验证；真实篮球理念可完整建模，**原生行动只能部分落地且须可解释地降级**。
- **AUTH-P1**：普通GM严格不修改Ability/Potential/Badge、员工任命尚无正式市场执行器、OVERALL只读、Tendencies需逐次玩家批准、不要偷做GM V4切换。
- **ENGINE-P2**：3D中玩家操控与Calendar内部仿真不同；本项目推理只管统一GM数据，差异量化交季后赛校准器；不保证胜率/“像历史冠军”。
- **ORGANIZATION-P2**：R2报告的组织文化置信度不得转化为基于传统给球队胜率+N%或优先交易权重；证据不足可长期UNKNOWN，允许世界线自然形成新传统。

## 8. 审阅结论

**三路研究在内容与架构层面已经形成闭合链条，可以据此制定B0/B1等Codex分阶段开发任务。** 当前尚不能标记整个BPTI已实现，R2来源索引与2K行为未知必须随实现保留；新档30队`UNASSESSED`、GM V4`NOT_ENABLED`原样保持。

采用的落地原则是：**篮球知识解释意图，球队历史约束选择，玩家可见游戏事实决定角色，原生字段决定能执行到什么程度；一切游戏修改只有玩家明确审批才进行。**
