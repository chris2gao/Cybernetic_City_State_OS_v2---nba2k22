# 03_mechanisms

General reusable capabilities. Each mechanism is self-contained: it can be described,
loaded and verified on its own, and a workflow references it rather than reimplementing
it.

## Holds

One subdirectory per mechanism. The communication protocol is one. Release binding,
lane coordination, and compliance validation are others in the first-generation system.

Each mechanism directory should be able to answer, from its own contents: what it does,
what loads it, what it needs on disk, and how a break would show up.

## Does not hold

Workflow-specific steps. If it only makes sense inside one workflow, it is a workflow
stage, not a mechanism.

## The one property every mechanism here must declare

**When a failure surfaces.** This is the field the first-generation system lacked and
paid for twice. A missing test fixture turns the suite red on the next run. A missing
permission policy produces no signal at all — the system simply stops refusing things,
and nobody learns of it until something that should have been refused happens.

A mechanism whose breakage is silent needs a registry entry more than one whose
breakage is loud, not less.

## Candidates for porting

The communication protocol stack, the release binding cycle, the lane epoch mechanism
and the compliance validator all work in the first-generation system and all have
measured failure histories worth carrying over with them. Porting is selective:
assessed one at a time, not copied wholesale.

## 当前机制

- `context_management/`：全局上下文管理、文件隔离、产物生命周期、发布边界与结构验证。
- `model_routing/`：模型、产品 surface 与参数档案的证据化 task-fit 路由；输出仅具
  `routing_only` authority。
- `mechanism_activation/`：formal-action constitution、机制触发、pre-action gate、
  L0–L4 生效盘点与 material claim 期望—观察—comparator 双向绑定。
- `task_orchestration/`：默认大任务与长时执行；内部 continuation 与真停止的边界、
  闭合前检查、终态生命周期声明。`authority_effect: none`。

工作流只引用该机制，不在 `01_workflow/` 内保留第二份实例。

累计面的可见性与归档不是独立机制：它属于 `context_management/`，见
`context_management/工作集与归档契约_v1.yml`。放在那里是因为"哪些内容属于哪个
生命周期类"本来就是上下文管理的职责，新建第二个机制会把同一职责劈成两半。
# 全局通讯机制

`communication_system/` 定义每任务公开通讯空间、端点与消息契约、精确引用、人工发布、
Git 收敛、导航和整体归档。新 formal action 使用 v2 pointer、constitution evidence、
compliance receipt 和 receiver setup；canonical 机制目录只保存定义，不保存 live state。
