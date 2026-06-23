## 1. 当前判断

可以细化，而且应该按 **LRP / Long-Run Program** 拆，而不是按“文件小任务”拆。

这里的拆分原则是：

```yaml id="split_principle"
split_principle:
  不是:
    - 创建一个文件一个任务
    - 修一个 prompt 一个任务
    - 写一个测试一个任务
  而是:
    - 每个长期任务都有独立目标
    - 每个长期任务都能持续运行
    - 每个长期任务都包含读取、设计、实现、验证、报告、handoff
    - 每个长期任务最后形成可审查成果
```

依据上，当前 master 的 `AI_Bootstrap_Sequence.md` 已经规定新模型启动时先判断 Engine A / Engine B / Human gate，并且只加载当前任务所需的最小上下文，不能全仓库预读。
Math Mentor 的教学规范也已经定义了教学双轨、Coordinator、Prep_Architect、Guided Socratic Router、Exam Agent 的四段教学管线。
Coordinator prompt 也明确了 target node lookup、bridge filtering、learned history、compressed state dump、讲解先行和 Exam handoff 等核心机制。

所以可以把教学系统后续拆成 **6 个长期任务**。

---

## 2. 推荐拆分：6 个独立长期任务

### LRP-01：教师初始化与上下文加载系统

```yaml id="lrp_01"
task_id: math-mentor-lrp-01-teacher-initialization-context-loading
priority: P0
status: planned
```

目标：定义一个新独立模型如何从 Plan 3 master 初始化为 Math Mentor 教师。

它解决的问题是：新模型不能靠旧上下文记忆，也不能全仓库预读。它必须知道从哪里开始、读哪些文件、什么时候进入 Math Mentor、什么时候停下来。

主要产物：

```yaml id="lrp_01_outputs"
outputs:
  - 08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md
  - 08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md
  - 08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md
```

核心内容：

```yaml id="lrp_01_scope"
scope:
  - Plan 3 bootstrap -> Math Mentor payload 的加载链
  - Engine B domain teaching 判断
  - Math Mentor Coordinator 初始化
  - Teaching Flow Spec 加载
  - target node / prerequisite / bridge / learned history 的最小加载规则
  - context boundary / drift recovery / new window reload
```

必须验证：

```yaml id="lrp_01_validation"
validation:
  - 新模型能从空上下文加载为 Math Mentor teacher
  - 不要求 Human 手动上传仓库内已有文件
  - 不全量读取 Math Mentor 目录
  - 能输出 actually_read_files
  - 能输出 compressed SYSTEM_STATE_DUMP
```

当前已知 blocker：Coordinator preflight 仍要求 `V9.1_认知映射引擎_终极实装蓝图.md` 已经物理存在于当前 context，不存在就拒绝继续。这个和懒加载冲突。
因此 LRP-01 必须修掉这个旧前提。

---

### LRP-02：Lesson Plan Schema 与 Agent Contract 统一

```yaml id="lrp_02"
task_id: math-mentor-lrp-02-lesson-plan-agent-contract
priority: P0
status: planned
```

目标：把 Coordinator、Prep_Architect、Socratic_Router、Exam_Agent 之间传递的 `lesson_plan.json` 变成正式协议。

它解决的问题是：现在教学系统有 pipeline，但 agent 之间共享的数据结构不够硬。Prep 生成什么、Socratic 消费什么、Exam 需要什么、bridge slots 怎么传、sub_topics 怎么覆盖，都需要统一 schema。

主要产物：

```yaml id="lrp_02_outputs"
outputs:
  - 08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md
  - 08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md
  - 08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md
  - 08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md
```

核心内容：

```yaml id="lrp_02_scope"
scope:
  - target_node schema
  - math_lane routing schema
  - subtopic_plan schema
  - occurrence_crisis schema
  - intuition_model schema
  - formal_compression schema
  - bridge_slots schema
  - learned_history reference
  - exam_handoff_conditions
  - reprep_triggers
```

必须验证：

```yaml id="lrp_02_validation"
validation:
  - Prep_Architect 输出能被 Socratic_Router 消费
  - Socratic_Router 能覆盖全部 sub_topics
  - Bridge slot 首次出现时必须展示 node id/name/connection
  - Exam handoff 必须包含高分辨率 Cognitive_State_Vector
```

依据：Teaching Flow 明确要求 Prep 生成 `lesson_plan.json`，提取 `sub_topics`，执行 graph backtracking，并把 `BRIDGE-XXX.yaml` 作为关联插槽嵌入剧本。
Coordinator prompt 也已经定义了 state dump 的字段形状，包括 Target_Node、Mode、Routing_Basis、Sub_Topics、Bridge_Slots、Next_Node_Outlook、Mapping_Status。

---

### LRP-03：教学 Prompt 一致性修复

```yaml id="lrp_03"
task_id: math-mentor-lrp-03-teaching-prompt-consistency-repair
priority: P0
status: planned
```

目标：修复 Teaching Flow、Coordinator、Prep、Socratic、Exam 之间的冲突，让所有 prompt 统一到“讲解先行 + 工具真实性 + Plan 3 懒加载”。

它解决的问题是：现在教学系统的主干规范已经升级，但部分子 prompt 还残留旧规则。

主要产物：

```yaml id="lrp_03_outputs"
outputs:
  - 08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md
  - 修正后的 Coordinator Prompt
  - 修正后的 Prep_Architect Prompt
  - 修正后的 Socratic_Router Prompt
  - 修正后的 Exam_Agent Prompt
```

重点修复：

```yaml id="lrp_03_scope"
scope:
  - Coordinator preflight 改为 lazy-load，而不是要求上下文预先存在
  - Plan3 Engine A/B 和 Math Mentor Mode A/B 命名隔离
  - Math Mentor Mode A/B 建议改名为 MathLane A/B
  - Socratic_Router 从高压拷问改为 teach-before-interrogation
  - 删除或改写 fake tool execution claims
  - Exam_Agent praise 改成 structural confirmation
```

当前已知冲突：

Socratic_Router 仍然自称“没有感情、极度克制的苏格拉底提问机器”，并要求单次输出不超过 150 字、只能以一个问号结尾。
但 Coordinator 明确规定 primary objective 是从直觉走向形式定义，必须先提供 compact explanatory bridge，然后再问一个 forcing question。

还有一个更严重的工具真实性风险：Socratic_Router 要求在涉及代数推演时主动宣告“我已经让底层 Z3 引擎去跑了”。
这个必须改成：**只有真实工具运行并有日志时，才能说已运行；否则只能说“可由工具验证”。**

必须验证：

```yaml id="lrp_03_validation"
validation:
  - 不再要求普通 teacher 全量预读
  - 不再有 fake Z3/SymPy/PyTorch execution claim
  - Socratic_Router 不再覆盖 Teaching Flow 的讲解先行原则
  - Mode 命名不会和 Plan 3 Engine A/B 混淆
  - 所有 prompt 服从 AI_Bootstrap_Sequence 的懒加载与 Human Speaker 权力边界
```

---

### LRP-04：教学测试系统与 Golden Cases

```yaml id="lrp_04"
task_id: math-mentor-lrp-04-teaching-test-harness-and-golden-cases
priority: P0/P1
status: planned
```

目标：建立可回归验证的教学测试系统，防止 prompt 改一次坏一次。

它解决的问题是：现在 Teaching Flow 有测试 oracle，但还没有系统化测试计划、fixtures、golden outputs、E2E simulation logs。

主要产物：

```yaml id="lrp_04_outputs"
outputs:
  - 08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md
  - 08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md
  - 08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_TEST_FIXTURES.md
  - 08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md
```

测试层级：

```yaml id="lrp_04_tests"
test_layers:
  static_consistency_tests:
    - no full repo ingestion
    - no fake tool execution
    - no Mode naming confusion
    - teach-before-interrogation preserved

  initialization_dry_runs:
    - empty context -> teacher
    - target node request -> state dump
    - missing context -> lazy load, not refusal

  golden_teaching_cases:
    - MathLane A basic concept
    - MathLane B abstract concept
    - bridge slot teaching
    - error handling
    - exam handoff
    - tool truthfulness

  e2e_session_simulation:
    - student request
    - coordinator state dump
    - lesson_plan
    - guided teaching
    - student wrong once
    - repair
    - student restatement
    - exam trap
    - node cleared
    - spaced review update or missing scheduler warning
```

依据：Teaching Flow 已经列出一组 bug oracle，包括 Mode 混淆、Z3 量词爆炸、文件未挂载、早期拷问、定义倾倒、漏判前置大桥、桥接隐身、毕业误判等。
LRP-04 的任务就是把这些 oracle 从文档要求变成可执行 / 可审查测试集。

必须验证：

```yaml id="lrp_04_validation"
validation:
  - 每个 golden case 有 input、expected behavior、must_have、must_not_have
  - 至少覆盖 MathLane A、MathLane B、bridge slot、exam handoff、tool truthfulness
  - E2E simulation 不能假装 scheduler 已存在
```

---

### LRP-05：学生学习状态与间隔复习记忆系统

```yaml id="lrp_05"
task_id: math-mentor-lrp-05-student-learning-state-spaced-review
priority: P1
status: planned
```

目标：定义学生学习历史、课堂通过、复习调度、长期毕业的持久状态系统。

它解决的问题是：当前系统有 learned history rule，但没有稳定的学习历史 / spaced review scheduler schema。没有这个，系统会把课堂答对误判成长期掌握。

主要产物：

```yaml id="lrp_05_outputs"
outputs:
  - 08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE_SCHEMA.md
  - 08_Domain_Applications/Math_Mentor/SPACED_REVIEW_SCHEDULER_SCHEMA.md
  - 08_Domain_Applications/Math_Mentor/LEARNED_HISTORY_RULES.md
  - 08_Domain_Applications/Math_Mentor/GRADUATION_CRITERIA.md
```

状态分层：

```yaml id="lrp_05_status_model"
learning_status:
  not_seen: 未接触
  introduced: 已引入
  classroom_passed: Exam_Agent 课堂陷阱通过
  review_due: 到期复习
  review_passed: 复习通过
  graduated: 长期毕业
```

必须验证：

```yaml id="lrp_05_validation"
validation:
  - node id 大小不能代表 mastery
  - classroom_passed 不能直接等于 graduated
  - missing scheduler 时必须输出 warning
  - bridge slot learned status 必须从 persisted state 读取
```

依据：Coordinator prompt 已经规定 learned status 应来自 persisted learning history，`课堂通过` 只是最低课堂标准；低 node number 只能在严格顺序课程中作为 fallback。
Teaching Flow 也明确说长期 Graduation 只能在复习验证后成立。

---

### LRP-06：教学工具与能力真实性系统

```yaml id="lrp_06"
task_id: math-mentor-lrp-06-teaching-capability-and-tool-truthfulness
priority: P1/P2
status: planned
```

目标：把数学教学中可能使用的外部能力注册清楚：什么工具可用、谁能调用、何时可以声称已运行、没有工具日志时怎么表达。

它解决的问题是：教学系统想使用 Z3、SymPy、PyTorch、计算器、可视化工具、未来 app / skill，但当前 prompt 有“工具已运行”的过度声称风险。

主要产物：

```yaml id="lrp_06_outputs"
outputs:
  - 08_Domain_Applications/Math_Mentor/MATH_MENTOR_CAPABILITY_REGISTRY.md
  - 08_Domain_Applications/Math_Mentor/TOOL_TRUTHFULNESS_POLICY.md
  - 08_Domain_Applications/Math_Mentor/DETERMINISTIC_CALCULATION_HANDOFF.md
  - 08_Domain_Applications/Math_Mentor/VISUALIZATION_AND_APP_CAPABILITY_PLAN.md
```

能力类别：

```yaml id="lrp_06_capabilities"
capabilities:
  deterministic_calculation:
    examples:
      - calculator
      - python
      - sympy
      - z3
    rule: 只有真实运行并有日志，才能说已运行

  semantic_audit:
    examples:
      - proof sketch review
      - structure consistency check
    rule: 只能说语义审查，不得伪装成机器证明

  visualization:
    examples:
      - graph plotting
      - geometry sketch
      - interactive concept block
    status: planned_or_tool_dependent

  human_brief:
    examples:
      - Obsidian
      - GitHub report
    status: planned
```

必须验证：

```yaml id="lrp_06_validation"
validation:
  - prompt 中不存在未运行却声称已运行的表达
  - 工具运行必须有 command/log/report
  - 无工具日志时统一使用 "可由工具验证" 或 "当前为语义审查"
  - 不激活 runtime / Coordinator / external app
```

这个任务可以稍后做，不必挡住 LRP-01 到 LRP-04；但它必须在真正上线“工具增强教学”前完成。

---

## 3. 推荐执行顺序

虽然 6 个长期任务可以独立维护，但推荐顺序是：

```yaml id="execution_order"
recommended_order:
  1:
    task: LRP-01 教师初始化与上下文加载系统
    reason: 先保证新模型能正确成为教师

  2:
    task: LRP-02 Lesson Plan Schema 与 Agent Contract 统一
    reason: 再保证教学管线内部数据结构一致

  3:
    task: LRP-03 教学 Prompt 一致性修复
    reason: 然后修掉 prompt 冲突和假工具声称

  4:
    task: LRP-04 教学测试系统与 Golden Cases
    reason: 用测试锁住前面修复成果

  5:
    task: LRP-05 学生学习状态与间隔复习记忆系统
    reason: 课堂通过后需要长期记忆和复习闭环

  6:
    task: LRP-06 教学工具与能力真实性系统
    reason: 最后接入外部工具能力，避免先接工具再制造幻觉
```

更保守的依赖图是：

```text id="dependency_graph"
LRP-01 初始化加载
    ↓
LRP-02 lesson_plan / agent contract
    ↓
LRP-03 prompt consistency repair
    ↓
LRP-04 test harness / golden cases
    ↓
LRP-05 learning state / spaced review
    ↓
LRP-06 capabilities / tool truthfulness
```

但实际可以并行的部分是：

```yaml id="parallelizable"
parallelizable:
  - LRP-01 and LRP-02 可以并行设计，但最后要对齐
  - LRP-05 可以提前设计 schema，不需要等 LRP-04 完成
  - LRP-06 可以先做 policy，不接 runtime
```

---

## 4. `未完成任务备忘录.yml` 可索引版本

可以把下面作为一个总索引，后续每个 LRP 再展开。

```yaml id="unfinished_index"
unfinished_tasks:
  - task_id: math-mentor-teaching-system-lrp-suite-0001
    title: Math Mentor 教学系统长期任务组
    status: planned
    priority: high
    owner: Human Speaker
    engine: Engine_B
    base_master_head: eb918a55becefe609e27723073a38be319f10586

    purpose: >
      将 Math Mentor Teaching System 从已有理念和 prompt 骨架，推进为可初始化、
      可授课、可测试、可回溯、可复习、可工具增强的长期教学系统。

    long_run_programs:
      - task_id: math-mentor-lrp-01-teacher-initialization-context-loading
        title: 教师初始化与上下文加载系统
        priority: P0
        target_outputs:
          - 08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md
          - 08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md
          - 08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md

      - task_id: math-mentor-lrp-02-lesson-plan-agent-contract
        title: Lesson Plan Schema 与 Agent Contract 统一
        priority: P0
        target_outputs:
          - 08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md
          - 08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md
          - 08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md
          - 08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md

      - task_id: math-mentor-lrp-03-teaching-prompt-consistency-repair
        title: 教学 Prompt 一致性修复
        priority: P0
        target_outputs:
          - 08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md
          - updated Coordinator / Prep / Socratic / Exam prompts

      - task_id: math-mentor-lrp-04-teaching-test-harness-and-golden-cases
        title: 教学测试系统与 Golden Cases
        priority: P0/P1
        target_outputs:
          - 08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md
          - 08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md
          - 08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_TEST_FIXTURES.md
          - 08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md

      - task_id: math-mentor-lrp-05-student-learning-state-spaced-review
        title: 学生学习状态与间隔复习记忆系统
        priority: P1
        target_outputs:
          - 08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE_SCHEMA.md
          - 08_Domain_Applications/Math_Mentor/SPACED_REVIEW_SCHEDULER_SCHEMA.md
          - 08_Domain_Applications/Math_Mentor/LEARNED_HISTORY_RULES.md
          - 08_Domain_Applications/Math_Mentor/GRADUATION_CRITERIA.md

      - task_id: math-mentor-lrp-06-teaching-capability-and-tool-truthfulness
        title: 教学工具与能力真实性系统
        priority: P1/P2
        target_outputs:
          - 08_Domain_Applications/Math_Mentor/MATH_MENTOR_CAPABILITY_REGISTRY.md
          - 08_Domain_Applications/Math_Mentor/TOOL_TRUTHFULNESS_POLICY.md
          - 08_Domain_Applications/Math_Mentor/DETERMINISTIC_CALCULATION_HANDOFF.md
          - 08_Domain_Applications/Math_Mentor/VISUALIZATION_AND_APP_CAPABILITY_PLAN.md

    global_must_preserve:
      - Plan 3 Human Speaker authority
      - Engine B human-moderated teaching domain
      - lazy-loading / anti-full-ingestion
      - teach-before-interrogation
      - no fake tool execution claims
      - classroom_passed != graduated
      - no runtime or Coordinator activation without explicit Human authorization

    next_action_when_quota_available: >
      Launch LRP-01 first as a completion-preserving Codex task from latest origin/master.
      Do not split LRP-01 into file-level microtasks. It must include reading, design,
      document creation, validation, report, dev branch push, and handoff.
```

---

## 5. 总体建议

可以拆成 6 个长期任务。
不要拆成 20 个小任务。
每个 LRP 都应该是完整闭环：

```yaml id="lrp_policy"
each_lrp_policy:
  completion_preserving: true
  includes:
    - read required files
    - design
    - implement docs / prompt fixes / schemas / tests
    - validate
    - report
    - commit
    - push dev branch
    - handoff
  excludes_unless_explicitly_authorized:
    - master push
    - runtime activation
    - Coordinator activation
    - new node generation
    - new bridge generation
```

我的建议是：**先做 LRP-01，再做 LRP-02，第三步做 LRP-03。**
这三个完成后，教学系统才有稳定的“新模型初始化 → lesson_plan → 前台教学”主链路。
