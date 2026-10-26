# 有界审核修复 — 施工状态

任务仅 F-01/F-02/F-03，原常规赛连续开发任务保持关闭。

F-02 已实现共享 strict_box_coverage：schedule 与 game_box 使用同一严格参与者/球队/得分契约，并按UTC及微秒选择同一观察单元。
三个必需反例、正常匹配、未解析身份、更新的仅Native部分单元和时间排序均已有测试。

F-03 已实现原始 receipt 再验证及独立冲突落账；不为改写的payload伪造receipt，保留LIVE_READ和原始artifact hash，仅存提议digest/对象ID/错误上下文。
20个真实采集adapter统一使用冲突隔离边界；隔离结果通过 CaptureQuarantined 明确作为非接受结果上报。
inspect-conflicts 为owner诊断入口，普通GM history/export仍不能读取fact_conflicts。
受控测试独立数据库中的LIVE_READ仅验证receipt契约，不代表本任务访问了真实游戏。

当前证据 evidence/review-tests.json：14项 F-02/F-03 针对性测试通过。
首次隔离实现使用了既有completeness枚举之外的标记，测试正确拒绝；修正为已有PARTIAL，隔离状态独立由source_key和fact_conflicts表示。

F-01 尚未完成，任务不能交付为全部修复完成。
实现方向：保留年度基线一次门禁；补录明确锚定该基线，使用受验证的有界Native目录/摘要发现变化，仅完整读取和保存新/变化记录。
四族原typed事实表继续保存实际值，增量身份/幂等索引仅存hash与typed记录指针，不把业务事实改成JSON/EAV。
Native重复读取成本必须由真实collector路径记录；不能先全读再靠SQL去重冒充Native增量。
同年阶段性荣誉可以追加原生来源观察，但未证的Native标志/矩阵不会因此自动变为已确认canonical奖项。
已有canonical冻结事实冲突继续隔离交Human；schema变化必须新副本迁移并逐表证明原v24未变。

待完成：F-01四reader选择性路径、SQL门禁/幂等与查询，2022同年分阶段反例，v24真实副本迁移/所有旧行比对，完整必要回归/smoke，OS完成指针与正式交付后停止。
