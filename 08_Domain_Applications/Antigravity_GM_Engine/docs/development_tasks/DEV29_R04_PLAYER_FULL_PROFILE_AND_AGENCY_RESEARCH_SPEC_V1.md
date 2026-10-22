# DEV29 R04 — 球员全部信息、可设置属性与未来 Player Agent 接口：研究任务书 V1

## 2026-10-21 R04结案后独立审核纠正：Agent示例不等于人格设计

用户特别指出：**本轮R04研究只是掌握游戏内全部球员信息、可用/可设置字段、实际机制作用及其联动，为未来独立球员人格模型提供原材料**。R04-G、R04-H涉及的谈判/拒绝/角色权利仅为“将来需要哪些游戏数据与可操作接口”的研究场景，**不是已批准的球员人格、目标权重、行为规则、角色协商协议或执行代码**。人格是未来另外的独立模型任务，目前没有开发。我们仍保留R04研究的源/字段/截图、72已登记静态Profile字段+37研究候选（109侧表），明确不是原生全量值已采或全字段全集。

正式用户循环是**采集模型→数据分析模型→教练模型→球员模型→GM模型→执行模型**，每个独立执行。细节：[研究与Agent开发职责边界](../game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)。R04状态仍`RESEARCH_CLOSED_WITH_NATIVE_MAPPING_GAPS`，不再为人格设计返工R04。R05研究经营规则，但不得开发独立球员或GM谈判引擎。


> 属于[DEV29 V3](DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)的独立研究轮。**不在此研究任务中开发真实人格Agent或修改2K22球员资料**。网页GPT主责，查NBA2K20–23的社区/攻略/官方手册/真实游戏图文，保留版本与来源证据；NBA2K22 PC本世代是最终实现目标，次世代及其它系列提供机制参考。

## 1. R04必须回答的本体问题

每一位虚拟球员在游戏原生数据中**到底有什么可以知道、可见、可设置、可观察变化的信息**？其每项参数如何影响进攻、防守、训练、合同、忠诚、情绪、角色与队伍选择？**哪些信息能够形成外部 Player Agent 的目标、记忆、承诺、策略及行动条件**？哪些参数如果改作外挂用途会损坏原生篮球模拟或带来重复计算？

不要只列能力0–99范围和徽章数。须覆盖球员档案从进入联盟、常规赛训练与比赛、伤病、合同谈判、改变球队到退休和历史纪录的全生命线；同时为**球员与GM之间可能真实冲突的行动权限**建立证据目录。

## 2. 中文攻略的8个主章节与完整字段清单

### R04-A 个人档案与职业身份
姓名与原生稳定PlayerID、生日/年龄、身高体重/臂展（如本版有）、国籍/学校、位置与备选位置、司职角色、选秀年份和顺位、年资、号码、当前team、合同、交易历史、状态、头像/动作/动画、历史赛季与荣誉等。区分球员静态身份、赛季动态归属与外部保存的自我叙述；不要拿改昵称等游戏字段充当安全人格存储位。

### R04-B 篮球属性与自然能力成长
投篮、终结、组织、防守、篮板、运动、篮球智商、耐力等各属性准确原文/中文名称、原生范围、读数来源、变化机制、峰值年龄与自然成长衰退、潜力/比赛后成长因子；按技能分类而不是只存OVR。区分**游戏自己允许玩家编辑**与本项目**GM常规经营禁止直接改Ability/Potential**。历史线重力另需玩家单独批准。

### R04-C 全部战术与行为倾向
完整已知`TENDENCY_OFFSETS`及尚未命名的倾向、各属性范围/激活条件/比赛效果、Shots/Touches/Drive/Pass/Handoff/Roll-vs-Pop/On Ball Steal/Foul/Play Discipline等，4 PlayTypes、Initiator、实际战术被调用与执行规则、是否被Coach Run Plays/ACE/球员个人偏好/角色强度覆盖。每项必须标**原生作用是否已证**，不能因“改变倾向可能影响选择”推算必定做何决策。优先对照项目`config/state_io_native/player.json`，它是**有限具名偏移字典**不是游戏玩家完整属性系统。

### R04-D 徽章/人格徽章/角色风格
所有游戏实际存在的徽章组、级别、条件、对场上/模拟/谈判/情绪的效果、成长/衰退或事件触发、当前人物可读性；**人格徽章不能仅当荣誉装饰**，社区有把人格徽章用于事件触发的改装讨论，须和原游戏内置效果分开。每项不默认允许直接写入，尤其不修改普通球员Badge作为外挂生成优秀球员的手段。

### R04-E 身体与风险
伤病现状、预计恢复、部位耐久、长期体能、疲劳、比赛负荷、个人休息与训练安排、受伤风险、复发/职业生涯影响；团队训练、医疗人员、教练健康策略与个人自我保护选择关系。R03先研究训练与恢复一般机制，R04负责**完整个人化原生数据与可观测字段**，避免内容冲突。

### R04-F 合同偏好、个人价值排序与忠诚
精确梳理**Play for Win、Financial Security、Loyalty**（原文名称、可见界面、字段编码、玩家观察的效果）及士气、团队角色、化学反应、明星声望、上场承诺、归属、合同选项和谈判窗口。区分游戏字段影响合同接受/报价金额/去留/满意度；如果玩家社区认为某属性影响签约，要标样本量、版本和争议，不能写死“忠诚=80就不交易”这种不存在的公式。
  
**核心玩家资料参考**：
- [Operation Sports 2K22 Attention to Detail roster](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/) 明确列有`PLAY FOR WIN, FINANCIAL SECURITY, LOYALTY EDITS`、人格徽章、各部位耐久和球员PlayTypes；是有用的社区实践而不是2K22 PC底层算法认证。
- [OS 2K22 roster原始讨论](https://forums.operationsports.com/forums/nba-2k-basketball-rosters/992144-nba-2k22-attention-detail-roster-ps4-ps5-xb1-xbsx-pc-switch.html)（应核对发帖时间与主贴细项）。
- [OS MyLeague Free Agent Contracts](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/814522-myleague-free-agent-contracts)：旧版玩家改变Financial Security、Peak End、Potential观察不同合同报价，**只是旧版局部实验**；说明需要把市场价值与偏好分开，不得诱导本项目日常修改潜力。
- [2K官方NBA2K22 MyNBA机制说明](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)：次世代员工/训练/伤病/人格属性的设计思路，只能对PC本世代机制提供参考。

### R04-G 外部 Player Agent 人格、谈判和自主权
**这部分只识别“可用原料与所需数据”，不提前强制规定球员必须怎样选。** 未来球员可能拥有`career_goals, championship_ambition, money_priority, loyalty, city_preference, trust, relationship_memory, training_preferences, injury_risk_tolerance, playing_role, public_reputation, negotiation_terms, refusal_history`等长期记忆和偏好。

现实历史**作为可参考角色灵感，不把现实做法写成硬编码剧本**：超级球员可能提出优先争冠、队友补强、教练体系、自主训练、合同条款乃至先交易指定球员之后加盟；球队必须比较资产、财政和替代方案并独立回应。以LeBron加入Miami/Lakers等现实经验或玩家自设76ers假设分开标识；不假定巨星会永久同意或不会犯错。

模拟角色权力：
- 球员可**提出**续约条件、加入球队前置条件、个人训练方案、自身战术风格建议；
- 球员可**接受/反报价/拒绝**球队提案，教练和GM也可拒绝球员要求；
- Player Agent行为会改变外部关系/承诺/情绪/未来谈判，允许短期非最优行为；
- 原生游戏的合法实际写入还须项目玩家本人批准和DEV14/对应专用执行器，不将Agent模拟同意当成现实许可；
- 玩家可选择单独设定某一虚拟球员的性格，但初始形象来源要标游戏原生值/社区假设/角色自行发展，不伪造为本人真实观点。

### R04-H 字段双语义映射与风险分级
每个字段补充`native_game_semantic / engine_effect_status / natural_value_source / read_identity / persistence / original_game_owner / external_role_semantic / agent_action_rights / native_write_approval / storage_class / risk_of_overwriting`。

四种归类：`NATIVE_READ_ONLY`、`AGENT_PROPOSED_PLAYER_CONSENT_THEN_PLAYER_APPROVAL`（受控游戏写入）、`EXTERNAL_SQLITE_CANONICAL`（人格与事件持久化首选）、`REPURPOSE_CANDIDATE_UNVERIFIED`（先研究，必须证明无不可接受副作用并获单独授权）。

**不能随意牺牲原生效果来存人格记忆**：比如Loyalty、Financial Security若引擎自己还用来决定签约，改写后可能发生与外部角色AI重复的隐形改变。必要时可以让外部Agent用本来就有意义的原生字段**表达自主决定的结果**，而不是把此字段当作任意藏数据槽。

## 3. R04成果形式与后续DEV28对接

1. `docs/game_mechanics/guides/K03_K12_PLAYER_PROFILE_AGENCY.md`：详尽中文机制攻略，全部原生资料与可设置字段归类、常见玩法、跨2K20–23版本差异、真人玩家如何管理球员。
2. `docs/game_mechanics/catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json`（研究字段目录，有证据再填真实枚举）：
```json
{
  "field_key": "Loyalty",
  "native_label": "Loyalty",
  "field_family": "contract_personality",
  "game_versions": ["NBA2K22 MyNBA community"],
  "pc22_read_status": "UNKNOWN",
  "native_semantic": "player contract/club loyalty preference",
  "source_ids": [],
  "known_legal_values": null,
  "effect_confidence": "COMMUNITY_REPORTED",
  "agent_observer_roles": ["PLAYER", "GM"],
  "agent_action_rights": ["PLAYER_PROPOSES"],
  "native_write_policy": "PLAYER_APPROVAL_REQUIRED",
  "external_storage_recommendation": "EXTERNAL_SQLITE_CANONICAL"
}
```
3. `docs/game_mechanics/catalogs/PLAYER_AGENT_INTERACTION_ATLAS.md`：以`球员⇄GM⇄教练⇄媒体`用例展示实际数据和动作桥接，包括明星要求交易、明星承诺签约、教练要求改变球员投篮倾向、球员坚持个人训练及伤病后拒绝高强度训练。
4. 同步`SOURCES.md`、`visuals/EXTERNAL_VISUALS.md`、`PROGRESS.md`。无法认证本机PC22菜单/具体字段时明确UNKNOWN，不因单个页面缺失使R04无期限拖住R05。

## 4. 建议具体研究分批（待用户按轮触发）

- **R04-A**：全部球员个人资料、能力、耐久/自然成长、徽章/人格徽章的图文与菜单；
- **R04-B**：完整倾向、PlayTypes/Initiator、现场/模拟行为，及Coach/训练联动；
- **R04-C**：Loyalty/Financial Security/Play for Win等合同与人格偏好、士气、个体训练和受伤风险；
- **R04-D**：全字段与Player Agent权力/记忆/保存双语义映射，以及GM、教练、媒体互动实际用例，全部研究出后关闭R04并交R05。

R04每个分批均可根据材料量拆小，**每批独立发布GitHub并回读验证**。完成R04不意味着必须实现个体Agent系统；那属于后续单独软件开发阶段。
