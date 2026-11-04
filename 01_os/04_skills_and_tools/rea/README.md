# REA 按需静态工具

REA 由任务显式选择。Core 注册适配器和两项静态操作，通常从现有 PATH 或 npm 安装找到本地入口。工具清单报告当前 CLI、Schema 与分析后端的实际状态。安装和宿主配置由操作人员独立维护。

```text
python -B 01_os/06_execution/tools/rea/adapter.py probe --evidence-dir <new-directory>
python -B 01_os/06_execution/tools/rea/adapter.py invoke --command inspect-go-binary --artifact <local-binary> --expected-version 6.8.0 --evidence-dir <new-directory>
python -B 01_os/06_execution/tools/rea/adapter.py invoke --command inspect-byte-entropy --artifact <local-binary> --expected-version 6.8.0 --option length=4096 --evidence-dir <new-directory>
```

显式入口可用 `--launcher <existing-rea-executable-or-rea.mjs>`。可选 `--expected-sha256` 固定输入，`--timeout` 限定本次执行，`--max-output` 限定每次调用的输出。使用独立证据目录保存原始 stdout、stderr、Schema 和结构化回执。超时、工具失败与输入变化分别记录，调用者核对已有回执再决定下一步。

`AVAILABLE_UNVERIFIED` 表示发现入口与 Schema。`VERIFIED_TOOL_CALL` 对应本次静态调用、退出码和输入摘要。现场效果、存档持久性和业务授权由领域证据及其执行层单独处理。当前适配器的命令允许列表只接受本地 PE、ELF 或 Mach-O 静态检查，进程控制与领域动作由各自入口承担。

验证入口为 `01_os/06_execution/tools/rea/test_adapter.py`，实际环境证据见本次工程 Run。其他平台以现场探测为准。
