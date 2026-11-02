# REA 批量写入吞吐优化 · 函数级执行合同

**任务 ID**：`NBA2K22-REA-BULK-THROUGHPUT-OPT-20261101-001`
**OS 角色**：`execution`，计划执行模型 Gemini Flash 3.8（按实际运行型号登记）；GPT-6 规划 `decision_architecture`。
**仓库**：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`
**工作分支**：`task/nba2k22-rea-bulk-throughput-optimization-20261101`
**固定基线 SHA**：`25b3748fa7d861d69a7e6d350bb0d36c1eefc17f`，含经 Human 验收的 12 人、2 chunk、真实游戏 SHOT_TENDENCY→0 试点。
**工程范围**：仅改善当前已验证 Player SHOT_TENDENCY 批量修改的会话开销与有效平均时间；不重新研究/替换 Native Setter，不增加 Coach/交易/属性等新动作。

## 一、目的、实测基线、判定指标

Human 当前要求：**先试会话复用等优化，实测能把平均每项修改的时间降低到多少；如果仍不合预期，再讨论并测试第二种批量修改路径**。本任务不自动启动未知的替代写入机制。

固定旧试点原始证据：
- `01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001/07_测试执行/stage2_mutation/execution_result.json`，**12/12 SUCCESS_APPLIED、2 chunk、39.40411 秒**，旧总时间 / 12 = **3.2837 秒/成功修改**。
- `07_测试执行/stage1_noop/execution_result.json`，12/12 No-op，2 chunk，39.52493 秒。两个批次时间近似，但**不直接认定 Native Setter 开销为零**。
- `transport.py:ReaCliTransport.execute` 每个 chunk 单独创建程序文件、PowerShell 子进程、Node + REA CLI、Frida attach、等待观察窗口、脱离及读回证据；`run_live_stage2_mutation.py` 设置 `duration_ms=15000`。两次 15 秒只是预算参数，并非经过逐阶段插桩的“真实等待耗时”。

主要性能指标：
- `T_batch_wall_seconds` 从第一次本次批次相关调用开始到最后一个结果通过校验并完成清理；
- `T_per_successful_setter_wall=T_batch_wall/confirmed_SUCCESS_APPLIED`；另外报 `T_per_planned_intent_wall` 和 `T_per_chunk`；如果分母为0记 null，不能算 NaN/无穷或把 No-op 当 Getter/Setter 成功数；
- `attach_count`、`process_spawn_count`、`script_load_count`、`native_getter_count`、`native_setter_count`、`cleanup_duration`、`game_thread_callback_max_ms`、`unknown_count` 和 `getters_after_verified_count`；
- 性能分段 `plan | journal_claim | compile | launch | attach/load | GUI_wait | game_thread_Native | results_parse | cleanup | independent_readback`；若不同进程时钟不可同步，应测各自 duration 而非混减 absolute timestamp；
- 每组测试标清计时是否包含冷备份、独立 Probe、最终验收 UI。**必须同口径比较原始 39.40411 秒与新结果，不能以排除原有 overhead 人为刷快**。

指导性的目标是尽量明显低于旧 3.28 秒/成功修改，不预设 Human 未给出的达标阈值。所有结果应报告绝对值、减少百分比、置信/重复次数和失败情况；仅允许实测证据支持结论。

## 二、模块函数锚点和实现顺序

源码基目录：`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/`

**优先阅读**：
`transport.py:ReaCliTransport.execute`
`run_native_program.ps1`
`bulk_executor.py:BulkExecutorService.run_with_transport`、`ReaChunkTransportAdapter.execute_chunk`、`BulkFridaScriptCompiler.compile_chunk`、`ExecutionJournal.claim_chunk`、`CrossProcessFileLock`
`runtime/common.js`、`runtime/gui_once.js`
`live_bulk_pilot.py`、`run_live_stage1_noop.py`、`run_live_stage2_mutation.py`、`probe_live_roster.py`。

### S1 · 细分耗时插桩（先测量，确保“不优化错误环节”）

1. 在 `ReaCliTransport.execute()`、`run_with_transport()`、PowerShell 调用和必要的 Node/JS 观察入口插入低开销计时；采用 Python monotonic / JS 或 PowerShell 各自可靠 stopwatch，单独输出分段 duration；无来源字段为 `NOT_MEASURED`。保留用于区分 script launched、script attached、GUI callback entered、first Native call、last Native return、last receipt emitted、cleanup finished 的关键事件，不向游戏公开敏感绝对地址。
2. 先保留完整旧时间基线；对 live 只读 Getter/多 chunk No-op 的测量与 Mock/Node VM 不同级别标注。**不得为了计时重新运行旧 mutation batch 或重复先前 intent_id**。
3. 调查本机**现有** Node/REA CLI 版本、帮助与脚本生命周期，确认：能否一个 attach 执行多个 chunk；可信完成后是否可安全提前退出；CLI 的 `--duration-ms` 是否强制等待、含 attach/cleanup 哪些时间。不得臆造支持参数或擅自修改签名/官方程序。
4. 输出 `baseline_timing_breakdown.json`，至少标明各观测来源以及无法精确拆分的阶段。

### S2 · 实现“单次 attach，多 Chunk”有界会话（本轮首选架构）

1. 建议增加一个`SessionBatchTransport` / `BoundedSessionExecutor` 小组件，负责 **一次 Rea CLI/Frida attach + 一份可执行程序 + 多 Chunk 有序执行**；后端仍调用原有已恢复 Getter/Setter Native bindings；`ReaCliTransport` 原单 chunk API 必须回归。
2. `BulkBatchPlanner.plan` 继续区分 team/action/field family，生成不可变 `plan_digest`、`chunk_digest`。会话可以常驻有限观察窗口，但每个 Chunk 都需独立 Claim、CAS、唯一回执、失败停止；**不能因为“一个会话”而将全部项目算作一次不可区分的大事务**。
3. 最小实现路线可考虑：将多个已编译的 chunk payload 编排到同一程序中，**只附加一次 Frida、只装一个 `gui_once.js` Hook**；使用受控的 Chunk 队列/分段时间预算并按顺序执行。不能简单拼接多份 `common.js/gui_once.js`，也不能在一轮 GUI 回调里无限循环数千 Setter。必须明确 GUI thread 每段运行预算、超时与回执、游戏流畅度/崩溃观察。
4. **Claim-before-Setter 硬约束**：多 Chunk 同一会话模式下，必须在任何可能触发 Native Setter 之前，持久化本次会话内全部可执行 Chunk 的精确 attempt claim，或设计可证明“每 Chunk 在下一段执行前由 Python 持久 Claim 并得到确认”的握手机制。Python 不得在游戏已执行时才事后 claim。已 Claim 但未运行者中断后按 UNKNOWN/NOT_EXECUTED 可证明边界保守分类，禁止自动重放。
5. 独立收据必须含 `batch_id, save_instance_id, plan_digest, chunk_id, chunk_digest, action_id, attempt_id, full intent IDs`，核对全部 Getter-before、目标、Getter-after、未请求字段保持、Native 调用预算及清理状态；发现缺/重/乱序/错误摘要、角色/进程变化、任意 UNKNOWN 时一律 STOP。
6. 保留跨进程互斥锁及之前的 Human 授权范围；**这次授权是吞吐优化和有界同类 Player SHOT_TENDENCY 验证，不自动授权任意上万次新写入**。旧 `execute-authorized` 的权限、CAS、Journaling 不得为了性能而变弱。
7. 对于不能在 GUI 线程安全分段执行的情形：允许有界多消息/多次调度到同一 Hook 的实现，先在 Node VM 模拟；若 CLI 不支持多 Chunk 可靠结果/受控退出，不强行混用不完整的协议，保留一个固定“替代方案候选”作为下一期决策，而不是引入未经实测 Native 直接内存写。

### S3 · 离线和实机对照实验

按增量运行，并从最小规模试验开始：
- **L0 离线**：1、2、4、8 个 chunk 的纯 Fake/Node VM 计时及运行语义；跨 chunk 的 Setter 次数、回执守恒、异常停止与持久 Claim；失败注入包括 `missing_chunk_receipt`、`fault_after_setter`、`process_lost`、`game_thread_timeout`、`duplicate_chunk`、`claim_IO_error`、`unknown_replay`。记录失败集合变化与测试命令。
- **L1 真实只读**：通过当前批准的现场游戏，对 12、24 项（若 live roster 确认足额）进行多 chunk Getter/No-op，必须零 Setter，测量原按块 attach 与单 attach 两种方式；允许跨 2 支球队但不得猜测 roster UID。
- **L2 有界真实写入性能验证**：仅在冷备份有效、Human 先前批准的同类字段与存档实际绑定、L0/L1 及安全门通过时，选取 **12 项**真实 `SHOT_TENDENCY`（与已授权并人工验收的试点规模一致），一个新 batch/nonce 和实际 live Getter CAS、至少 2 chunk，与旧 39.40411 秒作同口径对照。若 Human 已手动恢复则读取恢复后的**真实**值，绝不直接复用旧 `80→0` 列表或旧 intent_id。一次尝试，遇 UNKNOWN 不重试；不得自行扩大到24/100/10000实机 Setter。
- 不要求为这次用户已经批准的有界试验再次启动 Human 授权工作流；需要另一个存档、其他字段、超过上述规模或真正未知权限时再请求新裁决。
- 对比结果必须同时提供：旧单 chunk attach 两块 39.40411s；新单 attach 多 chunk 12项总耗时；正常完成回执数、平均每项实际修改毫秒、session次数；No-op 和写入两类分别报告。
- 如果明显降耗但尚未达到 Human 后续要求，**只提出第二条技术路线的方案与成本/风险/预计开销模型**，不自动执行另一种写入方法，也不自动扩大范围。Human 决定是否继续。

## 三、性能优化保留的不变量（不可裁剪）

- 每项 `CAS expected_before`，真实 Getter-before 与 Setter-after/Get-after；156B 相邻未修改字段保持、属性缓存标志协议与已有 REA 合同一致。
- 旧 Journal/UNKNOWN/跨进程锁、保存身份、EXE SHA/PID + start epoch、main-thread 安全执行、Native 调用预算、失败即停止仍然生效。
- 不修改存档文件、不自动推进游戏日历、不自动恢复/覆盖 Human 冷备份（Human 自行恢复）；不得在 GitHub 推送真实存档内容。
- 不创建新的“累计统计计算”，不更改球员能力或教练设置，不把 Mock 性能当真实速度。
- 保持原始 Runner 证据、每个 Chunk 的 provenance 和追加历史。旧的 12/12 验收记录不可覆盖。

## 四、内部开发 Loop、停止与产物

按 Core 内部 Loop：当前最高价值假设 → 有界实现 → 测试/故障注入 → 记录实测失败与耗时 → 修正 → checkpoint → 下一增量。模型必须如实登记，不把没有新证据的重复 PASS 算有效循环；不制造过多独立审核窗口，真实写入的承重权限边界如有改变则集中审核。

**建议最小可改范围**：`bulk_executor.py`、`transport.py`、`run_native_program.ps1`（若需且证据证明） 、`live_bulk_pilot.py`、有限新增 `bounded_session_transport.py`、`tests/test_bulk_executor.py` 及独立测试、当前 Run 目录。不修改 Core、WorldData、registry/Native bindings、其他动作。若需新 Native 入口，停止并提出 Human 架构方案。

**交付**：`performance_baseline.json`、`transport_timing_trace.json`、`session_batch_test_receipts.json`、`benchmark_comparison.json`、`loop_iterations.jsonl` 与程序化核对 `loop_summary.json`、`completion_pointer.md`、最终完整 commit SHA。显式分级 `OFFLINE_VERIFIED` / `LIVE_NOOP_VERIFIED` / `LIVE_WRITE_VERIFIED` / `NOT_RUN`。主线集成不作硬性禁止：Human 已授权**仅在分支隔离实质增加开发复杂度且差异和回归可控时**采用正规 PR/审核方式进行有界集成；本任务当前无需合并 master，因为基线与 master 差异巨大。
