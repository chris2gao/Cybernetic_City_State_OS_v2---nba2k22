# REA 单 Session 多 Chunk 吞吐优化 · GPT-6 定向评估

- 评估日期：2026-11-02（America/Los_Angeles）
- 固定交付 SHA：`340253931fe0c7e386ff6d6efa40d1f7f3e731fd`，远端任务分支 HEAD 已核实。
- 岗位：`decision_architecture / GPT-6`；证据来源为 GitHub 已提交源码、JSON 收据、Journal 和执行者报告。**未自行重跑实机测试；未进行游戏操作。**
- 执行模型报告：`Gemini 2.5 Pro`。本评估不推导 Gemini Flash 3.8 的工程能力。
- 被优化的原生动作：当前已验证的 Player `SHOT_TENDENCY`；不涉及 Coach / 其他 Setter。
- 评估结论：**`PERFORMANCE_RESULT_ACCEPTED_FOR_12_ITEM_LIVE_PILOT; SCALING_NOT_YET_CERTIFIED`**。

## 一、正式实机证据（独立于自然语言报告的固定 JSON）

来源：`07_测试执行/benchmark_comparison.json` 和各子目录 `execution_result.json`、`journal/receipts.jsonl`。

| 测试 | 12 项/2 Chunk | Attach | 总耗时 | 结果 |
|---|---:|---:|---:|---|
| 旧版真实写入 | 12 | 2 | 39.40411s | 12 SUCCESS |
| 新版真实 No-op | 12 | 1 | 7.60537s | 12 NOOP，0 Setter |
| 新版真实写入 0→1 | 12 | 1 | **7.23892s** | **12 SUCCESS**，0 UNKNOWN |
| 新版真实写回 1→0 | 12 | 1 | **7.76659s** | **12 SUCCESS**，0 UNKNOWN |

新版单次真实写入平均总墙钟开销 **0.60324 秒/成功项**，旧版 **3.28368 秒/成功项**；减少 **81.63%**，速度比约 **5.44x**。不应把这一比值解释为每次 Native Setter 自身耗时，也不应将一次 12 项批次直接线性推断 1万项。

冷备份和正式运行状态以该 Run 的文件收据为依据；`1→0` 是另一次独立 batch，并非包含在 `7.23892s` 里。单次 `0→1→0` 完成两轮总计约 **15.01 秒**（不含独立人工 UI 验收）。

## 二、源码确认的优化机制

`bounded_session_transport.py` 提供 `SessionCompiler`、`SessionBatchTransport.execute_session`、`BoundedSessionExecutor.execute_batch`。生成单份 JS 和单个 `gui_once.js` Hook，整个批次单次 Frida attach；在启动之前 Claim 所有拟执行 Chunk，脚本按 Chunk 输出消息。原旧版每 Chunk 分别启动 PowerShell/Node/REA/Frida，且配置 15000ms 观察窗口；新版测试设 2500ms。这可解释主要耗时改善。

`baseline_timing_breakdown.json` 的 4.5ms Native 估计针对一个6-player Chunk；其逐阶段数字来自**不同微基准和源码观察的重建**，与当次完整 39.40411s 有未归因 jitter，不是单次无缝端到端 trace。旧总耗时、两次新成功测试属于更强的真实墙钟证据。

## 三、先修承重正确性，再扩 100/1000/10000 项

1. **会话结果边界不足**：`SessionBatchTransport.execute_session` 直接将所有 `chunk-execution-result` 以 `chunk_id` 合成字典，重复 chunk 会覆盖；未确保精确匹配 batch/save/plan/chunk_digest/action/receipt 全集。`BoundedSessionExecutor.execute_batch` 仅基于 `intent_id` 提取收据、未核对每条 SUCCESS 的 getter_before/after/unaltered=true，不强制所有 Chunk 的 receipt conservation。因此异常或伪收据可能被记作成功，规模扩张前需复用既有 `BulkExecutorService.run_with_transport` 的严格校验契约，而不是独立维护弱协议。
2. **Claim 与跨进程互斥顺序**：`execute_batch` 在 `CrossProcessFileLock(session_executor.lock)` 取得之前完成 `journal.claim_chunk` 和资源检查；两个执行者并发时可能产生计划/锁状态竞态。应在**读取 Journal、过滤、Claim、执行、确认提交**的整个受限阶段持有统一互斥；避免用异常吞掉 Claim 落盘错误。
3. **主线程扩展上限未经验证**：当前 `executeAction` 在一个 `PeekMessageA` 回调里遍历全部 `SESSION_CHUNKS`，不是已证明的逐帧/yield 分段执行。12 项成功足以证明试点；报告对1000项300–500ms或50–100 Chunk仅8–12秒是**预测而非运行证据**，应先在 Node VM 做负载及游戏帧预算测试，再逐级扩大。
4. **原始失败历史必须保留**：此前试验的 `stage2_session_mutation` 出现 `ReferenceError: u8 is not defined` 引发 UNKNOWN，且已存在 `reconciliations.jsonl`；另一次 `stage2b_session_mutation_to_zero` 出现 CAS mismatch、最终返回 `conservation_holds=false`。后续 `0→1` 与 `1→0` 确实全部成功，故失败不否定新正式结果，却不应宣称本任务所有历史子运行“全部通过”或异常统计已全闭合。现有 Loop 五行均标 PASSED，应以附加证据记录失败与解决，不覆盖历史。

上述三项为扩大真实写入规模前的**有边界根因修复**，无需重新开发 Native binding 或另开复杂架构。其他细节不作为阻断12项实机成功的理由。

## 四、阶段决议建议

- **接受**“一次 Attach + 多 Chunk”作为 REA 已完成12项实机性能验证的优化基线。
- **保留** CAS、原生 Getter/Setter、每项读回、Journal、UNKNOWN fail-stop 和 Human 授权，不以降低安全检验换速度。
- 暂不使用报告里的1000/10000项性能估计决定是否采用 Resident IPC；先封闭会话结果协议、锁和主线程耗时，再获取更大规模的**离线负载/只读**证据，之后由 Human 决定受控扩大实机规模。若提速仍不满意，再比较其他原生批处理路径。
- WorldData 采集性能优化是**另一独立任务**，本次 REA 报告不包含它的完成证明。
- 本报告仅补充源证据，不改变既有 Human 测试授权、不操作游戏、不修改游戏或数据库、不将候选直接合并 NBA2K22 master。
