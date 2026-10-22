# BPTI 工作包 B：NativeBinding 与历史 TeamIdentity

2026-10-20，`BPTI_PACKAGE_B_V1`。沿用 `BPTI_KNOWLEDGE_V1`、M2 `Knowledge.bpti()` 和原 `gm_knowledge.py`，无新数据库或执行器。工程从含 DEV27 的 main `80459b4` 独立开发；交付为 Draft PR，不自动合并，不启用 GM V4。

## 数据与接口

`web_gm/knowledge/bpti/package_b_v1.json` 保存 B2/B3 的 sources、claims、140 条 NativeBinding、30 张 TeamIdentity、五层引用及四个细粒度机制入口。`scripts/build_bpti_package_b.py` 显式从既有静态 Registry、R2 表格和已审阅的四条来源记录构建；不访问游戏、活动数据库、网络或执行器。普通查询仅加载现有小型知识文件。

原 B0 source index、B1 system_cards 文件和 R1/R2 原研究不重写。新 Claim 保留 parent_claim_id、来源 ID、原始文档行号、事实时间、可知时间、证据状态与反证。R2 是后来研究，B3 逐 Claim 提取开档前背景，历史种子统一表示 2021-10-19 的快照；不把早期来源刊期误当成所有后来角色信息的可知时间。

## 原生方向的证据层级

每家族关联九组已有字段方向：八体系的两个选择字段、已认证教练默认方向、四个有序 Freelance、四 PlayTypes/Initiator、具名48倾向、18项 PERSONAL_DEFENSE、训练6+5、软轮换和本队书槽。字段名由既有 Registry 投影，不复制布局，也不对模型提供地址、原值或数值目标。

| mapping_status | 本包含义 |
|---|---|
| SUPPORTED_FIELD_DIRECTION | 该字段已有工程接口，篮球意图仅是定性方向；效果和具体对象仍须后续 M3 同批来源 |
| TYPE_MATCHED_ONLY | 必须另有原生或玩家报告的类型成员证据；本包没有此类实际映射 |
| UNKNOWN_NATIVE_BEHAVIOR | CRC类型、实际受益人、Tempo意义等未知；可研究名称候选，不生成动作 |
| UNSUPPORTED_ACTION | 普通GM整体防守、任意换书、匿名倾向、精确分钟/概率及实时控制不开放 |

完整字段集合和证据由 `bpti-binding` 读取；列表只返回短摘要。NativeBinding 是参考，绝不产生 Desired、approval tuple、stage 或 apply。字段存在不证明篮球效果；R1 高置信度也不提高原生行为证据等级。

Playbook 是本队68槽容器，内容可以来自共享池；1392条归档标识、静态名称和用途推断不能替代新同批已加载合法目录。FIST/GIVE/QUICK等词根不能认证 PlayType，多成员关系可存在，固定位置和固定受益人不是类型资格前置。球员四类型和球队四Freelance分别保留顺序，前槽优先，不创造频率、权重或失败阈值。

普通GM保持正常18项教练、PERSONAL18、具名48倾向等原有边界；Tempo虽有原生接口，BPTI不解释其篮球效果。OVERALL只读、51匿名倾向不写，PlaybookID只允许独立已确认 INITIAL_SAVE/COACH_CHANGE 事件的 TEAM_BOOK_REBIND。绑定之后须新来源和另一份槽方案；DEV27只修名称识别，不解除任何这些要求。

较低精度替代也明确列在绑定中：Tempo意义未知时研究已确认POE节奏；精确受益人未知时保留角色与类型研究；整体覆盖不开放时只研究真实个人对位；没有精确分钟控制时使用软轮换或HOLD。Intangibles25–99不是篮球实力或球探分数。

## 三十队的五层历史种子

每队使用 B0 TeamIdentity 原字段，另以 Claim 引用区分：FRANCHISE_IDENTITY、COACH_PHILOSOPHY、BASKETBALL_SYSTEM、PLAYER_ROLE_AND_AGENCY、MATCHUP_GAMEPLAN。引用包含组织/时代边界、教练背景、攻防候选、角色自主关系，以及调整条件、角色/空间/防守机会成本。

全部保持 HISTORICAL_SEED_ONLY、NOT_BOUND_TO_ANY_SAVE，实际球队仍 UNASSESSED。候选不是已经使用的战术，历史教练不是当前档任命。可作为将来 `TEAM_STRATEGY_STATE_V1.identity_reference` 的知识引用；本包不写该状态，也不生成M3经营评估。

普通GM按Claim过滤，未知部分列入 blocked_claims，不用同队其它可靠来源替缺源背书。ATL-S2仍只支持人员背景，不认证长期文化；LAL-S2和原有缺失来源保留 UNKNOWN/SOURCE_MISSING，不填替代URL。只有后续合法同批 GM_SANITIZED 人员、教练、财务和玩家触发任务才能进入实际经营。

本包复用既有 R2/来源补录，不声称重新逐页核实全部球队历史外文资料。团队种子的 SUPPORTED_INTERPRETATION 与原文 VERIFIED、项目技术接口 VERIFIED 分开。

## 四类体系的狭窄历史入口

[逐来源核验记录](development_reviews/BPTI_PACKAGE_B_HISTORICAL_EVIDENCE.md)与 `four_family_evidence_v1.json` 记录四条NBA官方文章的刊期、事件时期、定位及最低限度释义。它们按 B0 日期规则可供普通GM读取，但只形成 `GM_ELIGIBLE_MECHANISM_ONLY`：`card=null`，正文仅在 `mechanism_entries` 的细粒度Claim内。

截至2021-10-19，实际覆盖为10个家族有参考入口，其中6张完整B1参考卡、4条狭窄机制。不是10张整卡全部认证，更不是10类2K动作已实现。原四张含未证/未来材料的卡及其父Claim继续阻断；RESEARCH仍可查原资料。过早日期仍隐藏新增Claim，不修改截止日。

## 有界查询示例（使用说明，不是额外运行记录）

```powershell
python -B scripts/gm_knowledge.py bpti-bindings --system-id MOTION_READ_REACT --as-of 2021-10-19 --limit 2
python -B scripts/gm_knowledge.py bpti-binding --binding-id B2-MOTION_READ_REACT-BOOK --as-of 2021-10-19
python -B scripts/gm_knowledge.py bpti-bindings --field personal. --mapping-status SUPPORTED_FIELD_DIRECTION --as-of 2021-10-19 --limit 2
python -B scripts/gm_knowledge.py bpti-identities --as-of 2021-10-19 --limit 5 --offset 0
python -B scripts/gm_knowledge.py bpti-identity --team MIA --as-of 2021-10-19
python -B scripts/gm_knowledge.py bpti-context --system-id POST_HIGH_LOW --team PHI --as-of 2021-10-19 --limit 1
```

分页limit为1–5，offset非负，返回total_matches/next_offset；source/claim沿原B0接口读取。RESEARCH须显式选择；普通GM必须提供日期，且仍受2021-10-19截止。

Python沿原入口：`index = Knowledge(root).bpti()`；然后调用 `binding/search_bindings/team_identity/search_identities/context`。联合context返回一张可用完整卡或狭窄机制、最多五条绑定摘要和可选一队种子。未指定team时不载入30队正文。

## 给 B4/B5/B6 的复用边界

- B4可显式引用以上context/Claim，与已有M3 DTO中的 HOLD/INTERNAL/MARKET 比较相连；本包没有接入正式决策或新建Blueprint。
- B5可把identity_id作为既有策略状态的历史引用，仍由原workbench保存版本；不创建第二个经营系统。
- B6可复用现有只读接口和清楚分级的UNKNOWN；不能把本包四项检查当真实30队经营、比赛效果或原生执行验收。

实际验收仅B-B1至B-B4，见[工程验收报告](development_reviews/BPTI_PACKAGE_B_IMPLEMENTATION_AND_ACCEPTANCE.md)。没有B4–B6、DEV24、比赛/Calendar模拟、采集、游戏写入、GM V4或新存档。
