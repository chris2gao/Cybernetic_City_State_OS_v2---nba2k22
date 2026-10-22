# Codex 数据采集/开发/执行基线共用的当前状态与交接索引

## 2026-10-22 最新架构纠错：允许从根本上重构数据平台

玩家明确：旧双库、月度统计表、采集容器及相关API可以且应该根据长期平行篮球世界目标**整体重构**，不是不可更改的默认架构。旧工程是迁移的真实事实和安全机制来源，不能变成新模型的物理约束。新权威文档：[平行篮球世界数据架构V2](development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)。该设计区分world/save/generation/season/game/player incarnation/draft template身份，原生字节/解码事实/事件/状态快照/赛季累计/派生统计/AI决策与受控执行；允许改变SQLite库数量与Schema。候选逻辑与物理设计可以马上进行，正式DDL与数据迁移需Codex验收并单独批准；不直接变更当前生产库和游戏。下一段旧“复用双库”字样应理解为保留**已认证能力与事实**，并非禁止架构重构。

## 2026-10-22 最新项目级共识：NBA2K22权威引擎与SQLite平行世界

**优先阅读**：[项目宗旨](PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)、[平行篮球世界数据架构V1](development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V1.md)与[原生Native I/O蓝图V2](development/NATIVE_GAME_DATA_SYSTEM_RECONSTRUCTION_AND_IO_BLUEPRINT_V2.md)。游戏是比赛与自然成长的权威；外挂基于已认证Native对象建立双SQLite可追溯事实镜像、真实跨赛季历史账本、多角色AI与经玩家批准的有限执行反馈。保留六阶段采集→分析→教练→球员→GM→执行的目标顺序，不把基础设施当角色人格。

**工程状态**：DEV29 R01–R07正式研究结案。FINAL-CODEX审计`codex/final-code-audit-20261021@d1038811ecee3a6b35a5d9c4787c67bf65456438`已完成且经网页GPT独立审核接收（1项文档排版备注）；40族状态16历史部分/7已实现未发布/3未合并候选/1签约阻断/13参考或未知，20项缺口继续保留。比赛历史旧分支不应直接合并。AG-NATIVE-01至01D研究位于`dev/native-io-exploration@21d62ec9e04b86a1f737c1500ea2f41c34583215`，新增SEASON逐场/StatBank、Slot24生涯统计与对决矩阵样本；Curry16场与赛季记录18项一致的fixture值得Codex复核，**不意味着238场/全部游戏页/生产SQLite已独立验收**。

**下一阶段方法**：Gemini Flash只读快速逆向与实验性Decoder/候选Schema，Codex做复杂问题和独立实机验证；候选数据建模与验证并行。验收、审批后Codex沿现有DEV14多存档代际、full_verified_v1双库暂存发布、Potential脱敏、M0查询和执行审批集成，不另造生产事实库。旧Oct18生产批无GM_SANITIZED，继续禁止作为GM正式生产入口。完整GM/Coach/Player的“食材”仍有动态比赛、角色状态、UI列/历史留存/原生权限缺口；人格系统按原项目边界另立任务。以上是最新状态；以下旧日期段落仅作历史。

## 2026-10-21 R01–R07研究反推：以PC22游戏页面/完整对象为界的Native I/O V2蓝图

[正式规划V2](development/NATIVE_GAME_DATA_SYSTEM_RECONSTRUCTION_AND_IO_BLUEPRINT_V2.md)已综合R系列40族/694异质项、R04全球员信息、R05经营、R06世界、DEV24/28及已证`roster_directory`原生数组，确立：真实游戏UI完整页/Tab/表格及合法控件→原生对象/数据产生与查询机制→全量可证镜像/页面等价Query→经批准执行/回读。不能把游戏表格当SQL数据库已证；必须独立验证原生Getter、内存数组、文件存储与是否存在游戏内部数据库。局部PLAYER 55能力+17合同与倾向99byte/Badge研究≠完整PLAYER对象API，早期文档0xDF0与现采0x4F0冲突需保留证据版本。**这份V2只作后续工程的研发蓝图/任务边界，不扩大当前未结案FINAL-CODEX；AG/DEV28实机及任何写入仍需按包授权。**此前按角色筛选字段V1已撤回。

## 2026-10-21 玩家撤回上一版按用途列字段的原生能力开发规划（最新方法纠错）

此前[原生能力扩展路线V1](development/NATIVE_IO_CAPABILITY_EXPANSION_AND_FUTURE_ROLE_FOUNDATION_V1.md)已标记`RETRACTED_AS_DEVELOPMENT_PLAN`，**不得用于派发字段补丁式采集任务**。玩家要求以NBA2K22真实游戏UI所有页面/子页/统计表的**完整数据对象与表关系**为发现合同，研究引擎数据生成、原生结构/持久化、索引关联、渲染/汇总、查询能力和全部读写选项。尤其完整PLAYER对象必须包括资料、能力、倾向、徽章、合同、统计、伤病、发展和全部实际可见/关联项目，不能抽取几项偏好代表全体。目前玩家池原生1264字节`raw_struct`与其它独立统计数组已采，但`memory_field_profile`对PLAYER仅55能力+17合同，`player_details()`只是局部投影，不能宣称已有完整玩家对象API。**原生表状记录不等于已发现SQL数据库**：需技术确认底层为可访问DB/内部查询函数/内存数组/关联对象/渲染聚合中的哪种，不能凭UI形态假设支持SQL。FINAL-CODEX现有owner仍为Codex；不自动扩大审计，不从纠错直接启动新研究或真实游戏操作。

## 2026-10-21 玩家明确后续战略：原生I/O能力扩展优先于角色人格开发

**已登记规划（不等于DEV28实施授权）**：[原生游戏信息/控制能力最大化与未来角色建模底座V1](development/NATIVE_IO_CAPABILITY_EXPANSION_AND_FUTURE_ROLE_FOUNDATION_V1.md)。先由原Codex完成已有FINAL-CODEX覆盖对账；以后基于已知资料让Antigravity Gemini Flash按独立有界任务深挖游戏PC22内存、完整球员画像、比赛记录、Playbook/Coach、财务世界信息、原生合法修改表面并提交带真实样本/fixture/测试的独立模块；Codex以低成本复核并承担统一Registry/SQLite查询/执行安全/生产整合。最大化真实可用素材后，才**独立立项**GM/Coach/Player人格模拟。胜利/金钱/忠诚倾向与非竞技徽章既可提供角色原生信息，又可能影响游戏AI/合同/士气，不能未经验证当空闲储存位或自动授权修改；真实写入仍待逐案批准。遵循[跨模型所有权规范](development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md)，不以换模型接管未完主任务。

## 2026-10-21 跨模型任务所有权规范及FINAL-CODEX中断恢复（最新协作规则）

**项目正式规范**：[跨模型任务所有权、交付/核验与Antigravity子代理约束](development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md)。一个工程主任务由一个owner负责；额度/上下文中断仍由原owner在原工作现场恢复。其它模型只能接独立、边界清楚且可由消费者用SHA、schema、少量测试/实机只读对照验证的辅助工作；辅助`TASK_CLOSED`不等于主任务/生产验收。Gemini Flash子代理型号与主模型具体版本无法保证时默认禁用，不得用可能更弱的未识别subagent承担证据判断。

**FINAL-CODEX玩家已正式授权只读工程覆盖审计，因Codex的5小时额度耗尽中断，尚未正式交付或结案。** 据玩家提供的本地Codex和Antigravity执行回执，Codex工作区`codex/final-code-audit-20261021`已经生成40族JSON矩阵和中间证据；AG-01完成只读现场清点，AG-01B执行SHA备份与三份`DRAFT_PENDING_CODEX_REVIEW`初稿，**仅是辅助交付**，不能代替Codex最终审核。工作区与`_exports`不可清理。原主任务恢复由Codex负责；AG-02/AG-03尚未因这两次辅助交付自动启动。DEV28及真实游戏修改仍待另外批准。以下早期“FINAL-CODEX仍未授权启动”是历史段落，已被本节覆盖。

## 2026-10-21 DEV29研究阶段正式结案（新窗口独立复验）

**权威最新结论**：[R07两项定向修复独立复验与DEV29研究结案](development_reviews/DEV29_R07_TARGETED_INDEPENDENT_RECHECK_AND_DEV29_CLOSURE_20261021.md)已通过：`R07_RESEARCH_CLOSED_AFTER_INDEPENDENT_RECHECK` / `DEV29_RESEARCH_CLOSED_WITH_PC22_NATIVE_IO_GAPS`。694/694索引、682/682原JSON匹配、40族/86锚点、R06 20缺口均核对；人工主题别名和八项模型查询状态已修复，无任何实机运行/写入/Save成熟度升级。**下方“待独立复验”记录为历史交接状态，现已被本段覆盖。**

**仍未授权启动** FINAL-CODEX（有界静态只读I/O对账）、DEV28代码实施、选秀权V4旧+3改造、Coach/Player/Media人格开发及游戏写入。工程状态不因研究结案自动升级。

> [**2026-10-21 长窗口交接及后续开发规划快照**](development_snapshots/DEV_PLANNING_WINDOW_HANDOFF_20261021_V1.md)：网页GPT开发规划窗口上下文上限前已创建完整快照。研究最新可复核状态是R07两项机读修复已提交**待独立复验**，而不是DEV29正式结案；后续FINAL-CODEX仅待用户另批只读覆盖对账，DEV28实施也待另批；V4 Pick取消固定3届上限但旧代码+3仍待维护。

## 2026-10-21 R07独立审核后A/B机读修正已提交待复验

[独立审核报告](development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)接受R07主体研究，要求两项定向修正；[修复回执](development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)已登记：①R01指南主题`R07.0007/K02.SHOT_ZONES`、`R07.0010/K02.PER36`标为人工检索别名并锚定原章节，不冒称原机器主键；②F21/F22/F23/F26/F27/F32/F39/F40将`model_query_api_status`改为查询事实口径，把原交易/签约/Staff执行、V4+3差距、日期/存档真实性、审批和历史重力约束保存在独立Warning/Prerequisite/世界规则字段。694条7卷、40组86锚点、20原缺口均保留。**状态`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`：尚未正式研究结案或获得FINAL-CODEX授权。** 生产能力和普通球员能力禁改规则不受研究文档修正影响。



## 2026-10-21 R07独立审核：研究交付已验证，仍有两项机读字段修正

[DEV29 R07独立审核报告](development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)。R07七卷694项目/682源JSON记录直接匹配/40功能族/86功能锚点/20继承缺口通过静态检查；研究主旨和七维成熟度分离正确。**当前状态`R07_REVIEW_TARGETED_CATALOG_REPAIR_REQUIRED`，不是全面结案或Codex自动开发授权**。两个定向问题：PART_01两个R01人工主题ID需标`GENERATED_GUIDE_TOPIC_ALIAS`及具体章节；矩阵F21/F22/F23/F26/F27/F32/F39/F40的`model_query_api_status`混入写入/审批信息，应恢复为查询状态并另留执行警示。此类修复不意味着PC22真实运行时读回、逐场Box或存盘能力有进展。用户随后可另行触发FINAL-CODEX对账；禁止顺手开发人格/DEV28/游戏写入。


## 2026-10-21 R07研究成熟度总目录已发布，等待独立验收

研究入口：[R07七层证据成熟度中文指南](game_mechanics/guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)、[40功能族/10历史生产来源/20缺口JSON](game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)、[694条7分卷总入口](game_mechanics/catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)与[后续DEV28只读缺口交接](game_mechanics/R07_TO_DEV28_EVIDENCE_HANDOFF.md)。状态`R07_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`，**没有触发新的采集、查询实测、执行或游戏Save**。原R06研究已正式获独立审核通过。40/694等是异质研究对象，不是已可用的Native字段/动作数量；7个成熟度层不能压成一个done。现有生产能力仍以本文件具体证据、最新实际manifest以及37/38/40手册各自已验证范围为准；R07不扩展任何写入白名单，不能通过新目录自动启动DEV28或FINAL-CODEX。旧正文提到“3届Pick”的历史记录被2026-10-21 V4取消规则覆盖；现存旧+3执行守卫仍是未修工程差距。



## 2026-10-21 R06独立审核通过：游戏机制研究下一轮R07

权威验收：[DEV29 R06研究独立结案报告](development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)。R06-A/B/C/D网页研究结案接受，`R06_RESEARCH_CLOSED_WITH_PC22_NATIVE_RUNTIME_AND_PERSISTENCE_GAPS`；R06-D 26机制关系/20待证缺口/79处引用已经与8份原始JSON逐条比对；R06-B10奖项来源标为`sources=[]`且Eras争议字段改UNKNOWN，定向修复通过但游戏UI仍无实证。R06-C38项含7无直接来源保持待证。**当前下一研究轮R07**只整理所有R系列游戏可观测事实、可设置动作、源证和成熟度；不是开发球员/教练/媒体人格，也非启动DEV28的写入许可。选秀权世界V4旧`+3`代码继续是需要用户另行批准的独立Codex修复任务。

## 2026-10-21 R05独立审查：研究通过，选秀权V4代码兼容性尚未更新

**权威报告**：[DEV29 R05独立审核及四处Pick窗口工程缺口](development_reviews/DEV29_R05_INDEPENDENT_REVIEW_20261021.md)。DEV29 R05-A/B/C/D的经营机制/游戏原料研究**接受结案**，状态`R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS`；R06下一轮。**当前世界规则`PLAYER_RULES_20261021_V4`不再限制未来三届Pick交易，也没有固定五届规则上限**；本机只读覆盖连续五届共300条，但`src/draft_assets.py::trade_window`及`capture_assets`的`tradeable_draft_years`、`src/gm_core/calculations.py::draft_pick_window`、`src/gm_core/trades.py`、`src/approved_trade_executor.py`仍拒绝第4/5届。**这不是已经修好的执行能力**；由用户将来另批Codex最小同步任务，测试合法性/批准/存档与读回，不把+3换+5新世界规则。不能因R05研究结案或政策更新就执行第4/5届资产交易。其余签约、Staff/Scouting/Draft原生接口缺口继续待认证，DEV29不建人格/执行器。


> [**权威研发目标与现行状态区别**](PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：当前研发意图是六阶段各独立模型参与；Coach/Player人格尚未开发。DEV29做游戏原料、DEV28做可读/可执行工具，独立人格另立项。下方旧PR #12待合并记录仅为历史，PR已合并；R05为下一知识研究轮。

## 2026-10-20 PR#12已合并：DEV29 V2网页GPT研究资料库优先

- GitHub实时确认PR #12 `merged=true,state=closed`（Head原`ded900c`）；先前Draft和dirty/merge conflict说明仅为历史状态，**不再阻断DEV29研究**。GM V3/V4正式启用仍按原批准。
- 玩家决定先让**新的网页版GPT研究窗口**做NBA2K20–23（包括次世代）终极联盟机制和攻略、图文截图证据的多轮研究，保存在[docs/game_mechanics](game_mechanics/README.md)。正式指引：[DEV29 V2](development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)，[新窗口启动提示词](game_mechanics/NEW_GPT_WINDOW_BOOTSTRAP.md)，[PROGRESS](game_mechanics/PROGRESS.md)。
- 每轮网页研究后GitHub发布真实机制攻略、来源/截图和GM数据/可选项需要；**Codex不主导检索攻略**，研究阶段结束后仅FINAL-CODEX将知识目录与已有Registry/M0/DEV14/SQLite逐项核对，再启动DEV28有界输入/输出透明化开发。保留玩家批准、真实PC原生来源验证、未知项与第三方截图权利界限。

## 当前交付：PR #12已整合最新main基线，待玩家合并决定

初次同步main c68cb81与PR分支2f659138，共同祖先04b194a；先保存文档冲突解决为merge 1899d1a。玩家补充后再次fetch，最终主线为5c032a0bdb8885cc34d1421952527457251522a9，继续合入原PR分支。实际content冲突仍只涉及AGENTS.md与docs/33；第二次仅AGENTS的规范标题相邻处冲突，保留当前交接与最新社区优先/跨世代参考条款。本文件保留双方历史并将本次当前状态置顶。

主线[机制研究先行规范](GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md)、[DEV28完整规划](development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)、[十二类战术与双类型研究](development_research/NBA2K22_PLAYBOOK_12_CATEGORY_AND_NATIVE_TYPE_MAPPING_V1.md)、[共享池命名规则](GM_SHARED_PLAY_POOL_V1.md)和[DEV24来源要求](development_tasks/DEV_20261020_24_BPTI_ANTIGRAVITY_GAME_DATA_SOURCE_REQUIREMENTS_V1.md)完整保留；按最新main：社区/攻略/官方手册优先理解机制，次世代资料作为重要参考，具体执行接口再核对PC原生实现。本轮仅Git/文档整理，不展开机制研究或后续开发。F1–F4、M3/BPTI接口及演化隔离代码与已审查2f659138一致；原36执行基线、M3/BPTI手册和历史验收仍保留。

直接验证只核对冲突标记、源码/双方文件保留、入口链接和Git历史/远端合并状态，具体命令结果见[包C验收及交接](development_reviews/BPTI_PACKAGE_C_IMPLEMENTATION_AND_ACCEPTANCE.md)。没有新增或重跑合成测试/全项目回归、生产采集、现金调查、游戏实验或写入；V3有效/V4未启用、真实30队UNASSESSED。PR #12保持Draft，不自动合并main。状态BPTI_PACKAGE_C_MERGE_CONFLICT_RESOLVED_TASK_CLOSED；DEV28由玩家下一独立任务触发。


## PR #12 最终局部修复 F1–F4（玩家2026-10-20批准）

当前演化版本/来源与蓝图不一致会BLOCK_FINAL，final/strategy均核对；从旧策略基底继承的BPTI当前字段先清除，历史表不改。前态要求同队/career且save_id/save_instance_id/generation_id齐全相同，已记载history_branch_context连续；批次/赛季可变化，缺失或不同实例/代次/分支HOLD，无新增跨实例认证机制。

有效篮球蓝图与原生可执行状态分开：无支持动作时native_action_status=HOLD，MARKET继续由M3内部比较/GAP_REMAINS/财务/双边同版谈判决定。未支持的内部动作BLOCKED，只有INTERNAL+VIABLE_CANDIDATE可进入执行组合。此修复覆盖下方原“蓝图HOLD阻断市场”的旧行为。

四项直接合成检查均有通过证据：F1/F2/F4首次通过，F3改正原谈判状态断言后单项通过（17.169s）。首次入口意外额外收集了原C-C1～C-C5，9项/42.500s中8通过、F3断言失败；已改为模块引用，随后只复验F3，未运行完整项目回归。细节见[包C实施及验收](development_reviews/BPTI_PACKAGE_C_IMPLEMENTATION_AND_ACCEPTANCE.md)。

修复提交仍在原PR #12，不自动合并；V3有效、V4未启用、真实30队UNASSESSED，无真实数据/游戏操作。下一阶段权威为main上的[DEV28](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)：控制目录、真实Coach/Book/68槽生命周期、DEV24动态事实和完整执行读回另行授权，不在本轮实现。


源码交付：[Draft PR #12](https://github.com/chris2gao/nba2k22-gm-engine/pull/12)，实现da8a645；工作包C独立分支已推送，未合并main。实际验收与边界见紧随其后的包C记录。


## 2026-10-20 工作包C：B4/B5/B6完成，独立Draft交付

玩家已批准PR #11合并；main合并点04b194ab8b4644161242391e964051d3d9f9520a。随后独立触发包C，从该main建立codex/bpti-package-c，保留原season-match-history工作区。本包实现[B4/B5手册](BPTI_B4_B5_M3_REASONING_AND_EVOLUTION.md)中的M3按需篮球理由、D1–D6及HOLD/INTERNAL/MARKET比较、球队六级演化与已有工作台不可变历史；证据见[包C验收](development_reviews/BPTI_PACKAGE_C_IMPLEMENTATION_AND_ACCEPTANCE.md)。旧包B“未合并/包C未开始”是历史记录。

只运行C-C1～C-C5及直接失败项修正/复验，最终5/5 PASS（17.700s），未重跑旧B0/B1/B/M3/DEV14套件。修正合成蓝图必填状态、动作类型及测试导入路径，没有扩大测试。三队示例和跨队历史姓名/教练适配均为合成工程证据，不评定真实球队，也不认证比赛效果或存盘。

新增gm_decision submit-blueprint/record-evolution：CLI重新核对同批GM_SANITIZED，知识按游戏日期过滤；角色绑定当前可见技能，原生HOLD只限制不支持的内部动作，市场继续原M3门槛；蓝图修订要求重新评审/比较并刷新当前演化。BPTI_BLUEPRINT/BPTI_EVOLUTION沿原decision_artifacts/CAS/history/export，不新增数据库或审批。演化保留前态体系/文化，文化重构需跨季与管理层语境，不能由单月成绩或历史人名决定。

本包无新游戏来源、source_catalog项、原生registry字段或执行能力；第8节原执行能力表继续适用。OVERALL/Potential/Ability/Badge/unknown51及自由PlaybookID不开放；同批身份、本队书/全目录CRC、DEV14批准元组与CAS不变。Tempo含义/CRC类型/AI效果UNKNOWN，不能补造趋势或胜率。V3有效、GM_V4_NOT_ENABLED、真实30队UNASSESSED；DEV24、正式GM、采集/事实发布、新存档和游戏操作未启动。状态BPTI_PACKAGE_C_COMPLETE_TASK_CLOSED，源码Draft供玩家独立审阅/合并，不自动跟进。


## 2026-10-20 PR #12审查批准及DEV28下一阶段总规划

- 用户批准PR #12/BPTI C代码审查的F1–F4：蓝图更新下演化stale、跨save/generation历史串线、无native动作不该封锁合法市场、选定BLOCKED/RESEARCH内部动作等局部问题。Codex只在原Draft PR范围内修复和直接测试；PR #12仍由玩家审查合并，V3有效/V4不自动启用。
- **下一阶段唯一主计划**：[DEV28 GM全部原生设置候选可查、游戏动态事实完善、战术手册全生命周期和输出执行闭环](development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)。开发包D28-0（现状盘点）→D28-1（Book/Play/Slot/Coach真实绑定与换帅归位）→D28-2（静态可选项目录）+D28-3（DEV24比赛与人物动态）→D28-4（统一GM提案/执行/反馈）→D28-5（可用性和开档索引）。**所有后续包独立授权，不应夹到当前PR。**
- DEV27名字后缀修复已完成但是未完成30队全部本队Book目录、真实Coach PlaybookID绑定、Book指针/槽读回以及跨保存持久化；不能将`team_book()`一次成功当完整执行。DEV23三本书共204槽，148非空，111命名、37未知；类型、真实受益人、3D调用仍未认证。现有DEV14/GM权限及全部批准约束保持原样。
- Antigravity找可读/写原生来源+名字/游戏描述/战术类型，Codex复用M0/Registry/DEV14实现统一可查询合法选项和真实落地；逐场比赛/球员及高级统计以DEV24标准为准，缺失仍NOT_OBSERVED。Codex需要人类说明时**提交现有工作并TASK_CLOSED**而非活跃WAITING。

## 2026-10-20 工作包B：B2/B3/四类历史机制已完成，独立Draft交付

DEV27的867fe85与80459b4已按玩家新指令合入远端和本地main（快进到80459b4），本包从该主线建立codex/bpti-package-b。140条分级NativeBinding、30张五层历史TeamIdentity及四条NBA官方早期机制已通过现有Knowledge.bpti / gm_knowledge只读查询接入。用法见[B2/B3手册](BPTI_B2_B3_NATIVE_BINDINGS_AND_TEAM_IDENTITIES.md)，证据见[验收报告](development_reviews/BPTI_PACKAGE_B_IMPLEMENTATION_AND_ACCEPTANCE.md)。

实际仅执行B-B1～B-B4，首次4/4 PASS（0.869s）。截至2021-10-19，普通GM可读10/10家族入口，其中6张完整参考卡、4条狭窄机制；原四张复合研究卡仍阻断，不解锁未来材料。CRC类型匹配为零，原生动作受益人、ACE和精确效果继续UNKNOWN。30个历史seed均未绑定存档，不改变真实30队UNASSESSED。

没有新增游戏来源、source_catalog项或执行能力；OVERALL只读、本队书/新同批CRC/GM_SANITIZED/DEV14审批不变，Potential遮蔽不变。B4/B5/B6与DEV24未开始，V3有效/V4未启用。包B只发布源码Draft PR，不自动合并，不采集/上传游戏事实或写游戏。状态BPTI_PACKAGE_B_COMPLETE_TASK_CLOSED；以下DEV27/DEV23旧状态是历史交付记录。


## 2026-10-20 team_book名称后缀局部修复（独立分支，未合main）

玩家明确只修名称后缀。在`codex/fix-team-book-suffix`中，`src/gm_state_io/team_book.py:team_book()`保留原精确名称匹配，并将移除独立末尾Playbook标签后的名称同既有name/abbreviation/city+name精确别名比较，因此Bulls可对应Bulls Playbook（Heat/Warriors同理）。不改全局normalized()、不做包含/前缀/模糊查找，不改返回的index/enum_id/unique_id/name；多个匹配仍报TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS，不挑第一个。本队归属、身份摘要、CAS及批准路径均保持原实现。

仅目标函数、DEV27授权T1–T3小型静态验证与必要交接文档变更；三项一次通过（3 tests，0.005s），未运行旧套件。验收报告：[DEV27](development_reviews/BPTI_DEV27_TEAM_BOOK_SUFFIX_FIX_AND_ACCEPTANCE.md)。状态`BPTI_DEV27_BUGFIX_COMPLETE_TASK_CLOSED`；按玩家最新“直接提交即可”，本地实现提交`867fe85`，未创建Draft PR或合main。未打开游戏、采集、发布数据或写内存；没有验证真实执行/存盘。下方DEV23未修记录是原调查快照；原生类型UNKNOWN、其它功能/计划不在本次范围。

## 2026-10-20 DEV23 / PR #10：玩家已接受“战术知识基础设施”并批准main合并

玩家明确接受DEV23研究及共享战术池工程（88a16ec），同意[PR #10](https://github.com/chris2gao/nba2k22-gm-engine/pull/10)作为战术知识基础设施并入main。合并提交与实际状态读取PR/Git；下方原Draft/未合并文字为此前交付快照，不再代表玩家审批状态。1392条共享引用、1345个静态名、1335条名称推断用途及GM只读入口在本次接收范围内；精确原生类型仍UNKNOWN、用途适配为定性推断、team_book后缀缺口未修，不将接收升格为比赛效果或执行批准。没有追加测试、采集、数据发布或游戏操作。

## 2026-10-20 共享战术池：玩家追加授权的数据结构与GM只读检索

沿原Draft PR #10追加实现[共享池手册](GM_SHARED_PLAY_POOL_V1.md)：纯`gm_core/play_pool.py` DTO/引用查询，`Knowledge.play_pool()`按需接现有M2，`gm_knowledge.py`新增play-search/show/book/coverage，离线生成器build_gm_play_pool.py。知识文件在`web_gm/knowledge/plays/`，不是第二个事实数据库。1392个归档独立CRC，1345有静态名，47未知名，1335有名称推断用途，49用途未知，8仅Favorite组；455由多本书引用。用途/角色/球队打法/风险有规范化适配资料，查询时解析给GM，不把名字线索当逐条动作或原生类型认证。

每条types支持多类型成员及各自证据，当前精确类型均UNKNOWN；type_candidates单列，默认类型过滤不含推断，显式开关才能参考候选。原生ID去重，同名异ID不合并；手册保留68槽引用及30/20/10/8分组容量，分页报告归档占用，不宣称是当前存档。两种四槽均按前优先/更多执行的玩家规则保存；共享池中的动作可被其它球队加入/替换进本队手册，不能误解为改其它队书或只允许原来本队的CRC。当前执行器本来就是同批已加载全目录CRC限制，本轮未改变。

本次明确授权知识结构/适配性/GM读取，没有自动扩成整套B2–B6、真实GM或V4启用。执行了无地址归档种子整理及离线构建/构建内一致性读取，未运行新增/旧测试、采集、发布游戏数据或进程访问。source_catalog仍只描述原生产来源，无新原生字段/执行能力可注册；现有Knowledge读取能力及限制在本节更新。team_book后缀缺口仍未修，真实30队UNASSESSED。

## 2026-10-20 DEV23：三队核心Playbook只读研究部分交付，TASK_CLOSED

交付[Draft PR #10](https://github.com/chris2gao/nba2k22-gm-engine/pull/10)，研究提交`583b695`；未合入main，本节描述该独立分支的研究成果。

玩家后续E09/E10已回答操作问题（PLAYER_REPORTED_UI）：战术可跨多个类型分类，类型不匹配不能装载；球员第1/2类型主用、3/4偶尔，执行效果、教练及多因素会影响选择；指定调用是玩家按键，CPU对打自动执行，无固定位置资格限制。[手册与玩家规则补录](development_research/BPTI_DEV23_MANUAL_AND_PLAYER_CALLING_RULES_ADDENDUM_V1.md)已核对官方PC操作手册、2021年原作者经验与项目字段层。无需固定受益人证明作为类型资格前置；玩家明确不深究精确频率/算法。Q4–Q6全部已答，当前没有待答问题；逐CRC类型仍为技术缺口。球员四类型、球队四Freelance、POE侧重点/节奏/篮板与得分选择分开，不新增接口或测试。

从main `b3ace72`独立分支`codex/bpti-dev23-playbook-semantics`交付[研究报告](development_research/BPTI_DEV23_CORE_PLAYBOOK_SEMANTICS_AND_ROLE_EVIDENCE_V1.md)与[机读库存](development_research/BPTI_DEV23_PLAYBOOK_SEMANTICS_INVENTORY_V1.json)。状态`BPTI_DEV23_PARTIAL_REQUIRES_PLAYER_DESCRIPTION_TASK_CLOSED`；交付后结束，不设置等待玩家检查点。B1 PR #9已合并main，合并提交`f4d615c14f0b541fc9f1395b7035952b01e0e417`；下方旧B1阶段说明不覆盖此事实。

完成静态目录/历史密封SQLite与玩家允许的管理员只读进程调查：CHI/MIA/GSW各68槽，共204槽/148非零；111槽/89个不同CRC与本机PE静态标签精确匹配，37非零槽名UNKNOWN。46名当前球员四有序PlayTypes/Initiator与47条历史名单分来源保留；当前游戏档身份未确认，不绑定旧career。逐战术native type、发起/第一/第二受益人全部UNKNOWN，实际比赛执行未观察。类型覆盖/匹配不得从名字推定，未知时HOLD，不误报STATIC_PLAY_TYPE_UNSERVED。原文字问题已由后续E10答复，见本节上方补录；操作说明与原生证据分级保存。

发现当前`team_book()`不能匹配带` Playbook`后缀的三本实际标签，返回TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS；本轮只记录，没有修改/测试或绕过业务入口。已整合的Antigravity读写能力仍按DEV14原限制，名称研究不修复该阻断。没有实现B2–B6/DEV24、没有自动测试/旧测试重跑、正式采集、数据发布、游戏写入或正式GM。研究文件不加载进Knowledge默认视图，也不是GM_SANITIZED源；source_catalog、原生字段registry和执行能力白名单无新增/提权。V3有效、V4未启用，实际30队UNASSESSED。

## 2026-10-20 BPTI B1：十体系知识卡与有界检索（PR #9已合main；下文保留原交付范围）

玩家本次明确授权合并B0，PR #8已合main（e4b397e721a5b2fa91de557db5c1dc339e66f437）。随后从该最新main建立独立codex/bpti-b1-system-cards，实施DEV25：原SystemCard契约下十张完整知识卡、六条开档前机制Claim提取，原40复合Claim保持不变。沿Knowledge.bpti()/ResearchIndex与gm_knowledge新增bpti-system/bpti-systems，按ID/角色/反制有界查询；普通GM整卡来源/时间裁剪后才返回正文，研究全文显式RESEARCH。

创建数、研究查询数、GM可读数及实际三项验收证据见[B1验收](development_reviews/BPTI_B1_IMPLEMENTATION_AND_ACCEPTANCE.md)；用法/范围见[B1手册](BPTI_B1_SYSTEM_CARDS_AND_RETRIEVAL.md)。十卡齐全不等于GM十卡全可读，更不等于已认证原生行为。所有native_binding_refs为空，M3自动接入/B2/B3均未实施，真实30队仍UNASSESSED，V4未启用。下一阶段DEV23待玩家另行批准，DEV24仍后置；没有新采集/发布、游戏访问或能力修改。

## 2026-10-20 BPTI B0：知识契约与最小工程基础（PR #8已合main）

从最新main `6af12ba`建立独立`codex/bpti-b0-knowledge`，仅实现DEV22的B0。四类纯DTO（SystemCard/TeamIdentity/NativeBinding/SystemBlueprint）、来源/时间/非执行载荷校验及M2按需查询已实现；没有另建事实库或GM系统。研究索引覆盖R1十家族及R2三十队最小Claim，缺源和复合时间未拆分项保持UNKNOWN/SOURCE_MISSING，不等于B1完整卡或B3实局评估。

契约与用法：[BPTI_KNOWLEDGE_CONTRACT_V1](BPTI_KNOWLEDGE_CONTRACT_V1.md)；原始三项验证：[B0验收](development_reviews/BPTI_B0_IMPLEMENTATION_AND_ACCEPTANCE.md)。PR #8已按后续玩家明确授权合并，见本页B1增量；没有重跑B0或旧M3/DEV14集合。B0没有游戏来源/执行能力变更，无需修改source_catalog或执行能力白名单。V3继续有效、V4未启用、实际三十队仍UNASSESSED。

## 2026-10-20 DEV20/M4：系统自我进化工程完成，PR #7已合并main

独立审核后仅修正CAREER/IDENTITY跨存档复用局部event_id的幂等身份，完整scope入键；SYSTEM保留全局键与已登记记录。按玩家本次授权，只补并运行原test_02，1项通过（5.909秒），未重跑其余项目。收尾合并由玩家本次批准，不扩展Issue #6或后续工程。

已合并[PR #7](https://github.com/chris2gao/nba2k22-gm-engine/pull/7)，实现提交`652d10763b7bcfa6db811515f148014db74c609c`，修正提交`1e4fb665c30ad1863694cdf3dad360e84e32ce7f`，Ready后按玩家批准合入main，合并提交`c51fa36080ed39c8305635f1cb4363128475fdf0`。正式本地工作区已同步；远端新增BPTI研究文档完整保留，没有启动其开发。

状态 **M4_ENGINEERING_MAIN_MERGED / GM_V4_NOT_ENABLED**。玩家正式授权M4工程，从最新main `5a49d71`建立独立`codex/dev10-m4-system-evolution`，不混入已合并PR #4。权威范围为[DEV20](development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md)，覆盖旧M4“经营效果比较/比赛校准”混合定义。交付见[M4手册](M4_SYSTEM_EVOLUTION_WORKBENCH.md)、[实际验收](development_reviews/M4_SYSTEM_EVOLUTION_IMPLEMENTATION_AND_ACCEPTANCE.md)。本M4工程已合并正式main，经营规则/V4仍不启用。

- `gm_development_feedback.py ingest/list/show/triage/export/readiness`：原派生gm_workbench新增development_issues/events，稳定根因/能力/作用域指纹、跨批追加、同事件幂等、玩家决定/CAS/历史、有界SQL分页和引用输出。没有新游戏来源、事实库或内存执行器，也不扫描/自动push/建Issue/唤醒模型/修复Bug。
- 五项授权最小验收通过：实际CLI的事件追溯、跨批去重/历史、人工状态及修订边界、小型导出、诚实readiness。首轮共同URL校验误判修正后5项通过，未重跑已通过项/旧M3或DEV14集合。只用隔离合成来源及已有只读报告；无游戏访问、采集或额外测试。
- [CURRENT问题索引](../web_gm/development_feedback/CURRENT.md)与机器索引/每项详情已从本地工作台生成：Issue #6 P1/DEFERRED；BPTI、季后赛采集接口、独立双引擎校准器为P2/DEFERRED规划指针。occurrences为独立证据导入数，不是生产故障次数。下一次玩家主动触发开发规划才评估范围/成本，索引不是执行命令。
- [readiness清单](../config/m4_readiness_evidence.json)按实际日期/引用分开报告：M0–M3-T工程已合入、PR #4 MERGED，M4在该次导出时为待合并分支；当前PR #7合并与部署以本节回执为准。CURRENT/readiness保留原导出日期快照，后续由玩家显式触发更新；不把一次性索引冒充实时数据库；三Web实际连接、真实已脱敏新批次及GM消费、GSW/SAS/OKC新来源演练均PENDING；实际30队UNASSESSED、正式0队。Issue #6仍有完整目录生产路径阻断风险，未修复/重测，不宣称所有采集必然失败。BPTI为正式新档前置，季后赛采集与年度校准另立项目。
- V3继续生效、V4未启用；未改SOP/GM_CURRENT/正式赛季档案，未运行正式GM或新档。工程交付后停止，后续Bug修复、BPTI和校准由玩家独立授权。下方“M4未启动”等为历史阶段，不覆盖本次工程授权与交付状态。

## 2026-10-20 DEV14与M3-T均已正式合并，PR #4收尾完成

PR #5已按玩家批准合入main，合并提交`570419a`、最终开发提交`f68d75d`。下方DEV14“未合并”是交付时历史记录，不再代表当前部署状态。M3窗口在原PR #4分支以`82083b5`整合本底座，保留M3A/M3B并完成DEV13/M3-T本地工程；玩家已批准PR #4，标记Ready后合入main，合并提交`504a4c0656bad0e890c3783c89c656fca5b2e647`（开发head `7e8ba1a`）。正式本地工作区`E:\games\NBA 2K22\Antigravity_GM_Engine`已切回main并同步。合并时保留main新增规划文档；无额外测试或运行。采用开发规范V2，本任务八项最小验收均通过：首轮6项、修正样例后仅复验另2项，未重跑已通过旧集合。详见[实现与验收](development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)、[GM操作手册](../web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md)。

- 接入脱敏M0事实、原生对象/代次/Registry来源、八体系熟练度、四PlayTypes/Initiator、48具名倾向、6+5训练和Intangibles；D1–D6全员角色/分钟目标、内部修复比较、市场缺口和证据质量进入原工作台。普通GM仅个人防守、不写OVERALL；教练普通18项、本队已加载同名书68槽。新档或确认换帅后独立TEAM_BOOK_REBIND，绑定后新来源再另提槽位；换帅只休赛期每队每季一次，无员工市场执行器。
- 稀疏意图通过既有DEV14纯离线build_plan生成实际digest/审批tuple/diff，交易后或绑定后需重计划，导出不等于stage/批准/执行。Potential=1只为MASKED/NOT_GAME_OBSERVED；旧未脱敏包与旧缓存禁供GM。51未知倾向、CRC语义、疲劳/更多位置模板仍UNKNOWN，交Antigravity后续。
- 已发现DEV14完整Registry元数据中的世界设置键`world.contracts_and_finances.player_potential_factor`被净化器误识别为球员潜力别名；完整目录合成输入被阻断。玩家已明确选择本轮不扩展修复或追加1项检查，记录给DEV14窗口①后续修复。M3八项验证使用实际观察字段目录及真实净化凭据，不代表完整生产采集已验收。详见上述报告。
- 真实30队策略仍UNASSESSED、正式评估0队；V3继续生效、V4未启用、M4未启动；本轮没有游戏访问/写入、正式GM、新采集/发布或正式赛季档案改动。

## 2026-10-20 DEV14-H / DEV15：PR #5增量工程（未合并）

**开发规范V2：玩家要求任何扩展设计或追加测试先询问并等待确认。** 原定范围完成即交付，不继续为完备性扩展；规则已写入AGENTS和DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY。多存档采用独立目录/数据库的简单结构，review可选，不追加权限防伪工程。

代码版本`DEV14_V1.2_H_DEV15`，控制库user_version仍1；新增观察策略表`player_potential_masks`，M0保留`gm_sqlite_m0_v1`并增加rotation域和`require_gm_sanitized()`。Registry指纹随字段/策略改变。证据和最终提交查[DEV14_TO_M3_HANDOFF](development_reviews/DEV14_TO_M3_HANDOFF.md)，本节不代表main部署或正式游戏验收。

- H1：league/pool/control三库实际save/instance/generation与capture_id/snapshot/时间一致；先暂存、日志安装，失败恢复旧完整文件；PREPARED中断阻断托管入口，显式`save recover-capture`恢复，不释放未解决的原生写锁。
- H2按玩家2026-10-20最新决定简化：保留聊天中的具体方案批准、完整tuple/显式写入开关和原值回读，信任操作者批准引用（MANUAL_OPERATOR_TRUST_ONLY），不研究防伪或独立OS权限。apply/rollback可由Codex执行，review仅可选；文件或approved=true本身不构成批准。3项直接相关增量检查通过，不追加隔离研发。
- DEV15：full_verified_v1自动在原生RO采集及初步校验后、库安装/hash/JSON/backup/M0之前净化Potential；pool/roster/DEV14 PLAYER镜像的结构化、JSON和0x441均为1。记录覆盖数和非Potential字节指纹；Staff及游戏内存不变。旧M02/Release/Git历史不修改、禁供GM，无脱敏标记旧包禁止重发；公开旧历史仍可能含原值，未声称删除。新生产批次仍待玩家触发。
- Intangibles：`rotation.intangibles` / `PLAYER_ROTATION_OVR_BIAS`，25–99，profile/rating codec、唯一0x440、批准/CAS/回读/恢复；不开放其他能力或锁分钟。正式写入/UI效果/存盘均未验证。
- 普通GM：19默认的原生能力保留，PlaybookID仅限TEAM_BOOK_REBIND；整体18项只读、个人18项受控。本队同名已加载书68槽可编辑，新档/已确认换帅后绑定需独立人工确认，绑后重新取源再改槽。6+5训练、4PlayTypes/Initiator、48命名倾向沿用；51未知倾向、疲劳和CRC真实行为仍UNKNOWN。
- 窗口职责：只交DEV14底层；PR#4须接新的脱敏检查和Registry/operation合同后独立做M3-T。未合并PR、运行真实采集/发布/游戏写入或启用GM V4。

手册：[DEV15](DEV15_ROTATION_AND_POTENTIAL_RUNBOOK.md)、[GM数据语义](../web_gm/manuals/GM_POTENTIAL_FOG_AND_ROTATION_BIAS.md)。下方历史记录按本节新策略解释。

## 2026-10-19 DEV14 V1.1：确定性状态 I/O 与多存档底座

独立 `codex/dev14-state-io` 分支实现 A/B/C/D，未合并前不称 main 已部署。入口 `scripts/gm_state_io.py`，手册 [DEV14_STATE_IO_RUNBOOK](DEV14_STATE_IO_RUNBOOK.md)，实际验收见 [DEV14_ACCEPTANCE](development_reviews/DEV14_ACCEPTANCE.md)。沿用原生 coach/defense codecs、进程锁、full_verified_v1、SQLite backup、M0；GM 只给稀疏意图，Observed/Desired/Applied 分库、实例/代次/来源批次/批准摘要绑定。真实采集和游戏写入本轮均未触发，GM V4 未启用。

| 能力 | 当前实现和证据边界 |
| --- | --- |
| 字段/控制库 | 原19默认/18整体、个人防守、4 PlayType/Initiator、99倾向原字节（48命名可写）、68战术本槽、4双侧Gameplay、50世界设置、11训练字段接入；5 Sim只读。原生证据继承，统一引擎只做合成验证 |
| 执行 | stage/validate/preflight/apply/receipt/rollback；整批RO后RW、共享块mask合并、durable preimages、逐块回读/条件恢复/部分留锁；MEMORY_VERIFIED不声称游戏存盘 |
| 采集与访问 | 现有全量入口同RO会话扩充、既有来源审计/双库备份/M0静态分域查询；旧M02不追填。生产部署后只在玩家下次全量触发时出现新观测 |
| 存档 | 最多4档、唯一ACTIVE、create/adopt/activate/deactivate/retire/reset/recover；每档私有控制库，新代次清洁三库；发布历史无代次兼容时同名reset拒绝并要求新ID |
| 明确限制 | 游戏唯一save身份无法独立证明，正式动作须人工确认完整save/instance/generation；导师关系、未命名倾向语义、未提供可用布局的剩余世界曲线/Gameplay目录保留扩展；不泛化人物能力/徽章/合同写权限 |

以下历史说明不应把本工程的合成/静态验收升级为生产观察、已批准GM或main部署。

## 2026-10-19 DEV10 M3A/M3B：本地工程实现与范围内验收

状态 `M3_LOCAL_ENGINEERING_COMPLETE / WEB_CONNECTION_DEFERRED / GM_V4_DRAFT_NOT_ENABLED`，开发分支`codex/dev10-m3-design`，PR #4。按玩家确认的Astra设计审阅→编码分工交付M3A与M3B；[M3A验收](development_reviews/DEV10_M3A_ACCEPTANCE.md)、[M3B验收](development_reviews/DEV10_M3B_ACCEPTANCE.md)、[分析操作手册](../web_gm/manuals/ANALYTICS_M3_WORKBENCH.md)、[GM操作手册](../web_gm/manuals/GM_M3_DECISION_WORKBENCH.md)为当前入口。下方“设计待编码”保留阶段历史，以本节为准。

- M3A：已有team_source_stats的静态安全投影；全队全员事实/实际访问回执、明确上下文的区间计数差分、人物暂定匹配与UNKNOWN、固定M1/M2版本、注释导入/封存、有界钻取与角色字段筛选。封存后的市场补查独立追加，不改原包。
- M3B：全30队精确名单/六维/三类方案、独立兴趣和同版双方接受；候选竞争与所选资源/字段/执行依赖区分；当前M1组合成本、真实纯离线教练batch/dry_run/verdict/digest、唯一终稿历史、M2策略候选与事前观察假设。纯Python形状/业务校验，不新增模型API或游戏执行器。
- 实际已有M02只读演练：30队/466在队身份/1458员工/30球队统计/30教练/870整体防守/504原始签位行/30财务行。GSW/SAS/OKC完整身份分页一致，三类市场查询已实际运行。M02包为SEALED_PARTIAL，未填30队经营判断；全合成30队则通过P1–P5 CLI流程及v2终稿修订。范围内15项检查、89次主流程CLI演练与补充检查见验收，未扩大现金、网页或实机验证。
- **正式30队策略仍为UNASSESSED，正式评估0队；GM V3继续生效，V4未启用。** 没有正式GM/W03/赛季索引或GM_CURRENT变更，没有采集、数据发布、游戏访问/写入；M4未启动。工作台、合成样例和完整离线工件位于_exports，不提交SQLite/运行日志。
- Antigravity同期main提交`9b4fe87`仅新增7个DEV12文件，没有改M3分支或M0/M1/M2接口；当前M3不导入这些模块，无需撤销它来继续本任务。该提交的能力不作为M3验收依据。PR #4源代码审阅/合并和正式本地部署另按玩家指令，不能把开发分支交付写成main已部署。

## 2026-10-19 DEV10 M3：玩家已启动，Astra设计交接

玩家明确“开始M3”，并切换Astra Extra High。沿已约定分工，本阶段完成M3A分析包与M3B候选GM V4的设计/审阅，状态`ASTRA_M3_DESIGN_READY_FOR_SOL_IMPLEMENTATION`。入口：[M3总设计](development_tasks/DEV_20261019_10_M3_DESIGN_AND_IMPLEMENTATION_ENTRY.md)，[实现任务书](development_tasks/DEV_20261019_10_M3_IMPLEMENTATION_HANDOFF.md)，[设计审阅](development_reviews/DEV10_M3_DESIGN_REVIEW.md)。

设计包含同批SQLite累计统计投影、30队全员事实/访问覆盖、跨批指标与身份层级、按角色问题筛选候选、M1成本/M2策略引用、五个内部研究阶段、双方同版报价接受、选定资产/教练字段与执行依赖冲突、唯一终稿及事前假设。15个合成案例是待实现行为说明，不是已通过M3测试。

**M3运行CLI/工作台表尚未实现，M3工程尚未完成。** 正式30队策略仍UNASSESSED；现行V3保持生效、V4未启用；本设计不启动正式GM或更新W03。下一步按玩家模型安排由Sol实现M3A/M3B，再给实际工程验收。网页连接仍由玩家后续建立，不阻塞内部开发。M4、实时赛场调校、训练/员工任免、媒体世界等不在本轮范围。

代码/文档基线7a60d5e已包含M1/M2正式合并、最新3D赛场及原生控制发现研究；玩家已确认全局设置可修改，新NC01–NC15候选不当现成执行器。本轮未修改运行源码、事实/发布数据或游戏，没有采集、实际数据库分析或实机测试。下文“不启动M3”保留上一阶段边界，本次新授权和状态以本节为准。

## 2026-10-19 DEV10 M1/M2工程收尾（PR #3）

状态 `M1_M2_ENGINEERING_COMPLETE / WEB_CONNECTIONS_DEFERRED_BY_PLAYER`。本节随PR #3合入正式main后生效，优先于下方“本地实现、待分支审阅”历史记录。M1财务情景与M2知识/策略接口工程完成；操作入口与前次证据沿用下节链接，收尾记录见[DEV10_M1_M2_CLOSEOUT](development_reviews/DEV10_M1_M2_CLOSEOUT.md)。

最新审查提出的自定义路径问题已修复：共享工作台和财务导出均拒绝saves/query_snapshots/published/seasons，解析后忽略大小写；仅运行3项直接相关的临时目录检查并通过。已核对并纳入最新main的研究文档/记忆索引，无文本合并冲突，不复跑前次7+6项测试。

**30队策略仍为UNASSESSED候选，正式评估0队；GM V4尚未启用。** 不启动M3/M4。网页真实连接、cash实测、实际签约验证仍按玩家安排延后。本轮未连接游戏、采集、发布游戏数据或修改任何数据库观测事实。PR合并状态及SHA以实际GitHub记录为准，正式本地main同步后才作为执行仓库的新代码基线。

## 2026-10-19 DEV10 M1/M2：本地实现完成，待分支审阅

状态 `M1_M2_IMPLEMENTED_LOCAL / WEB_CONNECTIONS_DEFERRED_BY_PLAYER`。玩家从Astra设计交接切换Sol并明确开始实现。本节优先于下方原“设计待实现”历史记录；正式main仍按实际合并状态判断，不将开发分支当作已部署。

- M1财务工作台：三年合同/资产情景、KEEP/内部优化/交易签约比较、来源与假设标记、合同钻取及摘要导出；7项直接相关检查与已有M02 30队×3年静态CLI验证通过。见[M1手册](GM_FINANCE_WORKBENCH.md)、[回执](development_reviews/DEV10_M1_FINANCE_ACCEPTANCE.md)。槽序投影不是已认证保证工资或签约容量。
- M2知识与策略：12张战术卡、30队2021参考、19条机制、38来源；小结果检索与同批原生字典解析，Drop保留假设。共享派生库支持追加策略revision、旧版读取/冲突检查、可选finance run；6项M2检查及M02静态CLI通过。见[M2手册](GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH.md)、[回执](development_reviews/DEV10_M2_KNOWLEDGE_ACCEPTANCE.md)。
- 30队初始化结果为UNASSESSED候选，正式已评估0队；GSW/SAS/OKC仅提供有条件的研究方法，未写本局球队决策。策略保存/导出不是批准或执行。
- 没有新增游戏采集来源或业务写入器，来源登记和原执行能力范围不变；工作台与事实库隔离。没有运行生产采集/发布、正式GM、游戏写入、Web连接、现金实测或签约实机验证。保持当前GM规则，M3/M4及V4切换等待后续任务。
- 开发规范继续以优秀实现为主，验证只覆盖本次关键路径。允许开发时被认为正确的未知bug日后发现修复，现金例子不追加本轮调查。

## 2026-10-18 DEV10 M1：三年财务情景已实现

版本 `gm_finance_projection_v1`，`IMPLEMENTED_LOCAL`。`scripts/gm_finance.py`提供project/compare/show/list/export，读取M0同批静态双库并写独立派生workbench。区分槽位原值、已知小计、假设投影、选项/延期、财务资格与执行状态；支持球员/简单签转移、新签/替换/未来延期情景，不运行报价或游戏写入。

7项直接相关测试通过；已有M02静态来源生成30队×3年，并钻取GSW/SAS/CLE、验证小批查询/KEEP/导出。见[M1回执](development_reviews/DEV10_M1_FINANCE_ACCEPTANCE.md)、[手册](GM_FINANCE_WORKBENCH.md)。三年为显式槽序假设，未认证未来保证薪资或签约容量；Web连接、现金实测仍延后。M2沿既有设计继续实现，现行GM规则不变。

## 2026-10-18 DEV10后续：M0已合并，M1/M2设计与研究交接

M0 PR #2已合并，正式main代码基线为 `67bf4dc`；玩家随后切换Astra并明确开始后续流程。当前状态 `ASTRA_DESIGN_COMPLETE / SOL_IMPLEMENTATION_NEXT`，入口：[M1/M2实施交接](development_tasks/DEV_20261018_10_M1_M2_IMPLEMENTATION_HANDOFF.md)。

- M1已完成三年合同/资产情景的算法、来源与假设口径、接口、最小派生库和针对性验收设计。未来工资容量未认证时不抹掉可计算结果，也不擅自制定老板预算。
- M2已完成12张战术卡内容、GSW/SAS/OKC三队条件式方法、30队2021官方背景参考和长期策略状态/修订/检索设计。现实参考不是本局球队决策，现行GM规则未切换。
- 本轮成果是设计和研究文档；尚未实现M1/M2 CLI、工作台表和正式球队策略。下一步按玩家模型安排由Sol实现，M1/M2分别验收；Web连接和现金实测延后，不追加为研发门槛。
- 本轮没有运行测试、M02查询、采集、游戏写入或正式GM。旧下文“M0不实施M1—M4”是M0原交付范围，当前新授权与状态以本节为准。

## 2026-10-18 DEV-10 V2 / M0：本地 SQLite 按需访问

玩家开发规范已归档为 [DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md](DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)：边界先行、实现优先、只做范围内必要验证；接受实际使用中发现数据解释等问题后续修复，不追加穷尽式测试。本轮不为cash假设追做游戏UI/签约机制验收。

版本 `gm_sqlite_m0_v1`，状态 `IMPLEMENTED_LOCAL / WEB_CONNECTIONS_DEFERRED_BY_PLAYER`。从既有审计 Release 双库备份生成不可覆盖静态查询副本；新导出复用同一备份自动建立本地副本。`scripts/gm_data_query.py` 提供球队/名单/球员池/员工岗位及候选/合同/19教练/18对手防守/三届选秀权/财务查询与受限SQL聚合，默认20、最多50条，约20KB预算，游标固定批次。不会让网页模型直连活动事实库；专用消费者账号及ACL脚本见[操作手册](GM_SQLITE_QUERY_ACCESS.md)。

本地M02查询、隔离安全测试和导出钩子测试的实际证据见[M0验收](development_reviews/DEV_20261018_10_M0_SQLITE_ACCESS_ACCEPTANCE.md)及[机器证据](development_reviews/DEV_20261018_10_M0_LOCAL_EVIDENCE.json)。玩家在开发中明确取消本轮三Web窗口实际连接验收前置条件：完成实现/PowerShell验证后由玩家建立连接，连接问题以后修复；不声称三窗口已测或M0_CONSUMER_ACCEPTED。

cash仍保留uint32，signed32仅单列假设；资金/收入周期与签约容量不认证。没有修改真实财务数值、历史批次或published数据，无新采集/发布/游戏写入。全量-only与时间戳同步不变；不实施M1—M4、不切换现行GM规则。下次开发重读本节及手册，实际连接仍由玩家后续安排。

## 2026-10-18 首次教练生产来源启用回执（优先于下方历史待运行说明）

状态：`FIRST_PRODUCTION_CAPTURED_AND_PUBLISHED`。玩家触发正常 `full_verified_v1` 全量流程，沿用存档 `mc_haliburton_2021`、2021–2022赛季，游戏日期由玩家确认12月12日，记录为 `2021-12-12`，框架M02、普通检查点。日期不是内存自动观测，未标月末闭账。

- 快照：`2021-2022_M02_DEC12_FULL_20261018`；发布批次：`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`。
- `data_updated_at=2026-10-18T12:12:13.170996+00:00`；`uploaded_at=2026-10-18T12:14:23.439960+00:00`；`upload_status=UPLOADED`。数据发布提交：`a84e1b522e66d189f77f28f2f84947f9bee35b84`。
- 源审计 `PASS_VERIFIED`，教练同源审计通过；SQLite本快照包含30队、每队19默认字段、每队29个对手整体防守组，共870组。
- 本批包含 `coaching/teams.json`、`coaching/field_dictionary.json`、30份球队对手文件；字典有19默认字段及18项对手防守字段，coverage为 `coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`。
- 已读取GitHub main的最新指针，数据库Release附件状态为uploaded；现有 `gm_core.data_reader.DataReader` 成功装载30队教练并读取指定对手。网页GPT实际连接未代替玩家测试，不声称已运行正式GM。
- [最新数据入口](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/latest.json)；[本批数据库Release](https://github.com/chris2gao/nba2k22-gm-engine/releases/tag/data-2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2)。后续仍按玩家请求的新批次、时间和来源审计判断，不将此批次固定为未来事实。

下方DEV07开发验收记录保留原有技术证据；生产启用状态以本节真实回执为准。本次没有游戏写入、教练调整、比赛模拟或GM决策；新数据更新继续全量-only，已采有效批次仍可独立重发。

DEV07 V2已通过玩家审查，PR #1于2026-10-18合并main，合并提交`2509b3b6266accc2c95b17d8364bd80ffde225a3`，本地执行仓库已同步代码。首次真实生产采集与发布已于2026-10-18完成，见本页顶部真实回执。玩家最终明确将原生Tempo按raw开放、界面含义未知；该项不再作为开发阻塞。权威范围见[最终规格 V2](development_tasks/DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V2.md)，当前[字段矩阵](development_reviews/DEV_20261017_07_COACHING_FIELD_MATRIX.json)、[集成报告](development_reviews/DEV_20261017_07_COACHING_INTEGRATION_REPORT.md)、[批次验收](development_reviews/DEV_20261017_07_COACHING_BATCH_ACCEPTANCE.md)、[来源验收](development_reviews/DEV_20261017_07_COACHING_SOURCE_PUBLICATION_ACCEPTANCE.md)。六项 POE 沿用已验证证据；五项数值设置经 PHI 小步程序写入、玩家确认、日志恢复，30 队已捕获块完全恢复，见[滑块证据](development_reviews/DEV_20261017_07_SLIDER_EVIDENCE.json)。BenchDepth是轮换人数上限，9→10只是测试样本，玩家明确要求去掉此人为白名单；GM依据实际阵容选人数，仅保留原生整数格式保护。四项已确认百分比倾向为0–100。玩家已明确开放原生Tempo读写，界面含义未知，不称作已验证的进攻节奏或百分比；同局8位主帅已观测raw40–95，作为选择目标的实用参考，不变成执行白名单。四Freelance按完整原生枚举/布局和有序codec支持提案及受控执行，不宣称比赛内页面已实测；双体系/手册证据见下一段。五项 Sim 禁止 GM 控制。

双体系及命名手册已进一步在 PHI 与对手整体混合批次写入并恢复，14项默认字段有实机写回证据，另4项Freelance提供原生完整枚举的有序受控接口，加上玩家明确开放的原生Tempo共19项；玩家确认“主打内线→主打外线”和“76人→雄鹿手册”。PreferredSystem原生独立位域/回读通过，未单独查看其UI；玩家停止同类重复核对。Freelance不再因未做重复菜单测试而设执行白名单；Tempo原生raw接口已开放，界面映射未知。见[混合证据](development_reviews/DEV_20261017_07_MIXED_BATCH_EVIDENCE.json)。

指定对手“整体防守”已证明是 UI 批量修改该对手全部有效 matchup 记录，非单独 All 槽；PHI→IND 14 条 PressureOnball 经 UI 差分、程序写入显示“间隔”、事务恢复，所有已捕获块恢复一致。退出编辑页观察到 IsInUse 0→1，不能解释为 0=禁用。见[原生整体证据](development_reviews/DEV_20261017_07_OVERALL_DEFENSE_EVIDENCE.json)。批量执行与同会话采集/SQLite/JSON 集成代码已加入本分支，离线85项教练/40项GM测试及4个CLI帮助入口通过，首次真实全量生产采集/发布已通过，见顶部回执。[GM手册](../web_gm/manuals/GM_COACHING_OPERATIONS.md)和[执行手册40](40_COACHING_EXECUTION_RUNBOOK.md)已补齐19项/18项策略说明、完整外层提案与连续执行示例、首次部署/采集/发布启用核对。工程交付不冒充真实生产运行；实际使用按GM决策、玩家批准、执行回执及玩家反馈继续，不要求额外实机验收。以下 DEV06 记录保留历史含义。

状态版本：v5，2026-10-17。数据功能证据提交：`2d16a7d`；对应已发布入口提交：`875adb4`。本次基于`8274510`新增本地交易执行与签约候选源码；W02首次漏人数后已修复，玩家明确确认CHI/DET交易成功，标准交易v2已启用有限范围，见[文档37](37_APPROVED_TRADE_EXECUTOR.md)。签约只执行GM已定案的人物/去向/合同，源码未运行/未测试，写入关闭等待未来签约验证，见[文档38](38_APPROVED_SIGNING_EXECUTION.md)。既有休赛期P1模拟不被执行入口调用。这些证据不是以后任务的固定HEAD或固定数据版本。

教练开发增量（DEV06，2026-10-17）：[接口39](39_COACHING_TACTICS.md)、[实施报告](development_reviews/DEV_20261017_06_COACHING_IMPLEMENTATION_REPORT.md)、[验收矩阵](development_reviews/DEV_20261017_06_COACHING_EXECUTOR_ACCEPTANCE.md)、[全部已定位能力及对手评估](development_reviews/DEV_20261017_06_COACHING_CAPABILITIES_AND_MATCHUP.md)。旧TEAM POE语义/写入已撤销。PHI重点、AI IND六项均经玩家界面确认；保存及真实进程重启保持，IND六项已按新快照恢复内存原值。**仅六项默认POE技术就绪，须玩家批准具体方案；正式局未执行。** 其他字段分项保留限制。玩家停止恢复后额外保存重载，不宣称该项复核完成。Computer Use仅辅助；写前必须确认退出教练编辑页，防止缓存覆盖。下面旧数据批次证据保持历史含义。

**范围提示（2026-10-17）：** 本页专供 Codex 的文档 32（数据采集基线）、33（本地开发基线）和 36（批准方案执行基线）共同引用。网页版 GPT 的三份新基线位于 `web_gm/baselines/`，由 `docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md` 规定：Web GPT ANALYTICS 负责 GM 数据加工与报告 GitHub 回写，Web GPT GM 负责经营决策，Web GPT DEVELOPMENT 负责规划和给 Codex 任务书；这些都不会替代 Codex 本地数据更新、工程开发及具体批准后的执行职责。

本页供文档 32（采集基线）、33（开发基线）和 36（批准方案执行基线）共同引用。稳定职责写在提示词；易变的入口、能力、缺口集中维护在这里。新窗口开始任务时必须核对磁盘最新版和当前代码。

## 1. 先记住的规则

1. 玩家分别触发采集、GM、执行；前一步完成不启动后一步。
2. 脚本采集、Python/SQL 计算；模型不伪造字段和观测，不把历史 NBA 资料覆盖本局。
3. 采集只读游戏内存；每次校准当前进程。SQLite 是事实存储，JSON 是脚本生成的网页读取格式。
4. GitHub 同步只看采集/上传时间；源内存审计保留，不恢复 JSON 哈希、字段对比、下载复核。
5. 薪资只要求大名单球员薪资；不继续保障金额/死钱/完整现实 CBA 账本。
6. 选秀权只保留年、轮次、原球队、持有球队；无保护/交换玩法，只交易接下来三届。下一选秀年从已验证来源获取，窗口由 Python 计算。
7. 历史新秀库按真实新秀模型筛选；1984–2020 顺序轮回。自然成长由游戏控制，历史重力须具体批准，MC 成长故事暂缓。
8. 游戏写入、正式球队决策档案和批准执行脚本的具体变更受审批约束。模型自填 approved=true 不构成玩家批准。

## 2. 当前生产能力

| 项目 | 实际状态 | 入口/说明 |
| --- | --- | --- |
| 按新 save_id 初始化干净数据结构 | 已实现 | `save_context.py`、模板/schema；统一数据入口可创建隔离存档 |
| 当前存档全量更新 | 已实现 | `scripts/run_data_update.ps1`，`full_verified_v1` |
| 本次更新各步纯脚本运行 | 已实现 | 校准、采集、来源审计、计算/导出、按要求发布 |
| 中文关键词路由 | 由模型按第 3 节解析 | 当前没有把中文关键词直接作为命令行参数的路由程序 |
| 单来源独立生产更新 | **玩家明确取消开发目标** | 所有新数据采集一律全量刷新；不开发 -Sources 或 COACHING_ONLY |
| 单队独立更新 | **不规划** | 一次完整采集覆盖当前存档30队和全部已验证来源 |
| 不同来源不同采集时间的生产组合包 | **明确不规划** | 每次新批次都从同一当前游戏采集会话读取全部已验证来源；历史批次保留 |
| 同一有效批次重新发布 | 已实现 | `scripts/publish_web_snapshot.py --save-id ...`；不重新采集/改采集时间 |
| SQLite 备份 ZIP 与 JSON 自动导出 | 已实现 | `src/export_web_gm.py`；JSON 在 Git，ZIP 在 Release |
| 网页 GM 本地分析/计算/提案接口 | GM v1 已交付 | `src/gm_core/`、三个 GM CLI；无正式决策自动启动和执行权 |
| 休赛期自由球员系统 | P0部分研究；P1合成模拟源码未运行/未测试，规划器v1_1静态修正涨幅取整与RFA选择顺序 | `scripts/offseason_research.py`清点历史字段，`scripts/offseason_plan.py`/`offseason_validate.py`为合成来源离线竞价/回放入口；见[P0](development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md)/[P1](development_reviews/DEV_20261017_04_OFFSEASON_FA_P1_IMPLEMENTATION.md)。无真实休赛期来源、签约执行器或跨季验收 |
| 教练战术与批次接口 | main中的19项默认字段提供受控接口（14项有实机写回证据），指定对手整体已验收；Tempo按玩家明确选择开放原生raw，界面含义未知 | `coaching_batch.py` 和原有三个 CLI；默认纯离线；SQLite/JSON 同批集成已合并main；首次真实生产全量采集/发布已完成，见顶部回执 |
| 批准普通球员交易/简单选秀权 | 标准v2，CHI/DET经人数修复后玩家已确认成功；输入姓名/原队/目标队并由脚本固定身份 | `scripts/execute_approved_trades.py` / `run_approved_trades.ps1`；plan→显式execute→verify；限定布局/15人容量、计数保护/防重放。见文档37，不认证任意其他业务 |
| 通用交易、签约/裁员、历史新秀注入、历史重力执行 | 未完整验收 | 新实验代码不认证其他业务、原生交易日志或存盘持久化 |
| 模型自动派发、多模型谈判、v3 完整经营史 | 未完整实现 | 协议/边界预留不是生产功能 |

**当前执行结论（2026-10-18玩家明确确认）：**新游戏数据更新统一走`scripts/run_data_update.ps1`的`full_verified_v1`，一次刷新全部已验证来源（包括原生教练战术）。无单来源采集开发任务；独立`REPUBLISH`只重发已采有效批次。若玩家明确要求排除某来源，不能在不符合该约束时擅自运行全量，应先说明当前全量-only规则。教练首次正式采集与发布已完成，见顶部回执；原启用规划见[DEV08全量启用规划](development_tasks/DEV_20261018_08_COACHING_FULL_REFRESH_FIRST_PRODUCTION_V1.md)。

## 3. 数据任务路由（玩家只触发全量或重新发布）

规范生产行为**不是**将不同关键词转化成不同来源更新器。玩家提出“比赛数据、球员池、员工、球队信息、阵容、选秀权、教练”等**新数据更新**，统一解释为本次`FULL`更新任务，包含全部已验证来源；具体是否需要更新及是否上传由玩家触发决定。来源名称可用于解释GM需要何种事实，不能作为源级采集开关。

| 意图 | 实际入口与含义 |
| --- | --- |
| 新局/初始化 | 干净存档结构及一次玩家授权的完整全量采集，不继承旧局事实 |
| 月末/交易后/教练调整后/球员池/战绩/员工/选秀权等新数据刷新 | **全量**`full_verified_v1`：球队、球员池、名单/薪资、员工、赛季统计、选秀权、教练默认19项与29个对手整体防守等所有已认证来源，在同一批次读取 |
| 仅重新上传已有有效完整批次 | `REPUBLISH`：不连接游戏，不更改原采集时间，只刷新发布状态/上传时间 |
| 明确要求排除某个来源的任务 | 当前不支持此排除范围，解释完整更新规则；不得违背用户本次显式排除要求 |
| 伤病、精确个人分钟、逐场日志、游戏OVR等未认证来源 | 维持数据缺口，不把全量采集说成这些来源已存在 |

没有无人值守调度、按月自动触发或单独教练采集。任务以存档ID、游戏日期或获准UNKNOWN、赛季与事件上下文为前提；需`-Publish`才将完整审计批次推送GitHub。

## 4. 已交付的内存与数据库来源

实际字段解释查源码与 profile；这里不保留会重启失效的绝对地址。下面数量只描述本页证据批次，不可作为以后固定上限。

| 来源 | 已验证能力 | 本页证据批次 |
| --- | --- | --- |
| 名单目录/定位 | 双历史球员锚点，加目录布局/数组边界；球队、员工等来源来自同一目录 | 当前目录版本通过同 PID 强制失效缓存重扫；旧版本另有真实新 PID 验证，不能混称当前版本已重启验收 |
| 全局模型池 | 按目录数量遍历、姓名清理、草稿元数据、生日、55 项能力/潜力、历史新秀分类 | 有效模型 3,383；历史新秀模型 789 |
| 30 队阵容 | 名单身份、位置、55 项能力、生日、薪资；NULL 保留缺口 | 466 名大名单球员 |
| 制服组 | 按完整目录读取；NBA 球队指针和岗位反向核验 | 1,470 槽，1,458 个有姓名，240 个球队角色关联 |
| 球队战绩/统计 | 球队当前赛季统计索引与累计量；Python 场均和命中率 | 30 队；不是月度或逐场数据 |
| 球员技术统计 | 球员当前赛季统计索引与累计量；缺失索引为未知 | 389 名有当前统计记录 |
| 简单选秀权 | 当前/原球队、年、轮次；同版本原生 getter 签名复验；年份/轮次覆盖断言 | 300 枚未来资产；其中只有接下来三届允许交易 |

关键实现：

- `src/address_calibrator.py`：缓存探活、失效扫描、名单目录识别。
- `src/source_extensions.py` / `config/memory_field_profile.json`：字段、位域、统计、员工双向关联。
- `src/draft_assets.py` / `config/draft_asset_profile.json`：简单选秀权、原生 getter 版本验证、三届窗口。
- `src/dump_player_pool.py` / `src/historical_rookies.py`：全局池及 `raw[0x70] & 0xE0 == 0xE0` 新秀分类。
- `src/audit_sampling.py` / `src/audit_source_extensions.py`：源内存对照与完整性检查。

`is_rookie`、`rookie_tag_raw` 已不作为历史新秀筛选字段。潜力是 `+0x441`，旧 `+0xEB` 猜测废止。球队归属是指针解析，不取指针低字节当 team_id。运行时槽号与指针都不是跨存档永久人物身份。

当前工资规则仅配置 2021-2022；新赛季需要先确认配置与验证路径，不能静默复用旧规则签发结论。

## 5. 明确缺口与允许保留项

- 游戏显示年龄、OVR：未找到可靠的生产直接来源；玩家允许暂留缺口。生日已观测，旧代码有日期推算能力，推算结果不能称游戏显示年龄。
- 逐场比赛日志、精确并列排名、月度分段、伤病、完整轮换等：未观测，不用赛季累计值冒充。
- 玩家不要求继续做复杂合同/死钱/完整现实 CBA；不要列为阻塞采集交付的强制任务。
- 历史新秀候选查询与目标槽位写入是两件事，后者仍须独立实现/验收和批准。
- 选秀权已有权属和三届规则；旧候选批次不回填新认证。原始保护/交换位保留证据，不自动清除游戏中已有条件。

## 6. 数据与发布位置

项目路径可变时以当前根目录为准，不硬编码其他聊天的工作树：

```text
database/templates/                         干净模板配置/本地模板库
database/saves/<save_id>/league_state.sqlite 联盟历史快照
database/saves/<save_id>/player_pool.sqlite  当前完整模型池
database/saves/<save_id>/snapshots/          来源清单/审计/报告
published/index.json                        多存档入口
published/saves/<save_id>/latest.json        当前线上批次和两个时间戳
published/saves/<save_id>/batches/...        自动生成阅读包
_exports/archives/                          本地数据库 ZIP
_exports/receipts/                          发布回执
```

仓库：`https://github.com/chris2gao/nba2k22-gm-engine`；当前配置 public，玩家已授权本次游戏数据公开发布。后续任务仍按其实际发布范围处理，模型不修改仓库可见性。SQLite ZIP 在 Release，不在 Git 中反复覆盖二进制。

本页建立时当前局为 `mc_haliburton_2021`，玩家最后只确认 2021 年 11 月，准确日期未知。线上批次为 `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`，采集 `2026-10-17T11:50:28.464724+00:00`，上传 `2026-10-17T11:53:08.959661+00:00`。这是历史定位记录；下一任务读取 latest 和玩家的新时间，不照抄本段执行。

## 7. 开发窗口收尾的维护规则

1. 新功能落地后更新本页的状态、实际入口、限制和证据；没有跑通不能标已实现。
2. 新来源更新 `config/source_catalog.json` 与文档 31；操作方式变化更新文档 27/32；架构/迁移变化更新文档 33。
3. 当前已取消单来源更新开发。任何来源新增后加入统一`full_verified_v1`，更新本状态表、source catalog、导出及GM覆盖标识；不得将分来源版本组合规则作为规划待办。
4. 玩家规则变更更新 gameplay_policy、文档 26/AGENTS 及涉及的基线段落；执行器变化同时更新文档 28/36 和下面的能力表。只更新相关内容，不复制整份聊天史。
5. 每次数据采集不重写本页的整套计数；它们留在 manifest/latest。只有能力或维护口径变化才更新基线。
6. 基线窗口没有自动刷新推送能力。玩家派生新任务后，模型重新读磁盘文件；不要声称旧聊天已经自动学会新提交。

首次教练来源生产采集与发布已完成。后续数据刷新仍需玩家明确触发，逐次使用新批次和审计结果。文档33第7节已取消单来源开发。此处不触发采集、发布、GM或游戏写入。

## 8. 执行基线能力表：可读、可写底层与已验收业务分别看待

本表区分源码审阅与实机结果。W02交易实验的崩溃、已确认人数遗漏与限定修复见文档37；即时内存回读不代表稳定业务验收。完整执行规程见文档36；加载基线不打开游戏进程。实际任务开始前再次检查相关源码和验证证据。

| 动作/层 | 当前实际入口与状态 | 执行时必须处理的边界 |
| --- | --- | --- |
| M3候选决策交接 | `gm_analysis.py` / `gm_decision.py`本地工程已实现；真实纯离线教练工件及描述性普通交易条款 | 无游戏句柄、无live plan/preflight、无执行权；所有终稿NOT_GRANTED/false。V4候选不自动替换V3，交易实时身份/容量计划和具体玩家批准继续独立触发 |
| 进程校准/原值读取 | `memory.py`、`address_calibrator.py` 已用于只读采集与审计 | 校准不证明当前 save_id 自动识别，也不证明写入权限/批准或业务写回已验收 |
| 底层内存写入 | `GameMemory(read_only=False)`、`write_bytes` 与数值 writer 存在；默认实例只读 | 仅检查调用/写入字节数，不提供方案批准、身份白名单、交易事务或完整恢复；部分 writer 会掩码截断，调用前须校验 |
| 历史 TEAM 策略 | `StrategyManager.set_team_strategy` 无条件拒绝；旧调用已清除 | `LEGACY_TEAM_POE_OFFSETS_REVOKED`；旧 poe_* 只保留原始观测，GM 不认作教练战术 |
| 原生主教练战术 | 当前分支批次 CLI；19项 GM 默认字段和5项只读 Sim；六 POE、五项滑块有分项实机证据，整体防守有独立 UI bulk 证据 | 依最新 V2 profile/字段矩阵逐项准入；BenchDepth不设测试样本上限，由GM根据阵容选人数；四Freelance使用完整原生目录与有序接口，直接UI测试未做；Tempo原生raw可写、界面含义未知；其他教练实际值作为实用参考，不强行映射UI。须 `--coach-editor-closed` 和具体独立批准；PR #1已合并main，代码可用于正式接入；仍须玩家批准具体批次 |
| 对手 Gameplan、防守和轮换 | 独立 codec，只读/排序/离线预设；本次870条 IsInUse全0 | MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED；禁止强行开启；防守/人物引用未开放写入 |
| 球票定价 | `StrategyManager.set_ticket_pricing` 有有限非负检查与浮点回读 | 仍需本次批准、当前球队身份与只改批准字段；不等于通用经营执行器已验收 |
| 新局全局设置/30 队票价模板 | `bootstrap_new_game.py --approve-game-writes` 有批准开关；调用 slider 与票价；旧战术跳过 | 不把票价成功说成战术已配置；不能借初始化入口应用单笔GM战术或顺带改全联盟 |
| 球员普通能力/倾向/性格/动作 | `modifier.py` 对相关 setter 主动 `PermissionError`；`growth_engine.py` 旧入口停用 | 当前玩法禁止普通改值。不可删除拒绝逻辑；专项历史重力还需独立实现与批准 |
| 交易控制开关 | `modifier.py` 有旧开关 writer | 静态偏移和业务效果未作为本次通用执行能力验收；开关不等于交易，不因交易批准自动修改 CPU 交易行为 |
| 批准普通球员交易 | `approved_trade_executor.py` v2 + `trade_request.py`；玩家已确认CHI/DET成功，有限范围启用 | 姓名/原队/目标队输入，歧义需face/DOB；只读固定身份/合同原值；常规/活动/双向人数和完整引用核验，失败停止，已有回执不重放。普通球员能力不改 |
| 签约执行/原合同替换 | `approved_signing_executor.py` 与 `execute_approved_signing.py` 候选源码已写；未运行/未测试，布局及写入闸门关闭 | 只接GM已确定的球员/球队/合同；不报价/择队/重做GM。31位薪资共享位、年限/选项编码和名单关联源码准备，非空FA专用关联待未来验证；见文档38 |
| 通用签约/裁员及其他布局 | 未验收 | 交易成功不认证签约、裁员、复杂依赖或原生交易日志；旧trade_engine仍停用 |
| 外部系统定案→合同写回 | 执行端不运行报价模拟；新增签约候选源码/CLI，实机验证按玩家以后具体签约触发 | GM负责合同/去向，Codex只负责核对/执行/回读；既有P1合成模拟不被执行入口依赖，真实写入仍关闭 |
| 合同/薪资调整 | 已有薪资/合同读取 profile，无完整验收的受控写入入口 | 批准金额不等于可直接写满 32 位；需保护 31 位薪资的共享标志与真实合同/汇总关联；不扩展复杂现实账本 |
| 简单选秀权转让 | 已纳入标准交易v2；本次3枚签重启后确认目标归属 | 精确8字节持有者，其余24字节保留；三届/签名/身份/当前持有者先核对，不清保护/交换元数据 |
| 员工岗位/雇佣变更 | 已验证员工与球队岗位双向读取；无完整写回验收 | 必须维护人员与球队岗位双向关联、处理职位占用，不只改单向指针 |
| 历史新秀装载 | 来源新秀筛选/排重可用；目标槽位注入未完整验收 | 目标需另校准，不能复制含指针的全结构到不同对象或不同进程 |
| 历史重力属性调整 | 玩家允许专项具体方案；受控执行器未完整实现 | 限批准人物/字段/原值/目标；禁止扩大到同名克隆或普通成长 |
| MC 成长故事 | DISABLED_DEFERRED | 本次新增执行基线不启用该玩法 |
| 批量执行/回执/幂等/恢复 | 标准交易CLI已有计划/固定身份/回读/逐写回执/防重放；签约源码待验证 | 只接受互不重叠球队的交易批次，同队依赖分开请求；失败停止，无自动回滚/事务原子性；原事故/回执保留 |

任何新执行器只有同时具备具体批准入口、当前对象核验、字段布局/写前条件、写后业务回读、失败/重复执行处理与实际验证证据，才能在表中改为已验收。实现后记录验证范围和版本；仅通过 mock/源码检查不能声称正式游戏已写入成功。
