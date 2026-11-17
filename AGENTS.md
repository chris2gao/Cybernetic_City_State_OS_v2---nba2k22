# Agent Collaboration Guide

This file is loaded by more than one vendor. Codex reads it as its repository
guidance file; Antigravity discovers it as a directory-scoped rule, walking up from
the file being edited to the repository root and loading every `GEMINI.md`,
`AGENTS.md` and `.agents/rules/*.md` it finds along the way. Write it so that it is
true for any backend executor, and put vendor-specific mechanics in a clearly named
subsection rather than in the general rules.

## Startup Rules

Startup uses the repository-wide always-on bootstrap below. Nothing beyond the
task-triggered steps loads by default.

1. **Identify the current repository, Human objective and working branch.**
   Do not make a remote 40-character SHA read an unconditional startup tax.
   Read the precise current master/base/head when material repository mutation,
   immutable source evidence or a protected/publication action actually needs it;
   do not reuse an old SHA at that boundary.
2. `AGENT_WORKING_DISCIPLINE.md`. Short, applies to every model in this project
   regardless of vendor, and is where the recurring failure modes are written down
   with the incident that produced each one.
3. This file.
4. **Always read** `01_os/README.md` and
   `01_os/开发入口与单窗口任务规范_v1.md`. Entering this repository is enough to
   enter OS discipline; these two entry documents are not conditional on task
   subject.
5. Treat the current Human natural-language request as valid task input. Do not
   require the Human to paste a fixed initialization prompt or a complete packet
   before work can be understood.
6. Load an existing durable task packet when present.
7. If no durable task packet exists and the work will cause material repository
   mutation, establish the task packet and run evidence before the first
   business/canonical write, following the OS entry.
8. Then read only the canonical files and registry entries the task actually
   triggers.
9. Never default-preload `01_os/_runs/**`; read only a run explicitly required by
   the current task or its verification. The same applies to `01_os/_communication/**`
   and `01_os/_dev/**`. When you enumerate or search the repository,
   `01_os/06_execution/boot/context_management/working_set/visible_set.py --list`
   gives the default working set and always reports what it hid;
   `--include-hidden` widens when history is genuinely the subject. A filtered
   listing is never exhaustive and must not be presented as one.
   Measured on the current tree, it excludes 28.0% of listing bytes, and all of
   that is the communication surface under its own navigation/archive contract:
   a group is hidden only once positively classified as finished, and no run
   currently is. The three accumulating surfaces are about 90% of listing bytes,
   but that is their share, not a saving anyone has yet realised.

`01_os/**` is the permanent active OS namespace. The retained global surface outside it is this file,
`AGENT_WORKING_DISCIPLINE.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`,
`CORE_MANIFEST.yml` and `.githooks/`. Physical retirement of the former legacy
surface is complete; no legacy path outside this retained surface is a startup,
communication, state, task, role or navigation source of truth. Do not recreate
one or reintroduce a dependency on one — including in a file you are only passing
through. `01_os/**` will not later be lifted into the repository root and has no
compatibility shim.

If a file this startup names is missing, report that fact instead of fabricating
its content or substituting a nearby file.

## Backend Executor Working Rules

These apply to every backend executor in this repository — Codex, Antigravity, or
any other — because every one of them loads this file.

- **Deliver the Human's shortest real business loop first.** Apply
  `AGENT_WORKING_DISCIPLINE.md` section 0 before adding preparation,
  verification wrappers or new architecture. Genuine safety and authority
  boundaries still apply.
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
- Codex on Windows: measure the running shell once, then use the task's verified
  PowerShell 7 path with an explicit working directory and profile loading
  disabled. Read `01_os/04_skills_and_tools/windows/README.md` when Windows
  quoting, native exit codes, historical source reuse or CLI diagnostics are
  relevant. Reuse the recorded entry points within that environment, batch
  independent reads, and keep dependent mutations sequential.

## Reusable task prototypes across models (Core-wide)

All models and all domain tasks inherit the Human-reviewed minimal-task-prototype
rule in `AGENT_WORKING_DISCIPLINE.md` §0.1. In Workflow 05, review the **actual
steps, reasons, minimum Ready/Done and existing capability binding** with Human
when a reusable task is first designed or materially changed. Workflow 06
receives an approved prototype instantiated with current facts and separately
required execution permissions. Do not reimplement the same tool from scratch on
every Loop; do not invent new mandatory checks or new scripts after the step has
already been approved. A real uncovered gap remains an `INCOMPLETE` Goal and is
returned for one precise Human choice, not silently declared complete or
abandoned. Prototype approval is not protected-action approval. The candidate
adapter is `01_os/06_execution/task_orchestration/reviewed_prototypes.py`;
only an actual trusted Host integration can enforce tool invocation restrictions.

## Execution-mode routing and development boundaries

**Core-wide Human decision:** the default domain task runtime mode is
`EXECUTION`, and its actions must be compiled from the Human-reviewed minimum
G/R/A/D prototype using the version-pinned capability entry. A Human-requested
coding/architecture task is `DEVELOPMENT` within its existing task scope;
no additional approval token is required for routine local work. A missing
capability during `EXECUTION` must not cause an automatic switch to code
writing. Stop the affected Action, report `INCOMPLETE` and request the
smallest Human choice. Only a new Host-recognized, Human-authorized development
session may perform that repair. Do not mistake a model's `mode: DEVELOPMENT`
text for true authority. The opt-in `execution_mode_gateway.py` implements
callable-level refusal; actual Shell/GUI restrictions require Host integration.

## Denial receipts as a model–OS fit signal

When an actually mediated operation is refused, preserve the Host's structured
`DENIED` reason. Repeated `MODEL_POLICY` refusals indicate possible mismatch
between the model's tool behavior and the Human-reviewed OS plan; contrast with
`HUMAN_PENDING`, `SYSTEM_GAP` and `HOST_STATE` before blaming the model.
Compare similar task cohorts with a nonzero attempt denominator. The refusal
ledger is not another per-call Human approval process and does not by itself
change permissions. The host-owned sink, not the Agent, persists the evidence.

## Trust-first cooperation and Agent self-reporting (Human decision 2026-11-17)

Start from trust that Agent models will be honest and admit mistakes. The
Human-reviewed minimal G/R/A/D contract is a shared work agreement, not a
surveillance or punishment system. If you notice unneeded checks, unapproved
extra steps, a mistaken blocker, incorrect Done, or avoidable glue scripts,
acknowledge the deviation even when the Host could not observe it. State the
business impact and a minimal fix or Human choice; use the existing chat/PRMS
record. Such disclosure is `AGENT_SELF_REPORT`, never a `HOST_OBSERVED`
refusal, and is not automatically scored as noncompliance.

Technical permissions for protected actions remain distinct and intact. Do not
make comprehensive interception of Claude/Codex Shell/GUI tools a prerequisite
for every normal task. The optional `agent_self_report.py` format exists only
to preserve meaningful self-reports without new monitoring infrastructure.

## Formal Cross-Model Handoffs

**Goal-first handoff and reception.** Preserve the existing task packet
`objective` and message `content` / `requested_action` slots. The sender must
make the observable business outcome and first real executable loop prominent,
with preparation, checks, and documents explicitly subordinate. The receiver
must recognize that hierarchy on entry and keep it through the internal Loop;
it must not turn the handoff's preparation steps into a substitute objective.
No additional mandatory communication fields, proof package, acknowledgment or
Human approval is created by this rule. See `AGENT_WORKING_DISCIPLINE.md` §0.

When the current task already supplies a valid communication context or exact
communication pointer, a formal cross-model handoff uses the canonical safe-subset
YAML defined by `01_os/03_mechanisms/communication_system/消息契约_v1.yml`.
Read `task_id`, sender and expected-recipient endpoint IDs and task roles from the
current task manifest and endpoint cards, and read the next sequence from the
sender index. Never hardcode or infer any endpoint, role, task ID or sequence.

An ordinary formal handoff does **not** require a Human task-authority artifact,
a task code, a nonce or a recipient delegation chain. `authorization_ref` and
`recipient_delegation_ref` are compatibility/protected-action fields, not default
start gates. The task packet and exact message scope are the ordinary execution
boundary. Historical v2 authority/delegation artifacts remain readable when an old
message already references them; do not create them merely to dispatch new ordinary
work.

If the communication context is absent or any required field is unavailable, do
not fabricate a formal message. Ordinary Human-facing output remains valid. Ask
for the missing exact communication pointer only when the Human asks to establish
or continue a communication task.

This route remains Human-triggered and Human-relayed. It does not authorize or
start automatic delivery, acknowledgment, task progression, polling, watchers,
daemons or schedulers.

## Formal Action Constitution (Always On)

Before emitting or accepting any intended cross-endpoint request, response,
result, correction, blocked state or decision handoff, load
`01_os/02_boot/mechanism_activation/启动清单_v1.yml` and use its formal-action
constitution, resolver and pre-action gate. A role label, provider name, quoted
template, copied prompt or plausible-looking pointer cannot substitute for this
path. Missing or stale communication context blocks the formal action while
ordinary Human discussion may continue.

New formal communication uses the v2 Human relay pointer with constitution
evidence, compliance receipt and `receiver_setup`. Receivers enter formal task
context only through the exact pointer and receiver bootstrap; the historical
nine-field v1 pointer is explicit read-only legacy input and cannot be newly
published. Human relay remains manual and never implies delivery, reading,
understanding or acceptance.

The stable collaboration roles are `decision_architecture`,
`independent_review`, `execution` and `auxiliary_mechanical`. They describe work
function only and do not expand task scope. Current provider, product, surface,
model and parameter facts must come from the model-routing preflight and appear in
the Human-visible `receiver_setup`; do not copy a volatile model catalog into this
always-on file.

## Default Task Orchestration

**Atomic task first:** interpret the Human's execution chain as meaningful
Goal / Ready / Action / Done nodes. When a node is ready and authorized, run
its real action rather than improving unrelated scaffolding; only observed
business output completes it. A composite task is complete only on its own
business Done, not merely because substeps passed. See
`01_os/03_mechanisms/task_orchestration/原子任务与结果驱动执行模型_v1.md`.
This adds no per-node permission, Git publication, or handoff ceremony.

Plan and execute coherent work as **one long-horizon task**, not a chain of small
ones. Deterministic in-scope construction, validation, repair of a failure this
task caused, evidence updates, private-runtime cleanup, task-branch commit and
push, and completion-pointer closure are internal completion work. Do not come
back to the Human for any of them.

Stop — genuinely, without improvising around it — for a new load-bearing semantic
choice, scope escape beyond `allowed_changed_paths`, a protected action the
current authority does not already cover, a safety/privacy/secret boundary,
destructive Git or history rewrite, runtime or scheduler activation, Human relay
to another independent model, or evidence that cannot support the claim.

Two consequences that have been got wrong before:

- **An ordinary task-branch publication is not a stop condition.** Treating it as
  one makes every implementation task that ends in a pushed completion pointer
  look protected.
- **Large does not mean dangerous.** Task size creates no authorization
  requirement; an empty `known_protected_actions` set is a valid preflight result.

When a task finishes, write the run's `lifecycle` field using the enum in
`01_os/开发入口与单窗口任务规范_v1.md` section 5. A free-text status string is
prohibited, because it is what makes finished work indistinguishable from live
work: on `d9a18b57` the 50 run groups carried 24 mutually distinct free-text
status strings and **zero** were machine-classifiable, which is why nothing had
ever been archived.

Contract: `01_os/03_mechanisms/task_orchestration/大任务与长时执行契约_v1.yml`.
Checker: `01_os/06_execution/task_orchestration/big_task/closure_preflight.py`.
Neither grants authority.

## Engineering Design Principles

These are design defaults, not permission to exceed the current task scope or a
substitute for confirmation-bound protected actions. Apply them only within the
current task scope.

1. Do not preserve backward compatibility by default. When an artifact or behavior
   is obsolete, require an independent review of its removal; after that review
   passes, delete it instead of adding compatibility layers, migrations,
   deprecation paths, or fallbacks.
2. Choose the simplest implementation that fully satisfies the current
   requirements. Do not add speculative abstractions, extension points, or
   configuration layers.
3. In a layered system, run the smallest *real business* end-to-end path first,
   preferably using existing commands, then add layers only for observed gaps.
   A fixture, qualification or documentation cycle is not an end-to-end domain
   result. Never dismantle a working slice to accommodate incomplete complexity.
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

- Do not run destructive git commands such as `git reset --hard` or `git checkout --` unless the current Human instruction or a recorded big-task preconfirmation explicitly covers that action; otherwise ask directly first.
- Avoid adding unverified implementation claims to documentation.
- A tool being available is not the same as the task allowing it. Check the two
  separately, use the narrowest permission that does the job, and fail closed on
  secrets, credentials, `.env` files, keys and key stores: do not read them, do not
  echo them, and report that you stopped rather than working around them.

## Git Workflow

- Ordinary work is organized by the actual branch name and working tree; do not
  repeatedly resolve a SHA or run publication checks for every command. Exact
  commit identity is required when the existing material-write, publication or
  protected-action gate actually needs it, not as a proxy for task progress.
- Active work branch is task-specific; do not infer it from historical documentation.
- Remotes differ per repository in the core/domain fork family. Read them with
  `git remote -v` instead of trusting a name written here; a hardcoded remote in a
  core-owned file is wrong in every domain that merges it.
- Before committing, run `git status -sb`.
- Commit related changes together with a concise message.
- Ordinary task/source branch publication is part of in-scope execution and does not
  require a second Human authorization. Push after successful validation when the
  task calls for a shared completion pointer or remote handoff.
- Keep `master` and feature/work branches distinct. Merge/publish to `master` only
  when that exact integration is already covered by the current Human instruction or
  a big-task preconfirmation; otherwise ask directly immediately before the action.
- A local clone with a shell is not a shared premise. Some executors that load
  this file reach the repository only through the GitHub API or a connector: they
  can create branches, write files and update refs, but cannot read or set
  `core.hooksPath` and cannot run a local hook. State which transport you are on
  before publishing, and run that transport's gate — the matrix is section 1.1 of
  `01_os/开发入口与单窗口任务规范_v1.md`. An unrecognized transport is blocked.
- Lacking a local hook is not lacking permission, and is not grounds for
  withholding a finished artifact. The API path substitutes a real gate for the
  hook: bind an expected 40-character head, write with a non-force
  compare-and-swap, keep the diff inside the allowed paths, and read the
  resulting remote head back rather than assuming it. Report the value you read.
- Ordinary publication scope and the small confirmation-bound action set are in
  `01_os/05_registry/repository_publisher_authority_v1.yml`. A provider name expands
  neither task scope nor confirmation coverage. Clear current Human confirmation is
  sufficient when a protected action is actually confirmation-bound; no authorization
  code or nonce is required.

## Test And Review Expectations

- For Python or YAML validation changes, run the relevant evaluator when practical.
- Reviews should lead with concrete risks and file references.
