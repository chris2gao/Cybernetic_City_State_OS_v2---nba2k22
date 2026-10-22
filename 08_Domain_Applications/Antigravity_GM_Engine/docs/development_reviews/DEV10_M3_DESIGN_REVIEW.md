# DEV-10 M3 Astra设计审阅与交接

后续编码交付已完成本地工程验证，见[M3A验收](DEV10_M3A_ACCEPTANCE.md)及[M3B验收](DEV10_M3B_ACCEPTANCE.md)。本页保留Astra设计阶段审阅，不冒称已经进行独立的编码后Astra审查；正式V4仍未启用。

日期2026-10-19；基于main `7a60d5e`（末次fetch新增研究已合入设计分支，无运行源码变化）。结论：`ASTRA_M3_DESIGN_READY_FOR_SOL_IMPLEMENTATION`。本报告评审设计是否覆盖M3A/M3B及当前代码对接；**M3工程尚未实现，实际GM V4未启用**。

## 1. 原M3要求逐项对应

| 原要求/实际约束 | 设计证据与处理 | 当前完成层级 |
| --- | --- | --- |
| GM_DECISION_PACKET_V1，30队全员/统计/教练/财务/资产/市场/缺口 | [M3A](../development_tasks/DEV_20261019_10_M3A_DECISION_PACKET_DESIGN_V1.md) 1–7；prepare事实与import诊断区分，源身份集合验证 | 设计完整，待编码 |
| SQLite按需消费而非30份巨大JSON | M3A 2/3/7及[契约](../development_tasks/dev10_m3/CONTRACTS_V1.md) 5/6；新增已有team stats投影，固定批次/游标/小摘要 | 设计完整，待编码 |
| 实际staff/player pool可读证据 | source_access区分SQL筛选、实际返回、逐项评估；局部缺口只影响相应领域 | 设计完整，未运行真实访问演练 |
| 跨批表现、能力与合同变化 | 计数差分后重算；身份候选与确证分开；无poss/伤病/稳定键不伪造 | 设计完整，公式样例由Python计算 |
| 人才缺口与使用不当、现有/外部候选 | 全员供给+M2角色概念/实际字段映射，screen-market真实查询设计，三类方案 | 设计完整，待编码/GM判断 |
| 五个内部阶段、一次用户触发终稿 | [M3B](../development_tasks/DEV_20261019_10_M3B_GM_PROTOCOL_V4_DESIGN.md) 1/2/7；保存断点、全队深度、PARTIAL不冒充终稿 | 候选协议，不替换V3 |
| 30队独立利益/双方完整筹码接受 | M3B 3/4及契约Offer/Response；各自保留替代、同一terms版本、反报价撤销接受、NO_DEAL | 设计完整，待编码/GM判断 |
| 资产、合同、名额、三届签位、字段及执行范围 | M3B 5/6；候选竞争与selected冲突分开，同队交易/交易后战术依赖明确 | 设计完整；实际实时计划仍在独立执行窗口 |
| 唯一最终提案/精确批准清单 | M3B 6/7；教练纯离线真实生成器，交易仅待实时计划，外部approval不认可 | 设计完整，无实际生成执行批次 |
| 30队详细档案、策略候选、事前假设 | 契约TeamReview/Final/Hypothesis/StrategyCandidate；只显式保存，不推进正式策略 | 设计完整，当前30队仍UNASSESSED |
| BOOTSTRAP/SEASON_INITIALIZATION/CHECKPOINT | M3A上下文与M3B冷启动；新career不套旧MC/球队目标，跨季不直接差分 | 设计完整 |
| 三队V3/V4开发对照与后续全联盟 | [实现任务书](../development_tasks/DEV_20261019_10_M3_IMPLEMENTATION_HANDOFF.md) 3/4；三队真实静态钻取+合成30队全流程，不能冒称实局分析/网页验收 | 计划明确，未运行 |
| 启用V4与历史迁移 | M3B 8、任务书5；本地工程、实际Web使用、玩家切换分别记录，旧W03/V3保留 | 未启用，未来明确操作 |
| M4反馈接口但不实施M4 | hypotheses包含未来指标/反例，未执行回执保持null；不建后台监控/自动归因 | 设计预留，无M4工作 |

## 2. 与当前源码核对得到的关键修正

1. `gm_data_access/query.py`的q_teams没有投篮累计计数，但`database/schema.sql::team_source_stats`及`source_extensions.py`已有真实totals存储。M3必须扩已有只读投影，而不是要求新采集或让GM去读未开放raw表。
2. attributes的结构是`{raw,value}`，M2角色词不是字段名。M3A明确读取`.value`与实际原生field映射，防止角色筛选接口只存在于文档名词。
3. 旧`calculations.efficiency`只是算式，`roster_changes`用name+face并明确非永久身份。新设计不沿用它们的输出名来认证标准回合或确证成长。
4. M1`compare`可计算明确moves的成本/资产变化，M2Store可存版本化分析；复用这两层。研究无法认证的现金/额度不自动阻断当前已支持的普通转队研究，也不升级为真实签约空间。
5. 文档37与当前`approved_trade_executor.py`限定普通15槽、球队互不重叠批次且实时五人引用核验。设计显式限制同队串联交易和先交易后同批教练计划，不让“无资产重用”冒充所有执行条件都满足。
6. `scripts/coaching_batch.py`默认离线但导入执行器模块。新gm_core交接直接复用`gm_core.coaching_batch`纯生成/校验函数；严禁新决策CLI调用live preflight/plan。
7. 最新研究区分八个底层staff岗位与六个可任命UI岗位，并将实机竞技限定为3D赛场且排在M3之后。设计保留这些事实与优先序，未将训练/全局滑块/个人倾向/媒体世界纳入本阶段。
8. 收尾fetch取得原生控制发现清单：玩家已确认全局设置可修改，不要求重复定位；NC01–NC15新原生能力仍由独立研究验证后逐项接入。本设计不将研究清单当现成M3执行器。

## 3. 开发取舍审阅

本设计只增加实现M3核心路径所需的来源投影、派生对象和校验。没有强制所有数据语义先查清，没有固定额外实机测试或循环套用历史测试。cash、poss、FA资格、员工效果、持久身份等未认证事实在相关指标/动作保留UNKNOWN，其他能够完成的研究继续。

程序负责算术、身份/版本/冲突与真实交接材料；球队目标与篮球推理仍由GM负责。没有万能球员总分、固定队名文化、全联盟共用效用函数、自动模型派发或“文本够长算研究完整”的评分器。结构检查只能证明形式/来源一致，不能冒充经营判断正确。

## 4. 本轮实际做过的检查

- 只读核对正式main/PR #3交付与当前M0/M1/M2源码、现行V3/分析方法、执行器范围和最新研究。
- 生成[15个合成设计案例](../development_tasks/dev10_m3/DESIGN_CASES_V1.json)：含30个虚构球队的冷启动身份列表、区间计数算例、双边报价/冲突/依赖/版本/缺口/HOLD行为。数字由Python从显式合成输入计算。
- 文档链接/文件存在与git diff检查用于交接完整性；不是运行M3业务测试，也不证明未来CLI已实现。
- 没有读取实际SQLite数据、执行M02研究/正式GM、连接游戏、采集、发布游戏数据或修改事实；没有运行现金/Web/签约/比赛验证。

## 5. 交接结论

Astra设计包已覆盖原M3A/M3B目标和上述实际集成缺口，可进入约定的Sol编码阶段。M3工程验收须按实现任务书逐项给真实源码/CLI/测试/存储证据；不能以本报告或合成案例替代。M1/M2工程完成事实保留，当前30队仍UNASSESSED、GM V4仍未启用，M4与赛场/媒体研究未启动。
