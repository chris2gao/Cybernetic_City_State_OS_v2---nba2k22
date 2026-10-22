# NBA2K22 GM Engine — 网页GPT开发规划窗口完整交接快照 V1
**生成时点：2026-10-21（原开发规划窗口达到会话长度上限前）**  
**适用角色：新开的网页GPT开发规划/独立审核窗口；供GM、数据分析、Codex、Antigravity阅读。**  
**仓库：`chris2gao/nba2k22-gm-engine`，默认分支 `main`。**

> **恢复优先级**：本快照固定的是项目目标、已知技术边界、最近验收和待续路线。**任何时间敏感的“当前下一任务/完成情况”一律先实时重读** [研究进度](../game_mechanics/PROGRESS.md)第一节、[共享项目状态](../34_BASELINE_CURRENT_STATE.md)、[开发规划记忆](../../web_gm/memory/DEVELOPMENT_CURRENT.md)与最新`main`。不要把历史段落的`NEXT_R02`、`PR12_DRAFT`、`R06_PENDING`当现状。下面专门记录截至本快照读取GitHub时的最新R07阶段：**两项研究目录修复已提交、等待独立复验；未正式结案，FINAL-CODEX和DEV28均未获自动启动授权。**
>
> 本文件是**上下文与开发规划职责恢复材料**，不是批准任何游戏内存操作、真实交易、赛季推进、脚本、合并PR、启动Codex额度或开发人格系统。

## 0. 新窗口应保持的角色定位

你是**网页GPT开发规划与独立研究审核负责人**，不是运行中的30队GM，不是采集/执行Codex，不是玩家球员或教练人格。你的责任：
- 先熟悉已有NBA2K22 PC MyLEAGUE机制、外挂架构和项目真实开发状态，按社区/攻略/官方手册研究先行；策划**有界、可验证、不会重复现有工作的开发任务**。
- 审核其他网页研究窗口的R轮次交付、Codex/Antigravity阶段结果和GitHub文档/代码：**读取原文件并作结构、语义、来源、版本、实际可执行性与范围审查**；需整改只定向整改，研究可结案不等于实机数据完备。
- 根据玩家的明确要求**准备Codex/Antigravity提示词和验收合同**，在适当时机记录报告、基线/记忆、工程缺口；不擅自执行尚未经玩家批准的代码/游戏修改。
- 研究材料**不是人格程序**。不要由“哪些字段可用”擅自设计Coach/Player/Media Agent的权重阈值、状态机、人物行为规则、虚构剧情或同意/拒绝协议；这些都属于未来另外立项的模型任务。

## 1. 项目基础与业务世界线

- GitHub：`https://github.com/chris2gao/nba2k22-gm-engine`。
- NBA2K22 PC本世代离线MyLEAGUE，**2021–22赛季开局**，30支球队。**1984、1985、……、2020年历史选秀按先后顺序一届一届轮回**，2020之后返回1984；只有当玩家确认上一届选秀**实际完成**才推进外部轮回，不能仅随日历年份自动变化。资料里的NBA2K23次世代Eras是机制参考，**不是**本世界原生时代模式。
- 历史重力：2022–2025游戏年以现实对应赛季/争冠球队作为经审核参考，从游戏年2026起切换按“1984乔丹首选起四年后的历史时间线”作纪元类比。**只提供模拟历史线的候选修正**，不保证历史冠军/剧情，也不允许自动修改球员能力；任何特殊历史修正逐项经玩家批准。MC成长故事暂缓。
- 选秀权政策`config/gameplay_policy.json`：`PLAYER_RULES_20261021_V4`。用户已取消外挂世界的**只交易未来三届**人为限制（`maximum_future_drafts=null`），不是改1984–2020轮回。已知原生读取可覆盖**连续5届、共300条简单双轮资产记录**，并不构成固定5年交易上限。资产按年份、轮次、原持有球队、当前持有球队身份；**无保护/顺位交换**。当前代码旧`+3`仍有执行阻断，见§7。
- 默认**游戏自己决定自然成长**：普通经营不可编辑Ability/Potential/Badge直接增强；获明确批准的特定历史线例外另议。现有`Intangibles`用于轮换OVR偏置的狭窄已批准工作口径有独立范围，不等于开放其它属性或球员徽章。球员`Potential`对GM输入有遮蔽，不代表游戏原始潜力被改。游戏AI会覆盖轮换具体分钟，**不再开发精确分钟锁定**；可从BenchDepth/阵容/教练设置中合法尝试调整。
- 普通交易由双方同意后按已有外挂合法业务流程安排，不依赖2K交易难度；**真实写入**总需玩家批准具体方案版本，符合存档身份、preflight/CAS、读回、重载等已验收路径；不能把GM提案或Agent意愿当作授权。

## 2. 玩家正式确定的六个独立模型阶段

游戏每一轮外挂循环（通常新赛季开始、常规每月、交易截止日前一天、季后赛每轮、休赛期）：
1. **采集模型**：获取当前NBA2K22真实数据源，标存档/批次/时间/原生来源。
2. **数据分析模型**：原始数据加工和高阶指标，提供后续角色所需动态事实。
3. **各队教练模型**：独立执教，分析阵容、对手、战术/轮换，向GM提出要求；**独立教练人格尚未开发**。
4. **全部或部分球员模型**：经历职业/生活并自主决定要求、建议、倾向、训练等；**独立球员人格尚未开发**。
5. **各队GM模型**：目前已有主要决策人格，负责经营球队、球队文化和赢球哲学，综合教练/球员要求独立决定。
6. **汇总与执行模型**：收集可落地行动，**玩家真实逐案批准**后进行游戏更新与读回，不代替前5步制定行为策略。

未来可能增加媒体等模型，但**媒体不是已确定六阶段中的强制第七步**。希望角色自由地“玩”、竞争、犯错、修正和产生涌现，不是让研究GPT替所有角色编写一个所谓最优权重程序。

**项目级权威文档**：[开发意图和职责边界](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)，[R研究/人格边界](../game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md)。

## 3. 严格分清三个开发层次

### 3.1 DEV29（R01–R07）：研究游戏原材料，不开发角色人格
- 网页GPT多轮主动搜索玩家社区（Operation Sports、Reddit等）、攻略、官方手册、图文或视频；NBA2K20–23本/次世代均可用于理解**机制**，但NBA2K22 PC本世代的真实菜单、枚举、内存布局、作用与持久性须独立认证。
- 调查**能看到的数据、动态变化与历史留存、所有可设置项及合法值域、怎么玩、不同设置联动及其实际效果**。截图必要时来源索引分批记录，第三方受版权保护图片不批量搬进GitHub。
- 给未来Coach/Player/GM/Media提供**材料入口**，不能开发人格决策树、签约权重、谈判引擎、新闻角色或流程调度。
- 研究与真实技术能力是七个分离的成熟度：社区/官方研究→目标PC22 UI→静态原生Registry/locator→当前存档真实读回→有效采集发布→可被模型查询→经用户审批执行和保存回验。每项保持明确独立等级、UNKNOWN、来源身份，不把“静态偏移存在”写成“当前可读/可执行”。

### 3.2 DEV28：完整I/O透明化与技术闭环（仍待独立授权）
- 资料先来自DEV29，技术对照由**FINAL-CODEX**只读/有限静态工程清点；再授权DEV28的真实缺口开发。
- 所有有用的比赛和人员**动态事实**完整采集、可追踪、可按团队/人/比赛/阶段查询；特别是**原来“全量采集”竟缺逐场Game Logs、双边Box、真实高阶数据、Shot和GameID**，这是一类P0失败，不能只靠赛季总计拼造逐场。已公开机制不等于当前内存有原生获取路径。
- 全部可选静态控制（教练默认19、单防18、球队68格战术书、球员4个PlayTypes/Initiator及99倾向槽、训练6+5、Gameplay与世界设置、真实合同/Staff/财务/球探候选等）需要“参数身份、当前实际值、完整可选项/枚举与篮球意义、原生生效范围、执行资格、回读与Save”。已登记的数量是**历史研究/技术概况**，不能不核对现行原生源就说全部已采或可改。
- 使用已有M0、Registry、`DEV14`、SQLite和现有执行器，无需重做另一套审批/交易系统；按D28-0审计、D28-1 Playbook原生映射、D28-2静态全选项、D28-3 DEV24真实动态来源、D28-4经批准执行闭环、D28-5 30队验证等有界包安排。**不开发Coach/Player人格**。
- 原始状态/SQLite/网站/模型查询、游戏真实Save各自具有身份与持久证据；采集发布和GitHub上传成功不等于游戏保存成功。

### 3.3 未来独立人格与各角色运行系统
将来由其它**独立、需玩家批准的项目**选择模型提示、长期记忆、目标/意愿形成、模型间沟通与真正的选择/拒绝机制。R04八个场景、`Loyalty/Financial Security/Play for Win`只是球员原生资料、人格可利用外延和素材示例；**不能将“忠诚>80就续约”这样的程序冒充人格**。未来角色状态优先独立SQLite；如想牺牲原生闲置字段存外挂角色状态，需先证原生副作用、兼容、回滚并另批，不能抢占影响比赛/合同的真实字段。

## 4. 技术数据和工作分工现状

- 数据结构：SQLite `league_state.sqlite`（球队/阵容/合同/员工/快照等）、`player_pool.sqlite`（原始球员/选秀）、JSON发布入口`latest.json`（`data_updated_at/uploaded_at/game_date`）与`published/saves/<save_id>/latest.json`一类存档定位；务必核实**最新当前真正有权限的save_id/save_instance_id/generation_id、batch_id**，不要跨档跨批拼信息。
- **Codex**：源码、数据采集/初始化/更新、确定性计算、GitHub数据库上传、经玩家批准的具体执行；不能用大范围免费发散搜攻略占前期DEV29工作，也不要在研究收尾阶段自行写游戏。用户触发、Codex任务包完成即关闭。
- **Antigravity**：当前运行NBA2K22的本地菜单/内存/地址、真实选项与保存效果，按专项调查或已批准范围读写。玩家可提供成批截图，但优先社区研究减少用户成本。
- **网页开发规划GPT（本快照恢复的角色）**：系统边界、各R交付独立审核、开发需求拆分和提示词、现有源码状态交叉审查、规范/基线文件记忆维护。
- **数据分析GPT**：完整逐场/球队动态事实需求、指标有效性/可重复计算、按批次分析成果；无真实Game Log时标证据不足，不造指标。
- **GM GPT**：基于真实篮球体系、球队文化、教练与球员需要、市场约束做经营选择；BPTI/M3知识是参考，不是固定最优决策公式。一个赛季可有独立GM窗口；规划与GM职责不要混为一谈。
- PR #12：BPTI Package C/B4–B6/M3/F1–F4已在GitHub核实**CLOSED/MERGED**，`merge_commit=86c0d944f4dbdf2783fbc217e5df6c091296c17a`。它修复演化版本一致性、save实例连续性、市场与native HOLD解耦、执行候选必须实际可行；**不证明真实30队都已评估、签约执行或赛场读回。**
- 已有教练、战术、受控交易部分原生技术；签约器`src/approved_signing_executor.py`仍`approved_signing_v1_unvalidated`，`SIGNING_LAYOUT_VALIDATED=False`、`SIGNING_EXECUTION_ENABLED=False`，**不能写入**。普通获批交易的具体能力边界、战术绑定/Book槽、签约、员工雇聘、选秀权4/5届执行不能彼此借用验证结论。

## 5. DEV29 R系列历程与当前最新恢复点

| 轮次 | 已研究游戏原料 | 已知完成情况与边界 |
|---|---|---|
| R01 | 赛程、真实逐场比赛/Box/Advanced/Shot/历史留存 | 研究结案；PC22原版完整Stats菜单及真实Game Logs未完成技术认证 |
| R02 | 教练、12类战术/Playbook/ACE、个人防守、战术书 | 研究结案；部分本机PlayType枚举/2D战术语义仍需技术映射 |
| R03 | 团队/个人训练、健康、疲劳、伤病、自然成长 | 研究结案；当前角色真实健康数据未全采 |
| R04 | 球员身份/属性/徽章/99倾向/职业偏好/耐久与双语义 | 研究结案；109侧表=72静态Profile+37未映射研究候选，**不是全部字段或当前值已采**；8类Agent互动故事只是材料需求示例 |
| R05 | 财务/合同/交易/选秀权/Staff/球探/Draft、规则V4 | 研究结案；54异质数据、63研究操作，不等于54当前实时读数/63可执行按钮 |
| R06 | 3D vs Sim、阶段/保存、纪元/荣誉/媒体、跨域联动 | 已独立验收研究结案；R06-D **26关系、20证据缺口、79/79源目录引用有效**；不是26条引擎公式 |
| **R07（实时截至快照）** | **全R知识能力与证据成熟度矩阵** | **40功能族、86源锚点、694异质研究记录（7卷100+100+100+100+100+100+94），主体独立审核通过；两项机读修复已提交但正等待独立复验。尚未正式结案。** |

**必须保留的精确状态**：`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`。  
首次独立审核：[R07独立审核](../development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)；定向提交：[R07修复回执](../development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)。修复：
- A：`R07.0007/K02.SHOT_ZONES`与`R07.0010/K02.PER36`属于研究者从R01攻略生成的**检索主题别名**，分别有真实§4/§3章节锚点，不是原始JSON机器主键。
- B：F21/F22/F23/F26/F27/F32/F39/F40八族`model_query_api_status`原混入写入/权限/批次真实性和政策信息，已改为**真正查询层**，原执行限制另存warning/precondition，不升级旧实机执行能力。
- 独立初审已经验证：694/694唯一、682/682源JSON记录身份匹配、86/86功能族源锚点、20/20继承R06缺口。**需要另一审核模型对修复项及不变量做简短复验，出具正式结论后才能决定关闭DEV29。**

**当前研究主入口**：[PROGRESS](../game_mechanics/PROGRESS.md)，[R07指南](../game_mechanics/guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)，[40组矩阵](../game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)，[694索引入口](../game_mechanics/catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)（**本入口是七卷路径表，不包含单一巨型`items[]`，请逐卷fetch**），[R07→DEV28交接](../game_mechanics/R07_TO_DEV28_EVIDENCE_HANDOFF.md)。

## 6. 后续路线与建议优先顺序（不是自动开发授权）

### 最近一步：R07两项修复独立复验与DEV29正式结案
- 新开发规划GPT可**自己独立复核**或审核另一个模型的独立复验报告，但不要把提交者的“自检PASS”当独立审核。
- 验证两个人工R01索引的真实性、八项查询字段与警告拆分、694/40/86/20总量不变、十类R06B无直证奖项及七项R06C无来源仍UNKNOWN、不升级成熟度。
- 通过则形成R07正式审查与DEV29研究结案归档；**是否启动FINAL-CODEX仍需玩家另行同意**。

### 再后：FINAL-CODEX（小型、有边界、只读静态覆盖对账）
- 对照所有R系列**游戏需求全集**与`config/state_io_native/*.json`、`src/gm_state_io/registry.py`、现有`src/gm_data_access/query.py`、DEV14/Approved Trade/签约器、现存SQLite/manifest/`latest.json`、Playbook及球员信息目录。
- 输出按每个功能的**原生资料已知／UI认证／Registry登记／当前真实读回／正式入库发布／GM/Coach/Player将来可查询／已获批有界写入和Save回验**的差距表，明确优先权重与工程单元。
- 只核查**当前已存在**的能力，不得通过把40族/694行视作API数量，不能把查询与写入混在一个值里。Codex不要大规模再搜网、重复研究或擅自修复执行器。

### 其后：DEV28 D28-0～D28-5分包实施
- D28-0：按照真实能力盘点、现有证据完整性与可用性。
- D28-1：战术名称、真实PlayType、2D动画、团队独立68-slot Book、共享CRC映射、换帅时本队书技术归位等，PC22原生证据/读回另证。
- D28-2：Coach/球员/训练/全局设置所有合法值域/菜单可解释性、受控设置读回。
- D28-3：真实逐场Box/Game Logs/Shot及高级分析数据来源（DEV24）、GameID和3D/Sim模式区分、训练/伤病、阶段时间。
- D28-4：证据→候选选择→用户批准→DEV14/既有执行器→游戏读回/真实保存完整闭环。
- D28-5：30队验证、跨档隔离、端到端来源/失败/HOLD状态和可查询性验收。
- **角色系统以后独立开展**：Coach人格、Player人格、Media可选、模型间互动/记忆/谈判、模型调度，只有用户届时另立项才研究/开发，不能“DEV28顺便补”。
- 另一个**独立小维护任务**：选秀权V4 3年规则历史守卫未同步；无论是否与R07/DEV28并行都需用户明确触发Codex和限定验收边界。

## 7. 必须牢记的技术/来源陷阱

1. **V4 Pick规则与代码不一致**：`src/draft_assets.py::trade_window()`与`capture_assets()`的`tradeable_draft_years`、`src/gm_core/calculations.py::draft_pick_window()`、`src/gm_core/trades.py`的`DRAFT_PICK_OUTSIDE_THREE_YEAR_WINDOW`、`src/approved_trade_executor.py`仍旧三年拒绝。未来应以**实际已读取、唯一资产身份/当前归属/批准范围/执行器支持**校验，不机械把`+3`换`+5`新硬限。详见[R05审核](../development_reviews/DEV29_R05_INDEPENDENT_REVIEW_20261021.md)。
2. **没有Game Logs不能假装高级统计够用**。原始逐场、投篮与回合信息未取得，就明确`INSUFFICIENT_EVIDENCE/NOT_OBSERVED`。先找游戏机制/球员社区资料，再决定要读哪些字段；不再从“内存有多少地址”定义采集全集。
3. **跨版本、跨平台、跨模式必须分级**。NBA2K23次世代Eras和NBA2K22 PC MyLEAGUE不是同一实现；旧2K帖子描述不等于PC22本机字段；2K22模组社交媒体文本不证明原生新闻写入接口。
4. **实体身份与原生语义**：战术`'95 FIST 15 SIDE`真实游戏名已在静态池定位CRC`0x79215B33`，用户确认挡拆类型、FIST是挡拆动作、15为1号发起与5号配合、SIDE为侧路变体；但原生PlayType枚举仍待证，名字不能代替枚举。Coach `RunPlayTendency`与Player `PLAY_DISCIPLINE_TENDENCY`（`0x4A1`）会成为联动研究对象，未证确切因果概率。**球队拥有本队Playbook容器，多个球队可共享战术CRC，但本队槽位修改不得改别队书**。
5. **原生AI与外挂分工**：真实3D/SimCast/日历Sim对应数据和Gameplay vs Sim Slider消费者不同，Normalize Stats/Minutes应独立；两类引擎不可把同名“Pace/Help/Shot”当同一参数。
6. **存档持久性不是SQLite上传**：`GameDate`、`Save/Save as/Autosave/Reload`、DEV14管理的`save_id/save_instance_id/generation_id`、GitHub`latest.json`与本地SQLite各有权威，缺实机读回即UNKNOWN。
7. **GM知识不等于强制策略**：BPTI的篮球文化、队伍哲学、十个体系研究卡、M3/A/B与M4演化机制可作为模型依据；**不能因为决策逻辑看起来合理就剥夺GM或未来球员/教练自主选择**。角色目前是否实现仍按状态确认。
8. **真实权限优先**：任何原生游戏修改要人类玩家批准；不能经由文档、AI同意、合成测试通过而绕过。需要拆分具体对象/来源、原值、合法值域、写后读回与持久性验证。历史线例外及已批准Intangibles窄例外不可泛化。
9. **历史新闻/奖项待证**：R06-B十类奖项直接来源仍空、R06-C七项无直接来源；真实游戏冠军/奖项/纪录与现实2022冠军、外部历史重力各自保留来源，玩家媒体预测不是历史真值。

## 8. 长期恢复必读文档（按顺序）

1. [项目级开发意图/六阶段](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)、[`AGENTS.md`](../../AGENTS.md)、[世界线规则与审批](../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)。
2. [本开发规划窗口快照](DEV_PLANNING_WINDOW_HANDOFF_20261021_V1.md) + [开发规划当前记忆](../../web_gm/memory/DEVELOPMENT_CURRENT.md) + [实时共享状态](../34_BASELINE_CURRENT_STATE.md)。
3. [DEV29 PROGRESS第一节](../game_mechanics/PROGRESS.md)、[研究知识库](../game_mechanics/README.md)及[游戏资料索引](../game_mechanics/SOURCES.md)。
4. [R07独立审核](../development_reviews/DEV29_R07_INDEPENDENT_REVIEW_20261021.md)、[定向修复回执](../development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)、[R07能力矩阵/索引](../game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)、[R07→DEV28交接](../game_mechanics/R07_TO_DEV28_EVIDENCE_HANDOFF.md)。
5. [DEV28透明化总规划](../development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)、[DEV29 V3](../development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)。
6. [R05验收与选秀权代码差距](../development_reviews/DEV29_R05_INDEPENDENT_REVIEW_20261021.md)、[R06独立验收](../development_reviews/DEV29_R06_INDEPENDENT_ACCEPTANCE_20261021.md)、[签约执行未验说明](../38_APPROVED_SIGNING_EXECUTION.md)。

## 9. 可复制到新窗口的最短恢复口令

> 你现在接替NBA2K22 GM Engine的**网页GPT开发规划与独立审核基线窗口**，GitHub仓库`chris2gao/nba2k22-gm-engine`。旧窗口达到上下文上限。本任务不是30队GM，也不是直接运行Codex或游戏。
>
> **先按顺序读取**`docs/development_snapshots/DEV_PLANNING_WINDOW_HANDOFF_20261021_V1.md`、`docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md`、`docs/game_mechanics/PROGRESS.md`前几节、`docs/34_BASELINE_CURRENT_STATE.md`、`web_gm/memory/DEVELOPMENT_CURRENT.md`、R07独立审核/定向修复报告、DEV28总计划。
>
> 明确六模型循环：采集→数据分析→独立教练（未开发）→独立球员（未开发）→GM→经真实玩家批准的汇总执行。**R系列只研究游戏原材料；DEV28建设透明I/O；未来人格系统另外立项，不能用固定阈值程序冒充人格。**
>
> 截至快照最近GitHub状态为`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`，即R07主体质量认可、694项/40功能族/86锚点/20缺口通过初审、两项修复已提交，**等待独立简短复验**；无需重做R01–R06。先实时核实状态，若还未正式复验则优先独立审核；若已验收则准备将来玩家单独批准的**FINAL-CODEX只读当前工程覆盖对账**和**DEV28 D28-0～D28-5**实施规划。选秀权V4政策已取消人为3年上限但旧+3执行器仍阻断第4/5年，是另一个最小Codex任务。不要把研究候选说成当前已采或已执行。
>
> 恢复后先输出：①最新真实状态；②R07独立复验/DEV29结案是否完成；③下一开发规划任务与严格边界；④后续FINAL-CODEX、DEV28、角色系统的分阶段路线。**不得未授权执行Codex、原生写入、赛季推进、签约、人格系统开发。**


## 10. R系列之后的长期扩展任务池（保留规划，不等于批准开发）

> 用户特别要求**这个窗口结束后仍由新网页GPT继续做开发规划与独立审核**，而不因DEV29 R系列完成就停止。以下是长期待议范围，**不是已获批准的开发排序、实施命令或既定人格设计**。每个方向开始前须检查最新GitHub状态、现有代码/来源和用户当次意图；需求/权限仍按项目宗旨。

| 扩展方向 | 为什么保留 | 现在不能越过的边界 | 与已有工程的衔接 |
|---|---|---|---|
| **DEV29结案→FINAL-CODEX→DEV28** | R07把机制研究整理成40功能族/694来源索引；下一步要由真实工程盘点、实现“数据输入输出完全透明” | R07修复仍待**独立复验**，FINAL-CODEX和DEV28均不能由本快照自动启动 | [R07交接](../game_mechanics/R07_TO_DEV28_EVIDENCE_HANDOFF.md)、[DEV28](../development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md) |
| **P0真实动态比赛和发展事件来源（DEV24相关）** | 采集项目曾缺逐场Box/Game Log/Shot、GameID、3D或Sim模式、伤病/训练更新，使数据分析和教练复盘无法真正驱动决策 | 先源证和身份再推导数据；没有事件级真值不能伪造高阶/阵容因果 | DEV28 D28-3、R06D D06-G01..G05 |
| **原生静态全控制/Playbook生命周期** | 教练19项、个人防守18项、球队68槽战术书、PlayType与战术CRC、球员倾向、训练和世界设置可能成为未来独立模型的工具 | 共享战术≠共享球队书；原生CRC不等于类型枚举；需本机菜单/读回，未来角色个性另做 | DEV28 D28-1/D28-2、DEV12/13/16、R02/R04知识 |
| **V4未来选秀权窄修复** | 外挂政策不再人为固定3届，当前已知读源覆盖5届/300枚，但旧程序仍存在`+3`拒绝 | 仅更正旧业务守卫和发布口径、保证资产确实存在/当前归属/可执行，**不得把+3改+5形成新固定世界规则**；Codex需玩家单独触发 | R05审核G04、`draft_assets.py`/`gm_core/*`/approved trade executor |
| **休赛期合同、财务和独立自由市场** | 球队薪资空间、合同选择、竞价/拒绝和球员真实职业生涯，会需要完整工资帽/合同来源和后续模型能力 | 业务谈判与执行分离；已写入但未经实机验收的签约执行器保持关闭；不得把固定报价权重冒充球员人格 | DEV04/历史offseason设计、R05、[签约器说明](../38_APPROVED_SIGNING_EXECUTION.md) |
| **独立Coach人格及执教模型** | 六阶段第3步尚未实现；未来每队教练有自主看法、轮换/训练/战术及向GM提出交易/人员要求 | 这里仅保存目标和游戏可用资料；具体如何形成想法/选择/谈判必须届时另立项，不能靠阈值规则在R系列实现 | R02/R03、DEV28 Coach读写能力、M3/BPTI对接 |
| **独立Player人格和生涯模型** | 六阶段第4步尚未实现；球员生活、个体目标、受伤/训练、打法、续约/择队等为未来重要游戏扩展 | R04字段/八个场景只是信息和接口原料，**不是人格算法**；外部长期角色记忆优先另存，不默认篡用真实2K原生字段；普通Ability/Potential/Badge不允许直接改 | R04原生109侧表＋其余倾向/徽章目录、DEV28个人数据接口 |
| **GM篮球文化/策略自主与M3/M4迭代** | 已有GM是目前主要的自主经营角色，应能基于比赛、球队哲学、球员/教练建议经营，而非只输出排行榜或最优值 | BPTI十体系/球队文化是参考知识，不能替全联盟人格下死规定；F1–F4等已有代码先查实际主线，V4是否启用另核实 | PR #12已合并、M3/M4/BPTI、Analytics |
| **可选媒体/叙事世界** | 真实冠军、奖项、历史数据与新闻/声誉可能支持未来媒体参与和联盟沉浸 | 当前六阶段**没有强制第七媒体阶段**，2K22媒体模组文本不等于原版媒体Agent或已证写接口 | R06-B、R06-D、R07事实/来源权威等级 |
| **历史纪元模拟/重力与MC可选扩展** | 2022–2025现实历史参照、2026年起按历史选秀轮回推演纪元；另有此前提出的MC人物成长、主宰/持球慢动作等技术问题 | 不为历史复刻固定NBA冠军或擅改球员；历史重力修改**逐项获玩家批准**；MC不是当前主线，单独排期 | `gameplay_policy.json`世界线、DEV历史专题、MC技术调查 |

### 后续开发规划应怎样决策

当用户说“R系列结束，可以扩展”时，**不要自动同时启动全部扩展**。先验证是否已正式通过R07独立复验，然后和用户确定是否进入**FINAL-CODEX只读能力覆盖盘点**。以该盘点识别实际可用数据和执行器，再按各阶段价值/数据依赖/安全与PC22验证成本提出有界开发计划，由用户逐项授权。之后的角色人格、经济系统、媒体、历史线才各自另立专项；人格如何实现不由本快照预设。

**给下一开发规划窗口的长期目标**：DEV29不是项目终点。项目要最终形成一个可让独立Coach、Player、GM等“自主玩球”的世界，技术底层对游戏真实事实和可设置能力足够完整，运行中每个模型都能依据自己的反馈自由决定；网页GPT开发规划窗口持续负责研究成果审核、开发路线拆分、跨模型需求协调、向Codex/Antigravity发布经用户认可的边界清晰任务、审核实际反馈并维护GitHub长期记忆。
