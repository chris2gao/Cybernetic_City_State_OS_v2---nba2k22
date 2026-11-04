# task_orchestration — 默认大任务与长时执行

一份契约、一个校验器。它决定**任务的粒度**，不决定任务的内容，也不授予任何权限。

项目资料发现、同候选索引同步、精确HEAD交接和同签名失败预算，引用
`../context_management/项目资料发现与索引同步契约_v1.yml`及
`../../06_execution/task_discipline/project_context/`。此处不复制目录、状态服务或审核机制。

| 文件 | 作用 |
|---|---|
| `大任务与长时执行契约_v1.yml` | canonical 机器契约：内部 continuation 集合、真停止集合、闭合前检查必填项 |
| `01_os/06_execution/task_orchestration/big_task/closure_preflight.py` | 校验任务包是否可作为大任务派出；把一次拟停止分类为内部推进或真停止 |

## 为什么存在

碎片化有可测的账单，不是风格偏好：

- **状态被写坏。** `01_os/开发入口与单窗口任务规范_v1.md` 第 5 节声明了七个合法的
  run 生命周期值。实测 `d9a18b57` 上 50 个 run 组写出 **24 种互不相同**的自由文本
  状态字符串，且几乎都写在 `status:` 而不是 `lifecycle:` 下，能被机器判为终态的是
  **0 个**。每个小窗口各自即兴写一个状态词，没有谁需要和别人对齐。
- **入场费被重复支付。** 每个新窗口都要重跑一次 repository re-entry，
  bootstrap 固定读 61,534 字节 / 1,068 行。
- **归档因此从未发生。** communication 的归档机制早就存在，`archive/` 至今为空——
  缺的不是搬移代码，是"这个任务已完成"的机器判据。

## 两条边界

**不该停的**：确定性施工、验证、本任务造成的失败的确定性修复、证据更新、
清理、task-branch commit/push、completion 收尾。为这些反复回来问 Human 是禁止的。

**必须停的**：新的语义选择、越出 allowed paths、未覆盖的 protected action、
安全/隐私/secret、破坏性 Git 或改写历史、runtime 激活、需要 Human relay 转给另一个
独立模型、证据支撑不了声明。

其中最常被搞错的一条写死在契约里：**普通 task branch 的发布不是停止条件。**
把它当 Human 门，会让每一个以 pushed completion pointer 收尾的实现任务都被误判为
受保护动作。

## 默认内部迭代与系列审核

WorldData 的 Codex 工程任务 `nba2k22-world-data-full-implementation-01` 在同一大任务下记录 37 个增量：每轮交付一个有界可运行改进，保留 Native/SQLite 证据、单测/负例、候选SHA和未证缺口，继续选择下一最有价值的改进，最终按 Human 缩小的范围集中验证并冻结常规赛候选。其独立审核、全生命周期验收保持未完成。**复制的是“有证据的继续/停止决策”，不是固定37轮或无止境循环。**

这一迭代原则统一记录在 `大任务与长时执行契约_v1.yml` 的 `evidence_driven_iteration`；新的长任务在任务包声明具体可测增量与收敛证据，默认施工内部修复与继续。**独立审核仍是最终验收岗位**，可按 `01_os/开发入口与单窗口任务规范_v1.md` 第9节安排系列里程碑集中审核，只有承重依赖、正式 Workflow 完成门、高影响边界等触发即时审核。二者不是不同审批体系。本契约不授予进程、游戏、存档、master 或 protected action 的额外权限。

## 大不等于危险

任务规模本身不产生授权需求。`known_protected_actions: []` 是合法的闭合前检查结果。
只有当拟执行动作落进 protected 集合、且当前授权未覆盖它时，才需要新的 Human 授权。

## 边界

- 本机制**没有** `01_os/02_boot/` 启动清单：该路径不在产生本机制的任务的
  `allowed_changed_paths` 内，执行者不自行扩边界。是否需要 boot manifest 留作后续
  finding。当前由 `01_os/05_registry/task_orchestration_v1.yml` 注册。
- `closure_preflight.py` 只报告，不授权。它说"这个包可以作为大任务派出"，
  不等于任何动作被允许；权限仍只来自当前 Human 指令与 canonical 协议。
- 契约不新增停止条件。正本是开发入口第 11 节；本契约只是它的编排视角投影。

## 测试

```bash
python -m pytest 01_os/06_execution/task_orchestration -q
```

## Development Loop evidence (opt-in, read-only)

`loop_iteration_schema_v1.json` is the strict per-iteration record. Run the deterministic
`01_os/06_execution/task_orchestration/big_task/loop_observability.py` against
an immutable JSONL with `--input LOG --format strict --report DERIVED.json`.
It reports authority_effect=none and never modifies the source log. Exit codes:
0 = strict validated; 1 = evidence/validation findings; 3 = malformed input or output error.
A strict PASS is syntactic and internally consistent; it does not independently verify
receipt authenticity or replace independent review or Human authorization.

Historical read-only compatibility is `--format legacy_g2_s0` (2026-11-01 four rounds)
and `--format legacy_season_host` (2026-11-02 eight rounds). `--format auto`
detects homogeneous logs. Supply `--task-id` and `--source-ref` only as explicit
provenance from immutable `run.yml`/Git SHA, never as invented original fields.
Historical PASS/status or test-count assertions without actual exit codes remain
`LEGACY_EVIDENCE_MISSING`; compatibility is not strict audit acceptance.
See existing `closure_preflight.py` for the canonical `internal_continuation`,
`genuine_stop` and lifecycle enums; this CLI creates no parallel stop gate.

Tests: `python -m pytest 01_os/06_execution/task_orchestration -q`.
