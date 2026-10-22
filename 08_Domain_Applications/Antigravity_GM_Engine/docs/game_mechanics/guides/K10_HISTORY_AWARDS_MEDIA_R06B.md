# K10 — NBA2K22 历史选秀轮回、奖项、纪录、联盟媒体与规则历史（R06-B）

> DEV29 R06-B，2026-10-21；目标为 **NBA2K22 PC 本世代离线 MyLEAGUE**。本文件是纯资料研究，不批准或实现历史重力、媒体人格、奖项人工改判、自动推进赛季、存档/球员/教练写入。旧世代和次世代的功能用于理解，菜单与内存仍需独立认证。伴随机读目录 [R06B_HISTORY_AWARDS_MEDIA_RESEARCH_V1.json](../catalogs/R06B_HISTORY_AWARDS_MEDIA_RESEARCH_V1.json)；外部来源见 [SOURCES](../SOURCES.md) 的 SRC-0174–0186。

## 7. 三种时间轴不可混同：游戏赛季、历史选秀届、参考历史纪元

| 时间轴 | 当前项目实际规则 | 不能误当成什么 |
|---|---|---|
| `GAME_SEASON` / `GAME_DATE` | **NBA2K22存档2021–22开局**，之后由原生赛季、比赛与实际保存决定事实 | 历史球员的真实选秀年份、真实世界未来发生的赛果 |
| `DRAFT_CLASS_YEAR` | **1984→1985→…→2020→1984**；每完成一届选秀才推进，必须以真实已导入/完成节点验证 | 游戏日历年份自动等于历史选秀年份；每届全部真实球员一定有可认证新秀模型 |
| `REFERENCE_ERA` | 玩家另外审批的“历史重力/模拟纪元”研究背景；参考现实NBA及跨时代人物资料 | NBA2K22 PC 原生内建历史 Era 模式或现实世界结果必然发生 |

第一赛季（2021–22）对应首届目标历史选秀1984；按每季成功推进一届，2025–26赛季后为1988届。这只是**项目业务对照**，不能替代读当前存档赛季/已完成选秀计数，也不能将2026游戏年的奖项算成1988历史NBA奖项。

2K官方**2022-08-18**对NBA2K23 **PS5/XSX次世代**才发布 `MyNBA Eras` 四类开局：1983 Magic/Bird、1991 Jordan、2002 Kobe、Modern；包含时代球馆、球衣、电视滤镜和历史搬迁（SRC-0174）。因此不得把“NBA2K23 Eras原生动态”登记成**NBA2K22 PC的本地按钮或可写偏移**。2K官方对NBA2K22 MyNBA特色（MySTAFF/Prep Hub/Conditional Coaching）也明确限定次世代（SRC-0175）。

**历史新秀真正的2K22玩法**：2022年同版指南报道：开档初始弹窗可选择 `Auto-generate rookies` / `Create/Edit draft class` / `Load/Download draft class`，第二层有现成Historic或User-Created选择，之后可由Scouting→Prospect Scouting查看名单（SRC-0176）；同版玩家社区亦有历史人物混合选秀类内容（SRC-0177、SRC-0185）。具体PC22目标存档、年份覆盖、替换同档Draft Class后何时固定、导入成功后候选人身份，必须用游戏和项目选秀数据库另行核对；`src/draft_engine.py`相关玩家政策已有“新秀类型码/克隆”专门约束，不允许靠名字推断完整名单。2K23次世代玩家报告初次导入时文件不生效、需Scouting界面重载（SRC-0184），**这是跨版本错误线索，不是PC22已认证Bug**。

## 8. 联盟奖项：先找游戏原生赛季结果，再判断可否长期保留

2022-07 NBA2K22 MyLEAGUE玩家明确描述在菜单中看到**Past MVPs、Past Rule Changes、Past Retired Jerseys**，但一度找不到名人堂过去入选名单；随后自己表示找到隐藏位置，未给出可靠操作路径（SRC-0178）。因此“2K22存在部分历史奖项/规则/退役球衣可见页”有同版玩家证据；“所有奖项逐年完整、所有球员可回溯、名人堂入口精确位置”依旧 `UNKNOWN`。

**独立审核定向纠正（2026-10-21）**：`SRC-0178`只直接支持“Past MVPs / Past Rule Changes / Past Retired Jerseys”及HOF提问，不支持ROY、DPOY、Sixth Man、MIP、COY、All-NBA、All-Defensive、All-Rookie、All-Star、Champions这10个各自具体菜单。它们保留在研究待证候选目录中，但`sources=[]`、`classification=RESEARCH_CANDIDATE_UNSOURCED`，不以未匹配的来源冒充认证。`MVP`只继承Past MVPs菜单线索，不证明当前本存档MVP结果已采集；目录的31条是**功能/信息概念，非31个内存字段或数据库列**。外部2K23 Eras不构成排他证明“PC22绝无同名隐藏对象”，该项原生证明仍UNKNOWN。

应分层登记候选：
- **赛季竞争与结果**：常规MVP、ROY、DPOY、Sixth Man、MIP、COY；这些是2K系列常见奖项类别，但本轮**未取得PC22目标存档逐项菜单和历季读回**。
- **球队/联盟荣誉**：NBA冠军、总决赛MVP、All-NBA/All-Defensive/All-Rookie球队、All-Star等；All-Star选入和All-NBA阵容**不等于**获得年度MVP。
- **长期人物荣誉**：历史MVP、退役球衣、名人堂、球员卡个人获奖次数；获奖次数与每年的逐条获奖记录不是同一种数据。
- **可能的数据不一致**：2019旧版MyLEAGUE有玩家抱怨总决赛MVP没有出现在球员奖项历史，可能还影响HOF解释（SRC-0186）；不能推广为PC22肯定有此Bug，重要的是不同显示页彼此核对。

`NBA.com`真实NBA历史奖项**不能直接写进游戏当前赛季**。如果游戏模拟的2022赛季MVP不是现实2022的获奖者，原生游戏赛果是本存档权威事实；现实荣誉只可归为历史对照参考，不应覆盖 `GAME_AWARD`。

供未来模型使用的最小事实：`save_id`、`season_id`、`award_type`、`subject_kind`、`game_player_id / team_id / coach_id`、`display_name`、`selection_rank / all_league_team`（若适用）、`awarded_at_phase`、`source_menu`、`observed_batch`、`native_history_readback_status`。身份和时间字段不得缺省成“真实NBA同姓名人物”。

## 9. 纪录与联盟历史：显示页、事件、统计三份证据分别保存

2022-10用户在 NBA2k 社区表示在 MyNBA/MyLEAGUE 找不到生涯历史得分/助攻/篮板排行榜，有回帖给出 `League News > League History > NBA Records`（SRC-0179）；帖子跨越2K23上市后，**不能据标题直接认证为PC22精准菜单路径**。2023另一玩家描述2K21/23历史纪录视图中的生涯、场均、单赛季和季后赛类别，回复确认部分分类通过手柄切换（SRC-0180）。它是系列历史索引证据，不是PC22全部记录范围的最终列表。

研究分类：
1. 球员**单场**纪录：Regular Season / Playoffs / Finals 与Stat类别必须分开，不能和自然单场Box累计混算。
2. 球员**单季**纪录：季节统计和阈值资格（出场、出手）相关，无法由无逐场来源的“总计”恢复所有单场纪录。
3. 球员**生涯**总量/场均纪录：赛季累计与历史留存、退役和跨存档年数相关；不能用当前单季直接覆盖。
4. **队史与联盟纪录**：当前球队/历史球队身份可能发生迁移、扩张、改名，按游戏自己的franchise/team身份区分。
5. **破纪录新闻/3D庆祝**：是否触发赛场播报、新闻卡及特定动画，是**呈现层事件**；仅有纪录面板≠引擎可输出真实时点事件流。

`record_current_value`、`record_holder`、`record_old_holder`、`category/season_type`、`game_date`、`evidence_game_id`和`record_snapshot_time`分开登记。游戏一旦出现“比分归一化”和赛后Box不一致（R06-A）不可依据某一个字段断言破纪录。记录表是否重启后持久、退休后才刷新、跨选秀轮回是否出现重名克隆均保持`UNKNOWN`。

## 10. 新闻、社交媒体、实力榜与模拟选秀：原生信息≠真实媒体人格

2021-12存在面向**NBA2K22 PC MyLEAGUE**的社区文本替换Mod，作者分别讨论原生`social media`消息、`power rankings`、`mock drafts`栏目、记者姓名、静态话术以及社交媒体发言者随机分配（SRC-0181）。由“Mod修改原生可用文字”可相当确定2K22 PC存在**社交媒体和相关栏目资源/信息框架**；它不证明目标无Mod存档每个栏目目前都可点击，也不证明可以在不改文件时让程序创建任意媒体动态。

不能把这类系统误解成具备自主演化的采访人：
- 游戏显示`social message`、`power ranking`、`draft mock`是可观察**内容候选**，所报道赛果、交易、伤病应和真实游戏来源再核。
- 模组作者明确承认某些文本为可替换模板、发言人分配受游戏硬编码随机机制限制（SRC-0181）；由发言人的文字不能推导原生存在可用于外部Agent的记者心理、可信度或独立谈判API。
- 真正Media Agent/媒体投稿、播报注入、生成新闻和媒体影响球员等均为未来单独立项，**R06-B不开发或规定其人格/价值观**。
- 跨模式边界：`MyCAREER`过场采访、`2K League`电竞赛奖项、`MyTEAM`卡片消息不可直接当 `MyLEAGUE`媒体资源。

最低候选原料：`content_type`、`display_time`、`raw_text`、`visible_speaker`、`linked_team/player/event`（无则null）、`fact_or_opinion`、`original_media_asset / modded`、`game_save/batch`。来自外部媒体的预测属于观点，不应写成原生实际发生的交易。

## 11. 规则变更及历史记录：联盟合法性与“纪元”不是同一层

NBA2K系列MyLEAGUE玩家百科介绍休赛期**Rule Changes**可提案、全队投票、并提供关闭/否决的自定义可能性（SRC-0182），属于跨旧作的机制参考。2020老版玩家给出 `League News→Rule Change History→Active Rules` 的反向检查/禁用路线（SRC-0183）；**只能记作旧版玩家操作路径，不能认证当前PC22同菜单/同效果**。

应把`proposed_rule`（尚未通过）、`accepted_rule`（已投票并生效）、`effective_season`、`history_entry`、`user_veto`与当前规则状态分开记录；规则变化可能改变犯规/回合/季后赛或人数口径，不能未经验证就令历史场均统计跨规则环境同义可比。当前外挂“不限制只交易未来三届”的**世界规则V4**是项目政策，不是游戏原生球队投票结果；R05的旧`+3`执行器仍待独立Codex同步，R06不动代码。

## 12. 历史线的验证边界

本世界可参考现实2022勇士冠军、后来历史选秀产生的乔丹/奥尼尔/科比时代，但NBA2K22原生游戏的实际冠军、季后赛16队、MVP、选秀归属和自然成长**始终由当局的游戏结果决定**。历史重力如需要某些特殊属性或球队调整，必须未来独立列方案、获得玩家逐项明确批准；研究历史资料本身完全不授权任何修改。

旧项目文档`docs/08_TIMELINE_AND_EVOLUTION.md`和`docs/11_HISTORICAL_GRAVITY_AND_REALITY_ENGINE.md`仍包含被顶部声明废弃的“转会后自动觉醒”“固定属性增益”和“强制GM策略”示例；它们**不是现行玩家授权规则**。现行按`docs/26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md`与`config/gameplay_policy.json`执行。不能拿旧数值表重启已撤销玩法。

## 13. 跨领域数据契约和最小认证缺口（非DEV28实现任务）

| 原料组 | 研究已知 | PC22当前存档与DEV28需后续认证 |
|---|---|---|
| Draft Class/历史年份 | 同版开档选择三类、Scouting查看候选；历史届循环是项目规则 | 历史年份覆盖、真实候选ID/槽位、重复克隆、选择生效时点与持久化 |
| League History / Award | 同版用户报告Past MVP、Past Rules、Retired Jerseys | 逐奖项/奖季/人物ID/历年覆盖、HOF路径、运行时/长期持久 |
| NBA / Team Records | 系列有NBA Records菜单/多维记录类别 | 精确PC22本世代菜单、种类、刷新频率、重启后是否保留 |
| Social/Rankings/Mock | PC22 MyLEAGUE文字资源与模组验证栏目族存在 | 原版UI观察、消息生命周期、真实新闻事实/观点/模板识别、来源身份 |
| Rule Changes | 旧MyLEAGUE规则投票/历史操作有证 | 当前PC22合法选项、投票时机、可否关闭及与保存关系 |
| Era rules/presentation | **2K23 PS5/XSX**具有原生MyNBA Eras | PC22没有获得原生Era认证，项目历史纪元只能独立世界线资料化 |

**原生事实、新项目政策、玩家提供的未来历史线对照、外部媒体/现实NBA新闻必须由不同的`source_authority`和`timeline`字段隔离**。归档只存证据原料，不给各角色制定必选策略。

## 14. R06-B完成范围与后续唯一入口

本轮公开研究交付覆盖历史选秀加载、原生/外挂的纪元分层、联盟奖项/荣誉、NBA纪录与队史记录、社交媒体/实力榜/模拟选秀、规则历史与数据缺口；**并未**在目标PC22原版实机重新打开对应菜单，也未校验个人数据的原生内存地址、重启留存、全部枚举/合法值。本轮没有下载并重新发布未经许可的第三方截图，新增原版PC22逐像素认证图证=0。

研究状态：`R06_B_RESEARCH_PUBLISHED_WITH_PC22_UI_AND_HISTORY_GAPS`。下一轮：`R06_C_SEASON_PHASE_ADVANCEMENT_SAVE_PERSISTENCE_RESEARCH`，研究常规赛→交易截止→季后赛→休赛期→选秀→新赛季的阶段/时间、autosave与手动保存、存档覆盖/重启、同GameID逐场数据跨季存留。R06-D最后整合，全程不运行游戏、不开发人格、不自动推进日期。