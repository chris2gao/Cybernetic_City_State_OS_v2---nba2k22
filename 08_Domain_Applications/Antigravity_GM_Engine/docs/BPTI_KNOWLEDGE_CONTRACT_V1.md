# BPTI B0 — Knowledge Contract & Architecture Foundation V1

工作包B沿用本契约实现NativeBinding与TeamIdentity查询，新增细粒度机制的安全投影，见[B2/B3手册](BPTI_B2_B3_NATIVE_BINDINGS_AND_TEAM_IDENTITIES.md)。未新增DTO写入权限；下方B0/B1范围与“未映射”描述是原阶段证据。


日期：2026-10-20。契约版本：BPTI_KNOWLEDGE_V1。

B1增量沿用本契约和TypedDict；新增知识文件/整卡投影/有界检索见[B1手册](BPTI_B1_SYSTEM_CARDS_AND_RETRIEVAL.md)。下文B0范围与历史限制保留原阶段含义；原40复合Claim未升证，六条细粒度提取另存B1知识文件，不改变既有数据契约。
范围：DEV22 的 B0；不代表 B1–B6、DEV23、DEV24 或 GM V4 启用。
当前工程/验收/PR 状态见[验收报告](development_reviews/BPTI_B0_IMPLEMENTATION_AND_ACCEPTANCE.md)。
业务权威：[DEV22](development_tasks/DEV_20261020_22_BPTI_RESEARCH_TO_CODEX_PHASED_HANDOFF_V1.md)及[R4](development_research/BPTI_R4_RESEARCH_INTEGRATION_AND_ENGINEERING_HANDOFF_V1.md)。

## 1. 唯一落点和调用方式

- 纯 DTO/校验：[gm_core/bpti.py](../src/gm_core/bpti.py)。只接收普通 Python 字典；不访问网络、数据库、游戏、Registry 或执行器。
- 研究索引：[research_source_index.json](../web_gm/knowledge/bpti/research_source_index.json)，沿用现有 M2 知识目录，不是新事实库或正式球队状态。
- 现有 M2 的 Knowledge.bpti() 按需加载 ResearchIndex；原十二张卡、三十队参考和既有查询保持原路径。
- 现有 scripts/gm_knowledge.py 增加四个显式 B0 子命令，不自动加载研究正文，也不启动 M3 经营回合。

以下为使用说明，本页不声称已经运行每个命令：

~~~powershell
python -B scripts/gm_knowledge.py bpti-contract
python -B scripts/gm_knowledge.py bpti-source --source-id ATL-S2 --audience RESEARCH
python -B scripts/gm_knowledge.py bpti-claim --claim-id R1-C-MOTION_READ_REACT --audience RESEARCH
python -B scripts/gm_knowledge.py bpti-claim --claim-id R2-T-BOS-01 --as-of 2021-10-19
python -B scripts/gm_knowledge.py bpti-validate --input _exports/bpti/card.json --audience RESEARCH
~~~

普通 GM 是默认 audience，必须显式给出 as-of；没有游戏日期不猜。
RESEARCH 只用于开发/历史研究，不可将其完整输出作为 GM 事实包。
每次查询一条 source/claim；没有无界导出或新知识数据库。

## 2. 四种精确 DTO

TypedDict 的字段列表可由 bpti-contract 机器读取；运行时 validate_bpti_knowledge 校验必填字段、类型、状态、家族和 Claim 引用，拒绝额外字段。
全部对象含 schema_version、object_type、evidence_claim_ids、status。
字段里的篮球解释是叙述，不是游戏命令。

| 对象 | 最小业务字段 | 固定边界 |
| --- | --- | --- |
| SystemCard | system_id、title、role_requirements、advantage_chain、player_agency、defensive_counter_options、second_answers、known_failure_conditions、roster_budget_tradeoffs、observable_signals、native_binding_refs | REFERENCE_ONLY；十个非互斥家族 ID，不能当八个原生体系 enum |
| TeamIdentity | identity_id、team_abbr、historical_seed_as_of、franchise_value_claim_ids、historical_coach_claim_ids、unknown_values、system_candidates、confidence、operational_link | HISTORICAL_SEED_ONLY / UNKNOWN；NOT_BOUND_TO_ANY_SAVE，不标实际经营 ASSESSED |
| NativeBinding | binding_id、system_id、basketball_intent、field_candidates、mapping_status、behavior_effect、unknowns、fallback | REFERENCE_ONLY；仅语义字段候选，没有原生对象键、数值或字节；效果 UNKNOWN / HYPOTHESIS_NOT_GUARANTEED；失败 HOLD_RESEARCH |
| SystemBlueprint | blueprint_id、identity_ref、primary_system、secondary_systems、source_binding、team_id、coach_ref、player_role_refs、first_advantage、opponent_counter、second_answer、native_binding_refs、internal_alternatives、unknowns | DRAFT_UNAPPROVED；只定义/验证 DTO，不生成 D1–D6 或正式动作 |

SystemCard.advantage_chain 必须完整保留：
entry_condition → first_advantage → defensive_response → player_read →
second_advantage → counter_response → fallback。
观察信号须由卡片作者区分 Outcome / Mechanism / Context，数值或统计关联不自动证明因果。

player_agency 只接受 SCRIPTED_ENTRY、STRUCTURED_READ、CREATIVE_OPTION、BAILOUT_RIGHT、RESET_RIGHT。
SystemBlueprint 的 player_role_refs 逐项为 player_ref / roles / agency。
这些是结构内决策职责，不是五个游戏按钮、能力加成或精确分钟安排。
internal_alternatives 固定按 HOLD、INTERNAL、MARKET 比较，复用 M3 内部优先逻辑。

NativeBinding.mapping_status 为 SUPPORTED_FIELD_DIRECTION、TYPE_MATCHED_ONLY、
UNKNOWN_NATIVE_BEHAVIOR、UNSUPPORTED_ACTION。前两项须另有已审阅的 PROJECT_NATIVE_INTERFACE Claim；
R1 篮球 HIGH、来源 URL 或社区同名术语不满足该条件。
B0 未填入实际 NativeBinding 映射；其解析/本批字段依赖属于 B2。

## 3. Claim → Source → 原始研究

B0 索引覆盖 R1 十家族的最小 Claim 与主引，以及 R2 原有 R2-T-XXX-01 三十条 Claim。
R1 家族引用 ID 为 R1-C-<SYSTEM_ID>，不将原报告临时 GPT 引用 token 当永久来源。
每条 Claim 有 source_ids、原文 document/line_start/line_end、历史时期、
fact_valid_from / fact_valid_to、knowledge_available_from、retrospective_only、
claim_status、evidence_level、counterevidence、design_relevance、verification_ref。
publication_date 和稳定 URL 从关联 Source 追溯；原始日期精度保留为年/月/日，不补造精确日期。

研究身份分为 BASKETBALL_PRINCIPLE、FRANCHISE_HISTORICAL_REFERENCE、
COACH_HISTORICAL_PHILOSOPHY、GM_DESIGN_HYPOTHESIS、PROJECT_NATIVE_INTERFACE、
GAME_RUN_OBSERVATION、UNKNOWN。

Source 状态：
REFERENCE_INDEXED 仅表示归档有永久 URL；PARTIAL_SUPPORT 只支撑补录限定部分；
SOURCE_MISSING 的 url 必须为空；VERIFIED 必须另带审阅依据。
Claim 的 UNKNOWN / SOURCE_MISSING / SUPPORTED_INTERPRETATION / VERIFIED 与 Source 分开。
Claim 要 VERIFIED，所有所引 Source 必须有可靠出处及独立 verification_ref，Claim 也须有自己的审阅依据。
URL 存在、研究已接收、模型自报或文化 HIGH 都不自动认证。
这些是操作者如实记录的证据引用，沿用现有信任模型，不建设新的防伪系统。

生成器 scripts/build_bpti_research_index.py 只解析归档资料，保留补录的 MATCH /
EQUIVALENT / PARTIAL / MISSING 区别；可在修订归档来源后显式重建。
它不会下载或重新认证外文页面，也不会把补录替代文献伪装成恢复了原始原文。

实际缺口：

- ATL-S1 为等价补充；ATL-S2 仅证当期教练组，不能证明长期组织文化。
- LAL-S2 确切原文仍缺失。两篇非等价替代资料不填入其 url。
- 原 R2 引用 POR-S2，但原索引/补录都没有对应来源，保留 SOURCE_MISSING。
- B0 的 40 条是复合研究结论引用，不是逐子命题认证；其事实时间尚未拆分，因此均保留 UNKNOWN 或 SOURCE_MISSING，不直接供普通 GM 作先验。
- B1/B3 可从这些引用提取有确定时间窗的细粒度 Claim；不应直接把整个家族/球队研究包升为 VERIFIED。该工作不作为无限延迟 B0 的条件。

## 4. 双时钟与未来知识

ResearchIndex.claim 默认走普通 GM 投影。真实 NBA 初始知识截止固定为 2021-10-19；
有效截止为 min(显式游戏日期, 2021-10-19)，游戏推进不会自动解锁后来真实 NBA 的结果。
它不限制虚构本局后续比赛事实；本局事实继续由 M3 的同批 GM_SANITIZED 来源提供。

每个历史 Claim 必须先有明确 fact_valid_from、fact_valid_to 和 knowledge_available_from，
全部不晚于有效截止，才可成为 AVAILABLE_AS_OF_CUTOFF。
没有日期则 UNKNOWN_TIME_BOUNDARY；未来事实为 FUTURE_OR_HIDDEN；缺源/未知则隐藏正文。
GM 响应只有 ID、availability 和 claim=null，不返回未来事件叙述。

2023 年写的文章可以支持 2014 年已发生的事件，但必须显式提取仅涵盖早期事实的
retrospective_only Claim，不能传整篇 2023 文章。发表日期不是事件日期。
年份/月精度以该期间上界判断，不能将“2021”当作 2021-01-01。

独立 Source 查询在 GM 模式只给 ID 和研究定位提示，不输出可能透露未来结果的标题/URL；
开发可显式 RESEARCH 查出处。此设计是消费契约，不声称对能直接读仓库的操作者做权限隔离。

PROJECT_NATIVE_INTERFACE 是项目技术元数据，独立于 NBA 现实年表，不能充当篮球效果证明。
GAME_RUN_OBSERVATION 不得由研究索引冒充；返回 CURRENT_GAME_STATE_REQUIRES_M3_SOURCE。
Potential 的 MASKED、真实技能只读、Intangibles 只是软轮换偏置等语义保持不变。

## 5. 接现有 M2 / M3 / DEV14

Python 接口：

~~~python
knowledge = Knowledge("web_gm/knowledge")
index = knowledge.bpti()
view = index.claim(claim_id, as_of=player_game_date)  # 默认 GM
refs = index.reference_evidence(claim_ids, as_of=player_game_date)
dto = validate_bpti_knowledge(payload, index, as_of=player_game_date, analysis=m3_packet)
~~~

- M2：文件仍由现有 Knowledge 所在目录管理，不新增数据库。TeamIdentity 将来作为
  TEAM_STRATEGY_STATE_V1.identity_reference 的历史上下文；策略版本仍由原 gm_workbench 保存。
- M3：reference_evidence 返回现有 ref_id / kind=KNOWLEDGE / version / availability / value 形状，
  key 为 bpti-claim:<claim_id>。隐藏 Claim 的 value 为空，不把研究当当前比赛事实。
  B0 仅暴露这个 opt-in 接口；不改 gm_analysis.prepare 默认行为，不把研究自动注入旧包。
- SystemBlueprint 的普通 GM 校验复用 analysis_packet.require_gm_packet、same_source、team 和 evidence；
  career/batch/snapshot/date/实例/代次与既有包匹配，角色引用属于该队名单，
  coach_ref 须为该队实际 coach_object_key 的 native-object 引用。
  该校验接受已有的可信 M3 DTO，不替代上游 QuerySession.require_gm_sanitized()，
  不凭一个 MASKED 文本自证生产来源。
- DEV14：仍由 gm_data_access.decision_inputs.prepare_native_artifacts →
  gm_core.decision_handoff.native_intent → gm_state_io.plan.build_plan 形成未批准稀疏计划。
  后续 stage/preflight/审批/CAS/回读仍在既有执行端。B0 不 import 或调用此链，
  不创建 Desired、不构造批准 tuple、不拿篮球卡直接执行。

所有知识 DTO 复用 workbench_common.reject_authority，拒绝 approved、approval_status、
execution_authorized 等调用方权力声明，并拒绝 raw/address/changes/target_value 等原生载荷。
DTO 的 DRAFT_UNAPPROVED / REFERENCE_ONLY 表达非批准状态，不新建审批通道。
普通 GM 的正常18项教练、PERSONAL、四Type/Initiator、具名48倾向、本队68槽、
训练6+5、Intangibles25–99范围照旧；OVERALL、自由PlaybookID、51未知倾向仍不因此开放。

## 6. B1 可直接复用与停止点

B1 可复用 SYSTEM_IDS、AGENCY、完整优势链字段、四种 TypedDict、
validate_bpti_knowledge、ResearchIndex、M2 查询子命令和 M3 reference_evidence 投影。
可以据 R1 原文/来源索引逐家族制作简明可检索卡，但本阶段没有制作十张完整卡。

未知包括复合 Claim 的细粒度事实时间、未补齐来源、CRC/受益人/ACE、
Tempo 行为、51未知倾向、真实30队身份绑定与策略评估。
它们分别留给后续获批阶段；不做 DEV23 原生调查、不调用 DEV24 采集，
不启用 GM V4、不新建存档、不改游戏或球员能力。

本轮只允许三项静态边界检查，入口 scripts/check_bpti_b0.py：
缺源不认证；未来事实不入2021先验；知识对象不带原生写入/批准。
完成 B0 后停止，玩家批准后才启动 B1。
