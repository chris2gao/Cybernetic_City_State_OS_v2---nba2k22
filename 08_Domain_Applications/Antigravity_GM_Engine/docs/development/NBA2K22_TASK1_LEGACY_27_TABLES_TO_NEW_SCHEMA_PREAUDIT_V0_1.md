# NBA2K22 第一大任务 · 旧27表→新数据库设计证据对照 V0.1

**状态：真实已存在代码的静态盘点 + 规划建议，不是新物理Schema定稿。** 来源：当前 `master` 的 `08_Domain_Applications/Antigravity_GM_Engine/database/schema.sql`。以下27表均来自实际 CREATE TABLE 语句；示例列取静态文本中的一部分，**不是每表全部字段列举，数量/列定义/真实原生取值还须由Codex逐列可靠复核**。新架构不必保留旧表名或27张的数量。

| 现有旧表 | 新RES业务责任候选 | 现存列举例（非全部） | 为什么需要重审 | 来源状态 |
|---|---|---|---|---|
| `teams` | RES-T/D | `team_id`, `abbreviation`, `city`, `name` | 保留真实球队身份并核查存档作用域 | LEGACY_UNVERIFIED |
| `coaches` | RES-C | `coach_id`, `team_id`, `first_name`, `last_name` | 核实staff身份归属，不能按slot直绑 | LEGACY_UNVERIFIED |
| `staff_pool_observations` | RES-C/D | `snapshot_id`, `staff_slot`, `first_name`, `last_name` | 原始staff池观察 vs 真实任职隔离 | LEGACY_UNVERIFIED |
| `coaching_source_captures` | RES-C/D | `snapshot_id`, `data_updated_at` | 采集批次/原生证据责任 | LEGACY_UNVERIFIED |
| `coaching_team_observations` | RES-C | `snapshot_id` | 核实球队可证任职与时间 | LEGACY_UNVERIFIED |
| `player_source_details` | RES-P/D | `snapshot_id`, `pool_slot`, `birth_date` | 原生信息/人物身份关系 | LEGACY_UNVERIFIED |
| `staff_source_details` | RES-C/D | `snapshot_id`, `role` | staff角色字段及权限 | LEGACY_UNVERIFIED |
| `team_source_stats` | RES-T/D | `snapshot_id`, `totals_json` | 球队原生总计字段逐项证明 | LEGACY_UNVERIFIED |
| `draft_asset_observations` | RES-M/D | `snapshot_id`, `current_owner_team_id`, `draft_year`, `mapping_status` | 原版选秀资产观察≠自定义归属 | LEGACY_UNVERIFIED |
| `coach_mapping_quarantine` | RES-C/D | `legacy_coach_id`, `legacy_team_id`, `first_name`, `last_name` | 未知团队映射必须隔离 | LEGACY_UNVERIFIED |
| `players` | RES-P/M/T | `player_id`, `team_id`, `contract_team_id`, `first_name` | 身份、合同与状态混合；候选拆分 | LEGACY_UNVERIFIED |
| `trade_manifests` | RES-M | `trade_id`, `season_year`, `trade_date`, `team_a_id` | 旧强制原版CBA字段不能绑架自定义规则 | LEGACY_UNVERIFIED |
| `monthly_snapshots` | RES-D | `snapshot_id`, `season_year`, `month_index`, `month_name` | 年月粒度不能替代真实采集批次 | LEGACY_UNVERIFIED |
| `save_metadata` | RES-D | `key`, `value` | 缺少可靠单独存档作用域时需重构 | LEGACY_UNVERIFIED |
| `team_monthly_stats` | RES-T/M | `id`, `snapshot_id`, `team_id`, `team_abbr` | 球队月统计与财务事实分离 | LEGACY_UNVERIFIED |
| `player_monthly_stats` | RES-P | `id`, `snapshot_id`, `player_id`, `team_id` | 能力/合同/伤病/统计混合，拆分候选 | LEGACY_UNVERIFIED |
| `player_growth_history` | RES-P/H | `id`, `snapshot_id`, `player_id`, `player_name` | 仅有证发生或当次观察，避免推断事件 | LEGACY_UNVERIFIED |
| `team_monthly_evaluations` | RES-T/D | `id`, `snapshot_id`, `team_id`, `team_abbr` | 旧派生GM评估不等于游戏原始事实 | LEGACY_UNVERIFIED |
| `seasons` | RES-L/S/D | `season_year`, `season_code`, `salary_cap`, `luxury_tax_threshold` | 必须有单存档下赛季身份与规则口径 | LEGACY_UNVERIFIED |
| `team_season_history` | RES-T/H | `id`, `season_year`, `team_id`, `team_abbr` | 真实球队赛季最终事实与当前观察分层 | LEGACY_UNVERIFIED |
| `player_season_stats` | RES-P/H | `id`, `season_year`, `player_id`, `player_name` | 原生季累计与计算场均分离 | LEGACY_UNVERIFIED |
| `staff_dynasty_history` | RES-C/H | `id`, `season_year`, `staff_name`, `role` | 姓名关联不能证明staff跨季身份 | LEGACY_UNVERIFIED |
| `draft_picks_ledger` | RES-M | `pick_id`, `draft_year`, `round`, `original_team_id` | 自定义直接转让选秀权，不执行保护/互换 | LEGACY_UNVERIFIED |
| `mentorship_dynasty_trees` | RES-C/P | `id`, `season_year`, `team_id`, `mentor_name` | 真实导师关系和姓名同一性待证 | LEGACY_UNVERIFIED |
| `market_trade_block` | RES-M | `item_id`, `snapshot_id`, `team_abb`, `player_id` | 外挂挂牌与游戏可见市场分离 | LEGACY_UNVERIFIED |
| `market_trade_offers` | RES-M | `offer_id`, `snapshot_id`, `buyer_team`, `seller_team` | 自定义报价/谈判与原版CBA断开 | LEGACY_UNVERIFIED |
| `market_free_agents` | RES-M/P | `fa_id`, `snapshot_id`, `player_name`, `position` | 自由球员与球队/合同的当前观察 | LEGACY_UNVERIFIED |

## 必须交给 Codex ARCH/SCHEMA 的明确工作

1. **逐旧表**给确切字段数量、逐列原类型/约束/说明、已有源或真实游戏缺口，提案 `KEEP / REWORK / SPLIT / MERGE / RETIRE` 及数据历史迁移责任。此 V0.1 为事实入口，不替代逐字段工作。
2. **新增当前旧表覆盖不到的真实对象**：GAME主表及周期比分、PLAYER_GAME_BOX/TEAM_GAME_BOX、季后赛series、球员全Card字段族、完整球队轮换、教练个人战术与球队生效战术、世界线配置及开档读回、统一原生字段证据/采集一致性单元、冲突待审/缺口、真实外部业务事实及执行回执等。真实UI/Native逐列补证后建立新候选表与关系。
3. **先给一个真正可讨论的完整候选总表目录**：从本旧表映射加新增对象形成明确候选数量、每张表责任、身份键、来源键、字段族、关联对象、合并或拆分理由。候选可调整，但正式阶段03**必须**确切给出全部物理表、每张所有字段、合法值域、ER/PK/FK/索引与完整SQLite DDL。
4. **不能使用未确认的旧游戏规则/姓名映射作为约束**：自定义选秀权直转、外部交易事实/游戏再观测分离，旧表中的工资配平与选秀保护设计仅作遗留兼容风险；存档永不跨档分叉/继承/合并。
5. **旧表能查到不等于来源真实**：所有列逐项标 `SOURCE_RESEARCH / UI_NATIVE_VERIFIED / UNKNOWN / DERIVED / SENSITIVE` 等实际证据（具体等级应与02取证规范一致），未经证实不得填充假值或把计算数据冒充游戏原生。

这份总账只是**让第一批工作从真实27表及具体字段开始**，不是用27张旧表来决定新表数。
