# DEV-10 M1/M2 工程收尾（PR #3）

2026-10-19，状态 `ENGINEERING_COMPLETE`。本记录随PR #3合入正式main后生效；实际合并SHA以GitHub合并记录为准。M1/M2实现与既有验收分别见[M1](DEV10_M1_FINANCE_ACCEPTANCE.md)、[M2](DEV10_M2_KNOWLEDGE_ACCEPTANCE.md)。

## 本次审查修复

根据PR #3对head `1848267`的最新审查，仅修改两处目录保护：共享Store的自定义`gm_workbench.sqlite`和财务export均在创建文件/目录前拒绝解析后路径分量`saves/query_snapshots/published/seasons`，忽略大小写。默认派生路径保持可用，策略导出已有对应保护。

实际执行的唯一测试命令：

```powershell
python -B -m unittest discover -s tests -p test_gm_workbench_paths.py -v
```

三项通过：保护目录及混合大小写被拒绝且不创建目标；正常派生工作台可创建；财务导出保护生效且正常_exports目录可生成JSON/Markdown。全部使用临时目录，财务源为合成DTO；未读取或修改观测数据库。既有7+6项测试结果沿用前次证据，本次未重复运行。

## main与交付边界

收尾开始时已fetch并核对最新main `b2c3705`，将其合入开发分支，Git自动合并成功，无文本冲突。保留main新增的研究文档及DEVELOPMENT_CURRENT索引；未将研究规划转为开发任务。PR按玩家授权转Ready并正常合并，正式本地main随后以fast-forward同步；最终SHA由交付回复报告。

M1/M2工程完成；30队策略仍为`UNASSESSED`候选，正式已评估0队。GM V4尚未启用。Web真实连接、cash编码及实际签约验证继续延后；本轮不启动M3/M4，不做新采集、游戏数据发布、正式GM或游戏写入，不修改数据库观测事实。
