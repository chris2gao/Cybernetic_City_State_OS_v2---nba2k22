# 全局通讯机制

本目录保存供应商无关的 canonical 通讯契约。V1 只定义文件结构、校验规则和
Human 手工转交过程；它不轮询、不监听、不自动投递、不自动确认，也不推进任务状态。

运行时实例不写入本目录。公开任务空间位于配置的机器全局通讯根；需要 Web 端读取、
Human 明确要求或整任务收敛时，才由获授权执行者把 `repository_shareable` 文件发布到
当前任务分支的 `01_os/_communication/<repository_id>/`。本 Stage06 不在该逻辑载体中
创建任何 live state。

当前契约版本为 `citystate.communication.contract.v1`。启动入口、验证器和人工发布工具
位于 `01_os/06_execution/boot/communication_system/`。

