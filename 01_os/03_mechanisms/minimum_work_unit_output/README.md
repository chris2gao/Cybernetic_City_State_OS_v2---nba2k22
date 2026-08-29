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

## What the machine checks, and what they do not prove

The validator enforces a deterministic **structural anti-vacuity floor**, nothing
wider. It checks that all four core narrative fields are non-empty text rather than
a boolean, number, list or mapping; that a rationale is not one of a closed,
enumerated set of generic-only forms; that a rationale carries a minimum count of
content tokens; that an independent review's `verdict` is inside a closed enum; and
that every `primary_evidence_refs` entry in a review's assessment is drawn from the
`primary_evidence_examined` set that same review declares.

The two floors are deliberately different in strength. `work_performed_or_requested`
and `implementation_or_review_method` state what was done and how, so they carry the
type-and-emptiness floor only. `supportability_rationale` and
`feasibility_rationale` are justifications, so they additionally carry the
generic-only set and the content-token count.

Text handling is **Unicode-aware and language-neutral**. Normalization keeps the
letters and digits of every script instead of ASCII `a-z0-9`, and a script written
without a word separator contributes one content unit per character, because a
whitespace token count cannot measure content in such a script. Membership of that
class is decided only by the codepoint ranges declared in
`最小工作单元输出契约_v1.yml`; no text is ever classified by language. A Chinese
rationale that clears the floor passes, and `tests passed` still does not.

A passing validation therefore proves those structural properties and **only**
those. It does not prove that a rationale is true, sufficient, or appropriate to
the task, and set containment does not prove that the reviewer actually attacked
the executor rationale or reasoned correctly about it. No heuristic natural-language
judgement is attempted, by design. Semantic sufficiency stays where the contract
puts it: with independent review. The exact constants are in
`最小工作单元输出契约_v1.yml` under `machine_enforcement_boundary`,
`core_narrative_text_floor`, `rationale_machine_floor` and
`independent_review_machine_floor`, and the static
validator binds those declarations to the implementation constants so that either
side drifting is a validation failure rather than a silent divergence.

Formal MWU artifacts are parsed with a unique-key loader: a duplicate mapping key
at any level is rejected instead of resolved by last-key-wins.

## Load and validation

- Boot: `01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml`
- Registry: `01_os/05_registry/minimum_work_unit_output_v1.yml`
- Validator: `01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py`

Legacy artifacts that do not declare `minimum_work_unit_output` remain readable.
New formal outputs claiming MWU compliance are validated against the role-specific
requirements in the canonical contract.
