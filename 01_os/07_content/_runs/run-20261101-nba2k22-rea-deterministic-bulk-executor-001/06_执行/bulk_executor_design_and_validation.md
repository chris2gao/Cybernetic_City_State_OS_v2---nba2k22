# NBA2K22 REA · 确定性批量 Native 自动化执行器系统设计与验证报告

**文档 ID**：`NBA2K22-REA-BULK-EXECUTOR-DESIGN-VALIDATION-20261101`  
**所属 Run**：`run-20261101-nba2k22-rea-deterministic-bulk-executor-001`  
**任务 ID**：`NBA2K22-REA-DETERMINISTIC-BULK-EXECUTOR-20261101-001`  
**基线 SHA**：`3bbcbcaad98db6b9492ed915ce93aac076550c4f`  
**执行角色**：`execution` (Gemini 2.5 Pro)  
**状态判定**：`OFFLINE_BATCH_ENGINE_READY_FOR_GRADED_LIVE_TEST`

---

## 一、系统架构与执行模型

本系统设计旨在为 NBA2K22 提供一套确定性、参数驱动、可扩展至万级字段的大规模 Native 自动化执行工具集，彻底解决单字段修改时反复人工排障、频繁启动 Frida 附加、缺乏写前 CAS 校验与单字段独立收据的核心瓶颈。

### 1.1 总体架构流图

```
+-----------------------------------------------------------------------------------+
| 1. 参数输入层 (JSON / JSONL)                                                      |
|    - Batch Header: batch_id, save_instance_id, game_build_sha256, authorization_ref  |
|    - Intents: intent_id, action_id, team_id, player_id, field_id, expected_before, val|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. 静态预检与规则校验器 (BulkBatchPlanner.validate)                              |
|    - 校验构建一致性 (game_build_sha256 == contracts.BUILD: 1727ad72...)          |
|    - 校验字段族与值域 (Tendencies: 0..100, Attributes: 25..99, Coach: 0..100)     |
|    - 校验未支持范畴 (自由球员、未绑定槽位徽章、裸内存写 -> FAIL-CLOSED)          |
|    - 校验相互矛盾意图 (同一目标多值冲突) 与缺失依赖                               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. 受控分块调度器 (BulkBatchPlanner.plan)                                         |
|    - 按 team_id 聚合，划分为受控小块 (默认 25..50 项/块)                          |
|    - 控制单块 Native 调用预算 <= 200 次，主线程时间预算 <= 5,000 ms               |
|    - 计算批次与计划确定性哈希绑定 (plan_digest = SHA256(header + chunks))          |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. 分块运行时引擎 (BulkFridaScriptCompiler & Bounded Frida Transport)            |
|    - 单块单会话：1 次 Frida Attach + 1 次主窗口 PeekMessageA Hook                 |
|    - 块内串行执行 Native Getter (0x978360) -> CAS 比对 -> Setter (0x990a10)       |
|    - 遇 CAS 偏差或异常立即中断块 (Prefix Preservation)，严禁逆向重试              |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. 持久化日志与收据对账层 (ExecutionJournal & Reconciler)                        |
|    - 记录 batch_manifest.json 与 append-only receipts.jsonl                       |
|    - 强制执行守恒律断言: N_planned = N_success + N_noop + N_blocked + N_unk + N_not_exec|
|    - UNKNOWN 状态资源锁定，仅支持独立外部证据定向消除 (reconcile)                 |
+-----------------------------------------------------------------------------------+
```

---

## 二、核心机制与关键技术突破

### 2.1 硬 CAS（Compare-And-Swap）写前断言与 No-op 识别

在原有 `player_stats.js` 中，代码仅断言 Getter 读出的旧值在有效整数范围内（$[0, 255]$ 或 $[25, 99]$），但**完全没有比对调用方声明的基线预期值**。这在多批次或日历推进后极易导致脏写（Dirty Write）。

批量引擎强制执行三态硬 CAS 逻辑：

1. **写前比对**：
   $$V_{\text{real}} = \text{CallNativeGetter}(\text{player}, \text{index})$$
2. **三态决策**：
   - **分支 1（CAS 匹配且需修改）**：若 $V_{\text{real}} == V_{\text{expected\_before}} \land V_{\text{target}} \neq V_{\text{expected\_before}}$：
     - 调用 Native UI Setter（`0x990a10`）；
     - 立即调用 Native UI Getter（`0x978360`）验证 $V_{\text{after}} == V_{\text{target}}$；
     - 读取物理内存字节验证原生公式映射（倾向为 $V$，属性为 $3V - 75$）；
     - 校验 156 字节邻域未请求字段完全未被破坏；
     - 记录 `SUCCESS_APPLIED`。
   - **分支 2（已是目标值，No-op）**：若 $V_{\text{real}} == V_{\text{expected\_before}} \land V_{\text{target}} == V_{\text{expected\_before}}$：
     - 严禁调用 Setter；
     - 记录 `UNCHANGED_ALREADY_TARGET`，验证未修改字段，零写入安全通过。
   - **分支 3（CAS 偏差，环境被动）**：若 $V_{\text{real}} \neq V_{\text{expected\_before}}$：
     - 严禁调用 Setter；
     - 记录 `CAS_EXPECTED_BEFORE_MISMATCH`；
     - 中断当前分块后续所有意图，标记为 `NOT_EXECUTED`，防止级联破坏。

### 2.2 受控分块（Bounded Chunking）彻底解决 Frida 启动瓶颈

在单字段执行模式下，每次操作启动 1 次 Frida 注入与分离，耗时约 4 秒。若直接执行 10,000 项操作，将耗费 11.1 小时。

通过受控分块引擎：
- 10,000 项操作按球队与球员聚合，拆分为 201 个分块（每块 $\le 50$ 项）；
- 每个分块仅需启动 1 次 Frida 会话、1 次 GUI 消息挂钩，在游戏主线程中毫秒级串行完成 50 次 Getter/Setter 写入；
- 基础设施会话次数由 10,000 次降至 201 次，**开销降低 97.99%**，总耗时由 11 小时缩短至约 13 分钟。

### 2.3 严格守恒律与故障前缀保留（Prefix Preservation）

系统强制断言执行守恒律：

$$N_{\text{planned}} = N_{\text{executed\_success}} + N_{\text{noop}} + N_{\text{blocked}} + N_{\text{unknown}} + N_{\text{not\_executed}}$$

- 若某分块在第 $k$ 项遭遇意外崩溃或超时：
  - 前 $k-1$ 项已验证的收据完好持久化（`SUCCESS_APPLIED` 或 `UNCHANGED_ALREADY_TARGET`）；
  - 第 $k$ 项标记为 `UNKNOWN_EXECUTION_OUTCOME`，锁定目标资源槽位，严禁盲目自动重放；
  - 第 $k+1 \dots N$ 项标记为 `NOT_EXECUTED`。

---

## 三、10,000 项大规模合成压力测试与性能基准

在 Windows 10 本地环境（Intel64, Python 3.14.6, Node v24.22.1）上，执行了涵盖 30 支球队、450 名球员、99 项倾向与 53 项属性的 10,000 项合成基准压测：

### 3.1 真实基准性能指标

| 阶段 / 指标 | 实测数值 | 吞吐率 / 效率 | 判定 |
| :--- | :--- | :--- | :--- |
| 10,000 项生成与解析 | 60.40 ms | 165,562 items/sec | 极速 |
| 规则预检与 201 分块规划 | 33.78 ms | 296,033 items/sec | 极速 |
| 单分块 Frida JS 脚本编译 | 0.33 ms | 18,934 字节紧凑脚本 | 极速 |
| 全量模拟执行 (含 CAS 与状态迁移) | 144.49 ms | **69,210 ops/sec** | 极速 |
| **分块级延迟 (Chunk Latency)** | **p50: 0.71 ms** | **p95: 0.83 ms** | **p99: 0.95 ms** |
| **单意图延迟 (Item Latency)** | **p50: 0.014 ms** | **p95: 0.017 ms** | **p99: 0.019 ms** |

### 3.2 守恒律与故障注入验证

基准测试中注入了 150 项 No-op、2 处跨块 CAS 不匹配、1 处硬件崩溃/超时异常，最终真实核对结果为：

$$\begin{aligned}
N_{\text{planned}} &= 10,000 \\
N_{\text{success}} &= 9,825 \\
N_{\text{noop}} &= 150 \\
N_{\text{blocked}} &= 2 \\
N_{\text{unknown}} &= 1 \\
N_{\text{not\_executed}} &= 22 \\
\hline
\sum \text{Outcomes} &= 9825 + 150 + 2 + 1 + 22 = 10,000 \quad (\text{Strictly Conserved!})
\end{aligned}$$

---

## 四、单元与回归测试验证

自动化测试套件包含 10 项批量专用测试与 39 项角色/字段回归测试，共计 **49 项测试**：
- `test_bulk_executor.py`: 10/10 PASSED (0.43s)
- `test_role_batches.py`: 16/16 PASSED (1.45s)
- `test_role_capabilities.py`: 4/4 PASSED (0.32s)
- `test_player_stats.py`: 9/9 PASSED (1.48s)
- `test_player_editor_read.py`: 10/10 PASSED (2.42s)
- **总耗时**：7.50 秒，**通过率 100%（49/49）**，零回归。

---

## 五、CLI 命令行工具使用指南

批量执行器提供完整合规的命令行套件：

```powershell
# 1. 静态验证参数文件合规性 (检查值域、构建、未支持范畴、矛盾意图)
python bulk_executor.py validate data/bulk_samples/sample_player_tendencies_small.json

# 2. 模拟规划分块并输出摘要 (不触碰游戏或磁盘状态)
python bulk_executor.py dry-run data/bulk_samples/sample_player_tendencies_small.json --chunk-size 50

# 3. 编译指定分块的 Frida 注入脚本 (供审计与离线分析)
python bulk_executor.py compile data/bulk_samples/sample_player_tendencies_small.json --chunk-id chunk-0001-team-28 --out chunk_01.js

# 4. 离线合成执行并验证守恒律与收据生成
python bulk_executor.py offline-test data/bulk_samples/sample_player_tendencies_small.json --journal-dir ./test_journal

# 5. 审查已生成的执行收据统计
python bulk_executor.py inspect-receipt ./test_journal/receipts.jsonl

# 6. 使用外部观察证据对账 UNKNOWN 状态意图
python bulk_executor.py reconcile --journal-dir ./test_journal --intent-id INT-CRASH-001 --evidence ./evidence.json

# 7. 运行 10,000 项大规模基准压测
python bulk_executor.py benchmark --count 10000
```

---

## 六、未来渐进式实机小范围验证方案（Roadmap）

根据合同授权限制，**本工程任务仅完成离线工程开发与合成验证，未执行任何实机注入**。未来若 Human 批准开展实机验证，必须遵循以下逐级推进协议：

```
+-------------------------------------------------------------------------------------------------------+
| 阶段                     | 规模与目标                     | 准入前置条件                       | 验收通过标准           |
+--------------------------+--------------------------------+------------------------------------+------------------------+
| Stage 1: 单字段 CAS 回放 | Damian Lillard (UID 2459)      | Human 重新确认游戏 PID 与存盘状态； | Getter 读出 80，        |
|                          | SHOT_TENDENCY: 80 -> 80 (No-op)| 提交 plan_digest 并获单次授权。    | 确认 UNCHANGED_ALREADY_ |
|                          | 或 80 -> 82                    |                                    | TARGET 或回读 82。     |
+--------------------------+--------------------------------+------------------------------------+------------------------+
| Stage 2: 小规模受控组    | 1 名球员，2–5 项倾向/属性      | Stage 1 成功；提供明确 expected_   | 块内 5 项全部 SUCCESS， |
|                          | (如 Lillard 投篮+上篮倾向)     | before 基线值。                    | 156 字节邻域零破坏。   |
+--------------------------+--------------------------------+------------------------------------+------------------------+
| Stage 3: 单队花名册级    | 1 支球队 15 人，约 30–50 项字段| Stage 2 成功；                     | 单分块单次 Frida 附加， |
|                          | (开拓者全队投篮倾向校准)       | 验证单分块主线程耗时 < 100ms。     | 50 项全部读回一致。    |
+--------------------------+--------------------------------+------------------------------------+------------------------+
| Stage 4: 多队短分块      | 3–5 支球队，约 150 项字段      | Stage 3 成功；                     | 跨队分块调度稳定，     |
|                          | (多队核心球员倾向微调)         | 验证分块切换与内存指针隔离。       | 无游戏主线程假死。     |
+--------------------------+--------------------------------+------------------------------------+------------------------+
| Stage 5: WorldData 独立  | Human 触发 WorldData FULL 采集 | Stage 4 成功；由 Human 显式触发，  | WorldData player-skills|
| 闭环核对                 | 验证修改被独立采集管线识别     | 严禁 Agent 自动触发采集。          | 表读回值与修改值一致。 |
+-------------------------------------------------------------------------------------------------------+
```

> **最终安全红线**：
> 任何级别的实机写入，都必须以独立的 `plan_digest` 和具体字段列表向 Human 申请单次明确授权，**绝不通过一次笼统授权发起大规模实机写入**。
