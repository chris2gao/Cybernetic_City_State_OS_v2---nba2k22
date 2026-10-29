# W03-05 Codex Review Guide

## 1. 重点审核内容
1. **240 分钟守恒约束**:
   - `0x11b2bb0` 仅负责修改单个球员的 7 位分钟数，底层不校验全队是否满 240 分钟。
   - 业务包装层（如 GM Engine 或 Facade）在向 Native 批量写入前，必须运行 `validate_minutes()` 确保全队总分钟守恒，否则游戏在模拟或比赛开始时可能产生自动归一化或重分配。
2. **时间线模式与常规分钟模式的互斥**:
   - `has_rotation_timeline` (0x18c) 为 1 时优先使用 48 分钟矩阵；为 0 时使用教练 AI 动态轮换。
   - 建议在未指定精确时间线时保持 `has_rotation_timeline = 0`，仅通过设置单球员分钟来驱动轮换。
3. **集成建议**:
   - 将 `rotation_timeline_codec.py` 的 `encode_player_minutes_field` 接入 `rotation.set_player_minutes` (RVA `0x11b2bb0`)。
