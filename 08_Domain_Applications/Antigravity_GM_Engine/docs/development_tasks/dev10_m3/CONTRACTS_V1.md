# M3数据与接口契约草案

`contract_version=DEV10_M3_DESIGN_CONTRACT_V1`。本地实现已完成，运行契约由标准库Python校验器执行，见[M3A](../../development_reviews/DEV10_M3A_ACCEPTANCE.md)/[M3B](../../development_reviews/DEV10_M3B_ACCEPTANCE.md)验收及实际手册。本页保留原设计字段和拟议接口，补充的实际参数（template、artifact/section、历史上下文等）以手册/CLI为准。对象均为纯DTO；不能用契约或样例伪造观测/批准/执行回执。

## 1. 通用对象

**SourceBinding**：沿用M0的career_id/snapshot_id/batch_id/game_date/data_updated_at/publication_status/audit/query_version/purpose；M3补充显式season、history_branch_context、context_evidence。来源绑定由工具构建，模型不能覆盖。code_commit、calculation_version、knowledge_version单独记录；GitHub提交只看已有时间戳同步，M3不增加原始数据哈希比较。

**EvidenceRef**（工具生成或校验）：ref_id、kind=FACT/METRIC/KNOWLEDGE/FINANCE/STRATEGY/PLAYER_OBSERVATION、binding/run_id、entity、row_identity、field_path、availability、value_preview（小型）、method_version。JSON历史证据另带file/field；fact/metric引用必须可回查选定静态来源或封存派生run，不能用一段文字“已读取”替代。模型只提交ref_id，不改其值。

**Metric**：metric_id、value（number|null）、unit、basis=CALCULATED/HEURISTIC/UNKNOWN、scope=CUMULATIVE/INTERVAL、formula_version、input_refs、sample、unknown_reason。原始OBSERVED字段仍保留FACT引用。value为null时reason必填，真实0不能省略；百分率单位fraction，不混入0–100。

**Issue**：code、scope（run/team/player/action/field）、object_id、reason、evidence_refs、effect=BLOCK_AFFECTED_ACTION/REVIEW_ONLY/UNKNOWN_METRIC、needed_input。此为当前任务诊断，暂不实施M4全局问题队列或严重度自动分流。

## 2. AnalysisRun与TeamFeature

AnalysisRun：

```text
analysis_run_id, revision, supersedes_run_id, created_at, sealed_at
source_binding, previous_source_binding|null, context, code_commit
calculation_version, knowledge_version, finance_run_id|null
status DRAFT_FACTS / DRAFT_ANNOTATED / SEALED_COMPLETE / SEALED_PARTIAL
authority ANALYSIS_ONLY, execution_authorized=false
expected_team_ids[], read_team_ids[], prepared_team_ids[], annotated_team_ids[]
source_access[], method_registry[], issue_index[], team_index[]
```

status由工具根据输入与覆盖生成，调用方不能直接设置SEALED_COMPLETE。保存事实后若缺本局定性诊断，只是DRAFT_FACTS；分析模型可以对缺失员工效果给出有理由HOLD，但不能对未读取名单声称全员分析。

TeamFeature：team_id/abbr、observed_performance{cumulative,interval,comparability}、player_supply{source_identity_set,players[],coverage}、staff_context、coaching_context、financial_and_assets、annotations、issues、source_refs。players[]至少包含identity/name/position、能力与合同引用、原始统计引用、样本和缺口；`annotations`由分析端提供diagnosis/talent_gap_evidence/utilization_hypothesis/internal_levers/market_clues/strategy_change_signals/alternatives_explanations。事实字段只由adapter/calculator修改。

SourceAccess：access_id/entity/binding、projection/filters/query_version、screened_count（SQL真实返回）/read_count/returned_identities、cursor_exhausted、status、requested_scope、execution_origin{LOCAL_CLI|WEB_ACTUAL_SESSION,tool_name,time}。没有实际会话证据不能写WEB_ACTUAL_SESSION。aggregate不是全记录阅读，row数不是逐项评估。

MarketCandidate：candidate_id、run_id、requesting_team_id、candidate_kind=ROSTER_PLAYER/POOL_MODEL/STAFF_REFERENCE、source_identity、source_owner、screen_query_ref、fit_refs、cost_refs、availability_status、evaluation_status=SCREENED/READ/ASSESSED、unknowns。非在队pool模型保持SCOUTING_ONLY；staff仅参考。交易意愿由M3B独立决定，不在M3A预写seller_accepts。

ScreenQuery：query_id、source_domain、role_question、filters[{native_field,operator,value}]、excluded_team_ids、order_by[{native_field,direction}]、limit、source_binding。字段限已注册projection或attributes.<verified_field>.value，比较符限eq/gte/lte/is_null；由adapter参数化生成查询，不拼接模型原始SQL。结果记录filter_population_count、matched_count、unknown_required_field_count、returned_identities与next_cursor；聚合计数只是筛选证据。sealed run允许追加不同query_id的supplement，candidate_json内保留完整查询回执，不更新原packet。重复同query_id且内容变化拒绝，修改条件用新ID。

## 3. DecisionRun、球队审议和方案

DecisionRun：decision_run_id、revision、created_at、mode=DEVELOPMENT_CANDIDATE|FORMAL_ENABLED、protocol_id/version、source_binding、analysis_run_id、strategy_refs[]、phase、status=OPEN/PARTIAL/VALIDATED/FINAL_PROPOSED/SUPERSEDED、expected_team_ids[]、phase_progress、current_final_version|null、approval_status=NOT_GRANTED、execution_authorized=false。FORMAL_ENABLED仅由后续玩家批准的协议启用配置支持；不能靠调用方传一个mode开启。

TeamReview：decision_run_id/team_id/review_revision、expected_source_identity_set_ref、player_assessments[]、decision_dimensions{D1..D6}、competitive_window、team_interest_profile、evidence_refs、uncertainties、review_status。沿用原GM_TEAM_DECISION_CONTRACT的业务字段，通过适配层把round_id映为内部phase/group标识；旧V3文件与schema不改。

PlayerAssessment：source_identity、role_assessment、retain_or_research_position、key_evidence_refs、unknowns、review_depth=NORMAL/FOCAL。不用旧名称作唯一键；有实质信息的短评足够，不要求每人长文。每队人物评估与source_identity集合双向相等，人数相等但身份不同不通过。

Alternative：alternative_id、team_id、category=HOLD/INTERNAL/MARKET、status=VIABLE_CANDIDATE/RESEARCH/BLOCKED/NOT_APPLICABLE、problem、proposed_means、evidence_refs、benefit_hypotheses、costs_and_opportunity_costs、finance_scenario_ref|null、reversibility、counterevidence、change_conditions、selection_reason。三类都需实质方案或非适用理由；不能用空数组充数。定量成本仅引用实际M1或计算结果，不要求编造综合价值分。

TeamInterestProfile：objective_and_window、evidence_refs、role_priorities（有序）、retain_thresholds[]、sell_conditions[]、pick_commitment_conditions[]、contract_risk_conditions、best_internal_alternative_id、reversal_conditions。阈值可以是定性条件，数值必须有来源/计算，不把模型阈值当规则。冻结当前revision后再进入双边谈判；变动必须重新复核受影响报价。

## 4. Offer、Response、Portfolio与Final

Offer：offer_id、terms_revision、decision_run_id、source_binding、team_ids[2]、moves[]、conditions[]、dependency_ids[]、finance_scenario_ref、terms_digest（程序生成）、status=NEGOTIATING/AGREED_IN_PRINCIPLE/REJECTED/SUPERSEDED/NO_DEAL。普通球员moves以source_identity/from/to为核心，简单签以asset_id/year/round/original/current_owner为核心；所有权用当前batch，不用模型自报。

terms_digest规范输入为`{source_binding, team_ids, moves, conditions, dependency_ids}`：team_ids与dependency_ids排序；moves按(kind,source_identity或asset_id,from,to)排序；conditions保留规范条款数组原序，金额只用整数。序列化用sort_keys=true、ensure_ascii=true、separators=(',',':')，SHA256。说明文字、offer状态、响应和展示排序不入digest；版本仍单独匹配。任何语义条件变化都成为新条款，不能通过改措辞沿用接受。实现时共享一个规范化函数，不由多个CLI各自计算。

Response：response_id、offer_id、terms_revision、terms_digest、responding_team_id、team_interest_revision、stance=ACCEPT_IN_PRINCIPLE/REJECT/COUNTER/NEEDS_EVIDENCE、rationale{gain,cost,opportunity_cost,why_better_than_hold}、alternative_refs、conditions、evidence_refs。程序拒绝队外responding_team；ACCEPT不能新增隐藏条件（有新条件属于COUNTER）；模型response绝非玩家批准。

Portfolio：portfolio_id/revision、selected_offer_versions[]、selected_internal_action_versions[]、research_action_ids[]、holds[]、rejected_alternatives[]、conflicts[]、dependencies[]、team_combination_reviews[]。选定层资产/字段冲突不得带入可批准清单；同队交易依赖按现有执行器范围单列。变动portfolio使之前validation/final陈旧，需新验证记录。

ValidationReport：report_id、decision_run_revision、portfolio_revision、source_check、roster_coverage、bilateral_checks、asset_conflicts、field_conflicts、dependency_checks、finance_evidence、executor_readiness、issues、generated_artifact_refs、valid_for_finalization、execution_authorized=false。valid_for_finalization允许RESEARCH/HOLD存在，但不允许它们冒充可执行动作；不能单靠对外传入report_id确认通过，必须来自本地确定性validator当前版本。

FinalProposal：final_id/version、decision_run_id、portfolio_revision、validation_report_id、source_binding、protocol_version、status=FINAL_PROPOSED、approval_status=NOT_GRANTED、execution_authorized=false、team_summaries[30]、specific_approval_items[]、research_items[]、holds[]、alternatives_not_selected[]、hypotheses[]、strategy_candidates[]、generated_artifact_refs、supersedes_final_id|null。空动作且30队有理由HOLD为有效终稿；没有完整覆盖则PARTIAL_PROGRESS，不可用FINAL_PROPOSED伪装。

Hypothesis：hypothesis_id/action_or_hold_id、baseline_refs、mechanism_claim、alternative_explanations、expected_direction、observation_metrics、minimum_evidence_description、falsification_conditions、confounds、execution_receipt_ref=null。最后字段由将来M4实际回执关联，M3不能填写已执行证据。

StrategyCandidate：base_state_id|null/expected_revision、candidate_state（遵守M2schema）、reason、rejected_hypotheses。候选是分析版本，不携带APPROVED/EXECUTED；保存由显式M2命令执行。

## 5. 工作台：最小新增表与事务

保留M1/M2表及workbench_metadata(version=1)，以新增`workbench_component_versions(component PRIMARY KEY,version)`记录M3版本，避免无关全库迁移。M3写入口首次执行时在事务内建以下表；M1/M2只读功能不要求已有M3表。只读M3遇缺表返回M3_NOT_INITIALIZED，不创建目录/数据库。

```text
analysis_runs(run_id PK, career_id, batch_id, revision, status, source_json,
              previous_source_json, run_json, created_at, sealed_at)
team_features(run_id FK, team_id, feature_json, PRIMARY KEY(run_id,team_id))
market_candidates(run_id FK, candidate_id, team_id, candidate_json,
                  PRIMARY KEY(run_id,candidate_id))
decision_runs(run_id PK, career_id, batch_id, analysis_run_id FK,
              revision, phase, status, current_final_version, run_json, created_at)
decision_artifacts(run_id FK, kind, artifact_id, revision, payload_json, created_at,
                   PRIMARY KEY(run_id,kind,artifact_id,revision))
```

source_access和methods在analysis_runs.run_json内；人物明细在按队team_features.feature_json内，不另建全原始球员库。decision_artifacts.kind限定TEAM_REVIEW/ALTERNATIVES/OFFER/RESPONSE/PORTFOLIO/VALIDATION/FINAL/STRATEGY_CANDIDATE/HYPOTHESIS，读取接口按kind/队/ID投影，禁止无界输出整个JSON列。

post-seal市场supplement的query/access回执保存在candidate_json内；只追加新candidate/query，不覆盖sealed基线统计。查询时单列supplement计数，不把后来查过的记录追认成prepare时已读。

analysis draft修改需expected_revision；封存后不覆写，后续新run引用旧run。decision artifacts追加版本，写动作以BEGIN IMMEDIATE读取当前revision，验证预期再同事务更新run pointer与插入工件。相同artifact/revision重复内容返回已有结果或ALREADY_EXISTS，不追加重复接受；不同内容不可覆盖。finalize原子写final并更新current_final_version，旧final保留。

M1/M2引用同库具体run/state，跨career拒绝；跨batch的历史研究引用允许但标REFERENCE，不充当当前成本或当前事实。导出丢失本地来源时报告不可消费，不自动从活跃库补数据。

## 6. 代码分层与拟议CLI

```text
gm_data_access/analysis_inputs.py       QuerySession + q_team_stats -> plain DTO
gm_core/analysis_metrics.py           ratios/deltas/comparability/role evidence helpers
gm_core/analysis_packet.py            annotations + source coverage + seal validation
gm_core/decision_protocol.py          phases/team coverage/artifact contracts
gm_core/market_negotiation.py         terms normalization/response-version consistency
gm_core/decision_portfolio.py         selected resource/conflict/dependency checks
gm_core/decision_handoff.py           offline coaching + descriptive trade/signing intents
gm_workbench/store.py                 additive tables/optimistic revisions/queries
scripts/gm_analysis.py                explicit analysis commands
scripts/gm_decision.py                explicit decision artifact commands
```

不得从gm_core引入memory/approved_*_executor/coaching_batch_executor，不得从新CLI调用任何live plan/preflight。教练生成调用纯gm_core现有propose_batch/validate_batch，同批原始块只由已有DataReader适配读取；分析输出不携带运行时指针。真实游戏计划仍由现有执行窗口负责。

M3B拟议调用：

```text
gm_decision.py begin --analysis-run A --mode development --output-context FILE
gm_decision.py submit-review --run D --input TEAM.json --expected-revision N
gm_decision.py submit-alternatives --run D --input OPTIONS.json --expected-revision N
gm_decision.py submit-offer --run D --input TERMS.json --expected-revision N
gm_decision.py respond-offer --run D --input RESPONSE.json --expected-revision N
gm_decision.py select --run D --input PORTFOLIO.json --expected-revision N
gm_decision.py validate --run D --expected-revision N
gm_decision.py finalize --run D --expected-revision N
gm_decision.py show --run D
gm_decision.py team --run D --team SAS [--players --limit 20 --cursor C]
gm_decision.py export --run D --output NEW_DIR
```

所有入口共用--workbench（派生库路径保护）及只读查询边界；run ID可推导career，若显式career不一致则拒绝。expected-revision针对decision_run，客户端得到新revision再继续；artifact revision由库分配。query只读，import/write不接受任意SQL。无网络模型API、无自动唤醒、无--approved或--execute入口。

export生成index/30队短摘要/选定动作与相应引用/恢复checkpoint，默认_exports；拒绝published/saves/query_snapshots/seasons。后续玩家授权正式归档时由角色把分析/提案文件提交到既有docs/gm_analysis和season节点，不新增自动发布器。原始数据库不上传。

## 7. Schema与运行检查的分工

Sol实现JSON Schema（draft2020-12）用于对象形状、必需字段、状态枚举和无批准字段；新增候选schema独立命名，不使旧V3schema失效。现有项目未声明jsonschema运行依赖：选择加入明确依赖或用纯Python校验器作为唯一运行权威，**不能文档称验证了schema但实际从未调用**。不同时维护两套不同业务规则。

跨文件的身份集合、M0来源、两方同terms_digest、当前run revision、资产与字段冲突由确定性业务校验完成，schema不能证明。叙述质量/篮球判断由GM与用户审阅，机器不做“内容够长就是正确”的伪评分。验证只覆盖本次直接业务行为，不增长成额外现金/伤病/游戏引擎验收项目。
