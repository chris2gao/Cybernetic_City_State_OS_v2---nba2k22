# 有界审核修复 — 最终工程状态

任务仅 F-01/F-02/F-03，原常规赛连续开发任务保持关闭。

F-02 已实现共享 strict_box_coverage：schedule 与 game_box 使用同一严格参与者/球队/得分契约，并按UTC及微秒选择同一观察单元。
三个必需反例、正常匹配、未解析身份、更新的仅Native部分单元和时间排序均已有测试。

F-03 已实现原始 receipt 再验证及独立冲突落账；不为改写的payload伪造receipt，保留LIVE_READ和原始artifact hash，仅存提议digest/对象ID/错误上下文。
20个真实采集adapter统一使用冲突隔离边界；隔离结果通过 CaptureQuarantined 明确作为非接受结果上报。
inspect-conflicts 为owner诊断入口，普通GM history/export仍不能读取fact_conflicts。
受控测试独立数据库中的LIVE_READ仅验证receipt契约，不代表本任务访问了真实游戏。

最终证据：28项 F-01/F-02/F-03 针对性测试通过；精确候选 b847f717df6702fe6251872d64aed476ac707f6f 的受控run与inspect成功，329项完整回归、smoke和最终副本旧事实核对全部通过。
首次隔离实现使用了既有completeness枚举之外的标记，测试正确拒绝；修正为已有PARTIAL，隔离状态独立由source_key和fact_conflicts表示。

F-01 已实现并通过最终必要验证。当前状态 candidate_ready_for_independent_review；独立审核及master集成尚未执行，不宣称完整底层/生命周期验收。
实现：保留年度基线一次门禁；补录明确锚定该基线，采用证据引用与有界显式选择器，仅完整读取目标记录，教练额外读取必要引用目录。没有自动全生命周期发现器。
四族原typed事实表继续保存实际值，增量身份/幂等索引仅存hash与typed记录指针，不把业务事实改成JSON/EAV。
Native重复读取成本必须由真实collector路径记录；不能先全读再靠SQL去重冒充Native增量。
同年阶段性荣誉可以追加原生来源观察，但未证的Native标志/矩阵不会因此自动变为已确认canonical奖项。
已有canonical冻结事实冲突继续隔离交Human；schema变化必须新副本迁移并逐表证明原v24未变。

已验证：2022一次基线后三阶段原生荣誉追加、重复事实/请求幂等、已知荣誉撤回与canonical奖项冲突隔离、显式原生字段新值及缺失零值、四Reader路由与目标字节读取成本。
最终v25副本已证明100旧表/1470952原行原值不变；14条新字段登记单列验证，90455条派生幂等索引回填，原件hash保持不变。101表/1789列/1561421行，仍42个真实成功单元。
四族真实副本分页及12场schedule/Box一致性审计通过；四片连续gzip快照的逐片与解压hash通过。原绑定仍指向v24。
工程收尾与交接见 CLOSEOUT.md、NEXT_TASK_HANDOFF.md、08_结论/review_fixes_completion.yml；实际发布提交及远端回读见08_结论/publication-receipt.json。
完成普通工作分支交付后停止，不推进后续场景，不合并master；游戏进程读取/写入/日期推进/Computer Use/新真实采集均为0。
