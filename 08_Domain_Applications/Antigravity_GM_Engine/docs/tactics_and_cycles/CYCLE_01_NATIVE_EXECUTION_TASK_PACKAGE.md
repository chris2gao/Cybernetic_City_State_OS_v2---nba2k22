# NBA 2K22 赛季第 01 轮 30 队战术与无形资产 Native 批量执行任务数据包
# (Cycle 01 30-Team Tactical & Intangibles Native Execution Task Package)

> **任务标识 (Task ID)**: `CYCLE_01_30_TEAMS_NATIVE_REBALANCE`  
> **所属赛季周期**: `season_2021_2022_cycle_01` (2021-2022 赛季开赛期全联盟首轮智能重构)  
> **执行模型对接角色**: `role-developer` / `batch_executor` (REA Native 批量修改执行模型)  
> **派单角色**: `role-planner` / `decision_architecture` (Antigravity GM 决策架构)  
> **目标实机进程**: `NBA2K22.exe` | **目标生涯存档**: `MyLEAGUE0005`  
> **标准接口协议版本**: `v1.0_native_batch_mod`  
> **一键热写入清单 (Ready JSON)**: [`cycle_01_native_execution_ready.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/cycle_01_native_execution_ready.json)  
> **配套机器清单 (Manifest)**: [`cycle_01_native_execution_manifest.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/cycle_01_native_execution_manifest.json)  

---

## 一、 任务背景与执行目标

本任务包是本赛季 **第 01 轮全联盟全维度战术与出场时间智能优化方案** 的正式落地执行指令。
通过前置的 50+ 项单项属性建模与队内相对反推计算，我们已经为全联盟 30 支球队、共计 **464 名球员** 计算出了最契合 2K 原生 AI 调度机制的无形资产（Intangibles）数值，并重构了 30 支球队的教练滑条、战术发起点、防守对位与核心球员倾向。

**批量执行模型（Batch Executor）的核心目标**：
利用 REA 工具链（或 Python Native 内存修改工具），以实机热写入（Live Memory Hot-Patch）或底层数据块注入方式，按赛区批次执行修改，并在游戏内触发自动存盘，完成全联盟 30 队的战术与出场时间闭环。

---

## 二、 内存修改安全性与合规性前置守则 (Preflight Boundaries)

执行模型在调用 REA 工具执行 Native 写入前，必须严格遵守以下四项铁律：

### 1. 存档快照备份守则 (Snapshot Safety)
在向运行中的 `NBA2K22.exe` 注入任何数据前，必须确保存档目录已被完整备份：
- **目标存档路径**: `E:\games\NBA 2K22\data\steam\steam_settings\1644960\remote\MyLEAGUE0005`
- **本地快照库**: `C:\nba2k22\saves\MyLEAGUE0005\`

### 2. 教练设置菜单关闭铁律 (`coach_editor_closed_confirmed == True`)
- 2K 引擎在用户打开“教练设置/战术板”子菜单时，会在 UI 层维护一份临时的私有副本。如果此时通过内存热写入教练数据块，在退出菜单时会被 UI 副本反向覆盖。
- **守则**：执行修改时，游戏必须停留在 MyLEAGUE 主界面或日历模拟界面，严禁在战术编辑页面执行写入！

### 3. 外观堆指针绝不篡改守则 (Preserve `0x90` Appearance Pointer)
- 球员 1,264 字节结构体中，偏移 `0x90` 处的 64 位指针引用的独立外观数据块控制骨骼模型。
- **守则**：本次批量修改只涉及属性（无形资产）与倾向，**绝不触碰任何球员的 `0x90` 指针**，从根源上杜绝闪退与身材畸形。

### 4. 无形资产绝对值域约束 (`[25, 99]`)
- 全联盟所有 464 名球员的写入值必须被严格限制在整数 `25` 到 `99` 之间，严禁越界。

---

## 三、 Native 数据结构与 REA 字段偏移对照表

### 1. 球员结构体 (Player Struct - 1,264 字节, `0x4F0` 步长)
- **球员池线性起始基地址**: 动态校准 (参考 `address_calibrator.py` 与 `player_pool.sqlite`)
- **单个球员基地址计算**: `Base_Address = PlayerPool_Base + (Roster_Slot * 0x4F0)`

| 字段名称 | 字节大小 | 数据类型 | 允许取值 | 业务含义与作用 |
| :--- | :---: | :---: | :---: | :--- |
| **Intangibles (无形资产)** | 1 字节 | `uint8` | `[25, 99]` | **决定队内相对有效综评，间接控制出场时间** |
| **Shot Contest (干扰投篮)** | 1 字节 | `uint8` | `[25, 99]` | 防守战术修正 |
| **Pass Perception (传球感知)** | 1 字节 | `uint8` | `[25, 99]` | 截断传球倾向强化 |
| **Spot Up 3PT Tendency** | 1 字节 | `uint8` | `[0, 100]` | 定点三分倾向 |
| **Drive Tendency** | 1 字节 | `uint8` | `[0, 100]` | 突破攻框倾向 |

### 2. 球队与教练数据块 (Team / Coach Data Block)
- 通过 `CoachLocator` 动态定位目标球队控制块。

| 字段名称 | 数据类型 | 典型设置值 | 业务含义 |
| :--- | :---: | :---: | :--- |
| **Bench Depth (板凳深度)** | `uint8` | `8 ~ 11` (本周期统一设为 `9` 或 `10`) | 锁定 AI 使用的常规轮换人数 |
| **Bench Utilization (板凳使用度)** | `uint8` | `40 ~ 65` | 控制替补与主力的时间分配斜率 |
| **Lineup Pace (阵容节奏)** | `uint8` | `45 ~ 60` | 配合球队进攻体系的推反击/磨阵地速度 |
| **Defensive Help (防守协防)** | `uint8` | `45 ~ 65` | 护筐与外线轮转协防激进程度 |

---

## 四、 分区批次执行计划 (6 大赛区，共 30 支球队)

执行模型应按照以下顺序逐个赛区执行修改与校验，并在每个赛区完成后打出完成回执：

### 第 1 批次：大西洋赛区 (Atlantic Division - 5 队)
- **文件源**: [`BATCH_01_ATLANTIC_FULL_DIMENSIONAL_SPEC.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/BATCH_01_ATLANTIC_FULL_DIMENSIONAL_SPEC.json)
- **覆盖球队**: 
  1. `PHI` (76ers - 16人): 恩比德(50锁定主力)、西蒙斯(99)、哈里斯(99)、马克西(99)、赛布尔(99)、德拉蒙德(99)、科尔克马兹(25雪藏)
  2. `BOS` (Celtics - 15人): 塔图姆(85)、布朗(99)、斯玛特(99)、霍福德(99)、罗威(99)、普理查德(99)
  3. `NYK` (Knicks - 15人): 兰德尔(85)、巴雷特(99)、罗斯(99)、富尼耶(99)、罗宾逊(99)、奎克利(99)
  4. `BKN` (Nets - 15人): 杜兰特(87)、哈登(99)、欧文(99)、哈里斯(99)、克拉克斯顿(99)、阿德(99)、米尔斯(99)
  5. `TOR` (Raptors - 15人): 西亚卡姆(86)、范弗利特(99)、阿奴诺比(99)、巴恩斯(99)、特伦特(99)、阿丘瓦(99)

### 第 2 批次：中部赛区 (Central Division - 5 队)
- **文件源**: [`BATCH_02_CENTRAL_FULL_DIMENSIONAL_SPEC.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/BATCH_02_CENTRAL_FULL_DIMENSIONAL_SPEC.json)
- **覆盖球队**: `MIL` (雄鹿 15人), `CHI` (公牛 16人), `CLE` (骑士 15人), `IND` (步行者 15人), `DET` (活塞 15人)

### 第 3 批次：东南赛区 (Southeast Division - 5 队)
- **文件源**: [`BATCH_03_SOUTHEAST_FULL_DIMENSIONAL_SPEC.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/BATCH_03_SOUTHEAST_FULL_DIMENSIONAL_SPEC.json)
- **覆盖球队**: `MIA` (热火 14人), `ATL` (老鹰 16人), `WAS` (奇才 16人), `CHA` (黄蜂 15人), `ORL` (魔术 16人)

### 第 4 批次：太平洋赛区 (Pacific Division - 5 队)
- **文件源**: [`BATCH_04_PACIFIC_FULL_DIMENSIONAL_SPEC.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/BATCH_04_PACIFIC_FULL_DIMENSIONAL_SPEC.json)
- **覆盖球队**: 
  1. `GSW` (勇士 16人): 库里(87)、克莱(99)、维金斯(99)、普尔(99)、库明加(99)、怀斯曼(99)、波特(70)、卢尼(25)、格林(25)
  2. `LAL` (湖人 15人): 詹姆斯(82)、浓眉(68)、威少(60)、蒙克(99)、甜瓜(99)、霍华德(81)、里夫斯(99)、老将群(25)
  3. `LAC` (快船 16人), `PHX` (太阳 15人), `SAC` (国王 16人)

### 第 5 批次：西北赛区 (Northwest Division - 5 队)
- **文件源**: [`BATCH_05_NORTHWEST_FULL_DIMENSIONAL_SPEC.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/BATCH_05_NORTHWEST_FULL_DIMENSIONAL_SPEC.json)
- **覆盖球队**: `DEN` (掘金 16人), `UTA` (爵士 16人), `MIN` (森林狼 16人), `POR` (开拓者 15人), `OKC` (雷霆 16人)

### 第 6 批次：西南赛区 (Southwest Division - 5 队)
- **文件源**: [`BATCH_06_SOUTHWEST_FULL_DIMENSIONAL_SPEC.json`](file:///C:/nba2k22/exports/season_2021_2022_cycle_01/BATCH_06_SOUTHWEST_FULL_DIMENSIONAL_SPEC.json)
- **覆盖球队**: 
  1. `DAL` (独行侠 15人): 东契奇(86)、布伦森(99)、波尔津吉斯(99)、布洛克(99)、芬尼史密斯(99)、鲍威尔(99)、克莱伯(99)、格林(99)、哈达威(25雪藏)
  2. `MEM` (灰熊 16人), `NOP` (鹈鹕 15人), `HOU` (火箭 17人), `SAS` (马刺 15人)

---

## 五、 REA 执行工具调用与验收标准

### 1. REA 执行工作流推荐
1. **加载任务清单**: 读取 `cycle_01_native_execution_manifest.json`。
2. **连接游戏进程**: 获取 `NBA2K22.exe` 主进程句柄。
3. **分赛区事务写入**:
   - 遍历球队 $\to$ 写入教练滑条数据块。
   - 遍历球员 $\to$ 写入目标无形资产与关键倾向。
4. **内存读回校验 (CAS / Compare-and-Swap)**:
   - 写入完成后，立即回读目标地址的字节值。
   - 确认写入值与 `target_intangibles` 100% 一致。
5. **触发游戏内保存**:
   - 在游戏内进入日历界面模拟 1 天或手动按“保存游戏”，促使 2K 引擎将内存序列化至磁盘存档。

### 2. 验收完成标志 (Definition of Done)
- 30 支球队共计 464 名球员的内存无形资产写入完毕。
- 回读校验成功率 100%（0 读写失败）。
- 模拟测试运行 3 场比赛，确认各队轮换出场时间严格按照预期梯队运行，且无闪退、无卡死。
