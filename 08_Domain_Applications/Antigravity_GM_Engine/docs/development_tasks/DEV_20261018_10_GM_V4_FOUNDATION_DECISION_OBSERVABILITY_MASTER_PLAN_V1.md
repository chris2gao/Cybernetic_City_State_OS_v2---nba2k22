# DEV-20261018-10 — GM V4 自主经营引擎：数据可用性、知识/财务、决策压缩与运营反馈总规划 V1

> **2026-10-18 V2 范围更新：本文件中的 M0 大量 JSON 分页/分片方案已经取消。** 玩家决定让网页开发、数据分析、GM模型经授权终端按需只读查询本地 SQLite。**新的权威开发任务书为 [DEV10 V2 SQLite-first](DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md)**；M1—M4愿景仍可参照此V1，但如有冲突以V2为准，Codex首轮只做V2 M0，未授权游戏写入。

> **任务类型：多里程碑开发总任务书（MASTER PLAN），不是要求一次运行所有模块。**
>
> 项目：`chris2gao/nba2k22-gm-engine`；计划日：2026-10-18；状态：`PLAYER_REQUESTED_DEVELOPMENT_PLAN / NOT_IMPLEMENTED`。
> 负责人：Web GPT 开发规划；开发落地：Codex；篮球/组织知识研究：GM研究/分析模型；现场运行：玩家明确触发。
> **核心愿景**：把网页GPT建成具备实际篮球知识、经济约束和长期战略的30队独立自主GM；NBA2K22 PC Current Gen继续负责比赛和自然成长。常规经营节点争取**一次GM消息形成完整可审批提案**，需调整时通常2次，复杂节点目标3次（不是为了赶进度假报完成）。

## 0. 最重要的实际审计事实（Codex必须先看，而不是直接按愿景写模块）

当前M02真实已发布批次（**不是未来永恒latest**）：
- career=`mc_haliburton_2021`，game_date=`2021-12-12`，batch=`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`。以实际最新`published/index.json → latest.json`决定每次工作输入。
- `manifest.json`记录：30队、466在队球员、**1458员工观察**、3383球员模型、789历史新秀模型；`staff.json` **2,728,888 bytes**；`player_catalog/name_index.json` 481,433 bytes；`teams/GSW.json` 195,288 bytes；`coaching/teams.json` 244,897 bytes。通过Web GPT当前GitHub`fetch_file`实测：`staff.json`返回有SHA但**内容为空**（即此网页消费者无法有效读取，不代表仓库文件真的为空），按行请求也为空；不能将“采集成功/已发布/manifest计数正确”视为“模型可查询数据”。
- `league.json`的`cash`：CLE=4288804119、NOP=4290109259、UTA=4293156901、ORL=4291474586。四值接近`2^32`；以有符号32位解释分别约为 -6163177 / -4858037 / -1810395 / -3492710 **仅为字节解码候选**，不是已经证实的真实负现金。需本局原生字段类型/GUI/源码布局证据认证。另`payroll`、`total_salary`、`budget`、`staff_budget`、`cash`、`monthly_gate_revenue`各有不同语义或时间口径，不能相减推“可签约空间”。
- 当前`src/export_web_gm.py`已按队输出`teams/<abbr>.json`、按年份最多200项`player_catalog/<year>_<part>.json`及大`name_index.json`，但仍整包输出`staff.json`；`src/gm_core/data_reader.py`在本地Python可读取整个staff，**网页GitHub消费者不等于本地Python**。`docs/34_BASELINE_CURRENT_STATE.md`和`source_coverage.json`报告的是来源/同批审计，不是每个代理真实可读性的验证。
- `src/gm_core/calculations.py`当前以工资交换和代理差额为主，非真实可支配预算/3-5年财务预测。`src/gm_core/offseason.py`已有合成输入下的容量、合同/报价及竞价基础，但真实休赛期输入明确被拦截；不得声称已能生产签约。
- GM现行`web_gm/GM_DECISION_ROUNDS_V3.md`强制**至少5次实质用户触发回合**；V4需要让5个**内部业务阶段**在一次任务内完成，不能只是改提示词掩盖深度不足。`docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`仍含“每节点最多三轮”旧句。只有**经本计划的V4验收及玩家批准启用**才能统一修订这些冲突的现行规范，保留旧V3历史档案不回写。

### 全局权限、不变边界
1. 用户明确触发五阶段，绝不自动跨阶段：①Codex全量采集 → ②Web数据分析 → ③Web GM自主经营 → ④玩家审批 → ⑤Codex合法执行。每次新的游戏数据更新仍调用`full_verified_v1`全量采集，**不开发任何专项/增量数据采集**；derived JSON索引/卡片属于**同一次全量批次的数据导出**，不是第二次采集。
2. GM只提出`PROPOSED`；交易/教练/签约写游戏仍需玩家对准确动作、源身份、batch、版本、digest/审批参数单独批准。普通球员能力/潜力/徽章/倾向禁止经营性写入；历史重力例外遵守单独玩家批准。训练、锁定个人精准分钟、五项Sim控制都不纳入此项目。
3. 数据分析和GM可发布**分析/研究/提案/运营侧car文件**（玩家本次授权对应阶段发布时），不可改写`published/`的旧观测、审计事实、SQLite或游戏内存；代码对`published/`导出只能由Codex经原有玩家触发流水线生产/发布。各模型只做明确授权阶段，结束`*_READY_AWAITING_PLAYER`。
4. **不要求完整破解2K22引擎**，仅对经营有意义的本局原生规则、可用字段和外挂约束做有等级的事实认证。现实NBA CBA、次世代MyNBA介绍和球队真实历史不能覆盖本世代PC局/外挂规则。

## 1. 总体架构与交付链

```text
 玩家主动触发(游戏存档/日期)
   │
   ▼
 [Codex full_verified_v1 全量采集+同批导出] ──> source_health / consumer_access_manifest
   │    raw SQLite + 不可变 JSON (含适度分页、按队按岗位)
   ▼
 [Web数据分析+确定性计算] ────────────────> GM_DECISION_PACKET_V1 + analysis_health
   │      30队诊断、市场线索、合同/战术/财务摘要及可溯源原始引用
   ▼
 [Web GM 一次任务内5个内部阶段] ─────────> 30×TEAM_STRATEGY_STATE + GM_FINAL_PROPOSAL
   │      各队独立利益、替代方案、双边谈判、资产/财政闸门
   ▼
 [玩家批准明确动作/版本]
   ▼
 [Codex执行脚本和回读] ─────────────────> EXECUTION_RECEIPT + 审计问题证据
   │
   └── 只在玩家下次主动触发全量采集后，分析模型做事后对照
                                     ▼
                        GM_OPERATIONS_FEEDBACK / DEVELOPMENT_INBOX
                              (供后续开发规划窗口主动审查)
```

**采集事实**、**确定性计算**、**模型判断**、**玩家批准**、**游戏写入与后续观察**必须具有不同状态；不能因导出了JSON或执行脚本回执成功就自动宣称GM分析完成/比赛有提升。所有产物需`career_id/source_batch_id/game_date/run_id/schema_version/source_refs/status`，按需额外`previous_source_batch_id/decision_id/action_id/implementation_commit`。

## 2. 为什么采用多阶段：5个里程碑，逐阶段验收，研究支线并行

| Milestone | 核心交付 | 负责 | 前置条件 | 业务验收 / 停止门槛 |
| --- | --- | --- | --- | --- |
| **M0 — 数据实际可用性与可信财务字段** | 每角色`DATA_ACCESS_CONTRACT`、同批派生分片/索引、真实网页读回、数值异常识别 | Codex + Web数据/GM实际验证 | 现有全量导出 | **P0硬门**：网页分析与GM能真实查询员工/球员池、用可靠数值或明确UNKNOWN作决策 |
| **M1 — 游戏/外挂规则与财务资产计算基础** | `GM_GAME_ENGINE_KNOWLEDGE`、`FINANCIAL_FACTS_AND_CAPACITY_V1`、3年起的合同/选秀情景比较 | Codex+开发规划/游戏机制研究 | M0经济源可辨认 | 不把现金/预算/工资差误作签约空间；能输出各队未来承诺及合法性/战略负担，未认证资格返回UNKNOWN |
| **M2 — 篮球知识库和球队长期经营状态** | `GM_BASKETBALL_AND_FRANCHISE_KNOWLEDGE`，可检索战术卡、球队历史证据，`TEAM_STRATEGY_STATE_V1`30队 | GM研究/数据模型 + Codex索引支持 | 可与M1并行；历史事实需来源 | 三支代表球队可解释建队政策与战术适配；30队具备可维护、证据分级的长期状态 |
| **M3 — 面向决策的数据分析包和GM V4** | `GM_DECISION_PACKET_V1` + `GM_DECISION_PROTOCOL_V4` + 30队独立市场冲突审查 + 一次任务终稿 | Web数据分析+GM+Codex合同工具 | M0已通过，M1/M2有可消费最小内容 | 常规一个节点**目标一条GM回复**完整提案，未被证明的规则阻断相应动作；保留全队覆盖与双方独立议价 |
| **M4 — 运营反馈、自检与正式推广** | 质量探针、行动→观察配对、问题归因与`DEVELOPMENT_INBOX`、首次三队对照与全联盟推广 | Codex deterministic + 分析/GM + 开发规划 | M0~M3有稳定接口 | 玩家真实流程跑通（只对已触发任务），游戏自然数据产生可追踪“新开发线索”与改进请求；V4经玩家验收后正式替代V3 |

**执行策略**：一次Codex任务窗口只负责**一个里程碑**（M3允许拆为M3A分析/M3B GM），不要求一个窗口完成五个里程碑或等知识研究全部结束才能交付阶段产物。M0达标后即可在真实游戏中享受增强数据访问。M1/M2并行调查，M3先做数据契约再升级GM，M4反馈最低限度从M0开始植入，最终由M4贯通。每阶段独立PR/commit、证据和玩家确认，不自动推进下一阶段。

## 3. M0详规：五个“可用性”关口（本项目最高优先级）

### 3.1 每个来源必须拆分`CAPTURED → AUDITED → PUBLISHED → CONSUMABLE → USED_IN_DECISION`

这五个状态**不能合并**。例如staff现为已采集1458条、已发布2.7MB，但Web GPT无法取得正文，属于`PUBLISHED_BUT_CONSUMER_UNREADABLE`。消费者访问失败要变成**阻断具体经营维度的明确错误**和开发问题事件，而不是让模型凭主观篮球印象补齐员工分析、悄悄报告已完成。

为每类角色建立精简能力矩阵`web_gm/data_contracts/CONSUMER_DATA_CAPABILITIES_V1.md`及机器版：
- `CODEX_CAPTURE`：原生读取、SQLite写入、manifest同批计数/状态、导出分片。
- `WEB_ANALYTICS`：实际GitHub网页连接/相关文件工具读取；读取/按页遍历/执行确定性计算/产出JSON和GitHub回写（分开标记）。
- `WEB_GM`：读取分析包、逐队可回溯玩家/员工/教练/合同/选秀权查询、可以验证具体交易及战术前值、研究文档访问、发布未批准方案。
- `CODEX_EXECUTION`：已批准action身份及原值实时验证、对应已验收执行器、回执，未知操作拒绝。
- `WEB_DEVELOPMENT`：能读源健康/业务反馈、异常样本、失败栈摘要和现有实现/能力版本，从而形成新的研究和Codex任务。

每个关口存`status(READY/DEGRADED/BLOCKED/UNKNOWN), source_batch_id, observed_count, accessible_count, method, tool_or_path, failure_reason, verified_by, verified_at`。`accessible_count`是实际抽取可访问记录/完整性证据，不是来源manifest直接复制的计数。不同模型需真实核验自身读取能力；Codex本地pytest通过**不等于**Web GPT GitHub连接可读。

### 3.2 大文件读取解决路径：不改变全量采集，只增可查询导出层

优先在现有`src/export_web_gm.py`与同批只读导出流程生成稳定、有限大小的JSON：
- **员工**：保留原始`staff.json`不可变；新增`staff/index.json`（总数/同批指针/岗位覆盖/可用字段），`staff/teams/<ABBR>.json`（该队8个岗位与反向身份引用），`staff/people/page_####.json`（全量员工按稳定顺序分页）和必要的`staff/name_index_shards`或按岗位索引。任何页面的记录及身份必须可核对原始员工池，不能只导出240个在职岗位就丢掉1218位候选员工。不要将运行时staff_slot冒充永久稳定人员ID。
- **球员**：`teams/<ABBR>.json`当前队内roster继续保留；为分析创建精简`players/teams/<ABBR>_summary.json`和需要时按人物/按队分页的原生55项/合同详情入口；全球3383模型池使用`player_catalog/index.json`的年份分页并改造481KB的`name_index.json`为有目录的字母/哈希分片供按人查询（大索引可保留）；未在队候选、历史新秀和当前466人必须能独立查询；不能仅靠姓名/Face/slot单个字段认证跨批永恒身份。
- **教练**：19默认设置/18对手防守已经有批次文件；可增加供一次性GM阅读的30队精简工作摘要，不重复写一份缺来源的`coaching`事实。需要原生raw和enum时仍按既有`coaching/teams.json`/`field_dictionary.json`与对手按队文件读取。
- **财务**：来自本批的`finance/field_semantics.json`和`finance/teams/<ABBR>.json`派生视图，异常字段可读取原始值但应附`UNVERIFIED_ENCODING/UNKNOWN`，**绝不悄悄把2^32附近大值按signed结果覆盖raw**。
- **总入口**：`consumer_access/index.json`列已存在/缺失的派生文件、大小、条数、权限、批次版本及按类别查询方式；无重数据自动加载。建议单页目标在数十KB级（例如<=64KiB作为工程目标，按实际连接能力调整），不是任意截断记录；若一条内容超限则拆字段/按记录深读并保持schema身份。提供确定性`list/index → owner/page → detail`方式。
- 严格保持`full_verified_v1`的一次完整源采集和同一batch；所有派生数据都由这**同批SQLite/源JSON**生成，保留存档、批次、采集时间/游戏日期及source coverage，历史bundle不覆盖；发布仅在玩家触发的全量更新时根据原`-Publish`要求执行。
- 使用现有GitHub Contents文件访问，不急于部署网络服务/数据库server；若确有必要先证明分片也不能满足需求再提出新API。Web模型**不能被要求直接打开本地Windows SQLite**，除非已经显式确认相应连接和授权；Codex本地SQLite可用不等于网页GPT可用。

### 3.3 必须由真实消费者验收（不是模拟大文件“能读”）

在**真正的Web数据分析窗口和Web GM窗口**分别按照最新`consumer_access/index.json`完成独立检查（由玩家触发这一步，不跨模型自动调用）：
1. 从`latest.json`取得真实batch，随机/有目的地分别查询**在职主教练+其他7岗位**、同队以外员工候选、全局员工池总记录数/身份；可查`staff_pool`原始值和来源。
2. 查一支球队**全名单**的55项属性、合同、状态；跨两个球队选球员查身份差异，再从全球球员池查至少一个1984历史新秀及某个现役/未在队对象，核实按name索引读到具体详情，不只读到目录。
3. 获取30队教练19项与选定对手防守、合同和选秀权，核对同一来源批次；把一份资金异常球队记录正确标记不可用于签约空间。
4. Web分析端真实使用Python或已可执行的等价确定性计算；Web GM真实消费它写回的`ANALYSIS_ONLY`产物并回钻原始引用，产生一个**不执行的**模拟选择。至少验证GitHub回写/readback的能力。
5. 对故意缺文件、错误batch、员工单页读取失败、候选同名/重复身份分别模拟失败路径，必须`BLOCKED_DATA_ACCESS`/`DEGRADED_SCOPE`并给出替代查询路径、失败角色、具体路径、所需字段；**不能静默省略某种人员**。

**M0验收文档至少包含两类证据**：Codex本地端真实导出/离线完整性结果，及网页模型实际读取/查询结果（模型角色、工具、查询目标、成功计数与限制造成的失败）。没有后者不能标`M0_CONSUMER_ACCEPTED`。如无法立即组织网页验收，Codex提交`M0_LOCAL_READY_WEB_ACCEPTANCE_PENDING`并等待玩家安排，而不是假称完成。

### 3.4 资金字段审计（可与分片开发并行，但不阻塞所有其他业务）

对`team_monthly_stats.cash`原生偏移/类型及UI显示/内存同值关联、`payroll/total_salary/budget/staff_budget/monthly*_revenue`单位和时间口径逐一登记证据等级：`NATIVE_VERIFIED / UI_OBSERVED / SOURCE_DERIVED / HYPOTHESIS / UNKNOWN`。
- 对四个>2^32附近`cash`保留原观测原始表示；signed32转换是**待核实候选**，不可自动修整个库及历史published；确认后修改后续full capture的正确类型，保留schema/version/来源证据和异常修复说明；对旧批次用明确派生重解释，不篡改历史游戏观察。
- 检测：现金异常、年度工资/当前名单工资差、字段非负假设、同队各时点跳变、资金与签约规则不确定性。可能是合法负现金，也可能有编码或游戏逻辑，必须区分。
- 若`cash`与实际签约资格没有可证实联系，不因为数值修好就把现金作为硬性交易合法性闸门。可提供`financial_risk=UNKNOWN/AT_RISK`供GM审慎考虑，不能把`cash`当签约空间。

## 4. M1详规：游戏规则/财务与跨赛季资产引擎

- 权威规则分层：`CURRENT_GEN_NATIVE_OBSERVED`（游戏UI/原生读取）、`EXTERNAL_PLAYER_APPROVED`（简化三届选秀权、双边交易、休赛期竞价、自有资金/“土豪线”等已确认制度）、`NBA_REFERENCE_2021_22`（仅案例和解释）、`UNVERIFIED_COMMUNITY`、`UNKNOWN`。**外挂双边交易不受CPU难度/原生薪资匹配否决**；但玩家希望财政有经济约束，需要另外明确具体外挂资金计算规则，不得模型私定硬限额。
- 构建`GM_GAME_ENGINE_KNOWLEDGE`可检索规则条目：`rule_id, applies_to(PC_current_gen, save, season, phase), claim, scope, source_evidence, confidence, native_field, can_observe, can_execute, version, superseded_by`。遇同一字段多版本矛盾标冲突，不让后者静默覆盖。
- 金融第一版优先3年（可向5年扩展），逐队逐年`observed_salary_commitments`、到期/不明合同/选项`UNKNOWN`、下一季名单容量、现有未来三届合法选秀资产、核心续约情景、当前合同成本/代理cap-tax位置、可能的财务压力和超额情景。**把“合同承诺”“规则可签约额度”“老板愿承担的支出”“资产值不值得”分开**。
- 最少三个候选结果：`KEEP`、`INTERNAL_COACHING`、`TRADE_OR_SIGNING`，返回策略比较、工资变化、下季和再下一季影响、资产机会成本与未知项；不编造球员固定胜场贡献或现金清算。签约真实执行未认证时只提出`RESEARCH/BLOCKED_EXECUTOR`，不可绕过`offseason.py`的`SYNTHETIC_ONLY`保护。
- 复用`src/gm_core/calculations.py`和`src/gm_core/offseason.py`里可验证的纯计算；不要重复写一个并行的不兼容财政系统。规则/计算含完整版本、输入ID及适用年度（不可静默在2023重用2022规定）。
- 验收：30队能在已证实的输入上计算三年已知合同承诺、缺失因素显式UNKNOWN；GSW/SAS/CLE三队的资金与薪资不会误判断为预算差=可签约空间；交易前后两个队的资产/工资情景一致，合成休赛期不能伪装真实成交。

## 5. M2详规：篮球机制知识与30队经营记忆

- 不建大百科和必选100页长提示词；采用短`TacticCard`：`id, basketball_principle, required_player_roles/abilities, counters_and_weaknesses, opportunity_cost, observable_signals, nba2k22_fields, enum_evidence, confidence, reference_sources, game_version_scope`。先做挡拆、空间、转换、传切、低位、防守换防/Drop/Hedge/护框/协防等高价值主题。2K原生19默认/18整体防守映射需要精确现有字段字典；`Tempo`界面含义未知必须保留UNKNOWN。
- 历史组织样板只作为参考，先研究**GSW（高成本争冠）/SAS（发展与内部优化）/OKC（资产累积）**，出处/赛季/背景/可转用条件完整。再扩展30队历史初始身份；不能从当前阵容倒推文化标签，不得把现实冠军结果强制复制到游戏。
- 每队`TEAM_STRATEGY_STATE_V1`分慢/快变量：`identity_reference, identity_evidence, ownership_cost_preference_if_verified, competitive_window, core_assets_and_hold_thresholds, contract_window, tactical_direction, current_hypotheses, observed_challenges, current_actions, change_conditions, last_review_batch, status, strategist_version`。历史偏好非硬限制，本局战绩/合同可证据充分地推翻先前经营政策；保持30队**独立利益主体**。
- 30队都可`HOLD`，不强迫为每队虚构独特“赢球文化”。自然成长由游戏AI决定，不做训练编辑和精准个人分钟锁定。知识来源有`REAL_NBA_REFERENCE`与`IN_GAME_OBSERVED`区别。
- 验收：GSW/SAS/OKC相同输入分别作出有区别、可反驳的政策，给证据出处且说明哪些尚需本局实际确认；30队有schema合格的长期状态且可跨批演化，修改策略必须说明证据与被取代策略。

## 6. M3详规：真正的数据驱动分析包与一次任务 GM

### M3A — Web ANALYTICS：新增标准`GM_DECISION_PACKET_V1`

在现有`ANALYTICS_DECISION_READY_V2`基础上**升级目的，不重新打印排行榜**：
- 30队一队一卡：`observed_performance`（比赛增量/累积、eFG/3PA/TOV/篮板/罚球、数据口径）+ `player_supply`（现役466条中对应球队当前全员覆盖标志、核心/替补、能力与合同）+ `coaching_fit`（19项/对手18项及可执行性）+ `financial_and_assets`（3年承诺/资格未知/草拟风险）+ `strategy_change_signals` + `market_supply_and_demand_clues` + `missing_or_blocked_facts` + 每项引用`source_refs`。
- 分析模型负责编码、数据口径与异常、候选匹配，不替30支球队批准转会、不直接输出必改的原生教练raw。对员工池、全局球员池**必须真正执行访问自检**，不能像历史W03那样因为文件大就放弃并继续声称全面评估。
- 每个节点输出小`packet/index.json`+30份`packet/teams/<ABBR>.json`+`market_opportunities.json`+`finance_scenarios.json`+`access_coverage.json`+`analysis_methods.json`；按需附深入证据，不要求GM默认反复读取原始2.7MB池。
- 使用真实已读源和Python/SQL确定性计算；源无法读取即`DATA_ACCESS_BLOCKED`（若仅员工无法读取，员工相关结论必须HOLD，是否允许其它独立经营维度部分前进由影响分析判断）。不能复制manifest计数冒充访问了1458条。
- 在玩家授权分析阶段写入`docs/gm_analysis/<career_id>/<analysis_run_id>/`下的`ANALYSIS_ONLY`结构化文件及方法/诊断；不修改生产观测文件。

### M3B — Web GM：内部五阶段、外部一回合目标

当前V3的“五个有实质内容的研究阶段”必须保留**质量门槛**，但取消每阶段要求玩家下一条消息才能继续的耦合。新`GM_DECISION_PROTOCOL_V4`应当在**同一次由玩家触发的任务内**：
1. 读`GM_DECISION_PACKET_V1`、30队策略简表和最近行动/反馈。全30队唯一身份+全员评估覆盖可通过**结构化机器档案**满足，而不是网页向玩家输出466条流水账。
2. 针对高风险队/重大变更按需展开当期原始人物、员工、合同、教练真实状态，至少比较HOLD、内部阵容/战术调整、交易/签约；建立各队独立保留底线、需求与机会成本。
3. 由30个独立GM利益函数模拟内部市场意向，真正匹配双方可接受的完整筹码；资产不得被两份拟成交重复出售；谈不拢就`NO_DEAL`。
4. 程序化检查`career/batch/identity/合同与名单容量/选秀权3年/财务已认证边界/教练原生enum/执行器状态`，不能为“单回合”绕过阻断，未知选项降级`BLOCKED/HOLD`。
5. 输出**唯一**`GM_FINAL_PROPOSAL`（30队摘要+可审批动作+有理由HOLD+来源与必要风险），并存30队详细dossier、`TEAM_STRATEGY_STATE`新候选、行动效果假设和下一节点观察目标。
- 对话效率：常规一个消息目标；玩家要求调整时第二回合完成复核，复杂节点第三回合目标；**不是超时后无证据直接宣称完成**。若技术时间/上下文限制，返回明确分阶段已完成+未完成并在GitHub保存断点，不以多对话为常态。不要在未使用真实GitHub工具时冒充完成30队。
- 结构验证使用Python/JSON Schema+对照同批来源的**实际身份集合**，核对30队、各队全名单与关键资产覆盖、所有候选条件、双边接受、去重和不同动作间冲突；具体教练/交易方案由各自原有执行器生成真实计划/digest，GPT禁止编造审批摘要。
- **V4制度上线条件**：GM V4/ANALYTICS V3合同+真实网页消费演练通过，玩家明确批准从`V3_MIN_FIVE_USER_TURNS`切换到`V4_SINGLE_TRIGGER_INTERNAL_FIVE_PHASES`后，再由Codex统一更新`web_gm/GM_DECISION_ROUNDS_V3.md`(加历史superseded标注，不篡改旧记录)、GM SOP/基线/Schema、`docs/35...`旧“最多三轮”冲突、GM_CURRENT及赛季索引。**本总规划本身不是对旧执行权限的隐式放大。**

## 7. M4详规：游戏运行产生“可开发反馈”而不仅是比赛报告

**设计目标**：玩家按惯例触发五阶段时，已经运行的阶段自然生成可持续的**质量、机制、业务效果、开发线索**；下一次玩家来开发规划窗口，Web Development可以读取问题看板**主动提出有证据的开发任务**，不只依赖玩家发现BUG。此为现有玩家触发任务的伴生产物，**不是无人值守自动化、跨角色唤醒或给AI额外游戏写入权限**。

### 7.1 五段对应的反馈材料（各自只在本阶段实际运行时生成）

| 生命周期 | 伴生反馈产物 | 必须包含 | 不可夸大 |
| --- | --- | --- | --- |
| ①全量采集 | `ops/source_health/<batch>.json` + 同批`consumer_access/index.json` | 每来源真实条数、异常值、时间、批次、字段口径、分页查询可用性，是否发布 | Codex只证明本地导出/静态检查，**不能替Web模型宣布读得成功** |
| ②分析 | `docs/gm_analysis/<career>/<run>/analysis_health.json` | 各来源实际access状态、已读记录、身份/poss/财务不确定性、异常与缺口、可供GM使用的packet | 不把分析假设当游戏因果事实 |
| ③GM | `web_gm/decisions/<career>/<run>_hypotheses.json` / 30队策略候选 | 事前假设、预期**方向性信号**、替代行动、HOLD理由、下次观察条件、confidence、玩家是否批准 | 未获批准不计为实际执行 |
| ⑤执行 | 既有`EXECUTION_RECEIPT` + 只读副本引用 | 玩家实际批准字段、真实before/after、完成或部分失败、游戏保存状态未知/已证据确认 | 内存已写≠存档已保存≠下一采集观测到 |
| 后续①②节点 | `ops/decision_outcomes/<comparison>.json` + `DEVELOPMENT_INBOX.json` | 将**已执行**动作与后续真实同存档、可比数据配对；变化方向、样本/缺失、潜在混杂、异常、待研究机制、可复现路径 | 输赢变化不能直接归因于某单项战术；无足够新增比赛时标`INSUFFICIENT_OBSERVATION` |

用户未进入阶段④/⑤、尚无执行动作时，仍可记录模型数据错误/只读异常，但**不得输出“已执行效果报告”**。没有下一次新批次不能宣称游戏效果发生。

### 7.2 开发线索的生成/分流规则

创建`web_gm/development_feedback/README.md`和按career/批次/事件的机器可读索引，原则上由**当前实际执行的模型**根据已读证据生成/更新其权限范围内的记录。建议异常类型：
- `DATA_CONSUMER_UNREADABLE`：源已发布但网页读取空白/超限/不能查询（例如2.7MB员工池）。
- `SOURCE_SEMANTICS_CONFLICT`：数值编码/字段单位未认证（如四队cash）。
- `DECISION_PACKET_MISSING_OR_STALE`：分析未完成、文件批次落后、实用性差。
- `GM_STRATEGY_DRIFT`：决策与长期经营目标冲突或没有证据解释战略转向。
- `GM_PROPOSAL_INFEASIBLE`：无双边共识、资产重复使用、合同/字段原生非法或执行器不具备。
- `ACTION_EXPECTATION_MISMATCH`：有已执行回执和后续游戏观察，指标偏离事前假设（只作为研究线索，非因果归责）。
- `NEW_GAME_MECHANIC_CANDIDATE`：有玩家/界面/跨批观察支持可能存在的新经营机制，但尚无原生证据。
- `OPERATIONS_HANDOFF_FAILURE`：GM/分析/执行端无法打开同批文档、不会使用对应接口或写回失败。

统一事件字段：`issue_id, first_seen, last_seen, career_id, batch_ids, observation_source, stage, affected_capabilities, evidence_paths, repro_steps, severity(P0/P1/P2), confidence, hypothesis, proposed_owner(DATA/ANALYTICS/GM/DEV/EXECUTION), actionability, status(OPEN/TRIAGED/BLOCKED/RESOLVED/DISMISSED), related_issue_ids, next_review_trigger`。
- 同一异常跨批重复时用稳定规则合并/增加`occurrences`，不生成30份同样的错误；错误不自动转成GM动作或Codex开发命令。
- 优先级：P0事实错误/阻断核心数据消费/有机会误写游戏；P1导致财务/签约/交易战术决策偏差；P2研究兴趣、策略质量改善、新内容建议。
- 反馈报表同时包含**明确无需改动的HOLD**，避免“为了制造开发工作”而自动制造伪缺陷。
- 日常产物要小、可定位、按源批次/赛季归档，维护`web_gm/development_feedback/CURRENT.md`供开发基线按需加载，保留历史原始事件；敏感运行时指针、私人凭证、游戏进程内存转储、过大原始JSON不上传。
- Web Development的**下一次玩家主动召开的规划窗口**首先读取反馈CURRENT及top issues，自主推荐经证据支持的技术/数据/知识研究，再由玩家选择立项。若用户日后要求定期报告或自动条件监测，再另行讨论授权，不在本任务开后台cron或自动任务。

### 7.3 可用性与决策质量指标（非无根据胜率指标）

每批/节点可计：
- `source_coverage_ratio`（确认来源已采/审计）、`consumer_success_by_role`（网页实际可读/查询）、`staff_roster_read_coverage`、`player_pool_query_success`，**将可读成功和源采集成功分开展示**；
- `decision_packet_complete_team_count`、`gm_team_decision_count`、`trade_conflict_count`、`proposal_preflight_failures`、`stale_packet_count`、`user_gm_interaction_count`、`one_turn_full_result_rate`（多节点后才有意义）；
- `action_result_observed_count`、`outcome_unknown_count`、`strategy_reversal_with_evidence_count`、`regression_issue_count`；不可因为某次输赢直接把GM评为失败。
基线目标：重要来源的消费者查询必须`READY`或明确`BLOCKED+fallback`；每个正式经营节点30/30球队，无重复资产；模型不能虚报读到1458员工/3383球员。单回合目标不能抵消数据/财务闸门。

## 8. 三个“游戏运行模板”与最小演练

**BOOTSTRAP/新开档**：全量认证＋为30队创建初始政策、源可读性、人员/员工/选秀权与教练完整基线，记录引用现实历史的证据等级；只对允许的可执行事件求批准。

**SEASON_INITIALIZATION/每赛季**：承接30队长期政策、合同年进位/到期与选秀历史轮回、更新三年/五年战略情景；新赛季财务/自由球员规则无证据不得默认使用旧赛季。

**CHECKPOINT/每月或事件**：同赛季上一完整快照增量、进攻防守/角色/战术错配、合同/市场变化、行动事后观察；通常30队快速基线扫描，重点问题按需深入；默认一个GM消息提交完整审议案。

先选三个**无游戏写入的真实M02演练**：
- GSW：高工资的争冠窗口，区分本局总薪水/预算/税线/现金口径。
- SAS：内部挡拆优化、Poeltl留队/出售与双边底价、长期战略比较。
- OKC：选秀资产配置、核心年轻球员成长与未来合同机会成本。
用同一已发布批次生成`BASELINE_V3 vs CANDIDATE_V4`在源可读性、财务准确性、独立GM双边议价、证据可追溯和对话次数上的比较。**不能以模型写更多文字当进步**。玩家对三队满意并明确认可后再全30队/当期真实GM节点部署。

## 9. Codex每里程碑交付格式（不要求一次全部完成）

每个里程碑一个`docs/development_reviews/DEV_20261018_10_Mx_<name>_ACCEPTANCE.md`（如M3A/M3B单列），包含：
1. `status=IMPLEMENTED_LOCAL / WEB_CONSUMER_ACCEPTANCE_PENDING / ACCEPTED / PARTIAL_BLOCKED`、基于的源码commit、玩家批准边界和是否触碰游戏（默认NO）。
2. 已修改代码/Schema/文档准确路径和运行CLI；不发明已实现参数；保留旧接口兼容或迁移说明。
3. 实际运行的最小测试/真实查询结果、输入批次与输出位置；区分`SYNTHETIC`、`REAL_PUBLISHED_READ_ONLY`、`WEB_GPT_CONSUMER_VERIFIED`和`REAL_GAME_PRODUCTION_EXECUTION`。
4. 至少一个失败/未知分支的安全行为；旧历史未覆盖；本期原始观察不修改；无批准不运行游戏写入。
5. 是否可以让下一阶段使用、真实剩余阻断、谁需要做下一步、GitHub commit/PR链接。最终`CURRENT`索引由实际交付状态维护。
6. **不扩大无效测试**：仅在必要处做确定性测试、源码契约/真实网页消费验证与身份/异常安全检查，不要求游戏反复重启、教练滑块胜率验证或额外新存档。

**开发模型接此总文档的首轮正式执行范围仅M0。** 先给出准确代码基线、现有发布样本以及本地修复方案，实现M0并提交PR/文档；不擅自连带完成M1~M4。若某些M0消费者验收必须由独立Web模型完成，清楚写`WEB_CONSUMER_ACCEPTANCE_PENDING`和最小操作说明，交由玩家分别触发。M0验收且用户继续后再认领M1/M2。

## 10. 项目任务索引与冲突管理

- 当前角色职责：`docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`；当前GM规则：`web_gm/GM_DECISION_SOP.md`、`GM_DECISION_ROUNDS_V3.md`、`GM_DATA_TO_DECISION_STANDARD_V1.md`；分析方法：`docs/gm_analysis/ANALYTICS_DECISION_READY_V2_METHOD.md`。
- 已有教练19/18、双边交易和休赛期合成工具保留；`config/gm_policy.json`依然标`PROPOSED_PENDING_PLAYER_CONFIRMATION`，不能引用其中生命周期阈值作硬规则。
- 本计划是**开发任务授权与设计方向**，不是对游戏修改权限、未证实签约/CBA硬规则、V4已生产上线、可直接读取大员工池的事实声明。
- 任何研究/开发获得的`UNKNOWN`不应靠编造填上；规则与历史世界线影响GM推理，不覆盖真实比赛/自然成长。
- M0通过后建议先修员工/球员实际可用数据，随后再继续深化球员估值与策略研究；用户可以在任一阶段改变优先级，但应更新本计划与CURRENT状态，不能让旧分期目标悄悄继续运行。
