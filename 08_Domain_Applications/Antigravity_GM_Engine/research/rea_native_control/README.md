# MyLEAGUE Native Control：机制说明与Issue15功能验证

> 当前工程增量：`NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01` 已在历史62动作上增加2项[日期训练局部操作](TRAINING_PATCH_CONTRACT.md)及1项[明确球员分钟的原生执行](ROTATION_MINUTES_CONTRACT.md)，并将此前不可调用的[四槽PlayType动作](PLAYER_PLAYTYPE_NATIVE_CONTRACT.md)接入专用原生Setter。另增加2项[属性/倾向显式批量操作](PLAYER_STAT_NATIVE_CONTRACT.md)，恢复原有单字段动作的索引Native Setter。当前登记67动作、50绑定/布局（含明确不可调用的签约/父对象复制候选）。[角色能力与批次接口](ROLE_BATCH_EXECUTION.md)保留183项需求、59项有效映射；映射数未因已有动作的恢复而虚增。[发现与排除的调用链](CONTROL_CALLBACK_DISCOVERY.md)有固定静态证据。新增工程仅有离线证据，整体M0–M5尚未完成；下方Issue15内容保留对应历史范围。

本目录是PC NBA2K22离线MyLEAGUE的函数发现与执行接口研发候选。**角色模型首先阅读[机制与执行说明](ROLE_MODEL_MECHANISM_GUIDE.md)**：可设置项、取值、已知影响、输入和执行方法都从该页进入。外部GM/Coach/Player模型负责分析、协商、检查和决定；本层执行确定请求，不估值、不配平、不开发经营策略。

Issue13/PR14原来只作静态发现，Issue15在Human授权的独立测试存档进行功能验证。**当前真实结果见[VALIDATION_RESULTS.md](VALIDATION_RESULTS.md)**。`data/native_live_validation.json`按具体输入覆盖静态登记；不存在“目录里有接口便是实机通过”的推断。PR12旧防守与旧交易证据保持不变。

## 使用入口

| 文件 | 作用 |
|---|---|
| `contracts.py` | NativeBinding、Request、Plan、Result、能力与结果状态 |
| `registry.py` | NativeActionRegistry：加载动作、参数Schema、Native绑定和缺口 |
| `facade.py` | NativeControlFacade：prepare/render/dispatch及GM/Coach/训练/球探方法 |
| `runtime_codegen.py` + `runtime/` | 真实Frida源码生成器、fresh对象解析、参数编码及单次原生调用；不会在生成时附加游戏 |
| `transport.py` + `run_native_program.ps1` | 为下一任务准备的REA CLI实际执行后端；默认禁用，需要显式新任务运行上下文与管理员会话 |
| `readers.py` | NativeReadCatalog、NativeReadQuery、NativeReadFacade，统一数据查询与部分覆盖标记 |
| `data/action_registry.json` | 九域静态动作及新增执行路径；逐项成熟度/输入/调用链/UNKNOWN |
| `data/native_live_validation.json` | 本任务具体字段/输入组合的原生返回、独立回读与未验证轴 |
| `ROLE_MODEL_MECHANISM_GUIDE.md` | 给GM、教练、球员模型的机制与参数使用手册 |
| `data/native_bindings.json` | 具体RVA、Win64参数、对象、阶段、代码指纹及来源；不完整绑定不能执行 |
| `data/read_catalog.json` | 12类数据集覆盖、旧Reader复用点及未绑定字段 |
| `ACTION_SURFACE.md` | 人工可读的逐动作覆盖清单，由上述登记生成 |
| `DISCOVERY_NOTES.md` | 新恢复机制、关键ABI、证据与具体缺口 |
| `NEXT_TEST_HANDOFF.md` | 下一轮最小测试清单；本轮没有运行 |

模块采用本项目的目录导入约定：把此目录放入调用方`sys.path`，或从此目录运行CLI。以下只是接口形式，**不是本轮执行或Fixture**：

```python
from contracts import NativeActionRequest
from facade import NativeControlFacade

control = NativeControlFacade()      # 没有transport：不会访问游戏
request = NativeActionRequest(action_id, exact_model_parameters)
plan = control.prepare(request)
program = control.render(request)    # 只生成JS；UNKNOWN绑定不能生成调用程序
result = control.dispatch(request)   # 默认返回PREPARED_NOT_EXECUTED或UNKNOWN_BINDING
```

可用的命名接口包括`gm_trade`、`coach_defense`、`coach_offense`、`coach_settings`、`ensure_opponent_gameplan`、`train_team`、`train_intensity`、`scout`、`draft`、`sign`和`read`。**存在方法不代表该机制已恢复或可执行**：例如`sign`保留报价结构/函数候选，当前返回UNKNOWN_BINDING。`scout(...,goal_index=None)`走原生新建并追加指定对象目标；显式提供goal_index走低层既有目标setter，Trip聚合刷新仍单列待测。

运行时由执行者构造`LiveExecutionContext`与`ReaCliTransport`后注入Facade；默认不会运行。后端不安装软件、不自动提权、不重试；调用前验证唯一进程、完整EXE SHA和准备脚本SHA。当前Human已授予本任务持续执行权，批次文件记录该直接指令，不要求角色模型另行逐条申请许可。次数是外部桥发起的原生调用次数，不等同游戏内部嵌套调用数。返回拒绝保留原请求；没有回执或异常返回UNKNOWN，不自动重放。

## 已有与新增调用逻辑

- **继承成功**：`0x146eaa0` Gameplan→Coach Apply；`0x132b840`交易包装入口及AddPlayer/Validate。原成功案例只对应PR12的具体对象和值；参数化代码的新组合没有新实机证据。
- **Coach扩展**：六项POE，以及BenchDepth、RunPlayTendency、ZoneUsage、BenchUtilization，共10个当前Coach投影字段。未知的引用对象槽仍仅允许NULL分支；没有把旧“playbook引用”便利命名当事实。`COACH_SET_ROTATION_POLICY`只覆盖两个Bench字段，不冒充首发/分钟设置。
- **交易执行**：`gm_trade`默认转到`TRADE_EXECUTE_AGREED_PACKAGE`，私有提案→AddPlayer/AddPick→原生上下文Getter→直接Process，跳过外围FullCheck和外挂经营审查。Process内部身份检查保留。旧动作的完整检查路径仅保留为已有研究接口；不配平、不替换资产。多资产静态格式不冒充全面实测。
- **训练**：`0x1325f10`，`void(TEAM*,native_date_key,private64-byte input)`。三项focus float、三项profile byte、38项subfocus byte及3-bit intensity有静态格式；只给强度时先取得当前daily记录再保留其他值。日期是原生键，不猜公历转换，不自动换日期。
- **球探**：当前届次、公开候选身份、原始排名/点数、剩余次数；指定对象目标构造与原生追加链；显式执行已配置specific-prospect目标的考察。不会在无目标时调用原版自动择人分支，也不把原始点数当成已解锁能力报告。
- **选秀**：读取当前原生选择记录、用原生函数反核模型指定pick_id、核对归属/未使用，再选指定当前届次新秀。仅当前活跃选秀场景，不推进到未来顺位。UI场景、编号展示及副作用留待下一任务。

签约/续约、裁员、员工属性、球员Potential/徽章/其它资料、完整轮换、Playbook提交等仍有明确缺口。复制函数/原始布局、MyTEAM/MyCAREER或创建球员编辑器状态不直接晋级为MyLEAGUE可调用业务服务。

读取接口区分`unknowns`（阻止该调用的结构缺口）与`coverage_unknowns`（已绑定Reader仅返回已知子集）。例如球员读取当前只输出身份和合同，不称完整属性/徽章已实现；球探返回原始进度与UNKNOWN报告字段。所有数据集都有`coverage_complete:false`。

## 来源、边界和交付

固定PC22构建SHA256为`1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。新证据在`evidence/static/`，来自有界ASCII/RIP引用、chained-unwind函数、静态类型注册和既有REA证据；没有整游戏Ghidra重试。类型CRC名称匹配不替代函数ABI和业务意义，前缀窗口不冒充完整函数。

次世代参考使用[2K官方MyNBA功能公告](https://newsroom-uk.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)，只补MySTAFF、训练与Conditional Coaching的功能线索；实际PC22绑定均取本地PC22证据。见`data/reference_leads.json`，没有移植次世代地址。

原始静态文件保留字节与哈希，不上传EXE、资产、存档、凭据或绝对运行时地址。旧Writer和PR12证据不改写。仅指定分支提交与Draft PR，不合并master。交付语法检查不能证明代码功能、游戏操作、持久性或独立审核通过。
