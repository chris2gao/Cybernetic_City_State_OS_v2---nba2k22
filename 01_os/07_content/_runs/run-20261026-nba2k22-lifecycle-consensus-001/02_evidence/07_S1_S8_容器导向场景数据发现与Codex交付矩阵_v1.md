# NBA2K22 阶段02：S1–S8 容器导向的数据发现与 Codex 场景交付矩阵 v1

**状态**：`DESIGN_CANDIDATE_STATIC_SCENE_BRIEF_NOT_DISPATCHED`，2026-10-27。正式 A0-v1 与 A-v1-RC01 不变，原始第一大任务A v1.9及V0.4原型规划/ADR持续有效。**这是用于后续场景任务的范围与证据准备，不是实机已证清单，不是Human新增场景必做字段的批准，不是任何游戏/Native/工程执行许可。**

## 0. 一句话产品目标和核心不变量

**容器（统一数据库）用来如实装载游戏已经存在的食材（游戏实际文字、数值与关系）。S1–S8 不是八套系统，而是为了在不同游戏阶段最大限度发现所有食材的形态、来源和关联，再验证同一套长期可复用容器确实能装下。**

- 不要求“场景各一库／各一套表”。每独立save一份SQLite事实库，一套稳定Schema复用约100个赛季；实际字段/来源证据不足只标UNKNOWN，之后依版本化Schema扩充。
- PC22离线MyLEAGUE中的基础/高阶/累计/场均统计、排名、冠军和奖项优先读取**游戏实际已计算数值**，不做外部重新加总、排名/奖项重新计算、额外指标或职业模拟分析。
- 历史实际观察按unit保留，已确定事实不覆写；Native观察、外部提出目标值、经Human授权的执行回执与全新采集验证互相区分；角色权限保护隐藏Potential。
- v25固定工程 `a3927fb150a213201e404cca043ced4f57409bd1` 已有101 STRICT表/1789列/20注册Reader，**仅证明物理/注册存在及先前开发归档**，不能冒充每一场景原生来源完整验收。
- 实际S1–S8场景由Human提供并控制推进，不是正式采集频次P1–P12；场景期间编码/实机取证在另行获授权后交Codex单一Owner，Gemini只做有界性价比高的专项Native研究，未授权不执行。

## 1. “食材”最小分类——先盘全，再验证能装

每个游戏UI域/Native来源按这些类别登记，分类只是**目录，不是数据表**：

1. **人物与身份**：现役、自由、G League、历史/退役、选秀模板/正式新秀、球队、教练/员工及状态，保存确证当前与跨赛季关联，未证身份不凭姓名或ID强合。
2. **比赛与赛季**：赛程、原生单场Box、球队/球员原生当前/最终统计、赛季状态、季后赛轮次与系列赛、全明星等游戏真实存在的对象和文字/数值。
3. **球队操作状态**：人员归属、名单、角色、轮换、战术、训练、球员属性/倾向/徽章、伤病/士气。
4. **市场/合同/选秀**：合同逐年字段、自由市场资格/可签性、员工市场、原生选秀权、抽签、正式候选池、选秀结果与新人归属；可见市场状态≠交易/签约事实。
5. **历史/荣誉/设置**：原生历史、年度奖项、冠军/FMVP、纪录、游戏新闻（有真实源才收）、联盟规则/Slider以及获准的世界线实际设置。
6. **横向结构**：save/season/object键、Native+UI字段字典、类型/单位/合法值域、来源窗口、权限、观测时间、采集完整性、冲突、失败与可追溯查询。

**先找游戏确实有的目标字段及表间关系**。源池暂不可得可先预留类型化/关联容器，但不能自行补造游戏事实、Native偏移或不存在的对象。

## 2. S1–S8 Codex现场“找什么、不做什么”矩阵

此表是**候选寻找清单**，且已注册Reader/已建表不证明对应窗口实际可读。普通行的优先级仅为规划建议；经Human批准的核心/非核心名单需后续有界场景判定，不由本表自动冻结。

| 场景 | 现场优先发现的真实“食材”及边界 | v25候选 Reader→容器（举例；仅静态） | 现场应解决的具体未知 | 明确不做 |
|---|---|---|---|---|
| **S1** 已进行约1个月常规赛 | 完整当前球队/球员、真实属性/徽章/合同/伤病、轮换/战术、赛程、已完成单场Box、当前游戏赛季统计、设置与财务 | `schedule`→`games/player_game_boxes/player_season_totals`；`player-details`/`player-skills`→球员typed族；`organization`/`lineups`→团队/轮换；`settings` | PC22 UI字段是否全部映射、Native身份/得分/观测时点能否查回；game6/game10归档Box不完整的逐侧原因仍未知 | 不因前两个Box完整性false重建整个Reader，不用逐场累计替代Native原生赛季数值 |
| **S2** 全明星前后 | 入选/首发/替补、真实全明星比赛对象和游戏展示的荣誉/统计（存在且此时生成者） | `honors`/`league-history`/`schedule`→`native_player_stat_observations`、`season_award_instances`、`games`等 | 哪些项在赛前/赛后才产生；是否有独立全明星赛事与身份/字段，旧Reader能否装载 | 不预测或投票选人，不把历史荣誉槽视作当前全明星结果 |
| **S3** 交易截止日前 | 实际名单/合同、交易窗口状态、工资与选秀权归属、自由市场当前状态 | `market`/`finance`/`affiliations`/`player-details`→`draft_pick_ownerships`、`team_finance_observations`、`player_contract_observations`、`market_state_observations` | 截止日显示与Native状态/权限、真实选秀资产字段语义、对象稳定键及来源是否齐全 | 不开发交易谈判或交易评级模型，不凭两次名单差异造交易事件 |
| **S4** 常规赛结束且常规赛奖项颁发后 | 游戏实际已给出的最终常规赛球员/球队统计、排名、年度MVP等获奖事实、真实纪录与阶段边界 | `schedule`/`period-stats`/`honors`/`league-history`/`records`→`player_season_totals`、`native_player_stat_observations`、`season_award_instances`、`award_recipients`、`season_finalizations` | Native当前赛季统计的实际口径/期间选择；正式已颁奖对象与历史档案字段如何区别；真实定稿边界 | 不重算场均/积分榜/MVP，不把Native award旗标自动推成已经确认的本年获奖者 |
| **S5** 季后赛开始 | 已生成对阵/种子/轮次/系列赛、季后赛赛程、逐场Box与游戏提供的季后赛统计、是否初现新人池 | `schedule`/`game-mode`→`playoff_series`、`playoff_series_games`、`games`、`player_game_boxes` | 哪个原生字段绑定系列赛与比赛身份、首次出现时机、季后赛统计是否需独立source字段 | 不模拟季后赛、编造未来结果或通过胜负反推未经实证的Native系列赛ID |
| **S6** 季后赛结束但未进入休赛期 | 实际总冠军、FMVP、季后赛结束统计、最终系列赛事实、游戏历史与当前年获奖条目的新出现 | `league-history`/`honors`/`records`/`schedule`→`season_award_instances`、`award_recipients`、`native_league_history_observations`、`playoff_series` | 游戏何时正式产生本年冠军/FMVP、如何和S4已获得奖项一起追加且不覆盖，及其Native归属身份 | 不重新判总冠军/FMVP，不因S4完成过年度荣誉源就忽略S6新生成事实 |
| **S7** 休赛期**多个子窗口** | 员工市场、抽签、正式新秀候选池、选秀结果、新球员/签约、自由球员、训练营及退出临时池（详见第3节） | `staff`/`market`/`affiliations`/`planning`等→人员/选秀/合同/训练现有typed表 | 真正出现/消失时机、原生目录及身份；空模板与正式池、未归队与可签约如何区分 | 不模拟抽签、选秀、交易、签约决策或基于未生成池制造事实 |
| **S8** 新赛季开始 | 新Season ID/游戏日期、名单/合同/新秀转换、教练球队归属、赛程重建、训练/设置、以前所有确认历史 | `schedule`/`game-mode`/`organization`/`affiliations`→`seasons`、`roster_memberships`、`games`、`native_identity_links` | Native身份何时重用/重建，上一年人/队/合同怎样有证延续，同一库Schema能否同时容纳新旧年度 | 不跨存档fork/继承/合并，不按姓名强合球员，不复制旧年度当新观察 |

## 3. S7更细粒度的“临时食材”目标

| 子窗口 | Codex应寻找的新增材料 | 最小有效判据与避免误判 |
|---|---|---|
| 员工市场 | 可候选聘任的COACH/STAFF源、role/team指针、真实合同状态、聘任前后身份 | `COACHDATA`池存在不等于“此人可以签约”；未证生命周期单独列UNKNOWN |
| 抽签前／后 | 实际Pick资产/归属/序位变化、Lottery实际结果Native数据 | 根据游戏给的结果读存，不能据未来选秀权的年份猜本年抽签结果 |
| 正式选秀前 | 官方参选球员名单、评级UI、DraftClass年度、每个prospect的源槽/身份 | 研究用 `market` Prospects可能是预置Template；模板Native ID不自动成为新秀 |
| 选秀完成后 | 真实DraftResult、被选球员生成及其PLAYER/TEAM/ROSTER键、实际选秀字段 | 不能预设选秀前和之后的球员实体是同一个原生对象；需要before/after对照 |
| 自由市场／新秀签约 | 自由球员身份、资格/可签约状态、合同真实字段、所属与状态 | `affiliations` Native分类不等于实际可签约，也不由状态变化自动产生已发生签约事实 |
| 训练营／赛季转折 | 真实训练项目与选项、球员自然成长的Native值、阵容切换及池退出 | 保存游戏给出的能力与训练数据，不再实现能力成长模型 |

S7独立详细方案已在 `02_evidence/06_S7_休赛期分窗口现场来源发现与开发衔接规划_v1.md`。**实际子窗口可更细或发生先后差异，按游戏真实UI与Human进度调整；不能靠计划表假设它同时存在。**

## 4. 每个 Codex 场景包必须完成的“食材→容器”审计字段

场景里每个目标UI栏目或Native可读字段，都生成机器可对比的记录（可以聚合为一个字段清单，**不是每个字段单独签批**）：

| 字段 | 要求 |
|---|---|
| `scene_id/subscene_id` + `game_stage_evidence` | 人类提供的真实窗口、原生游戏日期/模式、观察范围。研发窗口≠正式采集频率 |
| `ui_page_tab_label` / `game_display_sample` | 原版目标游戏实际显示值/单位/状态；非UI来源需明确性质及访问权限 |
| `native_container/directory/field` | 实际来源对象/槽/Getter/字段、Native类型/编码及版本；找不到填UNKNOWN，不编偏移 |
| `subject_identity` + `save_id/season_id` | Native原ID与有证canonical身份、引用关系与源作用域，身份不明时保留source-only |
| `generation_status` | 严格区分 **实际已可读、实际观测空、实机证实尚未生成、来源读取失败、未观察/未授权**；不能把“当前没截图”当“没生成” |
| `reader_and_codec` + `table.column` | 复用或确需新增的Reader/Codec及具体typed表字段映射，带来源等级与决定；同一种食材不同场景不能重复造全套表 |
| `game_legal_range/unit/permission` | 真实值/类型/枚举、合法值域证据、敏感性、可读取/可写入成熟度和依赖；可读绝不自动等于可写 |
| `capture_unit_id/observed_at/source_artifact` | 一致性单元、真实来源回读或源文件hash、场景生命周期与可复查证据 |
| `query_readback_and_negative_case` | SQLite入库后查回**对应原始游戏数值和对象**、身份/缺失/权限负例；不自行累计篮球数值来验证正确 |
| `coverage_verdict/next_action` | `REUSED_AND_VERIFIED`、`NEW_CONTAINER_DELTA_PROVEN`、`READER_EXTENSION_NEEDED`、`SCENE_NOT_YET_AVAILABLE`、`SOURCE_GAP_UNRESOLVED`、`NONCORE_EXCEPTION_PENDING_HUMAN`等，逐项分清事实与工作包 |

## 5. Codex “为什么做／什么时候停”

**场景首次进入**：先做有界UI目标目录→已知原生来源/Reader→已存在SQLite表字段对照。按“复用→局部补源码/列→留缺口”的次序，不以固定每场景新增表数为绩效目标。

**一个目标数据族可以标已证**：至少存在该场景可复查的原始UI/Native来源、可确证身份和字段语义、typed入库成功、同unit查回、范围/完整性/未知标注；有历史真实证据且适用性明确时可避免重测。原生游戏不显示的字段须按批准的非UI范围及权限解释，不用猜测补齐。

**短时场景退出前**：尤其是S2/S4/S6/S7，保留必要的可重放最小原始证据、字段/来源表和当次失败/缺口，不在已离开的不可回溯窗口事后编造证据。由Human决定是否继续进度；Codex不得自动推进或保存游戏。

**停止开发／向Human反馈时**：
- 新目标已能用现有容器和Reader实测填入与查回：无新增工程。
- 有数据确实存在但v25字段/Reader缺失：提交**最小可证明差集**及受影响关系/迁移方案，纳入已授权工程任务；重大ADR/需求变化才Human讨论。
- 游戏阶段还没到，只有候选结构：记录`PENDING_SCENE`并停止静态猜测；以后现场继续，不虚报通过。
- Human已批非核心逐项例外：登记精确引用和影响；核心目标不能靠自批排除。
- 除未来单独授权的Native写任务外，本取证默认**只读**；阶段内不产生GM/Coach/Player业务算法。

## 6. 阶段02/03成果分界及整体收敛

**阶段02现在输出**：
- 已批准目标业务领域×S1–S8潜在游戏数据目录；
- 101表/20 Reader的复用映射及`UNKNOWN`/原型未证差集；
- 真实UI/Native在对应场景才能发现的项目清单；
- 影响SQLite容器设计的身份、关系、时间、合法值域、字段权限的**有界设计约束**；
- 下一阶段能够被Codex执行并验收的现场发现任务包（本文件尚未实际派发）。

**阶段03可输出**：基于现有v25、Human批准的ADR和已证字段，做完整可执行SQL/字段字典/关系/数据流的有证实现模型B，准确指出仍需待场景动态实证的列/来源及扩展规则。不能在阶段02无实机证据时假装已得到全部未知数据，也不能用仍有场景UNKNOWN为借口无限延期现有可行Schema工作。

**最终验收**：必须用Human实际提供的场景或能证明适用性的已有证据验证目标容器真实读取→typed装载→查询；核心容器不得从仅有DDL宣布PASS。真实Native写和未来大批量写后验证属于**已批准目标的后续有界工作包**，执行仍需明确Human授权，不能提前做。

**参考**：本Run `01a_需求共识_A0_v1.yml`、`01b_需求结果_A_v1_草案.yml`、`02_evidence/01_v25_结构与Reader只读盘点_v1.json`、`02_evidence/02_场景与Reader静态覆盖矩阵_v1.json`、`02_evidence/03_RQ02-01_来源缺口归并与场景优先级_v1.md`、`02_evidence/04_S1_Box身份严格性与缺口根因核销_v1.md`、`02_evidence/05_S4_S6_原生统计荣誉历史来源容器核销_v1.md`、`02_evidence/06_S7_休赛期分窗口现场来源发现与开发衔接规划_v1.md`，固定v25 `TABLE_CARDS.md`和`refresh.py`；PR#8生命周期场景合同为已知非master候选来源，其与正式Human A冲突时以Human批准A为准。

**只读范围与授权**：GitHub静态核对及本规划Run文档整理；不执行本机/游戏/Native读写、不改变DDL或目标权威A、不派发Codex/Antigravity、不合并master。
