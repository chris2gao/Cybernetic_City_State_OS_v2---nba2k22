# W03-04 Delivery Handoff: Coach Global Settings & 4 Freelance Slots

## 1. 范围与 20 项需求覆盖
本包全面研究并闭环了 `FREELANCE_AND_COACH_SETTINGS` 组的 20 项需求：
- 6 项 POE 重点策略 (`POE_O1`, `POE_O2`, `POE_O3`, `POE_D1`, `POE_D2`, `POE_D3`)
- 4 项战术滑块 (`RUN_PLAY`, `ZONE_USAGE`, `BENCH_DEPTH`, `BENCH_USE`)
- 体系与教练偏好 (`PREFERRED_SYSTEM`, `ACTIVE_SYSTEM`, `HELP_DEFENSE`, `TEMPO`)
- 自动化与 ACE (`ACE_MODE`, `COACH_AUTOMATION`)
- 4 项 Freelance 槽位 (`FREELANCE_1`, `FREELANCE_2`, `FREELANCE_3`, `FREELANCE_4`)

## 2. 核心原生机制发现
1. **统一投影机制 (`0x146eaa0`)**:
   - 游戏并不通过单个 Setter 独立修改教练数据，而是将 880 字节 GAMEPLAN 缓冲区的尾部（偏移 `0x178`..`0x18b`）一次性解包并应用到当前教练的 `COACHDATA` 结构体中（位于 `TEAM + 0xce8`）。
   - **6 项 POE 压缩位段 (`COACHDATA + 0x13c`)**:
     - 6 个 POE 字段各占 5 位（值域 0..31），紧密打包在 32 位整型中：
       - Bits 0..4: `poe_offense_1` (来自 `GAMEPLAN + 0x181`)
       - Bits 5..9: `poe_offense_2` (来自 `GAMEPLAN + 0x182`)
       - Bits 10..14: `poe_offense_3` (来自 `GAMEPLAN + 0x183`)
       - Bits 15..19: `poe_defense_1` (来自 `GAMEPLAN + 0x17e`)
       - Bits 20..24: `poe_defense_2` (来自 `GAMEPLAN + 0x17f`)
       - Bits 25..29: `poe_defense_3` (来自 `GAMEPLAN + 0x180`)
   - **战术体系 (`COACHDATA + 0x148`)**:
     - `GAMEPLAN + 0x184` 左移 17 位写入 `COACHDATA + 0x148` bits 17..24。
   - **自动化设置 (`COACHDATA + 0xfc`)**:
     - `GAMEPLAN + 0x18b` 左移 25 位写入 `COACHDATA + 0xfc` bits 25..30。
   - **独立滑块字节**:
     - RunPlay: `COACHDATA + 0xe0`
     - ZoneUsage: `COACHDATA + 0xe2`
     - BenchDepth: `COACHDATA + 0xde`
     - BenchUtil: `COACHDATA + 0x138`
     - ACE Mode: `COACHDATA + 0x109`

2. **Freelance 槽解析机制 (`0x146ec10`..`0x146ec33`)**:
   - `GAMEPLAN + 0x178` 开始为 uint16 的战术 ID 槽。
   - 原版通过循环读取战术 ID，若不为 `0xffff`，调用 `0x140f3f580` (`Play_ResolveById`) 获得 64 位 `Play*` 原生指针，并存入 `COACHDATA + 0x120`（槽 1）、`+0x128`（槽 2）、`+0x130`（槽 3）。若未指定，置 NULL（`0`）。
   - 第 4 个 Freelance 槽位作为体系预设默认 Freelance。

3. **刷新与提交脏标志 (`0x131f110` / `0x131f1b0`)**:
   - 球队 Franchise 上下文（偏移 `+0x7bc4`）的 Bit 1 为“教练设置脏标志”。
   - 当 Bit 1 为 1 时，调度引擎调用 `0x14146eaa0` 重新将 `GAMEPLAN + 0x7854` 投影到 `COACHDATA`，并清零 Bit 1。

## 3. 隔离候选与验证交付
- 交付编解码器：`coach_settings_codec.py`
- 交付独立测试：`pytest_gemini/test_coach_settings.py` (2 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
