# mutmut fail-closed WSL loader

`invoke.sh` 是 mutmut 的唯一 canonical repository wrapper。它只在任务显式
请求 mutation testing 时调用，不进入 boot，也不常驻。

## 基本调用

```bash
bash 08_os/06_execution/tools/mutmut/invoke.sh \
  --repo-root "$PWD" \
  --venv /absolute/path/to/dedicated-mutmut-venv \
  --project-dir 08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/real_target_tests \
  --target 08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py \
  --allow-target 08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py \
  --test-path tests/inspector_cases.py \
  --max-children 2
```

wrapper 在任何 mutation 执行前检查 Linux 文件系统、worktree root、clean
status、project/target/test 的 repository containment、单文件 allowlist、
virtualenv、可执行文件和精确版本 `3.6.0`。baseline pytest 失败时不进入 mutation。

## 退出码

- `0`：baseline 与 mutation 过程完成；survivor 仍须人工分类。
- `64`：参数或必填 allowlist 缺失。
- `65`：工作区、路径、目标类型或 allowlist 边界不成立。
- `66`：repository、project、target 或 test 不存在。
- `67`：baseline pytest 失败。
- `69`：virtualenv、Python 或 mutmut 不可用。
- `73`：worktree 在开始前不干净，或 mutation 后 repository 状态改变。
- `78`：版本探测失败或不是 `3.6.0`。
- 其他：保留 mutmut 自身退出码。

临时目录采用 `/tmp/citystate-mutmut.XXXXXX`，只由当前调用创建并由 `EXIT` trap
精确清理。不要把 wrapper 扩展为多目标、全仓库扫描或 `mutmut apply` 入口。
