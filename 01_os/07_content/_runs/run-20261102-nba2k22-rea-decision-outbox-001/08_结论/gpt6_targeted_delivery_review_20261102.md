# Decision Outbox · GPT-6 定向交付审核（只读源码复核，追加记录）

固定交付 SHA：`8b53b6bf278dfe1b5e0785d309d7290c654dce6c`；任务 `NBA2K22-REA-DECISION-OUTBOX-20261102-001`。
岗位：decision_architecture / GPT-6。
范围：GitHub 已提交代码、样例、测试文件与源报告的**只读静态复核**；未在本评估重新执行 pytest/SQLite/Node，没有连接 NBA2K22、没有新 Native 写入或存档操作。
Human 需求：不继续追逐已满意的100项约10秒性能；将 GM/教练/球员决定逐项放入标准容器、Seal、执行、读回、反馈；优先脚本自动化、避免新增体系复杂度。
结果等级：**OFFLINE_ARCHITECTURE_ACCEPTED; INTEGRATION_CORRECTNESS_BLOCKERS_OPEN**。保留当前实现，不撤销已提交的 65/65 执行者测试收据；但不能认定“多角色真实自动执行已安全闭环”。

## 一、真实完成的工程

- DecisionOutbox 实现 SQLite WAL 的 `decision_cycles, decision_intents, outbox_events` 和增量 `add/supersede/cancel/list/seal`；多轮只读/写读恢复及基本唯一主键约束。
- RoleActionBatch → BulkBatch 桥、明确 unsupported 分区、Fake 单 Session 执行与结果回填，具有实际离线端到端例子。
- 通用执行校验器能离线读取已有100-item金标准收据，并捕获部分摘要、值及 UNKNOWN 篡改。
- 原始10k benchmark 报 `0.37684s / 26536.3 intents/sec`；`loop_summary_validation.json` 则报 `0.38518s / 25961.9 intents/sec`，具体计时存在小幅不同。需用准确的各次测量/重跑来源解释，不作为架构阻断。
- `offline_end_to_end_receipts.json` 的示例：4 Native fields Fake SUCCESS，角色层 3 SUCCESS + 1 trade NOT_EXECUTED。示例 `validation_result.checks.manifest_game_build_valid=false` 但 `validation_passed=true`，不能将该验证器称为全面严格 fail-closed。

## 二、仅三组承重正确性问题

### B1 — 执行结果回填可将部分或不完整执行标记为 COMPLETED（高优先）

`decision_batch_bridge.py:map_receipts_to_outbox` 约305–325行：一个 Role ActionIntent 转成多个 BulkIntents 后，只要含 `SUCCESS_APPLIED` 且前面没有特殊失败状态，即可能返回整条 `SUCCESS_APPLIED`，即使同组另一个子意图 `NOT_EXECUTED/BLOCKED` 或缺失收据。没有与 `role_to_bulk_map` 所声明的精确子意图集合进行一一守恒。
`decision_outbox.py:record_execution_receipts` 约584–666行：接受调用方随意传入的 receipts；不核对 sealed 状态、sealed digest、batch/plan identity、所有原始意图/已验 receipt 的完整性，也未拒绝未知 intent 或重复同 intent；例如空 receipts 也能把 cycle 写成 `COMPLETED`；只有 NOT_EXECUTED 的 receipt 不计 has_failure，也会写成 COMPLETED。随后可重复调用并覆盖旧成功状态。
**最低修复**：只在回执已通过统一验证、sealed role/bulk 身份完全一致、每个原始 intent 的全部子项都有准确终态时，单次事务归档；任何 NOT_EXECUTED/BLOCKED/缺失不能标整条成功/全周期完成，UNKNOWN 始终独立保留；同 cycle 重复不同 payload 拒绝，不更新既有已执行状态。

### B2 — Supersede/Seal/Host 身份边界需小规模闭合（高优先）

`decision_outbox.py:supersede_intent` 约273–354行：仅核对 old intent 的 issuer 与操作 profile，一旦具备旧 intent 所有权，就不核验**新** `ActionIntent.issuer_uid` 是否等于 host profile、动作是否获该角色允许、phase_grants、新 target 是否在 team/player scope、或上下文是否仍一致。该分支可注入原来不允许的 ActionIntent，绕过 `add_intent` 的认证路径。
`decision_outbox_cli.py:cmd_add_intent/cmd_supersede_intent` 约29–80行从用户指定的 `--profile-file` 和 `--phase-grants-file` 直接反序列化并传入“受信 host”API，这仅是本地测试/可信 operator 接口，**不能称为真正宿主身份鉴别**。独立真实角色代理接入时需要受信 host，而不是让模型填写自己的角色凭证。
`decision_outbox.py:seal_cycle` 和 `add_intent` 在事务外获取 cycle revision/status，后面的 UPDATE 不含 `WHERE revision=expected AND status=COLLECTING`，存在并发 add/seal 竞态；`expected_revision` 也可省略。本次用户反对复杂锁，最小 SQLite `BEGIN IMMEDIATE + WHERE revision/status CAS` 足矣，不开发分布式锁。
**最低修复**：`supersede` 重用与 `add_intent` 完全相同的受信 host 校验；CLI 明确限本地人工/测试或通过真正 Host profile provider；各 DRAFT→SEALED 状态转换采用一个事务里的 revision CAS。

### B3 — 通用回执校验器仍非严格 fail-closed（高优先）

`validate_batch_execution.py` 约118–235行仅校验收据条数和缺失 ID，未检查 `receipt_ids - planned_ids`；未逐条绑定原批次 `team_id/player_id/field_id/expected_before/value`。成功结果缺 `expected_before/requested` 时校验逻辑会跳过；`unaltered_fields_check` 字段缺失不失败。Raw Chunk 只验数量、可选 plan digest 与 outcome，不验证 chunk_id/chunk_digest、action_id、batch/save 身份、重复/错位 chunk 与内部完整 intent 集合。独立 readback 只验汇总标志，没有逐人按 identity 核对。
以上都可能使构造的不对应收据返回 `validation_passed=true`；`manifest_game_build_valid=false` 但 validation_passed=true 是已提交的端到端示例。
**最低修复**：围绕已有 Batch/Planner 生成 expected chunk/intent maps，严格验证 raw messages 与 Journal 全集 exact match、强制所有 SUCCESS 的 Getter-before/after、before/target、unaltered==true 和对象身份一致；independent readback 按对象/字段逐条核对；缺关键证据失败。增加 7–10 个针对性负例即可，不需要新执行器。

## 三、范围和成熟度边界

`DecisionBatchBridge.SUPPORTED_NATIVE_ACTIONS` 包含 Player attributes、Coach settings，但当前100项实机验证只认证 Player `SHOT_TENDENCY`，不能把 Fake Coach/attributes 完成当成已具备真实 Native 执行资格。
`decision_batch_bridge._translate_action` 在部分输入缺 `team_id`、`expected_before` 时默认填 `0`，不符合“身份和 CAS 必须源于准确证据”的闭环原则；应缺值拒绝或标 `UNSUPPORTED/CONTEXT_REQUIRED`，而不是猜默认值。
`DecisionBatchBridge.bridge_batch` 对 `batch_plan.issues` 仍可能生成可执行 partial BulkBatch；当前“已明确标记 unsupported”是好的，但是需要让 host 明确选择部分执行策略，不能直接根据一个 `has_executable_batch` 把剩余内容当成全计划获准。
`decision_outbox_cli.py` 目前暴露 open/add/supersede/inspect/seal/show-outcomes；它并没有一键 `preflight → execute_authorized → verified_feedback` 的真实生产入口。真实场景需要后续与 Host/REA 已批准运行流程连接，本交付属于**离线候选**。

## 四、验收建议与修复范围

- **架构保留并认可本阶段工程进展；条件性接受离线原型**。无需重做容器、再建新数据库或进行新的100项实机修改。
- 开展一次**同任务内有界逻辑修复**，只涉及 `decision_outbox.py`、`decision_batch_bridge.py`、`validate_batch_execution.py`、对应测试及 CLI 身份标识，优先 B1→B2→B3。
- 通过验收标准：1) 2-field intent 1成功1失败/缺失 → 绝不整体成功；2) 空/缺/重/未知回执 → cycle 不完成；3) 非法替代与并发 Seal 冲突被拒；4) 100条金标准离线复核依旧 PASS，而制造错字段、错 Chunk/digest、假 Getter、伪 readback 必须 FAIL；5) GM/Coach/Player Fake 闭环仍可复算，unsupported 不被记作完成。
- 用户已明确偏好少审核少复杂度，本报告不启动新的研究领域、不是“原 REA 批量执行器的又一轮整改”，仅补此次容器最关键的逻辑门。
- 本审核没有更改游戏、存档、Native 设置或历史证据，也没有合并 master；若 Human 决定立即采用该容器作为长期外挂机制，应先完成上述三组小修复。
