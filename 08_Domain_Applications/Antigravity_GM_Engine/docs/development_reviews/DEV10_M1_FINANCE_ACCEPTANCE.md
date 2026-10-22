# DEV10 M1财务实现回执

状态：`IMPLEMENTED_LOCAL / WEB_CONNECTIONS_DEFERRED_BY_PLAYER`。基于设计提交a311e53实现；本回执只证明本地派生财务工具，不证明未来金额语义已认证、经济规则已获批或游戏合同已写入。

## 交付与设计要求对应

| 交付 | 证据 |
| --- | --- |
| 同批完整输入与三年投影 | finance_inputs复用M0查询分页；finance_projection为纯函数，槽位假设逐球员/年标记 |
| 已知小计、完整总额、选项/延期、未知传播 | 7项focused unittest中的partial/known/option案例；未知不删除可算部分 |
| KEEP/内部优化/市场方案 | finance_scenarios返回三种比较；球员/简单签所有权移动、重复拒绝、合同替换不双算 |
| 实际CLI及工作台 | gm_finance.py project/compare/show/list/export；独立库、不可覆盖run、事务与只读读取 |
| 30队三年、三队钻取 | M02静态副本CLI实际生成30队×3季，钻取GSW/SAS/CLE；见机器证据 |
| 批准/执行隔离 | 所有结果ANALYSIS_ONLY/NOT_REQUESTED，签约候选BLOCKED_EXECUTOR；无执行器导入 |

实际运行：`test_gm_finance_m1.py` 7项通过；`scripts/check_gm_finance_m1.py` PASS_LOCAL_STATIC_DEVELOPMENT，包含合同小批明细、KEEP零差额、三种比较和精简导出。工作台仅在开发_exports新建，事实库只读。证据：[DEV10_M1_LOCAL_EVIDENCE.json](DEV10_M1_LOCAL_EVIDENCE.json)。

读取批次：mc_haliburton_2021 / 2021-12-12 / 2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2。明确传入base_season=2021-2022；没有假称快照自动观测了赛季过账。机器证据的三年数值为SLOT_SEQUENCE情景，known_salary_subtotal=null、finance_eligibility=UNKNOWN、signing_capacity=null符合当前证据。

未运行Web连接、cash原生核对、全项目测试、新采集/发布、报价竞价、比赛模拟、正式GM、签约/交易/教练游戏写入。既有source_catalog与执行能力表不需改变：本轮新增派生计算，不新增观测来源或业务执行器。使用手册见[GM_FINANCE_WORKBENCH](../GM_FINANCE_WORKBENCH.md)。
