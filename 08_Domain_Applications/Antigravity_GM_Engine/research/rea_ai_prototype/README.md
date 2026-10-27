# NBA2K22 REA AI机制探索原型 — Issue #9

这是已实际运行的**探索性工程原型**，不是生产执行器。Human允许从未获独立审核通过的B开始开发；此例外不把历史审核改成PASS。源码只在指定研究分支，不修改旧执行器、世界数据阶段02或master。

## 直接运行

从仓库根运行；Python标准库即可运行CLI和语义测试。Capstone仅为重新执行静态PE研究工具所需，不是demo依赖。

```text
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/cli.py demo --verify
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/cli.py knowledge show AI_COACH_DEFENSE_M1 --role COACH
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/cli.py knowledge list --role GM
python -B -X utf8 -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/tests -v
```

`demo --verify --output <new-file.json>`另存完整回执，拒绝覆盖已有文件。默认终端只输出紧凑结果。`action assess --intent <json> --backend none`只判定，不执行；`action simulate --intent <fixture-json> --backend memory-model`运行纯离线状态模型。可用样例见`examples/`。

首个实际demo已显示：

```text
知识卡：can_reason=true / can_execute=false / AI_PATH_UNVERIFIED
Native候选上下文不足 → VALIDATED_MEMORY_WRITE_FIXTURE → FIXTURE_ONLY_PASS
两个fixture模型都合格 → NATIVE_FIXTURE_MODEL → FIXTURE_ONLY_PASS
真实游戏后端未合格 → NO_SAFE_PATH → NOT_EXECUTED
副作用集合不一致 → NO_SAFE_PATH → NOT_EXECUTED
写入后缓存/邻接字段不一致 → FAILED_READBACK
Native模型部分失败 → EXECUTED_BUT_UNVERIFIED；不自动重试Memory
```

这里 **Native模型是Python接口模拟器，Memory模型是自建字典状态模拟器**；都不调用游戏、不附加进程。fixture的cache_epoch和applied_focus是明确声明的模拟合同，不是本轮发现的游戏缓存字段。`game_target=false`与`game_proof_level=NOT_PROMOTED`写入每份回执。此前4096条Frida进程写实验不是本轮原型的游戏执行资格。

## 代码怎样形成纵切

`KnowledgeStore`以角色、模式过滤中文机制卡，明确SOURCE/UNKNOWN，隐藏内部研究字段。

`Intent.parse`只接受类型化领域动作、角色、逻辑身份、业务参数与预期版本；拒绝额外address/pointer/qualified等字段。权限或资格不能通过LLM自行传布尔值取得。

`Router`将动作绑定相应知识卡，先检查角色、引擎控制声明、模式、当前fixture构建/存档/场景/对象、版本、实验权限和共同副作用合同；依次选择合格Native模型、合格Memory模型或NO_SAFE_PATH。两个后端使用同一预期业务后置条件；实际调用开始后不自动切换后端。结果核对完整fresh快照，检测额外球队修改、丢失缓存刷新及相邻位域破坏。

真实游戏后端**没有装入**；即便调用者伪造qualified或声称获权，也不能由这个离线CLI发起游戏操作。真实进程观察在单独工具脚本中，经本轮Human后续明确授权后执行；观察工具不从角色意图入口调用。

## 本轮真实研究结果

| 机制 | 进展 | 当前仍未证明 |
| --- | --- | --- |
| M1 AI球员自然徽章成长 | CatchAndShoot深入候选、CornerSpecialist轻对照；读取旧源中的导师/成长定义，新的固定EXE局部分析识别LinkMentor和SetMentors片段 | 自然升级条件、刷新周期、两个模式AI成长是否共用、实际AI调用点；比赛效果表不当成长阈值 |
| M2 AI教练防守重点 | 当前进程核对COACHDATA的位域与enum，PHI/IND存值防守14、进攻5，29个对手Gameplan双读稳定；静态lookup的35容量/880步长/FF缺失值与profile相符 | AI自动设置入口、实际引擎控制标志、比赛消费者和效果、合格Native Setter、完整Memory生效链 |
| M3 AI GM↔AI GM交易 | 分开proposal/evaluation/validator/commit；找到EVALUATE_AI_TRADES名称、交易类型与异常资产访问器片段，排除把玩家交易菜单当AI证据 | 原生AI-AI validator/commit、完整薪资/合同/选秀权/事件联动及失败原子性 |

M2实机：第1次被coach池身份guard拦截；补核心球队ID筛选后，第2次通过，2.916秒、显式9308字节，REA证据`ev_69e7ab80b3250c3161dc85a8b4f965ad6379da3d152bcd0b3da73e689afa5390`。修复后成功支持身份筛选方法；第一次没有输出问题球队，具体冲突记录身份仍未证，不将推测写成事实。

随后对GetOpponentGameplanIndex候选进行900毫秒/最多12事件的有界hook，实际0事件。仅结论`NOT_OBSERVED_IN_WINDOW`，不是没有AI调用。两次成功会话与失败会话均cleanup_error=null、游戏存活，未主动调用游戏函数或显式写业务内存。Interceptor会临时安装代码探针，不称为完全被动读。

详见[dossiers/M1_BADGE.md](dossiers/M1_BADGE.md)、[M2_COACH.md](dossiers/M2_COACH.md)、[M3_TRADE.md](dossiers/M3_TRADE.md)。事实等级按claim拆分：指南L0、类型/实例L1、局部静态分支L2；没有本轮L3 AI比赛行为或L4授权原生动作效果。

## 证据与复现

- `evidence/source_registry.json`：9个固定Git来源的commit/blob/SHA256、3个本轮实机来源；同源文件不算独立证据。
- `evidence/static_ai_seams.json`、`static_ai_followup.json`：13+9个精确词项、每项最多12命中、120个引用上限；分别约0.827和0.868秒，实际17与27个引用。有命中截断，不是全游戏函数清单。
- `evidence/candidate_function_fragments.json`：6个局部unwind片段，只有RVA和指令解释；不发布原始EXE字节或绝对内存地址。
- `evidence/live_coach/`：本轮guard拒绝、成功读取、0事件追踪及脚本、哈希、目标/清理记录；不是重复发布旧52份档案。
- `data/knowledge_cards.json`：3张角色可读部分机制卡；每张均能解释什么可知、为什么可建议、哪些不能执行。
- `data/backend_matrix.json`：Native/Memory按机制分别判断及G0–G7缺口。
- `examples/`与Run中的真实demo回执、测试日志用于复验。

重新运行离线探针（仅当该轮任务覆盖静态EXE读取）：

```text
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/tools/probe_static_ai_seams.py --out <new-evidence-dir>
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/tools/probe_static_ai_seams.py --out <same-dir> --followup
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/tools/inspect_candidate_functions.py --dir <same-dir>
```

静态和实机固定游戏SHA256：`1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。实测REA6.8.0、Node24.22.1；官方研究参考commit `morluto/rea@570abe95f2a35b5c580a5ec2fca90c33d4114bdc`已查询确认。官方参考commit与已装npm版本是不同身份，不假定全部功能一致。无需重装、无需再试大EXE Ghidra。

## 新发现与B修订

1. 共享POE字需要保留非目标位：测试既验证fixture，也真实调用现有纯`coach_codec.encode_changes`，不运行旧Writer。
2. 原生lookup返回0xFF，索引0有效：新增`decode_gameplan_index`，拒绝35..254与bool，不做盲数组读取。
3. 当前EXE含conditional coaching定义；不能由存在推断已开放，更不能从跨世代攻略宣称当前实现。
4. 原型的资格证据与执行许可分离；未知副作用后禁止自动Memory重试；fixture模拟cache不写成游戏cache。这些实现修订见Run的`B_DELTA.md`。

当前真实游戏的Native和Memory业务动作都为`NO_SAFE_PATH`。这不会删除机制知识的研究价值，也不会覆盖原先获批的外部GM交易/签约/选秀架构。下一轮实验在Run的准入单列出，当前不会直接调用未知交易或教练业务函数。
