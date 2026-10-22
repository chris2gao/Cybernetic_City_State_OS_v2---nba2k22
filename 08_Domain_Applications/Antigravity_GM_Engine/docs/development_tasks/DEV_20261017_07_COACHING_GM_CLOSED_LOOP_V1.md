> **此V1已被2026-10-17最新玩家指令取代，禁止按此文件旧范围开发。** 当前有效规范为 [DEV-20261017-07 V2：19项默认教练战术＋指定对手整体防守](DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V2.md)。重要变更：五项独立Sim参数**不属于GM教练功能**；除了已认证的六项POE，主教练体系2/手册1/六教练滑块/四套优先级Freelance是**必须开发**；指定对手页面的整体防守理念同属正式开发范围；取消一切不必要的游戏比赛效果测试。V1中的“其余18项均可选/匹配防守未来再做/六POE即可完工”仅保留为历史陈述。玩家仍需单独批准每次正式游戏写入。

# DEV-20261017-07 — NBA2K22 GM 教练战术系统闭环集成（30队批量 + 来源发布 + GM/执行双手册）

- 创建：2026-10-17；责任分工：Web GPT DEVELOPMENT（规格/独立审查）、Codex DEVELOPMENT（代码/Windows安全验收）、Web GPT GM（球队战术决定）、玩家（具体审批/触发）、Codex EXECUTION（批准后受控写入）。
- **状态：SPEC_PUBLISHED / CODEX_IMPLEMENTATION_PENDING / NO_NEW_GAME_APPROVAL**
- 仓库 `chris2gao/nba2k22-gm-engine`；已存在基础提交 `5daeed8dc0001b5052dce1cfc97d6c22ee9317c3`、[PR #1](https://github.com/chris2gao/nba2k22-gm-engine/pull/1) ，目前仍 OPEN，尚未合并至main。
- Codex V1 证据文档（必须先读）：`docs/39_COACHING_TACTICS.md`、`docs/development_reviews/DEV_20261017_06_COACHING_CAPABILITIES_AND_MATCHUP.md`、`docs/development_reviews/DEV_20261017_06_COACHING_EXECUTOR_ACCEPTANCE.md`、`config/coach_tactics_profile.json`（在 PR head 分支）。
- 最新用户要求：**快速模拟比赛效果验证不需要，也不能再当开发完成门槛**；需要**30队受控批量执行**、**正常数据采集自动包括并发布教练战术来源给Web GPT GM**，并提供**两本互相匹配的正式手册：GM可决策功能手册、执行模型按玩家批准批量写入的手册**。用户明确要先看其余18项默认字段的详情，**尚未逐项批准它们作为生产可写范围**；本任务不能强行将18项或单一对手Gameplan全部开放写入。
- **正式完成定义**：六项已验收主教练默认POE + 技术可靠的多队批量事务 + 数据源随玩家正常采集/显式发布而自动同步 + 两份可直接用于GM/执行基线的已验收手册 + 本地与端到端技术验收。战绩/胜率/月度模拟效果实测**不是完成条件**，不再要求等玩家游戏一个月才认定“教练系统可用”。
- 游戏写入权限不变：开发和测试存档最小验证可做；正式局只有具体GM提案/版本/行动清单经玩家明确批准后，Codex EXECUTION才可执行；源更新、GM分析、执行仍须玩家各自独立触发。不触碰普通球员能力、潜力、徽章、倾向、MC成长或全联盟模拟滑块。

## 0. 范围边界：24项默认主教练字段中，6项生产可写，18项尚未生产放行

### 已开放的六项（主干必须保留/批量复用）
`POEOffense`进攻重点、`POEOffense2`进攻节奏重点、`POEOffense3`进攻篮板、`POEDefense`防守重点、`POEDefense2`防守身体对抗/侵略性、`POEDefense3`防守篮板/转换。全部使用`COACHDATA+0x13C`共享uint32六组5位，保护保留位30、31并按字段独立原生枚举校验。PR V1已在隔离局按玩家UI确认、真实重启及恢复技术验收，**不等于正式存档已获授权被修改**。

### 剩余18项（全部详细列出，供玩家看后决定扩展范围）

| # | 原生字段 | 中文含义 | 已知offset/位域 | 合法范围或已知缺口 | PR V1状态 |
|---:|---|---|---|---|---|
| 1 | `SimPace` | 独立模拟节奏 | COACHDATA +0xF4，bit0,width3 | 0 VERYLOW、1 LOW、2 AVERAGE、3 HIGH、4 VERYHIGH | 仅内存修改与恢复验证，存档重启未独立认证，生产禁用 |
| 2 | `SimPress` | 独立模拟防守压迫 | +0xF4，bit3,width2 | 0 LOW、1 AVERAGE、2 HIGH | 编码已实现，实机单项待验 |
| 3 | `SimHelpDef` | 独立模拟协防倾向 | +0xF4，bit5,width2 | 0 LOW、1 AVERAGE、2 HIGH | 同上 |
| 4 | `SimOffReb` | 独立模拟进攻篮板 | +0xF4，bit7,width2 | 0 LOW、1 AVERAGE、2 HIGH | 同上 |
| 5 | `SimDefReb` | 独立模拟防守篮板 | +0xF4，bit9,width2 | 0 LOW、1 AVERAGE、2 HIGH | 同上 |
| 6 | `PreferredSystem` | 教练偏好体系 | +0x108，bit16,width4 | 0 Balanced、1 Grit & Grind、2 Pace & Space、3 Perimeter、4 Post、5 Triangle、6 Seven Seconds、7 Defense | 编码已实现，实际加载/覆盖关系未验证 |
| 7 | `ActiveSystem` | 实际激活体系 | +0x108，bit28,width4 | 同前0–7 | 编码已实现，实际加载/覆盖关系未验证 |
| 8 | `PlaybookID` | 教练战术手册选择 | +0x108，bit8,width8 | 仅当前进程加载的、可识别名称的战术本，动态合法ID，不是任意0–255 | 编码已实现，写入/保存未单独认证 |
| 9 | `BenchDepth` | 替补深度 | +0xDE，8bit | 存储宽度已知，真实界面合法范围/单位未知 | 只读 |
| 10 | `RunPlayTendency` | 运行战术倾向 | +0xE0，8bit | 范围/单位未知 | 只读 |
| 11 | `ZoneUsage` | 联防使用倾向 | +0xE2，8bit | 范围/单位未知 | 只读 |
| 12 | `BenchUtilization` | 替补使用程度 | +0x138，8bit | 范围/单位未知 | 只读 |
| 13 | `Tempo` | 教练进攻节奏滑块 | +0x148，bit9,width8 | 范围/单位未知；不同于SimPace及POEOffense2 | 只读 |
| 14 | `HelpDefense` | 教练协防滑块 | +0x148，bit17,width8 | 范围/单位未知；不同于SimHelpDef | 只读 |
| 15 | `FreelanceType` | Freelance方案槽1 | +0xFC，bit25,width6 | 原生枚举标签/四槽激活及顺序语义尚未认证 | 只读 |
| 16 | `FreelanceType2` | Freelance方案槽2 | +0x148，bit26,width6 | 同上 | 只读 |
| 17 | `FreelanceType3` | Freelance方案槽3 | +0x15C，bit3,width6 | 同上 | 只读 |
| 18 | `FreelanceType4` | Freelance方案槽4 | +0x15C，bit9,width6 | 同上 | 只读 |

- 5 Sim + 2 System + 1 Playbook = 8项已可编码但未正式验收开放；6滑块+4Freelance=10项只读。
- 若玩家后续决定扩展18项，优先将前8项逐字段验证合法UI/写入/保存重启/原值恢复，成功后单独提高`production_enabled`并更新手册；后10项先找合法范围和关系。**上述任何“可编码”均不等于可批量正式写入**。
- Gameplan/独立29对手战术、18项对手防守、轮换不计入上述“24项主教练默认字段”，本版仍为只读与离线预案。尤其`IsInUse=0`不代表肯定失效，不能猜启用。

## 1. P0 — 多队批量受控执行（用户明确必需）

### 1.1 批量方案模型
在单队`src/coaching_executor.py`基础上新建独立批处理入口，例`scripts/coaching_batch_execute.py`及`src/coaching_batch_executor.py`。单个`batch_id`/ `decision_id`/ `version` 和**整批规范化内容digest**绑定1–30个`team_action`；每个队伍最多一个可编辑动作或按字段归并，一个动作可改任意已`production_enabled=true`字段（初期六POE）。30队GM可给`HOLD`队伍**不产生写入动作**，但保留只读审计记录（如用户要求30队都复核）。不引入策略值之外的player能力或联盟滑块字段。

参考只做schema示例（非真实玩家批准）：
```json
{
  "schema_version": 1,
  "operation": "COACHING_BATCH_CHANGE",
  "batch_id": "TACTICS-2022-M02-R01",
  "career_id": "PLACEHOLDER",
  "source_batch_id": "FROZEN_SOURCE",
  "coaching_snapshot_id": "FROZEN_TACTICS_SNAPSHOT",
  "game_season": "2021-2022",
  "game_date": "2021-11-20",
  "policy_id": "PLAYER_RULES_20261017_V3",
  "decision_id": "GM-COACHING-DECISION-V1",
  "version": 1,
  "status": "PROPOSED",
  "team_actions": [
    {"action_id":"TAC-A01","team_id":null,"coach_identity":null,
     "scope":"COACH_DEFAULT","changes":[{"field":"POEOffense","before_raw":null,"after_raw":null}],
     "old_blocks":{"0x13c:4":null}}
  ],
  "expected_effect": "Only team tactic configuration; no game-results promise",
  "execution_authorized": false
}
```
格式中null是示例占位，真实提案必须从已发布来源和只读快照绑定球队/教练/整块原值；digest不能包含随运行生成的绝对指针，不能用提案内的`approved`字段获得权限。可复用已有单队提案JSON做`team_actions`，但须有整个批次审批摘要/单次事务含义，不能把多个单队CLI直接包一层普通循环当“原子批量”。

### 1.2 明确“逻辑原子”而非虚假硬件原子
**NBA2K22进程内跨30个COACHDATA对象没有单个可供脚本调用的原生原子提交指令。** 因此必须实现**逻辑事务+事前全部验证+失败条件回滚+显式部分失败状态**，不得承诺真正物理同一瞬间改变30队。

严格分期：
- `DRY_RUN`：纯离线，输出30队提案完整性、每队变更名单、白名单、合法值、整块旧值、审批摘要、是否缺新数据/未验收字段；不连接任何进程。
- `PREPARE`：玩家明确授权执行窗口之后，先以只读内存重新校准当前进程，确认save/season/current game date尽可能可知、全部队伍当前主教练与来源snapshot身份、名单指纹、原生metadata、加载手册、目标位块old值、`coach_editor_closed`人工确认、无另一个事务运行。**任何一队不通过，则0次写入。**
- `DURABLE_PREIMAGE`：写前将完整动作计划、原始共享块、保留位、所有目标关联、玩家独立授权范围、整批digest/状态`PREPARED`写入本地受限事务journal，刷盘fsync并获得独占lock，**先保存预像再写内存**。
- `APPLY`：保持同PID/创建时间、根/教练/球队名单指纹有效；各队每个共享块尽量单次整块写，严格按集合批准的fields组掩码，写入前再次比对原值，每步回读。出现教练变更、缓存覆盖、并发AI改值，停止。
- `VERIFY`：全部队伍重读原生块、非目标bits以及其他队伍目标没有被间接覆盖；追加中间日志；最终全部通过才`COMMITTED_VERIFIED_IN_MEMORY`；这仍不表示已保存到游戏文件或游戏战绩已被验证。
- `ROLLBACK`：任意写入失败则逆序**条件性恢复**已经写过且当前仍等于本事务目标的块，保留第三方/AI变化；核对恢复后全体读值，完全恢复才`ROLLED_BACK_VERIFIED`，否则`PARTIAL_UNRECOVERED_MANUAL_REVIEW`，不能谎称30队零变化。
- `RECOVERY`：崩溃/重启/遗留锁时读取journal并进入只读分析，人工批准恢复；不能直接删除锁或覆盖不确定预像。历史提交回执只可作为日志，不能宣称当前游戏仍是该值。已经`COMMITTED`的重复执行返回幂等报告并标当前状态未重新验证。

一个批次可以覆盖1–30队，但提供30队能力必须至少用假内存完成30队的分组与失败注入；在隔离存档安排不破坏玩家正式游戏的**最小真实多队写入→回读→恢复**技术检验，不要求让Codex跑模拟比赛。正式30队真实执行仍须玩家针对该批次/具体行动清单批准。

### 1.3 不能跳过的权限与风险
- 只有玩家实际明确批准的`batch_id/decision_id/version/action_ids/digest`可由执行模型转为外部执行参数；**执行器校验参数，不是聊天审批的事实来源**。脚本默认dry-run；缺批准、未关闭Coach Gameplan编辑页、内存结构歧义均无RW句柄。
- 继承V1 `--coach-editor-closed`门槛：打开编辑页缓存会覆盖脚本已经写入的值。执行手册必须把它列为首要用户操作步骤。
- GM输出变化需带独立球队合理性理由、战术旧值/目标值；不应自动把30队都改相同模板。阵容交易/主教练换人导致原值和对象发生变化时fail closed。
- 改变单一对手Gameplan、共享Playbook槽内容、普通球员倾向不属于本P0。没有`production_enabled`认证的其他18默认字段一律拒绝，即使`writable=true`。
- 记录哪些球队`HOLD`而未写，哪些队伍`APPLIED`，禁止以“一批提交成功”掩盖局部失败或未覆盖球队。

## 2. P0 — 玩家正常数据更新自动包含教练战术并在明确发布时送到GitHub

### 2.1 触发语义
- 当前生产入口`scripts/run_data_update.ps1 -SaveId ... -GameDate ... -Publish`已将采集→`src/export_web_gm.py`→`scripts/publish_web_snapshot.py`串接。**只在玩家明确触发当前数据更新时**自动纳入新`coaching_tactics`来源；已有`-Publish`才真正发布到GitHub。没有`-Publish`就仅完成本地数据源更新和导出，绝不自行将任务改成后台持续采集或自动运行GM/执行。
- 不能将现有独立`scripts/coaching_snapshot.py`写在另一个时间节点后再人工粘到`published`；必须和本次游戏来源capture、同PID/相容coach/roster身份、同`snapshot_id`与`data_updated_at`一致并写SQLite。对不可同一周期取得的字段标`CAPTURE_FAILED`或`UNKNOWN`，不能借上个月当今天状态。
- 读取战术是纯只读，不能为了导出打开RW、修改教练/ACE或在更新后自动调整任何球队。

### 2.2 生产源schema和文件
在`config/source_catalog.json`新增生产来源`coaching_tactics`（与当前`development_only_sources.coaching_tactics_local`明确区分）；复用`src/auto_pipeline_ingest.py`已校准的内存句柄与当前source batch（或提供可审计的采集时点绑定），SQLite新增snapshot-scoped`coach_tactics_observations`和必要`coach_tactics_gameplans`只读来源表；外键`snapshot_id` + `team_id` unique，每队关联head coach实名/岗位/身份及`NATIVE_COACH_POE_V1`profile版本，统计可查询30条核心队记录。

发布建议`published/saves/<save_id>/batches/<batch_id>/coaching/teams.json`，至少包括：
```json
{
  "schema_version": 1,
  "source_id": "coaching_tactics",
  "capture_status": "OBSERVED_LIVE_READ_ONLY",
  "save_id": "PLACEHOLDER",
  "snapshot_id": "CURRENT_GAME_SNAPSHOT",
  "batch_id": "SAME_MANIFEST_BATCH",
  "data_updated_at": "SAME_CAPTURE_TIMESTAMP",
  "codec_version": "NATIVE_COACH_POE_V1",
  "teams": [
    {"team_id":null,"abbreviation":"PLACEHOLDER",
      "coach_identity":{"verified_role":"HEAD_COACH","name":"PLACEHOLDER","identity_tag":null},
      "defaults":{"POEOffense":{"raw":null,"label":null,"readiness":"EXECUTOR_IMPLEMENTED_READY_FOR_PLAYER_APPROVAL"}},
      "other_fields":{"SimPace":{"raw":null,"label":null,"readiness":"PRODUCTION_DISABLED"}},
      "matchup_scope":"READ_ONLY_NOT_ACTIVATED",
      "source_status":"UNKNOWN"}
  ]
}
```
示例NULL都只是占位，正式源由真实内存事实产生；未观察的字段必须NULL +明确availability，不能默认中性0。候选只读对手信息可另导`coaching/gameplans.json`（大体积）或按需分队文件，GM基线默认只读30队默认战术汇总，只有对手专题才加载29×30的870记录；避免给GM一次性吞噬巨大数据。
- 需有`coaching/field_dictionary.json`（原生字段名、合法enum和中文展示、作用域、可执行状态、版本/证据）供GM直接生成合法提案；来源文件`coaching/teams.json`只存游戏事实，不把GM主观建议伪装为事实。
- 必须同步更新`src/export_web_gm.py`的manifest文件清单、`source_coverage.json`、`latest.json`已规定时间戳语义和SQLite ZIP导出；**不要创造第二套“最新战术快照入口”或新同步协议**。本项目网页GM通过已有`published/index.json→latest.json→batch_path`访问。
- **严禁复活历史`team_monthly_stats.poe_*`旧TEAM字节的战术语义**；它们继续标记`LEGACY_UNVERIFIED`。同步修改`src/gm_core/coverage.py`等分析覆盖字段映射，让GM的offense/defense或新增`coaching`评估指向已发布原生`coaching_tactics`来源，不再对旧`poe_*`当实战进攻配置。

### 2.3 审计与发布失败
- 新source的真实可得性有明确`VERIFIED/UNVERIFIED/NOT_OBSERVED`等状态，不得把技术可写当游戏已修改；校验30队唯一`team_id`、主教练球队/角色反向关系、字段合法enum、game date与源batch对应。
- 如果核心30队原生教练来源缺失，按用户要求教练源必需性定义选择**fail closed整个需要该来源的发布**（建议强制阻止发布标称完整的新batch，保留旧last-good latest）；不得静默导出过期战术同日新战绩。
- 若原有采集版本兼容性导致新教练源读取失败，需要明确异常`COACHING_SOURCE_CAPTURE_FAILED`，保留旧时间戳/last good，不覆盖生产快照；不因捕获失败自动启动新的采集或直接运行GM。
- 对旧存档/历史batch做schema迁移时不可追填“本局当前教练策略”，旧数据缺新源就明确UNKNOWN；不能修改历史不可变JSON。
- `-Publish`遵守现有远端仓库/可见性/dirty-tree校验与normal push；不要以强推覆盖项目。PR #1仍未合并时，Codex须先选择现有`codex/coaching-tactics-v1`分支接续开发/提交供审查，**正式生产数据发布路径在合并部署后才生效**。

## 3. P0 — 两本正式角色手册（代码完成后才标正式READY）

### 3.1 GM使用手册
目标位置：`web_gm/manuals/GM_COACHING_OPERATIONS.md`（若目录不存在可新建）。必须供网页版GM长期使用，**不是本轮的抽象需求文档**，要在真实最终接口形成后用可执行字段和路径写成生产手册。内容：
1. 模块能力范围和禁区：默认六项已技术准入；18项如未单项验收不得提出为可执行写入；Matchup/Gameplan和18防守设置只读/预案；不直接改球员能力、体系熟练度和全局slider。
2. 每一项可写字段的中文篮球含义、原生raw枚举、英文/中文展示、战术/阵容适配原则、可能代价（如攻板 vs 退防）、策略如何与球员已有能力和赛季表现连接；**不凭主观猜测写固定提升胜率百分点**。
3. 数据阅读入口：`published/index.json` → `latest.json` → `batch_path/coaching/teams.json` → `coaching/field_dictionary.json`；锁`save_id/source_batch_id/data_updated_at/game_date`与真实当前主教练身份；NULL/READ_ONLY数据不可编造。
4. 30队GM每个玩家触发的赛季节点，逐队输出`HOLD|PROPOSED`，只有必要更改的球队生成细化`team_actions`；交易后可重新评估，不自动从一个球队复制29队最佳模板。
5. 可复制的单队与30队批次JSON**真实契约示例**，包括旧值、新值、共享block旧值、coach identity、`action_id`、整批digest/版本、用户批准点、等待执行状态；所有值应在范围内。请说明在线GM不会直接连接游戏、不会自行运行执行模型。
6. 状态机`OBSERVED→PROPOSED→PLAYER_APPROVED(external)→EXECUTED→READBACK→NEXT_CAPTURE`；GM只写PROPOSED；批准发生在玩家与执行模型之间。失败/教练换人/旧数据/非法枚举由GM重提案而非脚本强行写入。
7. 教练策略改变**不要求模拟胜率A/B实测**。玩家可以按常规赛月度结果判断经营选择，但该分析不是教练功能可用性的硬门槛。

完成时在`web_gm/baselines/GM_BASELINE.md`、`web_gm/GM_DECISION_SOP.md`、`web_gm/memory/GM_CURRENT.md`登记本手册和当前已验收可写字段，GM赛季窗口以后按需读取；**本轮不替GM作30队实际战术决策**。

### 3.2 执行模型操作手册
目标位置：`docs/40_COACHING_EXECUTION_RUNBOOK.md`，与`docs/39_COACHING_TACTICS.md`互链；对Codex EXECUTION是可重复执行runbook而不是源代码论文。至少说明：
1. 执行角色必须取得玩家本聊天明确批准的`batch_id/decision_id/version/action_ids`，使用最新GM批次方案与数据快照；不能靠JSON里的`approved=true`权限。
2. 当前进程/存档/游戏日期、主教练身份、team_id、source batch、合法enum与共享原值复核；游戏Coach Gameplan编辑页**必须关闭**，`--coach-editor-closed`只是玩家/操作者的声明，不能自动验证UI。
3. `--help`/命令行准确实例：只读snapshot → 纯离线batch validate/dry-run → 逐队完整read-only preflight → 外部批准digest匹配 → batch execute → readback/journal/receipt → 需要时条件rollback/recovery；输出根路径和可供玩家传回GM的审批/执行摘要。只有确认code真能运行才发布具体命令，不可写“设想CLI”作为正式命令。
4. 全30队含HOLD的方案如何检查所有队/需修改动作集合；保证批量preimage、写回后完整核验和部分成功时人工恢复说明；程序不能保证跨进程硬件级原子写入。
5. 事务故障表：`STALE_PID`、`COACH_CHANGED`、`COACH_EDITOR_MUST_BE_CLOSED`、`STALE_FULL_SHARED_BLOCK`、`MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED`、`BATCH_PARTIAL_UNRECOVERED`、`COACHING_SOURCE_CAPTURE_FAILED`、审批无效、旧计划引用、缓存回写等的停止/如何重做。
6. **执行窗口默认不得自动刷新SQLite、触发数据发布或GM回合**，除非玩家在同一指令额外明确要求采集/发布（按政策，实际负责采集的能力仍由独立数据角色核验）。要记录执行局游戏时点与实际完成状态，供下一次玩家采集后GM核对。
7. PR中当前六POE写入事实/本次技术验收，与未来自动公开来源和批量写功能的测试状态分开，明确`EXECUTOR_READY`并非有真实批准。

完成后同步`docs/36_EXECUTION_BASELINE_PROMPT.md`、`docs/28_EXECUTION_WINDOW_RUNBOOK.md`、`AGENTS.md`的最少必读/入口路由链接，避免新执行窗口只知道交易、不知道教练批量执行。更新`docs/34_BASELINE_CURRENT_STATE.md`的能力表，最终手册优先级高于旧`docs/13`仅供历史参考的POE猜测。

## 4. P1 — 18项默认字段后续扩展（不是本轮闭环必需）

如果玩家看完本文另外18项后明确选择希望扩大可写范围，可分包P1a(5 Sim)、P1b(2 System +1 Playbook)、P1c(6滑块+4Freelance)。先用现有profile中的精确bit布局复用masked codec/transaction，完成UI范围与隔离局写入/持久化/回退技术验收，再**仅将通过的字段**加入`production_enabled`、发布的字典/GM手册/执行手册/批量白名单。不得因为需求“教练系统完成”就强行让24项全部开放。其他对手Gameplan继续独立专题，除非后续明确要实现其覆盖与回退。

## 5. 分阶段测试和交付验收（不以比赛胜率做测试）

A. **回归**：V1 37项测试、原有GM协议/来源测试、CLI help、旧TEAM+0xEB2仍被封锁，新增功能不得打开危险旧通路。

B. **30队批量**：假内存覆盖30教练、部分队HOLD、共享位保护、同批多个动作、唯一team identity、重复/错队/换帅/非法enum、整批审批digest、一队缺条件时**0写入**、第1/第15/第30队失败后逆序恢复、模拟崩溃恢复、缓存覆盖/第三方改值导致`PARTIAL_UNRECOVERED`、幂等但标当前状态未复验；隔离测试存档小范围实写、读回及恢复。未经玩家正式局批准，绝不实写30队。

C. **数据源自动集成**：同一个玩家触发的game capture与教练原生字段绑定，30队SQLite snapshot行、JSON导出文件、manifest/source coverage与timestamps一致；重启/PID变化重校准；模拟故障使新batch不冒充完整或覆盖latest；旧存档迁移不追填历史；三种模式：
  1. 玩家本地采集不加`-Publish`→本地数据可用，不远端推送；
  2. 玩家采集带`-Publish`→正常发布包含教练字段/枚举，网页GM可按既有latest读取；
  3. 故障→保留上次good source和latest，不产生过期同日战术；
  4. 玩家未触发→绝无后台采集/出版。
D. **双手册一致性**：GM示例生成的batch schema能被批量CLI `--dry-run`真正接受；GM只提出合法可写项；执行runbook命令行对照`--help`真实可运行；示例未经玩家批准无法拿到RW句柄；两个角色都能识别指定对手暂不能执行。
E. **GitHub治理**：所有新代码和文档尽量继续追加到现有PR #1开发分支，完成后真实列出commit/diff/测试实绩。由玩家/审查流程决定合并，不自动合并/发布正式数据。提交新增文件：
- `docs/development_reviews/DEV_20261017_07_COACHING_INTEGRATION_REPORT.md`
- `docs/development_reviews/DEV_20261017_07_COACHING_BATCH_ACCEPTANCE.md`
- `docs/development_reviews/DEV_20261017_07_COACHING_SOURCE_PUBLICATION_ACCEPTANCE.md`
- 正式`web_gm/manuals/GM_COACHING_OPERATIONS.md`及`docs/40_COACHING_EXECUTION_RUNBOOK.md`
- 真实代码、Schema迁移、source catalog、导出/发布和必要测试。

## 6. 完成定义与状态

**达到所有以下条件，可对玩家宣告“教练系统基础版可供GM正式使用”**：

1. PR #1（或其后续合并）真实代码包含六POE的安全单队和1–30队批量受控执行，且技术验收/错误回滚可复查。
2. 正常玩家触发的数据更新能把30队教练字段带入SQLite与发布JSON，按原GitHub latest/manifest被Web GPT GM读取，明确NULL和未放行字段。
3. GM与Codex EXECUTION两本手册真实可用并纳入基线入口；双方的输入/输出与审批边界一致。
4. 上述A–D回归/集成/模拟失败测试通过、无旧TEAM writer复活；只读/开发范围与审批权限不被自动提升。
5. **不要求快速模拟效果对比、一个月后的战绩对照，亦不要求其余18项全部开放或29对手覆盖写入**。这些是增强事项/可选经营观察，不作为本基础版闭环完成门槛。

本文件是Codex工程任务**规格**，没有自动启动Codex、替用户同意任何具体球队更改、自动合并PR或新开游戏执行窗口的权限。即使工程完成，首次正式批量执行也必须另有玩家逐批具体批准。
