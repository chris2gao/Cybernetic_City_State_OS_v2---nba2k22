# GM W03/R03 · 第二组10队比赛数据驱动研究（M02）

**阶段**：`GROUP_B_RESEARCH_COMPLETED_NOT_APPROVED`；`game_date=2021-12-12`（玩家确认），不等于自然月月结。最新M02：`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`；对比M01：`2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`；`audit=PASS_VERIFIED`。

**方法**：对比同赛季两次累计队伍`season_totals`，仅计算检查点之间的新增7/8/6场进攻和防守投篮，得到两分/三分命中率与eFG；不在`poss`语义未确认时称其为进攻/防守每百回合效率。并逐人对比同队同名同slot的本季累计差分，禁止跨队/身份冲突错误归因。球员完整资料见[前5队76人记录](ROUND_R03_GROUP_B1_METRIC_FIRST.json)与[后5队76人记录](ROUND_R03_GROUP_B2_METRIC_FIRST.json)：本轮**152条真实当前名单记录**，含投篮/组织/防守关键原生能力、合同、年龄、潜力、实际赛季及可核对的区间比赛表现。球员池全库和员工大JSON/SQLite读取技术难题**按玩家指示决策阶段结束后解决**；本轮员工不参与经营评价，不生成虚构员工策略。

## 一、真实比赛证据总表

| 球队 | 新增战绩 | 新增场均净胜（分） | 本队eFG | 对手eFG | 当前教练选择 |
| --- | --- | ---: | ---: | ---: | --- |
| NOP | 3–4 | -1.43 | 58.14% | 58.97% | `POEDefense` 14→13 |
| UTA | 4–3 | -2.43 | 51.99% | 55.88% | `POEOffense` 5→4 |
| SAC | 6–1 | +19.29 | 60.62% | 48.01% | HOLD |
| NYK | 5–2 | +7.71 | 55.56% | 52.11% | HOLD |
| LAL | 3–3 | +5.33 | 55.28% | 55.08% | HOLD |
| ORL | 2–5 | -9.14 | 49.70% | 54.02% | `POEOffense` 5→1 |
| DAL | 1–7 | -6.38 | 54.67% | 58.33% | `POEDefense` 14→15 |
| BKN | 3–3 | -0.50 | 54.11% | 55.47% | HOLD |
| DEN | 3–4 | -1.71 | 55.77% | 59.23% | `POEDefense` 14→15 |
| IND | 3–5 | -1.38 | 56.32% | 54.12% | HOLD |

## 二、逐队攻防归因、战术选择与市场判断

### NOP：攻好守差，先保护禁区

**数据及人员证据。** 近7场本队120.29分、eFG58.14%，Ingram新增7场28.86分，Zion22.29，Valanciunas17.71；失121.71分。对手346次两分出手命中60.4%，278次三分命中38.1%。Zion内防59、Valanciunas75，球队不是缺攻篮下能力，而是缺防守质量。

**教练决策。** 保留当前BALANCED进攻系统，先将POEDefense由14→13(PROTECT_PAINT)；明确取消旧R01先改进攻POE5→1的优先度。该变化易使对手三分空位增加，因为本期对手三分出手占44.55%，后续看对手两分和三分命中是否此消彼长。

**交易与机会成本。** Zion/Ingram核心保留，Valanciunas篮板/终结有贡献；护框或防守翼候选留待全联盟比较，不假造具体成交。

### UTA：进攻效率低，先提高挡拆终结的质量

**数据及人员证据。** 新增7场4–3，进攻eFG51.99%，两分51.1%、三分35.4%，三分出手占44.56%；Conley传球92、Mitchell三分85（仅4场赛季记录）、Gobert内防97但三分25，现有PERIMETER系统并非缺乏射手，真正问题是出手效率。

**教练决策。** 只改POEOffense 5→4(PICK_AND_ROLL_OFFENSE)，保留ActiveSystem=PERIMETER(3)作为控制变量；比R01提出同时改体系与POE的做法更清晰。注意Gobert无远投易挤压空间，Mitchell小样本，下一批观测两分命中与eFG。

**交易与机会成本。** 不急于以9–16处理Gobert/Mitchell；优先内部教练调整后评价对价。

### SAC：不破坏当前最好的攻防结果

**数据及人员证据。** 近期7场6–1、每场净胜19.29；自身eFG60.62%，对手eFG48.01%，本队三分365投命中41.37%，每场失误仅9.43次。Fox新增7场场均11.14分（赛季场均助攻8.2，并非此区间实测助攻），本赛季Sabonis已转入但其赛季累计包含旧队。

**教练决策。** 保持PACE_AND_SPACE、BenchDepth11、全部原始POE，无新增改动。不要因PreferredSystem与ActiveSystem不同就认为错误；以比赛数据为主。

**交易与机会成本。** 保留Fox/Sabonis的现有赢球结构；Hield高薪但三分85的现值不能以账面成本为理由立即出售。

### NYK：打得好就先不动

**数据及人员证据。** 7场5–2、场均净胜7.71，对手两分命中49.74%，对手eFG52.11%。Randle新增7场25.14分、Barrett25.0分，两人均参与现有进攻产量；本队eFG55.56%较整季58.32%回落，暂不足以盖过赢球证据。

**教练决策。** 继续Thibodeau现有DEFENSE体系、BenchDepth9、BenchUtilization45；关注真实比赛中两位核心的负荷，但游戏AI决定准确分钟。

**交易与机会成本。** 保留Robinson（盖帽84）/Noel（盖帽96）双护框配置，不凭Kemba/Rose角色相似就交易。

### LAL：区间3–3不等于球队体系失效

**数据及人员证据。** 新增6场场均得115.17、失109.83，仍净胜5.33；Davis新增6场28.33分，本队两分56.14%。对手三分出手比例46.62%、命中37.10%，是监控风险但没压倒目前净胜正值。

**教练决策。** 保持Vogel的GRIT_AND_GRIND和原生POE配置；对手外投若持续升高再讨论POEDefense15，避免一次性削弱已有效的禁区保护。

**交易与机会成本。** James/Davis核心不出售；Westbrook合同大且投射73，但仍提供持球与组织，只有明确双边收益才参与价格审查。

### ORL：最明显的投篮低效，进攻先改

**数据及人员证据。** 7场2–5、净负9.14，进攻eFG49.70%，三分182投命中28.02%；Fultz三分69、Suggs78、Cole77，但三名后卫控球评分84–87。两分52.55%也非高效，说明球队整体终结短板，不能假设一改即痊愈。

**教练决策。** POEOffense 5→1(GET_TO_BASKET)，利用持球攻击现有防线，避免继续依赖低质量外围投射；保留BALANCED体系。可能在强护框对手前挤压内线，与对手匹配应复盘。

**交易与机会成本。** Suggs20岁潜力88、Franz20岁潜力82、Carter22岁潜力82保留，Ross/Harris等老将可在30队市场评估中报价，不以短期成绩送走成长核心。

### DAL：明确推翻旧护框优先的建议

**数据及人员证据。** 8场1–7、净负6.38、失122.63；对手三分279投命中42.65%，两分471投命中54.99%；自身eFG54.67%。Doncic新增8场35.13分、Porzingis19.38分，进攻有支撑但外围火力被对手反制。Nwaba刚进入DAL，个人赛季数据可能含旧HOU。

**教练决策。** 淘汰R01候选POEDefense14→13，改POEDefense 14→15(LIMIT_PERIMETER_SHOTS)，真实根据对手外线命中异常选择目标。DFS外围79、Nwaba79、Ntilikina83可做防守角色资源；外围加压也可能泄漏禁区。

**交易与机会成本。** 保Doncic22岁潜力99、Porzingis空间与盖帽80；若无法内部补救，在R05研究防守翼市场，先不提前指定出售资产。

### BKN：近期下滑还不足以推翻强队配置

**数据及人员证据。** 6场3–3、eFG54.11%，比累计58.98%低4.87个百分点；对手三分39.46%，季累计约34.2%。Harden同期29.67分、38.2分钟；Durant27.5分，球队仍17–8、累计净胜10分，需留意小样本波动。

**教练决策。** HOLD现有PERIMETER和默认POE；Harris远投90、Claxton盖帽88可作为进攻空间和内线保护备选，不改个人分钟。

**交易与机会成本。** 三巨头保留，避免短期6场变化驱动错误交易。

### DEN：对手外线与内线都命中，先单项改动

**数据及人员证据。** 7场3–4，对手两分56.79%、三分43.15%、eFG59.23%，场均失121；Jokic同期33.86分，本队eFG55.77%，核心进攻仍可。Jokic内防70/盖帽70、Gordon内防74，护框也存在硬件短板。

**教练决策。** POEDefense 14→15(LIMIT_PERIMETER_SHOTS)，先压最异常的43.15%外线命中率，暂不改ActiveSystem=PACE_AND_SPACE，保留Jokic策应和射手。若对手两分仍居高，单靠策略不足以解决，需真正护框补强。

**交易与机会成本。** Jokic/Murray/Porter留队；护框型前场是R05明确的潜在买方需求，须等待其它球队的卖方价值。

### IND：新阵容不该拿旧整季数据作决策

**数据及人员证据。** 8场3–5、净负1.38，但近期本队eFG56.32%超过整季53.50%，对手eFG54.12%优于整季56.58%。Haliburton slot1235现属IND，但其27场58.4分的个人累计混旧SAC；Ty Hali slot184是另一个记录、不能按face_id合并。Brandon Clarke也新加入，需要新的队内样本。

**教练决策。** HOLD Carlisle的PERIMETER与BenchDepth9；保留以Turner内防87/盖帽97为护框基础、MC Haliburton组织进攻的研究方向，但不声称已经观察到新两人同场真实效果。

**交易与机会成本。** 优先观测新队表现而非立即交易、签约或让MC人物改属性。

## 三、正式教练业务候选：仅做最小必要改变

| Action ID | 球队 | 原生字段 | M02 raw现值→目标 | native枚举 | 主要风险 |
| --- | --- | --- | --- | --- | --- |
| `GM-W03-R03-NOP-C01` | NOP | POEDefense | 14 → **13** | PROTECT_PAINT | 对方三分出手占44.55%，禁区优先可能放大外围三分风险 |
| `GM-W03-R03-UTA-C01` | UTA | POEOffense | 5 → **4** | PICK_AND_ROLL_OFFENSE | 可能牺牲Ingles/Bojan的外线出手机会；Mitchell整个赛季仅有4场统计不宜判断稳定效果 |
| `GM-W03-R03-ORL-C01` | ORL | POEOffense | 5 → **1** | GET_TO_BASKET | 两分当前仅52.5%，篮下也并非精英，有拥堵风险；对位精英中锋需灵活调整 |
| `GM-W03-R03-DAL-C01` | DAL | POEDefense | 14 → **15** | LIMIT_PERIMETER_SHOTS | Porzingis内防78、Moses Brown72，扩大外围压力可能漏切入；刚交易Nwaba本季统计混旧HOU。 |
| `GM-W03-R03-DEN-C01` | DEN | POEDefense | 14 → **15** | LIMIT_PERIMETER_SHOTS | Jokic内防70、Gordon74，护框不足不能仅靠限制外围修好；对手禁区得分可能回升。 |

以上5项均有同批`coaching/teams.json`确认的现任教练身份、readiness和raw前置值；不修改主教练个人能力、游戏精确分钟、训练或5项禁用Sim。当前**只是GM经营意图**，并未生成完整原生batch / dry_run / digest，不能直接执行；30队全部研究后R05综合检验、R06提交最终唯一执行方案。其余SAC/NYK/LAL/BKN/IND是有据`HOLD`而不是人为凑出10个战术动作。

## 四、与R01旧30队概览发生的真实修正

- **NOP**：旧提案`POEOffense5→1`不作为首选。新增得120.29分、eFG58.14%，应先修对手两分60.4%的问题。
- **UTA**：旧提案同时变更`ActiveSystem3→2`和`POEOffense5→4`过于宽泛。缩为一项`POEOffense5→4`，减少难归因的连锁影响。
- **DAL**：旧提案`POEDefense14→13`禁区保护被修正为`14→15`外线限制，因对手近期三分命中42.65%。
- **ORL**：旧提案进攻重点攻击篮筐有数据支撑（本期三分仅28.02%），保留但清楚标明两分仅52.55%的限制。
- **DEN**：新提出`POEDefense14→15`的候选，理由是对手三分43.15%而本队核心得分稳定；同样承认必须考虑护框交易，而不是假定单项设置治好全部防守。
- 其它五队实测没有明显超过调整风险的改动优势，故保留。

## 五、阶段交接与质量边界

- **30队进度**：此前R02组A10队，本轮R03组B10队，累计完成**20/30队**。剩余R04组C10队，然后R05联盟双方独立谈判、R06唯一终稿及Codex执行准备。
- **交易**：R03仅锁定卖方/买方需求方向，**不冒充30队市场已经谈判完成**。需要与R04的SAS/CHA/其他球队综合之后才能组合真实资产。尤其SAC Sabonis、DAL Nwaba、IND Haliburton/Clarke为新转队对象，单赛季累计不能作为新队贡献。
- **非必要分析停做**：不要求从球员列表“推导”某种空泛赢球文化；球队决策用明确比赛缺陷、原始战术字段和可检验绩效目标。除有独立证据的真实战略约束外，不做修辞性“哲学标签”。
- **审批与用户实机验证**：本轮没有游戏写入，也无玩家执行审批。已实现的19项战术配置可以用于下一轮形成原生执行方案，**不要求提前证明教练设置必然提升固定胜率**；执行后由玩家实机观察，再在新快照观察方向性变化。
- **待解决的技术债**：`staff.json`等大文件及球员池本地SQLite可查询通道属于决策后的独立任务。本轮已经能真实按球队独立JSON复核球员+比赛+教练，不拿读全池失败当本轮无法分析的理由，但也不宣称本轮已读取完整player_pool.sqlite。

主要来源：[M02 latest](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/latest.json)；[M02球队文件](https://github.com/chris2gao/nba2k22-gm-engine/tree/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/teams)；[M02教练](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/coaching/teams.json)；[M02赛季统计](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/season_totals.json)；[M01赛季统计](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2/season_totals.json)。
