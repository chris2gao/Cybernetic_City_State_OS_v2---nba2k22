# DEV14 V1.1 — A/B/C/D 工程验收

日期：2026-10-19。分支：`codex/dev14-state-io`，基线 main `635ff2a`。范围为统一确定性状态I/O和多存档底座；不含DEV13实现、M3 Draft PR合并、GM V4启用、生产全量采集或正式游戏写入。操作入口：[DEV14_STATE_IO_RUNBOOK](../DEV14_STATE_IO_RUNBOOK.md)。PR和最终提交以GitHub交付记录为准；本文件不冒称独立开发分支已经部署main。

## 实现与逐项证据

| 要求 | 实现 / 实际验证 |
| --- | --- |
| A：字段字典与三态分离 | Registry直接读取coach profile及归档Antigravity目录；带指纹版本。事实观察表、Desired控制库和Applied回执分开。稀疏stage稳定digest、共享bit合并、USER/CPU双侧不串、UNKNOWN不补50；源事实字节不变 |
| A：受限模型合同 | 仅action_id/object_key/field_key/target_value/reason；拒绝approved、地址、hex写入等额外字段。完整批准dataclass与显式operator参数独立于SQLite status/模型JSON |
| B：原生接入 | 原19默认/18整体复用旧codec；个人防守验证双方native-ID唯一映射；48命名倾向、4PlayType/Initiator、共享战术本68槽、双表Gameplay、world与training接同一批次内核。扩展provider/resolver可注入已审阅代码，不允许CLI加载任意模块 |
| B：批准、前值、恢复 | 整批RO→RW复核→durable全前像→逐块前值检查/写入/读回；失败条件恢复或留PARTIAL_UNRECOVERED锁。重复请求RO重验、不再次写入。RO到RW期间漂移产生REFUSED_BEFORE_WRITE，不伪造部分写入 |
| B：规模 | 50个合成人物×48命名倾向，2,400项稀疏变更一次批准；一次RO+一次RW，2,400块写入及回读。未操作实际游戏 |
| B：旧接口兼容 | 旧coaching batch、single executor、源和export相关套件继续通过；复用既有host/process lock。旧测试把Tempo当只读的过时夹具已改成显式read-only合成profile，不恢复已废止生产限制 |
| C：同批全量来源 | auto_pipeline_ingest同RO会话调用capture_bridge；字段解码器、原source audit、snapshot row binding及Connection.backup/M0安装复用；可选域缺失明确NOT_OBSERVED，旧批不回填 |
| C：消费与对账 | 30队/870整体对象/60合成人物的合成全量观察落库；M0新域实际视图/20行分页/USER-CPU过滤通过。后续原生float32值MATCHED与DRIFT只记录，不触发回写 |
| C：已有M02 | 只读打开现有审计静态副本，30队与旧教练查询通过；六新域均未观测，未修改原副本或历史published。没有把工程实现标成新来源已经生产发布 |
| D：多档、活动绑定 | A/B同M02/同人物ID、不同事实/控制/审批；错档、旧代次、无ACTIVE和legacy-shared拒绝；仅切active指针，不加载游戏。4档限制与retire保留历史生效 |
| D：reset | 精确代次/manifest确认、SQLite backup三库及journals密封、准备新代次、单manifest提交。archive验证/新代次准备/manifest提交/active提交四个点故障恢复旧完整三库；PREPARED中断拒绝工作，显式recover恢复 |
| D：发布兼容与互斥 | 已有无generation协议的published历史时同名reset拒绝，要求新ID。生命周期跨进程互斥实测；capture完整lease、UAC传递和PowerShell安全参数传输在合成/解析层核对；未声称真实提权采集已运行 |

## 实际检查

- `python -B -m unittest discover -s tests -p test_state_io.py -v`：DEV14定向合成组；覆盖完整采集投影、2,400字段、授权、身份、共享块、失败恢复、双档/四档、reset中断恢复、跨进程锁和CLI全量参数传递。
- 直接复用的相关组：`test_coaching_batch.py`、`test_coaching_safety.py`、`test_coaching_source.py`、`test_coaching_export_integration.py`、`test_gm_data_access.py`。具体计数和最终结果保存在同目录[DEV14_ACCEPTANCE.json](DEV14_ACCEPTANCE.json)。没有运行全项目测试或旧JSON同步检查。
- 25个直接相关Python文件AST解析、原生目录JSON解析通过；2个PowerShell脚本仅ParseFile解析通过，没有执行采集脚本。
- 本地静态M02：`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，游戏日期2021-12-12，原采集时间2026-10-18T12:12:13.170996+00:00。只读M0校验，不查询活动saves，不重采游戏。
- 运行日志与临时库位于临时目录/`_exports/`，未暂存数据库、WAL、runtime地址、备份或完整内存journal。机器回执只保存汇总和已公开的来源指针。

## 完成范围与剩余原生接入

**A/B/C/D工程已实现；生产实际运行与玩家批准分开。** 当前registry中，原有教练native证据沿用既有验收，其余Antigravity native布局与读写能力来自玩家明确提供的已测试模块；本轮只验证统一引擎的合成/静态路径，不宣称新的实机UI/保存/跨季验收。

1. 51个未命名倾向字节可原样读取但语义未知，保持READ_ONLY；48命名项按已有目录开放。
2. Mentor关系增删/计数和徽章传授事务没有接入通用writer；不直接改人物Badge或导师进度。已留注册/源provider/locator resolver扩展合同。
3. 超出当前court/world/settings目录可用布局的其它Gameplay、模拟/成长曲线需未来原生字段目录。未知字段不登记为可执行，不展开新的内存定位项目。
4. Playbook仅接受本批实际出现的原生CRC，不能据名称推断PlayType/触发效果。共享owner集合完整纳入对象/批准；切本与改内部槽分步。OVERALL+PERSONAL同一对手修改分步处理，避免未证执行顺序。
5. 缺乏独立游戏save唯一身份来源，正式操作由玩家显式确认完整save/instance/generation；回执披露人工降级，不开放无人监督写入。
6. 同名reset遇旧published协议时按规格允许方式BLOCKED_UNSUPPORTED_GENERATION，不破坏历史。正常新增世界使用新save_id；没有清空既有玩家库。

后续合并部署、玩家加载对应档并明确触发full_verified_v1后，才形成含DEV14字段的新Observed批次。DEV13继续在其独立任务消费对象/字段键、代次及完整审批合同；本工程没有自行启动该阶段。
