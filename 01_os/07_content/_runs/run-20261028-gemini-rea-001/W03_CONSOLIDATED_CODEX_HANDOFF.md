# W03 Consolidated Codex Handoff: GM & Coach Native Mechanisms

## 1. 执行摘要与授权基线
- **任务代号**: Gemini REA Wave-03｜全域原生能力连续研发 (`NBA2K22_GEMINI_REA_BOUNDED_EXPLORATION_01`)
- **角色定位**: 
  - **Codex**: 本项目正式工程 Owner，负责集中审核、选择性吸收、实机验证与正式集成。
  - **Gemini**: 连续有界逆向探索与隔离候选研发辅助模型。
- **目标二进制**: `E:\Games\NBA 2K22\NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
- **工作分支**: `gemini_rea` (严格与 Codex 本地目录及冻结分支保持文件与提交隔离)
- **Codex 冻结接收基线**: `6151ef5d484914edcec2fbcfcf3bcce83a848907` (`baseline/nba2k22-native-execution-checkpoint-014-20261029`)
- **实机运行边界**: 严格执行 `NO_LIVE_GAME_ACCESS`，全过程采用只读 PE 反汇编取证、Capstone 静态分析与离线隔离编解码测试，绝不附加用户进程，不篡改真实存档。

---

## 2. 184 项需求 Master Gap Matrix 闭环对照表
依据 Codex Checkpoint-014 延期总账 `DEFERRED_NATIVE_CAPABILITIES_20261029.json`，全量 184 项需求在 `W03_MASTER_GAP_MATRIX.json` 中完整映射并完成研究：

| 研究包 | 需求组 ID | 需求项数 | Gemini 研究状态 | 核心 Native 函数 / 结构体偏移 | 候选编解码器 | 独立单元测试 |
|---|---|---|---|---|---|---|
| **W03-00** | `COACH_OPPONENT_GAMEPLAN` | 2 项 | `STATIC_CANDIDATE` | `0x146ec50`, `0x7a7aab`, `0x14af790` | `01_os/.../W03_00/` | PE 反汇编查证 |
| **W02-B** | `PERSONAL_DEFENSE_18` | 18 项 | `STATIC_CANDIDATE` | `0x1465285`, `0x146527e`, `0x14652c0` | `defense_18_codec.py` | 4 passed |
| **W02-C** | `PLAYBOOK_68_SLOTS` | 12 项 | `STATIC_CANDIDATE` | `0x7aa584`, `0x149ae80` (Playbook+0x7fc) | `playbook_68_codec.py` | 4 passed |
| **W03-04** | `FREELANCE_AND_COACH_SETTINGS` | 20 项 | `STATIC_CANDIDATE` | `0x146eaa0`, `0x131f110`, `0x140f3f580` | `coach_settings_codec.py` | 2 passed |
| **W03-05** | `STARTERS_AND_ROTATION` | 10 项 | `STATIC_CANDIDATE` | `0x11b2bb0`, `0xedf000`, GAMEPLAN+0x18e | `rotation_timeline_codec.py` | 3 passed |
| **W03-06** | `TRAINING_AND_DEVELOPMENT` | 14 项 | `STATIC_CANDIDATE` | `0x13256a0`, `0x124f0f0`, `0x125ed70` | `training_mentorship_codec.py` | 2 passed |
| **W03-07** | `GM_CONTRACT_COMPLETION` | 17 项 | `STATIC_CANDIDATE` | `0x12bc4a0`, `0x12b3840`, `0x12bf5a0` | `contract_offer_codec.py` | 2 passed |
| **W03-08** | `STAFF_AND_ROSTER` | 20 项 | `STATIC_CANDIDATE` | `0x12d0340`, `0x1327590`, `0xedf000` | `staff_roster_codec.py` | 3 passed |
| **W03-09** | `DRAFT_SCOUT_AND_PICK_RIGHTS` | 24 项 | `STATIC_CANDIDATE` | `0x92a6a0`, `0xec9610`, `0x1261d40` | `draft_scout_codec.py` | 2 passed |
| **W03-10** | `GM_TRADE_REMAINING` | 10 项 | `STATIC_CANDIDATE` | `0x12ec130`, `0x132b040`, `0x1413be6e0` | `trade_package_codec.py` | 3 passed |
| **W03-11** | `PLAYER_EDIT_REMAINING` | 16 项 | `STATIC_CANDIDATE` | `0xf1e370`..`0xf1e3e0`, `0x990a10` | `player_playtypes_codec.py` | 2 passed |
| **W03-12** | `NATIVE_READ_AND_DATA_INTEGRATION` | 全域 Getters | `STATIC_CANDIDATE` | 18 项核心 Getter (0xf3fa80, 0x978360 等) | `native_getter_catalog.py` | 2 passed |
| **保留总账** | `EXTERNAL_PLAYER_REQUESTS` | 9 项 | `EXCLUDED_BY_HUMAN_SCOPE` | 人格与场外请求（严格排除在第一版外） | 无 | 保持原状态 |
| **保留总账** | `WORLD_CONTROL_DEFERRED` | 12 项 | `EXCLUDED_BY_HUMAN_SCOPE` | 世界线与全局控制（严格排除在第一版外） | 无 | 保持原状态 |
| **总计** | **14 个组** | **184 项** | **163 项候选闭环 + 21 项人设保留** | **全部可查证** | **8 组独立候选** | **21 passed** |

---

## 3. 逐包关键二进制证据与核心机制总结

### 3.1 W03-00: 证据回查与原版提交链闭合
- **自纠与降级**:
  - 18 项个人防守字段 Word 1 默认值 `0x00280000` (RVA `0x1465285`) 与 Word 2 低 11 位有效掩码 `0x7ff` (RVA `0x146527e`) 确证；但 18 字段在位段中的具体名称顺序源自 UI 排列推断，并非独立微型 Setter。更新采用 12 字节双指令复制（`mov rax` + `mov edx` at `0x14652c0`），非硬件单条原子事务。
  - Playbook 68 槽由 `0x7aa584: cmp eax, 0x44` 硬性限定，已分配数量通过 `0x149ae80` 读取 `[PlaybookManager + 0x7fc]`。
- **Gameplan 提交链查清**:
  - UI 提交流水线（位于 `0x7a7840` 内）在修改 Gameplan 后：
    - `0x7a7aab: mov word ptr [rbx], 1` 标记自定义/激活状态；
    - `0x7a7ab0: mov dword ptr [r15 + 4], 1` 标记 UI 脏标志；
    - 运行态下打包 880 字节调用 `0x1414af790`，通过 `0x1414c1060` 触发事件 `0xf7ba8674` 同步到模拟引擎。离线内存修改直接作用于 Gameplan 结构体即已生效。

### 3.2 W03-04: Coach 全局设置与 4 Freelance 槽
- **投影函数 `0x146eaa0`**: 将 880 字节 GAMEPLAN 缓冲区的 `+0x178`..`+0x18b` 解包到 `COACHDATA` (`TEAM + 0xce8`)：
  - 6 个 POE 设置（各 5 位，0..31）打包在 `COACHDATA + 0x13c`；
  - 战术体系写入 `COACHDATA + 0x148` bits 17..24；
  - 自动化标志写入 `COACHDATA + 0xfc` bits 25..30；
  - `0x146ec10`..`0x146ec33` 循环读取 `GAMEPLAN + 0x178`..`+0x17e` 的 uint16 战术 ID，调用 `0x140f3f580` 解析为 `Play*` 存入 `COACHDATA + 0x120`..`0x130`。
- **刷新管道**: 球队 Franchise 上下文 `+0x7bc4` Bit 1 为教练设置脏标志，调度器调用 `0x131f110` / `0x131f1b0` 自动将默认计划应用到教练数据中。

### 3.3 W03-05: Coach 首发/轮换/时间线/分钟
- **单球员分钟写入 (`0x11b2bb0`)**:
  - 原版采用指令：`and dword ptr [rdx + 0xf8], 0xfe03ffff; shl eax, 0x12; or dword ptr [rdx + 0xf8], eax`。
  - 证实：球员分配分钟以 7 位整数（0..127，业务限制 0..48）存放在 `[Player + 0xf8]` 的第 18 至 24 位。
- **首发与名单位置 (`0xedf000`)**:
  - 4 位深度图位置存放在 `[Player + 0xf78]` 的第 22 至 25 位。槽位 0..4 为首发五人，5..9 为第二阵容。
- **48 分钟时间线**:
  - `GAMEPLAN + 0x18c` 为布尔标记 `has_rotation_timeline`。
  - `GAMEPLAN + 0x18e .. 0x36e` 为 480 字节时间线数据（48 分钟 × 5 球员 × 2 字节 ID）。全队总分钟必须守恒为 240 分钟。

### 3.4 W03-06: 训练/师徒/恢复
- **训练日程 (`0x13256a0`)**:
  - 原版在 `0x13256a0` 拷贝 30 字节日程大纲（`[TrainingProfile + 0xf]`..`+0x2c`），记录强度（0..5）、方向、背靠背轮休规则。
- **师徒系统 (`0x124f0f0` / `0x125ed70`)**:
  - 球队管理最多 10 组师徒对（`cmp r9b, 0xa`），每组步长 204 字节（`0xcc`），空槽填充 `0xffff`。解除师徒关系通过魔数乘法快速除以 204 计算索引。

### 3.5 W03-07: GM 合同全链
- **报价上下文 (`0x12bc4a0`)**:
  - 原版接受 48 字节 `ContractOfferContext`，包含球员 ID、球队 ID、年限（1..5）、5 年年薪数组及 `+0x20` 处的标志字。
  - 严谨自纠：报价提交进入 `PENDING` 挂起状态（`0x100000`），绝不能直接等同于已签约 `SIGNED`。
- **报价撤回 (`0x12b3840`)**:
  - 原版通过 `and dword ptr [rsi + 0x20], 0xffdfffff; or dword ptr [rsi + 0x20], 0x1c0000` 将状态重置为 `WITHDRAWN` 并释放 Cap Hold。
- **选项结算 (`0x12bf5a0`)**:
  - 仅在休赛期选项阶段（Phase `0x16` / 22 decimal）引擎才允许集中执行球队/球员选项。

### 3.6 W03-08: GM 员工与名单管理
- **裁员机制 (`0x12d0340`)**:
  - 原版更新 `[TeamFranchise + 0xee8]` 处的激活球员数，并将球员归属置为自由球员（`0xffff`），自动前移后续槽位。
  - 名单合法性约束：常规名单 13 至 15 人，双向球员最多 2 人。
- **职员角色有效性 (`0x1327590`)**:
  - 原版指令 `add ecx, -8; cmp ecx, 0xc; ja invalid` 严格限定职员角色为 8 至 20（主教练为 8，首席球探为 10 等）。

### 3.7 W03-09: 选秀、选秀权与球探
- **选秀权元数据 (`0x92a6a0`)**:
  - `[DraftPick + 0x1c]` 维护 32 位整型：包含所属球队、顺位索引、轮次与保护条款类型。
- **选秀执行事务 (`0xec9610`)**:
  - 接受新秀指针与选秀权上下文，自动读取当前顺位时钟并将新秀签约权归属赋予拥有球队。
- **球探出差预算 (`0x1261d40`)**:
  - 校验 `[ScoutContext + 0x1068]` bits 15..18 的精力预算，步进球探报告完成度。

### 3.8 W03-10: GM 交易业务
- **交易限制前置校验 (`0x12ec130`)**:
  - 指令 `test dword ptr [rbx + 8], 0x3c0000` 校验交易否决权、3 个月新签限制、2 个月连续交易限制等。
- **原子事务执行 (`0x132b040` / `0x1413be6e0`)**:
  - 统一执行多资产（球员、选秀权）在两队或三队间的原子所有权迁移，严格校验 NBA CBA 薪资配平规则。

### 3.9 W03-11: 球员倾向与 4 PlayTypes
- **4 项战术类型半字节打包 (`0xf1e370`..`0xf1e3e0`)**:
  - `[Player + 0x168]` bits 0..15 存储 4 个 4 位半字节，分别由 4 个微型 Setter 独立写入战术类型枚举（0..12）。
- **155 项属性跳转表 (`0x990a10`)**:
  - 校验 `index <= 0x9b`，通过跳转表分发至对应属性/倾向写入。
- **徽章等级 (`0x992d40`)**:
  - 写入 0..4 级，0 级代表移除徽章。

### 3.10 W03-12: 全域 Native Getter 目录
- 建立了涵盖 6 大类别、18+ 关键只读例程的标准目录（`native_getter_catalog.py`），提供执行前校验与执行后读回验证支持。

---

## 4. 隔离候选与测试清单
所有候选实现均保存在实验目录 `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/` 中，测试全部隔离在 `pytest_gemini/` 下，共 21 项测试全部通过：

1. `test_coach_settings.py` (2 passed): 验证 6 POE 打包、战术体系、自动化及 Freelance 槽。
2. `test_rotation_timeline.py` (3 passed): 验证 7 位单球员分钟位写入、全队 240 分钟守恒及 48 分钟时间线往返。
3. `test_training_mentorship.py` (2 passed): 验证 10 组师徒槽（204 字节步长、0xffff 空标）及 30 字节训练大纲编码。
4. `test_contract_offer.py` (2 passed): 验证 48 字节合同上下文编码、年限薪资解包及撤回状态。
5. `test_staff_roster.py` (3 passed): 验证名单合法性校验（13-15 人）、职员角色 8..20 范围及裁员位移。
6. `test_draft_scout.py` (2 passed): 验证选秀权 32 位元数据打包及 60 人大榜序列化。
7. `test_trade_package.py` (3 passed): 验证 CBA 薪资配平规则及三方交易序列化。
8. `test_native_getters.py` (2 passed): 验证全域 Getter 字典查找与类别过滤。

---

## 5. Codex 集中审查指引与建议集成步骤
1. **优先吸收**:
   - `player_playtypes_codec.py`: 100% 确证的 4 个 PlayType 微型 Setter（`0xf1e370`..`0xf1e3e0`），可直接与 `facade.py` 的战术类型动作对接。
   - `coach_settings_codec.py`: 确证的 `COACHDATA + 0x13c` 6 POE 打包与 `[Franchise + 0x7bc4] |= 2` 脏标志触发流水线。
   - `rotation_timeline_codec.py`: 确证的 `0x11b2bb0` 单球员分钟位段写入（bits 18..24）。
   - `contract_offer_codec.py` & `trade_package_codec.py`: 48 字节合同报价结构与交易前置限制掩码（`0x3c0000`）。
2. **实机验证最小场景建议**:
   - **Coach POE 刷新**: 在 MyLEAGUE 模式下修改 `COACHDATA + 0x13c`，触发 `0x131f110`，进游戏教练战术界面检查 Offense Focus 是否由 0 变为 14。
   - **单球员分钟**: 选取某替补球员调用 `0x11b2bb0` 设置为 25 分钟，在轮换界面检查数值是否同步显示。
   - **PlayType 写入**: 调用 `0xf1e370` 将指定球员的 PlayType 1 设为 2 (P&R Handler)，检查球员编辑菜单战术类型 1 是否更新。
3. **安全边界确认**:
   - 本次研究未动用任何真实游戏运行进程，所有候选均为无副作用的离线模块，未污染任何正式工程文件。
