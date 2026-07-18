# Agent Collaboration Guide

## Startup Rules

- The first repository read is `06_Silicon_Index/AI_Bootstrap_Sequence.md`.
- Before executing a task, read `.ai/TOKEN_USAGE_PROFILE.md` and follow its Layer 1 discipline.
- At a context boundary, select exactly one routing manifest under `.ai/load_profiles/`; profiles and their metadata never authorize actions.
- After Bootstrap, read the current Human task and only the constitutional, handoff, or domain files triggered by that task.
- `README.md`, `PROJECT_CONTEXT.md`, and `ARCHITECTURE.md` are routing/navigation snapshots. Load them when they help locate scope or architecture; do not load them unconditionally and do not treat branch/task claims in them as current without Git or active-mailbox verification.
- For AI handoff or model-to-model coordination tasks, read `.ai/PROTOCOL.md` and `.ai/STATE.yml` before acting when these files exist.
- For Human-authorized long-run AI handoff programs, also read `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` and preserve the task as one coherent objective unless a protected Human gate is reached.
- For Math Mentor generation or validation tasks, read `08_Domain_Applications/Math_Mentor/Universal_Layer_Execution_Protocol.md`.
- If a referenced bootstrap or protocol file is missing, report that fact instead of fabricating its content.

## Codex Working Rules

- Use the existing repository structure and naming conventions.
- Prefer narrow, factual edits over broad rewrites.
- Use PowerShell commands in this Windows workspace.
- Use `rg` or `rg --files` for search when available.
- Use `apply_patch` for manual file edits.
- Do not overwrite or revert user changes unless explicitly requested.

## Safety Rules

- Do not read `数学知识路线图_全部.yaml` for routine layer work. Use the split level roadmap files unless full-graph analysis is required.
- Do not run destructive git commands such as `git reset --hard` or `git checkout --` without explicit approval.
- When generated files fail validation after repeated repair attempts, record them in `08_Domain_Applications/Math_Mentor/三次修复仍失败_待后续处理.md`.
- Avoid adding unverified implementation claims to documentation.

## Git Workflow

- Active work branch is task-specific. The legacy Math Mentor branch has been integrated into `master`; do not assume `legacy-mode-a-outsourcing` unless a current task explicitly names it.
- Remote: `origin` at `git@github.com:chris2gao/Cybernetic_City_State_OS_v2---teacher.git`.
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
