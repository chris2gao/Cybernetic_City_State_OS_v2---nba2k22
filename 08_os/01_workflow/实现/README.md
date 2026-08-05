# 七阶段工作流 · 最小运行实现

本目录保存跨阶段的最小机器契约。它只实现确定性控制面：阶段顺序、类型化产物、
版本与哈希、协同推演 receipt、冻结测试、执行 allowlist、重试/上游失效、独立验证和完成。

它不生成需求、证据、B、测试或实现内容，也不宣称模型判断是确定性的。七个阶段各自的
`实现/最小运行schema_v1.yml` 定义本阶段产物；统一 runner 位于
`08_os/06_execution/workflow/minimum_operational_loop/`。
