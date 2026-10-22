# 教练批量执行操作规程

DEV07 V2真实CLI规程。PR #1已通过玩家审查，于2026-10-18合并main（2509b3b）并同步本地执行仓库；首次真实生产采集/发布尚未运行。19项默认字段均支持提案/受控执行：六POE、五数值设置、双体系及命名手册14项有实机写回证据，四Freelance依据完整原生枚举/布局与有序codec放行，未冒充实机UI验收。原生Tempo按玩家明确选择开放读写；界面含义未知，不能称为已验证的进攻节奏或百分比。参考同局教练观测值选择目标，仅保留8位原生整数格式保护；存储端点不是已观测UI端点或建议值。BenchDepth是轮换人数上限，GM依据实际阵容选人数，不受9–10测试样本限制；其他四个已确认百分比字段为0–100。指定对手整体防守及默认/整体两对象混合批次已完成隔离局写入/条件恢复验证。正式存档不在开发测试范围。核对 `docs/34_BASELINE_CURRENT_STATE.md`、最新V2字段矩阵和profile，不从历史聊天推定能力。玩家已停止同类重复菜单/保存重启测试，不能编造未看见的UI或持久性结果。

## 第一次正式启用的部署核对

1. 玩家决定合并PR后，执行机器更新到包含该合并的版本；核对CLI、profile与两份手册来自同一部署。本次PR已由玩家明确批准合并；后续仍按实际部署版本核对，不从手册存在推定环境版本。
2. 玩家另行触发正常采集及 `-Publish`，沿用原数据入口；开发/执行窗口不为补验收自动运行它。
3. 所选career的 `latest.json` 指向新批次，上传状态为UPLOADED，`data_updated_at/uploaded_at`有效；存档、游戏日期与玩家本次指令一致。
4. 本批 `source_coverage.json` 中 `coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`，新来源已通过审计；缺失或未审计时停止，保留旧批次原样。
5. GM能读取本批 `coaching/teams.json`、`coaching/field_dictionary.json`，并按需读取owner的 `coaching/opponents/<TEAM>.json`。30队与来源绑定一致。
6. GM提供正式提案及生成器输出；玩家明确批准具体 `batch_id/decision_id/version/完整action_ids/batch_digest` 后，执行模型才能写正式局。

这些是首次正式使用时的核对步骤，尚未实际运行；文档示例不代替真实生产采集成功或玩家批准。后续实际使用由GM发布决策、玩家批准、执行模型按本手册操作并报告内存结果；玩家可以要求执行模型只读复查，也可在游戏中发现异常后反馈修复。不把每次使用变成保存重启或比赛效果验收。

## 输入与来源

主入口 `scripts/coaching_batch.py`；不带执行开关时完全离线，不打开游戏句柄。`--snapshot` 可读同批发布的 `coaching/teams.json`，对手动作按需重复传 `--opponent-source coaching/opponents/<TEAM>.json`。每个文件的 career/batch/date/data_updated_at 必须一致，一个 owner 文件必须恰有其他 29 队，禁止重复挂接或对自己。

执行模型按玩家要求顺序调用脚本，一个批准批次结束后再处理下一个。不安排多个教练执行脚本并发操作游戏。

也可使用隔离开发只读快照，但必须明确 `environment=ISOLATED_TEST`、存档确为隔离副本，并单独传 `--test-save-confirmed`。不要把开发快照补进正式发布包。正式动作必须来自本局最新可信同批来源；PID/创建时间绑定不符则重新采集，不用旧绝对地址。

## 连续示例：GM请求 → 30队批次 → 执行 → 回执

示例沿用此前PHI/IND的演示操作：PHI默认进攻节奏与面对IND的整体持球压迫两项调整，其余29队为GM明确决定的HOLD。30队参与批次不表示必须给30队都写值；实际需要调整多队时，由GM逐队补requests，不复制一套目标。以下是后续正式使用说明，**本次文档修订不执行任何preflight、写入或回滚命令**。

### 1. 接收篮球请求，由离线生成器补齐事实

按[GM手册的完整示例](../web_gm/manuals/GM_COACHING_OPERATIONS.md#从30队来源到requests再到完整外层提案)，保存 `gm_intent.json` 和该节 `build_proposal.py`，在已部署仓库根目录运行：

```powershell
python -B _exports/coaching_example/build_proposal.py '<实际career_id>'
```

说明脚本把GM选定的球队名称映射为实际team_id，按本批来源写出requests，并调用现有 `coaching_batch.py --requests` 生成 `batch.json`；最终生成可由 `decisions.py` 校验的 `gm_proposal.json`。教练身份、原始共享块、对手整体组与before_raw全部由确定性程序填入。`hold_other_teams`仅是GM手册示例脚本的输入约定，不是教练CLI开关。

产物均在 `_exports/coaching_example/`：

| 文件 | 用途 |
| --- | --- |
| gm_intent.json | GM填写的篮球决策，含球队/对手、目标与理由；不是native事实或批准 |
| requests.json | 已映射实际ID的CLI请求，含requests与hold_team_ids；不是执行批次 |
| batch.json | 现有离线生成器产出的完整COACHING_BATCH_CHANGE，执行器的`--batch`输入 |
| dry_run.json | 离线valid/executable、prepared_actions、blocked_action_ids与batch_digest |
| gm_proposal.json / gm_verdict.json | 完整外层GM提案及其结构/来源校验结果；并非批准 |

不需要再手工改写batch.json。若目标、来源或理由需调整，在**审批前**改篮球请求、重新生成和校验；已经批准后任何内容改变都应形成新版本并重新取得对应摘要的批准。

### 2. 已收到完整GM提案时，原样提取生成结果

若交接物已经是 `gm_proposal.json`，不必重复做上一节生成。将下面脚本保存为 `_exports/coaching_example/extract_handoff.py` 并运行 `python -B _exports/coaching_example/extract_handoff.py`。它原样提取程序生成的batch，并从其changes反向保留请求文件，**不重新编造身份、前值或整体组**。

```python
import json
from pathlib import Path

work = Path("_exports/coaching_example")
proposal = json.loads((work / "gm_proposal.json").read_text(encoding="utf-8-sig"))
batch = proposal["coaching_batch"]
requests = []
for action in batch["actions"]:
    request = {key: action[key] for key in ("team_id", "scope", "action_id", "expected_effect")}
    request["targets"] = {c["field"]: c["after_raw"] for c in action["changes"]}
    if action["scope"] == "VS_OPPONENT_DEFENSE":
        request.update(opponent_team_id=action["opponent_team_id"], defensive_setting_scope="OVERALL")
    requests.append(request)
for name, value in (("batch.json", batch),
                    ("requests.json", {"requests": requests, "hold_team_ids": batch["hold_team_ids"]})):
    (work / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```

此处requests只作交接和审批前重建用途；**执行使用原样提取的batch.json**。若确需重新生成，使用同一可信来源与现有 `--requests/--batch-id/--decision-id/--version/--proposal-output`，再核对生成结果和摘要；不同即停下更新提案并重新审批，不能沿用旧批准或手改已批准batch。未生成完整batch的篮球意图应走上一节，不可直接送入`--execute`。

### 3. 离线校验与摘要审阅

仍在仓库根目录，以玩家选定的实际career替换占位符；以下PowerShell变量在后续命令中沿用：

```powershell
$career = '<实际career_id>'
$work = Join-Path (Get-Location).Path '_exports/coaching_example'
$gm = Get-Content -LiteralPath (Join-Path $work 'gm_proposal.json') -Raw | ConvertFrom-Json
$latest = Get-Content -LiteralPath "published/saves/$career/latest.json" -Raw | ConvertFrom-Json
if ($latest.batch_id -ne $gm.source_batch_id) { throw '来源已变化，重新生成提案并审批' }
$batchDir = Join-Path (Join-Path (Get-Location).Path 'published') $latest.batch_path
$snapshotPath = Join-Path $batchDir 'coaching/teams.json'
$opponentPath = Join-Path $batchDir 'coaching/opponents/PHI.json'
$batchPath = Join-Path $work 'batch.json'
$stateRoot = Join-Path $work 'execution'
$common = @('--snapshot', $snapshotPath, '--opponent-source', $opponentPath, '--batch', $batchPath, '--state-root', $stateRoot)
python -B scripts/gm_validate_proposal.py --save-id $career --proposal (Join-Path $work 'gm_proposal.json')
if ($LASTEXITCODE -ne 0) { throw '外层提案校验失败' }
python -B scripts/coaching_batch.py @common --output (Join-Path $work 'dry_run.json')
if ($LASTEXITCODE -ne 0) { throw '批次校验失败' }
$dry = Get-Content -LiteralPath (Join-Path $work 'dry_run.json') -Raw | ConvertFrom-Json
if (-not $dry.valid -or -not $dry.executable) { throw '批次不可执行，停止' }
$claim = $gm.requested_approval[0]
if ($dry.batch_digest -ne $claim.batch_digest) { throw '摘要与提案不一致，重新审批' }
$claim | ConvertTo-Json -Depth 5
```

本例只有PHI需要对手文件；其他批次没有指定对手动作时去掉`--opponent-source`，多个owner则各重复一次，绝不挂错career或来源批次。CLI默认离线，以上不打开游戏句柄。`--requests`与`--batch`互斥；不能把外层gm_proposal.json直接当作batch。

审阅完整action集合、每队HOLD/调整、scope、对手、前后值和共享块。外层 `valid=true` 与离线 `executable=true` 都不是批准；不得把`requested_approval`自动转成玩家同意。`SIM_EFFECT_PENDING_PLAYER_MONTH`仅为兼容合同字段，不要求等一个月、胜率试验或推进游戏日期。

### 4. 玩家明确批准后，只读预检查，再执行

向玩家呈交 `$claim` 中的 `career_id`、`batch_id`、`decision_id`、`version`、**完整action_ids集合**与 `batch_digest`，连同篮球理由和目标值。批次包括HOLD内容，摘要也会覆盖它们。玩家只批准部分动作时必须生成新批次/版本/摘要，不把部分同意套用整批。

玩家明确批准且确认已退出教练编辑页后，执行模型才能按下节预检查和执行；批准的是具体内容，而不是由模型在JSON里填`approved=true`。实际批准记录来自玩家消息，不能从示例、校验结果或requested_approval字段推定。

## 只读预检查、执行与回执命令

先做只读预检查；此时仍不取得RW句柄：

```powershell
python -B scripts/coaching_batch.py @common --preflight --output (Join-Path $work 'preflight.json')
if ($LASTEXITCODE -ne 0) { throw '只读预检查失败，停止执行' }
```

`--preflight`核对全部目标、原始共享块、主教练、阵容、进程与动态目录。任何失败即停止；不自动重采、不改批准batch。来源或计划改变则重新生成并审批。要求玩家退出Coach Gameplan编辑页并停在日历/主界面；`--coach-editor-closed`只是根据玩家确认作出的声明，脚本不能自动看见菜单。

以下变量只在**已经收到玩家对完整元组的明确批准后**填写。将实际批准内容原样抄入，不能直接从模型requested_approval自动推导授权。`batch_digest`在CLI中对应参数名 `--approve-plan-digest`，没有`--approve-batch-digest`参数。

```powershell
$approvedCareer = '<玩家批准的career_id>'
$approvedBatch = 'COACH_BATCH_001'
$approvedDecision = 'COACH_DECISION_001'
$approvedVersion = 1
$approvedActions = @('PHI_DEFAULT_TEMPO', 'PHI_VS_IND_PRESSURE')
$approvedDigest = '<玩家批准的完整batch_digest>'
$approvalArgs = @('--approve-career-id', $approvedCareer, '--approve-batch-id', $approvedBatch, '--approve-decision-id', $approvedDecision, '--approve-version', $approvedVersion, '--approve-plan-digest', $approvedDigest)
foreach ($actionId in $approvedActions) { $approvalArgs += @('--approve-action-id', $actionId) }
python -B scripts/coaching_batch.py @common --execute @approvalArgs --coach-editor-closed --output (Join-Path $work 'receipt.json')
if ($LASTEXITCODE -ne 0) { throw '执行异常，停止后续写入，按下文检查journal' }
Get-Content -LiteralPath (Join-Path $work 'receipt.json') -Raw
```

只有所有目标均通过检查才会写入；本例的30队参与者中PHI两项动作执行，其余29队回执为HOLD。回执/journal来自执行器实际读回，不由模型填写“成功”。执行模型据它报告具体队、作用域、对手、前后值、摘要和错误；玩家要求时再只读查看修改后的内存，不安排新的比赛或保存重启验收。

隔离局技术验收额外加 `--test-save-confirmed`；正式局不能通过伪造环境跳过字段验收。输出和 state-root 必须在本仓库 `_exports` 下，不提交这些本地文件。

除各自事务锁外，单动作与批次执行器在任何游戏句柄之前取得同一份进程绑定锁。它位于当前执行账户的 `tempfile.gettempdir()/Antigravity_GM_Engine/coaching_execution_locks_v1/<process_binding>.lock`，不随 state-root 或仓库工作树改变；更换career标签也不能让同一进程同时被两个入口操作。它只是误开窗口的防护，不改变顺序执行方式。锁仅存本地元数据和对应journal路径，不进入Git。

先 RO 校验全批，RO 关闭后才取得 RW，再重新校验全批。全部目标 preimage 持久化并 fsync 后才首写。共享块合并 mask，保护未知位；整体动作必定覆盖认证组全部有效记录并保留 player/defender IDs，空槽不写，提交标记最后处理。每块读回，结束再读全批。运行失效或并发变化会停止并按逆序条件恢复。

这是软件事务，不是跨 30 队的物理瞬时原子操作。成功为 `COMMITTED_VERIFIED_IN_MEMORY`，只证明内存，不代表游戏存档已保存。全 HOLD 批次返回 `NO_WRITE_NEEDED`，零游戏句柄。重复已完成事务只返回缓存回执，并标 `NOT_REVALIDATED_CACHED_RECEIPT`；不能把缓存回执当成当前游戏仍保持目标值的证明。

## 恢复与异常

需要回滚且处于玩家已授权的恢复范围内时，沿用同一batch、snapshot、state-root和完整批准元组，先关闭编辑页：

```powershell
python -B scripts/coaching_batch.py @common --rollback @approvalArgs --coach-editor-closed --output (Join-Path $work 'rollback_receipt.json')
if ($LASTEXITCODE -ne 0) { throw '回滚异常，保留journal并转人工处理' }
```

`--rollback`会在自己的RO阶段验证当前整块仍等于本批次目标值，再按逆序条件恢复，成功为`ROLLED_BACK_VERIFIED_IN_MEMORY`。普通`--preflight`期待写入前旧值，不能把它当作写入后成功核对或回滚预检查；`--preflight/--execute/--rollback`互斥。原始snapshot仍绑定当前进程；跨重启、AI改值或换局后不能强行套用旧批次回滚。

失败期间只在当前块仍等于本事务刚写值时恢复旧值，避免覆盖第三方修改。`FAILED_ROLLED_BACK_TO_OPERATION_PREIMAGE` 表示此次操作已经条件恢复；`PARTIAL_UNRECOVERED_MANUAL_REVIEW` 表示仍有不确定块，停止后续写入并检查 journal，不能宣称全批恢复。锁文件提示崩溃或并发时不自动删除锁或强行重跑，先读取对应日志和当前状态。

共享锁只有在首写前失败，或已持久保存成功/完整恢复的最终journal后才释放。部分恢复、首写后的进程崩溃、最终journal写盘失败都会留下共享锁，阻止从别的state-root再次执行。根据锁内 `journal_path_local_only` 定位日志，人工核对当前进程、所有未恢复块和处理决定后，由具体获批的执行窗口处理；不提供自动解锁或强制重跑参数。日志目录仍须沿用，不用更换目录规避历史回执。

换帅、换局、换进程、原生布局变化、动态手册目录变化或任一旧块漂移，都要求重新取得来源和提案。不得用强制选项绕过检查。源代码和配置哈希记录在本地 journal 便于审查，不作为网页 JSON 同步契约。

## 保存、采集和发布各自触发

执行完成后停止游戏写入。玩家自行保存；玩家另行触发数据更新时，正常 `scripts/run_data_update.ps1` 才在原来的只读采集会话捕获教练来源，写入 snapshot-scoped SQLite、审计、导出轻量文件，`-Publish` 才使用已有发布器同步 GitHub。不带 `-Publish` 只本地导出。开发窗口不能为证明本功能自动运行全量采集或发布。

该来源接入代码已随PR #1合并main并同步本地；首次真实生产采集/发布未运行。缺队、非法值、身份歧义或审计缺失必须拒绝新包并保留 last-good/latest。历史批次没有教练来源时保持缺失，不回填新观察。


| 阶段／状态 | 真实含义与后续触发 |
| --- | --- |
| 外层valid / 离线executable | 结构、来源与字段可执行性通过；没有玩家批准，也没有游戏写入 |
| COMMITTED_VERIFIED_IN_MEMORY | 执行器已写并回读目标内存；不是游戏保存或未来仍保持的保证 |
| 玩家实际保存 | 玩家在游戏中保存当前结果；执行器不会因为内存成功自行保存、退出或重启 |
| 玩家后续数据采集 | 新的只读观察，写入新的snapshot/数据库和导出；不会改写旧批次事实 |
| GitHub发布 | 玩家数据任务带`-Publish`才调用既有发布器；上传成功由新的latest时间戳/状态表示，不能由执行回执代替 |

上述阶段逐个由玩家触发。日常实际使用沿GM决策→玩家批准→执行模型按手册执行→真实回执/必要时只读复查→玩家游戏反馈进行，不要求为每个设置补齐独立实机验收故事。
