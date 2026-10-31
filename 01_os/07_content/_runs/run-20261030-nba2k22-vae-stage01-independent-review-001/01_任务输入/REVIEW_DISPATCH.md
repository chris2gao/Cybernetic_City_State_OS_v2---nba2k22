# VAE Stage01 — 独立审核开发任务

**岗位**：`independent_review`。从 `NBA_COMMON_BASELINE_READY` 另起新GPT窗口，不从开发者窗口Fork。开发者为独立GPT执行窗口，不能自我审核。

**任务**：`NBA2K22-VAE-STAGE01-INDEPENDENT-REVIEW-20261030-001`。**被审核成果**：`5abf3cb154654872a3d05278b96658f190ed9241`；**完成指针**：`3b0ef0b2185780d304ca8b1aa6d4a69f0bd4e6f3`。精确任务入口和所有直接源文件见 `01_任务输入/task_packet.json`。请复核Core与NBA实际master是否变化，不把候选或旧研究冒充实证。

审核重点：
1. Core Stage01八槽位、可观察判据、跨字段一致性和高影响歧义是否符合真实规范；A候选是否精准表达E1–E4、MC作为MyLEAGUE底层验证载体、VAE与D1–D5独立、可证伪的迭代验证及NO_CHANGE。
2. R01–R09输入/输出/来源/失败及权限边界，能否支持首个纵向原型的可验收需求；不得把Stage01提前宣布Stage03或游戏可用。
3. Stage02取证矩阵的真实来源等级及UNKNOWN是否完整，特别是USER/CPU、Normalize、3D vs Calendar、Native/SaveReload、现有存档身份。
4. 独立核实静态测试报告的PASS可信范围。检查报告中中间提交引用c07916.../8108b...与最终候选 `5abf3cb154654872a3d05278b96658f190ed9241` 的对应关系；不可仅据开发者自述通过。
5. 验证开发者变更仅在Run内，明确Human版本确认PENDING、游戏/存档/REA写入NOT_RUN、PRMS与通讯回执NOT_RUN。

**交付**：在本审核Run提交独立审核证据矩阵、明确结论（支持、部分支持、返工或阻塞）和包含精确SHA的 `08_结论/completion_pointer.md`；说明有无足以交Human确认的A版本、剩余问题Owner及关闭证据。不得自行确认Human版本或修改开发者分支/游戏。记录指派模型、实际模型及其证据来源；无可信运行平台身份则写DECLARED/UNKNOWN，不冒充认证。
