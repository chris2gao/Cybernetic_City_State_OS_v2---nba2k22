# NBA 2K20~2K23 球员真实倾向底层逻辑与全量字节偏移修改规范 (Player Tendency Guide)

本文档融合了全球 2K 顶级拟真社区（Operation Sports 的 **ATD / Attention to Detail 项目**、**SimWorld**、**The Real 2K Insider**）的核心推演成果，以及从本地工具数据包中逆向解压出的 **全部 99 项球员倾向精确字节偏移表（Offset 0x458 ~ 0x4BA）**。

本文档是未来对球员进行倾向调优的唯一标准逻辑手册，**严禁凭感觉主观修改，必须严格依照现实数据换算公式执行**！

---

## 一、为什么 2K 官方默认倾向严重失真？（核心四大病灶）

2K 官方名单策划往往采用流水线通用模板批量刷数值，导致了严重破坏拟真度的四大病灶：

1. **投篮空间错位与长两分泛滥**：
   * 现代 NBA 追求“魔球化”（三分 + 禁区直杀），中投占比降至 15% 以下；
   * 但 2K 官方给绝大多数现代外线分配了极高的 `SHOT_MID-RANGE_TENDENCY (0x46A)`，而许多场均出手 6+ 记三分的 3&D 侧翼，其三分倾向 `SHOT_THREE_TENDENCY (0x472)` 却只有 15~25，导致空位不投、踩线长两分频出。
2. **持球无脑压步攻筐（The Universal Driving Spree）**：
   * 官方的 `DRIVE_TENDENCY (0x483)` 普遍虚高（平均 75+），导致哪怕是慢速老将接球后也会盲目运球硬挤内线，破坏了原本的战术跑位和传切流速。
3. **触球与出手比例脱节（Touches vs. Shot vs. Isolation）**：
   * 超巨单打倾向 `ISO (0x49D~0x4A0)` 和出手倾向 `SHOT_TENDENCY (0x458)` 动辄给到 99，导致模拟比赛中巨星场均出手 35 次砍 45 分，队友全部变成木头人看客；
   * 而传控大核（如哈利伯顿、保罗）的 `DISH_TO_OPEN_MAN_TENDENCY (0x498)` 给得不够高，压抑了突分传切威力。
4. **防守起跳送犯规（Contest vs. Block & Foul）**：
   * 官方盖帽手被赋予了过高的 `BLOCK_SHOT_TENDENCY (0x4B8)`（85+），而 `CONTEST_SHOT_TENDENCY (0x4B7)` 偏低，导致内线一见假动作就起跳，场均被造犯规 4~5 次；现实中的顶级护框大师（大洛佩斯、戈贝尔）大多是垂直贴防干扰（High Contest, Disciplined Block）。

---

## 二、真实 NBA 追踪数据到 2K 倾向的严密数学换算公式

### 1. 核心出手意愿与触球权重 (Shot & Touches)
* **现实依据**：NBA.com Tracking Data 统计的 **每 36 分钟真实出手数 (FGA / 36 min)** 与 **USG% (球权使用率)**。
* **整体出手倾向 (SHOT_TENDENCY at 0x458)**：
  $$\text{Shot Tendency} = \min\left(92, \max\left(15, \frac{\text{FGA per 36}}{22.0} \times 90 \right)\right)$$
  * 第一大核（东契奇、字母哥、恩比德、乔丹，FGA/36 $\ge 20$）：`85 ~ 92`（上限锁死在 92，杜绝一人独霸 40 分的失衡）；
  * 二当家 / 核心副攻（FGA/36 约 $15 \sim 18$）：`68 ~ 78`；
  * 战术首发第三点（FGA/36 约 $11 \sim 14$）：`45 ~ 60`；
  * 纯 3&D / 空间投手（FGA/36 约 $8 \sim 10$）：`30 ~ 42`；
  * 吃饼蓝领中锋（FGA/36 $< 7$）：`15 ~ 25`。
* **触球分配权重 (TOUCHES_TENDENCY at 0x499)**：
  * 主控发起人（哈利伯顿、保罗、特雷杨）：`85 ~ 95`；
  * 无球终结者（克莱、希尔德）：`50 ~ 65`。

### 2. 投篮热区分布倾向 (Shot Zone Frequency)
* **现实依据**：Basketball-Reference 球员真实投篮热区出手占比（0-3尺、3-10尺、10-16尺、16-3分线、3分）。
* **三分球出手倾向 (SHOT_THREE_TENDENCY at 0x472)**：
  $$\text{Shot Three} = \min(99, \max(0, \text{3PAr (三分出手占总出手百分比)} \times 110))$$
  * 极度魔球射手（克莱、希尔德，3PAr $> 60\%$）：`85 ~ 98`；
  * 现代空间内线（特纳、大洛佩斯，3PAr $40\% \sim 55\%$）：`65 ~ 80`；
  * 兼具中距离与突分的全能后卫（哈利伯顿、欧文）：`65 ~ 78`；
  * 传统突破后卫（莫兰特、威少，3PAr $20\% \sim 30\%$）：`35 ~ 50`；
  * 纯传统内线（卡佩拉、戈贝尔，3PAr $\approx 0\%$）：`0 ~ 3`。
* **转换急停追身三分 (TRANSITION_PULL_UP_THREE at 0x47F)**：
  * 库里、哈利伯顿、利拉德：`80 ~ 95`；
  * 常规外线：`15 ~ 35`；
  * 传统球员：`0`。
* **接球定点三分 (SPOT_UP_SHOT_THREE at 0x473)**：
  * 3&D 侧翼与外拆大前锋：`85 ~ 95`。

### 3. 突破攻筐 vs 突分助攻 (Attack vs. Dish)
* **现实依据**：NBA 官方场均突破次数 (Drives Per Game) 与 突破助攻率 (Pass% on Drives)。
* **突破倾向 (DRIVE_TENDENCY at 0x483)**：
  * 突破怪兽（莫兰特、字母哥、福克斯，Drives $> 15$ 次/场）：`85 ~ 95`；
  * 节奏型控卫（哈利伯顿、保罗，Drives 约 $10 \sim 13$ 次/场）：`60 ~ 72`；
  * 定点无球射手（克莱、邓肯·罗宾逊，Drives $< 3$ 次/场）：`15 ~ 25`。
* **突分空位队友倾向 (DISH_TO_OPEN_MAN_TENDENCY at 0x498)**：
  * 纯组织大师（哈利伯顿、纳什、基德，Drive Pass% $> 40\%$）：`88 ~ 98`；
  * 突分兼备全能核心（詹姆斯、东契奇）：`75 ~ 85`；
  * 纯攻坚单打手（乔丹、科比、欧文，被包夹才分球）：`50 ~ 62`。

### 4. 防守、盖帽起跳与犯规纪律 (Contest, Block & Foul)
* **现实依据**：NBA 干扰投篮数 (Contested Shots)、盖帽率 (BLK%)、犯规率 (PF / 36 min)。
* **投篮贴身干扰倾向 (CONTEST_SHOT_TENDENCY at 0x4B7)**：
  * 顶级防守核心（追梦、戈贝尔、浓眉、阿德巴约）：`90 ~ 98`；
  * 合格轮换防守人：`70 ~ 85`；
  * 防守散漫者：`30 ~ 50`。
* **盖帽起跳扑防倾向 (BLOCK_SHOT_TENDENCY at 0x4B8)**：
  * 极度依赖身体素质的飞天封盖手（怀特塞德）：`85 ~ 95`；
  * 讲究防守纪律性的顶级中锋（大洛佩斯、小加索尔）：`65 ~ 78`；
  * 地板流中锋（约基奇）：`35 ~ 50`。
* **持球抢断下手倾向 (ON-BALL_STEAL_TENDENCY at 0x4B6)**：
  * 抢断王（小卡、斯托克顿、阿尔文·罗伯特森）：`80 ~ 90`；
  * 谨慎防守人：`45 ~ 60`。
* **战术犯规与普通犯规 (FOUL_TENDENCY at 0x4B9)**：
  * 依据犯规率严格映射，杜绝首发 5 分钟 2 犯离场。

---

## 三、2K22 官方底层 99 项球员倾向精确字节偏移全景表

从本地工具底层逆向提取的完整偏移字典（基址：球员结构体起始地址，步长 `0xDF0`）：

| 倾向名称 (Tendency Name) | 字节偏移 (Hex) | 范围 | 核心控制逻辑 |
| :--- | :---: | :---: | :--- |
| **SHOT_TENDENCY** | `0x458` | 0~100 | **全场总出手意愿基准值** (由 USG% 与 FGA/36 严格换算) |
| DRIVING_LAYUP_TENDENCY | `0x459` | 0~100 | 突破上篮倾向 |
| STANDING_DUNK_TENDENCY | `0x45A` | 0~100 | 原地扣篮倾向 (传统中锋必改项) |
| DRIVING_DUNK_TENDENCY | `0x45B` | 0~100 | 突破扣篮终结倾向 |
| FLASHY_DUNK_TENDENCY | `0x45C` | 0~100 | 花式扣篮倾向 |
| ALLEY-OOP_TENDENCY | `0x45D` | 0~100 | 接空接扣篮倾向 (空接顺下人核心) |
| PUTBACK_TENDENCY | `0x45E` | 0~100 | 二次进攻补篮/补扣倾向 |
| CRASH_TENDENCY | `0x45F` | 0~100 | 冲击篮下拼抢进攻篮板倾向 |
| SPIN_LAYUP_TENDENCY | `0x460` | 0~100 | 转身拉杆上篮倾向 |
| HOP_STEP_LAYUP_TENDENCY | `0x461` | 0~100 | 跳步突破上篮倾向 |
| EURO_STEP_LAYUP_TENDENCY | `0x462` | 0~100 | 欧洲步突破上篮倾向 |
| FLOATER_TENDENCY | `0x463` | 0~100 | 禁区小抛投终结倾向 (特雷杨/东契奇核心) |
| STEP_THROUGH_SHOT_TENDENCY | `0x464` | 0~100 | 刺探步上下步挑篮倾向 |
| SHOT_UNDER_BASKET_TENDENCY | `0x465` | 0~100 | 篮下 0~3 尺强攻出手倾向 |
| SHOT_CLOSE_TENDENCY | `0x466` | 0~100 | 3~10 尺近距离投篮倾向 (宜调低，避免原地小跳投) |
| **SHOT_MID-RANGE_TENDENCY** | `0x46A` | 0~100 | **全场中距离出手基准值** |
| SPOT_UP_SHOT_MID-RANGE | `0x46B` | 0~100 | 定点中距离接球出手 |
| OFF_SCREEN_SHOT_MID-RANGE | `0x46C` | 0~100 | 借无球掩护中距离出手 |
| **SHOT_THREE_TENDENCY** | `0x472` | 0~100 | **全场三分总出手基准值** (由 3PAr 换算) |
| SPOT_UP_SHOT_THREE | `0x473` | 0~100 | 定点三分出手倾向 (3&D 侧翼核心) |
| OFF_SCREEN_SHOT_THREE | `0x474` | 0~100 | 借无球掩护反跑三分出手 (库里/克莱核心) |
| CONTESTED_JUMPER_THREE | `0x47A` | 0~100 | 顶着防守强投三分倾向 (巨星神仙球) |
| CONTESTED_JUMPER_MID-RANGE | `0x47B` | 0~100 | 顶着防守强投中距离 (乔丹/科比/杜兰特) |
| **STEPBACK_JUMPER_THREE** | `0x47C` | 0~100 | 后撤步三分倾向 (哈登/东契奇招牌) |
| STEPBACK_JUMPER_MID-RANGE | `0x47D` | 0~100 | 后撤步中距离倾向 |
| SPIN_JUMPER_TENDENCY | `0x47E` | 0~100 | 转身跳投倾向 |
| **TRANSITION_PULL_UP_THREE** | `0x47F` | 0~100 | **转换快攻追身三分倾向** (哈利伯顿/库里) |
| DRIVE_PULL_UP_THREE | `0x480` | 0~100 | 突破急停干拔三分 |
| DRIVE_PULL_UP_MID-RANGE | `0x481` | 0~100 | 突破急停干拔中距离 (保罗招牌中投) |
| **DRIVE_TENDENCY** | `0x483` | 0~100 | **持球突破整体意愿** (绝不可全员 70+) |
| SPOT_UP_DRIVE_TENDENCY | `0x484` | 0~100 | 接定点传球虚晃后突破 |
| OFF_SCREEN_DRIVE_TENDENCY | `0x485` | 0~100 | 借掩护卷切突破 |
| ATTACK_STRONG_ON_DRIVE | `0x497` | 0~100 | 突破强硬对抗终结 (造杀伤罚球意愿) |
| **DISH_TO_OPEN_MAN_TENDENCY** | `0x498` | 0~100 | **突破突分给空位队友倾向** (控卫核心) |
| **TOUCHES_TENDENCY** | `0x499` | 0~100 | **全队触球球权分配权重** |
| POST_UP_TENDENCY | `0x49A` | 0~100 | 低位背身后仰/坐打倾向 |
| ROLL_VS._POP_TENDENCY | `0x49B` | 0~100 | 掩护顺下攻筐 (0) vs 掩护外拆投篮 (100) |
| TRANSITION_SPOT_UP | `0x49C` | 0~100 | 攻防转换快攻落位底角射手倾向 |
| PLAY_DISCIPLINE_TENDENCY | `0x4A1` | 0~100 | **战术执行纪律性** (高值会耐心打完战术) |
| FLASHY_PASS_TENDENCY | `0x4B2` | 0~100 | 花式击地/不看人传球倾向 (哈利伯顿/魔术师) |
| ALLEY-OOP_PASS_TENDENCY | `0x4B3` | 0~100 | 输送空中接力传球倾向 |
| PASS_INTERCEPTION_TENDENCY | `0x4B4` | 0~100 | 传球路线抢断拦截倾向 |
| TAKE_CHARGE_TENDENCY | `0x4B5` | 0~100 | 制造进攻犯规倒地倾向 |
| **ON-BALL_STEAL_TENDENCY** | `0x4B6` | 0~100 | **持球死亡缠绕下手断球倾向** |
| **CONTEST_SHOT_TENDENCY** | `0x4B7` | 0~100 | **贴防举手干扰投篮倾向** (护框核心必改) |
| **BLOCK_SHOT_TENDENCY** | `0x4B8` | 0~100 | **起跳飞身封盖倾向** |
| **FOUL_TENDENCY** | `0x4B9` | 0~100 | **常规战术防守犯规倾向** |
| HARD_FOUL_TENDENCY | `0x4BA` | 0~100 | 凶狠犯规破坏反击快攻倾向 |

---

## 四、修改工作流操作规范（严禁主观编造）

未来当我们要为某位具体球星（如迈克尔·乔丹、泰雷斯·哈利伯顿、迈尔斯·特纳）修改倾向时，严格遵循以下三步：
1. **拉取真实赛季数据**：调取其当赛季或巅峰赛季的真实基础数据（FGA、3PA、3PAr、Drives、AST%、PF/36）；
2. **公式换算并填表**：代入本文档公式计算出精准的目标倾向值；
3. **内存安全写入**：通过 `modifier.set_player_tendency(addr, tend_name, value)` 直接写入上述对应真实偏移；
4. **模拟测试验证**：在终极联盟模拟 5~10 场，对比场均数据与真实 NBA 赛季数据，微调 $\pm 3$ 点闭环调优！
