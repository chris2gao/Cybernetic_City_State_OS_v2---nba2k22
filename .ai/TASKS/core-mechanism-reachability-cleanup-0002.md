---
task_version: "1.0"
task_id: "human-core-mechanism-reachability-cleanup-0002"
title: "Keep what the mechanism reaches, delete the rest"
mode: "goal"
task_level: 2

intent:
  goal: >-
    Walk 系统机制总结.md document by document, compute what the城邦 mechanism actually
    reaches, and delete everything in core that is not in the resulting keep set.
    One pass, one deletion commit, no per-file supersession arguments.
  why_now: >-
    The teacher-owned material has already been removed (c7156fc, 855 to 581 tracked).
    What remains is core's own accumulation. The Human has decided that post-refactor
    is a new starting point: historical traceability is not a goal, so the Evidence
    class, removal records and retrieval anchors from the previous task are dropped.
  definition_of_done:
    - "Every document named in 系统机制总结.md has been opened and its declared dependencies recorded."
    - "The keep set is computed and every declared root is in it; a root outside the keep set fails the run."
    - "All dynamic-load sites are resolved and their targets are in the keep set."
    - "Everything tracked and not in the keep set is deleted in one commit."
    - "After deletion the unit suite passes, run-fixtures passes, and the release-binding check is green."
    - "Directory indexes are regenerated so they describe the tree that now exists."

outputs:
  primary: ".ai/CODEX_REPORTS/core-mechanism-reachability-cleanup-0002.md"

inputs:
  required_refs:
    - "系统机制总结.md"
    - "CORE_MANIFEST.yml"
    - ".ai/communication_compliance/material_event_policy.yml"

scope:
  allowed_actions:
    - "read any file; run read-only git, python and the test suites"
    - "delete tracked files not in the keep set, in one commit on master"
    - "regenerate directory indexes"
    - "write the report and publish it to ai/review/latest"
  forbidden_actions:
    - "push master"
    - "rewrite history"
    - "touch the teacher repository"
    - "delete anything under 01_Research_Reports/"
    - "delete any file in the keep set"

return:
  packet_id: "codex-core-mechanism-reachability-cleanup-0002"

completion_policy: "completion_preserving"
---

# Keep what the mechanism reaches, delete the rest

## 1. The rule, in full

```
KEEP = reachable from the declared roots
     + loaded at runtime by code, tests or fixtures
     + 01_Research_Reports/
DELETE = everything else tracked
```

That is the whole rule. **Do not** classify into Evidence and Dead, do not argue that a
file was superseded by a newer one, do not write removal records or retrieval anchors.
Those existed to protect historical traceability, and the Human has decided that this
refactor is a new starting point. Core history is never rewritten, so anything deleted
stays retrievable from git; nothing further is needed.

If a file is not reached and not loaded at runtime, it goes. No argument required.

## 2. Where the keep set comes from

`系统机制总结.md` at the repository root is the survey to work from. Go through it
**document by document**: for each file it names, open that file and record what it in
turn requires. That transitive walk is the keep set.

It covers the receipt-required bootstrap set, the context-boundary initialization set,
the four role profiles and their fixed extensions, the constitutional digest and its
two conditional full sources, the communication and handoff protocol stack, the
communication-compliance policy/validator/schemas/fixtures/tests, the lane mechanism,
role memory, and the two-tier large-task execution stack.

Its own section 11 lists what it considers certain to keep — treat that as a starting
point to verify, not as the answer. Where your walk disagrees with it, your walk wins
and you say so.

Add the roots it does not cover: `CORE_MANIFEST.yml` `core_owned_paths`, the routing
table's five now-relative link targets, and real imports and invocations in scripts and
tests.

## 3. The two things that are not optional

Everything else in this packet is simplification. These two are not, and the reason is
not process purity — it is that both failure modes delete files the system is currently
using, and you find out days later through a broken suite rather than at deletion time.

**Path enumeration.** Use `git -c core.quotepath=false ls-files -z`. Under the default,
68 of the tracked paths are emitted as quoted octal escapes and will never match a
UTF-8 root string. The previous round classified six declared roots as deletable
because of exactly this. Assert that every declared root lands in the keep set, and
fail the run if one does not.

**Dynamic loading.** Fourteen call sites across ten files load by glob or directory
walk; four of those files are tests loading fixtures. Static reachability cannot see
any of it. Resolve every site to a concrete target set and put those targets in the
keep set. Re-count the sites yourself and report your number.

## 4. Indexes

There are 109 `index.md` files and they are generated, not authored. Do not reason
about their reachability. Delete those whose directory does not survive, keep the rest,
and regenerate at the end with `generate_repository_indexes.py` so they describe the
tree that now exists. `repository_index_manifest.json` currently claims 1883 tracked
files against a real 581 — it must be regenerated too, or it stays wrong.

## 5. `01_Research_Reports/` is an explicit exception

The Human keeps it. Note in the report that `CORE_MANIFEST.yml` currently lists it
under `domain_owned_paths`, so keeping it in core contradicts the manifest. Propose the
manifest correction; do not apply it in this task, because the manifest edit belongs
with the other ownership fixes.

## 6. Verification, and when to stop

After the deletion commit: run the unit suite, run `run-fixtures`, and check the
release binding. All three must be green. If any is not, the keep set was wrong —
report which file broke it rather than adding files back one at a time until it passes.

Stop and return `blocked` if: deletion would require touching a release-bound file's
content; a declared root does not land in the keep set; or the suites do not recover.

Record `origin/master` at start and end. Publish the report to `ai/review/latest`,
verify the head you report is on that branch, and write the immutable Human Brief.

Numbers in this packet were measured at `c7156fc`. Re-measure; where you disagree, your
measurement wins and you say so.
