# Cosmic Ray fail-closed WSL loader

`invoke.sh` 是 Cosmic Ray 的唯一 canonical repository wrapper。它只在任务显式需要
第二 mutation engine 时调用，不进入 boot、不常驻，也不暴露为 MCP。

## 基本调用

`--receipt-dir` 必须是尚不存在、位于 repository 外且不在 `/mnt/**` 下的 Linux
绝对路径。

```bash
bash 08_os/06_execution/tools/cosmic_ray/invoke.sh \
  --repo-root "$PWD" \
  --venv /home/user/.venvs/core-cosmic-ray-8.4.6 \
  --project-dir 08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/real_target_tests \
  --target 08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py \
  --allow-target 08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py \
  --test-path tests/inspector_cases.py \
  --receipt-dir /tmp/cosmic-ray-receipt-001 \
  --timeout-seconds 5 \
  --max-mutations 100
```

wrapper 先检查 Linux filesystem、worktree root/clean status、project/target/test
realpath containment、单一 `.py` allowlist、receipt 边界、virtualenv、
`include-system-site-packages = false`，以及 Python `3.14.4`、pytest `9.1.1`、
Cosmic Ray `8.4.6` 的精确版本。所有 Python 探测和执行前均清除 `PYTHONPATH`、
`PYTHONHOME`、`PYTHONUSERBASE`；失败诊断不回显 probe 输出、可执行路径或用户目录。
随后从 `HEAD` 归档 project 到
`/tmp/citystate-cosmic-ray.XXXXXX`，只在归档中生成 config、SQLite session、cache
和 mutated source；baseline 通过后才允许 init/exec。

receipt 只保留 raw dump、human report、stable JSON summary、各阶段 stdout/stderr 和
hash/配置回执，不复制 SQLite 或 mutated source。EXIT trap 只清理当前调用创建的精确
临时目录。

## 语义与退出码

`summarize.py` 删除随机 job id，以 module/operator/occurrence/source span/diff 形成稳定
对象摘要。它用 output=`timeout` 覆盖 Cosmic Ray 原生的错误 killed 标记，并把
pending、非 normal worker 和非 killed/survived test outcome 归入 unsafe outcomes。

- `0`：baseline、init、exec、dump/report 完成，且没有 unsafe outcome；survivor 仍须
  人工或可执行证明分类。
- `64`：参数、数值范围或“恰好一个 allowlist”契约失败。
- `65`：filesystem、路径 containment、目标类型、allowlist 或 receipt 边界失败。
- `66`：repository、project、target、test 或 receipt parent 不存在。
- `67`：baseline pytest 失败；init/exec 不会运行。
- `68`：session init 失败。
- `69`：virtualenv、Python、Cosmic Ray、cr-report 或 summary helper 可执行文件不可用。
- `70`：mutation exec 失败或 config 在 init/exec 间失效。
- `71`：dump、report、summary 或 archived source restore 校验失败。
- `72`：存在 timeout、incomplete、incompetent 或 worker error；结构化 receipt 已保留。
- `73`：worktree 开始前不干净，或执行后 repository 状态变化。
- `74`：init 产生的对象数超过显式 session 上限；exec 不会运行。
- `78`：virtualenv isolation 声明缺失/不可解析/非 false，或 Python、pytest、
  Cosmic Ray 版本探测失败及精确值不匹配。

不要扩展 wrapper 为多目标、HTTP distributor、远端 worker、并行写同一 source tree、
canonical mutation apply 或 repository 内 receipt 入口。
