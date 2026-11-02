# NBA2K22 REA · 标准化决策容器与批量执行闭环工程报告

**任务 ID**：`NBA2K22-REA-DECISION-OUTBOX-20261102-001`  
**OS 岗位**：`execution`  
**执行模型**：`Gemini 2.5 Pro (execution)`  
**分支**：`task/nba2k22-rea-decision-outbox-20261102`  
**基线 SHA**：`80955e8ed501a9ab57fc4b363646b525c0748a98`  
**交付状态**：`OFFLINE_DECISION_TO_BATCH_EXECUTION_CLOSED_LOOP_VERIFIED`  
**完成时间**：2026-11-02 04:50:00 UTC  

---

## 1. 任务背景与核心目标

Human 在前期 100 项实机基准测试（`NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001`）中已确认单次会话 10.318 秒的修改性能完全满足当前工程预期，明确要求停止对实机执行速度的单一追求，转入**角色日常决策标准化容器与批量执行闭环**的系统化构建。

本任务的核心工程目标：
1. **轻量持久决策容器（Decision Outbox）**：采用 SQLite WAL 模式与仅追加（Append-Only）事件日志，支持 GM、Coach、Player 在决策阶段持续逐条追加、撤销、替代 `ActionIntent`，并耐受系统崩溃与进程重启。
2. **确定性封存与 CAS 校验**：决策窗口关闭时触发原子封存（`seal_cycle`），生成不可变 `RoleActionBatch`、确定性 `sealed_digest` 与版本 CAS 控制，封存后严格禁止原地篡改。
3. **角色意图向 Native 批次的纯函数桥接（DecisionBatchBridge）**：复用现有 `ExecutionAggregator`，将支持的球员倾向（`PLAYER_PATCH_TENDENCIES`）与教练策略（`COACH_SET_KNOWN_CURRENT_SETTINGS`）转换为粒度明确的 `BulkIntentItem`，并将交易、签约等尚不具备批量 Native 能力的意图干净隔离为 `NOT_EXECUTED`（原因 `UNSUPPORTED_OR_EXTERNAL`），绝不伪造执行成功。
4. **通用 Fail-Closed 执行回执校验器（validate_batch_execution）**：重构并泛化既有校验逻辑，全面核验 Batch Digest、Chunk 摘要、Getter 前后值契约、Claim 锁定状态与守恒律；基于前序 100 项实机金标准收据进行 100% 离线复核与 5 类故障注入测试。
5. **多角色端到端离线闭环反馈**：连接 `BoundedSessionExecutor`（离线 Fake 传输层），执行结果逐项回填 Outbox，向下一轮角色决策暴露清晰的 `outcome_summary`（成功、失败、未执行及 UNKNOWN 清单）。
6. **严格执行权限约束**：本次任务严格禁止连接 NBA2K22 游戏进程、禁止调用真实 Native Setter、禁止篡改存档或触发 WorldData 采集。

---

## 2. 系统架构设计

```
[ GM / Coach / Player Roles ]
          │
          ▼ (add_intent / supersede_intent)
┌────────────────────────────────────────────────────────┐
│                   DECISION OUTBOX                      │
│  - decision_cycles (Context binding, revision CAS)     │
│  - decision_intents (DRAFT, SUPERSEDED, CANCELLED)     │
│  - outbox_events (Append-only event audit trail)       │
└────────────────────────────────────────────────────────┘
          │
          ▼ seal_cycle(cycle_id)
┌────────────────────────────────────────────────────────┐
│             SEALED RoleActionBatch                     │
│  (Immutable, sealed_digest, batch context frozen)      │
└────────────────────────────────────────────────────────┘
          │
          ▼ DecisionBatchBridge.bridge_batch(...)
┌──────────────────────────────────────┬─────────────────┐
│     Supported Native BulkBatch       │   Unsupported   │
│  - PLAYER_PATCH_TENDENCIES           │   Intents       │
│  - COACH_SET_KNOWN_CURRENT_SETTINGS  │   (GM.TRADE...) │
└──────────────────┬───────────────────┴────────┬────────┘
                   │                            │
                   ▼ (Fake REA Transport)       │
┌──────────────────────────────────────┐        │
│       BoundedSessionExecutor         │        │
│  - Single Frida Attach Session       │        │
│  - Claim-before-Setter Hard Guard    │        │
│  - Fail-stop on CAS mismatch         │        │
└──────────────────┬───────────────────┘        │
                   │                            │
                   ▼ ItemReceipts               │
┌────────────────────────────────────────────────────────┐
│         validate_batch_execution (Fail-Closed)         │
│  - Digest check / Getter Before & After / Conservation │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼ DecisionBatchBridge.map_receipts_to_outbox(...)
┌────────────────────────────────────────────────────────┐
│               OUTBOX CLOSED-LOOP FEEDBACK              │
│  - record_execution_receipts(...)                      │
│  - get_outcome_summary(...) -> GM/Coach Next Cycle     │
└────────────────────────────────────────────────────────┘
```

---

## 3. 十项验收门（G1–G10）达成证据

| 门禁 ID | 验收项名称 | 检查标准 | 验证结论与证据 |
|:---|:---|:---|:---|
| **G1** | 角色草稿意图输入与生命周期 | 支持同一 Cycle 逐条追加、列表、替代（SUPERSEDE）、撤销（CANCEL）、崩溃重启恢复；封存后禁止修改 | **PASSED**：`test_g1_draft_add_supersede_cancel_and_restart` 验证追加、替代事件生成与重启后不可篡改。 |
| **G2** | 上下文与世界线严格绑定 | `world_id`, `save_id`, `generation_id`, `season_id`, `phase`, `snapshot_ref`, `catalog_version` 强一致；跨上下文或篡改 Payload 拒绝 | **PASSED**：`test_g2_world_save_season_phase_binding` 验证不同 Save/Epoch 及重复 ID 不同 Payload 立即抛出 `ROLE_CONTEXT_MISMATCH` 与 `INTENT_ID_REUSED`。 |
| **G3** | 角色身份与权限隔离 | 复用 Host-authenticated Identity 与 Phase Grants；模型 JSON 无法自行提权或伪造发行者 | **PASSED**：`test_g3_role_credentials_and_phase_grants` 验证非授权 issuer_uid、空 Phase Grants 以及越界 Team Scope 全部被拒绝。 |
| **G4** | 资源冲突与依赖链检测 | 同一资源不同目标值判定冲突（`CONTRADICTORY_VALUES`）阻断封存；缺失依赖与循环依赖显式告警 | **PASSED**：`test_g4_collision_and_dependency_detection` 验证同一球员同字段不同倾向值时阻断封存，缺失依赖被捕获。 |
| **G5** | 不可变批次封存与 CAS | 封存生成不可变 `RoleActionBatch`、确定性 `sealed_digest`，支持 Revision CAS，重复封存具备幂等性 | **PASSED**：`test_g5_immutable_seal_and_revision_cas` 验证 CAS 校验、幂等重封存与封存后追加拦截。 |
| **G6** | 纯函数角色到 Native 桥接 | 准确映射 `PLAYER.EDIT.TENDENCY_BATCH` 与 `COACH.STRATEGY.RUN_PLAY`；不支持动作（如 `GM.TRADE.MIXED`）显式隔离为 pending | **PASSED**：`test_decision_batch_bridge.py`（3/3）验证双向映射，未支持动作保留在 `unsupported_intents`，绝不虚报成功。 |
| **G7** | 通用 Fail-Closed 校验器 | 100 项离线金标准收据（Mutation 与 No-op）100% 通过；Digest 篡改、缺 Getter、UNKNOWN 混入等 5 类故障注入全部 fail-closed | **PASSED**：`test_validate_batch_execution.py`（7/7）离线重放全部通过，所有注入异常均成功拦截。 |
| **G8** | 故障安全与 UNKNOWN 锁保护 | 进程重启后可完整恢复；遇到 UNKNOWN 状态时锁定对应资源，防止后续批次静默重试该动作 | **PASSED**：`test_g8_unknown_outcome_locks_resource_and_prevents_replay` 验证发生 UNKNOWN 后 Cycle 锁定，次轮重试被 `BLOCKED_BY_PRIOR_UNKNOWN_CLAIM` 拦截。 |
| **G9** | 离线端到端多角色闭环 | GM + Coach 决策持续追加 → 封存 → 桥接 → Fake 执行 → 严格校验 → 回执反馈入库，不支持动作明确标示 `NOT_EXECUTED` | **PASSED**：`test_g9_full_offline_decision_to_execution_closed_loop` 验证完整闭环，产出 `offline_end_to_end_receipts.json`。 |
| **G10** | 性能压测与真实工程溯源 | 1k 与 10k 离线插入吞吐实测；真实记录模型 `Gemini 2.5 Pro (execution)`；全量 65 项原生测试无回归 | **PASSED**：10k 意图插入仅耗时 0.385 秒（~25,961 条/秒）；全量 65 项测试 100% 通过（耗时 11.05s）。 |

---

## 4. 关键压测数据与性能对比

在 SQLite WAL 模式下执行批量参数插入基准压测（产物位于 `07_测试执行/10k_outbox_benchmark.json`）：

| 压测规模 | 耗时 (秒) | 吞吐量 (条意图 / 秒) | 存储与事务模式 |
|:---|:---|:---|:---|
| **1,000 项 Intent 批量插入** | 0.03864 s | **25,877.0 条/秒** | 单事务 + WAL + Append-Only Event |
| **10,000 项 Intent 批量插入** | 0.38518 s | **25,961.9 条/秒** | 单事务 + WAL + Append-Only Event |

> **结论**：本地轻量 SQLite 容器性能极其优异，单秒可处理逾 2.5 万项意图，相比多会话网络服务或分布式队列更加轻量、零依赖且具备原生 ACID 事务保障。

---

## 5. 端到端离线闭环执行收据核验（Gate G9）

在 `07_测试执行/offline_end_to_end_receipts.json` 中完整记录了 GM 与 Coach 混合意图的闭环测试结果：
- **Cycle ID**: `CYCLE-E2E-CLOSED-LOOP-001`
- **Sealed Batch ID**: `ROLE-BATCH-CYCLE-E2E-CLOSED-LOOP-001`
- **Sealed Digest**: `fece2a85031e2f04dbdd501caa44291307754414963ea31f98e69c37ca96e29f`
- **Native Bulk Plan Digest**: `91f133e6aa2421be68d31acb523a98ece44286b31e9dfb787fdd472392dd68f2`
- **意图构成与执行结果**：
  1. `I-GM-GIANNIS-TENDENCIES` (`PLAYER.EDIT.TENDENCY_BATCH`, 球员 1607): 拆分为 2 个原生字段修改，全部成功（`SUCCESS_APPLIED`）。
  2. `I-GM-LILLARD-TENDENCIES` (`PLAYER.EDIT.TENDENCY_BATCH`, 球员 2459): 1 个原生字段修改，成功（`SUCCESS_APPLIED`）。
  3. `I-COACH-RUN-PLAY` (`COACH.STRATEGY.RUN_PLAY`, 球队 1): 1 个教练策略设置，成功（`SUCCESS_APPLIED`）。
  4. `I-GM-TRADE-PROPOSAL` (`GM.TRADE.MIXED`): 不支持批量 Native 执行，正确分区并反馈为 `NOT_EXECUTED`（原因 `EXACT_TRADE_AGREEMENT_REQUIRED`）。
- **守恒律核验**：
  - 计划意图总数：4
  - 成功意图：3
  - 未执行（不支持）意图：1
  - UNKNOWN 意图：0
  - 守恒律检验：`4 == 3 + 1 + 0`，完全满足。

---

## 6. 最终交付产物清单

1. **核心工程实现**：
   - `decision_outbox.py`：SQLite WAL 决策容器、生命周期流转、冲突与依赖拓扑检查、原子封存。
   - `decision_batch_bridge.py`：角色批次向 Native 批次桥接器、未支持意图隔离、回执聚合与反向映射。
   - `decision_outbox_cli.py`：面向 Host 与自动化测试的轻量命令行接口。
   - `validate_batch_execution.py`：通用 Fail-Closed 批次执行校验器。
2. **测试与回归套件**：
   - `tests/test_decision_outbox.py`（6/6 PASSED）
   - `tests/test_decision_batch_bridge.py`（3/3 PASSED）
   - `tests/test_validate_batch_execution.py`（7/7 PASSED）
   - `tests/test_offline_closed_loop.py`（3/3 PASSED）
   - 全量回归测试：65/65 PASSED（耗时 11.05 秒）。
3. **元数据与审计凭证**（`01_os/07_content/_runs/run-20261102-nba2k22-rea-decision-outbox-001/`）：
   - `06_执行/sqlite_outbox_schema.md`：详细数据库表结构、外键与事件字典。
   - `06_执行/loop_iterations.jsonl`：5 个工程迭代循环的完整实证日志。
   - `06_执行/loop_summary_validation.json`：由原始日志复算的门禁核验摘要。
   - `07_测试执行/10k_outbox_benchmark.json`：1k/10k 吞吐性能压测数据。
   - `07_测试执行/offline_end_to_end_receipts.json`：端到端离线闭环执行收据与校验结果。
   - `08_结论/decision_outbox_report.md`：本综合工程报告。
   - `08_结论/completion_pointer.md`：交付索引指引。
   - `run.yml`：状态更新为 `COMPLETED`，如实登记模型 `Gemini 2.5 Pro (execution)`。
