# Human–AI Communication Compliance Gate v2

This directory contains the repository-level, fail-closed evidence gate for
material Human–AI workflow communications. It makes C1/C2 protocol obligations
mechanically testable while leaving ordinary C0 conversation outside GitHub.

The gate validates provenance and reports eligibility. It does not intercept
live output, authenticate a live Human by itself, change STATE, consume an
authorization atomically, push or merge code, or activate runtime components.
A host that executes a transition must independently authenticate its contexts
and compare-and-swap the exact active review head used by the proof.

## Release binding

The policy separates two heads:

- `source_mailbox_base_head` is only the neutral baseline for
  `.ai/INBOX.md`, `.ai/OUTBOX.md`, `.ai/STATE.yml`, and `.ai/HUMAN_BRIEF.md`.
- `protocol_release_head` is the immutable semantics commit whose canonical
  protocol blobs are loaded by bootstrap receipts.

A protocol release uses two ordinary commits. The semantics commit finishes
code, schemas, tests, generator, canonical docs, and ledger semantics with the
release field explicitly unbound. Its immediate binding-only child writes the
semantics SHA to policy and regenerates only release-derived fixtures, results,
and reports. Canonical receipt files must be blob-identical in both commits.

## Verification

From the repository root:

```powershell
python .ai/communication_compliance/fixtures/build_fixture_suite.py
python .ai/communication_compliance/validate_communication.py run-fixtures `
  --repo-root . `
  --suite .ai/communication_compliance/fixtures/fixture_suite.json `
  --output .ai/communication_compliance/fixtures/latest_fixture_result.json
python -m unittest discover -s .ai/communication_compliance/tests -v
```

The suite asserts exact result, exit code, and violation-code sets. It binds
fresh receipts for all four model providers to the release head and retains a
complete, digest-correct stale receipt for the neutral base as a negative case.

## Event and pointer evidence

C0 is ordinary, non-state-changing discussion. C1 includes dispatch, review,
completion/correction handoff, material acceptance, risk/conflict reporting,
and Human-gate reporting. C2 includes publication, merge/rebase, activation,
destructive or secret-sensitive work, objective change, and routing change.
Unknown event types fail closed; payload class claims and `human_gate` text are
descriptive only.

The seven pointer fields and order remain frozen. `detail_ref` remains the only
optional backend-to-foreground tail field. A Human always occupies
`human_speaker`; a Human direct backend dispatch uses the communication
direction's frozen `chatgpt_to_codex_v1` wire without impersonating a model
role. The repository artifact cannot authenticate its own `provider: Human`
claim, so a state-changing Human event additionally needs an externally
injected `ActorOriginContext`.

Production references are immutable `git_blob` objects with a full commit SHA,
safe path, and exact SHA-256. Resolution verifies that the 40-hex object is a
commit and that the path is one ordinary blob. Mutable refs, tree objects,
missing paths, symlinks, submodules, digest mismatches, duplicate keys,
multi-document YAML, tags, anchors, aliases, and merge keys fail closed.
`test_fixture_blob` exists only in explicit test mode and is never cached.

## Non-self-authenticating transition proof

`transition_request.schema.json` contains physical `event_ref`, `state_ref`,
`pointer_ref`, and optional `validation_artifact_ref`. Transition validation:

1. verifies an external `ActiveStateContext` and binds STATE to its currently
   observed review head;
2. strictly resolves and parses the actual event, then reruns `validate_event`,
   including every receipt file and required ref;
3. resolves the physical pointer, checks its ordered canonical bytes and exact
   equality to the event pointer, and closes every non-null pointer `_ref`;
4. derives task, event class, actual raw state, normalized state, transition ID,
   target state, and release head from evidence and policy;
5. if a durable validation artifact exists, requires exact canonical bytes and
   semantic identity with the fresh result; and
6. only after the proof chain passes checks separately injected C2 authority.

No supplied `result: pass`, claimed digest, claimed resolved status, descriptive
gate, or request claim can authorize or replace fresh computation. The output
is a `transition_proof` and always says
`authorization_granted_by_validator: false`.

The explicit state graph supports closed/accepted completion to backend,
backend to foreground review, review correction back to backend, review
acceptance to closed, review to Human publication gate, and protected
publication entry. Raw repository statuses use an exact alias registry; fuzzy,
prefix, or prose-based normalization is forbidden.

The standalone CLI has no trusted-host callback, so a trusted-looking JSON
payload cannot certify itself. Test fixtures may use deterministic test-only
contexts. A production host supplies verifiers, persists replay protection,
atomically consumes C2 authority, and performs the final state-head CAS.

## Drift history

`.ai/COMMUNICATION_DRIFT_LEDGER.yml` v2 preserves the immutable v1 parent as a
one-time migration anchor. Each occurrence appends a new sequenced, hash-chained
record; old records are never edited to increment an occurrence. Validation
resolves the previous ledger blob, compares the exact prior-record prefix,
checks the trusted candidate-base ledger, and rejects deletion, mutation,
reorder, duplicate IDs, sequence rollback, broken hashes, and occurrence gaps.

At occurrence two and later, recurrence evidence is an immutable suite Git
blob plus suite digest, unique negative case ID, and case digest. Mutable
`path#case` strings are forbidden. A genuine deterministic-impossibility
exception still needs immutable foreground-review evidence.

## Commands and boundaries

| Command | Purpose |
| --- | --- |
| `classify` | Fail-closed material-event classification. |
| `validate-bootstrap` | Release-head receipt validation. |
| `validate` | Fresh event, pointer, Human-content, and ref validation. |
| `transition` | Physical proof-chain recomputation; no supplied result input. |
| `validate-drift` | One record and recurrence evidence. |
| `validate-ledger` | Immutable history/prefix/base-head validation. |
| `run-fixtures` | Deterministic positive and adversarial suite. |

Exit codes are `0` pass, `1` compliance failure, `2` bad invocation, `3` bad
input/path, `4` unavailable configuration, and `5` internal failure. Errors are
deterministic JSON without traceback or host-path disclosure.
