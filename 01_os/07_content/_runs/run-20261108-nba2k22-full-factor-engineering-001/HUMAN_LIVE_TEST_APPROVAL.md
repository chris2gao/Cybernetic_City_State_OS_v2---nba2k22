# 首次字段资格验证候选

状态 `NOT_AUTHORIZED / NOT_RUN`。Issue #40 本轮批准工程开发。运行器只接受可丢弃测试槽 `MyLEAGUE0005`，`MyLEAGUE0003` 是冷备。参考赛程和候选剂量来自已留存的 0005 观察，启动前需重新绑定实际进程、存档指纹、Native Today、球员 UID、球队和合约球队。

| 候选字段 | Native 球队 / UID | 物理偏移 / 参数索引 | 历史观察 → 候选目标 |
| --- | --- | --- | --- |
| `SHOT_THREE_TENDENCY` | 0 / 1652 | `0x472` / 83 | 77 → 78 |
| `TOUCHES_TENDENCY` | 1 / 1516 | `0x499` / 122 | 60 → 61 |
| `UNKNOWN_RAW_BYTE_016` | 2 / 2456 | `0x467` / 72 | 尚无源单元读数。先只读取得字节，在注册域 0–100 内拟定一步剂量。 |

每项最多一个 setter，候选合计上限三次。每项先冻结真实 UID、当前字节、目标字节和 99 字节邻域。已知项读数有变时重新冻结候选，未知槽缺读数时没有可签署剂量。调用后读回目标字段及邻域并记录进程状态。遇到不一致、未知结果、存档或进程切换即停止，保留凭据。日历调用预算为 0。

已知项来自 [0005 保留的倾向源单元](REFERENCE_TENDENCY_VALUES.json)。候选 UID 来自 [合格球员池](../run-20261108-nba2k22-full-factor-plan-001/eligible_player_pool.csv)。表中是待审的候选矩阵，实际当前值和进程 epoch 要以一次新的只读预检为准。

只读入口 `SeasonCycleHost.read_factor_qualification_snapshot` 可读取上述三槽，包括 WorldData 命名视图未覆盖的未知槽。入口检查存档绑定、进程 epoch、前后日期与模式、Native UID 和球队归属，返回 99 字节邻域和指纹。该入口已用替身测试，尚未在游戏进程调用。

新增的独立入口是 `QualificationDelegation.run`。调用者需从 Human 交接获得 `nba2k22.vae.write_qualification.v1` 授权原始字节及可信 SHA-256。封套固定加载槽声明来源、进程和游戏日期、工作线绑定、两份磁盘指纹、Outbox 与日志位置、逐操作摘要和有效期。每个操作绑定一次新的完整邻域读数，仅允许一步剂量。批次先核对所有基线，然后经同一 SeasonCycleHost、Native Bulk 和 DecisionOutbox 逐个执行。Native setter 前有 99 字节比较，执行后用独立读回再次检查仅目标字节变化。异常或未验证回执终止该封套。日历上限固定为零。

资格入口保留单次验证证据。普通窗口接纳新字段时，必须使用独立审核接受的 `nba2k22.vae.accepted_tendency_qualifications.v1` 清单，并在新的实验授权中绑定同一清单的 SHA-256。每条清单要绑定真实 Native 计划、原始回执、独立读回的摘要与审核引用，入口另外核对槽位置、对象身份和前后邻域。当前仍无新增真实资格，样本和测试属于离线验证，实机资格为 `NOT_AUTHORIZED / NOT_RUN`。持久化和篮球效果需要独立证据。
