# DEV29 R03-A 研究断点补充 — 2026-10-21

> **状态：`R03_A_PUBLISHED_WITH_OPEN_ITEMS / TASK_CLOSED`；下一轮：`R03_B_INJURY_FATIGUE_RECOVERY_MENTOR_RESEARCH`。** R01/R02公开研究维持已结案状态。本文件是针对`PROGRESS.md`本轮写入受阻的**显式增量状态补充**，不是假称那个原文件已被更新；未来正常可写时应将本文件内容并入正式PROGRESS后再撤销重复指针。

## 本轮正式发表

- [K06训练、健康与自然成长中文攻略](guides/K06_TRAINING_HEALTH_GROWTH.md) §§0–8。
- [11类训练与角色自由选择研究目录](catalogs/K06_TRAINING_ROLE_INPUTS_RESEARCH_V1.json)，只描述可观察事实、可讨论选择、引擎效果等级与审批界限，不是Agent或执行schema。
- [SOURCES](SOURCES.md)新增`SRC-0049..0059`，含2K22官方、同年代社区与更早Visual Concepts开发人员对负荷的原始解释。
- [VIS](visuals/EXTERNAL_VISUALS.md)新增`VIS-0009/0010`，两张已看过实际像素的2K22官方**次世代MyNBA**训练截图；并非PC MyLEAGUE原生菜单认证。

## 已有工程事实与未知

项目静态训练字典`config/state_io_native/training.json`和Registry注册了6个Team Training、5个Player Training控制字段，以及9种通用培训原型；导师关系只登记DISCOVERED候选。历史疲劳结构的字节布局已经存在，但**没有证据表明该字段已被本轮捕获为有单位、有时间点的实时疲劳值**。R01每场Box和伤病可用性的PC原生完整查询仍有缺口。不能从字段已注册推断当前档有合法的当前健康观察结果，也不意味着允许直接改Ability/Potential/Badge。

## 用户新增跨世代机制解释权重

玩家明确校正：NBA2K22次世代和本世代**终极联盟大多数经营机制、选择和反馈高度可复用**；更大差异主要在物理比赛引擎。故下一轮应**积极借助2K22次世代MyNBA训练资料解释机制和可选行为**，而不是整体排除。同时将`concept/behavior transferability`与`PC22 exact UI/native enum/runtime capture`分为两个证据轴；有明确专属版本的Prep Hub UI/岗位、未经过验证的字段与效果不能凭类比声明PC本世代已实现。

## 下一轮R03-B唯一任务入口

从本检查点、[K06](guides/K06_TRAINING_HEALTH_GROWTH.md)、[SOURCES](SOURCES.md)、[VIS](visuals/EXTERNAL_VISUALS.md)和DEV29 V3启动：重点研究**真实疲劳（历史vs当前）、伤病类型/伤愈、Durability、训练师与导师、训练与比赛自然成长差分、受伤球员与教练/GM的可选冲突**。将观察事实、原生合法选择、外部角色想法和真实游戏反馈分开；可沿用跨世代机制材料，但注明PC具体原生事实等级。创建K06增量、来源、图证和研究断点；无须重复R03-A的Prep Hub全文。R04完整球员字段与Agent自主研究独立等待排期。

**边界**：本轮没有调用DEV28、Codex、游戏内存采集、游戏模拟、存档或球员能力写入。角色拒绝/谈判属于未来独立人格模型的行为原料，不是现有2K22原生API。
