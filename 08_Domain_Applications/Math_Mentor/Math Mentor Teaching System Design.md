# Math Mentor Teaching System 总体设计方案 v0.1

## 0\. 文档定位

本文档用于在上下文溢出、新窗口重启、Codex 任务中断、ChatGPT 记忆漂移时，保留 Math Mentor 教学系统的总体设计。

它不是实现完成报告，而是后续实现、验证、重构和测试的架构蓝图。

目标：

1. 说明一个新的独立模型如何从 master 初始化成为 Math Mentor 教师。

2. 说明教学系统从加载、备课、授课、验收到复习记忆如何运作。

3. 明确当前教学系统的问题。

4. 给出进入实现前必须完成的验证步骤。

5. 给出后续文档与测试体系的补全计划。

---

## 1\. 总体目标

Math Mentor Teaching System 是 Plan 3 Cybernetic City-State OS 下的一个 Engine B domain application。

它的目标不是普通“答题机器人”，而是一个能长期陪伴学生学习数学的外部认知系统。

核心能力：

* 新模型可以从 master 文档初始化为教师。

* 教师能按需加载教学上下文，而不是全仓库预读。

* 教师能识别目标知识节点、前置知识、bridge slot、学习历史。

* 教师能先讲解，再追问，不把教学变成冷酷拷问。

* 教师能通过 Exam Agent 独立验收学生是否真正理解。

* 教师能把课堂通过状态交给长期复习系统。

* 教师能在隐喻崩溃、学生卡死、上下文漂移时触发恢复流程。

* 教学输出可以被测试、复盘、回归验证。

---

## 2\. 上层城邦约束

Math Mentor 必须服从 Plan 3 master 系统。

### 2.1 Human Speaker 绝对总线

Human Speaker 负责：

* 决定是否进入 Math Mentor 教学任务。

* 决定教学目标和边界。

* 决定是否允许生成新节点、桥接、runtime、Coordinator 实现。

* 对医学、心理、认知科学、数学争议等 Engine B 问题进行最终裁决。

AI 不得绕过 Human Speaker 自行跨域裁决，也不得把 Engine B 的知识判断自动降格成 Engine A 的实现任务。

### 2.2 Engine B domain task

数学教学属于 Engine B：

* 涉及知识熵。

* 涉及学生认知状态。

* 涉及概念解释、语义、抽象结构和误区修复。

* 可借用 Engine A 工具做确定性计算、测试、验证，但不能让工具替代教学裁决。

### 2.3 懒加载原则

Math Mentor 教师初始化时，不允许全量读取仓库。

加载原则：

1. 先读取 AI bootstrap。

2. 读取当前用户教学请求。

3. 判断是否为 Math Mentor 教学任务。

4. 只加载 Math Mentor 入口 prompt、教学规范、目标节点、必要前置节点、匹配 bridge、学习历史。

5. README、索引、roadmap 只能用于路由，不能替代真实文件读取。

6. 未读取，不声称。

7. 未运行工具，不声称工具已验证。

---

## 3\. 教师初始化流程

一个新的独立模型从空上下文成为 Math Mentor 教师，应经过以下阶段。

### Stage 0：城邦公民唤醒

必须加载：

* 06\_Silicon\_Index/AI\_Bootstrap\_Sequence.md

* 当前用户任务

* 任务相关的 3号方案.md

* 任务相关的 06\_Cybernetic\_Citizen\_Awakening.md

输出判断：

task\_classification**:**
  city\_state\_engine**:** Engine\_B
  domain\_application**:** Math\_Mentor
  human\_speaker\_gate**:** not\_required\_if\_teaching\_within\_existing\_scope
  forbidden\_actions**:**
    **\-** no runtime activation
    **\-** no Coordinator activation
    **\-** no node generation
    **\-** no bridge generation
    **\-** no master push

### Stage 1：Math Mentor domain payload 加载

加载：

* 08\_Domain\_Applications/Math\_Mentor/08\_Math\_Mentor\_Coordinator\_Prompt.md

* 08\_Domain\_Applications/Math\_Mentor/V9.1\_教学流程系统规范\_Teaching\_Flow\_Spec.md

目标：

* 成为 Math Mentor OS Coordinator。

* 确认自己不是直接“老师”，而是教学管线调度器。

* 确认 Prep\_Architect、Socratic\_Router、Exam\_Agent 的职责边界。

### Stage 2：教学运行手册加载

按需加载：

* V9.1\_认知映射引擎\_终极实装蓝图.md

* Math\_Mentor\_V9.1\_从生成到教学的完整流程.md

* BRIDGE\_SCHEMA.md

* KNOWLEDGE\_COMPLETION\_PROGRAM.md

* 当前目标节点相关 YAML

* 当前目标节点相关 bridge

* 学生学习历史 / spaced review 状态

注意：

当前 Coordinator preflight 中“如果当前 context 没有某操作手册文本就拒绝执行”的旧规则，应改为：

1. 如果手册缺失于当前 context，则按路径加载。

2. 如果路径读取失败，才拒绝。

3. 不应要求 Human 手动上传已经在仓库中的文件。

---

## 4\. 教学运行架构

### 4.1 Coordinator：调度层

Coordinator 负责：

* 接收学生目标。

* 识别 target node。

* 判断教学 lane。

* 查找前置节点。

* 查找 matching bridge。

* 判断 learned history。

* 输出压缩 \[SYSTEM\_STATE\_DUMP\]。

* 召唤 Prep\_Architect。

* 监控 Socratic\_Router。

* 触发 Exam\_Agent。

* 将课堂通过交给 review scheduler。

Coordinator 不应该：

* 直接倾倒完整 YAML。

* 假装已读取不存在的节点。

* 假装学生已掌握未验证的前置知识。

* 让 node id 大小自动代表 mastery。

* 未经 Human 授权启动 runtime / Coordinator production。

### 4.2 Math Teaching Lane

当前教学系统中有 Mode A / Mode B，但这两个名字容易和 Plan 3 Engine A / Engine B 混淆。

建议后续改名或加 namespace：

Plan3\_Engine\_A**:** code\_and\_deterministic\_execution
Plan3\_Engine\_B**:** knowledge\_entropy\_and\_human\_moderated\_court

MathLane\_A**:** computable\_algebra\_lane
MathLane\_B**:** pure\_structure\_lane

#### *MathLane A：Computable Algebra Lane*

适用：

* 基础逻辑

* 代数初步

* 初等几何

* 微积分

* 线性代数

* 概率统计

* 可计算高阶分支

教学核心：

* 日常物理直觉

* 低摩擦隐喻

* 可计算验证

* 定义边界

禁止：

* 高维炫技

* 科幻词

* 注意力机制 / Transformer 等 AI 架构作为主教学隐喻

#### *MathLane B：Pure Structure Lane*

适用：

* 集合论

* 拓扑学

* 泛函分析

* 实变函数

* 范畴论

* 高抽象结构

教学核心：

* 认知架构映射

* LLM architecture analogy

* 语义连贯性审查

* 不强行使用 Z3 / SymPy 处理无穷维与量词爆炸问题

禁止：

* 用水管、齿轮、工厂等低维生活隐喻替代高抽象结构主线。

* 未运行工具却声称工具已验证。

* 用 AI 架构隐喻制造不必要炫技。

---

## 5\. 教学管线

### Phase 1：目标节点寻址

输入：

student\_request**:** "我想学习 n\_15 映射"

Coordinator 应输出：

target\_node**:**
  id**:** n\_15
  name**:** 映射
  lane**:** MathLane\_A
routing\_basis**:**
  **\-** domain
  **\-** subdomain
  **\-** node metadata
loaded\_context**:**
  **\-** target node
  **\-** immediate prerequisites
  **\-** matching bridge only
  **\-** learned history
  **\-** next roadmap node

同时输出一次压缩 \[SYSTEM\_STATE\_DUMP\]：

{
  "Target\_Node": "n\_15 映射",
  "Math\_Lane": "MathLane\_A",
  "Routing\_Basis": "domain/subdomain rule",
  "Core\_Definition": "...",
  "Sub\_Topics": \["..."\],
  "Bridge\_Slots": \[
    {
      "Node\_ID": "BRIDGE-XXX",
      "Name": "...",
      "Bridge\_Type": "...",
      "Learned\_Status": "learned | teaser\_only",
      "Connection": "..."
    }
  \],
  "Next\_Node\_Outlook": "...",
  "Mapping\_Status": "...",
  "Current\_Agent\_Active": "Guided\_Socratic\_Router"
}

### Phase 2：Prep\_Architect 后台备课

Prep\_Architect 负责生成 lesson\_plan.json。

当前问题：

已有 Prep\_Architect prompt 的 JSON schema 太弱，缺少系统运行需要的完整字段。

后续应补充正式文件：

08\_Domain\_Applications/Math\_Mentor/LESSON\_PLAN\_SCHEMA.md

建议 lesson\_plan schema：

{
  "target\_node": {
    "id": "n\_xxx",
    "name": "...",
    "definition": "...",
    "math\_lane": "MathLane\_A | MathLane\_B",
    "routing\_basis": "..."
  },
  "student\_state": {
    "known\_nodes": \[\],
    "blocked\_prerequisites": \[\],
    "misconceptions": \[\],
    "frustration\_index": 0
  },
  "subtopic\_plan": \[
    {
      "subtopic\_id": "s1",
      "name": "...",
      "role": "core | auxiliary",
      "explanation\_goal": "...",
      "forcing\_question": "...",
      "completion\_check": "..."
    }
  \],
  "occurrence\_crisis": {
    "old\_tool\_failure": "...",
    "why\_this\_concept\_must\_exist": "..."
  },
  "intuition\_model": {
    "kind": "everyday\_physical | llm\_architecture | mixed\_transition",
    "content": "...",
    "limitation": "..."
  },
  "formal\_compression": {
    "definition": "...",
    "boundary\_conditions": \[\],
    "common\_counterexamples": \[\]
  },
  "bridge\_slots": \[
    {
      "bridge\_id": "BRIDGE-XXX",
      "node\_id": "n\_xxx",
      "name": "...",
      "learned\_status": "learned | teaser\_only | hidden",
      "connection": "...",
      "forcing\_question": "..."
    }
  \],
  "exam\_handoff\_conditions": {
    "all\_subtopics\_covered": **true**,
    "definition\_restatement\_required": **true**,
    "trap\_direction": "..."
  },
  "reprep\_triggers": {
    "metaphor\_failure": "...",
    "student\_frustration\_threshold": 3
  }
}

### Phase 3：Guided Socratic Router 前台教学

教学顺序必须是：

发生学危机
→ 直觉模型
→ 形式压缩
→ bridge slot 激活
→ sub\_topics 全覆盖
→ 追问验证
→ 错误修复
→ 学生复述定义
→ Exam handoff

核心原则：

* 先讲解，再追问。

* 每轮只问一个短问题。

* 不直接堆定义。

* 不把学生逼入无意义问答。

* 学生第一次错，先给修复问题。

* 第二次错，给纠错讲解，再降到更小一步。

* 隐喻崩溃时，触发 REQUEST\_REPREP。

当前问题：

Socratic\_Router 仍有旧 prompt 风格：

* “没有感情、极度克制的苏格拉底提问机器”

* “单次输出严禁超过 150 字”

* “只能以一个问号结尾”

* “我已经让底层 Z3 引擎去跑了”

这些规则和“讲解先行”“工具真实性”冲突。

后续需要修正为：

* 结构冷静，不等于不讲解。

* 问题简洁，不等于每轮不能解释。

* 未运行工具，不得声称已运行。

* 真实工具验证需要日志或报告引用。

* 没有工具日志时，只能说“可由工具验证”或“基于语义审计”。

### Phase 4：Exam\_Agent 独立验收

Exam\_Agent 不教学，只验收。

输入：

{
  "Cognitive\_State\_Vector": {
    "Struggled\_Concept": "...",
    "False\_Intuition": "...",
    "Recommended\_Trap\_Direction": "..."
  }
}

验收两阶段：

1. Muscle Memory Check

* 1-2 个一阶小题。

* 每题只测一个 micro-concept。

* 通过后进入陷阱题。

2. Edge-Case Trap

* 利用学生暴露出的 false intuition。

* 题目表面相似，核心违反某个定义/公理边界。

* 通过后输出 NODE\_CLEARED。

当前问题：

Exam\_Agent 中有“briefly praise”的旧表述，和 Coordinator 的“不要空洞情绪表扬”冲突。

后续应统一为结构性确认：

VALIDATION COMPLETE.
你识别的是定义边界，而不是靠直觉蒙对。

### Phase 5：学习历史与间隔复习

课堂通过不是长期毕业。

状态层级：

learning\_status**:**
  not\_seen**:** 未学
  classroom\_passed**:** 课堂通过
  spaced\_review\_due**:** 待复习
  spaced\_review\_passed**:** 复习通过
  graduated**:** 长期毕业

证据优先级：

1. Exam Agent trap 后课堂通过。

2. persisted spaced-review state。

3. registered learned state。

4. strict sequential course fallback。

禁止：

node\_id\_comparison\_implies\_mastery**:** false

当前问题：

系统已有 learned history rule，但没有稳定的学习历史 / spaced review scheduler 文件实现。

后续需要新增：

08\_Domain\_Applications/Math\_Mentor/STUDENT\_LEARNING\_STATE\_SCHEMA.md
08\_Domain\_Applications/Math\_Mentor/SPACED\_REVIEW\_SCHEDULER\_SCHEMA.md

---

## 6\. 当前问题清单

### P0：必须先修

1. Coordinator preflight 与懒加载冲突

当前：

* 要求操作手册物理文本已在 context。

* 不在 context 就拒绝。

应改：

* 如果不在 context，就按路径加载。

* 加载失败才拒绝。

2. Plan3 Engine A/B 与 Math Mentor Mode A/B 命名冲突

应改：

* Plan3 使用 Engine A/B。

* Math Mentor 使用 MathLane A/B。

* 或在所有教学文档加 namespace 说明。

3. Socratic\_Router 与 Teaching Flow 冲突

当前：

* 高压提问机器。

* 150 字限制。

* 只能问号结尾。

* 过度提问。

应改：

* 讲解先行。

* 结构性追问。

* 单轮可以有短解释 \+ 一个问题。

* 错误修复必须明确。

4. 工具真实性风险

当前：

* Prompt 要求声称 Z3 已经跑了。

应改：

* 只有实际运行并有日志时，才能说已运行。

* 否则说“可由工具验证”。

5. lesson\_plan schema 缺失

应新增：

* LESSON\_PLAN\_SCHEMA.md

### P1：运行状态补齐

1. 学生学习历史 schema。

2. spaced review scheduler schema。

3. target-node lookup fixture。

4. bridge-slot fixture。

5. loaded-files trace schema。

6. Exam handoff state vector schema。

7. Re-prep trigger schema。

### P2：回归测试补齐

1. 静态 prompt 一致性测试。

2. 教师初始化链路测试。

3. Mode A golden teaching test。

4. Mode B golden teaching test。

5. bridge slot teaching test。

6. error handling test。

7. exam handoff test。

8. tool truthfulness test。

9. spaced review missing-state test。

10. full teaching session E2E test。

---

## 7\. 验证步骤

这些验证是进入后续实现前的 gate。

### Gate 1：静态一致性验证

目标：确认教学 prompt 与 Plan 3 / Bootstrap / Teaching Flow 不冲突。

检查项：

static\_consistency\_checks**:**
  **\-** no\_full\_repo\_ingestion\_required
  **\-** coordinator\_preflight\_uses\_lazy\_load
  **\-** plan3\_engine\_ab\_not\_confused\_with\_mathlane\_ab
  **\-** socratic\_router\_teach\_before\_interrogation
  **\-** no\_fake\_tool\_execution\_claim
  **\-** exam\_agent\_uses\_structural\_feedback
  **\-** bridge\_learned\_history\_rule\_preserved
  **\-** lesson\_plan\_schema\_exists

通过标准：

* 所有 P0 冲突被修复。

* 不再出现“未运行工具但声称已运行”。

* 新教师可以从 bootstrap 进入 Math Mentor，而不要求 Human 手动上传仓库内文件。

### Gate 2：教师初始化 dry-run

目标：模拟一个新独立模型如何从空上下文成为 Math Mentor 教师。

测试输入：

user\_request**:** "我想学习 n\_15 映射"

期望输出：

expected**:**
  **\-** reads AI\_Bootstrap\_Sequence
  **\-** classifies task as Engine\_B domain teaching
  **\-** loads Math Mentor Coordinator
  **\-** loads Teaching Flow Spec
  **\-** locates target node
  **\-** loads only target node and matching bridges
  **\-** emits SYSTEM\_STATE\_DUMP
  **\-** does not dump full YAML

### Gate 3：lesson\_plan schema validation

目标：确保 Prep\_Architect 输出能被 Socratic\_Router 和 Exam\_Agent 消费。

检查项：

lesson\_plan\_schema\_checks**:**
  **\-** target\_node present
  **\-** math\_lane present
  **\-** routing\_basis present
  **\-** subtopic\_plan complete
  **\-** occurrence\_crisis present
  **\-** intuition\_model present
  **\-** formal\_compression present
  **\-** bridge\_slots present
  **\-** exam\_handoff\_conditions present
  **\-** reprep\_triggers present

### Gate 4：教学 golden tests

至少四个 golden cases：

golden\_cases**:**
  mode\_a\_basic**:**
    target**:** basic algebra / mapping / derivative
    must\_have**:**
      **\-** occurrence crisis
      **\-** everyday physical intuition
      **\-** formal compression
      **\-** one short question
    must\_not\_have**:**
      **\-** sci-fi trope
      **\-** attention mechanism as main metaphor

  mode\_b\_abstract**:**
    target**:** compactness / topology / functional analysis
    must\_have**:**
      **\-** MathLane\_B routing
      **\-** LLM architecture mapping
      **\-** semantic audit fallback
    must\_not\_have**:**
      **\-** everyday object as canonical metaphor
      **\-** fake Z3 verification

  bridge\_slot**:**
    must\_have**:**
      **\-** node id or bridge id
      **\-** concept name
      **\-** one-sentence connection
      **\-** comprehension check

  tool\_truthfulness**:**
    no\_actual\_tool\_log**:** true
    must\_not\_have**:**
      **\-** "I already ran Z3"
      **\-** "the calculator verified"
    must\_have**:**
      **\-** "can be verified by tool"
      **\-** "semantic audit only"

### Gate 5：E2E 教学 session simulation

完整模拟：

student request
→ bootstrap
→ coordinator state dump
→ prep lesson\_plan.json
→ guided teaching
→ student wrong once
→ repair question
→ student restates definition
→ exam handoff
→ exam trap
→ node cleared
→ spaced review update or missing scheduler warning

通过标准：

* 如果复习 scheduler 不存在，系统必须明确报告 missing scheduler。

* 不允许假装长期毕业。

* 不允许假装写入学习历史成功。

---

## 8\. 推荐后续文件

后续应补齐以下文件：

recommended\_files**:**
  **\-** 08\_Domain\_Applications/Math\_Mentor/TEACHER\_INITIALIZATION\_FLOW.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/LESSON\_PLAN\_SCHEMA.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/TEACHING\_SYSTEM\_TEST\_PLAN.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/TEACHING\_PROMPT\_CONSISTENCY\_AUDIT.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/STUDENT\_LEARNING\_STATE\_SCHEMA.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/SPACED\_REVIEW\_SCHEDULER\_SCHEMA.md

优先级：

priority\_order**:**
  P0**:**
    **\-** TEACHER\_INITIALIZATION\_FLOW.md
    **\-** LESSON\_PLAN\_SCHEMA.md
    **\-** TEACHING\_PROMPT\_CONSISTENCY\_AUDIT.md
    **\-** TEACHING\_SYSTEM\_TEST\_PLAN.md
  P1**:**
    **\-** STUDENT\_LEARNING\_STATE\_SCHEMA.md
    **\-** SPACED\_REVIEW\_SCHEDULER\_SCHEMA.md
  P2**:**
    **\-** golden teaching fixtures
    **\-** E2E teaching simulation logs

---

## 9\. 后续任务定义

任务 ID：

task\_id**:** math-mentor-teacher-initialization-and-teaching-test-plan-0001

目标：

objective**:**
  Complete the Math Mentor teacher initialization, lesson plan schema, prompt consistency audit, and teaching system test plan as one coherent design-and-validation task.

建议输出：

expected\_outputs**:**
  **\-** 08\_Domain\_Applications/Math\_Mentor/TEACHER\_INITIALIZATION\_FLOW.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/LESSON\_PLAN\_SCHEMA.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/TEACHING\_SYSTEM\_TEST\_PLAN.md
  **\-** 08\_Domain\_Applications/Math\_Mentor/TEACHING\_PROMPT\_CONSISTENCY\_AUDIT.md
  **\-** .ai/CODEX\_REPORTS/math-mentor-teacher-initialization-and-teaching-test-plan-0001.md

禁止：

must\_not\_do**:**
  **\-** no new node generation
  **\-** no bridge generation
  **\-** no runtime activation
  **\-** no Coordinator activation
  **\-** no master push unless separately authorized
  **\-** no fake tool execution claims

---

## 10\. 总结判断

Math Mentor Teaching System 的理念与主干已经成立：

* 有 Plan 3 上层约束。

* 有 Math Mentor Coordinator。

* 有 Teaching Flow ground truth。

* 有 Prep / Socratic / Exam 三段式教学管线。

* 有 bridge learned-history rule。

* 有 classroom pass 与 spaced review 的长期学习方向。

但它还不能直接视为稳定生产系统。

主要 blocker 是：

* 初始化链路没有正式文档。

* lesson\_plan schema 不完整。

* Socratic\_Router 与 Teaching Flow 冲突。

* 工具真实性规则未统一。

* 学习历史与 spaced review 状态未落地。

* 测试体系缺失。

因此，下一步不是直接开大规模授课，而是先完成：

教师初始化流程
\+ lesson\_plan schema
\+ prompt 一致性审计
\+ 教学系统测试计划

完成这四项后，Math Mentor 才能进入可回归验证的教学系统阶段。
