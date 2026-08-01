# Cosmic Ray 系统职责与收益

## 决定

`verified_on_demand`。安装成功本身未参与准入理由；资格来自稳定 Python 3.14.4
runtime、四阶段对象级重复、decorator/timeout 语义、30 项 fail-closed wrapper、
canonical blob 不变，以及相对 mutmut 的真实增量。

## 增量与代价

Cosmic Ray 在 calibration 发现 mutmut 跳过的两个 decorator removal 对象，并在真实
目标找到 4 个可执行证明的入口/参数/后缀语义缺口；这足以作为第二引擎的实际增量。
代价是：真实目标 exec 约为 mutmut 的 2–3 倍，专用 venv 更大，16 个 survivor 中
12 个是注解或当前上下文等价噪声，而且 8.4.6 原生把 timeout 误记为 killed。

因此它不是常规默认 mutation tool。mutmut 继续承担更快、更密集的常规 mutation；
Cosmic Ray 仅在 decorator、模块入口、operator diversity 或独立引擎交叉验证值得额外
成本时使用，并且必须通过 canonical wrapper。native CLI 直连不属于已验证入口。

## 安全结论

wrapper 在 init 前完成 exact version、clean worktree、Linux filesystem、realpath
containment、单 `.py` allowlist、pytest baseline 和 receipt 边界检查；所有 mutation、
config、SQLite 与 source 写入都位于 `/tmp` Git archive。timeout、incomplete、
incompetent、worker exception 和解析失败不会计为 killed；它们生成结构化 receipt 并
非零退出。两次 success、真实 timeout、真实 worker exception、cleanup 与 no-process
证据均通过。

## 复验触发器

Cosmic Ray/Python/pytest 版本、wrapper/summary、local distributor、target 配置或
test semantics 任一变化，都必须重跑 run-014。HTTP distributor、远端 worker、
`/mnt/**`、多目标 mutation 和 canonical apply 仍未获准。
