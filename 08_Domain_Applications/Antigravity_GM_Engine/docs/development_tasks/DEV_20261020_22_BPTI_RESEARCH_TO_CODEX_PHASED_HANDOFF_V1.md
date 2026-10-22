# DEV22 — BPTI三路研究成果交Codex：阶段化实施与审批分界 V1

> **2026-10-20 最新权威执行状态及用户调度（覆盖旧B0/B1待做、PR9未合并、逐阶段中途等待等时间性说明）：** B0 PR #8已合并，B1 PR #9 **已合并**（GitHub已核实）；现可由玩家**单独触发**[DEV23](DEV_20261020_23_BPTI_CORE_PLAYBOOK_SEMANTICS_CODEX_DISCOVERY_V1.md)。DEV23不需要用户截图、Computer Use截图或预先打开特定游戏页面，Codex从仓库现存原生对象/已授权只读内存调查，无法证实的仍UNKNOWN；真需玩家文字解答时以完成报告+问题清单**结束当前任务**，玩家随后另开Codex任务。DEV23经玩家接受后，按[DEV26](DEV_20261020_26_BPTI_GROUPED_CONTINUOUS_DELIVERY_AND_FOUR_FAMILY_EVIDENCE_V1.md)分为**包B（B2→B3→四家族2021前补证）**和**包C（B4→B5→B6）**，每包一次新用户触发、包内自动连续实施，**不设交互检查点/暂停等待**；遇需人参与，提交已完成材料+准确问题后彻底关闭当前任务。DEV24由玩家决定推迟至B6之后。不授权任何游戏写入/自动合并/额外测试。旧资料中阶段门的静态工程条件仍生效，**不再保留运行中的等待检查点**。

## 0. 必读、当前状态与仓库事实

- `docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md`
- `docs/development_tasks/DEV_20261020_21_BPTI_THREE_RESEARCH_STREAMS_BEFORE_CODEX_V1.md`
- `docs/development_research/BPTI_R4_RESEARCH_INTEGRATION_AND_ENGINEERING_HANDOFF_V1.md`（**直接业务合同入口**）
- `docs/development_research/BPTI_R1_BASKETBALL_SYSTEMS_DEEP_RESEARCH_V1.md`及R1审核
- `docs/development_research/BPTI_R2_30_FRANCHISE_IDENTITIES_AND_EVOLUTION_DEEP_RESEARCH_V2.md`、R2审核及`docs/development_research/BPTI_R2_SOURCE_REPAIR_ADDENDUM_V1.md`
- `docs/development_research/BPTI_R3_NBA2K22_NATIVE_MAPPING_AND_CONFLICTS_V1.md`
- `web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md`、`web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md`、`docs/DEV14_STATE_IO_RUNBOOK.md`及最新`AGENTS.md`。
- 截至本研究整合，PR#4 M3-T、PR#7 M4均已合并main；`GM_V4_NOT_ENABLED`，30队**实际GM策略**`UNASSESSED`，Issue#6未修。与历史开发文档的旧状态不同，以最新main权威索引和实际PR核查为准。

## 1. 阶段拆分和Codex不得直接做的事情

- B0：研究证据/Schema/契约确认。**优先实施**。澄清R1/R2/R3领域分离、`claim_id`与`source_id`可追溯、2021知识截止、UNKNOWN及原生映射状态；仅需要最小DTO/校验及知识索引的落点设计。不要新增事实库。
- B1：10张R1 SystemCard的可检索实现。让GM可按家族/角色/防守反制查询一张简明知识卡，而不读取607行全文或将真实篮球动作误写成原生执行承诺。
- B2：2K原生映射与依赖，复用M3已认证coach/Book/Type/Tendency/Personal/Training。具体每队卡的游戏动作仅根据新同批可用元数据，未知CRC/固定受益人/Tempo/51匿名倾向一律UNKNOWN/HOLD。
- B3：30队R2历史seed及当期教练分离，保存可回溯时间知识边界；未开始正式新档不能标实际经营ASSESSED。ATL补来源只有部分，LAL-S2仍缺原文，保留UNKNOWN。
- B4：已有M3 D1–D6中插入篮球原因解释与SystemBlueprint，先比较HOLD/INTERNAL后MARKET；不要重做交易引擎/新薪资体系、也不要给球队分配强制风格配额。
- B5：六级团队演化历史状态，明确组织文化慢变量和战术快变量，需真实本局角色证据；不会自动换教练/编辑球员能力/引入真实未来结局。
- B6：按玩家另行批准的**最小**合成/静态验收，关注10家族、30历史seed、GSW/CHI/MIA机制差异、历史巨星转型、UNKNOWN/HOLD、原生意图没有自动审批。

**工作顺序**：玩家批准B0后Codex可以从当前main独立分支实施B0；B0通过、用户同意后再开展B1/B2/...；不要以本任务书为借口一个PR开发B0–B6整套，或因阅读研究立刻编辑游戏数据。

## 2. 开发中必须遵守的合同

- 研究资料身份：`BASKETBALL_PRINCIPLE`、`FRANCHISE_HISTORICAL_REFERENCE`、`COACH_HISTORICAL_PHILOSOPHY`、`GM_DESIGN_HYPOTHESIS`、`PROJECT_NATIVE_INTERFACE`、`GAME_RUN_OBSERVATION`、`UNKNOWN`。一篇球队官方宣传稿不能自动证明几十年文化稳定；单一模拟统计不能证篮球机制因果。
- 每条知识有稳定`source_id`或`SOURCE_MISSING`，可按`claim_id`回查原R1/R2文档/补充文献。研究里临时GPT引用token必须映射永久URL或标待证，不得原样写作知识库的唯一来源。
- 双时钟：历史现实知道的2021赛季前事件 vs 研究者后来知道的事实/球队演化 vs **虚构游戏当前存档日期**，不能偷渡以后赛季NBA结果和选秀名字最终生涯能力。正常GM只读脱敏原生玩家能力；球员Intangibles不等于篮球能力。
- 10家族可重叠，允许真实球队缺乏长期文化。不要让高`identity_confidence`自动增加胜率/交易审批或球队实力。
- 篮球层`SECONDARY_BRANCH`等是对战术意图的研究术语，除`KNOWN_NATIVE`实际字段外**不得当成2K enum**。R1五层球员决策权是认知职责，不是游戏五个按键。
- M3当前`GM_SANITIZED`同批身份约束、四PlayTypes有序、48具名倾向、18个人防守、68本队书、TEAM_BOOK_REBIND双批审批等边界照旧。普通GM不写OVERALL/Ability/Potential/徽章/精确分钟/未认证聘任。
- 保留`HOLD`与`UNKNOWN`可视，不能因为Model给出战术建议便无视游戏黑盒；3D/Calendar年度校准不属于BPTI此次工程。

## 3. 建议B0首个实现的最小交付

**内容范围候选**（需玩家具体批准）：
1. 一份`BPTI_KNOWLEDGE_CONTRACT_V1.md`：明确4类DTO与字段、现有M2索引/M3 DTO回接位点、状态枚举、证据编号、时间边界和Action Gate。
2. 一份可机读轻量`research_source_index.json`或等价知识库引用，至少覆盖R1十家族主引与R2 30队seed的最小`claim_id`，对补源无效内容`SOURCE_MISSING`；不强迫一次核验每一页外文。
3. 最小`validate_bpti_knowledge`校验器或使用现有校验能力：检查缺源不伪称VERIFIED、家族ID存在、时间截止、没有由篮球卡输出raw/Address/approved。
4. 局部B0审批后的静态最小验证（测试集合、预计时长与对象由玩家在批准B0时明确），本任务书本身未授权Codex扩张测试。
5. 报告版本、代码状态、来源没覆盖的字段及下一阶段B1建议；独立Draft PR或按玩家当时批准分支策略，**不自动合并**。

这只是B0建议的工程交付范围，不是要求本窗口替Codex编写运行代码或自动建立数据库。

## 4. 交接给GM而非另造执行平台

目标接口采用现有M2卡可检索 / M3决策与本批数据 / DEV14受控intent：`TeamIdentity`找“我们相信什么、哪些证据不足” → `SystemCard`找“如何制造优势、谁做决定、对手如何反制” → `NativeBinding`问“2K22已证能调整到什么程度” → `SystemBlueprint`将篮球思考放入现有D1–D6、HOLD/INTERNAL/MARKET比较和玩家审批。

**终极可验收体验**：相同球员到不同队时，GM能给出有根据的不同角色及经济机会成本；GSW/CHI/MIA能做本质不同、可追溯、可执行或诚实HOLD的方案；巨星到来先是职责/副分支调整而不是自动重写组织文化；游戏成长和经营历史由本世界线自己产生。
