# 全局通讯机制

本目录保存供应商无关的 canonical 通讯契约。V1 只定义文件结构、校验规则和
Human 手工转交过程；它不轮询、不监听、不自动投递、不自动确认，也不推进任务状态。

运行时实例不写入本目录。公开任务空间位于确定性解析的机器全局通讯根：显式 `--root`
优先，其次是环境变量 `CITYSTATE_COMMUNICATION_ROOT`，两者都没有时使用
`Path.home() / ".citystate" / "communication"`。每个仓库再使用 `<repository_id>/`
分区。需要 Web 端读取、
Human 明确要求或整任务收敛时，才由当前 task scope 内的执行者把 `repository_shareable` 文件发布到
当前任务分支的 `01_os/_communication/<repository_id>/`。本 Stage06 不在该逻辑载体中
创建任何 live state。

结构主契约仍为 `citystate.communication.contract.v1`；新 formal action 接入使用
`正式动作接入契约_v1.yml` 与 `Human中转指针契约_v2.yml`。新发布必须经过
mechanism-activation resolver/gate，产生 sender-owned constitution evidence 与 compliance
receipt，并输出带 receiver setup 的 v2 pointer。九字段 v1 pointer 仅供显式历史读取。
启动入口、验证器和人工发布工具位于 `01_os/06_execution/boot/communication_system/`。

普通 formal handoff 不需要 Human task-authority、授权码、nonce 或 recipient delegation。
`confirmation_ref` 仅用于需要跨窗口重放的 confirmation-bound protected action；
`authorization_ref` / `recipient_delegation_ref` 保留为历史兼容字段。
