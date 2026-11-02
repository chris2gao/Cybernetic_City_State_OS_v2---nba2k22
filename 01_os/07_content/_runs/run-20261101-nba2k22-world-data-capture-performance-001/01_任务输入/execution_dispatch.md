# WorldData 全量采集性能分析与定向优化 · 函数级执行合同

**任务 ID**：`NBA2K22-WORLDDATA-CAPTURE-PERFORMANCE-20261101-001`
**OS 岗位**：`execution`；目标使用 Gemini Flash 3.8，实际执行型号如实登记。GPT-6 为 `decision_architecture`。
**分支**：`task/nba2k22-world-data-capture-performance-20261101`
**工程基线**：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`（已有 `world_data_prototype` 完整工程）。
**禁止从 NBA master 直接拼接替代实现**：当前 master 未包含该完整工程；优化留在分支，避免未经核验地混入其他基线。Human 已允许在分支增加实质复杂度时合并主线，但**现在分支相对 master 大幅分叉**，合并并不简化当前工作；如确需集成，列出有界 diff、回归和正式 PR 后再处理，不直接改写 master。
**任务范围**：真实只读采集 + 离线 fixture/数据库副本上的性能剖析与局部优化。严格禁止运行 Native Setter、修改游戏存档、推进比赛/赛季、覆盖生产 SQLite 历史、修改字段语义与身份规则。

## 一、已有实测与工程目标

原始证据（需固定原文，不得改写）：
`01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment21/refresh-report.json`

- 2026-10-25 13 个源任务报告：10 个实际采集，3 个年度源复用先前历史观察；总耗时约 **199.51s**，并非“20个源全新采集”的总成本。
- `player-details` 从 14:05:05.746527 至 14:07:12.509182 = **126.76s**，涉及 3,390 player source 与 332,220 badge rows。
- `planning` ~19.47s；`schedule` ~13.53s；`player-skills` ~12.99s；`player-state` ~11.69s。各源串行执行，含 Reader、payload、磁盘和 SQLite；此前**未量出**上述层次分别耗时，不可认定都是读内存慢或都是 SQLite 慢。
- 原世界数据历史要求是追加保留、可回看；禁止以不插入完整徽章/字段、减少历史、关闭校验、跳过未知来源的方式虚增速度。

工程目标：针对最慢的 `player-details` 与可能复用的 `player-skills`，**先定位瓶颈、选一两个确定有效的局部优化，再复测完全相同的语义与数据量**。最终报告单数据源秒数、总耗时、读取调用数、读取字节量、解码/编码耗时、SQLite 写入行数及事务时间、缓存/文件系统开销与最大 RSS。速度目标以实测改善为准，不预设 Human 未批准的强制 SLA。

## 二、具体源码入口

根目录：`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/`

必读：
- `refresh.py:refresh_world, _capture, _unit_receipt, checkpoint`：按 SOURCES 串行触发，反复创建各 Reader，做进程上下文与版本核验、提交回执、磁盘 checkpoint。
- `live_reader.py:ReadOnlyGameProcess.__init__, read, close`：Windows `OpenProcess(0x1010)`、每次 `ReadProcessMemory` 上限 **1248 字节**、逐次构造字节/trace/sha256，需保留 fail-closed；**不允许为了性能删除读权限约束或私有 PLAYER 区间屏蔽**。
- `process_session.py:resolve_pid, handle_creation_time, owner_is_live`：绑定 PID 和进程启动时间。
- `player_detail_reader.py:collect_public_player_pool, collect_player_details, capture_player_details, projection_ranges, verify_detail_metadata`：3,390 玩家逐人、逐个公开区间读取与 **第二轮 recheck**、枚举/Native 元数据核对、原始资料构建。
- `player_skill_reader.py:skill_projection_ranges, collect_player_skills, skill_payload, capture_player_skills`：调用同一个 `collect_public_player_pool`，独立再读 Native player pool；现有完整公共字段、56 attributes/99 tendencies/4 play types 等必须保留。
- `engine.py:connect, ingest_capture, _check_envelope, _insert, _ensure_record`：目前逐行 Python 类型/键检查与 `conn.execute`；大批量 badge rows 是可测的 SQL 优化候选。
- `schema.sql`、`schema_model.py`、`live_world.py:_AcquisitionReceipt`：DB 索引、事务与 Live provenance。历史不可覆盖，冒充 LIVE_READ 的 fixture 禁止。
- `database_operations.py` 用于只读表大小、索引、容量基准。

## 三、分阶段执行（必须先有 profiling，再优化）

### D0 · 源码/数据基线锁定

1. 将上面的固定 `refresh-report.json` 作为“已存在的真实串行基准”。不要把 126.76s 误用为 `ReadProcessMemory` 净耗时。
2. 固定一份可重复播放的**原始 fixture/公开区间投影**及生产数据库的**独立只读副本**，登记每个表、字段、行数、语义身份、SHA。不要把未绑定的 fixture 晋升为真人 LIVE_READ。
3. 本机必须具备磁盘余量和适度内存预算；不允许把 2017 MacBook 的 16GB 机器压成不可用，不应一次性将全部历史和大对象装入 RAM；若受资源限制，记录中止与样本子集，不编造速度。

### D1 · 轻量真实计时拆分

在不改变源事实的前提下引入`PerformanceTrace`/ contextmanager 计时（可在新 `performance_trace.py` 模块），按各 family 统计：
- `t_process_open`, `t_native_metadata_verify`, `t_player_public_projection`, `t_player_control_recheck`, `t_decode_contracts`, `t_decode_badges`, `t_build_facts`, `t_write_raw_artifacts`, `t_hash_artifacts`, `t_db_schema_validate`, `t_db_ingest`, `t_db_commit`, `t_query_validation`, `t_total_wall`；
- `ReadProcessMemory` 次数/读取总字节/读取大小分位数/失败计数/公开区间比率；`sqlite_insert_count` 分表、sqlite_changes、磁盘增长/SQLite journal_bytes、峰值 RSS；分阶段准确标注 live vs fixture。
- 不要对每条读/每笔 SQLite INSERT 都调用昂贵日志格式化（计时探针应低开销聚合）；对实时采集的敏感地址不可发布未清洗的绝对地址。
- 记录开启/关闭插桩情况下的 overhead，确保不会因为追踪自身让性能基准失真。
- `refresh_world` 维持每源独立原子提交和跨源原有一致性范围，不假装它是一个全局同时刻的事务。

### D2 · 优化方向 A — SQLite 大批量写入（优先用离线副本做 A/B）

优先在`engine.ingest_capture` 的可控插入路径中比较：
1. 当前 `_insert` + `conn.execute` per row；
2. 保留字段白名单、数据类型、主外键、唯一身份/碰撞与 NULL 约束的**批量预校验 + 分批 executemany**；保留同一个 capture_unit 事务边界，不能绕过 `_ensure_record` 的已有同名核对行为。只在能证明每条错误仍能阻止整个 unit 提交时采用。
3. 用原始 332,220 行 badge facts 和其他真实表模型的离线回放测 A/B，不使用 synthetic 1000 行来冒充真实工作量；控制数据库初始状态一致、索引一致、磁盘缓存影响，对同一输入至少重复 3 次且记录中位数、波动。**不得以关闭 foreign_keys、关事务、禁用索引、禁用旧数据检查作为默认优化**。
4. 精确比较生成后的 SQLite 表主键/外键/数值及历史追加守恒，检验同 unit digest 幂等、跨 save 拒绝、同 unit 不同 payload 拒绝、损坏行 rollback，原始 source artifact SHA 与 provenance 不变；任何结果不同的“更快”方案立即不采纳。

### D3 · 优化方向 B — 减少重复跨进程读取（保留原生读源语义）

1. 只对公开字段区间形成合并读取段；仍遵守`ReadOnlyGameProcess.read` 的实际长度上限以及 `RESTRICTED_PLAYER_RANGES`，**不可为了“整块”而读 Potential 等受限字节**。
2. `collect_public_player_pool` 可实验性地比较原逐区间读取与**合并相邻/近邻可公开区间**、按页/上限分割合法区间的调用量；不跨私有区间，不改变 decode/offset/签名。
3. 当前 player-details 和 player-skills 是各自 `capture_*()` 新建 Reader、重新读取 3,390 Player 池与 Native metadata；允许提出**本次 refresh 会话内只读公共投影共享缓存**，但必须绑定 PID+进程创建时点+save/season/roster epoch、来源哈希及记录观察时间，不将缓存跨赛季、跨进程或跨存档当新鲜事实。**缓存复用不等于新一轮 LIVE_READ**：历史事件和 observation freshness 必须标记正确。
4. 二次一致性 recheck 必须保留，允许将相邻公开区间合并/批次 recheck，但不允许为了快完全取消、仅验证一次 root 或依赖旧内存缓存假装复查。
5. 如果本机真实读取要进行，则只用已经恢复存档后的当前游戏**只读**，不触发任何 Native Setter；读取时发现 roster/season 改变立即终止当前 unit 并报告。不同来源共享采样必须证明 snapshot epoch 条件成立。

### D4 · 结果验收与成本边界

至少交付以下 A/B 对照：
- 原固定 2026-10-25 基线：`player-details` 126.76s、全任务 199.51s（仅已采源）；
- 本轮未优化实现 + profiling 同机同状态；
- SQLite 优化前后（同 payload/同 DB copy）；
- Reader 优化前后（同公开数据、同 epoch 及返回值）；
- 综合改动后一次真实只读采集（如现场可用），且报告 **新旧 field/row counts/digests/Source refs** 一致；没有真实场景则标 NOT_RUN，不将 fixture 冒充实机性能。
- 展示 CPU/IO/RSS 峰值、逐 Family 时间、全任务累计时间、对 `player-details` 节省多少秒，以及总时间/平均每次字段或球员采集时间的口径。
- 因当前快照与 2026-10-25 游戏阶段、人数、磁盘缓存可能不同，**不同日期实机基准只能作为参考**；主要因果判断应依赖同环境 A/B 回放与当次真实采集。

## 四、数据安全和 OS 内部开发 Loop

所有游戏访问只读，不修改任何真实存档；数据库测试使用独立副本，所有源事实、历史观察、稀有年份/记录与外键关系保持。历史策略“全部可变字段可回看、追加而不覆盖”绝不因性能降级。

源代码更改限制：`world_data_prototype/engine.py, live_reader.py, player_detail_reader.py, player_skill_reader.py, refresh.py` 及最小 `performance_trace.py` 和对应 tests、当前 Run 证据；其他数据族如需改动，先说明其影响与证明。不得直接写 master 或改 Core 规范。

内部 Loop：逐个可证伪增量进行采样、失败定位、源代码/测试修复、固定 checkpoint，不能为了收集统计而无意义循环。当前任务与 REA 写入优化**可在不同窗口并行研发，但不能同时访问同一个游戏进程开展性能对照**，避免互相干扰。

**交付**：`source_baseline.json`、`profile_breakdown.json`、`sqlite_ab_benchmark.json`、`reader_ab_benchmark.json`、`source_equivalence_check.json`、`loop_iterations.jsonl`、可程序化核算的 `loop_summary.json`、`completion_pointer.md`、完整最终 Git SHA 和明示未完成的部分；保存原始命令/退出码/真实执行模型信息。

**停止条件**：精确存档身份/权限/内存布局不可核对、可能读到受保护 Player 字节、数据语义/事务/历史不一致、实测不再新增有价值证据、资源瓶颈、需要跨阶段授权、实际性能回归；停止要提交原因和可用证据，不得扩大范围。

**集成政策**：Human 已条件允许在确实减少开发复杂度时采取正规 PR/审核方式合并，但本任务所在旧 WorldData 基线与现有 master 大幅 diverged，不能因为“可以合并”就不经 diff 审核直接导入整条分支。优化成果先固定分支；后续是否拆出最小集成 PR 再按事实判断。
