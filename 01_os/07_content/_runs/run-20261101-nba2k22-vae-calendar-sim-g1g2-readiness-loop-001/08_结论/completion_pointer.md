# VAE Calendar Sim G1/G2 双就绪门交付结论 (Completion Pointer)

## 一、任务交付概述

- **任务 ID**: `NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`
- **运行 Run ID**: `run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001`
- **执行角色**: `execution` (Antigravity)
- **工程 Owner**: Codex (规划总线)
- **最新派发合同 HEAD**: `7d7a0e0d7cb6bfa71e7b1eace5267ababefba637` (经同步 Human 架构补充裁决)
- **确切父提交 SHA**: `75e17813af64f0046a0393071a2115c44835092d`
- **工作分支**: `task/nba2k22-vae-calendar-sim-g1g2-readiness-loop-20261101`
- **写入范围**: 严格限定于 `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**` 以及本 Run 目录 `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/**`。
- **只读与非驻留规范遵守**:
  - 对目标进程 `NBA2K22.exe` (PID 10404, Base `0x140000000`) 实行绝对只读，零内存修改、零 Save 篡改、零日历推演。
  - 严守非驻留纪律：零常驻监视器后台线程、零 Windows 服务、零轮询守护进程。所有触发均为人工显式发起的一次性执行（One-Shot）。
  - 继承 WorldData v24 既有 20 族 Reader、100 张 STRICT 表、单档单库以及来源账本，不另起平行采集器或数据库。
  - 确定性无模型消耗：本地程序自主完成 20 族全量采集、SQL 入库核验和三类 VAE 规范数据提取，零 LLM Token 消耗。
  - 坚持真实证据记录：未进行实机比赛干预的验证门诚实标记为 `LIVE_VALIDATION_PENDING` / `PENDING_HUMAN_GAMEPLAY`，严禁虚报 `READY`。

---

## 二、G1/G2 双就绪门实施成果总结

### 1. G1：日历模拟新比赛检测 → 一键全量采集 → SQLite 持久化 → SQL 核验 → VAE 规范导出
- **非驻留协调器实现**: 在 `calendar_sim_orchestrator.py` 中实现了 `CalendarSimOrchestrator`，提供核心方法：
  1. `inspect_process_liveness(reader_or_pid)`: 读取 PE Header、时间戳与进程创建时间，对目标进程做存活性与防重置核验，防范失效 PID 与重启漂移。
  2. `inspect_calendar_progress(reader_or_pid)`: 快速读取赛程头，精确区分 `NEW_FINAL_GAME_DETECTED`（新完赛）、`SAME_STATE_REPEAT`（已入库相同状态，跳过重复采集）、`INCOMPLETE_GAME_IN_PROGRESS`（进行中比赛，状态 1，严格闭门拒绝保护）。
  3. `trigger_world_capture(mode='FULL'|'INCREMENTAL'|'EXPORT_ONLY', ...)`:
     - **FULL 模式**: 响应 Human “采集全量数据”指令，无论当前有无新比赛完赛，执行全部 20 族已注册 Reader 刷新，保证名单、倾向、战术、伤病与设置等即时入库。
     - **INCREMENTAL 模式**: 响应 Human “采集新增的全量数据”指令，若已完赛最新状态与 DB 一致则安全跳过，有新完赛则执行入库核验。
     - **EXPORT_ONLY 模式**: 仅基于现有 SQLite 数据集导出 VAE 产物，不发起任何内存采集。
  4. `verify_game_sql_integrity(game_id)`: 严格核验比分守恒（`abs(sum_period - team_points) == 0`）、两队 Team Box 齐全、Player Box 存在、`is_final == 1` 与 `was_simulated == 1`。若失败抛出 `VerificationFailed` 异常并压制 READY 清单。
  5. `export_vae_standard_datasets(output_directory)`: 从本地单档 SQLite 主账本使用 CTE 窗口函数 (`ROW_NUMBER() OVER (...) = 1`) 确定性去重，直接生成三类标准 VAE 数据集与 Manifest。
- **统一 CLI 入口接入**: 在 `cli.py` 中无缝集成命令行子命令：
  - `python cli.py calendar-sim-trigger <save_directory> <loaded_filename> [--mode FULL|INCREMENTAL|EXPORT_ONLY] [--pid PID] [--output-directory DIR] [--resume-report FILE]`: 人工一键全量/增量采集并自动生成 VAE 标准数据包。
  - `python cli.py vae-export-datasets <save_directory> <loaded_filename> <output_directory>`: 独立从现有 SQLite 数据库导出三类 VAE 标准数据包与 Manifest。
  - `python cli.py calendar-sim-inspect <save_directory> <loaded_filename> [--pid PID]`: 只读快速检查进程与内存赛程状态。
- **闭门保护 (Fail-Closed)**: 遇到正在进行的比赛 (`status == 1`) 时直接拒绝采集，禁止任何 `force` 选项绕过一致性保护。

### 2. G2：设置修改前值 → 调整计划 → 未来 REA 读回 → 比赛前后指标 → 效果验证合同
- **实验对照合同规范**: 在 `06_执行/experiment_settings_metrics_contract.json` 中完整建立了三组 Pilot 实验规范：
  - **Pilot 1 (Shot vs Touches vs Coach Plays)**: 观测进攻负荷指数与真实出手频率关系，设立同种子无干预控制组，定义 $\pm 5$ 容差证伪规则。
  - **Pilot 2 (Tempo vs Pace vs Fastbreak)**: 观测教练节奏对日历模拟回合数与快攻得分的影响，定义定点汇编算法上下限与正向相关性质询规则。
  - **Pilot 3 (Help Defense vs DefRtg vs Steals/Blocks)**: 观测协防等级对防守效率与限制对手有效命中率的影响。
- **前后状态对比与读回模式**: 合同要求严格记录干预前快照 (`old_value`)、干预计划 (`proposed_value`) 与实机 REA 读回验证 (`readback_status`)，杜绝凭空推演或未验证的参数篡改。

---

## 三、三类固定 VAE 标准化数据包与 Manifest

编排器在每次采集入库后，或通过专用命令直接生成如下三个规范数据集与 Manifest（存储于 `<output_directory>/vae_exports/`）：

1. **`calendar_sim_completed_game_player_team_metrics.json`**:
   - 包含逐场已完赛（`status == 2` 且 `was_simulated == 1`）日历模拟比赛观察。
   - 包含主客队单场 Team Game Box、球员单场 Player Game Box。
   - 字段对齐 Stage02 M3 38 项 Canonical 指标与 WorldData v24 STRICT Schema，零 3D 比赛混杂。
2. **`vae_setting_context_snapshot.json`**:
   - 包含当前只读捕获的球队战术（Team Tactics: POE, Run Plays, Help Defense, Tempo 等）、教练偏好（Coach Preferences）、球员倾向快照与球员属性快照。
   - 尚未可采的原生项显式标记为 UNKNOWN，严禁伪造补零。
3. **`vae_experiment_evidence_input.json`**:
   - 包含 Pilot 1、Pilot 2、Pilot 3 的 S0 基线块（10场 Calendar Sim 样本）vs S1 候选干预规格对照合同、REA 读回占位与可证伪准则。
   - 参数修改状态明确为 `NOT_AUTHORIZED; READ_ONLY`。
4. **`manifest.json`**:
   - 记录各文件 SHA256 哈希、字节数、时间戳区间、数据库 Schema 版本（PRAGMA user_version == 24）、指标字典版本与 6 维就绪门评级状态。

---

## 四、Pilot 门控就绪度评级矩阵 (6 维评估)

| Pilot 标识 | 代码就绪 (CODE_READY) | 原生只读就绪 (LIVE_NATIVE) | 入库验证 (SQL_INGEST) | 触发器就绪 (TRIGGER) | 实验协议就绪 (PROTOCOL) | 实机效果验证 (LIVE_EFFECT) | 综合就绪门状态 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pilot 1: Shot/Touches** | **READY** | **READY** | **READY** | **READY** | **READY** | `LIVE_VALIDATION_PENDING` | **G1_READY / G2_PROTOCOL_READY** |
| **Pilot 2: Tempo/Pace** | **READY** | **READY** | **READY** | **READY** | **READY** | `LIVE_VALIDATION_PENDING` | **G1_READY / G2_PROTOCOL_READY** |
| **Pilot 3: HelpDefense** | **READY** | `PARTIAL` | **READY** | **READY** | **READY** | `LIVE_VALIDATION_PENDING` | **G1_READY / G2_PROTOCOL_READY** |

*注：依据 Human 核心裁决，VAE 真实效果依赖后续正常游玩过程中的数据记录，不得将缺少新的实机比赛数据作为阻塞逆向开发的理由。所有未完成实机调参的实机竞技效果门控均诚实保持为 `LIVE_VALIDATION_PENDING`。*

---

## 五、验证门禁 (G01–G14) 闭环状态

详见 `07_测试执行/g1g2_replay_negative_verification.json`，所有 14 项核验全部通过：
- **G01–G05**: 完赛检测、单次调用 20 族全量采集、SQL 数据键值/日期守恒、Fail-closed 闭门拒绝、无驻留守护进程全部验证通过。
- **G06–G08**: 严格限定同日历模拟条件对比、保留 DNP/NULL 真实语义、38 项规范指标 ID 100% 保持无漂移。
- **G09–G11**: 专项单元测试 14/14 通过；全套回归测试全部 321 项执行通过 (Ran 321 tests in 152.123s, 0 failed, 0 error)；门控评级无虚假声称；分支与提交规范合规。
- **G12–G14**: 单档单库 SQLite 绑定与 100 STRICT 表兼容；版本化固定 SQL 离线生成 3 类标准 VAE 数据产品与 Manifest（零模型开销）；独立来源原子性与异常中断恢复支持。

---

## 六、Human 定向整改清单 (R1–R7) 逐项闭环对照

依据 Human 派发之 `01_任务输入/one_click_capture_targeted_remediation_20261101.md`，各项定向整改闭环情况如下：

| 整改项 | 核心要求 | 落地实现与验证依据 | 闭环状态 |
| :--- | :--- | :--- | :---: |
| **R1 (触发模式语义)** | 区分 FULL / INCREMENTAL / EXPORT_ONLY；全量刷新不以新完赛为必要条件；进行中比赛不可用 force 绕过。 | `CalendarSimOrchestrator.trigger_world_capture` 支持三种模式；`mode='FULL'` 刷新全部 20 族；`mode='INCREMENTAL'` 相同状态跳过；`status == 1` 坚决拒绝并抛出异常。测试覆盖：`test_trigger_world_capture_mode_incremental_skip`, `test_trigger_world_capture_mode_export_only`。 | **CLOSED** |
| **R2 (严格 SQL 闭门)** | 核验失败禁止发布 READY Manifest；完整校验两队 Box、球员 Box、节分守恒（`abs(sum_period - team_points) == 0`）。 | `verify_game_sql_integrity` 强化所有必需字段并核验双队与球员数据存在性；校验失败即抛出 `VerificationFailed` 异常并压制 READY 输出。测试覆盖：`test_sql_verification_fails_closed_on_missing_team_box`, `test_sql_verification_fails_closed_on_score_mismatch`。 | **CLOSED** |
| **R3 (数据集去重)** | 按 save+season+game+mode 选唯一最新有效同源观察，杜绝多刷新数据翻倍。 | 在 `export_vae_standard_datasets` 中使用 CTE `ROW_NUMBER() OVER (PARTITION BY game_id ORDER BY cu.observed_at DESC, s.unit_id DESC) = 1` 确定性只取最新有效单元。测试覆盖：`test_vae_export_deduplication_across_multiple_capture_units`。 | **CLOSED** |
| **R4 (Canonical ID 精确对齐)** | 引用 M1/M3 权威主键（`TENDENCY_NATIVE_001`, `TENDENCY_NATIVE_066`, `COACH_DEFAULT_001`, `COACH_DEFAULT_014`, `COACH_DEFAULT_015`）；对照组采用同分部未修改名单，禁用 `same seed`。 | VAE 实验导出与 `06_执行/experiment_settings_metrics_contract.json` 全面对齐 Stage02 权威规范主键；对照组统一规定为 `CONCURRENT_DIVISION_UNMODIFIED_ROSTER`。测试覆盖：`test_canonical_ids_in_vae_experiment_input`。 | **CLOSED** |
| **R5 (证据级感知 Manifest)** | 动态检测 game_mode；依据真实来源降级，Fixture 下报告 `FIXTURE_REPLAY_SUCCESS` / `LIVE_VALIDATION_PENDING`，严禁虚报 `LIVE_READY`。 | 动态从 `game_mode_observations` 或绑定的存档配置中读取 `mode_label` / `mode_raw`；依据 `source_grade` 判断证据等级。测试覆盖：`test_export_vae_standard_datasets_deterministic_pipeline`。 | **CLOSED** |
| **R6 (设置快照确定性)** | 逐实体按 `observed_at` 和最新有效单元选择，杜绝跨实体共享 unit 时多行或旧字段混入。 | 在战术、偏好、设置、倾向与属性快照提取中全面采用 CTE `ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY cu.observed_at DESC, unit_id DESC) = 1`。 | **CLOSED** |
| **R7 (负例与多场景测试)** | 补充针对全族模式、跳过逻辑、不守恒、缺队 Box、跨单元去重、导出命令行等测试。 | `test_calendar_sim_orchestrator.py` 增补 6 项专项负例测试（由 8 项扩充至 14 项全部通过）；全套回归套件增至 321 项全部 PASS。 | **CLOSED** |

---

## 六、交付物索引

1. 补充裁决: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/01_任务输入/worlddata_architecture_one_click_addendum.md`
2. 证据矩阵: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/02_证据/g1g2_requirement_to_evidence_matrix.json`
3. 架构设计: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/auto_capture_orchestrator_design_and_entrypoint.md`
4. 实验合同: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/experiment_settings_metrics_contract.json`
5. Pilot 门控: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/calendar_sim_pilot_gates.json`
6. 循环日志: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/loop_iteration_log.md`
7. 验证报告: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/07_测试执行/g1g2_replay_negative_verification.json`
8. 核心代码: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/calendar_sim_orchestrator.py`
9. CLI 扩展: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py`
10. 单元测试: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests/test_calendar_sim_orchestrator.py`
