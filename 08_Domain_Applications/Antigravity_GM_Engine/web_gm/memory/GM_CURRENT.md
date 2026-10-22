# Web GPT · GM 基线当前记忆

## 2026-10-21 权威运行流程：GM是六阶段中的第五个独立模型

玩家明确每轮**①采集②数据分析③独立教练④独立球员⑤GM⑥汇总执行**，通常赛季开始/月度/交易截止前一天/季后赛每轮/休赛期运行。Coach、Player人格系统尚未开发，目前已有主要GM人格系统。**GM收到教练和球员模型提出的要求后进行独立经营和权衡，不能由DEV29研究文档的8个例子替教练/球员写人格规则**。人格、谈判和跨主体博弈另立未来开发任务；DEV29只研究真实2K22/2K20–23的游戏数据、设置、菜单、机制及可操作选项，DEV28只负责提供可读取/经玩家批准可写的技术原料。见[六阶段与研究边界](../../docs/game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)。R04研究结案，R05下一轮；没有上线新角色系统。

## 2026-10-20 DEV29 V3：GM是自主参与者而非全联盟最优优化器

玩家将最终目标调整为**多个具有独立目标、偏好、信息、记忆与选择/拒绝/谈判权的GM、教练、球员、媒体角色共同游戏并根据NBA2K22原生比赛反馈涌现**。单GM不应单方面替球员决定其倾向/训练，不应因篮球哲学模型推断的所谓最优收益强制角色接受所有交易；应让模型按角色利益自主选择，保留合同与资产约束、多人独立双边谈判、已批准真实游戏写入及原生比赛裁决。

[DEV29 V3](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)、[R04球员全量原料研究](../../docs/development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)已经纳入研究计划；R01完成、R02 NEXT，R03训练，R04球员个体身份/属性/倾向/徽章/耐久/健康、Play for Win/Financial Security/Loyalty与独立Agent授权，R05市场，R06世界与媒体，R07共用矩阵，FINAL-CODEX后置。长程偏好与关系应由外部SQLite保存，原生字段首要服务真实2K场上/合同机制。Agent同意不等于玩家游戏写入批准；不允许普通球员能力/潜力/徽章直接改值。此变更仅研究规划，不是已上线新Player Agent。

## 2026-10-20 DEV29 V2网页GPT游戏机制资料库与决策基础

- GM后续应以[docs/game_mechanics游戏机制资料库](../../docs/game_mechanics/README.md)和[DEV29 V2](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)作为长程知识入口：新网页GPT按R01–R06多轮整理NBA2K20–23/MyLEAGUE/MyNBA/次世代有价值的菜单、赛场/经营机制、攻略、截图证据及相互作用，全部写GitHub；Codex最终才做目录/工程能力对应。旧DEV29 V1中由Codex先行R0-C已被V2更改。正式GM仍不得把赛季合计当具体逐场证据，数据缺口`INSUFFICIENT_EVIDENCE`。本次只是资料库骨架，不是已完成攻略或已有新比赛来源。

## 2026-10-20 DEV29先于DEV28：全系列游戏玩法知识与GM证据需求基线

- 玩家指出现有全量采集遗漏**真实逐场赛程/Box Score/Game Logs/部分高阶统计**，导致GM难以从真实比赛理解人才不足、角色错误和战术效果。已有M02季累计及跨批差值不等于逐场比赛事实；GM不能在缺每场证据时断言某球员在特定对手/具体回合为何失效，允许证据不足的HOLD/研究结论。
- 权威前置任务：[DEV29 NBA2K20–23终极联盟机制、完整数据/操作目录与GM需求审计](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V1.md)。执行顺序为PR#12收尾→DEV29 R0-A/B/C→DEV28；不是现在启动研究或游戏写入。网页GM负责给出每月/季后赛/休赛期决定对应**最低需要哪些比赛、球员和战术事实**，并从已认证可选项目录选择，不再由少数已解偏移定义全部经营能力。
- 跨游戏2K20/21/22/23和次世代MyNBA的公开玩法/社区与官方资料可帮助理解管理逻辑；唯独目标NBA2K22 PC菜单与内存必须本机核对。研究产物应是所有GM窗口可复用的机制地图、机器可读菜单/数据覆盖台账与证据要求，而不只是长篇攻略。

## 2026-10-18 W03/R04：第三组C已完成，30队研究阶段结束（阶段候选未批准）

- `career_id=mc_haliburton_2021`; `game_date=2021-12-12`（玩家确认、非月结）；`source_batch_id=2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`仍是最新同一M02基准，没有新比赛或日期推进。
- **刚完成R04组C10队157条完整当期名单、5项教练业务候选、5队HOLD**，均按两批球队实际新增比赛2P/3P/eFG/得失分与当前原生教练19项定位。教练候选：`GM-W03-R04-DET-C01` POEDefense14→13（对手2P60.32%/3P42.13%）；`GM-W03-R04-OKC-C01` POEDefense14→13（对手2P59.13%）；`GM-W03-R04-SAS-C01` POEOffense5→4（自家3P27.39%、净负17）；`GM-W03-R04-MIN-C01` POEDefense14→13（对手2P55.2%）；`GM-W03-R04-CHA-C01` POEDefense14→15（对手3P41.96%）。TOR/HOU/PHX/POR/GSW均有比赛证据支持当前HOLD，**不是随机平均分配战术变更**。
- [第三组完整报告](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R04_GROUP_C_METRIC_FIRST_REPORT.md)、[机器C1](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R04_GROUP_C1_METRIC_FIRST.json)、[机器C2](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R04_GROUP_C2_METRIC_FIRST.json)、[R04回顾](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R04_RECAP.md)均已发布GitHub并经过写后核验；[联盟全30队研究索引](../seasons/2021-2022/windows/W03_GM_20261018/ALL_30_TEAMS_RESEARCH_INDEX.md)、[进度表](../seasons/2021-2022/windows/W03_GM_20261018/TEAM_REVIEW_TRACKER.json)也已更新。
- **深度审查30/30队，466条当期名单（A157+B152+C157）**，三组共有15条**阶段战术候选**，没有人事/交易/教练正式执行授权；旧CHA/SAS Poeltl↔P.J.Washington+2024 NOP二轮还须在R05独立两方重新估价，不能视为成交。
- **下一步等待用户触发`W03/R05`**：全联盟球队间资产与诉求比较、战术候选撤销/保留及风险复核、真实双边报价和排他冲突检查；R06才提交唯一GM终稿和教练真实native batch执行审批材料。不要提前进入R05、不要新开赛季、不要执行游戏。员工池和全球员SQLite访问技术债按玩家要求最终决策后解决；不追求空泛球队哲学、训练或个人分钟锁定。
- `game_write_approved=false`; `W03_R04=NOT_APPROVED_NOT_EXECUTED`; `native_batch_digest=null`.

## 2026-10-18 W03/R03：B组10队比赛数据驱动战术研判已完成

**玩家最新强调**：不要从当前阵容拼凑无篮球理论根基的“赢球文化/哲学”，不要浪费时间重复套模板；**必须用比赛动态数据（尤其两批累计的真正增量投篮/攻防）和玩家实际阵容属性来调整教练原生字段，以实际胜场/可观测得失分为目标**。员工池大JSON与球员池SQLite的可靠读取问题必须解决，但**安排在这次30队决策及终稿完成之后**；此节点员工分析暂缓（`STAFF_DEFERRED_BY_PLAYER`），不阻塞对每队15人左右的现有可读名单、教练19项及交易的研究。已将此权威新规则同步[SOP](../GM_DECISION_SOP.md)、[经营标准](../manuals/GM_DATA_TO_DECISION_STANDARD_V1.md)、[五轮制](../GM_DECISION_ROUNDS_V3.md)与[球队结构合同](../schemas/GM_TEAM_DECISION_CONTRACT_V1.json)；往后不再把空泛`winning_philosophy`当完成条件，使用`decision_objective`与可复盘KPI。

- `last_completed_round=W03/R03`，`career_id=mc_haliburton_2021`，`game_date=2021-12-12`，`source_batch=2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，区间M01→M02，来源未改变。
- 已完成**组B10队、152条完整当前大名单记录**，附每队真实区间得失分、2P/3P/eFG与对手对应数据，以及旧同队同姓名同slot可核对的球员两批差分，转队对象标记不可归因。 [完整人读报告](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R03_GROUP_B_METRIC_FIRST_REPORT.md)、[B1机器数据](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R03_GROUP_B1_METRIC_FIRST.json)、[B2机器数据](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R03_GROUP_B2_METRIC_FIRST.json)、[R03完成回顾](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R03_RECAP.md)均已写入GitHub。
- **战术5条（待R05/R06重新评估，绝未获执行批准）**：`GM-W03-R03-NOP-C01` `POEDefense14→13`，对手近期两分60.4%；`GM-W03-R03-UTA-C01` `POEOffense5→4`，自身近期eFG51.99%且Conley/Gobert适合挡拆；`GM-W03-R03-ORL-C01` `POEOffense5→1`，自身近期三分28.02%；`GM-W03-R03-DAL-C01` `POEDefense14→15`，对手三分42.65%；`GM-W03-R03-DEN-C01` `POEDefense14→15`，对手三分43.15%。SAC/NYK/LAL/BKN/IND`COACHING_HOLD`。本轮根据数据**推翻原R01 DAL优先护框和NOP优先修改进攻的旧判断**；UTA缩小为仅一个字段。
- 目前**20/30队、309条本赛季当前大名单**已完成研究；[tracker](../seasons/2021-2022/windows/W03_GM_20261018/TEAM_REVIEW_TRACKER.json)现等待玩家继续`W03/R04`组C：DET/TOR/HOU/OKC/SAS/PHX/MIN/POR/GSW/CHA。R05进行联盟交易/战术冲突综合，R06唯一终稿并准备真正教练执行器包。
- **安全状态**：员工暂未评估，全局球员池和staff.json未成功大文件打开的技术债未解决，不声称已遍历数据库；仅从每队源JSON得到所有当前阵容与球员能力。所有战术目前是篮球意图`PROPOSED_ONLY`，本轮未更改游戏、不批准Codex执行、不假造digest。玩家在后续具体批准之后委托执行模型写入，并亲自进入游戏观察是否有效。


## 2026-10-18 W03/R02：A组10队深度研究已完成（157球员，未执行）

玩家在同一个M02决策节点明确继续执行V3五轮以上GM流程，且确认**已验收功能可以形成具体执行方案，不需要在执行前额外验证战术能提高胜率；由Codex执行、玩家实际入游戏观察和后续采集形成反馈**。此话不是批准任何具体教练/交易变更，旧审批和原生执行闸门继续适用。

- `node=GM-S2021-2022-W03` / `last_completed_round=W03-R02`；`source_batch=2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，2021-12-12（玩家确认，非月结）。同批主教练与球员/战绩/选秀权已核对。
- **已完成第一组A：PHI/MIL/WAS/CHI/CLE/BOS/LAC/MEM/ATL/MIA共10队、157/157条大名单球员评估**，全部含六维STAFF/TACTICS/ROSTER_USE/MARKET/ASSETS_AND_DEVELOPMENT/TEAM_IDENTITY_AND_MONITORING、真实当季球员能力合同、角色互补、来源、不确定性及复盘方法。[详细人读报告](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R02_GROUP_A_TEAM_DOSSIERS.md)和[157球员机器JSON](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R02_GROUP_A_TEAM_DOSSIERS.json)已发布，随[R02回顾](../seasons/2021-2022/windows/W03_GM_20261018/ROUND_R02_RECAP.md)。[V3进度表](../seasons/2021-2022/windows/W03_GM_20261018/TEAM_REVIEW_TRACKER.json)：`deep_reviews_completed=10/30`。
- **本轮战术5项仅业务意图，未批准**：CLE、BOS、LAC各`POEDefense 14→15 LIMIT_PERIMETER_SHOTS`；ATL`POEDefense 14→13 PROTECT_PAINT`；MIA`ActiveSystem 2 PACE_AND_SPACE→7 DEFENSE`。PHI/MIL/WAS/CHI/MEM教练HOLD；十队现任主教练全部STAFF_HOLD。原R01 ATL→GSW对手OVERALL专项已降为R05复核候选，不提前推荐批量统一设置。原R01交易CHA/SAS需待组C和全局双方市场比较。
- **真实采集边界**：正式M02的`staff.json`源存在且staff_pool通过30队8岗位双向来源审计，但连接器对此2.7MB单文件返回空，本轮只从`coaching/teams.json`确认全部十位主教练身份。其他七岗位个人姓名和效用本会话未读取，不虚构、不申请具体雇佣/解雇；因均STAFF_HOLD且完整披露限制，篮球团队档案可标COMPLETE，涉及实际人员替换前必须重新核实身份、可用候选和员工双向安全写回。
- **新增经营深度**：CLE后场Sexton/Garland外防较弱而Allen/Mobley有护框；BOS双翼与Smart外防强但Kanter外防26；LAC Kawhi97/PG92外防；ATL Trae外防54而Capela内防86；MIA防守核心充足但本季净负2.23。PHI 20–6保持POST；MIL14–12/+9.35净胜不应急交易；WAS近期7–1、CHI新Grant、MEM新Brogdon都应保持并观察交易后的真实样本，不能把转队前赛季累计算成本队产出。
- **不产生执行授权**：教练还没有真实生成器`batch_digest`，未向玩家展示最终全部action_ids，Codex未收到批准执行指令；交易、人员、球员、教练、游戏均未写入，游戏日期未推进。**后续R03/R04各10队深度研究、R05全联盟双方交易和战术评审、R06唯一批准执行包**仍必须完成，不能因为R02已有五条详细目标就跳入执行。
- **下一次仅玩家继续后触发W03/R03组B**：NOP/UTA/SAC/NYK/LAL/ORL/DAL/BKN/DEN/IND；再R04组C；完成30/30再做全联盟谈判。


## 2026-10-18 GM六维数据驱动决策正式规范 + 历史人物定制移交开发

**玩家已批准本GM的完整闭环**：最新正式规范[GM_DATA_TO_DECISION_V1](../manuals/GM_DATA_TO_DECISION_STANDARD_V1.md)，每队的结构化档案约束[GM_TEAM_DECISION_CONTRACT_V1](../schemas/GM_TEAM_DECISION_CONTRACT_V1.json)；最新版[五轮以上V3](../GM_DECISION_ROUNDS_V3.md)必须用此六维内容标准验收所有10队/5队深度研究。

- **第一步数据**：对每支球队整个当前大名单逐人评估真实比赛累计与跨批表现（转队累计/本队表现分开）、55项实际技能、主要角色、互补/短板、实际AI分钟、薪资合同、潜力与自然成长机会；评价每队实际胜负、攻防及经确认统计，不能只写排行榜、冒称转队后的累计、混淆MC clone。
- **六维GM裁决**：D1 `STAFF`现任主教练/员工留用与更换价值；D2 `TACTICS`19项默认战术、关键对手18项防守；D3 `ROSTER_USE`内部分工/阵容/AI间接轮换；D4 `MARKET`两队各自独立交易/签约；D5 `ASSETS_AND_DEVELOPMENT`合同、未来3年简单选秀权及自然成长机会；D6 `TEAM_IDENTITY_AND_MONITORING`赢球哲学及下节点实测反馈。每队至少比较留任、内部调整与市场方案；全部30队审议完成后再跨队谈判和唯一终稿。
- **员工机制现实边界**：M02已认证staff_pool双向员工身份与30队×8岗位共240角色；仓库docs34记载雇佣/岗位**还没有完整写回验收**。当前不能将换帅/其他员工变化提交为可执行命令。NBA2K22次世代主机官方MySTAFF报道只作参考，不可把其17人四部门和能力增益当本PC局的证据。GM可提出`STAFF_CHANGE_RESEARCH_CANDIDATE`及数据缺口，对员工实际效益未知应`STAFF_HOLD`。合法的教练战术19+18是另一个成熟受控配置接口，并非更换教练本人。
- **历史线边界新分工**：GM通过球队独立赢球哲学/合理交易/签约/战术维护真实历史时代逻辑与本局现实竞争，**不负责对现有球员作属性/信息定制**。历史线“历史重力”例外由开发规划基线按[单独开发交接](../../docs/development_tasks/DEV_20261018_HISTORY_GRAVITY_GM_BOUNDARY_V1.md)设计，须明确历史依据、原值目标值、期限回滚与安全执行器；每项能力改动继续需要玩家单独授权，目前不可执行。普通球员属性成长仍交游戏AI。
- **规范状态**：本次只编写/链接规范，未启动W03/R02 10队深度GM、未进行历史线定制、没有对游戏采集/员工/交易/教练/球员的写入。W03/R01旧12项教练和CHA/SAS交易仍是未获批准的**浅层候选**，新V3要求R02组A开始逐队深究。
- **玩家旧限制继续**：训练与精确个人分钟不纳入外挂；不得编辑普通球员能力、潜力、徽章、倾向。估计胜率提升必须用有证据的方法，不能宣称教练员工固定+X%。


## 2026-10-18 玩家最高优先级：GM决策每节点至少5个深度回合（V3）

**玩家最新明确指令覆盖过去“一次30队初查后最多3轮终稿”的全部旧流程。** 当前权威文件：[GM_MIN_FIVE_ROUNDS_V3](../GM_DECISION_ROUNDS_V3.md)，以及已同步修订的[SOP](../GM_DECISION_SOP.md)、[GM角色指令](../GM_INSTRUCTIONS.md)、[GM赛季初始化基线](../baselines/GM_BASELINE.md)、[2021–22赛季INDEX](../seasons/2021-2022/INDEX.md)。

- **每个30队GM决策节点**：首先3个独立实质研究轮、每轮10队，逐队深入研究真实球队战力、55项能力核心、教练配置、阵容搭配、AI轮换、自然成长、合同/选秀权、市场双方独立诉求，逐队写有据可追的`HOLD/PROPOSED`与其他备选并GitHub归档。**30队全部输出并形成索引后，至少2个独立回合**分别完成30队跨队冲突/双边谈判和唯一最终决策+可批准执行包，总计至少**5轮，没有最大轮数上限**。
- **深度不足时**改为每轮5队，则先6轮完成30队，之后仍至少2轮，总计**至少8个实质轮**；不能把已有30队一行摘要算作有效深入研究。
- M02当前`W03/R01`此前已保存了全30队浅层总览、12项教练意图和1笔CHA/SAS交易候选，但只作`PRELIMINARY_SCAN_SUPERSEDED_FOR_FINAL_DECISION`及历史参考，**没有执行授权，候选必须重新论证**；它不占用V3的3个深度轮。
- **目前下一个待玩家触发轮次为`W03/R02`组A10队**：PHI/MIL/WAS/CHI/CLE/BOS/LAC/MEM/ATL/MIA；之后R03组B NOP/UTA/SAC/NYK/LAL/ORL/DAL/BKN/DEN/IND；R04组C DET/TOR/HOU/OKC/SAS/PHX/MIN/POR/GSW/CHA。R05整合30队与双边谈判，R06唯一终稿及执行准备；如果5队模式依次延长至R09。
- **不可抢先执行**：R01中类似`GM-W03-T01`的双方意图尚需完整深度研究+重新独立估值，不可视为最终双方共识。教练方案经全队复核后还需程序生成真正native batch与摘要、玩家逐项审批，再由Codex执行；不能捏造`batch_digest`。这份规则更改未推进NBA2K22存档、未重新采集、未授权任何交易/教练写入。
- 所有回合由玩家明确触发并在结束时同步GitHub，30队完全审议前不能跳入正式全联盟执行阶段。训练交游戏AI、个人分钟精调不追求、普通球员能力/徽章/倾向不可直接编辑的限制保持不变。


## 2026-10-18 M02正式GM经营节点已形成W03/R01提案（未获玩家批准）

当前正式生产源已由M01推进到**M02**：`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`（`game_date=2021-12-12`，玩家确认，非游戏自动发现；`month_closed=false`；审计`PASS_VERIFIED`；`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`）。网页分析M02 V2已发布并可作为启发式输入；其中source_refs某些链接多了一层`published/`，而攻防诊断模板化，GM独立读取原始来源验证关键事实。

正式GM W03/R01已有完整30队提案及教练/交易意图：
- [正式30队经营提案](../decisions/mc_haliburton_2021/20261018_M02_W03_R01_GM_PROPOSED.md)
- [12项教练及1项交易结构化意图](../decisions/mc_haliburton_2021/20261018_M02_W03_R01_GM_INTENT.json)
- `decision_id=GM-20261018-W03-R01`、`version=1`，状态**PROPOSED_AWAITING_PLAYER_APPROVAL**，未批准、未生成可执行教练`batch_digest`、未发生游戏写入。
- 战术意图12项：ATL（含针对GSW），DAL，MIA，UTA，ORL，TOR，OKC，DET，NOP，LAC，GSW，具体raw/风险以正式提案为准；其余球队有理由HOLD或交易讨论。唯一外部双边交易意图`GM-W03-T01`：CHA取得SAS的Jakob Poeltl；SAS取得CHA的P.J. Washington及CHA现持有的2024 NOP原始二轮`draft_pick:2024:2:11`。该签位在M02确实由CHA(id31)持有，双方各15条名单；**只是GM外部理性共识，不是玩家批准**。
- 特别重要：MC的Tyrese Haliburton（`pool_slot=1235`）现位于IND，但个人赛季累计包括此前SAC经历，不能用其1577分除IND整季累计3208分解释“入队后贡献率”；另一`Ty Hali` slot184并非可合并永久身份。
- 玩家最新V3已更改为每节点至少5轮：W03/R01是浅层候选，下一回合R02做组A10队深度研究；R03组B、R04组C、R05全联盟谈判、R06终稿。旧三轮上限失效。所有原生教练批次必须经确定性脚本生成，用户额外核实完整`action_ids`及`batch_digest`才授权。
- 当前教练/交易申请均处于待审批阶段，严禁因发表GitHub提案自行改游戏。下一轮只在玩家继续本赛季GM谈判时触发。


DEV07 V2 技术验收历史补充（首次正式生产来源现已由M02完成；本段其他旧时点描述仅保留作历史）：见[教练操作手册](../manuals/GM_COACHING_OPERATIONS.md)。新范围为 19 项球队默认设置、指定对手整体防守、30 队批准绑定批次及同会话来源；五项 Sim 禁止 GM 操作。PR #1已于2026-10-18合并main（2509b3b）并同步本地，首次生产采集/发布未运行；六默认 POE 沿用既有验证，整体防守新增 PHI→IND 14 条 UI 等价批量写入/显示/恢复证据，五数值设置、双体系与命名手册现也通过分项门槛，14项有实机写回证据，四Freelance依原生完整目录/有序codec提供受控接口，加上玩家明确开放的原生Tempo共19项；Tempo界面含义仍未知，参考同局教练实际值，不声称其为已验证的进攻节奏，BenchDepth不再设置9–10测试白名单，GM按阵容决定人数。未运行新的 GM 轮次、正式存档执行或数据发布，不改变以下已归档赛季决定。

- role: `WEB_GPT_GM`
- memory_version: 22
- gm_chat_scope: `ONE_CHAT_PER_GAME_SEASON_V1`（本赛季持续使用一个 GM 决策聊天；月度 Wxx 为节点归档，不要求另开聊天）
- updated_real_world: `2026-10-18`
- current_game_season: `2021-2022`
- current_career: `mc_haliburton_2021`
- current_window: `GM-S2021-2022-W03` / `R04`（三组30队/466条完成，下一轮R05待玩家触发）
- last_game_month_hint: `2021-12 / M02`（2021-12-12玩家确认，非月结）
- last_game_date_exact: `2021-12-12`（PLAYER_CONFIRMED）
- month_closed: false
- last_snapshot_batch: `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`
- last_snapshot_data_updated_at: `2026-10-18T12:12:13.170996+00:00`
- last_gm_decision_id: `GM-S2021-2022-W03/R04`（C组10队数据驱动经营档案已归档，无执行批准）
- approved_actions: W01 `GM-A01..GM-A07`（限战略/研究）；W02 `GM-W02-A01`、`GM-W02-R02-A01` 玩家批准且于2026-10-17报告已在游戏中成功落地
- current_game_change_decision: `W02_A01_GRANT_PLAYER_CONFIRMED_EXECUTED`; `W02_R02_A01_NWABA_PLAYER_CONFIRMED_EXECUTED`; `W02_A02_TURNER_NO_DEAL`; 两笔交易后的部分球员归属已在M02新快照观察；`W03_R01=PROPOSED_NOT_APPROVED`
- game_write_approved: false (W03本轮无游戏写入批准；W02过去两笔交易曾获分别批准并已完成，不构成新权限)
- gm_game_write_executed: `W02_TWO_TRADES_PLAYER_REPORTED_COMPLETED_2026-10-17_AND_M02_ROSTER_OBSERVED`; `W03_R01_NO_EXECUTION`

## 2026-10-18 玩家确认：游戏AI会覆盖精细分钟分配；GM不再寻求精确个人分钟控制

- **用户实机观察**：游戏AI会频繁重置并重新分配各球员上场分钟，外部细化修改易被复写；未来也不强求解决。此为用户认可的**长期设计边界**，不是未完成研发任务。
- **GM应做**：使用已认证的`BenchDepth`（轮换人数上限）、`BenchUtilization`（替补使用倾向）与教练攻防体系间接影响球员实际获得的时间；根据后续赛季真实`minutes_per_game`、健康状态（如果来源可用）、比赛绩效和成长观察，提出球队整体轮换取舍、阵容搭配与打法建议。
- **GM不应做**：不向Codex交付任何`player_id/minutes_before/minutes_after`精确分钟调整、分钟锁定、周期补写或与AI重置对抗的任务；**不再将`PLAYER_MINUTES_EXECUTION_UNAVAILABLE`列为待实现功能**，不在后续GM工作中因无法精调分钟而卡住。即使当前教练设置间接影响分钟，也不能保证某球员具体上场数值。
- 与“训练全交游戏AI、GM不参与”和“教练会影响游戏自然成长”的玩家规则同时生效；普通能力/倾向等不允许外挂直接编辑。本节点未触发新的采集、比赛、经营决策或游戏写入。
- 对应最新版[教练手册](../manuals/GM_COACHING_OPERATIONS.md)、[GM SOP](../GM_DECISION_SOP.md)、[GM基线](../baselines/GM_BASELINE.md)和[GM说明](../GM_INSTRUCTIONS.md)已一并修订。后续窗口以这一段覆盖历史有关“精确分钟待接口确认”的旧记忆。

## 2026-10-18 最新玩家明确规则：训练退出GM范围，教练影响自然成长，内部调配优先于只寻求交易

**最新指令优先于过去有关训练研究的任何历史文字**。

1. **训练**：外挂尚未引入训练机制。游戏训练交由NBA2K22 AI完整负责；GM不管理、不研究、不提出训练策略、不要求补齐训练源、不让Codex开发训练接口，除非玩家未来明确重新启用。
2. **教练与成长**：玩家和其他人类玩家在大量终极联盟赛季实战中观察到，教练机制会直接影响比赛结果，也会影响球员在游戏引擎控制下的**自然属性/倾向成长走势**。此为项目GM采用的经验性运营前提，而非能推导任何教练raw值具体成长幅度的公式。GM应围绕体系适配和合理出场角色创造更好的赢球与发展环境。**不通过外挂直接编辑普通球员属性、潜力、倾向、徽章**；这些自然变化归游戏AI。
3. **GM四项并行经营杠杆**：阵容搭配与首发/替补角色、上场时间及轮换负荷、教练默认19项/指定对手整体防守18项、必须时的交易签约。不再默认“球队问题=找交易”，先看现有人能否通过更好的使用方式改善，同时比较交易资产成本。对30队逐队给具体调配/教练建议或有理由HOLD。
4. **上场时间实施边界（更新）**：游戏AI持续调整并覆写逐人分钟，用户明确放弃追求精确个人分钟；`BenchDepth`和`BenchUtilization`只间接影响实际轮换。球员赛季场均分钟用于观察分析，不设可执行的个人分钟指令，不列开发待办。
5. **风险与证据**：阵容与教练强度兼顾健康、体力、胜率和自然成长。没有本局伤病/疲劳数据不得假称某参数提升了X%的伤病概率。次世代MyNBA公开资料只是参考，不能代替PC/MC实测。教练自然成长的多赛季经验不等于获得训练管理权限。
6. **操作**：优先读[GM教练手册](../manuals/GM_COACHING_OPERATIONS.md)、[GM SOP](../GM_DECISION_SOP.md)、[GM初始化基线](../baselines/GM_BASELINE.md)和[GM职责](../GM_INSTRUCTIONS.md)的最新文本。具体教练值仍须在玩家下次正式采集后取得同批`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`来源，通过程序生成动作和digest，玩家审批后由Codex执行。不能擅自新开GM回合、游戏采集或修改游戏。

此条是规则/认知升级，没有新的比赛、执行批次或训练操作。

## 2026-10-18 GM新经营机制正式加载（以main上的GM手册/执行规程为权威，非新GM决策）

本节基于玩家请求对main分支的正式机制再次核实。核对资料：
- [GM教练手册](../manuals/GM_COACHING_OPERATIONS.md)
- [教练执行手册](../../docs/40_COACHING_EXECUTION_RUNBOOK.md)
- [交易执行器](../../docs/37_APPROVED_TRADE_EXECUTOR.md)
- [签约执行](../../docs/38_APPROVED_SIGNING_EXECUTION.md)
- [能力状态表](../../docs/34_BASELINE_CURRENT_STATE.md)
- [休赛期P0研究](../../docs/development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md)
- [休赛期P1源码](../../docs/development_reviews/DEV_20261017_04_OFFSEASON_FA_P1_IMPLEMENTATION.md)

**教练19项球队默认设置：** `COACH_DEFAULT`。六项POE：`POEOffense/POEOffense2/POEOffense3/POEDefense/POEDefense2/POEDefense3`；`PreferredSystem`、`ActiveSystem`（0–7原生体系）；`PlaybookID`（仅用最新同进程已命名字典）；`BenchDepth`、`RunPlayTendency`、`ZoneUsage`、`BenchUtilization`、`Tempo`、`HelpDefense`；`FreelanceType/2/3/4`（34个原生合法枚举、有序四槽）。四项已确认百分比字段0–100；BenchDepth是轮换人数不是百分比，9–10仅测试样本无固定上限；Tempo允许原生raw读写，但UI/引擎效果UNKNOWN，不能假称进攻节奏、百分比；不自行猜原生枚举值。

**对手防守18字段：** `VS_OPPONENT_DEFENSE` + owner team + opponent team + `defensive_setting_scope=OVERALL`，改变该owner面对该对手的**所有有效matchup记录**，不是单球员对位写入。字段：`PressureOnball`、`PressureOffball`、`ForceDirection`、`ScreenDefenseOnBall`、`ScreenDefenseHedge`、`OffballScreenDefense`、`PostDefense`、`DoubleTeamPerimeter`、`DoubleTeamPost`、`ScreenDefenseOnBall5`、`ScreenDefenseHedge5`、`SwitchRule`、`OnballHelp`、`ScreenHelp`、`ExtendPressure`、`TagOnRoll`、`StayAttached`、`PreRotate`；每字段必须按最新source里的合法原生字典，部分原生名作用尚未知。禁止GM写五项SimPace/SimPress/SimHelpDef/SimOffReb/SimDefReb；旧TEAM poe_*不可当作教练值；无单独球员对位/轮换分钟写入能力。

**首次生产来源门槛：** 玩家下一次主动触发正式采集上传；读取最新 `published/index.json → saves/<career>/latest.json`，本批 `source_coverage.json` 必须 `coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`，存在 `coaching/teams.json`（30队）与 `coaching/field_dictionary.json`；对手按需读`coaching/opponents/<owner>.json`，不要默认全读870组合。2026-10-18本次检查的latest仍指向旧批次 `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`，**尚无可信正式教练新来源**。教练代码已main合并，隔离局技术验收与正式来源成功发布不可混淆。

**教练提案→执行：** GM逐队以球队真实阵容决定HOLD/PROPOSED、`COACH_DEFAULT`或`VS_OPPONENT_DEFENSE`、目标合法raw值、篮球理由；只能用程序从可信批次生成`gm_intent → requests → coaching_batch → gm_proposal`，模型不猜coach IDs、before_raw/共享块、整体组身份。玩家审核`career_id/batch_id/decision_id/version/全部action_ids/batch_digest`，批准后Codex才执行`scripts/coaching_batch.py`的离线校验、RO preflight、受控execute及回执；必须玩家确认先退出教练编辑页`--coach-editor-closed`。回执`COMMITTED_VERIFIED_IN_MEMORY`不等于玩家游戏保存或新批次上传。无批准不写，互不并行，异常按原执行手册处理。保持“不为验证胜率自动推进比赛”的规则。

**交易能力：** 受控`ownership_transfer_v2`脚本`scripts/execute_approved_trades.py`或`scripts/run_approved_trades.ps1`，常用姓名/from_team/to_team，可选face/DOB；简单三届选秀权身份；plan→player-approved execute→verify；15人常规名单上限、计数与引用一致、防重放。有限支持普通球队不重叠批次；不把此成功推广成复杂多笔同队依赖、签约或裁员能力。先前两笔交易玩家确认已落地，切忌重复执行。

**签约：** GM负责球员/目标球队/逐年整数美元合同/选项/择队/审批，Codex不重复议价。`approved_signing_v1_unvalidated`和`scripts/execute_approved_signing.py`仅源码准备，`SIGNING_LAYOUT_VALIDATED=False`/`SIGNING_EXECUTION_ENABLED=False`，真实写回未运行/未验收；等有正式签约且玩家明确批准才做实机布局核验、打开控制写入，不能现在当作可用完成态。

**休赛期竞价：** `src/gm_core/offseason.py`、`scripts/offseason_plan.py`、`scripts/offseason_validate.py` 已有30队集中竞价、同队最终匹配、UFA/RFA、工资/名额顺序占用的合成来源离线规划源码，但P0真实休赛期采集、到期判定/原生AI签约冻结、下一季资金资格、持久性及签约执行未验收。规划器v1_1只准`SYNTHETIC_OFFSEASON_V1`，真实输入会阻断，不得声称已“彻底堵死”原生球员流动。待玩家触发休赛期测试/采集，另行验证原生AI不覆盖外部决策与跨赛季保存。该系统是外部竞价与合同方案来源，不自动执行游戏写入。

**经营方向：** 每月30队独立经营，除交易/人员外新增球队体系与对手防守的战术选择，提高争胜能力，同时依据玩家历史重力专项规则平衡现实/历史线。普通球员属性/潜力/徽章、人物成长仍由游戏决定，任何历史重力例外需玩家逐项批准。此次仅加载文档与GM能力，无新比赛、无任何游戏写入、无新30队决策节点；仍沿用同赛季一个GM聊天、玩家先发布新源再触发GM的流程。

## 2026-10-17 玩家新指令：两个交易均已批准、攻防开发恢复

- `GM-W02-A01`: 公牛得到 Jerami Grant；活塞得到 Coby White、Derrick Jones Jr. 和 CHI 持有的 2022 POR 首轮（`draft_pick:2022:1:28`）。玩家明确批准；`APPROVED_BLOCKED_EXECUTOR`，尚无游戏写入或存盘/数据库回执。
- `GM-W02-R02-A01`: 独行侠得到 David Nwaba；火箭得到 Sterling Brown、DAL 原始 2022 次轮（`draft_pick:2022:2:17`）和 DAL 原始 2024 次轮（`draft_pick:2024:2:17`）。玩家在同一聊天明确批准；`APPROVED_BLOCKED_EXECUTOR`，尚未执行。
- 后续使用 `docs/36_EXECUTION_BASELINE_PROMPT.md`、`docs/28_EXECUTION_WINDOW_RUNBOOK.md` 与 `docs/34_BASELINE_CURRENT_STATE.md` 第8节，由玩家交 Codex 处理，执行端先只读核验；正式交易业务写回及选秀权转让执行器在本次审查的能力表中仍未完整验收。不要把批准误当成交。
- **攻防系统开发已恢复**：以玩家最新口头指令为准，允许 Codex/开发规划基线继续开发球队自身攻防、针对特定对手的攻防设置。GM 仅在玩家提供并经验证的接口能力后使用，不自行设具体枚举、不默认AI不会覆盖。
- **MC 哈利伯顿申请交易**：玩家确认该剧情即将导致转队，尚未发生；Sacramento 下一轮准备应对核心离队，不能把未来剧情当作已执行变更。
- 本次只针对当前赛季同批次W02的后续审批和技术交接，不新增已发生的比赛场次。后续每次真实游戏月份应依据最新同口径数据，30队都做明确经营裁决（HOLD亦需理由），而不仅列出观察问题。

## 2026-10-17 新进展：玩家确认两笔交易已在游戏落地（最新状态，优先于历史节点描述）

- **执行反馈（玩家权威陈述）**：`GM-W02-A01` 公牛/活塞 Jerami Grant 交易与 `GM-W02-R02-A01` 独行侠/火箭 David Nwaba 交易，均已成功完成游戏修改。此处登记 `PLAYER_REPORTED_EXECUTED`，不再标记“待执行”，不要求重复执行或再次批准。旧W02提案内 `PROPOSED` 属原审议时历史状态。
- **尚待下次数据发布复核**：`published/saves/mc_haliburton_2021/latest.json` 在本次检查仍指向交易前批次 `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`，不能拿旧球员归属质疑玩家已完成的执行。等玩家**主动触发** Codex 数据源更新、GitHub 新批次上传后再核对双方新阵容、合同归属和三枚选秀权。游戏执行已完成与数据同步待更新分别记载。
- **新功能进度（玩家报告）**：Codex已完善自动化交易、自由球员签约、模拟休赛期签约球员的脚本机制。前述 `docs/34_BASELINE_CURRENT_STATE.md` 第8节为旧版能力索引，不可继续简单断言“交易执行器仍没有”；但具体CLI、批准入口、适用范围、成功回读、签约资金/土豪线规则仍需下次获取最新文档/验收说明，不能自行臆造调用方式。
- **玩家固定同步节奏**：下一次 GM 月度或阶段经营前，玩家先主动触发数据源更新与发布；Web GM每次开始决策先读 `published/index.json`、职业存档 `latest.json` 和新批次，重新对齐W01/W02历史数据，不自动采集、不自动推定交易后的战绩。随后30队逐队独立经营并提出新提案。
- **攻防功能**：沿用玩家最新指令继续开发，尚需玩家届时提供具体已验收接口；正常比赛AI按游戏本体运行。不额外修改球员能力。MC哈利伯顿剧情转队仍须通过未来游戏结果验证。

## 必读入口：按赛季、游戏窗口和回合形成的决策链

1. [2021–2022 赛季GM时间线总索引](../seasons/2021-2022/INDEX.md)
2. [W02/R01最新归档：同批市场议价/战术续议（没有新比赛）](../seasons/2021-2022/windows/W02_GM_20261017/ROUND_R01_RECAP.md)；[W01历史归档](../seasons/2021-2022/windows/W01_GM_20261017/ROUND_R01_RECAP.md)
3. [W02 30队同批对比基线](../seasons/2021-2022/windows/W02_GM_20261017/TEAM_BASELINE.json)（完全复用W01观测）；[W01基线](../seasons/2021-2022/windows/W01_GM_20261017/TEAM_BASELINE.json)
4. [W02新待批准交易及战术方案](../decisions/mc_haliburton_2021/20261017_W02_SAME_SNAPSHOT_GM_PROPOSED.md)；[W01原30队经营初案](../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_PROPOSED.md)
5. [7项玩家批准回执](../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_APPROVAL.md)
6. [GM决策机制v2](../GM_DECISION_MECHANISM_V2.md)及[GM SOP v2](../GM_DECISION_SOP.md)

## W02 最新节点发生了什么（2026-10-17，游戏日期 UNKNOWN）

- **批次没有变化**：`published/latest.json`仍是W01的完整相同批次，W02为玩家再次启动的赛季内专题经营节点，不是下一自然月，不能计算新月战绩或视作游戏已经推进。
- **交易议价**：外挂CHI/DET两队GM对 `GM-W02-A01`（Coby White + Derrick Jones Jr. + CHI持有2022 POR首轮换Jerami Grant）模拟达成具体经营共识；状态 `PROPOSED_NOT_PLAYER_APPROVED`，执行器未验收且游戏未写。CHA/IND特纳旧报价判定 `NO_DEAL`，不冻结其资产。
- **战术方向**：GSW防守优先、UTA米切尔两场原因未知继续等证据、DAL改善防守；保护SAC Tyrese Haliburton，所有战术均未改游戏。
- **授权边界**：仅W01七项战略/研究/非约束询价已获有限批准，W02任何新交易尚无批准。W02节点已归档，同赛季GM聊天待命。

## W01 历史节点发生了什么

- **实测基线**：PHI 16–3、BKN 14–5、LAL 15–5、SAC 14–5、GSW 9–9、UTA 5–13、DET 2–16；全部30队战绩/球队指标保存在窗口JSON；当前数据是赛季截至快照累计，不是本月独立数据。
- **经营决定**：已对30队进行12模块战略审查；玩家批准GM-A01..GM-A07的方向/研究；保护玩家国王 Tyrese Haliburton (slot=1235)，不同于 Ty Hali (slot=184)。普通能力修改持续禁止。
- **未执行市场讨论**：MKT-01 CHI/DET 格兰特；MKT-02 CHA/IND 特纳；**双方GM尚无正式一致协议**、玩家没有批准交易、游戏名单/选秀权未因此变化。
- **机制修正**：外挂双方GM协商决定交易，而非游戏CPU；赢球优先，士气/化学反应次级；每个游戏节点最多3个GM回合，通常一次定案。
- **最新停写指令**：Codex因额度暂不可执行，玩家决定本窗口**任何经营修改都不落地**，不自行转交Antigravity，等待下一月GM决策节点。旧提案没有执行权，也不能自动递延为新月应执行的动作。
- **分工最新限制**：教练攻防系统可写范围、AI是否覆盖等由Codex先调研；**玩家将结果直接交开发规划基线处理**，GM无需参与开发调研/规划，只接收未来已验收的可用操作能力。此前[GM拟写的攻防开发需求](../seasons/2021-2022/DEV_REQUEST_COACHING_OPPONENT_GAMEPLANS.md)已标记历史草稿，不视作活动交接。

## 下一次玩家在本赛季聊天启动 GM 节点时，必须这样恢复

1. **同一游戏赛季沿用同一 GM 决策聊天**；从本季[时间线INDEX](../seasons/2021-2022/INDEX.md)找到最新决策节点 W02、先前W01和对应30队冻结对比表；检查最新`published/index.json`和`latest.json`，锁定本节点 `save_id/season/batch/data_updated_at/game_date`。W01、W02只是档案中的节点编号，不强制每月新开聊天；本次W02与W01完全同批次，下一次需要新的比赛数据须单独触发采集。
2. 分析基线读取新数据后，GM对照30队前后累计战绩：同存档同赛季同口径才用`ΔW/ΔL`计算新期间战绩；不从两个赛季平均值直接相减声称月度场均贡献。排查读档回退、赛季切换、球员去留变化及已执行回执。
3. 回看本轮保护核心战略是否经得住新的胜率、净胜分、球员样本、阵容变化；W02已有CHI/DET新拟成交方案，但仍为 `PROPOSED`，玩家若不批准就不能交执行；如新的实时数据已改变需先重新估价。CHA/IND本轮 `NO_DEAL`，未来若重谈必须用新证据。
4. 用本赛季下一节点时的**实际可用执行能力**决定战术/轮换提案，不研究技术本身，不推断数据缺口。士气/化学反应是赢球次级风险。
5. 用户每个游戏月或季后赛轮次独立触发**同一赛季聊天中的 GM 节点**；每个新节点仍建立 `web_gm/seasons/2021-2022/windows/Wxx_.../ROUND_Ryy_RECAP.md` + 新的30队基线（Wxx 是节点档案目录），更新本季 INDEX 和本 CURRENT，保留审批链。节点交付后在本聊天待命，不强制结束聊天。**只有玩家确认赛季完结并归档后，新赛季才开新的 GM 决策聊天与赛季目录。**

## 永久禁区和来源边界

一般球员能力、潜力、徽章、倾向、动作、性格不能靠外挂经营修改；历史重力须专项批准，MC成长仍关闭。1984–2020历史选秀循环的完成进度需要玩家确认。数据来源`NULL`不等于0，伤病/实际计划轮换/个体士气/交易请求未知则保持UNKNOWN；完整交易业务执行器尚需开发/验收。历史决策不是游戏实际发生的事实。
