# M3A — GM_DECISION_PACKET_V1：可查询的决策准备包

实现补记：当前本地工程已完成，实际命令以[分析手册](../../web_gm/manuals/ANALYTICS_M3_WORKBENCH.md)和[M3A验收](../development_reviews/DEV10_M3A_ACCEPTANCE.md)为准。以下保留原设计，非当前“未实现”状态。

状态`DESIGN_READY_FOR_IMPLEMENTATION`；命令与表均是待实现设计。总入口见[M3](DEV_20261019_10_M3_DESIGN_AND_IMPLEMENTATION_ENTRY.md)。基于DEV10 V2的SQLite消费方式，替代V1中“每队一个大JSON”的存储建议；保留V1全队/全员研究深度。

## 1. 输入与一次运行

输入：明确career、当前batch、season、node类型（BOOTSTRAP/SEASON_INITIALIZATION/CHECKPOINT）、可选previous_batch、可选M1 finance_run、可选M2策略revision、调用方提供的定性分析。所有事实固定在M0通过审计的静态双库；不直接读database/saves，不自动采集，不根据今天日期推断游戏时间。

analysis_run固定current SourceBinding与可选previous SourceBinding、代码commit/计算版本/知识版本/上下文来源。previous必须显式给出或由索引列候选后明确选择，不能随便选“latest之前一个”假设同一历史分支。season或历史连续性无证据时记录CONTEXT_REQUIRED；仍可交付当前单批事实，区间差分禁用。M1当前需要显式base_season，沿用该约定。

prepare动作生成**事实与计算草稿**：全队、每名名单球员、教练、工资/签位、访问证据、指标与缺口。不会凭代码生成生命周期结论、交易动机、人物保护线。ANALYTICS显式提供诊断和研究方向后，`seal`才产生不可变的ANALYSIS_ONLY packet；未填定性分析保持FACTS_PREPARED，不把“脚本跑完”说成30队已分析。

## 2. 必要的来源投影扩展

当前`q_teams`只有球队ID、W/L/G/win_pct/total_salary；已有`team_source_stats.totals_json`包含球队投篮等计数，但不在M0可查询投影中。新增`q_team_stats`，并在DEFAULTS/JSON_FIELDS/可用性描述/CLI帮助中登记：

```text
team_id, team, season_year, totals (JSON), source_status
```

SQL从静态facts.team_source_stats按snapshot_id过滤，与同批team_monthly_stats按team_id关联。只暴露totals_json，不暴露raw_struct、进程地址。旧快照缺表/缺队返回SOURCE_UNAVAILABLE或局部缺行，不能拼接别批。`source_status`由已有manifest/表观测事实得出，不由模型自报；新增投影不是新的采集能力。

复用其余投影：

| 领域 | 读取字段与用途 |
| --- | --- |
| players | identity/name/team_id/team/position/birth_date/face_id/pool_slot/attributes/contract/season_totals；全员当前供给与身份 |
| pool | identity/slot_id/name/position/roster_status/historical_rookie/attributes/draft信息；查询候选，不认定FA资格 |
| staff | identity/team_id/role/mapping_status/attributes/salary/years_left；实际岗位及候选，不编造效果 |
| coaching | 每队19 values/system/freelance/sliders/readiness；同批字典另按M2入口读取 |
| defense | owner/opponent/values/mixed_fields/status；按需查询重点对手，非870组全文预载 |
| picks | asset_id/owner/original_team/draft_year/round/trade_eligible；简单签位与三届窗口 |
| finance + semantics | 原始字段及解释；M1情景链接，不把cash差值计算为签约能力 |

名册常规/双向类型当前q_players未提供认证分类。M3不能把所有观测名单人数当regular_count，不能只凭two_way_days_left猜分类。名单净变化可算；常规15槽的精确可执行性仍由后续独立实时计划核对，不为M3新增内存采集。

## 3. 访问证据与覆盖：证明实际读了什么

适配层按M0游标消费小页（最多50、现有字节预算不变）。大属性页可能不足50行，必须跟随next_cursor，不能按返回行数猜“读完”。source_access记录每次实际查询的entity/字段/过滤条件/批次/返回数/耗尽状态与错误；数字由工具产生，不接受模型填写`read_all=true`。

prepare实际消费30队及**来源中的实际全名单身份集合**，固定到派生run；人数不写死为466。对每名身份存必要能力/合同/表现引用与缺口；0场或缺stats不省略人物。完成名册读取与完成GM人物评估是两个独立计数。

staff/pool至少执行有界聚合与具体验证行查询，证明确实可访问；按岗位/能力/身份筛选候选时记录筛选条件、总匹配数、返回身份、未展开范围。SQL筛选整个池只证明`QUERY_SCREENED`，返回条目才是`RECORDS_READ`，逐项讨论才是`ASSESSED`。不要求把1458员工/3383模型全载到模型上下文，也不允许仅复制manifest数量声称全池研究。

状态轴：AVAILABLE/QUERY_FAILED/SOURCE_UNAVAILABLE/NOT_REQUESTED；单独记录SCREENED/READ/ASSESSED数量和是否全部穷尽。blocked_scope列受影响的员工/市场/指标。员工无法访问可以使员工维度HOLD，不阻止其他已读维度；当前名单身份或当前批次不可认证时，对应球队不能标完成研究。

开发脚本真实运行仅证明LOCAL_CLI_RUN；Web自检必须由其实际会话运行并返回实际工具/查询记录，不能继承本地回执假称WEB_CONSUMER_VERIFIED。

## 4. 指标：先保留分子分母，再讲篮球

统一Metric对象：value/unit/basis/current_or_interval/formula_version/inputs/source_refs/sample/unknown_reason。OBSERVED为原始计数；确定性结果CALCULATED；估计量HEURISTIC；定性结论INFERRED。不将null填0，0分母返回UNKNOWN。

原生字段与公式：

| 输出 | 原字段与公式 |
| --- | --- |
| games / record | w+l；W/L来自同批team stats，并与球队摘要的相同口径对应 |
| efg | (made + 0.5 × 3pt_made) / attempted |
| three_attempt_rate | 3pt_attempted / attempted |
| two_point_pct | (made−3pt_made)/(attempted−3pt_attempted) |
| three_point_pct | 3pt_made/3pt_attempted |
| free_throw_attempt_rate | free_throws_attempted/attempted |
| turnover_estimated_rate | turnover/(attempted+0.44×free_throws_attempted+turnover)，估算定义不冒充实测回合 |
| assists_per_turnover | assists/turnover；0失误不输出Infinity |
| ppg / allowed_ppg / margin_pg | points/G、pa/G、(points−pa)/G |
| rebounds_per_game | offensive_rebounds/G、defensive_rebounds/G；对手对应分母缺失不造ORB% |

对手投篮指标只在字段profile/现有认证明确其含义时使用，不从ofga等名字猜测。口径证据缺失则该指标UNKNOWN，同时保留可用points_allowed。poss保持原始字段，不调用旧efficiency便直接冠名ORtg/DRtg；标准攻守回合口径未确认时不发布标准百回合指标。M3不追加poss实机调研或全量原生字段实验。

区间：先对**可比较累计计数**逐字段做current−previous，再代入公式，绝不相减百分比。同career/season/历史分支，游戏日期与来源次序可解释，场次不回退。负计数或不一致仅影响相关字段/球队区间，生成局部NON_COMPARABLE理由；不顺手推翻仍可信的当前累计事实。0新增场次为NO_NEW_GAMES，合同/名单仍可能变化，不能除以0或称比赛效果。区间称“两个检查点之间”，不假装有逐场或整月数据。

样本展示真实G/FGA/3PA等分母；小样本提醒为研究配置，不增加任意“10场以下不许决策”的玩法门槛。没有对手强弱/伤病/逐回合信息时，反事实效果和战术胜率提升保持未测。

## 5. 球员能力、跨批身份与角色供给

当前identity是snapshot:roster:team:slot；同批人物引用用它，pool映射只在同批以pool_slot且唯一匹配连接。任何时点都不把name/face/slot单独升级为持久身份。

跨批层级沿现有分析方法：VERIFIED_STABLE需来源认证的稳定键或独立可核对的明确人物链接证据；多字段唯一匹配只是TEMPORAL_CANDIDATE，AMBIGUOUS/UNMATCHED不输出确证成长。可存候选差分并明确provisional，不能计入已确认成长。交易后人物累计不是新队贡献；团队区间与人物区间分别标归属适用性。新赛季不能把薪资槽移位默认解释为涨薪/新签。

为GM准备角色供给：引用真实技能字段、合同与样本，使用M2卡片提出持球、投射、终结、护框、外围防守等**适配假设**。首版不造全联盟统一总价值/OVR或默认权重；可按显式字段/阈值筛选，返回原量与方法版本。每次筛选条件属于研究假设，不是游戏规则。

原生attributes是`{field: {raw,value}}`，适配层取已解码`.value`，不得再解码一次或把raw当能力评级。M2的概念能力词不直接当SQL字段名：例如投射研究可引用`3pt_shot.value`，组织可引用`ball_control/passing_accuracy/passing_vision.value`，外围防守可引用`perimeter_defense/lateral_quickness.value`，护框可引用`block.value`；这些是研究维度组合，不是唯一角色评分。字段映射根据当前profile逐项登记，缺字段就保留缺口。

**市场发现必须能实际运行。** 新增`screen-market --query FILE`：输入明确source_domain（当前roster/全局pool/staff）、角色问题、原生字段过滤、排除本队、排序字段和limit；工具在固定批次上筛选，保存真实候选身份与条件。排序以用户/模型明确指定的字段优先序、identity稳定破同值，不提供隐藏“最强球员总分”。缺能力值不填0；单列unknown候选数。M1成本可按已认证身份补充，但缺FA/合同资格不会变成可签约结论。

市场筛选可以发生在seal之后：以不可变supplement记录写market_candidates，每条携带自身查询/来源/访问回执，不修改sealed packet及其原access统计。GM可按同批研究需求补查，无需为了增加一个候选重新准备所有球队。新batch则必须新run。任何模型补充的fit理由仍是注释，不能改source_owner或数值。

区分TALENT_GAP与UTILIZATION_HYPOTHESIS：前者需要对本队全员和合理内部替代有证据；后者需要已有技能供给与使用/配置之间可解释的矛盾，并列替代解释。两者可共存，也可INSUFFICIENT_EVIDENCE；不允许代码按战绩阈值自动判定卖人或重建。

## 6. 教练、财务、历史参考如何进入packet

同批19字段以当前值、含义、readiness为背景。适配结论链接球队人物、统计和知识卡；ANALYTICS只提出研究方向，不选择必须执行的raw。重点对手由GM/分析明确问题后再展开，防守为OVERALL组；mixed值不是0、IsInUse=0不是禁用、Freelance顺序不变、Tempo原始接口可用但含义未知。

M1 run链接固定run_id和source_binding。无run仍可分析篮球，财务模块NOT_LINKED；不同批次标REVIEW_REQUIRED，当前成本应在当前批重新project后再比较。known_salary与slot情景投影分开，现金/预算/球队salary不同口径不得当同一余额。规则DRAFT不能替玩家制定老板预算。

M2 state只引用具体revision；初始UNASSESSED不会自动升级。历史文化、GSW/SAS/OKC参考只是可反驳的问题模板。当前策略由GM形成，ANALYTICS保留strategy_change_signals与证据，不替球队选方向。玩家场上反馈记PLAYER_OBSERVED，比赛模式、时间和适用范围同时登记；不混入确定性赛季计数。

## 7. 输出与封存

按[契约](dev10_m3/CONTRACTS_V1.md)写analysis_runs、team_features、market_candidates，复用Store。每队行含全员facts/coverage、指标和诊断；用户默认只看一条短诊断，`team/players/market/evidence`按需钻取。所有写入仅派生库，所有读连接只读；目录保护沿PR #3。

prepare/import-analysis更新DRAFT；seal校验实际身份集合、来源、引用与各必需维度明确有结论或缺口，在事务中存不可变sealed payload。模型结论与计算事实分栏，import不得覆盖source_binding、指标数值或工具访问记录。封存后新内容必须新run，supersedes_run_id保留历史。PARTIAL也可以封存供有限消费，但不能冒称完整30队packet。

拟议CLI（待Sol实现）：

```text
gm_analysis.py prepare --career C --batch B --season S --node-type CHECKPOINT [--previous-batch P] [--finance-run R]
gm_analysis.py import-analysis --run R --input analysis_annotations.json --expected-revision N
gm_analysis.py seal --run R --expected-revision N
gm_analysis.py show --run R
gm_analysis.py team --run R --team SAS
gm_analysis.py players --run R --team SAS --limit 20 [--cursor C]
gm_analysis.py market --run R --limit 5 [--team SAS]
gm_analysis.py screen-market --run R --query role_screen.json --limit 5
gm_analysis.py evidence --run R --ref E
gm_analysis.py export --run R --output NEW_DIR
```

每条状态/查询带career/batch/run/revision/derived标记；默认摘要不返回全联盟全员正文。小结果预算复用M0（默认20/最多50、字节上限），市场摘要默认5，cursor绑定run/查询/排序。正常超限用后续cursor，不能静默截断后仍标完整。

GitHub handoff只导出index.json、30队短摘要、access_coverage、methods/gaps及明确选中的方案/证据；完整人物明细留工作台按需查。导出必须显式，目录新建，不写published/seasons或事实库；是否提交GitHub仍由玩家/角色任务授权，不把导出自动接成发布。
