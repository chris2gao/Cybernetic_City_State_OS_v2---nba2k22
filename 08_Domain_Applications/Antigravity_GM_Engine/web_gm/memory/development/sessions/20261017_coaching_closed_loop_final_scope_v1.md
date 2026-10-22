# 2026-10-17 · 教练战术系统闭环需求定案（DEV-20261017-07）

- 角色：Web GPT DEVELOPMENT，状态：`SPEC_PUBLISHED_AWAITING_CODEX`，无正式游戏写入、无PR合并或代码实现。
- 项目：`chris2gao/nba2k22-gm-engine`，已有[PR #1](https://github.com/chris2gao/nba2k22-gm-engine/pull/1)，HEAD `5daeed8dc0001b5052dce1cfc97d6c22ee9317c3`仍OPEN未合并至main（本轮查询）。
- [新Codex任务书](../../../../docs/development_tasks/DEV_20261017_07_COACHING_GM_CLOSED_LOOP_V1.md)，创建提交`1aa5c2bacff2aaab80f4c7bb6c2b4c8c00f40d34`。

## 最新用户四项要求
1. 快速模拟比赛效果**完全不需要**，从教练系统技术完成/上线验收中删除，也不再强制玩家跑一个月来证明功能有效；未来游戏表现可按GM经营需求分析，但非此模块研发门槛。
2. 用户要详细查看余下18项主教练默认字段：5 SimPace/Press/HelpDef/OffReb/DefReb；2 PreferredSystem/ActiveSystem；1 PlaybookID；6 BenchDepth/RunPlayTendency/ZoneUsage/BenchUtilization/Tempo/HelpDefense；4 FreelanceType～FreelanceType4。共有24项默认，其中6POE正式生产允许，另18项不自动升权限。8项编码待验收，10项只读。可以先完成核心闭环，以后用户选择再逐项扩展。
3. 必须实现**30支球队批量受控执行**：严格整批玩家批准、所有目标先核查后0/全执行、预像刷盘、逐共享块掩码写入、回读、失败条件逆序恢复及人工恢复日志；RAM中跨30个对象无真正物理瞬时原子提交，因此不作绝对“硬件原子”保证。
4. 必须把原生COACHDATA教练战术**随用户正常触发的数据采集加入SQLite，正常导出及-Publish时一起发布到GitHub**，供网页版GM从现有`latest.json→batch_path`使用；不能自动发起采集、上传、GM或执行，也不允许把旧TEAM poe_*伪装为新战术。

此外工程完成须交两份**与真实代码接口一致**的操作手册：
- `web_gm/manuals/GM_COACHING_OPERATIONS.md`：网页GM能读取什么、合法枚举、30队HOLD/PROPOSED、球员/教练身份、JSON批次协议、审批和禁止操作。完成后接到GM_BASELINE/GM_SOP及GM_CURRENT。
- `docs/40_COACHING_EXECUTION_RUNBOOK.md`：Codex EXECUTION如何验证整批批准和原值、关闭Coach Gameplan编辑页、CLI实际调用、预验证、写入、回读、恢复、异常码、回执；完成后接到docs36/28/34。
当前docs39仅为Codex V1接口说明，不可替代上述两份角色手册。

## 当前仓库细节
- V1代码6POE已在隔离环境验证并在PR #1，另18中5Sim/2体系/1Playbook有合法enum编解码但未生产验收，6滑块/4Freelance只读；指定对手Gameplan 870条只读，IsInUse语义未知，仍不得写。
- 生产入口`scripts/run_data_update.ps1`用户触发，`-Publish`才同步GitHub；当前coaching snapshot是独立`development_only_sources`，缺生产SQLite/JSON集成。
- `src/gm_core/coverage.py`对旧`team_state.poe_*`返回None，因此新native coaching source需修正/新增GM评估读取映射，否则发布了也读不到。
- 缺V1多队原子批次；现有单队`src/coaching_executor.py`具外部批准、全共享块前值检查与条件rollback，不应仅for loop 30次来冒充整批事务。

## 研发与审批原则
任务书现在已发布到GitHub main；并非Codex已开始工作。Codex应在PR #1开发分支后续提交，并按测试真实情况更新文档、后续再由玩家决定merge。无默认30队真实战术修改权限；玩家对具体GM批次逐次单独批准。代码完成通过批量、采集、发布、双手册端到端技术检查后可宣布系统基础版可用，**不要求赛果/胜率测试、不要求18项全生产开放、也不要求29个对手覆盖**。
