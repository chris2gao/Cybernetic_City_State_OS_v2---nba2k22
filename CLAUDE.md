# Claude Code onboarding router

Routing adapter only. This file grants no authority and is not a source of truth.

Read in this order:

1. The current remote `master` 40-character SHA, read fresh. Never carry a SHA
   forward from chat, a report or a document.
2. `AGENT_WORKING_DISCIPLINE.md` — how to work here. Short, shared by every model
   in this project, and each rule names the incident that produced it.
3. `AGENTS.md` — backend working rules, engineering design principles, Git and
   publication discipline.
4. The current task packet: objective, exact base SHA, allowed paths,
   prohibitions, tests, completion pointer.
5. `01_os/README.md` and `01_os/开发入口与单窗口任务规范_v1.md` — when the task
   touches the OS. That entry defines the single-window rules, file placement,
   registry, run evidence, publication transport gates and the Human gate.
6. Only the canonical files the task actually names.

`01_os/**` is the active OS. Material elsewhere in this repository is either
retained global infrastructure — this file, `AGENTS.md`,
`AGENT_WORKING_DISCIPLINE.md`, `GEMINI.md`, `README.md`, `CORE_MANIFEST.yml`,
`.githooks/` — or legacy awaiting Human retirement. Legacy paths are not a
startup, communication, state, task or navigation source of truth; do not load
them to "get context" and do not restore a dependency on them.

Your role, model and reasoning level come from the current task packet, not from
this file. A role label authorizes nothing.

Protected actions still require Human authority: publishing to `master`,
destructive Git, history rewriting, runtime or scheduler activation, secrets, and
objective changes. `core` history is never rewritten. Which transport must prove
what before publishing is section 1.1 of
`01_os/开发入口与单窗口任务规范_v1.md`; who may publish at all is
`01_os/05_registry/repository_publisher_authority_v1.yml`. Never read or expose credentials or key
files.
