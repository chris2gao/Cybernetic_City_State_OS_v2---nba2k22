# Cosmic Ray

## 已验证形态

- 版本：`8.4.6`
- Python：WSL2 Ubuntu user-space `3.14.4`
- test runner：同一专用 virtualenv 中的 `pytest 9.1.1`
- validation parser：同一专用 virtualenv 中的 `PyYAML 6.0.3`
- virtualenv isolation：`include-system-site-packages = false`
- 安装边界：专用 user-owned virtualenv；不使用 `sudo`，不改系统 Python 或 PATH
- 挂载：`verified_on_demand`
- 默认加载：否
- MCP 暴露：否
- 证据：`08_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行/results.json`

## OS 职责与增量价值

Cosmic Ray 是 mutmut 的补充 mutation engine，不是替代品。它在 run-014 中覆盖了
mutmut 未生成的 decorator removal、模块级入口比较和更宽的 comparison/binary
operator 集合：强断言校准的 68 个对象为 56 killed、12 survived；真实
`inspect_schema_refs.py` 目标的 58 个对象为 41 killed、16 survived、1 worker
exception。16 个 survivor 经可执行证明分为 12 个注解或当前可达上下文等价项，
以及 4 个真实语义缺口。

同输入 mutmut 真实目标产生 129 个对象（127 killed、2 个已证明等价 survivor）。
因此两个工具的 operator reach 互补：mutmut 仍是更快、更密集的常规默认 mutation
工具；Cosmic Ray 只在任务需要 decorator、模块入口或第二引擎交叉验证时显式调用。

## 强制调用边界

所有 canonical 调用必须经过
`08_os/06_execution/tools/cosmic_ray/invoke.sh`。wrapper 固定 Cosmic Ray `8.4.6`、
Python `3.14.4`、pytest `9.1.1`，并要求 `pyvenv.cfg` 明确且唯一声明
`include-system-site-packages = false`。它只接受
WSL Linux 文件系统中的干净 Git worktree、一个 repository 内 Python 文件、一个
完全匹配的 allowlist 条目、一个 repository 内测试文件和一个 repository 外的
Linux receipt 目录。它只启用 `local` distributor、单 worker、显式 mutation timeout
与 session 对象上限，并先清除 `PYTHONPATH`、`PYTHONHOME`、`PYTHONUSERBASE`，再运行
baseline pytest。版本探测失败只输出固定诊断，不回显不受信任的 probe 输出、可执行路径
或用户目录。

Cosmic Ray 8.4.6 的原生 session 会把真实 timeout 写成 `test_outcome=killed`、
`worker_outcome=normal`，仅在 output 留下 `timeout`。canonical summary helper 会把它
重新分类为 `timeout`；任何 timeout、incomplete、incompetent 或 worker error 都使
wrapper fail closed（退出 `72`），不得计入 killed。

## 成本与限制

- 专用 venv：`73,253,524` bytes、`3,755` regular files（最终修正复验时点）。
- 同一真实目标的 mutation exec：Cosmic Ray 两次约 `35.07s`、`39.07s`；mutmut
  两次约 `17.84s`、`13.02s`。
- Cosmic Ray 会对 `from __future__ import annotations` 下的注解表达式生成大量运行时
  无效 mutation；survivor 必须逐项分类。
- 只验证了 local distributor 和单 worker；HTTP distributor、远端 worker、`/mnt/**`
  工作区和多目标扫描均不在准入范围。
- exact model token 与可靠的整棵进程峰值内存不可观测。source+test 字节只能作为
  `proxy_not_billing_tokens`，不得写成 token 账单。

升级 Cosmic Ray、Python、pytest、wrapper/summary、local distributor、目标配置或
测试语义后，必须重新运行 run-014。卸载仅删除专用 virtualenv；不得删除 run evidence。
