# REA Decision Outbox · 标准化决策容器与批量执行闭环

任务 ID：**NBA2K22-REA-DECISION-OUTBOX-20261102-001**
OS 岗位：**execution**（拟交 Gemini，务必记录实际运行型号）
规划：GPT-6 / decision_architecture
分支：`task/nba2k22-rea-decision-outbox-20261102`
基线：**80955e8ed501a9ab57fc4b363646b525c0748a98**（100项真实批量测试交付固定 SHA）
Human 需求（2026-11-02）：100项实机修改约10.32秒已经可接受；停止单纯追求加速。后续角色日常决策产生一条条标准化意图，进入统一持久容器；决策阶段结束后冻结完整批次，进入 REA 批量执行，自动读回并将结果反馈角色形成闭环。当前优先 REA，WorldData 采集优化暂缓。

## 0. 原则、权限和本任务的真正交付

**本任务是“决策意图集成与生命周期闭环”，不是第二套 REA、第二套 GM 决策数据库、第二套审批系统。**

- 容器 = 持久的 **Decision Outbox（待执行决策意图箱）**，不是 Docker 容器或 Frida 会话，既不允许增加原生动作能力也不决定篮球策略。
- 它应复用既有 `role_batches.py` 的 `BatchContext, ActionIntent, RoleActionBatch, ExecutionAggregator.collect/plan`、`role_capabilities.py` 的角色/权限与动作元数据、`BulkBatch/BulkIntentItem/BulkBatchPlanner` 的 Setter 校验、`BoundedSessionExecutor` 的有限单会话分块执行以及 `validate_100_receipts.py` 的自动对账经验。
- **Decision Outbox 不等于 Execution Journal**：Outbox 存“为什么、谁、何时、要做什么、未决议是什么”，既有 Journal 存“哪次 Native 已尝试、回执、UNKNOWN 与重放保护”。两者通过 `decision_id/intent_id/batch_id/evidence_id` 关联，不混写。
- 角色不能自行声明新权限，无法将一个 GM/Coach/Player 提议凭填写 JSON 变成授权执行。复用 host-authenticated profile、phase grants、现有 Human 裁决与现场授权接口；本任务不新增 Human 二次签署制度。
- Human 已授权此前**一次100条 SHOT_TENDENCY 实机测试**，但**本次未授予新的无限制角色决策 live Setter 权限**。当前任务仅开发离线闭环、Fake/NodeVM 及现有证据回放；若需要新真实游戏写入，单独依据当前 Human 指定范围操作，不得沿用一次测试授权扩权。
- 100条实机任务 10.31760s 是固定验收事实；不作为此任务必须再次跑100条的理由。既有 `100-live-benchmark-001` 原始报告与回执不可修改。

## 1. 源码与既有合同（先看再写）

研究根目录：`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/`

必读：
- `role_batches.py`: `BatchContext` 内 world/save/generation/season/phase/snapshot/catalog；`ActionIntent.decided` 的 canonical `parameters_json`；`ExecutionAggregator.collect/plan` 的身份/冲突/依赖；`NativeActionDispatcher` 的独立 action dispatch 和 UNKNOWN 守卫；
- `role_capabilities.py`: 当前合法 requirement action_id、受信 Host profile、phase applicability、submission parameter schema（不要猜测）
- `bulk_executor.py`: `BulkBatchHeader, BulkIntentItem, BulkBatchPlanner.plan, FieldCatalogLoader`, 注册动作别名与冲突/依赖；
- `bounded_session_transport.py`: `SessionCompiler, SessionBatchTransport, BoundedSessionExecutor`，以及现有已知“会话回执校验偏弱、Claim早于会话独占”限制；
- `validate_100_receipts.py`: 当前独立校验脚本及字段名问题；
- GM 路径 `docs/development_tasks/DEV_20261019_10_M3A_DECISION_PACKET_DESIGN_V1.md` 与 M3-T 接口：analysis packet 只是分析草稿，不能自动执行；明确形成**已决策** action intent 才进入 Outbox；
- `research/rea_native_control/ROLE_BATCH_EXECUTION.md`: 当前 role batch 还是 offline engineering candidate，不得误宣称所有角色/交易/Coach 实机路径已经支持。

已存在的两个抽象各自是对的：
**角色决策：RoleActionBatch / ActionIntent**；
**字段执行：BulkBatch / BulkIntentItem**。
缺失的是**跨一轮角色决策持续收集、持久版本化、冻结、翻译和闭环回执**。仅补这层，不修改下层对象的原有含义。

## 2. 推荐的最小容器方案：单本地 SQLite Outbox + append-only 事件

允许在同目录新增最小模块 `decision_outbox.py`、`decision_batch_bridge.py`、`decision_outbox_cli.py` 和测试；如果已有可靠持久机制可以复用，可采用等价的单文件+事件机制，但必须能在 Windows 中耐受崩溃，支持千条插入和不可变封存。

SQLite 为**执行管理元数据存储**，不是 WorldData 历史事实数据库。最少以下三张表或语义等价实现：
- `decision_cycles`：`cycle_id`、不可变 `BatchContext` JSON/hash、上下文来源、状态、revision、封存时间、`sealed_digest`、关联批次 ID；
- `decision_intents`：`intent_id`、`cycle_id`、host 确认 `issuer_uid`、requirement `action_id`、immutable canonical `parameters_json`、`dependencies`、`agreement_ref`、`source_evidence_ref`、`decision_reason`、`resource_key`、`state`、`supersedes_intent_id`、时间；不要让未认证的模型 origin 冒充授权；
- `outbox_events`：自增序号、`cycle_id/intent_id`、event_type、前后状态、revision、metadata、时间和必要的哈希。每项更新和事件在同一 SQLite 事务提交；历史不删除。
- 回执详情保留既有 Execution Journal，不复制100项 raw messages 入 Outbox。Outbox 只关联执行 `batch_id, plan_digest, journal_path, evidence_id, outcome, independent_readback_ref`，可从实际收据重新计算状态。
- 采用 SQLite WAL / unique keys / transactional seal（仅在同宿主文件系统且合理使用）；不编写常驻进程、消息队列服务器、Docker 或新的复杂分布式锁。
- 真实数据规模要求至少以 1,000/10,000 **离线**意图回放测吞吐；如果 SQLite 增加不必要复杂度，需提交证据说明更轻持久存储方案同样满足原子封存和历史审计。

## 3. 设计意图格式与阶段协议

**决策阶段 DRAFT 可持续 append**：GM、Coach、Player 每生成已决定的 action，按 `ActionIntent.decided(intent_id, issuer_uid, action_id, exact_parameters, dependencies, agreement_ref)` 加入容器；说明/数据证据存 Outbox metadata，不得污染 role capability 的 exact `parameters` schema。
- `issuer_uid` 从受信 host profile 绑定；字段/球员/教练/球队标识必须为当前世界线的已核验身份；UI 名称和猜测玩家ID不能成为唯一事实。
- 某决策修改期间需要替换目标，可对旧意图打 `SUPERSEDED` 并新增意图，保留变更事件；禁止原地覆盖已经进入执行窗口的记录。
- 同对象同字段冲突的不同目标值：**BLOCKED_CONFLICT_WAIT_ROLE_DECISION**，不按最后写入覆盖。完全同值同语义可由 existing aggregator 识别 coalesced aliases，且需保留两个决策来源与每个 issuer 的原始回执。不同意图之间依赖检查应保持。
- 没有匹配 Native 能力、已决定但当前仍不支持实机的动作：允许记录为 `UNSUPPORTED_PENDING`/ `NOT_EXECUTED`，不可静默丢弃或自动降级为不相干 Native action。
- 状态（高层）：`COLLECTING → SEALED → PREFLIGHTED → EXECUTING → VERIFIED_COMPLETE`；异常状态 `CONFLICTED/CONTEXT_STALE/STOPPED_PARTIAL/UNKNOWN_LOCKED`。每个状态转换要明确谁能触发、需要何种证据；没有 Host seal 不执行。

**决策完成触发 seal**：
1. host 结束当轮决策，运行 `seal(cycle_id, expected_revision)`，在事务中冻结 RoleActionBatch，固化全部已决定意图与来源、上下文、可执行/不可执行范围、唯一 `sealed_digest`；seal 后拒绝追加/覆盖，下一轮另建 cycle。
2. 使用 `ExecutionAggregator.plan` 对角色范围/phase grants/同字段资源冲突/依赖做统一预检；对不能执行的内容返回具体阻断清单，**禁止“只把可执行项执行了，其他悄悄丢掉”**。
3. 根据支持的当前 field action 实现极薄且纯函数的 `RoleBatch → BulkBatch` 适配器：角色 requirement `action_id` 与 Native canonical `action_id` 分开；**严格使用 role_capabilities 的 mapping 和 parameter schema**，不能把角色显示名称或策略概念词直接当 `field_id`。
4. 执行前 fresh snapshot / live Getter / game_build 和 save/epoch 再核验。原 `source_snapshot_ref` 是决策依据，不一定仍是当前 Getter 的 `expected_before`；如字段变动、球员转队或 roster 改变，返回 `CONTEXT_STALE / CAS_MISMATCH` 给决策方，**不能擅自“更新旧值继续写”**。
5. 只把已授权、确认为同一 Native 族且本次 live 能力足够成熟的项送给 `BulkBatchPlanner` / `BoundedSessionExecutor`。交易、签约、教练 Apply 等**不能因现有 100项倾向实测而自动升级**；适合 role dispatch 的动作沿用 `NativeActionDispatcher` 或保持 pending，不做错误分组。
6. 结果回收：严格校验本次 batch/chunk/intent digest、Getter-before/after、unaltered_fields_check 和独立 readback；每个原始决策意图产生一个 `VERIFIED_SUCCESS/NOOP/REJECTED/NOT_EXECUTED/UNKNOWN` 对应状态，任何 UNKNOWN 必须保留旧 claim+资源锁，不自动补偿重放。成功后的事实应由 WorldData 新 snapshot 后续读回确认，而非把执行回执直接伪装成已采集的历史游戏事实。
7. Outbox 只向下一轮角色/GM 决策暴露 **简洁的 outcome summary + 单项异常清单 + evidence refs**，不要强迫模型每次读取上万条原始 JSON。

## 4. 自动收据完整性：只开发**一个**可复用验证器

`validate_100_receipts.py` 已在本轮100项实测使用，固定交付对照为：
- 7 chunk、100 unique intents、100 SUCCESS_APPLIED、0 UNKNOWN；
- 新 REA 会话独立 readback 100/100；
- 实机 Setter 批次约 10.30–10.32s（各计时层不同），不说明存档已在退出后持久化。

但已观察到两项可证源码缺口（须修成通用脚本而非每次人工审查）：
- 该验证器在部分分支核对 `actual_before/actual_after`，而真实收据字段是 `getter_before/getter_after`；用 `if ... is not None` 跳过缺字段可能把不完整成功证据当通过；
- Raw REA evidence 主要做 chunk 消息数量与存在性检查，没有严查每个 chunk/batch/save/action/digest、精确 intent IDs 集合、Getter/Setter 值与 `unaltered_fields_check`，且 UNKNOWN 的名字可能是 `UNKNOWN_EXECUTION_OUTCOME` 而不只是 `UNKNOWN`。

**实施**：把验证逻辑封装为 `validate_batch_execution(batch, chunks, raw_messages, receipts, independent_readback)`，从实际注册的 schema 读取字段名，缺字段必须 fail-closed；每个 chunk、intent、字段和效果可复算。独立验证器可以读取旧100条真实收据做离线回归，但绝不能为此再次连接 NBA2K22 Setter。

## 5. 验收门和最小验证

- G1 角色输入：同一 cycle 支持逐条追加、列表、撤销/替代（仅未封存），崩溃恢复；1k/10k 离线规模。
- G2 Context：world/save/generation/season/phase/snapshot/catalog 全部绑定；跨 save/epoch、重用 intent_id 不同 payload 拒绝。
- G3 Roles：使用已有 host-authenticated identity/phase grant；GM、Coach、Player 权限隔离，模型 JSON 不能自授予。
- G4 Conflict & dependency：同字段异值显式冲突、同值 alias 保留、缺依赖/循环/交易协议等不可偷偷忽略。
- G5 Seal：不可变 RoleActionBatch + sealed hash，重复 seal 幂等且同 revision，seal 后任何改动拒绝。
- G6 Bridge：能将已有认证 Player 倾向意图转为 BulkBatch 精确一致；其他 Native families 标记 unsupported/单独 dispatcher，不伪造已认证场景。
- G7 Receipts：用固定100项真实执行收据**离线**独立复核100/100以及故障注入（错 digest、错人、重复 Chunk、缺 Getter、混入 UNKNOWN、uncertain readback）并全部 fail-closed。
- G8 Recovery：程序重启后可恢复 sealed outbox 和关联 Journal，不重复已经成功/UNKNOWN 的动作；不能混淆“未执行”与“执行未知”。
- G9 Closed-loop：最少模拟 GM + Coach 决策并持续 append → seal → plan → Fake 执行 → validate → feedback；已禁用 live action 要显示 `NOT_EXECUTED`，不是假成功。
- G10 OS observability：真实循环日志、模型身份、精确 SHA、测试与性能收据，可从事件/执行回执复算；任何界外真实游戏写入/存档操作都是 STOP。

推荐 CLI/API：`open_cycle / add_intent / supersede_intent / inspect / seal / preflight / execute_authorized / show_outcomes`。执行入口必须复用已有批准+运行环境核验，不因 CLI 名字写 authorized 就无条件开真实写入。CLI/接口是薄包装，禁止用长期服务或另一个大框架。

## 6. 允许修改和停止

允许新增 `decision_outbox.py`、`decision_batch_bridge.py`、`decision_outbox_cli.py`、通用 `validate_batch_execution.py`、必要测试及本任务 Run 文件；`validate_100_receipts.py` 可以提供兼容薄包装。既有 `role_batches.py / bulk_executor.py / bounded_session_transport.py / role_capabilities.py / registry.py` 默认为**只读可调用**；如发现核心接口阻断，先记录最小影响再提出有界修改，不自行重写它们。WorldData 数据源与 Core OS 不修改。用户已接受100项10秒左右，不在本任务里追求提速。

交付：可运行单文件 Outbox、抽象对象/生命周期/schema、Role→Bulk 纯适配、自动回执核验、离线端到端例子、1k/10k 离线压测、准确模型/Loop/测试收据、最终完整 Git SHA。**Human 当前未请求本任务重新进行现场写入**；不能把旧100项目标再写一次或用原任务授权无限重试。

最终目标是 `OFFLINE_DECISION_TO_BATCH_EXECUTION_CLOSED_LOOP_VERIFIED`，真实多角色自动游戏闭环需在其对应 Native 能力与明确场景授权下逐步认证；不能将100条 Player 倾向能力扩展成所有 GM/Coach 动作均成功。
