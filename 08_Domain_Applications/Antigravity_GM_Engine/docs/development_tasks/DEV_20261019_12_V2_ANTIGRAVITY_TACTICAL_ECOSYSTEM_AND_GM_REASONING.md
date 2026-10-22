# DEV12 V2 — Antigravity：基于现有教练机制扩展NBA2K22战术生态 + GM篮球决策知识引擎

**2026-10-19 · 唯一执行研发负责人：Antigravity · 委托方：玩家 · 篮球机制研究：Web Development · 使用方：GM V4。**

**本文件取代DEV12 V1（原来交Codex实现）的分工与执行方案。A、B、C、D四期全部由Antigravity负责。** 之前的V1技术问题与研究资料保留为参考，不需要重新让Codex实现。Antigravity可以自行查找内存、编写读写/采集/执行代码并对接现有教练机制；Codex仅在未来另有明确任务时做审阅、部署协助或跨模块整合，不是本专项必经执行方。Antigravity实施功能≠已获得玩家授权修改**正式游戏存档**：游戏实际变更仍按玩家审批规则。

## 0. 两个同等重要的最终交付，不是单纯内存外挂

**（I）能力层**：让GM通过现有审批链读取和（必要时）受控修改教练属性、体系适配、完整战术手册、球员4个Play Types/发起者角色、个体Tendencies、逐人防守策略，以及后续Antigravity研究中的训练/导师/疲劳恢复数据。保留原教练19项默认+18项指定对手整体防守，扩展而非重复开发。

**（II）理解层【本任务真正高难度与主要验收重点】**：建立NBA2K22原生行为机制的**有证据的关联图谱/决策解释规则**，使GM能说明：
- 谁是优势创造者（creator），谁转移优势（connector），谁终结（finisher）、掩护/护框、谁被放空/被包夹；
- 主教练本身的可读属性/偏好、当前体系、Freelance/POE、Playbook具体战术、4槽PlayTypes及个体Touch/Shot/Iso/Drive/Play Discipline等倾向如何共同影响**战术是否可调用、谁得到球、选择哪种动作和是否可能成功**；
- 对手的个人防守/团队防守怎样限制本队，以及赛前如何配置具有第二、第三进攻路径的反制方案；
- 当前球队是“缺战术/使用不当/倾向冲突/缺少执行能力/确实缺人才”，在HOLD、内部改造、训练、教练、交易之间为什么选一个；
- 哪些已得到2K22玩家验证、哪些只是篮球合理推理、哪些确实不清楚，**没有内部引擎公式时不得编造影响+X胜率的关系**。

**GM篮球解释优先于字段数量**：四期内功能完成而GM仍只能说“需要射手，建议交易”，不视为真正完成。

## 1. 必读仓库路径（均已在2026-10-19通过GitHub main实际获取）

**1A — 使用规则与系统入口**

- [GM教练决策和全部19+18字段](../../web_gm/manuals/GM_COACHING_OPERATIONS.md)：现有教练行动的合法枚举、POE/Playbook/四Freelance/体系与29个对手方案、审批、BenchDepth与分钟边界。注意手册较早的“训练永远排除/个人倾向不可修改”段落已被手册开头2026-10-19新用户决定覆盖。
- [教练批次执行手册](../40_COACHING_EXECUTION_RUNBOOK.md)：现有GM意图→提案→30队离线批次→玩家批准→Codex/执行方获批写入/条件恢复；新功能采用相同执行理念。
- [DEV07旧原生POE研究](../39_COACHING_TACTICS.md)：旧版布局/历史调试经验，**不得当现行接口状态**。
- [2026-10-18真实首次生产采集完成状态](../34_BASELINE_CURRENT_STATE.md)：**正确状态是FIRST_PRODUCTION_CAPTURED_AND_PUBLISHED**，不要被早期手册“尚未首采”误导；当前已有同批30队19默认和870对手整体配置。
- [SQLite与GM只读数据查询](../GM_SQLITE_QUERY_ACCESS.md)：M0读取方式与查询过滤。
- [来源能力注册表](../../config/source_catalog.json)：来源审计、当前coaching_tactics生产覆盖、新增来源的注册方式。
- [上一步篮球机制研究](../research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md)：2K22玩家实战、篮球因果链、勇士与反制案例。
- [旧DEV12 V1原交Codex任务书](DEV_20261019_12_TACTICAL_BEHAVIOR_ENGINE_CODEX_HANDOFF_V1.md)：**历史交接背景，责任人以本V2为准**。

**1B — 必须复用的真实代码**

| 真实路径 | Antigravity需要做什么 |
|---|---|
| [config/coach_tactics_profile.json](../../config/coach_tactics_profile.json) | 当前Coach/Gameplan/Playbook布局、19默认字段、18防守、原生枚举；其中已记录playbook type RVA / pointer / stride / 68 play slots（**槽容量不代表已解出具体PlayID/行为**）；增量schema或新profile，不破坏旧枚举 |
| [src/coach_locator.py](../../src/coach_locator.py) | 复用当前进程绑定、metadata/CRC、对象定位、playbooks目录；不能使用不验证的静态绝对地址 |
| [src/coaching_reader.py](../../src/coaching_reader.py) | 同一只读会话采主教练/战术设置/对手Gameplan，不二次构建“另一份教练快照” |
| [src/coaching_overall.py](../../src/coaching_overall.py) | 已有有效matchup的读取/切片/混合字段规则；每条有matchup_id、defender_id、8-byte防守设置（其中UI整体作用是“所有有效条目同值”） |
| [src/coaching_targets.py](../../src/coaching_targets.py) | 复用最新save/coach/roster/process binding及对象定位，避免改错队/对手 |
| [src/coach_codec.py](../../src/coach_codec.py) | 原生bitfield编码与前值保留、PlaybookID必须来自当前加载目录 |
| [src/defense_codec.py](../../src/defense_codec.py) | 原生8-byte防守字段的按位变更，须保留未动字段 |
| [src/gm_core/coaching_batch.py](../../src/gm_core/coaching_batch.py) | 离线30队方案与审批batch、OVERALL模式；可扩展PERSONAL但**不能把其冒充OVERALL** |
| [src/coaching_batch_executor.py](../../src/coaching_batch_executor.py) | 真实内存批次、读前值/同批、审批、回读、回滚、幂等保障 |
| [src/coaching_executor.py](../../src/coaching_executor.py) | 单动作审批/事务与同源前值机制，作为新PlayerTendency/PlayType执行器参考 |
| [src/gm_core/coaching.py](../../src/gm_core/coaching.py) | 纯离线proposal业务语义，模型不能以approved:true自行授予权限 |
| [src/gm_core/data_reader.py](../../src/gm_core/data_reader.py) | 必须从同一published/career/batch读取球队事实；新数据与旧batch不能错时拼接 |
| [scripts/coaching_snapshot.py](../../scripts/coaching_snapshot.py) | 独立开发期只读定位入口，不改变正式生产时间戳 |
| [scripts/coaching_batch.py](../../scripts/coaching_batch.py) | 已有支持审批批次的CLI入口，尽量复用其入参结构/离线+preflight+execute+rollback模式 |
| [scripts/run_data_update.ps1](../../scripts/run_data_update.ps1) | **玩家触发**的唯一full_verified_v1生产采集，不增加“按需求单独发布半套新来源” |
| [scripts/gm_data_query.py](../../scripts/gm_data_query.py) | 给网页GM提供按队/球员/对手查询新资料的受控只读查询（需加查询端点时可增量实现） |

**生产数据定位**：由[published/saves/mc_haliburton_2021/latest.json](../../published/saves/mc_haliburton_2021/latest.json)示范结构读取最新批次，之后跟实际career和batch，不得假设示例M02永久最新。单批含coaching/teams.json、coaching/field_dictionary.json、coaching/opponents/TEAM.json和source_coverage.json。全量Only/同一只读session及玩家触发时间是项目规则。

## 2. 禁止架构跑偏与权限边界

- 现有19教练默认+18整体对手防守稳定复用，不重写已有完整执行器，不破坏CoachData共享bitfield。
- 比赛真实3D期间**原版ACE保持ON**。不开发实时外挂看场模型、不改ACE算法、不让GM网页模型一直监控比赛；赛前写入原生教练/球员行为参数后允许原版ACE自主接管。
- 不要求精确锁个人分钟：游戏AI会覆盖。仅BenchDepth/BenchUtilization与实际人员配置作间接影响。
- 用户已明确授权GM按战术融入调整**个体球员Tendencies**；但每个正式球员/字段/前值/目标/理由都需要玩家批准，Antigravity提供代码能力不等于可自行改正式局。球员**原始能力值、潜力、徽章、身体数据、伤病**不能因为GM战术原因直接更改；训练造成的自然成长由原版游戏决定。用户另行批准历史线重力例外不在本开发任务内。
- 区分：全局Gameplay Tendencies ≠ 个体Player Native Tendency；Play Type槽 ≠具体PlayID；球队体系枚举≠本书内容；教练能力≠球队无条件+胜率；模拟结果与3D行为不能按同一个公式假定。
- 数据与业务身份不能错：本库有效Matchup存储确实有整数matchup_id/defender_id，但**尚不证明matchup_id直接等于玩家全局唯一player_id**。Antigravity必须实机比对角色/对手名单与UI定位，建立验证映射，不得凭变量名直接写某球员。
- 游戏菜单可能重写外挂刚写好的CoachData（已有实机证据）；运行写入要遵从已验收的离开Coach Editor前提，并对新增Player Edit、Playbook Edit、Training等UI缓存另外定位覆盖风险。
- 研究可以使用隔离/测试存档；不得未经玩家正式审批改变真实赛季球员。

## 3. 核心：先给GM做“机制知识图谱”，不是等所有写入完成才开始理解

以 **7层依赖关系和两条反馈路径**统一研究。Antigravity每找到一项原生字段，必须一起输出用途、连接、证据、边界、可能副作用，更新GM知识卡，而不只报告内存地址。

```
球队战略 / 球员原始能力(只读) / 员工教练能力(只读)
       ↓
主教练偏好与当前ActiveSystem、团队POE、四Freelance（当前19字段已有）
       ↓
PlaybookID → 该手册的具体PlayID/PlayType/原生场上角色及战术顺序（待新增）
       ↓
每球员四个有序PlayType槽 + Play Initiator + 球员角色（待新增）
       ↓
原始个体Tendencies（Touch、Shot、Iso、Drive、Post、Spotup、Play Discipline...）
       ↓
对手整体18字段 + 指定对手球员个人防守 + 自队实际匹配的defender
       ↓
NBA2K22原生ACE/3D比赛AI自主选择和执行（保留引擎）
       ↓
球员/球队游戏比赛表现，战术机会、出手分布、效率；训练/疲劳/自然成长
       ↓
GM下一经营节点：HOLD、调整赛前配置、角色培养、换教练、签约/交易
```

这是一张**依赖假设图**，不是游戏开放的公式。每一连线至少区分：
1. `CONFIG_COMPATIBILITY_VERIFIED`：静态可证明（如PlayType槽是否有同类PlayID）；
2. `COMMUNITY_BEHAVIOR_REPORTED`：2K22玩家重复观察到，但具体因果公式未知；
3. `BASKETBALL_REASONING`：篮球战术理论上合理，2K22实现不确定；
4. `PROJECT_OBSERVED`：本游戏版静态读数或玩家游戏体验；
5. `UNKNOWN`：不制造效果评分。

同时建立**两个不同结论**：
- “战术可以被调用”（PlayType对应书内实际类型，不代表有收益对象和战术成功）。
- “球队真的能利用战术赢球”（需要人员能力、偏好/权重、对手防守、游戏动画/判定与场上观察；不要伪造确定概率）。

## 4. 四期全部由Antigravity负责

### A期 — 原生字段/数据来源与现有教练执行器扩展

目标：**看见完整战术生态**，而不是只看到一个PlaybookID。按“已可读最短路径”交付：

1. **PLAYBOOK_CONTENT**：当前loaded Playbook下具体PlayID、每个Play的原生PlayType、当前手册包含和排序。记录发起者/掩护者/终结目标若PC内存可证，否则明确`target_roles=UNKNOWN`。现有profile里play_slots=68提示可能的槽数组，需自己解码有效数、空槽、名称/类型；不要一口气直接强制写内容。
2. **PLAYER_PLAY_TYPES**：每人原生四个**有序**Play Type（可能空值、重复类型、默认或PlayInitiator），真实enum。区分4个类型槽与“具体某场战术PlayID”。
3. **PLAYER_TENDENCIES**：优先Touch、Shot、Isolation类别、Play Discipline、Drive、Layup/Inside/Close/Mid/3PT、Spot-up/Offscreen/Post等**实际存在**的个体原生字段。读取原始数值、范围、与当前55项Ability字段在内存中是否共享块；防止写Tendency时触碰Ability。
4. **COACH_ATTRIBUTES/FIT**：主帅原生攻防/训练发展能力、System Proficiency/球员适配项（只要当前PC真的存在）。次世代MySTAFF有区别，不可无证移植。
5. **INDIVIDUAL_DEFENSE**：在现有8-byte Matchup记录中证明matchup_id与某名对手球员的身份，assigned defender映射及个体设置，厘清OVERALL写同值后如何保留PERSONAL差异。
6. **球员效果来源最小版**：保留同批已采球队/球员统计、缺失的出手类型或球队比赛表现只标`NOT_OBSERVED`，不使用推算的每球调用事件。

**阶段结果**：同career/batch/player_id/team_id绑定的合法只读schema、field_dictionary新增项、可查询的样本数据、UNKNOWN列表、read/write/effect状态表。新增生产源必须走玩家正常触发的同批`full_verified_v1`，开发期定点只读快照不能冒充已生产发布。

### B期 — GM战术因果知识与决策模型【最高研究难度、优先验收】

**不要等待C期全部可写才开始B期。** 对每类字段研究与真实球队/2K22经验连接的“如何影响战术选择”，形成机器可读的**知识卡**和可解释的诊断算法。

必须区分至少五种问题：
- **A类 结构不匹配**：球员四个PlayType某项非空，但当前Playbook里没有同类型战术→`UNSERVED_PLAY_TYPE`；即使类型匹配，实际Play是否强绑定某特定受益人须进一步确认。
- **B类 进攻球权分配失衡**：RunPlayTendency/POE/PlayInitiator与Touch、Shot、Iso、Play Discipline形成冲突，导致第一核心过度集中。社区有人认为Touch影响Freelance，而设定战术优先级更依赖本书/PlayType，**不使用“Touch=球权次数的线性公式”**。
- **C类 战术与能力不匹配**：如被要求大量持球创造者无必要BallHandle/Pass/决策能力；低运动能力内线被迫无限换防；通过角色/训练/交易解决，不直接加个人能力。
- **D类 防守责任冲突**：个人外线SMOTHER、掩护OVER/HEDGE、TagOnRoll、弱侧PreRotate与球队整体防守相冲突；强防射手可能放空内切者，必须把代价写给GM。
- **E类 应对被针对**：核心被Blitz、TopLock、Switch、Drop等限制后，是否存在真实可执行的二次进攻路径（掩护短顺下、翼侧持球、无球反切、错位攻击），避免“核心被锁死→无限ISO”。

每张`TACTICAL_KNOWLEDGE_CARD`至少含：

```yaml
id: "PNR_BLITZ_SHORT_ROLL_COUNTER"
basketball_principle: "高位夹击释放短顺下处理球人"
nba2k22_mechanisms:
  - "Playbook.PlayType and actual PlayID"
  - "Player.PlayType1..4 and Touch/Shot/Pass behavior"
  - "Coach.RunPlayTendency/Freelance/POE"
  - "Opponent Gameplan/Hedge/TagOnRoll"
requirements:
  roster_roles: ["ball_handler", "short_roll_passer", "weakside_finisher"]
  verified_native_fields: []
contraindications: ["no short_roll_passer", "no weakside_spacing"]
counterplay_and_cost: "弱侧轮转与干扰会改变突破收益"
evidence: [{kind: "2K22_COMMUNITY|NBA_REAL|PROJECT_OBSERVED|UNKNOWN",url: "source"}]
sim_effect: "UNKNOWN unless independently observed"
live_3d_effect: "reported|observed|unknown"
gm_alternatives: ["HOLD","PLAYBOOK_CHANGE","PLAY_TYPE_CHANGE","TENDENCY_CHANGE","TRADE"]
```

最低覆盖：
- NBA球队六到八类体系/赢球哲学：Motion/Split、Spread PnR、DHO/HighPost Hub、Five-Out、LowPost、Switch Defense、Drop Rim Protection、Transition；
- 进攻角色creator / offball gravity / short-roll connector / wing second-side scorer / roll man / floor spacer；
- 防守角色point-of-attack / wing stopper / rim protector / help-tag / switchable big；
- 对手至少四类防守反制：Drop/Blitz/Switch/TopLock+可能的弱侧tag。

**证明GM学会了的输出**不是一份万能词汇表，而是解释真实球队：
1. **2021–22勇士**：Curry与Klay的无球/持球威胁，Green高位策应、Looney屏障/篮板、Wiggins二级突破与侧翼防守；为何核心被夹击后必须有二级处理球与终结路线；2022 Finals G5 Wiggins26分13篮板/Curry16分0/9三分只用作现实篮球参考，不能以“该球员必定爆发”判断当前游戏存档。
2. **对照队**：实际选一支现有原生战术被不合理指派/手册缺PlayType的队，给出证据明确的`UNSERVED_PLAY_TYPE`或角色受益者错位实例；如数据不支持则输出未知，而非故意制造一个错误样例。
3. 给出每队`HOLD vs INTERNAL_SCHEME vs PLAYER_ROLE_TENDENCY vs INDIVIDUAL_DEFENSE vs TRAINING vs STAFF vs MARKET`的因果、执行依赖与机会成本；M3/财务决策仍由现有GM V4体系负责。

**关键2K22实证**：[Operation Sports Useful Findings 主帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)：Touch不一定决定叫战术，Run Plays与Playbook/PlayTypes/Play Discipline共同作用；[page4](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page4)：ISO POINT类型缺本书Play→该槽跳到下一项；有些内置战术强绑定受益人；[page10](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page10)：有作者实验明星Shot Tendency降低后球权分配更均衡，**不可把某人80设成所有人的硬上限**。深度研究应追踪相反样例和不同Playbook/球员，而不是把玩家经验冒充引擎确定公式。

阶段结果：
- `docs/research/NBA2K22_TACTICAL_RELATIONSHIP_EVIDENCE_V1.md`：关系矩阵（字段→功能→球员角色→正/反证→本代适用/未知）；
- `config/gm_tactical_knowledge_v1.json`（推荐）：机器可读知识卡、原生字段引用与推理链；**不可把“改参数值为90提高胜率”写成正式事实**；
- `TACTICAL_FIT_REPORT`：30队可查询的断链诊断，带来源/信心/UNKNOWN和真实推荐依赖；哪怕读数不全也能输出已证部分。

### C期 — Antigravity完成原生受控写入（不交给Codex重复开发）

实现并在隔离测试存档验证这些新增动作（按A期实际地址可执行程度顺序交付）：

1. `PLAYER_PLAY_TYPE_CHANGE`：指定player_id与team_id、4槽中的原生合法一个/多个、有序值、原值；确认目前Playbook是否具有所需类型。不存在时可以给GM另一个改Playbook候选，不应默默写无法调用的组合。
2. `PLAYER_TENDENCY_CHANGE`：按player_id、原生字段、old/new raw、范围检查，写时显式保护Ability/Potential/Badge；允许单人多个Tendency一起形成事务，不能借机批量使所有球员统一80/50。
3. `PLAYBOOK_CONTENT_CHANGE`：当前本书的实际PlayID增删/排序和类型兼容检查，保留其他内存结构与已加载目录；若无法确定正确游戏更新/提交机制，可先只开放整本`PlaybookID`选择+诊断，不准假装精确编辑成功。
4. `INDIVIDUAL_MATCHUP_DEFENSE_CHANGE`：必须同时用owner_team_id、opponent_team_id、verified_target_identity、defender_identity、确切field和enum，处理原生总体Bulk与个人Override的优先顺序；**OVERALL后来写值不能无声清除PERSONAL战术差异**。
5. 如果教练人员的能力属于游戏原始Coach属性，优先只读用于选帅和体系适配，**不因为系统智能不足直接修改教练技能等级**。游戏原生员工管理/聘约属于之前Codex合同机制，不做替代。

复用已存在`COACHING_BATCH_CHANGE`审批约定；如果引入新的action/scope，在旧CLI/纯codec上增量扩展或用独立模块接原审批策略，不允许破坏已验收默认19项与OVERALL18项。默认**离线预演**，实时`execute/rollback`只在玩家明确批准`career,batch,decision,version,action_ids,digest`后启用；当前存档、教练、球员、球队、战术本目录、Matchup发生变化就拒绝旧批次。读取+内存写入+回读+有条件恢复，不能悄悄覆盖他人的新值。保留前值镜像，不把模型建议当执行批准。

### D期 — 训练/体力/导师/成长与长期GM的战术联动（Antigravity同一任务）

Antigravity已经在研究训练，继续把**原生事实→决策后果**作为目标：
- 团队/个人训练种类、训练强度、训练重点/周期、自动训练状态；
- 个人身体疲劳、伤病风险/可用性/恢复与轮换实际使用；
- 导师/训练营、自然徽章/能力成长反馈（只读取游戏自然结果，不直接修改成长值）；
- 将训练方向与当前球员在体系中的角色和防守任务关联：需要投射/无球能力、传球轴、横移与外线换防、内线护框；如果训练类型做不到就标`TRAINING_SUPPORT_UNKNOWN`，不能编写“训练必加+X能力”。
- 在GM提案中把短期负荷（伤病/疲劳）与长期角色培养、合同年限、交易机会成本结合。
- 保持游戏自然成长与原版ACE，GM的赛前训练输入不直接授予增加原始属性的权力。

阶段结果：训练/体能原生可读字段与批准写入能力、训练-战术角色适配知识卡、长期`DEVELOPMENT_PLAN`与当月`TACTICAL_FIT_REPORT`衔接；缺真实效果证据则给出训练安排理由和“待自然观察”，不宣称能力已提高。

## 5. 最关键的GM诊断契约（贯穿A-D）

Antigravity发布给GM的每支球队分析，不是单一个“体系匹配评分”或每球员“价值高低”，而是可解释报告：

```yaml
career_id: "actual"
batch_id: "actual"
team_id: "actual"
coach: {identity: "verified",attributes: "observed_or_unknown",preferred_system: "observed",active_system: "observed"}
playbook: {id: "actual",play_types_present: [],play_ids_observed: [],unparsed: []}
player_roles:
  - player_id: "actual"
    play_types: ["verified_native_type_or_unknown"]
    per_slot_coverage: ["TYPE_MATCHED_ONLY|UNSERVED_PLAY_TYPE|ROLE_MISMATCH|UNKNOWN"]
    relevant_tendencies: {}
    ability_constraints_read_only: []
defense: {overall_vs_opponent: "observed",personal_matchups: "observed_or_unknown"}
tactical_hypotheses:
  - issue: "球员无法得到与个人角色匹配的战术调用"
    evidence: ["source & exact value"]
    causal_status: "STATIC_VERIFIED|REPORTED|INFERRED|UNKNOWN"
    alternatives:
      - {type: "HOLD",tradeoff: "保留现状"}
      - {type: "PLAYBOOK_CHANGE",tradeoff: "可能影响其它球员的战术覆盖"}
      - {type: "PLAYER_PLAY_TYPE_CHANGE",tradeoff: "改变角色定位"}
      - {type: "PLAYER_TENDENCY_CHANGE",tradeoff: "改变球权分配但不能保证真实调用"}
      - {type: "TRADE",tradeoff: "工资及失去原球员的机会成本"}
    effect_on_live_court: "UNKNOWN until directly supported"
    effect_on_calendar_sim: "UNKNOWN unless independently evidenced"
proposed_actions: []
blocked_unverified_capabilities: []
player_approval_required: true
```

完整解释需含反事实：
- 不改任何东西会怎样？
- 只换战术本/角色，而不改倾向会怎样？
- 只改倾向而手册没对应战术能否奏效？
- 核心被针对后球队有没有二级攻击路线？
- 如果无法内部解决，交易什么角色，放弃谁，以及会如何影响原本体系？
- 当前哪些推断只是现实篮球原理，而非2K22公式？

字段只完成读写，不输出以上解释，不能认为DEV12 V2研究部分验收通过。

## 6. 验收与禁止无意义开发

- A期：能读具体同一球队多个球员**真实4槽与本书真实PlayID/Type**；没找到的UNKNOWN。生产采集只在玩家触发full_verified_v1后出现同批数据，不强制Antigravity新开局或推进赛季。
- B期：至少一个勇士多路径案例及一个真实未匹配/对位缺陷候选（若证据不足则明确UNKNOWN），可解释**球员能力、个性化倾向、Playbook、教练策略与对手策略**如何共同形成赛场选择，附正反社区来源；输出可以直接供GM做HOLD/内部/交易比较，而不是无证据通用评分。
- C期：实际找到原生可写地址的模块按现有审批协议完成有限隔离验收；别为了凑完成数给每种Tendency或每队逐值/重启反复测试，未找到可用原生调用机制的条目允许`READ_ONLY/NOT_EXECUTABLE`。
- D期：训练/成长与赛场体系关联有可证观测，在球队GM报告中能区分训练输入与自然能力成长输出，保留疲劳/伤病成本与角色安排；不要求强迫打多年验证。
- 不扩张为NBA历史全量影音数据库、重建原版ACE、赛季Sim Engine调参、全30队万能“99效率战术”、锁精确分钟；也不要求Codex再实现同一套。
- 合规：**经审批才改真实游戏；球员原始能力值严禁作为普通经营性操作字段**，只准具体Tendency/战术角色、受控防守和原生训练输入。
- 每期都可以独立交付已实现且有证据部分，并汇报下一期能做什么，不要求为了未知字段阻塞所有GM建设。

## 7. Antigravity建议工作顺序（减少重复开发）

1. 读取本V2、GM手册、coach_tactics_profile、locator/reader/overall/targets/codec/batch executor，列出现有可直接扩展的字段和真实原生对象，而不是重新扫描19+18。
2. **优先Playbook内部战术清单 + 个人4 PlayTypes**，因为这能最快证明“有角色类型但没有战术”的断链；同时研究来源以建立B期知识卡。
3. 再纳入个人Tendencies与PlayInitiator、教练能力/Proficiency，优先读并生成解释，而不是第一天就改所有球队。
4. 用原有有效matchup结构开发逐人防守映射/与OVERALL共存策略；训练独立继续，不用等完全写入才能让GM阅读。
5. 当B期知识卡能真正诊断球队，才向GM V4开放新`q_tactical_fit`等有界只读接口与策略提案schema（查询接口实际名称由Antigravity设计，不直接假定存在）。
6. 根据玩家具体审批执行新增修改，逐步实现C/D，同时不改变M3现有实际代码或已发布数据语义。

**任务成功定义：GM不仅“能修改四槽/倾向/战术书”，还知道为什么应该修改、何时不改，以及修改会如何改变篮球进攻路线与对手反制的机会成本。**
