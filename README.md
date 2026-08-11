# Cybernetic City-State — core repository

This is the `core` repository of the City-State fork family. Core-owned material is
authored here and reaches every domain repository through `git merge core/master`;
core history is never rewritten, because every domain shares an ancestor with it.

## The active OS is `01_os/`

**`01_os/` is the only active OS in this repository.** Its structure, mechanisms,
registry, execution entrypoints and development rules are the current system:

- [`01_os/README.md`](01_os/README.md) — what each area holds and what it does not.
- [`01_os/开发入口与单窗口任务规范_v1.md`](01_os/开发入口与单窗口任务规范_v1.md) —
  the entry every new working window reads: minimum load order, one window one
  task, file placement, registry synchronisation, run evidence, publication
  transport gates, independent review and the Human gate.

The physical retirement is complete. Everything tracked outside `01_os/` is the
small retained global surface below:

| Path | Holds |
| :--- | :--- |
| `AGENT_WORKING_DISCIPLINE.md` | How to work here. Every rule names the incident that produced it. |
| `AGENTS.md` | Backend working rules, engineering design principles, Git and publication discipline. |
| `CLAUDE.md`, `GEMINI.md` | Vendor-discovered root routers. Pointers only. |
| `CORE_MANIFEST.yml` | Core/domain ownership boundary, merge and domain-creation procedure. |
| `.githooks/` | The push guard: non-fast-forward refusal and the `master` gate. |
| `README.md` | This file. |

The former bootstrap, protocol, mailbox, state, load-profile and navigation
surface has been physically retired. Do not recreate it or make it live through a
new reference. `01_os/**` is the permanent OS namespace: there is no future plan
to lift its contents into the repository root and no compatibility shim.

## If you are a model waking up here

Read, in this order: the current remote `master` 40-character SHA read fresh;
`AGENT_WORKING_DISCIPLINE.md`; `AGENTS.md`; your task packet; then the two `01_os`
entry documents above if the task touches the OS. Nothing else loads by default,
and a SHA quoted in any document — including this one — is not evidence.

## If you are the Human

`CORE_MANIFEST.yml` records what core owns, what each domain owns, how a domain
merges, and how a new domain is created (`new-domain.ps1`, never a folder copy).
Domain merges are frozen by decision while the new OS is being built; the freeze
and its reasoning are recorded in that file.
