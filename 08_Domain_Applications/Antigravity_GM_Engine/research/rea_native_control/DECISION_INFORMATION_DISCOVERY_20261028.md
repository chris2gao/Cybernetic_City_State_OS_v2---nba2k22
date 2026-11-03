# GM / Coach 决策信息：本阶段探索整理

2026-10-28；按Human最新要求停止新增探索，整理已知来源并移交有界辅助。主工程完整M0–M5尚未完成。本报告没有新游戏附加、调用、内存值采集、UI或存档证明，没有改变生产采集/数据库/历史链。

## 1. 先复用哪套已有工程

主执行分支当前统一REA Reader目录有15个数据集，其中统计项仍有占位。**这不代表项目缺少统计采集实现。** 独立世界数据分支已经有更丰富的源码与历史采集证据：

- 原工程基线：`task/nba2k22-world-data-full-implementation-20261024@17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`。
- 当前定点修复候选：`task/nba2k22-world-data-review-fixes-20261026@a3927fb150a213201e404cca043ced4f57409bd1`。本轮fresh `git ls-remote`确认两分支仍对应以上SHA。
- 入口：[候选源码](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/tree/a3927fb150a213201e404cca043ced4f57409bd1/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype)、`BASELINE_HANDOFF.md`、`REVIEW_FIXES_F01_F02_F03.md`、`DIFFICULT_ITEMS.md`。

下面的“已有”指固定候选源码可核对。历史采集、当前真实存档值、正式生产接入、独立验收分别判断；本轮没有重跑历史采集或验收。没有合并该数据分支。

## 2. 信息获取机制与使用边界

| GM / Coach 问题 | 已有获取或查询路径（world_data_prototype） | 关键口径 / 仍缺什么 |
|---|---|---|
| 哪场比赛、日期、对手、状态、主客场 | `schedule_reader.collect_schedule`、`query.schedule`、`calendar_reader` | SEASON的60字节比赛记录与Slot10的32字节索引分开，按实际descriptor计数；来源重读和冲突检查。日期/比分不能靠当前名单反推 |
| 逐场球员/球队Box、节次比分 | `live_reader`、`schedule_reader`、`competition_views.game_box_snapshot` / `query.game_box` | 同一选中capture unit中的双方数据；24字节Native球员Box行；参与者、ID、得分守恒不足时不得伪造完整比分；后来的header检查不能刷新旧Box时间 |
| 当前赛季表现、胜负和基础命中率 | `competition_views.player_seasons`、`season_summary` | 同一原始累计行派生场均和命中率；保留phase/team_scope。按胜率排序不等于官方分区种子/同战绩规则 |
| Native当前统计周期、历史统计槽 | `period_stats_reader`、`query.current_period_stats`、`native_player_seasons` | Player统计bank stride48、Team stride62；25个引用槽完整保留；Native有符号16位索引规则不是仅排除65535。当前选择槽与同unit模式上下文绑定，不能把所有槽自行贴成常规赛/季后赛 |
| 己方与对手球队信息 | `query.team_card`、`team_lineups`、`staff_team_slots`、`native_team_finance` | 对手仍用同一球队数据源，明确opponent_team_id即可；不同家族可能分别采集，必须保留各自时间/来源，不能冒充整张卡同一时刻 |
| 对手战术、个人防守与教练配置 | `planning_reader`、`query.gameplan_card(team_id,opponent_team_id)`；旧`gm_data_access.analysis_inputs.load_native` | 以owner/opponent及球员映射区分计划；配置/倾向不等于实际回合战术、触球或执行频率。已存Gameplan不是对手实时行为追踪 |
| 阵容、轮换和人员特点 | `lineup_reader`、`native_player_rotation`、`native_player_skills`、`native_player_state`、`player_card` | 命名五人组和原始高级轮换矩阵可查；矩阵48×5的轴/ID命名空间、Native时间单位仍有限制；不能据此生成真实On/Off或阵容NetRtg |
| 最近表现、对手拆分、交易前后变化 | 基于真实game_id / unit_id / team-at-game的Box序列查询 | 不能用赛季均值反造逐场，也不能用最新球队归属覆盖历史。需要足够完整的比赛样本和相同模拟/标准化口径 |
| 工资、人员、球探等经营背景 | 既有finance/staff/market/prospect查询；原生合同/球员查询 | Native金额/单位、资格和历史身份按原来源保留；本阶段不继续合同业务执行研究 |

旧集成树的`src/source_extensions.py`也能解码部分赛季累计、计算场均/命中率，但其中旧的7位年份和来源别名不能覆盖候选新Native元数据。本轮只记录差异，不改旧生产管线。

## 3. 高阶数据：现在能说到什么程度

现有`competition_views._rates`实现基础场均、篮板合计、FG/3P/FT命中率，并明确同一累计行、正分母和缺失状态；它没有实现一整套高阶分析。

| 类型 | 来源与结论 |
|---|---|
| eFG%、TS%、3PAr、FTr、Box失误率、双方篮板份额 | 现有K01/K02指南已有版本化公式研究。若同口径真实Box的所需字段齐全，可以派生；需注明定义/系数/分母/样本和DERIVED，不冒充游戏原生页面值。本阶段没有新建计算模块 |
| 百回合攻防效率、净效率、Pace | 先核对双方同场统计与回合/时间口径。Native有`possessions_raw`字段不自动证明单位或公式；Box估计回合必须标ESTIMATED。模拟器常量不是实测Pace |
| USG% | 使用率公式还依赖个人/全队同口径时间与出手等。不能把名为`Franchise_Role_GetUsageScore`的线索直接当USG% |
| PER / True Shooting / OffensiveRating / DefensiveRating | 固定PE存在`STAT_REPORT_PER`、`STAT_REPORT_TRUESHOOTING`、`STAT_OffensiveRating`、`STAT_DefensiveRating`等字面项，但本轮没有闭合它们的计算Getter、参数、单位与当前值；保留线索 |
| On/Off、阵容NetRtg、逐回合、真实投篮坐标/防守距离 | 单纯Box/累计无法证明这些来源。需要相应原生事件/在场片段/追踪信息，当前不能编造 |
| Overall及复杂聚合能力评分 | `DIFFICULT_ITEMS.md`中Overall为Human deferred；本次“高阶数据”探索没有重新启动它，也不提供假值 |

基础统计、原生存储、外部派生指标、游戏行为效果是不同证据轴。

## 4. 本轮新增的投篮分区静态证据

固定EXE SHA256：`1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。下面是本地PE/Capstone事实，**NOT_REA_PROVIDER**，不是新实机读取。

- `SHOTCHARTDATA`注册大小114：`NextFree`在0；`OffensiveStats`在2；`DefensiveStats`在58。两组数组的静态维度各为14×2，元素storage为2字节，恰覆盖56字节。
- `SHOTCHARTDATA_MINI`大小28、`Shots`数组；其维度记录关联候选`SHOTCHARTDATA_SHOT_LOCATION`与`SHOTCHARTDATA_FIELD_TYPE`。邻近字面库存在14个区域名及MADE/ATTEMPTED，但**本轮尚未完成枚举值表、轴顺序和消费者语义的闭环**，不能据相邻顺序给数值贴标签。
- `SHOTCHARTMANAGERDATA`大小2、字段`FirstFree`。它是管理/分配线索，不能当成某球员的投篮数据。
- Player chart data Getter `0xf3f6e0`：bank count/pointer在被解析对象的+0x1a0/+0x1a8，stride114。Player manager Getter `0xf3f7b0`对应+0x190/+0x198、stride2。
- Team chart data Getter `0xf41200`：+0x1e0/+0x1e8、stride114。Team manager Getter `0xf412d0`对应+0x1d0/+0x1d8、stride2。均有原生index边界/断言路径。
- 已保留Player chart Getter的23个直接调用点及若干短消费者完整体，但**尚未闭合实体→索引、时间窗口/累计刷新、区域坐标、历史归属或当前值**。不把这些Getter加入可用角色Reader。
- 两个enum descriptor候选为RVA`0x4d56620`和`0x4d56660`，所见LEA站点分别`0xa1f25`和`0xa1eb5`。当前工具明确归类为无unwind的未确认候选；不可伪装已证明的函数入口。这是辅助包的首个有界核对目标。

这些结构有望补足对手进攻分布和防守允许分布的信息源；是否属于指定赛季/场次、是否覆盖所有比赛，仍需后续证据。

## 5. 可审计来源与停止点

本Run `static/decision_information_*_001..007.json`保留初次检索、修正后的检索、完整选定函数、类型表、调用点和未确认enum候选。初次词法查询曾误命中普通英文per/Space；修正版保留原证据，没有把误命中或零引用当成能力事实。

工具：`tools/discover_decision_information.py`；既有`recover_functions.py`、`extract_type_schema.py`、`recover_callers.py`和`recover_rip_targets.py`。工具名称/匹配结果不是业务意义证明。世界数据源码以固定Git blob为准，正式采集仍是原来的独立工程。

按Human要求，本阶段不再新增探针或功能。下一步仅由Human转发[Gemini协助提示词](auxiliary/gemini_information_20261028/GEMINI_PROMPT_ZH.md)，在独立目录完成小包后停；Codex随后接收、复验和筛选。主工程不自动导入任何辅助结论。
