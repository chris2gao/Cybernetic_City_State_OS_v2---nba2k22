# EXPERIMENT_BATCH_01：待Human整批批准

已知场景：Human确认终极联盟、日历页、独立测试存档；球队为印第安纳，其他测试输入委托Owner选择。批单批准同时请确认该测试存档可恢复。

批单SHA256：`b6074763b5260c5ac6e30a454ecb6a8a832853ec6f1afb964ea0ee3b10f4d8a8`。

精确机器批单与六份已生成脚本位于`prepared-experiment-batch-01/`，每份Script SHA256及全部源文件指纹已写入batch.json。生成脚本的Node语法解析已通过；没有执行它们。

|顺序|Case / Action|精确输入与作用|游戏业务函数预算|
|---|---|---|---|
|1|team_read / READ_TEAM_ROSTER_BASIC|team_id20；必须当次读到IND；名单身份子集，不是全量采集|0|
|2|coach_before / READ_COACH_CURRENT|team_id20；记录当前Coach关联、三引用槽和10个已绑定字段|0|
|3|public_prospects_read / SCOUT_LIST_CURRENT_PUBLIC_PROSPECTS|limit20；当前届次公开身份，不读隐藏能力/潜力|0|
|4|scout_budget_before / SCOUT_READ_TRIP_BUDGET|team_id20；次数、0..3目标槽、每槽至多17项公开身份；不消费次数|0|
|5|coach_new_field / COACH_SET_KNOWN_CURRENT_SETTINGS|team_id20，RunPlayTendency raw55；只在1/2确认IND及Coach互链、三引用槽NULL后，调用RVA0x146eaa0一次|1|
|6|coach_after / READ_COACH_CURRENT|独立新附加只读同一Coach；核对目标55和其他9字段；缺少修改回执时也只读一次，不重放Setter|0|

**总上限**：6次有限附加、1次游戏业务原生函数调用；每脚本最多1MiB读取、GUI线程Hook最多4秒、REA观察15秒。只读脚本仍需要Frida注入、短时Hook及Windows窗口API，因此也属于待许可范围。无自动替换参数，无原防守14→13或1对1交易重测。

固定EXE SHA256：1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5。当前命令宿主不是管理员。批准范围包含**一次显式管理员批次启动**：优先通过标准Windows UAC启动此已哈希源码中的run_validation_batch.ps1；若系统显示UAC确认，需要Human正常允许。脚本自身不隐式提权、不关闭安全工具。先核实唯一进程PID、启动时间和EXE，再锁定整批；进程变化、构建不符、对象不可读或写入资格不符均不执行相应业务。

预期：Native返回后当前Coach新字段等于55，独立读取确认，其余9个已绑定字段保持；函数内完整352-byte投影应与预期相等，原Gameplan保持。若原来已是55，记录ALREADY_AT_TARGET_NOT_NEW_EFFECT，不临时换值重试。回执缺失时只核对独立读数，不能仅因目标值相符就断言函数正确执行。

停止与恢复：单次提交无自动重试。Setter异常/不明后只做该批已列出的独立读回，状态仍不明就停止业务。效果留给Human查看；不保存、不推进日历、不安排SaveReload实验。游戏自身是否自动保存未经观测，不能宣称禁用了自动保存；如需恢复，由Human使用可恢复的测试存档。

球探分派：本批先获得真实公开UID和可用槽。随后由Owner按Human委托选定一个明确UID，生成SCOUT_ASSIGN_TARGETS的精确脚本和后续批单；本批不消费考察次数。选秀、签权交易和所有未具备调用资格的候选均不进入本批。

许可来源要求是本次任务书第四节的“收到Human对整批动作及测试存档的明确许可之后才使用管理员Codex/REA附加真实游戏并实际运行”；当前批单尚未获批，之前已消费许可不复用。
