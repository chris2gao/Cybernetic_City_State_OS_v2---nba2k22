# VAE V2 三层原型 · 集中独立审核报告

**审核任务**：`NBA2K22-VAE-V2-PROTOTYPE-INDEPENDENT-REVIEW-20261030-001`。**固定对象**：`5d7fdcc9ed277f0db79fa0e986483dfe6d00f06a`。**上一轮审核**：`db57418981b99ad09aa74a656fe0d7859ffdb94c`。**依据**：Human V2三层目标及PROTOTYPE_CAPABILITY_EVIDENCE_MATRIX_V2原始文件。

## 裁定：REWORK_REQUIRED

V2**不是完整可验收原生操作+机制方法论+真实数据闭环**。它确有Python代码、12个动作规格、5个Seed影响边、角色数据Mock视图、R01–R09修订、测试及文档。但Human明示“离线脚手架不是完整原型”。应按三层分别记录：
- **Pillar1 Native**: 12个 ActionSpecification+execute_dryrun()，全部仍BLOCKED_AWAITING_GAME_AUTH；无本轮真实Native变更与独立前后读回。声明12项真实原生操作能力**不成立**。
- **Pillar2 Methodology**: 5字段+5边的种子表；非单项完整库。部分edge_type=DIRECT_CAUSE而verified_in_game=false，更新证据等级仅依据调用方传入 outcome。
- **Pillar3 Data**: RoleDataService不是D2/D3真实采集服务，而是固定CHI/Player数据。ACL只比对调用方可指定的RoleType和category，不校验被查询player_uid/team/save归属，存在越权结构风险。

## 关键测试与证据

1. GitHub base `45cc45cae0550ddcda192a2179ea48509b27f6ee` → `5d7fdcc9ed277f0db79fa0e986483dfe6d00f06a` **42个改变文件**，全部在开发Run和其已批准src/vae、tests/vae、config/vae路径内，分支范围合规。
2. 开发回执中`54 passed`与24项检查`PASS`为**开发者自测声明**；GitHub Commit status为空。本审核没有完整 checkout，**不宣称独立重跑54项测试**。
3. 审核者对固定源码逻辑构造并实际运行5个独立最小反例（source-equivalent，不是原包直接import）：GM奢侈税计算、角色跨对象ACL、R08文件失败却报成功、R05假字符串升级L3、机制图谱仅看调用方结果标verified。执行输出可在报告/本次审核记录重现。
4. 已确实修复部分旧P0：静态配置改为`STATIC_SPEC`、模拟比赛改为`NOT_OBSERVED`、R06增加Save/engine路径检查；但`Preflight READY`仍无可信身份与授权回执，R08 durable写入失败仍返回True，R05仍由任意字符串断言验证层。
5. `GM-01`函数以`max(0, payroll-tax)`命名`luxury_tax_projected`，实际是超税额，不是分档税金。2021–22官方工资帽/税线确实112.414M/136.606M；这不证明游戏内部使用全部现实CBA规则。现实2021–22超税1M的首档税率通常为1.5倍，须区分现实oracle与PC22引擎。来源： https://pr.nba.com/nba-salary-cap-for-2021-22-season-set-at-112-414-million/ 与 https://www.hoopsrumors.com/2021/08/salary-cap-tax-line-set-for-2021-22-nba-season.html 。
6. 无授权游戏操作、SaveReload或原生效果；不将离线验证等同LIVE。

## 分级Finding与关闭条件

| 编号 | 级别 | 现状 | 修复要求 |
|---|---|---|---|
| V2-01 | P0 | Human三层原型第一层未实现真实Native执行 | 逐项标真实GAP/BLOCKED并向Human请求有界授权；不得将12规格写成12 Native执行能力。 |
| V2-02 | P0 | 角色身份与对象ACL未绑定 | 可信Actor/Save/Team/Player身份由宿主绑定；负向跨球员、跨球队、伪WORLD_ADMIN用例。 |
| V2-03 | P0 | R08写盘失败仍返回成功并标APPENDED | 写失败必须失败状态，持久成功只在durable确认后；重启/注入写失败/并发重复测试。 |
| V2-04 | P0 | R05只靠任意字符串将Getter/UI/SaveReload标VERIFIED | 验证式证据对象，要求真实原生Getter及持久化独立读回，假字符串负向测试。 |
| V2-05 | P1 | GM税额确定性Oracle错误 | 以Human确认的PC22规则与现实参考区分；独立计算阶梯税及赛季版本、边界测试。 |
| V2-06 | P1 | 模型映射存在互相冲突的规则与未证先验 | 每条规则标League year/game settings/出处成熟度，待Human定例外。 |
| V2-07 | P1 | 角色查询输出硬编码却声称可用 | 仅OFFLINE_FIXTURE，不可供真实角色决策；接通可信采集及freshness/source/permission后再升级。 |
| V2-08 | P1 | 方法论图谱只有5项Seed且因果分级未证 | 机制清单字段级覆盖、source-grade分离，效果等级由可核验receipt更新。 |
| V2-09 | P1 | 旧P0部分修复但READY权限仍易伪造 | 绑定签名/可信授权与原始LIVE采样证据；不可只依赖字符串黑名单。 |
| V2-10 | P1 | R06静态比较字段补齐但来源与真伪未验证 | 构造跨Save/engine/trial/build反例，并实机验证前保持NOT_OBSERVED。 |
| V2-11 | P2 | 54项pytest只具备开发者回执 | 在只读干净checkout重跑并保存可复验日志和实际exitcode。 |
| V2-12 | P1 | Human V2三个支柱并未都达到交付门 | 报告PARTIAL/BLOCKED并提供每类所需Native能力与Reader授权包，不能宣布COMPLETE。 |

每项详细固定源码函数及证据见`07_测试执行/evidence_matrix.json`。

## 原审核问题复审

F02 PARTIAL，F03 offline initial-state FIXED，F04 **NOT CLOSED**（耐久失败仍成功），F05 Developer tests present, not independent PASS，F06来源隔离仍只在部分对象做对，F07 READY仅字符串黑名单、READBACK字符串L3，**PARTIAL**。不得简单全部标resolved。

## Human与下一步

**不建议 Human 当前接受为 V2 产品原型完成。** 可以认可“离线脚手架阶段性进步”，但不得对GM/Coach/Player宣称已拥有真实执行或可靠角色决策数据。下一步Gemini保持同一主开发任务集中修复：可信身份与权限、Native动作成熟度登记与最小真实测试授权请求、R08持久失败语义、R05分层来源验证、财务公式及真实D2/D3采集。受保护动作仍须单独Human批准；审核不启动实机。

## 模型与审核窗口

本次依照Human明确允许继续使用原GPT-6审核窗口，审核者不同于Gemini开发模型，但**并非新的隔离Fork**。平台窗口实例/模型身份外部认证UNKNOWN。GitHub Run恢复，不声称PRMS Save成功。审核只向本专用分支Run写入报告，未修改开发者分支、master、Core或游戏。
