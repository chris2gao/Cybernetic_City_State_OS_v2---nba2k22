# NBA2K22 VAE REA · ee515e0b 集中修复复审核报告

**独立审核任务**：`NBA2K22-VAE-REA-REMEDIATION-INDEPENDENT-REREVIEW-20261031-001`  
**固定开发候选**：`ee515e0b63461ace474878dde67864f3df524cf1`  
**父提交**：`f1e02101ead9e48c0dd3591e8c76501e407acfab`  
**上轮GPT审核**：`66f84d4dee100858710425c6ea5ab63ec0c9c519`  
**NBA master 固定基线**：`45cc45cae0550ddcda192a2179ea48509b27f6ee`

## 1. 判定：REWORK_REQUIRED，局部修复有效

这次修改**确实改进原有安全与认识论边界**。已将19项明显错误的Coach数据降级；World新增3类控制器目录+按字段读数类型解码；新`read_live_field`使用安全读数并取消Coach静态假收据；51个未知倾向撤回“已确认保留位”论断；204项机制加`PRIOR_LITERATURE_HYPOTHESIS`及`empirical_causality_verified=false`。这些成果可以保留，不能按全失败处理。

**但“12项完全修复”结论不能支持。** 当前候选仍存在3项P0、5项P1、2项P2，尤其历史不可变与测试隔离问题会导致证据丢失。当前不可判定204个字段均已获得正确实机证明，也不能认定48项`LIVE_RECEIPT`有完整字段身份凭据。Human不宜按已完成版本验收，允许继续在原Gemini主任务中返工。

## 2. 固定GitHub证据和审核方法

- GitHub远端任务分支HEAD=`ee515e0b63461ace474878dde67864f3df524cf1`，其直接父提交为上次受审核的`f1e02101...`。
- 一次提交改变**212个文件**：204个`field_records`、两个`src/vae_rea_research`文件、一个新增测试、两份证据文档、checkpoint、ledger、completion pointer等，**全部在该执行任务授权目录**。
- 原始`f1e02101`文件和最新`ee515e0b`同名字段记录逐对比。原始`WORLD_REG_002`采集值`1056964608`、原始时间`2026-10-31T03:31:03.580403+00:00`；最新文件`live_value=0.5`，`raw_legacy_capture.legacy_value=0.5`、`legacy_timestamp=""`。类似地`TENDENCY_NATIVE_001`的旧独立读取时间也已从最新记录中消失。这些**原始事实仍可从Git历史f1e021恢复**，但是最新档案自身不再正确保存。
- 原有`iteration_ledger.jsonl`为204次静态研究，最新为**208条**，末四条是重复的`FORENSIC_REMEDIATION_SWEEP`，报告的48/63/93数字在checkpoint与最后事务内一致，但修复重复执行不是新的实机观察。
- 审核者在隔离的Python临时目录执行**一次双轮最小源码等价复现实验**：第一轮存储位模式`1056964608`、原始时间；第二轮`raw_legacy_capture`被最新值`0.5`覆盖，时间变空，ledger被重复追加。此最小复现不是导入原Gemini完整程序，也不是开发者14项pytest的独立重跑。
- 没有访问NBA2K22游戏进程、Frida、REA、存档或被保护操作。本次没有证据证明新候选已经在真正游戏上按修正控制器重读任何字段。

## 3. 新P0阻塞：历史完整性与不应产生副作用的测试

### REMED-P0-01：pytest修改生产证据

源：`tests/vae_rea_research/test_live_analyzer.py::test_remediation_epistemology_and_downgrade`。其`analyzer` fixture直接以真实`repo_root`构建`LiveEngineAnalyzer`，并在测试函数调用`remediate_all_field_records()`。后者以`w`改写实际任务Run下**204份证据JSON、Dossier、collision table、current_checkpoint**，以`a`追加研究账本。测试没有指向`tmp_path`复制素材。结果是回归测试改变被审查对象本身，影响Git清洁状态、证据时间及审计复验。

**关闭条件**：测试全程用临时fixture仓库/Run和伪内存，严禁修改真实项目的任何数据。加入测试前后真实Run路径Hash相等且Git工作区无变化的核验。

### REMED-P0-02：证据修复不可重复，历史捕获时间与原位模式已经丢失

源：`src/vae_rea_research/live_analyzer.py::remediate_all_field_records`。每次使用当前`live_evidence`构造`raw_legacy_capture`，随后覆盖`live_evidence`。下次再运行便从新解释值构造所谓历史原始值，并且因新结构没有`read_timestamp`而写入空时间。旧实机记录的`read_notes`也被后处理说明替代。现仓库已有四个额外修复事务，而非单次修复。本轮从精确Git父提交确认原始记录在旧Git对象中可恢复，并不主张整仓数据不可恢复。

**关闭条件**：从固定原始`f1e02101`冻结`original_capture`，记录原始位模式/字节宽度/地址/时间/进程、源blob SHA和source capture批次；derived interpretation独立保留。修复必须幂等（运行两次无档案差异、只出现必要的一次真实更正事务），不得覆盖任一历史事实。

### REMED-P0-03：48个LIVE_RECEIPT的身份等级晋级仍不足

源：同一`remediate_all_field_records`中非RAW倾向分支。只验证旧数值非空和位于0–100，便直接设置`NativeIdentityGrade.LIVE_RECEIPT`并写`LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER`。这不能判定当前读数是否确由对应字段、结构体、保存档案和目标PE产生，也未获得独立Getter/行为消费证据。

更值得警惕：类级`TARGET_PE_SHA256`等常量在**离线修复**时写入204条`live_evidence`。该SHA可作为以前选择的目标版本候选，但本轮代码没读取exe并计算哈希，不能称本次“已验证PE身份”。

**关闭条件**：分离“从旧LIVE任务得到的字节候选”与“字段原生身份已验证”。若`LIVE_RECEIPT`仅表示字节已读取，必须在契约中明确定义，给下游显式`identity_verified=false`；若表示字段身份可用，则必须绑定不可伪造的原始Getter/Save/PE证据。

## 4. P1/ P2：其余尚待校验的改动

**REMED-P1-04 世界控制器**。新`read_live_field`可根据`SLOT_SETTINGS/SLOT_TRADE/SLOT_SLIDERS`选择类型；但过去86条原始值全部从旧`SLOT_SETTINGS`计算地址读出。本次`remediate_all_field_records`仅修改元数据解释，没有实际重读其它控制器。比如`WORLD_REG_085`是`SLOT_SLIDERS`对象，却继续保存来自旧`SLOT_SETTINGS+0x00`的原地址和`1056964608`，且`research_status=EVIDENCE_ADDED`。因此63个“范围内World候选”不能自动按目标字段获得有效观察资格。正确级别应为`SOURCE_SLOT_MISMATCH/UNKNOWN`，除非独立读取已通过。

**REMED-P1-05 静态身份常量**。TARGET_PE_SHA256、TARGET_PROCESS_PID、TARGET_MODULE_BASE分别在类中硬编码，并直接写入“live”证据。应作为`intended_target`或`inherited_prior_claim`，实际进程证明必须由本次读回的哈希、创建时间、Save和场景产生；缺少时明确UNKNOWN。

**REMED-P1-06 Coach 尚未重新验证**。代码改为读取`team+0xCE8`处的Head Coach指针，再读0x160字节调用`coach_codec.decode`，这比过去`team+gp_offset`直接读字节更合理；但没有复用`CoachLocator.calibrate`中的完整COACHDATA CRC/enum、Roster/Staff归属和存档身份校验；19项仍是UNKNOWN，不能称Coach native mapping已经实机确认。

**REMED-P1-07 测试设计**。新增六个测试中多数针对纯函数，如range、float32、静态collision table；没有真实/Mock内存读出失败、错误指针或伪造验证回执的综合测试。测试中`LiveEngineAnalyzer.__init__()`还调用`_init_memory()`尝试连接`NBA2K22.exe`，没有测试环境级`allow_attach=False`门。这不是证实发生越权操作，而是回归测试不具纯离线隔离保障。

**REMED-P1-08 别名映射**。`PHYSICAL_IDENTITY_COLLISION_TABLE.json`确实存在，整理了86个世界种子在静态目录中的50个`(slot,offset)`组合和36组重叠。但是构建仅依赖源目录字符串，不是真实内存实例/Controller类型独立验证。这是`STATIC_ALIAS_CANDIDATE`，不是完整物理身份认证。

**REMED-P2-09 机制措辞**。为全部204条标注`PRIOR_LITERATURE_HYPOTHESIS`值得保留。但`TENDENCY_KNOWLEDGE_MAP`内仍有“>85确立...”“>70确保...”“直接决定”等无实证的强语气。为避免下游模型跳过证据级别，建议把阈值整体写成“未证假设/拟真经验建议”，而非已验证的引擎输出公式。

**REMED-P2-10 生命周期**。checkpoint的汇总计数`48 LIVE+63 raw-in-bounds+93 UNKNOWN=204`内部一致，`READY_FOR_REMEDIAL_REVIEW`能诚实表达“待审核”；但并不表示204个字段已认证，`latest_completed_commit`仍指旧f1e021而不是当前版本，后续必须分离原始采集批次和数据更正事务。

## 5. 旧12项审核逐条复审结果

| 上轮发现 | 本轮状态 | 复核说明 |
|---|---|---|
| REA-AUD-P0-01 | **PARTIALLY_CLOSED** | 19 Coach错误读数降级；新读取需要独立校准 |
| REA-AUD-P0-02 | **PARTIALLY_CLOSED** | 新世界typed读取代码存在；旧86条未按目标控制器重读 |
| REA-AUD-P0-03 | **CODE_PATH_CLOSED / RUNTIME_UNVERIFIED** | safe读取+None与静态兜底移除，但缺真实/模拟内存失败注入 |
| REA-AUD-P0-04 | **OPEN** | 48 LIVE通过旧数值合法域自动晋级 |
| REA-AUD-P0-05 | **PARTIALLY_CLOSED** | 标注未证因果，但文字仍过强 |
| REA-AUD-P1-06 | **OPEN** | 新修复为批量改写，不是逐字段实机单步；ledger重复追加 |
| REA-AUD-P1-07 | **PARTIALLY_CLOSED** | 汇总计数协调，但批次/版本身份仍不完整 |
| REA-AUD-P1-08 | **CLOSED_FOR_LABELING** | 51个未知槽位恢复正确UNKNOWN表达 |
| REA-AUD-P1-09 | **OPEN** | PE哈希及会话身份是固定字段，不是本次采集证明 |
| REA-AUD-P1-10 | **PARTIALLY_CLOSED** | 静态Collision表已建立，真实地址身份尚未知 |
| REA-AUD-P2-11 | **PARTIALLY_CLOSED** | 增加6个测试，但其中一个污染正式证据且端到端负例不足 |
| REA-AUD-P2-12 | **OPEN** | raw_legacy_capture现在已不保留原始时间/位模式 |

以上为按每条原Finding分别裁定，机读文件中保存完整独立证据与关闭标准。不能因目录/函数/测试名含`remediation`就自动判断旧Finding已关闭。

## 6. 优先返工与真实修复门

建议Gemini继续**同一REA任务的一轮集中修复**，不要为了测试通过再重复覆盖204个字段。一次修复应优先解决：
1. 将`remediate_all_field_records`转化为**纯转换函数**，输入原始不可变快照与catalog，输出独立派生文件，不直接写入证据档案；如需发布，由专门经确认命令在不影响历史的条件下原子提交。
2. 将新增测试迁入`tmp_path`并伪造`GameMemory`和`Scanner`，保证任何pytest不连接NBA2K22，也不改真实Run。以相同源数据重跑两次验证字节级幂等。
3. **从Git固定父提交恢复历史位模式与UTC捕获时间**，作为受版本锁定的不可变RawCapture archive；不删除当前修正解释文档，而是通过`derived_from_capture_sha`绑定两者。
4. 降级48项尚无完整身份凭据的LIVE标记。旧实机采样可继续作为候选，不应被算法仅凭范围检查晋级。World旧错误控制器读数尽量保持UNKNOWN等待真正获准读回。
5. 保留typed/safe getters、19 Coach降级、51 UNKNOWN、机制HYPOTHESIS这些已经正确的修复；不要在没有Human具体进程授权时擅自继续实机附件/写入。
6. 建立测试收据，至少涵盖：RAW bitpattern/timestamp不变；失败与0可区分；对任何静态常量不晋级；Coach owner/enum；World slot typed read；二次修复无变化；干净工作区；一个真实Live证据升级必须绑定对应原始来源。

满足这些门后，可复核代码与证据安全性。但对204个不同字段的**引擎因果公式**仍需要后续单字段、获准、可对比的比赛试验，而不是本次源码返工自动关闭。

## 7. 审核边界

本审核只读 GitHub 固定版本，审核者独立运行临时文件Python源流程等价测试，**没有独立重跑原14项pytest**；当前容器无GitHub网络checkout，原14/14是Gemini开发者回执。未接入游戏、没有REA会话或Live原生读取，不代表能够直接否定Gemini先前的进程附加事实。任何模型/进程运行真实性均保持来源分级。

本窗口作为以前GPT审核窗口经Human先前明确允许继续审核，不是假装全新隔离Fork；审核与Gemini执行窗口不同，但平台实例ID与外部模型认证UNKNOWN。未执行PRMS Save和正式Communication。审计只在本任务专属审核分支的Run落地，绝不修改开发者分支或master。

**最终结论**：`REWORK_REQUIRED`。现候选可作为“数据降级纠错的部分修复”，不能作为“12项全部关闭、204项实机可用”的完成版本。
