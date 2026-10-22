# NBA 2K22 内存热修改与外部决策注入机制规范 (Modification & Injection Mechanism)

本文档详尽说明了 Antigravity 外部 GM 引擎如何安全、高效、零崩溃地将决策数据、属性微调、球星专属动作以及交易方案**逆向写回**至正在运行的 `NBA2K22.exe` 进程中。

---

## 一、核心安全守则与零崩溃协议 (Zero-Crash Protocol)

1. **写前内存属性校验：**
   * 写入任意地址前，必须先调用 `VirtualQueryEx` 确认该内存页具有 `PAGE_READWRITE`、`PAGE_EXECUTE_READWRITE` 或可写权限；如遇写保护，需通过 `VirtualProtectEx` 临时提权，写入完成后立即还原。
2. **严防溢出与越界：**
   * UTF-16LE 字符串写入必须以双零字节 `\x00\x00` 截断，严格限制在分配的缓冲区内（球员姓名不超过 40 字节）；
   * 能力值原生字段仅占 1 字节（`uint8`），写入前必须经过 `min(255, max(0, val))` 边界钳制，禁止写入非法值。
3. **写入时机考量：**
   * 推荐在**主界面、球队管理页、球员详情页、或者比赛暂停中**进行写回，严禁在比赛加载动画（Loading Screen）或保存存档磁盘写入瞬间并发改写。

---

## 二、2K22 内存“多副本缓存”（Multi-Copy Cache）陷阱与终极解决方案

在逆向修改 2K22 时，最常遇到的问题是：“**明明修改了内存中的数值，为什么切个菜单又变回去了？**”

### 1. 产生原因
2K22 采用多级数据缓存架构。在游戏运行期间，一个活跃球员在堆内存中最多存在 **10 ~ 13 个镜像副本**（包括：大名单数据库主副本、UI 渲染展示缓存、实时体力/比赛物理计算对象、战术统计对象、球员卡片缓存等）。如果仅用 CE 或脚本修改了其中某一个非主副本，当界面切换或触发自动计算时，引擎就会用主副本数据重新覆盖掉临时修改。

### 2. 终极解决方案（双轨同步法）
1. **活跃焦点球员指针法 (Active Player Pointer)：**
   * 游戏当前正在查看或编辑的焦点球员，其主数据指针挂载于静态基址：
     $$\text{ActivePlayer} = [[\text{NBA2K22.exe} + \text{0x0632B410}] + \text{0x118}]$$
   * 从该指针写入，直接命中当前 UI 所引用的根数据源，修改即刻呈现在屏幕上。
2. **全局全副本广播法 (Multi-Copy Broadcast)：**
   * 在进行全联盟大规模属性或合同更新时，通过内存特征码扫描锁定该球员的全部活跃副本（匹配 Face ID 与 姓名），对所有扫描出的有效副本同步执行批量写回；
3. **界面轻触唤醒 (UI Refresh Trigger)：**
   * 写回完成后，在游戏内轻拨一下手柄摇杆（切换至上一名/下一名球员再切回），即可强迫 2K UI 渲染管线重新从内存底层拉取最新数据。

---

## 三、球员精细化属性与球星专属互动修改规范

### 1. 属性与能力值修改
调用 `modifier.set_player_attribute(addr, attr_name, rating)`：
* 自动完成评分到内存原生的换算：$\text{Raw} = (\text{Rating} - 25) \times 3$；
* 示例：将哈利伯顿的三分从 25 改回 97，向偏移 `0x426` 写入 `uint8(216)`。

### 2. 球星专属被动赛场互动动画挂载 (Signature Package Injection)
这是 2K22 最具沉浸感的高级修改。无需替换球员面补，仅需改写球员结构体的动画与音效签名 ID，即可让任意年轻球员拥有历史超巨的招牌被动互动（抖肩、指表、看手、挑衅观众、专属回防步伐）：

| 目标球星风格 | 专属动画 ID (SIGNATURE_ID at 0xE8) | 专属音频 ID (AUDIO_SIG_ID at 0xEC) | 招牌被动赛场特写与回防互动 |
| :--- | :--- | :--- | :--- |
| **斯蒂芬·库里** (Curry) | `1629185898` (`0x611B676A`) | `1629185898` | 进三分后经典抖肩 (Shimmy)、嚼牙套摇头晃脑、蹦跳庆祝、队友暂停主动撞胸 |
| **达米安·利拉德** (Lillard) | `1628100000` 级别专属包 | `1628100000` | 关键球后冷酷点手腕看表 (Dame Time)、冷血散步回防 |
| **特雷·杨** (Trae Young) | `458013193` (`0x1B4CBA09`) | `458013193` | 冰人双手抱胸瑟瑟发抖 (Ice Trae)、客场投进三分后向观众鞠躬挑衅 |

### 3. 性格特征与关键先生位域激活 (Personality & Badges)
仅挂载动画包不够，必须激活球员的“外向”与“大心脏”底层掩码：
* **偏移 `0x4C0`：** 置位 `Bit 1 (0x02)` $\rightarrow$ 开启 `极具表现力 (EXPRESSIVE)`；
* **偏移 `0x4BD`：** 置位 `Bit 1 (0x02)` $\rightarrow$ 开启 `友善 (FRIENDLY)`（极大提升全队化学反应）；
* **偏移 `0x4BB`：** 置位 `Bit 1 (0x02)` $\rightarrow$ 开启 `领头羊 (ALPHA_DOG)`；
* **偏移 `0x4C4`：** 置位 `Bit 2 (0x04)` $\rightarrow$ 开启 `关键先生 (CLUTCH_PERFORMER)`；
* **关键射手徽章 (Clutch Shooter)：** 改为紫卡殿堂级（HOF Level 4）；
* **清除消极性格：** 强制将 `0x4BC`（内敛 RESERVED）与 `0x4C1`（悠闲 LAID_BACK）清零。

---

## 四、外部交易指令单注入与双轨执行模式 (Trade Execution Protocol)

外部 GM 决策引擎撮合出的合法交易，采用**双轨执行模式**注入游戏：

```
                    [Antigravity GM 撮合引擎]
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       【终极联盟 MyLEAGUE 模式】        【辉煌生涯 MyCAREER 模式】
       白道强制交易控制台注入            底层内存指针热互换
       (Trade Override Mode)           (Hot-Swap Memory Mode)
```

### 模式一：终极联盟 / MyLEAGUE 白道控制台强制过审法
这是**最稳定、最完美、100% 杜绝任何坏档风险**的推荐方案。
1. **关闭原生弱智交易：**
   * 写入基址：`NBA2K22.exe + 0x0632FAE8` 下的偏移 `0x170 (CPU_CPU_TRADE) = 0`；
   * 彻底剥夺 2K 原生 AI 自主发起的无脑交易权限。
2. **开启强制交易总开关 (Trade Override)：**
   * 写入偏移 `0x168 (TRADE_OVERRIDE) = 1`；
   * 游戏内的任何交易提案，对方球队将 100% 无条件强制同意。
3. **自动化安全过审：**
   * 由引擎通过键鼠模拟或内存提交交易表单；
   * 2K 原生引擎会自动重算两队的工资帽余额、自动调换球衣号码、更新战术轮换板、重新生成赛程战力榜，无需人工手动改写数百个指针。

### 模式二：辉煌生涯 / MC 模式底层内存指针热互换法
在玩家无法控制其他球队的纯 MC 模式下，采用底层指针调换：
1. **球员归属调换：**
   * 将 球员 A 的 `CURRENT_TEAM`（`0x60`）与 `CONTRACT_TEAM`（`0xA8`）改为 目标球队 B 的 `UNIQUE_ID`；
   * 将 球员 B 对应字段改为 球队 A 的 `UNIQUE_ID`；
2. **薪资总额与人数重算：**
   * 读取双方薪水 `SALARY_YEAR_1`（`0x1A4`），在两队结构体的 `TOTAL_SALARY`（`0xCBC`）与 `PAYROLL`（`0xFF4`）中完成增减平衡更新；
3. **轮换席位修复：**
   * 修正两队 `0x10A8`（活跃名单人数），确保不触发 2K 名单少于 13 人的防崩溃保护。

---

## 五、MC 模式真实历史与未来新秀名单注入协议 (MC Draft Class Injection)

### 1. 传统 MC 模式的致命局限
终极联盟模式在每个休赛期会弹窗允许玩家自由加载 `.FDC` 离线真实选秀名单（如 2022 班凯罗、2023 文班亚马、2025 弗拉格）。但 **MC 模式锁死了选秀名单选择入口**，每年只会生成由系统乱数拼凑出来的假人新秀，严重破坏了多赛季游玩的代入感。

### 2. 内存“偷梁换柱”注入流程
通过 Antigravity 外部注入器，可在 MC 模式中实现 **100% 真实选秀名单载入**：

```
[步骤 1: 触发时机]
MC 赛季打到季后赛结束进入休赛期前夕 (或者选秀大会开始前 1 天)
       │
       ▼
[步骤 2: 锁定系统生成的 60 个随机新秀槽位]
扫描内存中归属未分配/选秀池中的 60 个固定 Player 结构体 (0xDF0 步长)
       │
       ▼
[步骤 3: 批量覆盖真实历史/未来新秀 DNA]
读取本地预置的 JSON 新秀包 (包含文班亚马/切特/班凯罗等真实数据):
  - 写入真实姓与名 (0x0, 0x28, UTF-16LE)
  - 写入真实面补 Cyberface ID (0x6C)
  - 写入真实攻防属性与核心倾向 (0x41F~0x4B7)
  - 写入真实身高、臂展与身体模型参数
  - 写入球星专属动作包与性格徽章
       │
       ▼
[步骤 4: 推进游戏选秀大会]
选秀大会正常开启，各队按顺位选下被覆盖后的真实文班亚马、切特等超级巨星！
```

---

## 六、Python 自动化调用接口代码范式

```python
# -*- coding: utf-8 -*-
from memory import GameMemory
from modifier import LeagueModifier
import config

mem = GameMemory()
modifier = LeagueModifier(mem)

# 1. 安全开启强制交易，关闭原生 AI 交易
modifier.set_trade_override(True)
modifier.set_cpu_cpu_trade(False)

# 2. 获取焦点球员基址 (如哈利伯顿)
active_ptr = mem.read_uint64(mem.base_address + config.ACTIVE_PLAYER_STATIC_PTR_1)
if active_ptr:
    player_addr = active_ptr + 0x118
    
    # 3. 设置属性：三分 97，传球 98
    modifier.set_player_attribute(player_addr, "ATTR_THREE_POINT", 97)
    modifier.set_player_attribute(player_addr, "ATTR_PASS_ACCURACY", 98)
    
    # 4. 挂载库里招牌专属赛场互动 (0x611B676A)
    modifier.set_signature_package(player_addr, 0x611B676A)
    
    # 5. 点亮领头羊与极具表现力
    modifier.set_player_personality(player_addr, expressive=True, friendly=True, alpha_dog=True)
    
    print("已成功完成对焦点球员的完整生态注入！")
```
