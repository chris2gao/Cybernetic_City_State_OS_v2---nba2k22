# DEV27 — BPTI本队战术手册名称后缀匹配：最小Bug修复 V1

> **后续实际完整修复范围（2026-10-20）**：玩家已确认虽然DEV27的`867fe85`解决末尾独立Playbook标签的名字匹配，**战术手册总目录、真正挂载/教练ID关联、换帅后恢复同名书及槽内容更新的完整经营工作仍未完成**。上述需求已独立规划到[DEV28 D28-1](DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)；DEV27原T1–T3静态验收仍有效，但不能当作全面战术执行证明。**不在PR #12收尾中顺手扩展此项目。**

2026-10-20 | owner=Web DEVELOPMENT | executor=Codex（玩家新任务触发） | status=**BPTI_DEV27_BUGFIX_COMPLETE_TASK_CLOSED / LOCAL_COMMITTED_NOT_MERGED**。玩家最新指令“直接提交即可”覆盖下文Draft交付要求；实现提交867fe85，未创建PR。实际实现、T1–T3及交付见[验收报告](../development_reviews/BPTI_DEV27_TEAM_BOOK_SUFFIX_FIX_AND_ACCEPTANCE.md)。下文为原批准合同。

> 玩家已批准先修DEV23揭示的`team_book()`后缀Bug，再继续BPTI B2–B6；PR #10已在2026-10-20合并main（merge commit `8c80c7d452a69cdef72eee1c22b39562926af32a`）。本文件是单独Codex工程任务合同；写入规划不等于已实施修复。严格遵守`AGENTS.md`的**TASK CLOSED而非PAUSED**协议以及`PLAYER_DEVELOPMENT_POLICY_V2`。

## 1. 实际Bug及影响（已查证源码）

权威文件：`src/gm_state_io/team_book.py`：

`normalized()`把名字转NFKC/casefold并保留字母数字；`team_book(team, books)`从球队`name`、`abbreviation`、`city + name`生成别名后，要求`normalized(book.name) in aliases`。实际已加载书的名称带英文“ Playbook”后缀，如`Bulls Playbook`、`Heat Playbook`、`Warriors Playbook`；`normalized('Bulls Playbook') != normalized('Bulls')`，造成`TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS`。

DEV23真实只读观察报告：
- `docs/development_research/BPTI_DEV23_CORE_PLAYBOOK_SEMANTICS_AND_ROLE_EVIDENCE_V1.md` §6，证据 E04/E07；
- `docs/development_research/BPTI_DEV23_PLAYBOOK_SEMANTICS_INVENTORY_V1.json` 中`business_binding_finding`；
- 三本的当前教练Book ID与本队书一致，但业务入口仍不匹配。
- 该函数被`validate_rebind`和`validate_slot`共同调用。失败会阻碍GM安全投影/本队书提案，**并非只读知识池问题**。

## 2. 本次明确授权的最小修改

只修`src/gm_state_io/team_book.py`中`team_book()`的**本队同名手册精确识别**，使原本已支持的精确匹配继续工作，并兼容英文 `Playbook` 独立末尾后缀。可以把原始book名称的精确规范化标签与“只移除结尾Playbook后的精确规范化标签”同球队别名比对，或采用等效的小改动。不得用任意包含、模糊相似度、前缀匹配或根据当前Coach PlaybookID跳过同名规则。

核心保障：
1. 原先严格的本队身份、`team_directory`、`owner_team_ids=[team_id]`、唯一书匹配 `len(matches)==1`、`digest(book)`、当前枚举ID一致性和`TEAM_BOOK_REBIND`的已批准事件约束**全部原样有效**。
2. 仅允许在真实书名末端带`Playbook`作为标签时进行这种后缀兼容；不要让`Bulls Practice Playbook`、`Lakers Playbook`等错误名称被误配。
3. 存在两个都可与同队别名匹配的书仍报原错，不自动选第一本、不重写其它队书。
4. **不更改**`validate_rebind`与`validate_slot`的审批/所有权语义，不更改DEV14 Stage/Apply/CAS/Registry、不更改共享战术池、不改教练PlaybookID、不修改任何游戏数据。
5. 不改其它球队名字、库表、运行时查询、PlayType、CRC、球员能力/潜力和游戏控件。

## 3. 玩家在本次修Bug同时批准的仅三个最小定向静态检查

T1：使用与DEV23已记录命名方式一致的Bulls、Heat、Warriors球队/书**静态小fixture**，逐个验证带` Playbook`后缀的唯一识别成功；原有不带后缀的匹配仍正确。没有真实游戏访问。

T2：验证不存在、跨队、伪相似标签或两本重复的情况仍失败（`TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS`），不能放松唯一性与归属。

T3：通过**纯静态样例**调用现有`validate_slot`与`validate_rebind`所依赖的识别，确认本队唯一合法目标通过、它队/不匹配身份或缺少已确认事件仍拒绝。现有合同字段优先，若需新增复杂fixtures或测试基础设施则不扩张；可以将本次T3限制在最小函数级封闭验证并准确写明覆盖不足。

以上三个任务直接对应修复范围，不授权重新运行旧B0/B1/M3/DEV14完整测试、真实游戏采集、存档改写、全30队模拟、增设其它字段防线或长时间反复实验。若改动仅一小段代码，验证应保持同样小规模；不得为了第三项引入新的框架。任何额外设计/测试必须另获玩家批准，此时当前Codex任务应保存交付并**真正终结**，不能暂停等待。

## 4. Codex执行、分支、交付与终止

1. 从**最新main**启动**一个新的独立Codex任务**，先读`AGENTS.md`、政策V2、DEV27、DEV23报告以及实际`src/gm_state_io/team_book.py`。PR #10已合并，不从旧DEV23分支继续叠加。
2. 新建独立分支，只修改目标函数、相应小型静态验证及必要的最小文档/开发状态；不要把工作包B代码放进本次PR。
3. 以原函数的归属唯一性为权威约束；在已批准的T1–T3检查中如实记录实际运行/未运行与结果。
4. 交付一个**Draft PR**和简明验收报告`docs/development_reviews/BPTI_DEV27_TEAM_BOOK_SUFFIX_FIX_AND_ACCEPTANCE.md`，包含：目标文件差异、实际3项检查证据、限制、已知剩余UNKNOWN、PR/commit、新的完整结束状态。不自动合并。
5. 结束态正常：`BPTI_DEV27_BUGFIX_COMPLETE_TASK_CLOSED`；需人/超范围问题时：`BPTI_DEV27_BUGFIX_PARTIAL_TASK_CLOSED`，交付目前已完成的提交、明确问题和剩余工作后**完全结束当前任务**。**不得进入活跃中的wait/pause/checkpoint，玩家另开新的任务处理后续。**
6. 本修复**不会证明**逐CRC PlayType、Playbook实际比赛调用、30队真实GM运营、V4已启用或任何游戏变更。

## 5. 修复之后的BPTI顺序（本文件不自动启动）

玩家审核/批准合并DEV27 Draft PR后，**单独新任务**启动[DEV26](DEV_20261020_26_BPTI_GROUPED_CONTINUOUS_DELIVERY_AND_FOUR_FAMILY_EVIDENCE_V1.md)包B：`B2 NativeBinding → B3 TeamIdentity → 四家族2021前证据补充`，只用B-B1～B-B4四项最小检查，交付Draft PR，任务必须结束。B合并之后再独立触发包C：`B4 → B5 → B6`（C-C1～C-C5）。不在DEV27或包B内自动开始包C。

## 6. 已决定后置、不污染本次修复及B2–B6的扩展范围

玩家希望未来**让GM掌握全部可设置项的含义、候选、角色适配和使用方法，同时补齐逐场、球员、球队、伤病/高阶动态数据**，并继续扩大共享战术池的原生PlayType/CRC/动作受益人证据覆盖。这是BPTI之后独立的“全量可控项语义目录与GM使用手册/映射”及[DEV24](DEV_20261020_24_BPTI_ANTIGRAVITY_GAME_DATA_SOURCE_REQUIREMENTS_V1.md)等后续工程规划方向，**不是要求本次修复、更不是要求工作包B去穷尽所有1392条语义或执行游戏观察**。研究可信度维度保持独立，不能把名称推断标成原生类型认证。

## 7. 可复制的Codex触发指令

> **只启动DEV27独立、必须真正结束的Codex任务**。仓库`chris2gao/nba2k22-gm-engine`。玩家已批准修复`team_book()`的真实 `<Team> Playbook` 后缀匹配Bug及最多T1–T3三项直接相关静态检查；PR #10已合并。严格先读最新main `AGENTS.md`、`docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md`、`docs/development_tasks/DEV_20261020_27_BPTI_TEAM_BOOK_SUFFIX_MATCH_MINIMAL_FIX_V1.md`、DEV23报告及`src/gm_state_io/team_book.py`。仅精确支持末尾Playbook后缀，本队唯一性、owner、digest、rebind事件和实际审批边界不得变；不模糊匹配或修改其它组件、不启动B2–B6/DEV24、不访问或修改游戏、也不跑旧全套测试。完成最小代码+三项授权检查+验收报告，在独立分支发布Draft PR、终结任务回报`BPTI_DEV27_BUGFIX_COMPLETE_TASK_CLOSED`；若需人介入或额外授权，先提交可做成果及问题，返回`BPTI_DEV27_BUGFIX_PARTIAL_TASK_CLOSED`并**彻底结束任务**，绝不暂停等待。不得自动合并。
