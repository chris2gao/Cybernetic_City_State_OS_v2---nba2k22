# GREA-01 · Coach针对特定对手Gameplan原生保存/提交链 · Gemini首轮任务

任务状态：`READY_FOR_GEMINI` · 结果必须Codex检查，未获游戏实机写入授权。  
**仅研究本任务，不继续 GREA-02 等后续任务。**
来源：`gemini_rea`最初直接从 PR #19 的`39086984adfa554d36315382d41bc2e5d2e54c39`分叉；参考这条提交当时的72项Action / 65绑定 /61映射，不把计数当作实机成功。

## 产品需求与具体边界

教练应该能为**自己球队面对某一具体对手**保存独立的赛前Gameplan，不修改球队面对其他28个对手的计划，也不意外覆盖球队全局Coach设置/Book/Freelance。GM不负责修改此项，教练自行提供具体参数和明确取值；执行层不得替教练想战术或篡改意图。此项成功是后续18项个人防守和29队专项设置的底座。

**已经有的代码证据**（不要重复发现）：
- `COACH_ENSURE_OPPONENT_GAMEPLAN`当前有“获取/创建目标对手Gameplan”调用链，但**创建不是纯读取**，且不等于可完成持久Gameplan编辑。
- `COACH_SET_GAMEPLAN`仅`PARTIAL_BINDING`，没有被批准的完整对手计划编辑提交；`COACH_APPLY_DEFENSE_POE`及`COACH_SET_KNOWN_CURRENT_SETTINGS`是当前Coach的投影路径，**不能冒充针对指定opponent的持久保存**。
- 历史原生`Apply(Gameplan*,CoachData*)` RVA`0x146eaa0`及历史私有880字节Gameplan/352字节Coach投影是**当前字段线索**；不证明独立对手保存事务、非NULL引用、刷新/提交ABI、原生长期持久性。
- 已有K04领域研究区分Coach默认/对手专项/ACE比赛自动适应，已登记18项个人防守；这次仅取得**对手Gameplan生命周期、明确修改单项与提交路径**的可证明调用链，不扩展全部18项。

**本任务的边界**：查明一条可从外部明确输入`{team_id,opponent_team_id,field_id,value}`实现目标对手Gameplan中某个**有证据的字段**的原生业务修改/保存路径。此输入是**目标合同**，如实际Native证明需其它上下文，必须记录并提供真实合同，不能造不存在的setter。第一个字段由可靠源码证据决定，可来自K04，但不能先假设某POE字段确实存储在opponent计划。

## 前置熟悉和恢复（任务内的强制第一步）

1. 完成本Run `README.md`内的OS、项目索引、REA_WINDOW_CONTEXT_HANDOFF、最新PR19进度及K04读取。然后在`GREA_HANDOFF.md`中写**读过的具体路径/固定源SHA、最重要的5条REA经验、最新已存在调用链和要避免的错误**。不得只写“已了解”。
2. 检查当前实际可用的REA MCP/CLI工具与权限：**只读取名称、工具能力说明和非敏感状态，不读取/打印MCP配置秘钥、不安装/重装、不提权并访问游戏**。如无REA工具，明确记录不可用并以当前静态PE和源码研究继续；不能虚构已使用REA。
3. 仅使用`gemini_rea`独立工作区；不切换Codex正在写入的checkout，不清理别人的未提交文件。确认当前`git status`和本分支HEAD。
4. 优先重用：`research/rea_native_control/registry.py`、`data/action_registry.json`、`data/native_bindings.json`、`runtime_codegen.py`、`runtime/`已有gameplan处理器，`research/rea_native_control/CONTROL_CALLBACK_DISCOVERY.md`和`01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/`既有静态片段、`docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md`及既有`config/coach_tactics_profile.json`。每条新增定位指明来自哪个数据/哪个原始字节窗口。
5. 记录目标EXE构建身份和现有本地PE的来源/哈希；如果本地没有合法访问的目标二进制，不假设固定RVA正确、不从网络下载盗版游戏，只完成已有证据推演。

## 本轮技术探索步骤（全部限局部）

A. **现状盘点**：为这项操作确认输入语义、所属Coach和对手索引、目前`ensure`可能产生的副作用；明确当前Coach投影Apply为何不足以保证对手持久写入。给出1页对照。

B. **定位数据持有者**：从已恢复的目标计划Getter/Ensure返回值出发，追踪 owner/team/opponent 和对象生命周期；区分当前全局Gameplan、对手专用记录、私有复制、共享缓存。不得将Gameplan对象指针存在当作可写所有权。

C. **寻找原版调用者**：有界检查原始Gameplan编辑UI的 commit/apply/保存/离开菜单路径，确认是否存在“字段 setter → 通知/刷新 → 保存”原生函数链，并辨别GUI/非GUI线程约束。搜索到字符串、字段CRC、孤立setter或RAW memcpy均不能构成可调用完整事务。

D. **ABI/副作用证据**：如找到候选，整理RVA相对于固定EXE、函数体完整范围（含RET/尾调用）、Win64实参、this/所属生命周期、输入对象、原生上下文、要求的枚举、回读点、是否会覆盖其他28个对手或全局配置。对每个环节标`VERIFIED_STATIC`/`HYPOTHESIS`/`UNKNOWN`，不能默默填空。

E. **隔离离线候选**：只有当C/D具备有界静态证据时，才在`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/`建立**候选代码或生成器 + 受限伪Transport离线测试**；没有完整ABI就交可复现的研究脚本/候选清单，**不得写生产handler占位代码冒充已实现**。不改PR19原有正式registry/facade/runtime，必要的预期集成diff只写文字或单独patch建议。

F. **复核**：在离线fixture中核对明确Team/对手/字段/数值、遗漏其他字段保留、非目标对手不变、错误枚举/错误对象/场景失败、未知结果不可重放。测试命令应由Codex在无游戏进程环境重演；若本轮证据不足则列清阻碍和下一次最小可行研究，不偷用真实游戏写入达成“成功”。

## 明确停止条件（Gemini不做决定继续扩大探索）

- 需要全游戏Ghidra并发生重复provider_timeout，立即改为局部PE或停止；不反复重试。
- 碰到原生调用ABI、对象所有权或保存副作用未知：保留候选，不尝试实时调用。
- 仅发现`COACH_ENSURE_OPPONENT_GAMEPLAN`，而没有真实edit/commit：交`STILL_PARTIAL`证据，不宣称Gameplan已完成。
- 当前工作区与Codex冲突、Game进程需附加、需要管理员写入或需修改配置：停止相关操作并向Human报告；不要自行突破边界。
- 已取得本轮“单项可证明编辑+提交”候选后，不再顺路探索Playbook、18防守、轮换、员工或其它功能。

## 必须提交的文件（Codex可快速检查）

在`01_os/07_content/_runs/run-20261028-gemini-rea-001/GREA_01/`保存：

1. `GREA_HANDOFF.md`：版本、读取源、研究路线、真实所得、负面发现、UNKNOWN、停止原因及待Codex复核项。
2. `NATIVE_CALL_CHAIN.json`：`build_sha256`、`action_id`、`game_entity`、`source_refs`、`candidate_rvas`、`abi`、`preconditions`、`call_order`、`side_effects`、`readback_fields`、`evidence_status`、`unknowns`。字段无证据时用null/UNKNOWN，不填猜测。
3. `REPRODUCTION.md`：具体只读PE/源码重演命令、环境说明、输出哈希或精确diff、离线测试命令/结果。标注哪些本地资源不可用。
4. `CODEX_REVIEW_REQUEST.md`：最多10项最关键的Codex检查点与可接受/拒绝的依据。
5. 若有代码，放在上述 `experimental/gemini_rea/GREA_01/` 下，附真实离线测试；若没有可安全实现代码，提交研究材料也算完成本轮**探索任务**，不算完成Native功能。

遵守同一个Run下`GREA_HANDOFF_TEMPLATE.md`的字段格式。

## 最终回报格式

- `RESULT = STATIC_CANDIDATE | STILL_PARTIAL | NOT_FOUND_IN_BOUNDED_SCOPE | BLOCKED_ENVIRONMENT`
- 已确认的函数与来源；未确认项；离线验证实际运行结果。
- 是否触碰真实游戏：必须准确写`NO_GAME_ACCESS`或实际操作证据，本轮不允许主动游戏访问。
- Git固定HEAD、修改文件、复现入口、建议Codex先检查的3件事。
- 后续`GREA-02`处于`NOT_AUTHORIZED`，不自动启动。

这项实验的“成功”是**为Codex留下高价值、可复核、不会冒充实机的Gameplan机制发现或明确阻碍**，而不是要求Flash模型一次性破解完整游戏。
