# DEV10 M3A 本地工程验收

日期：2026-10-19。结论：`M3A_LOCAL_ENGINEERING_COMPLETE`。这是开发分支的工程交付，不是实际30队分析、网页连接验收或main部署。入口：[分析手册](../../web_gm/manuals/ANALYTICS_M3_WORKBENCH.md)；[M3B验收](DEV10_M3B_ACCEPTANCE.md)。

## 实现与直接证据

| 要求 | 实际实现与本轮证据 |
| --- | --- |
| 已捕获累计统计可用 | QuerySession新增q_team_stats，同批snapshot/team join，只有业务计数JSON与赛季年，无raw_struct/地址；CLI team stats。合成新来源/缺来源路径均验证，实际M02读取30条 |
| 全队全员事实 | analysis_inputs按真实cursor读取，页长不足50仍续页；prepare验证完整来源identity集合。实际M02 30队466在队身份，非固定人数断言 |
| 指标与区间 | 计数先减后重算，保留输入/分母/公式/ref/UNKNOWN；零场、负增量局部缺口、不同上下文不比较。来源season_year=2022对应2021-2022的结束年，实际CLI确认；保留原始统计而不改观测 |
| 人物身份/能力/合同变化 | `.value`读取；多字段唯一匹配仅TEMPORAL_CANDIDATE，暂定attributes/contract/season_totals变化分别记录；歧义不计确证成长、交易后累计不当新队贡献 |
| 来源和评估分开 | source_access记录真实分页、rows、身份、source binding、LOCAL_CLI执行来源。SQL筛选人口、实际返回READ、模型ASSESSED分开；未伪造WEB_ACTUAL_SESSION |
| 员工/教练/财务/资产 | 同批1458员工行、30教练、870整体防守、504原始签位行、30财务行。签位原始行含无法认证资产ID的历史条目，不能把504行当504枚可交易简单签位。员工8原生角色/6UI岗位与效果未知分别记录 |
| M1/M2参考 | 固定具体finance_run和strategy revision；跨career拒绝、跨batch标参考；知识卡冻结为参考，cash签约容量仍UNKNOWN |
| 注释/封存/证据 | import只能写模型注释；optimistic revision、封存不可变、30队注释覆盖决定COMPLETE/PARTIAL；facts/metrics/knowledge/finance/strategy及市场补查ref可追溯 |
| 市场真实筛选 | roster/pool/staff实际执行，使用参数化SQL与登记字段、明确顺序、identity破同值；缺值不补0。封存后补查含零匹配都有独立回执，相同query ID不可改条件 |
| 有界入口/导出 | prepare/import-analysis/seal/show/team/players/market/screen-market/evidence/export已执行；默认20/max50、市场max5、字节预算与cursor。导出显式新目录/来源可用检查，拒绝事实/正式赛季路径 |

运行契约由标准库Python校验器统一执行，不宣称运行外部JSON Schema；无新增jsonschema或模型服务依赖。没有新原生采集来源、数据库观测修正或生产增量采集机制。

## 实际M02演练

career=`mc_haliburton_2021`，batch=`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，游戏日2021-12-12。只读取已有M0静态副本；派生run=`M02_853e7e6a`，源码版本为当次开发工作树，run如实记录code_commit与dirty状态。

| 球队 | 本批完整名单 | 实际分页 | 累计比赛数 | eFG（fraction） |
| --- | ---: | ---: | ---: | ---: |
| GSW | 17 | 3 | 25 | 0.5695749440715884 |
| SAS | 15 | 3 | 24 | 0.5038919413919414 |
| OKC | 16 | 2 | 24 | 0.5261516314779271 |

数字由CLI/Python读取和计算，每队实际返回identity集合与封存来源完全相等。这是相对于旧V3手工阅读方式的工程消费对照：新增统计/完整名单/缺口/访问证据可以直接钻取；**没有给三队编经营目标、认定卖方/买方或声称改善了篮球判断**。

市场补查实际执行了三类问题：排除GSW后的在队3pt_shot.value≥75、历史新秀标记pool模型、未分配角色staff。每类返回5个候选并保留SQL人口/匹配/未知与具体身份。pool模型仍SCOUTING_ONLY，未认证FA。M02封存状态SEALED_PARTIAL，真实球队注释/正式评估0，30队策略未升级。

完整本地开发工件：`_exports/m3_acceptance_853e7e6a/report.json`及同目录派生库、query文件、M02精简导出；工件不入Git。少量可复核工程摘要随本报告和[M3B报告](DEV10_M3B_ACCEPTANCE.md)版本化，不发布源JSON或SQLite。

## 本轮检查与发现的局部问题

范围内命令 `python -m unittest discover -s tests -p test_gm_m3.py -v`：15项通过。覆盖来源/指标/分页/身份、双边报价/组合、M1/M2共享存储、版本与离线教练等相邻M3路径。最后对直接受影响的counter/bilateral/atomic/coach检查及教练候选动作映射做定向检查，均通过，未扩全项目回归。

实际CLI联合演练成功89次调用，含真实M02查询/筛选/封存/导出，以及全合成30队P1–P5；详情见M3B。开发中发现旧签位asset_id可为null会干扰无关证据查找，已局部修复并加入对应检查。合成30队fixture的员工候选槽位冲突也已修正；未修改真实观测。

网页真实连接、现金语义调查、签约/游戏实机验证按玩家安排延后。本轮没有游戏句柄、数据采集/发布、生产事实改写或正式GM运行。
