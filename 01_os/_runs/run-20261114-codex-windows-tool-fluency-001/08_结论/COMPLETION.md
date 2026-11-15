# Windows tool fluency engineering candidate

Task `OS-CORE-CODEX-WINDOWS-TOOL-FLUENCY-20261114-001` implements the Core
engineering and offline comparison requested in the current Human instruction.
Base `953b3e34d5432b93f05cdff7215da49fe7f87833`.
Branch `codex/windows-tool-fluency-20261114`.
The exact verified candidate and managed-verification projection are recorded in
`verification.json` after execution. This record is an engineering handoff.

## Change and reason

Codex's AGENTS subsection now points to an on-demand Windows calling guide.
The guide reuses existing preflight, path ledger, managed verification, PRMS
source and REA entries. It fixes the documented invocation conventions for
PowerShell Core, native arrays, JSON files, cmd shims, NUL-safe Git paths,
UTF-8 Python output, errors, stderr and deadlines.

The existing static REA adapter validates local options before launching a tool.
Known validation errors retain the tool code, bounded message and field errors,
including the 60000 limit seen in GE-01. Local range errors identify the option,
received value and bounds. The existing entropy option `block-size` now checks
the actual schema key `blockSize`. Missing artifacts or launchers receive a
specific missing-source/tool status. Operation scope remains the two registered
static commands and every receipt retains `automatic_replay: false`.

The replay code belongs to this Run. No new reusable command runner or environment
probe was warranted. Windows measurement found the currently executing shell was
PowerShell Core 7.6.4 at the Program Files installation. The WindowsApps pwsh
alias was absent. Python's actual executable differs from its WindowsApps
launcher, so Unicode subprocess output is explicitly tested with `-X utf8`.

## Measured comparison

`07_测试执行/results.json` is recomputed by `summarize.py` from the raw local
measurement files and `tool_calls.json`. Each recorded outer call really invoked
one exec_command. Inputs are individually hashed. Both routes exercised the same
seven cases, including frozen historical Python processing and real REA entropy
inspection of the same Git executable.

| Recorded metric | Split baseline | Batched candidate |
|---|---:|---:|
| Outer calls | 7 | 2 |
| Tool wait total | 9.884 s | 8.178 s |
| Observed route including inter-call intervals | 55.881 s | 15.866 s |
| First business result available at a tool reply, discovery included | 34.117 s | 15.866 s |
| First reply for the known reuse portion | 2.608 s | 7.392 s |
| Repeated searches | 0 | 0 |
| Temporary source scripts created during replay | 0 | 0 |
| Unexpected execution errors during measured route | 0 | 0 |
| Known parameter diagnostic lost | 1 | 0 |

Outer calls decreased 71.4% and tool wait decreased 17.3%. Git snapshot,
historical source/hash, historical processor output and actual entropy output
matched. Grouping delays the first reply within the known reuse portion because
that reply also waits for the diagnostic and static analysis cases. The measured
route stays below both requested time targets. These are bounded replay results.
General unfamiliar-task performance and the historic 85-minute preparation
interval require separate observations.

Setup and implementation calls are outside the performance comparison. The
retained replay scripts are test infrastructure counted separately from
temporary source scripts. The paired route was run once, without randomized
task assignment or a new model window. Scheduling intervals are not an isolated
measurement of model inference.

## Diagnostic and evidence boundaries

`ge01_cases.json` keeps four exact source proofs and a minimal projection of the
stopped GE-01 archive at
`99938b46e47c7ded9a8ba317fef6a7849342a171`. It preserves the real parameter
error and the real pre-dispatch fixture error. The original fixture evidence
lacks observed GameID/day/home/away values. That gap remains explicit.

An intentionally synthetic offline row demonstrates reporting
`away expected=28 observed=27`. Domain Calendar instrumentation has not been
modified. It needs a separately scoped change to emit equivalent field detail
from a live precheck. Original UNKNOWN records and their reconciliation authority
continue to belong to the domain. This Core change grants no replay permission.

During construction, the original source extraction check needed a whitespace
correction for `invoke(17, payload)`; that extraction then passed. The shell test
exposed corrupted Chinese Python stdout and passed after selecting UTF-8. The
initial task packet used an unsupported lifecycle field name and was corrected
to the existing `terminal_lifecycle_state`. These development failures preceded
the measured comparison and are not hidden in its zero-error count.

Independent final review is pending. Before master integration or authoritative
adoption, a fresh reviewer should verify the fixed source, reproduce the
parameter and blockSize regressions, rerun the Windows comparison and examine
the measurement limitations. Human retains the existing integration decision.

## Minimum work unit output

- Work performed. Added the Codex Windows guide and repaired reproduced static
  REA diagnostics and schema handling within the existing entry.
- Method. Used fresh master, existing task/preflight/verification tools, frozen
  historical errors, actual PowerShell and REA calls, and a paired bounded replay.
- Supportability. The measured route preserves source and business results while
  reducing actual outer calls. Negative cases retain actionable field diagnostics
  and no automatic replay.
- Feasibility. The implementation uses the installed PowerShell, Python, Git,
  ripgrep and REA, with existing repository execution and Registry conventions.
  The domain fixture change and general cold-task timing remain outside this
  Core evidence.

The `completion_pointer` in `verification.json` binds the actual candidate,
verification and publication readbacks. The Run lifecycle denotes a candidate
awaiting independent review.
