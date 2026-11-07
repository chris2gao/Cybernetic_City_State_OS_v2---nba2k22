# SIM_THROUGH_DATE 控制合同候选

`sim_control.py` 是脚本化离线控制器。输入带存档、世界线、PE、进程 epoch、赛季与模式的绑定，以及起止日期、应完赛 ID、最大观察次数与匹配的 fixture grant digest。模块没有原生传输、日期写入口、Setter 或调度器。fixture digest 只绑定离线样例。真正的 Human 批准仍由现有审批与 Host 边界提供。

| 阶段 | 守门与失败 |
|---|---|
| preflight | 只读对比绑定、日历、ID 集合、完整性、场景及禁止跨越的事件。空赛程、已有进行中比赛、跨度不合法或目标不匹配时拒绝。缺 grant 只报告 dry run。 |
| reserve | 以 save/worldline 为键独占创建一次性 Journal，记录计划和摘要并落盘，再接收模拟帧。重启、改 epoch、改目标或重复运行仍持有旧 Journal。空或不完整的 Journal 也须先由 Human 调和。 |
| observe | 模拟与保存期间保持等待。检查日期不回退/不越界，赛程身份与窗口不漂移。对话框、未知状态、进程或赛季切换转 UNKNOWN。轮次预算耗尽转 TIMEOUT_UNKNOWN，保留 Journal。 |
| reconcile | 空闲且到达目标后，逐场核对 final/simulated、Box 完整性及相同采集单元。全部通过才得 OFFLINE_COMPLETE。缺失则 PARTIAL_RESULT，保留证据。 |
| hold | UNKNOWN、PARTIAL_RESULT、完成或超时均保留一次性记录。进程终止与可能副作用必须另核。 |

后续如获批准，复用现有 S4/Outbox 做精确批次密封及 Setter Getter，另用独立的一次日历授权触发原生模拟。两类授权分别绑定：日历绑定存档、世界线、构建、epoch、日期窗、赛程、时限及停止点；Setter 绑定 plan digest、角色、对象、原值、目标值、有效期和同队 S4 上限。取得确认后顺序为 `seal → approved setter/getter → separately approved native sim → native readback → existing capture/SQL/Box verification → compare → checkpoint`。本轮 fixture 只覆盖日历部分，自动化扩权须另行审议。

游戏恢复到空闲且证据完整后才可考虑下一个新窗口。常规赛末交还 Human。进程/存档/模式变化、重大事件、场景阻断、授权到期、CAS 不符、结果未知、超时或缺少赛果一律停止。现有 Reader、WorldData、Host 和审批仍是各自原有层的入口。当前离线窗口约定为包含起止日并过滤已完赛，和历史七天半开区间、Native UI 转换分别处理，未来 adapter 必须在入场前冻结具体边界与场次名单。
