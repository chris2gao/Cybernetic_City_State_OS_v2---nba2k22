# NBA2K22 REA · 批量原生执行器架构审查与耗时归因报告

**文档 ID**：`NBA2K22-REA-BULK-ARCH-INVENTORY-20261101`  
**所属 Run**：`run-20261101-nba2k22-rea-deterministic-bulk-executor-001`  
**任务 ID**：`NBA2K22-REA-DETERMINISTIC-BULK-EXECUTOR-20261101-001`  
**基线 SHA**：`3bbcbcaad98db6b9492ed915ce93aac076550c4f`  
**执行角色**：`execution` (Gemini 2.5 Pro)  
**环境**：Windows 10/Server x64, Python 3.14.6, Node.js v24.22.1, REA CLI 6.8.0, NBA2K22.exe (Build SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)

---

## 一、既有组件复用审查与能力边界

根据任务派发要求，本批量执行器严禁重新发明角色权限、数据库或脱离原生合约的自由写入器，必须全面复用并扩展既有经过实机与离线验证的组件。

### 1.1 组件复用矩阵

| 组件文件 | 既有能力 | 本轮复用方式 | 扩展/整改要点 |
| :--- | :--- | :--- | :--- |
| `research/rea_native_control/role_batches.py` | `RoleActionBatch`、`ActionIntent`、`BatchContext`、`ExecutionAggregator`、`ExecutionJournal`、资源锁、冲突检测、Stop-on-Unknown、At-most-once 调度。 | 作为核心批次编排、依赖拓扑排序和本地持久化 Journal 状态机。 | 优化针对万级意图的资源冲突检测算法（从 $O(N^2)$ 全量扫描优化为基于资源键的哈希索引分桶）；扩充 CAS（Compare-And-Swap）意图字段。 |
| `research/rea_native_control/role_capabilities.py` | 角色能力字典、需求映射、权限验证、角色范围（GM / COACH / SCOUT / WORLD_ADMIN）。 | 复用已有能力目录和字段族校验，确保角色不能越权发起未授权操作。 | 保持不变，拒绝在批量引擎中绕过角色约束。 |
| `research/rea_native_control/player_fields.py` | 99 项球员倾向（0–100）、54 项球员属性（25–99）、偏移表（0x41f–0x4ba）、属性字节编码算法（`val * 3 - 75`）、缓存标志位掩码。 | 作为字段合法性、值域合法性、Native Index 与物理内存偏移的唯一真理源。 | 引入批量字段批处理编译逻辑，支持将同一球员的多个倾向/属性合并为紧凑调用。 |
| `research/rea_native_control/transport.py` | `ReaCliTransport`、Frida 附加流程、PowerShell 调度子进程、`runner.log`、`evidence.json` 解析。 | 复用其与 REA CLI（`rea.mjs`）的集成协议与安全边界。 | **重大架构整改**：原有 `ReaCliTransport` 每个 Action 独立起一个目录、一个 PowerShell、一次 Frida 附加与 Detach。批量引擎必须引入**受控分块传输器（Chunked Transport）**，单次 Attach 执行 20–50 项 Native 修改，消除 98% 的进程创建与附加开销。 |
| `research/rea_native_control/runtime/player_stats.js` | 核心 Native Getter（`0x978360`）与 Setter（`0x990a10`）调度、156 字节邻域物理字节比对、缓存标志位验证、无自动重试。 | 复用其经过实机验证的原生 UI 函数调用调用链与安全断言。 | **核心缺陷修复**：原有代码仅校验旧值在 $[0, 255]$ 或 $[25, 99]$ 范围，**未比对调用方声明的 `expected_before`**！本轮增加硬 CAS 断言：旧值不符预期立即中断；旧值与目标值相同则标记 `UNCHANGED_ALREADY_TARGET`（No-op）跳过 Setter。 |
| `research/rea_native_control/runtime/gui_once.js` | Windows 主窗口与 GUI 线程定位、`PeekMessageA` 拦截注入、单次安全消息触发与超时保护（4000ms）。 | 复用其游戏 GUI 线程上下文安全调度机制。 | 将单 Action 触发扩展为**分块循环执行器**，单次进入游戏消息泵循环依次执行本分块所有 Native 调用，严格控制单次占用主线程时间 $< 100\text{ ms}$。 |
| `research/rea_native_control/validation_batch.py` | 静态批次验证套件、离线断言。 | 作为单元测试和回归测试的参考用例。 | 升级为万级合成测试套件。 |
| `world_data_prototype/calendar_sim_orchestrator.py` | WorldData 一键采集与日历推进调度、`FULL` 模式 20 族采集、`INCREMENTAL` 模式跳过逻辑。 | 用于未来闭环核对规约，明确独立采集触发条件。 | 明确：批量执行器本身**不自动触发采集**，只能由 Human 授权在后续独立步骤中触发 `FULL` 采集。 |

---

## 二、前次 Lillard 单字段实机执行 10 分钟耗时全景归因

在任务 `NBA2K22-REA-PHASE-A-READONLY-PREFLIGHT-20261101-001` 中，Human 授权了 Damian Lillard（UID 2459）`SHOT_TENDENCY` 95→80 的单字段实机修改。从启动排障到最终在游戏内存与 UI 中确认修改，总耗时约 10 分钟。

通过对 Gemini 本地运行时目录 `_runtime/18363b5a47524434a0bae629d9495fd2/` 中的 `runner.log`、`evidence.json`、`program.js` 以及 OS 执行日志的逐项只读审计，耗时真实分解如下：

```
+-------------------------------------------------------------------------------------------------------+
| 阶段                     | 耗时估算        | 性质         | 根本原因 / 瓶颈分析                            |
+--------------------------+-----------------+--------------+-----------------------------------------------+
| 1. 环境与脚本诊断        | ~4 分钟 (240s)  | 环境缺陷     | powershell.exe -NoProfile 下未加载 Utility     |
|                          |                 |              | 模块，导致 Get-FileHash 缺失报错 (Command-    |
|                          |                 |              | NotFoundException)，需定位并替换为 pwsh。      |
| 2. 窗口与线程句柄发现    | ~1 分钟 (60s)   | 运行时探测   | 枚举系统窗口并正则匹配 "NBA 2K22" 标题，确认  |
|                          |                 |              | PID 10404 与 GUI 线程 8536。                  |
| 3. Frida 附加与脚本注入  | ~2.5 秒 (2.5s)  | 基础设施耗时 | node rea.mjs 启动，Frida 注入游戏进程，分配   |
|                          |                 |              | 内存并编译 program.js (111 KB)。               |
| 4. 消息队列调度与进入    | ~150 毫秒 (0.15s)| 游戏线程同步 | PostMessage 触发 PeekMessageA 钩子回调。       |
| 5. 原生 Getter 预检      | ~20 毫秒 (0.02s)| 真实执行     | 调用 0x978360 读回 95，验证 156 字节内存。     |
| 6. 原生 Setter 写入      | ~15 毫秒 (0.015s)| 真实执行     | 调用 0x990a10 写入 80。                        |
| 7. 原生 Getter 回读核验  | ~25 毫秒 (0.025s)| 真实执行     | 调用 0x978360 读回 80，核验相邻字节与标志位。 |
| 8. Frida 结果回传与分离  | ~1.5 秒 (1.5s)  | 基础设施耗时 | Frida send 消息序列化，进程 Detach 并退出。   |
| 9. 人工与外部核对        | ~4 分钟 (240s)  | 人工交互     | 人工切换游戏查看 UI、比对数值并确认结果。      |
+--------------------------+-----------------+--------------+-----------------------------------------------+
| 总计                     | ~10 分钟        |              | 真实 Native 机器指令执行耗时仅 < 60 毫秒！     |
+--------------------------+-----------------+--------------+-----------------------------------------------+
```

### 2.1 关键洞察与优化结论

1. **Native 执行本身极其高效**：真正的 Native UI Getter、Setter 与物理内存比对在 60 毫秒内即可完成。
2. **“一次操作起一个 Frida 会话”在大规模下必然崩溃**：
   - 若对 10,000 个字段采用单操作独立会话模式：
     $$10,000 \times (2.5\text{s (Attach)} + 1.5\text{s (Detach)}) = 40,000\text{ 秒} \approx 11.1\text{ 小时}！$$
   - 并且会触发 10,000 次系统窗口枚举与 10,000 次子进程创建，极易引发 Windows 句柄泄漏或游戏崩溃。
3. **分块单会话执行（Bounded Chunking）是唯一解**：
   - 将 10,000 项操作按“球队 / 球员”聚合，划分为 200 个分块（每块 50 项）。
   - 每个分块仅启动 1 次 Frida 会话、1 次消息队列挂钩，在游戏主线程中毫秒级串行完成 50 次 Getter/Setter 写入，总基础设施耗时降至：
     $$200 \times 4\text{s} = 800\text{ 秒} \approx 13.3\text{ 分钟}，$$
   - 基础设施开销降低 **98%**！

---

## 三、支持与不支持能力边界矩阵

为杜绝任何“万能批量自由写内存”的投机倾向，批量引擎必须严格限定支持与不支持范围：

```
+-------------------------------------------------------------------------------------------------------+
| 范畴       | 目标实体 / 字段族                     | 支持状态        | 准入限制与说明                           |
+------------+---------------------------------------+-----------------+------------------------------------------+
| 球员倾向   | 99 项球员倾向 (SHOT_TENDENCY 等)      | FULLY_SUPPORTED | 必须位于目标球队 15 人 active roster 中；|
|            | 值域 [0, 100]，Native Index 1..99     |                 | Native Setter 0x990a10，Getter 0x978360。|
+------------+---------------------------------------+-----------------+------------------------------------------+
| 球员属性   | 54 项球员属性 (3PT, SPEED 等)         | FULLY_SUPPORTED | 必须位于目标球队 15 人 active roster 中；|
|            | 值域 [25, 99]，Native Index 1..54     |                 | 编码: val*3-75; 校验 0x31c 缓存标记清空。|
+------------+---------------------------------------+-----------------+------------------------------------------+
| 教练策略   | POE 攻防 (POEOffense, POEDefense 等)  | FULLY_SUPPORTED | 仅限已知教练设置表恢复的字段；           |
|            | 轮换偏好 (ZoneUsage, RunPlay 等)      |                 | 值域 [0, 100]；BenchDepth 暂不支持。     |
+------------+---------------------------------------+-----------------+------------------------------------------+
| 自由球员   | Free Agents (无签约球队)              | UNSUPPORTED     | 无法通过 Team Active Roster 指针定位，   |
|            |                                       |                 | 严禁通过遍历全局内存猜测指针！           |
+------------+---------------------------------------+-----------------+------------------------------------------+
| 选秀候选   | Draft Prospects                       | UNSUPPORTED     | 生命周期不在当前赛季主花名册中。         |
| 退役球员   | Retired / Historic Roster             | UNSUPPORTED     | 内存结构存在偏移变体，尚未完成 ABI 验证。|
+------------+---------------------------------------+-----------------+------------------------------------------+
| 球员徽章   | Badges (4 级徽章)                     | UNSUPPORTED_IN_ | 虽然已有 badge_fields，但联动能力点数与  |
|            |                                       | BATCH           | 动态槽位尚未完成批量原子化验证。         |
+------------+---------------------------------------+-----------------+------------------------------------------+
| 任意内存   | Raw Memory Writes (任意地址直接写入)  | STRICTLY_BANNED | 绝不允许任何无 Setter 绑定的裸内存注入！ |
+-------------------------------------------------------------------------------------------------------+
```

---

## 四、参数契约规范与硬 CAS 机制设计

### 4.1 批次文件参数格式（JSON / JSONL）

系统同时支持单 JSON 文件（带批次头与 `intents` 列表）以及流式 JSONL 文件（首行为元数据 Header，后续每行为单个 Intent）。

#### 规范字段定义：
```json
{
  "batch_id": "BATCH-20261101-LILLARD-PILOT-001",
  "save_instance_id": "save_20261101_user_active",
  "game_build_sha256": "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5",
  "expected_process_name": "NBA2K22.exe",
  "authorization_ref": "AUTH-HUMAN-20261101-GRADED-TEST-001",
  "source_snapshot_ref": "snap_worlddata_20261101_full_001",
  "dry_run": false,
  "intents": [
    {
      "intent_id": "INT-0001",
      "action_id": "COACH.STRATEGY.PLAYER_TENDENCY",
      "team_id": 28,
      "player_id": 2459,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 95,
      "value": 80,
      "source_justification": "Human S0 baseline calibration protocol"
    }
  ]
}
```

### 4.2 硬 CAS（Compare-And-Swap）三态决策表

每个修改意图在执行前，必须首先调用 Native Getter 读回真实内存值 $V_{\text{real}}$，并与调用方声明的 `expected_before` $V_{\text{exp}}$ 以及目标值 $V_{\text{target}}$ 进行精确比对：

$$\begin{cases}
V_{\text{real}} == V_{\text{exp}} \land V_{\text{target}} \neq V_{\text{exp}} & \longrightarrow \text{CALL\_SETTER (安全写入并回读)} \\
V_{\text{real}} == V_{\text{exp}} \land V_{\text{target}} == V_{\text{exp}} & \longrightarrow \text{UNCHANGED\_ALREADY\_TARGET (No-op 跳过，安全记账)} \\
V_{\text{real}} \neq V_{\text{exp}} & \longrightarrow \text{CAS\_EXPECTED\_BEFORE\_MISMATCH (阻断写入，整块报错停止)}
\end{cases}$$

> **重要安全红线**：
> 1. 当 $V_{\text{real}} \neq V_{\text{exp}}$ 时，说明调用方持有的基线数据已过期或外部环境已被篡改，**严禁盲目覆盖写入**，必须立刻阻断当前意图并保留现场。
> 2. 严禁隐式自动将 $V_{\text{exp}}$ 补填为当前值或默认值。

---

## 五、受控分块与游戏主线程预算保护

为防止批量修改导致游戏主线程阻塞、看门狗超时或界面假死，分块调度器强制执行以下硬性约束：

1. **分块容量上限**：每块最大包含 50 个修改意图（默认推荐 25–50）。
2. **同队聚合**：同一分块优先聚集同一支球队的球员，极大减少 Team 指针解析的虚表寻址开销。
3. **主线程执行时间预算（Time Budget）**：单分块 Native 调用在游戏主线程中的总耗时不得超过 **100 毫秒**；总观察等待超时（Frida 脚本级）设定为 **5,000 毫秒**。
4. **单分块调用预算（Call Budget）**：单分块内允许的最大 Native 函数调用次数 $\le 250$ 次（包含 Getter 与 Setter）。
5. **串行调用原则**：分块内部的 Native 函数必须在单次进入的 `PeekMessageA` 钩子回调中串行同步执行，**严禁使用任何异步并发或多线程竞争写入游戏内存**。
6. **故障前缀保留（Prefix Preservation）**：若分块执行到第 $k$ 项发生异常，前 $k-1$ 项已验证的收据必须落盘，第 $k$ 项标记为 `UNKNOWN`，第 $k+1 \dots N$ 项标记为 `NOT_EXECUTED`，**严禁自动重试，严禁逆向自动回滚**。

---

## 六、守恒律与收据模型

系统必须严格遵守执行守恒律：

$$N_{\text{planned}} = N_{\text{executed\_success}} + N_{\text{noop}} + N_{\text{blocked}} + N_{\text{unknown}} + N_{\text{not\_executed}}$$

所有结果均必须生成具有确定性哈希绑定的 Journal 收据，记录在本地 `06_执行/` 目录下，严禁上传任何二进制内存 Dump 到代码仓库。
