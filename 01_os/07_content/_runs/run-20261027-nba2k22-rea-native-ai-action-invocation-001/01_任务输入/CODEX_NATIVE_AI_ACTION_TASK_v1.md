# Codex 开发任务｜REA 调用 NBA2K22 原生 AI 行为：输入值→原生函数→真实游戏状态

**任务 ID**：`NBA2K22-REA-NATIVE-AI-ACTION-01`  
**任务性质**：`EXPLORATORY_NATIVE_ACTION_ENGINEERING`（探索性**真实操作入口**研究与受控PoC，不是第二轮纯机制解释文档工程）  
**主工程 Owner**：用户指定的**本地 Codex 客户端窗口**，本Issue仅为可复核任务交接，不会自动启动任意Codex窗口。  
**代码分支**：`task/nba2k22-rea-native-ai-action-invocation-20261027`，从上一轮 `PR #10` 冻结发布头 `cfce2c88bcaf38362ff7270242cd982bd9757415` 派生。上一轮 [PR #10](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/10) 仍为草稿PR，不代表master已合并或Code已上线。

## 0. 本次 Human 的**最新产品裁决**，优先于上一轮研究取舍

> 通过 REA 逆向真正供游戏 AI 操作游戏的函数与机制，**外部输入目标值/操作参数，调用游戏内部原生函数，让原游戏完成战术调整、攻防策略、球员属性变化、交易、签约、选秀等行为**。这些动作一旦被打通，再研究它们对比赛与长期游戏的深刻影响。当前不是优先解释“为什么选择保护禁区会影响防守”，而是先使游戏接受“把防守重点设为保护禁区”的原生操作。

**必须改变上一轮研究优先级**：
- `Action Invocability（可实际调用）`、`Native mutation entrypoint（原生操作入口）`、`Parameter ABI（参数合同）`、`Actual game state change（游戏状态修改）`是主线；消费函数的赛场策略意义研究**明确后置**。
- 不再满足于只读取POE值、取得AI消费者候选、输出机制知识卡或让Python Fixture PASS：这些是研究起点，不是本任务主要成功标准。
- 一个真实、有限、可恢复的原生游戏操作PoC及其来源/资格/结果，比大量表格、无界知识图谱和重复Fixture测试更重要。
- Human希望未来**原版AI能够操作的行为尽量都可由外挂 AI 下达参数后通过原生机制执行**；本轮先构建真实可用性能力目录、实现最有价值的代表操作，随后逐类扩展，不以单次工作必须破解所有行为制造虚假完成。

### 关键架构纠偏：外部AI替代“决策”，尽量复用原版“动作执行”

```text
GM/Coach/Player 外挂AI决定WHAT / TARGET / VALUE
                 ↓
          Typed Native Action Request
                 ↓
   识别有效的原版AI执行入口（若可用）或AI也复用的底层业务操作核心
                 ↓
   NBA2K22 Native Game Function / Engine Service（REA协助定位/调用）
                 ↓
  游戏原生状态/名单/合同/设置/进度改变 → fresh readback对账
```

这里不是要求Codex让 NBA2K22 自己的AI决定“保护禁区”，而是**外挂AI决定13等目标值，调用原生操作入口设置到游戏里**。因此不要把“AI策略决策caller”错误地提升为**所有共享底层业务Setter调用的绝对前提**：

- 优先找到`AI自动行为调用路径`，其次找到AI与Human菜单可能**共享的原生底层业务函数/服务**；只研究共享的业务变更核心，不做Human专属UI弹窗、输入/编辑、MyCAREER玩家成长流程。共享底层函数只要游戏构建、对象上下文和真实效果证据足以支持外部调用，可标为候选；必须在报告中明示`AI调用链是否已证`，**不能谎称它是原版AI的独有函数**。
- **游戏内部Human控制标志≠外挂决策者是AI**；不能为了调用共享内核强行改游戏控制权，也不要以未知/某队Human标志机械阻断所有Native服务入口的研究。只有实际函数业务前提依赖这个标志时才当硬条件。
- `PLAYER`游戏实体不等于`HumanController`。更改属性可能属于原生编辑Setter或成长/训练引擎服务，不一定存在“AI可直接设任意属性数值”的入口；如只有Human编辑UI路径，**不要模仿UI或包装成AI AI函数**，但可研究UI和AI都复用的底层状态服务。
- **已证业务操作**不一定要先弄清深度机制的收益/策略。只需弄清**操作要改什么、参数与约束、是否被原游戏接受、是否正确改变业务状态并持久/可再次读取**。赛场价值和AI策略效用是下一阶段。

## 1. 操作能力研究目录（全覆盖寻址，逐类可行性结论）

| 领域 | 想交给原生游戏的最小输入 | 首选原生操作链 / 验证重点 | 首轮目标 |
|---|---|---|---|
| **C1 教练攻防重点/策略** | Team/Coach、`POEDefense=13 (PROTECT_PAINT)` 或同类真实枚举、当前会话 | 原生 Setter/Manager Update/AI共享业务服务，游戏读回攻防共享字与关联设置；无需先证明赛场战术因果 | **第一优先打通真实Native操作PoC** |
| **C2 轮换/出场时间/战术与训练** | 球队、球员、槽位、分钟、战术/训练参数 | Rotation/Gameplan/Training Manager原生事务入口、必要刷新与约束 | 第二优先根据现有代码/场景推进 |
| **C3 球员属性/倾向/徽章/状态** | 球员ID、属性/倾向/徽章ID、目标值/等级 | 优先共享的原生属性应用/进展/状态Setter，区分自然成长、编辑与游戏AI业务；合法值、关联刷新 | 尝试一项可逆且低副作用的属性或倾向原生设置 |
| **C4 AI–AI 交易** | 双方Team、球员/选秀权/资产包 | AI proposal/evaluation（若需要）→ Validate → Commit 或共享事务核心；验证名单、合同、薪资、选秀权、记录/缓存 | 先定位有上下文的完整链，再考虑真正交易PoC |
| **C5 签约/自由球员/续约** | Team、球员、合同条款/薪资/选项 | AI市场/合同合法性 → 原生签约Commit或共享引擎事务；真实合同/名册/球队薪资 | 建立事务候选/能力等级，找到时可做隔离测试 |
| **C6 选秀/选秀权** | 选秀球队、候选球员、顺位/轮次或签权 | AI Draft Pick Selection / Commit、身份状态及选秀权与新秀归属/合同 | 建立真实原生流程候选，不强制提前推进赛季 |
| **C7 其他高价值AI动作** | 如阵容调整、球队重点或批量训练等 | Codex自主选且说明与原版AI可执行行为的关系 | 鼓励新发现，但不替代C1–C6报告 |

C1–C6 逐类列出`Native功能入口/调用所需上下文/输入值域/成功读回/不足证据/实现成本`，没有就明确`NO_ENTRY_FOUND_IN_SEARCH_SCOPE`、`NOT_IN_CURRENT_GAME_MODE`、`DANGEROUS_TO_CALL`等**有边界结论**，不能把“没找到”写成“不存在”。不强求每个领域都必须在一次迭代内完成真实调用。

## 2. 最小必须能运行的工程证明（不是纯文字）

### P0: 调用管道而非另一套规则解释

用现有 `rea_ai_prototype/` 作为基础，新增或改进：
- `NativeActionSpec`：`action_id`、适用`game_build`/模式、目标对象身份及生命周期、函数定位锚、ABI/this/线程/场景、合法输入和预期原生状态、权限级别、风险/失败处理。
- `NativeActionInvoker`：把外部输入参数编排为实际函数调用所需的对象/结构/枚举，不是仅在Python中模仿调用。REA若不能直接提供安全Native Call API，可以在证据支持下用`REA定位/Frida NativeFunction执行`或其它可行的技术方法，明确各组件作用。**从API/符号/参数/实际游戏对象一路给出真实证据**。
- `NativeActionReceipt`：`NOT_FOUND`、`CANDIDATE_ONLY`、`READY_FOR_BOUNDED_POC`、`REAL_GAME_CALL_EXECUTED_UNVERIFIED`、`REAL_GAME_EFFECT_VERIFIED`、`FAILED_OR_ABORTED`；引用代码版本、真实游戏build、输入参数、结果和fresh读取。离线Fixture`PASS`不能升级。
- **支持操作发现与实际可调用状态分离**：即使没有获得真人的effectful许可，也须形成可运行的`preflight/read-only candidate/ABI test/fixture`工具；不能用“所有原生操作必须完全理解AI决策数学”作为开发开始的条件。

### P1: 尽早实现一个 **真正的 NBA2K22 内部函数成功改变游戏设置** 的端到端PoC

**优先 C1**：在已隔离的离线MyLEAGUE测试存档/场景，指定球队的**AI或AI共用的原生设置函数**，把防守重点变更为 `PROTECT_PAINT=13`（或由现场原生enum证实的等价参数）；验证改前值、真实调用、改后值以及重进相关设置/页面是否一致，必要时观察是否被覆盖。**不必先证明比赛AI会怎样防守**。

若 C1 受版本/调用约束无法到达，有充分依据时**可主动换成 C2轮换/训练、C3单一属性等更安全动作**。不应在某一Setter上无限反编译。说明为什么切换、做了多少探索以及下一条最优线索。

注意真实**验证路径不是必须经过游戏内Human操作菜单**：可以利用只读游戏数据对照，但不能把自动点击/手动确认当成Native操作PoC。

### P2: 第二个不同业务领域 PoC（条件性）

若第一项有游戏级成功及可重复条件，优先选择**C3单球员某项可逆属性或倾向**，证明通用Native调用器可扩展，而不是只为POE硬编码。交易/签约/选秀为事务性操作且关联资产广，除非已具有完整提交与恢复证据，否则先证明入口与上下文，**不能用改TeamID/ContractID伪造原生交易成功**。

## 3. 怎么定位函数：Codex可自行突破旧路线，但报告必须真实

建议顺序（不是强制）：
1. 从已知真实COACHDATA字段`+316`、已验证Native枚举、旧`coach_codec`和`Gameplan Manager`对象、Native类型名及REA type/member references，追踪谁**修改**POE，而不只是谁**读取**它。以WRITE xref / Method / dispatched command / setter注册项为高信息增益入口。
2. 把游戏一次自然发生的AI相同行为或可观察设置状态转换作为基准，观察函数入口/目标对象/线程与变化值；若只可通过Human UI触发观察，须标签为对照辅助，**不能偷换为AI专属调用证据**。
3. 在静态证据足够时用Frida/REA对候选调用点做**有预算、可清理、不会改游戏行为的短trace**，记录 caller、this、argument marshal 的证据成熟度。不要把没捕获事件等同函数不存在。
4. 选一个低风险、可逆、参数和值域明确的原生动作，经独立测试场景批准后，进行游戏级调用/新采读回。若REA内置功能限制，则对比替代的同进程调用方式，不强求全部调用必须由REA单个接口实现；本任务目标是**通过REA逆向定位并复用原版Native业务机制**。
5. M3/M5/M6优先列真实业务事务候选、上下文、失败条件。找到可调用的共享底层服务即有效探索，但不强求复现原AI的全部决策策略。

**技术自由度**：允许Codex自选Python/Frida/REA/Capstone、小范围反编译器、PE引用图、内部工具和有价值的新假说；可写一个最小RPC或调用桥，若具实证优势；可以跨C1–C6调整顺序；**不能把纯Python Fixture调用冒充成功。**

## 4. 探索与真实修改的区别：尽量少的硬门，但不冒险盲调用

过去 STAFF 范围、352对齐和核心球队ID的先验守卫已经误伤可读调查。**本任务继续保持：身份/来源假设不能阻断已经批准的有界只读探索**。不同层次应区别：

- **静态/离线探索**：Codex自行执行，不用逐函数、逐字段请求Human；有界失败/证据来源即可。
- **已经获准的真实游戏只读查看与短trace**：继续在实际Human批准范围内进行，不因为未知STAFF身份或“原AI控制权”而自动全局中止；先验证页面可读/预算/异常隔离。新增出原批准范围的游戏操作另按其类型获得许可。
- **真实Native变更调用**：先验证针对当前版本的真实函数与参数/对象上下文，确保不会直接破坏正常游戏状态，使用可单独回滚的**测试存档或被Human明确允许的可恢复对象**。相同场景、同类函数的有限调用可合并成**一次范围化Human实验许可**，而不是每个字段反复审批。**本任务书不是对任何未知函数一次性无限调用的许可**。
- **交易、签约、选秀等不可逆/高影响事务**：研究、定位、参数模拟与短trace可以先行；真实提交和赛季推进必须在测试保存隔离、全域资产读回条件满足且Human授权覆盖时才执行。
- 对于共享Native Setter，是否具有原版AI caller与当前球队引擎AI旗标，作为**来源与适用性证据字段**，不是对所有共享Setter绝对硬门。满足函数真实参数、控制对象合法性、业务效果和执行权限就可测试；若其内部业务确实依赖AI controller位，再针对该机制单独处理。
- **不应因不确定比赛策略的深层效果而阻断“设置值写入→游戏回读相等”的原生Setter验证。** 对功能效果的后置检查只按本轮真正目标：动作已被原生引擎接受并正确更新相应游戏业务状态；对交易类事务必须验证必要资产不变量。
- 不修改master、不对现有正式存档做未经允许的高影响业务提交、不让Codex自动替Human批准或改变Windows权限/安全配置。

**PoC小范围准入单**（遇到首次effectful游戏调用时才需提交；不妨碍此前全部静态与只读探索）：
```yaml
experiment_id: EXP-NATIVE-ACTION-01
game_build_sha256: LIVE_REVERIFY
scene_and_test_save: FRESH_IDENTIFIED_AND_ISOLATED
target_action: COACH_SET_DEFENSE_FOCUS
target_object_and_value: TEAM_COACH + PROTECT_PAINT_ENUM_13
entrypoint_RVA_and_type: SOURCE_BACKED_OR_NOT_READY
ABI_this_thread_lifetime: SPECIFIED_OR_NOT_READY
script_sha256_and_rollback_readback: READY_OR_NOT_READY
call_budget: BOUNDED_EG_1_TO_3
pre_and_poststate_comparison: POE_WORD_AND_ASSOCIATED_SETTINGS
Human_scope_approval: PENDING_FOR_FIRST_EFFECTFUL_CALL
```
批准一个可界定的PoC场景包即可，不要把自动审批流程复杂化。

## 5. 面向 Human 的交付物（按工程与证据，不按文档页数）

A. **Native Action Capability Atlas**：C1–C6各有一行清晰结论，输入/本机候选/使用Native可能性/已证明等级/卡点；不得用泛泛“正在研究”代替。
B. **实际代码**：能接受`SET_COACH_POE(team,13)`等有类型的命令，至少完成真实函数查找/调用前置工具及一个隔离PoC（如已获许可、技术资格已满足）。不许只是重新包装Python字典模拟。
C. **一个优先的真实游戏动作结果**：给出真实游戏的精确构建、函数/参数/上下文及操作前后读回；若实际找不到安全入口或未获得必要许可，交付可证伪的不可行性/障碍和下一次最有效实验，明确`NO_REAL_ACTION_VERIFIED`，绝不编造成功。
D. **第二业务域扩展验证**：按证据进展决定是否真正执行（默认球员属性/轮换），不是强制做交易写入。
E. **原系统替代判断**：为每类动作标`REPLACE_MEMORY_NOW / NATIVE_CANDIDATE_MORE_EVIDENCE / KEEP_EXISTING_MEMORY_OR_EXTERNAL_EXECUTOR / NO_SAFE_PATH`，仅依据实际游戏事实、兼容性与权限；不能因为研究到一个地址就声称可替代旧Writer。
F. **最短可复现报告**：一条最重要动作的技术路径、日志与代码、失败证据、当前剩余领域与合理优先级、新发现/原型修改、技术成本。保留累计成本但不把token数量当成成果。
G. 若Native实际能更快地达到一致业务结果，**可以减少深层机制原理文档**。这次不要求解释`PROTECT_PAINT`策略收益或比赛AI战术消费者。角色知识说明仍保留已知/UNKNOWN，避免向模型编造游戏规则。

### 本轮完成门的实质判据

`SUCCESS`：至少一个 **NBA2K22实际进程** 通过所定位的原生函数/共享引擎业务服务**接受外部传入值并产生与该动作匹配、可复查的游戏状态变化**（附授权与隔离读回）；同时形成覆盖多领域的后续可用性目录。  
`PARTIAL`：可信函数入口、参数上下文、可试验调用桥已搭好，但没有得到真正游戏业务变更证明；报告具体下一步。  
`BLOCKED_WITH_EVIDENCE`：原生代码可达性、版本或必要场景确有实证阻碍；保留可用的现有Writer或外部执行路线，不为了漂亮状态强行报告Native成功。

没有任何“必须一轮研究完6类操作才能提交”的要求。**但只有纯Fixture和只读字段而没有新的Native动作链研究，不应再称达成本轮核心目标。**

## 6. Git和协作规则

- 仅在`task/nba2k22-rea-native-ai-action-invocation-20261027`及其有据子分支开发；基础PR #10仍是只读依赖来源，不在此任务代用户合并master。
- Codex只有用户实际指定的本地窗口能接收本Issue：GitHub Issue/分支**不是**自动运行触发器。
- 新Run位置：`01_os/07_content/_runs/run-20261027-nba2k22-rea-native-ai-action-invocation-001/`。工程新增源码可放`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/`或合理扩展现有REA原型；避免一次重写既有GM/Coach/Player生产接口。
- 建议新PR以**上一轮实验分支**为base（或待上一轮PR最终集成之后再rebase），使本轮差异只包括Native Action部分；**严禁因为PR #10已存在就合并master**。
- 真实进展与探索失败要能验证；影响控制权、交易签约存档规则及重要产品目标的分歧交Human选择，其余原型设计Codex自主迭代。

**最后强调：这轮最重要的问题是，“外部 AI 输入一个动作参数后，能否借助REA发现并调用NBA2K22原生业务函数，让游戏自己完成相同的操作？”** 不要再将主线引回战术深层影响解释。