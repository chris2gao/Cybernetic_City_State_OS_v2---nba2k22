# mutmut 系统职责与收益

## 决定

mutmut `3.6.0` 可作为 core 的 `verified_on_demand` 外部工具，但只允许经
canonical WSL wrapper 对显式 allowlisted 的一个 Python 文件运行。它不进入默认
boot，不暴露为 MCP，不常驻，也不拥有 source mutation 的写回权限。

## 已证收益

校准证明它能区分真实测试缺口与等价 mutant。真实 OS schema-reference inspector
在测试增强后把 survivor 从 11 降到 2；最终两项都能用 Python stdlib 行为给出
可执行等价性证明。输出把源代码与测试的较大审阅面压缩为 survivor 摘要，可降低
后续模型需要阅读的上下文表面。

这个结论是“context proxy”，不是精确 token 计量。exact model tokens 与可靠的
整棵进程峰值内存不可观测，因此保持 `not_observable`，不作节省比例承诺。

## 风险边界

- mutation score 不是正确性证明；survivor 需要 Human/模型语义判断。
- 高阶动态行为、C 扩展、非 fork 平台或全仓库 mutation 不在本次验证范围。
- virtualenv 与 WSL workspace 是机器前置条件；registry 只提供发现和调用契约。
- 版本、Python、wrapper、target config 或测试语义变化后必须完整复验。
