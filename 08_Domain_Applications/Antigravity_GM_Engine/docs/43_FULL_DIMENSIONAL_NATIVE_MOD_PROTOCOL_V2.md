# NBA 2K22 全维度战术、教练与球员资产 REA Native 批量注入标准接口协议 (v2.0 全维通用规范)
# (Full-Dimensional Tactical, Coaching & Player Assets REA Native Batch Injection Protocol Specification v2.0)

> **协议标识 (Protocol ID)**: `SPEC-FULL-DIMENSIONAL-NATIVE-MOD-V2`  
> **适用版本**: NBA 2K22 (Steam PC x64) | 引擎底层: `NBA2K22.exe`  
> **适用场景**: 全联盟 30 队战术重构、赛季轮次调整（Cycle 01~04）、休赛期训练强化、选秀与自建名单批量注入。  
> **覆盖范围 (6 大核心维度)**:  
> 1. 球队与阵容信息 (`Team & Lineups`)  
> 2. 教练滑条与轮换深度 (`Coach Settings`)  
> 3. 战术板、发起点与自由战术 (`Tactical Playbook & Initiator`)  
> 4. 攻防重点与防守对位 (`POE & Defensive Gameplan`)  
> 5. 球员攻防属性与战术倾向 (`Player Attributes & Tendencies`, 含无形资产)  
> 6. 球员技能等级徽章与性格特征 (`Player Badges & Personality`)  
> **对接角色**:  
> - **发布方 (任务规划/数据输出)**: `role-planner` / `decision_architecture`  
> - **执行方 (批量热注入/回读校验)**: `role-developer` / `batch_executor`  

---

## 一、 协议核心设计原则与三大宪法守则 (Constitutional Principles)

为确保全联盟 30 支球队、464+ 名球员在实机运行内存（`NBA2K22.exe`）中一键安全生效且 100% 杜绝游戏崩溃与数据污染，上游模型必须严格遵循以下原则：

### 1. 外观堆指针绝不篡改守则 (Preserve `0x90` Appearance Pointer)
- 球员 1,264 字节结构体中，偏移 `0x90` 处的 64 位指针引用的独立外观数据块控制骨骼模型。
- **守则**：全维度批量修改过程中，**绝不触碰任何球员的 `0x90` 指针**，从根源上杜绝闪退与身材畸形。

### 2. 四维锁定精确寻址原则 (Deterministic 4-Point Addressing)
- 严禁仅提供球员纯文本名字。在 2K 庞大的球员池中，同名球员多达数个版本。
- 每个球员条目必须提供：
  1. `team_id`: 球队索引 (`0 ~ 29`)
  2. `roster_index`: 球队名册槽位序号 (`0 ~ 15`)
  3. `cyberface_id`: 官方真实面补 ID（防串号双重锚点校验）
  4. `player_name`: 校验用全名

### 3. 双轨数值与纯数字枚举 (Dual-Track Values & Pure Numeric ID)
- 所有数值同时给出人类可读数值（`val_human`）与内存底层直写字节（`val_raw`）；
- 涉及战术系统、POE、防守规则、战术类型等枚举时，**严禁输出混合字符串**（如 `"FEED_THE_POST (3)"`），必须标准化为纯数字 ID（如 `{"id": 3, "name": "FEED_THE_POST"}` 或直接输出 `val_raw: 3`），杜绝执行端正则解析脆弱性。

---

## 二、 六大维度数据结构与底层二进制偏移速查字典

### 维度 1：球队与阵容 (Team & Lineups)
- 球队数据块步长：`4,696 字节` (由 `AddressCalibrator.check_and_calibrate_teams()` 动态定位)
- 球队名册指针数组：`team_address + 0x00 .. 0xC8`（25 个 64 位球员结构体指针）
- 主教练指针：`team_address + 0xCE8`（64 位指针，指向该队主教练的 `STAFF` 结构体）
- 阵容首发/终结五虎：在 `lineups` 数组中记录 `roster_index`（0~15）或球员全名。

### 维度 2：教练滑条与轮换设置 (Coach Settings)
目标结构体：主教练 `COACHDATA`（步长 352 字节，通过 `team_address + 0xCE8` 定位）

| 字段名称 | 偏移 (十进制) | 偏移 (十六进制) | 数据类型 | 取值范围 | 业务含义与说明 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Preferred System** | 266 | `0x10A` | `uint8` (低3位) | `0 ~ 7` | 偏好战术系统 (0=平衡, 1=磨阵地, 2=跑轰, 4=内线策应等) |
| **Active System** | 267 | `0x10B` | `uint8` (高4位) | `0 ~ 7` | 当前激活战术系统 (写入时: `raw = (raw & 0x0F) \| (id << 4)`) |
| **Bench Depth** | 268 | `0x10C` | `uint8` | `8 ~ 11` | 轮换人数 (常规赛锁定 9~10 人，季后赛 8 人) |
| **Bench Utilization** | 269 | `0x10D` | `uint8` | `0 ~ 100` | 替补使用率 (通常设为 45~65) |
| **Run Play Tendency** | 224 | `0x0E0` | `uint8` | `0 ~ 100` | 战术执行倾向 (跑战术频率，典型值 70~85) |
| **Zone Usage** | 226 | `0x0E2` | `uint8` | `0 ~ 100` | 联防使用频率 (通常为 0~25) |

### 维度 3：战术体系与发起点 (Tactical Playbook & Initiator)
目标结构体：球员结构体 `PLAYER_STRUCT`（步长 1,264 字节，`0x4F0`）

| 字段名称 | 偏移 (十进制) | 偏移 (十六进制) | 数据类型 / 位域 | 取值范围 | 业务含义与说明 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Is Play Initiator** | 362 | `0x16A` | `uint8` | `0` 或 `1` | 战术发起者标志 (`1`=拥有控球发起权，`0`=终结者) |
| **Play Type Slot 1** | 360 | `0x168` | 低 4 位 (`& 0x0F`) | `0 ~ 15` | 第一主打战术类型 (枚举见下表) |
| **Play Type Slot 2** | 360 | `0x168` | 高 4 位 (`>> 4`) | `0 ~ 15` | 第二战术类型 |
| **Play Type Slot 3** | 361 | `0x169` | 低 4 位 (`& 0x0F`) | `0 ~ 15` | 第三战术类型 |
| **Play Type Slot 4** | 361 | `0x169` | 高 4 位 (`>> 4`) | `0 ~ 15` | 第四战术类型 |

**战术类型枚举表 (`Play Types Enum`)**:
- `0`: NONE (无)
- `1`: ISOLATION (单打)
- `2`: ISOLATION_POINT (控卫单打)
- `3`: ISOLATION_WING (侧翼单打)
- `4`: PR_BALL_HANDLER (挡拆持球人)
- `7`: PR_ROLL_MAN (挡拆下顺人)
- `8`: POST_UP_LOW (低位背身)
- `9`: POST_UP_HIGH (高位背身)
- `11`: CUTTER (空切拉开)
- `12`: HANDOFF_RECEIVER (手递手接球人)
- `13`: HANDOFF_PASSER (手递手传球人)
- `14`: MID_RANGE (中距离战术)
- `15`: THREE_POINT (三分定点/无球跑位战术)

### 维度 4：攻防重点、模拟侧重与防守对位 (POE & Simulated Gameplan Focus)
目标结构体：比赛策略数据块 `GAMEPLAN`（步长 880 字节 / `0x370`）

#### 1. REA Native 结构体精确定位寻址规程 (GAMEPLAN Memory Resolution)
- **FRANCHISE 基址定位**：通过游戏全局 Getter `getter(6278620)`（即 `Process.mainModule.base + 0x5fcddc` 处 RVA 寻址指令）读取 64 位全局 Franchise 控制块基址；
- **球队 Franchise 记录定位**：`record = FRANCHISE + 0x19cfd0 + i * 0x13e70`（`i ∈ [0, 35]`，根据 `uint16(record + 0x00) == team_id` 匹配目标球队）；
- **GAMEPLAN 物理基址**：`gameplan_base = record + 0x7854`；
- **归属双核验守卫**：核验 `uint16(gameplan_base + 0x02) == team_id`，杜绝串队写入。

#### 2. 模拟侧重 12 字节连续安全写块字典 (0x178 ~ 0x183 / 376 ~ 387)
该 12 字节区域直接控制 NBA 2K22 终极联盟/王朝模式中的“模拟侧重”核心中枢与 6 大 POE 攻防哲学：

| 字段名称 | 偏移 (十进制) | 偏移 (十六进制) | 数据类型 | 取值范围 / 枚举 | 业务含义与说明 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Scoring Option 1** | 376 | `0x178` | `uint16` (小端序) | 真实球员 ID | 终结第一选择：绑定球队第一得分核心 (如 Embiid: 4090) |
| **Scoring Option 2** | 378 | `0x17A` | `uint16` (小端序) | 真实球员 ID | 终结第二选择：绑定副攻手 (如 Harden: 1603) |
| **Scoring Option 3** | 380 | `0x17C` | `uint16` (小端序) | 真实球员 ID | 终结第三选择：绑定第三得分点 (如 Maxey: 8011) |
| **POE Offense (进攻重点)** | 382 | `0x17E` | `uint8` | `1 ~ 6` | `1`=冲击篮筐, `2`=为射手跑位, `3`=打低位内线, `4`=挡拆进攻 |
| **POE Offense Tempo (进攻节奏)** | 383 | `0x17F` | `uint8` | `7 ~ 9` | `7`=耐心阵地战 (Patient), `8`=中立, `9`=尽早出手反击 (Shoot at Will) |
| **POE Offense Rebound (前板策略)** | 384 | `0x180` | `uint8` | `10 ~ 12` | `10`=冲抢前板 (Crash), `12`=极速退防限制快攻 (Limit Transition) |
| **POE Defense (防守重点)** | 385 | `0x181` | `uint8` | `13 ~ 15` | `13`=保护禁区 (Protect Paint), `15`=贴防外线三分 (Limit 3PT) |
| **POE Defense Physicality (对抗策略)** | 386 | `0x182` | `uint8` | `16 ~ 18` | `16`=保守防犯规, `18`=强硬身体对抗 (Play Physical) |
| **POE Defense Rebound (后板策略)** | 387 | `0x183` | `uint8` | `19 ~ 21` | `19`=全员保护防守篮板 (Crash Boards), `21`=抓板下反击 (Run Transition) |

#### 3. COACHDATA 镜像位域同步 (可选高内聚守卫)
在主教练结构体 `COACHDATA`（`team + 0xCE8`）偏移 316（`0x13C`）处的 `uint32` 打包字中，低位段同步存储了上述 6 大 POE（5 位每项）：
`word = (poe_def) | (poe_def_phys << 5) | (poe_def_reb << 10) | (poe_off << 15) | (poe_off_tempo << 20) | (poe_off_reb << 25)`。
写入 `GAMEPLAN` 后可同步回写该打包字，保证游戏内教练界面与后台模拟引擎 100% 状态一致。

### 维度 5：球员属性与战术倾向 (Attributes & Tendencies)
目标结构体：球员结构体 `PLAYER_STRUCT`（1,264 字节）

1. **核心攻防属性（29 项全量，`0x41F ~ 0x455`，单字节 `uint8`）**：
   - **换算公式**：$\text{Raw} = \min(255, \max(0, \lfloor(\text{Rating}-25)\times 3\rfloor))$
   - **无形资产 (Intangibles)**：`offset: 1088 (0x440)`，**决定队内相对有效综评，间接控制 AI 轮换出场时间**
   - 投篮属性：`shot_close (1060)`, `mid_range (1061)`, `three_point (1062)`, `free_throw (1063)`
   - 终结属性：`driving_layup (1055)`, `standing_dunk (1077)`, `driving_dunk (1078)`
   - 背身属性：`post_hook (1057)`, `post_fadeaway (1056)`, `post_moves (1058)`
   - 组织属性：`ball_control (1064)`, `pass_accuracy (1066)`, `pass_iq (1065)`, `pass_vision (1107)`
   - 防守属性：`interior_def (1069)`, `perimeter_def (1070)`, `lateral_quick (1071)`, `steal (1074)`, `block (1073)`, `pass_perception (1072)`
   - 篮板属性：`off_rebound (1067)`, `def_rebound (1068)`
   - 身体素质：`speed (1079)`, `speed_with_ball (1080)`, `acceleration (1081)`, `vertical (1082)`, `strength (1083)`, `stamina (1084)`, `hustle (1085)`

2. **战术倾向（29 项全量，`0x458 ~ 0x4BA`，直写整数 `0 ~ 100`）**：
   - 核心决策：`touches (1177)`, `shot (1112)`, `drive (1155)`, `dish_to_open_man (1176)`
   - 投篮倾向：`shot_close (1126)`, `shot_mid_range (1130)`, `shot_three (1138)`, `spot_up_three (1139)`
   - 防守倾向：`contest_shot (1207)`, `block_shot (1208)`, `on_ball_steal (1206)`, `pass_interception (1204)`
   - 内线与挡拆：`post_up (1178)`, `roll_vs_pop (1179)`, `attack_strong_on_drive (1175)`

### 维度 6：徽章与性格特征 (Badges & Personality)
目标结构体：球员结构体 `PLAYER_STRUCT`（`0x4BB ~ 0x4E2`）

1. **性格特征位域 (`0x4BB ~ 0x4C4`, 10 字节)**：
   - 领头羊 (Alpha Dog)、极具表现力 (Expressive)、禁区硬汉 (Enforcer)、团队至上 (Team Player)、微波炉 (Spark Plug) 等。
2. **技能等级徽章位域 (`0x4C5 ~ 0x4E2`, 30 字节位域，80 项技能徽章)**：
   - 等级：`0`=无, `1`=铜, `2`=银, `3`=金, `4`=紫 (Hall of Fame)
   - 每个技能等级徽章在底层占用 **3 位（Bits）**；
   - 写入前自动清除泥人残留技能等级徽章，写入后保留底层性格特征。

---

## 三、 标准化全维执行规格书 JSON Schema 模板 (Machine-Ready JSON Blueprint)

上游规划模型发布全维任务时，必须输出符合以下格式的单一 JSON 清单文件（例如：`cycle_XX_native_execution_ready.json`）：

```json
{
  "protocol_version": "v2.0_full_dimensional_native_mod",
  "task_package_id": "CYCLE_02_30_TEAMS_TACTICAL_AND_ATTR_REBALANCE",
  "season_id": "2021-2022",
  "target_career": "MyLEAGUE0005",
  "target_process": "NBA2K22.exe",
  "total_teams": 30,
  "total_players": 464,
  "batches": [
    {
      "batch_id": "BATCH_01_ATLANTIC",
      "division": "Atlantic",
      "teams": [
        {
          "team_id": 0,
          "team_abbr": "PHI",
          "team_name": "Philadelphia 76ers",

          "team_settings": {
            "team_chemistry": 85,
            "fan_interest": 92
          },

          "coaching_writes": [
            {
              "field_name": "active_system",
              "target_block": "COACHDATA",
              "offset": 267,
              "type": "uint8",
              "val_human": 4,
              "val_raw": 4,
              "desc": "Post Centric"
            },
            {
              "field_name": "bench_depth",
              "target_block": "COACHDATA",
              "offset": 268,
              "type": "uint8",
              "val_human": 9,
              "val_raw": 9
            },
            {
              "field_name": "bench_utilization",
              "target_block": "COACHDATA",
              "offset": 269,
              "type": "uint8",
              "val_human": 65,
              "val_raw": 65
            },
            {
              "field_name": "run_play_tendency",
              "target_block": "COACHDATA",
              "offset": 224,
              "type": "uint8",
              "val_human": 80,
              "val_raw": 80
            },
            {
              "field_name": "poe_offense",
              "target_block": "GAMEPLAN",
              "offset": 382,
              "type": "uint8",
              "val_raw": 3,
              "desc": "FEED_THE_POST"
            },
            {
              "field_name": "poe_defense",
              "target_block": "GAMEPLAN",
              "offset": 385,
              "type": "uint8",
              "val_raw": 13,
              "desc": "PROTECT_PAINT"
            }
          ],

          "player_writes": [
            {
              "player_name": "Joel Embiid",
              "roster_index": 4,
              "cyberface_id": 4090,
              "position": "C",
              "target_minutes": 37.0,

              "tactical_playbook": {
                "is_play_initiator": 1,
                "play_types": [8, 9, 7, 14]
              },

              "modifications": [
                {
                  "field": "intangibles",
                  "target_block": "PLAYER_STRUCT",
                  "offset": 1088,
                  "type": "uint8",
                  "val_human": 50,
                  "val_raw": 75,
                  "expected_prev_raw": 180,
                  "cas_formula": "raw = (val_human - 25) * 3"
                },
                {
                  "field": "touches",
                  "target_block": "PLAYER_STRUCT",
                  "offset": 1177,
                  "type": "uint8",
                  "val_human": 96,
                  "val_raw": 96
                },
                {
                  "field": "contest_shot",
                  "target_block": "PLAYER_STRUCT",
                  "offset": 1207,
                  "type": "uint8",
                  "val_human": 95,
                  "val_raw": 95
                },
                {
                  "field": "shot_close",
                  "target_block": "PLAYER_STRUCT",
                  "offset": 1060,
                  "type": "uint8",
                  "val_human": 92,
                  "val_raw": 201
                }
              ],

              "badges": {
                "RimProtector": 3,
                "Intimidator": 3,
                "PostDropStepper": 3,
                "BackdownPunisher": 3,
                "AlphaDog": 1
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### 单队模拟侧重规格书 JSON Schema 模板 (`SIMULATED_GAMEPLAN_FOCUS_MOD`)
针对专属任务子目录下的单队模拟侧重独立文件（如 `00_PHI_sim_focus_mod.json`），采用以下紧凑纯差分标准：

```json
{
  "protocol_version": "v2.0_full_dimensional_native_mod",
  "spec_type": "SIMULATED_GAMEPLAN_FOCUS_MOD",
  "team_id": 0,
  "team_abbr": "PHI",
  "team_name": "Philadelphia 76ers",
  "source_research_doc": "56_PHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md",
  "target_menu": "教练设置 - 模拟侧重 (Simulated Focus / Gameplan Focus)",
  "execution_target": "GAMEPLAN (stride 880, continuous offset range 376-387 / 0x178-0x183)",
  "conflict_resolution": "STRICT_LATEST_RESEARCH_DOC_PRIORITY",
  "simulated_focus_summary": {
    "scoring_options": [
      { "option_slot": 1, "player_name": "Joel Embiid", "player_id": 4090, "roster_slot": 2, "touch_proposal": 88 },
      { "option_slot": 2, "player_name": "James Harden", "player_id": 1603, "roster_slot": 12, "touch_proposal": 82 },
      { "option_slot": 3, "player_name": "Tyrese Maxey", "player_id": 8011, "roster_slot": 5, "touch_proposal": 62 }
    ],
    "poe_settings": {
      "poe_offense": { "id": 3, "name": "FEED_THE_POST", "desc": "打低位内线" },
      "poe_offense_tempo": { "id": 7, "name": "PATIENT_OFFENSE", "desc": "耐心阵地战" },
      "poe_offense_rebound": { "id": 12, "name": "LIMIT_TRANSITION", "desc": "极速退防限制快攻" },
      "poe_defense": { "id": 13, "name": "PROTECT_PAINT", "desc": "保护禁区油漆区" },
      "poe_defense_physicality": { "id": 18, "name": "PLAY_PHYSICAL", "desc": "强硬身体对抗" },
      "poe_defense_rebound": { "id": 19, "name": "CRASH_DEFENSIVE_BOARDS", "desc": "全员保护防守篮板" }
    }
  },
  "writes": [
    { "field_name": "scoring_option_1", "target_block": "GAMEPLAN", "offset": 376, "type": "uint16", "val_raw": 4090, "val_human": "Joel Embiid" },
    { "field_name": "scoring_option_2", "target_block": "GAMEPLAN", "offset": 378, "type": "uint16", "val_raw": 1603, "val_human": "James Harden" },
    { "field_name": "scoring_option_3", "target_block": "GAMEPLAN", "offset": 380, "type": "uint16", "val_raw": 8011, "val_human": "Tyrese Maxey" },
    { "field_name": "poe_offense", "target_block": "GAMEPLAN", "offset": 382, "type": "uint8", "val_raw": 3, "val_human": "FEED_THE_POST" },
    { "field_name": "poe_offense_tempo", "target_block": "GAMEPLAN", "offset": 383, "type": "uint8", "val_raw": 7, "val_human": "PATIENT_OFFENSE" },
    { "field_name": "poe_offense_rebound", "target_block": "GAMEPLAN", "offset": 384, "type": "uint8", "val_raw": 12, "val_human": "LIMIT_TRANSITION" },
    { "field_name": "poe_defense", "target_block": "GAMEPLAN", "offset": 385, "type": "uint8", "val_raw": 13, "val_human": "PROTECT_PAINT" },
    { "field_name": "poe_defense_physicality", "target_block": "GAMEPLAN", "offset": 386, "type": "uint8", "val_raw": 18, "val_human": "PLAY_PHYSICAL" },
    { "field_name": "poe_defense_rebound", "target_block": "GAMEPLAN", "offset": 387, "type": "uint8", "val_raw": 19, "val_human": "CRASH_DEFENSIVE_BOARDS" }
  ]
}
```

---

## 四、 执行端自动化流水线与验收闭环 (Automated Execution & CAS Acceptance)

执行模型拿到满足本 v2.0 协议的规格书后，自动执行以下标准化操作：

```mermaid
flowchart TD
    A["加载 v2.0 全维就绪清单 JSON"] --> B["Step 1: 动态内存校准锁定 30 支球队基址"]
    B --> C["Step 2: Preflight 检查 (确认 PID、存档时间戳快照)"]
    C --> D["Step 3: 按 6 大赛区遍历球队"]
    D --> E["写入教练滑条与战术系统 (COACHDATA / GAMEPLAN)"]
    E --> F["定位球队 25 球员指针，核验 0x90 外观指针未篡改"]
    F --> G["写入战术发起点 (0x16A) 与四槽战术类型 (0x168..169)"]
    G --> H["CAS 校验并写入无形资产、攻防属性与倾向"]
    H --> I["按位清空残留等级徽章，写入真实技能徽章与性格位域"]
    I --> J["Step 4: CAS 全量立即回读断言 (ReadProcessMemory)"]
    J --> K["生成标准化全量回执 CYCLE_XX_NATIVE_EXECUTION_RECEIPT.json"]
```

### 验收交付回执标准
每次执行完成后，在 `C:\nba2k22\exports\` 自动输出执行回执，核心断言指标：
1. `total_teams_executed == 30` (100% 成功)
2. `total_players_verified == 464` (100% 成功)
3. `mismatches_count == 0` (0 读写异常)
4. `appearance_pointer_0x90_integrity == 100.0%`


---

## 五、 REA Native 纯差分执行与分队/全局输出规范 (2026-11-23 升级准则)

为确保数据更新绝对精准、零内存污染且易于独立分步执行与全量审计，自 2026-11-23 起本接口协议正式实施以下三大铁律：

### 规则一：REA Native 原生工具更新与零占位纯差分原则 (REA Native Only & Strict Sparse Delta)
1. **严格使用 REA 原生方法更新**：
   - 更新操作必须严格通过 REA 工具调用游戏底层已认证的 Native 功能或安全包装接口；
   - **严禁使用任意内存直接暴力写入 (Memory Poking / Raw VirtualWrite)**。
2. **零占位假数据铁律 (No Placeholders / Dummies)**：
   - 接口文件中**严禁出现任何占位数据**（如 `65535`、`0`、`null`、未定角色或随机伪造数值）；
   - 文件内**仅包含本次明确需要更新的数值与设置项**；无需修改的设置绝对不写进文件，杜绝污染已有干净存档环境。

### 规则二：开发模型输出规范：日期+任务专属子目录与按队单文件 (Task Subfolder & Single-Team / Global Separation)
1. **专属时间戳目录**：
   - 开发模型每次执行开发任务生成执行包时，必须在对应的 `exports/` 目录下创建本次任务的专属子文件夹；
   - 子文件夹命名规范：`YYYYMMDD_<task_name>_execution`（例如：`20261123_simulated_gameplan_focus_execution`）。
2. **球队/球员任务：按队独立单文件**：
   - 凡涉及球队或球员的更新，一律按照 **“一队一文件”** 形式生成（命名如 `{tid:02d}_{abbr}_mod.json`）；
   - 每个单队文件严格遵循本协议格式，仅包含该队本次需要修改的设置信息；
   - **无需要更新内容的球队严禁建立文件**。
3. **全局设置任务：独立全局文件**：
   - 凡与特定球队无关的全局设置（如全局滑条、联盟规则、跨球队共享配置），生成**单独的一个全局设置文件**（如 `global_settings_mod.json`），规则与纯差分要求完全相同。

### 规则三：执行模型作业标准：顺序批处理、未明确项阻断上报与全量闭环审计 (Sequential Execution & Gap Interruption)
1. **定位并按序执行**：
   - 执行模型进入工作时，直接定位目标任务对应的子文件夹；
   - 严格按照文件命名顺序（如 Team ID 升序），**每次读取一个文件进行批量修改**。
2. **未明确项即时阻断与上报**：
   - 执行模型调用 REA 工具的 native 功能注入时，若检测到某项设置未明确定义、存在数值歧义或目标未定位，**必须立即暂停并向人类上报**，严禁擅自推断或跳过。
3. **严格单文件闭环与最终全量核验**：
   - 必须完全执行完当前文件并核验成功后，才能按照顺序开始执行第二个文件；
   - 当该目录下所有文件全部执行完毕后，执行全量自动化核验流水线，检查是否所有目标文件都已准确无误执行完成，并输出标准化执行回执。

---

## 六、 复杂多队/多球员开发任务的蜂群分叉克隆（Swarm Fork）架构与人类前置询问准则 (2026-11-24 增补)

为解决多球队（如全联盟 30 队）或多球员批量研判中，单模型聊天窗口面临的 **输出 Token 截断、上下文注意力衰减（Attention Drift）以及死板代码脚本无法胜任复杂战术定性博弈判断** 的核心矛盾，自 2026-11-24 起正式确立“蜂群分叉克隆（Swarm Fork）”批量研发架构：

### 1. 蜂群分叉克隆架构运作机制
1. **主协调员母体（Coordinator as Single Source of Truth）**：
   - 主窗口（Coordinator）加载并维护最新的全局离线记忆（PRMS 单元）、Doc 85 倾向规范与 Doc 86 训练规范；
2. **上下文零冷启动分叉（`fork: "coordinator"`）**：
   - 派发分析工作者（Worker）时，必须指定 `fork: "coordinator"` 参数，从主窗口的历史会话直接分叉；
   - Worker 诞生瞬间 100% 继承全部前置讨论、规则与哨兵基线，零重复读盘，最大化命中底层的提示词缓存（Prompt Caching）；
3. **任务切片与独立纯差分输出（Task Sharding）**：
   - 每个 Worker 仅负责 2~4 支球队（约 20~40 位球员），专注读取对应球队的最新战术报告（Doc 50~79）；
   - 由大模型发挥顶尖的篮球战术与博弈定性判断能力，精准提取训练模板与倾向差分；
   - 直接输出严格符合本协议第 5 节的独立单队 JSON 至专属目录（如 `C:\nba2k22\exports\YYYYMMDD_<task>_execution\`），**纯差分零占位，严禁任何 dummy/65535 覆盖**；
4. **主协调员统一闭环验收**：
   - 各 Worker 交付后，Coordinator 运行自动化脚本对所有文件进行语法、零占位与哨兵抽验（如哈利伯顿、约基奇、克莱、戈贝尔），出具总回执。

### 2. 人类前置询问铁律（Human Gate Before Activation）
1. **激活触发阈值**：
   - 凡是接获涉及 **多支球队（≥3 支）** 或 **多名球员（≥15 名核心轮换）** 的批量研判、战术重构或属性倾向调优任务；
2. **前置询问义务**：
   - **开发模型严禁擅自静默开跑！** 必须在主窗口首先向人类总架构师发起正式询问：
     > *“检测到本次任务涉及多支球队/大量球员的批量深度研判，是否启动‘蜂群分叉克隆（Swarm Fork）’并行开发模式？（提议分 X 个克隆节点，按赛区切片并行生成纯差分单队执行文件）”*
3. **执行约束**：
   - 仅在获得人类明确许可（“可以启动 / 赞同 / 跑一次”）后，方可正式调用 `swarm(action="add", fork="coordinator", ...)` 推进任务；若人类选择单步推进或普通对话，则严格遵循单步交互。
