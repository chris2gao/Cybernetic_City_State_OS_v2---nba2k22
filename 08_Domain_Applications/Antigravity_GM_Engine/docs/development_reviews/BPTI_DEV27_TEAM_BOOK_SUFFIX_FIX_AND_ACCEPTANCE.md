# DEV27 — team_book() 名称后缀修复与验收

后续部署记录（2026-10-20）：玩家明确授权“如果没合并，你合并下，并继续之前的工作”。本次审阅原两提交后将远端/本地main从52fe691快进至80459b4，包含867fe85修复；未重跑T1–T3。以下“未合main/直接本地交付”属于原DEV27终结时的历史状态。包B在另一独立分支交付，不改变DEV27验收范围。


2026-10-20 | `BPTI_DEV27_BUGFIX_COMPLETE_TASK_CLOSED` | 按玩家最新“直接提交即可”，本地提交交付，未创建PR或合main。

## 修改与边界

从最新main `52fe691`创建`codex/fix-team-book-suffix`。依据DEV27合同，仅修改`src/gm_state_io/team_book.py:team_book()`：原有完整名称精确匹配保留；对NFKC后的书名按空白分出末词，仅当末词casefold等于`playbook`时，将前段规范化后与原球队别名精确比较。`Bulls Playbook`可匹配Bulls；`BullsPlaybook`、`Bulls Practice Playbook`不能因后缀兼容误配。

唯一性仍按匹配书对象数量判断；原名书与后缀书同时存在也报原歧义错误。返回的index/enum_id/unique_id/name原样保留。`normalized()`、`identity()`、`validate_slot()`、`validate_rebind()`和DEV14其余代码均未修改；owner、digest、枚举目标、已确认事件及审批/CAS原实现保持。

其余改动仅为小型静态检查、此验收及AGENTS/33/34/DEV27交接状态。没有修改游戏数据、共享战术池或添加功能。

## 已授权检查与实际结果

执行：`python tests/test_team_book_suffix.py`（使用Codex bundled Python）；仅运行一次，`Ran 3 tests in 0.005s / OK`。

| 检查 | 静态覆盖 | 结果 |
| --- | --- | --- |
| T1 | Bulls/Heat/Warriors小fixture；name、abbreviation、city+name，各自无后缀及带独立Playbook后缀；核对返回原生identity | PASS |
| T2 | 空目录、它队、Practice伪相似、无分隔粘连、非末尾标签、同名双书、原名和后缀双书；均保留原缺失/歧义错误 | PASS |
| T3 | 纯函数validate_slot合法本队通过；错owner/它队identity拒绝。validate_rebind合法事件和本队枚举通过；它队枚举、缺事件、教练身份不符拒绝 | PASS |

T3仅为最小函数级封闭验证，不覆盖完整Stage/Apply/CAS集成；没有新建测试框架，也未重跑旧B0/B1/M3/DEV14套件。

## 限制及结束状态

没有游戏访问、生产采集/发布、内存写入、存盘或真实GM执行验证。逐CRC原生PlayType、动作受益人和比赛效果仍UNKNOWN；修复不启用GM V4、不评估30队、不启动B2–B6或DEV24。

实现提交：`867fe85`（`fix: match independent terminal Playbook labels for own-team books`）。玩家在提交完成后明确“直接提交即可”，因此本次以本地提交交付，不创建Draft PR、不自动合main。当前任务已终结。
