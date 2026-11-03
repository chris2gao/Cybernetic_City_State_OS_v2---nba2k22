# NBA2K22 VAE Stage02 下一任务 · 原生高级统计发现与 WorldData 统一采集增强

## 0. 任务身份

- 任务 ID：`NBA2K22-VAE-NATIVE-STATS-WORLDDATA-LOOP-20261101-001`
- OS 角色：`execution`，执行模型：**Gemini**（具体 Gemini 型号、版本及使用工具以真实运行回执为准）
- 规划岗位：`OS_PUBLIC_DEVELOPMENT_PLANNER / decision_architecture`
- 正式仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`
- 唯一工程分支：`task/nba2k22-vae-native-advanced-stats-worlddata-loop-20261101`
- **精确开发父提交**：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`（WorldData v24 既有工程候选）
- 原 NBA master：`45cc45cae0550ddcda192a2179ea48509b27f6ee`
- 本任务 Run：`01_os/07_content/_runs/run-20261101-nba2k22-vae-native-stats-worlddata-loop-001/`

**基线选择理由**：WorldData v24 的实际采集器代码不在 NBA master。本分支刻意从其已有 20 Reader 的冻结候选 HEAD 建立，以复用原架构和真实测试资产，不得称作已并入 master、已获全域独立审核。Stage02 GPT 机制需求在另一分支，只能按精确提交读取为证据输入，**禁止直接合并其整棵代码树**。

## 1. 本任务为什么开始

Human 目标是“边开发边玩”，最终建立：
**游戏原生数据 → VAE 模型诊断倾向/教练/攻防设置 → REA 原生设置修改与读回 → 用户正常比赛 → 新原生比赛数据 → 机制效果检验 → 迭代改进**。

本任务位于其中的**数据发现与采集准备阶段**。不实施 VAE 生产调参、不控制比赛、不改变存档。

上一任务 Stage02 M1–M5 的 204 字段目录、68节点/50关系边、38项统计需求、3组S0/S1/S2实验合同，已在独立审核 `8ed0baff7fd7cf6439c0a49e158dea5b1838d1e3` 获得 `PASS_REQUIREMENT_BASELINE_WITH_RESEARCH_GAPS`，关闭六项定向整改。**它通过的是语义需求基线，不是所有统计原生可读、Gameplay因果证明，也不是当前MC存档验收。**

依照 Human 新原则：
**游戏已经计算好的统计数据优先直接获取。当前Reader没有 ≠ 游戏没有。游戏原生计算值已确认存在时，不另造同名公式。** 只有可靠记录有界来源调查仍确认缺失、且有单独派生需求时，才提出不同名称的估算代理，不在此项目自动改写原生意义。

## 2. 必读来源及双线固定证据

执行前从 Core OS 当前正式 master 初始化公共工作纪律，读取此 Run 的 `run.yml`、`task_packet.json`、`verification_plan.json`，核对 NBA 分支精确 HEAD 及当前工作区状态。

- Stage02 候选 SHA：`c812042e087f4c7000d27ac42d3839741039c188`
  - `01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-mechanism-metric-evidence-001/06_执行/metric_native_first_requirements.json`
  - `.../06_执行/data_source_gap_matrix.json`
  - `.../06_执行/mechanism_metric_links.json`
  - `.../06_执行/pilot_experiment_contracts.json`
- 审核 SHA：`8ed0baff7fd7cf6439c0a49e158dea5b1838d1e3`
  - `01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-m1m5-independent-review-001/08_结论/remediation_rereview_20261101.md`
  - `.../07_测试执行/remediation_rereview_matrix_20261101.json`
- WorldData v24 源提交：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`
  - `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/BASELINE_HANDOFF.md`
  - `README.md`, `refresh.py`, `live_reader.py`, `period_stats_reader.py`, `player_detail_reader.py`, `field_dictionary.json`, `schema_model.py`, `tests/`
  - `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment37/field-maturity.json`
  - 同目录 `source-coverage.json`, `verification-report.json`
- 机制资料：`094f1aa641f93dec2277707ad9dbf5bdb0341247` 的 `docs/game_mechanics/guides/K01_K02_GAME_STATS.md`，仅作发现入口。

WorldData v24 是 **100 STRICT表、1,775列、20族Reader** 的冻结常规赛候选。保留真实来源和研究fixture区别，现有累计统计由游戏计算，本任务不重构累计计算。

## 3. 一个长期任务的五段内部 Loop

**L0 · 重建来源地图。** 以 M3 38 个 `metric_id` 为不变输入，逐项查已存在 Reader、原生来源证明、UI候选、原始数据结构、数据粒度、同名是否派生。先建立 `native_stats_discovery_inventory.json`，全部38条必须有查找/适用/UNKNOWN 状态。注意上一审核发现：v24 7项 team_game_boxes 列是全NULL，旧 PLAYER_PTS 是 `2*FGM+3PM+FTM` 派生，四项球员Box为研究fixture数据，不能复用为当前游戏Native认证。

**L1 · 原生高级统计定位。** 优先调查 NBA2K22 PC 的球员选项卡 Game Log / Advanced / Per Game / Per 36（实际页面名称以此构建为准），球队高级统计及比赛明细。寻找 UI 中具体标签、数据结构、Getter/内存访问、原始字节、类型、显示精度/舍入、存档与赛季归属。先验证**字段确实由游戏维护并计算**，再区分纯UI格式化/数据库累计/战术事件临时内存。不得从NBA官网“Tracking”分类推定2K22游戏也有同类事件。

**L2 · 打通一条最小真实数据链路。** 先选择 **一项逐场球员基础统计和一项真正的原生高阶统计**（例如USG、TS、eFG、PER36中的实际可证者），在已确认的同一存档、同一球员、同一比赛/赛季粒度下只读验证；不要求未证字段硬凑。原生结果与可见UI或其它独立只读位置交叉比较，不强行要求外部公式数值相等。保存实际数据取证和负例（DNP/未完赛/不同赛季/重复索引/当前模式与Game Log历史槽位）。只取有界公开球员信息，避免读取隐藏Potential或不必要的私有内存。

**L3 · 增强现有统一采集架构。** 在 `world_data_prototype` 的已有 Reader/Source Unit/Codec、`refresh-world`、单档SQLite历史、field dictionary、按时点查询/导出上做最小可运行扩展。已有 Reader 能表达的则复用/扩展，无法表达时才说明新 Reader family 的必要性。新增字段必须绑定真实来源、主键(player/team/game/season/phase)、模式(3D/Calendar Sim等)、类型/单位、精度、来源成熟度、采集时间、完整性/新鲜度和缺失语义。不得把所有高阶数据强填进一次Box结构；确需新表或迁移时使用**拷贝升级、历史逐列保留、旧快照哈希不变**，不得原位修改冻结v24证据库。自动采集只指后续明确触发统一 `refresh-world` 时把新增 Reader 一起跑，并不授权安装后台任务/定时器。

**L4 · 集中回归和VAE就绪。** 确认新字段从实际只读源码到 typed observation、SQLite staging、新增字段查询、统一采集命令可重复；跑 WorldData 现有单测、SQL smoke、真实来源负例、重启PID和版本防旧址；建立 `metric38_coverage_and_readiness.json`，对38项逐项给出 `REAL_NATIVE_READABLE / READER_IMPLEMENTED_NOT_LIVE_VERIFIED / UI_CANDIDATE / FIXTURE_ONLY / DERIVED_ONLY / NO_NATIVE_SOURCE_FOUND / UNKNOWN` 等**不越级状态**。对M5三个实验明确列出可以直接使用的真实指标、Reader路径、剩余关键缺口以及3D和日历SIM分别可比的条件。

每段都可多次迭代，不能只交文字总结。**一轮Loop = 有界假说/任务 → 实际读取/实现 → 测试 → 发现与修正 → 精确SHA+证据检查点 → 下一增量**。选择最高价值且能验证的下一项；没有固定轮数。完成一个Reader或一个测试绿灯不意味着整个需求已实现；一个字段无来源也不阻塞其它独立部分。

## 4. 必须保留的技术边界

- 游戏和原始存档：**只读**。不改变球员倾向、教练设置、战术、轮换、日期/赛季和游戏资源；不得通过Setter修改任何数值。
- 进程/逆向：静态PE和授权测试环境的有界只读内存分析可以使用；每次运行核对 EXE、PID+创建时间、版本/模块和真实存档绑定，不能沿用旧地址。若读取需要新权限、调用副作用未知Getter、注入或Patch，先保留阻塞证据，不自行实施。
- 数据库：允许在**新的独立staging副本**上验证现有框架扩展，保留旧真实库、旧采集单元及append-only历史。不能重写历史观察或未经证据跨MC与MyLEAGUE合并身份。
- 来源资格：`UI label` / `native bytes` / `decode` / `Reader actual live` / `SQLite values` / `VAE candidate` 六层证据分别记录，不能只凭列存在就升为Native成功。
- 已有工程：**不建第二套采集器、不重写D1–D5、不做新的生产VAE系统。** 新发现要接入已有 `refresh-world`，不能只生成孤立CSV/JSON宣称统一采集已完成。
- 写入边界：仅 `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**` 和本任务Run。Core、NBA master、Stage02审核Run及WorldData历史Run只能读，不能改。无force、merge或history rewrite。

## 5. 验收与明确缺口

验收至少区分以下层次：

- `RESEARCH_DISCOVERED`：具体游戏Native来源线索 + 可复现静态证据；
- `GAME_NATIVE_VERIFIED`：真实本构建/存档原生值与身份/粒度核实；
- `READER_IMPLEMENTED`：新Reader代码存在、单测与边界用例成功；
- `LIVE_CAPTURE_VERIFIED`：真实游戏只读捕获实际完成；
- `UNIFIED_REFRESH_VERIFIED`：统一采集、持久化、查询/导出和来源/历史核实；
- `PILOT_DATA_READY`：M5实验所需指标已有可比较同粒度数据。

高优先级硬目标是**至少一项逐场基础球员数据加一项真实游戏计算的高阶指标**打通原生只读→统一采集→查询闭环（前提是测试环境和Native来源实际存在）。找不到、读不到或尚需权限时不伪造PASS；保留局部实证、准确缺口、下一次验证条件并继续其它授权研究。

本任务不是批准VAE调参、比赛自动控制或生产部署。审核排期为VAE系列集中审核；若新Reader/API在后续自动调参系统成为承重接口，必须在该边界之前审核相关关键部分；Core七阶段的正式完成门不受开发Loop改变。

## 6. 交付文件

- `02_证据/native_stats_discovery_inventory.json` —— 38字段来源/证据/未知清单
- `02_证据/ui_native_reader_binding_dossier.md` —— 游戏页签/字段语义/原生身份可复现证据
- `06_执行/metric38_coverage_and_readiness.json` —— 采集覆盖与三组Pilot准备度
- `06_执行/reader_integration_log.md` —— 每次内部Loop的实际迭代、代码SHA、测试和问题
- `07_测试执行/loop_verification_and_regression_report.json` —— 最终执行结果、日志与旧v24回归
- `08_结论/completion_pointer.md` —— 最终Head、达到与未达到的目标、后续研发入口
- 实际最小 Reader/Codec/Refresh/Query/Tests 改动位于原有 `world_data_prototype/**`。

整个执行以 `01_任务输入/verification_plan.json` 的 V01–V12 为核验门。不提供实机数值时明确 `NOT_RUN`，绝不把Fixture绿灯变成真实Native验收。

## 7. 立即开始

1. OS及Run初始化、核对当前分支及来源SHA。
2. 读取M3/M4的38项指标需求和审查报告，读取WorldData20族Reader。
3. 输出一个短恢复回执，不等待逐字段批准。
4. **从真实原生数据发现开始**：选择优先的Player Card/Game Log/Advanced样本，验证定位假说。
5. 每发现一个可用字段，**尽早把可验证的Reader最小纵向切片集成现有采集体系**，跑测试并保存证据，再进行下一项。
6. 按已授权开发Loop持续推进；需要额外游戏/存档操作权限、超过任务路径或承重语义裁决时才停止并交回Human。
7. 完成候选远端提交与完成指针；**不自动合并master，不逐个Reader派独立审核**。

**本任务的最终价值，是让VAE后续只需调用现有统一采集，就能获得真实游戏计算好的可验证比赛数据。**
