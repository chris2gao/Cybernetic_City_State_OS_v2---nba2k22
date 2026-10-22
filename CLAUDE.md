# Claude Code onboarding router

Routing adapter only. This file grants no authority and is not a source of truth.

After Claude Code loads this adapter, enter the repository-wide always-on
bootstrap in this order:

1. The current remote `master` 40-character SHA, read fresh. Never carry a SHA
   forward from chat, a report or a document.
2. `AGENT_WORKING_DISCIPLINE.md` — how to work here. Short, shared by every model
   in this project, and each rule names the incident that produced it.
3. `AGENTS.md` — backend working rules, engineering design principles, Git and
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

`01_os/**` is the permanent active OS namespace. Material elsewhere in this repository is
retained global infrastructure — this file, `AGENTS.md`,
`AGENT_WORKING_DISCIPLINE.md`, `GEMINI.md`, `README.md`, `CORE_MANIFEST.yml`,
`.githooks/` — and nothing else is a current startup surface. Physical legacy
retirement is complete.

Task-specific root-cause analyses, handovers and unverified hypotheses stay in
their existing `01_os/_runs/<run>/` records; they do not create another root-level
archive or startup surface. Read them only when the current task routes you there.
Do not recreate a retired path or restore a dependency on
one. Shared communication handoff behavior is defined only in `AGENTS.md`.

Your role, model and reasoning level come from the current Human request and any
durable task packet, not from this file. A role label authorizes nothing.

Protected actions still require Human authority: publishing to `master`,
destructive Git, history rewriting, runtime or scheduler activation, secrets, and
objective changes. `core` history is never rewritten. Which transport must prove
what before publishing is section 1.1 of
`01_os/开发入口与单窗口任务规范_v1.md`; who may publish at all is
`01_os/05_registry/repository_publisher_authority_v1.yml`. Never read or expose credentials or key
files.
