# 首批真实结果：新Coach字段已独立读回

EXPERIMENT_BATCH_01已按Human批准执行。游戏PID10940，启动UTC2026-10-28T06:38:23.0486449Z；完整EXE SHA与固定构建一致。原始REA返回、精确程序、管理员目标记录及逐文件哈希在batch-01/。六个有限附加均有一个结果，无消息截断或脚本错误，cleanup_error均为null；归档中的state=running是返回快照，不冒充持久会话仍存活或DETACHED状态。批次管理员launcher已退出且exit_code0。

|验证目标|实际结果|证据边界|
|---|---|---|
|IND名单Reader|team_id20对应IND，15人；首项Malcolm Brogdon UID7239，当前/合同TEAM互链为true|真实身份/名单子集；财务raw值没有UI单位证明|
|Coach Reader|Rick Carlisle，互链true，三引用槽NULL，10个绑定字段可读|未验证完整员工/轮换/持久Gameplan|
|公开候选Reader|当前公开列表20项，包括Michael Jordan UID33142、Sam Perkins UID33143|只身份；不解读为完整报告或隐藏属性|
|IND球探槽Reader|franchise record index18，3个Goal已满，remaining_trips_raw7；每Goal当前11个候选可映射UID|原始槽/次数与身份；非球探报告文本或评分|
|COACH_SET_KNOWN_CURRENT_SETTINGS|RunPlayTendency **90→55**；原生RVA0x146eaa0一次返回，完整352-byte预期投影匹配，原Gameplan未变|只本例字段、当前Coach投影|
|独立Coach读回|新会话读到同一IND/Carlisle字段55，其余9个已绑定设置保持；原防守仍13|REAL_NATIVE_EFFECT_VERIFIED；未声称UI对应、SaveReload或独立审核|

本批游戏业务Native调用实际1次，无二次提交。效果留供Human查看。不保存、不推进日期；游戏自身自动保存是否发生未观测。原PR12两项成功未重测。

后续：UID已真实取得，Owner按Human委托选Sam Perkins UID33143作球探追加请求。IND三槽已满，因此预期原生Append返回拒绝，不删除/替换旧Goal，不换队制造成功。下一精确脚本须另列整批许可；可同时验证一个实际名单球员的独立PLAYER Reader。
