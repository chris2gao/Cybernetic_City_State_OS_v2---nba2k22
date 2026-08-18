# Human completion brief — stage alignment enforcement

## Intended result

Make mandatory Human alignment real in `stage_collaborative_deliberation`: every task and
every workflow stage must show the current Human what will be done, how, why it is feasible,
the expected result, the verification method and the load-bearing risks, and get an explicit
confirmation bound to the exact current model version before substantive execution. Remove
the fixed round-count gate. Close CR-005 and RR2-001.

## Actual implementation

One Current Model, built by foreground and Human together; inquiry, discussion and brief are
methods for maintaining it, not separate mechanisms.

- Readiness is five conditions required together: model complete, proposed method,
  feasibility support, verification method, and explicit current-Human confirmation bound to
  the exact model version. Silence, inferred consent, a previous stage's confirmation, an
  older model version's confirmation, and executor or reviewer confirmation each fail.
- `full=5 / incremental=2` minimum substantive rounds deleted. `mechanism_version` stays 1.
- `dormant` now means "model adequate, no new load-bearing gap, so no *additional* inquiry".
  It never waives projection or confirmation.
- `effective_current_stage_model` = common model + the exact profile's `required_model_fields`,
  resolved at validation time from the receipt's `profile_id_and_version`. Common fields are
  not copied into the seven profiles.
- CR-005: a seven-stage child calls the real base stage-receipt validation, takes its actual
  exit code, and only on 0 overlays alignment and stage/profile binding. The self-reported
  `base_receipt_validation` flag is no longer read.
- RR2-001: completion pointers are append-only, bind the exact final semantic candidate, and
  must reference the retained prior record when superseding one.
- Ordinary local reversible choices stay model-owned; no micro-approval. Resolved Human input
  is not re-asked within the same model version.

## Deviations from the plan

- One naming set was chosen and applied everywhere (`proposed_method_or_solution`,
  `verification_or_acceptance_method`, `open_load_bearing_items`); no alias kept.
- An intermediate commit `772ab167` was published with the static repo gate failing at exit
  13 because a blob binding was left at an intermediate value. It was corrected in
  `d429962e` by a follow-up commit rather than an amend. Both are retained.
- A first blob-rebinding pass was too broad and rewrote provenance hashes in historical run
  records. It was reverted in full; rebinding is now scoped to the boot manifest and the
  seven workflow profile references only.

## Tests and evidence

| gate | result |
|:--|:--|
| validator static repo | exit 0 |
| validator static snapshot | exit 0 |
| no canonical live state | exit 0 |
| fixture suites (6) | 72 cases, 72 passed |
| preserved regressions | 15 of 15 |
| single-mutation causality gates | 29 of 29, control exit 0 |
| `git diff --check` | exit 0 |
| master modified | false |

The mutation gates matter more than the totals: each starts from one control that exits 0,
changes exactly one field, and asserts the resulting code, so the code is caused by that
change rather than by ambient breakage.

## Remaining risks

- All evidence is foreground executor evidence measured on one workstation. The repository
  has no CI, so nothing here is independent CI evidence.
- The seven profiles' own `required_model_fields` were not individually re-reviewed for
  whether they are the right obligations for each stage; only that composition enforces them.
- The mechanism remains `staged_inert` / `active_dormant`. Nothing here activates it.

## Exact versions

- final semantic candidate: `d429962efc0ed46679d2dfac7ef73af80c21e24b`
- base: `31296e1c1dd573310e26327b50ec2f70e176bc2a`
- model/output version of record: completion_pointer_00001
- pointer: `01_os/_runs/run-20260817-stage-human-alignment-enforcement-root-cause-001/08_结论/completion_pointer_v1.yml`
