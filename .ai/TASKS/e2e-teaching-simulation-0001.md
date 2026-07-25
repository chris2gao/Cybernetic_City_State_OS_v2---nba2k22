---
task_id: "e2e-teaching-simulation-0001"
title: "E2E模拟教学演练×2(用尽当期Fable5额度,为真实第一课扫雷)"
mode: "goal"
assigned_executor: "fresh_cowork_session (Fable5) 或 claude_cli"
risk_tier: "T2"
human_gate: "approved(Human 2026-07-19口头,用尽当期额度)"
base: "master@94b617e(开工核验)"
boundary: "纯本地模拟;不推GitHub、不激活runtime/writer、不动learner真实状态、不生成bridge、不碰Codex正在跑的批次1路径(逻辑节点/dev分支)"
---

# 任务:两场模拟教学

1. **接管**:按 `.ai/load_profiles/math_mentor_teacher.md` 冷启动(读宪法摘要+教学五合同+role_memory的core/teacher);记录 actually_read_files——这本身是接管机制实测。
2. **场A**:目标节点 COMPLEX_ANALYSIS-418(已认证,MathLane_A)。按 `08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md` 全链跑:SYSTEM_STATE_DUMP → lesson_plan(LESSON_PLAN_SCHEMA)→ 讲解先行教学 → 模拟学生犯一次典型错 → 诊断+定向修复 → 学生复述 → EXAM_HANDOVER → classroom结果 → 状态更新**提案**(无writer,明示)→ scheduler placeholder warning。工具声明全程守 TOOL_TRUTHFULNESS(无日志=semantic_only)。
3. **场B**:ABSTRACT_ALGEBRA-468(已认证,MathLane_B)。同链,但直觉层必须用LLM架构映射(禁日常隐喻),v8_sanity_audit只作semantic_only。
4. **自审**:对照 TEACHING_GOLDEN_CASES 的 must_have/must_not_have 逐项打勾;违规如实列出。
5. **产出**(全部本地写文件,不推远端):
   - `E:\newStand\城邦简报\04_知识摘要\模拟教学场A_复分析418.md`(逐字稿+自审表)
   - `E:\newStand\城邦简报\04_知识摘要\模拟教学场B_抽象代数468.md`
   - `E:\newStand\城邦简报\04_知识摘要\模拟教学缺口报告.md`(发现的合同缺陷/prompt问题/给真实第一课的修正建议,≤40行)
6. 若额度中途耗尽:每场结束即保存,断点明示,不硬撑。
