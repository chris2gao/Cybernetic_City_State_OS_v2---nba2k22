# NBA2K22 · Human 主控赛季闭环 Host 集成任务合同

**任务 ID**：`NBA2K22-LIVE-HOST-CLOSED-LOOP-INTEGRATION-20261102-001`
**OS 岗位**：`execution`；建议 Codex 负责代码集成，Gemini 后续在 Human 参与下做现场只读/有限已批准 Native 测试；GPT-6 `decision_architecture` 规划和重大问题审核。
**工作分支**：`task/nba2k22-live-host-closed-loop-integration-20261102`
**Host 集成基线**：`6f3a04fd62368aca261a9f0179e081ffee7be6fb`（含 Decision Outbox、REA 100 项实机验证及审核）。
**WorldData 优化基线**：`a231708df8255a9f2ccf1087c736325a3f606afb`（优化代码）以及定向验收记录 `341e9f9395649cf44e93a40093bd4789be47310a`。
**Human 最新裁决**：可在本人参与下进行游戏日历模拟、整赛季多轮调整和数据库/决策/执行闭环验证；已恢复旧存档，亦允许另开新档；Human 通过明确的提示词决定每轮何时执行。首选每 **7 个游戏日** 一轮、先 4 轮试点，常规赛与关键事件约 **20–40 次采集/赛季**；需要先设计并交付标准操作命令。

## 0. 任务定义与禁止范围

本任务是把现有 `WorldData → Role Decision → Decision Outbox → REA → Receipt → Calendar Progress → WorldData` 接成单一 **非后台、Human 触发** 的 Host 工作流。**不重建数据库、决策引擎、Native Getter/Setter、Outbox、OS 工作流或游戏日历模拟器。**

- Calendar Sim 目前的 `calendar_sim_orchestrator.py` 提供比赛完成检测、按命令采集、SQL 核验及数据导出，**不负责使游戏日期向前推进**。真实游戏日历推进默认由 Human 在游戏界面进行；不要臆造已拥有模拟日历的 Native API。若将来开发原生 Calendar Advance，须另行规划与实测授权。
- 此次用户已允许进行**整赛季的日历模拟测试**，但不表示可不经验证地执行交易、签约、球员属性/教练设置等所有 Native 写入。当前可作为实际写入示范的成熟批量动作是 Player `SHOT_TENDENCY`；Coach、交易等只在证明相应已授权且具备独立实机验收时逐项开放。未支持的意图留 `NOT_EXECUTED`，绝不能伪成功。
- 真实修改必须依赖当前 Host/Human 的本次 `cycle_id + plan_digest + action-scope` 确认，不得借用已消耗的“100项实机测试”临时授权。
- 新旧存档不得混淆：恢复旧档可能使游戏日历倒退但 `save_id` 相同；Host 必须识别新的**worldline/session instance**、fresh game epoch，并使用新绑定数据库/派生观测链或正式隔离策略，防止把之前未来日期的历史观测误认当前事实。新建档同样独立初始化。绝不通过删除旧历史掩盖时间倒退。
- 任何全量采集读取仍只读 NBA2K22 进程；不擅自保存/覆盖游戏存档、恢复冷备份、修改真人存档或写 production WorldData 历史。真实运转如需写 WorldData 历史，必须写到**该世界线对应的正式绑定数据库**，不可当成临时 A/B 隔离库；而此任务的试点使用可核验、独立的测试数据库。
- 大规模一季可能真实运行多轮；不得在未经 Human 一轮轮触发情况下启动持续后台代理、cron 或自动日历循环。

## 1. 已有代码入口（先读再开发）

`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/`：
- `refresh.py:refresh_world`：20个注册来源串行采集、各 source atomic transaction、checkpoint/binding/epoch；`families=None` 默认全来源，annual family 按年跳过。不要把独立 Source 的结果说成同一时刻全局事务。
- `calendar_sim_orchestrator.py:CalendarSimOrchestrator.inspect_calendar_progress, trigger_world_capture`：模式 `FULL, INCREMENTAL, EXPORT_ONLY`。现有 INCREMENTAL 会在没有新完赛比赛时跳过（除 force），虽然其内部仍可能刷新大量家族，**不是仅抓变化字段的精细 Delta Reader**；场内发生 Setter 但没有新比赛时，采用 fresh Getter/明确允许的强制采集，不静默跳过。
- `cadence.py`：年度来源的 `ANNUAL_ALREADY_REFRESHED` 策略。
- `live_reader.py`、`process_session.py`：只读进程绑定、当前时点 / epoch。
- `engine.py`、`player_detail_reader.py`、`player_skill_reader.py`：需有限接入最新已验优化的批量入库、合并读取和**archive_ranges** 重新投影。目标明确：保留原 192B player-detail、210B player-skill artifact 以及 Potential 受限字节完全隔离。

`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/`：
- `decision_outbox.py:DecisionOutbox`：open/add/supersede/inspect/seal/record_execution_receipts/get_outcome_summary。
- `decision_outbox_cli.py` 当前 `LOCAL_OPERATOR_TEST_MODE` 仅可信人工/测试入口，生产 `Host` 应以实际受信调用者身份与 grants 注入，模型自己的 JSON 不能宣称授权。
- `role_batches.py:ActionIntent, BatchContext, RoleActionBatch, ExecutionAggregator`；`role_capabilities.py` 当前动作与角色权限；`decision_batch_bridge.py:DecisionBatchBridge.bridge_batch/map_receipts_to_outbox`。
- `bulk_executor.py, bounded_session_transport.py, validate_batch_execution.py`：当前安全 Native 批量执行及严格结果对账。将 Raw Native evidence + Journal + 独立真实 readback 全部绑定之后，才允许以可信 Host 身份一次性回填 Outbox。`validate_batch_execution` 部分 readback 可选、raw 内部回执按 ID 处理，**Live Host 模式必须额外强制 full readback 与 per-item identity/values**；使用脚本自动执行，避免人工逐项核验。
- 新增 Host 是**薄协调器**，不是另一套执行引擎；以少数独立脚本/CLI 子命令实现。

## 2. 用户可控的操作协议

固定指令语义详见本 Run 的 `01_任务输入/human_trigger_playbook.md`。所有操作必须提供回执、下一步和当前状态。

状态建议：
`UNBOUND → SESSION_BOUND → BASELINE_CAPTURED → DECISION_OPEN → DECISION_SEALED → PLAN_PREFLIGHTED → WAITING_HUMAN_EXECUTION_AUTH → EXECUTED_AND_READBACK → WAITING_CALENDAR_ADVANCE → NEXT_CAPTURED`。
意图异常 `CONFLICTED, CONTEXT_STALE, NOT_EXECUTED, UNKNOWN_LOCKED, STOPPED_PARTIAL` 不自动进下一轮。

用户触发：
- `初始化赛季闭环`：只读绑定当前存档/世界线和 Human 冷备份/测试库，并作完整初始采集，未确认当前 save/epoch 不自动执行；
- `进行第N轮采集与决策`：检测与前一轮游戏进度、按需要进行 INCREMENTAL 或 FULL、构建只读指标与角色决策，然后逐条加入 Outbox，展示待办、冲突/证据；不触发写入；
- `冻结第N轮决策`：sealed digest、计划分组、预算、未支持项，预检 live Getter/CAS，展示精确修改明细和失败停止条件；
- `授权执行第N轮 ... digest ...`：仅在本轮用户确认的许可动作/对象/数量里执行一次，所有真实回执与独立只读 readback 完全校验后记成功；no-op/UNKNOWN/partial 真实反馈；
- `我已在游戏日历模拟至[游戏日期]，继续第N+1轮`：新的日期和完赛校验，继续本轮采集/决策；game running or progress mismatch → stop；
- `查看赛季闭环状态`、`暂停赛季闭环`、`查看未执行决策`、`导出第N轮验收结果`：只读查询。

用户每次不必复制代码、填写 PID、重传同一批对象；Host 从已绑定现场/Outbox 取上下文。身份和摘要必须在 Host 生成后向 Human 展示，不能提前猜测。

## 3. 推荐游戏日历与采集周期（候选默认值）

**初始试点：4个7游戏日周期**。从当前实际游戏日历绑定，若新档尚未开始比赛，先 baseline 只读；Human 逐次模拟7天后以提示词确认继续。每轮不超过1个已批准的 live batch，不自动重放任何失败项。

**正式整赛季：常规赛每7游戏日一次检查与采集**，约25–27次，实际按档案赛程的起止日期计算，不硬编码跨季日期；加上赛季开始、交易截止日、全明星、季后赛各系列结束、休赛期选秀/自由球员关键节点等 5–10 个事件检查点，**目标约20–40次/赛季**。同一游戏日撞期合并为一次采集，避免无意义重复；若某个周没有新比赛且无世界变更，自动返回 `SAME_STATE_REPEAT` 而非制造“新观察”。

采集模式：
- `BASELINE/FULL`：新档、恢复旧档、换档/赛季跨年、重要身份/roster变化、用户直接说“采集全量数据”；
- `INCREMENTAL`：用户完成一个7日模拟周期后，存在新完赛比赛；有些 Family 仍会全家族重跑，年度来源遵守已有 cadence；
- `TARGETED_READBACK`：REA 写入之后立即按受影响字段只读核验，不再为了读回100字段强制全量采集；
- `EVENT/FULL_OR_SELECTED_FAMILIES`：交易、选秀、阵容、全局设置等事件，根据实际来源家族和依赖进行明确选择；不要绕过采集依赖错列“全量”。
- 某些游戏高级统计只有比赛后更新，必须在本轮结果中区分 `NATIVE_STALE_UNTIL_NEXT_GAME`，不要凭“已修改设置”制造新的比赛样本。

## 4. 每轮决策协议与指标

- 执行数据：只读 `WorldData` 当前已发表带 save/season/epoch 的字段 + 预定义游戏本机高阶数据/原生字段；缺失标 `NOT_CAPTURED/STale`，不补造累计统计。
- 角色：GM 决定经营目标与优先级，Coach 决定战术/训练/轮换调整，Player profile 的建议须经 role grants；不强制每轮都产生改动，**No Change 是合法结果**。
- 单项意图至少有 `intent_id, cycle_id, role/issuer, action_id, target player/team, field_id/target_value, expected_before or snapshot ref, reason, evidence_refs, scope, dependencies, rollback_policy(no automatic restore), proposed_verification_metric`。实际 `ActionIntent.parameters` 严格按已存在 role capability schema；额外 metadata 留 Outbox。
- 同一对象/字段多角色不同目标：人/规则明确消解，不能后写覆盖；相同值 coalesced aliases 保留决策来源。未知 Native / 未在当前 Live allowlist 的动作 `NOT_EXECUTED`。
- 每轮可产生0到多条决策；pilot 前两轮建议 1–3 条 **真实已允许 Player SHOT_TENDENCY** 改动，其余动作可以离线规划但不实际写，确保先验证闭环而非扩大动作矩阵。
- 真实 Native 修改后先 Getter-after，然后**等待 Human 日历模拟**获得新比赛事实；下一轮以新比赛数据评估之前的提议是否有效。不以小样本比赛波动自动断定教练策略优劣；优先日历模拟样本，用户可决定延长观察窗口。
- 结果需区分 `ACTION_APPLIED`、`ACTION_NOOP`、`DECISION_UNSUPPORTED`、`CAS_MISMATCH`、`UNKNOWN`、`GAME_EFFECT_NOT_YET_OBSERVED`。

## 5. 开发与验收顺序（内部 OS Loop）

### S1 · 最小源集成和 Host 只读能力

本新任务分支从 Outbox/REA 已验代码起步。只把 WorldData 优化分支的 `engine.py, performance_trace.py, player_detail_reader.py, player_skill_reader.py` 等必要改动**选择性集成**；定向运行 WorldData 与 REA 测试，固定各来源文件 blob SHA，避免把另一个完整旧任务分支直接合并进 master。保留所有已有 schema、source/history 和 20 Family 调用机制。

编写 `season_cycle_host.py` 最小模块与 `season_cycle_cli.py` 人类触发入口，复用 CalendarSimOrchestrator、WorldData DB binding、Outbox。完成绑定、快照、状态机、轮次/事件时钟、季节 trace、崩溃恢复；允许没有游戏时 Fake 注入。

### S2 · 离线四轮完整闭环

用固定 GameState 及日历 progression 模拟至少4个7日周期，含多角色意图、其中一次 NO_CHANGE、一次冲突、一次失败和一次 UNKNOWN、一次跨赛季/恢复存档世界线不同、一次重复提示词调用、一次并发触发；确保只读和唯一事务边界，结果不会自动被重试。至少10k intents 仅离线测记忆/性能，不需要大量真人修改。

### S3 · Human 参与的真机四轮 Pilot

Human 在游戏界面按已知流程操作日历。Host 每轮先核验进程/存档/历史，执行用户主动发起的采集和决策；有正式计划后 Human 显式确认 `plan_digest` 的本轮 live 允许动作，才可调用已验证的 REA Native Writer。初期只认证 `PLAYER_PATCH_TENDENCIES/SHOT_TENDENCY` 小规模写入；其他角色动作留观察/离线 Fake，不能因 Outbox 可以封存就开放实机。一个循环包括后续比赛数据重新采集和前后指标对照，**不需要自动把游戏日期推进**。

### S4 · 扩大整赛季（由 Human 选择触发）

Pilot 四轮通过后，User 可触发当前赛季继续到 regular season end、playoffs 或 offseason；按 event cadence 建周期，无需重新部署。每一轮计划与授权可合并交互，但默认不无声执行或无限自动模拟。产出 `season_run_ledger`（轮次、游戏开始/结束日期、fresh snapshot、角色决策、真实 actions、readback、比赛观察变化、异常、总耗时）。

若 Human 想让 Host 一键持续模拟整赛季，不应声称已经拥有模拟能力：先交付**人工推进→单指令完成当轮采集与决策**的系统，自动游戏推进属于单独验证的下阶段接口。

## 6. 核心停机门及交付

- 当前 live 进程/存档/角色权限/游戏日历不确定、无有效备份、正在比赛、epoch/schema 跳变，停止而非继续/自动重试。
- 无完整原始 Native 收据、Journal 和每项独立 Getter 对照时，不回填 `VERIFIED_SUCCESS`。
- 没有授予新动作的 Human/Host 授权，就不要实际写入；旧100次批量验证证明单一 Player 倾向实现，不证明任意多角色动作成熟。
- 不允许把新来源读数伪装为累计统计；游戏历史采用 append-only。
- 决策与执行循环不能迫使用户在每轮重复输入 PID、备份哈希等已绑定但可实时核实的数据。
- 优先最小复用与脚本自动化；避免创造长驻后端、全新数据表体系、额外审核工作流。
- 测试、错误、性能、真实模型和证据必须进入当前 Run；内部 Loop 可连续直到代码稳定，不以每小改动召开独立评审。

**产物**：`season_cycle_host.py`、`season_cycle_cli.py`、可测试的 Host→WorldData/Outbox/REA 桥、`season_cadence_policy.json`、`human_trigger_playbook.md`、4轮离线与真实测试收据、`season_run_ledger.jsonl`、`loop_iterations.jsonl`、`loop_summary.json`、`completion_pointer.md`，完整最终 SHA 和测试命令/退出码。真实4轮测试须由 Human 逐次触发，不得因 Codex 离线开发完成就冒称已完成 Live。

**本任务当前阶段**：`DISPATCHED_NOT_EXECUTED`。不合并 master；仅在 Human 已给出的“减少复杂度并充分验证”条件成立时以明确有界 PR 集成。
