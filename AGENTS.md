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

## Engineering Design Principles

These are design defaults, not grants of deletion, modification, or publication
authority. Apply them only within the current task's authorized scope.

1. Do not preserve backward compatibility by default. When an artifact or behavior
   is obsolete, require an independent review of its removal; after that review
   passes, delete it instead of adding compatibility layers, migrations,
   deprecation paths, or fallbacks.
2. Choose the simplest implementation that fully satisfies the current
   requirements. Do not add speculative abstractions, extension points, or
   configuration layers.
3. In a layered system, establish the smallest working end-to-end path first, then
   add layers incrementally. Never dismantle a working slice merely to accommodate
   incomplete complexity.
4. Keep components modular, with clear boundaries and separation of concerns.
5. Prefer mature, actively maintained libraries. Do not reimplement an available
   capability without a concrete, task-relevant reason.
6. Before adding a dependency or writing a custom implementation, inspect the
   project's existing dependencies and the capabilities they already provide.
7. Make architecture decisions for the long-term target. Do not accept a knowingly
   temporary "use this now and replace it later" design; this does not justify
   speculative implementation beyond current requirements.
8. For material design problems, first study how mature products and established
   patterns solve the same problem. Adapt a proven pattern instead of inventing a
   new one from scratch.

## Safety Rules

- Do not run destructive git commands such as `git reset --hard` or `git checkout --` without explicit approval.
- Avoid adding unverified implementation claims to documentation.

## Git Workflow

- Active work branch is task-specific; do not infer it from historical documentation.
- Remotes differ per repository in the core/domain fork family. Read them with
  `git remote -v` instead of trusting a name written here; a hardcoded remote in a
  core-owned file is wrong in every domain that merges it.
- Before committing, run `git status -sb`.
- Commit related changes together with a concise message.
- Push the current branch after successful commit when the user asks for publication.
- Keep `master` and feature/work branches distinct unless the user asks to merge.
- A local clone with a shell is not a shared premise. Some executors that load
  this file reach the repository only through the GitHub API or a connector: they
  can create branches, write files and update refs, but cannot read or set
  `core.hooksPath` and cannot run a local hook. State which transport you are on
  before publishing, and run that transport's gate — the matrix is section 1.1 of
  `08_os/开发入口与单窗口任务规范_v1.md`. An unrecognized transport is blocked.
- Lacking a local hook is not lacking permission, and is not grounds for
  withholding a finished artifact. The API path substitutes a real gate for the
  hook: bind an expected 40-character head, write with a non-force
  compare-and-swap, keep the diff inside the allowed paths, and read the
  resulting remote head back rather than assuming it. Report the value you read.
- Publication authority itself, and which acts remain action-bound even under the
  widest Human grant, are in `.ai/REPOSITORY_PUBLISHER_AUTHORITY.yml`. A provider
  name authorizes nothing there — it is text the caller writes about itself.

## Test And Review Expectations

- For Python or YAML validation changes, run the relevant evaluator when practical.
- Reviews should lead with concrete risks and file references.
