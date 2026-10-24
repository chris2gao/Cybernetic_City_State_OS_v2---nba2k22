# NBA2K22 第一大任务 · 全域数据库初始原型架构 V0.1

**状态：INITIAL_ARCHITECTURE_CANDIDATE / NOT_HUMAN_DECIDED / NOT_IMPLEMENTED**。Human批准了 V0.4 原型共同设计方法；**尚未批准本文的具体架构选择**。本原型参考获批需求 A v1.9、旧27表、146工程字段注册与39个AG Native研究入口。候选表名、字段名、类型和数量都可依实机逆向与Codex实现不断修订；未经02核验的游戏值域、UI或offset始终是UNKNOWN。

## 1. 初始总表目录：**56张候选表**

分类数量：RES-D 8张，RES-T / 身份 6张，RES-P 9张，RES-G / 统计 8张，RES-C 8张，RES-M 8张，RES-S/L 4张，RES-H 3张，RES-D/M 2张。**这个数字是当前设计提案，不是最终交付的物理表数量**；所有字段列表是初步已知列与未来需填实的字段族示例，不表示每张表已列完最终全部列。每张表必须在开发时逐列补充含义、准确SQLite类型、真实合法值域、单位、来源、空值、约束和测试。统一约定逻辑作用域必须是独立`save_id`，跨对象FK禁止连接不同存档；其他表的实际复合主键由Codex根据Human选定的物理隔离方式定型。

| # | RES | 候选表名 | 一行的数据粒度/职责 | 初步关键列/类型提示（非最终字典） | 关联方向 | 分表理由 |
|---:|---|---|---|---|---|---|
| 1 | RES-D | `saves` | 独立游戏存档 | save_id TEXT PK; native_save_fingerprint TEXT?; game_build TEXT? | 全部表的存档作用域 | 不存parent_save/fork/merge |
| 2 | RES-D | `seasons` | 本档一个赛季 | season_id TEXT PK; save_id TEXT FK; season_code TEXT; phase TEXT? | saves→seasons | 年份本身不足以唯一 |
| 3 | RES-D | `capture_runs` | 一次总采集 | capture_id TEXT PK; save_id TEXT FK; season_id TEXT?; started_at TEXT; game_date TEXT? | saves→capture_runs | 游戏时间≠真实采集时间 |
| 4 | RES-D | `capture_units` | 一个来源一致性单元 | unit_id TEXT PK; capture_id TEXT FK; source_key TEXT; status TEXT; observed_at TEXT | capture_runs→capture_units | 局部失败不污染成功项 |
| 5 | RES-D | `native_fields` | 真实字段与证据注册 | field_id TEXT PK; native_key TEXT; ui_label TEXT?; data_type TEXT?; min_value TEXT?; max_value TEXT?; evidence_grade TEXT; visibility TEXT | 数据观察引用字段字典 | 工程注册不等于实测 |
| 6 | RES-D | `source_artifacts` | 一份有界原始证据 | artifact_id TEXT PK; unit_id TEXT FK; source_hash TEXT; source_version TEXT; payload_ref TEXT?; restricted INTEGER | capture_units→source_artifacts | 敏感原始字节不得普通GM直读 |
| 7 | RES-D | `field_gaps` | 一个目标字段的缺口 | gap_id TEXT PK; field_id TEXT?; domain TEXT; cause TEXT; impact TEXT; human_exception_ref TEXT? | native_fields?→field_gaps | Q10 Human例外单列 |
| 8 | RES-D | `fact_conflicts` | 一笔观察/事实冲突 | conflict_id TEXT PK; save_id TEXT FK; object_ref TEXT; evidence_a TEXT; evidence_b TEXT; review_status TEXT | 可信事实与冲突候选 | 已确定历史不可改写 |
| 9 | RES-T / 身份 | `teams` | 本档球队身份 | team_id TEXT PK; save_id TEXT FK; native_team_id TEXT?; display_name TEXT | saves→teams | 球队改名/扩张身份须证明 |
| 10 | RES-T / 身份 | `team_seasons` | 球队某赛季的参赛状态 | team_season_id TEXT PK; team_id TEXT FK; season_id TEXT FK; conference TEXT? | teams×seasons | 跨季身份与赛季属性分离 |
| 11 | RES-T / 身份 | `players` | 本档球员身份 | player_id TEXT PK; save_id TEXT FK; native_player_id TEXT?; identity_state TEXT | saves→players | 同名与原生slot不构成跨档身份 |
| 12 | RES-T / 身份 | `staff_members` | 本档员工身份 | staff_id TEXT PK; save_id TEXT FK; native_staff_id TEXT?; identity_state TEXT | saves→staff_members | staff池槽位≠球队归属 |
| 13 | RES-T / 身份 | `roster_memberships` | 球队与球员的真实归属观察 | membership_id TEXT PK; player_id TEXT FK; team_id TEXT? FK; unit_id TEXT FK; observed_at TEXT | players→teams×capture_units | 当前名单≠真实交易事件 |
| 14 | RES-T / 身份 | `team_rotation_slots` | 球队某次轮换计划槽位 | slot_id TEXT PK; team_id TEXT FK; player_id TEXT? FK; unit_id TEXT FK; slot_index INTEGER; planned_minutes INTEGER? | teams×players×capture_units | 计划分钟≠真实比赛分钟 |
| 15 | RES-P | `player_vitals_observations` | 球员一次Vitals读取 | observation_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; height_raw INTEGER?; weight_raw INTEGER?; birth_date TEXT? | players×capture_units | 真实基础信息与更改历史区分 |
| 16 | RES-P | `player_attribute_snapshots` | 一次球员能力字段族快照 | observation_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; overall_raw INTEGER?; shot_close_raw INTEGER?; driving_layup_raw INTEGER?; potential_restricted_raw INTEGER?; other_confirmed_rating_columns [TBD] | players×capture_units；native_fields | 宽typed字段族以控制100季历史膨胀；潜力严格受限 |
| 17 | RES-P | `player_tendency_snapshots` | 一次倾向字段族快照 | observation_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; tendency_columns [TBD]; layout_version TEXT | players×capture_units | 未枚举的倾向字段不伪装已完成 |
| 18 | RES-P | `player_play_type_slots` | 一个有序PlayType槽 | slot_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; slot_index INTEGER; play_code TEXT? | players×capture_units | 有序关系须独立可查询 |
| 19 | RES-P | `player_badge_values` | 一次观察中某种徽章及等级 | badge_obs_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; badge_key TEXT; native_code INTEGER?; tier_label TEXT?; owned_state TEXT | players×capture_units | 2bit与五标签编码矛盾待验证 |
| 20 | RES-P | `player_contract_observations` | 球员一次真实合同状态 | contract_obs_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; team_id TEXT? FK; salary_raw INTEGER?; years_left INTEGER?; original_years_raw INTEGER?; extension_length_raw INTEGER? | players×teams×capture_units | 合同同offset833疑点不得猜值 |
| 21 | RES-P | `player_health_observations` | 球员伤病/疲劳实际状态 | health_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; injury_code TEXT?; fatigue_raw INTEGER?; availability TEXT? | players×capture_units | 伤病与Durability能力属性不同 |
| 22 | RES-P | `player_morale_observations` | 球员真实士气/角色状态 | morale_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; morale_raw INTEGER?; role_code TEXT? | players×capture_units | 不生成AI人格指标 |
| 23 | RES-P | `player_training_observations` | 一次个人训练设置 | training_id TEXT PK; player_id TEXT FK; unit_id TEXT FK; focus_code TEXT?; intensity_raw INTEGER? | players×capture_units | 不推断训练必然产生发展 |
| 24 | RES-G / 统计 | `games` | 某赛季一场真实比赛 | game_id TEXT PK; season_id TEXT FK; native_game_id TEXT?; home_team_id TEXT FK; away_team_id TEXT FK; game_date TEXT?; status TEXT | seasons×teams | GameID跨季唯一性待Native证实 |
| 25 | RES-G / 统计 | `game_period_scores` | 某场某队某节得分 | game_id TEXT FK; team_id TEXT FK; period_index INTEGER; period_points INTEGER; unit_id TEXT FK | games×teams；复合唯一候选 | 加时扩展；累计和Game原值不同 |
| 26 | RES-G / 统计 | `team_game_boxes` | 一场一队真实Box | box_id TEXT PK; game_id TEXT FK; team_id TEXT FK; unit_id TEXT FK; points INTEGER?; rebounds INTEGER?; assists INTEGER? | games×teams | 原生高阶只收真实可证字段 |
| 27 | RES-G / 统计 | `player_game_boxes` | 一场一球员真实Box | box_id TEXT PK; game_id TEXT FK; player_id TEXT FK; team_id TEXT FK; unit_id TEXT FK; points INTEGER?; fg_made INTEGER?; fg_attempted INTEGER?; minutes_raw INTEGER? | games×players×teams | StatBank原值、计算值须区分 |
| 28 | RES-G / 统计 | `playoff_series` | 一个真实可证系列赛 | series_id TEXT PK; season_id TEXT FK; team_a_id TEXT FK; team_b_id TEXT FK; round_code TEXT? | seasons×teams | 不凭日期推断系列赛 |
| 29 | RES-G / 统计 | `playoff_series_games` | 系列赛中某一比赛的关联 | series_id TEXT FK; game_id TEXT FK; sequence_no INTEGER? | playoff_series×games | 有证关系才入库 |
| 30 | RES-G / 统计 | `player_season_totals` | 某球员某季原生累计观察 | total_id TEXT PK; player_id TEXT FK; season_id TEXT FK; unit_id TEXT FK; team_scope TEXT?; gp INTEGER?; points INTEGER? | players×seasons×capture_units | Slot24源≠Box自行聚合 |
| 31 | RES-G / 统计 | `team_season_totals` | 某球队某季原生累计观察 | total_id TEXT PK; team_id TEXT FK; season_id TEXT FK; unit_id TEXT FK; wins INTEGER?; losses INTEGER?; points INTEGER? | teams×seasons×capture_units | 阶段性累计与最终定稿区分 |
| 32 | RES-C | `staff_team_assignments` | 一次员工所属球队/岗位的可证观察 | assignment_id TEXT PK; staff_id TEXT FK; team_id TEXT? FK; role_code TEXT; unit_id TEXT FK | staff_members×teams | 未知映射允许隔离 |
| 33 | RES-C | `staff_contract_observations` | 一次员工合同状态 | contract_obs_id TEXT PK; staff_id TEXT FK; unit_id TEXT FK; salary_raw INTEGER?; years_left INTEGER? | staff_members×capture_units | 人员与合同不混表 |
| 34 | RES-C | `staff_skill_observations` | 员工实际能力配置 | skill_obs_id TEXT PK; staff_id TEXT FK; unit_id TEXT FK; offense_raw INTEGER?; defense_raw INTEGER?; scouting_raw INTEGER? | staff_members×capture_units | STAFF13项为候选线索 |
| 35 | RES-C | `coach_preferences` | 教练个人偏好设置 | pref_id TEXT PK; staff_id TEXT FK; unit_id TEXT FK; preferred_system INTEGER?; personal_style TEXT? | staff_members×capture_units | 教练偏好≠球队生效战术 |
| 36 | RES-C | `team_tactic_settings` | 球队POE/ACE/Freelance等实际设置 | tactic_id TEXT PK; team_id TEXT FK; unit_id TEXT FK; poe_code TEXT?; ace_code INTEGER?; freelance_code INTEGER? | teams×capture_units | 真实键和值域待02 |
| 37 | RES-C | `team_playbook_slots` | 球队Playbook中一个有序槽位 | slot_id TEXT PK; team_id TEXT FK; unit_id TEXT FK; slot_index INTEGER; play_code TEXT? | teams×capture_units | 打法与排序是多行关联 |
| 38 | RES-C | `team_training_settings` | 球队一次团队训练设置 | training_id TEXT PK; team_id TEXT FK; unit_id TEXT FK; focus_code TEXT?; intensity_raw INTEGER? | teams×capture_units | 与球员训练区分 |
| 39 | RES-C | `mentorship_relations` | 一次真实可得导师关系 | mentor_id TEXT PK; player_id TEXT FK; mentor_player_id TEXT? FK; team_id TEXT? FK; unit_id TEXT FK | players同档自关联 | 不靠姓名或变化推造导师关系 |
| 40 | RES-M | `team_finance_observations` | 球队某次真实财务状态 | finance_id TEXT PK; team_id TEXT FK; unit_id TEXT FK; payroll_raw INTEGER?; cap_space_raw INTEGER?; luxury_tax_raw INTEGER?; budget_raw INTEGER? | teams×capture_units | 原版数值不等于自定义GM规则 |
| 41 | RES-M | `market_state_observations` | 真实市场状态或外挂挂牌 | market_id TEXT PK; save_id TEXT FK; unit_id TEXT?; person_ref TEXT?; market_status TEXT; origin_type TEXT | 人员身份及来源可证映射 | 报价、市场现态和已成交事件分离 |
| 42 | RES-M | `external_transaction_events` | 外部机制真正确认的一笔成交 | transaction_id TEXT PK; save_id TEXT FK; event_type TEXT; occurred_at TEXT?; source_ref TEXT; status TEXT | saves→transaction_events | 不能从转队差分制造历史 |
| 43 | RES-M | `transaction_components` | 成交中的一个人员/资产/合同组件 | component_id TEXT PK; transaction_id TEXT FK; from_team_id TEXT? FK; to_team_id TEXT? FK; person_ref TEXT?; pick_id TEXT? | transaction_events 1:N | 支持多资产交易但不套用原版复杂保护 |
| 44 | RES-M | `draft_pick_assets` | 某档一个可转让选秀权 | pick_id TEXT PK; save_id TEXT FK; draft_year INTEGER; draft_round INTEGER; original_team_id TEXT FK; owner_team_id TEXT? FK | saves×teams | 自定义规则直接整项转移 |
| 45 | RES-M | `draft_pick_ownerships` | 选秀资产一次可证归属记录 | ownership_id TEXT PK; pick_id TEXT FK; owner_team_id TEXT FK; unit_id TEXT?; event_ref TEXT? | draft_pick_assets×teams | 当前实际游戏值与外部权益账分源 |
| 46 | RES-M | `draft_prospects` | 真正可识别的选秀候选 | prospect_id TEXT PK; save_id TEXT FK; draft_year INTEGER; native_prospect_id TEXT?; display_name TEXT? | saves→draft_prospects | Slot55/57未证，不虚造候选 |
| 47 | RES-M | `draft_results` | 一项实际选秀结果 | result_id TEXT PK; prospect_id TEXT? FK; pick_id TEXT? FK; team_id TEXT FK; player_id TEXT? FK; source_ref TEXT | prospects×assets×players | 候选不直接等于生成球员实例 |
| 48 | RES-S/L | `worldline_config_versions` | 某存档拟应用的一个配置版本 | config_id TEXT PK; save_id TEXT FK; config_version TEXT; config_hash TEXT; approval_ref TEXT? | saves→config_versions | 仅记录目标配置，不求最优值 |
| 49 | RES-S/L | `game_setting_observations` | 一次实际读取的游戏设置值 | setting_obs_id TEXT PK; save_id TEXT FK; unit_id TEXT FK; field_id TEXT FK; native_value TEXT?; display_value TEXT?; scope_code TEXT | native_fields×capture_units | 联盟/比赛/USER/CPU/Normalize实际数据 |
| 50 | RES-S/L | `startup_config_checks` | 本次开档配置目标与实测对账 | check_id TEXT PK; config_id TEXT? FK; setting_obs_id TEXT? FK; result TEXT; dependency_ref TEXT? | config_versions×game_setting_observations | 为后续配置执行器预留不开发执行器 |
| 51 | RES-S/L | `league_rule_observations` | 某赛季实际联盟规则值 | rule_id TEXT PK; season_id TEXT FK; unit_id TEXT FK; rule_key TEXT; raw_value TEXT?; display_value TEXT? | seasons×capture_units | 原版规则与外部自定义规则区分 |
| 52 | RES-H | `season_award_instances` | 某季真实已发生奖项 | award_id TEXT PK; season_id TEXT FK; award_code TEXT; award_type TEXT; unit_id TEXT FK | seasons→awards | 暂时榜首不能变成最终奖项 |
| 53 | RES-H | `award_recipients` | 真实获奖人/球队名单项 | recipient_id TEXT PK; award_id TEXT FK; player_id TEXT? FK; team_id TEXT? FK; rank_index INTEGER? | awards×players/teams | 一奖多人/最佳阵容槽可表达 |
| 54 | RES-H | `season_record_entries` | 游戏真实纪录与持有人 | record_id TEXT PK; season_id TEXT FK; record_key TEXT; holder_player_id TEXT? FK; holder_team_id TEXT? FK; value_raw TEXT; source_ref TEXT | seasons×players/teams | 不开发额外高级荣耀统计 |
| 55 | RES-D/M | `external_execution_receipts` | 未来获授权写入的一次回执 | receipt_id TEXT PK; save_id TEXT FK; transaction_id TEXT? FK; attempted_at TEXT; write_status TEXT; source_ref TEXT | transaction_events?×saves | 只负责数据契约，不开发游戏写入器 |
| 56 | RES-D/M | `external_readback_checks` | 执行后游戏复读/事实对账 | check_id TEXT PK; receipt_id TEXT FK; unit_id TEXT? FK; expected_state TEXT; observed_state TEXT?; reconcile_status TEXT | external_execution_receipts×capture_units | 执行器报告成功不等于游戏已证成功 |

## 2. 第一版真实关系图

```text
saves
 ├── seasons ── games ── game_period_scores
 │       │       ├─ player_game_boxes ── players
 │       │       ├─ team_game_boxes ── teams
 │       │       └─ playoff_series_games ── playoff_series
 │       ├── player_season_totals / team_season_totals
 │       ├── league_rule_observations
 │       └── season_award_instances ── award_recipients / season_record_entries
 ├── teams ── team_seasons / roster_memberships / team_rotation_slots
 │       └── team_tactic_settings / team_playbook_slots / team_training_settings / team_finance_observations
 ├── players ── player_attribute_snapshots / player_tendency_snapshots / player_badge_values
 │       └── player_vitals / play_types / contracts / health / morale / training
 ├── staff_members ── staff_team_assignments / contracts / skills / coach_preferences
 ├── draft_pick_assets ── draft_pick_ownerships / draft_results
 ├── external_transaction_events ── transaction_components
 └── capture_runs ── capture_units ── source_artifacts + 原生对象观察
```

## 3. 两项需要Human先决定的核心架构ADR

### ADR-01 存档数据库的物理组织

- **A（建议）**：**每个完全独立游戏存档一份SQLite事实数据库**；原始字节证据/控制清单可单独归档。优点：防串档容易证明，同档事务和100季查询简单；成本：多存档维护与Schema升级需批量处理。
- **B**：所有独立存档保存于同一SQLite，所有事实/关系均使用严格`save_id`复合键/FK隔离。优点：集中Schema升级和管理；代价：串档防线、单库体积、错误传播与权限设计更复杂。
- 不论A/B，游戏存档互不继承/分叉/合并已由Human确定，**不再提选项**。A只是初始工程建议，缺真实容量/事务测试，不宣称性能最优。

### ADR-02 高频球员能力/倾向/徽章的100季存储方式

- **A（建议）**：身份和比赛事实采用正常typed表；Attributes/Tendencies等高频大量字段按**字段族typed宽快照表（某球员某批次一行）**保存；PlayTypes/Badges有序或稀疏集合采用独立子表；配原生字段目录和一致性单元。优点：大规模历史更紧凑，查询完整球员更直接；代价：新字段需要Schema迁移和来源状态管理。
- **B**：所有属性作为`(save,player,field,observed_at,typed_value)`细粒度长表。优点：新增字段灵活；代价：数十或数百字段×数千球员×40次×100季导致极大细行数量，约束和常见宽查询更复杂。
- 建议A为主体，对尚不能形成稳定typed快照的稀疏/未知/变长来源允许少量B式行存储；但不能用万能JSON/EAV逃避每个实际字段的业务定义和值域。

## 4. 现有证据与建表时必须保持的未知项

- **GAME**：AG_NATIVE_01D研究将game_id、日期、双方、节比分、状态等指向`SEASON_SCHEDULE`，球员Box指向`BOXSCORE_STATBANK`；研究中`final_score`为`DERIVED_WITH_FORMULA`，不能伪称游戏原生读数。
- **季赛统计**：Slot24 PLAYER_STATS研究有games_played、games_started、points等候选原生累计，与比赛Box累加要分别保真与对账；`team_scope/TOT`真实性待验证。
- **球员**：Slot1 PLAYER及72个工程注册字段为研究入口，不能宣称PlayerCard全字段已证；合同`original_contract_years`与`extension_length`同offset833、徽章2-bit与五标签等问题交Native探索。
- **教练**：STAFF13注册不足以证明员工队伍归属；战术/训练的全部游戏UI来源待逆向。PLAN中的`team_tactic_settings`不能冒充已核实ACE/POE全部字段。
- **选秀/G联赛**：Slot36选秀资产候选可研究，`draft_prospect_pool`与G League team映射仍UNKNOWN；不得虚造球员或身份关系。
- **设置**：初步字段结构只承载原生真实值与未来外部预期；世界线最优值、实际游戏写入与模拟交易策略均不是本任务。
- **历史**：真实荣誉/新闻须有游戏来源；时间发生型事实与采集观察不同，Q22 Human冲突、Q23幂等补录、Q24赛季定稿都要落实到SQL。
- **旧27表**：仅作迁移对照，不保证保留旧表名或数量；旧CBA强制规则与选秀保护业务不允许反向约束新简化自定义GM。

## 5. Codex实现前需明确的设计约束

1. 每个候选表的**业务含义/数据粒度/源/关系**要可检验；Codex可合并或拆分表，但要保留解释和全域数据覆盖对照，不能因为一张通用大表保存JSON就宣称全部数据库完成。
2. 字段真实值域（例如某原始评分的允许范围、是否存在某Slider）需02取证；原型可以保留候选SQLite类型，但**不能以猜测建立不可逆CHECK约束**。
3. `player_attribute_snapshots`、`player_tendency_snapshots`采用字段族宽行候选不是忽略字段级新鲜度：每个来源一致性单元必须可证全组成功，部分失效字段不能写为新零值；必要时拆快照单元/增加字段缺口记录。
4. 游戏内真实时间、读取/入库时间、原生来源版本彼此区分；完成历史事实不可覆写，跨档相同原生ID不能连接。
5. 外部成交/未来写入回执作为数据库**数据契约**预留，第一任务不开发真实游戏写入程序；hidden Potential不能向普通GM查询/导出/聚合。
6. 进入实际代码施工前，由Human先裁决上面两项全局ADR或给出调整意见；此后Codex负责可运行SQLite原型与持续实现，Gemini按来源缺口小包补证，开发期有限轻量验证，完整候选之后集中独立审核。

**状态：PROTOTYPE_ARCHITECTURE_CANDIDATE_PENDING_HUMAN_ADR。**
