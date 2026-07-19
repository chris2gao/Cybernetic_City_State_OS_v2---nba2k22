# KCP PROP_LOGIC Batch 1 Validation

## Outcome

The exact five-node batch passed local deterministic, sandbox, bulk, YAML,
prerequisite-graph, path-scope, and repeatability checks. These are local
`teaching_ready` candidates pending exact-head semantic review, not consumer admissions.

## Executed evidence

- `PROP_LOGIC-001`: 4 binary and 2 unary assignments; all five connectives and
  `P→Q ≡ ¬P∨Q`; standalone commit `3cc415d`.
- `PROP_LOGIC-002`: 8 distinct three-variable rows and 48 assignment checks over
  six common equivalences.
- `PROP_LOGIC-003`: 18 Boolean-algebra identities over 8 assignments each,
  totaling 144 comparisons.
- `PROP_LOGIC-004`: complete 4-row examples for tautology, contradiction,
  satisfiable non-tautology, entailment, and a declared countermodel.
- `PROP_LOGIC-005`: PDNF and PCNF reconstruction for all 256 three-variable
  truth functions, totaling 4,096 normal-form evaluations.
- Individual sandbox evaluator: `5/5` passed, zero warnings.
- Isolated bulk evaluator: `5/5` passed, exit code `0`.
- Batch validator: passed; output and complete log include exit code `0`.
- Re-execution produced byte-identical per-node output SHA-256 values.

## Scope and safety

- Prerequisite graph has 8 resolved in-batch edges and no cycle.
- Exactly five business node files changed; all other durable files are under
  the named program-run evidence root.
- Four protected teaching-contract files, every bridge path, learner state,
  scheduler, runtime, and Coordinator remain untouched.
- Central P0 rows remain `unclaimed`, five alias conflicts remain open, and
  `consumer_allowed` remains zero.

## Limitation

Executable passes establish only their declared finite truth-functional claims.
All formal-definition, completeness, uniqueness, mapping, and pedagogy claims are
listed separately for semantic acceptance.
