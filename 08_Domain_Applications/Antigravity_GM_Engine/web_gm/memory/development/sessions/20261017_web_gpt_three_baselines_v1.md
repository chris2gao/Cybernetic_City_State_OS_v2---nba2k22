# 2026-10-17：Web GPT 三基线与跨窗口持久记忆机制建立

- role: WEB_GPT_DEVELOPMENT
- run_id: 20261017_web_gpt_three_baselines_v1
- status: COMPLETED
- career_id: NOT_APPLICABLE（项目级组织任务）
- source_batch_id: NOT_APPLICABLE；历史数据参考 `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`
- game_date: UNKNOWN
- policy_id: PLAYER_RULES_20261017_V3
- approval_state: NOT_APPLICABLE（本次只修改项目协作文档）
- game_memory_modified: false
- formal_gm_round_started: false

## 本次完成

1. 建立 `docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`：项目三类 Web GPT 角色、Codex/玩家分工、GitHub ↔ Python → 分析回写、跨窗口状态及批准边界。
2. 创建 `web_gm/baselines/README.md` 和 3 份完整可复用提示词：`GM_BASELINE.md`、`DEVELOPMENT_BASELINE.md`、`ANALYTICS_BASELINE.md`。建立基线和新派生任务必须由玩家触发。
3. 创建 `web_gm/memory/README.md`，并初始化 `GM_CURRENT.md`、`DEVELOPMENT_CURRENT.md`、`ANALYTICS_CURRENT.md`；规定按每个任务新建 session 记录、收尾更新 CURRENT。
4. 同步 `AGENTS.md`、`README.md`、`web_gm/START_HERE.md`、`web_gm/GM_INSTRUCTIONS.md`、`web_gm/GM_DECISION_SOP.md`、`docs/25_GITHUB_AND_WEB_GM_PROTOCOL.md`、`docs/34_BASELINE_CURRENT_STATE.md` 的角色与上下文入口。
5. 对历史说明的过时游戏日期/已支持数据范围作局部澄清。**没有修改任何** `published/`、数据库、Release、游戏内存、已确认球队档案、Codex 原有采集/开发提示词或执行脚本。

## 三类责任人

- Web GPT GM：赛季/球队经营与待批准 GM 决策；
- Web GPT DEVELOPMENT：需求文档、Codex 任务书、独立代码审查；
- Web GPT ANALYTICS：网页数据读取、Python/SQL GM 量化加工、`docs/gm_analysis/` 数据与报告 GitHub 回写；
- Codex：Windows 数据源、只读采集/SQLite/事实发布、工程代码实现及单独批准的游戏执行。

## 证据/入口

- [三基线索引](../../../baselines/README.md)
- [协作协议](../../../../docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md)
- [GM 最新记忆](../../GM_CURRENT.md)
- [开发最新记忆](../../DEVELOPMENT_CURRENT.md)
- [分析最新记忆](../../ANALYTICS_CURRENT.md)
- [此前分析报告](../../../../docs/gm_analysis/2021-2022_SIMPLE_PICKS_V1_ANALYSIS_ONLY.md)

## 未解决/下一轮需求

- 三类基线提示词已在 GitHub 可读，**并没有替玩家实际创建三个产品聊天窗口**；需玩家使用文档中的初始化提示词自行开设。
- 后续分析任务如需严格运行仓库原版 `gm_prepare.py`，先确认新窗口是否有真实的 clone/文件导入执行能力；否则如实注明计算采用 SOURCE_COMPATIBLE_PYTHON_EXECUTED 的路径，不虚报原始脚本执行。
- 新任务发生时应逐岗位记录并更新记忆索引，避免本任务后的规则版本长期写死在基线。
