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

启动区只声明“启动时读什么”；机制方法论和生命周期定义位于
`../03_mechanisms/context_management/`。
