# 教练设置：模拟侧重 (Simulated Gameplan Focus) REA Native 机制与规范指南

> **文档标识**: `SPEC-REA-NATIVE-SIMULATED-FOCUS-V1`  
> **适用目标**: PC NBA2K22 (Steam x64) 离线 MyLEAGUE | 结构体: `GAMEPLAN` (`stride 880`)  
> **所属模块**: `research/rea_native_control`  
> **关联调用**: `coach.apply_gameplan` / `GAMEPLAN` 原生基址定位与纯差分受控注入  

---

## 1. 机制背景与 UI 对应关系

在 NBA 2K22 游戏中，主教练设置界面中存在专门的 **“模拟侧重” (Simulated Focus / Gameplan Focus)** 全局配置页面。该页面由以下两大部分构成：
1. **三大终结选择 (Three Scoring Options)**：决定当战术跑出多个机会或战术失效时，AI 决策与传球分配的第一、第二、第三终结优先级。
2. **六大攻防重点 (Six Points of Emphasis / POE)**：决定全队进攻重点、进攻节奏、进攻篮板策略、防守重点、防守身体对抗强度以及防守篮板与转换策略。

在早期 REA 原生发现阶段（如 `runtime/coach_poe.js`），前三项 `0x178 + i * 2` 被误填为占位哨兵值 `65535`。现经反编译与内存审计确认：**`0x178` ~ `0x183` 构成了连续 12 字节的“模拟侧重”原生专属数据块**，必须严格按照真实球员 ID 与纯数字枚举进行受控写入，严禁填充占位假数据。

---

## 2. 连续 12 字节内存布局规范

目标结构体：**`GAMEPLAN`**（位于主教练关联的比赛计划块中，`stride 880` 字节）。

| 字段名称 (Field) | 相对偏移 (Offset) | 尺寸与类型 | 合法取值范围 | 说明与业务含义 |
| :--- | :---: | :---: | :---: | :--- |
| **`scoring_option_1`** | `0x178` (376) | 2 bytes (`uint16`) | 合法 `PLAYER_ID` | **第一进攻选择**：战术大核，主要单打/挡拆终结者 |
| **`scoring_option_2`** | `0x17A` (378) | 2 bytes (`uint16`) | 合法 `PLAYER_ID` | **第二进攻选择**：副攻手，战术第二持球/投射终结点 |
| **`scoring_option_3`** | `0x17C` (380) | 2 bytes (`uint16`) | 合法 `PLAYER_ID` | **第三进攻选择**：第三终结点，弱侧空切/定点射手 |
| **`poe_offense`** | `0x17E` (382) | 1 byte (`uint8`) | `1..6` | **进攻重点/进攻侧重**：<br>`1`=冲击篮筐 (Get to Basket)<br>`2`=为射手跑位 (Get Shooters Open)<br>`3`=打低位内线 (Feed the Post)<br>`4`=挡拆进攻 (Pick & Roll Offense)<br>`5`=中立进攻 (Neutral)<br>`6`=围绕得分手运转 (Run Offense Through Scorer) |
| **`poe_offense_tempo`** | `0x17F` (383) | 1 byte (`uint8`) | `7..9` | **进攻节奏**：<br>`7`=耐心阵地战 (Patient Offense)<br>`8`=中立节奏 (Neutral)<br>`9`=尽早出手反击 (Shoot at Will / Fast Pace) |
| **`poe_offense_rebound`** | `0x180` (384) | 1 byte (`uint8`) | `10..12` | **进攻篮板策略**：<br>`10`=全力拼抢前场篮板 (Crash Offensive Boards)<br>`11`=中立<br>`12`=极速退防限制快攻 (Limit Transition) |
| **`poe_defense`** | `0x181` (385) | 1 byte (`uint8`) | `13..15` | **防守重点/防守侧重**：<br>`13`=保护禁区油漆区 (Protect the Paint)<br>`14`=中立防守<br>`15`=贴防限制外线三分 (Limit Perimeter Shots) |
| **`poe_defense_physicality`**| `0x182` (386) | 1 byte (`uint8`) | `16..18` | **防守对抗策略**：<br>`16`=保守防守避免犯规 (Play Conservative)<br>`17`=中立身体对抗<br>`18`=强硬身体对抗 (Play Physical) |
| **`poe_defense_rebound`** | `0x183` (387) | 1 byte (`uint8`) | `19..21` | **防守篮板策略**：<br>`19`=全员保护防守篮板 (Crash Defensive Boards)<br>`20`=中立防守篮板<br>`21`=抓篮板极速反击 (Run in Transition) |

---

## 3. REA 原生方法执行准则

1. **禁用裸内存写入 (No Direct Memory Poking)**：
   - 严禁通过外部调试器直接暴力覆盖未经验证的地址空间；
   - 必须通过 REA 原生 Native 调度器定位当前球队的 `GAMEPLAN` 基址。
2. **纯差分与零占位铁律 (Sparse Delta & No Placeholders)**：
   - 严禁在执行包中使用 `65535`、`0`、`null` 或随机伪造数值作为占位符；
   - 仅输出需要修改的项；三名得分选择球员必须是该队大名单真实存在的球员 UID。
3. **安全边界保障**：
   - 写入区域严格锁死在 `[0x178, 0x183]`（共 12 字节），绝不得向前（`0x176`）或向后（`0x184` 及以后）越界破坏相邻的教练体系与战术本指针。
