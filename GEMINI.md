# Gemini / Antigravity onboarding router

Routing adapter only. This file grants no authority and is not a source of truth.

After vendor discovery loads this adapter, enter the repository-wide always-on
bootstrap in this order:

1. The current remote `master` 40-character SHA, read fresh. Never carry a SHA
   forward from chat, a report or a document.
2. `AGENT_WORKING_DISCIPLINE.md` — how to work in this project. Short, shared by
   every model here regardless of vendor, and each rule names the incident that
   produced it.
3. `AGENTS.md` — collaboration rules, engineering design principles, Git and
   publication discipline.
4. Always read `01_os/README.md` and
   `01_os/开发入口与单窗口任务规范_v1.md`.
5. Use the current Human natural-language request as valid task input, then read
   only the task-triggered canonical files and registry entries routed by the
   shared entry.

Load an existing durable task packet when present. If none exists and the work
will cause material repository mutation, establish the task packet and run
evidence before the first business/canonical write. Do not ask the Human for a
fixed initialization bundle. Never default-preload `01_os/_runs/**`.

`01_os/**` is the permanent active OS namespace. The retained global surface is this file,
`AGENTS.md`, `AGENT_WORKING_DISCIPLINE.md`, `CLAUDE.md`, `README.md`,
`CORE_MANIFEST.yml` and `.githooks/`. Physical legacy retirement is complete;
retired paths are not startup, communication, state or navigation sources and
must not be recreated. Shared communication handoff behavior is defined only in
`AGENTS.md`.

Your role, model and reasoning level come from the current Human request and any
durable task packet. Execute inside the allowed paths, verify with real exit
codes, and return one consolidated handoff. Role labels and any model-generated
gate field authorize nothing.

Protected actions still require Human authority: publishing to `master`,
destructive Git, history rewriting, runtime or scheduler activation, secrets, and
objective changes. `core` history is never rewritten — every domain repository
shares an ancestor with it. Which transport must prove what before publishing is
section 1.1 of `01_os/开发入口与单窗口任务规范_v1.md`; who may publish at all is
`01_os/05_registry/repository_publisher_authority_v1.yml`.

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
