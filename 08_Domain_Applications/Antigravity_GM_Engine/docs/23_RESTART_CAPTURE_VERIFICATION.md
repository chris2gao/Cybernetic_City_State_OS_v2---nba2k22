# 游戏重启与数据抓取验收

## 当前基线与证据

隔离验收存档：`restart_validation_20261016`。重启前快照：`2021-2022_M01_PRE_RESTART`。游戏 PID：5224。完整管理员流水线已完成采集、数据库入库、25 项脚本审计和数据库 GM 建议生成；结果为 `PASS_VERIFIED`。测试未写入游戏内存。

| 来源 | 重启前结果 |
| --- | ---: |
| 核心球队 | 30 |
| 现役球员 | 466 |
| 球员池物理槽位 | 3,320 |
| 有效球员池记录 | 3,319 |
| 历史新秀类型匹配 | 789 |
| 制服组原始结构 | 78 |
| 无效姓名记录进入数据库 | 0 |

物理 Slot 0 不是有效球员，已被采集器拒绝。制服组目前只作为 raw 观测保存，球队归属未验证；不能据此宣称正式教练映射可用。未观测的战绩、比赛统计和伤病等字段仍为 NULL。

`validation/forced_rescan_pre_restart.json` 保留 PID 5224 的模拟缓存进程变化测试；`validation/forced_rescan_validation.json` 记录重启后 PID 1608 的同类复核。测试保留临时缓存中的旧地址、将 PID 改为 -1，由生产校准器废弃三个堆地址后重新扫描。全部锚点恢复为 HEALTHY；3,319 条有效球员原始结构体与数据库、两个实时池候选逐条一致。槽位 0 双方均无效，若有字节差异则单独记录。正式运行时缓存未被临时测试修改。

`validation/pre_restart/` 已保存重启前的 SQLite 数据库、球员池、入库清单、审计凭证、运行时地址图和 `baseline_evidence.json`。该基线禁止被下一轮采集覆盖。

## 实际重启结果：本次已通过

玩家于本地 2026-10-16 重启游戏，新进程 PID 为 1608，启动时间 21:46:58。保留旧 PID 5224 的正式地址缓存后，运行 `POST_RESTART`，第一次入库校准报告保留了 `previous_pid=5224`、`pid=1608`、`process_changed=true`，并重新扫描全部堆锚点。

| 锚点 | 重启前 | 重启后 | 地址变化 |
| --- | --- | --- | --- |
| 球队 Pacers 基址 | `0x7ff4e270fd10` | `0x7ff4e731b510` | 是 |
| 全局球员池 | `0x7ff4e6dfb2e8` | `0x7ff4e6dfb2e8` | 否，但已重新扫描验证 |
| 制服组池 | `0x7ff4e2815f88` | `0x7ff4e7421680` | 是 |
| 焦点球员地址 | `0x7ff4e4e9abd8` | `0x7ff4e4e9abd8` | 否，但已重新解析静态指针 |

首次全扫描 8627.44 ms，状态 HEALTHY。随后 `POST_RESTART_REPEAT` 使用新缓存，校准耗时 8.11 ms。两批各通过 25 项审计，并生成绑定各自新快照的、需玩家批准的 GM 建议。

`scripts/verify_restart_capture.py` 核验三批清单/审计/SQLite 摘要/球员池文件哈希，以及真实 PID 变化、生产缓存废弃、缓存重复使用、全部已采集业务字段比较。30 队全部快照字段、466 人阵容字段、3,319 条球员池解码字段和 78 条制服组身份，在重启前后及重复抓取时均一致。未验证的 `raw_team_id` 只作诊断，不解释为制服组归属。

`validation/real_restart_verification.json` 为总验收报告，`real_restart_verified=true`；`validation/post_restart_runtime_map.json`、`post_restart_player_pool.sqlite` 和 `game_process_after_restart.json` 分别保存新地址图、第一次重启后球员池和真实进程启动信息。重启后全部 3,319 条有效球员 BLOB 与当前内存的独立逐条复核也通过。

本次样本为一次真实重启和一次新缓存重复采集。每次后续重启仍必须执行正常动态校准及审计，不把本次通过扩展为所有进程、存档或游戏版本的保证。

## 可复用的实际重启验收步骤

1. 玩家正常退出并重启 NBA2K22，加载同一个 MC 存档，停留在可读取阵容的稳定菜单。首次对照尽量不推进赛程或修改名单。
2. 保留 `database/runtime_memory_map.json` 中的旧进程缓存，让生产代码识别进程变化；不得手动填入新地址或删除旧缓存后再声称恢复成功。
3. 确认当前游戏 PID 与基线 5224 不同，保留进程启动时间。
4. 运行以下命令，使用相同隔离存档和不同快照名：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run_admin_data_capture.ps1 -SaveId restart_validation_20261016 -Season 2022 -Month 1 -Name POST_RESTART
```

5. 检查第一次入库校准报告的 `previous_pid=5224`、`process_changed=true`、当前 PID、扫描日志及 HEALTHY 状态。审计阶段第二次校准可能已经命中新缓存；应以入库清单保留的第一次校准为进程变化证据。
6. 确认本批次真实入库并通过所有内存抽样检查，GM 只读取新的已审计批次。对照前后姓名、球员身份、球队阵容、合同和已观测数值。原始结构可能含运行时指针，不能要求跨进程所有 BLOB 字节不变；任何业务字段变化必须能从新内存解释。
7. 再执行一次同一新 PID 的普通采集，使用 `POST_RESTART_REPEAT`，验证新缓存可复用且更新成功。保留两轮清单、审计和日志。

## 当前可复用命令

```powershell
# 只读权限及锚点验证
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run_admin_data_capture.ps1 -CalibrationOnly

# 临时缓存的进程变化模拟及全部球员原始数据复核
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run_admin_data_capture.ps1 -SaveId restart_validation_20261016 -RescanOnly

# 不读取游戏，验证不可读槽位会拒绝提交并保留旧正式球员表
python scripts/verify_capture_failure_guard.py

# 核验本次保存的三批数据库、清单、审计及实际重启证据
python scripts/verify_restart_capture.py --save-id restart_validation_20261016
```

管理员启动器日志在 `database/saves/_admin_runs/`。源代码和模板静态检查通过不能代替真实新进程验收。一次实际重启及一次缓存复用通过后，才能记录“该次重启恢复通过”；跨多次重启的稳定性结论仍需更多实际重启证据。
