# 新局模板与月度数据闭环规程

> **规则优先级：** 项目总规则见 [22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md](22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md)。

本指南描述当前代码实际执行的流程。抓取、审计和 GM 决策分别运行在独立阶段；任何缺失的关键观测都会使本批次停止，未通过审计的快照不能进入 GM 引擎。

## 新开一局

为每个游戏存档指定一个稳定且唯一的 ID：

```powershell
python src/bootstrap_new_game.py --save-id mc_run_01
```

程序从 `database/schema.sql` 创建干净的 SQLite 模板，并将副本放入 `database/saves/mc_run_01/`。默认只读校准并采集数据，生成 `M00_BASELINE`；它不会修改游戏设置或球队。只有玩家已批准本次初始化写入，才使用 `--approve-game-writes` 应用全局比赛设置与 30 队 POE/门票模板，并逐项回读核验。每个存档有独立的联赛数据库、球员池、快照、审计凭证、备份和报告。重复运行同一 ID 不会清空数据库；不同游戏存档要用不同 ID。

```powershell
# 仅当玩家明确批准本次游戏设置写入后使用
python src/bootstrap_new_game.py --save-id mc_run_01 --approve-game-writes
```

模板只保存数据库结构和稳定的初始规则，不包含上局球员数据、工资数据或游戏内存地址。新局启动时，脚本校准球队数组、按当前进程读球队数据，并把运行时地址标记为 `RUNTIME_ONLY`，不把地址写进可复用模板。

## 每月数据更新：交付后等待玩家

推进游戏到需要复盘的节点后，运行：

```powershell
python src/run_monthly_cycle.py --save-id mc_run_01 --season 2022 --month 1 --name NOV
```

统一入口顺序执行：

1. 对该存档数据库做一致性备份。
2. 以只读方式检查本次进程内存中的队伍、焦点球员、历史球员池和制服组锚点。
3. 重新抓取 30 队当前观测字段、球队名单和全量球员池，并写入该存档的 SQLite。
4. 对未观测赛况字段执行 NULL 断言；缺少内存读数、球队覆盖不完整或球员池锚点失效时停止。
5. 用确定性脚本的固定随机种子抽样球队、球员和制服组原始结构，与当前进程内存交叉比对；同时检查 SQLite 完整性、外键、行数和数据摘要。
6. 审计通过后只生成 `DATA_REPORT_<snapshot_id>.md`，以 `DATA_READY_AWAITING_PLAYER` 交付；外层 `run_data_update.ps1` 再按本次要求导出和发布。采集和初始化不调用 GM 候选生成器。玩家之后另行触发 GM 决策，批准具体方案后再到执行窗口触发本地执行，详见文档 27/28。

审计器是确定性 Python 校验脚本，不是大模型。它会把审计时间、入库清单摘要、当前快照行摘要和球员池文件摘要绑定在凭证中。任一文件或数据库行在审计后改变，GM 闸门都会拒绝使用旧凭证。GM 查询数据库使用 SQLite 只读连接；建议不会直接写回游戏内存。

省略 `--save-id` 会继续使用旧的共享数据库 `database/league_state.sqlite`，用于兼容已有存档。新存档应使用独立 ID，避免不同游戏的数据混合。

## 数据来源规则

- 30 队 ID 使用已校准的 NBA 核心球队集合；2K 的全明星保留槽位不计入 NBA 队数，黄蜂 ID 31 会纳入。
- 球员能力、合同和位置使用严格内存读取；读失败会终止采集，不能伪装成数值 0。
- 游戏内存未提供的战绩、出勤、场均和伤病字段保持 SQL `NULL`，不会用工资或战术数据反推。
- 全量球员池按新局独立保存。历史新秀从原始结构 `raw_struct[0x70] & 0xE0 == 0xE0` 判断，不另存重复的 `is_rookie` 或 `rookie_tag_raw` 字段。
- 制服组先保存原始结构和候选 TEAM_ID。槽位顺序及单个原始 ID 还不足以证明某人是某队主教练；映射未核验前不写入 `coaches` 主表。旧版产生的教练行会先完整保存在 `coach_mapping_quarantine`，再从正式表隔离。
- CBA 交易合法性需要完整 cap holds、roster charges、例外和球队工资账本。现有快照不足时 GM 只会输出待 CBA 复核候选，不标记为合法，也不会虚构选秀权。
- 当前工资规则只配置了 2021-2022 赛季；其他年份会停止并要求先补入已验证规则。

## 当前校验边界

实机权限验证：当前普通 Codex 执行通道拿不到 `PROCESS_VM_READ`；项目 UAC 启动器已通过管理员 Python 进程完成采集。一次实际重启（PID 5224 → 1608）后，生产校准器识别旧缓存、完成全扫描和新批次 25 项审计；同一新 PID 的重复采集也通过，业务字段与重启前基线一致。详见 [23_RESTART_CAPTURE_VERIFICATION.md](23_RESTART_CAPTURE_VERIFICATION.md)。后续每次重启仍执行同样的动态校准与审计；错误 5 代表没有采到数据，不能继续 GM 决策。
