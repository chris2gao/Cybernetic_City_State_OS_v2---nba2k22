# 单存档实验规则和边界

这一工作单元承接 [Issue #40](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40)。同一个母任务跨窗口、常规赛和经 Human 确认的恢复继续。单轮检查点记录进度，结案条件是冻结范围内各研究端点已经独立复证、经预注册有足够功效而未检出，或有证据说明无法识别。其余不可测项保留理由和 Human 裁决。

## 字段与来源

`mechanism_research_ledger.json` 由 Stage02 M1–M5、Single-Field Sweep 和固定设计版本重建。204 条 Stage02 观察条目分为 99 倾向、86 世界设置和 19 教练设置。99 倾向含 48 个命名槽和 51 个未知只读槽。10 个 Coach 投影是另一来源视图，和 Stage02 的语义重叠待核。历史 S4 对 `SHOT_TENDENCY` 的一次 `95→96` 实机写入有 Getter 与精确批次证据。资格和剂量授权分开，研究因果覆盖仍为零。

R0 两次重复的 44 场均有不同结果指纹，35 场可比比分均不同，16 场胜方不同，9 场比分未知。Human 收口于两次重复。旧 461 roster、302 eligible 与 44 场赛程只用于方法和波动参照。以新的绑定采集重建资格和机会，沿用 [R0 Draft PR #36](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/36)。

## 预注册与估计

1. 用现有 WorldData `read_binding`、GameMode、roster、player-state、player-skills 和 schedule 采集绑定 `save/worldline/season/epoch`、源单元、名单和完整待赛表。按 R0 的唯一 UID、可寻址球队 slot、健康、位置、近 21 日至少三次同队 10 分钟实际出场和至少两场计划机会筛选。明确赛季前瞻事件、跨日停界和哪些队伍资料不全。绑定漂移或队伍无合格候选须先补采或预注册新设计。
2. 冻结六个五队区组及每队一个球员。组块在随机化前根据球队赛前强度、球员位置、近期分钟和 FGA、起始倾向、赛程强度和对手暴露匹配。保存原始特征、标准化、缺失、匹配规则、平衡报告与区组名单。当前程序消费该预冻结区组，组块优化和真实可比性尚未实测。
3. 固定 seed 与身份后按 SHA256 排序，每组分配 H/L/C 和两个保留队。H/L 候选剂量相对基线 ±5，C 保持自然同期基线，保留队只贡献赛程和对手暴露。一队一人一主因素。计划必须同时记录作用 UID、基线、目标、空的实际施加值、Game ID、主客队和两侧处理标签。首个通过的实机窗口优先短于 7 天。
4. 主指标为预选球员每个预登记赛程机会的 FGA。已确认 DNP 记录零出手并保留真实零分钟。来源缺失记 NULL，保留缺失原因与分母。以区组内队级平均 H−C/L−C 作筛选效应量。次指标分别报告分钟、FGA/36、同 Game ID/Unit 的球队出手占比、队友出手和对手暴露。主估计保留总效应，分钟属于可能受处理影响的结果。真实 Touch 和 Shot Location 缺源时留 NULL，代理指标单独标识。
5. 同队、对手和重复比赛相互依赖。首轮只给出区组对比、暴露计数、机会和缺失，CI 为空且状态 `UNDERPOWERED_SCREENING_ONLY`。确认轮事先登记最小有意义效应、样本与停止规则，按组块随机化推断或相应依赖模型估计区间，确认多指标时预登记检验族与 FDR。R0 自然波动用于设计敏感性，避免将玩家场次当独立样本。
6. 后续轮换仅使用有资格且获批的对象。已处理队的残留剂量、成长、伤病、交易、阵容与赛程变化进入证据账。恢复值需要单独纳入批准与 CAS。恢复值不能撤销已产生的比赛历史。跨独立世界线的关键复证保留 W0/WP/WC/WI 的设计和来源轴。
7. 每轮追加 `hypothesis_version, preregistered_at, seed, identity, round, assignment, planned/applied, Getter, exact plan digest, game_ids, source_units, opportunities, exposures, uncertainty, contradictions, confirmed_scope, remaining_gaps, next_test`。事后更新标 `POST_HOC`，独立复验前保留原假设、反证和失败收据。未来知识索引只引用有可追溯证据和限定场景的记录。

## 复用接口与运行边界

| 组件 | 来源与接法 | 当前验证 |
| --- | --- | --- |
| 日期和原生模拟 | #39 的 `read_native_today` / `simulate_to_native_date` 测试接口。Getter 的可运行历史源在 #38；Simulator 的原始实机脚本及 REA 回执由 #39 归档。 | 已复核原始 13+53 场、两个目标日期、下一日未误模拟。第二段 Box 消息日期标签写死为 12 月 31 日，精确脚本哈希证明实际两次读取均要求 1 月 7 日。另有独立赛程读回。前台之外、异常码和重载仍开放。 |
| Setter | 复用 `SeasonCycleHost`、`DecisionOutbox` 与 REA Bulk。通过已批准 role manifest、同队 1–3 人、精确 batch SHA/plan digest、CAS 及 resource claim。 | 主线 S4 有一笔 `SHOT_TENDENCY` 内存写入证据。没有针对本轮实际 UID、目标值与世界线的批准。 |
| 赛果 | 复用 WorldData v24 和 `CalendarSimOrchestrator.verify_game_sql_integrity`。按 Game ID 与单元核对 Final、WasSimulated、比分守恒、球员和球队身份。 | fixture 检查缺场、混单元和比分不守恒。真实 Host/REA/WorldData 串联待 #39。 |

离线 `window_harness.py` 支持 plan、dry-run、one-window、inspect、reconcile、stop。只使用合成端口，每个计划独占一次尝试目录，先登记意图再发模拟，UNKNOWN、CAS、进程崩溃、缺 Box 等均停止。生产并发与故障恢复沿用原 Host/Outbox 和 #39 日历锁，不由离线日志提供。

`read_observed_window.py` 将同世界线的赛后 WorldData 精确采集单元转换成分析输入。任何计划赛果未通过都会留下逐场原因并阻止效应分析。即使所有赛果齐全，真实处理效应仍须核对独立的 Setter 收据。

`verify_round_application.py` 将已经执行的 S4 单项封包、结果和独立 Getter 绑定到预登记计划。私有证据目录以 `s4-receipts.json` 索引各批次的 seal、result、getter 文件名和摘要。操作者提供索引的独立摘要。该入口只核验已发生的处理，控制组及赛前漂移的同源读回另行保留。

`analyze_bound_round.py` 读取同一私有目录下的 `s4/`、`pre/`、`post/`。操作者分别提供 S4 索引、赛前和赛后 `refresh-report.json` 的独立 SHA。赛前复核所有 H/L/C/保留球员和待赛集合。输入完整才能运行筛选估计，首轮不能据此宣布发现或认定效果不存在。

到批准终点，冻结完整季检查点，列出覆盖、窗口和已完成 Game IDs、保存证据、未决原因。连续成长或长期效应优先建议 Human 手动进入下一常规赛。复核强反证或需要清除处理残留时，建议 Human 恢复冻结起点到隔离槽。只在私有渠道交付槽和备份路径、哈希、目标日期和首条只读核验。Human 完成后重新绑定槽、原生日期、世界线、SQLite 及有效委托，继续原 Issue。

`season_checkpoint.py checkpoint` 接收已核验现场摘要、赛季最后日、停止原因、研究意图、冻结备份 SHA 和逐窗回执索引。输出保留已核对 Game IDs 与未决窗口。UNKNOWN 等异常先做只读对账，若确需重置再建议恢复冻结备份。正常季末根据研究意图给出续季或恢复建议。Human 选择后，`verify-rebind` 校验该选择对应的精确检查点、新采集、常规赛阶段、实际槽及对应世界线或恢复摘要。两个命令都要求独立提供输入 SHA，只校验已核验来源之间的一致性。新一轮权限仍需重新核对。

`current_schedule_observation.json` 是 2022-01-07 现场只读核对。本次候选周 50 场待赛覆盖 30 队，1 月 14 日另有 9 场待赛。它尚无同一新鲜 WorldData/Save 绑定和候选 UID，故与 30 队合成可复算计划分开。现场执行须使用更短的 #39 首窗验证以及后来预登记的真实计划。
