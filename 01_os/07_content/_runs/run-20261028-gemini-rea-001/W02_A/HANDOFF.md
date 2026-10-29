# W02-A: GREA-01 证据修正与自纠交接报告

## 1. 任务基本信息
- **工作包**: `W02-A` (GREA-01-EVIDENCE-REPAIR)
- **状态**: `STATIC_CANDIDATE`
- **目标二进制**: `NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
- **Git 分支**: `gemini_rea`

## 2. 核心修正与自纠总结

### 2.1 撤回与澄清：`GAMEPLAN+0x2` 与 `0x146ec50` 数据类型
- **原陈述**: GREA-01 报告文本中描述 `0x146ec50` 为 `mov rcx, [rcx+2]; call 0x146eaa0; ret`，引起审查质疑：若 `+2` 是 uint16 `owner_team_id`，怎么可能是 64 位 Coach 指针？
- **原始 PE 字节核验**:
  在 `0x146ec50` 真实指令为：
  ```assembly
  0x146ec50: push     rbx
  0x146ec52: sub      rsp, 0x20
  0x146ec56: mov      rbx, rcx
  0x146ec59: movzx    ecx, word ptr [rcx + 2]
  0x146ec5d: call     0x140f40eb0
  0x146ec62: xor      edx, edx
  0x146ec64: mov      rcx, rax
  0x146ec67: call     0x1409cd2a0
  0x146ec6c: mov      rdx, rax
  0x146ec6f: mov      rcx, rbx
  0x146ec72: add      rsp, 0x20
  0x146ec76: pop      rbx
  0x146ec77: jmp      0x14146eaa0
  ```
- **结论**: `GAMEPLAN+0x2` **确实是 uint16 `owner_team_index`**。`0x146ec50` 读取该 16 位整数，通过 `0x140f40eb0` 转换为 `TEAM*`，再通过 `0x1409cd2a0` 取得 `CoachData*`，最终将 `pGameplan` (rcx) 与 `pCoach` (rdx) 传递给 `0x146eaa0`。不存在数据类型冲突，前述简写已撤回并更新为精确反汇编。

### 2.2 降级：`0x131f110` 提交作用域
- **原陈述**: 认为 `0x131f110` 是通用 Gameplan 提交函数，可将对手计划刷写存盘。
- **原始 PE 字节核验**:
  在 `0x131f110` 真实指令为：
  ```assembly
  0x131f11a: test     byte ptr [rcx + 0x7bc4], 1
  0x131f126: add      rcx, 0x7854
  0x131f12d: call     0x1414f7ec0
  0x131f149: lea      rcx, [rbx + 0x7854]
  0x131f154: call     0x14146ec80
  0x131f159: and      dword ptr [rbx + 0x7bc4], 0xfffffffe
  ```
- **结论**: `0x131f110` **仅用于提交/刷新默认 Gameplan（Slot 35，偏移 `+0x7854`）**及 Coach 脏状态。它完全不处理 35 个对手 Gameplan 槽位！
- **降级处理**: 明确撤回“`0x131f110` 提交特定对手 Gameplan”的结论。特定对手计划在内存中生效的真实凭据是 `0x7a7aab: mov word ptr [rbx], 1`（置 `IsInUse = 1`），其长期存盘依赖 MyLEAGUE 整体赛季存档序列化，而非 `0x131f110` 立即写盘。

### 2.3 物理证实：35 槽位与 880 字节
- `0x12f6540` 内部循环 `cmp ebx, 0x23`（35 槽）及 `imul rcx, rax, 0x370`（880 字节），证实管理器槽位容量与跨度。
- `0xfe12f0` 内部指令 `movzx ecx, word ptr [rcx + 4]` 证实 `GAMEPLAN+0x4` 为 uint16 `opponent_team_index`。
- `0x146e780` 内部指令 `lea rax, [rsi + 6]; cmp rcx, 0x17; add rax, 4` 证实阵容槽位为 23 项、每项 4 字节。

## 3. 交付状态与停止判定
W02-A 完成了全部 4 轮迭代，消除了 GREA-01 中的过度表述与类型疑惑，成果已记录入 `EVIDENCE_LEDGER.json` 与 `ITERATIONS.jsonl`。
