# task_discipline — 任务纪律工具

三个只读或只报告的执行辅助工具。它们**不授权任何动作**，只把每次任务都要重复付出的
三类成本收敛成一次调用。

| 工具 | 入口 | 一句话 |
|---|---|---|
| 预检 | `preflight/preflight_task_context.py` | 开工前一次性给出真实 HEAD、门禁、allowlist、禁止项、工作区状态 |
| 安静验证 | `quiet_verify/quiet_verify.py` | 跑一组检查，通过只留一行，失败才展开尾部输出 |
| 路径账本 | `path_ledger/changed_path_ledger.py` | 从 Git 生成规范化 UTF-8 变更路径集合，并与任务包 allowlist 求子集 |

## 为什么存在

这些不是通用工具，是对已发生事故的收敛：

- **路径账本**：`git status --porcelain` 默认把未跟踪目录折成一行；`core.quotepath`
  默认把中文路径打成八进制转义。本仓路径大量是中文，手写路径清单因此会静默出错，
  并且真出过错。工具一律用 `-z`（NUL 分隔，永不加引号）并强制展开未跟踪目录，
  所以无论仓库配置怎样，它的答案都不变。
- **安静验证**：通过的检查不需要打印它的全部输出。绿的时候几行，红的时候才给证据。
- **预检**：同一批事实过去要十几次工具往返分别去取，每次都重新携带全部上下文。

## 退出码

| 工具 | 0 | 1 | 3 |
|---|---|---|---|
| preflight | 预检完成且硬前提成立 | 硬前提失败（工作区脏、hook 守卫不符、HEAD 非声明 base 后代、分支不符、master 已移动） | 输入或 git 错误 |
| quiet_verify | 全部检查符合预期退出码 | 有检查不符 | 输入错误 |
| path_ledger | 账本生成；给了 allowlist 则全部在内 | 有路径越出 allowlist | git 或输入错误 |

## 用法

```bash
# 开工前
python 08_os/06_execution/task_discipline/preflight/preflight_task_context.py \
    --packet 08_os/_runs/<run-id>/01_任务输入/任务包_v1.yml

# 有授权门时一并核
    --gate 08_os/_runs/<run-id>/06_执行/Human授权_进入阶段六_v1.yml \
    --gate-key authorization.enter_stage_06_execution

# 验证
python 08_os/06_execution/task_discipline/quiet_verify/quiet_verify.py

# 收尾路径账本
python 08_os/06_execution/task_discipline/path_ledger/changed_path_ledger.py \
    --base <exact_base_sha> --packet 08_os/_runs/<run-id>/01_任务输入/任务包_v1.yml
```

## 复核状态与已知缺陷

第一次独立复核结论是 **REJECT_CORRECTION_REQUIRED**。两个假阴性缺陷已修，
两个未修。完整记录见
`08_os/_runs/run-20260809-任务纪律工具-001/08_独立复核/独立复核结论摘要与Human裁决_v1.yml`。

| 编号 | 工具 | 缺陷 | 状态 |
|---|---|---|---|
| F1 | path_ledger | 跨提交 rename 只报新路径，旧路径不出现（假阴性） | **已修**：`--no-renames`，改名呈现为 delete + add；3 个回归测试 |
| F2 | preflight | `--no-remote` 时未核验 master，摘要仍打印 `ok` | **已修**：master 核验三态化，未核验即阻塞，除非显式 `--accept-unverified-master`，且摘要如实标注 |
| F3 | preflight | 授权门接受 YAML 1.1 裸 `yes` / `on`，却拒绝字符串 `'true'` | 未修 |
| F4 | quiet_verify | 失败输出只按行封顶，单行超长时不封顶 | 未修 |

**因此：** F3 影响的是授权门的严格度一致性——写门禁文件时请用字面 `true`，不要用
`yes` / `on`。F4 意味着某个失败检查如果吐出超长单行，输出仍可能很大。
这两条修好并通过新的独立复核之前，本工具集尚未获得独立验收。

## 边界

- 工具自身代码不写仓库内容，也不改 Git 状态。但 `quiet_verify --checks` 执行的是
  调用者声明的任意命令，**那些命令能写仓库**——"不写入"只对工具自身成立。
- `path_ledger` 不展开 submodule 内部的脏文件；子模块内的改动不在它的账本里。
- `preflight` 报告"门开着"只等于"那个文件此刻写着 true"，不等于动作被允许；
  权限仍然只来自当前 Human 指令与 canonical 协议。
- `quiet_verify` 通过只证明所列命令在本次会话的这棵工作树上通过，不证明更宽的命题。

## 测试

```bash
python -m pytest 08_os/06_execution/task_discipline -q
```

路径账本的 `worktree_paths` 有一个真 Git 临时仓测试：它故意把仓库配成
`core.quotepath=true` 且 `status.showUntrackedFiles=normal`，再断言未跟踪目录
被展开、中文路径没有被转义。纯函数部分（allowlist 匹配、门禁判定、硬失败分类）
由单元测试覆盖。
