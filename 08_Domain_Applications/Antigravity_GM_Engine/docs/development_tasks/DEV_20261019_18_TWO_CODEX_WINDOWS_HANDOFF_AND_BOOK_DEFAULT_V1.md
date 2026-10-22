
# DEV18 — 两个Codex窗口的所有权、接力与球队同名手册默认规则

**2026-10-19 · 最新用户确认 · 权威开发窗口调度指令。** 本任务只形成开发交接，不授权合并PR、真实游戏内存写入或生产数据采集。

## 一、严格区分两个开发模型窗口

| 工作窗口 | 已有独立成果 | 唯一代码负责范围 | 不应做的事 |
|---|---|---|---|
| **① DEV14底层Codex窗口** | [PR #5](https://github.com/chris2gao/nba2k22-gm-engine/pull/5)，`codex/dev14-state-io`；DEV14-A/B/C/D已实现，仍未合并 | SQLite三库、字段注册、读取与捕获、Potential后处理、原生Codec/Resolver、确定性`stage/validate/preflight/apply/receipt/reconcile`、人类审批/安全边界，向M3提供稳定数据与动作接口 | 不实施M3的30队篮球研究、战略候选、交易策略或教练文化决策 |
| **② M系列主线Codex窗口** | [PR #4](https://github.com/chris2gao/nba2k22-gm-engine/pull/4)，M3A/M3B已实现，Draft未合并 | M3A/M3B研究工作台、DEV13/M3-T战术决策与HOLD/INTERNAL/MARKET、阵容/教练/个人防守/轮换/训练/本队战术手册GM业务规则、交易市场与反馈 | 不重新建设DEV14采集器/SQLite/内存编码/玩家授权及第二套执行器 |
| **Antigravity后续扩展** | 本地独立原生资料 | 补CRC→真实战术知识、51未命名Tendency、位置训练模板、疲劳解码；实际某个原生入口卡住时提供最小修复 | 不为30队手册克隆、共享冲突做新的大规模专项，不替代DEV14底层 |

**重要：两个Codex是互相隔离的不同模型窗口，不能假定它们共享聊天上下文、Git分支或本地代码。** 用户负责触发对应窗口；以GitHub PR/commit + 交接文件传递事实。PR#4与#5均未合并，已有实现不能因为两人都说“完成”就当作正式main已支持。

## 二、窗口①交付清单：DEV14收尾，不碰M3决策

1. [DEV14-H](DEV_20261019_14H_DEV14_POST_REVIEW_HARDENING_V1.md)：pool/league/control同save、instance和generation来源，审批来源不能由执行模型自签；若无独立签发权限明确只能人工监督。
2. [DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)：每次`full_verified_v1`采集完成到正式发布前自动把**所有球员**Pot置1（结构化字段、JSON、PLAYER raw byte0x441），标MASKED；不可将GM脱敏`raw_struct`反向用于历史选秀写入。只处理入库数据，不修改游戏原生潜力。
3. DEV14原生受控能力注册`PLAYER_ROTATION_OVR_BIAS`：PLAYER intangibles byte0x440，25–99，是30队GM通用轮换策略字段；保留CAS/读回/玩家审批，不扩大原始Ability/Potential/Badge写权限，不做对其它游戏系统副作用研究。
4. 为GM暴露已实现Coach默认19项、Personal 18防守、已加载Playbook68槽/合法Book enum、球员四PlayTypes/48具名倾向、当前训练6+5项等**真实可用字段**；未知语义仍UNKNOWN。普通GM不写OVERALL与自由切BookID，只有新档或被确证换帅后`TEAM_BOOK_REBIND`可受控修改Coach PlaybookID，底层验证动作类型和独立玩家批准。
5. **交付必须有**`docs/development_reviews/DEV14_TO_M3_HANDOFF.md`：PR#5最终commit、schema/adapter版本、读取及稀疏intent字段示例、只读与可写清单、代码入口、定向测试、失败/未实现项、PR#4可能冲突的文件。不能把未证的“接口预留”说成已通过实际游戏验收。
6. 这轮继续在窗口①既有PR#5分支增量commit，**不在PR#5里写M3研究器**；PR#5合并由用户单独授权。

## 三、窗口②接收清单：M3系列主线，不碰底层

1. 接收到窗口①完成回执后读取`DEV14_TO_M3_HANDOFF.md`、PR#5最终commit与[DEV13](DEV_20261019_13_M3_TACTICAL_DECISION_INTEGRATION_V1.md)、[DEV17](DEV_20261019_17_CODEX_FIRST_MAINLINE_TEAM_BOOK_COACH_RULES_V1.md)。没有交接证据时不假定DEV15新字段已完成。
2. 建议PR#5完成定向测试并**经用户批准**先合并main；然后窗口②将main的新底层整合到PR#4分支，处理两PR修改`src/gm_data_access/query.py`和`scripts/gm_data_query.py`等文件的差异，跑M3 P1–P5定向回归。PR#4的合并也需要独立的用户授权。本任务书不自动合并。
3. 只利用DEV14 Observed、Registry及安全Desired合同，完成30队M3-T的教练/本队战术/球员能力/4PlayTypes/倾向/个人防守/已知训练/Intangibles分钟控制的分析与战略比较，并形成稀疏可执行意图；对未知战术名、未知51倾向、未解疲劳保持UNKNOWN，不伪造。
4. **制度**：每队每游戏赛季**仅休赛期最多主动换一名主教练**，该期只实现GM决策门禁与确认换帅事实后的球队Book恢复动作规划；完整员工合同/竞价/签约和自由市场阶段控制**后续单独开发**。
5. 普通GM仅写`PERSONAL_DEFENSE`、整体防守只读；本队战术书内容可按当前教练体系修改，日常不自由切书。
6. M3分析可以先开发不依赖新字段的部分，但**正式完整M3-T对接必须读取窗口①交付后的已实现接口**，不能在另一个分支另起数据底座。

## 四、用户提供的球队同名手册不变量：不再要求30队共享冲突研发

**用户明确保证**：新档30队通常各有对应自己队名的独立战术手册容器，外挂GM始终维持“球队→当前主教练→本球队同名手册”。因此**默认不存在跨队共用同一个可编辑书造成连带改动的问题**。

标准流程：A队/A教练/A书 → 休赛期A队签下B教练，游戏短暂变成A队/B教练/B书 → **经玩家批准，将A队当前B教练的PlaybookID恢复为已存在的A队同名书原生枚举ID** → 回读当前已绑定本队A书68槽 → 根据B教练和A队球员替换/添加A书槽位。B队手册保持不变。**业务上不切换战术书来调战术，只因换帅而恢复本队书**。

取消旧文档中将以下事项列为主线门禁的内容：
- Antigravity先完成30队各书的唯一性全面认证、克隆引擎、书容器创建/重新分配；
- 因假想的共享书事件而先阻塞整个DEV13/M3-T；
- 将“同名书共享冲突”作为必须开发才能开工的特殊工程模块。

**保留正常确定性执行安全检查**：按当前团队、游戏已加载Playbook名称与`enum_id/index/unique_id`取得目标A书，确认正确Team/Coach/Book源身份、原值、目标值、CAS与回读；不需逐本额外人工研究。若确实遇到“同名书不存在/匹配歧义/真实异常”则仅此动作BLOCKED，不修改别队，并视具体异常决定是否向Antigravity交小任务。这是异常处理而非新的默认研发范围。玩家假设≠“已完成30队原生验证”的实验报告，不得混称。

## 五、建议调度顺序

| 顺序 | 谁 | 只做哪些 |
|---|---|---|
| ① | DEV14窗口 | DEV14-H + Potential=1自动入库清洗 + Intangibles受控字段 + GM所需已知原生动作接口 + 交接清单 |
| ② | 用户人工闸门 | 审核PR#5及交接文档后决定是否允许合并main |
| ③ | M系列窗口 | 合入已授权的DEV14主线，解决PR#4差异、完成M3-T GM策略与Book归位流程、独立回归与后续PR |
| ④ | 用户人工闸门 | 审核PR#4/M3-T，以及后续正式游戏运行与GM V4启用 |
| ⑤ | Antigravity | 主线稳定后扩展倾向、战术知识及训练疲劳细分 |

任何窗口额度不够均只交一个小批次和可续commit，不把任务转给另一窗口随意续写；**窗口①专门维护底层，窗口②专门维护GM业务，GitHub文件和审阅验收是交接渠道**。

**本文件为当前双窗口调度的最高优先级说明，之前DEV16/17里“AG先完成Book独占研究”及“单个Codex窗口做全部B0/B1/B2”的表述应视为失效。**
