# DEV29 外部截图/图文证据索引

> 版权策略：本文件只保存网页定位信息和待证可见性，**不复制第三方图片到GitHub**。无法直接审看画面像素时只能标记“待人工/后续截图核对”，不能将帖主描述等同图片中确证字段。2026-10-20首次研究。

| VIS ID | 关联来源 | 游戏版本/模式 | 位置 / 原始网页 | 可追溯的证据与待核项 | 审查级别 | 分发许可 |
|---|---|---|---|---|---|---|
| VIS-0001 | SRC-0014 | NBA2K22 PS5/次世代 MyCareer（玩家自报） | [Reddit贴文内两张原始截图](https://www.reddit.com/r/NBA2k/comments/uxwomf)，原文靠近帖子开头“Image: img”两处 | **已核实原帖称包含两图**，帖主与评论谈Shot Chart/Hot Zones差异；**未独立读取原图像素、栏目名和数值**；不能证明PC MyLEAGUE页签 | EXTERNAL_VISUAL_CANDIDATE_NOT_PIXEL_VERIFIED | 第三方版权未明，只留链接 |
| VIS-0002 | SRC-0004 | 官方NBA2K22 PC英文手册 | [官方PDF第2页（0基索引第1页）目录](https://cdn.2kgames.com/manuals/nba2k22/PC/2KSWIN_NBA2K22_PC_Online_Manual_ENG.pdf) | **已逐页查看目录截图**，包含基本/进阶操作、战术及防守，不提供MyLEAGUE统计图谱；作为官方文档覆盖边界证据，不是游戏数据页 | OFFICIAL_PDF_PAGE_VISUALLY_CHECKED | 官方版权；仅链接，不复制 |
| VIS-0003 | SRC-0006 | 2K22论坛中的2K20历史Box操作经验 | [Operation Sports贴文第11页对应回帖](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/923062-thunder-up-rebuild-in-okc-nba-2k22/page11) | **文字证据索引，不是已发现截图**：回帖给出Box按Y/Triangle切换系列历史场次的方法，需PC22 screenshot/实机认证 | TEXTUAL_VISUAL_CAPTURE_REQUEST | 原帖版权，链接定位 |

## 目标PC22截图证据待办（R01-B，不依赖实时写入游戏）

| 待补截图位 | 需要截的画面与关联指南 | 最关键的证据 |
|---|---|---|
| `VIS-TODO-PC22-01` | MyLEAGUE联赛赛程：同一天一场已完成与未完成比赛 | 日期/主客/比分/菜单操作与可选Daily View |
| `VIS-TODO-PC22-02` | 已结束比赛的Box Score：球员页与球队页各一张 | 所有列、DNP/Starter、加时与节次、真实比赛身份 |
| `VIS-TODO-PC22-03` | 球员统计的页签栏、Game Log（若存在） | 是否有逐场栏目、可选赛季/阶段、对手/日期 |
| `VIS-TODO-PC22-04` | 球队/球员Season Stats：Per Game、Per36、Advanced（若存在） | 真实名称、字段与过滤器完整列表 |
| `VIS-TODO-PC22-05` | PC22 MyLEAGUE的Shot Chart/Hot Zones（若有） | 单场/赛季范围、分区/坐标的实际有无 |
| `VIS-TODO-PC22-06` | League Settings中Quarter Length、Simulated Quarter Length、Normalize | 实际选项名称、当前值、开关、对应游戏模式 |

**使用方式**：图源仅说明到何处核查。除`VIS-0002`外，本轮没有逐像素确认可引用的截图字段，公开攻略不得写成“已有PC22原生截图”。图证补全后可以按此编号推进；玩家私有实机截图遵守`visuals/README.md`的授权路径。


## DEV29 R01-B 图文与菜单证据增量（2026-10-20）

> 新索引的外部页面图片仍然**只做网页定位**，除非可读到图中像素和真实菜单，不得声称已认证任意PC22原生UI。数字ID与R01-A保留，不覆盖旧条目。

| VIS ID | SRC ID / 原始链接 | 对应版本/状态 | 图/文字所在位置与证明了什么 | 目前未证明什么 | 图像版权 |
|---|---|---|---|---|---|
| VIS-0004 | SRC-0020 / [Gamepur 2K22 Hot Zones攻略](https://www.gamepur.com/GUIDES/NBA-2K22-HOW-TO-FIND-A-PLAYERS-HOT-ZONES) | NBA2K22 MyCareer/MyTeam，文章标“Screenshot by Gamepur” | 页面中Hot Zone图/说明；原文给MyCareer暂停→Stats→Roster→R3→RT/R2切换Hot Zones | 截图像素未独立核对，**不是MyLEAGUE菜单图证** | 网站第三方，链接-only |
| VIS-0005 | SRC-0025 / [2K22 PC Remastered UI展示](https://www.2kspecialist.net/2021/09/nba-2k22-remastered-blog-new-details.html) | **MODDED_PC22_NOT_VANILLA** | “Main Menu Overhaul”及自定义PC版MyNBA样式截图所在版块，用来排除误用修改版界面 | 不可作为PC22原生统计页/Hot Zone/Box确证 | 第三方模组作者，链接-only |
| VIS-0006 | SRC-0024 / [NBA2k线上未保存比赛BUG报告](https://www.reddit.com/r/NBA2k/comments/xk44uu) | 2K22/23线上模式跨平台，不属于目标PC离线 | 发帖文字称附50多场未存比赛的截图；定位到正文第2个“Bug”段落；本轮**未核对图片像素** | 并无PC22离线Game Log历史留存证据 | 玩家图片，只留原帖链接 |

### 重要的“只有文字，没有截图”的索引

- [SRC-0016 OS 2K22 Useful Findings 第7页 #93/#96](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page7?t=992582)：玩家**用文字**指出游戏结束后Shot Chart可与Stats Summary/PIP比对；这是一手报告，但**不是截图认证**。
- [SRC-0017 Reddit 2K22 Feedback](https://www.reddit.com/r/NBA2k/comments/plmeto)：PS5玩家**用文字**指出Triangle切到Per36和该页排序异常；无本轮独立核对的PC22表格截图。
- [SRC-0021 OS 2020 MyLEAGUE历史Bracket](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/889354-myleague-viewing-past-playoff-bracket)：Coach2K仅文本回答，没有确认旧单场Box留存范围。

### 下阶段最有价值的截图集合（保留R01-A的六位TODO）

优先序：`VIS-TODO-PC22-03` (Stats页面完整表头、Triangle/Y真实按键) → `VIS-TODO-PC22-02` (当前赛季主客Box、球员列和球队列) → `VIS-TODO-PC22-01` (同日不同比赛日历与进入Box方式) → `VIS-TODO-PC22-05` (赛后Shot Chart及历史查询) → `VIS-TODO-PC22-04` (球队/球员Advanced、Per36所有列) → `VIS-TODO-PC22-06` (实战模拟分钟与标准化参数)。额外需要**跨赛季的只读存档画面**验证旧Bracket/Box是否能调出，不能为了取证擅自推进正式世界线。


## DEV29 R01-C — 官方图文中的Box描述与PC截图缺口（2026-10-20）

| VIS ID | 关联 | 图文位置、实际可见信息 | 为什么不能当PC22 Box证据 | 权利/状态 |
|---|---|---|---|---|
| VIS-0007 | SRC-0026 | [2K22 MyNBA开发团队说明](https://hoopsgamers.com/nba-2k22-mynba-full-details-mystaff-training-pre-built-teams-more) 的`COMPACT SPREADSHEETS`小节；旁边配图为`MySTAFF Roster`，[该配图原地址](https://assets.2k.com/1a6ngf98576c/7jr3c008x0rKag3ykS3nGs/adaf38d3e3c8870bb2337758d53eb751/Roster.jpg)。对应**官方文字**提到了Box Score，但图片名称为Roster.jpg，不是已证的Box Score截图。 | 官方原文明确本节属于2K22 **次世代MyNBA**，不能证明PC本世代MyLEAGUE布局，也没有提供完整球员/球队Box表头。图片原地址本轮未逐像素解析，不升级为已检视像素的Box证据。 | 2K官方图片受版权保护；仓库只索引，不转载。状态：`OFFICIAL_NEXTGEN_ADJACENT_VISUAL_NOT_PC22_BOX` |

### R01-C图源质量审计

公开检索出现若干题为“NBA2K22 PC MyNBA”的图片，已登记`VIS-0005`说明存在**将次世代界面移植到PC的Remastered模组**，无法在缺少原版/模组元数据时拿来确证PC原生菜单。其它命中包括NBA.com 2021–22真实比赛的Box、NBA 2K22 MyCareer热区图、2K21/2K23教学视频、非NBA2K统计模拟器；**不得计入PC22 MyLEAGUE原生菜单截图覆盖率**。

**保留未完成原生取证任务**：`VIS-TODO-PC22-01..06`全部待PC22原版画面。R01-C为其补充以下**单张/少量截图即可回答的判定标准**：

- `STATS_HEADER`：截图包含游戏版本/页面位置、筛选器、列名以及底部按钮映射；每种Totals/PerGame/Per36/Advanced类型各至少一张，不能单凭2K22 PS5写PC按键。
- `GAME_BOX_TWO_TEAMS`：在同一场已完赛比赛显示主客身份及两个队伍的球员行、团队总计；每页可以多截，记录是否能横向切列。
- `GAME_LOG_OR_CALENDAR`：若找不到独立Game Logs标签，也要拍可检索到的所有相关Stats页签并记录实际路径，才能区分`FEATURE_NOT_FOUND_IN_UI`与`GAME_LOG_ABSENT`。
- `POSTGAME_SHOT`：同场赛后Shot Chart与赛程旧Box页面分别截图，核查是否能在离开比赛后重新打开；热区图不能替代Shot Chart。
- `OLD_SEASON_BOX`：只在已经自然经历跨季的**只读页面**检查旧季；不推进、修改正式存档，也不能以旧赛季Standings推断旧Box有无。

原网页/视频的**准确时间戳若无法读取视频帧，保持`UNKNOWN`**，不得虚构“第几分第几秒看到表头”。图证索引暂不上传任何图片二进制。


## DEV29 R01-D — 最终截图来源审计与最小取证请求（2026-10-20）

**本轮合格新增`VIS-####`为0。** 既有`VIS-0001..0007`全部保留原先版本、来源和许可级别；没有任何一条升级为目标`PC22_UI_CONFIRMED`。**严格禁止为了凑图源数把游戏封面、Steam外层成就统计、NBA.com或2K22 PC Remastered当作原版MyLEAGUE统计图。**

### 排除项（不是新增VIS）

- [Steam NBA 2K22社区Screenshots](https://steamcommunity.com/app/1644960/screenshots/)：PC游戏平台身份成立，但当前检索未找到可同时识别原版MyLEAGUE及真实Box/Stats表头的可审查图片；外层“View Stats”是成就页，不等于游戏内`Player Stats`。
- [GamesKeys 2K22 MyLeague Player Lock文章](https://gameskeys.net/how-to-use-player-lock-position-lock-in-nba-2k22/)：带MyLEAGUE操作截图但主题是`Player Lock/Position Lock`，不显示本次需要的Box/Advanced/Game Logs表头；按键提示采用PS手柄术语，平台不能强行标PC。
- [2K22 PC Remastered](https://www.2kspecialist.net/2021/09/nba-2k22-remastered-blog-new-details.html)已有`VIS-0005`：非原版，禁止提升UI认证。
- 其它视频/图片检索：无法读取实际相关帧或得不到准确时间戳时只能记录为`VIDEO_FRAME_NOT_REVIEWED`，**不能声称看见任何具体字段**。

### 从六类TODO缩成三组最少截图（用户将来可按需提供）

| 优先级 | 保留原TODO | 最少提供 | 从画面要记录的原始事实 | 一组图可关闭的疑问 |
|---|---|---|---|---|
| **A，先做** | `VIS-TODO-PC22-03`+`04` | **约2张**：①Stats入口/菜单栏/按钮提示；②进入Player Stats或League Leaders后页签、切换提示、真实表头 | `NBA2K22 PC original offline MyLEAGUE`、选中球员或球队、栏目名/英文原文、筛选、按钮映射 | ①Stats、②独立Game Logs是否可由页签看出、④Per36/Advanced候选 |
| **B，接着做** | `VIS-TODO-PC22-01`+`02` | **约2张**：①已完赛日期的Calendar/选中比赛操作菜单；②同一场Box含主客/列名；另一队或Team Totals不在同屏时补一张 | game date/season/phase、主客、Box球员/球队栏目、能否横向切字段 | ②Calendar→Box实际路线、③Player/Team Box和本季比赛可回看 |
| **C，按需要** | `VIS-TODO-PC22-05`+`06`及跨季 | **按已有页面补1–2张**：赛后Shot Chart或已经自然完成的旧赛季Box入口；若模拟口径仍不明再拍Setup | 图中区域/图例/时段、是否从旧比赛重开、跨季可见窗口、实际`Normalize`名称 | ⑤Shot Chart与Hot Zones关系、⑥历史留存；节长标准化作为质量上下文 |

当组A/B无法显示某项，也只记录`NOT_VISIBLE_IN_OBSERVED_PAGE`，而不是`FEATURE_ABSENT`。组C的“跨季”只能在**已自然跨季**存档进行只读查询，不为取证擅自模拟或推进正式世界线。所有图片若未来获准归档，需补作者/平台、存档阶段、版本、无模组声明、操作页面路径、字段、权利及`VIS`编号；**本轮没有上传任何第三方媒体文件或生成图像**。

**结案标记**：`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。未来R01截图空缺交给独立玩家只读页面取证/以后授权的Antigravity，DEV29网页研究现在直接转R02。详见[PROGRESS](../PROGRESS.md)与[攻略§20–22](../guides/K01_K02_GAME_STATS.md)。

## DEV29 R02-A — 教练与战术视觉证据审查（2026-10-20）

视觉素材不等于每个画面的游戏版本与模式已经认证。**本轮没有新的NBA2K22 PC原版MyLEAGUE Coach/Playbook/ACE全部菜单的逐像素认证图**；资料的一手文字可以支持机制经验，但截图等级必须独立审核。

| VIS ID | 来源、原始页面 | 可定位到什么 | 图证等级与适用限制 | 许可 |
|---|---|---|---|---|
| **VIS-0008** | SRC-0033 / [Operation Sports 2021-10-18：Help Defense Saga Part 2](https://www.operationsports.com/the-ongoing-help-defense-saga-in-nba-2k22-part-2/) | 文章页面主图为“NBA 2K22 help defense”，正文中有作者引用的弱侧协防/赛中画面示例说明和视频内容区；真实支持的是**同年文章中的防守AI/补丁评论** | **EXTERNAL_VISUAL_CONTEXT_NOT_MENU_PIXEL_VERIFIED**：本轮未独立检查视频逐帧、不提供时间戳，主图也不是已认证的PC22 Coach Gameplan字段截图；不能证明本局菜单某项已实现 | 图片/视频属原作者或第三方，仓库仅留网页链接 |

### R02-B定向视觉候选清单（暂不把待办算成VIS证据）

| 待办 | 最少画面及为何重要 | 能认证与不能认证 |
|---|---|---|
| VIS-TODO-R02-01 | 原版NBA2K22 PC MyLEAGUE Coach Gameplan首页、POE栏目、底部按键提示 | 静态POE页签/菜单；**不**证明3D自动效果 |
| VIS-TODO-R02-02 | 同一球队Book编辑界面：Regular/Bench/Endgame/Favorite切页及1条完整Play Name/2D战术预览 | 证明UI类别、槽位与当前CRC关联候选；**不**凭名字写入类型id |
| VIS-TODO-R02-03 | Player Edit/PlayTypes四槽有序分配与12类具体play目录过滤面板 | 证明“球员角色枚举≠play类别”两个界面独立；需同时记录过滤后候选及实际动画 |
| VIS-TODO-R02-04 | Freelance四槽与Offensive Settings/ACE/Automatic Playcalling是否在比赛暂停/Timeout菜单出现 | 区分本队静态Coach字段和比赛内动态调整；不从PS5视频直接推PC |
| VIS-TODO-R02-05 | 选定对手具体球员的个人防守页及整体防守页（只读） | 查看18类列及特殊OnBall5/Hedge5/TagOnRoll含义；**日常GM仍不写OVERALL** |

已检索但不当可认证画面：SRC-0034 Xbox One+Series X原帖写了防守选项且作者纠正错误，可给**同代文字**，不自动产出PC22截图；SRC-0039 NG玩家写PlayVision/Auto菜单，不代表其有目标PC UI；SRC-0038按键控制表，不是球队Coach配置图。未来如有玩家自供真实截图且获得允许，可按[视觉材料规范](README.md)在approved/独立保存。**R02-A研究无游戏读写、无第三方图片复制、无虚构视频时间戳。**

## DEV29 R02-B — 菜单真实画面审计与最后一轮PC22截图优先级（2026-10-21）

**新增合格原版NBA2K22 PC MyLEAGUE可读菜单图证：0；VIS-0001..0008原证据等级不变。** 仅有文章正文引用了“视频”“Image”或玩家文字说明菜单，并不能登记为`PC22_UI_CONFIRMED`。没有获取或上传任何版权不明的图片文件。

| 文本/画面线索（本轮新增） | 原始页面 / 来源 | 实际核实到的证据 | 不得声称 |
|---|---|---|---|
| 2K22的ACE即使Off，Defensive Settings仍自动切回的报告 | [OS 2022-01 贴文](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/920049-defensive-settings-not-staying-on-custom) / SRC-0040 | 原作者与回复在搜索索引可读；**直接打开因redirect loop失败** | 已看见PC22原版ACE UI/证明一切ACE设置无效 |
| 2K22 Series选中后回Freelance | [OS 2021-09-16原帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917118-are-series-not-working) / SRC-0042 | XBX作者的**文字一手报告**，没有本轮逐帧视频和时间戳 | PC22必然同错，或已经读取Series native ID |
| Xbox Series X/S **MyTEAM**的Run Freelance菜单步骤 | [Reddit 2K22教程](https://www.reddit.com/r/MyTeam/comments/q36nsh) / SRC-0043 | 作者自报平台与按键、场上两步激活流程；**未提供可复核PC MyLeague页签图** | 相同的PC22按键/自动CPU调用 |
| 2K16的On Ball Screen (Center)与Hedge (Center)讨论 | [OS 2016 第2页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/806956-on-ball-screen-center-hedge-center/page2) / SRC-0044 | 可读取旧版多位玩家对持球防守者/掩护人/己方大个身份的争论 | PC22 Center字段精确触发、UI顺序或实战执行已实机认证 |
| 旧版TagOnRoll从Gameplan消失、SimCast仍能访问的报告 | [OS 2018 第2页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/865843-defensive-settings-discussion/page2) / SRC-0045 | 玩家文字明确表示**没有验证SimCast改动效果** | PC22一定隐藏或SimCast能执行 |
| PC版CPU-vs-CPU MyLeague实际玩家生态 | [OS NBA2K PC Forum](https://forums.operationsports.com/forums/forum/basketball/nba-2k-pc-forum/918715-cdcool-nba-2k22-cpu-vs-cpu-myleague-sliders) / SRC-0046 | 原帖实际自报PC、控制所有队、逐场看3D不快Sim | 已经找到本机PC22 Coach菜单像素/默认数值 |

### R02-C仅一次目标视觉补证，优先2组少量截图

- **组A（控制入口，优先2–3张）**：现有原版PC22离线MyLEAGUE Coach Gameplan中的POE/Coach Settings/Freelance四槽、ACE/自动叫战术菜单（若出现）。要求画面包含完整栏目、可选值、上下文与底部按键说明；需分清赛前静态 vs 暂停临场，两者若不同分别标注。
- **组B（战术内容/对手方案，优先2–3张）**：Book编辑内Regular/Bench/Endgame/Favorite、12类别筛选、某条具体动作的2D动态棋盘；以及选定对手某持球者后的PERSONAL Defense页中`OnBallScreen(Center)/Hedge(Center)/TagOnRoll/PreRotate`（已有页面能看见哪些就截哪些）。
- **历史保持未知**：任何截图能证实**UI菜单是什么**，但不能证明3D比赛真实跑此play或ACE永久保存。同一对手不同时间读数对比/视频必须有明确场次、时间戳与平台；未经同意不推进/模拟正式比赛。

若第三方公开视频无法读取足够清晰的原始菜单画面、没有可信的精确时间戳，统一`VIDEO_FRAME_NOT_VERIFIED`。R02-C若仍无新一手原版图，**保留UNKNOWN并关闭R02公开研究，转R03**；不为一个UI无限重复搜索2K16或在研究期启动DEV28/Antigravity。本文件只有文字索引、没有第三方截图复制。

## DEV29 R02-C — 最后一轮直接图证核查及R02研究结案（2026-10-21）

**原版NBA2K22 PC本世代离线MyLEAGUE Coach/ACE/Playbook/Freelance/Personal Defense可复核完整UI新增：0。** 保留`VIS-0001..0008`既有定位和证据等级，不把本轮检索到的截图容器、文章主图或模拟版MyNBA误记为`PC22_UI_CONFIRMED`。本轮没有获得能完整核实的目标视频帧或准确时间戳；因此**不新增编号式VIS实证**。SRC-0048是MyLEAGUE玩家对Freelance按球队自动保存的**纯文字**一手报告，亦不产生图证。

### 定向公开素材审计

| 链接/检索线索 | 实际来源属性 | 结论 |
|---|---|---|
| [NBA2K22 Steam社区](https://steamcommunity.com/app/1644960/screenshots/)及[SteamDB游戏截图](https://steamdb.info/app/1644960/screenshots/) | PC游戏ID是正确的，但目前没有可辨别目标MyLEAGUE赛前Coach页面全部字段的独立原版画面 | **PC game container only**，非原版Coach截图实证 |
| [官方2K22 MyNBA新功能报告（OS转载）](https://www.operationsports.com/nba-2k22-mynba-details-revealed-mystaff-staff-carousel-prep-hub-attributes-badges-more/) | **PS5 / Xbox Series的MyNBA**；明确含Conditional Coaching和更新后的Coach Gameplan表格 | 可供V3未来条件决策概念参考，**不得认证PC本世代也有该原生命令界面** |
| [2K22原版PC Remastered UI新闻](https://www.2kspecialist.net/2021/09/nba-2k22-remastered-blog-new-details.html) | 标明移植MyNBA外观的改装PC UI，先前VIS-0005已登记 | 排除，禁止当作vanilla MyLEAGUE |
| [NBA2K22同发行季MyLEAGUE Freelance保存讨论](https://www.reddit.com/r/NBA2k/comments/qg2amb) / SRC-0048 | 2021-10/12文字，平台未知，玩家表示比赛中改Freelance会为队伍保存 | **TEXT_ONLY_NO_VIS**，不认证PC22保存范围 |
| [被错误日期误导的“2K22精确分钟”攻略](https://www.magicgameworld.com/how-to-adjust-player-minutes-in-season-mode-in-nba-2k22-myleague/) | 显示2021-04-30早于2K22正式发售，且无可读原版菜单，仅泛化控制叙述 | **REJECT_DATE_PROVENANCE_AND_GAME_AI_CONFLICT**，不单独分配VIS |

### 保留的最小未来只读截图需求（不会阻断R03）

**A：教练设置两页。** 同队原版PC22 MyLEAGUE赛前Coach Gameplan（包含6 POE中的实际项目/下方按键），以及比赛暂停/ACE/进攻设置（如可进入）各1张；记录是否同一支球队和游戏阶段，避免把比赛策略当静态字段。

**B：战术/防守两页。** 本队Book内一条play的完整名称、类型筛选及2D战术板（如果不是同页可追加1张），以及一个指定进攻球员的PERSONAL Defense页面（优先Center与TagOnRoll/PreRotate选项）。可以先只提供有画面的部分，未出现的字段仍UNKNOWN。

身份条件：`NBA2K22 / PC_CURRENT_GEN / VANILLA_UNMODDED / OFFLINE_MYLEAGUE / menu_path / game_date / team / before-or-after-timeout`，且真实表头能清楚阅读；不要求玩家模拟正式比赛或读取内存。**未看见某个字段≠引擎没有该功能。**

**R02官方结案：`R02_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。** 已有原生字段和当前采集能力保留原等级；待以后独立授权的Antigravity/DEV28定向只读取证或玩家偶尔自主截图时，增量升级K04，不重开R02整个网络研究。**下一研究批次R03训练/健康与自然成长。**

## DEV29 R03-A — 训练和负荷的官方可读图证（2026-10-21）

本轮新增**2个已实际查看像素的官方2K22次世代图源**；**NBA2K22 PC本世代离线MyLEAGUE训练菜单合格画面仍为0**。第三方/官方版权图片**只留稳定原图URL/官方出处，不上传到GitHub**。图源版本不可因同为2K22而合并。

| VIS ID | SRC ID/官方页与原图 | 平台、模式、具体可见栏目 | 原生PC22取证资格 | 权利及状态 |
|---|---|---|---|---|
| **VIS-0009** | SRC-0049/0050；[2K Newsroom原页](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)；[Individual Training Focus PNG](https://cdn.prgloo.com/media/2858117e546348dbb3c016b7282e72c3.png?height=663&width=442) | **NBA2K22 PS5/Xbox Series MyNBA**：已看见`SKILL TRAINING FOCUS`、位置列表PG/SG/SF/PF/C、`PLAYER TYPE`、`TRAINING COMPATIBILITY`列及所选球员OVR；PG可见一组all-around/two-way/Offensive/Defensive/Athletic/Rebounding/Playmaking/Outside Scoring/Inside Scoring原型名称 | **不符合PC22_UI_CONFIRMED**；不能凭截图给本机(player.position,player_type)和UI顺序建立1:1 raw映射 | `OFFICIAL_NEXTGEN_SCREEN_PIXEL_REVIEWED`，2K版权，仅文字/外链 |
| **VIS-0010** | SRC-0049/0050；[官方Newsroom原页](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)；[Training Schedule PNG](https://cdn.prgloo.com/media/eedbfc01c17a465eb26f5093c697ee8b.png?height=663&width=442) | **2K22次世代MyNBA**：已看见`TRAINING SCHEDULE`日期日历、底部`TEAM SYSTEM`、`TRAINING GOALS`、`TEAM OVERVIEW`三块信息摘要；多日练习/比赛与球队系统显示在同屏 | **不符合PC22_UI_CONFIRMED**；不能证明PC当前局逐日计划、实际疲劳单位、官方建议训练配方；小图中的所有练习格文字未完整验明 | `OFFICIAL_NEXTGEN_SCREEN_PIXEL_REVIEWED`，2K版权，仅文字/外链 |

同页有[Prep Hub原图入口](https://cdn.prgloo.com/media/3d1a4901fc3c49cd8f4a0f65808d1a61.png?height=663&width=442)，**本轮无法可靠取回原图像素**，只作为文字定位，不分配新的已认证VIS。

### PC22 R03未来最小分批只读证据（无需现在提供）

1. **团队训练页（约1–2张）**：原版PC22无模组离线MyLEAGUE，完整主页/客场强度、是否Auto、背靠背前后休息与恢复选项的屏幕、可选值、游戏日与页脚控制提示。
2. **个人训练页（约1–2张）**：当前人物、Position、可见训练原型/模板列表、强度、Override和伤病恢复，优先一名PG及一名中锋用于发现UI模板按位置变化。不要为了取证擅改正式存档。
3. **健康和导师页（以后可选）**：在已经自然发生的状态下截玩家fatigue/fatigue history、伤病状态与预计康复、训练师/导师链接，以及徽章发展的显示数据；必须区分“历史条”和“当前值”。

截图可认证**菜单候选/来源身份**，但不能保证训练收益或伤病概率。现有技术目录的`progressive_fatigue_history`尚无本轮实时解码认证，不能以任何截图名词替代。

**R03-A真实图证：VIS-0009..0010为2K22官方次世代**；目标PC22新增UI图证0。后续R03-B继续伤病/恢复/真实负荷来源，不需再次把Prep Hub营销稿当作PC22证据。

## DEV29 R03-B/C — 健康/导师原版视觉取证与审核结案（2026-10-21）

R03-B和R03-C新增合格`NBA2K22 PC VANILLA OFFLINE_MYLEAGUE` **健康状态、伤病列表、康复剩余天数、导师进度或Trainer精确效果的菜单截图：0**。既有`VIS-0009/0010`是已实际查看像素的**2K22官方次世代MyNBA训练页**，持续作为高价值终极联盟机制参考，不降级其机制价值，也**不冒充PC本世代屏幕或字段读值**。

| 可追溯图证线索 | 本轮实际可用证据 | 图证级别与边界 |
|---|---|---|
| [OS 2021 MyLeague Injury Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918980-myleague-injury-sliders) / SRC-0060 | 玩家关于手打/Sim伤病差异的**文字实战报告**，也有人自述亲见Luka受伤动画 | `TEXT_ONLY`；未看到可认证PC22的受伤视频具体帧 |
| [OS 2022 MyLeague Why no injuries](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/921266-myleague-why-are-there-no-injuries) / SRC-0061 | 多位玩家对滑块/Durability调节作出互相冲突的文字描述 | `TEXT_ONLY`；改Durability不是研究授权动作 |
| [OS 2022/23 MyNBA Injury Duration](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/926689-mynba-injury-duration) / SRC-0063 | 历史伤停时间与实际返场提前的玩家回忆/个案 | `TEXT_ONLY`；无原版PC22恢复日列表像素 |
| [Reddit 2022 Mentor assignment crash](https://www.reddit.com/r/NBA2k/comments/s88jzz) / SRC-0068 | 玩家对某些导师组合会引起崩溃的文字描述 | `TEXT_ONLY`；未获得重现录像与PC版本证据 |
| [2K官方新世代MySTAFF医疗分工](https://www.operationsports.com/nba-2k22-mynba-details-revealed-mystaff-staff-carousel-prep-hub-attributes-badges-more/) / SRC-0064 | 各Sports Medicine职位功能的官方文字/图片上下文 | `OFFICIAL_NEXTGEN_MECHANISM`；不证明PC22本世代能聘七个新医疗岗位 |

### 以后最少4组可分批取证（不是现在让用户执行）

1. **真实伤病页**：当前Game Date、球队、具体球员身份、伤病类型/部位/严重度、预计返场天数与真实最后复赛日期。至少同一球员两个自然出现的时间点；未出现伤员时不人为制造。
2. **实时与历史疲劳**：同一球员的比赛前/后体力、Training History或Progressive Fatigue字段，明确时点、单位、原版或次世代来源；不由过去历史尾数假装当前体力。
3. **导师页**：一个真实Mentor/Mentee pair、可选Badge、Compatibility和自然推进后的进度，优先仅只读；发生已知崩溃风险则停止，不操作正式游戏。
4. **PC本世代Trainer与个人训练原型**：训练师原生UI属性、球员Training中的Position+Player Type原型与Intensity、是否显示Recovery等，和现有Registry逐项映射。

研究完结时的图证状态：`R03_RESEARCH_COMPLETE_WITH_NATIVE_DATA_GAPS`、`PC22_HEALTH_UI_FULL_VERIFIED=0`。**不能据此说原版游戏没有健康菜单，只是当前公开材料无法完成源级认证**。R04完整身体部位Durability的研究会独立展开，在用户审核R03后方可启动。

## DEV29 R04-A — 原版2K22球员资料与Badge视觉证据登记（2026-10-21）

本轮检索NBA2K22本世代MyLEAGUE原始**Edit Player / Vitals / Attributes / Durability / Badge / Personality / Development**菜单，以及同年PS5 MyNBA的可借鉴画面。研究取得**版本指向明确的详细球员字段页面**，但没有逐帧/像素确认`vanilla_PC22_Offline_MyLEAGUE`中同样分组和完整标签的可读截图，**不新增`PC22_UI_CONFIRMED`或已认证正式VIS编号**。本页保留稳定网页索引和未来最小证据请求，供R04后续研究使用。

| 原网页/视觉线索 | 真实性与这次具体获得什么 | 视觉审查结论 |
|---|---|---|
| [2kAuction：NBA2K22 Joel Embiid](https://2kauction.com/mynba/2k22/players/joel-embiid?roster=offseason_nba) 和 [Marques Johnson](https://2kauction.com/mynba/2k22/players/marques-johnson) | 页面以原站文字版分栏输出`Attributes/Badge/Bio/Development/Contract/Injuries`，每个字段具体存在并配一个导出玩家数据样例 | **THIRD_PARTY_GAME_SNAPSHOT_HTML_NOT_GAME_MENU_PIXEL_VERIFIED**：可作字段清单和示例来源，不是原版游戏菜单截图、不是本项目当前save |
| [OS：NBA 2K22 All Player Ratings第2页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916765-nba-2k22-all-player-ratings/page2) | 页面玩家贴`Jordan Clarkson 2K22 Player Edit`内容，有嵌入的YouTube链接`https://www.youtube.com/watch?v=RWGYk4y_i2M` | **VIDEO_LINK_LOCATED_NOT_FRAME_REVIEWED**：可后续核对版别/菜单，不能填写看见的完整UI字段或视频时间戳 |
| [OS：2021 2K22 ATD编辑报道](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/) | 编辑内容涉及Durability、Attributes、Badge、Peak及Personality；2021-12 PC名单尚处WIP | **CUSTOM_ROSTER_RESEARCH_TEXT**，非vanilla PC本局的真实数值 |
| [2K Film Room：2K22 Badge Cheat Sheet](https://2kfilmroom.com/cheat-sheets/2k22) | 可读取80项当代Badge标签文字，20/20/20/20四类分布 | **TEXTUAL_BADGE_REFERENCE**，不是MyLEAGUE PC Edit Badges原生截图，MyPLAYER解锁条件不能用于本局成长公式 |
| [2K22 PS5历史新秀Boom/Bust讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916715-jb-s-2k22-ps5-fictional-draft-classes/page6) | 一手作者说明Vitals中最低/最高潜力、Boom/Bust概率和峰值年龄 | **NEXTGEN_PLAYER_REPORTED_TEXT**，不冒充PC原版Vitals图或算法实测 |

### 下一轮最少的定向真实菜单证据（不要求立即用户操作）

1. **人物Vitals 1–2张**：在NBA2K22 PC无模组离线MyLEAGUE下，当前球员姓名/主副位置/生日/身高臂展/选秀和Peak Start/End、Boom/Bust如果有。记录`game_date`和保存版本，避免把同名历史人物当同一ID。
2. **Attributes与Durability 1–2张**：左侧分类和真正可见全部字段，尤其**耐久是否恰为16还是还有其它类别**；截图能证UI列名、不能从一次数值推演伤病概率。
3. **Skill与Personality Badges 1–2张**：徽章组、实际标签、数量和层级，区分赛季自然变化、手工编辑页、MyPLAYER构建页；同版网页清单中的名字不等于本机native badge ID。
4. **人物Development/Contract 1–2张**：`Peak`/可见潜力类设置要严格保密，**不要拍摄或上传会向普通GM/媒体泄露真实Potential的页面**。可仅由授权隔离人员做字段名/选项范围检验并遮蔽真实值。

**版权**：本轮无第三方图像复制或上传。文字研究用`SRC-0072..0082`追溯，新增机读目录`PLAYER_FIELD_AND_RIGHTS_MATRIX.json`和`PLAYER_BADGES_R04_A_REFERENCE.json`对应R04-A，PC可读菜单和完整人物Agent权限以后分R04-B/C/D逐项补齐。

## DEV29 R04-B — Player Tendencies、PlayTypes与Initiator画面研究（2026-10-21）

**本轮没有获得可认证的NBA2K22 PC原版无模组离线MyLEAGUE，完整`Edit Player → Tendencies / PlayTypes`的逐项可读菜单画面**；符合条件的**新PC22_UI_CONFIRMED=0**。不要把“找到2K22归档球员数据”错误升级为“已核对PC游戏内存或菜单帧”。本轮也没有可逐帧复核的YouTube时间戳/版权许可，没有复制或上传媒体文件。

| 候选页面/图证 | 实际完成的核对 | 对PC22目标有什么用 | 证据等级 |
|---|---|---|---|
| [2kAuction 2021-09 NBA2K22 Anthony Davis历史导出](https://2kauction.com/mynba/2k22/players/anthony-davis?roster=offseason_nba)，SRC-0083 | 搜索索引可读取`Shot`35/`Drive/Pass`43/`Defense`7/`Other tendencies`14，共99具名导出标签；可见`Touches`/TT/ISO与具体动作区分 | 丰富该版球员可选的篮球行为**名录**；不认证99个原生偏移映射 | `2K22_ARCHIVED_PLAYER_HTML_EXPORT_NOT_NATIVE_UI` |
| [2kAuction Trae Young](https://2kauction.com/mynba/2k22/players/trae-young?roster=offseason_nba)与[Tatum](https://2kauction.com/mynba/players/jayson-tatum?game=2k22&roster=current_nba)，SRC-0086/0087 | 同版归档文本明确各4个类型及`Play Initiator Yes/No`，人物状态可不同 | 确认概念独立；不能从外站标签“Three-point screens”认证本机`3 PT`的native raw | `2K22_ARCHIVED_PLAYER_TEXT_NOT_CURRENT_SAVE` |
| [OS同年具体UI文字讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/917138-nba-2k22-tendencies-a-better-realism-for-roster-creators)，SRC-0084 | 2021-11玩家明确讲`Edit Player`的`Freelance`组含`Touches`、`Shot`及下面按防守等级分的ISO条目 | 确定菜单操作的定位线索，但没有目标PC截图/完整字段顺序 | `NBA2K22_COMMUNITY_TEXT_MENU_PATH` |
| [OS ATD同年名单编辑研究](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/)，SRC-0072 | 官方社区编辑作者详述改Shot/Drive/Screen/Post/Iso/三威胁/全队Book/PlayTypes的行为 | 了解篮球动作/3D与Sim可能不同，避免以角色设定覆盖游戏原生能力 | `COMMUNITY_EDIT_REPORT_NOT_PIXEL_EVIDENCE` |

### 未来最少2组可选只读认证

**A：倾向和动作**：原版PC22`Edit Player → Tendencies`页，包含同一个球员的`Shot/Freelance/ISO`，`Driving/Dribbling/Defense/Post`页脚与当前可选值（每个截图应记录原版、球队、日期、操作入口）。尤其可帮忙查51个`UNKNOWN_RAW_BYTE`的合法名称是否对应某条菜单条目，但**即使出现相似名称也不能不做单字段对应认证**。

**B：球员战术角色**：`PlayType 1–4`有序菜单与`Play Initiator`、该队Playbook与具体12类Filter/2D Playboard；菜单截图只证明可见性和当次配置，CPU是否自动跑该战术需要独立比赛观测。

**执行边界**：本轮不是催用户截图或启动原生内存调查。未来仅在独立授权后可增量补VIS，`GM_VISIBLE_POTENTIAL_MASKED`规则继续有效。以后需解决3D vs Sim倾向实际效果，也不能仅看静态截图或已有Editor数值。

## DEV29 R04-C — 动机、人格Badge、士气与合同意愿视觉证据（2026-10-21）

**本轮原版NBA2K22 PC无模组离线MyLEAGUE的Motivations/Personality/Morale/Contract Thoughts像素完整可认证新图证：0。** 即使2K22同版第三方历史球员网页完整显示数值，也只按**同版导出字段及静态快照**认定，不伪造`PC22_NATIVE_UI_CONFIRMED`。未复制或上传任何第三方图像，本文提供原网页链接和可观察事实。

| 定位/来源 | 实际已取得的内容 | 证据等级及不能推断 |
|---|---|---|
| [2kAuction NBA2K22 Joel Embiid](https://2kauction.com/mynba/2k22/players/joel-embiid?roster=offseason_nba)、[Haliburton](https://2kauction.com/mynba/2k22/players/tyrese-haliburton?roster=offseason_nba)，SRC-0093 | 2K22档案`Motivations`完整三个标签`Loyalty / Playing for a winner / Financial security`，0–100值，可作为**文本源的准确字段证据** | `ARCHIVED_2K22_PLAYER_HTML_NOT_GAME_EDITOR_PIXELS`；没有本机偏移、当前存档真实值和PC原版菜单可读截图 |
| [OS 2K22 ATD原帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916767-nba-2k22-attention-to-detail-roster-ps4-ps5-xb1-xbsx-pc-switch)，SRC-0092/0103 | 球员人格Badge/职业偏好编辑设计，外部事件生成器的文字描述 | `COMMUNITY_CUSTOM_ROSTER_AND_EXTERNAL_EVENTS`；**不可当官方游戏自带Event Generator画面** |
| [2K20开发博客：Morale与3项自由市场Badge](https://www.operationsports.com/nba-2k20-franchise-mode-developer-blog-mygm-2-0-myleague-more/)，SRC-0091 | 官方开发解释每个机制用途、大小市场/气候/税务tie-break及士气平衡 | `OFFICIAL_OLDER_FRANCHISE_TEXT`；不是PC22场景截图或本机CPU参数 |
| [NBA2KW人格词条](https://nba2kw.com/nba-2k-finance-savvy-badge)、[Media Ringmaster](https://nba2kw.com/nba-2k-media-ringmaster-badge)、[Warm Weather Fan](https://nba2kw.com/nba-2k-warm-weather-fan-badge)，SRC-0098 | 可读取人格术语和语义，包括Finance Savvy税务偏好与Financial Security不同 | `CROSS_SERIES_BADGE_GLOSSARY`；本轮没有核对PC22人格Badge编辑菜单所有枚举和原生IDs |
| [2022 PS4 MyLEAGUE unhappy players](https://www.reddit.com/r/Nba2k22/comments/s1fuk4)，SRC-0094 | 明确PS4作者口述即便设置首发/调整士气仍有转会意愿 | `SAME_GAME_PS4_TEXT_ONLY`；不是动态Morale指标截图，更不是一份确定Bug复现实验 |

### 未来两组最小原版取证，不阻碍R04-D继续

- **A 人格与动机静态页**：NBA2K22 PC离线MyLEAGUE`Edit Player → Vitals/Motivations`真实三个标签和值域（如出现）、人格徽章列表（尤其Media Ringmaster/Warm Weather Fan/Finance Savvy及Alpha Dog）。须记录球员身份、存档日期、菜单路径和是否无模组；不要公开真实Potential或任何私有角色记忆。
- **B 职业选择动态页**：同一球员在正常已发生的赛季阶段显示其Morale/Status/Extension Thought，以及真实自由市场报价与状态，区分游戏UI上“准备测试FA”与实际已签新队；不为了制造剧情而手动调玩家合同、模拟正式存档或修改人格徽章。

新增VIS编号 **0**。PC原生偏好/真实角色目标区别、21人格徽章的来源分级与角色报价能力详见[K03/K12 §17–23](../guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、[R04-C机读目录](../catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)。待独立授权取得目标本机素材后才增量升级；本研究轮未启动DEV28/Antigravity/Codex。

## DEV29 R04-D — 跨模式Player/GM/Coach/Media互动图谱视觉证据与终结（2026-10-21）

**本轮新增经过像素完整核对的PC22无模组离线MyLEAGUE人物互动/Contract Conversation/Trade Request/公开采访原生菜单：0。** R04-D主要整合已有K03/K04/K06、项目Registry、合同/交易真实执行安全合同以及新来源的**文字证据**，不冒充外部角色协议为游戏内有此按钮。

| 来源 | 核实的是哪种研究材料 | 视觉等级与边界 |
|---|---|---|
| [2K20原开发博客MyGM关系与行动点](https://www.operationsports.com/nba-2k20-franchise-mode-developer-blog-mygm-2-0-myleague-more/)（SRC-0106） | 开发者描述MyGM 2.0的Chit Chat、Coach Gameplan信任门槛、部门任务，**同稿分开讲MyLEAGUE级别Morale/Personality Badge** | `OFFICIAL_2K20_MYGM_TEXT_NOT_PC22_MYLEAGUE_UI`；不能给本机增加不存在的对话/交易同意页 |
| [NBA2K22次世代官方MyNBA更新](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)（SRC-0108） | Conditional Coaching、MySTAFF/Prep Hub作为可借鉴的经理/教练自主行为 | `OFFICIAL_NBA2K22_NEXTGEN_MECHANISM_REFERENCE`；没有本机PC22 Conditional Coaching控件逐像素确认 |
| [NBA2K21 MyGM与MyLEAGUE实战区别](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/900689-nba-2k21-mygm-vs-myleague)（SRC-0107） | 老PC/PS4同代角色对话/信任 vs 离线沙盒权限的区别 | `OLDER_SAME_GENERATION_COMMUNITY_TEXT`，没有可认证2K22 PC原始菜单 |
| [NBA2K23次世代MyNBA模式整合说明](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/932739-mynba-can-t-sub-players-in-during-timeouts)（SRC-0109） | 玩家说明新世代把MyGM/MyLEAGUE合并、可开关RPG内容；不同作者代际叫法可能不同 | `2K23_PS5_COMMUNITY_TEXT`，不证明PC22 MyLEAGUE是同样的RPG模式 |
| [NBA2K22 MyNBA真实伤病播报/Player DNA问答](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916965-mynba-q-a-and-general-discussion-thread)（SRC-0112） | 同版玩家报告比赛播报员会对某次真实受伤给出更新；另有人询问复制DNA后新秀Years Pro错误 | `NBA2K22_NEXTGEN_PLAYER_TEXT`，提问不是证实，播报不是本机健康记录；没有逐帧验证原图 |
| [R04-D八类人物互动Atlas](../catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md) | 完整角色可观察事实、提议/拒绝/安全执行与后续世界反馈的**研究叙述** | `EXTERNAL_RESEARCH_NOT_NATIVE_PIXEL_ARTIFACT`：虚拟谈判示例不能登记为PC UI或现实事件 |

### 保留最少PC本机图证请求，不阻断下一轮R05

1. 球员合同/去留状态：真实NBA2K22 PC离线MyLEAGUE某个同一人物的合同年份、Option与FA判断、显示的Morale/role或Trade Request（若存在），必要时连续两时点记录。
2. 教练与球员真实菜单路径：Coach Gameplan/Role/Training/Player Tendencies不同入口是否原生可见；将游戏里的信息提示、提示性质和实际游戏更新区分，不把MyGM关系界面错误当MyLEAGUE内容。
3. 比赛真实伤病/公共报道：已自然发生的受伤比赛实时播报与赛后真实伤情，如果存档没有则不强行制造。只认证公开事件/位置及时间，不泄露私有健康推断。
4. 若未来真要把人格徽章/职业动机导向游戏写入：要由另行授权的原生专项对字段名、来源、原始值、负面副作用进行读前/读后认证，不能仅凭菜单截图判断算法。

**证据总结**：R04-A/B/C/D的原版PC22新增精确像素取证仍为0。本轮没有发布独立的VID/VIS截图编号，也没有复制第三方图片。**`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`**是网页研究分工的结案，不意味着本机实时玩家人格/伤病/合同模式已被完整采集或可执行。下一主题R05，未启动。

## DEV29 R05-A — 原生工资帽、合同报价和球队Business界面视觉证据（2026-10-21）

**本轮新增确认NBA2K22 PC无模组离线MyLEAGUE中完整可读的Salary Cap Table、Contract Offer、Cap Holds、Team Finances原始菜单截图：0。**

**结论：没有新合格PC22原版菜单图证**。外部2K22次世代含图论坛只算未逐像素认证的视觉线索；不能升级为本项目PC菜单确证。 本轮依据NBA官方文字、2022游戏社区文字以及本项目Native合同Profile与数据库源码进行语义整理，**未将外部新闻/论坛配图视为已核实PC22原生菜单**。

| 图片/界面证据定位 | 实际查到什么 | 版本与视觉认证 |
|---|---|---|
| [2022-04 Reddit Flat/Front/Back/Bird合同报价帖](https://www.reddit.com/r/NBA2k/comments/ucf16e) — SRC-0117 | 原贴**含两张附图链接**，2022同版MyNBA玩家回帖逐项解释合同类型、逐年薪资曲线与Bird合同限制 | `2K22_NEXTGEN_COMMUNITY_POST_HAS_IMAGES_NOT_PIXEL_INSPECTED`；图片中的精确菜单标签/按钮及游戏版本未逐像素确认，不赋合格VIS-ID、不冒充PC22 |
| [2022-04 2K22 Cap Holds / Trade Exception 帖](https://www.reddit.com/r/NBA2k/comments/u7zvde) — SRC-0119 | 同版玩家文字说旧本世代Salary Cap Table与新版MyNBA独立Cap Holds页的区别 | `SAME_GAME_COMMUNITY_UI_PATH_REPORTED_TEXT_ONLY`；作者找不到TPE按钮不代表游戏一定不支持 |
| [2021–22 PS5 Pistons MyNBA长篇赛季日记](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/918956-2k22-ps5-mynba-detroit-pistons/page4) — SRC-0126 | 2K22 PS5玩家以截图/文字记载Option、QO、放弃Hold、合同报价与双向人员的实际操作 | `SAME_GAME_NEXTGEN_PLAYER_DIARY_TEXT_REVIEWED_NOT_ORIGINAL_UI_PIXEL_REVIEWED`，文内图片未全部逐帧检视，不用其选人决定或工资代入当前档 |
| [2K官方次世代MySTAFF文章](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles) — SRC-0128 | 本世代可以复用的员工预算/岗位分工机制参考 | `OFFICIAL_NBA2K22_NEXTGEN_OFFICE_DEPARTMENT_SOURCE`，不能确认PC22全部员工菜单同名同编码 |
| [旧NBA2K Business Wiki](https://nba2k.fandom.com/wiki/Business) — SRC-0127 | 旧版Facilities/Game Pricing/Team Finances/Owner Goals分类 | `OLDER_MYGM_SERIES_CATEGORY_NOT_PC22_MYLEAGUE_MENU`；不能凭Wiki创建PC22设施原生字段 |

### 将来只读核对最值钱的三组画面

1. `NBA2K22 PC Offline MyLEAGUE / Salary Cap Table`：实际Soft Cap、Luxury Tax、硬帽/apron显示、当前工资、Cap Hold与Renounce、Trade Exception是否真的可选，记录同一Game Date与team_id；**避免只显示现实NBA参考值**。
2. `Contract Offer/Extensions/Qualifying Offers`：Flat/Front/Back/Bird菜单（若有）、实际合同年数/金额/Player/Team Option/No-trade、原生FA身份/阶段与接受/推进后的readback；与Project原生Contract 17字段逐项对应。
3. `Front Office / Financials / Business`：总薪、Payroll、Cash、Budget、Staff Budget、Fan Interest/门票定价及真实收入/支出时间范围、是否可以修改、能否存盘保留；**不以菜单显示一个数就断言签约资金真实可用**。

**本轮不请求用户立即进行截图/测试**；保留`PC22_VANILLA_UI_PROOF_PENDING`并继续R05-B交易原料研究。新合格VIS为0，来源以[SRC-0114..0128](../SOURCES.md)为准；无第三方图片上传。

## DEV29 R05-B — 交易菜单、选秀权、截止日与原生执行器视觉证据（2026-10-21）

**本轮新确证的 NBA2K22 PC无模组离线MyLEAGUE 原版 Trade Logic/Propose Trade/Stepien/选秀权保护、薪资匹配与完整交易后名单双方界面截图：0。** 已发现**同版PC玩家2022-07一手文字报告**，不是原版目标菜单逐像素核对；也没有对其它用户的游戏实施交易。**新合格VIS编号：0**，不得将`页面包含图片链接`等同`亲自读过截图文本`。

| 研究素材 | 具体得到的内容 | 是否满足目标原版PC22图证 |
|---|---|---|
| [2K22交易设置攻略](https://realsport101.com/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes) SRC-0131 | 同版攻略文字列`Trade Logic/Deadline/Financial Trade Rules/Recently Signed/Stepien/Override/CPU Offers/CPU-CPU Trades`等菜单候选 | `2K22_CROSS_GEN_GUIDE_TEXT_NOT_VANILLA_PC_MENU_CAPTURE`；原指南设置建议不是本机值 |
| [2022 PC MyLeague交易确认却不转队](https://www.reddit.com/r/NBA2k/comments/vrtew2) SRC-0132/0143 | **一手PC目标平台**报告按“YES”后两队人物不动；评论列全队控制与三方等不同解决经验 | `PC22_FIRST_HAND_TEXT_REPORT_NO_READBACK_IMAGE`；不能认定本项目交易器故障或唯一修法 |
| [2022本世代日期锁定异常](https://www.reddit.com/r/2KMyLeague/comments/sc30m8) SRC-0133 | 声称12/25仍因12/15限制不能交易，和Recently Signed开关可能有关 | `2K22_CURRENTGEN_ANECDOTE_NOT_VERIFIED_PC_SCREEN` |
| [2022 MyNBA假想多队Ben Simmons交易讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917608-nba-2k22-mynba-trade-discussion-thread) SRC-0134 | 玩家草拟三队多人/选秀权/保护条款的文字报价 | `HYPOTHETICAL_COMMUNITY_TRADE_NOT_EXECUTED_UI`；不能把三队proposal当游戏菜单已真实执行 |
| [2022 Xbox One MyGM交易成就教程](https://www.trueachievements.com/a338876/maxed-out-achievement) SRC-0142 | 同代老世代玩家叙述Trade Override/Financial Rules/Stepien等UI操作 | `SAME_GAME_OTHER_MODE_MYGM_TEXT`；不能偷换为PC22 MyLEAGUE的菜单执行能力 |
| [CBA2017历史交易规则](https://www.cbafaq.com/salarycap17.htm) SRC-0129 | 大小薪资匹配档、TPE/Stepien与15人名单等真实NBA制度 | `REAL_NBA_FINANCIAL_TEXT_NOT_GAME_MENU`；没有NBA2K22 PC经认证的真实交易工资判断截图 |
| [本机真实已批准转队技术记录](../../37_APPROVED_TRADE_EXECUTOR.md) | CHI/DET人数不一致后修复、名单与选秀权读回，用户接受某一游戏UI结果 | `PROJECT_NATIVE_OPERATION_LOG_AND_PLAYER_ACCEPTANCE_NOT_PUBLISHED_SCREENSHOT`；不可给这里新增游戏截图/跨季全部功能确认 |

### 后续可选的最少目标PC22只读取证（无需用户立即操作）

1. NBA2K22 PC MyLEAGUE **Trade Sliders完整页**，先确认每个选项实际存在、当前值、是否在重启后保留。界面需识别当前游戏模式/无mod，不能拿MyGM次世代图顶替。
2. **Propose Trade/Trade Finder/Trade Block**完整操作页，含球员/选秀权切换、可选资产年份、2队/3队输入槽、选秀权保护/交换菜单如果存在；截屏不能直接证明交易已经落地。
3. **真实工资/合法性错误、日期限制**：当一个本局真实合法的只读候选被游戏判Illegal时记录具体消息与GAME_DATE（非游戏外日期），与财政/交易规则当前实际开关对应；不能为了提供截图修改正式存档。
4. **真实交易生效后读回**：同一人物当前队、合同队、双方15人名单/2双向/13活动人数/选秀权当前持有人/财务条目，同时注明是否已保存重载。本项目已有的外部执行器已完成有限真实玩家验收，不能因此认为所有这些UI自动可观察。

**范围声明**：DEV29只研究、保存来源与设置名称，不能开启游戏、开发Agent、修改真实开关、打包“示范交易”或启动Codex/DEV28。研究结束状态`R05_B_RESEARCH_PUBLISHED_WITH_TRADE_UI_AND_CBA_GAPS`；下一轮R05-C员工/球探/选秀，未启动。


## DEV29 R05-C — 员工、球探、历史选秀菜单原版视觉审计（2026-10-21）

**本轮新增确认为NBA2K22 PC（非PS5/XSX、无MOD）、离线MyLEAGUE的8种STAFF职位、Edit Staff、Scouting Report、Lottery、Historic Draft Class的像素级菜单截图：0。** 证据来自项目自己的STAFF原生结构与真实读取器、NBA2K22次世代官方图文及原版同年代社区导入攻略。**外部页面展示了图片，不代表已逐像素核对来源平台和本机菜单顺序。新增合格PC22 VIS编号0。**

| 可取得页面与视觉线索 | 本轮有何可读证据 | 图证/平台限制 |
|---|---|---|
| [2K 官方2021 MySTAFF新闻稿](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)；[全文含Staff Carousel、Staff Card及Prep Hub图](https://nba2kw.com/nba-2k22-mynba-full-details-mystaff-training-pre-built-teams-more)，SRC-0145 | **官方次世代**四部门、完整岗位、17个可招名额和Staff Budget、可查看员工卡、球探国内/海外分工 | **NBA2K22_PS5_XBX_MYNBA_OFFICIAL_IMAGE_AND_TEXT**，可以研究功能，但**不能当PC22 vanilla MyLEAGUE确证图证** |
| [DiamondLobby：NBA2K22 Draft Class教程](https://diamondlobby.com/nba-2k22/how-to-download-a-draft-class-nba/)，SRC-0149 | 2022-04文章嵌入联盟开始/Load/Download/Scouting页面的多张配图，描述Historic/User Created/Scouted Projected OVR/D.E. Rank列 | **2K22_COMMUNITY_GUIDE_WITH_EMBEDDED_IMAGES_NOT_PLATFORM_PIXEL_CERTIFIED**，文章以MyLEAGUE/MyGM合并叙述，不能确认本机PC按钮排列 |
| [2022 2K22 Online导入选秀班Reddit](https://www.reddit.com/r/NBA2k/comments/tlv74d)，SRC-0150 | 同版用户之后通过Prospect Scouting选新人弹出的选项完成加载，最初问题由后续评论修正 | **ONLINE_MY_LEAGUE_TEXT_WORKAROUND_NOT_PC_OFFLINE_VISUAL** |
| [2020 MyLEAGUE Staff Roles讨论](https://www.reddit.com/r/NBA2k/comments/gnk1fg)，SRC-0146 | 旧版可见CFO/Assistant GM/Head Coach/Assistant Coach/Scout/Trainer的菜单文字 | **NBA2K20_COMMUNITY_NOT_SAME_GAME_PIXEL** |
| [2022 MyLEAGUE潜力字母与Edit Player评分区别](https://www.reddit.com/r/NBA2k/comments/wc2bwb)，SRC-0155 | 同版用户明确看见卡片A级潜力和Misc 25–100真实Potential两个不同显示 | **SAME_GAME_2022_FIRST_HAND_TEXT_NOT_VERIFIED_MENU_FRAME**，未来角色不得越权读取游戏真Potential |

**最少但足够有价值的定向本机画面需求，均只读且须另行批准/安排**：

1. **Staff Carousel / Staff Pool / Hire & Fire**：原版PC22离线MyLEAGUE队伍完整岗位列表、当前职位、可聘人员、Staff Salary、Years Left、Staff Budget、雇佣年限/空缺提示。检验8个Profile enum与真实UI的对应，不按PS5的17人自动补职位。
2. **Scouting / Prospect Scouting**：某届完整报表的Name/Position/Height、Scouted%、Projected OVR、Potential Grade、D.E./2K/NBA.com排序列，自动或手动侦察操作菜单及刷新时点；需要保存`source_game_date/game_save/team/selected_draft_class`，**隐藏GM不可用的游戏真Potential**。
3. **Load Draft Class / Historic Draft Class / Create/Edit**：启动时和赛季进行中可选菜单、载入后的目标届次、新秀身份/是否复制/同步人名；观察实际是否保持用户提供的历史新秀角色。
4. **Draft Lottery → Draft Result → Draft Rights**：至少同一选秀年/同一真实保存状态下，资产Year/Original Owner/Current Owner和最后选择Player的关联、Option/新秀合同是否真实自动生成；不能用现实NBA2022 Draft Board替游戏世界选秀结果。
5. **Business/Staff Budget**：查看Budget/Cash/Staff Salary及解雇/续约的输入栏和值域；含清晰的人员身份与季节。截图本身只能确证可见，不代表工资影响已完成动态因果验证。

不请求用户此刻手动截屏，不开展游戏存档写入或员工聘任测试。**当前原生未认证的不是“功能缺失”，而是缺目标PC22版本、读写接口、真实场上/选秀推进后的反馈。** 研究阶段\`R05_C_RESEARCH_PUBLISHED_WITH_STAFF_SCOUT_DRAFT_UI_GAPS\`，下一轮R05-D只做经营知识整合。

## DEV29 R05-D — 经营全域证据复核与旧三届世界规则撤销（2026-10-21）

**本轮没有取得新的、经过完整像素及平台认证的PC22原版MyLEAGUE经营菜单截图，新增合格VIS仍为0。** R05-D主要整合R05-A/B/C三轮游戏功能与项目Native源码，**不为了凑图而把PS5 MyNBA、2015 MyGM、2K19开发图或NBA真实交易网页充作本机画面**。

| 证据线索 | 可用信息 | 不能升级为 |
|---|---|---|
| [2K19官方开发博客](https://www.operationsports.com/nba-2k19-myleague-and-mygm-developer-blog/) SRC-0161 | **2K19**游戏从未来4年可交易选秀权扩到5年，是系列历史机制参考 | PC22全部未来选秀权菜单、原生7年交易能力 |
| [2022现实NBA Stepien文章](https://www.cbssports.com/nba/news/nba-trade-deadline-2022-how-complex-stepien-rule-decides-which-teams-can-and-cant-deal-first-round-picks/) SRC-0162 | 现实2021–22 CBA最长未来7年与连续首轮限制 | NBA2K22 PC原生具有7年选秀权、或用户游戏世界必须受7年上限 |
| [项目选秀权Native Profile](../../../config/draft_asset_profile.json) | 本机每32字节资产、5届共300枚的真实记录布局（精确技术内容来自仓库） | 5年必须是用户新规则的世界上限；本项目现有执行器已支持第4/5届 |
| [项目选秀权业务规则](../../../config/gameplay_policy.json) | **2026-10-21删除了外挂三届硬上限**，保留简单签、无保护/Swap、真人批准 | 已在游戏页面成功做4/5届交易，原生选项及合法日期当前UNKNOWN |

**高价值待证的原版游戏界面/动态来源（不要求本轮立刻验证）**：PC22 Salary Cap/Table+Exceptions、FA合同真实报价/签约后读回、完整交易设置及Year 4/5列表、Staff Pool/聘解约、Scouting/新秀榜单、Draft Class选择/正式选中、跨赛季财务和Draft资产变更。

**证据/工程分界**：政策`PLAYER_RULES_20261021_V4`已在GitHub直接更新，游戏Native执行器仍有三届代码路径待另行授权的Codex同步；有政策≠可执行。R05-D研究关闭于`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`，下一轮R06尚未启动。

## DEV29 R06-A — 3D实时比赛、日历Sim与Normalize菜单视觉证据（2026-10-21）

**本轮新增达到完整“NBA2K22 PC无Mod/本世代离线MyLEAGUE/可读页面标题＋菜单字段＋存档/游戏平台身份”的游戏截图：0**。真实游戏设置的文字证据比此前充实得多：**SRC-0163和SRC-0164均为明确PC22玩家的亲述/手抄设置列表**；这仍不是经游戏菜单逐像素复核的截图。**新增合格VIS ID=0**。

| 候选媒体 | 有效内容与原版本身份 | 认证结论 |
|---|---|---|
| [cdcool PC22 CPU-vs-CPU MyLEAGUE实战帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-pc-forum/918715-cdcool-nba-2k22-cpu-vs-cpu-myleague-sliders)，SRC-0163 | 明确PC版、全控30队、观看所有3D比赛而非Sim；完整文本记录Game Speed、投篮/防守/犯规等 | **PC22_CURRENTGEN_FIRSTHAND_TEXT_NOT_TARGET_MENU_PIXEL**，作者的视频演示和自定义设置不可当当前游戏默认或保存后的读回 |
| [RES2 PC默认阵容与MyLEAGUE Simulation帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders/page3)，SRC-0164 | 玩家问PC/default rosters，作者回答Yes并列Quarter/Simulation各分组选项和值 | **PC22_CURRENTGEN_PLAYER_RECORDED_MENU_LABELS**，无同批原版界面帧精确印证；本人也改动Roster Tendency |
| [DarthRambo 2021-09 PS4本世代Simulation文档](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)，SRC-0165 | 确认PS4 2K22日历模拟各组可见 | **SAME_GAME_PS4_NOT_PC_IMAGE**，取值为玩家调整 |
| [ShadyMike PC/Console NBA2K22 Slider Showcase](https://www.youtube.com/watch?v=yMGZbgeqqSM)，SRC-0166 | 视频发布页显示2K22 Gameplay、With Ball/Without Ball Movement八项及部分原生场景 | **VIDEO_DESCRIPTION_REVIEWED_FRAMES_NOT_AUTHENTICATED**；不能凭视频标题确定每帧平台或当前PC菜单 |
| [RealSport101 2K22菜单介绍](https://realsport101.com/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes)，SRC-0167 | 公开游戏Setup、Normalize Minutes/Stats、Sim Difficulty及模拟滑块的分类与作者示例 | **MIXED_MYNBA_MYLEAGUE_COMMUNITY_GUIDE**，页面若含图片未独立核实可读字段与平台 |
| [MyLEAGUE Normalize 比分异常报告](https://www.reddit.com/r/NBA2k/comments/var3vi)，SRC-0170 | 2022同版玩家提供比分从场内到日历极端变化的文字叙述 | **2022_TEXT_INCIDENT_NO_GAME_FRAME**，不能将其例子当2K22 UI原生存储或确定修复方案 |

### 独立定向PC22未来图证最小需求（不要求本轮用户拍照）

1. 原版NBA2K22 PC Offline MyLEAGUE **Setup页**：完整显示Quarter Length、Sim Quarter Length、两个Normalize、Season Length、Playoff Length、Difficulty和Game Speed，若跨页则分别截取对应标题；说明开始时间和版本。
2. **日历Simulation菜单**：Team Pace/Fast Break、Possession Results、Shot Types/Percentages、Stat Distribution、Fatigue/Recovery所有组的**可读文字/当前合法Min/Max**；每个滑块保存时是否会复位与真实Game Date。
3. **LIVE 3D USER和CPU对照页**：Offense/Defense/Attributes/Tendencies/Fouls/Movement一共7组，标清手柄受控方和当前CPU-vs-CPU观看模式，不能从“管理30队”判断用哪栏。
4. **SimCast跳入现场/退出结果**：同一真实GameID的场内比分、完场Box、Calendar记录、Normalize分钟/统计开关；只读记录不进行示例交易或擅自推动正式游戏赛程。

**重要真实技术区分**：仓库`config/state_io_native/settings.json`和`world.json`共86条注册候选；即使登记了原生RVA、偏移和默认值，**并未因此获得本轮现场菜单/内存/持久化验收**。R06-A研究状态`R06_A_RESEARCH_PUBLISHED_WITH_PC22_RUNTIME_VERIFICATION_GAPS`。R06-B历史纪元/奖项/媒体下一轮，不开发任何人物系统或执行器。

## DEV29 R06-B — 历史/奖项/媒体视觉证据边界（2026-10-21）

**新增满足目标NBA2K22 PC原版离线MyLEAGUE、完整截图/平台/存档身份认证的VIS ID = 0。** 本轮网页文字和跨平台资料足以研究栏目范围，但不能冒充本游戏本局UI画面。第三方素材只登记原来源，不二次分发未授权截图。

| 线索 | 说明 | 视觉认证状态 |
|---|---|---|
| [NBA2K22 Draft Class教程](https://diamondlobby.com/nba-2k22/how-to-download-a-draft-class-nba/) SRC-0176 | 图文教程显示建档时选秀加载流程 | `NBA2K22_GUIDE_IMAGES_NOT_TARGET_PC22_SAVE` |
| [NBA2K22 名人堂菜单玩家讨论](https://www.reddit.com/r/NBA2k/comments/wbudty) SRC-0178 | 玩家文本提及Past MVP/Rule Change/Retired Jerseys | `PC22_MENU_TEXT_ONLY_NO_PIXEL_VERIFIED` |
| [NBA2K22 MyLeague媒体文字Mod](https://www.2kspecialist.net/2021/12/nba-2k22-myleague-social-media-overhaul.html) SRC-0181 | 社交媒体/实力榜/模拟选秀文本模板的PC mod生态线索 | `MODDED_RESOURCE_NOT_UNMODDED_MENU_SCREENSHOT` |
| [2K23 官方MyNBA Eras公告](https://newsroom.2k.com/news/rewrite-nba-history-in-nbar-2k23-with-all-new-mynba-features-for-playstation-5-and-xbox-series-xs-consoles) SRC-0174 | 次世代历史时代表现及官宣开局年份 | `OFFICIAL_2K23_NEXTGEN_NOT_PC22` |

最小后续PC22只读取证：历史奖项/纪录菜单标题和切换按钮；原版社交媒体、实力榜、Mock Draft栏目；历史Draft Class当前年份与已选名单；规则变化生效前后历史页。无需立即要求玩家操作正式赛季或修改游戏。


## DEV29 R06-C — 赛季阶段与存档视觉资料审计（2026-10-21）

**新增经PC22当前本局原版完整页面与存档身份认证的VIS=0**。正文来源多为玩家文字证词、其它平台截图或后代Steam说明，未上传第三方图片。

| 资料 | 视觉认证限制 |
|---|---|
| [OS 2K22历史休赛期Save建议](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/923062-thunder-up-rebuild-in-okc-nba-2k22/page10?postcount=314) SRC-0188 | 同版话题中玩家文字建议，未看到可认证PC22全部休赛期UI菜单和存档画面 |
| [DiamondLobby 2K22启动配置](https://diamondlobby.com/nba-2k22/set-up-fantasy-draft-nba-2k22-myleague/) SRC-0189 | 同版Setup图文，未认证本游戏当前存档状态 |
| [Reddit PC Steam存盘故障](https://www.reddit.com/r/NBA2k/comments/w6rgfl) SRC-0191 | PC同版玩家文字报告，不含原版逐帧存盘数据和重载差异证据 |
| [OS PS4 2K22玩家赛程设置](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/916690-the-orlando-magic-dynasty) SRC-0199 | 同版PS4但非目标PC本局像素认证 |

以后如定向核验，应在**获玩家允许的测试档**采样季后赛结束、Lottery、Draft、FA Moratorium及下赛季开始的页标题与日期，分阶段保存并重进对比GameDate/合同/联盟历史及GameID。**仅为证据需求，不授权现在推进游戏。**


## DEV29 R06-D — 跨领域关系索引与视觉认证边界（2026-10-21）

**本轮新增原版NBA2K22 PC完整UI逐像素验收VIS = 0；新增外部SRC = 0。** R06-D为既有研究卡交叉索引，不把旧3D滑块帖/PS4/PS5截图/模组演示升级为当前存档UI、原生读数或游戏引擎因果证据。历史、纪录、合同、选秀及Save等仍按R01–R06-C视觉索引保留各自的PC22取证缺口。

详细机读逐项回链见[26关联与20项缺口](../catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)；不重复抓取第三方图片，也不要求玩家当前立即进入游戏测试。


## DEV29 R07 — 知识/可观察/可执行性总目录视觉证据边界（2026-10-21）

本轮仅静态归并R01–R06来源目录、项目已报告生产覆盖和旧VIS索引。**新PC22实机原版完整菜单视觉认证 = 0，新外部SRC = 0，新实时游戏读回 = 0。** R07对40组功能族的模式/版本适用性维持R01–R06原文；不把原有PS4/2K23截图提升为本机PC22现场证明。索引：[R07七层成熟度指南](../guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)、[40组能力与证据目录](../catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)。未来要取的原版图片与实机样本沿用旧VIS清单，需用户批准的独立测试档才能进行。
