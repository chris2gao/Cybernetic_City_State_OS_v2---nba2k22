# DEV14 — 确定性状态读写引擎（Deterministic State I/O Engine）V1.1

> **2026-10-19 开发模型窗口职责（最新）**：[DEV18两个Codex窗口接力](DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)明确本文件的底层工作由**独立DEV14 Codex窗口①/PR#5**负责。M系列Codex窗口②/PR#4只在用户转交`DEV14_TO_M3_HANDOFF.md`和稳定接口后实施GM战术与球队经营，不应在PR#4重复实现数据库、内存编码、潜力脱敏和审批执行器。新档各队本名Playbook为用户确认的默认业务前提，**取消预先研究克隆/共享书冲突的前置开发**；仍保留正常Book Native ID和内存写入回读校验。PR合并和游戏真实变更仍需用户授权。

> **2026-10-19 个人防守与独占战术书新GM写权限（覆盖旧执行依赖）**：[权威GM政策](../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)。已有DEV14可以读写OVERALL/PERSONAL及共享Book，但GM最新指令要求**日常仅PERSONAL_DEFENSE写、OVERALL_DEFENSE只读**，不再生成常规先整体后个人批次；**GM日常禁止写coach.PlaybookID**，只编辑本队真实独占Playbook（原生owner严格一个且等于本队）。对共享书（即使owner集合无变化）返回SHARED_PLAYBOOK_MUTATION_BLOCKED，不能让A改Book连带B。换帅/建档技术性专属Book绑定是玩家特别批准、AG原生确认后的例外；若不能形成独占对象即Fail Closed不改槽。实施与最小验收见[DEV16](DEV_20261019_16_M3_NATIVE_COVERAGE_AND_GM_TRAINING_PLAYBOOK_INTEGRATION_V1.md)。此段为**当前用户授权开发的新需求**，PR#5现有代码还未实现完毕。

> **2026-10-19 DEV16新增字段范围与家族验证原则**：[DEV16](DEV_20261019_16_M3_NATIVE_COVERAGE_AND_GM_TRAINING_PLAYBOOK_INTEGRATION_V1.md)确认原统一读写机制已实质接入19Coach默认/18Overall和个人防守、68手册槽、4PlayTypes/Initiator、48个具名可写+51个未知只读Tendencies、6队伍/5球员训练、4Gameplay USER/CPU及50World；Codex无需重写。Antigravity补手册Play CRC映射及替换流程、51未知倾向真实语义、按位置训练模板+当前疲劳只读。训练只改模版/强度/B2B恢复，不逐属性微调；已实测的同类codec只需一条代表样本，保留通用值域/原值/对象身份/位域校验。World/Gameplay仍按已有已登记字段执行，未注册的字段只待字典补录，无逐项反复手工测试要求。整体防守+个人防守、换Playbook+编槽位的限制属于顺序依赖，不是禁止同一GM方案。

> **2026-10-19 用户最终决定：DEV15 V2覆盖潜力与综评补偿旧例外限制**：[DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)要求`full_verified_v1`采集完毕后且正式commit/SQLite备份/manifest哈希/发布前**自动执行潜力置1后处理**，包括pool/roster数值、JSON、PLAYER raw_struct byte 0x441，并将这类人为遮蔽明确标`NOT_OBSERVED`；同时允许通过特定allowlist为30队GM开放PLAYER 0x440`Intangibles`综评补偿25–99的获批轮换动作，不要求额外研究交易/合同/模拟副作用，仍不准泛化修改其它原始Ability字段。DEV14原A/B/C/D架构无需重构，新开发仅增量添加这两部分。

> **上线前加固（2026-10-19）**：[DEV14-H](DEV_20261019_14H_DEV14_POST_REVIEW_HARDENING_V1.md)须在正式自动执行之前处理第三库`player_pool.sqlite`代次绑定和独立真人审批来源，现PR#5工程完成不等于生产完成。[分批执行顺序](M_SERIES_20261019_QUOTA_AWARE_EXECUTION_PLAN_V1.md)。新注册`Intangibles`/OVR compensation须按[DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)的已确认PLAYER 0x440特殊单字段权限，不属于普通Ability写权限；GM查询输出隐藏真实Potential，但本地原始源保留。

**日期：2026-10-19；执行模型：Codex；原生字段/游戏内存适配来源：Antigravity；需求与审阅：Web Development；游戏修改批准人：玩家。**
**状态：APPROVED_TO_DEVELOP_BY_PLAYER_REQUEST / GAME_WRITE_NOT_AUTHORIZED / CAPTURE_NOT_TRIGGERED。** 本文件是交付Codex的正式工程任务，不表示任何正式存档已经修改。
**实施优先级**：DEV14底座先于DEV13的M3-T生产级集成；不推翻已完成的M3A/M3B，不提前启用GM V4/M4。
**V1.1新增用户需求**：开新档、活动存档切换、可恢复的安全reset。复用`src/save_context.py`按`save_id`物理隔离，最多4个可切换档、同一时刻一个活动档，不采用全库清空。DEV14新增D期。

## 0. 一句话目标、为什么现在做

把游戏全局平衡设置（USER与CPU两页）、MyLEAGUE世界线与Sim/成长设置、30队教练与战术/个人防守、球员99项Tendencies/4项Play Types、全联盟训练与导师等大量原生配置，统一成**数据库管理的事实/目标/批准计划/执行结果**。模型最多产生少量`{对象, 字段, 目标值, 理由}`，**确定性Python代码**独立完成展开、范围与身份验证、位域编码、写前前值比对、批量写入、读回和恢复；采集反向复用同一字段字典和解码器，更新已有不可变批次，使将来的Gemini Flash等低成本调度模型**无须逐项操作上千个内存地址**。

**核心：Model plans; database stores states; deterministic code executes/captures; player approves writes.**

不追求把NBA2K22内存做成“保证物理原子提交”的假数据库：进程内存没有SQLite事务；允许条件恢复及准确披露`PARTIAL_UNRECOVERED`，不谎报成功。本任务明确工作范围，不发动无关广泛测试。

## 1. 已经存在的系统与必读真实路径

| 路径（main真实存在；M3仍为Draft PR） | 职责 / DEV14复用方式 |
|---|---|
| `docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md` | **开发先行、边界明确、适量定向验证**；不要无休止覆盖边缘场景 |
| `docs/GM_SQLITE_QUERY_ACCESS.md`、`src/gm_data_access/query.py`、`scripts/gm_data_query.py` | M0已有同批、只读、分页/限额、角色与来源回执，不另造给网页GPT的直连活动库 |
| `database/schema.sql` | 现有事实数据库Schema，含非连续球队ID的真实集合（如CHA=31），**不假设30队ID固定0..29** |
| `src/auto_pipeline_ingest.py`、`src/coaching_source.py` | 已有`league_state.sqlite`观测入库、教练同会话读/批次审计（30队19项、对29队整体防守） |
| `src/export_web_gm.py`、`scripts/run_data_update.ps1`、`scripts/gm_data_snapshot.py` | 玩家触发`full_verified_v1` → 双库审计归档 → 只读查询副本/JSON发布。保留唯一latest、历史批次不可覆盖 |
| `src/coach_locator.py`、`src/coaching_reader.py`、`src/coaching_targets.py` | 正确定位当前游戏、存档、30队教练及战术对象，作为插件/适配器 |
| `config/coach_tactics_profile.json`、`src/coach_codec.py`、`src/defense_codec.py` | 原生字段/位域/合法枚举来源，**注册后复用，禁止再写第二份含义矛盾的offset字典** |
| `src/gm_core/coaching_batch.py`、`src/coaching_batch_executor.py` | 已有无内存的提案校验、batch digest、`BatchApproval`、preflight、独占写、前值持久化、条件恢复、读回。DEV14抽公共规则并保证旧CLI可用 |
| `src/tactical_reader.py`、`src/player_tactics_adapter.py`、`src/matchup_defense_adapter.py` | main早期DEV12读取/写入模块。**Antigravity本地新版不一定与main一致**：Codex拿到其完整`antigravityUse/完整战术与球员行为系统/`成果后先做字段/对象对照，不盲目覆盖旧源码 |
| `docs/development_tasks/DEV_20261019_12_V2_ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING.md` | DEV12原生游戏能力与知识层由Antigravity开发，本任务**不再重新找99个Tendency内存地址** |
| `docs/development_tasks/DEV_20261019_13_M3_TACTICAL_DECISION_INTEGRATION_V1.md` | 后续M3战术决策集成，本任务只提供可复用底座与数据接口 |
| `docs/research/NBA2K22_EXTERNAL_GM_MYLEAGUE_WORLD_SETTINGS_V1_20261019.md`、`docs/research/NBA2K22_WORLD_RULES_V2_GAP_AUDIT_20261019.md` | 世界线候选及未决语义：`CPUAttributeBoost`等不因代码能定位便自动批准配置 |
| `config/source_catalog.json`、`web_gm/memory/DEVELOPMENT_CURRENT.md` | 已有生产来源/开发状态契约；正式完成时更新能力登记与开发记忆 |

M3当前`PR #4`（`fa62fb2...`）是Draft、未合并；现有M0/M1/M2与DEV12早期实现均在main。**优先从main创建独立DEV14分支**，不用把尚未合并的M3硬拷贝到main；只声明以后DEV13消费的稳定接口。

## 2. 数据模型决议：三类状态，不是30×N张重复表

保留事实两库：
- `database/league_state.sqlite`：正式采集后的游戏观测事实；`player_pool.sqlite`：人物池。不可让执行器直接修改已封存的`snapshot`事实。
- **新增`database/saves/<save_id>/gm_control.sqlite`（每个存档各一份，复用`save_context`隔离，不允许全局共享）**：目标配置、审批批次、写入结果、对账与恢复日志索引。实际文件与完整内存日志默认不当GitHub源码跟踪；只在玩家允许的发布流程上传需要的审计摘要。不得把未批准`desired`发布为`observed`。

数据库“按游戏页面区分逻辑视图、但按对象类型共享物理表”：**不创建30个完全相同的Pacers/Warriors/Lakers战术表，也不为USER/CPU维持两份冗余迁移代码**。例如`gameplay_settings`有`side=USER/CPU`，并可创建`v_gameplay_user`与`v_gameplay_cpu`视图；球队字段用**经过观测验证的原生team_id**。

### 2.1 最小表模型（命名是建议，Codex在不破坏现有Schema前提下可调整）

**静态字段注册（代码/JSON权威，可在SQLite投影为查询表）**：
- `native_field_registry`：`profile_version, domain, field_key, display_name, target_kind, value_type, native_codec, range_or_enum, byte_group/bit_mask, source_adapter, writer_adapter, read_status, write_capability, setting_page, validity_scope, behavior_evidence`。
- 类型和原生地址/位域遵从`coach_tactics_profile`、`memory_field_profile`及Antigravity真实字段目录；绝对运行内存地址**不存作跨进程可重用字段**。`raw范围已证`与`游戏行为影响已证`是两个状态；缺失值`UNKNOWN/NULL`，绝不自动补50。
- registry使用版本和fingerprint，每份批次绑定该profile版本，避免修改字典后用新意义解释旧值。

**观察状态（已有业务事实表尽可能扩展或投影，不重复导出）**：
- `observed_setting_values`（如需要新增通用投影）：`career_id,snapshot_id,object_scope,team_id,opponent_team_id,player_identity,coach_identity,slot_index,side,field_key,value_json,raw_hex,source_status,registry_version,observed_at`。
- 观察原始字段可仍存于`coaching_team_observations.observation_json`及未来Antigravity专用真实来源表；通用投影是**衍生查询**，必须注明来源，而非另一个未经审计的真相库。
- 玩家Tendencies、4 Play Types、团队训练、单个matchup个人防守等表可按访问效率使用窄表`player_tendencies`、`player_playtypes`、`team_training`、`personal_defense`；禁止读一条记录便擅自声称所有字段完整已采。
- 个体记录使用`career_id + snapshot_id + verified identity`；Playtype再加`slot 1..4`，防守再加`owner,opponent,target-player,defender,field`；个人改变归属时旧意图不能自动拿新队应用。player_id与GM查询的`batch-scoped identity`映射必须复核；`matchup_id`不得凭名字直接当通用全局ID。

**控制库（每档私有`database/saves/<save_id>/gm_control.sqlite`）**：
1. `desired_change_sets`：`change_set_id,career_id,source_batch_id,source_snapshot_id,profile_version,decision_id,version,status,created_at,change_digest,origin_model,reason`；
2. `desired_changes`：`change_set_id,action_id,target_kind,team_id,player_id,opponent_team_id,defender_id,slot,side,field_key,expected_observed_raw,target_value_json,field_registry_version,reason,dependencies`；UNIQUE`(change_set_id,action_id)`，逻辑字段冲突按**真实对象键**，非名字；
3. `approval_records`：`change_set_id,approved_digest,career_id,source_batch_id,decision_id,version,approved_action_ids,approved_scope,player_approval_reference,approved_at`；**存在一条approve记录不等于模型可自行创建该记录**，由玩家明确批准流程写入；
4. `execution_runs`：`run_id,change_set_id,digest,game_process_fingerprint,started_at,status,completed_at,readback_summary,error_code`；
5. `execution_blocks`：`run_id,storage_target_key,validated_identity,byte_mask,before_raw,expected_after_raw,readback_raw,state,journal_path`，按实际共享字节/位域块去重；
6. `reconciliation_records`：`career_id,new_snapshot_id,change_set_id,field_target,expected_applied,observed_again,comparison_status,comment`；
7. `capability_registry`（可是JSON静态文件+SQL视图）：每项`read_verified / write_verified / game_save_persisted / gm_enabled`，不把代码存在等同权限或效果证实。

**不新增第三份“观察权威”**：执行器可能读取近期观测镜像协助preflight，但数据库的`desired`不修改`league_state.sqlite`。只有下一轮`full_verified_v1`才能产生新的不可变Observed版本。

### 2.2 建议通用对象键

- `GLOBAL_GAMEPLAY(side,field_key)`：USER与CPU分开，**30队User经营不证明所有比赛球员使用USER滑块**。
- `WORLD_SETTING(group,field_key)`：赛季规则/工资/Sim/成长曲线；具有`season_scope`和UI生效时点，部分开档设置不能在月中假设可写。
- `COACH_DEFAULT(team_id,coach_identity,field_key)`；`PLAYBOOK_SLOT(team_id,playbook_identity,slot_index)`。
- `PLAYER_TENDENCY(team_id,player_identity,field_key)`；`PLAYER_PLAYTYPE(team_id,player_identity,slot=1..4)`。
- `PERSONAL_DEFENSE(owner_team_id,opponent_team_id,opponent_player_identity,defender_identity,field_key)`；**GM只准个人防守写入，整体只读**，无需再安排同一日常GM方案先Overall后Personal的写入顺序；多名个人对位可在一个批次合并。
- `TEAM_TRAINING(team_id,training_period,field_key)`；`PLAYER_TRAINING(team_id,player_identity,training_period,field_key)`、`MENTOR(team_id,player_identity,mentor_identity,slot)`。

这些都是**业务标识**，不是具体进程地址。由执行时的locator解析进程当前地址，并验证所属save/team/roster。

## 2A. 新增存档生命周期与重置（V1.1，必须实现）

### 2A.1 决策：方案二，但只允许一个活动存档

**不采用方案一“每次开档把所有SQLite中的业务数据清空”。** 推荐方案二的**物理按档隔离**：最多同时登记4个可切换工作区，实际只有1个ACTIVE。旧档不会因切换而失去球队数据、审批历史、player_pool、不可变发布批次和GM分析记忆。用户绝大多数时间只用1档时，界面只面对ACTIVE即可，模型无须管理4档数据。

**此架构已存在可复用基石，不需要开发多租户共表**：`src/save_context.py`已通过`save_paths(save_id)`生成`database/saves/<save_id>/league_state.sqlite`、`player_pool.sqlite`、`snapshots/`、`backups/`、`evaluations/`；`create_or_open_save()`由干净的`database/templates/league_template_v2.sqlite`建立新档，并在`save_metadata`验证save_id。`src/auto_pipeline_ingest.py`已调用`resolve_context(save_id)`，`scripts/run_data_update.ps1`必须提供`-SaveId`，M0`database/query_snapshots/<career>/<batch>`与`published/saves/<save_id>/latest.json`也按档隔离。

**已知实际风险**：`resolve_context(None)`还会退回`legacy-shared`根目录数据库；`monthly_snapshots.snapshot_id`基于赛季/月，不包含career，若放进一份共享事实库，A/B档相同M02会相撞、现有`ON CONFLICT`/删除可能覆盖别的档。**DEV14新入口必须拒绝隐式shared，不得将多个save_id的事实写进一份SQLite。** 保留旧CLI兼容但新控制执行强制显式/可信活动绑定。

### 2A.2 目录/绑定/schema

在每档现有目录新增：
- `database/saves/<save_id>/gm_control.sqlite`：该档私有的Desired/Approval/Execution/Journal索引/Reconciliation，不能放到全局共享`database/gm_control.sqlite`。
- `database/saves/<save_id>/workspace.json`：至少`save_id,save_instance_id,generation_id,schema_version,created_at,lifecycle_status,manifest_digest`。不同新游戏存档必须有不同save_id或generation；同名重新开档必须推新代次，旧审批一律失效。
- `database/active_save.json`：全局唯一活动指针，至少`save_id,save_instance_id,generation_id,activation_status,activated_at`，持久化时原子替换。其他非活动档允许显式只读历史查询，不得成为默认修改目标。
- 可选`database/saves/<save_id>/reset_archives/<generation>/`：老代次三库及控制日志的密封一致性备份；不同save_id不可互相恢复。

最多**4个非RETIRED的可切换存档工作区**，超限拒绝新建、不自动删档；retire保留历史且腾出名额。绝不自动删除历史`published`、已审计`query_snapshots`、旧`latest`或别档数据。游戏实例标识≠队伍标识，不能靠30队名单相同推断载入同一个真实存档。

### 2A.3 明确三种业务操作

1. **create / activate（优先，非破坏）**：`save create --save-id NEW`用现有clean template创建空事实库和新gm_control；`save activate --save-id X`只切换本地唯一活动绑定，不自动加载游戏存档、不采集、不提交GM决策、更不能自动向游戏内存写入。激活后首次状态`NEW_UNCAPTURED`，直到用户加载对应NBA2K22存档并正式触发一次`full_verified_v1`采集形成同代次快照才能执行GM决策。重复`create`不得擦旧档。
2. **switch / deactivate / retire（无破坏）**：切档前校验当前没有`APPLYING`、`PREFLIGHT_OK`、`PARTIAL_UNRECOVERED`等未解决的写入/回滚任务；检查目标库`save_metadata`、身份/版本、控制库及快照归属。`save list/status`只读；`save deactivate`不丢数据；`save retire`需玩家明确批准，历史档保持只读可恢复。
3. **reset（危险的例外操作）**：用户坚持在**同一个save_id下重开全新游戏世界**时，才允许`save reset --save-id X --dry-run`→展示将替换的三库、审批记录及归档路径→玩家对`save_id + generation + manifest digest`二次明确确认→**先密封归档，再由干净模板创建新generation**，不能执行`DELETE FROM ALL TABLES`。默认建议为新世界使用新save_id；若现有published代次协议无法识别新旧generation，则同名reset必须`BLOCKED_UNSUPPORTED_GENERATION`，直接建议创建新ID，而不是破坏旧发布数据。

### 2A.4 reset的确定性安全细节

- reset/activate/retire/create都要和`stage/apply/capture/publish/reconcile`共用生命周期互斥锁；不允许正在游戏写入时切档。模型只能调用固定CLI，不允许`--all`/`--force`/任意目录路径、裸SQL或通配清库。
- 目标存档的`league_state.sqlite`、`player_pool.sqlite`、`gm_control.sqlite`与执行journal必须保留完整一致备份；SQLite活动/WAL数据库用`Connection.backup()`创建归档，不要直接复制正在使用的SQLite文件。归档附带hash、save_id、generation、版本/最新batch/来源metadata。归档校验失败则原档完全不动。
- 多份SQLite文件没有跨文件原子替换。推荐**先准备完整新代次目录与三库，校验无误后一次提交活动manifest/指针**，或采用有持久activation journal和中断恢复的等效方案；任何程序只按已提交generation读取同一组三库。崩溃后必须恢复旧完整generation，或进入`RESET_INTERRUPTED_BLOCKED`，禁止“新league + 旧pool + 旧control”混合。
- 新generation必须清空**该档业务数据**但保留数据库Schema、静态球队目录/外键参考、合法枚举等必要模板初始值；控制库无审批、无目标、无已执行事项。人物池如果只能通过正式采集生成，创建时可为缺失/空但标`NOT_CAPTURED`，**不可偷偷拿上一代player_pool冒充新档**。
- 当前`published/saves/<save_id>/latest.json`与不可变history如果不支持generation，则绝不把上一代latest当新档；无法升级发布协议即要求换新save_id，避免使历史快照/脚本索引失效。
- 用户输入`--save-id`不是游戏内存已加载哪个save的证明。必须优先获取游戏中可验证的save实例来源/唯一锚点；若缺乏，标`GAME_SAVE_BINDING_UNVERIFIED`并阻止无人监督的正式内存写。仅以玩家显式确认和可核验源事实作为人工降级措施，执行回执必须披露无法独立唯一辨别的风险。
- 每项`change_set`绑定`save_id + generation + source_batch + decision_version + digest`；跨档同球员/同M02/同decision ID均无关联。切回旧档时不得静默执行此前挂起的已批准batch，必须针对实际载入状态重新preflight。
- 正常月度采集**绝不是reset**：保留旧M02/历史赛季数据；新档建库不修改旧档历史记录或释放旧的玩家批准。

### 2A.5 本项验收（只需合成+现有M02静态副本）

1. 创建A/B，两个档都有相同的`2021-2022_M02`与同样的球员ID，但事实、player_pool、控制库、审批与快照不串档。
2. A为ACTIVE，`activate B`成功后只改变active绑定；不写游戏、不采集、不发布，A未完成方案不能在B执行。四档限额/retire生效。
3. 没有可靠真实游戏档身份、无active、请求错档或旧generation时，`apply/capture`必须阻断；历史查询`--career A`只读不切换ACTIVE。
4. 无确认`reset A`直接拒绝；确认后仅A进入新generation的`NEW_UNCAPTURED`，B不受影响，旧A归档可回读且旧批准不可新代次执行。
5. 注入归档和新代次提交中途故障：只能看到旧完整generation或新完整generation，不可混三库；发生未恢复内存写入时切档/reset拒绝。
6. 新DEV14 CLI不允许默认`legacy-shared`，但不破坏旧版本`resolve_context(None)`的历史兼容；历史published旧代次不能成为同名新世界的当前来源。


## 3. 核心确定性管道：三个简单入口，模型不直接处理千条地址

### 3.1 阶段1：stage（仅写目标库）

输入GM/M3提出的最小`change_set`，例如只改变12名球员共18个战术相关值。纯离线`stage`：
1. 绑定现有不可变`career/source_batch`与registry版本，找事实前值；
2. 展开/标准化字段对象与合法enum、允许的`team+side+slot`、是否有字段权限，明确HOLD/NO_OP；
3. 校验同批逻辑冲突、交易后身份变更、同一共享位域重叠、OVERALL与PERSONAL的执行顺序；写前后值作为**意图**而非事实；
4. 对未改变的99项倾向**不写回**，只沿用已观测状态；不能为了“全部字段表完整”让模型复制数百人的全部数值；
5. SQLite事务把ChangeSet保存为`DRAFT/VALIDATED`，生成稳定、排序后digest与有限diff预览；**stage没有内存RW句柄，绝不执行**。

`APPROVED`仅通过已有玩家审批合同产生：模型的`approved: true`字段、聊天内容、数据库本地`status=APPROVED`都不是用户授权的替代物；旧`BatchApproval`可改造成通用`ApprovedChangeSet`，但禁止削弱`career+batch+decision+version+action_ids+digest`的绑定。

### 3.2 阶段2：apply（只有完整批准可开始写内存）

- 单命令只接受`change_set_id`与外部玩家批准令牌/参数；直接目标地址、8字节hex或任意SQL不得成为公开可写入口。
- 获取已有全局互斥锁，解析真实进程/存档版本与对象身份；所有要写对象的完整前值**先读一次**，不匹配即`STALE_SOURCE/REFUSED`，不“自动纠偏”和不偷偷调整目标。
- 将按字段的变更转为**实际物理storage block**：相同bytes / overlap bits的修改只编码一次；保留块内未批准字段，按mask安全合成，防误修改能力/潜力/徽章/合同等邻近区域。
- **在第一笔游戏内存写入之前**持久保存所有`preimages`、digest、profile、运行环境与目标块计划；先对本地计划日志完成安全落盘，然后执行。
- 批量写：按模块/球队分组，逐块检查前值、写入、立刻回读；若发生失败，停止后续，尽力按相反顺序**仅在当前字节仍为本次写入的after值时条件恢复**。无法恢复必须保留日志与`PARTIAL_UNRECOVERED`事实，不伪称全局原子成功。
- `MEMORY_VERIFIED`表示仅实时内存读回成功，不表示游戏UI点击保存/关闭设置页面、生涯存档写盘或重启后仍然有效。`GAME_SAVE_CONFIRMED`仅后续确认时声明。
- 幂等：重复提交相同`career+decision+version+digest`查询以前事务结果；**不再次盲写**。若当前内存发生变化，优先返回`REVALIDATION_REQUIRED`或错误，不按缓存认定状态依旧。变更批次数千字段时允许按**已批准子批次**分批，不能让轻量模型重新生成一批新授权数据。

### 3.3 阶段3：capture / reconcile（采集和回执）

- **唯一正式采集入口保持**`scripts/run_data_update.ps1`，玩家触发`full_verified_v1`。Antigravity字段的读逻辑通过新增adapter进入已有`auto_pipeline_ingest.py`及`source_catalog.json`。
- 一个RO游戏会话读取当批要求的所有字段；校验已证球队集合、球员身份、值域、字节合法性，记录来源统计与未知字段；不把stage/apply时的Desired与Reported写成游戏Observed。
- 继续旧`Connection.backup()`双库一致性归档、同一来源审计和只读副本安装；若新增世界/战术源未认证，可标部分来源`NOT_OBSERVED`，不伪造新批数据，也不因某个非必需源缺失就无止境重写全采集框架。只有明确认定必需的源才由既有fail-closed规则阻断发布。
- 新观测批次保存后，`reconcile`比对“最近一个批准方案的内存读回”与“后续独立游戏观测”；允许`MATCHED`、`DRIFT_DETECTED`、`NOT_OBSERVED`、`IDENTITY_CHANGED`、`GAME_MANAGED_EXPECTED`等。**只报告偏离不自动重写**，避免与ACE、轮换分钟、疲劳和原生自动训练冲突。
- Web GPT继续使用`gm_data_query.py`和同批查询副本；扩充`world/gameplay/tactics/tendency/training/defense`只读域，按team/player/field分页，不将30队×99项读进一次模型上下文。默认20、最多50、20KB预算等既有M0约束不改。

## 4. 共用NativeFieldRegistry与编解码契约

建议`src/gm_state_io/`下拆分（最终命名由Codex决定，遵守现有目录风格）：
- `registry.py`：字段唯一编码字典、range/enum、当前profile版本、是否可读/可写、所属对象、页面和原生source adapter，不主动连接游戏；
- `models.py`或`schema.py`：ChangeSet、ExecutionRun、Observation typed DTO及SQLite migration；
- `plan.py`：`stage / validate / digest / conflict grouping`，纯离线且无任何RW/import游戏依赖；
- `codec.py`：注册/复用`coach_codec.py`、`defense_codec.py`及Antigravity的个人Tendency/训练native codecs。**同一codec提供`decode(raw)`和`encode_patch(raw, changes)`**，禁止采集/执行各有一份意义不一致的定义；
- `executor.py`：只在真实玩家批准后取得RW；批次锁、写前核对、journal、条件恢复、结果回执；
- `capture_bridge.py`：调用现存read-only adapters并输出统一DTO给原`auto_pipeline_ingest.py`；
- `reconcile.py`：离线比较已批准执行回执与新不可变batch；
- `scripts/gm_state_io.py`：单命令入口（见下面CLI），不必在Web聊天直接执行本机权限操作。

**Native字段的“字节编码真实”与“游戏效果真实”分别验证**：如`CPUAttributeBoost`或原生模拟/成长曲线，缺字段语义不能给GM假作用解释，缺写入认证不能`gm_enabled=true`。

**重要保护**：个人Tendency是新增获准的赛前战术修改对象；普通GM对**球员原始Ability、Potential、Badge、身高、速度、合同与伤病**没有泛化写权限。合同/交易走原有专门获批执行业务；历史重力例外与本通用设置执行器隔离。全局Gameplay Attribute sliders是“比赛全局乘性规则”，**不等于直接写某个球员Attribute**，需以`GLOBAL_GAMEPLAY`显式权限处理。

## 5. CLI（推荐对模型暴露的极少固定命令）

`python -B scripts/gm_state_io.py registry [--domain ...]`：只读当前生效字段与能力；
`python -B scripts/gm_state_io.py stage --career ... --source-batch ... --proposal ...`：只操作控制库，输出change_set_id、字段差分、digest、需要的人类批准；
`python -B scripts/gm_state_io.py validate --change-set ...`：纯离线检查，显示不支持/过期/冲突；
`python -B scripts/gm_state_io.py preflight --change-set ...`：当前游戏RO读与预计blocks，绝不改变；
`python -B scripts/gm_state_io.py apply --change-set ... --approval ...`：**仅用户明确批准的完整摘要可运行**；验证后才取得RW；
`python -B scripts/gm_state_io.py receipt --change-set ...`：受限执行日志摘要与详细本地日志位置；
`python -B scripts/gm_state_io.py reconcile --career ... --batch ...`：对新正式快照做离线对账；
`python -B scripts/gm_state_io.py rollback --change-set ... --approval ...`：仅在既有条件回滚规则与授权边界允许下执行。

这些是**推荐新接口，尚未实现**。为了不破坏旧用户工作流，`scripts/coaching_batch.py`和`scripts/coaching_snapshot.py`等入口可调用新内核，也可保持原样由新内核复用其内部函数；无须强制迁移既有历史审批数据。

### 输出范例（说明字段语义，不是实际授权）

`stage`返回：
```json
{
  "change_set_id": "DEV_ONLY_SAMPLE",
  "career_id": "sample_save",
  "source_batch_id": "sample_batch",
  "status": "VALIDATED_PENDING_APPROVAL",
  "actions_requested": 18,
  "actions_effective": 16,
  "unchanged": 2,
  "native_blocks_planned": 11,
  "digest": "sha256-of-canonicalized-plan",
  "approval_required": true
}
```

`apply`返回：
```json
{
  "change_set_id": "DEV_ONLY_SAMPLE",
  "status": "MEMORY_VERIFIED",
  "blocks_preflighted": 11,
  "blocks_written": 11,
  "blocks_readback_verified": 11,
  "persisted_in_save": false,
  "result_is_game_observation": false
}
```

示例仅表示`11个块更新了16个有效字段`，不是声称目前真实游戏已经有这个结果。

## 6. 数据与身份兼容/批次部署策略

- 真正team_id来自同一已校准NBA球队目录，支持非连续ID；`player_id`、球员池slot、`face_id`、`coaching.matchup_id`含义不可混用；如果交易后已换队，旧计划必须拒绝。
- Antigravity原生字段含`coach_tactics_profile`、`memory_field_profile`、DEV12本地技能与训练模块；**只把已经证实的字段写进可执行列表**，新增别的字段可先只读。
- 世界静态设置/全局Gameplay、球员倾向、训练、教练和逐人防守各自不同目标解析器，但输出相同`native storage blocks`和变更回执；对抗USER/CPU保持双side；成长曲线只允许经批准的世界级PROFILE变更，不算日常球队经营。
- 对**本队独占的`PLAYBOOK_SLOT`**、`PLAYER_PLAYTYPE`与`PLAYER_TENDENCY`和多球员`PERSONAL_DEFENSE`建立变更依赖/身份约束。**普通GM不修改`PlaybookID`和`OVERALL_DEFENSE`**；只有正式换帅后必要且获另行批准的原生独占书绑定可能涉及BookID修改，换帅后必须先重新采集。共享原生Book一律阻断单队改槽，禁止跨队影响。
- SQLite控制库写入可以用事务；运行时游戏不能单事务。源批次发布与控制状态不组成跨SQLite/内存的伪分布式事务，改用明确阶段状态与日志、重试的幂等行为。
- 世界配置此前已有Antigravity制作的可复用原值表，待其本地资料由玩家/Codex提供后按`registry`导入；文档未提供的raw默认值不编造。
- 旧快照保持不可变；代码和schema迁移向前兼容，可通过显式schema_version执行迁移。不因这次创建第三SQLite就重做M0安全ACL/静态双库路径。

## 7. 开发切分：A/B/C加D存档管理，由Codex同一任务完成

### DEV14-A：规范化字段与控制数据模型

实现：
1. 统一registry（优先教练19默认、18整体防守、一个USER/CPU全局field以及一项个人Tendency），支持加载已有profile；
2. SQLite控制库schema和迁移，`observed/desired/applied`严格分离；对同源只读观测建立小型字段投影；
3. `stage/validate` CLI，少量稀疏GM字段修改转稳定digest/逐项差分/物理块组；断言UNKNOWN不能误变为50、未获批不能写；
4. 制定扩展接口，后续任何Antigravity原生字段都可注册而非一模块一套脚本。

完成标准：合成1队/2名球员/同一字节多个教练field/USER/CPU两个side的stage变更正确且不修改游戏内存/真实事实库。

### DEV14-B：生产级通用批准批次执行与适配器接入

实现：
1. 抽取/复用现有`CoachingBatchExecutor`的批准摘要、preflight、block merger、journal、读回/条件恢复，不破坏既有19/18；
2. 把main原有或Antigravity整理后已证的`global settings、world settings、player playtype/tendency、matchup-personal、training`分批注册为可读或可写；**未在本地提供的功能保留adapter接口，不以找不到训练源码强阻塞完成共同引擎**；
3. `apply/receipt/rollback`仅绑定完整玩家授权且类型权限许可，执行范围按原生已认证字段逐项开放；
4. 失败中途停止/恢复/部分未恢复报告；批次幂等与人类批准范围严格对齐；
5. 对数千字段批量采用一趟进程对象解析/一次RO preflight、同字节块合并、逐块回读和少量日志摘要；不让模型重复发一千条写入命令。

完成标准：只在**合成MemoryBackend/隔离环境**验证覆盖单字段成功、共享位域合并、旧源拒绝、未批准拒绝、失败一笔的条件恢复/失败回执；旧Coaching批次核心路径仍然可用。**不因完成开发而对正式NBA2K22保存状态执行RW**。

### DEV14-C：只读采集扩充、静态发布与状态对账

实现：
1. Antigravity已读出的原生世界/游戏平衡/战术/个人Tendency/训练字段，通过registry的decoder与适配器进入现有`full_verified_v1`源框架，不重复开发多个capture入口；
2. 每次由玩家显式触发时，按可用源产生同批SQLite事实、coverage/read status；写入前保留来源审计、SQLite backup一致快照机制和历史latest不可覆盖策略；
3. 在已有`gm_data_query`添加分域限额查询，让GM V4/DEV13按队和球员消费，而非一次取上千字段；
4. `reconcile`以新独立观测比对已批准MEMORY_VERIFIED变化，输出MATCHED/DRIFT/UNKNOWN/IDENTITY_CHANGED/GAME_MANAGED等，不自动重写游戏；
5. 记录哪些Adapter目前仅`DISCOVERED`、`READ_ONLY`、`MEMORY_WRITE_VERIFIED`、`PERSISTENCE_CONFIRMED`，不能因注册存在就让GM假定已生产可用。

完成标准：合成全量采集一套 + 已有M02静态SQLite离线只读校验，不重采真实比赛/跨赛季模拟或大规模端到端游戏测试；生产新数据随下次玩家触发真正的full_verified_v1自然出现。

### DEV14-D：单活动存档、开新档与安全重置（新增必做）

直接实现第2A节的`save list/status/create/activate/deactivate/retire/reset`接口和每档`gm_control.sqlite`，复用现有`src/save_context.py`、M0按career快照隔离及唯一采集入口。优先无损`create + activate`，不要开发四套互不相同的执行器；危险同名reset可以在历史published代次不兼容时阻断并要求新save_id，不准冒险清库。

完成标准：两存档同名M02数据不会相撞、仅活动档可执行、切档无需删除数据、reset写前有完整备份与严格确认、失败可恢复/明确阻断，旧审批不会继承到新代次。使用定向合成测试，不触碰正式游戏。


### 交付物清单

- 代码：`src/gm_state_io/`共享registry、schema/stage/validator/executor/capture/reconcile及`scripts/gm_state_io.py`（或更贴近仓库的等价模块名称）；
- DB：`database/gm_control_schema.sql`和实际迁移逻辑；每档`database/saves/<save_id>/gm_control.sqlite`私有化；已有事实表必要增量迁移；README描述按游戏页面逻辑视图而非30物理表；
- 存档生命周期：复用`src/save_context.py`、活动manifest/generation、开新档/切档/安全reset命令与两档隔离验收。
- 文档：`docs/DEV14_STATE_IO_RUNBOOK.md`（字段登记/CLI/审批/异常恢复/数据源/部署步骤）；`docs/development_reviews/DEV14_ACCEPTANCE.md`（仅直接相关的有限检查及实际未验收项）；
- 集成：`config/source_catalog.json`能力说明；`web_gm/memory/DEVELOPMENT_CURRENT.md`索引；`docs/development_tasks/DEV_20261019_13_M3_TACTICAL_DECISION_INTEGRATION_V1.md`补充DEV14依赖（只写说明，DEV13代码开发不在本任务范围）；
- PR：独立DEV14分支/PR，具体提交、影响路径、离线运行示例和未实现的原生字段列表。**不自动合并**。

## 8. 限定的直接相关验收清单（避免测试无限扩张）

1. **两side**：USER/CPU同名global slider不串值；30队用户经营权不会被错误映射成USER比赛控制。
2. **历史身份**：真实非连续team_id、同名字球员、交易后旧player/team身份失效；不同career或source_batch不能混用。
3. **共享bitfield**：两条字段同一block合并后保留未批准bit；个人Tendency不覆盖Ability/Potential/Badge，个人防守不能被一次overall变更无声抹平。
4. **数据三态**：只读采集→Observed；stage→Desired（事实库原封不动）；完整批准+preflight+读回→Applied Memory（不得标存档已永久确认）。
5. **模型权限**：只提供`approved: true`、裸地址或本地改SQL状态都无法绕过玩家批准；无法认证字段的`READ_ONLY`不可以被执行。
6. **失败与重复**：中途失败停下、日志可查、可条件恢复或标部分未恢复，重复批次不二次盲写；旧Coaching CLI仍可正常运行。
7. **采集对账**：后续观测与既有applied不一致时记录DRIFT而非自动写回；UNKNOWN保持NULL；GM查询有batch与分页来源约束。
8. **交付不越权**：本轮不运行正式游戏RW、不生成正式30队决策、不启用V4、不合并M3 Draft PR#4、不替代Antigravity已独立做的DEV12游戏定位与训练系统。

**直接相关合成测试+已有M02静态副本足够验证DEV14工程底座**。若源模块在Antigravity本地尚未整理到GitHub，交付可用框架、示例适配器、明确BLOCKED_SOURCE清单即可，不以完成每个100+成长曲线证明为前提。后续真实体验发现问题再修，遵从既有用户开发规范。

## 9. Codex执行指令（供新窗口直接转发）

- 仓库：`chris2gao/nba2k22-gm-engine`。
- 权威任务文档：`docs/development_tasks/DEV_20261019_14_DETERMINISTIC_STATE_IO_ENGINE_V1.md`。
- 请直接完成A/B/C以及D存档管理四项工程，在**独立工作分支**实现并提交PR；保留已有M0/M1/M2、M3 Draft和19+18教练执行器的结构；不征求重复技术方案确认。
- 先看现有M0数据库与`src/coaching_batch_executor.py`，**从它们抽取最小可行公共实现，而不是另建庞大数据库服务或一堆独立字段脚本**。
- 你负责确定性数据库和执行/采集内核；Antigravity后续提供字段目录和本地原生适配器。缺失的原生数据明确标BLOCKED，而不编造地址、不为其停工。
- 正式游戏内存写入与全量采集只有玩家另外明确触发时才执行；本任务授权开发和合成/静态副本验证，**不授权影响当前存档**。
- 完成后回复：源码PR、schema/字段注册、包含save create/activate/reset dry-run在内的CLI示例、两档隔离与中断恢复定向测试、哪些域已接入、哪些域因Antigravity本地文件未到位、下一步如何供DEV13的GM决策使用。

**成功定义：无论30队涉及几十还是上千项调整，模型只提交少量结构化意图与获批批次ID；由确定性程序读取正确事实、执行可认证字段、核对游戏实际结果并给GM提供可回查的可信下一批次事实。**
