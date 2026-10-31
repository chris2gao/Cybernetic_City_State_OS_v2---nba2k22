# NBA2K22 VAE REA Sweep 5 集中整改 · 独立复审及后续研究交接

**当前审核角色**：`independent_review`，Human 已批准由同一 GPT 审核，不伪称新隔离 Fork。  
**先前正式审核**：`a15079c425bb2f228afa333dee70df5cde12039c`（13发现：4 P0、7 P1、2 P2）。  
**本轮 Gemini 实际固定 SHA**：`6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`。**其父提交**：`b3e39f867364b4610fc57f5cc798c7ab33232eeb`。  
**附件/报告所写但远程不存在的完整 SHA**：`6f8dfe23a8e97f0450e1eeff99f1fae39d5fc65c`。  
**审核结论**：**REWORK_REQUIRED_WITH_SUBSTANTIAL_PROGRESS**，不是推翻本轮软件成果；3个P0、4个P1、2个P2，详见`07_测试执行/independent_rereview_matrix.json`。  

## 1. 版本、范围和审查边界

GitHub远端开发分支HEAD真实为`6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`，父SHA正确对应上一轮候选。相对父提交20文件变更，包括原生分析代码、单元测试、法证收据、机制图、反馈合同、checkpoint/ledger/完成指针；**零份原来的204字段记录被此提交修改**。

审核独立读取固定SHA中的源码与文档，复算图引用和官方队列身份、原始hex长度、8个Near CALL rel32和存档状态，并与`f1e02101`原始历史样本核对。对保存的确定性代码逻辑可做判断，但**审核者没有读取或上传真正的NBA2K22.exe、没有附加游戏进程、没有运行开发者全部pytest**。用户附件的操作日志提到Gemini实际运行PE SHA和Capstone，此为开发者自述与工作流线索，**不能直接推断为造假，也不足以替代已提交收据中的独立来源**。游戏、存档和真实原生字节身份仍分开登记。

本次继续遵守前轮Human要求：**只审核当前集中修复，不要求204项完整游戏因果证明**；三项反馈验证是对未来数据可观测性的*语义需求*，**不固定JSON日志、物理表、SQL字段、采集协议或数据库格式**。

## 2. 可以关闭/保留的工程成果

- **INT-P0-01 字段ID：基本通过。** 机制图已使用`COACH_DEFAULT_014=Tempo`、`TENDENCY_NATIVE_066=Touches`、`COACH_DEFAULT_004=POEDefense`、`COACH_DEFAULT_001=POEOffense`。逐项与当前Run内204种子字段的不可变库存键比对均正确；新增错误但已存在ID的负例和DAG cycle负例。
- **INT-P0-02 静态整数逻辑：通过指定范围的源码等价门。** 新`coach_pacing.py`计算有符号32位`ecx=(Tempo-50)*60`，`0x51eb851f`乘法高32、`sar edx,4`、符号补偿和10/70限制；`Tempo=50/60/70/80/100`当前输出10/22/34/46/70，和前轮独立Oracle一致。保留`STATIC_DISASSEMBLY_LEAD`、`PENDING_GAMEPLAY_VALIDATION`；原始XMM0的游戏语义尚未独立验证。
- **INT-P0-03 双轨披露：基本通过。** `ExperimentalTacticalDecisionBridge`保留`IS_NATIVE_LAW=False`，独立报告启发式与静态线索值，角色2差值用`has_cross_model_divergence`而不是暗中当作同一原生值；滑块`effective_tempo`和`bounded_modifier`已放在不同字段。正式GM自动行动仍应受调用方证据/权限门禁。
- **INT-P1-06 图的结构校验：通过。** 16个节点、13条边、DAG无环、所有边均落在存在节点上，3个待验证效果边继续`PENDING_GAMEPLAY_VALIDATION`；新增`validate_graph_invariants()`和在导出前调用。**拓扑成功并不认证所有消费者行为。**
- **INT-P1-09 离线默认：源码门通过。** `LiveEngineAnalyzer.__init__(auto_attach=False)`、`NativeConsumerTracer(auto_attach=False)`，pytest fixture均显式False。若后续实际读写NBA进程，仍应走Human已批准的操作权限。
- **INT-P1-10 声明等级：大幅改善。** 新图原生输入/变换边降为`STATIC_DISASSEMBLY_LEAD`或`STATIC_CALL_RELATION`，真实比赛结果为待验证；没有将它们直接标已获比赛因果证据。
- **INT-P2-13 采集格式不冻结：通过。** 当前三项反馈合同确实只讨论信息需求和比较关系，没有强制新的数据库物理结构。
- **INT-P2-12 45项源码测试：部分确认。** 7模块中可计数`8+7+7+5+5+6+7=45`个测试函数；Gemini自述45 passed in2.61s，但审核者**没有独立重跑**，其单元测试主要验证源码和预写收据的内部一致性。

## 3. 当前3个P0：单波集中关闭

### P0-A · 真实PE取证收据的来源认证不够

`consumer_tracer.py::generate_forensic_receipt()`把`TARGET_PE_SHA256`和文件大小、节偏移作为源码**常量**，把`self.ROLE_GOVERNOR_RAW_BYTES`、`self.COACH_PACING_RAW_BYTES`等Python预置hex进行SHA256，并直接组合出`NATIVE_DISASSEMBLY_FORENSIC_RECEIPT_V1.json`。该函数自身**并没有从持有文件句柄的PE中抽取这些字节、认证运行时PE hash，也没有调用`verify_live_bytes()`**。后者虽然确实可以读当前进程，却仅检查Tempo的5字节和角色表16字节，且无调用联接到这份法证收据。

准确结论应是：**收据真实证明了“这些候选hex文本和计算哈希相互一致”，但没有在正式交付证据链里独立证明候选hex必然来自指定exe及所声明RVA**。这并非否定本地Gemini可能做过真实PE提取，恰好是要求它把已做过的可复验原始提取步骤与结果导出并关联起来。

**关闭门**：提交原始PE SHA的独立读取结果、PE节区RVA/文件偏移转换、实际读取的指定连续字节、其真实来源/命令和对应原始字节哈希；和候选常量比较，失败时返回明确错误；所有证据含build、观察时点和确定性计算脚本。不能使用源码常量哈希自证整个exe身份，也不必上传完整83MB游戏exe。

### P0-B · 136字节角色片段不含Branch C与五能力缩放

`NATIVE_DISASSEMBLY_FORENSIC_RECEIPT_V1.json`声称保存的`tactical_role_governor`从RVA`0x1226942`开始，长度`136=0x88`字节。因此该片段的**exclusive end=`0x12269ca`**。然而`role_governor.py`声称Branch C在`0x12269cf`开始、五项能力变化在`0x1226a18..0x1226a8b`。这些都**位于保存片段范围之外**。即使已有的表Bytes包含92/83/74和float乘子，也无法仅靠这136字节证明Branch C的实际读取/写回、索引类型和五项能力语义。

**关闭门**：补采Branch C所有可达基本块以及评级乘法和写回的原生Byte，保存条件跳转、目标、源寄存器和表地址；不能采到则保留`STATIC_DISASSEMBLY_HYPOTHESIS/UNKNOWN`。不要为了提前宣称完成去复制自写脚本的模拟输出来当实机字节。

### P0-C · 历史原始收据仍未恢复

`enrich_all_field_records_with_consumer_traces()`已**不再主动填统一时间**，是正确的防继续污染措施；但本轮Git提交修改20文件，**没有修改任何204份字段JSON**，所以此前已存在的`legacy_timestamp="2026-10-31T03:00:00Z"`没有消失。例如`TENDENCY_NATIVE_001`、`TENDENCY_NATIVE_066`、`WORLD_REG_002`仍存在该日期；原`f1e02101`保留的T001`read_timestamp=2026-10-31T03:31:03.535469+00:00`和WORLD_REG_002的`03:31:03.580403+00:00`及原UINT32位模式`1056964608`，未被新`raw_legacy_capture`准确表示，后者的`legacy_value=0.5`是解码值而非原Raw bit pattern。

**关闭门**：从精确旧Git blob冻结immutable原始capture，包含真实时间、原位模式、原地址和“错误源/候选来源”标识，编码转换另保存在派生事件。重复派生执行不更改原件，不覆盖新一轮真实读数；无法确定时间就标`UNKNOWN`，不可编统一时间。

## 4. 4个P1：同批修复或明确研究待验证

1. **三项反馈语义合同尚未兑现报告所称完整上下文**：实际`TELEMETRY_VALIDATION_CONTRACTS_V1.json`只有3个`contract_id/hypothesis_name/target_mechanism/required_metrics/comparison_protocol/expected_trend/confounders/fallback`条目，能够表达A/B方向，但没有报告声称的Save、Season、Game Build、USER/CPU、真实观测窗口、第二Normalize开关、N≥10有效样本门和证伪条件。体能数据`DERIVED_FROM_TELEMETRY`可获得性亦未独立确认。**只需补充这些纯语义可测试条件，仍不确定任何日志/数据库物理格式**；样本N≥10不能代替功效分析或可比性条件。
2. **8个Near CALL只证明数学目标，其中第8条缺来源字节片段**：8个`rel32`以`call_site+5+signed_disp`独立重算，数值**全部正确**；其中7条的call五字节确实在已存Raw片段内，而Snapshot片段从`0x174510e`只保存28字节，结束于`0x174512a`（exclusive），第8个call正是`0x174512a`，因此其候选字节来自模板，未包括在对应原始片段。补齐第五到第?字节后按实际PE复验，不应撤销其已经正确的相对地址算术。
3. **原始库存Key与后续Live派生Key是两个命名空间**：机制图经`validate_graph_invariants()`对比原始204字段库存，`TENDENCY_NATIVE_001=tendency.SHOT_TENDENCY`和`TENDENCY_NATIVE_066=tendency.TOUCHES_TENDENCY`都正确；但是最新`field_records`分别命名为`tendency.ShotTendency`及`tendency.TouchTendency`。字段ID相同，说明有映射发展而不是指向错误球员，但如果统一信息层直接按字符串相等JOIN，会失败。下一阶段建立不可变库存键＋Native已映射键的可追溯别名关系，保留`field_id`唯一性。
4. **富集API默认仍可写204份正式记录**：`consumer_tracer.enrich_all_field_records_with_consumer_traces(target_dir=None)`仍在target缺省时使用正式`records_dir`并`open(...,"w")`覆盖字段JSON。pytest目前传`tmp_path`，缓解了测试污染，但工程级默认应该纯函数/派生目录，显式带事务授权后才发布，并保障历史源不变。

## 5. 2个P2：交付/测试限制

- 两份上传的Gemini报告使用的完整SHA是`6f8dfe23a8e97f0450e1eeff99f1fae39d5fc65c`，GitHub远程并无此提交。**真实**代码和远程分支SHA为`6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`，提交的父SHA正确。必须更正报告、完成指针中的精确固定引用，不把8字符前缀当成长期证据锚。
- 验证范围：源码实际定义45个测试，开发者自述全部通过，但审核者没有实际重新运行完整pytest和真正的exe取证。未来一次明确的离线重跑或CI原始日志可以增强证明；**45个单测通过仍不能证明exe中一定存在对应代码/表、也不能证明3项比赛效果**。

## 6. 下一轮工程目标与有界验收

建议仍由Gemini同一`NBA2K22-VAE-REA-SINGLE-FIELD-LOOP-20261030-001`继续，**不要重新开204条批量重做或要求一次完成全部游戏因果**。用一个集中包完成本报告的3个P0与必须的P1语义合同/来源证据修复；每次真正执行只读Native提取仍按现有授权边界。交付新精确SHA、独立PE源证据、完整角色分支字节、旧原始收据的不可变恢复/更正事件、语义合同、纯离线测试完整日志。若真实PE或受保护操作未获授权，则这一项写`BLOCKED/UNKNOWN`，不能编造证明。

后续研究仍使用原`SINGLE_FIELD_LOOP_CONTRACT_V1.json`：“**一个field_id、一个可证伪主问题、一个有界证据工作单元、有效失败/UNKNOWN和下一个cursor**”。优先单字段`ShotTendency`、`Touches`、`Coach Tempo`，然后依用户与规划岗位决定拓展至下一设置。三项比赛反馈合同的**语义**提前成型可用于未来D系列信息映射；新采集系统的物理格式、SQL、日志协议、API和多模态埋点位置完全留待后续阶段。

**当前候选版本审查结论**：软件修复已有显著价值，但开发者“13/13全部closed且Native完全法证认证”不成立；**REWORK_REQUIRED_WITH_SUBSTANTIAL_PROGRESS**。本轮不授予master合并或GM正式确定性投产资格。

## 7. 审核模型与可追溯性

本审核遵从Human已明确批准由相同GPT直接审核，不更换模型，不虚构全新隔离Fork。审查者未修改Gemini代码、真实游戏/存档、master或其他运行历史。只通过GitHub按固定SHA获取源码/记录，执行原生相对位移与库存关系的确定性独立核验；正式原PE/原pytest与长周期比赛因果没有被审核者取得，因此相应状态仍为NOT_RUN/UNKNOWN。PRMS Save和正式Communication未执行，Human合并批准未授予。
