# DEV13 — M3A/M3B × Antigravity DEV12：GM战术决策整合方案 V1

**2026-10-20工程回执：** 主线窗口②已接收正式main DEV14（570419a/f68d75d），整合提交82083b5，并在原PR #4完成M3-T消费、诊断、稀疏意图和本轮8项最小验收。见[实现与验收](../development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)、[GM手册](../../web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md)。PR #4已按玩家批准合入main（504a4c0）；正式30队仍UNASSESSED、V4未启用。下文为设计依据及历史增量，当前支持与已知底层目录脱敏阻断以交付报告为准，不以旧计划扩大测试或开发。

窗口①底层交接见[DEV14_TO_M3_HANDOFF](../development_reviews/DEV14_TO_M3_HANDOFF.md)：DEV14-H/DEV15、rotation域、GM净化访问检查、TEAM_BOOK_REBIND稀疏合同与MANUAL_OPERATOR_TRUST_ONLY。窗口②接准确提交后再做M3策略和回归，不复制数据库/Codec/审批，不把此说明当作已合并。

DEV14工程消费合同：见[实际运行手册](../DEV14_STATE_IO_RUNBOOK.md)与[验收](../development_reviews/DEV14_ACCEPTANCE.md)。M3-T读取M0新域的object_key/field_key、registry_version及save_instance_id/generation_id，向gm_state_io stage提交最小稀疏changes，再由玩家批准完整摘要。不得生成裸地址、复制前像或自建执行事务。能力缺失/新档未全量采集则明确未观察；本次仅补依赖说明，没有实施DEV13或启用GM V4。
> **2026-10-19 最终窗口分工和Book默认规则（最高优先级）**：[DEV18双Codex窗口交接](DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)：PR#5独立窗口①负责全部DEV14安全IO、自动Potential=1、Intangibles原生字段和受控BookID动作；**本DEV13只交PR#4的M系列Codex窗口②**负责GM分析、战术训练方案、换帅同名书归位。不同窗口必须靠PR#5最终commit+`DEV14_TO_M3_HANDOFF.md`交接，不能把两个模型当同一执行者。用户确定新档30队各自持本队同名Book，换帅归位即可，**不要另建共享书克隆/全联盟逐书验证项目**；保留通常的Native ID/CAS/读回。51未知Tendency、完整战术CRC、训练模板和疲劳知识均是后续Antigravity扩展。正文与此冲突的早期任务描述作废。

> **2026-10-19 赛季换帅与Codex主线优先**：[DEV17](DEV_20261019_17_CODEX_FIRST_MAINLINE_TEAM_BOOK_COACH_RULES_V1.md)规定：每队每游戏赛季只允许**休赛期换帅一次**。A队换B教练后，将当前教练的PlaybookID从可能的B书**恢复为A队同名且独占原生Book**，再根据B教练理念和A队球员改变A书内部战术，不触碰B书；本轮不开发合同到期/签约/自由市场机制，只做业务政策和确认换帅事件后的Book恢复动作。**Codex先集成已有DEV14与M3字段进行最低闭环**，AG余下CRC语义/倾向/模板/疲劳属于后置扩展，唯独原生Book安全绑定阻塞可提前给AG小任务。

> **2026-10-19 GM防守/Playbook最高优先级新规则（覆盖旧段落）**：[GM个人防守与球队专属战术手册](../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)要求：GM正常经营**只写PERSONAL_DEFENSE、OVERALL_DEFENSE只读不改**；**不主动修改coach.PlaybookID切书**，而是在经原生身份验证的**本队独占**Playbook 68槽中增删/替换战术。共享书owner=[A,B]时禁止任何单队写槽；换帅后重新取新教练和手册归属，需要AG认证的技术性球队书绑定时另获用户批准，再按新教练理念改本队书。此前本文件任何“先Overall后Personal/日常先切Book再改Slot”的文字作废，不能继续用旧规则生成M3动作。

> **2026-10-19 用户七项正式定稿 / DEV16**：以[DEV16完整GM战术、训练与原生字段整合](DEV_20261019_16_M3_NATIVE_COVERAGE_AND_GM_TRAINING_PLAYBOOK_INTEGRATION_V1.md)为本文件后续业务依据。具体执行限制仅为同一team/opponent的`OVERALL_DEFENSE+PERSONAL_DEFENSE`不能在同一内存批次（必须顺序预检执行）、`coach.PlaybookID + PLAYBOOK_SLOT`不能同批（先切本后重读槽位）。二者不是篮球策略互斥。Antigravity负责Playbook/现实战术映射与替换、补51无名Tendency、按位置训练模板与疲劳只读；Codex负责注册统一DEV14、GM D1-D6诊断。训练只允许球队/个人强度、恢复及球员原型/位置模板，不扩展到单项属性训练或直接徽章操作。已证同codec家族允许一项代表实测支持整类实现，不要求逐字段游戏手工验证；但字段地址、值域、真实来源不能省。World当前50及Gameplay4项接入有效，未认证其它字段不得假装全覆盖。

> **2026-10-19 用户最终决定 DEV15 V2（覆盖本文件所有旧门禁）**：GM所有队允许以原生球员`Intangibles`（PLAYER 0x440，25–99）作为策略性轮换控制输入，目标是引导原版AI首发/第六人/分钟；其作为仅此一个字段的普通GM经营权限例外，经玩家批次批准和DEV14确定性前值/写入/读回即可。**不再要求研究/验证对交易、合同、模拟及其它系统的副作用**，不锁定精确分钟。全部球员真实潜力在正式采集入库后/发布前由统一确定性脚本将各表、JSON及Player raw_struct 0x441**置1**，来源标`MASKED_NOT_OBSERVED`，GM禁止将1当作真实潜力。详见[DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)及[额度分批计划](M_SERIES_20261019_QUOTA_AWARE_EXECUTION_PLAN_V1.md)。早期“仅GM投影隐藏Pot/必须先研究Intangibles副作用”的段落全部失效。
> **2026-10-19 M3-T新决策接口与低额度执行次序**：先读[分批开发顺序](M_SERIES_20261019_QUOTA_AWARE_EXECUTION_PLAN_V1.md)。正式GM使用M3之前，需按[DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)在采集入库后、发布前强制将所有Player Potential数据覆盖为1（并标记MASKED），不准将1作为球员潜力依据；M3诊断引入首发/第六人/轮换分钟`minutes_target_band`与实际分钟对账，优先教练BenchDepth等非原生属性调整。已知本局PLAYER `intangibles`字段0x440作为综评补偿、玩家逐批批准后，才允许单字段例外`PLAYER_ROTATION_OVR_BIAS`通过DEV14执行。该值只是可能影响显示OVR/轮换的策略性代理，**GM市场估值和实力评估不能使用被调整OVR替代真实能力/比赛数据**。本扩展不恢复硬锁分钟，不扩大直接修改原始Ability/Potential/Badge权限。正式动作权限与真人凭据见[DEV14-H安全加固](DEV_20261019_14H_DEV14_POST_REVIEW_HARDENING_V1.md)。

2026-10-19 · owner: Web Development（决策与审阅） · implementation: Codex（M3集成及源数据接入），Antigravity（原生游戏战术与训练接口的开发及实机验证） · authority: USER approval for all game writes.

**决策：M3A/M3B原工程验收保留，不重做P1–P5、不重跑已经通过的业务接口。不把DEV12直接吞进原M3代码。新增M3-T战术证据、GM诊断约束、提案动作与组合依赖整合层，并在GM V4正式启用前完成最小必需部分。**

> **2026-10-19 DEV14底层依赖更新**：正式新增[DEV14确定性状态读写引擎](DEV_20261019_14_DETERMINISTIC_STATE_IO_ENGINE_V1.md)，Codex先在独立分支实现`NativeFieldRegistry + Observed/Desired/Applied状态隔离 + SQLite控制库 + 批次审批/前值/写入/读回/条件回滚 + 同批采集/对账`。**DEV13只消费其已证状态查询和获批动作合同**，不得自行写第二套内存事务或另建30队数据库表。DEV14完成不自动启用GM V4；Antigravity本地DEV12字段未归档时，能力清单按READ_ONLY/BLOCKED_SOURCE显式保留。`

> **DEV14 V1.1存档隔离前置条件**：DEV14新增每存档私有控制库、唯一活动存档、generation、无损切档与危险reset防护。DEV13所有M3-T球员/战术/训练提案必须带`save_instance_id + generation + source_batch`与玩家批准绑定，**旧档计划不得在新档自动执行**；新档首次`full_verified_v1`后才能形成正式GM分析。详情见[DEV14](DEV_20261019_14_DETERMINISTIC_STATE_IO_ENGINE_V1.md)第2A节与DEV14-D。

## 0. 核对现状和仓库引用

- [PR #4](https://github.com/chris2gao/nba2k22-gm-engine/pull/4)，head fa62fb2d371438cd9d8062e1fa842e7c8eede4ad；37文件，Draft、Open、未merge；代码存在且M3A/M3B本地工程完成不等于30队实际研究已启动。
- [M3B工作手册](https://github.com/chris2gao/nba2k22-gm-engine/blob/fa62fb2d371438cd9d8062e1fa842e7c8eede4ad/web_gm/manuals/GM_M3_DECISION_WORKBENCH.md)；[M3A手册](https://github.com/chris2gao/nba2k22-gm-engine/blob/fa62fb2d371438cd9d8062e1fa842e7c8eede4ad/web_gm/manuals/ANALYTICS_M3_WORKBENCH.md)；[M3B验收](https://github.com/chris2gao/nba2k22-gm-engine/blob/fa62fb2d371438cd9d8062e1fa842e7c8eede4ad/docs/development_reviews/DEV10_M3B_ACCEPTANCE.md)。
- 现M3六维：D1_STAFF，D2_TACTICS，D3_ROSTER_USE，D4_MARKET，D5_ASSETS_AND_DEVELOPMENT，D6_TEAM_IDENTITY_AND_MONITORING。HOLD/INTERNAL/MARKET及双边接受、报价digest、资产冲突、教练19默认/18整体防守的离线生成已经存在。缺乏完整战术/训练输入的强约束；非COACHING动作在现源码被研究状态阻断。
- [Antigravity在main提交的部分DEV12代码 commit 9b4fe87](https://github.com/chris2gao/nba2k22-gm-engine/commit/9b4fe8739315013128234da9c7fc976252174c6f)：src/tactical_reader.py、src/tactical_fit_analyzer.py、src/player_tactics_adapter.py、src/matchup_defense_adapter.py、config/gm_tactical_knowledge_v1.json、研究和tests。用户又提供本地专用工作区 e:/games/NBA 2K22/antigravityUse/完整战术与球员行为系统/ 的README、CLI、训练联动和步行者实机报告，**这些本地文件尚未全部在GitHub线上可供我审核**。线上已见7文件≠全部本地完成能力。
- [DEV12 V2](DEV_20261019_12_V2_ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING.md)仍由Antigravity负责原生地址、读写、实机验证与训练；本DEV13不改变开发分工。

## 1. 用户要的M3完整GM决策链（从事实到交易）

每支球队每个检查点以**以下因果顺序**分析，不准把“缺人所以交易”作为起点：

1. 一致来源：球队现有教练原始评级及8体系熟练度（只读）/ActiveSystem/PreferredSystem/POE/Freelance/RunPlayTendency/球队本Playbook及68槽原生数据、每人4有序Play Types/PlayInitiator/99 Tendency（实际认证字段）/55原始能力（只读）/全部对手18整体及逐人防守/球队训练及疲劳可用性/战绩与本人及队友统计、合同预算。
2. 进攻身份：优势创造者、传导者、终结者、掩护者、无球牵制、篮板/二次进攻；防守身份：主防、协防/tag、护框、可换防、后场篮板。问战术为什么会或不会被调用，不能看OVR排序直接判定。
3. 发现断链：类型未覆盖；同类型但战术真实受益人未知；个人倾向与叫战术频率冲突；教练体系偏好与人员适配冲突；逐人防守责任与原版整体默认是否产生继承/覆盖问题（GM不修改整体防守）；球员原始技能限制；训练/疲劳使人员无法完成高强度角色；或者根本没有问题，HOLD。
4. 给出正反事实与代价：HOLD vs 调原有教练设置/本队独占战术本内部plays vs 调4PlayType槽位/PlayInitiator vs 最小必要个人Tendency vs 逐人防守（整体防守仅观察） vs 训练/恢复 vs 员工与主教练 vs 自由市场/交易。每个候选必须有“为何优于/劣于HOLD、有哪些替代及负效应、若被对手针对的下一选择”。
5. 只有证明了无法经济合理地使用现有人员与战术修复角色缺口，才进入D4 MARKET；交易必须符合M1财务和M3双方独立GM利益，不把愿意卖/合理换当必定成交。
6. 赛前提案，原版ACE比赛中继续自主调整；后续批次再看表现。3D与CalendarSim具体影响权重若不可证标UNKNOWN，不能编提高胜率百分比；训练输入不直接改人物原始能力。
7. 30队彼此独立形成报价和组合同步：一个队交易掉的球员可能是另一个队的核心，成交后的战术/训练/逐人防守人员绑定全部重新规划，而不是沿用旧快照继续执行。

## 2. 关键在线代码审计发现（仅针对目前已公开的9b4fe87版，不代表用户本地新版本仍有问题）

### 阻断A：战术手册“已完全解构” ≠ 已知道每条Play所属PlayType

- src/tactical_reader.py 的 read_team_playbook() 读取68个4字节值并转为hex CRC（all_active_crcs）；没有返回每个战术对应的原生Play Type或实际发起/终结者。
- src/tactical_fit_analyzer.py 的槽位检查：对名字包含 pacers 的手册 + Isolation Point 硬编码 STATIC_PLAY_TYPE_UNSERVED，其余非空槽直接 TYPE_MATCHED_ONLY。**这个逻辑不能证明有同类型战术，更不能声称STATIC_VERIFIED**。
- 必须改为：PlayID/CRC经真实原生映射给play_type且可追溯→计算交集。无法映射则COVERAGE_UNKNOWN，禁止把“手册有30条战术”或Pacers硬编码当因果证据。

### 阻断B：倾向阈值和“最佳体系”过强结论

- 在线诊断器将Touches≥75且PlayInitiator或Iso定义PRIMARY_CREATOR，≥3人则BALL_DOMINANCE_CONGESTION；建议固定主控88、副控72、三控60。这是篮球启发式，不是已证明的2K22 Touch调用公式。
- 教练当前体系不是其8项能力中的最大值，就直接标SUBOPTIMAL_SYSTEM_MISMATCH；可能忽略球员Roster Fit、Playbook与教练偏好共存关系。不能仅因Carlisle Perimeter85就确认整个球队OPTIMAL_ALIGNMENT；最多确认COACH_NATIVE_PROFICIENCY_ALIGNMENT，而不是战术效果最优。
- config/gm_tactical_knowledge_v1.json 卡片包含minPassingIQ75、DISH≥75及固定PlayType1规则；这些应标RESEARCH_HEURISTIC或HYPOTHESIS，不能标NBA2K22原生必备阈值。对于训练原型亦是建议，不代表自然成长有保证。
- 新M3对于这些结果需展示源/解释/置信类别，并允许GM否定、提出替代；禁止将启发式观察直接转成数字修改决定。

### 阻断C：独立操作能力不等于已接入M3完整审批

- main版 src/player_tactics_adapter.py 的 execute_single_write(runtime_addr,expected_old,new_val) 在函数入口只做前值CAS+写回读回，**没有在这一入口强制包含career/batch/player identity/field allowlist/玩家批准digest**；preflight有字段白名单但直接write接受任意runtime地址。需要执行时重新验证来源、身份、字段和用户批准；禁止将裸地址写函数暴露给GM外部CLI。
- main版 src/matchup_defense_adapter.py 的 execute_matchup_write(settings_addr,...) 类似接受裸地址与任意8字节hex；preflight通过位掩码编码new_value但未在这段验证真实原生枚举合法性，可能截断。需复用原有18字段enum合同、实际条目身份/对手/owner绑定与玩家审批。
- Antigravity本地更新版是否已实现绑定，以最新实际源码及测试验证为准；**DEV14原生集成交窗口①，不由本M系列窗口复制执行引擎**。目前不能宣称生产可安全执行。

## 3. M3-T增量架构：先建立源数据与只读GM规则，再接动作

### T1 来源和快照桥接（Antigravity可本地采，Codex把产物接入M0/M3A）

不要在网页GM调用直接依赖live_memory/CoachLocator；原生游戏运行在玩家Windows本地，网页GM必须通过已有GitHub JSON/SQLite读取。提供同一次玩家触发的full_verified_v1生产批次下新增tactical数据文件或SQLite安全投影。保留M0原始源时间和snapshot ID、不修改既有M1/M2语义。

建议规范化DTO字段（实际名称由Codex确认，禁止把UNKNOWN默认为0）：
- team_tactics(team_id,coach_id,coach_ratings,system_proficiencies,active/preferred,freelances,run_play,playbook_id,playbook_crc_catalog,playtype_resolution_status)
- player_tactics(team_id,player_identity,native_player_id,play_types[4],play_initiator,tendencies{field:value},role_candidates,coverage_status)
- defense_personal(owner_team_id,opponent_team_id,opponent_player_id,defender_player_id,settings{18},inheritance_status)
- training(team_id,player_id,archetype,intensity,mentor,fatigue,current_availability,effect_certainty)
- evidence_provenance(career_id,batch_id,game_date,source_hash,code_version,profile_version,read_count,decoded_count,unknown_fields,enum_dictionary)
- special: per-play PlayType/beneficiary source may remain UNKNOWN if only CRC observed; must not make up mapping.

仅读快照；source unavailable时返回 TACTICAL_SOURCE_UNAVAILABLE/ANALYSIS_PARTIAL。身份映射同时验证本季球队名单与player_id，交易/解约/赛季转换后必须换来源。query采用现有QuerySession分页，M3来源投影一队/球员/对手有界，不要把99×466原值一次复制到决策提示上下文。

### T2 M3A事实包与证据索引

扩展prepare -> team_tactical_context、player_tactical_context summaries、individual_defense_context、training_context/source_coverage，并在团队D2/D3/D5与市场候选共享。保存可回查 evidence: tactical:TEAM、tactical-player:IDENTITY、tactical-playbook:TEAM、tactical-defense:OWNER:OPP:PLAYER、tactical-training:PLAYER 等**真实查询索引**。

不要悄悄在seal后的M3A包内插入事实：源扩展应该从新run prepare并固定旧run supersedes，缺实时资料则研究隔离另加有来源的supplement而不改变旧基线。P1允许UNKNOWN但市场交易理由不能把未知来源冒充静态已证缺口。

### T3 M3B六维研究增强（保留P1–P5并显式校验必要诊断）

- D1_STAFF：主教练真实熟练度/职责评级、人员系统适配、换教练代价。
- D2_TACTICS：体系、手册、实际PlayType覆盖状态、ACE约束、对手Drop/Switch/Blitz/TopLock应对与至少一条反制。
- D3_ROSTER_USE：全员四槽/Touch/Shot/Iso/Drive/99个体倾向关键字段、只读能力、首发/角色/真实分钟非锁定。
- D4_MARKET：严格在内部调整排除缺口后才构建角色规格与报价，M1金融代价与对方独立利益。
- D5_ASSETS_AND_DEVELOPMENT：具体训练原型、强度、导师、疲劳/可用性与合同窗口、自然成长的事实与假设分离。
- D6_TEAM_IDENTITY_AND_MONITORING：球队进攻哲学、防守策略、针对与被针对的对策、事后观测计划。
- 每队增加 machine-checkable internal_tactical_diagnosis_refs / rejected_internal_fixes / market_gap_after_internal_assessment / evidence_quality，不靠文字长度证明篮球结论。
- 当缺战术数据时允许证据不足HOLD、RESEARCH，而不是强迫没有依据的交易；同一球队可以保留合理“先不调整”。

### T4 动作与组合校验（从RESEARCH_ONLY逐项升级）

增加明确动作和能力注册：COACH_DEFAULT（已有）、PERSONAL_DEFENSE（GM正常唯一对位写类型）、PLAYER_PLAY_TYPE、PLAYER_TENDENCY、TEAM_EXCLUSIVE_PLAYBOOK_CONTENT、TRAINING_PLAN、LINEUP_ROLE（如实机认证）。OVERALL_DEFENSE继续读，不进入普通GM修改提案；coach.PlaybookID只能由独立获批的专属Book绑定或原生合法换帅流程处理。未有正式执行器的动作保持RESEARCH_ONLY/BLOCKED_EXECUTOR，不可由于Antigravity演示了preflight就算可批准落地。

- 冲突键：
  (player_id,playtype_slot)；
  (player_id,tendency_field)；
  (team_id,playbook_id_or_play_slot)；
  (owner,opponent,opponent_player_id,defender_id,defense_field)；
  (player_id,training_period,training_field)；
  (team_id,coach_field/opponent_overall_field)。
- 顺序：现任Coach与本队独占Playbook影响PlayType适用性；个人防守单独稀疏写，GM不再先修改Overall；换帅后重新认证球队专属Book并改写本队槽位，原已批slot计划失效；交易后人员/个人对位/训练/战术绑定必须按新名单重计划。
- 最终输出仍分离：ANALYSIS_CONFIRMED vs RESEARCH_HYPOTHESIS vs OFFLINE_PREPARED vs APPROVED_BY_USER vs EXECUTED_READBACK_VERIFIED，不得混淆。交易/签约当前独立执行链不变。
- 修改球员Tendency是玩家新许可的运营输入，但仍每个player+field+before/after+reason+approval+source绑定；普通能力、潜力、徽章、身高速度不可直接写。教练属性只读用以选择教练/合同，不允许任意提高原始教练评级。

### T5 GM决策知识：不靠100条虚假权重公式

Antigravity交付的gm_tactical_knowledge_v1可做source-grounded规则卡来源，但必须给每条关系标状态：
- STATIC_VERIFIED：真实PlayType与对应Playbook Play的Type已经解出且匹配；
- GAME_NATIVE_FIELD_VERIFIED：原生数值与实际身份读回，不代表效应验证；
- COMMUNITY_BEHAVIOR_REPORTED：已发布2K22玩家观察；
- BASKETBALL_REASONING：现实篮球可解释但2K引擎未验证；
- HEURISTIC_THRESHOLD：Touch75、DISH75等经验假设；
- UNKNOWN：不能确认。
不要因为字段可读就称“+12胜场”；高Touches不等于天生球权冲突，高教练Proficiency不等于全队战术最优。每一条交易/倾向/训练建议必须回答：观察到的事实、为何选择该方法、改变哪项机制、潜在反效果、为什么优于HOLD、被对手针对后的反制。

建议以两个实例验收：1）现实GSW/Curry Klay Green Looney Wiggins的短顺下和二级进攻路径；2）本局IND Carlisle Brogdon LeVert Sabonis Duarte针对个人Touch、PlayType与真实书内Type的检查，未查出战术Type时标UNKNOWN，不得擅称已经证明Pacers书没有ISO Point。

## 4. 迁移与验收策略

**不能要求Codex推翻已完成的M3主干**：已有15个直接检查、合成30队P1–P5、真实M02 30队466身份验证仍有效。增量开发新增以下专门验收案例：
1. 同职业生涯同批数据，30队与466球员真实身份对应，分页和缺省字段未知；错队错时拒绝；
2. 68个Playbook槽只有CRC而没有类型映射时，所有这类PlayType coverage必须UNKNOWN；不得因为Team=IND或PB name=pacers就断言STATIC_VERIFIED；
3. 玩家Touch≥75但球权分布实际合理时不能自动判定TRADE；同样教练最高熟练体系与实际Active不同不能自动改体系；
4. 同一个球员同一Tendency不同值冲突、不同槽合法组合、重复当前同值幂等；
5. 同一对手的多个PERSONAL_DEFENSE字段/球员可安全组成一个稀疏批次，默认不产生任何GM整体防守写；整体字段仍保留RO；
6. **按用户默认30队各有同名书**，已确认换帅后将当前Coach的BookID恢复到本队已存在同名Book并重新采集本队68槽；只修改当前本队书、其它队数据不动。仅真实读到同名ID缺失/身份异常才阻断该动作，不另开发模拟共享书克隆。交易后个人战术、训练与对位旧目标须重新绑定或BLOCKED；
7. 未经玩家批准，任何新增动作都不能拿裸运行时地址/8字节hex绕过身份与digest白名单直接写游戏；坏enum、新批、来源过期拒绝；
8. 原始能力/潜力/徽章保存前后内容不变（只在隔离测试存档核查），训练自然进步只能是游戏后续结果；
9. 两种比赛路径：3D赛场与CalendarSim无法证明的效果写UNKNOWN，并给赛前可证假设/反例；
10. 同一分析有HOLD/INTERNAL/MARKET三种可比替代，两方同版接受/财务/终稿修订和历史回溯不受新的tactical actions破坏；
11. 在线/本地版本差异：Antigravity本地完整目录经Codex整理提交后，重做本文件第2节的源码审阅；不能拿9b4fe87七文件替最新本地通过验收。

## 5. 交付与版本门禁

- M3A/M3B PR#4先保持既有工程成果，提交/合并需要用户另批准；新任务优先在**独立M3-T分支/PR**增量完成，避免干扰正在调试的Antigravity本地专用目录或重复实现DEV12。
- Antigravity扩展在M3主线之后按需提交；本M系列窗口**只从窗口①的DEV14_TO_M3_HANDOFF.md和已合入的PR#5接口消费字段**，不再归并第二套coach_locator/采集器。
- 短期“最小GM V4启用前门禁”：M3能读同批战术上下文；P1/P2必须有经证据审阅的内部战术替代对照；战术信息不足时不能产生伪证交易结论；动作仍可RESEARCH_ONLY，不必等99倾向每种全写才能开GM分析。
- 完整功能激活条件：真正有效的Playbook类型映射、个人防守/训练/倾向的有界审批执行器、跨交易依赖和写入后读回以及新一轮可比比赛数据。所有允许修改的人物Tendency需玩家具体批准。
- 不自动把GM V4从DRAFT_NOT_ENABLED改FORMAL，不自动更改任何球队/游戏/原始SQLite，不合并PR，不启动M4。

状态：M3-T_RESEARCH_AND_INTEGRATION_PLAN / NOT_EXECUTED。整理负责人尚未实际拿到Antigravity本地README及全部源码版本，本规划以上线9b4fe87和用户本轮报告为事实基础，需后续新版入库再针对差异审阅。
