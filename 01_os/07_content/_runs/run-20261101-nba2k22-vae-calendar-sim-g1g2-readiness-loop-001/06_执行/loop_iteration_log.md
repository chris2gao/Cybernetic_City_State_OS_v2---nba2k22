# VAE Calendar Sim G1/G2 双就绪门开发循环日志 (Loop Iteration Log)

**任务 ID**: `NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`  
**执行角色**: `execution` (Antigravity)  
**工程 Owner**: Codex (规划总线)  
**工作分支**: `task/nba2k22-vae-calendar-sim-g1g2-readiness-loop-20261101`  
**派发基线 HEAD**: `436d557e4152512c02a7adbeb7ed5966ab1353fb`  
**确切父提交 SHA**: `75e17813af64f0046a0393071a2115c44835092d`

---

## 一、迭代概览与循环执行记录

| 阶段 / 轮次 | 核心任务与涉及文件 | 执行操作与技术决策 | 验证与结果 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **A0: 环境初始化与基线校验** | `execution_dispatch.md`<br>`verification_plan.json`<br>`task_packet.json` | 确认工作分支；确认实机进程 `NBA2K22.exe` (PID 10404, Base `0x140000000`) 正常运行；确认只读约束。 | 验证派发 HEAD 与父提交 SHA；确认只读目标进程，禁止写内存、改设置、推日历。 | `COMPLETED` |
| **A1: G1/G2 证据矩阵与适用性映射** | `02_证据/g1g2_requirement_to_evidence_matrix.json` | 梳理已有代码证据 vs 实机运行态差距；建立 6 维评估矩阵；映射 38 项 Canonical 指标在日历模拟下的有效性与缺失。 | 建立代码与实机证据台账，明确日历模拟排他性标准，排除 3D 比赛混淆。 | `COMPLETED` |
| **A2: 自动采集协调器与 CLI 开发** | `calendar_sim_orchestrator.py`<br>`cli.py`<br>`06_执行/auto_capture_orchestrator_design_and_entrypoint.md` | 实现非驻留、显式触发的 `CalendarSimOrchestrator`；支持进程保活核验、新终场比赛识别、同一状态跳过、进行中比赛拒绝闭门保护，以及采集后 SQL 入库即时核验；扩展 `cli.py`。 | 架构设计文档与 entrypoint 规格完整，绝不启动常驻后台监视守护线程。 | `COMPLETED` |
| **A3: G2 实验设置与指标对照合同** | `06_执行/experiment_settings_metrics_contract.json`<br>`06_执行/calendar_sim_pilot_gates.json` | 为 Pilot 1 (投篮/触球)、Pilot 2 (节奏/快攻)、Pilot 3 (协防/防守评级) 制定严谨的 S0 基线 vs S1 干预对照合同、同种子对照组、REA 读回模式及证伪准则。 | 三组 Pilot 的 6 维门控状态显式定义；诚实标记未执行比赛的项为 `LIVE_VALIDATION_PENDING`。 | `COMPLETED` |
| **A4: 循环测试验证与缺陷修复** | `tests/test_calendar_sim_orchestrator.py`<br>`tests/` 全套回归 | 针对协调器编写 6 项单元测试。修复 `collect_schedule` 数据结构中 `manifest['entries']` 的取值路径以及比赛进行中状态位在 `flags` (offset 56, bit 11) 的设置方式。运行全套回归。 | 专项测试 6/6 通过；全套回归套件运行完成，0 失败 0 错误。 | `COMPLETED` |
| **A5: 交付物整理与检查点固定** | `07_测试执行/g1g2_replay_negative_verification.json`<br>`08_结论/completion_pointer.md`<br>`run.yml` | 汇总 G01–G11 复现与负向测试报告，更新运行状态至 `completed`，生成完成指针，提交并推送到远端 GitHub。 | 全部 11 项 G 系列门禁核验通过，分支成功推送。 | `COMPLETED` |

---

## 二、关键技术问题根因诊断与修复记录 (Internal Loop Debugging)

### 1. `collect_schedule(reader, read_final_boxes=False)` 字段路径修复
- **现象**: 在 `CalendarSimOrchestrator.inspect_calendar_progress` 初始实现中，调用 `collect_schedule` 后尝试通过 `schedule_info.get('entries', [])` 获取赛程项，导致始终返回空列表，进而判定为 `NO_FINAL_GAMES_IN_MEMORY`。
- **根因**: `schedule_reader.py` 的返回字典结构为 `{'header': ..., 'games': ..., 'manifest': {'entries': entries, ...}}`，`entries` 实际嵌套在 `manifest` 字典内部。
- **修复**: 将读取逻辑修正为 `entries = schedule_info.get('manifest', {}).get('entries', [])`。

### 2. 比赛状态位（In-Progress）二进制编码对齐
- **现象**: 单元测试 `MidGameMemory` 试图模拟进行中比赛时，通过 `struct.pack_into('<I', g, 8, 1)` 修改了偏移 8 的 `game_id`，导致未能将状态修改为 `status == 1`。
- **根因**: 在 2K22 原生 `SEASON_GAME` 60 字节结构中，状态并非独立整数字段，而是位于偏移 56 的 `flags` 字中的第 11-12 位：`status = (flags >> 11) & 0x03`。
- **修复**: 在测试中通过位运算精确更新状态位：
  ```python
  flags = struct.unpack_from('<I', g, 56)[0]
  flags = (flags & ~(0x03 << 11)) | (1 << 11)
  struct.pack_into('<I', g, 56, flags)
  ```
  使协调器能够准确捕获 `INCOMPLETE_GAME_IN_PROGRESS` 并执行 Fail-Closed 拒绝。

---

## 三、非驻留与安全原则保证

1. **绝对只读**: 对目标进程 `NBA2K22.exe` (PID 10404) 的访问严格通过只读内存句柄，未注入线程，未调用任何内存修改或 Save 写操作。
2. **非驻留架构**: 本轮开发的 `CalendarSimOrchestrator` 与 CLI 子命令 `calendar-sim-inspect`、`calendar-sim-trigger` 为按需单次调用的非驻留工具。没有任何后台线程、Windows 服务、`while True` 轮询循环或未授权监视器在系统中驻留。
3. **闭门保护 (Fail-Closed)**: 遇到未完成比赛、进程退出、时间戳或校验和漂移等异常情况，采集流程立即中止并返回拒绝代码，严禁将不完整状态写入正式世界数据库。
