# 开发规划专项交接：历史重力球员定制与常规GM经营隔离

- `handoff_id: DEV_HISTORY_GRAVITY_SEPARATION_20261018_V1`
- `status: SPEC_ONLY_AWAITING_DEVELOPMENT_REVIEW_AND_PLAYER_APPROVAL`
- `owner_for_design: WEB_GPT_DEVELOPMENT_PLANNING`
- `gm_owner: WEB_GPT_GM` — **只负责30队正常比赛、建队、人员流动、教练和独立GM交易谈判**
- `game_edit_authorized: false` / `direct_player_attribute_edit_authorized: false`

## 玩家2026-10-18新分工

玩家希望GM阶段避免“历史线属性调整”挤占真正30队经营的分析与谈判。**如需模拟历史发展而定制当前联盟已有球员，单独由开发规划模型规划并交玩家审批；GM不处理这类能力/属性定制。**

常规GM围绕**实际数据**持续推演各球队的短期获胜与长期争冠逻辑，可以在真实历史人物或王朝背景下自发通过交易、签约与教练风格形成类似时代走势。历史线是`REFERENCE`，不是复刻现实结果的硬胜负脚本；不要求强制历史冠军、原历史球队名单、不允许历史线直接影响30队正常`source_batch_id`事实。

### 任务切割

| 动作 | 负责人 | 边界 |
| --- | --- | --- |
| 当前30队球员分析、阵容互补、攻防设置与赢球哲学 | GM基线 | 当前M02及后续正式来源，逐队6维度深度研究，不能改普通能力 |
| 历史线风格交易、历史资产价值比较与双边协议 | GM基线 | 两队独立利益同意，玩家批准交易后Codex受控执行 |
| 历史人物年代线的参考资料、年代推演与历史重力数值设计 | **开发规划基线** | 分离工作流，独立版本、与GM交易方案无执行绑定 |
| 游戏内人物能力/潜力/倾向特例变更 | **Codex执行基线在完整原生执行器验收和玩家逐项审批后** | 只有历史线例外允许讨论，普通成长仍禁止干预 |
| 员工机制/任免对引擎的实际效果与岗位写入 | 开发规划基线负责技术机制与验收，GM只提业务需要 | 当前员工关联可读但岗位双向变更未验证，不能交未经验证的人员换帅动作 |
| 训练及球员精确分钟 | NBA2K22原生AI | **不加入外挂开发待办** |

### 历史线参考坐标

- 游戏起点2021–22；现实现代线与历史参照的切换点仍以已批准规范文档26为准：**到游戏2026年**，切换为参考1984年乔丹选秀四年后的历史时代；此后跟随玩家确认的1984→2020历史选秀轮回推进。
- 游戏日历年、球员建模年份与当前导入历史选秀届次不可混淆；未来三届选秀权仍采用游戏日历年份而不是历史标签。
- 不能因为球员和现实历史同名就把复制模型静默合并；需处理`player_identity`和历史人物克隆/在役重复，尤其玩家MC与历史克隆冲突。
- GM为了争冠可以做出和现实不同的决定；开发历史重力仅在玩家另行批准的**独立专项**中产生有限人物特征调整，不使历史惯性凌驾实际游戏结果。

### 若开发模型将来确需提出历史重力专项，必须交付的最小合同

- `historical_project_id`、`source_career_id`、`source_batch_id`、`game_date`、`game_season`；
- `reference_epoch`、`historical_sources`（真实历史参考并与本局观测分开）；
- 明确目标球队、**经认证的球员身份**、原生`before_values`、`proposed_values`、字段效果/理由；
- 对每个字段有**最小必要**调整与具体`calculation_script_ref`、`impact_constraints`、长期干预副作用；
- 原生执行接口的只读/写入验证状态、`rollback_plan`、`post_exec_readback`、`expiry_or_permanent`；
- `approval_state=NOT_APPROVED`直到玩家逐项明确批准；GM日常交易批准无法放行历史能力调整；
- `published`的原始数据不得根据历史剧情回填伪观测，只能在实际游戏改变后由玩家触发的全量采集按真实状态发布。

### 当前阻断，不推定已有

文档26载明**历史重力受控人物属性执行器尚未实现**；`growth_engine.py`旧自动成长入口和`modifier.py`任意属性编辑停用。**本交接只是规范与开发规划责任登记，不是用户授权现在开始设计具体球员加成，也不是命令Codex改游戏。** 若将来玩家触发专项，再由开发规划基线按此文和文档26执行规划。

### GM接入合同

- GM只记录`historical_style_context`（真实NBA参考）、`worldline_trade_preference`（可选，不能当事实/强制成交）、`development_handoff_needed`（只有用户要求属性专项时）。普通球员`player_assessments`永远反映当前真实存档而非历史改动假定结果。
- 历史开发方案不得直接在GM节点D1–D5中混入可审批的教练或交易动作；历史能力专项与交易/教练分开审批、分开执行回执和来源更新。

关联：[GM数据到决策规范](../../web_gm/manuals/GM_DATA_TO_DECISION_STANDARD_V1.md) · [历史与角色权威规则](../26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md) · [开发规划当前记忆](../../web_gm/memory/DEVELOPMENT_CURRENT.md)。
