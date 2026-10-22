# DEV-20261018-10 V2 — GM V4 SQLite按需数据访问、金融知识、经营决策与反馈系统

2026-10-20：M3已按玩家批准合入main（PR #4 / 504a4c0）；M4最新职责由[DEV20](DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md)覆盖本文件旧混合定义，仅工程问题池/开发交接/readiness，不做GM赛果比较或双引擎校准。独立M4分支实现和5项最小验收见[M4交付](../development_reviews/M4_SYSTEM_EVOLUTION_IMPLEMENTATION_AND_ACCEPTANCE.md)，PR #7已按玩家批准合main（c51fa36），不启用V4。

- 更新：2026-10-18
- **2026-10-19最新阶段**：Astra设计审阅后，玩家已授权继续编码；M3A/M3B本地工程完成，见[M3入口](DEV_20261019_10_M3_DESIGN_AND_IMPLEMENTATION_ENTRY.md)、[M3A验收](../development_reviews/DEV10_M3A_ACCEPTANCE.md)、[M3B验收](../development_reviews/DEV10_M3B_ACCEPTANCE.md)。PR #4待源代码审阅/合并，正式30队仍UNASSESSED，V3继续生效、V4未启用。下方“不启动M3”是此前阶段边界；本次不启动M4。
- **本次M0开发中的玩家最新修正（优先于下文原C3/E连接前置要求）**：不要求Codex测试三个Web GPT的真实连接；完成实现与PowerShell本地访问验证即可交付并提交GitHub，玩家在开发完成后自行建立连接，有问题届时修复。三个角色仍如实记录未测试，不冒称M0_CONSUMER_ACCEPTED。M0本地交付与Web后续连接分开，不因此启动M1—M4。实现与本地证据见[验收报告](../development_reviews/DEV_20261018_10_M0_SQLITE_ACCESS_ACCEPTANCE.md)。
- 当前进度：`M0_MERGED_MAIN / M1_M2_ENGINEERING_COMPLETE`（2026-10-19，随PR #3收尾交付）。M0随PR #2合并（`67bf4dc`）；M1/M2设计、实现、审查路径修补及范围内验证已完成，见[交接](DEV_20261018_10_M1_M2_IMPLEMENTATION_HANDOFF.md)和[收尾记录](../development_reviews/DEV10_M1_M2_CLOSEOUT.md)。下文“首轮仅M0”是原阶段范围；30队策略仍UNASSESSED、正式评估0队，Web连接延后，GM V4尚未启用，不启动M3/M4。
- 权威关系：**本V2取代**[DEV10 V1](DEV_20261018_10_GM_V4_FOUNDATION_DECISION_OBSERVABILITY_MASTER_PLAN_V1.md) 的**M0大JSON分片架构和与之矛盾的M3/M4数据访问描述**。V1其余GM愿景、历史审计、篮球/经济/决策/反馈研究方向仍作背景；执行以本V2为准。Codex首轮**仅实施M0**，其它里程碑必须玩家再次触发。
- 仓库：`chris2gao/nba2k22-gm-engine`。开发模型执行具体代码；本文件由Web Development制定。
- 玩家新增条件：**可以让网页版开发、数据分析和GM三个GPT，通过玩家授权的本地命令行，访问本机SQLite。** 这是授权意愿，不等于三个会话的本地连接已实际验证或自动取得写权限。
- 总体目标：`SQLite权威事实 + 本地小结果只读查询 + 独立派生工作台 + GitHub精简跨模型交接 + GM每节点目标一次答复`，不是再把每个巨大员工池拆成海量新JSON。
- 用户原有五阶段不变：①玩家触发Codex **full_verified_v1** 全量采集，②玩家触发Web数据分析，③玩家触发Web GM决策，④玩家逐项审批，⑤玩家触发Codex受控执行。**不增加单来源增量采集、后台自运行、任何未批准游戏写入**。

## A. 为什么转向SQLite

当前真实M02发布批次`mc_haliburton_2021 / 2021-12-12 / 2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`中，`staff.json`约2.73MB、1458员工；GitHub Web文件工具取到SHA但正文为空，不能凭已发布断言网页GM能阅读。`player_catalog/name_index.json`约481KB、完整池3383模型、在队466人，默认大批读取会污染上下文。原V1拟通过JSON分页解决，用户现在明确希望网页模型直接本地查询SQLite，因此决定**把复杂筛选与聚合下沉到本地确定性查询层，每次只把所需少量结果送回模型**。

经仓库审查，**两套现有事实库已经足够作为起点**：
- `database/saves/<save_id>/league_state.sqlite`（实际路径以`src/gm_engine.py`、`src/data_context`及`database`上下文为准）：球队`team_monthly_stats`、人员`player_monthly_stats/player_source_details`、员工`staff_pool_observations/staff_source_details`、原生教练`coaching_team_observations/coaching_source_captures`、选秀权`draft_asset_observations`、球队赛季总数`team_source_stats`等。
- `player_pool.sqlite`：`player_pool`含`slot_id/full_name/draft_year/position`等列，已有`idx_full_name`、`idx_draft_year_pick`；模型ID及slot不天然跨新名单版本持久。
- `staff_source_details.details_json`、`player_source_details.details_json`及`coaching_team_observations.observation_json`是**有结构的JSON TEXT列**，不代表必须把所有字段再复制成新表：先SQL过滤少量行，再`json_extract`（确认JSON1可用后）或Python在受限行内解析，并投影指定字段。高频检索瓶颈再建索引/业务视图。
- `src/export_web_gm.py`已经以`sqlite3.Connection.backup()`生成一致的两库备份，放进GitHub Release ZIP，具有`data_sync_metadata`快照绑定；`src/gm_engine.py`早已有`mode=ro`查询。**复用现有组件**，不再重写数据库引擎。
- `database/schema.sql`还有历史模拟/预测/业务意图或`coaches/players`旧表；**有表 ≠ 有本局认证观测值**。查询层仅将已审计、按snapshot存储的真实来源认证为游戏事实。旧TEAM POE、未实测OVR和假想训练/员工评分不能直接升级为可决策数据。

现金疑点保留：CLE/NOP/UTA/ORL`cash`接近`2^32`；其有符号解释可能是负数，但未验证原生编码，不允许静默修正或把`budget−salary`当真实签约空间。

## B. 新架构：读事实库，写派生库，保留GitHub小型交接

```text
玩家启动一次 full_verified_v1 全量采集（现有；不改变）
  → Codex原生只读采集 + SQLite写入 + 同批审计
  → 从同一批次做 SQLite backup：league_state.sqlite + player_pool.sqlite
  → 本地只读 query_snapshots/<career>/<batch>/ 双库（原始事实不可变）
  → 原有 GitHub Release ZIP + latest/manifest（仅玩家授权-Publish）
       |
玩家连接网页模型到本地命令行（必须分别验证）
       |
       +-- Web分析：只读CLI按条件SELECT/SQL聚合 → 小查询结果
       |       → 独立gm_workbench.sqlite中存计算好的球队特征/金融情景/分析状态
       |       → 精简GitHub ANALYSIS_ONLY+schema+来源引用
       +-- Web GM：用同一CLI按队、球员、岗位、战术/合同查询
       |       → 消费派生工作台/精简分析摘要，决定30队经营与待审批动作
       +-- Web Development：读查询状态、反馈/异常与相关证据，规划后续开发
       |
玩家审批明确动作 → Codex执行器受控写游戏内存/回读
       |
下一次玩家主动触发全量采集时，再根据游戏真实结果做反馈配对
```

**三层数据严格隔离**：
1. `FACTS`：两套采集SQLite+历史审计，所有Web模型仅只读，绝不添加或覆盖观测；禁止将派生判断写回事实表。
2. `DERIVED_WORKBENCH`：建议独立`gm_workbench.sqlite`（M3/M4逐步实现）；放分析结果、财务预测、30队状态、事件与缺口，显式标记`ANALYSIS_ONLY/PROPOSED/UNKNOWN`。只有明确触发当前角色工作时，受控写入器可写对应schema；**这些不是游戏事实/玩家批准**。
3. `HANDOFF`：GitHub的小型`latest.json/manifest/source_coverage`、规则知识、分析摘要、待批准提案、执行回执、长期记忆、DEV问题索引。现有JSON兼容输出和数据库Release在M0不必删；**大型原始JSON不再作为Web GM的必读输入**。因本地电脑关闭/网络权限丢失导致SQLite不可用，必须报告阻断，依照已有已认证小文件作受限决策或HOLD；不能拿过期工作台冒充当前来源。

## C. M0（第一轮Codex唯一开发范围）— 只读SQLite数据消费平台

### C1. 固定批次与读写隔离

1. 复用`src/export_web_gm.py`已有的SQLite一致性备份，按实际目录政策新建本地只读的`database/query_snapshots/<career_id>/<batch_id>/`，含同一次采集的两份SQLite、manifest和采集审计来源绑定。这个目录是**查询用静态快照**，不要让Web模型连接`database/saves/`中正处于更新/替换的活动数据库。
2. 两库分别用`mode=ro`连接，设置`PRAGMA query_only=ON`，用操作系统权限分配只读文件访问（不要用允许模型写入事实库的管理员会话伪装“只读”）。如果将来需要从WAL写入状态获取一份快照，应调用一致性backup，而不是仅复制一个有未提交WAL的文件，也不要使用`immutable=1`读取有实时WAL的活动库。
3. 验证`data_sync_metadata`在两个文件的`snapshot_id/save_id/data_updated_at`一致，并绑定`batch_id/game_date/audit/PASS_VERIFIED`；与最新GitHub`latest`不一致时标明`LOCAL_AUDITED_NOT_PUBLISHED`或者`STALE_OR_MIXED_BATCH`。正式网页GM是否可作为生产来源，严格遵守现行的发布及玩家触发闸门，不因机器里有最新库就偷偷换入尚未发布的新事实。
4. 每次查询回传精简`source_binding`，包括career、snapshot、batch、game_date、data_updated_at、发布状态、query版本；支持显式`--batch`和latest解析，避免分析模型取新快照、GM取旧快照、球员池又取另一期。
5. 静态快照不会阻塞Codex下一次采集；保留被GM决策引用的历史批次，清理旧本地副本前验证引用/保留可从Release复原。不要将本地原始数据库、个人本机路径、游戏原始内存指针重新上传为GitHub text。

### C2. 统一受控查询器，不让模型默认`SELECT *`

建议实现`scripts/gm_data_query.py` + `src/gm_data_access/`。下面是**拟议命令，不是现成命令**，Codex可在开发中细化、用`--help`标注真实语法：

```powershell
python scripts/gm_data_query.py status --career mc_haliburton_2021
python scripts/gm_data_query.py team summary --career mc_haliburton_2021 --team SAS
python scripts/gm_data_query.py team roster --career mc_haliburton_2021 --team SAS --fields name,position,salary,contract --limit 20
python scripts/gm_data_query.py staff team --career mc_haliburton_2021 --team SAS --fields name,role --limit 20
python scripts/gm_data_query.py staff search --career mc_haliburton_2021 --name "Popovich" --limit 10
python scripts/gm_data_query.py player search --career mc_haliburton_2021 --name "Michael Jordan" --scope pool --limit 10
python scripts/gm_data_query.py coaching team --career mc_haliburton_2021 --team SAS --fields system,freelance,sliders
python scripts/gm_data_query.py finance team --career mc_haliburton_2021 --team CLE --fields salary,budget,cash --limit 1
```

- 采用**固定业务子命令 + 参数化SQLite SELECT/聚合**，支持按姓名、球队、位置、岗位、选秀年份、到期合同、战术、选秀资产等条件检索；必要时对分析模型单独开放经审查的只读SELECT入口，但必须防SQL多语句/ATTACH任意文件/PRAGMA写入、性能超时、结果爆炸。
- 默认`LIMIT 20`、上限建议50，控制列清单而非全部原始55项/JSON/BLOB；原始详情按明确命令小批返回。全联盟可用`GROUP BY`聚合得到30队统计，不把全部466现役、1458员工或3383模型塞进对话。工具返回`rows/row_count/source_binding/query_version/status/next_cursor/truncated/field_evidence`。输出设软预算如20KB；超额返回`RESULT_LIMIT_REACHED`与分页指针，而不是截断JSON或冒充全部已读取。
- 同名球员/员工需返回多候选及来源身份，不只按姓名/face_id/slot当永久人物ID；`staff_source_details`无验证的候选人员不应被标记为已在某队任职。
- 先核对现有schema/查询规划后再补少量复合索引或受控业务视图；员工全池约1458并非值得上分布式搜索引擎，简单SQLite索引即可。模型不允许直接在只读数据库里建表、改索引、跑DB迁移。

### C3. 五个数据质量关口与真正的消费者权限验收

把来源状态分为`CAPTURED → AUDITED → PUBLISHED/LOCAL_AUDITED → QUERYABLE_BY_ROLE → ACTUALLY_USED`。定义`DATA_ACCESS_CONTRACT`，按`CODEX_CAPTURE/WEB_ANALYTICS/WEB_GM/WEB_DEVELOPMENT/CODEX_EXECUTION`记录：`career_id,batch_id,query_version,requested_data,actual_row_count,field_coverage,success/error,verified_by,verified_at,tool_used`。
- **Web三个模型必须各自真实验证**终端连接与权限；用户“愿意提供权限”不是成功证据，插件或远程终端是否已连接本机需要现场检查。Codex本地Python成功**不能代替**网页窗口的实际能力验收。
- Web ANALYTICS：能从同批SQLite按队读全员、获得30队聚合、分岗位找现任与候选员工、查球员池1984 Jordan及无队球员，并用本地Python/SQL计算一个可复现指标。
- Web GM：从同批来源读某队教练19字段、对手防守18字段、员工8岗位、全名单合同/能力、合法选秀权及几个市场候选；再根据Web分析产物回钻证据，形成**不写游戏**的HOLD/PROPOSED小提案。
- Web DEVELOPMENT：能只读查看快照版本、员工/球员索引与来源缺口、4队可疑现金raw与字段解释，读取结构化问题索引，不连原生进程。
- 失败分支必须覆盖：设备离线/权限不足、SQLite文件不存在、无法同时绑定双库、校验失败、过期批次、未认证字段、结果过量、同名冲突、恶意输入和尝试写库；模型应报告`BLOCKED_LOCAL_DB_ACCESS` / `STALE_OR_MIXED_BATCH` / `UNVERIFIED_FIELD` / `RESULT_LIMIT_REACHED`，说明哪些业务不能继续，不能沉默降级为“全部员工已分析”。
- M0完成后Codex先报告`IMPLEMENTED_LOCAL / WEB_CONSUMER_ACCEPTANCE_PENDING`及三个模型的独立实测命令。只有真实Web三角色完成访问、同批和只读验证，才标记`M0_CONSUMER_ACCEPTED`。不必重新做无意义的真实比赛或改游戏测试。

### C4. 现金字段语义检查仍是M0另一项P0目标

M02`cash`异常可疑`unsigned/signed32`解释，必须比对真实字段offset与编码及有条件的本局UI展示；保持raw观测，已证实后才修改后续全量解析器。旧历史快照不可静默覆盖。`cash/budget/payroll/total_salary/staff_budget/monthly*_revenue`分别标单位、时间跨度、是否能进入交易/签约资格计算、证据等级。**不准将任一原始差额自动升级成“可签约现金”**。输出`finance_semantics`业务视图，未认证返回`UNKNOWN`并附风险提示。M1实际薪资模型在此基础上继续建设。

### C5. M0交付物和非目标

建议提交：
- `scripts/gm_data_query.py`、`src/gm_data_access/`（带明确`--help`、只读、超限保护、真实源绑定）；必要的少量schema索引/快照输出钩子。
- `docs/GM_SQLITE_QUERY_ACCESS.md`：三个网页模型通用命令、身份绑定、权限设置、查询示例、失败处理和GitHub精简交接。
- `web_gm/data_contracts/CONSUMER_DATA_CAPABILITIES_V2.md`和机器可读测试回执（本地部分与三个Web端分别登记），`docs/development_reviews/DEV_20261018_10_M0_SQLITE_ACCESS_ACCEPTANCE.md`；同时记录财务字段语义假设/确认结论。
- 与实际`latest`绑定的`query_snapshots`小型manifest，及开发反馈`DATA_CONSUMER_UNREADABLE`/财务异常的最小事件入口。

**M0非目标**：不重做大JSON分片、不开外部数据库服务、不对游戏事实库授予Web写权限、不替用户改变现有全量采集频率、不改GM审批规则、不开发休赛期真实竞价写入，不让Web GPT直接写游戏内存。

## D. M1—M4继续按分期完成，但变更主要访问与存储接口

| 里程碑 | 目标 | V2读写契约 |
| --- | --- | --- |
| **M1 财政/2K22规则** | 审计工资帽/税线/现金/预算、外挂合同竞价约束，按本局真实数据模拟未来3年已知合同承诺及资产机会成本 | 从两库SQLite查询事实；在`gm_workbench.sqlite`中写`finance_scenarios`等**派生**记录，附UNKNOWN |
| **M2 篮球和30队长期战略** | 结构化挡拆、空间、换防、传切等战术知识；现实组织参考与本局独立GM战略，GSW/SAS/OKC三队试点后扩30队 | 知识用Markdown/小型JSON或SQLite索引；30队`TEAM_STRATEGY_STATE`可建工作台表，并保留GitHub精简版本及历史，不从当前阵容捏造文化 |
| **M3A 数据分析升级** | 把分析模型从排行榜转向决策准备：30队、跨批、教练、财务、市场机会与行动信号 | SQL计算/按需查询；结果写`gm_workbench.sqlite`表`analysis_runs/team_features/market_candidates`；GitHub提交精简`ANALYSIS_ONLY`来源和方法，GM可按队查询，不生成海量30队JSON详情 |
| **M3B GM V4** | 同一个用户触发任务内做完30队审查、方案对比、独立交易谈判、财务/资产冲突闸门、最终审批案；理想一次答复，复杂不超过3次为目标 | GM使用受控CLI查询事实与工作台；详细理由/事前假设存工作台/文档，给玩家只呈现可审批事件/HOLD摘要 |
| **M4 运营反馈闭环** | 结合下次玩家触发的全量采集，将已执行动作与之后游戏观测、源错误、GM质量问题进行可信对照，形成开发待办 | `gm_workbench.sqlite`中`source_access_events/action_hypotheses/outcome_comparisons/development_issues`，并生成GitHub`DEVELOPMENT_INBOX/CURRENT.md`轻量摘要供下次开发窗口主动审计 |

**不要求M0同时建设完整工作台**；先建设稳定的事实库只读访问，M3/M4逐步加入派生数据表及按角色权限写入器。不要把模型自行用SQL`UPDATE`事实库当作“可以操作本地数据库”的授权。

### 运营反馈规则（必须贯穿分期实施）

采集结束报告source health，网页模型实际查询后写自己的consumer access health；分析记录数据口径/来源缺口；GM记录前置假设与`HOLD/PROPOSED`理由；玩家批准和Codex执行才生成`EXECUTED`回执；**只有下一次新全量采集后才可比较真实比赛表现**。允许产生`NEW_GAME_MECHANIC_CANDIDATE`或异常建议，但不能据此直接断言因果、自动触发开发或写游戏。反馈去重并带`career/batch/action_id/evidence/confidence/severity`。下一次用户主动启动Web Development时由其先看`DEVELOPMENT_INBOX`，提出要修的新功能/知识研究候选，玩家选择立项。

### GM V4规则切换闸门（不变）

现有`GM_MIN_FIVE_ROUNDS_V3`仍是有效玩家规则，保留历史`W03`材料；新的`GM_DECISION_PROTOCOL_V4`必须先基于真实同批SQLite，完成GSW/SAS/OKC无游戏写入演练，并且30队覆盖/双边独立利益/资产冲突/财务闸门和网页真实消费能力合格，**用户再明确批准切换**。届时再一次性修订GM SOP、V3 superseded指针、schema、基线和`docs/35`的轮次数冲突。单回合不是降低质量的理由。

## E. 开发分期执行及验收操作

1. **本轮给Codex的正式开发范围只有M0**：先做两库同批静态只读快照、CLI小结果查询、访问角色状态与财务异常调查。Codex对现有代码进行真实兼容性审计后再写，保留旧发布文件和M02历史观察。按最小必要逻辑测试证明身份、SQL只读、分页与异常处理；无须连接/写游戏或重复保存测试。
2. Codex独立提交M0代码、操作文档、CLI示例与`M0_LOCAL_READY_WEB_ACCEPTANCE_PENDING`报告，给出需要玩家在三个Web窗口实际试用的命令和本地权限准备条件。此时**不得自行声称三个Web GPT已接上电脑**。
3. 玩家分别连接并触发Web ANALYTICS/GM/DEVELOPMENT实际查询。记录成功/失败、可读字段与边界；失败回开发模型处理、再验收。M0成功后才启动M1；M2知识搜集可在明确授权的研究窗口提前准备。
4. 后续每里程碑独立任务窗口、独立验收报告、commit/PR及记忆索引；不要一次交付含5阶段但无法验收的“大引擎”。M3/M4应遵守玩家触发五阶段，不在后台处理。
5. 当前安全限制继续：普通球员能力/潜力/徽章/倾向不改；教练/交易正式游戏执行要获批；训练、锁定个人分钟和Sim设置禁纳入GM执行；选秀只交易现行三届简单年份/轮次/原队/持有队。

## F. 交给三个Web模型的工作方式（最终目标，而非当前已实现）

- 分析模型：查询`status`→SQL按队/时点聚合→对异常查少量原始行→计算与写入派生工作台→提交精简`ANALYSIS_ONLY`交接。
- GM模型：查询`status`→读工作台30队摘要、策略状态→针对有经营动作的队伍按需查球队/员工/球员/合同/对手防守→做独立双边谈判与风险检验→一次任务提交`PROPOSED`。
- 开发规划模型：查询`status`、访问错误及开发反馈索引→查看某个异常的**最小必要**源记录及代码→输出有证据的新开发建议/任务书，而不是默认全量载入数据库。

**最后界限：本V2仅更新开发方向和规格，未表示本地终端已授权、M0代码已开发、网页模型已经具备访问能力或游戏事实已经更改。**
