# EVIDENCE_AND_GAPS.md
## NBA2K22 REA · 实机证据分级、真实缺口清单与审计纠偏

> **文档性质**：Gemini 辅助研究交付文档，供 Codex（正式工程 Owner）额度恢复后作为独立技术验收依据。
> **基线环境**：
> - 正式工程基线：`baseline/nba2k22-native-execution-checkpoint-014-20261029` @ `6151ef5d484914edcec2fbcfcf3bcce83a848907`
> - Gemini 研究参考：`gemini_rea` @ `6cad7c7454798dbe18e7bd800d85e2a9d1c7119c`
> - 独立审计记录：`HIGH_RISK_CONFLICTS.md` @ `d9c0e173`
> - 目标游戏可执行文件：`NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
> - 运行模式：PC22 Steam 离线 MyLEAGUE（本世代）

---

### 一、取证分级标准 (Evidence Hierarchy)

为了彻底杜绝“将静态逆向推测误当实机功能闭环”的技术通胀，本专项建立四级严格证据体系（L0–L3）：

```
[ L3: PRIOR_LIVE_HARDWARE_VERIFIED ] 
  ├── 实机运行、内存写入、游戏UI界面验收及重启/重载检验完全闭环
[ L2: RUNTIME_CALL_RECOVERED_OFFLINE_TESTED ] 
  ├── 原生ABI/函数入口已恢复，通过Node VM/专用Harness完成私有内存测试，但缺少实机Save/Reload闭环
[ L1: STATIC_LAYOUT_VERIFIED_NO_SETTER ] 
  ├── 静态逆向确证PE偏移、结构体布局、位段宽度，但无受控原生写入函数或参数合同
[ L0: UNVERIFIED_SPECULATION / NOT_BOUND ] 
  └── 纯反汇编片段猜测、社区传言或外部模型编造逻辑，无原生支持证据
```

- **L3（实机硬件与 UI 验收闭环）**：必须同时满足三个条件：
  1. 在真实运行的 `NBA2K22.exe` 进程中完成受控写入；
  2. 游戏内部原生 UI 菜单（如交易核准、教练设置、轮换时间表）直接观察到相应变更；
  3. 内存读回与重启/游戏自保存后数据保持一致。
- **L2（运行时调用逻辑恢复与离线测试通过）**：
  1. 原生 ABI 签名、参数布局、Caller/Callee 关系已明确并在 `runtime/*.js` 中实现；
  2. 在 Node VM 或模拟测试桩中完成边界、脏内存、Canary 隔离及非目标字段保护验证；
  3. 但尚未在实机生产批次中进行全流程存盘与长期游戏推进验证。
- **L1（静态结构体布局确证，无运行时 Setter）**：
  1. 通过反汇编确证结构体偏移、位段（Bitfield）起止位、值域范围；
  2. 可进行只读解析（Reader），但没有官方受控的 Native Setter 调用合同；
  3. 严禁直接通过盲写内存宣称功能实现。
- **L0（未验证推断 / 延期未授权）**：
  1. 仅在代码中有常量比较（如 `cmp eax, 0x44`）或符号猜测；
  2. 未证明原生引擎是否存在相应对象；
  3. 严格标记为 `NOT_BOUND` / `NOT_CALLABLE`。

---

### 二、重点业务领域实机证据与状态审计

#### 1. 交易领域 (Trade Domain)

| 操作项目 | 证据级别 | 核心实机/静态证据来源 | 真实技术现状与边界核定 |
|---|---|---|---|
| **双队 1v1 球员交易** | **L3** | `_exports/execution/mc_haliburton_2021/W02_approved_v1/`<br>`src/approved_trade_executor.py` (`ownership_transfer_v2`)<br>`docs/37_APPROVED_TRADE_EXECUTOR.md` | **已在实机上完全证实**。<br>CHI（公牛）与 DET（活塞）球员交换成功，玩家在游戏界面验收通过。核心技术点是必须在修改球员名单引用的同时，受控维护 `team+0xCB1`（常规名单人数）与 `team+0x1047` 高4位（活动名单人数）。 |
| **双队多球员互换交易** | **L3** | 同上。CHI/DET 实测涉及 5 名球员转队。 | **实机证实可行**。<br>要求转队后双方常规名单不超过 15 人，活动名单不超过 13 人，且必须保留完整的五人阵容引用组，不得产生空槽空指针悬挂。 |
| **简单选秀权交换** | **L3** | 同上。CHI/DET 实测包含 3 枚选秀权转让。 | **实机证实可行**。<br>32 字节选秀权记录中，仅更新当前持有队指针（偏移 `+0x00`），历史原队（Original Team）、轮次与年份保持只读透传。依据 `PLAYER_RULES_20261021_V4`，废除人为的未来 3 届限制，支持原生已读的 5 届未来选秀权。严禁增加保护、互换（Swap）等复杂衍生条款。 |
| **原生 ABI 调用交易**<br>(`trade.process`) | **L2** | `runtime/trade.js`<br>RVA `0x1413be6e0` / `0x132b040`<br>`trade.context` (RVA `0x12e945b`) | **调用链已恢复，离线测试通过，待实机二次验证**。<br>构造 1668 字节私有 Proposal 内存块，通过 `trade.add_player` 与 `trade.add_pick` 装载资产，再通过 `trade.process` 提交给原生引擎。引擎自行进行内部合法性校验。 |
| **三方交易 (Three-Team)** | **L0** | `DEFERRED_NATIVE_CAPABILITIES_20261029.json`<br>`HIGH_RISK_CONFLICTS.md` | **完全无实机支持证据，坚决禁止调用 (NOT_CALLABLE)**。<br>1. 原生 Proposal 结构体仅有双队槽位（`proposal+0x04` 写入 `team_a`，无 Team C 存储空间）；<br>2. PC22 离线 MyLEAGUE 菜单仅提供双队交易与 Trade Finder，无原生三方交易 UI；<br>3. 失败时无原子回滚机制。 |

#### 2. 教练与战术领域 (Coaching & Strategy Domain)

| 操作项目 | 证据级别 | 核心实机/静态证据来源 | 真实技术现状与边界核定 |
|---|---|---|---|
| **防守重点 (POE Defense)** | **L3** | `runtime/coach_poe.js`<br>基线清单：`PRIOR_LIVE_SUCCESS` | **实机验证成功**。<br>通过 `coach.apply_gameplan` 写入 Coach 结构体 `+316` 字节低 5 位（shift 0），游戏内教练偏好设置即时变动。注意：该操作作用于当前 Coach 投影，存档持久化依赖游戏触发保存。 |
| **进攻重点 (POE Offense)** | **L2** | `runtime/coach_poe.js`<br>`test_role_batches.py` | **调用链已恢复，离线测试通过**。<br>写入 Coach 结构体 `+316` 字节高位（shift 15，掩码 31），测试证实不影响低位防守 POE。 |
| **常规教练战术偏好**<br>(RunPlay, Zone, Bench) | **L2** | `runtime/coach_settings.js`<br>`data/coach_settings.json` | **调用链已恢复，离线单向映射测试通过**。<br>覆盖 RunPlayTendency (0..100)、ZoneUsage (0..100)、BenchDepth (0..15)、BenchUtilization (0..100) 等 10 项已恢复字段。超出此范围的字段未受控，禁止传入。 |
| **对手比赛计划 (Gameplan)** | **L2 / L1** | `runtime/gameplan.js`<br>调用 `gameplan.ensure_opponent` | **仅实现容器获取，参数编辑与持久化未闭合**。<br>可以 Get-or-Create 880 字节的指定对手记录，但无法将其安全写入 29 支对手并保证跨存档持久化。 |
| **战术手册 (Playbook 68槽)** | **L1** | `01_os/07_content/.../playbook_rotation_commit_leads_001.json`<br>`data/action_registry.json` | **静态逆向候选，无稳定写接口 (PARTIAL_BINDING)**。<br>发现了 360 字节战术手册及 68 槽结构，但 CRC 校验算法、Flush 机制未闭合，槽位删除/交换为 `NOT_BOUND`。 |
| **18项个人对位防守设置** | **L0** | `DEFERRED_NATIVE_CAPABILITIES_20261029.json` (18项全部标为 `NOT_BOUND`) | **无运行时绑定，禁止调用 (NOT_CALLABLE)**。<br>仅有局部反汇编位段猜测，无原生 Setter、无 Matchup Context 绑定。 |

#### 3. 轮换与出场时间领域 (Rotation Domain)

| 操作项目 | 证据级别 | 核心实机/静态证据来源 | 真实技术现状与边界核定 |
|---|---|---|---|
| **单球员分钟分配** | **L2** | `runtime/rotation_minutes.js`<br>`tests/test_rotation_minutes.py`<br>`tests/rotation_minutes_harness.js` | **调用链恢复，内存与标志位读回验证通过**。<br>通过 Delegate 虚表调用 `rotation.set_player_minutes`，更新目标球员槽位 `+0xf8` bits 18..24，随后调用 `rotation.mark_team_change(team, 1, 0)`。测试验证邻近球员位段未被破坏。缺口：不会自动配平全队 240 分钟，需由上层角色保证总和合法。 |
| **48分钟轮换时间线与切片** | **L1** | `W03_05/EVIDENCE_LEDGER.json`<br>`Claim C-W03-05-02` | **仅有静态数据结构推测，无写接口**。<br>Gameplan `+0x18c` 存在 480 字节时间线切片结构，但外部覆盖极易引起游戏引擎崩溃，未发现官方受控提交函数。 |
| **首发阵容与轮换顺序重排** | **L0** | `DEFERRED_NATIVE_CAPABILITIES_20261029.json`<br>`TEAM_SET_STARTERS` 标为 `NOT_FOUND_WITH_SEARCH_SCOPE` | **未在搜索范围内找到原生写接口，维持延期**。<br>不能通过直接覆写内存中的 Depth Chart 宣称实现了首发设定。 |

#### 4. 训练与成长领域 (Training Domain)

| 操作项目 | 证据级别 | 核心实机/静态证据来源 | 真实技术现状与边界核定 |
|---|---|---|---|
| **球队单日训练日程与强度** | **L2** | `runtime/training.js`, `training_intensity.js`<br>RVA `0x1325f10` (`training.set_team_on_date`)<br>`tests/training_patch_harness.js` | **调用链恢复，离线测试通过**。<br>操作 56/64 字节的团队单日计划，支持日期定位与私有 input 隔离拷贝。遇比赛日自动安全退出。仅控制团队每日安排，与个人预设无关。 |
| **球队训练分项补丁** | **L2** | `TRAINING_PATCH_CONTRACT.md`<br>`runtime/training_patch.js` | **离线测试通过**。<br>纯透传 3 个 float32 focus 与 38 个 subfocus 字节，保留未请求字段。 |
| **个人训练预设模板 (Player Focus)** | **L1** | `config/state_io_native/training.json`<br>`player_training` (stride 796, 偏移 `0xC60`)<br>标志位 `+0x318` bits 11..15 | **静态布局确证，但无原生 Setter 绑定 (NOT_BOUND)**。<br>9 种通用原型（0..8）确证，但各位置在真实 PC22 UI 中的菜单映射依然为 `UNKNOWN`。无受控写接口。 |
| **个人训练强度 (Player Intensity)** | **L1** | 同上。`player_training+0x318` bits 16..18 (0..5) 与 bit 20 (`is_intensity_overriden`) | **静态布局确证，与训练模板属于完全独立的位段与系统**。<br>目前无 Native Setter，维持 `NOT_BOUND`。 |
| **球员师徒关系分配 (Mentorship)** | **L1** | `mentorship_manager` (偏移 `0x132A8`, stride 204)<br>`data/action_registry.json` (`PARTIAL_BINDING`) | **静态逆向发现最多 10 对师徒槽，但运行时写接口未闭环**。<br>社区报告直接写入易引发崩溃，维持只读检查。 |

---

### 三、真实技术缺口清单 (Technical Gaps Ledger)

为确保 Codex 恢复工作后能够直击技术痛点，以下梳理当前最为关键的四大类技术缺口：

#### 1. 静态与元数据缺口 (Static & Metadata Gaps)
- **GAP-ST-01: PC22 离线 MyLEAGUE 个人训练 UI 菜单真值缺失**
  - *现状*：已掌握底层 9 种 `player_type`（0..8）与 5 个 `position`（0..4），但缺乏真实游戏界面的文本列表与映射关系。
  - *阻断*：无法断定各位置是否显示相同的 9 项模板，或者存在位置专属模板名（如中锋显示“护框精英”、后卫显示“组织核心”）。
  - *解决途径*：测试人员需在离线 MyLEAGUE 个人训练界面截取 PG/SG/SF/PF/C 五个位置的预设模板下拉列表。
- **GAP-ST-02: 战术手册 68 槽 CRC 算法缺失**
  - *现状*：已定位 360 字节战术手册结构与 68 槽位，但其内部校验和（CRC）计算方式未恢复。外部修改槽位会导致游戏读取校验失败并回滚。

#### 2. 运行时与 ABI 调用缺口 (Runtime ABI Gaps)
- **GAP-RT-01: 个人训练缺乏受控 Native Setter**
  - *现状*：团队训练拥有 `training.set_team_on_date` (RVA `0x1325f10`)，但个人训练仅有内存位段偏移，没有恢复出原版应用模板或强度的原生函数。
  - *阻断*：直接内存 Patch 缺少游戏内通知机制与脏标记刷新。
- **GAP-RT-02: 完整首发阵容与轮换顺序 Setter 缺失**
  - *现状*：仅有单人出场时间函数 `rotation.set_player_minutes`；缺少一次性提交 15 人首发与替补深度图（Depth Chart）的原生函数。

#### 3. 回读与持久化缺口 (Readback & Persistence Gaps)
- **GAP-PS-01: 教练战术设置的跨存档持久化未闭环**
  - *现状*：`coach.apply_gameplan` 成功修改了内存中的当前 Coach 结构体（`SCOPE: CURRENT_COACH_PROJECTION_ONLY`），但没有触碰存档中的 Franchise Manager Gameplan 根记录。
  - *影响*：若游戏在未触发内部保存事件前退出，设置将在重启后丢失。
- **GAP-PS-02: 交易执行后的游戏自保存触发机制**
  - *现状*：`approved_trade_executor.py` 成功修改了常规与活动名单引用及计数，并在内存重启中观察到保留，但外挂系统没有受控的“立即保存当前存档（Force Save Game）”原生调用。

#### 4. 边界与授权缺口 (Boundary & Policy Gaps)
- **GAP-BP-01: 三方交易原生不支持**
  - *现状*：所有原生提案结构体（Proposal Buffer）均为双队设计，目前没有任何证据证明离线 MyLEAGUE 原生支持三方原子交易。强行开发三方交易属于违背事实的伪需求。

---

### 四、历史认知纠偏与审计反思 (False Claims Rectification)

在前期 Gemini 独立研究阶段（特别是 `gemini_rea@6cad7c74`），由于过度关注静态反汇编与离线 Python 测试，产生了一系列脱离实际工程的推论放大与误判。基于 Codex 独立审计文档 `HIGH_RISK_CONFLICTS.md`，在此逐一明确纠偏，立此存照：

1. **纠正“163 项闭环、21 项测试全过”的技术通胀**：
   - *错误*：Gemini 在 `W03_MASTER_GAP_MATRIX.json` 中将 184 项需求中的 163 项标为闭环，造成了几乎全部原生能力已可用的假象。
   - *纠偏*：所谓“163项通过”仅仅指 Gemini 编写的离线 Python 编解码测试通过，**绝不等同于真实游戏实机功能实现**！真实基线 Checkpoint 014 明确指出全目标未达成（`full_goal_complete: false`），绝大部分操作仍然处于 `DEFERRED_NOT_AUTHORIZATION` 或 `NOT_BOUND`。
2. **纠正在交易执行器中自行编写 CBA 薪资计算逻辑（P0 冲突）**：
   - *错误*：Gemini 在 `trade_package_codec.py` 中编写了复杂的 `validate_salary_matching` 函数，试图在 Python 层裁决交易是否符合劳资协议。
   - *纠偏*：Codex 基线明确指出：GM 的职责是达成协议并选择 WHO/WHAT/TERMS，Native 执行器只需忠实提交资产，交易合法性完全由 NBA2K22 原生游戏引擎自行检验。外部自行编写薪资算法不仅容易因 2K22 内部简化规则产生误杀，还越权侵占了游戏引擎的职责。
3. **纠正“三方/多资产原子交易”的伪造推论（P0 冲突）**：
   - *错误*：Gemini 在 `W03_10/EVIDENCE_LEDGER.json` 中宣称 `Trade_CommitTransaction` (0x132b040) 是支持多方交易的底层原子事务。
   - *纠偏*：原生执行批次明确表明“Batch 不是底层原子事务”！原生提案结构体仅支持两队，三方交易缺乏任何 ABI、所有权和失败回滚证据，坚决禁止调用。
4. **纠正将局部位段反汇编推断为 18 项个人防守完整 Setter（P1 冲突）**：
   - *错误*：Gemini（`defense_18_codec.py`）仅根据几处位掩码初始化代码，就声称实现了 18 项个人对位防守设置。
   - *纠偏*：Codex 审计证实这 18 项完全没有原生 Setter 合同，也没有 Context 绑定，纯属静态猜测。
5. **纠正“所有位置拥有完全一致训练模板”的盲目预设**：
   - *错误*：试图将 9 种通用原型简单机械地复制给 PG/SG/SF/PF/C 全部五个位置。
   - *纠偏*：本专项明确要求：没有真实 UI 或可信原生证据，不得推断每个位置一定拥有相同模板清单，未证实部分必须诚实标记为 `UNKNOWN`。
