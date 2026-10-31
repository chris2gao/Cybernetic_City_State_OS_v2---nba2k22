# NBA2K22 VAE 机制整合 · 综合独立审核与集中整改建议

**审核任务**：`NBA2K22-VAE-MECHANISM-INTEGRATION-INDEPENDENT-REVIEW-20261031-001`  
**固定任务派发 SHA**：`3c378d05a42be50d7f105256d5bb978bd88eefa5`  
**固定 Gemini 候选 SHA**：`b3e39f867364b4610fc57f5cc798c7ab33232eeb`（父提交 `f953f622c833a40a714a6ff6055af170b2070a7e`）  
**审核分支**：`task/nba2k22-vae-mechanism-integration-review-20261031`（初始派发 HEAD=`3c378d05...`）  
**master 基线**：`45cc45cae0550ddcda192a2179ea48509b27f6ee`  
**最终审核裁定**：**REWORK_REQUIRED（集中返工）**。保留本轮研究成果；不要求这一轮证明204个字段的全部竞技因果效应。

## 1. 审核边界、方法与有效成果

已读取正式`task_packet.json`、`REVIEW_DISPATCH.md`、`verification_plan.json`及本仓库OS启动规范，按**RV01–RV10**审查。GitHub候选实际提交确实包含三项新子系统：`role_governor.py`、`coach_pacing.py`、`mechanism_graph.py`，补充`consumer_tracer.py`、`decision_bridge.py`、204条研究字段、图与三条`TELEMETRY_VALIDATION_CONTRACTS_V1`。相对父提交有217个文件变动（204个field_records）。

**有效且应保留的部分**：
- 图在当前版本**16节点、12有向边**，引用的节点均存在，确实是DAG，3条未来反馈边与验证合同在结构上相符；
- Gemini已创建可单测的三分支角色模型、节奏模型、实验性桥接器以及有意义的未来比赛指标方向；
- 所有可观察比赛效果相关边标成`PENDING_GAMEPLAY_VALIDATION`，这一保守层次是正确方向；
- 桥接类级`MODEL_TIER="EXPERIMENTAL_HEURISTIC"`、`IS_NATIVE_LAW=False`值得保留；
- 7个测试文件实际定义**40个测试函数**（8+7+5+5+5+5+5），但**仅验证源码数量**，执行方“40/40 PASS”不是审核者独立运行结果。

**限制**：本审核使用GitHub固定SHA代码和JSON、按保存机器码说明独立复原定点整数过程与REL32地址、逐项核对字段ID与图，**没有真实NBA2K22.exe/进程读取许可或原始 PE 字节捕获**，因此并不对“原始游戏真实是否使用这些RVA”作反向断言；提交里文本/常量不足以认证这一点。完整pytest未独立重跑。所有结论以本报告及`07_测试执行/independent_evidence_matrix.json`具体证据为准。

## 2. P0-01：主键关联有3个确定性错误，且均为“错误但存在”的合法ID

对比最新`06_执行/field_records`与`MECHANISM_RELATIONSHIP_GRAPH_V1.json`：

| 机制图node_id | 图的声称 | 固定字段档案真实含义 | 正确目标ID |
|---|---|---|---|
| `COACH_DEFAULT_005` | Tempo | **POEDefense2** | **`COACH_DEFAULT_014`** |
| `TENDENCY_NATIVE_002` | Touches | **DrivingLayupTendency** | **`TENDENCY_NATIVE_066`** |
| `COACH_DEFAULT_002` | POEDefense | **POEOffense2** | **`COACH_DEFAULT_004`** |

上述不是无害注释：`COACH_DEFAULT_005 -> TRANSFORMER_COACH_PACING`及`TENDENCY_NATIVE_002 -> TRANSFORMER_ROLE_GOVERNOR`被标成`PROVEN_NATIVE_ASSEMBLY`，真实查询就会将防守POE2/突破上篮倾向错误映射到节奏/Touches模型。第三个错配也污染防守POE关系。机制图的`test_mechanism_graph_initialization`、`test_forward_impact_chain_coach_tempo`甚至明确断言错误`COACH_DEFAULT_005`存在及其路径；**通过的测试本身复现了错误**。

**P0关闭条件**：修复图节点、边及全部相关导出结果；建立`field_id + canonical_key + category + value_domain`的自动关联校验；专门设置“错误但真实存在的field_id”反例，图必须拒绝或报告冲突。未来每轮字段添加不得靠人工编号关联。

## 3. P0-02：Coach整数运算并未实现所声称的Native定点逻辑

`coach_pacing.py::calculate_tempo_modifier`计算了`edx`，但最终却写成`unclamped = int(round(offset * 0.6)) + 10`，**没有用它计算出来的edx**。其`0x51EB851F`有符号IMUL高32、`sar edx,4`、符号修正指令对应的定点结果**不是**此Python的浮点0.6计算。

在限定“XMM0输入等于给定Tempo”的源材料假设下，独立用32位有符号寄存器过程的静态等价核验得到：

| 输入Tempo | Gemini函数返回bounded_modifier | 提交所列指令的计算结果 |
|---|---:|---:|
| 50 | 10 | 10 |
| 60 | 16 | 22 |
| 70 | 22 | 34 |
| 80 | 28 | 46 |
| 100 | 40 | 70 |

具体流程：`ecx=(tempo-50)*60`（i32），有符号`EDX:EAX=EAX*ECX`且`EAX=0x51EB851F`，随后`sar edx,4`，结合符号补正和`+10`、上限70/下限10。提交中的`test_coach_pacing.py`反而把`Tempo100→40`、`Tempo70→22`当成正确预期。

另有**上游/下游身份未认证**：XMM0是否确实是教练UI Tempo？`EDI`是否为比赛回合目标？`0x120bafe`的`5x+2x`究竟评价什么候选？仅有汇编算数结构，不能把`net_target`、`possession_score`直接命名成真实比赛回合数。

**P0关闭条件**：以精确游戏版本原始字节和自动反汇编核验指令地址，构建独立的带i32溢出、`cvtss2si`/MXCSR舍入及负数处理的oracle；按`0,10,40,50,51,52,60,70,80,100`及边界/负数交叉比较。区分`raw_slider`、`native_internal_modifier`、`gameplay_possessions`，未知处标UNKNOWN。不可简单把“0.6”改为另一个猜想而继续称Native法则。

## 4. P0-03：实验桥接器返回互相矛盾的结果，存在下游误用风险

`decision_bridge.py::calculate_role_ceiling_governor`仍使用旧的单`role_tier`和调用者给的`role_ceiling`；同时新增`native_eval = NativeTacticalRoleGovernor.evaluate(role_tier=role_tier,secondary_tier=role_tier,...)`，将其结果命名为`native_ground_truth`。

**可复现冲突**：取`role_tier=2, shot_tendency=88, role_ceiling=80`。桥接旧启发式计算`effective_shot_tendency=75`、`is_suppressed=true`。其内建新三分支模型在`primary=2`时选择**BRANCH_C**，table值74，按其定义有效值为`max(88,74)=88`而不是75。桥接输出仍展示“原生”分支和表，但没有显式宣告与75结果冲突。

Tempo同样一方面将原始滑块80裁成`effective_tempo=70`，另一方面内建整数模型返回当前错误的`native_bounded_modifier=28`，输出说明仍称“超过70 Native饱和”，混淆滑块与内部修正量。

**P0关闭条件**：将两个模型作为**独立、明确标注试验性的数据通道**；任何数值矛盾必须显式显示并禁止生成“Native Ground Truth”式GM建议。真正进入GM生产调用前必须有能力/权限门与证据等级过滤。对角色2场景增添负例。

## 5. P0-04 / P1：原生证据等级、角色分支和机器码可信性

角色模型`role_governor.py`硬编码表`uint32[4]=(92,83,74,0)`和`float[4]=(0.94,0.96,0.98,1.00)`，所有输出标`PROVEN_NATIVE_ASSEMBLY`；图亦把7条边标成同一等级。但在本固定提交中，未提供能让审核者核验所有基本块、原始表字节、角色身份/索引、表的对象归属、浮点舍入模式和所有写回路径的独立实机证据。**不能以候选反汇编文本或pytest fixture的自洽性取代实机证明**。

值得特别调查：模型的非核心角色Branch C把深度替补Shot/Touches最低提升到92，方向可能与直觉不同，但不能据此否定；正确做法是保留`STATIC_DISASSEMBLY_LEAD`并追真实表索引/变量单位和调用时点。另外`scaled_ratings`用Python `round(r*multiplier)`并夹在0..99，SSE实际指令、`uint8`写回及5个能力渠道含义没有足够独立证据；输入角色被Python静默clip到0..3，可能隐藏实际引擎异常值。

前次审查未关闭的源码自洽问题仍在`consumer_tracer.py`：给定Tempo机器码从`0x14120ba72`起，`mov eax,70`按字节位置位于`0x14120ba83`，而手写汇编说`0x14120ba98`；`verify_live_bytes()`在`base+0x120ba98`期待`mov eax,70`，与其硬编码byte span抵触。Snapshot`E8 0D 07 23 00`从`0x14174510e`计算目标为`0x141975820`而不是注释中的`0x140975820`。这些是提交内**代码与字节不能同时成立**的事实，不能认定真实游戏哪一种正确。

**集中整改门**：只在确有来自当前PE/受授权实机的独立原始bytes时认证地址、CALL/CFG、table及寄存器；所有其它证据按`STATIC_CALL_RELATION`或`HYPOTHESIS`保留并可继续研究。图导出需验证每条边证据和字段主键，不准默认`GraphNode.epistemological_grade="PROVEN_NATIVE_ASSEMBLY"`；DAG拓扑正确不表示语义正确。建议为role模型加入0..3×0..3路径、无效索引、0/100、负数、浮点边界、byte写回的独立负例。游戏因果作用维持PENDING。

## 6. 三项未来比赛反馈验证：当前属于“信息需求”，不是采集格式

当前`TELEMETRY_VALIDATION_CONTRACTS_V1.json`三条方向可以保留：

| 原contract ID | 应回答的可证伪问题 | 未来需要的语义信息（不指定字段结构） |
|---|---|---|
| `VAL_CONTRACT_FGA_SUPPRESSION` | 角色/ShotTendency是否影响球员实际FGA/36与使用率，幅度多大？ | 同一球员/球队/赛季/比赛身份、上场时间、出手总数及类别、角色与出手/触球倾向前后值、教练战术与阵容背景、模式/USER或CPU、有效比赛样本与对照 |
| `VAL_CONTRACT_TEMPO_SATURATION` | 原始Tempo、内部修正量和实测回合数是否存在饱和阈值？ | 教练/球队及比赛身份、Tempo实际值和采集时点、比赛长度、真实或估计的回合数及其口径、球权转换/快攻/出手时钟（若可得）、两项Normalize状态、玩家控制状态、模式/对手/阵容、有效样本与对照 |
| `VAL_CONTRACT_TEMPO_FATIGUE` | 更高节奏是否导致更多体力消耗或末节效率变化？ | 球员/球队/比赛身份、节奏值、体能前后与观察时段、上场时间/轮换、体能和伤病/训练/疲劳滑块、出手效率和第四节表现（若可得）、比赛模式/控制来源、重复与对照条件 |

**三项共同的信息需求**：游戏Build及Save/世界线身份、赛季与游戏模式（3D/日历模拟分别标注）、观察的真实时间和比赛事件时间、球队/球员一致身份、Human控制还是AI控制、调整前后取值/有效生效点、可观测性和缺失原因、真实值/转换值/计算值区别、样本有效性与重复/对照、前后同口径比较、`Normalize Stats`与`Normalize Played to Sim Minutes`（或项目实际确认的两种Normalize设置）区分、来源与新鲜度、适用范围及混杂因素。

**绝对不要求**：当前就确定`JSON log`文件格式、数据库物理表名、SQL字段、具体采集API、文件路径、传输协议、同一比赛一定要采到的全部未开放技术字段。这些是D系列采集/数据系统后续裁决；VAE只交付有优先级、有获取可行性及UNKNOWN处理的**可测试语义需求**。

三条图边`PENDING_GAMEPLAY_VALIDATION`状态正确，但描述中“directly regulates”“determines”等因果肯定语应降为待验证假说，不能因为输入→输出图存在就宣称效果已测。

## 7. 40项测试与运行时隔离的真实评价

**源码计数**：`test_verification_plan.py`8、`test_live_analyzer.py`7、`test_consumer_tracer.py`5、`test_decision_bridge.py`5、`test_role_governor.py`5、`test_coach_pacing.py`5、`test_mechanism_graph.py`5，总计**40个测试函数**，执行方称40/40通过；审核者没有独立运行完整pytest，也未证实真实原生机器码。新测试有两个确定性盲点：`test_mechanism_graph.py`明确要求错误的Tempo ID；`test_coach_pacing.py`明确要求错误的`Tempo100→40`。

**安全边界**：`LiveEngineAnalyzer.__init__(auto_attach=True)`仍是默认，测试`analyzer` fixture用`LiveEngineAnalyzer(repo_root=repo_root)`，若本地游戏运行便尝试GameMemory只读附加；`test_sweep_3_full_live_grounding`甚至在附加成功条件下执行204项实机读取。其写盘测试素材已采用`tmp_path`隔离，是有效改进，但**测试不会接触游戏进程**这一更强主张目前不成立。`consumer_tracer`的enrichment API默认`target_dir=None`仍可写正式`field_records`，不能把生产数据发布等同于纯分析。

**验收门**：所有默认单测`auto_attach=False`+FakeMemory，显式授权的实机只读试验另开单独验证运行；测试先后正式Run的hash/ledger一致；建立与原代码不同源的算术oracle、主键负例、图cycle测试、PE原始bytes/rel32负例、跨模型矛盾门；提供收据明确40个收集数/运行数/成功数并标环境版本。历史`raw_legacy_capture`统一占位时间`2026-10-31T03:00:00Z`和某些Raw bit pattern丢失需从`f1e02101`等真实Git源恢复或标UNKNOWN，不可将占位视为原始观察。

## 8. 单一集中整改包：建议Gemini同一任务一次返工，再一次复审

**P0 必须先修**（与未来真实比赛反馈无关）：
1. 重建机制图中的三处错误关联，校验全量field-ID、canonical key、表/值域和边证据等级；下游图查询遇冲突自动阻断；
2. 修正Coach定点数学，保存独立byte+register执行oracle和有符号/舍入边界测试，并不把内部modifier冒充真实比赛回合数；
3. 使`ExperimentalTacticalDecisionBridge`不再混用启发式数值与所谓native_ground_truth，发现冲突时阻断确定性建议；
4. 将当前没有可核验原始PE证据的`PROVEN_NATIVE_ASSEMBLY`降为候选和已知静态路径，不损失已有研究线索。

**P1 并入同一工程提交包**：修完整Role三分支/表身份/浮点与数据类型边界的可证伪问题；补真正的graph invariants/负例；纠正或隔离不自洽的RVA/Callsite；默认pytest不附加真实游戏且不污染正式证据；恢复历史原始捕获；把三项Telemetry扩展为语义需求（包括可得性与缺口），避免固定未来存储。不要为追求一次PASS在没有实机证据时人为补齐UNKNOWN。

**退出条件**：可提供新的精确Gemini修复SHA、字段/图关联无误、独立数学oracle对齐、所有实验模型输出不冒充Native、离线测试实际不接进程/不改正式Run、未来三条测量需求足以指导D系列而无物理协议。达到这一**有界软件/证据安全门**即可给`PARTIALLY_SUPPORTED / NEXT_RESEARCH_WAVE_READY`，长期204项因果研究按原单字段循环继续，不必等到比赛数据系统完成。

**下一责任人**：Gemini执行窗口在原任务代码/Run白名单内集中返工；OS规划岗位以后按照研究进度安排单字段深挖；Human负责任何未来游戏进程附加或数值修改权限的独立授权。审核者未修改Gemini源代码或游戏。

## 9. 审核身份和发布纪律

Human于当前对话明确批准由本GPT直接继续审核，不要求另换模型。因此本审核为**与Gemini开发独立、但不是全新物理Fork的审核窗口**。角色`independent_review`成立，`new_isolated_fork=false`如实注明；模型GPT-6，平台外部身份验证及窗口ID UNKNOWN。仅审核固定候选SHA，不以之后开发分支的HEAD替换候选。通过GitHub API只在指定审核Run写报告、机读矩阵及完成指针；不修改master/开发源码/游戏/存档，不声称已使用PRMS或正式Communication。
