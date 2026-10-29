# GREA-01: 对手Gameplan修改与原生提交调用链交接报告

## 1. 任务基本信息
- **任务编号**: `GREA-01`
- **执行模型**: Gemini (REA Native机制探索与隔离候选开发)
- **工程所有者 / 审核模型**: Codex
- **基准提交**: `39086984adfa554d36315382d41bc2e5d2e54c39` (Codex Draft PR #19)
- **工作分支**: `gemini_rea`
- **生命周期状态**: `candidate_ready_for_independent_review`
- **隔离实现目录**: `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/`

---

## 2. 核心逆向发现总结

### 2.1 对手Gameplan的宿主与所属关系
经过对 `NBA2K22.exe` 的反汇编逆向与调用者追踪，彻底明确了对手Gameplan在原生内存中的宿主关系：
1. **获取入口**: 调用 `GetTeamGameplanManager` (RVA `0xfda730`)：
   - 签名: `FRANCHISE_GAMEPLAN_MANAGER* (TEAM* pTeam, int flag=0)`
   - 内部逻辑: 通过 `0xedefe0(pTeam)` 解析出当前球队的 `team_index` (0..29)，读取全局 Franchise 实例指针（`0x3c23170`），返回该球队专属的管理器指针：
     $$\text{Manager} = \text{Franchise} + 0x19cfd0 + \text{team\_index} \times 0x13e70$$
2. **`FRANCHISE_GAMEPLAN_MANAGER` 内存布局** (总大小 `0x13e70` = 81,520 字节)：
   - `+0x0`: uint16 `team_record_index`
   - `+0x2`: uint16 `team_id`
   - `+0x4`: **对手Gameplan连续数组**，共 35 个槽位（覆盖联盟全部可能对手），每个槽位大小为固定 880 字节（`0x370`）。
     - Slot 0..34 偏移范围: `0x4` 至 `0x7854`。
   - `+0x7854`: **默认Gameplan (Slot 35)**，大小同样为 880 字节，用于对阵未单独指定对手时的全局基准计划。
   - `+0x7bc4`: uint32 `dirty_flags`（事务标志位：bit 0 为 Gameplan 待刷写，bit 1 为 Coach 待同步）。

### 2.2 880 字节 `GAMEPLAN` 对象结构完整解码
原版 880 (`0x370`) 字节的布局经反汇编逐段确认如下：
- `+0x0`: uint16 `IsInUse`（0=默认未单独启用，1=已定制且在比赛中生效；在原版 UI 提交函数 `0x7a7840` 中由汇编指令 `0x7a7aab: mov word ptr [rbx], 1` 置 1）。
- `+0x2`: uint16 `owner_team_id`（拥有本计划的球队 ID）。
- `+0x4`: uint16 `opponent_team_id`（目标对手球队 ID；若为 `0xFFFF` 则代表默认计划）。
- `+0x6`..`+0x62`: 本队阵容 23 个球员槽位（每槽 4 字节：uint16 `player_uid`，uint16 默认时间 `0x00FF`），共 92 字节。
- `+0x62`..`+0x64`: uint16 对齐填充（2 字节）。
- `+0x64`..`+0x178`: **针对对手球员的 23 槽位防守 Matchup 数组**（每槽固定 12 字节，与前期实机证据 `DEV_20261017_07_OVERALL_DEFENSE_EVIDENCE.json` 的 `start=100, stride=12, count=23` 逐字节完美匹配）：
  - `+0`: uint16 `opponent_player_uid`（对手球员 UID，`0xFFFF` 为空槽位）。
  - `+2`: uint16 `assigned_defender_uid`（我方指定主防球员 UID，`0xFFFF` 为自动对位）。
  - `+4`: uint32 `defensive_settings_word1`（防守设置位段字 1）：
    - **`bits 0..2` (mask `0x7`): `PressureOnball`**（持球施压：0=AUTO, 1=GAP, 2=MODERATE, 3=TIGHT, 4=SMOTHER）。
    - `bits 3..5` (mask `0x38`): `PressureOffball`（无球施压：0=AUTO, 1=MODERATE, 2=TIGHT, 3=DENY）。
    - `bits 6..7` (mask `0xC0`): `ForceDirection`（逼迫方向：0=AUTO, 1=NO_PREF, 2=BASELINE, 3=MIDDLE）。
    - `bits 8..10` (mask `0x700`): `ScreenDefenseOnBall`（掩护防守：0=AUTO, 1=OVER, 2=UNDER, 3=SWITCH）。
    - `bits 11..13` (mask `0x3800`): `ScreenDefenseHedge`（延误防守：0=AUTO, 1=NO_HEDGE, 2=SOFT, 3=HARD, 4=CATCH）。
    - `bits 14..15` (mask `0xC000`): `OffballScreenDefense`。
    - `bits 16..18` (mask `0x70000`): `PostDefense`。
    - `bits 19..20` (mask `0x180000`): `DoubleTeamPerimeter`。
    - `bits 21..23` (mask `0xE00000`): `DoubleTeamPost`。
    - `bits 24..26` (mask `0x7000000`): `ScreenDefenseOnBall5`。
    - `bits 27..29` (mask `0x38000000`): `ScreenDefenseHedge5`。
    - `bits 30..31` (mask `0xC0000000`): `SwitchRule`。
  - `+8`: uint32 `defensive_settings_word2`（防守设置位段字 2）：
    - `bits 0..1`: `OnballHelp`。
    - `bits 2..3`: `ScreenHelp`。
    - `bits 4..5`: `ExtendPressure`。
    - `bits 6..7`: `TagOnRoll`。
    - `bits 8..9`: `StayAttached`。
    - `bit 10`: `PreRotate`。
- `+0x178`..`+0x17C`: 3 个关联指针/ID 槽。
- `+0x17E`..`+0x183`: 6 个 POE 设置字节。
- `+0x184`..`+0x18B`: 战术与轮换倾向参数（节奏、战术使用率、联防倾向、替补深度等）。
- `+0x18C`: uint8 `has_rotation_timeline`。
- `+0x18E`..`+0x36E`: 48 分钟轮换时间线（48 × 10 字节）。

---

## 3. 多对手隔离不变性

在实际比赛中，教练必须能够独立针对不同对手做不同准备。例如：
- 步行者对阵 76ers：对恩比德设置 `DoubleTeamPost = ON_CATCH`，持球施压 `SMOTHER`；
- 步行者对阵 雄鹿：对字母哥设置持球施压 `GAP`，放投不放突；
- 步行者对阵 其他未单独定制球队：回退使用默认 Gameplan（Slot 35）。

**隔离机制证明**:
1. 每个对手的 Gameplan 在 `FRANCHISE_GAMEPLAN_MANAGER` 中占用独立的 `slot_index * 880` 连续偏移内存块。
2. 查找逻辑通过遍历 35 个槽位并匹配 `slot->opponent_team_id`，定位到唯一对应的 880 字节指针。
3. 对该指针所指向的 880 字节区域的写入，物理上完全限制在该 880 字节内，绝不会越界触及其他槽位。
4. 单元测试 `test_multi_opponent_data_isolation` 完整证实了这一不变性：对 PHI、MIL、BKN 的并发设置在序列化/反序列化后完全独立保持，且默认计划保持原样。

---

## 4. 原生提交事务调用链

原版 UI 界面（Gameplan UI 菜单）在玩家修改完成点击退出/保存时，执行的核心调用链如下：

```
[UI 界面触发提交]
       │
       ▼
1. 0xfda730 GetTeamGameplanManager(pTeam, 0)
       │ -> 返回 FRANCHISE_GAMEPLAN_MANAGER* (offset 0x19cfd0)
       ▼
2. 0x1244230 FRANCHISE_GAMEPLAN_MANAGER::EnsureOpponentGameplan(manager, pOpponentTeam)
       │ -> 遍历槽位；若无则分配新槽位并调用 0x146c260 GAMEPLAN::Init
       │ -> 返回 GAMEPLAN* (880 字节对象)
       ▼
3. 0x14651c0 GAMEPLAN::InsertOrFindOpponentMatchup(pGameplan, pOpponentPlayer, pDefender)
       │ -> 定位 +0x64 处的 12 字节 Matchup 槽位
       ▼
4. [业务修改字段]
       │ -> 写入 Matchup+4 (defensive_settings_word1)，修改 PressureOnball 对应位 (bits 0..2)
       ▼
5. 0x146ec50 GAMEPLAN::ApplyToCoach(pGameplan)
       │ -> 调用 0x146eaa0 同步当前 Gameplan 设置至 Coach 运行时结构
       ▼
6. [标记启用]
       │ -> 0x7a7aab: mov word ptr [pGameplan+0x0], 1 (设置 IsInUse = 1)
       ▼
7. 0x131f110 FRANCHISE_GAMEPLAN_MANAGER::CommitPendingFlags(manager)
       │ -> 检查 manager+0x7bc4 (dirty_flags |= 0x3)
       │ -> 执行原版状态同步并清除待处理位
```

---

## 5. 隔离候选实现与测试交付物

所有代码与测试均已安全隔离在：
`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/`

- **`gameplan_opponent.py`**:
  - `PressureOnball`、`PressureOffball` 等相关枚举；
  - `MatchupDefensiveSettings` 完整位段编解码器；
  - `OpponentMatchupEntry`（12 字节条目）；
  - `OpponentGameplan`（880 字节对象打包/解包/对齐）；
  - `FranchiseGameplanManager`（81,520 字节管理器状态机与持久化）。
- **`native_call_chain.py`**:
  - 8 项核心原生函数的元数据规范定义（RVA、ABI、签名、反汇编说明、成熟度分级）；
  - `OpponentGameplanTransactionHarness` 仿真执行线索。
- **`tests/test_grea_01_gameplan_opponent.py`**:
  - 12 项严谨的离线 pytest 单元测试，全部通过。

---

## 6. 未知项与局限性 (Unknowns & Limitations)

1. **实机内存注入尚未执行**：
   - 本轮根据 OS 启动纪律与任务安全规范，采取了纯静态逆向分析 + 离线编解码仿真。
   - 所有函数 RVA 均已反汇编验证，但尚未在 live 2K22 进程中挂载 Hook 或由注入器实际调用。成熟度定级为 `STATIC_DISASSEMBLED`。
2. **Coach 结构同步深入细节 (0x146eaa0)**：
   - 已知 `0x146ec50` tail-call `0x146eaa0`，其实参包含了 coach 指针。但在非比赛日（例如单纯在 MyLEAGUE 菜单中翻阅日历）该同步是否会直接写回只读 Save 存档，需要 Codex 在实机调试器中打断点验证。
3. **槽位耗尽策略**：
   - 管理器目前硬编码支持 35 个对手槽位。NBA 常规赛对手共 29 支球队，35 个槽位完全足够。但如果超出 35 个，原生代码会抛出异常或覆盖末尾槽位。
