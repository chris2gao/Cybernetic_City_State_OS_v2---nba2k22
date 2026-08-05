# 阶段协同推演闭环启动入口

本目录只声明 staged boot 清单，不代表机制已经激活。

启动顺序由 `启动清单_v1.yml` 冻结：公共方法、profile 契约与七 profile、P2 三份机器契约、P2 receipt 来源叠加层、P3 路由失败契约和 validator。任一必需路径缺失、部分发布、版本不匹配、过期、引用未知、无效或未授权时必须 fail closed，禁止使用旧版本回退。

加载器必须先运行 static validator，再解析当前 workflow profile，之后才能验证阶段实例并发布 receipt。dormant 路线也必须产生有效 receipt。当前状态为 `staged_inert`；激活和 master 集成需要独立 Human 授权。
