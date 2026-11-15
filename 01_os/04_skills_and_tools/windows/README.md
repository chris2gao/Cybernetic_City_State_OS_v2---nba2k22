# Windows tool calls from Codex

Measure the current command process before choosing an invocation. In this task,
Codex executed PowerShell Core 7.6.4 at
`C:\Program Files\PowerShell\7\pwsh.exe` on Windows 10 build 19045.
The WindowsApps `pwsh.exe` alias was absent. A second PowerShell executable
was discoverable in the Codex runtime. Interpreter selection belongs to each
host/session. The run's shell receipt records actual paths and versions.

## Shell and arguments

For `exec_command`, set `shell` to the measured PowerShell 7 executable,
`login: false` and `workdir` to the exact repository. For an explicit child
script use the measured executable with `-NoLogo -NoProfile -NonInteractive
-File <script.ps1>`. Keep multiline work in a script file. PowerShell
`$PSVersionTable.PSVersion`, `$PSVersionTable.PSEdition` and
`(Get-Process -Id $PID).Path` identify the process executing the script.
`Get-Command pwsh.exe -All` only inventories candidates. Windows PowerShell
`powershell.exe` 5.1 has different native argument behavior.

Use `& $executable @arguments`, with one array element per argument. Quoted
literal paths and `-LiteralPath` preserve spaces, Chinese characters and
wildcard characters. For ripgrep, pass a real directory and `-g '*.py'`;
PowerShell does not expand a quoted `directory/*.py` into native file arguments.
Use explicit UTF-8 for text and JSON files, and explicit bounds for output.
For Python Unicode stdout captured by PowerShell, use `python -B -X utf8`.
This host's default Python pipe encoding corrupted Chinese stdout even while
native argv preserved the original string. The replay exercises the UTF-8 path.

PowerShell 7's Windows native argument mode handles executable arguments, while
`.cmd` and `.bat` follow legacy Windows command-line parsing. Check
`$PSNativeCommandArgumentPassing` when arguments fail. Prefer an existing CLI's
JSON file argument for nested JSON. The REA adapter already resolves its npm
shim to `node.exe` plus `rea.mjs`. Call that existing adapter. Simple
`.cmd --version` calls can be used directly. The replay checks both paths.

Inside a task script set `$ErrorActionPreference = 'Stop'`. For native programs,
capture `$LASTEXITCODE` immediately and preserve it. With
`$PSNativeCommandUseErrorActionPreference = $false` a nonzero native result
does not become a PowerShell exception, so test the captured code explicitly.
Set that preference only in the script scope when it is needed. An empty stderr
does not establish success, and nonempty stderr with exit zero can be a warning.
Capture stdout and stderr separately. Use the existing foreground runner for
deadlines and logs. On timeout, retain the execution stage and uncertainty about
external effects before deciding whether another call is permissible.

The calling conventions follow Microsoft's PowerShell 7.6 parsing and error
preferences. [Argument parsing](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parsing?view=powershell-7.6),
[preference variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables?view=powershell-7.6).

## Find and reuse

Read a task's exact source references, the relevant Registry and tool entry
first. Use a bounded filename or text search only when the pointer is missing.
Reuse these existing entries, with `python -B` and task-scoped output paths.

| Need | Existing entry from repository root |
|---|---|
| Git HEAD, branch, dirty paths, ancestry, hooks and master | `01_os/06_execution/task_discipline/preflight/preflight_task_context.py --packet <packet.yml> --repo-root <repo> --json` |
| Changed-path ledger with NUL-safe paths | `01_os/06_execution/task_discipline/path_ledger/` |
| Pinned required verification with full logs and timeouts | `01_os/06_execution/task_discipline/managed_verification/managed_verify.py run`, then `inspect` against the same candidate and attempt |
| Development diagnostics | `01_os/06_execution/task_discipline/quiet_verify/quiet_verify.py --checks <checks.yml>` |
| Exact historical source and blob/hash checks | `GitSource` in `01_os/06_execution/boot/context_management/prms/source.py` |
| REA schema, version and bounded static calls | `01_os/06_execution/tools/rea/adapter.py` |
| Existing project index and affected module discovery | `01_os/06_execution/task_discipline/project_context/project_context.py` |

For one exact historical file, `git show <40-char-sha>:<path>` is sufficient.
When saving source for Python processing, capture Git's binary stdout directly
with Python `subprocess.run([...], check=True, stdout=destination)`. Avoid text
pipelines that can change encoding or newlines. Use the existing `GitSource.read`
when the task already consumes its verified source and proof.

Batch independent read calls in one outer tool call, preserving each result and
exit code. Construct a Git snapshot from HEAD, branch, status and the necessary
diff summary in the same batch. Run dependent operations in sequence. A receipt
from a long-running tool supplies the handle for the next bounded wait. Poll only
that handle, at a useful interval and with a small output cap.

Record only reusable paths, observed versions, limitations and exact source
references in the existing task evidence/index. Recheck after a host, executable,
source or schema change. PRMS save/resume requires its existing authorized state
store and explicit operation. Successful source lookup alone is no PRMS save.

## Read the actual result

| Observation | What to report and retain |
|---|---|
| Argument or schema rejection | Parameter name, received value when known, allowed range, raw error and tool exit. REA `INVALID_REQUEST` preserves bounded `field_errors` and `tool_message`. |
| Executable or backend absent | `NOT_INSTALLED` / `BACKEND_UNAVAILABLE`, selected launcher and the missing capability. |
| Host permission or environment failure | `PERMISSION_DENIED`, native exit or PowerShell error identifier and the failing stage. |
| Business precondition fails | Expected/observed fixture values, object identity, comparison field and whether dispatch was reached. |
| External effect uncertain | Original unknown receipt, last established stage and evidence gaps. Reconcile through the existing owner before any replay. |
| Business operation succeeded | Actual output, input identity, exit code and the operation's required readback. A static REA `VERIFIED_TOOL_CALL` proves the selected static call. |

REA's `automatic_replay: false` remains part of every adapter receipt. Local
option checks run before launcher discovery. Entropy `block-size` accepts
powers of two from 256 through 65536. The adapter additionally caps byte options
at 512 MiB. Its camel-case schema key is `blockSize`.

GE-01's original `durationMs` error stated a maximum of 60000. Its later
`Schedule fixture differs` observation established a pre-dispatch failure but
contained no observed GameID/day/home/away values. Preserve that historical gap.
With an offline fixture containing expected and observed rows, report the
specific differing field. A live Calendar caller needs those values from its own
domain precheck to produce the same detail.

## Evidence and limits

Task `OS-CORE-CODEX-WINDOWS-TOOL-FLUENCY-20261114-001` owns the replay in
`01_os/_runs/run-20261114-codex-windows-tool-fluency-001/07_测试执行/`.
Read its `results.json` and completion record for measured call counts, timing,
temporary scripts, output equality and diagnostic coverage. The comparison
concerns the recorded offline workload. It provides no live Calendar, game
effect, save persistence or independent acceptance result.
