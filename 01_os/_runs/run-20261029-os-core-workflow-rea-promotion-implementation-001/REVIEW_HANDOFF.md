# Workflow 与 REA 统一升级审核交接

任务 `OS-CORE-WORKFLOW-REA-PROMOTION-20261029-001`。工程交付范围覆盖 S1–S5。

| 阶段 | 可审核交付 |
|---|---|
| S1 | Stage01 的唯一活动规范、Schema、Boot 和七阶段 runner 同步更新。A0 与 A 的确认各自绑定 ID、版本、内容摘要及不同确认引用。验证器检查结果项和成功判据、证据问题的双向覆盖。 |
| S2 | 项目入口和模块注册表按任务选择。项目工具复用 PRMS 固定 Git 来源，检查来源状态、索引同候选同步和交接。Stage02 证据按成熟度、来源及用途分层。 |
| S3 | Core 注册按需 REA 静态适配器。当前版本、Schema、后端能力、失败结果及原始证据摘要来自现场调用。 |
| S4 | NBA Profile 固定构建和研究来源，连接 Core 静态工具及现有领域业务入口。P03/P09 随同项目索引与注册表交付。 |
| S5 | 固定候选 managed verification、G1/G2 发现、真实 REA 静态调用、跨仓回执和独立审核输入。 |

Core 工程起点为 `d463b83c74c17d74cacf64c4d82e4abce5004b75`，该基线已包含 Core #13 的开发 Loop。统一任务恢复时保留此前 S1 与 S2 的提交，纳入该上游基线并重新执行测试。Core managed verification 固定在 `31b5c2edcbad3c4840e2ff2c6621ad20a030b72a`，NBA managed verification 固定在 `228abf11fc15d34a0a3d71813581adc6797ef58d`。跨仓回执的 Core 固定源是 `f083ae685764e88e6f522cc91f2c58b7a33ee99f`，与 Core managed verification 版本间仅有本 Run 的任务包验证项、验证计划及测试脚本差异。首次超时及两次 Windows 共享临时路径清理失败的回执随报告保留。

正式规划固定在 NBA `15d664405330cd38e04fee5980a89ada36376d14`。Core #9 `b2f81214a883db9b8f40ba6ede0852669455c4d1` 已提供双层 Stage01 规范草案，旧 runner 尚未覆盖双确认。NBA #18 `094f1aa641f93dec2277707ad9dbf5bdb0341247` 提供导航和逐例研究。NBA #26 `aee5a9109ea5cd0a5c7bc4adb750c64a1603afec` 已提供领域业务执行源码，因此本次 S4 使用固定入口和证据映射，保留该候选自己的集成边界。

## 复验

1. 在两个干净工作区检出上表测试源。Core 运行当前 Run 的 `verification_plan.json`。NBA 运行领域 Run `run-20261029-nba-rea-core-adapter-001/verification_plan.json`。使用已登记的 `managed_verify.py run` 与 `inspect`，给每次尝试独立的外部证据目录。
2. 在 Core 使用 PRMS `cli.py catalog` 固定测试源，检查 REA 属于可选工具。对 NBA 固定测试源运行 `cli.py domain`，检查项目候选与正式 G2 状态各自表达。
3. 运行 NBA 领域 Run 的 `verify_joint.py`，选用已知非游戏样本并传入跨仓回执中的两个固定源。该脚本验证域构建不符时拒绝，以及真实静态工具回执的内容绑定。
4. 阅读 `verification/managed_report.json` 的实际命令、退出码及日志 SHA256。原始测试 stdout/stderr 与 JSON 同目录保存。REA 收据和跨仓结果记录工具、源文件及原始结果摘要。操作指引见 `01_os/04_skills_and_tools/rea/README.md`。

## 证据范围

Stage01 检查的是结构、版本和摘要绑定，真实 Human 记录及语义充分性由独立审核核对。当前运行验证覆盖 Windows 上已安装的 REA 6.8.0 和两项静态操作。探测环境中 Ghidra、Hopper、IDA 和 Kuna 报告不可用。NBA 原生操作、UI 与存档持久性在本任务均为 `NOT_RUN`。正式 G2 仍为 `DOMAIN_CATALOG_UNINITIALIZED`。

本 Run 状态为 `candidate_ready_for_independent_review`。独立审核应在另一个隔离会话进行，使用固定提交、原始测试和任务输入。审核和发布决定由 Human 单独记录。
