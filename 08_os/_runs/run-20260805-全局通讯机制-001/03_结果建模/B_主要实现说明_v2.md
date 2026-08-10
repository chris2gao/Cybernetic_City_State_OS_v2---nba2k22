# B 主要实现说明 v2

状态：阶段三共同审阅材料，不是已确认规范。

## 一、系统解决什么问题

该机制不负责自动投递、自动推进任务或授予权限。它负责让 Human、架构/决策模型、独立审核模型、执行模型、Desktop、CLI 与 Web 模型在同一 task 中，通过本地文件或当前任务 GitHub 分支交换完整、准确、可定位的信息，同时避免把长内容持续复制进聊天上下文。

## 二、角色与上下文如何结合

上下文机制已有三种信息平面：角色有效上下文、耐久系统事实、事件与审计。通讯机制只负责为角色提供精确入口与 handoff，不另造新的通用 coordinator 角色。

### 架构与决策角色

建议承担 `task_navigation_owner` 职责：

- 创建或确认 task 通讯空间；
- 维护 manifest 与 Human/current；
- 决定是否需要本地—GitHub 收敛；
- 在冲突、阻塞、角色不明或越权请求时作出架构判断，必要时交给 Human；
- 任务完成时决定进入归档流程。

这些是导航职责，不自动授予业务文件修改、发布或其他受保护权限。

### 独立审核角色

- 使用独立上下文入口；
- 只发布自己的消息、审核文档和 sender index；
- 不维护执行模型的消息，不维护全局共享消息索引；
- 输出审核结论、纠正请求或阻塞消息。

### 执行角色

继续使用现有 Codex / Antigravity 等后端执行角色：

- 按 task 授权执行文件修改和测试；
- 发布自己的执行消息、报告和 sender index；
- 不因收到通讯消息而获得新权限；
- 超出角色范围时必须读取独立 Human 授权。

### Human

- 决定实际转发给哪个端点；
- 决定是否上传 GitHub、是否触发全量收敛、是否归档；
- 决定越权授权、冲突处理和任务链是否继续。

## 三、当前建议目录

每个 repository 的通讯根分为活动任务和归档任务：

```text
<communication_root>/<repository_id>/
├─ active/
│  └─ <task_id>/
└─ archive/
   └─ <task_id>/
```

每个活动 task：

```text
<task_id>/
├─ manifest.yml
├─ endpoints/
├─ Human/
│  ├─ current.yml
│  └─ decisions/
├─ durable/
│  ├─ final_results/
│  └─ material_failures/
├─ indexes/
│  └─ <sender_endpoint_id>.yml
├─ messages/
│  └─ <sender_endpoint_id>/
└─ documents/
   └─ <sender_endpoint_id>/
```

模型私有草稿、缓存和临时分析不放入该公开 task 文件夹，而放在上下文机制规定的未跟踪 `_runtime/` 或仓库外工作区。公开 task 文件夹因此可以整体归档，不需要逐文件判断哪些提升、哪些删除。

## 四、sender index 与序号

每个 sender 在每个 task 中拥有独立 index、消息目录和文档目录。

序号范围：`00001`–`10000`。

序号绑定 `task_id + sender_endpoint_id`，新 task 从 `00001` 重新开始。归档保留旧 task 的完整 index，但旧 index 不进入新 task 默认上下文。

如果未来取消 task 绑定，才需要扩大到 1,000,000；当前不采用该方案。

## 五、canonical message 是什么

`canonical message` 不是聊天内容，也不是某个 CLI 命令。它是系统认可的正式消息文件：

- 有固定最小字段；
- 有明确 sender、预期接收 endpoint 和预期角色；
- 有不可变 message_id；
- 长内容通过 required_refs 外置；
- 可以由 validator 机械检查；
- 发布后不原地修改，纠正通过新消息完成。

当前建议字段：

```yaml
message_id:
task_id:
title:
message_type:
sender_endpoint_id:
sender_task_role:
expected_recipient_endpoint_id:
expected_recipient_task_role:
content:
requested_action:
required_refs:
```

角色字段只用于选择正确上下文和判断职责，不授予权限。validator 应核对角色字段与 endpoint card 是否一致。

### canonical 与发布工具的关系

canonical 性来自“文件形态 + validator 规则”，不是来自某一个特定工具。

建议采用 endpoint-native 发布：

- Desktop / CLI 本地模型：通过终端脚本或 Git/GitHub CLI 写文件、分配序号、更新 sender index；
- Web 模型：通过已授权 GitHub connector/API 写同一形态的文件和自己的 sender index；
- Human 手工上传：仍必须满足同一文件契约并在后续验证中通过。

本地可以提供 `publish` helper，把序号分配、YAML 安全写入、index 更新和校验机械化；但不把“必须运行该 CLI”作为 Web 端协议前提。

## 六、Human/current 的作用

`Human/current.yml` 是 task 的极简 Human 导航页，不是消息状态机，也不是每条消息的摘要。

建议只包含：

```yaml
task_id:
title:
current_stage_or_checkpoint:
important_refs:
pending_Human_decision:
last_material_update:
```

作用：

1. Human 不需要扫描多个 sender index 才知道任务现在处于哪里；
2. 新窗口或决策模型恢复时，有一个稳定入口；
3. 重大阻塞、待决事项和最终结果可以直接定位；
4. 不复制消息正文，因此维护成本低。

建议由架构与决策角色独占维护，只在任务开始、Human 决策、重大阻塞/风险、阶段完成、最终结果和 Human 明确要求时更新。普通消息不更新。

## 七、requested_action 的作用

它把“信息是什么”与“希望接收方做什么”分开，避免接收模型从长文本中猜动作。

建议：

- `request`：必填；
- `decision_required`：必填；
- `blocked`：必填，写明需要谁补什么；
- `response`、`result`、`correction`：可选，通常省略。

## 八、长文档 front matter 的作用

新建的通讯长文档建议强制最小 front matter：

```yaml
---
document_id:
task_id:
author_endpoint_id:
author_task_role:
purpose:
privacy_class:
---
```

作用：

- 不读取正文即可确认文档属于哪个 task、由谁创建、用途是什么；
- GitHub 发布前可机械检查 privacy class；
- 接收模型可以快速判断是否需要读取；
- 归档、纠正和引用时不依赖文件名猜测。

已有源码、规范、测试、任务文件不需要为了被引用而重写 front matter；消息可以直接引用现有资源。

## 九、本地与 GitHub 如何工作

### 默认

默认发布到本地活动 task。

### 发布到 GitHub 的触发条件

满足任一条件：

1. expected recipient 是 Web 模型；
2. Human 明确要求；
3. Human 或架构/决策角色触发本地—线上完整收敛。

### 完整收敛

不进行语义级逐文件比对，使用同一 task 分支的普通 Git 收敛：

1. 只处理该 task 的 repository_shareable 文件；
2. 获取当前远端分支状态；
3. 合并顺序执行期间远端已发布的其他 sender 独占目录；
4. 提交本地最新 task 文件；
5. push 当前 task 分支；
6. 将最终远端 head fast-forward 到本地副本。

正常顺序执行中不应出现同一路径冲突。若出现冲突，说明 sender 所有权、执行顺序或共享文件写入设计存在问题；停止自动处理，交给架构/决策角色和 Human。

## 十、任务完成与归档

建议用整体归档取代逐文件 cleanup：

1. 确认任务最终结果、Human 决定和重要失败已写入 task；
2. 确认 private `_runtime` 不属于公开 task 归档；
3. 将 `active/<task_id>/` 整体移动到 `archive/<task_id>/`；
4. 更新 repository 级发现入口，使该 task 不再属于 active；
5. 新 task 使用新的目录和从 00001 开始的 sender index。

本地归档通常是目录重命名；Git 中同一 blob 的路径移动不会复制文件正文，成本通常低于逐文件分析和提升。归档保留历史，但默认加载器只读取 active task 或 Human 指定的 archived task。

## 十一、当前必要与非必要

### 必要

- task 隔离；
- 角色化上下文入口；
- sender 独占目录和 task-bound index；
- canonical message；
- 长内容外置；
- direct required refs；
- Human 手动路由；
- 权限独立；
- endpoint-native 发布；
- deterministic validator；
- active/archive 分区；
- 冲突 fail-closed。

### 当前不必要

- 自动 watcher；
- 自动投递；
- actual recipient 或已读状态；
- 共享全任务消息 index；
- 内容级自动双向合并；
- 每条消息 timestamp / digest；
- OS 级不可变；
- 逐文件 durable 提升与 cleanup；
- 为通讯机制新造 coordinator 角色。
