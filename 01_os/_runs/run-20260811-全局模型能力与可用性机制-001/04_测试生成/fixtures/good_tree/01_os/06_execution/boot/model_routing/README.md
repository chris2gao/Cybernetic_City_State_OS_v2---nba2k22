# model_routing 执行入口（Stage 04 fixture）

> positive fixture，非 canonical。

加载：按 `01_os/02_boot/model_routing/启动清单_v1.yml` 的 `load_order` 依次读取，
然后运行清单声明的 validator。只在 Human 或获授权执行者显式调用时运行。

失败行为：fail closed。validator 非零退出即停止，不回退到旧目录、不猜测账户可用性、
不以静态 entitlement 代替 Human availability override。

receipt：记录 boot_manifest_version、mechanism_version、loaded_catalog_version、
loaded_paths 与 validator_exit_code。

不启动任何后台过程：crawler_watcher_scheduler_daemon: prohibited。
