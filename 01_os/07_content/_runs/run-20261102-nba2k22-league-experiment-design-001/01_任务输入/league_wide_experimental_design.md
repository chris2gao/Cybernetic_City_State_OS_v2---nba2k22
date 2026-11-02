# NBA2K22 · 全联盟多因素并行实验计划 v1（规划，不执行）

任务 ID：`NBA2K22-VAE-LEAGUE-WIDE-EXPERIMENT-DESIGN-20261102-001`
规划：GPT-6 / `decision_architecture`
基础分支：`plan/nba2k22-league-wide-experimental-design-20261102`
主工程事实基准：Host 任务 GPT-6 最新审核 SHA `25eae0063cfe72cab595263bc57c0ceb8fc22889`；**目前 Host Live Writer 仍有待关闭的接线门，不可借本计划绕过授权。**
Human 目标：把30队与约400+球员变为一张大型并行试验台，每轮尽量覆盖更多倾向、教练设置，多轮观察每一设置的效果和作用机制；Game Calendar Sim 是首要结果生成方式；Human 选择何时采集、何时做决策、何时执行、推进日期；用户可手动恢复或新建存档。

## 1. 核心认识和实验范围，不混淆变量

实验目标包含4个不同问题：
(A) Native Setter是否即时改变目标字段？（技术可执行性/Getter readback）。
(B) 该字段是否影响**日历模拟结果**？（sim mode causal effect）。
(C) 其作用通过什么可观察的中间机制发生？（FGA、3PA/3PAr、犯规、助攻、篮板、轮换等；仅使用存在的真实Native指标）。
(D) 该字段与另一字段、战术、队友、对手是否有交互？（factorial/interaction）。
一场比赛的 Box 变化不能直接回答四个问题。

字段库存档案按 `experiment_field_registry`：
- 球员倾向资料 `R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json`：99个 Native slots、48个命名位置、51个 unnamed；99个 UI Export Label **不能据位置推断成99个 Native Setter**。只有 Registry+已验证语义+允许读+真实Setter能力+Human本轮授权的字段才加入真实 write plan；51未知原生字段保持只读。
- 教练 `rea_native_control/data/coach_settings.json`：10个当前 Coach projection 候选，含 `POEOffense/POEOffense2/POEOffense3/POEDefense/POEDefense2/POEDefense3/RunPlayTendency/ZoneUsage/BenchDepth/BenchUtilization`；真实原生写入能力按每个 Action/field 独立确认，不能因 Coach投影已知就视为10项全部可写。
- VAE Stage02 204项主要是**观测/证据字段**，不是204个必然可改的设置。
- 必须区分 `LIVE_VERIFIED, TECHNICALLY_MAPPED_BUT_UNVERIFIED, READ_ONLY, UNKNOWN_SEMANTICS, NO_MEASURABLE_ENDPOINT`。初期仅 Player `SHOT_TENDENCY`有当前批量100项实机闭环证据，其他字段先离线规划/逐项资格证据后扩展。外部世界真实比赛/3D游戏和日历模拟**两个结果模式不能混为一个**，主要研究`CALENDAR_SIM`。

## 2. 实验层级：不要让同轮改动相互污染

至少三层独立实验单元：
- Player-level：本人体征、出手/触球/技能行为，`unit=player`；**同队资源分配有干扰**，其他球员 FGA 改变可能是队友倾向结果，不可把队友当独立无污染对照。
- Team/Coach-level：教练POE、节奏、轮换/阵容配置，`unit=team`；最多30个独立集群，不得把30队×15人假当450个独立教练样本；比赛对手也受影响。
- Global/World-level：赛季滑块、规则、全联盟设置，`unit=worldline`，不能用30队作为30个独立全局实验；需要独立存档副本/复赛季、且全部留原历史。
同时建 `interference_graph`：player→teammates（球权/分钟）、coach→全队、team→opponent（赛事对阵）。同一队每个互相高度影响的 gameplay family 在同一轮最多一个主处理球员；异 family 多人并改只允许作为**筛选（screening）**，不能宣称严格独立效果。比赛双方的arm标记必须进入对手特征。

**最优做法是“双轴隔离”：按对象分配+按存档世界线分配。**
同一冻结时点拷贝生成身份独立的：
`W0 CONTROL` 无新改动；
`WP PLAYER_SCREEN` 只修改当前获批球员字段，Coach保持相同；
`WC COACH_SCREEN` 只修改当前获批教练设置，Player保持相同；
`WI INTERACTION` 仅在明确需要时添加顶尖2–3交互实验。
每个世界线保存独立原生MyLEAGUE存档、WorldData DB、Outbox、plan digest、完整源 save fingerprint；同一时间点的赛程/名单/全局设置尽可能一致。不能直接把在同一个存档“每7天改不同字段”视为独立 A/B，因为赛程、伤病、发展、交易、累积比赛结果发生漂移。
**先在2次无修改的复赛季上确认游戏重复模拟是否完全确定**；不要假定恢复相同存档自动得到相同随机结果。如果不确定，则每种arm需要多独立副本/不同运行序列，评价变化分布，不用单次结果绝对归因。

## 3. PLAYER_SCREEN：一轮全域筛选的可实现容量

假设30队各有平均8名**实际获得稳定出场机会**的合格样本，最多240个球员处理槽（需现场依据真实轮换核对），设其中约20%为明确未修改的内部对照、40–60%为处理参与者、其余保留未干预保护槽/替补。这是**规划预算**而非已经核对的实际数量。
可讨论两个模式：
1. `BROAD_SCREEN`：优先覆盖最多命名可测字段。比如实际48个全部有至少3名符合字段机会条件的合格球员，则需144名处理者，另保留约48名明确对照，余48个槽作保护/未参与。48×3=144只是**覆盖量，不等于统计学效应已经可靠**；通常每字段只有1–2个高/低剂量实例，单周比赛机会不够。若 eligibility不足，字段必须标`INSUFFICIENT_ELIGIBLE_PLAYER`，绝不随机指定不会触发该动作的球员凑样本。
2. `FOCUSED_CONFIRM`：每轮只确认8–16个筛选后最有信号的字段，对每个字段分配匹配的多名球员与不同球队/角色，保留自身对照和无变动队友，收集多场实际模拟比赛；得到有用置信区间/阈值/位置异质性。
设计中`player`在同一实验时间窗只承担**一个主研究字段**；除非后期明确`INTERACTION`方案，禁止同一个球员在同一时窗同时大改Touches、Shot、Three和ISO来声称独立估计。
每个 field 根据 eligible baseline `b` 安排 `H=clip(b+delta,0,100)`、`L=clip(b-delta,0,100)`、`C=b`，初筛推荐`delta=10`或由该字段范围/敏感性选择10–15；保证有效变化`abs(target-b)>0`，并记录是否碰边界。仅允许在**可写字段**和Human审核值上真实apply。三剂量也可放在不同球员、但需要match baseline与role；不假设100与0是线性关系。
队伍/角色/轮换/基线能力/初始数值的分层：PG/SG/SF/PF/C、usage、OVR、上场时间、球队强弱、球权位置、近7-21天机会数、是否伤病。采用固定`randomization_seed`的约束随机化，先按位置和机会匹配，再为`H/L/C`分配，记录平衡检验。不能让所有H都在强队、L都在弱队。
**注意**：若一队多个玩家同时测试相互竞争的领域，即使给了不同player，主效应可能被队友/教练间接影响；标记`CROSS_FAMILY_SPILLOVER_RISK`，做确认实验时改用“一队一个核心字段”或世界线对照。

## 4. COACH_SCREEN：30队是30个实验单元而不是450个

同一单个世界线内30队不足以对10个Coach设置同时进行“上/下/对照×足够复制”的可靠估计。因此分为：
- `C_BROAD_SCREEN`：每轮30队可试探10个Coach字段，例如每字段先分2队、剩余10队暂不改；同时与独立W0同球队基线比较。这只属于**低可信度筛选**；还要记录赛程对手也被测试影响。
- `C_CONFIRM`：一个验证时窗只选择1–2个Coach字段；每字段使用匹配球队分`H/L/C`，例如30队测试2字段时每字段分15队，5/5/5。更强证据来自重复世界线的随机轮换分配和长窗口。
- 枚举型POE以准确枚举值做`A/B/C`，不可盲目数值+10；RunPlay/ZoneUsage/BenchDepth等数值用合法边界、真实readback和用户批准的微调值。
- 不把Coach字段变化当成球员独立实验；team wins/ORtg/DRtg/pace/rotation等真实可用指标，若来源无可靠口径则使用最接近 Native Box 的合法代理并标`PROXY`。
- 重要机制（Coach战术 × Player倾向）的交互在`WI`中做明确`2×2`：`(C0,P0),(C1,P0),(C0,P1),(C1,P1)`；只用于筛选出有效的字段，避免99×10全部组合不可控。

## 5. 统计结果与机会过滤

每个设置至少定义：
- `field_id, eligible_roles, expected_mechanism, opportunity_definition, primary_native_metric, secondary_metrics, negative_control_if_valid, aggregation_unit, sim_mode, lag_policy, missingness_policy`；
- 例`SHOT_TENDENCY`：主指标`FGA/36`（需要真实上场分钟）、总FGA、USG（仅当原生值真实可取）、球队队友FGA变化作为`spillover`，分场数据与持球资源竞争区别。
- `SHOT_THREE_TENDENCY`：`3PA/FGA`（有足够FGA时）、3PA/36、球队3PA；中投/三分比例可代理出手分布，不以3P%本身作为唯一主指标。
- `DISH_TO_OPEN_MAN_TENDENCY`：助攻/36、AST/TOV（真实来源可靠时），但“助攻上升”不能自动证明该动作触发次数。
- `BLOCK_SHOT_TENDENCY`：盖帽机会通常稀疏，Blocks/36、Fouls/36、对手内线机会及防守场景必须有暴露量；7天可能无有效观察。
- Coach`POEDefense`：对手3PA、内线得分（若可取）、球队失分及防守策略的读回；对手强弱和对手被调整字段应控制。
其余字段按已核准 Native 可用数据索引填写，缺原生指标标`MECHANISM_UNOBSERVABLE`，仅可测统计代理，不可造“控球次数/距篮米数/战术触发次数”。
**数据源优先级**：游戏原生Player Card高阶指标（若已实际采集并验证）→ native per-game/season stat →真实Box聚合（准确来源标DERIVED）→不可评估；Game 3D和Calendar Sim分开。缺分钟/投篮机会时本周的0事件不等于0效果。任何原生累计季数据要在两次 snapshot 相减之前确认相同口径及跨队历史，优先真实game-by-game。
强烈建议两层结果：
(i) `SETTER_VERIFIED`：按REA raw+fresh Getter-after确认参数真的写入；
(ii) `GAME_EFFECT_ESTIMATED`：模拟N场后对目标行为效应做带不确定性的统计报告。
分析模型至少含field/dose、玩家基线、role/position、team、opponent treatment、calendar week、minutes/opportunity、injury/trades、worldline replicate。球员/球队/重复游戏需要使用cluster-aware估计或按cluster bootstrap；不可把同队同一场每个player_game当独立Coach样本。报告效应量、样本、置信区间、机会充足性及多重假设`FDR`，不要只按p值/一周胜率下结论。
对无显著差异的结果分`NO_DETECTED_EFFECT_WITH_POWER`、`UNDERPOWERED`、`NO_OPPORTUNITY`、`METRIC_UNAVAILABLE`、`SETTER_NOT_VERIFIED`、`SIM_MODE_UNSUPPORTED_HYPOTHESIS`；不将所有非显著都写“无效设置”。

## 6. 多轮推进：筛选→轮换→确认→相互作用→机制知识

`R0/Calibration`：冻结起点存档、完整WorldData基准、赛程/阵容/版本、两次完全不改的同起点7天模拟，估计原生随机波动。不同世界线必须独立save-binding与DB。
`R1`：`WP`球员广覆盖筛选，约48命名字段（仅真实合格且获批的子集）；`WC`教练广覆盖筛选（仅验证的原生动作）；`W0`保留全局对照。这是一个**逻辑实验轮**，可包含多个存档世界线的模拟；若用户不想反复读档，先只跑单世界线筛选，结论等级降低。
`R2`：重新从R0相同起点生成匹配副本，交换高低剂量/球队/位置与随机序列；或同赛季顺序继续但标记有不可消除的period/carryover混杂。弱证据不应伪装R1独立重复。
`R3+`：把强信号字段放入`FOCUSED_CONFIRM`，每批8–16球员字段或1–2 Coach字段，至少多周/多个世界线重复；长期指标（成长/士气/训练）需要更长时窗、独立初始存档且禁止不验证的简单“回设值即washout”。
`R4+`：对2–3个已确认主效应的字段运行`2×2`交互场景，对单字段+两字段效果进行对照，辨别协同/冲突。
`SEASON`：Human每7游戏日触发采集与审批；多轮积累对机制的校准表。真实正常世界线的GM优化决策与实验治疗 **分开**，不可在试验世界中无记录地让AI自适应修改所有指标。
参数状态：`UNTESTED→BROAD_SCREENED→EFFECT_CANDIDATE→CONFIRMING→REPLICATED/NO_DETECTED_EFFECT/UNIDENTIFIABLE`，每轮允许对实验假设更新，但已经看过结果后变更的假设要记录为`POST_HOC`，下一轮再预注册验证。
整个赛季20–40个采集检查点只是**观测频率目标**，不保证每字段的有效暴露/足够统计力量。最终按`qualified player-games, eligible teams, opportunities, independent worldline replicas`计算证据水平。

## 7. 研发实现：把实验计划放入现有 Decision Outbox，不新造 Native Writer

建议只新增少数纯分析/分配文件（执行代码尚未授权建设）：
- `experiment_field_registry.json`：每个字段的 Native身份、可写/已验状态、层级、合法剂量、机会、主要指标、交互组、资格；
- `experiment_assignment.py`：从WorldData当前合格玩家/球队+赛程构造`eligibility_pool`，按约束随机数分`worldline/round/field/target/dose/control`，输出`experiment_manifest.json`与按game schedule构造的interference矩阵；随机化种子固定并可以复算；
- `experiment_outcome.py`：读取每个世界线经核验的WorldData snapshot、实际REA readback与新比赛历史，输出field-level `effect_table`、交互/功效/机会警告，不自造Box数据；
- Host小适配：试验决定只作为已核准`ActionIntent`放进已有Outbox，封存digest后Human明确授权，再用既有REA写入；非Live字段只产生计划不进入真实Setter。严格前置Host Live P0修复，禁止测试计划绕过。
每项意图metadata至少：`experiment_id, worldline_id, round_id, assignment_seed, treatment_unit, field_id, baseline_value, target_value, arm, expected_mechanism, primary_metric, assigned_team_id, participant_player_uid, baseline_snapshot_ref, eligibility_ref, control_match_id, interference_group, observation_window, role_authorization_ref, native_readback_ref`。
每轮 Human一段简短触发：`启动实验第N轮：按预注册实验计划给我分组、各组参数/目标/对照、计划digest。先不写。等我授权并手动模拟7天后，采集效果和生成下一轮轮换方案。`
必须先有Host安全执行，不能因“用户允许做整个赛季”理解为全部字段和无限实机修改均已授权。

## 8. 最重要的实验失败门

- 先测模拟器是否对同起点复跑确定，不同世界线生成的比赛状态和保留历史能否可靠核验；
- 一轮多个player动过同一队互相关联玩法的字段，必须标`SPILLOVER`；无法确定则不能作为纯单字段效果确认；
- Coach改变同时Player改变导致效果混合，分`WP/WC`或显式`WI`，不能只看球队差异自动归因；
- 未合格出场机会、数据端未取到真实统计、对照不平衡、模拟比赛未推进、世界线不独立、原生字段写入未证实均不得标`MECHANISM_VERIFIED`；
- 保存/恢复原始档案属于Human，实验路径不得自动把正式游戏存档覆盖；过去/新档的数据库须append-only并区分世界线；
- 允许一轮写成千数值，但不能把同一字段在大量互干扰对象的结果当作统计独立复制；出于安全只执行有Human本轮授权与已认证Native路径的部分。

## 9. 发布范围与下一步

本文件是`DESIGN_ONLY_NOT_EXECUTED`，没有修改真实游戏、存档、数据库、REA和Host代码。当前优先完成Host已有P0接线整改并在只读模式认证，再将本设计作为独立的实验规划/分析能力接入；不新建七阶段Workflow、不因实验计划去开发游戏Native日历快进。

研究方法外部参考（方法论，不是NBA2K22机制事实）：
- NIH `Parallel Group- or Cluster-Randomized Trials`（randomization unit、集群内相关和matching）：https://researchmethodsresources.nih.gov/methods/grt
- BMJ `Use of multiple period, cluster randomised, crossover trial designs`（carryover、period effects、washout）：https://www.bmj.com/content/371/bmj.m3800
