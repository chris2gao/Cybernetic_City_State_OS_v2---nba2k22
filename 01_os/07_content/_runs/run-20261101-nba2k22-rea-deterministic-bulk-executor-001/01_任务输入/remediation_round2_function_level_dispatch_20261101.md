# NBA2K22 REA 批量原生执行器 · 第二轮定向整改（函数级实施合同 / Gemini Flash）

**任务 ID**：NBA2K22-REA-DETERMINISTIC-BULK-EXECUTOR-20261101-001
**任务性质**：原任务第一次交付后的**第 2 轮、现有 Core §11 预算内最后一轮定向整改**；不是新任务、不是新 Workflow 阶段。
**GitHub 工作分支**：task/nba2k22-rea-deterministic-bulk-executor-20261101
**固定源 SHA**：1a800563c0051999fb882cc7231f75ec724b832f
**执行岗位**：execution；计划使用 Gemini Flash 3.8，**实际运行模型必须如实登记**（前次报告为 Gemini 2.5 Pro，不得事后改记）。
**GPT 规划岗位**：decision_architecture；已给出函数级设计，Gemini 实施并用真实测试修正。
**Core 开发 Loop 来源**：Core 候选 f3ae6b83897c04f6ee7758a9b32fc8ea2d06cea5 的开发 Loop 机制及已批准 v0.1 观测计划；试点评估固定 SHA 3dc65c3ca4e690078ddf0bf8b8df30912e174356。
**授权**：严格离线。**不允许** NBA2K22 进程附加、Frida 在真实游戏加载、Native Setter 调用、存档写入、游戏日历推进、WorldData 新采集或 master 合并。Human 此次批准的是本轮任务派发与离线整改，不是任何真实游戏操作。

## 0. 完成边界与责任

本任务只解决当前源码的三项重大阻断：A. 参数批次到 Fake Transport 再到 Journal 的实际闭环；B. 受已恢复 Native 合同约束的 JS 生成和 Player/Coach 路由；C. UNKNOWN、恢复、收据和 10k 统计真实对账。不要重新开发 RoleActionBatch、Native Registry、Frida Runner、世界数据系统；不要开展 Lillard 因果实验，不要扩大未恢复的业务接口。

目标状态：**OFFLINE_END_TO_END_BATCH_EXECUTION_VERIFIED**。这只表示离线可重放、逻辑闭合，**不表示 LIVE_CERTIFIED、实机可直接执行或存档持久性已验证**。如果仅能完成 Player 路径，Coach 保持明确 UNSUPPORTED_FOR_LIVE，不应为了齐全而编造已恢复能力。真正的 live adapter 只有在未来另行 Human 授权、权限服务具备可信验证和本轮必要验证通过时才可启用。

## 1. 固定的源码入口及问题：不准仅按文字描述判断

仓库相对基目录：08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/

| 文件 / 函数（源 SHA 下） | 已核实问题 | 本轮确定的修改方向 |
|---|---|---|
| bulk_executor.py:cli_execute_authorized（约 1338） | 校验 flag 后仅创建 Adapter 并返回，打印「Human authorized」，无分块执行，且字符串 authorization_ref/flag 无可信授权校验 | 将真实模式维持 fail-closed；增加离线 DI 的执行协调入口，按验证、规划、逐块派发、结果解析、Journal 闭环；禁止打印未证实的 Human 已授权 |
| bulk_executor.py:BulkExecutorService（约 957） | 仅有 run_offline_test，未与 ReaChunkTransportAdapter 正式协调；Mock 成功不能证明真实 transport 调用链 | 新增独立、可 Fake 运行的 run_with_transport 或等价有界方法，不抹掉旧离线接口 |
| bulk_executor.py:ReaChunkTransportAdapter.execute_chunk（约 686） | 传 BULK_CHUNK_{team_id}，不是 LiveExecutionContext.allowed_action_ids 登记动作 | 不再伪造 action_id；chunk 按已注册动作/同类 binding 拆分或使用经过独立验证的显式 adapter 身份；不得靠放宽白名单绕过授权 |
| transport.py:ReaCliTransport.execute（约 13） | 只读取 kind=native-control-result；批量脚本发送 kind=chunk-execution-result，导致无有效收据 | 在不削弱旧单动作契约的前提下新增**明确的批量结果解释器**或兼容的有界消息封装；严格验证 request_id、chunk_id、plan_digest、结果数和重复消息 |
| bulk_executor.py:BulkFridaScriptCompiler.compile_chunk（约 346） | 输出 standalone JS 缺少 team/rosterPlayer/read/call/u8；未使用完整 Common/GUI Runtime；直接使用 PeekMessageA Hook 但未校验游戏窗口线程；部分异常遗漏未执行项 | 使用 runtime_codegen.py 的已恢复拼接方法：common.js、需要的业务 helper、一个 executeAction、gui_once.js；注入绑定表、预算、目标构建检查、请求摘要，**每块仅一个 Hook**。不准手写无原生合同的替代入口 |
| runtime_codegen.py:render_program（约 12）；runtime/common.js；runtime/gui_once.js | 现成的单动作模板含 request/bindingSpecs/limits、native signatures、线程选择、调用预算 | 提取/复用最小公共拼接逻辑；原单动作脚本仍需回归，不在多处复制不一致的 ABI / RVA |
| runtime/player_stats.js；data/native_bindings.json | 现有实现验证 stat delegate/vtable、156字节期望快照、属性缓存标志、Getter 再回读；批量实现省掉许多关键保护，且 hardcoded context 未证明 | 将这些守卫复用于每个有写操作的 Player group；逐项 CAS；无论成功/失败，都不可仅凭单一 rawByte 和 Getter 声称 untouched 字段 PASS |
| runtime/coach_settings.js；data/coach_settings.json | 已恢复完整 880B GamePlan 输入投影、352B Coach 验证与位段/枚举；批量字段 COACH_FIELDS 的 0..100 和 offset 映射不符 | 不使用临时 COACH_FIELDS 当作真实合同：必须从 data/coach_settings.json 读取明确 field/enum/width/offset；根据现有 coach.settings 合同构造输入并检查前后效果；无法安全闭合则 fail-closed |
| bulk_executor.py:ExecutionJournal（约 711） | receipts 写后才 lock UNKNOWN；进程崩溃窗口内无前置 claim；reconcile_unknown 仅凭 applied 布尔值就解锁 | 先持久 claim/资源锁再调用；隔离或复用 role_batches.py 的保护语义；UNKNOWN 禁自动重放；外部观察有明确来源、时点与目标匹配才允许解锁 |
| bulk_executor.py:run_10k_benchmark（约 1135） | Mock 做了调用但 outcome_conservation 靠 9825/150/2/1/22 常量，且150项变更当前值可能触发 CAS mismatch | 从实际 Mock receipts 聚合全部结果；No-op 必须 current == expected_before == value；所有计数自动守恒，杜绝硬编码 |
| tests/test_bulk_executor.py | 现有测试只检查脚本包含字符串与 Fake 守卫，缺少真实分块结果处理/脚本执行 | 添加强约束离线 integration/fault-injection/Node VM tests，不用简单关键字 grep 冒充端到端 |

从 1a800563 可直接核实：COACH_FIELDS 中临时 POE 0..100 与 data/coach_settings.json 的位宽、枚举、GamePlan offset 不一致；coach_settings.js 中 POEDefense 槽位与直接字节 patch 也不是同一个操作定义。**不能把「Frida script 包含 call('coach.apply_gameplan')」当成 Coach 事务已经正确。**

## 2. 包 A：闭合执行协调器（先实现，再验证）

### A1. Batch / Chunk / Action 关系

在 BulkBatchPlanner.validate/plan 及新的协调器中执行以下顺序：

1. 读取 JSON/JSONL，验证固定 EXE SHA、队伍和当前 active roster 范围、保存身份字段存在、唯一 intent_id、field/value/expected_before 类型和范围；验证 action_id 属于对应的 PLAYER_PATCH_TENDENCIES、PLAYER_PATCH_ATTRIBUTES 或允许的 COACH_SET_KNOWN_CURRENT_SETTINGS，拒绝字段与角色/动作不匹配。对 dependencies 验证环和处理顺序；无法支持则明确 BLOCKED 而不是忽略。
2. 按保存实例、队伍、**注册 action_id 与字段族**确定性分组，避免原版每个 Coach、Player 属性/倾向跨合同乱组。分块上限同时满足 item 数、Native 调用次数、读取字节和预计主线程预算；若 10k chunk 数相对旧基准变化，如实重新测量。
3. 计算不可变 plan_digest；每个 chunk 生成独立 chunk_digest（批次/保存/对象/字段/value/expected_before/顺序/构建/调用预算），并传入脚本与收据。执行期间不允许修改计划、目标或上下文。
4. 明确预注册字段身份与对象活跃范围，不用未证明的 Player UID 猜自由球员/G 联盟/退役球员。

### A2. 可注入执行方法（只在离线测试中调用）

建议方法形式：BulkExecutorService.run_with_transport(batch, transport_adapter, *, execution_context, max_chunk_size=...)。transport_adapter 为通过 Fake 实现的接口（输入 chunk、compiled_script、action_id/chunk_digest，输出结构化结果）。**本轮生产 CLI 不应直接注入 real ReaCliTransport 来连接游戏**。

协调器逻辑（作为实现伪代码，而非指定不变函数名）：
- validate → plan → check_plan_and_authorized_scope → durable journal manifest。
- 每块调用前 reserve/claim 所有待执行资源，检查跨 batch 冲突和同一 intent 的 plan_digest；对已确认 SUCCESS/NOOP 只可在完全相同上下文下 REUSED，UNKNOWN 一律锁住不重试。
- compile_chunk → fake_transport.execute_chunk(**精确上下文**) → parse/validate message → append signed/hashed evidence reference and per-intent receipts。
- 若 transport 超时、崩溃、无消息、多消息、哈希不符、收据缺失/重复或身份不符：对受影响的**已进入执行窗口**目标标 UNKNOWN；对确定未开始的后续目标标 NOT_EXECUTED；释放绝无执行可能的资源，不释放 UNKNOWN。禁止重试或继续后续 chunk。
- 输出一次运行范围内每条 intent 恰一终态 receipt；把已有历史收据与本次运行的结果分开统计，断言 planned=success+noop+reused+blocked+unknown+not_executed。

### A3. 真实 Transport 暂停启用门

现有 cli_execute_authorized 中的 --allow-live-mutation、authorization_ref、expected_pid 只能是 **请求意图**，不能自行构成可信 Human 授权。立即修正误导性成功提示；保持真实路径禁用，明确返回 LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE 或等价确定性错误。在未具备可信 plan_digest、对象、save epoch、时间、数量和 action 范围的外部授权验证器之前，不得把 enabled=True 视作权限。允许 CLI 新增仅 Fake/fixture 的 offline end-to-end 模式。

## 3. 包 B：Runtime/Native 原生合同闭环

### B1. JS 构建

复用 runtime_codegen.render_program 现有拼接思路和 runtime/common.js 的受控版本。输入替换明确包含 __REQUEST__/__BINDINGS__/__LIMITS__/__COACH_FIELDS__/__PLAYER_CONTRACT_FIELDS__；必须从 registry.binding 收集真实 native_bindings.json，不要把任意未登记 RVA 当作已认证。生成一个 executeAction()（内部遍历 chunk），最后仅拼一次 gui_once.js；不能叠加第二个 PeekMessageA Hook，不能依赖未定义 u8。通用运行时的绑定签名检查、游戏线程选择、一次执行守卫应可被 JS Stub 测试观察到。

### B2. Player 保护

调用真实已恢复 Player stat context 的 root/delegate/vtable 校验；使用 team → rosterPlayer 解析 active roster 身份。逐项 Getter 与 expected_before **先比较再 No-op**；Getter 返回目标但 expected_before 不匹配时仍要拒绝，不静默跳过。Setter 前确认同一对象与状态未变；构建 156 字节的 expected snapshot，属性使用原有 raw 编码 (value * 3 - 75)，校验缓存 flag 变化与原 player_stats.js 一致；Setter 后读全块、Getter-after 与目标一致才可对可验证范围声称 PASS。未知 Native 副作用、读回异常或命令超时应 UNKNOWN/未证，不做补偿写。

### B3. Coach 保护

**参考真正的 data/coach_settings.json，而不是当前 COACH_FIELDS**。读取当前 Coach 结构并校验归属；采用 coach_settings.js 的完整 880B GamePlan copy/恢复投影与 352B Coach expected 编码、枚举位宽检查，以及 Apply 后真实 Coach 投影/原始 GamePlan 不变检查。若无法在局部整改里证明其安全和具体字段值，返回 UNSUPPORTED_FOR_LIVE 并用 Fake 验证 fail-closed，不得为了达到表面覆盖而用 inputBuf.add(offset).writeU8 一次 patch 代替完整协议。

### B4. JS 离线动态测试

使用 Node 的 vm 或合成 Frida JS stub（**绝不附加真实进程**），模拟 Process、Memory、NativeFunction、Interceptor、send 和游戏线程事件。必须覆盖：已选择正确线程才触发一次；Getter/Setter 调用顺序；无效 Root/Delegate/Coach owner 拒绝；CAS mismatch 零 Setter；属性缓存及邻域 bytes 变化负例；超时前后回执唯一性；失败前缀/未执行后缀与 chunk 消息内容。只做 node --check/字符串存在性不足以通过 Gate B。

## 4. 包 C：Journal 和 10k 证据闭环

- 在 ExecutionJournal 新增 claim ledger（引用 batch_id, plan_digest, chunk_digest, resource, target, save_instance_id, intent_id, expected_before, value, state），**在 Native 可能发生之前**原子提交/flush。跨进程或第二次启动遇 claim=STARTED/UNKNOWN 必须 fail-closed；损坏日志/丢失锁文件不可视为「没锁」；对同一 intent_id 但不同 digest 的复用拒绝。
- 必须参考 role_batches.py:ExecutionJournal/NativeActionDispatcher 已有的 claim-before-execution/at-most-once 语义；优先局部复用，不要生第二套互相冲突的权限总账。
- reconcile_unknown 不允许接受无来源的 {applied:true/false} 直接释放锁。观察证据至少绑定：原 claim/plan/save/对象/字段、来源种类/时点、独立 Getter 或等效只读证明、目标值、完整性；证据不足则保持 UNKNOWN 和锁；不可仅凭当前等于目标就认定此前 Setter 唯一造成结果。**本轮不执行现场外部取证**。
- 10k 模拟 benchmark：保留 Mock 计时；将收据合并真实计数，依据已执行 receipt 统计 success/noop/blocked/unknown/not-executed/reused，并断言每 intent 一条；测试中实际注入可复现 No-op（current == expected_before == target）、CAS mismatch、timeout 和后缀停止；不要把 9825/150/2/1/22 直接写成常量结果。当前4秒/session及小于50ms的实机时间只可保留为 **ESTIMATE/PROJECTION**，不叫实测。
- 输出结构须区分 Mock 计算耗时（实际测试）、会话/Native 执行耗时（假设）、未来游戏端真实测量（NOT_RUN）；不能凭测试过 54 个用例就宣称 live ready。

## 5. 强制失败注入/验收门（本轮均为离线）

1. FAIL_CLOSED：无可信授权、只给 --allow-live-mutation/authorization_ref、dry_run 误用、未知构建、错 action_id/字段、跨存档和无有效 plan hash 均不得启动 real transport。
2. E2E_FAKE：至少一份两块及混合字段的文件从 CLI/Service 贯穿 validate→plan→compile→fake execute→chunk receipt→journal→summary；Fake 必须被**实际调用**，不能只检查适配器构造。
3. JS_RUNTIME：Node/vm 合成环境实际触发一次 executeAction；检验对 native message 的 kind、chunk_id、request_id、plan_digest、无裸地址、结果数量的处理；旧单动作 render_program+transport 回归不退化。
4. FAILURE：CAS mismatch、Native 返回前/后异常、丢/多收据、错 digest、超时、Coach 不支持、对象漂移、主线程未进、Journal 崩溃/锁文件损坏、第二次请求和改过 plan 的重复 intent，全部守恒且不盲目重写。
5. BENCHMARK：1/10/100/1000/10000（规模按资源允许），固定可重放输入、全数结果实际聚合、统计原始明细与说明、p50/p95/p99；若运行压力过大保存准确停止与部分结果，不虚构。
6. REGRESSION：运行 test_bulk_executor.py、test_role_batches.py、test_role_capabilities.py、test_player_stats.py、test_player_editor_read.py，以及新加的 Node 模拟与断言，保存命令、exit code、输出与版本。现存的 54/54 仅是**旧版本**回执。
7. FORMAL_BOUNDARY：任何真正的 Frida target attach、Native Setter、真实 Coach Gameplan Apply、存档/比赛/WorldData FULL 都是 NOT_RUN 且不授权。

未全部满足 Gate A/B/C 时，只能报告具体缺口，不能继续使用 OFFLINE_BATCH_ENGINE_READY_FOR_GRADED_LIVE_TEST 作为本次当前工程通过判断。

## 6. Gemini Flash 内部开发 Loop：从「任务实施」而不是「重复写报告」出发

这是第 4 个 Core Loop v0.1 观察样本，**与 Gemini 函数级指引试验分别评价**。在一个持续的第二轮整改任务内部，选小的有价值步骤（建议 3–5 项局部修复/检验一组），执行：
(1) 根据已有失败和固定源选一个最高价值增量 → (2) 实际改代码/提出可反证机制 → (3) 执行聚焦正例、负例、回归并保存原始输出 → (4) 对比前后失败集合，明确新证据 → (5) 更新真实 checkpoint，继续下一增量或按现有 Core §11 停止。

**不要每执行一条命令算一轮；同一测试无代码/假设/新证据变化的重复不算新迭代。** 开发内部有意义增量不设固定轮数，但不得无证据无限运行。当前已经首次交付，并使用了第 1 轮交付后定向整改；本次整体是**第 2 轮交付后整改**，内部多个增量不增加交付后整改轮次。完成本次后不得另开第三轮改名续做来绕过 Core 预算。

在同一 Run 下**追加式**维护：
- 06_执行/loop_iterations.jsonl：每轮强制 schema_version、task_id、iteration_id、record_type、trigger_type、trigger_ref、bounded_objective、actions、sha_before/after（没有有效快照可明确 null）、test_receipts、outcome、decision、next_trigger_or_stop_ref、recorded_by_model、failure_set_before/after、evidence_grade。
- 08_结论/loop_summary.json：分别统计内部有效迭代、交付后整改轮次、可复算各 outcome 与 stop class；摘要应从现存原始行得出。**原任务迭代编号 iter-005 缺失且摘要 6 对账本 5 不符：不得凭空补造 iter-005 或覆盖历史**。新记录从实际下一个唯一编号追加；增设 discrepancy note / additive correction，输出 reported_count 与 verified_log_count，不假装它们已一致。
- 08_结论/completion_pointer.md：写固定最终提交、测试证据、实际执行模型、各 Gate 判定、真实缺口、下一次 Human 授权边界。若测试失败则诚实保留 OPEN_GAPS，禁止冒称 FULL PASS。

停止原则：达成离线三包验收（可交候选）；或出现真正外部依赖/新高风险授权/代码证据无法支持的 Native 语义/重复无价值失败（按 Core §11 停止并报告）。不新增独立审核窗口，不自动触发 master 合并。

## 7. 交付顺序和验证输出

**增量顺序建议**：A1 输入动作校验+分组 → A2 Fake run_with_transport+消息协议 → C1 claim-before-execution → B1 runtime 动态执行 → B2 Player/Coach 严格守卫/受控降级 → C2 10k 可重算与回归 → 汇总/提交。允许证据驱动调换，但不可在 A/权限仍未闭合时启用 live。

最低交付：
- 同一原任务分支实际代码、合成 JavaScript 与 Fake Transport 测试、旧用例回归；
- 离线运行/故障注入/Benchmark 的真实机器输出；
- 失败集合前后差异、Loop 原始记录与可复算摘要；
- 对当前 3 个阻断包逐项 EXACTLY_CLOSED / CLOSED_WITH_LIMITATION / OPEN；
- 完成时推送原任务分支，给出**完整 commit SHA**、明确改动文件和精确证据定位。
- **不要改写此任务书、旧 Human 裁决或旧运行收据。**

此为 GPT 规划岗位依据固定源码提供的具体实施方法，不构成新的 Native ABI/内存地址已实测认证。若实际源码合同存在冲突，以原始 Native 证据与已恢复合同为准，停止猜测并报告具体冲突和可验证下一步。
