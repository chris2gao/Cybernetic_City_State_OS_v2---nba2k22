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

[MyLEAGUE0005 实测检查点](FRESH_0005_CHECKPOINT.md) 记录六来源采集、30 队七日候选及 #39 单日实机回执。1 月 7 日的 9 场已完赛，1 月 8 日的 6 场仍待赛。该结果仅覆盖内存状态。

[WorldData 接入进度](WORLDDATA_CHECKPOINT.md) 保留管理员只读进程核对和真实历史样本的 30 队复算。

继续同一母任务。[#39 草稿 PR #42](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/42) 的固定提交 `be0d7f65a767274830cb9644a42b96f53e025d3a` 提供测试专用归档。该版本已在限定窗口内完成一次原生模拟并通过离线原始回执复核。保存重载与赛季委托仍待验证或批准。

恢复现场工作时，先只读核对槽、进程、日期与赛程，再按新状态冻结新的处理窗口。禁止重用 1 月 7 日七日候选或已消费的单日许可。赛季自动多批次仍须通过 Save/reload 验证和明确的分项授权。
