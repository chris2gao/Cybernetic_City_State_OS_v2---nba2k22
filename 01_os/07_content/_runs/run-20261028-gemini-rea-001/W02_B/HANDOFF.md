# W02-B: 18项个人防守原生操作交接报告

## 1. 任务基本信息
- **工作包**: `W02-B` (GREA-02-MATCHUP-DEFENSE)
- **状态**: `STATIC_CANDIDATE`
- **目标二进制**: `NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
- **Git 分支**: `gemini_rea`

## 2. 核心成果

### 2.1 18 项个人防守字段分类总表
全部 18 项个人防守字段均在原生二进制汇编中定位到了具体位段和取值域：
- **Word 1**（Matchup+4，32位，默认 `0x00280000`）：
  1. `PressureOnball` (bits 0..2, 0..4) - `CONFIRMED_FROM_BYTES`
  2. `PressureOffball` (bits 3..5, 0..5) - `CONFIRMED_FROM_BYTES`
  3. `ForceDirection` (bits 6..7, 0..2) - `CONFIRMED_FROM_BYTES`
  4. `ScreenDefenseOnBall` (bits 8..10, 0..4) - `CONFIRMED_FROM_BYTES`
  5. `ScreenDefenseHedge` (bits 11..13, 0..5) - `CONFIRMED_FROM_BYTES`
  6. `OffballScreenDefense` (bits 14..15, 0..3) - `CONFIRMED_FROM_BYTES`
  7. `PostDefense` (bits 16..18, 0..4) - `CONFIRMED_FROM_BYTES`
  8. `DoubleTeamPerimeter` (bits 19..20, 0..3, 默认 1) - `CONFIRMED_FROM_BYTES`
  9. `DoubleTeamPost` (bits 21..23, 0..4, 默认 1) - `CONFIRMED_FROM_BYTES`
  10. `ScreenDefenseOnBall5` (bits 24..26, 0..4) - `CONFIRMED_FROM_BYTES`
  11. `ScreenDefenseHedge5` (bits 27..29, 0..5) - `CONFIRMED_FROM_BYTES`
  12. `SwitchRule` (bits 30..31, 0..3) - `CONFIRMED_FROM_BYTES`
- **Word 2**（Matchup+8，低 11 位，掩码 `0x7FF`，默认 `0x00000000`）：
  13. `OnballHelp` (bits 0..1, 0..2) - `CONFIRMED_FROM_BYTES`
  14. `ScreenHelp` (bits 2..3, 0..2) - `CONFIRMED_FROM_BYTES`
  15. `ExtendPressure` (bits 4..5, 0..2) - `CONFIRMED_FROM_BYTES`
  16. `TagOnRoll` (bits 6..7, 0..2) - `CONFIRMED_FROM_BYTES`
  17. `StayAttached` (bits 8..9, 0..2) - `CONFIRMED_FROM_BYTES`
  18. `PreRotate` (bit 10, 布尔值 0..1) - `CONFIRMED_FROM_BYTES`

### 2.2 Setter 原生实现形态
- 独立单字段微型 Setter：`NOT_FOUND_IN_BOUNDED_SCOPE`（原版二进制未逐字段实现微型 setter）。
- 块更新原生函数：`0x14652c0` (`GAMEPLAN::InsertOrUpdateMatchup`) 接收 12 字节条目指针并执行插入/替换。
- 候选实现：在 `experimental/gemini_rea/W02_B/defense_18_codec.py` 实现了 18 字段原子修改与 8 字节设置块编解码，离线测试 4 项全部通过。

### 2.3 边界声明
因特定对手 Gameplan 整体生命周期尚未在游戏中进行 live 写盘验证，本轮严格遵循纪律：**不做全部个人防守可直接在运行中游戏写入的虚假宣称**。
