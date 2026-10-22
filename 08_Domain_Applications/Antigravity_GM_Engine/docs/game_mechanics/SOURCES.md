# 游戏攻略、官方资料与社区证据登记

研究窗口应在此登记每轮**真正打开并核对过**的资料。来源应注明主题、适用版本/模式/平台、发布日期（如可得）、原始链接、支持的结论与限制。来源本身不是游戏内存认证。

| Source ID | 来源 | 适用游戏/版本 | 研究用途 | 证据级别 | 状态 |
|---|---|---|---|---|---|
| SRC-0001 | [DEV29 V1现有来源入口](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V1.md) | NBA2K20–23 | 前期已收集的官方、NBA2KW、OS文献索引 | PROJECT_EXISTING_REFERENCE | 下一轮需按主题核对正文 |
| SRC-0002 | [NBA 2KW — 2K23 MyNBA Settings Explained](https://nba2kw.com/nba-2k23-mynba-eras-settings-explained) | NBA2K23 / MyNBA Eras | 演示完整游戏参数表如何呈现描述、范围、可选项；不能直接当PC22参数 | COMMUNITY_GUIDE / VERSION_SPECIFIC | 导航参考 |
| SRC-0003 | [OS — Adding and removing plays from playbook](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/841395-adding-and-removing-plays-from-the-playbook) | NBA2K18及讨论适用模式 | 玩家报告Playbook容器与UI退出后修改恢复的联系；需要PC22验证 | COMMUNITY_REPORTED / OLDER_VERSION | 导航参考 |

> SRC-0002/3为当前已检查的研究案例，**不是已经完成的主题机制文档**。下一窗口发现原帖已更新/失效须更新状态。勿把初步例子无限重复复制到每张卡片；每个事实直接指向对应的source_id及必要的页内位置。

格式建议：`SRC-#### | title | URL | 20/21/22/23 | PC/PS4/PS5/Xbox | mode | authored_at | reviewed_at | supported_claims | caveats`。每轮只加有实质帮助的来源，不追求引用数量。


## DEV29 R01-A：2026-10-20 首批按主题核对的来源

以下都已读取/核对对应可访问页面内容或带原帖正文的搜索结果。不是PC22内存证据；对PC22具体菜单无直接支持的均保留“不证明”的边界。

| ID | 标题/原始网址 | 版本/平台/模式；发表时间 | 本轮真正使用的事实 | 级别 / 限制 |
|---|---|---|---|---|
| SRC-0004 | [2K官方NBA 2K22 PC英文手册](https://cdn.2kgames.com/manuals/nba2k22/PC/2KSWIN_NBA2K22_PC_Online_Manual_ENG.pdf) | 2K22 PC，官方手册2021；PDF页1–11 | 按键/临场攻防设置；目录**没有**详细MyLEAGUE统计图谱，不能据此判定其不存在 | OFFICIAL_PC22，非统计菜单来源 |
| SRC-0005 | [Operation Sports / Daily schedule in my league?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/781588-daily-schedule-in-my-league) 与 [where is league schedule](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/688998-where-is-the-league-schedule-in-myleague) | 2014–2015早期MyLEAGUE/MyGM，玩家社区 | 从Calendar操作进入Daily View看其它比赛；有玩家明示MyGM与MyLEAGUE权限未核实相同 | COMMUNITY_OLDER_VERSION，不证明PC22准确键位 |
| SRC-0006 | [Operation Sports / Thunder Up! Rebuild in OKC (NBA 2K22), page 11](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/923062-thunder-up-rebuild-in-okc-nba-2k22/page11) | 2022讨论；回帖描述 **NBA2K20**，Xbox/PS按键 | 从最近Box按Y/Triangle遍历Game1/2等旧季后赛Box；回帖人主动提示只确认2K20 | COMMUNITY_FIRST_HAND_2K20_ON_2K22_FORUM，PC22未证；页面完整打开曾受缓存影响，使用可见正文 |
| SRC-0007 | [NBA2K21 Next-Gen MyNBA Courtside Report, Dave Zdyrko开发者说明](https://devtrackers.gg/nba2k/p/8ff62bb9-nba-2k21-next-gen-mynba-courtside-report) | 2020，2K21 PS5/Xbox Series MyNBA | 官方制作人说明Daily View包括NBA/G League，支持普通sim、SimCast、SimCast Live；也明确旧MyLEAGUE与新MyNBA不同 | OFFICIAL_AUTHOR_MIRROR_NG，不能认证PC22菜单 |
| SRC-0008 | [Reddit / my league question current gen](https://www.reddit.com/r/NBA2k/comments/v8697b) | 2022-06-09，2K22本世代 MyLEAGUE | 玩家在SimCast跳入比赛后日历102:110→142:150不一致，关闭“normalize sim minutes”后表示修复 | COMMUNITY_FIRST_HAND_ANOMALY，选项精确字符串和普遍性待核 |
| SRC-0009 | [Reddit / myNBA League Leader Stats Bug](https://www.reddit.com/r/NBA2k/comments/us3tgd) | 2022-05-18，2K22线上MyNBA，平台未确证 | 赛季得分异常、Box与累计同时受影响；自述SimCast Live和36分钟标准化 | COMMUNITY_BUG_REPORT，不能外推PC离线 |
| SRC-0010 | [Basketball-Reference Glossary](https://www.basketball-reference.com/about/glossary.html) | 篮球分析标准资料，非游戏页面 | Per Game/Per36、eFG%、TS%、USG%、TOV%、Pace、估算回合等计算定义 | STAT_METHODOLOGY，非2K原生字段证明 |
| SRC-0011 | [Basketball-Reference Four Factors](https://www.basketball-reference.com/about/factors.html) | 篮球战术/四因素方法学，非游戏页面 | eFG、TOV、ORB、罚球因素及攻防两侧解释 | STAT_METHODOLOGY，权重不等于2K胜率公式 |
| SRC-0012 | [NBA.com Players Advanced Box Scores](https://www.nba.com/stats/players/boxscores-advanced) 与 [Players Advanced](https://www.nba.com/stats/players/advanced) | 现实NBA官方统计页，非NBA2K模拟 | 区分真正Advanced Box的可见字段、季/阶段/对手筛选与实际跟踪统计 | OFFICIAL_REAL_NBA_REFERENCE，**不能当作游戏内置栏目** |
| SRC-0013 | [Reddit / Are my hot zones the same in NBA and Park?](https://www.reddit.com/r/NBA2k/comments/q1eays) | 2021-10-04，2K22本世代 **MyCareer/Rec/Park** | 玩家描述从Roster/Stats看Shot Chart与Hot Zone Chart及模式切换；评论对热区继承有分歧 | COMMUNITY_CURRENT_GEN_DIFFERENT_MODE，不能证PC MyLEAGUE |
| SRC-0014 | [Reddit / Can someone explain how Hot Zone works?](https://www.reddit.com/r/NBA2k/comments/uxwomf) | 2022-05-26，2K22 **次世代MyCareer** | 原帖含两张图，玩家称热区与投篮图显示不同；评论解释存在矛盾 | COMMUNITY_NEXT_GEN_SCREENSHOT_POST，图像本体未复制且像素证据待审 |
| SRC-0015 | [Operation Sports / NBA2K22 MyLeague settings/sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders) | 2021-09~10，2K22 **PS4 MyLEAGUE**，DarthRambo等人 | Simulated Quarter Length、Team Pace、Possessions per Game、Shot Types/Percentages/Stat Distribution影响模拟统计口径；帖内值为玩家自选 | COMMUNITY_FIRST_HAND_CURRENT_GEN，PC相同性仍待核 |

### R01的采信规则

- 对玩家原帖如回复时间和模式不确定，本文注明，非官方承诺不能升级为游戏系统真相。
- **截图已知存在 ≠ 本轮已逐像素核对**。参见 `VIS-0001`，未许可图片不复制。
- `Basketball-Reference` 和 `NBA.com` 是解释篮球计算和数据粒度的参照，不是2K菜单或内存结构的证据。
- 各行的研究核查日期均为2026-10-20；一旦有PC22本机画面，优先新增独立实机证据而非覆写原跨代引文。


## DEV29 R01-B：2026-10-20 新增版本交叉证据（全部保留适用边界）

| ID | 可复核的原始来源与日期 | 游戏/平台/模式 | 核实的操作或风险 | 证据与限制 |
|---|---|---|---|---|
| SRC-0016 | [Operation Sports: NBA 2K22 Useful Findings，第7页，帖#93与#96](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page7?t=992582)，2021-09-24 | NBA2K22，OS玩家讨论；具体平台/离线模式未认证 | tcnumba10报告赛后Shot Chart可与Stats Summary比较，某些禁区外中投被算入PIP | COMMUNITY_FIRST_HAND_TEXT; **页面未提供本站可像素核对的PC22截图**，不证明内存/历史保留 |
| SRC-0017 | [Reddit: r/NBA2k 2K22 Feedback Vol.1，2021-09-10回帖](https://www.reddit.com/r/NBA2k/comments/plmeto) | NBA2K22 **PS5 MyNBA** | player stats按Triangle切换per-36；PAPG与plus/minus排序被玩家报告有问题 | COMMUNITY_DIRECT_BUG_REPORT，不能用于PC22按钮认证 |
| SRC-0018 | [Operation Sports: NBA2K16 MyGM/MyLEAGUE Thread，第33页，#485–486](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/780313-nba-2k16-mygm-myleague-thread/page33?postcount=238)，2015-10-21 | NBA2K16 MyLEAGUE；PS/Xbox按键 | 统计页按Triangle/Y切换普通、per36、advanced；问题讨论PER与Points per Possession | COMMUNITY_OLDER_MY_LEAGUE_FIRST_HAND，**不证明PC22完整字段** |
| SRC-0019 | [Reddit: How can I look at My Career stats on next gen?](https://www.reddit.com/r/NBA2k/comments/103i5j5)，2023-01-04 | NBA2K23 **MyCareer次世代** | MyCareer→Stats→League Leaders，按Y切total/per-game/per36/advanced | COMMUNITY_OTHER_MODE，不能当MyLEAGUE直接菜单 |
| SRC-0020 | [Gamepur: NBA 2K22 — How to find a player's hot zones](https://www.gamepur.com/GUIDES/NBA-2K22-HOW-TO-FIND-A-PLAYERS-HOT-ZONES)，2021–2022文章 | NBA2K22 **MyCareer/MyTeam** | MyCareer暂停→Stats→Roster→R3→RT/R2到Hot Zones；红蓝灰区域意义和MyTeam不同入口 | GAME_GUIDE_SCREENSHOT_PAGE; 图像元信息存在，但本轮未核对原图像素；**不证明PC22 MyLEAGUE Shot Chart** |
| SRC-0021 | [Operation Sports: MyLeague Viewing past Playoff Bracket?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/889354-myleague-viewing-past-playoff-bracket)，2020-02-23，Coach2K #2 | 2020年MyLEAGUE（当时2K20系列） | 旧赛季Bracket不可回看，前赛季Standings能查 | COMMUNITY_OLDER_MY_LEAGUE，**并未回答单场Box是否删除** |
| SRC-0022 | [Operation Sports: Playing MyEras — any chance to access old stats?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/954313-playing-myeras-any-chance-to-access-old-stats)，2025-03至04，帖#1–3 | 后期MyEras次世代（具体版本/平台没有可靠锁定） | 用户报告旧季详细统计访问困难，另有用户认为年分统计可看，**意见不完全一致** | CONFLICTING_LATER_VERSION_TESTIMONY，不可推成PC22一年留存 |
| SRC-0023 | [Reddit: Is there a way to view season and game records in 2k23 my career current gen?](https://www.reddit.com/r/NBA2k/comments/102td0m)，2023-02回帖 | NBA2K23 **本世代MyCareer** | Play Next Game赛程向过去滚动能打开前面比赛Box；另有玩家表示已找到 | COMMUNITY_OTHER_MODE，**跨季历史未证明** |
| SRC-0024 | [Reddit: Major Bugs of MyNBA Online](https://www.reddit.com/r/NBA2k/comments/xk44uu)，2022-09-21 | NBA2K22/23 **线上MyLEAGUE/MyNBA**多平台 | 发帖人报告部分已打比赛未保存，提及50余场未记录及截图；仅作在线模式质量风险 | COMMUNITY_UNVERIFIED_BUG_REPORT，**不等于PC22离线会丢存档** |
| SRC-0025 | [2KSpecialist: NBA 2K22 Remastered — UI overhaul](https://www.2kspecialist.net/2021/09/nba-2k22-remastered-blog-new-details.html)，2021 | NBA2K22 **PC第三方Remastered模组** | 作者公开展示修改界面并将“MyNBA”样式引入PC；说明网络截图需辨模组 | MODDED_UI_PROVENANCE_WARNING；不用于原生菜单认证 |

**R01-B 文献边界审计（2026-10-20）**：独立打开OS#485-486及2020旧Bracket讨论正文；其余以可访问的原帖/全文检索段核对。图文仅按“页面存在或发帖人声称附图”登记，**不把未逐像素看到的第三方截图当作`PC22_UI_CONFIRMED`**。第三方资料链接不等于再发布图像许可。NBA2K22 PS5≠NBA2K22 PC本世代，NBA2K23 MyCareer≠MyLEAGUE，2025 MyEras≠2021版游戏。最终仍需目标平台独立取证。


## DEV29 R01-C — 2026-10-20 版本/模式明确的新一手资料

| ID | 来源及直接定位 | 版本、时间、作者 | 支持的具体事实 | 严格限制 |
|---|---|---|---|---|
| SRC-0026 | [2K22 MyNBA官方开发团队说明：MyNBA Full Details](https://hoopsgamers.com/nba-2k22-mynba-full-details-mystaff-training-pre-built-teams-more)，§`COMPACT SPREADSHEETS`（[2K原始页面](https://nba.2k.com/courtside-report/nba-2k22-mynba)） | 2021-09-08，Visual Concepts开发团队，经NBA2KW/HoopsGamers转载；**PS5/Xbox Series MyNBA** | 官方文字列`roster, coach gameplan, box score`三类压缩表格，每屏显示行数超过此前两倍；图文页面旁有MySTAFF Roster截图 | OFFICIAL_AUTHOR_REPRINT_VERIFIED_TEXT，**不是PC/PS4 MyLEAGUE界面证明**；未取得可核验的Box本体截图；原站可能403 |
| SRC-0027 | [Operation Sports：What are some new things you want to see in 2K23 MYleague?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/920627-what-are-some-new-things-you-want-to-see-in-2k23-myleague)，2022-02-02/10，#6与#9 | NBA2K22时期玩家讨论（当前世代MyLeague与次世代MyNBA混合） | #6直接区别`Current Gen MyLeague`和`NextGen MyNBA`；#9希望将季后赛统计及单场最高放入球员卡并增强历史跟踪 | COMMUNITY_CONCURRENT_WISHLIST；**期待改进≠已验证PC22功能不存在、也≠存档无Box历史** |
| SRC-0028 | [Steam：NBA2K17 PC MyLEAGUE特殊联盟规则下场内与Box得分不一致](https://steamcommunity.com/app/385760/discussions/0/1290691308577544770/)，2017-05-26，Ray原帖 | NBA2K17 **PC MyLEAGUE** | 玩家指出“罚球自动给分”规则下，场内统计34分，赛后Box/赛季重新结算只计27分；说明一些游戏规则可能造成统计阶段不一致 | COMMUNITY_FIRST_HAND_OLDER_PC；**不是NBA2K22仍有此BUG的证据**，仅用来定义质量风险和分层来源 |

### 本轮保留而不重复计数的来源
- [SRC-0015] 2K22 PS4本世代MyLEAGUE **DarthRambo #1–#2**：再次直接核对原文中`Quarter Length`, `Simulated Quarter Length`, `Team Style Factors`, `Possession Results`, `Shot Types`, `Shot Percentages`, `Stat Distribution`栏目；11分钟和各数值是**作者个人设置**而非PC默认/游戏中的现实回合数。
- [SRC-0025] PC自定义`Remastered`新闻：继续作为排除非原版PC截图的重要警示，不能将其“MyNBA”菜单作为本项目证据。

**研究结果的阴性边界**：针对“NBA2K22 PC MyLEAGUE Game Logs/Advanced/Per36菜单截图、每场完整Box表头、赛后Shot Chart、跨年单场Box寿命”做了多组中文/英文和PC/本世代限定检索。返回大量**真实NBA联盟统计网站**、2K次世代官方图文、2K其它玩法、游戏模组或非NBA2K软件；**没有找到足以逐像素确证上述PC22原生页面的独立公开材料**。阴性搜索不等于不存在功能，不给`PC22_UI_CONFIRMED`、`PC22_NATIVE_READ_VERIFIED`或`PROJECT_CAPTURED`升级。2026-10-20只读取公开材料，没有复用/上传外部截图文件。


## DEV29 R01-D — 最后一轮有界视觉取证（2026-10-20）

**本批次只登记1项经核查、真正提升PC版本边界的新增一手文本；没有获得满足PC22原版MyLEAGUE统计表头标准的可审查截图。** 来源数不是本轮目标。

| ID | 页面 / 准确定位 | 版本、平台、模式 | 可采信的具体事实 | 证据级别与不可外推范围 |
|---|---|---|---|---|
| **SRC-0029** | [Operation Sports — RES2 2K22 All Star Current Gen Sliders，第3页，2022-01-07 #40/#41](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders/page3) | NBA2K22 **PC本世代玩家**的MyLEAGUE设置文字模板；作者首页注明主要玩`Season Mode`，MyLeague配置参考IrishSalsa | 问者询问能否用PC默认阵容；res2答“Yep - PC with default rosters”，转贴自己的MyLeague Setup/Simulation设置：Quarter Length=12、Simulated Quarter Length=11，以及Team Pace/ Possessions Per Game/Shot Types/Shot Percentages/Stat Distribution等项目 | `PC22_COMMUNITY_REPORTED_TEXT`；**不是MyLEAGUE菜单截图或Stats/Box字段认证**。作者在首帖自述实际主要玩`Season Mode`、MyLeague清单借鉴他人后修改；数值是玩家自选，不是游戏默认/用户当前设置，也不构成编辑授权 |

### R01-D公开检索范围与未采用材料（审查痕迹，不计SRC/VIS）

| 检索类别与网址 | 查核结果 | 为什么不升级PC22 UI |
|---|---|---|
| [Steam NBA2K22 Screenshots](https://steamcommunity.com/app/1644960/screenshots/) 和 [NBA2K22社区](https://steamcommunity.com/app/1644960) | 正确游戏PC平台图库，但没有获取到可可靠标记`原版+MyLEAGUE+统计字段可读`的目标屏幕。Steam的“View Stats”是游戏成就页外层UI而非MyLEAGUE中的Player Stats | 画面身份/原始菜单内容不成立 |
| [GamesKeys — 2K22 MyLeague Player/Position Lock攻略](https://gameskeys.net/how-to-use-player-lock-position-lock-in-nba-2k22/) | 包含带截图的MyLEAGUE操作攻略，目标却是`Options→Position Settings→Player Lock`等操作 | **不显示Game Logs、Box Score、Advanced或Shot Chart的已证列名**；无法凭PS按钮断定PC平台 |
| [NBA2K22 PC版已知问题Steam指南](https://steamcommunity.com/sharedfiles/filedetails/?id=2796430022) | PC专属指南，但正文聚焦其它问题 | 不含目标统计菜单截图/字段 |
| [2K22 PC Remastered来源，既有SRC-0025](https://www.2kspecialist.net/2021/09/nba-2k22-remastered-blog-new-details.html) | 非原版UI，前轮已登记 | 排除，不重复新增 |
| 带`NBA 2K22 PC/ MyLeague`标题的网络视频/图像或真实NBA Game Log表格 | 未能同时获得可辨原版PC MyLEAGUE菜单、字段和可靠视频时间戳；部分结果实际是NBA.com、MyCareer、2K23、其它游戏 | **检索标题≠已观看的游戏画面** |

**关闭结论**：R01-D未取得符合五重身份条件（NBA2K22 + PC + 原版无模组 + 离线MyLEAGUE + 可读统计字段）的新图证；记作`NO_NEW_PC22_UI_CONFIRMED`，不等于“无Box Score/无Game Logs”。已完成公开研究`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。未来新截图只增量更新当前指南§20、[VIS TODO](visuals/EXTERNAL_VISUALS.md)和[PROGRESS](PROGRESS.md)，下轮直接研究R02教练与攻防。

## DEV29 R02-A — 教练与攻防机制：2026-10-20新核对资料

以下新增的是**真正有教练/战术作用事实的来源**，并非只按游戏标题扩展检索量。URL在本轮分别打开或审看可访问的对应作者原帖/官方正文；社区数字只是个人经验，主机同代不自动成为PC22实机认证。

| ID | 原始页面与定位 | 版本/平台/模式及时间 | 本轮支持的具体事实 | 证据等级与限制 |
|---|---|---|---|---|
| **SRC-0030** | [2K官方新闻：NBA 2K22 Unveils New Gameplay Innovations](https://newsroom.2k.com/news/nbar-2k22-unveils-new-gameplay-innovations)，Defense/Shot IQ段 | 2K22官方，2021-08-31；跨平台新闻，对PC MyLEAGUE菜单无专门字段表 | 2K22官方宣布重新设计干扰投篮、封盖、防守轮转，并重视高质量出手机会 | OFFICIAL_2K22_GAMEPLAY；不认证Coach某个字段的量化效果 |
| **SRC-0031** | [OS：NBA 2K22 Useful Findings首页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)，2021-09-18 **#1、#4、#5** | 2K22同年玩家，作者比赛设备/模式并非全部可精确认证 | tcnumba10与jimbo3772对Touches、Shot Tendency、Play Discipline、教练Run Plays和Book/PlayTypes关联提出不同经验；#5发现球员类型与本队书的类型未匹配使该SF得不到合适战术 | COMMUNITY_2021_FIRST_HAND_DISCUSSION；不是官方AI公式；触球50等个人调数值不适用于项目自动建议 |
| **SRC-0032** | [OS：NBA 2K22 Useful Findings 第10页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page10)，2021-10-07 **#136–139** | 2K22玩家，未独立确定其PC/PS5/PS4 | Tynole14声称自动叫战术反复只给魔术两名后卫，改Touches没解决；另一用户观察相反/提供不同替代经验 | COMMUNITY_CONFLICTING_PLAYCALLING_REPORT；不是PC22稳定缺陷，更不构成改球员倾向授权 |
| **SRC-0033** | [Operation Sports：The Ongoing Help Defense Saga in NBA 2K22 Part 2](https://www.operationsports.com/the-ongoing-help-defense-saga-in-nba-2k22-part-2/)，Chase Becotte，2021-10-18，Help Defense Issues / On Ball vs Off Ball / Gameplan段 | 2K22同年作者亲玩/技术评论，具体PC目标/补丁版本未确证 | 弱侧协防、无球紧贴与轮转问题；暂停Gameplan有说明但某些设置效果受游戏bug/补丁影响 | ORIGINAL_EDITORIAL_GAMEPLAY_CRITIQUE；主观分析+案例，不当作所有游戏版本某按钮无效的定理 |
| **SRC-0034** | [OS：NBA on TNT 2k22 Realistic Game Play，第1页与#12–14](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918002-nba-on-tnt-2k22-realistic-game-play-for-me)，2021-10-11至20 | 作者明确 **Xbox One + Xbox Series X**；Player/Gameplan相关，主机本世代类比适用，**非PC实测** | 玩家文字说明Gameplan→Defensive Settings、Pressure、Screen、Hedge、Stay Attached、Post、Double Team；#12指出Pressure合法词是Gap/Moderate/Tight/Smother而非Go Over，#14原作者承认修正 | CURRENT_GEN_XBOX_ONE_TEXT_ANALOGUE；文中具体值是个人设定，非官方最优推荐；页面内标题Image未用作菜单画面认证 |
| **SRC-0035** | [Reddit：Best playbooks?](https://www.reddit.com/r/NBA2k/comments/r6yxow/best_playbooks/)，2021-12-02 | NBA2K22 **MyNBA次世代**帖子标记MyNBA；非PC MyLEAGUE | 一名用户因达拉斯锋线使用缺适合其角色的战术，在Book加入Cutter、Mid、3PT后反馈球队进攻更顺 | COMMUNITY_NEXT_GEN_EXPERIENCE；不能当作通用必胜配方 |
| **SRC-0036** | [OS：Questions regarding coach settings](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/862337-questions-regarding-%E2%80%98coach-settings%E2%80%99)（2018-09-10 #1–3）及[ACE Effectiveness](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/903464-ace-effectiveness)（2020-11-22 #1–8） | NBA2K19/21时代（不同作者与平台），非2K22 PC直接证明 | 玩家对于ACE/Auto Playcalling/临场默认Freelance是否自动覆盖、是否重复调用存在分歧；某人认为开ACE会在暂停后重排，另一人称ACE有助动态变化 | COMMUNITY_OLDER_VERSION_CONFLICTS；不可把旧菜单具体开关直接搬到本机 |
| **SRC-0037** | [OS：Is ACE engine Team or Coach Specific?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/814745-is-ace-engine-team-or-coach-specific)，2016-09-22 | 2K17前后；论坛保存开发者介绍/引文，非2K22官方游戏菜单 | 说明ACE设计意图包括不同阵容、对手与关键时间变化、临场动态攻击策略；“归教练还是队伍所有”原帖本身属于玩家争论 | OLDER_SERIES_DEVELOPER_TEXT_REPRODUCED；不证明2K22 PC当前运行频率/覆盖规则 |
| **SRC-0038** | [NBA2KW/HoopsGamers：2K22 Controls Guide](https://hoopsgamers.com/nba-2k22-controls-shooting-dribbling-dunking-defense-rebound-offense-guide-xbox-1-x-ps5-ps4)，2021-09-10 | 2K22 **PS4/PS5/Xbox One/Series**操作表，非PC键盘映射 | 正常比赛有On the Fly Coaching(D-pad)、Call Play(L1/LB)、防守换人、协防/包夹等手动操作 | SAME_GAME_CONSOLE_CONTROL_GUIDE；不证明GM网页能向CPU强制实时调用 |
| **SRC-0039** | [OS：NBA2K22 The Eccentric Edition Realistic NG Slider Set](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917100-nba-2k22-the-eccentric-edition-realistic-ng-slider-set)，EccentricMeat首帖2021-09-15，后续版本于12月更新 | 2K22 **次世代**个人Slider/Coach Settings，非PC MyLEAGUE | 玩家公开将PlayVision=All Plays、PlayVision Display=Full、Offense Playcalling=Auto用于观察更活跃的进攻跑位 | COMMUNITY_NEXT_GEN_USER_SETTINGS；不能把个人值域推荐当PC22默认/实战CPU自动比赛认证 |

### 本轮的内容与图源审核纪律

- 已分别打开2K官方新闻、OS原帖、OS编辑文章、HoopsGamers控制说明和Reddit的MyNBA用户回帖；Coach2K关于Isolation/P&R/Fade/Post/Cutter的旧版术语索引已被本项目12类文档引用，**当前直接URL抓取返回404**，本轮不新增编号，也不把搜索引擎摘要说成完整网页正文。
- [SRC-0034] 的作者初稿存在“Pressure=Go Over”错误，后续回帖当面改正：这是为什么按字段登记enum，比复制网红一键设置更重要。
- 原版PC22 Coach/ACE/Freelance的完整操作截图仍未取得；当前项目既有原生字典与用户游戏经验单列“项目事实”，不靠主机截图倒证。外部图像未获再分发许可，不复制到GitHub。

## DEV29 R02-B — ACE/Series/Freelance冲突、Center防守语义、PC CPU-vs-CPU及角色视角（2026-10-21）

本轮优先一手有情境的玩家操作报告；**不以同年代=同平台、或文章里有Image就等于已逐像素核对菜单**。只登记具体推进已知问题的来源，不重复R02-A范围。

| ID | 原始网页 / 作者定位 | 版本、模式、证据事实 | 不可外推的界限 |
|---|---|---|---|
| **SRC-0040** | [Operation Sports：Defensive Settings Not Staying On Custom](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/920049-defensive-settings-not-staying-on-custom)，2022-01-02/03 #1–4（smuhead/vetmin/jeebs9） | **2K22时期**：用户报告Team Focus/Defensive Settings比赛中Custom反复变Automatic，即使ACE=Off仍无法保留；其他用户首先建议ACE Off或Offense Only | `COMMUNITY_USER_REPORT_SEARCH_INDEXED_FULL_PAGE_REDIRECT_FAILED`，原网页直接打开因重定向循环失败，引用只按带原帖内容的搜索索引；没有平台/模式认证，不能说所有PC22 ACE失效 |
| **SRC-0041** | [Operation Sports：Adaptive Coaching Engine](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/921133-adaptive-coaching-engine)，2022-02-24—03-05 #1–3（DJ81） | 同版玩家提出ACE Off可能让手控设置保留，却需人工比赛中改Tempo/篮板；并主张“ACE only affects the user” | `COMMUNITY_FIRST_HAND`：对真人user情境的主张，不是NBA2K22 PC CPU-vs-CPU源代码事实，与SRC-0040分歧并列 |
| **SRC-0042** | [Operation Sports：Are series not working?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917118-are-series-not-working)，2021-09-16 #1（Smirkin Dirk） | 2K22发售早期，玩家称无论Gameplan选Series还是比赛暂停再选，场上似乎都回退Freelance | `COMMUNITY_2K22_XBX_SELF_REPORTED`，作者签名指XBX，实际模式/PC未证；只报告现象，不代表所有Series失效 |
| **SRC-0043** | [Reddit r/MyTeam：Freelance sets EASY FIX in MyTeam](https://www.reddit.com/r/MyTeam/comments/q36nsh)，2021-10-07，原作者wiiiiigs | **NBA2K22 Xbox Series X/S MyTEAM**：先暂停Offensive Settings选set，再场上方向键Gameplan→Run Freelance，然后Freelance→具体set；由此区分“选中配置”和“主动触发” | `COMMUNITY_CURRENT_2K22_NEXTGEN_MYTEAM`，不等于PC本世代MyLEAGUE的菜单或自动CPU调用 |
| **SRC-0044** | [OS：On ball screen (center), Hedge (center) 第2页 #18–23](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/806956-on-ball-screen-center-hedge-center/page2)，2016-08（harryl/Nevertheles109等） | **2K16旧系列**：普通On-Ball Screen控制盯持球人的防守者，Hedge是掩护者防守人；Center后缀可能表示有中锋参与的掩护，讨论关于“被设置的对手持球者”和“己方协防中锋”身份的区别 | `KNOWN_IN_SERIES_PLAYER_EXPLANATION`，不是NBA2K22 PC Center字段实际触发、enum、对位特殊情况和覆盖关系认证 |
| **SRC-0045** | [OS：Defensive Settings discussion 第2页，2018-11 #22–27](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/865843-defensive-settings-discussion/page2) | **NBA2K19时期经验**：球员报告Tag On Roll在Gameplan消失但SimCast Defensive Settings仍见，明说未测是否有效；另外讨论Hedge(Center)/Pre-Rotate与具体掩护/帮助 | `OLDER_SERIES_CONFLICTING_MENU_VISIBILITY`，不能说NBA2K22 PC同样隐藏或一定生效 |
| **SRC-0046** | [OS NBA 2K PC Forum：cdcool NBA 2K22 CPU vs CPU MyLeague Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-pc-forum/918715-cdcool-nba-2k22-cpu-vs-cpu-myleague-sliders)，2021-11-03 #1（2022-01更新） | 明确为**NBA2K22 PC MyLEAGUE，全联盟控制、每场看3D CPU-vs-CPU且不快模拟**；玩家公开自定义12分钟、Game Speed及打法滑块 | `PC22_COMMUNITY_DIRECT_MODE_TEXT`，可以确认有该研究条件，**不能认证Coach UI/ACE效果**；作者滑块数值非项目默认/非推荐 |
| **SRC-0047** | [OS：Next-Gen Freelance / Series / Offensive and Defensive Gameplanning Questions](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/907707-next-gen-freelance-series-offensive-and-defensive-gameplanning-questions)，2021-03-17 #1–2（skeenz/El_Tercero） | **NBA2K21次世代MyNBA**：玩家将Freelance、Series、暂停策略和Gameplan分成不同控制入口，抱怨赛前选Freelance不持久及改用Timeout的经验 | `OLDER_NEXTGEN_PLATFORM_UI_REPORT`，不证明本项目PC22本世代有同一菜单/BUG，不算目标版视频像素认证 |

**外部视觉审核结果**：寻找PC22 MyLEAGUE无模组Coach/ACE/Defense/Book、2D战术板与视频精确帧，未找到足以同时辨认平台、原版、模式与完整菜单/字段的材料；**本轮新增`PC22_UI_CONFIRMED=0`，不等于功能不存在**。有标题的YouTube视频、OS文章“Image”、Xbox MyTEAM文字教程均不冒充PC22像素认证。未复制/公开再分发第三方截图。

**R02-B主要新研究值**：把ACE是否重置、Series是否被调用、Center个人防守的“谁掩护/谁防”角色视角、SimCast旧版字段可见性和本世代PC CPU-vs-CPU玩法分别登记，构建可证伪的对象/时点/角色观测合同，而非“建议统一设置某个数值”。

## DEV29 R02-C — 原版PC22菜单的有界补证与V3研究结案（2026-10-21）

本轮只登记**1项确有新增信息的同版MyLEAGUE玩家经历**。没有为了凑来源数量登记Steam封面、重构UI Mod、2K20/21旧截图或没有目标菜单画面的攻略。

| ID | 原始链接与准确位置 | 游戏/平台/模式 | 已核对的具体新增事实 | 不能认证的内容 |
|---|---|---|---|---|
| **SRC-0048** | [Reddit r/NBA2k — Saving coaching strategy](https://www.reddit.com/r/NBA2k/comments/qg2amb)，主帖2021-10-26；2021-12-19原提问者追问后回覆 | 发帖时间属于NBA2K22发行季，原帖写MyLEAGUE；**平台不明**，没有可逐像素审查的页面 | 提问者起初不知道如何持续保存默认Freelance，每场似乎要重新设置；后续明确表示，在比赛中修改后会按**该球队**自动保存。这与另一玩家报告Series/Freelance被覆盖并不直接矛盾——两者可能涉及不同入口、游戏阶段或其他条件 | `COMMUNITY_2K22_ERA_MYLEAGUE_REPORTED_PERSISTENCE`；不能升级`PC22_UI_CONFIRMED`、`PC22_NATIVE_READ_VERIFIED`或跨赛季确定保存；不能当作ACE/CPU vs CPU原生覆盖公式 |

### R02-C检索排除和版本警告

- 定向核查NBA2K22 PC原版MyLEAGUE `Coach Gameplan / ACE / Offensive Settings / Defensive Settings / Edit Playbook / Freelance / 2D Play Diagram`，包含Steam社区截图、公开视频标题、图片检索、PS4/Xbox One同代图文。返回的2K22 MyNBA Conditional Coaching官方说明[既有SRC-0026](https://www.operationsports.com/nba-2k22-mynba-details-revealed-mystaff-staff-carousel-prep-hub-attributes-badges-more/)明确限PS5/Xbox Series，不能冒充PC22“赛中规则代理”。
- [Magic Game World：2K22 MyLEAGUE固定轮换分钟文章](https://www.magicgameworld.com/how-to-adjust-player-minutes-in-season-mode-in-nba-2k22-myleague/)显示发表2021-04-30，**在NBA2K22 2021-09-10发售前**；未提供真实PC22游戏菜单/实验，声称固定分钟能持续整季与项目用户已观察AI重新分配分钟不符。**不采信，不分配SRC-####**。
- [NBA2K22 PC SteamDB截图页](https://steamdb.info/app/1644960/screenshots/)与[Steam Community截图页](https://steamcommunity.com/app/1644960/screenshots/)可确认目标游戏容器，但主要是平台商店图像/非可识别MyLEAGUE菜单；不可把外层`View Stats`当游戏内Coach/Stats界面。
- [2K22官方MyNBA Conditional Coaching](https://www.operationsports.com/nba-2k22-mynba-details-revealed-mystaff-staff-carousel-prep-hub-attributes-badges-more/)报告让玩家在模拟时设置条件指令，这是**2K22次世代官方机制**而不是PC MyLEAGUE证据；R03可参考其中训练内容但仍不得迁移为本机字段。
- 其它版本MyLEAGUE和主机MyTEAM的菜单文章已在SRC-0030..0047登记。**本轮没有新增符合NBA2K22 + PC + 无模组 + 离线MyLEAGUE + 目标菜单字段可读五条件的画面，`NEW_PC22_UI_CONFIRMED=0`**。不意味着功能缺失；不虚构截图、字段枚举或视频时间戳。

**结案**：`R02_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`。已编写教练、GM、球员和媒体的`OBSERVABLE/ACTIONABLE/MECHANISM/OWNER`研究原料与权限矩阵于[K04 §19–21](guides/K04_COACH_AND_PLAYS.md)；PC22 UI和赛中引擎覆盖待日后定向只读证据。**下一轮R03训练、健康、自然成长；不重启R02网络搜证，不启动DEV28/Codex/游戏改动。**

## DEV29 R03-A — 训练、健康与自然成长：官方/玩家一手来源（2026-10-21）

**研究目标=为未来角色列出可观察事实、合法选择及反馈，而非提供万能高强度训练方案。** 与已有仓库PC22原生字段区别：这些外部文献解释历史机制，但**不证明本期训练字段已经有动态观测值**。下列SRC-0049..0059除注明的个别网页只可检索到正文外，均已从真实页面或可核对的原文检索定位，非单纯题名。

| ID | 原文、链接和原始日期 | 版本 / 平台 / 模式 | 真正证实或报告的内容 | 证据边界 |
|---|---|---|---|---|
| **SRC-0049** | [2K Newsroom官方新闻：2K22 Adds New Features to MyNBA](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)，2021-09-08 | **NBA2K22 PS5/Xbox Series MyNBA，仅次世代** | 新增MySTAFF、Prep Hub、团队及个人训练改进、教练条件指挥。官方附Prep Hub/Individual Training Focus/Training Schedule等具名原图入口 | OFFICIAL_NEXT_GEN_ONLY，**绝不能说PC22 MyLEAGUE原生有Prep Hub**；游戏图片版权官方 |
| **SRC-0050** | [NBA2KW：NBA 2K22 MyNBA Full Details（官方Courtside Report正文转载）](https://nba2kw.com/nba-2k22-mynba-full-details-mystaff-training-pre-built-teams-more)，2021-09 | **2K22 PS5/Xbox Series MyNBA**；同份开发者文字另在[Reddit开发博客转录](https://www.reddit.com/r/NBA2k/comments/pkc7ii) | Prep Hub显球队/对手/熟练度；团队训练未来3周的训练种类、Intensity/Fatigue/Injury Risk、Game Fitness、伤员与Load Management；玩家可自主采取较低负荷练习；个人Focus影响希望发展的方向 | OFFICIAL_DEV_TEXT_REPRODUCED_NEXTGEN；原版PC旧世代所有上述菜单和玩家“自动降训练”仍UNKNOWN |
| **SRC-0051** | [OS玩家：2k22 - MyNBA - Training schedule](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916991-2k22-mynba-training-schedule)，2021-09-13—19，coachmac75 #1/#6/#7 | 2K22 **MyNBA次世代**，作者页面签名2K22 MyNBA Pistons | 真实玩家问负荷/背靠背、练习日和Game Day冲突；推进日程后练习顺序错乱，称逐天修正是一种 workaround；帖附2段YouTube视频 | SAME_YEAR_NEXT_GEN_FIRST_HAND_TEXT；**视频未本轮逐帧检验，不虚构时间戳**，不能说PC22也有该BUG |
| **SRC-0052** | [OS开发人员Leftos：Regarding Training Intensity in MyGM and Promises](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/697404-regarding-training-intensity-in-mygm-and-promises)，2014-10-21，#1 Visual Concepts AI engineer Leftos | **NBA2K15年代MyGM**，开发人员本人解释 | `Overall Workload`由训练强度+比赛/休息天/实际出场+Work Ethic共同作用，原帖称承诺与投诉按滚动两周而不是单一强度判断，游戏日视同高强度训练日 | DEVELOPER_OLDER_VERSION_FIRST_HAND；对现代多Agent有价值的机制思路，但**两周公式/强度换算不是PC22已证规则** |
| **SRC-0053** | [OS：Schnaidt1 2K22 Sliders第31页的PS4球员帖子](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917177-schnaidt1-s-nba-2k22-next-gen-mynba-gameplay-sliders-settings/page31)，tetoleetd约2022-02-01 | **NBA2K22 PS4本世代 MyLEAGUE，ATD roster修改过进步/退化滑块**；标题含Next Gen但作者明确写PS4，需以回帖为准 | 玩家表示逐人设训练方向，多数强度High/Very High，模拟首季之后未见预期年轻人成长 | CURRENT_GEN_PS4_SELF_REPORTED_CASE_SEARCH_EXCERPT；精确回帖页面带postcount参数直接打开时403，已从可用搜索摘要阅读；不可反推训练无效，样本含多混杂设置 |
| **SRC-0054** | [OS：Advice for player development for MYGM/MyLeague](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/706081-advice-for-player-development-for-mygm-myleague)，2014-11-07，玩家回帖 | **NBA2K15时期MyGM/MyLEAGUE** | 玩家指出专练单一投篮技能时其他能力可能后退、OVR与单技能进步背离，强度高可能导致赛季疲劳加快，示范按原型培养 | OLDER_COMMUNITY_CASE；此个案不是2K22可改逐属性训练比例证据 |
| **SRC-0055** | [OS：Help with setting training in myleague](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/772729-help-with-setting-training-in-myleague)，2015-08-04起 | **NBA2K16左右旧MyLEAGUE**，非目标版 | 玩家在“injury rehab / player type / intensity”之间切换；另提问老将、中生代、新秀如何选强度、过度训练是否带伤病反效果 | OLDER_PLAYER_EXPERIENCE；并非证明PC22 InjuryRecovery准确伤愈速度 |
| **SRC-0056** | [OS：How's your MyNBA Going — 2K22 Edition](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916895-how-s-your-mynba-going-2k22-edition)，2021-09-12 #11–15，asap_lenoo、lakerhater等 | 同年**NBA2K22 MyNBA次世代**训练设置玩家讨论 | 有玩家指出与2K21旧版分配单属性训练比例不同，2K22 MyNBA仅可选训练presets，不能逐属性微调 | COMMUNITY_NEXT_GEN_MENU_REPORT；不能据此删PC22本世代任何已证训练选项 |
| **SRC-0057** | [OS：Is 2K23 MyNBA any better than 2K22?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/936550-is-2k23-mynba-non-eras-version-any-better-than-2k22)，2023-04-02 #3 dwayne12345 | **2K23次世代玩家对2K22 MyNBA日程缺陷回顾** | 该用户说2K22训练日程推进几天后排列错乱，在2K23已修复部分；与SRC-0051同期玩家叙述呼应 | LATER_COMMUNITY_RETROSPECTIVE；版本补丁不明，不能断言PC22有同BUG |
| **SRC-0058** | [OS：What do the assistant coach and trainer affect again?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/787529-what-do-the-assistant-coach-and-trainer-affect-again)，2015-11-26 #1–4 | 旧MyLEAGUE员工培训讨论（非2K22） | 玩家对训练师究竟影响预防/康复/耐久或休赛期训练营数量存在不一致理解，回帖一人称A-训练师换C-后训练营名额由7变4 | OLDER_COMMUNITY_CONFLICTING；不能给PC22 Trainer属性固定增长加成和训练营资格公式 |
| **SRC-0059** | [Reddit r/NBA2k：Understanding MyLeague Player Progression](https://www.reddit.com/r/NBA2k/comments/vvy2gu)，2022-07-10 | NBA2K22发行年度附近的MyLEAGUE社区问答，**具体玩家游戏版本和平台未自证** | 玩家提问年轻球员如何自然涨分及徽章，其他人讨论Potential/Boom-Bust/AVG及教练Mentor类徽章影响；意见非独立实验 | COMMUNITY_VERSION_UNCONFIRMED / LOWER_CONFIDENCE；只能用于标记R04需核对哪些字段，**不成为直接修改Potential或徽章的依据** |

### 本轮来源与工程验证补充

**重要项目内证据链**：`config/state_io_native/training.json`登记6个团队训练布局、5个个人flags、9种通用player_type、可见强度0–5以及fatigue/history/mentor结构候选；`src/gm_state_io/registry.py`精确注册`training.team.{home_intensity,away_intensity,automate_intensity,rest_before_b2b,rest_after_b2b,injury_recovery}`和`training.player.{position,player_type,intensity,injury_recovery,is_intensity_overriden}`。`docs/development_reviews/DEV14_TO_M3_HANDOFF.md`交付说明该11项已进通用Native state I/O，但同批当前疲劳/伤病/导师进度不等于已经可靠采到；无玩家新批准本轮**没有采集、运行或修改**。更旧`docs/research/NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md`“尚无训练接口”的描述属于当时报告，不应取代更新后Registry事实。

**阴性来源审计**：搜索中大量“Madden 22 progressive fatigue”的结果属于NFL游戏，不是NBA2K22；MC/The W使用徽章点数的玩法也**不等于MyLEAGUE自然徽章发展**。2K22次世代官方图片只登记为`NEXT_GEN_VISUAL_ONLY`，未经许可不上传第三方媒体原图。R03-A交付中文K06§0–6和未认证范围，下一轮**R03-B伤病/实时疲劳/恢复/导师与角色选择**。

## DEV29 R03-B/C — 健康事件、疲劳、导师与训练师专项证据（2026-10-21）

**来源编号 SRC-0060..0071**；下列研究优先基于2K22同年玩家及官方开发文本，次世代机制允许复用作“角色选择和风险”资料，具体PC22可读/可写字段仍单独定级。每条明确内容，不把讨论者的slider偏好当科学公式。

| 来源编号 | 可复核原始链接、年份与作者 | 真实支持的论点 | 适用范围和不能推出的结论 |
|---|---|---|---|
| SRC-0060 | [Operation Sports: MyLeague Injury Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/918980-myleague-injury-sliders), 2021-11-14 起，swanklax/Cesco/titanswin53 | 同版玩家称手打100+场无伤而Sim有伤；另玩家表示MyNBA首场Luka有真实受伤动画，反驳“3D永不伤”；讨论伤病sliders调高与不同游戏模式的反应 | NBA2K22 MYLEAGUE/MYNBA_COMMUNITY_CONFLICTING；部分PS5次世代，非PC22实机伤病概率公式 |
| SRC-0061 | [OS: MyLeague Why are there no injuries](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/921266-myleague-why-are-there-no-injuries), 2022-03-06 至04-12，Hockeytown954/vetmin/MattyIce 等 | 49场无受伤、模拟伤病多；有人见鼻骨伤，有人尝试降低Durability得到伤病，反例即使滑块开满仍未受伤 | NBA2K22同年未经控制的**冲突个案**。不能建议改球员Durability或强行生成随机伤病来补“真实性” |
| SRC-0062 | [RealSport101: NBA 2K22 Sliders](https://realsport101.com/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes), 2021/后更新 | 2K22攻略在MyLEAGUE/MyNBA环境里列出Fatigue Rate、Player Recovery Rate、CPU Injury Frequency、模式设置等候选世界层参数 | THIRD_PARTY_SERIES_SLIDER_GUIDE。编辑推荐数值是主观；平台、菜单分组和GM可调整权限须独立PC22验证，不按说明直接写World |
| SRC-0063 | [OS: MyNBA Injury Duration](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/926689-mynba-injury-duration), 2022-09-16，ripken823/dwayne12345/coachmac75 等 | 2K23 MyNBA玩家说实际康复快于最初伤期；dwayne12345明确声称2K22也有同类问题；讨论伤期/世界Duration与场次长度的混杂 | 2K23直接经验+2K22**回忆**，不可认PC22恢复天数计算或断言bug必现 |
| SRC-0064 | [2K官方MyNBA开发博客转载（OS）](https://www.operationsports.com/nba-2k22-mynba-details-revealed-mystaff-staff-carousel-prep-hub-attributes-badges-more/), 2021-09-08, Sports Medicine章 | 官方明确2K22**次世代**Team Doctor、Strength Trainer、Stamina Trainer、Sports Psych、Sports Scientist、Physio、Sleep Doctor的各自医学/体能职责 | OFFICIAL_NEXTGEN_MY_NBA，**机制与角色分工可复用**；不是PC22能聘七岗或Trainer加成公式 |
| SRC-0065 | [OS: Can MyLeague Players Earn New Badges?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/908209-can-myleague-players-earn-new-badges), 2021-04-01..05，canes21 #3/#5/#7 | 玩家称离线MyLeague训练页有Mentor，Mentor页可见目标徽章进度，并可比较前后卡片与赛季自然变化 | NBA2K21时代OFFLINE_MYLEAGUE 一手社区，不能假装PC22当前mentor进度已采 |
| SRC-0066 | [OS: Mentor System](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/904106-mentor-system), 2020-12-05..2022-01 | 2K21 current gen有人报告老将导师确实向年轻人传过徽章，另有人质疑此类机制过去版本失效 | SAME_SERIES_CURRENT_GEN_PLAYER_EXPERIENCE，不证明NBA2K22每个师徒都有效 |
| SRC-0067 | [Reddit r/NBA2k: MyLeague Player Mentorship](https://www.reddit.com/r/NBA2k/comments/rm6rr9), 2021-12-22 | 同2K22发售期玩家询问把恩比德Post Lockdown传给斯图尔特是否会扣掉导师徽章，回帖认为不会 | COMMUNITY_2K22_ERA_ANSWER；平台与真实通过结果未证，不是“必定不会消耗导师等级”的官方定律 |
| SRC-0068 | [Reddit: MyLeague Player Mentorship Broken](https://www.reddit.com/r/NBA2k/comments/s88jzz), 2022-01-20..04-08 | NBA2K22 MyLeague玩家报告为特定学员指定某导师时反复崩溃；其他人表示复现，有人说在更改前单独保存 | COMMUNITY_2K22_FIRST_HAND_FAILURE；非当前PC22定向Crash确认，亦不意味着整个系统失效 |
| SRC-0069 | [学术研究：Game Load, Fatigue, and Injury Risk in NBA](https://pmc.ncbi.nlm.nih.gov/articles/PMC6107769/), 2018 | 真实NBA观察研究发现球员个体之间负荷/疲劳与伤病风险关系存在差异，给出科学的“不同球员风险可能不同”背景 | REAL_NBA_RESEARCH_ONLY：不是游戏内部伤病概率，也不产生替游戏设置健康阈值的合法权力 |
| SRC-0070 | [Reddit: 2k22 MyLeague Online](https://www.reddit.com/r/NBA2k/comments/pmg3z0), 2021-09-11..2022-02-24 | 在线MyLeague用户先认为没有Mentoring，后来有人指出可在Overview里滚动并看到“Change Mentor” | NBA2K22 ONLINE_LEAGUE_MENU_DISCUSSION，不能从线上入口推断离线PC具体按钮 |
| SRC-0071 | [OS: Has Anyone Figured Out How Training/Progression Work?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/899504-has-anyone-figured-out-how-training-progression-work), 2020-09-03 | 玩家称模拟多个赛季、很高训练强度、A级Trainer与冠军球队，却见部分球员OVR下降；交易到其它队后个别球员又恢复 | NBA2K20/21附近一手社区报告；混杂年限、年龄、世界滑块、潜力、位置与状态，不说明PC22强度→属性数学式 |

**研究中明确否决的不可靠迁移**：
- 有人把“Trainer A”同次世代Sports Scientist、Physio、Sleep Doctor几项效果相加，缺PC本世代原生依据，不采用。
- 只看历史`progressive_fatigue_history`已存在指针就宣称可以获取球员当前体力和伤病，缺实机解码、时序与来源批次，不采用。
- 依据同年手动比赛与Sim伤病争论就修改球员Durability、手动添加伤情以制造事故，**不在DEV29研究授权内**。
- 依别的2K游戏/MyCAREER/移动版徽章成长说明将导师`badge_slot.progression`写成MyLEAGUE的已确认执行接口，不采用。

**R03-C结论**：中文K06增补§§9–15，研究范围覆盖；PC当前身体状态/医学事件实时数据仍有缺口。独立审核见`reviews/R03_COMPLETENESS_AUDIT_V1.md`，R04需等玩家完成审核。

## DEV29 R04-A — 人物身份、完整已注册属性、耐久、徽章与自然成长（2026-10-21）

下列**SRC-0072..0082**用于描述NBA2K22个人卡/Vitals、属性分组、Durability、Peak与Badge。**第三方球员站的2021年导出数值不代表本项目当前2021–22存档真实值**；2K22多平台社区编辑数据也不能替换原版，徽章解锁攻略可能特指MyPLAYER。

| ID | 精确来源 / 作者 / 日期 | 本轮用于什么真实研究事实 | 平台、版本及局限 |
|---|---|---|---|
| **SRC-0072** | [Operation Sports编辑报道：NBA 2K22 Attention to Detail Roster From CelticLG and Crew](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/)，Chase Becotte，**2021-12-16** | 2K22球员编辑维度包括Tendencies、Attributes、Badges、Durability、Personality、Play Types、Peak Start/End、Potential、Play For Win/Financial Security/Loyalty、合同、号码、身高与容貌等 | EDITORIAL_REPORT_OF_CUSTOM_ROSTER；当时报道明确PC版本still work in progress，**不能把ATD编辑值当原版PC默认** |
| **SRC-0073** | [OS官方ATD 2K22原始讨论，第11页#151等](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916767-nba-2k22-attention-to-detail-roster-ps4-ps5-xb1-xbsx-pc-switch/page11)，CelticLG及后续回复，2021-11-27至29 | 作者同年代说明其项目覆盖属性/倾向/Gameplay及Personality Badges/各部位Durability，社区回复声称约60属性、120倾向、80Gameplay和20Personality、25Durability。源码/菜单单项清单并未在帖子完整逐名提供 | PRIMARY_2K22_ROSTER_CREATOR_CLAIM；**这些数量是制作者自述，不是当前项目本机Field Registry的总数证明**，不得以25去猜其余身体字段 |
| **SRC-0074** | [2kAuction同版球员资料：Marques Johnson](https://2kauction.com/mynba/2k22/players/marques-johnson)，其页面称2K22安装快照/2021年数据 | 对一个真实样例逐栏提供Attributes/Badges/Tendencies/Animations/Bio/Development/Contract/Injuries标签，Bio含生日、身高、臂展、体重、位置/号码、选秀/年资，Development含Peak、最低/最高Potential、Boom/Average/Bust与曲线，显示16个具名Durability | THIRD_PARTY_GAME_SNAPSHOT_INDEX；**不是用户当前PC save的官方直接内存/菜单逐像素认证**，图片或站方抽取字段尚需独立核对 |
| **SRC-0075** | [2kAuction NBA2K22人物：Joel Embiid（Offseason NBA）](https://2kauction.com/mynba/2k22/players/joel-embiid?roster=offseason_nba)，2021-09基线 | 再次证实导出站分离Bio、Draft、Development、Motivations(Loyalty/Playing for a winner/Financial security)、4 PlayTypes及合同、2个伤病slot等候选结构，人物出生与归属可独立存在 | THIRD_PARTY_2K22_EXPORT；`Motivations`当前项目原生raw偏移未认证，R04-C后续调查原生效果；伤病duration不可与当前剩余天数混淆 |
| **SRC-0076** | [2kAuction NBA2K22人物：Michael Porter Jr.（Offseason）](https://2kauction.com/mynba/2k22/players/michael-porter-jr?roster=offseason_nba)，2021版数据 | 相同球员不同身体部位耐久值可以不同，Back/Misc/Hip与其它部位独立字段，构成“部位耐久≠实时伤停”示例 | THIRD_PARTY_2K22_EXPORT；任何展示的单人数字都不是当前用户存档数据 |
| **SRC-0077** | [OS：What causes Player Progression in MyLeague?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/908145-what-causes-player-progression-in-myleague)，2021-03-30至04-01，jk31/El_Tercero/marshdaddy等 | 玩家描述Edit Player→Vitals里Peak Start/End的观察位置，讨论Peak之前成长/之后退化及Potential/Progression Slider对成长的作用，**互有不同解释**；其中用户怀疑Boom/Bust属于Next Gen | NBA2K21时期MyLEAGUE系列级玩家一手经验，不能推成PC22精确年龄衰退函数或Boom/Bust有本世代原生raw |
| **SRC-0078** | [OS：JB's 2K22 (PS5) Fictional Draft Classes，第6页#78–80](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916715-jb-s-2k22-ps5-fictional-draft-classes/page6)，2022-01-29/31 | 2K22 **PS5 MyNBA**玩家明确举例Vitals中Boom/Bust机会、最低/最高潜力，以及Peak Start/End的角色；个人预测未经独立多档概率试验 | SAME_GAME_NEXT_GEN_FRANCHISE_MECHANISM；PC22本世代是否同菜单/编码，尚需认证 |
| **SRC-0079** | [NBA2KW：NBA 2K22 All-in-One Complete Badges Guide](https://nba2kw.com/nba-2k22-all-in-one-complete-badges-guide-breakdown-analysis)，2021-08-31 | 2K22游戏徽章分Finishing、Shooting、Playmaking、Defense/Rebounding四大类，常见Bronze/Silver/Gold/HOF等级，游戏技术技能辅助玩法 | COMMUNITY_SAME_GAME_MYPLAYER_GUIDE；**徽章点数获取/身高解锁条件不等于MyLEAGUE历史球员自然增长与导师规则** |
| **SRC-0080** | [OS：NBA 2K22 All Player Ratings 第2页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916765-nba-2k22-all-player-ratings/page2)，2021-09-11作者Real2KInsider及2022年内容 | 玩家同版公开列Jordan Clarkson等球员Offense/Defense/Athleticism/Mental评分与Finishing/Shooting/Playmaking/Defense徽章；后续样例将Alpha Dog、Finance Savvy、Media Ringmaster、Expressive、Extremely Confident等列为Personality | ORIGINAL_2021_2K22_PLAYER_EDIT_DISCUSSION；其中任何建议的新评分是**个人自制R2K编辑值**，不属于默认真实数据；原生徽章功能未一一测试 |
| **SRC-0081** | [NBA2K Wiki：Personality（跨版本术语）](https://nba2k.fandom.com/wiki/Personality)，当前检索可见旧系列人格徽章解释 | Alpha Dog、Low Ego、Friendly、Legendary/High Work Ethic、Unpredictable、Pat My Back、Keep It Real、Hardened、Championship DNA等可作为跨代名录候选 | WIKI_KNOWN_IN_SERIES; **网页直接展开可能受防爬限制，且历史列表不是NBA2K22 PC逐个徽章原生列表**；不把旧MyCareer阈值搬进MyLEAGUE |
| **SRC-0082** | [2K Film Room：NBA 2K22 Badge Cheat Sheet](https://2kfilmroom.com/cheat-sheets/2k22)，2KFR社区独立表 | 页面可读取完整 **80项Gameplay Badges名称**，Finishing20、Defense&Rebounding20、Playmaking20、Shooting20，可作为检索标签池；已登记于[PLAYER_BADGES_R04_A_REFERENCE.json](catalogs/PLAYER_BADGES_R04_A_REFERENCE.json) | FANSITE_2K22_MYPLAYER_BADGE_REQUIREMENTS；**列出的属性阈值及身高门槛属构建玩法，未证明本机MyLEAGUE当前各球员Badge真实native ID、自然升级公式或执行接口** |

### 本轮仓库内可证据定位（非网页SRC项）

- `config/memory_field_profile.json` 的 `fields.PLAYER` 共**72项已经命名字段：55项attributes（39个非耐久评分 +16个具体Durability），17个合同字段**，只是本项目原生已注册子集。不要误写成2K22游戏完整属性总数；具体源偏移放进矩阵，但游戏里对人的自然变化仍由原生决定。
- `src/source_extensions.py` 的 `player_details()` 返回 `birth_date`、按game_date推算`age`、`current_team_id`、`contract_team_id`、`attributes/contract`，且明确`overall_rating=None`/`overall_source=NOT_OBSERVED`；不是已经采到全部Vitals或人物Career荣誉。
- `config/state_io_native/player.json`目前含4 PlayTypes的0..15编码与48个命名Tendency offsets；Registry定义0x458..0x4BA共99字节，**51未知raw**不得给模型解释成确定倾向。此处详细内容留R04-B。
- **严格保护**：DEV15批准的公开数据库Potential=1是`MASKED_BY_GM_WORLD_RULE`，不是观察到的真实潜力；不得公开真实Potential/泄给GM或媒体；特殊`Intangibles 0x440`仅被批准用于特定经人工审批的轮换偏置，不能衍生“任意评分修改”。
- 同版2K22球员导出站显示16个具名Durability，ATD编辑作者自述25个**计数口径未证**；不构造9个不存在的名字/偏移，不把`injury_status`和`durability`合并。

**R04-A范围**：K03/K12§§0–8和两份研究矩阵均属于原料交付，R04-B接全部行为倾向及教练/Book联动，R04-C接合同偏好与人格徽章，R04-D完成角色权利与互动图谱。没有创建任何Agent、启动DEV28/Codex、打开游戏或改存档。

## DEV29 R04-B — 倾向、出手分配、3D/Sim与PlayTypes同版证据（2026-10-21）

本轮新增**SRC-0083..0090**，均只支持其能够证明的行为/界面/来源版本。**重点：2K22同版用户报告Touch与Shot不同作用且彼此冲突；不能选择合自己偏好的那个结论当2K引擎公式。** [R04-B研究目录](catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)保存99个原生slot和独立的99个同版归档导出标签；两组**没有经认证的行序/offset映射**。

| ID | 来源和定位 | 内容如何帮助研究 | 等级与边界 |
|---|---|---|---|
| **SRC-0083** | [2kAuction NBA2K22 Anthony Davis · Offseason NBA 2021/09 v91历史存档](https://2kauction.com/mynba/2k22/players/anthony-davis?roster=offseason_nba)；参照[Haliburton 同版页](https://2kauction.com/mynba/2k22/players/tyrese-haliburton?roster=offseason_nba) | 归档人物详细独立标签：`Shot`（含投篮/背身35项）、`Drive / Pass`（含三威胁、左右、连续运球、ISO vs防守等级43项）、`Defense`7项、`Other tendencies`（区域出手）14项，共**99个具名label**。可观察Shot/Tou​​ches/Post, TT/Setups、ISO四级、Play Discipline、防守7类等界面语义；均以第三方导出为研究原料 | **SAME_GAME_THIRD_PARTY_ARCHIVED_ROSTER_HTML**。网页快照值≠本项目当前球员；网页可读条目≠NBA2K22 PC原版滚动截图；**不能据“99”把label逐行对应Registry原生99字节** |
| **SRC-0084** | [Operation Sports：NBA 2K22 Tendencies — A Better Realism for Roster Creators](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/917138-nba-2k22-tendencies-a-better-realism-for-roster-creators)，Sheitan 2021-09-17 #1，Evtnj与Sheitan 2021-11-25 #9–11 | 作者尝试把3D行为倾向按经验频率/分位数分类，认为极端0或99会使人物行动单一；同月用户明确说`Edit Player→Freelance`有`Touches`和`Shot`及下方ISO防守等级。Sheitan后答`Freelance Shot`主要对应**Sim统计**而非3D，不是场上各类具体投篮动作的同义词 | **2K22_2021_COMMUNITY_DIRECT_ROSTER_DISCUSSION**；个人测试、部分作者PSN/Xbox不详，**不是PC原生effect=0的已证公式**；“避免99”是作者名单设计哲学，角色可不服从 |
| **SRC-0085** | [OS：NBA 2K22 Useful Findings](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)，2021-09 #1–7，以及[第10页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page10)，2021-10 #136–150 | tcnumba10认为全队降低Touches或主星Shot后3D出手更分散；jimbo3772认为Touches主要用于Freelance、Book/PlayTypes/POE/RunPlays决定叫谁的set；Tynole14报告把Shot调至0仍只给两后卫叫战术。**这是实质互相冲突的同版场上观察** | **COMMUNITY_2K22_FIRST_HAND_CONFLICTING**，同一游戏不同控制模式/角色/战术书/AI设置样本未控制；不得形成“Shot≤80最佳”“Touches都调50”强制规则 |
| **SRC-0086** | [2kAuction 2K22 Trae Young v91历史人物档案](https://2kauction.com/mynba/2k22/players/trae-young?roster=offseason_nba) | 将`Play Initiator=Yes`与4个**有序PlayTypes**分别列出，并有Touches/Shot等偏好；证明**字段概念独立存在于2K22归档人物展示** | THIRD_PARTY_2021_PLAYER_EXPORT；不可据外站Yes/No认定本项目当前人物，也不能反推出cpu固定控球时长 |
| **SRC-0087** | [2kAuction NBA2K22 Jayson Tatum Current NBA](https://2kauction.com/mynba/players/jayson-tatum?game=2k22&roster=current_nba)，2021-09历史导出 | `Play Initiator=No`却仍有4个PlayTypes，其中`Pick & roll wing`、`Isolation`、`Three-point screens`、`Handoff`。与Trae对比证明Initiator概念独立于4槽存在；官网字面“Three-point screens”与本机`3 PT`enum**不认定编码相同** | THIRD_PARTY_2K22_EXPORT，非当前GM名单/原生enum逐项已验 |
| **SRC-0088** | [OS：2K22 MyLeague Settings / Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)，DarthRambo 2021-09-20/21 | 同版MyLEAGUE玩家表示在测试Sim赛季时批量编辑了Foul/3PT/Midrange/Drive Pull-Up等球员倾向，并提供**Sim进球/得分/犯规**的另一组联盟世界滑块；表明原生球员倾向与世界全局权重是**两个对象** | COMMUNITY_CURRENT_GEN_PS_PLAYER_EXPERIENCE；作者按个人风格调整，并非官方“正确数值”；不得改当前世界全局Slider或人物能力 |
| **SRC-0089** | [OS：Shot Tendency](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-last-gen/471405-shot-tendency)，2012-02-18/19，beast10/youALREADYknow/RyanFitzmagic | 老版用户对总体Shot究竟影响Sim还是3D、Touches/战术类别/球星目标哪个是主要驱动有不同解释。支持“不用单一公式直接计算每场FGA” | **OLDER_SERIES_COMMUNITY_CONFLICTS**；2012不同引擎版本，不能当2K22原生准确机制 |
| **SRC-0090** | [OS：Tendency Edits That Are Game Changers for Realism? 第84页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/841295-tendency-edits-that-are-game-changers-for-realism/page84)，vannwolfhawk、daveberg、JoFri 2021-09-17至20 | Vannwolfhawk以2K22编辑者身份讨论左右突破、左右后撤步、Flashy Passing对CPU 3D动画选择的影响；同帖用户又对Shot/Shot Location影响Sim或3D提出疑问，另一些答案明确只基于2K19 | **MIXED_CONTEXT_PRIMARY_EDITOR_DISCUSSION**；2021版经验有用，内嵌2K19案例不得当2K22验证或角色统一参数模板 |

### 本轮与本地原生来源的交叉核对

`config/state_io_native/player.json`精确**48个已命名offset**，`src/gm_state_io/registry.py`将`0x458..0x4BA`共**99个1-byte PLAYER_TENDENCY槽**注册为技术`raw_range=[0,100]`，其中**51个`UNKNOWN_RAW_BYTE`只读**；四个PlayType槽是`0x168/0x169`的4×4bit/0..15，Initiator为`0x16A`一个1bit候选。**所有这些原生当前值是否已采、是否具有真实PC菜单精确名字和3D效果是独立事实**。玩家角色是否愿意改、Coach/GM是否反对、真实玩家是否批准也是独立权限，不由`writable=true`自动赋予。

**图证阴性确认**：本轮已检索2K22 PC原版Tendencies、PlayTypes、Initiator截图和Google图片，未获得具有可读滚动菜单、能明确识别原版PC和Offline MyLEAGUE的认证页面。2kAuction为**可读网页数据导出，不是Edit Player原版菜单帧**；见VIS增量。本次新增合格`PC22_UI_CONFIRMED=0`，不说明这些功能不存在。

**R04-B交付**：K03/K12新§§9–16和原生/外部两个99项目录；R04-C继续人格徽章与Loyalty/Financial Security/Play For Win、士气、合同/关系的自主选择；不启动Agent、DEV28/Codex或游戏采集/修改。

## DEV29 R04-C — 人格徽章、三类职业动机、士气、合同意愿与角色协商（2026-10-21）

新增**SRC-0091..0105**。同版玩家案例、2K20开发人员原始说明与老版受控/半受控试验的效力分开评价；外部自制Event Generator不当游戏内置能力。**角色目标和原生职业偏好是两套数据，研究不等于允许修改原始球员资料。**

| 来源 | 页面、版本与具体位置 | 可靠的机制原料 | 不可做的推断 |
|---|---|---|---|
| **SRC-0091** | [OS转载NBA2K20 MyGM/MyLEAGUE开发博客](https://www.operationsports.com/nba-2k20-franchise-mode-developer-blog-mygm-2-0-myleague-more/)，2019-07-29 `Additional MyLEAGUE-Level Features`；亦见[2KW全文转录](https://nba2kw.com/nba-2k20-mygm-myleague-mode-details-features-leaderboards-action-points-more) | **开发人员明确**：Morale/Team Chemistry各自向每日平衡点变化、工作态度差异影响Chemistry；针对顶薪竞争引入Media Ringmaster大市场、Warm Weather Fan暖气候、Finance Savvy税务的选择“辅助平局因素”，不是主导签约的绝对规则 | **官方2K20系列说明**：不能据此说2K22 PC保留完全相同数值系数/页面原生地址，或用它替代外部Player Agent的自由选择 |
| **SRC-0092** | [Operation Sports 2021-09-10 原创ATD 2K22帖子](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916767-nba-2k22-attention-to-detail-roster-ps4-ps5-xb1-xbsx-pc-switch)，CelticLG #1及第二帖 | ATD作者明确将`Play For Win / Financial Security / Loyalty`作为独立人格/合同请求编辑字段；也分开处理Personality Badges；贴文同时称外部MyNBA Event Generator 200+ scenarios | 自制名单主张并不构成默认2K22原版数值、CPU合同公式，Event Generator是社区外挂配套作品，**不是游戏内建NPC事件系统** |
| **SRC-0093** | [2kAuction：NBA2K22 Joel Embiid Offseason 2021](https://2kauction.com/mynba/2k22/players/joel-embiid?roster=offseason_nba)、[Tyrese Haliburton Offseason 2021](https://2kauction.com/mynba/2k22/players/tyrese-haliburton?roster=offseason_nba) | 真实可读同版球员数据`Motivations`分组：`Loyalty / Playing for a winner / Financial security`独立0–100评分。例如Embiid 80/15/70，Haliburton 100/50/30；均有其人物资料和合同快照 | **第三方2K22游戏归档HTML**，不是本用户当前存档，也没有真实PC22编辑菜单逐像素与native offset映射；三个数字不是比例和必须的签约决定 |
| **SRC-0094** | [Reddit r/Nba2k22：Unhappy players in MyLeague](https://www.reddit.com/r/Nba2k22/comments/s1fuk4)，2022-01-11/12，作者答使用**PS4** | 作者报告降低Morale/调整Loyalty/Play for Winner后，给予Brissett首发和队内第三进攻点仍遭遇球员想离队的局面 | **2K22_CURRENT_GEN_PS4_ANECDOTE**；一人一档未控制因果，不证明本机PC22相同bug或“调整3项完全无效” |
| **SRC-0095** | [Reddit：2K22 MyNBA Free Agency is Awful](https://www.reddit.com/r/NBA2k/comments/v2mwpq)，2022-06-01 | 同版次世代MyNBA玩家报告不同队报价/球员要价和谈判可接受程度不对称，少数80+球员长期没人签、每个FA阶段要再次寻找球员并接洽 | **2K22_NEXTGEN_PLAYER_FIRST_HAND_BUT_COMPLAINING**；用户描述不是合同AI官方公式，不足以据此设置球员贪婪/忠诚性格 |
| **SRC-0096** | [OS：Free Agent Logic in MyGM，第2页及2015-03-15 #27–30](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/754168-free-agent-logic-in-mygm/page2) | 旧版玩家分别测试三项忠诚/争冠/金钱权重组合、续约/测试FA/胜利后果，另有用户提出不同“会留”的观察 | **2K15_MyGM_COMMUNITY_SMALL_EXPERIMENT**；各种“Loyalty=99必留”“只有夺冠才接受”是个人试验报告，不能当2K22 PC规则 |
| **SRC-0097** | [OS：MyLeague Free Agency Movement](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/901133-myleague-free-agency-movement)，2020-10-02/05，El_Tercero/WeFireThoseCannons | 玩家不同试跑出现Giannis签不同球队，回复认为Money/Role/3 Motives与Media/Weather/Tax可能影响去留，但最终结果带随机感 | **2K21时期本世代系列经验**；逻辑复杂性和未知必须保留，不证明精确合同概率 |
| **SRC-0098** | [NBA2KW人格词条：Media Ringmaster](https://nba2kw.com/nba-2k-media-ringmaster-badge)、[Warm Weather Fan](https://nba2kw.com/nba-2k-warm-weather-fan-badge)、[Finance Savvy](https://nba2kw.com/nba-2k-finance-savvy-badge)、[Alpha Dog](https://nba2kw.com/nba-2k-alpha-dog-badge)、[Friendly](https://nba2kw.com/nba-2k-friendly-badge)、[Unpredictable](https://nba2kw.com/nba-2k-unpredictable-badge)、[Legendary Work Ethic](https://nba2kw.com/nba-2k-legendary-work-ethic-badge) | 为这些独立人格徽章提供可读英文/通用语义，例如Friendly外向、Unpredictable行为难预期、传奇训练态度极高；前3项有SRC-0091开发说明作机制支撑 | 多词条混合MyPLAYER/旧版本释义；Alpha Dog旧版场上临时+属性的说明**绝不是PC22已认证效应**；21人名录中的其它项目还需认证native id与版本归属 |
| **SRC-0099** | [OS：Personality Badges in MyLeague/MyGM](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/827405-personality-badges-in-myleague-mygm)，2017-03-11 | 真实玩家问All Time Great、Legendary Work Ethic究竟会不会影响成长/受伤/合同，显示**社区本身不清楚单项机制** | **OLDER_COMMUNITY_QUESTION_ONLY**；问题不是已证“可以Very High练且不会受伤”的答案 |
| **SRC-0100** | [OS：MyLeague impressions? 2K20，第7–8页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/881906-myleague-impressions-2k20/page7)，2019-09玩家 | 玩家解释`Player Morale`与`Team Chemistry`不同；上场时间、赢球、角色和联盟动态与球员拒绝续约有关；有人报告名单箭头显示士气和伤病等综合状态变化 | 同版**2K20**论坛玩家观测，非PC22单场原生字段映射；不能用一条评分箭头倒推出Ability被永久改写 |
| **SRC-0101** | [Reddit r/2KMyLeague：The same glitches are bothering me year after year](https://www.reddit.com/r/2KMyLeague/comments/sqfmqh)，2022-02-12 | 2K22玩家称受限球员签多年合同后被一年QO替代，无法确认某些市场条款持久正确，影响对“已经签约”的理解 | SAME_GAME_PLAYER_REPORTED_FREE_AGENCY_BUG；不认定所有平台/每次都会发生，R05再研究RFA/签约流程 |
| **SRC-0102** | [OS：PLAYER LOYALTY - FINANCIAL IMPORTANCE - PLAY FOR WINNER](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/871898-player-loyalty-financial-importance-play-for-winner)，2019-03-14问题 | 作者询问三种偏好是否会**随赛季/转会/赢球/工资变化而自动更新**，论坛未给出可验证结论 | **UNANSWERED_OLDER_SERIES_QUESTION**；R04-C标三项native跨季动态机制UNKNOWN，不应擅自动调整 |
| **SRC-0103** | [ATD社区2021-09主帖第二段说明外部MyNBA Event Generator](https://forums.operationsports.com/forums/nba-2k-basketball-rosters/992144-nba-2k22-attention-detail-roster-ps4-ps5-xb1-xbsx-pc-switch.html) | 作者自建约200–250个随机/人物事件场景，允许使用社区编辑的人格徽章筛选活动 | **EXTERNAL_COMMUNITY_EVENT_TOOL**，不是原生NBA2K22/PC/PS5自动剧情引擎；不能由此推断“NBA2K22自带200个事件” |
| **SRC-0104** | [NBA2K22 MyNBA官方开发细节转述：MySTAFF Sports Psych](https://www.operationsports.com/nba-2k22-mynba-details-revealed-mystaff-staff-carousel-prep-hub-attributes-badges-more/)，2021-09-08 | 2K22**次世代**官方称Sports Psych影响Morale/Team Chemistry；若弱可能出现负反馈循环 | **OFFICIAL_NEXTGEN_ROLE_MECHANISM_REFERENCE**，不证明PC本世代能雇用完全同名岗位或已读此属性 |
| **SRC-0105** | [NBA2K Wiki：MyGM Front Office / Review Player Roles](https://nba2k.fandom.com/wiki/Front_Office) | 老MyGM资料列Star/Starter/Sixth Man/Role Player/Bench Warmer/Prospect等角色，并认为角色影响士气与续约、合同谈判涵盖薪资、年限、球员/球队Option和No-trade | **OLDER_MyGM_MODE_DOCUMENTATION**，不是2K22 PC原版MyLEAGUE菜单或新增Agent谈判接口的证明 |

**新研究原料与工程边界**：
- 完整独立目录[`R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json`](catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)：三项0–100动机、21个来源分级的人格候选（原R04-A 20项加Warm Weather Fan）、四类情绪/角色/谈判状态、六类可提出/拒绝的角色选择。全部`native_offset=null`和当前真实人物数值`null`，不虚构PC22可写。
- NBA2K22 Archived Motivation的**三个数值不要求合计100**；`Finance Savvy`是环境税务偏好，和`Financial Security`收入保障偏好**两个不同实体**。
- 玩家与GM各自的外部思想、决议、合同承诺必须独立于原生游戏的字段读值；普通游戏操作不允许改Ability、Potential、Badge、Durability；交易/合同仍需原生合法条件、当事角色权利与真人玩家批准。
- 现有`config/memory_field_profile.json`确有17项已注册合同字段，但是没有本轮可核对的三项Motivation原生具名偏移；**字段存在于网页归档不代表现行存档已捕获值，也不代表能直接写**。

**R04-C状态**：`R04_C_RESEARCH_PUBLISHED_WITH_NATIVE_MOTIVATION_GAPS`，下一轮`R04_D_PLAYER_AGENT_DUAL_SEMANTICS_AND_INTERACTION_ATLAS`；独立审核由其它模型负责，本研究窗口不主动审核、不开发Agent，不启动DEV28/Codex或修改游戏。

## DEV29 R04-D — Player/GM/Coach/Media交互原料、模式分界与真实合同和权限（2026-10-21）

以下SRC-0106..0113为**新查阅角度及跨平台取证补充**；旧来源如SRC-0091、0093仍适用并交叉引用。特别注意`2K20 MyGM 2.0≠PC22 Offline MyLEAGUE`，`Real NBA CBA≠2K22 simulation executor`，`2K22次世代MyNBA≠本机菜单截图`。

| Source | 原文链接与时间 | 能提供给角色的研究事实 | 不得迁移的结论 |
|---|---|---|---|
| **SRC-0106** | [Operation Sports：NBA2K20 Franchise Mode Developer Blog](https://www.operationsports.com/nba-2k20-franchise-mode-developer-blog-mygm-2-0-myleague-more/)，2019-07-29，原开发团队主稿的**MyGM 2.0 – Action Points / Revamped Relationships / Goals and Tasks** | 开发团队明确谈到MyGM的行动点、日常`chit chat`、玩家/员工/对手GM信任、球员/教练提目标、完成任务会改变关系；教练Gameplan菜单访问可被信任限制。适合作为**多角色关系、请求/拒绝与时间资源**的系列参考 | **2K20_MYGM_ONLY_RELATIONSHIP_AND_AP**，不能说NBA2K22 **PC离线MyLEAGUE已经自带**这些对话、角色Agent和菜单解锁API。同稿“Additional MyLEAGUE-Level Features”里的Morale/Chemistry和FA Badge属于另一范围，见SRC-0091 |
| **SRC-0107** | [OS：NBA2K21 MyGM vs MyLeague](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/900689-nba-2k21-mygm-vs-myleague)，2020-09-24—10-01；K_rob11/jk31/CujoMatty等 | 同年代玩家明确区分**PC/PS4本世代MyGM的关系/Coach信任**和**MyLEAGUE沙盒**；一个PC玩家通过MyGM谈话获得Coach轮换/叫战术权限，另有玩家只玩MyLEAGUE以保全联盟编辑自由 | 仅跨代对模式边界的用户证据，**不是PC22 MyLEAGUE信任API已证**；作者在PC MyGM提到使用第三方工具，不是原生本游戏接口 |
| **SRC-0108** | [2K Newsroom NBA2K22 Adds New Features to MyNBA](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)，2021-09-08 | 同版官方明确**PS5/Xbox Series MyNBA**有Conditional Coaching（在模拟时符合条件自动替换用人）、MySTAFF、Prep Hub和训练反馈，提供教练自主选择/疲劳管理的经营机制类原料 | OFFICIAL_NBA2K22_NEXT_GEN_ONLY；本项目PC旧世代**没有认证完整Conditional Coaching native原生菜单和动作合同**，不得用新代新闻给原生字段/读值作证 |
| **SRC-0109** | [OS：MyNBA Can't sub players in during timeouts?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/932739-mynba-can-t-sub-players-in-during-timeouts)，2022-10-27—11-04，jyod21与jk31 #9–12 | 2K23 PS5同代MyNBA玩家明确说新世代MyNBA把MyLEAGUE/MyGM合并，RPG内容可切换，而本世代仍有分离的MyGM与MyLEAGUE；信任可能影响轮换页面 | **2K23_NEXTGEN_COMMUNITY_EXPLANATION**，并非直接2K22 PC菜单取证；作者的“current/last gen”术语必须转成平台和年份 |
| **SRC-0110** | [NBA.com 2021 Free Agency: Options and Qualifying Offers](https://www.nba.com/news/2021-free-agency-options-and-qualifying-offers)，John Schuhmann，2021-08-02 | 2021现实联盟球员Option行权/拒绝、QO与受限自由球员的实例和时序，帮助区分**可讨论的真实职业选项**与报价接受 | **REAL_NBA_2021_CBA_CONTEXT**，不是2K22游戏CPU合同接受概率、原生写入API或每个本游戏历史选秀球员的有效合同 |
| **SRC-0111** | [Reddit r/NBA2k：2k21 MyLeague Player Morale "Usage?"](https://www.reddit.com/r/NBA2k/comments/m2yrn7)，2021-03-11 | PS4等平台未明确的同代MyLEAGUE玩家描述Tony Allen已获29分钟但仍抱怨“usage in recent games”，回复认为渴望更多出手；说明**分钟与球权是不同协商概念** | NBA2K21系列玩家个案，**不证明2K22 PC个体士气有确定“多投5次便满意”公式** |
| **SRC-0112** | [OS：NBA2K22 MyNBA Q&A & General Discussion](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916965-mynba-q-a-and-general-discussion-thread)，2021-09-13起 | 2K22次世代玩家问复制Player DNA到新秀后Years Pro/年龄身份可能错位，一位玩家称赛中伤情有新动画、播报员晚些提供消息；另外人问Morale是否真影响续约 | SAME_GAME_NEXT_GEN_COMMUNITY_DIRECT_OBSERVATION与问题分开：**发问并不证明Morale续约因果，播报内容不是本机PC真实伤病数据**。可为R04-D公共新闻/私有健康/新秀身份消歧提供案例 |
| **SRC-0113** | [OS：MyLeague Online Discussion，第11页开发者Leftos历史回复转引](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/774019-myleague-online-discussion-great-dev-post-kickoff/page11)，约2015，本轮搜索索引引用原Leftos回答 | 旧版**ONLINE** MyLEAGUE的CPU交易可提交仲裁、管理员配置是否需要最后批准，体现**联盟管理员审批**可与AI交易接受分开 | OLDER_GAME_ONLINE_ADMIN_SERVER_MECHANISM，**不是**本项目本世代Offline MyLEAGUE内置server arbitration；当前项目玩家批准是外挂安全业务规则，不能当游戏自带在线Admin Approval。原页面本轮直接打开时缓存失败，因此严格只凭搜索返回的历史引用，不作进一步原文断言 |

### 新研究产物的来源与权限入口

- **[Player⇄GM⇄Coach⇄Media八例交互图谱](catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)**：八种谈判/拒绝/失败场景的事实级别、可选行动、隐私/公开边界及原生交易/签约/训练/战术衔接；**不是执行Agent或真实球员已说过的话**。
- **[109行球员字段双语义侧表](catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)**：基于已发布的[109个字段/候选主目录](catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)按字段保存`native_semantic, mechanism_grade, current_value_status, identity_requirements, role_rights, external_role_semantic, overwrite_risk`；所列数值不是实际新读取的游戏数据。
- **本项目工程来源**：[批准交易](../37_APPROVED_TRADE_EXECUTOR.md)有身份/资产/计划/审批/读回边界；[批准签约源码](../38_APPROVED_SIGNING_EXECUTION.md)明确`approved_signing_v1_unvalidated`且默认禁止真实写入；[早期FA竞价计划](../development_tasks/DEV_20261017_04_OFFSEASON_FREE_AGENCY_V1.md)使用固定权重选择的旧工程思路，不自动符合V3人物自由拒绝目标；[世界线原则](../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)允许历史重力特例但**每次须用户额外批准**，普通改Ability/Potential/Badge禁止。
- **终态研究结论**：R04-A/B/C/D研究完成`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`，合法行动与角色自主原料已经分层；本项目游戏实时Morale/三Motivations Native Offset/51 UNKNOWN字节、完整人格Badge ID、单次签约真实回读等仍未证。不因缺像素就无限重复网络取证，也不伪称系统已完成部署。**下一轮R05市场财务（NOT_STARTED）由用户再次触发**；DEV29不做独立审核、不启动DEV28/Codex/Agent、不修改存档。

## DEV29 R05-A — 工资帽、合同类型、Bird/RFA、Cap Holds与球队经营资金（2026-10-21）

本轮登记**SRC-0114..0128**。权威层级严格分开：**现实2021/22 NBA正式劳资公告**、**2K22同版游戏菜单/玩家经历**、**其它版本或模式的假说**、**本项目有原生Profile但当前状态未认证**。若阅读的是2017版CBA或当前可能已经更新的NBA通用网页，只取与原研究年份一致且可核对的定义，不直接复制2026年的新版劳资条款进2K22。

| ID | 原始研究来源及时间 | 本轮可获得的有效信息 | 真实限制 |
|---|---|---|---|
| **SRC-0114** | [NBA Communications官方：NBA Salary Cap for 2021-22 Season](https://pr.nba.com/nba-salary-cap-for-2021-22-season-set-at-112-414-million/)，2021-08-02 | 官方确认2021–22 Salary Cap **112,414,000**、Tax **136,606,000**、Minimum Salary **101.173m**、Mid-Level非税9.536m/纳税5.890m/Room4.910m；当年签约暂停期确切真实日期 | **REAL_NBA_2021_PRIMARY**，不是NBA2K22当前或以后年份游戏规则与税款结算；真实新闻未列apron数字 |
| **SRC-0115** | [SalarySwish历史工资帽表](https://www.salaryswish.com/salary-cap)，2021–22历史行 | 列当年apron **143,002,000**、tax/cap与官方相吻合、2022–23薪资基准 | **REAL_CBA_SECONDARY_ARCHIVE**；apron非本轮官方公告直接值；不能假定游戏本年同值 |
| **SRC-0116** | [NBA Communications官方：NBA Salary Cap 2022-23](https://pr.nba.com/nba-salary-cap-2022-23-season/)，2022-06-30 | 现实下季Salary Cap **123,655,000**、Tax **150,267,000**、non-taxpayer MLE **10.490m**、taxpayer **6.479m**、room **5.401m**；说明不能把2021工资帽永久沿用 | **REAL_NBA_2022_PRIMARY**；当前2K22游戏以后赛季是否按现实2022线上调整必须看存档，不直接作为本模拟下一季硬数据 |
| **SRC-0117** | [Reddit r/NBA2k：What do flat, front, back and bird contract “types” do?](https://www.reddit.com/r/NBA2k/comments/ucf16e)，2022-04-26，MyNBA原帖带两幅界面图，回帖票数高 | 2K22同年玩家对**Flat**每年等额、**Front**逐年减约5%、**Back**逐年涨约5%、**Bird**合格续约涨约8%的界面玩法解释；玩家偏爱程度只有社区口述 | **NBA2K22_NEXTGEN_MYNBA_COMMUNITY_UI_AND_TEXT**；不能认本机PC22每一项均同名或像素已验；`Bird contract curve`不等于本地PLAYER`contract_type`枚举 |
| **SRC-0118** | [Operation Sports：Bird exception and RFA issue ?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/912417-bird-exception-and-rfa-issue)，2021-07至08 | 玩家反映Moratorium为本队RFA提供5年合同，推进后变单年Qualifying Offer，提到Cap Hold/RFA Offer Sheet导致空间占用，评论有人尝试错峰出价 | **PRE_NBA2K22_RELEASE_OLDER_VERSION_PLAYER_CASE**：不能因为作者后来签名“2K22 MyNBA”认发帖时使用2K22，不能说本目标PC已复现 |
| **SRC-0119** | [Reddit r/NBA2k：2K22 next-gen renounce trade exceptions?](https://www.reddit.com/r/NBA2k/comments/u7zvde)，2022-04-20 | 明确同版玩家说**旧本世代MyLEAGUE Salary Cap Table可以放弃Cap Hold**，次世代MyNBA迁移至独立Cap Holds页，但他找不到Trade Exceptions放弃按钮 | **NBA2K22_CROSS_GEN_MENU_PATH_REPORT**；作者个人找不到按钮不证明次世代没有功能，PC22菜单应另证 |
| **SRC-0120** | [NBA官方：Free Agency Explained](https://www.nba.com/news/free-agency-explained)，当前NBA通用释义页，采用1976–2017/2021已有机制定义时需独立核验年份 | UFA/RFA、QO、Bird/Early Bird/Non-Bird、Offer Sheet、Player/Team Option、Cap Exceptions和Moratorium概念 | **NBA_REAL_CBA_EXPLANATION_MAY_HAVE_NEWER_RULE_UPDATES**；2026版本的具体年份、例外金额/截止日/Second Apron不能自动用于2021的2K22引擎 |
| **SRC-0121** | [NBA官方：2022 Free Agency Options and Qualifying Offers](https://www.nba.com/news/2022-free-agency-options-and-qualifying-offers)，2022-06至08更新 | 真实2022年Player Options（如Kyrie/Westbrook）、Team Options、QO/RFA产生条件和真实样例 | **REAL_NBA_2022_PLAYERS_CONTEXT**，不说明本用户经过1984历史新秀轮回后的模拟人物有相同选项 |
| **SRC-0122** | [Reddit r/2KMyLeague：The same glitches are bothering me year after year](https://www.reddit.com/r/2KMyLeague/comments/sqfmqh)，2022-02-12，原帖明确自述已购**2K22 MyLEAGUE** | 真实同版用户称长年合同被单年QO覆盖、未选择QO也可能自动出现、相关cap space受影响；同年另一用户建议调交易频率/手动审核 | **NBA2K22_2022_CURRENT_GEN_OR_UNKNOWN_PLATFORM_PLAYER_FIRST_HAND**：样本未控制、bug未经本机复现。尤其不能无批准直接编辑合同绕过 |
| **SRC-0123** | [Reddit r/NBA2k：Why after all these years can't we do sign-and-trade?](https://www.reddit.com/r/NBA2k/comments/14rao0h)，2023-07-05 | 玩家继续报告RFA自动变一年QO和Bird Rights拒绝超帽续约，质疑sign-and-trade支持范围 | **NBA2K23_NEARBY_SERIES_COMMUNITY_REPORT**，有人说2K23的交易功能不足只是用户看法，不证明2K22目标版没有签换 |
| **SRC-0124** | [Reddit r/NBA2k：Newbie question but how does salary cap work?](https://www.reddit.com/r/NBA2k/comments/spsa80)，2022-02-11 | 玩家面对负`cap room`/`luxury tax room`不知能否签任何球员，回复区分MLE、Bird和一般签约 | **NBA2K22_2022_PLAYER_QA**；回答较粗略，不是该版精准例外及硬帽资格表 |
| **SRC-0125** | [Reddit r/NBA2k：Should I sign Bird free agents first or last?](https://www.reddit.com/r/NBA2k/comments/oxlvb6)，2021-08-04 | 系列玩家确认BirdFA签约先后及Moratorium多报价，说明同样现金/空间按先后可以产生不同合同机会 | **NBA2K21_2021_PRE_2K22_SERIES_COMMUNITY**；不能认同年2K22已经发布，或把用户“可给3次报价/天”当官方游戏硬规则 |
| **SRC-0126** | [Operation Sports：2k22 (PS5) MyNBA Detroit Pistons，多页真实逐赛季叙述](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/918956-2k22-ps5-mynba-detroit-pistons/page4)，2021-11至2022-01 | 同版PS5作者实战展示球队Option/QO、Renounce Cap Holds、签约RFA对手能否匹配、签2Way和阵容形成，包含游戏内具体薪资与选秀权背景 | **NBA2K22_NEXTGEN_PLAYER_REPORTED_DIARY**；作者的剧情/队伍选择及外站截图不等于本局已发生；个别球员数字不可导入项目 |
| **SRC-0127** | [NBA2K Wiki旧版Business功能条目](https://nba2k.fandom.com/wiki/Business) | 旧模式中设施、票价、商品/餐饮/停车、球队收入支出、老板目标、球衣销售等经营资料类别 | **SERIES_OLDER_MODE_WIKI**：尤其`Owner Goals/Facilities`偏MyGM，不能认NBA2K22 PC离线MyLEAGUE能够操作这些完整菜单 |
| **SRC-0128** | [2K Newsroom官方：NBA2K22 MyNBA / MySTAFF功能](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)，2021-09-08 | 同版次世代明确引入Front Office/Coaching/Scouting/Sports Medicine四部门与受Staff Budget限制的可雇人员；作为**经营员工成本与分工**的游戏机制原料 | **OFFICIAL_NBA2K22_NEXTGEN_ONLY_UI**；本世代PC是否拥有同一员工部门/全部岗位/17职位上限未知，R05-C研究 |

### R05-A项目内源码与知识事实（不计互联网SRC）

- `config/memory_field_profile.json`中17个球员Contract原生字段：6薪资槽低31位、年限/选项/延期/no-trade/Bird/TwoWay/EuroStash等；`STAFF.salary`位域24bit/`+0xF8`。内容在[K07/K08/K09攻略](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)及[机读目录](catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json)，**不是当前存档全部合法合约对象已认证**。
- `docs/development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md`曾只读检查某批30队466人、`market_free_agents=0 rows`、选项/年限跨季滚动和真实FA尚待证；`current_team+0x60`与`contract_team+0xA8`不能仅凭一端更改认定已签约。
- `config/source_catalog.json`保留`P0_PARTIAL_REAL_GAME_NOT_VERIFIED`、`cash signed hypothesis unverified`；`src/gm_core/finance.py`已明示`salary_cap_minus_payroll_proxy`不是真实cap space；`docs/GM_FINANCE_WORKBENCH.md`只有独立静态三年/最多六年情景，`signing_capacity=UNKNOWN`；`docs/38_APPROVED_SIGNING_EXECUTION.md`还没完成真实签约验收，两个写入闸门关闭。
- 原生市场可选项词表可以研究，但**DEV29不开发自由市场竞价算法、固定意愿规则、Coach/Player人格或执行器**。研究完成不代表能够更改上述原始字节；用户具体授权与游戏读回永远分开。

**阶段**：`R05_A_RESEARCH_PUBLISHED_WITH_FINANCE_EXECUTION_GAPS`，下一轮R05-B交易/选秀权与球员名单市场规则，未启动。

## DEV29 R05-B — 交易市场、2017 CBA配平、Stepien、原生选秀权与真实名单执行（2026-10-21）

以下**SRC-0129..0144**服务于K07–K09/R05-B。这批同时有**2017 CBA时期可复核规则**、2K22 **PC本世代**一手玩家报告、同版/相邻版本游戏设置及旧版菜单示例。**跨代机制可研究，平台和模式的原生UI未认证不可直接升级**。不得用2023新CBA first/second-apron惩罚冒充2021–22 NBA2K22的规则。

| ID | 来源、时间、版本定位 | 真实提供的机制资料 | 不得推断 |
|---|---|---|---|
| **SRC-0129** | [Larry Coon 2017 CBA FAQ](https://www.cbafaq.com/salarycap17.htm) Q85–Q100，2022-11-05修订添加2021–22金额 | 2017 CBA的Trade Salary Matching：**非纳税队**发出$0–6,533,333档175%+$100k，$6,533,334–19.6m档发出+$5m，超过19.6m档125%+$100k；**纳税队**125%+$100k，按交易后状态判断；15人Roster、TPE、双向交易估值、签换及Trade Cash限额；2021–22现实交易现金限制$5.785m；选秀权与Stepien有专章 | **HIGH_AUTHORITY_HISTORIC_2017_CBA_SECONDARY_EXPERT_REFERENCE**，不是NBA2K22实际交易合法性代码，不支持“所有球队统一125%”；页面在2022-11后有小修订，需防比对误差 |
| **SRC-0130** | [NBA官方：Free Agency Explained / Traded Player Exception](https://www.nba.com/news/free-agency-explained)，当前可检索网页 | 官方解释Non-Tax与Tax匹配两种分支、同时/非同时Trade和例外原则、潜在Sign-and-Trade限制 | **REAL_NBA_CBA_GENERAL_OFFICIAL**，网页2026时可能更新，不能把新规则或工资额直接视为2021有效；精确2021数值以SRC-0129历史版交叉核对 |
| **SRC-0131** | [RealSport101：NBA2K22 Sliders Game Options](https://realsport101.com/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes)，约2021/22发布的2K22社区指南 | 同版交易设置列Trade Logic、Trade Deadline、Recently Signed/Traded/Rookie Restrictions、Financial Trade Rules、Stepien Rule、Trade Override、CPU Trade Offers和CPU-CPU Trades；另Trade Negotiation Difficulty等数值滑块 | **2K22_CROSSGEN_COMMUNITY_MENU_LABELS_AND_SUGGESTED_SETTINGS**，列出的On/Off或难度80是作者主张，不是本项目实际存档选项值/引擎系数 |
| **SRC-0132** | [Reddit：cannot make trades in MyLeague](https://www.reddit.com/r/NBA2k/comments/vrtew2)，2022-07-05，提问者明确平台**PC** | 玩家表示2K22交易UI确认后人物仍留在原队；评论称CPU-CPU交易可能要求控制双方、另有人建议以3队菜单操作或关某些交易限制绕过 | **SAME_GAME_2K22_PC_CURRENT_GEN_ANECDOTE**；个案/建议未经本项目复现，不能视作任一唯一正确修复，也不自动要求DEV29去改游戏参数 |
| **SRC-0133** | [Reddit r/2KMyLeague：Stuck on date please help (Current gen 2k22)](https://www.reddit.com/r/2KMyLeague/comments/sc30m8)，2022-01-25 | 2K22本世代玩家游戏12/25却看到“不能交易直到12/15”，回帖建议关闭Recently Signed/Traded选项；作者同时报告月度奖项异常 | **SAME_GAME_CURRENT_GEN_PLAYER_REPORTED_CLOCK_ANOMALY**；没有PC本机存档、没有精确日期内存证据，不能认定每个赛季都有该bug |
| **SRC-0134** | [Operation Sports：NBA 2K22 MyNBA Trade Discussion Thread](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917608-nba-2k22-mynba-trade-discussion-thread)，2021-09-28起 | 玩家互评三方Ben Simmons和多个2022–25首轮/乐透保护的**假设报价**，展示多人交易、乐透保护选秀权、跨年条件怎样在游戏社区被讨论 | **COMMUNITY_HYPOTHETICAL_TRADE_PACKAGES**；作者写三方交易方案不证明原版2K22菜单真正支持该交易，更不是当期实际交易 |
| **SRC-0135** | [Reddit：Draft Pick Protections in MyEras](https://www.reddit.com/r/NBA2k/comments/10crgsh)，2023-01-15 | 新世代2K23 MyEras玩家称自己挑选选秀权时未被提示添加保护，显示Unprotected | **NBA2K23_NEXTGEN_MENU_ANECDOTE**，不能得出2K22 PC原版不支持保护或本项目可以执行 |
| **SRC-0136** | [Reddit：Does anyone know how to swap picks in MyNBA next gen?](https://www.reddit.com/r/NBA2k/comments/zu68zj)，2022-12-24起 | 次世代MyNBA用户讨论Pick Swap Best/Worst、Trade Finder/价值显示是否相反以及PS4/PS5差别 | **2K22_OR_2K23_2022_NEARBY_NEXTGEN_UNCLEAR_VERSION**，不可当PC22确证，也不可给本项目添加已明确禁止的Swap交易 |
| **SRC-0137** | [CBS Sports：NBA trade deadline 2022 and Stepien Rule](https://www.cbssports.com/nba/news/nba-trade-deadline-2022-how-complex-stepien-rule-decides-which-teams-can-and-cant-deal-first-round-picks/)，2022-02 | 现实2022年球队2022–28首轮权利、禁止连续未来首轮空缺、保护顺延如何限制更多未来选秀权，以及不确定届次的“first allowable”设计 | **REAL_NBA_2022_JOURNALISM**，不代表PC22是否按这一数学式执行；用户目前三年无保护/无交换是独立世界规则 |
| **SRC-0138** | [NBA官方2021–22 Trade Tracker](https://www.nba.com/news/2021-22-nba-trade-tracker)，2022-03-30官方归档（2022-02-10截止日）；另[2022-01-11 ESPN讨论引用](https://www.reddit.com/r/nba/comments/s1ep8l) | 现实2021–22的2022-02-10交易截止日及球队操作示例，旨在解释游戏“Trade Deadline”控制真实世界时间的参考 | **REAL_NBA_DATE_CONTEXT**；官方归档写明2022年2月10日美东时间15时截止，且列出联盟已批准真实交易；不据日期推导本局以后赛季固定截止日 |
| **SRC-0139** | [Reddit：NBA 2K MyLeague Trading](https://www.reddit.com/r/NBA2k/comments/13wip9g)，2023-05-31 | MyLEAGUE用户报告工资无法配平和超15人提示，回帖建议使用Trade Finder与调整双方收到的人数 | **NBA2K_SERIES_2023_GAME_VERSION_NOT_EXPLICIT**，不是PC22 native执行上限证据，本项目Roster能力需以文档37为准 |
| **SRC-0140** | [NBA2K旧版Wiki Front Office](https://nba2k.fandom.com/wiki/Front_Office)“Execute Trades” | 描述Player Finder、Propose Trade、Trade Finder三条菜单入口，资产为球员/选秀权，Trade Finder可查看系统列出的对手报价 | **OLDER_MYGM_FRONT_OFFICE_WIKI**，不能证明PC22 MyLEAGUE菜单完整同名与排序，或当前游戏已开放自动GM谈判 |
| **SRC-0141** | [Operation Sports 2015：Dumb question how to trade picks in MyLeague](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/753574-dumb-question-but-how-do-you-trade-picks-in-myleague)，2015-02-22 | 老本世代MyLEAGUE玩家称选秀权需在交易选人页切换；有人说当年不能做三方交易 | **OLDER_2015_MYLEAGUE_UI**，与2022 PC玩家“三方可解决”不同年代/条件，不可简单选一个当2K22真理 |
| **SRC-0142** | [NBA2K22 Xbox One MyGM成就交易方法](https://www.trueachievements.com/a338876/maxed-out-achievement)，2021–22时代玩家技巧 | 真实同版Xbox One使用MyGM Game Settings中Trade Override、Financial Rules、Stepien与Recently Signed开关，并进行选秀权交换的操作描述 | **SAME_GAME_OLDGEN_BUT_MYGM_NOT_MYLEAGUE**；它是菜单/开关同代参照，不能把MyGM XP流程映射到离线MyLEAGUE权限 |
| **SRC-0143** | [NBA2K22 PS4/PC 2022玩家交易故障讨论](https://www.reddit.com/r/NBA2k/comments/vrtew2)，同SRC-0132多回复的操作背景 | 该帖还出现“需要两队都受控/尝试三方交易/Trade Logic关掉仍无变化”等**互相不完全相容的玩家经验**，适合标记交易是否真正生效的额外来源争议 | **NOT_INDEPENDENT_SOURCE_DUPLICATE_THREAD**，与SRC-0132指向同帖不应当成两篇独立复现或新增bug成功样本 |
| **SRC-0144** | [Reddit r/NBA：2020年选秀保护概念讲解](https://www.reddit.com/r/nba/comments/isqrc0)，2020-09、以及[CBA 2017 FAQ](https://www.cbafaq.com/salarycap17.htm) | 解释现实保护签Top-N/乐透保护、Swap权仅交换顺位、未送达可能顺延/转换；与本项目简化普通所有权交换形成概念对照 | **REAL_NBA_COMMUNITY_EXPLANATION_AND_CBA_REFERENCE**，不是NBA2K22 PC可以设计保护合同的证据；本世界保护/交换政策为NOT_USED |

### GitHub内真实源及其已验范围（不是互联网SRC）

- **[config/draft_asset_profile.json](../../config/draft_asset_profile.json)**：NBA2K22原生取值Getter确认32字节资产槽，三项8-byte指针、元数据；`src/draft_assets.py`要求未来**5届×2轮×30原队=300条**读数整体完整且原队不重复。用户`gameplay_policy.json`只允许**接下来3届**交易，以当前batch确认的下一选秀年份为起点，禁止新保护/交换。**本机能读5届不授权交易5届**。
- **[config/roster_association_profile.json](../../config/roster_association_profile.json)**＋[doc37](../../docs/37_APPROVED_TRADE_EXECUTOR.md)说明NBA2K22本机**15常规＋2双向＋13活动**、两个独立人数位域以及当前/合同队指针；某些已批准CHI/DET交易从人数遗漏到受控修复，用户最终接受UI。执行器`ownership_transfer_v2`是**有限范围**，没有自动写薪资/税、通用三方、双向、签约/释放和真实CBA完整校验；仍需当前具体玩家批准与readback。
- **[config/gameplay_policy.json](../../config/gameplay_policy.json)**是本世界权威：`draft_pick_trades={year,round,original,current;next_three;no_protection;no_swaps}`，交易双方自愿≠原生CPU必须接受；游戏世界2022选秀年度≠本次历史1984届标签，避免把未来选秀权当历史球员名。
- **[docs/14_TRADE_VALUATION_AND_ASSET_POOLS.md](../../docs/14_TRADE_VALUATION_AND_ASSET_POOLS.md)**仍有历史旧版绝对非卖名单、统一10000点评分、全队固定倍率与125%一律薪资匹配假设；**它是历史提案，不是现行用户批准世界规则，也不应作为DEV29的人格/经营指导模型**。2017现实CBA有不同薪资匹配分支，用户已有新的六模型角色分工。DEV29不改旧文件、不额外开发GM价值打分算法。

**R05-B阶段**：`R05_B_RESEARCH_PUBLISHED_WITH_TRADE_UI_AND_CBA_GAPS`；**R05-C员工、球探和选秀研究尚未启动**。全新原版PC22交易菜单合格逐像素VIS为0，延后独立授权只读定向实机取证；不开发或运行Agent/DEV28/Codex/执行器，不修改游戏。


## DEV29 R05-C — 员工、球探与历史选秀：NBA2K22系列原料和本机Staff/Pools对照（2026-10-21）

**SRC-0145..0160**，共16条**研究参考记录**；同一网址出现于此前SRC时明确为**重新用途索引不是独立新证据**。严守目标**PC22本世代Offline MyLEAGUE**、PS5/XSX次世代MyNBA、老代MyGM、现实NBA和用户项目原生Profile之间的来源分界。

| SRC | 来源、时间、平台 | 本轮有根据的机制原料 | 证据边界 |
|---|---|---|---|
| **SRC-0145** | [2K Newsroom官方 MyNBA/MySTAFF 开发说明](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)，2021-09-08；全文可见[开发组原文转录](https://nba2kw.com/nba-2k22-mynba-full-details-mystaff-training-pre-built-teams-more) | 官方确切4部门/前台+教练+球探+医疗的完整职位；\`Head Scout\`、4\`Domestic\`、2\`Foreign\`，团队17名最大受Staff Budget限制、员工徽章与岗位适配度；Prep Hub/团队训练的正式角色 | **SAME_GAME_OFFICIAL_NEXTGEN_PS5_XSX_ONLY**；已有旧SRC-0128是较短版本。本机PC Native静态8岗位不因此变17岗位或宣称“总员工数17” |
| **SRC-0146** | [Reddit r/NBA2k：Staff Roles in MyLeague](https://www.reddit.com/r/NBA2k/comments/gnk1fg)，2020-05 | 2K20旧本世代MyLEAGUE用户列CFO/Assistant GM/Head Coach/Assistant Coach/Head Scout/Trainer六个旧基础职位、玩家不确定具体岗位用途 | **OLDER_CURRENT_GEN_2K20_COMMUNITY**, 回复“某级球探给额外训练营”未受控制且可能混淆Scout/Trainer，不当公式 |
| **SRC-0147** | [Operation Sports：To my MyLeague guys: does this new MyStaff stuff really make a difference?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916833-to-my-myleague-guys-does-this-new-mystaff-stuff-really-make-a-difference)，2021-09-10–12 | 刚发布的2K22玩家说有17人限制、四部门名额冲突、伤病恢复有个别观察；有玩家猜6名Scouts会使新秀充分侦察 | **2021_2K22_NEXTGEN_PLAYER_EXPERIENCE_VS_SPECULATION**；一个医学配置与伤停案例不是引擎效应量化；“6人全部100%”是猜想 |
| **SRC-0148** | [Reddit：MyStaff Unpopulated](https://www.reddit.com/r/NBA2k/comments/plqir1)，2021-09-10/13 | 有玩家描述开档后部分职位空缺且Staff Budget不足以填满，对象称\`MyLeague\`，展示开档真实预算与员工位置需要分开研究 | **2K22_2021_COMMUNITY_PLATFORM_NOT_VERIFIED**；发帖者可能指新代MyNBA俗称MyLeague，不能证明PC本机也有空缺BUG |
| **SRC-0149** | [DiamondLobby：How to Download a Draft Class in NBA2K22](https://diamondlobby.com/nba-2k22/how-to-download-a-draft-class-nba/)，2022-04-30 | 同版MyLEAGUE/MyGM说明Auto-Generated、Historic、User-Created、Create/Edit Draft Class；可进入\`Scouting→Prospect Scouting\`，查看DraftExpress/2K/NBA.com排名列及Scouts Projected OVR，文章含截图 | **2K22_COMMUNITY_GUIDE_MIXED_MYLEAGUE_MYGM_MODE; SOURCE_IMAGES_NOT_PC22_PIXEL_AUTHENTICATED**，不能把“DraftExpress是最佳”这种作者主观看法当GM决策法则 |
| **SRC-0150** | [Reddit：Online MyLeague: Custom Draft Classes](https://www.reddit.com/r/NBA2k/comments/tlv74d)，2022-03–06 | 最初表示Online模式找不到选秀班载入按钮，后续用户确认可通过\`Scouting→Prospect Scouting→选择一位新人\`弹出Import Draft Class菜单 | **2K22_ONLINE_MY_LEAGUE_USER_RESOLUTION**；不能据此认Offline必须联网或每次都自动弹窗 |
| **SRC-0151** | [Reddit：Do you turn scouting on Auto in myLeague?](https://www.reddit.com/r/NBA2k/comments/p4fzvv)，2021-08-14/15 | 旧同代玩家描述Auto一般侧重高排名/本队手中签附近人物，但可能不会100%覆盖；可手动侦察作为选项 | **PRE_NBA2K22_RELEASE_2K21_OR_OLDER**；不能认成2021-09上市的2K22 CPU策略数学式 |
| **SRC-0152** | [Reddit：MyLeague tutorial?](https://www.reddit.com/r/NBA2k/comments/zkqqwb)，2022-12-13–16 | 一手提问者看见Prospects部分人有\`Scouted 40%\`而不知道如何再提高；回帖建议查Auto/Manual、Scout评分和选取球员 | **LATE_2022_GAME_VERSION_AND_PLATFORM_NOT_RESOLVED**, 不是PC22已知每回合进度或百分比公式 |
| **SRC-0153** | [Operation Sports：MyLeague - How in the bloody hell do you Scout?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/692527-myleague-how-in-the-bloody-hell-do-you-scout)，2015-06，开发者Leftos旧回复 | 老MyLEAGUE员工球探每隔若干游戏天刷新一次菜单、可在旧模式手动指定新秀侦察，示范游戏Scout Report有阶段/旧报告 | **2015_MYLEAGUE_DEVELOPER_FOR_OLDER_GAME**，不能将“11月15起每15天一次”或“每组7人”硬编码为PC22日期/可选数 |
| **SRC-0154** | [Reddit：My NBA Draft Prospect question](https://www.reddit.com/r/NBA2k/comments/yvo6n0)，2022-11-15 | 同代玩家举\`scouted 100%\`时\`81 OVR/A- Potential\`与\`76 OVR/A+ Potential\`问题，询问是否代表真实潜力 | **COMMUNITY_QUESTION_NOT_VERIFIED_CAUSAL_ANSWER**，不能由询问证明“A Scout 100%”准确，也不能导出官方potential grades对应表 |
| **SRC-0155** | [Reddit：MyLeague Potential](https://www.reddit.com/r/NBA2k/comments/wc2bwb)，2022-07-30，作者明确说MyLeague 2K22 | 玩家区分球员卡\`Potential Grades A-/B+\`与\`Edit Player/Misc Potential 25–100\`基础属性，是**同版本两种不同显示对象** | **SAME_GAME_MYLEAGUE_2022_COMMUNITY**；卡面潜力评分不等于游戏原始潜力，也不能绕本世界GM Potential=1遮蔽 |
| **SRC-0156** | [Reddit：2k22 Xbox draft class](https://www.reddit.com/r/NBA2k/comments/v70hop)，2022-06至08；参考[OS 2022-11 Export/Import DNA](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/932913-can-you-create-a-draft-class-using-existing-players-from-historic-draft-classes) | 2K22玩家描述历史新秀复制成Rookie级、Export/Import Player DNA/自建Draft Class的路径；后续相邻2K系列用户一致提到DNA复用 | **GAME_EDITOR_UI_CANDIDATE_AND_COMMUNITY_WORKFLOW**；玩家自己改能力≠本项目可擅自改普通人物能力，PC22 Import DNA精确字节范围未知 |
| **SRC-0157** | [NBA.com：2022 NBA Draft Board](https://www.nba.com/draft/2022/draft-board)，2022年官方赛后实际选秀名单 | 现实选秀结果有Pick、Team、Player、Position、College、Country等，说明**实际Draft Result对象**与Game Draft Projection的性质不同 | **REAL_WORLD_2022_DRAFT_OUTCOME_NOT_PROJECT_WORLD_STATE**；本项目2022游戏内选1984历史新人，不能拿现实Banchero当本局状元 |
| **SRC-0158** | [The Ringer 2022 NBA Draft Guide](https://nbadraft.theringer.com/2022/)，2022-06-23终版；亦见[Chad Ford Big Board vs Mock Draft](https://www.nbabigboard.com/p/2022-big-board-1)，2021-11 | 现实篮球媒体严格区分Big Board（媒体自己觉得谁厉害）与Mock Draft（预测谁被哪队选），且会更新排名/球队需要 | **REAL_BASKETBALL_EDITORIAL_CONTEXT_ONLY**，不是NBA2K22原版三种榜单的计算函数，不能向本局媒体泄漏未来真实选秀已发生结论 |
| **SRC-0159** | [Bleacher Report 2022 Post-Combine Big Board](https://bleacherreport.com/articles/2956335-2022-nba-draft-big-board-top-50-prospect-ranking-post-combine)，2022-05 | 现实NBA2022选秀球员体测、运动能力和5月实战观测资料可影响真实媒体评价 | **REAL_WORLD_COMBINE_NOT_PC22_GAME_UI**；不能证明原版PC22离线MyLEAGUE可配置同名Combine/Workout页面 |
| **SRC-0160** | [Reddit：This game should explain how MyLeague actually works](https://www.reddit.com/r/NBA2k/comments/xvdc5e)，2022-10-04 | NBA2K玩家直接质疑教练、Trainer、Mentorship、不同专科Staff的真实效果；回复有人认为Head Coach显著、另有人认为专科教练没用、伤病医疗有效，声音相互不一致 | **OCT_2022_LIKELY_2K23_SERIES_COMMUNITY_CONFLICTING_EFFECTS_NOT_2K22_PC_VERIFIED**；回复“效果为零/＋1–2属性”没有控制实验且跨新代UI，不能变成R05-C“专科员工无用”定论 |

### R05-C已确认项目原生源与旧文范围说明

- **STAFF Profile确知13项字段、8种Position枚举**：\`config/memory_field_profile.json\`、\`src/source_extensions.py::staff_details\`。后者从`name_anchor-0x30`读取`0x160字节`、STAFF.team_pointer at +0x18，使用球队反向职位指针把岗位匹配标为\`VERIFIED_RECIPROCAL_TEAM_ROLE\`。**没通过反向匹配的员工不能被默认当Free Agent**。Github已有\`published/.../staff.json\`路径表示已发布员工数据，但本轮没有声明其最新日期或完成全部人事业务读取。
- **Draft源限制**：\`src/historical_rookies.py\`只有\`raw_struct[0x70] & 0xE0 == 0xE0\`且年份/身份有效者可作1984–2020历史新秀候选；\`docs/20_HISTORICAL_DRAFT_POOL_AND_INJECTION_SPEC.md\`记录旧批次3,320总球员槽与某些届次覆盖示例，而**目标临时新人槽没有验证成可执行注入工具**。\`src/extract_live_draft_class.py\`是早期内存聚类实验工具，不等于已认证真实Draft数据源。
- **Potential绝不泄漏**：\`docs/development_tasks/DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md\`要求给GM的数据里真实潜力脱敏为1，其含义是`MASKED`、不是低潜力。未经隔离的真实潜力历史新秀源也不得从公开脱敏库反向用作原生选秀注入，防止把潜力1写进游戏。
- **旧人设/增强方案拒绝归为事实**：\`docs/05_STAFF_AND_PLAYER_GROWTH.md\`开头已标旧版成长改值已废止，\`docs/12_NATIVE_MENTORSHIP_AND_STAFF_GUIDE.md\`很多定量医疗/训练影响也未经PC22实机验证。DEV29只收录已追溯原生来源和可靠UI语义，不继承“训练师自动让Jordan的三分直接上涨”等违反用户世界法则的编排。
- 本轮不对任何GM作选秀排序、员工招聘建议或球探行为算法；**Staff薪资/合同、Scouting细节、Draft结果未认证的精确菜单和值域仍为UNKNOWN**。机读全目录[`R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json`](catalogs/R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json)，中文指南[§§16–22](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)。

**本轮状态：\`R05_C_RESEARCH_PUBLISHED_WITH_STAFF_SCOUT_DRAFT_UI_GAPS\`；下轮R05-D经营全域资料整合，未启动。**

## DEV29 R05-D — 经营全域交叉来源与2026-10-21选秀权政策更新

| 来源ID | 来源及日期 | 具体研究价值 | 证据限界 |
|---|---|---|---|
| **SRC-0161** | [Operation Sports：NBA 2K19 MyLEAGUE and MyGM Developer Blog](https://www.operationsports.com/nba-2k19-myleague-and-mygm-developer-blog/)，2018-08-02 | 2K开发者历史说明：2K19从原先可提前交易未来四届选秀权**扩展为五届**，同时拥有每届折旧率等研究对象；说明2K游戏系列可支持与真实NBA不同的未来年份交易限制 | **OFFICIAL_DEVELOPER_2K19_NOT_2K22_NATIVE_PROOF**；不能单凭旧版文章认证PC22全部菜单/值域；本项目Native 5届资产另有独立真实源支持 |
| **SRC-0162** | [CBS Sports：NBA trade deadline 2022 / Stepien Rule](https://www.cbssports.com/nba/news/nba-trade-deadline-2022-how-complex-stepien-rule-decides-which-teams-can-and-cant-deal-first-round-picks/)，2022-02-10前夕 | 现实2021–22 NBA交易选秀权最长提前七年、未来连续首轮/保护顺延限制；说明真实NBA的七年、2K19设计的五年、本项目曾经三届的外挂限制是**三个不同来源层** | **REAL_NBA_2022_JOURNALISM_ALREADY_CROSS_REFERENCED_SRC-0137**；与SRC-0137同网页，为R05-D“多来源不同层次”索引，不能计作全新独立验证材料 |

### R05-D项目原生与业务边界交接

2026-10-21用户明确**取消“选秀权仅未来三届可交易”的世界规则**。已在[权威机读配置](../../config/gameplay_policy.json)发布`PLAYER_RULES_20261021_V4`：`draft_pick_trades.maximum_future_drafts=null`、原生资产核对/唯一归属仍必需，**不取代为世界选五届固定上限**；不使用保护和Swap、不修改球员Ability、交易写入需真实玩家具体批准，全部保留。文字权威[文档26](../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)同步。

**资料≠实现**：`src/draft_assets.py::trade_window`、`src/gm_core/calculations.py::draft_pick_window`、`src/gm_core/trades.py`、`src/approved_trade_executor.py`尚有三年窗口依赖；旧runtime因此仍可能拦截原生第4/5届。此为未来明确授权的**Codex工程同步缺口**，本轮DEV29不开发/运行修复，严禁谎称5届均已可以执行。

整合机读[R05-D经营全域目录](catalogs/R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json)收录17合同字段、10财务观察/候选、14名单/选秀权结构、13 Staff字段，共**54条异质资料项**；又收录21市场概念、16交易候选、10球探类别、10Draft类别、6员工管理候选共**63类信息/操作原料**，记录12项相关机制及12项PC22未认证缺口。**不能把54写成54条当前真实游戏数值，也不能把63写成63个已证明可以写入的UI按钮**。见[K07/K08/K09完整中文攻略§§23–29](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)。

**阶段结束**：`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`，保留来源及实机未知，R06下一轮未启动；独立审核交其他模型，不开发Agent/GM竞价规则、DEV28/Codex或修改游戏。

## DEV29 R06-A — NBA2K22本世代3D、日历Sim、滑块与统计标准化（2026-10-21）

以下SRC-0163..0173按**真实游戏平台/模式/资料发生日期**分开；早年作品的MyLEAGUE、PS4旧世代与PC22有机制参考价值，但不能未经实机证据直接升级为同一内存偏移和游戏效应。作者调校值只作为所见菜单/案例来源，**绝不是官方默认值或本世界获批设置**。

| 编号 | 证据链接、时间和平台 | 提供的可研究游戏事实 | 版本及因果限制 |
|---|---|---|---|
| **SRC-0163** | [Operation Sports：cdcool NBA2K22 CPU vs CPU MyLeague Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-pc-forum/918715-cdcool-nba-2k22-cpu-vs-cpu-myleague-sliders)，2021-11-03至2022-01-01 | **PC专版**一手明确`CONTROLLING ALL TEAMS`、`Watching every game, not Simming anything`，Quarter 12、Game Speed 65、实时投篮/防守/犯规等Gameplay真实菜单选项；能直接说明30队经营与3D CPUvsCPU是不同操作维度 | **2K22_PC_CURRENTGEN_FIRSTHAND_TEXT**；作者的滑块组合变化次数多、不受控，不能证明每个值必然产生其描述的结果，亦不是本用户存档当前值 |
| **SRC-0164** | [OS：RES2 NBA2K22 All Star Current Gen Sliders第3页](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders/page3)，2022-01-07 | 玩家明确询问PC默认阵容，作者明确答`Yep - PC with default rosters`，并列Setup Quarter Length 12、Sim 11、Simulation Fatigue/TeamPace/Fastbreak/Possession Results/Shot Types/Shot Percentages/Stat Distribution完整分组及对攻防设置 | **NBA2K22_PC_ACCEPTED_PLAYER_REPORTED_SETTINGS**；作者同时建议提升犯规的Roster tendency编辑，不能把全部Sim统计结果归因某滑块；设置数值不是默认 |
| **SRC-0165** | [OS：DarthRambo NBA2K22 MyLeague settings/sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)，2021-09-14起，作者明确`I am on PS4` | **同版PS4旧世代**列同套Simulation设置，分Player Fatigue、Team Style Factors、Possession Results、Shot Types/Percentages、Stat Distribution；同时列3D CPU/USER和角色Tendency改动 | **NBA2K22_PS4_MYLEAGUE_OLDER_CONSOLE_NOT_PC_PIXEL_CAPTURE**；PS4作者“觉得两代一样”是经验主张，不是内存实现验证；其个人Tendency改动混杂结果 |
| **SRC-0166** | [Shady Mike Gaming：NBA2K22 PC/旧世代Slider Set Gameplay Showcase](https://www.youtube.com/watch?v=yMGZbgeqqSM)，2021-10-31 | 视频发布页列Hall of Fame、Quarter 12、Game Speed 55、Real Player%控制与Offense/Defense/Attributes/Tendencies/Fouls，以及**8类With/Without Ball Movement Min/Max**；作者称PC的部分Movement滑块效果不确定 | **2K22_PLAYER_VIDEO_DESCRIPTION_CROSSGEN_PC_REFERENCE**；描述不是逐帧验证的PC原生UI；作者认为“broken”是自述疑虑，不证明真的无效 |
| **SRC-0167** | [RealSport101：NBA2K22 Sliders & Game Options](https://realsport101.com/article/nba-2k22-sliders-realistic-settings-gameplay-options-optimized-experience-offense-defense-movement-attributes)，原发布于2K22上市后 | 同版混合MyLEAGUE/MyNBA攻略给出了Season/Quarter/Sim Quarter/Normalize Played Minutes/Stats和Simulation Difficulty、Player Recovery/Team Pace/Possessions等菜单名 | **2K22_CROSSGEN_COMMUNITY_GUIDE_AND_SUBJECTIVE_RECOMMENDATIONS**；某个作者建议`Pace=49`与PC玩家的`Pace=100`不一致，不能用推荐值冒充默认或某种固定篮球输出 |
| **SRC-0168** | [gu8lal8 2K22 COMPETITIVE sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)，2022年 | 旧世代作者记录HoF、All-Star等难度基线与USER/CPU Offense/Defense、Shot Timing/Real Player%、控制配置、Gameplay滑块类别 | **2K22_PS4_USER_RECORDED_PRESET_TABLE_NOT_CURRENT_PC_BUILD_READBACK**；默认USER和CPU数值可能不同，不可把全部当50或从别家配置直接改动本存档 |
| **SRC-0169** | [Operation Sports：CPU Sliders = User's CPU teammates](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/847158-cpu-sliders-user-s-cpu-teammates)，2017年代旧NBA2K讨论 | 老玩家讨论手柄实际操控一名球员时，场上其他电脑操控队友是否遵从CPU Slider；提供经营控制权/场上AI消费两者可能分离的问题线索 | **OLDER_VERSION_COMMUNITY_INTERPRETATION_NOT_PC22_PROOF**；不可给全队30支User-controlled球队统一强行灌USER参数 |
| **SRC-0170** | [Reddit r/NBA2k：MyLeague Glitch](https://www.reddit.com/r/NBA2k/comments/var3vi)，2022-06-12—13 | 同版MyLEAGUE玩家报告实场比分126:116，退出显示304:287及球员得分等异常高值，回复建议检查Normalize Played to Sim开关，用户承认打开 | **NBA2K22_2022_PLAYER_REPORT_UNCONTROLLED**；不能得出确定固定缩放系数、每个平台必然出现、菜单真实存储布局已验证 |
| **SRC-0171** | [OS：Normalize Played to Sim Minutes Error?](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/909203-normalize-played-to-sim-minutes-error)，2021-04-25（**早于NBA2K22上市**） | 玩家报告8分钟实场/12分钟模拟下Stats和Minutes缩放分离，回帖明确存在两个不同开关 | **PRE_RELEASE_OLDER_2K_SERIES**；不能冒充2K22 PC同版BUG；用于解释为什么现有`simulation.normalize_stats`单字段不必然覆盖两个菜单 |
| **SRC-0172** | [Reddit：Can you adjust played stats to sim stats in 2k22 MyGm?](https://www.reddit.com/r/NBA2k/comments/tcdy67)，2022-03-12—06-18 | 同版**MyGM**用户找不到Normalize设置，回复者称MyLEAGUE已有类似选项；说明即使同一游戏，模式入口可能不同 | **2K22_MYGM_MENU_UNCERTAINTY_AND_COMMENTS**；提问/找不到不等于目标离线MyLEAGUE没有功能 |
| **SRC-0173** | [OS：J-Kits NBA2K22 12min HoF Sim Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917660-j-kits-kingsimkits-nba-2k22-12min-hof-sim-sliders-real-stats-gameplay)，2021-09—2022-02 | 同版**PS5 MyNBA次世代**作者公布HoF USER/CPU 3D投篮、Movement、接触、防守等很细分设置与Box对照；说明引擎分组可供知识查漏 | **NBA2K22_PS5_NEXTGEN_DIFFERENT_COURT_ENGINE**，严禁照搬PC22数值/偏移/获批配置；作者的“12min sim”标题指拟真Gameplay也不能替代Calendar Quick Sim实证 |

### R06-A 原生项目资料索引与实机能力边界

- [settings.json](../../config/state_io_native/settings.json)与[world.json](../../config/state_io_native/world.json)：项目可追溯注册**49+37=86个静态字段候选**；可能不同catalog同地址重复，不是86个实时已观测值或安全可改按钮。`src/gm_state_io/registry.py`已有WORLD_SETTING目录导入逻辑，软件允许计划`writable`不等于PC22内存地址、UI枚举、持久化及玩家批准完成验证。
- [court.json](../../config/state_io_native/court.json)只给出较窄的4个Gameplay滑块技术参考；[src/slider_manager.py](../../src/slider_manager.py)属于旧静态地址读取/一键设置工具，后者会改游戏，本轮未运行。旧[docs/10_GAME_SETTINGS_AND_SLIDERS.md](../../docs/10_GAME_SETTINGS_AND_SLIDERS.md)开头已经自行标注部分“权威默认与最优值”未经实测，不能当原生默认真值。
- **一个重要字段差距**：项目`settings.json`目前只有一个概括的`simulation.normalize_stats`，公开MyLEAGUE设置却区分**Normalize Played to Sim Minutes**与**Normalize Played to Sim Stats**，不能不经认证把单字段硬解释成两个开关都已观察到。
- 真实游戏玩家观察与命中率/防守因果隔离，详见[Live Court V3](../../docs/research/NBA2K22_LIVE_COURT_GAMEPLAY_PARAMETERS_V3.md)和[原HOF研究](../../docs/research/NBA2K22_HOF_CURRENT_GEN_PROVEN_SLIDER_RESEARCH_20261019_V1.md)。R06-A不执行全局设置修改、不关闭原版ACE、不开发实时教练、不修改人物能力、不创建Agent/调度。
- [R06-A中文攻略](guides/K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md)和[机读研究目录](catalogs/R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json)登记来源和字段级覆盖，但**没有在当前PC22正式存档上进行新内存读写、真正CPU比赛或重启持久化验证**。

**研究状态`R06_A_RESEARCH_PUBLISHED_WITH_PC22_RUNTIME_VERIFICATION_GAPS`。下一轮R06-B历史纪元/奖项/媒体尚未启动，R05用户批准结案状态不变。**

## DEV29 R06-B — 历史纪元、奖项、联盟纪录、媒体与规则历史（2026-10-21）

研究只收集游戏可见事实、参数及机制；**不设计媒体/教练/球员人格**，不写游戏。历史参考与本游戏实际赛季分离，PC22原生能力状态严格审计。

| 来源编号 | 游戏版本/原始资料 | 支持的研究事实及限制 |
|---|---|---|
| **SRC-0174** | [2K23 Eras官方公告 2022-08-18](https://newsroom.2k.com/news/rewrite-nba-history-in-nbar-2k23-with-all-new-mynba-features-for-playstation-5-and-xbox-series-xs-consoles) | 2K23 PS5/XSX ONLY；1983/1991/2002/Modern原生Era，**不是PC22原生功能** |
| **SRC-0175** | [2K22 MyNBA官方次世代新功能 2021-09-08](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles) | 2K22 PS5/XSX MySTAFF/Prep Hub等；不能推断PC当前世代原生菜单 |
| **SRC-0176** | [DiamondLobby NBA2K22下载Draft Class指南 2022-04](https://diamondlobby.com/nba-2k22/how-to-download-a-draft-class-nba/) | NBA2K22 MyLEAGUE开档三选与Scouting→Prospect Scouting，文章附截图但不是本存档实机读回 |
| **SRC-0177** | [OS NBA2K22历史球员Draft Class讨论 2021-12](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/919626-nba-2k22-best-draft-classes-2022-2026) | 玩家历史球员自建Draft Class报告，非当前player_pool库存或全部1984–2020认证 |
| **SRC-0178** | [Reddit NBA2K22 MyLeague HOF历史菜单问答 2022-07](https://www.reddit.com/r/NBA2k/comments/wbudty) | 同版玩家实际看到Past MVPs/Past Rule Changes/Past Retired Jerseys，HOF最终称找到但无导航截图 |
| **SRC-0179** | [Reddit NBA Records菜单导航回复 2022-10](https://www.reddit.com/r/NBA2k/comments/ybauno) | 标题/语境可跨2K22/23，回复称League News>League History>NBA Records，不能当原版PC22精确菜单认证 |
| **SRC-0180** | [Reddit MyLeague历年NBA Records分类 2023-06](https://www.reddit.com/r/NBA2k/comments/14iox5m) | 2K21/23玩家纪录维度与按钮类别讨论；跨版本，不能推断PC22完整历史读写 |
| **SRC-0181** | [2KSpecialist NBA2K22 PC MyLeague 社交媒体文字资源Mod 2021-12](https://www.2kspecialist.net/2021/12/nba-2k22-myleague-social-media-overhaul.html) | PC22 Social Media / Power Rankings / Mock Draft已有文本资源和模板线索；修改版与无Mod UI/独立媒体AI不可混同 |
| **SRC-0182** | [NBA2K Wiki MyLEAGUE通用页面](https://nba2k.fandom.com/wiki/MyLEAGUE) | 系列旧作对休赛期Rule Changes、投票、关闭或否决的概述；非原版PC22同一菜单逐项认证 |
| **SRC-0183** | [OS 2020 MyLEAGUE Rule Change History操作问答](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/887262-reverse-rule-changes) | 旧版可通过League News、Rule Change History、Active Rules检查/关闭；不保证PC22同效 |
| **SRC-0184** | [OS 2K23 MyNBA Draft Class不生效与Scouting重载社区讨论 2022-09](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/926111-2k23-mynba/page9) | 2K23版本玩家导入问题，PC22仅作为待排查线索 |
| **SRC-0185** | [2KSpecialist 2K22 历史Draft Class 1950–2017资源 2021-10](https://www.2kspecialist.net/2021/10/nba-2k22-draft-class-1950-79-1980-84.html) | PC22历史人选自建资源/年份形式参考，不代表当前存档选秀完整或类型码已验 |
| **SRC-0186** | [OS NBA2K19 MyLeague Finals MVP Awards History缺失 2019-11](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/885237-gripe-finals-mvp-s-aren-t-listed-under-players-award-history-in-myleague) | 旧版单玩家获奖菜单遗漏问题，不能当PC22肯定仍有同Bug |

详见 [R06-B K10中文攻略](guides/K10_HISTORY_AWARDS_MEDIA_R06B.md) 与 [31类机读目录](catalogs/R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json)。**R06-B仅公开研究结案**，新的已确认原版PC22完整菜单像素截图、当前存档运行时历史奖项/纪录读回、跨季持久化和全部菜单合法枚举均为0；这些是待独立验证缺口，绝不可报为已实现。


## DEV29 R06-C — 赛季阶段、游戏存档与跨期历史保留（2026-10-21）

本批只登记同版玩家证据、跨模式/旧版问题线索与官方平台支持边界；不把故障个例认定全平台普遍问题，保留任何目标存档原生UI和GameDate取证UNKNOWN。

| ID | 直接来源 | 所支持的事实及不能越界的解释 |
|---|---|---|
| **SRC-0187** | [2K官方Online Services Status（NBA2K22）](https://support.2k.com/hc/en-us/articles/33058906107667-2K-Online-Services-Status) | 2K22在线服务2023-12-31终止；MyLeague/MyNBA列离线可玩。官方支持说明，非Steam云端及存档实时持久化认证 |
| **SRC-0188** | [OS Thunder Up Rebuild NBA2K22 2022-07休赛期多存档建议](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/923062-thunder-up-rebuild-in-okc-nba-2k22/page10?postcount=314) | 2022同版讨论明确阶段Save推荐；部分来自旧MyLeague经验，Staff Draft锁定等不证明2K22原生 |
| **SRC-0189** | [DiamondLobby NBA 2K22 MyLeague Fantasy Draft设置](https://diamondlobby.com/nba-2k22/set-up-fantasy-draft-nba-2k22-myleague/) | 同版MyLeague Start in Regular Season / Setup Options；个人范例，不是用户当前存档读回 |
| **SRC-0190** | [DiamondLobby 2K22 MyLeague自由市场报价](https://diamondlobby.com/nba-2k22/create-a-superteam-nba-2k22-myleague/) | 同版Free Agency报价Offers和Expected列、谈判；数值公式不明 |
| **SRC-0191** | [Reddit NBA2K22 PC Steam Save与Save as均未持久](https://www.reddit.com/r/NBA2k/comments/w6rgfl) | 2022-07同版PC单人问题报告，证明当事用户用过Save/Save as，不证明普遍失效 |
| **SRC-0192** | [Reddit 2K22 PC MyGM卡VC saving与MyLeague文件消失](https://www.reddit.com/r/NBA2k/comments/tgmbpi) | 2022-03跨模式单人故障报告，不能推广到所有离线MyLeague |
| **SRC-0193** | [Reddit 2K22 PC存档限制猜测](https://www.reddit.com/r/NBA2k/comments/tl3h4l) | 2022-03保存故障与网友推测总文件/下载球队过多；未验证上限 |
| **SRC-0194** | [Reddit NBA2K22 2022跨平台反馈线程](https://www.reddit.com/r/NBA2k/comments/tz5gx4) | 2022玩家报告PS5 MyNBA推进/休赛期Bug；未验证PC本世代同缺陷 |
| **SRC-0195** | [Reddit 2020前代MyLeague统计错季/奖项缺失](https://www.reddit.com/r/NBA2k/comments/j0maya) | 旧版本球员前季数据混乱第一手，作为检查风险非2K22实证 |
| **SRC-0196** | [Reddit 2019更早MyLeague历史选秀/交易/退休记录疑问](https://www.reddit.com/r/NBA2k/comments/ckc80q) | 提问不等于证明2K22历史留存范围 |
| **SRC-0197** | [2K官方2026 Steam云端备份恢复通用指南](https://support.2k.com/hc/en-us/articles/53087390841491-Restoring-Saves-from-the-Cloud) | SteamCloud同步依赖客户端及游戏支持；2026通用平台说明，非2K22原版存档机制证明 |
| **SRC-0198** | [OS 2K22退役球员转教练教程](https://www.operationsports.com/heres-how-to-make-any-player-become-a-coach-in-nba-2k22/) | 同版退休页面与未来员工候选线索；教程涉及改年龄/能力，本项目禁止照做 |
| **SRC-0199** | [OS 2K22 PS4 Orlando Magic Dynasty设置](https://forums.operationsports.com/forums/forum/dynasty-headquarters/basketball-dynasties/916690-the-orlando-magic-dynasty) | 2K22 PS4本世代玩家公开82赛季/BO7、真实与Sim、Normalize设置；个人配置不代表PC默认 |

[R06-C中文攻略](guides/K11_SEASON_SAVE_PERSISTENCE_R06C.md)及[38类候选机读目录](catalogs/R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json)均为**研究原料，不是38项已测本机原生偏移**。本轮不进行游戏推进/存档/重启实验，不开发Agent或DEV28。
