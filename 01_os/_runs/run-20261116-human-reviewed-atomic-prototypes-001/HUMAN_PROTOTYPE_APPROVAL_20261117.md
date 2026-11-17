# Core PR #37 · 首个真实 Human 任务原型设计批准

- **裁决日期：** 2026-11-17（America/Los_Angeles）
- **裁决来源类型：** 当前 ChatGPT 对话中 Human 的直接答复（不是开发者合成的测试夹具）
- **Human 原话：** “批准”
- **所答复的提案：** 紧邻上条助手消息《Core PR #37 · 首个真实任务原型已提交 Human 设计审核》，明确询问是否批准 `core-prms-registry-read-v1` 的一次只读调用、零额外业务 Ready、真实结果 Done。
- **提案的不可变来源提交：** `566e8ca493e0dd5f0b116ccc3f1cd2d86b84920b`
- **提案路径：** `01_os/_runs/run-20261116-human-reviewed-atomic-prototypes-001/FIRST_PRMS_PROTOTYPE_PROPOSAL.json`
- **prototype_key：** `core-prms-registry-read-v1`
- **prototype_digest (reviewed_prototypes.digest)：** `5bbfdfd45e75b936933922620a81e0c55b645a212b380256447a5c28ba9ce501`
- **task_scope：** `OS-CORE-HUMAN-REVIEWED-ATOMIC-PROTOTYPES-SYSTEM-UPGRADE-20261116-001`
- **决策：** `APPROVED`（仅针对上述精确原型内容和适用范围）

## 已批准的具体操作合同

1. **Goal：** 只读获得固定 Core 版本中 PRMS v1 注册清单、实际条目及可追溯 Git 来源。
2. **Ready：** 不增加额外业务前置条件；编译阶段要求存在真实且版本匹配的 callable 和固定 Git 源。
3. **Action：** Host 预绑定 `catalog.py::mapping(source, '01_os/05_registry/prms_v1.yml')`，只调用一次；保留函数结果以供 Done 回读。
4. **Procedure：** 唯一 Host 动作是调用已存在的 `catalog.mapping`；现有 `GitSource.read` 内部负责固定源读取验证；不额外扫描仓库、临时增加业务检查或新增 PRMS 查询函数。
5. **Done：** 从实际返回值及 GitSource 的固定 commit/path/blob 读取记录确认 PRMS 注册数据与目标对应。函数无异常退出不自动等于 Done。
6. **权限与例外：** 此批准不赋予写入 Core master、Native、破坏性文件、PRMS 有效状态或其他受保护操作的权限；异常或不能确认 Done 时保持 `INCOMPLETE`，不盲重试；内容/版本的负载关键变更需重新审定。

## 来源真实性与实现边界

本文件如实保存了当前 Human 对话中的明确批准，**不是** Human 本人在 GitHub 上进行的单独签名。它由执行 Agent 代为整理入现有 Run；GitHub 文件的提交身份单独不能证明批准者身份。

`PRMSReviewLookup.verify_human_source` 仍须由调用方可信 Host 依据实际 Human 对话/现有可信来源核验，不得由任意 Agent 自写 `lambda: True` 就宣称完成了 Host 级身份验证。允许对批准内容进行只读 E2E 验证，但必须区分实际 Human 批准事实与技术性 Host 来源认证是否已部署。

本批准不等于整个 PR #37 最终验收或 master 合并授权。
