# Managed verification

这是 foreground verification runner，不是通用业务执行器、最终独立验收或抗篡改服务。
它把当前手工验证链中容易漏掉的“候选、范围、必需检查、实际退出码、完整日志、消费者复算”
连成一次有界调用；不启动后台任务、不发布分支、不修改 master。

任务包使用规范的 `task_packet` 包装，并声明 `verification_plan: <repo-relative-plan.json>`。
`required_tests` 必须逐项等于计划中 checks 的有序 ID，不能是未执行的自然语言测试承诺。
计划是候选中受 Git 跟踪的普通 UTF-8 JSON 文件：

```json
{
  "schema_version": "citystate.verification_plan.v1",
  "task_packet": "01_os/_runs/<run-id>/01_任务/task_packet.yml",
  "checks": [
    {"id": "unit", "argv": ["@python", "-B", "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"], "timeout_seconds": 300, "expected_exit_code": 0}
  ]
}
```

全部检查必需，没有 skip/optional/条件、重试、缓存或恢复。argv 不经过 shell 展开；
`@python` 仅在第一个位置指当前入口解释器。拒绝未知键、重复键、坏 UTF-8、空集合、
布尔充整数和非有限数字。YAML 任务包另由共享 reader 读取，合法 merge override 仍合法。

在干净候选工作树中运行（外部 evidence-parent 必须已存在，attempt 名必须未使用）：

```text
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py run --repo-root . --candidate <40-character-SHA> --plan <plan.json> --attempt <external-evidence-parent/new-attempt>
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py inspect --repo-root . --candidate <same-SHA> --plan <same-plan.json> --attempt <same-attempt>
```

入口固定 candidate、base、task packet、plan、runner、changed paths 和有限 runtime 信息。
检查链开始前、每个已执行检查之后及结束时检查源状态；隐藏 index 标志和 submodule
当前明确拒绝。每一步留下 started/finished/source 记录及分离的二进制 stdout/stderr，
保留真实退出码。源变化或首个失败停止后续
执行，余项为 not_run；完成摘要最后原子落盘。中断/落盘失败没有成功结果，保留现场。
inspect 从固定输入和实际记录重算结论，不信任 hand-written `status: success`。

`0` 只表示这些固定的必需检查均完成且结果符合期望；`1` 是真实退出码不符；`3` 是
输入、源、执行、超时或证据错误。非零预期码用于明确负例，不是把任意失败当成功。
旧 attempt 永不覆盖，重跑必须新目录，失败记录仍保留。

日志可能含检查本身输出的私有数据：只允许运行当前任务授权且已知不会读取/输出秘密的
命令，发布前检查日志。运行时解释器路径留在本地原始 input，不直接当公共交付文件。

## 能力边界

- 不保证测试语义充分，不证明审核者独立；这需要后续独立验收。
- 同一 full-access 身份可篡改代码与记录或绕过入口；哈希不是历史真实性签名。
- 不隔离任意命令的副作用。命令只能是前台检查，不得启动脱离进程树的工作。
  超时只作尽力终止并无条件失败，不能据此认定没有副作用或自动重试。
- Git clean 不覆盖 ignored 输入、外部服务、瞬时改后还原的文件或完整依赖环境。
- 某些旧静态 validator 按原始工作区字节核 blob；必须用无换行转换的精确 checkout
  复验，不能把 CRLF/LF 的物化差异解释成候选语义回归。
- 当前是显式调用路线，不是已部署的远端必经门。部署独立控制的 CI/publisher 或其他
  runtime 需要 Human 明确决定；不能以本地 PASS 宣布整个 OS 已 operational。
