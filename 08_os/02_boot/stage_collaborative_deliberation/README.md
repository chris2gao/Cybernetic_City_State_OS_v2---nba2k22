# 阶段协同推演闭环启动入口

本目录声明当前 active-dormant boot 清单。机制已全局激活为可发现、可加载状态，但默认路线仍为 dormant，不会自动创建讨论 session。

启动顺序由 `启动清单_v1.yml` 冻结：公共方法、profile 契约与七 profile、核心机器契约、receipt 来源叠加层、append-only 激活状态、Human 激活授权、v1 基础 validator 与 v2 当前 validator。任一必需路径缺失、部分发布、版本不匹配、过期、引用未知、无效或未授权时必须 fail closed，禁止使用旧版本回退。

加载器必须先运行 v2 static validator，再解析当前 workflow profile，之后才能评估 trigger、验证阶段实例并发布 receipt。未命中触发条件时走 dormant 路线且仍必须产生有效 receipt；命中 full 或 incremental 条件时仍须满足当前任务的 profile gate 与权限。全局激活不授权外部行动或不可逆操作。
