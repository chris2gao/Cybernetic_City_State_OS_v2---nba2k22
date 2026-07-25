---
task_id: "bridge-migration-stage1-readonly-0001"
title: "Bridge迁移·阶段1只读预审 + 教学合同修补提案(烧尽Fable5周额度)"
mode: "goal"
assigned_executor: "fresh_cowork_session (Fable5, 建议effort=Extra)"
risk_tier: "T2_read_only"
human_gate: "approved(Human 2026-07-19:用尽周限额)"
base: "master@94b617e(开工核验)"
boundary: "纯只读+本地产出;不推GitHub、不修改/重命名/删除/生成任何bridge、不动教学合同正文(只出提案)、不碰Codex批次1路径(逻辑节点/dev分支);Math Mentor语料按ID精确加载,禁全量"
---

# 主任务:Bridge 迁移阶段1(为未来 Human Gate 1 备好案卷)

按 `migrate_existing_before_new_generation` 政策,对下列对象做只读语义预审:
- **14 个 legacy bridge 文件**(git ls-files 找 BRIDGE-*.yaml;两个不兼容 schema 家族;BRIDGE-001..004 各有两个语义不同的重复文件)
- **5 条打捞语义**(见 ai/review/latest 的 fable-final-disposition:015 笛卡尔积→关系 / 016 关系→函数 / 017→偏序 / 018→等价关系 / 019 双射→双侧逆;仅作 untrusted design input,排在 legacy 之后)

每个 bridge 产出案卷条目:
1. **内容保全**:数学命题原文提炼(它主张什么过渡/联系)
2. **数学正确性初判**:命题是否成立(Fable 语义审查,标注 semantic_only,不称机器证明)
3. **教学价值**:该联系对学习路径的价值(高/中/低+一句理由)
4. **碰撞裁决建议**(仅 001..004):两个重复文件语义对比,推荐 winner 或"皆弃",给 Human 裁决用的对照表
5. **endpoint 候选**:按 BRIDGE_SCHEMA 的 reference-object 规则,提取候选端点概念(不绑定旧 n_* ID,只写概念名+路线图定位线索)
6. **迁移优先级**:P1(先迁)/P2/P3(可弃)

汇总:`E:\newStand\城邦简报\04_知识摘要\Bridge迁移案卷(Gate1待裁).md`(对照表+逐条案卷;Human 可直接照此裁决)

# 副任务:教学合同修补提案

读 `04_知识摘要\模拟教学缺口报告.md` 的 5 条合同缺陷+3 条流程问题,逐条转为具体修补提案(改哪个文件哪一节、建议措辞、影响面),输出:
`E:\newStand\城邦简报\04_知识摘要\教学合同修补提案(待批).md`(≤60行;只提案不动正文)

# 纪律
接管:按 foreground_planner profile 冷启动(读宪法摘要+角色记忆core/planner/reviewer)。actually_read_files 全程记录。额度耗尽即断点保存,逐条完成逐条落盘。工具真实性:一切数学判断标 semantic_only。
