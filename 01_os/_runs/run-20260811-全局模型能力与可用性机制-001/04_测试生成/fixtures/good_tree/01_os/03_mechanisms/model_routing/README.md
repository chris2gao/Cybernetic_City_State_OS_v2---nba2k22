# 全局模型能力与任务路由机制（Stage 04 fixture）

> 本文件是 Stage 04 冻结测试的 **positive fixture**，不是 canonical 实现。
> 它存在的唯一目的，是证明 28 条验收检查在一棵满足契约的树上确实全绿，
> 因而它们的红不是"检查本身写坏了"。Stage 05/06 的真实实现不得复制本文件。

## 职责

按当前任务的 role / risk_tier / task_shape / required_capabilities 与 Human
availability override，选出 model + product surface + parameter profile，并给出
routing basis、evidence refs 与 limitations。输出的 authority 恒为 `routing_only`。

## 谁加载

`01_os/02_boot/model_routing/启动清单_v1.yml` 声明加载顺序；
`01_os/06_execution/boot/model_routing/` 是执行入口说明；
`01_os/05_registry/model_routing_v1.yml` 记录用途、loader 与失效显现方式。

## 磁盘依赖

本目录的路由契约、模型与产品面目录、项目观察证据三份文件，以及 `实现/` 下的
结构 validator。没有其他磁盘依赖，不读取账户状态，不访问网络。

## 失效如何显现

validator 在下一次运行时 fail closed：schema 不符、pointer 断裂、重复 key、
registered 条目缺 source/verified_at/invalidation/confidence、mechanism_version
三处不一致，均以非零退出码显现。crawler_watcher_scheduler_daemon: prohibited。
