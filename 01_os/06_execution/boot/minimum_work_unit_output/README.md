# Minimum Work Unit Output validator

`validate_minimum_work_unit_output.py` has three explicit modes:

- `static --root <repo>` validates the canonical contract/boot/registry/navigation bundle and runs built-in regressions.
- `artifact <path>` validates a declared `minimum_work_unit_output`; add `--require-mwu` when the artifact is a new formal output that must declare one.
- `selftest` runs positive/negative contract regressions without repository state.

Legacy artifacts remain readable when they do not declare MWU. The validator never
grants authority and never asks for private chain-of-thought.
