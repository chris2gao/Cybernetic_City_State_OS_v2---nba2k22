# NBA2K22 阶段02 · S1 比赛 Box／身份严格性与根因核销 v1

> **状态：STATIC_CODE_AND_ARCHIVED_EVIDENCE_PARTIALLY_SUPPORTED; PER_GAME_CAUSE_UNKNOWN**  
> 研究问题：RQ-02-01 / RQ-02-02 / RQ-02-03；结果需求：RES-01 / RES-02 / RES-04 / RES-06。  
> 日期：2026-10-27。工程代码固定 `a3927fb150a213201e404cca043ced4f57409bd1`；阶段01 Human 精确批准 `A-v1-RC01`。  
> 此文只做GitHub只读源码与历史证据核对；**未运行Windows、未访问SQLite原件、未连接游戏、未执行测试、不改变 v25 工程结论或阶段02总门**。

## 1. 追溯链（工程一手材料）

| 证据 | 固定Git Blob SHA | 已证范围 |
|---|---|---|
| `world_data_prototype/competition_views.py` | `e75a87fa43183c1f7a38c978099886052c9df97e` | 第16–43行 `strict_box_coverage`；45–70行 `game_box_snapshot` |
| `world_data_prototype/query.py` | `54e70472088a65b9a92e107dc11dcae8a2451b4c` | 第588–641行 `schedule` 与同一严格覆盖谓词 |
| `world_data_prototype/schedule_reader.py` | `d48ce685bb861fa5ddce6ca236a3633f8a05142d` | 第41–95行原生窗口读取/重读；第133–171行typed事实；第174–190行冻结源；第193–215行增量绑定/重采 |
| `world_data_prototype/live_world.py` | `dab24dd38a67cc45c8cdbac4f584fbda414ded47` | 第101–188行Native-ID→当前PLAYER池唯一候选；第275–295行Native Box保留与canonical映射/显式缺口 |
| `world_data_prototype/tests/test_review_box_completeness.py` | `1e5325de6aed9b08ba4dfe77fd4bcf05dfa51603` | 7个F-02定点fixture测试的方法与断言存在；本轮未执行 |
| `world_data_prototype/tests/test_competition_views.py` | `311062d2fa7b77ea4aeee819ca9818da37f6992a` | 测试跨单元禁止混拼、缺失/错误身份、得分缺口、不可推算零分 |
| `world_data_prototype/tests/test_incremental_schedule.py` | `84c6c8763ccedf88bf5056268e85b1ef2cf5047d` | 第57–85行冻结复用、变更重采与部分单元不得覆盖旧完整证据 |
| `world_data_prototype/REVIEW_FIXES_F01_F02_F03.md` | `60bd163d00afa417c1236b20d7cccceb85a2c249` | F-02设计边界；既有原作者修复说明非独立运行复现 |

相对工程文件根路径均为 `08_Domain_Applications/Antigravity_GM_Engine/`；历史证据位于相应OS Run。两份不同源码互相调用仍属于**同一个项目开发来源**，不冒充双独立实机证据。

## 2. 具体严格判定是什么

`strict_box_coverage` 在选择的单一 `unit_id` 内，按HOME/AWAY分别确认：

1. 至少存在真实Native观测及活动参与者；
2. 活动Native行与canonical行数量一致、所有canonical `in_use` 有效，Native与球队目录 ID 对齐；
3. Native球员ID去重、与canonical球员实际Native ID逐人逐分成对完全一致，活动行身份状态为 `CURRENT_CONTEXT_RESOLVED`；
4. 双侧Canonical和Native活动行得分均非NULL，且各侧总和一致。

仅两侧同时达到 `ALL_CAPTURED_NATIVE_PARTICIPANTS_RESOLVED`，`schedule()` 才能给出 `canonical_box_complete=1` 与派生两队得分。若不满足，来源内可接受的Native/业务观察照实存在，但**不得伪造完整canonical比分**；当前接口也有原始游戏状态分数与qualified派生分数的来源区分。

`game_box_snapshot` 从同一个最新成功采集单元返回 `states`、`period_scores`、`player_boxes`、`team_boxes`；旧单元仍可指定 `--unit-id` 历史查看。最新header检查单独显示而不刷新原Box观察时点。新版部分Box不会向旧单元借球员/分数字段拼接看似完整的Box。

**当前身份解析的显式范围**是已读取的当前Native PLAYER池及确切目标Native ID：`live_world.collect_world` 对匹配多个候选、无有效名字或必要队伍/统计控制的主体拒绝强合并；`schedule_facts` 保存所有已捕获Native Box观测，只有按当前上下文确认的主体进入canonical `player_game_boxes`。并不证明退役、历史、跨赛季原生ID稳定。

## 3. 第6、第10场的已见事实与证据不足

`01_os/07_content/_runs/run-20261026-nba2k22-world-data-review-fixes-001/evidence/real-copy-query-audit.json`（Blob `3fa3e32b27021293f88737bfe4489f83448787ae`）在历史v25副本抽样的12场中：
- `season:native-year:2022:game:6` 的 `canonical_box_complete=false`，`box_unit_id=live-world:62052310fffb4ca792946781`；
- `season:native-year:2022:game:10` 同上；
- 其他10场为true。

固定 `increment37/source-coverage.json`（Blob `46d43f0e827030ecc7c20df4390dfb4a16d4f33f`）记载该 `unit_id` 是2026-10-25T18:56:18.428726+00:00的 `BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS`，标签 `LIVE_READ/PARTIAL`，其全单元日志有930 Native Box、893 canonical player Box、1232条game_source_checks。这是跨该单元所有比赛的数量，不是上述两场的人数或逐人对应。不能把930−893直接解释成37个真实缺失球员。

**该历史unit仅登记的本地缺口含 `CURRENT_SEASON_SCOPE`，未列明这两场的逐侧严格谓词失败。** 其他历史单元登记过 `UNRESOLVED_BOX_PLAYER_IDS`，说明身份不明属于已知的一类问题；但**不得据此认定game:6、game:10就是该问题**。

`real-copy-query-audit.json` 不包含逐侧 `box_coverage` 字段、Native/canonical原始行、`game_state`及header的相关状态。因此目前没有证据区分以下原因：更晚单元覆盖旧完整单元、未赛/不适用状态、活动参与者缺失、Team/Player ID不符、得分NULL或Native/Canonical逐人分数不一致，以及其它表级或读源问题。

**当前子结论**：严格覆盖和隔离逻辑有明确的候选代码及fixture测试；第6、10场未通过严格完整判定是历史开发报告事实；具体原因与是否真实工程缺陷 `UNKNOWN`。不需要重建整个Reader或新增Box表的证据尚未出现，但也不宣称现有场景已通过验收。

## 4. 最小化后续实证（当前只定义，不执行）

### A. 如Human允许独立模型使用隔离的v25 SQLite副本

优先**无需游戏进程**、不写数据库执行：
1. 对上述两个 `game_id` 在固定v25副本运行现有只读 `game DB GAME_ID --unit-id UNIT_ID`、`schedule DB ...`（仅使用实际CLI已支持的参数）；保存完整返回值，尤其是每侧 `coverage`、`selected_unit_id`、`observation_units`、`latest_header_check`、`score_provenance` 和 `is_final`，以及实际退出码/环境SHA。
2. 用受控只读SQL逐侧计算该unit活动Native条数、canonical条数、唯一ID对照、Team ID、各项points NULL和得分差异；检查同一game更早成功 `unit_id` 是否曾是完整且合格的冻结源。
3. 将上述具体谓词结果归类为 `NOT_FINAL_OR_NOT_APPLICABLE`、`LATEST_PARTIAL_OBSERVATION`、`UNRESOLVED_CURRENT_IDENTITY`、`TEAM_OR_POINTS_MISMATCH`、`MISSING_NATIVE_WINDOW`、`SCHEMA_OR_QUERY_DEFECT_CONFIRMED` 等，不允许直接将布尔false写成bug。
4. 验证所有原始比赛事实与以前成功单元未被修改；若需要新的Native来源才可判定，标 `SCENE_PROOF_REQUIRED`。

仅授权临时/隔离副本，不接触原MyLEAGUE档案或正式world.sqlite；能否实际执行需Human另行批准现有已准备Windows独立复核任务。

### B. 如果SQLite副本仍不能判定

待Human将专用游戏存档置于S1并明确**只读Native**授权后，才按现有 `schedule_reader`、`game_source_checks` 与PLAYER身份源进行小范围对照：对应game状态与时间、两队Native Box参与者、合法人员身份、是否为新出现的比赛记录、采集对象绑定。不得改变比赛进度/日期，也不在未授权情况下执行 `--recheck-frozen` 或连接进程。

## 5. 阶段02对结果B的实际约束／停止判断

- **可以复用的候选**：`games`、`game_state_observations`、`game_period_scores`、`team_game_boxes`、`player_game_boxes`、`native_box_observations`、`game_source_checks`、采集单元历史、统一 `strict_box_coverage`、`frozen_game_sources`、只读查询。
- **不得提前设计的新增工程**：新的Box数据库容器、另一套赛程/Box评分、按姓名强制映射历史球员、跨unit混拼状态、强制把Game6/10改标完整；只有经过按谓词实证形成的具体失败才允许成为 `CONFIRMED_DELTA`。
- **不影响阶段03结构讨论的前置未知**：两场历史样本的exact failure reason可以先列入有界实机/副本复核；但 `game_id`/season/当前Native球员身份的最终时间有效性不可假定已证。
- **RQ-02-01=S1子项状态**：`STATICALLY_SUPPORTED_WITH_BOUNDED_RUNTIME_UNKNOWN`；`RQ-02-02`整体仍 `PARTIAL_STATIC_VERIFIED_RUNTIME_NOT_REPLAYED`；`RQ-02-03`关于跨会话身份稳定仍待证。
- **EIG停止条件**：当前GitHub静态代码与现有审计未保存更细的逐队谓词证据。再次宽泛扫描同一文件难以确定原因；下一项最有信息增益的取证是读取隔离v25副本的现有 `game_box`覆盖返回；若无访问权限，则记录 `BLOCKED_NOT_ACCESSIBLE`，并继续其他可凭仓库核销的S4/S6/S7事项。
- **阶段02总体**：`stage02_evidence_verdict=NOT_ASSESSED`；没有Windows、实机、Writer、schema设计或master发布授权。RR-05B=D，仅未来获授权实时内存写后新采集入库与清单对账，**不要求Save/Reload**。
