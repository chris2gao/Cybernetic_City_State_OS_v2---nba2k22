# DEV-20261017-07 来源与发布接入验收

状态：`IMPLEMENTED_OFFLINE_INTEGRATION_PASSED / REAL_PRODUCTION_RUN_NOT_PERFORMED`。未部署main，未运行真实全量采集，未调用数据发布器或新建Release，不能报告D项已完成真实生产验收。

来源集成源码提交：`8473d7f9c1687135694443d39ddbd719f8fce2c3`。这是代码证据SHA，不是新的游戏数据批次或发布提交。

## 正常入口中的实现

既有`run_data_update.ps1`调度不变。`auto_pipeline_ingest.py`在现有只读句柄、同一个名单目录与同一snapshot事务内捕获教练；不再打开另一只读会话后把较晚快照冒充同批。严格核对根目录、30个球队指针、当前主教练身份与阵容、19值/原生块和29对手集合。失败回滚并拒绝新批次。

事实写入`coaching_source_captures`与`coaching_team_observations`，保持snapshot/save/data_updated_at绑定，冻结当时profile。`audit_sampling.py`使用其既有RO句柄重读，对照进程绑定、原生布局、教练/名单/动态手册、默认块和认证整体块。仅manifest声明本批已捕获时要求该新来源；历史批次缺失保持缺失。

实际导出器在创建新输出前加载同批SQLite和源审计证明。来源缺队、非法身份/原生值、数据更新时间不符或审计缺失时拒绝，旧last-good/latest保持。沿用既有data_updated_at/uploaded_at契约，没有新增网页JSON哈希验证或下载比较。

## 轻量文件

- `coaching/teams.json`：30队当前教练、19值、原始块及readiness，Sim另列GM_CONTROL_DISABLED；不一次塞入870条对手对象。
- `coaching/field_dictionary.json`：19默认字段、动态加载手册、Freelance顺序与34枚举、整体防守字段及原生合法值。
- `coaching/opponents/index.json`及30个`<TEAM>.json`：按owner分文件，每个恰有另外29个对手，仅发布认证整体防守组及原始提交标记，不发布对手进攻/轮换和逐球员操作接口。

共33个文件，由同一个既有bundle staging、manifest、SQLite archive和指针替换流程纳入。正常不带`-Publish`只导出本地，带该开关才走原发布器；本任务没有运行这两个真实流程。

GM DataReader仅当coverage为`VERIFIED_OBSERVED_SAME_BATCH`且career/batch/date/data_updated_at一致时启用默认事实。某队某对手动作才懒加载该owner文件；再次校验owner/29集合/日期。外层GM批次验证还将模型提供的整体对象与实际发布文件比较，不能让模型生成前值成为事实。

## 离线验收

```powershell
python -m unittest discover -s tests -p 'test_coaching_source.py' -q
python -m unittest discover -s tests -p 'test_coaching_export_integration.py' -q
```

分别11项和4项通过，已纳入74项教练测试，不重复运行。前者覆盖同批SQLite往返、失败保存last-good、固定当时profile、只读句柄、33文件、旧批次不补、审计漂移和懒加载绑定。后者使用临时真实SQLite/schema与实际导出器，验证33文件进入manifest/archive、uploaded_at仍为空、新来源失败保留既有包/指针、缺审计拒绝、旧manifest不补新源。

这4项导出集成中，原有全联盟GMEngine audit被显式stub，以隔离新来源接入；不能用它们冒充真实游戏采集、完整原审计或网络发布成功。

后续源边界补充：四个已确认的百分比字段增加 `observation_raw_range=[0,100]`，实际观测raw101即拒绝同批写入，保留last-good。BenchDepth的9–10测试白名单已按玩家要求撤销；11既可真实保存，也可由GM按阵容选择，未猜其完整菜单端点。来源测试现为13项通过，教练相关总计85项、GM40项通过；本次增加的两项包含完整原始块匹配后的非法值与last-good保护，不只是字段值不匹配测试。

## 真实运行还需核对

玩家另行触发正常数据任务后，才能记录真实采集批次与生产审计/发布结果。现有旧AddressCalibrator仍依赖Jordan/Olajuwon及员工固定锚点，自定义测试名单曾缺Jordan，因此正常全量入口可能在教练hook之前拒绝；本任务未擅改已接受的原校准器或绕开它伪造成功。需以届时只读校准的实际结果处理这一风险。

本次只读代码核对进一步确认，正常入口还强制要求有效MC焦点球员及其大名单身份；`dump_player_pool.py`又单独检查历史Jordan/Olajuwon。因此自定义MyLEAGUE支持不能只通过替换一个校准函数宣告完成，仍需独立的数据来源校准/审计规范；本次没有降低原有守卫或自动启动全量采集。

单来源生产更新仍未实现。只读教练CLI、局部开发探针和本分支hook不等于已有“只更新教练”生产入口；不得静默扩大为全量。不得为补齐报告自行运行采集/发布，也不得重新标记旧批次事实。
