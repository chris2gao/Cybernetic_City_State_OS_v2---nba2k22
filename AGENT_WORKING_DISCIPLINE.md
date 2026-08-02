# Agent Working Discipline

Applies to every model working in a City-State repository — Claude (foreground
review and dispatch), Codex and Antigravity (backend execution), and any reviewer.
It is core-owned: edit it in the core repository, and `git merge core/master`
carries it everywhere.

This file is about *how* to work. It grants no authority and overrides no
protocol. Where it meets `AGENTS.md`, `.ai/PROTOCOL.md` or a current Human
instruction, those win.

Every rule below was paid for. The incident is named so the rule is not mistaken
for style preference.

## 1. Land the output; the chat holds nothing

Anything that matters — decisions, verdicts, evidence, contracts — goes into the
repository or the brief vault before the task is called done. A conversation is a
workbench, not a record.

*Paid for 2026-07-25:* a long session became unreachable through the UI (its
transcript was stranded under a previous install path). Nothing of value was lost,
because every conclusion was already in git or the brief vault. That is the only
reason it was a curiosity rather than a loss.

## 2. Filter large output before you fetch it

Never run an unbounded recursive search or print an unfiltered scan. Use targeted
search tools, path filters, `head`/`-First` limits, or aggregate counts.

*Paid for 2026-07-25:* a recursive `findstr` walked into a cache directory and
produced 1.79 million characters; a privacy scan printed 1,254 lines when three
numbers were the answer. Both cost more context than the work they served.

This is the cheapest available saving. It beats any configuration setting.

### The specific habits, and what each one costs

Measured 2026-07-26 across 50 Codex rollout sessions on this workstation: 2,599
shell calls, 5,360 tool outputs, 8.84 billion input tokens. The numbers below are
from that measurement, not estimates.

- **Never read a whole file when a slice answers the question.** Use `-TotalCount`,
  `-First`, `head -n`, or an explicit line range, and widen only after the slice
  proves insufficient. *Measured:* 303 of 355 `Get-Content` calls (85%) carried no
  length limit; an unlimited read cost 6,283 characters on average against 1,839
  for a limited one — **3.4x per call**. Those 303 reads alone were 1.9 million
  characters, roughly a fifth of all tool output.
- **Cap output at the call site, before it runs** — not by ignoring it afterwards.
  *Measured:* output is median 244 characters but p99 28,075; the twenty largest
  outputs were 8.8% of every character returned.
- **When polling a background job, pass the smallest token cap the tool offers,
  and poll less often rather than truncating a large payload repeatedly.**
  *Measured:* the `wait` tool was **30% of all tool traffic** (1,468 calls,
  3.39M characters). 92 of those calls — 6.3% — returned over 10,000 characters
  and accounted for **56% of all polling traffic**. The tool accepts a
  `max_tokens` argument that was never used.
- **Ask Git for the summary first:** `git status -sb`, `git diff --stat`,
  `git log --oneline -n`. Fetch full text only for the hunk in question.
  *Measured:* one `git status` returned 40,093 characters — the truncation
  ceiling, meaning the real output was longer still.
- **Write anything longer than one line as a script file and run the file.** Do
  not pack multi-statement logic into a single `-Command` or `-c` string.
  *Measured:* one quoting mistake in a single-line PowerShell command produced
  53.5 KB of repeated parser errors. Outputs containing a PowerShell error
  averaged 3,655 characters against 1,717 for clean ones — **twice the cost**.
- **On failure, do not re-run the same command unchanged.** Read the error,
  change the hypothesis, and cap the output of the retry.

### What is not worth optimising

The shell *invocation* is not where the tokens go. Command arguments are 0.87% of
all conversation content, and Windows-specific text — escaped backslashes and CRLF
— is about 0.07%. 96.8% of input tokens are cache hits, so a few characters of
path syntax cost essentially nothing. Claims that one operating system costs
tens of percent more than another do not survive measurement; output volume does.

## 3. Verify before acting — then report the finding, not the reading

Check the actual state before you change anything: real HEADs, real file contents,
real exit codes. Then say what you found and what differs. Do **not** replay the
material you read.

*Paid for 2026-07-25, three times:*
- a routine `git merge core/master` would have deleted 1,132 files and 204,156
  lines from a domain — caught by checking the merge delta on a scratch branch
  first, not by trusting that "merging core is safe";
- a folder about to become a new repository still had `origin` pointing at another
  repository; one push would have written into the wrong system;
- a derived denylist term matched 10,708 lines on both trees, which is how it was
  identified as a path fragment rather than a learner identifier.

Each check cost a few commands. Each would have been expensive to undo.

The second half matters as much: reciting file contents back to the Human is pure
cost. Give the conclusion and the delta.

## 4. Dispatch objectives and red lines, not hard numbers

A task packet states the goal, the boundary, what must not happen, and how the
result will be judged. It should not pin counts, path totals or SHAs that the
executor can measure — those go stale between writing and running.

*Paid for 2026-07-25:* two dispatches specified a changed-path count ("15 paths",
"14 paths") that no longer matched reality by execution time. One of them also
required both a count and an edit that necessarily changed that count — mutually
exclusive instructions. The executor measured, followed the measurement, and
reported the contradiction.

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

*Standing failure mode:* six review rounds on one subsystem kept producing the same
shape of error — a claim slightly wider than the thing actually checked. It was not
six mistakes by one careless author; it was one relationship structure (author
designs their own verification) reproducing itself. Where it matters, separate the
two roles, or hand a reviewer the raw material with the conclusions stripped out.

## 6. Irreversible actions are announced before they happen

Report first, then act: history rewriting, force push, repository deletion,
visibility changes, publishing to master, activating a runtime or scheduler,
touching a real learner store.

`core` history is never rewritten. Every domain shares an ancestor with it; one
rewrite breaks mergeability for all of them at once and nothing repairs it
afterwards.

This rule is about the act, not the tool. A branch created through a GitHub API
connector, a `gh` invocation and a local `git push` are the same publication;
writing to master through one of them is the same announced action as writing to
master through another. The local pre-push hook covers only the local transport,
so its silence elsewhere proves nothing — read the remote for that. What each
transport must prove instead is the matrix in section 1.1 of
`08_os/开发入口与单窗口任务规范_v1.md`; who may publish at all, and which acts stay
action-bound even under the widest grant, is
`.ai/REPOSITORY_PUBLISHER_AUTHORITY.yml`.

*Paid for once:* an executor with only a connector read "I cannot run
`git config --get core.hooksPath`" as "I am not permitted to publish", withheld a
finished artifact, and then published a proposal branch through that same
transport. One executor, one session, two incompatible rulings — because the rule
said nothing about the transport and it had to invent one twice. An undefined
gate does not fail safe; it fails inconsistently.

## 7. Keep durable memory honest

Long-lived notes about a fast-moving project decay into confident false statements.
Periodically merge duplicates, correct what changed, and delete what was overturned.
When a stored note names a file, flag or setting, confirm it still exists before
recommending it.

*Paid for repeatedly:* a report kept asserting "both nodes remain review_required"
after they had been accepted, and "master still holds residue" after a merge had
cleaned it. Each stale line forced a later reader to work out which statement to
believe.

## Roles and the flow between them

Read this whole section even though only one part describes you. Every incident
this project has paid for was a **boundary** failure — work done by the wrong
party, or a result accepted by someone who should not have been the one accepting
it. You cannot recognise "this is not mine to do" or "this reviewer is checking
its own output" without the map.

**A role label grants nothing.** It says what you are expected to do, never what
you are permitted to do. Authority comes only from current Human instruction and
the canonical protocol. This applies to every line below.

### Who does what

| Role | Held by | Produces |
|:--|:--|:--|
| Foreground: dispatch, adjudication, verification | Claude | Task packets, verdicts, decision records |
| Backend execution | Codex, Antigravity | Changed files, exit codes, one consolidated handoff |
| Independent review | ChatGPT (dedicated project) | Accept / reject with the evidence it rests on |
| Analysis and design discussion | ChatGPT (separate project) | Options, trade-offs, failure modes |
| Deep research | Gemini web, ChatGPT web (separate project) | Sourced material and a first synthesis |
| Closed-corpus refinement | NotebookLM | Citation-grounded comparison across supplied sources |
| Scheduled cloud automation | Gemini Spark | Not in service; requires a custom MCP node |

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

1. **The reviewer never reviews its own family's output.** ChatGPT reviews
   Gemini's reports; reports written by ChatGPT go to the foreground or to a fresh
   review context with the conclusions stripped. Isolating contexts prevents
   context leakage; it does nothing about a shared model's blind spots, which is
   why this rule exists separately.
2. **The author does not design the verification of their own work.** Where it
   matters, separate the two parties, or hand the reviewer the raw material with
   the conclusions removed.

### The flow

Research produces material → review judges it → the repository keeps it.

Nothing is finished at the point a model says it is finished. A deep research
report is not a finding; an executor's handoff is not an acceptance. Both become
real only after someone who did not produce them has read the primary evidence,
and only once the conclusion is written into the repository or the brief vault.

Research reports land in `01_Research_Reports/`, which `CORE_MANIFEST.yml` marks
domain-owned: each domain keeps its own, and core ships none.

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
