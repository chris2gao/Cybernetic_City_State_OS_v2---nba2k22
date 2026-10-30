# CODEX_REVIEW_HANDOFF.md
## NBA2K22 REA · Codex 独立验证与审查交接备忘录

> **致 Codex（正式工程 Owner / Native 执行系统主工程师）**：
> 本文档是 Gemini 辅助研究模型在 Codex 额度受限暂停期间，依据用户最新指令整理的专项研究成果交付与技术交接文档。
> 
> **交接总原则**：
> 1. 本次交接绝不合并任何未经验证的代码至正式分支；
> 2. 严禁将研究覆盖度（Research Coverage）冒充为功能实现（Implemented Capability）；
> 3. 彻底纠正前期 Gemini 独立研究中的推论放大与误判（如 CBA 薪资外挂计算、三方原子交易、18 项个人防守虚假闭环）；
> 4. 聚焦于 GM、Coach、Player 的**常规原生操作最小可用范围**，由游戏原生引擎负责比赛运行与球员自然成长。

---

### 一、交付文件索引与精确 SHA 锚点

所有交付产物均存放于独立研究工作区分支：`research/rea-standard-action-and-training-preset-20261030`。

| 产物文件 | 路径与格式 | 核心价值与内容摘要 |
|---|---|---|
| **1. 常规操作最小能力矩阵** | [`STANDARD_ACTION_MINIMUM_MATRIX.md`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/STANDARD_ACTION_MINIMUM_MATRIX.md) | 逐项核定双队交易、简单选秀权、三方交易、教练设置、单人分钟、战术手册及训练等常用操作的 Native 来源、参数合同、证据等级与验证边界。 |
| **2. 个人训练预设模板映射** | [`PLAYER_TRAINING_PRESET_MAPPING.json`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/PLAYER_TRAINING_PRESET_MAPPING.json) | 机器可读 JSON。以 PC22 离线 MyLEAGUE 为目标，锁定 5 个位置、9 种通用原型枚举、强度与模板分离位段，并明确标出各位置真实 UI 菜单的 UNKNOWN 缺口。 |
| **3. 证据分级与真实缺口清单** | [`EVIDENCE_AND_GAPS.md`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/EVIDENCE_AND_GAPS.md) | 建立 L0–L3 严格证据分级，梳理静态/ABI/持久化真实缺口，系统纠偏前期 5 大历史认知误区（响应 `HIGH_RISK_CONFLICTS.md`）。 |
| **4. 审查与技术交接备忘录** | [`CODEX_REVIEW_HANDOFF.md`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/CODEX_REVIEW_HANDOFF.md) | 本文档。为 Codex 提供接收建议、拒绝清单、待定事项与最小复现测试方案。 |

- **冻结基准 Commit SHA**：`6151ef5d484914edcec2fbcfcf3bcce83a848907` (`baseline/nba2k22-native-execution-checkpoint-014-20261029`)
- **参考研究 Commit SHA**：`6cad7c7454798dbe18e7bd800d85e2a9d1c7119c` (`gemini_rea`)
- **独立审计 Commit SHA**：`d9c0e173` (`01_os/07_content/_runs/run-20261029-gemini-rea-independent-audit-001/HIGH_RISK_CONFLICTS.md`)
- **目标游戏二进制文件**：`NBA2K22.exe` (PE SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)

---

### 二、Codex 审查决策建议表 (Triage Guidance)

请 Codex 在恢复额度后，按以下分类快速处理 Gemini 的研究候选：

#### 1. 建议接收 (ACCEPT) · 具备实机或稳定离线测试支持
1. **双队球员与简单选秀权交易 (`ownership_transfer_v2`)**：
   - *接收理由*：实机硬件 L3 证据已在 CHI/DET 交易中闭环，已修复 `+0xCB1`（常规名单人数）与 `+0x1047`（活动名单高4位计数），代码位于 `src/approved_trade_executor.py`。
   - *注意事项*：严格遵守 `PLAYER_RULES_20261021_V4`（已废除未来 3 届限制，支持原生 5 届未来选秀权，禁止保护与 Swap）。
2. **单球员轮换分钟分配 (`COACH_ROTATION_SET_PLAYER_MINUTES`)**：
   - *接收理由*：通过 Delegate 虚表调用 `rotation.set_player_minutes`，更新目标球员槽位 `+0xf8` bits 18..24 并设置标记位，离线 Harness 测试与位段读回完全闭环。代码位于 `runtime/rotation_minutes.js`。
3. **教练防守重点设置 (`COACH_APPLY_DEFENSE_POE`)**：
   - *接收理由*：`runtime/coach_poe.js` 已被基线登记为 `PRIOR_LIVE_SUCCESS`，可安全投影至当前 Coach 结构体。
4. **个人训练结构体静态布局**：
   - *接收理由*：`player_training` (stride 796, 偏移 `0xC60`) 的 `+0x318` 位段确证了 `position` (bits 8..10), `player_type` (bits 11..15), `intensity` (bits 16..18), `is_intensity_overriden` (bit 20)，可供 Reader 只读消费。

#### 2. 坚决拒绝 (REJECT) · 存在严重冲突、越权或伪造闭环
1. **拒绝 Gemini 编写的外部 CBA 薪资计算引擎 (`trade_package_codec.py: validate_salary_matching`)**：
   - *拒绝原因（P0 冲突）*：GM 负责达成意向与条款，合法性由 2K22 引擎自身校验。禁止把 Python 层计算的薪资规则塞入 Native 执行器。
2. **拒绝三方/多资产原子交易提案 (`GM.TRADE.THREE_TEAM`)**：
   - *拒绝原因（P0 冲突）*：原生 1668 字节 Proposal Buffer 仅有 `team_a` 槽位，根本不支持第三支球队。游戏离线 MyLEAGUE 也没有原生三方交易界面。必须坚决维持 `NOT_BOUND` / `NOT_CALLABLE`。
3. **拒绝 18 项个人对位防守设置 (`COACH.DEFENSE.*`)**：
   - *拒绝原因（P1 冲突）*：Gemini 的 `defense_18_codec.py` 仅凭位段反汇编就声称实现闭环。实际上无原生 Setter、无对位 Context 绑定，坚决维持 `NOT_BOUND`。
4. **拒绝全队 48 分钟轮换切片时间线外部覆写**：
   - *拒绝原因（P1 冲突）*：外部直接改写 480 字节时间线极易引发游戏逻辑死锁与崩溃，缺乏官方受控提交接口。
5. **拒绝将 `coach.apply_gameplan` 当作存档持久化成功**：
   - *拒绝原因（P1 冲突）*：该调用仅修改当前内存 Coach Projection，未写入存档中的 Gameplan 根记录，不能向用户宣称持久化完成。

#### 3. 延期并等待证据 (DEFER) · 缺少关键前置输入
1. **球员个人训练预设模板 Native 写操作 (`TRAIN.PLAYER_FOCUS`)**：
   - *延期原因*：目前缺少各位置在 PC22 离线 UI 中的真实菜单选项与 9 种 `player_type` 的 1v1 映射证据（见 `GAP-ST-01`），且缺少官方原生 Setter。维持 `DEFERRED_NOT_AUTHORIZATION`。
2. **战术手册 68 槽操作 (`COACH.PLAYBOOK.BOOK_*`)**：
   - *延期原因*：CRC 校验算法未逆向完成，外部修改会导致校验失败。维持 `PARTIAL_BINDING`。

---

### 三、Codex 最小独立验证协议 (Minimal Verification Protocols)

为便于 Codex 快速实机复现与核验，提供以下 3 项最小独立验证协议：

#### 协议 1: 双队交易与人数一致性验证 (Dual-Team Trade Protocol)
- **目标**：验证 1v1 球员交易、选秀权交换及名单计数器的一致性。
- **前置条件**：游戏打开离线 MyLEAGUE 存档，记录两支测试球队（例如 CHI 与 DET）的球员与人数。
- **复现步骤**：
  ```powershell
  # 1. 计划阶段：校验资产归属与名单合法性，生成只读计划
  python 08_Domain_Applications/Antigravity_GM_Engine/scripts/execute_approved_trades.py `
      --request 08_Domain_Applications/Antigravity_GM_Engine/examples/approved_trade_request.json `
      --phase plan

  # 2. 玩家在会话中显式批准后，执行写入
  python 08_Domain_Applications/Antigravity_GM_Engine/scripts/execute_approved_trades.py `
      --request 08_Domain_Applications/Antigravity_GM_Engine/examples/approved_trade_request.json `
      --phase execute --approve-game-writes

  # 3. 独立只读复核
  python 08_Domain_Applications/Antigravity_GM_Engine/scripts/execute_approved_trades.py `
      --request 08_Domain_Applications/Antigravity_GM_Engine/examples/approved_trade_request.json `
      --phase verify
  ```
- **预期检验点**：
  1. `team_a` 与 `team_b` 的常规名单指针数组更新；
  2. `team+0xCB1` 确切反映变动后的常规人数；
  3. `team+0x1047` 高 4 位确切反映变动后的活动名单人数；
  4. 选秀权 `pick+0x00` 持有队指针更新；
  5. 游戏内部交易日志或球队名单 UI 正确显示目标球员。

#### 协议 2: 单球员出场时间设置验证 (Player Minutes Protocol)
- **目标**：验证 `rotation.set_player_minutes` 与脏标记置位。
- **离线回归执行**：
  ```powershell
  # 运行单人分钟离线 Harness 与回归用例
  node 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tests/rotation_minutes_harness.js
  python -m pytest 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tests/test_rotation_minutes.py
  ```
- **实机检验点**：
  1. 传入指定球员 `minutes=32`；
  2. 目标球员槽位 `+0xf8` 读取值 `(word >>> 18) & 127` 等于 32；
  3. 同队其余球员的 `+0xf8` 分钟位段未被破坏；
  4. 游戏内“轮换时间表”菜单显示该球员分钟变更为 32。

#### 协议 3: 个人训练底层结构只读核验 (Player Training Readback Protocol)
- **目标**：核对当前存档中球员训练位置、模板与强度底层位段。
- **前置检查脚本（Python 只读测试）**：
  ```python
  # 只读读取目标球员 training.flags dword
  # base = 0x140000000, slot_training = read_ptr(base + 0x0632B480)
  # player_record = slot_training + 0xC60 + player_index * 796
  # flags = read_u32(player_record + 0x318)
  # position = (flags >> 8) & 7       # 0..5 (PG, SG, SF, PF, C, None)
  # player_type = (flags >> 11) & 31  # 0..8 (All-Around .. Inside)
  # intensity = (flags >> 16) & 7     # 0..5 (Rest .. Very High)
  # is_override = (flags >> 20) & 1   # 0/1
  ```
- **待 Codex 推进项**：在真实 PC22 UI 中切换某球员的个人训练模板，观察上述位段如何变动，填补 `PLAYER_TRAINING_PRESET_MAPPING.json` 中的 `UNKNOWN` 项。

---

### 四、交接总结与后续建议

1. **当前分支状态**：
   - 处于独立研究分支 `research/rea-standard-action-and-training-preset-20261030`；
   - 未改动 master 分支，未改动正式基线 commit `6151ef5d`；
   - 未在正式 Registry 中激活任何未经验证的动作。
2. **后继工程路线建议**：
   - **第一步**：Codex 恢复后，直接复审并接收 `approved_trade_executor.py` 的双队交易能力与 `rotation_minutes.js` 的分钟设定能力；
   - **第二步**：组织一次轻量级的实机只读观察（被动采集），记录 PC22 离线 MyLEAGUE 个人训练界面中五个位置的真实下拉菜单文本，彻底闭合 `PLAYER_TRAINING_PRESET_MAPPING.json`；
   - **第三步**：维持三方交易、18 项个人防守与时间线覆写的封存状态，不浪费工程额度在无原生 ABI 支持的伪需求上。
