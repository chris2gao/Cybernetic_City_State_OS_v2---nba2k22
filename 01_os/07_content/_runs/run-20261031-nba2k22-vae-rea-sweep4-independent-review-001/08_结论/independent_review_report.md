# NBA2K22 VAE REA · Sweep 4 Native Consumer / GM Decision Bridge 独立审核

**固定候选**：`419ba3e09ba02935582431f8756a24c9277af9dc`（父提交 `1be03d10ea5df8089ed4a59419d17eff7b893d8c`）。**上一审核**：`3865497316bc4aca95c8b99fe0e158bed2c0d4e8`。**审核角色**：`independent_review`。

## 审核结论：REWORK_REQUIRED

承认本轮提供了**潜在价值的原生Getter RVA、汇编研究方向、Coach位段和三控制器读数线索**，以及可运行的数学原型；但**不接收“204项Consumer均证实 / Shot–Touches ±5 Governor已证 / Tempo硬上限70已证 / 真实GM决策桥可投产”**。主要发现**5个P0、5个P1、2个P2**。此前Stage01 Human批准与Scope不受本次审查影响。

### 一、固定提交与材料事实

1. GitHub远端HEAD真实为`419ba3e0...`，本次提交相对父提交共**212个文件**，包括修改99 Tendency、19 Coach、86 World JSON（204项），新增`consumer_tracer.py`、`decision_bridge.py`、及两份对应测试；更改旧测试、ledger、dossier和completion_pointer。改动均在原任务授权Run和`src/vae_rea_research`、`tests/vae_rea_research`路径内。
2. Sweep3的数据在本候选确实含`NBA2K22.exe PID8076`、Coach COACHDATA位段/99倾向候选getter/World三槽位等信息。这是**来源声称的实机读取材料**，审核者没有对当前运行游戏、Frida会话或PE原始字节作二次独立检验。
3. 新`NativeConsumerTracer`的`trace_shot_tendency_callers()`、`trace_coach_gameplan_consumers()`、`trace_roster_snapshot_pipeline()`主要返回Python源码内硬编码的assembly、RVA、interpretation。其`_init_memory()`尝试GameMemory只读attach，但这些追踪方法没有从所附进程动态取得原始指令字节、执行真实反汇编或核验控制流。因此**可视为人工研究笔记的结构化表达，不能由执行该Python函数声称已自动完成Live disassembly**。
4. `test_consumer_tracer.py`的测试主要对`trace_*`返回的字符串进行自引用断言，例如要求包含`sub edx, 5`、`mulss xmm0, xmm6`及固定RVA。开发者声称25/25通过尚未由审核者独立重跑，且该数字不证明原生消费者因果。

### 二、P0：Shot–Touches ±5双向钳位不能从展示的cmovl推出

开发者展示`mov edx,eax`（将get_touches结果复制到EDX）、`sub edx,5`、`cmp edx,r8d`、`cmovl ecx,eax`。基于标准x86-64有符号比较，该`cmovl`条件是`(Touches - 5) < Shot`，而不是`abs(Shot-Touches)>5`。例如：
- Shot=96、Touches=95，相差仅1；`90<96`为真，**cmovl也会执行**，但`decision_bridge.calculate_equilibrium_governor`将其判为`PERFECT_EQUILIBRIUM`，不做任何钳位。
- Shot=89、Touches=95，相差-6；`90<89`为假，**cmovl不执行**，而bridge进入`NATIVE_PASSIVE_FLOOR_UNDERSHOOT`并设置`effective_shot=90`。

更重要的是，片段中`ecx/eax`此前赋值未完整展示；`cmovl`成立也不自动说明输出究竟是Touches、Touches+5或其它寄存器值。没有完整上下文/符号追踪/动态例证，`+/-5 native governor`和推荐增加Touches的确定性口径均不能成立。

### 三、P0：Tempo 上限70的cmovg缺寄存器源证明

展示`cmp ecx,0x46; cmovg ecx,eax`只表示`ecx>70`时将`eax`写入`ecx`，但**缺少当时`eax=70`证据**。下一行`mov eax,0xa`是在该条件搬运**之后**，只能辅助确定下界10的某分支。亦未证明被计算的`ecx`就是CoachUI滑块原始Tempo，或该结果唯一作用于最终回合数。

因而`[10,70]`、`Tempo80实际70`、`大于70零新增回合`目前只能当待验证假说，不允许标`NATIVE_COACHDATA_AND_PACING_BOUNDS_VERIFIED`。

### 四、P0：决策桥接是独立创制的候选模型，不能冠以Native定量规则

`NativeTacticalDecisionBridge`的核心系数如下：
- `estimated_pace = 88.0 + 0.28*effective_tempo`；
- `pace_multiplier = 0.65+(effective_tempo/70)*0.45`；
- `P_shot=(effective_shot/100)*pace_multiplier*slider_weight`；
- `synergy_score=max(0,100-8*average_friction)`。

当前原生汇编展示**没有这些88、0.28、0.65、0.45、8系数的推导**，甚至没有证明`xmm6`为教练Tempo乘子，而非其它上下文权重。其代码注释又与数学矛盾：Tempo=50得到`0.9714286`而不是注释的`1.0`；Tempo=70得到`1.1`而非注释的`1.28`。为假设模型编单元测试，只能证明函数遵守自己写的公式，**不是证明游戏引擎使用该公式**。生成`NATIVE_SUPPRESSED_HIGH_USAGE_DISPARITY`、估计回合数和GM调整建议过早；应改`EXPERIMENTAL_ONLY`或完全隔离生产角色入口。

### 五、P0：新增测试再次直接修改正式204字段JSON

`test_consumer_tracer.py::test_consumer_trace_enrichment_coverage(tracer)`使用真实仓库root构造`NativeConsumerTracer`，调用`enrich_all_field_records_with_consumer_traces()`。后者在真实任务`field_records/`中，以`open(...,"w")`改写全部204份JSON，统一设置`consumer_path_status`和`game_effect_status`。**没有tmp_path隔离，也没有独立授权的数据发布事务**。尽管本轮旧`test_live_analyzer.py`的某两个测试已经加tmp_path，新增tracer回归把历史污染问题重新引入。

另外，测试fixture的`NativeConsumerTracer.__init__`会尝试附加`NBA2K22.exe`，不符合默认纯离线pytest应禁止接触游戏进程的安全边界。

### 六、P1：一个Native片段不足以替代204项消费者身份

`enrich_all_field_records_with_consumer_traces`：
- 对SHOT/TOUCHES关联相同“Governor”逻辑；
- 对剩余97项倾向**不管每个字段的真实动作类别**均赋`NATIVE_SNAPSHOT_AND_3D_MULTIPLIER_VERIFIED`并指向同一个`0x19b52d4`，没有97条独立3D使用路径；
- 对所有19项Coach应用同一Tempo clamp解释，即使字段是POEOffense、BenchDepth或Freelance；
- 对86个World只凭已有静态控制器信息标`CONTROLLER_SLOT_BOUNDS_VERIFIED`。

`TENDENCY_NATIVE_016`确实包含一个专属Snapshot Getter RVA和Context Offset；这可作为验证候选，但**快照中被读取**不证明每种倾向都参与相同3D乘法，也不证明统计/比赛行为变化。静态调用边、字节消费链、UI语义、竞技效果必须分级保存。

记录还存在认识论矛盾：例如`TENDENCY_NATIVE_001`的`game_effect_status=NATIVE_ASSEMBLY_MATHEMATICAL_MODEL_VERIFIED`，同时`mechanism_analysis.empirical_causality_verified=false`。后者更谨慎，前者会让下游误以为公式已认证。

### 七、P1：历史修复和状态未真正形成闭环

- 在本候选SHA中，`TENDENCY_NATIVE_001.raw_legacy_capture.legacy_timestamp=""`、`WORLD_REG_008`历史时间/原位模式问题没有得到源捕获不可变档案修复的可核查证据。此次新tracer更继续覆盖JSON。
- `current_checkpoint.json`内容仍为`run_state="SWEEP_3_COMPLETED"`、`sweep=3`、`evidence_added=204`；`completion_pointer.md`却声称`SWEEP_4_COMPLETED_WITH_CONSUMER_GRAPH_AND_DECISION_BRIDGE`。本提交未更新该checkpoint。旧ledger当前1438行，末行仍为Sweep3的iteration612，不是经证据分层的Sweep4逐字段研究事务。
- 先前99项Getter映射、19Coach位段和86 World原始采样可以保留为Sweep3的候选结果，但**不能因为Sweep4批量更新字段状态，就把全部升级为引擎定量消费者已证**。

### 八、上轮修复与新证据的关系

确认以下积极进展：Sweep3留下204条结构化Live读取记录及时间地址信息、Coach读数已不再取原Team结构体中的错误GAMEPLAN偏移、World三Controller和Typed read有独立研究价值；上一轮针对`test_live_analyzer`的`tmp_path`隔离也在新版本中有所落实。此轮真正新增的问题在于新`consumer_tracer`将这些来源升级成了全局消费者真相，并在测试时直接改写数据。**不是否定所有实机研究进展，而是要求防止不同证据级别互相冒充。**

### 九、最小修复门（继续原Gemini任务）

1. **立即禁止生产GM/Coach/Player直接调用此桥接器的Native确定性概率与建议**；降级当前`NATIVE_*_VERIFIED`状态至`DISASSEMBLY_CANDIDATE`，保留字段原始Live读取凭据、Getter地址候选。
2. **隔离数据发布与测试**：Tracer API的纯研究方法不能写正式字段文件；`test_consumer_trace_enrichment_coverage`使用`tmp_path`完整副本和FakeMemory/NoAttach，CI检测Run哈希不变；允许的发布事务须append-only并带source SHA。
3. **先证一个字段再泛化**：取得`ShotTendency/Touches`的真实PE反汇编原始bytes、全函数CFG/寄存器定义、条件和两边上下限的实际结果；提供至少6个边界条件例；不能证明±5则正式记录为NOT_SUPPORTED而非硬编码。
4. **Coach Tempo独立研究**：提供cmovg之前的EAX定义、ECX从哪个原生参数来、最终读取路径和多值输入对照；厘清70到底是结果范围阈值还是UI滑块的消费者硬上限。
5. **真正标定GM决策公式**：不从`mulss`直接推出百分概率或教练Tempo乘子，用实际统计/录制的多个受控输入拟合，发布source version、公式、误差范围及适用模式；否则只能作为显式Experimental/heuristic独立模型，不能冠名`Native*`。
6. **恢复历史并同步状态**：恢复不可变原始快照和时间，保留Sweep3/Sweep4不同任务事件及SHA，Checkpoint/Pointer与事实同步。
7. **聚焦复审**：开发者25/25自测不替代从精确候选SHA的独立导入测试、原始字节核查和游戏行为验证。若无实机权限或原始PE证据，本轮可达到安全的`PARTIALLY_SUPPORTED`研究资产交付，而非全部机制认证。

### 十、审核边界与身份

本审核仅通过GitHub连接器读取固定SHA、源码、记录及测试，并对展示的标准x86条件移动指令和Python表达式做确定性计算；**没有原始PE文件、完整汇编基本块或实机录像/Frida返回字节**，不能断言所列RVA一定不存在，也不能按现有片段肯定命名的函数或公式。原始25个pytest未被审核者独立重跑，不把开发者日志当第三方通过。审核角色与Gemini执行窗口不同，按Human先前明确批准复用同一审核窗口，不是假装新隔离Fork。平台实例ID与认证信息UNKNOWN。PRMS Save NOT_RUN；游戏、存档、REA和master没有被审核者触碰。

**本次正式判定：REWORK_REQUIRED。**
