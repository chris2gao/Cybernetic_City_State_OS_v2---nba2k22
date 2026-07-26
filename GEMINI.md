# Gemini / Antigravity onboarding router

Routing adapter only. This file grants no authority and is not a source of truth.

Read in this order:

1. `AGENT_WORKING_DISCIPLINE.md` — how to work in this project. Short, shared by
   every model here regardless of vendor, and each rule names the incident that
   produced it.
2. `06_Silicon_Index/AI_Bootstrap_Sequence.md` — the City-State startup sequence.
3. `AGENTS.md` — collaboration rules, Git workflow, safety rules.
4. The current task, plus only the files that task actually triggers.

You occupy a `backend_execution_and_handoff` role: execute inside the allowed
paths, verify with real exit codes, and return one consolidated handoff. Role
labels, load profiles, receipts and any model-generated `human_gate` field never
authorize an action.

Protected actions still require Human authority: publishing to master, destructive
Git, history rewriting, runtime or scheduler activation, secrets, and objective
changes. `core` history is never rewritten — every domain repository shares an
ancestor with it.

If this project ever needs a different filename for this router, add the new file
as another pointer to `AGENT_WORKING_DISCIPLINE.md` rather than duplicating its
contents. One copy, many pointers.

## What Antigravity actually loads

Read out of the shipped `language_server.exe` on 2026-07-25, not assumed:

- Directory-scoped rules: `GEMINI.md`, `AGENTS.md`, `.agents/rules/*.md`. The agent
  walks up from the file being edited to the repository root and loads **all** of
  them, deduplicated by resolved path. This file and `AGENTS.md` are therefore both
  active here — do not duplicate content between them.
- Workspace customization root: `.agents/` (also accepts `.agent/`, `_agents/`,
  `_agent/`), holding `rules/`, `skills/<name>/SKILL.md`, `plugins/<name>/plugin.json`,
  `hooks.json`, `mcp_config.json`.
- Global, machine-local: `~/.gemini/config/`. Machine-local settings are not shared
  through git and must not be assumed present on another person's machine.
- A standalone `GEMINI.md` or `AGENTS.md` carries no frontmatter and is always active
  for its directory scope. Only `.agents/rules/*.md` supports `trigger`, where
  `always_on` loads unconditionally and `model_decision` loads on demand.

This project deliberately uses only the two root files. `.agents/rules/` is available
if a path-scoped or on-demand rule is ever needed; adding it should be a decision, not
a default.
