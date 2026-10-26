# 下一任务入口：全生命周期场景与增量采集

先由 Human 组织本次候选的独立审核；本文件供后续独立开发任务使用，不启动采集或未来场景。
正式状态和精确提交见 `08_结论/review_fixes_completion.yml`、`08_结论/publication-receipt.json`。
本次受控测试候选 `b847f717df6702fe6251872d64aed476ac707f6f`；后续同一应用树的证据交付提交不改变应用代码。

## 可以直接复用

- 应用根：`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/`；20族 Reader 与原重启/恢复设施保持，新增四年度来源的明确所选记录补录路径。
- v25 定义：`schema_model.py`、`schema.sql`、`field_dictionary.json`、`TABLE_CARDS.md`。101表/1789列；公开与 owner/restricted 查询边界继续适用。
- 最终副本：本 run `_runtime/migration/world-v25-final.sqlite`，SHA256 `f3ae5fd169845b7ad87fc3da96be37e59f514eb612a82e5b0e2afc0b2a7af753`。未切换原 save.json。
- 可恢复快照：本 run `snapshots/world-v25.snapshot.json` 与有序四分片；按 manifest 的连续gzip流说明恢复到新路径并核 hash。不是 `WORLD_FACT_BACKUP_V1` 格式。
- 原冻结基线：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`；原 `BASELINE_HANDOFF.md` 及原run increment37 的 source-coverage、field-maturity、table-inventory、query-api-catalog仍是详细来源/成熟度入口。它们描述 v24，v25增量以本次文件及新字典为准。
- `reconnect-game` / `refresh-world auto` 继续处理 PID、创建时间、模块/layout、动态根与日期场景复核；旧地址不可复用。不存在后台自动采集任务。
- `annual-facts` 组合同年基线和唯一补录；`inspect-conflicts` 是 owner 冲突入口。普通 GM 不应拿到 owner 数据库文件。

## 后续受控执行顺序

1. Human 提供实际存档文件名、场景和变化说明。同档后续观察与独立新档分开；独立档用 init-save 建独立事实库，不能凭名字/数据相同自动关联。
2. 依据独立审核结论选择代码及新的数据库副本，显式完成迁移/绑定。原 MyLEAGUE0003 与 v24 保留，不能在旧 v24 上直接使用新年度补录。
3. 新场景先 reconnect-game auto 并复核版本、Native日期/阶段/赛季；重启只是动态连接变化，未被 Human 声明的数据更新不能臆造。保留新场景manifest和来源证据。
4. 16个普通族按实际变化采集；4个年度族普通基线仍同年一次。已存在年度基线时，由场景证据选择新事实/原缺失条目，构造 WORLD_ANNUAL_ADDITION_REQUEST_V1，再调用 capture-annual-additions。
5. 请求必须含正确save/family/year/baseline、NEW_FACT或PROVEN_OMISSION、evidence_ref及有界selectors，最多128条。honors/staff可显式选公开Native字段，默认只补新荣誉；示例格式见 REVIEW_FIXES_F01_F02_F03.md。
6. 校验 Native 目标记录、必要目录/控制和前后现场证据；真实读取成本按 collector trace 分角色记录。重复请求返回旧单元/旧时间，不能当作新采集；不同请求没有新事实也不能隐去实际读取成本。
7. 用 annual-facts 读取完整已接受年度事实。旧 native-honors/staff-history 等单元接口可能是稀疏补录；NULL不能表示原荣誉被撤销。CaptureQuarantined 后由 Human 裁决，不能重试覆盖旧事实。
8. 顺序覆盖常规赛结束、季后赛/冠军与FinalsMVP、休赛期、选秀、自由市场、跨赛季及中断恢复。仅为真实场景暴露的明确缺口另建有界工作，不能由当前测试推断场景验收。

## CLI 入口（下面是复用说明，本任务未运行游戏命令）

```text
cli.py reconnect-game SAVE_DIRECTORY MyLEAGUE0003 NEW_OUTPUT_DIRECTORY
cli.py refresh-world auto SAVE_DIRECTORY MyLEAGUE0003 NEW_OUTPUT_DIRECTORY
cli.py capture-annual-additions auto SAVE_DIRECTORY MyLEAGUE0003 REQUEST_JSON NEW_OUTPUT_DIRECTORY
cli.py annual-facts DATABASE NATIVE_HONOR_STATS 2022 --limit 100
cli.py schedule DATABASE
cli.py inspect-conflicts DATABASE
```

每次使用新的输出目录；精确参数以该版 `cli.py --help` 为准。修改测试进程内存、推进日期、写存档、人格决策、master集成不由本交接授权。
完整赛季容量、100年及保留期限按 Human 既定安排在获得完整赛季数据后处理；Overall维持延期。computer-use不使用，Gemini/Antigravity如确需批量辅助，由Human转交，不能逐任务自动委派。
