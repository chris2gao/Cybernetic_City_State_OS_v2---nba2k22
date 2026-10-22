# K11 — NBA2K22 赛季阶段推进、保存、重启及跨季数据留存（R06-C）

> DEV29 R06-C / 2026-10-21。目标：NBA2K22 PC本世代离线MyLEAGUE。只研究游戏原生信息、实际玩法、可能的阶段与信息反馈，不实施自动推进、存档操作、角色人格、DEV28或游戏写入。来源：SOURCES `SRC-0187..0199`；机读目录：[R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json](../catalogs/R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json)。

## 15. 五个彼此独立的时间和保存对象

| 对象 | 什么才是原始权威 | 不能偷换成什么 |
|---|---|---|
| 游戏现实时间 `game_date` | 当前MyLEAGUE存档内日期/赛季阶段与原生赛程页；**当前存档值本轮未读** | 研究当天真实日期、GitHub提交日期、用户重开窗口时刻 |
| 比赛 `game_id / result` | 同档同比赛状态+3D结束/日历Sim/Box/赛季聚合各来源标签 | 仅凭月度总计倒推完整逐场比赛/投篮分布；Normalize可能污染显示 |
| 游戏保存 `save_slot / save_revision` | 游戏Save/Save as界面动作后退出并重新加载核实 | 内存中已变化/外部SQLite文件已更新，就等于游戏写入持久 |
| 数据采集 `capture_batch` | 玩家触发本批`full_verified_v1`并按项目已有审计发布，绑定真实加载的档和游戏日期 | 调用GM模型、GitHub push、本地复制数据库自动推进游戏 |
| 外挂选秀轮回 `draft_cycle_index` | 项目规则1984→2020→1984，经过玩家批准、确已完成的每一届选秀后才前进 | 游戏年份=1984，或赛季换年就自动advance历史新秀年度 |

R06-A区分`LIVE_3D_CPU_CPU`与`CALENDAR_SIM`，同Game ID应分开`played_quarter_length`、`simulated_quarter_length`、Normalize Minutes/Stats、现场结束比分、日历比分、Box和赛季累计。**更改真实游戏日历时间不应由R06研究模型发起**。

## 16. 常规赛、交易截止、季后赛：对用户可见的推进动作

2K22 MyLEAGUE支持`Start in Regular Season`与Setup阶段选项（SRC-0189）；同版PS4玩家实践了82场常规赛、季后赛各轮Best-of-7和3D/SimCast混合玩法（SRC-0199），是**个人配置而非目标PC22默认规则**。赛程/比分来源宜分`SCHEDULED / LIVE / FINAL_3D / FINAL_CALENDAR_SIM / SIMCAST_JUMP_IN`；这些是研究分类，不表示当前项目已具备该原生状态枚举。

玩家通常通过日历选定单场、模拟一部分赛程、进入季后赛以及完成系列赛；具体`Sim to Date`、`Sim Through Date`、`Sim Through Game`等按钮文字、输入确认、可否跳过交易截止，R06-C **没有PC22逐页截图或实机读回，保留UNKNOWN**，不制造精确UI操作指令。

对未来GM/Coach/Player/Media而言，可观察事实应当有`season_id`、`game_date`、`game_phase`、`regular_season_completed_games`、`playoff_round`、`series_id`、`game_id`、`opponent`及获证的`event_timestamp`。交易截止日期、季后赛赛制若被游戏内联赛规则更改，不能固定按现实NBA2022日历日期换算为目标存档时间。本轮没有找到能证明当前PC22精确交易截止**按钮/时间值**的一手页面。

## 17. 赛末→休赛期→新赛季：研究清单与已证的范围

一位2K22主题里的2022-07资深MyLEAGUE用户（SRC-0188）提供了以下**推荐存档检查点**，从旧版本经验总结，且特意承认“Staff Hiring阶段可能是最后加载新秀名单机会”未确认2K22：

1. 季后赛结束、尚未进入Offseason；2. Draft Lottery前；3. Staff Hiring阶段；4. NBA Draft前；5. 签约新秀（Rookie Signing）前后；6. Free Agency Moratorium第一天；7. Training Camps前。

**上面是用户的建议检查点，不能当本机PC22恰好七个阶段、严格阶段顺序或按钮完整列表。** 它直接提供了研究入口：每个阶段至少记录目前页标题、游戏日期、操作前后合同/球队名单/选秀资产/球员年龄与退役状态，以及越过阶段后是否能反悔、是否自动完成一部分AI交易。

游戏同版攻略确认自由市场页可看报价数量、预期薪资并进入谈判（SRC-0190）；2K22退休/转教练攻略确认存在赛末Retirements页面以及转下个赛季的人员流动概念（SRC-0198）。但它没有确认当前所有人员都可转教练，更不允许照教程对球员改年龄或能力以诱导退休。

R05经营研究已有合同、员工、选秀、市场字段候选。**这项R06-C只研究其“何时生效、如何保存、跨阶段旧状态能否取证”**。真实NBA的June/July日程不能照搬为PC22每个阶段的原生模拟日期。特别是现有`approved_signing_v1_unvalidated`尚不能据“游戏进入Moratorium”擅自开写；休赛期合同竞价应另外按其已批准业务机制和真实时点认证。

## 18. Save、Save as、Autosave、外部副本：何者能恢复什么

同版PC Steam玩家2022-07称其MyLeague使用`Save`与`Save as`后退出，文件仍不见（SRC-0191）；另一位PC玩家2022-03报告MyGM保存页卡住和MyLeague存档列表突然消失（SRC-0192）；另有PC用户称新MyLeague保存后不持久，网友猜测下载队伍/总存档量过多（SRC-0193）。**仅为不同个案、猜测及模式混杂，不能宣布2K22全部存档默认损坏，或给出确定硬上限数字**。

可采取而不是宣称已实测的安全理解：
- `Save`：可能覆盖当前槽；`Save as`：可能生成独立槽，但必须退出并重新加载新槽、核对游戏日期/球队数据后才能认定。
- `Autosave`：设置开启不说明触发频率、是否先写磁盘、是否能恢复覆盖前状态；本轮未证精确菜单和时机。
- `Steam Cloud`：2026官方通用说明涉及Steam客户端云同步及游戏支持（SRC-0197），这是**平台二级复制**，不能保证旧版2K22本档已成功同步，也不同于`MyLEAGUE`当前手动保存。
- `project database`：DEV14的`league/pool/control`数据库、GitHub latest.json与Game save是不同物理资产；已发布SQLite仅保存采集源的观测，不保证内存操作已经持久化到真实游戏。
- **回滚**：读取旧游戏槽 ≠ DEV14条件原生内存回滚 ≠ GitHub恢复旧数据库代次；这些每一个都需要独立角色/来源/审批及真实观察。

Game保存检查属于以后针对当前PC22的独立实机取证，不在DEV29运行。用户没有要求截图前不得要求其批量进入生产档，尤其避免通过“测试”误推进正式赛季。

## 19. 再次进入存档后的长期状态与历史归档风险

**分清“游戏还记得”与“游戏保留完整供我们查询的历史”。**

前代MyLEAGUE用户报告过往球员统计年份错配及奖项历史消失（SRC-0195），更旧社区还在询问能否查看退役非明星球员过去赛季、历史完整选秀顺位和旧赛季交易记录（SRC-0196）。这是**观察和版本缺口线索**，不是当前PC22赛季数据已丢失的证据。NBA2K22当前本局尚未实机验证以下每项：`PAST_SEASON_STANDINGS`、`PAST_BOXSCORE`、`PAST_GAME_LOG`、`CAREER_SEASON_STAT`、`PAST_DRAFT_BOARD`、`PAST_TRANSACTION_LOG`、`AWARD_HISTORY`、`RETIRED_PLAYER_DETAIL`及`NBA_RECORD_HISTORY`。

风险与依赖：没有逐场GameID/Box可能无法在赛后事后补出逐场数据；离开某一阶段后原生菜单可能变化或历史页将旧数据汇总；NBA2K系列先前出现Stats/Minutes Normalize不一致（R06-A）；球员退役/转队后`player_id`、`season_id`身份不可仅按姓名确定。**不得据此发明“只能保留一年”或“游戏自动删去所有Box”的固定规律**。

给DEV28未来数据层的**研究需求**是：在玩家可验证的阶段边界前存`current game_id`与受支持Game Log/Box、当前名单/合同、球队财政、选秀球员ID、联盟奖项和已知新闻/纪录的完整捕获快照，待取证确认具体哪些字段真的可能丢失。这里讨论的是**采集需求，不是授权自动触发全量采集或修改现行仅玩家触发的规则**。

## 20. 项目现有多存档/分支数据与游戏Save的关系

项目已有DEV14手册`docs/DEV14_STATE_IO_RUNBOOK.md`，其save管理规定最多四档、一个ACTIVE，以及`save_id + save_instance_id + generation_id`、来源批次、只读捕获和执行提案审批。另`docs/27_DATA_WINDOW_RUNBOOK.md`要求玩家确认当前游戏加载存档并触发`full_verified_v1`，不得从旧来源混合出当前批次；管理层数据库`league_state/player_pool/control`与游戏物理存档仍不同。

现有文档对DEV14部分模块使用`ENGINEERING_IMPLEMENTED`或`REAL_CAPTURE_NOT_TRIGGERED`状态，R06-C没有运行代码/游戏，不把文件含有原生字段当已证持久化。可观察的`save_generation`与真实游戏跨年阶段如果不同步，应留证据并让用户判断，不允许模型静默替代真实游戏时间。

项目游戏权威仍然是`NBA2K22已存盘真实状态`。GitHub repo commit日期、数据发布时间、当前聊天真实时间不可以推导新的`game_date`。

## 21. 对未来六类参与者的可观察资料与边界

- **采集模型**：当前存档身份、真实game date、赛季阶段、各游戏页面可见数据与来源版本；缺项记`NOT_OBSERVED`。
- **数据分析模型**：知道每场是3D/SimCast/Calendar哪套原生路径生成、数据标准化设置与统计时间窗口；不能只靠老赛季总平均构造Box。
- **Coach**：赛前赛后阵容/对手/结果/战术信息的所在游戏阶段与时效；本研究不安排他的个人行为。
- **Player**：身份、历史合同、奖项、伤病/退役真实状态的可得性、更新时间与剩余期限；不设计人物要求或性格。
- **GM**：市场/交易截止/休赛期/未来选秀权业务的合法时间窗口与数据真实性；不设计必然买卖方案。
- **Media**：赛果/比赛纪录/官方奖项何时已经确认，媒体模板与预测未确认时不得反向写成比赛事实；不开发独立记者Agent。

## 22. R06-C结果与继续条件

**结论已知**：2K22本世代玩家能使用多种赛程、实场/模拟/季后赛形式；2K22同年社区确有多存档休赛期分段经验和原生PC Save/Save as的使用及故障个案；官方确认NBA2K22 MyLeague离线可用（SRC-0187）。

**尚未认证**：目标PC22存档所有赛季阶段的逐帧菜单/时点、Game Date原生偏移与真实读回、Autosave触发规则、Save as覆盖规则、Steam Cloud当前同步、跨赛季逐场Game Logs/Box/历史获奖/选秀/交易保留长度。**本研究运行时采集次数0、游戏推进次数0、写入0、原版PC22合格新视觉截图0**。

本轮标记：`R06_C_RESEARCH_PUBLISHED_WITH_PC22_PHASE_SAVE_RETENTION_GAPS`。下一轮：`R06_D_CROSS_DOMAIN_SYNTHESIS_AND_GAPS`；之后R07统一研究/证据/行动矩阵与最终小型FINAL-CODEX。R06-D前必须确保R06-B审核Q1/Q2/Q3修正已完成；本次已进行定向修正，但独立审核是否接受仍由后续审核决定。