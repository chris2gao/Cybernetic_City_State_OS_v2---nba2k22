# Web GPT 三基线持久记忆规范（网页 GPT 专用）

本目录保存三类 ChatGPT 网页版窗口的**跨节点、跨聊天交接记忆**，不等于游戏存档、数据库事实、玩家批准记录或自动同步的聊天记忆。

**角色生命周期不同**：Web GPT GM 从基线派生**一个赛季一个决策聊天**，同季多个玩家触发节点持续使用同一聊天；分析与开发仍可一任务一窗口。GM 每节点单独存档、更新本季时间线和 CURRENT，但**节点结束不等于赛季聊天关闭**。只有玩家确认赛季结束并归档后，下一赛季新开聊天。因上下文限制转新聊天时以同赛季续接处理。任何新节点均不因新数据自动启动。

## 目录与权威程度

- `GM_CURRENT.md`：最近 GM 节点、当前游戏赛季、已确认与未批准事项及同一赛季聊天下一节点入口；不是“每月新开聊天”的指令。
- `DEVELOPMENT_CURRENT.md`：Web GPT 需求/规格/代码审核窗口近期结果与待办；**不是** Codex 的 `docs/34_BASELINE_CURRENT_STATE.md`。
- `ANALYTICS_CURRENT.md`：网页 GPT 分析端使用过的最后数据批次、已发布报告/JSON、可重用分析方法与缺口。
- `gm/sessions/<run_id>.md`、`development/sessions/<run_id>.md`、`analytics/sessions/<run_id>.md`：每次玩家触发的任务/GM 节点新建、原则上不可变的审计式总结。GM 还须维护 `web_gm/seasons/<season_id>/INDEX.md` 及其 `windows/Wxx_.../` 节点归档；Wxx 只是历史编号，不要求新开聊天。新聊天默认只读 CURRENT 与本季 INDEX，必要时沿链接读最近节点记录，避免上下文膨胀。

**优先级**：玩家当前明确指令 > `config/gameplay_policy.json` 与治理文档 22/26 > 最新已发布游戏事实 > 具有来源与玩家确认状态的历史记录 > CURRENT 摘要 > 旧任务聊天与旧示例。GM 经营阈值配置如仍为 PROPOSED，不是已批准球队指令。

## 单次任务记忆模板

每次任务写入 `<role>/sessions/<YYYYMMDD>_<topic>_<unique>.md`。示例文件内容：

```markdown
# 任务：<简要目标>
- role: WEB_GPT_GM | WEB_GPT_DEVELOPMENT | WEB_GPT_ANALYTICS
- run_id: <唯一 ID>
- status: COMPLETED | PARTIAL | BLOCKED
- career_id: <存档或 NOT_APPLICABLE>
- source_batch_id: <批次或 NOT_APPLICABLE>
- source_data_updated_at: <原始采集时间或 UNKNOWN>
- game_date: <玩家确认日期或 UNKNOWN>
- policy_id: <已确认玩法版本>
- code_ref: <本次实际使用的 commit>
- calculation_method: <工具与版本或 NOT_APPLICABLE>
- approval_state: ANALYSIS_ONLY | PROPOSED | PLAYER_CONFIRMED_WITH_EVIDENCE | NOT_APPLICABLE

## 本次完成（带证据链接）
## 本次发现（OBSERVED / CALCULATED / REFERENCE / PROPOSED 分类）
## 尚未解决的问题与数据缺口
## 下轮要做的最小下一步
## 交付文件及 GitHub commit / 未上传原因
```

聊天摘要不是事实来源，必须以引用的当前批次文件和计算结果为准；不能把 SYNTHETIC、REFERENCE 或 PROPOSED 逐次复制后变成 OBSERVED。GM 提案的批准，只能使用玩家对确切方案和版本的明确授权证据，不能依据任务记录字段声称。

## 完成单次任务/GM 决策节点的原子性与并发

1. 对新报告与 task summary 使用唯一 run_id，避免覆盖其他窗口结果。不要直接更改已有 session。
2. 仅在成功提交任务结果后，将其 commit/路径写入对应 CURRENT；如果任务没有产生新结果，也可仅记结构性进度。
3. 更新 CURRENT 之前先读取当前文件 SHA；若其他窗口已经先写入，重新合并，不用旧 SHA 强行覆盖。
4. GitHub 写入结果再回读，确认文档存在与来源引用正确；失败必须明确报告，无任何自动重试后台任务。
5. 只更新本岗位 CURRENT；跨岗位交付通过链接和人工触发，不能替其他岗位默默提升状态。
6. CURRENT 应保持简洁（约一页）；历史细节放 session 文档。**GM 节点完成后在本赛季聊天等待下一次玩家触发，不自动进入新节点或关闭聊天**；赛季结束归档后下一季新开聊天。文档结构/所有权变化由开发规划任务和玩家审查。
