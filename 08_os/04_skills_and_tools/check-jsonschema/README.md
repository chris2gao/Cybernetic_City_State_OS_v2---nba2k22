# check-jsonschema

## Verified status

- status: `verified_on_demand`
- verified version: `0.37.4`
- validation date: `2026-07-30`
- mount: `on_demand_cli`
- default loaded: `false`
- MCP exposed: `false`
- canonical wrapper:
  `08_os/06_execution/tools/check_jsonschema/invoke.ps1`
- version gate: exact runtime match to `0.37.4` before validation
- schema gate: strict self-contained local `.json`; references must be fragment-only
- evidence:
  `08_os/_runs/run-012-check-jsonschema安装接入验证/`

The current Windows installation was independently resolved through `PATH`, matched
the pipx-isolated package and Python runtime, and passed the run-012 positive,
negative, repetition and fail-closed wrapper matrix. The bare `pipx` command was not
visible in the executing shell; `py -m pipx` reproduced the pipx metadata without
changing the environment.

The correction matrix additionally proved that HTTP(S), relative-file and non-string
reference keywords, HTTP(S) identifiers, YAML schemas and damaged JSON are rejected
before validation. Fake 9.9.9, corrupt-version and failed-version probes all stopped
before their validation sentinel could be written.

## OS responsibility

Use this tool only for a real JSON Schema and a local YAML/JSON instance. It can
reliably reject encoded structural errors such as missing required fields, wrong
types, invalid enum values, unwanted properties and malformed nested objects.

It does not decide whether a claim is true, evidence is sufficient, a file reference
exists, two documents agree, or a business choice is reasonable. Those remain the
responsibility of repository validators, source/evidence review and Human/model
semantic review.

The existing workflow `*schema_v1.md` files are Markdown specifications, not machine
JSON Schemas. Run-012 validates only its calibration contract and does not silently
promote those Markdown files into checked contracts.

## Verify, upgrade, uninstall

Availability and version:

```powershell
check-jsonschema --version
& "08_os/06_execution/tools/check_jsonschema/invoke.ps1" `
  -SchemaPath "<local-schema-path>" `
  -InstancePath "<local-instance-path>"
```

Human-managed pipx lifecycle commands, to be executed only in a separately authorized
maintenance task:

```powershell
py -m pipx upgrade check-jsonschema
py -m pipx uninstall check-jsonschema
```

Every upgrade requires rerunning run-012's schema meta-check, positive YAML/JSON,
all core negative cases, reference-closure and version-drift cases, five-run
repetition, Unicode/space path and wrapper unavailable-path tests before the registry
version/status changes.

## Stop downstream

Stop the consuming task when the wrapper cannot find its executable or input files,
the wrapper cannot find Python/inspector, schema closure or metaschema validation
fails, the instance is malformed, the version probe differs from 0.37.4, or validation
returns nonzero. Do not fall back to “the model thinks it looks valid.”
