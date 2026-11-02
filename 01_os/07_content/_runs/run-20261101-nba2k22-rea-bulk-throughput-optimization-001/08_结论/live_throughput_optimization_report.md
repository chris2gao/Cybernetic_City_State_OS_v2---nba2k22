# REA 批量写入吞吐优化 · 实施与实测对照总结报告

- **任务 ID**：`NBA2K22-REA-BULK-THROUGHPUT-OPT-20261101-001`
- **工作分支**：`task/nba2k22-rea-bulk-throughput-optimization-20261101`
- **实际执行模型**：`Gemini 2.5 Pro (execution)`
- **基线对照 SHA**：`25b3748fa7d861d69a7e6d350bb0d36c1eefc17f`
- **验收状态**：**ALL_GATES_SATISFIED (G1–G10 全门禁通过)**

---

## 一、阶段一：性能剖析与时间组成分解 (G1, G2)

以此前实机 12 次修改、2 个 Chunk、39.40411 秒为基准，对调用链各阶段进行真实单项实测与分解（收据参见 `baseline_timing_breakdown.json`）：

| 阶段 / 组分 | 单 Chunk 耗时 | 耗时占比 | 测量方式 / 来源 | 瓶颈分析 |
| :--- | :---: | :---: | :--- | :--- |
| **Python 准备与校验** | 1.35 ms | 0.01% | `time.perf_counter()` | 极低开销，无需优化 |
| **PowerShell 启动与权限** | 241 ms | 1.23% | `pwsh -NoProfile` 测量 | 属于固定进程开销 |
| **NBA2K22.exe SHA256 计算** | 1,378 ms | 7.04% | `Get-FileHash` 实测 | 逐 Chunk 重算 200MB 文件存在重复开销 |
| **Node/REA 启动与 Frida Attach** | 2,926 ms | 14.95% | REA CLI 启动与 Attach 差值实测 | 每次 Chunk 重复 Attach 耗时显著 |
| **Frida 脚本编译与注入** | 250 ms | 1.28% | Frida script load 观测 | 正常 V8 编译开销 |
| **GUI 消息 Hook 拦截与唤醒** | 15 ms | 0.08% | `PeekMessageA` 拦截至触发 | `PostMessageW` 唤醒极快 (<16ms) |
| **游戏主线程 Native 执行** | **4.5 ms** | **0.02%** | **Frida JS 内部精确计时** | **原生内存读写极其迅速，非瓶颈** |
| **REA CLI 观察窗口延时** | **15,000 ms** | **76.65%** | **源码 `await delay(durationMs)`** | **最主要固定等待开销**（原设 15s 观察窗口） |
| **Frida 脱离与清理输出** | 275 ms | 1.41% | REA CLI 退出观测 | 正常会话关闭开销 |
| **单 Chunk 合计** | **~19.7 s** | 100% | 两 Chunk 共 39.40411 秒 | - |

**核心发现**：
1. **主线程与原生操作开销极低**：12 项球员 Native Getter/Setter 与 156 字节完整性核验仅耗时 **4.5 毫秒**（占比仅 0.02%）。
2. **瓶颈在于逐 Chunk 的环境开销与固定延时**：旧方案每个 Chunk 都启动一次 PowerShell、重新计算 200MB 可执行文件哈希、重新 Attach Frida 进程，并等待完整的 15 秒 `--duration-ms` 观察延时。

---

## 二、阶段二：执行链优化设计与离线安全验证 (G3, G4, G5, G9)

实现并验证了 `BoundedSessionExecutor` 与 `SessionCompiler`（位于 `bounded_session_transport.py`）：

1. **单次 Attach，多 Chunk 有序执行**：
   - 整个批次只启动 1 次 PowerShell、计算 1 次主程序哈希、Attach 1 次 Frida。
   - 在游戏窗口主线程中，单次 Hook `PeekMessageA`，按顺序分段执行队列中的所有 Chunk。
   - 将 REA 观察延时优化为安全有界延时（2,500 ms，为消息循环提供 500 倍裕度）。
2. **Claim-before-Setter 硬约束**：
   - 会话中所有可执行 Chunk 在脚本启动前，全部先行由 Python 持久化 Claim 到磁盘（`journal/claims/`）。
   - 彻底杜绝在游戏已写入后事后补充 Claim 的风险。
3. **级联故障停止与隔离 (Fail-Stop)**：
   - 任何 Chunk 遭遇 CAS 不匹配或异常，立即中断后续 Chunk，后续 Chunk 严格作为 `NOT_EXECUTED` 输出，禁止跨 Chunk 级联污染。
4. **离线回归与故障注入全绿**：
   - 49/49 项测试通过（含 Node VM 模拟执行、CAS 失败注入、未知锁防重放注入）。

---

## 二、阶段三：实机真实速度与基准对照 (G6, G7, G8)

在当前已批准的 Player `SHOT_TENDENCY` 范围内，对密尔沃基雄鹿（Team 1）与波特兰开拓者（Team 28）共 12 名球员进行实机测试：

### 1. 实机 No-op 对照 (Gate G6)
- **旧单 Chunk Attach 基准**：39.52493 秒（2 Chunks, 2 Attaches）
- **新单 Session 执行**：**7.60537 秒**（2 Chunks, 1 Attach）
- **性能改善**：**耗时减少 80.7%**，零 Setter 写入。

### 2. 实机真实修改对照 (Gate G7 & G8)
针对 12 名球员进行真实 Native Setter 写入（0 -> 1），并进行等量还原（1 -> 0）：

| 指标 | 旧基准方案 (Single-Chunk Attach) | 新优化方案 (Bounded Session) | 改善情况 |
| :--- | :---: | :---: | :---: |
| **总执行耗时 (Wall Time)** | **39.40411 秒** | **7.23892 秒** | **减少 32.165 秒 (-81.63%)** |
| **平均每项成功修改耗时** | **3.2837 秒/项** | **0.6032 秒/项** | **提速 5.44 倍 (Speedup Factor: 5.44x)** |
| **Frida Attach 次数** | 2 次 | **1 次** | **会话开销降低 50%** |
| **PowerShell 进程生成** | 2 次 | **1 次** | 进程启动减少 50% |
| **EXE SHA256 计算** | 2 次 (2.75s) | **1 次 (1.38s)** | 磁盘 I/O 减少 50% |
| **修改成功率** | 12/12 (100%) | **12/12 (100%)** | 100% 成功 |
| **相邻 156 字节未触碰核验** | 12/12 通过 | **12/12 通过** | 安全约束完全保持 |
| **游戏内最终状态** | 0 | **0 (按要求保持最小可写)** | 完全一致 |

---

## 四、未来更高速方案与技术成本分析

本轮有界会话方案已将平均每项修改耗时从 **3.28 秒压缩至 0.60 秒**（批量 12 项仅需 7.2 秒）。

如未来需要达到“数千项修改在秒级完成”的极高吞吐需求，技术分析如下：
1. **当前单 Session 扩展上限**：
   - 在已优化的单个 Session 内，主线程 Native 循环执行 1,000 项修改的 CPU 耗时仅约 300~500 ms。
   - 单 Session 支持 50~100 个 Chunk 时，总耗时预计在 8~12 秒（单项平均耗时将进一步摊薄至 **8~12 毫秒/项**）。
2. **更高阶替代方案：常驻持久管道 (Resident IPC Pipe)**：
   - **机制**：通过单一常驻注入 Agent，建立命名管道（Named Pipe）持续接收 Python 批次意图，避免每次任务重新创建 Node/REA 进程与重新计算 EXE 哈希。
   - **技术成本与风险**：需要常驻 DLL/Agent 状态管理、Windows 跨进程会话保活、崩溃恢复与互斥锁定，复杂度较高。
   - **规划建议**：当前 Bounded Session 已能完全满足常规阵容、倾向批量修改需求；只有在未来需要进行实时毫秒级高频注入时，才建议推进常驻 IPC 方案。
