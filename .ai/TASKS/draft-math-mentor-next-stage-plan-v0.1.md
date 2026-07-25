---
design_id: "math-mentor-next-stage-plan-v0.1"
title: "Math Mentor 下一阶段能力推进路线(Fable 只读架构审查产物,待 Human 审批)"
status: "read_only_review_output_awaiting_human_approval"
reviewer: "Fable (foreground, high)"
base_master: "94b617e67bdbdb958443545d41b90cdbba77e54d"
not_dispatched: true
---

# Math Mentor 下一阶段路线(审查结论)

## 1. actually_read_files(本轮增量;此前深读经 git log 核验零变更仍有效)
- 增量:`.ai/load_profiles/math_mentor_teacher.md`(全文)· TEACHING_GOLDEN_CASES.md(用例清单)· KNOWLEDGE_COMPLETION_PROGRAM.md(§0-2 程序模型)· STUDENT_LEARNING_STATE_SCHEMA.md / BRIDGE_SCHEMA.md(结构骨架)
- 既读有效(386749b 时代全文/大部,08 目录至今零 commit):Coordinator Prompt、Teaching Flow Spec、AGENT_CONTRACTS、LESSON_PLAN_SCHEMA、TOOL_TRUTHFULNESS、GRADUATION_CRITERIA、认知映射引擎、MASTER_PLAN、CURRENT_STATE、ROLE_AND_HANDOFF

## 2. 当前事实矩阵
- canonical_active:六 LRP 全套合同/prompt/schema/测试文档;P0 静态控制面(104/104);teacher load profile + role memory(teacher.md)
- present_but_incomplete:golden cases 从未被真实教学运行检验(specified_manual_only 的全部含义)
- design_only:writer(learning-state/scheduler)、visualization、KCP Stage1-6 批次
- legacy_or_conflicting:14 legacy bridge(0 canonical)+ 昨日打捞的 5 条 P3 语义(untrusted input)、复习巩固期旧 prompt(只读 importer 输入)
- missing:certification at scale(667 中 4)、writer 实现
- runtime_not_activated:Coordinator/scheduler/consumer(consumer_allowed=0)——保持

## 3. 四工作流依赖与推荐顺序
**A → B(并行批次程序)→ C(设计)→ D(迁移设计)**
- A 零变更风险、直接检验纸面合同,且产出:行为缺口清单→喂 B 优先级;状态更新提案→成为 C 的 fixture;bridge slot 诚实降级实测→喂 D。A 是唯一无前置的。
- B 只依赖 A 的首例反馈(弱依赖),可在 A 首场后作为 KCP 长运行程序并行开跑(它自带 Stage0-9 检查点模型,天然 completion-preserving)。
- C 强依赖 A 的提案样本;D 的 endpoint 重绑依赖 B 的 Stage 6 认证——两者押后。

## 4. 第一任务:教学 dry-run(A)完整边界 ✅建议立即作为第一个 completion-preserving 任务
- objective:两场真实手工教学(Human=真实学习者),验证发布合同可教学
- 首批用例映射(用已认证 4 节点,别碰未认证语料):
  - 场1:**GC-A-001** → COMPLEX_ANALYSIS-418(MathLane_A,含 GC-ERROR/GC-EXAM/GC-TOOL 环节自然折叠)
  - 场2:**GC-B-001** → ABSTRACT_ALGEBRA-468(MathLane_B,LLM 架构映射教学;zero-context takeover 测试)
  - GC-BRIDGE-001 顺带验证"无可消费 bridge 时诚实降级 teaser/unavailable"(反而是最好的诚实性测试)
- 教师安排:场1 = ChatGPT 网页(零 Claude 成本,它已重建基线);场2 = Claude 新窗口(测 zero-context 接管);Fable = 场后合规审计(对照 golden must/must-not + 工具真实性扫描)
- must_do:zero-context 接管 → SYSTEM_STATE_DUMP → lesson_plan → teach-before-interrogation → 错误诊断/定向修复 → 学生复述 → Exam handoff → classroom≠graduated → **状态更新只出提案文件**(无 writer)→ scheduler 明示 warning → actually_read_files 全程
- must_not:激活 Coordinator/writer;改学习者持久状态;生成 bridge;把 simulation 称作 production E2E;无日志称工具已运行
- validation:Fable 审计报告(对照表)+ 缺口清单;expected_outputs:两份 transcript + 审计报告 + 状态提案 fixture + 缺口→B/C 输入
- real_human_decisions:①批准本任务 ②**你选第一课**:复分析-418(计算直觉路线)或抽象代数-468(结构映射路线)——这是你自己的学习,你选

## 5. 语料认证批次策略(B)
- 机制:KCP 自带长运行模型,一个 Human 授权包覆盖 Stage 范围,批≤5、Stage/批双检查点、隔离 run 分支
- **批次1 = 四个 prerequisite-frontier**(恰好≤5):CA-417、PDE-486(Mode A,确定性证据,低冲突直接审计)+ AA-467(Mode B,需 Human 语义接受)+ DIFF_GEO-653(Mode B,且需先对账已发布的 653 semantic pilot 历史)
- 证据合同:Mode A=run_with_log 确定性验证;Mode B=Human 语义接受记录;每节点出 identity/mode/formal/prereq/teaching-ready 证据链
- 双门分离:teaching_ready(可人工教)≠ consumer_allowed(留 0,Stage 8 另 gate)
- 节奏:每周 1 批或随学习需求拉动(你学到哪、认证到哪——**learner-driven certification**,建议采纳)

## 6. writer 架构真实分叉(C,仅设计,列给未来 Human)
1. **存储介质**:repo 内 append-only 事件文件(git 审计,复用 lane/reducer 模式)vs CityState 本地 vs 混合。倾向:repo 事件+派生快照(隐私注意:仓库可见性你确认)
2. **写入权属**:foreground 单 writer(复用 STATE reducer 模式)vs Human 触发脚本。倾向:确定性脚本+Human/前台触发,无常驻
3. **Human 权威注入**:graduation 等转换需 Human 事件——用 publish-helper 提交的 Human 接受事件,不造 ActorOrigin 机器
4. **回滚**:事件溯源补偿事件(不改历史)
5. **scheduler writer 必须分离**:它触碰 protected `scheduler_or_polling` 边界 → 独立未来 gate,学习状态 writer 不捆绑
- classroom_passed→graduated 无捷径:转换表硬编码最少 2 次复习通过(GRADUATION_CRITERIA 已定)

## 7. bridge 迁移 Human gates(D)
输入:14 legacy(先)+ 5 条 P3 打捞语义(后,依 migrate_existing_before_new_generation)
流程:inventory→collision 分组(001..004 重复)→内容保全→endpoint 候选提取→**Gate1 Human 数学复核/碰撞裁决**→canonical v1 提案→validation→indexing→**Gate2 landing 授权**→(远期)**Gate3 Stage 8 admission/consumption**
依赖:endpoint 重绑需 B 的 Stage 6 认证节点——D 排 B 后

## 8. 仅真实 Human 决策
1. 批准 A 为第一任务 + **选第一课**(418 或 468)
2. 批准 B 批次1 范围(四 frontier)与 learner-driven 节奏
3. C 存储介质分叉(可等 A 完成后再定)
4. (D 无当期决策;碰撞裁决到任务内再出)

## 9. 下一步
Human 批准后:A 作为单个 completion-preserving 任务发包(教师=ChatGPT/Claude,审计=Fable);B 作为 KCP 长运行包草拟另批。本文件即"可供 Human 审批的方案",未派发实现。
