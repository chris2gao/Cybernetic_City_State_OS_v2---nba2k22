# NBA2K22 PC MyLEAGUE — 原生页面/对象/数据生产与操作链重建：Native I/O 底座蓝图 V2

**2026-10-21；状态：RESEARCH_DERIVED_ENGINEERING_BLUEPRINT / 待玩家分别授权实施。** 本文件是对[已撤回V1](NATIVE_IO_CAPABILITY_EXPANSION_AND_FUTURE_ROLE_FOUNDATION_V1.md)的技术方法纠错。**不是当前游戏完整页面已经认证的清单，不批准游戏写入、推进赛季、正式数据库迁移、自动合并或启动DEV28实施。**

## 0. 唯一目标：以游戏数据体系为边界，而不是以当前GM需求为边界

从DEV29 R01–R07的游戏机制研究、DEV06/10/12/14/15/16/23/24/28及现有原生采集与SQLite证明，真正需要恢复的是：
`NBA2K22实际UI页面/表格/操作 → 数据由游戏引擎产生/统计/渲染的路径 → 原生对象/关联/索引/保存机制 → 可利用的读取/查询源 → 保留原始结构的外挂完整数据镜像 → 页面等价的结构化查询 → 经玩家批准可执行的原生动作及反馈`。

**两个重要区别**：
1. **一个游戏页面不必对应一张SQLite物理表**。可能为多个原生对象联结、计算、索引或瞬时UI聚合结果；应以页面作为**覆盖/验收视图**，以实际原生对象和关联作为**数据源/Schema依据**。
2. **页面显示表格不证明游戏内部存储SQLite/SQL表**。原生实现可能是C++记录数组、指针/索引链、内存缓存、存档二进制、native Getter或内部数据库。探索是否存在直接查询的游戏数据库/API是P0研究题，未经证实不得声明可以执行游戏SQL。

**先完整理解游戏，再建模数据**：能力、倾向、徽章、身份、统计、合同、伤病等应当共同覆盖完整球员对象。不能因未来人格模型先关注Loyalty/Win/Financial Security就只抓这些字段，也不能把R07的694研究项当694个原生字段。

## 1. R系列/开发系列 → 应恢复的实际游戏对象与页面视图

下面是**研究引导的待核PC22页面/数据家族**；具体页面、Tab和列必须从目标NBA2K22 PC本世代MyLEAGUE实机菜单/显示逐项确认（其他世代资料只提供研究线索）。括号为研究追踪锚点，不代表全部原生字段已证。

| 游戏对象与完整页面视图（待实机逐页登记） | R系列及关联工程 | 应探明的原生对象/生成路径与操作 |
|---|---|---|
| **GAME/SEASON**：日历、赛程、GameID、已完赛比赛页面、主客队/个人全部Box子表、进阶统计、投篮图/热区、赛后页面、Game Logs、跨季历史 | R01；R06-C；F01–F06/F31/F38；DEV24；未合并Match History候选 | SEASON/SCHEDULE、比赛记录、LineScore、BoxScore、StatBank、游戏生成模式、UI渲染与历史保留范围。**先确认页面所有表/列，再决定哪些是真正已保存的原生数据**。 |
| **PLAYER全对象**：名单/个人卡/编辑页面全部Tab与列；Vitals/位置/身份/年龄/外观、全部Ability/耐久、全部Tendency、PlayTypes、全部Gameplay及Personality Badge、合同/角色/士气、伤病/健康、出勤、赛季/生涯/逐场统计、训练/成长与历史 | R04-A/B/C/D；R03；F07/F13–F19；DEV14/15；`player_pool`/Profile/Registry | PLAYER整体原始记录+独立PLAYER_STATS和其它真实关系/缓存/子对象。**逐页双向对账，不用72字段代表全体**；对原结构未解字段保留UNKNOWN，禁将第三方Badge/倾向名称强套未知byte。 |
| **TEAM/FRANCHISE**：球队名单/深度/管理、教练职员、资金、经营与市场、合同与薪资、球队赛季/历史统计、球队设置 | R05；R02；F05/F08/F09/F20–F22/F26；DEV10 M1、DEV14、DEV06 | TEAM结构、名单成员指针、球队统计、财务/合同关联、职业管理相关对象；需要区分游戏实测与外部模拟金融规则。 |
| **COACH/TACTICS**：教练与岗位、POE/战术体系/ACE/攻防设置、专属Book、战术槽/CRC/名称/原生类型、Freelance、个人/整体防守与执行反馈 | R02；F09–F12/F14；DEV06/12/16/23/28-1 | CoachData、关联TEAM/PLAYER、本队Book独立容器与共享Play条目、调用条件与游戏UI真实候选；字符串匹配不等于真实绑定。 |
| **TRAINING/HEALTH/GROWTH**：球队训练、个人训练、导师、体力/疲劳、伤病状态/历史、成长与退化 | R03；F15–F17；DEV14训练6+5现状 | 检查相关页面真实记录、不同时间域/比赛域的动态性，避免把Stamina能力值当场上实时疲劳，把已注册训练字节当真实训练结果。 |
| **MARKET/DRAFT/STAFF**：自由市场、报价/签约、合同条款、交易、选秀权、球探、Draft Class导入、实际选秀、员工聘任及过程状态 | R05；F19–F26；DEV04/37/38、DEV14 | 原生多对象操作及关联的真实状态转换；已批准Trade部分实证，Signing原生执行仍阻断；不能以研究选项直接覆盖执行器。 |
| **WORLD/SETTINGS/SIM**：Setup、World、日历Sim参数、3D Gameplay USER/CPU、两种Normalize、各种比赛方式、Rule Changes、游戏赛季阶段 | R06-A/C/D；F27–F32/F36/F40；DEV09/14 | 游戏设置真实页、合法枚举、谁消费该滑块/模式、刷新与AI覆盖；Sim引擎和3D消费路径应分离证据，不假设内部引擎公式已证。 |
| **HISTORY/RECORDS/MEDIA/SAVE**：各季奖项/纪录/队史/球员生涯、新闻和实力榜、选秀及交易历史、存档/恢复/跨年留存 | R06-B/C；F33–F38；R05历史选秀 | 历史事实结构/原生UI来源、持久保留和可查询窗口，明确本世代是否具有对应页面，跨世代/现实NBA不能伪装为当前存档事实。 |

**跨所有领域F39**：采集批次、原始源、对象身份、存档代际、数据库镜像、权限裁剪、查询和发布的基础设施；不应重新造第二套事实数据库/审批中心。

## 2. 已实际具备的结构性基础（优先复用）

- `src/source_extensions.py::roster_directory`：从已校准根目录解析`players(0x4F0=1264B), staff(0x160=352B), player_stats(48B), team_stats(62B), draft_assets(32B)`的**独立数组/目录/索引**，并做地址范围与终点方程校验。
- `src/dump_player_pool.py` / `player_pool.sqlite`：已有PLAYER完整`raw_struct BLOB`及基本身份，不能从此推定已全部解码或当前游戏显示全部数据已在`GM_SANITIZED`查询层可读。
- `config/memory_field_profile.json` + `src/source_extensions.py::decode_fields`：PLAYER已登记**55个attributes（含16部位耐久）+17个合同**；另有STAFF/TEAM_STATS/PLAYER_STATS局部字段；`player_details`目前主要输出attributes+contract及部分身份，不是完整PLAYER DTO。
- `config/state_io_native/player.json` + `src/gm_state_io/registry.py`：PLAYER倾向99个原始字节，其中48个已命名、51个UNKNOWN；现有4+1战术角色槽、教练/训练/世界/Gameplay/Playbook候选。技术可写与玩家授权/生产回执分别登记。
- `docs/31_SOURCE_EXTENSION_DISCOVERY.md`已有真实样本及双向Staff/队伍归属、赛季统计守恒、全球员完整目录读回、DraftData原生Getter的静态/运行代码研究经验。
- `src/gm_data_access/query.py`：本项目自己的SQLite受限只读查询层（不是游戏内部SQL引擎证据）；已有双库、安全投影、原始表限制、GM脱敏与批次约束。
- `DEV14_STATE_IO_RUNBOOK.md`：多存档/代际、`full_verified_v1`、控制库与单次经批准写入/readback；不要重建。
- **未合并**`codex/season-match-history@b4e17e1`：SEASON/Schedule/BoxScore/StatBank候选Reader、5表Schema及查询CLI；四项离线合成测试曾通过，但PC22真实偏移、GameID、Stats对象身份/来源、历史保留、事务/查询隔离未正式认证；不可直接合main。
- **资料冲突**：早期`docs/02_DATA_STRUCTURE_SPEC.md`称PLAYER步长`0xDF0`；后期有数组终点方程/实测采集支持`0x4F0`。必须保留不同上下文与版本、证据等级，不可按旧文档直接覆盖正式Codec/本机Reader。

## 3. 首先调查游戏内部的真实数据访问/生成机制

这是**独立P0技术研究题**，优先于大规模新建SQLite表：

1. **页面资产与真实结果**：对目标PC22 UI逐页截图/记录完整列、筛选/排序、当前存档/游戏日期/是否赛后、所有Tab及可编辑控件；在不触发保存或模拟推进的情况下辨认页面层级。既有R指南中未经目标PC认证的入口保持`REFERENCE_ONLY`。
2. **原生对象定位**：页面元素反查到目前已知ROSTERDATA/PLAYER/TEAM/STATS/SEASON等数组或子结构；找不同页面复用的同一ID/Index/指针及取值、映射、聚合口径。
3. **直接数据源途径的鉴别**：非侵入式检查安装目录/文件格式/导出定义/模块依赖/可读取的持久数据文件；如果确有引擎内部数据库、SDK或原生查询函数，记录格式、版本、接口、只读可用性、权限和对象稳定性；若只有内存数组/Getter，优先做统一Object Reader，**不得假定SQL、不得为证明猜想而注入DLL/Hook或修改可执行文件**。
4. **数据生产链**：同一场比赛赛中、赛后、赛季聚合、日历视图、历史视图可能更新不同对象或经Normalize变化；按实际来源、时间和版本证明相等/不等，不从一套累计统计反推另一套单场表。
5. **缓存/存档留存**：同一数据对象是否为UI临时缓存、进程中常驻、存档中持久、跨季历史；长期游戏需要捕捉原生在覆盖前保留的真实事实，否则明确`HISTORY_NOT_RETAINED`，不得人工造历史。

交付`NATIVE_STORE_AND_QUERY_CAPABILITY_REPORT`：对各对象明确`GAME_INTERNAL_SQL_VERIFIED / NATIVE_GETTER_VERIFIED / MEMORY_STRUCT_VERIFIED / GAME_SAVE_PERSISTED / UI_ONLY / UNKNOWN`。这些等级按证据分别成立，不将`memory structs`称为`database tables`。

## 4. 推荐的工程组织：Native Object Graph + 页面等价Query View

**A. 原生对象层（Native Object Catalog）**：对象名、真实类型/记录长度、原生ID/代际/生命周期、源地址/目录/Getter、原始字节、字段字典、索引关联、未解区间、版本/证据。完整的原始记录尽量优先保存，而不是因为当前没有用途就丢弃已合法采集的数据；确认为敏感/玩家限制内容须在隔离管理员层保存或不对外发布。

**B. 页面目录层（UI View Catalog）**：每个真实游戏页面及完整Tab/列、类型、单位/显示格式、排序和筛选、可操作项、所依赖对象/聚合公式、页面原值证据；一个视图可以Join多个原生对象，也可能来自即时计算。逐项`MATCHED_NATIVE / NATIVE_UNDECODED / DISPLAY_DERIVED / UI_ONLY / NOT_OBSERVED / UNSUPPORTED`。

**C. 采集与数据库镜像层（Object Snapshot + Relations + Timeline）**：重用两事实库`league_state.sqlite`、`player_pool.sqlite`与DEV14发布路径；实体表+原始结构证据+关联/时间表+必要的聚合/视图。每份原始观察绑定`save_id/save_instance_id/generation_id/batch_id/game_date`与原生对象身份/来源版本。**不要在发现前就声称一页一表或创建数百空列**；首先在独立候选schema上测试，在玩家批准后才由Codex执行正式数据库迁移。

**D. 有界查询层（Game-equivalent Query Services）**：按`PLAYER_FULL_PROFILE`、`TEAM_ROSTER_AND_STATS`、`GAME_COMPLETE_REPORT`等完整**视图/对象级**入口查询，再可用受限SQL聚合或关联返回需要的部分。角色安全视图按权限投影，`GM_SANITIZED`不能泄漏真实Potential；完整管理员来源与模型可见源分开。SQL是外挂SQLite的可验实现，游戏原生SQL接口要另证。

**E. 原生控制层（Native Operation Catalog）**：把游戏UI实际允许的所有动作、字段值域/枚举、作用对象与多对象一致性加入研究目录。分别标注`READ_ONLY`、`TECHNICALLY_LOCATED_UNAUTHORIZED`、`APPROVED_ACTION_EXECUTOR`等；允许的游戏写入需要对象身份/CAS前态/计划/用户逐案批准/事务补救/原生读回/需要时Save重载和实际游戏效果观察。独立研究“可控”不等于GM普通经营有权改任何字段，尤其不得直接改普通球员Ability/Potential/Badge。

## 5. 全面验收指标：以页面、对象及来源闭环，不以字段总数

1. **页面覆盖**：已实机确认的页面/Tab中有多少已完整登记列与操作；未知具体菜单路径不得冒充已枚举完成。
2. **原生结构覆盖**：对象数、已定位关联数、已完整保存原始结构数、结构内部已解释字节/位域覆盖率、未知部分；55/72/99等不同口径不得相加冒充百分比。
3. **展示一致性**：同一存档/日期、同一球员/球队/GameID的UI行和采集值比对；各列标明单位、按赛季/场均/Per36的分母及显示Normalize；同场个人PTS/全队分与赛季合计守恒按规则解释差异。
4. **数据生产/历史**：同次比赛/两次采集/赛季更替之间的对象更新、旧Game/Box保留、重新登录及Save/Reload后的留存边界；缺失真实来源应报告，不合成伪事实。
5. **控制覆盖**：原生菜单合法选项已证的数量/对象、可读但未获授权的数量、已获批准可执行动作的闭环数量；写入字节、游戏接受、AI覆盖、Save留存、因果效果分开。
6. **跨模型交付质量**：每个Flash子模块提供`source/version + raw sample/UI对照 +纯解码源码 +fixture +测试与负例 +可用来源/API契约 +UNKNOWN`；Codex可用少量独立断言复核，不须重跑全面逆向。未核实同型号子代理默认禁用。

## 6. 具体实施顺序与唯一owner

**既有FINAL-CODEX保持Codex独占**：其40族矩阵/20缺口/静态证据工作由原Codex恢复，Flash不接手余下主审计。其结论作为后续“现有什么”参考，**不能因此把40研究族视为完整PC22页面目录**。

**新研发工作包（需要分别授权）**：

| 编号与技术职责 | 适合owner | 可独立交付及复核 |
|---|---|---|
| **NATIVE-01 游戏页面与对象映射研究规范 + 实物清单样板** | Web开发规划/Flash在游戏中逐页调查；各自独立小包 | 实际页面ID/Tab/完整列/控件、截屏/版本/状态、每列候选原生源、UNKNOWN；从单一具体页面家族开始，不一次假装摸清整个游戏 |
| **NATIVE-02 游戏内部数据存储与Query机制鉴别** | Flash独立技术探索，Codex最终复核 | 证明/否定当前证据范围内可查询游戏数据库、Getter或数组目录；给出只读复现证据和最小数据访问入口，禁止无证声称SQL |
| **NATIVE-03 GAME页面族完整对象实证** | Flash独立子模块 | 单场完整UI页面及所有子表与SEASON/SCHEDULE/Box/Stats关系、可重放原始样本和Reader/Codec，保存疑难字段原始字节，先与一场真实GameID对照 |
| **NATIVE-04 PLAYER页面族完整对象实证** | Flash独立子模块 | 一名同档Player的全部可见Tab/列与1264字节原始PLAYER、其它统计/徽章/倾向/合同关系的完整map；对未解区间和原生独立记录列出缺口、纯读取/解码测试 |
| **NATIVE-05 其它UI数据家族** | Flash逐个独立家族 | Coach、Team、Training、Finance/Draft/Staff、World/History/Save；不开发半途混用的巨型跨域模块 |
| **NATIVE-06 正式统一Schema、查询、安全执行接入** | Codex主工程owner | 以Flash合格模块+DEV14/M0/Registry原架构映射回正式物理库、查询、批次/权限、测试/发布及经玩家批准后执行；拒绝未达到真实性/兼容门槛的模块 |
| **NATIVE-07 角色模型应用** | 未来另立项 | 在Native事实/合法动作足够透明后建设独立人格，不反向硬编码底层或拿原生属性当人格数据库 |

**工程解耦原则**：Flash负责可独立验收的**完整数据源家族模块**（而非Codex主工程的“半份Schema/半份报告”），Codex拥有生产架构和最终集成；同一生产路径只有一个owner。所有页面/对象能力都是逐层成熟度，不因文档发布自动授权原生写入。

## 7. 证据与本次修正依据

- 游戏机制：`docs/game_mechanics/guides/K01_K02_GAME_STATS.md`、`K03_K12_PLAYER_PROFILE_AGENCY.md`、`K04_COACH_AND_PLAYS.md`、`K06_TRAINING_HEALTH_GROWTH.md`、`K07_K08_K09_FRANCHISE_OPERATIONS.md`、`K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md`、`K10_HISTORY_AWARDS_MEDIA_R06B.md`、`K11_SEASON_SAVE_PERSISTENCE_R06C.md`。
- 研究索引：`docs/game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json`（40族），`R07_ITEM_TRACEABILITY_INDEX_V1.json`（7卷694项），`R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json`（20缺口），R04/R05/R06各分域JSON。
- 原生/执行工程：`docs/31_SOURCE_EXTENSION_DISCOVERY.md`、`config/memory_field_profile.json`、`config/state_io_native/*.json`、`src/source_extensions.py`、`src/dump_player_pool.py`、`src/gm_state_io/registry.py`、`src/gm_data_access/query.py`、`database/schema.sql`、`docs/DEV14_STATE_IO_RUNBOOK.md`、`docs/37_APPROVED_TRADE_EXECUTOR.md`、`docs/38_APPROVED_SIGNING_EXECUTION.md`。
- 既有计划：`docs/development_tasks/DEV_20261020_24_BPTI_ANTIGRAVITY_GAME_DATA_SOURCE_REQUIREMENTS_V1.md`、`DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md`、[多模型owner规则](MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md)。
- 早期设计（包括`docs/02_DATA_STRUCTURE_SPEC.md`的0xDF0）属于**待源证冲突核查的历史文档**，不能凭其标题覆盖后期经实际验证的0x4F0等原生信息。

**结论**：下一期的核心开发对象不是“GM还想要的字段”，而是**实际PC22游戏完整数据页面→原生数据对象及查询/生产机制→外部可复查数据库视图→受控原生操作与真实游戏结果**的全链路。这套底座才可能让未来独立的GM、Coach、Player模型获得与游戏同等丰富的事实、原生选择和反馈机制。
