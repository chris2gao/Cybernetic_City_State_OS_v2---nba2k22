# Minimum Work Unit Output validator

`validate_minimum_work_unit_output.py` has four explicit modes:

- `static --root <repo>` validates the canonical contract/boot/registry/navigation bundle,
  binds the declared contract structures to the implementation constants, and runs the
  built-in regressions.
- `artifact <path>` validates a declared `minimum_work_unit_output`; add `--require-mwu`
  when the artifact is a new formal output that must declare one.
- `selftest` runs the positive, negative and adversarial contract regressions without
  repository state.
- `drift --root <repo>` copies only the paths `static` consumes into an isolated temporary
  root, applies one shadow mutation at a time, and requires the matching static error.
  It proves the static bindings actually fire; it never writes to the repository.

Every mode returns a non-zero exit code and a single JSON line on failure. Parse
failures — including a duplicate mapping key at any level of a formal artifact —
surface as ordinary validation failures, never as a Python traceback.

## Enforcement boundary

The checks are a deterministic structural anti-vacuity floor: value type, non-emptiness,
a closed generic-only form set, a minimum content-token count, a closed independent-review
verdict enum, and containment of assessment evidence refs within the declared examined
evidence. Passing proves those structural properties and nothing wider — not that a
rationale is true, sufficient or task-appropriate, and not that a reviewer genuinely
attacked the executor rationale. Semantic sufficiency remains independent-review judgement.

Legacy artifacts remain readable when they do not declare MWU. The validator never
grants authority and never asks for private chain-of-thought.
