# NBA2K22 REA · 批量执行器实机准入前安全工程 · 函数级派单

任务 ID：**NBA2K22-REA-BULK-SAFETY-ADMISSION-20261101-001**
OS 岗位：**execution**；执行模型目标为 **Gemini Flash 3.8**，必须在各次收据中登记实际运行模型（如实际使用 Gemini 2.5 Pro，须如实记载，不得混算 Flash）。
规划模型：GPT-6 / decision_architecture。
工作分支：**task/nba2k22-rea-bulk-safety-admission-20261101**
冻结的上游 REA Bulk 工程 SHA：**04c378151c576140b5e347c94a1b0952b15903cd**；实现提交 **3868c9f0fb95b674036970f0e0cb2f50826ec40a**。
上游原任务：NBA2K22-REA-DETERMINISTIC-BULK-EXECUTOR-20261101-001；首次交付后两轮整改预算已使用，不得在旧 Run 虚构第三轮或回写旧证据。
Human 决定：**批准拆根因的新阶段离线安全准入工程，不批准游戏写入**。Core 第11节要求原任务冻结、另立根因任务、由 Human/总架构决定继续，此处采用新任务与新分支正是对该边界的落实。

## 0. 目标与绝对权限边界

本任务的独立新增目的：**把离线批量引擎转化成可审计、可阻断、可人工单次授权设计复核的安全准入候选**。它不是扩大 Player/Coach Native 功能的第三次补丁，也不是生产实机执行器交付。

允许：源码修订、Fake Transport、Node VM/合成内存、故障注入、10k Mock、GitHub 轻量证据上传、追加式 Loop 记录。
禁止：NBA2K22.exe 进程附加/Frida 真实注入、真实 Setter 或 Coach Apply、存档/日历修改、WorldData 新 FULL/INCREMENTAL 采集、运行真实 execute-authorized、安装工具/提升权限、master 合并、改变 Core canonical 定义、自动启用服务或 scheduler。
**所有实时运行入口继续 fail-closed**：任何 CLI flag、自填 authorization_ref、PID 或 JSON 都不构成 Human 授权。若真需要运行游戏，停止并交付候选，由 Human 单次确认，之后必须按相应审核与验证门另立授权范围。

验收状态：**OFFLINE_SAFETY_ADMISSION_CANDIDATE**；含义仅是已通过可信离线安全模拟和证据完整性审查。不可声称 LIVE_READY、PRODUCTION_CERTIFIED、10k 游戏实测、SAVE_PERSISTED。

## 1. 源码先读与设计限制

源文件根路径：
08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/

必读：
- bulk_executor.py 中 BulkBatchHeader/BulkIntentItem/BulkBatchPlanner.plan、BulkFridaScriptCompiler.compile_chunk、ReaChunkTransportAdapter.execute_chunk、ExecutionJournal.claim_chunk/recover_interrupted_claims/reconcile_unknown/get_locked_resources、BulkExecutorService.run_with_transport、run_10k_benchmark
- role_batches.py 中 ExecutionJournal / NativeActionDispatcher（既有 claim-before-execution 和 at-most-once）
- registry.py、data/action_registry.json、data/native_bindings.json、data/coach_settings.json、transport.py、runtime_codegen.py、runtime/player_stats.js、runtime/coach_settings.js、runtime/common.js、runtime/gui_once.js
- tests/test_bulk_executor.py、tests/node_vm_chunk_runner.js；上一轮 Run 下执行报告和 Loop 评估。

现有实质缺陷（冻结 SHA 的静态证据）：
1. run_with_transport 约1296行将 prior UNKNOWN resource 锁判断写成 locking_id != item.intent_id，**同 ID 可再次进入 Transport**；is_intent_completed() 又仅按 intent_id 判断，无完整 request/plan/save 身份绑定。
2. reconcile_unknown 约955–960行仍接受仅有 applied:true/false 的未经观察证据，随后可强制 unaltered_fields_check=true 并解锁。
3. claim_chunk 约884行、lock_resource 约935行采用可覆盖 write_text，按 chunk_id 命名，未证明 atomic no-clobber / fsync / 跨 batch 独立身份；recover_interrupted_claims 以任意结果的 intent_id 作为 completed，get_locked_resources 在损坏时返回空映射。
4. run_with_transport 约1368–1371行只在 digest 字段存在时核验；等长但错误 receipt ID 的响应可能在索引时失败，且成功回执字段缺失默认 true。
5. BulkBatchPlanner.plan 约339–356行只按 save/team 分组，混合 action 时贴 PLAYER_PATCH_TENDENCIES 标签；行为与注册 action 权限不一致。
6. has_failure 仅在 chunk 声称 CHUNK_HALTED 时停止后续块；缺少 strict response/Getter/readback 不变式校验。
7. Coach 原生批量路径不能从 Node Mock 认证；现有脚本 is_live=false，仅在 is_live=true 才拦截 Coach，不能把原生 Apply 方案认作真正准备就绪。

**不允许为了过测试而删除 Node VM 负例或放宽旧安全守卫。** 优先复用既有角色原生合同，避免第三套权限/存档/Journal 系统。只实现以下可验证的根因修复与离线“授权边界设计”。

## 2. 包 S1：Journal 守恒与 at-most-once 的单一安全状态机（最高优先）

修改锚点：ExecutionJournal.__init__、claim_chunk、recover_interrupted_claims、is_intent_completed、get_locked_resources、is_resource_locked、lock_resource、reconcile_unknown、BulkExecutorService.run_with_transport；必要时提取同目录有限 helper。

**确定性实现步骤**：
A. 使用不可变 Claim identity = SHA256(canonical(batch_id, save_instance_id, plan_digest, chunk_digest, action_id, ordered intent targets+expected_before+value))；禁止仅靠 chunk-0001 filename 表示全局唯一。新 Claim 必须在“真实可能进入执行窗口”之前持久化，采用创建不覆盖/同卷原子文件替换或等效机制，加同步与校验。提交失败直接中止；不要虚称普通 write_text 为 atomic。
B. 运行前重建 journal 的目标状态。锁定源为 Claim + append-only receipts/reconciliations，可使用衍生 lock index 作为缓存，但索引缺失、损坏、与账本冲突时**fail-closed**；不能返回空映射当成无锁。支持安全的并发/跨进程文件互斥，或显式排除并发运行且在代码中硬阻断（不能只写文档）。
C. 状态建议：PLANNED → CLAIMED/STARTED → [VERIFIED_SUCCESS / VERIFIED_NOOP / VERIFIED_REJECTION / UNKNOWN]；UNKNOWN 在人工独立证据未完成前永久禁止同一资源的新写入，**即使 intent_id 完全相同**。同一 ID 的重复请求仅在原始 request/save/plan/digest 全部一致、且之前已完整 verified terminal 时可 REUSED_HISTORICAL_RECEIPT；任一差异均拒绝。
D. 崩溃窗口要覆盖 Claim 已写、Transport 被调用但返回前、receipts 仅部分写入、锁索引损坏、跨 batch 同 chunk ID、重复进程并发。恢复时无法证明未开始写入，则 UNKNOWN 并锁定；不能试图自动补偿、重放、猜测成功。
E. reconcile_unknown() 移除 applied-only 降级分支；证据必须关联 Claim digest、save/epoch、动作、资源、观察时间、已认可的独立只读来源、原始读回值与完整性信息。**只读观察当前等于目标不自动证明过去由本意图唯一导致**；不能认定效果来源时保留 UNKNOWN，或仅记录观察状态，不释放写入锁。由 Human/独立验证准入决定是否可解锁。不能默认 unaltered_fields_check=true。

目标测试：同 intent prior UNKNOWN 重试零 Transport calls；跨 save/plan 相同 ID fail-closed；crash-after-claim/call/partial-receipt；缺失/腐败锁索引；并发启动；仅 applied 布尔值尝试 reconcile；污染数据恢复，不自动解锁。

## 3. 包 S2：注册 Action、不可变计划与完整回执协议

锚点：BulkBatchPlanner.validate/plan、BulkFridaScriptCompiler.compile_chunk、BulkExecutorService.run_with_transport、data/action_registry.json（只读）、tests/test_bulk_executor.py。

步骤：
A. 仅允许 registry 存在且明确具备本次范围的 Native action；规范化 ACTION_ALIASES 之后按 (save_instance_id, team_id, **canonical_action**, field_family) 切块。不得把混合 Player attribute / tendency / Coach 设置送入伪造的 PLAYER_PATCH_TENDENCIES 组；若跨动作依赖无法正确排序，拒绝计划，不能忽略依赖或只看是否存在。禁止依靠伪造 action_id 绕开 allowed_action_ids。
B. 每块 immutable chunk_digest 绑定精确有序 intents、原值、目标值、动作、game-build、source/save/epoch 身份与预算；如果在运行时过滤 completed/locked intent，**必须重新计算实际 sub_chunk_digest**，不能沿用原完整 chunk 摘要。
C. 针对本任务 batch 只能接收一种严格 envelope：kind=chunk-execution-result；强制且逐一匹配 batch_id、save_instance_id、action_id、chunk_id、chunk_digest、plan_digest、schema_version、receipt ids（与预期 intent 集合完全相等、每个一次）和状态闭集。消息丢失、多份、损坏、错序、摘要缺失、异常、多余/缺少 intent、不可识别 outcome，都转换为 conservative UNKNOWN + stop；不要用宽容 native-control-result 直接替换批次回执。
D. SUCCESS_APPLIED 至少要有 getter_before==expected_before、getter_after==requested、明确为 true 的 unaltered_fields_check（仅已认证范围）以及与意图一致的 target/field；没有证据的“成功”降为 UNKNOWN。No-op 必须 before == expected_before == requested 且无 Setter 调用证据，不能编造。
E. 如果任何一项失败或 UNKNOWN，不论 envelope 自报 CHUNK_SUCCESS/CHUNK_HALTED，均立即停止后续块。已确定未执行的后缀 NOT_EXECUTED，已进入执行窗口却无可靠逐项证据的 UNKNOWN。每批一次性 assert planned=success+noop+reused+blocked+unknown+not_executed，且每 intent 恰好一个**本次**终态。
F. Player 只在现有已恢复 Getter/Setter 路径进行离线模拟；Coach 可以由 planner 识别，但必须默认标记 UNSUPPORTED_FOR_LIVE，不从 is_live=false 推导安全认证。不补写任何新 RVAs、指针布局或不可靠跨季身份。

测试：不同动作同球队分块；缺摘要、错摘要、混入其他 intent ID、假 SUCCESS 缺 before/after、false unaltered、失败却标 CHUNK_SUCCESS、重复/跨块回执、action alias 异常、dependency cycle、plan mutation、subchunk digest 实际一致。

## 4. 包 S3：准入权限设计与执行隔离（不连接游戏）

锚点：ReaChunkTransportAdapter、cli_execute_authorized、transport.py（只在不破坏单动作路径时调整）、新测试。
- 明确两个层：offline fake DI 能调用，但 live adapter 继续 hard-deny。保留 LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE。
- 输出一份**待未来 Human 审核的授权接口设计**，必须拟绑定精确 plan_digest / chunk_digests、save_instance、EXE SHA、process start epoch、菜单/对象生命周期、具体对象字段旧值新值、数量/调用/时限预算、允许一次或有限次数的范围，以及独立执行证据号。
- 本次**不实现可被 CLI 文本绕过的授权替代品**，也不激活游戏运行时。不得在 Node Stub 之外连接 Frida 或用远程工具测试游戏。
- 给出真实游戏 Stage-1 单字段验证方案，但仅作为未来单独 Human 决策输入：现场确认世界线/备份/存档、再请求独立临时授权；优先验证 80→80 No-op，随后是否尝试有写入的值由 Human 另行裁决。不要恢复旧 Lillard 因果实验或自行推进赛季。
- 未来正式实机门必须包含独立审核/可信授权验证器、环境绑定、失败停止与单次范围。当前无这些即 STOP_AT_HUMAN_GATE。

## 5. 包 S4：实证测试与性能/Loop 收尾

必须通过以下**源代码与可执行测试**，不是 grep/口头描述：
- G1 zero-real-game-attachment and CLI/adapter fail-closed，且没有任何测试 import 自动启动真实 Transport。
- G2 same-intent UNKNOWN / cross save / plan drift / corrupt claim / partial write / concurrency 重放零执行。
- G3 reconcile 无独立观察证据不能清锁；禁止 applied-only。
- G4 Planner canonical action 分块+依赖图；50/200预算、真实 subchunk digest 和输入全 hash 绑定。
- G5 Strict envelope：缺任意必填、错误 kind/错目标/错集合、假成功等负例必须保守处理。
- G6 Node VM 运行 Player 正例、CAS mismatch、byte invariant、cache flags；Coach 不支持路径 fail-closed。
- G7 1/10/100/1000/10000 Mock 输入；每笔原始 receipt → 汇总可复算（包含故障注入）；性能实测 vs 会话估算 vs 实机预测严格分级。不要声称 10k 实机完成。
- G8 已有 60 项回归+本轮新增用例，保存运行命令、exit code、原始输出、固定 SHA、失败集合前后、测试 fixture 和真实执行模型。
- G9 Loop 观测真实性：在新 Run 使用候选 v0.1 最小通用 schema；每轮记录触发、bounded objective、实际修改、失败假设、测试收据、evidence grade、决策及 stop class；摘要必须程序化从 JSONL 复算。旧 REA 迭代缺 iter-005 是历史事实，不在本任务回填旧账或把本任务算作旧整改第3轮。

Loop 标准：单项有限增量 → 修改 → 聚焦正/负测试 → 分析发现 → 修正 → checkpoint → 下一增量；不得靠反复运行同一测试、空报告、无变化的 PASS 来累计轮次。任务内部开发有界增量不强设 3/5/10 轮，但每次必须有新证据。首次交付后纠正预算沿用 Core §11；本任务完成后必须如实停止，不以空转延长。

## 6. 发布边界、交付内容与停止

**允许修改的源码范围**：
- research/rea_native_control/bulk_executor.py
- research/rea_native_control/tests/test_bulk_executor.py
- research/rea_native_control/tests/node_vm_chunk_runner.js（仅必要）
- research/rea_native_control/transport.py（仅有旧兼容证据时）
- research/rea_native_control/role_batches.py（原则只读；如需修改必须停止并提出新的变更边界）
- 新增同目录专用、最小 helper 如确有测试理由
- 当前 Run 目录下任务合同、实际测试、Loop、completion pointer

不得改 Core、其他 REA 独立机制、任何 save/database、NBA master。边界超出即提交阻断说明，不自行扩大。

交付至少：
1. 完整可用的离线安全状态机/严格协议代码与 tests；
2. real live-admission authority 接口方案文档（设计，不激活）；
3. 自动化测试原始命令/日志（可复核），含 failure injection 与 10k Mock；
4. Loop 原始记录+程序化派生 summary，精确记录实际模型；
5. 最终 completion pointer：各 Gate PASS/PARTIAL/FAIL、可实证性质、明确 OPEN_GAPS、准确工作 SHA、禁止游戏操作的边界。
6. 保留上游原任务的旧结论和两轮整改历史，不改写上游 Run。

**真实停止门**：Core 第11节六类停止条件；新 Native 合同需要猜测、需要 Human 新语义、跨路径、新 protected action、真实游戏进程需求、测试不能证明主张或无有效下一增量时停止并附证据。

任务只能在分支交付 OFFLINE_SAFETY_ADMISSION_CANDIDATE 或真实缺口；任何真实游戏写入、运行时启用、Core/NBA master 合并，均必须另行 Human 确认与适当的独立审核。
