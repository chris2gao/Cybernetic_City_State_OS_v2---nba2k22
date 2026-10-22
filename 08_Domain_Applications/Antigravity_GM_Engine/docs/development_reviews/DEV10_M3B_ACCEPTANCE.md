# DEV10 M3B 本地工程验收与交接

日期：2026-10-19。结论：`M3B_LOCAL_ENGINEERING_COMPLETE`，协议仍 `DRAFT_NOT_ENABLED`。现行V3、W03、GM_CURRENT、赛季INDEX不变。入口：[GM手册](../../web_gm/manuals/GM_M3_DECISION_WORKBENCH.md)、[M3A验收](DEV10_M3A_ACCEPTANCE.md)。

## S4–S7 实现审计

| 阶段/要求 | 当前源码与实际证据 |
| --- | --- |
| P1全队研究与恢复 | begin绑定sealed analysis、批次/赛季/context、M1/M2版本；mode仅development。逐队精确全员评估、六维、证据、独立兴趣与观察假设，部分状态可恢复；替换同人数另一身份会被拒绝 |
| P2真实替代方案 | 每队HOLD/INTERNAL/MARKET均有问题、手段、收益假设、成本/机会、反例、转向条件、理由。best_internal引用实际方案；未完成/过时P2不进入联盟定案 |
| P3独立报价 | 具体两队/当前资产/条款/依赖由程序绑定；单一规范函数产生terms digest；双方同版接受、各自兴趣与替代方案revision、机会成本/为何优于保留均独立记录。改条款或P1/P2变化使旧接受失效；REJECT明确NO_DEAL，COUNTER保持谈判 |
| 候选竞争/组合选择 | 相同资产可出现于不同候选，选中才检查唯一支出；同字段不同目标阻塞，重复同值合并。同队不同交易标执行范围依赖；同队多承诺要求组合比较，不把单笔接受当全部组合接受 |
| P4财务与执行准备 | 当前M1 run重算选定moves组合成本；cash/CBA/FA未知不冒充容量。普通交易仅SPECIFIC_TRADE_INTENT/REQUIRES_LIVE_TRADE_PLAN；同队串联/交易后教练计划/未实现业务保留研究，不能进入立即执行清单 |
| 真实离线教练交接 | 直接调用gm_core.coaching_batch纯生成/验证；固定同批teams及必要owner文件；保存实际batch/dry_run/gm_verdict/action_ids/digest。伪摘要和外部批准被拒绝；没有导入scripts/coaching_batch.py或执行器 |
| P5唯一终稿/历史 | 全30队研究覆盖+当前程序validation才能finalize；30队全HOLD合法，PARTIAL不得冒充FINAL。final事务原子写入并更新单一current pointer，旧版不可覆盖；组合变化清除旧current并需重验 |
| 策略与后续观察 | 每队M2 schema候选带base/expected_revision及明确分析状态；不自动save正式策略。假设保留反例/观察指标，execution_receipt_ref=null，不实施M4归因或反馈引擎 |
| 入口与输出 | begin/template/submit-review/submit-alternatives/submit-offer/respond-offer/select/validate/finalize/show/team/artifact/export可用；列表有界、section逐层钻取，导出仅显式新派生目录 |

策略候选中的PROPOSED/RESEARCH/HOLD都是分析状态，不能授予游戏执行权。程序只能校验形式、来源和确定性冲突，不能证明主观篮球判断公平；不存在统一联盟效用、自动球员总价值或虚构30个模型调用。

## 本轮实际验证

15项直接M3检查通过，并对最后受影响路径做定向检查。明确覆盖：双边同价/反报价/旧接受、候选竞争与所选资产冲突、同队不同交易范围、组合复核、精确名单、部分员工缺口、M1/M2旧行可读写、乐观revision冲突、唯一final/不可变历史、封存市场补充、真实离线教练与伪digest、交易后教练重计划、财务净变化、外部批准拒绝，以及研究事项/未选理由进入终稿、已选HOLD不被误记为被否定假设。

全合成30队使用独立静态M0测试副本，实际CLI完成：prepare→import-analysis→seal→begin→逐队30份review+30份alternatives→select(all HOLD)→validate→finalize→team/artifact分页→export。合成run=`SYNTHETIC_853e7e6a`，decision=`SYNTHETIC_DECISION_853e7e6a`。它产生30队摘要、30份策略候选、30份事前假设、一个current final；实际30队评估仍0。与真实M02部分合计89次CLI调用，均成功；冲突/重议/终稿修订另由同一业务层的合成检查证明。

另外，已有M02真实同批教练JSON经纯离线生成器实际生成了一个明确标DEVELOPMENT_CANDIDATE的GSW默认项技术包，并验证真实digest；只证明源码/codec交接，没有游戏访问、篮球效果或批准。工件在 `_exports/m3_acceptance_853e7e6a/m02_offline_coach.json`，不提交执行日志或SQLite。没有用模型自报digest替代生成器。

最后受影响检查还实际运行了template和已有终稿show两个CLI；核对12个新增Python文件的语法/导入与9个手册/验收链接，并通过新适配器读取GSW同批29个owner对手记录，调用现有纯生成器完成一个指定对手整体防守技术包校验。没有打开游戏。`_exports/check_m3_delivery.py`结果为M3_DELIVERY_CHECK_OK。

收尾另用6次合成CLI调用修订同一节点：保留v1、select/validate/finalize生成唯一current v2，查询60个未选方案理由，并把一个明确研究事项带入终稿后导出。结果M3_FINAL_REVISION_PASS，见同目录revision_report.json；实际球队未被研究或修改。研究ID必须解析到真实已存alternative/action，M2候选的rejected_hypotheses只保存明确否定项，不能把选中的HOLD也列为被否定。

最后资产字段核对补充：球员动作只接source_identity，签位动作只接asset_id，拒绝两类身份字段混填；selected资源键也按动作类型确定，防止混合ID掩盖同一资产。受影响的bilateral/candidate_competition两项定向检查通过。

## 15个原设计案例对应

| 设计案例 | 本轮对应证据 |
| --- | --- |
| A_INTERVAL_METRICS / A_ZERO_AND_REGRESSED_COUNTER / A_TEMPORAL_IDENTITY | counter_deltas检查：先差计数、0场/负增量、候选/歧义不确证成长 |
| A_IDENTITY_NOT_COUNTS / A_PAGED_ACCESS | exact_identities和byte_limited_consumption；真实三队逐页精确集合 |
| B_COLD_START_30 | 合成CLI完整P1–P5；无正式策略升级 |
| B_INDEPENDENT_INTERESTS / B_COUNTER_RESETS_ACCEPTANCE | bilateral检查、每方当前利益/替代版本与完整理由 |
| B_CANDIDATE_VS_SELECTED_CONFLICT / B_EXECUTOR_TEAM_OVERLAP | 两个候选可并存；selected资产冲突阻塞，同队不同资产交易转研究 |
| B_TRADE_COACH_DEPENDENCY / B_FINANCE_UNKNOWN_SCOPE | post_trade检查与实际M1组合计算；cash未知不阻断普通交易研究 |
| B_STALE_REVISION_AND_FINAL / B_NO_DEAL_VALID_HOLD | atomic检查保留旧final、单current pointer、冲突不覆盖；全HOLD CLI终稿、REJECT→NO_DEAL |
| B_PREPARATION_IS_NOT_APPROVAL | 批准/伪digest拒绝、离线真生成、所有终稿NOT_GRANTED/false |

## 同期Antigravity操作影响

只读Git证据确认：正式main与origin/main当次均为`9b4fe87`，reflog显示其DEV12提交曾rebase后推入main。该提交仅新增7个文件（四个src模块、知识配置、研究文档和测试），不改M3开发分支、现有M0/M1/M2接口或本工作区未提交内容。M3分支仍以`c3ce332`设计为前任，当前实现没有导入这些DEV12模块，因此无需撤销它来完成本任务，也未替该工作进行验证/验收。

## 交付边界

本工程交付在PR #4开发分支，尚未合并或部署正式main。当前30队策略仍UNASSESSED；合成研究不替代实际经营。网页连接由玩家后续建立，cash实测、实际签约、比赛/保存重启继续延后；GM V4须玩家另行启用，M4未启动。没有改游戏、观测事实、published、既有V3规则或正式赛季档案。
