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

**Stage 1 — publish what already exists.** Two prior reports
(`core-structural-integrity-diagnosis-0001.md`, `link_fix_0001.md`) plus the human
brief were committed to `master` and were reported with a `review_branch_head` that is
actually a master commit. Publish them to `ai/review/latest` so an independent
reviewer can read them from GitHub, and verify the head you report is on that branch.

**Stage 2 — compute the closure.** From the roots in section 3. Record for each
reached file which edge reached it.

**Stage 3 — resolve dynamic loading.** Nine sites load by glob or directory walk
(`chat_channel.py`, `consolidate_ledger.py`, `autonomous_factory_agent.py`,
`bulk_evaluator.py`, `global_topology_tracer.py`, `rescue_remaining.py`,
`rescue_sub_topics.py`). Static text reachability will not see what they load. Resolve
each to a concrete set and mark those files live, naming the site.

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

## 8. Reporting

Report what you measured, not what this packet says. Every number here was measured by
a Claude instance at head `bf9e126`; re-measure, and where you disagree, your
measurement wins and you say so. Return the canonical seven-field handoff with a
`review_branch_head` that you have verified is a commit on `ai/review/latest`.
