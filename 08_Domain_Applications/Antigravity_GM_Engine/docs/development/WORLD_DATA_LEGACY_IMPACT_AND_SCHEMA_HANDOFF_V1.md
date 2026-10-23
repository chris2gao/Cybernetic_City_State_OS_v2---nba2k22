# WORLD-DATA-ARCH-01 旧系统影响与 WORLD-DATA-SCHEMA-01 交接 V1

状态：CANDIDATE_PENDING_INDEPENDENT_REVIEW；2026-10-22。源码基准为 407e2134bd2f595477099b2c6e3484c818059fd9。本任务只读源码和 schema 文本，未打开生产 SQLite，未运行游戏或 AG 历史测试。

Human 审核更新（2026-10-22）：本轮明确结论为“这次算审核通过”。详情及后续实际验证结果以 OS run 的 completion_pointer.json / human_review.md 为准；独立模型审核尚未进行，候选未合入 master。

## 1. 旧结构到新语义的映射

[旧 schema](../../database/schema.sql)提供设计缺口证据，不证明某张表当前有真实记录。保留旧来源库和封存文件，只在获准迁移时映射。未知旧字段携带原值、来源/口径及未知状态，不由列名或默认值提升可信度。

| 旧资产/表 | 新模型与可迁移字段 | 结构性缺口 / 处置 |
|---|---|---|
| league_state / player_pool 两文件 | 有证事实、快照、source manifest；逐档登记来源 | 文件数不是概念约束；物理切分由 SCHEMA-01 比较。未经绑定的 legacy-shared 不自动归档入世界 |
| teams / coaches | Franchise、TeamSeason、Staff、StaffEmployment、StateObservation | 当前球队/岗位/参数混放；team_id 和名字的长期稳定性待证。保留名称为属性 |
| players | PlayerIncarnation、RosterMembership、Contract、StateObservation、NativeIdentityMapping | 当前球队、合同、能力和内存地址混合；AUTOINCREMENT player_id 不是 native ID 或跨季证明；memory_address 仅受限源定位 |
| player_source_details / staff_source_details | NativeObject、CaptureObservation、StateObservation、映射 | snapshot/team/roster_slot 或 staff_slot 只定位本批次；raw/JSON 中敏感值不能进入通用视图 |
| coaching_source_captures / coaching_team_observations / staff_pool_observations / coach_mapping_quarantine | CaptureBatch、教练状态、Staff、未解映射与质量记录 | 隔离区事实不能升级为已确认教练身份；保留采集状态和候选理由 |
| team_source_stats | SeasonTotals + DerivedStatistic | metrics_json 分字段辨别原生与 per_game 公式；不能一个 JSON 全部标 native |
| monthly_snapshots | CaptureBatch / 游戏时间标签 / SourceManifest | 月度标签不是事件身份；现实 snapshot_date 不一定是游戏日；games_in_period 默认 0 不能作为观察事实 |
| player_monthly_stats | 状态观察、ContractSeason、SeasonTotals、DerivedStatistic | 能力/合同/伤病/场均混合；player_name 不能建 FK，player_id 缺失需保留身份未解 |
| team_monthly_stats / team_monthly_evaluations | TeamFinance/SeasonTotals/教练配置 与 AI 分析分别映射 | 评估和公式不能与原生数值共用来源类型；保留公式版本/缺失输入 |
| player_growth_history | 两期 StateObservation 与派生 delta；评价归 AI | OVR 差异不证明修改原因；mentor_name 与评语不自动建立真实因果或人格记忆 |
| seasons | Season + league-rule/finance state + Award | 年份主键不足跨存档；FMVP/MVP 名称不能直接解析球员；历史选秀年属于 template reference |
| team_season_history | TeamSeason、SeasonTotals、TeamFinance、Award、AI assessment | NOT NULL 与默认数不能补造历史；必须回查数据是否观察、推导或人工填写 |
| player_season_stats | 原生累计/DerivedStatistic/状态/薪资/Award 分解 | 场均、百分比和 PER 不能当原生累计；player_id 可空而姓名非空，身份需要证明；按球队的行不能当全赛季总行重复求和 |
| staff_dynasty_history | StaffEmployment、Staff StateObservation、DerivedStatistic | 姓名关联不稳定；trainer/doctor multiplier 无来源时为候选或未知 |
| draft_asset_observations / draft_picks_ledger | DraftPick、PickOwnership、TransactionEvent | draft_year 混真实模板年/游戏季的风险；保护/互换语义未证，不能用描述文本假装完整执行能力 |
| trade_manifests | AgentDecision、Approval、ExecutionReceipt、TransactionEvent 分开 | PENDING/APPROVED 不等于已交易；EXECUTED 还需检查来源回执与回读，reasoning 属 AI |
| market_trade_block / market_trade_offers / market_free_agents | 原生市场状态与外部意向分类，关联 Actor/Decision | 报价/挂牌不证明签约成交；签约 Gate 继续关闭 |
| mentorship_dynasty_trees | 有来源的角色关系/研究或 AI 档案 | 不能把旧导师谱系名称理解为本项目世界分叉；不引入跨存档记忆，不根据关系名认定自然成长效果 |
| save_metadata / gm_control 控制表 | TechnicalBinding、CaptureBatch、Approval、Receipt | 保留原三元组及 digest/CAS/journal；稳定 world_id 需要显式迁移登记，不重标旧审批 |
| AG01C/01D 实验 SQLite 与导出器 | 原生证据来源索引和研究样本 | 不直接导入为生产；Slot44 旧 schedule 语义已被修订；旧 match_history 分支不得直接合并 |

**可淘汰的是物理组织，不是历史事实。** players 混合宽表、monthly 混合表、年份唯一 seasons、姓名式历史连接及旧快照拼接 identity 均是候选替换对象；在新模型映射、shadow 对账、回滚和独立审核完成之前不得删除旧表/库或停掉可用路径。旧审计文档和 raw 原始来源保留。此处“可淘汰”不等于本轮删除授权。

## 2. 必须复用的安全能力

- [DEV14 workspace](../../src/gm_state_io/workspace.py)：显式登记、active 三库绑定、reset 封存与 hash 验证、恢复和未解决写入阻断。reset 同时换 instance/generation，见[ADR](WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md)。
- [capture_files](../../src/gm_state_io/capture_files.py)：PREPARED journal、完整 cohort、异常恢复、来源一致性。多文件 rename 不具备跨文件原子性；不能宣传单库事务已经覆盖多库发布。
- [executor](../../src/gm_state_io/executor.py)：批准元组、before 值、掩码/CAS、持久前像、有限回滚、Readback。引入 world_id 不放松原安全三元组或变更写入范围。
- [M0 Query](../../src/gm_data_access/query.py)：固定封存批次、只读连接、受限视图/authorizer、结果限制和显式 GM_SANITIZED/potential_v1 检查。旧未脱敏批次仅受限历史审计，不能作为普通 GM 输入。
- Source Registry/Codec：复用已经有证据的字段布局与编码，不把所有研究字段一并认证。物理 API 可替换，证据范围与未知状态必须保留。

## 3. 下一任务收到什么

WORLD-DATA-SCHEMA-01 的输入必须绑定本候选最终 Git SHA、审核记录及被接受的 ADR 版本。Human 在本轮明确表示“这次算审核通过”，记录于 OS run 的 human_review.md；该 Human 审核不等于已进行另一会话的独立模型审核。当前交付仍为任务分支候选，不据此自动启动 Schema 或合并 master。

1. [领域模型](WORLD_DATA_DOMAIN_MODEL_V1.md)：七域、44 概念实体、59 二元关系与有类型多态引用、特殊基数。
2. [身份与时间 ADR](WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md)：独立世界、业务 ID、DEV14 绑定、跨季/交易/技术重建、双时间与修订。
3. [实体字典](WORLD_DATA_ENTITY_CATALOG_V1.json)：属性、scope、source_refs、unknown_fields、关系和不可变约束；不是 DDL。
4. [真实性与质量契约](WORLD_DATA_SOURCE_AND_QUALITY_CONTRACT_V1.md)：source/fixture/UI/derived/unknown 独立轴、数据缺失与隐私。
5. 本映射与 OS run 的六场景输入、检查源码、受控验证日志、实际候选 SHA 和完成指针。

Schema 应当交付：逻辑关系模型、主/外键及同世界约束、唯一和时间区间约束、来源/修订模型、角色安全视图、迁移映射、索引与容量分析、SQLite 物理候选比较。实现可通过复合外键、同档文件边界或等价可证明策略落实 world 约束；nullable 未知值不能使复合 FK 绕过必需关联。参考 [SQLite 外键要求](https://www.sqlite.org/foreignkeys.html)与[关系完整性约束说明](https://www.postgresql.org/docs/18/ddl-constraints.html)，不据此改换数据库引擎。

物理选择至少比较：同世界事实与控制在一个事务库；事实库加独立原生证据/控制库。比较跨文件一致性、敏感原始数据隔离、备份恢复、跨季增长和查询开销。SQLite 优先，文件名/数量本轮不冻结。时间范围排他性、typed polymorphic 引用和追加修订如何强制，是 Schema 必须做的具体设计，而不是留给 UI 自律。

## 4. 必须能回答的查询与反例

- 指定 world/player，从 2021–22 至 2030–31 的每季、每队出场和累计；结果注明 native/derived 与缺失期，不因同名跨档混入。
- 指定 game_uid 的当前可接受 Box，以及“在较早知识时点已知的旧版本”；重复采集不能重复计场。
- 某场实际出场球队与当时名单/合同球队的关系，冲突保留；不能连接当前 roster 代替历史。
- 原生赛季 70 分与已采单场 45 分的对账报告、来源集合和覆盖率；不生成缺失比赛。
- 同一 DraftTemplate 在不同存档的实例分别查询；静态模板不带入另一个实例的生涯或记忆。
- GM 的允许字段视图、隐藏字段/原始字节/派生敏感信息负例，以及旧绑定审批被新代际拒绝。

## 5. 未证问题清单与下游责任

| 问题 | 当前处理 | 接收任务 |
|---|---|---|
| native PlayerID/GameID 在跨季、重载、复赛中的稳定范围 | 原生键限作用域、未解 HOLD，不设猜测唯一约束 | NATIVE-ACCEPT-01 |
| StatBank 有效边界、InUse、退役/未出场、Box→PLAYER 映射 | 保存原始范围和候选证据，不假设容量=有效记录数 | NATIVE-ACCEPT-01 |
| 7-bit season_code+1900、20项 career 循环和哨兵 | 长期概念身份不受此上限限制，原码保留 UNKNOWN | NATIVE-ACCEPT-01 |
| Slot44 matchup 与 Slot10/SEASON schedule 对应 | 旧 schedule 解释不得生产化 | NATIVE-ACCEPT-01 |
| 初始 game-save 身份及 reset 后同档证明 | 用明确登记/同档证据，不能仅用 save_id | SCHEMA-01 合同；INGEST-01 后继实现 |
| retired 玩家、Staff、历史 Awards/RecordBook 的持久来源 | 区分世界事实与内置真实历史；未知保留 | COVERAGE-01 / NATIVE-ACCEPT-01 |
| 同档回退的有效历史边界 | 单一当前有效历史，旧断言保留审计；边界未知 HOLD | SCHEMA-01 修订合同，迁移/实机另批 |
| 物理分库、事务、索引、隐私投影、旧库 dry-run | 仅模型要求，未决定生产文件布局 | WORLD-DATA-SCHEMA-01 |
| 新人格和真正角色自主性 | 仅事实/权限与 AI 记录接口 | WORLD-ACTOR-DATA-01 之后另立项 |

Schema 可设计未知字段的显式状态与可选引用，但不能将未证关系强制 NOT NULL 后以假值填齐。INGEST 的实际发布仍依赖 NATIVE-ACCEPT 和原型通过。ARCH 交付不启动后继任务。

## 6. 验收追踪与审核入口

| Human 验收项 | 对应证据 |
|---|---|
| 1 完整实体/基数 | 领域模型、实体字典；CATALOG_RELATIONS 检查 |
| 2 独立存档无分叉 | ADR 1–3；S1/S6；字典禁止世界亲缘字段 |
| 3 连续生涯 | ADR 4–6；S2 的交易/赛季关系 |
| 4 原生/业务 ID scope | ADR 2/4/7；字典 identity 与 source registry |
| 5 五类事实/时间 | 质量契约 1–4；ADR 5 |
| 6 六反例 | OS run scenario_inputs.json 与 verify_architecture.py SIX_SCENARIOS 实际日志 |
| 7 DEV14 理解 | ADR 3 与源码函数；不修改现行实现 |
| 8 迁移能力/可替换旧结构 | 本文 1–3 |
| 9 不升级研究 | 所有新文档候选标签、质量契约样本边界 |
| 10 Schema 输入/未知 | 本文 3–5 |
| 11 JSON/引用/ER/task/scope | CATALOG_RELATIONS、LINKS_AND_SCOPE、OS_CLOSURE |
| 12 提交、OS验证、完成指针 | run.yml、verification receipt、completion pointer 和远端 SHA 回读 |

独立审核应重点攻击：world/technical instance 的必要区分是否成立；无原生稳定 ID 时是否错误生成重复球员；同档恢复历史是否仍隐含分叉；Box 修订是否重复计数；多态引用是否可绕过 world；隐私规则是否覆盖派生与嵌套。自检不是独立审核。
