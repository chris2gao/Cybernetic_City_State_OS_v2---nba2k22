# Claude Code onboarding router

Routing adapter only. This file grants no authority and is not a source of truth.

After Claude Code loads this adapter, enter the repository-wide always-on
bootstrap in this order:

1. Identify the active repository, working branch and Human objective. Read a
   fresh remote master/base/head SHA when the actual material-write, immutable
   evidence or publication boundary requires it, not before every routine task.
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
fixed initialization bundle.

**Role initialization.** When the Human names your role — 任务规划, 任务开发 or 审核
in core; 特色内容开发 or 特色内容教学或使用 in a domain — invoke the matching role
skill in `.claude/skills/`: `role-planner`, `role-developer`, `role-reviewer`,
`role-content-developer` or `role-content-user`. It loads every mechanism skill
that role needs and ends with a role-initialization receipt. A role the Human
names in a domain that is none of these is a domain role, which that domain
defines itself in `09_Domain_Global_Mechanisms/`: invoke `role-content-user`
(or `role-content-developer` when the task is to build or change that role),
which looks it up in `09_Domain_Global_Mechanisms/domain_mechanisms.yml`.
`citystate-os` is the map of the whole OS. The chat window is a temporary
workbench: decisions, results and evidence land in the repository or the brief
vault as they form.

Accumulating surfaces — `01_os/_runs/**`, `01_os/_communication/**`,
`01_os/_dev/**`, `08_Domain_Applications/_runs/**` — are history: do not enumerate
or bulk-read them. Any exact path that a loaded skill, a boot manifest or the
current task names is read directly; there is no separate permission or
forbidden zone.

`01_os/**` is the permanent active OS namespace. Material elsewhere in this repository is
retained global infrastructure — this file, `AGENTS.md`,
`AGENT_WORKING_DISCIPLINE.md`, `GEMINI.md`, `README.md`, `CORE_MANIFEST.yml`,
`.githooks/`, and the generated skill adapters in `.agents/skills/` and
`.claude/skills/` — and nothing else is a current startup surface. Physical legacy
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
