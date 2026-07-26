---
task_version: "1.0"
task_id: "human-core-live-set-and-cleanup-0001"
title: "Determine the live file set, publish it for independent review, then remove what is dead"
mode: "goal"
task_level: 2

intent:
  goal: >-
    Establish which files in the core repository are actually in use, by
    reachability from declared entry points rather than from generated indexes;
    publish that evidence where an independent reviewer can read it; and after the
    single Human gate, remove the files proven dead. One task, sequential stages,
    no new packet between stages.
  why_now: >-
    The core repository carries archive and superseded material that merges into
    every domain. The index system cannot answer which files are live: its own
    manifest describes 1883 tracked files while the repository has 851. The
    release binding is now closed and all tests pass, so the tree is in a coherent
    state to measure.
  definition_of_done:
    - "A reachability closure is computed from the root set in section 3 and written to outputs.primary, with the edge kind recorded for every included file."
    - "All 9 dynamic-load sites are resolved to concrete file sets, and files reachable only at runtime are marked live with the loading site named."
    - "Every tracked file is placed in exactly one of the three classes in section 4, with per-file evidence."
    - "A separate ownership proposal covers 06_Silicon_Index/factory_pipeline, including the cross-repository move order in section 6."
    - "The classification is published to ai/review/latest with conclusions separated from evidence, and review_branch_head is verified to be a commit on that branch and not on master."
    - "After the Human gate in stage 5, class 3 files are removed in one commit, the unit suite still passes, and the release binding remains green."
    - "origin/master is recorded at task start and again at task end; any change between them is reported as a concurrent external write, not silently absorbed."
    - "The class 3 list is checked for intersection with release-bound paths and with every dynamic-load target before it is proposed."

outputs:
  primary: ".ai/CODEX_REPORTS/core-live-set-0001.md"
  additional:
    - ".ai/CODEX_REPORTS/core-live-set-0001-classification.md"
    - ".ai/CODEX_REPORTS/core-live-set-0001-factory-pipeline-ownership.md"

inputs:
  required_refs:
    - "CORE_MANIFEST.yml"
    - ".ai/communication_compliance/material_event_policy.yml"
    - ".ai/CODEX_REPORTS/core-structural-integrity-diagnosis-0001.md"
  local_files:
    - "E:/newStand/城邦简报/core/03_决策档案/2026-07-26_绑定闭环完成与重构闭包根集.md"

scope:
  allowed_actions:
    - "read any repository file; run read-only git and python"
    - "write the three output reports"
    - "publish to ai/review/latest"
    - "after the stage 5 gate only: delete class 3 files and commit on master"
  forbidden_actions:
    - "push master without explicit Human authorization"
    - "rewrite history"
    - "delete or relocate anything classed 2 (evidence)"
    - "act on adjudication items C1 or C2"
    - "delete anything before the stage 5 gate"
    - "treat index.md or repository_index_manifest.json as evidence of use"

return:
  packet_id: "codex-core-live-set-and-cleanup-0001"

completion_policy: "completion_preserving"
---

# Live set, independent review, then cleanup — one task

## 1. How this task is packaged

This is deliberately **one task with sequential stages**, not five packets. Per
`.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`, discovered cleanup, validation, reporting and
publication steps that are necessary to finish the authorized objective are folded in.
Do not stop for a new dispatch between stages 1 and 4.

There is exactly **one real Human gate**, at stage 5, because deletion in core
propagates into seven domain repositories on their next merge. Everything before it
runs continuously.

## 2. Stages

**Stage 1 — publish what already exists.** The original text of this stage was wrong
about where the artifacts live. Corrected after measurement at `5d1951c` /
`origin/ai/review/latest@b1e40c6a`; re-measure before acting:

| artifact | on master | on review |
| :--- | :--- | :--- |
| `.ai/CODEX_REPORTS/core-structural-integrity-diagnosis-0001.md` | no | yes |
| `.ai/CODEX_REPORTS/release-rebinding-cycle-0001.md` | no | yes |
| `.ai/CODEX_REPORTS/link_fix_0001.md` | yes | no |
| `.ai/HUMAN_BRIEFS/link_fix_0001/codex-001.md` | yes | no |

No artifact exists on both. So the actual work is: **publish the two master-only
files to `ai/review/latest`, and leave the two already there untouched.** Do not
claim that all of them were newly published from master.

Separately, one earlier handoff reported a `review_branch_head` that was a master
commit. Whatever you report must be verified to be on the review branch.

**Stage 2 — compute the closure.** From the roots in section 3. Record for each
reached file which edge reached it.

**Stage 3 — resolve dynamic loading.** The original text of this stage said "nine
sites" and listed seven files. Both were wrong: they came from a truncated search
whose pattern also matched `Get-ChildItem`. Re-measured over
`.glob(` / `.rglob(` / `iterdir(` / `os.listdir(` / `os.walk(` / `os.scandir(`:
**14 call sites across 10 files.**

```
 1  .ai/communication_compliance/tests/test_validate_communication.py
 3  .ai/runs/tests/test_agent_runner.py
 3  .ai/token_profile/chat_channel.py
 1  .ai/token_profile/consolidate_ledger.py
 1  .ai/token_profile/tests/test_chat_channel.py
 1  06_Silicon_Index/factory_pipeline/autonomous_factory_agent.py
 1  06_Silicon_Index/factory_pipeline/bulk_evaluator.py
 1  06_Silicon_Index/factory_pipeline/global_topology_tracer.py
 1  06_Silicon_Index/factory_pipeline/rescue_remaining.py
 1  06_Silicon_Index/factory_pipeline/rescue_sub_topics.py
```

Count these yourself and report your number. Do not reconcile to 14 to match this
packet; if you measure something else, that is the finding.

Four of the ten are test files loading fixtures dynamically. Those targets are
especially dangerous to misclassify: a fixture judged dead will not fail at
classification time, it will fail in the test suite after deletion.

Static text reachability will not see any of this. Resolve each site to a concrete
file set, mark those files live, and name the loading site for each.

**Stage 4 — classify and publish.** Three classes, section 4. Publish to
`ai/review/latest`. The classification artifact must present evidence with the
conclusion column separable, so a reviewer can judge from the material rather than
from your verdict.

**Stage 5 — Human gate, then delete.** Stop. Report the class 3 list and wait. After
authorization, delete in one commit, rerun the unit suite and the release-binding
check, and confirm both still pass. This stays inside this task and this task ID; do
not open a new packet.

## 3. Root set

Do **not** use `index.md` or `repository_index_manifest.json` as evidence of use. They
are generated mirrors of the tracked tree, and the manifest is stale by more than a
factor of two. They record what exists, not what is used.

Roots:

- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `AGENT_WORKING_DISCIPLINE.md`
- `06_Silicon_Index/AI_Bootstrap_Sequence.md`
- `CORE_MANIFEST.yml` `core_owned_paths`
- `material_event_policy.yml` `bootstrap_required_loaded_files` and
  `bootstrap_on_demand_requirements`
- `.ai/load_profiles/*.md` — note four pins reference files absent from core
- Communication stack: `PROTOCOL.md`, `PROTOCOL_ADHERENCE.md`,
  `HANDOFF_COMMON_CONVENTIONS.md`, `HANDOFF_INIT_PROMPT.md`,
  `AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`
- Task execution stack: `CODEX_WORK_MECHANISM_PROTOCOL.md`,
  `CODEX_TASK_INPUT_CONTRACT.md`, `LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`,
  `DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`
- `Plan 3 External Augmentation OS 总体架构设计方案 v0.1.md` and the five files its §3
  lists — see section 5
- `00_City_State_Routing_Table.md` — repaired to relative links; all five targets
  resolve
- Real imports and invocations in tests and scripts

## 4. Three classes

1. **Live** — reached by the closure, or loaded at runtime by a site from stage 3.
2. **Evidence** — not reached, but is the record of a decision or an execution:
   `.ai/CODEX_REPORTS/`, `.ai/PROGRAM_RUNS/`, `.ai/HUMAN_BRIEFS/`,
   `01_Research_Reports/`, parliament verdicts. **Unreachable is not useless.** Code
   not referencing a verdict does not make the verdict disposable. This class is also
   adjudication item C1 — **do not touch it**.
3. **Dead** — unreachable, not evidence, and superseded by a newer version. Only this
   class is a deletion candidate.

When a file is arguable between 2 and 3, it goes in 2 and you say why.

## 5. Plan 3 completion is not self-evident

Its §3 lists five files to be added later. All five already exist. So by the
document's own acceptance criterion the plan is complete. But its §2 marks several
runtime components `planned / not yet implemented` and `future / protected`.

"The plan document is finished" and "the system the plan describes is built" are
different propositions and this v0.1 contains both. If you rely on Plan 3 status to
keep or drop anything, **state which criterion you used.** Do not let the ambiguity
pass silently.

## 6. `factory_pipeline` ownership — propose, do not execute

Twenty-one of the thirty-two non-`.ai` Python files sit in
`06_Silicon_Index/factory_pipeline/` and are a mathematics-teaching production
pipeline. `CORE_MANIFEST.yml` keeps `06_Silicon_Index/` in core because it is "the
shared bootstrap every city-state instance starts from" — true of the bootstrap
documents in that directory, not of these twenty-one files.

Propose the reclassification and record the move order, which cannot be reversed:

1. In **teacher**, copy the files to a domain-owned path and commit there.
2. Then in **core**, delete them.
3. teacher's next `git merge core/master` drops the core copy and keeps its own.

Reversed, teacher loses its only copy at merge time. The other six domains will also
lose these files, which is the intended outcome.

Note `debug_json.py` / `2` / `3` / `4` and `find_keys.py` / `find_keys2.py`: numbered
duplicates are the signature of throwaway debug scripts and are strong class 3
candidates — after stage 3 clears them.

## 7. Stop conditions

Stop and return `blocked` if: a class 3 candidate is reachable by an edge kind not in
section 3 that you believe should count; deletion would require touching a
release-bound file; the unit suite or release-binding check fails at any point; or the
Human gate at stage 5 has not been answered.

## 7A. Revision round 1 — required before the stage 5 gate is answered

Independent review returned `changes_required`. Deletion is **not** authorized. The
following work continues **inside this same task and task ID**; do not open a new
packet.

### R1. Recompute the closure with unescaped paths — this is the root cause

The classification contradicted its own declared roots: `0号方案.md`, `1号方案.md`,
`2号方案.md`, `3号方案.md`, `城邦系统需要实现的目标原则.md` and
`Plan 3 External Augmentation OS 总体架构设计方案 v0.1.md` were classed Evidence, yet
the first five are **exact entries in `core_owned_paths`** and the Plan is a declared
root. `3号方案.md` is additionally a conditional-Live constitutional source.

Measured cause, confirmed independently: under default settings `git ls-files` emits
non-ASCII paths as quoted octal escapes, so they never match a UTF-8 root string.
**68 of 855 tracked paths are escaped under the default.** The defect is therefore not
limited to the six named files — up to 68 paths may have been misclassified.

Recompute using NUL-separated, unescaped output:

```
git -c core.quotepath=false ls-files -z
```

Then add an assertion that fails the run: **every declared root must end up in Live.**
A classification that cannot place its own roots is invalid regardless of its totals.
The previously reported `Live 278 / Evidence 571 / Dead 6` are void; report new ones.

### R2. The `debug_json*` supersession claim is not supported

The report claimed `find_nodes.py` supersedes the four `debug_json*.py` probes. Read
the code: the four probes search by key or by `NAME`, emit `CHILDREN`, dump a fixed
node, and probe whether the topology file is a dict or a list. `find_nodes.py` uses
seven hard-coded keywords, searches only `NAME`, prints only ID and name, caps at ten
results, takes no parameters, and emits neither `CHILDREN` nor full node structure.
That is not behavioural replacement.

The report also states the probes and their claimed replacement entered in the **same**
commit — so the replacement is not a newer version either. Class 3 in this task
requires unreachable **and** not evidence **and** superseded by a specific newer file.
Two of the three fail.

Move all four back out of Class 3. If you still believe they are dead, argue it on a
different basis and say which basis — "looks like a throwaway debug script" is not one
of the three criteria.

`find_keys.py` and `find_keys2.py` are a stronger case: their recursive traversal was
copied into the two rescue scripts. But that is a diagnostic-to-repair relationship,
not equivalence. Re-argue them separately; do not carry them through on the strength
of the group.

### R3. Missing immutable Human Brief

The stage 5 handoff is a material Human-gate event and returned `brief_ref: null`.
Write `.ai/HUMAN_BRIEFS/<task-id>/<lane-instance-id>-<message-seq>.md` and reference
it. Independent expression inside the main report does not substitute for it.

### R4. Teacher migration — widen the inventory, and note what it collides with

The `factory_pipeline` ownership direction is accepted. But **29 references to
`factory_pipeline` exist in core outside that directory**, including six in
`.ai/CODEX_TASK_INPUT_CONTRACT.md`, plus `ARCHITECTURE.md`, `CHANGELOG_AI.md`, and
`开发分支与合并进度总账.md`.

`CODEX_TASK_INPUT_CONTRACT.md` is both release-bound and pinned in
`canonical_ref_digests`. **Editing it triggers both binding mechanisms, so the core-side
reference fix must ride inside a release rebinding cycle's semantics commit, not a
standalone commit.** Record this dependency; do not perform it in this task.

Extend the migration inventory beyond `factory_pipeline` to at least:
`.ai/load_profiles/math_mentor_teacher.md`, `.ai/role_memory/teacher.md`, the Math
Mentor rules in `AGENTS.md`, the pipeline path examples in
`CODEX_TASK_INPUT_CONTRACT.md`, and the Knowledge Completion Program binding in
`LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. For each, propose exactly one of: keep as
generic routing / migrate the domain implementation / rewrite as a domain-relative
reference / let the teacher repository override it. Propose only — none of it is
authorized here.

### R5. Migration ordering, so teacher's in-flight work is never broken

Human decision: teaching material belongs to the teacher repository under its
`08_Domain_Applications/`. Codex may operate that repository. Execute the migration so
that **no moment exists where a file is absent from teacher**:

1. **teacher** copies the files to `08_Domain_Applications/Math_Mentor/pipeline/` and
   commits. Both paths now exist there; in-flight tasks referencing the old path keep
   working.
2. **teacher** repoints its own references to the new path at its own pace, verifying
   by running its tests. The old path is still present as a fallback throughout.
3. **teacher** confirms zero remaining references to `06_Silicon_Index/factory_pipeline/`.
4. Only then does **core** delete, together with the reference fixes from R4.
5. **teacher** merges `core/master`; the core copy disappears and nothing references it.

The dangerous step is not the deletion, it is step 5 — and step 3 is what makes step 5
a no-op. Teacher controls when it merges, so it cannot be surprised. Steps 1 to 3 are
teacher-side and are not authorized by this packet; report the plan.

### What was accepted and must not be redone

Stage 1 provenance handling; the dynamic-load inventory of 14 sites across 10 files
with tracked-core targets distinguished from external and temporary run data; the
empty intersection between the six candidates and both release-bound paths and tracked
dynamic targets; 215/215 fixtures and 17/17 tests; evidence directories untouched;
review-branch identity correctly verified at `173a4439`. Do not re-derive these.

## 8. Reporting

Report what you measured, not what this packet says. Every number here was measured by
a Claude instance at head `bf9e126`; re-measure, and where you disagree, your
measurement wins and you say so. Return the canonical seven-field handoff with a
`review_branch_head` that you have verified is a commit on `ai/review/latest`.
