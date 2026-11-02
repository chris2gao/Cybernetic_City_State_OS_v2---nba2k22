# WorldData 采集性能优化 · Human 恢复执行指令

任务：`NBA2K22-WORLDDATA-CAPTURE-PERFORMANCE-20261101-001`
分支：`task/nba2k22-world-data-capture-performance-20261101`
原始工程固定基线：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`
恢复执行决定：2026-11-02 / Human
OS 角色：`execution` / 真实执行模型需在每轮如实登记。
当前状态：`RESUMED_BY_HUMAN_DISPATCHED_NOT_EXECUTED`。

## 一、本次 Human 裁决

Human 已接受 REA 100 项真实修改约 **10.3176 秒**的性能和 Decision Outbox 离线整改成果，现要求优先推进之前暂缓的 **WorldData 全量采集耗时优化任务**。

**这是原任务恢复，不是新建任务，不重新规划数据库架构，也不重新发布 REA 任务。**

必须先阅读并遵守同一 Run 下：
1. `01_任务输入/execution_dispatch.md`：原函数级完整实施方案；
2. `01_任务输入/verification_plan.json`：G1–G10；
3. `run.yml`：更新后的状态；
4. 固定历史原始证据 `run-20261024-nba2k22-world-data-implementation-002/06_执行/increment21/refresh-report.json`。

优先级顺序：**D0 基线和测试副本 → D1 真实分段计时 → D2 SQLite 插入 A/B → D3 Reader 优化 A/B → D4 结果复测和守恒**。根据 profiler 数据决定是否继续某一方向，不要求为凑指标同时修改所有 Reader。

## 二、关键可证伪假设

此前真实采集一轮约 **199.5s**，其中 `player-details` **126.76s**、3,390 玩家、332,220 Badge rows。历史全批次中有 3 个年度数据源复用旧结果，并非全新采集。

测量后必须识别哪一项对 `player-details` 贡献最大：
- `ReadProcessMemory` 次数、实际字节量、重复读取和第二次控制读回；
- 原始数据投影/徽章及合同解码、facts 构造、JSON/Hash 写文件；
- SQLite per-row `execute`、索引和 `commit`；
- metadata/roster 身份验证、不同 family 重复打开 Reader、磁盘 I/O。

**只接受“同数据、同索引、同安全约束、同执行环境”的 A/B 实测进步。** 如果 SQLite 只占很小时间，就优先 Reader；如果 Reader 本来很快，优先 SQLite。不要先假设谁是瓶颈。

## 三、最小工程实现和 Loop

1. 先检查 `world_data_prototype/{refresh.py,live_reader.py,player_detail_reader.py,player_skill_reader.py,engine.py,process_session.py,schema.sql}`；复用现有采集工具和目录，不另起一个 WorldData 服务或历史数据库。
2. 采用有限、低开销计时器与计数器，尽量将采集读取、解码、源文件写入、SQL ingest/commit、核验分开计时。采集只读。不要将一个源全耗时伪装成纯内存读取或纯 SQL 耗时。
3. 离线数据库 A/B 优先真实体量 `332,220` Badge facts，保留 `_ensure_record` 的语义、外键、唯一键、历史记录、原有事务和失败 rollback；以完全相同的数据库副本分别测 `execute` 与 `executemany` 等安全选项。保留完整表计数和值/身份摘要。
4. Reader A/B 只合并已经批准的公开区间，不能跨受限 player ranges；现有每次最多1248字节的读取约束、内存可读性检查、二次 recheck 不可删除。任何 session cache 必须绑定 game PID+创建时间、save/season/roster epoch 与来源；不能把缓存结果冒充新的 live snapshot。
5. 开发 Loop：聚焦一个有收益的增量、测试、分析时间/守恒/失败、修正或停止，记录准确实际执行模型；不为凑轮数重复 PASS。若出现因果对照不公平，修正测试而不是把差异算作提升。
6. 本任务继续**不授权**任何 Native Setter、游戏日历推进、游戏存档覆盖或真实 WorldData 生产库历史更改。实际游戏只读采集可在现场 identity/epoch 已验证时运行；若无法核实则只保留 offline A/B，并如实标 `NOT_RUN_LIVE`。
7. 可用已有分支进行开发；Human 之前只在合并**能实际减少集成复杂度**时条件允许正规 PR，不能不经差异核验直接合并整个 WorldData 旧基线到 master。REA 100 项已接受且当前不再做性能开发，避免访问同一游戏进程进行干扰测试。

## 四、验收与交付

- 必须量化 `player-details` 和总耗时的改善，记录新旧分阶段时间、成功/失败、源表/行数/字段数、内存读取次数、读取 bytes、SQLite 写入行数、RSS/CPU/I/O。没有可比较的旧采样时要实测本轮**未优化同环境基线**。
- 每次性能主张附原始命令/退出码、固定源码 SHA、数据源哈希/快照标识、工作线程/进程数、存储环境和重复次数；不把历史不同日期的耗时当精确 A/B。
- 结果正确性以 `source_equivalence_check.json`、源事实 SHA、完整数据库记录与既有历史守恒为依据；任何无法解释的内容变化均判失败，不能靠删除/少采集换速度。
- 保持既有 G1–G10 验收门。输出 `source_baseline.json`、`profile_breakdown.json`、`sqlite_ab_benchmark.json`、`reader_ab_benchmark.json`、`source_equivalence_check.json`、`loop_iterations.jsonl`、程序可复算 `loop_summary.json`、`completion_pointer.md` 和准确最终 GitHub SHA。
- 若某个优化方向实际无收益或引入更多复杂度，记录“不采用”并继续下一个有证据价值的方向；不要为完成列表引入无意义重构。

**最终状态只有在代码、性能及数据等价性证据满足要求后才能标 `WORLDDATA_CAPTURE_PERFORMANCE_OPTIMIZED_VERIFIED`；其余应如实保留部分结论与缺口。**
