# NBA2K22 · VAE 原生统计数据可信度修正与 S0 基线准备

**Task**：`NBA2K22-VAE-NATIVE-METRIC-HARDENING-S0-20261101-001`

**角色**：`execution`；**工程 Owner 建议 Codex**（Gemini 只按具体 Native 难题由 Human 顺序转交）。

**仓库**：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`

**分支**：`task/nba2k22-vae-native-metric-hardening-s0-20261101`

**精确父提交**：`3fdc1b3ae3870785fb8a070a9225382b01c529d4`（Gemini WorldData 增强候选，不是 NBA master）。

**写范围**：`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**` 及 `01_os/07_content/_runs/run-20261101-nba2k22-vae-native-metric-hardening-s0-001/`；其他仓库分支和历史运行证据只读。

## A. 原则与意义

Gemini 上轮取得有价值的 PE、Slot 01、Slot 24、Slot 28、SEASON_GAME 和 GameScore 候选结构，但代码/测试、证据状态和上一轮审核通过的 38 项统计契约出现实质差异。

本任务不是再开一次冗长审核，而是**在下一开发 Loop 中修复直接影响下一步 VAE 比赛指标判读的差异，并准备 S0 只读基线**。禁止把“无编译错误”“307 项旧测试PASS”“函数已实现”“在内存看见值”直接解释为“已在统一采集里保存和可对照”。

Human 核心原则：**游戏原生计算值优先；统一 WorldData 原生 Reader/刷新/历史/查询；无原生证据时标未知，派生指标单独命名；开发阶段循环验证，系列集中独立审核。**

## B. 证据输入（按精确 SHA）

- 原 Stage02 M3 的**唯一正典 38 个指标 ID**：
  `c812042e087f4c7000d27ac42d3839741039c188:01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-mechanism-metric-evidence-001/06_执行/metric_native_first_requirements.json`
- 原 Stage02 M4/M5 及审核：
  `8ed0baff7fd7cf6439c0a49e158dea5b1838d1e3:01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-m1m5-independent-review-001/08_结论/remediation_rereview_20261101.md`；其定向整改6/6关闭，只认证需求基线。
- Gemini 交付：
  `3fdc1b3ae3870785fb8a070a9225382b01c529d4` 的上次 Run `run-20261101-nba2k22-vae-native-stats-worlddata-loop-001`；重点 `ui_native_reader_binding_dossier.md`, `metric38_coverage_and_readiness.json`, `loop_verification_and_regression_report.json`。
- WorldData v24 历史基线：
  `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4` 的 `BASELINE_HANDOFF.md` 和来源/字段成熟度。

**请不要重新读取204份外部档案、重复旧Stage02整轮审核或从 master 重搭空白新采集器。**

## C. 开发内部 Loop 的五项工作

### H1 · 修复 38 项ID偏移与指标语义

我方对比已经核定：旧M3的38个ID与Gemini新38个ID只有**14个完全匹配，24个原ID缺失、另增加24个非原ID**。

因此先做唯一规范ID映射。保留M3全部38个 `metric_id` 的原名和粒度，Gemini额外指标可以进入 `discovered_native_metric_aliases` 或新增研究清单，不能替换正式需求或挪用其计数。每个字段的源标签、Native对象、读入实例、旧fixture、派生比例和VAE可用性分别定级；禁止把31个混杂来源全部标为`REAL_NATIVE_READABLE`。

### H2 · 真正闭合 GameScore 原生采集

Gemini 新增 `family_codec.extract_player_advanced_metrics(raw)`，能够解析1264字节 PLAYERDATA 中的近五场GameScore/排名候选。然而当前新增查询 `query.player_game_log` **仍直接从Box重新计算GameScore**，且此次增量未证明该原生值通过 `refresh-world → 持久化 → 查询` 写入事实库。

优先通过已授权的公开安全字节区间读取必要的 `PLAYERDATA` 槽位（原位保留raw、浮点、日期、分钟、字段身份、来源批次），复用现有Reader及 typed Source Unit 接入 `refresh-world`。不得因便捷而读取整个1264字节对象：WorldData原规则物理排除隐藏Potential字节区间，事后过滤不等价于禁止取得。

若不能在当前游戏测试环境确认直接Native采集，则**保留游戏结构发现，GameScore查询明确标为`BOX_DERIVED`**，原生GameScore绑定状态写`NOT_INTEGRATED`而不是`FULLY_READY`，并说明下次所需的真实原始证据。

### H3 · 先修真实数值、快照与查询逻辑

1. 两份报告同一恩比德样本相互矛盾：汇报稿的22分8/17等统计代入其所列GameScore公式得到**17.50**，不能得到21.10；详细dossier给的27分10/23样本才得到21.10。必须用固定游戏、球员、球队、比赛、原始Box bytes/hash、Native float原值和同一计算器重新核对。没有证据直接标`UNREPRODUCED`，保留冲突旧文件作为历史，不覆盖。
2. 原生与估计必须分清：没有永久存储 `USG/TS/eFG` **不等于已证实游戏UI没有动态计算源**；未找到也不等于证明其在整个游戏引擎中不存在。派生的 `TS%`、`eFG%`、`Per36` 仅作明确标记的可选代理，先继续原生Getter/UI调查。
3. **不得把 `FGA+0.44*FTA+TOV+0.33*AST`当成真实 Touches 次数或已证明等价的触球代理**；若保留指数须改成不同、明确的实验名称，不可映射`MET_TOUCHES_NATIVE`且不可用作自动调参的触球证明。
4. 修复 `player_game_log`对重复采集单元的重复出场、非终场/不完整值、`NULL→0`，并沿用WorldData已有“同一游戏单个成功单元”与as-of规则。修复赛季累积只按 `total_id DESC`取值造成阶段/球队/时间来源混淆，以及 `team_advanced_metrics` 中单场均值没有按当前赛季/采集单元限定的问题。
5. `team_game_boxes`从所有 player entry 加总和默认 `240+25*OT` 可能在缺员/不完整来源或自定义节长时失真。先用游戏直接维护的Header/Slot数值，聚合字段需要具备全部有效球员、实际节长与加时的合法前提；不满足时保留缺失，不能用非NULL填值证明准确。检查两队/节分/原始Header/Box分数和对手关键字段守恒。

### H4 · 只读最小纵向证据链

将至少一个**当前有源且真实可采集**的球员逐场指标与一个真实游戏计算的高级指标尝试贯通：

`Bounded Native Reader → Decoder → Source Unit → Existing refresh-world → New staging SQLite → Query → Same-unit independent readback`

保留玩家与比赛身份、游戏版本、存档绑定、日期/赛季、3D与Calendar SIM分别标记、UI/Getter和ReadProcessMemory的来源等级。运行原307项回归测试及新增值域、跨批次、非终场、受保护内存、迁移/SQLite约束负例；不要用Fixture单测通过代替实际Native读回。

**当前进程/存档未必还是Gemini取证时的PID 10404**。仅在明确授权的只读测试游戏环境可用时重新定位进程、根、存档。无可访问实例时正常完成可执行的代码修复和真实证据缺口报告，不能伪造Live PASS，也不要求Human为了修复文档临时推进游戏。

### H5 · 为下一阶段建立 S0 数据基线（不执行干预）

按M5已有三组Pilot分类建立只读指标准备度：
- **Shot + Touches + Coach Run Plays/POE/Freelance**：出手、分钟、球权代理、真实Touches若有、Coach现值、模式与球队/球员身份；
- **Tempo + POE + Rotation**：真实或候选原生回合/节奏、球员分钟、比赛时长、Sim Quarter与Normalize、替补轮换；
- **HelpDefense + Defense POE**：对手FGA/三分/禁区得分、协防事件若有、教练防守现值、对手进攻结构。

每组注明`S0_READY` / `S0_PARTIAL` / `S0_NOT_READY`，具体真实来源及仍缺内容。**不要在本任务做任何 S1 REA Setter、游戏设置写入、比赛操作、自动调参、生产部署。** 实验开始需要独立Human授权。

## D. 验证、文件、收尾

必交：
- `02_证据/critical_finding_reconciliation.md` — 八项有重大影响的原始发现及修复/未证情况；
- `06_执行/accepted38_metric_coverage.json` — 正典ID逐项和额外发现隔离；
- `06_执行/native_capture_provenance_matrix.json` — 字段级证据轴与可比较的数据粒度；
- `06_执行/pilot_s0_data_readiness.json` — 三组Pilot的只读真实可用程度；
- `06_执行/loop_increment_log.md` — 每轮实际修改、输入、测试、异常和下一轮；
- `07_测试执行/reproducible_hardening_checks.json` — 真实测试回执；
- `08_结论/completion_pointer.md` — 远端SHA、与父提交diff、可用成果、未解决缺口、后续S1边界。

代码仅在 `world_data_prototype/**` 改动，不修改冻结的旧 v24数据库、旧Run、Core 或NBA master。按 `01_任务输入/verification_plan.json` 的Q01-Q11执行可复验检查。

**审核节奏**：开发期间采用 `evidence_driven_iteration`，没有固定轮次，局部失败自行修复，不逐字段开启独立审核；完成候选先并入VAE系列审核排期。在下一步把指标变成自动游戏写入决策的**承重数据契约**之前，必须对相应关键子集完成有效确认。

**停止条件**：已解决所有授权范围内且可用现有证据修复的关键问题，剩余真实来源缺口已分级；或者出现权限/来源/存档前提不足的真正停止边界。不得无新证据无限重复。

本次任务结束后的下一工作应是 **Human批准的第一组VAE S1/S2实际比赛验证**，而不是再次建立一套数据库。
