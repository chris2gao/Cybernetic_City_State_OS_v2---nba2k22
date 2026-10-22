# ANALYTICS M02 V2 — GitHub 发布及回读交接

- role: WEB_GPT_ANALYTICS_V2
- date: 2026-10-18
- run_id: 20261018_M02_DEC12_V2_ANALYSIS_01
- career_id: mc_haliburton_2021
- game_date: 2021-12-12 (玩家确认)
- source_batch_id: 2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2
- previous_source_batch_id: 2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2
- status: PUBLISHED_ANALYSIS_ONLY_PARTIAL_DATA_GATES
- execution_authorized: false
- execution_mode: GitHub连接器读取批次后JS确定性计算；早前的本地Python编排/核对；未原样执行仓库脚本。
- GitHub写入情况：第一轮连接器触发安全拦截；玩家显式重新调用连接器后创建文件成功。账号chris2gao的仓库 push 权限已确认。本轮没有更改 published/、原始SQLite或游戏。

## 五个已发布的正式产物

- [简明报告](../../../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.md)
- [30队决策准备表](../../../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_TEAM_DECISION_TABLE.md)
- [跨批变化表](../../../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_CHANGE_TRACKING.md)
- [计算方法与来源](../../../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_METHOD_AND_SOURCES.md)
- [机器可读JSON](../../../../docs/gm_analysis/mc_haliburton_2021/20261018_M02_DEC12_V2_ANALYSIS_01_ANALYSIS_ONLY.json)

> 链接以main当前路径为准。本session不替代最新latest检查。

## GitHub回读审计

五份文件均由GitHub fetch_file重新读取成功。按主JSON与Markdown双向核验：30队=30行且 team_id 唯一；新比赛104场；30队增量战绩对齐；5项选秀权变更；11个名称级跨队名单候选；30队共870组对手防守同队29组内容一致；所有文件状态 ANALYSIS_ONLY，不包含玩家游戏写入授权。

主JSON是在GitHub写入恢复后，从已发布四份Markdown及原始GitHub联赛/赛季累计/资产/教练来源再次确定性构建（GM_ANALYTICS_M02_V2_GITHUB_RECONSTRUCTED_20261018），并**不是原本地JSON字节级复制**。数据契约中的数据缺口仍如实标为PARTIAL：无法认证人物永久跨批键、逐球员55字段前后完整导出尚未交付、poss语义未核实、对手攻防详细回合字段不完整。潜力变化的无差异结论仅限已核对的同队候选，不能推广为全联盟已认证。不要把177名候选视为确认自然成长，也不得将is_in_use_raw=0解释为防守未启用。

## 后续GM可直接读取

先读简明报告与30队表（证据与潜在非交易修正），需要改变阵容和教练时再查原始来源及玩家审批；跨批和技术方法作为独立证据。保持分析与决策执行隔离；未来根据更新批次重新计算，而不是使用此M02快照冒充最新数据。
