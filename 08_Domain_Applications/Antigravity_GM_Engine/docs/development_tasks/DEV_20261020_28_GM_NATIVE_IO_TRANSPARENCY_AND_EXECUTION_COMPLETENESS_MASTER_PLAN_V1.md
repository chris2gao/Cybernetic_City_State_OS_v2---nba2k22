# DEV28 — GM 原生输入/输出全透明、动态数据完备及战术手册完整生命周期：总规划 V1

> [**DEV28只交技术底层**](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：DEV29先提供完整机制和候选能力需求；DEV28将其变为可靠采集、查询、选项、批准执行与回读能力。角色人格、模型间谈判、行为程序、涌现算法由另立任务负责。

## 2026-10-21 用户明确DEV28边界：只建设游戏原生I/O原料，不做角色人格

每轮外挂流程是**①采集→②数据分析→③独立教练→④独立球员→⑤GM→⑥汇总与执行**，一般在开赛、月度、交易截止前、季后赛每轮、休赛期启动。当前教练、球员独立人格系统均尚未开发；已有主要是GM人格系统。**DEV28只负责把DEV29研究所得的游戏信息/实际可见数据/原生可选参数/合法调整能力变成可靠可读、可查询、经批准可执行并回读的技术底层**。本文件之前的`Actor-Aware World State`与`Negotiated Action`等是未来系统可能消费的接口方向，**不授权DEV28写球员人格算法、教练意图模拟、媒体模型、角色拒绝谈判程序、Agent调度或固定行为状态机**。人格与多模型互动由其他独立任务开发；这里不制定它们的决策规则。玩家提出的双层同意设想是未来角色系统的问题，本阶段仅遵守已有真人玩家游戏写入许可与原生游戏规则。

正式依据：[DEV29研究与人格开发职责边界](../game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)。R04研究已完成，R05继续原生合同/经营/员工/球探/选秀内容；任何GAME数据更新仍由玩家另行批准。


## 2026-10-20 DEV29 V3更新：世界级多角色事实/行动接口（最高优先级规划修订）

玩家澄清外挂长期目标为**GM、教练、球员、媒体等自主角色共同参与篮球世界，靠真实比赛/合同/历史反馈试错涌现**，不是仅GM选择最优队伍。DEV28原先的“GM全面输入/输出”继续作为核心交付，但**未来接口需求不应限定为GM所有/单方批准**，改为`Actor-Aware World State + Capability Catalog + Negotiated Action + User-Approved Execution Receipt`的可扩展世界层。任何角色可观察哪些事实、提出/反报价/拒绝哪些原生动作，以及执行后如何影响角色历史，必须从DEV29 V3/R04/R07知识矩阵获得。

- 新[DEV29 V3](DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)将R04单独定为**完整球员身份/全部属性/倾向/徽章/疲劳伤病/Play for Win、Loyalty、Financial Security及Player Agent行动信息研究**，并形成[完整专项任务书](DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)。原经营、世界与整合研究后移为R05–R07；R01结束，R02仍NEXT。其研究及多角色交付先于DEV28正式开发。
- DEV28数据能力盘点须记录球员/球队/教练/媒体分别**有权读取什么、可执行候选全集、可提案/否决什么、同意链与玩家授权是否满足**。不以一个`gm_enabled`布尔字段替代角色所有权语义；可在既有权限层增补，不要重造DEV14或业务执行器。
- 外部人格/记忆/关系/荣誉执念/约定优先独立SQLite持久化，游戏Player原生字段保留其比赛/训练/合同功能。玩家提出“把一些原生字段转作外挂专用参数”是未来可研究的选择，**在验证原生作用、持久化、存档/比赛/合同副作用并得到用户专项批准前禁止重用**。普通球员Ability/Potential/Badge无特殊批准不得直改；模拟球员对Tendency/训练同意是额外业务条件，无法替代用户现实写入审批。
- DEV28不是当前即启用Player Agent、自动新闻、联赛虚拟市场系统的授权。先用研究成果完整展示**每个角色可观察/可选择的游戏原料及证据等级**，再分阶段开发实际多智能体运行、记忆、谈判与效果反馈。

## DEV29 V2交付结构及执行顺序覆盖（2026-10-20）

**玩家最新决定**：PR #12已合并，接下来**网页GPT新独立开发规划/研究窗口**主导[DEV29 V2游戏万事通知识库](DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)，按R01–R06多轮搜社区/攻略/官方资料和图文，成果持续写入[docs/game_mechanics/](../game_mechanics/README.md)。**Codex不主导前期全网攻略搜集**，仅在网页研究完成后做FINAL-CODEX的来源/索引/机读目录/现有Registry与M0/DEV14能力对照，输出本DEV28具体实施缺口。旧DEV29 V1的R0-A/B/C角色安排以V2覆盖。截图先登记网页来源、版本/菜单/可见事实，网络第三方版权未明的图片不得未经许可批量复制到GitHub；玩家可按需提供实机截图。真正DEV28原生采集/写入仍需独立授权。

> 2026-10-20 / Web Development / 玩家提出下一阶段目标并授权审查梳理。**本文件是PR #12之后的开发主计划，不是Codex自动开工、游戏写入、PR合并或V4启用授权。**
>
> **先完成PR #12审查修复F1–F4，交付并单独获得合并确认；再按独立已授权工作包执行DEV28。** 对Codex按任务包结束即TASK_CLOSED执行：如需玩家文字协助/决定，只交已完成产物和未决问题，然后彻底结束当前会话；禁止PAUSED/WAITING以消耗额度。
>
> 项目 `chris2gao/nba2k22-gm-engine`；游戏 NBA2K22 PC Current Gen MyLEAGUE；GM只用批准后的游戏写入，默认球员普通经营不能直接修改Ability/Potential/Badge，个人Tendency权限遵循当前明确的DEV14/DEV15登记与玩家审批。

## 前置门槛：先完成DEV29游戏机制与数据/控制全域知识审计（2026-10-20玩家决定）

**权威研究计划**：[DEV29 / R0 — NBA2K20–23 终极联盟完整机制与玩法知识研究](DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V1.md)。玩家发现原全量采集缺逐场比赛、Game Logs、每场Box Score与高阶分析基础；教练/战术和训练能力仅有字段但缺完整游戏可选项，证明之前先找内存再定GM需求的开发顺序有根本缺陷。

**开发顺序修订为**：PR #12冲突解决与由玩家决定合并→DEV29 R0-A（20–23官方/社区/攻略/菜单与篮球经营机制图谱）和R0-B（GM与分析反推所需数据/操作证据）→R0-C（Codex核对现有源/查询/执行缺口与DEV28具体实施表）→**再开始DEV28 D28-0～D28-5工程**。编号29创建晚于28，但执行先于28。DEV28已有DEV24比赛来源要求为候选，不代表已验证真实逐场数据；Game Logs/Box分源和赛季统计差异务必查明。研究完将`FEATURE_DATA_CONTROL_MATRIX`与`GM_DECISION_TO_EVIDENCE_MATRIX`作为D28-0的输入，**不能在没有业务需求目录时只依据已知地址宣称“全量”。**

**作用于所有职责模型**：研究GPT主导官方/社区玩法，GM列经营问题，数据分析列基础与高级指标，Codex对照Registry/M0/DEV14真实工程状态，Antigravity按缺口找本机PC22内存与菜单。次世代材料可用来理解机制，但特定PC内存/菜单单独认证。每包单独授权，Codex在需用户反馈处真正TASK_CLOSED；当前计划发布**不授权启动研究包、游戏写入或额外测试**。

## 0. 玩家真正想要什么

**所有游戏中实际存在、GM可能使用的输入设置与业务操作**，不再只呈现一个内部字段名或裸内存值；GM应能知道：①当前对象/状态，②本局实际能选的完整合法值域和战术候选，③该选项用来做什么/适合何种体系或角色，④能否执行以及为何UNKNOWN/阻断，⑤获批执行后游戏真实状态是否变动并持久。

**所有实际能采集到、持续变化且与GM有关的动态事实**（完整赛程、真实单场、个人/球队表现、名单/教练、伤病疲劳、角色、训练成长等）也应可按来源、比赛/赛季时间、球队/球员身份查询。游戏本身不存在或可观察窗口之外的数据不得伪造为“完整”。

**输入全透明 → GM能选/能解释 → 输出真正能应用 → 游戏读回 → 数据源再次确认**，构成闭环；不是把所有内存地址倾倒给GPT，更不是让它直接写裸字节。

### 明确排除
- 不重新打造第二套业务市场/合同/选秀/球探原生UI：外挂GM仍模拟交易/签约/球队竞争/球探与选秀，Codex只落实玩家批准的真实游戏结果。
- 不重新研究Antigravity已经实测可修改的全局设置地址；接入统一可选项目录即可。
- 不因实现本计划而允许日常GM修改所有球员原始能力或潜力，不绕过DEV14针对教练/Playbook/倾向/回合的现行白名单。
- 不是日历Quick Sim参数调校项目；赛场竞技专项仍只面向实时3D；但是**逐场事实数据可以包括游戏实际产生的各种已完赛场次**。
- 不启动另一个巨大综合回归平台，按同类编码家族及实际问题做足量而非无限验收。

## 1. 已有事实与证据（避免将“可读/已编码”误写成“GM可用”）

### 已有代码、来源和真实限制
- `src/gm_state_io/registry.py`现有Coach19默认、个人18防守/整体仅只读、4+1 PlayTypes、99球员Tendency位（48具名、51未知）、68-slot Playbook CRC、球队6/个人5训练参数、Gameplay以及部分World/Settings目录；`gm_enabled`与实际可写范围必须依审批。原生向外接口已经存在，**本计划只补齐缺漏、链接与语义**。
- `src/gm_data_access/query.py`已有`q_teams/q_team_stats/q_players/q_pool/q_staff/q_coaching/q_defense/q_native_books`及部分`q_native_*`投影；有查询并不等于每个控制项已提供菜单枚举/允许候选/真实身份和业务说明。
- `src/gm_state_io/team_book.py`已有名称规范化+末尾独立“Playbook”后缀兼容 `team_book()`、`validate_rebind()`、`validate_slot()`，仅匹配本队同名书与身份保护，**不证明全部书目录、coach当前真实绑定链、类型/槽位语义、换帅后重新挂载/槽修改都已实机端到端验证**。
- `DEV23`实机专项调查读取CHI/MIA/GSW三本书共204槽，148非零；111槽能匹配静态名称、37个非空名称UNKNOWN、56空槽；**89个不同CRC**名称匹配，不代表PlayType、发起人和第一受益人的原生认证；未观察真实比赛中ACE调用。另有232条静态游戏战术候选目录，按名字prefix猜类型只属于研究线索。来源：`docs/development_research/BPTI_DEV23_CORE_PLAYBOOK_SEMANTICS_AND_ROLE_EVIDENCE_V1.md`。
- `DEV24`目前定义完整比赛事实、逐场球员/球队Box Score、GameID/赛程、节次、伤病/疲劳、投篮区域/高级统计的采集来源优先级；`config/source_catalog.json`仍有部分赛季累计而无完整逐场历史。**本计划采用DEV24要求而非再编第二套数据规范**。
- `DEV27`的`867fe85`是精确后缀名称Bug修复，静态匹配测试，不是完整战术绑定验证；历史政策见`docs/development_tasks/DEV_20261020_27_BPTI_TEAM_BOOK_SUFFIX_MATCH_MINIMAL_FIX_V1.md`。
- `GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md`现行玩家政策：每队有对应同名Book容器，**多队可以引用同一条共享战术**；正常GM改变本队68槽，不能因为风格变化随便改`coach.PlaybookID`；新档/换帅后可获单独批准进行本队同名书技术归位。整体防守不作为常规GM写入，个人防守按真实对手球员。
- 现有M3/BPTI `HOLD/INTERNAL/MARKET`、M1财务、M2知识、DEV14生效权限与CAS/字节/身份校验必须复用；不能因本计划再造另一个执行器/审批中心。
- Antigravity已找到并可修改用户提供的全局菜单参数。后续实际文件与地址由其按项目源文件接入；**用户声明生效与仓库已有发布状态需分开标注，未提交/未同批采集前不能假装M0生产已有此字段**。

## 2. 两种独立透明度：静态控制目录与动态事实

### 2.1 静态“原生选项与能力登记簿”——GM真正能选择

对**全局、Coach默认、单人防守、球队Playbook槽/战术池、球员4 PlayTypes/Initiator、已具名Tendency、球队训练和个人训练、球队角色/阵容、员工/职业合同落地接口**分别登记：
```json
{
  "capability_id": "coach.RunPlayTendency",
  "category": "COACH_DEFAULT",
  "scope": "TEAM",
  "object_selector_contract": "current coach identity of source-bound team",
  "game_build": "NBA2K22_PC_CURRENT_GEN",
  "source_batch_id": "CURRENT_VERIFIED_BATCH",
  "native_field_key": "coach.RunPlayTendency",
  "current_value": "OBSERVED_VALUE",
  "options": [{"native_value": "REAL_ENUM", "label": "GAME_DISPLAY_TEXT", "description": "EVIDENCED_USAGE"}],
  "range_or_enum_provenance": "NATIVE_PROFILE_OR_PLAYER_REPORTED_UI",
  "basketball_meaning": {"intended_effect": "HYPOTHESIS_OR_VERIFIED_DIRECTION", "confidence": "UNVERIFIED"},
  "read_status": "SOURCE_OBSERVED",
  "write_status": "AVAILABLE_WITH_EXPLICIT_APPROVAL",
  "save_persistence": "UNKNOWN",
  "cpu_override": "UNKNOWN",
  "transaction_requirements": ["DEV14_SOURCE_BINDING", "OWN_TEAM", "EXPECTED_OLD_VALUE", "PLAYER_APPROVAL"],
  "unknowns": [],
  "registry_version": "VERSION_ID"
}
```
这只是**建议的DTO合同示意**，不能把占位的“REAL_ENUM”等当游戏真实枚举。

必备三个可查询答案：
1. **Available Controls**：30队/每个玩家/员工/世界当前哪些项目确实可控/只读/被政策禁止/未知？有多少已认证/待研究？
2. **Allowed Options**：每个项目全部原生真实枚举、值域或当前Book可用CRC+战术名称。**既要提供当前值，也要提供可选的全集，带来源/版本/对象范围**。
3. **Meaning and Effect**：球员/战术角色语义、优点与代价，严格区分原生UI文字、游戏静态资源、社区篮球经验、BPTI假设和真实3D执行证据。

**GM读的是有界投影/筛选的选项，而不是每次打印所有99个倾向和所有战术、全部内存偏移；可按类型、球队、战术家族、战术名/PlayType/发起角色检索。** 完整目录由Codex本地维护，可按需查询。

当前某字段未能解码/无法合法修改，也要列`UNKNOWN / READ_ONLY / BLOCKED_POLICY / NOT_OBSERVED`，不能从界面省略来假装100%完成。

### 2.2 动态“真实比赛/人物状态”——GM在决策时知道实际发生过什么

复用DEV24定义的game、schedule、player_game_stats、team_game_stats、已观察的shot zones/高级指标、真实首发/DNP/分钟、伤病/疲劳/恢复、coach与playbook实际引用、训练成长差分、阶段/赛程。优先完成真实可观测的P0，P1来源有证据再加；P2赛时Play-by-play/ACE实时行为如果未找到则标UNKNOWN，不因追求理想“全动态”编造缺失。

- 每个事实记录实际`save_id/save_instance_id/generation_id/career_id/batch_id`及对应游戏日期，身份/队伍/对手/阶段，重复采集去重。历史球员换队要沿当场所属球队，而非当前队重新写旧Box Score。
- 支持`last N games`、`vs opponent`、`before/after change`、`starter/DNP`、`injury/fatigue`、`team & player trends`及`evidence refs`的有界SQL查询。未知累积疲劳不允许指派月度高强度训练。
- 保留`NATIVE_OBSERVED / DISPLAY_OBSERVED / DERIVED_EXACT / ESTIMATED / UNKNOWN / NOT_OBSERVED`，公式产生的“估算回合/高级指标”不可冒充游戏真实tracking。
- 兼容玩家仍按月触发`full_verified_v1`完整批次；游戏历史比赛明细如会过期，必须明确游戏实际保留窗口。未经玩家批准不自动常驻监控进程、抢抓实时数据或改变常规触发频率。
- 真值数据库与GM可见`GM_SANITIZED`继续分开；尤其新秀Potential与历史全知球探问题不能借“全透明”直接透出限制内容。

## 3. 战术书专项：从“字符串匹配”升级为可用的全部原生手册、战术、绑定与执行

这项是**DEV28最先处理的高价值执行缺口**。不再把战术书“名字后缀兼容”误视成全面修复。

### 3.1 建立完整战术实体及身份目录（Antigravity采集实机、Codex统一注册）
- **BOOK_DIRECTORY**：当前版本当前加载的全部原生Books：`index/enum_id/unique_id/raw_display_name/normalized_name/owner_team_id_or_unknown/native_pointer_identity`；所有30队分别显示`team_id→expected_own_book→observed_coach_binding→actual_book_identity`及重名/改名/不可用情况。**名称只是发现线索，绑定权威是已认证游戏原生对象ID及指针关系。**
- **PLAY_CATALOG**：从真实已加载战术目录与游戏静态资源取得尽可能完整的`native_crc/CRC32 algorithm+source_text/actual_game_display_name/description/play_type/status`；`PE_STRING_MATCH`与`UI_VISIBLE_NATIVE_TYPE`分级。别名、历史真实NBA/教练战术名称的连接属于知识/语义层，不允许以`FIST`、`GIVE`、`QUICK`前缀直接宣称真实原生PlayType或谁投篮。
- **TEAM_BOOK_SLOTS**：本队68槽逐一记录`slot_index/section/CRC/linked_play_id/resolution_status/current_coach_binding/source_batch`；空槽单独记录；允许多个球队书引用同一play，不允许普通GM修改另一队书容器。
- **PLAY_USABILITY**：战术实际适用的1–4种球员PlayTypes、适合的进攻发起条件、可选受益人与再反制说明；证据分为`NAME_ONLY / TYPE_NATIVE_OBSERVED / ALLOCATION_OBSERVED / IN_GAME_USED`。实际`primary beneficiary`可能随球队分配变化，不能把一条战术固定给某个历史名人。
- **GM检索与选择**：支持`team current book`、`all selectable plays`、`plays matching given role/type/system`、`available slot for replacement`，返回**完整原生候选ID+显示名+实际可选性+认知质量+HOLD原因**，不是只有CRC序列。

### 3.1A 战术名字、真实类型与游戏2D战术板：最新玩家机制补充（2026-10-20）

> 用户提供的**实际游戏UI经验**：NBA2K22可在战术详情页面看到类似2D动态棋盘的战术演示，五名球员按战术移动；同类别不同战术可能只在走位/动作的局部有差异。名字往往携带战术年代、位置组合、动作（投篮、挡拆、手递手等）线索。**这是PLAYER_REPORTED_UI和名称解释线索，不是本仓库已经验证存在可直接读取的动画脚本/时间轴内存，更不是实机AI已照此执行的证据。**

三个不可混淆的层级与优先次序：

1. **原生PlayType认证（首要技术缺口，Antigravity）**：以实际`play_native_crc`关联当前游戏中战术类型成员关系（可能一个CRC对应多个原生分类），优先寻找游戏战术选择UI/当前进程已读取的原生类型字段、对应对象与枚举；必须明确`play_crc + native_type_id + provenance + save/build`，不能只用`FIST/GIVE/QUICK/数字`猜种类。取得可认证类型之后，GM才能根据球员四个有序PlayTypes和可用书槽做`TYPE_MATCHED_ONLY`分析；**类型匹配≠保证某球员为唯一发起人/最终投篮者**。
2. **名称语义分析（模型+可信篮球来源）**：分解原始名称中的`formation_token / action_token / numeric_sequence / era_candidate / finish_hint`等候选。用户举例`9015shot`：**仅作假设演示**，“90=90年代、15=一号位和五号位、shot=投篮”；当前尚未找到该具体游戏战术的原生来源，不能写成已证命名文法，更不能从年代代码直接认定每条2K22战术的空间、三分设计。数字可能用于位置、阵型、顺序/动作或游戏内部命名，必须结合**此条战术的原生类别/完整名称/2D演示/同家族其他例子**核验。NBA2K22玩家实际教学将FIST/PnR、QUICK/offball、GIVE/handoff等作为常用命名线索，系社区经验而非游戏官方全部语法（[2K22战术呼叫教程](https://www.reddit.com/r/MyTeam/comments/pnjrwb)、[2K社区战术命名问答](https://www.reddit.com/r/NBA2k/comments/k3wn8m)）。
3. **游戏2D演示动作证据（高价值的后续观察）**：页面可见演示则优先标注`UI_2D_DEMO_PLAYER_REPORTED`。若现有只读内存或静态原生文件能给出**可靠的战术步骤/动作时序**，可进一步定位`2D_PREVIEW_NATIVE_SEQUENCE`；**不能从“画面可播放”推定必然能提取动画帧、路径脚本、每步球员位置或有简易内存开关**。不能取证时允许玩家文字描述一个核心战术的起始站位→首传/掩护→移动/接应→终结→失败后的第二路线；此前玩家已明确无法提供截图，**不把截图、录屏或当前停在指定画面作为交付门槛**。若需要玩家说明，Codex单次任务交付已完成研究和具体问题、真正TASK_CLOSED，不能等待回答耗额度。

特别区分**三种人物职责**：

- `CALLER/ASSIGNED_PLAYER`：由谁/何种原生角色发起调用或分配此战术。当前已知Player四个有序PlayTypes影响调用资格与优先，不能凭原始名称确定具体谁被AI选中。
- `ACTION_INITIATOR / SCREEN_PARTNERS`：第一回合动作中哪位持球/传球、谁做掩护/手递手、切入者和接应位置（用户所说“1/5挡拆”等多属这个层次）。
- `PRIMARY_OPTION / SECONDARY_READ / FINISHER`：实际优先终结机会、对手封堵后第二解法以及真正完成投篮者；可能随站位、战术分支、球队指定球员和赛场AI而变化。

**绝对不固化为一名球员**：战术主体动作可由不同球员在相同位置/角色执行，2D棋子是角色而非真实姓名。完整记录结构可为：
```yaml
play_id: "2K22_PLAY_<native_crc>"
native_types: {status: UNKNOWN, memberships: []}
raw_name: "NAME_OBSERVED_OR_UNKNOWN"
name_semantics:
  tokens: []
  era_candidate: null
  positions_candidate: []
  action_candidate: []
  provenance: NAME_INFERENCE_ONLY
preview:
  available: PLAYER_REPORTED_UI
  native_steps_readable: UNKNOWN
  opening_alignment: UNKNOWN
  action_sequence: []
  branch_points: []
  first_advantage: UNKNOWN
  second_answer: UNKNOWN
actor_roles:
  assigned_caller: UNKNOWN
  initial_ball_handler_role: UNKNOWN
  screen_partners: []
  first_option_role: UNKNOWN
  later_read_roles: []
evidence:
  type_level: TYPE_UNKNOWN
  motion_level: UI_DEMO_NOT_CAPTURED
  in_game_ai_execution: NOT_OBSERVED
```

为GM建立**渐进式可用性**：
- 只有类型认证：可检索、按球员PlayTypes进行**类型兼容**，但战术动作描述仅限候选，不冒充特定受益人或固定篮球效果。
- 只有名字/社区定义：可供GM研究/备选比较，类型仍UNKNOWN，不得形成经类型筛选的确定性战术写入建议。
- 2D演示得到可靠动作标注：可描述首优势、协作角色、掩护/手递手、变化、第二解法及与年代篮球空间的差异；这只证明**预览设计**，不等于3D比赛中自动战术调用成功。
- 真实3D赛场调用被观察：单独升级`IN_GAME_EXECUTION_OBSERVED`，再研究ACE/策略覆盖、角色指派和对手反制；不要求每个1,392条CRC逐项做3D验证。

**优先原则**：原生类型的全池读数优先；然后从30队主要体系挑选有代表性的战术研究2D变化及名字语义，逐渐聚合成可复用家族知识。不要为每条战术手动看完整动画、或在玩家无法提供截图时卡死整个阶段。**“游戏战术板演示”与“比赛实际运行”属于两个不同的证据层**。

### 3.1B 用户确认的战术命名规则（2026-10-20）

已从共享池核实真实条目：`'95 FIST 15 SIDE`，CRC `0x79215B33`，`play_id=2K22_PLAY_79215b33`；静态名称与CRC已对应。玩家确认此战术在游戏中属于**挡拆**，属于`PLAYER_REPORTED_UI`事实；当前池`types.memberships=[]`仍是原生具体枚举未认证，不能擅自填入4/5/6/7。

按玩家实际游戏知识：`'95`表示1995年版本；`FIST`是挡拆动作；`15`或`1-5`表示1号位持球发起、5号位掩护的主要参与结构；`SIDE`表示侧翼执行区域，并不单独确定左侧或右侧。不同年份如'85/'05的战术可体现不同篮球时代的空间理念；名字本身不保证已考证到1995年哪支真实球队。

这不是泛泛臆测名字，而是**有实际用途的命名语法**。GM应解析`era/action/position_actors/location/finish`，识别其他战术家族中的变体；在明确以投篮终结为计划的命名中，第二位置还可能表示预定终结投篮者，不能机械解释为挡拆人。**预设计划与实际场上选择不同**：球员可能因防守失位提前传球、投篮或改变机会。

重要执行因素：球员`Play Discipline`（战术纪律性倾向）与教练`Run Plays`等战术调用设置协同影响执行既定跑位与自由进攻；NBA2K22社区亦讨论纪律、Touches、Shot、PlayTypes和Playbook共同作用，但不能假造固定阈值和概率公式。见 [Operation Sports](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)。**字段已在现行项目中确定**：`config/state_io_native/player.json`包含`PLAY_DISCIPLINE_TENDENCY`的偏移**1185/0x4A1**，教练配置包含`RunPlayTendency`。下一步是接入GM对这两项的可解释查询和业务判断、验证实际临场交互，而不是重复寻找已经登记的球员纪律性偏移。个人Tendency调整遵守本项目现行的具体提案、玩家逐项批准与Codex受控执行政策，绝不擅自改原始Ability/Potential/Badge。

证据分别记：`STATIC_LABEL_CRC_JOIN`（游戏静态名字）、`PLAYER_REPORTED_UI`（具体挡拆类型与语法）、`NATIVE_TYPE_VERIFIED`（待内存枚举认证）、`2D_DEMO_OBSERVED`（待演示轨迹）、`IN_GAME_EXECUTION_OBSERVED`（待3D比赛）。演示预览≠游戏已在实战调用。不要直接编辑生成池而不更新种子/生成器；后续D28-1由Codex在版本化原始知识层接入。

### 3.1C 玩家列出的12种战术类别与双类型映射（最新）

**完整研究与调查合同**：[NBA2K22战术类别与内存类型映射V1](../development_research/NBA2K22_PLAYBOOK_12_CATEGORY_AND_NATIVE_TYPE_MAPPING_V1.md)。本次玩家原话依次列出**12项**（逐项计数），不是11项：单打、挡拆战术、挡拆外弹中投、挡拆外弹三分、挡拆战术选项、低位背身单打、高位背身单打、后卫背身单打、中投、三分、手递手、切入。社区Coach2K和2021本世代游戏战术目录提供相应类型与部分实例，**主动检索公开文献是默认前置步骤**，不需要先让玩家逐类口述。

**纠正关键概念**：这份`PLAY_CATEGORY`（战术目录动作分类）与已登记`PLAYER_PLAY_TYPE`（球员四个有序槽位的0–15原生枚举、含None）不是同一个键空间。用户推断单个战术在内存块中有所属类型，可作为高优先级取证假说，但`play_crc→category/type membership`究竟直接存于战术对象、分类索引、UI列表还是多对多表，必须从真实内存布局确认；**不要把名称推断的4/5/6/7作为已认证映射**。用户已确认的`'95 FIST 15 SIDE`类别为挡拆，可标`PLAYER_REPORTED_UI`，但还不能硬指定本机的native_category_id。

**提供给GM的输出必须区分**`native_play_category`、`player_play_type_compatibility`、`name_semantics`、`2D_preview`、`in_game_execution`。附来源等级、当前值及可选全集；目录分类可供研究，但自动生成准确写入需要合法原生ID/CRC/所有权/审批。

**玩家截图回退流程**：Antigravity先从当前目录对象/过滤选择UI及内存布局查找；若未获得可靠类型映射，**允许请求玩家提供截图**，可能需要几十张覆盖各种战术。先明确缺哪几类/哪个页面、形成样例截图批次和已覆盖清单，按需要逐批取证；**不能以“无法截图”为默认结论**，也不能在Codex活动任务中`PAUSED/WAITING`索取资料。需要玩家介入就提交已完成发现、结束任务`TASK_CLOSED`，由玩家下一轮另行触发。

### 3.2 换帅后的技术归位与战术槽更新（Codex，复用DEV14）
必须把以下**两个单独审批/读写步骤**变成受控、可重复执行的正常业务工作流：
1. `READ_CURRENT_BINDING`：真实新档或用户确认已换帅，重新读取队/新主教练/Coach PlaybookID/原生本队同名Book对象及owner；根据真实对象身份消解该队同名Book的目标`enum_id`。匹配缺失/多候选不能凭名字任意写；先输出阻断证据。
2. `TEAM_BOOK_REBIND`：在玩家独立批准与已有DEV14身份/CAS限制下，将此队当前教练PlaybookID恢复为其本队书目标。**确认写入地址真实对应当前教练对象**，并能从游戏重读验证`coach.PlaybookID == expected_team_book.enum_id`；若UI/游戏资源重载另需操作，记录实际机制。
3. `REFRESH_POST_BIND_SOURCE`：**新批次重新读取同一个教练/实际书绑定与68槽的当前指针/CRC**；前一批的旧槽地址、旧目录与旧approval tuple不得重用。
4. `EDIT_OWN_BOOK_SLOTS`：GM选择真实有名、有合法Native ID/CRC的战术，根据主教练体系与本队球员4 PlayTypes分配到本队68槽；复用已有DEV14稀疏变更和团队独占检查。未知PlayType/CRC语义不做虚构；有认证可用的候选先做。
5. `VERIFY_EFFECT_AND_PERSISTENCE`：至少区分`write+readback`、关闭编辑页后回读、游戏保存重新加载后仍保留、真实3D场上是否调用（后者是独立后续观察，不应成为所有战术槽更新的前置）。执行回执明确处于哪一档，无法保留的操作不能标为已落地。
6. `RECOVERY`：只要部分失败，保留原始Coach/Book/slot值和已证读取；能自动恢复的按既有回滚，不可安全恢复则暂停**这一动作**并交玩家处理，**不是在Codex活跃会话等待答复**。

**当前玩家确定的业务规则仍有效**：每队长期保有本队同名书，普通GM不为了换打法切换到别队书；本队手册内容可替换为共享战术池中的其它合法战术。最小修复目标应先验证1队完整链，再扩展30队目录。不要因为需读30队的Book就把每个CRC在3D场上都演示一次，避免无边界测试。

### 3.3 针对目前`team_book()`未完全修复的进一步排查

- 根因不能再限定为“后缀匹配”一种；显式区分`DIRECTORY_NOT_LOADED / NAME_ALIAS_MISMATCH / DUPLICATE_CANDIDATES / TEAM_NATIVE_ID_MISMATCH / COACH_BINDING_DIFFERS / BOOK_OWNER_ID_INVALID / SAVE_OR_GENERATION_CHANGED / SLOT_REBIND_RECAPTURE_REQUIRED / WRITE_NOT_PERSISTED`。
- 当前`team_book()`返回`identity(index,enum_id,unique_id,name)`；**并不直接证明该Book的当前物理地址、教练挂载与后续槽读写使用同一个对象**。下一任务要从`src/gm_state_io/adapters.py`及`coach_locator`实际观察的运行时关联核对，而不是让字符串归一化承担整个绑定验证。
- 不能因为某支队名字能匹配就宣称30队已全部可执行；同时用户无需截图。AG/Codex优先静态目录→有授权的只读进程数据→必要时玩家文字描述，任务到问题点交已做成果**并彻底结束**。

## 4. 统一GM输入/输出契约与可验收动作（建议，不另起执行器）

Codex应该给外部GM一个逻辑上统一、可查询的**Capability Catalog + Observed State + Validated Native Target + Execution Receipt**；可以扩展现有M0/Registry/DEV14 CLI而不是强制照搬新命令名。

| 阶段 | GM应取得的产物 | 必须保证 |
|---|---|---|
| `DISCOVER` | 按team/coach/role/playtype等列可用功能、合法候选、含义/UNKNOWN | 候选来自当前可用版本/已认证字典，不凭模型捏造 |
| `OBSERVE` | 当前实际值/绑定/名单/最近N场及资料缺口 | 同存档同批，GM_SANITIZED，有证据与身份 |
| `REASON` | BPTI体系意图、战术角色、HOLD/INTERNAL/MARKET及财务比较 | 每个可执行目标能反向指向当前可选项 |
| `PLAN` | 按当前source生成合法稀疏目标、真实原生enum/CRC及审批tuple | 目标值存在于可选全集，限制对象/范围/字节/预期旧值 |
| `AUTHORIZE` | 玩家单独批准动作/条款、执行窗口绑定 | 文档/媒体/GM AI不能自动批准 |
| `APPLY` | 统一DEV14或专用受控合同/交易执行器 | 原生游戏确实执行受控操作，非单纯SQL修改 |
| `VERIFY` | 来源回读、save/重开持久性（按真正可测范围）、副作用、执行状态 | **拒绝把裸内存写成功冒充完成业务** |
| `FEEDBACK` | 后续正常批次中真实队伍/球员/球队策略变化 | 通过数据反馈并归档来源及不确定度 |

已有采集、执行、签约、交易、教练等专用接口保留，统一的是**契约、状态和审计回执**而非把不同业务执行器强行重写成同一个“万能内存接口”。

## 5. 下一阶段的实际开发包及协作边界

每包独立申请/授权、提交成果并TASK_CLOSED；不在检查点暂停Codex等待玩家发消息；不得连续自动越过人类必须批准的合并、存档修改或真实实机检查。

| 包 | 负责人 | 最小成果 | 验收边界 |
|---|---|---|---|
| **D28-0 当前能力与缺口清点** | Codex主、AG提供其当前完成结果 | 逐领域`EXISTING/INCOMPLETE/NOT_OBSERVED/UNKNOWN/POLICY_BLOCKED`台账；与DEV23/DEV24/Registry/M0/DEV14交叉核对，避免重复 | 静态源码和已有证据核对，不需游戏进程 |
| **D28-1 Playbook目录+绑定完整修复** | AG找真实Book/Play地址及战术名称/描述/类型；Codex做团队映射/工作流及受控执行 | Book/Play/Slot/Coach真实身份，GM能按名称/类型选择、可技术归位/改槽且获得分层回执，明确未解语义 | 先确定性静态/只读、再获批后对一队最小实机验证；不得偷带其它队改动 |
| **D28-2 其它静态操作语义目录** | AG游戏菜单/内存字典；Codex M0/Registry/BPTI整合 | 覆盖World、Gameplay、Coach、Personal Defense、PlayTypes、Tendency、Training、Roster等的当前值+完整已证合法候选+用途解释+政策边界 | 以一个家族的一次可靠读写/观测证明同编码类复用，不逐枚举全跑游戏；未知仍可查询 |
| **D28-3 动态事实DEV24扩展** | AG查游戏真实源/历史保留窗口；Codex扩展同批采集/SQLite/M0有界只读投影 | Game/schedule/Box Score、个人与球队战绩、伤病疲劳/发展事件按可见源完整入库、时间线和质量报告 | 保留`full_verified_v1`全量生产更新触发与同批一致性；无源字段NOT_OBSERVED，不追求伪tracking |
| **D28-4 统一GM选择/规划/执行完整性** | Codex负责，Web GM参与决策回读检查 | 所有已支持动作从`available option→GM提案→DEV14/业务执行器计划→批准→游戏回读`状态对齐；错误有清楚可执行原因 | 不跑全项目大回归，仅每关键动作家族少量链路验收；玩家控制真正游戏写入 |
| **D28-5 GM可用性与交付整合** | Codex+Web Analytics+GM | 每队可选项/来源/覆盖率报告、文档、示例查询、能力清单、仍BLOCKED列表、真实新档初始化说明 | 有界查询30队、3代表性本队Book、确认不会用UNKNOWN冒充VALIDATED；V4切换另批 |

调度建议：先完成`D28-0`以确认已完成工作，再优先`D28-1`解决当前战术书闭环，再根据Antigravity的真实产出安排`D28-2`和`D28-3`；最后`D28-4/D28-5`。如动态数据先完成，可并行准备接口，但**Codex不能在同一未闭合长任务中等待玩家或AG交付**。每个阶段应能独立完成并归档。

### 各方固定分工
- **Antigravity**：找游戏真正支持的目录、内存结构、静态战术名称和描述/类型、疲劳/比赛等动态源；标注`RAW_NATIVE`、`UI_OBSERVED`、`STRING_CRC_MATCH`、`PLAYER_REPORTED_UI`、`UNKNOWN`；不要重写既有执行器、假设游戏当前页面可截图。
- **Codex**：唯一负责原生Source Registry、M0 SQL投影、Book真实身份和教练绑定生命周期、DEV14/专用交易签约受控执行集成、缺失项与最小验收；收到AG成果后校验真实布局并归档，不能仅信“可写”口头声明就覆盖生产字典。
- **Web Development**：审阅真实覆盖缺口、篮球知识语义等级和BPTI的可用性，提出业务优先级及PR审查，不直接游戏写入。
- **Web Analytics/GM**：在真实GM_SANITIZED事实与已认证选项上形成分析/选择，不能返回原生未知值；GM不能操作禁止的能力字段。
- **玩家**：批准模块正式游戏写入、是否合并PR、最终世界设置/V4启用。

## 6. 不变量与完成定义（避免“只有地址，不知道怎么用”）

**静态控制目录完成**：每一项已实机或源字典观察到的可选控制，至少有值域/枚举、显示名称、所属对象、读写策略、用途/未知、来源证明；全量候选目录能按需查询；没有真实语义的不是空白而是`UNKNOWN_RESEARCH`。

**战术书完成**：30队当前加载团队书名单（若30队全部存在）、当前教练与书实际ID/指针绑定、合法的Book→Slot→CRC/名称/已知Type链路可查询；新档/换帅时在现有批准机制下做**绑定→新源回读→槽修改→最终读回**。识别不到/不能稳定保存则明确`BLOCKED`，不能只返回名字匹配成功。

**动态事实完成**：所有经过实机证据确认、游戏内确实留存的比赛/球员/球队/身体状态来源，具备历史键、更新时间、身份、覆盖率、已观察/估算标识；游戏不提供的字段有缺口和退化路径。**不能声称捕捉到没有来源的Play-by-play或赛场AI事件**。

**GM可操作完成**：每条正式支持的GM动作都能从已知选项构成提案，经过确定性校验/实际执行/读回/状态对齐；凡不能生效或存在权限限制，GM得到明确原因并能选择HOLD或已证替代，而不是以为可用却静默失效。

**证据层分级**：`SOURCE_DISCOVERED / RAW_READ_VERIFIED / OPTION_SET_VERIFIED / PLAN_VERIFIED / GAME_WRITE_READBACK / SAVE_RELOAD_VERIFIED / GAMEPLAY_EFFECT_OBSERVED`。只完成前几级不等于达到后几级。游戏中一次实际局部失败允许后续修复，但不准把未测操作写成全面已验收。

**运营底线**：别把成熟的19 Coach、18 Personal Defense、交易/签约、99倾向/PlayTypes、训练字段重复造一份；不要因“追求全透明”暴露新秀隐藏Potential或取消玩家审批；不要修改普通球员能力，保持游戏自然成长和竞技权威。

## 7. 和PR #12及其它旧任务的精确关系

- **PR #12/C仍只修F1–F4**：B5蓝图演化修订一致、前态存档实例隔离、B4不将原生动作缺失错误升级为市场禁用、M3选择不接受BLOCKED/RESEARCH的内部动作。**不要为了本计划在PR #12实现全量Books/DEV24或改变BPTI原生执行白名单**。修完做少量直接测试并申请用户审查/合并。
- **DEV23**：战术语义基础事实与UNKNOWN清单，不能把89个CRC名称匹配推断成全部类型可写。
- **DEV24**：动态比赛与高级统计需求来源，是D28-3权威数据字典规划。
- **DEV27**：保留名字后缀兼容最小修复作为已完成事实，D28-1处理更深层真实绑定/全书目录，不把它撤销或冒充已完成完整生命周期。
- **DEV16/17/18**：沿用两Codex所有权与“每队同名书+修改本队槽”的业务规范；本计划的D28-1是由真实错误需求驱动的执行接口完善，不要求30队共享Playbook克隆。
- **M3/M4**：M3负责真正经营与球员战术调整；M4负责工程问题反馈与路线记录，不把本计划重新叫M4、也不重写M4；V3/V4的正式启用仍需玩家。
- **GM World实时赛场竞技参数调校**：独立未来任务，不以Quick Sim为目标；本计划只是让选项可用、来源可信、执行正确，不承担比赛公平性的长周期实战调参验收。

**交付原则**：先让GM能看懂并正确操控已证明真实存在的功能，再增补没有观察的数据；未知公开列出，不允许“有一个地址”替代完整经营能力，也不允许每个未证假设都把任务变成无限研究。

## 8. 机制研究先行：规范化来源策略

玩家已正式要求Codex开发**先搜索社区、游戏攻略与官方手册，理解游戏机制后再实现**。详情见[游戏机制研究先行开发规范V1](../../docs/GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md)。DEV28 D28-0盘点与D28-1战术类型/手册、D28-2训练与教练选项、D28-3数据源完整性都必须先从已有证据、**社区和游戏攻略、2K官方手册/开发者材料（包含本世代与次世代）**理解机制，再让Antigravity确认目标PC本世代的实际菜单、原生字段与内存结构。**跨世代机制概念可借鉴，不要求一律是PC专用研究资料；具体执行接口仍需PC原生证据。**战术名称可先按已知规则与社区资料理解，不能为等待每条CRC类型内存认证而彻底中止语义知识输出。用户允许必要时分批提供战术分类截图；遇到必须人类提供信息的点提交现有成果后TASK_CLOSED。任何新测试/游戏写入/下一工作包仍需单独授权；当前PR #12纯合并冲突不因本规范触发扩大研究。

