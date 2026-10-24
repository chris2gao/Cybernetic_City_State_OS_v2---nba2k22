# NBA2K22 第一大任务 · RES-P 字段族原生登记库存候选 V1

**状态**：`01b_source_inventory_candidate`。这份清单不是数据库最终字段字典，不等于真实 UI 选项卡全集、实机可采集的字段全集，也不证明这些 offset 在不同存档/赛季稳定。

## 已核对来源与口径

- `config/memory_field_profile.json`：`fields.PLAYER` 共 72 条注册记录，其中 `attributes` 55 条，`contract` 17 条；原始字段名和 offset 均按仓库记录抄录。
- `research/native_access/AG_NATIVE_01D/ui_native_source_matrix.json`：`screens.PLAYER_CARD.fields` 注册 8 个入口级项目；研究文件自述若干 `NATIVE_VERIFIED`，但这一标记只是**仓库已有研究的状态声明**，不是本次独立游戏实机验证。
- `potential` 作为登记中隐藏字段：不得因为“登记”就对普通 GM/Coach 展示。游戏界面可见的 OVR、Durability 集合、全部 Tendency 和 Badge 逐项字典需单独现场核实。
- 现有注册中 `original_contract_years` 和 `extension_length` 共用数值 offset 833；**只能标为潜在复用/冲突待核实**，不能擅自认定两字段完全等价。
- 任一名字是工程注册键，并不自动等于游戏 UI 文本、最终 SQL 列名或业务范围已确定。

## Attributes 注册项（55 条）

| # | 工程字段名 | Offset (十进制) | 现有转换登记 | 数据证据/访问状态 |
|---:|---|---:|---|---|
| 1 | `driving_layup` | 1055 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 2 | `post_fadeaway` | 1056 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 3 | `post_hook` | 1057 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 4 | `post_moves` | 1058 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 5 | `draw_foul` | 1059 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 6 | `shot_close` | 1060 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 7 | `mid_range_shot` | 1061 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 8 | `3pt_shot` | 1062 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 9 | `free_throw` | 1063 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 10 | `ball_control` | 1064 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 11 | `passing_iq` | 1065 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 12 | `passing_accuracy` | 1066 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 13 | `offensive_rebound` | 1067 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 14 | `standing_dunk` | 1077 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 15 | `driving_dunk` | 1078 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 16 | `shot_iq` | 1086 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 17 | `passing_vision` | 1107 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 18 | `hands` | 1109 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 19 | `defensive_rebound` | 1068 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 20 | `interior_defense` | 1069 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 21 | `perimeter_defense` | 1070 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 22 | `block` | 1073 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 23 | `steal` | 1074 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 24 | `shot_contest` | 1110 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 25 | `lateral_quickness` | 1071 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 26 | `speed` | 1079 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 27 | `speed_with_ball` | 1080 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 28 | `acceleration` | 1081 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 29 | `vertical` | 1082 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 30 | `strength` | 1083 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 31 | `stamina` | 1084 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 32 | `hustle` | 1085 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 33 | `head_durability` | 1090 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 34 | `neck_durability` | 1091 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 35 | `back_durability` | 1092 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 36 | `left_shoulder_durability` | 1093 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 37 | `right_shoulder_durability` | 1094 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 38 | `left_elbow_durability` | 1095 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 39 | `right_elbow_durability` | 1096 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 40 | `left_hip_durability` | 1097 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 41 | `right_hip_durability` | 1098 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 42 | `left_knee_durability` | 1099 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 43 | `right_knee_durability` | 1100 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 44 | `left_ankle_durability` | 1101 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 45 | `right_ankle_durability` | 1102 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 46 | `left_foot_durability` | 1103 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 47 | `right_foot_durability` | 1104 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 48 | `misc_durability` | 1105 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 49 | `pass_perception` | 1072 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 50 | `defensive_consistency` | 1075 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 51 | `help_defensive_iq` | 1076 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 52 | `offensive_consistency` | 1087 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 53 | `pick_and_roll_defensive_iq` | 1108 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 54 | `intangibles` | 1088 | `rating` | REGISTRY_ONLY; UI/读值逐项待核实 |
| 55 | `potential` | 1089 | `rating` | HIDDEN_RESTRICTED; 不能向普通GM泄漏 |

## 合同注册项（17 条；第8轮讨论业务输出）

| # | 工程字段名 | Offset (十进制) | bytes | 证据状态 |
|---:|---|---:|---|---|
| 1 | `bird_years` | 854 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 2 | `original_contract_years` | 833 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 3 | `years_left_on_contract` | 814 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 4 | `contract_option` | 791 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 5 | `no_trade` | 838 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 6 | `extension_length` | 833 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 7 | `extension_option` | 834 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 8 | `extension_no_trade` | 796 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 9 | `contract_year_1` | 420 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 10 | `contract_year_2` | 424 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 11 | `contract_year_3` | 428 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 12 | `contract_year_4` | 432 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 13 | `contract_year_5` | 436 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 14 | `contract_year_6` | 440 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 15 | `contract_type` | 836 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 16 | `euro_stash_years_left` | 659 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |
| 17 | `two_way_days_left` | 351 | unknown | REGISTRY_ONLY; 具体合同语义/冲突与字段映射待核实 |

## Native Player Card 入口级状态

| 研究字段组/入口 | 研究文件 status | 01b 未完成的拆解 |
|---|---|---|
| `identity_names` | `NATIVE_VERIFIED` | 真实PC22 UI页签/身份/时间与数据源双向映射 |
| `player_id` | `NATIVE_VERIFIED` | 真实PC22 UI页签/身份/时间与数据源双向映射 |
| `current_team_ptr` | `NATIVE_VERIFIED` | 真实PC22 UI页签/身份/时间与数据源双向映射 |
| `current_season_stats_index` | `NATIVE_VERIFIED` | 真实PC22 UI页签/身份/时间与数据源双向映射 |
| `career_history_stats_array` | `NATIVE_VERIFIED` | 真实PC22 UI页签/身份/时间与数据源双向映射 |
| `player_attributes` | `NATIVE_VERIFIED` | 单项能力/综合数值、显示单位、读值与角色隔离 |
| `player_tendencies` | `NATIVE_VERIFIED` | 每一项倾向与合法值 |
| `player_badges` | `NATIVE_VERIFIED` | 所有真实徽章身份、等级编码、类别、缺失状态 |

## 不允许直接宣称已完成的项目

1. 55 条 Registered Attributes 不等于 55 个 **GM 可见**能力字段，`potential` 是隐藏/受限；最终显示全集以真实游戏UI核实为准。
2. `player_tendencies` / `player_badges` 为字段族入口，当前这个注册文件未枚举它们的完整逐项 UI 字段数量和标识；不能自动宣称已覆盖。
3. `Play Types` 的具体枚举、槽位、顺序/空值及原生位置，需 02 提供目标版本游戏证据。
4. 允许的 OVR 数值、综合 Durability 的实际 UI 对应、合同字段重叠/选项语义需进一步证实；不计算不存在证据的 OVR 公式。
5. 最终数据库表数、字段类型、PK/FK、索引、带历史的物理表/JSON/Delta 实现不在本清单确认范围，由结果建模 B 决定。
