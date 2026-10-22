# DEV17 V1.1 — M系列专属Codex窗口的GM主线实现（接收DEV14）

**2026-10-19** · 最新唯一任务分配见[DEV18双窗口接力](DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)，GM规则见[同名战术书与个人防守V2](../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)。

> **重要：DEV17代码执行者只限窗口②（PR#4 M3系列）**。此前将DEV14-H、Potential=1和DEV13都交给“同一个Codex窗口”实施的指令失效。底层由独立窗口①接手PR#5；窗口②只负责接收与应用。

## 本局GM业务规则

- 所有球队有本队同名Playbook容器（用户玩法保证，默认成立）。正常GM不为了换打法切`coach.PlaybookID`，在本队的68槽手册中增删战术；遇到实际无法定位的目标Native ID，单动作Fail Closed，不要求AG预先研究30队书克隆/共享。
- 换帅：A队/A教练/A书 → A队/B教练/B书（原生临时）→ **恢复A队B教练`PlaybookID`到A同名书** → 重新读取A书 → 按B教练体系与A阵容修改A书。B书不改。技术性绑定与槽位修改先后两次DEV14执行及批准。
- 每队每游戏赛季**仅休赛期最多一次主动换帅**，本轮只做M3规则、已确认换帅事实、Book恢复决策计划；完整教练合同/竞价/自由市场留后续单独任务。
- GM只写`PERSONAL_DEFENSE`，`OVERALL_DEFENSE`留作只读；球员原始能力不可直接修改，已获批例外`Intangibles`引导原版AI轮换、Potential发布前自动置1均由窗口①实现，窗口②按其合同使用。

## 本窗口②的具体开发步骤

**M0—交接读入**：等待或读取窗口①交付的`docs/development_reviews/DEV14_TO_M3_HANDOFF.md`与PR#5当前commit；PR#5经用户明确批准合并main后，从最新main向PR#4分支引入底层。处理`src/gm_data_access/query.py`、`scripts/gm_data_query.py`等交叠文件并运行现有M3 P1–P5定向回归。PR#4单独批准后才能合并；任何PR不可自动合并。

**M1—战术数据桥**：复用DEV14现有教练19项、球队同名68槽书、4槽PlayTypes、已具名48项Tendency、球员当前篮球能力、PERSONAL_DEFENSE、现有团队6项/个人5项训练，以及Intangibles软轮换来源。51未知倾向/部分CRC语义/疲劳数据缺失仍标UNKNOWN/NOT_OBSERVED，不准臆造。

**M2—经营决策**：在既有M3A/M3B D1–D6工作台执行30队HOLD/内部战术与训练/市场交易比较，基于篮球风格、实际赛果、年龄/负荷/角色产生候选；生成符合`save_instance_id+generation+source_batch`的稀疏DEV14意图。先发、第六人和分钟范围可由Intangibles影响，ACE自行实时换人。

**M3—教练与本队Book决策**：为每队建立同名Book读索引（team_id/name→已加载Book Native ID），普通GM防守只按个人对象提案；换帅严格OFFSEASON_ONLY、每队每赛季一次。已确认B教练来到A队且本局A同名Book存在时，GM提出受控`TEAM_BOOK_REBIND`，回读后重新规划A的手册68槽变更。没有真实员工执行器时不声称签约完成，不修改其他队书。

**M4—集成验收**：按既有合成30队和M02旧数据定向测试未知字段/权限/旧事实边界；读取DEV14回执并复核，不创建第二套SQLite、memory executor、approval机制。不执行正式游戏，不强迫重跑119项DEV14旧测试。

## Antigravity后置

AG扩展战术CRC现实动作与体系、剩余51倾向名字、更多位置训练模板和疲劳读取，在上述主线跑通后以增量Registry/GM知识模块对接。只有真实已加载本队Book原生ID或现存slot操作出错，才单独给AG一个最小修复任务；不以假想共享风险阻塞M3。

**本窗口输出**：PR#4增量工程和定向验收；清楚区分窗口①已经交付的native能力、窗口②正在开发的GM策略和仍需AG扩展的字段。业务由用户批准，但本文件不是合并/游戏写入授权。
