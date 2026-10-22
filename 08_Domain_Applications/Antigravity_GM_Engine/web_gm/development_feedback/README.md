# 工程问题与开发候选交接

本目录是DEV20/M4明确触发导出的轻量工程管理资料，不是游戏事实、正式球队决策、修复授权或后台任务队列。

- [CURRENT.md](CURRENT.md)：当前有界问题页、影响/复现条件/证据/玩家决定和下一触发条件。
- [index.json](index.json)：机器可读页、全池状态计数、游标和筛选。详情按DEV编号命名，每项仅附最近3条历史摘要。
- [readiness.json](readiness.json)：带日期分项准备状态，始终保留GM_V4_NOT_ENABLED；完整证据输入在[config](../../config/m4_readiness_evidence.json)。
- [操作手册](../../docs/M4_SYSTEM_EVOLUTION_WORKBENCH.md)：事件契约、分页/triage/导出、明确输入与不自动运行的边界。

下一次玩家主动触发Web DEVELOPMENT时，先看问题与原证据，再提出最小研究/实施范围、成本和任务书草案，等待玩家选择批准。来源不充分的事项是UNKNOWN/RESEARCH，不编造故障；DEFERRED不自动重开。计划指针不新增PLANNED状态。

本次4条资料来自已有Issue #6与DEV19/DEV20规划。Issue #6保留静态合成报告的风险说明，没有重现或修复；另3条是未来需求而非Bug。独立导入次数不代表生产故障次数。它们已持久化到原本地派生workbench，但SQLite/原始日志不提交Git。

导出默认只写新本地目录，不自动同步GitHub。后续由获得授权的任务在审阅后选择提交小型文件；不要把日志/raw、运行时地址、凭据、私密路径或游戏数据放入本目录。M4既不评价GM战术效果，也不做比赛统计校准或Simulation Sliders调节。
