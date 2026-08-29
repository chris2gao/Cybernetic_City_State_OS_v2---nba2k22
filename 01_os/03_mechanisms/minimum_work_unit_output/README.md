# Minimum Work Unit Output

This mechanism promotes the observed `T2-MWU-OUTPUT-TRIAL-001` pattern into one
global output contract for **material work units**.

It applies when a model produces a formal decision/architecture dispatch, an
execution completion/handoff, or an independent-review completion. It does **not**
apply to every tool call, micro-operation, scratch iteration, or private reasoning
step.

Canonical semantics live in `最小工作单元输出契约_v1.yml`. The stable core is:

- `work_performed_or_requested`
- `implementation_or_review_method`
- `supportability_rationale`
- `feasibility_rationale`

Role-specific additions keep decision dispatch, execution evidence, and independent
review explicit without creating a second workflow.

The load-bearing review rule is that executor rationale is a claim to attack:
independent review must test both supportability and feasibility rationales against
primary evidence and report unsupported or inferred claims.

This mechanism grants no authority, changes no task scope, and introduces no Human
authorization/delegation chain. It does not modify the communication envelope,
context selection, model routing, or workflow progression.

## Load and validation

- Boot: `01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml`
- Registry: `01_os/05_registry/minimum_work_unit_output_v1.yml`
- Validator: `01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py`

Legacy artifacts that do not declare `minimum_work_unit_output` remain readable.
New formal outputs claiming MWU compliance are validated against the role-specific
requirements in the canonical contract.
