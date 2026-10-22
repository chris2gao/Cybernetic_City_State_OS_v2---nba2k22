# DEV24 — 给Antigravity的逐场与高级统计源扩展建议（BPTI/M3联用）V1

> **DEV28后续接入指针（2026-10-20）**：玩家在BPTI包C之后提出GM输入输出全透明及动态比赛/球员数据完备性的下一阶段目标。本文件的源/身份/质量/查询要求由[DEV28 D28-3](DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)复用，**并不是现在自动启动游戏数据采集的授权**。Antigravity负责实际原生观测，Codex复用`full_verified_v1`/M0/SQLite，不重写第二套比赛事实规格。

2026-10-20 | owner: Web GPT Development | 状态：SOURCE_REQUIREMENTS_PREPARED / ANTIGRAVITY_SEPARATE_USER_TRIGGER | 不自动授权开发、游戏访问、采集或数据发布。

> **2026-10-20玩家最新调度：DEV24暂缓到BPTI B0–B6全部完成后再由玩家触发。** 本文为需求清单而非正在运行的工作命令。BPTI先使用现有赛季累计/原生配置可信数据建立认知、静态映射和决策合同；未观察逐场数据时不可宣称已实现逐场趋势推理。任何真实新档的生产数据可信度门槛不因后置而取消。

## 0. 当前真实数据边界

截至本任务编写前的repo `config/source_catalog.json` / `docs/24_DATA_SOURCE_REGISTRY_AND_PLAYER_TRIGGERS.md` / `docs/31_SOURCE_EXTENSION_DISCOVERY.md`：
- `games_box_scores_standings`仍标`VERIFIED_PARTIAL_SEASON_TOTALS`，包括30队当季胜负/赛季累计和约389名当前有索引球员的赛季合计；**无逐场赛程、逐场Box Score、比赛类型、月度分段**。
- `injuries_availability_rotations`仍`NOT_OBSERVED`；完整当期球员上场分钟/伤病/疲劳/阵容出勤是明显GM诊断缺口。
- `team_monthly_stats`/`player_monthly_stats`虽含net/ORtg/DRtg/pace、PER/USG/TS/plus-minus等**可空schema预留列**，不表示已有对应原生观测。
- 当前M3/DEV14已可在采集批次中读取教练、68槽、本队对手PERSONAL、具名Tendencies、4 PlayTypes与训练；**不要与本次比赛源重复开发**。
- 本次玩家已让Antigravity开始全量数据源扩展，下面是可直接合并到其设计中的**建议优先字段和接受/放弃标准**。先盘点Antigravity正在实现的真实能力，避免重复编码、重建管线或打断进度。
- 保持原`full_verified_v1`的全量采集业务入口，同批真实性审计。这里的`historical game tables`是**一轮全量更新中可包含多条历史已完赛记录**，不是另开每场都必须全量重抓一遍的触发模式，也不要求逐场保存完整游戏进程内存。

## 1. P0 最重要：比赛实体、日程和双队关联（先把事实颗粒度做对）

目标：任何一场已完成比赛在SQLite内都能唯一识别，可按球队、赛季、日期、对手与赛程阶段查询；相同比赛在两次采集中不能复制或覆盖成两个事实。

建议对象`game`：
- `save_id / save_instance_id / generation_id / source_batch_id / observed_at`、`game_native_id`（仅若原生ID可确证）、`season_id/year`、`game_date`（游戏真实显示/玩家明确输入，分清来源）、`season_phase`（preseason/regular/playoffs/play_in/other/UNKNOWN，以真实原生枚举确认）、`scheduled_vs_completed`、`home_team_native_id`、`away_team_native_id`。
- `home_score/away_score`、`result_winner`（可推算，勿把未来未完赛记作已知比分）、`overtime_count`（若可见）、`game_duration/quarter_length`（如有）及`round/series_id`（如游戏可读）。
- `source_object_identity`与`source_view` (SCHEDULE/BOX_SCORE/GAME_RECAP/UNKNOWN)、`observed_status`。如果不能拿到Native GameID，稳定自然键含真实存档实例+赛季+日期+主客队+比赛类型，并显式标`NATIVE_GAME_ID_UNAVAILABLE`；同日重复对阵时需附加来源可区分符而非默认为唯一。
- 重复采集去重、两队胜负/比分对称、常规赛时积分一致性、赛程已结束记录守恒；不靠当前累计战绩反推逐场对手或比分。
- 每场有不止一个真相来源（scoreboard和recap不一致等）时保存冲突/缺失，而非静默覆盖。未完赛Future Schedule只给比赛配对和时间，严禁提前写赛果。

## 2. P0 玩家Box Score和球队Box Score（有游戏页面/可认证内存时必优先）

`player_game_stats`：复合键`game_key + player_native_identity(+team_native_id)`；至少尝试`starter/played/DNP_reason / minutes_seconds / points / FGM,FGA,3PM,3PA,FTM,FTA / offensive_rebounds,defensive_rebounds,total_rebounds / assists,steals,blocks,turnovers,personal_fouls / plus_minus`；某字段真实页面无值则NULL/NOT_OBSERVED。受伤、交易导致球队改变时用比赛当时`team_native_id`，不使用当前名单覆盖历史比赛归属。DNP不得默认为0分钟及0出手，除非真实源如此确认。

`team_game_stats`：双方得分、FG/3PT/FT命中与出手、篮板、助攻、失误、抢断、盖帽、犯规；如来源有失误来源/快攻分、禁区分、失误得分/二次进攻分、领先变化、最大分差等可选保留。**比赛球队数据不能从当前赛季累计拆回单场**。个人统计和球队统计可核对时应核对场次得分/投篮并解释team rebound等非个人求和的合法差异。

必要的玩家运营查询：
- `team last N games`、`player last N games`、`team vs opponent`、`quarter/playoff segment`、`played vs DNP`和`coach/control changes before/after`。
- 不要求每次GM窗口直接dump全联盟全部Box Score，只需M0受控SQL接口提供有界列表/分页和可追溯游戏ID。

## 3. P1 高价值且非常适合BPTI的来源

按照“游戏真实能显示/内存可认证，再入库”：
1. **投篮分布和机会类型**：逐场个人/球队`paint, restricted_area, midrange, corner3, above_break3` FGM/FGA（如果UI提供），shot chart/shot location（若可见）；`assisted/unassisted FGM`、catch-and-shoot/pullup、post、PnR ball/roll/offscreen/handoff/ISO频率与PPP**若没有真实游戏源则UNKNOWN**，绝对不能凭一项总命中率反推战术调用。
2. **完整球员出勤/伤病/疲劳/阵容轮换**：游戏能读到的球员伤病、可比赛状态、体力/疲劳、实际每场分钟、首发、轮换顺序/深度；尽量能按比赛前后或至少同批日终记录。在不同时间点有身份版本，未捕捉到赛中即时伤情则NOT_OBSERVED。
3. **节次分数/球队高级表现**：按节比分、加时，帮助观察关键时段；如果球赛页面有PACE、OffRtg/DefRtg/NetRtg、TS%、eFG%、TOV%、OREB%、FT rate、USG%、AST%等，可以直接保存原生显示值+定义/分母+来源。若仅有基础count，可由下游Python**带公式与估算标识**计算eFG%、TS%、AST/TO、FTr、per-game possession estimates及基于合理前提的ORtg，不能把估计回合写成真实tracking possessions、不能用“高级”名称伪造真实原生字段。
4. **本次上场阵容上下文**：若游戏提供五人组/二人组±、on/off、时间/阵容组合，独立采；若只有player plus-minus，不能推出整支球队五人组净效率。
5. **比赛结束控件/场上控制类型**：能认证玩家3D/CPU CPU 3D/Calendar Fast-Sim标签则可保存独立`game_provenance`，但**用户后续提供的季后赛3D场次清单是校准器的重要正式输入**；不能仅凭某场统计倾向猜该比赛的仿真类型。正常GM数据消费不按照3D/Sim分裂；只有独立校准器按标记分层。

## 4. P2 价值有但不用阻断BPTI开发的长期来源

- Play-by-play/事件时间轴、战术调用/ACE行为事件、切入/掩护类型、回合详细接球人与投篮来源——**没有实际游戏页面/可靠记录即NOT_OBSERVED**，不主动做ACE逆向。
- 视频级防守轮转/高阶空间tracking、传球网络、真实Defensive assignment、球员赛时疲劳曲线。对BPTI锦上添花，但不作为此批采集完备性目标。
- 人物媒体、球员关系、士气故事、完整财务CBA等，均为本次统计扩展之外。

## 5. 采集与审计的关键不变量

- 保持现有SQLite双事实库/受控query_snapshot语义；新增比赛历史事实是原源真实观察的派生持久表，**不是通过Web人工虚构比赛、重新生成赛程或新的事实权威库**。
- 遵守GM Potential遮蔽和同批要求，新增`source_catalog`覆盖和状态；身份关联采用游戏原生稳定ID+存档实例+批次映射，存在同名/交易/改存档冲突时BLOCKED/UNKNOWN。
- 标注统计是`NATIVE_OBSERVED` / `DISPLAY_OBSERVED` / `DERIVED_EXACT` / `ESTIMATED_FROM_BOX` / `NOT_OBSERVED`；定义高级统计公式的`metric_spec_version`及分钟/加时分母；避免本局和现实NBA统计混用。
- 时间范围：一场历史比赛首次被抓取时的`game_date/season_phase`依真实源记录；不能假设游戏内存保存过去每场Box Score。**若游戏只存最近几场记录，明确history retention window与backfill capability，不编造缺失历史**；定期玩家触发完整采集可能无法恢复被游戏覆盖的详情，需要玩家与开发者根据实测决定下一步采集触发频率。
- 对每批比较`new_games/updated_games/unavailable_games`，检查已完赛比分、球队得分、已采比赛累计与真实赛季累计趋势；不一致不是强迫“修好”，而是`DATA_GAP/CONFLICT`。
- 不为这些需求设计复杂常驻抓取守护或隐式后台读取游戏。当前玩家明确触发的全量采集入口保持；若确实发现历史比赛详情只短期保留，**单独提出最小新增玩家触发点建议**，由玩家决定是否增加。
- 先查Antigravity当前进行的扩展清单，已覆盖的字段不要重复作业。每一类新数据首次成功抓取需要只读观察证据、稳定身份与字段解码、数据行样例、覆盖/缺失报告；真实生产游戏访问/发布按玩家分开授权。

## 6. 适配BPTI的轻量消费契约（后续Codex按授权接M0/M3）

优先支持以下GM层问题，而非建立新的综合排行榜：
1. 最近N场进攻“结果”变化是否真的在本队多个球员/阵容中出现，而不是只看赛季总值？
2. 核心与替补是否承担了SystemBlueprint预期的触球/得分/组织/护筐职责（仅在来源支持时作推断）？
3. 某角色缺口是技能不足、没机会、因伤病未上场，还是当前战术书可能没给他分配正确PlayType？
4. 新战术/人员/教练更动前后，哪些可观察数值变化，样本和对手有多大限制？不能由相关性直接说该改动造成胜率上升。
5. 若数据无法回答“防守到底采取了Drop还是Switch”，明确`MECHANISM_UNOBSERVED`，需要篮球逻辑/录像案例和源扩展而不是猜。
6. 保留每场必要gameID和统计基础，为后续独立双引擎校准器和季后赛历史积累提供事实入口；BPTI当前不直接调整Simulation Sliders。

## 7. 交付给Antigravity的优先清单（可复制）

**先做P0**：赛程/比赛身份+最终比分+双方球队箱分、每名实际出场球员每场箱分/分钟/DNP/±，做好两队关联、历史去重和采集覆盖报告；还要确认游戏是否保存全部历史比赛详情，以及何时会被覆盖。

**然后P1**：比赛前后球员伤病/可用性/疲劳、按节比分与相关Game Recap；游戏真实提供的高级统计/投篮区分布按有据字段采集；若只有基础计数，用Python衍生eFG/TS等并明确估算，不要伪造原生高级指标。

**暂不做P2**：ACE战术调用逆向、所有五人组合/Tracking/全场回合事件。需先说明是否在当前游戏中实际存在可认证来源及复杂度，未来独立授权。

根据玩家最新调度，Antigravity的DEV24扩展**后置至B0–B6完成之后**，届时再单独授权。B0–B3依据现有同批coach/player/roster字段设计；B4的比赛趋势诊断在无逐场来源时应输出NOT_OBSERVED或不执行，不能伪称完整球队运行行为。
