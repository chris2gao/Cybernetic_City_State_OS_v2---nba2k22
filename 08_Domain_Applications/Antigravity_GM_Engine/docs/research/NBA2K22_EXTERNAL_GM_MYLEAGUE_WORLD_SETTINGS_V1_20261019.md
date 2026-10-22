# NBA2K22 外挂GM专用终极联盟世界规则 V1：完整设置提案

> **2026-10-19 世界规则后续缺口审查**：类别二日历模拟真实性和类别三100+成长曲线，以及历史导入班随机修改风险、联盟退役/自动补员，原V1尚不完整；[世界规则V2缺口审查](NBA2K22_WORLD_RULES_V2_GAP_AUDIT_20261019.md)已分类标出优先级、保留/修改条件和缺失的Antigravity原值证据。类别四直接交Antigravity DEV12 V2，类别六原生交易估值已被外挂GM替代无需优化。V2是补充调查，不等于已批准或已经修改本机游戏。

> **2026-10-19 30队控制权的进一步评估**：[全部30队设为User-controlled vs Gameplay USER/CPU消费规则](NBA2K22_30_TEAM_USER_CONTROL_EVALUATION_V1_20261019.md)。建议新开MyLEAGUE将30队都归玩家经营，以切断原生GM后台经营；但Game Participation保留Auto，伤病和游戏中的ACE/自动换人继续原生。**经营权不等于实时比赛所有球员都消耗USER滑块；CPU侧继续保留HoF原值**。当前无法确认具体控球与消费映射，不可据此覆盖原HOF USER/CPU差异。

日期：2026-10-19。适用2021–22开局、30队独立GM、历史1984–2020轮回选秀、游戏3D实时比赛与自然成长。**研究提案，未批准写入游戏**；游戏原始值/原生PC菜单真实枚举仍以Antigravity已发现的当前版本为准。

与仓库旧10_GAME_SETTINGS_AND_SLIDERS.md相比，本版优先级更高。旧文中把某些缺少实验依据的滑块称为“权威/科学最优”，不可据此不加区分地执行，也不得使用成长引擎直接经营性修改球员属性。

证据类型：
- OFFICIAL：NBA官方历史规则金额。
- COMMUNITY：明确玩家在某NBA2K版本使用过的配置，不保证是普适最优。
- ENGINE-DESIGN：30队外挂GM取代原生商业AI后的系统设置。
- PROPOSED：首次为本项目选择的数值，尚无本局长期验证。
- UI-CHECK：部分选项可见性、枚举和是否按队覆盖需要用游戏当前版本核实。

## 1. 联盟和赛季

| 原生选项 | 推荐设定 | 解释 |
|---|---|---|
| League Type | NBA / 2021–22 / 30 Teams | 完整保留现役阵容 |
| User Control | 30队可受控经营 | 关闭自动化需要覆盖30支球队，而不只玩家亲控队 |
| Fantasy Draft | OFF | 不重洗NBA2021开局阵容 |
| Season Length | 82 | 官方常规赛 |
| Playoffs | 7/7/7/7 | 全部七战四胜 |
| Play-In Tournament | ON | 2021–22实际附加赛 |
| Draft Lottery | ON | 保留原生抽签；由外挂确认签位 |
| League Expansion/Relocation | OFF | 固定30队与稳定ID |
| Automatic Rule Changes | OFF | 不让原生赛季提案改变世界规则 |
| Historic Draft Class | 手工/外挂按1984–2020轮回 | 每届明确只导入一次，不生成额外虚构新秀 |
| Fantasy/Generated Draft Quality | 50/默认，实际不用来改变历史班 | 不直接调整历史新秀真值/潜力 |
| Generated Prospect Attr/Potential/Badge/Tendency | 原版默认 | 原生随机选秀生成不作为主来源 |
| Draft Minimum Age | 历史兼容；菜单允许优先18，有更低合法历史先例则单列特例 | 不能为了年龄门槛直接改真实球员生日/能力 |
| Min/Max Standard Roster | 14/15（最小按阶段及已验收业务兼容） | 实际最多15标准合同；短期少于14的豁免不能机械禁止 |
| Two-Way Slots | 2，但外挂/执行器完全支持后再开启相关自动补位 | 2021–22可另持两份双向合同 |

来源：[2021–22官方赛制、附加赛、双向名额](https://pr.nba.com/nba-board-of-governors-play-in-roster-rules-2021-22-season/)。

## 2. 交易与选秀权

| 选项 | 推荐值 | 解释 |
|---|---|---|
| Trade master | ON | 保留原生交易功能；尚未认证内存执行必须开 |
| CPU-CPU Trades | **OFF** | 不允许游戏自行交易 |
| CPU Trade Offers | **OFF** | 报价由外挂GM虚拟交易市场承担 |
| Trade Frequency | **0** | 辅助保险，不单凭频率保证交易关闭 |
| Trade Approval | ON | 原生交易提案若出现仍需人为批准 |
| Trade Logic | ON | 保留原生合法性辅助检查；不能覆盖外挂的双方同意决策 |
| Trade Override | OFF | 不默认启用原生强制交易，必要的获批直接由Codex受控执行 |
| Trade Deadline | ON | 保留截止日 |
| Recently Signed/Traded/Rookie Signing Restrictions | ON/ON/ON | 游戏内原生状态规则保留，外挂独立政策 |
| Financial Trade Rules | ON | 留作原生辅助；实际外部财务判断不得由未解码的2K黑箱代替 |
| Stepien Rule | OFF | 当前项目只有未来三届简单年/轮/原队/现持有队，不支持完整现实连续首轮约束 |
| Previously Traded Picks | ON | 保持选秀资产链，外挂不开放保护/互换 |
| Trade Negotiation Difficulty | 默认/50（原生业务不用） | 双方外部GM负责判断利益 |
| Player Trade Value, Type Discounts, Pick Importance/Depreciation, Lineup Impact | **全部原版默认** | 游戏贸易市场已被外挂替代，刻意调这些没有直接效果 |

参考：[2K22 PC玩家对CPU Trade Offers和CPU-CPU Trades开关关系的实测反馈](https://www.reddit.com/r/NBA2k/comments/rexpee)。

## 3. 30队Team Automation

| 功能 | 配置 |
|---|---|
| Prospect Scouting / Staff Management | OFF / OFF |
| Trades / In-Season Free Agent Signings / Contract Extensions / Waivers | 全部OFF |
| Draft / Team Options / Qualifying Offers | 全部OFF |
| Offseason Free Agent Signing / New Season Fill Roster / New Season Waivers | 全部OFF |
| Trade Block / Target List / Untouchables | 全部OFF |
| Lineup Before Game / Roster Changes | OFF；阵容与角色由Codex，原版实际分钟和比赛中自动换人保留 |
| Injury Lineup/Reserve Automation | **暂ON**；替代接口到位才OFF，防止伤员无法正常换人 |
| Training Automation | **暂ON**；Antigravity训练接口与Codex落地之后OFF |
| Coach ACE | **ON，Offense & Defense** |
| Offensive/Defensive Playcalling | **AUTO/AUTO** |
| Substitution/Player Minutes | **AUTO/AI**，不重新开发锁个人分钟 |

已有外部自由市场、选秀、签约是业务权威；实际游戏中合同、球员归属、历史新秀写回仍须玩家批准和Codex执行，且需要按来源确认是否已真实落地。禁原生自动签约之前先保证阶段经营执行窗口可用，否则球队可能缺人。参考[Armor & Sword NBA2K22 2021 Team Automation逐项清单](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918473-armor-sword%E2%80%99s-average-joe%E2%80%9D-nba-2k22-pro-real-fg-ft-custom-sliders-ps5-x-s)。

## 4. 财务和合同

| 项目 | 设定 | 类型/边界 |
|---|---|---|
| Salary Cap | ON | NBA软工资帽 |
| Salary Cap Value | **$112,414,000** | OFFICIAL 2021–22 |
| Luxury Tax | ON（若游戏有） | 财政惩罚仍然存在 |
| Luxury Tax Threshold | **$136,606,000**（若菜单可调） | OFFICIAL |
| Salary Floor | **$101,173,000**（若菜单可调） | OFFICIAL |
| Hard Cap global switch | **OFF** | NBA2021–22只有特定交易/签约才触发apron硬限制，不是全联盟统一最高工资 |
| Tax Apron | **$143,002,000**（存外挂财务规则，不能直接充当全局Hard Cap） | OFFICIAL |
| Staff Budget | ON | 员工雇佣要有经营成本；钱如何在原生现金账扣除暂未认证 |
| Salary Cap Inflation Slider | **保留原版默认** | 原始0–100值不是已认证的真实年度增长百分比；外挂采用逐年度实际Cap表，避免两个系统叠加 |
| CPU Re-Signing Aggressiveness | **0，且依靠真正Automation OFF**；如该值无法安全分离则保持原版 | 原生自动续约是外挂虚拟市场的敌对决策路径 |
| Contract Negotiation Difficulty | **默认/50** | 外部GM市场决定报价，2K内置原生难度无用 |
| Salary Demands（Min/Max Rating、Curve、Potential、Durability、Minutes、Fame、Ambitions等） | **全部默认** | 不因原版AI失去决策权就重新优化无用权重 |
| 原生Team Cash/Budget | **30队各自原值HOLD，不统一充值** | 源raw cash可能被误读接近2^32；游戏存档现金不是工资帽空间 |

真实工资帽跨年基准（单位：百万美元）：

| Season | Cap | Tax |
|---|---:|---:|
| 2021–22 | 112.414 | 136.606 |
| 2022–23 | 123.655 | 150.267 |
| 2023–24 | 136.021 | 165.294 |
| 2024–25 | 140.588 | 170.814 |
| 2025–26 | 154.647 | 187.895 |
| 2026–27 | 164.961 | 200.428 |

来源[NBA 2021](https://pr.nba.com/nba-salary-cap-for-2021-22-season-set-at-112-414-million/) / [2022](https://pr.nba.com/nba-salary-cap-2022-23-season/) / [2023](https://pr.nba.com/nba-salary-cap-for-2023-24-season-set-at-136-021-million/) / [2024](https://pr.nba.com/2024-25-nba-season-salary-cap/) / [2025](https://pr.nba.com/nba-salary-cap-2025-26-season/) / [2026](https://www.nba.com/news/nba-salary-cap-2026-27-season)。2023新CBA出现首道/第二道apron，不能硬称2021NBA2K22已原生支持。游戏年2026之后若超出现实资料，外挂可以采用每年约**4%名义增长的首次政策假设**，并保留未来动态调整；这不是游戏Slider raw=4的含义。

### 4.1 30队差异化初始增量机动资金（外挂设计模型，不是原生Cash）

本金和工资帽必须分开；2021已承诺合同和税费保持原状，不倒逼强队减员。额外增量机动资金只供今后批准的聘员工、额外税费及短期经营费用使用，不能当薪资空间：

| 档 | 2021年福布斯价值排名 | 球队 | 外挂新增机动资金 |
|---|---|---|---:|
| A | 1–5 | NYK GSW LAL CHI BOS | **$60M** |
| B | 6–15 | LAC BKN HOU DAL TOR PHI MIA POR SAC SAS | **$40M** |
| C | 16–25 | WAS MIL PHX UTA DEN ATL IND CLE ORL OKC | **$25M** |
| D | 26–30 | DET CHA MIN NOP MEM | **$15M** |

分组参考[Forbes2021球队估值排名](https://www.sportingnews.com/us/nba/news/nba-team-values-list-knicks-warriors-lakers-most-valuable-2022/fgfhzjtpimi9cjr9lsnzcoir)。**球队市值不等于流动性，以上60/40/25/15均是新设计参数，没有对应真实球员市场事实或历史账户余额**。实际老板奢侈税容忍度还应由M2球队文化、当期争冠窗口和已有工资负担决定，并在M1能计算实际现金支出后才正式启用；不可直接写到Team Cash或冒充游戏事实。

## 5. 球员成长/衰退、训练与徽章（仅原生引擎自然变化）

| Setting | 建议 | 证据 |
|---|---|---|
| Player Progression Rate | **48** | PROPOSED，参考2K22 Armor45和2K21 Schnaidt48折中，避免历史新秀成长过慢 |
| Player Regression Rate | **50** | COMMUNITY，Armor2K22采用50，暂不额外惩罚老将 |
| In-Season Training Effects | **50** | COMMON/NORMAL；原生训练收益 |
| G-League Training Effects | **原版默认/50** | 无同版证据证明必须压低 |
| Badge Progression/Regression | **默认/50和50**（若独立控制） | 允许游戏原生升降徽章 |
| All Attribute Growth/Peak/Decline detail | **原版默认** | 运动、意识、投篮技能年龄轨迹不同，避免一套强制年龄 |
| Peak Start/End Age | **原版默认** | 不把历史伟大球员强行统一在25–32岁巅峰 |
| Training Automation | 暂ON，原生训练设置接入才由GM取代 | 自然成长的实际数值由游戏控制 |
| Mentorship | 原版ON | 设置导师而不是给球员直接加徽章 |

参考：[Armor & Sword 2K22成长45/50和训练50](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918473-armor-sword%E2%80%99s-average-joe%E2%80%9D-nba-2k22-pro-real-fg-ft-custom-sliders-ps5-x-s)、[Schnaidt1 2K21 48/52](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/900202-schnaidt1s-2k21-myleague-and-gameplay-sliders)、[2K22玩家降低成长后高强训练仍进步不足](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917177-schnaidt1-s-nba-2k22-next-gen-mynba-gameplay-sliders-settings/page31)。所有此表建议仅针对全局速率，不准经营性修改具体球员能力/潜力/徽章。

## 6. 伤病/疲劳、士气、化学反应及老板

| Setting | 目标 | 来源等级 |
|---|---|---|
| Injuries | ON | 游戏身体风险保留 |
| Progressive Fatigue | ON | 有负荷/轮换代价 |
| Sim Injury Frequency | **55** | PROPOSED：轻微提高但不追求过度伤病 |
| Sim Injury Severity | **40** | PROPOSED：降低部分重大伤病成本，但不能换算固定轻伤百分比 |
| In-Game Injury Frequency USER/CPU | **50/50** | 玩家已认为3D伤病基本正常 |
| In-Game Injury Severity USER/CPU | **50/50** | 没实际失真不改 |
| Career-Ending Injury | **5** | PROPOSED：罕见生涯终结；5是raw，不是5% |
| Injury Duration | **原版默认/50**（如有） | 不重复缩短伤停 |
| Morale System | ON | 保留角色和合同诉求 |
| Morale Difficulty | **35** | PROPOSED：弱化比赛时间AI覆盖导致的无端抱怨 |
| Morale Effects | **40** | PROPOSED：减轻低士气即时能力连锁惩罚 |
| Chemistry | ON | 保留队伍磨合和更衣室生态 |
| Chemistry Difficulty/Effects | **50/50** | PROPOSED：中性 |
| Staff Abilities | ON（如可） | 员工需真实影响经营结果 |
| GM Fired / Menu Lock / Staff Quit / Random Owner Personality | **OFF**（如果字段存在） | 不允许原生AI剥夺外部30队GM的经营权 |

社区伤病/士气值分歧显著，见[Schnaidt1长期系统](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/900202-schnaidt1s-2k21-myleague-and-gameplay-sliders)及[Armor & Sword 2K22](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918473-armor-sword%E2%80%99s-average-joe%E2%80%9D-nba-2k22-pro-real-fg-ft-custom-sliders-ps5-x-s)，无可信单一最优滑块。

## 7. 3D赛事、统计、日历模拟

| Setting | 目标 | 说明 |
|---|---|---|
| Gameplay Difficulty | 以玩家原版HoF为赛场基线 | 之前的HOF Court V1另一个独立候选，不在世界初始化时自动覆盖 |
| ACE | ON Offense & Defense | 游戏原版临场教练 |
| Offensive/Defensive Playcalling | Auto/Auto | GM赛前制定计划，游戏自行战术调用 |
| Player Minutes/Substitutions | Auto | 用户已确认不再锁定个人精确分钟 |
| Quarter Length | **12min** | 完整实时比赛节奏 |
| Simulated Quarter Length | **12min** | 正常联盟日历记录长度，不代表研究SimEngine |
| Normalize Played Minutes/Stats | **OFF/OFF**（实际12min时） | 若用户最终手打8–10分钟且希望与联盟标准口径可比，另选ON/ON；必须同时保存实际时长元信息 |
| Simulator Difficulty | 原版默认/50 | 不通过模拟难度指定历史赛果 |
| Calendar Sim Engine Sliders | **全部原版默认** | 用户此前明确“竞技优化只针对实时3D”，此处仅保存正常初始化 |
| Gameplay 全部细项 | 原版HoF（独立Court V1须另批准） | Movement/Defense/Offense/Attributes/Tendencies/Fouls当前不在本提案同时改 |

资料：[NBA2K22现实设置范例](https://realsport101.com/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes)和[Armor & Sword 2K22](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918473-armor-sword%E2%80%99s-average-joe%E2%80%9D-nba-2k22-pro-real-fg-ft-custom-sliders-ps5-x-s)。两者对Normalize Played Stats不一致，必须按实际游戏分钟决定而非假定有官方唯一最佳。

## 8. 提案状态与部署约束

- Status: RESEARCH_PROPOSAL_NOT_APPROVED；没有连接游戏、没有写入内存、没有覆盖原生cash/球员能力、没有启动GM正式30队经营。
- 游戏原生滑块字段/保存期/“ON但30队归属”按Antigravity实际地址目录确认；文档中未知枚举与真实经营限制不能被当作完整受控执行能力。
- 关闭原版经营之后，务必保留受控的Codex签约、球员归属及历史新秀更新窗口；没有完成业务落地不冒充外部市场已经更新游戏。
- 开档后先记录game build、career/save ID、全部global preimage和实际工资帽/现金元数据，形成WORLD_PROFILE候选。用户批准之后才能从研究版升级正式。
