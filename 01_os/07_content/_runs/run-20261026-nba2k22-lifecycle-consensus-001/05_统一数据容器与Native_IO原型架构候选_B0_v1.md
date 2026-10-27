# NBA2K22 第一大任务｜统一数据容器、场景采集和 Native I/O 原型架构候选 B0-v1

> **版本/状态**：`B0-v1 / STAGE02_PROTOTYPE_DESIGN_CANDIDATE_NOT_STAGE03_B`，2026-10-27。
> 本文件是 GPT 开发规划成果；**不是已经完成阶段02、不是 Human 批准的阶段03 实现结果 B、不是 Codex 工程代码或施工授权**。任何未证 Native 内存机制/偏移/值域不得凭规划冻结。

## 0. 建模出发点与权责

**一句话**：用同一套可验证、类型化、可复用100个赛季的数据库容器，容纳 NBA2K22 PC 离线 MyLEAGUE 不同阶段所生成的全部目标文字、数字和对象关系；S1–S8的作用是发现实际“食材”，不是开发八套场景业务引擎。

- **产品依据**：Human批准的原第一大任务 `A v1.9`（九业务领域 RES-P/G/T/C/M/L/H/S/D）、2026-10-26 `A-v1-RC01`（独立任务六个RES结果及RR-01至RR-06）、初始原型协同设计 `V0.4`、`ADR-01`一档一库和`ADR-02`属性/倾向typed快照、徽章/PlayType关系行。两个任务的RES编号分别解释，不能互相覆盖。
- **已批准的核心目标**：`RES-01/02`数据来源/完整Schema/八场景可填充；`RES-03`字段可读/可写与共享Native机制分类；`RES-04`历史只追加、来源与当期查询；`RES-05`获准的实时内存批量改写/新采集入库全量清单核对；`RES-06`独立工程证据、最终10K+字段批量自动验收及Human游戏UI抽样。
- **明确非目标**：不额外重算游戏已算好的累计/场均/排名、重新评奖、开发交易/选秀/签约决策规则或人格、自动游戏推进/监听调度、存档回档/跨档合并、不做 Save/Reload 写盘持久化验收。
- **人机分工**：GPT提出架构候选、资料缺口、讨论议题、分包和验收；Codex为后续工程实现单一Owner，进入相应Human提供的游戏场景后进行Native追踪/Reader/DDL/接口编码和实测；不自动派Codex执行。GPT可在当前规划分支整理证据，不操作本地机或游戏。

## 1. 固定资产基线与归因

- v25固定候选 `a3927fb150a213201e404cca043ced4f57409bd1`：**101张STRICT表、1789列、20注册Reader族**，静态源码与字段字典对应已核；不是完整实机场景验收。
- 同Run `02_evidence/08_v25_101表20Reader九领域静态映射_v1.json` 为**101表逐张机器清单**，包括领域/粒度/历史最近单元行数。**不要在本候选重复抄一份虚构的“最终DDL字段全集”**。冻结 `schema.sql`、`schema_model.py`、`field_dictionary.json` 为03物理差集核验基线；03仍必须交最终每表全部字段、类型、PK/FK、索引、来源、值域和可执行SQL。
- `schema_model.py` Blob `677b115b39b2f6cd93011143c658107b8000d6ff` 的表定义提供对象粒度：`saves`第98行、`seasons`106、`teams`107、`players`108、`staff_members`109、`games`110、`capture_runs`111、`capture_units`112、`roster_memberships`134、`player_attribute_snapshots`142、`player_tendency_snapshots`152、`player_season_totals`226、`team_season_totals`227、`market_state_observations`352、`draft_prospects`379、`draft_results`425、`season_award_instances`471、`award_recipients`476、`external_execution_receipts`525、`external_readback_checks`526、`native_identity_links`527、`season_finalizations`533。**定位为候选实物，不视为对应Native已可读/可写。**
- `refresh.py` Blob `4c0bb0859361f6a962fdb1cb1372cef02c481e0a` 注册20家族；第152行明确跨家族批次是多个原子观测单元，**不是同一瞬时世界快照**。无证不能拼新旧来源获得一个“共同当前态”。
- `query.py` Blob `54e70472088a65b9a92e107dc11dcae8a2451b4c` 有玩家/员工/球队卡片、游戏Box、当前期段统计、荣誉、市场、历史、查询/导出等入口；`observation_scope.py` Blob `6d906f7b88ff3c6e35f033ab841fa3f34379c33f` 提供observed-as-of查询约束。
- 开发者历史Source ledger中的 **74/101**张表最近一组各族成功unit有非零行、27张没有：是**有限旧归档截面**，27不是缺表总数、74不等于UI内容齐全或S1–S8验收。

## 2. B0 基础架构：五个逻辑层，复用一份长期容器

| 层 | 职责/输入输出 | 已存在候选与剩余需证 |
|---|---|---|
| L1 `source_catalog` 来源层 | 某真实UI页签/原生对象/阶段 → Native schema/动态指针/来源版本/字段名称或枚举/原值；同时记录实际存在、空、未生成、不可访问/失败 | `native_fields`、`source_artifacts`、`field_gaps`以及Native Reader/Profile已存在；仍缺完整UI↔Native字段逐项正反例、S2–S8窗口证据 |
| L2 `subject_identity` 对象关系层 | 单独save中的`Season/Team/Player/Staff/Game/Pick/Prospect` → 真实Native局部身份、跨年度稳定身份/关系，歧义隔离 | `saves/seasons/teams/players/staff_members/games/native_identity_links/native_player_sources`；未证跨季UniqueId/PreservedId寿命，不能从同名猜合 |
| L3 `typed_facts` 数据容器层 | 以确切对象/字段族/观察或事实粒度保存Native显示/原生值；游戏已提供的累计、获奖、纪录照原样存 | `player_attribute_snapshots/player_tendency_snapshots/player_badge_values/player_play_type_slots`，Box/SeasonTotals，`season_award_instances/award_recipients`，Draft/Staff/Market/Settings等；缺口通过逐场景差集决定扩展 |
| L4 `observation_history` 采集与历史层 | `capture_run→capture_unit→artifacts→typed事实/来源新鲜度`；不覆盖原历史，冲突与Human裁决更正独立记；成功原子unit保留 | 现有`capture_runs/capture_units/source_artifacts/fact_conflicts/annual_fact_claims`，`observed_at`与`source_grade`；检查业务事实最终性/非同时性、跨赛季查询及补录一致性 |
| L5 `operations_contract` 查询与操作层 | 用权限限制的确定性查询/导出取得事实；未来Human授权后，字段类别安全改Native，随后**全新**Native采集入库逐项对账 | `query.py`、`fact_queries.py`、`external_execution_receipts/external_readback_checks`为候选；没有证明可用统一Native Writer、授权试写或10K项能力 |

### 2.1 跨域对象关系候选（实际物理外键和多值关系仍以v25＋03证据为准）

```text
physical save [one independent SQLite database]
 ├─ seasons: one save -> many seasons
 │   ├─ teams/team_seasons -> roster_memberships -> players
 │   ├─ games -> game_state_observations / game_period_scores
 │   │           -> team_game_boxes / player_game_boxes
 │   │           -> playoff_series / playoff_series_games [evidence dependent]
 │   ├─ player_season_totals / team_season_totals [game-provided]
 │   ├─ season_award_instances -> award_recipients [final-source gate]
 │   └─ settings / finance / contracts / drafts / training as observed
 ├─ players / staff_members / teams [save-local canonical identities]
 ├─ draft_pick_assets / ownerships / prospects / draft_results [separate entity scopes]
 └─ capture_runs -> capture_units -> source_artifacts -> time-stamped observations
                              ├─ native raw/source rows, source-only identities
                              └─ typed canonical rows when identity is proven
 external proposed targets / planned commands [not game fact]
       -> Human-approved execution -> fresh Native read capture
       -> typed DB actual observations -> checklist diff -> execution receipt
```

**不成立的快捷做法**：仅用`player_id`把多年数据覆盖到一行；把当前Native slot或姓名当永久球员ID；将`draft_prospect`模板直接等于已生成PLAYER；把一张万能JSON表替代全部对象/typed关系；拿旧unit冒充执行后fresh capture。

### 2.2 容器字段设计的确定性检查

设计/扩展每类数据结构都必须回答：`entity_type`、一行事实粒度、已证source或候选状态、确切`table.column`、数据类型/NULL与特殊值、原始/游戏显示口径、键与基数、观察时间/赛季/阶段、来源与权限、历史/当前投影规则、是否能确定性查询、如何验证真值及负例。当前Native合法值域未证不应提供“可安全写入”的默认值。

**同型年度实例**：`seasons`作为保存和联结的业务上下文，100个年度共用相同表/列/Reader逻辑；Game以实际有证赛季/团队/比赛身份引用，历史观测追加；独立测试存档不要自动合成同一条世界线。单个赛季末游戏已算的stats不从Box重新计算。

**历史冻结**：已完整终局Box与获确认历史获奖等不可无证覆盖。源数据发生冲突追加`fact_conflicts`等可复核记录由Human裁决；新年度事实与首次新生成的获奖按真实时点补录，避免一次P5读取阻断P7 FMVP的新荣誉。

### 2.3 不能现在擅自确定的设计问题

- UI究竟包含多少目标字段、各字段的Native位置/值域/单位；当前字段字典有1394个游戏合法值域`UNKNOWN`，**不是代码缺字段数量**。
- S2–S8的实际来源创建/释放时机、S7正式选秀池与当前`market`模板的关系；必须等Human提供对应游戏场景让Codex实证。
- 具体哪些Native合法字段共用物理Writer机制、哪些需要复合操作/额外联动、哪些只有只读权限。单个属性的值域相似不等于同Native Writer。
- 100年真实数据库占用、各类来源成本与SQLite性能；需一整季样本后的合理成本估算/性能实测，不能先编数字。
- 最终每表全部列的增减、DDL迁移与回填范围及变更后的精确总表数；03提供基于实际来源的差集设计，不能擅自把101写死为永远最终数量。

## 3. A级原型：跨S1–S8“食材发现→容器填充”接口设计

**不是“每场景一套表”**；统一`SceneDiscoveryReport`候选承载以下结构：

| 项目 | 候选必有属性与状态 |
|---|---|
| `context` | save绑定、真实游戏阶段、游戏年/日期、subscene、Native布局指纹、capture unit/source grade |
| `target` | 游戏实际UI页面/Tab/目标字段及显示值/单位；非UI必要原生来源单独标访问级别 |
| `source` | Native容器/对象枚举/原始字段/动态寻址/编码/Reader/Codec/完整度/原值 |
| `mapping` | 已证或候选canonical identity、typed `table.column`、转换版本、权限、NULL与特殊值 |
| `verification` | 真实字段按同单位入库后查询返回游戏原值；覆盖数/失败样本/来源指纹/真实场景适用性 |
| `delta` | `REUSE_VERIFIED`、`READER_PATCH_PROPOSED`、`SCHEMA_DELTA_PROPOSED`、`PENDING_SCENE`、`OBSERVED_EMPTY`、`PROVEN_NOT_GENERATED`、`READ_FAILED`、`NONCORE_HUMAN_EXCEPTION_PENDING` |

以`07_S1_S8_容器导向场景数据发现与Codex交付矩阵_v1.md`的S1–S8任务为实施期目标目录，现场Codex根据真实游戏修正，而不把规划名单变成虚构Native存在性证明。S7各子窗口在Human推进后现场发现并开发；正式采集P1–P12与研发八窗口分离。

**字段生命周期示例**：S7选秀前候选模板 `source_only_prospect`→游戏生成正式选秀结果 `draft_result`→观察到真正新秀`player` ID/Team归属；三者不能在当前直接以模板名合并。若现场证据证明不同设计才可做有界Schema差异更新。

## 4. B级原型：统一CRUD查询与 Native I/O 契约候选（逻辑接口，不是代码）

### 4.1 统一“读”与数据库增删改查的不同层次

- 对数据库容器的**读/查询/导出**：`GetEntity(save,season,identity,as_of,role)`、`ListFacts(domain,filters,unit_id,provenance)`、`TraceField(ui_target)`、`ListGaps(scene)`等只是**03待定的语义示例**；优先复用`query.py`/`fact_queries.py`，不重新开发相同功能。
- 数据库事实新增仅由**真实已采集来源或经授权且已证的外部事件**驱动；纠错只追加，新版本观察是新行不是UPDATE旧历史。操作层可以提供明确更新当前投影或工作清单的受限逻辑，但**不得让普通CRUD绕过原生事实来源、直接改写历史游戏事实**。
- 对**实时游戏Native内容的修改**与对**SQLite中事实表的直接改值**严格分离：要求最终能确定性选择对象/字段并操作获授权Native，但是现场寻址、共享Writer、越界保护、执行器都是Codex后续工程。

### 4.2 字段能力 `FieldCapability`（数据结构要求，不是已证所有字段可写）

`field_id; entity_kind; target_table.column; scene_scope; Native source/decoder; raw/display/typed; unit; enum/range/sentinel; source_layout_version; read_evidence; writer_class; native_addressing_method; shared_writer_mechanism_evidence; role_visibility; read_status; write_mechanism_maturity; current_Human_authorization; required_dependent_fields; exceptional_member_reason`。

严格分开这四层：
1. `READ_OBSERVED`仅证明成功取数；
2. `WRITER_CLASS_HYPOTHESIS`不证明可写；
3. `WRITER_MECHANISM_REPRESENTATIVE_VERIFIED`需Human单独批准实机试写并证实**同类型、合法值域、Native编码/寻址/共用Writer结构**，成员可按授权规则继承“机制已证”，不是声称每字段实测；
4. `OPERATION_AUTHORIZED`来自具体Human执行许可，与上面的技术可行性独立。

### 4.3 批量变更协议 `ExecutionPlan → NativeAttempt → FreshCapture → Reconcile`

```text
Human明确本次测试游戏/存档/允许字段类别/对象/目标/时间
  ↓
ExecutionPlan (execution_id, expected_old, new_target,
 save_id, season_id, object_id, field_id, class_evidence,
 unit_dependencies, authorized_scope)
  ↓
DryRun: field/identity/permission/range/source/version/
 old_value/related-object/consistency-unit checks
  ↓
Only if allowed: bounded native writes by independent business units
  ↓
Record each attempt; partial business unit != SUCCESS;
 independent proven completed units may remain valid
  ↓
Trigger entirely NEW Native read capture bound to execution_id
  ↓
Reader/Codec -> typed SQLite actual rows in read_capture_batch_id
  ↓
Compare EVERY planned object×field + mandatory related invariants,
 preserving missing/unknown/mismatch and unit-level failures
  ↓
PASS_REALTIME_MEMORY_ONLY or PARTIAL/UNKNOWN/FAILED with evidence
```

**验收不允许**：仅看调用返回ok、旧数据库记录恰巧等于目标、UI随机抽样全对，就宣告整批全对；也不要求Save/Reload持久化。补偿要先有单独有证安全方案和Human权限，没有安全补偿的部分写入必须保留异常和报告，不声称回滚。

**重要工程未知**：`external_execution_receipts`与`external_readback_checks`是现有**表候选**，但不证明上述全新采集业务协议已工程实现；最终清单和执行状态可能需要有证扩展，留03形成精确差集。

## 5. C级原型：面向Codex的验证分层，不提前开发

| 门 | 什么才可标通过 | 现阶段状态 |
|---|---|---|
| G1 固定 v25 基线 | 完整表/字段/字典/DDL/Reader固定版本比对且差异可信 | 静态已部分成立；Windows独立回归尚未跑 |
| G2 逐场景核心容器 | 实际适用窗口中真实UI/Native数据→对象完整枚举→Reader/typed→同unit查回，非核心缺口有Human明确例外 | S2–S8新取证 `PENDING_SCENE`，不可声称PASS |
| G3 稳定容器/100年结构 | 第一季发现的所有目标类别可被同一逻辑Schema的不同季节数据实例装下；身份/历史跨年度查询不混合 | 理念已Human决定；物理容量实测/跨年场景待证 |
| G4 字段Writer类别 | 有直接共享机制/范围/身份依据，类别代表在另获许可的实机中写入并新采回读；例外分类 | 没有本轮新实机权限，`NOT_VERIFIED` |
| G5 单业务unit | 按清单预检、Native尝试、全新采集、数据库字段逐项对账、失败隔离，且来源可复核 | `DESIGN_ONLY` |
| G6 完整集成高负载 | 模块全成品后，10K+合法字段/数百球员/合同/归属等真实负载脚本，每项新采数据库全量核对+Human抽样 | 最后阶段工程验收项，绝非本轮工作 |
| G7 OS独立复核/发布 | 独立审核与保护分支门禁，未经批准不master合并 | `NOT_RUN` |

关键疑问标`EVIDENCE_REQUIRED`，但不能因为当前游戏没进入S7就阻止形成可逆的完整架构候选；也不能因此跳过未来核心现场验收。

## 6. 将来阶段03必须把B0收敛成可施工的正式B

具体必须有：
1. **物理Schema**：固定精确候选总表数，逐表全部列与类型/单位/默认值/合法值域/唯一及CHECK、PK/FK/复合索引、来源、当前与观察/冻结规则、SQL DDL完整可运行；交增量迁移与冻结旧数据规则，不编造未证Native字段。
2. **全域目标目录**：九业务领域和UI目标字段/Tab ↔ Native来源/Reader/Codec ↔ `table.column`双向Machine catalog；S1–S8每类目标映射及缺口不能靠总表数证明。
3. **查询读协议**：对象与场景、最新可证时间/历史观察、来源与权限正确，游戏已计算的统计照原样显示。
4. **写协议**：字段类别/合法游戏范围/共享Writer机制证据、Human授权、批量修改清单/一致性单元/新采对账/失败处理之接口与异常约定。
5. **场景发现与工程任务**：各场景Codex独立最小任务包、顺序与必要中止条件；实机场景差集反哺Schema，不另建不同年度业务表。
6. **验收/负例与信源证据**：证据成熟度、动态游戏场景不可提前获得的清单、独立验证门、最终高负载条件和Human必需授权。
7. **重大ADR清单**：继承一档一库/typed字段族/append-only；如果确有新增不可逆身份、历史、权限、Schema核心选择，先提供证据与备选交Human，而不是GPT单方冻结。

## 7. 本轮可以自行决定与必需Human参与的界面

**自主完成**：复用优先、已有table/Reader静态核查、工作包候选拆分、明确已证和UNKNOWN、技术值域未证即不授予可写、阶段02资料修订、同类游戏数值直接读存、下游Codex须真实游戏现场证据。

**不自主决定**：减少核心业务数据范围、排除核心场景、跨存档自动身份融合、改一档一库或历史不覆盖、非核心缺失正式例外、游戏/Native访问授权、实际Writer试写、Codex工程派发、最终物理B批准、master保护发布。需讨论时按OS的 `stage_collaborative_deliberation` 核对承重缺口和方案后少量追问，不重问已获批ADR与RR。

**当前决定**：暂不发Human选择题。已批准目标充分，当前下一工作是把此架构候选转为**Codex可消费的阶段03候选工作包**并对RQ02-03至07分项整理来源与可行性限制，而非扩大需求或代Codex写代码。

## 8. 来源引用与验证边界

- 本Run：`01b_需求结果_A_v1_草案.yml`原批准Blob `b60570547c6686261a1e7ae756605dce5e37429a`；`01b_结果A完整性与Human版本确认_20261026.md`；`03_跨任务需求原型与阶段02防偏离继承索引_v1.md`。
- 本Run `02_evidence/01_v25_结构与Reader只读盘点_v1.json`、`02_evidence/08_v25_101表20Reader九领域静态映射_v1.json`、`02_evidence/09_九领域S1_S8容器覆盖差异与开发优先级_v1.md`、`02_evidence/07_S1_S8_容器导向场景数据发现与Codex交付矩阵_v1.md`。
- 固定v25 `TABLE_CARDS.md` Blob `1e9ab7731ef50b466f1f7e92973941d782e5bed9`、`schema_model.py` Blob `677b115b39b2f6cd93011143c658107b8000d6ff`、`refresh.py`、`query.py`、`observation_scope.py`上述Blob。
- 本轮仅GitHub只读和领域Run规划文件写入；**没有**本地repo/Windows/实时游戏/数据库执行，没有Native新采集或写入，也没有开发任务派发与master集成。
