# 任务包 84: 终极联盟世界线与全局规则参数 REA 原生执行任务包

> **任务标识**: `TASK-20261123-WORLDLINE-GLOBAL-SETTINGS-EXECUTION`  
> **任务类型**: 全局设置执行派单与 REA Native 结构化注入执行包  
> **协议规范**: `SPEC-FULL-DIMENSIONAL-NATIVE-MOD-V2` (Doc 43 第 5 节)  
> **本地执行目录**: `C:\nba2k22\exports\20261123_worldline_settings_execution\`  
> **仓库对应目录**: `08_Domain_Applications/Antigravity_GM_Engine/exports/20261123_worldline_settings_execution/`  
> **目标执行文件**: `global_worldline_settings_mod.json`  
> **执行目标**: 联盟全局规则控制器 `SLOT_TRADE` (`RVA 0x0632B498`)  
> **安全级别**: 严格受控 REA Native 结构化注入 (纯差分，零占位，禁用任意内存写入)  

---

## 1. 任务背景与世界线边界对齐

本任务包旨在落实 NBA 2K22 终极联盟（MyLEAGUE）中与**游戏世界规则紧密绑定的核心全局设置参数**。  
根据最新世界规则与人类指令，本执行包确立以下三大执行边界：

1. **排除项（绝不修改）**：
   - **30 队自动化 (Team Automation)**：完全取消，不强制覆盖，保留游戏自然状态；
   - **交易相关设置 (Trade & Draft Rules)**：人类玩家已在游戏内部配置完毕（电脑自主交易已彻底关闭），执行包内**完全不含任何交易设置项**；
   - **财务与合同 (Contracts & Finances)**：保持 NBA 官方 CBA 默认规则，保留新赛季中游戏 AI 球队自主在自由市场上按需签约的生态行为，不进行硬性压制。
2. **纯差分与零占位准则 (Strict Sparse Delta & No Placeholders)**：
   - 严格遵循 Doc 43 第 5 节升级准则，执行文件中**仅包含本次明确需要变更的 6 项关键参数**；
   - 严禁包含未改动的设置或占位伪造数据，杜绝一切脏数据污染。
3. **REA Native 原生调用**：
   - 执行模型必须通过 REA 原生工具的 native 能力定位 `SLOT_TRADE` 基址进行受控参数校准，严禁裸内存暴力 VirtualWrite。

---

## 2. 本次全局修改参数明细对照表

本次任务从采集基线中对比出真正需要校准的 6 项核心世界线参数，严格锁定在 `SLOT_TRADE` 模块中：

| 序号 | 字段名称 (Field) | 相对偏移 (Hex / Dec) | 类型 | 采集/原版基线 | 目标设定值 | 人类业务含义与生效理由 |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | **`career_ending_injury_frequency`** | `0x264` (612) | `uint32` | 50 | **5** | **【用户指定必改项】** 生涯报销退役大伤频率：极限压制至 5，彻底杜绝年轻超巨与历史球星在模拟中突发退役，保障联盟顶级战力完整性。 |
| 2 | **`injury_severity`** | `0x25C` (604) | `uint32` | 50 | **40** | **【用户指定必改项】** 模拟伤病严重程度：大幅削减 6~10 个月跟腱/十字韧带等毁灭性大伤，转化为 3~10 天每日观察 (Day-to-Day) 或 1~3 周短期休战。 |
| 3 | **`cpu_injury_frequency`** | `0x250` (592) | `uint32` | 50 | **55** | **【伤病联动调校项】** 模拟伤病发生频率：微调至 55，配合降低后的严重度（40），既产生真实常规赛小伤轮换考验，又绝不毁灭球星赛季。 |
| 4 | **`offseason_progression_rate`** | `0x26C` (620) | `uint32` | 50 | **48** | **【成长防通胀项】** 球员休赛期属性成长速率：微调至 48，压制 2K 原生 3 年后全联盟 80+ 评分恶性通胀，同时保障 1984~2021 历史新秀自然成长。 |
| 5 | **`morale_difficulty`** | `0x238` (568) | `uint32` | 50 | **35** | **【更衣室防崩项】** 更衣室士气波动难度：下调至 35，大幅削弱替补球员因出场时间微调即剧烈抱怨、摧毁更衣室的非理性过激反应。 |
| 6 | **`morale_effects`** | `0x23C` (572) | `uint32` | 50 | **40** | **【更衣室防崩项】** 低士气能力惩罚幅度：下调至 40，斩断原生“连输 3 场 -> 士气跌破 30 -> 全员能力暗扣 8~10 点 -> 必继续输球”的恶性循环。 |

---

## 3. 保持基准默认不变的参数清单（未列入执行包）

以下参数在采集基线中已完全符合本项目标准，按照纯差分零占位原则，**不写入执行文件**：
- `quarter_length`: 12 分钟 (实机比赛标准)
- `sim_quarter_length`: 12 分钟 (日历模拟标准)
- `normalize_stats`: 0 (实打 12 分钟严格关闭数据归一化，杜绝二次折算数据爆炸)
- `game_speed`: 0.50 (实机 50 标速)
- `injuries_enabled`: 1 (伤病系统全局总开关开启)
- `chemistry_difficulty` & `chemistry_effects`: 50 (化学反应保持官方中性)
- `regression_rate`: 50 (衰退速率保持官方中性)
- `training_effects`: 50 (日常训练保持官方中性)

---

## 4. 执行模型作业规范 (Execution Runbook)

执行模型拿到本任务包后，执行以下标准化流程：

1. **定位执行文件**：
   - 读取 `C:\nba2k22\exports\20261123_worldline_settings_execution\global_worldline_settings_mod.json`；
2. **基址解析与预检 (Preflight)**：
   - 通过 REA Native 机制解析 `SLOT_TRADE` 基址（静态指针槽位 `0x0632B498`）；
   - 验证目标进程 `NBA2K22.exe` 为当前活跃进程，存档处于就绪状态；
3. **逐项差分写入 (Sparse Delta Injection)**：
   - 遍历 `global_writes` 数组中的 6 项写入定义；
   - 计算目标物理地址：`target_addr = slot_trade_base + write["offset"]`；
   - 采用 `uint32` 格式依次写入 `val_target`；
4. **立即回读断言 (Readback Verification)**：
   - 写入完成后，立即对这 6 个偏移执行回读；
   - 断言：`actual_value == val_target`；
5. **异常阻断与回执生成**：
   - 若遇到基址未解析或回读数值不匹配，立即中断并向人类上报；
   - 全部写入并回读通过后，在 `C:\nba2k22\exports\` 目录下生成标准执行回执：
     `20261123_WORLDLINE_SETTINGS_EXECUTION_RECEIPT.json`。
