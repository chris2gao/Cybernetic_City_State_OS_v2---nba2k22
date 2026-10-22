# DEV21 — BPTI 三方并行深度研究与Codex前置交接计划 V1

2026-10-20 | 负责人：Web Development GPT | 状态：RESEARCH_PLAN_ACTIVE / NO_BPTI_CODEX_IMPLEMENTATION | 优先于DEV19早期的先修Bug/双引擎校准顺序。文档授权范围：玩家已要求规划三方研究；**不授权游戏内存写入、全量游戏采集、自动启用V4、自动合并PR、额外工程测试**。

> **R1进展（2026-10-20）**：GPT Deep Research R1报告已按原文归档到 [BPTI R1 完整研究](../development_research/BPTI_R1_BASKETBALL_SYSTEMS_DEEP_RESEARCH_V1.md)（607行、10张非互斥SystemCard、R1-S01～S32来源索引）。[R1审核记录](../development_reviews/BPTI_R1_DEEP_RESEARCH_REVIEW_V1.md)结论为 **ACCEPTED_FOR_INTEGRATION**，关键NBA官方数字经抽样核实；原报告ChatGPT临时引用需在R4转换为可持久访问的Claim→SourceID，2K22原生字段映射未完成。**R2 Gemini研究待收，R3映射与R4整合尚未完成，BPTI Codex实现未获本次授权。**

> **2026-10-20三路研究整合进度（覆盖旧“R2待收、R3待完成”描述）：** R1完整报告及独立审核已入库；R2-V2由GPT Deep Research补位Gemini完成，30/30历史档案与结构化表[归档](../development_research/BPTI_R2_30_FRANCHISE_IDENTITIES_AND_EVOLUTION_DEEP_RESEARCH_V2.md)，[审核](../development_reviews/BPTI_R2_V2_DEEP_RESEARCH_REVIEW_V1.md)认可为研究候选，少数[来源缺口已部分补录](../development_research/BPTI_R2_SOURCE_REPAIR_ADDENDUM_V1.md)；R3 [2K22原生机制映射](../development_research/BPTI_R3_NBA2K22_NATIVE_MAPPING_AND_CONFLICTS_V1.md)已完成架构研究；R4 [三路整合与工程规格](../development_research/BPTI_R4_RESEARCH_INTEGRATION_AND_ENGINEERING_HANDOFF_V1.md)已形成。**下一份供玩家批准的Codex阶段入口是[DEV22](DEV_20261020_22_BPTI_RESEARCH_TO_CODEX_PHASED_HANDOFF_V1.md)。R2缺证/2K22战术语义UNKNOWN需保留，BPTI代码未启动，GM V4未启用。**

## 0. 修订后的优先级与独立上线门

新顺序：M4工程由M系列Codex继续；与此同时GPT Deep Research、Gemini Deep Research、当前Web GPT提前分头完成BPTI调查；三方研究在Codex启动BPTI工程前交叉审阅/整合；**随后由Codex实施BPTI**；Issue #6等底层Bug修复、季后赛逐场/高阶统计采集及3D/Calendar Fast-Sim年度校准工程可安排在BPTI之后。

依赖判断：BPTI系统卡、2021组织史、球队哲学候选及基于已认证原生字段的战术推理，不依赖新的逐场季后赛源。PR #4目前已在GitHub合并，M3-T接口为可用工程底座。尚未修Issue #6时，不得假称全量Registry采集已经正式通过；BPTI的**30队历史候选**可以预制，**30队真实批次绑定/生产验收和最终开档**需要在新保存档和可靠脱敏来源具备后进行。双引擎校准器可以后开发；首次年度校准必须有首次季后赛真实样本，不能是开档前已达成的统计效果。

M4=外挂技术问题及需求自我进化；GM经营反馈=比赛/交易/战术的球队经营；3D vs Calendar Fast-Sim的模拟统计校准=独立校准器。BPTI是前置于GM数据决策的篮球哲学及战术认知。职责不混合。

## 1. 现有资产与R0缺口审计

必须阅读仓库public/main：
- `docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md`
- `docs/development_research/DEV10_M2_BASKETBALL_AND_FRANCHISE_RESEARCH_V1.md`（**12张技战术卡**+30队2021现实背景种子，不是完整篮球体系）
- `docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md`（2K22行为社区观察，未认证细节需保留）
- `docs/GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH.md`、`web_gm/schemas/TEAM_STRATEGY_STATE_V1.json`
- `web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md`、`web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md`
- `AGENTS.md`、`docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md` V2。

目前已知：8个原生教练体系、19教练设置、各队同名68-slot book、4 PlayTypes+Initiator、48具名倾向、18项PERSONAL_DEFENSE、训练及角色轮换等进入M3-T；真实slot CRC→战术动作/受益人未全部确证、51未知倾向无语义，不能编造。普通GM能力/潜力/徽章不改；已有玩家单独批准的战术性Tendencies、PlayTypes等仍要逐次批准游戏写入。教练合同/任命执行暂不完整。**有字段不代表知道它的行为影响**。

现有历史30队seed多为2021 Draft Outlook，偏组织/选秀大背景，远不足以独立推断30队教练哲学；要扩充球队组织价值、教练战术路线及主副体系的**事实与推论边界**。不可从当前阵容表现倒推所谓文化。

## 2. 三条并行研究流（资源不重叠）

### R1 — GPT Deep Research：篮球战术原理、体系设计、战术反制（篮球科学）

目标：以真实篮球教练教学/历史实战为依据，研究10个可交叉组合的篮球家族，而非归纳10套均衡的2K设置。优先FIBA/WABC Level1–3、NBA官方战术分析、教练一手访谈、NBA Coaches Association；另用专业教练文献/战术分析交叉核查。围绕：
1. Motion/Read-and-React，Triangle/Inside-Out，Spread PnR，Isolation/Midrange Creator，Post/High-Low，Point-Center/Elbow Hub，Transition/Early Offense；
2. Defense-First/Rim Protection，Switchable Pressure Defense，Adaptive/Multiple Systems。
每种至少呈现：攻防基本原理与真实“优势产生→反应→防守反制→二次/三次应变”因果链；角色技能/无球职责/空间；组织者vs自主创造者的自由度条件；弱点/机会成本；适用的阵容原型、例外场景；现实典型赛季和反面案例；能被比赛数据辅助观察的信号，但不能把统计相关性当战术因果。
攻防模型正交（可自由组合），不把2014马刺/2022勇士/1996公牛固化成全部其他球队的复制模板。明确球员自由并非全员无限自主，而是“结构内的选择权”。关注抗魔球同质化同时接受证据反驳。
交付 `R1_BASKETBALL_SYSTEMS_REPORT.md`、`R1_SYSTEM_CARDS.json或结构化附录`、`R1_SOURCES.md`，标注真实出处/URL/发行年/解释层级，中文为主，英文本源优先。不需Codex代码。

### R2 — Gemini Deep Research：30队历史组织文化、2021教练哲学、篮球演化（历史组织）

目标：形成每队独立的**历史事实参考**和可以转化为篮球身份的研究，而不是基于当前阵容的GM正式决策。范围2021–22赛季开始节点，历史延伸1984–2021用于理解组织文化（例如乔丹公牛、科比/奥尼尔湖人、马刺邓肯时代等），不要把2024–2026的人员或制度直接输入2021开始的世界线。
30队每队：组织文化的有据事迹，2021–22主帅及其战术偏好（无法证实时UNKNOWN），总经理/管理理念的有据事实，区别“多年球队传统”与“任期内主帅临场体系”与“当季阵容”，进攻/防守可选路线（作为研究推论），球员创造力与体系适应、长期建队哲学、一次历史转型案例（有证据才写）、转型触发条件（研究建议）、反证/异议。
兼顾2021–22非争冠球队不能被假称有独特固定战术“传统”；适当标NOT_EVIDENCED，允许虚构联盟中随后演化形成新身份。不要拿联盟高效打法统一替代球队哲学，也不要机械从城市/队名捏文化。
优先NBA/球队官方历史、官方教练访谈、真实球队赛季资料、严肃战术与组织分析；社区评论只能辅助且明确级别。与R1交接只引用统一system_family IDs，不自行研究2K22具体raw值。
交付 `R2_30_FRANCHISE_IDENTITIES.md`、`R2_TEAM_SEEDS.json或结构化表`、`R2_HISTORICAL_TRANSITIONS.md`、`R2_SOURCES.md`。30/30历史参考覆盖，完全没有证据的项明确留空。

### R3 — 当前Web GPT：NBA2K22 PC Current Gen原生行为、游戏字段映射、证据冲突审阅（游戏落地）

目标：从仓库M3-T/DEV14真实接口出发，寻找NBA2K22 PC current-gen当代官方/玩家实践资料，建立 `BASKETBALL_INTENT_TO_2K_MAPPING` 事实与假设矩阵：
- 8教练系统、Active/Preferred、Freelance、POE、RunPlayTendency、Tempo（语义待证）；
- 本队唯一68个slot/现有可定位CRC → 未必可理解真实动作；优先确认所需核心战术动作而非全量破解；
- 4 PlayTypes、Initiator、Touch/Shot/ISO/Post/Drive等48具名Tendencies；个人18项防守及对手适应、轮换/训练；
- 逐条说明语义、必要输入、关联的SystemCard角色、执行效果证据等级、已知冲突、HOLD/降级替代、实际项目接口与不支持边界；
- 对社区中Touch被认为主要影响Freelance与被称对战术调用影响大的分歧、战术调用面向特定硬编码球员的投诉建立CONFLICT_RECORD，而不是选择看起来对的一个说法；游戏子世代限制严格核查，NBA2K22新世代MyNBA功能不能直接套用PC旧世代终极联盟。
当前Web GPT还担任R1/R2合稿的**独立证据审阅和跨角色接口协调者**，不改写两模型发现的真实篮球出处，不给工程未知做无来源补全。
交付 `R3_2K22_NATIVE_MAPPING.md`、`R3_KNOWN_CONFLICTS_AND_GAPS.md`、`R3_RESEARCH_SOURCE_INDEX.md`；本轮可以先出R0已知能力/高风险条目，R1/R2返回后补最终映射。

## 3. 统一研究证据标准和交付合同

每条关键claim卡建议如下字段（文档或JSON均可，Codex后续才定严格schema）：
- `claim_id`, `statement`, `domain` (BASKETBALL_PRINCIPLE/FRANCHISE_HISTORY/COACH_PHILOSOPHY/2K_NATIVE/2K_COMMUNITY/GM_INFERENCE), `applies_to_seasons`, `platform` (NBA2K22_PC_CURRENT_GEN/OTHER/NA), `source_url/title/author/published_at`, `source_excerpt_or_page`, `support_level`, `counterevidence`, `status` (VERIFIED_SUPPORTED/HYPOTHESIS/CONFLICTING/UNKNOWN), `downstream_use`。
- 对用户当局真实数据和球员合同：不得从现实NBA网站直接导入；只引用以后真正的同批事实。
- 真实NBA战术“合理” ≠ 2K22原生支持；社区讨论“玩家曾观察” ≠ 当前PC已经复现；合成逻辑通过 ≠ 真正比赛验证；每一步保留独立证据标签。
- 每个系统卡要指出创造机会的机制、球员需要的天赋、进攻/防守对策和改变体系的条件，不能只写“擅长传球、重视三分、注重团队”。
- 使用短引用与原创概括，保留URL、页面/段落、日期；禁止大篇复制论文/PDF及上传全文版权资料。
- 研究结果允许矛盾和UNKNOWN；跨源冲突不能为了让成果看起来完整而人工消除。
- 研究项目只提供`RESEARCH_CANDIDATE`和篮球意图，不带可立即执行的raw字节、批准或游戏操作指令。

## 4. 工作顺序（在Codex开发BPTI之前）

R0：Web GPT完成已有仓库与首批外部源审核，发布计划/源与缺口指针，发出R1/R2提示词；M4 Codex可并行开发，不等待研究完成。
R1/R2：GPT Deep Research 与 Gemini Deep Research **由玩家分别手动触发**。它们可以读公开GitHub链接，但**网页查阅不等于可直接git push或改本地SQLite**；默认在聊天完整输出可供审阅的报告/结构化交接，若确有授权上传途径再将结果写回对应研究文档。不要在两份研究报告中擅自认定已提交GitHub。
R3：Web GPT进行原生2K22证据核查与仓库约束映射，可与R1/R2并行。
R4：三方成果返回后，由Web GPT/开发规划模型检查引用、年份、平台、相互矛盾、可映射性，形成 `BPTI_RESEARCH_INTEGRATION_V1` + 系统卡/球队卡+映射矩阵+待证清单。给玩家审阅，再交Codex分阶段B0/B1/...建设；**不能把未经审阅的研究直接交Codex自动编码**。
M4完成后可以启动BPTI研究以外的实现计划；如R1/R2未完成，Codex仅能处理已研究充分的部分，不编造其余内容。本期重点为先完成研究再进行Codex正式实现。

## 5. 研究结束判据（不等于开档验收）

- 10个非互斥体系：都有完整篮球因果/角色/反制/创造权说明及可引用现实证据；能够区分团队传切、巨星创造、低位、控球核心与不同防守理念。
- 30队：有可检索2021历史参考（组织文化、教练时代及变化条件）；不强制30种人工不同Playbook，证据薄弱项明确UNKNOWN。
- 2K22映射：每种拟实施核心篮球行为至少有一个**已知游戏控制方向或可靠最小候选**；分清直接原生字段、社区猜测、未解CRC/51倾向和能力不允许修改的边界；未实证候选不能被Codex写成确定映射。
- 代表性GSW Motion/CHI DeRozan creator/MIA switching defense与一个历史巨星易队/时代演变情境，能从真实篮球逻辑给出**差异化业务推论**（不是本局正式经营方案）。
- 交付物可由Codex获取：GitHub轻量Markdown+可解析附录或玩家显式转交的完整研究报告；来源可靠、冲突暴露、范围锁定；即使未形成所有游戏战术ID，仍能开始有证范围内的认知编排。
- 不要求在此研究阶段提前跑游戏/测试胜率/反复采集/一口气破解全部68槽和51未知项。

## 6. 已核对的高价值初始来源（供三个模型延伸，不等于已完整研读）

官方篮球：
- FIBA/WABC教练手册全集目录 https://about.fiba.basketball/en/wabc-documents （Level1–3与Coaches Manual）。
- NBA官方2014 Spurs X's and O's https://www.nba.com/mavs/2014-playoff-primer-breaking-down-the-mavs-vs-spurs-xs-and-os
- NBA官方2022 Heat/Celtics防守对抗 https://www.nba.com/heat/heat-celtics-butler-tatum-conference-finals-preview
- NBA官方2014年马刺赛季历史 https://www.nba.com/news/history-season-review-2013-14
游戏官方：
- 2K22官方2021 Gameplay更新 https://newsroom.2k.com/news/nbar-2k22-unveils-new-gameplay-innovations
游戏社区（经验、非原生代码证明）：
- Operation Sports 2021 2K22 Useful Findings https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings
- 同主题Page4 https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page4

## 7. GPT Deep Research可直接复制提示词（R1）

你是NBA2K22 GM Engine的BPTI篮球认知研究员，**只负责真实篮球体系与战术逻辑R1**，不要编写游戏代码、原生raw参数、30队组织年表或未验证的2K映射。先读公开仓库 https://github.com/chris2gao/nba2k22-gm-engine 的 `docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md` 和 `docs/development_tasks/DEV_20261020_21_BPTI_THREE_RESEARCH_STREAMS_BEFORE_CODEX_V1.md`，并参考M2既有12卡。优先英文FIBA/WABC教练手册、NBA官方战术/教练资料以及具名教练采访。调查10个非互斥篮球体系家族（Motion/Read React、Triangle/Inside-Out、Spread PnR、Iso/Midrange Creator、Post/High-Low、Point-Center/Elbow、Transition/Early Offense、Defense-First/Rim Protect、Switchable Defense、Adaptive Multiple）；进攻和防守可正交组合。每套研究真实篮球的空间/优势创造、球员角色/天赋、阅读防守、二次进攻、被克制原因、对手反制与反制、球员自主创造权的合理边界、人才与财政机会成本、比赛可观察信号，并找至少一个年代/赛季明确的真实球队案例与适用边界。请认真研究2014马刺、2015–2022勇士、乔丹公牛、科比/奥尼尔湖人、约基奇掘金、2021–22公牛等不同哲学，不要把每队浓缩为效率排序，更不要统一成三分魔球。保留来源URL、出版年和具体事实对应，区分教练一手观点、历史事实与研究推断；不确定的明确UNKNOWN。输出中文深度研究报告、10张可结构化的SystemCards、来源索引和争议点列表，在对话中给出完整可交接内容，未经授权不要声称已写GitHub。**研究的成功标准是能让AI解释“为什么这套篮球能创造优势，又如何在被反制时改变”，不是列一堆战术名词。**

## 8. Gemini Deep Research可直接复制提示词（R2）

你是NBA2K22 GM Engine BPTI项目的**30队组织历史/球队文化与教练哲学研究员R2**，专注真实NBA 1984–2021历史到2021–22开局，不负责2K22内存字段和编码。先读公开仓库 https://github.com/chris2gao/nba2k22-gm-engine 的 `docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md`、`docs/development_tasks/DEV_20261020_21_BPTI_THREE_RESEARCH_STREAMS_BEFORE_CODEX_V1.md` 和 `docs/development_research/DEV10_M2_BASKETBALL_AND_FRANCHISE_RESEARCH_V1.md`。输出30支2021–22球队的独立历史参考档案：分清长期组织文化、2021–22主教练理念、过去的代表性战术体系与2021赛季现状；用历史真实事件、球队/教练/NBA官方来源说明，缺资料保留UNKNOWN，不从当年球员数据倒推“文化”。每队给出组织建队风格、教练执教哲学及具体战术实例、对球星个人创造力与团队体系的关系、主/副攻防体系候选及角色要求（这些是设计推断，不是原生执行参数）、重大历史转型案例和未来改变策略的合理条件。加入跨时代经典案例研究：1990年代公牛、2000年代奥尼尔/科比湖人、邓肯时代马刺、2014马刺、勇士Motion、2010年代魔球及其反制、2021–22公牛/热火等；不将2022年后发生的真实交易、人事或冠军倒灌2021开局。尤其考察“球队文化保留，但教练和巨星改变打法”的机制，避免30个固定战术模板，也避免30队用同一种最优化公式。输出中文详细报告、30队结构化参考表、球队哲学演化案例、逐条英文原始来源索引和冲突/证据缺口，完整留在聊天供玩家转交，未经授权不要声称已提交GitHub。

## 9. 本窗口Web GPT R3工作定义

由当前Web GPT直接基于GitHub main最新可读工程做NBA2K22 PC Current Gen的“研究到可执行性”映射及证据审阅，不启动Codex/Antigravity。优先核查社区冲突、现实战术需哪些原生字段、未知CRC不构成已知战术、教练换帅/本队书绑定、人类批准、不同来源标签与历史赛季一致性；输出R3及未来R4合稿。此项需要玩家在BPTI研究阶段继续触发本窗口完成细分研究任务，不承诺后台或异步推进。

## 10. 研究与开发分离

三路Research只产出内容和证据，不运行新增测试；Codex在研究成果整合审阅后再接受已授权分阶段实现任务。BPTI后续代码、Issue #6、季后赛采集、双引擎校准均由玩家逐阶段触发；正式新档与GM V4上线须玩家单独批准。
