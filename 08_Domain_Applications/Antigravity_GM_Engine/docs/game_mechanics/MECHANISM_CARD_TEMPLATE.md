# 每个NBA2K游戏机制攻略主题的写作模板

> 此模板为研究写作结构，不代表有任何游戏数据已实测。新卡片置于`guides/K##_TOPIC.md`，可多张按功能拆分，避免一个上千行大文件。

```yaml
mechanism_id: K01.GAME_LOGS
title: 逐场比赛日志
priority: P0
research_status: RESEARCH_IN_PROGRESS
version_scope:
  - game: NBA2K22
    platform: PC_CURRENT_GEN
    mode: MYLEAGUE
    feature_status: UNKNOWN
other_versions: []
sources: []
visuals: []
gm_consumers: [WEB_GM, WEB_ANALYTICS]
pc22_native_status: NOT_OBSERVED
dev28_followup: UNKNOWN
```

## 1. 机制概述与篮球/经营意义
说明该功能的实际用途、与真实NBA篮球/终极联盟经营的联系；不得仅复写字段名。

## 2. 游戏如何使用
- 菜单路径（明确在哪个版本/平台/模式观察或社区报道）
- 当前值、合法可选项与说明（如为可控制项）
- 静态设置还是比赛期间动态事实，记录刷新/保存与AI覆盖条件
- 玩家社区的常用攻略、错误示范及有分歧之处

## 3. 与其它游戏机制的关系
绘制文字关系链，例如训练负荷→疲劳→伤病风险→出场与表现，或Playbook→战术类别→球员PlayTypes→教练Run Plays→实际调用。**只断言证据支持的因果，未知公式不能编造**。

## 4. 数据输入、输出与GM使用
- 玩家真实看得到的数据或菜单选项是什么？
- GM最低需要哪些基础事实，哪些可派生，哪些必须有原生数据？
- 当前项目是否已采/可查/可执行？如果尚未对照代码，写`PROJECT_STATUS_NOT_AUDITED`，不要猜。
- 如何按DEV28将此机制变成GM选项查询、提案、授权执行及读回结果？

## 5. 证据、截图和版本差异
- 来源`SRC-####`，具体支持内容；截图`VIS-####`与真实来源页
- `OFFICIAL / COMMUNITY / PLAYER_SCREENSHOT / GAME_NATIVE / INFERRED / UNKNOWN`
- 其它版本可帮助理解什么；PC22的哪个具体菜单/内存偏移仍待认证？

## 6. 当前结论与待办
**已证机制**、**跨版本可借鉴**、**待PC22确认**、**DEV28定向需求**分开。支持`INCOMPLETE_WITH_OPEN_ITEMS`，不得冒充全部已验证。
