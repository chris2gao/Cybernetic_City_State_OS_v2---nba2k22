# W03-04 Codex Review Guide

## 1. 重点审核内容
1. **CoachData 与 Gameplan 的关系**:
   - 游戏原生设计中，`COACHDATA` 是运行期战术执行上下文，而 `GAMEPLAN` 是持久化与 UI 编辑缓冲区。
   - 修改教练设置最安全、最符合原版规范的方式是：修改 `GAMEPLAN` 尾部对应字节，随后设置 `[FranchiseContext + 0x7bc4] |= 2`，由原版管道触发 `0x146eaa0` 自动刷新 `COACHDATA`。
2. **Freelance 槽指针生命周期**:
   - `0x140f3f580` 必须在当前游戏战术数据包已载入的上下文中有效。离线或非比赛态若直接解析指针需确保战术表有效。
3. **集成建议**:
   - Codex 可直接将 `coach_settings_codec.py` 纳入 `research/rea_native_control/codecs/` 或与 `facade.py` 的 `coach.apply_gameplan` 对接。
