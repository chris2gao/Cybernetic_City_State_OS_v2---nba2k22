# task_discipline — 任务纪律工具

任务事实读取、前台验证执行和候选证据门。它们**不扩大 task scope，也不产生 Human confirmation**。
验证日志写入仓库外部；全权限调用者可以绕过工具，因此不能把工具可用称为全局强制执行。

| 工具 | 入口 | 一句话 |
|---|---|---|
| 预检 | `preflight/preflight_task_context.py` | 开工前一次性给出真实 HEAD、门禁、allowlist、禁止项、工作区状态 |
| 安静验证 | `quiet_verify/quiet_verify.py` | 跑一组检查，通过只留一行，失败才展开尾部输出 |
| 路径账本 | `path_ledger/changed_path_ledger.py` | 从 Git 生成规范化 UTF-8 变更路径集合，并与任务包 allowlist 求子集 |
| 受控验证 | `managed_verification/managed_verify.py` | 从候选内任务包和计划运行全部必需检查，完整留证，再由 inspect 重算结果 |

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
| quiet_verify | 全部诊断检查符合预期退出码 | 有检查不符 | 输入、启动或超时错误 |
| path_ledger | 账本生成；给了 allowlist 则全部在内 | 有路径越出 allowlist | git 或输入错误 |
| managed_verify | 必需检查实际完成且符合预期、源未变 | 检查退出码不符 | 输入/源/执行/证据不完整或损坏 |

## 用法

```bash
# 开工前
python 01_os/06_execution/task_discipline/preflight/preflight_task_context.py \
    --packet 01_os/_runs/<run-id>/01_任务输入/任务包_v1.yml

# 只有任务显式声明了 legacy/readiness boolean gate 时才核；新普通任务默认不传 --gate
    --gate 01_os/_runs/<run-id>/06_执行/<declared-gate>.yml \
    --gate-key <declared.boolean.path>

# 验证
python 01_os/06_execution/task_discipline/quiet_verify/quiet_verify.py

# 收尾路径账本
python 01_os/06_execution/task_discipline/path_ledger/changed_path_ledger.py \
    --base <exact_base_sha> --packet 01_os/_runs/<run-id>/01_任务输入/任务包_v1.yml
```

## 复核状态

本轮 OS execution foundation 改造的任务包、共享读取器、完整日志和受控验证路线仍待
新的独立验收。下面是旧工具的历史复核状态，不代表新候选已通过。

第一次独立复核结论是 **REJECT_CORRECTION_REQUIRED**，四条行为缺陷经执行者独立复现后
成立，**现已全部修复**。完整记录见
`01_os/_runs/run-20260809-任务纪律工具-001/08_独立复核/独立复核结论摘要与Human裁决_v1.yml`。

| 编号 | 工具 | 缺陷 | 修法 |
|---|---|---|---|
| F1 | path_ledger | 跨提交 rename 只报新路径（假阴性） | `--no-renames`，改名呈现为 delete + add |
| F2 | preflight | `--no-remote` 未核验 master 仍打印 `ok` | 核验四态化；未核验即阻塞，除非显式 `--accept-unverified-master`，且摘要如实标注 |
| F3 | preflight | 授权门接受 YAML 1.1 裸 `yes` / `on` | 同时要求解析值为 `True` 且字面量为小写 `true`，并记录 `raw` 与 `reason` |
| F4 | quiet_verify | 失败输出只按行封顶 | 行截断后再加 `--max-chars`（默认 4000）字符硬上限 |

测试 33 → 51。修复后重跑原始探针：F1 旧路径已出现，F3 `yes`/`on` 均 `open=False`，
F4 单行 30 万字符降到 4,034。**尚未经过第二轮独立复核。**

## 边界

- 工具自身代码不写仓库内容，也不改 Git 状态。但 `quiet_verify --checks` 执行的是
  调用者声明的任意命令，**那些命令能写仓库**——"不写入"只对工具自身成立。
- `path_ledger` 不展开 submodule 内部的脏文件；子模块内的改动不在它的账本里。
- `preflight` 报告"门开着"只等于"那个文件此刻写着 true"，不等于动作被允许；
  权限仍然只来自当前 Human 指令与 canonical 协议。
- `quiet_verify` 通过只证明所列命令在本次会话的这棵工作树上通过，不证明更宽的命题。
- `quiet_verify` 为每个检查创建独立的外部诊断目录，保留完整 stdout/stderr 与进程记录；
  展示时仍只取有界尾部。这些 unbound_diagnostic 记录不替代候选门。
- 任务包读取共享 `packet_input/`：规范包装优先，旧平铺格式显式报告；混用不回退。
  预检的 `publisher.expected_remote_master_head` 只指 master 基线，不能从发布目标
  `expected_remote_head` 猜测。缺必填字段、非法类型、显式重复键、循环或坏 UTF-8 为输入错误。
- 受控候选验证用法、检查计划和保证边界见 [managed_verification](managed_verification/README.md)。

## 测试

```bash
python -m pytest 01_os/06_execution/task_discipline -q
```

路径账本的 `worktree_paths` 有一个真 Git 临时仓测试：它故意把仓库配成
`core.quotepath=true` 且 `status.showUntrackedFiles=normal`，再断言未跟踪目录
被展开、中文路径没有被转义。纯函数部分（allowlist 匹配、门禁判定、硬失败分类）
由单元测试覆盖。
