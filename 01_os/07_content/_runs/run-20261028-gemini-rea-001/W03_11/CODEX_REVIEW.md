# W03-11 Codex Review Guide

## 1. 重点审核内容
1. **战术类型的执行影响**:
   - `[Player + 0x168]` 的 4 个 PlayTypes 决定了进攻战术调用引擎在执行战术时，哪些战术可以分配给该球员。
   - 保证 4 个 PlayTypes 均为合法战术枚举（0..12），避免填入越界值导致战术引擎匹配空指针。
2. **属性与倾向的范围限制**:
   - 属性值一般在 [25, 99] 之间，倾向在 [0, 100] 之间。`0x990a10` 接收 0..99 的数值。
3. **集成建议**:
   - 将 `player_playtypes_codec.py` 与已有绑定 `player.set_playtype_1..4` (0xf1e370..0xf1e3d0) 及 `player.set_stat_ui` (0x990a10) 直接对接。
