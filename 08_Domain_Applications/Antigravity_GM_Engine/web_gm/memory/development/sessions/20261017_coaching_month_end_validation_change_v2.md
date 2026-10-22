# DEV-20261017-05：开发完成后由玩家进行一个游戏月的验证（规则变更V2）

- 真实日期：2026-10-17
- 角色：WEB_GPT_DEVELOPMENT
- 状态：SPEC_UPDATED_IMPLEMENT_WHEN_MEMORY_FEASIBLE / PLAYER_MONTH_TEST_PENDING / NO_FORMAL_GAME_WRITE
- 主任务书：[docs/development_tasks/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md](../../../../docs/development_tasks/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md)
- V2技术任务书变更提交：`08d013ef52e98849cdaecd5e9699906c0aebec18`、`d5702d759a14285b76def883b7ff2306ff345b3a`。

## 最新玩家要求（覆盖旧调研方案）
原Codex P0 要做快速模拟20/100场对照实验并依据效果再开发；**现改为Codex确认UI↔内存映射、合法枚举、隔离存档最小安全读写与保存持久性后，直接继续实现GM战术功能，Codex不做批量比赛效果验证**。开发完成后玩家在真实NBA2K22存档中推进一个游戏月，然后由玩家分开触发真实比赛来源采集→Web GPT ANALYTICS量化报告→GM评估。Codex仍要做必要的代码单测与读写安全检查，但不必先实证胜率变化才能研发。
这些允许的研发动作并非授权修改正式存档；具体球队战术更改仍须GM提案和玩家批准，再交受控执行端。

## 反馈观测逻辑
- 在实际批准执行战术之前保留同存档同赛季冻结批次、球队状态与策略前值；执行回执记录生效时间。
- 月末再次采集同口径的赛季累计 `W/L` 与可用球队技术统计总量，计算 `ΔW`、`ΔL`、`ΔG` 和对应月度分布；赛季场均的两个值不可直接相减。
- 一月的变化受赛程、阵容交易、伤病等混杂，属于初步观察，不等于严格因果证明；无采集数据则不能臆测效果。
- 实际快模拟效果及AI比赛过程是否覆盖，等待玩家真实游戏月的验证；未测统一标`SIM_EFFECT_PENDING_PLAYER_MONTH`。

## 更新范围
仅修改本项目 V2 Codex 任务书和研发记忆/历史评估指向，不修改球队状态、球员能力、生产源码、游戏存档或`published/`。
