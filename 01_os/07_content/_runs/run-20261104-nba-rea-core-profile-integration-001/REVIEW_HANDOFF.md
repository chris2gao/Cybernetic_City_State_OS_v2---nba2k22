# NBA2K22 REA Core Profile 主线接入审核

任务 `OS-NBA2K22-REA-CORE-PROFILE-INTEGRATION-20261104-001`。沿用 NBA [PR #27](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/27)。测试固定在 NBA `be89b5fa5585942881e21ab2f70b19542b3fa005` 和 Core `08d8e534a3438269aa7d7eb1b080ab11c172f462`。测试后提交只增加本 Run 的交接和回执。

NBA master 基线 `dfa08af8bb6e4abf1cd8ad304f47b096ecc38167` 已含 #26、#28。原 #27 `400c998be89ab2c8b902e50667af500f0fda178e` 是候选祖先，原 Profile、bridge、测试和原 S4/S5 Run 原样保留。导航修正涉及项目总索引、P00–P12 注册表及 Profile README。GitHub API 初次返回旧 base，Git 传输和实际合并提交均确认任务指定基线。

| 证据级别 | 结论 |
|---|---|
| `STATIC_VERIFIED` | 6 项 Profile 测试通过。13 个模块和 61 个当前树入口通过检查。Core master 的 adapter 与 `a668307405df1f932008ba27be073654878bb577` 固定版本字节相同。真实 REA 6.8.0 对非游戏样本返回验证回执，原 Profile 拒绝构建不匹配的样本。 |
| `HISTORICAL_LIVE_EVIDENCE` | #18 固定输入 `094f1aa641f93dec2277707ad9dbf5bdb0341247` 的 62 个动作、38 个绑定、12 个 Reader。交易、教练和球探三例仍绑定原历史验证；本次读取目录及逐例标记。 |
| `NOT_RUN` | 当前游戏附加、Native 写入、交易、存档和游戏效果。 |

#26 的 facade、Bulk、Outbox 固定对象与 master 同字节。#28 目录树与 master 相同，归档解析仅服务历史 WorldData，本 Profile 使用独立的 #18 研究路径。238 个已归档数据 blob 均未随本 PR 引入，原 Host 也未进入候选祖先链。

复验在干净工作区固定上述测试 SHA。运行 Profile 的 `test_bridge.py`、本 Run 的 `verify_integration.py`，以及原 S4 Run 的 `verify_joint.py`，传入两个固定测试 SHA 和非游戏样本。本次样本为 GitHub CLI 的 `gh.exe`。同目录保存测试退出码、跨仓回执、REA 版本回执、逐对象 SHA256 和 OS Loop 检查点。独立审核及 Human 合并决定分别待定。
