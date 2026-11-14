# Issue #40：实机研究失败审阅材料

Human 已停止本轮研究，并要求把失败材料直接发布到任务 GitHub，供其选定的 GPT 查看。本次仅发布历史审阅材料，不恢复研究、不操作游戏、不宣称研究完成或独立验收。

**本轮约一小时：16 次单步字段资格修改通过读回；正式 H/L 处理 0、日历调用 0、模拟完成比赛 0、完整实验闭环 0。**

## 建议阅读顺序

1. [失败审阅报告](FAILURE_REVIEW_FOR_GPT.md)：操作时间线、失败修复、实际改值、目标偏移与原因自查、证据限制。
2. [证据索引](FAILURE_EVIDENCE_INDEX.json)：227 个原始文本证据的源路径、发布路径、SHA-256 与时间，另含 6 组资格结果。
3. [最终实机结果](evidence/qualification-live-final/RESULT.json)和[执行 stdout](evidence/qualifications.stdout.log)：确认 16 项资格完成及 0 次日历调用。
4. 两次派发前失败：[第一次 RESULT](evidence/qualification-live-fast/RESULT.json)、[第二次 RESULT](evidence/qualification-live-repaired/RESULT.json)。完整 Host ledger、封套及相关 JSON 均在对应目录。
5. [新鲜采集回执](evidence/fresh-capture-receipt.json)、[REA 日期证据](evidence/rea_native_today_evidence.json)、[原始 16 槽值](evidence/fresh-16-slot-values.json)。
6. [冻结计划](FIRST_BATCH_FROZEN_PLAN.json)、[现场计划差异](PLAN_DELTA.md)、[历史运行方案](REAL_LIVE_RESEARCH_RUNBOOK.md)、[本轮源码差异快照](FAILURE_SOURCE_DIFF.patch)。
7. [原始运行脚本](evidence/run_qualifications.py)与[计划生成脚本](evidence/build_first_batch.py)，便于核查重复采集、批次结构与执行路径。

[全部公开文本证据目录](evidence/)保持原始文件内容；源 `_runtime/xxx` 映射为 `evidence/xxx`。索引的 `path` 保留原源路径，`published_path` 是仓库中真实可访问路径。没有上传 ZIP、数据库、存档或可执行二进制。

## 当前状态与解释边界

资格结束时 0005/0003 的磁盘指纹未变化，内存保留 16 项资格改值。随后 Human 要求停止研究，未确认重载，未恢复测试。本报告不要求读者立即执行其中任何历史运行步骤。

报告中的“尚未提交/发布”“本地原始证据”等文字描述审计形成时的历史状态。本次将报告及证据作为文档发布到 PR #43 的任务分支；源码修改本身没有作为可执行更新提交，仅以 patch 供审阅。此前生成的本地 ZIP 与本地档案回执不属于本次发布产物。

这套材料是执行者自查与历史证据，不是完整聊天逐字导出，不证明整个项目必然失败，也不证明实机批量研究已可用。失败审阅报告明确说明已知缺口，不将资格成功替代比赛实验成功。

## 发布与范围

发布传输为 local Git；使用已配置的 `.githooks`，普通非强制任务分支 push，不合并 master。文档发布的完整性检查验证每个源文件与发布文件的哈希，并验证最终结果和 16 份 APPLIED 资格回执。该检查仅证明材料复制完整，不能补足本轮缺失的比赛实验。

`exclusion_or_deferral`: Human 已停止研究；本轮实机研究未达到预期，延后后续实验，仅归档并发布失败材料。公开审阅入口为本 README；Issue #40 的发布评论提供固定提交链接。
