# Human completion brief v3 — Human authority provenance

Successor to briefs v1 and v2, both retained unmodified. Covers only the post-merge
fix-forward for `HUMAN_CONFIRMATION_PROVENANCE_BYPASS`.

## Intended result

Stop a repository object from granting itself Human authority, and tie key decisions to a
one-time code the Human generates independently — without building an external identity
system and without reopening F1, F2, CR-005, RR2-001 or the seven stage profiles.

## Actual implementation

The old check accepted `actor_class: current_Human` plus `explicit: true` written into the
object itself. Any model that could write the object could write those two lines. The
seven-stage child overlay also compared two absent references, and `None == None` passed.

Authority now runs the full chain: interaction → explicit Human disposition → a code the
Human generated → durable disposition record → exact task/stage/decision/model binding →
nonce commitment → validator resolves and validates → progression. The validator opens the
referenced file, recomputes its blob sha, and checks task, stage, decision id and type,
exact model version, authorized scope, affirmative disposition, provenance, staleness,
invalidation and prior consumption.

**Two codes, never interchangeable.** A *Human Authorization Code* is produced after you
confirm the exact Current Model and permits only starting substantive execution — it cannot
show you accepted the result. A *Human Completion Code* is produced after you read the
completion brief and accepts the result. Each is single-use and exactly bound, so no code
carries to another task, stage, decision, model version or output candidate. There is no
task-wide code.

**Nothing secret is stored.** Only the commitment — SHA-256 over canonical JSON, sorted
keys, fixed separators — goes into Git. The plaintext never enters a run artifact, a
communication document, a fixture, a log or a command line.

**Challenge verification.** A later model that doubts the provenance runs
`human_challenge_verify.py`, which reads the record, asks you for that decision's code, and
recomputes the commitment. The code is read from stdin only and never echoed or stored. A
code taken from executor output, the repository or another model's report is explicitly not
proof — any of those could have produced the record being challenged.

**What needs a code:** task and stage execution authorization, material architecture or
scope choices, risk acceptance, protected actions, completion acceptance, master publication
when the gate requires it. **What does not:** helper naming, fixture layout, ordinary
reversible implementation choices, retries inside confirmed scope. It is not a
micro-approval system.

## Honest limit

The foreground that first receives your code necessarily knows it. This mechanism gives
anti-self-assertion control, exact binding, replay control, cross-model challenge and
auditability. It is **not** proof of natural-person identity, not proof that you understood
what you approved, and not protection against a model that has already seen the plaintext.
Safety rests on you generating a fresh code per decision, exact binding, no plaintext
persistence, and independent challenge when provenance is doubted.

## Deviations

Two older test harnesses swapped the stage profile without moving the disposition with it,
so the authority gate fired before the assertion under test. The implementation was right;
the probes were stale and were corrected. Two composition negatives now legitimately fail at
the authority layer instead of the composition layer; their expectations were corrected with
a note, and composition itself stays covered by the per-stage cases.

## Tests and evidence

| gate | result |
|:--|:--|
| provenance adversarial gates | 25 of 25, control exit 0 |
| F2/F1 causal gates | 14 of 14 |
| earlier causal gates | 29 of 29 |
| fixture suites (6) | 86 cases, 86 passed |
| preserved regressions | 15 of 15 |
| challenge verifier, correct code | exit 0, verified |
| challenge verifier, wrong code | exit 1, mismatch |
| plaintext nonce anywhere in repo | none found |
| static repo / snapshot / live-state | exit 0 / 0 / 0 |
| material_event / review_execution | exit 0 / exit 0 |
| `git diff --check` | exit 0 |
| master modified | false |

## Remaining risks

- Foreground executor evidence only; the repository still has no CI.
- Nonce strength is a Human-side property. The validator checks the commitment's structure
  and binding; it cannot check how much entropy you actually used.
- `consumed_by` marks a spent nonce, but nothing forces a record to be marked consumed —
  invalidation depends on the disposition record being maintained.

## Exact versions

- base: `8d953a823275b3b98b8530ceef6682eeb84f0020`
- semantic candidate: `64434d2b369d6e668dd03722c283cb5d86ce026a`
- pointer: `08_结论/completion_pointer_v3.yml`, supersedes `completion_pointer_00002`
