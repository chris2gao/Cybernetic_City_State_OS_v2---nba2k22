# NBA 2K22 PC 本世代《终极联盟 MyLEAGUE》完整玩法与原生功能地图 V1

- 编制：2026-10-19，Web Development 研究。
- 用途：**首先弄懂NBA2K22终极联盟有哪些功能、每个界面如何玩、各阶段的经营含义**；以后再决定让外部GM接管哪些、保留哪些，不在本手册预先批准接管或写游戏。
- 项目：`chris2gao/nba2k22-gm-engine`。计划新开独立 MyLEAGUE 存档，2021–22开始，1984–2020历史选秀轮回。30队 GM V4 数据采集→分析→GM决策→玩家审批→Codex执行仍适用。
- 输入一：玩家提供的《全局设置清单》（2026-10-19；包含建档、MyLeague Settings、USER/CPU Gameplay、休赛期规则、Team Automation和旧地址），**它是用户提供的候选菜单清单**。玩家亲自确认许多本世代与次世代的**全局设置相同**；尊重这项实机结论，不武断说全部不同。但候选列表里的每个子菜单、取值范围、内存类型和地址尚未逐项实机认证。
- 输入二：NBA2K22 本世代攻略、2K官方 MyNBA 文章、玩家实际菜单讨论、项目仓库已验证源码。**官方次世代 MySTAFF/Prep Hub/Conditional Coaching专题仅为类比材料，不能自动认证 PC 2021版也有其新增专用系统。**
- **本文件是玩法研究文档，不是内存字段地图/开发任务书/游戏已验收报告。** 它追求功能覆盖，明确「菜单候选、功能解释、版本证据、未来GM接口」的界限。Antigravity 后续提供实际菜单、截图及字段差分后应在本文件逐条补齐。

> **2026-10-19 研究方向修订（按玩家PC实际经验）**：这份文档首先是人类终极联盟的功能导航，但我们系统真正的研究目标是**外部GM是否已能查询→分析→决策→经批准执行某项经营任务，哪些经营能力仍缺失**。对应的[GM能力覆盖审计与月度训练方案](NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md)为后续功能接管判断的优先入口。玩家确认本世代制服组UI有六个可任命岗位，原始内存还有8种员工代码；训练与NBA2K20类似，体力/伤病约束决定月度训练接管门槛。**菜单能显示≠GM已具备经营闭环。**

## 0. 最快理解：终极联盟是在模拟什么？

MyLEAGUE 是一个可以跨赛季运行的 NBA Franchise/Sandbox：玩家不只是打比赛，还经营球队阵容、教练体系、员工、薪资、交易、选秀、培养；游戏持续运行联盟赛程、赛果、球员成长、伤病、自由市场、季后赛和赛季间规则变化。相比MC单人职业生涯，MyLEAGUE更接近「管理NBA联盟经营世界」。

### 功能板块导航地图

| 大类 | 常见英文标签/入口 | 玩家真正要解决的问题 | 自身业务角色 | 研究优先级 |
|---|---|---|---|---|
| 日历与赛程 | Home / Calendar / Schedule / Simulate | 下一场是谁、什么时候停表、是否推进日期 | 游戏阶段控制 | 很高 |
| 行政办公室/管理层 | Front Office / Roster / Trades / Free Agents / Contracts / Staff | 怎么组队、花多少钱、和谁交易/续约/签约 | 核心GM | 很高 |
| 执教 | Coaching / Coach Gameplan / System Proficiency / Playbook | 用什么打法、对谁采取哪种防守、谁上场 | 核心GM+比赛 | 很高 |
| 训练与发展 | Training / Team Training / Player Training | 球员如何在游戏原生机制中培养、体能如何管理 | GM管理输入、游戏负责成长 | 高 |
| 球探与选秀 | Scouting / Prospect Scouting / Mock Draft / Draft Class | 选谁、什么时候选、怎么发现人才 | GM长期资产 | 很高 |
| 扩展与搬迁 | Expansion / Relocation / Team Branding | NBA城市、球队数、身份、球场如何改 | 世界结构 | 中、开局优先 |
| 联盟新闻 | League News / Transactions / Injuries / Awards | NBA世界发生什么重要事件 | 情报/观察 | 高 |
| 排名/赛季/历史数据 | Standings / Power Rankings / League Leaders / Stats / Records | 球队赢球质量、球员表现与长期纪元如何发展 | 数据分析 | 很高 |
| 联盟/比赛设置 | Options / MyLEAGUE Settings / Sliders | 哪些游戏机制存在、如何影响模拟环境 | 世界规则 | 很高 |
| 管理自动化 | Team Automation / CPU Control | 哪些工作由游戏AI做，哪些交给外部GM | 权限划分 | 很高 |
| 赛季结束及休赛期 | Playoffs / Offseason / Draft / Free Agency | 退役、规则、签约、选秀、培训、下赛季 | 阶段经营 | 很高 |

**导航说明**：表中英文是不同代际/版本的常见功能别名，不等于已查明 PC 2021版每个按钮文字与菜单层级。当前实际菜单路径由 Antigravity 实机补齐。来源：2K Wiki《MyLEAGUE》、Front Office、Coaching、NBA2K22 Current Gen玩家视频，见末尾参考资料。

### 这份手册里的证据等级

- **PROJECT_VERIFIED**：我们仓库的真实 NBA2K22 游戏读回/代码/玩家实机已验证；例如原生教练19项+指定对手整体18项已经采集/验收部分写回。
- **PLAYER_CONFIRMED**：你已实机确认的功能，例如 PC 本世代拥有大量与次世代相同的全局设置；不替代各字段逐项差分。
- **CURRENT_GEN_GUIDE**：NBA2K22本世代玩家教程、论坛、视频直接说明。
- **CROSS_VERSION_REFERENCE**：其它年份 MyLEAGUE 或次世代 MyNBA 解释功能概念；不能用来证明 PC 菜单完全相同。
- **GEMINI_INVENTORY_UNVERIFIED**：你提供的完整候选设置清单，但具体值域、存在性和地址未经交叉实机认证。
- **PENDING_PC_UI**：需要 Antigravity/玩家以后补真实PC菜单页面；不用假装已确认。

特别提醒：有些指南将「所有能手工编辑的数据」也叫设置。**编辑球员能力是一种可能的原生菜单能力，但按项目规定不允许 GM 以此经营性改变属性。** 原生训练安排则可以作为培养决策候选，属性成长仍交给游戏算法。

---

## 1. 开新终极联盟档：整个游戏世界的初始化

### 1.1 常见进入路径和建档类型

典型路径：主菜单 → MyLEAGUE → 建立联盟 → 选择当前NBA / 扩展联盟 / 自定义联盟 → 阵容来源 → 队伍控制范围 → 联盟设置 → 开始赛季。具体中文标签及选项顺序需PC实机确认。

- **Current League（当前联盟）**：从当前30队开始，适合我们的2021–22赛季、维持实际NBA阵容/赛程/竞争历史线。
- **Expansion League（扩展联盟）**：在联盟加入额外球队，通常还涉及扩军球队名单及扩军选秀；扩到多少队依具体菜单与存档选项为准。
- **Custom League（自定义联盟）**：自由组建现役/历史/自定义球队，可能涉及替换队伍和不同赛制。别误把「自定义选秀名单」和「幻想选秀」当成同一功能。
- **Fantasy Draft（梦幻选秀）**：用重选全联盟队员重新分配当前NBA球员；**不是**我们按1984→2020历史选秀班轮回的赛季新秀注入逻辑。新开档如要保留2021–22实际球队基线，应辨别并尽量避免误开启重选。
- **Roster Source（阵容来源）**：官方阵容、自定义阵容、历史队伍，涉及同名球员、阵容ID、历史面孔及现役复制。
- **User Control（控制球队）**：选择管理一队/多队/所有球队的范围及管理员选项。我们目标30队GM，不代表随意认定UI已替我们自动打开30队控制；需要在开档时验证且记录，避免存档后不可逆。
- **League Settings（世界设置）**：赛季长度、赛制、工资、交易、伤病、球员成长、选秀、自动化等，其中一部分可能只在创建时设置，另一些可赛季内更改。

### 1.2 开档应理解的主要选择

| 选择 | 游戏含义 | 对我们的建议（尚非已批准最终值） |
|---|---|---|
| 30队还是扩军 | 影响球队身份、联盟结构、赛程、选秀/人员容量 | 第一版保留30队，除非用户决定扩军 |
| 82/58/29/14场等赛季长度 | 影响样本量、疲劳、统计以及检查点节奏 | 倾向82场，依玩家批准 |
| 单节/模拟单节时长 | 影响单场统计量与真实时间 | 模拟单节12分钟作为标准候选 |
| 季后赛每轮场数和附加赛 | 决定晋级路径、比赛数量 | 对照2021–22真实规则 |
| 赛季开始时间 | 开局赛季和游戏纪元基线 | 绑定项目save_id和game_date |
| 工资帽/硬帽/职工预算 | 决定合同合法性与经济压力 | 与M1财务机制统一 |
| 交易权限/原生AI交易 | 控制是否出现未经过外部GM的资产流动 | 研究可行后逐项接管，勿一次全关 |
| 训练/球探/签约自动化 | 游戏AI是否替球队处理经营 | 有执行能力后分模块关闭 |
| 历史选秀轮回 | 不是游戏默认的任意选秀类别 | 外挂规则独立管理并避免重复生成 |

### 1.3 操作步骤（新开档）

1. 在测试存档先浏览全部开局菜单，记录默认值、选项范围和只能开档设置的条目；不要把「当前显示默认值」写成游戏所有版本的统一默认。
2. 选择30队、基础21–22阵容，设置30队可经营范围；明确操控 vs CPU 自动执行的关系。
3. 确定赛程/季后赛/选秀/交易/工资/伤病/模拟节奏等，形成一份 `MYLEAGUE_WORLD_PROFILE`。
4. 创建新存档独立 `save_id`；避免沿用MC数据。开档后首轮玩家主动触发全量采集，建立新的球队名单/教练/人员/财务基线。
5. 后续通过GM V4只提出获批的球队经营动作；**不在常规节点自动修改整个联盟世界的基础参数**。

---

## 2. 首页、日历与赛季时间推进（Home / Calendar / Schedule）

### 2.1 常见功能

- **Upcoming Games**：下场对手、比赛时间/主客场，供玩家选择手打/观战/快速模拟。
- **Calendar / Schedule**：月历、逐场赛程、球队休息天数、背靠背（如果界面提供）；可以定位GM按月/关键日期停表。
- **Simulate Day / Week / Through Date**：推进比赛与联盟状态，可能发生CPU交易、伤病、成长、训练、合同/赛程事件。
- **Game Results / Box Score**：查看已完成比赛比分、单场球员统计、球队统计。
- **Notifications / Inbox**：合同消息、伤病、比赛、重要联盟事件（具体条目待PC菜单证实）。
- **Play / SimCast / Spectate（可能的入口）**：手打、模拟、观看；存在性和菜单名称以当前局实际界面为准。

### 2.2 玩家怎么利用

- 常规：推进几场→看看联盟排名与球队问题→重要日期触发全量采集→数据分析→GM决策→批准后执行。
- 截止日前：暂停自动推进，核对可交易日期、所有待决谈判，再推进。
- 季后赛：阶段性收缩到具体对手、教练对位与伤病；不要用一个月样本覆盖长期战略。
- 休赛期：每个不可逆的年终阶段到来前停表，先查看GM是否已经能接管，不用不停按「继续」造成AI抢先签人/选秀。

**不应误解**：某张月历上显示「本月」≠数据采集已经抓取整个自然月的所有比赛；必须用明确game_date与已完成比赛字段认证。

---

## 3. 行政办公室（Front Office）：真正管理一支NBA球队

这是与我们GM Engine最直接相关的板块。2K Wiki的系列级Front Office说明涵盖阵容、角色、交易、合同、球探、员工和自由球员；属于功能参照，具体菜单放置在PC版可能不同。

### 3.1 阵容名单（Roster）

- 查看15人左右的名单、各位置、生日/年龄、身高体重、球队角色、当前合同、受伤/健康、球员总体与单项能力、徽章和倾向；可以多维排序。
- 了解**球队使用谁**和**游戏实际当前持有谁**；交易后首轮应该核验流动双方名单，不能只信外部执行回执。
- 候补/伤员/G联赛/双向合同（若菜单具备），区分NBA正式名单、候选球员池、受限自由球员，不要把球员池“不在NBA名单”当作可立即签约。

**GM问题**：核心球员是否适合当前战术？替补/位置冗余和缺口是什么？是不是应HOLD而不是做交易？

### 3.2 球员角色（Player Roles / Team Status）

系列机制中常见 Star / Starter / Sixth Man / Role Player / Bench Warmer / Prospect 等；角色可能与士气、合同及续约意向有关，但本存档的角色枚举、修改持续时间和实际效应尚未PC实机验证。

**GM问题**：角色与实际出场、球队竞争窗口是否一致？士气是否值得启用？玩家已经明确实际影响次于战术与合同，不能让角色干扰阻断真实适配交易。

### 3.3 交易（Trades）

典型操作：Propose Trade（指定双方筹码）、Trade Finder（由游戏生成报价候选）、Player Finder（查目标）；包括球员和选秀权。交易难度、频率、薪资匹配与覆盖开关是**游戏内部规则**，不同于我们的外挂简化交易审批。

**我们已开发**简单选秀权窗口和获批交易受控执行；外部GM的核心规则是**两队各自同意→玩家批准→Codex实施**，不能由2K交易难度重写经营结论。

关注：谁拥有哪枚选秀权、是否已交易、交易日期、自由签约限制、资产冲突、双方球员名单人数和合同新承诺。

### 3.4 合同续约（Contract Extensions）与自由市场（Free Agents）

- 合同界面可能提供每年薪金、合同长度、球员/球队选项、Bird相关资格、续约资格与谈判状态；不同2K版本有不同条款显示。
- 签约流程涉及自由球员名单、报价、签约竞争、限制自由球员与匹配、队伍名单容量、工资帽与可能的例外规则。
- 对本项目：**先核实实际PC游戏+外挂的约束**，M1计算合法/可承担/值得做三个独立问题；不得用 `budget-total_salary`伪造可签约额度。
- 正式休赛期原生选项与我们的外挂竞价框架之间，需要选出唯一的执行权源：尽量避免「外部报价决定结果」和「游戏AI再次自动报价/续约」同时运行。

### 3.5 员工（Staff / Staff Hiring）

- **玩家实际PC本世代制服组界面：六个主要可任命岗位**：财务/CFO、总经理/GM、主教练、助理教练、球探、训练师。观察职位候选的工资、任期、已证实评级/属性，按需比较和经营。**数据库目前解码8个STAFF职位枚举和30队×8个内存指针槽（含Governor、Assistant GM），这与六个界面岗位并不自动矛盾，但不能把底层8槽当作8个可聘岗位；需要UI逐项核对。**
- **PC 当前局我们已有员工1,458观察+在队角色关系，M0 SQLite按需查询**；但员工具体能力如何影响训练/比赛，需要另立规则条目。
- 次世代MyNBA 2K22宣传的17个可分配岗位、四部门和MySTAFF特殊徽章机制属于单独版本，不能把每个新岗位硬套在PC已采8岗位表上。
- 普通终极联盟可能展示员工评级、预算和合同；建议在Antigravity后续截图中逐项标记录用的中文UI值域。

### 3.6 财政办公室（Finances / Salary Cap）

- 查看球队 `total_salary`、`payroll`、`budget`、`cash`、`staff_budget` 及相关工资帽与税线规则。
- 当前编码问题：CLE/NOP/ORL/UTA `cash` 近 `2^32`，有signed32候选但未确证；`payroll`口径不等于球员年度合同合计。
- 从人类玩法角度，财务的用途是**决定是否能负担一名即战力，以及未来续约核心的机会成本**；从系统角度，直到M1证据足够，不把现有原始金额直接变成交易合法性硬门。

---

## 4. 执教（Coaching）：战术、体系、阵容使用

本版最重要的优势是：项目**已经有真实原生教练设置数据和执行接口**，不需要从零建立。

### 4.1 教练计划（Coach Gameplan）

通常涉及首发、替补、轮换深度、进攻/防守重点（POE）、体力、关键球打法、指定对手战术。部分操作可针对全联盟对手统一设置，也可针对具体对手；系列指南支持这一基本玩法。

**项目实际确认**：
- 每支球队原生`coaching_tactics`默认 **19项**设置；
- 对29个对手各有指定的**18项整体防守**配置；所谓“整体”对应修改对手各有效matchup数据，不是一个唯一的All槽；
- 19项包括POE、PreferredSystem、ActiveSystem、PlaybookID、BenchDepth、RunPlayTendency、ZoneUsage、BenchUtilization、Tempo、HelpDefense、4个Freelance类型等；实际字段枚举/混合字段精确含义以 `coaching/field_dictionary.json` 及 `docs/40_COACHING_EXECUTION_RUNBOOK.md` 为准；
- **Sim相关5项只读GM参考、不做正式修改**；`Tempo`即使可读写，其UI含义仍未完整认证，不能解释成有证据的模拟回合数参数；
- 游戏AI会重新分配球员分钟，**精确锁分钟不再是项目开发目标**；允许用`BenchDepth`和合法体系控制轮换方向。

### 4.2 系统适应性（System Proficiency）

系列玩家界面有Balanced、Defense、Grit & Grind、Pace & Space、Perimeter Centric、Post Centric、Triangle、Seven Seconds等体系标签，常以星级/适应情况展示球队与主教练体系关系。项目有PreferredSystem/ActiveSystem原生字段，但不能仅凭数值推断全部胜率因果。

**人类玩家实践**：先判断目前核心人员适合怎样创造投篮优势、如何防守，再根据系统选择教练/配套球员；不能只看体系星级直接卖掉核心。

### 4.3 战术手册（Edit Playbook / Offensive Plays）

- 设置球队有哪些战术配合、某类球员被分配什么Play Type，如挡拆持球手/顺下者、定点、低位、单打。
- 在比赛中选择战术执行；不同球员有不同可用配合。2022年社区提示可在Coaching→Edit Playbook里切换不同球员的战术种类。
- 我们的`PlaybookID`只是某层原生标识；**修改整个每名球员的战术分配**是否存在另一个内存结构，目前需要Antigravity实际定位；不要宣称已有PlaybookID就完全掌控所有战术。

### 4.4 临场阵容、练习和指挥

- **On-the-fly Lineups**：预设快、强防、长人、投射、替补等临场阵容（系列级参照）。
- **Practice Plays**：让玩家查看/试跑战术；与真正的「训练提升球员属性」并不是同一项。
- **Freestyle / Scrimmage**：无胜负的单人/队内练习，主要是人类熟悉投篮和战术的工具；对我们自动经营价值偏低。
- **ACE / Adaptive Coaching Engine**：比赛中动态调整（具体是否显示、启用条件和全局菜单选项以PC本局UI为准）；如开启，GM改的设置可能被AI运行时重写，需要区分「预设生效」和「比赛中动态覆盖」。
- **Conditional Coaching**：官方2K22次世代MyNBA加入的新条件式教练规则，不可直接认证当前PC有同等原生菜单；若用户看到对应功能再记录。

### 4.5 GM实际怎么用

一场比赛输了、三分低、篮板差，先看对手、球员实力和样本，再决定HOLD、改变体系、替补人数、POE、对手防守或交易；对照M3分析包持续复盘。**战术不是球队永久文化**，属于比长期组织战略变化更快的层。

---

## 5. 训练与球员发展（Training / Player Development）

> **玩家确认的本世代训练细节**：球员导师（选择可传授徽章）、球队整体训练、个人训练及训练强度，与NBA2K20的界面概念类似；训练和比赛消耗体能，过高累积疲劳可能导致伤病/缺赛甚至成长倒退，老将和高负荷首发需要更保守。**目前项目尚未采集训练配置、实时疲劳及伤病可用性，因此不能直接让GM按月自动指定高强度计划。** 详细的月度负荷/重点球员/兜底机制与相关研发缺口请读[专项审计](NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md)。

### 5.1 三种不同概念，必须分清

1. **训练安排（经营行为）**：选择团队训练/个别球员训练方向或强度、疲劳恢复等，要求确认PC可操作界面。这是我们以后允许GM接管的候选。
2. **自然成长/衰退（比赛引擎输出）**：球员赛季推进后的属性增长/老化，由2K游戏决定；不能通过经营脚本直接提高能力。
3. **全局成长环境（世界规则）**：Player Progression/Regression/Peak Age/Badge Progression Rate等参数，影响整个联盟演化，不应由每队GM为了短期好处任意调整。

### 5.2 玩家怎样使用训练菜单

- 观察球员发展阶段：年轻新秀、中生代核心、成熟球星、高龄老将。
- 团队层：训练主题、强度/恢复、负担与是否自动训练（具体PC菜单可供选项待截图）。
- 球员层：个人发展重点，如射手、组织、防守、内线等原生可选培养方向；这是**计划方向，不是外挂直接写球员三分/速度值**。
- 观察：自然成长、能力变化、伤病和疲劳、比赛上场参与；隔一段时间比较变化而不是看到一次波动就反复改计划。
- 员工层：若有相应教练、训练师或医疗相关岗位，研究其实际加成是否独立成立。

**版本差别**：2K22官方次世代MyNBA新增的三周训练日程、Prep Hub、Game Fitness/负荷系统，不能未经PC实机证明就当作我们已有。旧本世代仍有球队训练/球员训练概念，具体显示与输入方式需要实机菜单核对。

### 5.3 GM如何利用

争冠队倾向保持核心健康、避免训练与密集赛程冲突；重建队着重年轻人发展方向。但这是经营策略偏好，不等于未经证实的2K精确收益公式。每项计划记录生效时间、对象、状态、后续能力变化（仅观察），不在月中直接写属性。

---

## 6. 球探考察、选秀准备（Scouting / Prospect Scouting）

### 6.1 模块的玩法目的

球探不是简单看一个新秀名单，而是处理**信息不确定性**：选秀前并不知道每名球员的真实潜力和长期发展，球探可形成评估结果，模拟选秀预测可能和最后实际顺序不同。

常见细项（菜单名称需PC UI核对）：
- **Prospect Scouting**：按位置/球员查询、选择重点考察对象。
- **Prospect List / Rankings**：候选名单、预测排名、大学/国际队信息、年龄、体测、可能的发展模板。
- **Scouting Progress**：侦察完成比例、哪些能力信息已揭露；不要把未完全考察的潜力当100%可信。
- **Mock Draft**：模拟媒体/游戏预测的选秀排序，不等于GM最终选人顺序。
- **Draft Class**：在赛季合适阶段选择游戏自动生成、读取自定义/历史名单，之后进行实际选秀。
- **Draft Picks Owned**：拥有的选秀权与归属球队。
- **Staff Scouting**：球探雇用、业务能力与考察效率，需在PC局核对加成含义。

### 6.2 2K22玩家实例

2022年的MyLeague玩家询问新秀考察进度卡在40%；玩家讨论提示需要检查Scouting Automation及人工优先级，能力也与球探有关。另有NBA2K22用户指出，可在 Scouting→Prospect Scouting→选新秀的入口加载选秀名单；这是社区操作经验，**对具体平台/离线能否下载在线名单不能做当前保证**。

### 6.3 我们的特殊历史选秀

- 历史班从1984开始，顺序循环至2020，再按项目年表推进；每季进入下一历史班。
- 这属于外挂世界规则，**不能仅用游戏标准的“Draft Class Quality”随机新秀生成滑块代替**。
- 要确认导入历史班发生在游戏的哪个阶段，以免游戏先生成随机班、又被外挂重复注入；避免同一历史名宿重复出现、重复球队资产。
- 每队GM独立评估历史新秀的前景与自己选秀签价值，不能只按历史现实荣誉锁死球员未来成长；游戏照常决定能力成长。
- 从2026以后历史重力模拟的特例依玩家批准，不在普通选秀/训练中随意改属性。

---

## 7. 扩展、球队搬迁、身份与联盟组织（Expansion / Relocation）

### 7.1 概念区别

| 操作 | 实质含义 | 可能影响 |
|---|---|---|
| Expansion（扩军） | 在NBA新增球队，不是把旧队换个城市 | 球队总数、分区、赛程、扩军选秀、球员资源分散 |
| Relocation（搬迁） | 现有球队移往新城市 | 城市、球队身份、球迷/球队展现，具体财务效果未认证 |
| Rebranding（品牌重设） | 保持或改变城市/名称/标志/球衣/球场 | 视觉、队名、可能影响记录/外部team_id映射 |
| Custom League（自定义联盟） | 在开局调整参赛队组成 | 联盟结构、历史球队替换、赛程 |
| Realignment（分区重组） | 重新划分球队所在分区 | 分区赛程/季后赛归属，依实际模式 |
| Expansion Draft（扩军选秀） | 从已有球队可被选择的球员中配置新队 | 现有阵容、合同、资产转移 |

早期MyLeague从NBA2K17起已有扩军/历史/自定义球队沙盒；社区在NBA2K22里讨论扩军和赛中搬迁，说明功能存在但操作入口和能否赛中继续加队**需要当期界面验证**。单独的Team Relocation vs Expansion菜单可能比较容易误按；留意先创建测试存档。

### 7.2 玩家玩法

- 新增西雅图球队、拉斯维加斯球队，或将某队搬到其它城市；
- 自定义队徽、球衣、主场和队名；
- 调整联盟分区/城市结构；
- 查看扩军带来的保护名单/人员再分配是否实际出现。

### 7.3 对我们的系统影响

扩军将把既有**30队决策架构**扩成31–36队（取决于游戏规则），增加队ID、赛程、员工、薪资、选秀权、GM身份和数据覆盖复杂性；会影响所有SQLite的主键与脚本边界。**第一版建议原生保留，不由GM按月自动触发扩军。**

搬迁与换名称尤其需要确认外部稳定team_id不随展示名称变化，原有的中文/英文队名和缩写不可作为唯一永久键。

---

## 8. 联盟新闻、情报及事件（League News / Transactions / Injury Report）

### 8.1 常见资讯类别

| 信息 | 玩家为什么看 | GM / 分析如何用 |
|---|---|---|
| 最新交易与球队变动 | 哪支队补强/失去核心 | 验证是否有未批准的CPU交易 |
| 自由球员签约/裁员 | 市场实际变化 | 避免重复谈判，检查自动化设置 |
| 伤病与复出 | 核心不能上场、胜率与轮换改变 | 区分短期表现与真正阵容缺口 |
| 奖项竞争、MVP/ROY/DPOY等 | 球员当前赛季代表性表现 | 经营故事线；不是代替比赛真实数据 |
| 全明星、周/月最佳及球队纪录 | 联盟发展、球星人气与历史线 | 提供长期叙事与经营反馈 |
| 新秀、退役、名人堂及重大里程碑 | 赛季切换、历史纪元发展 | 检查历史班注入、球员自然退役 |
| 季后赛晋级、总冠军、选秀乐透 | 不可逆的状态变化 | 触发赛季/休赛期GM节点 |

「League News」可作为**发现变化的提示面板**；真正的交易、伤病、球员变化应由游戏数据采集认证。当前我们已拥有教练和名单来源，**新闻全文/交易日志/奖项历史是否能直接内存采集尚需单独核对**，不因UI有页面就声称SQLite已有。

### 8.2 玩家检查顺序

每个节点先看近日新闻/通知有没有关键球员伤病、CPU暗自签约/交易和比赛阶段变化，再用 Standings/Stats 判断是否影响竞争窗口，最后由GM从数据库查询相关球队/人员事实。不要把新闻标题当 GM 行动批准。

---

## 9. 排名与数据（Standings / Stats / League Leaders / History）

### 9.1 必须分清的几个数据表

- **Standings（联盟排名）**：胜/负、胜率、分区与分组位置、胜差、近期表现及主客场等，反映竞争格局和季后赛资格。
- **Power Rankings（实力榜）**：游戏/媒体式主观或算法排名，未必与胜率相同；不要当作已经验证的球员价值算法。
- **Team Stats（球队赛季数据）**：得失分、投篮、三分、罚球、篮板、助攻、失误、防守等；按赛季或赛段。
- **Player Stats（球员赛季数据）**：得分、篮板、助攻、投篮百分比、上场、抢断盖帽、犯规等；**样本量与上场机会**必读。
- **League Leaders（单项领跑）**：联盟球员得分王/篮板王/助攻王/效率类榜单等。
- **Box Score（单场技术统计）**：判断某场表现与赛季均值是否偏离、对手、伤病与阵容变动。
- **Advanced Stats（高级统计）**：如eFG%、TS%、助攻/失误等；仅按游戏界面或数据库实际具备的字段使用，不编造球队回合数、ORtg、DRtg等。
- **Player Comparison / Team Comparison**：两个球员或球队的能力/结果比较，辅助交易谈判。
- **Season Awards / History / Records（奖项、历史、纪录）**：赛季MVP、最佳阵容、冠军、历史记录、球员生涯表现等；需要按年保存做历史纪元分析。

### 9.2 人类经营分析方法

1. **先比较胜率与净胜分**：前者是结果，后者可显示运气/赛程影响的迹象，但不是因果证明。
2. **再看进攻投篮结构**：三分出手量/命中率、两分/内线创造、罚球、失误、篮板和对手防守。
3. **再定位人员因素**：核心/替补的使用、可用能力、年龄、伤病和合同，不因短期三分波动就马上交易。
4. **最后映射教练机制**：是否先改POE、体系或替补深度，还是实际缺乏某类人才。
5. 对于拥有足够分母的数据可用Four Factors（eFG、TOV、ORB、FT）做诊断，但缺分母时标缺口，不对任何“每百回合”值造假。

### 9.3 项目数据从哪里来

- 现有 `team_monthly_stats`、`player_monthly_stats`、`player_source_details`、`team_source_stats` 等是真实批次，当前M0只读CLI可按需查询；
- 游戏UI如提供更丰富的单场Box Score、Lineup On/Off和球员奖项，未来可依GM价值按需研究，不一开始无限扩大采集；
- M3数据分析应提供 **30队决策信号**，而不是重复输出“排行榜”；
- 研究清单中所有「该页面可以展示」与「我们目前已采集」必须分别登记，不能把看到的菜单当已获得数据。

---

## 10. 联盟设置 MyLEAGUE Settings：用户/Gemini全局清单逐类整理

**重要**：这一节以用户提供的候选字段全集为第一输入；用户已实机确认很多本世代和次世代全局设置相同，但**并未对下列每个枚举、默认值、范围、内部地址做逐项验证**。所以以下为标准化的**设置类别/候选参数**，不是“2K22 PC的认证字段字典”。以后由Antigravity产出页面截图→字段名和值域→实际地址证据。

### 10.1 一般与比赛基础（General）

| 候选项 | 含义和管理影响 | 修改时间建议 |
|---|---|---|
| Game Difficulty | 玩家手打或比赛对抗难度 | 世界配置，不让球队单独改 |
| Quarter Length | 玩家实际操控的每节时长 | 开局/世界配置 |
| Simulated Quarter Length | 电脑模拟比赛的每节时长 | 开局统一 |
| Game Speed | 动作整体播放速度，不等于持球最低速度 | 保持独立；不用于修中锋月球慢动作 |
| Fatigue / Progressive Fatigue | 单场/连续赛程体力疲劳 | 影响阵容/训练，世界级 |
| Shot Timing / Real Player % | 投篮由玩家时机或球员能力主导 | 主要影响手打，区分模拟 |
| Free Throw Difficulty / Real Player FT % | 罚球控制规则 | 主要手打 |
| Normalize Played Minutes / Normalize Played Stats | 把实际较短单节的手打时间与数据规格化 | 如果我们主要模拟CPU比赛，重要性较低 |

### 10.2 交易与人工接管（Trades & Trade Logic）

候选开关：Trades、Trade Logic、Trade Deadline、Recently Signed Restrictions、Recently Traded Restrictions、Rookie Signing Restrictions、Financial Trade Rules、Stepien Rule、Trade Override、CPU Trade Offers、CPU–CPU Trades、Trade Approval、Previously Traded Draft Picks；候选滑块：Trade Frequency、Trade Negotiation Difficulty。

候选价值权重：Overall Rating、Potential、Age Discount、Team Style Importance、Contract Years Remaining、Expiring Contract Value、Draft Pick Importance、Draft Pick Depreciation。

**经营作用**：约束游戏AI能否自己谈判、签订交易、发送报价、审查交易合法性。项目交易另由双方GM达成共识与获批执行。关闭`CPU–CPU Trades` 是减少野生交易的合理候选；然而「关闭原生Trade总开关是否也阻止外挂受控交易」必须通过实机验证，不能仅凭推理宣称最优值。游戏可能提供的交易审批/保护/互换机制，也不能自动改变我们的三年简单签位业务规则。

### 10.3 工资合同（Contracts & Finance）

候选：
- Salary Cap开关及Cap Value；Hard Cap开关及Hard Cap Value；Cap Inflation；Staff Budget；
- Min/Max Roster Size、Two-Way slots；Contract Negotiation Difficulty；CPU Re-Signing Aggressiveness；
- Salary Demands：Min Rating for Max Contract、Max Rating for Min Contract、Salary Curve、Potential Weight、Durability Weight、Minutes Weight、Player Fame Weight、Non-Financial Ambitions等（后面多项**尤其需要实机核对有无对应PC页面**）。

业务用途：决定原生球队能否合法签约、要支付多少以及球员报价倾向；**不是**把`cash/budget`两列相减获得球队自由市场资金。M1需同时研究游戏真实规则与外挂休赛期竞价规则。工资帽设置属于全联盟世界级，不由单队GM随意调低竞争对手工资空间。

### 10.4 成长、年龄与徽章（Progression/Regression）

候选：Player Progression Rate、Player Regression Rate、In-Season Training Effects、G-League Training Effects、Peak Start Age、Peak End Age、Badge Progression Rate、Badge Regression Rate。

业务用途：决定联盟总体球员成长生态，尤其本项目历史选秀轮回和历史重力阶段。**调全局成长滑块**与**外部修改单个球员能力**不同，但都影响世界平衡，应由玩家在开局/重大节点批准；正常GM不直接写个体能力。

### 10.5 士气、化学反应（Morale/Chemistry）

候选：Morale System、Morale Difficulty、Morale Effects、Team Chemistry、Chemistry Difficulty、Chemistry Effects。

业务用途：角色接受度、球队表现和稳定性（具体效应公式未认证）。我们过去把士气看作次要因素，不等于必须关掉，也不意味着可以凭社区经验说必然有固定“-10能力”扣分。是否保留自然球员意愿，属于世界规则讨论。

### 10.6 伤病（Injuries）

候选：Simulated Injury Frequency、Simulated Injury Severity、In-Game Injury Frequency User/CPU、In-Game Injury Severity User/CPU、Career-Ending Injury Frequency，另有总开关与疲劳作用。

业务用途：影响球队深度价值、替补轮换和老将续约风险。模拟伤病和手打伤病要区别；不应因某月一个球星受伤就临时更改全联盟的伤病发生率。

### 10.7 选秀及随机生成（Draft/Prospect Generation）

候选：Draft Lottery开关、Draft Class Quality、Prospect Potential、Attributes、Badges、Tendencies、Durability、Draft Storylines、Draft Age/Eligibility。

业务用途：原生随机新秀生态。**我们历史选秀由外部轮回控制**，这些如果对外部注入人物不起作用，就不应为了“更真实”随意调整；具体先核对PC菜单位与算法消费场景。

### 10.8 赛季模拟（Simulation Sliders）

候选：Sim Pace/Possessions、Team Scheme Impact、Attribute Impact、Sim Shot Success（内/近/中/三/罚）、Sim Shot Tendencies、各类模拟篮板/助攻/抢断/盖帽/失误/犯规权重、CPU Attribute Boost。

这些变量被Gemini列为模拟比赛参数，但当前PC真实菜单与实际字段一一对应**尚待核验**。它们与项目教练观测中的只读五项Sim字段**也不能自动对应**。以真实内存、UI标签和值域为准；模型调参不要借“提高胜率”单队擅自修改全联盟模拟规则。

### 10.9 比赛对抗 Gameplay Sliders：USER与CPU

这里与玩家当前控制的测试页面直接相关。候选一级分类：

| 类别 | 候选设置 | 作用 |
|---|---|---|
| Offense | Inside/Close/Mid/3PT Shot Success、Layup/Dunk Success、Contact Shot、Dunk in Traffic、Pass Accuracy/Speed、Alley-Oop、Body-Up Sensitivity | 手打/CPU比赛攻框、传球与对抗 |
| Defense | Driving/Inside Contact Frequency、Layup/Jump Shot Defense Strength（起跳/出手）、Help Defense Strength、Steal Success | 防守干扰及接触 |
| Attributes | Speed、Acceleration、Strength、Vertical、Stamina、Speed with Ball、Hustle、Ball Handling、Hands、Dunking、Off/Def Awareness、Off/Def Rebounding、Fatigue Rate、Lateral Quickness等 | 全局调节游戏比赛中的属性作用，不直接修改存档球员原始属性 |
| Tendencies | Inside/Close/Mid/3PT Shot、Attack the Basket、Look for Post Players、Throw Alley-Oops、Attempt Dunks/Putbacks、Play Passing Lanes、On-Ball Steals、Contest Shots、Take Charges | 全局出手/防守事件倾向，不同于单个球员tendency |
| Fouls | Shooting、Reach-in、Loose Ball、Charging、Blocking、Over the Back、Flagrant及版本可有的Illegal Screen | 犯规环境 |
| **Movement** | **Speed with Ball Min/Max、Acceleration with Ball Min/Max、Speed/Acceleration without Ball Min/Max**（具体用UI校准） | 限制最慢/最快球员的运动区间；中锋“月球运球”研究重点 |

**当前研究状态**：旧`src/slider_manager.py`的`ADDR_TRADE=0x0632FAE8`、`ADDR_SETTINGS=0x06332630`、`ADDR_SLIDERS=0x063319F8`是**历史候选偏移**，不能因为源码存在就当成当前进程已确认的真实读写地址。2021年Operation Sports Current Gen玩家确有讨论USER/CPU gameplay/sliders、伤病、犯规、投篮、运动等实际方案，但社区值不是我们的游戏默认值，也不证明某字段对应内存。

---

## 11. 联盟规则、规则变更与自动化

### 11.1 联盟规则（League Rules & Rule Changes）

用户提供的候选包括：进攻24秒/其它时限、进攻篮板回表14秒、8秒过半场、5/6/7犯离场、罚球Bonus触发、最低选秀年龄、乐透概率、全明星赛制、季后赛种子及干扰球规则等。

这类规则可能在**建档设置**或**休赛期联盟会议/规则修改**出现；系列Wiki记载休赛期存在联盟投票/规则变更的概念。不能把某个选项所在页面和具体投票频率认定为当前PC已验证。它们由**世界规则/玩家审批**决定，而不是30支球队每月任意重写，否则竞技生态不连续。

### 11.2 球队自动化（Team Automation）

用户清单候选包含：Roster Management、Injury Reserve Management、Free Agency/Extensions、Scouting、Training、ACE、Substitution Method，以及其它合同/选秀/员工/球探自动操作。

**最重要的行为边界**：`Team Automation`不是单个总开关。对每项应建立 `NativeAI / ExternalGM / HumanManual`责任矩阵：

| 功能 | 当前项目可承担多少 | 建议接管原则 |
|---|---|---|
| 球队主动交易 | 有受控获批交易（有限） | 优先研究屏蔽CPU自主交易，保留可执行交易入口 |
| 教练默认及对手整体防守 | 已有19/18原生教练接口 | 可由GM按节点建议、玩家批准执行，观察AI覆盖 |
| 具体单人上场分钟 | 游戏AI会覆盖外部细致写入 | **不接管精细分钟**；保持游戏管理 |
| 自由球员竞价/到期合同 | 已有外部规划与部分执行研究 | 未完成真实休赛期闭环前不要一口气关掉AI |
| 选秀/签约新秀 | 历史轮回/签位账本已部分具备 | 注入、球员选择、名单签约一致以后再接管 |
| 球员训练 | 只有高层需求，PC原生训练字段尚待核验 | 先学游戏机制再接管训练安排 |
| 员工招聘/解雇 | 在队与候选员工可采/查，受控执行待开发 | 先建立岗位适配与员工市场决策 |
| NBA比赛和自然成长 | 由2K执行 | 永远保持原生模拟，不直接外挂加能力 |
| 联盟结构扩军/搬迁 | 经营动作可见，风险高 | 开档玩家决定，平时默认不动 |
| 整体比赛难度/成长/Sim平衡 | 世界配置 | 玩家主导，普通GM不修改 |

这里明确区分：**“保留游戏AI处理某项业务”不意味着它是好的终局**；只说明外挂尚未形成可运作闭环时，不应制造球队没有签人/无人训练/卡在休赛期的问题。

---

## 12. 赛季运行阶段与休赛期（The Offseason）

这是终极联盟相对MC最值得经营的部分。一个赛季不是“82场比赛一口气模拟完”，它有多次经营关键节点。

### 12.1 常规赛

- 新赛季名单、员工合同、体系与轮换初始化；
- 通过日历推进赛程，观察胜率、排名、伤病、球员状态；
- 交易截止日前评估买方、卖方和资产价值；
- 每月/关键比赛节点触发GM V4；
- 处理教练对位、战术改变、长线战略稳定性。

### 12.2 季后赛

- 查看季后赛席位/附加赛以及对手；
- 更重视阵容健康、替补深度、指定对手防守和系列赛变化；
- 不能在无真实输入时编造“某套战术胜率+8%”；允许依据比赛具体表现比较战术；
- 决出总冠军及历史纪元记录（如2022勇士现实冠军历史重力参考仅在玩家批准历史线模拟时发生）。

### 12.3 休赛期操作图（**概念顺序**，不是已认证PC每一个按钮先后）

```text
季后赛结束 / 总冠军 / 奖项
  ↓
球员退役、教练/员工去留、联盟规则变化（实际先后需PC菜单记录）
  ↓
选秀顺位/乐透和当届候选最终名单
  ↓
NBA选秀 / 球员交易 / 新秀合同
  ↓
球员及球队合同选项、到期/续约/资格报价（实际先后按PC UI）
  ↓
自由球员市场多轮报价与签约竞争
  ↓
最低阵容人数/双向合同/裁员与合同清算
  ↓
训练营、球队战略/员工/教练调整、进入新赛季
```

关键提醒：**真实游戏内部流程可能把某些步骤放在完全不同顺序**。有的游戏会先显示退休人员、员工签约或选项，后显示选秀/自由市场。这里是GM经营工作链，Antigravity后续应实际记录每页`phase_id, UI标题,可返回/可跳过,所需玩家选择,是否不可逆`并替换为精确操作顺序。

### 12.4 GM休赛期最重要的经营链

- 选秀权是谁的？是否有未来三届可交易签，是否打算为争冠交换？
- 哪些球队急需腾出合同空间？哪些球队希望延长年轻核心的低成本窗口？
- 新秀预测表现与核心阵容冲突吗？合同成本和发展周期适合吗？
- 现有球员会不会成为自由球员？资格报价/球员选项/鸟权是否在游戏真实存在并如何执行？
- 双方GM的自由市场竞价与原生游戏签约，如何避免**重复发生**？
- 对手通过签约变强，竞争窗口是否需要调整？
- 30队是否都能合法进入新赛季，而不是某几支球队名单不足造成AI异常补人？

---

## 13. 完整玩法示例：从开档到第二赛季

**示例不是实际GM决策，也不修改游戏。**

1. 新建MyLEAGUE（30队、2021–22），选择赛程/工资/成长/自动化；存 `WORLD_PROFILE`；按需引入历史1984选秀规则但不把1984班强塞进2021年已有NBA球员名单。
2. 首次全量采集：30队阵容、合同、教练、员工、选秀权和球员池真实快照；新局单独save_id。
3. 分析模型SQL计算30队战绩/阵容、关键合同和战术弱点；GM读30队长期策略，优先提出少量影响大的方案，其余HOLD。
4. 例如马刺：现有Murray/Poeltl适合挡拆却外围投射不足，GM比较HOLD、教练/打法内部优化和交易；本局财政及Poeltl对对手队的价值需要独立谈判。
5. 玩家批准某个教练改动或CHI/DET等交易后，Codex在游戏原生内存执行并读取确认。**未批准不执行**。
6. 推进比赛。若比赛新闻提示CPU意外交易或伤病，记录问题但不默认认定可由外挂直接覆盖。
7. 到2月交易截止日前，GM评估争冠球队的短期即战力与重建球队未来签价值，避免所有球队都做无意义交易。
8. 季后赛根据对手防守调整POE/整体防守；游戏模拟自然决出冠军。
9. 到休赛期按菜单阶段停表，GM分别计划当届历史新秀选秀、球员合约到期、自由市场竞价和人员招聘。若执行器不支持某一步，暂停并由玩家/原生游戏处理，**不能跳过不可逆流程再假称GM全接管**。
10. 进入2022–23赛季，保存新快照、比较上季GM假设与真实比赛结果、更新30队长期战略，准备新历史选秀班。

---

## 14. 功能对接清单：未来决定“接管/保留”，本阶段只登记

| 模块 | 当前项目证据/基础 | 研究状态 | 暂定方向（待玩家审批） |
|---|---|---|---|
| 30队阵容与合同读取 | M02已采466在队+合同+55项属性 | PROJECT_VERIFIED | GM读取/决策 |
| 员工及候选池 | 1458观察，SQLite M0按需查询 | PROJECT_VERIFIED基础 | GM研究员工聘用 |
| 30队教练默认/对手防守 | 原生19/18，部分执行已证实 | PROJECT_VERIFIED | **优先GM接管** |
| CPU球队间自动交易开关 | Gemini候选，有旧历史偏移 | PENDING_PC_UI | **优先研究关闭** |
| 外部双方同意交易 | 有获批执行v2有限范围 | PROJECT_VERIFIED部分 | **逐步GM接管** |
| 球员签约/休赛期竞价 | 现有合成规划框架，生产仍需补充 | PARTIAL | 未来GM接管 |
| 1984→2020选秀班轮回 | 项目规则；历史模型池已采 | PARTIAL | 外挂计划，游戏原生选秀执行需核对 |
| 球员训练、员工加成 | 用户明确期望，PC实机尚待细表 | PENDING_PC_UI | 研究原生训练安排 |
| 全局工资、成长、伤病 | Gemini候选+部分旧地址 | MIXED | 世界档案、玩家主导 |
| 扩军/搬迁/重命名 | 系列及2022玩家实例 | CURRENT_GEN_GUIDE_PARTIAL | 默认不动；特殊世界事件由玩家决定 |
| 联盟新闻/历史奖项/单场统计 | UI概念有资料、现有事实采集不全 | PARTIAL | **优先作为观察/反馈** |
| 30队经营记忆与GM一次对话 | DEV10 M1–M4规划 | IN_DEVELOPMENT | GM V4 |
| 强行修改球员能力/训练成绩 | 游戏菜单可能允许，但违反项目日常规则 | POLICY_PROHIBITED | **不接管**，只有历史重力独立审批例外 |

**严禁误用**：旧`slider_manager.py`的历史地址（`ADDR_TRADE`等）未经当前进程确证，不应被这份手册自动认证；`docs/10_GAME_SETTINGS_AND_SLIDERS.md`是早期策略建议，不能当作所有旧设置已验收的生效证明。

---

## 15. Antigravity后续实机菜单记录模板（补全这本手册）

未来收到完整的教练、训练、员工、运营、选秀、扩军、比赛设置细表时，优先**扩充本手册已有板块**，不要每次再新建互相冲突的百科副本。

每个原生UI条目建议记录下列字段：

```yaml
menu_id: MYLEAGUE.COACHING.GAMEPLAN
ui_zh: "执教 / 教练比赛计划"
ui_en: "Coaching / Coach Gameplan"
mode: "NBA2K22_PC_CURRENT_GEN"
menu_path_observed: null        # 精确导航顺序
page_observed: false            # 有无当期PC实机截图
input_type: null                # toggle/enum/slider/list/action
ui_values_observed: null        # 当前UI确认的实际值域
scope: "TEAM"                   # WORLD/TEAM/PLAYER/MATCHUP
stage: "REGULAR_SEASON"         # SETUP/REGULAR_SEASON/PLAYOFFS/OFFSEASON
game_semantics: null            # 游戏功能说明
native_memory_evidence: null    # 程序地址/基址/布局，仅当实机差分确认
read_supported: false
write_supported: false
persisted: null                 # 是否跨菜单/保存/赛季持续
ai_overrides: null              # 是否被游戏自动覆盖
data_source: null               # 对应SQLite查询/数据源
gm_relevance: "HIGH"
control_owner: "UNDECIDED"      # USER_APPROVED_WORLD/GM_APPROVED/AUTO_NATIVE/HUMAN
evidence_level: "PENDING_PC_UI"
reference_urls: []
notes: ""
```

重要：本手册是*功能与玩法地图*，真正内存地址、写入能力应由未来独立 `MYLEAGUE_NATIVE_CONTROL_REGISTRY` 承担。来源论文/界面位置可对照，但字段字典和执行代码不能用主观攻略推断。

### 未来最值得补的PC实机页面

1. **完整菜单主层级**：行政办公室、执教、训练、球探、扩展、联盟新闻、排名、赛季/历史统计、选项/设置的准确中文/英文标签。
2. **Team Automation详细页**：球队名单管理、交易、自由市场、续约、训练、员工、球探、选秀各项AI代理开关及适用范围。
3. **教练补充**：19项默认/18对手以外的首发阵容、Playbook内部战术、球员Play Types、换人模式及实际可编辑性。
4. **训练+员工**：训练计划、强度、负荷、个人发展方向、岗位评价与雇佣/解约的实际菜单。
5. **新秀与休赛期**：从季后赛结束到新赛季每一步**真实UI出现顺序**，哪些是推进日期前必须处理。
6. **财务与合同**：游戏视图里显示的 `cash/budget/payroll/tax/cap`口径；员工预算与普通薪金是否互通。
7. **World sliders**：用真实UI当前页做字段/数据类型/内存差分，特别是 USER/CPU Movement 最低速度与加速度。

---

## 15A. 外部GM的能力边界：可查看并不代表已接管

- **已具备的观察能力**：30队名单、55项球员能力/合同、员工候选及原生8职位代码、球队财务raw、教练19默认+18指定对手防守、三届可交易选秀权、部分赛季统计。M0 SQLite用于按需查询，仍应先确认当前已发布批次和页面可访问。
- **有限可执行**：玩家批准的普通球员/签权交易、已验收的教练设置字段。**签约/裁员、员工任免、训练安排、导师、完整选秀及CPU自动化开关未被这份手册证明可写。**
- **未观测的关键运营数据**：当前`config/source_catalog.json`将伤病/疲劳/可用性/轮换统一列为`NOT_OBSERVED`；现有`player_monthly_stats`的injury列和`player_growth_history.mentor_name`不能凭有schema就当已采集。没有可信疲劳与恢复观测，月度训练应保持保守或由原生机制处理。
- **可以超越原生AI的部分**：30支独立GM、3年合同/选秀资产约束、跨队双边谈判、角色/战术适配、历史经营经验、信息不对称球探评估、跨批策略假设和经营效果反馈。这些均需在实际数据与受控执行基础上逐步发展，而不是先改球员属性。
- **六职位UI与八枚举待合并认知**：当前`STAFF.position`含HEAD_COACH/ASSISTANT_COACH/HEAD_SCOUT/TRAINER/GM/GOVERNOR/CFO/ASSISTANT_GM，具体哪些当前玩家可聘必须由PC页面核验；不能静默修改已采原始数据或把未证实职位当经营入口。

为避免重复维护，所有细分差距、优先级、训练决策草案与实机取证要求以[GM运营能力覆盖与月度训练专项](NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md)为准。

---

## 16. 资料来源、适用范围与版本冲突

**核心与原生模式有关的来源（本手册全文为原创摘要，不复制原文）：**

1. [NBA2K Wiki — MyLEAGUE（系列模式概览、扩军、规则变化）](https://nba2k.fandom.com/wiki/MyLEAGUE)，**跨版本概念**。
2. [NBA2K Wiki — Front Office（阵容/角色/交易/续约/球探/员工/自由市场）](https://nba2k.fandom.com/wiki/Front_Office)，**系列级菜单，不保证PC22逐字一致**。
3. [NBA2K Wiki — Coaching（比赛计划、阵容、体系、战术手册、练习）](https://nba2k.fandom.com/wiki/Coaching)，**系列级概念**。
4. [MyLeague NBA2K22 Current Gen — The Goods（2021-09-09视频，平台包括PC/PS4/Xbox One/Switch）](https://www.youtube.com/watch?v=PpGYIkBJwYg)，**本世代版本观测入口**。
5. [Operation Sports — 2K22 MyLeague settings/sliders（2021，本世代PS4用户真实测试）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders?p=24510715)，**本世代社区示例，非官方默认值**。
6. [DiamondLobby — How to Download a Draft Class in NBA2K22（2022）](https://diamondlobby.com/nba-2k22/how-to-download-a-draft-class-nba/)，**游戏攻略**。
7. [Reddit — 2K22 MyLeague Prospect Scouting（2022）](https://www.reddit.com/r/NBA2k/comments/zkqqwb)，**社区不完整观测**。
8. [Reddit — 2K22 Scouting加载选秀名单（2022）](https://www.reddit.com/r/NBA2k/comments/tlv74d)，**社区界面描述**。
9. [Reddit — 2K22 Relocation/Rebranding（2022）](https://www.reddit.com/r/NBA2k/comments/w3u7i8)，**社区具体菜单线索**。
10. [Reddit — NBA2K22 Expansion/Relocation 实例（2021）](https://www.reddit.com/r/NBA2k/comments/qh5kmf)，**玩家经验**。
11. [2K 官方：NBA2K22 MyNBA MySTAFF / Prep Hub / Conditional Coaching（2021-09-08）](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)，**明确PS5/Xbox Series平台，不可直接推广到PC**。
12. [GameSpot：MySTAFF and Prep Hub only on PS5/Xbox Series（2021）](https://www.gamespot.com/articles/nba-2k22-mynba-mode-features-new-mystaff-and-training-systems-on-ps5-xbox-series-x-s/1100-6496040/)，**版本差异确认**。
13. [Operation Sports — 如何调MyLeague轮换与Coaching Gameplan（跨版本旧帖）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/719111-how-to-adjust-lineups-and-rotayions-in-myleague)，**操作逻辑参考**。
14. [Reddit — 在NBA2K22 Coaching中Edit Playbook（2022）](https://www.reddit.com/r/NBA2k/comments/wsvt1u)，**同代玩家方法**。

**项目证据（开发仓库，优先于外部论坛对本局已实现能力的推断）**：
- `docs/34_BASELINE_CURRENT_STATE.md` — 当前局教练真实采集/执行状态与其它来源清单；
- `docs/39_COACHING_TACTICS.md`、`docs/40_COACHING_EXECUTION_RUNBOOK.md` — 原生教练战术读取与执行；
- `docs/GM_SQLITE_QUERY_ACCESS.md` — M0按需查询本地事实数据库；
- `docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md` — 用户定义的工程验证与行动边界；
- `docs/development_tasks/DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md` — GM知识/财务/数据决策/反馈建设；
- `docs/10_GAME_SETTINGS_AND_SLIDERS.md`、`src/slider_manager.py` — 早期设置/历史旧偏移参考，**不等于最新内存认证**。

### 最新待补状态

- **已形成完整业务地图与操作原理**，涵盖开档、首页、行政、执教、训练、球探、扩军搬迁、新闻统计、候选全局设置、CPU自动化、赛季/休赛期、30队经营框架。
- **尚不是逐像素逐菜单实机穷举**：Antigravity未提交各PC页面截图和逐项地址校准；因此存在`PENDING_PC_UI`，不得宣称清单每一项及每一个MemoryOffset已最终确认。
- 下一步先研究功能和实际操作，再由玩家**讨论每项交给GM还是游戏AI**，之后独立规划内存定位/控制开发；本手册不直接执行游戏写入。

