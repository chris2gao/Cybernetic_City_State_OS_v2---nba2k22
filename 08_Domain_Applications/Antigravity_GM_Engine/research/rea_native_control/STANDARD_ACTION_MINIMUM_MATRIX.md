# STANDARD_ACTION_MINIMUM_MATRIX.md
## NBA2K22 REA · 常规原生操作最小能力矩阵与边界核定

> **文档性质**：Gemini 辅助研究交付文档（只读研究与结构化整理），供 Codex（正式工程 Owner）额度恢复后独立验证与选择性接收。
> **基线环境**：
> - 正式工程基线：`baseline/nba2k22-native-execution-checkpoint-014-20261029` @ `6151ef5d484914edcec2fbcfcf3bcce83a848907`
> - Gemini 研究参考：`gemini_rea` @ `6cad7c7454798dbe18e7bd800d85e2a9d1c7119c`
> - 独立审计输入：`HIGH_RISK_CONFLICTS.md` @ `d9c0e173`
> - 目标游戏可执行文件：`NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
> - 运行模式：PC22 Steam 离线 MyLEAGUE（本世代）

---

### 一、最新 Human 使用边界与核心原则

1. **角色原生操作第一目标**：使 GM、Coach 以及后续适用的 Player 角色能够受控触发游戏已有的常规原生能力。不追求在外部 Python/Node 环境中实现完整 NBA 劳资协议（CBA）或自定义规则引擎。
2. **重点操作收敛范围**：
   - **双队球员交易**：1换1、多换多互换。
   - **简单球员与选秀权交易**：仅限所有权明确的球员与未来选秀权，严禁开发复杂的保护条款、互换权（Swap）及衍生特例。
   - **最多三方交易**：必须独立证明游戏原生引擎是否支持；未证实前严格标记为 `NOT_BOUND` / `NOT_CALLABLE`，不脑补三方原子事务。
   - **个人训练**：严格限定于 PC22 离线 MyLEAGUE 真实存在的预设训练模板（Preset Templates），严禁开发自定义属性滑块修改系统。
   - **常规教练设置、轮换、分钟与战术**：收敛到已有原生 Native Call 与只读投影，区分内存投影与存档持久化。
3. **真实引擎分工**：比赛实时运行、胜负裁决、球员自然成长/衰退、真实疲劳与伤病演进，完全由 NBA2K22 原生引擎负责，外挂系统严禁伪造数值或直接篡改属性。
4. **防通胀红线**：严禁将“研究覆盖数量”（Research Coverage）冒充为“功能实现数量”（Implemented Capability）。

---

### 二、常规操作最小能力矩阵 (Master Capability Matrix)

#### 1. GM 交易操作 (Trade Domain)

| 序号 | 需求 ID & 操作语义 | Action ID & 准确来源 | 参数、对象身份、阶段与权限合同 | 实机证据等级 | 剩余静态/读回/持久化缺口 | Gemini 已知错误与 Codex 基线冲突 (P0/P1) | Codex 最小独立验证方法 |
|---|---|---|---|---|---|---|---|
| T01 | **双队球员1换1交易**<br>`GM.TRADE.EXECUTE_AGREED` | `TRADE_EXECUTE_AGREED_PACKAGE`<br><br>来源 1: `src/approved_trade_executor.py`<br>(`ownership_transfer_v2`)<br>来源 2: `runtime/trade.js`<br>(RVA `0x1413be6e0` / `0x132b040`) | **参数**：`team_a`, `team_b`, `players_a` (1人), `players_b` (1人), `execution_mode`<br>**身份**：双向 Roster 指针与球员 UID 核验；<br>**阶段**：交易截止日前（Trade Window Open）；<br>**权限**：双方 GM 身份授权与 host `TradeAgreement`。 | **L3 (实机验证通过)**<br>实测证据见 `_exports/execution/mc_haliburton_2021/W02_approved_v1/`（CHI/DET 实机交易成功，玩家 UI 验收确认）。 | 1. 内存修改方案必须维护 `team+0xCB1`（常规名单人数）与 `team+0x1047`（活动名单高4位计数）；<br>2. 原生 `trade.js` 调用需确保 `trade.context` 非空且生命周期就绪；<br>3. 跨赛季/新存档重载需依赖游戏保存。 | **P0 冲突**：Gemini 曾尝试在 `trade_package_codec.py` 中自行计算 CBA 薪资匹配；Codex 基线明确约束：GM 指定 WHO/WHAT/TERMS，由游戏引擎自行检验合法性，执行器不塞入外部 CBA 规则。<br>**P0 冲突**：Gemini 误将 Batch 描述为原子事务；Codex 明确 batch 不是底层原子事务。 | 1. 运行 `tests/test_approved_trade_executor.py`；<br>2. 在离线 MyLEAGUE 中执行两队 1v1 交易，验证内存中名单指针、`0xCB1`、`0x1047` 读回及游戏交易菜单显示。 |
| T02 | **双队多球员互换交易**<br>`GM.TRADE.MULTI_PLAYER` | `TRADE_EXECUTE_AGREED_PACKAGE`<br><br>来源：同 T01 | **参数**：`team_a`, `team_b`, `players_a` (多选), `players_b` (多选)<br>**约束**：转出后双方常规名单人数不超过 15 人，活动名单不超过 13 人；五人引用组保持完整。 | **L3 (实机验证通过)**<br>CHI/DET 实测涉及 5 名球员，经受控人数修复后完全稳定。 | 多人转队时活动名单指针空洞压缩与重排；双向合同（Two-Way）球员若在活动名单中需特殊保护，防止越界。 | 同 T01。Gemini 离线测试未覆盖 15 人常规容量溢出防护，Codex 必须保留人数上限硬校验。 | 构造 2换2 或 2换3 测试用例，验证交易后双方 `+0xCB1` 是否等于常规指针数，`+0x1047` 高4位是否等于活动名单数。 |
| T03 | **简单选秀权交换**<br>`GM.TRADE.PICK_ONLY` | `TRADE_EXECUTE_AGREED_PACKAGE`<br><br>来源 1: `src/approved_trade_executor.py`<br>来源 2: `runtime/trade.js`<br>(`trade.add_pick` @ RVA `0x12ec130`) | **参数**：`picks_a`, `picks_b`<br>**对象**：32字节 Draft Pick 结构体，当前所有者指针偏移 `+0x00`；<br>**约束**：无保护、无互换权；仅限游戏原生已读未来 5 届选秀权（依据 `PLAYER_RULES_20261021_V4`，废除旧3年人为限制，但不得扩展至未认证年份）。 | **L3 (实机验证通过)**<br>CHI/DET 包含 3 枚选秀权转让，内存回读与重启后归属保持一致。 | 选秀权在更替持有队后，在后续模拟选秀大会（Draft Event）中的原生消耗闭环；选秀顺位界面实时刷新。 | 旧代码 `src/gm_core/calculations.py` 仍残留 `+3` 年硬编码；Codex 需确保世界政策同步为 V4。 | 验证选秀权当前所有者指针 `pick+0x00` 写入前后的原子性，核对选秀权历史原队（Original Team）与年份未被污染。 |
| T04 | **球员与选秀权混合交易**<br>`GM.TRADE.MIXED` | `TRADE_EXECUTE_AGREED_PACKAGE`<br><br>来源：同 T01/T03 | **参数**：`players_a`, `picks_a`, `players_b`, `picks_b` 组合<br>**约束**：同时满足名单人数限制与选秀权所有权核验。 | **L3 (实机验证通过)**<br>CHI/DET 实机即为 5 球员 + 3 选秀权混合交易。 | 资产间依赖关系失败时的部分写入隔离；由于缺少原生原子回滚，失败时必须立即中断并保留回执。 | 同 T01。禁止任何自动补齐资产或寻找替代人的逻辑。 | 验证混合请求的解析、计划生成与单次通过执行。 |
| T05 | **三方交易**<br>`GM.TRADE.THREE_TEAM` | **无原生绑定 (NOT_BOUND)**<br><br>来源：`DEFERRED_NATIVE_CAPABILITIES_20261029.json` 明确标为 `NOT_BOUND` | **合同状态**：`NOT_CALLABLE`。<br>目前无任何合法 ABI 合同。原生私有交易提案内存块（1668字节）仅为双队设计（`proposal.add(4).writeU16(team_a)`，无 Team C 槽位）。 | **L0 (无实机证据 / 纯理论推断)**<br>实机 MyLEAGUE 交易界面仅支持双队。 | 1. 原生 2K22 PC 离线引擎是否存在三方交易对象完全未知；<br>2. 原生交易 ABI `trade.process` 不接收第三支球队；<br>3. 失败副作用不可控。 | **P0 严重冲突**：Gemini 在 `W03_10/EVIDENCE_LEDGER.json` 中声称 `Trade_CommitTransaction` (0x132b040) 支持 multi-party 并实现原子提交。Codex 审计（`HIGH_RISK_CONFLICTS.md`）明确指出这是严重推论放大，坚决拒绝！ | **Codex 接收处置**：严格保留为 `DEFERRED_NOT_AUTHORIZATION`。除非有人在真实 PC22 UI 中找出原生三方交易入口，否则禁止作为原生 Native 调用暴露。 |

---

#### 2. 教练常规设置与战术操作 (Coach Strategy & Tactical Domain)

| 序号 | 需求 ID & 操作语义 | Action ID & 准确来源 | 参数、对象身份、阶段与权限合同 | 实机证据等级 | 剩余静态/读回/持久化缺口 | Gemini 已知错误与 Codex 基线冲突 (P0/P1) | Codex 最小独立验证方法 |
|---|---|---|---|---|---|---|---|
| C01 | **防守重点 (POE Defense)**<br>`COACH.STRATEGY.POE_D1` | `COACH_APPLY_DEFENSE_POE`<br><br>来源：`runtime/coach_poe.js`<br>调用 `coach.apply_gameplan` | **参数**：`team_id`, `value` (0..31), `expected_before`<br>**对象**：Coach 结构体偏移 `+316` 低位（shift 0，掩码 31）；<br>**阶段**：任意管理阶段/赛前。 | **L3 (实测成功)**<br>基线登记为 `PRIOR_LIVE_SUCCESS`。 | 1. 目前仅更新当前内存中的 Coach Projection，未写入存档中的持久化 Gameplan 记录（`SCOPE: CURRENT_COACH_PROJECTION_ONLY`）；<br>2. 游戏重启后若未触发自然保存，可能重置。 | **P1 冲突**：Gemini 误将内存脏标记和 Projection 推广为“已持久化保存并在比赛中完全生效”；Codex 明确界定其为只读投影与单次应用，缺少 Save/Reload 授权。 | 调用 `coach_poe.js` 写入 POE_D1，并在游戏内部“教练设置”界面核对选项是否同步变动。 |
| C02 | **进攻重点 (POE Offense)**<br>`COACH.STRATEGY.POE_O1` | `COACH_APPLY_OFFENSE_POE`<br><br>来源：`runtime/coach_poe.js`<br>调用 `coach.apply_gameplan` | **参数**：`team_id`, `value` (0..31), `expected_before`<br>**对象**：Coach 结构体偏移 `+316` 高位（shift 15，掩码 31）。 | **L2 (调用逻辑已恢复)**<br>`CALL_LOGIC_RECOVERED`。Node VM 测试通过。 | 同 C01，持久化依赖 Save 触发。 | 同 C01。 | 测试 shift 15 写入，验证 Coach 结构体 `+316` 字节未破坏低位防守 POE。 |
| C03 | **常规教练战术偏好**<br>(RunPlay, ZoneUsage, BenchDepth, BenchUse)<br>`COACH.STRATEGY.RUN_PLAY`<br>`COACH.STRATEGY.ZONE_USAGE`<br>`COACH.STRATEGY.BENCH_DEPTH`<br>`COACH.STRATEGY.BENCH_USE` | `COACH_SET_KNOWN_CURRENT_SETTINGS`<br>`COACH_SET_ROTATION_POLICY`<br><br>来源：`runtime/coach_settings.js`<br>基于 `data/coach_settings.json` | **参数**：`team_id`, `settings` 字典：<br>- `run_play_tendency` (0..100)<br>- `zone_usage` (0..100)<br>- `bench_depth` (0..15)<br>- `bench_utilization` (0..100)<br>**对象**：Gameplan 输入缓冲区对应偏移（`0xe0`, `0xe2`, `0xde`, `0x138`）。 | **L2 (调用逻辑已恢复)**<br>`CALL_LOGIC_RECOVERED`。离线测试验证 10 项字段单向映射。 | 1. BenchDepth 原生 UI 端点未完全对应，若传入非法深度（如 255）会导致未定义行为；<br>2. 仅限已恢复的 10 项当前 Coach 字段子集。 | **P1 冲突**：Gemini 将局部解构出的字段视为完整教练系统；Codex 限制为只读/单次 Apply，超出字典的字段一律拒绝。 | 针对单支球队修改 `run_play_tendency`，回读 Gameplan 与 Coach 内存块，验证邻近字段零污染。 |
| C04 | **对手比赛计划获取与创建**<br>`COACH.PLAYBOOK.OPPONENT_PLAN_FIND` | `COACH_ENSURE_OPPONENT_GAMEPLAN`<br><br>来源：`runtime/gameplan.js`<br>调用 `gameplan.ensure_opponent` | **参数**：`team_id`, `opponent_team_id`<br>**对象**：Franchise Manager `+0x7854`。 | **L2 (调用逻辑已恢复)**<br>`CALL_LOGIC_RECOVERED`。 | 1. 仅能实现 Get-or-Create 880 字节的对手记录容器；<br>2. 内部具体参数编辑与提交路径未闭合。 | 无法保存并应用到 29 支对手的正式比赛中。 | 调用原生 `ensure_opponent`，核对返回指针所有者与对手 ID 是否匹配。 |
| C05 | **战术手册与槽位替换**<br>`COACH.PLAYBOOK.PLAYBOOK_SELECT`<br>`COACH.PLAYBOOK.BOOK_ADD / REPLACE` | `COACH_REPLACE_PLAYBOOK`<br>`COACH_ADD_REPLACE_PLAY`<br><br>来源：`data/action_registry.json` | **状态**：`PARTIAL_BINDING`。<br>战术槽位 68 槽操作。 | **L1 (静态候选)**<br>静态逆向发现 CRC 与槽位布局，但未恢复稳定运行时调用。 | 1. 战术手册 360 字节结构、68 槽 CRC 校验及 Flush 机制不完整；<br>2. 槽位移除（REMOVE）与互换（SWAP）为 `NOT_BOUND`。 | **P1 冲突**：Gemini（`playbook_68_codec.py`）将 `cmp eax, 0x44` 推广为 68 槽完全证明；Codex 明确指出 Flush 缺口依然存在。 | Codex 暂不开放生产级写操作，仅保留为静态候选。 |
| C06 | **18项个人对位防守设置**<br>`COACH.DEFENSE.*` (18项) | **全部无原生绑定 (NOT_BOUND)**<br><br>来源：`DEFERRED_NATIVE_CAPABILITIES_20261029.json` | **合同状态**：`NOT_CALLABLE`。无 Native ABI、上下文及回读绑定。 | **L0 (无运行时证据)**<br>仅有局部比特位反汇编猜测。 | 缺少每个字段的原生枚举、指定球员对位 Context、Setter 函数及 UI 保存生效链。 | **P1 严重冲突**：Gemini（`defense_18_codec.py`）将位段初始化和两次拷贝推广为 18 项完整原生 Setter；Codex 审计明确指出 18 项均无正式 Setter 合同，坚决拒绝伪造实现。 | 维持 `DEFERRED_NOT_AUTHORIZATION`，本阶段不纳入最小可用集合。 |

---

#### 3. 轮换与分钟操作 (Rotation Domain)

| 序号 | 需求 ID & 操作语义 | Action ID & 准确来源 | 参数、对象身份、阶段与权限合同 | 实机证据等级 | 剩余静态/读回/持久化缺口 | Gemini 已知错误与 Codex 基线冲突 (P0/P1) | Codex 最小独立验证方法 |
|---|---|---|---|---|---|---|---|
| R01 | **单球员出场分钟分配**<br>`COACH.ROTATION.PLAYER_MINUTES` | `COACH_ROTATION_SET_PLAYER_MINUTES`<br><br>来源：`runtime/rotation_minutes.js`<br>调用 `rotation.set_player_minutes` 与 `rotation.mark_team_change` | **参数**：`team_id`, `player_id`, `minutes` (0..48 整数)<br>**对象**：Delegate 虚表驱动，目标球员槽位 `+0xf8` bits 18..24 (掩码 `0xfe03ffff`)；<br>**约束**：全队 15 人常规名单校验，分钟数范围合法。 | **L2 (调用逻辑已恢复)**<br>`CALL_LOGIC_RECOVERED`。测试套件 `test_rotation_minutes.py` 验证位段写入与标记置位。 | 1. 修改单个球员分钟不会自动配平全队 240 分钟总额（`automatic_minute_balancing: false`）；<br>2. 仅完成当前上下文内存写与标记，需依赖存档或界面推进持久化。 | **P1 冲突**：Gemini 将单球员分钟设置推广为“完整首发轮换业务闭环”；Codex 指出仅逐人分钟有已恢复 Native 调用，全轮换尚未闭合。 | 在 MyLEAGUE 中执行特定球员分钟修改（如调整为 32 分钟），通过 `rotation_minutes_harness.js` 验证位段读回，并进游戏“轮换时间表”菜单核验。 |
| R02 | **完整轮换顺序与时间线**<br>`COACH.ROTATION.ROTATION_ORDER`<br>`COACH.ROTATION.STARTING_FIVE`<br>`COACH.ROTATION.SECOND_UNIT` | **未在搜索范围内找到 (NOT_FOUND_WITH_SEARCH_SCOPE / NOT_BOUND)**<br><br>来源：`DEFERRED_NATIVE_CAPABILITIES_20261029.json` | **合同状态**：`NOT_CALLABLE`。 | **L1 (仅有静态布局猜测)**<br>Gameplan `+0x18c` 存在 48 阶段 480 字节时间线猜测，但无受控写接口。 | 1. 深度图（Depth Chart）首发与替补关联未恢复原生提交函数；<br>2. 48 分钟细分切片覆盖缺乏合法性防崩校验。 | **P1 冲突**：Gemini 尝试编写 48 分钟切片时间线编解码器，但游戏无法接受外部构造的时间线覆盖；Codex 明确限制其为未闭合功能。 | 维持延期状态。禁止直接写内存覆盖深度图。 |

---

#### 4. 训练与成长操作 (Training & Development Domain)

| 序号 | 需求 ID & 操作语义 | Action ID & 准确来源 | 参数、对象身份、阶段与权限合同 | 实机证据等级 | 剩余静态/读回/持久化缺口 | Gemini 已知错误与 Codex 基线冲突 (P0/P1) | Codex 最小独立验证方法 |
|---|---|---|---|---|---|---|---|
| TR01 | **球队单日训练安排与强度**<br>`TRAIN.TEAM_SCHEDULE`<br>`TRAIN.TEAM_INTENSITY` | `TRAIN_TEAM_SET_SCHEDULE`<br>`TRAIN_TEAM_SET_INTENSITY`<br><br>来源：`runtime/training.js`, `training_intensity.js`<br>调用 `training.set_team_on_date` | **参数**：`team_id`, `date`, `intensity_raw` (0..5)<br>**对象**：团队单日 56/64 字节训练记录；<br>**约束**：仅限当日已有训练记录，遇比赛日或空记录自动安全退出。 | **L2 (调用逻辑已恢复)**<br>`CALL_LOGIC_RECOVERED`。`training_patch_harness.js` 验证通过。 | 1. 仅限**团队级（Team-level）**训练，不控制个人模板；<br>2. 对背靠背比赛日无效应。 | 严禁混淆团队每日日程与球员长期个人培养模板。 | 针对指定日期调用 `training_intensity.js`，验证私有 input+8 拷贝及 `+61` 字节强度写入。 |
| TR02 | **球队训练偏好与分项补丁**<br>`TRAIN.TEAM_FOCUS`<br>`TRAIN.TEAM_PROFILE` | `TRAIN_TEAM_PATCH_FOCUS_RAW`<br>`TRAIN_TEAM_PATCH_PROFILE_RAW`<br><br>来源：`TRAINING_PATCH_CONTRACT.md`, `runtime/training_patch.js` | **参数**：`team_id`, `date`, `focus_values_raw[3]`, `profile_values_raw[3]`, `subfocus_points_raw[38]`<br>**约束**：保留其余未请求字段，防越界。 | **L2 (离线测试通过)**<br>`OFFLINE_TESTED_ONLY`。Node VM 私有内存模型验证通过。 | 1. float32 具体 UI 单元及 38 分项对应名称仍为 UNKNOWN；<br>2. 无实机保存证明。 | 保持原始编码 0..255 纯透传，不擅自除以 100 或做外部归一化。 | 运行 `test_training_patch.py` 验证不破坏非目标字段。 |
| TR03 | **球员个人训练预设模板**<br>`TRAIN.PLAYER_FOCUS` | **无原生调用绑定 (NOT_BOUND)**<br><br>来源：`DEFERRED_NATIVE_CAPABILITIES_20261029.json` 明确标为 `NOT_BOUND` | **目标字段**：`player_training` (stride 796, 偏移 `0xC60`) 中 `+0x318` 标志位的 `player_type` (bits 11..15, 0..8) 与 `position` (bits 8..10, 0..5)。<br>**合同状态**：`NOT_CALLABLE`。 | **L1 (静态结构完全确证，但无 Native Setter 绑定)**<br>见 `config/state_io_native/training.json`。 | 1. 原生导出 Setter 函数未恢复；<br>2. 五个位置在 PC22 UI 中的真实菜单选项与 9 种 `player_type` 的精确对应关系**尚未经过实机菜单核验 (EXACT_MAPPING=UNKNOWN)**；<br>3. 直接内存写缺少脏标记刷新与持久化证明。 | **P1 冲突**：Gemini 将局部静态反汇编当做可执行完整业务；本专项明确结论：禁止盲目推断所有位置拥有完全一致的预设清单，无 UI 证据前严格标为 UNKNOWN。 | 见任务 B 交付文件 `PLAYER_TRAINING_PRESET_MAPPING.json`。Codex 后续需在游戏中打开个人训练界面逐位置记录真实菜单。 |
| TR04 | **球员个人训练强度**<br>`TRAIN.PLAYER_INTENSITY` | **无原生调用绑定 (NOT_BOUND)**<br><br>来源：同 TR03 | **目标字段**：`player_training+0x318` bits 16..18 (`intensity`, 0..5) 与 bit 20 (`is_intensity_overriden`, 0/1)。<br>**合同状态**：`NOT_CALLABLE`。 | **L1 (静态结构完全确证)**。 | 同 TR03。训练强度 (0..5: Rest~Very High) 与训练模板 (0..8) 属于完全独立的位段与概念。 | 严禁将个人强度与模板混同。 | 内存只读核对 `0x318` 位段；待 Native Setter 恢复后独立验证。 |
| TR05 | **球员师徒关系分配**<br>`TRAIN.MENTOR_ASSIGN` | `TRAIN_PLAYER_MENTOR_ASSIGNMENT`<br><br>来源：`data/action_registry.json` | **状态**：`PARTIAL_BINDING`。<br>基于 `mentorship_manager` (偏移 `0x132A8`, stride 204, 最多 10 对关系)。 | **L1 (部分绑定)**<br>社区存在崩溃分歧报告。 | 徽章槽传递、触发概率与长期 readback 尚未闭环。 | 不为追求效果私自直接改球员 Badge。 | 仅进行只读槽位检查，不投入生产级高频写。 |

---

### 三、常规原生能力收敛结论与 Codex 接入边界

1. **绝对具备实机可用性的操作（Tier 1 - Production Ready for Codex）**：
   - **双队球员交易（1v1 / 多人互换 / 选秀权混合）**：经 `approved_trade_executor.py` (`ownership_transfer_v2`) 驱动，在保证维护 `+0xCB1` 和 `+0x1047` 人数的前提下，拥有实机 L3 级别证据。
   - **单球员轮换分钟设定**：`rotation.set_player_minutes` 拥有清晰的 Delegate ABI 与位段读回验证。
   - **防守 POE 设定**：`COACH_APPLY_DEFENSE_POE` 拥有实机成功记录。
2. **仅限离线/内存投影级能力（Tier 2 - Projection / Staging Only）**：
   - **球队单日训练更新**：`training.set_team_on_date` 离线测试完备，但不可用于个人训练。
   - **进攻 POE 与常规教练战术偏好**：可完成当前 Coach 结构体投影，但跨存档持久化需谨慎。
3. **严格禁止调用 / 维持 DEFERRED 状态的操作（Tier 3 - Blocked / Non-Callable）**：
   - **三方交易**：游戏底层 proposal 结构不支持第三队，无 Native 依据，坚决维持 `NOT_BOUND`。
   - **48分钟轮换时间线与全队深度重排**：无受控提交接口，禁止外部强行写时间线。
   - **18项个人对位防守**：无原生 Setter 合同，维持延期。
   - **个人训练模板写入**：静态结构已锁定，但因缺少 Native Setter 与真实 UI 映射，维持 `DEFERRED_NOT_AUTHORIZATION`。
