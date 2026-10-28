# 功能验证任务逐项证据核对（进行中）

本页在任务收尾时更新。真实成功只以本任务实际Native返回及独立读回为依据。

|任务书要求|当前权威证据|状态与边界|
|---|---|---|
|指定分支与PR14固定来源|task_packet.yml，基线0008af1，继承2bdda79；首批代码和原始证据提交8bda788|已核实；未修改PR12/PR14/master|
|第一步只读Team/Coach/Player子集|batch-01/team_read、coach_before；第二批player_read已准备|Team/Coach实际成功；Player独立Reader待第二批许可/执行|
|当前公开候选与球探进度/槽|batch-01/public_prospects_read、scout_budget_before；第二批精确prospect/progress已准备|20个身份与IND3槽实际可读；报告文本/隐藏评级仍UNKNOWN|
|至少一个此前未测的新Setter|BATCH_01_RESULT.md，batch-01/sequence-summary.json、原生/独立读取Evidence|REAL_NATIVE_EFFECT_VERIFIED：IND/Carlisle RunPlayTendency90→55，其他九设置保持|
|选择训练或新Coach设置，以实际上下文决定|本轮选择新Coach字段；未额外执行训练或创建对手Gameplan|满足一个低影响新Setter要求，不宣称训练已测|
|精确球探分派及原生容量拒绝|EXPERIMENT_BATCH_02，IND20/UID33143；已知三槽已满|待第二批批准；不删除目标、不换队，不通过别的操作假装追加成功|
|球探次数消耗独立许可|两批均不含SCOUT_EXECUTE_CURRENT_TRIP|NOT_REQUESTED_NOT_EXECUTED；剩余次数raw7已读|
|条件性真实选秀场景|Human当前场景为日历，没有当前选秀大会|DEFERRED_NO_SCENE；不调用Draft getter/selection，不推进日期|
|条件性签权/组合交易|本轮没有明确资产集合和对应许可|DEFERRED_MISSING_EXACT_ASSETS_AND_PERMISSION；不重新测试旧1对1|
|未知ABI服务保持不可执行|未调用签约、裁员、完整编辑、导师、完整轮换/Playbook|未用猜测参数放行；不扩成全面逆向|
|整批新许可/精确哈希/管理员运行|HUMAN_APPROVAL_BATCH_01.md，batch01 SHA，管理员target/launcher；batch02单列待批|首批实际符合；不会用首批许可覆盖第二批|
|只一次提交、缺少收据先只读|每case排他started标记，exact-script transport；首批完整返回且独立读回|没有自动重放、换值/对象、配平或业务优化|
|前后值、原请求、Native链、失败和成熟度差异|原始case/REA/script，native_live_validation.json，BATCH_01_RESULT.md|逐例证据；Generic动作仍只标已验证字段子集|
|不保存/不推进，不补持久性/交易历史研究|脚本无保存、UI操作或日历推进调用|未研究SaveReload；游戏自动保存是否发生未观测|
|更新能力登记与Draft PR|已实现Registry按动作附加live_validation证据；后续最终提交/PR待完成|任务尚未收尾，不用当前页冒充完成声明|
