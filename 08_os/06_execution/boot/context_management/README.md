# 上下文管理 loader

## 读取

1. `08_os/02_boot/context_management/启动清单_v1.yml`
2. `08_os/05_registry/context_management_v1.yml`
3. 清单按序引用的 OS、开发规范、机制入口、生命周期和布局契约
4. `08_os/03_mechanisms/context_management/实现/verify_context_structure.py`

活动 D2 仅从清单声明的 `08_os/_dev/决定_谁执行_v0.2.md` 加载。

## 注入与排除

注入当前机制版本、D2 v0.2、最小活动规则和任务声明的获准引用。默认排除原始
Deep Research、完整 run 历史、其他角色 private/scratch、D2 v0.1 等旧设计与聊天历史。

## 失败

缺项、清单/registry 版本不一致、引用不存在、validator 非零、部分读取或入口 stale 均
停止加载。不得退回旧 workflow 路径或用完整历史猜测。receipt 必须证明
`boot_manifest_version`、`mechanism_version`、实际读取路径和 validator 退出码。
