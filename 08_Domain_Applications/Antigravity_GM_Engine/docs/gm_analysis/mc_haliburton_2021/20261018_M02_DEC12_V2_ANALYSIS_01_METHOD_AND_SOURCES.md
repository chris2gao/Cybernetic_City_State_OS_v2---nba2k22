# M02 决策准备分析 — 20261018_M02_DEC12_V2_ANALYSIS_01

- 状态：`ANALYSIS_ONLY`、**PARTIAL（身份/统计语义认证待补）**。
- 已发布至 GitHub `main` 分支（分析文档）；游戏数据未修改。
- 存档：`mc_haliburton_2021`，2021–22 赛季；游戏日期：2021-12-12。
- 当前：`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`；对比：`2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`。
- 计算：GitHub 连接器读取真实发布源，以 JS 确定性计算，并用本地 Python 编排、复核、生成报告；**没有原样运行仓库 Python 脚本**。
- GM/玩家保留所有交易与教练指令裁决；本文件没有游戏写入授权。

## 数值计算与限制

- 当前球队累计来源：[M02 league.json](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/league.json)、[M02 season_totals.json](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/season_totals.json)；对照来源：[M01 league.json](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2/league.json)、[M01 season_totals.json](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2/season_totals.json)。
- 球员来源：两批各30份 `teams/<abbr>.json`，进行了全30队读取与同队人物候选比较（总计60份）。
- 教练：M02 `coaching/teams.json`、`coaching/field_dictionary.json`、`source_coverage.json`、`coaching/opponents/index.json`及全部30份 `coaching/opponents/<owner>.json`，每份29条，870条有效、mixed_fields 0。索引 owner 缩写 `NO`、`NY`、`SA`、`GS` 与 league 缩写 `NOP`、`NYK`、`SAS`、`GSW` 不同，遵循原生索引。
- 选秀权：[M01 draft_assets.json](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2/draft_assets.json)、[M02 draft_assets.json](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/published/saves/mc_haliburton_2021/batches/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/draft_assets.json)，以`asset_id`对齐并只对 `current_owner_team_id` 做差分。
- `eFG%=(made + .5*3pt_made)/attempted`；`3PA%=3pt_attempted/attempted`。
- `TOV估算占比=turnover/(attempted+.44*free_throws_attempted+turnover)`，不是经认证的原生失误率。
- `PPG=points/(w+l)`；`PA/G=pa/(w+l)`。两次战绩差分以累计胜负相减，联盟新增场次=`Σ(Δw+Δl)/2`，合计104场。
- `poss` 为原始未认证回合计数；对照估算 `attempted + .44*free_throws_attempted - offensive_rebounds + turnover`。30队原始与估算每场绝对差的均值≈0.224；即使误差小也不能证明原生守回合分母已认证，故不输出标准ORtg/DRtg/NetRtg。
- 角色供给启发式：投射 `(3pt_shot + mid_range_shot)/2`；组织 `(ball_control + passing_accuracy + passing_iq + passing_vision)/4`；侧翼 `(perimeter_defense+lateral_quickness+steal)/3`；护框 `(interior_defense+block+defensive_rebound)/3`；低位 `(shot_close+standing_dunk+post_moves)/3`。各维度≥78，且赛季场均分钟≥14才计入候选。这不是原生2K球队能力评分、也不是伤病可用性证明。
- 状态：`ANALYSIS_ONLY`。GM提案尚未作出，不能更改球员能力、游戏合同、教练设置或游戏进程。

## 重要的不可用数据/失效条件

1. **跨批稳定球员ID未认证**，无法把所有55项before-after-delta标作VERIFIED，也不能判断天赋发展由特定战术驱动。需 `DATA_SOURCE_REQUEST: PERSISTENT_PLAYER_IDENTITY`。
2. **攻守回合语义未知**，需 `DATA_SOURCE_REQUEST: POSSESSIONS_SEMANTICS`；对手`o3pa/ofga`前缀的统计含义也需确认。
3. 无完整伤病状态、球员OVR、逐场对手战术实际调用率、球员真实使用率。
4. 不可把对手`is_in_use_raw=0`解释为防守没有开启；870组未发现组内差异并不证明控制无效。
5. **写入GitHub未成功**：两次由GitHub连接器发出的`create_file`写入请求（包括极简测试文件）被平台安全检查阻断，尽管仓库权限显示`push=true`。为遵守限制，未尝试绕开安全措施；本交付仅在沙盒中生成。

## 审计/重现

报告来自该会话中的GitHub连接器查询（原始仓库的main分支）；先由JavaScript汇总球队统计、全部30队的60份名册以及870条防守，再将聚合结果录入本地Python、检验30队唯一性和新增104场并生成Markdown/JSON。**此交付非全量原始文件镜像，也非仓库原生 gm_prepare.py 执行**。历史原始数据未改动。