# Cybernetic City-State — core repository

This is the `core` repository of the City-State fork family. Core-owned material is
authored here and reaches every domain repository through `git merge core/master`;
core history is never rewritten, because every domain shares an ancestor with it.

## The active OS is `01_os/`

**`01_os/` is the only active OS in this repository.** Its structure, mechanisms,
registry, execution entrypoints and development rules are the current system:

- [`01_os/README.md`](01_os/README.md) — what each area holds and what it does not.
- [`01_os/开发入口与单窗口任务规范_v1.md`](01_os/开发入口与单窗口任务规范_v1.md) —
  the entry every new working window reads: minimum load order, task scope,
  file placement, registry synchronisation, run evidence, publication
  transport gates, independent review and the Human gate.
- `.agents/skills/` (mirrored to `.claude/skills/`) — the whole OS as skills:
  `citystate-os` is the map, one role skill per role, one skill per mechanism.
  Generated from the registry; do not edit by hand.

The physical retirement is complete. Everything tracked outside `01_os/` is the
small retained global surface below:

| Path | Holds |
| :--- | :--- |
| `AGENT_WORKING_DISCIPLINE.md` | How to work here. Every rule names the incident that produced it. |
| `AGENTS.md` | Backend working rules, engineering design principles, Git and publication discipline. |
| `CLAUDE.md`, `GEMINI.md` | Vendor-discovered root routers. Pointers only. |
| `CORE_MANIFEST.yml` | Core/domain ownership boundary, merge and domain-creation procedure. |
| `.githooks/` | The push guard: non-fast-forward refusal and the `master` gate. |
| `.agents/skills/`, `.claude/skills/` | Generated skill adapters: OS map, role skills, mechanism skills. |
| `README.md` | This file. |

The former bootstrap, protocol, mailbox, state, load-profile and navigation
surface has been physically retired. Do not recreate it or make it live through a
new reference. `01_os/**` is the permanent OS namespace: there is no future plan
to lift its contents into the repository root and no compatibility shim.

## If you are a model waking up here

If the Human has told you your role, invoke that role's skill (`role-planner`,
`role-developer`, `role-reviewer`, `role-content-developer`, `role-content-user`);
it does the rest. Otherwise use the repository-wide always-on bootstrap: identify
the repository, branch and Human objective; read `AGENT_WORKING_DISCIPLINE.md`,
`AGENTS.md`, `01_os/README.md` and `01_os/开发入口与单窗口任务规范_v1.md`. Read the
exact remote `master` SHA fresh when a material write, immutable evidence or a
publication boundary needs it. A SHA quoted in any document — including this
one — is not evidence.

The current Human natural-language request is valid task input. Load an existing
durable task packet when present. If none exists and the work will cause material
repository mutation, establish the task packet and run evidence before the first
business/canonical write; do not require a fixed initialization bundle from the
Human. Accumulating history surfaces are not enumerated by default, but any exact
path a loaded skill, boot manifest or task names is read directly.

## If you are the Human

`CORE_MANIFEST.yml` records what core owns, what each domain owns, how a domain
merges, and how a new domain is created (`new-domain.ps1`, never a folder copy).
A domain repository is the latest core plus two directories it owns:
`08_Domain_Applications/` (its content) and `09_Domain_Global_Mechanisms/` (its
loading configuration). Core ships neither, so merging core upgrades the OS and
leaves 08 and 09 untouched. The 2026-08-02 merge
freeze and its lifting are recorded in that file.
