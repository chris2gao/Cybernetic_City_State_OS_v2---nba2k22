# M02 决策准备分析 — 20261018_M02_DEC12_V2_ANALYSIS_01

- 状态：`ANALYSIS_ONLY`、**PARTIAL（身份/统计语义认证待补）**。
- 已发布至 GitHub `main` 分支（分析文档）；游戏数据未修改。
- 存档：`mc_haliburton_2021`，2021–22 赛季；游戏日期：2021-12-12。
- 当前：`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`；对比：`2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`。
- 计算：GitHub 连接器读取真实发布源，以 JS 确定性计算，并用本地 Python 编排、复核、生成报告；**没有原样运行仓库 Python 脚本**。
- GM/玩家保留所有交易与教练指令裁决；本文件没有游戏写入授权。

## 一、战绩与工资精确快照差分

| 球队 | M01 | M02 | 区间战绩 | 名单人数 M01→M02 | 球队 total_salary 变化 |
|---|---|---|---|---|---:|
| PHI | 16-3 | 20-6 | 4-3 | 16→16 | +0 |
| MIL | 11-8 | 14-12 | 3-4 | 15→15 | +0 |
| WAS | 10-8 | 17-9 | 7-1 | 16→16 | +0 |
| CHI | 11-8 | 15-11 | 4-3 | 16→15 | +4,443,840 |
| CLE | 6-13 | 9-17 | 3-4 | 16→16 | +0 |
| BOS | 10-9 | 13-13 | 3-4 | 15→15 | +0 |
| LAC | 8-10 | 11-15 | 3-5 | 17→17 | +0 |
| MEM | 10-8 | 14-12 | 4-4 | 16→16 | +0 |
| ATL | 11-8 | 12-13 | 1-5 | 16→16 | +0 |
| MIA | 13-6 | 16-10 | 3-4 | 15→15 | +0 |
| NOP | 10-10 | 13-14 | 3-4 | 15→15 | +0 |
| UTA | 5-13 | 9-16 | 4-3 | 16→16 | +0 |
| SAC | 14-5 | 20-6 | 6-1 | 16→16 | -2,254,380 |
| NYK | 11-7 | 16-9 | 5-2 | 15→15 | +0 |
| LAL | 15-5 | 18-8 | 3-3 | 14→14 | +0 |
| ORL | 5-14 | 7-19 | 2-5 | 16→16 | +0 |
| DAL | 9-8 | 10-15 | 1-7 | 15→15 | +1,650,000 |
| BKN | 14-5 | 17-8 | 3-3 | 15→15 | +0 |
| DEN | 8-10 | 11-14 | 3-4 | 16→16 | +0 |
| IND | 7-13 | 10-18 | 3-5 | 14→14 | +2,254,380 |
| DET | 2-16 | 5-19 | 3-3 | 14→15 | -4,443,840 |
| TOR | 7-12 | 11-14 | 4-2 | 15→15 | +0 |
| HOU | 8-10 | 13-11 | 5-1 | 17→17 | -1,650,000 |
| OKC | 4-14 | 6-18 | 2-4 | 16→16 | +0 |
| SAS | 8-9 | 10-14 | 2-5 | 15→15 | +0 |
| PHX | 10-8 | 14-10 | 4-2 | 16→16 | +0 |
| MIN | 8-10 | 11-14 | 3-4 | 15→15 | +0 |
| POR | 12-7 | 17-9 | 5-2 | 16→16 | +0 |
| GSW | 9-9 | 13-12 | 4-3 | 17→17 | +0 |
| CHA | 7-13 | 11-17 | 4-4 | 15→15 | +0 |

## 二、逐球员55项/潜力

**未达到VERIFIED_STABLE身份门槛**：当前来源只有姓名、DOB、Face ID及模型内pool_slot等，无法证明跨批永久人物唯一键。球队内的候选变化记录只能用`HIGH_CONFIDENCE_TEMPORAL_CANDIDATE`理解，不能称为已确认自然成长、已确认回退或教练带来的成长。本交付包含各队有变化的候选人数摘要，但**未完整导出所有候选人物逐项55字段的 before/after/delta**，需要后续可信批次分析补齐。

| 球队 | 同队唯一人物候选中发生非零属性变化的人数 | 身份状态 |
|---|---:|---|
| PHI | 7 | PROVISIONAL（未经永久人物认证） |
| MIL | 2 | PROVISIONAL（未经永久人物认证） |
| WAS | 6 | PROVISIONAL（未经永久人物认证） |
| CHI | 5 | PROVISIONAL（未经永久人物认证） |
| CLE | 3 | PROVISIONAL（未经永久人物认证） |
| BOS | 2 | PROVISIONAL（未经永久人物认证） |
| LAC | 5 | PROVISIONAL（未经永久人物认证） |
| MEM | 6 | PROVISIONAL（未经永久人物认证） |
| ATL | 11 | PROVISIONAL（未经永久人物认证） |
| MIA | 7 | PROVISIONAL（未经永久人物认证） |
| NOP | 6 | PROVISIONAL（未经永久人物认证） |
| UTA | 8 | PROVISIONAL（未经永久人物认证） |
| SAC | 4 | PROVISIONAL（未经永久人物认证） |
| NYK | 7 | PROVISIONAL（未经永久人物认证） |
| LAL | 7 | PROVISIONAL（未经永久人物认证） |
| ORL | 6 | PROVISIONAL（未经永久人物认证） |
| DAL | 5 | PROVISIONAL（未经永久人物认证） |
| BKN | 5 | PROVISIONAL（未经永久人物认证） |
| DEN | 5 | PROVISIONAL（未经永久人物认证） |
| IND | 2 | PROVISIONAL（未经永久人物认证） |
| DET | 5 | PROVISIONAL（未经永久人物认证） |
| TOR | 6 | PROVISIONAL（未经永久人物认证） |
| HOU | 11 | PROVISIONAL（未经永久人物认证） |
| OKC | 8 | PROVISIONAL（未经永久人物认证） |
| SAS | 9 | PROVISIONAL（未经永久人物认证） |
| PHX | 3 | PROVISIONAL（未经永久人物认证） |
| MIN | 4 | PROVISIONAL（未经永久人物认证） |
| POR | 9 | PROVISIONAL（未经永久人物认证） |
| GSW | 6 | PROVISIONAL（未经永久人物认证） |
| CHA | 7 | PROVISIONAL（未经永久人物认证） |

本次已检查的同队姓名+DOB+FaceID唯一候选潜力变化均为0；该描述**不是全联盟跨队潜力稳定证明**。不可把已转队/特殊MC双记录合并。

## 三、跨队名单人物候选变动（不是已认证交易回执）

| 人物记录名 | M01所属队 | M02所属队 | 身份级别 |
|---|---|---|---|
| Jerami Grant | DET | CHI | PROVISIONAL 名称迁移 |
| Coby White | CHI | DET | PROVISIONAL 名称迁移 |
| Derrick Jones Jr. | CHI | DET | PROVISIONAL 名称迁移 |
| Domantas Sabonis | IND | SAC | PROVISIONAL 名称迁移 |
| Justin Holiday | IND | SAC | PROVISIONAL 名称迁移 |
| Tyrese Haliburton | SAC | IND | PROVISIONAL 名称迁移 |
| Ty Hali | SAC | IND | PROVISIONAL 名称迁移 |
| Brandon Clarke | MEM | IND | PROVISIONAL 名称迁移 |
| Malcolm Brogdon | IND | MEM | PROVISIONAL 名称迁移 |
| David Nwaba | HOU | DAL | PROVISIONAL 名称迁移 |
| Sterling Brown | DAL | HOU | PROVISIONAL 名称迁移 |

## 四、选秀权持有权变动（基于经验证资产ID和current_owner字段）

| asset_id | M01当前持有队ID | M02当前持有队ID |
|---|---:|---:|
| `draft_pick:2022:1:28` | 3 | 21 |
| `draft_pick:2022:1:20` | 20 | 13 |
| `draft_pick:2022:2:10` | 20 | 13 |
| `draft_pick:2022:2:17` | 17 | 23 |
| `draft_pick:2024:2:17` | 17 | 23 |

说明：选秀权仅报告持有变化，不能在无回执的情况下推断具体交换对价；工资变化也不能被解释为签约或现金扣款。