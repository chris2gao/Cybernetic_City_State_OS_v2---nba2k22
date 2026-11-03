# EXPERIMENT_BATCH_02：指定球探追加的原生拒绝及Player Reader

待Human批准。继续同一可恢复MyLEAGUE日历测试存档，锁定PID10940及启动UTC2026-10-28T06:38:23.0486449Z。首批已读取IND三Goal槽已满、剩余次数raw7。Owner依据Human“球探部分可以自己设定值”的委托，明确选择已观察到的Sam Perkins UID33143；不换队、不删除旧目标来制造成功。

批单SHA256：`7c7d45475ded7bd5a72b24b986baf5a00424b26a9c32bcb166f5804b365ed4f6`。精确输入、源码指纹、七份程序及各自哈希见`prepared-experiment-batch-02/batch.json`。

|顺序|Action与输入|预算/检查|
|---|---|---|
|1|READ_PLAYER_PROFILE_ATTRIBUTES_TENDENCIES_BADGES；player_id7239（实际IND名单Malcolm Brogdon）|Native player.by_id一次；只身份/合同已绑定子集，不读能力/倾向/徽章或潜力|
|2|SCOUT_READ_PROSPECT_INFO；player_id33143|公开身份/原始排名字节；只读，UI排名换算UNKNOWN|
|3|SCOUT_READ_PROGRESS_RAW；team_id20/player_id33143|目标当前raw点数/标志，不等于已解锁报告|
|4|SCOUT_READ_TRIP_BUDGET；team_id20|新会话核对3个旧Goal及公开UID、次数|
|5|SCOUT_ASSIGN_TARGETS；team_id20/player_ids[33143]|initialize_goal→focus_specific→append_goal，共3次外部原生调用；前三分之二只构造私有Goal，最后一次让原版处理容量|
|6|SCOUT_READ_TRIP_BUDGET；team_id20|独立读回目标槽/旧身份/次数；拒绝不得改变旧Goal|
|7|SCOUT_READ_PROGRESS_RAW；team_id20/player_id33143|独立读回目标raw点数/标志|

总上限7次有限附加、4次游戏原生函数调用（其中1次是Player只读Getter，3次为指定球探请求链）。每程序读预算1MiB、GUI Hook4秒、REA15秒。具体代码与第一批同样使用Facade、生成器、明确启用的LiveExecutionContext和管理员进程；包含一次显式标准UAC管理员批次启动。

本例预期原生Append在3槽已满时返回0，记REJECTED_BY_GAME，独立核对3个旧Goal和raw7不变。如果在运行前上下文已改变，按实际Native结果和独立读回报告；不改变指定参数，不另找队伍或候选重试。没有SCOUT_EXECUTE_CURRENT_TRIP，不消费次数，不覆盖或删除旧目标，不推进日历、不保存或安排SaveReload。若结果缺失，只独立读回，状态仍不明则停止。

第一批Coach55效果保留，不重测或恢复。本批不会把“拒绝路径验证”升级为“球探分派成功”；成功分派仍须有空余目标槽的另一次明确任务/场景。
