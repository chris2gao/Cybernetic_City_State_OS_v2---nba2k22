# DEV29 R06-B 新窗口跨会话恢复与研究质量独立审核（2026-10-21）

**结论：跨窗口恢复通过；R06-B研究可以作为已发布初稿保留；须完成一次有界的来源—条目映射修正，才能将其标为“独立审核通过”。R06-C可以并行继续，不要求重开R06-A或全部返工R06-B。**

> 本报告是独立静态审核：已读取GitHub主线R06-A/B攻略、JSON、SOURCES、VIS、PROGRESS、README、记忆与Bootstrap；并抽查[官方2K23 Eras公告](https://newsroom.2k.com/news/rewrite-nba-history-in-nbar-2k23-with-all-new-mynba-features-for-playstation-5-and-xbox-series-xs-consoles)、[NBA2K22 Draft Class指南](https://diamondlobby.com/nba-2k22/how-to-download-a-draft-class-nba/)、[同版2K22 Reddit HOF问答](https://www.reddit.com/r/NBA2k/comments/wbudty)、[PC22媒体文本模组说明](https://www.2kspecialist.net/2021/12/nba-2k22-myleague-social-media-overhaul.html)的网页正文。不是全来源逐篇复验；未连接本地PC游戏、没有运行采集/写入/存档/引擎试验；不授权人格/DEV28开发。

## 1. 跨窗口恢复与工程交付

- **接续正确**：R06-A旧窗口已发布，R06-B实际生成并发布；`PROGRESS.md`顶部唯一当前断点为`R06_C_SEASON_PHASE_ADVANCEMENT_SAVE_PERSISTENCE_RESEARCH`，后续R06-D→R07→FINAL-CODEX。新窗口未重做R06-A。
- **R06-A旧成果只作为恢复背景，不能记到新窗口“新开发工作量”**：`R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json`实际86原生Registry候选（settings49+world37）、118菜单/参数候选（Setup13+Calendar Sim32+3D73），各ID唯一；**本轮运行时读回0、精确PC原版合法值域/完整截图认证0**。研究把静态已注册与实际已采/可执行分开，口径正确。
- **R06-B新窗口实交**：`K10_HISTORY_AWARDS_MEDIA_R06B.md`、`R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json`、SOURCES新增SRC-0174..0186、VIS审计/PROGRESS/README/开发记忆/Bootstrap。JSON实际31条唯一`fields`、13个`sources`、9项`gaps`；31项的`target_pc22_current_value=null`、`pc22_native_read_verified_in_R06B=false`、`project_captured_in_R06B=false`、`gm_queryable_in_R06B=false`；**31是研究候选概念，不是31个PC22已采字段**。
- **最后commit`3d7aa486...`仅包含Bootstrap单文件修改**，其余研究资料在此前独立commit已落主线；“最终main头提交”正确，但不应误解为整个研究均只由该commit修改。
- **职责遵守**：不同年代Game Season / Historic Draft Class / Reference Era分层；原生奖项≠现实NBA历史；PC22媒体文本Mod≠原版可写/媒体人格；不开发新Agent、CodeX执行器，不写游戏。符合项目宗旨。

## 2. 主要抽样证据核对

| 来源 | 本次外部正文可直接证明 | R06-B是否保留正确边界 |
|---|---|---|
| 官方2K23 Eras (SRC-0174) | 2K23 PS5/XSX新MyNBA Eras含1983/1991/2002/Modern | **是**，作为跨版本设计背景，不冒充PC22 |
| DiamondLobby 2K22指南 (SRC-0176) | 初始MyLEAGUE/MyGM三种Draft Class选择与Scouting等操作 | **是**，不能代替当前PC22保存/导入成功验收 |
| Reddit 2K22 HOF讨论 (SRC-0178) | 发帖人称看见Past MVPs、Past Rule Changes、Past Retired Jerseys；HOF路径忘记 | **这四点是**，但其它十类奖项的来源映射有缺陷 |
| 2KSpecialist PC22媒体文本Mod (SRC-0181) | 该Mod描述social media账户、power rankings和mock drafts文本及限制 | **是**，仅说明资源/栏目线索，不能认证无Mod目标存档UI及动态注入能力 |

## 3. 有界修正项（研发质量问题，非整轮失败）

### Q1 / P1 证据映射不充分：`SRC-0178`被作为不相关奖项类别的唯一来源

`R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json`中以下10项`KNOWN_IN_SERIES`均单独指向`SRC-0178`：

`K10.ROOKIE_OF_YEAR`, `K10.DEF_PLAYER_YEAR`, `K10.SIXTH_MAN`, `K10.MOST_IMPROVED`, `K10.COACH_OF_YEAR`, `K10.ALL_NBA`, `K10.ALL_DEFENSIVE`, `K10.ALL_ROOKIE`, `K10.ALL_STAR`, `K10.CHAMPIONS`.

然而SRC-0178 Reddit原帖正文只直接提及**Past MVPs/Rule Changes/Retired Jerseys/HOF**，**不能单凭它证明上述10类具体奖项都有目标NBA2K22可见菜单或已被玩家在该帖观察**。中文攻略§8事实上已经将其列作“系列常见候选、目标PC22未验证”，叙述比JSON的单一引用更加谨慎。

**修正要求（二选一）**：
1. 为确实存在的各类别补充**真正出现该名称/页签/获奖记录**的官方/同版玩家资料，并更新来源ID；或
2. 将其逐项标`RESEARCH_CANDIDATE_UNSOURCED`（或同义`UNVERIFIED`），不能继续指向与该概念不相干的SRC-0178作为认证来源。不要为凑来源数量添模糊链接，不要求现在取得PC22内存值。

该问题是数据谱系和来源规范，不是说这些NBA奖项在2K游戏里一定不存在。

### Q2 / P2 研究概念名称需防止误认原生结构字段

JSON的`fields`31条里，14类为`KNOWN_IN_SERIES`、3类为同版玩家报告、3类为PC22模组间接线索、另有跨版和项目政策；目标PC22这次真实源值/读回/GM可查询均0。**建议在目录说明中进一步强调“feature/field research candidates”**，使R07或Codex不会误将31概念合并为31个原生偏移或数据库列。

其中`worldline.native_eras_feature:false`应明确是当前**项目对2K23 Eras外部参考模式的约定**；如果含义为“已实机证明PC22一定不存在Era相关对象”，则应改为`UNKNOWN/NOT_VERIFIED`，避免用2K23新功能公告代替PC22排除性实机验证。

### Q3 / P2 跨窗口启动说明中的历史指针有过期内容

`docs/game_mechanics/NEW_GPT_WINDOW_BOOTSTRAP.md`仍保留标题“本轮立即执行R01”和末尾“下一轮R02”措辞；虽然最新`PROGRESS.md`的R06-C入口优先且新窗口实际遵守了它，**未来下次重开仍有误启动风险**。应把单一当前恢复入口置顶，写明其余R01/R02只属历史示例，或改写为“动态以PROGRESS为准”；`README.md`下层R06-A条目也留有“下一轮R06-B”的旧文字，最好标历史批次语境。

## 4. 正式独立审核建议

- **跨窗口恢复：通过**。不应责令模型重做R06-A；R06-B文档和机读目录确已交付，符合研究/执行/人格开发边界。
- **R06-B内容：原则上接受已发布初稿，但独立审核状态设`REVIEWED_TARGETED_SOURCE_REPAIR_REQUIRED`**，不是“31个每项已经有相应来源直接验证”的充分研究结案。
- **并行顺序**：R06-C可继续，不因Q1–Q3阻断赛季/存档研究；在R06-D跨域整合或R07能力合并前，必须修正Q1并清晰保留源数据与候选区别。Q2/Q3可同一个小型文档维护回合完成。
- **无需启动Codex/DEV28/Agent系统**，也无需请求用户立即大量截图。保持`PC22 UI/RUNTIME UNKNOWN`，不要擅自以未知填充选项/游戏内存。
