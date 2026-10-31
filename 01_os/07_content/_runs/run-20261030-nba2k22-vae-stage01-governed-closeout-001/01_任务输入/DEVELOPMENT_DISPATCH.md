# VAE Stage01 已确认 A-v1 · Governed Closeout 执行指令

**本次岗位**：独立 GPT 执行窗口 `execution`，从 `NBA_COMMON_BASELINE_READY` Fork。不是VAE规划窗口，也不是旧开发或审核窗口。使用本Run的 `task_packet.json` 恢复任务。

## 唯一需要完成的事
**将 Human 已明确批准的固定 Stage01 A-v1 形成可验证的正式工作流阶段收尾**，提供可审阅的阶段产物、Human绑定确认及真正可查的校验/runner回执。执行前检查现行Core真实runner支持的阶段操作、Profile/Receipt/Hash绑定和Human门禁，不可自行设计替代的“已完成”状态。

### 固定不变的事实
- A文件：`5abf3cb154654872a3d05278b96658f190ed9241:01_os/07_content/_runs/run-20261030-nba2k22-vae-gpt-development-001/01_需求建模/A_需求建模_v1.yml`，blob `612ed21f8f3e441366296ee2ac6170bb5974584b`。**内容不得修改**，如需要在新Run中承载，逐字节复制并验证相同blob或使用核心规范允许的精确原始引用。
- Human的本次直接确认记录：`a98aa2db6e442bbc3aecfa552665ea13d482683e:01_os/07_content/_runs/run-20261030-nba2k22-vae-stage01-001/01_任务输入/HUMAN_STAGE01_A_V1_CONFIRMATION_20261030.yml`，明确批准A-v1并接受审核限制，确认来源不可由模型自行创造。
- 独立审核：`4640f6e05f2b84e31661c7b2039dfc5d202b30a5:01_os/07_content/_runs/run-20261030-nba2k22-vae-stage01-independent-review-001/08_结论/completion_pointer.md`，结论 `PARTIALLY_SUPPORTED`，F02–F07后续修正；F01因真实Human确认已具备关闭基础。
- 实际Core和NBA远端master必须fresh-read；Core Stage01最小运行Schema、七阶段runner及协同推演receipt须按真实代码和profile处理。

### 实际执行步骤
1. 先输出《岗位与任务恢复回执》，只读取本任务直接相关的G1/G2/P00–P12正文与固定SHA来源；正确判明 PRMS是否真的可用。
2. 核验 Human确认记录与固定A的SHA/blob完全对应；检查独立审核遗留发现，且只确认A产品语义，不将F02–F07升级为已解决。
3. 核查现行Core阶段runner与协同推演receipt机制，在新Run中创建符合其真实契约的Stage01正式产物。**优先实际运行原有验证器并保存返回码、输出、Git SHA/blob，以及必要审批来源。**
4. 若现行runner的真实路径要求完整七阶段、前驱/实例/Profile或当前权限不允许单独Stage01完成，则不要伪造 `PASS`：保持 `NOT_RUN/BLOCKED`，写明准确可复现的阻塞点、下一责任人和最小关闭步骤。
5. 在新任务分支、允许路径内提交并回读；输出结果指针，记录指派/实际模型、身份来源及受限状态。执行者不自行宣布独立审核通过。
6. 将简短完成指针交Human转交VAE规划窗口：task_id、HEAD、完成/阻塞状态、实际Runner证据与下一Owner。

### 重要边界
- **已经获得Human的A-v1确认，绝不重复要求用户确认相同版本。**
- 本次不修正R06/R08/R03-R05，不开始Stage02，不实施游戏、存档或REA写入，不改Core/global机制，不动开发/审核/规划分支。
- Stage01完成以现行正式治理验证为准；Human批准本身是完成门的一部分，不是全部。
- 若缺少平台真实模型ID，记录实际模型 `DECLARED` 或 `UNKNOWN`，不冒充签名运行时身份。
