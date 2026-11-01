# NBA2K22 REA · 确定性大规模批量 Native 写入自动化 · 工程执行任务

**任务ID**：`NBA2K22-REA-DETERMINISTIC-BULK-EXECUTOR-20261101-001`
**固定代码起点**：`3bbcbcaad98db6b9492ed915ce93aac076550c4f`
**工作分支**：`task/nba2k22-rea-deterministic-bulk-executor-20261101`
**OS岗位**：`execution`，执行模型如实登记。
**授权限制**：本任务只批准**离线开发、合成内存测试和原始日志只读性能审计**。未批准 Frida 附加游戏、Native Setter、修改游戏、更新存档、推进日历或采集新数据。不要影响 Human 当前正在进行的 Lillard 实机验证。

## 一、Human目标和已经发生的事实

Human已授权过**单次** Lillard SHOT_TENDENCY 95→80 实机写入，Gemini在真正NBA2K22.exe获得 Getter前95/后80、物理内存后80的证据，Human称游戏UI也看到了修改。前次自动化+排障流程耗时约10分钟，目标是改进为稳定参数化操作，不是继续人工脚本诊断。该授权仅覆盖当时一字段，**不能继承为本次万级批量写入的授权**。

未来运行时，Human/角色模型可提供数百至上万条具体“对象/字段/旧值/新值”修改，自动完成安全预检、执行、独立核验和轻量收据。服务球员倾向、部分属性、教练已恢复设置等**已有合格原生动作**；未恢复原生逻辑的机制必须`UNSUPPORTED`，绝不直接raw-memory-writer兜底。

## 二、先复用，而不是重复发明

**必须先逐项审查当前代码并给出真实适用范围**：

1. `research/rea_native_control/role_batches.py` 中 `RoleActionBatch`/`ExecutionAggregator`/`ExecutionJournal`/`NativeActionDispatcher`：已具备权限、依赖、跨指令冲突、原子资源 claim、stop-on-unknown 和 at-most-once 语义；测试多为 fake transport。当前算法对大型批次可能 O(n²) 冲突比较以及对已有资源线性扫描；改进须保留可复核语义。
2. `PLAYER_PATCH_TENDENCIES`/`PLAYER_PATCH_ATTRIBUTES`/`COACH_SET_KNOWN_CURRENT_SETTINGS`：已有按同对象多字段编排，但没有通用数千对象一次执行的原生 runtime。PATCH依旧非原子，不能宣称整批事务安全。
3. `transport.py`：当前每个单action创建随机工作目录、写program、调用powershell子进程及 Frida；`runtime/gui_once.js`：每程序Hook一次游戏窗口线程。**调度层必须尝试在受控有限会话/分块中减少重复附加和原生绑定初始化**，不要对10000个字段发10000次独立会话或GUI Hook。
4. `validation_batch.py`/`run_validation_batch.ps1`：仅小规模有限验证序列，`READ_ACTIONS|EFFECT_ACTIONS` 中没有通用 PLAYER_SET_TENDENCY；不当成已具备万级批改能力。
5. 本次真实写入收据 `run-20261101-nba2k22-rea-phase-a-readonly-preflight-001/06_执行/lillard_shot_tendency_modification_receipt.json`；可从 Gemini 本地保留的`runner.log`、`rea-stderr.log`、Frida Evidence（只读）分析约10分钟中诊断/attach/GUI消息/编译/单次Setter/回读的各耗时，**不得假定所有字段单次调用需要10分钟，不能编造perf测量**。

## 三、设计兼容现有 OS 能力的参数化批次引擎

希望提供可用的命令行接口：`validate`、`dry-run`、`compile`、`offline-test`、`inspect-receipt`、`reconcile`。可准备`execute-authorized`的代码入口，但默认关闭，且本次**禁止实机调用**。不需增加独立的角色/权限系统或新的Canonical Workflow阶段，直接复用现有角色能力与授权边界。提供最小易读的JSON/JSONL输入示例，确保任何人可以只改参数填写修改目标。

建议输入契约：
- `batch_id`, `save_instance_id`, `game_build_sha256`, `expected_process_identity`（实际PID/creation-time只在现场获Human同意后绑定），`authorization_ref`, `source_snapshot_ref`, `dry_run`。
- 每条：`intent_id`, `action_id`, `team_id`, `player_id`或已绑定实体、`field_id`, `expected_before`, `value`, `source/justification`；同对象多字段可按字段族合并，但保留每条intent+结果。
- 例如单字段的`expected_before=95`是硬写前CAS比较；原`player_stats.js`只验证值域而**没有比对特定expected_before**，本次必须补上。没有原值证据可先做显式本地/Native只读预检，不许隐式填95或直接写。
- 完整预校验：数据类型、显式值域、分支固定构建和bindings、权限/phase/role、跨保存线/ID、重复目标、相互矛盾预期、资源冲突、当前菜单和受支持对象生命周期。
- No-op：当前值等于目标值时明确记`UNCHANGED_ALREADY_TARGET`，若预期原值不匹配仍应阻断或要求有证据的Human裁决；不能无条件跳过。
- 计划、编译产物、输入快照和授权范围用canonical hash绑定，运行中不可修改计划。现场Human单次授权应限定`plan_digest` + 具体目标/字段/值 + 绑定游戏/save/epoch + 最大改动数/调用预算，不能靠一个文字“允许批量”无限扩张。

**运行策略**：分块分组（按队伍/对象/Setter族等），对每个受控块只准备一次脚本、一次短期Frida附加、一次安全的游戏线程执行入口，块内串行执行原生调用，不并行写游戏内存。块大小与游戏主线程消息预算可配置且经合成/后续小规模实测定标；禁止由10000次Native调用长期占用游戏主线程导致卡死。严格超时、每块有限read_bytes/native_calls、进程epoch与绑定守卫、游戏生命周期切换立即停止；错误时保留已做的前缀结果，不写后缀、不自动重试或反向写入。仅在已有已知 Getter/Setter契约内实现。

每个目标至少应记录：`intent_id`, `target`, `field`, `expected_before`, `getter_before`, `requested`, `getter_after`, `raw_after(if justified)`, `unaltered_fields_check`, `outcome`, `source_unit/exec_evidence_id`, `timestamp`, `chunk_id`, `saved/unsaved/unknown`。完整游戏原始内存与敏感指针不提交GitHub。核验失败标记`UNKNOWN_EXECUTION_OUTCOME`，不得谎称没写入；恢复/补采集只能按Human批准的独立动作进行。

**扩展覆盖边界**：已恢复的Player核心（目前仅能通过目标team的15人active roster定位）和合格Coach setting分开adapter；自由球员、选秀候选、G联赛/退役或非当前Roster不应凭ID猜测进入此Setter。每个字段族维护读回能力矩阵，未验证的徽章/复杂联动、未绑定Staff属性/完整战术及可能的原生副作用仅列入未来扩展，不因批量框架存在而放开。

## 四、证据分层：即时Getter、采集、真实持久性、比赛机制不能混为一谈

A. **即时Native效果**：同一受控运行块中Getter前/后、字节/不请求字段不变；记录执行原始receipt，并在可行时用第二个只读观察途径再次核对。只有A通过才能标为`NATIVE_IN_MEMORY_CONFIRMED`。
B. **WorldData最新采集一致性**：代码已确认 `world_data_prototype/calendar_sim_orchestrator.py` 的`FULL`即使没有新增完赛比赛也执行20族采集（player-skills含倾向），而`INCREMENTAL`无新增比赛可能skip。**Gemini只能由Human明确要求时执行FULL，模型不得自行触发**。新采集需使用新的output目录/采集单元，验证`observed_at`晚于写入、`source_grade=LIVE_READ`、`player-skills`真实ACQUIRED而非RETAINED/ANNUAL_ALREADY_REFRESHED；核对本次全部目标和未请求值，对未被WorldData覆盖的字段标`NO_INDEPENDENT_COVERAGE`而非PASS。
C. **存档持久性**：Human自行保存/重载，随后再由Human触发采集或允许独立读回。只有完成时才标`PERSISTED_AFTER_RELOAD`。FULL不自动证明磁盘存档持久。
D. **机制效果**：Human后续模拟指定天数比赛、自己要求Gemini采集，才分析FGA/36等变化与对照组。静态横截面 -3.25 FGA/场不是实机验收阈值。

## 五、强制离线验证与规模回归

允许合成内存/Mock Native Handler，不触碰当前真实游戏：

- 1对象/1字段，1对象10/50字段（仅其真实字段权限允许），多人多队100/1000/10000条样本；字段与队伍混合场景。
- 所有样本验证计划分块、稳定顺序、Intent→结果1:1、重复/冲突检测、反向CAS不匹配零写入、并发取消、跨存档/错进程、途中停止、崩溃、超时、慢回读、丢日志、duplicate receipt、stale epoch、invalid字段及越界。
- 10000项离线合成测试至少一组；全字段逐一反算，`num_planned=num_executed_success+num_noop+num_blocked+num_unknown+num_not_executed`严格守恒；不允许虚构真实游戏表现。
- 核实重复请求绝不触发第二次 Setter；UNKNOWN需独立观察证据才能解除字段资源冲突；断点恢复不能重放已开始或状态未知动作。
- Benchmark分离prepare/compile、单次attach启动的模拟成本、chunk执行与Getter回读、文件journal I/O；记录真实命令、运行机器、统计p50/p95/p99和吞吐，不凭感觉承诺每10000个多少分钟。
- 和现有`test_player_stats.py`、`test_role_batches.py`、`test_player_editor_read.py`及相关test一起离线运行，保存真实回执，不能为了过测简化断言。
- 自测中如果新增的会话型批量封装在游戏线程Hook运行存在定时/消息重入问题，应停止而不是擅自切主线程策略/猜函数ABI。

## 六、Loop实施与交付门

执行有真实证据的内部增量：①现有能力审计和10分钟耗时归因 ②参数合同/计划/权限/CAS ③单会话分块调度与异步证据/Journal ④合成10k规模重放和失败注入 ⑤测试、必要修复及成果收据。实际迭代轮数由证据决定，不要求强凑5轮。保持`loop_iterations.jsonl`与`loop_summary.json`，严格区分首次交付后定向整改与内部增量；不新建正式审核窗口，不触发master合并。

**交付产物**：可直接运行的批量工具代码及适当测试、JSON输入例、清晰CLI用法、支持字段/实体矩阵、10k合成压力测试与耗时分解、可追溯单字段收据、真实游戏未来小范围验证方案、明确STOP与Human授权门。数据库/二进制/大型备份只留本地，GitHub只提交轻量代码与测试回执，确保整个任务在其分支完成。

**正式完成判定**：`OFFLINE_BATCH_ENGINE_READY_FOR_GRADED_LIVE_TEST`，不是生产万级操作的`LIVE_CERTIFIED`。等Human认可并允许后，再走单字段已有Lillard回放证据→2-5字段受控实机组→单队小规模→多队短分块，逐级证实吞吐、确定性与新FULL采集一致性。任何实机大规模写入都要新的单次Human明确授权。