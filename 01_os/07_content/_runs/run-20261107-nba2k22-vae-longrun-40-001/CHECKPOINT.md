# Issue #40 第一阶段检查点

**母任务保持运行。** 当前工作单元处于 `EXPERIMENT_RULES_AND_LEDGER_READY`、`ONE_WINDOW_HARNESS_READY_OFFLINE` 和 `SEASON_DELEGATION_PROPOSAL_READY`。真实世界线绑定与委托激活仍有前置门。

- [字段覆盖总账](mechanism_research_ledger.json) · [构建器](build_ledger.py)
- [单存档实验规则](experiment_rules.md) · [首轮 H/L/C 离线计划](round_fixture_plan.json) · [真实赛程只读快照](current_schedule_observation.json)
- [§7.2 委托变更对比](season_delegation_review.md) · [机器合同候选](season_research_delegation.json)
- [66 场原始回执复核摘要](native_calendar_receipt_audit.json) · [验证收据](verification_receipt.json)
- [赛季停止与重绑定验收](season_checkpoint.py)

## 续接点

| 项 | 现场事实 |
| --- | --- |
| project_task_id / run_id | `NBA2K22-VAE-AUTONOMOUS-MECHANISM-DISCOVERY-LONGRUN-20261107-001` / `run-20261107-nba2k22-vae-longrun-40-001` |
| NBA / Core | `bb73a06e710158c538caf809a771eca291eee028` / `877077c16bad41cfa97c1ebc9862a70ce610ff0b`。实际共同祖先 `934425cf43d4fe3307b0112142aec1ba434a5734`。 |
| 历史源 | Stage02 `c812042e087f4c7000d27ac42d3839741039c188`。设计 `de874b64f40808269f8d68e3474989197d47e8fa`。R0 草稿 `87826a88acd9bf927c97a74dee36c56f7e31c887`。日历草稿 `80fbd8ba98e86d56fb57ef87c02cf97b83198225`。 |
| 当前现场日期 | 只读 REA 2022-01-07。1 月 7–13 日 50 场待赛覆盖 30 队。当前 Live 计划的 loaded slot、WorldData/worldline、season、UID/剂量还没有共同绑定。 |
| 计划与授权 | 合成计划摘要 `39596cd46d08b00309dde5ebb0d152b0c5af5a29b91bb7c457552e1de2819abd`。当前只有离线与只读工作，季委托待填充、待裁决。 |
| 已完成 Game ID | 历史日历 516–581 已复核。Issue #40 本轮实机完成 Game ID 为空。 |
| 日志与异常 | 合成 Journal 回归包括 UNKNOWN 拒绝重放。历史日历崩溃、`RaiseException` 原因、前台之外、保存和重载仍待 #39 核验。 |
| 恢复来源 | 此分支的精确提交和 GitHub 检查点。PRMS WriterGate 尚未在本阶段执行保存。 |

## 复算

在仓库根目录使用 Python 3.10+。需有账本记录的 Git 对象。先检查这些分支的当前远端位置，再以账本固定对象复算。

```powershell
$run = '01_os/07_content/_runs/run-20261107-nba2k22-vae-longrun-40-001'
python -B -X utf8 "$run/build_ledger.py"
python -B -X utf8 "$run/experiment_round.py" --seed 20261107
python -B -X utf8 "$run/test_longrun.py" -v
python -B -X utf8 "$run/window_harness.py" dry-run --journal "$run/_runtime/fresh-fixture-journal"
python -B -X utf8 "$run/window_harness.py" one-window --journal "$run/_runtime/fresh-fixture-journal"
```

在原执行环境可用 `audit_calendar_receipts.py <私有历史回执目录>` 重核逐场来源，脚本仅输出脱敏摘要。真实赛果应通过原 WorldData 同 Game ID、同 source unit 核验。

## 下一项安全动作

### V2 实机首轮（2022-01-08 至 2022-01-15，后者不含）

Human 已在 Codex 的活动目标中直接批准 V2 有界封套。隔离槽 `MyLEAGUE0005` 的同一进程内，首轮冻结 6 H、6 L、6 C 和 12 保留队。S4 成功修改 12 队各一名球员，逐项通过 Getter/CAS 与写后读回。原生日历实际调用 5 次，4 次验证完成 50 场，另一次因游戏中断未完成。恢复后，精确重核旧调用的赛程均待赛且调度帧空闲。旧请求永久留存，新的单日请求完成该段首日，再完成余下两日。未重复 Setter。

两次绑定 WorldData 采集合并得到 47 场可用比赛。同一场仍要求同采集单元的球员与球队 Box，剔除比分不守恒的 598、612、620。相对同期对照，每赛程机会的候选球员 FGA 为 H–C **+4.54**（3 个完整分层）、L–C **−1.04**（5 个完整分层）。小样本且对手暴露相关，未估计可信区间。仅为筛选结果。

首轮结果为 `IN_MEMORY_ONLY`。第二轮从 2022-01-15 自动启动，11 队各一名球员写入并读回成功。第 12 个候选的球队 ID 为 31，超出现有 S4 Writer 的 0–29 认证范围。Planner 在 Native 调用前拒绝，原值读回与空 Native journal 复核后记为未执行。保留其余处理并自动续跑。后续分组仅允许认证球队进入 H/L。

第二轮四次 Native 调用共完成 54 场，于 2022-01-22 结束。48 场 WorldData 合格，6 场比分不守恒被隔离。每赛程机会的 H–C 为 **−2.94**、L–C 为 **−2.58**，各 4 个完整分层。H–C 方向与首轮相反，仍属筛选结果。第三轮从 2022-01-22 自动启动。未跨季、未主动保存，恢复时从当前精确 Outbox/日期续接，原始回执和 Human 授权只留私有运行目录。

| V2 轮次 | 游戏 Today 区间 | Setter 成功 | 原生完成场数 | WorldData 合格 | H–C / L–C FGA |
| --- | --- | ---: | ---: | ---: | --- |
| 3 | 01-22 → 01-29 | 12 | 50 | 44 | +0.18 / −3.06 |
| 4 | 01-29 → 02-05 | 12 | 51 | 45 | +0.61 / −1.44 |

前四轮合计 47 次成功处理、205 场原生完赛、184 场合格 WorldData。各轮有同期对照，前轮处理仍可能影响后轮队友和对手，不作为独立复验。第五轮 12 项 Setter 已读回，首个 02-05 → 02-07 原生调用遇全明星弹窗。Human 处理并手动推进后，REA 确认同一进程的 Native Today 为 02-22，旧目标场次已全部结束。保留旧调用记录，将该轮及人工推进区间排除于自动效果分析。02-22 → 02-24 原生推进只覆盖两天空档，0 场比赛，02-24 的赛程仍待赛。第六轮从 02-24 自动开始。

V2 runner 复用 #42 日历候选 `ada6f300` 和 R0 资格导出 `87826a88acd9bf927c97a74dee36c56f7e31c887`。同一 Outbox 保留所有 Native 申请和回执。不要从新的输出目录重启已开始的轮次。

[MyLEAGUE0005 实测检查点](FRESH_0005_CHECKPOINT.md) 记录六来源采集、30 队七日候选及 #39 单日实机回执。1 月 7 日的 9 场已完赛，1 月 8 日的 6 场仍待赛。该结果仅覆盖内存状态。

[WorldData 接入进度](WORLDDATA_CHECKPOINT.md) 保留管理员只读进程核对和真实历史样本的 30 队复算。

继续同一母任务。[#39 草稿 PR #42](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/42) 的固定提交 `be0d7f65a767274830cb9644a42b96f53e025d3a` 提供测试专用归档。该版本已在限定窗口内完成一次原生模拟并通过离线原始回执复核。保存重载与赛季委托仍待验证或批准。

恢复现场工作时，先只读核对槽、进程、日期与赛程，再按新状态冻结新的处理窗口。禁止重用 1 月 7 日七日候选或已消费的单日许可。赛季自动多批次仍须通过 Save/reload 验证和明确的分项授权。
