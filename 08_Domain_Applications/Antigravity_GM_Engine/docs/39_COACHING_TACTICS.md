# 教练战术接口 V1

**历史接口文档：下文描述 DEV06/V1 的状态，不代表 V2 当前门槛。** DEV07 后续已新增指定对手整体防守、批次执行、来源集成代码及五项数值设置验收；当前入口见[执行手册40](40_COACHING_EXECUTION_RUNBOOK.md)、[GM手册](../web_gm/manuals/GM_COACHING_OPERATIONS.md)和[状态34](34_BASELINE_CURRENT_STATE.md)。旧 `VS_OPPONENT` 预设仍不执行；新的 `VS_OPPONENT_DEFENSE` 具有独立合同和经验证的整体批量语义。以下 V1 不可替代 V2 的字段矩阵或审批。

2026-10-17，DEV-20261017-06。**默认六项 POE 已完成隔离局写入、玩家界面确认、保存后真实进程重启及恢复内存原值，技术接口可在玩家批准具体方案后使用。** 六项 production_enabled=true，其余字段保持各自限制；这不代表任何正式局已经获批或执行。玩家明确目标是内存实时修改，Computer Use仅为辅助。完整状态见 [字段矩阵](development_reviews/DEV_20261017_06_COACHING_FIELD_MATRIX.json)、[执行器验收](development_reviews/DEV_20261017_06_COACHING_EXECUTOR_ACCEPTANCE.md)及[能力清单与对手方案评估](development_reviews/DEV_20261017_06_COACHING_CAPABILITIES_AND_MATCHUP.md)。

## 范围与对象

玩家指定界面是“终极联盟 → 执教 → 教练比赛计划”（MyLEAGUE → Coaching → Coach Gameplan）。玩家已确认步行者六项中文选项全部对应测试目标。必须分别看待球队主教练默认配置、指定对手 Gameplan、比赛内临场设置；默认修改在指定对手页面出现，不能证明独立对手覆盖已实现。

| 模块 | V1 当前能力 | 正式执行 |
| --- | --- | --- |
| 默认六项 POE | 原生枚举、读取、提案、共块一次受控写入/回读/条件恢复；PHI和AI IND实测，IND六项保存/真实重启通过 | EXECUTOR_IMPLEMENTED_READY_FOR_PLAYER_APPROVAL |
| 五项 Sim | 完整原生 bit/enum，支持编码与只读；SimPace 2→4→2内存实测 | 禁用；尚未独立保存认证，其他四项未写入验收 |
| PreferredSystem / ActiveSystem | 八种原生体系，独立掩码编码与只读 | 禁用；不改熟练度或人物能力 |
| PlaybookID | 当前加载目录校验，可编码现有有名战术本选择 | 禁用；未写入验收，不改共享 68 CRC 槽 |
| 六项教练滑块 | BenchDepth、RunPlayTendency、ZoneUsage、BenchUtilization、Tempo、HelpDefense 只读 | 禁用；真实单位/菜单范围未完成认证 |
| 四个 Freelance | 原生 enum/位域只读 | 禁用 |
| 指定对手 Gameplan | 按 owner ID 扫描、校验对手集合、排序、离线预设 | MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED |
| 18 项防守、普通/高级轮换 | 普通记录读取、原生防守掩码与 enum CRC；高级轮换保留缺口 | 禁用；人物引用、约束与激活机制未验收 |

六项默认 POE 共用 `COACHDATA+0x13C` 的四字节块。依次为 Defense bit0、Defense2 bit5、Defense3 bit10、Offense bit15、Offense2 bit20、Offense3 bit25，均 width5。保留 bit30/31。同一方案影响同块的多项修改合并为一次四字节写入，写前比对完整块，写后比对完整块；不逐字段覆盖别人的修改。

五项 Sim 共用 `+0xF4`：Pace bit0/width3，Press bit3/width2，HelpDef bit5/width2，OffReb bit7/width2，DefReb bit9/width2。它们与 Tempo 和六项 POE 分别建模。体系在 `+0x108` 的 bit16/width4 与 bit28/width4；合法值仍只有原生枚举 0–7。其余位和同块 PlaybookID 均受掩码保护。

## 安全边界

`StrategyManager.set_team_strategy` 无条件报 `LEGACY_TEAM_POE_OFFSETS_REVOKED`。历史 `poe_*` 字段保留原始观测，但 GM 不再把它们认作战术。bootstrap 仍需原有 `--approve-game-writes` 才能改全局设置/票价；旧战术模板跳过，不映射到新枚举。

定位从当前模块原生 getter 和反射结构开始，每次读取当前目录、全部核心球队 ID、唯一主教练及岗位双向引用，核对名单成员和所属球队。当前自定义名单替换了固定 Jordan 槽位，因此新教练定位不依赖固定历史姓名/槽位，也不读取旧堆缓存。PID、进程创建时间、PE 时间戳/映像大小、原生元数据、当前球队/教练/名单指纹和加载战术本内容均参与执行前检查。

**写入前必须退出教练比赛计划编辑页。** 实测在编辑页打开时写入 POEOffense2=7，立即回读成功，退出/重开页面后却被游戏改回8；玩家先退出编辑页，再由脚本写7并稳定回读，重新进入后玩家确认显示耐心进攻。执行入口要求独立的 `PlayerApproval.coach_editor_closed_confirmed=True` / `--coach-editor-closed`，缺失时任何进程句柄都不开。这是玩家确认的当前操作状态，不是自动检测菜单，也不依赖Computer Use。

career_id、游戏赛季/日期仍由玩家给出，系统不能自动证明存档名称。测试局允许日期未知并明确标记；正式快照要求 ISO 日期。重启、读档、换教练、换名单或完整前值改变后，旧方案停止，重新读取和形成具体方案；不能把新快照偷偷塞回已批准旧方案。运行时地址只在本地日志中使用。

提案只允许 PROPOSED 和 `execution_authorized:false`。嵌套的 approved/player_approved/executed/write_authority 等授权声明被拒绝。执行角色根据聊天中的真实批准，单独提供 career/decision/version/action/digest；CLI 参数是操作者传递批准的接口，不是自动取得玩家同意的机制。

每次执行一个球队的一个具体 action，可以在其多个已确认共享块内修改。**V1 没有多球队原子批次 CLI**；不能把循环调用单项接口当成全批次预验/原子事务。正式批次业务入口仍需补全独立预验与依赖协议。

持久 preimage、命令/源码指纹、外部批准范围、前后块和回读写入本地事务日志；重复 career+decision+version+action 返回既有结果，并标 `current_state=NOT_REVALIDATED_CACHED_RECEIPT`，不能把历史成功当作当前游戏值仍未变化。失败只在身份仍一致且当前块仍等于本执行器目标时恢复；并发变化保留并报 PARTIAL_UNRECOVERED。崩溃遗留锁或不完整事务须人工审阅，不能删除日志重新执行。

## CLI

从本仓库根目录运行。所有命令提供 `--help`。输出/事务目录只能在当前仓库 `_exports/`；不会改 SQLite、published、latest 或生产来源时间戳，不会自动发布或模拟比赛。实机只读需要能读取游戏的 Windows 执行权限；代码不会自动绕过权限错误。

```powershell
# 仅在玩家明确触发的教练读取任务中使用；正式快照的日期由玩家确认。
python -B scripts/coaching_snapshot.py --career-id SAVE_ID --source-batch-id SOURCE_BATCH --game-season 2021-2022 --game-date 2021-11-20 --output _exports/coaching/snapshot.json

# 隔离开发局日期可未知，必须实际载入玩家确认的测试副本。
python -B scripts/coaching_snapshot.py --career-id TEST_SAVE --source-batch-id DEV_ONLY --game-season TEST_CONTEXT --isolated-test --output _exports/coaching/test_snapshot.json

# 以下数值只说明接口，不是对任意球队的经营方案或批准。
python -B scripts/coaching_validate.py --snapshot _exports/coaching/snapshot.json --team-id 20 --decision-id EXAMPLE_ONLY --version 1 --action-id A01 --set POEOffense=2 --expected-effect "具体获批风格；模拟效果待玩家月份评估" --output _exports/coaching/plan.json
python -B scripts/coaching_validate.py --snapshot _exports/coaching/snapshot.json --proposal _exports/coaching/plan.json

# 默认纯离线 dry-run，无进程句柄，返回完整 prepared_blocks 与 plan_digest。
python -B scripts/coaching_execute.py --snapshot _exports/coaching/snapshot.json --proposal _exports/coaching/plan.json
```

仅当对应字段已经完成验收并另有玩家具体批准，才由执行角色添加 `--execute --approve-career-id SAVE_ID --approve-decision-id DECISION_ID --approve-version VERSION --approve-action-id ACTION_ID --approve-plan-digest DIGEST --coach-editor-closed`。**当前仅默认六项POE可通过正式字段门槛，独立批准仍不可省略。** 隔离技术验证另需测试快照和 `--test-save-confirmed`；不能用这个开关冒充正式局是测试局。`--rollback` 使用同一方案、同一快照、同一批准和同一 state-root，且前提是已存在 EXECUTED_VERIFIED 日志；仍只做条件恢复，不承诺跨重启恢复。实际跨重启恢复采用新进程重新校准、新快照和独立恢复动作，不复用旧地址。输出回执用 `--output _exports/.../receipt.json`。

对手预设在 `coaching_validate.py` 增加 `--opponent-team-id`，生成 `VS_OPPONENT`；任何执行都被阻断。`gameplan_codec.py` 是独立字节布局读取器，唯一写入入口主动拒绝，绝不把 COACHDATA 的 packed 布局用于 Gameplan，也不修改 IsInUse。

GM 网页离线包装方案若调用既有 `gm_core.decisions.validate_proposal`，须附完整 `coaching_plan` 和对应 `coaching_snapshot`，decision/version/career/batch、球队缩写及 ID 必须一致。旧 `changes: [{field:poe_off_pace,value:...}]` 合同已撤销。仅用独立 coaching_validate 的外部文件也可进行离线验证，不会导入游戏模块。正式源 JSON 的生产集成另行开发，本次没有把测试快照上传成正式源事实。

## UI 查证与后续验收

玩家当前键位说明：LF1/RF1 为减号/加号（必要时数字小键盘）；LF2/RF2 为 `[` / `]`。这些是玩家给出的当前配置线索，尚未由截图/按键结果确认，不硬编码为所有机器的通用键位。

检索找到 [NBA2K22 官方 PC 手册](https://cdn.2kgames.com/manuals/nba2k22/PC/2KSWIN_NBA2K22_PC_Online_Manual_ENG.pdf) 的键盘/控制表；它主要描述比赛控制，不能证明当前教练菜单分页键或存档接受情况。另有作者本人录制的 [Coach2K Coach Gameplan 使用及保存说明](https://www.youtube.com/watch?v=HeBLVrN-7uc)，发布于 2019 年，只能作为旧版本菜单研究线索，不能替代本次 PC 2K22 实机。未采用 2K20/PS5 MyNBA/后续游戏的设置推荐或数值作为当前写入依据。

实际验收由玩家操作保存/重启、脚本内存核对完成：PHI进攻重点5→2已持久；AI控制的IND六项同时修改，玩家改为控制IND后确认全部对应，保存完全退出重启后六项仍在。随后用新进程独立恢复动作一次写回六项原值；30队24个已知教练字段全部恢复。玩家明确停止额外重复保存重载，因此恢复后的再次落盘不作已验证声明。原始事务和完整字节核对留本地，公开脱敏证据见矩阵。

指定对手Gameplan仍仅只读/预设。原始870记录的IsInUse均为0，但原生UI对部分对手POE字节产生过变化，不能凭0断言已禁用，也不能猜写1。所有比赛效果保持 SIM_EFFECT_PENDING_PLAYER_MONTH，玩家正常运行一个月后分别触发采集、分析、GM评估。
