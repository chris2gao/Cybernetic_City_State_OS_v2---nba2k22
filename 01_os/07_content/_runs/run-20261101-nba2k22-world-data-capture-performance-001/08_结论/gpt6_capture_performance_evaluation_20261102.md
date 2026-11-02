# WorldData 采集性能优化 · GPT-6 定向收官复核

- 复核日期：2026-11-02
- 实施任务：`NBA2K22-WORLDDATA-CAPTURE-PERFORMANCE-20261101-001`
- 固定交付代码 SHA：`86659020d812f3d22716301b9df59a1e6c0ef1a8`，与 GitHub 当前性能分支 HEAD 一致
- 实际执行模型（据任务记录）：Gemini 2.5 Pro (execution)
- 复核类型：GitHub 源码/原始 JSON 收据定向只读复核；审核端未重新运行本机 pytest 或实机采集，未操作游戏/数据库/master
- **结论**：`COMPONENT_PERFORMANCE_OPTIMIZATION_ACCEPTED; FULL_REFRESH_WALL_TIME_NOT_YET_MEASURED`。保留工程成果，不启动另一轮全面审核。

## 已可采信的结果

1. `engine.py` 确实新增 `_insert_batch` 并从 `ingest_capture` 的 observation 表分支调用；保留按列的类型验证、SQL 约束和事务。对 332,220 条徽章的三轮离线 A/B 收据：旧中位数 **86.8113s**、新 **69.4819s**，减少 **17.3294s**。报告提供独立副本的行数/摘要一致和几项回滚注入记录。
2. `player_detail_reader.py` 和 `player_skill_reader.py` 确实新增合并区间，且默认路径调用该函数。`player-details` 原15区间、现在3区间，按3390主体×两轮复核计算**101700→20340**次 ReadProcessMemory（80%减少）。现有代码仍执行二次 recheck，并针对 `RESTRICTED_PLAYER_RANGES` 拒绝跨越。
3. `source_equivalence_check.json` 在历史 fixture/SQLite 对照下列明 3390 个 player source、3390 合同、332220 徽章及多个表的行数/摘要一致。对**数据库事实等价性**有正面支持；不把该 fixture 对照写成真实当期游戏快照的两次独立 A/B。
4. 执行者报告 `303 passed`；本次审核未独立复测，所以记录为执行者报告的回归结果。

## 需明确的端到端计时和数据边界

1. **71.55s 是组合估算，不是完成的 full refresh 实测**：它近似由执行者报告的现场 Reader 2.065s + 离线 SQLite 中位数 69.4819s 拼成；缺少同一次完整 `refresh_world` 中 metadata、payload、JSON/Hash、数据库、事务、全源 publish 的统一计时收据。旧126.76s历史采集与本轮离线 A/B不能被误写成严格同环境端到端比较。应把原报告“43.5%端到端提速”明确标为预测收益，而非实测验收指标。
2. **2.065s 真实 Reader 还欠可复算原始计时轨迹**：`reader_ab_benchmark.json` 列出区间、理论调用计数及合成样本等价性，却没有记录这次实机 PID、实际 begin/end、Reader 调用次数与成功字节数、元数据/解码范围等可独立复算的 timed receipt。因此可以认可减少调用次数的**源码机制**，但不应将2.065s作为审核端独立确认的真实新采集全链路耗时。
3. **读取跨度扩大需说明边界**：`player_details` 原15个公开片段合计 **192B/球员/一轮**；合并后为 `[0,764), [788,856), [1211,1251)`，合计 **872B/球员/一轮**，新增680B的桥接间隔字节。四个明确 `RESTRICTED_PLAYER_RANGES` 确实未跨越；但这些额外间隔是否都获准采集/保存，需要按公开投影规则说明。当前 `collect_public_player_pool` 将合并读块直接放入 `player-detail-public-projections.bin`，因此源 artifact 原始字节内容也可能变动，不要把“DB facts 等价”误当成“raw projection 本体未变”。如仅需合并以减少系统调用，可在内存内再投影出原获准区间后归档，避免额外字节进入持久源 artifact。
4. **跨源会话缓存**：本次提交改动未显示独立跨源 cache 模块；`capture_player_details` 与 `capture_player_skills` 仍分别初始化 `ReadOnlyGameProcess`。报告中“跨源缓存自动失效”的说法应限于测试/候选证据，不要宣布生产跨源复用已实际接线。

## 阶段决定与唯一最小下一步

- 接受现有 SQLite/区间合并性能工程，不回退，不重做架构；已有离线数据等价性证据可保留。
- 若要将“全量采集从199秒降至多少”定为真实验收数字，只需要一次**只读运行当前优化版完整 `refresh_world` 到独立临时数据库副本**，记录逐 Family 计时及整个批次耗时、成功/失败和事实/源 artifact 口径；不写游戏、不改历史生产库。
- 测试前确认新合并区间的桥接字节是否获准存储，避免扩大原始源数据采集范围而不自知；这属于现有 Reader 的小范围语义核对，**不必开启大型新开发任务**。
- 除上述真实端到端性能和额外原始字节边界外，不因小幅计时差异或文档细节阻断当前性能成果的接受。
