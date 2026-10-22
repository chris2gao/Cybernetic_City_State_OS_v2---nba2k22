# M3B 候选GM决策工作台操作手册

2026-10-20增量：M3-T已在原PR #4接入正式main的DEV14，新增已脱敏原生事实、内部优先诊断、角色/目标分钟、个人防守/球员战术/训练/轮换及本队手册意图。完整新用法见[M3-T手册](GM_M3_TACTICAL_WORKBENCH.md)。新包必须通过potential_v1净化，旧M02与未脱敏缓存不供GM；本页P1–P5与交易协议继续复用。PR #4已按玩家批准合入main（504a4c0），V3生效、V4未启用。

协议ID为 `GM_V4_SINGLE_TRIGGER_INTERNAL_FIVE_PHASES`，状态DRAFT_NOT_ENABLED。当前V3继续生效。本工具在DEVELOPMENT_CANDIDATE模式保存研究和离线交接，不能直接启动正式GM、批准、写游戏或替换W03。分析包操作见[M3A手册](ANALYTICS_M3_WORKBENCH.md)。

## 1. 开始、查看与恢复

```powershell
python scripts/gm_decision.py begin --analysis-run A01 --run D01 --mode development --output-context _exports/D01_context.json
python scripts/gm_decision.py show --run D01
python scripts/gm_decision.py template --analysis-run A01 --team SAS
```

共用 `--workbench`、`--query-root`、`--published-root`，默认与M3A相同。begin要求封存分析包并检查固定静态来源。只支持development；调用者传FORMAL_ENABLED无效。可用 `--constraints FILE`绑定当前source_binding、protected_identities和context_evidence，仅能添加本局实际身份保护，不能授予执行权。不根据另一个career的名字自动保护人物。

template给出当前身份集合的review_template和三类alternatives_template，判断字段刻意为空，不能直接通过审议。取出各对象分别填入文件提交。球队以本批实际30个ID为准，5/10队分组只作内部保存粒度。

show返回各阶段完成/未完成队ID、当前revision、唯一final指针和报价状态。恢复时重读show，继续缺失球队；不依赖聊天自动记忆。所有写动作须 `--expected-revision`，冲突不会覆盖原数据。

## 2. P1逐队研究与P2比较方案

```powershell
python scripts/gm_decision.py submit-review --run D01 --input SAS_review.json --expected-revision 1
python scripts/gm_decision.py submit-alternatives --run D01 --input SAS_options.json --expected-revision 2
python scripts/gm_decision.py team --run D01 --team SAS
python scripts/gm_decision.py team --run D01 --team SAS --players --limit 20
```

review必填字段由template提供，主要约束如下：

- player_assessments与来源identity集合双向相等，每人含角色、保留/研究态度、自己的player证据、未知项及NORMAL/FOCAL深度。人数相同但换一人不能通过。
- 六维键为D1_STAFF、D2_TACTICS、D3_ROSTER_USE、D4_MARKET、D5_ASSETS_AND_DEVELOPMENT、D6_TEAM_IDENTITY_AND_MONITORING。每维包含conclusion/evidence_refs/unknowns/alternatives；可以对效果未知给有理由HOLD。
- competitive_window包含assessment/evidence_refs/alternatives。team_interest_profile包含目标窗口、本方证据、有序角色优先序、保留/出售/签位/合同风险条件、best_internal_alternative_id和转向条件。不自动设统一球员价值或套用历史球队目标。
- monitoring_hypothesis包含baseline_refs、mechanism_claim、alternative_explanations、expected_direction、observation_metrics、minimum_evidence_description、falsification_conditions、confounds。只记事前假设，不接受已执行回执。

alternatives含team_id和alternatives数组，HOLD/INTERNAL/MARKET三类都要有实质方案或明确非适用/阻塞理由。每项有alternative_id/category/status/problem/proposed_means/evidence_refs/benefit_hypotheses/costs_and_opportunity_costs/reversibility/counterevidence/change_conditions/selection_reason。status限VIABLE_CANDIDATE/RESEARCH/BLOCKED/NOT_APPLICABLE。best_internal_alternative_id必须指向本队INTERNAL项。

定量成本可以用finance_scenario_ref链接分析包所绑定M1运行中实际存在的情景。没有已认证老板预算或cash容量不影响篮球研究，不能把模型数值当可用额度。

需具体教练动作时在相应方案内加action：

```json
{
  "action_id":"SAS_TACTIC_01",
  "kind":"COACHING",
  "requests":[{
    "action_id":"SAS_DEFAULT_01",
    "team_id":25,
    "targets":{"POEOffense":2},
    "expected_effect":"填写有证据的适配假设、替代解释和观察条件"
  }]
}
```

以上为原M3B接口示例，不是当前球队建议。M3-T普通GM只允许不含PlaybookID的18项教练默认，指定对手仅PERSONAL_DEFENSE，OVERALL只读；不再使用scope=VS_OPPONENT_DEFENSE/OVERALL生成日常GM动作。当前T包的纯离线工件由DEV14适配层准备，个人防守、轮换及TEAM_BOOK_REBIND规则见[M3-T手册](GM_M3_TACTICAL_WORKBENCH.md)。19项原生读取能力继续保留。

## 3. P3独立报价、反报价与NO_DEAL

全30队P1/P2完成后才进入市场定案。先提交完整两队条款：

```json
{
  "offer_id":"O01",
  "team_ids":[25,29],
  "moves":[{"kind":"TRADE_PLAYER","source_identity":"从实际分析包取得","from_team_id":25,"to_team_id":29}],
  "conditions":[],
  "dependency_ids":[]
}
```

```powershell
python scripts/gm_decision.py submit-offer --run D01 --input offer.json --expected-revision N
python scripts/gm_decision.py artifact --run D01 --kind OFFER --artifact-id O01
```

普通球员交易保持合同；简单签位用kind=TRADE_PICK和asset_id，必须为本批实际持有且在未来三届范围。多队/保护/互换或先签后转卖不变成执行包。

工具分配terms_revision，并按来源、排序后的队/资产动作/依赖及原序conditions计算terms_digest。展示文字和状态不入digest。这个摘要仅绑定报价，不是数据同步hash检查，也不是玩家批准。更改条款时重新submit-offer，旧接受失效。

每方分别提交响应：

```json
{
  "response_id":"O01_SAS",
  "offer_id":"O01",
  "terms_revision":1,
  "terms_digest":"复制工具刚生成的真实摘要",
  "responding_team_id":25,
  "team_interest_revision":1,
  "stance":"ACCEPT_IN_PRINCIPLE",
  "rationale":{"gain":"本队得到什么","cost":"本队付出什么","opportunity_cost":"放弃何种内部/外部替代","why_better_than_hold":"为什么优于保留"},
  "alternative_refs":["internal:25"],
  "conditions":[],
  "evidence_refs":["team:25"]
}
```

```powershell
python scripts/gm_decision.py respond-offer --run D01 --input SAS_response.json --expected-revision N
```

team_interest_revision为该队TEAM_REVIEW工件revision，不是全局run revision。程序还绑定当前替代方案revision；P1或P2变化后旧接受需重新提交。双方同版同digest接受才AGREED_IN_PRINCIPLE。新条件须COUNTER；REJECT对应NO_DEAL，NEEDS_EVIDENCE可保留研究。模型不得代填“对手肯定同意”，独立性是各队利益和理由的独立，不冒充调用了30个模型。

## 4. 选择可共存组合

select输入：portfolio_id、selected_offer_versions、selected_internal_action_versions、research_action_ids、holds、rejected_alternatives、team_combination_reviews。

research_action_ids引用已存方案的alternative_id或其action_id，程序会把实际研究事项带入终稿；不能填写无法解析的研究ID。rejected_alternatives引用真实方案并说明否定理由。其余未选方案保留原研究理由与工件revision，选中的HOLD不会被写成被否定假设。

```json
{
  "portfolio_id":"P01",
  "selected_offer_versions":[{"offer_id":"O01","terms_revision":1}],
  "selected_internal_action_versions":[{"team_id":0,"alternative_id":"internal:0","revision":1}],
  "research_action_ids":[],
  "holds":[{"team_id":1,"reason":"有来源的保留理由","evidence_refs":["team:1"]}],
  "rejected_alternatives":[{"alternative_id":"market:1","reason":"为何不选"}],
  "team_combination_reviews":[]
}
```

这里是结构示例，提交时必须让本批全部30队被动作或有理由HOLD覆盖。internal ref的revision是本队ALTERNATIVES工件revision。不能同时给同队HOLD和选定动作。候选可以竞争同一资产，选定组合不能重复出售。同一owner/opponent/field不同目标阻止终稿；相同目标合并生成而保留原方案理由。

同队多笔交易即使资产不同仍超出现有执行批次范围，转为DEPENDENCY_UNSUPPORTED研究；同二队可重新议成一个完整包。交易后同队教练方案标POST_TRADE_COACHING_REPLAN_REQUIRED，等待玩家另触发更新/重新计划；不复用旧roster signature自动串执行。

同队多个承诺需team_combination_reviews元素，含team_id/selected_ids/team_interest_revision/why_better_than_hold/evidence_refs，比较整个组合与保留。程序复用M1重算选定交易moves的组合成本；未知的常规/双向分类留给独立实时交易计划，不把观测总人数当15常规槽认证。

## 5. P4离线准备与P5终稿

```powershell
python scripts/gm_decision.py select --run D01 --input portfolio.json --expected-revision N
python scripts/gm_decision.py validate --run D01 --expected-revision N
python scripts/gm_decision.py finalize --run D01 --expected-revision N
```

validate生成本地确定性报告，调用者不能提交valid=true或伪digest替代。报价/组合/球队研究变动使先前验证和final指针失效；修订后重新validate。PARTIAL保存断点，不能finalize。

交接分开analysis_status、rule_check、financial_evidence、executor_readiness、approval_status：

- 普通交易仅SPECIFIC_TRADE_INTENT，REQUIRES_LIVE_TRADE_PLAN；不会调用会打开游戏的live plan/preflight。
- 教练调用纯gm_core生成器，读取同批teams.json和必要owner文件，保存真实batch、dry_run、gm_verdict、action_ids和digest。离线准备完成仍需另行玩家批准。
- 签约/合同变更、员工任免、训练、精确分钟或本阶段没有的操作只在研究列表，BLOCKED_EXECUTOR；不会用INTERNAL标签绕过。
- 现金/FA资格未知不阻止普通受控交易研究，也不等于获得签约额度。没有审批字段可授权游戏写入。

finalize原子追加不可变终稿并设置唯一current_final_version，旧版可查。全30队有理由HOLD是有效终稿；不要求达成交易。包含30队摘要、具体批准事项、研究/HOLD、舍弃理由、未来观察假设与M2策略候选。候选遵守现有M2schema，通过显式M2 save才写分析状态；finalize不逐队修改正式策略。

## 6. 有界查询、历史与导出

```powershell
python scripts/gm_decision.py artifact --run D01 --kind FINAL --artifact-id final
python scripts/gm_decision.py artifact --run D01 --kind FINAL --artifact-id final --artifact-revision 1 --section team_summaries --limit 5
python scripts/gm_decision.py artifact --run D01 --kind VALIDATION --artifact-id current --section generated_artifact_refs.0.batch.actions --limit 5
python scripts/gm_decision.py export --run D01 --output _exports/D01_handoff
```

artifact默认只列顶层字段与子项数；--section按存储工件的点路径/数组索引钻取。所有列表默认20、最多50并有字节预算，继续传cursor。不提供无界数据库或全人物JSON服务。

导出只写明确的新目录：索引/checkpoint和当前终稿的小摘要、选定事项、假设、策略候选及实际离线工件；保留详细研究在工作台按需读。输出为候选分析，不能当执行回执、网页验收或GM V4启用。GitHub提交、正式赛季归档、真实经营、M4反馈均由后续明确任务触发。
