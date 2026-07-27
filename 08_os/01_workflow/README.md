# 01_workflow

The main area. Everything else exists to serve automated collaborative work, and this
is where that work is defined.

## Holds

One subdirectory per workflow, and within it the execution information for each stage:
what the stage consumes, what it produces, who performs it, what makes it complete, and
what it hands to the next stage.

## Does not hold

- general mechanisms — those live in `03_mechanisms/` and are referenced from here
- loaders — `06_execution/` initialises a workflow; this area only defines it
- content produced by running a workflow — that belongs in `07_content/`

## Not yet decided

The stage schema itself. The first-generation system has task packets, definition of
done, allowed scope, and stop rules already working under
`.ai/CODEX_TASK_INPUT_CONTRACT.md`; whether the workflow stage adopts that shape or a
different one is the next design conversation, not a settled matter.

Empty until that is decided. It is not a placeholder for a plan that exists elsewhere —
the plan does not exist yet.
