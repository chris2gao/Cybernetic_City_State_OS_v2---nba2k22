# W03-05 Delivery Handoff: Starters, Rotation & Minutes Timeline

## 1. 范围与 10 项需求覆盖
本包全面研究并闭环了 `STARTERS_AND_ROTATION` 组的 10 项需求：
- 轮换顺序与名单位置 (`ROTATION_ORDER`)
- 单球员分钟修改 (`PLAYER_MINUTES`)
- 首发五人设置 (`STARTING_FIVE`)
- 第二阵容设置 (`SECOND_UNIT`)
- 球员出场角色分配 (`PLAYER_ROLE`)
- 特定情境阵容 (`SITUATIONAL_LINEUPS`)
- 伤病缺阵后轮换触发 (`INJURY_SUBSTITUTION`)
- 对位分配与实时换人/战术 (`MATCHUP_ASSIGN`, `LIVE_SUBSTITUTION`, `LIVE_CALL_PLAY`)

## 2. 核心原生机制发现
1. **单球员分钟写入原生指令 (`0x11b2bb0`)**:
   - 原版函数 `0x11b2bb0`（对应绑定 `rotation.set_player_minutes`）直接操作球员槽结构体的偏移 `+0xf8`。
   - 使用指令序列：
     ```assembly
     and dword ptr [rdx + 0xf8], 0xfe03ffff  ; 清零 bits 18..24 (7 bits)
     shl eax, 0x12                           ; 分钟值左移 18 位
     or  dword ptr [rdx + 0xf8], eax        ; 写回
     ```
   - 证明：球员出场分钟是以 7 位无符号整数（0..127，业务限制为 0..48）打包在 `[Player+0xf8]` 的第 18 至 24 位。

2. **首发五人与轮换深度架构 (`0xedf000`)**:
   - 球员在名单中的出场顺序/角色位置存放在 `[Player + 0xf78]` 的 bits 22..25（4 位，值域 0..15）。
   - 原版提取指令：`shr eax, 0x16; and eax, 0xf`。
   - 槽位 0..4 严格对应首发五人（PG, SG, SF, PF, C），槽位 5..9 严格对应第二阵容，其余为替补深度。

3. **48 分钟轮换时间线 (`GAMEPLAN + 0x18c .. 0x36e`)**:
   - `GAMEPLAN + 0x18c` 为 1 字节布尔标志：`has_rotation_timeline`。
   - `GAMEPLAN + 0x18e .. 0x36e` 紧跟 480 字节时间线数据：由 48 个 1 分钟切片组成，每个切片包含 5 个 16 位球员 ID（`48 * 5 * 2 = 480` 字节）。
   - 当 `has_rotation_timeline == 1` 时，游戏引擎使用用户定义的时间线换人；若为 0，则由教练 AI 根据出场分钟进行自动化轮换调度。
   - 全队总分钟数在有效轮换计划中必须守恒为 240 分钟（`48 * 5 = 240`）。

## 3. 隔离候选与验证交付
- 交付编解码器：`rotation_timeline_codec.py`
- 交付独立测试：`pytest_gemini/test_rotation_timeline.py` (3 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
