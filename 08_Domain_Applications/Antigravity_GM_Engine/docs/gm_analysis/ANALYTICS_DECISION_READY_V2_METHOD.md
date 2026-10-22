# Web GPT ANALYTICS V2 — GM 决策准备分析方法与交付契约

- 文档版本：`ANALYTICS_DECISION_READY_V2`
- 建立：2026-10-18
- 所有者：`WEB_GPT_ANALYTICS`
- 类型：分析工作规范／方法学；**不是实际 M02 分析结果，不授权执行游戏**
- 依据：玩家转达的 GM 分析需求（四项优先级）和“简明报告、30队决策准备表、跨批变化表、计算方法/来源引用”交付要求。
- 规则优先级：玩家明确指令 > `config/gameplay_policy.json` / 数据治理规则 > 当前可信发布批次 > 本文。本文仅规定**怎样分析**，不批准 GM 决策。

## 0. 目标和减负：用可决策证据取代排行榜

从“联盟名次罗列”改为“球队需要何种经营判断”；**默认不做**长篇全联盟战绩、工资、能力、选秀权排行榜，也不每次展开 870 组防守原始配置、逐一罗列全部 55 项能力或复制全队球员明细。排序仍可以**作为计算工具和异常筛选**，以及玩家单独请求时作为附表，但不是主要交付物。

保留必要计算：30队战绩、近期*增量*战绩、得失分、薪资/名单结构、选秀权、能力维度、场均分钟/使用状况、教练数据覆盖率和效率指标。这些底层值构成证据，不以精简报告为由省略校验。

优先顺序：
1. 30队一队一诊断；区分“关键能力供应不足”与“现有能力尚未充分利用”。
2. M01→M02及之后相邻**同存档同赛季**批次的可复核变化：能力/潜力、球员流动、薪资合同、选秀权、战绩。
3. 教练默认19项与按需的指定对手OVERALL 18项适配/异常分析。
4. 进攻特征和效率：先守住原始计数语义与样本边界，再计算指标。
5. 休赛期竞价与签约结构只在真实来源认证后正式分析；合成模拟严格隔离。

## 1. 数据入口、时点与来源锁定

从 `published/index.json` → `published/saves/<career_id>/latest.json` → 当前 `batch_path` 读取。要求 `upload_status=UPLOADED`、`purpose=production`、有采集及上传时间，并记录 `career_id`、`source_batch_id`、`data_updated_at`、`game_date`、代码commit、计算版本。不得合成跨时间来源；旧批次只用于**明确标识为历史的跨批对比**。

主要文件：`league.json`（球队战绩/财务）、`season_totals.json`（球队赛季累计统计）、`teams/<abbr>.json`（当前球员名单、球员 `attributes`/`potential`、`source_details`、薪资合同及当前场均分钟）、`draft_assets.json`（简单签权属）、`staff.json`；教练需 `source_coverage.json` 中 `coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`，再读 `coaching/teams.json` + `coaching/field_dictionary.json`，对需要评估的 owner 按需读 `coaching/opponents/<TEAM>.json`。M01 无教练来源，不填入 M02 教练值当成 M01 事实。

截至本规范核验：`mc_haliburton_2021` 最新M02批次为 `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，玩家确认游戏日期 `2021-12-12`，其中教练覆盖状态为 `VERIFIED_OBSERVED_SAME_BATCH`；M01批次 `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2` 不含教练生产文件。**这些仅是制定方法时的检查点，不得作为以后任务的永恒latest指针。**

所有数字为 OBSERVED、CALCULATED、PROVISIONAL、REFERENCE 或 UNKNOWN；`NULL` 与0不同。旧 `team_monthly_stats.poe_*` 是废止语义的原始TEAM字段，不当成教练POE。没有游戏OVR或伤病/完整首发、逐场记录，继续UNKNOWN。薪资差分不是现金自动扣除；商业财务时间窗口不明的字段不强称月收入。

## 2. 30队决策准备表：每队最少一行，深层证据按需链接

对每个队计算下列结构，尽量紧凑：

| 列名（建议JSON key） | 意义／判定依据 |
| --- | --- |
| `team_id`, `abbr`, `career_id`, `source_batch_id` | 稳定的联盟球队身份、时间锚 |
| `stage_candidate`, `stage_confidence` | 比赛表现＋核心年龄/合同/资产的生命周期**候选**；`gm_policy.json`仍PROPOSED，不标GM已裁决 |
| `record_current`, `record_interval` | 本期W/L和与可比上批的胜负/比赛数增量；不是逐场近期状态 |
| `offense_profile`, `defense_profile` | eFG%、3PA占比、TOV占比、篮板、罚球、得失分与有效样本；防守仅用可验证对手计数 |
| `core_and_bench` | 核心能力、替补覆盖、出场分钟分布/实际贡献与被压缩机会（不是精确调控分钟） |
| `coaching_fit` | ActiveSystem、POE、Playbook、四Freelance与轮换值对照本队优势/短板；逐字段证据/UNKNOWN |
| `talent_gap_evidence` | 位置/职责所需关键能力供应不足：例如护框、侧翼防守、持球组织、空间；用真实球员和替补能力分布支持 |
| `utilization_gap_evidence` | 现有能力与战术/实际使用表现不匹配：例如可投射队员多但战术设置不适配；只有推论强度，没有伪称真实战术使用率 |
| `internal_lever_candidates` | 不交易的候选：体系/POE/Freelance/BenchDepth/BenchUtilization/对手整体防守；只描述分析方向，不直接写原生raw指令 |
| `trade_need_assessment` | `NOT_ESTABLISHED / POSSIBLE / STRUCTURAL_GAP_EVIDENCED`，附缺口与内部替代方案；最终交易裁决由GM |
| `uncertainty`, `evidence_refs` | 缺少伤病、OVR、球员身份或对位证据时明确标注；指向实际来源文件及计算字段 |

“缺人才”的最低条件：从可用大名单与55项能力中证明某关键职责缺少足够可用替代，且主要问题不只由单一教练设置解释。 “没有用好”只能是 `UTILIZATION_HYPOTHESIS`：证明球队已有相应技能供给，同时教练设置/轮换/表现之间存在可解释的错配；**不**用场均分钟冒充真实角色或进攻回合占用。两类可以并存。没有足够证据时 `INSUFFICIENT_EVIDENCE`，禁止默认把任何弱队判为需要交易。

输出一张覆盖30队的简明表，每队一句主要结论＋两个候选杠杆＋证据索引；复杂球员指标放JSON而不堆进文本。

## 3. 跨批差分与自然成长：先身份、后数值

### 3.1 可比性门槛

仅相同`career_id`、相同联赛赛季、按`data_updated_at`先后有序的两个**已发布正式批次**可构成常规区间。核对各队赛季场次W+L不回退、球队累计统计计数不回退；如果赛季重置/读旧存档/重建名单或采集解释不一致，暂停差分并标 `NON_COMPARABLE`。赛季累计 `M02 - M01` 可以估算*这两个快照之间*的球队表现（分母为新增场次，联盟比赛数为30队新增场次之和/2），不等于逐场日志或固定月历窗口。104场等数字需要同口径重算，不只复制旧报告。

### 3.2 玩家身份：不得只用姓名、Face ID 或pool_slot作为永久ID

`src/gm_core/calculations.py::roster_changes` 的旧比较注明`name+face_id` **不是永久真实人物身份**；`pool_slot` 只对本次模型目录有效，进程指针/`stats_index`也是局部标识。不能以这个函数单独认证55项成长、交易归属或合同连续性。

三层处理：
- `VERIFIED_STABLE`：存在跨快照真正持久且来源认证的球员唯一键，或可信的明确人物关联/交易回执并通过身份、同一存档和一对一唯一性核验。才能发布`verified`的逐球员真实差分；任何复用/冲突必须拒绝。
- `HIGH_CONFIDENCE_TEMPORAL_CANDIDATE`：当前仅能用姓名、DOB、Face ID、原始选秀身份（若有）、球队间连续性、唯一性等多维信息交叉筛选，必须无一对多歧义，且没有与已知变更事件冲突；它是**区间候选映射，绝不是永久玩家ID**。可发布明确标为provisional的候选差分供核对，不计入“已确认成长人数/总变化”。
- `AMBIGUOUS / UNMATCHED / NEW / EXITED`：同名、模型复制、槽位移动、交易/导入无法核实，差分保持UNKNOWN，输出证据/需要的身份字段；不以缺失推断能力下降。

把 `match_method`、`match_evidence`、`confidence`、`prior_reference`、`current_reference`、`conflict_reason` 置于每条记录；独立标 `new`/`exited` 和 `potential_transfer`。若源中确实缺真正稳定人物键，记录 `DATA_SOURCE_REQUEST: PERSISTENT_PLAYER_IDENTITY` 给开发/采集方，**不阻断球队级增量指标分析**。

### 3.3 数值差分

只有身份层通过对应闸门且相同55项 schema/version、属性源已验证时，对每个`attributes[<field>]` 的`value`计算 `current - previous`；保留全部55字段的before/after/delta；`potential`独立计算，不当成OVR。优先保存全量机器可查JSON；Markdown只列已核验有变化的主要球员、变化字段及例外。要检查字段集合一致、数值范围有效、0值不能当UNKNOWN，重复潜力字段不重复计数。游戏自然变化仅作`OBSERVED_DELTA`，不归因于Tempo/POE等教练项，不直接修改球员任何能力。

球队级名单：只有相同队身份可准确计算名单条目和人数的**集合候选变动**；人物级转入/转出需通过上述身份门槛。合同逐球员6年薪资槽、年限、选项、当前/合同球队归属只在身份可靠时对比；赛季变更需先处理合同年进位，不误判为签约。选秀权用 `draft_assets.json` 的同届 `draft_year + draft_round + original_owner_team_id` 与 `asset_id`、重复与唯一性校验后对比`current_owner_team_id`；`asset_slot`不是永久键；只交易后3届的规则不影响历史归属差分。

## 4. 教练适配及870组整体防守：读取，分层，压缩

默认先分析30个 `COACH_DEFAULT` 19字段（六POE、PreferredSystem/ActiveSystem、PlaybookID、BenchDepth、RunPlayTendency、ZoneUsage、BenchUtilization、Tempo、HelpDefense、四有序Freelance）。只引用同批字典中`production_enabled`/`gm_control_enabled`及当前合法enum，区分“观测值”和“可被GM改”。五项Sim只读禁写；Tempo语义UNKNOWN，不解释为节奏百分比；具体个人分钟由AI重置，不编排/开发个人分钟写入；训练完全排除。

适配评估采取**证据矩阵**而非虚构加成：
- `ROSTER_STRENGTH`：关键球员篮下/投射/传球/防守/篮板能力与可用深度、真实出场。
- `SYSTEM_INTENT`：ActiveSystem/PreferredSystem和Playbook/Freelance原生命名所表达的可能空间/打法意图；没有可靠战术播放逐回合数据时限制解释。
- `COACH_PREFERENCES`：六POE与替补深度/利用、协防/联防/战术频率。
- `FIT_FINDING`：`ALIGNED / REVIEW / EVIDENCE_INSUFFICIENT`，字段与球员证据、篮球机制理由及替代解释。分数如需引入，先版本化公开权重/阈值并标HEURISTIC，不假装2K胜率引擎公式。
- `GROWTH_CONTEXT`：跨批确认的球员成长与当期体系只做共同时间背景；无对照不做因果陈述。

对手18项`VS_OPPONENT_DEFENSE`（整体OVERALL）按需解析29个对手文件。870组不默认原文输出；采用**异常+优先对手**摘要：首先筛身份/覆盖异常、mixed_fields/缺组和显著离群；然后结合对手外线出手和有效命中、失误/禁区等已核实统计，以及主客队能力短板，产生`MATCHUP_REVIEW_CANDIDATE`。仅选高价值组展开原生值，附对应owner文件路径、opponent_team_id、字段与同批字典引用。不要从 `is_in_use_raw=0` 断言防守不存在/禁用；它不是业务开关认证，不能强行开启。null/mixed字段不补成0；整组设置不是逐人防守写入。

## 5. 进攻/防守特征与效率：公式、证据门槛

`season_totals.json` 提供球队累计 `points, pa, attempted, made, 3pt_attempted, 3pt_made, turnover, offensive_rebounds, defensive_rebounds, free_throws_attempted, free_throws_made, poss` 等。先核对每队累计、范围、命中≤出手、三分出手≤总出手、W/L与`league.json`一致，且批次间单调；任何字段未知则该指标UNKNOWN。若使用 `ofga/ofgm/o3pa/o3pm`作为对手投篮，须先确认字段来源语义，不从前缀猜测。

默认可以确定性计算（FGA=`attempted`，FGM=`made`，3PA=`3pt_attempted`，3PM=`3pt_made`，FTA=`free_throws_attempted`，TOV=`turnover`）：
- `eFG% = (FGM + 0.5 * 3PM) / FGA`；`FGA>0`且字段含义验证。
- `3PA_rate = 3PA / FGA`，`FT_attempt_rate = FTA / FGA`。
- `TOV_estimated_rate = TOV / (FGA + 0.44*FTA + TOV)`；明确标“估算口径”且绝不与真正以poss为分母的TOV%混称。
- `AST/TOV` 在`TOV>0`时；`ORB_per_game = ORB/(W+L)`和篮板原始合计；无真实对手DRB/对位口径时不发表标准ORB%。
- `points_per_game = points/(W+L)`，`points_allowed_per_game = pa/(W+L)`，`point_diff_per_game = (points-pa)/(W+L)`。不得称作百回合效率。

**`poss` 语义验收关口**：`src/gm_core/calculations.py::efficiency(points,poss)` 目前只是数值计算函数，不能证明 `poss` 是标准球队每次进攻回合、也不能证明攻守回合单位与`pa`对应。应执行30队分布/跨批同口径/内部估算 `FGA + 0.44*FTA - ORB + TOV` 的差异诊断，核对 `poss>0`、合理每场值及进攻/防守回合关系；查`src/source_extensions.py`及原始field profile，必要时`DATA_SOURCE_REQUEST: POSSESSIONS_SEMANTICS`。一致性检查只是必要而非充分条件；缺原生定义或独立对照时 **不**以`100*points/poss`标“标准ORtg/DRtg/NetRtg”，可作为`PROVISIONAL_POINTS_PER_100_RAW_POSS`单独输出并说明限制，或者暂不展示。只有攻守双端口径分别确认，才推出标准百回合进攻/防守/净效率。不用对手得分`pa`直接除进攻`poss`冒充防守效率。

跨批区间率：对可比且单调的*累计分子分母分别相减后*重新计算，不能相减两个累计比率；发生负增量、分母0或来源口径变化时标UNKNOWN。

## 6. 输出目录和文件格式（每个run独立）

本规范位于 `docs/gm_analysis/ANALYTICS_DECISION_READY_V2_METHOD.md`；实际任务在 `docs/gm_analysis/<career_id>/` 下以唯一`<run_id>`新建（不覆盖旧`SIMPLE_PICKS_V1`报告）：

1. `<run_id>_ANALYSIS_ONLY.md` — **简明报告**：最近区间概述；联盟结构性问题3–8条；GM优先研究的球队和不足；主要数据缺口；只附少量关键数值，不生成长排行榜。
2. `<run_id>_TEAM_DECISION_TABLE.md` — **30队决策准备表**（每队一行/短诊断），并在同名JSON `team_decisions` 提供结构化证据字段。
3. `<run_id>_CHANGE_TRACKING.md` — **跨批变化表**（30队增量、确证球员成长/潜力、候选身份匹配分隔表、名单/合同/签权变化），同名JSON `cross_batch_changes` 中保留所有校验、未匹配记录与逐字段delta。
4. `<run_id>_METHOD_AND_SOURCES.md` — **本run计算方法与来源引用**：输入两批（若有）、每文件精确路径、原始字段、代码commit、公式、身份匹配证据、`poss`状态、缺失/假设、执行模式、不可比项。
5. `<run_id>_ANALYSIS_ONLY.json` — 主结构化产物：`schema_version`、`analysis_version=ANALYTICS_DECISION_READY_V2`、`career_id`、`source_batch_id`、`previous_source_batch_id`、`data_updated_at`、`game_date`、`policy_id`、`calculation_version`、`code_commit`、`execution_mode`、`status=ANALYSIS_ONLY`、`execution_authorized=false`、`team_decisions`、`cross_batch_changes`、`league_findings`、`metric_validity`、`source_refs`、`unknown_fields`。四份MD与JSON的表格数字必须一致。

只在玩家明确触发正式分析并授权写回时生成以上实际产物；基线文档升级不是分析执行。每批玩家明确要求更新时按其目标实际重算；若缺上批或没有可信身份键，也交付其他可做部分并清晰标`PARTIAL`与阻塞项，不造数。

## 7. 实现路线、工程分工与验收

**分析端直接实现（可在任务窗口Python/SQL做，不待Codex）**：
- 读取同批30队、出场数据、教练19项及指定对手文件；球队级W/L/场均增量和上述经验证的投篮/失误率。
- 跨批球队级战绩、工资、资产差分（身份不足者保留未匹配）。
- 按上述证据矩阵生成30队短诊断、教练匹配假设、18项防守重点及四+一交付物；固定模型版本、来源、缺口。
- 能安全执行原脚本则记`EXACT_REPO_SCRIPT_EXECUTED`；只运行兼容代码则`SOURCE_COMPATIBLE_PYTHON_EXECUTED`；仅做规范则`NOT_EXECUTED`；不能用自然语言计算冒充Python/SQL。

**需要额外来源或工程审查**（不作为先行四部分全部停工理由）：
- `DATA_SOURCE_REQUEST: PERSISTENT_PLAYER_IDENTITY`：若没有认证且跨批保持唯一的球员身份关联，联系Codex数据采集/开发基线设计持久映射，提供重复ID/换队/导入测试证据；不得通过hash姓名+face声称解决。
- `DATA_SOURCE_REQUEST: POSSESSIONS_SEMANTICS`：请采集/开发端核对`poss`与`pa`、攻守回合原生语义及统计截面；分析端先做数值一致性诊断。
- `DEVELOPMENT_REQUEST`仅在当前只读Python不能可靠提取、需要调整仓库计算器或新增认证字段时提出；不要默默修改数据源/执行器。

验收清单：30队恰好30行且唯一team_id；两批锚点完整；增量非负/重置明确；55项成长只在已确认身份上标verified；选秀权年/轮/原队不变且每资产唯一；19/18字段遵循字典与source coverage；`is_in_use_raw=0`不判禁用；`poss`未认证不标NBA标准ORtg/DRtg；传统排行榜不占主文；每个断言可回溯数据及公式；报告和JSON `ANALYSIS_ONLY`且玩家未授权游戏写入；写回GitHub后回读、新session、更新本岗位CURRENT；不自动唤醒GM。

## 8. 设计理由（给后续窗口复述）

- GM的实际选择发生在“保留现有阵容并改善使用方式”与“用交易补结构缺口”之间；名次只能描述结果，不能解释产生结果的可调整因素。
- 只有跨批同人物、同字段、同赛季的可信变化才支持成长研究；误把重排slot或同名模型当本人，会直接污染GM长期历史线。
- 教练19+对手18提供可操作而非直接能力编辑的杠杆；适配异常比把870组原始代码全部印出更省上下文、便于GM审批。
- eFG、投篮构成与失误控制是可解释的过程指标；百回合效率虽更直观，但`poss`含义未经认证就命名标准值会产生虚假精度。
- 四份精简Markdown按GM阅读任务分工，结构化JSON完整保留证据与差分；无需让GM重新做相同的数值分析。

### 方法源文件

- `web_gm/baselines/ANALYTICS_BASELINE.md`
- `web_gm/manuals/GM_COACHING_OPERATIONS.md`
- `src/gm_core/calculations.py`（现有`efficiency`与`roster_changes`的精度/身份边界）
- `src/gm_core/data_reader.py`（同批教练校验）
- `config/source_catalog.json`、`docs/34_BASELINE_CURRENT_STATE.md`
- 当前存档两批 `published/saves/mc_haliburton_2021/batches/<M01|M02>/`（具体完整`batch_id`见第1节）
