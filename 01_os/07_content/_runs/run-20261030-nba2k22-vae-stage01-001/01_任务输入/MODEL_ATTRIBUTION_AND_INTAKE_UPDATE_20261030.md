# VAE 后续任务的模型记录与独立审核接收约定（当前任务限定）

本约定来自Human本轮最新指令：**不追补历史任务；以后的任务记录必须保留模型信息**。此处不修订Core PRMS Schema或通讯协议，默认依赖Model Routing接收设置、Communication endpoint card、既有task packet/Run、MWU与completion pointer。

## 新任务派单应记录
- `task_id`、`assigned_collaboration_role`；
- `assigned_provider`（OpenAI/Anthropic/Google等）、`assigned_product`（ChatGPT/Codex/Claude/Antigravity等）、`assigned_model`（如能明确则准确标签，未可确证则UNKNOWN）；
- `assigned_surface`、`assigned_window_or_endpoint`、`assignment_source`；
- 预期独立审核模式与是否隔离，review任务与开发任务分别保持独立task_id、Run、HEAD与证据。

## 新任务完成时应记录
- `actual_provider`、`actual_product`、`actual_model`、`actual_window_instance`、`identity_evidence_source`、`identity_confidence`；
- 开发、辅助与独立审核分别记录自己的执行身份，不能把接收方或指派身份当实际执行人；
- 宿主没有可信运行时模型身份时记录 `DECLARED_BY_EXECUTOR` 或 `UNKNOWN`；不能凭GitHub author、任务标题、模型自称伪造平台验证；
- 同一任务中发生模型替换、协作、恢复时保留各执行片段及其职责/证据，禁止把前后模型合并成一个虚构身份；
- 附 `task_id`、精确Git HEAD、完成指针、验证证据和审核来源；不复制开发者完整日志。

此条为**未来新任务的最低署名约定**；现有VAE执行者旧任务不要求补录。当前新增的独立审核任务已示范记录 assigned_model 和 actual_model pending。

## GPT开发成果接收状态
- 执行任务：`NBA2K22-VAE-GPT-STAGE01-20261030-001`
- 候选源码：`5abf3cb154654872a3d05278b96658f190ed9241`
- 完成指针：`3b0ef0b2185780d304ca8b1aa6d4a69f0bd4e6f3`
- 经规划岗位核对：源文件存在、候选变更集中单一Run、九对象原型与Stage02缺口矩阵存在；此处不是正式独立审查。
- 候选状态：`DEVELOPMENT_CANDIDATE_DELIVERED`、`HUMAN_CONFIRMATION_PENDING`，未执行实机验证。
- 已发布独立审核任务：`NBA2K22-VAE-STAGE01-INDEPENDENT-REVIEW-20261030-001` @ `ccdfc57afe5693f8a36cf31ec6b1d4508a7e65eb`。
- 审核结果：`NOT_RUN`，Human版本确认：`PENDING`。
- 注：开发者静态测试报告包含中间提交的锚点；审核任务要求独立核对其与最终成果的可追溯一致性。

不创建额外OS全局机制、不宣称Communication v2正式送达、不宣称PRMS保存成功、不合并master。
