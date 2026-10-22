# DEV10 M2 本地实现验收

日期2026-10-19。状态 `IMPLEMENTED_LOCAL / WEB_CONNECTIONS_DEFERRED_BY_PLAYER`；本报告覆盖M2实现，不声称正式球队分析或GM V4已启用。

| 交付 | 已实现与实际证据 |
| --- | --- |
| 知识内容 | 小型JSON含12卡、30队2021参考、19条机制、38来源；来源ID/URL和当前字段校验通过 |
| 按需消费 | `gm_knowledge.py search/show/franchise/rules`；摘要最多5条，按标签、字段、球队试点及文本检索 |
| 原生映射 | 当前profile与同批字典解析标签；PNR直接枚举、Drop近似假设、无来源缺口三个分支通过；动态手册与四槽顺序沿同批目录 |
| 条件式三队参考 | 相同合成“即战力侧翼/首轮及多年工资/内部替代”问题可携带GSW/SAS/OKC不同优先追问、转向条件与保留/内部替代；未生成当前真实三队决策 |
| 状态维护 | 纯DTO校验；共享workbench新增策略表；两修订历史可读、过期预期冲突不覆盖、审批/执行状态拒绝、可选财务run与跨批复核 |
| 30队初始化 | 全部UNASSESSED，核心/动作/预算为空；实际已评估球队数0 |
| 本地CLI | 已有M02静态副本走通检索、映射、30候选、SAS未评估候选保存/读取及摘要导出；无游戏连接 |

实际运行：

```powershell
python -B -m unittest discover -s tests -p test_gm_knowledge_m2.py -v
python -B -m unittest discover -s tests -p test_gm_finance_m1.py -v
python -B scripts/check_gm_knowledge_m2.py
```

结果：M2六项通过，M1七项通过（共享Store受本次新增策略表影响，因此做一次相关复核）；本地CLI `PASS_LOCAL_STATIC_M02`。机器证据 [DEV10_M2_LOCAL_EVIDENCE.json](DEV10_M2_LOCAL_EVIDENCE.json)。合成测试用于内容/表达/版本验证，不证明本局胜率、成长效果或现实球队政策适用。

实现期间第一次映射检查发现现有枚举目录实际为raw→label，已改为反向查找语义标签后通过；没有为该问题扩大游戏测试。未执行全项目回归、UI菜单扫查、保存/重启、Web连接、现金调查、采集、数据发布、交易/签约或教练写入。正式执行脚本与数据源注册表未新增能力，现有19默认/18防守执行范围不变；知识可检索不等于新业务执行器。

操作入口见 [M2手册](../GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH.md)。M1证据独立见 [M1验收](DEV10_M1_FINANCE_ACCEPTANCE.md)。M1/M2提供后续M3可消费的本地组件，未实现M3/M4、未自动进入下一阶段。
