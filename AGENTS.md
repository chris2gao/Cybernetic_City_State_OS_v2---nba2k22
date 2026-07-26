# Agent Collaboration Guide

This file is loaded by more than one vendor. Codex reads it as its repository
guidance file; Antigravity discovers it as a directory-scoped rule, walking up from
the file being edited to the repository root and loading every `GEMINI.md`,
`AGENTS.md` and `.agents/rules/*.md` it finds along the way. Write it so that it is
true for any backend executor, and put vendor-specific mechanics in a clearly named
subsection rather than in the general rules.

## Startup Rules

- The first repository read is `06_Silicon_Index/AI_Bootstrap_Sequence.md`.
- Read `AGENT_WORKING_DISCIPLINE.md` early. It is short, applies to every model in
  this project regardless of vendor, and is where the recurring failure modes are
  written down with the incident that produced each one.
- Before executing a task, read `.ai/TOKEN_USAGE_PROFILE.md` and follow its Layer 1 discipline.
- At a context boundary, select exactly one routing manifest under `.ai/load_profiles/`; profiles and their metadata never authorize actions.
- After Bootstrap, read the current Human task and only the constitutional, handoff, or domain files triggered by that task.
- `README.md`, `PROJECT_CONTEXT.md`, and `ARCHITECTURE.md` are routing/navigation snapshots. Load them when they help locate scope or architecture; do not load them unconditionally and do not treat branch/task claims in them as current without Git or active-mailbox verification.
- For AI handoff or model-to-model coordination tasks, read `.ai/PROTOCOL.md` and `.ai/STATE.yml` before acting when these files exist.
- For Human-authorized long-run AI handoff programs, also read `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` and preserve the task as one coherent objective unless a protected Human gate is reached.
- For Math Mentor generation or validation tasks, read `08_Domain_Applications/Math_Mentor/Universal_Layer_Execution_Protocol.md`.
- If a referenced bootstrap or protocol file is missing, report that fact instead of fabricating its content.

## Backend Executor Working Rules

These apply to every backend executor in this repository — Codex, Antigravity, or
any other — because every one of them loads this file.

- Use the existing repository structure and naming conventions.
- Prefer narrow, factual edits over broad rewrites.
- Use PowerShell commands in this Windows workspace.
- Use `rg` or `rg --files` for search when it is actually on `PATH`. Check with
  `Get-Command rg` rather than assuming; availability differs per execution
  environment on the same machine — Codex ships its own `rg` inside its package
  and sees it, while a plain PowerShell session on the same workstation does not.
  Report which environment you measured. Fall back to `Select-String` with an
  explicit path filter and a match limit.
- Do not overwrite or revert user changes unless explicitly requested.

Vendor-specific mechanics, and nothing else, belong here:

- Codex: use `apply_patch` for manual file edits.

## Safety Rules

- Do not read `数学知识路线图_全部.yaml` for routine layer work. Use the split level roadmap files unless full-graph analysis is required.
- Do not run destructive git commands such as `git reset --hard` or `git checkout --` without explicit approval.
- When generated files fail validation after repeated repair attempts, record them in `08_Domain_Applications/Math_Mentor/三次修复仍失败_待后续处理.md`.
- Avoid adding unverified implementation claims to documentation.

## Git Workflow

- Active work branch is task-specific. The legacy Math Mentor branch has been integrated into `master`; do not assume `legacy-mode-a-outsourcing` unless a current task explicitly names it.
- Remotes differ per repository in the core/domain fork family. Read them with
  `git remote -v` instead of trusting a name written here; a hardcoded remote in a
  core-owned file is wrong in every domain that merges it.
- Before committing, run `git status -sb`.
- Commit related changes together with a concise message.
- Push the current branch after successful commit when the user asks for publication.
- Keep `master` and feature/work branches distinct unless the user asks to merge.

## Test And Review Expectations

- For Python or YAML validation changes, run the relevant evaluator when practical.
- For Math Mentor generated nodes, use `bulk_evaluator.py` or `sandbox_evaluator.py` according to the protocol.
- For teaching-flow changes, check consistency with:
  - intuition before formal definition,
  - guided explanation before questioning,
  - full `sub_topics` coverage,
  - Exam Agent trap handoff,
  - spaced-review handoff after classroom pass.
- Reviews should lead with concrete risks and file references.
