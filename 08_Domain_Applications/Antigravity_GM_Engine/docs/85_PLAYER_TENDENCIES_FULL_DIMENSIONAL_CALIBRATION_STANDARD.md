# 85 球员全维度 99 项倾向校准与战术重力标准规范
# (Player Tendencies Full-Dimensional Calibration & Tactical Gravity Standard)

> **文档标识**: `DOC-85-PLAYER-TENDENCY-CALIBRATION-STANDARD-V1`  
> **所属系统**: Cybernetic City-State OS v2 - NBA2K22 GM Engine (`08_Domain_Applications/Antigravity_GM_Engine/`)  
> **制定时间**: 2026-11-24  
> **机制依据**: REA 原生内存数据契约 (`0x458` ~ `0x4BA`，共 99 字节)、人类游戏机制裁决与真实攻防博弈逻辑  
> **关联宪法**: [43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) 第 5 节三大铁律  

---

## 1. 核心哲学与引擎双轨机制

在 NBA 2K22 引擎架构中，球员倾向属性（取值范围 `0 ~ 100`，存储于球员结构体偏移 `0x458` 至 `0x4BA` 的连续 99 字节）具有超越传统“技术统计映射”的底层控制价值。它不仅支配着 **3D 实时对局中的 AI 决策树与物理动画触发率**，更是 **日历模拟引擎（Sim Engine）中战术执行流转、球权博弈与技术统计生成的核心权重**。

更重要的是，**倾向直接影响球员在 MyLEAGUE / 终极联盟长期演进中的属性与徽章成长**。频繁触发单打或运球倾向的年轻球员，其控球与单打相关属性才能获得充分的成长点数积累。

---

## 2. 人类裁决六大核心铁律与调校准则

根据人类总架构师于 2026-11-24 的关键指导，全联盟 30 支球队所有球员的倾向调校必须严格遵循以下六大准则：

### 铁律 1：区域投篮意愿与热区结果解耦原则（方案 B）
* **机制本质**：14 项细分区域投篮倾向（底角、侧翼、弧顶等）本质上是球员在该位置触发投篮动作的**意愿与决策**，而热区图表（Shot Chart / Hot Zones）则是整个赛季战术跑位与投篮行为的**统计结果**。两者不可倒果为因。
* **标定准则**：细分热区投篮倾向不与历史热区强行绑定，而是根据球员在各距离维度的**战术决策意愿**进行平滑均衡配置。避免因人为过度拟合历史样本而导致球员在某些区域完全不敢出手的战术停滞现象。

### 铁律 2：运球动作门槛与年轻成长豁免机制
* **痛点问题**：2K22 原生名单中，大量防守型内线或蓝领球员（如戈贝尔、卡佩拉）残留有 30~50 的 Crossover、Spin 等花式运球倾向，导致比赛引擎中经常出现传统中锋在外线持球强行变向并被轻易抢断的严重失真。
* **常规门槛**：针对已定型的巅峰期或老将角色球员，若“控球能力（Ball Handle）< 60”，强制将 8 项花式运球倾向（`0x48D` ~ `0x494`）压低至 `0 ~ 5`，并将 `0x495 No Dribble Move`（直接加速/无花式）设为 `90 ~ 100`，从根本上锁死非受迫性运球失误。
* **成长豁免（Growth Bypass）**：**若球员处于成长发育期（通常年龄 ≤ 23 岁且具备控球潜力），且球队有培养其持球进攻能力的明确诉求，则无视上述门槛，为其保留合理的运球动作倾向，以刺激其在赛季演化中获得控球相关属性与徽章的持续成长。**

### 铁律 3：单打评级阶梯与年龄成长红利法则
* **成长红利期（年龄 ≤ 24 岁且定位为进攻核心新星）**：
  * 为其赋予充沛的单打成长权重，即便面对顶尖防守者（vs Elite / Good）也维持在中高水平（50 ~ 75），确保其在模拟中拥有充足的主攻球权，最大化触发单打属性的潜力兑现。
* **成熟与巅峰期球员（年龄 > 24 岁）**：严格执行三级阶梯逻辑：
  * **第一梯队（超巨 / 绝对单打核心，如杜兰特、东契奇、欧文）**：
    * `vs Elite`: 65 ~ 75 | `vs Good`: 80 ~ 85 | `vs Average`: 90 ~ 95 | `vs Poor`: 95 ~ 100
  * **第二梯队（合格主攻 / 战术二单，如米德尔顿、CJ·麦科勒姆）**：
    * `vs Elite`: 25 ~ 35 | `vs Good`: 50 ~ 60 | `vs Average`: 70 ~ 80 | `vs Poor`: 85 ~ 90
  * **第三梯队（定点 / 蓝领终结点，如布里奇斯、PJ·塔克）**：
    * `vs Elite`: 0 ~ 10 | `vs Good`: 15 ~ 25 | `vs Average`: 35 ~ 45 | `vs Poor`: 50 ~ 60

### 铁律 4：挡拆下顺与外弹的动态能力标定（拒绝极端化）
* **机制映射**：`0x49B Roll vs Pop` 为反向标量（0 为纯顺下攻筐，100 为纯外弹投篮）。
* **非极端准则**：**严禁设置 0 或 100 等极端极性数值**。任何现代内线都具备短挡拆停顿、高位策应或错位强打的选择。必须根据球员真实的“攻筐终结能力”与“中远投射能力”进行平滑比例换算：
  * **攻筐吃饼型内线（卡佩拉、阿伦、加福德）**：标定在 `15 ~ 25`（主顺下，但不丧失高位策应与假掩护能力）。
  * **高炮台空间型内线（唐斯、特纳、大洛佩斯）**：标定在 `75 ~ 85`（主外弹，但面对小个换防依然具备顺下惩罚能力）。
  * **全能双能内线（约基奇、恩比德、戴维斯）**：标定在 `45 ~ 55`（完全由防守方防挡拆策略决定顺下或外弹）。

### 铁律 5：防守核心犯规天花板安全锁
* **模拟失真隐患**：日历模拟中，高封盖意愿且犯规倾向超过 60 的内线（如小贾伦·杰克逊）会极高概率在 20 分钟内吃到 5~6 次犯规离场，导致核心球员出场时间与战绩严重失真。
* **安全天花板**：
  * **常规犯规（`0x4B9 Foul`）**：全联盟最高硬性天花板设定为 `45 ~ 50`。
  * **凶狠犯规（`0x4BA Hard Foul`）**：常规球员基线控制在 `0 ~ 15`；仅极少数球风强悍的战术恶汉（如狄龙·布鲁克斯、追梦格林）可设定为 `25 ~ 35`，严禁超过 40。

### 铁律 6：战术重力放大器与进攻发起权法则（核心与角色定位）
* **战术执行几率本质**：**Shot Tendency（`0x458` 出手总倾向）不仅是持球人终结意愿，更是 2K 战术体系中“每回合执行该球员专属战术”的最高权重调度器！**
  * 若某位球员的 Shot Tendency 显著高于队友，AI 教练每回合都会优先为该球员呼叫专属战术。
  * **战术重力放大效应**：正如约基奇或奥尼尔，球队核心的战术执行优先级最高，其目的往往不是自己强行出手，而是通过战术发起迫使对手陷入防守博弈（如包夹、延误、收缩），从而撕裂防线，为外线与空切队友创造大量绝对空位。
* **触球权（`0x499 Touches`）与出手总倾向（`0x458 Shot Tendency`）的协同矩阵**：
  * **全能持球大核（詹姆斯、东契奇）**：`Touches 90~95`，`Shot Tendency 85~90`（战术核心呼叫 + 绝对进攻终结）。
  * **组织策应枢纽（约基奇、哈利伯顿、保罗）**：`Touches 85~95`，`Shot Tendency 70~80`（极高的战术发起频率，但大量回合在创造优势后分球）。
  * **无球神射终结者（克莱·汤普森）**：`Touches 55~65`，`Shot Tendency 75~85`（不控球，但战术呼叫其反跑、绕掩护投篮的优先级极高）。
  * **定点角色球员（PJ·塔克、布洛克）**：`Touches 30~40`，`Shot Tendency 40~50`（完全不占用球队主动呼叫战术的回合，仅在绝对机会下出手）。

---

## 3. 全量 99 项倾向字段底层内存索引与标定映射总表

| 序号 | 偏移 (Hex) | 内存字段名 (REA Native Contract) | 游戏内 UI 标签 | 类别划分 | 建议取值区间 | 调校数学逻辑 / 战术功能描述 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `0x458` | `SHOT_TENDENCY` | Shot | 投篮主控 | 35 ~ 95 | **战术发起与终结总权重**。核心大核 80~95，主攻手 70~80，蓝领 35~50 |
| 2 | `0x459` | `DRIVING_LAYUP_TENDENCY` | Driving Layup | 攻筐终结 | 10 ~ 90 | 突破行进间上篮意愿。后卫/突破锋线 60~90，纯内线 10~30 |
| 3 | `0x45A` | `STANDING_DUNK_TENDENCY` | Standing Dunk | 攻筐终结 | 0 ~ 95 | 篮下原地暴扣。吃饼中锋 75~95，外线后卫 0~10 |
| 4 | `0x45B` | `DRIVING_DUNK_TENDENCY` | Driving Dunk | 攻筐终结 | 0 ~ 95 | 冲筐扣篮。莫兰特/字母哥 85~95，地板流射手 0~15 |
| 5 | `0x45C` | `FLASHY_DUNK_TENDENCY` | Flashy Dunk | 攻筐终结 | 0 ~ 80 | 快攻花式暴扣。扣将 40~80，实用派 0~10 |
| 6 | `0x45D` | `ALLEY_OOP_TENDENCY` | Alley-Oop Finish | 攻筐终结 | 0 ~ 90 | 空接扣篮/终结意愿。吃饼中锋/跳跳男 70~90 |
| 7 | `0x45E` | `PUTBACK_TENDENCY` | Putback | 攻筐终结 | 0 ~ 75 | 前场篮板直接补扣/补篮。前板狂魔 50~75，外线 0~15 |
| 8 | `0x45F` | `UNIDENTIFIED_TENDENCY_01` | Use Glass | 投篮技巧 | 0 ~ 70 | 投篮擦板意愿。邓肯/欧文打板 40~70，常规射手 5~15 |
| 9 | `0x460` | `CRASH_TENDENCY` | Crash | 篮板拼抢 | 10 ~ 85 | 冲抢前场篮板侵略性。防守后卫 10~25，冲抢锋线 60~85 |
| 10 | `0x461` | `SPIN_LAYUP_TENDENCY` | Spin Layup | 攻筐技巧 | 0 ~ 65 | 突破中转身挑篮。技巧型后卫 25~65，内线 0~5 |
| 11 | `0x462` | `HOP_STEP_LAYUP_TENDENCY` | Hop Step Layup | 攻筐技巧 | 0 ~ 70 | 跳步上篮。哈登/字母哥 40~70 |
| 12 | `0x463` | `EURO_STEP_LAYUP_TENDENCY` | Euro Step Layup | 攻筐技巧 | 0 ~ 80 | 欧洲步上篮。吉诺比利/韦德/哈登 50~80 |
| 13 | `0x464` | `UNIDENTIFIED_TENDENCY_02` | Shot Close | 基础投篮 | 20 ~ 95 | 禁区附近近距离投篮（5-10英尺）意愿 |
| 14 | `0x465` | `FLOATER_TENDENCY` | Floater | 攻筐技巧 | 0 ~ 85 | 抛投倾向。特雷·杨/保罗 60~85，长人内线 0~10 |
| 15 | `0x466` | `UNIDENTIFIED_TENDENCY_03` | Under Basket Shot | 区域热区 | 25 ~ 95 | 合理冲撞区正下方投篮意愿 |
| 16 | `0x467` | `UNIDENTIFIED_TENDENCY_04` | Close Shot Left | 区域热区 | 20 ~ 80 | 近距离左侧投篮意愿（平滑均衡配置） |
| 17 | `0x468` | `UNIDENTIFIED_TENDENCY_05` | Close Shot Middle | 区域热区 | 20 ~ 80 | 近距离中路投篮意愿（平滑均衡配置） |
| 18 | `0x469` | `UNIDENTIFIED_TENDENCY_06` | Close Shot Right | 区域热区 | 20 ~ 80 | 近距离右侧投篮意愿（平滑均衡配置） |
| 19 | `0x46A` | `UNIDENTIFIED_TENDENCY_07` | Mid-Range Shot | 基础投篮 | 5 ~ 95 | 中距离总出手倾向。德罗赞/杜兰特 85~95，魔球射手 5~20 |
| 20 | `0x46B` | `UNIDENTIFIED_TENDENCY_08` | Spot Up Mid-Range | 投篮形式 | 5 ~ 85 | 定点接球中投。定点内线/锋线 50~85 |
| 21 | `0x46C` | `UNIDENTIFIED_TENDENCY_09` | Off Screen Mid-Range | 投篮形式 | 0 ~ 85 | 绕掩护接球中投。汉密尔顿/克莱 60~85 |
| 22 | `0x46D` | `UNIDENTIFIED_TENDENCY_10` | Mid Left | 区域热区 | 15 ~ 75 | 中距离左侧区域投篮意愿（平滑配置） |
| 23 | `0x46E` | `UNIDENTIFIED_TENDENCY_11` | Mid Left-Center | 区域热区 | 15 ~ 75 | 中距离左肋区域投篮意愿（平滑配置） |
| 24 | `0x46F` | `UNIDENTIFIED_TENDENCY_12` | Mid Center | 区域热区 | 15 ~ 75 | 中距离正顶弧投篮意愿（平滑配置） |
| 25 | `0x470` | `UNIDENTIFIED_TENDENCY_13` | Mid Right-Center | 区域热区 | 15 ~ 75 | 中距离右肋区域投篮意愿（平滑配置） |
| 26 | `0x471` | `UNIDENTIFIED_TENDENCY_14` | Mid Right | 区域热区 | 15 ~ 75 | 中距离右侧区域投篮意愿（平滑配置） |
| 27 | `0x472` | `UNIDENTIFIED_TENDENCY_15` | 3PT Shot | 基础投篮 | 0 ~ 95 | 三分球总出手倾向。库里 95，西蒙斯 0 |
| 28 | `0x473` | `UNIDENTIFIED_TENDENCY_16` | Spot Up 3PT | 投篮形式 | 0 ~ 95 | 定点接球投三分。底角射手 85~95 |
| 29 | `0x474` | `UNIDENTIFIED_TENDENCY_17` | Off Screen 3PT | 投篮形式 | 0 ~ 95 | 绕掩护投三分。库里/克莱 85~95 |
| 30 | `0x475` | `UNIDENTIFIED_TENDENCY_18` | 3PT Left | 区域热区 | 10 ~ 85 | 三分左底角投篮意愿（平滑配置） |
| 31 | `0x476` | `UNIDENTIFIED_TENDENCY_19` | 3PT Left-Center | 区域热区 | 10 ~ 85 | 三分左侧翼投篮意愿（平滑配置） |
| 32 | `0x477` | `UNIDENTIFIED_TENDENCY_20` | 3PT Center | 区域热区 | 10 ~ 85 | 三分正顶弧投篮意愿（平滑配置） |
| 33 | `0x478` | `UNIDENTIFIED_TENDENCY_21` | 3PT Right-Center | 区域热区 | 10 ~ 85 | 三分右侧翼投篮意愿（平滑配置） |
| 34 | `0x479` | `UNIDENTIFIED_TENDENCY_22` | 3PT Right | 区域热区 | 10 ~ 85 | 三分右底角投篮意愿（平滑配置） |
| 35 | `0x47A` | `UNIDENTIFIED_TENDENCY_23` | Contested Mid-Range | 强投意愿 | 0 ~ 85 | 顶人强投中距离。科比/杜兰特 65~85，普通球员 10~25 |
| 36 | `0x47B` | `UNIDENTIFIED_TENDENCY_24` | Contested 3PT | 强投意愿 | 0 ~ 85 | 顶人强投三分。库里/利拉德 60~85，角色球员 5~20 |
| 37 | `0x47C` | `UNIDENTIFIED_TENDENCY_25` | Stepback Mid-Range | 技巧跳投 | 0 ~ 80 | 后撤步中投。东契奇/欧文 50~80 |
| 38 | `0x47D` | `UNIDENTIFIED_TENDENCY_26` | Stepback 3PT | 技巧跳投 | 0 ~ 90 | 后撤步三分。哈登/东契奇 75~90 |
| 39 | `0x47E` | `UNIDENTIFIED_TENDENCY_27` | Spin Jumper | 技巧跳投 | 0 ~ 65 | 转身跳投。科比/乔治 40~65 |
| 40 | `0x47F` | `UNIDENTIFIED_TENDENCY_28` | Step Through Shot | 技巧跳投 | 0 ~ 60 | 上下步交叉步挑篮/跳投。皮尔斯 40~60 |
| 41 | `0x480` | `UNIDENTIFIED_TENDENCY_29` | Transition Pull-Up 3PT| 投篮形式 | 0 ~ 85 | 快攻转换抢投三分。库里/特雷·杨 65~85 |
| 42 | `0x481` | `UNIDENTIFIED_TENDENCY_30` | Drive Pull-Up Jumper | 投篮形式 | 5 ~ 85 | 持球急停跳投。保罗/布克 70~85 |
| 43 | `0x482` | `DRIVE_RIGHT_TENDENCY` | Drive Right | 突破路线 | 30 ~ 70 | 顺步右侧突破偏好（50 为左右绝对均衡） |
| 44 | `0x483` | `DRIVE_TENDENCY` | Drive | 突破总控 | 10 ~ 95 | 持球突破总意愿。字母哥/莫兰特 85~95 |
| 45 | `0x484` | `SPOT_UP_DRIVE_TENDENCY`| Spot Up Drive | 突破形式 | 10 ~ 75 | 定点接球假投后强突。突破侧翼 50~75 |
| 46 | `0x485` | `OFF_SCREEN_DRIVE_TENDENCY`| Off Screen Drive | 突破形式 | 5 ~ 75 | 绕掩护接球顺势攻筐 |
| 47 | `0x486` | `PUMP_FAKE_TENDENCY` | Triple Threat Pump Fake| 三威胁动作 | 10 ~ 80 | 三威胁假投虚晃。甜瓜/德罗赞 60~80 |
| 48 | `0x487` | `JAB_STEP_TENDENCY` | Triple Threat Jab Step | 三威胁动作 | 10 ~ 85 | 三威胁刺探步。甜瓜 85 |
| 49 | `0x488` | `IDLE_TENDENCY` | Triple Threat Idle | 三威胁动作 | 10 ~ 60 | 三威胁持球静止观察 |
| 50 | `0x489` | `SHOOT_FROM_TRIPLE_THREAT`| Shoot From Triple Threat| 三威胁动作| 10 ~ 80 | 三威胁直接干拔起跳投篮 |
| 51 | `0x48A` | `SIZEUP_TENDENCY` | Sizeup | 起步准备 | 5 ~ 90 | 运球节奏试探（Sizeup）。控球后卫 65~90 |
| 52 | `0x48B` | `HESITATION_TENDENCY` | Hesitation Setup | 起步准备 | 5 ~ 85 | 拜佛/迟疑步启动。保罗/欧文 65~85 |
| 53 | `0x48C` | `NO_SETUP_MOVE_TENDENCY`| No Setup Move | 起步准备 | 15 ~ 95 | 无多余动作直接启动（直线加速型球员偏高） |
| 54 | `0x48D` | `CROSSOVER_TENDENCY` | Crossover Move | 运球动作 | 0 ~ 90 | 体前变向。控卫 60~90；**蓝领内线受门槛保护 ≤5** |
| 55 | `0x48E` | `SPIN_MOVE_TENDENCY` | Spin Move | 运球动作 | 0 ~ 85 | 运球转身。西卡/字母哥 65~85；**蓝领内线 ≤5** |
| 56 | `0x48F` | `STEP_BACK_MOVE_TENDENCY`| Step Back Move | 运球动作 | 0 ~ 90 | 运球后撤步。哈登 90；**蓝领内线 ≤5** |
| 57 | `0x490` | `HALF_SPIN_TENDENCY` | Half Spin | 运球动作 | 0 ~ 75 | 半转身虚晃。欧文 75；**蓝领内线 ≤5** |
| 58 | `0x491` | `DOUBLE_CROSS_TENDENCY` | Double Cross | 运球动作 | 0 ~ 80 | 双重变向。库里 80；**蓝领内线 ≤5** |
| 59 | `0x492` | `BEHIND_BACK_TENDENCY` | Behind Back | 运球动作 | 0 ~ 85 | 背后运球。沃尔/福克斯 75~85；**蓝领内线 ≤5** |
| 60 | `0x493` | `HESITATION_MOVE_TENDENCY`| Hesitation Move | 运球动作 | 0 ~ 85 | 行进间拜佛。杜兰特 75~85；**蓝领内线 ≤5** |
| 61 | `0x494` | `IN_AND_OUT_TENDENCY` | In-and-Out | 运球动作 | 0 ~ 80 | 内外侧运球晃动。保罗 75~80；**蓝领内线 ≤5** |
| 62 | `0x495` | `NO_MOVE_TENDENCY` | No Move Dribble | 运球动作 | 10 ~ 95 | 纯直线加速突击。**蓝领中锋受保护设为 90~95** |
| 63 | `0x496` | `ATTACK_STRONG_TENDENCY`| Attack Strong | 进攻侵略性 | 15 ~ 95 | 顶人强攻意愿。威少/锡安 90~95 |
| 64 | `0x497` | `UNIDENTIFIED_TENDENCY_31`| Play Discipline | 战术纪律 | 20 ~ 95 | 严格等待战术跑出机会（高）vs 自行即兴单打（低） |
| 65 | `0x498` | `DISH_TO_OPEN_MAN_TENDENCY`| Dish To Open Man | 组织分球 | 15 ~ 95 | 突破吸引包夹后分球给空位。哈利伯顿 95，欧文 35 |
| 66 | `0x499` | `TOUCHES_TENDENCY` | Touches | 球权核心 | 25 ~ 95 | **触球主控权**。组织核心 85~95，终结者 50~65，蓝领 25~40 |
| 67 | `0x49A` | `POST_UP_TENDENCY` | Post Up | 低位总控 | 0 ~ 95 | 背身落位要球总意愿。恩比德/约基奇 85~95，纯后卫 0~10 |
| 68 | `0x49B` | `ROLL_VS_POP_TENDENCY` | Roll vs Pop | 挡拆决策 | 15 ~ 85 | **挡拆选择**。0 顺下，100 外弹。**严禁极端值，动态平滑标定** |
| 69 | `0x49C` | `TRANSITION_SPOT_UP_3PT`| Transition Spot Up | 快攻跑位 | 10 ~ 85 | 快攻中奔赴两侧底角/弧顶就位投三分 |
| 70 | `0x49D` | `ISO_VS_ELITE_DEFENDER` | ISO vs Elite | 单打分层 | 0 ~ 75 | 面对精英防守者单打欲望（遵循成长红利与三级阶梯） |
| 71 | `0x49E` | `ISO_VS_GOOD_DEFENDER` | ISO vs Good | 单打分层 | 15 ~ 85 | 面对良好防守者单打欲望 |
| 72 | `0x49F` | `ISO_VS_AVERAGE_DEFENDER`| ISO vs Average | 单打分层 | 35 ~ 95 | 面对中等防守者单打欲望 |
| 73 | `0x4A0` | `ISO_VS_POOR_DEFENDER` | ISO vs Poor | 单打分层 | 50 ~ 100| 面对防守漏勺/错位点名单打欲望 |
| 74 | `0x4A1` | `POST_SHIMMY_TENDENCY` | Post Shimmy | 低位技巧 | 0 ~ 75 | 背身后晃肩假动作。科比/恩比德 50~75 |
| 75 | `0x4A2` | `POST_FACE_UP_TENDENCY` | Post Face Up | 低位技巧 | 0 ~ 85 | 背身接球后转面框单打。诺维茨基/字母哥 60~85 |
| 76 | `0x4A3` | `POST_BACKDOWN_TENDENCY`| Post Backdown | 低位技巧 | 0 ~ 90 | 持续背身向禁区压制推进。奥尼尔 90 |
| 77 | `0x4A4` | `AGGRESSIVE_BACKDOWN_TEND`| Aggressive Backdown | 低位技巧 | 0 ~ 85 | 强力发力顶开防守人。锡安/字母哥 75~85 |
| 78 | `0x4A5` | `SHOOT_FROM_POST_TENDENCY`| Shoot From Post | 低位终结 | 0 ~ 85 | 低位背身直接起球终结意愿 |
| 79 | `0x4A6` | `POST_HOOK_LEFT_TENDENCY`| Post Hook Left | 低位终结 | 0 ~ 80 | 左手低位勾手。贾巴尔 80 |
| 80 | `0x4A7` | `POST_HOOK_RIGHT_TENDENCY`| Post Hook Right | 低位终结 | 0 ~ 90 | 右手低位勾手。约基奇/恩比德 75~90 |
| 81 | `0x4A8` | `POST_FADE_LEFT_TENDENCY`| Post Fade Left | 低位终结 | 0 ~ 85 | 左侧翻身后仰跳投。科比 85 |
| 82 | `0x4A9` | `POST_FADE_RIGHT_TENDENCY`| Post Fade Right | 低位终结 | 0 ~ 85 | 右侧翻身后仰跳投。杜兰特 85 |
| 83 | `0x4AA` | `POST_UP_AND_UNDER_TEND` | Post Up and Under | 低位技巧 | 0 ~ 80 | 上下步虚晃假动作骗起防守再终结。斯科拉/麦克海尔 75~80 |
| 84 | `0x4AB` | `POST_HOP_SHOT_TENDENCY`| Post Hop Shot | 低位技巧 | 0 ~ 70 | 背身跳步投篮 |
| 85 | `0x4AC` | `POST_STEPBACK_TENDENCY`| Post Stepback | 低位技巧 | 0 ~ 75 | 背身后撤步跳投 |
| 86 | `0x4AD` | `POST_DRIVE_TENDENCY` | Post Drive | 低位技巧 | 0 ~ 80 | 背身顺步直接抹向篮下 |
| 87 | `0x4AE` | `POST_SPIN_TENDENCY` | Post Spin | 低位技巧 | 0 ~ 85 | 背身突然转身抹过防守人 |
| 88 | `0x4AF` | `POST_DROP_STEP_TENDENCY`| Post Drop Step | 低位终结 | 0 ~ 90 | 经典低位沉底步强起。奥尼尔/霍华德 80~90 |
| 89 | `0x4B0` | `POST_HOP_STEP_TENDENCY`| Post Hop Step | 低位技巧 | 0 ~ 75 | 低位跨步合球终结 |
| 90 | `0x4B1` | `FLASHY_PASS_TENDENCY` | Flashy Pass | 传球风格 | 0 ~ 75 | 不看人/花式传球。白巧克力 75，稳健控卫 5~15 |
| 91 | `0x4B2` | `ALLEY_OOP_PASS_TENDENCY`| Alley-Oop Pass | 传球风格 | 5 ~ 85 | 抛投空接意愿。特雷·杨/哈登 75~85 |
| 92 | `0x4B3` | `PASS_INTERCEPTION_TEND`| Pass Interception | 防守侵略 | 20 ~ 90 | 判断传球路线飞身抢断。抢断王/长臂怪 75~90 |
| 93 | `0x4B4` | `TAKE_CHARGE_TENDENCY` | Take Charge | 防守风格 | 0 ~ 75 | 舍身造进攻犯规。洛瑞/瓦兰 60~75 |
| 94 | `0x4B5` | `ON_BALL_STEAL_TENDENCY` | On-Ball Steal | 防守侵略 | 15 ~ 85 | 贴身下手逼抢/抢断控球人。保罗/巴特勒 70~85 |
| 95 | `0x4B6` | `CONTEST_SHOT_TENDENCY` | Contest Shot | 防守态度 | 40 ~ 95 | 扬手扑防投篮态度。防守大闸 85~95，防守走神者 40~55 |
| 96 | `0x4B7` | `BLOCK_SHOT_TENDENCY` | Block Shot | 防守护筐 | 5 ~ 95 | 起跳封盖意愿。大白边/特纳 85~95，地板后卫 5~20 |
| 97 | `0x4B8` | `FOUL_TENDENCY` | Foul | 纪律防守 | 15 ~ **50** | **普通犯规倾向**。**受铁律 5 约束，全联盟最高锁定在 50** |
| 98 | `0x4B9` | `HARD_FOUL_TENDENCY` | Hard Foul | 纪律防守 | 0 ~ **35** | **凶狠犯规倾向**。**常规球员 ≤15，极少数恶汉上限 35** |
| 99 | `0x4BA` | `UNIDENTIFIED_TENDENCY_45`| Fast Break Foul | 战术犯规 | 10 ~ 65 | 快攻战术犯规（点球破坏转换）意愿 |

---

## 4. 六大典型战术角色配置模板矩阵 (Archetype Matrices)

为确保模型在面对具体球员时能瞬间调取对应的战术几何结构，固化以下 6 种经典球员原型的倾向基线：

### 模板 1：全能持球进攻大核 (Alpha Engine - 如卢卡·东契奇、勒布朗·詹姆斯)
* **核心权重**：`Shot Tendency: 88` | `Touches: 95` | `Dish To Open Man: 80`
* **终结偏好**：`Drive: 85` | `Stepback 3PT: 88` | `Floater: 75` | `Contested 3PT: 70`
* **单打分级**：`vs Elite: 70` | `vs Good: 85` | `vs Average: 95` | `vs Poor: 100`
* **战术逻辑**：每回合绝对的第一战术发起人，通过高持球与单打重力吸纳包夹后突分，全面带动体系。

### 模板 2：战术策应枢纽 (Tactical Hub - 如尼古拉·约基奇、德雷蒙德·格林)
* **核心权重**：`Shot Tendency: 78` | `Touches: 92` | `Dish To Open Man: 95`
* **终结偏好**：`Post Up: 88` | `Post Hook Right: 85` | `Play Discipline: 85` | `Floater: 80`
* **挡拆协同**：`Roll vs Pop: 50`（绝对均衡，视防守策略动态选择）
* **战术逻辑**：战术呼叫率极高，通过高位或低位发起战术，迫使防守变换阵型，优先为队友创造大空位。

### 模板 3：无球跑动神射终结者 (Movement Sniper - 如克莱·汤普森、雷迪克)
* **核心权重**：`Shot Tendency: 82` | `Touches: 58` | `Dish To Open Man: 25`
* **终结偏好**：`Spot Up 3PT: 95` | `Off Screen 3PT: 95` | `Drive: 35` | `Contested 3PT: 55`
* **运球保护**：`No Setup Move: 80` | `No Move Dribble: 85` | `Crossover: 15`
* **战术逻辑**：不控球但战术执行频率极高，AI 教练频繁呼叫战术为其跑出掩护空位，接球瞬间高度果断出手。

### 模板 4：护筐吃饼传统中锋 (Rim Rolling Anchor - 如克林特·卡佩拉、鲁迪·戈贝尔)
* **核心权重**：`Shot Tendency: 45` | `Touches: 35` | `Dish To Open Man: 15`
* **终结偏好**：`Standing Dunk: 90` | `Driving Dunk: 80` | `Alley-Oop: 90` | `Putback: 75` | `Shot 3PT: 0`
* **挡拆偏好**：`Roll vs Pop: 20`（主顺下，绝不极端化设为 0）
* **运球安全门槛 (铁律 2)**：除 `No Move: 95` 外，所有花式运球全量压制在 `0 ~ 5`
* **防守安全锁 (铁律 5)**：`Block Shot: 90` | `Foul: 45 (上限受控)` | `Hard Foul: 15`

### 模板 5：空间型五号位高炮台 (Stretch Big - 如卡尔-安东尼·唐斯、迈尔斯·特纳)
* **核心权重**：`Shot Tendency: 75` | `Touches: 65` | `Dish To Open Man: 45`
* **终结偏好**：`3PT Shot: 82` | `Spot Up 3PT: 85` | `Post Up: 60` | `Driving Layup: 45`
* **挡拆偏好**：`Roll vs Pop: 80`（主外弹跳投，保留 20 顺下强攻错位）
* **防守安全锁 (铁律 5)**：`Block Shot: 80` | `Foul: 42` | `Hard Foul: 10`

### 模板 6：成长期待培养新星 (Young Prospect - 如杰伦·格林、凯德·坎宁安)
* **核心权重**：`Shot Tendency: 78` | `Touches: 80` | `Dish To Open Man: 65`
* **成长豁免红利 (铁律 2 & 3)**：
  * 无视控球能力门槛：保留 `Crossover: 65`、`Hesitation: 60`、`Stepback: 65`，全面激发持球属性成长；
  * 赋予越级单打红利：`vs Elite: 60` | `vs Good: 75` | `vs Average: 85` | `vs Poor: 95`，保障成长期间的回合占有率。

---

## 5. REA 实机执行包落地规范与校验准则

依据 [43 号接口协议](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) 第 5 节三大铁律，在针对各队生成球员倾向的更新执行包时，执行如下规范：

1. **绝对纯差分零占位**：仅提取当前球队中**确实需要调整倾向的球员**，仅包含**发生数值变动的倾向键值**。严禁填充未改动倾向，严禁输出占位符。
2. **字段标识一致性**：JSON 键名使用标准的 16 进制偏移字符串（如 `"0x458"`）或 REA 契约字段名（如 `"SHOT_TENDENCY"`），由执行器原生解析器（Native Dispatcher）直接寻址到内存块。
3. **数据格式范例**：
```json
{
  "task_metadata": {
    "task_id": "CYCLE_02_TEAM_TENDENCY_CALIBRATION",
    "team_id": 14,
    "team_name": "Indiana Pacers",
    "protocol_version": "v2_sparse_delta",
    "generated_at": "2026-11-24"
  },
  "player_tendency_updates": [
    {
      "player_id": 1630169,
      "player_name": "Tyrese Haliburton",
      "tendency_deltas": {
        "0x458": 74,
        "0x499": 92,
        "0x498": 95,
        "0x472": 82,
        "0x480": 70,
        "0x4B9": 35
      }
    }
  ]
}
```

---

## 6. 附录：核心哨兵球员核验基线 (Sentinel Roster)

任何针对全联盟或分队倾向的批量更新包发布前，必须在本地或内存镜像中抽检以下哨兵球员，确保未发生逻辑漂移：
* **哨兵 1：泰雷斯·哈利伯顿 (Tyrese Haliburton, UID: 1630169)**
  * `Touches (0x499)` ≥ 90 且 `Dish To Open Man (0x498)` ≥ 92；`Shot Tendency (0x458)` 控制在 70~76 之间。
* **哨兵 2：克莱·汤普森 (Klay Thompson, UID: 202691)**
  * `Touches (0x499)` ≤ 65 且 `Spot Up 3PT (0x473)` ≥ 92；`Shot Tendency (0x458)` 维持在 80~85。
* **哨兵 3：尼古拉·约基奇 (Nikola Jokic, UID: 203999)**
  * `Roll vs Pop (0x49B)` 必须在 45~55 之间；`Post Up (0x49A)` ≥ 85。
* **哨兵 4：鲁迪·戈贝尔 (Rudy Gobert, UID: 203497)**
  * `Crossover (0x48D)` 与 `Spin (0x48E)` ≤ 5；`No Move (0x495)` ≥ 90；`Foul (0x4B9)` ≤ 48。
