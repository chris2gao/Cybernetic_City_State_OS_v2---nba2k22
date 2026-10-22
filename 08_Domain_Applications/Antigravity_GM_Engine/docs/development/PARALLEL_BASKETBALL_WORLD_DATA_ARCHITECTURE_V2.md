# NBA2K22 平行篮球世界：数据架构与整体重构蓝图 V2

**2026-10-22；项目级目标架构/数据建模设计基线（尚未批准实施迁移）。** 本文件取代[V1](PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V1.md)中“必须复用原双事实库物理Schema/不能重新设计数据库”的限制。保留V1作为历史决策记录；本文优先。相容原则、研究证据与待验证项必须分开，不代表任何AG模块已经通过Codex生产验收，不批准实机修改、生产迁移、删除原库或游戏推进。

## 0. 正式纠错：旧库是迁移来源，不是设计约束

**以完整NBA2K22平行篮球世界为第一原则，允许重新设计整个采集容器、数据库文件边界、主键、表、关系、历史模型、API和发布布局。** 原有`league_state.sqlite`/`player_pool.sqlite`、`database/schema.sql`、月度事实表和自动采集脚本属于第一代实现；不能因已运行而强制新数据适应旧Schema。

应**复用的是被验证过的能力、游戏事实、权限边界和工程不变量**，不是必需维持的表名/文件数/数据列。不可牺牲的原则包括：NBA2K22游戏引擎是比赛和自然成长的权威；逐案玩家批准游戏修改；来源与save/generation/batch绑定；隐藏Potential不向GM公开；失败不发布伪完整数据；不伪造没有真实采集的比赛和历史；可回滚迁移与独立验收。

当前旧Schema存在结构性问题：`players`融合身份、合同、能力及当前状态；`player_monthly_stats`混合能力、合同、伤病与赛季结果；`player_season_stats`大量只有派生场均值且必填；`seasons`只用年份标识；部分历史以姓名为联系字段；`monthly_snapshots`被当作自然时间粒度。需要进行完整逻辑建模，而不是无限增加现有表列。

## 1. 五层技术系统，不变的六阶段角色流程

1. **Game authority**：NBA2K22 PC MyLEAGUE原生比赛、自然成长、规则、存档。
2. **Native acquisition/adapters**：版本签名→Getter/内存数组/原生索引→只读原始观察→字段解码；UNKNOWN与代码版本保留；可替换采集容器。
3. **Parallel World Data Platform**：对象身份、逐场事件、各类状态快照、长期历史、原始证据、派生视图和审计质量，结构可整体重构。
4. **Multi-actor world**：数据分析、独立教练/球员/GM等模型按获准可见性使用数据，自由决策；原生数据基础设施不冒充独立人格。
5. **Approved execution**：动作意向→游戏规则校验→玩家批准→有限执行→原生状态回读→历史审计。

**技术五层≠操作六阶段**，继续遵守采集→分析→教练→球员→GM→汇总执行。数据读写与AI决策/修改权限相互分离。

## 2. 先定领域与时间身份，再定SQLite物理文件

### 2.1 主要领域聚合与候选实体

| 领域边界 | 概念实体（逻辑层，不等于马上创建同名物理表） | 数据生命周期 |
|---|---|---|
| WORLD/TIME | World、SaveInstance、Generation、Season、Phase、CaptureBatch、GameCalendar | 多存档/分叉/赛季/批次 |
| ENTITY/IDENTITY | Person、PlayerIncarnation、StaffRole、Franchise、TeamSeason、DraftTemplate、NativeIdentityMapping | 身份历史/防重号/防名字歧义 |
| ROSTER/CONTRACT | TeamMembership、RosterAssignment、Contract、ContractSeason、WaivedSalary、PickAsset、PickOwnership | 随游戏时间变化的权益与合同 |
| GAME | Game、TeamGameStats、PlayerGameStatline、LineScore、BoxExtra、GameStatus | 比赛发生及后来更正/阶段变化 |
| STATS/HISTORY | PlayerSeasonTotals、TeamSeasonTotals、CareerHistoryLink、RecordBook、SeasonAwards、HistoricalEvent | 原生累积、跨季保留 |
| PLAYER_STATE | PlayerAttributeObservation、TendencyObservation、BadgeObservation、Morale/Role、Injury、Training | 按观测时间有效，不等同比赛流水 |
| COACH/TACTICS | CoachAssignment、System、Playbook、Play/PlayType、Gameplan、TrainingSetting、TacticalObservation | 配置、历史及其适配观察 |
| LEAGUE/MARKET | SalaryCapRule、TeamFinanceObservation、StaffMarket、FreeAgencyOffer、TradeProposal、Draft/Scout | 原生观测和获准外挂规则分层 |
| AGENTS/ACTIONS | ActorVisibleView、Proposal、Approval、ExecutionAttempt、ReadbackReceipt、AnalysisArtifact | 有效权限、决策记录和执行证据 |
| NATIVE_EVIDENCE | ObjectType、NativeRecordObservation、FieldEvidence、SourceManifest、Coverage/QualityReport | 原始来源、布局版本、裁剪/遮蔽 |

**按原生结构与真实业务关联确定最终关系模型**。UI菜单与统计分类成为验收视图而不是“一页一表”。G联赛/新秀报告尚未解证时只保留候选关系，不抢设已实现实体。

### 2.2 永久身份与历史选秀轮回

必须区分：
- `world_id`：同一平行篮球世界线；
- `save_instance_id`、`generation_id`：存档身份、恢复或分叉代际；
- `season_id`：属于一个world的具体赛季，不仅是2022这个年份；
- `game_uid`：世界线+赛季+有效比赛原生身份（复赛/赛事类型/代际冲突需查清）；原生GameID、Slot仅为映射值；
- `player_incarnation_id`：在本游戏世界线实际存在的一个球员实例，不能简单等同姓名、Cyberface、模板球员或短期内存Slot；
- `draft_template_id`：1984–2020轮回历史选秀素材的模板身份，与当年新生成的`player_incarnation_id`分离；
- `team_identity_id`与`team_season_id`：稳定球队身份与跨季阵容/更名/扩张状态分离；
- 游戏原生指针、数组索引、PLAYER ID都必须具备版本与作用域验证，不能直接当跨存档永久主键。

当前难点（native PlayerID是否复用、GameID在哪些赛季/比赛类型唯一、场次赛后覆盖行为）由Codex验收并写进身份策略，不预先杜撰。

### 2.3 时间模型：事件、快照与观测三种不同事实

- **事件事实**：已经完赛的单场Box、真实交易及执行回执、选秀/奖项等，以可追踪事件身份和来源版本入账；逻辑上append-only，可有订正版本，不把新快照覆盖旧事件。
- **状态观察**：球员能力/士气/伤病、名单、教练设置、合同/球队财务；采集的是“在何时看到何值”，相同实体随时间形成状态序列。
- **原生累计**：Slot 24赛季统计和生涯索引是某一时点游戏的累计观测，与逐场累计进行可加性校验，但不能把月度均值伪装成独立比赛事件。
- **两套时间**：游戏内有效时间（赛季、阶段、比赛日期）与现实采集时间（observed_at/ingested_at），以及source版本/批次，分别保存。
- **历史事实不补造**：过去未采到的原生比赛流水不能凭当期赛季总分复原；原生历史纪录、赛季汇总、用户确认日期与实时内存读回必须显式不同证据等级。

### 2.4 原生字节、规范事实、计算结果分别存放

1. `raw observation`：原始固定长度字节或有界安全摘要、offset/stride、layout版本、可见性与敏感裁剪、fixture哈希。
2. `decoded native facts`：单位、位宽、枚举、身份链、真实时间范围、已知/UNKNOWN状态；与raw source一一关联。
3. `canonical domain facts`：在校验后建立可用事实视图，保留冲突及版本；同一Game的新观测不能盲目`REPLACE`旧子表。
4. `derived statistics`：PER/TS%/eFG%、Win/Loss/Starter/Bench/Home/Away/Last5等需保存口径、参数、公式版本和源集合；不能伪装为原生UI值。
5. `AI analytics`：教练分析/GM提案与真正比赛数据分层存放，不能从分析稿反写游戏真实事实表。

## 3. 物理存储：SQLite优先，但库的数量可以重构

推荐**SQLite作为当前首选引擎**：单机Windows游戏外挂、确定性采集、离线查询及几十个赛季的比赛/球员量级均有合理适配性。先做明确数据量、索引/事务及查询性能基准，达到限制再选择别的引擎，不因历史代码拘泥两文件。

**推荐物理候选方案（待架构评审与基准测试定稿）**：
- `world.sqlite`：同一个存档世界线的实体、关系、比赛事实、赛季累计、状态/历史观察、业务视图；优先保证同一世界线跨表事务与外键。
- `native_archive.sqlite`或带清单的原始证据文件：高体积原生记录、敏感隔离原始源、布局/Decoder版本与hash；取决于体积及可见性，不能直接公开未脱敏字节。
- `control.sqlite`：批次、生命周期、审批、执行回读、审计/迁移/来源发布控制；可与现有DEV14控制库兼容迁移。
- 独立模板/资源库（可选）：历史DraftTemplate、真实世界研究目录与静态资产，不能与当前已生成球员实例混淆。

这只是**一个可评测的物理切分**，不是对新文件名/文件数的永久约束。可以根据交易一致性、数据量、敏感隔离与AI查询性能选择合并或进一步拆分。SQLite跨文件无通用跨库外键保障；若多文件发布，必须保留/重构DEV14的完整批次manifest、跨文件hash、暂存安装与崩溃恢复机制，不把单文件事务冒充原子发布。

## 4. 数据接收与自动化：不是把现有表补列

统一流程应重构为：
`Game readonly capture → Native raw snapshot → versioned decode → identity reconcile → semantic validation → staged domain facts → derived/materialized views → quality manifest → atomic cohort publish → role-safe query → approved game action/readback`。

正式能力必须包含：
- 可扩展Source/Decoder Registry及版本绑定；未知结构隔离、不污染完整批次。
- 增量/重复采集幂等且可证，重载/复赛/跨档识别；全量快照与逐场事件分开保留。
- 游戏数据与历史模板、现实NBA资料、外挂规则、AI推断分别标注来源。
- 赛程/StatBank的容量与有效边界；球员PLAYER ID、首发/登场`InUse`、各球队汇总、单场→赛季守恒等质量检查；校验合理例外和未证字段，不强制修改数值“通过”。
- 游戏内真实时间/赛季/阶段及快照发布、统计计算的固定范围。
- 访问控制与Potential等隐藏字段脱敏；AI查询须明确身份、世界线、批次、口径。
- 对发布失败明确NOT_OBSERVED/PARTIAL/BLOCKED，并在GM生产入口按来源要求fail closed。
- 已有交易/教练等合法执行适配新实体身份与批次；不得未经批准扩大写入范围。

**原来的`src/auto_pipeline_ingest.py`、`database/schema.sql`、`gm_data_access`可以重大重构或替换。** 已验证的原生字段Codec、游戏安全只读、批准元组/回执、DEV14故障恢复及生产事实不能丢弃，但API与物理结构不要求原样保留。

## 5. 先建立架构验收合同，再决定正式DDL

此时**可以确定概念/逻辑架构方向**；但尚不能确定每个原生字段的物理列/主键和所有跨季身份规则，也不能宣布完整生产Schema已经定稿。

**建议单独架构任务`WORLD-DATA-ARCH-01`，由Codex主导设计、网页GPT独立审核，Gemini提供只读原生证据**，交付：
1. 领域概念图（World/Season/Game/Player/Team/Contract/Career/Action等）、对象生命周期、稳定身份与多存档分叉模型。
2. 每域的关系字典/ER图/字段规范：`raw_native`、`verified`、`derived`、`unknown`、`sensitive`，含来源、时间、基数、主键、索引、约束。
3. 物理数据库选型与文件切分对比、参考DDL、大小/性能测算、跨库一致性契约，带一套真正可查询的实验性可迁移实例。
4. 原有两事实库、player_pool、DEV14控制数据、旧月度/赛季/history Schema的迁移映射与测试；历史缺证不能填0或猜测值，原数据只读保留，迁移脚本可回滚。
5. 实机AG-NATIVE-01D Box/Season/Career/Slot44等的来源字段验证清单及未证阻断；结构试验可用fixture，但不能将自有fixture回放等同当前完整游戏认证。
6. 统一自动化流水线契约（采集/映射/验证/暂存/发布/查询/角色访问/审计），分阶段切换的兼容方案与验收标准。
7. 受控审批执行器与新模型ID绑定的兼容设计：禁止GM查询潜力、禁止随意修改能力、明确已认证和未认证的写入动作。
8. 页面覆盖矩阵与角色素材就绪度：不是“40族DONE”，而是逐字段/对象的SOURCE_DISCOVERED → RAW_CAPTURED → DECODED → IDENTITY_VERIFIED → PUBLISHED → QUERYABLE → UI_MATCHED；教练/球员人格仍是另立任务。

**强制架构门槛**：先验收概念模型/身份与生命周期、候选DDL和迁移计划；再单独批准代码重构与生产迁移。保留现有可用GM/采集路径直到新的发布与查询实现通过同档回归。不要先大批量建表再反推对象含义，也不必等待所有53个UNKNOWN被破解才设计世界模型。

## 6. 与当前工程的关系

- DEV29 R01–R07：机制和UI能力覆盖研究已结案；694条资料是研究目录，不是694个数据库字段。
- FINAL-CODEX：40族/20缺口的工程证据审计作为**旧工程基准**，不是新Schema边界。
- AG-NATIVE-01D：真实提交的Curry16场与48B累计18项一致，是数据模型的高价值**候选证据**；尚待Codex独立实机验证StatBank偏移、全联盟边界、GameID、身份与持久性，不直接合并旧match-history分支。
- 用户的长期愿景是游戏外构建尽量完整的平行篮球世界，可大幅扩展经营与多角色玩法；不得因现有双库/既有脚本太简陋而压低此目标。

**状态**：`TARGET_ARCHITECTURE_DEFINED / CONCEPTUAL_MODEL_REVIEW_REQUIRED / PHYSICAL_SCHEMA_NOT_APPROVED`。本文件允许自由重构方案设计，但**不批准真正迁移、游戏读写或修改任何游戏数据**。
