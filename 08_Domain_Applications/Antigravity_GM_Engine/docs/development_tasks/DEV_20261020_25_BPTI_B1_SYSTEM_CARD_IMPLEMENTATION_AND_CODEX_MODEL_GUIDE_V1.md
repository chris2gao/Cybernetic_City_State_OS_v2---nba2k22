# DEV25 — BPTI B1：10种篮球体系卡实施任务 + B系列Codex模型建议 V1

日期：2026-10-20 | 开发规划Web GPT | 当前状态：**B0 PR #8静态审核通过、仍待玩家合并；B1 TASK_READY / NOT_EXECUTED**。本任务书不直接批准合并、游戏内存写入、DEV23、DEV24或后续B2–B6。玩家将相应阶段提示词交给Codex才视为该阶段获授权。

## 0. 当前B0状态与分支规则

B0：[PR #8](https://github.com/chris2gao/nba2k22-gm-engine/pull/8)，head `538eef31615a22c4163017a58152c9bb26202d21`，Draft/未合并（本任务编写时）。本开发规划窗口已对PR作GitHub review COMMENT（静态审核PASS，推荐玩家合并）；本窗口**未独立重跑开发者报告的3个已通过测试**。

B0已给出四种TypedDict/运行时校验、十家族SYSTEM_IDS、优势链、AGENCY、ResearchIndex、M2 Knowledge.bpti()以及91 Source/40个**复合**Claim。**普通GM默认视图屏蔽UNKNOWN/来源缺失/未来知识**；不能误以为40 Claim可立即全部供GM阅读。B1不能重做B0 schema或绕过B0时间裁剪。

**B1开工条件**：玩家先批准合并PR #8，Codex确认最新main已包含B0且工作树干净后，从**新main**独立建立`codex/bpti-b1-system-cards`并提交独立Draft PR；不要把B1代码直接追加到旧B0分支。若玩家有意在B0合并前启动stacked PR，必须单独说明并获得用户许可。

## 1. 推荐Codex模型与思考等级（按工作复杂度而非一律最贵）

下表指**实际Codex模型选择器可见时**的推荐；模型访问取决于账号/工作区。官方模型文档目前推荐`GPT-6.1 Sol`兼顾智能与成本，`GPT-6 Astra`用于最复杂推理/代码，Codex模型选择器可能按工作区显示不同选项。无相应模型选可选实际可用最强Sol，保持同一思考等级，不为型号更改阻断交付。

| 阶段 | 首选Codex模型 | 推荐思考等级 | 理由 |
|---|---|---|---|
| **B1** 10卡与知识检索 | **GPT-6.1 Sol** | **High** | 依据大量篮球文本合成精确数据卡、重用B0结构与GM安全投影；不需Astra默认 |
| **DEV23** 核心CRC/本队角色专项 | **GPT-6 Astra** | **High** | 原生内存与菜单证据/多对象角色映射更复杂；无法拿到就Sol High |
| **B2** 战术意图→原生NativeBinding | **GPT-6 Astra** | **High** | 源批身份、B0/B1兼容、M3/DEV14边界和UNKNOWN/部分支持条件交错 |
| **B3** 30队历史TeamIdentity | **GPT-6.1 Sol** | **High** | 30个受证据/年份约束的数据卡与最小查询/检索 |
| **B4** 篮球推理接M3 D1–D6 | **GPT-6 Astra** | **High** | 业务与工程交叉最多，既要有篮球因果，又要忠于HOLD/INTERNAL/MARKET和授权规则 |
| **B5** 跨赛季演化 | **GPT-6.1 Sol** | **High** | 历史状态版本与六级演化，适合有界独立工程阶段 |
| **B6** 已授权的最小综合验收 | **GPT-6.1 Sol** | **High** | 综合验证与问题定位；仅发现真实复杂交叉缺陷时另询问是否升Astra |

不默认使用Extra High/xhigh/max：这些等级在官方文档中适用于少数确有明显收益的特别复杂长流程；当前阶段范围较小，应先用High并遵守最小测试范围，**不能借高思考等级自动增加测试或设计**。

## 2. B1唯一开发目标

使用B0已有接口和R1完整Deep Research，正式建立**10张精简、可靠、有真实篮球因果链且可按需检索的SystemCard**。每张不是一堆战术术语，而是能回答：
- **ENTRY**：当前阵容/教练/对手条件为什么可能选择这个体系？
- **FIRST**：谁、以什么掩护/接应/空间动作创造第一防守困难？
- **RESPONSE/READ**：对手以什么方式回应？球员如何读防守？
- **SECOND**：第一次未成时如何再创造优势？什么反制会令此体系不理想？
- **FALLBACK**：何时由明星自主处理、或重新组织，而不是每次静态调用同一战术？
- **ROLES/COST**：需要哪些技能角色、替补/薪资机会成本是什么？哪些信息可被本局比赛数据观察，哪些机制难以从Box Score证明？

对象：既有`SYSTEM_IDS`的全部10个，覆盖七种进攻家族+三种防守家族；**攻防正交、组合而不是互斥30套模板**。保持Jordan/Bulls、Kerr/GSW、SAS等具体真实历史只作有出处的案例，不复制现实的冠军结果和未来能力到GM世界线。

## 3. B1具体可改范围

1. 在原`web_gm/knowledge/bpti/`下新增一个小型`system_cards_v1.json`（或符合M2目录组织的等价文件），一张一个`SystemCard`，使用B0原有TypedDict字段，不新增第二套事实库/查询引擎。
2. 每卡须填写全部`advantage_chain`七段、`role_requirements`、`player_agency`、`defensive_counter_options`、`second_answers`、`known_failure_conditions`、`roster_budget_tradeoffs`、`observable_signals`和`evidence_claim_ids`；无Playbook已证据支持前，`native_binding_refs`允许为空，不能编造CRC或绝对执行效果。可借既有文本列表描述“双方反制”，不为B1开发ACE自动反制流程。
3. 复用`Knowledge.bpti()`及研究`ResearchIndex`，添加按家族ID读取单张卡、按角色/关键反制查有限张卡的最小API与原`gm_knowledge.py`子命令（建议`bpti-system`、`bpti-systems`，若项目已有等价CLI命名可遵循现有约定）；默认有界、不得每次GM查询读取R1 607行全文。
4. 知识引用最小化：保留R1已有`R1-C-* / R1-S*`和原文定位，并在必要时仅对**明确属于2021开档前的具体战术史事实**拆分细粒度Claim（含适用时间/当时可知时间）；**不能把B0的UNKNOWN复合Claim批量升级VERIFIED**。R1研究真确度与原生游戏支持度分开，资料不足就`REFERENCE_ONLY / UNKNOWN`，不使用ChatGPT临时引用作为唯一来源。
5. **GM可读性要如实报告**：所有10张在显式RESEARCH范围可查询；普通GM只可看到按B0时间/来源过滤后合法的内容，未认证Claim或未来NBA结果不得通过SystemCard文字/查询回填泄露。可以将无法安全供GM读取的卡或段落保留`RESEARCH_ONLY/NOT_READY`（作为外围查询视图，不改变B0 TypedDict枚举），不得声称`GM_10_OF_10_READY`除非实际满足。GM要用的最小安全篮球原则应优先从R1可追溯且对2021无未来泄露的机制中提取；不能仅因数据全部UNKNOWN而绕过B0校验。
6. 区分篮球观察：`OUTCOME/MECHANISM/CONTEXT`；如果现有B0的`observable_signals:list[str]`不足以明确类型，可使用稳定的短串编码/独立查询解释，而不是无授权改变B0契约或创造新的统计引擎。
7. 修改必要的M2知识手册、BPTI使用手册与状态索引。**本次绝不**加入R2 30队正式TeamIdentity（B3）、原生战术绑定（B2/DEV23）、SystemBlueprint生成或M3 D1–D6策略自动注入（B4）。

## 4. B1明确授权的三项最小验证（不扩大）

- **B1-T1 十张卡与因果内容**：10/10 `SYSTEM_IDS`唯一，调用B0校验通过，七段`advantage_chain`完整、角色/自主权/失效条件/第二答案/机会成本/可观察信号非空。
- **B1-T2 有界检索与可追溯出处**：按一个family ID检索能回显相应卡，按一个角色/反制条件查询能返回有限条目，核心Claim→Source→原文行定位存在；不能默认dump十卡原文/研究全文。
- **B1-T3 历史截止与非执行边界**：利用最小合成记录核验普通GM不会看到未来赛果/UNKNOWN复合内容、源缺失不能自动升VERIFIED；卡片没有原生地址/游戏改写命令/获批状态；B1不得借SYSTEM名字假称NativeBinding受益人或执行效果已认证。

这3项可作为`scripts/check_bpti_b1.py`（可复用B0测试辅助，但不重新执行B0三项或M3/DEV14大型集合）。有问题只修直接失败项并定向复验；任何额外设计/测试必须遵守`PLAYER_DEVELOPMENT_POLICY_V2`征得玩家批准。

## 5. B1交付与停止

- 从合并后的最新main独立B1分支、独立Draft PR；不自动合并。
- 可运行的十家族知识文件、受控查询/验证、来源状态、简短使用手册、`docs/development_reviews/BPTI_B1_IMPLEMENTATION_AND_ACCEPTANCE.md`；更新AGENTS、33/34的必要状态。
- 验收报告**分别**声明`SYSTEM_CARD_10_OF_10_CREATED`、`RESEARCH_QUERY_COVERAGE`、`GM_ELIGIBLE_COVERAGE`，不要混用，也不承诺3D/Calendar现实比赛效果。
- 停止在`BPTI_B1_ENGINEERING_COMPLETE_AWAITING_PLAYER`；不自行实施DEV23，后者必须B1通过/玩家批准后另触发。
- 本阶段不修改游戏、球员能力/潜力/徽章、不访问实时内存、不运行新采集/发布、不启用GM V4或新档。

## 6. 可以直接发送给Codex的执行提示词

仓库：`chris2gao/nba2k22-gm-engine`。请先阅读最新main的`AGENTS.md`、`docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md`，以及本文件`docs/development_tasks/DEV_20261020_25_BPTI_B1_SYSTEM_CARD_IMPLEMENTATION_AND_CODEX_MODEL_GUIDE_V1.md`。随后阅读DEV22、R1原始完整报告、R1审核、R4整合、B0工程合同和B0源索引。**前置门**：PR #8由玩家批准合并进main后，再由最新main建立独立`codex/bpti-b1-system-cards`分支，不在未合并B0上直接工作。

本次只实施B1：沿用B0 `SystemCard` TypedDict、`SYSTEM_IDS`、`CHAIN`、`AGENCY`、`ResearchIndex`与`Knowledge.bpti()`，把R1十个非互斥篮球体系编成可用的十张高质量、短而精的知识卡；每张有完整优势→防守回应→球员阅读→第二答案→反制→重置链、角色、创造权、失效/机会成本及来源；不用统一数据效率最优化代替篮球因果。扩展M2已有按需CLI来按系统/角色有界查询，保留来源永久索引和2021截止、不自提UNKNOWN为VERIFIED；全部卡可在RESEARCH检索，GM仅得到有合法时间/证据的部分，报告GM可读覆盖率，不能冒充10/10已投入运营。只做本任务明确的B1-T1～T3最小验证，一次通过即停，不运行B0/M3/DEV14旧测试集合；遵守政策V2，不擅自扩展设计与测试。

交付B1代码、必要文档、验收报告和独立Draft PR，不合并，不启动DEV23/B2–B6/DEV24，不做游戏写入、采集、正式经营。完成后明确`BPTI_B1_ENGINEERING_COMPLETE_AWAITING_PLAYER`。
