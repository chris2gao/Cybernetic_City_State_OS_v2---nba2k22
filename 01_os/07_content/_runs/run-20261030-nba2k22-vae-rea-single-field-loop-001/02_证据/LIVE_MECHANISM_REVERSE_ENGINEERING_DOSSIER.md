# NBA 2K22 全量 204 个种子字段实机 REA 机制逆向与证据质量分层档案 (Remediated V2)

> **生成时间**：2026-10-31T10:26:38.026068+00:00
> **实机目标**：`NBA2K22.exe` (PE SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`, PID: 5488, Base: 0x140000000)
> **核心分析对象**：现役焦点球员 Tyrese Haliburton (Player Struct 步长 0xDF0, 倾向块 0x458..0x4BA)
> **控制器槽位分离**：SLOT_SETTINGS (0x0632B4B0), SLOT_TRADE (0x0632B498), SLOT_SLIDERS (0x0632B4A0)
> **认知分层声明**：全量 204 项机制分析均严格标识为 `PRIOR_LITERATURE_HYPOTHESIS`，在获得授权的受控实机变化实验前，不主张已测定真实引擎因果。

## 证据质量分层统计
- **总字段记录**：204
- **有效实机收据 (`LIVE_RECEIPT`)**：48 (经结构体与范围校验的球员倾向)
- **原始快照候选 (`RAW_MEMORY_CAPTURE_CANDIDATE`)**：156
- **其中降级为 `UNKNOWN`**：71 (包含 19 项 Coach 地址别名字段与越界世界设置)
- **浮点位型解码修正**：11 (如 game_speed 1056964608 -> float32 0.5)
- **物理地址碰撞与别名映射**：详见 `PHYSICAL_IDENTITY_COLLISION_TABLE.json` (共 36 组别名对，实际对应 50 个物理控制器槽位)

---

### TENDENCY_NATIVE_001 · SHOT_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SHOT_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b030` | 解码值 `96`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：全场总出手意愿基准闸门。决定持球人在半场阵地战中优先寻找个人终结还是转移球。
- **机制与跨字段关联**：
  - 由真实 FGA/36 与 USG% 换算，直接锚定球员战术定位
  - 与 Touches (0x499) 协同确立全队球权阶层，避免单场40分独霸破坏模拟拟真
  - 与突破倾向 (0x483) 和突分倾向 (0x498) 构成进攻终结方式竞争三角
  - 进一步细分为篮下(0x465)、中投(0x46A)、三分(0x472)热区子倾向
  - 受教练 Pace 影响：Pace > 75 时显著加速 16 秒内提早出手概率
- **非线性阈值/边界**：数值 > 85 确立第一得分核心行为；数值 < 25 强制进入纯蓝领/组织传控逻辑。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x458)


### TENDENCY_NATIVE_002 · DRIVING_LAYUP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.DRIVING_LAYUP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b031` | 解码值 `30`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：突破合球切入禁区（0~6尺）时选择普通挑篮/打板上篮而非扣篮或分球的意愿。
- **机制与跨字段关联**：
  - 受 Driving Layup 属性门禁与上篮动作包加成
  - 与 Slithery Finisher, Acrobat, Fearless Finisher 徽章联动
  - 与突破扣篮倾向 (0x45B)、禁区小抛投 (0x463)、突分给空位队友 (0x498) 竞争终结槽位
  - 防守人装备 Intimidator 徽章时，直接影响强行出手时的上篮命中衰减
- **非线性阈值/边界**：数值 > 70 展现丰富拉杆上篮动作；数值 < 30 在对抗时更倾向急停或回传。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x459)


### TENDENCY_NATIVE_003 · STANDING_DUNK_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.STANDING_DUNK_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b032` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：篮下低位静止持球时原地拔起双手扣篮或背扣的终结意愿（内线中锋核心项）。
- **机制与跨字段关联**：
  - 严格受 Standing Dunk 原生属性与身高模型约束（后卫若属性 < 40 则静默失效）
  - 与 Rise Up（死区扣将）和 Fast Twitch（快速出手）徽章形成乘数激发
  - 与篮下近距离强攻 (0x465) 联动，直接压制低效的原地虚晃小跳投
- **非线性阈值/边界**：数值 > 80 确保内线大闸在深位接球瞬间触发霸王扣篮；数值 < 20 导致频繁原地假动作被封盖。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x45A)


### TENDENCY_NATIVE_004 · DRIVING_DUNK_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.DRIVING_DUNK_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b033` | 解码值 `75`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：持球突破行进冲刺时直接起跳战斧、单手或双手暴扣终结意愿。
- **机制与跨字段关联**：
  - 受 Driving Dunk 属性和弹跳 (Vertical) 属性门禁约束
  - 与 Limitless Takeoff（无限起飞）和 Posterizer（隔扣达人）徽章强绑定
  - 对抗防守人 Rim Protector 徽章时，引擎判定进入隔扣对抗判定还是被撞停上篮
  - 与突破上篮倾向 (0x459) 互为消长
- **非线性阈值/边界**：数值 > 75 确保具备冲刺空间时优先起跳扣篮，规避追尾盖帽；数值 < 25 则全员地板流上篮。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x45B)


### TENDENCY_NATIVE_005 · FLASHY_DUNK_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.FLASHY_DUNK_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b034` | 解码值 `10`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：突破扣篮时触发观赏性花式扣篮包（360度、大风车、双手折叠背扣）的意愿。
- **机制与跨字段关联**：
  - 受球员士气、观赏度及客场比赛氛围调制
  - 与 Special Delivery 与防守人贴身破坏率权衡（花式扣篮脱手失误率增加 15%~25%）
  - 严禁过高分配给注重实用防守的主力，避免关键分被切球
- **非线性阈值/边界**：数值 > 50 频繁触发高难度扣篮动画；数值 < 10 保证动作朴实高效。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x45C)


### TENDENCY_NATIVE_006 · ALLEY_OOP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.ALLEY_OOP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b035` | 解码值 `25`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 ALLEY_OOP_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x45D)


### TENDENCY_NATIVE_007 · PUTBACK_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.PUTBACK_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b036` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：拼抢前场篮板瞬间不落地直接在空中完成补篮或补扣的终结意愿。
- **机制与跨字段关联**：
  - 受 Offensive Rebound 属性门禁与身高臂展判定约束
  - 与 Putback Boss（补篮大王）徽章联动，提供抢板起跳瞬间弹跳与滞空补偿
  - 与常规进攻篮板下地重置战术（0x45F）形成博弈
- **非线性阈值/边界**：数值 > 50 展现暴力空中二次进攻；数值 < 10 落地重置进攻节奏。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x45E)


### TENDENCY_NATIVE_008 · CRASH_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.CRASH_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b037` | 解码值 `65`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：外线投篮出手瞬间，无球人员从外线主动冲抢前场篮板的进攻激进度。
- **机制与跨字段关联**：
  - 直接与教练战术中的 Crash Offensive Glass 选项形成权重乘法
  - 与本方转换防守（Fast Break Defense）形成剧烈权衡：冲抢失败将直接送对手多打少反击
  - 与球员体力衰减曲线联动，频繁冲撞显著加速体能恶化
- **非线性阈值/边界**：数值 > 70 极大提高二次进攻机会，但反击失分增加 30%；数值 < 30 第一时间有序退防。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x45F)


### TENDENCY_NATIVE_009 · SPIN_LAYUP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SPIN_LAYUP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b038` | 解码值 `60`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SPIN_LAYUP_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x460)


### TENDENCY_NATIVE_010 · HOP_STEP_LAYUP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.HOP_STEP_LAYUP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b039` | 解码值 `65`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 HOP_STEP_LAYUP_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x461)


### TENDENCY_NATIVE_011 · EURO_STEP_LAYUP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.EURO_STEP_LAYUP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b03a` | 解码值 `45`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 EURO_STEP_LAYUP_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x462)


### TENDENCY_NATIVE_012 · FLOATER_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.FLOATER_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b03b` | 解码值 `55`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：突破至油漆区边缘（3~10尺）时急停使用单手小抛投终结意愿（后卫避封盖招牌动作）。
- **机制与跨字段关联**：
  - 受 Close Shot 属性与 Tear Dropper（抛投大师）徽章强绑定
  - 有效破解内线护框大闸的垂直起跳封盖（Rim Protector 难以干扰抛物线顶点）
  - 特雷杨、东契奇、哈利伯顿等节奏型后卫的核心得分武器
- **非线性阈值/边界**：数值 > 80 成为禁区前首选终结武器；数值 < 20 则强行硬挤篮下造成失误。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x463)


### TENDENCY_NATIVE_013 · STEP_THROUGH_SHOT_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.STEP_THROUGH_SHOT_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b03c` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 STEP_THROUGH_SHOT_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x464)


### TENDENCY_NATIVE_014 · SHOT_UNDER_BASKET_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SHOT_UNDER_BASKET_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b03d` | 解码值 `54`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：篮下 0~3 尺极深位置受贴防时的就地起跳强攻终结意愿。
- **机制与跨字段关联**：
  - 与 Fast Twitch 和 Grace Under Pressure 徽章联动
  - 受防守人 Interior Defense 和 Menace 贴防压迫干扰
  - 内线强攻中锋（恩比德、约基奇）的主要得分手段之一
- **非线性阈值/边界**：数值 > 75 确保篮下得球绝不犹豫回传；数值 < 30 容易在包夹下停球被判三秒违例。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x465)


### TENDENCY_NATIVE_015 · SHOT_CLOSE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SHOT_CLOSE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b03e` | 解码值 `36`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：罚球线内 3~10 尺短距离区域的原地跳投出手意愿（现代 NBA 低效热区）。
- **机制与跨字段关联**：
  - 与近距离投篮 (Close Shot) 属性联动
  - 现代魔球化名单中通常建议大幅调低此项，避免原地小跳投停滞阵地战流速
  - 与小抛投 (0x463) 互为竞争替代项
- **非线性阈值/边界**：数值 < 25 可有效净化进攻选择，促使球员往外分球或直接杀入篮下。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x466)


### TENDENCY_NATIVE_016 · UNKNOWN_RAW_BYTE_016
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x467`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b03f` | 解码值 `2`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_017 · UNKNOWN_RAW_BYTE_017
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x468`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b040` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_018 · UNKNOWN_RAW_BYTE_018
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x469`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b041` | 解码值 `4`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_019 · SHOT_MID_RANGE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SHOT_MID_RANGE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b042` | 解码值 `11`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SHOT_MID_RANGE_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x46A)


### TENDENCY_NATIVE_020 · SPOT_UP_SHOT_MID_RANGE
- **家族与候选键**：`player_tendency` / `tendency.SPOT_UP_SHOT_MID_RANGE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b043` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SPOT_UP_SHOT_MID_RANGE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x46B)


### TENDENCY_NATIVE_021 · OFF_SCREEN_SHOT_MID_RANGE
- **家族与候选键**：`player_tendency` / `tendency.OFF_SCREEN_SHOT_MID_RANGE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b044` | 解码值 `45`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 OFF_SCREEN_SHOT_MID_RANGE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x46C)


### TENDENCY_NATIVE_022 · UNKNOWN_RAW_BYTE_022
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x46d`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b045` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_023 · UNKNOWN_RAW_BYTE_023
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x46e`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b046` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_024 · UNKNOWN_RAW_BYTE_024
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x46f`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b047` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_025 · UNKNOWN_RAW_BYTE_025
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x470`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b048` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_026 · UNKNOWN_RAW_BYTE_026
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x471`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b049` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_027 · SHOT_THREE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SHOT_THREE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b04a` | 解码值 `98`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：全场三分球总出手基准意愿。现代空间篮球的第一核心战略滑块。
- **机制与跨字段关联**：
  - 由球员真实 3PAr（三分出手占总出手百分比）严格换算
  - 与 Three-Point Rating (98)、Sniper、Limitless Spot-Up 徽章强绑定
  - 与教练战术体系（如空间五外 5-Out、七秒跑轰）形成战术共振
  - 与中投倾向 (0x46A) 构成现代魔球化替代关系
- **非线性阈值/边界**：数值 > 85 确立高产魔球三分手（场均 8+ 次出手）；传统内线必须锁定在 0~5。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x472)


### TENDENCY_NATIVE_028 · SPOT_UP_SHOT_THREE
- **家族与候选键**：`player_tendency` / `tendency.SPOT_UP_SHOT_THREE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b04b` | 解码值 `95`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：侧翼与底角定点接球三分出手意愿（3&D 侧翼生命线）。
- **机制与跨字段关联**：
  - 与 Corner Specialist（底角专家）和 Catch & Shoot 徽章强联动
  - 决定战术突分传出后，底角空位射手是果断拔起还是停顿犹豫
- **非线性阈值/边界**：数值 > 90 打造顶级无球空间炮台（克莱、希尔德）。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x473)


### TENDENCY_NATIVE_029 · OFF_SCREEN_SHOT_THREE
- **家族与候选键**：`player_tendency` / `tendency.OFF_SCREEN_SHOT_THREE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b04c` | 解码值 `75`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：借掩护反跑溜底线或电梯门掩护反切三分线出手的意愿（库里/雷阿伦模式）。
- **机制与跨字段关联**：
  - 与 Playbook 3PT 专属掩护跑位战术强绑定
  - 与 Slippery Off-Ball 和 Tireless Shooter 徽章联动
- **非线性阈值/边界**：数值 > 85 构成顶级无球神射手跑位威胁。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x474)


### TENDENCY_NATIVE_030 · UNKNOWN_RAW_BYTE_030
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x475`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b04d` | 解码值 `14`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_031 · UNKNOWN_RAW_BYTE_031
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x476`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b04e` | 解码值 `99`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_032 · UNKNOWN_RAW_BYTE_032
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x477`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b04f` | 解码值 `61`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_033 · UNKNOWN_RAW_BYTE_033
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x478`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b050` | 解码值 `76`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_034 · UNKNOWN_RAW_BYTE_034
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x479`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b051` | 解码值 `7`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_035 · CONTESTED_JUMPER_THREE
- **家族与候选键**：`player_tendency` / `tendency.CONTESTED_JUMPER_THREE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b052` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：防守人贴身对位（Tight/Smother）情况下依然强拔三分出手的意愿（巨星神仙球）。
- **机制与跨字段关联**：
  - 与 Deadeye（神射手）和 Blinders（盲区）徽章联动
  - 极高值会导致普通球员顶着包夹强投，严重恶化真实命中率（TS%）
- **非线性阈值/边界**：超巨建议 40~55；常规轮换球员严禁超过 25。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x47A)


### TENDENCY_NATIVE_036 · CONTESTED_JUMPER_MID_RANGE
- **家族与候选键**：`player_tendency` / `tendency.CONTESTED_JUMPER_MID_RANGE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b053` | 解码值 `18`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 CONTESTED_JUMPER_MID_RANGE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x47B)


### TENDENCY_NATIVE_037 · STEPBACK_JUMPER_THREE
- **家族与候选键**：`player_tendency` / `tendency.STEPBACK_JUMPER_THREE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b054` | 解码值 `64`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：持球运球后突然后撤步拉开空间拔起投三分的倾向（哈登/东契奇招牌动作）。
- **机制与跨字段关联**：
  - 受 Ball Handle 控球属性与 Space Creator 徽章强绑定
  - 与普通定点三分区分，属于典型的持球单打创造出手空间动作
- **非线性阈值/边界**：单打大核给到 85~95；纯定点投手置 0。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x47C)


### TENDENCY_NATIVE_038 · STEPBACK_JUMPER_MID_RANGE
- **家族与候选键**：`player_tendency` / `tendency.STEPBACK_JUMPER_MID_RANGE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b055` | 解码值 `48`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 STEPBACK_JUMPER_MID_RANGE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x47D)


### TENDENCY_NATIVE_039 · SPIN_JUMPER_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SPIN_JUMPER_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b056` | 解码值 `15`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SPIN_JUMPER_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x47E)


### TENDENCY_NATIVE_040 · TRANSITION_PULL_UP_THREE
- **家族与候选键**：`player_tendency` / `tendency.TRANSITION_PULL_UP_THREE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b057` | 解码值 `46`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：攻防转换快攻推反击过程中，尚未落位直接追身干拔急停三分的倾向。
- **机制与跨字段关联**：
  - 与教练战术 Pace 和 Fast Break Focus 强关联
  - 哈利伯顿、库里、利拉德等持球大核的快攻追身三分核心参数
- **非线性阈值/边界**：快攻神射给 80~95；传统后卫置 15~30。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x47F)


### TENDENCY_NATIVE_041 · DRIVE_PULL_UP_THREE
- **家族与候选键**：`player_tendency` / `tendency.DRIVE_PULL_UP_THREE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b058` | 解码值 `42`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 DRIVE_PULL_UP_THREE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x480)


### TENDENCY_NATIVE_042 · DRIVE_PULL_UP_MID_RANGE
- **家族与候选键**：`player_tendency` / `tendency.DRIVE_PULL_UP_MID_RANGE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b059` | 解码值 `31`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 DRIVE_PULL_UP_MID_RANGE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x481)


### TENDENCY_NATIVE_043 · UNKNOWN_RAW_BYTE_043
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x482`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b05a` | 解码值 `10`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_044 · DRIVE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.DRIVE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b05b` | 解码值 `99`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：外线持球突破整体意愿。决定球员接球后是选择投篮/转移球还是弯腰压步突内线。
- **机制与跨字段关联**：
  - 受 Speed with Ball 与 Quick First Step 徽章加成
  - 官方默认全员 75+ 是造成内线拥堵的根本病灶，必须根据场均突破次数严格定级
  - 与突分倾向 (0x498) 形成突破后后续处理的分叉判定
- **非线性阈值/边界**：突破狂魔（莫兰特/字母哥）90+；纯投手压缩在 15~25。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x483)


### TENDENCY_NATIVE_045 · SPOT_UP_DRIVE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.SPOT_UP_DRIVE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b05c` | 解码值 `25`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SPOT_UP_DRIVE_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x484)


### TENDENCY_NATIVE_046 · OFF_SCREEN_DRIVE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.OFF_SCREEN_DRIVE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b05d` | 解码值 `35`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 OFF_SCREEN_DRIVE_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x485)


### TENDENCY_NATIVE_047 · UNKNOWN_RAW_BYTE_047
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x486`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b05e` | 解码值 `75`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_048 · UNKNOWN_RAW_BYTE_048
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x487`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b05f` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_049 · UNKNOWN_RAW_BYTE_049
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x488`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b060` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_050 · UNKNOWN_RAW_BYTE_050
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x489`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b061` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_051 · UNKNOWN_RAW_BYTE_051
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x48a`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b062` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_052 · UNKNOWN_RAW_BYTE_052
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x48b`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b063` | 解码值 `25`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_053 · UNKNOWN_RAW_BYTE_053
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x48c`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b064` | 解码值 `25`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_054 · UNKNOWN_RAW_BYTE_054
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x48d`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b065` | 解码值 `25`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_055 · UNKNOWN_RAW_BYTE_055
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x48e`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b066` | 解码值 `45`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_056 · UNKNOWN_RAW_BYTE_056
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x48f`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b067` | 解码值 `30`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_057 · UNKNOWN_RAW_BYTE_057
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x490`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b068` | 解码值 `45`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_058 · UNKNOWN_RAW_BYTE_058
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x491`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b069` | 解码值 `15`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_059 · UNKNOWN_RAW_BYTE_059
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x492`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b06a` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_060 · UNKNOWN_RAW_BYTE_060
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x493`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b06b` | 解码值 `15`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_061 · UNKNOWN_RAW_BYTE_061
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x494`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b06c` | 解码值 `30`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_062 · UNKNOWN_RAW_BYTE_062
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x495`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b06d` | 解码值 `15`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_063 · UNKNOWN_RAW_BYTE_063
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x496`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b06e` | 解码值 `90`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_064 · ATTACK_STRONG_ON_DRIVE
- **家族与候选键**：`player_tendency` / `tendency.ATTACK_STRONG_ON_DRIVE`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b06f` | 解码值 `20`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 ATTACK_STRONG_ON_DRIVE 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x497)


### TENDENCY_NATIVE_065 · DISH_TO_OPEN_MAN_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.DISH_TO_OPEN_MAN_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b070` | 解码值 `70`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：持球突破撕扯防线后，主动跳起分球给外线或内线空位队友的无私助攻意愿。
- **机制与跨字段关联**：
  - 与 Pass Accuracy (95)、Dimer（十全十美）、Bullet Passer 徽章强联动
  - 顶级组织大师（哈利伯顿、保罗、纳什）的核心灵魂倾向
  - 与纯得分后卫单打到底（Attack Strong On Drive 0x497）互为相反调节
- **非线性阈值/边界**：顶级传控核心给 90~98；纯终结攻坚手维持 45~60。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x498)


### TENDENCY_NATIVE_066 · TOUCHES_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.TOUCHES_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b071` | 解码值 `98`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：全队球权支配权重。直接决定阵地战谁持球过半场及战术终结优先权（Touches 争议核心）。
- **机制与跨字段关联**：
  - 与教练 Playbook 中 Primary Scoring Option 战术调用权重联动
  - 在战术破产或进入 Freelance Motion 时决定无球呼叫要球频率
  - 与 USG% 和全队五人薪资/地位梯队严密咬合
- **非线性阈值/边界**：第一持球大核 90~99；二当家 75~85；无球侧翼 45~60；吃饼内线 20~35。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x499)


### TENDENCY_NATIVE_067 · POST_UP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.POST_UP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b072` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：呼叫战术或落位时背身靠打（Post Up）要求的意愿。
- **机制与跨字段关联**：
  - 受 Post Control 属性与 Backdown Punisher 徽章联动
  - 与现代魔球空间体系冲突，仅适用于约基奇、恩比德等低位万花筒
- **非线性阈值/边界**：传统低位杀手给 80+；现代空间后卫与侧翼置 0~5。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x49A)


### TENDENCY_NATIVE_068 · ROLL_VS_POP_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.ROLL_VS_POP_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b073` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 ROLL_VS_POP_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x49B)


### TENDENCY_NATIVE_069 · TRANSITION_SPOT_UP
- **家族与候选键**：`player_tendency` / `tendency.TRANSITION_SPOT_UP`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b074` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 TRANSITION_SPOT_UP 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x49C)


### TENDENCY_NATIVE_070 · UNKNOWN_RAW_BYTE_070
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x49d`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b075` | 解码值 `20`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_071 · UNKNOWN_RAW_BYTE_071
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x49e`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b076` | 解码值 `59`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_072 · UNKNOWN_RAW_BYTE_072
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x49f`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b077` | 解码值 `91`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_073 · UNKNOWN_RAW_BYTE_073
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a0`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b078` | 解码值 `92`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_074 · PLAY_DISCIPLINE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.PLAY_DISCIPLINE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b079` | 解码值 `90`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：战术执行纪律性。数值越高越会耐心完整跑完教练预设的全部掩护与切入路线。
- **机制与跨字段关联**：
  - 与教练 Offensive Playcalling 设置联动
  - 高数值抑制单打独斗，提高团队配合得分占比
- **非线性阈值/边界**：老将与战术型控卫给 85~95；乱战得分手给 30~50。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4A1)


### TENDENCY_NATIVE_075 · UNKNOWN_RAW_BYTE_075
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a2`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b07a` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_076 · UNKNOWN_RAW_BYTE_076
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a3`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b07b` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_077 · UNKNOWN_RAW_BYTE_077
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a4`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b07c` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_078 · UNKNOWN_RAW_BYTE_078
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a5`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b07d` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_079 · UNKNOWN_RAW_BYTE_079
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a6`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b07e` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_080 · UNKNOWN_RAW_BYTE_080
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a7`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b07f` | 解码值 `4`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_081 · UNKNOWN_RAW_BYTE_081
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a8`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b080` | 解码值 `8`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_082 · UNKNOWN_RAW_BYTE_082
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4a9`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b081` | 解码值 `28`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_083 · UNKNOWN_RAW_BYTE_083
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4aa`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b082` | 解码值 `13`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_084 · UNKNOWN_RAW_BYTE_084
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4ab`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b083` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_085 · UNKNOWN_RAW_BYTE_085
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4ac`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b084` | 解码值 `20`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_086 · UNKNOWN_RAW_BYTE_086
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4ad`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b085` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_087 · UNKNOWN_RAW_BYTE_087
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4ae`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b086` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_088 · UNKNOWN_RAW_BYTE_088
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4af`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b087` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_089 · UNKNOWN_RAW_BYTE_089
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4b0`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b088` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_090 · UNKNOWN_RAW_BYTE_090
- **家族与候选键**：`player_tendency` / `tendency.RAW_0x4b1`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (UNKNOWN_RAW_BYTE_WITH_ADDRESS)
- **内存地址与数值**：地址 `0x7ff4e4e9b089` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：未映射原生内存槽位（位于 0x458..0x4BA 连续倾向内存块内）。反汇编尚未定位到具体读取或消费函数，属于未解析原始字节，不推定为保留或历史模板。
- **机制与跨字段关联**：
  - 球员结构体连续字节流
  - 内存对齐与未标注功能槽位
- **非线性阈值/边界**：UNKNOWN_RAW_BYTE_WITH_ADDRESS
- **审计说明**：Unmapped raw byte offset in player continuous block; no disassembly consumer traced.


### TENDENCY_NATIVE_091 · FLASHY_PASS_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.FLASHY_PASS_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b08a` | 解码值 `35`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 FLASHY_PASS_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B2)


### TENDENCY_NATIVE_092 · ALLEY_OOP_PASS_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.ALLEY_OOP_PASS_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b08b` | 解码值 `99`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 ALLEY_OOP_PASS_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B3)


### TENDENCY_NATIVE_093 · PASS_INTERCEPTION_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.PASS_INTERCEPTION_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b08c` | 解码值 `75`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 PASS_INTERCEPTION_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B4)


### TENDENCY_NATIVE_094 · TAKE_CHARGE_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.TAKE_CHARGE_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b08d` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 TAKE_CHARGE_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B5)


### TENDENCY_NATIVE_095 · ON_BALL_STEAL_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.ON_BALL_STEAL_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b08e` | 解码值 `85`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 ON_BALL_STEAL_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B6)


### TENDENCY_NATIVE_096 · CONTEST_SHOT_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.CONTEST_SHOT_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b08f` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：贴身防守举手贴脸干扰投篮的纪律性（护框大师必改核心项）。
- **机制与跨字段关联**：
  - 受 Interior Defense、Perimeter Defense、Menace 徽章加成
  - 不盲目起跳，最大程度压缩对手投篮命中率且杜绝被造投篮犯规
- **非线性阈值/边界**：顶级防守人（追梦/戈贝尔）给 90~98；防守散漫者 30~50。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B7)


### TENDENCY_NATIVE_097 · BLOCK_SHOT_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.BLOCK_SHOT_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b090` | 解码值 `60`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：迎面飞身起跳封盖投篮的激进倾向。
- **机制与跨字段关联**：
  - 与 Block 属性、Rim Protector 徽章强相关
  - 过高会导致一见假动作就起跳吃晃送犯规，必须与 Contest Shot 保持梯队平衡
- **非线性阈值/边界**：暴力盖帽王 80~90；纪律型护框大闸 60~75；地板流中锋 35~50。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B8)


### TENDENCY_NATIVE_098 · FOUL_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.FOUL_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b091` | 解码值 `34`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：常规防守战术犯规与阻滞快攻犯规的激进度。
- **机制与跨字段关联**：
  - 严格依据现实 PF/36 犯规率换算
  - 直接决定轮换被罚下风险与罚球赠送率
- **非线性阈值/边界**：控制在 25~45 之间可杜绝主力首发 5 分钟 2 犯离场。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4B9)


### TENDENCY_NATIVE_099 · HARD_FOUL_TENDENCY
- **家族与候选键**：`player_tendency` / `tendency.HARD_FOUL_TENDENCY`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_IN_ACTIVE_PLAYER)
- **内存地址与数值**：地址 `0x7ff4e4e9b092` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 HARD_FOUL_TENDENCY 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **审计说明**：Read uint8 from active player Tyrese Haliburton memory (offset 0x4BA)


### WORLD_REG_001 · settings.game_settings.quarter_length
- **家族与候选键**：`world_settings` / `settings.game_settings.quarter_length`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e68fe04c` | 解码值 `12`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[1, 12]
- **审计说明**：Observation 12 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_002 · settings.game_settings.game_speed
- **家族与候选键**：`world_settings` / `settings.game_settings.game_speed`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e68fe038` | 解码值 `0.5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.game_speed 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.5 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_003 · settings.game_settings.free_throw_difficulty
- **家族与候选键**：`world_settings` / `settings.game_settings.free_throw_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e68fe098` | 解码值 `0.5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.free_throw_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.5 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_004 · settings.game_settings.shot_clock
- **家族与候选键**：`world_settings` / `settings.game_settings.shot_clock`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e68fe0ac` | 解码值 `24`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.shot_clock 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[12, 60]
- **审计说明**：Observation 24 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_005 · settings.game_settings.foul_out
- **家族与候选键**：`world_settings` / `settings.game_settings.foul_out`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e68fe0d8` | 解码值 `6`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.foul_out 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[2, 8]
- **审计说明**：Observation 6 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_006 · settings.game_settings.injuries_enabled
- **家族与候选键**：`world_settings` / `settings.game_settings.injuries_enabled`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e68fe128` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.injuries_enabled 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 1 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_007 · settings.simulation.sim_quarter_length
- **家族与候选键**：`world_settings` / `settings.simulation.sim_quarter_length`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff2b8` | 解码值 `12`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.simulation.sim_quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[1, 12]
- **审计说明**：Observation 12 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_008 · settings.simulation.normalize_stats
- **家族与候选键**：`world_settings` / `settings.simulation.normalize_stats`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff804` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.simulation.normalize_stats 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_009 · settings.trade_rules.cpu_cpu_trades
- **家族与候选键**：`world_settings` / `settings.trade_rules.cpu_cpu_trades`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff374` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.cpu_cpu_trades 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_010 · settings.trade_rules.trade_override
- **家族与候选键**：`world_settings` / `settings.trade_rules.trade_override`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff36c` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.trade_override 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_011 · settings.trade_rules.trade_deadline
- **家族与候选键**：`world_settings` / `settings.trade_rules.trade_deadline`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff370` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.trade_deadline 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 1 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_012 · settings.trade_rules.financial_trade_rules
- **家族与候选键**：`world_settings` / `settings.trade_rules.financial_trade_rules`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff364` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.financial_trade_rules 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 1 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_013 · settings.trade_rules.recently_signed_rule
- **家族与候选键**：`world_settings` / `settings.trade_rules.recently_signed_rule`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff358` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.recently_signed_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 1 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_014 · settings.trade_rules.recently_traded_rule
- **家族与候选键**：`world_settings` / `settings.trade_rules.recently_traded_rule`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff35c` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.recently_traded_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 1 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_015 · settings.trade_rules.trade_difficulty
- **家族与候选键**：`world_settings` / `settings.trade_rules.trade_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff378` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.trade_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_016 · settings.trade_rules.cpu_trade_frequency
- **家族与候选键**：`world_settings` / `settings.trade_rules.cpu_trade_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff37c` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.cpu_trade_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 0 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_017 · settings.trade_rules.blockbuster_trade_frequency
- **家族与候选键**：`world_settings` / `settings.trade_rules.blockbuster_trade_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff380` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.blockbuster_trade_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_018 · settings.trade_rules.untouchable_threshold
- **家族与候选键**：`world_settings` / `settings.trade_rules.untouchable_threshold`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff388` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.untouchable_threshold 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_019 · settings.contracts.contract_difficulty
- **家族与候选键**：`world_settings` / `settings.contracts.contract_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff414` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.contract_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_020 · settings.contracts.player_non_financial_ambitions
- **家族与候选键**：`world_settings` / `settings.contracts.player_non_financial_ambitions`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff418` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_non_financial_ambitions 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_021 · settings.contracts.min_contract_rating
- **家族与候选键**：`world_settings` / `settings.contracts.min_contract_rating`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff41c` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.min_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[50, 99]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_022 · settings.contracts.max_contract_rating
- **家族与候选键**：`world_settings` / `settings.contracts.max_contract_rating`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (OUT_OF_BOUNDS_CHECK_FAILED: 40 not in [70, 99])
- **内存地址与数值**：地址 `0x7ff4e67ff420` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.max_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[70, 99]
- **审计说明**：Raw reading 40 violates declared range [70, 99]. Target belongs to SLOT_TRADE (0x0632B498) offset 0x21C, not SLOT_SETTINGS.


### WORLD_REG_023 · settings.contracts.player_potential_factor
- **家族与候选键**：`world_settings` / `settings.contracts.player_potential_factor`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff424` | 解码值 `60`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_potential_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 60 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_024 · settings.contracts.player_durability_factor
- **家族与候选键**：`world_settings` / `settings.contracts.player_durability_factor`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff428` | 解码值 `20`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_durability_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 20 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_025 · settings.contracts.player_fame_factor
- **家族与候选键**：`world_settings` / `settings.contracts.player_fame_factor`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff430` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_fame_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_026 · settings.contracts.cpu_interest_in_resigning
- **家族与候选键**：`world_settings` / `settings.contracts.cpu_interest_in_resigning`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff438` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.cpu_interest_in_resigning 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 0 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_027 · settings.injuries_and_morale.user_injury_frequency
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.user_injury_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff450` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.user_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_028 · settings.injuries_and_morale.cpu_injury_frequency
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.cpu_injury_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff454` | 解码值 `55`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.cpu_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 55 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_029 · settings.injuries_and_morale.user_injury_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.user_injury_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff458` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.user_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_030 · settings.injuries_and_morale.cpu_injury_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.cpu_injury_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff45c` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.cpu_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_031 · settings.injuries_and_morale.injury_severity
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.injury_severity`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff460` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.injury_severity 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 40 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_032 · settings.injuries_and_morale.injury_duration
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.injury_duration`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff464` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.injury_duration 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_033 · settings.injuries_and_morale.career_ending_injury_frequency
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.career_ending_injury_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff468` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.career_ending_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 5 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_034 · settings.injuries_and_morale.morale_difficulty
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.morale_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff43c` | 解码值 `35`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.morale_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 35 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_035 · settings.injuries_and_morale.morale_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.morale_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff440` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.morale_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 40 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_036 · settings.injuries_and_morale.chemistry_difficulty
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.chemistry_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff444` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.chemistry_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_037 · settings.injuries_and_morale.chemistry_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.chemistry_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff448` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.chemistry_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_038 · settings.progression.training_effects
- **家族与候选键**：`world_settings` / `settings.progression.training_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff46c` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.progression.training_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_039 · settings.progression.offseason_progression_rate
- **家族与候选键**：`world_settings` / `settings.progression.offseason_progression_rate`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff470` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.progression.offseason_progression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 0 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_040 · settings.progression.regression_rate
- **家族与候选键**：`world_settings` / `settings.progression.regression_rate`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff478` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.progression.regression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **审计说明**：Observation 50 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_041 · settings.gameplay_sliders.game_difficulty_preset
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.game_difficulty_preset`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ff95c` | 解码值 `4`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.game_difficulty_preset 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 4]
- **审计说明**：Observation 4 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_042 · settings.gameplay_sliders.speed_with_ball_min_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_min_user`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcd8` | 解码值 `0.4000000059604645`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_min_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.4000000059604645 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_043 · settings.gameplay_sliders.speed_with_ball_min_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_min_cpu`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcdc` | 解码值 `0.4000000059604645`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_min_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.4000000059604645 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_044 · settings.gameplay_sliders.speed_with_ball_max_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_max_user`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcd0` | 解码值 `0.699999988079071`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_max_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.699999988079071 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_045 · settings.gameplay_sliders.speed_with_ball_max_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_max_cpu`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcd4` | 解码值 `0.699999988079071`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_max_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.699999988079071 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_046 · settings.gameplay_sliders.acceleration_with_ball_min_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.acceleration_with_ball_min_user`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcf8` | 解码值 `0.4000000059604645`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.acceleration_with_ball_min_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.4000000059604645 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_047 · settings.gameplay_sliders.acceleration_with_ball_min_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.acceleration_with_ball_min_cpu`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcfc` | 解码值 `0.4000000059604645`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.acceleration_with_ball_min_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.4000000059604645 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_048 · settings.gameplay_sliders.speed_without_ball_min_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_without_ball_min_user`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffcc8` | 解码值 `0.3499999940395355`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_without_ball_min_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.3499999940395355 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_049 · settings.gameplay_sliders.speed_without_ball_min_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_without_ball_min_cpu`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE_IN_BOUNDS)
- **内存地址与数值**：地址 `0x7ff4e67ffccc` | 解码值 `0.3499999940395355`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_without_ball_min_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **审计说明**：Observation 0.3499999940395355 in bounds; retained as RAW_MEMORY_CAPTURE_CANDIDATE pending slot-specific UI readback.


### WORLD_REG_050 · world.trade_and_draft_rules.cpu_cpu_trades
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.cpu_cpu_trades`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff374` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.cpu_cpu_trades 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_051 · world.trade_and_draft_rules.cpu_trade_frequency
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.cpu_trade_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff37c` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.cpu_trade_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_052 · world.trade_and_draft_rules.ted_stepien_rule
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.ted_stepien_rule`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff384` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.ted_stepien_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_053 · world.trade_and_draft_rules.trade_override
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.trade_override`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff36c` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.trade_override 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_054 · world.trade_and_draft_rules.trade_deadline
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.trade_deadline`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff370` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.trade_deadline 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 1; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_055 · world.trade_and_draft_rules.financial_trade_rules
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.financial_trade_rules`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff364` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.financial_trade_rules 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 1; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_056 · world.trade_and_draft_rules.recently_signed_rule
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.recently_signed_rule`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff358` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.recently_signed_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 1; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_057 · world.trade_and_draft_rules.recently_traded_rule
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.recently_traded_rule`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff35c` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.recently_traded_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 1; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_058 · world.trade_and_draft_rules.trade_difficulty
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.trade_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff378` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.trade_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_059 · world.contracts_and_finances.cpu_interest_in_resigning
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.cpu_interest_in_resigning`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff438` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.cpu_interest_in_resigning 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_060 · world.contracts_and_finances.contract_difficulty
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.contract_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff414` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.contract_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_061 · world.contracts_and_finances.player_non_financial_ambitions
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_non_financial_ambitions`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff418` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_non_financial_ambitions 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_062 · world.contracts_and_finances.min_contract_rating
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.min_contract_rating`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff41c` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.min_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_063 · world.contracts_and_finances.max_contract_rating
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.max_contract_rating`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff420` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.max_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 40; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_064 · world.contracts_and_finances.player_potential_factor
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_potential_factor`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff424` | 解码值 `60`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_potential_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 60; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_065 · world.contracts_and_finances.player_durability_factor
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_durability_factor`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff428` | 解码值 `20`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_durability_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 20; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_066 · world.contracts_and_finances.player_fame_factor
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_fame_factor`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff430` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_fame_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_067 · world.progression_and_regression.offseason_progression_rate
- **家族与候选键**：`world_settings` / `world.progression_and_regression.offseason_progression_rate`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff470` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.progression_and_regression.offseason_progression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_068 · world.progression_and_regression.regression_rate
- **家族与候选键**：`world_settings` / `world.progression_and_regression.regression_rate`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff478` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.progression_and_regression.regression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_069 · world.progression_and_regression.training_effects
- **家族与候选键**：`world_settings` / `world.progression_and_regression.training_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff46c` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.progression_and_regression.training_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_070 · world.injuries_and_morale.user_injury_frequency
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.user_injury_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff450` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.user_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_071 · world.injuries_and_morale.cpu_injury_frequency
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.cpu_injury_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff454` | 解码值 `55`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.cpu_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 55; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_072 · world.injuries_and_morale.user_injury_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.user_injury_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff458` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.user_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_073 · world.injuries_and_morale.cpu_injury_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.cpu_injury_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff45c` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.cpu_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_074 · world.injuries_and_morale.injury_severity
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.injury_severity`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff460` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.injury_severity 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 40; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_075 · world.injuries_and_morale.injury_duration
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.injury_duration`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff464` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.injury_duration 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_076 · world.injuries_and_morale.career_ending_injury_frequency
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.career_ending_injury_frequency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff468` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.career_ending_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 5; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_077 · world.injuries_and_morale.morale_difficulty
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.morale_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff43c` | 解码值 `35`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.morale_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 35; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_078 · world.injuries_and_morale.morale_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.morale_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff440` | 解码值 `40`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.morale_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 40; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_079 · world.injuries_and_morale.chemistry_difficulty
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.chemistry_difficulty`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff444` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.chemistry_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_080 · world.injuries_and_morale.chemistry_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.chemistry_effects`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff448` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.chemistry_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 50; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_081 · world.injuries_and_morale.injuries_enabled
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.injuries_enabled`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e68fe128` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.injuries_enabled 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 1; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_082 · world.gameplay_and_calendar.quarter_length
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.quarter_length`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e68fe04c` | 解码值 `12`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 12; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_083 · world.gameplay_and_calendar.sim_quarter_length
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.sim_quarter_length`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff2b8` | 解码值 `12`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.sim_quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 12; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_084 · world.gameplay_and_calendar.normalize_stats
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.normalize_stats`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff804` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.normalize_stats 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_085 · world.gameplay_and_calendar.game_difficulty_preset
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.game_difficulty_preset`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e67ff95c` | 解码值 `4`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.game_difficulty_preset 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 4; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### WORLD_REG_086 · world.gameplay_and_calendar.game_speed
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.game_speed`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `EVIDENCE_ADDED` (UNVERIFIED_LEGACY_RAW_CAPTURE)
- **内存地址与数值**：地址 `0x7ff4e68fe038` | 解码值 `0.5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.game_speed 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **审计说明**：Raw observation 0.5; unconstrained range; retained as RAW_MEMORY_CAPTURE_CANDIDATE.


### COACH_DEFAULT_001 · POEOffense
- **家族与候选键**：`coach_settings` / `POEOffense`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742129c` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 POEOffense 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 5 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_002 · POEOffense2
- **家族与候选键**：`coach_settings` / `POEOffense2`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742129c` | 解码值 `8`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 POEOffense2 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 8 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_003 · POEOffense3
- **家族与候选键**：`coach_settings` / `POEOffense3`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742129c` | 解码值 `11`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 POEOffense3 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 11 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_004 · POEDefense
- **家族与候选键**：`coach_settings` / `POEDefense`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742129c` | 解码值 `14`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 POEDefense 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 14 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_005 · POEDefense2
- **家族与候选键**：`coach_settings` / `POEDefense2`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742129c` | 解码值 `17`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 POEDefense2 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 17 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_006 · POEDefense3
- **家族与候选键**：`coach_settings` / `POEDefense3`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742129c` | 解码值 `20`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 POEDefense3 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 20 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_007 · PreferredSystem
- **家族与候选键**：`coach_settings` / `PreferredSystem`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e7421268` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 PreferredSystem 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 1 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_008 · ActiveSystem
- **家族与候选键**：`coach_settings` / `ActiveSystem`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e7421268` | 解码值 `4`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 ActiveSystem 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 4 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_009 · PlaybookID
- **家族与候选键**：`coach_settings` / `PlaybookID`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e7421268` | 解码值 `0`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 PlaybookID 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 0 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_010 · BenchDepth
- **家族与候选键**：`coach_settings` / `BenchDepth`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742123e` | 解码值 `11`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 BenchDepth 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 11 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_011 · RunPlayTendency
- **家族与候选键**：`coach_settings` / `RunPlayTendency`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e7421240` | 解码值 `70`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 RunPlayTendency 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 70 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_012 · ZoneUsage
- **家族与候选键**：`coach_settings` / `ZoneUsage`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e7421242` | 解码值 `1`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 ZoneUsage 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 1 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_013 · BenchUtilization
- **家族与候选键**：`coach_settings` / `BenchUtilization`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e7421298` | 解码值 `60`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 BenchUtilization 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 60 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_014 · Tempo
- **家族与候选键**：`coach_settings` / `Tempo`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e74212a8` | 解码值 `80`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 Tempo 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 80 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_015 · HelpDefense
- **家族与候选键**：`coach_settings` / `HelpDefense`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e74212a8` | 解码值 `50`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 HelpDefense 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 50 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_016 · FreelanceType
- **家族与候选键**：`coach_settings` / `FreelanceType`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e742125c` | 解码值 `5`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 FreelanceType 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 5 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_017 · FreelanceType2
- **家族与候选键**：`coach_settings` / `FreelanceType2`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e74212a8` | 解码值 `3`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 FreelanceType2 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 3 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_018 · FreelanceType3
- **家族与候选键**：`coach_settings` / `FreelanceType3`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e74212bc` | 解码值 `18`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 FreelanceType3 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 18 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.


### COACH_DEFAULT_019 · FreelanceType4
- **家族与候选键**：`coach_settings` / `FreelanceType4`
- **证据等级与状态**：`RAW_MEMORY_CAPTURE_CANDIDATE` | `UNKNOWN` (INVALID_COACH_STRUCTURE_BASE_TEAM_ALIAS)
- **内存地址与数值**：地址 `0x7ff4e74212bc` | 解码值 `28`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（尚未在受控实机实验中获得因果验证）
- **字段作用与影响**：控制教练战术体系中 FreelanceType4 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **审计说明**：Team structure address was used as GAMEPLAN base address. COACHDATA RVA layout requires coach_codec bitfield decoding. Value 28 demoted to RAW_MEMORY_CAPTURE_CANDIDATE pending verified COACHDATA readback.
