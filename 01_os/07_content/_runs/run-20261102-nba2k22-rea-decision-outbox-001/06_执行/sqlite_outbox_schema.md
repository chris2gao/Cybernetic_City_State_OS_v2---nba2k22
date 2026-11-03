# SQLite Decision Outbox Schema & Architecture Specification

**任务 ID**: `NBA2K22-REA-DECISION-OUTBOX-20261102-001`  
**模块路径**: `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/decision_outbox.py`  
**存储引擎**: SQLite 3 with WAL (Write-Ahead Logging) and foreign key constraints enabled  

---

## 1. 架构定位与职责边界

`DecisionOutbox` 是 NBA2K22 REA 体系中专用于角色决策阶段的**轻量持久化意图箱**与生命周期管理容器：
- **存前不存后**：Outbox 负责存储角色决策意图（Why、Who、When、What）、关联依据与封存批次；执行阶段的 Native 调用回执与 UNKNOWN 锁由现有的 `ExecutionJournal` 负责，两者通过 `(cycle_id, intent_id, batch_id, plan_digest)` 形成严格关联与闭环对账。
- **角色安全屏障**：角色不能自我声明权限。所有意图提交必须由受信 Host 注入 `RoleCapabilityProfile` 和当前上下文 `phase_grants` 进行逐条认证。
- **单调递增生命周期**：
  ```
  COLLECTING (Draft / Supersede / Cancel / Conflict Check)
      ↓ seal_cycle() (Immutable RoleActionBatch)
    SEALED (Revision CAS & Deterministic Sealed Digest)
      ↓ Bridge to BulkBatch & Execute
  COMPLETED / STOPPED_PARTIAL / UNKNOWN_LOCKED (Closed-loop Feedback)
  ```

---

## 2. 关系表结构设计

### 2.1 表 `decision_cycles`（决策周期主表）

| 列名 | 数据类型 | 约束 | 语义与设计说明 |
| :--- | :--- | :--- | :--- |
| `cycle_id` | TEXT | PRIMARY KEY | 决策周期的全局唯一标识（如 `CYCLE-20261102-001`） |
| `context_json` | TEXT | NOT NULL | 绑定的 `BatchContext` 规范化 JSON 序列化字符串 |
| `context_digest` | TEXT | NOT NULL | `BatchContext` SHA256 哈希，杜绝静默篡改上下文 |
| `status` | TEXT | NOT NULL | `COLLECTING`、`SEALED`、`CONFLICTED`、`COMPLETED`、`UNKNOWN_LOCKED` |
| `revision` | INTEGER | NOT NULL DEFAULT 0 | 乐观并发控制与 CAS 递增修订版本号 |
| `sealed_batch_id`| TEXT | NULLABLE | 封存时赋予的 `RoleActionBatch` 聚合批次 ID |
| `sealed_digest` | TEXT | NULLABLE | 封存意图与上下文的不可变完整性 SHA256 哈希 |
| `created_at` | TEXT | NOT NULL | ISO 8601 UTC 创建时间戳 |
| `sealed_at` | TEXT | NULLABLE | ISO 8601 UTC 封存时间戳 |
| `updated_at` | TEXT | NOT NULL | ISO 8601 UTC 最近变更时间戳 |

### 2.2 表 `decision_intents`（决策意图表）

| 列名 | 数据类型 | 约束 | 语义与设计说明 |
| :--- | :--- | :--- | :--- |
| `intent_id` | TEXT | PRIMARY KEY | 意图唯一业务主键（如 `I-GM-001-MIL-TRD`） |
| `cycle_id` | TEXT | NOT NULL, FK | 外键关联 `decision_cycles(cycle_id)` |
| `issuer_uid` | TEXT | NOT NULL | 经受信 Host 验证的签发角色唯一 UID |
| `role_type` | TEXT | NOT NULL | 角色类型（`GM`、`COACH`、`PLAYER`、`WORLD_ADMIN`） |
| `action_id` | TEXT | NOT NULL | 角色能力需求动作标识（如 `PLAYER.EDIT.TENDENCY_BATCH`） |
| `parameters_json`| TEXT | NOT NULL | 严格规范化的参数 JSON 串（由 `ActionIntent` 保证） |
| `dependencies_json`|TEXT | NOT NULL DEFAULT '[]'| 依赖的前序意图 ID 数组（有序，无重复） |
| `agreement_ref` | TEXT | NULLABLE | 双方贸易或正式协议引用 ID |
| `source_evidence_ref`|TEXT | NOT NULL DEFAULT ''| 决策来源事实凭据引用 |
| `decision_reason`| TEXT | NOT NULL DEFAULT ''| 角色做此决策的业务/策略说明 |
| `target_resource_key`|TEXT| NOT NULL DEFAULT ''| 规范化的资源定位键（用于同字段碰撞检测） |
| `status` | TEXT | NOT NULL DEFAULT 'DRAFT'| `DRAFT`、`SUPERSEDED`、`CANCELLED`、`SEALED`、`SUCCESS`、`NOOP`、`FAILED`、`UNKNOWN`、`NOT_EXECUTED` |
| `supersedes_intent_id`|TEXT| NULLABLE | 追踪被此条替代的前序意图 ID |
| `outcome_reason`| TEXT | NOT NULL DEFAULT ''| 执行阶段回填的详细反馈原因 |
| `created_at` | TEXT | NOT NULL | ISO 8601 UTC 提交时间戳 |
| `updated_at` | TEXT | NOT NULL | ISO 8601 UTC 状态更新时间戳 |

### 2.3 表 `outbox_events`（只追加事件审计表）

| 列名 | 数据类型 | 约束 | 语义与设计说明 |
| :--- | :--- | :--- | :--- |
| `event_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 严格单调递增的事件流水号 |
| `cycle_id` | TEXT | NOT NULL, FK | 外键关联 `decision_cycles(cycle_id)` |
| `intent_id` | TEXT | NULLABLE | 关联意图 ID（若为周期级事件则为 NULL） |
| `event_type` | TEXT | NOT NULL | `CYCLE_OPENED`、`INTENT_ADDED`、`INTENT_SUPERSEDED`、`INTENT_CANCELLED`、`CYCLE_SEALED`、`RECEIPTS_ATTACHED` |
| `prev_state` | TEXT | NULLABLE | 变更前状态 |
| `new_state` | TEXT | NOT NULL | 变更后状态 |
| `revision` | INTEGER | NOT NULL | 发生变更时的周期修订版本号 |
| `payload_json` | TEXT | NOT NULL DEFAULT '{}'| 事件结构化元数据详情 |
| `timestamp` | TEXT | NOT NULL | ISO 8601 UTC 事件发生时间戳 |

---

## 3. 索引与性能保证

```sql
CREATE INDEX IF NOT EXISTS idx_intents_cycle ON decision_intents(cycle_id);
CREATE INDEX IF NOT EXISTS idx_intents_resource ON decision_intents(cycle_id, target_resource_key);
CREATE INDEX IF NOT EXISTS idx_intents_status ON decision_intents(cycle_id, status);
CREATE INDEX IF NOT EXISTS idx_events_cycle ON outbox_events(cycle_id);
```

- **WAL 模式保障**：并发写入时不阻塞只读查询。
- **万级性能支持**：单连接事务批量写入可在 100-300 ms 内完成万条记录的插入与事件追加，完全满足离线大规模决策模拟需求。
