# GM 决策机制纠偏：外挂管理、胜率优先

- role: WEB_GPT_GM
- session_id: GM-20261017-V2-MECHANISM-CORRECTION
- status: COMPLETED_DOCUMENTATION_ONLY
- source: PLAYER_EXPLICIT_CORRECTION_2026-10-17
- last_source_batch: 2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2
- career_id: mc_haliburton_2021
- approved_game_write: false
- executed_game_write: false
- new_gm_operating_mechanism: `WEB_GM_DECISION_MECHANISM_V2`
- latest_bilateral_trade_execution_approval: NONE

## 玩家已确认的系统边界

1. 我曾误以为NBA2K22原生交易引擎的难度/谈判/配平是外挂GM成交的裁判；该理解已纠正。双边外挂GM各自独立判断，双方接受同一份交易后直接交玩家批准，Codex实现。不要求游戏CPU再同意。
2. 士气/化学反应影响相对有限；以能赢球、长期争冠为主目标。允许证据支持的轮换和角色变化，即使有次级士气风险。
3. 数据驱动：上场时间调整要有球员/球队实测依据、实际计划分钟与后续结果核验；若有真实交易申请，外部GM可以将球员列入货架候选。
4. 每月、季后赛每轮由玩家启动GM节点；每个节点最多三回合，默认一回合提出决定。30队内部谈判不计入用户来回对话。

## 交付与后续

- [GM v2机制](../../../GM_DECISION_MECHANISM_V2.md)
- [GM v2 SOP](../../../GM_DECISION_SOP.md)
- [GM基线](../../../baselines/GM_BASELINE.md)已加入 v2 阅读入口
- [技术开发需求交接](../../../decisions/mc_haliburton_2021/20261017_GM_V2_DEVELOPMENT_HANDOFF.md)
- 具体金额算法、轮换调整幅度、士气效果和执行接口属于待证事实或可选技术建议，并非用户确认的硬阈值。
- 未更改 `published/`、真实球队名单、选秀权/能力、政策配置或Codex代码。
- 先前 MKT-01/MKT-02 仍只是玩家已批准的**非约束询价**，v2不会自动将其升级为交易双方已达协议。
- 下一次GM任务必须按新机制直接充分内部谈判并交付最终可审批方案；若交易/轮换执行器缺失则按原审批界限等待开发侧。
