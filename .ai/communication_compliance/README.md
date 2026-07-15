# Human–AI Communication Compliance Gate

This directory contains the repository-level, fail-closed compliance gate for
material Human–AI workflow communications. It makes the published C1/C2
protocol mechanically testable without turning ordinary C0 conversation into
a GitHub workflow.

The gate validates evidence and reports transition eligibility. It does **not**
intercept live model output, perform a state transition, grant Human authority,
push or merge code, activate a runtime, or prove that a model subjectively
understood what it read. A separately Human-authorized Communication Gateway
would be required for direct UI/runtime interception.

## One-command verification

From the repository root in PowerShell:

```powershell
python .ai/communication_compliance/validate_communication.py run-fixtures `
  --repo-root . `
  --suite .ai/communication_compliance/fixtures/fixture_suite.json `
  --output .ai/communication_compliance/fixtures/latest_fixture_result.json
```

The command succeeds only when every positive and negative fixture has the
exact expected result, exit code, and violation-code set. Regenerate the suite
after intentionally changing its source:

```powershell
python .ai/communication_compliance/fixtures/build_fixture_suite.py
```

Run focused unit and CLI tests with:

```powershell
python -m unittest discover -s .ai/communication_compliance/tests -v
```

The implementation uses Python plus the repository environment's existing
`PyYAML` and `jsonschema` packages. No network installation is required.

## Event classes

- `C0`: ordinary discussion, teaching, brainstorming, and other
  non-state-changing chat. No durable receipt or GitHub artifact is required.
- `C1`: material dispatch, review, completion/correction handoff, risk or
  conflict report, significant acceptance, and Human-gate reporting. The
  durable artifact, exact immutable references, role receipt, and Human-facing
  content must validate before the corresponding transition is eligible.
- `C2`: publication, merge, runtime/Coordinator activation, destructive or
  secrets-sensitive actions, objective changes, and routing changes. These
  need all C1 evidence plus a separate `AuthorizationContext` injected by a
  trusted external host.

Unknown event types fail closed. A payload's claimed class and descriptive
`human_gate` text never lower the class and never confer authority.

## Commands and exit codes

The CLI emits deterministic, sorted JSON to stdout. `--output` writes the same
bytes to a file.

| Command | Purpose |
| --- | --- |
| `classify --event-type TYPE` | Classify a named event; unknown types fail closed. |
| `validate-bootstrap --input FILE` | Validate a provider/role onboarding receipt against immutable protocol blobs. |
| `validate --input FILE` | Validate a C0/C1/C2 communication event. |
| `transition --input REQUEST --validation-result RESULT` | Revalidate a proposed transition and its evidence binding. |
| `validate-drift --input FILE` | Validate one privacy-safe drift record and recurrence obligation. |
| `run-fixtures --suite FILE` | Execute the deterministic regression suite. |

| Exit | Meaning |
| ---: | --- |
| `0` | Compliance pass. |
| `1` | Well-formed input failed a compliance rule. |
| `2` | CLI invocation error. |
| `3` | Input document, path, strict-parser, or output error. |
| `4` | Policy/schema/dependency configuration error. |
| `5` | Unexpected internal error; no traceback or host path is emitted. |

JSON rejects duplicate keys. YAML additionally rejects duplicate keys,
multi-document input, tags, anchors, aliases, and merge keys. Inputs are size
bounded. Production references must be exact `git_blob` references containing
a full commit SHA, safe repository path, and expected content digest. Mutable
branch names, trees, submodules, symlinks, suffix-only IDs, and basename/fuzzy
resolution are rejected. `test_fixture_blob` exists only under explicit test
mode and cannot be used as production evidence.

## Bootstrap receipts

`bootstrap_receipt.schema.json` binds:

- exact protocol commit and provider-neutral occupied role;
- the role's frozen wire schema;
- every required file as an immutable Git blob with content digest;
- the Human-only authority boundary and provider onboarding answers.

A receipt demonstrates a deterministic evidence claim: the required bytes
resolved at the stated commit and the answers matched the contract. It cannot
prove cognition, sincerity, or hidden mental state. ChatGPT and Claude occupy
the foreground review/dispatch role; Codex and Claude Code occupy the backend
execution/handoff role; only the Human occupies the Human Speaker role.

## Pointer and Human-content rules

The canonical pointers keep their frozen seven-key names and order.
`detail_ref` is the only optional tail key for the backend-to-foreground
pointer. Validation-result references stay outside the pointer core. Extra
prose or authorization fields inside a pointer fail validation.

A mixed-recipient response must either keep the complete Human-operational
content in a separable Human section or point to a resolvable durable Brief
containing that complete section. Pointer-only waiver never erases Human
content. Material Human content validates the eight preflight booleans,
independent-expression separation and bounded sentence count, dispatch-only
execution recommendation, and deterministic prohibitions against false
authorization or requests for hidden chain-of-thought. Generic expression is
a warning for foreground semantic review, not machine proof of quality.

## Transition eligibility and authority

`communication_validation.schema.json` binds the event digest, policy digest,
bootstrap receipt digest, exact resolved references, protocol head, and
proposed transition. The transition command revalidates those bindings and
fails closed for missing, stale, malformed, failing, or digest-mismatched
evidence.

The defined eligibility checks cover dispatch to `awaiting_codex`, backend
completion to `awaiting_chatgpt_review`, foreground acceptance, publication
candidate, and protected-publication entry. Accepted/publication-candidate are
transition identifiers here, not additions to the canonical repository state
enum.

For C2, `authorization_context.schema.json` is deliberately separate from the
model-generated event. A production host injects a context through the library
interface together with its own `trusted_authority_verifier`, bound to the
task, event, transition, action, target, protocol head, revocation state, and a
single-use context ID. The validator always emits
`authorization_granted_by_validator: false`; it only checks evidence. The
deterministic fixture authority mode is test-only and is rejected if presented
as trusted production authority. The standalone CLI deliberately has no
trusted-host verifier, so merely supplying `--authority-mode trusted-host` and
a trusted-looking JSON payload fails closed. The external host also owns
durable replay-state persistence. No secret or signing key belongs in these
repository artifacts.

## Drift ledger

`.ai/COMMUNICATION_DRIFT_LEDGER.yml` is append-only evidence. A record contains
the violation class, detection, correction state, repository-work preservation,
root cause, and preventive action, but no private reasoning or secret content.
At occurrence two and later, it must point to a matching negative fixture. If
deterministic coverage is genuinely impossible, the record must instead state
why and carry an immutable foreground semantic-review reference.

## File map

- `material_event_policy.yml`: versioned classes, roles, frozen wire keys,
  transitions, reference rules, and drift threshold.
- `*.schema.json`: strict contracts for receipts, events, results, transition
  requests, external authority, drift records, and the ledger.
- `validate_communication.py`: deterministic CLI and reusable validator.
- `fixtures/build_fixture_suite.py`: deterministic fixture generator.
- `fixtures/fixture_suite.json`: positive/negative contract suite.
- `fixtures/latest_fixture_result.json`: auditable latest fixture outcome.
- `tests/test_validate_communication.py`: focused schema, boundary,
  determinism, mailbox-neutrality, and regression tests.
