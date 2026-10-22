# BPTI B0 — 实现与最小验收

2026-10-20。状态：**BPTI_B0_ENGINEERING_COMPLETE_AWAITING_PLAYER**。
独立分支：codex/bpti-b0-knowledge。交付形态：独立 Draft PR，不自动合并。
基线：最新 origin/main 的 6af12ba6167c82bd1040138ad53180ba38902b11。
本报告描述本分支实现，不声称 main 已合并/部署或正式 GM 已启用。

## 1. 授权和阶段顺序

玩家本次明确授权 B0 代码、必要知识接口、文档、三项静态验证和独立 Draft PR。
已按最新 DEV22 执行：B0 → 玩家审核/批准 B1 → DEV23 → B2 → B3 → B4 → B5 → B6；
DEV24 后置。原 DEV19 的并行建议不覆盖 DEV22 最新顺序。
遵守 PLAYER_DEVELOPMENT_POLICY_V2；没有提出或执行范围外扩展/追加验证。

## 2. 交付与证据

| 要求 | 本次实现 | 直接证据 |
| --- | --- | --- |
| 四种最小知识对象 | TypedDict + 精确字段/类型/状态/家族/证据引用运行时校验 | src/gm_core/bpti.py：SystemCard、TeamIdentity、NativeBinding、SystemBlueprint、validate_bpti_knowledge |
| 可追溯研究索引 | 91 个 Source、40 个最小 Claim；R1 十家族主引、R2 原三十队 Claim；永久 URL/原文行定位及补录状态 | web_gm/knowledge/bpti/research_source_index.json；scripts/build_bpti_research_index.py |
| 2021 历史知识边界 | 普通 GM 默认投影、显式游戏日期、2021-10-19 上限、具体事件时间/已知时间、回顾性早期事实提取；隐藏未来或时间未知正文 | ResearchIndex.claim/availability/source/reference_evidence |
| 思想/创造力/原生三层 | 完整优势链和五种 agency；NativeBinding 仅语义候选/方向性证据及 UNKNOWN，不生成数值/字节 | 四种契约及 docs/BPTI_KNOWLEDGE_CONTRACT_V1.md |
| 复用 M2/M3/DEV14 | Knowledge.bpti()、原 gm_knowledge CLI；投影现有 reference_evidence；Blueprint 复用 M3 packet/source/team/coach/role 引用；DEV14 不变 | src/gm_core/knowledge.py、scripts/gm_knowledge.py、契约第5节 |
| 轻量可运行实现 | 文件索引 + 纯 Python 校验，无新库/schema/执行器或新的 GM 编排 | 本分支代码；三项实际静态检查 |
| 文档/基线 | 新契约/本报告，更新 AGENTS、33、34、现有 M2 手册 | 本次 Git diff |

正式 SOURCE registry / 采集基线32 / 执行能力表没有新能力需要登记：
B0没有增加游戏观测来源或执行字段，只增加研究引用合同。既有状态和执行白名单保留。

## 3. 实际验证：仅三项，一次运行

命令（本工作树实际执行）：

~~~powershell
python -B scripts/check_bpti_b0.py
~~~

结果：**Ran 3 tests in 0.092s — OK**，退出码 0。

1. test_01_missing_or_unreviewed_source_cannot_be_verified：实际加载 M2/B0 索引；
   缺失/未审阅出处不能升 VERIFIED；R1/R2 最小引用齐全、LAL-S2/POR-S2 保持缺源，
   查询经过现有 CLI 入口，临时 GPT token 未作为永久索引。
2. test_02_future_nba_events_hidden_but_earlier_retrospective_facts_allowed：
   合成 2022 事件在 2021 视图隐藏；游戏日期推进至2026仍不自动解锁真实未来；
   2023发表但明确提取的2014事实可以读取，未拆分的真实 BOS 复合研究引用不进入先验；
   M3 引用投影和 Source 查询不输出未来正文。
3. test_03_four_contracts_cannot_carry_native_writes_or_approval：
   四类 DTO 的纯研究形状可校验；嵌入 native_intent/raw/address 或 approved 被拒绝；
   单凭篮球 Claim 不能冒充已证原生字段支持。

合成日期/角色/Blueprint仅用于这三项静态合同检查，不是本局事实或正式篮球建议。
没有重跑通过项目、追加测试、编译/lint 扫描、旧 M3/DEV14 集合或实机验证。

生成研究索引属于交付数据构建，已实际运行；不是一次额外游戏/篮球统计验证。
源文件差异审阅/Git提交/PR状态读取属于交付操作，不计作新测试轮次。

## 4. 证据等级与真实限制

- 91个Source是归档引用，非91个已重新访问、逐篇认证的网页。
  Source有URL不自动认证Claim；本任务没有另做外部文献核验。
- 40个Claim是可回查的复合研究结论，不是B1十张完整可检索卡或B3三十队正式身份。
  尚未逐子命题拆分事件/已知时间，保留UNKNOWN或SOURCE_MISSING；
  因此普通GM消费不会直接获得整段复合历史，B1/B3再按范围提取更细的可用Claim。
- ATL-S1为等价补充；ATL-S2只支持教练组，不证明长期组织文化。
  LAL-S2确切原文未恢复，非等价替代网页不填其URL。
  POR-S2在R2引用中出现但原索引/补录均未登记，保持SOURCE_MISSING。
- NativeBinding只建立合同，未完成B2映射；CRC→动作/受益人、ACE行为、Tempo含义、
  51未知倾向、3D与Calendar差异仍未证。本阶段没有执行DEV23调查。
- M3消费函数是opt-in接口，B4正式插入D1–D6尚未实施；
  不把仅有MASKED文本当来源认证，上游仍由require_gm_sanitized提供可信包。
- 没有更改比赛、球员能力、Potential、Desired、审批记录、游戏日期或正式赛季档案。
  没有访问游戏、采集/发布真实数据、创建存档或启动正式GM。V3继续有效、V4未启用、
  实际三十队策略仍UNASSESSED。

## 5. B1 可复用与下一步

可复用：

- SYSTEM_IDS、AGENCY、完整优势链和四种 TypedDict；
- validate_bpti_knowledge、ResearchIndex 的来源认证/时间/非执行载荷约束；
- Knowledge.bpti() 及原脚本 bpti-contract / bpti-source / bpti-claim / bpti-validate；
- 研究索引的稳定claim_id/source_id和原R1/R2/补录行定位；
- M3 reference_evidence 的 bpti-claim:<id> 投影接口。

B1获批后可以实现十家族精简检索卡，拆出明确历史时间的知识命题，保留角色/反制/
再反制/机会成本和UNKNOWN；不需要重建数据或执行平台。
本报告不授权该阶段。**B0完成后停止，等待玩家审核并明确批准启动B1。**
