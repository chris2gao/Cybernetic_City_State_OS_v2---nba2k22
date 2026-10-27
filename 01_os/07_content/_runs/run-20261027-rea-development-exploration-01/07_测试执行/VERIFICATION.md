# 阶段材料离线验证

被验证的研究候选：`131abe3969e3cba87413a9f934b52bbd86cb8a19`。

使用当前OS `managed_verify.py run` 及同候选 `inspect`，两者退出码均为0；固定计划SHA256为 `15b7e09f465d39b82385c0bb65e4f3633cb83a186f2d4e2ffded229a4038b7c7`。

| 检查 | 范围 | 结果 |
| --- | --- | --- |
| artifact-integrity-and-scope | 52份Evidence/分析文件本地字节与Git blob的SHA256、唯一安全路径、实际变更allowlist、未包含资产二进制、Python语法及手册本地链接 | PASS |
| evidence-and-document-contract | 3次元数据观察的构建/脚本/清理及错误检查、27次类型观察与代码片段匹配、4096条fixture独立回读和恢复、16次fixture调用事件、资源副本精确变化、UI更正与UNKNOWN边界 | PASS |
| MWU artifact | stage_snapshot_mwu.json的结构性要求 | PASS；不证明叙述真实性或独立验收 |

`result.json`及两份stdout是候选131abe39实际运行记录的原字节副本。原始attempt保存在本机 `rea-onboarding/development-exploration-20261027/publication-verification-01`；不发布包含本机解释器细节的input文件。该提交附加的只是验证记录和本文；最终发布head的精确检查会在推送前另做并向Human报告，不以父提交验证冒充未验证的head。

本次验证不重跑游戏或fixture，不证明新游戏效果；它核对已经保存的实验记录与阶段文档。完整研究仍按Human决定暂停，无master合并及独立最终验收。
