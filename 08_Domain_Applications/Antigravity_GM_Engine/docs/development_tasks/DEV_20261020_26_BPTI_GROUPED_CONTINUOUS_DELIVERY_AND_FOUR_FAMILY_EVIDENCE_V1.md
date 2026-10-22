# DEV26 — BPTI B2–B6 分组连续开发与四体系补证执行计划 V1

日期：2026-10-20 | 编制：Web 开发规划 | 状态：**SCHEDULING_DECISION_CONFIRMED / EACH_PACKAGE_REQUIRES_NEW_USER_TRIGGER**。本文件仅改变推荐调度，不自动合并PR、授权游戏内存读写、正式运营GM V4或启动Codex。玩家转发相应工作包提示词后，该工作包的具体范围和明确最小检查视为授权；授权后工作包内不需要每个B阶段再逐一征求批准。仍遵守`PLAYER_DEVELOPMENT_POLICY_V2`：工作包以外扩展设计/追加检查必须先询问玩家。

> **强制执行规则（玩家最新决定，覆盖本文件及DEV22/DEV23所有旧“检查点、等待玩家回复、继续执行”表述）**：每次Codex只接**一个明确定义的完整任务包**，包内已批准步骤可以依顺序连续执行，但**不得停在任何交互检查点、待反馈的暂停会话、常驻工具调用或后台等待**。一旦真正需要玩家回复、额外授权、游戏说明或超出授权范围的设计/测试，Codex必须完成当前能够完成的内容→保存/提交已有成果→在终结性答复中列出不超过必要的问题与未完成工作→**彻底结束当前任务**。玩家反馈后，玩家会**新建下一条Codex任务**继续，不复用处于等待态的旧调用；即使全部批准的步骤做完也必须结束任务。对只影响局部精度的UNKNOWN/CRC不可解/文献缺口则保留UNKNOWN并完成其它已授权可做事项，不为了不必要的完备性停下来问玩家。禁止任何“请回复继续/我在此等待/你批准后我自动推进”的活跃任务机制。**用户要求的是TASK CLOSED，不是TASK PAUSED。**

> **2026-10-20 玩家最新顺序（覆盖本文旧DEV23待执行描述）：** PR #10已MERGED（merge `8c80c7d`），DEV23本次研究及共享战术池交付完成；玩家明确批准**先执行独立[DEV27本队Playbook后缀匹配最小修复](DEV_20261020_27_BPTI_TEAM_BOOK_SUFFIX_MATCH_MINIMAL_FIX_V1.md)，由Codex交付Draft PR并真正结束；玩家另行批准其合并后，再启动本文件工作包B**。DEV23剩余逐CRC类型UNKNOWN不必阻断包B其它已知能力。本次修复不纳入包B使其混成一个会话。玩家将来希望全面调查可控项与补齐动态比赛数据，那是B6后独立扩展，不增加本文件B/C的测试和任务范围。任一阶段需要人工参与时必须终结任务，绝不暂停等待。

## 0. 当前GitHub事实与此前方案冲突的解决

- B0 PR #8 已合并main（`e4b397e`）；B1 [PR #9](https://github.com/chris2gao/nba2k22-gm-engine/pull/9) **现已MERGED**（已直接查询GitHub状态，head `65efdafb43636812eebeb8e88e6e1660763d7f97`）；完成10/10 SystemCard、10/10研究可读、截至2021-10-19普通GM可读6/10。**DEV23尚未因PR9合并而自动获得启动授权**。
- [DEV23](DEV_20261020_23_BPTI_CORE_PLAYBOOK_SEMANTICS_CODEX_DISCOVERY_V1.md) 待玩家**独立触发**，先做仓库原生目录/已授权只读内存调查，**不要求截图、Computer Use或玩家预先打开指定页面**。仅在现有静态/只读来源不能支持关键判读时请玩家另一次任务提供**文字说明**。若需要说明，当前DEV23应提交部分成果与问题清单、完全结束。
- [DEV22](DEV_20261020_22_BPTI_RESEARCH_TO_CODEX_PHASED_HANDOFF_V1.md) 的B2/B3/B4/B5/B6**独立阶段中途停工要求改为分组完成**：只有包A→包B、包B→包C这些**已经结束的独立任务之间**才由玩家按新消息重新触发。DEV22知识/授权/代码质量边界不变。工作包内里程碑不是交互检查点，也不等待确认。
- [DEV24](DEV_20261020_24_BPTI_ANTIGRAVITY_GAME_DATA_SOURCE_REQUIREMENTS_V1.md) Antigravity逐场/高级统计扩展由玩家决定**在B0–B6全部完成后进行**。这不取消正式开档另需可靠真实采集的独立条件；B4/B6不可伪造逐场赛果或真实30队已评估。

## 1. 三个独立且终结的执行包（包内连续，不保留检查点）

| 包 | 内容 | 单次任务如何真正结束 |
|---|---|---|
| **A / DEV23** | 仓库静态 + 可行的只读原生内存Playbook/角色调查；用户只可补充**文字菜单描述** | 全部证据可得则提交研究报告/文件并**结束任务**；必需玩家答疑则提交已有成果+短问题清单、**结束任务**，不在原任务等待 |
| **B / KNOWLEDGE** | **B2 → B3 → 四家族2021前证据补充** | 单次授权后内部连续开发、可做局部Git提交；全部完成才提交完整Draft PR并**结束任务**；若遇真正人工阻断，保存当前成果、报告未完成并**结束任务** |
| **C / GM INTEGRATION** | **B4 → B5 → B6** | 单次授权后内部连续开发，限范围最小验收后提交Draft PR并**结束任务**；真正人工阻断则提交已有进度并**结束任务**；不启用V4/新档 |

理由：B2/B3/四补证同属**知识与事实解释层**，B4/B5/B6同属**决策与验收层**；每包一条完整Codex任务，一次完成，结束后自然交付/合并决定，**不是运行过程中设置一个会等待用户回复的“检查点”**。两个大包比一次B2–B6超大PR更利于控制上下文，也比B2/B3/B4逐项暂停更节省额度。

**PR策略**：每包独立分支/一个Draft PR，内部小型提交仅用于恢复而非交互检查点。**Codex不自动把任何Draft PR合入main**；A交付并由玩家接受的研究先入main，玩家再以新任务触发B；B完成且PR由玩家决定合并后，以新任务触发C。**PR9当前已合并**。若A的某项原生语义UNKNOWN，不要求无止境调查：明确哪些原生字段仍可支持B2，标UNKNOWN/HOLD，其余交玩家另行决定。

## 2. 包A：DEV23独立一次性任务（不等待页面/截图）

读取DEV23静态目录/68槽/PlayTypes/角色/本队同名书；在**已授权、可行的只读内存条件**下分析原生对象，不要求用户提供截图、远程控制画面或事先停在编辑菜单。优先聚焦Warriors Motion、Bulls Iso/Mid、Heat Hub与少量PnR/Post/Elbow，区分`UI_OR_STATIC_LABEL_VERIFIED`、`RUNTIME_ASSIGNEE_OBSERVED`、`IN_GAME_EXECUTION_OBSERVED`，其中第三层比赛执行**不获授权**。若必须由玩家文字描述菜单行为才能继续，**研究者完成已可做工作并结束当前任务**，将明确问题留在最终报告；文字描述不可冒充内存认证。具体步骤和终止状态见DEV23。即使部分UNKNOWN仍可供B2开展降级映射，不强制穷尽CRC。

## 3. 包B：B2、B3和四家族补证连续执行

### B2 NativeBinding：R3+DEV23→B0 DTO

复用M3/DEV14：八Coach系统、19默认字段的可写边界（常规18）、Freelance1–4、本队已加载68槽/同批真实CRC、4 PlayTypes+Initiator、具名48 Tendencies、18 PERSONAL_DEFENSE、训练及软轮换；系统家族与原生Enum绝不强制一对一。仅生成只读`NativeBinding`及简短匹配报告、`SUPPORTED_FIELD_DIRECTION/TYPE_MATCHED_ONLY/UNKNOWN_NATIVE_BEHAVIOR/UNSUPPORTED_ACTION`；行为效果未知保持HYPOTHESIS。实时内存/游戏/DEV14执行器禁止引入gm_core。51未知倾向、Tempo解释、受益球员若未获DEV23证据必须HOLD。

### B3 TeamIdentity：R2 30/30历史seed与本局对象分离

按2021-10-19真实历史可知界限，区分组织文化、教练本人哲学、当期战术和人员优势。产出30/30 TeamIdentity可检索历史`HISTORICAL_SEED_ONLY`，保留未证据支持的UNKNOWN、LAL-S2/POR-S2缺URL/ATL-S2部分支持的现有B0条件；不凭当期名单或城市名字捏造文化。留已有M3同批Team/Coach/Roster绑定钩子，但在未收到新档合法源前`NOT_BOUND_TO_ANY_SAVE`、真实30队仍UNASSESSED。

### B1-EVIDENCE-4：在B4之前给四个RESEARCH_ONLY家族做**最小、真实、在2021前已知的知识补充**

正式GM目前10家族中6张可读；四张`ISOLATION_MIDRANGE_CREATION`、`POST_HIGH_LOW`、`TRANSITION_EARLY_OFFENSE`、`DEFENSE_FIRST_RIM_PROTECTION`暂`NOT_READY`。四者是正常篮球常见打法，B4若只能在六家族中选择会形成结构性偏置。

Codex限范围完成：
1. 将下面**已初步查实**的2021前NBA官方历史报道作为**候选来源**，对照原文与2021日期确定适用的机制句子、来源标题/发表时间、具体事件时间、证据界限和反证；无需重新启动长篇Deep Research或修改R1原始报告。
2. 每体系只补一条**保守的篮球原理细粒度Claim**（如需第二来源才能支持具体重要主张，可保留较窄范围、不扩大调查），遵守B0的`SUPPORTED_INTERPRETATION`与`source_id/parent_claim_id/fact_valid_from/fact_valid_to/knowledge_available_from`，有确切原始URL、时间和事实才入库；不要把NBA官方单队案例当作全联盟战术有效性定律。
3. 按既有B0/B1校验将卡片关联改为截止日前可阅读的机制Claim；保留牌面七段篮球意图，但不能让未证实/未来句子顺着单一许可引用泄漏到普通GM。
4. **目标是10/10普通GM具备至少一个2021前定性机制入口，非必须逐命题VERIFIED或游戏行为验证。** 若真实来源不能支持完整卡片叙述，只将可支撑的子命题做安全可读参考，其它仍NOT_READY/UNKNOWN；**不可人为改变日期、绕过索引或直接解除HOLD以凑10/10**。研发如未完成，明确`GM_ELIGIBLE_COVERAGE`的真实值与B4可用子集，继续在安全子集内实施，不阻断整项BPTI计划。

**初步核实的四条2021-10-19前来源（均为NBA官方，核实仅供候选，不算项目Claim认证）：**

| 家族 | 官方文章 | 发表时间 | 可支持的最小机制 |
|---|---|---|---|
| 单打/中距离 | `https://www.nba.com/news/film-study-kawhi-crowd` | 2019-06-04 | Leonard面对提前包夹/高压时，创作者要及早读协防，个人创造与二次传球互补 |
| 低位/高低位 | `https://www.nba.com/news/sixers-crown-jewel-shines-game-4` | 2019季后赛 | Embiid低位遭绕前，用罚球线高位接应建立高低位入口；包夹后及时找外线/切入 |
| 转换/早期 | `https://www.nba.com/news/film-study-lakers-transition-lebron-james-anthony-davis` | 2020-05-13 | 2019–20 Lakers篮板/提前传球制造早期优势，防守落位前的决策时间决定机会 |
| 护框优先 | `https://www.nba.com/news/film-study-sixers-joel-embiid-rim-protections` | 2020-07-08 | 护框分威慑出手与干扰出手，Drop会影响挡拆持球者的射程和选择 |

**单一文章有可能支持一个狭窄原理而非一张完整七段卡的所有句子；发布前逐条核对，杜绝全卡借一条来源“认证”。** 不把以后赛季DeRozan/Gobert的数据回填2021认知。

### 包B最小检查（若用户转发任务词则仅授权以下4项）

- B-B1：核心Binding中，已确认原生字段与尚未知CRC/受益人严格分级；个人18项防守、本队书、OVERALL只读、51未知不写；不能生成任何真实Desired/批准。
- B-B2：30张历史TeamIdentity唯一、来源可回查、2021截止/UNKNOWN和未绑定存档身份正确。
- B-B3：四类补充Claim候选逐条对照2021前年份与官方文章；GM可见/阻断覆盖结果如实记录，不能漏出未来赛果；不得为了达10/10绕过校验。
- B-B4：B2+B3共同查询是有界只读、返回状态和证据，研究包不会改变M3/DEV14执行权限或初始化正式30队运营状态。

不跑旧B0/B1/M3/DEV14全量测试；授权检查未通过只修直接失败项并定向复验。任何额外扩展或验证征询玩家。

## 4. 包C：B4、B5、B6连续执行

### B4：实际连接M3决策

在现有D1–D6、M1交易/资金、M3教练/类型/个人防守、DEV14审批环节**引用而不是重做**B1/B2/B3知识；输出`why_this_basketball`、`primary_secondary_system`、`first_advantage`、`opponent_counter`、`second_answer`、`roles_agency`、`native_support_and_unknowns`和三个经营备选HOLD/INTERNAL/MARKET。球队哲学必须影响解释与内部调整/人才缺口比较，不仅生成一个装饰性的历史段落；普通GM只能消费可用历史Claim和**同批经过脱敏的实际球员教练资料**，其余Research-only家庭不得漏进运营上下文。没有逐场Box Score时不虚构趋势/胜率效果；当前轮换分钟AI可覆盖，不强控精确分钟。

### B5：真实本局跨赛季演化状态

记录先前体系与文化、已观察变化和决定、六级转型建议`ROLE_TWEAK / SECONDARY_BRANCH / CO_PRIMARY_SYSTEM / TACTICAL_REBASE / COACH_ALIGNMENT_CHANGE / ORGANIZATIONAL_REIDENTIFICATION`；建队身份慢变量与教练/战术快变量分离；历史新秀名号不得决定未来职业能力，实际技能只由本局合法动态来源触发。存现有gm_workbench衍生历史/版本或等价已有点位，**不新增第二个GM经营数据库或教练签约市场**；所有建议仍须玩家审核，不自动换帅/交易或写内存。

### B6：最小集成验收与工程报告

验收**设计和离线安全推理**，不假称真实新档30队已经营、3D/Calendar效果验证、赛季统计校准完成或GM V4已启用。建议以现有合成安全DTO为输入，不跑实际比赛/采集。

### 包C最小检查（若用户转发任务词则仅授权以下5项）

- C-C1：GSW Motion、CHI Creator/Midrange、MIA Defense-first三个实例给出**篮球原因与不同角色结构**，允许来源/Native不支持时HOLD，不能把三个队变同一种效率优化。
- C-C2：B4真实走M3的HOLD/INTERNAL/MARKET比较及角色/教练/市场机会成本，不创建重复审批器/市场。
- C-C3：历史巨星**异队**及教练变化的合成案例仅基于当期可见技能/组织惯性触发六级演化中的合理步骤，不能因姓名自动获得职业巅峰能力，也不随月度成绩瞬间重写球队文化。
- C-C4：数据源不可用/GM_SANITIZED身份不符、UNKNOWN Native或B1不可用卡正确HOLD；对真实比赛效果和缺失逐场数据不杜撰。
- C-C5：对接DEV14仍仅输出**未获批准意图**，不会自动修改Ability/Potential/Badge/OVERALL、51未知倾向、其它队书，或绕开CAS/玩家审批。GM_V4_NOT_ENABLED，30队实际经营仍UNASSESSED。

只运行本包这些直接相关检查，失败定向修正；不重跑旧完整集合，也不自行添加未知风险防御套件。

## 5. 无交互等待：任务完成与真正阻断的统一终止协议

**最高优先级：用户要求“任务到此真正结束，不是暂停”。**

1. 玩家每次**只启动一个任务包**A、B或C；Codex在该包授权范围内完整执行，不用B2/B3/B4中途再问一次。每个内部阶段可以提交Git以避免进度丢失，但**绝不能在这些点启动审批式等待、会话暂停或后台轮询**。
2. **正常完成**：做完该包的明确范围和指定最小检查，发布必要文档/代码及一个Draft PR（若需要），最终回复完成态，然后**终止本轮Codex任务**。不自动合并、不后台继续、不自动进入下包。状态中的`AWAITING_PLAYER`仅表示“任务已结束、玩家可在未来审阅”；不是等待态的任务实例。
3. **遇到必须人工介入**：允许完成此前已获授权、不依赖该问题的工作，随后保存局部提交与资料、形成可独立审阅的部分交付/若合适则Draft PR，最终回答`PACKAGE_A/B/C_PARTIAL_TASK_CLOSED`或`BLOCKED_TASK_CLOSED`，列出需要玩家答复的**精确问题**、已完成步骤、尚未完成步骤、可复用分支/提交，**完全终止任务**。用户后来提供文字、批准设计或其他条件后，需发起新的Codex任务；不得“在这里暂停等我回复”。对实质阻断无法完成的内容不可标完成。
4. **范围外需求/测试**：不在活跃会话中弹确认窗等用户，严格按照政策V2直接停止受影响工作，将扩展范围、必要性及工作量写入最终报告并结束；用户决定后新开任务。**不允许工具调用停住等待人输入**。
5. **UNKNOWN非人工阻断**：不能解码某CRC、找不到真实受益人、文献支持不足，不自动构成必须打断整个包的人工门；使用已验证字段、保留UNKNOWN/HOLD/不达标的覆盖率，继续完成包内仍能合法完成的能力。**禁止为了达到10/10或所有CRC而无限加测/逆向**。
6. **失败与恢复**：遵守一次失败三次修复预算和既定最小测试；真实超时或成本障碍时尽量保留已完成提交，下一次由玩家触发从已完成提交恢复，**不承诺任务实例在后台保留或恢复运行**。
7. 模型建议：A（DEV23）Astra High；B（B2→B3→四补证）Astra High；C（B4→B5→B6）Astra High，无法选择则当前可用最强Sol High。高思考等级不授予任何额外测试/开发范围。
8. 不得游戏写入、直接改Ability/Potential/Badge、自动修Issue #6、启用GM V4/新档、做DEV24采集或3D/Calendar校准、自动合并PR。

## 6. 可直接发送Codex的两个连续包授权入口

**包B（DEV23任务已实际结束且研究归档/经玩家接受后）**：

> 启动**一个完整且必定终结的Codex任务**：BPTI工作包B，按**B2→B3→四体系补证**连续开发。先读最新main、DEV26第3/5节、DEV22、R4、B0/B1合同及DEV23研究。仅授权包B的定义范围与**B-B1～B-B4四项最小检查**，一个独立分支，阶段内部连续实现和局部提交，不设置人工检查点或挂起等待，不做B4–B6/DEV24/游戏写入。完成发布一个Draft PR与验收报告，终结当前任务，返回`BPTI_PACKAGE_B_COMPLETE_TASK_CLOSED`；若发生确需玩家介入的阻断，保存已有成果、最终列出问题，返回`BPTI_PACKAGE_B_PARTIAL_TASK_CLOSED`并**完全终结任务**。未知CRC/战术受益人保持UNKNOWN并尽量不阻断其它可实现功能。玩家答复后必须新启动任务，不允许原任务等待回复。

**包C（包B已结束且玩家批准合并其PR后）**：

> 启动**一个完整且必定终结的Codex任务**：BPTI工作包C，按**B4→B5→B6**连续开发。先读最新main、DEV26第4/5节及DEV22、R4、B0/B1/B2/B3/DEV23验收、M3/DEV14。仅授权包C定义范围与**C-C1～C-C5五项最小检查**，从最新main独立分支，包内连续实现、局部提交，不设置人工检查点，不做真实游戏写入/正式GM V4/新档/DEV24/额外测试。完成提交一个Draft PR与整体验收，返回`BPTI_PACKAGE_C_COMPLETE_TASK_CLOSED`并**完全终结任务**；需人工介入时提交当前成果+具体问题后返回`BPTI_PACKAGE_C_PARTIAL_TASK_CLOSED`并结束。玩家答复必须通过新的Codex任务处理，任何情况下不暂停会话等待输入。
