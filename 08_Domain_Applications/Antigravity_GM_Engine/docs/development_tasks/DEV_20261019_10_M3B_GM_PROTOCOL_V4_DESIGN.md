# M3B — GM_DECISION_PROTOCOL_V4 候选设计

实现补记：候选协议的本地工程已完成，见[GM手册](../../web_gm/manuals/GM_M3_DECISION_WORKBENCH.md)和[M3B验收](../development_reviews/DEV10_M3B_ACCEPTANCE.md)。DRAFT_NOT_ENABLED仍是实际启用状态，工程完成不替换V3。

状态`DRAFT_NOT_ENABLED`。protocol_id=`GM_V4_SINGLE_TRIGGER_INTERNAL_FIVE_PHASES`。现行`GM_DECISION_ROUNDS_V3.md`仍是生效规则；本设计不替代其玩家逐轮触发要求，不更新W03/赛季索引/GM_CURRENT。

## 1. 产品目标和工作方式

玩家在同一赛季聊天触发一个经营节点后，候选V4允许GM在任务内完成五个内部阶段，再给唯一终稿。每阶段成果存派生工作台，过程可恢复；不是要求玩家依次输入五次“继续”。常规目标一次完整回复，修改/复杂情况最多3次为体验目标，证据或上下文不足时交付明确PARTIAL与断点，不硬称完成。

一个GM节点锁定career、season、game_date、current batch、sealed analysis run、知识版本、M1 run与M2策略revision。source发生变化时旧研究保留，进入SOURCE_CHANGE_REBASE_REQUIRED；重新准备受影响的事实/方案/接受记录，旧终稿与旧摘要不能沿用审批。新数据出现不自动触发新GM。

内部分组可用10队或5队作处理与保存单位，覆盖集合从本批实际30队取得，不能硬编码旧赛季分组当联盟成员。分组只是任务内部恢复粒度，不改变每队深度。每队完整在队身份集合必须与当前事实一致；机器计数通过不证明判断质量，正文证据和替代方案仍须GM自己形成。

## 2. 内部五阶段与可恢复产物

| 阶段 | 必须完成的工作 | 持久产物/推进条件 |
| --- | --- | --- |
| P1 研究30队 | 读取packet及来源缺口，逐队全员、员工、教练、合同/签位与长期状态；提出问题和目标 | team_reviews含实际人物评估和六维；每队COMPLETE/REWORK_REQUIRED/BLOCKED，未完成团队计数真实 |
| P2 比较方案 | HOLD、INTERNAL、MARKET三类逐队比较；确定独立保护线、可谈条件和机会成本 | alternatives、team_interest_profile；每类有实质方案或明确NOT_APPLICABLE/BLOCKED理由 |
| P3 独立市场与联盟整合 | 双方按自己的P2判断谈完整报价；报价/反报价/拒绝；选择可共存方案 | negotiations含各方对同版条款判断；selected portfolio、被舍弃方案理由；NO_DEAL合法 |
| P4 程序复核与执行准备 | 核对来源、身份、覆盖、选定资产和字段冲突、依赖、M1情景、执行范围；离线生成教练批次 | validation report及可复用生成物；分离invalid、研究缺口、待实时计划，不把任何缺口统统当fatal |
| P5 唯一终稿 | 30队摘要、动作与HOLD、每方理由、成本/风险、精确批准事项、未来观察目标 | immutable final revision、action hypotheses、strategy candidates与断点索引；只有一版CURRENT_FINAL_PROPOSED |

P1/P2可在单队内部交错深入，但P3定案须全联盟P1/P2达到可审议状态。局部员工HOLD可以完整审议，整队未读取名册不能记COMPLETE。P4失败回到受影响阶段修订，不重做无变化球队；程序只能报告结构/事实矛盾，不能自动编理由替GM补齐。

中断时工具报告完成的球队、未完成团队/阶段、最后保存revision、待回答问题。恢复前重读run和版本；模型不得用聊天记忆跳过磁盘状态。不中断任务创建其它聊天/模型，也不后台自动派发。

## 3. 每队需要怎样的判断

新的M3 review对象复用现有`GM_TEAM_DECISION_CONTRACT_V1`的业务要求，增加run/ref/版本映射；保留原schema供V3。代码负责current source identities与player_assessments集合精确相等；姓名相同但不同identity不能合并。人物可短评，但至少有本局角色、保留/研究态度、关键证据及未知项。明星/候选/显著使用问题加深解释。

六维必须回答，允许按事实缺口HOLD：

- D1_STAFF：真实岗位/人员/证据和留用或研究理由。八个原生关联不伪装八个可任免UI岗位；玩家确认六岗另列。效果公式、任免写入未确认时无员工操作批准项。
- D2_TACTICS：阵容技能供给、当前19项及相关对手整体设置的适配；篮球逻辑与替代解释；不保证效果。目标字段只有通过既有离线生成器才进入正式操作包。
- D3_ROSTER_USE：持球/无球、攻防互补、主替补机会、自然成长与负荷背景；个人分钟由AI，缺伤病疲劳数据不造数，精确轮换/训练只保留研究缺口。
- D4_MARKET：外部补强是否有必要？相比HOLD/内部改善解决什么？卖方为何愿意？FA身份未认证的非在队模型仅SCOUTING，不升级可签约球员。
- D5_ASSETS_AND_DEVELOPMENT：合同窗口、当前阵容角色、未来三届简单签位、保留核心/年轻人的代价与机会；潜力不当OVR，slot投影不当保证义务。
- D6_TEAM_IDENTITY_AND_MONITORING：本局目标、证据与可反驳条件，慢变量保留历史来源；现实/历史线参考适用年登记，不制造命定冠军或名人必须回现实母队。

每队`team_interest_profile`是该队独立、可修订的经营政策：窗口与证据、角色优先序、核心保留阈值、可售条件、签位使用条件、合同风险承受条件、内部替代、策略转向触发。不设全联盟统一总估值公式；可比较同队方案的角色增益、时间窗口、薪资负担与资产损失，所有数值来自M1或确定性计算。

`gm_policy.json`仍DRAFT时，不把生命周期阈值/名字保护清单自动当生效规则。玩家针对当前career已明确的MC保护或限制需单独绑定实际身份和指令来源；新档不继承别局人名特权。历史重力人物定制不在M3中实施。

## 4. 独立议价：同一个模型也必须分别回答两方问题

首版以二队普通球员/简单选秀权交易为可准备范围；多队包、同队串联再转卖或签后再换可以留研究，但不借“全联盟优化”扩现有执行器。

完整proposal terms包含source binding、参与队、逐项asset身份/原持有/目标、合同语义（普通交易保持合同）、所有条件、明确的前置依赖。`terms_revision`递增；程序规范化排序后生成`terms_digest`。此digest只绑定业务报价，不参与游戏数据同步哈希验收，也不能代表人类批准。

各方独立提交`stance`：ACCEPT_IN_PRINCIPLE/REJECT/COUNTER/NEEDS_EVIDENCE，并附本方P2引用、获得的角色/时间价值、付出及机会成本、保留替代、可推翻条件。程序校验双方均对**相同terms_digest**接受；有一方反报价、条款变更或缺席，协议回到NEGOTIATING。单字段`bilateral_accepted=true`不算两方记录；不得由买方填写“对手一定同意”。

独立性是利益与理由的独立，不假装调用了30个真实模型或人类经理。机器可以验证双方记录、引用、条款一致和冲突；不能证明主观理由公平。因此最终报告必须能让玩家看到每方“为什么胜过保留”，而非输出一个算法公允分数。

候选可以同时竞争同一球员/签位：候选层标竞争关系，不能禁止提出替代方案。**选定组合**才要求无重复支出；两份相互排斥备选不可同时列入批准清单。谈不拢或最优内部替代更好，明确NO_DEAL/HOLD，无成交数量KPI。

联盟整合步骤：

1. 过滤本局规则禁止/来源错误的候选；技术待验候选留研究清单，不悄悄删除价值分析。
2. 只将双方同版接受的二队条款作为可选择交易候选。
3. 列资源冲突与各队可承受承诺；GM依据各队独立比较选择一致组合，不能最大化一个联盟统一效用而牺牲某队。
4. 组合改变任何一队的角色/阵容、工资或签位条件，重算关联M1情景、人物/战术假设并重新取得该方对最终条款的接受；不能把针对单笔的接受当成对累计多笔的同意。
5. 无同时可行组合时保留HOLD/内部优化或挑选较有证据的方案；其余说明未选理由。

每轮反报价应有新信息或实质让步；研究预算可配置为默认最多2次counter/re-prompt后交NO_DEAL/NEEDS_PLAYER_DIRECTION，属于交互预算，不是CBA或球员价值规则。用户明确要求深入时可提高，不能因此编造接受。

## 5. 跨动作冲突与依赖

| 情形 | 检查和处理 |
| --- | --- |
| 同球员/签位进入两笔选定交易 | 相同source-bound资产唯一支出；报冲突，GM选择一种 |
| 两笔不同资产交易涉及同队 | 经济上可能可行，但当前执行批次要求球队互不重叠。能合为同二队单一包时重新谈完整包；其余DEPENDENCY_UNSUPPORTED，不能虚构串行执行已支持 |
| incoming球员再次卖出、先签后换 | 来源持有不成立/序列依赖；首版不生成执行清单，只留研究 |
| 同owner/opponent/field不同教练目标 | 字段资源键冲突；同值可以合并但保留两条理由，重生成最终batch/digest |
| 交易后阵容改变教练适配 | 标依赖；原批教练快照/roster signature不能直接当交易后计划。输出先交易、再玩家触发更新和重新计划的条件，不自动串采集/执行 |
| 财务/名额 | 合并选定moves重算M1净变化；缺常规/双向分类则待实时计划，不拿观测全名单直接证明≤15常规槽；本轮不补写释放/裁员 |
| 历史线或受保护人物 | 按本career玩家规则与实际身份检查；现实名气/历史叙事不覆盖观测或任意造批准 |

冲突检查对候选返回图/原因，对selected返回阻止形成相应可批准操作包的错误。HOLD和RESEARCH可以进入最终说明，但不是执行action。

## 6. 财务与执行状态：保留可做事项

分开五个字段：analysis_status、rule_check、financial_evidence、executor_readiness、approval_status。不得用一个`valid=true`暗示五项都通过。

- cash、工资帽/税线、签约额度未知：成本研究照常；任何声称有可用额度/法定CBA合规的结论必须UNKNOWN。当前受控普通交易保留合同、不要求新增现实CBA规则；不能为缺cash一刀切阻止所有已支持交易研究/具体审批准备。
- 普通交易：可生成`SPECIFIC_TRADE_INTENT`，准确列当前source-bound球员/签位与双方理由；执行准备`REQUIRES_LIVE_TRADE_PLAN`。M3不得调用execute_approved_trades的plan，因为它会打开游戏读取。实际批准后的执行窗口重新解析身份、合同原值、常规容量及五人引用组。
- 签约/合同替换/延期：M1可算成本，当前写入开关未验证；输出`BLOCKED_EXECUTOR`与批准讨论所需条件，不能混入“立即可执行”清单。
- 教练：离线使用gm_core.coaching_batch及同批原始教练快照/选定owner文件生成batch/dry_run/gm_verdict。真实生成结果的完整action_ids/digest进入精确批准摘要；没有生成物就EXECUTION_PREPARATION_PENDING。gm_core不导入coaching_batch_executor；模板名或模型自报digest不成立。
- 员工任免、精确个人分钟、训练、人物能力/倾向、全局Gameplay：本阶段没有对应批准执行包。分别RESEARCH/HOLD或规则禁止；不能借标签“INTERNAL”绕过。

最终“需要玩家决定”可以列具体交易商业条款与已离线生成的教练操作两类；明确各自后续计划条件。所有M3记录`approval_status=NOT_GRANTED`、`execution_authorized=false`，源代码验证不创建玩家批准。现有具体批准/执行流程不因V4改变。

## 7. 终稿、策略候选与下一次观察

终稿包括：绑定来源/协议版本，30队完成摘要，选定动作及双方比较，具体批准事项，未选方案/HOLD与缺口，未来观察信号。玩家默认看到动作/理由/代价/条件和30队一行摘要，详细人物/完整报价/方法按引用钻取。

每个action hypothesis：假设、支持证据、替代解释、方向性预期、机会成本、可推翻条件、下次观察指标及所需新数据。没有数据支持时不给量化胜场增益。未执行动作不得归为实施；M4以后再做执行与后续观测配对，本轮只保留接口。

生成M2策略**候选**revision，附base_state_id/expected_revision/新来源与change_reason/rejected_hypotheses；没有已研究策略就从UNASSESSED冷启动，不能空壳改为REVIEWED_ANALYSIS。采用M2已有显式save，不由finalize悄悄逐队改正式策略。保存REVIEWED_ANALYSIS仍不代表玩家批准或游戏变更。

finalize必须有完整30队审议或明确PARTIAL结果；只有完整节点可产生CURRENT_FINAL_PROPOSED。旧final不可覆盖；修订新version并使旧版SUPERSEDED，旧批准不得自动迁移。派生库事务原子更新当前final指针，避免两个可批准“最新版本”。

## 8. 候选接口、权限和实际启用

拟议入口`gm_decision.py`：begin/show/team/submit-review/submit-alternatives/submit-offer/respond-offer/select/validate/finalize/export；参数和事务见[契约](dev10_m3/CONTRACTS_V1.md)。它们保存调用方判断并做确定性校验，不调用模型、不自动生成经营意见、不连接游戏。

开发时`mode=DEVELOPMENT_CANDIDATE`，产物只在_exports/独立开发workbench；新协议文件位于此设计包。正式V4启用需：本地实现与相关验证完成、玩家建立真实Web连接并实际消费、玩家明确批准协议切换。连接推迟不阻塞工程与本地演练，不能把演练称为网页验收。

后续切换任务需统一更新GM/ANALYTICS基线、GM SOP、docs35、schema入口、GM_CURRENT及赛季索引。V3文件保留历史并添加superseded说明；W03旧档仍按当时规则解释，不重写成V4已完成。现行赛季聊天生命周期仍一季一个聊天，Wxx是节点；当前未完V3节点若要迁移，必须明确从哪个节点/阶段开始，不能默认续跑已过时的R01候选。
