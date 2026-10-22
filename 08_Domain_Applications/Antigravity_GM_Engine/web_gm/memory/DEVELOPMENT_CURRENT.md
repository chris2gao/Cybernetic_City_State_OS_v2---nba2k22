# Web GPT · 开发规划基线当前记忆

## 2026-10-21 完整Native I/O重建蓝图V2（由R系列与现工程推导）

[完整蓝图V2](../../docs/development/NATIVE_GAME_DATA_SYSTEM_RECONSTRUCTION_AND_IO_BLUEPRINT_V2.md)：从R01–R07/DEV系列现有成果推导研发合同，不再从未来角色需求倒推局部字段。以目标NBA2K22 PC实际**所有页面/子页/表格全部列与操作**为覆盖面，回溯完整PLAYER/TEAM/GAME/SEASON/Staff/Stats/Coach/Finance等对象和原生数据生产、索引、Getter、存档/缓存/可能存在的内部数据访问机制，再镜像真实原生结构为统一SQLite实体/关系/时序/页面查询视图，增加经批准游戏动作及效果验证。一个UI表≠一个SQLite物理表，内部SQL数据库未证；不误把外部M0 SQLite当游戏原生SQL。现有PLAYER原始1264字节及55能力+17合同解码、99原生Tendency byte与独立Stats数组/Badge未解，需要完整对象映射。早期`docs/02`的0xDF0与当前0x4F0冲突以原生实测证据判定，不用历史文档覆盖。Codex原FINAL仍由Codex恢复；Flash以后独立完成可复查原生页面/对象家族模块，Codex统一接入，任何实机读写/Schema变更按包授权。此前V1已撤回。

## 2026-10-21 玩家重大方法纠错：原生数据探索必须以游戏页面/数据实体整体为单位

上一版[按用途分组的Native I/O路线V1](../../docs/development/NATIVE_IO_CAPABILITY_EXPANSION_AND_FUTURE_ROLE_FOUNDATION_V1.md)已撤回为`RETRACTED_AS_DEVELOPMENT_PLAN`，旧§2/§6不可派单。用户认为其忽视游戏真实页面表格、数据如何生产/索引/存储/计算/展示以及每个球员的完整信息，不能仅凭将来人格所需偏好零散抓数值。后续开发规划前必须逐页理解NBA2K22 PC本世代MyLEAGUE中全部原生UI/子页/可见表/列/查询过滤与游戏数据关联，以完整PLAYER、GAME/BOX、TEAM等对象图形成原生来源链，再定义数据库视图、Schema与接口，列出未证字段/界面、不得擅称游戏内部SQL引擎已存在。仓库当前`PLAYER raw_struct`1264字节，Profile只登记55能力+17合同并由`player_details`局部投影；倾向Registry和赛季统计在其它布局/数组，不等于完整可消费球员对象。必须完整调查能力/倾向/徽章/资料/统计/合同等。保留真人授权写入与自然成长政策，未授权不扩展真实游戏写入。Codex FINAL-CODEX保持唯一owner，不让Flash半途接管。

## 2026-10-21 玩家下一阶段核心意图：原生游戏能力最大化→独立人格建模

[正式规划文档](../../docs/development/NATIVE_IO_CAPABILITY_EXPANSION_AND_FUTURE_ROLE_FOUNDATION_V1.md)：**先铺设最强可用PC22原生I/O底座，后开发GM/Coach/Player等独立人格系统**。不仅服务当前GM字段，也尽可能发现有意义的比赛动态、完整球员职业/非竞技偏好、人格徽章、Coach/战术、财务/合同、世界及存档信息，以及合法参数/原生效果/AI覆盖/持久性。原生胜利/金钱/忠诚倾向、媒体发言人类徽章等作为未来外部自主角色的**可用事实或经批准行动效果接口**研究，不把字段擅自当无害闲置字节或把外部记忆写到原生能力/徽章。Codex完成当前FINAL-CODEX后再按缺口扩展DEV28；Antigravity Gemini Flash是有能力做独立原生勘探和受限小模块代码开发的工程模型，不限于写报告，Codex复核并集成。当前额度等待期可独立开展边界清楚的只读原生证据小项目，但不改Codex主工作区、不卡主审计。子代理型号未知默认禁用；真实游戏修改和Save仍单独逐项批准。

## 2026-10-21 玩家确立跨模型分工与FINAL-CODEX续作原则（最新）

正式规范：[单一Owner／可复查辅助模块／验收与Flash subagent模型边界](../../docs/development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md)。**不因另一个模型有额度，就移交主模型未完成的工作**；Codex暂停的FINAL-CODEX由Codex恢复。辅助模型只做可独立验收的底层准备（SHA备份、只读采证、最小故障复现/隔离测试），接收者通过hash、schema、受限复现/抽样进行质量核验；需要全面重做说明分工不合格。Antigravity Gemini Flash子代理默认禁用，只有能可靠确认使用与主模型同一具体级别且获明确许可才用，未知则不倚赖subagent结论。

玩家报告：Codex额度中断前产生6份审计辅助脚本、4份中间JSON与`FINAL_CODEX_CAPABILITY_MATRIX_20261021_V1.json`（40族矩阵），尚未交付正式MD。AG-01已关闭（保全清点），AG-01B已关闭（11项SHA一致备份；三份`DRAFT_PENDING_CODEX_REVIEW`初稿）。这些是**用户转述的本地执行结果，并非本窗口已读取/认可完整内容**；不更改正式原生/SQLite/执行成熟度。此前建议Flash代写Codex主报告的分工过宽，**不再继续扩大**。应待Codex额度恢复自行完成FINAL-CODEX，AG-02原生只读取证、AG-03离线复现若由玩家另外触发属于独立辅助任务；DEV28仍待另批。

## 2026-10-21 新开发规划窗口接替与DEV29正式研究结案（最高优先级）

- **已重新读取交接快照、项目六模型宗旨、PROGRESS、共享状态和本CURRENT；旧R07“修复待独立复验”指针正式被下列结论覆盖。** [独立R07复验与DEV29研究结案报告](../../docs/development_reviews/DEV29_R07_TARGETED_INDEPENDENT_RECHECK_AND_DEV29_CLOSURE_20261021.md) PASS。
- 研究状态：`R07_RESEARCH_CLOSED_AFTER_INDEPENDENT_RECHECK` / `DEV29_RESEARCH_CLOSED_WITH_PC22_NATIVE_IO_GAPS`。独立重验694/694唯一、682/682原JSON匹配、10个R01字面主题+2个明确原文章节别名、40组/86锚点、20原R06缺口、R06-B十项无直证奖项、R06-C七项无来源；修复八组查询成熟度未提升当前真实执行/Save证据。**以下旧时间段状态只作历史记录。**
- **下一计划门禁**：仅当玩家明确批准，才准备/派发`FINAL-CODEX`有界、只读、静态工程覆盖对账：R07→真实Native Registry/Profile/DEV14→SQLite/manifest/latest→模型安全查询→既有批准执行范围。其后DEV28 D28-0～D28-5须再分别授权；不得自行开发人格、行为权重、谈判、媒体、角色记忆、场上修改或直接动游戏。
- 另有选秀权V4取消人为三年上限但执行器旧+3未清的**独立授权维护缺口**。六阶段为采集→分析→独立教练（未实现）→独立球员（未实现）→GM→玩家批准后执行；研究知识和工程I/O不等于角色人格。

> [**2026-10-21 长窗口开发规划完整交接**](../../docs/development_snapshots/DEV_PLANNING_WINDOW_HANDOFF_20261021_V1.md)：原开发规划聊天将达长度上限。新窗口先读快照及PROGRESS首节，最新R07状态为研究主体通过、两项定向目录修复已提交待独立复验；不得自动宣布DEV29结案或启动FINAL-CODEX/DEV28。六阶段/世界线/选秀权V4旧+3技术差距/人格独立任务均在快照中。

## 2026-10-21 R07独立审核后两项机读目录定向修正

- 玩家独立审核结论：[R07独立审核](../../docs/development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)主体通过，正式结案须先修A/B。现已提交[修复回执](../../docs/development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)并自检，状态`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`，**等待独立简短复验，不能自行宣布DEV29结案或启动FINAL-CODEX**。
- A：索引PART_01的`R07.0007`与`R07.0010`人工别名已经标出R01指南原§4/§3章节标题与术语，12项manual topic都不是原生机器主键。B：矩阵F21/F22/F23/F26/F27/F32/F39/F40的`model_query_api_status`只表达查询，原执行限制/数据真实性/批次前置条件/世界线规则都分别存储；没有升级任何当前存档原生读取、已发布字段覆盖、受控写入或Save持久认证。
- 已重新读回7卷694条，ID与来源身份唯一，历史10项未证奖项与7项空来源保留；40组86处锚点、R06D 20缺口应继续独立复验；R07文档不开发人格，不授权DEV28或代码执行。项目V4仍取消人为3年Pick规则，旧执行代码+3拒绝是独立授权Codex问题，勿误写为“第4/5届Pick不可查询”。
- 后续窗口从[PROGRESS](../../docs/game_mechanics/PROGRESS.md)第一节恢复；不要重新启动R01–R07研究，也不要把修复提交视为独立审核结论。



## 2026-10-21 R07独立审核：694索引/86锚点合格，2项定向修正待办

[正式独立审核](../../docs/development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)已检查7份R07分卷694条、682源JSON原记录逐条匹配、40功能族及86/86原目录锚点、20继承缺口与77种SRC编号（均有登记）；R06B十项奖项缺源继续正确UNKNOWN，未在R07新验证PC22当前数据或执行。研究主体通过但机读目录状态暂为`R07_REVIEW_TARGETED_CATALOG_REPAIR_REQUIRED`：PART_01的R07.0007与R07.0010为无法用完全原文ID匹配的R01指南人工主题ID，应标别名及章节定位；成熟度矩阵F21/F22/F23/F26/F27/F32/F39/F40在`model_query_api_status`混入执行/政策状态，应独立分类并保持原风险说明。修复后二次有界复核即可正式结案并等待用户授权FINAL-CODEX工程对账；不用重做R系列，不启动DEV28、Codex或Coach/Player人格。


## 2026-10-21 DEV29 R07总目录已发布，等待独立验收

- R06正式独立验收已通过：`R06_RESEARCH_CLOSED_WITH_PC22_NATIVE_RUNTIME_AND_PERSISTENCE_GAPS`；R06-B 10奖项来源修复正式接受，仍是真实外部证据缺口。R07本轮完成[七层证据与40组成熟度指南](../../docs/game_mechanics/guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)、[40组能力矩阵与10组既有生产证据](../../docs/game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)、[694条7卷机读索引总清单](../../docs/game_mechanics/catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)、[R07→DEV28后续证据交接](../../docs/game_mechanics/R07_TO_DEV28_EVIDENCE_HANDOFF.md)。
- **R07状态：`R07_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`**，下一阶段仅等待独立审核/定向修复；审核通过后是否启动FINAL-CODEX或DEV28仍由玩家单独批准。新成果引用原R01–R06研究，不新增SRC/PC22实机UI认证、运行时读回或游戏修改。694条包含候选/指南/静态字段，并非694个验证原生字段；可读取索引为1总清单+7分卷，分卷回读和694身份数量通过。40功能族共86原研究锚点，R07没有逐页复核所有网页语义；引用存在与引用真的支持事实是不同审核层次。
- 当前真实能力仍依基线34/37/38/40/DEV14手册分别判定：历史全量数据来源、SQLite查询和部分教练/批准普通交易执行可用，但实际签约写入、逐场Box/Shot/GameLog、2K22模式标记、完整Save重载、职业/历年纪录均未被R07新认证。V4选秀权旧+3执行守卫由独立Codex维护审批，不阻碍研究封存。
- 最重要规则：DEV29研究游戏原料、DEV28建设I/O基础、Coach/Player/Media未来人格单独立项；原生球员普通Ability/Potential/Badge不可修改，游戏写入和数据采集必须获玩家分别明确触发。权威断点：[PROGRESS](../../docs/game_mechanics/PROGRESS.md)。



## 2026-10-21 DEV29 R06正式独立验收通过，R07 NEXT

已在[独立审核报告](../../docs/development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)确认R06-A/B/C/D研究可结案，状态`R06_RESEARCH_CLOSED_WITH_PC22_NATIVE_RUNTIME_AND_PERSISTENCE_GAPS`。R06D 26关联、20缺口和79/79目录锚点均准确，R06B十类奖项已降级`sources=[]`且Eras平台排除性断言改UNKNOWN；R06C38项中7项无直接来源保留未知。**R07_CROSS_RESEARCH_ROLE_OBSERVABLE_ACTION_EVIDENCE_MATRIX**为研究唯一NEXT；其责任为对已有K01–K12做游戏可读/可选/作用、证据等级与I/O缺口统一矩阵，不是编写Coach/Player/Media人格、模型决策逻辑或启动DEV28。先后各批的发布状态不代表真实PC22界面/运行时读写/存盘已验；选秀权V4旧+3代码阻断依旧另行Codex维护。

## 2026-10-21 R06-D跨领域整合已发布：下一研究候选R07

- DEV29最新研究报告：[R06-D K05/K10/K11跨域中文指南](../../docs/game_mechanics/guides/K05_K10_K11_CROSS_DOMAIN_INTEGRATION_R06D.md)和[26机制关系＋20 PC22资料缺口目录](../../docs/game_mechanics/catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)均已发布。关系ID关联K04/K06/R04B/R05D/R06A/B/C源目录ID并在提交前作存在性检查；**不是26条实机验证因果公式**。20缺口是资料与DEV28未来可参考需求，不是自动授权Codex。
- 本轮未新增SRC/VIS、PC22运行时读回、Save重进、游戏推进、存档/原生球员写入，R06-D为`R06_D_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`。R06-B 10项奖项来源已清空降级、旧Era布尔排他断言已修正，但**审核独立复核尚待结果**。后续`R07_CROSS_RESEARCH_ROLE_OBSERVABLE_ACTION_EVIDENCE_MATRIX`仅整理各角色所需可观察事实/合法选项候选/数据来源、真实技术认证与历史反馈，不能开发人格/角色决策。R07后再单独考虑FINAL-CODEX。
- 所有游戏与操作仍以当前玩家批准为准；V4选秀权世界不再限制3届，但旧+3执行代码维护另立Codex任务。唯一权威研究断点[PROGRESS](../../docs/game_mechanics/PROGRESS.md)。


## 2026-10-21 R06-B独立质量审核定向修复与R06-C研究交付

- 已接受[审核报告](../../docs/development_reviews/DEV29_R06B_CROSS_WINDOW_RESEARCH_QUALITY_REVIEW_20261021.md)发现：SRC-0178只证明Past MVPs/Rule Changes/Retired Jerseys和HOF线索，不支持另10项奖项；已修复R06-B JSON 10项`sources=[]`+RESEARCH_CANDIDATE_UNSOURCED，MVP明确仅指历届MVP菜单。31项明确为机制/信息概念，非内存字段；2K23 Eras不能排他证明PC22没有任何Era对象。Bootstrap/README/PROGRESS更正旧启动指针。**修复已提交、自查，仍待独立质量复核结果**。
- [R06-C K11阶段/存档研究指南](../../docs/game_mechanics/guides/K11_SEASON_SAVE_PERSISTENCE_R06C.md)与[38类机读目录](../../docs/game_mechanics/catalogs/R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json)已发布；来源SRC-0187..0199共13条；同版PC22 Save/Save as使用和故障有个案、OS 2022年有Offseason多存档建议（部分引用旧2K经验）、2K官方证实MyLeague离线可用，持久化、实际原生GameDate、Autosave和跨年GameLog/Box/奖项/交易存留都未实机认证。本轮PC读回/实际游戏推进/存盘操作/新实机截图0。
- **DEV29下一轮唯一恢复指针**：`R06_D_CROSS_DOMAIN_SYNTHESIS_AND_GAPS`，其后R07→FINAL-CODEX。研究只交基础游戏事实/设置/可见操作/机制联动，不写角色人格、交易策略、DEV28基础设施，不触碰真实存档；选秀权V4三年旧代码拒绝仍留独立Codex维护。


## 2026-10-21 DEV29 R系列研究最新交接：R06-B已发布，下一轮R06-C

- 依据[PROGRESS](../../docs/game_mechanics/PROGRESS.md)正式断点：R01–R05全为研究结案（原生UI/运行时缺口保留）；R06-A双引擎/86 Registry候选/118菜单参数候选已发布；本次跨窗恢复已发布[R06-B历史奖项媒体指南](../../docs/game_mechanics/guides/K10_HISTORY_AWARDS_MEDIA_R06B.md)、[31类研究目录](../../docs/game_mechanics/catalogs/R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json)、13条来源SRC-0174..0186并同步图证索引。R06-B状态`R06_B_RESEARCH_PUBLISHED_WITH_PC22_UI_AND_HISTORY_GAPS`，非独立审核批准结案；下一轮唯一入口`R06_C_SEASON_PHASE_ADVANCEMENT_SAVE_PERSISTENCE_RESEARCH`，之后R06-D/R07/FINAL-CODEX。
- R06-B严格区别**原生2021–22起算Game Date/Season**、1984–2020按批准选秀完成推进的**外挂历史Draft Year**、独立参考**历史纪元**。NBA2K23 PS5/XSX原生MyNBA Eras不得当作NBA2K22 PC原生功能；奖项/League News/NBA Records/Social/Power Rankings/Mock Draft/Rule Changes相关报道均按平台与版本分层，大多PC22现存档菜单、运行时值、历史留存仍UNKNOWN。本轮未运行游戏、写内存、启动DEV28/Codex或实现媒体/球员/教练人格。
- **并行独立工程差距**：V4已取消未来仅三届选秀权规则，但交易、计算、执行旧+3拒绝尚未同步；必须由用户单独授权Codex小范围代码/测试，不阻断DEV29研究，不改成新硬五届。


## 2026-10-21 R04审核通过与六独立模型执行轮：研究只提供游戏原料

- R04-A/B/C/D研究交付独立审核已核对：`PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json`实际109条无重复且与主目录109逐条匹配，**72本项目静态Profile+37未映射候选**；109项全部`NO_R04_LIVE_SAVE_CAPTURE`，并非全游戏字段总数/已获真实游戏值。Atlas恰8个用例、来自研究材料，非人格实现；来源到SRC-0113。签约仍`approved_signing_v1_unvalidated`；R04可研究结案，PC22字段/内存仍有明确缺口。
- 玩家重新确认每轮外挂游戏流程为**采集模型→数据分析模型→独立教练模型→独立球员模型→GM模型→最终汇总交执行模型**，触发点一般新赛季/月度/交易截止日前一天/季后赛每轮/休赛期。**Coach和Player人格系统没有开发，主要已有GM人格系统**。DEV29只调查2K20–23尤其PC22的游戏信息、动态数据、全部可设置项、玩法与联动，为未来模型提供原料；DEV28只完成这些原料的读取/查询/合法受控执行，不创建角色人格、谈判/拒绝算法、媒体、调度。真实玩家写入批准与游戏权威保持不变。
- 已在[权威六阶段流程与研究职责边界](../../docs/game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)及DEV29 V3/R04专项/Atlas/DEV28/AGENTS/PROGRESS/README更正此前过度设计角色行为的表述。R05 NEXT只做市场财务合同、员工、球探和选秀游戏原料研究，不顺手开发Agent。

## 2026-10-20 DEV29 V3：玩家转向自主多智能体篮球世界，R04球员全领域研究

- 玩家明确目标不是优化器式GM，而是**让GM、教练、球员、媒体形成有独立目标/记忆/偏好与谈判拒绝权的模型角色**，在NBA2K22真实比赛/职业合同/世界事件中主动试错、根据反馈涌现。不同Agent有不同信息，BPTI与历史篮球哲学是可参考建议而非必执行条款。
- 已在main新增[DEV29 V3](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)与[R04 Player Full Profile/Agency研究任务书](../../docs/development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)。完整球员个人档案/属性/倾向/徽章/人格徽章/身体部位耐久/伤病与疲劳/Play for Win/Financial Security/Loyalty/合同角色/长程职业动机都必须研究。**R01-A/B/C/D已经结案，R02依然NEXT**；R03研究训练健康通用机制，新增R04研究全量球员信息与自主行为，原经营、世界、整合顺延R05–R07，网页GPT各轮发文到game_mechanics，FINAL-CODEX仍最后。
- 未来DEV28需面向多角色提供可读事实/合法选项/谁能提出谁能拒绝/已认证原生执行与反馈。**模拟球员同意≠用户真实游戏写入授权**；职业长程记忆/关系/目标优先外部SQLite。玩家提出可能以废弃的原生参数作为外挂人格持久化空间：未认证与未单项批准前**不允许重用**，免得破坏原生球员AI、比赛、合同、存档。Ability/Potential/Badge普通运营禁直改仍有效。
- 社区依据：2K22 OS Attention to Detail球员研究明确列Play for Win/Financial Security/Loyalty和个体部位耐久、人格徽章，开发次世代官方说明亦涵盖自主训练/员工健康；是跨平台机制线索而非PC22原生全字段认证。研究任务本身不开发人格Agent/不进行游戏修改。

## 2026-10-20 DEV29 V2组织改为网页GPT多轮攻略研究，PR #12已合并

- GH核对PR #12已`CLOSED/MERGED`、原head`ded900c`，原“冲突处理中/等待合并”已过期。**DEV29 V2**取代V1具体前期执行组织：[规划](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)，[游戏机制资料库](../../docs/game_mechanics/README.md)，[研究进度](../../docs/game_mechanics/PROGRESS.md)，[新研究窗口启动提示词](../../docs/game_mechanics/NEW_GPT_WINDOW_BOOTSTRAP.md)。
- 主责是新网页GPT开发规划研究窗口，分R01–R06多轮研究NBA2K20–23终极联盟完整机制、社区/官方/游戏攻略及网页截图；每轮在GitHub提交中文机制卡、逐场动态数据/全部静态可选项/相互作用、`SOURCES`/图证索引/断点PROGRESS。**Codex不在研究阶段做大量资料搜集**，只在研究结束做一次FINAL-CODEX源/图/机器索引完整性与现有Registry/M0/DEV14/SQLite对应的工程收尾，形成DEV28具体缺口。
- 研究允许图片来源链接、分批参考必要的游戏截图；第三方截图版权许可不明者默认只保存URL和可见证据，不把带水印/未获授权图批量复制进公开仓库。用户可提供游戏截图。正式NBA2K22 PC原生地址/执行状态另行认证，原游戏修改仍需玩家逐项批准。

## 2026-10-20 玩家调整顺序：DEV29全系列游戏机制知识先于DEV28开发

- 玩家要求首先系统理解**NBA2K20/21/22/23系列与终极联盟游戏机制、菜单、全部可见数据、全部可选设置、最佳玩家攻略**，再推进DEV28的原生I/O全透明开发。指出原全量采集连逐场比赛/Box Score及高级指标基础都没准备好，先找内存→后定数据需求的开发方法必须改为**GM业务决策证据需求→游戏全域功能目录→来源/采集/查询/执行差距审计→Codex/Antigravity针对性补齐**。
- 新权威[DEV29/R0全系列玩法知识前置规划](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V1.md)和已更新[DEV28开头的前置门槛](../../docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)。程序包按R0-A官方/社区百科与菜单图谱、R0-B GM和Analytics反向证据设计、R0-C Codex现有工程能力矩阵，**全部在D28-0之前**。这是研究计划已发布，不是所有机制已研究完成。
- 所有模型共用`FRANCHISE_MECHANICS_ATLAS`、`FEATURE_DATA_CONTROL_MATRIX`、`GM_DECISION_TO_EVIDENCE_MATRIX`，按照游戏版本/模式、官方与社区来源、真实菜单/内存、现行采集与GM可用性分层；缺少Game Logs不可做逐场因果分析。次世代MyNBA/2K23 Eras可参考机制，不得直接冒充PC22原生API。PR #12尚在Codex处理冲突，不因计划修改它的分支；不新开实际开发、不合并PR或修改游戏。

## 2026-10-20 PR #12玩家批准审查修复与DEV28全透明开发路线

- 玩家明确授权PR #12/F1–F4**局部修复**，需Codex在原Draft分支完成：蓝图与B5演化修订相符、同存档代次/分支历史引用、B4可执行native动作限制不可误封正常外部MARKET、portfolio只选择VIABLE_CANDIDATE内部动作；直接关联小范围测试后结束任务，合并及V4启用独立授权。
- 新的后续开发主计划：[DEV28 GM Native I/O透明、动态事实完整性、战术手册真实绑定与执行闭环](../../docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)。分D28-0～D28-5：能力缺口盘点、全部Book/Play目录及Coach→Book/slot生命周期修复、世界/教练/个人防守/倾向/训练合法候选枚举与游戏文义、DEV24逐场/球员/球队/身体状态、GM查询/提案/DEV14执行/读回、跨模块可用性报告。用户想让GM知道全部**当前游戏实有的**选择项和真实动态事实，而不是返回生裸值。
- `team_book()`在DEV27的867fe85只修了末尾独立Playbook后缀的严格名称匹配；用户认为未彻底修复。DEV23实机三队204槽/148非零/111可命名/37未知；原生PlayType、实际发起/受益人和3D使用尚缺。D28-1查全部30队本队已加载Book名单、原生真实引用/Coach当前BookID、CRC及意义，用批准的**两次动作**技术归位→重新来源采集→本队槽写入/读回；不做自由跨队改BookID，正常GM仍改本队书槽。
- Antigravity继续找原生地址/游戏选项/静态战术名称类型及DEV24动态观测源，Codex唯一接现有M0/Registry/DEV14。外部GM虚拟交易/签约/选秀业务不变，历史新秀Pot遮蔽及玩家批准保留；不存在的原生比赛/疲劳值显示NOT_OBSERVED。**DEV28计划写入并不批准实际游戏修改，也不应污染PR #12范围。**

## 2026-10-20 M4系统自我进化交付索引

Codex窗口②已从合并M3后的main实现DEV20/M4，状态M4_ENGINEERING_MAIN_MERGED / GM_V4_NOT_ENABLED，PR #7经审核小修正后按玩家批准合入main（`c51fa36080ed39c8305635f1cb4363128475fdf0`）；正式本地main已同步。本次仅定向test_02通过，未扩大测试或处理Issue #6。玩家下次主动触发开发规划时，先读[工程问题CURRENT](../../web_gm/development_feedback/CURRENT.md)、[准备状态](../../web_gm/development_feedback/readiness.json)及必要的每项详情/原证据，再提出最小研究/实现范围、成本和任务书草案，等待玩家批准；不把候选当作已立项任务。长期Codex实态查[docs34](../../docs/34_BASELINE_CURRENT_STATE.md)、[M4验收](../../docs/development_reviews/M4_SYSTEM_EVOLUTION_IMPLEMENTATION_AND_ACCEPTANCE.md)。Issue #6、BPTI、季后赛采集与双引擎校准均仍DEFERRED；M4只管理工程需求，不评价GM篮球经营效果或实现校准器。真实30队UNASSESSED、Web/已脱敏生产消费待证、V3生效。本条仅开发交接指针，不启动后续任务或游戏。

## 2026-10-20 Codex主线交付指针

DEV14 PR #5已合入main（570419a/f68d75d）；M3窗口②以82083b5接收，M3A/M3B+M3-T工程及本轮8项最小验收已完成，原PR #4已按玩家批准合入main（`504a4c0656bad0e890c3783c89c656fca5b2e647`），正式本地工作区已同步，未追加测试或运行。长期Codex状态仍以[docs34](../../docs/34_BASELINE_CURRENT_STATE.md)为准，具体接口、证据与完整目录脱敏待办见[M3-T交付](../../docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)、[GM手册](../manuals/GM_M3_TACTICAL_WORKBENCH.md)。本条仅作开发索引；V3生效、V4未启用、真实30队UNASSESSED，不代表正式经营或新数据。

## 2026-10-19 DEV14 V1.1工程交付索引

Codex独立分支实现A/B/C/D：统一NativeFieldRegistry、每档控制SQLite、稀疏stage/批准绑定执行/恢复、同批全量来源/M0分域查询/离线对账、最多四档唯一ACTIVE与归档后新generation。见[运行手册](../../docs/DEV14_STATE_IO_RUNBOOK.md)、[实际验收](../../docs/development_reviews/DEV14_ACCEPTANCE.md)、[工程会话记录](development/sessions/20261019_dev14_state_io_engineering.md)。未合并前不称main部署；原生证据继承自现有与Antigravity玩家反馈，本轮仅合成/静态验证，无正式采集、游戏写入、GM V4切换或M3合并。

## 2026-10-18 玩家最新开发职责：历史线人物定制单独立项，与GM球队经营分离

玩家明确将**符合历史年代逻辑的当前联盟人物特殊能力/属性定制**放到**开发规划模型**，与网页GM五轮以上30队赢球经营/正常交易/教练修改隔离。正式交接：[DEV_HISTORY_GRAVITY_SEPARATION_20261018_V1](../../docs/development_tasks/DEV_20261018_HISTORY_GRAVITY_GM_BOUNDARY_V1.md)。GM最新六维经营：[GM_DATA_TO_DECISION_V1](../manuals/GM_DATA_TO_DECISION_STANDARD_V1.md)。

- 开发基线任务仅是机制/方法/人物同一性/时代参考/数值边界/原值→拟议值/短长期影响及回滚与安全执行器的**独立规划**；按已批准规则2026游戏年开始模拟1984乔丹选秀四年后的历史年代，历史选秀1984–2020循环依玩家确认，不自动推进或强制历史赛果。
- 当前**没有批准任何历史人物能力改动**；文档26记载历史重力受控属性执行器尚未实现，旧`growth_engine`/通用`modifier`停用。不得因职责移交就启动开发执行/修改游戏或数据库。具体专项由玩家另行明确触发，再设计、审计、逐项批准、交Codex受控执行。
- GM只负责本局真实的30队球员评估、制服组/战术、市场交易签约，以符合历史发展逻辑为参考而非硬改属性；正常交易授权永不包含历史重力改属性。
- **员工变化同样存在开发/GM职责界面**：M02来源已验证30队×8岗位员工关联可读，员工产生的PC版游戏属性/比赛影响和完整雇佣/岗位变更写回未认证。GM在六维评价中可提出业务上换帅/换员工的研究候选；只有玩家未来触发开发专项，开发基线再核验真正有效字段、双向变更与恢复路径。次世代MySTAFF的17人四部门与加成不可误导PC来源。
- 训练与个人分钟锁定在本项目明确交由游戏AI，不建立外挂开发任务。



- role: WEB_GPT_DEVELOPMENT
- memory_version: 4
- last_reviewed: 2026-10-18
- state: COACHING_CODE_MAIN_DEPLOYED_FULL_CAPTURE_FIRST_PRODUCTION_PENDING
- linked_codex_state: `docs/34_BASELINE_CURRENT_STATE.md`（**Codex 状态索引，不在此复制更新**）

DEV07 Codex 已在 PR#1 分支继续实施 V2，不再处于代码未开始状态。当前证据、字段门槛和剩余工作只读 [Codex 状态34](../../docs/34_BASELINE_CURRENT_STATE.md)与[集成报告](../../docs/development_reviews/DEV_20261017_07_COACHING_INTEGRATION_REPORT.md)。已建立 [GM 操作手册](../manuals/GM_COACHING_OPERATIONS.md)及 [Codex 执行手册](../../docs/40_COACHING_EXECUTION_RUNBOOK.md)。当前19项默认字段接口已实现，Tempo按玩家明确选择开放原生raw并标明界面含义未知；PR #1已于2026-10-18通过玩家审查并合并main（2509b3b），本地已同步；真实生产采集和数据发布未运行，不能把代码部署当成数据发布成功。

玩家最新修正：正式脚本顺序执行；不要把少量验收样本当作允许值白名单。BenchDepth取消9–10人为上限，由GM读取阵容后选择人数；四Freelance按完整原生枚举/布局及有序codec提供受控接口，不因未重复菜单检查而禁用，也不冒充实际UI已验证。当前19项默认字段可提案/受控执行；玩家明确开放原生Tempo并保留界面含义未知，结合其他教练观测值选择目标，不增加测试样本限制。原生类型/枚举、来源身份、具体批准和条件恢复保护保留。

## 已知工程事实

- GM v1.0 M1–M6 的 Python 核心、命令行分析准备、提案协议已由 Codex 实现；v2 双方谈判、v3 正式王朝经营仍未全部实现。
- 最新来源已包括 30 队赛季胜负/累计统计、球员 55 项能力、部分球员赛季表现、员工关联、简单选秀权；玩家将薪资采集需求限定为当前大名单工资。
- 上一次 Web GPT 的 30 队独立量化分析已写到 `docs/gm_analysis/`；这是网页分析角色，不应每轮交给 Codex 重新做。
- 现有 Codex 数据采集/开发基线为 `docs/32`、`docs/33`，它们与本 `web_gm/baselines/DEVELOPMENT_BASELINE.md` **分属不同执行角色**。

## 待做（由玩家按需触发）

- 维护 Web GPT 需求文档与 Codex 工程开发任务书：例如 GM v2 交易谈判、多模型交接、对话基线协议的后续自动化可行性；**单来源生产更新已被玩家取消，不再开发**。
- 新开发需求发生时先核对仓库当前代码、相关测试与 commit；不要根据之前工作总结宣称新功能已有生产能力。
- 完成一次开发任务后保存 `development/sessions/<run_id>.md`，更新此索引并报告实际变更/交接文件/提交。

## 边界

本窗口的默认任务是**研发设计、Codex 任务书与验收**，不是 Codex 本地脚本执行窗口；不默认修改生产源码/采集真实内存/发布游戏数据，不提交未经授权的正式 GM 战略和游戏执行变化。

## 最近已完成的开发规划/文档任务

- [2026-10-17 三份 Web GPT 专用基线及记忆协议建立](development/sessions/20261017_web_gpt_three_baselines_v1.md) — `COMPLETED`；Web GPT GM / DEVELOPMENT / ANALYTICS 三种基线现已放在 `web_gm/baselines/`，角色协议 `docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`，Codex 的 docs/32–34 保持独立。
- 此次成果仅建立文档与项目职责，并未自动生成聊天窗口、启动 GM、运行采集或写入游戏。

## 当前开发交接：DEV-20261017-04 休赛期自由球员签约（规划完成、代码待做）

- 状态：`SPEC_PUBLISHED_AWAITING_CODEX_P0`。此项为研发任务书，不构成正式赛季签约许可。
- 入口：[Codex 任务书](../../docs/development_tasks/DEV_20261017_04_OFFSEASON_FREE_AGENCY_V1.md)，[本次规划归档](development/sessions/20261017_offseason_free_agency_plan_v1.md)。
- 任务书创建提交：`3ff1ff53e50084390092402462efa7e2600c8e3a`。
- 顺序：P0休赛期安全节点及原生AI自动签约调研 → P1 30队只读候选池/报价/母队竞价 → P2安全签约执行器测试 → P3全闭环跨赛季实机验收。
- 硬阻塞：没有经过验证的完整签约执行器/自由球员权属/原生AI控制。2021–22薪资规则不得代替以后年份；大名单工资帽差额非真实签约空间。正常球员能力编辑禁止；玩家每次具体签约需要独立批准。

## 2026-10-17 教练战术对模拟比赛影响：历史评估（赛前A/B建议已被V2规则覆盖）

- 状态：`SIM_TACTICS_ASSESSMENT_ONLY`，不代表Code已开发或允许写入正式存档。
- [评估报告](../../docs/development_reviews/DEV_20261017_COACH_TACTICS_SIMULATION_ASSESSMENT_V1.md)；[会话归档](development/sessions/20261017_coach_tactics_simulation_assessment_v1.md)，报告提交`b599e17`。
- 结论：优先验证NBA2K22 PC普通快速模拟的Sim Points of Emphasis/教练体系与传统球队POE、战术手册是否分路生效；有效才提供GM season tactic proposals、玩家批准及Codex受控执行。不开发未经验证的实时模拟教练AI。
- 技术风险：`StrategyManager.set_team_strategy`仅uint8/回读；`poe_on_ball`枚举冲突；还需真实UI字段↔内存映射、Sim效应对照、AI覆盖与存档持久性证据。次世代主机Conditional Coaching不能视为PC功能。

## 当前交接：DEV-20261017-05 教练战术定位、条件开发、玩家月度验证 V2

- 状态：`MEMORY_DISCOVERY_THEN_IMPLEMENT / GAMEPLAY_TEST_DEFERRED_TO_PLAYER_MONTH_END`。玩家最新要求**Codex先定位内存、确认安全后直接开发；不要求Codex先跑20/100场对照模拟**。开发期只需合法枚举、对象身份、隔离存档读写/恢复/重启等最小技术安全检查。
- [V2主任务书](../../docs/development_tasks/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md)（原V1同路径覆盖更新）；[V2变更历史归档](development/sessions/20261017_coaching_month_end_validation_change_v2.md)。任务书最后更新提交`d5702d759a14285b76def883b7ff2306ff345b3a`。
- 交付：Codex在确认部分字段可安全实现后，直接编写GM读取/提案及**受控**执行器，提交真实代码/必要技术验证/字段矩阵。技术实现完成时**不得声明模拟比赛效果得到证明**，效果标`SIM_EFFECT_PENDING_PLAYER_MONTH`。
- 下一步游戏内测试归**玩家**：具体战术方案须独立审批并由执行端受控落地，玩家推进一个游戏月后分别触发比赛来源更新→Web GPT ANALYTICS分析→同赛季GM决策复核。游戏效果属于首月观察，不自动证明因果关系。
- 月度计算仅在同存档同赛季同统计口径且游戏日期单调前进时：`ΔW`/`ΔL`/`ΔG`以及累计总量差计算本月指标，不能对赛季累计场均做直接相减；已知只有赛季累计，不假称逐场明细存在。
- 持续保持游戏写入审批、不得改普通球员能力/潜力/倾向/徽章、不得偷改全联盟Simulation Sliders，也不得因开发完成自动开始采集、GM回合或正式存档执行。仍未知：比赛内CPU AI是否覆盖、普通快速模拟具体读取哪些战术字段，等实际反馈。

## 最新交接：DEV-20261017-06 NBA2K22 原生教练战术受控执行器实施

- 状态：`IMPLEMENTATION_TASK_PUBLISHED_AWAITING_CODEX`，用户转交Codex原生代码+进程只读调研并允许直接开发；截至此处无正式写入和赛果效果实测。用户原话“可以开发”不等于对任何30队具体战术方案的正式游戏写入批准。
- [Codex正式开发任务书](../../docs/development_tasks/DEV_20261017_06_COACHING_IMPLEMENTATION_V1.md)（创建提交 `dd561e9e5455b118ff01e304689cd6460b519d6b`）；[玩家转发只读调研](../../docs/development_reviews/DEV_20261017_05_COACHING_READONLY_HANDOFF.md)；[开发规划归档](development/sessions/20261017_coaching_native_implementation_handoff_v1.md)。
- **高危缺口：旧TEAM+0xEB2不能再用于策略写入！** `src/strategy_manager.py`的旧setter和`src/bootstrap_new_game.py`初始30队批量调用必须先停用/迁移，不能把旧0..6枚举自动转换为新POE值；票价功能独立保留。
- 新默认教练六POE为`COACHDATA+0x13C`的32bit共享位域，six×5bit，bits30..31保留；精确enum列在实施任务书。Sim系列另在教练`+0xF4`附近共享位域，尚缺完整bit掩码。查实时code再允许写。
- 对手方案：`FRANCHISE_GAMEPLAN_MANAGER`每队35槽、29条有效他队方案，本局报告总870条，Gameplan=0x370/条。原生`IsInUse=0`全未启用，启用语义未知则只读/提案，不得声称写入会生效；Playbook当前加载84本只用于该次读数，不可固定上限。
- Codex应先重新实测结构、修旧入口，再做可行模块的GM只读+提案和执行器、必要技术安全检查与Github交付；未完成战术作用验证时标`SIM_EFFECT_PENDING_PLAYER_MONTH`，不要求Codex事先模拟20/100场。
- **玩家实效验收**：具体GM战术方案→玩家批准→Codex执行回执→玩家游戏正常推进一个月→玩家另行触发数据采集→Web GPT ANALYTICS用同存档同赛季累计值计算月度`ΔW/ΔL`及可观测统计差→GM评估。不得自动串联。
- 证据边界：上面的新原生地址/位域依据玩家转交的Codex文本，当前Web GPT未取得实机源码/日志，因此属于`USER_RELAYED_CODEX_FINDINGS_NOT_INDEPENDENTLY_RETESTED`，不是已验收业务执行器。

## 最新交接：DEV-20261017-07 GM教练系统30队批次/来源/双手册

- 状态：`COACHING_CLOSED_LOOP_SPEC_PUBLISHED_AWAITING_CODEX`，**以下为已过期的历史规划状态；当前代码与合并状态以本页顶部及状态34为准**。用户不再要求“快速模拟胜率效果验证”；教练机制完成以工程闭环为准。
- [Codex最终完善任务书](../../docs/development_tasks/DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V1.md)（首次提交`1aa5c2bacff2aaab80f4c7bb6c2b4c8c00f40d34`）；[本次范围归档](development/sessions/20261017_coaching_closed_loop_final_scope_v1.md)；既有[PR #1](https://github.com/chris2gao/nba2k22-gm-engine/pull/1)，已上传代码HEAD `5daeed8dc0001b5052dce1cfc97d6c22ee9317c3`。
- 基础版必须：**六项默认POE正式读写 + 1–30队整批预验证/逻辑事务/失败条件恢复 + 用户触发常规采集自动包含COACHDATA战术来源入SQLite与GitHub发布JSON + 两份正式角色手册**（`web_gm/manuals/GM_COACHING_OPERATIONS.md`、`docs/40_COACHING_EXECUTION_RUNBOOK.md`）并更新GM/执行基线入口。所有内容必须有真实代码/接口/回归集成测试。
- 主教练余18项：5Sim、2体系、1战术本（编码可用，未生产验收）；6教练滑块、4Freelance（只读）。玩家请求详细查看，**尚未批准统一转为可写**；单一对手Gameplan/18项具体防守/轮换保持只读。每字段独立认证后再提升production_enabled。
- `src/gm_core/coverage.py`旧`team_state.poe_*`应明确脱钩，改以新增`coaching_tactics`来源让GM读新原生字段；仍从现有`published/index.json→latest.json→batch_path`，无后台触发，不造第二个同步入口。仅原数据采集有`-Publish`才真正推送GitHub。
- 跨30队内存不存在硬件物理原子写；要求事前全部核验、批次批准、一致性验证、fsync预像日志、尽力条件rollback与`PARTIAL_UNRECOVERED`明确异常，绝不谎称所有失败能无损回滚。
- 开发完成后需要GM/执行模型每次分别按玩家批准的具体提案/批次工作；绝不代替用户批准真实游戏的30队修改。不再因未跑一个游戏月或不知模拟作用而阻止教练系统工程验收。

## 当前最高优先级：DEV-20261017-07 V2 19项球队级教练战术＋单对手整体防守

- 状态：`COACHING_V2_SPEC_PUBLISHED_AWAITING_CODEX`；[最新V2正式任务书](../../docs/development_tasks/DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V2.md)（`3651e1d440d1fdba43a346cb8228b867889e29af`）；[完整上下文](development/sessions/20261017_coaching_scope_v2_19_plus_opponent_defense.md)。**前一条DEV07 V1“只有六POE是必需/其它18可选、指定对手防守以后再做”已作废**。PR#1现有六POE代码不代表V2已完成。
- 最新明确业务：五个`Sim*`仅玩家模拟比赛使用，GM不操作；球队默认需**19项**：六POE＋`PreferredSystem/ActiveSystem`＋`PlaybookID`＋六教练滑块`BenchDepth/RunPlayTendency/ZoneUsage/BenchUtilization/Tempo/HelpDefense`＋按1→4优先序配置的四个`FreelanceType`。主教练HEAD_COACH的设置映射到所属球队默认打法，不是全联盟共同slider。
- 用户当前PC UI报告六滑块可取1–100，但旧社区资料有0–100且BenchDepth具体单位存疑；Codex最小读/单项UI对照确定合法显示值→raw关系。可只读参考Kerr/Spoelstra/Popovich/Thibodeau等当前存档主教练值，不得捏造数值。
- 另一必需模块：**指定对手页面的整体防守理念**（原生GAMEPLAN8byte、18项候选），与单个对手的独立覆盖相关，不能推成全局。当前逐项防守读取器带`matchup_id/defender_id`，须最小差分确认“整体/All”对应owner/条目和`IsInUse`/继承/取消；若无法确认只能BLOCKED，不能误写个人对位或声称完整实现。
- V2闭环仍必须：30队全批预验证/受控写入/条件恢复＋玩家正常采集自动含战术源SQLite/JSON/GitHub发布＋GM/执行两本实用手册和基线接入。**不用快模拟比赛效果或大量无意义保存重启测试**，只做最小必要安全验证。游戏正式写入每批另需玩家批准。

## 2026-10-18 最新决策：所有游戏新数据更新只走全量，教练源不另开开发分支

- **这是最新范围裁定，优先于本文件中的历史规划段落**。用户已与Codex讨论并采纳全量刷新：脚本化完成、数据量不大，每次都更新所有已验证来源。正式数据更新唯一入口仍是`scripts/run_data_update.ps1`的`full_verified_v1`；不开发`COACHING_ONLY`、单来源/单队快照、跨不同来源日期组合发布、增量同步或独立教练latest。
- [DEV08全量教练源首次生产启用规划](../../docs/development_tasks/DEV_20261018_08_COACHING_FULL_REFRESH_FIRST_PRODUCTION_V1.md)已写入main（首次提交`d0da3ea34ec8d2e4b07aab638d66e4647caf2db7`）。该计划**不是研发新特性**：SQLite`coaching_source_captures/coaching_team_observations`、同RO会话采集与审计、19默认字段、29个对手整体防守、JSON`coaching/`、GM按batch读取均已随DEV07进入main，首次真实生产采集/上传目前尚无证据。
- 当前唯一待做的教练来源数据任务：由玩家下次**明确触发完整全量采集及按需-Publish**；Codex报告最新source coverage必须为`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`、30队/19字段/29对手记录、SQLite、manifest/latest与GM源同批一致。任何失败只修该次真实阻断，不预开发单源采集，也不做比赛或反复保存重启验收。
- GM决定→玩家批准→执行模型内存写入和回读→玩家自行游戏/保存；下一次只有**玩家触发全量更新**后，GM才能从新已发布批次读到修改后的教练值。执行回执不能直接覆盖SQLite原始观察，也不自动采集/发布。
- 已同步最新`AGENTS.md`、Codex开发/数据基线32、33、状态34、数据runbook27、source registry24及GM教练手册的full-only规则。历史旧任务中的“单来源优先待办”作废。

## 2026-10-18 DEV09：NBA2K22 PC 当前终极联盟CPU滑块页 + MC主宰/佳得乐研究

- 已编写[DEV09三专项只读研发任务](../../docs/development_tasks/DEV_20261018_09_MC_MOVEMENT_TAKEOVER_GATORADE_RESEARCH_V1.md)；用户将其转交Codex：当前游戏位于终极联盟测试存档**CPU持球速度与持球加速度页面**，要优先就地只读记录画面原值及当前内存差分，找真正Movement字段，并核查MC/终极联盟底层共用但实际settings实例可能不同、HOF/CPU vs USER差异。
- 玩家已排除PC帧率和整体运行环境问题；中锋低持球属性导致的局部整套运球/篮球落地动作过慢，目标是两项Min的全局调整可行性，不准写普通球员能力，不动Game Speed/HOF。旧`slider_manager.py`静态地址及“拟真一键写入”不可信/会动其它设置，禁止本次直接使用。
- 另研究当前代MC**主宰类型**（须与充能/比赛激活分离）和Gatorade消耗品/每周锻炼额外体力槽/Gym Rat永久状态；先只读定位，服务端权益不可假造。**本次未批准任何游戏内存写入**；必要的GUI单值差分由玩家操作或在另行获准后于测试存档最小操作并恢复。
- [本次开发归档](development/sessions/20261018_mc_movement_takeover_gatorade_research_handoff.md)。研究不自动触发正式全量采集、GM回合或任何正式局写入。

## 2026-10-18 DEV10 — GM V4 phased development plan

- Master plan: `docs/development_tasks/DEV_20261018_10_GM_V4_FOUNDATION_DECISION_OBSERVABILITY_MASTER_PLAN_V1.md` (M0-M4). FIRST Codex delivery is M0 only: published data consumability, small queryable staff/player exports, consumer evidence and cash field semantics; no game writes.
- Observed issue: M02 staff.json manifest says 2,728,888 bytes / 1,458 employees, but current Web GitHub fetch returns empty content despite file SHA; Web GM cannot infer access from source audit. Large player catalogue and individual roster accessibility require live consumer tests separately.
- Financial anomaly: CLE/NOP/UTA/ORL cash near 2^32; signed 32-bit interpretations are unverified hypotheses, never silently replace raw values. `budget`, `cash`, `payroll`, `total_salary` not interchangeable.
- M1 financial & current-gen rules; M2 basketball/franchise knowledge and 30 team memory; M3 ANALYTICS decision packet plus five internal GM stages in one user-triggered decision task; M4 lifecycle feedback, issue inbox, and representative pilots. Feedback produced by normal player-triggered stages, never by unattended background work.
- Existing GM V3 five-interaction protocol stays effective until the new V4 contract passes real Web model verification and the player approves switching. Only the plan has been created; no implementation or game update is claimed.

## 2026-10-18 DEV10 V2 — Web GM / ANALYTICS / DEVELOPMENT SQLite-first

- Latest authoritative task: [DEV10 V2 SQLite-first master plan](../../docs/development_tasks/DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md). User offered authorized local terminal access for all three Web GPT roles. This access must be verified in each real Web chat; it has NOT been proven by the planning phase.
- **V2 overrides V1 M0 JSON paging/sharding**. Continue the existing full_verified_v1 capture and paired SQLite databases. Build immutable same-batch read-only local snapshots and a parameterized, limit-bound `gm_data_query.py` CLI for staff, active roster, global player pool, coaching, finance and picks. Only return small bounded rows/aggregates, not whole 2.7MB staff.json or 3383-model table. JSON remains for small cross-model GitHub handoffs and current publication compatibility.
- Strict roles: Web GPT facts SQLite read-only; Codex writes certified source only on authorized full capture; derived analytics/strategic feedback in separately writable `gm_workbench.sqlite` via controlled writers (M3/M4); no Web SQL access may directly edit source DB or game memory. Bind both DBs to career/batch/snapshot/data timestamp and GitHub publication status.
- M0 still includes unverified unsigned-like cash anomalies and original financial field semantic audit. First Codex delivery covers M0 only; requires actual read-only CLI validation by WEB_ANALYTICS, WEB_GM and WEB_DEVELOPMENT before `M0_CONSUMER_ACCEPTED`. Tool availability is not proof of machine connectivity. M1-M4 retained, with SQLite query/sidecar interfaces instead of enormous derived JSON files. Feedback remains player-triggered.
- Original [DEV10 V1 plan](../../docs/development_tasks/DEV_20261018_10_GM_V4_FOUNDATION_DECISION_OBSERVABILITY_MASTER_PLAN_V1.md) carries a supersession banner. No runtime database changes, game writes, or authorized terminal use occurred in this update.

## 2026-10-19 MyLEAGUE玩法全景研究：PC本世代终极联盟主战场

- 用户计划放弃以MC为主要模拟存档，改以NBA2K22 PC本世代终极联盟新开档运行30队GM V4；新局应独立save_id。M1/M2由Codex进行中，原五阶段仍玩家分别触发。
- 完整可持续扩充的[MyLEAGUE玩家操作/原生系统手册](../../docs/research/NBA2K22_PC_MYLEAGUE_PLAYER_OPERATIONS_AND_SYSTEMS_GUIDE_V1.md)已创建：16章，首页/日历、行政、教练、训练发展、球探/选秀、扩军搬迁、联盟新闻、排行榜/统计、全球设置、球队AI自动化、规则变化、休赛期与GM接管映射，并纳入用户提供的Gemini候选设置全集及外部资料来源。
- 用户已实机确认PC本世代很多全局设置与次世代一致；但PS5/Xbox Series 2K22新增MySTAFF/Prep Hub/Conditional Coaching具体专用机制不能未经PC菜单观察直接当PC事实。Gemini原文某些默认值/枚举/旧ADDR_TRADE/SETTINGS/SLIDERS地址尚未逐条认证；需Antigravity后续提供实机页面、实际值域与内存差分，补入手册，再独立规划MYLEAGUE_NATIVE_CONTROL层。
- **研究手册不授权任何游戏修改或自动接管**；已有教练19默认+18对手、交易等继续复用。GM可未来接管原生训练安排但仍禁止经营性直接改球员能力，世界级成长/伤病/工资帽设置由玩家批准。逐项确认GM已能执行后再关闭相应原生CPU自动化，以免休赛期无法签人/选秀。下一次玩家主动触发阶段更新时保留来源与反馈。

## 2026-10-19 MyLEAGUE实际GM能力审计/六人制服组/月度训练

- 新研究：[外部GM运营能力覆盖与月度安全训练方案](../../docs/research/NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md)；已同步修订[终极联盟玩法手册](../../docs/research/NBA2K22_PC_MYLEAGUE_PLAYER_OPERATIONS_AND_SYSTEMS_GUIDE_V1.md)，从人类可查看菜单转向外挂GM的`OBSERVED → ANALYSIS/DECISION → APPROVED EXECUTION → OUTCOME`覆盖审计，独立于现有M1/M2未验收设计PR #3。
- 玩家本世代实际UI可任命六人：CFO/财务、GM、主教练、助教、首席球探、训练师；当前`memory_field_profile.json`底层仍有8个staff岗位enum与8个反向指针槽，其中Governor/AssistantGM不能当作玩家UI已验证的可聘岗位，注意区别。主教练上任关联的Playbook/体系、助教/训练师加成实际公式待研究；已有数据读取但未有受控员工聘任执行闭环。
- 玩家确认训练类与2K20类似：球员导师影响徽章成长机会，团队/个体训练方向及强度，比赛+训练共用疲劳负担；老将/高分钟首发易过载，高潜年轻替补可在身体状况允许时更积极。但`source_catalog.json: injuries_availability_rotations`当前为`NOT_OBSERVED`，训练配置/伤病/疲劳/导师关系未认证读取；目前不应让GM基于假疲劳数据制定积极的每月高强度自动训练。首选`保守月度球队基准+少量目标球员例外`，无疲劳数据时原生自动或低强度HOLD；不能保证伤病为零。
- 下一步候选能力：累计疲劳/伤病与训练设置真实数据、六职位员工任免与人员市场、聘教练自动联动、CPU原生交易签约选秀自动化、导师、球探/休赛期阶段及历史事件账本；GM可新增信息不对称新秀/交易评估、长期预测等超出原生UI能力。**这些只是研究缺口，不直接给Codex新开发任务、不修改游戏，也不要求正在进行的M1/M2改范围。**

## 2026-10-19 NBA WORLD球员/媒体/赛场沉浸研究（不抢GM开发）

- 玩家最终次序：**先GM V4，随后球员系统，再做媒体系统**；媒体是高优先级的沉浸目标，不能只用“是否改变游戏数值”衡量其价值。独立研究文档：[NBA WORLD 人格、Obsidian媒体及NBA2K22赛场沉浸可行性](../../docs/research/NBA_WORLD_PLAYER_MEDIA_AND_BROADCAST_IMMERSION_FEASIBILITY_V1.md)。
- 研究证据：2K20 官方MyLeague士气化学反应+性格徽章；2K22社区阵容编辑Play For Win、Financial Security、Loyalty，为PC22字段线索，**本局尚未实机认证这些游戏内存地址**。用户设想“长期拒绝交易导致能力下降”与目前不准普通经营性直接修改球员属性的规则冲突，**不得按设想直接开发**；优先用外挂续约/交易请求/球员接受报价及已证实原生士气机制表达，任何超出既定规则的能力惩罚需玩家另行审议批准。
- NBA2K22 PC社区已存在Looyh NBA2K Hook（资源导出/加载日志/动态Mod/扩展插件线索）、Debug Unlock/Free Camera脚本和转播计分板Mod，证明部分改编空间；但**不证明**2K20破纪录叫暂停庆祝、记者/采访/社交观众图层仍存在于22，更不证明有可写事件触发器。分R0 Obsidian纯报道、R1外置赛场覆盖、R2原生转播UI资源Mod、R3原生事件/解说/动画注入四级，只读研究后再决定是否开发，禁止未经批准游戏修改。
- Obsidian原生Markdown+YAML+内链，可由未来Codex在玩家提供Vault路径权限后离线写文稿（不需要绑定未知插件）。媒体文章永远明确区分游戏事实、模拟报道/人物公开语句与传闻；每月/季后赛可先做，逐场真实赛后报道/即时场边采访须增加可信逐场或即时数据来源，现有数据仍缺game logs。

## 2026-10-19 GM V4之后：NBA2K22 PC竞技对抗与Sim Engine调校研究

- 用户确认发展次序：**先完成GM V4获得真实队伍建设与攻防决策能力，再独立调校NBA2K22 PC MyLEAGUE竞技引擎**，使竞技能力、对抗过程及博弈真实，而不是人/AI随便获胜；为后续球员、媒体沉浸生态奠基。
- 新研究基线：[竞技模拟与比赛引擎调校路线V1](../../docs/research/NBA2K22_COMPETITIVE_SIMULATION_CALIBRATION_ROADMAP_V1.md)。已初步检索Operation Sports本世代MyLeague sim研究、RES2 Current Gen、部分PC跨版反馈、Competitive slider比照及2021–22NBA统计基准。**不能直接套用社区整套数值；来源版本、玩法USERvsCPU/CPUvsCPU live/日历quick sim必须分开**，先动作/AI出手选择/犯规/战术响应，再投篮命中与联盟统计。
- 游戏世界级`WORLD_GAMEPLAY_PROFILE`只由玩家批准、稳定运行；GM按月仅调教练/战术/阵容等合法策略，绝不靠每月改变全局参数保证单队获胜。现有旧`docs/10_GAME_SETTINGS_AND_SLIDERS.md`自称权威但多个数值与效果未证实，旧`src/slider_manager.py`地址未经实机重新核验，不做一键写入。球员原始能力/潜力/徽章保持禁止普通经营性修改。
- 未来Antigravity取字段与内存真实地址/游戏消费验证，Codex按获批差分执行，分析模型比较赛场过程、联盟真实统计分布和GM战术效果；维持适量验证、不为找最优值长期停摆。**本轮只做研究文档，不开启调校开发或更改游戏。**

## 2026-10-19 玩家修正竞技调校范围：只针对NBA2K22实时3D赛场

- **新的权威文档**：[NBA2K22实时3D赛场引擎竞技调校V2](../../docs/research/NBA2K22_LIVE_COURT_ENGINE_CALIBRATION_V2.md)；前一版[竞技模拟调校V1](../../docs/research/NBA2K22_COMPETITIVE_SIMULATION_CALIBRATION_ROADMAP_V1.md)已经标记范围被覆盖。**用户明确不调日历快速模拟/Sim Engine，不以统计/赛季结果拟合作为项目目标。**
- 赛场唯一核心杠杆：**比赛Gameplay全局参数**（速度/加速度/防守/动作/疲劳/投篮与接触判定）、**球员Tendencies**（全局Tendency滑块 vs 个体球员真实倾向明确分开，后者现行普通属性/倾向禁写政策未自动改变，需要特别批准）、**球队教练战术**（19默认/18指定对手，手册/体系）及**AI攻防针对性临场调整/ACE覆盖**。CPU与玩家应凭篮球能力、战术对抗和操作公平竞争，不是通过CPU无解释加成确保结果。
- 重点用Operation Sports NBA2K22本世代RES2滑块反复调试经验、Eccentric关于先倾向后命中、Competitive体验作为候选，不直接照搬；**以玩家亲自打实时比赛/CPU对CPU观赛观察为主**，每次一个场上现象→模型查经验/定位相关机制→小范围配置差分→玩家再打后给出体验→保留/恢复，版本化LIVE_COURT_PROFILE。旧地址未经实机认证，不自动写游戏。
- **阶段顺序不变：M3 GM V4先完成，随后专项Live Court调校**；媒体球员系统之后，不把Sim Engine、训练/球员能力修改偷渡进新任务。当前文档只是研究规范。

## 2026-10-19 玩家已打通原生全局设置，Antigravity下一批原生GM控制点调研

- 玩家报告**之前交Antigravity查找的全局设置均已可以修改设置**；今后不再浪费查找时间重复扫描那些全局开关/滑块。M1/M2已合并main，M3 GM V4仍优先，Antigravity并行查操作入口。
- 新任务清单：[MyLEAGUE原生GM控制缺口发现V1](../../docs/development_tasks/DEV_20261019_MYLEAGUE_NATIVE_GM_CONTROL_DISCOVERY_V1.md)。P0：球队/个人训练与疲劳伤病读数、六职位员工任免、完整Playbook/得分选择/球员战术优先级、激活/首发角色、导师、ACE赛场覆盖；P1：真正合同签约裁员、休赛期阶段机、历史选秀大会选中与新秀归属、球探任务；P2：原生士气人格、逐场比赛/纪录新闻、老板商业、自然成长记录。
- 每项Antigravity交付须分别记录：真实UI、字段/类型/地址与对象身份、读能力、**实际执行操作及提交机制**、菜单退出/存档重开持久性、AI覆盖、效果证据和已验证范围。仅地址能读/设置页能显示不等于完成经营闭环；新增功能仍由玩家批准交Codex执行，不抢M3。
- 保留项目政策：不可普通经营性直接修改球员属性、潜力、徽章及倾向；原生训练/导师/招聘是合法的经营输入，球员个人Play Type若对应原始角色倾向需另获审批。旧世界级设置既然玩家已报告成功，不因开发记忆旧证据重开该任务。

## 2026-10-19 玩家纠正Native Control责任分工、M3设计审查

- 用户明确：[Native Control V2权威分工](../../docs/development_tasks/DEV_20261019_MYLEAGUE_NATIVE_GM_CONTROL_DISCOVERY_V2.md) **取代原V1中Antigravity工作分配**；Codex负责员工合同及任免、完整教练战术手册/球员角色/阵容（与已有交易签约教练执行器衔接）；外挂GM自建虚拟市场、球探/选秀/休赛期业务，Codex处理批准后的游戏合同/名单/新秀实际落地；**不要求Antigravity重新实现原生签约、选秀、球探、休赛期UI动作**。Antigravity已经继续找训练/导师/疲劳伤病/士气/赛场信息等原生读写接口，继续即可。
- 用户指出全真潜力/55项新秀数据会导致外部GM“全知选秀”，将来建议双视图：事实数据库保留真值，GM只看来源/资历/不确定性明确的虚拟球探档案，**尚不是M3工程阻塞**，也不能为了迷雾而修改游戏内球员能力。
- Codex PR #4（head `c3ce332`）Astra已完成M3A分析包与M3B独立30队GM五阶段/双边同版报价/portfolio冲突/策略状态的设计及15个合成场景，**没有M3运行实现、未在Web验证、正式30队仍UNASSESSED、V3仍生效**。研发侧审查认为可由Sol High按照设计包进入工程实现，重点 q_team_stats 真实来源、30队全员访问证据、双边同版接受、组合执行依赖、离线教练真实批次和持久状态；不为Cash/Web连接/单独引擎测试扩大交付。签约外部虚拟市场的商业逻辑与当前受控签约执行仍须区别，未来逐项接入。

## 2026-10-19 实时3D赛场AI与ACE研究优先顺序

- 最新研究交接：[DEV11球员决策/ACE临场教练调研V1](../../docs/development_tasks/DEV_20261019_11_LIVE_COURT_AI_AND_ACE_DISCOVERY_V1.md)。用户要先让球员AI做出合理投篮、传球、挡拆、跑位选择，**先查AI行为/战术调用与全局Tendency→临场ACE/攻防自动调整→最后调命中/运动/身体对抗**，只限真实3D比赛，不调日历Sim。
- 已有19默认+18对手教练受控写入，Antigravity不重建静态教练执行器而优先找**ACE实际控制范围**（玩家端/CPU端，自动进攻/防守，临场RUNTIME Coach/Gameplan实例、静态数据与live覆盖，是否每场重置、ACE四模式当前PC枚举）；并记录比赛前、节间、暂停后少量时点的动态状态，允许UNKNOWN，不把社区猜测视为已认证指针。Codex继续完整Playbook/阵容/角色实现。
- 2022 Operation Sports RES2本世代玩家为维持Play Physical选择关ACE，另一论坛用户指出ACE只作用于USER端，证据互有冲突；**开关不等于提高CPU教练智商**。长期若可受控运行时写入比赛计划，可以研究玩家批准的暂停/节间规则控制器，**目前仅研究不执行**，不承诺逆向/重编ACE内部算法。
- 当前项目仍不准经营性改个体球员真实倾向/能力/潜力/徽章；全局Gameplay Tendency可作为世界配置研究输入，今后若专项修改个体Tendency需玩家独立批准。用户主观实战体验与定向场上观察为调校主要反馈，M3优先级不变。

## 2026-10-19 用户最终限定实时赛场竞技：ACE原版开启，三方仅调Gameplay

- **最新权威研究：[NBA2K22实时赛场Gameplay全局参数V3](../../docs/research/NBA2K22_LIVE_COURT_GAMEPLAY_PARAMETERS_V3.md)**，覆盖前版Live Court V2中ACE动态控制部分及[DEV11 ACE实时控制探索V1](../../docs/development_tasks/DEV_20261019_11_LIVE_COURT_AI_AND_ACE_DISCOVERY_V1.md)。用户明确**不做C2实时内存改战术、C3外挂临场教练、不逆向修改ACE的决策算法**，无法常驻模型看比赛；已观察原版AI与教练会叫暂停、变更防守，接受其运行；**实时3D比赛ACE全程ON**。
- GM/Codex负责比赛开始前阵容、原生教练策略、Playbook、球员打法/个人倾向（个体倾向需明确批准设定与能力属性禁改边界）。之后游戏原版AI/ACE全程作场上临场调整。Antigravity不重复原生ACE实时对象逆向，之前已发现的全局GamePlay可读写接口作为来源即可。
- 用户+Web Development+Antigravity下一个竞技目标是**打磨Gameplay全局环境**：A运动8项上下限+Game Speed；B防守与接触/防守干扰；C投篮判定/覆盖和时机；D传球/控球安全；E Attributes全球作用倍率/疲劳；F犯规；G全球Tendencies（默认HOLD，与GM个人Tendency严格分开）；H真人操作/辅助与投篮模式。优先解决真实场上运动与攻防执行，不匹配赛季快速Sim统计、不先改个体能力/潜力/徽章。
- 继续采用玩家实时3D打球发现问题→按NBA2K22本世代社区资料定位参数小组→玩家批准差分→保留/回滚的反馈机制，适量试验；无后台监控，没有AI实时比赛干预。GM M3工程继续最高优先级，当前只是后续研究方案。

## 2026-10-19 玩家数十场HOF实时比赛EYE_TEST：实际竞技问题优先级

- 已归档完整原始观测及假设分层：[NBA2K22赛场玩家眼测与首轮针对性A/B](../../docs/research/NBA2K22_LIVE_COURT_USER_EYE_TEST_20261019_V1.md)。玩家打了数十场名人堂NBA2K22实时3D比赛。CPU勇士传切反跑、伦纳德接触强攻表现出彩；没有观察到HoF整体作弊式投篮/速度/抢断篮板，犯规/疲劳/篮板与基本防守总体合理→**这些HOLD，不因为社区要求强行降低难度**。
- 第一优先问题：**挡拆后两人围住持球人、顺下roll man频繁无人防守形成免费得分**，不能未经实际防守观察断言是SWITCH交接失误还是主动HEDGE/夹击却缺第三人TAG/轮转。先由现有19/18赛前Gameplan的`ScreenDefenseOnBall/Hedge/SwitchRule/StayAttached/PreRotate`做有理由对照，ACE原版ON，不研究实时外挂控制。
- 第二：普通CPU球员篮下只要有防守便几乎打铁、小后卫还敢正面挑战中锋，拆成不合理出手决策（个人/全球Tendencies、Playbook/RunPlayTendency/进攻调用）与轻接触下命中判定过严（Layup Defense Takeoff/Release、Contact Shot、Inside/Close/Layup、Shot Coverage）；社区2K22 HOF/跨版本玩家亦有类似篮下强干扰失真反馈。**保持球星强终结与防守尺寸差，不全局无脑加成功率**。
- 第三：勇士已有成功传切而多数球队少流畅组合，优先GM/Codex完善赛前战术手册和球员战术分配。用户之前仅中锋持球月球慢动作，Movement专项留后。
- V3研究路线已改为以玩家实际问题驱动、先挡拆与篮下，而非预设先8项Movement。短时A/B：3–5个类似挡拆回合+普通/明星轻接触内线终结，按单一参数族、用户批准、保持原版ACE、记录副作用。**待明确几十场HOF究竟是MyCareer单人控制还是MyLeague全队控制**，不能提前断言USER/CPU滑块归属和教练权限。

## 2026-10-19 用户最后确认名人堂原版基线 + 仅接受有来源成功经验

- **权威新调研**：[NBA2K22本世代名人堂赛场参数，已验证玩家经验与证据分级](../../docs/research/NBA2K22_HOF_CURRENT_GEN_PROVEN_SLIDER_RESEARCH_20261019_V1.md)。用户所有几十场打球都是原版Hall of Fame下观察，**必须保留名人堂完整默认参数为唯一差分起点；不改成Pro/All-Star再试**。玩家明确拒绝让模型猜数值后叫自己A/B测试，要求模型**搜索、追踪、对比其他玩家确实用过、改过且反馈改善或失败的方案**。旧Live Court V3/眼测文档的“玩家做3–5回合/模型猜微调数值”方案已标记不再执行。只有来源证据成熟且玩家自主批准后才实施参数。
- 2022 PS4本世代作者gu8lal8提供默认HoF对照：部分CPU投篮/篮下成功率56，USER48，防守干扰和协防默认为50（仍以Antigravity用户本机实际读取为最终权威）；另一PS4的IrishSalsa案例明确HoF开局并只改列出的参数，但**没有证明其Help Defense=70修复PnR**。
- 用户进一步明确PnR情况是**弱侧第三人无人补防，至少应该正确换防**。OS 2021本世代CPUvsCPU案例反馈Help Defense=100、Over/Drop、Pre-Rotate甚至关闭ACE仍没修好；2022部分PC用户反馈高防守滑块改善整体防守但未证明能修roll-man的tag。因此**目前没找到可证实的本世代HoF PnR完整成功修复参数，不建议瞎给Help=100或全防守=100**，本来正常的防守和名人堂基线保留。
- 篮下接触终结方面已有直接反馈改善资料：2022次世代Eccentric作者本人用Inside60/Close55/Contact50认为改善了中锋近筐终结（他自己的套装条件）；H2UKNOW HoF次世代减弱Layup Defense对詹姆斯/字母哥轻接触惩罚；J-Kits PS5 HoF V2.3针对layup干扰反复修订并有实战视频。**这些证据支持参数作用方向，不是PC本世代HoF适用的“已验收最终值”**，不交用户试错。继续只查2021–2022 HoF PC/PS4的可追踪成功结论；若未知明确写UNKNOWN，宁可不推荐。
- ACE始终ON，不引入实时C2/C3；GM赛前战术与球员倾向由Codex另行接入；M3继续主任务。当前没有新的游戏写入或场上数值。

## 2026-10-19 名人堂Gameplay V1候选（玩家请求实际可输入的单套方案）

- 正式提案文档：[NBA2K22 HOF COURT PROFILE V1](../../docs/research/NBA2K22_HOF_COURT_PROFILE_V1_PROPOSED_20261019.md)。**以PC/PS4 2K22原版HOF为底，只有四种Gameplay滑块发生更改（CPU/USER各侧），不是直接套社区整套Pro/All-Star**：Inside Shot Success USER48→52 CPU56→60；Layup Defense Strength Takeoff和Release USER/CPU原版50→35；Help Defense Strength USER/CPU 50→70。原版ACE开启，所有其余Offense、Defense、Attributes、Movement、Tendencies、Fouls、Controller正常项保持HoF。
- 依据：gu8lal8 PS4本世代HOF默认表；IrishSalsa PS4 HOF Help70/70；H2UKNOW次世代HOF原作者回复上下Layup防守改35；Eccentric次世代作者明确Inside60改善大个子内线。**这是Web结合不对称HoF默认构成的研究型候选，不是任何来源验证过的整个四项组合**。尤其Help70**不能保证修复两人围持球者+无人tag roll man**，有本世代Help100仍失败的反例。
- 玩家这轮已明确要自行验证一个有来源的综合方案，区别于此前拒绝研究人员随机给不明数值并长期A/B磨参数。此文档**未写游戏、不自动执行**，待玩家实际观察结果反馈后才评价是否成为正式WORLD profile。

## 2026-10-19 MyLEAGUE全局世界设置/外挂财务研究V1

- **最新候选权威文档**：[2021–22终极联盟30队外挂GM世界规则及全局设置V1](../../docs/research/NBA2K22_EXTERNAL_GM_MYLEAGUE_WORLD_SETTINGS_V1_20261019.md)。2026-10-19根据玩家要求检索本世代/次世代2K22 MyLeague方案与NBA官方真实2021–22薪资/税线，并逐项给出赛制、30队经营自动化、交易/选秀、成长伤病士气、球队财务、3D/日历基础设定。**这只是未执行的研究提案，最终由玩家批准才能写游戏**。旧docs/10_GAME_SETTINGS_AND_SLIDERS.md已贴非认证警示。
- 2021–22实际联盟财务：Cap112.414M、Tax136.606M、2021版Tax Apron143.002M（**只对特定签约触发硬帽，不能统一设置全联盟HardCap143M**）；SalaryFloor101.173M。游戏SalaryCap ON、HardCap OFF（独立外挂约束）、Tax ON（若可）、Staff Budget ON；直到2026–27现实NBA每年度真实Cap/Tax计划由外挂引用，游戏通胀raw不当成确定年度百分比。
- 原生经营：Trade ON保持游戏框架、CPU-CPU Trades OFF、CPU Trade Offers OFF、TradeFrequency0、Trade Approval ON；30队Automation交易/签约/选秀/球探/员工OFF，仅训练/伤病应急仍暂ON待替代，ACE进攻/防守ON，比赛中AI自动控制战术调用与实际分钟。外部GM谈判决策、Codex批准后游戏落地，不让2K黑盒评估重写双方意愿。当前签约执行能力仍待正式验收。
- 自然成长/生态PROPOSED初稿：Progression48、Regression50、Training50、Badge默认50、各能力Growth/Peak年龄曲线保留原版；Injuries总开、ProgressiveFatigue开、SimInjuryFrequency55/Severity40、实机50/50、CareerEnding5；Morale ON Difficulty35 Effects40、Chemistry ON Difficulty/Effects50/50。**没有任何玩家公认最佳值，均需标注来源及提案状态**；继续禁止普通经营性直接改球员能力/潜力/徽章。
- 原生每队TeamCash保持当前事实且语义未证，不向游戏内存统一注资。外挂另建议按2021Forbes市值排序A60M/B40M/C25M/D15M四档机动经营资金（**全新游戏设计数值，不是真实球队现金**），已有2021合同及税费不追溯，M1财务现金解释和虚拟税务成本未核实时不得作为真实签约容量。真实比赛仍以HoF默认赛场参数为底，另一个HOF Court V1候选独立等待玩家体验，日历SimEngine全部默认。

## 2026-10-19 30队全部玩家经营权评估：建议User-owned，比赛CPU/USER滑块仍需分离

- 用户担心CPU球队自动化改写外挂GM决定，提出新MyLEAGUE将30队都设为**User-controlled franchises**。评估文档：[30队控制权与场上滑块作用范围V1](../../docs/research/NBA2K22_30_TEAM_USER_CONTROL_EVALUATION_V1_20261019.md)。**建议采用**：2K22 PC玩家cdcool已采用全30队控制且每场CPUvsCPU观赛；这样能让外部GM独占交易、签约、员工、选秀等经营，30队Team Automation经营项Manual/Off，但比赛参与Game Participation建议Auto、训练及伤病应急暂Auto、比赛ACE/战术自动调用/换人仍由原版AI负责。
- **特别澄清**：球队被标为User-controlled仅代表经营权限，不足以证明游戏3D赛场10名球员使用USER Gameplay Sliders。跨版本Operation Sports玩家对CPU/USER作用在AI队友的规则有互相矛盾结论，**当前2K22 PC精确消费路径UNKNOWN**，不要把USER/CPU两栏合并/丢弃。名人堂HoF原始USER Inside48 vs CPU56及独立候选52/60暂都保留，不自动修改为所有队一侧。球场手柄居中CPUvsCPU与真人控单队可能不同，calendar sim是另一引擎。
- 30队User也不能保证原版实际分钟、伤病自动重排、特定对手教练计划和休赛期提示永远不覆盖；外部GM事实决策与游戏真正的名单/合同写入继续玩家审批。此处只是文档评估，**没有读写游戏或改变正式存档**。

## 2026-10-19 NBA2K22战术生态与球员Tendency战术适配——GM/Codex后续重点

- 新权威机制研究：[NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1](../../docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md)；给Codex的接入任务书：[DEV_20261019_12_TACTICAL_BEHAVIOR_ENGINE_CODEX_HANDOFF_V1](../../docs/development_tasks/DEV_20261019_12_TACTICAL_BEHAVIOR_ENGINE_CODEX_HANDOFF_V1.md)。这是M系列后GM正式以球员和战术为核心经营必备的篮球知识：教练能力与阵容适配→Preferred/Active体系→Freelance/POE→本内实际PlayID与PlayType→球员4个有序PlayType/PlayInitiator→Touch/Shot/Isolation/Drive/PlayDiscipline等个体Tendencies→实际55只读原始能力→对手整体18+逐人特殊防守→原版ACE运行→比赛输出→内部改善/交易签约。
- **新授权**：用户明确允许GM调整**球员个人原生Tendencies**以融入赛前球队战术体系，必须是基于原生数据的具体提案、玩家逐项批准、Codex受控执行；**不是一般性获准直接写游戏**，绝不扩大到普通能力/潜力/徽章修改（仍只能历史重力单独批准）。Play Type 4槽是另一类角色输入，不能冒充已有可写能力。
- 当前已经能够读取执行的教练19默认+每队对其他29队整体防守18字段不变；但本Book具体PlayID目录、球员4槽、完整个体Tendencies、个别防守、主教练属性实际作用等**未完成本局读写验收**。DEV12首批先只读补这些字段+生成PlayType和Playbook静态不匹配/角色受益人冲突报告，下一批Codex实现经批准的个人Tendencies、PlayTypes、个人防守差异、Playbook内部编辑，不在新的DEV重复建19/18执行器。
- Operation Sports 2K22实际玩家发现：ISO POINT类型不在本队Playbook就会跳过到Play2；Touch与CloseShot的作用出现互相矛盾的玩家观察，2K22有某些硬编码叫战术受益人，不能用统一50和虚假概率公式判断。2022勇士总决赛G5 NBA官方Curry16分0/9三分、Wiggins26分13板，说明次级进攻点与错位攻击/防守对位的合理GM问题，并不等于当局直接改Wiggins能力。
- **训练旧禁令被用户后续决定覆盖**：Antigravity会单独找到训练类型/强度/疲劳/恢复/导师，交Codex。GM教练手册已加注用户最新授权优先条款，待源认证后再纳入训练与赛场表现的联合诊断。仍不开发实时外挂AI/关闭ACE、锁定精确分钟、擅改CalendarSim全球参数。

## 2026-10-19 DEV12 V2：四期原生战术+GM知识引擎全部由Antigravity完成

- **最新唯一Antigravity开发入口**：[DEV12 V2 Antigravity完整研发任务](../../docs/development_tasks/DEV_20261019_12_V2_ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING.md)。**用户明确重新分工：原交Codex的A/B/C/D四期全部由Antigravity负责**；旧[DEV12 V1 Codex交接](../../docs/development_tasks/DEV_20261019_12_TACTICAL_BEHAVIOR_ENGINE_CODEX_HANDOFF_V1.md)已经加废止提示，仅保留历史背景。Antigravity基于main现有教练19默认+18指定对手整体防守接口增量开发，Codex不再承担同一套战术生态实现，除非用户以后另外指定。
- 任务的**最重要成功条件是GM懂原生战术系统中各字段关系与实际篮球行为**，不是找齐可写地址。A期：Playbook内PlayID/type/角色、每人4 Play Types、原生Touch/Shot/Iso/Drive/PlayDiscipline等Tendencies、教练属性及Proficiency（若真存在）、逐人防守/真实Matchup身份；B期：可解释战术断链、主攻/副攻/防守对策、真实NBA2K22来源证据与知识卡、战术适配诊断和内部调整/交易/HOLD理由；C期：受玩家审批的PlayType/Tendency/Playbook内容/个别防守写入+读回恢复，OVERALL不能覆写PERSONAL；D期：Antigravity原在查的训练/导师/疲劳恢复与球员自然成长机制纳入GM长短期战术决策。
- **实核源码路径**：`config/coach_tactics_profile.json`（playbook相关pointer/stride与68 slots只是布局线索，不意味内战术已解）、`src/coach_locator.py`、`src/coaching_reader.py`、`src/coaching_overall.py`（有效matchup、defender、8-byte设置，matchup_id与全局player_id对应仍需认证）、`src/coaching_targets.py`、`src/coach_codec.py`、`src/defense_codec.py`、`src/gm_core/coaching_batch.py`、`src/coaching_batch_executor.py`、`scripts/coaching_snapshot.py`/`scripts/coaching_batch.py`，gm手册及执行手册。2026-10-18首次真实同批来源**已经**完成30队19默认+870对手整体采集；旧手册的“尚未正式首采”被`docs/34_BASELINE_CURRENT_STATE.md`后续状态覆盖。
- 用户已授权GM按赛前战术适配**提出**个人Tendencies修改，真实正式存档仍逐动作经用户批准；不直接改球员原始能力/潜力/徽章/伤病。ACE原版一直ON、不做外挂实时教练、个人精确分钟不锁定。Antigravity可以独立实现，但生产新增来源遵守玩家触发全量`full_verified_v1`同批，不发布错时半套数据。
- 重点2K22社区证据：玩家实测个人ISO POINT槽若当前Playbook没有对应Type会被跳过；有些内置plays的受益者硬绑定，Touch等单一值不能保证谁得到战术。完整机制关系研究原文：[TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1](../../docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md)。不建立虚假的角色适配百分比或属性修改捷径。

## 2026-10-19 Antigravity类别2–6：世界规则V2缺口复核

- [新研究：NBA2K22世界线V2类别二至六设置缺口审计](../../docs/research/NBA2K22_WORLD_RULES_V2_GAP_AUDIT_20261019.md)。用户给出Antigravity总结：日历模拟20+、能力成长巅峰衰退100+、30队战术/轮换/训练、历史新秀生成6项、原生交易估值25+。**这只是该摘要而非完整Antigravity raw字段表；SLOT_TRADE/GAMEMODE_SETTINGS_SAVED_PROFILE等具体偏移与CPUAttributeBoost效果仍待原值和实机证据，不能自称已认证。**
- **类别2 Sim Engine是之前V1真实漏项**，因为30队GM多数赛事日历模拟，且GM根据这些比赛数据进行交易/战术诊断。设2021–22 NBA.com官方标尺PPG110.6、PACE98.8、FG46.1%、3PT35.4%、三分出手占比39.9%、eFG53.2%；**标尺不是Slider raw值**。先保存现有全局sim设置、同批统计核对，不能任意拼DarthRambo11min方案与RealSport101另一套数值；实际3D仍是独立HoF Court Profile。
- **类别3成长曲线是第二漏项**：V1 Progression48/Regression50仅保留候选，各属性Growth/Peak/Decline和全球Peak年龄原版HOLD直到拿原生实际值/年龄阶段语义；肌体能力先于IQ衰退是经验方向，不直接套2K20 Comduklakis整套Speed12/-5/-30等为2K22最优。GLeague历史有超级成长风险，当前2K22未经证实；训练属DEV12，游戏自然成长严禁经营直接改Ability/Potential/Badge。
- **类别4已交Antigravity DEV12 V2**，不重复开发。Antigravity声称能直接锁Target Minutes或Crunch Time5，不等于已经证明真实3D游戏AI会始终遵守（以前实际看到分钟被覆盖）。保留原版ACE/AI换人并视实机持续验证；不强制重启锁精确分钟任务。
- **类别5历史班保护**：DraftClassQuality及随机新秀Potential/Badge/Durability原版HOLD；DraftStorylines若存在优先OFF以避免导入历史球员原值无意随机化，仍需核实关闭后历史原始能力/潜力实际稳定。检查历史1984→2020每班60个选秀名额真实人与generated填充比例，循环名字与ID冲突。
- **类别6原生交易估值全部HOLD**：Year2–5选秀权贬值、九种PlayerType折价及四种球队资产偏好是原生AI市场权重，30独立GM已代替其决策，原生总开关与CPU自主交易由世界配置负责；不同球队价值哲学/未来选秀权相对价值需要在M3外部GM协议和DEV12技能匹配中形成，不要浪费精力改引擎市场价。提高原生Pick Depreciation raw可能是提高价值保留，不能由字段名臆断。
- 世界规则下一步更重要的补漏：退役/永久伤退/自动补员/自由球员去向与长期联盟人数守恒、真实Cap/Tax与游戏原生通胀或外挂税款重复、训练疲劳+日历Sim伤病双重扣减、30队User经营自动化与原版CPU市场抑制、固定2021比赛规则不随1984历史班轮回自行变1980年代、世界配置季节版本快照。
- 本文件只完成研究和GitHub索引，**没有更改真实游戏**。最终全字段数值版需要Antigravity现有设置表的name/current/default/range/type/真实消费路径/读写读回验证，先不要让模型瞎补100+曲线。

## 2026-10-19 紧急更新：M3A/M3B已工程完成，DEV12战术系统需要M3-T整合

- Codex PR [#4](https://github.com/chris2gao/nba2k22-gm-engine/pull/4) 已提交M3A/M3B本地工程，实现head `fa62fb2d371438cd9d8062e1fa842e7c8eede4ad`，Draft/Open/mergeable，未合并、未开启GM V4、30队正式研究仍0/UNASSESSED。已有15项直接测试、真实M02 30队466在队身份和合成30队P1–P5主流程/终稿v2；不应因战术新需求推翻已有M3主干。
- 玩家报告Antigravity在本机`e:/games/NBA 2K22/antigravityUse/完整战术与球员行为系统/`已研发完整DEV12 A–D（68槽战术本、4PlayTypes、99Tendencies、8教练体系与评级、个人防守、训练联动、受控预检），正在与玩家实机调试；**线上main已含其早期commit `9b4fe87`七文件，但用户报告本地新版更多文件尚未全部入库，不能把旧GitHub 7文件当当前本地完整成果**。
- **最新决策**：M3必须有战术和训练因果理解，不能只是HOLD/INTERNAL/MARKET叙述能力。已发布[DEV13 M3-T增量集成方案](../../docs/development_tasks/DEV_20261019_13_M3_TACTICAL_DECISION_INTEGRATION_V1.md)，并在PR#4留下集成审阅[discussion](https://github.com/chris2gao/nba2k22-gm-engine/pull/4#issuecomment-6282559304)。保留M3A/M3B现有30队审议/报价/版本/终稿结构；下一步待Antigravity本地新代码由Codex归档线上后，再增量加入同批战术/个人Tendency/训练只读投影、来源索引、D1–D6诊断约束、内外部调整比较、跨交易动作失效、个人字段冲突及审批落地，独立PR；暂不启用GM V4/不操作游戏。
- **已发现仅在线早期9b4fe87代码风险需在新版本重验**：`tactical_reader.read_team_playbook`目前只输出68槽hex CRC、不含每条Play的Type/目标球员；`tactical_fit_analyzer`凭Pacers名称+Isolation Point特例判UNSERVED并标STATIC_VERIFIED，非真实PlayType交集；Touches≥75/多个创造者、最高教练体系熟练度=最优体系属启发式不可证明胜率；`player_tactics_adapter.execute_single_write`和`matchup_defense_adapter.execute_matchup_write`可接收裸地址/hex写入，函数本身没有career/batch/user approval绑定，正式执行不能直接暴露。**本地新版本是否已经修复未知**，需要Antigravity最新源码、训练导出与实机测试后验证。
- GM正式经营核心规则：读球员55 Ability（只读）+99行为Tendencies（可逐审批改）+有序4 PlayTypes/真实手册类型/教练体系/逐人防守/训练与疲劳；先判断使用问题、战术缺口和内部修复能否解决，仍缺执行者时再发起经济自洽、对手GM独立接受的交易；原版ACE始终ON，精确分钟不锁定，普通能力值/潜力/徽章严禁直接修改。

## 2026-10-19 新优先级 DEV14：确定性数据库-内存双向I/O底座

- **Codex已获玩家授权开发新DEV14（授权开发不等于授权正式游戏写入）**：[完整开发任务书](../../docs/development_tasks/DEV_20261019_14_DETERMINISTIC_STATE_IO_ENGINE_V1.md)。DEV14优先于DEV13的M3-T正式接入；M3A/M3B PR #4继续Draft未合并，DEV12由Antigravity在独立本地目录研究原生字段与训练。
- 数据建模：保留`league_state.sqlite` + `player_pool.sqlite`既有正式事实权威与不可变`full_verified_v1`批次；新增本地`gm_control.sqlite`记录Desired变更/用户Approval/执行Run/Shared Byte Preimages/Receipt/Reconciliation；无30队同构物理表，统一按`career/batch/team/player/side/opponent/slot/field`建模并可创建游戏页面视图。全部字段共享版本化NativeFieldRegistry和read/decode/encode_patch，未知不可假补50。
- Codex三个阶段A:registry+控制库+stage/validate，B:复用既有CoachingBatchExecutor做审批、共享bitfield合并与条件回滚、按已认证适配器整批写入，C:扩充现有玩家触发`run_data_update.ps1`而不是另造capture路径、SQLite双库审计归档/GM分页查询/approved-applied-vs-observed自动对账。模型只提交稀疏字段变更、执行模型只触发获批批次；即使数千字段也靠Python确定性写入，SQLite事务与进程内存非原子必须区分。
- 本任务只做定向合成测试与既有M02只读副本，禁止无玩家后续审批自动运行正式RW、采集、发布或合并PR。不直接改玩家原始能力/潜力/徽章；个人Tendency/教练/训练/游戏全局仅按字段允许范围与审批。DEV13已添加先消费DEV14底座而不重复开发执行器的说明。

## 2026-10-19 DEV14 V1.1：新增多存档管理与非破坏性重置

- 玩家希望新开档可重置数据，也可能同时保留最多4个世界，但日常只玩一个。评估仓库现有`src/save_context.py`与M0查询代码后，**选择方案二的物理隔离，不清空全库**：已有`database/saves/<save_id>/league_state.sqlite`、`player_pool.sqlite`、各档快照/备份/静态查询，开发成本比30队或多档混表低。
- [DEV14 V1.1 开发主文档](../../docs/development_tasks/DEV_20261019_14_DETERMINISTIC_STATE_IO_ENGINE_V1.md)新增第2A节与**DEV14-D（必须做）**：每档`gm_control.sqlite`，本地唯一`active_save.json`及generation身份、最多4个切换工作区但仅一个ACTIVE，`save list/status/create/activate/deactivate/retire/reset`，默认以新save_id从干净模板创建新世界。切档**不**自动加载游戏/采集/内存写；不同存档同名M02/player_id/decision_id永不串档。仅活动档允许执行。
- 实核技术边界：旧`resolve_context(None)`会fallback到`legacy-shared`；新版DEV14 CLI必须拒绝这种隐式共享，但保留历史工具兼容。原`monthly_snapshots.snapshot_id`不带career，因此多档必须物理分库存储，不能在共享league表中混写同名赛季快照。
- **危险重置**只在用户确需重复同一save_id时使用，dry-run→精确双确认→旧三库/控制journal的SQLite backup完整归档→准备新generation→持久化激活指针；任何归档或替换失败都保留旧完整generation或阻断，不能混新旧league/pool/control。历史GitHub发布、旧快照和其他档不删；旧审批对新代次无效。若当前`published/latest`代次不支持安全复用同名save_id，宁可BLOCKED，要求新save_id。
- 目前仅更新开发文档/开发记忆，**尚未运行reset、修改游戏、采集或创建多档工作区**；DEV14开发仍交Codex，Antigravity只负责原生字段接口。需针对两个档同名快照/同球员和切档中执行/重置失败做少量合成定向验收。

## 2026-10-19 Codex额度优先顺序+新GM潜力遮蔽/OVR轮换机制

- 用户反馈Codex周额度约9%、5小时额度约49%（当时界面状态，不推算能执行多少任务）。推荐单次一阶段：**B0 DEV14-H**三库pool代次/人工审批信任边界小补丁→**B1** PR#5由玩家授权合并、PR#4适配/定向回归 + GM潜力脱敏→**B2** DEV13 M3-T只读数据与GM六维战术诊断→**B3** 经Antigravity原生证据的OVR软轮换反馈。[M系列分批执行总计划](../../docs/development_tasks/M_SERIES_20261019_QUOTA_AWARE_EXECUTION_PLAN_V1.md)。
- [DEV14-H](../../docs/development_tasks/DEV_20261019_14H_DEV14_POST_REVIEW_HARDENING_V1.md)指出PR#5 `Workspaces.check_databases()`只核league和control却未核pool；pool采集`os.replace(*.capture)`后generation元数据容易丢。CLI用户输入的`--approve-game-writes`、`player-approval-reference`由调用者提供，不构成不可伪造真人批准；模型自动调度不得为自己签授权，同权限操作无法靠同目录HMAC提供强隔离，生产期间保持MANUAL_OPERATOR_TRUST_ONLY。
- [DEV15](../../docs/development_tasks/DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)：**A P0潜力信息遮蔽必须在GM V4正式分析前实现**。当前M0`q_players/q_pool.attributes`直接JSON暴露原生attributes，PR#4 M3将其解到`decoded_attributes`，市场筛选支持`attributes.<field>.value`，所以GM view需要allowlist、SQL/屏蔽属性测试，新版GM导出不应包含原生Potential；内部私有原始库可保留以支撑自然成长/校验。若GM仍可从GitHub原始SQLite直接读取Potential，则标FOG_NOT_ENFORCED_RAW_SOURCE_ACCESSIBLE，不能声称实现严格信息遮蔽；历史选秀的现实未来成就不能自动当当前世界线确定未来。
- **B P1 新用户单字段例外**：玩家称原版球员有25–99的综评补偿、能影响显示OVR与AI优先首发/第6人/轮换分钟，非真实投射/传球/防守技能调整。旧2K Intangibles玩家反馈支持方向但对2K22 PC具体效果/合同和Sim副作用未认证；只允许Antigravity确认具体原生字段和能力保护之后，以玩家逐项批准的`PLAYER_ROTATION_OVR_BIAS`引导原版自动换人；继续不做锁定分钟。先把GM`minutes_target_band`、教练BenchDepth、年龄/体系、球员位置、先发和第6人等加入DEV13诊断，依据真实采集校准而不是发明分钟公式。可调整的显示OVR不得直接变成GM球员真实实力/交易价值。
- 现有DEV13任务文件已加本批新规则与依赖；DEV14原任务V1.1保留但已标新的小补丁及例外。已有M3PR#4 Draft、DEV14PR#5 Open尚未合并；此轮只更新GitHub文档，未执行代码/游戏、更未触发全量采集。

## 2026-10-19 玩家正式修订：Potential强制入库遮蔽与全联盟Intangibles轮换

- **本条覆盖前文DEV15 V1“GM查询层遮蔽即可”和“Intangibles副作用研究必须先做”的早期建议。** [权威DEV15 V2](../../docs/development_tasks/DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)已确认PLAYER `intangibles` offset1088/0x440（rating/1 byte），`potential` offset1089/0x441（1 byte），见`config/memory_field_profile.json`、`src/dump_player_pool.py`。两字段相邻，DEV14例外只允许获批写入Intangibles一个字节，不开放其他Ability/Potential/Badge。
- **Potential后处理固定为1**：每次`full_verified_v1`原生RO采集完、正式备份/SQLite哈希/manifest/发布前，自动执行确定性`sanitize_player_potential`处理所有在队和球员池记录：`player_pool.potential`、`raw_potential`、`player_pool.source_details_json.attributes.potential`、`player_source_details.details_json.attributes.potential`（raw/value均1）及两边完整PLAYER `raw_struct[0x441]=1`，覆盖新扩展存储的其它Player raw镜像（如`state_io_objects`）；失败阻断发布，哈希须脱敏后计算。**不改游戏真正Potential**，此值是MASKED占位而非观察值，GM不得当作选秀/成长依据。历史已发布潜力可能泄露，单独处理老批隔离或获批的新GM安全副本，不暗改immutable。
- **Intangibles作为30队GM正常轮换手段**：GM可按首发、第六人、板凳人数、角色目标分钟，提出25–99综评补偿偏置并从真实后续赛场分钟反馈调整；原版ACE自动换人继续ON，不硬锁分钟。用户已放弃额外研究Intangibles对游戏其它模块副作用的要求，Codex不应浪费额度做研究；但确定性身份/字段/写前/写后/回滚和每批游戏修改的玩家批准照旧。
- **DEV14已有实际整合而非空架构**：PR#5 `registry.py`注册19默认/18整体、个人防守、4PlayTypes/initiator、48可命名可写+51语义未知只读的99Tendencies、68槽本、4Gameplay USER/CPU、50世界设置、6球队+5球员训练并通过NativeSession RO/RW/capture bridge。欠缺其余原生字段/导师关系、正式游戏生产采集验证，以及将战术理解转为M3决策的DEV13。不要再立项重做整个通用采集写入器。
- [额度友好计划](../../docs/development_tasks/M_SERIES_20261019_QUOTA_AWARE_EXECUTION_PLAN_V1.md)现分B0原加固，B1首先潜力入库后强制脱敏，B2 DEV13战术/训练决策，B3综评补偿动作和反馈；该规则也已写入DEV13与DEV14权威文档。本次仅更新GitHub文档，**Codex代码尚未实现这两项新增修改**。

- **重大新发现：GM脱敏球员池不可用于原生历史选秀注入。** `src/historical_rookies.py.query_historical_draft_class()`返回`player_pool.raw_struct`及`raw_potential/potential`。GM正式采集发布库已按用户决定将PLAYER byte0x441和所有潜力明文置1；**任何利用这份脱敏raw_struct向游戏注入1984–2020历史新秀的脚本，可能把真实原生Potential变成1**，违背游戏人物自然成长规则。历史选秀入游戏必须使用独立权限的未脱敏原生私有注入来源，或每次从真实游戏原生存档正确重读；未提供则报`SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE`拒绝导入，而不是用GM发布库冒险。此为数据防污染工程约束，不是用户取消的Intangibles额外副作用研究。已写入DEV15 V2，并在PR#5评论明确。

## 2026-10-19 用户最终补充七项DEV16：教练冲突澄清、战术本、倾向语义和训练范围

- [DEV16授权开发文档](../../docs/development_tasks/DEV_20261019_16_M3_NATIVE_COVERAGE_AND_GM_TRAINING_PLAYBOOK_INTEGRATION_V1.md)：主任务是把已完成的DEV14字段能力交GM用、补缺知识与训练疲劳；不重做已有原生框架。
- **教练所谓冲突并非球场战术矛盾**：DEV14 plan代码目前拒绝同一owner/opponent同批OVERALL+PERSONAL防守，以及同批coach.PlaybookID切本+PLAYBOOK_SLOT编辑。可以GM提出组合策略，执行器拆为有序可审批子批：整体防守再个人例外；先切新手册并再采新槽位原值后修改。原Coach POE共享位域支持合并。
- **战术/倾向Antigravity责任**：战术本68槽CRC≠已掌握实际Play Type/使用位置，AG补Play CRC↔UI名称/类别/教练体系/现实篮球动作与替换安全流程；51剩余未知Tendency补真正语义/映射后交Codec家族登记，不要开发第二套读取/写入。
- **训练范围收敛**：仅队伍主客场强度/自动强度/B2B休息和个人训练位置模板、原型、强度、伤病恢复；不做各单项能力微调、直接加能力或徽章、导师复杂关系作为本期必需。当前`config/state_io_native/training.json`仅能证实通用九类player_types(0..8)，尚未覆盖用户提到每个位置约十套模板的实际UI枚举，AG给位置/模版对应。原生已记录progressive_fatigue_history @0x2F5与count flags，但DEV14 Registry当前只把5个个人训练flags读作设置字段，**疲劳当前值/趋势解码仍未接入可供GM读取的字段**：由AG补ReadOnly fatigue映射，Codex复用统一采集/查询，GM结合比赛分钟/赛程决定训练强度与伤病风险，不把历史字段当实时确定值。
- **同一家族验证**：用户与AG已验证一类中有代表的单个字段写入成功即可认同一原生编码类别的机制；不要求每个World字段/99个Tendencies反复手工测。仍保留确定性原字段slot/offset/合法值域、唯一球队球员身份、mask和CAS/读回；复杂手册替换因实测曾失败，独立修复。World仅现已注册50、Gameplay当前4项USER/CPU足够，不得将未知未映射项称为已可执行；其他世界字段未来按已证codec加registry即可。
- DEV15 V2 Potential入库后全部置1和Intangibles 0x440/25–99 30队软轮换规则继续有效，无新增副作用研究。所有游戏修改都需玩家批准。本轮只更新GitHub文档，不运行游戏、合并PR或开始实际代码开发。

## 2026-10-19 GM防守与战术书最终定稿：个人策略、球队独占实体

- [新权威GM运营文档](../manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)及修订[DEV16](../../docs/development_tasks/DEV_20261019_16_M3_NATIVE_COVERAGE_AND_GM_TRAINING_PLAYBOOK_INTEGRATION_V1.md)：玩家最新明确**GM日常完全不修改OVERALL_DEFENSE，仅对对手具体球员按需写PERSONAL_DEFENSE**。用户确认原生整体防守会覆盖所有个人防守；原有“先改Overall后改Personal”经营规则作废。Overall仍可采集/只读，DEV14底层codec保留，非GM维修需要独立授权。无法唯一匹配个人native ID时BLOCKED，不得偷改整体。
- **战术手册策略**：GM正常经营不得自由改coach.PlaybookID切换书。每队以专属的**物理独立原生Playbook对象**（优先本队同名原生书）为资产，允许在68槽添加/替换内容满足当前教练体系和球员；更换教练是员工/合同事件，需重新采集新任教练与Playbook的原生绑定，必要时经玩家批准做仅用于确保球队独占的技术性绑定，再修改本队专属书槽位。**名称同队名不代表书实体独立**。
- PR#5的`adapters.py`会识别共享owner集但Registry标记`EXPLICIT_ALL_SHARED_OWNERS_OBSERVED_PLAY_CRC_ONLY`，因此目前共享Book若所有owner身份没有变化仍可能按共享方式被写。**新GM政策必须默认阻止任何包含多Owner原生Playbook的单队编辑**：`SHARED_PLAYBOOK_MUTATION_BLOCKED`，需要`owner_team_ids == [team_id]`且原生指针/实体独立。不能因两教练都使用PHI书而让一队改槽影响另一队。Antigravity负责认证一队一本的真实克隆/预留/技术绑定可行性，不能实现则BOOK槽位保持BLOCKED，GM仍可调球员PlayTypes/Tendency/教练其他字段。
- 现有DEV14代码尚未完成此新增审批策略；本轮仅发布GitHub规范和开发交接，**无真实游戏修改、PR合并或生产采集**。同步改GM_COACHING_OPERATIONS/DEV13/DEV14/DEV16/额度计划，旧文档中先Overall再Personal或日常切书建议已废止。 

## 2026-10-19 换帅后球队本名书归位、每赛季休赛期一次、Codex主线优先

- [DEV17](../../docs/development_tasks/DEV_20261019_17_CODEX_FIRST_MAINLINE_TEAM_BOOK_COACH_RULES_V1.md)最新规则：A队原A主教练/A手册，聘B教练后可能原生变为A队/B教练/B手册；**玩家批准技术性修改A队新Coach的PlaybookID恢复A队同名独立原生A手册**，其后再根据B教练体系与A队阵容改A书68槽，不能编辑B队书/共享书。新档建库原始本名书绑定也是技术初始化，不等于日常自由切Book。每队每游戏赛季只能在休赛期换帅**一次**；本轮只实现GM赛季/阶段约束及换帅后Book恢复接口，休赛期合同到期、员工竞价、自由市场及阶段控制明确不在本轮开发。
- **Codex先主线，AG扩展后置**：B0 DEV14-H、B1 Potential=1、B2 用现有DEV14读取/编码/审批及M3流程建设已知字段最低闭环与Book同名索引/恢复、个人防守与Intangibles。AG的CRC真实战术、51未知倾向、各位置训练模板、当前疲劳完整解码均在主线后补，唯独同名Book无法找到独占对象或现有槽位技术无法写入时给AG最小专项。缺数据允许UNKNOWN/HOLD，不伪称完整战术科学已实现。
- 本轮仅在GitHub更新开发和GM文档，未授权正式换帅/实际修改游戏或合并PR。

## 2026-10-19 用户最终确认：两个独立Codex开发窗口与球队同名书默认不变量

- [DEV18最新两窗口交接](../../docs/development_tasks/DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)覆盖DEV13/16/17早期将B0/B1/B2交给同一个Codex的错误安排。**窗口①DEV14专项Codex**负责PR#5底层：DEV14-H同档三库/真实批准、DEV15 Pot=1自动采集后清洗、Intangibles受控轮换、原生Codec/BookID限制/受控动作、`DEV14_TO_M3_HANDOFF.md`；**窗口②M系列Codex**负责PR#4既有M3A/M3B和DEV13 M3-T、30队GM决策、教练/轮换/训练/个人防守和球队本名Book恢复策略。先①形成PR#5增量交接→用户独立授权合并#5→②将main整合进#4，处理冲突并继续；#4的合并也须单独审批。两个窗口不共享上下文，只通过GitHub commit/接口报告传递。
- **玩家明确声明新档每支球队有自己队名的独立原生战术手册容器**；默认不存在此前虚构的多队共享书风险，取消为此研究物理克隆/全联盟手册身份验证的立项或主线门禁。换帅导致新教练BookID短暂指向B球队书时，以获批受控动作将**A球队的新教练BookID恢复到A球队同名书**，然后按新教练体系和A队阵容编辑A书，不操作B书。简单保持现有Native ID/原值/CAS/读回；只有真实单一对象异常才Fail Closed，不据此预先研究共享冲突。
- 换帅每队每赛季仅休赛期一次，完整员工合同/竞价/自由市场系统留后续；GM日常不写OVERALL_DEFENSE，针对球员PERSONAL_DEFENSE；DEV14当前已知教练/68槽/48具名倾向/训练与GAMEPLAY/WORLD统一机制继续复用。AG战术CRC/51未知倾向/位置模板/疲劳为后续扩展，不先阻塞主线。
- 上述是本轮Github文档改动，两个PR仍独立未合并，未修改游戏或生产事实。


## 2026-10-20 战术命名、PlayType及2D演示三级语义补录

- 玩家补充NBA2K22战术有**2D动态棋盘预览**，很多同类战术仅有跑位变体；命名常带行动位置、动作/投篮和时代线索。玩家举例`9015shot`的“90年代/1&5号位/投篮”含义是**特定假说**，还没有实机逐条验证，也不能把名称中的“发起人”当作固定实际调用者或得分人。
- 当前共享战术池为**84本原生手册、1392个不同CRC、1345有静态名字、47名字未知，原生CRC→PlayType精确认证仍为0**，比DEV23最初三队204槽/89具名CRC样本范围大。不得因共享池已经有文字解释就提升到已证 native membership。
- 新[DEV28 §3.1A](../../docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)确立先找真实CRC→原生类型，再做名字语义低置信解析，最后有来源时复原**游戏2D预览战术动作**。区分CALLER/动作发起位置/第一机会/第二解法/实战终结者；游戏2D预览存在不意味着脚本能从内存提取，也不能证明3D比赛实行动作。适量研究关键BPTI战术，不强制全部1392条人工演示；若无法截图，可以文字记录关键路线。**PR #12仅修已批F1–F4，不借此扩范围，不执行游戏写入。**

## 2026-10-20 玩家确认真实战术 '95 FIST 15 SIDE 命名文法及战术纪律联动

- 仓库`web_gm/knowledge/plays/play_pool_v1.json`确实包含`'95 FIST 15 SIDE`，`play_id=2K22_PLAY_79215b33`、CRC 0x79215B33，静态标签已和CRC匹配；玩家确认游戏中**类别为挡拆**。名称按领域规则解释：`'95`为1995年历史版本、`FIST`为挡拆动作、`15`为1号位持球动作发起/5号位掩护、`SIDE`表示侧翼执行版。85/05年同源名称可随篮球时代区分战术空间；具体1995历史球队不能仅由名字确认。
- 这是有定义的命名语法，**纠正此前一律将数字解释为无含义/位置角色全是猜测的过保守表述**。不过动作计划、谁被AI分配调用、首选与二次终结、2D预览轨迹及真实3D执行仍分层取证；当前原生`types.memberships=[]`，玩家“挡拆”是PLAYER_REPORTED_UI而非逐CRC原生enum认证，不能擅自指定type_id=4/5/6/7。
- **Play Discipline原生字段已经找到**：`config/state_io_native/player.json`的`PLAY_DISCIPLINE_TENDENCY`偏移1185/0x4A1；Coach也有`RunPlayTendency`。二者结合球员4有序PlayTypes、Playbook、Shot/Touches影响战术执行/提前机会的逻辑，OS 2K22玩家研究亦有相符经验，但不能编造精确调用概率。个人原生Tendency仍遵守玩家逐项批准与Codex受控执行；不可改能力潜力徽章。
- 权威更新：[DEV28 §3.1B](../../docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)、[共享战术池](../../docs/GM_SHARED_PLAY_POOL_V1.md)、[DEV23附录](../../docs/development_research/BPTI_DEV23_CORE_PLAYBOOK_SEMANTICS_AND_ROLE_EVIDENCE_V1.md)。后续Codex应在**知识源种子/生成器**而非只在生成JSON中维护命名规则，PR #12 F1–F4修复不加此范围，DEV28另立包。


## 2026-10-20 玩家12类战术分类、社区先行研究与PR12修复复审

- 玩家质疑之前不主动从社区获取战术知识，正确。新研究[12类战术目录与球员PlayType映射](../../docs/development_research/NBA2K22_PLAYBOOK_12_CATEGORY_AND_NATIVE_TYPE_MAPPING_V1.md)已对照Coach2K以及2021本世代社区分类与真实Fist/Quick/Give/Iso/Punch/Cut战术名称；以后默认先社区检索游戏知识，再让Antigravity验证运行时原生类型，不把尚未有本机enum理解为篮球语义未知。
- 用户列出的**12项而非11项**：单打、挡拆、挡拆外弹中投、挡拆外弹三分、挡拆选项、低位背身、高位背身、后卫背身、中投、三分、手递手、切入。**战术动作类别与球员4槽PlayType的0–15原生枚举是两个概念**；禁止将类型候选4/5/6/7冒充战术原生分类。以CRC→分类关联对象/过滤列表/原生type字段作取证目标，不预设固定块内存结构。
- Antigravity首先从内存找类型。如果找不到**可以向玩家请求截图**，哪怕需要按类别分批几十张；不必要求一次全部提交，任务到用户介入点要彻底TASK_CLOSED，禁止WAITING消耗额度。玩家此前无法提供某个任务的截图不等于以后永远禁止按需截图。
- PR #12最新修复`2f659138`静态复审发现F1–F4代码均已落地且有四项合成通过证据；**GitHub当前mergeable=false / mergeable_state=dirty**，分支落后main并与main冲突，不能宣称当前可直接合并。PR依旧Draft，V3有效/V4尚未启用。先让Codex有界解决合并冲突、保留main DEV28新文档并针对受影响文件作检查，随后玩家另外授权merge；不扩大PR到DEV28开发。

## 2026-10-20 用户批准“官方手册+玩家社区”研究先行开发规范及次世代适用修订

- 已发布长期[GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1](../../docs/GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md)，并载入AGENTS、开发边界V2及开发规划基线。未来Codex凡涉及NBA2K22 PC本世代MyLEAGUE游戏机制、字段意义、战术、教练、训练/倾向、数据采集与可操作性，应**先查原仓库材料、**主动优先检索Operation Sports/Reddit/Coach2K玩家社区、游戏攻略及2K官方手册/开发者说明**，先理解机制再开发；**PS5/Xbox Series次世代MyNBA资料也可作为共通篮球与经营机制参考**，但具体PC菜单、枚举与内存执行依旧以当前实机为准；不能让用户逐条解释网络已有知识。不因次世代版本不同就排除高价值机制资料，也不把不同版本UI或具体内存地址混淆。纯Git/机械Bug不需要无关网页检索。
- 玩家允许Antigravity在无法确认全部战术原生类别时，按类别分批请用户提供截图（可几十张），需用户介入则TASK_CLOSED不活跃等待。开发政策V2关于审批/最少验证依旧不变。
- PR #12的F1–F4先前复审通过，但最新GitHub状态dirty/mergeable=false，用户现在请求**Codex提示词修复与main的合并冲突**，不可自动merge或启动DEV28；保留最新主线的该新规范/DEV28/12类战术知识以及PR原B4/B5/F1–F4。

