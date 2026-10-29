# W02 Consolidated Codex Handoff: Wave-02 连续研发交付总结

**阶段编号**: `GREA-Wave-02`  
**执行模型**: Gemini (REA 连续有界逆向探索与自纠)  
**工程所有者 / 审核人**: Codex (阶段性集中审核与集成)  
**基准分支**: `gemini_rea`  
**生命周期状态**: `candidate_ready_for_independent_review`  
**实机状态**: `NO_GAME_ACCESS` (严格遵循只读与离线纪律，未访问、未注入任何运行中游戏进程)  

---

## 1. 三个工作包状态一览

| 工作包 | 核心课题 | 最终状态 | 离线测试 | 核心成果 / 关键自纠 |
|---|---|---|---|---|
| **W02-A** | GREA-01 证据修正与自纠 | `STATIC_CANDIDATE` | 12 passed (GREA-01) | 澄清 `0x146ec50` 汇编指令取 uint16 `owner_team_index`，撤回指针冲突假象；降级 `0x131f110` 作用域为默认计划刷新；确证 `0x7a7aab` 置位及 35 槽 / 880 字节循环边界 |
| **W02-B** | 18项个人防守原生操作 | `STATIC_CANDIDATE` | 4 passed | 18 项字段位段 100% 对应物理字节（Word 1 占满 32 位，Word 2 占低 11 位）；查明无独立微型 Setter，原版以 12 字节条目整体更新 (`0x14652c0`)；实现并验证 18 字段原子修改与无位泄漏编解码器 |
| **W02-C** | Playbook 68槽原生操作 | `STATIC_CANDIDATE` (`STILL_PARTIAL` for live flush) | 4 passed | 确证 `PLAYBOOKDATA` 360 字节（`0x168`）、`+0x58` 起始 68 槽（`cmp eax, 0x44`）；划分 REGULAR (30)、BENCH (20)、ENDGAME (10)、FAVORITE (8) 四分区；区分共享池与专有书；实现 68 槽操作候选引擎；独立原生 Flush 标记为缺口 |

---

## 2. 核心真实所得与关键结论修正

### 2.1 W02-A: 彻底消解 GREA-01 报告中的数据类型矛盾
- **修正前疑点**：GREA-01 报告中把 `0x146ec50` 简写为 `mov rcx, [rcx+2]; call 0x146eaa0`，引发质疑：若 `GAMEPLAN+0x2` 是 uint16 `owner_team_id`，64位指针读法必将读取未对齐的 8 个字节。
- **物理反汇编事实**：
  ```assembly
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
  `0x146ec59` 读取的是 16 位无符号整数（`owner_team_index`），通过 `0x140f40eb0` 转换为 `TEAM*`，再通过 `0x1409cd2a0` 得到 `CoachData*`，最终调用 `0x146eaa0(pGameplan, pCoach)`。**完全没有类型矛盾**。

### 2.2 W02-A: 降级 `0x131f110` 的提交作用域
- **物理反汇编事实**：
  ```assembly
  0x131f11a: test     byte ptr [rcx + 0x7bc4], 1
  0x131f126: add      rcx, 0x7854
  0x131f149: lea      rcx, [rbx + 0x7854]
  0x131f154: call     0x14146ec80
  ```
  `0x131f110` 内部显式硬编码偏移 `0x7854`（即 Slot 35: Default Gameplan）。它**只负责刷新默认全局 Gameplan 与 Coach 脏位**，并不遍历 35 个对手槽位。对手 Gameplan 生效的依据是 `0x7a7aab: mov word ptr [pGameplan], 1`（置 `IsInUse = 1`），其长期持久化依赖整个 MyLEAGUE 的保存流程。

### 2.3 W02-B: 18 项防守字段全部与原生二进制对齐
- **Word 1 (Matchup+4)**：32 位完全占满，默认值 `0x00280000`（由 `0x1465285: mov dword ptr [rax+4], 0x280000` 写入）：
  - `PressureOnball` (0..2), `PressureOffball` (3..5), `ForceDirection` (6..7), `ScreenDefenseOnBall` (8..10), `ScreenDefenseHedge` (11..13), `OffballScreenDefense` (14..15), `PostDefense` (16..18), `DoubleTeamPerimeter` (19..20, 默认 1), `DoubleTeamPost` (21..23, 默认 1), `ScreenDefenseOnBall5` (24..26), `ScreenDefenseHedge5` (27..29), `SwitchRule` (30..31)。
- **Word 2 (Matchup+8)**：低 11 位有效，掩码 `0x7FF`，由 `0x146527e: and dword ptr [rax+8], 0xfffff800` 证实：
  - `OnballHelp` (0..1), `ScreenHelp` (2..3), `ExtendPressure` (4..5), `TagOnRoll` (6..7), `StayAttached` (8..9), `PreRotate` (10)。
- **Setter 机制**：原版未提供 18 个独立的微型 Setter 函数；原生通过 `0x14652c0` (`GAMEPLAN::InsertOrUpdateMatchup`) 执行 12 字节整块原子复制。

### 2.4 W02-C: Playbook 68 槽物理布局与四大分区确证
- `PLAYBOOKDATA` 总大小为 360 字节（`0x168`），`+0x58` 处为 68 个 uint32 CRC 槽位（由 `0x7aa584: cmp eax, 0x44` 证实）。
- 四大分区：
  - `REGULAR`: 槽 0..29 (30 槽)
  - `BENCH`: 槽 30..49 (20 槽)
  - `ENDGAME`: 槽 50..59 (10 槽)
  - `FAVORITE`: 槽 60..67 (8 槽)
- 球队战术书仅保存 CRC32 槽位引用，修改槽位绝不污染全局共享战术库。

---

## 3. 建议 Codex 集中审核与接收清单 (Codex Action Items)

1. **结构常量采纳**:
   - `GAMEPLAN`: 880 字节，Matchup 在 `+0x64`（23 条目，每条目 12 字节）。
   - `PLAYBOOKDATA`: 360 字节，68 槽从 `+0x58` 开始。
2. **候选代码选择性移植**:
   - `experimental/gemini_rea/W02_B/defense_18_codec.py`: 可直接作为 18 项防守字段的纯位段编解码器并入生产 `src/`。
   - `experimental/gemini_rea/W02_C/playbook_68_codec.py`: 可直接作为 Playbook 68 槽分区管理与槽位校验器并入生产 `src/`。
3. **保留的缺口与后续实机门禁**:
   - 保持对手 Gameplan 与 Playbook 在内存中通过置位/槽位写入生效；
   - 独立的 MyLEAGUE 存档写盘事务待 Codex 在实机 MyLEAGUE 环境中打断点验证。

---

## 4. 交付文件索引与 Git 范围

```
01_os/07_content/_runs/run-20261028-gemini-rea-001/
├── W02_A/
│   ├── HANDOFF.md
│   ├── EVIDENCE_LEDGER.json
│   ├── REPRODUCTION.md
│   ├── ITERATIONS.jsonl
│   └── CODEX_REVIEW.md
├── W02_B/
│   ├── HANDOFF.md
│   ├── EVIDENCE_LEDGER.json
│   ├── REPRODUCTION.md
│   ├── ITERATIONS.jsonl
│   └── CODEX_REVIEW.md
├── W02_C/
│   ├── HANDOFF.md
│   ├── EVIDENCE_LEDGER.json
│   ├── REPRODUCTION.md
│   ├── ITERATIONS.jsonl
│   └── CODEX_REVIEW.md
└── W02_CONSOLIDATED_CODEX_HANDOFF.md

08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/
├── GREA_01/ (保留上一轮历史成果，12 tests)
├── W02_B/   (18项个人防守编解码器及测试，4 tests)
└── W02_C/   (Playbook 68槽编解码器及测试，4 tests)
```
- 全部离线测试总计 20 项全部通过（exit code 0）。
- 本轮严格未修改任何正式生产文件（无 master 变更、无正式 registry/facade 变更、未触碰 Codex 工作目录）。
