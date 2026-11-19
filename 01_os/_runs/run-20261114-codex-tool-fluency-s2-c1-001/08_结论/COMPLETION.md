# C1 Chinese diagnostic path repair candidate

Task `OS-CORE-CODEX-TOOL-FLUENCY-S2-C1-20261114-001`, contract [Issue #28](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/issues/28).
Base `3f645d3048b32835dd5430da2780bd99939b3f8e` was read fresh and matched the Human baseline.
Branch `codex/tool-fluency-s2-c1-unicode`.

## Result and boundary

The existing Python CLI encoded redirected diagnostic output as CP936 on this
Windows host. Captured native bytes decoded correctly as CP936 but failed strict
UTF-8 decoding. A PowerShell `-File` wrapper returned the same CP936 bytes. The
Codex return displayed replacement characters. With only the child's
`PYTHONIOENCODING=utf-8` changed, both CLI and wrapper emitted strict UTF-8 with
the exact Chinese path and the same exit 1. The boundary is controllable in Core;
there is no claim that an external RDC defect was repaired.

The canonical wrapper now sets this process-local variable during invocation and
restores its original state in `finally`. An originally absent item is explicitly
removed; empty and nonempty original values are retained. No installed package,
system code page, PATH or global environment changes are involved. Closure,
version checks, parameters, output channels and exit handling retain their paths.
Production diff is 15 added lines and 5 documentation lines.

## Actual verification

`../07_测试执行/verify_unicode.py` calls the actual installed tool and the canonical
wrapper. It checks Chinese-and-space invalid YAML, valid YAML, ASCII-path invalid
YAML, valid JSON, a real invalid Schema definition with nonempty CLI stderr,
blocked external Schema reference (65), version mismatch (78),
missing executable (69) and missing file (66). Five real CLI reference calls must
match the wrapper's exit and both output byte channels. Six in-session cases prove
environment restoration for absent, empty and CP936 values on success and early
failure. Initial regression caught absent-to-empty restoration; the corrected
suite passed all cases. No mocked validation outcome is used.

Managed verification runs the same targeted script against the exact clean task
candidate and records full stdout/stderr outside the repository. The delivery PR
supplies the final candidate SHA, attempt path, inspect result and remote readback.
`completion_pointer`: task branch plus this record, verification plan and exact
candidate SHA in the delivery PR. Independent final review remains pending.

## Timing and tool use

Observed start `2026-11-15T08:01:01.936Z`; actual reproduction returned at
`08:01:55.873Z` (53.937 seconds); first corrected caller-visible diagnostic returned
at `08:05:19.411Z` (257.475 seconds). These are measured from the first instrumented
tool boundary, not an attestation of the exact request-receipt time. Commands,
exits, output and byte-boundary evidence are in `../07_测试执行/results.json`.
One run-specific four-case raw-byte probe was necessary to localize the fault;
the regression uses one temporary parameterized caller per suite to test
in-session state restoration. Existing fixtures remain read-only. No generic
tool runner, Registry or per-operation OS tasks were created.

Three repair events are explicit: the packet initially omitted the preflight's
expected-master field, and the first implementation restored an absent value as
empty, and the first managed plan named an absent test file instead of the actual
Run-scoped regression. Each was repaired from the actual failure and rechecked. Bounded tool
discovery was reused; no identical search was repeated.

The runtime retained earlier conversation context. Human explicitly confirmed in
this task that execution may continue here and window selection belongs to Human.
Timing describes this chosen window and does not establish an isolated
fresh-window cold-context performance trial.

## Independent review handoff

Review the exact candidate from primary evidence, reproduce the Unicode failure
with the base wrapper, then run the candidate plan and inspect its receipts.
Check UTF-8 path bytes, unchanged CLI channels/exits, closure and version gates,
and all three environment states across success and failure. Authoritative
adoption/master integration remains subject to independent review and Human
decision. Post-fix RDC rendering, other shells/code pages and a fresh Codex
window have not been independently verified.

## Minimum work unit rationale

Work performed: repaired the real diagnostic encoding boundary in the existing
canonical wrapper. Method: raw-byte differential probe, scoped environment
override, real CLI comparisons and exact-candidate managed verification.
Supportability: the same input now returns the exact Chinese path and the same
invalid-enum result; local tests compare both byte channels and preserve refusal
gates. Feasibility: existing PowerShell/Python/CLI suffice with no installation;
state restoration is directly exercised. These executor findings support the
bounded engineering candidate, not independent acceptance or general host claims.
