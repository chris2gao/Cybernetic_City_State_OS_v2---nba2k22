# check-jsonschema execution wrapper

`invoke.ps1` is the canonical on-demand entry point for local JSON/YAML instance
validation. It starts one CLI process, forwards stdout/stderr, returns the CLI exit
code, and leaves no loader or server resident.

## Usage

```powershell
& "08_os/06_execution/tools/check_jsonschema/invoke.ps1" `
  -SchemaPath "<local-schema-path>" `
  -InstancePath "<local-instance-path>"
```

An optional `-Executable` accepts either a command resolvable through `PATH` or an
explicit executable path supplied by the caller. The wrapper itself contains no
user-specific path.

## Failure contract

| Exit | Meaning |
|---|---|
| underlying CLI code | validation completed; exact CLI result is preserved |
| 66 | local schema or instance file does not exist |
| 69 | executable is absent from `PATH` or the explicit path is invalid |
| 70 | the native process returned no exit code |

Parameter-binding errors remain PowerShell errors. The wrapper never asks a model to
replace a failed check, never treats a URL as a local schema, and never installs,
upgrades, starts MCP, changes `PATH`, or writes global state.

## Load boundary

This file is discovered through the tools registry and invoked only when a task names
it. It is not referenced by boot. Its complete output should normally stay in a run
artifact; a model should receive only the minimum diagnostic needed for the next
decision.
