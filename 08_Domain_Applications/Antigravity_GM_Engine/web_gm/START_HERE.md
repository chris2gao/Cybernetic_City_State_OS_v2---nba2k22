# 网页 GPT：从这里开始（角色与数据入口）

> [**网页版所有模型的项目意图**](../docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：先理解采集→分析→Coach→Player→GM→执行六阶段和三层职责：DEV29调查玩法/数据/设置，DEV28提供I/O，未来人格另立项，Coach/Player独立人格尚未上线。

本页专供 ChatGPT 网页版阅读。项目 GitHub：`chris2gao/nba2k22-gm-engine`；仓库目前按玩家授权公开，连接器权限与可读性仍须在任务中实际确认。不要沿用旧版说明中的「仓库必定为私有」或「当前游戏日一定是 2021-11-20」；游戏日期始终取当前 `latest.json` 及玩家明确说明。

## 第一步：根据任务选择专用基线

- **经营/交易/教练/战术/联盟 GM 决策**：`web_gm/baselines/GM_BASELINE.md`
- **技术架构、Codex 开发任务书、代码审查与验收**：`web_gm/baselines/DEVELOPMENT_BASELINE.md`
- **GitHub 数据、本地 Python/SQL 分析、报告/结构化结果同步**：`web_gm/baselines/ANALYTICS_BASELINE.md`

三种基线都在 [web_gm/baselines/README.md](baselines/README.md) 提供可复制初始化提示词。跨窗口记忆索引在 `web_gm/memory/*_CURRENT.md`；完整协作与保存规则见 [文档 35](../docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md)。

**初始化只读取上下文，不触发本岗位实际任务。** 从基线另开窗口后，由玩家明确要求执行本轮。基线之间不自动联系。

## 第二步：只读最新游戏事实

1. 先看 `AGENTS.md`、`config/gameplay_policy.json`、文档 22/26，记下玩法版本。
2. 读 `published/index.json` 选择玩家指定的 `career_id`；再读 `published/saves/<career_id>/latest.json`，看 `data_updated_at`、`uploaded_at`、`upload_status`、`game_date` 和 `batch_path`。
3. 当前批次在 `published/saves/<career_id>/batches/<batch_id>/`。按本轮需求读取 `source_coverage.json`、`league.json`、`calculations.json`、`draft_assets.json`、`season_totals.json`、`staff.json` 和具体 `teams/<abbr>.json`。不要一次读入所有球员模型。
4. 日常数据同步只看时间戳，不恢复 JSON 哈希、逐字段远端验收或 ZIP 回下载；内存来源审计由 Codex 负责。大 SQLite 的原始备份在对应 GitHub Release，不意味着 Web GPT 已经下载或直接查询它。

## 第三步：根据本岗位独立交付

- **ANALYTICS**：实际执行 Python/SQL（或注明没能运行），写 `docs/gm_analysis/` 的 `ANALYSIS_ONLY` Markdown/JSON，更新本岗位记忆。不要写游戏事实或正式 GM 决策。
- **GM**：读取**相同批次**分析及必要球队文件，作出独立经营判断；获得玩家明确 GM 触发后才能进入正式决策，所有执行相关方案仍为 `PROPOSED` 待玩家批准。
- **DEVELOPMENT**：按需读取源代码与约束，给出 Codex 任务书、验收结果与工程文档。工程代码实现由 Codex 管理，数据更新由 Codex 数据窗口负责。

无论哪个岗位，任务结束后写本岗位 `web_gm/memory/<role>/sessions/<run_id>.md`（如果已授权保存）并更新 `*_CURRENT.md`；给出实际 GitHub 提交和路径，停止，不自动启动下个阶段。

Web GPT 基线不替代 Codex 的文档 32/33/34。所有游戏执行另走文档 28 的玩家明确批准路径。
