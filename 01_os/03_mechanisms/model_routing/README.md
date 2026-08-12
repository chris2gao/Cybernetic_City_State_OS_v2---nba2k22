# 模型能力与任务路由

这是 repository-wide 的独立全局机制。它根据任务角色、风险、任务形态、所需能力与
Human 提供的当前可用性覆盖，选择 model、product surface 与 parameter profile。
workflow 只引用本机制，不复制活动目录或路由规则。

## Canonical 组成

- `路由契约_v1.yml`：稳定输入、输出、选择顺序与权限边界；
- `模型与产品面目录_v1.yml`：带来源、新鲜度和 surface 参数证据的活动事实；
- `项目观察证据_v1.yml`：与供应商目录分离、带有效性等级的项目观察；
- `来源索引_v1.yml`：把目录中的 source token 解析到 kind 与可审计 locator；
- `实现/verify_model_routing.py`：结构、引用、新鲜度和禁止项 validator。

boot 清单位于 `../../02_boot/model_routing/启动清单_v1.yml`，执行 loader 位于
`../../06_execution/boot/model_routing/`，registry 位于
`../../05_registry/model_routing_v1.yml`。

## 边界

路由结果的 authority 永远是 `routing_only`。模型或 surface 的选择不授予文件、发布、
安全或 Human-gated 权限。本机制不定义角色，不管理上下文，不运行后台账户探测，也不维护
固定降级链；首选候选不可用时，在剩余候选中重新执行 task-fit 选择。

机制失效必须在 validator 或 loader receipt 阶段显现。缺少来源或新鲜度、重复身份、断裂
pointer、非法活动输入或不受 surface 证据支持的参数均须 fail closed。
