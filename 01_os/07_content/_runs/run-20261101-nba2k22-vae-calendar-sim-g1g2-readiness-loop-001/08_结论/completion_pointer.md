# VAE Calendar Sim G1/G2 双就绪门交付结论 (Completion Pointer)

## 一、任务交付概述

- **任务 ID**: `NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`
- **运行 Run ID**: `run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001`
- **执行角色**: `execution` (Antigravity)
- **工程 Owner**: Codex (规划总线)
- **派发基线 HEAD**: `436d557e4152512c02a7adbeb7ed5966ab1353fb`
- **确切父提交 SHA**: `75e17813af64f0046a0393071a2115c44835092d`
- **工作分支**: `task/nba2k22-vae-calendar-sim-g1g2-readiness-loop-20261101`
- **写入范围**: 严格限定于 `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**` 以及本 Run 目录 `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/**`。
- **只读与非驻留规范遵守**:
  - 对目标进程 `NBA2K22.exe` (PID 10404, Base `0x140000000`) 实行绝对只读，零内存修改、零 Save 篡改、零日历推演。
  - 严守非驻留纪律：零常驻监视器后台线程、零 Windows 服务、零轮询守护进程。所有触发均为显式、选择性触发 (Opt-in)。
  - 坚持真实证据记录：未进行实机比赛干预的验证门诚实标记为 `LIVE_VALIDATION_PENDING` / `PENDING_HUMAN_GAMEPLAY`，严禁虚报 `READY`。

---

## 二、G1/G2 双就绪门实施成果总结

### 1. G1：日历模拟新比赛检测 → 自动触发统一采集 → SQLite 持久化 → SQL 验证
- **非驻留协调器实现**: 在 `calendar_sim_orchestrator.py` 中实现了 `CalendarSimOrchestrator`，提供三个核心方法：
  1. `inspect_process_liveness(reader_or_pid)`: 读取 PE Header、时间戳与进程创建时间，对目标进程做存活性与防重置核验，防范失效 PID 与重启漂移。
  2. `inspect_calendar_progress(reader_or_pid)`: 快速读取赛程头，精确区分 `NEW_FINAL_GAME_DETECTED`（新完赛）、`SAME_STATE_REPEAT`（已入库相同状态，跳过重复采集）、`INCOMPLETE_GAME_IN_PROGRESS`（进行中比赛，状态 1，闭门拒绝保护）。
  3. `trigger_capture_if_new_game(...)`: 选择性触发 WorldData 采集并直接进行 SQLite 事务持久化，严防重复写入。
  4. `verify_game_sql_integrity(game_id)`: 采集完成后自动执行针对该比赛的 SQL 读取核验（包含 Game 表、Observations 表、单节比分、球队数据与球员数据完整性）。
- **统一 CLI 入口接入**: 在 `cli.py` 中无缝集成两项命令行子命令：
  - `python cli.py calendar-sim-inspect <save_directory> <loaded_filename> [--pid PID]`
  - `python cli.py calendar-sim-trigger <save_directory> <loaded_filename> [--pid PID] [--output-directory DIR] [--force]`
- **闭门保护 (Fail-Closed)**: 遇到正在进行的比赛 (`status == 1`) 时直接拒绝采集，保护数据库免受截断数据污染。

### 2. G2：设置修改前值 → 调整计划 → 未来 REA 读回 → 比赛前后指标 → 效果验证合同
- **实验对照合同规范**: 在 `06_执行/experiment_settings_metrics_contract.json` 中完整建立了三组 Pilot 实验规范：
  - **Pilot 1 (Shot vs Touches vs Coach Plays)**: 观测进攻负荷指数与真实出手频率关系，设立同种子无干预控制组，定义 $\pm 5$ 容差证伪规则。
  - **Pilot 2 (Tempo vs Pace vs Fastbreak)**: 观测教练节奏对日历模拟回合数与快攻得分的影响，定义定点汇编算法上下限与正向相关性质询规则。
  - **Pilot 3 (Help Defense vs DefRtg vs Steals/Blocks)**: 观测协防等级对防守效率与限制对手有效命中率的影响。
- **前后状态对比与读回模式**: 合同要求严格记录干预前快照 (`old_value`)、干预计划 (`proposed_value`) 与实机 REA 读回验证 (`readback_status`)，杜绝凭空推演或未验证的参数篡改。

---

## 三、Pilot 门控就绪度评级矩阵 (6 维评估)

| Pilot 标识 | 代码就绪 (CODE_READY) | 原生只读就绪 (LIVE_NATIVE) | 入库验证 (SQL_INGEST) | 触发器就绪 (TRIGGER) | 实验协议就绪 (PROTOCOL) | 实机效果验证 (LIVE_EFFECT) | 综合就绪门状态 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pilot 1: Shot/Touches** | **READY** | **READY** | **READY** | **READY** | **READY** | `LIVE_VALIDATION_PENDING` | **G1_READY / G2_PROTOCOL_READY** |
| **Pilot 2: Tempo/Pace** | **READY** | **READY** | **READY** | **READY** | **READY** | `LIVE_VALIDATION_PENDING` | **G1_READY / G2_PROTOCOL_READY** |
| **Pilot 3: HelpDefense** | **READY** | `PARTIAL` | **READY** | **READY** | **READY** | `LIVE_VALIDATION_PENDING` | **G1_READY / G2_PROTOCOL_READY** |

*注：依据 Human 核心裁决，VAE 真实效果依赖后续正常游玩过程中的数据记录，不得将缺少新的实机比赛数据作为阻塞逆向开发的理由。所有未完成实机调参的实机竞技效果门控均诚实保持为 `LIVE_VALIDATION_PENDING`。*

---

## 四、验证门禁 (G01–G11) 闭环状态

详见 `07_测试执行/g1g2_replay_negative_verification.json`，所有 11 项核验全部通过：
- **G01–G05**: 完赛检测、状态幂等防重复、SQL 数据键值/日期守恒、Fail-closed 闭门拒绝、无驻留守护进程全部验证通过。
- **G06–G08**: 严格限定同日历模拟条件对比、保留 DNP/NULL 真实语义、38 项规范指标 ID 100% 保持无漂移。
- **G09–G11**: 专项单元测试 6/6 通过；全套回归测试全部执行通过；门控评级无虚假声称；分支与提交规范合规。

---

## 五、交付物索引

1. 证据矩阵: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/02_证据/g1g2_requirement_to_evidence_matrix.json`
2. 架构设计: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/auto_capture_orchestrator_design_and_entrypoint.md`
3. 实验合同: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/experiment_settings_metrics_contract.json`
4. Pilot 门控: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/calendar_sim_pilot_gates.json`
5. 循环日志: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/loop_iteration_log.md`
6. 验证报告: `01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/07_测试执行/g1g2_replay_negative_verification.json`
7. 核心代码: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/calendar_sim_orchestrator.py`
8. CLI 扩展: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py`
9. 单元测试: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests/test_calendar_sim_orchestrator.py`
