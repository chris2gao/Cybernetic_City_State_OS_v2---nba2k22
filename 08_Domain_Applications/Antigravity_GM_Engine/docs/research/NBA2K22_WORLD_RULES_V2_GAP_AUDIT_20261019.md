# NBA2K22 世界规则 V2：类别2–6缺口审查与执行优先级

2026-10-19；研究型补充，未批准修改游戏。此前世界规则V1：docs/research/NBA2K22_EXTERNAL_GM_MYLEAGUE_WORLD_SETTINGS_V1_20261019.md。

玩家转述Antigravity的SLOT_TRADE、SLOT_FRANCHISE、GAMEMODE_SETTINGS_SAVED_PROFILE、字段与地址摘要；没有提供其完整原始数值与持久化读回表，因此本报告不能把地址和字段作用系数称为已独立验证。世界规则与GM单队运营权限分离：Antigravity已开始DEV12 V2，包含类别4；交易原生估值已由外挂GM替代。所有人物原始能力、潜力和徽章禁止普通GM直接编辑，个体行为倾向可提案，但正式操作仍需玩家批准。

## 1. 分类决定

| 类别 | 状态 | V2处理 |
|---|---|---|
| 2 日历Sim Engine | 漏项，重要 | 建立独立SIM_PROFILE，真实2021–22统计目标，先读原生raw并审计批次统计，再按有证据的完整配置确定数值，不瞎按NBA百分比填写0–100原生滑块 |
| 3 个人生涯成长/衰退曲线 | 漏项，重要 | 48总成长/50总衰退继续仅作为V1候选，三阶段各属性原值先保持，研究运动能力与篮球IQ不同衰减；区分原生个人Peak值与世界生成规则 |
| 4 阵容/教练/逐人防守/训练 | 已交付开发任务 | Antigravity DEV12 V2负责，不重开Codex任务 |
| 5 生成新秀品质 | 大多非主路径 | 每年导入1984–2020历史班，品质/潜力/徽章/耐久度生成滑块默认；Storylines优先关闭，审计是否偷偷改变导入数据 |
| 6 原生交易估值 | 本项目无必要调整 | 所有Year2–5 depreciation、9类PlayerType discount、重建/争冠相对价值原版默认；真实价格由30队独立GM协商模型决定 |

## 2. 日历模拟：提供真实统计基准，不编滑块映射

NBA.com统计回顾2021–22：联盟PPG110.6、Pace98.8（其口径）、OffRtg111.4、FG46.1%、3P35.4%、三分出手占比39.9%、eFG53.2%、TO率13.9%。Basketball-Reference同季每队场均约35.2次三分、88.1次整体投篮、24.6次助攻、13.8次失误、19.6次犯规。不同数据源的Pace算法有差异，固定一个主参考，不混用。

来源：https://api-hub.nba.com/news/2023-24-nba-stats-survey-league-scoring-averages
https://www.basketball-reference.com/leagues/NBA_stats_per_game.html

| 设置组 | 初版世界配置 | 应看哪类结果 |
|---|---|---|
| SimulatorPossessions、TeamPace、FastBreak | 当前原生raw，暂HOLD | 按当前同季游戏快照计算PACE、进攻回合和PPG |
| SimulatorShotSelection (Dunk/Layup/Close/Mid/3PT) | 当前原生raw，暂HOLD | 三分出手占比及球队间差异、出手结构 |
| SimulatorShootingSuccess (各距离/FT) | 当前原生raw，暂HOLD | 命中率、eFG、罚球及优秀射手与普通人差异 |
| Turnovers/Fouls/Assists/Steals/Blocks/Rebounds | 当前原生raw，暂HOLD | NBA2021–22同口径联盟分布 |
| Sim Fatigue/Recovery/Injuries | 与训练和伤病世界配置统一；暂HOLD | 不重复放大训练负荷、伤病事件 |
| CPUAttributeBoost | FIELD_SEMANTICS_UNVERIFIED，暂HOLD | 需Antigravity提供真实UI描述、原值、方向；不能直接假定其为强队隐藏加成 |

NBA2K22 PS4 2021年的实际用户研究DarthRambo发布过 TeamPace100、Possessions100、ShotMedium70、ShotThree55等完整模拟套装；RealSport101给出了Pace49、Possessions49、ShotThree80等差异很大的完整套装。部分套装还依赖改变大量个体倾向和11分钟Sim Quarter，不能把数值直接拆出到我们的12分钟世界。资料：
https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders
https://realsport101.fly.dev/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes

**GM分析关联**：赛季日历模拟会产生球员/球队数据；SIM_PROFILE的全球变化不属于某队GM战术决策，不准把模拟结构性偏差解释成“球队必须交易”。胜负与联盟总数据分别审计，不模拟指定2022冠军。

## 3. 成长/衰退：三阶段不等于指定年龄

| 项 | 初版建议 | 重点 |
|---|---|---|
| 总体Progression/Regression | 48/50继续列为V1候选，不标最优 | 只影响总体速率，不能保证某位历史超巨必成名 |
| PeakStart/PeakEnd相关全局字段 | 原版HOLD；先定位是否是生成分布或个人字段 | 不强制全联盟28岁开始下滑 |
| 属性Growth/Peak/Decline各曲线 | 原版HOLD（保存全部当前raw） | 技术/IQ和身体衰退差异值得后续研究，但缺2K22最优整套 |
| BadgeProgression/Regression | 默认50/50（如果该局默认确是50），否则当前原值 | 自然升降徽章，GM不直接加徽章 |
| GLeague训练效果 | 原值HOLD；留意过快成长及历史新秀膨胀 | 跨年份存在GLeague超常成长案例，不代表本局必有 |
| 训练强度、体力与导师 | Antigravity DEV12 | GM设训练投入→游戏自然成长，不能直接改Ability |

关键成熟参照：Comduklakis 2019年发表完整多项三阶段数字，如Speed 12/-5/-30、Acceleration 12/-5/-30、LateralQuickness 12/-5/-38、ShotIQ 75/15/+5、PassIQ 75/22/+5、Strength 75/15/0；这属于NBA2K20玩家完整经验，并非NBA2K22官方曲线，不能把“Speed下降30”直接解读为30岁速度下降。
https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/882284-regression-progression-and-contract-sliders
Barnsey对身体机能先衰退、成熟后IQ较稳定的篮球解释可作研究框架：
https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/863174-barnsey-s-myleague-player-progression-regression-sliders-2k19

游戏各项滑块未必是所有能力变化的唯一入口：2021年玩家报告将Progression/Regression及分项设0后，赛季末仍看到部分能力变化。https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916343-disabling-player-progression-regression

## 4. DEV12已涵盖类别4，不重复开发

Antigravity负责Playbook、球员4个有序PlayTypes、Tendencies、逐人防守、教练能力/体系和训练。世界只设置权限、默认和跨系统接口：ACE一直ON，原版AI完成临场战术与换人；个人分钟此前玩家实测会被AI重排。Antigravity提出可以写Target Minutes与CrunchTime5不代表已证明比赛会持续遵从，更不自动重新启用“强制锁分钟”开发，需玩家更新需求并完成真正实战持久化取证。已有19默认+18对手整体防守实现不可被新Personal防守无声覆盖。

权威任务：docs/development_tasks/DEV_20261019_12_V2_ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING.md

## 5. 历史班不是随机生成班：最需防止静默篡改

| 原生候选设置 | 初版建议 | 验证 |
|---|---|---|
| DraftClassQuality | 保持当前原版值（一般50，实际需读回）；不调40–45 | 导入历史班时有效人物、是否混入虚构补位球员 |
| ProspectPotentialDistribution | 默认/HOLD | 导入后是否重排历史新秀原始Potential |
| ProspectBadgeQuality | 默认/HOLD | 是否改变历史班Badge |
| ProspectDurabilityQuality | 默认/HOLD | 是否改变原始耐久度 |
| DraftStorylines | 若PC2K22有此开关，优先OFF | 历史导入前后Ability/Potential/Badge/Durability等原值一致性检查，不保证OFF即可绝对禁止改动 |

跨版历史经验提醒：MyLeague 2016年玩家认为DraftStorylines会带来导入班原始能力波动；2022年NBA2K23玩家报告OFF也不能阻止某些随机化。**都不是本项目NBA2K22已证bug**，只能驱动身份/属性哈希审计。
https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/813835-draft-class-storylines-what-are-they
https://www.reddit.com/r/NBA2k/comments/xyqxu1

历史班每年固定1984→2020循环，一年最多60个选秀席位。尤其注意某些历史班实际有效真实球员不足60、剩余自动生成新秀可能进入球员池；品质滑块作用于生成补位者还是导入班必须取证。虚拟球探以后用信息滤镜而不是改真实新秀能力。

## 6. 原生交易估值：无需为外挂GM调原生数字

Year2–5选秀权衰减、9种球员类型折价、各队Contending/Buying/Selling/Rebuilding选秀偏好、NetValue、年龄/Fame/Untouchable/Overall等原版估值全部保持默认。因为CPU-CPU与原生报价均关闭、30队GM独立议价且用户审批，改变2K报价系数不会产生我们期望的GM谈判。当前外挂可交易选秀权只覆盖三年窗口，Year4/5的原生滑块对外挂甚至没有可用资产。

另一风险：提高原生Pick Depreciation raw不一定提高“贬值”，Year2=90常可能代表相对价值保留90，用户转述中的“调高以防止廉价囤签”需要核查语义。比较2K22玩家方案不同：https://diamondlobby.com/nba-2k22/create-a-superteam-nba-2k22-myleague/ 。

正确做法是GM根据阵容年龄、合同剩余、潜在乐透概率、三年资产窗口和目标时代选秀班中真实战力来估值，并由独立30队GM基于各自赢球哲学谈判。原生Trade相关开关只保留执行需要的结构与原生自动交易OFF。

## 7. 更容易漏掉、比类别6更重要的世界规则

1. 退役/伤退、球员被裁去向、自由球员池生存、赛季末自动补员、每年60选秀名额中真实历史人物与虚构补位人数——联盟人口和长期人才供给的守恒。
2. 2021–22真实工资帽/税线/附加硬帽、原生年度通胀与外挂真实年度工资表的互斥；员工合同、税款、现金扣费要有一次而不是两个系统重复记账。
3. 日历模拟伤病/体力/训练与3D赛场伤病独立来源，不对同一球员重复叠加；年度时间快照及原始设定追溯。
4. 30队USER经营和全部交易/选秀/签约自动化Manual，比赛参与Auto、ACE ON；USER拥有球队不证明其两队3D比赛均用USER滑块。
5. 2021版游戏引擎不随1984历史班循环自动回到1980年代比赛规则；历史新秀循环仅是人才来源，除非另得用户授权才引入年代式联盟统一出手/节奏规则。
6. 教练体系/球员Tendencies影响3D与日历Sim的具体权重尚未证实，GM应分别说明LIVE_3D / CALENDAR_SIM效果证据，不发明统一公式。
7. 世界规则版本需保存game build/career/batch/原生raw/外部规则与玩家审批，常规GM每月只能改球队经营不重新调全球成长系数。

## 8. 需要Antigravity现有完整设置表的最小字段

至少须有字段名（UI英文中文）、当前raw、原版raw、合法值域/类型、类别/存储范围、读取与写入状态、保存后是否仍生效、谁消费此设置（模拟/实时3D/随机新秀生成/原生AI市场）。重点补类别2全套Simulation、类别3分项三阶段曲线、类别5历史导入与DraftStorylines、CPUAttributeBoost语义。

结论：下一份正式WORLD_PROFILE_V2应增加SIM_PROFILE、ATTRIBUTE_CURVE_PROFILE、HISTORICAL_DRAFT_INTEGRITY和RETIREMENT_ROSTER_ECOLOGY四块；类别4走Antigravity DEV12，类别6只留原生默认，由外挂GM估值。
