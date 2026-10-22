# DEV-20261018-08 — 全量更新原则下的教练数据源首次正式启用（开发规划，不新增专项更新）

- 日期：2026-10-18
- 状态：`FULL_REFRESH_POLICY_CONFIRMED / IMPLEMENTATION_ALREADY_IN_MAIN / FIRST_PRODUCTION_CAPTURE_PENDING_PLAYER_TRIGGER`
- 工程仓库：`chris2gao/nba2k22-gm-engine`。
- 重要：**本规划不是新内存读取器、SQLite教练schema、专项更新命令或同步协议的开发请求。** DEV07 V2 的教练数据源已随 PR #1 于2026-10-18合并main；只是目前线上生产最新批次来自2026-10-17旧代码，尚无第一份真实发布教练来源。首次运行结果未见证据，不能标记“生产已验收”。
- 用户最新明确规则：**任何新游戏数据采集/更新，一律运行完整`full_verified_v1`全量流程，刷新全部已验证来源**。此前讨论过分来源更新，Codex已建议因采集脚本化、工作量适中而取消；这一结论现在由玩家明确确认，取代旧文档中“优先开发单来源生产更新、球员池年更/统计月更、跨来源不同采集时间组合”等所有建议。**不开发**`COACHING_ONLY`、`--sources`、`--only-stats`、`--skip-player-pool`、跨来源时间复用或多套latest。
- 用户游戏和权限规则保持：数据采集、GM决策、受控游戏执行分别由玩家触发；教练执行批次只有具体批准可内存写入。采集只读、不修改游戏，也不自动触发GM或下一任务。发布仍需玩家给出本次`-Publish`授权；单纯对同一有效批次的**重新发布**是同步操作，不属于“新采集/更新”，可继续沿现有republish命令。

## 1. 当前代码与数据事实（已审查main源码）

| 能力 | 现状 | 依据 |
|---|---|---|
| 全量游戏数据采集 | 已实现 | `scripts/run_data_update.ps1` 调用 `scripts/run_admin_data_capture.ps1`，`full_verified_v1` |
| 原生教练采集同一RO会话 | 已实现 | `src/auto_pipeline_ingest.py` 中 `capture_coaching_source`、`store_coaching_source`，同一snapshot_id，失败则回滚 |
| SQLite原生教练表 | 已实现 | `coaching_source_captures`、`coaching_team_observations`；保留各队19默认战术、4套Freelance、主教练身份、对手整体防守观察 |
| 采后同源只读审计 | 已实现 | `src/coaching_source.py` 与现有审计流程，30名HEAD_COACH / 29条对手records验证 |
| 导出和GitHub同步 | 已实现 | `src/export_web_gm.py` 输出 `coaching/teams.json`、`field_dictionary.json`、`opponents/index.json`、`opponents/<TEAM>.json`，manifest/source_coverage、latest一致；`-Publish`调用旧发布器 |
| Web GM读取 | 已实现 | `src/gm_core/data_reader.py` 以同一已发布batch装载30队`coaching`，按需读取指定对手文件 |
| **本局首次真实生产教练数据包** | **未见发布证据** | 当前`mc_haliburton_2021`线上latest是2026-10-17的旧批，旧`teams/IND.json`只有`state/roster`，且该batch没有`coaching/teams.json` |
| 单项/专项源刷新 | 用户明确取消 | 不作为缺陷或规划目标 |

**不要**把旧队伍`team_monthly_stats.poe_*`当教练配置：它们是`LEGACY_UNVERIFIED`的历史原始字节。SQLite旧`teams.primary_system`、`coaches.preferred_system/active_system`只是兼容字段，权威源为本批`coaching_tactics`原生COACHDATA读取。

## 2. 唯一当前执行任务：首次玩家触发的正常全量更新

本开发规划**不授予本轮立即运行采集、发布、写游戏、合并PR或重新开发功能的权限**。

用户下一次明确触发数据源更新时，由DATA/Codex按实际游戏时间、存档及用户发布要求：
1. 先核对本地`main`已含合并代码、游戏已加载正确存档、当前有效进程、存档ID及玩家给出的`game_date`。已知`mc_haliburton_2021`是历史候选ID，具体以玩家本次指定为准；绝不自动把历史日期当今天游戏日期。玩家明确允许未知日期可用`-GameDateUnknown`，但这会保留游戏日期未知，可能限制GM正式方案生成。
2. 调用**现有**`scripts/run_data_update.ps1`：一次性完整采集已验证的球员池、阵容/薪资、制服组、球队与赛季统计、选秀权、原生教练战术和其他当前已认证来源；不需要先跑独立`coaching_snapshot.py`，不需要专项更新CLI。
3. 同次只读内存校准和审计中，原生`coaching_tactics`必须在SQLite形成唯一30支球队快照，HEAD_COACH归属及19默认字段合法，30×29对手整体防守对象完整（按当前已认证的本局原生布局）；游戏异常/换帅/场景失效应fail closed。不得因某一字段读不到就伪造值。
4. 现有导出器生成本批JSON/SQLite归档与新的`latest.json`；`source_coverage.json`必须含`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`，`coaching/teams.json`恰含30队，`coaching/field_dictionary.json`含19可执行默认字段和针对对手18项各自enum/作用域；按需检查某队`coaching/opponents/<TEAM>.json`恰含其他29队。审计时采集/更新批次和教练数据原始同源，不出现“本月统计+上月教练”混合版本。
5. **只有本次玩家明确要求`-Publish`**，才按现有发布器上传GitHub，远端`latest.json`须显示`upload_status=UPLOADED`与可信`data_updated_at`/`uploaded_at`、`batch_path`指向新全量包。若仅本地更新，无`-Publish`，不能声称网页GM已取得新数据。
6. Web GM用 `published/index.json→latest.json→source_coverage.json→coaching/teams.json→field_dictionary.json`，通过`team_id`将教练信息与`teams/<TEAM>.json`阵容、战绩等**同一完整批次**关联；分析特定对手时才读`coaching/opponents/<TEAM>.json`。GM若读不到或审计状态不合格，则教练写入方案HOLD并报告来源缺口，不用旧`poe_*`替代。
7. 完成数据任务后明确输出`DATA_READY_AWAITING_PLAYER`及batch/时间/存档/是否上传；**不要自动触发GM决策、战术写入、保存游戏或下一轮流程**。

示意命令，仅在玩家下一次正式授权后填入正确参数再执行（不是要求现在就执行）：

```powershell
# 以用户提供的真实career ID、当前游戏日期及赛季/月为准
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_data_update.ps1 `
  -SaveId '<PLAYER_CONFIRMED_SAVE_ID>' -GameDate '<YYYY-MM-DD>' `
  -Season 2022 -Month 1 -Event checkpoint -Name COACHING_FIRST_FULL -Publish
```

不要把`Season`、`Month`或`GameDate`示例当当前真实游戏事实。仓库已有`-GameDateUnknown`路径，但精确日期优先由玩家确认。

## 3. 教练方案执行后如何同步

- GM基于**最近一次完整、已发布、已认证的全量batch**作出各队教练战术提案，需玩家单独批准`batch_id/decision_id/version/完整action_ids/digest`；Codex执行脚本按手册40修改实时游戏内存、回读并给receipt。
- 执行模型不手改SQLite或已发布JSON来伪造游戏观测；`COMMITTED_VERIFIED_IN_MEMORY`也不代表保存已完成。
- 当玩家下次**明确触发全量更新**时，重新采集全部来源（包括调整后的教练现值），产生新独立batch并按玩家要求发布。GM下一个节点从新batch读原生设置。**不要求每次执行后自动启动全量更新**：触发权仍由玩家掌握。
- 历史immutable批次保留原观测；`latest`仅指向玩家实际发布的最新完整批次。已存全量批次重新上传是`REPUBLISH`，不改`data_updated_at`。

## 4. 必要验收与故障处理（不做冗余实验）

- 本任务只需要**一次真正被玩家触发的全量生产采集/发布**及简短的源状态、计数、GM读取验证；不要求战术生效快模拟、反复游戏存档重启、再对19/18字段逐个做安全性开发试验，也不要求模拟一个月。
- 失败时只修复**本次真实失败的阻断点**：定位当前进程、原生来源校准/教练身份、SQLite存储/审计、同批导出、GitHub发布状态或GM来源读取。保留旧latest last-good，不能“回填”新值到旧批次；不做预防性重构或开发单项流水线。
- 若完全成功，Codex只需将`docs/34_BASELINE_CURRENT_STATE.md`、`config/source_catalog.json`状态从`FIRST_PRODUCTION_PENDING`提升到`FIRST_PRODUCTION_CAPTURED_AND_PUBLISHED`（仅当确实上传），必要时修订数据/GM/执行手册状态。记录真实新batch ID、数据更新时间与发布状态（不要把运行时内存指针持久化）。
- 发布后GM和Codex执行模型分别按已有`web_gm/manuals/GM_COACHING_OPERATIONS.md`与`docs/40_COACHING_EXECUTION_RUNBOOK.md`使用，无需另一本专项更新手册。

## 5. 验收结果/结束条件

**开发代码目标本身已经在main，故无需另立新特性任务。** 本工作唯一待验收状态为`FIRST_REAL_FULL_CAPTURE_NOT_YET_RUN`。成功一次玩家触发的完整来源审计、SQLite写入、JSON导出及GitHub上传（若授权）后，网页GM可以基于真实同批教练数据制定下一批战术。

- 非目标：`COACHING_ONLY`、单队/单源跳过更新、不同来源不同时间组合包、专门教练`latest`、自动按战术回执改SQLite、无人触发的后台更新、比赛胜率证明。
- 开发计划由Web GPT DEVELOP撰写；**本轮仅更新需求/基线文档，没有运行数据采集、没有改变游戏内存/数据库内容或发布正式游戏事实**。
