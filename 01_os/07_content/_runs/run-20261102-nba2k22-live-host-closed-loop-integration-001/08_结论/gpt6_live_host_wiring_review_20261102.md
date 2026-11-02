# NBA2K22 Season Host · GPT-6 定向代码复核

日期：2026-11-02。角色：decision_architecture / GPT-6。
固定被审交付 SHA：`6b827b2b7dade3720e3fcc6c9f6d51a58bc14fda`（GitHub HEAD 已核验）。
审核证据：GitHub 交付源码、5 个 Host 测试函数、四轮 Fake 回执、`loop_summary.json`、已有 WorldData `refresh.py` 和 `calendar_sim_orchestrator.py`。本次没有在本机复跑测试、没有连接 NBA2K22 实机，也没有真实 Native Setter 或游戏存档操作。

## 阶段评语

**`OFFLINE_HOST_SCAFFOLD_ACCEPTED; LIVE_HOST_EXECUTION_NOT_READY`**。

保留已开发的单次触发 Host CLI/状态机、WorldData 优化模块选择性集成、Decision Outbox 与离线四轮模拟证据。交付自述 Host 5 tests + WorldData 337 tests 为执行者收据，本审核不冒称独立重跑。

但是 Live Host 现在存在几处影响正确性的接线缺口。**请暂不执行 `season_cycle_cli.py authorize`，也不得告诉 Human “现在输入一句启动指令就能自动采集、决策与安全写游戏”。**

## P0-1 初始化/世界线/采集绑定不真实

- `season_cycle_host.py:initialize_season` 仅当 `reader is not None or pid != "auto"` 时才尝试 `trigger_world_capture(FULL)`。CLI 默认 `--pid auto`，因此正常用户不提供 PID 时**不会做初始 FULL 采集**，而 `self.state.status` 无条件设为 `BASELINE_CAPTURED`，返回 `INITIALIZED_AND_BASELINE_BOUND`，`capture_summary` 可以是 `ALREADY_BOUND`。
- 此方法捕获异常后置 `MOCK_OR_FALLBACK_INIT`，**仍然允许标记已采集**，不是 fail-closed。
- `inspect_worldline` 会在游戏日期早于数据库最后比赛日时创建新的 child DB，但 `CalendarSimOrchestrator.trigger_world_capture` 内调用 `refresh_world`，后者的数据库由 `bound_database(save_directory,binding)` **重新解析原绑定数据库**（`refresh.py:120` 之后），不能由在 Orchestrator 构造器中提供的 `database_path=target_db` 自动改写。于是可能把新世界线采集提交到旧数据库，或者在 child DB 中观测不到新数据。
- 日历日期不是从当前进程准确读取：`initialize_season` 用 `mock_game_date`、`{observed_game_season_year(reader)}-10-25`，失败则 `2021-10-25`，无 reader 还默认 `2021-10-25`。这种推导日期不足以判断真实回档、世界线分叉。
- `_make_context` 目前固定 `season_id="2021-22"`、`phase="REGULAR_SEASON"`、默认 `MyLEAGUE0003` 和合成 `snapshot_ref`，不满足跨赛季准确 identity/freshness。

**最小整改**：正常 CLI 必须 resolve 当前 PID/创建时间和真实存档+游戏日期；已验证的 FULL Refresh 成功/提交/快照证据才能推进 `BASELINE_CAPTURED`；真实数据和子世界线绑定必须经过 `refresh_world` 可验证的一致 DB 路由，旧历史绝不覆盖；任何采集失败不改变成功状态；禁止 mock 日期进入 Live 入口。

## P0-2 Human 下一轮和采集没有真正连通

- `start_cycle` 在 CLI 真实调用时没有传入 `reader`，因此不运行 `inspect_calendar_progress`；也**不调用 `trigger_world_capture`**。它只是在 Outbox 打开 cycle，将用户可选的 `--intents-file` 逐条登记，缺少承诺的“每7游戏日采集、读取新事实、角色输出决策”真实入口。
- `advance_calendar_check` CLI 也未提供 reader：`new_date = mock_advanced_date or curr_date`，即使没有日历变化也直接写入 `NEXT_CAPTURED`，并回 `CALENDAR_ADVANCE_VERIFIED`；没有新比赛检测、没有 WorldData 刷新与 SQL 核验。
- 自己提供 `--mock-date` 的离线四轮测试可以证明状态机跑通，但不能证明日历实机已推进。

**最小整改**：CLI 的非 mock 模式必须调用现有 CalendarSimOrchestrator 的真实 `inspect_calendar_progress` 与 FULL/INCREMENTAL 采集；必须使用实际结果中的日期和 epoch， `SAME_STATE_REPEAT` / `INCOMPLETE_GAME_IN_PROGRESS` 保持原状态。角色候选若仍由 JSON 输入/人工提供，应明示“决策输入待接入”，不得自动声称 GM/Coach/Player 已自主产生建议。

## P0-3 Live Setter 的授权与验证存在绕过

- `season_cycle_cli.py` 的 `seal` 直接调用 `seal_cycle_decisions(cycle_id)`，**没有注入实时 Getter**，于是函数里的 `if getter_func` CAS 检查不执行，却仍可能产生预检成功 digest。默认 `expected_pid=5720` 是过去的测试 PID。
- CLI 的 `authorize` 同样只传 cycle_id+digest，没有提供现场 PID、fresh save/epoch/live scope/Getter-after；`authorize_and_execute` 默认 `expected_pid=5720`，却直接实例化 `BoundedSessionExecutor`（如果 fake_runner None 会进入真实 Runner），真实写入可能使用过期进程身份。
- `authorize_and_execute` 把 `readback_passed` 初始化为 True，`getter_after_func=None` 时**不作任何逐项 readback**；不调用 `validate_batch_execution` 的 Live 严格模式，没有把 readback_failed 作为阻断；照样调用 `record_execution_receipts`，清除 active plan 并将周期推进至 `WAITING_CALENDAR_ADVANCE`。
- `_make_profiles` 是静态测试用户 `gm_user_01/coach_user_01`、球队 ID(1,25,28)、固定 actions/grants，不是来自 Host 的受信角色/赛季权限；必须禁止把本地 JSON 的 `actor_uid` 当成真实身份授权依据。

**最小整改**：默认 `authorize` 在 Live 模式必须拒绝执行，直至 fresh PID+创建时间+存档/世界线+身份/权限+每字段 CAS 检查与具体本轮 Human digest/scope 均通过。真实 Writer 后须读取原始 Native messages、每 chunk 的 plan/digest、Journal、全部意图的独立 Getter-after，并且 **Validator PASS 才能回填 SUCCESS**。读回缺失/失败/UNKNOWN → 保持证据与锁，不清计划、不把周期推进成功；不得重试未知操作。为首批实机只开放经过认证的 `SHOT_TENDENCY`，其他动作保留 NOT_EXECUTED。

## P1（边修时顺手，不另设大型阶段）

- `seal_cycle_decisions` 在 `NO_CHANGE` 分支没有调用 `outbox.seal_cycle`，但自身状态显示已完成计划预检；需要保证 Outbox 状态与 Host 状态一致。
- `SeasonCycleHost.resume` 无论暂停前真实状态为何都恢复为 WAITING_CALENDAR_ADVANCE；应记录并恢复暂停前状态，UNKNOWN_LOCKED 不得无声解锁。
- `state_file.write_text` 未原子替换，冲突或崩溃可导致错误恢复；可沿用现有原子写+状态校验，不新增服务/锁框架。

## 推荐的最小复测门

1. CLI 无 `--pid` 执行 init → 实际解析 PID+fresh game date，且必须产生成功完整 FULL/绑定快照收据；缺游戏/读档失败→不得 `BASELINE_CAPTURED`。
2. 使用恢复旧档且日期倒退→子世界线数据库成功接收新 Source observations，旧原始数据库事实/历史逐项不变。
3. `cycle/advance-check` 真实读取当前日期/完赛并在需要时采集；日期未动或游戏进行中→严禁 `CALENDAR_ADVANCE_VERIFIED`。
4. `seal` 缺 native Getter 或有 CAS mismatch→无法生成可执行 Live digest；动态 PID/epoch，不使用5720常量。
5. `authorize` 无真实 Human scope 授权、无 Getter-after、误填 digest、测试身份/存档漂移、缺/伪造 raw receipt→fail-closed 且 **0 Native Setter**；一旦已尝试动作但 UNKNOWN，绝不再次自动发出。
6. 通过已有100项金标准证据离线回放及负例，再只读实机从正确世界线初始化；Human 后续明确授权小规模 SHOT_TENDENCY 才进行第一次 Live Writer。
7. 跑原 Host 5个测试、REA和 WorldData 定向回归，记录真实命令/退出码，保留四轮 Fake 证据与新一轮 Live 证据的明确区分。

**仅修复 Host 调用与信任边界，优先复用已有代码，不得因这次审核重建 Outbox、REA Setter、Reader 或数据库架构。** 开发可在原任务同分支沿 OS 内部 Loop 整改；审核只看影响重大的逻辑、数值和安全回归。master 保持不变。
