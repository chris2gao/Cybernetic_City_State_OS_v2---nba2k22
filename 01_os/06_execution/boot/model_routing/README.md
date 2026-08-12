# 模型路由 loader

## 读取与验证

1. 读取 `01_os/02_boot/model_routing/启动清单_v1.yml`；
2. 读取 `01_os/05_registry/model_routing_v1.yml`；
3. 严格按清单读取契约、活动目录、canonical source index 和项目观察账本；
4. 显式运行清单声明的 validator：
   `python 01_os/03_mechanisms/model_routing/实现/verify_model_routing.py static .`；
5. 将最终选择写入当前任务的 `executor_profile`，并记录机制版本、目录版本、source index
   版本、实际读取路径与 validator 退出码。

## 失败行为

缺项、部分读取、重复 YAML 键、版本或 pointer 不一致、活动事实缺少来源/新鲜度、参数缺少
surface 暴露证据，均停止路由。不得退回入口中的旧型号表，不得从账户静态 entitlement 推断
当前可用性。Human availability override 是任务时点的账户可用性权威输入。

本 loader 只在 Human 或获授权任务执行者显式调用时运行；不启动后台进程，不授予任何权限。
路由输出始终只有 `routing_only` authority。
