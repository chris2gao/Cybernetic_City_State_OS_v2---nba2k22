---
task_version: "1.1"
task_id: "human-core-mechanism-file-audit-0003"
title: "Find the files no repository reference can reveal, before another cleanup deletes them"
mode: "goal"
task_level: 1

intent:
  goal: >-
    Identify every tracked file whose retention depends on an external tool loading it
    over a conventional fixed path, audit all 80 paths deleted in round 0002 for others
    of that class, and propose how each survivor becomes a declared root so no future
    closure can reach the same conclusion twice.
  why_now: >-
    Round 0002 computed a correct closure and deleted .claude/settings.json, the shared
    agent permission policy carrying the deny rules for history rewriting, remote
    repointing and secret reading. It was not misjudged. Nothing in the repository
    loads it and nothing references it: Claude Code reads it from outside, by
    convention, at a fixed path. No search inside the repository could have found the
    loader. Nothing reported its absence either - a deleted fixture turns the suite
    red, a deleted policy simply stops refusing things.
  definition_of_done:
    - "Every candidate is classified by naming its loader, the discovery mechanism (documented convention, hardcoded default, or config reference), and evidence for that claim."
    - "All 80 deleted paths from 61ee42f and 6dda5cb are checked, including the one already known, so the method is verifiable end to end."
    - "Tracked-mechanism findings and ignored-environment findings are reported as two separate sets with separate totals."
    - "Each surviving tracked mechanism file has a proposed protection mechanism that a program can check."
    - "No file is deleted, no closure is recomputed, no protocol or manifest file is edited."

outputs:
  primary: ".ai/CODEX_REPORTS/core-mechanism-file-audit-0003.md"

inputs:
  required_refs:
    - "CORE_MANIFEST.yml"
    - "ai/review/latest:.ai/CODEX_REPORTS/core-mechanism-reachability-cleanup-0002.md"
    - "ai/review/latest:.ai/CODEX_REPORTS/core-mechanism-reachability-cleanup-0002-closure.json"

scope:
  allowed_actions:
    - "read tracked repository files and repository configuration"
    - "run read-only git"
    - "write the report and publish it to ai/review/latest"
  forbidden_actions:
    - "read .ssh/**, *.pem, *.key, id_rsa*, id_ed25519*, .env, .env.*, .credentials.json, or any private key or credential material"
    - "delete any file"
    - "recompute or modify the 0002 closure"
    - "modify CORE_MANIFEST.yml, any protocol file, or any load profile"
    - "push master"
    - "touch the teacher repository"

return:
  packet_id: "codex-core-mechanism-file-audit-0003"

completion_policy: "completion_preserving"
---

# The files no repository reference can reveal

Version 1.1. Version 1.0 was rejected in independent review for three defects, all
confirmed by measurement and all corrected here: two required refs did not exist at the
declared source head, the root cause was stated too loosely, and a blanket permission to
read any file contradicted the private-key risk the same packet reported.

## 1. The real shape of the miss

Version 1.0 framed this as *document reference* versus *program load*. That is too
loose. The accurate statement:

```
A file can be required by a tool that is not in this repository,
which finds it at a fixed path it already knows,
with nothing anywhere in the tree pointing at it.
```

`.claude/settings.json` is read by Claude Code. `.gitattributes` and `.gitignore` are
read by git. `.pytest_cache/` is written by pytest. None of these is referenced by a
document, and none is loaded by any program in the repository. **No search inside the
tree can find their loader, because the loader is outside it.**

This changes the method. You cannot grep for who loads these. You must enumerate the
tools that operate on this repository and, for each, list the paths it reads by
convention. Work from the tool inward, not from the file outward.

Tools known to operate here: git, Claude Code, Codex, Antigravity, pytest/unittest,
the index generator, the lane scripts, and the Windows shells. There will be others.

## 2. Evidence standard

A loader claim is only useful if it is checkable. For each finding give:

- **path**
- **loader** — the tool that reads it
- **discovery mechanism** — documented convention, hardcoded default, or referenced
  from another config file
- **evidence** — the documentation, the tool's own file, or the observable behaviour
  that establishes it. "It looks like config" is not evidence.
- **survives at HEAD** — yes or no, and the recovery commit if no
- **what breaks**
- **when the break would surface** — the decisive field. A missing fixture surfaces in
  the next test run. A missing permission policy may never surface; it just stops
  refusing things. Sort your findings by this column, not by severity.

## 3. Two separate sets, not one list

These are different questions with different remedies and must not be merged:

**Set A — tracked mechanism files.** In git, at risk from a future closure. The remedy
is a declared root or a protected-paths entry. This is the retention question.

**Set B — ignored or untracked environment material.** Not in git, so no closure can
delete it, and it is not a retention question at all. `.ssh/` sits in the working tree
with a live private key; it is correctly ignored at `.gitignore` line 11 and no key path
has ever been added in any commit, verified across all history. The exposure is that a
private key lives inside a working tree where one `git add .` would publish it — a
convention defends it, not a boundary. Report it as workstation hygiene, for the Human
to decide. **Do not read the key material to characterise it.**

## 4. The retrospective half, which matters more

Round 0002 deleted 80 exact paths:

```
git diff-tree --no-commit-id --name-only -r --diff-filter=D 61ee42fb9160c8512d49f0288fac0fccfe03c2ac
git diff-tree --no-commit-id --name-only -r --diff-filter=D 6dda5cb656d6d81de876d764fd84276bc8ab1907
```

Check **all 80**, including `.claude/settings.json` which is already known and has been
restored by hand. Including the known case is deliberate: if your method does not
independently rediscover it, the method is not yet trustworthy for the other 79.

Measured hint, offered with its own limitation: 65 of the 80 are dot-paths, but 64 of
those are ordinary `.ai/` content and exactly one lies outside `.ai/`. Position is a
weak signal here — one true positive in sixty-five. Do not lead with it.

Do not restore anything. Report and let the Human decide.

## 5. Ownership gaps, recorded not fixed

Measured at HEAD: `.claude/`, `.ai/HANDOFF_COMMON_CONVENTIONS.md`,
`.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`, `.ai/COMMUNICATION_DRIFT_LEDGER.yml`,
`.ai/DECISIONS.md`, `.ai/runs/` and `.gitattributes` appear in neither ownership section
of `CORE_MANIFEST.yml`. Two of them are in the receipt-required bootstrap set, so a
domain may edit a file that breaks its own release binding, with no rule against it and
no merge conflict to reveal it.

Note them in the report. Do not edit the manifest here.

## 6. Reporting

Publish to `ai/review/latest`, verify the head you report is on that branch and not on
master, and write the immutable Human Brief.

Record `origin/master` at start and end. Everything measured here was measured at
`6dec9f7d2df5f98117ef06efcb61be5e35c4a0cb`; re-measure, and where you disagree, your
measurement wins and you say so.
