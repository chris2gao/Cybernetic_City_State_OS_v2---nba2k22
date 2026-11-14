# NBA2K22 Native Calendar 测试专用入口

面向 [Issue #39](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/39)，供 [Issue #40](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40) 在满足前置后调用。能力、PE 构建、两份 JS 的源码摘要和证据等级见 [manifest](capability_manifest.json)。归档候选不进入生产动作注册表。

- `native_today.js` 是可直接用 REA file-backed Frida attach 的原生 civil Today 读数。它检查 PE、GameMode getter 字节和 vtable，仅从已绑定内存位置双读。公开结果的 `NATIVE_DATE_ONLY` 明确区分存档身份。
- `simulate_to_native_date.js` 是历史成功帧前方案的参数化后缀。Python 先提供固定计划，再拼接上面的只读源码。支持 1–2 日、Win64 固定构建、MyLEAGUE 常规赛、前台可见且非最小化、自然引擎线程入口 `0xbad3c0`、caller `0x17bcb95` 且无活动帧。唯一原生动作是 command 17 加选择日参数。旧帧内执行点从未进入新入口。
- Box 日期字段来自同采集单元的实际二次核验 Today。每批带编号，按完整 Game ID、队伍、计划/实际日期、原生 Final/WasSimulated 和双方比分与球员得分总和核验。次日待赛也检查。原始数据留在私有运行目录。

## 显式入口

在已设置的本机测试环境，用 Python 3.11+ 运行 `calendar_cli.py`。命令会调用项目已有的 `ReaCliTransport` 和 WorldData。此传输按现有规范要求已经授权的 Windows 管理员会话，并检查实际运行模块的 PE 文件 SHA。当前普通权限的 WorldData reader 返回 WinError 5。现有授权管理员采集端需先提供新鲜上下文。没有安装、提权或切换目标的隐式操作。

| 命令 | 输入与结果 |
| --- | --- |
| `read-native-today` | `--runtime --save-directory --loaded-filename --pid --read-ref`。将 REA 日期与 WorldData、操作人声明槽、epoch 交叉核对。 |
| `plan --plan FILE` | 离线校验并输出 canonical plan digest。不给运行时权限。 |
| `observe-frame --plan FILE --runtime DIR --read-ref REF` | 只读帧观察，可先用 `engine_thread=0` 且证据引用留空。用观察结果固定实际线程和独立 GUI 线程，再冻结正式计划。 |
| `simulate-to-native-date --plan FILE --runtime DIR --outbox FILE --execute-once --approval FILE --approved-sha SHA` | 唯一可写测试入口。缺启用标记、精确批准或现场校验时拒绝。 |
| `inspect --plan FILE --outbox FILE` / `audit --plan FILE --receipt FILE` | 前者只读共享 Outbox 占用，后者核验私有 REA 回执。保持 UNKNOWN 占用，后续由 Human 裁决并按原证据核对。 |

私有计划使用 [测试示例](test_calendar_cli.py) 的结构。实际运行还须填 `save_directory`、绝对 `database`、`cold_backup` 和现有 `outbox_db`。原生文件名由操作人确认，WorldData 保存隔离 worldline，文件哈希与冷备相互独立。计划保留批准的 Build/source SHA、完整 epoch、起止日、赛季停止线、当期无事件范围和每场两队。批准对象使用 `action, plan_digest, authorization_scope, max_dispatches, approved_by_operator, human_decision_ref, revoked, valid_from, expires_at`。SHA 由操作人从真实 Human 记录绑定，JSON 标记自身不提供身份认证。只有一个有界窗口和一次调用，最长授权 24 小时。

使用同一份已更新的 Host `DecisionOutbox` DB。日历在 `BEGIN IMMEDIATE` 事务中登记 intent，现有 S4 claim 同样在事务里检查日历。只有经过核验的内存完成或明确零 dispatch 可结束占用。UNKNOWN、调用中断、任何观察异常或缺少 Box 均保留占用。该互斥要求唯一操作路径，未经更新的 Host、其他 DB 或直接手写 Frida 命令均不在已认证运行条件内。

## 现场资格矩阵

| 条件 | 已有证据 | 未决 |
| --- | --- | --- |
| 前台可见 | 历史两段实机成功，候选归档版观察到自然引擎线程入口 | 新归档版写入未跑 |
| 可见但失焦、最小化、锁屏、远程断开 | 历史见过后台线程等待。各状态须分别核对 | 写入资格均未建立 |
| 帧内与帧前 | 帧内先推进后退出，帧前两段历史内存验证 | 崩溃根因未定位 |
| 异常 | 历史一次 `KERNELBASE!RaiseException`，旧脚本无码。新脚本记录该入口的异常码 | 归档版实机异常采集未运行，任何异常先停 |
| 保存与重载 | 历史磁盘未变 | 显式 Save、重载后 Today、完整 Game IDs/Box 需另批独立测试 |

首个短窗使用 [候选提案](../../../../../../01_os/07_content/_runs/run-20261107-nba2k22-test-only-calendar-39-001/short_window_proposal.json) 所列单日赛程。该提案需要现场重新绑定和 Human 针对确切摘要批准。后续保存测试、WorldData 刷新和多窗封套独立验收。
