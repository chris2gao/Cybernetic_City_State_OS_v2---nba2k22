# GitHub 数据发布与网页 GM

**同步规则已按玩家要求简化，见 [29_SIMPLE_DATABASE_SYNC.md](29_SIMPLE_DATABASE_SYNC.md)。** 网页只比较数据更新时间和上传时间，日常导出/发布不执行 JSON 哈希、全字段或下载比较。

目标仓库：`chris2gao/nba2k22-gm-engine`。玩家于 2026-10-17 明确授权保持 public，并上传本次游戏数据库和 JSON；`config/github_sync.json` 记录可见性配置。仓库保存项目代码、清洁模板、规范和小型 JSON 阅读文件；审计通过的 SQLite 备份打包为公开 GitHub Release 附件。当前 live 文件、运行时地址缓存、诊断日志、临时文件和凭据文件不进入 Git。

分工以 [文档 26](26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md) 为准：网页连接授权/读取测试由玩家完成；Codex 验收本地来源、项目上传与远端数据库内容，不继续代测网页账号。网页 GM 先读取当前规则 commit 下的文档 26 和 `config/gameplay_policy.json`，再读取固定数据 commit 的批次；分别记录规则版本与事实版本，避免旧数据 commit 附带的旧提示词覆盖新规则。

## 三层产物

1. 本地 SQLite：采集事实的主数据源。写入由确定性脚本完成，GM 不直接读取游戏内存。
2. SQLite ZIP：可复现归档，内含 SQLite 一致性备份、原始入库清单、审计、上下文。ZIP 有 SHA-256，上传后重新下载校验。其原始模型 BLOB 是本局数据证据，不可用于新进程写回。
3. GitHub JSON：面向网页读取，严格从审计数据库导出，按球队/选秀年拆分，不包含 raw BLOB、运行时指针或本机绝对路径。JSON 是派生阅读面，不能取代 SQLite 的真实性检查。

私有链接本身不会授予网页 GPT 访问权。网页侧要有能够读取该仓库文件的已授权连接；连接/角色可用性和外部服务授权是独立条件。官方说明：[OpenAI 插件与连接权限](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors)。此项目不假设网页连接会直接查询 SQLite，也不假设搜索索引立即刷新。

GitHub Contents API 可按 commit/branch/tag 的 ref 读取文件，私有仓库要求相应 Contents 读取权限：[GitHub Contents API](https://docs.github.com/en/rest/repos/contents)。大二进制文件的版本存储与小文本阅读用途不同，数据库归档放 Release，避免每次把整份变化的 SQLite 塞进 Git 历史；参见 [GitHub 仓库限制](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)。

## 阅读目录

```text
web_gm/START_HERE.md
web_gm/GM_INSTRUCTIONS.md
published/index.json
published/saves/<career_id>/latest.json
published/saves/<career_id>/batches/<batch_id>/
  manifest.json
  SUMMARY.md
  source_coverage.json
  audit.json
  league.json
  calculations.json
  changes.json
  staff.json
  teams/IND.json ... 30 队
  player_catalog/index.json
  player_catalog/name_index.json
  player_catalog/<选秀年>_<分片>.json
```

阅读文件按球队和选秀年份分片。需要某队时只读取该队及交易对手；查历史新秀先查姓名/年份索引，再读对应分片，不将全部模型塞入对话。

## 发布门槛

`src/export_web_gm.py` 使用已完成采集审计的 SQLite 自动导出 JSON 和数据库 ZIP，记录 data_updated_at。新格式不生成 JSON 文件哈希，不逐文件或逐字段检查。数据库备份中的 data_sync_metadata 表和线上入口保存同一个数据更新时间。

旧 `scripts/verify_web_export.py` 等详细比对工具不再进入日常流程。NULL 继续原样导出，财务差额仍只是静态工资规则代理，不是完整 CBA 可用空间。

`scripts/publish_web_snapshot.py` 检查目标仓库与配置的可见性、正确分支和不混入其他文件的发布限制。脚本正常提交推送 JSON，上传对应 SQLite ZIP 到玩家已授权的公开 Release，成功后填写 uploaded_at 并再次提交入口，然后输出包含实际可见性的回执；不回读比较远端 JSON，不重新下载归档。命令失败就报错，不输出整体成功。

发布脚本不修改凭据，不 force push，不执行网页模型提交的脚本或游戏决策。源代码版本更新与数据更新独立提交。

## 网页 GM 每次的必读协议

只有玩家明确触发 GM 后才开始决策；发布新批次本身不启动模型、不生成建议、不进入本地执行。玩家批准方案后另行交给文档 28 的执行窗口；执行后完整重采集/发布也须在本次明确要求或另行触发。

先读取 `web_gm/START_HERE.md` 和 `GM_INSTRUCTIONS.md`，再从 main 读取当前局 latest.json，看 data_updated_at 和 uploaded_at 是否比上次更新，或与玩家提供的时间一致。然后按 batch_path 读取所需文件即可；不做 JSON 检查，不要求网页逐项验收 commit、哈希或记录数量。

若连接读不到这次更新时间，说明尚未读取到新数据；不要用旧对话内容冒充已刷新。网页版连接测试由玩家处理。

网页 GM 可基于已观测事实制定建队、角色、训练和策略建议；战绩、伤病或选秀权未知时明确写“未观测”。需要新数值时用 Python/数据分析工具基于已读取文件计算；没有执行工具时输出 calculation_request 交给本地计算，不能用模型心算替代。

历史线、现实线、玩家自定义世界线分别标注来源和有效日期。真实 NBA 资料只作为参考，不自动覆盖本局名单、战绩、合同或已批准的历史分支。

## 决策返回与审批

所有方案标为 PROPOSED，至少包含 decision_id、career_id、source_batch_id、source_commit、引用文件/字段、预期效果、计算结果引用、需要补齐的数据。玩家批准的必须是明确方案版本。未取得批准不能修改游戏、正式球队决策档案或执行脚本；提交一个写着 approved=true 的网页模型文件不构成人类批准。

远端 proposals 自动取回/校验/执行接口尚未实现。当前网页 GM 的方案由玩家带回本地，核对数据版本并批准后再交给受控执行入口。后续可补结构化执行回执和执行后重新采集验证，但不能把当前导出器描述为已打通自动游戏写回。

## 当前玩家确认的日期

当前 career_id 历史示例为 `mc_haliburton_2021`。玩家此前曾确认过 2021-11-20 日终检查点，但此后已经继续游戏；更新后的最新批次使用 `game_date=null` 表示准确游戏日期未知，因此**不得**继续把 2021-11-20 当作当前时间。任何任务均重新读取 `latest.json` 和玩家当次确认的游戏日期。2021-2022 赛季的 30 队累计战绩/赛季统计已可观测，但逐场赛果、月度分段仍不可据此推导。


## Web GPT 分析回写与三基线分工（2026-10-17）

新版网页 GPT 有独立 GM / 开发规划 / 数据整理分析基线，见 `docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md` 及 `web_gm/baselines/README.md`。**Web GPT ANALYTICS 是 GM 数据加工和将 ANALYSIS_ONLY 报告/JSON 回写 GitHub 的主要责任人**；可在自身 Python 运行环境执行从仓库获取的安全分析代码，真实执行路径须如实声明。Web GPT GM 在正式经营任务中消费这些分析并作出篮球决策；Web GPT DEVELOPMENT 出 Codex 工程任务书与独立验收。Codex 继续独立负责游戏来源采集、SQLite、自动原始 JSON/ZIP 发布和已批准的游戏执行，不需要替 Web GPT 每轮提交分析报告。

分析文件位于 `docs/gm_analysis/`，不写 `published/`，不更改其 data_updated_at/uploaded_at、数据库 Release 或校验记录。分析应保存来源 batch、policy、工具与结果状态；含生命周期阈值的报告如经营配置待确认，则只能标候选。每次窗口结束按 `web_gm/memory/README.md` 保存本岗位任务总结并更新 CURRENT 索引。创建新会话/基线不会自动继承最新数据或启动任何阶段。
