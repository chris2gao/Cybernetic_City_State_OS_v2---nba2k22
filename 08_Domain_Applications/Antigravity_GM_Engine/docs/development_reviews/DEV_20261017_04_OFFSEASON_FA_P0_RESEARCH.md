# DEV-20261017-04 P0：休赛期自由球员机制与来源调查

日期：2026-10-17。状态：**PARTIAL_RESEARCH / REAL_GAME_NOT_VERIFIED**。
规格来源提交 `527bf10`，任务书初次提交 `3ff1ff5`。这是源码/归档调查记录，**不是P0实机验收通过记录**。

## 玩家环境与本次授权

玩家确认载入 `MyCAREER0004`，MC模式，第一个赛季常规赛；所提供的存档文件存在。玩家确认没有休赛期测试副本，先交付可完成的P0与离线部分，并明确“现在先不用测试”，休赛期另行通知。

本次没有创建/载入测试存档、推进日期、操作游戏菜单或签约，没有打开游戏读写句柄，没有采集正式数据库或发布事实包。只查询了进程与存档文件元数据。界面观察先遇窗口最小化，激活后截图超时，未取得可用截图；窗口激活不是机制证据。未将MC误记为MyNBA，未假定MC可以设置30队用户管理。

玩家澄清的目标架构：**竞价、择队与方案生成在游戏外完成，具体签约获批后再写回合同及必要关联**。无需让原生谈判系统参与竞价；是否被原生签约覆盖、合同和转队是否持久有效仍须实测。

## 已取得证据与可复现清点

新增 `scripts/offseason_research.py`：不导入游戏内存模块，不运行全量采集/导出/发布；只读取指定既有归档，SQLite以 `mode=ro`、`query_only=ON` 打开。输出仅允许 `_exports/` 子目录，已有目录不覆盖。

本次在玩家说“现在先不用测试”之前运行的字段清点命令：

```powershell
python scripts/offseason_research.py --archive-save-id mc_haliburton_2021 --output _exports/offseason/p0_20261017_inventory_v2
```

实际使用Codex bundled Python。输出 `P0_INVENTORY.json` 留在本地；未提交数据库、日志或运行时指针。首版从 `league.json` 取不到 snapshot_id，源码核对后改读 `data_update.json` 再运行清点，未改变归档。

被选归档：`2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`，数据时间 `2026-10-17T11:50:28.464724+00:00`，游戏准确日期未知。这不是新采集，也不证明当前载入文件与该归档是同一状态。

| 对象 | 清点结果 | 能证明的范围 |
| --- | --- | --- |
| published大名单 | 30队、466人，均含六年薪资与下表合同字段 | 历史字段可用性，不是休赛期到期认证 |
| 实际库 `player_source_details` | 所选snapshot 466行 | 细节JSON存在；没有提取/公开BLOB |
| 实际库 `player_monthly_stats` | 所选snapshot 466行 | 月度薪资/年限有生产读取 |
| 实际库 `team_monthly_stats` | 所选snapshot 30行 | 财务观测字段存在 |
| 实际库 `market_free_agents` | 所选snapshot **0行** | 表为预留，不证明真实FA池已采集 |
| `league.rules` | season_code=`2021-2022`，ACTIVE | 模板CONFIGURED，不是下一季实机规则 |

## 字段矩阵与语义边界

布局来自 `config/memory_field_profile.json`、`src/source_extensions.py`、`src/auto_pipeline_ingest.py`、`src/export_web_gm.py`。本次核对源码和归档存在性，没有重新验证当前内存或休赛期变化。

| 字段 | 现有布局/状态 | 休赛期尚未证明 |
| --- | --- | --- |
| `years_left_on_contract` | +0x32E，bit2起4位；月度 `contract_years_left`，历史OBSERVED | `==1`不证明下一季UFA；跨阶段语义UNKNOWN |
| `original_contract_years` | +0x341，bit4起3位；历史OBSERVED | 不证明续约/选项结果 |
| `contract_option` | +0x317，bit4起2位；已有标签 | 未验证行使节点，选项未决不得入池 |
| `extension_length/option` | +0x341 bit7起3位 / +0x342 bit2起2位 | 不能忽略延长合同而判到期 |
| `bird_years` | +0x356 bit6起4位，跨字节 | 不等于认证Bird/Early/Non-Bird资格 |
| `contract_year_1..6` | +0x1A4..+0x1B8，每项低31位 | 槽位滚动/目标季承诺语义UNKNOWN；写回须保留共享高位 |
| 当前/合同球队 | +0x60/+0xA8，uint64指针，捕获内解析 | 不是低字节ID；转队还需双向名单/合同关联 |
| total_salary/payroll | 球队+0xCBC/+0xFF4，uint32 | 汇总刷新时点与签约联动UNKNOWN |
| budget/cash | +0x1014/+0x1010，uint32读取 | UI单位、符号、支用权限、税结算周期未认证 |
| cap/tax/apron | 模板→seasons→league.rules，CONFIGURED | 仅2021–2022模板；不能认证未来季规则 |
| 空间/特例、最低/最高合同、服务年限、要求年薪 | 无认证休赛期来源，UNKNOWN | 不用现实履历、默认OVR/年龄或工资差核发资格 |
| RFA/QO/匹配权、独立FA目录、可用席位 | 无认证生产读取，UNKNOWN | 未映射球队指针、空工资和表名不能证明自由身 |
| 稳定身份 | 姓名/face/model/槽位为捕获局部证据 | 跨赛季连续身份未认证，同名/克隆不能按姓名合并 |

`src/gm_core/finance.py` 的 `salary_cap_minus_payroll_proxy` 仍是代理；模板规则不升级为游戏观测。休赛期专用来源不扩展普通月度完整CBA采集。

## 原生AI、停点及写回路径

| 问题 | 当前状态/拒绝代码 | 下一条有效证据 |
| --- | --- | --- |
| CPU签约前可冻结的节点 | `OFFSEASON_SAFE_GATE_NOT_FOUND`，未知，并非证明不存在 | MC测试副本各节点UI、只读前后记录；玩家控制推进 |
| 30队自动续约/签约能否关闭 | `NATIVE_AI_SIGNING_NOT_CONTAINED`，未知 | 精确选项名/界面、MC支持性、存盘重开与干扰记录 |
| CPU交易开关是否足够 | **不能作为签约控制证据** | slider_manager只列CPU_CPU_TRADE、续约积极性等，无认证签约关闭入口；不写0试探 |
| 到期与薪资槽跨节点变化 | `CONTRACT_TRANSITION_NOT_VERIFIED` | 同一身份在常规赛末、选项后、FA、新季的合同/UI对照 |
| 游戏外报价合法性 | `SIGNING_ELIGIBILITY_NOT_VERIFIED` | 目标年度规则、逐人限额、逐队真实资格与独立财务约束 |
| 游戏外结果写回 | `EXECUTOR_NOT_VERIFIED` | 验证最小合同写回；跨队另验名单/合同队/汇总，无需原生谈判参与竞价 |
| 重开/下一季持久性 | `CROSS_SEASON_PERSISTENCE_NOT_VERIFIED` | 测试副本保存重开、下一季30队核对；不自动推进当前局 |

`GameMemory`默认只读，裸writer不是签约执行器。未新增 `offseason_execute.py`，未恢复旧modifier。不得整块复制raw_struct、覆盖31位共享标志、额外扣税或修改能力/潜力/徽章/倾向。

## 阶段准入与恢复条件

- **P0实机完成：否。** 完成源码/归档清点和证据分类，等待玩家休赛期测试通知。缺测试副本不是三次修复失败，不写FAILURE_LOG。
- **P1合成数据离线开发：可继续。** 不认证本局合法报价、真实FA覆盖或可执行签约。按玩家最新要求不运行测试。
- **P1真实来源：不通过。** 休赛期最小专用来源未实现；不从月度JSON推断到期池，无自动capture入口。
- **P2/P3：未实机开发验收。** 工程授权不等于正式签约批准，不授权推进本次赛季。

未来最小来源只处理本任务所需阶段、身份、合同/选项、年度资格、财务、席位。恢复时重读任务书/基线，先确认测试副本与模式；不能用MyNBA资料代替MC实测。

## 测试记录

本阶段没有运行单元测试、游戏测试或写回验收。实际执行仅是上述离线字段清点及Git/源码读取。玩家要求“现在先不用测试”后未再运行研究脚本、规划器或验证器。历史文档的PASS不是本任务证据。
