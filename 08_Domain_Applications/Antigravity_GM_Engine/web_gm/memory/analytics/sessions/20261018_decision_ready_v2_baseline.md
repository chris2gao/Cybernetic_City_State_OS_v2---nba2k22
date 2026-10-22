# ANALYTICS 基线 V2：GM 决策准备方法升级（2026-10-18）

- role: WEB_GPT_ANALYTICS
- run_id: 20261018_decision_ready_v2_baseline
- status: COMPLETED_DOCS_ONLY
- career_id: mc_haliburton_2021（仅检查最新索引，不运行新分析）
- source_batch_id: 2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2
- previous_source_batch_id: 2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2
- source_data_updated_at: 2026-10-18T12:12:13.170996+00:00
- game_date: 2021-12-12（由玩家确认）
- policy_id: PLAYER_RULES_20261017_V3
- calculation_method: NOT_EXECUTED（文档规划/在线源结构核对，不是新分析结果）
- approval_state: NOT_APPLICABLE；游戏执行未授权
- baseline_version: WEB_GPT_ANALYTICS_V2
- method_version: ANALYTICS_DECISION_READY_V2

## 输入与核对

用户转达了GM决策窗口对分析的四项优先要求：①30队逐队决策诊断；②M01→M02逐球员55项/潜力/名单/合同/签权差分；③教练体系与870组对手防守按需摘要；④由season_totals现有原始计数构建可靠效率指标，poss源语义必须先确认。另要求每批交付简明报告、30队决策准备表、跨批变化表、方法及来源引用。

读取了本岗位基线/当前记忆、`src/gm_core/calculations.py`、`src/gm_core/data_reader.py`、`published/index.json`、本存档latest、M01和M02的`season_totals.json`及`teams/IND.json`样例、M02`coaching/teams.json`、`coaching/field_dictionary.json`、`coaching/opponents/IND.json`、`source_coverage.json`、选秀权源、GM教练手册等。

## 实际修改

1. 新建 `docs/gm_analysis/ANALYTICS_DECISION_READY_V2_METHOD.md`：四主任务、停止默认排行榜的理由、逐队字段、身份匹配三层门槛、差分、教练/对手适配、公式、poss验证、四MD＋主JSON交付格式及验收。
2. 更新 `web_gm/baselines/ANALYTICS_BASELINE.md`：切换为`WEB_GPT_ANALYTICS_V2`、将四主任务设为默认、指向完整方法文件、定义新交付清单。
3. 更新 `web_gm/baselines/README.md`：提供V2入口说明（与基线一致）。
4. 更新 `web_gm/memory/ANALYTICS_CURRENT.md`：下一任务入口、当前事实批次和V2阻塞项。

## 方法关键决策及理由

- **减负**：默认废止长篇联盟排行榜，但不删除用于筛选/校验的数值计算。GM更需要球队人才不足与未用好现有球员的证据区别。
- **自然成长**：旧`roster_changes`基于姓名+Face ID，源码承认不构成永久身份；跨批先认证身份，不可认证者单列区间候选，不能累计为确定的55项增长。
- **教练**：M02同批30队19项与29组/队对手记录、来源字典已存在，可供分析；五项Sim禁写、Tempo UNKNOWN、`is_in_use_raw=0`不表示无防守。旧M01没有教练来源，不回填。
- **效率**：FGA/FGM/3PM/FTA/TOV等支持eFG、3PA率、估算失误率；`poss`虽存在但原生攻守回合语义未完全证实，不把`points/poss*100`冒称标准ORtg。
- **新输出**：简明报告、30队决策表、跨批变化表、来源与方法文件、同数字的结构化主JSON，按run_id不覆盖历史。

## 实际执行与审计边界

仅进行了仓库源代码与来源结构读取和GitHub文档写入。**没有实际运行新的M01→M02计算、没有计算/发布任何新球员成长结果、没有运行Python分析脚本、没有游戏进程/内存操作、没有GM决策与游戏执行**。代码执行模式：NOT_EXECUTED。

## 下次玩家触发后的最小步骤

1. 重新读取GitHub`main`的本岗位基线、CURRENT、V2方法、最新latest和必要两批来源；锁定具体career/season/区间。
2. 在安全的Python/SQL环境进行30队诊断、区间战绩/资产差分、教练19项/按需18项、防守进攻风格指标；真实身份不明者保持暂定/UNKNOWN，poss按准入标签输出。
3. 若需持久球员ID或poss定义，登记`DATA_SOURCE_REQUEST`，其余模块继续交付。
4. 仅经玩家触发/授权发布四MD＋主JSON；回读校验、记session和更新本岗位CURRENT；交给GM链接，不唤醒GM。

## 文档提交证据

- [方法规范提交](https://github.com/chris2gao/nba2k22-gm-engine/commit/c45bf7c63d0a5fff110658426eb69ca56cceb3ca)
- [分析基线V2提交](https://github.com/chris2gao/nba2k22-gm-engine/commit/94ce9c5f01094be6ca1cab9adf01e0f6e59ed00a)
- 本session与索引的具体提交SHA以写入工具返回及任务回复为准，不先虚构。
