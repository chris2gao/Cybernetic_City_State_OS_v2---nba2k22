# 全机制实验工程实施方案

状态为 `AWAITING_HUMAN_IMPLEMENTATION_REVIEW`。本文件交付设计。现有 Core/NBA 仓库规则、Human 授权和原生保护门继续适用。读源固定在 NBA master `bb73a06e710158c538caf809a771eca291eee028`、V2 候选 `cdb2a3b2b9f9de79fe068b1644c6ba147d05d8e5`、日历候选 `ada6f30051eb9a2f17193af6985497eeb789ea1c` 和字段目录记录的 Stage02/R0 来源。以下新接口均为实施提议。

## 数据流与验收层级

每轮从 `BaselineManifest` 派生 `FactorRegistry × EligibilityPool × ScheduleUnit`，产生不可变的 `AssignmentPlan`。已经授权的子计划走 `RoleActionBatch → DecisionBatchBridge → BulkBatch → SeasonCycleHost/DecisionOutbox`。日历仍用独立测试入口。WorldData 返回同场同单元 Box、前后设置和事件事实。统计模块从这两类回执生成 `MechanismEvidence`。各层分别记录静态映射、物理 Getter/Setter、模拟消费、输出可观察性、筛选和独立复验。

所有 GameID 使用 `(save_id, worldline_id, season_id, game_id, source_unit)`。所有设置使用 `(build_sha, native_object, exact_field_or_slot, uid_or_team_or_worldline, scene)`。GitHub/PRMS 只保留脱敏摘要、代码版本和检查点，私有完整原始采集仍留本机。失败和 UNKNOWN 是结构化状态，重放需既有锁和可独立验证的对账。

## D1 · 通用 PLAYER Getter 与命名 Setter

- **现有** `world_data_prototype/player_skill_reader.py::collect_player_skills` 复用公开玩家投影，`player_skill_codec.py::decode_skills` 解码存储。 `research/rea_native_control/player_fields.py::validate_values` 和 `runtime/player_stats.js::executeAction` 提供候选字段合同。 `season_cycle_host.py::_get_fresh_live_getter` 核对 Native UID、球队、合同球队和 CAS，当前认证链只开放 Shot。
- **提议** 在 `player_fields.py` 增加 `resolve_exact_stat_slot(build, factor_id)`，复用 `data/player_stat_fields.json` 及 R04B 槽号。扩展 `_get_fresh_live_getter` 支持描述符型 Getter，返回 `uid, team, slot, value, encoding, source_unit, epoch`。 `player_stats.js` 消费原生索引和既有合法范围，写后独立读目标和邻域。生产权限保持按现有角色解释。
- **依赖和验收** 先回归已有 1 项，再对其余 47 个命名槽逐项资格核验。测试合法边界、错误 UID/球队、别名、描述符错构建、CAS 冲突和无副作用失败。后续 Human 单独批准在可丢弃副本执行最小剂量、双向读回和可重复性检查。候选上限 48，只有逐项实机通过才记为可写。

## D2 · 51 个未知槽的物理资格

- **现有** R04B 的 `native_slots` 固定 99 个连续槽、物理范围 `0x458–0x4BA`。 `player_skill_reader.py::skill_projection_ranges` 已保护非公开范围，编译目录的未知项仍有独立阻断标记。
- **提议** 在现有 REA `tools/` 下增加 `qualify_tendency_slot.py`，输出只读报告与可交审的 `SlotQualification{offset,index,width,encoding,neighbors,consumer,legal_values,readback_refs}`。升级 `player_fields.py` 时只接收精确 build 与资格证据的编号。校验 Getter 与独立字节读取、目标掩码、相邻哨兵、重复结果和最小合法剂量。共享位或 getter 错配进入专门调查。
- **依赖和验收** D1 的身份、Outbox 和独立读回先稳定。先验证头、中、尾与跨边界槽，再逐项扩展至 51。负例包括错一位/一字节、非法枚举、私有范围、读回残留。后续实机资格仍需 Human 批准。篮球语义可以保持未知，物理身份和安全边界必须可证。

## D3 · 19 个 Coach 研究目标

- **现有** `data/coach_settings.json` 描述 10 个候选投影，`runtime/coach_settings.js::executeAction` 有 COACH 和活动 GamePlan 的回读/复制逻辑。 `planning_reader.py::collect_planning`、`lineup_reader.py::collect_lineups` 提供部分原生读源。Stage02 的 19 条是研究库存。
- **提议** 在 `data/coach_settings.json` 增加 `default_binding`、`active_projection_binding`、枚举域及消费模式；在 `planning_reader.py` 增加 `collect_active_coach_projection`。把 Coach 带对手 GamePlan 的身份和前后源单元接入 `DecisionBatchBridge.bridge_batch`。输入为 `team_uid, coach_uid, target_projection, enum_or_dose, expected_before`，输出含默认和活动投影各自的 readback。
- **依赖和验收** D1 通用资格回执和 D6 原生权限。十个名称匹配从双投影证据验别名，另外九项先定位再写。测试错误 owner、错 enum、错对手、改阵容导致 stale 以及未知指针分支。资格验收上限 19 项，明确日历与 3D 消费边界。

## D4 · 训练、世界设置和事件接口

- **现有** `planning_reader.py::training_team_values/training_player_values` 投影 6+5 个训练字段。 `TRAINING_PATCH_CONTRACT.md`、`runtime/training_patch.js` 证实 44 个日记录组成位置的离线构造。 `settings_reader.py::catalog_layout/collect_settings` 按 RVA、偏移和类型归并真实世界设置读源。
- **提议** 扩展现有 `planning_reader.py` 的训练事实为 `TrainingExposure{team,uid,date,plan,applied,settled,source_unit}`。在 `facade.py` 的训练动作和候选 `runtime/world_settings.js` 接入白名单 getter、合法域和权限前置。复用 `native_bindings.json` 已知团队按日 Getter/Apply，单独查个人 Apply、导师关系、疲劳和成长结算。世界设置用 `WorldSettingIntent{physical_cell,scope,mode,expected_before,value,event}`。
- **依赖和验收** 先做训练动作、结算检测和两个模拟世界参数，再扩展健康、经营及成长的真实事件。训练 55 候选项、世界 50 概念全部保留，安全控制数在逐项验收前待定。测试错日期、漏结算、共享参数错误使用球队作对照、禁写隐私区、浮点范围和恢复原值。实机核验需对应可丢弃副本与真实事件，避免把训练记录的结构证明当成效果。

## D5 · 多因素排程和分配

- **现有** V2 `build_observed_round.py::build`、`experiment_round.py::plan` 可冻结单字段 H/L/C，`run_batch_experiment.py::subplans` 切短窗。
- **提议** 在该研究模块实现 `allocate_factor_windows(baseline, factors, policy)`。输入真实赛程、队伍和候选池、writer 资格、剂量边界、事件缓冲；输出逐场双侧暴露、分层分组、精确子窗和候补。加入可复算最优窗选择、五组容量目标和不可行原因，保留计划哈希、种子及独立世界线待重绑状态。
- **依赖和验收** 可在 D1–D4 并行做离线器。集成测试检查真实 GameID 只在一条世界线内唯一排程，每个处理队只有一个主因素，GameID 对照、无赛日和事件禁跨保留，未认证槽不进入可执行子计划。目标覆盖 99 倾向、19 Coach 和 2 个共享因子的第一批可排赛程，以及 103 个事件/模式保留位。

## D6 · 多字段 REA Bulk 与一次性授权

- **现有** `DecisionBatchBridge.bridge_batch`、`BulkBatchPlanner.validate/plan`、`BulkFridaScriptCompiler`、`BoundedSessionExecutor.execute_batch`、`SeasonCycleHost.authorize_and_execute` 和 `DecisionOutbox.claim_execution` 已形成认证单字段链。
- **提议** 按角色、球队、Native UID、字段/族和世界线派生 `AuthorizedSubBatch`，保留旧授权入口。封套绑定冻结基线、场次、剂量、用户权限、次/时预算、有效期、撤销和 outbox CAS。多组在同轮可并行计划，真实原生调用仍在一个安全会话串行发出。按物理资源统一锁别名，原生持久性和未知结果沿用证据等级。
- **依赖和验收** 每个可写字段必须先过 D1/D2/D3/D4。测试越界、假授权、进程漂移、重复 claim、部分失败、恢复和全局停止。验证成功的单字段路径回归为硬门，多字段的上限只能来自独立获批封套。

## D7 · WorldData 可观测数据

- **现有** `refresh.py::refresh_world` 管理采集源，`schedule_reader.py::capture_season` 提供原生赛程和同单元比分，`read_observed_window.py::readback` 校验赛果和 Box，`lineup_reader.py`、`player_state_reader.py`、`planning_reader.py` 提供轮换、健康和训练读源。
- **提议** 在现有 `schema_model.py` 加入可证的 `factor_exposure_observations` 和 `event_opportunities` 表，以 `build/save/worldline/season/game_or_event_id/source_unit` 连接。扩充 `read_observed_window.py` 输出区分同源完整、DNP、缺失、赛事特殊与分母。增加交易/合同事件和训练前后观测，待定位的 touches、区域和动作标签留空。
- **依赖和验收** D5 先固定预期机会。校验同单位、分数守恒、区分历史与现场、跨源歧义和部分缺失。完成标准是每个因素协议有可核的可用端点或明确缺项，禁止把所有注册字段都报成可观测。

## D8 · 未知机制发现与证伪

- **现有** `analyze_bound_round.py::screen` 和 `experiment_round.py::analyze` 可筛同字段出手指标。
- **提议** 新增研究模块 `discover_mechanism_candidates(exposures, outcomes, protocol)`，保留实际处理、队友和对手暴露、原生初值、同源端点与缺失。对 51 个未知槽输出按偏移索引的效应向量、反例、功效和候选解释。先用独立标签和无效对照检查假阳性，再开放多指标探索。
- **依赖和验收** D2 和 D7 达标的槽才进入分析。测试模拟混因、DNP 与缺失、方向反转、反证记录、FDR 和敏感性。不以效果相关反推唯一语义。51 槽在总账有状态，统计可识别数量待实证。

## D9 · 单字段确认、交互和不确定性

- **现有** V2 分层 H/L/C 估计保留 `complete_strata` 与 `ci=null`。单世界线曾观察效应方向反转。
- **提议** 扩展 `experiment_round.py` 的分析输入为 `ExposureMatrix`，使用按球队/赛程依赖的估计、带重复世界线的区间和事前登记最小效应。另建 `estimate_factorial_interaction` 比较四角的差中差，配对 GameID、位置、健康和初始值。把确认族、显著性校正与探索结果分开。
- **依赖和验收** 单字段物理及模式资格通过后，先筛后锁定端点、独立复验。交互至少保留四条真实独立恢复线及重复。测试无效果、有交互、Simpson 反转、对手干扰和低功效。完成标准是效应区间、依赖来源、负例与不可识别情况能复算。

## D10 · 研究历史、恢复和机制知识接口

- **现有** `season_checkpoint.py::make_checkpoint/verify_rebind`、`DecisionOutbox`、既有 GitHub Run 和 PRMS `TASK_CONTINUITY.md`。
- **提议** 在现有台账扩展 `MechanismEvidence{factor,build,mode,effect,interval,n,exposure,source,contradictions,state}`，提供 GM/Coach/Player 可查询的角色过滤视图。恢复必须比对原始冻结指纹、实际加载槽、赛季日期、名单、GameID 和新 WorldData 单元。保存重载独立认证。PRMS 使用既有显式 WriterGate/任务恢复，仅当具备用户要求和现有状态仓时提交。
- **依赖和验收** D5–D9 有可核真实证据。测试恢复错槽、重复世界线、缺失历史、派生读权限和 UNKNOWN 锁。跨季由 Human 完成，结果分世界线留存，不能借复制复用赛果。完整机制知识条目以独立复验为主要升级门。

## 实施边界与顺序

先 D1/D2 的物理资格和 D5 的离线分配，同时推进 D7 可观测性。再 D3/D4、D6 权限衔接和集中资格测试。经批准后运行首个可执行的多因素窗；用 D8/D9 的对照和重复实验提高证据等级，D10 贯穿检查点。其他构建、受保护数据、生产 G2 启用、自动覆盖冻结档、自动跨季都不在当前审批包内。其影响是其他构建不可复用、隐私端点维持不可观测、跨季需要 Human、长程实验的持久恢复需额外验证。
