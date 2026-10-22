# R06-D — NBA2K22世界运行、比赛、历史与存档跨域知识整合（DEV29）

> 2026-10-21；**研究已发布，待独立审核**：`R06_D_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`。目标为NBA2K22 PC本世代离线MyLEAGUE。R01–R06-C均**只作现有研究输入，不重新启动**；产物是游戏知识、菜单/可见事实与联动及缺口，不设计Coach/Player/Media人格、模型仲裁、GM最优策略或DEV28 I/O程序。**本轮没有连接游戏、变更设置、触发自动推进、保存存档或采集发布数据。** 逐项映射见[机读关联与缺口目录](../catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)。

## 1. 证据和数值采用什么口径

- `SOURCE_DOCUMENTED`只表示**直接原始来源支持原先研究项的限定事实**；`PROJECT_STATIC_REGISTERED`是技术登记；`PLAYER_REPORTED_PC22`是同版玩家报告；`OTHER_VERSION_REFERENCE`仅跨代参考；`CURRENT_SAVE_VERIFIED`需要实际游戏当前档/字段与本轮可核对批次。本研究**未新增后者**。
- **26条关系**不是26条因果公式。分为语义不能混同、条件相互作用、时点依赖、数据来源和权威隔离、证据缺口等。关联来源为各原研究卡所链接的目录项，**来源支持一个原语义不代表已证明两个原语义的引擎因果**。
- R06-A：86条`settings+world`静态候选与118类Setup/Simulation/3D Gameplay菜单候选，**不是204个独立已采/安全可写原生字段**。R06-B：31类历史/媒体/奖项研究概念，其中10类奖项直接匹配来源不足已降级为空来源，独立审核尚未确认修复通过。R06-C：38类阶段/存档/留存概念，其中7类无直接来源。R05-D另有54项异质数据候选及63项操作研究项，**不能相加当作一个原生字段总数**。
- 原生2K22真实赛场和比赛数据、外部历史规则、跨平台官方/社区经验、玩家自由决定、CodeX已证执行器必须分开。2K官方列NBA2K22的MyLEAGUE为离线可用，不证明Steam Cloud/Autosave可靠（既有SRC-0187）；官方2K23 Eras明确PS5/XSX版本，不代表PC22可直接调用（SRC-0174）。
- **源目录不补造来源**：所有R06-B unsourced awards维持`sources=[]`；不为填满来源栏而用无关论坛帖子。R06-C无来源项亦保留原状。

## 2. 六层游戏事实不是一份总表

| 层 | 游戏里研究什么 | 下一层如何利用，不能推断什么 |
|---|---|---|
| `GAME_CLOCK_AND_IDENTITY` | 游戏日期、Season、日历阶段、真实Save槽、球员/球队/比赛ID | 真实2026年不是游戏2026年；新GitHub批次不等于推进一季 |
| `ENGINE_AND_MODE` | 实场3D USER/CPU、CPUvsCPU、SimCast Jump-in、Calendar Sim、原生Gameplay与Sim两套设置 | 全队被User经营不代表10个球员全读USER侧滑块 |
| `DYNAMIC_FACTS` | GameID→比分→逐场Box/Shot→赛季累计、伤病、身体与自然成长 | 不能从Season总计反造逐场因果或球员完整历史 |
| `CONTROL_AND_MARKET` | 教练/战术/个人倾向、训练、交易/选秀、合同/Staff/规则选项 | 研究有菜单≠能用原生地址执行；球员能力普通经营禁直改 |
| `HISTORY_AND_MEDIA` | 冠军、奖项、纪录、退役、Rule Change历史、Social/Power Rankings/Mock Draft | 媒体预测不是已发生交易或真实选秀；现实NBA荣誉不是存档奖励 |
| `PERSISTENCE_AND_EXTERNAL_SYNC` | Save/Save as/Autosave/Reload、DEV14托管save代次、full_verified_v1、GitHub批次、外部研究历史 | 游戏物理存档、SQLite、媒体叙事和现实时间是多份独立来源 |

## 3. 六个高价值跨域交互（WHAT / HOW / WHY / EVIDENCE LIMIT）

### 3.1 同一场比赛会出现四份“看似相同”的统计

`GameID→LIVE_3D / CALENDAR_SIM / SIMCAST→现场比分→赛后Box→日历比分→赛季累计`。两个Normalize（Minutes、Stats）也必须独立观测，不能因项目原Registry登记一项`simulation.normalize_stats`就说两项皆可读。2K22有Normalize导致比分变化的社区个例（R06-A SRC-0170），没有普遍固定倍率实证。因此先规定各数字的来源、游戏模式、时间、保存后是否存在；再谈真正分析球员表现。R01缺逐场Game Log仍是DEV28高价值技术候选，**不是DEV29现在执行采集的许可证**。关联：X01/X02/X03/X16/X20。

### 3.2 Coach/Playbook/PlayTypes与3D、Sim联动不能用相似词代替实证

教练本队Book、POE、Run Plays、四类个人PlayTypes/Touches与NBA2K22真实3D比赛存在机制关系研究资料，但ACE是否临场覆盖及防守个人设置对球员真实执行仍需分模式/比赛实测。`Team Pace`的日历Simulation滑块**不是**实场自动叫战术频率，也不是GameBox算出的Pace；统一存一个“pace”字段会污染分析。游戏Slider总体防守强度与教练个人防守设定同理。R04B的99个Tendency字节与原网站99个名字仍不能靠位置自动配对。关联X04/X05/X06/X25。

### 3.3 原生自然成长和合同流动是两个不同世界动作

球队训练负荷、个人训练、伤病、耐久、Staff影响自然成长的具体数学效应仍未知；潜力/徽章/属性改值不属于普通GM经营。`FA Moratorium`、合同到期、签约条件、Bird/RFA、报价和实际签约生效是不同对象；新版休赛期外挂竞价规划和仍未开放的真实签约写入不能取代原生生效与保存验证。R06-C所述赛末、抽签、员工、选秀、自由市场、训练营存档建议不是PC22经逐页认证的七个唯一阶段。关联X07/X08/X09/X23/X26。

### 3.4 三套时间轴与选秀/规则履历不能互相覆盖

`GAME_SEASON`从2021–22开始；`DRAFT_CYCLE_YEAR`按1984→2020轮回，必须看确已发生的选秀，而不是加一赛季就自动视为选秀完成；`REFERENCE_ERA`只存历史参考。原生历史Draft Class目录并不保证本项目所有年份的克隆ID完备。**选秀权世界V4取消了人为三届上限，但相关旧执行器+3校验未同步**；这是独立Codex维护的已知差距，不能由R06借机改代码。游戏原生Rule Changes/旧CBA和外部项目选秀政策也分别归档。关联X10/X11/X12/X13/X22。

### 3.5 奖项/记录/媒体必须保留“正式事件”和“观点”的身份

一个赛季的游戏MVP、冠军、历史纪录、退役资料有不同产生与保存时点。已直接确认的同版玩家历史菜单线索只有Past MVPs/Past Rule Changes/Retired Jerseys及HOF提问；另10类候选`sources=[]`不应升级为已证PC22完整获奖菜单。PC同版媒体Mod说明Social/Power Rankings/Mock Draft文字资源，但这不等于媒体已被赋予外挂叙事人格或内容注入API。Mock Draft预测与选秀大会实际决定不能共用`DRAFT_RESULT`。关联X14/X15/X17/X21/X24。

### 3.6 一个“保存成功”的说法需要明确是哪一份资产

`Game Save Slot`、`DEV14 managed save_id/save_instance_id/generation_id`、`SQLite league/pool/control`、`GitHub latest.json`和未来外部角色记忆均不同。MyLEAGUE本身可离线使用，但不保证Steam Cloud有保存某个槽，也不说明Autosave覆盖策略；Steam玩家“Save as失败”是个案而不是普遍Bug。跨季Game Log/历史比赛/奖项保留期限未知；不可把研究用数据清单当作已经能重载的原生存档。关联X18/X19/X20/X24。

## 4. 逐条跨域关系：26条可定位机制关联

以下表格的`relationship_class`是**研究用途分类**，不是原生游戏方程。精确的两个或多个关联目录ID、目标游戏状态和观察需求见对应机读JSON；凡`UNKNOWN/CONDITIONAL`均不得转写为确定的因果句。

| ID | 关系说明 | 关系类别 | 原生证据限制 |
|---|---|---|---|
| X01 | 真实3D与日历模拟是不同计算路径 | SEPARATION | 已证玩家区分比赛方式；没有PC22当前GameID模式标记/引擎公式 |
| X02 | 三分的Sim出手、3D命中环境与个人投篮倾向不得等同 | SEMANTIC_DIFFERENCE | 三类原生对象不同；不能由Sim命中推断个人倾向已改变 |
| X03 | 3D全局出手倾向与个人Tendency是独立对象 | SEMANTIC_DIFFERENCE | 引擎作用顺序、叠加量、具体消费者未认证 |
| X04 | Coach战术/POE、球员PlayTypes与场上结果可能联动 | CONDITIONAL_INTERACTION | 是研究中的联动假设；不从单场因果倒推唯一设置 |
| X05 | Coach设置与日历模拟行为的映射未证 | UNKNOWN_INTERACTION | 不能把3D ACE实际战术效果当Sim策略权重 |
| X06 | 教练和球员防守设置与3D Help Defense不应同值解释 | SEMANTIC_DIFFERENCE | 个人/球队防守指令≠全局防守滑块；内存作用细节需认证 |
| X07 | 伤病事件/疲劳恢复需要按游戏模式与时间窗口建档 | DATA_DEPENDENCY | 不存在本批可用同位疲劳数值；事件发生机制未精确量化 |
| X08 | 训练、耐久、Staff对自然成长与恢复的作用需要分离 | CONDITIONAL_INTERACTION | 旧版/跨世代机制参考不证明PC22稳定效果公式，普通经营禁直接编辑能力 |
| X09 | 自由市场报价、合同状态和真实阶段需三者同时核对 | TEMPORAL_DEPENDENCY | 合同类型/资格、当前FA阶段、获批执行与游戏重进持久互不等价 |
| X10 | 交易允许动作与交易截止阶段分开 | TEMPORAL_DEPENDENCY | 现实NBA截止日不能作为游戏内法律日期；外部交易器亦非原生UI规则的替代 |
| X11 | 1984–2020历史选秀轮回依赖真实完成选秀而非时间推断 | WORLDLINE_SEPARATION | 选秀轮回属玩家外部规则；原生GameYear与对应历史届不等同 |
| X12 | 历史Draft Class加载与抽签/Scout流程需独立身份认证 | RESEARCH_DEPENDENCY | 外部克隆Type与实际Draft Class中球员ID未自动一一对应 |
| X13 | 选秀资产未来年限是游戏资产来源/业务规则/执行代码三层 | POLICY_TECHNICAL_SEPARATION | 世界政策已撤旧+3；执行代码仍有拒绝，读到五届不是强制新上限 |
| X14 | 获奖记录与跨年持久保留不是同一能力 | TEMPORAL_DEPENDENCY | 2K22玩家仅报告部分历史菜单；完整历季获奖者记录和PC22读取未知 |
| X15 | 其他10类荣誉是待证研究候选不可当PC22菜单证据 | EVIDENCE_AUDIT | R06B 10项sources=[]；不可再用Past MVPs Reddit帖为它们背书 |
| X16 | NBA纪录和单场Box留存不等同 | RESEARCH_DEPENDENCY | 纪录页有时汇总但无法倒推每场投篮事件，跨季GameLog留存未证 |
| X17 | 社交消息/实力榜/Mock Draft的观点不等于正式事实 | AUTHORITY_SEPARATION | Mod内容文字资源≠当前无Mod完整动态数据/独立人格；mock≠真实选秀结果 |
| X18 | 游戏Save/Save As与DEV14托管存档及发布数据库独立 | STATE_AUTHORITY_SEPARATION | 保存是否成功须退出重入验证；GitHub库新批次不是游戏Save revision |
| X19 | Autosave/云同步/离线支持不能互相证明 | STATE_AUTHORITY_SEPARATION | 官方离线支持不保证SteamCloud同步；Autosave机制未知 |
| X20 | 3D末比分/日历结果/标准化统计必须同GameID区别保留 | DATA_INTEGRITY | 玩家单一故障案例不得当确定缩放公式；缺逐场来源不可重建比赛 |
| X21 | 原生球员潜力与球探报告需要保护认知层差异 | OBSERVATION_AUTHORITY | 真实隐藏能力不应通过媒体预测/Scout编号泄漏，未证明球探概率 |
| X22 | 规则投票、当前活跃规则与外挂政策不可混为一体 | RULE_AUTHORITY | 老代菜单不能当本机合法枚举；外挂选秀V4不是游戏规则投票 |
| X23 | 退役/转教练、员工招聘需要跨年身份与阶段留存 | TEMPORAL_DEPENDENCY | 同版社区教程可能要求非法改球员能力；本研究仅保留界面线索 |
| X24 | 连贯媒体记忆依赖可信历史数据，不是游戏原生记者代理 | RESEARCH_DEPENDENCY | 历史GameLog/奖项存储未知；本项目外部媒体模型未开发 |
| X25 | 教练技战术、逐场反馈与日历Sim不可通过同一统计推断 | EVIDENCE_CAUSALITY | 缺3D/Sim分域Game Log及对照条件，不能将团队风格变化归因为唯一Coach字段 |
| X26 | 训练/休息阶段与球员自然成长需要观察而不是直接增强 | EVIDENCE_CAUSALITY | 本局训练与成长数值未在该研究轮读取，不能直改能力 |
 
## 5. 原生/资料缺口：20项（不是20个授权开发任务）

| 缺口ID | 研究关注优先序 | 未认证原料 | 当前限制 |
|---|---|---|---|
| D06-G01 | P0 | 单场Game Logs/Box/Shot与赛季聚合 | UNVERIFIED_CURRENT_SAVE_CAPTURE |
| D06-G02 | P0 | 比赛生成路径3D/SimCast/QuickSim | MODE_EFFECT_UNKNOWN |
| D06-G03 | P0 | Normalize Minutes与Stats两个开关及分数冲突 | NATIVE_ENUM_AND_FIELD_MAPPING_UNKNOWN |
| D06-G04 | P0 | 原生game_date、赛季phase和外部采集批次关联 | GAME_DATE_NATIVE_SOURCE_NOT_VERIFIED |
| D06-G05 | P0 | Save/Save as/Autosave退出重载持久化 | NO_TARGET_SAVE_RELOAD_TEST |
| D06-G06 | P0 | 选秀年、实际导入新秀与完成选秀触发 | DRAFT_CLASS_CYCLE_AND_NATIVE_IDS_UNVERIFIED |
| D06-G07 | P0 | 休赛期各阶段及原生AI签约/合同变动 | PC22_PHASE_RUNTIME_UNKNOWN |
| D06-G08 | P0 | 交易资产V4规则和旧+3程序拒绝 | KNOWN_POLICY_EXECUTOR_DIVERGENCE |
| D06-G09 | P1 | 教练默认、对手防守、ACE与Sim效果 | ON_COURT_CAUSALITY_UNVERIFIED |
| D06-G10 | P1 | 训练疲劳伤病的实际分域数据 | NATIVE_HEALTH_AND_EFFECT_UNKNOWN |
| D06-G11 | P1 | Draft/scouting历史名单与球员身份 | PLAYER_DRAFT_ID_MAPPING_UNKNOWN |
| D06-G12 | P1 | Past MVP/其它奖项历年获奖者 | 10_CANDIDATE_AWARDS_UNSOURCED |
| D06-G13 | P1 | 职业、赛季、季后赛纪录的维度和刷新 | PC22_RECORD_UI_AND_RETENTION_UNKNOWN |
| D06-G14 | P1 | 跨赛季逐场GameLog/Box/交易/选秀/奖项留存 | CROSS_SEASON_RETENTION_UNKNOWN |
| D06-G15 | P1 | 媒体文本、实力榜与Mock Draft事实性 | UNMODDED_PC22_UI_AND_PROVENANCE_UNKNOWN |
| D06-G16 | P1 | Rule Changes合法选项及何时生效 | TARGET_PC22_MENU_AND_VOTE_HISTORY_UNKNOWN |
| D06-G17 | P1 | 薪资帽空间、Staff预算、合同状态、市场可写性 | BUDGET_AND_EXECUTOR_VALIDATION_GAPS |
| D06-G18 | P2 | 2K23 Eras与本世界1984轮回对照说明 | CROSS_VERSION_REFERENCE_ONLY |
| D06-G19 | P2 | Save云端与本地文件权限/可靠性 | STEAM_CLOUD_NOT_GAME_SAVE_PROOF |
| D06-G20 | P1 | R06-B独立质量复核 | REPAIR_SUBMITTED_REVIEW_PENDING |

以上优先级只是**研究证据重要度**，不是Codex开发排期，也不是批准任何执行。尤其D06-G08现行世界选秀政策与旧+3执行代码不一致，需要玩家**另行授权**Codex小范围代码同步，禁止在本研究中顺带修复。

## 6. R07应继承什么，而不替角色下决策

R07的职责是把K01–K12已有原始研究关联为统一的**观察/选项/版本/来源/技术认证/历史留存**矩阵：
1. `WHO_CAN_OBSERVE`仅反映游戏可见公开/私有事实的研究候选，不硬写球员“必然同意/拒绝”。
2. `WHAT_ACTION_EXISTS`区分`SERIES_REFERENCE`、`PC22_MENU_EVIDENCE`、`PROJECT_NATIVE_REGISTERED`、`RUNTIME_VERIFIED`、`PLAYER_APPROVED_EXECUTABLE`；后两者不能由研究文件推定。
3. `EVIDENCE_CHAIN`须按`catalog_id/item_id→准确SRC/PROJECT_FILE→所支持句子→存档批次`引用，无匹配直证即留空而非捏造；沿用R06-B审核标准。
4. `FEEDBACK`与`HISTORY`仅列实际可发生的比赛/签约/选秀/新闻观察及可能保存时间，不能编写Agent人格、世界调度、谈判优先级。
5. `FINAL-CODEX`只能待R07结束、玩家另行授权后对照已有DEV14/Registry/M0/SQLite和DEV28缺口做有限工程整理；本R06-D不发Codex任务。

## 7. R06-D交付与可诚实宣告的完成状态

完成的只有**跨领域研究整合和证据/原生能力缺口编目**。输入目录都沿用原来的受审核状态，没有升级任何PC22当前存档合法值、原生读写状态、Save重入状态；本轮没有新增SRC或VIS（而是重用先前研究并已核查的来源），新增原版PC22完整UI截图=0。

`R06_D_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`；R06系列研究汇总已发布，但不自行宣告独立审核已接受。建议下一轮`R07_CROSS_RESEARCH_ROLE_OBSERVABLE_ACTION_EVIDENCE_MATRIX`在审阅后开始；任何人格系统/代码实现/自动游戏操作均不在当前研究权限内。