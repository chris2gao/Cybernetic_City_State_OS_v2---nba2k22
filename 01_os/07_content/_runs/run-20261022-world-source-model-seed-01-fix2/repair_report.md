# WORLD-SOURCE-MODEL-SEED-01 — 第二次有界修订

执行修复候选；最终独立复核待另一会话完成。本报告不替代阶段 B 的原审核结论。

来源：原始候选 `142531f2d60813bce5b90254c5e347050c40b406`，审核版本
`8cdbfaefbcb001c6ca0612017957c6414876eea4`；工作分支
`task/world-source-model-seed-01-fix2` 从审核版本延续，保留审核材料与历史证据。
本轮 fresh-read 远端 master 为 `407e2134bd2f595477099b2c6e3484c818059fd9`。

## 修复及证据

| Finding | 实际变更 | 执行验证与保留边界 |
| --- | --- | --- |
| B-01 | 12 个 R00 项分别登记来源起点、对象范围、方法、正反例、样本/区域/20 分钟上限、结果、UNKNOWN 和两条不同失败路径后升级合同 | R00-10 使用 save_context、DEV14 workspace 与实际加载确认的限制，不使用 world_draft_season 作为身份；R00-11 明确四个设置根、两个具体设置及 default/target/observed 区分；R00-12 链接三个具体 action_id、原始来源和只读来源。全部 NOT_RUN / NOT_DISPATCHED |
| B-02 | 74 条受同类生成规则影响的字段改为基于原始对象及记录粒度的语义归属，附来源对象、候选身份、时间、关系和原 entity | DraftPick、PickOwnership、SeasonTotals、PlayerGameStatline 分开；菜单配置不冒充交易事件，当前球队/合同球队指针分别归属 RosterMembership/Contract；未知 player/season/game/team/stint 关联均 UNKNOWN。详见 semantic_change_manifest.json |
| B-04 | 新增两套历史倾向偏移的冲突条目；AG01D 及 99 原生槽都链接冲突和 R00-04 | 保留 AG01D 原 `0x170..0x260` 与 R04/Profile `0x458..0x4BA`；不选地址，不认证当前 build；修正 AG01D 的 NH_CAREER/职业历史邻域为 NH_TENDENCIES |
| B-05 | 在目录内为六个 HUMAN_DECISION_20261022 引用建立注册映射 | 精确绑定原候选 human_task.md 第 3 行、40 位 SHA 与原始 blob SHA256；保留年龄候选公式、独立存档、无跨档动态继承；Human 规则不升级为引擎公式 |

仍保留 888 条字段、75 历史槽、207 全部禁止执行的 action 和 12 个未派发任务。
原始来源引用、原始状态、native hints 和字段认证标志未因语义归类而升级；domain 仍作为
发现导航分组，实体归属以各字段的 semantic_binding 为准。

## 验证口径

专项计划有九项必需检查：旧种子不变量、字段语义、来源关系、倾向冲突、Human 引用、
R00 队列、16 个反向变异、范围/证据保存及执行 MWU 合同。新 managed run 与 inspect
须绑定已提交的干净 SHA；实际退出码、日志和原始证据引用以 completion_pointer.json
及 verification_receipt.json 为准。开发期诊断成功不能替代上述候选验证。

边界：这些检查证明离线目录修复及其否定用例，不证明 888 条逐项实机认证、原生读取、
游戏效果、持久性或新一轮独立审阅。R00 只是可复查的调查输入，Human 决定是否另行启动。

## B-03 与停止边界

本轮不修改原 run、原审核文件或原机器 attempt；对原 attempt 全部文件及 hash 做保存比较。
原目录严格 Inspect 的历史问题仍由证据所有者处理；本报告不声称它当前 Inspect 通过。
本轮新 attempt 是新候选的验证，不能替换或“修复”原 attempt。

本轮属于第二次定点修订。若专项检查后仍有重大语义阻断，保留证据并返回主规划窗口裁决；
不展开第三轮无界修订。最终独立复核及 master 集成均未在本窗口完成。

## 实际新候选验证

候选 `0f5bb86b3640a1607a03e7765795d12a5f2110fb`：OS Preflight=0、Managed Run=0、Inspect=0，九项必需检查全部完成；16 个反向变异全部被拒绝。新 attempt 的 48 个文件按原始字节归档于 `verification/candidate_attempt/`，外围调用日志单独保存，未混入严格 attempt。

该结果只绑定上述修复提交；本次收尾提交保存验证证据和完成指针，不冒称原 B-03 attempt 已通过。最终分支 SHA 由发布后远端读回报告。
