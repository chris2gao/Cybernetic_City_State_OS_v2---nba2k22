# DEV-20261018-10 V2 / M0 — SQLite 本地访问验收

核对日期：2026-10-18。状态：`IMPLEMENTED_LOCAL / ENGINEERING_DELIVERY_COMPLETE / WEB_CONNECTIONS_DEFERRED_BY_PLAYER`。

玩家在开发中明确修正原C3/E验收条件：本轮完成实现和PowerShell本地访问验证即可交付，三个Web连接由玩家以后建立，连接问题届时修复，不阻塞当前交付。**未标M0_CONSUMER_ACCEPTED，未声称Web角色实际连接成功。** 现行GM规则不因M0切换。

## 实现与范围

- `src/gm_data_access/snapshots.py` / `scripts/gm_data_snapshot.py`：从已有exporter审计双库ZIP建立静态同批查询副本，复用SQLite backup语义；源审计/双库时间/原始池绑定/游戏日期核对，本地SQLite文件封存，批次不可覆盖。
- `src/export_web_gm.py`：既有备份完成后从同一归档建立本地查询副本，成功前不切换latest。无新采集任务、无新数据指针、无修改published字节、无自动上传。
- `src/gm_data_access/query.py` / `scripts/gm_data_query.py`：球队/名单/球员池/员工岗位和候选/合同/19教练/18对手防守/简单三届签位/财务语义业务视图，按snapshot固定。默认20、上限50、约20KB小结果、批次游标、受控SELECT聚合和约2秒SQL超时。SQL不能直读原始表、BLOB、地址或历史未筛行。
- `scripts/set_gm_query_permissions.ps1`：独立非管理员消费者RX/显式拒绝写删，拒绝活动saves访问；拥有者权限保留。由于玩家留待以后建立连接，本轮没有实际配置消费者账号或运行ACL脚本，不把文件只读属性当作用户隔离证明。
- `DATA_ACCESS_CONTRACT_V2`：每次查询的来源/角色声明/条数/覆盖/状态/工具与实际时间；`issues`给出最小问题入口，不开发M4反馈工作台。
- [操作手册](../GM_SQLITE_QUERY_ACCESS.md)、[消费者契约](../../web_gm/data_contracts/CONSUMER_DATA_CAPABILITIES_V2.md)和三角色基线入口已同步；AGENTS、32/33/34/35、31及来源登记更新。36/执行能力表不新增写入能力，原执行批准边界不变。

## 实际验证

1. `python -B -m unittest discover -s tests -p test_gm_data_access.py -v`：**24项通过**，合成隔离库。覆盖跨批行隔离、分页/限额/预算、同名身份、候选岗位不冒充任职、三届选秀权、19教练与混合防守、原值保留、拒绝SQL写入/ATTACH/扩展/原始表/注入/CTE、超时、双库缺失/摘要被改/审计绑定及历史/未发布状态。没有游戏连接。
2. `python -B -m unittest discover -s tests -p test_coaching_export_integration.py -v`：**5项通过**，既有合成SQLite导出夹具补齐真实格式的绑定，验证查询副本钩子、未上传状态、旧包不追填教练、审计失败和查询副本失败保留旧latest。全源实机审计在该夹具中仍是显式stub，不冒充实机采集。
3. `./scripts/verify_gm_sqlite_m0.ps1 -Career mc_haliburton_2021`：PowerShell调用本地查询成功；**16项真实M02副本CLI检查通过**。SAS完整名单和8岗位、Popovich、候选主帅、1984 Jordan历史新秀模型、未在队模型、55能力/合同小批、19默认教练、18对手防守、三届签位、30队聚合、全名单计数、财务语义、问题入口及写请求拒绝。命令不会运行正式GM；检查名称不是三个Web窗口的验收。
4. 单独运行手册中的PowerShell参数化SQL示例，成功返回SAS少量姓名/工资记录；`git diff --check`通过。

真实副本绑定：`mc_haliburton_2021` / `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，游戏日期`2021-12-12`，`data_updated_at=2026-10-18T12:12:13.170996+00:00`。这是既有M02观察，不是本轮采集或新发布。本地查询记录名单466人，SQL按队聚合返回30行，按需逐页消费而非全池上下文。

细节和逐检查结果见[机器证据](DEV_20261018_10_M0_LOCAL_EVIDENCE.json)。本轮没有运行全项目测试、JSON同步验证脚本、游戏写入/保存/重启、采集或数据发布。

## 财务语义核对与保留项

本轮核对现有解析代码：`cash=TEAM+0x1010`、`budget=+0x1014`、`staff_budget=+0x1018`、`total_salary=+0xCBC`、`payroll=+0xFF4`均由require_uint32读取；收入在+0xFD8/+0xFDC/+0xFE4。球员薪资按31位掩码读取、共享高位保留。原生UI签名/时间跨度/财务购买力未在本轮重新研究。

|队|cash原始uint32|单列signed32解释假设|可签约资金认证|
|---|---:|---:|---|
| CLE | 4288804119 | -6163177 | UNKNOWN |
| NOP | 4290109259 | -4858037 | UNKNOWN |
| ORL | 4291474586 | -3492710 | UNKNOWN |
| UTA | 4293156901 | -1810395 | UNKNOWN |

用户指出现金有符号/无符号bug可在开发时不被发现，这是接受实现优先、后续修复的例子。本轮不追加现金专项测试或修复：raw不改、signed32是单列解释，不回写任何真实数值。`finance semantics`覆盖total_salary、payroll、budget、staff_budget、cash、三类收入、球员当前薪资/六年槽及员工薪资，区分编码、单位、时间口径与证据。**payroll不当作当前合同总额，收入列名不证明月度周期，预算差/现金/工资帽差不自动变成合法签约空间。** 所有资格输出UNKNOWN。

## 后续与未验证边界

- Web DEVELOPMENT/ANALYTICS/GM真实连接、消费者账号ACL部署由玩家以后建立；不是本轮剩余阻塞，不冒称已完成。
- 本轮只实现M0；派生工作台、财务模型、GM V4切换和反馈引擎属于M1—M4，未启动。
- 现有JSON及Release兼容保持；不开发大JSON分页、不更改玩家触发全量采集机制。
- [玩家开发规范](../DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)已归档并引用：优秀实现优先、合理边界、适量验证；允许当时未发现且被认为正确的bug，在后续使用/开发中发现后修复，不以穷尽检查挤占实现。
