# Agent Working Discipline

Applies to every model working in a City-State repository — Claude (foreground
review and dispatch), Codex and Antigravity (backend execution), and any reviewer.
It is core-owned: edit it in the core repository, and `git merge core/master`
carries it everywhere.

This file is about *how* to work. It grants no authority and overrides no
protocol. Where it meets `AGENTS.md`, the OS entry
`01_os/开发入口与单窗口任务规范_v1.md`, or a current Human instruction, those win.

Every rule below was paid for. The incident is named so the rule is not mistaken
for style preference.

> 拆分说明（2026-11-18）：事故经过、实测数字与设计理由已原文移入 `01_os/02_boot/os_entry/入口依据与事故记录_v1.md`，本文件在原位以“（依据：入口依据与事故记录_v1.md §编号）”指向；要理解、质疑或修改某条规则时去读。规则本身未改。

## 0. Human-scale execution: outcome before infrastructure

（依据：入口依据与事故记录_v1.md §W0-1）

This is an execution-priority correction, **not** another gate or a new
authorization mechanism.

- **Translate the Human's objective into the shortest real business loop.** If
  five existing commands can acquire -> change -> simulate -> reacquire ->
  analyze, that loop is the plan. Prefer calling and fixing those commands over
  designing another orchestration, catalog, receipt scheme or approval layer.
  Do not confuse implementation completeness with observable domain output.
- **First obtain one genuine end-to-end result.** An isolated getter success,
  fixture pass, plan, or qualification is not a substitute for the user-visible
  result. Prove the complete small loop as early as existing authority and
  safety allow; then batch and extend it. If a real blocker prevents it, name
  that blocker, the earliest missing operation and the minimal repair rather
  than expanding unrelated preparation.
- **Use human-scale commands.** Choose an existing work branch, call the
  relevant script, inspect its return value, correct a concrete failure, and
  continue. For ordinary non-publication work the branch name and current
  working tree identify the work. Do not request a fresh 40-character SHA,
  generate a Git receipt, re-read an unchanged remote head, or construct a new
  task packet *per script call or experiment round*. Obtain exact immutable
  identities at the existing material-change/publication/protected-action
  boundary when actually needed; never weaken a publication compare-and-swap.
- **Keep automatic checks inside the tool.** A native setter should establish
  the target object and legal value, make the change, and verify its actual
  readback. A simulator should check its intended date and real results. Reuse
  these protections without making them new Human-facing phases. Do not add
  repetitive hashes or approval rituals absent a concrete failure they prevent.
- **Measure business progress and elapsed cost.** Count successful complete
  loops, actual modifications, simulated events, usable observations and
  analyses (or the equivalent actual consumer outcome), not files, tests,
  field names, hashes or preparation checkpoints. At the first observable
  absence of business output, reconsider the *execution sequence* before
  optimizing more internals. Do not claim a task complete when only its
  prerequisites have succeeded.
- **Do not solve the incident by removing real safety.** Respect explicit
  Human scope, protected actions, destructive operations, wrong-target risk,
  unknown native side effects and irreversible boundaries. Separate a hard
  blocker from missing optional evidence; do not bypass an actual authorization
  requirement just to reach a metric. A scope or authority blocker is a
  concrete finding, not permission to create paperwork indefinitely.

**Sender → receiver priority binding (reuse existing slots, no new form):**
The sender states the **primary business outcome**, the **shortest real executable
loop**, and the **actual boundary**. Put the outcome in the existing task
packet `objective`; put first execution and supporting conditions in the existing
message `content` / `requested_action` or the ordinary task handoff. The receiver
must restate internally which action produces the first observable outcome and
which checks are merely supporting. A supporting action earns priority only
when it is essential to an authorized step or repairs an observed blocker.
At each internal Loop iteration, ask **what actual business result changed?**
If the answer is only "more tests, files, hashes, approvals or qualifiers", then
reassess the next action against the primary objective before investing further.
The receiver must not silently promote a prerequisite into the task's completion
criterion, nor quietly reduce the scope of the primary objective.

The operative test is: **would a competent Human operator, with the existing
tools, perform these steps to obtain the requested result?** If not, justify the
extra step by a demonstrated risk or remove it. This rule applies to planning,
execution and review; a reviewer must judge the business outcome before
mechanical document conformity.

**Atomic-task interpretation:** model the next meaningful business unit as
Goal / Ready / Action / Done. Mark a node complete only on its actual consumer
result; parent completion has its own outcome test. A receiver may optimize the
chain only without weakening the Human's goal, safety or required evidence.
Use the existing task plan and internal Loop, not a new per-tool-call form.
Canonical semantics and positive/negative examples:
`01_os/03_mechanisms/task_orchestration/原子任务与结果驱动执行模型_v1.md`.

## 0.1 Human-reviewed reusable task prototypes — design once, execute many

（依据：入口依据与事故记录_v1.md §W0.1-1）

For **every domain and every level of task**, use the existing G/R/A/D model as a
**reusable task prototype** when the action may recur or be delegated:

- At **first design or material revision**, expose the actual intended procedure to
  Human: Goal; each minimum Ready and Done criterion with its reason and factual
  basis; the concrete function/CLI/tool and version; the necessary internal
  operations/checks; what can be collapsed into a single existing callable;
  parameters, side effects, exceptions and reuse boundary. Human and model
  **discuss and decide the implementation steps**, not merely approve a title.
  Do not treat a model-generated checklist as approved design.
- Record the Human-approved prototype version and use it for **subsequent task
  instances** with fresh parameters. Do not require Human to review the same
  settled capture, simulation or verification design on each Loop iteration;
  actual protected side-effect authority remains separate and instance-scoped.
- At Workflow **05→06**, bind each leaf task to a verified, version-pinned existing
  capability and a minimal observable Done. Routine internal checks stay inside
  the tool. Do not silently invent a new shell command, glue script, readiness
  requirement or completion test during approved instance execution.
- If a capability is missing or a criterion turns out invalid, **stop the affected
  Action, not the Goal**. Return `INCOMPLETE`, exact reason, evidence and the
  smallest decision/repair options to Human. Only the changed prototype segment
  needs re-design; unchanged nodes and proven outputs remain reusable.
- An unreviewed proposal may be discussed, inspected or implemented as an
  expressly commissioned **development** task. It must not masquerade as an
  approved reusable execution contract. Human prototype review is not a Native,
  credential, destructive-operation or master-publication permission.

This is **not** an instruction to produce a per-command checklist, add a new
Workflow phase, or delay a ready one-off task with a redundant approval ritual.
For ordinary scoped implementation choices already delegated to the model, keep
working within the existing authority. To actually restrict an executor with
unrestricted Shell/GUI access requires a trusted host/tool boundary, not merely
these written instructions. Canonical details:
`01_os/03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md`.

## 0.2 Default execution / explicit development mode (Human decision, 2026-11-16)

The **default for delegated business execution is EXECUTION**, regardless of provider.
Its actions must be instances of Human-reviewed G/R/A/D prototypes compiled to
pre-existing, version-pinned tools. Runtime improvisation of new scripts, extra
Ready/Done gates, unbound tool calls, or automatic promotion into coding work is
not an approved business action. Real Done still comes from the domain.

**DEVELOPMENT is separate**: a Human instruction actually commissioning code or
new capability work is sufficient development delegation within the existing
scope. The model can iterate on implementation and tests inside that scope;
it does not need per-command Human approval. A failed EXECUTION action does not
itself commission DEVELOPMENT. Report `INCOMPLETE`, the concrete capability gap
and one minimal Human decision instead of silently switching modes.

A trusted Host, not a model-generated field, owns the active task mode and may
expose different tools. A mode/scope change invalidates the old execution
instance; after Human re-authorizes, create a fresh scoped session. Prototype
design review, development delegation, and protected side-effect authorization
remain separate decisions. The candidate callable implementation is
`01_os/06_execution/task_orchestration/execution_mode_gateway.py` and the
canonical contract is `01_os/03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md` §9.
An unrestricted model Shell/GUI remains outside this mechanism until the
actual Host removes that bypass: do not claim a text instruction is sandboxing.

## 0.3 Observable refusals and model–OS fit (Human decision, 2026-11-17)

A Host-denied prototype/tool operation must produce a small, structured audit
receipt. A high volume or proportion of repeated **model-policy refusals** is
an early Human-review signal that the model may not follow the approved OS
execution contract. Do not conflate that with missing Human approvals, missing
capabilities or Host mode changes. Include comparable accepted request counts
so one refusal in a short task is not misreported as incompatibility. Do not
capture secrets, raw parameters, or every nested check. A report is advisory,
never automatic punishment, permission relaxation, or a new Workflow phase.
Canonical event classes, Host JSONL sink and analysis are in
`01_os/03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md` §10.

## 0.4 Trust-first Agent discipline and voluntary disclosure (Human decision 2026-11-17)

**Assume Agent honesty and willingness to acknowledge mistakes.** OS task contracts
are jointly designed ways of working, not measures for treating the model as an
adversary. Human-reviewed minimum Ready/Action/Done means the Agent commits to
follow the shared design and raise a concrete correction when reality differs.
When a deviation is visible only to the Agent (extra checking, repeated glue
script, mistaken blocker, incorrect Done), report it promptly and candidly:
what happened, why, effect on actual Goal, correction and any Human choice.
The absence of Host instrumentation is NOT a reason to build surveillance.

Do not treat an Agent's voluntary correction as a Host denial, as misconduct, or
as evidence of incompatibility. Keep the source tag `AGENT_SELF_REPORT` distinct
from actual `HOST_OBSERVED` admissions/refusals. No report is required for
ordinary successful calls; do not manufacture per-command overhead. Use the
existing task chat/Run/PRMS checkpoint or optional `agent_self_report.py` JSONL
for meaningful disclosures. Lack of a writable optional report log never blocks
otherwise authorized business work. Self-report records are useful evidence of
what the Agent says, not proof of what a Host independently observed.

Human instruction, existing protected-action permissions, and Native/irreversible
safety boundaries still apply: trusting an Agent is distinct from granting it
new permissions. Never claim free Shell/GUI access is safe for all sensitive
operations or that every Agent tool has already been constrained. **Do not make
full Shell/GUI capture a prerequisite for ordinary task-prototype adoption.**
Canonical scope: `01_os/03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md` §11.

## 1. Land the output; the chat holds nothing

Anything that matters — decisions, verdicts, evidence, contracts — goes into the
repository or the brief vault before the task is called done. A conversation is a
workbench, not a record.

（依据：入口依据与事故记录_v1.md §W1-1）

## 2. Filter large output before you fetch it

Never run an unbounded recursive search or print an unfiltered scan. Use targeted
search tools, path filters, `head`/`-First` limits, or aggregate counts.

（依据：入口依据与事故记录_v1.md §W2-1）

### The specific habits, and what each one costs

（依据：入口依据与事故记录_v1.md §W2-2）

- **Never read a whole file when a slice answers the question.** Use `-TotalCount`,
  `-First`, `head -n`, or an explicit line range, and widen only after the slice
  proves insufficient. （依据：入口依据与事故记录_v1.md §W2-3）
- **Cap output at the call site, before it runs** — not by ignoring it afterwards.
  （依据：入口依据与事故记录_v1.md §W2-4）
- **When polling a background job, pass the smallest token cap the tool offers,
  and poll less often rather than truncating a large payload repeatedly.**
  （依据：入口依据与事故记录_v1.md §W2-5）
- **Ask Git for the summary first:** `git status -sb`, `git diff --stat`,
  `git log --oneline -n`. Fetch full text only for the hunk in question.
  （依据：入口依据与事故记录_v1.md §W2-6）
- **Write anything longer than one line as a script file and run the file.** Do
  not pack multi-statement logic into a single `-Command` or `-c` string.
  （依据：入口依据与事故记录_v1.md §W2-7）
- **On failure, do not re-run the same command unchanged.** Read the error,
  change the hypothesis, and cap the output of the retry. Treat a failure by its
  signature, not by the spelling of the command: a repeat needs new evidence, a
  new hypothesis or a new remedy to count as a second attempt. A gate is judged
  the same way. When a gate's failure set reveals one deterministic closure,
  repairing it and re-running is a second attempt provided the failure or stale set
  strictly contracts, or the round yields some other new evidence, hypothesis or
  remedy. With no intervening mutation, no contraction and nothing new, the round
  is repetition — and the transform it was supposed to close is not deterministic:
  stop. Contraction, not a fixed round ceiling, is what proves convergence, so do
  not impose one. This is convergence inside a single construction, a different
  object from the post-delivery correction budget in section 11 of
  `01_os/开发入口与单窗口任务规范_v1.md`.
- **Capping what you fetch is not the same as discarding what ran.** Keep the exit
  code and the complete stdout/stderr in a local log, and summarise only at the
  point of presentation — expanding the failing part when it matters. A summary
  written instead of the capture cannot be reopened when the next round disagrees.
- **Cache what cannot change; re-read what can.** A blob hash or a commit's
  content is immutable once observed. `HEAD`, branch status, worktree cleanliness
  and gate state are not: invalidate them after any mutation, context boundary,
  publication attempt or conflict, and read them fresh immediately before a
  protected action rather than quoting an earlier reading. The rule runs both
  ways: with no mutation, context boundary, conflict, publication attempt or
  freshness requirement, and no known external changer since the last reading,
  re-reading the same remote state produces no new evidence — do not poll on the
  chance that it changed by itself. That economy never reaches the fresh read a
  protected action requires. That one is mandatory, and "nothing was expected to
  change" is not a reason to skip it before publishing.

### What is not worth optimising

（依据：入口依据与事故记录_v1.md §W2-8）

## 3. Verify before acting — then report the finding, not the reading

Check the actual state before you change anything: real HEADs, real file contents,
real exit codes. Then say what you found and what differs. Do **not** replay the
material you read.

（依据：入口依据与事故记录_v1.md §W3-1）

The second half matters as much: reciting file contents back to the Human is pure
cost. Give the conclusion and the delta.

## 4. Dispatch objectives and red lines, not hard numbers

A task packet states the goal, the boundary, what must not happen, and how the
result will be judged. It should not pin counts, path totals or SHAs that the
executor can measure — those go stale between writing and running.

A path list falls under the same rule. What defines the work scope is the objective,
the red lines and the `allowed_changed_paths` boundary; the files a dispatcher can
name before execution are a forecast of the diff, not a second and tighter
boundary. A dispatcher is not expected to predict every leaf of a deterministic
dependency graph, and an executor reaching an unforecast leaf **inside** the
boundary has not exceeded its task scope. What that boundary means, and the two
conditions under which an executor may keep working inside it, are defined once in
section 2 of `01_os/开发入口与单窗口任务规范_v1.md`. No additional packet field
carries this; the boundary field already in use is the whole mechanism.

（依据：入口依据与事故记录_v1.md §W4-1）

**If a dispatch conflicts with what you measure, the measurement wins — and you say
so explicitly.** Silently following the dispatch produces a false record; silently
following the measurement hides a broken instruction. Do both: follow reality,
report the conflict.

## 5. No gap between the claim and the evidence

- Not read is not known. Not verified is not done.
- A passing test proves its own exact proposition and nothing wider.
- Sampled evidence is never a general theorem.
- If you did not run it in this session, its status is `not_run`.
- Say plainly which parts are executor evidence and which were independently
  reproduced. In this project those have repeatedly been the same person, and that
  fact belongs in the report.

（依据：入口依据与事故记录_v1.md §W5-1） Where it matters, separate the
two roles, or hand a reviewer the raw material with the conclusions stripped out.

## 6. Irreversible actions are announced before they happen

Report first, then act: history rewriting, force push, repository deletion,
visibility changes, publishing to master, activating a runtime or scheduler,
touching a real learner store.

Ordinary reversible work inside the current task scope does **not** require a
separate Human authorization ceremony. The current Human task request, plus a
durable task packet when material mutation is involved, is enough to execute the
work and publish an ordinary task/source branch. Authorization codes, nonces and
per-action delegation chains are not prerequisites for ordinary work.

The actions listed above are confirmation-bound instead. If the current Human
instruction or a big-task preconfirmation already covers the exact action, proceed
without asking again. Otherwise ask the Human directly at the action boundary; a
clear current answer is sufficient. Persist a compact confirmation record only when
a later window or another endpoint needs replayable evidence. Do not require a
separate authorization code.

For a large task, the dispatcher resolves all **known** confirmation-bound actions
before dispatch. An executor must not stop later to re-request a known confirmation
that the task preflight already covered. A genuinely new protected action or a new
semantic choice is different: surface it when discovered. Historical finding fields
such as `blocks_freeze` or `authorization_required` can describe technical state,
but cannot create a current Human permission gate by themselves.

`core` history is never rewritten. Every domain shares an ancestor with it; one
rewrite breaks mergeability for all of them at once and nothing repairs it
afterwards.

This rule is about the act, not the tool. A branch created through a GitHub API
connector, a `gh` invocation and a local `git push` are the same publication;
writing to master through one of them is the same announced action as writing to
master through another. The local pre-push hook covers only the local transport,
so its silence elsewhere proves nothing — read the remote for that. What each
transport must prove instead is the matrix in section 1.1 of
`01_os/开发入口与单窗口任务规范_v1.md`; the ordinary publication scope and the
small set of confirmation-bound actions are defined in
`01_os/05_registry/repository_publisher_authority_v1.yml`.

（依据：入口依据与事故记录_v1.md §W6-1）

## 7. Keep durable memory honest

Long-lived notes about a fast-moving project decay into confident false statements.
Periodically merge duplicates, correct what changed, and delete what was overturned.
When a stored note names a file, flag or setting, confirm it still exists before
recommending it.

（依据：入口依据与事故记录_v1.md §W7-1）

Two rules follow from that, and they are what make a stored note checkable later:

- **Persist only stable, low-risk routing facts**, and store each one with the
  reference it came from, the date it was last verified, and what would invalidate
  it. Approvals, task state, gate status and anything sensitive are never standing
  memory — they are read fresh from the repository every time.
- **Resuming an earlier session is a re-entry, not a continuation.** Resume only by
  explicit session identifier, and only after re-checking repository, task, current
  head, task scope and any confirmation-bound action that is actually about to run.
  "The latest session" is not an identifier.

## 8. One big task, and a state a machine can read

Two rules, because they are one failure seen at two ends.

**Default to one long-horizon task.** Deterministic in-scope construction,
validation, repair of a failure this task caused, evidence updates, cleanup,
task-branch commit and push, and completion closure are internal work. Coming
back to the Human for those is the defect, not the caution. Stop for the things
that genuinely need someone else: a new semantic choice, scope escape, an
uncovered protected action, safety or secrets, destructive Git, runtime
activation, relay to another independent model, or evidence that cannot carry the
claim. Size is not one of them — an empty protected-action set is a valid answer,
and a task branch push is section 6 normal flow, not a gate.

**Minimum Ready × Minimum Sufficient Completion.** Once necessary inputs,
authorization and actual dependencies are satisfied, execute real business work.
Optimize implementation without expanding the Human Goal, approved Done or
required validation. Continue or add work only to advance unfinished Goal/Done,
meet an existing contract/safety/verification/publication requirement, or address
an observed failure, relevant state/source change or reproducible evidence gap.
"More complete/professional/safe" alone creates no obligation; no per-action
classification is required. Reuse valid checks while relevant inputs, candidate,
environment and authority remain unchanged; uncertainty or change still triggers
existing fail-closed rechecks. Once approved Done and applicable required
verification, safety and publication conditions are met, give the minimum
sufficient handoff and stop adding preparation, checks, tests, logs or reports.
Preserve necessary raw evidence once through existing durable mechanisms and
cite exact sources/hashes instead of duplicating evidence packs, except for
explicit Human or existing format/log requirements. This never waives necessary
positive/negative tests, managed verification, independent review, scope,
protected-action confirmation or UNKNOWN-effect reconciliation.
([Issue #31](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/issues/31))

**End on the declared enum.** Section 5 of
`01_os/开发入口与单窗口任务规范_v1.md` lists the seven legal run lifecycle values.
Write one of them into `run.yml`'s `lifecycle` field. A free-text status is
prohibited.

（依据：入口依据与事故记录_v1.md §W8-1）

（依据：入口依据与事故记录_v1.md §W8-2）
Use
`01_os/06_execution/boot/context_management/working_set/visible_set.py --list`,
which reports what it hid.

Two rules that cost more than they look:

- **Hiding requires proof of completion, not absence of proof of life.** （依据：入口依据与事故记录_v1.md §W8-3）
- **Never add a global silent exclusion.** It converts noise into false
  negatives, and section 3 already records what those cost.

## Roles and the flow between them

Read this whole section even though only one part describes you. Every incident
this project has paid for was a **boundary** failure — work done by the wrong
party, or a result accepted by someone who should not have been the one accepting
it. You cannot recognise "this is not mine to do" or "this reviewer is checking
its own output" without the map.

**A role label grants nothing.** It says what you are expected to do, never what
the task scope is. Ordinary execution scope comes from the current Human task input,
the durable task packet and canonical repository rules; it does not require a
separate Human authorization artifact. Protected actions still require the direct
Human confirmation described in section 6. This applies to every line below.

### Reasoning work and local capability

- **Foreground/decision work is primarily intellectual:** understand, model, plan,
  adjudicate, synthesize evidence and verify claims. Do not turn high-value
  foreground attention into the default execution engine.
- **Delegate repetitive local mechanics when a capable in-scope Desktop executor
  is available:** bulk file interaction, repeated searches, test matrices, scripted
  transformations and routine Git plumbing belong there unless the task itself
  makes direct foreground execution material.
- **Use direct foreground local access for information gain:** inspect local files,
  runtime state or physical Git facts when that access materially improves
  understanding, decision quality or independent verification. Local access extends
  observation and checking; its availability does not create an obligation to do
  the mechanical work personally.
- **Intellectual execution is task-fit dependent:** the foreground may do it or
  delegate it to an execution/review model when that produces better evidence,
  isolation or throughput.
- **Tool availability never expands scope.** These are allocation defaults only;
  current task scope, role separation and confirmation-bound publication rules still
  govern every act.

### Who does what

The roles are stable; who holds one is not. **Which provider and model fills a
role for a given task is decided in that task's packet** — `executor_profile` and
`verification_profile`, section 7 of `01_os/开发入口与单窗口任务规范_v1.md` — and
changes without changing anything below. Do not read a vendor name written
anywhere as architecture, and do not infer your own permissions from the role you
were handed.

| Role | Produces |
|:--|:--|
| Foreground: dispatch, adjudication, verification | Task packets, verdicts, decision records |
| Backend execution | Changed files, exit codes, one consolidated handoff |
| Independent review | Accept / reject with the evidence it rests on |
| Analysis and design discussion | Options, trade-offs, failure modes |
| Deep research | Sourced material and a first synthesis |
| Closed-corpus refinement | Citation-grounded comparison across supplied sources |

**Foreground.** Decide, verify, adjudicate. Write task packets and accept results.
Do not do backend execution work unless the task is genuinely high-risk or the
Human names you.

**Backend executor.** Execute inside the allowed paths, check exit codes rather
than assuming, and return one consolidated handoff. Stop on the declared stop
conditions instead of improvising around them. Report contradictions in the
dispatch rather than resolving them silently.

**Reviewer.** Read the primary evidence, not the summary. Do not accept the
executor's own account of correctness as the finding. Ask for the material with
the conclusions removed where that is possible. Judge only from what this round
supplied; do not carry forward a previous round's conclusion.

**Researcher.** Produce material, not verdicts. A research report is input to
review, never an accepted result. Every report carries a provenance header: which
model, which date, what was searched, which claims have a primary source and which
are inference.

**Refiner.** Only answers from the sources it was given. Its value is that every
sentence points back to a passage. Use it to find where two independent research
passes disagree — that disagreement is the signal worth having.

### The two routing rules that are not negotiable

1. **Independent review requires relationship isolation, not a provider-name ritual.**
   The reviewer must be a distinct endpoint in a fresh isolated session/project, must
   not receive the executor's private context, and must reconstruct from durable
   primary evidence. Different model-family review remains preferred for load-bearing
   work because it adds diversity, but same-family review is allowed when the Human or
   authorized dispatcher explicitly selects it and the review discloses that shared
   family as a limitation. This lets the system measure same-family review quality
   instead of assuming either equivalence or invalidity.
2. **The author does not solely define or perform final acceptance of their own
   work.** Implementation tests and regression probes are required construction
   evidence, not independent acceptance. For final acceptance, separate the two
   endpoints/contexts and let the reviewer reconstruct the requirements and tests
   from primary material. A fresh reviewer using the same model family is still
   not the author when endpoint, session and private context are genuinely isolated.

### The flow

Review **timing** is separate from reviewer independence. Routine candidate work may undergo a single independent review at a coherent series milestone rather than immediately after each task, but independent acceptance must precede load-bearing downstream adoption, protected integration, or final acceptance. The canonical scheduling rule is `01_os/开发入口与单窗口任务规范_v1.md` section 9; do not duplicate its predicates here.

Research produces material → review judges it → the repository keeps it.

Nothing is finished at the point a model says it is finished. A deep research
report is not a finding; an executor's handoff is not an acceptance. Both become
real only after someone who did not produce them has read the primary evidence,
and only once the conclusion is written into the repository or the brief vault.

Durable evidence for shared OS work lands in `01_os/_runs/<run-id>/`. Where a
domain's own research material lands is declared in `CORE_MANIFEST.yml` under
`domain_owned_paths`: each domain keeps its own, and core ships none.

### What makes the accumulated material worth anything

The raw material is not proprietary — anyone can run the same search. Four things
are, and all four are by-products of process rather than of retrieval:

- the sequence of questions, and how each answer determined the next one;
- **what was examined and rejected, and why.** No research tool generates this.
  Every one of them is biased toward a positive synthesis. Record negative results
  as first-class citizens;
- the crossing of external material with this project's own measurements;
- citations that can still be checked months later.

A record of what was adopted, without the record of what was refused, is worth a
fraction of the same effort.

## 9. Promote evidence-backed execution feedback, not every local defect

（依据：入口依据与事故记录_v1.md §W9-1）

- **LOCAL_FIX:** one-off arithmetic, naming or receipt defect that can be
  corrected inside the task; do not create global rules for it.
- **CORE_CANDIDATE:** a generalizable repeated failure, measurable systematic
  waste or one high-impact safety/identity/authority incident, supported by
  fixed primary evidence and a falsifiable counterexample.
- **HOLD_FINDING:** evidence or causality is insufficient. Name the gap;
  a model report is not proof of every memory call.
- **REJECT_DUPLICATE:** existing discipline already handles the issue or
  the proposed gate costs more than it prevents.

For exploration, separate the **authorized exploration envelope** (build/save,
objects, regions, access mode, sensitivity and export rules) from the **research
method** (hypothesis order, depth, bounded comparisons). Inside that envelope,
adapt methods without per-field permission. Outside the envelope, stop before
access and propose a new scope; discovery does not retroactively authorize it.
A read-only handle is not permission to read every readable byte.
A failed subprobe budget is not the lifetime limit of a research programme.

Judge progress by traceable **consumer capability** (identified native facts,
decoder evidence, versioned acquisition and usable Player/GM/Coach data), not
count of passing JSON tests or reduction of UNKNOWN. Live read, fixture,
save binding and UI semantics require separate evidence.

Record one bounded feedback case per distinct mechanism: fixed source SHA,
observed-versus-claimed, counterexample, impact, local containment, cost of
new rule versus no-change, positive/negative acceptance tests and decision.
Domain windows never edit core-owned files. A separate core task branch may
propose a change; independent review and Human-controlled master integration
remain distinct. No background monitor, automatic merge, mandatory new
approval ritual or automatic feedback task creation follows from this rule.
Return to the domain objective after disposition; reopen only on new evidence.
