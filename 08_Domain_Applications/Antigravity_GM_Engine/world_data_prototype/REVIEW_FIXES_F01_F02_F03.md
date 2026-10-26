# 独立审核 F-01 / F-02 / F-03 定点修复候选

Human 授权日期：2026-10-26。新任务 `nba2k22-world-data-review-fixes-01`；
分支 `task/nba2k22-world-data-review-fixes-20261026`，精确起点 `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`。
原常规赛持续施工任务保持结束。本候选只修复三项 finding，完成后交独立审核，不合并 master。
证据目录：`01_os/07_content/_runs/run-20261026-nba2k22-world-data-review-fixes-001/`。

## F-01：年度一次基线与有证据的追加

Schema v25 为 **101表 / 1,789列**。保留 `annual_refresh_once`，只允许每存档/Native赛季年/来源族一次成功 LIVE_READ `BASELINE`。
`ADDITION` 必须锚定同一存档、来源族和年度的成功 LIVE_READ 基线，带请求身份及实际补录控制 artifact 哈希。
普通年度 refresh 仍会跳过已完成的基线，不自动重扫旧历史，也不自动发现所有未来事实。

`annual_fact_claims` 仅保存幂等身份、hash及 typed 表/行/列指针，**不存业务值**。
Native 行观察、原生荣誉字段、明确指定的其他原生字段和 canonical 奖项事实保留各自证明范围。
荣誉补录只保存新字段，旧MVP、旧计数不会因新增冠军/FinalsMVP而被重复保存；NULL 表示本补录未存该字段，完整已知事实通过基线及各自原始来源时间读取。
新发现的完整来源行可追加一次；已知行的非荣誉字段须在请求 `fields` 中明确选择，只有新的值或原先缺失的值才追加，零值也按实际值处理。
已登记正荣誉值的更改/撤回、canonical 冻结奖项的不同内容进入 F-03 隔离，不自动覆盖。
原生 flags 仍不是已确认的最终奖项/人物归属；历史人物、共享记录及分配生命周期未被本任务自动证明。
幂等使用已有来源作用域内的记录/字段键，以及canonical事实的稳定键；不凭同名或不同来源槽位推断同一历史人物/奖项。

新增命令：

```text
capture-annual-additions PID_OR_AUTO SAVE_DIRECTORY LOADED_FILENAME REQUEST_JSON NEW_OUTPUT_DIRECTORY
annual-facts DATABASE FAMILY PERIOD_YEAR [--limit 100] [--cursor-json JSON] [--as-of TIMESTAMP]
```

四个既有年度 Reader 也接受 `addition_request=REQUEST_JSON`：`capture_records`、`capture_native_honors`、
`capture_league(..., mode='HISTORY_AWARDS')`、`capture_staff_history`。
请求示例中的索引和基线ID是占位说明，须由后续场景任务根据真实来源选择，不能照抄为当前游戏地址：

```json
{
  "format": "WORLD_ANNUAL_ADDITION_REQUEST_V1",
  "save_id": "nba2k22_test_01",
  "family": "NATIVE_HONOR_STATS",
  "period_year": 2022,
  "baseline_unit_id": "EXACT_EXISTING_ANNUAL_BASELINE_UNIT",
  "reason": "NEW_FACT",
  "evidence_ref": "scene-manifest-and-observed-new-award-evidence",
  "expected_game_year": 2022,
  "selectors": {"indices": [123]}
}
```

`reason` 仅 NEW_FACT / PROVEN_OMISSION。证据引用记录发现依据，本身不替代 Native 证明；接入还须核对真实字节、布局、前后场景和已知事实。
每请求最多128条来源记录。records/honors/staff 使用 `indices`；league 使用 `history_indices` 和 `matrix_slots: [[award0..14, recipient0..4]]`。
荣誉/教练统计可选 `fields: ["points_raw"]` 等本族公开原生列；其他表、隐藏列和任意地址不是选择器。
可选 `expected_period_raw` 绑定明确的 Native 观察阶段。补录桶年与观察现场年分别保留；不把观察阶段自动当作累计统计 phase。

Native 读取策略：只读取所选完整记录及必要控制；教练另读有界引用/UID目录，计算当前共享引用数，名称仅取相关主体。
不调用原年度全量 collector；目录/摘要、目标记录、复读一致性控制和完整 ReadProcessMemory trace 分别记录成本。
已成功的相同请求可直接返回旧单元及旧时间，明确 `fresh_native_capture=false`；不同请求读到相同已知事实也不会再入库，但会如实保留这次读取成本。
SQLite 幂等索引不是 Native 读取优化的证据；目标读取策略与受控字节读取测试另有记录。
league 的部分历史/矩阵补录不证明完整获奖组，保留原生行而不伪造 canonical 完整收奖人列表。

`annual-facts` 按固定观察范围组合基线和唯一补录，逐项保留源时间/grade。`NATIVE_HONOR_FLAG`、`NATIVE_FIELD_VALUE`、`SOURCE_ROW_OR_CANONICAL_FACT` 分开表达。
既有 `native-honors`、`staff-history` 等仍是单观察单元接口；补录可能是稀疏子集，完整已知年度事实应使用新接口，不能把最新单元的 NULL 当作原事实消失。

## F-02：赛程与单场 Box 共用严格判定

`strict_box_coverage` 同时服务 `schedule` 和 `game_box_snapshot`，验证同一单元内的球队、参与者ID、非NULL得分、Native身份状态及逐人得分一致。
两者按UTC/微秒选择同一最新 Box 单元，较新的部分单元不会借用旧完整数据。
赛程状态仍保留其最后实际观察的 `unit_id/observed_at`；Box 另有 `box_unit_id/box_observed_at/box_source_grade`，避免仅有新部分Box时丢掉旧的可靠比赛状态或混淆来源时间。
人数相同但人物不同、任一点数NULL、Native与Canonical得分不同均不完整；不可靠派生分数保持NULL。
此判定只证明捕获窗口的一致性，不宣称全部历史人物生命周期或UI已验收。

## F-03：保留合法 receipt 的独立冲突隔离

`ingest_or_quarantine(..., _live_receipt=...)` 验证原始提议receipt，失败的领域写入回滚后独立登记提议digest、对象、错误、原来源和 artifact 引用。
不为改写后的payload伪造receipt，不降低LIVE_READ等级。隔离单元采用 `quarantine:` 命名，不能消费年度基线桶，也没有原提议领域事实。
20个真实采集入口使用 `ingest_acquired_capture`；隔离后抛出 `CaptureQuarantined`，避免把冲突当作成功采集。
Owner 可用 `inspect-conflicts DATABASE [--proposed-unit-id ID]` 查询；普通 GM history/export 仍拒绝该表。
测试采用独立数据库和受控适配器，属于receipt契约验证，不代表本任务读取了真实游戏。

## 原 v24、升级与下一任务

原 `nba2k22_test_01/world-v24.sqlite`、原绑定和游戏文件均保留。升级只向新文件复制；旧100表每个原行/原列逐值比对，
只排除明确变化的版本头，并单独验证14条新字段目录登记及新增幂等索引，不放宽旧事实检查。
v24 仍可用冻结旧代码读取；v25 的年度补录需先显式复制升级，不会就地改写旧库。
本任务的 final v25 副本、快照和正式完成指针以该新run的最终证据为准。

下一独立任务才接入 Human 提供的全生命周期场景，产生具体补录请求并复用现成 Reader、重启重连和增量基础设施。
本任务不新增自动场景发现、不操作游戏、不研究Overall、不做人格决策或容量压测；独立审核及master接入另行办理。
