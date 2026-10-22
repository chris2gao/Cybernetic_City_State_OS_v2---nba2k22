# K01/K02 — NBA2K20–23 终极联盟逐场比赛、Box Score、Game Logs、投篮和高级统计实用指南

> DEV29 V2 / R01-A，2026-10-20，研究主目标 **NBA2K22 PC 本世代离线 MyLEAGUE**。研究文献涉及 NBA2K20–23、PS4/PC本世代和PS5次世代；跨版本经验可指导查找和经营，不等于已获得 PC22 内存认证。
>
> **当前研究状态：`INCOMPLETE_WITH_OPEN_ITEMS`**（第一批可用攻略已交付）；**目标游戏原生状态：`UNKNOWN / PC22_NATIVE_PENDING`**，本轮没有进入游戏、读写进程或运行采集。页面位置若没有直接证据均写为“检索路径/待核”，绝不伪造已确认的精确PC操作按键。
>
> 本文中的 `SRC-####` 引用见 [SOURCES](../SOURCES.md)；`VIS-####` 见 [外部图源](../visuals/EXTERNAL_VISUALS.md)。真实截图、菜单身份、保留期最终均须按指定平台取证。

## 0. 证据分级和开箱先读

| 标签 | 准确定义 | R01判定 |
|---|---|---|
| `KNOWN_IN_SERIES` | 同系列已有实物/一手社区资料，可能不同游戏版本、平台、模式 | Schedule/Daily View、历史Box查询、球员投篮图 |
| `PC22_UI_CONFIRMED` | 本项目实际NBA2K22 PC本世代 MyLEAGUE 对应页面已截图及确认 | **本轮未达到** |
| `PC22_NATIVE_READ_VERIFIED` | 对同一目标存档、对象身份、读数验证 | **本轮未达到** |
| `PROJECT_CAPTURED` | 原生数据进入带来源和批次的正式数据库 | 逐场Game/Box/Shot **未由本轮审计证明** |
| `GM_QUERYABLE` | GM可稳定按GameID/球队/球员/日期读取并追溯 | 逐场事实 **未由本轮证明** |
| `UNKNOWN` | UI、字段、定义、历史留存等尚缺证据 | 明确留为未知 |

**最重要的区别**：真实 NBA.com 提供 Play-by-play、Tracking、Shot Dashboard、Advanced Box，**不代表2K22 PC自带这些全部数据**。2K22 PC英文官方手册列的是按钮与临场战术控制，没有逐场统计页面索引、合法字段清单或历史数据保存承诺；因此不能用该手册“证明没有该功能”[SRC-0004]。

## 1. K01.GAME_SCHEDULE / K01.GAME_LOGS — 从赛程找到“这一场发生了什么”

```yaml
mechanism_id: K01.GAME_SCHEDULE
priority: P0
version_scope: NBA2K22_PC_CURRENT_GEN_MYLEAGUE_TARGET
knowledge: KNOWN_IN_SERIES
pc22_ui: UNKNOWN
pc22_native: NOT_OBSERVED
project_capture: DEV28_GAP_OPEN
gm_consumers: [WEB_GM, WEB_ANALYTICS]
sources: [SRC-0005, SRC-0006, SRC-0007, SRC-0008]
```

### 1.1 WHAT：赛程、Game Log、Box Score 是三个层次

- **Schedule/Calendar / Daily View**：一场赛事是否存在，日期、主客场、对手、当前赛季阶段、比赛状态及最终比分。它是 **game identity** 的来源，而不是比赛表现的完整记录。
- **Game Logs**：同一球员/球队按场次展开的时间序列，回答“最近5/10场表现如何”“对哪支球队打得好”“交易/换帅前后怎么变”。**玩家常说的 Game Log 既可能是球员分页，也可能只是从日历逐场打开 Box 的替代操作**；本轮没有在 PC22 证明独立 Game Logs 标签存在。
- **单场 Box Score**：与某个 game 绑定，所有上场和未上场球员的实际计分统计、对应球队合计；不能用“本赛季场均 × 已打场数”反推出每场明细。防止把赛季统计当逐场历史。
- **Play-by-play/逐回合、事件级射点和阵容在场片段**：与上述三者再分开；即使能打开Box，也不代表有这些追踪数据。

### 1.2 HOW：可靠历史导航线索（不能照抄成PC22已证键位）

**路径A：日历/球队赛程 → 选择过去某场 → 进入比赛相关操作 → 查当场Box**。Operation Sports 关于早期MyLEAGUE的玩家经验称，Calendar上的比赛可进入“Daily View”以切换当日其它比赛；2015年原帖中另一位玩家明确表示 MyGM/ MyLEAGUE 权限可能不同 [SRC-0005]。作为2022年NBA2K22重建记录帖中的玩家回帖，另有人针对“查看旧季后赛Box”解释了 **2K20的特定操作**：上一次比赛Box后按 Xbox Y / PS Triangle 依Game1、Game2顺序切换；发言者**特别注明只在2K20验证** [SRC-0006]。这项信息只用于 PC22 定向检查，不是2K22现成操作说明。

**路径B：球员卡/Stats → 按游戏内提供的统计维度切换 → 检查有无逐场Game Log及比赛日期/对手**。这是给未来实机核验的导航尝试，**不是已认证菜单路径**。检查入口选择球员个人页、球队统计页、League Stats及赛程详情，准确记录页签名、按键、筛选器和结果集合。

**路径C：次世代MyNBA → Daily View**。2K21次世代高级制作人Dave Zdyrko的正式开发者介绍确认 Daily View 可查看当日NBA/G League安排，进入比赛或普通模拟、SimCast、SimCast Live [SRC-0007]。此信息是次世代MyNBA，不应把G League、所有操作和UI复制到PC22 MyLEAGUE。

### 1.3 WHERE：PC22实机需要按顺序查的页面及可见选项

| 候选页面 | 实机读数检查（列名与可选项未确认前不写死） | 玩家使用方法/意义 | 证据 |
|---|---|---|---|
| 联赛日历/球队赛程 | 当前/往日、球队、轮次、比赛是否完成、主客、比分、对手、入口按键 | 从“赢/输”钻到单场对手问题 | 系列一手玩家/次世代官方；PC22待核 |
| 当日 Daily View | 可否转到其它队赛事；普通Sim、SimCast与现场观看分支 | 同日30队跟踪、侦察潜在对手 | SRC-0005/0007，模式不同 |
| 完赛 Box Score | 球员列表、主客球队、得分、分钟、合计、节次表、DNP、赛后退出后能否回看 | 追查某场核心球员效率和轮换 | SRC-0006（2K20）、PC22待核 |
| 个人/球队赛季统计 | 是否存在 Game Logs、切换球队/时期/赛季及比赛类型；统计页签和排序 | 不同于 Season Totals 的逐场动态 | 待PC22截图 |

**不能跳过赛程键**：`game_id` 首选真实原生稳定ID，如缺则记录 `save_instance + season + league + phase + date + home_team + away_team + occurrence` 复合候选身份并检测冲突；“日期+球队”不足以区分极端重赛、季后赛、同日异常或跨存档。不允许当前球队归属覆盖旧比赛事实。

### 1.4 常见陷阱：模拟标准化与比分对不上

2022-06-09 的**2K22本世代 MyLEAGUE**玩家报告：在SimCast模拟后跳入比赛，场内结束显示102:110，日历却显示142:150；回复建议检查“normalize simulated minutes/stats”（回帖具体英文选项名不确定），原发言者随后表示关闭分钟标准化后恢复 [SRC-0008]。这是可复核的单例玩家证据，**不是对所有版本和玩法都必然成立的引擎公式**。

实务：在读Box之前先抄 `played_quarter_length`, `simulated_quarter_length`, `normalization_enabled`（分别如实填 `UNKNOWN`）、`sim_mode`（Play/Quick Sim/SimCast/SimCast Live/Jump-in）以及 “Box/日历/赛后” 三处比分；遇矛盾打 `SCORE_CONFLICT` 而不是直接取最新的覆盖旧值。教练对比、交易评价也必须按相同模拟设置分组。

## 2. K02.GAME_BOX_PLAYER / K02.GAME_BOX_TEAM — 单场球员与球队Box

```yaml
mechanism_id: K02.GAME_BOX_PLAYER
priority: P0
research_status: DOCUMENTED_WITH_OPEN_ITEMS
version_scope: NBA2K20_22_SERIES; PC22_UNVERIFIED
sources: [SRC-0006, SRC-0008, SRC-0009]
pc22_native_status: NOT_OBSERVED
dev28_followup: D28-3
```

### 2.1 什么是“最小可分析”的原始Box

逐场球员候选：真实Player ID、当场Team ID、`game_id`, `starter`, `played/DNP`, `minutes`, `PTS`, `FGM/FGA`, `3PM/3PA`, `FTM/FTA`, `OREB/DREB/REB`, `AST`, `STL`, `BLK`, `TOV`, `PF`, `+/-`（如原生有），技术犯规/盖帽被盖/DNP原因仅在来源证实时加入。这里是**采集候选字典**，不是“已在PC22看到每一列”。

球队逐场候选：主/客队ID、每节得分、总PTS、FG/3P/FT出手命中、进攻/防守/总篮板、助攻、抢断、盖帽、失误、犯规、快攻分/禁区分/二次进攻分/替补得分（原生存在则采）、得失分和胜负；对手同级原始Box必须成对保存，不能拿最新赛季场均替代。

**球员出场分钟和赛季合计不可随便反算：**
- 球员`MIN`的分钟/秒单位、精度、标准化状态要保留；DNP可记录`0`上场分钟+明确DNP标志，但不能推断缺行=0分钟；
- 赛季小数分钟和BOX分钟四舍五入可能不精确相加；允许容差并留原始字符串；
- 每一侧的球员分数求和应与队伍总分在相同原生口径内核对；若不一致，记录标准化/加时/模拟及其它异常证据，不替游戏修正。

### 2.2 GM如何真正用单场Box：三组分析

**进攻识别**：先看队伍出手结构 (`3PA/FGA`)、罚球频率 (`FTA/FGA`) 与失误，再看核心球员使用了多少出手与罚球；如果外围投得少，不应只根据最终胜负立刻调整主教练进攻体系。观察同类对手连续若干场，检验是否是战术、球员定位、对手防守还是随机样本。

**防守识别**：以对手 eFG%、对手FTA/FGA、失误和进攻篮板比判断问题出在对手投得准、犯规控制、球权施压或篮板终结；**一个球员单场 +/- 不能单独证明防守好坏**，它包含共同出场球员、对手强度和轮换影响。

**阵容/合同识别**：近5/10/20场的真实分钟、出手和效率变化，先辨认角色变化或教练造成的使用方式差异，再谈交易。用户规定不通过改能力值“修好”低命中率；GM可提出真实人员调整或已有受控教练配置，不得擅改球员能力/潜力/徽章。

### 2.3 核查结果质量

同一比赛要尽量有：`score_calendar`, `score_box`, `score_end_screen`；`sum_player_pts`, `team_box_pts`, `game_final_pts`；主客两队字段完整性；`played/simmed/normalized`；常规赛/季后赛；来源时间和屏幕/源标识。出现全部球员得分大幅膨胀或奇怪重复统计不应进入无标记的趋势分析。

2022年一位2K22线上MyNBA玩家报告部分AI队员赛季得分异常高，且Box与异常赛季累计一致；其使用SimCast Live和36分钟标准化 [SRC-0009]。这是另一种**社区故障报告**，不证明相同故障在PC22离线必现。与单场日历不符案例共同提醒：从结果页面读取的数字也可能已有污染，不意味着采集脚本出错。

## 3. K02.PER_GAME_PER36_ADVANCED — 三种统计不要混淆

```yaml
mechanism_id: K02.ADVANCED_STATS
priority: P0
sources: [SRC-0010, SRC-0011, SRC-0012]
status: SERIES_MENU_UNKNOWN_PC22; STANDARD_FORMULAS_DOCUMENTED
pc22_native_status: NOT_OBSERVED
```

| 分类 | 计算粒度 | 实际解释 | 可否从真实逐场Box可靠得到 |
|---|---|---|---|
| Season Totals / 累计 | 每项统计赛季求和 | 出勤和负荷量 | 是，需逐场完整性 |
| Per Game / 场均 | 累计÷符合口径的GP | 比赛产出，受分钟影响 | 是，需知道GP与DNP规则 |
| Per 36 Minutes | 统计累计÷总实际分钟×36 | 消除部分出场时间差，不等于球员真实打36分钟会等比生产 | 是，MIN>0；不是平均单场`per36`的简单平均 |
| eFG% | `(FGM+0.5×3PM)/FGA` | 三分额外价值，衡量有效投篮效率 | 是，FGA>0 |
| TS% | `PTS/[2×(FGA+0.44×FTA)]` | 结合三分、罚球的真实命中效率**估计** | 是，分母>0，0.44为约定 |
| 3PAr | `3PA/FGA` | 球员/球队的三分投篮选择 | 是 |
| FTr (常见版本) | `FTA/FGA` | 罚球制造频率；“罚球因素”也有FTM/FGA口径 | 是，须显式记录具体定义 |
| TOV% (常见Box模型) | `100×TOV/(FGA+0.44×FTA+TOV)` | 每次结束进攻行动的失误比 | 是，分母>0 |
| Team ORB% | `ORB/(ORB+Opp DRB)` | 争抢可用进攻篮板的份额 | 是，需要对手篮板 |
| Estimated Possessions | `FGA+0.44×FTA−ORB+TOV` | **粗估**回合数；不等于真正逐回合记录 | 可估，不能宣称 exact |
| Estimated Team OffRtg/DefRtg | `100×本队得分/估计回合`、`100×失分/估计对手回合` | 按百回合调整攻防，分母不精确 | 可估；使用固定版本，显示 estimated |
| USG% | 需要个人与全队FGA、FTA、TOV以及个人/球队实际分钟的标准公式 | 球员在场时球队由其投篮/罚球/失误终结的使用比，不是持球时间或触球次数 | 可近似，必须同场分钟与球队相同口径 |
| PER / BPM / VORP / RAPM | 依各自具体模型，需要联盟基准、场上片段或更多资料 | **不是**用基础Box随意拼成的“自定义PER” | 本项目当前不应宣称可计算原版 |
| Real on-court On/Off、lineup NetRtg | 需要球员在场时间段、双方得分/回合、阵容替换 | 识别双人搭配、替补协同和防守影响 | **纯总Box无法精确生成** |

数学定义与估算边界按Basketball-Reference Glossary及Four Factors [SRC-0010/0011]；实际NBA.com官方Advanced页面证明现实联盟有更多筛选和指标（如NetRtg、Pace、PIE、USG%），**不能冒充2K22 PC原生Advanced列表** [SRC-0012]。任何“2K自身Advanced”页签内容、PER算法、是否提供Per36/每百回合等均须从PC22屏幕独立验证。

**正确聚合方式示例**：球员近10场真实`TS%` = `SUM(PTS)/[2×(SUM(FGA)+0.44×SUM(FTA))]`，不是对10个单场TS%做等权平均。按对手/赛程/先发替补拆分也先筛选真实Box，再聚合。

篮球四要素（Four Factors）指导球队质量诊断：eFG%、TOV%、ORB%、罚球率，各自分攻防两个方向，比较己方与对手值[ SRC-0011 ]。权重是篮球经验模型，不得强行写成2K模拟胜率概率公式。

## 4. K02.SHOT_CHART / SHOT_ZONES — 投篮落点、热区和命中率不是一回事

```yaml
mechanism_id: K02.SHOT_CHART
priority: P1
sources: [SRC-0013, SRC-0014]
visuals: [VIS-0001]
known_in_series: YES
pc22_myleague_menu: UNKNOWN
raw_attempt_coordinates: NOT_OBSERVED
```

- **Shot Chart** 可能显示一个时期某场/一段样本的投篮出手分布和结果；若能按区域统计出手数/命中数，就可计算区域命中率及出手频率。
- **Hot Zones / 热区图** 是游戏状态/显示机制，不等于已采集到每次出手的原始坐标，也不意味着同一数值必适用所有模式。NBA2K22 Reddit玩家讨论确实把这两种图分开，有人介绍在Roster/Stats能切换Shot Chart及Hot Zones [SRC-0013]。其讨论围绕 MyCareer、Park、Rec；**这不是NBA2K22 PC离线MyLEAGUE的具体菜单确认**。
- 2K22 **次世代**玩家贴出两种图的截图并询问为何显示不同，回复对热区跨模式适用性有不同说法 [SRC-0014/VIS-0001]。因此跨模式互相继承、热区阈值、刷新范围不能靠单条评论认证，尤其不能将次世代UI直接照搬PC22。
- **Shot Zones Aggregates** (如禁区/近投/中距离/角落三分/弧顶三分) 与 **Shot Coordinates** (每次真实落点x,y、命中/失手) 要拆分：只有分区汇总不能生成像素级热力图；没有投篮尝试细目，不能宣称有事件序列/投篮质量/防守者距离。
- 经营上看的是“出手地图×人员能力与角色×教练战术×防守对策”；仅有命中率且样本量极小，不能据此认定某个球员完全不适合某一区域或要求直接修改他的属性。

### PC22当前需要抓的证据

打开真实 PC22 MyLEAGUE 球员卡、球队统计页、完赛 Box/赛程、实时比赛暂停统计，核对能否在 **单场/全季** 切换Shot Chart、区域表、热区；每个页面记真实显示的区域名、单位、图例、样本时间窗、选项提示和可否回顾旧比赛。如果没有，`UNKNOWN`，不要通过 2K22 MyCareer 或NBA.com图替换。

## 5. 统计与游戏设置的联动：避免GM做出伪因果

| 原因或背景 | 影响哪些数据解释 | 能做什么、不该做什么 |
|---|---|---|
| 实战每节时长 vs Simulated Quarter Length | 出手/得分/上场时间、场均及Per36 | 必须记录，不混合不同规范化批次 [SRC-0008] |
| 标准化 Sim Minutes/Stats | Box与日历/赛季统计可能出现不同口径 | 先定位源与屏幕，不静默缩放到“统一值” [SRC-0008/0009] |
| 使用不同比赛方式（Play/SimCast/Quick Sim） | 比赛统计生成路径可能不一样 | 先标模式，比较前确保分层 |
| 教练 Pace/Run Plays/体系、Rotation | 球队回合数、球权分配、出手区域可能发生变化 | 统计提示需要调查；无引擎因果证据不得说修改X必提高Y |
| 对手风格与防守、体能伤病 | 攻防效率和出场分工 | 结合阶段、主客、强弱队样本解读 |
| 赛季阶段（Regular/Playoffs）、加时 | 分母、出场时间、比赛胜负 | 分阶段与加时标记，不能默认48分钟 |
| 赛季迁移、球员转会 | 历史球员归属及球员持续追踪 | 旧Box永久记录当场team_id，不追溯改写为最新所属队 |

2K22 PS4本世代Operation Sports高参与度模拟调参帖列出了 `Quarter Length`, `Simulated Quarter Length`, Team Pace、Possessions per Game、Shot Types、Shot Percentages、Stat Distribution 等，并明确是在研究“模拟统计是否像真实NBA”；用户给的数值是其自用滑块，不是原生默认或GM必须采用的“最优值” [SRC-0015]。本项目严格禁止自动改球员能力来校准统计，研究不是调参授权。

## 6. 推荐给GM的五步逐场诊断法（可以直接执行的分析逻辑）

**第一步：选正确比较对象**。选最近10场，按对手水平、主客、比赛阶段和模拟配置过滤，标记已知异常；保持同档口径。10场只代表趋势初探，不自动得到统计显著性。

**第二步：先算团队四要素与百回合估算**。先识别得分起伏主要来自回合数（Pace）、投篮质量/效率（eFG/TS proxy）、罚球制造、篮板还是失误，再找球员。

**第三步：看核心与替补**。每场记录分钟、FGA/3PA/FTA、效率、TOV及谁得分；观察高使用率低效率是否有连续性。对角色改变，用换帅/调整前后比赛分段与对手进行相似性对照。

**第四步：只有证据足够才提行动**。问题若是整体出手结构或协防，可提出已有认可范围内的教练/轮换/战术提案；若是某个位置持续缺人，再讨论交易和虚拟市场资金；不能根据一场起伏就调整所有战术，更不能用修改球员能力制造目标效果。

**第五步：下一批验证**。提案仅在玩家批准后交受控执行；后续正常全量采集比较相同指标，并记录对手、伤病、比赛方式变化。表现改善可视为关联，不能直接归因单一教练参数。

## 7. DEV24既有来源缺口与DEV28-3交付要求（本轮不实施）

项目`config/source_catalog.json`与DEV28总规划表明已经有赛季累计/部分静态来源，但没有可以据此声称**可靠全联赛逐场历史**的认证证据。DEV24是未来D28-3动态数据缺口的基础；本轮不重复设计执行器，也**不将尚未审计过的源码当已证实缺失全部字段**。以下为研究确定的**采集需求优先级**：

| 等级 | 实体 / 最小字段与关系 | 质量与身份要求 | 当前状态 |
|---|---|---|---|
| P0 | `game`: game_id/日期/season/phase/home/away/最终比分/状态 | 同存档稳定ID、来源与游戏时间，可能双重比分及冲突标记 | `DEV28_GAP_OPEN` |
| P0 | `player_game_box`: player_id/game_id/team_id/分钟及基础Box、DNP/Starter若存在 | game×player唯一区分、真实当场team、与球队Box核对 | `DEV28_GAP_OPEN` |
| P0 | `team_game_box`: game_id/team_id/基础Box及对手侧 | 两球队成对、统计一致性、来源字段可见性 | `DEV28_GAP_OPEN` |
| P0 | `coverage_quality`: 赛季/赛事总数、已见场次、玩家与AI比赛覆盖、缺行/异常 | 非完整覆盖不得自称“全赛季所有比赛”；异常保留原值 | `DEV28_GAP_OPEN` |
| P1 | `shot_zone_game/season`: 区域+FGA/FGM/适用窗口 | 必须真实原生有区域聚合，不由整场FG假分配 | `UNKNOWN` |
| P1 | `advanced_game/season`: 游戏直接显示字段或公式版本的派生指标 | `observed/derived/estimated`分开，不混用不同指标定义 | `UNKNOWN` |
| P2 | 每次投篮坐标/防守者距离、真正逐回合、lineup-stint与真实On/Off | 只有真实来源才采，不由Box合成 | `UNKNOWN` |

最小身份/来源结构：`save_id,save_instance_id,generation_id,career_id,batch_id,season,phase,game_id,game_date,source_page_or_object,raw_or_derived,formula_version,capture_at,quality_flags`。需分别标 `KNOWN_IN_SERIES`、`PC22_UI_CONFIRMED`、`PC22_NATIVE_READ_VERIFIED`、`PROJECT_CAPTURED`、`GM_QUERYABLE`，不以“有截图/有地址”直接升级到最终等级。

建议严格以真实原生Box为事实，用显式版本计算 `eFG%/TS%/Per36/FourFactors/estimated possessions`；不能把现实NBA Stat官方逐场数据倒灌进游戏虚构赛季。这是游戏世界线独立性要求。

## 8. 本轮验证表、未解决项与下一轮操作入口

| 核对问题 | R01结果 | 下次专用取证动作 |
|---|---|---|
| NBA2K20–23系列可查赛程/旧场Box？ | 有玩家一手线索，但2K22具体操作未证 | 进入PC22现有存档，选1场已经完赛的玩家队比赛与1场AI对AI比赛 |
| PC22是否存在直接Game Logs表页？ | `UNKNOWN` | 球员卡/Stats页签逐一核对；保存完整英文标签 |
| 单场Box具体列及球队合计、首发、DNP？ | `UNKNOWN` | 同一game比对Score/TeamBox/PlayerBox，记录逐字段可见性 |
| League Stats是否提供Per36/Advanced分页？ | `UNKNOWN` | 记录玩家/球队所有统计页签、选择维度及默认值 |
| Shot Chart在PC22 MyLEAGUE是否可按单场查看？ | `UNKNOWN` | 不把MyCareer热区图直接当MyLEAGUE页面 |
| 多少赛季/多长时间还能重新打开旧Box？ | `UNKNOWN` | 在同一存档分别测试当月、跨月、季后赛、下一赛季与重开后；只记录观察，不人为推进正式世界线 |
| Sim standardization对日志/赛程影响？ | 本世代社区有实际异常 [SRC-0008] | 仅独立测试存档比对原始比分与统计，并记模拟参数 |
| 项目现行SQLite能否按player/game取历史事实？ | `NOT_AUDITED_IN_THIS_ROUND` | DEV29最终交Codex进行DEV24/Registry/M0比对，当前不调用DEV28 |

**恢复指针**：本批次 `R01-A` 完成 K01/K02 机制综述、标准派生公式、质量门槛与源/图索引；**R01-B** 优先补“PC22原生统计页/表头原始截图或可审查同代演示”和确切Game Log入口、Shot Chart可选窗口、历史存储期（可能需要玩家截图），然后决定 R01 是否真正 `COMPLETE`；R02研究教练Playbook不应抢在R01残缺核验之前自动启动。

**范围与安全**：只做公开资料研究并保存文字证据。无内存、没有真实游戏写入、没有新采集，没启动DEV28或Codex。玩家批准是任何游戏执行必要条件。


---

# DEV29 R01-B — 原生菜单交叉考证、跨赛季记录与数据质量（2026-10-20）

> **研究进度**：`R01_B_RESEARCH_PUBLISHED_WITH_OPEN_ITEMS`。这一节是R01-A的补充，不改写原始来源或凭推论提升认证级别。没有连接NBA2K22进程、没有PC22游戏截图，因而仍 **没有达到`PC22_UI_CONFIRMED`或`PC22_NATIVE_READ_VERIFIED`**。本节引用`SRC-0016..0025`。

## 9. K02.STAT_MENU — 统计分类“确实存在”与“在PC22哪个菜单”要分离

### 9.1 从2K16原生MyLEAGUE到2K22次世代的证据链

**NBA 2K16 MyGM/MyLEAGUE** 玩家在2015-10-21的Operation Sports问答里明确提问能否看`Player Efficiency Rating`及`Points per Possession`；另一玩家回答进入Player Stats后，反复按PS Triangle/Xbox Y可轮换“regular / per 36 / advanced metrics” [SRC-0018]。这是**较早MyLEAGUE同系列精确操作证据**，比不分游戏的篮球网站展示更有价值，但不是PC22版本证明。

**NBA 2K22 PS5 次世代 MyNBA**：2021-09-10玩家在Reddit反馈，进入player stats，按Triangle到`per-36`后，`PAPG`和`plus/minus per game`排序异常 [SRC-0017]。此证据同时支持 **(a)** 2K22版本中该统计视图真实存在；**(b)** 即使有分类页，也不能信任它的排序逻辑。帖中明确标注PS5，不得升级为PC22本世代已见。

**NBA 2K23 MyCareer**：2023-01-04玩家详细描述从MyCareer→Stats→League Leaders，按Y切换`totals / per game / per 36 / advanced` [SRC-0019]。这是相邻年份操作连续性的辅助证据，但模式不同，PC22不应据此锁定入口。

| 探索顺序 | 研究中已知机制 | NBA2K22 PC证据等级 | 要确认什么 |
|---|---|---|---|
| 1. MyLEAGUE的Stats / League Leaders / Player Stats | 系列提供球员与联赛统计表 [SRC-0018/0017] | `KNOWN_IN_SERIES`; PC22 `UNKNOWN` | 实际菜单名、键位、球员/球队的不同入口 |
| 2. 切换Totals / Per Game / Per36 | 2K16原生MyLEAGUE、2K22 PS5、2K23 MyCareer有相关证据 [SRC-0018/0017/0019] | PC22 `UNKNOWN` | 当前页提示按键、默认视图、数值精度和排序 |
| 3. Advanced统计 | 2K16 MyLEAGUE明确有进阶视图；2K23 MyCareer有 [SRC-0018/0019] | PC22 `UNKNOWN` | 全部表头、公式/指标解释是否有内置帮助 |
| 4. Stats的`Game Log`（逐场明细） | 本轮没有找到2K22 PC独立标签可检证截图；不能把游戏职业模式的`Game Log`文字搬来 | `UNKNOWN` | 是否真正独立入口，还是通过日历→单场Box查看 |
| 5. 各页`Playoffs / Season / Team / Year`过滤 | 系列/现实NBA显示不同视图，但PC22可选项无证据 | `UNKNOWN` | 每种统计页的可选维度和回溯长度 |

### 9.2 玩家具体怎么用，避免操作造成错误决策

先在同一统计页切换并**抄下视图名称及排序键**；在Per-36中任选两名球员，人工验证某列排序与显示值是否一致。在历史球员或替补对比时，如果排序有错误，以有来源的原始数值为准，在Analytics重新排序，不从游戏榜单位置直接做交易评级。

最重要的篮球边界：`Per36`是时间标准化，不是可靠的“真实打36分钟会产出这么多”；高级统计值域/定义、球员场上`OffRtg`与球队估算OffRtg不可仅因名字相同就合并。赛季统计同样可能被模拟分钟标准化和游戏模式影响，必须记录口径。

## 10. K01.HISTORICAL_BOX_ACCESS — 历史比赛记录是可被淘汰的界面视图，不自动是可靠数据库

### 10.1 分清四种历史长度

1. **同一赛季、当天或刚结束比赛**：此前R01-A的赛程/Box导航线索；不是跨季证明。
2. **同赛季跨月（包括CPU对CPU）**：需要复核日历是否仍能打开对应`game_id`的完整个人Box与球队Box。
3. **常规赛结束→本季季后赛**：季后赛Bracket和系列赛Box通常是另一入口；2K20玩家在2K22论坛的回帖描述旧赛次切换操作，但本人明确只确认2K20 [SRC-0006]。
4. **跨到下一个赛季**：保留了职业生涯统计、往年Standings或冠军纪录，并不意味着单场Box、旧Bracket甚至旧赛程还存在。

**2020-02-23 Operation Sports原生MyLEAGUE问答**：Coach2K回答旧赛季的`playoff bracket`不能回看，但能看 previous years standings [SRC-0021]。这不是单场Box已被删除的直接证据，而是“历史视图保留粒度不同”的证据。

**2025-03～04 MyEras回忆帖**：提问者称仍在同一存档，但旧赛季的球队统计和选秀历史不可完整追溯，回复之间存在不一致 [SRC-0022]。MyEras为后来的次世代产品且发帖时间晚于2K22，故标记`LATER_VERSION_CONFLICTING_COMMUNITY_TESTIMONY`；不能用“最多一季”或“全部清除”当PC22保存常量。

**2K23本世代MyCareer问答**：在`Play Next Game`日程向前滚动能查看以往比赛Box，另有玩家成功照做 [SRC-0023]。只证明某相邻版本/其它模式的赛程入口，**不是跨季留存认证**。

### 10.2 研发不可忽视的结果

- **数据采集时效需求**：若游戏历史滚动窗口受限，逐场Box的保存宜以玩家正常触发的全量采集批次尽早归档，并以“已知覆盖率”标记漏采；**不能将此建议理解为本轮允许自动跑采集或赛季推进**。
- **赛季转换前后**：保留两次只读观测的实际`save_instance/season/game_id`集合，比较可见历史范围；若仅保留按赛季汇总统计也如实标`BOX_ARCHIVE_UNAVAILABLE`。
- **对比哪怕同一个比分**：`game_id`、date、home/away、stage、sim_mode、source_menu`必须成组记录，旧年份排名不能替代逐场原始统计。
- **多存档分离**：即使两档历史选秀重演导致日期、队伍和比分相同，也必须靠存档实例区分。

### 10.3 特殊的“比赛打了但记录没保存”

2022-09-21的**2K22/2K23在线MyNBA/MyLEAGUE**玩家集合帖单独提出，在线联赛有比赛完毕不被记录的BUG，并提到帖子附图统计50多场丢失 [SRC-0024]。**只是一手社区故障报告**，而且模式在线、不同于项目离线PC目标；不可说“PC22普遍丢档”。但设计数据质量检查时，应区别 `GAME_NOT_RECORDED_IN_GAME`（没有原生事实）、`NOT_CAPTURED_BY_PROJECT`（游戏内有而外部没采）与`SOURCE_CONFLICT`（有但数值冲突）。

## 11. K02.POSTGAME_SHOT_CHART — 为什么投篮图可以帮助纠正游戏“禁区得分”

**2021-09-24 Operation Sports — NBA 2K22 Useful Findings**讨论，tcnumba10先报告：2K的`Points In Paint (PIP)`可能将禁区外中距离球计为禁区得分；随后解释具体对比方法：在`end-of-game shot chart`看出手区域，再与`end-of-game stats summary`中的PIP比对 [SRC-0016]。这项说法的重要性不仅是可能的BUG：

- **可操作的玩家攻略**：真实玩/观战结束时，进入赛后统计；若屏幕提供Shot Chart和团队Stats Summary，可先定位一组侧翼中投的场上落点，再核对PIP得分是否符合视觉直觉。保存对应`game/session`及截图后才作为实验的对照组。
- **已知与未知**：这表明NBA 2K22论坛一手玩家声称 **赛后有Shot Chart**，并给出了对照用途；**帖子不是我们直接看到的游戏截图**，也没有确认平台、截图具体栏目、是否可跨季打开、是否能导出落点。
- **影响GM的实际解释**：禁区得分异常高可能是球员实战内线攻击，也可能来自统计口径/分区判定，因此不能只凭PIP对教练`Attack the Basket`或内线战术加权；应结合`FGA`分区、3PA、篮板与观战画面核实。
- **禁止不合规纠错**：不通过虚构坐标或减少PIP数值修复；如果游戏原生PIP和可能的区域计算冲突，保留两个来源和`PIP_ZONE_DISAGREEMENT`标志。

**2K22 Hot Zones图像图文出处**：Gamepur在2021/2022版NBA2K22攻略明确指示**MyCareer**打开暂停菜单，切到MyCareer→Stats→Roster，选球员，按R3进入卡片，RT/R2翻至Hot Zones；其文章还谈MyTeam不同入口与红/蓝/灰区域的含义 [SRC-0020, VIS-0004]。这提供了“卡片可能存在热区页面”的版本近似导航，也进一步证明**不能把MyCareer的个人热区页面自动当MyLEAGUE的单场Shot Chart**。截图只是外部页面材料，不擅自上传。

### 11.1 三种常被混为一谈的投篮证据

| 对象 | 实际证明内容 | 无法证明内容 | 处理原则 |
|---|---|---|---|
| `POST_GAME_SHOT_CHART`（2K22玩家报告） | 赛后可依据落点图和统计摘要对照 [SRC-0016] | 保存几年、每次坐标是否可读、所有联赛比赛是否存在 | `KNOWN_IN_SERIES` |
| `PLAYER_HOT_ZONE_VIEW`（2K22 MyCareer攻略） | 个人卡可找红/蓝/灰热区 [SRC-0020] | PC22 MyLEAGUE菜单、单场投篮点 | `VERIFIED_GUIDE_FOR_DIFFERENT_MODE` |
| `RAW_ATTEMPT_COORDINATES` | 若有真实坐标可支持区域自定义、地图与投篮热区统计 | 目前没有本机有效源 | `PC22_NATIVE_READ_PENDING` |

### 11.2 提防PC“NBA2K22截图”被模组改版误导

2021年的NBA2K22 Remastered社区项目明确展示**对PC主菜单/界面进行自定义修改**，宣称为PC引入不同的MyNBA样式 [SRC-0025, VIS-0005]。因此，凡是网上写“NBA2K22 PC MyNBA”的图，必须看作者是否使用Remastered、UI mod或自定义前端；若改过版，最多可用于玩法研究，**不能为本项目原生PC22界面作认证**。

## 12. R01-B 补证后的结论：什么可以告诉GM，什么还不能说

| 知识断言 | 当前适用范围 | 证据状态 | 经营/技术影响 |
|---|---|---|---|
| 可切换到Per36与高级指标视图 | 2K16 MyLEAGUE / 2K22 PS5 MyNBA / 2K23 MyCareer | `KNOWN_IN_SERIES` | PC22应重点找统计视图切换，不能以没采到宣布不存在 |
| 2K22 PS5某Per36列排序有BUG报告 | PS5 MyNBA | `COMMUNITY_BUG_REPORTED` | 保留原值、外部再排序，不直接信名次 |
| 2K22玩家能在赛后看Shot Chart | OS 2K22用户文字说明 | `COMMUNITY_FIRST_HAND` | 把赛后Shot图作为首要定位页；未证历史可重放 |
| 2K22 PIP可能错算某些禁区外中投 | 2K22 OS用户声称 | `COMMUNITY_QUALITY_RISK` | 打`PIP_ZONE_DISAGREEMENT`，不凭单指标调整系统 |
| 旧赛季可留Standings但未必留Bracket | 2020 MyLEAGUE | `OLDER_VERSION` | 历史信息不同层级独立管理 |
| 旧Box跨赛季的完整留存时长 | NBA2K22 PC离线 | **`UNKNOWN`** | DEV28-3必须单独做真实存档只读取证 |
| 原生每场球员与球队Box全字段/英文列名 | NBA2K22 PC离线 | **`UNKNOWN`** | 不生成确定的内存表/SQL输入位置 |
| PC22 Game Logs独立页签 | NBA2K22 PC离线 | **`UNKNOWN`** | 先查Player Stats再查Calendar Box，不假造按钮 |
| PC22 Advanced算法与真实可选全集 | NBA2K22 PC离线 | **`UNKNOWN`** | 若未证，可暂以Box派生指标且显式写公式 |
| 游戏本身的PBP/坐标/真实OnOff | NBA2K22 PC离线 | **`UNKNOWN`** | 不能使用现实NBA追踪数据替代游戏世界事实 |

## 13. 玩家可按图核查的有界路线（只读、不强制开正式存档）

如以后玩家自然处在已打完比赛的游戏界面，一次只读观察即可补上大量未知；**本轮没有要求用户立即操作，亦不启动游戏**。可以依顺序截取：

1. `MyLEAGUE > Stats / League Leaders / Player Stats` 的实际入口及完整底部按键提示；逐次切换并截`Totals / Per Game / Per 36 / Advanced`真实表头、排序。
2. 同一赛季已结束的自己球队比赛及另外一场AI对AI比赛：Calendar→Box的球员/球队页和比分，并记录页签。
3. 一场完整比赛的赛后`Shot Chart`与`Stats Summary`，比较PIP；只看截图不声称有可写源。
4. 若本身已经跨过赛季，在已有历史UI中查询上一年的旧赛程/Box/Bracket/Standings；不要为研究擅自模拟推进正式赛季。
5. 游戏当前版本及是否模组、自订UI；模拟/实战节长和Normalize开关（若UI有）分开记录。

**R01-B阶段结论**：新增的是高价值**菜单线索、统计可信度和历史保留风险**，而不是PC22本机最终认证。R01整体保持`INCOMPLETE_WITH_OPEN_ITEMS`，下一恢复项是`R01-C_PC22_UI_AND_RETENTION_EVIDENCE`（可由玩家日后截图或公开的真正PC22无模组界面逐页补齐）。没有授权任何DEV28/DEV24、Codex任务、原生数据采集或球员能力修改。


---

# DEV29 R01-C：NBA2K22 PC原版统计UI证据复核与GM落地边界（2026-10-20）

> **本轮执行性质**：已独立检索2K22 PC/PS4 MyLEAGUE、Reddit、Operation Sports、Steam、官方制作人报告、公开视频与图文结果；只将实际能核实的事实增补。**尚未找到能够逐像素确证“无模组NBA2K22 PC本世代MyLEAGUE”全套统计菜单、Box表头、Game Logs、历史保存期的公开屏幕证据**。这不是游戏没有这些菜单/数据的证明。原生认证仍为`PC22_UI_PENDING`，无游戏访问或写入。本节来源`SRC-0026..0028`，重用既有`SRC-0015`。

## 14. 官方同年份、不同平台的“Box Score界面”证据

2K22次世代MyNBA（**只适用PS5和Xbox Series**）的开发团队在2021-09-08《MyNBA Full Details》官方说明里单列`COMPACT SPREADSHEETS`，指出`roster`、`coach gameplan`及`box score`表格改用更紧凑布局，一屏能显示以前两倍以上的行数 [SRC-0026]。同一文稿开头明确此新内容仅介绍次世代MyNBA，而不是PC本世代MyLEAGUE。

**实用攻略含义**：
- `Box Score`是开发者明确按名字识别的球队经营表格，不只是比赛直播时的短暂统计提示。
- 不得假设PC22会出现该压缩布局、同一行数或相同横向页签；跨世代UI不同会直接影响截图取证与表头识别。
- “开发者确认存在Box Score表格”不是“每场Box保留多年”或“能按game_id直接导出”。后两者仍未知。
- [VIS-0007]仅索引该官方图文的`COMPACT SPREADSHEETS`标题与相邻**Roster截图**：这张官方示意图**不是Box Score截屏**，不能为Box字段背书。

## 15. PC22 本世代可操作研究：先辨认统计生成机制，再辨认界面

一手同代玩家DarthRambo于2021-09公开其 **NBA2K22 PS4 MyLEAGUE**`Simulation`设置文字清单 [SRC-0015]，显示至少存在以下**菜单组名称的玩家抄录**，这是比NBA.com指标表更接近本项目需求的资料：

| 关联统计 | 2K22 PS4玩家记录的设置组/示例 | 对Box和GM判断的意义 | 不能断言的结论 |
|---|---|---|---|
| 出场时间 | `Setup > Quarter Length` 与`Simulated Quarter Length`（玩家均设11分钟） | 实战与模拟应分别记录比赛节长，跨场比较分钟/场均时先分口径 | 11分钟是玩家选择，不是默认或PC22必然值 |
| 比赛次数与节奏 | `Simulation > Team Style Factors > Team Pace / Team FastBreak` | 改变节奏的设置和比赛产生的回合数有关，诊断进攻不能只看单场PTS | 无证据精确导数/百分比 |
| 回合结果 | `Simulation > Possession Results > Possessions Per Game, Shots, Assists, Steals, Blocks, Turnovers, Fouls, Injuries` | **比赛模拟器设置值**不同于已观测的真实球队统计，应在事实层保留设置快照 | 玩家写的`Possessions Per Game=100`是滑块值，**不是球队实际100回合** |
| 投篮类别 | `Simulation > Shot Types > Dunks, Layups, Shot Close, Shot Medium, Shot Three` | 可解释不同模拟条件下出手结构为什么可能改变；GM可以看`3PA/FGA`或区域聚合 | 不代表`Shot Chart`坐标可读取，也不是球员位置热区 |
| 命中率与归属 | `Shot Percentages`及`Stat Distribution` | 不同类别的模拟参数与赛后Box、季节统计之间存在**需要验证的关联假设** | 不要把数值50当作50%命中率，或宣称每项都线性影响结果 |

**对本项目的运营政策**：上述玩家改倾向/能力的做法属于其自定义阵容；GM Engine严格遵守**不修改普通球员能力/潜力/徽章**的规则。R01只研究观测与解释，**不批准改模拟器设置**；GAMEPLAY参数是否在本项目已受控支持也应由其它既有能力记录决定，不能由本文授权。

### 15.1 “UI统计”和“模拟器生成统计”是两套不同对象

`sim_engine_settings`（比赛前参数）→`played_or_simulated_game`（生成结果）→`post_game_box`（当场观察）→`season_rollup`（赛季聚合）→`external_gm_derived_metrics`（外挂派生）。

箭头是**信息依赖链**，不是对2K内部固定算法或内存对象的证实。若季后赛推进、AI比赛或游戏规则改变，仍须在各层独立记录观察值，不能把赛季平均伪装成历史每场。

## 16. 历史与场内/场外统计不一致：比“Box是否存在”更关键的质量问题

- **2022年同系列玩家公开诉求**：2022年2月 Operation Sports玩家提出“希望2K23把季后赛统计记录得更详细，并能在球员卡上显示季后赛场均/总量/单场最高”，另一玩家明确区分`Current Gen MyLeague`与`NextGen MyNBA` [SRC-0027]。这证明2022年玩家认为某些季后赛历史呈现**不足**，但严格说只是**产品建议而非逐个核对已不存在的字段**。
- **对比更早的PC同系列可复现错误类型**：NBA2K17 PC Steam玩家报告，MyLEAGUE采用“投篮犯规自动给分而非罚球”的联盟规则后，一名球员在场内显示34分，完赛退出Box及赛季统计重新计算只显示27分 [SRC-0028]。这只证明**旧版本/特定规则**曾有屏幕与Box不一致问题；不能声称NBA2K22仍然复现，却证明`displayed_ingame_pts`、`posted_box_pts`、`season_rollup_pts`应在审计时保留三个阶段和差异来源。
- 对已有R01-A标准化SimCast问题 [SRC-0008/0009]，**不要合并成同一个“2K22必然错算”结论**：它们分别是本世代赛程数值与场内不一致、次世代线上统计污染、旧版本特殊规则重新结算，触发条件不同。

### 16.1 将旧R01-A的原始候选字段改成“字段层级字典”（不是已发现的PC22字段）

| 层级 | 首先询问什么 | 最小候选键 | 缺证时的动作 |
|---|---|---|---|
| L0比赛身份 | 是否能找到真实唯一Game ID？有主客/赛季/阶段/状态吗 | `save_instance, season, phase, date, home, away, occurrence, game_id_if_observed` | 不能靠比分匹配两档世界线 |
| L1球队Box | 双方比分、球队合计、每节与加时、来源是赛后还是历史详情？ | `team_game_key, points, fg/3p/ft, reb, assists, tov` | 原生没有该列即`UNKNOWN`，不自己补值当“RAW” |
| L2球员Box | 实际当场team、分钟是否为标准化后、DNP/首发是否可见？ | `player_game_key, team_at_game, min_raw, stats_raw, is_dnp_observed` | 不能把缺行等同DNP，也不能把本队当前归属回填旧场 |
| L3比赛图 | 游戏能显示`Shot Chart`、时段/全场、球员/球队筛选吗？ | `chart_scope, zones_if_observed, attempts_if_observed` | 只有外部图片链接但无落点读数，状态`UI_ONLY`，不可生成`attempt_xy` |
| L4赛季表 | Per Game、Per36、Advanced页的时间窗、排序、是否反映已打Box？ | `season, mode, stat_page, native_value, formula_if_derived` | 排序异常保留原值，外挂重算排序 |
| L5历史寿命 | 已跨季的Box还能由旧赛程和旧球员卡打开吗？ | `queried_season, history_source_page, oldest_visible_game` | `UNKNOWN`；不得猜测一年/永久/最近N场 |

为将来数据质量审计预留三个冲突类型（不预设数据库已经建立）：
`SCORE_CONFLICT_DISPLAY_VS_BOX`、`BOX_VS_SEASON_ROLLUP_MISMATCH`、`GAME_EXISTS_BUT_BOX_UNAVAILABLE`。它们不能互相替代，更不能把“没找到页面”直接判为“游戏没有存”。

## 17. 多轮检索结果判定：已支持到哪里，什么资料不能继续当证据

| 目标问题 | R01-C新增资料是否推进 | 最严格可用判断 |
|---|---|---|
| PC22原版MyLEAGUE统计菜单、Game Logs独立入口 | 搜索未获得可复核的纯原版PC画面 | **`PC22_UI_PENDING`**；绝不声称菜单不存在 |
| PC22球员/球队Box精确列名及分页 | 官方证实2K22次世代`box score`表格存在且新布局；PC布局不同 | **`KNOWN_IN_SERIES`**，字段和值未知 |
| PC22 Per36/Advanced原生选项 | R01-B已证PS5 2K22/老版MyLEAGUE；本轮没有更强PC22证据 | **`PC22_UI_PENDING`** |
| PC22 Shot Chart在历史赛程或赛后可重开 | R01-B已有2K22玩家赛后文字报告；本轮没有PC历史页新证据 | **`KNOWN_IN_SERIES`**，回顾能力未知 |
| PC22旧Box留存跨月/跨赛季 | 2022愿望帖与2020 MyLEAGUE旧Bracket例子都不直接测Box | **`UNKNOWN`** |
| 数据质量依赖 | 明确同年PS4模拟参数目录、较老PC同系列特殊规则计分BUG | **需要对模式与口径打来源标签**；不得概括为PC22已复现 |

**严禁的错误来源替代**：现实NBA.com、Basketball-Reference展示的`Game Logs / Shot Chart / Advanced`是篮球分析方法论，**不是NBA2K22电子游戏UI截图**；同样，`NBA2K22 PC Remastered`自定义版的“MyNBA”截图不能认定原版PC22拥有次世代UI [SRC-0025]。外部早期2K12/2K11“Box Score导出工具”和非同系列模拟器不能用作PC22数据留存证明。

## 18. R01-C实际研究交付与下一断点

**可交付知识**：跨世代“Box Score存在与显示布局”的官方证据；与统计结果直接相关的2K22本世代模拟设置标签；季后赛历史视图需求不足的同期玩家反馈；游戏内与赛后Box差异的旧PC案例；基于原始观测层级的最小验收与质量追踪字典。它们能让GM**知道该问哪项数据、为何不能只信赛季排行榜以及何时必须HOLD判断**。

**不能交付并必须透明说明**：没有完成`PC22_UI_CONFIRMED`，没有确认2K22 PC全部Box表头，没有证明独立Game Logs页，没有跨赛季历史Box寿命，没有访问游戏进程或生成`PROJECT_CAPTURED`数据。研究知识充分不代表工程已能提取这些数据。

**下一恢复指针**：`R01_D_TARGET_PC22_VISUAL_EVIDENCE_OR_CLOSE_UNKNOWN`。优先复核**原版PC22无UI Mod**从MyLEAGUE内`Stats`页以及本队/AI队完赛Box、赛后Shot Chart、历史赛程打开旧Box；如果仍无公开可信屏幕材料，则保持`UNKNOWN`并把“需玩家已有只读页面截图”列为一次性证据请求，终止该轮。**不得无限搜索同质文章，也不启动DEV28、采集、模拟比赛或Codex**。


---

# DEV29 R01-D — 目标PC22视觉证据最终盘点与R01公开研究结案（2026-10-20）

> **终态：`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。** 这是一次有界的公开网络资料取证，不是开发、不是实机菜单认证。本节之后**停止重复搜索R01**；没有看到的字段不填写，不把搜索失败误判成游戏不存在。后续R02研究教练、攻防与Playbook。具体PC22证据作为DEV28/Antigravity未来的**待认证输入**，并不授权现在执行DEV28或任何游戏改动。

## 19. 本轮调查范围、直接证据结果与排除理由

专门尝试按`NBA 2K22 + PC/current gen + MyLEAGUE + statistics / player stats / team stats / game log / box score / advanced / per 36 / shot chart / history`检索：Steam 2K22游戏社区的Screenshots/Discussions、Operation Sports本世代/PC专版论坛、NBA 2K系列指南、公开视频索引，以及页面/图片搜索。审查每个结果是否同时满足**（1）2K22，（2）PC，（3）原版无UI模组，（4）MyLEAGUE，（5）实际可辨的指定统计画面**；只有五项全部成立，才允许`PC22_UI_CONFIRMED`。

结论：**公开可复核材料没有同时满足五项的目标统计页。R01-D新增PC22统计菜单视觉认证为0。** 这一判断不是“经过证明游戏没有此功能”，也不是整个网络必然不存在该图片。

**本轮唯一新增、对PC22确实有所增益的文字资料**：[SRC-0029] Operation Sports `RES2 2K22 All Star Current Gen Sliders` 第3页，2022-01-07玩家`res2`对“是否可用于PC默认阵容”明确答`Yep - PC with default rosters`，并贴出`My League`的Setup/Simulation配置，包括Quarter Length=12min、Simulated Quarter Length=11min、Team Pace、Possessions Per Game、Shot Types、Stat Distribution等。证明**PC玩家在2022年公开了MyLEAGUE设置模板**；但原帖首页§Mode and Roster Notes明确说作者本人主要玩`Season Mode`、自定义球队，其MyLeague配置部分取自另一玩家并作调整，**不能直接断言作者在PC MyLEAGUE实机逐项检视过所有设置**。更不能证明Stats页面、Box表头或默认数值。数值是作者自定义，不代表本项目当前设置，不建议改动。[SRC-0029]

**认真排除的近似结果**：
- [Steam NBA2K22 Screenshots](https://steamcommunity.com/app/1644960/screenshots/) 属于正确PC游戏容器，但可找到的页面或索引没有满足原版MyLEAGUE**统计菜单表头**的具体可审查画面；**Steam页面写着`View Stats`通常是成就统计，不是游戏内Stats菜单**。
- [GameKeys 2K22 MyLeague Player Lock攻略](https://gameskeys.net/how-to-use-player-lock-position-lock-in-nba-2k22/) 的网页含图片，并描述MyLEAGUE中的选队、Options→Position Settings、Player Lock/Position Lock；**它研究的是操作控制，不含本轮需要的Stats/Game Logs/Box字段，也不能单凭按PS按钮判断PC平台**。因此不提升任何R01结果，也不占用新SRC/VIS序号。
- [2K22 PC Remastered修改UI](https://www.2kspecialist.net/2021/09/nba-2k22-remastered-blog-new-details.html)已见旧[SRC-0025/VIS-0005]，会把MyNBA样式带到PC；不能将其作为原版PC MyLEAGUE证据。
- GameFAQs或视频列表出现`NBA2K22 PC`游戏分类、YouTube标题`MyLEAGUE`，**但未获得视频逐帧可辨识目标表头及准确时间戳**；没有将这些弱线索虚构成视频截图。
- [Game/Series其它版本资料](../SOURCES.md)包括2K16 MyLEAGUE按Triangle/Y换统计模式、2K22 PS5 MyNBA Per36、2K22玩家赛后Shot Chart；继续用于玩法研究，但不再被重复计数为PC22画面。

## 20. 目标版本最终证据表：统一状态与后续行动

状态词语义：
- `PC22_UI_CONFIRMED`＝原版PC22本世代离线MyLEAGUE的**真实截图/视频可审查**，包含页面身份与可读菜单/列；
- `CURRENT_GEN_ANALOGUE`＝确认PS4/Xbox One本世代、但PC未认证的相同主题页面；
- `KNOWN_IN_SERIES`＝明确对应其它版本/模式的系列功能；
- `UNKNOWN`＝公开资料还不能认证本项目目标；
- `DEV28_NATIVE_DISCOVERY_REQUIRED`是**未来取证队列**，不是现在执行授权；从UI可见性到原生稳定读取、跨季保存还需独立验证。

| 核查对象 | 最严格主证据状态 | PC22认证字段/操作 | 来源线索 | 后续接手问题 |
|---|---|---|---|---|
| ① Stats菜单、Player Stats、Team Stats、League Leaders全部页签和筛选 | `KNOWN_IN_SERIES`，PC目标项为`UNKNOWN` | **无**。无法给PC22具体按键、表头、Team Stats/League Leaders过滤全集 | SRC-0018较老MyLEAGUE、SRC-0017为PS5 MyNBA；当前PC证据不足 | `DEV28_NATIVE_DISCOVERY_REQUIRED`：认证导航、页面选项全集 |
| ② 独立球员Game Logs，或日历→比赛Box替代路径 | `KNOWN_IN_SERIES`，PC22的独立标签与导航`UNKNOWN` | **无**。未见独立标签，**绝不推断逐场数据不存在** | SRC-0005/0006是旧系列Calendar/2K20季后赛Box | `DEV28_NATIVE_DISCOVERY_REQUIRED`：分别检测Player Stats与Calendar→Completed Game入口 |
| ③ 完赛双方Player Box及Team Box全部字段、首发/DNP/分钟 | `KNOWN_IN_SERIES`；PC22全部字段`UNKNOWN` | **无**。不得将L1/L2候选字段列表视作实际Box表头 | SRC-0026为PS5/Xbox Series MyNBA压缩表格官方文字，无PC Box图 | `DEV28_NATIVE_DISCOVERY_REQUIRED`：同一场双队Box逐列和稳定身份 |
| ④ Per Game / Per36 / Advanced真实分类与栏目、切换方法 | `KNOWN_IN_SERIES`；PC22分类和字段`UNKNOWN` | **无**。不得照搬2K22 PS5的Triangle或老版高级指标表头 | SRC-0017（PS5 2K22）、SRC-0018（2K16）、SRC-0019（2K23 MyCareer） | `DEV28_NATIVE_DISCOVERY_REQUIRED`：每个原生分类表头、排序与派生公式口径 |
| ⑤ 赛后Shot Chart、旧完赛比赛重开、球员/球队范围 | `KNOWN_IN_SERIES`，PC22历史回看`UNKNOWN` | **无**。本轮未见PC原版图，也未取得`attempt_xy` | SRC-0016为2K22玩家赛后文字报告；MyCareer Hot Zone不同 | `DEV28_NATIVE_DISCOVERY_REQUIRED`：赛后/日历详情分别试读、比较Chart与Hot Zone |
| ⑥ 历史赛程、季后赛、跨赛季单场Box留存 | `UNKNOWN`（只有其它版本历史差异） | **无**。没有任何年份保留期限可写成PC22常量 | SRC-0021旧版Standings/Bracket不同、SRC-0022后代MyEras意见不同 | `DEV28_NATIVE_DISCOVERY_REQUIRED`：同一save历史GameID/Box在跨月、季后赛、跨季的可用窗口 |
| 旁证：模拟器统计生成设置 | **`PC22_COMMUNITY_REPORTED_TEXT`**，非`PC22_UI_CONFIRMED` | 有PC玩家列设置类别，**没有目标Stats/Box画面** | SRC-0029为PC玩家文字；SRC-0015为PS4同版本 | 日后复核配置实值只为解释比赛统计，不是R01新增采集 |

**状态决策**：六个目标中 `PC22_UI_CONFIRMED = 0/6`；不是`0/6`游戏功能存在，而是`0/6`达到目前严格的截图认证门槛。没有新`CURRENT_GEN_ANALOGUE` **统计表头图证**；PS4模拟器设置**不能冒充Stats菜单**。从R01-A到D的研究使得数据口径、统计派生、质量风险、证据级别和工程观察目标清晰，剩余是**目标平台直接观察**而非继续推演篮球理论。

## 21. 最少有效截图请求：先两组，后按结果补一组

**优先组A（最小，一次只读查看）**：现有PC22原版离线MyLEAGUE → Stats/Player Stats/League Leaders。给出 **1张“统计模块完整栏目与底部按钮提示”** + **1张“选一名球员后的统计页签/逐场或高级分页”**。若从同一页已能切Per36/Advanced，不必为每个模式重复拍整套；仍未展示的表头保留UNKNOWN。目标是解决①②④的主要分叉。

**优先组B**：在**已经打完**的一场比赛上从Calendar或Daily View尝试打开Box。**1张完整赛程/比赛操作菜单** + **1张Box可辨表头、主客队和对应球员数据**；若同页可切球队合计或另一队，只补切页1张。目标是解决②③和历史回看入口。若菜单没有Box入口，也只记录`NOT_FOUND_AT_THIS_PATH`，不能宣布整个游戏不存在Box。

**只有在A/B仍不能回答时再补组C**：已有赛后 Shot Chart **1张**；如玩家存档已自然跨赛季，旧季同一比赛可否进入Box的页面 **1张**。不为此启动正式赛季推进、模拟或修改。这样通常能用约4–6张高价值截图逐步判别，不要求一次覆盖游戏所有页面。

图片必须带`version=NBA2K22`、`platform=PC`、`mode=offline_MyLEAGUE`、`original_ui/not_modded`、当前赛季与入口上下文；对无法完整判断的属性保留UNKNOWN，不假造视频时间戳。**这是未来可选的人工证据，不是本轮玩家必须立刻提供的材料**。截图授权登记见[VIS清单](../visuals/EXTERNAL_VISUALS.md)。

## 22. 研究结案与R02交接

**R01-A/B/C/D文献研究完整封存**：不再为了搜到一张可能的截图而无限扩充老版本论坛与统计公式。核心结论：逐场数据与赛季累计不是一回事；Game Logs是否独立不能代表Box是否存在；Per36与Advanced的可派生部分可由真实原始Box谨慎计算；Shot Chart/Hot Zone/出手坐标是不同数据层；跨赛季留存和统计生成口径必须单独证实。它们对GM经营具有实际用途，已在§§0–18详解。

**未来DEV28/Antigravity交接（仅积压，不启动）**：使用上面的六行需求、图证TODO及候选数据层L0–L5，首先只读确定PC22界面/历史对象，再定向找game identity、Box、shot zone和advanced的真实原生来源；`PROJECT_CAPTURED`与`GM_QUERYABLE`必须由未来独立正式验收，不得因R01完成自动提升。对于不同历史选秀世界线，不从现实NBA.com导入与游戏赛季不同的场次/结果。

**下一研究轮直接R02**：Coach Gameplan、POE、ACE、Playbook、12类战术、Freelance、PlayTypes/Play Discipline、个人与团队防守；优先K04教练攻防的“玩家实际有哪些菜单和值域、如何联动”的中文攻略，先读当前开发文档/已认证源码范围，按DEV29规则核实社区/官方图文并发布`guides/K04_COACH_AND_PLAYS.md`；**不启动DEV28，不要求R01先拿到完美截图**。

> 结案标识：`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`；`R01_D_TASK_CLOSED`。仍可在未来获取真实PC22画面时只增量更新具体UNKNOWN项，不能因此重启整个R01网络研究。
