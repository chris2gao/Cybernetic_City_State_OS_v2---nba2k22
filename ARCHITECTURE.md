# Architecture

Status: structural routing snapshot. This file describes core ownership and layout; it is not authoritative current branch, worktree, task, or mailbox state. Start from `06_Silicon_Index/AI_Bootstrap_Sequence.md`, the active task, and `CORE_MANIFEST.yml`.

## Core Structure

- `.ai/`: execution protocols, task packets, communication validation, cooperative lanes, role memory, run tooling, and load profiles.
- `01_Research_Reports/`: Human-retained research reports and source material. Its ownership declaration in `CORE_MANIFEST.yml` remains a known manifest correction for a later ownership task.
- `04_Parliament/`: issues, proposals, verdicts, debates, and resolved governance records.
- `05_Carbon_Index/`: Human-facing navigation.
- `06_Silicon_Index/`: AI bootstrap, constitutional routing, capability declarations, plans, scripts, and tests.
- `07_Compiler/`: compiler and schema support.
- `07_Execution_Plans/`: core execution plans and closed-loop records.
- `07_Silicon_Private_Zones/`: protected private-zone routing surfaces; ordinary tasks do not inspect private bodies.
- `campaigns/`: campaign schemas and state definitions.
- `short_term_tasks/`: generic short-term task contracts and templates.
- `system_backbone/`: shared backbone schemas and registry prototypes.

## Mechanism Responsibilities

- Bootstrap and load profiles select the minimum context required for an executor role.
- Constitutional documents establish authority and stop conditions.
- Communication compliance validates material events without granting identity or authority.
- Cooperative lanes provide descriptive write ownership and deterministic reduction.
- Role memory routes agents to durable evidence without becoming task state.
- Large-task protocols preserve one coherent Human-authorized objective across execution and review.
- The index generator produces navigational `index.md` files and `repository_index_manifest.json`; generated indexes are not authority.

## Ownership Boundary

Core contains reusable mechanism, governance, schemas, and routing. Domain repositories contain their own teaching, business, or other domain material. Domain repositories receive core updates through the merge procedure in `CORE_MANIFEST.yml`; core does not embed or actively bind one specific domain.

## Verification Boundary

Git and the active task establish live branch and execution state. `README.md`, `PROJECT_CONTEXT.md`, this file, generated indexes, and historical records are navigation or evidence only. Release-bound protocol changes require the repository release-binding checks before they may be treated as active.
