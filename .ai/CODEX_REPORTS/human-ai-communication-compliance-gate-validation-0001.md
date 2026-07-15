# Human–AI Communication Compliance Gate — Validation Evidence

```yaml
task_id: human-ai-communication-compliance-gate-0001
base: d235e602c14250d16b91f2897cb8308e031cc13c
validator_version: 1.0.0
fixture_result: pass
unit_test_result: pass
deterministic_repeatability: pass
```

## Environment

```text
Python 3.14.6
PyYAML 6.0.3
jsonschema 4.26.0
referencing 0.37.0
```

No package was installed for this task.

## Consolidated fixture run

Command:

```powershell
python .ai/communication_compliance/fixtures/build_fixture_suite.py
python .ai/communication_compliance/validate_communication.py run-fixtures `
  --repo-root . `
  --suite .ai/communication_compliance/fixtures/fixture_suite.json `
  --output .ai/communication_compliance/fixtures/latest_fixture_result.json
```

Result:

```yaml
total_cases: 79
matched_cases: 79
mismatch_count: 0
expected_pass: 25
expected_fail: 51
expected_error: 3
operations:
  classify: 2
  parse_document: 3
  transition: 21
  validate_bootstrap: 8
  validate_drift: 5
  validate_event: 40
result_sha256: f7deba7f9104b0e565ed2110121b8a4e4fba40809aca6bba6014f118c84b2737
```

The expected-error cases are strict-parser rejections and return documented
input exit code 3. Compliance-negative cases return exit code 1. All expected
passes return 0.

## Focused tests

Command:

```powershell
python -m unittest discover -s .ai/communication_compliance/tests -v
```

Result: 13 tests passed. The tests cover:

- all seven JSON Schemas;
- disjoint event classification and unknown fail closure;
- both frozen pointer cores and provider-neutral roles;
- English and Chinese visible sentence boundaries;
- strict duplicate-key/anchor/alias/tag/multi-document parsing;
- all 79 fixture outcomes;
- required boundary-case inventory;
- malformed field-type fail closure without invalid result output;
- timezone/hash-seed independent CLI JSON;
- JSON invocation errors without traceback or absolute host path;
- canonical document bindings and separate routing envelope;
- drift-ledger schema/privacy invariants;
- source mailbox candidate blob identity against the exact base.

Python byte compilation also passed for validator, fixture generator, and test
module.

## Deterministic repeatability

The complete fixture suite ran in two fresh validator processes with:

```yaml
run_1: {TZ: UTC, PYTHONHASHSEED: "1", exit: 0}
run_2: {TZ: Pacific/Kiritimati, PYTHONHASHSEED: "98765", exit: 0}
byte_identical: true
sha256: f7deba7f9104b0e565ed2110121b8a4e4fba40809aca6bba6014f118c84b2737
```

No timestamp, random identifier, branch name, absolute path, traceback, or
environment-dependent mapping order is emitted.

## Authorization-forgery coverage

The suite proves all of the following fail closed:

- descriptive payload `human_gate` without external authority;
- nested authorization data inside the canonical pointer;
- structured authorization inside Human content or independent expression;
- authorization prose inside independent expression;
- deterministic test authority presented as trusted-host authority;
- a production-shaped `trusted_external_host` context with no separately
  injected verifier;
- a context bound to another task/action;
- replay of an already consumed context ID.

Positive C2 cases are limited to explicit deterministic test-fixture mode and a
test-harness-injected verifier callback. The standalone CLI owns no production
trust root and cannot turn a trusted-looking JSON file into authority.

## Staging, mutable-ref, and path exclusion coverage

This task has no domain staging corpus. The equivalent source-integrity checks
reject mutable branch/review-head references, unsafe or fuzzy paths, symlinks,
trees, submodules, non-blob Git objects, unresolved `self` during transitions,
and test fixture refs outside explicit test mode. Source mailbox files and all
forbidden domain/runtime paths remain outside the candidate diff.

## Final structural checks

The consolidated final pass includes:

- JSON parse and Draft 2020-12 schema checks;
- strict YAML parse for policy and ledger;
- Markdown fence-balance check for every changed/added Markdown file;
- `git diff --check`;
- exact allowlist check over tracked modifications and untracked additions;
- source mailbox clean-filter blob identity against the base;
- scoped added-secret signature scan that reports counts/paths only;
- exact generated-suite reproducibility;
- development-branch remote exact-head readback after publication;
- `master` and source mailbox neutrality recheck after publication.

## Known boundary

This evidence establishes repository validator behavior. It does not establish
live UI interception, production host authentication, transition persistence,
or action execution. Those capabilities remain absent and separately gated.
