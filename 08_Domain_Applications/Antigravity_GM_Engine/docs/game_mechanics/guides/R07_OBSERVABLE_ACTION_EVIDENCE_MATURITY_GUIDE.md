# DEV29 R07 — NBA2K22 游戏原生信息、可观察能力及可执行性最终研究矩阵

> 2026-10-21；`R07_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`。研究对象 NBA2K22 **PC本世代离线MyLEAGUE**。这是R01–R06研究完成并经过R06独立验收后的**研究知识整合**，不是DEV28实现、Codex执行、比赛推进、原生菜单测试或人格系统开发。本轮没有访问真实游戏进程、没有任何游戏写入；新实际采集与UI像素认证均为0。

**可读取性说明**：694项逐条索引现在采用[总入口清单](../catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)和**7份JSON分卷**，每卷94–100条；总入口只列分卷路径、计数与边界，不将超过连接器读取上限的巨型单文件当成可用交付。使用时必须依次读取`parts[].path`，不能只查总入口就误认缺少`items`。每卷同时保留`SRC-####`外部引文和`project_refs / original_research_source_refs_raw`项目/内部来源，未逐项核对的原文语义仍保持未认证。

本轮两份机读入口： [40组功能成熟度矩阵](../catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json) / [694条研究项可追溯索引](../catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)。之前已经由独立审核接受的正式R06研究状态为`R06_RESEARCH_CLOSED_WITH_PC22_NATIVE_RUNTIME_AND_PERSISTENCE_GAPS`；详见[验收报告](../../development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)。以下的40/694都是**不同抽象级别的研究计数，不是已认证游戏能力数字**。

## 一、R07的任务边界与业务问题

我们需要回答：① NBA2K22有哪些菜单和事实？② 哪些事实被游戏/已有项目实际读取？③ 哪些可以随完整批次发布并由GM查询？④ 哪些由已验证的受控执行器按玩家批准写入？⑤ 哪些仍停在同版资料、跨版参考或静态内存候选？

最终的多独立模型循环由**采集模型→分析模型→独立教练→独立球员→30队GM→用户批准后的执行模型**组成；Media可以是将来的角色，但不被R07擅自加入固定第七步。上述角色的偏好、人格、目标、价格/交易函数、要求、接受或拒绝逻辑、谈判及调度应当未来另立开发任务。本文列出的`potential_observers`是资料可能适用的视角，**不是实际角色ACL、已存在模型实例、游戏原生同意机制或允许写入的权限**。

## 二、严格独立的七个证据成熟度维度

| 维度 | 代表什么 | 不意味着什么 |
|---|---|---|
| 1. `mechanism_knowledge` | 有对应游戏研究描述，附适用平台/模式、来源或UNKNOWN | 游戏存在同名PC22按钮 |
| 2. `game_information_visibility` | PC22本世代对应界面真正显示该值、合法选项及刷新状态 | 找到游戏内存地址或项目已采集 |
| 3. `native_structure_or_locator` | 本项目静态Profile或真实逆向定位出对应原生布局/字段 | 当前存档内存槽安全、可读值一致或可写 |
| 4. `current_save_readback` | 当前实际加载存档、对象ID、进程、时间、目标字段来源的实时读回证据 | 已经同步进正式SQLite/JSON |
| 5. `batch_captured` | 本次已验收的`full_verified_v1`批次真实记录并与身份及审计绑定 | 后续每批、所有字段一直完整，或模型能直接查询 |
| 6. `model_queryable` | Web GM/分析或未来角色能用受支持的路径、标识与时间查询到该项目 | 游戏写入已获批、数据没有隐私/来源限制 |
| 7. `approved_write_and_postsave` | 该具体动作属于已验证执行器范围，得到现实玩家针对本次方案的批准，执行读回并单列Save持久化验证 | 模型提案、JSON里`approved=true`、字段地址存在或过去某笔交易成功即自动授权 |

**不能用累计成熟度分数或一个`done`来替代七个维度。** PC22原版同版玩家帖子、2K23次世代官方手册、项目Registry、当前源批次、GM查询、获批写入均属于不同证据类型。R07没有新逐项实机读回，因此逐项索引保守使用`NOT_PER_ITEM_VERIFIED_IN_R07`等状态；这并不否定项目已经在其他批次验证并发布的有限生产来源，后者单独列为有日期范围的历史证据。

## 三、资料溯源：如何实际从目录追到“这一项”

`R07_ITEM_TRACEABILITY_INDEX_V1.json`包含**694条异质研究记录**：12项R01逐场统计指南主题 + K04教练10项 + K06训练11项与健康8项 + R04原生档案109项、倾向99项、三动机/21个性参考/四动态概念 + R05原生员工13项与名单14项、经营数据54项与动作63项 + R06-A静态登记86项与菜单118项 + R06-B历史媒体31项 + R06-C赛季存档38项。索引以`origin.path + origin.array + origin.item_id`定位原目录，不复制游戏真实值，不生成伪偏移，不对前代资料追加PC22认证。

源引用已做**SOURCES编号存在性校验**，但没有逐篇重读全部外部网页以确认每条主张的语义匹配，因此每条`direct_source_support_verified_in_R07=false`。这是独立的证据质量缺口，不可把“编号存在”误读为来源直接支持。R06-B的十类奖项`sources=[]`保持不变，R06-C七个无直接证据项目仍待证。R01的12项是**指南主题手工锚点**，不是新发现的12个内存字段。

索引中的`native_field_key_candidate`只保留静态布局/原生标识线索，**不作为允许读写的现场地址**；历史球员重名、交易球队归属和Save generation必须重新确认。人员潜力、忠诚偏好、合同内部数据对媒体或非授权角色不天然公开。

## 四、40组能力成熟度：研究覆盖到何处

以下“既有证据范围”保留原文等级，不是当前存档即时状态；**能力读写的严格限定见JSON**。

| 组 | 功能主题 | 既有证据范围 | 当前实际执行层 |
|---|---|---|---|
| F01 | 赛程、对阵及GameID | UNKNOWN CURRENT SAVE | 未认证通用写入 |
| F02 | 逐场球员及球队Game Logs | NOT CAPTURED | 未认证通用写入 |
| F03 | 逐场双方Box与比赛细节 | NOT CAPTURED | 未认证通用写入 |
| F04 | 投篮图、热区及出手类型 | NOT CAPTURED | 未认证通用写入 |
| F05 | 球队赛季统计与战绩 | PRIOR FULL VERIFIED SNAPSHOT REPORTED | 未认证通用写入 |
| F06 | 球员赛季累计与每场指标 | PRIOR SEASON STATS REPORTED NOT ADVANCED ALL | 未认证通用写入 |
| F07 | 全球球员模型池及新秀身份 | PRIOR FULL VERIFIED SNAPSHOT REPORTED | 未认证通用写入 |
| F08 | 30队名单归属与人数核验 | PRIOR FULL VERIFIED SNAPSHOT REPORTED | 未认证通用写入 |
| F09 | 教练19项默认设置、POE与体系 | PRIOR CAPTURE AND PARTIAL REAL WRITEBACK REPORTED | COACH_FIELDS_SELECTIVE_APPROVAL_GATE |
| F10 | 整体防守与对手Gameplan | PROJECT OVERALL DEFENSE SCOPE REPORTED PER PLAYER UNKNOWN | 未认证通用写入 |
| F11 | Playbook、战术与Freelance | PROJECT PARTIAL TECHNICAL PROFILE | 未认证通用写入 |
| F12 | ACE及真实战术执行反馈 | ENGINE CAUSALITY UNKNOWN | 未认证通用写入 |
| F13 | 个人属性、耐久、潜力数据 | PARTIAL PRIOR PROFILE CAPTURE REPORTED | 未认证通用写入 |
| F14 | 球员倾向及个人PlayTypes | STATIC PROFILE NOT CURRENT CAPTURE | 未认证通用写入 |
| F15 | 球队/个人训练设置 | PROJECT STATIC REGISTERED NO R07 LIVE | 未认证通用写入 |
| F16 | 实时体力、疲劳及伤病 | NOT CAPTURED | 未认证通用写入 |
| F17 | 自然成长与退化历史 | GAME CONTROLS GROWTH NOT CAPTURED | 未认证通用写入 |
| F18 | Loyalty/财务偏好/人格徽章参考 | CROSS VERSION ARCHIVE NOT CURRENT SAVE | 未认证通用写入 |
| F19 | 合同条款、选项与Bird状态 | PRIOR CONTRACT SOURCE REPORTED PER FIELD UNCERTAIN | 未认证通用写入 |
| F20 | 球队薪资与市场可支出能力 | PROFILE CANDIDATES CAP ROOM NOT CERTIFIED | 未认证通用写入 |
| F21 | 自由市场与真实签约 | FA PLANNER SYNTHETIC ONLY | 未认证通用写入 |
| F22 | 普通球员交易与审批执行 | APPROVED TRADE V2 BOUNDED NATIVE EVIDENCE | BOUNDED_APPROVED_TRADE_V2 |
| F23 | 简单选秀权权属及V4规则 | PRIOR PICKS 300 READ REPORTED | 未认证通用写入 |
| F24 | Draft Class导入、轮回与真实选秀 | DRAFT POOL PARTIAL NO CURRENT DRAFT COMPLETION | 未认证通用写入 |
| F25 | Scouting、Mock Draft及不完全信息 | REPORT VS TRUE POTENTIAL UNVERIFIED | 未认证通用写入 |
| F26 | 员工、职位、薪资及雇聘 | PRIOR STAFF SOURCE REPORTED | 未认证通用写入 |
| F27 | Setup、Game Speed与世界设置 | STATIC REGISTRY 86 CANDIDATES | 未认证通用写入 |
| F28 | 日历Simulation引擎设置 | MENU CONCEPTS NOT RUNTIME | 未认证通用写入 |
| F29 | 3D Gameplay与USER/CPU滑块 | MENU CONCEPTS NOT RUNTIME | 未认证通用写入 |
| F30 | Normalize Stats/Minutes与统计冲突 | TWO MENU CONCEPTS ONE PARTIAL PROFILE | 未认证通用写入 |
| F31 | 3D、SimCast、QuickSim模式事实 | MODE MARKER NOT CAPTURED | 未认证通用写入 |
| F32 | 游戏时间、阶段、数据批次身份 | PROJECT DATE INPUT READBACK UNCERTAIN | 未认证通用写入 |
| F33 | 奖项、名人堂与历届获奖者 | PARTIAL MENU PLAYER REPORT TEN AWARDS UNSOURCED | 未认证通用写入 |
| F34 | NBA纪录、生涯纪录及队史 | CROSS VERSION REFERENCE | 未认证通用写入 |
| F35 | 社交媒体、实力榜和新闻 | PC22 MOD TEXT INDIRECT ONLY | 未认证通用写入 |
| F36 | League Rule Changes与生效规则 | OLD SERIES MENU REFERENCE | 未认证通用写入 |
| F37 | Save、Autosave、重载和SteamCloud | SAVE AS PLAYER REPORT NO RELOAD TEST | 未认证通用写入 |
| F38 | 历史比赛、交易、选秀跨年留存 | NOT CAPTURED | 未认证通用写入 |
| F39 | 外挂全量采集/SQLite/发布与重发 | PRIOR FULL CAPTURE AND PUBLICATION REPORTED | 未认证通用写入 |
| F40 | 三套时间轴、历史参考和历史重力 | EXTERNAL POLICY NOT NATIVE 2K23 ERAS | 未认证通用写入 |

每组保留：`reference_anchors`(原研究文件/数组/ID)、`subject_group`、`potential_observers_not_authorized_permissions`、`observation_or_setting_refresh_context`、7维成熟度、`existing_execution_scope`、`unknown_and_handoff_gaps`。40组共**86处目录锚点**，提交前核对都指向真实已存在项目。时间字段仅为待核的“可能发生/刷新窗口”，绝不伪称PC22正式已认证触发器。

## 五、已存在的项目生产能力：历史证据与研究候选不能互换

这部分依赖[开发基线现状](../../34_BASELINE_CURRENT_STATE.md)、[交易正式执行手册](../../37_APPROVED_TRADE_EXECUTOR.md)、[签约执行范围](../../38_APPROVED_SIGNING_EXECUTION.md)、[教练批次执行手册](../../40_COACHING_EXECUTION_RUNBOOK.md)和[全量采集规程](../../27_DATA_WINDOW_RUNBOOK.md)。以下为仓库**既有工程证据**，R07本次未重新运行游戏或采集程序；示例数量均属其历史证据批次，不是2026-10-21最新存档内实时值。

| 编号 | 能力 | 既有来源与发布证据 | 写入能力或限制 |
|---|---|---|---|
| REAL-01 | 全局模型池与历史新秀 | FULL_VERIFIED_V1_SNAPSHOT_REPORTED | NONE_FROM_RESEARCH |
| REAL-02 | 30队阵容与球员合同信息 | FULL_VERIFIED_V1_SNAPSHOT_REPORTED | NORMAL_PLAYER_RATINGS_WRITE_FORBIDDEN |
| REAL-03 | 球队与球员赛季累计统计 | FULL_VERIFIED_V1_SNAPSHOT_REPORTED | NONE |
| REAL-04 | Staff岗位与球队关联 | FULL_VERIFIED_V1_SOURCE_REPORTED | STAFF_HIRE_FIRE_NOT_VALIDATED |
| REAL-05 | 简化选秀权资产 | FULL_VERIFIED_V1_SOURCE_REPORTED | APPROVED_SIMPLE_PICKS_BOUNDED_V2_WITH_OLD_PLUS3_CODE_GAP |
| REAL-06 | 原生教练战术默认值与对手防守 | FULL_VERIFIED_V1_COACH_SOURCE_REPORTED | SELECTIVE_APPROVED_COACH_SETTINGS_WITH_READBACK |
| REAL-07 | 已批准普通交易执行器 | VERIFY_PHASE_SEPARATE_READ_ONLY | HUMAN_SPECIFIC_APPROVAL_REQUIRED |
| REAL-08 | 自由市场竞价模拟与签约写入 | REAL_OFFSEASON_DATA_NOT_VERIFIED | REAL_SIGNING_WRITE_DISABLED |
| REAL-09 | 游戏Save、GameDate、逐场日志、健康历史 | NO_R07_CURRENT_SAVE_CAPTURE | NONE |
| REAL-10 | 完整同批数据更新与网页来源 | PRODUCTION_FULL_VERIFIED_REPORTED | NO_GAME_MEMORY_WRITE_FROM_CAPTURE |

具体必须分开的事实：
- 旧基线例子：**全球球员池3383、历史候选789、30队大名单466、球队赛季统计30队、球员赛季统计389、Staff 1470槽/1458姓名/240关联、未来选秀权300**。这些只是基线所记录的历史验收批次规模，不证明本局实时总数不变、全部扩展字段可用或逐场Game Logs已采。
- 本项目教练19项默认原生设置（其中14项有既有实机写回证据）、18项指定对手球队整体防守维度等已有部分原生技术基础；球员个人防守、五项只读`Sim*`、Tempo原生raw与3D效果不可泛化为同一已证完整可写控制能力。
- **批准普通球员/简单选秀权交易**有CHI/DET成功的人为验收，`ownership_transfer_v2`仍受身份、人数、交易容量、同一批次交互和旧`+3`守卫约束。取消世界三届限制的V4项目政策不是已完成执行器支持。
- **自由市场竞价模拟**已有研究和离线算法；真实2K22休赛期自由球员来源、原生合同写入和跨年持久验证尚未完成，不能称生产签约系统已经可用。
- 当前游戏**全量更新只能走玩家独立触发的`full_verified_v1`**，同批覆盖已验证来源；没有单来源新生产采集或自动推进赛季。研究完成不构成采集、上传、交易或修改球员的触发。

## 六、对四类未来游戏主体，究竟有哪些可以观察的原料？

| 未来观察视角 | 可能使用的已研究事实类别 | 主要证据缺口 | 禁止直接推断 |
|---|---|---|---|
| GM | 名单、合同、预算、Staff、交易资产、赛季/逐场比赛、教练及新秀历史 | 真实可支出工资帽、自由市场原生执行、阶段、历史保留 | “这个队应该卖掉核心”或“全部30队按同一算法经营” |
| Coach | 球员技术与体力、战术、对手防守设置、逐场胜负和模式专属结果 | 真实逐场Box、当场3D对位效果、训练/伤病值、个人防守源 | “现有手册写着联动，所以某套战术一定提高胜率” |
| Player | 自身合同、出场表现、伤病/训练状态、奖项历史，以及合法公开的球队事件 | 当前个人职业偏好、角色私有记忆、跨赛季成长/历史 | “忠诚度高的人必须留队”或“球员一定同意/拒绝” |
| Media | 官方公布的赛果、球队/球员公开统计、已确认的交易和奖项、公共消息 | 游戏原版Social/历史新闻动态和公私边界 | 读取隐藏Potential/内部报价，或把模拟选秀观点写成真实签约/选秀 |

这里的“可能使用”是未来模型需要的**信息清单和披露边界研究**，不是当前运行中的Coach/Player/Media人格或权限代码，也不承诺所有信息已经有独立角色读取接口。

## 七、八项P0缺口如何转成将来可验证的输入条件

| 缺口 | 当前真实问题 | 所需最小实机证据（仅未来获批后） |
|---|---|---|
| D06-G01 | 没有完整逐场Game Logs、双方Box和真实Shot数据 | 同档同GameID场次、双方人员、页签和逐场回读，区别赛季累计 |
| D06-G02 | 无法把3D、SimCast、Quick Sim统计自动可靠打模式标签 | 同比赛来源模式和对应比分/原生赛后页，分USER/CPU |
| D06-G03 | Normalize Minutes与Stats被混成一个候选设置 | 原版UI两开关、原值与保存后读回、同GameID差异 |
| D06-G04 | 原生GameDate/Phase与batch可能不同步 | 当前真实存档ID、游戏日期、阶段、source manifest及批次 |
| D06-G05 | Save/Save As/Autosave持久化未证 | 获准测试档退出和重新进入后的日期/身份/合同/比分 |
| D06-G06 | 历史Draft加载、名单身份与轮回触发未证 | 1984–2020选秀类实际导入/完成节点及当前球员ID |
| D06-G07 | 休赛期原生AI会改变合同/名单，安全切入点未知 | 同档获批测试阶段前后原生合同/名单与AI变化 |
| D06-G08 | 选秀权政策V4与旧+3执行器冲突 | 未来独立Codex批准后才可更新校验/测试，不新增固定五年世界限额 |

额外P1/P2共12项涉及战术因果、健康、Staff、历史奖项/纪录、媒体、财务、规则变更和云同步，完整见机读目录。**P0/P1/P2是研究证据重要度，不是开发授权、优先级承诺或工程任务排期。**

## 八、R07自检边界与正式交接

- 研究项694条、功能族40组、功能族锚点86处、已知既有生产能力范围10条、已继承的D06缺口20条。不存在唯一的“总原生字段数”可以从这些异质分类直接相加计算。
- 本轮只做源目录静态交叉读取和语义审计，没有增加新的已验证PC22原版菜单、新实时读回、新发布游戏批次、获准写入、合法取值范围或存盘实测。
- 原R06的**研究结案**独立审查已经通过；R07只是**发布待独立审核**。审阅后可将[DEV28交接资料](../R07_TO_DEV28_EVIDENCE_HANDOFF.md)交给后续独立任务，但**FINAL-CODEX以及DEV28代码启动仍需用户明确独立触发**。
- 任何普通经营球员属性/潜力/Badge直接改值继续禁止，历史线的特殊例外必须单独提出具体方案并获玩家批准。任何JSON内`approved`标记均不能代替玩家当次批准。


## R07独立审核后的目录字段定义修正（2026-10-21）

[独立审核](../../development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)发现的A/B问题已修复，参见[定向修复回执](../../development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)。

**指南主题ID**：R01中全部12项`manual_research_topics`均是R07研究者整理的Markdown指南检索主题，而不是原R01 JSON机器记录；`R07.0007/K02.SHOT_ZONES`指向原文第4节`K02.SHOT_CHART / SHOT_ZONES`及`Shot Zones Aggregates`，`R07.0010/K02.PER36`指向第3节`K02.PER_GAME_PER36_ADVANCED`及`Per 36 Minutes`。两个完整`K02.`别名在原文中并未字面出现。

**查询成熟度**：F21/F22/F23/F26/F27/F32/F39/F40的`model_query_api_status`现在只描述数据查询证据，不再容纳写入许可、旧+3交易限制、存档身份、审批或历史重力。原始八种提示仍通过各`*_warning`、`query_prerequisites`、`existing_execution_scope`及`reviewed_old_query_value`保留。真实GameDate不因批次存在而获证；第五届Pick能读不意味着能交易。研究成果依旧不能新增游戏执行权限。

**当前研究状态**：`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`，尚待独立复验，不自行关闭DEV29。
