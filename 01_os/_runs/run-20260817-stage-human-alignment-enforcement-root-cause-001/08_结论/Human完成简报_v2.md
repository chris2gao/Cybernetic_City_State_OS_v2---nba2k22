# Human completion brief v2 — stage alignment enforcement, review corrections

Successor to `Human完成简报_v1.md`, which is retained unmodified. This brief covers only
what changed after the independent review returned CHANGES_REQUIRED on F2 and F1.

## Intended result

Close two review findings without reopening the architecture, without touching CR-005 or
RR2-001 semantics, and without redesigning the seven stage profiles.

## Actual implementation

**F2 — the common Current Model is now fully required.** All eleven keys must be present
before substantive execution, plus the explicit current-Human confirmation bound to the
exact model version. The previous check used one `if not model.get(field)` for everything,
which cannot distinguish a missing key from a legitimately empty answer. Fields are now in
three classes: eight need a substantive value; `constraints_and_dependencies` and
`assumptions_risks_alternatives_unknowns` accept `none_material`;
`open_load_bearing_items` accepts `[]`. "Checked and found empty" is a real answer; "never
considered" is not. A present-but-null value fails. The contract carries the same three
classes so it cannot drift from the validator.

**F1 — an unknown required stage field blocks by default.** The `UNKNOWN_DISPOSED`
capability is kept, but a model no longer certifies its own unknown as harmless.
Progression requires an explicit `deferred_nonblocking` deferral, `blocking: false`, a
reason and scope, a revisit trigger, and a downstream impact assessment that explicitly
clears all five dimensions — stage objective, decision, verification, authority, downstream
acceptance. If the unknown is load-bearing or sits on a Human decision boundary it also
needs a current Human basis that is not silence, inference or stale.

Resulting semantics: raw unknown fails, asserted or incomplete deferral fails, blocking
unknown fails, fully justified non-blocking deferral passes.

## Deviations

One of my own positive fixtures was exactly the pattern F1 targets: the stage 06
`package_completion_pointer_candidate` was deferred with only `blocking: false` and a
revisit trigger. F1 rejected it. It is now a genuinely justified deferral — the pointer
cannot be written before the final semantic candidate exists, and nothing downstream is
blocked by that ordering — which also demonstrates the capability still works.

## Tests and evidence

| gate | result |
|:--|:--|
| fixture suites (6) | 86 cases, 86 passed |
| preserved regressions | 15 of 15 |
| F2/F1 causal gates | 14 of 14, control exit 0 |
| F1 A–H matrix | 77 checks across 7 profiles, 0 failures |
| earlier causal gates | 29 of 29, unchanged |
| validator static repo / snapshot | exit 0 / exit 0 |
| no canonical live state | exit 0 |
| material_event / review_execution | exit 0 / exit 0 |
| `git diff --check` | exit 0 |
| master modified | false |

The F1 matrix uses each profile's own `required_model_fields`, not invented field names.

## Remaining risks

- Foreground executor evidence only. The repository has no CI.
- The seven profiles' `required_model_fields` were still not individually re-reviewed for
  whether they are the right obligations per stage; F1 only enforces how an unknown among
  them may be disposed.
- `downstream_impact_assessment` records the foreground's own judgement. The validator
  checks that all five dimensions are explicitly cleared, not that the judgement is correct.

## Exact versions

- new semantic candidate: `8a001f017daf7a0b8001a1de9fbcac160a6249e2`
- superseded semantic candidate: `d429962efc0ed46679d2dfac7ef73af80c21e24b` (pointer v1 retained)
- base: `31296e1c1dd573310e26327b50ec2f70e176bc2a`
- pointer: `08_结论/completion_pointer_v2.yml`, supersedes `completion_pointer_00001`
