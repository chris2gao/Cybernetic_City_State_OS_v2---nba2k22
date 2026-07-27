---
task_version: "1.0"
task_id: "human-core-mechanism-file-audit-0003"
title: "Find the files a document closure cannot see, before another one deletes them"
mode: "goal"
task_level: 1

intent:
  goal: >-
    Identify every file whose retention depends on a program loading it rather than a
    document referencing it, audit the 80 paths already deleted in round 0002 for
    others of that class, and declare the survivors as roots so no future closure can
    reach the same conclusion twice.
  why_now: >-
    Round 0002 computed a correct document closure and deleted .claude/settings.json,
    the shared agent permission policy carrying the deny rules for history rewriting,
    remote repointing and secret reading. It was not misjudged: no document names it,
    so it was never in the graph. Nothing reported its absence. A deleted fixture turns
    the suite red; a deleted policy is silent until an agent does something that should
    have been refused.
  definition_of_done:
    - "Every candidate is classified by its loader - the program, tool or host that reads the path - not by which document mentions it."
    - "The 80 paths deleted in 61ee42f and 6dda5cb are each checked for membership in this class, and any further casualty is named with its loader and its recovery SHA."
    - "Surviving mechanism files are proposed as declared roots so the next closure includes them by construction."
    - "No file is deleted and no closure is recomputed in this task."

outputs:
  primary: ".ai/CODEX_REPORTS/core-mechanism-file-audit-0003.md"

inputs:
  required_refs:
    - ".ai/CODEX_REPORTS/core-mechanism-reachability-cleanup-0002.md"
    - ".ai/CODEX_REPORTS/core-mechanism-reachability-cleanup-0002-closure.json"
    - "CORE_MANIFEST.yml"

scope:
  allowed_actions:
    - "read any file; run read-only git"
    - "write the report and publish it to ai/review/latest"
  forbidden_actions:
    - "delete any file"
    - "recompute or modify the 0002 closure"
    - "modify CORE_MANIFEST.yml or any protocol file"
    - "push master"
    - "touch the teacher repository"

return:
  packet_id: "codex-core-mechanism-file-audit-0003"

completion_policy: "completion_preserving"
---

# The files a document closure cannot see

## 1. The distinction this task exists to make

```
document file   — kept because some document REFERENCES its path
mechanism file  — kept because some program LOADS its path
```

Round 0002 implemented mechanism reachability as document reachability. For protocol
text those are the same thing. For configuration they are not: a permission policy
governs what an agent may do, and no markdown has any reason to name it, so it is a
lone node in a graph of 1267 edges and falls out by construction.

**The test is "who loads this", not "who mentions this".** For each candidate, name the
loader: a program, a test runner, a host application, a shell, git itself. If nothing
loads it and nothing references it, only then is it unused.

## 2. Where to look — position is a hint, not the rule

A first pass suggested mechanism files live in dot-directories. Measurement says
otherwise, so scan all of the following and do not treat the list as exhaustive:

- **dot-directories**: `.ai/`, `.claude/`, `.agents/`. Exclude `.git/` (git's own
  storage) and `.pytest_cache/` (generated).
- **dot-files at root**: `.gitattributes`, `.gitignore`. These are not directories and
  a folders-only sweep misses them. `.gitattributes` controls EOL normalization — the
  cause of the CRLF/LF digest mismatches that cost several hours to diagnose. Losing it
  would reintroduce all of them.
- **root-level scripts and manifests**, none of which sit in a dot-directory:
  `CORE_MANIFEST.yml`, `generate_repository_indexes.py`, `new-domain.ps1`,
  `agent-run.ps1`, `agent-status.ps1`, `agent-stop.ps1`,
  `repository_index_manifest.json`.
- anything else your loader search turns up. Report what you find beyond this list —
  that is the useful part.

## 3. The retrospective half, which matters more than the forward half

Round 0002 deleted 80 exact paths:

```
git diff-tree --no-commit-id --name-only -r --diff-filter=D 61ee42fb9160c8512d49f0288fac0fccfe03c2ac
git diff-tree --no-commit-id --name-only -r --diff-filter=D 6dda5cb656d6d81de876d764fd84276bc8ab1907
```

We know one file of this class was lost and has since been restored by hand. **Check
the other 79.** For each, ask whether any program, tool, host or runner loads that path
— not whether a document mentioned it.

Anything you find: name it, name its loader, give the commit it can be recovered from,
and state what would break and **when it would be noticed**. That last field is the
whole point. A missing fixture is noticed in the next test run; a missing policy may
not be noticed at all.

Do not restore anything in this task. Report and let the Human decide.

## 4. Make the next closure include them by construction

For each surviving mechanism file, propose the mechanism that keeps it: a declared root
entry, a manifest ownership entry, or an explicit protected-paths list. Prefer whichever
is checkable by a program.

Note the two ownership gaps already measured, and do not fix them here:
`.claude/` is not listed in `CORE_MANIFEST.yml` under either ownership section, and
neither are `.ai/HANDOFF_COMMON_CONVENTIONS.md`, `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`,
`.ai/COMMUNICATION_DRIFT_LEDGER.yml`, `.ai/DECISIONS.md`, `.ai/RUNNER.md`,
`.ai/runs/`, `.ai/LONG_RUN_LOGS/`. Two of those are in the receipt-required bootstrap
set, so a domain may edit a file that breaks its own release binding with no rule
against it and no conflict to reveal it.

## 5. One security item found while measuring, reported not fixed

`.ssh/` sits in the repository working tree and contains a live private key
`id_ed25519`. It is correctly ignored — `.gitignore` line 11 — and no key path has ever
been added in any commit; that was verified across all history before the last push.
The exposure is not in git, it is that a private key lives inside a working tree where
one `git add .` would publish it. That is exactly what the no-`git add .` rule defends,
which means the defence is a convention rather than a boundary. Report it; the Human
decides whether to relocate it.

## 6. Reporting

State for each finding: path, loader, class, whether it survives at HEAD, recovery
commit if not, what breaks, and when that break would surface. Publish to
`ai/review/latest`, verify the head you report is on that branch, and write the
immutable Human Brief.

`origin/master` is `e7b68e9acec32607c6ca99e4debff03a139c506d` at the time of writing
and the working tree is clean and pushed. Record it at start and end. Numbers here were
measured at that commit; re-measure, and where you disagree, your measurement wins and
you say so.
