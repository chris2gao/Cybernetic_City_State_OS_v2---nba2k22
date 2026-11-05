# 常规赛世界数据工程基线与下一任务入口

日期：2026-10-26。任务：`nba2k22-world-data-full-implementation-01`。
分支：`task/nba2k22-world-data-full-implementation-20261024`。
已集中验证的代码提交：`cbdaba0cb263083ea04171f8222aab65a00e3d30`；后续基线交付提交只补收尾文档、OS 状态和验证证据。

Human 已要求完成有界工作后固定当前常规赛工程基线并停止本轮持续开发。
这是待独立审核的工程候选；完整底层系统、全部目标字段、完整生命周期和 master 接入均未完成验收。
总体评分获准本次不交付。多场景存档（含赛季结束）和完整赛季研究放在下一任务。

## 直接复用的资产

| 资产 | 当前基线 |
|---|---|
| 可执行结构 | Schema v24，100 张 STRICT 表，1,775 列；`schema_model.py`、`schema.sql`、`field_dictionary.json`、`TABLE_CARDS.md` |
| 实际事实库 | `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/_runtime/world-saves/nba2k22_test_01/world-v24.sqlite` |
| 数据库摘要 | 1,470,952 行（含来源/元数据/引用关系），42 个成功采集单元；不是 1,470,952 个比赛/业务事件 |
| 数据库 SHA256 | `f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218` |
| Human 绑定 | `nba2k22_test_01` / `MyLEAGUE0003`；原游戏文件 `E:\games\NBA 2K22\data\steam\steam_settings\1644960\remote\MyLEAGUE0003` |
| 本地绑定 | 同目录 `save.json` 指向 `world-v24.sqlite`，以 Human 声明的已加载文件名建立身份，文件 hash/PID/同名球员均不单独证明存档身份 |
| 已发布快照 | 本 run 的 `06_执行/increment34/world-v24.snapshot.json` 及四个同目录 `.gz.partNNN`；本轮再次逐片及完整解压校验，结果见 increment37/snapshot-check.json |
| Reader | `refresh.py:SOURCES` 的20族，源码模块/函数/最新实际来源/落表计数见 increment37/source-coverage.json |
| 集中验证 | 301 项回归与 SQLite smoke 通过；实际库 integrity/FK、生成/物理 DDL 与字段字典一致；真实筛选230行/14页/导出哈希比对通过 |
| 核心报告 | 本 run `06_执行/increment37/verification-report.json`、`table-inventory.json`、`field-maturity.json`、`source-coverage.json` |

快照保留数据库事实及来源账本，不等于打包全部外部原始材料；原始 Native 证据与归档清单继续按各 increment 保留。
本轮没有逐一重验全部外部 raw 文件。现有快照是连续 gzip 流的分片；它与 `backup-facts` 生成的 `WORLD_FACT_BACKUP_V1` 目录是两种格式。
下一任务直接复用已绑定事实库；若需要副本，可用现有 `backup-facts` / `restore-facts` 生成并验证新的独立候选，保持原绑定不变。

## 来源覆盖与语义边界

| 需求域 | 已实现的可复用范围 | 尚未证明或未闭合的部分 |
|---|---|---|
| RES-P 球员 | 全池 Native 主体、当前唯一身份链接、公开能力/倾向/徽章/PlayTypes、合同、Vitals/健康/士气、归属分类、当前/历史统计与按时点查询 | 综评本次延期；部分 UI 单位/显示处理、历史身份/分配生命周期、未解析旧 Box 主体；完整 Player Card UI 未逐项验收 |
| RES-T 球队 | 当前核心球队、名单关联、球队统计、阵容/轮换槽位、财务原始字段与员工槽位 | 自定义/扩张与跨季迁移场景；轮换时间/财务 UI 单位与部分原生标志含义 |
| RES-C 教练/战术/训练 | 全 staff 池、个人属性/战术、球队员工槽位、计划/训练来源、当前教练统计与年度历史 | 战术 CRC 当前文字来源；教练历史槽位到年份/阶段的映射；不能从共享引用推断历史雇佣关系 |
| RES-G 比赛 | 真实赛程/分类、比赛状态、节分、Native Box 与可靠参与者关联、保留既有比赛事实与来源检查 | 部分历史 Native 球员 ID 未解析；真实高级逐场字段及 UI 口径；季后赛系列赛与后续场景 |
| RES-L 联盟赛季 | 日历/模式/阶段原始观察、赛季累计/场均查询、同批次胜率排序与37类球员统计榜单 | 累计统计的阶段保持 NULL；官方种子/同战绩/资格规则不冒充已验证；跨季最终归档待后续 |
| RES-M 市场/财务/选秀 | 已读合同/薪资/财务、市场分类、选秀权与原生消息/交易候选来源 | 新秀池/选秀结果尚无对应场景实证；Native 交易候选不能冒充外部业务执行回执 |
| RES-H 历史荣誉 | 真实纪录、原生历史统计/荣誉和联盟历史/奖项来源；年度4族独立刷新桶 | 原生标志不自动等于已定稿奖项；历史人物身份/年份/分配可达性按各来源保持未知 |
| RES-S 设置 | 实际游戏设置、规则、原始数值与已证枚举；历史/按范围查询 | 没有 Human 目标配置/关键依赖清单的输入，不伪造开档目标版本及核验通过记录；UI 效果/写回未验收 |
| RES-D 核心 | 单档 SQLite、来源/缺口账本、append-only、局部采集提交、历史 cutoffs/分页、公开字段过滤/导出、备份恢复、进程重连与恢复基础设施 | 完整生命周期集中验收、所有列的 UI 等价性、全季/100年容量与独立审核仍未完成 |

`field-maturity.json` 对1,775列列出字段声明、单位、权限及实际非 NULL/NULL 行数；非 NULL 只证明已存值。
Native 读取/元数据/消费者代码、已验证转换、计算结果、UI 含义和存档持久性是不同证据轴。
每个 Reader 的 Native profile 与对应 increment 原始验证保留其证明范围；普通字段字典中的 UNKNOWN 不由计数或回归 PASS 自动消除。
source-coverage 中的 field_gaps 是来源局部历史声明，可能被后来的来源补充，不能简单按总数判定当前功能是否完成。

明确待决定项目见 [DIFFICULT_ITEMS.md](DIFFICULT_ITEMS.md)，容量安排见 [CAPACITY_AND_RETENTION_POLICY.md](CAPACITY_AND_RETENTION_POLICY.md)。
只有 Human 已明确延期的范围按延期处理；其他语义缺口仍需在后续范围/验收中明确决定。

## 采集与查询工程入口

从本 checkout 根目录操作，Python 使用现有 Python3.14。以下是下一任务的复用命令，不在本次收尾自动执行游戏采集：

```powershell
$repoRoot = 'C:\Users\gk\Documents\ChatGPT\nba2k22\world-data-full-implementation-01'
$pyPath = 'C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$cliPath = Join-Path $repoRoot '08_Domain_Applications\Antigravity_GM_Engine\world_data_prototype\cli.py'
$saveDirectory = Join-Path $repoRoot '01_os\07_content\_runs\run-20261024-nba2k22-world-data-implementation-002\_runtime\world-saves\nba2k22_test_01'
$dbPath = Join-Path $saveDirectory 'world-v24.sqlite'

# 每次使用全新、尚不存在的输出目录。
& $pyPath -X utf8 $cliPath reconnect-game $saveDirectory MyLEAGUE0003 '<NEW_RECONNECT_DIRECTORY>'
& $pyPath -X utf8 $cliPath refresh-world auto $saveDirectory MyLEAGUE0003 '<NEW_CAPTURE_DIRECTORY>'
& $pyPath -X utf8 $cliPath summary $dbPath
& $pyPath -X utf8 $cliPath standings $dbPath 'season:native-year:2022'
& $pyPath -X utf8 $cliPath player-leaderboard $dbPath 'season:native-year:2022' --metric points_per_game
& $pyPath -X utf8 $cliPath fact-fields player_season_totals
& $pyPath -X utf8 $cliPath query-facts $dbPath player_season_totals --limit 100
```

`refresh-world --families` 可选择20族中的所需来源，完整清单由 `--help` 和 source-coverage 给出。
ordinary16族：schedule、game-mode、period-stats、organization、staff、coach-stats、lineups、finance、market、planning、settings、player-details、player-state、affiliations、player-skills、news。
annual4族：records、honors、league-history、staff-history，按每独立存档每 Native 游戏赛季年刷新一次；同年已成功则跳过。
`reconnect-game` 只保存当前进程/Native 连接证据，不新增事实采集单元。

进程重启正常发生，无须重复通知 PID。`auto` 会按 PID+创建时间+模块/版本重新连接，重新解析动态根和来源；旧地址不可复用。
中断恢复使用新输出目录及 `--resume-report OLD_REPORT`，先证明旧 worker 已终止并校验已提交单元。
如果 Human 明确更新数据，使用 `--data-updated`；Native 日期/阶段/赛季变化也会要求重新采集。
相同日期不证明数据未变。这里没有后台采集调度器。

主要查询：player/team/staff 卡、game、schedule、season/player-seasons、lineups/native-player-rotation、finance、native-staff/staff-slots/coach-stats/staff-history、market/planning/gameplan、settings/rules、records/native-honors/awards/league-history/native-news/native-transactions，以及各 Native 字段族查询。
字段条件筛选使用 `query-facts`；选择列、筛选和导出使用 `export-filtered`。各实际函数签名见本 run increment37/query-api-catalog.json，CLI 参数见 cli-help.txt。
历史查看使用 `--as-of`（采集时间）、history/history-page；它不等于游戏日期。
普通 GM 接口只提供允许的 typed 字段，不提供 owner 原始材料/隐藏 Potential；SQLite 文件自身是 owner 资产，不是逐列权限服务。

## 下一任务：全生命周期场景与增量采集

1. Human 提供文件名与场景，并说明是同一存档的后续阶段还是独立测试档；前者延续已明确绑定的观察历史，独立档使用 `init-save` 建独立目录与数据库。不能凭同名/同值自动合并。
2. 每次加载后重新连接并核对 Native 版本、目录、日期/阶段/赛季，保留场景 manifest 与完整来源证据；不用旧 PID 或动态地址。
3. 优先用现成20族 Reader 做明确触发的增量采集，保留已成功单元；只为实际场景暴露的具体缺口开展后续有界研究。
4. 分别覆盖赛季结束、季后赛、休赛期、选秀、跨赛季、归档/历史回看和进程重启恢复；当前空表不能作为场景不存在的证明。
5. 获得完整真实赛季后再测量增长、评估100年目标并由 Human 决定保留年数；现阶段不删历史。
6. 游戏写入、推进日期、独立人格/决策、master 集成继续适用各自授权；本基线提供只读数据基础设施。

当前交付的下一 Owner 为 Human 组织的独立审核；审核范围应固定为此工程基线，保留本页列出的未来工作。
本轮没有启动审核、合并 master 或声明 Human 最终验收。
