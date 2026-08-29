# 06_execution

The loaders. Given the registry, this is where a mechanism, a workflow part, the
environment, a skill or a tool gets initialised or reloaded — so that a model picks up
the right thing, correctly, every time.

## Holds

One subdirectory per area it can load, mirroring the structure it loads from:

```
06_execution/
  workflow/      loads a workflow and its stages
  boot/          establishes the environment
  mechanisms/    initialises or reloads one mechanism
  skills/        makes a skill available and verifies it is present
  tools/         same, for tools
  task_discipline/  reports task context, verification and changed paths
```

`task_discipline/` is the one area that loads nothing. It reports: preflight state,
verification results, and the physical changed-path ledger. It is listed here because
it lives under the same `<area>/<name>/` convention and carries the same registry
obligation, not because it initialises anything.

Each loader states what it reads from the registry, what it puts in context, in what
order, and how to tell afterwards whether it worked.

## Does not hold

Definitions. A loader for the communication protocol lives here; the protocol itself
lives in `03_mechanisms/`. Keeping them apart is what allows a mechanism to be reloaded
without being rewritten.

## What "correct loading" has to mean here

Not "the files were read". The first-generation system could already prove which files
a session loaded, by receipt, and that proof was genuinely useful. What it could not
do was answer what happens when a load is partial or stale — and the cost showed up as
sessions that believed a stale routing snapshot over physical Git state.

So each loader declares its own failure mode: what a partial load looks like, and what
the model should do when it detects one. Failing loudly is a requirement, not a
nicety — this is the area whose failures would otherwise be silent by construction.

## 当前加载器

- `boot/context_management/README.md`：读取 boot 清单和 registry，注入最小活动定义，
  排除原始研究报告、运行历史与私有 scratch，并运行结构 validator。
- `boot/stage_collaborative_deliberation/README.md`：加载 active-dormant 阶段协同推演机制。
- `workflow/minimum_operational_loop/`：加载七阶段契约和七份 schema，验证上下文管理与
  阶段协同推演前置条件，并提供 static、run validation 和只读 pilot materialization。
- `task_discipline/README.md`：预检、安静验证与变更路径账本三件报告工具。
  它们不加载、不写入、不授权；registry 见 `05_registry/task_discipline_v1.yml`，
  调用约定见 `01_os/开发入口与单窗口任务规范_v1.md` 第 1.2 节。
- `boot/context_management/working_set/`：默认可见工作集计算、生命周期读取、
  引用安全扫描与通用归档搬移。`visible_set.py --list` 每次都报出隐藏了多少，
  过滤过的结果不许自称穷举；`archive_group.py` 没有 force 开关。
  契约见 `03_mechanisms/context_management/工作集与归档契约_v1.yml`。
- `task_orchestration/big_task/closure_preflight.py`：判定任务包能否作为一个大任务
  派出，并把一次拟停止分类为内部推进、真停止或未识别（按停止处理）。只报告，不授权。

加载 receipt 必须记录机制版本和实际读取项；缺项、旧版本或 stale 均失败退出。七阶段 runner
只实现确定性控制面，不生成需求、证据、B、测试、步骤或实现语义。
# 通讯系统

`boot/communication_system/` 提供显式初始化、纯校验、人工发布、单次 Git 收敛和整体归档入口。
它不启动后台进程，运行实例由任务配置的通讯根承载，不写入 canonical 机制目录。
