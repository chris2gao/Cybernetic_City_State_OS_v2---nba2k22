# Human completion brief v4 — synthetic authority escape

Successor to briefs v1–v3, all retained unmodified. Covers one blocking defect found before
independent review.

## Intended result

Stop the test fixtures from being usable as real Human authority.

## Actual implementation

The synthetic disposition records under `fixtures/human_dispositions` were marked
`synthetic_test_record: true`, but the production authority path never looked at that field.
A real instance could point `durable_disposition_ref` at one of them and let a test record
grant Human progression authority.

The production path now rejects any record carrying that marker, and the check runs **first**
— before task, stage, decision, model version, blob or commitment. So a synthetic record that
is correct in every other respect still fails, and fails for the right reason rather than
tripping over some later mismatch. Path naming and comments are not the control; the marker
in the record is.

The only way past it is a keyword-only `synthetic_authority_context` that defaults to false
and is passed by the test harness that built the fixture. It is never read out of the
instance being validated, so writing `test_mode: true` or `allow_synthetic: true` into the
instance changes nothing. The CLI does not expose it, so no command line can enable it.
Both properties are asserted by gates against the source, not just claimed here.

A non-synthetic control record was added so the path is shown to accept a genuine durable
Human disposition, rather than simply rejecting everything.

`consumed_by` was left alone as instructed: no consumption state machine was added, and
exact decision binding plus cross-event replay rejection are unchanged.

## Deviations

Regenerating the records changed their blob shas, which briefly made the fixtures fail on a
stale blob (exit 13) instead of the synthetic rejection (15). The fixture refresh was keyed
on a text pattern that only matched its own first output, so it was not idempotent. It is now
keyed on the record path, and the exit codes report the intended semantics.

## Tests and evidence

| gate | result |
|:--|:--|
| synthetic escape gates | 8 of 8 |
| production instance → synthetic record | exit 15 |
| synthetic yet correct in every other field | exit 15 |
| instance self-declares test_mode / allow_synthetic | exit 15 |
| genuine non-synthetic disposition | exit 0 |
| production CLI run against a synthetic fixture | exit 15, refused |
| authority adversarial gates | 25 of 25 |
| F2/F1 causal gates | 14 of 14 |
| earlier causal gates | 29 of 29 |
| fixture suites (6) | 86 cases, 86 passed |
| preserved regressions | 15 of 15 |
| static repo / snapshot / live-state | exit 0 / 0 / 0 |
| material_event / review_execution | exit 0 / exit 0 |
| `git diff --check` | exit 0 |
| master modified | false |

## Remaining risks

- The marker only protects records that carry it. A test record written without
  `synthetic_test_record: true` would not be caught by this control; the non-synthetic
  control record in the fixtures is itself an example of that shape.
- Nonce entropy remains a Human-side property the validator cannot measure.
- `consumed_by` marks a spent nonce but nothing forces a record to be marked consumed.
- Foreground executor evidence only; the repository still has no CI.

## Exact versions

- base: `8d953a823275b3b98b8530ceef6682eeb84f0020`
- semantic candidate: `7d666bfa26c6bb9d9b3de357250fd4c463c183c6`
- superseded: `64434d2b369d6e668dd03722c283cb5d86ce026a` (pointer v3 retained)
- pointer: `08_结论/completion_pointer_v4.yml`
