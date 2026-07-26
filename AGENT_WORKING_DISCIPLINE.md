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

## 7. Keep durable memory honest

Long-lived notes about a fast-moving project decay into confident false statements.
Periodically merge duplicates, correct what changed, and delete what was overturned.
When a stored note names a file, flag or setting, confirm it still exists before
recommending it.

*Paid for repeatedly:* a report kept asserting "both nodes remain review_required"
after they had been accepted, and "master still holds residue" after a merge had
cleaned it. Each stale line forced a later reader to work out which statement to
believe.

## Role notes

**Foreground (review and dispatch).** Decide, verify, adjudicate. Write task
packets and accept results. Do not do backend execution work unless the task is
genuinely high-risk or the Human names you.

**Backend executor (Codex, Antigravity).** Execute inside the allowed paths, check
exit codes rather than assuming, and return one consolidated handoff. Stop on the
declared stop conditions instead of improvising around them. Report contradictions
in the dispatch rather than resolving them silently.

**Reviewer.** Read the primary evidence, not the summary. Do not accept the
executor's own account of correctness as the finding. Ask for the material with the
conclusions removed where that is possible.
