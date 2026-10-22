# DEV20 / M4 系统自我进化工程与最小验收

2026-10-20。状态：**M4_ENGINEERING_MAIN_MERGED / GM_V4_NOT_ENABLED**。独立分支 `codex/dev10-m4-system-evolution`，从最新main `5a49d71`开始；此前PR #4已按玩家批准合并，合并SHA `504a4c0656bad0e890c3783c89c656fca5b2e647`，本次不向原PR #4添加代码。M4最初交付独立Draft PR；玩家审核后批准作用域小修正`1e4fb66`并合并，实际合并SHA `c51fa36080ed39c8305635f1cb4363128475fdf0`，正式本地main已同步。

首次实现及PR创建历史：工程实现提交：`652d10763b7bcfa6db811515f148014db74c609c`；独立[Draft PR #7](https://github.com/chris2gao/nba2k22-gm-engine/pull/7)，base为main，创建后核对OPEN/Draft、MERGEABLE/CLEAN。后续仅补交付索引链接，不改实现或重跑验证。

## 实现范围

- M4-A：在已有派生workbench增量登记M4组件，新增development_issues、development_issue_events两表。稳定根因/能力/作用域指纹、独立事件次数、跨批来源、首次/最近、严重度、负责人建议、状态、玩家决定和不可覆盖历史；复用原事务、路径隔离及revision方式，不另建游戏事实库。
- M4-B：可运行 `scripts/gm_development_feedback.py ingest/list/show/triage/export/readiness`。事件输入、SQL分页、结果大小及导出均有界；同事件幂等，同ID变更拒绝；不同档/身份或不同根因不混并。无证据输入为UNKNOWN/RESEARCH，不宣称M4已复现；导入不自动改变玩家暂缓/关闭决定。
- M4-C：小型CURRENT、机器索引、按问题详情及最近历史摘要。导出只写指定新目录、不自动push/创建Issue/调用模型。4条已有参考记录：Issue #6及DEV19 BPTI、季后赛数据采集、独立双引擎校准器的后续规划指针，均DEFERRED。原始事件保留在本地派生库，SQLite不提交。
- M4-D：带日期证据清单和分项readiness。真实PR #4合并与M0–M3-T工程分开于M4分支；Web、生产批次、GM消费、真实30队、无写入演练、Issue #6、BPTI和后续接口/玩家门分别列出。没有实时Web/游戏/GitHub探测，不把工程验收当生产验收，不切换SOP。

主要落点：`gm_core/development_feedback.py`仅校验DTO/证据并计算准备状态；`gm_workbench/development_store.py`是原Store的增量组件；唯一共享改动为Store加入该组件继承。无采集/codec/执行器或gm_core篮球决策修改。使用说明见[工作台手册](../M4_SYSTEM_EVOLUTION_WORKBENCH.md)。

## 本轮唯一五项验收

### 独立审核后收尾：跨存档局部事件ID（玩家本次授权）

审核认可工程主体，仅要求修正局部事件身份。CAREER/IDENTITY的event_key现加入完整scope；同一producer可在不同存档复用event_id。SYSTEM明确表示全局，保留既有键以兼容已经登记的4条系统记录；无表迁移、无历史改写。仅在原test_02补同producer/同局部ID、不同CAREER/IDENTITY分别保存、各自重放幂等及同scope不同内容仍拒绝的断言。

实际只运行 `python -B -m unittest discover -s tests -p test_m4_system_evolution.py -k test_02 -v`，1项通过（5.909秒）；没有重跑另外4项、旧M3/DEV14集合或Issue #6复现。以下5项记录仍是原交付证据，不冒称本轮重跑。本次按玩家授权在修正后将PR #7标Ready、合并并同步正式main；实际合并SHA在状态34登记。

命令：`python -B -m unittest discover -s tests -p test_m4_system_evolution.py -v`。只有5个test方法，调用实际CLI、临时隔离SQLite和合成事件；Issue #6仅复制已有报告引用为离线样例，没有运行净化器。事实占位文件逐项保持原字节。

| DEV20目标 | 已运行证据 | 结果 |
| --- | --- | --- |
| 1 事件导入与证据追溯 | CLI导入、存储、show/history/event-key、原报告/错误/批次追溯，无事实文件改动 | PASS |
| 2 跨批去重和历史 | 两批同根因、重导入幂等、同ID改内容拒绝、不同根因/存档身份分开、玩家DEFERRED保留 | PASS |
| 3 人工状态与修订边界 | 无玩家引用拒绝，APPROVED/自报权限拒绝，CAS旧版不覆盖，显式分流/带修复证据的合成RESOLVED、重复事件不重开 | PASS |
| 4 有界查询与小型导出 | list/history分页与筛选、页数限制、事件/引用大小及raw/地址/私密路径拒绝，CURRENT/index/详情导出、不得写事实目录或覆盖旧导出 | PASS |
| 5 准备状态诚实 | 当前PR4 MERGED与合成OPEN两种状态、缺证PENDING、三Web待验、真实30队UNASSESSED、Issue #6待修、BPTI后置、M4待合并及V4始终未启用 | PASS |

首轮5项均在共同输入校验处失败：路径检测把https://尾部的s:/误识别成Windows盘符。仅修该匹配边界后，原5项全部通过，最终运行10.683秒。没有已通过项目被重跑，没有追加测试案例/文件、全量回归、旧M3或DEV14 119项测试。通过后只进行明确要求的参考问题导入/交接文件生成、文档和Git交付，不另开验证轮次。

## 实际证据与待办

- 当前PR #4合并状态由本任务开始前GitHub API核对；Issue #6实际为OPEN/BACKLOG_ONLY，引用其原报告而非再现。准备清单以日期和引用披露该次事实，不冒称自动在线更新。
- Issue #6完整Registry世界设置键潜力误判：仍未修复；已有合成复现说明，完整目录生产路径存在阻断风险，尚未证明所有生产采集必然失败。玩家已明确留给独立DEV14/其他开发模型。M4不改`src/player_potential_mask.py`、不追加其测试。
- 三Web真实连接、已脱敏新生产批次与GM消费没有新证据；真实30队仍UNASSESSED，正式评估0队；旧M02和合成测试不能替代正式准备。
- BPTI是正式新档前置；季后赛统计采集与双引擎年度校准后续另立项目。51未知倾向、全部CRC与疲劳等原生研究继续后置；本M4无球队经营效果/赛果比较/滑块调参功能。
- 显式triage信任操作者对真实玩家决定的引用，不新增身份认证服务；RESOLVED只记录人工结论，不能替代修复证据或批准游戏执行。工程报告提案不自动成为任务，下一次玩家主动触发开发规划后再提出范围/成本并待批准。

本轮没有访问/修改游戏、运行新采集/发布、建立正式新档或GM回合，也没有改V3/V4规则、正式球队档案、GM_CURRENT或赛季INDEX。源事实、原历史批次与原生安全保护沿用；正式main已包含M4与审核小修正；工程合并不批准正式GM、游戏或后续项目。
