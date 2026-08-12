# 01_workflow（Stage 04 fixture 摘录）

> positive fixture，非 canonical。

workflow 只负责阶段顺序、输入输出、失效回退与机制调用时点。模型目录、参数档位与
路由规则不在此处保存；阶段需要路由时调用
`01_os/03_mechanisms/model_routing/` 的契约，不复制目录内容。
