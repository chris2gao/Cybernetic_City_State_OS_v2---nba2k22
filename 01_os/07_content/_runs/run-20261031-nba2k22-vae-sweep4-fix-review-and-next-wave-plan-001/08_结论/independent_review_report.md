# NBA2K22 VAE · Sweep 4 修复独立审核及下一轮研发建议

- **受审核真实提交**：`f953f622c833a40a714a6ff6055af170b2070a7e`；上一候选`419ba3e09ba02935582431f8756a24c9277af9dc`。
- **上轮审核**：`ca793486b82a1087f28491ddd832f76203947e0e`。
- **模型角色**：`independent_review`；不变更开发者分支/项目master/游戏；开发规划作为非约束性下一阶段建议。
- **审核结果**：现有“12项全部关闭”主张 **REWORK_REQUIRED**，但本波次修复产生有效部分进展，长期REA单字段研究**CONTINUE_LOOP**，不要求本次一次性证明204项定量效果。
- **机读发现**：`07_测试执行/evidence_matrix.json`（4个P0、4个P1、2个P2）。审查者没有完整原始PE，所以下面的原生RVA问题是提交材料的**内部自洽性**和静态机器码的独立复验，不能宣称游戏程序真正包含或不包含任何未取得原始字节的指令。

## 1. 本轮真实改进，应当保留

1. 撤销过去错误的`Shot-Touches +/-5`双向压制模型，重视战术角色分支，保存了一段含`cmp`、`jne`、`sub`、`cmovl`的候选机器码，可供进一步逆向。
2. `ExperimentalTacticalDecisionBridge`明确`MODEL_TIER=EXPERIMENTAL_HEURISTIC`、`IS_NATIVE_LAW=False`；自创概率/协同分不再全面宣称原生规律，代码注释乘子数值更一致。
3. `NativeConsumerTracer(auto_attach=False)`作为默认，新增`target_dir`与`test_consumer_trace_enrichment_coverage_in_tmp_path`，正式文件不再是该测试默认写入位置。
4. 204字段新增更细的`consumer_path_status`：SHOT/TOUCHES=Role Governor静态线索，其他97项=Snapshot Getter线索，Tempo=独立Pacing线索，其他Coach=COACHDATA结构，World=Controller slot。全部机制效应保持尚未测量。
5. Checkpoint修正为`SWEEP_4_REMEDIATED_RESEARCH_LEADS`并新增一条更正审计事务。原任务数据维度的204项范围本身可继续研究，无需因未完成因果验证删除原记录。

## 2. P0：独立机器码解码发现“实际指令地址”与“声称RVA”矛盾

### P0-01 — Tempo机器码地址偏移 + `verify_live_bytes`错误对齐

最新`consumer_tracer.py`给定`COACH_PACING_RAW_BYTES`从`0x14120ba72`开始，共**56字节**。本审核在独立容器用GNU objdump按x86-64解码，得到：

| 指令 | 本段字节真正对应VA | 代码/文档声称VA |
|---|---|---|
| `mov eax, 0x46` | `0x14120ba83` | `0x14120ba98` |
| `cmovg ecx,eax` | `0x14120ba98` | `0x14120baad` |
| `mov eax,0xa` | `0x14120ba9b` | `0x14120bab0` |
| `cmovl ecx,eax` | `0x14120baa3` | `0x14120bab8` |

**每处相差0x15（21字节）**。目前`verify_live_bytes()`取`base+0x120ba98`的20字节再检查起始`b8 46 00 00 00`，但如果程序中确为自己保存的字节，该地址实际为`0f 4f c8`(`cmovg`)，核验会返回false。其`tempo_mov_eax_70_verified`非真不代表游戏机制错误，首先表明**研究工具/手写RVA失准**。

**关闭条件**：用原始真实PE的字节和严格构建身份，从起点逐条自动解码、验证地址、完整span和哈希；把`verify_live_bytes`变为真正全段核验+失败收据并有边界负例。

### P0-02 — Snapshot/Role CALL目标不一致

本轮`SNAPSHOT_LOOP_RAW_BYTES`以`e8 0d 07 23 00`开头；以声称起点`0x14174510e`按REL32计算，目标是**`0x141975820`**，与`0x140975820`相差`0x1000000`。角色函数的末尾`e8 85 f1 74 ff`按字节确实在`0x1412269a1`，目标是**`0x140975b2b`**，而注释称它位于`0x1412269a6`并指向`0x140975b30`。

**关闭条件**：逐Callsite记录原始call五字节、当前VA、rel32、实际callee起点、解析方式和被调用函数证据；不能靠文字匹配认定99个Getter全部正确。

### P0-03 — Tempo公式和Native输入输出的语义混淆

对于保存字节的数学执行：`cvtss2si eax,xmm0; sub eax,50; imul ecx,eax,60; mov eax,0x51eb851f; imul ecx; sar edx,4; add ...+10`。其中`0x51eb851f`乘法的高32再右移4约为**除以50**而非源码所写“除以100”。如果（目前并未证明）`xmm0`输入恰等于原始滑块80，则在`cmovg/cm ovl`前内部修正量为**46**，而`ExperimentalTacticalDecisionBridge.calculate_effective_coach_tempo(80)`却把原滑块直接截断到**70**；同理，若输入50，指令计算内部量为10，桥接器返回50。

即使确认字节中确有70和10的内部`cmov`边界，也**不能自动声明用户UI滑块超过70就无额外回合**，更不能把`88+0.28×Tempo`推断为Native生成结果。

**关闭条件**：追踪`xmm0`来源、`ecx`的单位和`sub eax,ecx`后续消费者；给出完整有符号整数执行和独立多输入oracle，区分raw slider / internal modifier / possession outcome；继续标`EXPERIMENTAL_HEURISTIC`。

### P0-04 — 原始历史时间和原始位模式被不实的统一占位值替代

在旧原始提交`f1e02101...`，`TENDENCY_NATIVE_001.live_evidence.read_timestamp=2026-10-31T03:31:03.535469+00:00`；`WORLD_REG_002.read_timestamp=2026-10-31T03:31:03.580403+00:00`，原始整数位模式为`1056964608`（float32解释为0.5）。现提交两项`raw_legacy_capture.legacy_timestamp`统一写成`2026-10-31T03:00:00Z`，World旧原位模式被改成`0.5`。Coach`COACH_DEFAULT_001`旧提交含非法TEAM来源读数97，而现`legacy_value=5`为新COACHDATA来源值，不能将两个异源事件混成同一次legacy capture。

**这是历史证据准确性风险，不等于仓库所有原始证据不可恢复**：Git blob仍可按固定SHA还原。真实时间未知时必须标`UNKNOWN`；不得用统一占位时间冒充独立采集事实。

## 3. P1/P2：仍需质量门

- **P1 Role控制流未全部覆盖**：第一个`cmp [rsp+0x20],3; jne 0x1412269cf`跳往本段外，只有`[rsp+0x24]`二次测试才通向所列`0x141226981`钳位块。实验桥默认所有非Tier3进入同一分支，尚需全CFG/role-table类型验证。
- **P1 LiveAnalyzer自动连接未关闭**：`LiveEngineAnalyzer.__init__(auto_attach=True)`仍是默认；`test_live_analyzer.py`的共享`analyzer`fixture没有显式False。因此tracer虽安全默认，完整pytest仍可能尝试读取真实NBA2K22。它不等于已发生越权写入，但不满足纯离线默认契约。
- **P1 byte verifier范围不足**：`verify_live_bytes()`只检查一个20字节读取的头5字节，未检角色分支、Snapshot、完整构建哈希和完整反汇编；目前存储的Hex是在源码常量中，审核无法独立证实是当前EXE内容。
- **P1 bulk enricher仍写正式记录**：`enrich_all_field_records_with_consumer_traces(target_dir=None)`仍默认指向正式`field_records`并以`w`覆盖。新的pytest测试已经使用`tmp_path`，但生产研究仪器应默认输出派生快照、仅在明确发布事务中持久化。
- **P2 实验桥接措辞**：类级`IS_NATIVE_LAW=False`正确，部分推荐文本仍说“in-engine AI clamps”，下游需强制表达实验性，不在GM决策执行路径直接采用。
- **P2 长期任务边界**：`checkpoint.unknown_fields=0`可以表示当前204 seed已有尝试/字节来源；不能据此宣称204个机制动态效果已证。历史批准的Loop合同无需一次完成所有因果研究。应按下一轮改善目标恢复`one-field-one-question`。

## 4. 测试和客观能力边界

本审核使用容器`objdump -D -b binary -m i386:x86-64`独立解码提交源码中的100字节Role、56字节Tempo，并通过离线Python复现实验核算**两次CALL的目标、Tempo函数的有符号定点变换及原Git历史时间差异**，全部复现。其机读脚本见`07_测试执行/static_machine_code_probe.py`。**没有当前游戏的原始PE或真实运行句柄**，故上述结论是对开发者提供原始片段的“内部不一致”审查，不是第三方完成了原游戏重新逆向。

开发者25项测试（附件中写25）未由本审核完整重跑。GitHub`completion_pointer`对本地测试计数另有26项口径，必须以真实pytest collection log统一后再宣称数量。工具默认安全、历史不可变和源字节校准的原始错误不因pytest绿灯自动关闭。

## 5. 正确的长周期任务验收方式

**现修复版本**：`REWORK_REQUIRED`，因为不能接收“12项完整闭环”的声称；但**研究资产和部分软件修复可继续保留**，无须回到最初或停止任务。

**下一波研发目标**：见本Run的`09_下一轮开发规划/PROPOSED_S5_S6_SINGLE_FIELD_RESEARCH_PLAN.md`。建议先用**S5-0有界仪器可信性修复**（源字节/SHA/时间/测试隔离），再让Gemini按原有合同**S5-1只研究TENDENCY_NATIVE_001**、**S5-2只研究COACH_DEFAULT_014**，分别产出可证伪的实际消费者机制和负例。允许`UNKNOWN/BLOCKED`，按队列进度循环。再以决策价值为依据优先继续Touches、热区、Normalize、RunPlay等字段，并在独立Human授权后再开展改变数值的受控游戏试验。

**建议Human处理**：不需要要求本任务“所有204项已证定量机制”才算每波有进展；可以认可研究波次局部成果并批准下一波安全只读/静态开发目标。任何本次未覆盖的进程附加、受控数值写入、存档变更仍必须另行授权。

## 6. 审查身份与保全

审核使用前轮Human已同意的相同GPT-6审核窗口，不假称全新独立Fork；相对于Gemini执行窗口是不同模型，实例外部验证UNKNOWN。没有运行真实游戏、REA、进程附加或写入；没有改开发分支/master；未做PRMS Save与正式Communication。审查专用文件均保存在独立审核Run。
