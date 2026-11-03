# Decision Outbox · B1/B2/B3 定向整改最终复核

- 复核日期：2026-11-02 (America/Los_Angeles)
- 审核岗位：decision_architecture / GPT-6
- Gemini 执行模型：Gemini 2.5 Pro (execution)，据任务记录
- **固定整改代码 SHA**：`a1ff98852512d1d7aea07e0f88a88f8ea80aeac5`；Github 任务分支 HEAD 与该 SHA 一致
- 本机远程只读复测：Desktop Commander 连接 `DESKTOP-FPNE2NQ`，`E:\gemini_space\nba2k22`；`git rev-parse HEAD` 与固定 SHA 一致，`git status --short` 为空
- **独立执行命令**：在 `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control` 下 `python -m pytest tests/test_decision_outbox.py tests/test_decision_batch_bridge.py tests/test_validate_batch_execution.py tests/test_offline_closed_loop.py tests/test_bounded_session_executor.py tests/test_bulk_executor.py tests/test_role_batches.py tests/test_role_capabilities.py -q`
- 本机独立测试结果：**78 passed in 11.98s；exit code 0**。不依赖 Gemini 的 11.75s 自述计时。
- 本次仅离线回归；无 NBA2K22 attach、Setter、存档修改或 master 合并。

## 验收判断

**`OFFLINE_DECISION_TO_BATCH_EXECUTION_CLOSED_LOOP_VERIFIED; B1_B2_B3_MATERIAL_LOGIC_CLOSED`**。

1. **B1**：`decision_batch_bridge.map_receipts_to_outbox` 逐 role intent 使用既定 `role_to_bulk_map` 检查全部 sub intent，缺失输出 `INCOMPLETE_RECEIPTS`，部分成功/失败输出 `PARTIAL_EXECUTION_HALTED`，不再错误标全成功。`decision_outbox.record_execution_receipts` 加了 SEALED、非空、精确 intent 集合、重复/未知回执与终态不可覆盖的检查；含 NOT_EXECUTED 则周期 `STOPPED_PARTIAL`，UNKNOWN 则 `UNKNOWN_LOCKED`。
2. **B2**：`_validate_intent_submission` 统一用于 add 和 supersede，新替代意图需要通过 issuer、上下文、角色允许动作、phase grant、scope 审查。add/supersede/seal 使用 SQLite `BEGIN IMMEDIATE`、revision/status 比较更新；没有为简单本地容器引入分布式锁。CLI 明示凭据文件属于 `LOCAL_OPERATOR_TEST_MODE`，不虚称真实宿主鉴权。
3. **B3**：通用 Validator 加入 unexpected intent 对账、逐项身份/旧值/目标/Getter/未请求字段校验、chunk digest/action/batch/save 身份、重复/遗漏 Chunk 检查和按球员 readback；修正 Manifest build 指纹检查。新增负例并且本机测试通过。
4. **闭环证据**：提交的离线 `offline_end_to_end_receipts.json` 记录 4 Native 子字段 Fake 成功，但 1 条角色交易意图 `NOT_EXECUTED`，决策周期现正确为 `STOPPED_PARTIAL`；`manifest_game_build_valid=true`。
5. **性能**：10k 记录插入的原始 `10k_outbox_benchmark.json` 是约 `0.37785s`，而 Loop Summary 登记 `0.35376s`，属于不同口径/运行收据不完全一致。数量级足以证明容器在当前离线规模下不是瓶颈，不因此重新开性能整改。

## 仅保留下一阶段接入注意（不阻断本次离线验收）

- **真实闭环主机接口尚未交付**：`record_execution_receipts` 依然是可信调用方 API，本身不重新验证全部 native evidence；真正接入游戏前必须由 Host 执行“通用批次验证 PASS → 原始批次身份关联 → 一次性回填”的原子/受控编排，不能让普通角色模型直接提交伪造 SUCCESS。
- **回执校验边界**：当前 Raw Chunk 的内部回执核验主要是 intent ID 集合；独立 readback 是可选输入，且逐玩家缺失时没有统一强制失败。若未来以真实 Native 结果作为生产级终态，需要把这两个检查作为严格 Live 模式的强制条件。离线已提交金标准测试通过并不证明任意缺失证据均可识别。
- **角色与 Native 动作成熟度**：当前 Fake GM/Coach 示例不等于 Coach、Player attributes、交易等已完成实机认证；已有 100 项 Live 实测仅证明具体 Player SHOT_TENDENCY 批量路径。Bridge 的 `allow_partial_execution` 应在宿主执行政策明确决定，不能因默认值为 true 自动获得全角色批次的生产授权。

## 最终决议

本轮 **无须再开启针对这三项的反复审核或重写 Outbox**。接受当前分支作为后续 GM/教练/球员决策阶段共享的**离线基础组件**；后续要形成可自动操作真实游戏的生产闭环，应在独立 Host 接入阶段处理真实授权、计划与回执原始证据绑定和 Live 强制验证，不把本任务范围扩大。WorldData 性能优化仍按 Human 指令保持暂缓。

本报告是追加审核材料，不更改本轮执行 SHA 的代码、原始测试证据或任何游戏数据。
