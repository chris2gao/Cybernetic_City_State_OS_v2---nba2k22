# Codex Review Points: W02-A GREA-01 Evidence Repair

## 1. 核心审查重点 (Top Audit Points)

1. **`0x146ec50` 指令核验与类型澄清**:
   - 之前 GREA-01 报告简写 `mov rcx, [rcx+2]` 引发了 `GAMEPLAN+0x2` 到底是 uint16 还是 64位指针的矛盾。
   - 本轮原始 Capstone 反汇编证实其实际指令为 `0x146ec59: movzx ecx, word ptr [rcx + 2]`，取 uint16 `owner_team_index`，随后通过 `0x140f40eb0` 和 `0x1409cd2a0` 获取 Coach 指针。
   - 审查结论：`GAMEPLAN+0x2` 确为 uint16，不存在指针/整数类型冲突。

2. **`0x131f110` 作用域降级**:
   - 反汇编证实 `0x131f110` 内部显式硬编码 `lea rcx, [rbx + 0x7854]`（默认 Gameplan，Slot 35），并无对对手槽位（`+4` 至 `+0x7850`）的遍历或提交逻辑。
   - 审查结论：`0x131f110` 仅提交球队默认比赛计划与教练脏状态，不得宣称其能刷写特定对手 Gameplan。对手计划生效依赖 `0x7a7aab` 置 `IsInUse = 1`。

3. **35 槽位与 880 字节物理验证**:
   - 函数 `0x12f6540` 循环硬编码 `cmp ebx, 0x23` (35) 与 `imul rcx, rax, 0x370` (880)，证实结构数组规格。
