# GM SQLite 本地按需查询（DEV-10 V2 / M0）

DEV14增量：新增 world/gameplay/tactics/tendency/training/personal_defense 只读域，支持 --team、--player-identity、--field-key、--side 与原批次分页。默认行含object_key供稀疏提案引用；仍只读密封M0副本、默认20/最多50/约20KB，不读控制库或活动三库。只有后续full_verified_v1实际采得并审计的新批次才有新域；旧M02保持缺失，不据此声称已完成Web连接。见[DEV14手册](DEV14_STATE_IO_RUNBOOK.md)。

状态：`IMPLEMENTED_LOCAL`。玩家在本次开发中明确把三个 Web GPT 的真实连接测试延后：本轮完成实现与 PowerShell 本地验证，连接由玩家以后建立，有问题届时修复。**不标记 `M0_CONSUMER_ACCEPTED`，但这不再阻塞本轮工程交付。** 不进入 M1—M4，不更改现行 GM 轮次数、经营审批或全量采集规则。

## 安装与数据来源（本地拥有者操作）

检出包含本功能的代码。需要 Python 3.11+（实际本机验证 Python 3.14）、SQLite JSON1；不安装数据库服务，不连接 NBA2K22。所有命令在该代码仓库根目录的 PowerShell 执行。脚本默认根目录是**脚本所在仓库**，换工作树时显式指定共享的 `--query-root`；不要把工作树缺失的本地数据误判为需要重新采集。

现有采集和发布继续使用玩家触发的 `scripts/run_data_update.ps1` / `full_verified_v1`。新导出在既有双库 `Connection.backup()` 归档后，用同一归档建立 `database/query_snapshots/<career>/<batch>/`。发布仍须玩家授权 `-Publish`。没有单来源更新、自动采集或新的一组 latest 指针。旧批次不重写。

已有审计归档可单独建立查询副本，无须游戏在线，也不重新导出/上传：

```powershell
$career = 'mc_haliburton_2021'
$latest = Get-Content "published/saves/$career/latest.json" -Raw | ConvertFrom-Json
$manifest = "published/$($latest.batch_path)/manifest.json"
$archive = "_exports/archives/$($latest.batch_id).zip"
python -B scripts/gm_data_snapshot.py --archive $archive --manifest $manifest
if ($LASTEXITCODE -ne 0) { throw '快照准备失败；不要改用活动数据库' }
```

当归档位于另一工作树，`--archive` 指向已有 ZIP；本工具不自动下载。不要将活动库用 Copy-Item 当作一致性备份。安装器只从既有审计 ZIP 读取指定成员，用 SQLite backup 生成新副本，验证双库 `data_sync_metadata`、源审计、快照行摘要、原始池审计绑定、池计数、游戏日期和存档一致；原子安装到不可覆盖的批次目录。失败 staging 保留供拥有者诊断。它不是新的内存采集或日常 JSON 哈希同步检查。

每份快照有双 SQLite、源 ingest/audit/context/data_update 和本地 manifest。库文件只读，manifest 内的 SQLite 文件指纹用于本地静态副本完整性；不恢复 JSON 文件哈希、下载比对或更改现有时间戳同步契约。不要把本地数据库、归档、manifest 中的运行时源材料、个人路径或 ACL 日志提交到 GitHub。

保留被 GM 引用的历史 batch，**本版没有自动清理**。如以后清理，先确认决策引用、独立保留或可用 Release 恢复，不能仅因 latest 已改变就删除旧批。

## 连接与操作系统权限（玩家以后建立连接时）

网页 DEVELOPMENT / ANALYTICS / GM 都调用同一个本地 CLI；`--role` 只声明调用者，不代表已建立连接或获得权限。开发不创建远程连接、不读取凭据、不代替三个网页会话测试。

1. 使用单独的**非管理员**本地消费者账号，通过玩家授权的终端连接运行。仓库代码、Python 和 `published/` 只授予读取/执行；消费者不能修改代码或已发布指针。
2. 拥有者准备查询副本后，使用下面 ACL 脚本，明确传入两个互不包含的目录。脚本给予消费者查询目录 RX 并显式拒绝写/删，拒绝其访问活动 saves；拥有者/SYSTEM/Administrators 保留维护权限。快照根的父目录也拒绝消费者写/删除子项，防止通过父目录替换快照。
3. 不要把拥有者账号、管理员组、Users 或 Everyone 当作消费者。脚本拒绝同账号及这些公共身份；玩家还须确认该专用账号未加入 Administrators。普通 chmod/文件只读属性不是用户隔离的替代方案。

```powershell
# 仅拥有者运行。账号与路径由玩家按机器实际填写，不要把示例当成已配置。
./scripts/set_gm_query_permissions.ps1 -ConsumerAccount 'COMPUTER\GmReader' -QueryRoot 'E:\path\database\query_snapshots' -AuthoritySavesRoot 'E:\path\database\saves'
```

消费者不运行 `gm_data_snapshot.py` 或 ACL 管理脚本。新增快照继承查询根权限；复制/移动快照到别处后由拥有者重新核对 ACL。消费者连接失效时报告阻断，不借管理员会话或活动数据库绕过。CLI 的双库 `mode=ro`、`query_only=ON` 和 SELECT authorizer 是额外防线，并不声称能限制一个拿到管理员任意 shell 的人。

## 实际查询命令

先运行 `python -B scripts/gm_data_query.py --help`。默认从**本地可信发布指针**解析 latest，默认20条，最多50条，最终结果预算约20KB。`--batch` 可固定明确的历史批次；翻页必须保持 batch、筛选、字段、limit 不变。

```powershell
python -B scripts/gm_data_query.py status --career mc_haliburton_2021 --role WEB_DEVELOPMENT
python -B scripts/gm_data_query.py team summary --career mc_haliburton_2021 --team SAS
python -B scripts/gm_data_query.py team roster --career mc_haliburton_2021 --team SAS --fields identity,name,position,salary,years_left --limit 20
python -B scripts/gm_data_query.py team roster --career mc_haliburton_2021 --team SAS --fields identity,name,attributes --limit 2
python -B scripts/gm_data_query.py staff team --career mc_haliburton_2021 --team SAS --fields identity,name,role --limit 20
python -B scripts/gm_data_query.py staff search --career mc_haliburton_2021 --name Popovich
python -B scripts/gm_data_query.py staff search --career mc_haliburton_2021 --job HEAD_COACH --candidates --limit 5
python -B scripts/gm_data_query.py player search --career mc_haliburton_2021 --scope pool --name 'Michael Jordan' --draft-year 1984 --historical-rookie
python -B scripts/gm_data_query.py player search --career mc_haliburton_2021 --scope pool --unrostered --position PG --limit 5
python -B scripts/gm_data_query.py contract team --career mc_haliburton_2021 --team SAS --limit 5
python -B scripts/gm_data_query.py contract search --career mc_haliburton_2021 --years-left 1 --limit 5
python -B scripts/gm_data_query.py coaching team --career mc_haliburton_2021 --team SAS --fields team,coach,values
python -B scripts/gm_data_query.py coaching opponent --career mc_haliburton_2021 --team SAS --opponent GSW
python -B scripts/gm_data_query.py picks team --career mc_haliburton_2021 --team SAS --trade-eligible --limit 20
python -B scripts/gm_data_query.py finance team --career mc_haliburton_2021 --team CLE
python -B scripts/gm_data_query.py finance semantics --career mc_haliburton_2021
python -B scripts/gm_data_query.py issues --career mc_haliburton_2021
```

按明确 `identity` 查询可以消除同名歧义，但身份只在所绑定 batch 内有效。slot/face/name 不升级为跨名单永久 ID。`--unrostered` 表示未出现在本批 NBA 名单的模型，**不等于已验证自由球员**。`--years-left 1` 只筛观测合同年限，不证明休赛期到期、选项已处理或已有签约资格。员工 `role` 仅认证双向岗位关联；候选的 `candidate_position` 来自其原生职位字段，未任职不编造球队。

教练 `values` 提供19项默认设置，不包含五项 Sim；Tempo 保持 raw/含义未知，BenchDepth 是人数。对手防守 `values` 含18项，`mixed_fields` 中的 null 保留“组内不同”的含义，不伪造共同旧值。这里不生成可执行提案，不返回内存块/地址。

SQL 仅允许受控 `q_*` 业务视图的单条 SELECT：`q_teams/q_players/q_pool/q_staff/q_coaching/q_defense/q_picks/q_finance/q_finance_semantics`。`status` 列出字段及来源是否有观测。只投影所需列；禁止 SELECT *（COUNT(*)例外）、CTE、原始表、扩展加载、PRAGMA、ATTACH、写入、多语句和未准许函数；约2秒 SQL 超时。SQL 参数使用 `--params` JSON数组。

```powershell
python -B scripts/gm_data_query.py sql --career mc_haliburton_2021 --role WEB_ANALYTICS --select 'SELECT team,COUNT(*) AS player_count,SUM(salary) AS roster_salary FROM q_players GROUP BY team ORDER BY team' --limit 50
python -B scripts/gm_data_query.py sql --career mc_haliburton_2021 --select 'SELECT name,salary FROM q_players WHERE team=? ORDER BY salary DESC,identity' --params '["SAS"]' --limit 5
$page = python -B scripts/gm_data_query.py player search --career mc_haliburton_2021 --scope pool --limit 5 | ConvertFrom-Json
if ($page.next_cursor) {
    python -B scripts/gm_data_query.py player search --career mc_haliburton_2021 --scope pool --limit 5 --batch $page.source_binding.batch_id --cursor $page.next_cursor
}
```

SQL分页应有稳定 ORDER BY；游标绑定查询/参数/batch/limit，最大offset10000。超额仍返回完整有效JSON和 `RESULT_LIMIT_REACHED`，不把第一页当完整池；单行太大时缩减字段。默认不返回55能力/完整合同/全部员工，只有明确字段请求才投影受限行。

## 三个 Web 角色以后如何使用

| 角色 | 最小起步查询与边界 |
| --- | --- |
| WEB_ANALYTICS | status → roster → 30队SQL聚合 → 员工岗位/候选 → 1984 Jordan/未在队模型 → 用Python或SQL计算可复现指标。只保存精简 ANALYSIS_ONLY 结果与来源；本轮未建设派生工作台。 |
| WEB_GM | status → 当前同批分析摘要 → 某队19教练/18对手防守/8岗位/全名单合同与能力/三届签位/少量市场候选。只在玩家触发GM时经营；小提案仍为HOLD或PROPOSED，不写游戏。 |
| WEB_DEVELOPMENT | status → issues → 四队cash raw与finance semantics → 按需查看源代码/来源缺口；不连游戏进程，不把连接许可当采集许可。 |

三角色使用相同 career/batch。每次输出有 `source_binding/field_evidence/DATA_ACCESS_CONTRACT_V2`，记录声明角色、请求、实际条数、时间、成功/错误与工具；本地运行明确为 `LOCAL_CLI_EXECUTION_ONLY_NOT_WEB_ATTESTATION`。`CAPTURED→AUDITED→PUBLISHED/LOCAL_AUDITED→QUERYABLE_BY_ROLE→ACTUALLY_USED` 各阶段不互相代替。本轮证明 `QUERYABLE_LOCAL`，Web两个后续阶段保留未测试；不允许修改 `--role` 就自证实际Web访问。

GitHub 继续承载小型来源引用、分析摘要、提案、回执与角色记忆；保留原JSON与Release兼容。无需先读整份 staff.json/name_index.json，不新增大型JSON分页。M0不修改V3/V4经营规则切换门槛。

## 最小本地验收与失败诊断

```powershell
./scripts/verify_gm_sqlite_m0.ps1 -Career mc_haliburton_2021
```

只测试合成隔离数据库和已有查询副本；不会捕获游戏、创建正式GM节点、写游戏或发布数据。本地细节回执在 `_exports/dev10_m0/local_cli_receipt.json`。操作系统ACL脚本可在拥有者有具体消费者账号后配置；本次不声称实际配置过该账号或验证过Web权限。

| 状态 | 诊断与处理 |
| --- | --- |
| BLOCKED_LOCAL_DB_ACCESS | 本机/终端离线、路径/账号权限、Python/JSON1、文件缺失。检查status及拥有者配置；不退回活动库或旧JSON整池。 |
| STALE_OR_MIXED_BATCH | 双库绑定不符、字节被改、审计/日期不符、游标换批。保留证据，重新由拥有者从对应有效归档建立副本；不补签认证。 |
| LOCAL_AUDITED_NOT_PUBLISHED | 本地来源不匹配已上传latest。仅开发可显式 `--allow-local-audited`；不能当正式Web GM当前生产数据。 |
| HISTORICAL_EXPLICIT_BATCH | 显式指定旧batch；只供历史研究，不自动作为当前经营输入。latest不可用时不会静默改用旧批。 |
| UNVERIFIED_FIELD | 无该来源/字段（如OVR/旧TEAM POE）。保持UNKNOWN，交开发缺口，不能补默认值。 |
| RESULT_LIMIT_REACHED | 按cursor继续，或减少字段；未拿到后续页不能宣称全池已读。 |
| INVALID_SQL / QUERY_TIMEOUT | 写入/多语句/原始表/函数/通配或超时被拒绝；改用业务子命令、明确投影及受限聚合。 |
| MULTIPLE_CANDIDATES | name匹配多个batch身份；用更多已观察条件区分，不自动选首条。 |

异常字段问题入口是 `issues` 的稳定issue_id，访问失败通过标准回执报告；消费者可将小型回执保存在自己的派生工作目录/角色交接文档中，**不写事实表**。不在M0启动M4反馈数据库或后台调度。财务调查见 [M0验收](development_reviews/DEV_20261018_10_M0_SQLITE_ACCESS_ACCEPTANCE.md)。
