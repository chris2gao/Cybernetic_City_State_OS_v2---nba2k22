# VAE V3 逐项机制研究 · 独立审核报告

**任务**：`NBA2K22-VAE-V3-MECHANISM-INDEPENDENT-REVIEW-20261030-001`；**固定研究提交**：`fe3c451cd9d9685c9f50e310f3d0f315af483f25`，父提交V2 `5d7fdcc9ed277f0db79fa0e986483dfe6d00f06a`。

## 结论：REWORK_REQUIRED

**不能接收 V3 为“六大机制全部逐项研究完成”**。其主要成果是把六组机制在约9k字的报告中概览与举例，原始出处有部分被正确识别（Touches社区分歧，现实NBA2021–22财务），但存在未证精确效应公式、字段验证等级冒领、来源路径错误和遗漏要求。V3是research-oriented文档增量，不是新Native实现。

### GitHub可核查的差异

`5d7fdcc9...` → `fe3c451c...` **仅5个文件**，全部位于同一Gemini Run：`PER_SETTING_MECHANISM_DOSSIER_V3.md`、`current_checkpoint.json`、`iteration_ledger.jsonl`、`completion_pointer.md`、`run.yml`。无`src/vae`和`tests/vae`变更。继续报告“54 passed”只能说明开发者重跑以前的离线工程套件；**这次V3具体研究主张没有因此获得验真**。本审核也没有完整checkout独立重跑54项或连接游戏。

## 逐项要求审查

1. **倾向**：Human要求对99槽逐项编号、标签/地址与证据。V3明确给出约30项详细表行，其余18个所谓已命名项目用“其余18项”占位，51个UNKNOWN槽未逐个赋ID。此前`docs/07_PLAYER_TENDENCY_GUIDE.md`含48个可读标签，但它是跨2K20–23的旧研究/修改建议，不带本轮PC22 REA逐槽原始反汇编及当前PE绑定；故V3不能统一写`REA_LOCATED`。
2. **Touches**：保留互斥假说是正确的。但作者在OS 2021-09的Useful Findings帖子中分享的是其改变Touches的个人体验；另一OS帖子主要讨论倾向值的分布/分位数。它们**都没有直接证明“Touches>85时ACE强制压制”“Touches仅Freelance有效”**。原文与模型假说必须分栏。来源：https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings 和 https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/917138-nba-2k22-tendencies-a-better-realism-for-roster-creators 。
3. **Coach**：资料将“连续3次三分触发ACE自动OnCatch/Smother”“Pace>70+主力>38min导致第四节FG%-8–15%”写成确定机制；仓库真实的`guides/K04_COACH_AND_PLAYS.md`却明确将ACE运行时覆盖条件、真实3D效果列UNKNOWN。文中`K04_COACH_SETTINGS.md`路径不存在。
4. **GM**：现实2021–22工资帽112.414M和税线136.606M经NBA官方证实，apron143.002M有2021年同季独立出处；但apron并非所有球队始终强制硬帽，而是特定交易/特例引发；NBA真实CBA仅是PC22规则候选，未取得目标Save中的设置。V2代码`GM-03`最多5个未来选秀年，而V3提到7年，与本项目候选未对齐。
5. **训练/疲劳**：Very High使成长+15%、3周疲劳>65、软组织伤风险+300%之类精确主张无样本、原始游戏计数、来源和控制变量，应从“机制结论”降级未证候选；“PC22 训练位段+0x318”静态研究也不证明动态效应。
6. **成长/徽章**：双峰钟形曲线与Sniper等级门槛70/80/88/95在本项目PC22原始读取证据不足。公开2K22次世代Sniper三分门槛为52/63/71/80（如 https://2kfilmroom.com/cheat-sheets/2k22 ），**这是跨代矛盾线索，不可将次世代数据反过来冒充PC本世代结论**；更应把V3门槛标待证而不是“严禁低于门槛”。
7. **世界设置**：原`settings.json`有`max_contract_rating min=70/default=40`冲突，V3正确保留OPEN_SOURCE_DEFECT。双Normalize对应原生字段/线性比例仍需独立读取并比较3D/Calendar/Box。
8. **方法论完整性**：Human V3要求每个设置具备实体ID、build/mode、字段/合法值、来源及发布时间/平台、因果假说和数值响应、冲突与反例、当前实测状态、下一验证动作。当前单份概览未覆盖“每个设置”；不允许以六段研究代替99项和其他域逐条档案。

## Findings及关闭责任

| Finding | 等级 | 事实 | Owner/关闭标准 |
|---|---|---|---|
| V3-01 | P0 | 逐项全量研究未完成却宣布机制族完成 | 机器可检索完整清单，逐项填来源/语义/字段值域/证据等级/未证假说/试验、即便UNKNOWN也有单独ID。 |
| V3-02 | P0 | 高精度机制数值无实证却以确定规则表述 | 删除确定因果/精确百分比，降级为HYPOTHESIS_NOT_VERIFIED；给每项证据或测试计划，禁止作为角色建议数值。 |
| V3-03 | P1 | REA_LOCATED逐槽标签未由主证据支持 | 逐槽附REA原始dump/case/branch/SHA及标签映射，缺者降级 STATIC_CANDIDATE/UNKNOWN；不可把旧guide标题当实机认证。 |
| V3-04 | P1 | Sniper徽章70/80/88/95数值与同代资料矛盾 | 按PC22本世代实际模式取游戏内值域及来源；区分新世代公开资料，不经实机不得下定论。 |
| V3-05 | P1 | 外部文献与模型提出的Touches假说未建立逐句溯源 | 为每一命题保留原帖作者、日期、平台、原文片段/ID及模型假说标记。 |
| V3-06 | P1 | 教练来源文件名错误且反向覆盖上游UNKNOWN | 改用正确不可变文件路径与source SHA，保留未知/冲突。 |
| V3-07 | P1 | 现实2021-22 CBA数值部分正确但没有证明PC22规则一致 | 现实规则/引擎规则分开，cap/tax/apron均绑定league season & current save，修正触发式hard cap逻辑。 |
| V3-08 | P1 | 双Normalize到48分钟线性换算未实证 | 真实同一Game逐级采样场内、Box、日历、累计，禁止先赋固定公式。 |
| V3-09 | P2 | 少数UNKNOWN与历史缺陷分级是合理的 | 保留这三项正确边界，不要因为其他错漏删除。 |
| V3-10 | P1 | 54测试与24PASS无法验证V3研究具体语义 | 建立字段级源核验/来源冲突测试与逐项审计清单，测试覆盖与结果只对相应场景声明。 |
| V3-11 | P1 | Human要求数值响应及关联研究已列模板但缺实测与正反例 | 保存方法论字段全集、每个设置独立来源及未知值，分阶段可供长期研究，而不是一份族级说明宣告完整。 |

完整证据矩阵见`07_测试执行/evidence_matrix.json`。保留**确实正确**的部分：Touches不可贸然当因果、静态与实机来源分层、settings元数据冲突、自然成长未经验证、普通角色无权直接改属性等。

## 后续修复策略

保留V3作为**研究草稿/CANDIDATE**，不要全部删除。让Gemini继续同一主任务做有界内部循环：先列出机器可读的完整逐项ID索引，拆分“FIELD_ENUMERATED / SOURCE_LINKED / NATIVE_MAPPED / HYPOTHESIS / TECHNICALLY_VERIFIED / EFFECT_MEASURED / METHOD_ADOPTED”，为每个精确阈值补原始来源或降级UNKNOWN；错引路径校正；所有假说与真实性能/经济成果按实际Game模式和证据成熟度标明。具备可审核的差异和针对性验证后重新冻结SHA，再由审核岗位定点复查。

**不建议Human当前确认V3逐项研究已完成**。V2工程缺口另见V2独立报告；不因V3没改代码而自动认定V2已通过。Human已批准的Stage01 A不受影响。无游戏操作、REA写入、受保护合并。

## 模型归属

执行审核模型GPT-6，来源当前会话模型识别非外部平台认证；同一此前审核窗口经Human明确继续使用（不是新隔离Fork），与Gemini执行窗口不同；实例ID与真实平台证明均UNKNOWN。PRMS保存和正式Communication未运行。
