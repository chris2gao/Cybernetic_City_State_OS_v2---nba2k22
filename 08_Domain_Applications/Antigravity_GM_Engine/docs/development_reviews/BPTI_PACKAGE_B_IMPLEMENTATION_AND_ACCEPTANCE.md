# BPTI 工作包 B — 实现与最小验收

2026-10-20。终结状态：`BPTI_PACKAGE_B_COMPLETE_TASK_CLOSED`。交付分支 `codex/bpti-package-b`；独立Draft PR供玩家审阅，包B不自动合并。

## 前置条件与授权

玩家本次明确追加授权“如果没合并，你合并下，并继续之前的工作”。先审阅DEV27 `867fe85`及交接`80459b4`，确认相对main仅两提交；将远端main从`52fe691`快进到`80459b4ad7c2047e2479b0cb9b1140bfbf77e6ea`，并同步本地main，未重复运行DEV27 T1–T3。此前“未推送/未合main”文字是DEV27原交付快照。

B0 PR #8、B1 PR #9、共享池 PR #10均已合并。包B从含DEV27的最新main建立独立工作树；原`codex/season-match-history`和其内容保留，不用旧DEV23分支覆盖main。仓库命令由已确认管理员权限的PowerShell执行。

## 实际实现

1. **B2**：140条NativeBinding，覆盖十家族与既有原生控制方向/未知/不支持动作；字段名从静态Registry构建，没有复制执行器或创建另一套审批。每条含技术出处、意图、不确定性及HOLD。原生八体系不与十个篮球家族一一对应。
2. **B3**：30张唯一TeamIdentity，沿用B0 DTO；每队五层Claim、原R2父引用、时间与来源边界，以及候选、角色、成本/调整条件和UNKNOWN。全部历史seed、未绑定存档。通过现有知识入口和TEAM_STRATEGY_STATE的既有引用槽衔接，不创建/写入正式经营状态。
3. **B1-EVIDENCE-4**：逐条读取四篇NBA官方来源，增加四条SUPPORTED_INTERPRETATION机制Claim，保留刊期与事实期。原四张完整研究卡不解锁；普通GM只取得狭窄机制，旧父Claim与未来内容仍隐藏。
4. **查询/文档**：现有Knowledge.bpti与gm_knowledge增加绑定、身份和联合context入口，所有摘要分页1–5。使用手册、B0/B1索引、AGENTS、开发基线33及状态34已维护。本包没有新游戏来源或新执行能力，因此不修改source_catalog或执行器白名单。

实现文件：`src/gm_core/bpti_package.py`、`bpti.py`、`knowledge.py`，`scripts/gm_knowledge.py`、`build_bpti_package_b.py`，以及`web_gm/knowledge/bpti/package_b_v1.json`和`four_family_evidence_v1.json`。

## 四项授权检查：实际结果

管理员会话运行 `python -B scripts/check_bpti_package_b.py` 一次；**Ran 4 tests in 0.869s — OK**。构建命令为 `python -B scripts/build_bpti_package_b.py`，它是显式知识生成，不是游戏采集或新增测试。

| 检查 | 实际覆盖 | 结果 |
|---|---|---|
| B-B1 | 十家族绑定；支持字段对应现有gm_enabled；具名48倾向/PERSONAL18/训练11/四Type+Initiator；OVERALL/自由PlaybookID/RAW不开放；当前类型匹配为零，假类型匹配证据被拒；无native目标载荷 | PASS |
| B-B2 | 30唯一seed与五层引用；历史时间、父Claim、来源链接；全部未绑定且UNASSESSED；早于种子日期不暴露内容；LAL-S2缺源、ATL-S2非长期文化证据保留 | PASS |
| B-B3 | 四个官方源URL与日期/事实区间/父Claim；普通GM仅狭窄入口，原整卡与父复合Claim仍隐藏；早期日期不泄露；实际覆盖10入口/6整卡 | PASS |
| B-B4 | 原Knowledge接口的体系+绑定+球队联合查询；限制/分页；现有CLI一次联合查询；保护的执行/策略文件前后字节相同 | PASS |

B-B3的外部真实性证据是实际读取官方页面及[精确定位记录](BPTI_PACKAGE_B_HISTORICAL_EVIDENCE.md)，静态检查只核对所记录的契约/时间与投影，不冒充现场重新认证网页内容。B-B4的CLI检查只对应其实际运行的联合查询，其他手册示例不声称已逐条运行。

没有重跑B0/B1/M3/DEV14或DEV27旧套件、没有新增广泛回归/性能平台、没有比赛效果测试；四项均首次通过，因此未作复验或追加检查。

## 真实覆盖与限制

- 八原生体系、已认证教练方向、四Freelance/四PlayTypes顺序、具名倾向、个人防守、训练和软轮换有工程接口；绑定只证明字段方向，具体同批对象/枚举、来源与批准仍由M3/DEV14负责。
- 本包没有任一实际TYPE_MATCHED_ONLY。共享池精确CRC类型、受益人/动作分支、ACE、调用频率、Tempo篮球意义、3D/Calendar效果仍UNKNOWN。名称推断只供研究。
- 本队书可从共享池选条目，但实际可写CRC必须来自新同批加载目录；不改其它队书。TEAM_BOOK_REBIND独立确认/批准后取新来源，再另作槽方案。普通GM整体防守只读、51匿名倾向不可写。
- 普通GM截至2021-10-19：**10/10家族有已过滤参考入口 = 6张完整参考卡 + 4条狭窄机制**。四张完整原卡并未变成可读/VERIFIED；不宣称十个完整体系、原生行为或球队成绩已认证。
- 30历史身份不等于30队实际GM评估。R2资料未全量重新外文核实；部分长期传统、教练细节和出处保持未知，不通过新源掩盖LAL-S2/POR-S2等缺口。
- B4/B5/B6只可复用本包接口，尚未实现。V3保持有效，V4仍未启用；本任务不访问游戏/活动库、不切档、不创建存档、不采集/发布游戏事实、不执行交易/签约/换帅/战术、不修改Ability/Potential/Badge。

工程分支发布和Draft PR属于本次授权的源码交付，与游戏数据-Publish分开。当前任务完成后终结；后续包C须玩家新任务明确触发。

## 实际源码交付位置

实现提交：`8776c7841e6e5132d458b660e09dbc786033ec3a`。
Draft PR：[PR #11](https://github.com/chris2gao/nba2k22-gm-engine/pull/11)，base `main`，head `codex/bpti-package-b`。
后续仅补此交付链接，不追加测试或修改实现；本包不自动合并。
