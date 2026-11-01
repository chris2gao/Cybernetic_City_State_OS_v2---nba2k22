# NBA2K22 VAE Stage02 M1–M5 · 综合独立审核报告与定向整改要求

> 角色：`independent_review`；执行：GPT-6（本对话、与本次 Stage02 执行交付不同任务；未经外部平台身份证明，不伪称物理隔离新Fork）。报告只在独立审核Run发布，不修改开发成果、Core、master、游戏或存档。

## 一、审核固定对象与正式结论

- **审核对象精确SHA**：`cf95f2451bbe5722b6d946434078c515564252a9`，父提交 `bb38b34d0ef676e9f7f5d87b60dfa439b57593ce`，含 Human 2026-11-01 长期研究原则；不能审核旧提交后假称覆盖此补充。
- **执行任务**：`NBA2K22-VAE-STAGE02-MECHANISM-METRIC-EVIDENCE-20261101-001`；原派发 `f27846c86e92345e279ad01816593d909595f472`。
- **源基线**：NBA master `45cc45cae0550ddcda192a2179ea48509b27f6ee`；Core OS `934425cf43d4fe3307b0112142aec1ba434a5734`。
- **GPT来源** `f3233d285300ac40933b04e8086cf631fad46fbb`、**Gemini REA来源** `6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`、**独立再审** `08ace12bcf92faaef20634c4701b7d6a03876a34`、**WorldData旧存档v24** `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`、固定队列Blob `af5567e14e03cd9f7761e396a978311e347d7c17`。
- **总体审核结论**：**`REWORK_REQUIRED_TARGETED_EVIDENCE_GATES`**。保留M1–M5需求与实验方案，**M3/M4旧Reader可用性和Native来源证明尚不能正式接收**。合计 **2 P0、2 P1、2 P2**，详见独立矩阵。
- **边界**：这是**静态研究、结构和证据资格审核**；游戏实机、MC当前存档、NBA2K22.exe真实PE、实赛指标、实验对照、未来D系列采集器均 `NOT_RUN`。不要求对204项全部获得因果证明，不替Human许可写入；不确定研究项继续 `UNKNOWN/NEED_EVIDENCE`。

## 二、通过的部分：不得因发现数据源缺口推翻整套阶段规划

### M1 · 204字段双流对账：结构门通过，字段级溯源需补充

独立从队列Git SHA `6436515330f77c0cc5cc675b521590adeb69c5d4` 读取`VAE_FIELD_INVENTORY_SHARED_V1.json`，确认Blob与固定值完全一致；Stage02 `field_evidence_matrix.fields`顺序和`field_id` **204/204逐项完全相同，唯一性204**：99倾向、86世界、19教练。双流GPT/Gemini SHA/档案路径逐项保留，`FIELD_ID_OR_REGISTRY/UI_SEMANTIC/NATIVE_IDENTITY/NATIVE_CONSUMER/GAME_OUTCOME`五轴基本独立，并未把Gemini的LIVE声明直接变成新独立证明。

尤其肯定：51条GPT `NO_DIRECT_NATIVE_FIELD_IDENTITY_SOURCE` 可在每条 `gpt.result` 中查到；95项没有直接竞技指标的字段`GAME_OUTCOME=NO_DIRECT_GAMEPLAY_METRIC_IDENTIFIED`，且无强加的`proposed_metrics`。但参见P1-04，24项元数据缺口、3条ledger计数和15份冲突键问题只作全局摘要。

### M2 · 机制图：数量、可达性基本一致；聚合指标映射缺失

独立核验：**68节点（唯一）、50条边、全端点存在、拓扑DAG（68/68可排序）**。每条边都有`evidence_grade`、精确SHA和来源路径、竞争解释、反证或核验门；分布为**6条未认证原生静态线索、21条外部/项目语义候选、20条待比赛验证、3条模式上下文**；**没有新增被判作已验证因果的边**。这是恰当的证据治理，不应因为Gemini上一轮法证P0没关闭就判Stage02所有需求不可能继续。

不过15个`MET_*`指标节点目前仅存描述，无`metric_requirement_id(s)`，无法沿图直接查询同一Entity/Grain的具体38指标；见P1-03。12个故意/无意孤立节点应分开记录覆盖状态，不能以节点数暗示每个都有机制路径。

### M3 · Native-First 指标需求：方向合格，部分来源等级需纠正

38项指标需求、16组Action/Setting→Behavior→Metric候选映射均存在；引用的metric_id全部能在38项清单中找到；均声明`derived_fallback.allowed=false`，保留Game Log、Player Card、Advanced、Per Game、Box、Game Reader的Native优先调查入口，细分比赛、节、赛季、3D/日历Sim、当前MC与旧存档。没有因Reader缺失就判定游戏没有指标。

但至少一个同名统计被既有旧存档以公式存储，却在Stage02被标为Native已认证来源（P0-02）；其余若依赖全NULL队伍Box，M3 Reader状态也不可当可调用事实（P0-01）。

### M5 · 三个试验合同：设计门通过，执行许可仍关闭

`PILOT_01_SHOT_TOUCHES_POE`、Tempo/Rotation和`PILOT_03_HELP_DEFENSE`等3个计划均为`NOT_RUN_DESIGN_ONLY`。S0身份/原始设置、S1单变量授权后REA Setter并独立即时读回、S2真实比赛、S3支持/反驳/不可判定判断，保存竞争解释、对手/阵容/伤病/分钟/ACE、两个Normalize、3D与Calendar分层，明确`setter_authorized=false`。这符合Human持续迭代原则；建议保留，不因尚未完成采集系统而退回。

## 三、P0-01 · M4中9个“Reader已确认”指标缺真正的旧存档材料化值或直接列

**固定证据**：

- Stage02最终：`06_执行/data_source_gap_matrix.json`（16项`WORLDDATA_READER_CONFIRMED_ON_OLD_SAVE`）。
- WorldData v24 `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`：`01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment37/field-maturity.json`（1775个字段成熟度记录）、`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/schema.sql`。
- `team_game_boxes`有**2124行**，但下列源列**0条非NULL、2124条NULL**：

| Stage02声称“已确认的可用Reader指标” | v24实列 | non-NULL / total |
|---|---|---|
| TEAM_FGA | team_game_boxes.fg_attempted | 0 / 2124 |
| TEAM_THREE_PA | team_game_boxes.three_attempted | 0 / 2124 |
| TEAM_THREE_PM | team_game_boxes.three_made | 0 / 2124 |
| TEAM_TOV | team_game_boxes.turnovers | 0 / 2124 |
| TEAM_STL | team_game_boxes.steals | 0 / 2124 |
| TEAM_OREB | team_game_boxes.offensive_rebounds | 0 / 2124 |
| TEAM_DREB | team_game_boxes.defensive_rebounds | 0 / 2124 |

另有`OPPONENT_FGA` 与 `OPPONENT_THREE_PA` 被Stage02登记为`team_game_boxes:opponent FGA`、`team_game_boxes:opponent 3PA`的**直接Reader路径**；v24`team_game_boxes`表中**不存在**对应的 `opponent_fg_attempted` / `opponent_three_attempted` 列。未来可能通过同一game_id的对手team box JOIN或其它源读到，但目前不能说这是已经验证的**直接**Reader入口。

**本次明确不做的错误推论**：0非NULL不证明游戏没有这些统计，也不证明v24所有其它历史Reader都有错；在相同表内其它`possessions_raw`等确有非NULL。正确结论仅为：**对应的当前固定旧库字段在已发表成熟度记录中没有可用材料化值/直接列，因此不能交给下游当成已证可用Reader**。

**验收门**：上述7项降级为`SCHEMA_PRESENT_OLD_SAVE_VALUE_NOT_OBSERVED`或项目现有等价证据标签；两项对手统计改为`JOIN_OR_NATIVE_SOURCE_DISCOVERY_REQUIRED`，除非另提交固定旧存档上非NULL来源和可重放的Reader查询及关联对照。更新M3镜像Reader状态，M4分类数与M06结果，使“存在表/列”“有值”“真实原生取数验证”“当前MC可读”“游戏UI原生计算存在”彼此独立。

## 四、P0-02 · PLAYER_PTS既有派生数被错误表述为“游戏直接原生已计算值”

WorldData v24 `field-maturity`记录：`player_game_boxes.points`有**26400/26400非NULL**，但`source_declaration`是：

`DERIVED_WITH_FORMULA: 2*fg_made+three_made+ft_made; AG01D fixture replay`。

Stage02 `PLAYER_PTS`却同时声称`specific_game_native_status=NATIVE_BOX_OR_PLAYER_SOURCE_ON_OLD_SAVE`、`reader_status=WORLDDATA_READER_CONFIRMED_ON_OLD_SAVE`。这描述了**存储值/既有计算来源**，不是游戏引擎在同精度/粒度上已经计算的原生统计来源证据。

Human原则不是禁止旧系统存在任何已知派生数，而是**原生与旧派生的真实性及优先级不得混淆**。这一项应标`EXISTING_DERIVED_OLD_SAVE_VALUE`及其原始输入、单位与公式；原生PLAYER_PTS仍有独立发现/对齐需求。不能自动复用公式替代原生同名值，也不要求这轮删除既有值或开发新的计算器。

**验收门**：将`PLAYER_PTS`的`game_native_exact_field_exists` / reader current status拆为真正Native、已有派生、UI候选三个轴，保留原有`points`事实的来源；用精确文件Source Reference证明Native同名字段是否已读，未证即UNKNOWN；更新Native-First验收收据，不能以`derived_enabled=0`掩盖**既存**公式派生字段被认证为Native。

## 五、P1-03 · M2图观察指标与M3/M4具体统计指标缺显式JOIN

机制图有`MET_FGA/MET_PACE/MET_TOUCH/MET_DEF3/MET_USG`等**15个`OBSERVABLE_METRIC`节点**，没有一个带`metric_requirement_ids`；它们的node_id也不等于38项`metric_requirements[].metric_id`（如`PLAYER_FGA`/`TEAM_FGA`、`TEAM_PACE_NATIVE`、`MET_TOUCHES_NATIVE`）。M3的16行`action_behavior_metric_requirements`通过field_id能提供**间接**路径，但缺与graph edge_id/observable node ID正式绑定，无法保证图末端的多指标/粒度取值一致。

例如：
- `TENDENCY_NATIVE_001 → CONS_ROLE_GOV → BEH_USAGE → MET_FGA`；最终应明确`PLAYER_FGA`还是`TEAM_FGA`，以及何种Game/Player粒度。
- `COACH_DEFAULT_014 → CONS_COACH_PACE → BEH_POSSESSION → MET_PACE`；真实Native候选是`TEAM_PACE_NATIVE`，不能默认外部估算的per48等价。
- `COACH_DEFAULT_015 → BEH_HELP → MET_DEF3`；需明确对应`OPPONENT_THREE_PA`、`OPPONENT_PAINT_FGA`等并标UNKNOWN时的可用性。

**验收门**：为观察指标节点新增明确`metric_requirement_ids[]`、对象/数据粒度和状态，允许一对多或UNKNOWN；加入M02/M04跨表参考完整性脚本，执行三条端到端路径检验。**不需要增加“证实的因果边”**，也不能为凑满指标强加机制关系。

## 六、P1-04 · GPT来源问题尚欠“具体受影响字段”索引

M1总体`DUAL_STREAM_SOURCE_RECONCILIATION.md`正确保留：51项无PC22直接原生身份来源、24项元数据缺口、3条ledger来源计数差异、15份非统一冲突键。M1里51项可用独立`gpt.result`检索到；但`field_evidence_matrix.fields[].known_conflicts`的实际枚举只包含`SEED_KEY_VS_GEMINI_KEY_ALIAS_UNVERIFIED`、`GEMINI_INDEPENDENT_REVIEW_OPEN_P0`和`NO_CONTROLLED_PC22_GAMEPLAY_CAUSAL_RECEIPT`，没有对24/3/15问题明确逐项定位。

**验收门**：从固定GPT证据源逐项建立`field_id -> source_metadata_issue / ledger_count_issue / conflict_key_issue`（如不能确定受影响field_id则明确`UNLOCATABLE_FROM_CURRENT_SOURCE`），并指向旧审计准确SHA和原文位置。可用附加`field_anomaly_index`而非强迫大规模重写204条；不虚构错误归属。

## 七、P2 · 完成收据与有限覆盖声明

1. **M09收据是Pre-closeout**：执行Run当前`verification_receipt.json`仍把`verified_source_head=7340552e...`、检查的`commits=6, changed_paths=6`、`final_commit_readback=PENDING_POST_PUBLICATION`称为`M09 PASS`。本审核通过远程Git独立确认实际分支最终`cf95f245...`，相对派发SHA为**8提交、9路径，全部在Run范围**。不能要求完成指针在同一Git提交内包含自身不可预测SHA；可另设事后Remote receipt，或将M09明写为`PRE_PUBLICATION_PASS_FINAL_REMOTE_READBACK_SEPARATE`，避免历史下游误解。
2. **M2分层覆盖未完全连通**：独立检查发现12个孤立节点，包含`MET_ORATING`、`MET_ACTION`、`CONS_GAME_STATS`、`CTX_SAVE`、`CTX_ROSTER`等；这可以是明确保留的未展开知识节点，不是必须补边。建议给每个标`UNLINKED_PROSPECTIVE_NODE`及未连接原因；`REBOUND_TRADEOFF`在M3关联`COACH_DEFAULT_003=POEOffense3`并在图中关联抢篮板取舍，只是语义候选，不能当作已确定Native“Crash Glass”控制器。

## 八、三组实验及Human长期原则专项裁定

经逐项检查，三个实验均区分：**可读的S0原始观察**、**未来才单独授权S1修改并即时独立回读**、**实际比赛后S2追加原生统计**、**S3支持/反驳/不可判定与竞争解释**。每个合同列出多目标`canonical_target_field_ids`供未来选择单因子，不能理解为一次同时调整所有字段；真正执行前还需Human/规划确认具体目标字段、原始值、改变值和回滚与对照条件。本轮 `setter_authorized=false, game_run_authorized=false, ddl_authorized=false` 均如实保留。

Human追加的循环原则已进入源文件和实际`human_supplement`字段，并保留`NO_CHANGE/NEED_EVIDENCE/EXPERIMENT_PROPOSAL/AUTHORIZATION_REQUIRED`边界。**允许在局部机制成熟后逐步使用，不等于自动允许本轮写入或调参；相关并不等于因果**。支持、反驳、UNKNOWN都应保留历史。此次无需因一个未证的Native机制而停止整个Stage02研究，更不需提前定义未来采集协议或SQL物理表。

## 九、验收状态（M01–M09）与处理建议

| Gate | 独立审核 | 理由 |
|---|---|---|
| M01 | PASS | 204唯一、顺序与冻结queue/blob完全一致 |
| M02 | PARTIAL | GPT异常未字段化；观察指标M2→M3映射缺少合同 |
| M03 | PASS（结构/等级） | 50边均未冒充独立已证因果 |
| M04 | FAIL | PLAYER_PTS已有派生值冒称Native；部分旧Reader未材料化 |
| M05 | PASS（设计） | Native-first发现、粒度/模式/Normalize保留缺口 |
| M06 | FAIL | 16条确认Reader中至少10条具体证据不匹配 |
| M07 | PASS（设计） | 3个未执行、有界、未来受授权实验具支持/反驳/UNKNOWN门 |
| M08 | PASS（范围） | 比对派发→最终8提交、9文件，全任务Run；无其它变更 |
| M09 | PASS（事后审核） / 旧收据不充分 | 最终分支SHA已实际读回，Run内旧收据仍为发布前版本 |

**下一个执行包（小范围修复）**：保持同一Stage02任务身份与所有稳定`field_id`、metric IDs、三个Pilot IDs，不重跑GPT/Gemini 204个研究，不改变游戏或采集器。执行方只需：
1. 按WorldData`field-maturity`及源码证据纠正9个Reader可用性误判与PLAYER_PTS派生身份；重算M04/M06，并同步M3指标Reader标签。
2. 为15个图聚合Metric节点建立具体指标ID映射/适用粒度；补至少三条端到端referential gate。
3. 为24/3/15 GPT遗留异常提供Source级字段索引，不能定位则显式保留UNKNOWN而不假造。
4. 让M09完成态与远端实际发布的验证范围清晰分离，保留Human长期迭代增补来源。

**复审通过的有界条件**：M04/M06不再给来源不足指标“Reader确已可用/Native已证明”的等级；M02可查询映射成立、GPT异常可追踪； M07原实验及安全门不退化。此时可裁定 **`STAGE02_EVIDENCE_REQUIREMENTS_A_v1_CANDIDATE_READY_FOR_HUMAN`**（命名建议，不代替Human的正式版本批准）。然后规划独立的D1/Native Player Card Advanced/Per-Game按需求发现、D2数据Reader缺口收敛，仍遵循Native优先和现有统一数据系统，不预设物理表或自动执行。

## 十、证据能力限制与发布纪律

审核者访问了**固定SHA的GitHub仓库文本、WorldData v24 schema.sql/field-maturity.json/source-coverage.json、Core OS标准以及完整Stage02五项矩阵**；用ECMAScript确定性检查204排序、50边DAG/引用/来源、38指标、三实验引用、Git提交范围。**并未取得游戏原始PE、当前存档、真实数据库SQLite字节、在Windows上重跑旧Reader或真实比赛**。所以v24结论严格限制在其已归档`field-maturity.json`的直接声明，不能声称重新采集游戏。Human正式批准、master合并、PRMS保存、独立采集系统发布均`NOT_RUN`。
