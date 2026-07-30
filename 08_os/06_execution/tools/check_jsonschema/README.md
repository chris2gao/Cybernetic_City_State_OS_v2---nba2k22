# check-jsonschema execution wrapper

`invoke.ps1` is the canonical on-demand entry point for a self-contained local JSON
Schema and a local JSON/YAML instance. Before validation it runs two fail-closed gates:

1. `inspect_schema_refs.py` strictly parses the local `.json` schema and permits only
   fragment-only `$ref`, `$dynamicRef` and `$recursiveRef`; HTTP(S) `$id`/legacy `id`
   and all external-file references are rejected.
2. The resolved CLI must report exactly `check-jsonschema, version 0.37.4`.

Only after both pass does it start validation, forward stdout/stderr and preserve the
CLI exit code. No loader or server remains resident.

## Usage

```powershell
& "08_os/06_execution/tools/check_jsonschema/invoke.ps1" `
  -SchemaPath "<local-schema-path>" `
  -InstancePath "<local-instance-path>"
```

Optional `-Executable` and `-PythonExecutable` values accept either a command
resolvable through `PATH` or an explicit caller-supplied path. `-ExpectedVersion`
defaults to `0.37.4`; changing it does not verify a new version and is intended only
for a separately authorized revalidation run. The wrapper contains no user-specific
path.

## Failure contract

| Exit | Meaning |
|---|---|
| underlying CLI code | validation completed; exact CLI result is preserved |
| 65 | schema is not strict self-contained JSON under the canonical reference policy |
| 66 | local schema or instance file does not exist |
| 69 | tool, Python or inspector dependency is unavailable |
| 70 | the native process returned no exit code |
| 78 | version probe failed, was unparseable, or did not match the expected version |

Parameter-binding errors remain PowerShell errors. The wrapper never asks a model to
replace a failed check and never installs, upgrades, starts MCP, changes `PATH`, or
writes global state.

The canonical v1 policy intentionally does not support modular schemas in sibling
files. A future recursive local closure design must separately define root
containment, symlink handling, cycle detection and file-count/byte limits. Directly
calling `check-jsonschema` bypasses this wrapper and can use remote schemas or refs;
the package itself must not be described as network-disabled.

## Load boundary

This file is discovered through the tools registry and invoked only when a task names
it. It is not referenced by boot. Its complete output should normally stay in a run
artifact; a model should receive only the minimum diagnostic needed for the next
decision.
