# Math Mentor OS (V9.1) 从知识维护到手动教学的完整流程

Status: aligned operational lifecycle manual for LRP-01 through LRP-06 contracts.

## 1. 文档边界

本文档说明知识节点如何作为已存在的教学证据进入手动聊天教学。它不授权或激活：

- 节点生成或批量重生成；
- bridge 设计、生成、登记或 Coordinator 消费；
- runtime 或 production Coordinator；
- Z3、SymPy、Python、PyTorch、calculator、sandbox 或 app 执行；
- learning-state、learned-history 或 spaced-review scheduler 写入；
- source/master 发布。

指令权威采用 .ai/PROTOCOL.md 的 canonical instruction authority and state freshness 规则。文件加载顺序不是权威顺序；Git、mailbox 和时间戳的新鲜度也不是执行授权。仓库初始化由 06_Silicon_Index/AI_Bootstrap_Sequence.md 路由。

## 2. 知识维护阶段与教学阶段分离

知识节点生成是独立的、未来 Human 授权的维护任务，遵循 Universal_Layer_Execution_Protocol.md。普通教学不会自动进入该阶段。

当维护任务需要路线图时：

1. 根据目标层级读取对应的 split roadmap，例如 数学知识路线图_第一层基础工具.yaml 至 数学知识路线图_第六层前沿领域.yaml 中与任务相符的一份或少数几份；
2. 仅在明确授权 full-graph audit 时读取 数学知识路线图_全部.yaml；
3. 记录 actually_read_files，不得用文件名、索引或隐藏记忆代替物理读取；
4. 将生成、验证、合流和索引更新视为单独授权动作。

v8_sanity_audit、SymPy/Z3 风格伪代码和张量片段默认只是 semantic_only 或高密度 prompt evidence。没有具体 run_with_log 时，不得描述为已执行、已计算、已验证、sandbox passed 或 machine-proven。

## 3. 活跃的手动教学管线

当前可执行的文档级教学管线是：

~~~text
Human request
-> Coordinator minimal loading and MathLane routing
-> Prep_Architect lesson plan
-> Guided Socratic explanation-first teaching
-> Exam_Agent independent classroom test
-> learning-state / spaced-review placeholder
~~~

这条管线是 manual-chat-only。它描述代理间契约，不启动生产 runtime 或 Coordinator。

### 3.1 Human Request

Human 提供概念、node id 或精确文件目标。普通学习请求只授权手动教学，不授权修改 prompt、node、bridge、roadmap、state 或 scheduler。

### 3.2 Coordinator Minimal Lazy Loading And Routing

Coordinator：

1. 读取 08_Math_Mentor_Coordinator_Prompt.md、Teaching Flow Spec、Lesson Plan Schema、Teaching Agent Contracts 和 Tool Truthfulness Policy；
2. 使用精确 node id、索引或当前层级 split roadmap 定位目标；
3. 只读取目标节点、必要的 immediate prerequisites、端点匹配的 bridge，以及确有需要的 learned-history evidence；
4. 维护 actually_read_files 与 unavailable_files；
5. 使用 Plan3_Engine_B 作为教学权威路由，并在 MathLane_A、MathLane_B 或已审查的 mixed 中选择教学 lane；
6. 输出压缩 SYSTEM_STATE_DUMP，字段使用 Math_Lane，不使用旧 Mode 字段。

普通教学不得全量读取仓库、Math Mentor 目录、Pure_Math_Intuition_DB、所有 bridge 或完整路线图。

### 3.3 Prep_Architect Lesson Plan

Prep_Architect 生成符合 LESSON_PLAN_SCHEMA.md 的 wrapper：

- occurrence crisis 在形式定义之前；
- intuition model 与 MathLane 一致；
- 每个 source sub_topics 精确进入一次 subtopic_plan；
- bridge slot 只消费有端点与 learned-history 证据的记录；
- tool truthfulness 使用 not_run、semantic_only、unavailable、planned、review_required 或带日志的 run_with_log；
- 缺少 MathLane_B mapping 时返回 re-prep，不用家庭或工厂隐喻替代。

### 3.4 Guided Socratic Explanation-First Teaching

教学顺序：

1. 解释概念为何必须出现；
2. 给出有边界的 lane-consistent intuition；
3. 压缩为 formal definition；
4. 在证据允许时激活 bridge slot；
5. 覆盖全部 sub_topics；
6. 每个互动回合最多提出一个紧凑问题；
7. 学生错误时先追问一次，再纠错或 re-prep；
8. 要求学生用自己的话复述定义或判据。

纯拷问先于讲解无效。MathLane_B 使用有明确 mapping_boundary 的 LLM-architecture structural analogy，pure_math_definition 始终是数学权威。

### 3.5 Exam_Agent Independent Classroom Test

只有在全部 subtopics 已覆盖、bridge 检查完成或明确不可用、学生已复述定义后，Socratic_Router 才发送 SYSTEM_INTERRUPT: EXAM_HANDOVER。

Exam_Agent 独立测试当前课堂边界和陷阱，不补教替代课程。允许结果：

- classroom_passed；
- failed；
- needs_reprep。

classroom_passed != graduated。课堂通过不代表长期保持、review pass、scheduler 写入或 learned-history 更新。

### 3.6 Learning-State / Spaced-Review Placeholder

没有单独写入授权时，只输出：

~~~yaml
review_scheduler_status: "placeholder_not_written"
actual_learning_state_write_performed: false
actual_learned_history_write_performed: false
actual_scheduler_write_performed: false
graduation_status: "not_graduated"
~~~

## 4. 确定性计算的未来 Engine A Handoff

教学代理可以指出某个命题适合确定性检查，但不能静默执行 exec()、后台 sandbox 或任何外部工具。

真实计算需要未来 Human 授权的 Plan3_Engine_A 任务，并产生：

~~~yaml
tool_truthfulness:
  tool_status: "run_with_log"
  tool_family: "<Z3 | SymPy | Python | PyTorch | calculator | other>"
  input_ref: "<required>"
  log_ref: "<required>"
  output_ref: "<required or null>"
  environment_ref: "<required>"
  limitations: []
~~~

缺少这些证据时，状态保持 not_run、semantic_only、unavailable、planned 或 review_required。

## 5. Operational Audit Checklist

1. **目标未定位**：只读取必要索引或对应层级 split roadmap，不读取完整路线图。
2. **MathLane 不清楚**：回到 Coordinator 的 domain/subdomain evidence；不得用 level number 单独路由。
3. **MathLane_B 映射缺失**：请求 re-prep；不得使用日常物理隐喻作为 primary mapping。
4. **工具证据缺失**：标记 semantic_only 或 not_run；不得假定预验证结果。
5. **教学漂移**：重载最小缺失 authority/manual/target evidence，并更新 actually_read_files。
6. **Exam 通过**：记录 classroom result 与 review placeholder；不得宣称 graduated 或已写 scheduler。
7. **任何激活动作**：本文档不授权 runtime、Coordinator、node/bridge generation 或状态写入，必须由新的 Human 任务明确开启。
