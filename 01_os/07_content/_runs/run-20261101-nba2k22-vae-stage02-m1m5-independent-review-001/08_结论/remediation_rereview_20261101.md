# VAE Stage02 M1–M5 · 六项定向整改复审

**审核角色**：`independent_review`（GPT-6，同一Human批准的审核工作台，不伪称新隔离模型）  
**整改固定代码/文档 SHA**：`c812042e087f4c7000d27ac42d3839741039c188`  
**原待整改 SHA**：`cf95f2451bbe5722b6d946434078c515564252a9`  
**上一正式审核**：`553ee3af68dba5cd42e52969e739ab0748989faa`  
**WorldData v24审查源**：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`；GPT Sweep1 `f3233d285300ac40933b04e8086cf631fad46fbb`。  

## 结论：PASS_REQUIREMENT_BASELINE_WITH_RESEARCH_GAPS

按Human最新明确尺度：**只有影响研发目标、业务行为、数值真实性、原生与派生来源的误判、主键/关系逻辑错误或违反操作权限的重大缺陷才阻塞**；文档细节、少量未归一的UNKNOWN分类、尚需后续实机验证的研究项原则上不阻塞。本次仅复核上轮6项发现和必要回归，不重新启动204项全量语义挖掘。

**六项全部可关闭**：P0 2/2，P1 2/2，P2 2/2。M1–M5目前可作为**下一规划/原生Player Card Advanced、Per Game、Game Log数据发现/D系列Reader需求收敛的语义基线**，不必重复返工，不必等204项机制全部实机证明。只有`STAGE02_REQUIREMENTS_REVIEW_PASS`，**并非**`NATIVE_GAMEPLAY_VALIDATED`、`PRODUCTION_GM_ENGINE_READY`、`Human_A_v1_APPROVED`或任何代码合并授权。

## 六项闭环核验

### P0-01：Reader来源过高认证 —— 通过

按固定v24 `field-maturity.json`逐项核对新的`data_source_gap_matrix.gaps`：
- 7项`team_game_boxes`对应列0/2124非NULL，统一降为`SCHEMA_PRESENT_OLD_SAVE_VALUE_NOT_OBSERVED`；
- 2项对手FGA/3PA没有该表对应直接列，改`JOIN_OR_NATIVE_SOURCE_DISCOVERY_REQUIRED`；
- 4项球员Box仅作为`MATERIALIZED_RESEARCH_FIXTURE_REPLAY_ONLY`；
- 节比分为`MATERIALIZED_PERIOD_RESEARCH_FIXTURE_ONLY`；
- 球员属性快照为`MIXED_ATTRIBUTE_FIELD_LEVEL_EVIDENCE_REQUIRED`，不因`overall_raw`全NULL抹去其余有证据列；
- 旧Player PTS单独明确公式派生。6类`7+2+4+1+1+1=16`，和旧16项全部逐项对应。当前MC实例仍`NOT_RUN`。

**已消除影响下一数据任务的“有表/有行=有真实原生指标可读”重大风险**。

### P0-02：PLAYER_PTS的原生与派生混淆 —— 通过

`player_game_boxes.points`保留26400条旧值，但`reader_current_status=EXISTING_DERIVED_OLD_SAVE_VALUE`，引文完整保留`DERIVED_WITH_FORMULA: 2*fg_made+three_made+ft_made`。M3同样标`EXISTING_DERIVED_OLD_SAVE_VALUE`，精确游戏计算的Native值为`UNKNOWN`，没有把旧公式自动投入VAE或替代后续游戏内原生指标。

### P1-03：M2末端与M3具体Native指标JOIN —— 通过

68节点、50条原有假说边不变；15个`OBSERVABLE_METRIC`节点逐个增加`metric_requirement_ids`，均引用38项规范统计需求中的真实ID，并保留一对多及数据粒度。复核3条`sample_end_to_end_traces`的每段`edge_id`，路径源/终点连续且目标指标存在：
`Shot→FGA`、`Tempo→Pace`、`HelpDefense→Opponent3PA`。相应`metric_bundle_mappings`也全部一致。没有将未验证行为边提升为已证明因果。

### P1-04：GPT历史异常逐字段可定位 —— 通过

直接读取固定GPT源审计 `sweep01_full_204_static_audit.json`，统计吻合：24个来源元数据缺漏条目分布于10个字段、3个Ledger来源计数差异字段、15个无标准顶层冲突键的档案、51条`NO_DIRECT_NATIVE_FIELD_IDENTITY_SOURCE`结果。新`gpt_source_anomaly_index`索引23个去重字段，记录原审计/档案SHA路径；Stage02字段表中有明确对应索引入口。异常未被“修好”或转为已证Native，但可追查，不影响本次需求基线。

### P2-05：发布收据时间范围 —— 通过

新增`targeted_remediation_verification.json`，区分早先预发布静态验证、本次修正输入`0b078012087707f4cbf527d7536af456b3ae7f04`及实际远端最终提交`c812042e087f4c7000d27ac42d3839741039c188`。GitHub固定比较`cf95…c812`得到**4个新增提交、11个变更路径**，均在Stage02原Run内；master未移动。这已满足当前静态文档交付的发布可追溯要求；不会要求提交在自身内容内提前写出其未来哈希。

### P2-06：12个孤立研究节点 —— 通过

确认`isolated_nodes_declared`包含12个真实无边节点，所有相关节点标`UNLINKED_PROSPECTIVE_NODE`；不存在为凑数量捏造的语义边。`POEOffense3`与篮板取舍仍只作为待证机制假说，不当作已确认的Crash Glass原生控制。

## 发现但不阻塞的剩余研究事项

M3的`specific_game_native_status`与M4`game_native_exact_field_exists`使用不同的UNKNOWN枚举名称，且`NATIVE_DISCOVERY_REQUIRED`有时与`UNKNOWN`同义，但**读数资格与真实Native认证方向相同（尚未证实）**，不构成错误值/错误可用性的阻塞问题。可在下一D系列统一模型接入时择机归一，不需为此再开Stage02整改。

相关六项闭环以`07_测试执行/remediation_rereview_matrix_20261101.json`为机读准据。仍存在的**游戏取数真实性、Native PE、实际比赛因果、存档操作和采集系统物理设计**明确属于未来另行授权的研究/开发，而非本阶段拒收理由。

## 下一步与权限边界

**建议交规划岗位**：接受Stage02 M1–M5作为语义需求候选，按Human优先级规划独立数据发现任务：首先查NBA2K22 PC22 Player Card的Native Game Log / Advanced / Per Game真实统计标签、粒度、原生对象/Getter；其次沿已建立的38项指标需求，评估旧20族Reader哪些能够复用、哪些需要补充；后续再由人决定三组S0/S1/S2实验授权。不得默认重新计算游戏已经计算的同名统计；不得在新的数据任务之前冻结日志、SQL或采集协议。

**审查执行限制**：仅从GitHub固定SHAs读取研究资产和v24归档字段成熟度；独立进行跨表ID/枚举/原生标签/source JOIN/三条edge路径/提交变更范围核验。未运行真实游戏、旧SQLite二进制、Windows Reader、REA Setter或比赛控制实验，未修改master、开发源码、当前存档，也未取得Human对生产调参的授权。审核分支只增加本次复审文档，保留上一轮正式审查作为历史。
