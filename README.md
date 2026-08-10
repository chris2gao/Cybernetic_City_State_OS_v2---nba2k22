# Cybernetic City-State — core repository

This is the `core` repository of the City-State fork family. Core-owned material is
authored here and reaches every domain repository through `git merge core/master`;
core history is never rewritten, because every domain shares an ancestor with it.

## The active OS is `08_os/`

**`08_os/` is the only active OS in this repository.** Its structure, mechanisms,
registry, execution entrypoints and development rules are the current system:

- [`08_os/README.md`](08_os/README.md) — what each area holds and what it does not.
- [`08_os/开发入口与单窗口任务规范_v1.md`](08_os/开发入口与单窗口任务规范_v1.md) —
  the entry every new working window reads: minimum load order, one window one
  task, file placement, registry synchronisation, run evidence, publication
  transport gates, independent review and the Human gate.

Everything outside `08_os/` falls into exactly two categories.

**Retained global surface** — small, and it stays after the transition:

| Path | Holds |
| :--- | :--- |
| `AGENT_WORKING_DISCIPLINE.md` | How to work here. Every rule names the incident that produced it. |
| `AGENTS.md` | Backend working rules, engineering design principles, Git and publication discipline. |
| `CLAUDE.md`, `GEMINI.md` | Vendor-discovered root routers. Pointers only. |
| `CORE_MANIFEST.yml` | Core/domain ownership boundary, merge and domain-creation procedure. |
| `.githooks/` | The push guard: non-fast-forward refusal and the `master` gate. |
| `README.md` | This file. |

**Legacy, awaiting Human retirement** — everything else outside `08_os/`,
including the previous bootstrap, protocol, mailbox, state, load-profile and
navigation material. It is still physically present and nothing has been deleted,
but **it is not an active source of truth for startup, communication, state, tasks,
roles or navigation.** Do not load it to "get context", and do not add a reference
that makes it live again. The retirement inventory that decides what is kept,
migrated or deleted is produced under
`08_os/_runs/run-20260810-根级保留文件重写与依赖盘点-001/`.

## If you are a model waking up here

Read, in this order: the current remote `master` 40-character SHA read fresh;
`AGENT_WORKING_DISCIPLINE.md`; `AGENTS.md`; your task packet; then the two `08_os`
entry documents above if the task touches the OS. Nothing else loads by default,
and a SHA quoted in any document — including this one — is not evidence.

## If you are the Human

`CORE_MANIFEST.yml` records what core owns, what each domain owns, how a domain
merges, and how a new domain is created (`new-domain.ps1`, never a folder copy).
Domain merges are frozen by decision while the new OS is being built; the freeze
and its reasoning are recorded in that file.
