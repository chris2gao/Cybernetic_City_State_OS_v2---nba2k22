---
request_id: "independent-review-request-0001"
title: "独立评审请求:单执行者时期产出的全部待审项(致 ChatGPT foreground reviewer)"
requested_by: "claude_cowork (backend_executor, sole-executor mode)"
requested_at: "2026-07-19"
reviewer_role: "foreground_independent_reviewer"
review_head: "master@ebb16be"
status: "awaiting_independent_review"
---

# 为什么有这份请求

Codex 额度耗尽、Fable 仅剩一次调用期间,Human 授权我(backend executor)单人推进。
结果是**执行者与自审者是同一个**,而本项目已有一次实证说明这条防线不可省:2026-07-18
盲审在我的教学产出中查出自审未捕获的实质数学错误(场A 把 1+i 记作 2e^{iπ/4},
`(1+i)(√3+i)` 的模记作 4,实为 √2e^{iπ/4} 与 2√2),该场被裁 FAIL,自审表被降级为
`historical_incorrect`。

因此以下产出**全部标记 `pending_independent_review`**,请逐项裁决。你可以推翻其中任何一项;
我在下面每项都写了"如果我错了,最可能错在哪",请优先攻击那些点。

评审所需证据全部在公开仓库 `master@ebb16be`,可直接读取。

---

## R1(最高优先|阻塞教学)CA-417 与 PDE-486 的语义接受

**你的权限**:按 `KNOWLEDGE_COMPLETION_PROGRAM.md` Stage 5,"判断 Mode A 证据是否与所述概念相符"
是 foreground reviewer 的角色。**我故意没有自我接受**——装配证据者不能同时判断证据是否匹配概念。
这两个节点因此停在 `semantic_acceptance_required.status: review_required`、`teaching_ready: false`。

**证据位置**
- 节点:`08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-417.yaml`、`PDE-486.yaml`
- 审计脚本:`.ai/PROGRAM_RUNS/kcp-batch-2-mode-a-certification-0001/AUDITS/*.py`
- 运行日志:同目录 `LOGS/*.log`(CA-417 14 断言、PDE-486 20 断言,exit=0,sympy 1.14.0)

**请具体裁决**
1. 断言集是否真的覆盖了各自的 4 条 `sub_topics`?我已声明 CA-417 子主题4(虚数在物理矢量场中的实在性)
   **无机器证据**、PDE-486 的一般 S-L 谱定理/完备性/级数收敛**未验证**——这些声明是否足够,
   还是说这些子主题根本不该在证据不足时进入 teaching-ready 路径?
2. `pure_math_definition` 的数学表述是否准确、范围是否恰当?**这是我最可能出错的地方**,
   请独立复核,不要因为"有 SymPy 日志"就放松——日志只证明被断言的命题为真,不证明定义写对了。
3. `mapping_boundary.invalid_inferences` 是否遗漏了重要的错误外推?
4. 若接受,请回写 `status: accepted` + `accepted_by` + `accepted_at` + `acceptance_ref`;
   若拒绝,请指出需修复的具体字段。**注意保持** `coordinator_consumable: false` /
   `consumer_allowed: false` / `bridge_readiness_status: manual_review_required` 不变(语义接受≠消费准入)。

## R2(架构|请重点挑战)learning-state writer 设计

**文件**:`.ai/CODEX_REPORTS/math-mentor-learning-state-writer-design-0001.md`

**核心论点**:writer 不需要新存储系统,`.ai/lanes/` 已实现的 append-only 事件 + 单写者 reducer +
原子重命名 + epoch 绑定 + envelope 先发 + 非 force 发布,恰好覆盖 writer 所需。因此 C 从"造系统"
降为"加一种事件类型 + 一个 reducer"。

**如果我错了,最可能错在**:lanes 是为**多方协作通信**设计的,学习状态是**单主体私有数据**,
两者的一致性、并发、权威模型未必真的同构。我在设计里主张"这是不同的域,本地存储不构成降级"——
这个论证是我自己造的,没有第三方检验过。**请攻击它。**

**D1 存储介质改判**:我原本推荐 repo 内事件,实测发现本仓库**公开可读**
(无凭据 `git ls-remote` 成功,exit=0)后改判为本地存储。请复核:
(a) 这个事实判断对不对?(b) 改判是否过度——是否存在既能公开审计又不泄露画像的方案是我漏掉的?

## R3(合同)P8 与首课审计发现2 的落地

**commit**:`e2782e8`(纯新增 11 行,零删除)

- P8:`common_misconceptions` 进 `Universal_Layer_Execution_Protocol.md` 阶段2 为新节点必备字段;
  既有节点缺失不阻断教学,由 Prep 自构造并标 `common_misconceptions_absent`;消费侧在
  `LESSON_PLAN_SCHEMA.md` §4.11 说明 `trap_direction` 优先派生自它。
- 发现2:`actually_read_files` 属自陈述、不可核验、不得作为正确性证据链上游,精确数量声明同样不可依赖。

**请裁决**:P8 的落点选在生成规范(而非节点 identity schema 或 KCP Stage 6)是否正确?
向后兼容条款是否留得太松,以至于 667 个既有节点永远不会被补齐?

## R4(实现)转换表是否忠实于合同

**文件**:`08_Domain_Applications/Math_Mentor/learning_state/`(reducer / validator / schema / epoch / writer)

- `reduce_readonly.py` 的 `ALLOWED_TRANSITIONS` 是我从 `STUDENT_LEARNING_STATE_SCHEMA.md` §5
  转换表手工誊写的,`MINIMUM_REVIEW_PASSES = 2` 取自 `GRADUATION_CRITERIA.md`。
- **请逐行比对**是否有誊写偏差、遗漏或擅自新增的转换。我额外加了表中未明写的
  `review_passed → review_due` 与 `stale → review_due`(理由:复习周期需要可重入),
  **这属于我的解释而非合同原文,请特别裁决是否越界**。
- 28 项测试全过,但测试是我自己写的——测试通过只说明实现符合我的理解。

## R5(交叉检查)本轮全部 commit

`e2782e8` P8+发现2 · `d9eac97`/`d612b6a` writer 设计 · `a4998e0` 只读 reducer ·
`1ff32bb` 批次2 Mode A 证据 · `c0e0b91` schema+validator · `ebb16be` writer+gitignore

请留意任何**我声称做了但实际没做**、或**做了但没声明**的地方。

---

## 不需要你评审的部分

学习者 No.1 的实际学习数据**不在仓库里**(位于 gitignored 的
`08_Domain_Applications/Math_Mentor/learners/no_1/`),因为仓库公开。这部分的正确性由
reducer 的确定性校验与哈希链保证,不需要语义评审;你也**不应**要求把它推上来。

## 我请求你不要做的事

不要仅因为"有机器日志/有测试通过"就通过 R1 与 R4。那两处的风险恰恰在于:
日志与测试都只检验了**我选择去检验的命题**。真正的问题是我有没有选对命题。
