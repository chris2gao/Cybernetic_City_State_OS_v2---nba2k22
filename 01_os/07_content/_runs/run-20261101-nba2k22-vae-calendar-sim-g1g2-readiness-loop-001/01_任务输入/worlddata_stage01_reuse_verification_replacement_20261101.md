# Human 更正：取代旧 B1–B3 整改指令 · 先复核并直接复用 WorldData 第一阶段

## 生效性
- 当前任务：`NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`
- 开发分支：`task/nba2k22-vae-calendar-sim-g1g2-readiness-loop-20261101`
- **替代且废止**：`01_任务输入/final_three_data_integrity_blockers_20261101.md` 及由该文件产生的旧 Gemini 继续执行提示词。不可按旧 B1–B3 作为必修整改清单执行。
- **原因**：Human 确认 INCREMENTAL 无新完赛比赛时跳过可接受；第一阶段已实施精细的同采集单元与时间控制，必须先查已存在的代码、测试及实际库，再决定是否有新增VAE接口的缺口。
- 此更正不取消当前分支此前已经完成的 R1–R7 工作成果；不创建新任务，不更换分支，不授权游戏操作或 master 合并。

## 已由规划总线核实的 WorldData 第一阶段事实

基准工程固定 SHA：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`，目录：
`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/`。

1. `competition_views.py:game_box_snapshot(path, game_id, unit_id=None)` **先选单个合法的采集单元**，然后所有 game state/period scores/player boxes/team boxes 均按 `game_id AND unit_id`读取。返回 `selected_unit_id`、`capture`、`observation_units`、双方 Native 参与者完整性与得分资格。后来的 header 单元仅作为 `latest_header_check`，不把旧 Box 的时间刷新为当前。
2. `query.py:game_box()` 直接复用 `game_box_snapshot()`；`query.py:schedule()` 通过 `box.unit_id=s.unit_id`及 Native 参与者数量检查，限制不合格计分；各类 current state 查询有各自合适的快照逻辑。
3. `observation_scope.py` 提供 `observed_as_of`、成功采集单元集合、`query_connection`、`query_at`、观察范围指纹和限定分页等。历史时间是**采集时间，不是游戏日期**。不同来源族在`refresh-world`中独立原子采集，本来就不是全球同时刻快照；不应要求一整次20族来源共享一个`unit_id`。
4. `tests/test_incremental_schedule.py` 含 `test_header_reuse_does_not_refresh_box_source_time_or_mix_units`、`test_cache_requires_live_complete_mapping_and_never_falls_back_from_new_partial`、`test_research_fixture_is_not_a_live_frozen_cache`、`test_reuse_wrong_hash_or_other_game_is_rejected_atomically`。
5. `tests/test_observation_scope.py` 覆盖历史 cutoff、成功单元集合、部分字段不同时间、失败单元不可见、同时间分页、跨库保护、回填后分页失效。
6. `tests/test_refresh.py` 覆盖20族有序注册、单来源已提交回执、年频跳过、部分失败、恢复与进程重启不丢来源证据。
7. 第一阶段 `BASELINE_HANDOFF.md` 和 `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment37/` 的 `verification-report.json`、`source-coverage.json`、`table-inventory.json` 给出了实际库/来源证据（v24、100 STRICT表、1,775列、20族Reader，301项原回归测试）；这些是常规赛工程候选而不是对所有Native字段的最终认证。

## Gemini 继续执行的次序

**Step 1 / 原架构实证**：回读固定SHA及当前开发分支中上述函数的实际版本，整理一页“原系统已负责什么—当前VAE新导出实现什么—是否已复用—剩余真实接口差距”对照。不要仅凭新CTE结构不同就宣判架构错误。

**Step 2 / 第一阶段已生成数据库的只读复核**：如果Gemini当前本地环境存在该历史库，优先只读打开：
`01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/_runtime/world-saves/nba2k22_test_01/world-v24.sqlite`
并核验本地`save.json`/schema、采集单元、`game_source_checks`、历史重复游戏、冻结Box复用及`game_box_snapshot`结果；记录来自现有历史数据的实际GameID、source unit、observed_at、completeness与来源等级（公开报告脱敏，不上传私有原始存档）。只读DB或在临时副本运行负例；不得原位写改历史库。若该库在当前环境不存在，则用第一阶段已经发布的字段/表/来源报告及其原测试fixtures验证，明确`HISTORICAL_LOCAL_DB_NOT_AVAILABLE`，无需为了普通SQL查询使用GPT的RDC。

**Step 3 / 当前VAE导出对照**：目前`calendar_sim_orchestrator.py:export_vae_standard_datasets`有比赛state、球队Box和球员Box各自独立`ROW_NUMBER`选择的实现。检查与第一阶段`game_box_snapshot`、`schedule`和`observation_scope`相比，在真实历史重复采集/源回用/部分单元下，是否产生可复现的“混单元误输出”或错误状态。若确有差距，**优先通过调用已有稳定查询API/明确unit pin/最薄适配来复用已有规则**，不另起通用采集/时间一致性框架；若现有接口已等价安全，保留原代码并用证据说明，不强制修改。

**Step 4 / 就绪等级最小核对**：检查VAE新`manifest`的`CURRENT_NATIVE_READ`、`SQL_INGEST`、`STANDARD_DATASET_EXPORTED`和`POST_CALENDAR_NEW_GAME_VERIFIED`是否来自本次实际选中的成功source units，而非全库中其他来源曾经有过`LIVE_READ`。若原有来源等级/历史语义已经可以直接复用，使用原API即可；不要改造已验证的底层结构。只在实际错误有测试证据时做定点修正。

**Step 5 / 轻量定点回归**：复用第一阶段测试及新VAE测试，对“完整同源比赛、冻结Box回用、较晚部分单元、多个来源时间、研究Fixture、历史库实际只读查询”进行少量高价值验证，记录实际PASS/FAIL与修复SHA。不人为制造新审核轮次或大批次低价值测试。

## Human 本次正式裁决

- **INCREMENTAL 没有新增已完赛比赛时跳过可接受**。不再以此为P0，不能为了旧提示词强制修改现有分支。Human正常要求全量采集时仍使用已经实现的`FULL`及第一阶段`refresh-world`；未来如有独立非比赛状态采集需求再决定触发机制。
- **第一阶段有权威的同源时间抽象**。VAE必须沿用，不能把新开发中“独立各取最新”当成更正确的第二套查询架构。
- **针对真实错误才修复**。若经过历史实库/测试证明无问题，可以直接确认继承；若新VAE导出没有复用旧规则，做最小查询适配并保留旧历史原样。
- 全部工作保持开发阶段内部Loop；不启动游戏、不改存档/球员/教练设置、不推进日历、不调用RDC作普通SQL/Git检查、不合并master。
- 不改变G1/G2长期目标：Human一键触发全量采集，自动写入现有单档SQLite，并通过固定VAE数据提取为Calendar Sim实验提供规范化数据；真实新增比赛与设置效果仍需将来用户触发才可验收。

交付简明复核记录、必要的最小修复与专项回归、最终SHA、实际剩余缺口。**禁止仅凭旧 B1–B3 清单盲目改代码。**
