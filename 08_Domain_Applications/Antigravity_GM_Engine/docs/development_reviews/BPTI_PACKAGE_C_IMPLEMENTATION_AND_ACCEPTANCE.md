# BPTI工作包C — B4/B5/B6实现与最小验收

日期2026-10-20。状态：BPTI_PACKAGE_C_COMPLETE_TASK_CLOSED。独立分支codex/bpti-package-c，交付Draft PR，未批准自动合并。

## 前置条件与范围

玩家批准PR #11合并后，main为04b194ab8b4644161242391e964051d3d9f9520a；本地main和origin/main已同步。包C单独从该主线启动，复用托管工作树；原E盘codex/season-match-history保留。权威范围为DEV22/DEV26/R4的B4→B5→B6，不包含DEV24、GM V4激活或实际30队经营。

仓库命令与五项检查在ADMIN=True的独立隐藏PowerShell执行。未打开游戏进程/活动数据库、未运行生产采集/游戏数据发布/存档推进/写入。

## 实际交付

- B4：gm_core/bpti_decision.py消费B0蓝图、B1/B2/B3日期过滤知识及M3密封DTO。当前技能角色、why_this_basketball、第一优势/反制/第二答案/自主权、身份与阵容/成本冲突进入真实D1–D6及原HOLD/INTERNAL/MARKET方案。内部动作须匹配支持候选；来源/知识/方向不明为HOLD，市场继续使用原M3缺口/内部比较。没有收益计算器或姓名巅峰规则。
- B5：gm_core/bpti_evolution.py实现六级候选演化记录、当前证据、前态体系/文化、保留与改变原因、教练适配、逆转条件。前态由CLI解析已有同career/同队不可变记录。文化延续优先，重构需长期和管理层语境；没有教练市场执行器或实际换帅。
- 现有decision_protocol与gm_decision新增submit-blueprint/record-evolution，复用decision_artifacts、run CAS、有界artifact/history和原导出。候选final/strategy带BPTI派生材料；不会自动保存正式M2状态或产生玩家批准。蓝图换版阻断旧评审/备选定稿。
- 选中动作仍走现有M3/DEV14纯规划，得到NOT_GRANTED的intent/approval tuple；不创建另一套数据库、市场、审批或内存执行器。更新AGENTS、33/34/36及GM手册索引。没有新原生能力或游戏来源，source_catalog/字段registry/执行白名单无需变动。

## 五项检查及结果

命令：python -B tests/test_bpti_package_c.py。最终 **Ran 5 tests in 17.700s — OK**。只引用旧测试模块的合成夹具，不运行其测试类或旧套件。

| 检查 | 实际覆盖 | 结果 |
|---|---|---|
| C-C1 | GSW Motion、CHI Creator/Midrange、MIA Defense-first三种合成体系有不同理由、角色和第二答案；可用知识裁剪；真实评估仍UNASSESSED | PASS |
| C-C2 | 真实M3 apply/store路径保存蓝图、D1–D6评审和三类备选；角色优先/机会成本、原市场内部比较门槛；蓝图换版后旧方案拒绝；历史版本保留，正式策略表无新增评定 | PASS |
| C-C3 | 合成历史姓名球星位于不同队，角色按该源可见技能；姓名不能替代技能；演化沿已有工作台追加并保留前态系统/文化，教练适配候选不自动重写文化，单月文化重构被拒 | PASS |
| C-C4 | 批次不符、RAW角色、早于历史证据、Tempo篮球方向未知均HOLD；实际CLI缺失源返回HOLD；不生成胜率/箱分预测 | PASS |
| C-C5 | 复用真实DEV14纯规划生成OFFLINE_PREPARED、未批准intent；合成源未变；Potential/OVERALL/Badge/unknown51/自由PlaybookID/无匹配槽动作不开放；伪批准与陈旧CAS拒绝，V4未启用、无真实30队评定 | PASS |

### 失败与直接修正记录

首次五项未通过（16.648s）：合成蓝图漏填B0必填status，返回HOLD。补齐后直接重跑五项（16.234s），暴露合成动作误用NATIVE_STATE（原M3契约为COACH_DEFAULT）及CLI测试导入路径遗漏。修正动作类型和导入路径时，一次进程在测试前因scripts/gm_state_io.py遮蔽包而退出；改为保留src优先级。最终五项通过。

另执行一次只读根因诊断，输出各蓝图的hold_reasons（BPTI_EXACT_OBJECT_CONTRACT_REQUIRED），不新增验收用例。没有已通过项目后的追加回归、性能/比赛效果测试、复跑旧套件或真实GM决策。各失败均保留临时管理员任务日志；修复直接对应已授权五项范围，未绕过保护。

## 交付限制

这是本地合成工程验收，不能声称真实生产GM消费、真实换帅/交易/签约、AI调用效果、赛场效果、存盘或游戏事实发布已验证。历史知识可读不等于本档阵容适配；当前缺失的精确CRC类型/受益人/ACE/调用频率/Tempo含义与比赛因果仍UNKNOWN。B4当前不从未知类型生成装载承诺，不改变底层既有同批全目录CRC、本队书及单独TEAM_BOOK_REBIND规则。

仍沿既有gm_core纯DTO、M3市场/M1财务、DEV14身份/字节校验/CAS/批准元组执行边界；Potential遮蔽不是球探能力，Intangibles只为既有软轮换例外，OVERALL只读。V3有效、GM_V4_NOT_ENABLED、实际30队UNASSESSED。源码分支/Draft发布与游戏数据-Publish分开。交付结束，不启动DEV24或后续任务。

## 源码交付位置

实现提交：da8a645d95602eb6cc244559599ebab66fa55231。

Draft PR：[PR #12](https://github.com/chris2gao/nba2k22-gm-engine/pull/12)，base main，head codex/bpti-package-c。未合并；后续仅补交付链接，不修改实现或追加测试。

## PR #12 玩家批准 F1–F4 最终修复（2026-10-20）

本节覆盖上方“后续仅补链接”的原交付结束点。已读取PR #12最新两条Web Development审查（UTC 2026-10-21 03:41:42 / 04:07:20，均针对9071cae）、磁盘AGENTS和相关M3源码。仅在原codex/bpti-package-c完成F1–F4，不引入DEV24/DEV28或新审批系统。

| 修复 | 实际实现和证据 |
|---|---|
| F1 | bpti_evolution.current统一检查当前蓝图revision/来源/球队/演化状态；validate给BPTI_EVOLUTION_STALE/BLOCK_FINAL，finalize和strategy_candidate再次拒绝陈旧演化。策略基底原BPTI当前字段先清除。合成完整路径：蓝图r1/演化r1→蓝图r2→r2评审/备选→validate失败、不能final/strategy→重新记录r2演化→validate/final成功，旧r1历史内容未变。 |
| F2 | 原前态同team/career检查保留，另核对齐全非空且相同的save_id/save_instance_id/generation_id及连续history_branch_context。CLI从原已存run恢复旧记录分支上下文；新记录自带该上下文。批次、snapshot、赛季变化允许；各身份冲突/缺失/不同分支HOLD。没有新增跨实例血缘桥接；同名标签本身不能认证世界线。 |
| F3 | 有效蓝图的DRAFT_UNAPPROVED与native_action_status分开；无支持动作只原生HOLD，MARKET不再自动BLOCKED。不支持的INTERNAL具体动作标BLOCKED/native HOLD；原M3内部人才缺口、财务引用/执行检查和双边同版谈判均未改。合成无动作与未知Tempo方向后，有GAP_REMAINS/内部比较证据的市场方案仍可提交offer，未回应仍NEGOTIATING；撤掉缺口证据继续被原门槛拒绝。 |
| F4 | decision_portfolio.resolve仅接纳category=INTERNAL、status=VIABLE_CANDIDATE且有具体action/当前备选版本的选定内部动作。BLOCKED/RESEARCH/NOT_APPLICABLE拒绝；inspect及select/validate复用该函数。研究引用和HOLD继续保留，无隐藏值补写。 |

针对性命令为python -B tests/test_bpti_pr12_fixes.py。首次入口直接导入了旧PackageCChecks类，unittest意外额外收集C-C1～C-C5：**实际Ran 9 tests in 42.500s，8通过，F3失败**。F1/F2/F4已通过，旧五项均通过；F3失败是新断言把原bilateral的NEGOTIATING误写为AWAITING_RESPONSES，未发现市场实现故障。随后改为模块引用以消除额外收集，并按原状态修正断言。

只复验失败的F3：python -B tests/test_bpti_pr12_fixes.py PR12FixChecks.test_F3_native_hold_does_not_veto_evidenced_market；**Ran 1 test in 17.169s — OK**。因此F1–F4均有对应通过证据；没有重跑已通过的F1/F2/F4，没有完整项目回归或游戏测试。原test_bpti_package_c中两个原生HOLD断言同步改用native_action_status，保留与F3新语义一致；本轮额外旧五项运行已如实记载，不能声称“仅运行四项”。

本轮只验证合成派生工作台，不证明实际生产GM、比赛、交易/签约执行、存盘或真实数据完整。当前没有可认证的跨实例历史桥接；实例/代次不符或证据不足时保持HOLD，不能凭career同名连接。无新数据库/审批/执行器、无游戏数据改动；V3有效/V4未启用、真实30队UNASSESSED。

后续权威规划为[DEV28主计划](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)：全量控制目录/合法值、实际Coach/Book/换帅归位/68槽、DEV24动态事实和完整执行读回均需下一独立玩家任务；本轮不实施，也不自动合并PR #12。

## PR #12 与最新main的最终冲突整理（2026-10-20）

本轮玩家仅授权主线同步、真实冲突修复、直接必要验证和原PR交付，不重新实现F1–F4。开始重新fetch远端main与codex/bpti-package-c：main为c68cb81f884cd9873d8f7b677d6e0ec1b608f423，PR为2f6591383ff1db8a51168eb84c40f2e357c57e6b，共同祖先04b194ab8b4644161242391e964051d3d9f9520a。初始GitHub状态CONFLICTING/DIRTY，仍Draft。

先从该main版本读取AGENTS、开发边界V2、游戏机制研究先行V1、状态34及DEV28主计划。遵守新永久规范；本任务属于纯Git冲突，不额外搜索游戏机制。

采用git merge --no-ff --no-commit origin/main；实际content冲突只有AGENTS.md与docs/33_DEVELOPMENT_BASELINE_PROMPT.md顶部新增说明。两个hunk均逐段合并：主线研究先行/DEV28授权与资料在前，PR的包C/F1–F4实现和历史记录继续保留，再加清楚的当前交付说明。没有对大型文档整文件选择ours/theirs。docs/34自动合并了双方内容，另加当前状态与资料入口。

main新规范、DEV28、十二类战术研究、共享池命名规则、DEV24来源要求与相关研究文件照原主线保留；PR的36执行基线、M3/BPTI手册、源码及两份合成测试照已审查版本保留。已有验收记录只追加本节，不改写历史结果。当前状态优先于下方旧“待修/未开始”的阶段说明。

本轮只做文档合并，因此不新增或重跑已通过的合成测试，也不做全项目回归。直接检查覆盖：无未解决冲突/残留标记；src/scripts/tests与2f659138无差异；main非重叠文件和PR非重叠文件内容保留；关键文档入口指向现存资料；原main及PR提交都是新merge的祖先。具体验证回执在本节后补。没有游戏进程/活动库访问、数据采集/发布、现金调查、存档或写入，没有DEV24/DEV28实现或V4启用。

终结状态BPTI_PACKAGE_C_MERGE_CONFLICT_RESOLVED_TASK_CLOSED。保留原PR #12、Draft，不自动合入main；下一阶段由玩家另行决定。

初次c68cb81快照的直接检查：python -B <临时目录>/check_merge.py为PASS；未解决index/冲突标记均0，src/scripts/tests对2f659138无差异，main独有9份文件及PR独有11份文件的Git内容保持一致，新增27个仓库文档链接均存在。本轮手动整理文件的git diff --cached --check通过；全量check显示的3个末尾空行均与main既有差异完全相同（DEV23研究、DEV28计划、DEVELOPMENT_CURRENT），保持主线原样，不扩展清理。玩家随后补充规范更新，最终仍将继续fetch并整合执行时最新main，以下此快照不代表最终main SHA。

### 玩家补充后最终主线：5c032a0

初次冲突保存为merge 1899d1a8da0ac91f4f43b7ca449f35f8f042e54a后，再次fetch得到最新main **5c032a0bdb8885cc34d1421952527457251522a9**，继续merge --no-ff --no-commit。增量只更新规范/交接文档；实际只有AGENTS标题相邻处再次content冲突，保留PR交付摘要并采用最新主线规范标题与完整正文；docs/33及其余规范自动合并。

最终保留的规范明确：先社区/攻略/官方手册理解游戏机制，次世代资料是高价值参考；具体PC菜单/枚举/对象/内存及执行路径再按PC原生来源核实。本轮仍纯Git/文档，不展开游戏资料检索、机制开发或DEV28。c68cb81段落是本轮第一次抓取快照，当前权威main为5c032a0。最新规范全文与主线一致，当前AGENTS/33/34的顶部交付说明同步更新。

最终5c032a0直接检查同样PASS：git ls-files -u为空；相关文件无冲突标记；git diff --exit-code 2f659138 -- src scripts tests为0，覆盖B4/B5→M3调用、F1当前演化版本/来源、F2存档/分支隔离、F3原生HOLD与市场分离、F4可行状态门槛的完整已审查源码。main独有9份、PR独有11份文件Git内容与各自来源一致；新增27个仓库文档链接目标均存在。手动整理文件git diff --cached --check通过；全量相对2f659138的3个EOF空行警告与04b194a→最新main的既有警告完全一致，未改主线原文。这些是本次Git/文档直接检查，不是重新认证比赛机制或重跑已有合成验收。

实际命令包括git fetch origin main codex/bpti-package-c、git merge-base、git diff --name-status、两次git merge --no-ff --no-commit origin/main，以及python -B <临时目录>/check_merge.py执行上述保留/链接/标记检查。后续正常push原分支，不force、不改写PR历史；GitHub合并状态以推送后的实时PR回执为准。
