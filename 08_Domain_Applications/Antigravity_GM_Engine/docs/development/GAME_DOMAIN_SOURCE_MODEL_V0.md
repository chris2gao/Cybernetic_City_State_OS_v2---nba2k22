# GAME_DOMAIN_SOURCE_MODEL_V0 — 游戏原始数据建模 V0

**任务** WORLD-SOURCE-MODEL-SEED-01 · **状态** 研究候选，未实机验收 · **基准** `master@407e2134bd2f595477099b2c6e3484c818059fd9` · **参考架构** `task/world-data-arch-01@734188ab378974cf1d4426e67c675de561aac692`，仍为独立审核未闭合的候选。

## 1. 设计目标、原则与证据边界

优先建设两项基础：①尽可能完整发现、无损保存、自动化采集 NBA2K22 PC 离线 MyLEAGUE 的真实游戏数据；②逐对象登记可操作字段，未来经 Human 批准建立统一受控执行框架。GM/Coach/Player 的分析、人格和统计派生按需后置，不能把旧月度累计表当未来设计上限。**每个存档是完全独立、跨赛季连续的世界**，无分叉/合并/跨档动态历史与角色记忆继承；历史选秀模板仅共享静态来源，不共享游戏球员的实际职业生涯。

**L0** 原生结构/字节/UI观察、时间、来源、版本和受限证据；**L1** 已认证身份、口径和原生来源的游戏事实（含游戏自算 SeasonTotals、生涯历史和游戏高级 UI 显示值）；**L2** 外挂公式/自定义聚合/模型评价，未来有实际需求才开发。L0/L1 是食材，L2 不能冒充游戏原生事实。一次 Box 再采集不代表新比赛；游戏累计不等于当前已采逐场之和；部分覆盖不自动算 CONFLICT。

## 2. 七大业务领域：候选逻辑数据族（不是物理表）

| 领域 | 建模接收族 | UI 与已知 Native 来源 | 生命周期 |
|---|---|---|---|
| Player | PlayerIdentity、Bio、Attributes、Durability、Tendencies、Badges、Appearance、Vitals、Career、Training、Health | 球员卡各页/球队名单，PLAYER、R04字段矩阵 | 个人资料相对静态；能力、徽章、球龄、健康动态 |
| Game | GameIdentity、Calendar、PlayerBox、TeamBox、NativeSeasonTotals、NativeAdvancedDisplay、ShotChart | Game Logs、比赛 Box、联盟排行，SEASON/StatBank/Slot24/26 | 比赛事件、统计观察、游戏累计分离 |
| Team | FranchiseIdentity、TeamSeason、RosterMembership、TeamStats、TeamFinance | 球队名单/薪资/战绩、TEAM/TEAM_STATS、R05 | 球队长期身份，赛季名单与财务按时间 |
| CoachStaff | StaffIdentity、Employment、CoachSettings、Playbook、Training、GamePlan | 员工、教练、训练 UI，STAFF/coach Registry | 训练与设置可变，执教岗位有生效区间 |
| World | WorldIdentity、TechnicalBinding、SeasonCycle、Phase、GameSettings、CaptureBatch | MyLEAGUE 设置/规则/赛季阶段、DEV14、R06 | 存档连续且隔离；generation 只是技术代际 |
| Operations | Contract、ContractSeason、DraftAsset、PickOwnership、Trade、Signing、FreeAgency | 交易/选秀/工资/合同、R05研究 | 资产和交易事件须真实游戏证据 |
| History | CareerHistory、RecordBook、Awards、FranchiseHistory、LeagueHistory | 生涯页、奖项、纪录及Slot39候选 | 游戏中发生的事实与内置真实NBA历史分开 |

**UI 页面是发现导航，不是数据表。** 同一球员在球员卡和球队名单显示不同字段子集，来源可能分别是 PLAYER/TEAM/Contract/SeasonTotals；用同一个 player_uid 归属，不依赖 UI 文本拼接来认定是同一数值。游戏日期、采集时间、实际显示页面和游戏模式都要独立记载。

## 3. 研究目录的真实覆盖

机器目录 `GAME_UI_FIELD_CATALOG_V0.json` 当前 **888 条来源索引**，领域分布：Player 422、Operations 45、Game 52、Team 49、History 31、CoachStaff 47、World 242。它包含研究字段、Native Registry、跨版本菜单、外部 UI 导出标签、未知结构和显示候选，**不代表 888 个已确认原生字段或游戏 UI 覆盖率**。新增本地进程读取、自动全量采集验证均为 0。

R04 球员原字段 109 项与已注册的 55 属性/16耐久、17合同子项是证据来源；99 个原生倾向字节含 48 命名与 51 未知，而第三方 HTML 99 标签必须独立登记，禁止按下标强配。80 Gameplay Badge 和 20 Personality 研究标签并非 PC22 Native Badge ID 证据。R05/R06 的财务、员工、市场、世界设置有跨版本/静态 Profile 候选，不能因名称或默认值存在就认定当前游戏实际值。AG01C/01D 75 槽、SEASON、GameID/PlayerID、生涯索引和 StatBank 均须独立原生验收；StatBank 的容量不等于有效记录数。

## 4. ARCH-01 全部 44 个概念实体到 V0 的映射

概念身份与时间不被本任务重写，实体≠物理表；FutureAnalysisOnly 和 AI 角色只是后续合同。

| ARCH-01 | V0领域 | 逻辑接收族 |
|---|---|---|
| `GameSave` | World | WorldIdentity |
| `TechnicalBinding` | World | TechnicalBinding |
| `Season` | World | SeasonCycle |
| `SeasonPhase` | World | SeasonPhase |
| `GameCalendar` | Game | GameCalendar |
| `CaptureBatch` | World | CaptureBatch |
| `Franchise` | Team | FranchiseIdentity |
| `TeamSeason` | Team | TeamSeason |
| `PlayerIncarnation` | Player | PlayerIdentity |
| `DraftTemplate` | Player | DraftTemplate |
| `Staff` | CoachStaff | StaffIdentity |
| `RosterMembership` | Team | RosterMembership |
| `Contract` | Operations | Contract |
| `ContractSeason` | Operations | ContractSeason |
| `WaivedSalary` | Operations | WaivedSalary |
| `DraftPick` | Operations | DraftAsset |
| `PickOwnership` | Operations | PickOwnership |
| `TeamFinance` | Team | TeamFinance |
| `TransactionEvent` | Operations | Transaction |
| `StaffEmployment` | CoachStaff | StaffEmployment |
| `Game` | Game | Game |
| `TeamGameResult` | Game | TeamGameResult |
| `PlayerGameStatline` | Game | PlayerGameStatline |
| `BoxScore` | Game | NativeBox |
| `SeasonTotals` | Game | NativeSeasonTotals |
| `CareerHistory` | History | CareerHistory |
| `RecordBook` | History | Records |
| `Award` | History | Awards |
| `DerivedStatistic` | Game | FutureAnalysisOnly |
| `StateObservation` | Player | TypedStateObservation |
| `Playbook` | CoachStaff | Playbook |
| `TacticalConfiguration` | CoachStaff | TacticalState |
| `NativeObject` | World | NativeObject |
| `NativeIdentityMapping` | World | NativeIdentityEvidence |
| `CaptureObservation` | World | CaptureObservation |
| `DecoderVersion` | World | DecoderVersion |
| `SourceManifest` | World | CaptureManifest |
| `DataQualityReport` | World | QualityReport |
| `Actor` | World | FutureAgentActor |
| `AgentObservation` | World | FutureAgentObservation |
| `AgentDecision` | World | FutureAgentDecision |
| `Approval` | World | HumanApproval |
| `ExecutionReceipt` | World | ExecutionReceipt |
| `GameReadback` | World | GameReadback |

## 5. 页面/字段扩展策略

每个来源保持：field_id、entity、field_family、ui_pages、native object/offset/Getter、原始成熟度、值类型/单位、数据生命周期、source_refs、unknowns、sensitivity 与下轮 next_probe。页面已观察与研究猜测分别登记，字段发现须查字节邻域、合法指针邻域、UI相邻字段和多对象对照。新的词条先看能否属于现有数据族；不为每个 UI 标签创建冗余实体。初始模型允许未来增加有据原生字段，不因已知数组大小冻结生涯年份或游戏字段数量。

## 6. 下一步

Flash R00 先实机核对版本、ROSTERDATA/SEASON、历史75槽与 UI 页面地图；R01 优先 Player age 输入、OVR、徽章编码、51 未知倾向；R02 逐场 Box、GameID/PlayerID、StatBank、原生 SeasonTotals 与跨季历史；Action 先读、再研究能否写。Codex 独立验收 Decoder、身份和范围，不自动批准任意批量修改。
