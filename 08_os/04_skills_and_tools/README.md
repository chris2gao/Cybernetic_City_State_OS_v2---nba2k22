# 04_skills_and_tools

External skills and tools that extend what a model can do here. Bolted on rather than
built in: the system works without them, and works better with them.

## Holds

- skill definitions the model can invoke
- tool wrappers and their usage contracts
- for each: what it requires to be installed, and how to check that it actually is

## Does not hold

Mechanisms the system itself runs on. If the city-state cannot operate without it, it
is a mechanism, not an extension.

## The check that must not be skipped

**Availability is measured, not assumed.** The first-generation system instructed every
agent to search with `rg`, on a workstation where `rg` was not installed. The
instruction sat there being wrong until someone checked. A separate note recorded
PowerShell behaviour that belonged to a version that was not the one running.

Every entry here declares how to verify the tool is present and at what version, and
that check is part of the entry rather than a note beside it.

## Human documents

- [工具选型_v1.md](工具选型_v1.md)：run-005 形成的候选与替代路线快照。
- [确定性工具接入收益与风险评估_v1.md](确定性工具接入收益与风险评估_v1.md)：
  安装前的收益、风险、资源、按需加载与准入测试决策依据。

这两份文档只用于 Human 定向审阅。当前没有因这些文档而安装、激活、
暴露、加载或调用任何候选工具；长评估文档也不进入默认 boot。

## Verified on-demand tools

- [check-jsonschema](check-jsonschema/README.md)：`0.37.4`，通过 run-012
  独立安装真实性、正负例、重复性与 fail-closed wrapper 验证。
- [mutmut](mutmut/README.md)：`3.6.0`，通过 run-013 在 WSL Linux 文件系统、
  独立 virtualenv、`fork`、校准样本与一个真实 OS Python 目标上验证；仅在任务
  显式给出单文件 allowlist 时按需调用。

已验证工具仍不进入默认 boot，不暴露为 MCP，也不因登记而自动调用。任务必须通过
registry 发现并显式调用 canonical wrapper。
