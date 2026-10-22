# NBA WORLD — NBA2K22 球员人格、媒体叙事与赛场沉浸可行性研究 V1

> 2026-10-19 / Web Development 研究文档。**研究，不是开发授权，不变更游戏及GM规则。**
>
> 已确认优先级：**GM V4先完成 → 球员系统 → 媒体系统**。赛场呈现的资源/Hook可行性允许独立只读研究，但不抢占GM开发工作。长期目标不只是交易/训练功能更多，而是让玩家在一个可演化的架空NBA世界中看到比赛的历史意义、媒体采访、职业人物和联盟时代。

## 一、系统价值：沉浸感本身是第一等目标

媒体可以没有任何游戏属性写入，依然是高价值的核心体验系统。现实NBA球迷的重要体验来自报道、系列赛叙事、赛前预告、赛后采访、球员和球队历史以及转播呈现。GM目标为经营合理性，媒体目标为「世界对玩家刚经历的事情给出及时、连续、有情境的回应」，不能因为没有影响球员能力就认为不值得开发。

与媒体「制造影响」相比，**媒体先学会观察、记忆、报道、解释和讲述连续故事**更重要。例：一个在架空游戏世界发生的破纪录比赛应在下一轮被媒体认出、在季后赛对手分析中引用、在赛后采访中再次提起；不能像没有记忆的NPC那样无视重大事件。

角色边界：
- GAME：唯一正式比赛、比分、数据、自然成长的来源。
- GM：球队管理、谈判/合同/交易/教练等获批行动。
- PLAYER_MODEL：本世界模拟职业态度、合同意愿、公开言论、私人职业目标，不得篡改现实真实人物史。
- MEDIA：根据允许访问的游戏事件、球员公开表态、经许可的GM公开信息进行独立报道、采访、流言/分析，**不自行制造已成交交易、伤病、球员能力变化**。
- WORLD_EVENT_LEDGER：事实分层、时间、来源、公开/内部信息边界、人物长期记忆。
- PLAYER（人类）：审核实际游戏内存改动；历史重力需要单独批准。

## 二、球员人格：游戏原生数值有利用价值，但要隔离

### 2.1 研究发现（来源等级）

- **官方2K20 Franchise开发日志**：2K20改进MyGM/MyLEAGUE士气/球队化学反应的每日平衡演化和人物关系；提供“Media Ringmaster”大城市、“Warm Weather Fan”温暖气候、“Finance Savvy”税务偏好等自由市场人格特征。这些具体机制有2K20历史依据，但不能未经本局UI/内存确认自动宣称22所有字段和算法完全相同。来源：[NBA2KW对2K20官方日志的转述](https://nba2kw.com/nba-2k20-mygm-myleague-mode-details-features-leaderboards-action-points-more)、[Operation Sports原开发博客](https://www.operationsports.com/nba-2k20-franchise-mode-developer-blog-mygm-2-0-myleague-more/)。
- **2022同代社区阵容工程**：“Play For Win / Financial Security / Loyalty”明确列为2K22球员设定调整目标；支持这些职业偏好是实用游戏数据字段线索，但未证实当前我们SQLite已有可信偏移。来源：[Operation Sports NBA2K22 Attention to Detail roster](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/)。
- **NBA2K20 MyLEAGUE攻略**：Ambitions界面描述比赛胜利、财务保障和忠诚度为0–100偏好（另有社区测试结果）；必须区分源适用2K20、并非已实测22。来源：[JeuxMangas攻略](https://www.jeuxmangas.com/soluces-et-astuces/24158-nba-2k20-les-stars-a-recruter-dans-ma-ligue-mon-gm)、[Operation Sports 2K19玩家实验](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/863174-barnsey-s-myleague-player-progression-regression-sliders-2k19/page6)。
- **本项目**：`config/source_catalog.json`当前只证明55项部分属性、合同、staff/教练等；`full_player_models`对完整徽章、人格倾向、历史和伤病数据尚未完全认证。不得因为原生2K存在相关菜单，就声称所有对应数值已经进入游戏事实数据库。

### 2.2 双层人物资料与影响边界

`NATIVE_PLAYER_STATE`: game可观察的士气、团队化学反应、Play for Winner、Financial Security、Loyalty、媒体/天气/税务偏好（实际字段待认证）、合同/球队/位置/出场/生涯比赛等。来源批次及可信等级必须记录。

`EXTERNAL_PLAYER_MIND`: 角色期望、谈判偏好、留队/交易意愿、公开采访风格、联盟世界的人际关系和职业故事，作为虚构NBA模拟角色状态。不能从真人现实姓名推断其真实私生活、心理疾病、关系/犯罪与未核实负面消息；需标明“本架空赛季模拟”。

自然影响闭环首选：`生活/职业事件 → 公开/私下诉求 → 经纪人报价条件/是否愿意续约/交易请求 → GM战略改变 → 玩家批准游戏内执行`。

用户提议：长期得不到交易希望时，触发能力下降。**此项目前不能执行**，与项目“不得经营性直接改球员能力”规则冲突。可先模拟强烈不满、续约要求变化、提出交易请求、公开发表诉求。待研究PC士气、化学反应或原生有效机制后，另由玩家审批是否仅同步到**原生情绪值**，观察游戏自己对能力的自然影响；不得直接降低球员原始55属性/潜力/徽章。若用户将来确实要求增加此类处罚，应先正式修改全项目经营规则，不能借球员模拟悄悄绕过审批。

**信息不对称**：人设私下交易希望不等于已经公开；媒体未经公开发言、经纪人授权或可信消息源不能按“确认”发布。新秀的游戏隐藏潜力即使数据库可读取，也应考虑独立球探信息权，不把模型变成全知球队。

## 三、2K20→2K22沉浸内容：可验证事实与猜想分开

### 3.1 NBA2K22 PC真实技术线索

- **NBA2K Hook by Looyh**：2021的工具介绍支持Mod文件热加载、多Mod目录、内置GUI、资源导出和加载日志、扩展DLL/Lua插件规划，说明PC22游戏资源与程序可通过已有模组生态接触，不代表开发者已经公开所有事件API。来源：[NBA2K 中文网](https://nba2k.net/threads/12982/)。
- **Hook插件脚本包（2022）**：公开列出Free Camera、Roster Modding、Player Editor和**Unlock Debug Options**，并注明官方补丁后仅能解锁部分隐藏菜单。由此能证明**部分隐藏/调试内容可重新访问**，但不能直接证明“2K20破纪录庆祝、采访触发器存在于2K22”。来源：[TGsoGood插件介绍](https://www.patreon.com/TGsoGood/posts/plugin-script-64657175)。
- **NBA2K22计分板Mod**：已存在自制NBC赛场记分牌以及包含/不包含犯规、暂停提示的版本。这是比赛内UI与转播层替换的具体实践，不等于“能向当前正在运行的游戏任意位置推送任意文字”，后者仍需单独探索。来源：[NBA2K22 NBC Scoreboard by Looyh](https://www.2kspecialist.net/2022/02/nba-2k22-nbc-scoreboard-by-looyh-fixed.html)。
- **2K22旧采访减少有社区记载**：2021年玩家问本世代半场/赛后采访是否已在21移除、22是否仍缺；另有2021–22 MyCareer玩家反馈采访很少甚至不出现。这证明功能体验存在差异，**不是被隐藏代码仍存留的证明**。来源：[2021提问](https://www.reddit.com/r/NBA2k/comments/pmxhqr)、[2022讨论](https://www.reddit.com/r/NBA2k/comments/s1fb9o)、[2021体验](https://www.reddit.com/r/NBA2k/comments/q2kfka)。
- **破纪录暂停庆祝**：玩家提到2K20曾出现的庆祝镜头属用户第一手回忆；本轮未找到可以核实它在2K22 PC可触发、其资源文件存在或状态机还保留的技术证据。**当前状态：UNVERIFIED_2K22_ASSET_AND_TRIGGER**，不要未经取证按内存地址实现。

### 3.2 四级可行性与“技术已证明”区别

| 层级 | 体验 | 技术判断 | 验收依据 |
|---|---|---|---|
| **R0 外部媒体** | Obsidian采访/专题/比赛前瞻/球员社交网络、赛季纪录片式连载 | **高、可直接开发**（Markdown与结构化资料） | 来源批次正确、人物连续、内容具备公开/模拟标识 |
| **R1 外置赛场覆盖** | 赛前画面、比分之外的球队新闻跑马灯、暂停/中场短新闻与赛后采访页面，可用独立窗口/叠加层 | **中高，需选定本地显示技术**；可以不修改2K进程 | 游戏能继续、不会遮挡关键操作，提供手动开关 |
| **R2 游戏内原生呈现扩展** | Scoreboard/overlay纹理、部分调试菜单/自由视角和资源、已有演出资源替换 | **中，已有NBA2K22 Mod先例但事件API未知** | 原始游戏资源/正确版本、离线可定位、稳定恢复 |
| **R3 深层游戏演出** | 动态记者采访镜头、打破记录自动庆祝、解说多句组合/球员原生口型、球迷推文插入 | **高难度且成功率未知**；资源、事件状态、音频/字幕、动画状态机同时成立才可行 | 静态资源存在+真实触发链/安全时机+一次隔离存档演示；不能仅凭2K20曾有认定存在 |

R2/R3只在本地离线游戏副本或测试存档研究，不联网对战、避开反作弊和账号服务，不下载或运行来源不明的可执行Mod；先只读核对原生资源/版本，再考虑玩家单独批准的受控测试写入。不要因发现可修改文件就大范围hook执行引擎。

### 3.3 Antigravity/未来研究模型应采取的取证顺序（不要求立即开发）

1. 盘点NBA2K22 PC本机版本/文件/已存在的Mod资源，**只读文件索引**；参考Hook资源加载日志/可导出资源做名称及引用检索，注意无需恢复/复制整个包进聊天。
2. 按**真实可见演出**收集控制样本：暂停、战术镜头、回放、节间、中场、赛后、赛季奖项、主客场各一次；建立UI按钮/可见事件目录。
3. 比较20和22对应的**可访问资源名/字幕/动画元数据/菜单字段**，确认到底是(A)仍在22但入口关闭、(B)资源仍在但触发脚本缺失、(C)仅20存在、(D)22有可重用不同形式的资源。各项记录`ASSET_OBSERVED / TRIGGER_OBSERVED / UI_VISIBLE / WRITABLE_VERIFIED`不能跳级。
4. 如果可定位场景事件，优先制作**不改变比分/球员能力/合同的纯呈现验证**；不要在比赛关键回合强制暂停或覆盖输入，避免损坏正常模拟；比赛中动态播报内容要考虑时机与字数。
5. 如果R3不可行，仍推进R0/R1/R2：优先做到进入季后赛像观看真实系列赛——比赛前资讯+赛后专访+连续人物故事+联赛历史回顾。

## 四、媒体在Obsidian的存储架构（建议）

**Obsidian原生使用本地Markdown文件+YAML属性+双向链接**，无需为了生成报道采购另一套封闭文章数据库。官方资料：[Properties](https://obsidian.md/help/Editing%2Band%2Bformatting/Properties)、[Internal links](https://obsidian.md/help/Linking%2Bnotes%2Band%2Bfiles/Internal%2Blinks)、[Obsidian URI](https://obsidian.md/help/uri)。

建议本地Obsidian Vault（路径由玩家以后配置）：
```text
NBA_World/
  00_Dashboard/
    Today.md                 # 当前日期、比赛、头条和争冠格局
  01_News/
    2021-2022/2021-12/
  02_Playoffs/
    2022/Round_1/
    2022/Conference_Finals/
    2022/Finals/
  03_Teams/
    SAS.md                   # 关联本赛季与长期经营叙事
  04_Players/
    <stable_person_id>.md    # 游戏身份/架空履历，不以姓名作永久主键
  05_Interviews/
  06_Draft_and_Free_Agency/
  07_League_History/
  08_Media_Organizations/
  09_Fact_and_Source_Index/
```

可选`article`属性：
```yaml
---
article_id: "NW-2022-PO-R01-G03-001"
career_id: "THE_NEW_MYLEAGUE_SAVE"
season: "2021-2022"
game_date: "2022-04-23"
story_type: "SERIES_RECAP"
media_outlet: "SIM_BASKETBALL_NETWORK"
status: "SIMULATED_IN_UNIVERSE"
visibility: "PUBLIC"
source_batch_id: "BATCH_ID_FROM_GAME"
source_event_ids:
  - "EVT-EXAMPLE-0001"
teams:
  - SAS
players: []
verified_facts: []
simulation_opinions: []
---
```

Markdown正文包括：数据事实、可公开的当事人声明（原生真实或**明确架空模拟**）、媒体独立分析、与此前赛季故事的关联。用`[[03_Teams/SAS]]`、`[[04_Players/<person_id>]]`建立人物/球队长期关联。**事实原本在SQLite，文章是媒体投影**；媒体不得修改原始游戏比分或报道未发生的已经成交交易。跨职业存档和历史纪元独立命名空间，确保1984新秀乔丹在架空局不自动获得现实六冠履历。

Obsidian可以由Codex本地命令行将Markdown以普通文件写入Vault；这比依赖一个尚未证实可连接的Obsidian插件更简单。必须先由玩家明确提供Vault目录权限和导出方案；目前没授权就不写本机Vault。

### 在媒体完全不影响游戏数值时的高价值体验节点

- **赛前**：重大比赛前瞻、两支球队的历史与战术、伤病/阵容仅依据已采来源。
- **常规赛每月**：球队专栏、交易市场、球员成长、数据对比、新秀观察。
- **交易截止日前**：确认名单/合同需求→可信市场流言→正式双方谈判→最终官方确认，不反过来拿流言创造已执行交易。
- **季后赛每轮**：对阵前瞻→逐场更新→抢七特别节目→赛后独家专访→晋级后的下一轮世界叙事。
- **破纪录**：实时UI无渠道时先做外置纪录突发新闻、赛后专访、历史榜单回顾，而不是球员破记录游戏画面完全没反应。
- **总冠军与休赛期**：王朝历史、球迷庆典、退役纪念、选秀大会前情报与赛后赢家/输家评论。

## 五、游戏实况事件频率与数据边界

项目当前发布主要是**月度/检查点快照 + 累计赛季数据**，不是逐球实时事件流。`config/source_catalog.json`的`games_box_scores_standings`是`VERIFIED_PARTIAL_SEASON_TOTALS`，且明示没有完整game logs/schedule/monthly splits；`injuries_availability_rotations`当前NOT_OBSERVED。由此：
- 每月文稿与赛季专题可以先做；
- **每场比赛赛后采访、每节演播室节目、赛场记录即时弹窗**需要未来再增加被真实批准的数据源或轻量只读实时触发信号；不能用两个月累计差额伪造某一场的具体转折、绝杀、单节比赛细节。
- 本项目保持`full_verified_v1`完整全量采集机制；若未来需要“游戏进行中的事件只读广播通道”是不同的可选架构议题，必须经玩家专门确认，不得在本研究偷渡一个未授权的增量采集器。

## 六、阶段顺序及验收

**正式业务建设顺序不变**：M1/M2 → M3 GM决策 → M4反馈/正式GM闭环；之后球员人格/经纪谈判，最后完整媒体系统。**沉浸机制只读可行性调研可另择空闲模型研究，不成为当前GM的阻断条件**。

未来按能力增量：
1. PLAYER P0：原生偏好字段认证、球员双层职业状态、诉求/续约/交易请求有来源且不篡改原始能力。
2. MEDIA P0：统一事件账本、世界事实边界、Obsidian Markdown写入及每月热点/重大交易报道（R0）。
3. MEDIA P1：季后赛专题、每场比赛卡片（**需要逐场数据**）、赛前/赛后媒体节目、人物采访（模拟世界，明确标识）。
4. PRESENTATION P1：外部窗口/覆盖层同步、转播增强和小型实机只读证据库；R2/R3是否推进取决于真实Hook事件与资源探索，不承诺一定解锁被移除内容。

**媒体系统的核心成功指标**不是能改多少游戏变量，而是：是否能依据真实NBA2K22游戏事件产生**情境正确、跨月和跨赛季连续、有人物记忆、不会伪造已经发生的比赛/交易**的报道，让玩家在季后赛获得真实系列赛氛围。

本研究不授权添加人物惩罚属性修改、不授权Hook运行、比赛自动暂停、原生采访强制注入或任何未经玩家批准的游戏写入。
