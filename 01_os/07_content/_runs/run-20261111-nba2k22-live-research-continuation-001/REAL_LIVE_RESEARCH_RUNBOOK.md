# Issue #40 首批实机研究

任务合同为 [Human/GPT 2026-11-11 执行任务](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40#issuecomment-6794780940)。工程源固定为 PR #43 的 `1372d1b62467dbd6fa51a9db24f0c4feaff40a1c`。

Human 最新指令“直接开始，不用做检查，就是给你准备的。”作为本次立即执行 0005 单步资格试写的指示。具体矩阵来自本次真实读数，最多 16 个不同槽、每槽一个不同 UID、一步改值、日历预算 0。程序通过现有 QualificationDelegation 将父矩阵分为各自最多 3 槽的子封套，保留父文件 SHA 与原指令来源，复用 Host、Outbox、Native Bulk 和独立读回。当前现场原始回执保存在本组忽略的 `_runtime/qualification-live-final`，所有尝试共用 `_runtime/qualification-live-fast/outbox.sqlite`。早先两次封套在角色参数校验时被拒绝，未派发 Native 写入，证据分别保留在 `qualification-live-fast` 与 `qualification-live-repaired`。

正式研究矩阵是 W01–W03 的 153 场、15 字段、60 H/L 席位和 12 次原生日历短窗。三窗发生在同一条连续世界线，累计旧处理与对手暴露。操作表和当前过渡缺口见 [冻结计划](FIRST_BATCH_FROZEN_PLAN.json) 与 [PLAN_DELTA](PLAN_DELTA.md)。

单步资格操作会改变当前内存中的测试字段。资格完成后，Human 需要重新加载尚未被保存的原 0005，随后建立正式研究绑定。程序始终核对 0005 与冷备指纹，任何不确定 Native 结果均停止，不自动重试。正式研究的场次、写入数和结论以真实回执累计，首批不作为母任务结束条件。
