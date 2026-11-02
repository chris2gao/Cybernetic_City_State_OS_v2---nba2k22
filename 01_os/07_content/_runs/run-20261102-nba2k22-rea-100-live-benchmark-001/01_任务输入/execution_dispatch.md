# REA · 100 条实机 Native 修改耗时基准测试（先测量，不开展性能重构）

**任务 ID**：`NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001`
**OS 岗位**：`execution`；计划由 Gemini 实施，**实际模型必须如实登记**。GPT-6 负责 `decision_architecture` 和后续证据审核。
**工作分支**：`task/nba2k22-rea-100-live-benchmark-20261102`
**固定技术起点**：`f68b2703a7b7be691b92c3f816480e2fa6f9a449`（包括被 Human 认可的 12 项单 Session 性能优化及 GPT 定向评估）。
**Human 当前新裁决**：
- **明确批准进行一次 100 条数据的真实批量修改，先取得实际耗时，再决定下一次开发任务。**
- 批次回执完整性同意以**简单自动化脚本**实现。
- 并发与 Journal 也优先简单自动化；若会明显增加工程复杂度，**本轮不开发该重构**，只施加最小运行时独占/失败停止条件。
- 主线程分段可后续尝试，但**不得在本次基准前擅自重构**。
- WorldData 采集性能优化**暂停执行**，先完成 REA 吞吐基准。
- Human 将自行手动恢复存档；本任务不自动恢复、反向写入、推进日历或保存覆盖。
- 当前批准**仅限这一个受控真实 100 项 Player SHOT_TENDENCY 写入批次**以及必要只读预检、真实 No-op/Getter 和独立读回，不代表允许任意字段或无限重试。

## 一、唯一目标与固定对照

**问题**：在当前的 `SessionCompiler + SessionBatchTransport + BoundedSessionExecutor` 实现下，真实修改 **100 项**需要多少完整墙钟时间？每条成功修改平均摊销多少时间？单次 Frida Attach、按球队分 Chunk 的伸缩实际表现如何？

已有固定实机基准（不可覆盖）：
1. 旧每 Chunk Attach：12 SUCCESS、2 Chunk、39.40411s，总耗时/成功数=3.283676s。
2. 新单 Session：12 SUCCESS、2 Chunk、7.23892s，总耗时/成功数=0.60324s。
3. 同方案另一次 12 SUCCESS、2 Chunk、7.76659s；真实 No-op 12/12、7.60537s。
4. 前期失败回执（u8 未定义引发 UNKNOWN、后续 CAS mismatch/守恒失败）继续保留；这些历史说明必须正确处理异常和总数。

**严格约束**：`100` 是实际发生 Setter 的目标条数，不能以 100 个计划但只有 70 个应用成功宣称 100 项测试通过。若失败，按真实 `planned=100 / attempted / confirmed_success / failed / UNKNOWN / not_executed` 如实报告；不要为了凑 100 在失败后重放，也不能另选替代对象继续补写。不得通过多次重复单次 12 项来凑出“100 项”；目标是 **单次受控有界 Session、至少多个 Chunk、100 个不同的 intent**。

## 二、保持冻结工程，允许的最小自动化

源码基目录：`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/`

必读：
- `bounded_session_transport.py` 中 `SessionCompiler.compile_session`、`SessionBatchTransport.execute_session`、`BoundedSessionExecutor.execute_batch` 和 `_build_summary`；
- `bulk_executor.py` 的 `BulkBatchHeader, BulkIntentItem, BulkBatchPlanner, ExecutionJournal, CrossProcessFileLock`；
- `probe_live_roster.py`（当前**只硬编码 Team 28、Team 1 和 PID 10404**；不能直接复用其目标列表）；
- `run_final_live_benchmark.py`（旧脚本**硬编码 12 名球员和 source_snapshot_ref**，不得直接复跑）；
- `transport.py, run_native_program.ps1, runtime/common.js, runtime/gui_once.js`；
- 前次真实 `benchmark_comparison.json`、每轮 `execution_result.json`、Journal、REA 原始 evidence。

允许新增：
- `benchmark_100_live_once.py`：薄调用层，**仅在现场只读观察结果形成新计划后**调用旧 BoundedSessionExecutor。不要对旧目标、旧 PID 或旧 `MyLEAGUE0003` 假定为事实。
- `validate_100_receipts.py`：独立的**只读验证脚本**，不执行 Setter，不解锁 UNKNOWN；读取 manifest、精确 batch/chunk digest、原始 REA messages、receipts.jsonl、独立只读 readback，并生成明确 PASS / FAIL / UNKNOWN 与恒等式。
- `tests/test_benchmark_100_live_once.py`：小型离线输入/输出、回执篡改、失败状态测试；必要时给旧 probe 薄封装增加队伍列表参数，**默认仍只读**。
- 本次 Run 下的数据、回执、Loop 与完成报告。

**不允许**以本任务为由修改 `bounded_session_transport.py` 的 Native 执行原理、核心 Journal、安全互斥设计、原始 Native bindings、原 GamePlan、Core OS 或 WorldData；如发现旧引擎的关键缺陷阻碍本次安全测试，应 STOP_WITH_EVIDENCE 并把它作为**测试后开发任务的依据**，不能一边改引擎一边把修改后的速度冒充当前基线。

### 自动化核验脚本必须做什么

在启动真实修改**之前**读取并校验：
- 编译脚本和任务 SHA、Process EXE SHA、实际 PID+创建时间、存档/赛季/roster 标识和本地冷备份 SHA；脚本只能读取这些值，不得假定旧 PID 10404 或历史姓名/数值仍成立。
- 当前没有其他 REA 修改进程或已挂起的相同存档/对象 UNKNOWN Claim；用现有 `CrossProcessFileLock` 保护本次脚本的会话独占，不额外引入并发调度服务；**如果独占不能确认就停止**。
- 100 个唯一的 `intent_id`、100 个唯一 `(team_id, player_id, SHOT_TENDENCY)`，都在 fresh active roster 内；原值与 Getter 精确相同、值在合法范围内、每项恰有一次非零合法改动；所有 action_id 均为 `PLAYER_PATCH_TENDENCIES`。
- 分块计划中的 100 项与本次 manifest 及预算完全一致；`max_chunk_size` 不超过现有旧实现的限制，不能为了凑大规模绕过每块 Native 调用上限；是否跨多个球队由实际 roster 候选决定。

真实修改后**仅只读核对**：
- 每个 `chunk-execution-result` 必含 `batch_id/save_instance_id/plan_digest/chunk_id/chunk_digest/action_id` 且与执行计划**精确一致**；不得因响应缺字段、重复 chunk、未知 chunk、重复 intent、未请求 intent、Getter-after 缺失而返回 PASS。
- 完整集合 `expected_intents == receipt_intents`，100 个 intent 每个**恰好一条本次终态**，单个真实 SUCCESS 必须 `getter_before == expected_before`、`getter_after == target`、`unaltered_fields_check is True`；其它结果禁止改写成功。
- `planned = success + noop + blocked + unknown + not_executed + reused`；由于本次目标是 100 次真实 Setter，**合格目标必须 100 SUCCESS、0 NOOP/UNKNOWN/REUSED/NOT_EXECUTED**；遇到 UNKNOWN 或缺收据不能用其他脚本重试。
- 对 100 个目标进行**独立新 REA 只读会话的 Getter-after** 复核，保留现场人名/球员ID/球队/数值/时间和 hash（不把存档本体上传 GitHub）；验证失败如实 FAIL，不能自动修复/恢复。
- 输出 `validation_result.json`，包含错误代码和准确证据定位；**验证脚本事后 PASS 不能倒推证明执行期间完全不存在并发竞争**，对没有足够证据的性质标记 NOT_PROVEN。

自动化处理的原则是“尽量减少人工逐条核验”，**不是删减必要正确性检查**。

## 三、100 条测试怎么选择与执行

### L0 — 离线静态及模拟预检（不改原引擎）

1. 固定工作树 SHA、校验脚本/测试脚本；用新独立 Run 目录，严禁清理/修改此前试验 Journal。
2. 用 Fake/Node VM 对 100 项、至少多个 Chunk 做一次模拟，检查输出是否缺 Chunk/Intent，及单次 GUI 回调总执行的估计时间；对消息缺字段、重复、CAS 失败、超时、后缀停止、Claim 损坏做最小负例。
3. 检查基于当前源代码的唯一 Hook 与最大 `maximum_game_calls`。目前单次 `executeAction` 可能在**同一次 GUI 回调循环全部 Chunk**，本轮只允许**观察和设置现有硬预算**，不得进行未验证的“逐帧改造”。若预估会超出当前游戏主线程的已知可接受时间/既有合约预算，报告并停止实机写入；不要依赖“1000次只需几百毫秒”的预测。

### L1 — 真实只读选样 + 一次 100 项 No-op

1. 对当前游戏/存档进行实时只读扫描，从合法 active-roster 球员中选出**100 名不同球员**，每人只选一个字段 `SHOT_TENDENCY`；可跨多支球队，不能以重复同一球员的多次修改凑数。
2. 优先选当前 getter 位于 1..99 的球员，目标值采用确定性 `target=before+1`；若不足100名，可合法使用 before=0→1 或 before=100→99（均为1点变化）。**不得使用每人统一目标0、旧硬编码的12人目标或没有实时读回的期望旧值**。如果没有100个可信候选，停止而不是偷偷减少任务数。
3. 记录 cold backup 的本地存在、校验和与独立可恢复性；用户负责后续手动恢复，不运行自动 restore 或覆盖保存。
4. 使用这100个新对象构造单独的只读 No-op batch（`expected_before=value`），同一单 Session 多 Chunk，要求 **100/100 NOOP、0 Setter、无 UNKNOWN**，且真实主线程/CLR没有意外异常；计时与正式 Setter 批次分开。
5. 根据 No-op 后**再次 fresh Getter**确定写入 CAS；进程/存档/roster 变化则停止。

### L2 — 一次真实 100 条批量修改

1. 将上述100个经读回证实的唯一 Player intents 固定为一个新 batch、一次 nonce、一次 session；精确记录全部队伍ID、球员ID、旧值与目标值。选择现有允许的 `max_chunk_size`，确保多球队、多 chunk 能保守停止。
2. **仅运行一次**：`execute_batch` 负责 Claim-before-Setter，采用现有互斥并在启动前确认仅有本次执行器；**本任务不声称已经证明跨进程全过程无竞争**。如果现场存在并发 REA 执行者、锁获取失败或 Claim 状态冲突，停止，不为了本次跑分修改核心锁设计。完成所有 Chunk 的真实 Setter 前后确认。出现任何 UNKNOWN、CAS mismatch、对象漂移、超时、读回不一致、runner 报错、游戏无响应，即停止而不是重放/分组补齐。
3. 完成后保存一次新会话的100个真实 Getter、每个 Chunk 的 Runner 原始 messages/收据、执行会话清理状态。
4. **不执行100项还原的第二批次**，Human 会手动恢复冷备份。对当前世界线的临时修改不进行模拟赛程或保存覆盖。
5. 若最终100/100成功并完成独立读回，标记 `LIVE_100_ITEM_MEASUREMENT_CONFIRMED`；若少于100，按实际 `LIVE_PARTIAL_OR_BLOCKED` 处理，不重复启动以补齐。

### L3 — 计算与呈现

提供下列**绝对测量值**，不能只显示“提速多少倍”：
- `full_benchmark_wall_seconds`：**只包含本次100项 Setter 批次**的开始规划执行至清理/回执落盘完整墙钟；另报 `preflight_seconds`、`noop_seconds`、`independent_readback_seconds`，不能将 No-op 或人工备份耗时混到 Setter 批次。
- `transport_wall_seconds`、`frida_attach_count`、`chunk_count`、`active_team_count`、`actual_setter_count`、`confirmed_success_count`、`unknown_count`、`cleanup_status`；
- `full_benchmark_wall_seconds / 100`：全部100条成功时的每项墙钟均摊；`wall / confirmed_success`（若部分失败，明确注明分母和偏差）；`native_GUI_callback_ms` 可准确测则填，无法可靠测则写 `NOT_MEASURED`；
- 以旧12项`7.23892s`与当前100项实测对照，但不得声称这是同规模的严谨A/B；固定成本导致均摊下降是可能结果，不使用线性外推代替实际结果；
- 对万级修改只可提供附带假设的模型，不能声明万级实测已经完成。

## 四、执行证据与停止

本任务为**性能基准测试，不是新一轮吞吐优化开发**；Gemini 不得在本次过程中引入常驻 IPC、动态 DLL、绕过原生 Setter、改变 game-thread Hook 机制，也不要为了追逐某个理论性能目标反复修补/循环测试。

需输出：
`01_任务输入/execution_dispatch.md`；
`06_执行/live_candidate_inventory.json`（100条独立对象身份与本次 fresh Getter）；
`06_执行/loop_iterations.jsonl`（仅有真实新证据时记轮）；
`07_测试执行/preflight.json`；
`07_测试执行/noop_100_execution_result.json`；
`07_测试执行/mutation_100_execution_result.json`；
`07_测试执行/validation_result.json`；
`07_测试执行/independent_readback.json`；
`08_结论/benchmark_100_result.md`；
`08_结论/completion_pointer.md`；
完整 Git SHA 与实际执行模型。
允许另存原始 REA Runner / scripts/日志在当前 Run 子目录，内容需脱敏且可重算。

**所有 100 项修改需要明确的游戏内回执依据，不能仅凭汇总字符串声称通过。** 若合同任一必需条件无法满足，记录原因，保留原始成功/失败数据，不隐瞒、不自动重试。

**本任务不要求另一轮 Human 批准**：Human 已明确授权本次100项实际测试。但这不是对其他动作、其他存档、超过100项、新 Native 写入机制或无限次重复的授权。

WorldData 采集性能优化在此期间保持 `DEFERRED_BY_HUMAN`，不修改该分支，不运行同一个游戏的并行采集。

**master 集成**：Human 只在减少复杂度时条件授权；此基准用独立分支更易复算，不直接修改 NBA master。
