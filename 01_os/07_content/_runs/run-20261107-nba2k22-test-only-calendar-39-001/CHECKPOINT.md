# Issue #39 测试专用归档检查点

关联 [Issue #39](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/39) 和长期 [Issue #40](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40)。当前子工作单元交付测试入口与离线验证。实机短窗、保存重载与长期委托继续待前置。

| 项目 | 状态 |
| --- | --- |
| 基线 | NBA `bb73a06e710158c538caf809a771eca291eee028`，Core 规则 `877077c16bad41cfa97c1ebc9862a70ce610ff0b`。 |
| 日期入口 | 归档 JS 在当前进程只读返回 2022-01-07 00:00，mode 1、period 29。证据 `ev_76458e092cb418a53bf374dbab3e16a6191e8bc52b13479d7847099f55d428a6`。 |
| 帧入口 | 归档源生成的只读帧观察返回引擎线程 3056，GUI 线程 4192。识别空闲帧入口和精确待赛范围，未获得存档共同绑定。证据 `ev_1c07b3fa019ca0dc951dd10f3a0ce136b3f5eaee827b495df6064ac5d54a3d04`。 |
| 历史两段 | 原始 13+53 场已复核。日期标签缺陷在候选改为同单元读值。旧帧内崩溃和第二段 `RaiseException` 原因开放。 |
| 当前 Native 写入 | `NOT_RUN`。共享 Outbox 保守互斥、精确单次授权、次日与 Box 核验已离线验证。游戏仍响应，磁盘摘要与原冷备相同。 |
| WorldData / 重载 | 普通权限调用现有 `ReadOnlyGameProcess` 被 WinError 5 拒绝，完整绑定和实机 CLI 未跑。保存与重载 `NOT_VERIFIED`。 |
| 恢复与权限 | 用这份 GitHub 检查点和精确 SHA 恢复。PRMS WriterGate 未调用。旧 #36、#38 原始证据保持独立。 |

[入口和使用边界](../../../../08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tools/test_only_calendar/README.md) · [首个一日候选](short_window_proposal.json) · [验证收据](verification_receipt.json)

首个新实机窗口候选是 1 月 7 日的 9 场，验收 Today 进入 1 月 8 日，1 月 8 日 6 场仍待赛。下一步使用现有获准的 WorldData 环境冻结实际槽、数据库、世界线、赛季/事件、冷备、进程与唯一共享 Outbox，随后给 Human 提交绑定后的精确 plan digest。异常即停止。保存重载采用单独批准的测试，角色写入继续沿用已有 S4 批次审批。
