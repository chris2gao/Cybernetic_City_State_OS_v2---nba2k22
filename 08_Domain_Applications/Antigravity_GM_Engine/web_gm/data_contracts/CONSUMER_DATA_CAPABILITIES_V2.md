# DATA_ACCESS_CONTRACT_V2 — SQLite消费者能力

工程范围：DEV-10 V2/M0。权威实现与命令见 [操作手册](../../docs/GM_SQLITE_QUERY_ACCESS.md)。

2026-10-19后续实现：玩家另行授权的M1/M2已提供[财务CLI](../../docs/GM_FINANCE_WORKBENCH.md)和[知识/策略CLI](../../docs/GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH.md)，可从同批静态来源创建派生财务run、检索少量参考、维护显式策略revision。工作台写权限由玩家后续建立的运行边界单独分配，M0事实消费者ACL不自动授予派生库写权限。知识查询不要求完整联盟预载；30队候选仍未评估。这里只登记本地能力，不声称三个Web角色已连接或已使用，不启动正式GM或切换V4。

玩家开发中最新修正：三个Web模型实际连接由玩家在工程完成后建立；本轮仅实现和PowerShell本地验证，连接问题以后修复，不阻塞交付。所有角色保留 `DEFERRED_BY_PLAYER_NOT_TESTED`，不冒称 `M0_CONSUMER_ACCEPTED`。

|角色|权限与可消费内容|当前证据|
|---|---|---|
|CODEX_CAPTURE|玩家触发全量更新；从同批审计双库backup建查询副本|既有备份复用；M02本地恢复与CLI验证|
|WEB_ANALYTICS|本地只读CLI；按队/岗位/球员池筛选和SQL聚合；写派生报告不写事实|接口已实现，Web连接延后|
|WEB_GM|同批名单/合同/能力、19教练、18对手防守、8岗位、简单三届签位；只在玩家触发时提案|接口已实现，Web连接延后；经营规则未切换|
|WEB_DEVELOPMENT|版本/索引/字段覆盖、访问问题、四队现金与字段语义|接口已实现，Web连接延后|
|CODEX_EXECUTION|可读来源；本工具不授予任何游戏写权限，原批准机制不变|没有调用执行入口|

每条响应的 `access_contract` 记录 `role/career_id/batch_id/query_version/requested_data/actual_row_count/field_coverage/success/error/verified_by/verified_at/tool_used`；角色为声明值，**不是认证令牌**。消费者权限由专用非管理员本机账号和ACL提供，数据库以mode=ro、query_only与authorizer再约束。

业务行只认证实际所选snapshot来源；SQL计算、签约资格UNKNOWN、有符号cash假设、未在队模型、岗位候选都有独立语义，不借表名或非空值升级事实。窗口换角色/换batch时重新status；输出条数/分页和缺口必须一起交接。GitHub只回传精简摘要/来源/回执，原始库/路径/内存地址不提交。

五个关口分别为：CAPTURED、AUDITED、PUBLISHED或LOCAL_AUDITED、QUERYABLE_BY_ROLE、ACTUALLY_USED。当前发布审计事实证明前三项；Codex本地验证证明本地CLI可查询，不替代Web角色后两项。机器可读本地结果见 [M0证据](../../docs/development_reviews/DEV_20261018_10_M0_LOCAL_EVIDENCE.json)。
