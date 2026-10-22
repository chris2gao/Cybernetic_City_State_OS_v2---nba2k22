> **2026-10-17 最新状态（覆盖以下V2的阶段叙述）：玩家已转交Codex只读原生内存调查，默认POE为`COACHDATA+0x13C`六个5-bit字段，并发现旧`TEAM+0xEB2`策略writer不安全。** 本研究任务保留历史背景，后续产品工程请**优先执行 [DEV-20261017-06 正式开发任务书](DEV_20261017_06_COACHING_IMPLEMENTATION_V1.md)**；研究摘要及证据边界见 [只读交接](../development_reviews/DEV_20261017_05_COACHING_READONLY_HANDOFF.md)。不要按本文件早期旧POE枚举或先做赛果A/B测试；Codex必要技术安全检查后开发，游戏战绩效果由玩家推进一个游戏月后验证。此页尚不能证明生产写入成功。

# DEV-20261017-05 — NBA2K22 PC 教练攻防、模拟策略与战术手册：内存定位 → 条件开发 → 玩家月度验证 V2

> 状态：MEMORY_DISCOVERY_THEN_IMPLEMENT / GAMEPLAY_EFFECT_TEST_PLAYER_MONTH_END  
> 2026-10-17 · Web GPT DEVELOPMENT → Codex DEVELOPMENT  
> 仓库：`chris2gao/nba2k22-gm-engine`；游戏：**NBA2K22 Windows PC，2021–22 赛季起**。严格区分PC/MyLeague与PS5/XSX次世代MyNBA；当前玩家多为快速模拟对战。  
> **2026-10-17 玩家后续指令优先于旧V1：Codex 先进行 UI/内存定位和最小字段安全核验，一旦确认可实现，即允许在本轮任务中继续编写正式功能；不要安排由Codex在开发前做多批模拟比赛测试。功能交付后由玩家本人在游戏内运行一个游戏月，再独立触发比赛数据采集与网页分析评价效果。** 开发授权不等于GM决策、正式存档写入、自动推进游戏或玩家正式执行批准。  
> 规则：`config/gameplay_policy.json` (`PLAYER_RULES_20261017_V3`)；任何正常球员能力、潜力、徽章、倾向、性格修改仍禁止，教练战术不能绕开该限制；游戏写入需独立、具体玩家批准。

## 0. 研究目的和最终设计边界

用户表示 NBA2K22 的教练菜单可配置每队攻防和Playbook，实际比赛时 CPU AI 会动态调整，但普通快速模拟是否读设置、是否AI改写设置尚未知。Codex 已找到部分策略地址。本轮不是“设计一个新的比赛引擎”，而是**验证原生游戏已有控制量的准确位置、作用范围、枚举、持续性和普通快速模拟是否真正使用**，从而给网页GM开放有意义、可审批的球队级策略决策。

**开发价值预判**：优先球队级Sim POE、教练轮换/体系、战术手册；比赛中实时ACE的改写暂缓。四种状态独立：`MAPPED`（UI与内存定位）/ `SAFELY_WRITABLE`（隔离测试存档技术核验）/ `IMPLEMENTED`（正式接口代码交付）/ `SIM_EFFECT_OBSERVED`（玩家运行一个游戏月后有来源数据支持）。不得以尚未进行月度比赛测试阻塞已证明技术可行的字段开发，也不得先声称战术提升胜率。

**特别注意四个不同对象**：
1. 联盟级 `Simulation Sliders`（全联盟、可能影响模拟算法）：只做实验环境参数记录，绝不能当30队独立GM策略。
2. `Sim Points of Emphasis`（球队级模拟重点）：优先验证，但不能默认已有Team结构偏移正好对应Sim POE。
3. `Coach Gameplan / Coaching Sliders / Defense Settings`：可能有 All Teams 默认方案、指定对手的单独 Gameplan、比赛内临时值、以及 AI 的 ACE/教练自动调整；必须分作用域。
4. `System Proficiency / Playbook / Freelance`：教练偏好、球队激活体系、战术列表和比赛临时调用池可能是不同数据对象；不能只找一个整数即宣布覆盖完整战术手册。

## 1. 可核对资料及证据强弱

### 较直接关联 NBA2K22
- [NBA2K22 Attention to Detail Roster 说明](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/)：社区团队专门为30队修订Coaching Profiles/Coaching Sliders和POE以优化模拟统计。证明有人按此路径调校，不证明具体单字段因果或代码偏移。
- [2K22 MyLeague simulation sliders，PS4帖子](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)：展示全联盟Simulation/Team Style Factors等与游戏内比赛Sliders分开；这些是**联盟级**设置，项目中不应被当作单队GM旋钮。
- [2K22 教练菜单防守策略讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917100-nba-2k22-the-eccentric-edition-realistic-ng-slider-set/page11?postcount=140)：针对实战游戏，由社区描述根据对手调整Help Defense、手动gameplan，不能直接推断快速模拟效果。
- [2K22 轮换保存问题](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/920193-mynba-rotations-not-saving)：玩家报告游戏自动轮换、Lineup Performance Factor/Player Minutes开关和保存行为可能影响可持久化性；需用PC实机核对。

### 跨版本概念表（作为Codex的UI核对清单，不得作为2K22 PC的最终枚举）
- [MyLeague旧版Sim POE完整选项讨论](https://www.reddit.com/r/NBA2k/comments/i2g4bi/)：六类Focus、Tempo、Off Rebounding、Def Focus、Aggression、Def Rebounding的英文枚举候选。
- [旧版Sim POE影响快速模拟统计的经验研究](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/922628-getting-realistic-myleague-2.html)：有对统计分布的观察，不等于2K22 PC版本已验证。
- [篮球2K Coaching 模块说明](https://nba2k.fandom.com/wiki/Coaching)：游戏系常见 Coach Gameplan、System Proficiency、Edit Playbook菜单和8类战术体系；不应全部视作2K22当前UI固定项。
- [旧版MyLeague Sim POE/教练滑块提纲](https://gamefaqs.gamespot.com/boards/2000208-sports-and-racing-nba/76861758)：Help Defense/Run Plays/Zone Usage及选手主要得分选择，跨版本候选。
- [2K官方2021-09-08 NBA2K22 Next Gen MyNBA公告](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)：Conditional Coaching在模拟中触发条件指令，但官方注明PS5/XSX，**不能在PC本项目上认定已存在**。

## 2. Codex 第一阶段：游戏UI枚举台账（不要先猜内存）

在复制的NBA2K22 PC 终极联盟存档打开教练设置，逐项截图并手动归档：菜单路径（中文/英文）、是否每队可独立控制、是否默认和对手专属分层、所有UI合法取值及默认值、读取/修改后UI是否即时刷新、存档再开是否保留。

候选清单如下。每项都要标示 `PRESENT_PC22|ABSENT_PC22|NOT_CHECKED`，没有的不要硬猜或从别的版本补入。未知初始为NOT_CHECKED。

### A. Sim POE（最高优先级，6组）
1. `sim_offensive_focus`：Neutral / Play Through Star / No Preference / Get to Basket / Get Shooters Open / Feed Post / Pick & Roll 等旧版候选；逐项核实。
2. `sim_offensive_tempo`：Average / Shoot at Will / Patient / No Preference 候选。
3. `sim_offensive_rebound`：Some Crash / Limit Transition / Crash Glass / No Preference 候选。
4. `sim_defensive_focus`：Neutral / Limit Perimeter / Protect Paint / No Preference 候选。
5. `sim_defensive_aggression`：Neutral / Play Physical / Conservative / No Preference 候选。
6. `sim_defensive_rebound`：Some Crash / Run in Transition / Crash Glass / No Preference 候选。
- 若UI存在 `first_scoring_option`、`second_scoring_option`、`third_scoring_option`，另归档；如游戏版本已移除，记为ABSENT，不用人物倾向修改来替代。

### B. Coaching Sliders / Coach Gameplan
- `help_defense`（协防强度）、`run_plays_frequency`（战术执行频率）、`zone_usage`（区域联防频率）。
- `bench_depth`（轮换人数）、`bench_utilization`（替补使用比重）、`lineup_performance_factor`（若有）。
- 每名球员的上场分钟、首发、替补排序与On-the-Fly Lineups，球员必须使用已验证身份，不凭姓名/指针持久关联。
- `player_minutes_auto`、替换模式（轮换/体能）、`ACE`启用状态、进攻/防守自动叫战术：要区分**球队配置 / 玩家本地控制选项 / 比赛临时状态**，不可默认这些都属于每队可控制属性。
- 多队或仅单队可编辑问题，Codex需实机辨别。

### C. 教练体系
- `system_preferred` / `system_active`：Balanced、Grit & Grind、Pace & Space、Perimeter Centric、Post Centric、Triangle、Seven Seconds、Defense这8类是已有`STAFF` profile编码的初步候选。
- `system_proficiency` 是否是只读派生评价、可手动设置或主教练-球员融合计算，**不得直接修改派生分数以提高胜率**。如只有系统选择可写，只使用合法选择，不注入熟练度。

### D. Playbook / Freelance / Plays
- Playbook选择对应的playbook ID / 名称；每队战术本引用、战术数目、各项战术条目ID和顺序；Edit Playbook更换操作。
- Freelance offense（若可选）：方案、Series选项、调用优先级、ACE/手动叫战术关系。
- 注意“战术本改名/ID”“教练战术调用概率”“球员Play Types/Touches”可能属于不同层；**本项目禁止通过改球员的个人倾向或Play Types来配合战术**，最多用其已采集事实做GM分析。

### E. Defensive Settings / Defensive Matchups（优先定义目录，不默认可用于快模拟）
- 队级：On-Ball Pressure、Off-Ball Pressure、Force Direction、On-Ball Screen、Hedge、Center对应两项、Stay Attached、Off-Ball Screen、Post、Perimeter Double / Post Double、Switch Rules、Pre Rotate、Screen Help Rules、Drive Help Rules；如实际UI存在DHO相关选项也纳入。
- 球员对位级：防守目标、指定防守者、按对手个人的压迫及挡拆方案；记录是否 per-opponent 存储、对手球员转会后是否自动失效。
- 比赛临时值：暂停界面/On-The-Fly修改是否仅影响单场，并与赛前Gameplan内存作对照。
- 快速模拟是否真正使用这类防守设置先标记 `SIM_EFFECT_PENDING_PLAYER_MONTH`；即使技术可写也不能提前宣传效果。

### F. 全联盟 Simulation Settings（仅记录月度分析背景，不为GM独立修改）
- Simulation Difficulty、Simulated Quarter Length、Team Pace/Team Fastbreak、Possessions、Shots、Assists、Shot Types 等。
- 记录玩家当前游戏的全局设置，供一个游戏月后排查比赛数据变化；不得以全联盟滑块实现针对一支球队的战术增强。

## 3. 现有仓库线索和必检异常

- `src/strategy_manager.py` 已提供 `StrategyManager.get_team_strategy/set_team_strategy`，候选Team结构偏移：
  `0xEB2 OFF_PACE`、`0xEB3 FASTBREAK_FOCUS`、`0xEB4 OFF_REBOUND`、`0xEB5 DEF_REBOUND`、`0xEB7 ON_BALL_PRESSURE`、`0xEB8 OFF_BALL_PRESSURE`、`0xEB9 PICK_AND_ROLL_DEF`、`0xEBC HELP_DEFENSE_LEVEL`。这些并未证明是**Sim POE**，可能只是球队比赛策略。
- 旧 `docs/13_TACTICAL_STRATEGIES_AND_BUSINESS_OPERATIONS.md` 含由注释推断的取值和“某体系熟练度95”建议，以及与 `strategy_manager.py` 参数名不完全一致的示例。它是**历史规划/线索，不是实机枚举认证、百分百生效或能力改动授权**。
- `config/gm_policy.json`中的 `poe_on_ball` 明确为`UNVERIFIED_ENUM_CONFLICT_OBSERVED_7_VS_LEGACY_0_TO_4`；旧取值0..4/0..6或历史读到7互相矛盾。无需急于统一，先UI单变量测试确认范围、含义及bit-packed的可能性。
- `config/memory_field_profile.json` 的 `STAFF` 有`preferred_system`、`active_system`三bit字段（需由教练对象定位和岗位关联支持），但不是`TEAM`长期战术引用已认证的证据。
- `src/gm_core/tactics.py` 目前是分析+占位验参，不是可用游戏执行器；`src/gm_core/coverage.py`部分team POE已作为observed观测；无已验收的Playbook、SimPOE完整字段采集器/运行中按对手指令执行器。
- `src/strategy_manager.py` setter只检查uint8 0..255，不验证游戏合法枚举/目标队伍重复身份/共享位掩码/事前授权；不能因写后readback一致就认为游戏战术有效。应核实写入权限、参数名，禁止旧文档未经验证的`pnr_def`示例误导开发。
- 先对 `src/address_calibrator.py`、`src/source_extensions.py`及现有源profile进行复用，不发布指针/未经认证的值作为永久球员或球队ID。

## 4. Codex 第二阶段：UI ↔ 内存定位协议（复制测试存档）

每个字段单独做最小观察：
1. 在复制存档记录进程PID、版本、save ID、当前球员名单、球队内部`team_id`/教练身份、Gameplan范围(All Teams/指定对手/当前比赛)、当前UI原值与字节/结构快照。
2. 在游戏菜单**只改动一个选项**，例如从A→B；在静态会话对比内存变化，排除镜像、UI缓存、别的同时变化参数以及菜单切换噪声。观察是Team结构、Coach结构、League settings、opponent-specific表、playbook数组还是比赛临时对象。
3. 依次测试不同取值B→C→A，反证：恢复原UI值后，候选字节应可逆回到原始值。针对按位编码必须验证读写仅变目标bit，保留同字节其他flag；数组必须校验长度、元素类别和引用完整性，不以固定偏移的整个内存块覆盖。
4. 更换第二支球队同样修改同一UI项，验证两个独立owner的映射；返回第一队确认值没有被全局覆盖；更换指定对手重复以识别对手级索引。注意“选择球队”不一定等于实际控制者，验证对象和场景作用域。
5. 经本轮玩家研发调研许可，若需要验证直接内存写入，只允许在**隔离复制测试存档**对一项已知合法UI枚举做最小可逆写入，遵守当前程序写入权限；观察UI反向更新、返回菜单/进入比赛、存档关闭重开。未具备可信指针/bit语义时保持只读，不试验多字节猜写。
6. 验证最低限度保存持久性：当前游戏菜单值→退出菜单→保存→退出游戏→重启读取；另检查切换球队/教练和对手时的作用域。**跨游戏月份/赛季的持久性与AI比赛中覆盖，留待玩家后续游戏月度反馈**；只有临时比赛对象不得当作长期球队配置。
7. 开发阶段只检查最小技术覆盖风险（切换菜单/球队、保存重启、教练变化等），不要求Codex运行多批快速模拟、SimCast或CPU-v-CPU效果测试；模拟过程中的AI覆盖与比赛效果由玩家首个游戏月后按实际数据与字段回读核查。未测标`AI_OVERRIDE_DURING_GAME_UNKNOWN`。
8. 记录`enum_map`：UI中文名/英文名、encoded raw value、类型/bit宽、合法范围、拥有对象ID、来源证据、作用域、存档持久性、当前是否授权/只读。不能用`uint8 0..255`作为合法游戏枚举。
9. 每个重要结果需至少另一支球队和重启进程复验；不要把工作内存指针写进跨存档身份标识。

强制失败状态：`NO_UI_FIELD`、`AMBIGUOUS_ADDRESS`、`UNVERIFIED_ENUM`、`WRITES_NOT_PERSISTENT`、`AI_OVERWRITES`、`WRONG_SCOPE_LEAGUE_GLOBAL`、`NO_SAFE_WRITE_PATH`；允许部分字段通过，不要求全部通过才产出调研结论。

## 5. 开发完成后：玩家一个游戏月的比赛数据效果验证（替代旧A/B模拟实验）

**本节为新强制流程，覆盖V1中Codex开发前20场/100场模拟分组验证要求。** 不需要Codex为验证战术胜率去批量模拟、改变游戏时间、开展CPU-v-CPU实验。发现安全可用的内存字段后，直接实现对应功能。

### 5.1 开发交付前必须保留的“基线”
- `save_id`、游戏赛季与用户确认的游戏日期、最新`source_batch_id`、`data_updated_at`和`policy_id`。
- 每队真实战术初始值、实际通过GM提案的目标值、合法枚举及对应教练/球队身份；应用状态`PROPOSED|PLAYER_APPROVED|EXECUTED_VERIFIED|BLOCKED`，执行回执记录确切生效游戏日期/月份。没有实际执行就不能称球队战术已经生效。
- 保存玩家触发的**变更前**比赛来源快照（赛季累计胜负/球队累计技术统计，凡字段未观测均保留NULL），可复用已有同一赛季数据；不允许Codex为了本次开发自动刷新正式存档或发布数据。若缺前置批次，应标`BASELINE_MISSING`并提示玩家单独触发数据采集。
- 技术交付保留精确UI↔RAM映射、合法取值、最小隔离测试存档的字段回读/恢复与保存重启、安全执行路径、审批保护；只要求常规代码验证与必要内存安全检查，不要求赛果统计测试。
- 除非玩家批准具体球队、字段、前后值，**不可对正式游戏存档下发战术变更**。游戏中第一次真实应用战术的时间应晚于批准与执行回读。

### 5.2 玩家操作与月末反馈
1. 玩家在游戏内正常推进**一个游戏月**，不由开发脚本自动推进赛季或模拟对照。赛季中如有交易、球员离队、教练变更、伤病等会影响解释，应在可用来源内记录。
2. 玩家月末独立触发Codex比赛数据采集，然后独立触发Web GPT ANALYTICS计算，最后按需触发同一赛季GM窗口审议。不自动串联。检查最新CLI是否真正支持只采集比赛来源；未实现则先征求玩家指定可行采集模式。
3. 同一存档/赛季/统计口径、同一累计窗口且游戏日期未回退时，以 `ΔW`、`ΔL`、`ΔG`计算游戏月胜率`ΔW/ΔG`。球队技术统计必须对**累计总量**先做两期差，再除以本月场数；不能直接对两次“赛季至今场均”求差宣称本月场均。跨赛季或缺少可比统计返回`MONTH_COMPARISON_INVALID`。
4. 分析已观测的每队得分/失分、三分出手、篮板、助攻、pace等变化（如有可靠累计统计和分母），记录各队是否实际调整、战术类型、哪一天起生效、当月比赛样本与对手强弱。不能凭不存在的逐场统计、年龄/OVR或隐藏战术调用数据填补因果链。
5. 如果首月数据好转，标记`EFFECT_OBSERVED_MONTH_1`，**不等于因果已证实**；如果表现无明显变化，标记`NO_EFFECT_DETECTED_YET`。样本不足、时间或来源不符为`INSUFFICIENT_DATA`；如果配置被AI覆盖，标记`POSSIBLE_AI_OVERRIDE`并交开发基线另行修复。
6. 分析角色输出`ANALYSIS_ONLY`量化包，GM根据30队经营目标解释战术价值，开发基线只处理技术缺口。用户可在下个游戏月继续自然复盘，不自动生成任务。

**首月重点**：评估实际游戏运行的配置是否持续、球队风格与效率是否变化，区分共时发生的交易、对手与阵容变化。普通快速模拟、SimCast和实机比赛的来源若未明确标注，不能跨模式推断。

## 6. 可行字段正式实现的GM提案契约（允许Codex开发）

Codex完成字段技术可行性验证后即可实现以下已认证字段的只读/受控执行代码和GM提案契约，实际比赛效果在一个游戏月后验证。GM可提出三类方案：
- `SEASON_TEAM_TACTIC`：30队长期默认方案。每队一组经验证的`sim_poe`、`system`、`coach_sliders`、`playbook_ref`、轮换。一般季初/交易后/每个玩家触发的GM节点复核，控制改变次数，不保证“一改就赢”。
- `MATCHUP_TACTIC`：针对指定对手的赛前布置，若已确认存在`per_opponent`独立数据对象、合法枚举及安全写入，即可开发为**仅技术可用且模拟效果未知**的功能。目标对手和球员身份必须核验；快模拟真实作用由玩家月末数据和后续实测决定，未验证前不承诺能优化模拟胜率。
- `IN_GAME_TEMPORARY`：比赛内ACE/临时指令，暂缓开发，不覆盖原生AI；必须显式区分正在跑的比赛引擎临时数据与长期球队设置。

拟实现的`tactics_plan.json`提案应携带：
`career_id`、`season`、`game_date`、`source_batch_id`、`policy_id`、`decision_id`、`version`、`status=PROPOSED`、`team_id`、`coach_id`、`scope=TEAM_DEFAULT|VS_OPPONENT|IN_GAME`、`opponent_team_id?`、`changes:[{field,old_raw,proposed_value,enum_version,source_evidence,effect_scope,readiness}]`、`expected_effect`、`unknowns`、`rollback_plan`。
批准后的执行器还需玩家具体批准、目标球队/教练/存档身份复验、原值检查、白名单映射、逐字段写入/回读、失败回滚、存档重启校验与执行回执；任何MODEL传入的`approved=true`不得当作授权。禁止分析侧`src/gm_core`import游戏写入/内存模块。

## 7. 阶段门槛：技术可行即可研发，游戏内效果玩家月末验证

**先定位并验证安全性，马上进入可行字段研发；比赛效果不再是研发准入门槛。**

- G0 `UI_CATALOG_COMPLETE`：NBA2K22 PC实际菜单选项、合法枚举、球队或对手作用域已记录；不存在的标NA。
- G1 `MEMORY_MAPPING_VERIFIED`：可重复的UI↔RAM映射、不同球队隔离、原值恢复、必要保存重启验证；歧义字段保持UNKNOWN。
- G2 `SAFE_WRITE_FEASIBLE`：隔离复制存档最小技术写入、合法枚举、备份/回滚、字段原值/目标值回读；无不可控副作用。**G0/G1/G2在确认的字段子集上成立后直接进入代码实现，不必先证明战术对模拟胜负的统计影响。**
- G3 `IMPLEMENTATION_DELIVERED`：实现GM只读字段、方案校验与受控执行器；覆盖批准来源、具体球队/字段/原值、只改合法范围、回读、失败处理和回滚；交源码、必要代码测试、提交与能力说明。不得写正式存档/自动发起GM。
- G4 `PLAYER_MONTH_GAMEPLAY_VALIDATION_PENDING`：Codex完成研发后明确停在这里；等玩家亲自游戏内运行一个月，并分别触发数据更新、分析、GM复核。游戏效果报告由后续真实来源产生。
- 不支持/未能安全写入的字段可独立标`UNSUPPORTED`或`BLOCKED`，不因其他字段可开发而冒充也已支持。
- 如果技术上只发现普通比赛方案，没有可定位的独立Sim POE，也可以先交付“实际比赛战术控制”可行子集，但必须把快速模拟效果状态保留UNKNOWN，不能声称全部模拟用战术已实现。

## 8. Codex 必须提交的研发结果

**保留最初约定的调研输出，并新增实现结果：**
- `docs/development_reviews/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_REPORT.md`：UI、字段来源、地址定位、技术风险、可写入范围。
- `docs/development_reviews/DEV_20261017_05_COACHING_FIELD_MATRIX.json`：字段矩阵，细分`ui_memory_roundtrip`、`technical_write_safe`、`implemented`、`sim_effect=SIM_EFFECT_PENDING_PLAYER_MONTH`，不能把未进行的比赛实测填成True。
- 实现源码和接口：按代码规范选择路径。建议离线GM候选/提案接口放`src/gm_core/`纯计算层，现场受控执行放独立Codex本地执行模块，二者不可直接相互导入内存写模块。全联盟Simulation Sliders不作为球队级战术设置。
- `docs/development_reviews/DEV_20261017_05_COACHING_IMPLEMENTATION_REPORT.md`：真实提交SHA、已实现字段、技术测试与未测内容、如何供玩家单独批准执行、正式月度效果待确认及所需前后批次。
- 更新`docs/34_BASELINE_CURRENT_STATE.md`与必要接口文档，只能把已开发且经过技术核验的内容标为实现；游戏效果状态仍是`PENDING_PLAYER_MONTH`，不得声称已提升30队战绩。

字段记录基础示例：
```json
{
  "ui_path": "Coaching > Coach Gameplan > ...",
  "ui_label": null,
  "feature_group": "SIM_POE",
  "scope": "TEAM_DEFAULT",
  "game_platform": "PC_NBA2K22",
  "owner": {"team_id": null, "coach_id": null, "opponent_team_id": null},
  "address_status": "UNVERIFIED",
  "location": {"base_structure": null, "relative_offset_hex": null, "width_bits": null, "bit_offset": null},
  "enum_status": "UNVERIFIED",
  "choices": [],
  "ui_memory_roundtrip": false,
  "technical_write_safe": false,
  "implemented": false,
  "sim_effect": "SIM_EFFECT_PENDING_PLAYER_MONTH",
  "evidence": []
}
```
报告须标注实际游戏版本、复制测试存档、字段所属结构、合法选项、不同球队隔离性、保存持久性、技术写入风险与Codex真实完成能力；未执行赛果测试不得填报改善比例。调研及开发不上传包含个人信息的内存转储，不顺带改`published/`、玩家正式方案或策略属性。

## 9. 给Codex的新执行顺序（玩家已调整）

1. 查Git状态与真实HEAD、重新读开发基线与玩家规则。
2. 在NBA2K22 PC游戏界面确认字段与合法枚举，重点Sim POE、Coach Sliders、体系、战术手册、队级/对手级策略。
3. 在隔离复制存档定位UI↔RAM、验证对象归属和最小可逆安全读写及持久化。**只做技术验证，不先跑大量比赛**。
4. 一旦确认某字段/模块确实可以安全实现，**直接开发GM读写/提案及受控执行模块**。无需先证明“模拟胜率变化”；不能安全定位的字段不开发。
5. 进行必要代码测试、文档更新、提交GitHub，记录准确的技术能力和`SIM_EFFECT_PENDING_PLAYER_MONTH`，汇报实施接口及待批准项。Codex开发到此停止。
6. **玩家**另行批准具体战术并在游戏里执行，随后自行推进一个游戏月；月末**玩家单独触发**比赛数据采集→分析→GM评估，最终确认效果。不创建后台自动流水线、不借开发授权改正式存档。
