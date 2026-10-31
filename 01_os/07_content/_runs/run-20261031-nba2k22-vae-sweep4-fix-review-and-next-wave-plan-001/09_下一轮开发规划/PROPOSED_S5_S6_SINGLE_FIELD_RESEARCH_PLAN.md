# NBA2K22 VAE REA · 下一轮持续开发目标（审查建议，待规划/Human采纳）

**基线候选**：`f953f622c833a40a714a6ff6055af170b2070a7e`；**任务不变**：`NBA2K22-VAE-REA-SINGLE-FIELD-LOOP-20261030-001`。该文档为审查者提出的**下一波开发目标建议**，**不是变更正式Human批准的Task Packet或授权范围**。

## 0. 目标与长期终局

用户明确：这是一项长周期、循环改进、**一次一个字段**的原生机制和数值影响研究，不是每个审查轮次必须一次性证明全部204项。沿用已经批准的 `SINGLE_FIELD_LOOP_CONTRACT_V1.json`，保持队列和字段ID、REA01–REA08、增量checkpoint、失败/未知可恢复、无固定总轮数。阶段成果可为`PARTIALLY_SUPPORTED`；“204条字段都有内存值”仅是取数/种子覆盖，**不等于**204条原生消费者完整实证，也不等于204条数值效应定量已完成。

长期产物应支持：
1. **可证实原生字段身份**：UI/Native Getter/字段宽度和内存位置、游戏build+Save+模式、有效值域。
2. **可证实消费者机制**：字段被哪些游戏函数读取、何时读、其结果进入哪些分支、3D与Calendar差异。
3. **可测量数值影响**：一项数值改变对AI动作、频率、分布、战术决策、体能或模拟结果的方向、大小、饱和阈值、随机性和交互项；真实试验始终依赖独立授权。
4. **可供GM/教练角色安全使用的信息契约**：有效性/来源/不确定性/适用模式/作用链/冲突和调参建议，未确认模型只作实验观察，不可宣称硬性游戏规则。

## 1. 下一开发波次 S5：有界修复门 + 两个真正的单字段试验

### S5-0 · 先修复研究仪器的可信性（可离线，不阻塞其他纯静态研究）

**目标**：创建能以真实文件字节而非文案作准的、可重复复盘的证据采集/解码层，并保障历史不覆写。

- 将`consumer_tracer.py`拆成`read_code_bytes → decode_instruction_list → verify_cfg_and_rel32 → semantic_hypothesis`四层；“代码里预写的汇编字符串”只能作**待检模板**。在只读离线fixture内独立检查精确起始RVA、length、每条指令地址、relative-call目标、源码hash、完整字节对比，错误必须失败关闭。
- 修正保存的Tempo偏移：给定byte模板由`0x14120ba72`开始，`mov eax,70`实际位于`0x14120ba83`，`cmovg`位于`0x14120ba98`；`verify_live_bytes()`不应在cmovg位置要求mov-eax。两条已发现的CALL目标亦需按rel32重算后核查源代码真实区段，而不能通过修改文字掩盖矛盾。
- 从`f1e02101`冻结第一次采集原始JSON/时间/uint32位模式为**独立不可变capture批次**；以后独立保存每次真实观察，`derived_value`/修正理由只追加。未实际记录的时间标`UNKNOWN`，绝不能统一回填虚构的`03:00:00Z`。
- 测试构造函数与夹具统一`auto_attach=False`，从纯离线调用到GameMemory附加动作前必须显式授予权限；所有测试和分析默认输入/输出均指向临时副本或纯函数，禁止隐式覆盖官方204条证据。
- **验收**：静态指令解码负例错位必须红；所有需要精确RVA的检验必须依原始字节通过；历史source hash和UTC timestamp可追溯；重复离线重算不改变真实Run；未授权测试不访问游戏。

### S5-1 · 单字段：`TENDENCY_NATIVE_001 / ShotTendency`

**研究问题**：“读取`ShotTendency`后，哪些战术角色路径会改变[AI Controller+0x2dd]，所谓Role Ceiling表中的数值到底是什么？”

- 精确汇编：`0x1226942`附近**所有可到达基本块**，特别是`jne 0x1412269cf`路径、`rcx`从`[rsp+0x20]`和`[rsp+0x24]`的不同身份、`rsi`所指内存主体/表、`0x2dd`消费者。
- 原始字节/地址校验；对核心和非核心路径分别构建条件控制流图；验证role类别不等同仅一个整数`role_tier`，识别来源后再决定bridge参数契约。
- 先只读追踪。观察的两个字段（Shot和Touches）可同时作为**受控背景量**，但本次迭代只回答Shot的一个主问题，Touches另立下次迭代，不做双变量干预。
- **可关闭结果**：一条真实代码路径与来源证明；或`UNKNOWN/BLOCKED`并记录下一可行证据，推进队列。不能因为发现一个CMP就自认游戏回合效果。

### S5-2 · 单字段：`COACH_DEFAULT_014 / Tempo`

**研究问题**：“`xmm0`的来源到底是不是Coach Tempo UI原值？内部[10,70]钳位作用的是哪一个修正量？”

- 用当前保存原始指令独立计算有符号乘积/high32/算术右移/rounding，特别验证输入`0/10/40/50/60/70/80/100`。**若xmm0为原Tempo**，代码片段对输入80推导的内部修正量是46（不是bridge直接剪裁到70）。
- 向上追`xmm0`赋值与游戏模式/设置来源，向下追`sub eax,ecx`结果的消费者；区分`raw_slider`、`effective_modifier`、`pace_possessions`和`3D/Calendar`效果。
- 保留experimental模型作`what-if`演示；不得以`Tempo>=70 => 比赛回合数完全不增加`发布正式游戏事实，除非有实际数据证明。
- **可关闭结果**：完整指令链+输入输出单位+边界记录，或诚实`UNKNOWN`且列下一证据。

## 2. S6+ · 循环研究机制作用和交互：一次一字段，而不是一次204项扫表

优先级由“GM/教练决策依赖 × 证据薄弱 × 容易只读验证”决定，推荐的初始下一轮候选：
- `TENDENCY_NATIVE_066 / Touches`：区分原始Getter、触球角色和分配时序，不预设与SHOT双向强耦合。
- `TENDENCY_NATIVE_016 / ShotAreaCloseLeftTendency`：验证PE字符串与Getter、snapshot和真实热区消费者的独立路径。
- `WORLD_REG_008 / normalize_stats`、`WORLD_REG_085 / game_difficulty_preset`：验证三控制器槽位的真实UI读回与模式，声明性range检查不等于行为效应。
- `COACH_DEFAULT_011 / RunPlayTendency`、`COACH_DEFAULT_010 / BenchDepth` 等：从相关GM动作所需字段及消费者逐项深挖，再扩展其他领域。

每一`one_iteration`固定7步：读取精确源/ledger → 固定一个`field_id`和**可证伪问题** → 检查当前证据与冲突 → 只执行已有权限的静态/只读追踪（游戏附加权限需另外核对） → 独立解码/反例 → append证据与状态 → 指向下一单字段/下一改善方向。

### 若将来Human另行批准受控数值干预

一次仅调整一个数值和一个目标值，保持游戏build、Save副本、mode、对手、阵容、角色、其它sliders及RNG/随机源条件尽可能一致；独立记录前后读回、动作/模拟输出、重复样本、负对照和可恢复性。分别报告3D与Calendar，不擅自把一种模式的定量关系移植到另一模式。因果结论必须有实验支撑，不能由汇编读路径直接越级。

## 3. 证据分层与每轮退出条件

建议字段研究采用彼此**独立**的维度：
- `identity_evidence`：UNKNOWN → ADDRESS_CANDIDATE → NATIVE_GETTER_OR_CODEC_VERIFIED → UI/SAVE_CORROBORATED。
- `consumer_evidence`：NONE → RAW_BYTES_CAPTURED → RELOCATIONS_AND_CFG_VERIFIED → DATAFLOW_AND_MODE_CONSUMER_VERIFIED。
- `effect_evidence`：UNMEASURED → TESTABLE_HYPOTHESIS → CONTROLLED_OBSERVATION → REPRODUCED_AND_SCOPED_EFFECT。
- `permission`：STATIC_ONLY / AUTHORIZED_READ_ONLY / ACTION_SPECIFIC_TRIAL_GRANTED，按真实来源，不由Model推断。

**单轮停止**：一个字段主问题已有可信来源+失败负例→输出记录/暂停；或同方法重复失败不超过合同规定1次→UNKNOWN/BLOCKED并前进；遇到越权、范围变化、未授权实机行为、历史改写风险即暂停该操作请求Human裁决。

**整波停止**：S5-0仪器门通过、S5-1/S5-2各给可审计事实/UNKNOWN；将下一批3–5候选列入backlog，得到允许继续的`PARTIALLY_SUPPORTED / NEXT_SWEEP_READY`。没有要求这一波把204项都测到效果；若后续完整改善波次没有新增证据且无可行合法办法，按旧合同`PARTIAL`停止该波，保留长期任务上下文与人工续跑能力。

## 4. 交付和职责

**Gemini execution**在原Run和src/tests白名单中实现 S5-0与单字段研究；**GPT外部资料流**负责真实社区/游戏资料，不得为Native证据晋级；**GPT独立审核**仅审核冻结候选和证据边界；**Human**批准涉及游戏进程、存档、数值更改或重大契约变化的操作。

建议交付：`raw_code_fragments.jsonl`（静态/只读来源、精确RVA+raw bytes hash）、`cfg_dataflow/field_id`、`controlled_trials/field_id`（只在授权时）、`field_records`派生视图、逐字段ledger、checkpoint、`next_field_priority.json`、`completion_pointer.md`。不合并master，未经批准不修改正式Loop契约。

**规划状态**：`PROPOSED_FOR_PLANNER_AND_HUMAN_APPROVAL`。具体后续受控实验需另行授权；本计划并不授权游戏写入或自动后台循环。
