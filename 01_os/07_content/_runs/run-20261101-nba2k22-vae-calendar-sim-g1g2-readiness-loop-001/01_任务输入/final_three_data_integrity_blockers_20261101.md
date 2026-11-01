# G1 一键全量采集 · 最后三项关键逻辑整改（规划总线源码检查）

**关联任务**：`NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`

**核查基准**：`28d9ba41d60b17d5e38eec1bb996a92f016a2df7`；源对象 `calendar_sim_orchestrator.py`（只读 GitHub 逐函数检查）；Human 已明确两条指令：
- `采集全量数据`：Human已声明存档、调用第一阶段所有当前已注册的适用20族Reader、落库并提取固定标准数据。
- `采集新增的全量数据`：对同一Human已绑定存档再次调用第一阶段现有全族刷新，保留旧源事实及年度策略，**不以有新完赛比赛为必要条件**。

这是开发阶段内部 Loop 的**定点续修**，不是另起任务、独立审核、额外游戏访问或新架构。之前的14专项/321回归记录保留为历史真实回执，不据此断言以下负例已经通过。

## B1 · INCREMENTAL仍有新比赛门槛（阻断 Human 第二条指令）

`CalendarSimOrchestrator.trigger_world_capture` 的 `INCREMENTAL` 分支：`not progress.get('new_final_game_detected')` 时直接 `SAME_STATE_REPEAT`、`triggered=False`。然而日历不动时仍可能有新伤病、交易、名单、训练、教练战术、倾向/能力/财务等状态变化；`test_trigger_world_capture_mode_incremental_skip` 反而把该错误作为 PASS 预期。

**整改**：
1. 同一比赛状态只表示“没有新的已完赛比赛”，**不能推导所有20族来源都未更新**。正常的Human `INCREMENTAL`指令仍要执行现有WorldData原始增量刷新逻辑（可依赖 `--data-updated`、来源更改检测及年频跳过），不以比赛是否新增决定是否刷新；如引入可信的按来源变更证据才能只跳过该来源。
2. 对相同游戏进度、**但已发生设置/名单/伤病变化**补负例，断言source更新与SQLite观察可复核；对无变化的二次采集，允许追加新来源观察（符合append-only）但不能将旧比赛误计作新增赛果。单源年频规则不改变。
3. `FULL`无新比赛仍全族采集，这部分已基本正确，不必推翻。

## B2 · R3“去重”未解决跨来源/跨采集单元混拼（阻断VAE指标可信性）

`export_vae_standard_datasets` 当前通过三个独立 CTE 依次对 `game_state_observations`、`team_game_boxes`、`player_game_boxes` 分别做 `ROW_NUMBER` 最新选择，未将Box限定为对应比赛观察**相同有效source unit**。若较晚仅采到部分来源，会把最新game状态、上次team、再上次player按game_id拼在一起。

`verify_game_sql_integrity` 有 `expected_unit_id` 形参，但主调未传入。其查询同样是 `WHERE game_id=?` 在多次采集后读取未排序的任意旧记录；可能用旧Box验新game、错误宣布成功。

**整改**：
1. 以已经确认成功、同save、同season、同game、同Calendar Sim模式的**一个有据的采集单元**或原架构已明确记录的冻结Box回用关系作为同源约束；不能仅靠各表独立“最新”。
2. `verify_game_sql_integrity` 要核对**本次refresh确实提交的新有效game source unit**（或对没有新game的全族刷新标明`NO_NEW_GAME_TO_VERIFY`，而不是偷偷检查旧赛果后发布本轮“新比赛验证通过”）；双队Box、球员Box、节分及game状态必须与匹配的source unit关联且守恒。
3. 新增两次成功采集同一场、第二次只有部分来源数据/出现新比赛状态等反例。结果必须要么来源严格一致，要么 fail closed/明确PARTIAL；旧历史不篡改。

## B3 · Manifest仍可能错误宣称LIVE/G1就绪（影响模型使用边界）

`export_vae_standard_datasets` 用整个 `capture_runs` 的 `SELECT DISTINCT source_grade` 判等级：只要任意历史来源包含 `LIVE_READ`，即使当前导出的比赛Box全是 `RESEARCH_FIXTURE`，也落入 `G1_LIVE_VERIFIED` 分支。`vae_setting_context_snapshot` 和实验合同在空值时也恒标 `READY`。`game_mode`以最后 `unit_id` 字典序推断而非可验证的当前/指定epoch。

**整改**：
1. 由**本次导出实际引用的源单元**逐项取来源等级、季节/存档/模式、数据完整度、新鲜度；不能用整库“曾经有过LIVE_READ”认证本次导出。
2. `CURRENT_NATIVE_READ`、`FULL_REGISTERED_FAMILIES_COMMITTED`、`POST_CALENDAR_NEW_GAME_VERIFIED`、`SETTING_CONTEXT_READY` 等分开定级。只有真实受控新赛果入库、对应SQL同源查实且所有必要来源成功才能宣告相应真实门通过。
3. Fixture+旧LIVE混合库、空设置快照、不完整source unit、不同保存模式和不同赛季必须测试，`READY`不可只由导出文件写出成功推定。

## 验收与下一步

补齐B1–B3的代码与关键负例，运行专项和既有回归；真实ReadProcessMemory新进程验证可以保留`NOT_RUN`，不假称已通过。所有更改限当前任务Run与 `world_data_prototype/**`，提交新SHA、真实运行日志与清晰残余缺口。

**此次只修影响Human一键全量/新增全量与VAE真实数据可信性的三个大问题**；不展开204字段新研究、全库架构翻新、过度审查文档，不需要RDC，也不重新打开独立审核窗口。

修复后进入首个 Human 明确触发的只读本地采集实测，随后才评估 S0/R EA介入。
