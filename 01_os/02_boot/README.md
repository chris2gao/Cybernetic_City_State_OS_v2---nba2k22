# 02_boot

Environment information and the mechanisms that establish it. What a model needs to
know before it can do anything, and what manages that knowledge over time.

## Holds

- environment description: which tools exist, which shells, which paths, what is
  installed and at what version
- context management: what is loaded when, lazily or eagerly, and what is dropped
- global state that is true across every workflow rather than within one

## Does not hold

Per-mechanism logic. If it only matters when one mechanism runs, it belongs with that
mechanism.

## Carried over from the first-generation system

The old repository solved parts of this and the solutions were paid for:

- lazy loading rather than whole-repository preloading
- a fixed bootstrap file set, verified by receipt, so that what was loaded is provable
- the separation of instruction authority from state freshness — two orderings that
  must not be merged into one table
- environment facts must be measured, not assumed: the old system recorded a tool as
  present on `PATH` when it was not, and the note stayed wrong for weeks

These are candidates for porting, not decisions. Each needs assessing on its own.

## 当前启动入口

- `context_management/启动清单_v1.yml`：上下文管理加载顺序、版本与失败行为；
- `context_management/README.md`：入口边界与 receipt 要求。
- `communication_system/启动清单_v1.yml`：Human 中转通讯契约与纯校验入口；加载时不创建运行实例。
- `mechanism_activation/启动清单_v1.yml`：formal-action constitution、触发 resolver、
  pre-action gate 与双向物理事实绑定；formal action 时 always-on，加载不授权、不执行机制。
- `model_routing/启动清单_v1.yml`：任务时点模型路由与 Human-visible receiver setup；
  不进行后台账户或配额探测。
- `minimum_work_unit_output/`、`stage_collaborative_deliberation/`、
  `workflow_minimum_operational_loop/`：各自机制的读取清单。
- `task_orchestration/启动清单_v1.yml`（2026-11-18 新增）：任务编排的精确读取清单。
- `os_entry/`（2026-11-18 新增）：B0 入口的读取分层。启动必读是 `AGENT_WORKING_DISCIPLINE.md`、`AGENTS.md`、`01_os/README.md` 与开发入口；同目录的 `开发入口_按动作细则_v1.md`（开发入口按原节号移出的按动作部分）与 `入口依据与事故记录_v1.md`（B0 原有的事故、实测与理由）按动作读取；`CORE_MANIFEST.yml` 为程序读取。
- `task_continuity/`、`task_discipline/`、`publication/`、`skills_and_tools/`、`domain_content/`（2026-11-18 新增）：原来没有 boot 的 skill 单元的读取分层。

每份启动清单的 `read_tiers`（启动必读 / 按动作读取 / 程序读取 / 有则必读）是该单元“读什么”的唯一来源，由 `06_execution/skills/generate_skills.py` 生成为对应的机制 skill；`load_order` 等原有键不变，仍是机制自身 validator 的输入。角色 skill 按角色组合这些机制 skill（角色矩阵在 `01_os/05_registry/skills_v1.yml`）。

启动区只声明“启动时读什么”；机制方法论和生命周期定义位于
`../03_mechanisms/context_management/`。
