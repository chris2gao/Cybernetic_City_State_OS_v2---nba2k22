# NBA2K22 · 01b 逐字段证据与缺口矩阵 V1

状态：未完成目标游戏 UI 字段全集核证；仅记录当前仓库原生研究和工程注册，供 Q53=A 后续逐字段扩展。

证据等级：REGISTRY_ONLY（仅注册），RESEARCH_CLAIM（研究文件声称），UI_VERIFIED（需阶段02实机验证，当前不宣称具备）。隐藏 PLAYER.potential 不得向普通 GM 暴露。

来源：`config/memory_field_profile.json`（PLAYER 72，STAFF 13，TEAM_STATS 27，PLAYER_STATS 34，共146条）；`research/native_access/AG_NATIVE_01D/ui_native_source_matrix.json`（39个研究入口）。两者可能重叠，不能作为已确认 UI 字段数。

## 字段级清单

以各个来源登记项为独立行；每行必须含领域、工程字段键/Native入口、来源、证据等级、UI核证、权限、缺口及后续验证阶段。已有以下五份字段登记分卷，总计146条工程注册与39条Native研究入口；它们可能重叠，均未达到逐字段游戏实机验收：

- [PLAYER 逐项登记（72 条）](NBA2K22_TASK1_01B_FIELD_COVERAGE_PLAYER_V1.md)
- [STAFF 逐项登记（13 条）](NBA2K22_TASK1_01B_FIELD_COVERAGE_STAFF_V1.md)
- [TEAM_STATS 逐项登记（27 条）](NBA2K22_TASK1_01B_FIELD_COVERAGE_TEAM_STATS_V1.md)
- [PLAYER_STATS 逐项登记（34 条）](NBA2K22_TASK1_01B_FIELD_COVERAGE_PLAYER_STATS_V1.md)
- [NATIVE_RESEARCH 逐项登记（39 条）](NBA2K22_TASK1_01B_FIELD_COVERAGE_NATIVE_RESEARCH_V1.md)

每行保留工程或研究键、来源/偏移或原生入口、证据等级与未核验状态；字段级真实UI标签、合法权限和最终数据库字段需在02/03逐项核定。

## 关键缺口

RES-P：全部真实球员页签、倾向、徽章、Play Types、伤病、训练、逐场高阶。

RES-G：完整赛程和季后赛系列赛来源。

RES-T：球队完整身份、轮换与统计。

RES-C：教练实际归属、战术和训练全字段。

RES-M：财务、交易执行回执、选秀候选。

RES-L：世界线、联盟、比赛设置、历史荣誉。

03在02证据完成后形成最终DDL；完整需求A仍待Human整体确认。
