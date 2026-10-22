# Web GPT · 数据整理分析基线当前记忆

## 2026-10-21 统计模型为六阶段第二步：加工事实供教练/球员/GM

玩家确认周期运行流程**采集→数据分析→独立教练→独立球员→GM→汇总执行**，常见周期是赛季开启、月度、交易截止前一天、季后赛每轮、休赛期。Analytics职责是把真实游戏源转为后三类独立模型可核对的比赛/球员/球队/健康/合同事实与有来源的派生指标；**不替角色决定偏好和行动**。DEV29研究游戏数据与机制，DEV28补技术I/O，教练与球员人格另由其它任务开发。详见[六阶段与研究边界](../../docs/game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)。R04知识已结案但109项侧表无实时采集值，必须区分静态注册、研究候选与已采数据；R05下一轮只研究财务/合同/员工/球探/选秀游戏信息。

## 2026-10-20 DEV29 V3：逐场事实支持GM、球员、教练、媒体各自反馈

最新[DEV29 V3](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)明确目标为**自主多智能体篮球世界**，不只是GM最优方案。Analytics要设计从真实NBA2K22逐场比赛、球员健康/技能/倾向/士气、训练变化、合同与媒体事件生成**按角色授权可见的事实/反馈数据**：Player可判断职业目标和训练适配，Coach可评价战术实际效果，GM可评估合同与球员表现，Media可形成基于来源的报道但传闻必须标记。原生真值、估算指标、对外公开信息、角色自我叙述不能混成一套全知数据。R04新增完整球员原生字段与意图/权限研究，R01仍结案、R02仍为NEXT；统计缺口D28-3未完成，不能用赛季累计伪造单场互动。

## 2026-10-20 DEV29 V2资料库R01：Game Logs与高级统计优先

- 网页GPT新研究窗口按[DEV29 V2](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)主导NBA2K20–23游戏内容研究；**R01优先研究真实每场Game Logs、赛程、球员/球队Box、Advanced/Shot Chart**，形成`docs/game_mechanics/guides/K01_K02_GAME_STATS.md`及[PROGRESS](../../docs/game_mechanics/PROGRESS.md)的来源/截图证据。Analytics需将其转为GM每个问题的最低基础事实/可派生高阶指标，不把跨版本UI或公式估算冒充生产SQLite。Codex仅在研究全部完成后FINAL-CODEX盘点接口并准备DEV28，而非先替研究模型搜集网页攻略。

## 2026-10-20 DEV29前置：逐场比赛与高级指标来源反向审计

- 玩家确认之前全量采集以已知内存字段为出发点，遗漏逐场比赛、每场球员/球队Box Score、Game Logs、部分高阶指标。现有M02赛季合计/跨批差值不能还原具体对手、球员上场、场次和战术决策，分析模型必须说明`INSUFFICIENT_EVIDENCE`，不可把平均或累计伪装为真实逐场数据。
- 权威前置研究：[DEV29 NBA2K20–23终极联盟全域机制审计](../../docs/development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V1.md)。Analytics负责`GM_DECISION_TO_EVIDENCE_MATRIX`的最低/推荐/可选数据，Game Logs/Box/Per36/Advanced/Shot Zones和数据保留窗口按不同2K版本及PC22实际可观测区分。高级指标按`NATIVE_UI_OBSERVED`/`EXACT_DERIVED`/`ESTIMATED`/`UNKNOWN`标识，不能挪用NBA.com现实联盟tracking冒充本局游戏数据。
- 顺序为PR#12收尾→DEV29研究A/B/C→DEV28数据补齐，不在本次文档新增中重新跑分析、访问游戏或发布SQLite。最新生产实态每次重新查latest，旧数据门槛仍有效。

- role: WEB_GPT_ANALYTICS
- baseline_id: `WEB_GPT_ANALYTICS_V2`
- method_version: `ANALYTICS_DECISION_READY_V2`
- memory_version: 3
- last_reviewed: 2026-10-18
- state: `M02_V2_PUBLISHED_ANALYSIS_ONLY_PARTIAL_DATA_GATES`
- current_observed_published_batch: `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`（核验时最新；**下一任务必须重新读latest**）
- current_observed_game_date: `2021-12-12`（玩家确认）
- previous_comparison_candidate: `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`
- last_completed_analysis_batch_id: `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`（V2分析已发布，仍有数据身份与poss语义缺口）
- latest_analytics_run_id: `20261018_M02_DEC12_V2_ANALYSIS_01`
- latest_analytics_execution_status: `PUBLISHED_ANALYSIS_ONLY_PARTIAL_DATA_GATES`
- latest_analytics_session: [M02 V2发布及回读记录](analytics/sessions/20261018_m02_v2_analysis_github_publish.md)
- latest_analytics_dir: [M02 V2简明报告](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.md)
- latest_analytics_json: [M02 V2结构化JSON](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.json)
- latest_methodology_session: [20261018_decision_ready_v2_baseline](analytics/sessions/20261018_decision_ready_v2_baseline.md)

## 正式方法和交付

- [新版方法规范：ANALYTICS_DECISION_READY_V2](../../docs/gm_analysis/ANALYTICS_DECISION_READY_V2_METHOD.md)
- [分析基线V2](../baselines/ANALYTICS_BASELINE.md)
- 历史已发布的 [30队量化报告](../../docs/gm_analysis/2021-2022_SIMPLE_PICKS_V1_ANALYSIS_ONLY.md) / [原JSON](../../docs/gm_analysis/2021-2022_SIMPLE_PICKS_V1_ANALYSIS_ONLY.json)。它们不是M02新分析。
- **M02 V2分析于2026-10-18已发布至GitHub main**：简报、30队表、跨批表、方法来源与主JSON共5份。此前“未执行”的说明只适用于基线初始化任务。

GM要求V2放弃**默认长篇排行榜**，改为四项决策支持：
1. 30队简短诊断：阶段候选、区间战绩、核心与替补、攻防问题、教练与阵容是否匹配、内部改善与人才缺口/交易需求证据。
2. 相邻同存档同赛季批次的球员55项/潜力和名单、合同、简单选秀权差分；身份必须可信，旧`roster_changes`的姓名+FaceID只作候选，不是稳定身份。
3. 同批19项教练默认设置与按需18项对手OVERALL防守适配、异常和优先复核摘要，不复制870组原始数据。M02教练源`VERIFIED_OBSERVED_SAME_BATCH`；M01无教练来源。
4. 进攻特征、eFG%、3PA率、估算TOV率、场均得失分等确定性指标；`poss`的原生攻守语义未认证前，不能称结果为标准ORtg/DRtg/NetRtg。

每轮玩家授权发布时，在`docs/gm_analysis/<career_id>/`新建一组五个文件：`_ANALYSIS_ONLY.md`（简明报告）、`_TEAM_DECISION_TABLE.md`、`_CHANGE_TRACKING.md`、`_METHOD_AND_SOURCES.md`、`_ANALYSIS_ONLY.json`（完整证据）。每个报告必须绑定两批（如适用）、game_date、规则、计算版本/方法、身份匹配等级和未知项。

## 当前已发布M02 V2分析的验证说明

- [简报](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.md) / [30队决策准备表](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_TEAM_DECISION_TABLE.md) / [跨批变化表](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_CHANGE_TRACKING.md) / [方法来源](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_METHOD_AND_SOURCES.md) / [主JSON](../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.json)。
- GitHub创建写入已经恢复并实际完成，五文件重新读取通过；30队唯一、104场区间新增、5选秀权变化、870对手防守记录校验一致。
- 主JSON是从四份已发布MD和原始 GitHub 事实重新构建，不是旧本地 JSON 的逐字节复制；身份/55逐字段差分以及poss语义仍未完全认证，状态为`PARTIAL_DATA_GATES`。GM可用已验证的球队级事实与启发式诊断，不能把177名候选称为已验证成长。

## 下一次任务入口和明确缺口

1. 新窗口先读本CURRENT、方法规范、当前`latest.json`和选定的历史批次，重新判断当前真实latest；不要默认M02永远最新。
2. 验证可比性后用安全Python/SQL执行已有真实来源的30队、教练与区间计算；身份不足部分标`HIGH_CONFIDENCE_TEMPORAL_CANDIDATE` / `UNKNOWN`，不把候选成长当确定事实。
3. 需要可靠永久跨批球员键 → `DATA_SOURCE_REQUEST: PERSISTENT_PLAYER_IDENTITY`；`poss`语义 → `DATA_SOURCE_REQUEST: POSSESSIONS_SEMANTICS`。不要求单来源重新采集（当前采集全量-only）；缺口不妨碍其他分析。
4. 仅按玩家当前任务授权发布新五文件，回读，写对应session，最后更新本CURRENT；交接链接给GM，不自动开启GM。

## 权限边界

分析不改`published/`、`latest.json`、原数据库、Release ZIP、正式球队档案、普通球员能力、游戏内存或执行脚本。五Sim只读禁写、Tempo语义UNKNOWN、`is_in_use_raw=0`不等于防守关闭；逐人分钟与训练不在目标。源码可用则按实际Python运行方式报告，不冒充`gm_prepare.py`原样执行。单笔交易/签约、具体教练raw、历史重力都由GM玩家审批与Codex另行执行。
