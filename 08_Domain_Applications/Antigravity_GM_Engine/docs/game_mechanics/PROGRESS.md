# DEV29 游戏机制知识库：研究进度与断点恢复

> Native工程checkpoint010：[签约枚举/字段与报价读取](../../research/rea_native_control/SIGNING_NATIVE_CONTRACT.md)恢复25字段、27内部枚举及六个工资槽；ACCEPTED6不等于SIGNED8。原版GenerateContract会推导/调整条款，acquire/reset可修改球员薪资；均不作为无副作用初始化。仅静态/离线证据，无新游戏捕获/写入、UI或Save验收，原有40族研究成熟度不升级。

## 2026-10-21 R07 A/B独立复验通过：DEV29研究阶段正式结案

**当前权威状态：`DEV29_RESEARCH_CLOSED_WITH_PC22_NATIVE_IO_GAPS` / `R07_RESEARCH_CLOSED_AFTER_INDEPENDENT_RECHECK`。** [新窗口独立复验和结案报告](../development_reviews/DEV29_R07_TARGETED_INDEPENDENT_RECHECK_AND_DEV29_CLOSURE_20261021.md)已直接核对7卷694/694唯一ID、682/682原始JSON记录、12个人工R01主题（10字面+2已明示章节别名）、40个功能族和86/86锚点、20/20继承R06缺口（P0=8/P1=10/P2=2），以及R06-B十项/R06-C七项仍无直证。与修复前版本比对，八个查询状态已和写入/政策/时间权限分离，其余32族及实时读回、发布、执行和Save成熟度未升级。**以下“待独立复验”段落保留为结案前历史记录，不再作为最新状态。**

研究结案 **不等于** NBA2K22 PC本机全I/O验收。FINAL-CODEX只读工程覆盖对账、DEV28 D28-0～D28-5、选秀权V4旧+3维护、人格/媒体、任何游戏写入或存档推进，均保持**玩家另行明确批准才能启动**。

## 2026-10-21 R07独立审核A/B定向修复完成，提交独立简短复验

**最新修复交接状态：`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`，不是DEV29结案。** [独立审核报告](../development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)提出的两项问题已局部修正，详细逐项对照及自检见[修复回执](../development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)。

- A：[R07索引PART_01](catalogs/R07_ITEM_TRACEABILITY_PART_01_V1.json)中`R07.0007/K02.SHOT_ZONES`与`R07.0010/K02.PER36`保留原主题名称但明确为`GENERATED_GUIDE_TOPIC_ALIAS`；原文锚点分别是R01指南§4`K02.SHOT_CHART / SHOT_ZONES`和§3`K02.PER_GAME_PER36_ADVANCED`，原文并无这两个完整机器ID。12个手工Markdown指南主题均明确不是原始JSON主键；[694项总清单](catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)加别名阅读约定。
- B：[R07 40组能力矩阵](catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)仅将F21/F22/F23/F26/F27/F32/F39/F40的`model_query_api_status`改为真实查询证据口径；原签约/交易/选秀权+3/Staff写入与用户审批规则、日期真实来源/批次前提，保留在`execution_warning`、`data_integrity_warning`、`query_prerequisites`、`world_rule_warning`和原已有字段。**所有以前读/写/保存成熟度未因修复而升级。**
- 已再次完整读取7卷694条，检查694唯一ID和唯一来源身份；原R06-B十项未证奖项、R06-C七项空来源不变，矩阵40组、86锚点和20项（P0=8/P1=10/P2=2）缺口保留。尚需独立审核者复验和正式R07/DEV29结案决定。
- **不启动FINAL-CODEX**、DEV28、人格系统、Codex或游戏采集/写入；后续工程覆盖对账须玩家另外批准。



## 2026-10-21 R07独立审核：主体通过，机读目录两项定向修正后结案

[独立审核报告](../development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)已发布：694记录的7卷全部真实回读/ID唯一；682个源JSON记录准确匹配，R01指南12个人工主题中10个直接字面匹配、**2个需要标明人工主题别名**；40功能族ID唯一，**86/86原目录锚点存在**；20/20 R06D缺口保持，十个R06B待证奖项仍无来源。研究职责和七维数据/真实执行边界符合项目规范；**没有PC22新运行读写或存盘验证**。

当前独立审核状态：`R07_REVIEW_TARGETED_CATALOG_REPAIR_REQUIRED`；**仅两项有界修正**：① R07 PART_01中的`R07.0007/K02.SHOT_ZONES`和`R07.0010/K02.PER36`是人工R01攻略主题ID，添加确切原章节锚点和合成别名标记；② R07 40组矩阵的`model_query_api_status`在F21/F22/F23/F26/F27/F32/F39/F40混入签约/交易写入、存档或审批状态，应归回正确查询成熟度字段，并另存原执行/政策警示，**不得自行升级任何已认证能力**。修完复核，方可正式关闭R07并由玩家决定FINAL-CODEX。**无需重做R01–R06、不得提前启动DEV28/人格/Codex或真实游戏写入。**


## 2026-10-21 DEV29 R07研究总目录已发布，等待独立质量审核

[R07静态自检与独立审核检查清单](../development_reviews/DEV29_R07_RELEASE_SELF_CHECK_20261021.md)已发布。**该文档只是本研究窗口的自检，不是独立接受决定。**



**最新研究状态：`R07_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`。研究提交已完成，但此处不自行宣布R07独立审核通过。下一步是对R07机读索引、40功能族、工程成熟度和源证链进行独立审核；任何`FINAL-CODEX`、DEV28实施或游戏操作必须玩家此后另行触发。** R06独立研究验收正式状态仍为`R06_RESEARCH_CLOSED_WITH_PC22_NATIVE_RUNTIME_AND_PERSISTENCE_GAPS`，不重开R01–R06。

交付：
- [R07 中文成熟度指南](guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)——七个独立证据维度、40项功能族、真实生产证据与未来角色视角；
- [40功能族＋10既有生产证据＋20继承缺口机读目录](catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)——共86个经检查的原始目录锚点，所有游戏执行权限仍按已有手册单独审查；
- [R07逐项研究索引总清单](catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)——694条异质研究记录，**已拆分为七份可单独读取JSON**（每卷94–100项），保留项目来源与`SRC-####`索引。694不是694项当前PC22已认证Native字段；
- [R07→DEV28证据缺口交接说明](R07_TO_DEV28_EVIDENCE_HANDOFF.md)——分离已部署来源、静态注册、运行时/Save未证、有限真实交易/教练写入范围，**不是发布实施工单**。

已静态验证：40功能族的86处锚点存在；总共694项索引按原始文件与数组定位，来源编号在SOURCES中登记，七份分卷均可回读；R06-B十项错误奖项仍`sources=[]`，R06-C七项原本无直接来源仍待证。R07没有重新逐页验证全部外部网页的**语义匹配**，仅登记了来源存在性，不把原源码/原语义研究引用自动升级为`PC22_UI_VERIFIED`。本轮新实际游戏采集=0、写入=0、真正新增原版PC22图证=0、新外部SRC=0。

成熟度不得压成一个`done`：研究机制→UI可见→原生结构定位→当前存档读回→有效批次入库→模型查询→玩家批准的有界执行/保存回验，是不同事实。项目已有历史全量生产来源（30队、球员/Staff/赛季聚合、Pick、教练部分字段）与已批准普通交易范围；并不据此宣布所有原生信息都可查或签约/新秀注入/历史重力可执行。

**等待独立审核**。审核时应检查矩阵里既有工程能力的表述和历史基线是否一致，不能仅数JSON条目；若有跨档、跨版、source_id对内容不支持的发现，定向修正后再交给未来工程。



## 2026-10-21 R06-A/B/C/D独立审核通过：R07正式下一轮

正式独立审核：[DEV29 R06四轮研究验收报告](../development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)。R06-A/B/C/D研究**批准结案**，总状态`R06_RESEARCH_CLOSED_WITH_PC22_NATIVE_RUNTIME_AND_PERSISTENCE_GAPS`。实际核验R06-D **26关系ID唯一、20缺口ID唯一、79/79跨8目录原始条目引用存在**；R06-B原先Q1/Q2/Q3均已按证据边界修复（十类奖项仍无直接来源，不是目标游戏已认证）；R06-C 38概念中7项未有直接来源仍保持UNKNOWN。此为文档/机读目录独立审查，不是PC22游戏UI、数据采集或存盘读回验收。

**新的唯一研究下一轮：`R07_CROSS_RESEARCH_ROLE_OBSERVABLE_ACTION_EVIDENCE_MATRIX`**。汇总R01–R06全部原生可见信息、设置候选、作用机制、模式/时点和证据等级，明确哪些已在项目技术Registry登记、哪些实时已读/可查询/经批准可执行、哪些只是待证；不得将异质数量相加当游戏字段总数、不得替教练/球员/媒体开发人格或模型编排，也不启动DEV28/Codex/存档写入。并行待修：选秀权V4旧三届代码拒绝，由玩家以后独立授权Codex。保留R06-D原始`PENDING_INDEPENDENT_REVIEW`作为发布时历史状态，以本段独立审核结论为最终研究状态。

## 2026-10-21 R06-D — 游戏运行、历史、媒体与存档跨领域整合已发布

**当前最新研究状态：`R06_D_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`；建议下一轮唯一入口 `R07_CROSS_RESEARCH_ROLE_OBSERVABLE_ACTION_EVIDENCE_MATRIX`（需保留R06-D独立审核前提）。** R06-A/B/C/D均已完成网页研究发布，但PC22当前存档原生功能认证缺口依旧存在；并不自行将R06系列宣布为独立审核已批准结案。

- 交付：[K05/K10/K11跨域整合中文攻略](guides/K05_K10_K11_CROSS_DOMAIN_INTEGRATION_R06D.md)及[26条关联＋20项缺口机读目录](catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)。**26是语义/阶段/数据完整性/互斥和待证关系，不是26个原生引擎公式；20是证据缺口而不是20个获批工程任务。** 关联项的多目录路径与ID已逐条核对存在，源来自K04/K06/R04B/R05D/R06A/B/C，无新增已验证PC22原生数据。
- 研究继承：R06-A 86 Registry静态候选＋118菜单参数候选；R06-B 31功能/信息研究候选（含10个已修复来源不匹配、现`sources=[]`待证奖项）；R06-C 38阶段/存档研究概念。R05-D 54异质资料项＋63操作研究项各有不同口径，**任何数字均不可相加当作PC22已采原生字段总量**。R06-B Q1/Q2/Q3已定向修复但**独立复核结论尚未收到**。
- 关键分界：Gameplay/Sim/SimCast／个体Tendency与Coach系统不能混同；真实`GameID→3D完场→日历→Box→季节累计`含Normalize潜在不一致；`game_date`／历史选秀轮回／外部对照历史分别保存；游戏Save、DEV14 save身份、外部SQLite批次和SteamCloud不能混同；奖项记录/媒体预测/模拟选秀不能视为同一个原生已发生事件。
- 边界：本轮未打开当前游戏进程、未读取或写入PC22当前存档、未测试GameDate/Save重进/自然成长、未自动推进赛季，没有新增SRC或VIS原版证据。仅交知识整合与将来DEV28定向差距输入；不开发独立人格/模型调度，也不启动Codex/DEV28。选秀权V4旧`+3`代码阻断仍归独立玩家授权的Codex维护。
- 下一轮R07仅在现有K01–K12的范围内整理各独立角色**可观察事实/合法选择候选/实际原生证据/权限来源与反馈**的能力矩阵，不替任何未来Coach/Player/Media决定人格、应接受何种合同或如何行动；待R07研究完成后才考虑单独授权FINAL-CODEX做小范围工程对应审计。



## 2026-10-21 R06-C — 赛季阶段、Save/Save as/Autosave与跨季历史留存研究已发布

**最新断点：`R06_C_RESEARCH_PUBLISHED_WITH_PC22_PHASE_SAVE_RETENTION_GAPS`；下一轮唯一入口`R06_D_CROSS_DOMAIN_SYNTHESIS_AND_GAPS`。** R06-A/B/C研究均已发布，仍不代表当前PC22 UI、内存运行时及持久化已验证。R06-B独立审核Q1/Q2/Q3有界修复已提交但**尚未获得后续独立审核结论**；R06-D整合时应保留该事项，不得宣称全部31项有直接来源。

- [K11赛季与存档中文研究§§15–22](guides/K11_SEASON_SAVE_PERSISTENCE_R06C.md)、[38类候选信息/阶段目录](catalogs/R06C_SEASON_SAVE_PERSISTENCE_RESEARCH_V1.json)、[SRC-0187..0199](SOURCES.md)13条真实外部资料及[视觉证据边界](visuals/EXTERNAL_VISUALS.md)已经发布。38是原料概念，不是原生已采38个字段；目标存档PC22实机读取、保存/重进校验、跨年历史内容认证、日历推进、新版VIS均为**0**。
- 证据重点：2K22玩家在OS推荐Offseason分阶段Save检查点，但作者也承认某些流程来自旧版本；同版PC Steam有Save/Save as退出后未保存的孤例与另一些跨模式文件丢失传闻，不能推导普遍Bug或确定存档数上限；2K官方明确离线MyLEAGUE可用，云同步另属平台侧备份，不等于游戏内保存。NBA2K22 PS4玩家比赛/赛程示例不可当当前PC设置值。
- **三重时钟**：真实游戏Season/GameDate由游戏权威，1984→2020外挂选秀循环由已完成并获批选秀驱动，数据批次/仓库时间不推导游戏时间。五种信息实体：真实GameID/Box、游戏存档revision、DEV14 managed save身份、GitHub发布数据库、外部角色历史记忆必须分开。
- 下一轮R06-D只做K05/K10/K11与R01–R05已知机制的**数据—菜单—作用—版本—原生可读性—执行边界**交叉目录和缺口映射，不启动DEV28/Codex的代码工作，不自动采集/推进/保存，也不建立任何角色人格。R07之后才最终小型FINAL-CODEX。


## 2026-10-21 新窗口R06-B独立质量审核（不阻断R06-C）

[独立审核报告](../development_reviews/DEV29_R06B_CROSS_WINDOW_RESEARCH_QUALITY_REVIEW_20261021.md)：跨窗恢复正确、R06-A没有重做、R06-B 31项唯一/13来源/9缺口符合文件统计；研究职责和版本证据边界合格。**R06-B初稿保留，但10项奖项候选均使用不能直接证明该类别的SRC-0178，应在R06-D合并前定向修正来源或降级为未认证候选**；`worldline.native_eras_feature:false`不得被理解为目标PC22已完成排除性实机认证。建议状态`REVIEWED_TARGETED_SOURCE_REPAIR_REQUIRED`，不是R06-B全能力已审定。新网页窗口入口旧R01/R02提示需以本PROGRESS权威新指针覆盖。**R06-C仍为唯一下一轮，允许直接继续**；不启动Codex/DEV28/任何Agent或游戏写入。

## 2026-10-21 R06-B 质量审核Q1/Q2/Q3定向修正

根据[独立审核报告](../development_reviews/DEV29_R06B_CROSS_WINDOW_RESEARCH_QUALITY_REVIEW_20261021.md)，已将R06-B目录10项不被SRC-0178直接支持的奖项类别更正为`RESEARCH_CANDIDATE_UNSOURCED`、`sources=[]`；MVP仅关联Past MVPs历史菜单线索，31项明确为研究功能/信息概念不是31个已采字段。`native_eras_feature`不再使用排他性`false`，改`null`和`UNKNOWN_NOT_NATIVE_VERIFIED`。攻略/Bootstrap/README同步。**这是按审核问题修复并自查，独立审核是否通过仍由外部审核决定。**R06-C的研究任务不受阻断。

## 2026-10-21 R06-B — 历史纪元、奖项、纪录、媒体与规则历史已发布

**当前最新研究状态：** `R06_B_RESEARCH_PUBLISHED_WITH_PC22_UI_AND_HISTORY_GAPS`。新的唯一下一轮：`R06_C_SEASON_PHASE_ADVANCEMENT_SAVE_PERSISTENCE_RESEARCH`；然后R06-D跨域整合，再R07和最终小型FINAL-CODEX。R01–R05已按各自正式状态结案，R06-A保留已出版结论且未重做。此次为DEV29纯网页研究，未启动Codex、DEV28、独立角色人格、游戏内存、存档写入或日历推进。

交付：[K10历史/奖项/媒体中文机制攻略](guides/K10_HISTORY_AWARDS_MEDIA_R06B.md)；[31项机读目录](catalogs/R06B_HISTORY_ERA_AWARDS_MEDIA_RESEARCH_V1.json)；[SRC-0174..0186](SOURCES.md)共13个有版本限制的来源；[视觉索引](visuals/EXTERNAL_VISUALS.md)本轮新增合格原版PC22菜单截图为0。新资料覆盖历史Draft Class/1984–2020外挂选秀轮回与2K23 Eras的**不可等同**、历季奖项与退役球衣、NBA/球队/单季/生涯/季后赛纪录、MyLEAGUE社会媒体/Power Rankings/Mock Draft文字资源、休赛期Rule Changes的旧版参考。**31项不代表31项当前存档已采集或可写**。

重要结论：原生奖项/纪录/媒体播报 ≠ 真人现实历史结果，也 ≠ 外挂可修改历史冠军/球员能力；2019和2023的相关用户讨论只能跨代辅助认识。R06-C专门研究真实赛季阶段、Autosave/手动Save、重启与跨季留存，不在R06-B提前假定历史记录持久性。


## 2026-10-21 R05-A/B/C/D独立审核：接受研究结案，选秀权V4执行代码待同步

独立审核报告：[DEV29 R05审核与V4工程差距](../development_reviews/DEV29_R05_INDEPENDENT_REVIEW_20261021.md)。**R05研究结案正式接受**，保留原状态`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`。审计核对D目录54数据候选、63操作研究项、12联动、12缺口无重复标识；63项中**53个合法选项范围仍UNKNOWN**，来源到SRC-0162（包含与旧SRC-0137同一网页的交叉引用），这不是PC22 UI/实时读数/真实执行的全部认证。**不需要R05返工**，R06仍NEXT且不开发媒体/球员/教练人格。

**G04工程阻断（不阻断研究结案）**：V4已于`config/gameplay_policy.json`撤销原三届人为上限，现行`src/draft_assets.py`（含`capture_assets()`对外返回旧`tradeable_draft_years`）、`src/gm_core/calculations.py`、`src/gm_core/trades.py`、`src/approved_trade_executor.py`尚有+3/三年拒绝逻辑；第4/5届即使有原生5年300条实证也未能合法执行。留给以后用户单独授权的**Codex有界代码/测试同步任务**，不得机械改成固定5年上限，不改旧快照、不自动执行游戏交易。


> [**R05及所有后续轮次的范围前提**](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：本项目六阶段模型流程和DEV29边界以项目级文档为准。本知识库只提供原生游戏事实、玩法、参数和作用，不开发未来Coach/Player人格或固定决策程序。R04研究已结案，R05-A工资帽/合同和R05-B交易机制研究均已发布，R05-A/B/C/D经营研究均已出版，R05完成网页资料研究；下一轮R06规则/历史/媒体/存档研究尚未启动。选秀权三届世界上限于2026-10-21取消。

## 2026-10-21 R04独立审核与R05研究范围纠正

- 独立审核已直接读取R04-D 8例互动图谱、双语义侧表与109条主目录并和现有交易/签约工程说明比对：**109项ref无重复且与主目录逐一对应；其中72为有静态Registry/Profile的真实注册字段，37为未认证的研究候选，109项本轮均无current save实时采集值**。R04其余原生99倾向槽位、外部99标签、徽章、动机等是独立研究目录，不能将109宣告成“全游戏字段总数”。签约执行仍保持`approved_signing_v1_unvalidated`。R04的研究交付可结案；本审核未独立检验所有网页链接事实或运行游戏/测试。
- 用户纠正DEV29职责：**这里只搜集游戏信息、设置/参数/玩法/联动和所有模型需要的原材料**；Coach、Player的独立人格/决策系统尚未开发；角色意志如何模拟和协商由其他任务决定。ATLAS八例不是人格设计、不可作为正式Agent规则。六阶段工作流：**采集→分析→独立教练→独立球员→各队GM→汇总并交执行模型**；实际玩家批准与原生读回始终独立。权威边界：[RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md](RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)。
- **R05按A/B/C/D分批研究、不需要回头返工R04**：集中研究NBA2K20–23合同/薪资帽/预算/Staff/Scouting/Draft/Free Agency/交易及合法游戏操作，给未来角色提供**原始可观察信息与可用动作**；不开发薪资谈判算法/球员决策树、教练性格、媒体行为或执行器，成果按原R05研究方法写GitHub并关闭当前轮。


**当前权威研究状态**：`R06_D_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`（2026-10-21）；R06-A/B/C为已发布历史批次。R05-A/B/C/D已由用户最终批准研究结案，保持`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`；R04保持批准结案，选秀权V4代码同步留独立Codex任务，不阻断R06研究。
**当前最新：`R06_D_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`；建议下一轮 `R07_CROSS_RESEARCH_ROLE_OBSERVABLE_ACTION_EVIDENCE_MATRIX`（尚未启动，R06-D待独立审查）。** R01-A/B/C/D的公开资料研究全部结束；R01已形成带版本边界、GM数据需求、公式和质量检查的中文攻略，**不是说PC22 UI/内存/逐场采集已经实现**。R01遗留UI未知列入以后单独取证待办，**不再重复R01论坛检索**。研究计划：**[DEV29 V3 多智能体世界研究路线](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)**（原[V2](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)网页GPT多轮交付方法继续有效）。

## 当前批次地图

| 轮次 | 工作主题 | 最新状态 | 权威产物 |
|---|---|---|---|
| R01-A | Schedule、Game Log与逐场Box候选、篮球统计派生 | PUBLISHED | [K01/K02](guides/K01_K02_GAME_STATS.md) §§0–8；SRC-0004..15、VIS-0001..03 |
| R01-B | Stats视图切换、Shot Chart、旧季历史与数据异常 | PUBLISHED | 同一指南§§9–13；SRC-0016..25、VIS-0004..06 |
| R01-C | 官方同版次世代Box证据、PS4模拟器参数、PC旧版本质量异常 | PUBLISHED | 同一指南§§14–18；SRC-0026..28、VIS-0007 |
| **R01-D** | **最后一轮PC22原版公开视觉取证；证据矩阵和精简截图需求** | **`RESEARCH_CLOSED_WITH_PC22_UI_GAPS / TASK_CLOSED`** | **同一指南§§19–22；SRC-0029；本轮合格新VIS为0；来源排除审计已写入图证索引** |
| **R02-A** | **教练、攻防、Book/PlayTypes/Freelance/ACE基本语义、原生已有接口与权限** | **PUBLISHED_WITH_OPEN_ITEMS** | [K04第一批中文攻略](guides/K04_COACH_AND_PLAYS.md)；SRC-0030..39、VIS-0008 | 
| **R02-B** | **ACE自动覆盖与Series/Freelance、Center双挡拆字段与TagOnRoll旧版可见性、CPU-vs-CPU差异、多角色权利** | **PUBLISHED_WITH_OPEN_ITEMS / TASK_CLOSED** | [K04 §§11–17](guides/K04_COACH_AND_PLAYS.md)，SRC-0040..47；新合格PC菜单图证0 |
| **R02-C** | **有界原版PC22教练、ACE、Book、个人防守UI搜证；封存UNKNOWN，四角色能力原料目录** | **`RESEARCH_CLOSED_WITH_PC22_UI_GAPS / TASK_CLOSED`** | [K04 §§18–21](guides/K04_COACH_AND_PLAYS.md)，SRC-0048；[角色能力研究JSON](catalogs/K04_ROLE_CAPABILITY_RESEARCH_V1.json)；新合格PC22 UI图证0 |
| **R03** | 训练、健康、伤病、自然成长 | **APPROVED_RESEARCH_CLOSED_WITH_NATIVE_DATA_GAPS** | [K06](guides/K06_TRAINING_HEALTH_GROWTH.md)与[R03交付断点](R03_COMPLETION_REVIEW_CHECKPOINT.md)，用户已批准结项 |
| **R04-A** | 球员Vitals、39项已登记属性、16项Durability、职业成长、Badge | **PUBLISHED_WITH_OPEN_ITEMS** | [K03/K12指南](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、[字段目录](catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)、[徽章参考](catalogs/PLAYER_BADGES_R04_A_REFERENCE.json)、SRC-0072..0082 |
| **R04-B** | 99原生倾向字节/99同版独立导出标签、四PlayTypes/Initiator、Touches与Shot/Discipline以及Sim vs 3D分歧 | **PUBLISHED_WITH_BEHAVIOR_GAPS / TASK_CLOSED** | [K03/K12 §9–16](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、[99+99研究目录](catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)，SRC-0083..90 |
| **R04-C** | 三项合同职业动机、人品徽章候选、Morale/Chemistry、自由市场个人偏好、士气与角色自由谈判 | **PUBLISHED_WITH_NATIVE_MOTIVATION_GAPS / TASK_CLOSED** | [K03/K12 §§17–23](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、[R04-C动机/人格目录](catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)、SRC-0091..0105 |
| **R04-D** | 109项Profile及候选双语义侧表、八种玩家⇄GM⇄Coach⇄媒体的自主协商/拒绝/安全执行衔接案例 | **PUBLISHED / RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS** | [Player Agent Interaction Atlas](catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)、[109项双语义侧表](catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)、[K03/K12 §§24–29](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、SRC-0106..0113 |

| **R04 整体** | **K03/K12 完整球员职业生命周期、倾向、徽章、人格、合同偏好和选择权** | **RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS / R04-A/B/C/D ALL_PUBLISHED** | [R04独立研究任务书](../development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)，后续分R04-A/B/C/D |
| **R05-A** | **工资帽、税线/apron、真实球队经营财务、17项合同Native字段、4种报价曲线、Bird/RFA/QO/Cap Holds/FA分期** | **PUBLISHED_WITH_FINANCE_EXECUTION_GAPS / TASK_CLOSED** | [K07/K08/K09 §§0–7](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05-A机读目录](catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json)、SRC-0114..0128 |
| **R05-B** | **16项交易菜单/市场候选、2021–22 CBA工资匹配分档、原生5年300条未来签；**旧三届世界限制已于2026-10-21撤销**、15常规＋2双向＋13活动名额和有界交易器** | **PUBLISHED_WITH_TRADE_UI_AND_CBA_GAPS / TASK_CLOSED** | [K07/K08/K09 §§8–15](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05-B机读目录](catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json)、SRC-0129..0144、VIS有界审计 |
| **R05-C** | **员工8岗13字段、次世代四部门17人名额、球探报告/估计/榜单/侦察进度、Draft Class菜单与1984–2020历史班真实源** | **PUBLISHED_WITH_STAFF_SCOUT_DRAFT_UI_GAPS / TASK_CLOSED** | [K07/K08/K09 §§16–22](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05-C机读目录](catalogs/R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json)、SRC-0145..0160 |
| **R05-D** | **54项原生注册/候选信息、63类菜单/市场操作候选、12项跨领域机制联动、12项PC22原生缺口；更新选秀权世界规则取消三年限制** | **PUBLISHED / RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS** | [K07–09 §§23–29](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05-D机读全集](catalogs/R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json)、[政策V4](../../config/gameplay_policy.json)、SRC-0161..0162 |
| **R06-A** | **全局设置、LIVE 3D USER/CPU与CPU/CPU、Calendar Sim独立参数、Normalize统计与原生Registry证据分级** | **PUBLISHED_WITH_PC22_RUNTIME_VERIFICATION_GAPS / TASK_CLOSED** | [K05/K10/K11世界指南§§0–6](guides/K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md)、[86注册候选+118项菜单研究](catalogs/R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json)、SRC-0163..0173 |
| **R06-B NEXT** | **历史纪元、联盟规则改变、奖项/纪录、媒体可观察信息；和2026世界线切换分开** | **NEXT / NOT_STARTED** | R06研究下一独立批次，仅知识原料，不开发媒体Agent |
| **R06-C PLANNED** | **常规赛/季后赛/休赛期推进、Autosave和Save Slot、跨期数据留存及可靠恢复** | **PLANNED** | R06-B后继续 |
| **R06-D PLANNED** | **K05/K10/K11资料联动、原生可读/可改/UNKNOWN和最终领域知识目录** | **PLANNED** | R06-C后继续 |
| R07（原R06） | 多角色知识矩阵、GM/球员/教练/媒体决策证据及可执行能力查漏 | NOT_STARTED | 后续 |
| FINAL-CODEX | 源/图索引、已有Registry/M0/DEV14/SQLite与DEV28能力差距收尾 | NOT_STARTED | **只在主要网页研究R01–R07结束后** |

## R01-D到底新增/没有新增什么

- **新增确有PC平台指向的文字来源`SRC-0029`**：2K22本世代Operation Sports玩家`res2`确认“PC with default rosters”并贴Setup/Simulation等参数；但他在首帖称自己主要玩`Season Mode`、MyLeague参数多从别的玩家转载再修改，**这不是PC原版MyLEAGUE统计菜单屏幕证据**。此处不提升任何Stats、Box或Game Log字段。
- 本轮面向PC MyLEAGUE、Steam Screenshots、各类公开视频/攻略检索后**未获得同时满足NBA2K22/PC/无UI Mod/MyLEAGUE/可读目标统计菜单的原图/视频帧**：新增`PC22_UI_CONFIRMED = 0/6`、新增合格VIS为0；并不说明六项游戏功能不存在。
- Steam外层`View Stats`属于平台成就入口；网上的`MyCareer Hot Zones`、真实NBA.com Box、2K22 PS5 MyNBA/2K23、`PC Remastered`的自定义菜单**均不能作为PC22原版认证**。
- 审核截图来源与许可，未上传任何第三方图片。资料足够完善“该查什么/怎么判数据质量/GM该如何利用原始Box”，但**不能捏造本机真实数据**。

## R01最终目标证据表

| 目标 | 目标PC22状态 | 已知跨版本事实 | 未来取证队列 |
|---|---|---|---|
| 1. Stats、Player Stats、Team Stats、League Leaders完整页签和筛选 | `UNKNOWN` | `KNOWN_IN_SERIES`：老版MyLEAGUE、PS5 MyNBA其它版统计页 | `DEV28_NATIVE_DISCOVERY_REQUIRED` |
| 2. Player Game Logs独立入口或Calendar→每场Box | `UNKNOWN`；没找到独立标签不表示无逐场数据 | `KNOWN_IN_SERIES`：老版Calendar/Daily View、2K20旧比赛Box | `DEV28_NATIVE_DISCOVERY_REQUIRED` |
| 3. 主客双方Player/Team Box原生表头、合计及DNP/Starter | `UNKNOWN` | `KNOWN_IN_SERIES`：2K22次世代官方Box表格文字 | `DEV28_NATIVE_DISCOVERY_REQUIRED` |
| 4. Per Game、Per36、Advanced本机字段/操作提示 | `UNKNOWN` | `KNOWN_IN_SERIES`：2K16 MyLEAGUE、2K22 PS5、2K23 MyCareer | `DEV28_NATIVE_DISCOVERY_REQUIRED` |
| 5. Shot Chart赛后及历史比赛回看、可选窗口 | `UNKNOWN` | `KNOWN_IN_SERIES`：2K22玩家赛后文本报告，MyCareer热区不可代替 | `DEV28_NATIVE_DISCOVERY_REQUIRED` |
| 6. 跨月/跨季旧Box、赛程、季后赛记录保留期 | `UNKNOWN` | 其它版本保留粒度不同；没有可外推的PC22固定期限 | `DEV28_NATIVE_DISCOVERY_REQUIRED` |

**证据等级无变化**：没有新`PC22_UI_CONFIRMED`、`PC22_NATIVE_READ_VERIFIED`、`PROJECT_CAPTURED`、`GM_QUERYABLE`。只有研究机制`DOCUMENTED_WITH_VERSION_LIMITS`。PS4玩家提供的模拟器设置为当前世代间接证据，**不是Stats菜单的`CURRENT_GEN_ANALOGUE`截图**。

## 最小外部补证（非R01继续网上研究）

若玩家日后自然有机会查看正在使用的原版PC22 MyLEAGUE，分两组、总计**优先约4张**：①Stats首页/按钮与Player Stats切页各1张（解决1/2/4）；②已完成比赛Calendar入口及同场Box表头各1张（解决2/3）。其它列未显示时仅增加一张横向/另一队切页图。Shot Chart、旧赛季Box可在**已有真实历史页面**按需要补1–2张，不能为取证擅自模拟/推进正式存档。详见[VIS待办与许可](visuals/EXTERNAL_VISUALS.md)，以及[K01/K02第20–21节](guides/K01_K02_GAME_STATS.md)。

**后续责任**：DEV28/Antigravity只获得明确的`PC22_ORIGINAL_STATS_UI`和`NATIVE_READABILITY`积压清单，之后是否授权由玩家另行决定；这份研究结案**不启动DEV28**、不开始Codex、游戏进程、数据采集、存档修改或普通球员属性变动。取得新截图时仅局部升级目标列与VIS/SRC，不重新开启R01全面网络检索。

## R02历史启动入口（归档，仅供理解，不是当前待执行任务）

1. 读取本`PROGRESS.md`与[DEV29 V2](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)、知识库README、Mechanism Card模板；**不要再重复K01/K02研究**。
2. 阅读项目已有`web_gm/manuals/GM_COACHING_OPERATIONS.md`、`docs/40_COACHING_EXECUTION_RUNBOOK.md`、`docs/development_research/NBA2K22_PLAYBOOK_12_CATEGORY_AND_NATIVE_TYPE_MAPPING_V1.md`及DEV28规划的相关教练/战术段；避免把现有已做的19 Coach defaults/18 opponent defense/PlayTypes重新定义成虚构待建系统，精确已实现/已在目标游戏验证另分层。
3. 主动搜索**2K20–23、NBA2K22 PS4/PC MyLEAGUE/PS5 MyNBA**的玩家操作截图、社区战术帖、教练游戏计划、POE、ACE、Playbook、Freelance、12种战术分类/球员4个PlayTypes、战术纪律与防守调整，标清版本/合法枚举/联动/GM决策证据/已知BUG；不要把截图和真实内存混用。
4. 直接写实际**中文经营与战术攻略**到`docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md`（可拆R02-A/B），同步SOURCES、VIS、PROGRESS及README，提交GitHub回读。**不要先产出仅规划的任务清单。**

> 终态：`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS / DEV29_R01_D_TASK_CLOSED / NEXT_R02`。

## 2026-10-20 新增多智能体游戏目标（不改变当前NEXT_R02）

玩家正式提出：项目的最终价值是**自主GM、教练、球员、媒体等角色在真实NBA2K22游戏状态中进行选择、谈判、试错并产生涌现**，而非唯一GM优化器。为此DEV29新增完整球员研究R04，保留R03训练一般机制，原R04/R05/R06顺延为R05/R06/R07。**R02仍为下一轮，R01已结束，无需重新做统计文献搜索**。研究所有信息不仅问“GM能看到和修改什么”，还应问“Player/Coach/Media能够看到、提出、拒绝什么，原生字段是否可安全映射外挂人格、哪些应优先独立SQLite保存”。完整规划见[DEV29 V3](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)。这只是规划更新，R04尚未开始、未修改游戏或角色数据库。

## R02-A（2026-10-20）：本轮实际研究交付与断点

**状态：R02_A_PUBLISHED_WITH_OPEN_ITEMS / TASK_CLOSED；R02领域整体未COMPLETE。** R01已经关闭并保留PC22 UI证据缺口，不重新研究。

**可直接用于GM的中文机制卡**：[K04_COACH_AND_PLAYS](guides/K04_COACH_AND_PLAYS.md) §§0–10，明确分清：
- 19项Coach defaults（六POE、8个教练体系、BenchDepth/RunPlay/Zone/BenchUtilization/Tempo/HelpDefense/四Freelance和BookID）的原生含义、GM可用/只读限制；
- 球队同名**战术书容器**68槽Regular30/Bench20/Endgame10/Favorite8与**共享1,392 CRC池**，书归属不是战术条目独占；CRC真实战术类别映射仍UNKNOWN；
- 玩家报告12类目录类别和球员4个有序PlayTypes的**不同枚举**，四Freelance也独立于这些对象；
- 官方2K22防守改进 [SRC-0030] 与2K22同年玩家触球/纪律/自动Playcalling及防守BUG的冲突报道 [SRC-0031..34]；不把建议Touches=50/Discipline=100当游戏规律；
- ACE动态层 vs 静态Coach/Playbook设置 vs 3D实际调用的分层；2018–20旧版意见仅KNOWN_IN_SERIES；
- **日常GM只能提案逐人PERSONAL_DEFENSE，整体OVERALL_DEFENSE只读**，不修改能力/潜力/徽章。换帅后Book重绑与slot更新必须按本队政策和玩家逐笔批准。
- 以场次/阵容/类型与真实对手Box为起点，提出HOLD或有依据的POE、战术书、个体防守候选；不得因缺少真实逐场数据直接编胜率效果。

**源与图**：[SOURCES](SOURCES.md)新增**SRC-0030..0039**（10项），含2K官方、同年OS论坛与编辑评测、Xbox One本世代文字菜单、PS5 MyNBA球队增补Playbook报告、较早ACE分歧、同年控制指南；[VIS清单](visuals/EXTERNAL_VISUALS.md)新增**VIS-0008**（2021年2K22帮助防守图文上下文，**不是PC原生UI认证**）及**VIS-TODO-R02-01..05**，没有第三方图片上传。

**本轮严格保留UNKNOWN**：PC22本机Coach/ACE/Offensive/Defensive所有菜单和动态覆盖；特殊OnBall5/Hedge5/TagOnRoll、2D预览到原生CRC/类别对应；四Freelance实际自动切换/真实频率；整套执行器能力以当前DEV14部署/同批来源而非K04假定。

### R02-B历史启动方法（已完成）

1. 先从GitHub读**本PROGRESS**和[K04 §§0–10](guides/K04_COACH_AND_PLAYS.md)、[SRC-0030..39](SOURCES.md)、[VIS-TODO-R02](visuals/EXTERNAL_VISUALS.md)，不要重新整理已有19/18项原生schema。
2. 优先公开**NBA2K22 PC本世代无模组MyLEAGUE**的Coach Gameplan、ACE/Offensive Settings、Personal Defense、Freelance和2D战术板界面；如只有Xbox One/PS4同代素材，等级为CURRENT_GEN_ANALOGUE。
3. 针对ACE和Freelance、Play Discipline/Run Plays与个人防守的冲突寻找同年实测及不同意见；游戏效果未知不承诺胜率公式，旧版本不升级为PC22事实。
4. 补K04具体截图与菜单、来源和图索引，形成下一批可直接读的攻略并提交GitHub回读。若所需原生数据取不到，保留DEV28/Antigravity未来待认证项而不启动它们。
5. **权威研究路线已更新为DEV29 V3的R01–R07**：R03训练，R04人物完整资料/Player Agency，R05经营，R06世界，R07总矩阵；不要从V2旧表误标后续轮次。FINAL-CODEX须所有R01–R07后。

**执行边界**：纯文献与GitHub知识文档。没有运行Codex、DEV28、游戏进程/采集/模拟或存档/玩家能力修改。R02仍有未完成项，**不能标全部完成**。

## R02-B（2026-10-21）：研究成果、反证与研究下一轮指针

**R02-B已实际完成并发布**；R02总体仍`INCOMPLETE_WITH_PC22_UI_GAPS`，不能声称原版PC22教练与战术动态覆盖已完全认证。R01继续保持`R01_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`，没有再次搜统计旧菜单。

- [K04 §§11–17](guides/K04_COACH_AND_PLAYS.md)新增：**2022年ACE关掉仍重置Defensive Custom**与**ACE Off可保留人工手动调度**的对立玩家报告；将静态原生Coach值、赛前Gameplan、暂停后动态覆写、3D执行分成四层。`SRC-0040/0041`
- 2K22早期Xbox玩家说设置Series后仍回Freelance；同年**Xbox Series MyTEAM**需场上Run Freelance两步激活，是跨模式的诊断线索，不意味着PC离线MyLEAGUE有相同按钮或自动CPU执行。`SRC-0042/0043`
- 2K16的On-Ball Screen/Hedge(Center)讨论把**持球者B、掩护者S、双方防守者DB/DS**分别标识；2K19提到Tag On Roll在赛前菜单不可见但SimCast页仍见。旧版场景帮助理解字段，但**PC22精确触发、UI和值域/可执行性均UNKNOWN**。`SRC-0044/0045`
- 2K22 PC Forum作者明确公开“控制所有队、逐场看3D CPU-vs-CPU MyLEAGUE，不用Fast Sim”的研究方式；不能用人控MyTEAM调ACE的经验等同这种比赛。`SRC-0046`
- 2K21次世代玩家将Freelance/Series/Timeout与Gameplan定义为多个入口，不能套用于本世代。V3新增教练/GM/球员/媒体的观察、提议、否决、长期学习信号与外部SQLite语义区分。`SRC-0047`
- [SOURCES](SOURCES.md)新增**SRC-0040..0047**；[VIS](visuals/EXTERNAL_VISUALS.md)新增**R02-B视觉负面核验和R02-C的2组最小原版截图需求**，**未新增合格VIS编号或PC22_UI_CONFIRMED画面**。所有外部图片留网页原始链接，未上传媒体文件。

**本轮最重要的未知**：PC22完整Coach/Offense/Defense/ACE界面、ACE真正覆盖保存规则、Freelance四槽调用概率/2D形态、Series在CPU对CPU被选择的方式、十二类Play CRC→真实category id以及个人防守OnBall5/Hedge5/TagOnRoll/StayAttached/PreRotate原版UI与执行条件。项目已记录的19教练原生、18对手防守、34 Freelance raw和68 Book槽**保持已有等级**，不得因为文学调研重写原生字典或批准执行。

### R02-C历史启动说明（已执行并结案）

1. 从GitHub读取本PROGRESS与[K04 §§11–17](guides/K04_COACH_AND_PLAYS.md)、[SRC-0040..0047](SOURCES.md)、[VIS-TODO-R02](visuals/EXTERNAL_VISUALS.md)，**优先目标PC22原版画面，而非继续堆积旧论坛讲法**。
2. 若有清楚原版PC22 Coach、ACE/Freelance、Book与个人防守视图，登记原链接/确切版本/菜单位置/页签/可辨字段/版权，按证据升级。优先原版PC22 **赛前Coach页**和**指定对手个人防守/Book的动态2D预览**两个画面组合。只有PS4/Xbox One一代画面则标`CURRENT_GEN_ANALOGUE`。
3. **一次有限公开检索**仍拿不到可靠原版PC22界面，保留UNKNOWN；把目标画面需求交未来玩家可选截图/已获授权Antigravity的原生专项，**关闭R02公开文献阶段直接进入R03团队/个人训练、疲劳、伤病和自然成长**。不因此启动DEV28或Codex。
4. V3的后续顺序是R03训练健康、R04全量球员及Agency、R05财务合同经营、R06历史规则与媒体、R07全角色矩阵、最后FINAL-CODEX；V2旧排期不再权威。每轮更新GitHub并回读。

> 权限与边界：R02-B只做网页研究及GitHub文档更新。用户批准前不启动游戏内存扫描、正式存档、比赛模拟、球员属性编辑、DEV28、Codex或外部Agent实现。研究可提出不同教练目标和反对声音，**不将篮球策略强制为全队最优模板**。

## R02-C（2026-10-21）：最后一轮原版PC22视觉取证已结束，R02公开研究正式关闭

**权威状态：`R02_RESEARCH_CLOSED_WITH_PC22_UI_GAPS`；下一轮R03，不再发起R02-D。** 这是研究结案而不是本机Coach菜单和比赛AI原生效果完全认证。

**本轮直接完成**：
- 专项检索NBA2K22 PC vanilla MyLEAGUE Coach Gameplan/POE、Freelance、ACE/Offensive/Defensive Settings、12类战术/2D战术板及Personal Defense。**新`PC22_UI_CONFIRMED=0`**。没有凭Steam商店图、PS5官方MyNBA Conditional Coaching、PC Remastered、MyTEAM临场按键或无时间戳视频“补全”PC22菜单。
- 保留唯一新增同版**有新增机制事实的文本源SRC-0048**：2021年MyLEAGUE玩家起初找不到Freelance跨场保存，12月补述比赛中改动后可按该队保存；**具体平台未知，不能当PC22 Native Persistence证明**。
- 发现网页声称`NBA2K22 MyLEAGUE精确分钟锁定`但文章显示**早于2021-09-10游戏发售**，又与本项目玩家已确认的AI重新分配分钟规则冲突；只记于排除清单，不允许提升来源等级。
- 在[K04 §§18–21](guides/K04_COACH_AND_PLAYS.md)给出目标PC证据终态矩阵、静态/临场/实战区别、最少两组未来截图请求、四角色**观察/合法动作/机制反馈/主人与否决权**表。没有机械“最优建队/战术”强制规则。
- 新增**纯研究数据目录**：[K04_ROLE_CAPABILITY_RESEARCH_V1.json](catalogs/K04_ROLE_CAPABILITY_RESEARCH_V1.json)，10类角色可观察/可选择原料，标明源字段、证据等级、适用角色、允许提出的选择、原生写入审批边界和真实反馈条件。**文件不是Agent程序、可执行动作schema、数据采集或玩家批准**。有字段不等于本次存档已采到值。
- 更新[SOURCES](SOURCES.md)至`SRC-0048`、[视觉索引](visuals/EXTERNAL_VISUALS.md)的R02-C搜证与后续只读需求，**VIS仍仅有0001..0008且未升级原版PC22教练UI等级**。

**R02学到的完整原料边界**：项目19教练默认设置/18针对对手防守/34原生Freelance/68 Book槽继续保留已建立技术证据；12个战术类别与PlayTypes四槽需要与具体play CRC匹配，当前精确CRC→native type仍UNKNOWN。ACE是否动态覆盖、Series/4Freelance实际被CPU调用及历史保存窗口未实证。本项目日常GM**仅修改经批准的个人防守，不写整体OVERALL；不直接编辑普通球员能力/潜力/徽章**。教练、GM、球员、媒体Agent的独立目标/接受/拒绝/谈判可作为未来模型选择自由，**不是本轮开发的Agent、不是真实2K游戏自带的人格API**。玩家真实批准始终是游戏写入必要条件。

### R03-A历史启动入口（已完成；仅保留断点历史）

1. 从GitHub读取本PROGRESS、[DEV29 V3](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)、[R04人物专项](../development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)、[K04联动](guides/K04_COACH_AND_PLAYS.md)、已有训练开发/运营手册，以及SOURCES/VIS尾部；**不要重开R01/R02**。
2. 搜官方NBA2K20–23与同年玩家训练操作、MyLEAGUE全队/个人训练、恢复/休息、负荷、疲劳、伤病/身体耐久、医疗员工、赛场 vs 快模拟对成长的影响；按PC22本世代/PS4同代/PS5次世代/其它版本严格分层。不因为有PS5 MySTAFF/Prep Hub照片就冒充PC22。
3. 从游戏原料角度列出`WHAT_CAN_OBSERVE / CHOICES / CONSTRAINTS / NATIVE_EFFECT / WHO_CAN_PROPOSE_OR_REFUSE / LEARNING_SIGNAL`，让教练、GM、球员和媒体可拥有不同偏好和未来协商空间。**不能直接改变自然能力属性，不能用优化配方夺走球员选择权**。只调查机制和已有来源，未确认的真实可写操作标UNKNOWN。
4. 直接创建`guides/K06_TRAINING_HEALTH_GROWTH.md`的有实际来源的第一批中文攻略，更新SOURCES/VIS/PROGRESS/README并提交GitHub回读；R03可分A/B/C。**R03共性训练健康 ≠ R04完整球员个人资料/徽章/人格/全部耐久及合同倾向专项**。
5. 随后按V3：R04全量球员、R05经营与谈判、R06世界与媒体、R07全角色交叉矩阵，最后FINAL-CODEX；**DEV28/Antigravity只在另行授权后定向原生取证，不是本轮启动**。

> **DEV29 R02结案与权限**：研究发布后无任何DEV28、Codex、游戏进程、真实存档或人物属性变更。新PC22截图以后仅增量补R02相关UNKNOWN，不导致重新开启R02公共资料无限检索。

## R04-A（2026-10-21）：球员档案首批研究交付

R03已由用户批准结项；独立审核未来由其他模型负责，DEV29研究窗口只发布研究。R04-A发表[K03/K12](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)，注册55个本机属性（39非耐久+16耐久）与17个合同原生字段，另37项候选个人档案/成长/人格和80项Gameplay徽章、20项人格标签候选；每类标真正来源等级和可写权限。新增SRC-0072..0082和R04-A图证审计（无已认证原版PC22菜单）。下一轮R04-B完整倾向与场上行为，由用户再触发；不开发Agent、不修改游戏。

## R04-B（2026-10-21）—球员行为倾向、PlayTypes和教练/比赛联动的研究成果

**状态`R04_B_RESEARCH_PUBLISHED_WITH_BEHAVIOR_GAPS / TASK_CLOSED`**；下一轮`R04_C_PLAYER_MOTIVATIONS_PERSONALITY_RESEARCH`，未启动。用户已明确：本GPT专注R系列研究及GitHub交付，独立完整性审核由其它模型负责，不再主动设置研究后的审核门槛。

**本轮最重要的实际源核对**：
1. 直接查`config/state_io_native/player.json`：**48已命名TENDENCY_OFFSETS**；查`src/gm_state_io/registry.py`：`PLAYER[0x458..0x4BA]`总计**99 byte，51 UNKNOWN_RAW_BYTE只读**，名录给48项technical writable但并不授权直接改球员倾向。
2. 同年`2kAuction NBA2K22 v91 Sep 10 2021`归档人物数据显示**Shot/背身35、Drive/Pass/ISO43、Defense7、Other区域14，共99个具名标签**。**两个99彼此独立**，不根据数量强配offset；[研究机读目录](catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)同时列99原生槽（48命名、51 UNKNOWN）与99外部导出标签（所有原生offset仍为null），外加0..15全部PlayTypes和Initiator的精确bit布局。
3. 2021 2K22社区对`Shot/Touches/Play Discipline`在**快Sim与3D**的作用产生互相矛盾的一手观察：一些球员认为Shot更偏模拟、具体SpotUp/OffScreen等影响3D；另有人降低Shot/Touches后观察到出手更分散，也有人保持“两后卫全拿战术”。记录来源与冲突条件，**没有认证万能数值/概率公式**。
4. 游戏行动对象分隔：`team Playbook 68CRC`、`12战术类别`、`player 4 PlayTypes`、`Initiator(0x16A bit2)`、`Touch/Shot/Discipline`、`Coach POE/RunPlays/ACE`相互关联但不能替代。第三方归档“Three-point screens”并非已认证本机`3 PT=15`逐字UI标签。
5. 按V3交付的角色原料：Player可提出/反价/拒绝改变打法，Coach可主张体系及拒绝，GM可提出资产和人员/训练支持，Media仅报公开比赛事实。**这些是未来角色行为，不是原生可执行Agent命令或当前人物同意**；球员倾向技术Registry可写仍需逐项权限验证和真人玩家批准。
6. [K03/K12 §9–16](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)已正式发布；[SOURCES](SOURCES.md)新增`SRC-0083..0090`，含同版档案、同年代编辑作者、OS正反实验与跨版本争论；[VIS索引](visuals/EXTERNAL_VISUALS.md)记录**新PC22原版Edit Player截图0张**，严格不冒充外站HTML为原版游戏UI。

**本轮精确遗留**：99个外部标签怎样对应51未命名raw/游戏其它字段、PC22原生全页签与合法值、3D vs FastSim引擎分别使用何种倾向与指令、PlayType/Initiator对本队Book实际调用概率、当前存档球员真实性和角色独立同意，都仍`UNKNOWN`。允许未来独立授权的DEV28对原生资料增量补证，**不因缺截图无限重复网页检索，也不启动DEV28或Codex**。

**R04-C唯一后续任务**：重点Loyalty/Financial Security/Play for Win、全部人格徽章的真实源级语义、士气/球队角色/承诺与职业谈判、金钱/冠军/个人荣誉冲突及玩家可见设置和球员外部目标的分离；继续更新K03/K12、人格字段/双语义目录、SOURCES、VIS、PROGRESS、README并提交GitHub回读。R04-D再完成完整Agent交互/权限图谱；**本轮不实现任何Agent或修改游戏数据**。

## R04-C（2026-10-21）— 球员职业诉求、人格徽章、士气与独立谈判研究交付

**状态：`R04_C_RESEARCH_PUBLISHED_WITH_NATIVE_MOTIVATION_GAPS / TASK_CLOSED`**。R04整体仍未结案，下一轮`R04_D_PLAYER_AGENT_DUAL_SEMANTICS_AND_INTERACTION_ATLAS`尚未启动。DEV29研究窗口只负责研究交付；独立审核由其他模型负责。

- [K03/K12指南 §§17–23](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)：NBA2K22同版导出`Loyalty/Playing for a Winner/Financial Security`独立0–100职业偏好、2015 MyGM试验分歧、2020 MyLeague人员去留不确定；**同版存在字段≠PC22 native offset已找到，也≠签约概率公式**。
- NBA2K20**开发者原文**确认Morale与Team Chemistry动态平衡以及Media Ringmaster大市场、Warm Weather Fan气候、Finance Savvy税务的**自由市场tie-breaker**设计；本轮积极复用其跨世代经营机制价值，仍保留PC22引擎实际权重/像素和当前值`UNKNOWN`。
- 20个人格候选新增遗漏的`Warm Weather Fan`，在[R04-C独立人格与动机目录](catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)共**21名候选**，其中3项有开发者明确的市场偏好语义；**21项并非已核实完整PC22原生人格Badge列表，也没有强加人格等于决定的刻板规则**。
- 2K22 **PS4 MyLEAGUE**一手玩家报告：即使给球员首发/队内第三得分位置、尝试调整忠诚/士气，他仍可能想走；2K22次世代MyNBA玩家报告竞价与球员出价回应不对称。记录为个案与待证异常，不把人物的拒绝解释成绝对“贪财/不忠”或一项控制必然失败。
- **重要排除**：2K22 ATD作者声称人格Badge能触发其200+场景，场景来自**社区自制MyNBA Event Generator**，不是NBA2K22自带原生Agent事件。`Finance Savvy`税务偏好≠`Financial Security`总薪资保障偏好；二者在机读目录单列。
- 同步[全字段与权限矩阵](catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)：把三项偏好研究候选补全为同版0–100证据、原生偏移NULL、不可直接获批改动、外部人物记忆另存SQL；[SOURCES](SOURCES.md)新增**SRC-0091..0105**，[VIS索引](visuals/EXTERNAL_VISUALS.md)记录原版PC22 Motivations/Morale/人格Badge菜单**合格新图证为0**，不意味着游戏没有这些功能。
- 外部角色的目标、承诺、谈判、反报价、拒绝、错误与关系历史为未来多模型自主选择的**可能行为原料**；它们不是原生游戏带有的NPC谈判按钮。游戏普通人物能力/潜力/徽章不可直接改；真实交易/签约/训练等变更仍需合法执行器、角色协商边界及**玩家实际批准**。

### 下一轮R04-D的最短恢复入口

1. 先从GitHub读本PROGRESS、[K03/K12 §§0–23](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、[R04专项任务书](../development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)，以及三份机读原料：[PLAYER_FIELD_AND_RIGHTS](catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)、[R04B_TENDENCY](catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json)、[R04C_MOTIVATIONS](catalogs/R04C_PLAYER_MOTIVATIONS_PERSONALITY_V1.json)；不重做R04-A/B/C。
2. 聚焦跨期玩家身份、数据可见权限/时间戳、Game Native vs External Role memory、原生偏好复用与双重作用风险、合同/交易/训练合法控制、人物⇄GM⇄Coach⇄Media冲突和拒绝；生成`docs/game_mechanics/catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md`完整具体用例，并在主字段矩阵中统一来源与权利，**不能把研究记录当可执行API**。
3. 检查R04任务书8类资料是否都有来源或清晰`UNKNOWN`；只做DEV29研究成果交付，不做独立审核。R04-D之后按用户确认/后续调用转R05市场财务研究。
4. 网页与GitHub文档研究、更新SOURCES/VIS/PROGRESS/README并回读。**不启动DEV28/Codex/Agent，不修改游戏存档/球员能力**。

## R04-D（2026-10-21）—全字段双语义、四角色互动图谱与R04正式研究结案

**状态`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`；R04-A/B/C/D均已完成网页研究交付。** DEV29只研究、整理和写入知识文件；按照用户指定，**不自行执行独立审核**，不为进入下一轮自行设置审核表单和准入审查。**下一主题R05尚未启动**。

1. 发布[K03/K12最终§§24–29](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)：四角色观察/提议/否决范围、游戏原生与外部人格双语义、`OBSERVED→ROLE_INTENT→NEGOTIATED→PENDING_HUMAN→EXECUTED_READBACK→FUTURE_GAME_RESULT`真实性层级、历史轮回选秀信息边界和R05研究入口。
2. 新建[PLAYER_AGENT_INTERACTION_ATLAS.md](catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)：**8个详细自选分支用例**：巨星有条件加盟、主动申请交易、球权与首发争议、内线球员转型、伤病/强度拒绝、导师关系、薪资选项与续约、媒体推断/公开更正。每个用例记录源数据、四类角色可能独立意见、可拒绝方、候选后果、原生执行权限与谁有权知道。
3. 新建[PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json](catalogs/PLAYER_FIELD_DUAL_SEMANTIC_R04D_V1.json)：将原[109项字段/候选主目录](catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json)逐行以`field_key`关联成**109项双语义/证据/身份/权限/覆写风险侧表**，没有动原Profile或游戏数据；另把R04-B 99原生槽/99网页名录、R04-C 3职业动机/21人格标签、R03训练健康、R02教练战术以引用方式串联。**109不是NBA2K22所有球员字段的全集**。
4. 研究工程边界：本项目[交易执行器](../37_APPROVED_TRADE_EXECUTOR.md)有批准、身份检查、计划与读回；[签约执行器](../38_APPROVED_SIGNING_EXECUTION.md)当前`approved_signing_v1_unvalidated`，**不因为两个虚拟角色谈妥就认为签约已被游戏写入**。旧[休赛期竞价方案](../development_tasks/DEV_20261017_04_OFFSEASON_FREE_AGENCY_V1.md)采用固定效用评分，不天然满足V3的独立人物拒绝能力，留R05和未来工程重新考虑。
5. 浏览核查模式差异：2K20**MyGM-only** Action Points/Chit Chat/Coach Trust不能直接当PC22离线MyLEAGUE原生Agent；2K20 **MyLEAGUE-Level** Morale/Personality可作为跨系列机制；2K22次世代MyNBA Conditional Coaching可参考但PC22原生未证；真实NBA2021 Player Option/QO是制度背景不等于游戏已有执行器。增补**SRC-0106..0113**及[VIS](visuals/EXTERNAL_VISUALS.md)有界文字/视觉索引，新增PC22原始互动界面认证**0张**，不伪称原生功能缺失。
6. **依然未知且留待独立授权下增量取证**：51个未命名原生Tendency byte、外部网页99倾向label精确映射、三动机和21个人格候选PC原生位置/实际动态值、玩家Morale/当前伤病/真实导师进度、合同签约执行实机验收、历史Box跨季保留/部分PlayerID稳定性。不强迫资料空白变成数值，不把GM遮蔽Potential=1当真实潜力。
7. 任何外部Player/GM/Coach/Media模型将来可以自主提出/反价/拒绝或错判，但**模型同意≠真人玩家授权**；禁止直接改普通球员Ability/Potential/Badge/Durability，也不使用原生仍有效的字段当外部人物记忆空间。角色状态仅未来外挂独立持久层的研究设想，本轮**没有开发任何Agent、运行游戏、抓取实时内存、启动DEV28/Codex或改存档**。

### R05的单一下一轮入口（等待用户下一次触发）

从GitHub先读本PROGRESS、[DEV29 V3](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)、[R04互动图谱](catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md)、[K03/K12](guides/K03_K12_PLAYER_PROFILE_AGENCY.md)、已存在的交易签约/财务/员工/球探/选秀合同。**R05研究K07/K08/K09**：Salary Cap/奢侈税/原生团队财务、Bird Rights与球员选项、RFA/QO、真正FA时序、交易合法性与未来选秀权、员工、球探/历史选秀及报价竞争，重点为各GM与球员提供**能接受/拒绝、冒预算风险、试错与对手博弈**的规则原料。严格区分2021现实NBA、NBA2K20–23跨系列与用户批准的本世界经营规则，**不直接生成或执行交易/签约**。每轮按原方法发布中文攻略、机读目录与SOURCES/VIS/PROGRESS/README并回读，不开展独立审核。


## R05-A（2026-10-21）— 财务、合同、Bird/RFA与自由市场机制研究交付

**状态**：`R05_A_RESEARCH_PUBLISHED_WITH_FINANCE_EXECUTION_GAPS / TASK_CLOSED`；R05整体分A/B/C/D继续，下一轮**R05-B交易/选秀权规则**，当时尚未启动（历史断点，现已完成）；最新见下方R05-B。R04正式保持`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`，用户已经批准结案，DEV29不返回做人设/独立审核。

**首批实质产物**：[K07/K08/K09经营中文攻略§§0–7](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05-A 17项原生合同字段 + 10项财务观测字段/候选 + 21类市场操作的机读研究目录](catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json)。[SOURCES](SOURCES.md)新增`SRC-0114..0128`共15来源、[VIS](visuals/EXTERNAL_VISUALS.md)新增原版薪资/合同菜单的有界取证索引（**没有新合格PC22原始菜单画面**），[README](README.md)同步入口。

### R05-A原生事实与机制发现

1. 现实NBA**2021–22**官方Salary Cap **$112.414m**、Tax **$136.606m**、非税/纳税/空间中产**9.536/5.890/4.910m**，apron **143.002m**只来自二手历史表（非此官方新闻原文）。现实2022–23又变成Cap **123.655m**、Tax **150.267m**。**这是现实年份参考，不是本项目2021历史开局后的游戏内动态联赛规则来源**。
2. 2022同版MyNBA玩家报告`Flat/Front/Back/Bird`的合同报价曲线玩法与逐年薪资变化。**Bird报价曲线不等于本项目PLAYER.contract_type的`CORE/HARDSHIP/TWO_WAY/EURO_STASH/LINEUP`Enum**。后者是Native合同身份类型而不是递增工资结构。
3. 本仓库`config/memory_field_profile.json`注册**17项PLAYER.contract**；6个薪资slot低31位共享高位，不可整块覆盖；`bird_years`、Option、No Trade、Extension、TwoWay/EuroStash等已命名，不表示每个真实市场限制都已采到；`PLAYER.current_team +0x60`与`contract_team +0xA8`也不能只改其一认定完成签约。
4. RFA/QO、Bird/Early Bird/Non-Bird、Cap Holds/Renounce Rights、工资帽例外与Tax/Apron是不同规则；系列社区报告RFA多年合同在Moratorium之后变一年QO，同版2022玩家也有报告，早期2021-07论坛**早于2K22发行**不得冒充2K22当场游戏证据。
5. **财务真正现状**：项目`total_salary/payroll/budget/cash`已有历史原生来源，但周期/符号/Staff Budget/净现金流未全证；`salary_cap_minus_payroll_proxy`及三年财务情景**不是legal signing capacity**。FinanceWorkbench的`signing_capacity=UNKNOWN`和六薪资slot年季映射为`SCENARIO`的声明必须保留。
6. 当前独立FA池此前只读P0历史批次**0行**，不代表没有真实自由球员；休赛期阶段、Option/QO、真实Cap Holds、签约CPU干扰、游戏跨期持久性、当前签约执行器仍**未实机验收**，`SIGNING_LAYOUT_VALIDATED=False`、`SIGNING_EXECUTION_ENABLED=False`。**存在签约源码不允许DEV29执行签约、也不准擅开闸门**。
7. NBA2K22次世代MySTAFF与旧MyGM Business丰富市场预算/经营概念可研究，但**PC22原版员工部门及设施UI不可凭旧版本文字直接确认**；员工/Scouting集中研究归R05-C。

### 后续唯一入口：R05-B

从GitHub先读本PROGRESS、[DEV29 V3](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)、[K07/K08/K09](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05-A目录](catalogs/R05A_FINANCE_CONTRACT_MARKET_RESEARCH_V1.json)、[已批准交易执行](../37_APPROVED_TRADE_EXECUTOR.md)、项目`config/gameplay_policy.json`、选秀权清单和Trade市场研究。重点研究**原生Trade Finder/Trade Block/多方交易、工资匹配/超帽交易例外、Roster/两向、Trade Deadline/选秀夜资产与交易限制、特殊条款和研究当时适用、但**现已撤销**的三年选秀权旧规则**，完整来源、合法可选菜单与未认证Native功能；不把现实2021 CBA和游戏原生/外挂双方同意即执行的世界规则混为一谈。

**DEV29分工**：仅研究游戏原材料、真实源/可选择项/作用/证据；不作人格或交易决策算法、不产生真实GM方案、不运行游戏/内存、不开发DEV28/Codex或Agent、不修改游戏。每一轮GitHub出版并回读，不由本研究窗口做独立审核。

## R05-B（2026-10-21）— 交易、工资匹配、选秀权和名单原生能力研究交付

**状态`R05_B_RESEARCH_PUBLISHED_WITH_TRADE_UI_AND_CBA_GAPS / TASK_CLOSED`。** R05-A/B已研究发布，R05-C员工/球探/选秀**尚未启动**，R05-D之后整合；R04已获用户正式结案，不返工/不开球员人格设计。**DEV29职责仅研究游戏资料、真实接口及可选菜单，不制定交易算法或GM策略**，独立审核由其他模型。

**已提交**：[K07/K08/K09 §§8–15](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、[R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json](catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json)，[SOURCES](SOURCES.md)新增**SRC-0129..0144**，含2017 CBA2021–22历史表、NBA官方真实交易截止日期、同版2K22设置清单、**2022-07 PC MyLEAGUE用户“确认交易但人物未实际转队”**、本世代2022日期限制异常、邻近代选秀保护和Swap的有界来源；[EXTERNAL_VISUALS](visuals/EXTERNAL_VISUALS.md)明确**新增PC22原版可读目标交易UI图证0张**。2022原版PC机制不存在或存在不可由缺截图直接断言。

1. **游戏设置研究**：Trade Logic、Financial Trade Rules、Recently Signed/Traded/Rookie Restriction、Trade Deadline、Stepien、Trade Override、CPU Offers/CPU-CPU及Trade Finder/Block/Propose Trade等**16项菜单/操作候选**，按同版社区与旧模式分等级，不声称当前存档数值已采或自动执行权限。
2. **CBA实际不同薪资匹配**：非纳税队低/中/高三档对应175%＋$100k、原工资＋$5m、125%＋$100k；纳税队125%＋$100k。此为**2017历史CBA现实规则参考**，不是2K22 PC原生核实公式，尤其不能用旧项目`docs/14...`的单一125%公式宣称所有合法性。TPE、Sign-and-Trade、硬帽限制仍需与游戏UI及真实数据分开。
3. **Native 5年 vs 本世界3年**：`config/draft_asset_profile.json`＋`src/draft_assets.py`证据支持32-byte资产记录、**5届×每届30队×2轮=300条未来选秀权**的读取一致性；但`config/gameplay_policy.json`只允许**接下来3届**交易，无保护、无交换。例如下一届游戏年2022，则2022–24可交易而2025–26**仅可读不能按本世界规则交易**。游戏年2022!=实际1984届历史新秀标签。
4. **名单与执行器**：本机注册15常规、2双向、13活动真实容量，常规人数`+0xCB1`、活动/双向人数`+0x1047`位域，球员当前队`+0x60`及合同队`+0xA8`，选秀权当前持有队`+0x00`。受限`ownership_transfer_v2`已被玩家接受CHI/DET成果，并有只读核对，但**不自动支持任意三队、双向、签换、释放/签约或完整薪资CBA校验**。
5. **权限边界**：本世界双方独立GM将来达成协议，不等于原生CPU会接受、不等于交易时刻已合法，也不等于**现实玩家本人批准写入**。`Trade Override`的游戏菜单覆盖与外挂的本地批准执行不同。**任何普通球员能力/潜力/徽章绝不因交易变更**，历史线批准特例另行处理。
6. **旧文档非权威**：`docs/14_TRADE_VALUATION_AND_ASSET_POOLS.md`提到固定10000点资产值/绝对非卖巨星/一刀切125%/更长未来签与保护交换，属于历史方案；研究当时权威为用户`PLAYER_RULES_20261017_V3`（**2026-10-21被V4覆盖**）及DEV29原料职责。R05-B没有改旧方案、实现规则/评分，也不为未来GM强制执行任何价值函数。

**R05-C唯一下一入口**：K09员工、球探、选秀与球队经营可操作参数。先GitHub读本PROGRESS和K07–09已发§§0–15、`config/memory_field_profile.json` STAFF字段、游戏Staff Pool/Coach配置、原生历史新秀池/选秀库和已有球探来源，再重点查NBA2K22 PC同代Staff Roles、Scouting/Prospect Grades/Draft Board/Mock Draft、1984–2020 Draft Class与原生Draft Rights、球队Budget和Staff Salary等**真实信息+合法设置选项+效果+平台来源分级**，按相同方式发布中文机制指南、研究目录、SRC/VIS/PROGRESS/README。**不做模型人格/真实GM选人和策略开发、不启动DEV28/Codex或修改游戏。**


## R05-C（2026-10-21）— Staff、Scouting、Draft Class与历史新秀研究发布

**正式状态**：`R05_C_RESEARCH_PUBLISHED_WITH_STAFF_SCOUT_DRAFT_UI_GAPS / TASK_CLOSED`。R05-A/B/C均完成当前研究发表，**R05-D经营知识整合尚未启动**。R04原状态继续保持用户批准结案`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`。本研究只提供游戏事实/参数/可用选项/效果证据，不进行人格或GM决策规则开发，独立审核由其他模型负责。

**本轮文件**：[K07/K08/K09 §§16–22中文攻略](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)；[R05-C STAFF/Scouting/Draft机读目录](catalogs/R05C_STAFF_SCOUT_DRAFT_MECHANICS_V1.json)；[SOURCES](SOURCES.md)新增**SRC-0145..0160**共16项原始来源登记；[EXTERNAL_VISUALS](visuals/EXTERNAL_VISUALS.md)新增跨世代界面视觉来源审计，**PC22原版员工/球探/选秀完整像素认证仍0张**；[README](README.md)同步入口。

1. 本机**真实Staff静态数据**：`config/memory_field_profile.json`注册13项STAFF字段：position 0..7八类（Head Coach/Assistant Coach/Head Scout/Trainer/GM/Governor/CFO/Assistant GM）、years_left、salary及8种F..A+能力级别（Offense/Defense/Potential/Contracts/Trading/Scouting/Training/Business）和两组0..7体系。项目`src/source_extensions.py::staff_details()`有`STAFF +0x18`职位所属球队反向关系确认，失败标`UNMAPPED_NOT_ASSUMED_FREE_AGENT`，**本地具STAFF读取而非通用人事合同执行器**。当前仓库含staff.json正式批次，不能据此虚构真实当期员工自由池。
2. NBA2K22官方**PS5/XSX MyNBA**新MySTAFF四部门/Coach细分专岗/Head Scout与4 Domestic＋2 Foreign Scouts/7医疗岗位，受**17名员工资格位置与Staff Budget**约束。其版本不是PC22本世代MyLEAGUE。2021-09同版玩家报告空缺与预算问题、招不同医疗/教练后主观反馈，不形成可量化因果。
3. 同版NBA2K22选秀攻略的`Scouting→Prospect Scouting`以及Generated/Historic/User-Created/Create-Edit Draft Class、Projected OVR、`D.E. Rank/2K/NBA.com`榜单是**可研究的原生信息类别**；`Scouted 40/100%`、Auto/Manual主要社区经验，真实侦察周期、Current PC22精准效果和每队可见范围尚UNKNOWN。**报道潜力等级≠游戏真Potential，公开GM Potential=1是脱敏，不是零潜力**。
4. 1984→2020→1984历史选秀轮回仅随**用户确认选秀已经完成**推进；游戏2022年持有签≠“1984年签”。全局Pool旧文有3320条原始槽，`raw_struct[0x70]&0xE0==0xE0`真实类型标志、身份去重/部分届次人员缺额；**历史新人目标60个临时槽位内存没有完成正式可靠注入校准**，差额游戏生成新人，不擅编能力潜力。
5. 两条严禁混用的旧资料：`docs/05_STAFF_AND_PLAYER_GROWTH.md`曾提“教练直接给球员加Ability”的已废止方案；`src/extract_live_draft_class.py`的旧固定指针区间内存聚类是**未经验证的试验工具**，不是当前已经可用的实时Draft Class源。已公开脱敏的GM球员池**不能被当成原始真实新秀注入源**，否则Potential=1会污染游戏。
6. 员工薪资/预算不等于球员工资帽可签额度；真实`staff_budget`口径、解聘/签约员工的PC22菜单和值域、球探误差系数、Draft Lottery与Draft Result原生读取，以及新人合同/海外Stash的实际逻辑仍**未认证**。**不存在因研究完成就获准运行游戏聘任/引入新秀的许可**。

**R05-D下一入口**：先从GitHub读本PROGRESS、DEV29 V3、[K07/K08/K09 §§0–22](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)、R05-A/B/C三份机读目录、SRC-0114..0160和VIS，整理**所有经营领域的原生观察/合法游戏动作/可能效应/证据/缺口交叉表与完整经营知识索引**；纠正重复或来源不明的菜单字段，保持R04/Potential边界。**R05-D只研究整合，不设计球队哲学人格、自由市场算法、选秀评分或启动DEV28/Codex/Agent/游戏写入，也不代替外部模型执行独立审核**。


## R05-D（2026-10-21）— K07/K08/K09经营游戏原料整合交付及选秀权规则V4

**正式研究状态**：`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`，A/B/C/D都已发布；**这是研究交付结案、不是外部审核通过或全部PC22原生执行闭环**。用户规定审核由其它模型执行，本窗口只研究。R04`R04_RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`仍原样维持用户批准状态。

1. **已提交**：[K07–09完整攻略§§23–29](guides/K07_K08_K09_FRANCHISE_OPERATIONS.md)与[R05-D原生经营全集目录](catalogs/R05D_FRANCHISE_CAPABILITIES_ATLAS_V1.json)，从R05-A/B/C继承**17项合同字段＋10项财务观察/候选＋14项名单选秀资产Native结构＋13项STAFF字段=54条异质数据原料**（**并非54条当前游戏实测值**）；**21市场/合同概念＋16交易候选＋10球探类别＋10选秀选项＋6员工职位变更候选=63种操作研究项**（不是63个已验证按钮），另外12个机制联动与12个PC22未知/未验缺口。SOURCES新增SRC-0161..0162，VIS增加R05-D跨模式图证审计（合格新增PC22菜单图证0）。
2. **最新玩家新政策已直接落入权威配置**：`config/gameplay_policy.json`从`PLAYER_RULES_20261017_V3`升级到`PLAYER_RULES_20261021_V4`，`draft_pick_trades.maximum_future_drafts=null`，彻底删除**世界人为未来三届上限**；不替代成新五届硬上限。**原生目前可读未来五届是技术覆盖事实，不是政策年限**；保持Year/Round/Original Owner/Current Owner、无新增保护或Swap及玩家逐笔审批。文字权威[文档26](../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)已更新，[R05-B机读目录](catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json)同步撤销旧政策；研究形成**新旧政策差异明确可追溯**。
3. **工程差距仍真实存在**：`src/draft_assets.py::trade_window`和`src/gm_core/calculations.py::draft_pick_window`仍含`+3`，`src/gm_core/trades.py`返回`DRAFT_PICK_OUTSIDE_THREE_YEAR_WINDOW`，`src/approved_trade_executor.py`调用旧窗口。若现在请求第4/5届，即使有真实Asset，**执行器仍会拒绝**。此项归独立用户授权的Codex**代码与测试同步工作**；DEV29没有改执行脚本，没有承诺已可执行第4/5届。
4. **来源分层**：2K19游戏开发者历史资料已说明该游戏扩展至五年（SRC-0161），现实NBA2022交易七年上限与Stepien（SRC-0162，和旧SRC-0137为同源交叉引用）；它们均不自动升级为PC22本局的UI枚举或世界年限。球队薪资帽、员工Staff Budget、合同Option、市场报价、Draft结果、球探错误概率继续保留当前PC22真实性/时间/持久化UNKNOWN。
5. **工作分工**：经营研究仅提出哪些实际/候选游戏资料、哪些可选操作、已知引擎语义和缺口；没有决定GM怎样交易、员工怎样获聘、球员怎样谈判或历史巨星怎样成长。不运行游戏、不编写人格、不开放签约/历史新秀注入/员工执行器，不修改任何现实NBA2K存档和人物能力。
6. **R06单一下一入口**：K05/ K10/ K11 游戏规则、3D与Sim设置、赛季和各阶段推进/保存、历史纪元/奖项/媒体事件及事实公开性。按DEV29 V3从旧研究资料和NBA2K20–23真实来源获得游戏中可观察数据/可选设置/原生效果/证据并发布新的中文攻略＋机读目录＋SOURCES/VIS/PROGRESS/README，仍禁止设计媒体Agent或自动推动游戏时间。R06此刻**NOT_STARTED**。


## R06-A（2026-10-21）— 游戏全局设置、3D比赛与日历模拟机制研究正式交付

**本批状态**：`R06_A_RESEARCH_PUBLISHED_WITH_PC22_RUNTIME_VERIFICATION_GAPS / TASK_CLOSED`；**R06系列未结案**，下一轮`R06_B_HISTORY_ERA_AWARDS_MEDIA_MECHANICS_RESEARCH`尚未启动。R05-A/B/C/D根据用户最终审核**已接受研究结案**，永久保持`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`，不因4/5届选秀权代码未同步返工。该代码修改归独立Codex维护任务，本轮未启动。R04状态亦不变。

**新交付**：[K05/K10/K11中文研究指南§§0–6](guides/K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md)、[R06-A注册/菜单研究目录](catalogs/R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json)；新增[SRC-0163..0173](SOURCES.md)共11条PC22/PS4/PS5及旧版来源；[VIS](visuals/EXTERNAL_VISUALS.md)增加来源/平台审计（新增合格PC22原版逐像素图证0）。README同步入口，直接GitHub回读完成后收尾。

1. **本世代同版新证据明确了两个比赛引擎**：2021-11 PC22 MyLEAGUE玩家**30队全控但观看3D CPUvsCPU每场、不是日历Sim**；2022-01 PC22默认阵容玩家明确Setup Quarter与Simulated Quarter可不同，**Simulation**又细分Player Fatigue、Team Pace/Fastbreak、Possession Results、Shot Types、Shot Percentages、Stat Distribution。和2021-09 PS4 MyLeague本世代互证，但作者自定义数值与改变Player Tendencies不代表PC原版默认/引擎数学公式。
2. 机读目录把**项目静态Registry中的86个记录候选**逐条保存：`settings.json`有49项，`world.json`有37项；**可能跨目录共享Native Slot/Offset，不是86个互不重叠UI按钮或当前已读游戏值**。`src/gm_state_io/registry.py`确实会自动纳入WORLD_SETTING，但软件可登记、旧静态RVA代码、可计划写入，不等于当前PC22 UI+原值+写后读回+存盘验收。另`court.json`有较窄4项Gameplay受限项目定义。
3. 游戏菜单研究**118项候选**：Setup13、Calendar Simulation32、3D Gameplay73，来自明确来源的项目分类研究；都保留`current_value=null`及对应具体版本标签，**不是本游戏全套原版字段已逐帧认证**。尤其`Simulation Shot Three`≠3D`3PT Shot Success`≠Player个人`Take 3PT Tendency`。
4. 玩家/社区已报的**Normalize伪数据风险**：2022-06 2K22 MyLeague用户场内126:116后日历显示304:287及球员统计变化，有用户认为与Norm开关有关；2021旧MyLeague有Stats变而Minutes未变的报告，不可当目标版普适公式。当前`settings.json`的`simulation.normalize_stats`**不能代表“分钟”与“统计”两个独立开关都已找到**。同一GameID要区分场内比分、赛后Box、日历结果与季节聚合。
5. **Gameplay USER/CPU与模式**：一队被指定User-controlled仅是经营所属，比赛控制器、USER/CPU Gameplay Slider消费、CPU-vs-CPU/SimCast和ACE应分别记状态；2017旧版本论坛观点不认证PC22行为。用户HoF实际观察保留，**不在R06-A建议改变其当前游戏设置**，不关闭ACE，不自动改球员能力/潜力/徽章。
6. **后续顺序**：R06-B研究历史纪元/规则提案/奖项/纪录/媒体的原生可见事实；R06-C研究赛季阶段、保存/重启、真实Game Date和历史单场数据保留；R06-D跨领域整合。所有研究只交原料、不开发媒体人格/运行流程、不调用PC游戏、不修改游戏存档；每次更新GitHub资料并回读。

