# VAE 机制参数反馈验证 · 复用世界数据采集候选的云端调研结论

日期：2026-10-31。角色：VAE decision_architecture。**研究与规划记录；未派新工程任务，未授权或进行实机采集、设置写入或新测试。**

## 本次固定来源
- 世界数据工程分支`task/nba2k22-world-data-full-implementation-20261024`，HEAD`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`，稳定基线代码`cbdaba0cb263083ea04171f8222aab65a00e3d30`。
- `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/BASELINE_HANDOFF.md`：Schema v24，**100张STRICT表、1775列**、1470952行含来源账本、42成功采集单元、20 Reader族（16普通、4按游戏赛季年刷新）。
- `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment37/source-coverage.json`：20 Reader 各自LIVE_READ/PARTIAL和落表来源计数；`table-inventory.json`、`field-maturity.json`：已落表≠每字段含义已核实。
- `world_data_prototype/refresh.py`：`refresh-world auto <save_dir> <loaded_filename> <new_output_dir> --families ... --data-updated`；逐族原子采集、非一瞬间一致性全局快照；无自启动后台调度。
- `world_data_prototype/live_reader.py`：以`0x1010 VM_READ|QUERY_LIMITED_INFORMATION`附加游戏进程，未实现游戏写入/注入/自动提权；本地访问依 Windows 进程权限。
- `world_data_prototype/engine.py`、`observation_scope.py`、`query.py`、`schema.sql`：每存档独立事实库，成功单元+来源SHA与观察时点、append-only、as-of回看、公开角色查询与owner数据库分离。
- `world_data_prototype/BASELINE_HANDOFF.md`明确：原正式候选本轮是常规赛工程基线，独立审核、跨季全生命周期和全字段UI语义尚未最终完成，`master`未包含该支完整候选。
- VAE当前审结`a15079c425bb2f228afa333dee70df5cde12039c:01_os/07_content/_runs/run-20261031-nba2k22-vae-mechanism-integration-independent-review-001/08_结论/consolidated_independent_review_and_remediation.md`为REWORK_REQUIRED；旧VAE Native模拟公式/字段ID不得作为默认可信测试策略。

## 可用范围与缺口
世界数据样例库实际存在`player_tendency_snapshots`（9822行）、`player_attribute_snapshots`（9822）、`player_game_boxes`（26400）、`team_game_boxes`（2124）、`team_tactic_settings`（90）、`gameplan_observations`（1740）、`game_setting_observations`（1092）、`player_training_observations`（912）、`player_health_observations`（6780）、`game_mode_observations`（9）。数字只表示历史样例数据，**不代表当前存档有相同条数、当前每字段可实时准确读到或所有统计单位已核实**。例如`player_game_boxes.minutes_raw`单位须核实后才能计算FGA/36，`possessions_raw`含义/来源必须核实后才能计算Pace；单个赛末体能不支持估计第四节内体能下降斜率。FGA、Tempo、Fatigue三个VAE研究方向可以据此形成可执行的逻辑采集需求与缺口清单。

## 采集体系临时复用决定（候选，待最小本地烟测）
1. **读源**暂候选为WorldData v24 `refresh-world`；输出到独立专用**测试存档的世界事实数据库**，不要使用历史事实库做破坏性测试，不要写入真实NBA2K22存档。把该分支的固定SHA和代码版本作为底线，不能误称已经合并master或正式量产。
2. **写源**只能是REA经既有权限审查的原生Setter/Action。世界数据采集器不得用于执行任何游戏数值变更。
3. **必要本地小烟测**：核对使用中的Human声明存档、PE/build/PID权限；在已有可授权的目标测试存档上，完整跑一次指定Reader族`refresh-world`，校验SOURCE LIVE_READ、`success`、`completeness`、实体ID与数值单位，库查询能把本次和早期`as-of`结果分开；游戏进程不能访问则登记BLOCKED，不自动提权；无本次动作授权时不执行。
4. **必须`--data-updated`**：同一天进行REA设置改变后的再采集要显式声明数据变化；并记录设置作用生效点。游戏推进后的采集保留Native日期/阶段/游戏列表、完成和未完成比赛分别可辨。
5. 16 ordinary Reader按需要选择：`schedule`,`game-mode`,`player-skills`,`organization`,`lineups`,`planning`,`settings`,`player-state`等，按真实依赖选，年度4族不要因为每周测试而重复采集。
6. User normal-play推进（周/月/赛季）由Human亲自操作；采集前后确认同一save、build、比赛模式、USER/CPU、节长、两种Normalize、控制/对手等。source不完整/跨赛季迁移时禁止自动拼接数据。

## 可解释的批量实验设计
每个实验组需`mechanism_id / target_field_id / role/entity / sample_id / source_version / pre_value / new_value / method_reason / expected_primary_and_side_metrics / data_requirements / observational_window / comparator / interference_group / native_write_receipt / post_readback / result / evidence_grade`等语义，不锁定SQL/JSON物理结构。

**一轮允许批量执行大量经授权、预注册的调整，但必须满足分析的因果识别：**
- 只有各自独立球队/球员且关键交互不重叠的单杠杆实验才能尝试单项归因；当全队教练POE改变时，队内球员倾向同时改变构成交互/混杂，不能分别当作单字段独立效应。
- 对交互关系，应以球队为簇分组、设置对照簇、分期批次或明确2x2对照（none / A / B / A+B），并且有必要的相似度、样本和覆盖能力。不能凭不同对手赛程或同时批量调整后单次均值差就宣布每项因果已证。
- 对全局滑块/Normalize/联盟设置，单存档同时调整全局设置不能创建同一存档的未处理对照；优先独立测试存档/不同时段/不直接因果宣称。
- 每个对象的`Before`含原值与校验/基线窗口，执行REA后即刻`S1`只读读回验证参数实到位，正常游玩后`S2`采集结果，统计/赛季累计按前后窗口和新增实际完成比赛去重。
- 结果用Python/SQLite确定性计算：给出公式、单位、分母/样本、类别、置信或不确定范围（合适时）、反事实可比性、失败/负效应/INCONCLUSIVE，不直接让模型凭记忆算术。
- 首批只选少量、相互不干扰、数据覆盖已证的示范机制，例如2-4类代表项目，验证反馈链，而非直接把204个数值一次全改；实际批量多寡由数据有效性与实验单位决定，不设未经来源证明的固定最大数。

## 研发验证 Loop 与工程执行批次
预条件：Gemini收到VAE固定审核REWORK_REQUIRED返工并先闭合P0身份/算术/实验桥证据边界，至少不能给出来源相矛盾的Native确定性建议。
执行：`Baseline(S0)→ Human审批的REA多组原生修改→ ImmediateReadback(S1)→Human游戏推进→ PostCapture(S2)→ deterministic Python Stats→ evidence classification→ method revision→ next candidate`。
先用历史fixture和真实旧数据作**流水线功能测试**，不当作新实机因果证明。试验阶段必须独立授权，结果历史只追加、失败可回退，真实数据才把`PENDING_GAMEPLAY_VALIDATION`提升为结果有限的证据。

Gemini Flash纪律：任何数值/百分比/概率/矩阵差分必须运行Python或已有确定性验证工具；每次调用只处理一组3–5条离线计算/修复事项，保存checkpoint并硬停止交接，**不能用自然语言指示“不要一次做完”作为唯一限流**；强制本地任务计数器并由外部调度仅放行一个批次，运行结束自动退出（是否能真正实现取决于执行者界面/Host门控能力，未在本轮开发）。`loop`意味着下一次由Human再次触发同一任务检查点，而不是后台无人值守地无限运行。

## 尚未决议及处理
- 100表世界数据来源是否是用户当前加载存档可读——**未在本规划窗口进行Windows实机或数据库烟测**。
- 新D系列采集还未实现，不可把旧WorldData schema v24硬升为正式长期数据规格；VAE只写语义需求+版本适配层。
- 是否同一批次修改大量设置/权限、指定测试档及回退条件需Human批准，并由REA执行模型操作；本记录不授权。
- 下一工程包只需一个`WorldData Read-Only Adapter + VAE Evaluation Harness`开发合同，在最小烟测通过且Gemini当前P0返工验收后发布，避免同时污染现有任务。
