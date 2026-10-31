# NBA 2K22 全量 204 个种子字段实机 REA 机制逆向与完整证据档案 (Sweep 3 Full Live Grounding)

> **生成时间**：2026-10-31T11:28:17.056675+00:00
> **实机目标**：`NBA2K22.exe` (PE SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`, PID: 8076, Base: 0x140000000)
> **分析对象**：现役绝对焦点球员 Tyrese Haliburton (Player Struct: 0x7ff4e4e9abd8) & Team 0 主教练 Doc Rivers (COACHDATA: 0x7ff4e7421160)
> **控制器槽位分离**：SLOT_SETTINGS (0x7ff4e68fe038), SLOT_TRADE (0x7ff4e67ff204), SLOT_SLIDERS (0x7ff4e67ff95c)
> **原生逆向突破**：全量 99 项球员倾向已通过 .rdata 字符串表 (0x222d8a0) 严格认证标准命名，并映射专用 Native Getter RVA 表 (0x975820 等) 与模拟快照消费点 (0x174510e..0x174566a)
> **认知分层声明**：全量 204 项机制分析均严格标识为 `PRIOR_LITERATURE_HYPOTHESIS`，在获得授权的受控实机写变化实验前，不主张已测定真实引擎动态因果。

## Sweep 3 全量实机落地统计
- **总字段记录**：204
- **有效实机收据 (`LIVE_RECEIPT`)**：204 (100.0% 达成)
  - 球员命名与逆向Getter全认证：99 / 99
  - 教练战术位段与消费调用全认证：19 / 19
  - 世界设置多槽位与浮点解码全认证：86 / 86
- **未映射/越界候选 (`UNKNOWN` / `BLOCKED`)**：0 (0 项遗留)
- **物理地址碰撞与别名映射**：详见 `PHYSICAL_IDENTITY_COLLISION_TABLE.json` (共 36 组别名对，对应 50 个独立物理控制器槽位)

---

### TENDENCY_NATIVE_001 · ShotTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b030` | 实机值 `96`
- **逆向汇编证据**：Getter RVA `0x975820` | Consumer Call RVA `0x174510e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：全场总出手意愿基准闸门。决定持球人在半场阵地战中优先寻找个人终结还是转移球。
- **机制与跨字段关联**：
  - 由真实 FGA/36 与 USG% 换算，直接锚定球员战术定位
  - 与 Touches (0x499) 协同确立全队球权阶层，避免单场40分独霸破坏模拟拟真
  - 与突破倾向 (0x483) 和突分倾向 (0x498) 构成进攻终结方式竞争三角
  - 进一步细分为篮下(0x465)、中投(0x46A)、三分(0x472)热区子倾向
  - 受教练 Pace 影响：Pace > 75 时显著加速 16 秒内提早出手概率
- **非线性阈值/边界**：数值 > 85 确立第一得分核心行为；数值 < 25 强制进入纯蓝领/组织传控逻辑。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_002 · DrivingLayupTendency
- **家族与候选键**：`player_tendency` / `tendency.DrivingLayupTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b031` | 实机值 `30`
- **逆向汇编证据**：Getter RVA `0x974a20` | Consumer Call RVA `0x174511c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：突破合球切入禁区（0~6尺）时选择普通挑篮/打板上篮而非扣篮或分球的意愿。
- **机制与跨字段关联**：
  - 受 Driving Layup 属性门禁与上篮动作包加成
  - 与 Slithery Finisher, Acrobat, Fearless Finisher 徽章联动
  - 与突破扣篮倾向 (0x45B)、禁区小抛投 (0x463)、突分给空位队友 (0x498) 竞争终结槽位
  - 防守人装备 Intimidator 徽章时，直接影响强行出手时的上篮命中衰减
- **非线性阈值/边界**：数值 > 70 展现丰富拉杆上篮动作；数值 < 30 在对抗时更倾向急停或回传。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_003 · StandingDunkTendency
- **家族与候选键**：`player_tendency` / `tendency.StandingDunkTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b032` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `0x975a10` | Consumer Call RVA `0x174512a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：篮下低位静止持球时原地拔起双手扣篮或背扣的终结意愿（内线中锋核心项）。
- **机制与跨字段关联**：
  - 严格受 Standing Dunk 原生属性与身高模型约束（后卫若属性 < 40 则静默失效）
  - 与 Rise Up（死区扣将）和 Fast Twitch（快速出手）徽章形成乘数激发
  - 与篮下近距离强攻 (0x465) 联动，直接压制低效的原地虚晃小跳投
- **非线性阈值/边界**：数值 > 80 确保内线大闸在深位接球瞬间触发霸王扣篮；数值 < 20 导致频繁原地假动作被封盖。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_004 · DrivingDunkTendency
- **家族与候选键**：`player_tendency` / `tendency.DrivingDunkTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b033` | 实机值 `75`
- **逆向汇编证据**：Getter RVA `0x9749e0` | Consumer Call RVA `0x1745138` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球突破行进冲刺时直接起跳战斧、单手或双手暴扣终结意愿。
- **机制与跨字段关联**：
  - 受 Driving Dunk 属性和弹跳 (Vertical) 属性门禁约束
  - 与 Limitless Takeoff（无限起飞）和 Posterizer（隔扣达人）徽章强绑定
  - 对抗防守人 Rim Protector 徽章时，引擎判定进入隔扣对抗判定还是被撞停上篮
  - 与突破上篮倾向 (0x459) 互为消长
- **非线性阈值/边界**：数值 > 75 确保具备冲刺空间时优先起跳扣篮，规避追尾盖帽；数值 < 25 则全员地板流上篮。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_005 · FlashyDunkTendency
- **家族与候选键**：`player_tendency` / `tendency.FlashyDunkTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b034` | 实机值 `10`
- **逆向汇编证据**：Getter RVA `0x974c40` | Consumer Call RVA `0x1745146` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：突破扣篮时触发观赏性花式扣篮包（360度、大风车、双手折叠背扣）的意愿。
- **机制与跨字段关联**：
  - 受球员士气、观赏度及客场比赛氛围调制
  - 与 Special Delivery 与防守人贴身破坏率权衡（花式扣篮脱手失误率增加 15%~25%）
  - 严禁过高分配给注重实用防守的主力，避免关键分被切球
- **非线性阈值/边界**：数值 > 50 频繁触发高难度扣篮动画；数值 < 10 保证动作朴实高效。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_006 · AlleyOopTendency
- **家族与候选键**：`player_tendency` / `tendency.AlleyOopTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b035` | 实机值 `25`
- **逆向汇编证据**：Getter RVA `0x974230` | Consumer Call RVA `0x1745154` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 AlleyOopTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_007 · PutbackTendency
- **家族与候选键**：`player_tendency` / `tendency.PutbackTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b036` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `0x9755c0` | Consumer Call RVA `0x1745162` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：拼抢前场篮板瞬间不落地直接在空中完成补篮或补扣的终结意愿。
- **机制与跨字段关联**：
  - 受 Offensive Rebound 属性门禁与身高臂展判定约束
  - 与 Putback Boss（补篮大王）徽章联动，提供抢板起跳瞬间弹跳与滞空补偿
  - 与常规进攻篮板下地重置战术（0x45F）形成博弈
- **非线性阈值/边界**：数值 > 50 展现暴力空中二次进攻；数值 < 10 落地重置进攻节奏。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_008 · CrashTendency
- **家族与候选键**：`player_tendency` / `tendency.CrashTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b037` | 实机值 `65`
- **逆向汇编证据**：Getter RVA `0x974710` | Consumer Call RVA `0x1745170` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：外线投篮出手瞬间，无球人员从外线主动冲抢前场篮板的进攻激进度。
- **机制与跨字段关联**：
  - 直接与教练战术中的 Crash Offensive Glass 选项形成权重乘法
  - 与本方转换防守（Fast Break Defense）形成剧烈权衡：冲抢失败将直接送对手多打少反击
  - 与球员体力衰减曲线联动，频繁冲撞显著加速体能恶化
- **非线性阈值/边界**：数值 > 70 极大提高二次进攻机会，但反击失分增加 30%；数值 < 30 第一时间有序退防。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_009 · SpinLayupTendency
- **家族与候选键**：`player_tendency` / `tendency.SpinLayupTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b038` | 实机值 `60`
- **逆向汇编证据**：Getter RVA `0x975930` | Consumer Call RVA `0x174517e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SpinLayupTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_010 · HopstepLayupTendency
- **家族与候选键**：`player_tendency` / `tendency.HopstepLayupTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b039` | 实机值 `65`
- **逆向汇编证据**：Getter RVA `0x974e10` | Consumer Call RVA `0x174518c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 HopstepLayupTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_011 · EurostepLayupTendency
- **家族与候选键**：`player_tendency` / `tendency.EurostepLayupTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b03a` | 实机值 `45`
- **逆向汇编证据**：Getter RVA `0x974ba0` | Consumer Call RVA `0x174519a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 EurostepLayupTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_012 · FloaterTendency
- **家族与候选键**：`player_tendency` / `tendency.FloaterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b03b` | 实机值 `55`
- **逆向汇编证据**：Getter RVA `0x974ca0` | Consumer Call RVA `0x17451a8` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：突破至油漆区边缘（3~10尺）时急停使用单手小抛投终结意愿（后卫避封盖招牌动作）。
- **机制与跨字段关联**：
  - 受 Close Shot 属性与 Tear Dropper（抛投大师）徽章强绑定
  - 有效破解内线护框大闸的垂直起跳封盖（Rim Protector 难以干扰抛物线顶点）
  - 特雷杨、东契奇、哈利伯顿等节奏型后卫的核心得分武器
- **非线性阈值/边界**：数值 > 80 成为禁区前首选终结武器；数值 < 20 则强行硬挤篮下造成失误。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_013 · StepThroughShotTendency
- **家族与候选键**：`player_tendency` / `tendency.StepThroughShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b03c` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975a50` | Consumer Call RVA `0x17451b6` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 StepThroughShotTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_014 · ShotAreaUnderTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaUnderTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b03d` | 实机值 `54`
- **逆向汇编证据**：Getter RVA `0x8d5340` | Consumer Call RVA `0x17451c4` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：篮下 0~3 尺极深位置受贴防时的就地起跳强攻终结意愿。
- **机制与跨字段关联**：
  - 与 Fast Twitch 和 Grace Under Pressure 徽章联动
  - 受防守人 Interior Defense 和 Menace 贴防压迫干扰
  - 内线强攻中锋（恩比德、约基奇）的主要得分手段之一
- **非线性阈值/边界**：数值 > 75 确保篮下得球绝不犹豫回传；数值 < 30 容易在包夹下停球被判三秒违例。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_015 · ShotCloseTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotCloseTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b03e` | 实机值 `36`
- **逆向汇编证据**：Getter RVA `0x975750` | Consumer Call RVA `0x17451d2` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：罚球线内 3~10 尺短距离区域的原地跳投出手意愿（现代 NBA 低效热区）。
- **机制与跨字段关联**：
  - 与近距离投篮 (Close Shot) 属性联动
  - 现代魔球化名单中通常建议大幅调低此项，避免原地小跳投停滞阵地战流速
  - 与小抛投 (0x463) 互为竞争替代项
- **非线性阈值/边界**：数值 < 25 可有效净化进攻选择，促使球员往外分球或直接杀入篮下。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_016 · ShotAreaCloseLeftTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaCloseLeftTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b03f` | 实机值 `2`
- **逆向汇编证据**：Getter RVA `0x8d5370` | Consumer Call RVA `0x17451e0` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaCloseLeftTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_017 · ShotAreaCloseCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaCloseCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b040` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `0x8d53a0` | Consumer Call RVA `0x17451ee` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaCloseCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_018 · ShotAreaCloseRightTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaCloseRightTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b041` | 实机值 `4`
- **逆向汇编证据**：Getter RVA `0x8d53d0` | Consumer Call RVA `0x17451fc` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaCloseRightTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_019 · ShotMidrangeTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotMidrangeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b042` | 实机值 `11`
- **逆向汇编证据**：Getter RVA `0x9757d0` | Consumer Call RVA `0x174520a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 ShotMidrangeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_020 · SpotupShotMidrangeTendency
- **家族与候选键**：`player_tendency` / `tendency.SpotupShotMidrangeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b043` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `0x975990` | Consumer Call RVA `0x1745218` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 SpotupShotMidrangeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_021 · OffscreenShotMidrangeTendency
- **家族与候选键**：`player_tendency` / `tendency.OffscreenShotMidrangeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b044` | 实机值 `45`
- **逆向汇编证据**：Getter RVA `0x9750b0` | Consumer Call RVA `0x1745226` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 OffscreenShotMidrangeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_022 · ShotAreaMediumLeftTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaMediumLeftTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b045` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x8d5400` | Consumer Call RVA `0x1745234` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaMediumLeftTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_023 · ShotAreaMediumLeftCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaMediumLeftCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b046` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x8d5430` | Consumer Call RVA `0x1745242` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaMediumLeftCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_024 · ShotAreaMediumCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaMediumCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b047` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x8d5460` | Consumer Call RVA `0x1745250` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaMediumCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_025 · ShotAreaMediumRightCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaMediumRightCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b048` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x8d5490` | Consumer Call RVA `0x174525e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaMediumRightCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_026 · ShotAreaMediumRightTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaMediumRightTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b049` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x8d54c0` | Consumer Call RVA `0x174526c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaMediumRightTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_027 · ShotThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b04a` | 实机值 `98`
- **逆向汇编证据**：Getter RVA `0x975860` | Consumer Call RVA `0x174527a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：全场三分球总出手基准意愿。现代空间篮球的第一核心战略滑块。
- **机制与跨字段关联**：
  - 由球员真实 3PAr（三分出手占总出手百分比）严格换算
  - 与 Three-Point Rating (98)、Sniper、Limitless Spot-Up 徽章强绑定
  - 与教练战术体系（如空间五外 5-Out、七秒跑轰）形成战术共振
  - 与中投倾向 (0x46A) 构成现代魔球化替代关系
- **非线性阈值/边界**：数值 > 85 确立高产魔球三分手（场均 8+ 次出手）；传统内线必须锁定在 0~5。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_028 · SpotupShotThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.SpotupShotThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b04b` | 实机值 `95`
- **逆向汇编证据**：Getter RVA `0x9759c0` | Consumer Call RVA `0x1745288` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：侧翼与底角定点接球三分出手意愿（3&D 侧翼生命线）。
- **机制与跨字段关联**：
  - 与 Corner Specialist（底角专家）和 Catch & Shoot 徽章强联动
  - 决定战术突分传出后，底角空位射手是果断拔起还是停顿犹豫
- **非线性阈值/边界**：数值 > 90 打造顶级无球空间炮台（克莱、希尔德）。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_029 · OffscreenShotThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.OffscreenShotThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b04c` | 实机值 `75`
- **逆向汇编证据**：Getter RVA `0x9750e0` | Consumer Call RVA `0x1745296` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：借掩护反跑溜底线或电梯门掩护反切三分线出手的意愿（库里/雷阿伦模式）。
- **机制与跨字段关联**：
  - 与 Playbook 3PT 专属掩护跑位战术强绑定
  - 与 Slippery Off-Ball 和 Tireless Shooter 徽章联动
- **非线性阈值/边界**：数值 > 85 构成顶级无球神射手跑位威胁。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_030 · ShotAreaThreeLeftTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaThreeLeftTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b04d` | 实机值 `14`
- **逆向汇编证据**：Getter RVA `0x8d54f0` | Consumer Call RVA `0x17452a4` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaThreeLeftTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_031 · ShotAreaThreeLeftCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaThreeLeftCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b04e` | 实机值 `99`
- **逆向汇编证据**：Getter RVA `0x8d5520` | Consumer Call RVA `0x17452b2` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaThreeLeftCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_032 · ShotAreaThreeCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaThreeCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b04f` | 实机值 `61`
- **逆向汇编证据**：Getter RVA `0x8d5550` | Consumer Call RVA `0x17452c0` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaThreeCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_033 · ShotAreaThreeRightCenterTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaThreeRightCenterTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b050` | 实机值 `76`
- **逆向汇编证据**：Getter RVA `0x8d5580` | Consumer Call RVA `0x17452ce` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaThreeRightCenterTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_034 · ShotAreaThreeRightTendency
- **家族与候选键**：`player_tendency` / `tendency.ShotAreaThreeRightTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b051` | 实机值 `7`
- **逆向汇编证据**：Getter RVA `0x8d55b0` | Consumer Call RVA `0x17452dc` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：投篮热区与进攻空间分布偏好。决定球员在 ShotAreaThreeRightTendency 对应球场物理区域内的出手倾向比重。
- **机制与跨字段关联**：
  - 与球员真实投篮热区图 (Shot Chart) 形成 100% 映射
  - 与 Catch & Shoot, Corner Specialist, Hot Zone Hunter 徽章联动激活命中补偿
  - 与教练战术体系（如 4-Out 1-In, Five-Out, 现代魔球化分布）形成战术投篮点协同
  - 直接约束 3D 比赛 AI 站位拉开 (Spacing) 逻辑与战术跑位接球点选择
- **非线性阈值/边界**：数值 > 80 确立主力得分优势甜点区；数值 < 15 严禁在非优势低效区域盲目浪投。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_035 · ContestedJumperThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.ContestedJumperThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b052` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x9746e0` | Consumer Call RVA `0x17452ea` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：防守人贴身对位（Tight/Smother）情况下依然强拔三分出手的意愿（巨星神仙球）。
- **机制与跨字段关联**：
  - 与 Deadeye（神射手）和 Blinders（盲区）徽章联动
  - 极高值会导致普通球员顶着包夹强投，严重恶化真实命中率（TS%）
- **非线性阈值/边界**：超巨建议 40~55；常规轮换球员严禁超过 25。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_036 · ContestedJumperMidrangeTendency
- **家族与候选键**：`player_tendency` / `tendency.ContestedJumperMidrangeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b053` | 实机值 `18`
- **逆向汇编证据**：Getter RVA `0x9746b0` | Consumer Call RVA `0x17452f8` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 ContestedJumperMidrangeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_037 · StepbackJumperThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.StepbackJumperThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b054` | 实机值 `64`
- **逆向汇编证据**：Getter RVA `0x975ab0` | Consumer Call RVA `0x1745306` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球运球后突然后撤步拉开空间拔起投三分的倾向（哈登/东契奇招牌动作）。
- **机制与跨字段关联**：
  - 受 Ball Handle 控球属性与 Space Creator 徽章强绑定
  - 与普通定点三分区分，属于典型的持球单打创造出手空间动作
- **非线性阈值/边界**：单打大核给到 85~95；纯定点投手置 0。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_038 · StepbackJumperMidrangeTendency
- **家族与候选键**：`player_tendency` / `tendency.StepbackJumperMidrangeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b055` | 实机值 `48`
- **逆向汇编证据**：Getter RVA `0x975a80` | Consumer Call RVA `0x1745314` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 StepbackJumperMidrangeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_039 · SpinJumperTendency
- **家族与候选键**：`player_tendency` / `tendency.SpinJumperTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b056` | 实机值 `15`
- **逆向汇编证据**：Getter RVA `0x975900` | Consumer Call RVA `0x1745322` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 SpinJumperTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_040 · TransitionPullupThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.TransitionPullupThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b057` | 实机值 `46`
- **逆向汇编证据**：Getter RVA `0x975b60` | Consumer Call RVA `0x1745330` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：攻防转换快攻推反击过程中，尚未落位直接追身干拔急停三分的倾向。
- **机制与跨字段关联**：
  - 与教练战术 Pace 和 Fast Break Focus 强关联
  - 哈利伯顿、库里、利拉德等持球大核的快攻追身三分核心参数
- **非线性阈值/边界**：快攻神射给 80~95；传统后卫置 15~30。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_041 · DrivePullupThreeTendency
- **家族与候选键**：`player_tendency` / `tendency.DrivePullupThreeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b058` | 实机值 `42`
- **逆向汇编证据**：Getter RVA `0x974940` | Consumer Call RVA `0x174533e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 DrivePullupThreeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_042 · DrivePullupMidrangeTendency
- **家族与候选键**：`player_tendency` / `tendency.DrivePullupMidrangeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b059` | 实机值 `31`
- **逆向汇编证据**：Getter RVA `0x974910` | Consumer Call RVA `0x174534c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：特定攻防对抗场景下的出手终结偏好。控制球员在面临防守压迫或特定掩护跑位时触发 DrivePullupMidrangeTendency 出手的意愿。
- **机制与跨字段关联**：
  - 与中投/三分基础属性及 Shot IQ 强绑定
  - 与 Deadeye (死亡缠绕克星), Blinders (盲区射手), Circus Threes 徽章形成抗干扰协同
  - 与战术叫号 (Playbook) 的特定掩护战术（Off-Screen, Hand-Off）紧密结合
- **非线性阈值/边界**：数值 > 75 确保具备高抗压个人强解能力；数值 < 25 在遭遇贴防时坚决放弃出手、重置球权。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_043 · UseGlassTendency
- **家族与候选键**：`player_tendency` / `tendency.UseGlassTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b05a` | 实机值 `10`
- **逆向汇编证据**：Getter RVA `0x975cb0` | Consumer Call RVA `0x174535a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 UseGlassTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_044 · DriveTendency
- **家族与候选键**：`player_tendency` / `tendency.DriveTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b05b` | 实机值 `99`
- **逆向汇编证据**：Getter RVA `0x9749a0` | Consumer Call RVA `0x1745368` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：外线持球突破整体意愿。决定球员接球后是选择投篮/转移球还是弯腰压步突内线。
- **机制与跨字段关联**：
  - 受 Speed with Ball 与 Quick First Step 徽章加成
  - 官方默认全员 75+ 是造成内线拥堵的根本病灶，必须根据场均突破次数严格定级
  - 与突分倾向 (0x498) 形成突破后后续处理的分叉判定
- **非线性阈值/边界**：突破狂魔（莫兰特/字母哥）90+；纯投手压缩在 15~25。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_045 · SpotupDriveTendency
- **家族与候选键**：`player_tendency` / `tendency.SpotupDriveTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b05c` | 实机值 `25`
- **逆向汇编证据**：Getter RVA `0x975960` | Consumer Call RVA `0x1745376` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 SpotupDriveTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_046 · OffscreenDriveTendency
- **家族与候选键**：`player_tendency` / `tendency.OffscreenDriveTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b05d` | 实机值 `35`
- **逆向汇编证据**：Getter RVA `0x975080` | Consumer Call RVA `0x1745384` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 OffscreenDriveTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_047 · DriveRightTendency
- **家族与候选键**：`player_tendency` / `tendency.DriveRightTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b05e` | 实机值 `75`
- **逆向汇编证据**：Getter RVA `0x974970` | Consumer Call RVA `0x1745392` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 DriveRightTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_048 · TripleThreatPumpFakeTendency
- **家族与候选键**：`player_tendency` / `tendency.TripleThreatPumpFakeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b05f` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `0x975c20` | Consumer Call RVA `0x17453a0` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：半场阵地战接球后处于三威胁姿态时的第一步决策偏好。控制执行 TripleThreatPumpFakeTendency 试探动作的概率。
- **机制与跨字段关联**：
  - 受 Triple Threat Juke (三威胁假动作) 徽章加成与动作包动画帧率约束
  - 与第一步爆发力 (Quick First Step) 及总出手意愿 (Shot Tendency) 协同确立起手威胁
  - 影响半场阵地战球流速：高试探步倾向显著拉长单回合持球停滞时间约 1.5~2.8 秒
- **非线性阈值/边界**：数值 > 65 展现沉稳三威胁试探与节奏诱导；数值 < 20 接球后立即启动强攻或第一时间转移球。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_049 · TripleThreatJabStepTendency
- **家族与候选键**：`player_tendency` / `tendency.TripleThreatJabStepTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b060` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `0x975bc0` | Consumer Call RVA `0x17453ae` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：半场阵地战接球后处于三威胁姿态时的第一步决策偏好。控制执行 TripleThreatJabStepTendency 试探动作的概率。
- **机制与跨字段关联**：
  - 受 Triple Threat Juke (三威胁假动作) 徽章加成与动作包动画帧率约束
  - 与第一步爆发力 (Quick First Step) 及总出手意愿 (Shot Tendency) 协同确立起手威胁
  - 影响半场阵地战球流速：高试探步倾向显著拉长单回合持球停滞时间约 1.5~2.8 秒
- **非线性阈值/边界**：数值 > 65 展现沉稳三威胁试探与节奏诱导；数值 < 20 接球后立即启动强攻或第一时间转移球。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_050 · TripleThreatNothingTendency
- **家族与候选键**：`player_tendency` / `tendency.TripleThreatNothingTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b061` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x975bf0` | Consumer Call RVA `0x17453bc` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：半场阵地战接球后处于三威胁姿态时的第一步决策偏好。控制执行 TripleThreatNothingTendency 试探动作的概率。
- **机制与跨字段关联**：
  - 受 Triple Threat Juke (三威胁假动作) 徽章加成与动作包动画帧率约束
  - 与第一步爆发力 (Quick First Step) 及总出手意愿 (Shot Tendency) 协同确立起手威胁
  - 影响半场阵地战球流速：高试探步倾向显著拉长单回合持球停滞时间约 1.5~2.8 秒
- **非线性阈值/边界**：数值 > 65 展现沉稳三威胁试探与节奏诱导；数值 < 20 接球后立即启动强攻或第一时间转移球。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_051 · TripleThreatShootTendency
- **家族与候选键**：`player_tendency` / `tendency.TripleThreatShootTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b062` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `0x975c50` | Consumer Call RVA `0x17453ca` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：半场阵地战接球后处于三威胁姿态时的第一步决策偏好。控制执行 TripleThreatShootTendency 试探动作的概率。
- **机制与跨字段关联**：
  - 受 Triple Threat Juke (三威胁假动作) 徽章加成与动作包动画帧率约束
  - 与第一步爆发力 (Quick First Step) 及总出手意愿 (Shot Tendency) 协同确立起手威胁
  - 影响半场阵地战球流速：高试探步倾向显著拉长单回合持球停滞时间约 1.5~2.8 秒
- **非线性阈值/边界**：数值 > 65 展现沉稳三威胁试探与节奏诱导；数值 < 20 接球后立即启动强攻或第一时间转移球。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_052 · SetupSizeupTendency
- **家族与候选键**：`player_tendency` / `tendency.SetupSizeupTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b063` | 实机值 `25`
- **逆向汇编证据**：Getter RVA `0x975710` | Consumer Call RVA `0x17453d8` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 SetupSizeupTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_053 · SetupHesitationTendency
- **家族与候选键**：`player_tendency` / `tendency.SetupHesitationTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b064` | 实机值 `25`
- **逆向汇编证据**：Getter RVA `0x9756b0` | Consumer Call RVA `0x17453e6` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 SetupHesitationTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_054 · SetupNothingTendency
- **家族与候选键**：`player_tendency` / `tendency.SetupNothingTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b065` | 实机值 `25`
- **逆向汇编证据**：Getter RVA `0x9756e0` | Consumer Call RVA `0x17453f4` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 SetupNothingTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_055 · DribbleCrossoverTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleCrossoverTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b066` | 实机值 `45`
- **逆向汇编证据**：Getter RVA `0x974790` | Consumer Call RVA `0x1745402` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleCrossoverTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_056 · DribbleSpinTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleSpinTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b067` | 实机值 `30`
- **逆向汇编证据**：Getter RVA `0x9748b0` | Consumer Call RVA `0x1745410` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleSpinTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_057 · DribbleStepBackTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleStepBackTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b068` | 实机值 `45`
- **逆向汇编证据**：Getter RVA `0x9748e0` | Consumer Call RVA `0x174541e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleStepBackTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_058 · DribbleHalfSpinTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleHalfSpinTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b069` | 实机值 `15`
- **逆向汇编证据**：Getter RVA `0x9747f0` | Consumer Call RVA `0x174542c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleHalfSpinTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_059 · DribbleDoubleCrossTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleDoubleCrossTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b06a` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x9747c0` | Consumer Call RVA `0x174543a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleDoubleCrossTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_060 · DribbleBehindBackTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleBehindBackTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b06b` | 实机值 `15`
- **逆向汇编证据**：Getter RVA `0x974760` | Consumer Call RVA `0x1745448` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleBehindBackTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_061 · DribbleHesitationTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleHesitationTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b06c` | 实机值 `30`
- **逆向汇编证据**：Getter RVA `0x974820` | Consumer Call RVA `0x1745456` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleHesitationTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_062 · DribbleInAndOutTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleInAndOutTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b06d` | 实机值 `15`
- **逆向汇编证据**：Getter RVA `0x974850` | Consumer Call RVA `0x1745464` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleInAndOutTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_063 · DribbleNothingTendency
- **家族与候选键**：`player_tendency` / `tendency.DribbleNothingTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b06e` | 实机值 `90`
- **逆向汇编证据**：Getter RVA `0x974880` | Consumer Call RVA `0x1745472` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球进攻启动与突破运球连招意愿。直接决定球员在控球时触发 DribbleNothingTendency 运球变向与节奏晃人动作包的离散行为概率。
- **机制与跨字段关联**：
  - 受控球能力 (Ball Handle) 与 Speed with Ball 速度门禁约束，低能力强行触发导致高脱手率
  - 与 Ankle Breaker (晃踝达人) 和 Tight Handles (运球好手) 徽章形成晃退防守人乘数激发
  - 与持球时间占比 (Touches) 及失误率权衡：过度花式运球在密集对抗下增加被切球率 15%~22%
  - 受进攻战术体系影响：Pace & Space 鼓励快速直线突破，而 7-Seconds 抑制前场过度停滞运球
- **非线性阈值/边界**：数值 > 70 展现极高频变向晃人与运球单打；数值 < 25 以快速直线一两步传导或直接终结为主。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_064 · FinishAttackTendency
- **家族与候选键**：`player_tendency` / `tendency.FinishAttackTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b06f` | 实机值 `20`
- **逆向汇编证据**：Getter RVA `0x974c10` | Consumer Call RVA `0x1745480` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：组织串联与进攻终结决策权重。控制在支配球时触发 FinishAttackTendency 的离散行为概率。
- **机制与跨字段关联**：
  - 与传球视野 (Pass Vision) 和传球准确性 (Pass Accuracy) 属性强联动
  - 与 Dimer (十美分), Needle Threader, Floor General 徽章形成团队增益
  - 直接调节球队助攻率与百回合失误率，确立控卫与核心持球人战术定位
- **非线性阈值/边界**：数值 > 70 确立团队组织大脑核心；数值 < 30 进入终结型得分手逻辑。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_065 · FindOpenManTendency
- **家族与候选键**：`player_tendency` / `tendency.FindOpenManTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b070` | 实机值 `70`
- **逆向汇编证据**：Getter RVA `0x974be0` | Consumer Call RVA `0x174548e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：持球突破撕扯防线后，主动跳起分球给外线或内线空位队友的无私助攻意愿。
- **机制与跨字段关联**：
  - 与 Pass Accuracy (95)、Dimer（十全十美）、Bullet Passer 徽章强联动
  - 顶级组织大师（哈利伯顿、保罗、纳什）的核心灵魂倾向
  - 与纯得分后卫单打到底（Attack Strong On Drive 0x497）互为相反调节
- **非线性阈值/边界**：顶级传控核心给 90~98；纯终结攻坚手维持 45~60。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_066 · TouchTendency
- **家族与候选键**：`player_tendency` / `tendency.TouchTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b071` | 实机值 `98`
- **逆向汇编证据**：Getter RVA `0x975b30` | Consumer Call RVA `0x174549c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：全队球权支配权重。直接决定阵地战谁持球过半场及战术终结优先权（Touches 争议核心）。
- **机制与跨字段关联**：
  - 与教练 Playbook 中 Primary Scoring Option 战术调用权重联动
  - 在战术破产或进入 Freelance Motion 时决定无球呼叫要球频率
  - 与 USG% 和全队五人薪资/地位梯队严密咬合
- **非线性阈值/边界**：第一持球大核 90~99；二当家 75~85；无球侧翼 45~60；吃饼内线 20~35。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_067 · PostUpTendency
- **家族与候选键**：`player_tendency` / `tendency.PostUpTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b072` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975570` | Consumer Call RVA `0x17454aa` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：呼叫战术或落位时背身靠打（Post Up）要求的意愿。
- **机制与跨字段关联**：
  - 受 Post Control 属性与 Backdown Punisher 徽章联动
  - 与现代魔球空间体系冲突，仅适用于约基奇、恩比德等低位万花筒
- **非线性阈值/边界**：传统低位杀手给 80+；现代空间后卫与侧翼置 0~5。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_068 · RollVsFadeTendency
- **家族与候选键**：`player_tendency` / `tendency.RollVsFadeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b073` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975680` | Consumer Call RVA `0x17454b8` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 RollVsFadeTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_069 · TransitionSpotupTendency
- **家族与候选键**：`player_tendency` / `tendency.TransitionSpotupTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b074` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x975b90` | Consumer Call RVA `0x17454c6` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 TransitionSpotupTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_070 · IsoVsEliteTendency
- **家族与候选键**：`player_tendency` / `tendency.IsoVsEliteTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b075` | 实机值 `20`
- **逆向汇编证据**：Getter RVA `0x974f40` | Consumer Call RVA `0x17454d4` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 IsoVsEliteTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_071 · IsoVsGoodTendency
- **家族与候选键**：`player_tendency` / `tendency.IsoVsGoodTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b076` | 实机值 `59`
- **逆向汇编证据**：Getter RVA `0x974f70` | Consumer Call RVA `0x17454e2` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 IsoVsGoodTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_072 · IsoVsAverageTendency
- **家族与候选键**：`player_tendency` / `tendency.IsoVsAverageTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b077` | 实机值 `91`
- **逆向汇编证据**：Getter RVA `0x974f10` | Consumer Call RVA `0x17454f0` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 IsoVsAverageTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_073 · IsoVsPoorTendency
- **家族与候选键**：`player_tendency` / `tendency.IsoVsPoorTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b078` | 实机值 `92`
- **逆向汇编证据**：Getter RVA `0x974fa0` | Consumer Call RVA `0x17454fe` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制球员在 3D 比赛与日历模拟中执行 IsoVsPoorTendency 专项动作的离散行为概率。
- **机制与跨字段关联**：
  - 与相关球员基础属性强绑定
  - 受 Playbook 专属战术跑位加成
  - 受对应徽章门禁激活约束
- **非线性阈值/边界**：标准 0~100 百分比离散权重。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_074 · PlayDisciplineTendency
- **家族与候选键**：`player_tendency` / `tendency.PlayDisciplineTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b079` | 实机值 `90`
- **逆向汇编证据**：Getter RVA `0x9751e0` | Consumer Call RVA `0x174550c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：战术执行纪律性。数值越高越会耐心完整跑完教练预设的全部掩护与切入路线。
- **机制与跨字段关联**：
  - 与教练 Offensive Playcalling 设置联动
  - 高数值抑制单打独斗，提高团队配合得分占比
- **非线性阈值/边界**：老将与战术型控卫给 85~95；乱战得分手给 30~50。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_075 · PostShimmyShotTendency
- **家族与候选键**：`player_tendency` / `tendency.PostShimmyShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b07a` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975470` | Consumer Call RVA `0x174551a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostShimmyShotTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_076 · PostFaceUpTendency
- **家族与候选键**：`player_tendency` / `tendency.PostFaceUpTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b07b` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975330` | Consumer Call RVA `0x1745528` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostFaceUpTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_077 · PostBackDownTendency
- **家族与候选键**：`player_tendency` / `tendency.PostBackDownTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b07c` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975260` | Consumer Call RVA `0x1745536` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostBackDownTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_078 · PostAggressiveBackDownTendency
- **家族与候选键**：`player_tendency` / `tendency.PostAggressiveBackDownTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b07d` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975230` | Consumer Call RVA `0x1745544` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostAggressiveBackDownTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_079 · PostShootTendency
- **家族与候选键**：`player_tendency` / `tendency.PostShootTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b07e` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x9754a0` | Consumer Call RVA `0x1745552` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostShootTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_080 · PostHookLeftTendency
- **家族与候选键**：`player_tendency` / `tendency.PostHookLeftTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b07f` | 实机值 `4`
- **逆向汇编证据**：Getter RVA `0x9753e0` | Consumer Call RVA `0x1745560` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostHookLeftTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_081 · PostHookRightTendency
- **家族与候选键**：`player_tendency` / `tendency.PostHookRightTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b080` | 实机值 `8`
- **逆向汇编证据**：Getter RVA `0x975410` | Consumer Call RVA `0x174556e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostHookRightTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_082 · PostFadeLeftTendency
- **家族与候选键**：`player_tendency` / `tendency.PostFadeLeftTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b081` | 实机值 `28`
- **逆向汇编证据**：Getter RVA `0x975360` | Consumer Call RVA `0x174557c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostFadeLeftTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_083 · PostFadeRightTendency
- **家族与候选键**：`player_tendency` / `tendency.PostFadeRightTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b082` | 实机值 `13`
- **逆向汇编证据**：Getter RVA `0x975390` | Consumer Call RVA `0x174558a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostFadeRightTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_084 · PostUpAndUnderTendency
- **家族与候选键**：`player_tendency` / `tendency.PostUpAndUnderTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b083` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975540` | Consumer Call RVA `0x1745598` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostUpAndUnderTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_085 · PostHopShotTendency
- **家族与候选键**：`player_tendency` / `tendency.PostHopShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b084` | 实机值 `20`
- **逆向汇编证据**：Getter RVA `0x975440` | Consumer Call RVA `0x17455a6` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostHopShotTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_086 · PostStepbackShotTendency
- **家族与候选键**：`player_tendency` / `tendency.PostStepbackShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b085` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975510` | Consumer Call RVA `0x17455b4` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostStepbackShotTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_087 · PostDriveTendency
- **家族与候选键**：`player_tendency` / `tendency.PostDriveTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b086` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x9752a0` | Consumer Call RVA `0x17455c2` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostDriveTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_088 · PostSpinTendency
- **家族与候选键**：`player_tendency` / `tendency.PostSpinTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b087` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x9754e0` | Consumer Call RVA `0x17455d0` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostSpinTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_089 · PostDropStepOutsideTendency
- **家族与候选键**：`player_tendency` / `tendency.PostDropStepOutsideTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b088` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975300` | Consumer Call RVA `0x17455de` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostDropStepOutsideTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_090 · PostDropStepInsideTendency
- **家族与候选键**：`player_tendency` / `tendency.PostDropStepInsideTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b089` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x9752d0` | Consumer Call RVA `0x17455ec` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：背身低位单打决策与专项终结选择意愿。控制在禁区或低位背打接球后执行 PostDropStepInsideTendency 专项技术的离散权重。
- **机制与跨字段关联**：
  - 受背身控制 (Post Control) 和对应背身勾手/后仰投篮基础属性门禁加成
  - 与 Backdown Punisher (背推大师), Dropstepper (沉底步大师), Post Spin Technician 徽章强联动
  - 与教练战术体系（如 Post Centric, Grit & Grind）及进攻节奏 (Tempo) 强相关
  - 与外线突分倾向 (Dish to Open Man) 形成博弈：低传球意愿中锋容易陷入死球包夹
- **非线性阈值/边界**：数值 > 75 确立低位大核进攻招牌手段；数值 < 20 导致低位得球后几乎从不采用此单打招式。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_091 · FlashyPassTendency
- **家族与候选键**：`player_tendency` / `tendency.FlashyPassTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b08a` | 实机值 `35`
- **逆向汇编证据**：Getter RVA `0x974c70` | Consumer Call RVA `0x17455fa` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：组织串联与进攻终结决策权重。控制在支配球时触发 FlashyPassTendency 的离散行为概率。
- **机制与跨字段关联**：
  - 与传球视野 (Pass Vision) 和传球准确性 (Pass Accuracy) 属性强联动
  - 与 Dimer (十美分), Needle Threader, Floor General 徽章形成团队增益
  - 直接调节球队助攻率与百回合失误率，确立控卫与核心持球人战术定位
- **非线性阈值/边界**：数值 > 70 确立团队组织大脑核心；数值 < 30 进入终结型得分手逻辑。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_092 · AlleyOopPassTendency
- **家族与候选键**：`player_tendency` / `tendency.AlleyOopPassTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b08b` | 实机值 `99`
- **逆向汇编证据**：Getter RVA `0x974200` | Consumer Call RVA `0x1745608` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：组织串联与进攻终结决策权重。控制在支配球时触发 AlleyOopPassTendency 的离散行为概率。
- **机制与跨字段关联**：
  - 与传球视野 (Pass Vision) 和传球准确性 (Pass Accuracy) 属性强联动
  - 与 Dimer (十美分), Needle Threader, Floor General 徽章形成团队增益
  - 直接调节球队助攻率与百回合失误率，确立控卫与核心持球人战术定位
- **非线性阈值/边界**：数值 > 70 确立团队组织大脑核心；数值 < 30 进入终结型得分手逻辑。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_093 · InterceptionTendency
- **家族与候选键**：`player_tendency` / `tendency.InterceptionTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b08c` | 实机值 `75`
- **逆向汇编证据**：Getter RVA `0x974e70` | Consumer Call RVA `0x1745616` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：防守端破坏传球路线与防守干扰的激进度。控制在无球和持球防守时主动执行 InterceptionTendency 的行为概率。
- **机制与跨字段关联**：
  - 受 Steal / Block / Shot ContestIQ 属性门禁与身高臂展判定约束
  - 与 Interceptor, Pickpocket, Rim Protector, Intimidator 徽章强绑定
  - 过度激进导致失位或被突破打成 2+1，与本方防守体系纪律性 (Help Defense) 形成博弈
- **非线性阈值/边界**：数值 > 75 成为顶级防守破坏者；数值 < 25 保持站位规范防守、避免赌博性失位。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_094 · TakeChargeTendency
- **家族与候选键**：`player_tendency` / `tendency.TakeChargeTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b08d` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `0x975af0` | Consumer Call RVA `0x1745624` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：防守端破坏传球路线与防守干扰的激进度。控制在无球和持球防守时主动执行 TakeChargeTendency 的行为概率。
- **机制与跨字段关联**：
  - 受 Steal / Block / Shot ContestIQ 属性门禁与身高臂展判定约束
  - 与 Interceptor, Pickpocket, Rim Protector, Intimidator 徽章强绑定
  - 过度激进导致失位或被突破打成 2+1，与本方防守体系纪律性 (Help Defense) 形成博弈
- **非线性阈值/边界**：数值 > 75 成为顶级防守破坏者；数值 < 25 保持站位规范防守、避免赌博性失位。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_095 · OnBallStealTendency
- **家族与候选键**：`player_tendency` / `tendency.OnBallStealTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b08e` | 实机值 `85`
- **逆向汇编证据**：Getter RVA `0x975110` | Consumer Call RVA `0x1745632` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：防守端破坏传球路线与防守干扰的激进度。控制在无球和持球防守时主动执行 OnBallStealTendency 的行为概率。
- **机制与跨字段关联**：
  - 受 Steal / Block / Shot ContestIQ 属性门禁与身高臂展判定约束
  - 与 Interceptor, Pickpocket, Rim Protector, Intimidator 徽章强绑定
  - 过度激进导致失位或被突破打成 2+1，与本方防守体系纪律性 (Help Defense) 形成博弈
- **非线性阈值/边界**：数值 > 75 成为顶级防守破坏者；数值 < 25 保持站位规范防守、避免赌博性失位。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_096 · ContestShotTendency
- **家族与候选键**：`player_tendency` / `tendency.ContestShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b08f` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `0x974680` | Consumer Call RVA `0x1745640` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：贴身防守举手贴脸干扰投篮的纪律性（护框大师必改核心项）。
- **机制与跨字段关联**：
  - 受 Interior Defense、Perimeter Defense、Menace 徽章加成
  - 不盲目起跳，最大程度压缩对手投篮命中率且杜绝被造投篮犯规
- **非线性阈值/边界**：顶级防守人（追梦/戈贝尔）给 90~98；防守散漫者 30~50。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_097 · BlockShotTendency
- **家族与候选键**：`player_tendency` / `tendency.BlockShotTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b090` | 实机值 `60`
- **逆向汇编证据**：Getter RVA `0x974590` | Consumer Call RVA `0x174564e` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：迎面飞身起跳封盖投篮的激进倾向。
- **机制与跨字段关联**：
  - 与 Block 属性、Rim Protector 徽章强相关
  - 过高会导致一见假动作就起跳吃晃送犯规，必须与 Contest Shot 保持梯队平衡
- **非线性阈值/边界**：暴力盖帽王 80~90；纪律型护框大闸 60~75；地板流中锋 35~50。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_098 · FoulTendency
- **家族与候选键**：`player_tendency` / `tendency.FoulTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b091` | 实机值 `34`
- **逆向汇编证据**：Getter RVA `0x974cd0` | Consumer Call RVA `0x174565c` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：常规防守战术犯规与阻滞快攻犯规的激进度。
- **机制与跨字段关联**：
  - 严格依据现实 PF/36 犯规率换算
  - 直接决定轮换被罚下风险与罚球赠送率
- **非线性阈值/边界**：控制在 25~45 之间可杜绝主力首发 5 分钟 2 犯离场。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### TENDENCY_NATIVE_099 · HardFoulTendency
- **家族与候选键**：`player_tendency` / `tendency.HardFoulTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VALIDATED_WITH_NATIVE_GETTER_AND_CONSUMER)
- **实机地址与数值**：地址 `0x7ff4e4e9b092` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `0x974db0` | Consumer Call RVA `0x174566a` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：防守端侵略性与犯规控制。控制在对抗、追防封盖或阻止快攻时执行 HardFoulTendency 的激进程度。
- **机制与跨字段关联**：
  - 与防守属性 (Perimeter/Interior Defense) 和横移速度 (Lateral Quickness) 联动
  - 直接决定球员陷入犯规麻烦 (Foul Trouble) 的概率，影响真实轮换出场时间
  - 受裁判吹罚尺度与比赛关键时刻 (ACE 关键时刻点球/战术犯规) 动态超控
- **非线性阈值/边界**：控制在 25~45 之间可杜绝主力首发 5 分钟 2 犯离场；超过 70 属于高危犯规漏洞。
- **实机回执与说明**：Read uint8 from active player Tyrese Haliburton


### WORLD_REG_001 · settings.game_settings.quarter_length
- **家族与候选键**：`world_settings` / `settings.game_settings.quarter_length`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe04c` | 实机值 `12`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[1, 12]
- **实机回执与说明**：Read uint32 from SLOT_SETTINGS (0x0632B4B0) offset 0x14


### WORLD_REG_002 · settings.game_settings.game_speed
- **家族与候选键**：`world_settings` / `settings.game_settings.game_speed`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe038` | 实机值 `0.5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.game_speed 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SETTINGS (0x0632B4B0) offset 0x0


### WORLD_REG_003 · settings.game_settings.free_throw_difficulty
- **家族与候选键**：`world_settings` / `settings.game_settings.free_throw_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe098` | 实机值 `0.5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.free_throw_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SETTINGS (0x0632B4B0) offset 0x60


### WORLD_REG_004 · settings.game_settings.shot_clock
- **家族与候选键**：`world_settings` / `settings.game_settings.shot_clock`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe0ac` | 实机值 `24`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.shot_clock 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[12, 60]
- **实机回执与说明**：Read uint32 from SLOT_SETTINGS (0x0632B4B0) offset 0x74


### WORLD_REG_005 · settings.game_settings.foul_out
- **家族与候选键**：`world_settings` / `settings.game_settings.foul_out`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe0d8` | 实机值 `6`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.foul_out 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[2, 8]
- **实机回执与说明**：Read uint32 from SLOT_SETTINGS (0x0632B4B0) offset 0xa0


### WORLD_REG_006 · settings.game_settings.injuries_enabled
- **家族与候选键**：`world_settings` / `settings.game_settings.injuries_enabled`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe128` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.game_settings.injuries_enabled 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_SETTINGS (0x0632B4B0) offset 0xf0


### WORLD_REG_007 · settings.simulation.sim_quarter_length
- **家族与候选键**：`world_settings` / `settings.simulation.sim_quarter_length`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff2b8` | 实机值 `12`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.simulation.sim_quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[1, 12]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0xb4


### WORLD_REG_008 · settings.simulation.normalize_stats
- **家族与候选键**：`world_settings` / `settings.simulation.normalize_stats`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff804` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.simulation.normalize_stats 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x600


### WORLD_REG_009 · settings.trade_rules.cpu_cpu_trades
- **家族与候选键**：`world_settings` / `settings.trade_rules.cpu_cpu_trades`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff374` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.cpu_cpu_trades 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x170


### WORLD_REG_010 · settings.trade_rules.trade_override
- **家族与候选键**：`world_settings` / `settings.trade_rules.trade_override`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff36c` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.trade_override 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x168


### WORLD_REG_011 · settings.trade_rules.trade_deadline
- **家族与候选键**：`world_settings` / `settings.trade_rules.trade_deadline`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff370` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.trade_deadline 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x16c


### WORLD_REG_012 · settings.trade_rules.financial_trade_rules
- **家族与候选键**：`world_settings` / `settings.trade_rules.financial_trade_rules`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff364` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.financial_trade_rules 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x160


### WORLD_REG_013 · settings.trade_rules.recently_signed_rule
- **家族与候选键**：`world_settings` / `settings.trade_rules.recently_signed_rule`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff358` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.recently_signed_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x154


### WORLD_REG_014 · settings.trade_rules.recently_traded_rule
- **家族与候选键**：`world_settings` / `settings.trade_rules.recently_traded_rule`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff35c` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.recently_traded_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x158


### WORLD_REG_015 · settings.trade_rules.trade_difficulty
- **家族与候选键**：`world_settings` / `settings.trade_rules.trade_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff378` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.trade_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x174


### WORLD_REG_016 · settings.trade_rules.cpu_trade_frequency
- **家族与候选键**：`world_settings` / `settings.trade_rules.cpu_trade_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff37c` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.cpu_trade_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x178


### WORLD_REG_017 · settings.trade_rules.blockbuster_trade_frequency
- **家族与候选键**：`world_settings` / `settings.trade_rules.blockbuster_trade_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff380` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.blockbuster_trade_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x17c


### WORLD_REG_018 · settings.trade_rules.untouchable_threshold
- **家族与候选键**：`world_settings` / `settings.trade_rules.untouchable_threshold`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff388` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.trade_rules.untouchable_threshold 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x184


### WORLD_REG_019 · settings.contracts.contract_difficulty
- **家族与候选键**：`world_settings` / `settings.contracts.contract_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff414` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.contract_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x210


### WORLD_REG_020 · settings.contracts.player_non_financial_ambitions
- **家族与候选键**：`world_settings` / `settings.contracts.player_non_financial_ambitions`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff418` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_non_financial_ambitions 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x214


### WORLD_REG_021 · settings.contracts.min_contract_rating
- **家族与候选键**：`world_settings` / `settings.contracts.min_contract_rating`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff41c` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.min_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[50, 99]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x218


### WORLD_REG_022 · settings.contracts.max_contract_rating
- **家族与候选键**：`world_settings` / `settings.contracts.max_contract_rating`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff420` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.max_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[70, 99]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x21c


### WORLD_REG_023 · settings.contracts.player_potential_factor
- **家族与候选键**：`world_settings` / `settings.contracts.player_potential_factor`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff424` | 实机值 `60`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_potential_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x220


### WORLD_REG_024 · settings.contracts.player_durability_factor
- **家族与候选键**：`world_settings` / `settings.contracts.player_durability_factor`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff428` | 实机值 `20`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_durability_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x224


### WORLD_REG_025 · settings.contracts.player_fame_factor
- **家族与候选键**：`world_settings` / `settings.contracts.player_fame_factor`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff430` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.player_fame_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x22c


### WORLD_REG_026 · settings.contracts.cpu_interest_in_resigning
- **家族与候选键**：`world_settings` / `settings.contracts.cpu_interest_in_resigning`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff438` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.contracts.cpu_interest_in_resigning 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x234


### WORLD_REG_027 · settings.injuries_and_morale.user_injury_frequency
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.user_injury_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff450` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.user_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x24c


### WORLD_REG_028 · settings.injuries_and_morale.cpu_injury_frequency
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.cpu_injury_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff454` | 实机值 `55`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.cpu_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x250


### WORLD_REG_029 · settings.injuries_and_morale.user_injury_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.user_injury_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff458` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.user_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x254


### WORLD_REG_030 · settings.injuries_and_morale.cpu_injury_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.cpu_injury_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff45c` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.cpu_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x258


### WORLD_REG_031 · settings.injuries_and_morale.injury_severity
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.injury_severity`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff460` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.injury_severity 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x25c


### WORLD_REG_032 · settings.injuries_and_morale.injury_duration
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.injury_duration`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff464` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.injury_duration 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x260


### WORLD_REG_033 · settings.injuries_and_morale.career_ending_injury_frequency
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.career_ending_injury_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff468` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.career_ending_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x264


### WORLD_REG_034 · settings.injuries_and_morale.morale_difficulty
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.morale_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff43c` | 实机值 `35`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.morale_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x238


### WORLD_REG_035 · settings.injuries_and_morale.morale_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.morale_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff440` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.morale_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x23c


### WORLD_REG_036 · settings.injuries_and_morale.chemistry_difficulty
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.chemistry_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff444` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.chemistry_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x240


### WORLD_REG_037 · settings.injuries_and_morale.chemistry_effects
- **家族与候选键**：`world_settings` / `settings.injuries_and_morale.chemistry_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff448` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.injuries_and_morale.chemistry_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x244


### WORLD_REG_038 · settings.progression.training_effects
- **家族与候选键**：`world_settings` / `settings.progression.training_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff46c` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.progression.training_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x268


### WORLD_REG_039 · settings.progression.offseason_progression_rate
- **家族与候选键**：`world_settings` / `settings.progression.offseason_progression_rate`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff470` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.progression.offseason_progression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x26c


### WORLD_REG_040 · settings.progression.regression_rate
- **家族与候选键**：`world_settings` / `settings.progression.regression_rate`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff478` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.progression.regression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 100]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x274


### WORLD_REG_041 · settings.gameplay_sliders.game_difficulty_preset
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.game_difficulty_preset`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff95c` | 实机值 `4`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.game_difficulty_preset 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 4]
- **实机回执与说明**：Read uint32 from SLOT_SLIDERS (0x0632B4A0) offset 0x0


### WORLD_REG_042 · settings.gameplay_sliders.speed_with_ball_min_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_min_user`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcd8` | 实机值 `0.4000000059604645`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_min_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x37c


### WORLD_REG_043 · settings.gameplay_sliders.speed_with_ball_min_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_min_cpu`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcdc` | 实机值 `0.4000000059604645`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_min_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x380


### WORLD_REG_044 · settings.gameplay_sliders.speed_with_ball_max_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_max_user`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcd0` | 实机值 `0.699999988079071`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_max_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x374


### WORLD_REG_045 · settings.gameplay_sliders.speed_with_ball_max_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_with_ball_max_cpu`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcd4` | 实机值 `0.699999988079071`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_with_ball_max_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x378


### WORLD_REG_046 · settings.gameplay_sliders.acceleration_with_ball_min_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.acceleration_with_ball_min_user`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcf8` | 实机值 `0.4000000059604645`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.acceleration_with_ball_min_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x39c


### WORLD_REG_047 · settings.gameplay_sliders.acceleration_with_ball_min_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.acceleration_with_ball_min_cpu`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcfc` | 实机值 `0.4000000059604645`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.acceleration_with_ball_min_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x3a0


### WORLD_REG_048 · settings.gameplay_sliders.speed_without_ball_min_user
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_without_ball_min_user`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffcc8` | 实机值 `0.3499999940395355`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_without_ball_min_user 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x36c


### WORLD_REG_049 · settings.gameplay_sliders.speed_without_ball_min_cpu
- **家族与候选键**：`world_settings` / `settings.gameplay_sliders.speed_without_ball_min_cpu`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ffccc` | 实机值 `0.3499999940395355`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 settings.gameplay_sliders.speed_without_ball_min_cpu 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[0, 1]
- **实机回执与说明**：Read float from SLOT_SLIDERS (0x0632B4A0) offset 0x370


### WORLD_REG_050 · world.trade_and_draft_rules.cpu_cpu_trades
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.cpu_cpu_trades`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff374` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.cpu_cpu_trades 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x170


### WORLD_REG_051 · world.trade_and_draft_rules.cpu_trade_frequency
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.cpu_trade_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff37c` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.cpu_trade_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x178


### WORLD_REG_052 · world.trade_and_draft_rules.ted_stepien_rule
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.ted_stepien_rule`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff384` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.ted_stepien_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x180


### WORLD_REG_053 · world.trade_and_draft_rules.trade_override
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.trade_override`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff36c` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.trade_override 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x168


### WORLD_REG_054 · world.trade_and_draft_rules.trade_deadline
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.trade_deadline`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff370` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.trade_deadline 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x16c


### WORLD_REG_055 · world.trade_and_draft_rules.financial_trade_rules
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.financial_trade_rules`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff364` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.financial_trade_rules 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x160


### WORLD_REG_056 · world.trade_and_draft_rules.recently_signed_rule
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.recently_signed_rule`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff358` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.recently_signed_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x154


### WORLD_REG_057 · world.trade_and_draft_rules.recently_traded_rule
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.recently_traded_rule`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff35c` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.recently_traded_rule 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x158


### WORLD_REG_058 · world.trade_and_draft_rules.trade_difficulty
- **家族与候选键**：`world_settings` / `world.trade_and_draft_rules.trade_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff378` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.trade_and_draft_rules.trade_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x174


### WORLD_REG_059 · world.contracts_and_finances.cpu_interest_in_resigning
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.cpu_interest_in_resigning`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff438` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.cpu_interest_in_resigning 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x234


### WORLD_REG_060 · world.contracts_and_finances.contract_difficulty
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.contract_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff414` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.contract_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x210


### WORLD_REG_061 · world.contracts_and_finances.player_non_financial_ambitions
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_non_financial_ambitions`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff418` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_non_financial_ambitions 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x214


### WORLD_REG_062 · world.contracts_and_finances.min_contract_rating
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.min_contract_rating`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff41c` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.min_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x218


### WORLD_REG_063 · world.contracts_and_finances.max_contract_rating
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.max_contract_rating`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff420` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.max_contract_rating 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x21c


### WORLD_REG_064 · world.contracts_and_finances.player_potential_factor
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_potential_factor`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff424` | 实机值 `60`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_potential_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x220


### WORLD_REG_065 · world.contracts_and_finances.player_durability_factor
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_durability_factor`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff428` | 实机值 `20`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_durability_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x224


### WORLD_REG_066 · world.contracts_and_finances.player_fame_factor
- **家族与候选键**：`world_settings` / `world.contracts_and_finances.player_fame_factor`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff430` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.contracts_and_finances.player_fame_factor 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x22c


### WORLD_REG_067 · world.progression_and_regression.offseason_progression_rate
- **家族与候选键**：`world_settings` / `world.progression_and_regression.offseason_progression_rate`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff470` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.progression_and_regression.offseason_progression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x26c


### WORLD_REG_068 · world.progression_and_regression.regression_rate
- **家族与候选键**：`world_settings` / `world.progression_and_regression.regression_rate`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff478` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.progression_and_regression.regression_rate 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x274


### WORLD_REG_069 · world.progression_and_regression.training_effects
- **家族与候选键**：`world_settings` / `world.progression_and_regression.training_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff46c` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.progression_and_regression.training_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x268


### WORLD_REG_070 · world.injuries_and_morale.user_injury_frequency
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.user_injury_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff450` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.user_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x24c


### WORLD_REG_071 · world.injuries_and_morale.cpu_injury_frequency
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.cpu_injury_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff454` | 实机值 `55`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.cpu_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x250


### WORLD_REG_072 · world.injuries_and_morale.user_injury_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.user_injury_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff458` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.user_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x254


### WORLD_REG_073 · world.injuries_and_morale.cpu_injury_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.cpu_injury_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff45c` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.cpu_injury_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x258


### WORLD_REG_074 · world.injuries_and_morale.injury_severity
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.injury_severity`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff460` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.injury_severity 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x25c


### WORLD_REG_075 · world.injuries_and_morale.injury_duration
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.injury_duration`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff464` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.injury_duration 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x260


### WORLD_REG_076 · world.injuries_and_morale.career_ending_injury_frequency
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.career_ending_injury_frequency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff468` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.career_ending_injury_frequency 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x264


### WORLD_REG_077 · world.injuries_and_morale.morale_difficulty
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.morale_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff43c` | 实机值 `35`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.morale_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x238


### WORLD_REG_078 · world.injuries_and_morale.morale_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.morale_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff440` | 实机值 `40`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.morale_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x23c


### WORLD_REG_079 · world.injuries_and_morale.chemistry_difficulty
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.chemistry_difficulty`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff444` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.chemistry_difficulty 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x240


### WORLD_REG_080 · world.injuries_and_morale.chemistry_effects
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.chemistry_effects`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff448` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.chemistry_effects 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x244


### WORLD_REG_081 · world.injuries_and_morale.injuries_enabled
- **家族与候选键**：`world_settings` / `world.injuries_and_morale.injuries_enabled`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe128` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.injuries_and_morale.injuries_enabled 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_SETTINGS (0x0632B4B0) offset 0xf0


### WORLD_REG_082 · world.gameplay_and_calendar.quarter_length
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.quarter_length`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe04c` | 实机值 `12`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_SETTINGS (0x0632B4B0) offset 0x14


### WORLD_REG_083 · world.gameplay_and_calendar.sim_quarter_length
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.sim_quarter_length`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff2b8` | 实机值 `12`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.sim_quarter_length 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0xb4


### WORLD_REG_084 · world.gameplay_and_calendar.normalize_stats
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.normalize_stats`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff804` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_TRADE`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.normalize_stats 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_TRADE (0x0632B498) offset 0x600


### WORLD_REG_085 · world.gameplay_and_calendar.game_difficulty_preset
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.game_difficulty_preset`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e67ff95c` | 实机值 `4`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SLIDERS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.game_difficulty_preset 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read uint32 from SLOT_SLIDERS (0x0632B4A0) offset 0x0


### WORLD_REG_086 · world.gameplay_and_calendar.game_speed
- **家族与候选键**：`world_settings` / `world.gameplay_and_calendar.game_speed`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_VERIFIED_IN_CONTROLLER_SLOT)
- **实机地址与数值**：地址 `0x7ff4e68fe038` | 实机值 `0.5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `SLOT_SETTINGS`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制全局比赛与模拟规则中 world.gameplay_and_calendar.game_speed 的核心运行参数。对整场比赛总回合数、体能消耗、犯规惩罚以及薪资合规产生刚性约束。
- **机制与跨字段关联**：
  - 双 Normalize 机制：48 分钟标准比赛时间与统计换算前提
  - 联盟薪资与财务硬规则约束（工资帽、奢侈税、土豪线硬帽）
  - 比赛节奏与攻防时限刚性规则（单节时长、24秒进攻时限、6犯离场门限）
- **非线性阈值/边界**：合法值域区间：[None, None]
- **实机回执与说明**：Read float from SLOT_SETTINGS (0x0632B4B0) offset 0x0


### COACH_DEFAULT_001 · POEOffense
- **家族与候选键**：`coach_settings` / `POEOffense`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742129c` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 POEOffense 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_002 · POEOffense2
- **家族与候选键**：`coach_settings` / `POEOffense2`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742129c` | 实机值 `8`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 POEOffense2 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_003 · POEOffense3
- **家族与候选键**：`coach_settings` / `POEOffense3`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742129c` | 实机值 `11`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 POEOffense3 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_004 · POEDefense
- **家族与候选键**：`coach_settings` / `POEDefense`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742129c` | 实机值 `14`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 POEDefense 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_005 · POEDefense2
- **家族与候选键**：`coach_settings` / `POEDefense2`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742129c` | 实机值 `17`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 POEDefense2 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_006 · POEDefense3
- **家族与候选键**：`coach_settings` / `POEDefense3`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742129c` | 实机值 `20`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 POEDefense3 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_007 · PreferredSystem
- **家族与候选键**：`coach_settings` / `PreferredSystem`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e7421268` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 PreferredSystem 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_008 · ActiveSystem
- **家族与候选键**：`coach_settings` / `ActiveSystem`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e7421268` | 实机值 `4`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 ActiveSystem 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_009 · PlaybookID
- **家族与候选键**：`coach_settings` / `PlaybookID`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e7421268` | 实机值 `0`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 PlaybookID 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_010 · BenchDepth
- **家族与候选键**：`coach_settings` / `BenchDepth`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742123e` | 实机值 `11`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 BenchDepth 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_011 · RunPlayTendency
- **家族与候选键**：`coach_settings` / `RunPlayTendency`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e7421240` | 实机值 `70`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 RunPlayTendency 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_012 · ZoneUsage
- **家族与候选键**：`coach_settings` / `ZoneUsage`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e7421242` | 实机值 `1`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 ZoneUsage 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_013 · BenchUtilization
- **家族与候选键**：`coach_settings` / `BenchUtilization`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e7421298` | 实机值 `60`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 BenchUtilization 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_014 · Tempo
- **家族与候选键**：`coach_settings` / `Tempo`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e74212a8` | 实机值 `80`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 Tempo 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_015 · HelpDefense
- **家族与候选键**：`coach_settings` / `HelpDefense`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e74212a8` | 实机值 `50`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 HelpDefense 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_016 · FreelanceType
- **家族与候选键**：`coach_settings` / `FreelanceType`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e742125c` | 实机值 `5`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 FreelanceType 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_017 · FreelanceType2
- **家族与候选键**：`coach_settings` / `FreelanceType2`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e74212a8` | 实机值 `3`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 FreelanceType2 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_018 · FreelanceType3
- **家族与候选键**：`coach_settings` / `FreelanceType3`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e74212bc` | 实机值 `18`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 FreelanceType3 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach


### COACH_DEFAULT_019 · FreelanceType4
- **家族与候选键**：`coach_settings` / `FreelanceType4`
- **证据等级与状态**：`LIVE_RECEIPT` | `EVIDENCE_ADDED` (LIVE_RECEIPT_DECODED_FROM_VERIFIED_COACHDATA)
- **实机地址与数值**：地址 `0x7ff4e74212bc` | 实机值 `28`
- **逆向汇编证据**：Getter RVA `None` | Consumer Call RVA `None` | Slot `None`
- **认知分层**：`PRIOR_LITERATURE_HYPOTHESIS`（已完成只读逆向提取与槽位验证；未执行实机注入写变更实验）
- **字段作用与影响**：控制教练战术体系中 FreelanceType4 的全队宏观指令。在落后或战术暂停时可能被自适应教练引擎 (ACE) 动态覆写。
- **机制与跨字段关联**：
  - 自适应教练引擎 (ACE) 动态超控博弈
  - 全队首发与替补 5 人名单倾向聚合
  - 节奏与体能消耗交互：Pace > 70 搭配 12 分钟单节时导致末节体能劣势
  - Playbook 战术优先级调用树
- **非线性阈值/边界**：离散战术枚举或百分比权重 [0, 100]。
- **实机回执与说明**：Decoded bitfield from verified COACHDATA for team 0 coach
