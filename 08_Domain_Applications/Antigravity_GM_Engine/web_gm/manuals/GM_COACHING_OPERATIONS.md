# GM 教练战术操作手册

2026-10-20玩家补充：球员四个PlayTypes和球队四个Freelance槽都按前槽优先、执行更多理解（PLAYER_REPORTED_UI），保持原生顺序但不设固定比例。共享战术池、用途和球员/球队适配已接入[GM共享池入口](../../docs/GM_SHARED_PLAY_POOL_V1.md)；多队可引用同条战术并添加/替换到各自书中，不能把“本队书独占”误读成“战术只能本队使用”。正式目标仍是本队书、CRC来自新同批已加载全目录，仍需具体批准；本补充未修同名书匹配缺口。

2026-10-20工程补充：GM须同时读取[Potential遮蔽与Intangibles规则](GM_POTENTIAL_FOG_AND_ROTATION_BIAS.md)。PR#5底层限制/人工监督review状态查docs/34和DEV14_TO_M3_HANDOFF；旧PlaybookID切换及整体防守示例不是日常GM提案规范。新档本队同名书是用户保证的默认前提，不以克隆/共享专项作为门槛，仅实际异常单动作阻断。

> **2026-10-19 主教练/球队本名战术书规则**：[DEV17](../../docs/development_tasks/DEV_20261019_17_CODEX_FIRST_MAINLINE_TEAM_BOOK_COACH_RULES_V1.md)与[GM个人防守/Book政策](GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)：每队每游戏赛季只有休赛期允许换帅一次（合同竞价/签约另列后续），A队聘B教练后必须在获得玩家批准的技术绑定操作中，将可能继承的B书恢复到**A队同名的真正独占原生Book**，再根据B教练体系与A球员修改A书68槽；B书不得被修改。普通GM不改Overall、不随意切BookID。此处是最新运营政策；实际同名Book唯一性和换帅写入还未完成本局生产验证。

> **2026-10-19 最新玩家决议（GM运营优先规则）**：[GM个人防守与球队专属手册政策V1](GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)已生效。**普通GM只使用逐人PERSONAL_DEFENSE策略，不改OVERALL_DEFENSE**；整体18项可继续采集只读，后面旧“修改整体防守”的章节仅供已部署旧执行器的历史技术参考，**不是新的GM提案规范**。**普通GM不通过PlaybookID切换战术手册**，必须使用本队原生独占书、编辑该书68槽；换帅后重取教练和书绑定、按新教练理念修改本队书。如果本队和其他球队共享同一本PHI等原生书，**禁止任何单队修改共享槽位**，需Antigravity确认专属书实体与受控技术绑定，不能仅通过名称伪装独占。用户对新方案仍逐批审批；并不意味着现有DEV14已实现新禁写和独占规则。

> **2026-10-19 第二次补充：新增原生战术生态四期开发全部由Antigravity负责。** 现行实施任务为[DEV12 V2 Antigravity：教练-手册-4槽-倾向-逐人防守-训练-知识引擎](../../docs/development_tasks/DEV_20261019_12_V2_ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING.md)。本手册仍是已验收19默认/18整体的操作依据；新任务必须复用其内存定位、原生枚举、审批/恢复与全量采集，不视为已拥有完整Playbook内战术、个人PlayTypes、Tendencies和逐人防守写入。核心目标是教会GM解释多个设置对球员选择和战术执行的相互作用，再形成内部调整与交易决策。**这覆盖先前DEV12 V1分配给Codex的实施职责。**

> **2026-10-19 玩家战术生态与倾向授权更新**：本手册内“训练机制永久排除”和“球员个人Tendencies一概不准经营修改”等早期范围限制，已被玩家后续明确决定**部分覆盖**：训练设定与疲劳/成长的原生接口由Antigravity调查、提交Codex开发；球员个人Tendencies已获准作为**GM赛前战术适配提案类别**，需真实原生字段和玩家逐项批准、Codex安全执行，仍不准直接修改个人能力/潜力/徽章。本手册当前19项默认/18项针对对手整体防守的**现有执行能力边界不变**，不因新授权自动变成可写的个人Play Type、个人倾向、完整Playbook或个人防守。权威分析：[战术生态研究V1](../../docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md)；Codex任务：[DEV12](../../docs/development_tasks/DEV_20261019_12_TACTICAL_BEHAVIOR_ENGINE_CODEX_HANDOFF_V1.md)。赛场原版ACE保持ON、游戏实际分钟继续由原版AI控制。

状态：DEV07 V2已通过玩家审查；PR #1于2026-10-18合并main（2509b3b）并同步本地执行仓库。首次真实生产采集/发布尚未运行，等待玩家触发。整体防守及混合批次已完成隔离局技术验证；默认六POE沿用既有验证，五数值设置、双体系与命名手册合计14项已有实机写回证据，四Freelance按完整原生枚举与有序接口提供，加上玩家明确开放的原生Tempo，共19项可提案和受控执行。Tempo界面含义未知，不称为已验证的进攻节奏或百分比。板凳深度由GM根据实际阵容选择，没有9–10测试样本上限。不能越过字段字典的生产门槛。本手册随实际验收更新，不代表玩家批准了任何具体战术。

## 2026-10-18 玩家补充：精确分钟控制不再追求

玩家已在本局实际操作中观察到：**游戏AI会频繁重新分配或重置个人上场分钟，外挂的精确分钟修改会被覆写**。因此GM应将其视为**AI持续拥有的控制权与本项目有意接受的玩法边界**，不是必须补齐的接口缺口。当前及可预见后续均**不以开发稳定的逐人分钟写入、锁定和防覆盖机制为目标**，也不针对这一点提出研发、复写对抗或循环补写任务。

- 保留并积极使用已认证的间接杠杆：`BenchDepth`（最多使用多少人）、`BenchUtilization`（替补使用倾向）、进攻/防守体系、阵容互补性；它们影响AI如何使用球员，**不承诺将任何具体球员控制在指定分钟**。
- GM可以观察每位球员赛季实际场均上场时间、比赛效率与角色成长，判断轮换是否偏重、负荷是否过高、年轻人机会是否不足；结论以**球队层级的轮换方向**呈现，例如“适当扩大轮换”，不安排个人分钟精确值或逐人minutes计划。
- 玩家长期经验确认教练机制影响游戏自然成长；**不以精确个人分钟控制作为成长机制必要前提**。训练仍由游戏AI完全负责、外挂不参与。
- 对本局没有认证的首发/具体球员调换接口也不冒充可写；若暂无写回，阵容搭配仅作为分析与在其他合法手段（交易、签约、教练体系）中的运用依据。
- 此段**覆盖本文旧有的`PLAYER_MINUTES_EXECUTION_UNAVAILABLE`“待接口确认”性质表述**：不作为后续开发/验收待办，不因无法精调分钟而阻止GM制定其他可操作的19+18教练方案。

## GM 核心经营原则：阵容使用、上场时间、教练体系与自然成长（2026-10-18玩家规则更新）

**玩家确认的经营经验**：根据玩家长期模拟终极联盟以及其他人类玩家的多赛季经验，教练体系不只影响当前比赛打法与结果，**也会影响球员在游戏引擎中的自然成长轨迹**。将这条经验纳入GM长期判断与建队策略；其具体属性/倾向变化路径、数值公式、幅度、适用版本及因果强度仍可能无法从本局数据独立识别，不能编造“某参数必然提升+X能力”。这些是玩家观测到的**游戏自行成长**，不是外挂GM直接编辑球员能力。

**训练机制明确排除**：目前外挂系统没有训练设置接口。训练完全交给 NBA2K22 游戏AI处理，**GM不研究、不规划、不建议调整、不申请开发、不采集训练负荷或训练结果，也不把训练写入教练批次**。此项不作为本轮或后续GM经营待办。若将来玩家亲自改变规则再恢复关注。

**新经营优先级**：交易如更换食材，阵容搭配、角色与上场时间、主教练可操作设置、球队独占战术书的战术槽、按对手具体球员的个人防守方案，才决定如何发挥现有人才。每个真实经营节点先评估**当前球员能否通过内部调配取得更好结果**，再与交易或签约进行机会成本比较；本原则**不强制**先调战术、不强制每队改设置，也不否定必要补强。

### 30队的四项常规经营杠杆

| 杠杆 | GM决策问题 | 当前真实接口边界 |
| --- | --- | --- |
| **阵容搭配与角色** | 后场/侧翼/内线是否互补？核心持球与无球职责、空间、防守对位和替补组合是否合理？是否有球员被错误使用？ | 可使用大名单、55项已认证能力和赛季统计分析。具体首发/搭配/角色的写回需要各自验证；不能假装教练19项能直接替换任意首发或指定个人角色 |
| **上场时间与轮换** | 核心是否打得太少/太多？替补战力是否足够？能否调整轮换深度/替补使用以平衡胜率、体能和发展机会？ | 当前已认证可写`BenchDepth`（使用人数上限）和`BenchUtilization`（替补使用倾向），**不是具体某球员的分钟数**。累计`minutes_per_game`是比赛统计，不是原轮换计划。玩家实测游戏AI经常重置/重新分配个人分钟，精细写入即使短时成功也会被覆写；本项目不追求锁定个人分钟，不能生成虚假`minutes_before/minutes_after`执行内容 |
| **教练战术体系** | 挡拆、空间、低位、转换进攻、护框、外线防守、协防、联防、Playbook和Freelance是否匹配实际球员？ | `COACH_DEFAULT`19项，使用当前同批来源/原生字典；Tempo具体UI含义UNKNOWN，五项Sim禁止写入 |
| **针对对手与球队建设** | 面对强外线/强内线球队，如何组织整体持球施压、掩护处理、协防和篮板？是否确实需要交易/签约补齐无法弥补的人员短板？ | `VS_OPPONENT_DEFENSE`18项作用于指定owner面对指定opponent的有效整体matchup组，不开放逐人专项防守指令；交易有独立有限范围执行器，仍须玩家审批 |

### 竞争力、身体负荷和成长是联动目标

- **即期比赛结果**：通过现有球员适配的体系、战术手册、Freelance、POE与对手策略提高球队竞争机会。调整是有目的的篮球假设，不承诺固定胜率加成或AI必定按设计调用。
- **体能、健康与可用性**：轮换太短、主力使用过重、比赛攻防强度过高可能带来疲劳与潜在伤病成本；同时替补过度使用也可能牺牲眼前胜场。玩家明确将这些影响视作长期策略的重要条件，但当前缺可靠本局伤病/疲劳来源，不能声称某个raw值使伤病概率变化多少。
- **球员自然成长**：承认玩家和其他玩家跨赛季观察到的教练影响成长现象。GM应优先为年轻球员寻找匹配其特点、能够获得有意义比赛机会的阵容角色与教练体系，随后在未来同口径快照中观察能力、潜力和比赛表现的实际变化。**教练影响成长不等于授权直接修改球员属性/倾向/徽章**；数值增长由游戏AI与自然机制产生。
- **游戏观察与确定性因果的差别**：战术可能改变场上出手、跑位和使用率；未来若发现底层属性或倾向变化，可记录为游戏自然变化，但不要在缺控制组/精确游戏记录时把任何变化断言为单一教练字段造成。我们不要求为此做额外实验，不推进游戏验证。
- **现实线/历史线平衡**：让强队或历史巨星依靠更合理的阵容与体系形成真实竞争力。优先用球队经营、轮换与教练模拟时代风格；仍不允许未经专项批准直接增强普通球员属性，也不为重演历史赛果而强制胜负。

### 每次GM经营节点的具体工作流程

1. **锁定可信来源**：以`latest.json`和`source_coverage.json`为准；只有`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`且当前批次完整包含30队`coaching/teams.json`及`field_dictionary.json`时，才可生成教练raw写入方案。缺数据时只给战术方向与`COACHING_SOURCE_UNAVAILABLE`，不冒充已观测字段。
2. **逐队分析阵容搭配与角色**：用真实球员能力、位置、统计、合同和比赛表现，判断谁适合持球、护框、拉开空间、补位、替补衔接。首先说明哪些问题属于当前阵容内部可优化，哪些属于人才硬缺口。
3. **逐队分析上场时间与轮换**：读取实际出场场均分钟与样本规模，必要时建议缩短或加深轮换，平衡主力负担、替补质量、伤病风险和年轻人成长机会。可通过已认证的`BenchDepth/BenchUtilization`提出具体改值；个人分钟由游戏AI负责，GM仅从实际分钟数据评估球队级轮换方向；不设个人目标分钟、不提出精细化分钟开发或执行请求。
4. **教练默认体系**：为球队实际核心检查六POE、双体系、Playbook、四Freelance、四百分比倾向、Tempo等，选择必要且可逆的修正；只能用同批字段字典中合法raw值。避免对所有球队使用同一模板。
5. **对手专项防守（新规范）**：按需读取本队对指定对手的个人对位条目，以双方球员native ID确认为前提，按实际持球威胁/内线/外线/防守者能力设置18项合法`PERSONAL_DEFENSE`目标；**不产生`OVERALL_DEFENSE`调整**。现有整体防守来源仅作只读背景，禁止伪装个人目标。
6. **交易与签约对比**：先比较内部搭配、轮换、教练优化所能解决的问题，再决定是否需要新人。不能因为有教练功能就拒绝所有交易；若人才确实无法完成职责，仍应果断补强。
7. **每队做出具体决定**：输出`COACHING_PROPOSED`或有理由的`COACHING_HOLD`，以及`ROSTER_CONFIGURATION`、`ROTATION_REVIEW`、`TRADE`等需要的运营决策；没有字段证据时HOLD具体写入而非停止篮球分析。
8. **获批执行与后续复盘**：GM只制定篮球目标与合法字段，经程序生成可信批次，玩家批准具体摘要后交Codex执行。玩家主动推进游戏并在下一次更新来源后，GM复盘球队攻防、球员出场、健康（如有数据）与游戏自然成长。不得要求额外训练操作、胜率试验或自动推进。

### 资料来源与证据边界

本项目以**玩家及其他玩家多赛季经验**确立“教练影响游戏内长期成长”为GM长期经营的经验事实；不会错误地降格为“只改变进攻战术、无成长关联”。但不据此宣称任何具体`COACH_DEFAULT`字段有已证明的成长公式。相关公开背景材料包含2K官方[2K22 MyNBA说明](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)及[2K22教练设置被AI覆盖的社区反馈](https://www.reddit.com/r/NBA2k/comments/w0v87c/)，仅作版本背景；其中次世代MyNBA专属内容不充当本项目PC/MC已认证的可写能力。**训练功能不在本外挂GM研究及执行范围。**

**执行边界不变**：本节仅定义篮球决策。19项默认、18项对手OVERALL的具体目标仍需可信来源、字段字典、玩家批准与Codex受控执行；逐人分钟、直接首发/角色编辑、训练、五项Sim、普通球员能力/潜力/倾向/徽章都不因本节变成可写接口。

## 第一次正式启用

首次启用按以下顺序核对；这是后续使用流程，不是本次文档修订已执行的动作：

1. PR #1 已由玩家决定合并，执行机器已更新到包含该合并的版本；确认当前代码、profile与本手册一致。本次PR已经玩家批准合并main；执行机器的实际版本仍需与合并提交对应。
2. 玩家触发正常数据采集及发布：沿用 `scripts/run_data_update.ps1` 的真实参数和 `-Publish`；不新增“只采教练”开关，不由开发窗口自动运行。
3. `published/saves/<career>/latest.json` 的新批次已完成上传（`upload_status=UPLOADED`，`data_updated_at/uploaded_at`有效），并指向所选存档与玩家确认的游戏日期。不能沿用尚不含教练来源的旧批次。
4. 新批次 `source_coverage.json` 中 `coaching_tactics` 为 `VERIFIED_OBSERVED_SAME_BATCH`；新来源审计通过，不能仅凭文件存在认定可用。
5. GM可读本批 `coaching/teams.json`、`coaching/field_dictionary.json`，需要某队对手方案时再读该队 `opponent_file`。本批恰有30队，身份、日期与更新时间一致。
6. GM形成提案、离线生成并校验批次；玩家明确批准具体摘要后，执行模型才按[执行手册](../../docs/40_COACHING_EXECUTION_RUNBOOK.md)写游戏。

第一次真实生产采集/发布尚未运行。此处核对的是启用条件，不能把本手册、此前隔离局验证或下面的示例说成生产验证成功。

## 读取本局事实

按 `published/index.json → saves/<career>/latest.json → batch_path` 选择玩家要求的生涯和批次。先核对 `data_updated_at`、`uploaded_at`、`game_date`、career/batch，再读 `coaching/teams.json` 和 `coaching/field_dictionary.json`。不存在这些文件或 coverage 未标 `VERIFIED_OBSERVED_SAME_BATCH` 时，教练来源不可用；不能拿旧 TEAM `poe_*`、另一局截图或现实 NBA 声誉补值。

`teams.json` 含 30 队各自当前 HEAD_COACH 身份、阵容签名、19 项原始值、原始共享块和逐字段 readiness。更换主教练、名单、游戏进程或存档后需要重新取得可信来源。不能在旧采集包里补入较晚读取的教练数值，伪装成同一时点。**2026-10-18玩家确认全量-only规则**：任何新数据更新（包括因教练战术调整而触发）均按已授权的`full_verified_v1`刷新全部已验证来源，不开发、不请求单独教练来源刷新。GM不能自动触发更新；如玩家明确限制排除某项来源，应说明全量-only边界。

GM先读取实际阵容和当前教练设置，自行选择人数、倾向与已知原生枚举。不要把少量测试过的值当作白名单：BenchDepth的9→10只是验收样本，11、12等人数不会因此被拒绝。四个已确认百分比字段的0–100是实际UI范围；原生整数位宽/枚举校验与对象保护仍保留。完整UI端点未知时如实标未知，不编造游戏上限。

所有教练设置的取值判断统一参考本局其他教练的实际值和已核对的原生枚举，不安排逐值试验、菜单端点或保存重启测试。GM据分布、阵容和战术意图选择实用目标；样本最小值/最大值不是执行限制。

仅在确实分析某一对手时读取该队 `opponent_file`，例如 `coaching/opponents/PHI.json`。不要在 GM 启动时一次读取 870 条方案。旧批次不追填新观察。

## 球队默认战术：19 项

作用域 `COACH_DEFAULT`，对象是该队当前 HEAD_COACH。这里的默认表示该队面对所有对手的基础设置。

| 字段 | 篮球含义与允许值 |
| --- | --- |
| POEOffense | 进攻重点：0 NO_PREFERENCE、1 GET_TO_BASKET、2 GET_SHOOTERS_OPEN、3 FEED_THE_POST、4 PICK_AND_ROLL_OFFENSE、5 NEUTRAL_OFFENSE_FOCUS、6 RUN_OFFENSE_THROUGH_SCORER |
| POEOffense2 | 进攻节奏策略：0 NO_PREFERENCE、7 PATIENT_OFFENSE、8 NEUTRAL_OFFENSE_TEMPO、9 SHOOT_AT_WILL |
| POEOffense3 | 进攻篮板：0 NO_PREFERENCE、10 CRASH_OFFENSIVE_BOARDS、11 NEUTRAL_OFFENSE_REBOUND、12 LIMIT_TRANSITION |
| POEDefense | 防守重点：0 NO_PREFERENCE、13 PROTECT_PAINT、14 NEUTRAL_DEFENSE_FOCUS、15 LIMIT_PERIMETER_SHOTS |
| POEDefense2 | 防守侵略性：0 NO_PREFERENCE、16 PLAY_CONSERVATIVE、17 NEUTRAL_DEFENSE_TEMPO、18 PLAY_PHYSICAL |
| POEDefense3 | 防守篮板与转换：0 NO_PREFERENCE、19 CRASH_DEFENSIVE_BOARDS、20 NEUTRAL_DEFENSE_REBOUND、21 RUN_IN_TRANSITION |
| PreferredSystem | 教练偏好体系，0–7原生枚举；原生元数据与独立位域写入/回读/恢复已验收，未单独看到其UI，玩家停止同类重复核对 |
| ActiveSystem | 当前体系，0–7原生枚举；4主打内线→3主打外线已由玩家确认，不修改体系熟练度或评分 |
| PlaybookID | **普通GM只读**；仅换帅及获玩家另行批准的本队专属Book技术绑定可能更改，必须使用已加载真实enum_id，绝不凭名称认为独占 |
| BenchDepth | 板凳深度，即轮换球员人数上限；GM结合可用阵容与目标轮换自行选择。9→10仅为测试样本，没有10人的人为上限；保持原生整数格式校验，不解释为百分比 |
| RunPlayTendency | 执行战术频率，0–100、步长1；70→71已验收 |
| ZoneUsage | 区域联防频率，0–100、步长1；1→2已验收 |
| BenchUtilization | 替补球员使用率，0–100、步长1；40→41已验收，与轮换人数分开 |
| Tempo | 玩家已明确开放原生raw读写；UI及实际效果未确认，不混同POE进攻节奏、SimPace、阵容表现因素或百分比。此前同局8位主帅观测40–95（Rivers80、Kerr95、Nurse40等），可按这些值选择实用目标；0–100仅为据分布推断的参考刻度，不是UI端点证明或执行白名单。8位存储格式只拒绝溢出和非整数，不建议按存储极值制定战术 |
| HelpDefense | 协防，0–100、步长1；50→51已验收 |
| FreelanceType | Freelance 优先级第 1 槽 |
| FreelanceType2 | Freelance 优先级第 2 槽 |
| FreelanceType3 | Freelance 优先级第 3 槽 |
| FreelanceType4 | Freelance 优先级第 4 槽 |

体系原生枚举：0 BALANCED、1 GRIT_AND_GRIND、2 PACE_AND_SPACE、3 PERIMETER、4 POST、5 TRIANGLE、6 SEVEN_SECONDS、7 DEFENSE。

四套 Freelance 用 `freelance_sets:[slot1,slot2,slot3,slot4]` 保留顺序，或只修改一个具名槽。数组与具名槽不能在同一动作中重复指定。原生 34 个名称/raw 映射已由当前进程 enum CRC 与同版本可执行文件标签配对，见本批 `field_dictionary.json` 和仓库 `config/coach_tactics_profile.json`；按原生字段编号保存第1至4槽的顺序，提供全部34种合法枚举；不以测试样本缩减选项。未直接查看本局比赛内四槽页面，不宣称该项UI验证或四套使用概率相同。

五项 `SimPace/SimPress/SimHelpDef/SimOffReb/SimDefReb` 仅允许只读兼容，标 `GM_CONTROL_DISABLED`；任何 GM 目标均拒绝这些字段。逐球员对位、逐人预设上场分钟、直接首发/角色调整、普通球员能力和全联盟模拟滑块不属于此接口。个人上场分钟由游戏AI动态重新分配，玩家已确认不再追求精确控制；BenchDepth和BenchUtilization仅能间接调节轮换人数上限和替补利用倾向。

## 原有整体防守采集与执行技术（历史兼容，GM不再常规修改）

作用域必须是 `VS_OPPONENT_DEFENSE`，同时指定 `team_id`、`opponent_team_id`、`defensive_setting_scope=OVERALL`。例如 PHI(0) 面对 IND(20) 的方案不会用于其他 28 个对手。

本局 PC 页面本身就是整体防守，没有额外 All 下拉项。实际存储由该对手的全部有效 matchup 记录组成。一次整体调整会把所选字段应用到整个有效组，保留各记录的球员 ID、已分配防守者、空槽和其他未选字段。**这是DEV07旧版整体防守生成器的限制，不代表DEV14个人防守不能操作。最新GM规范必须通过DEV14个人对象，禁止从该旧生成器建立新的整体防守修改提案。**

本批字典列出 18 个原生字段及各自合法值：PressureOnball、PressureOffball、ForceDirection、ScreenDefenseOnBall、ScreenDefenseHedge、OffballScreenDefense、PostDefense、DoubleTeamPerimeter、DoubleTeamPost、ScreenDefenseOnBall5、ScreenDefenseHedge5、SwitchRule、OnballHelp、ScreenHelp、ExtendPressure、TagOnRoll、StayAttached、PreRotate。前 17 项分别使用自己的原生 enum，不共享一个通用枚举表；PreRotate 是原生 packed bool，只接受整数 0/1。无法确认的 PC 中文标签保留原生名称，不自行解释 OnBall5、Hedge5 或 TagOnRoll 的页面位置。

已直接配对的 PC UI：PressureOnball 0=自动，1=间隔。一次 UI 操作、程序同范围写入、玩家页面确认及条件恢复均成功。其他原生合法值使用字段字典中的英文标签，不把猜测译名作为观测。

每个整体对象保存全部有效记录的身份和完整 8-byte 前值。`values[field]` 若为 null、且列入 `mixed_fields`，表示当前各记录取值不同，不表示观察不到整个对象。整体目标会有意统一该字段，同时保留所有旧块供条件恢复；不能伪造一个共同旧值。`IsInUse` 是原始提交标记：已观察 UI 退出时 0→1，执行器在数值写完后复现该提交动作；不要将 0 直接解释成禁用或清除原始事实。

## 如何从设置形成篮球方案

下面描述GM选择这些设置的篮球意图与取舍，不声称已验证游戏内部算法或固定胜率收益。先看本局阵容、当前教练和其他教练的实际取值，再选本批字段字典中的合法目标；含义不明时保持 `UNKNOWN`，可以HOLD，不为确定取值另做菜单端点或逐值试验。

| 默认字段 | 决策意图与主要取舍 |
| --- | --- |
| POEOffense | 按核心与空间选择突破、射手空位、低位或挡拆；把主攻方式与实际持球人、掩护人和投射配置对应，不全联盟复制同一重点 |
| POEOffense2 | `PATIENT_OFFENSE`偏向耐心组织，`SHOOT_AT_WILL`表达更快寻找出手机会；根据球权组织与失误风险取舍，它才是已确认的进攻节奏策略 |
| POEOffense3 | `CRASH_OFFENSIVE_BOARDS`争取二次进攻，`LIMIT_TRANSITION`侧重退防；看篮板优势与对手转换威胁 |
| POEDefense | 保护禁区与限制外线之间取舍，看对手突破、内线与投射来源 |
| POEDefense2 | `PLAY_CONSERVATIVE`与`PLAY_PHYSICAL`表达保守或更具对抗性的防守意图；结合犯规、对位与防守资源，不承诺犯规或抢断变化幅度 |
| POEDefense3 | 冲抢防守篮板与更早转换进攻之间取舍；先考虑能否稳定结束防守回合 |
| PreferredSystem | 教练偏好体系，用于表达长期风格；与当前体系分开，不修改任何人或球队的熟练度评分 |
| ActiveSystem | 当前采用的体系，应匹配已观察阵容：如内线支点、外线投射或转换资源；不能把换体系直接解释为球员能力提升 |
| PlaybookID | **新GM只读取教练关联且确认归本队独占的手册**，通过改变该专属书内部槽位适配核心角色；不允许日常任意切换书，只有获批的换帅/技术性独占绑定例外 |
| BenchDepth | 轮换总人数上限；轮换深度、疲劳与核心上场时间的安排。按可用阵容选人数，不是百分比，也没有10人的人为上限 |
| RunPlayTendency | 预设战术调用倾向；较重视组织化set plays或更多自主处理之间取舍，参考当前持球组织能力 |
| ZoneUsage | 区域联防使用倾向；按对手空间、传球与本队协防配置决定，不承诺对任何进攻必然有效 |
| BenchUtilization | 替补使用倾向；在深度、疲劳与主力负担之间分配，与“最多用几人”的BenchDepth分开 |
| Tempo | `UNKNOWN`：原生raw读写已获玩家明确开放，但当前界面含义和实际作用未确认；只能参考本局教练分布选raw，不能当POE进攻节奏、SimPace或已验证百分比 |
| HelpDefense | 协防倾向；帮助防突破与保留原对位/外线空间之间取舍，结合具体对手整体方案考虑 |
| FreelanceType | 第1槽，规划为主要自由进攻方案；不表示经验证的固定使用概率 |
| FreelanceType2 | 第2槽，可作为对主要方案的补充或针对性替代；保持原生顺序 |
| FreelanceType3 | 第3槽，可用于另一空间结构或节奏选择；不保证AI必然按预期切换 |
| FreelanceType4 | 第4槽，备用方案；同样是有序配置，不是四个无关的随机选项 |

体系名称表达的意图可以作规划参考：`POST`内线支点、`PERIMETER`外线、`PACE_AND_SPACE`节奏与空间、`SEVEN_SECONDS`更早组织进攻、`DEFENSE`防守、`BALANCED`均衡；`TRIANGLE`与`GRIT_AND_GRIND`保留原生名称。具体游戏实现和加成不由名称推定，未知机制仍标UNKNOWN。

四套Freelance先确定本队主要进攻形态，再安排有用的替代，而不是为了填满四槽选四个名字。`FOUR_OUT`、`THREE_OUT`可作为空间结构的名称线索；`FLOW`、`TWENTY_ONE_DELAY`及各队命名方案的本版本具体落位/触发细节为UNKNOWN，不能仅凭名称编造战术过程。完整34项原生目录在文末；数组 `[slot1,slot2,slot3,slot4]` 保留配置顺序，不要求四套均匀使用。

| 指定对手字段（18项） | 篮球策略说明／未知边界 |
| --- | --- |
| PressureOnball | 持球压迫；`GAP`留间隔、`TIGHT/SMOTHER`表达更紧的压迫。按对手投射与突破威胁取舍；已配对UI为0自动、1间隔 |
| PressureOffball | 无球施压；`GAP/LEAVE`表达更多放空，`TIGHT/DENY_BALL`表达更紧或限制接球，取舍是补防空间与失去原对位的风险 |
| ForceDirection | `MIDDLE/BASELINE`表达引导中路或底线的意图；与本队协防位置配合，不推断引擎一定成功封堵 |
| ScreenDefenseOnBall | 持球掩护应对；`GO_OVER/GO_UNDER/SWITCH/ICE`分别表达绕上、绕下、换防或ICE策略。依据投射、突破与换防资源选合法枚举 |
| ScreenDefenseHedge | 掩护延误；`NO_HEDGE/SOFT_HEDGE/HARD_HEDGE/DOUBLE/CATCH_HEDGE`表达不同支援方案，取舍是持球压力、顺下和弱侧空位；精确触发细节UNKNOWN |
| OffballScreenDefense | 无球掩护的绕上、绕下或换防；看对手接球投射威胁与本队追防/换防能力 |
| PostDefense | `FRONT/BEHIND/THREE_QUARTERS_TOP/THREE_QUARTERS_BOTTOM`表达低位前顶、身后或不同侧的防守位置；看接球路线与身后协防 |
| DoubleTeamPerimeter | 外线包夹；`MANUAL/ON_CATCH/ON_DRIVE`按手动、接球或突破阶段表达包夹意图，接受放出其他空间的代价 |
| DoubleTeamPost | 低位包夹；`MANUAL/DIG/ON_CATCH/ON_DRIBBLE`表达手动、短暂协扰或不同触发阶段；`DIG`的本版本具体实现UNKNOWN |
| ScreenDefenseOnBall5 | `UNKNOWN`：保留原生独立字段与自己的枚举，不从后缀5推断适用球员、与普通项的覆盖关系或中文菜单位置 |
| ScreenDefenseHedge5 | `UNKNOWN`：保留原生独立字段；不能未经依据当作普通Hedge的别名或指定中锋设置 |
| SwitchRule | `SWITCH_AUTO/ALL/BIGS/GUARDS`表达换防对象规则的意图；本版本如何划分BIGS/GUARDS及具体无球触发UNKNOWN |
| OnballHelp | `HELP/NO_HELP`表达持球侧支援或保留原对位的取舍；准确中文菜单位置与引擎触发UNKNOWN |
| ScreenHelp | `HELP/NO_HELP`表达掩护场景支援或减少帮助的意图；与Hedge独立，不当作同一字段 |
| ExtendPressure | 扩大施压的原生YES/NO选项；具体扩大到何处、何时触发UNKNOWN，不编造全场压迫效果 |
| TagOnRoll | `UNKNOWN`：保留原生名及AUTO/YES/NO，不凭英文推断本版本具体tag规则或中文对应 |
| StayAttached | 保持紧贴的原生YES/NO意图；具体适用对象、与Hedge/Tag关系UNKNOWN，不自行宣称可消除掩护威胁 |
| PreRotate | 预轮转意图；原生packed bool仅0/1。具体触发和覆盖关系UNKNOWN，不把它解释为另一个AUTO/YES/NO枚举 |

这些动作只影响所选owner队面对指定对手的整体组；不开放逐球员防守或轮换写入。原生英文与raw映射始终以本批字段字典为准，`AUTO`不解释为“关闭”。

## 逐队决定与提案

30 队分别根据已观察的阵容能力、核心角色、深度和教练打法选择 HOLD 或 PROPOSED。每个动作说明具体篮球理由，不全联盟复制一套配置，不承诺固定胜率提升。`SIM_EFFECT_PENDING_PLAYER_MONTH`只是现有合同兼容字段，由生成器填写；它不要求等待一个游戏月份、做胜率验收或推进日期，也不是新的发布/执行门槛。

### 从30队来源到requests，再到完整外层提案

GM先读取本批30队、实际阵容和可用字段，逐队决定HOLD或调整。只为要改的队填写请求；指定对手方案还要选对手并按需加载owner文件。GM负责球队、对手、字段、合法目标raw和篮球理由；确定性程序负责补入career/batch/date、当前教练身份、原始共享块、整体组身份、before_raw及codec版本。**模型不得手写或猜这些原生事实。**

下面是完整可运行的离线例子，沿用先前PHI/IND的说明场景，**不是本局正式建议、玩家批准或新的实机验收要求**。例子表示已审阅30队：PHI两项调整，其余29队明确HOLD。若实际来源没有PHI/IND，按真实球队改意图后再生成，不能伪造队名或来源。`hold_other_teams`是本段说明脚本的篮球意图约定，不是现有CLI的新开关；只有GM明确决定其余队HOLD时才设true。

把以下篮球意图保存为 `_exports/coaching_example/gm_intent.json`：

```json
{
  "batch_id": "COACH_BATCH_001",
  "decision_id": "COACH_DECISION_001",
  "version": 1,
  "requests": [
    {"team":"PHI","scope":"COACH_DEFAULT","targets":{"POEOffense2":7},"action_id":"PHI_DEFAULT_TEMPO","expected_effect":"示例：更耐心组织进攻，不承诺胜率变化"},
    {"team":"PHI","opponent":"IND","scope":"VS_OPPONENT_DEFENSE","defensive_setting_scope":"OVERALL","targets":{"PressureOnball":1},"action_id":"PHI_VS_IND_PRESSURE","expected_effect":"示例：面对IND采用留间隔的整体持球压迫方案"}
  ],
  "hold_other_teams": true,
  "expected_effect": "示例：按所选阵容与对手规划战术，效果以实际游戏反馈为准",
  "data_gaps": []
}
```

以下脚本保存为 `_exports/coaching_example/build_proposal.py`，在**已部署的仓库根目录**运行 `python -B _exports/coaching_example/build_proposal.py <实际career_id>`。它只读已发布JSON、调用现有离线CLI并输出本地文件，不发起GM回合、不连接游戏、不批准执行。它展示的 `proposal` 字典列全外层合同，最终JSON嵌入真实完整batch/snapshot，**没有省略号、伪造旧块或待模型补齐的身份占位符**。

```python
import copy
import json
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
sys.path.insert(0, str(root / "src"))
from gm_core.data_reader import DataReader, attach_coaching_opponents, load_json, safe_child
from gm_core.decisions import validate_proposal

work = root / "_exports/coaching_example"
intent = load_json(work / "gm_intent.json")
data = DataReader(root).read(sys.argv[1])
if not data.coaching:
    raise ValueError("本批没有已审计的教练来源；等待玩家触发首次采集发布")
snapshot = copy.deepcopy(data.coaching)
by_name = {row["abbreviation"]: row for row in snapshot["teams"]}
requests = []
owner_files = {}
for item in intent["requests"]:
    row = by_name[item["team"]]
    request = {key: item[key] for key in ("scope", "targets", "action_id", "expected_effect")}
    request["team_id"] = row["team_id"]
    if item["scope"] == "VS_OPPONENT_DEFENSE":
        request["opponent_team_id"] = by_name[item["opponent"]]["team_id"]
        request["defensive_setting_scope"] = item["defensive_setting_scope"]
        owner_files[row["team_id"]] = row["opponent_file"]
    requests.append(request)
if intent.get("hold_other_teams") is not True:
    raise ValueError("此30队示例须由GM明确其余队HOLD；不能自动代替决策")
changed = {item["team_id"] for item in requests}
holds = sorted(row["team_id"] for row in snapshot["teams"] if row["team_id"] not in changed)

def write(name, value):
    (work / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

write("requests.json", {"requests": requests, "hold_team_ids": holds})
command = [sys.executable, "-B", str(root / "scripts/coaching_batch.py"),
    "--snapshot", str(data.batch_directory / "coaching/teams.json"),
    "--requests", str(work / "requests.json"),
    "--batch-id", intent["batch_id"], "--decision-id", intent["decision_id"],
    "--version", str(intent["version"]),
    "--proposal-output", str(work / "batch.json"), "--output", str(work / "dry_run.json")]
for relative in owner_files.values():
    path = safe_child(data.batch_directory, relative)
    command.extend(["--opponent-source", str(path)])
    attach_coaching_opponents(snapshot, load_json(path))
subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)
batch = load_json(work / "batch.json")
dry_run = load_json(work / "dry_run.json")
if not dry_run["valid"] or not dry_run["executable"]:
    raise ValueError(dry_run)
participants = {a["team_id"] for a in batch["actions"]} | set(batch["hold_team_ids"])
evidence = [{"source_batch_id": data.source.batch_id, "file": "coaching/teams.json",
             "field": "teams", "availability": "OBSERVED"}]
evidence.extend({"source_batch_id": data.source.batch_id, "file": relative,
                 "field": "records", "availability": "OBSERVED"}
                for relative in owner_files.values())
approval_request = {key: batch[key] for key in ("career_id", "batch_id", "decision_id", "version")}
approval_request.update(action_ids=[a["action_id"] for a in batch["actions"]],
                        batch_digest=dry_run["batch_digest"])
proposal = {
    "decision_id": batch["decision_id"], "version": batch["version"],
    "career_id": batch["career_id"], "source_batch_id": batch["source_batch_id"],
    "status": "PROPOSED", "operation": "COACHING_BATCH_CHANGE",
    "teams": [r["abbreviation"] for r in snapshot["teams"] if r["team_id"] in participants],
    "evidence": evidence, "calculation_refs": [],
    "expected_effect": intent["expected_effect"], "data_gaps": intent["data_gaps"],
    "requested_approval": [approval_request],
    "coaching_batch": batch, "coaching_snapshot": snapshot,
    "execution_authorized": False
}
verdict = validate_proposal(proposal, data)
if not verdict["valid"]:
    raise ValueError(verdict)
write("gm_proposal.json", proposal)
write("gm_verdict.json", verdict)
print(json.dumps({"proposal": str(work / "gm_proposal.json"), "validation": verdict,
                  "requested_approval": approval_request}, ensure_ascii=False, indent=2))
```

这个脚本使用现有 `src/gm_core/decisions.py` 校验完整外层提案。`calculation_refs:[]`表示本例没有另行引用计算产物；实际引用数值计算时必须填入真实计算ID，并在验证CLI传同批 `--run`，不能编造引用。篮球理由若引用阵容、合同或统计，应把相应已发布JSON字段加入 `evidence`；本例仅演示教练设置合同，不替玩家生成正式篮球决策。

可以再用现有外层CLI校验文件（完全离线）：

```powershell
python -B scripts/gm_validate_proposal.py --save-id '<实际career_id>' --proposal _exports/coaching_example/gm_proposal.json
```

得到 `valid=true` 仍是结构和来源校验，`execution_authorized=false/player_approval=NOT_GRANTED` 保持不变。`requests.json`不是可执行batch；`gm_proposal.json`也不能作为 `--batch` 输入。执行器读取其中由程序生成的 `coaching_batch`，即 `batch.json`。四套Freelance可在requests中用 `freelance_sets:[slot1,slot2,slot3,slot4]`；生成后会正规化为具名槽的changes。

若网页GM不能运行本地CLI，它只提交篮球意图和真实来源引用，由获委派的本地模型运行上述离线生成和外层校验后再呈交摘要审批；不得由模型补写native身份或前值。完整外层JSON应使用实际生成的文件交接，无需在聊天中手抄30队原始块。

## 批准与生命周期

玩家逐批明确批准 batch_id/decision_id/version/action_ids/digest 后，才交执行角色按 `docs/40_COACHING_EXECUTION_RUNBOOK.md` 操作。任何目标、范围或版本变化都需重新批准。执行回执 `COMMITTED_VERIFIED_IN_MEMORY` 只证明内存提交；游戏保存及后续数据更新各由玩家单独触发。

执行角色顺序调用脚本，不组织并发写入。若收到共享执行锁或未恢复告警，保留当前提案与缺口，不通过更换批次、career标签、工作树或日志目录绕过执行端人工审阅。

GM 赛季聊天按玩家触发的月度、交易截止、季后赛和休赛期节点继续；不自动触发下月、采集、比赛模拟、写入或发布。数据陈旧、换帅、来源缺失或字段门槛关闭时输出具体缺口和 HOLD，等待可信来源或开发验收。

## 原生 Freelance 完整目录（同版本可执行文件 CRC 对应）

下列名称来自已加载原生枚举与同 PE 游戏字符串的唯一 CRC 对应，不编造中文译名。四槽按原生字段顺序提供完整目录；玩家已取消重复菜单验收，当前可执行状态以本批字段字典为准，不宣称已直接验证比赛内中文页面或保存持久性。

| Raw | 原生名称 |
| --- | --- |
| 0 | `DEFAULT` |
| 1 | `TWO_MAN` |
| 2 | `THREE_MAN` |
| 3 | `THREE_OUT` |
| 4 | `WNBA_THREE_OUT` |
| 5 | `FOUR_OUT` |
| 6 | `BUCKS_2018` |
| 7 | `CLIPPERS_2018` |
| 8 | `DENVER_2018` |
| 9 | `HAWKS_2018` |
| 10 | `JAZZ` |
| 11 | `MAVERICKS_2018` |
| 12 | `PELICANS_2018` |
| 13 | `PHILLY_ELBOW` |
| 14 | `PISTON_SNAP` |
| 15 | `SPURS_2018` |
| 16 | `WARRIORS` |
| 17 | `FLIP_PUSH` |
| 18 | `FLOW` |
| 19 | `FORTY_THREE` |
| 20 | `FOURTEEN` |
| 21 | `PACE` |
| 22 | `POINT_FREELANCE` |
| 23 | `PRINCESTON_CHIN` |
| 24 | `SEVEN_SECONDS` |
| 25 | `SLICE` |
| 26 | `SWING` |
| 27 | `TRIANGLE` |
| 28 | `TWENTY_ONE_DELAY` |
| 29 | `BULLS_88` |
| 30 | `CELTICS_86` |
| 31 | `EIGHTY` |
| 32 | `FREELANCE_ONE` |
| 33 | `FREELANCE_TWO` |
